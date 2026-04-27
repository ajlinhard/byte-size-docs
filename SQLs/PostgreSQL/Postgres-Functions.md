## PostgreSQL Functions — The Basics

### Defining a Function

The core skeleton is:

```sql
CREATE OR REPLACE FUNCTION my_function(param1 INTEGER, param2 TEXT)
RETURNS INTEGER AS $$
-- body here
$$ LANGUAGE plpgsql;
```

The `$$` are dollar-quote delimiters — just a way to wrap the body without escaping single quotes inside it. You can use any word (`$body$`, `$func$`), or nothing between the `$$`.

---

### Inputs

Parameters can be defined three ways:

```sql
-- Positional (most common)
CREATE FUNCTION add(INTEGER, INTEGER) RETURNS INTEGER ...

-- Named
CREATE FUNCTION add(a INTEGER, b INTEGER) RETURNS INTEGER ...

-- Named with defaults
CREATE FUNCTION add(a INTEGER, b INTEGER DEFAULT 0) RETURNS INTEGER ...
```

PostgreSQL also supports `IN`, `OUT`, and `INOUT` parameter modes:

```sql
CREATE FUNCTION divide(IN a NUMERIC, IN b NUMERIC, OUT result NUMERIC, OUT remainder NUMERIC) ...
```

`OUT` parameters let you return multiple values without a composite type, and when you use them you can omit the `RETURNS` clause entirely.

---

### Variables

Variables are declared in a `DECLARE` block before `BEGIN`:

```sql
DECLARE
    v_user_id   INTEGER;
    v_name      TEXT := 'default';   -- initialized inline
    v_count     INTEGER DEFAULT 0;   -- same thing, different syntax
BEGIN
    ...
END;
```

You can also declare a variable using `%TYPE` to bind it to a column's type, which is useful for avoiding drift:

```sql
DECLARE
    v_name users.first_name%TYPE;   -- inherits whatever type that column is
```

Or `%ROWTYPE` to bind to a whole row:

```sql
DECLARE
    v_user users%ROWTYPE;
BEGIN
    SELECT * INTO v_user FROM users WHERE user_id = 1;
    RAISE NOTICE 'Name: %', v_user.first_name;
END;
```

---

### Outputs

You have several options:

**`RETURNS scalar`** — return a single value with the `RETURN` statement:
```sql
RETURNS INTEGER
...
RETURN v_some_integer;
```

**`RETURNS TABLE`** — return a result set, using `RETURN NEXT` or `RETURN QUERY`:
```sql
RETURNS TABLE(id INTEGER, name TEXT) AS $$
BEGIN
    RETURN QUERY SELECT user_id, first_name FROM users;
END;
$$
```

**`RETURNS SETOF type`** — similar to above but returns a set of a named type or scalar:
```sql
RETURNS SETOF users   -- returns full rows matching the users table shape
```

**`RETURNS VOID`** — for functions that only perform side effects with no return value.

**`RETURNS INTEGER` with `RETURNING ... INTO`** — as in your `upsert_form_question`, where you grab the new ID directly from an `INSERT`:
```sql
INSERT INTO ... RETURNING question_id INTO v_question_id;
RETURN v_question_id;
```

---

### Control Flow

plpgsql has full procedural control:

```sql
-- Conditionals
IF x > 0 THEN ... ELSIF x = 0 THEN ... ELSE ... END IF;

-- Loops
LOOP ... EXIT WHEN condition; END LOOP;
FOR i IN 1..10 LOOP ... END LOOP;
FOR row IN SELECT * FROM users LOOP ... END LOOP;  -- cursor-style iteration
WHILE condition LOOP ... END LOOP;
```

---

### Exception Handling

Exceptions are caught in a `BEGIN...EXCEPTION...END` block, which you can nest anywhere:

```sql
BEGIN
    SELECT ... INTO STRICT v_id FROM ...;
EXCEPTION
    WHEN NO_DATA_FOUND THEN
        RAISE EXCEPTION 'Not found: %', p_name;
    WHEN TOO_MANY_ROWS THEN
        RAISE EXCEPTION 'Ambiguous: %', p_name;
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Unexpected error: %', SQLERRM;
END;
```

`RAISE` has several levels — `DEBUG`, `INFO`, `NOTICE`, `WARNING`, and `EXCEPTION`. Only `EXCEPTION` aborts execution; the others just emit messages.

---

### Notable PostgreSQL-Specific Features

**Multiple languages** — the `LANGUAGE` clause is not cosmetic. PostgreSQL supports:
- `plpgsql` — the standard procedural language
- `sql` — pure SQL, no variables, but simpler and often faster
- `plpython3u` — Python (the `u` means "untrusted", has filesystem access)
- `plperl`, `plv8` (JavaScript), and others via extensions

**`LANGUAGE sql` functions** are worth knowing — they're lighter than plpgsql and the planner can sometimes inline them:
```sql
CREATE FUNCTION add(a INTEGER, b INTEGER) RETURNS INTEGER
LANGUAGE sql AS $$ SELECT a + b; $$;
```

**Volatility categories** — PostgreSQL lets you declare how a function behaves relative to the database state, which affects optimization:
- `VOLATILE` (default) — can return different results each call, never cached
- `STABLE` — same inputs return same result within a single query; planner can optimize
- `IMMUTABLE` — same inputs always return same result, ever; can be used in indexes

```sql
CREATE FUNCTION clean_text(t TEXT) RETURNS TEXT
LANGUAGE sql IMMUTABLE AS $$ SELECT LOWER(TRIM(t)); $$;
```

**Functions in indexes** — because of `IMMUTABLE`, you can use a function directly in an index, which is rare in other SQL databases:
```sql
CREATE INDEX idx_lower_email ON users(LOWER(email));
```

**`STRICT`** — if any input is NULL, skip execution and return NULL automatically:
```sql
CREATE FUNCTION add(a INTEGER, b INTEGER) RETURNS INTEGER
LANGUAGE sql STRICT AS $$ SELECT a + b; $$;
```

**Security Definer** — functions can run with the permissions of the function's *owner* rather than the caller, useful for controlled privilege escalation:
```sql
CREATE FUNCTION admin_delete(id INTEGER) RETURNS VOID
SECURITY DEFINER LANGUAGE plpgsql AS $$ ... $$;
```

**Functions vs Procedures** — PostgreSQL added `PROCEDURE` in v11. The key difference is that procedures support transaction control (`COMMIT`/`ROLLBACK` inside the body) while functions do not — they always run inside the caller's transaction.

## Function Execution
The most likely issue is the use of `PERFORM` vs. the right call syntax depending on what `upsert_form` is:

- **`PERFORM`** → calls a **function** inside PL/pgSQL and discards the result
- **`CALL`** → calls a **procedure** (PL/pgSQL or plain SQL)
- **`SELECT`** → calls a **function** in plain SQL scripts

If `upsert_form` is a **procedure** (created with `CREATE PROCEDURE`), fix it to:

```sql
CALL upsert_form(
    'DEV SMART File',                                                         -- p_form_name
    'SMART File',                                                             -- p_form_type
    'SteerBridge Structured Medical Analysis and Review Tool (SMART) '
    'File for VA disability claims.  Covers veteran profile, claim '
    'header, findings, diagnosis, evidence, and next development '
    'actions.',                                                               -- p_form_description
    1,                                                                        -- p_form_level
    v_file_name,                                                              -- p_form_output_name
    true                                                                      -- p_active_fl
);
```

If `upsert_form` is a **function** and this is a **plain SQL script** (not inside a `DO $$ ... $$` block or stored function), use:

```sql
SELECT upsert_form(
    'DEV SMART File',
    'SMART File',
    'SteerBridge Structured Medical Analysis and Review Tool (SMART) '
    'File for VA disability claims.  Covers veteran profile, claim '
    'header, findings, diagnosis, evidence, and next development '
    'actions.',
    1,
    v_file_name,
    true
);
```

**`PERFORM` is valid only inside a PL/pgSQL block** (e.g., inside a `DO $$...$$`, trigger, or stored function body). If you're seeing an error like `syntax error at or near "PERFORM"`, that's your cause — you're running it as a plain script.

---

### Compared to Other Databases

| Feature | PostgreSQL | SQL Server | MySQL/MariaDB | Oracle |
|---|---|---|---|---|
| Multiple languages | Yes (plpgsql, Python, Perl, JS…) | T-SQL only (CLR via extension) | SQL/procedural only | PL/SQL + Java |
| Functions in indexes | Yes (if IMMUTABLE) | Limited (deterministic) | No | Yes (function-based indexes) |
| Volatility hints | Yes (IMMUTABLE/STABLE/VOLATILE) | "Deterministic" only | "Deterministic" only | Similar via optimizer hints |
| Transaction control in functions | No (use PROCEDURE) | Yes in stored procs | Yes in stored procs | Autonomous transactions |
| Overloading | Yes | No | No | Yes |
| SECURITY DEFINER | Yes | Via EXECUTE AS | No | AUTHID DEFINER |
| Return a full table | RETURNS TABLE / SETOF | RETURNS TABLE | No | PIPELINED TABLE functions |

The biggest practical differentiators are **overloading**, **multiple languages**, and **IMMUTABLE functions usable in indexes** — those three don't exist or are very limited in SQL Server and MySQL.
