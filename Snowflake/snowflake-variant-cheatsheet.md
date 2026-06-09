# Snowflake VARIANT Cheatsheet

Working with `VARIANT` columns that hold strings, integers, JSON objects, and lists — including how to unnest arrays and JSON with `FLATTEN`.

---

## Setup: a table with mixed VARIANT values

A single `VARIANT` column can hold a scalar (string, int, boolean), an object, or an array.

```sql
CREATE OR REPLACE TABLE variant_demo (
    id   INTEGER,
    data VARIANT
);

-- Use INSERT ... SELECT so PARSE_JSON / TO_VARIANT can run
INSERT INTO variant_demo
SELECT 1, TO_VARIANT('hello')                          -- string
UNION ALL
SELECT 2, TO_VARIANT(42)                               -- int
UNION ALL
SELECT 3, PARSE_JSON('{"name":"Ada","age":30}')        -- JSON object
UNION ALL
SELECT 4, PARSE_JSON('[10, 20, 30]');                  -- list / array
```

> `PARSE_JSON` turns a JSON string into a VARIANT. `TO_VARIANT` wraps any scalar. Use `TRY_PARSE_JSON` when the input might be malformed — it returns `NULL` instead of erroring.

---

## Storing each type

| You have | Store it with |
|----------|---------------|
| A string | `TO_VARIANT('text')` |
| An int/number | `TO_VARIANT(42)` |
| A JSON object | `PARSE_JSON('{"k":"v"}')` |
| A list/array | `PARSE_JSON('[1,2,3]')` or `ARRAY_CONSTRUCT(1,2,3)` |
| Bad-JSON-safe parse | `TRY_PARSE_JSON(maybe_bad_text)` |

---

## Reading scalar values back

**The #1 gotcha:** path access returns a VARIANT *with quotes*. Always cast with `::TYPE` to get a clean, typed value.

```sql
SELECT
    data:name              AS raw,        -- "Ada"   <- quoted, still VARIANT
    data:name::STRING      AS name_str,   -- Ada     <- clean string
    data:age::INTEGER      AS age_int     -- 30
FROM variant_demo
WHERE id = 3;
```

Access patterns:

```sql
data:name           -- dot/colon path to object key
data:user.address   -- nested key
data['name']        -- bracket notation (same as data:name)
data[0]             -- array element by index
GET(data, 'name')   -- function form of key access
GET(data, 0)        -- function form of index access
```

Common casts: `::STRING`, `::INTEGER`, `::FLOAT`, `::NUMBER(10,2)`, `::BOOLEAN`, `::DATE`, `::TIMESTAMP`.

---

## Checking what a VARIANT holds

Useful when the column is genuinely mixed (like `variant_demo` above).

```sql
SELECT
    id,
    TYPEOF(data)      AS type,        -- VARCHAR / INTEGER / OBJECT / ARRAY
    IS_VARCHAR(data)  AS is_string,
    IS_INTEGER(data)  AS is_int,
    IS_OBJECT(data)   AS is_json,
    IS_ARRAY(data)    AS is_list
FROM variant_demo;
```

`AS_INTEGER(data)`, `AS_VARCHAR(data)`, `AS_ARRAY(data)`, etc. cast *and* return `NULL` if the value isn't that type — handy for safely pulling one type out of a mixed column without errors.

---

## Unnesting a list (array → rows)

Use `LATERAL FLATTEN`. Each array element becomes its own row.

```sql
-- [10, 20, 30] -> three rows
SELECT
    v.id,
    f.index            AS position,     -- 0, 1, 2
    f.value::INTEGER   AS element       -- 10, 20, 30
FROM variant_demo v,
     LATERAL FLATTEN(input => v.data) f
WHERE v.id = 4;
```

FLATTEN exposes these columns on `f`:

| Column | Meaning |
|--------|---------|
| `f.value` | the element (cast it!) |
| `f.index` | array index (NULL for objects) |
| `f.key`   | object key (NULL for arrays) |
| `f.path`  | path to the element, e.g. `[0]` |
| `f.seq`   | sequence id of the input row |
| `f.this`  | the whole element being flattened |

---

## Unnesting JSON (object → key/value rows)

Pointing `FLATTEN` at an object yields one row per key.

```sql
-- {"name":"Ada","age":30} -> two rows
SELECT
    f.key                AS field,    -- name, age
    f.value::STRING      AS value     -- Ada, 30
FROM variant_demo v,
     LATERAL FLATTEN(input => v.data) f
WHERE v.id = 3;
```

---

## The common real case: array of objects

JSON like `{"customer":"Ada","items":[{"sku":"A1","qty":2},{"sku":"B2","qty":1}]}` — flatten the inner array, keep outer fields.

```sql
CREATE OR REPLACE TABLE orders_v (id INTEGER, payload VARIANT);

INSERT INTO orders_v
SELECT 1, PARSE_JSON('{"customer":"Ada","items":[{"sku":"A1","qty":2},{"sku":"B2","qty":1}]}');

SELECT
    o.payload:customer::STRING AS customer,   -- outer field, repeated per row
    f.value:sku::STRING        AS sku,        -- A1, B2
    f.value:qty::INTEGER       AS qty         -- 2,  1
FROM orders_v o,
     LATERAL FLATTEN(input => o.payload:items) f;   -- flatten the inner array
```

The pattern: `FLATTEN(input => <path to the array>)`, then reach into each element with `f.value:<key>::TYPE`.

---

## FLATTEN options

```sql
LATERAL FLATTEN(
    input     => v.data,      -- the array/object/variant to expand (required)
    path      => 'items',     -- drill to a sub-element before flattening
    outer     => TRUE,        -- emit a row even when input is empty/null (LEFT-JOIN-like)
    recursive => TRUE,        -- expand every nested level, not just the top
    mode      => 'BOTH'       -- 'ARRAY', 'OBJECT', or 'BOTH'
) f
```

- **`outer => TRUE`** — without it, rows whose array is empty or NULL disappear entirely. Use it to keep parent rows that have no children.
- **`recursive => TRUE`** — walks the whole tree; combine with `f.path` to see where each value lives.

```sql
-- See every leaf in a nested object with its full path
SELECT f.path, f.value
FROM variant_demo v,
     LATERAL FLATTEN(input => v.data, recursive => TRUE) f
WHERE v.id = 3;
```

---

## Handy helper functions

```sql
ARRAY_SIZE(data)            -- number of elements in an array
OBJECT_KEYS(data)           -- array of an object's keys
GET(data, 'key' | index)    -- pull one element/field
FLATTEN(...)                -- explode array/object into rows (above)

ARRAY_AGG(col)              -- collapse rows back into an array
OBJECT_AGG(key_col, val_col)-- build an object from rows
TO_JSON(data)               -- VARIANT -> JSON string
```

---

## Gotchas to remember

- **Always cast.** `data:name` is a quoted VARIANT (`"Ada"`); `data:name::STRING` is `Ada`. Joins and comparisons silently misbehave without the cast.
- **`PARSE_JSON` errors on bad input**; use `TRY_PARSE_JSON` for untrusted data.
- **Empty/NULL arrays vanish** under a plain `FLATTEN`. Add `outer => TRUE` to keep the parent row.
- **JSON `null` ≠ SQL `NULL`.** Use `IS_NULL_VALUE(data:field)` to detect a JSON null specifically.
- **`FLATTEN` needs an array or object.** Pointing it at a scalar errors — check with `IS_ARRAY` / `IS_OBJECT` first if the column is mixed.
- **Comma + `LATERAL` is a lateral join.** `FROM tbl, LATERAL FLATTEN(...)` correlates the flatten to each row of `tbl`; you don't need an explicit `ON`.
