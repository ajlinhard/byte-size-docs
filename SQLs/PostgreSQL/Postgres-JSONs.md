# Postgres JSONs
## PostgreSQL JSON Syntax

PostgreSQL supports two JSON types: `json` (stores exact text) and `jsonb` (binary, indexed, generally preferred).

---

### Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `->` | Get JSON object field (returns JSON) | `data -> 'key'` |
| `->>` | Get JSON object field (returns text) | `data ->> 'key'` |
| `#>` | Get nested field (returns JSON) | `data #> '{a,b}'` |
| `#>>` | Get nested field (returns text) | `data #>> '{a,b}'` |
| `@>` | Contains | `data @> '{"key":"val"}'` |
| `<@` | Is contained by | `'{"a":1}' <@ data` |
| `?` | Key exists | `data ? 'key'` |
| `?|` | Any key exists | `data ?| array['a','b']` |
| `?&` | All keys exist | `data ?& array['a','b']` |
| `||` | Concatenate (jsonb) | `data || '{"c":3}'` |
| `-` | Delete key (jsonb) | `data - 'key'` |

---

### Querying

```sql
-- Basic field access
SELECT data -> 'name'        -- returns JSON: "Alice"
SELECT data ->> 'name'       -- returns text: Alice

-- Nested access
SELECT data #>> '{address,city}'

-- Array element (0-indexed)
SELECT data -> 'tags' -> 0
SELECT data #>> '{tags,0}'

-- Filter rows
SELECT * FROM users WHERE data ->> 'status' = 'active';
SELECT * FROM users WHERE data @> '{"role": "admin"}';
```

---

### Modifying (jsonb)

```sql
-- Set a key
UPDATE t SET data = jsonb_set(data, '{key}', '"value"');

-- Set nested key (create path if missing)
UPDATE t SET data = jsonb_set(data, '{a,b}', '42', true);

-- Remove a key
UPDATE t SET data = data - 'key';

-- Remove nested key
UPDATE t SET data = data #- '{a,b}';

-- Merge/overwrite
UPDATE t SET data = data || '{"x": 1, "y": 2}';
```

---

### Useful Functions

```sql
-- Parse
SELECT '{"a":1}'::jsonb;

-- Build
SELECT json_build_object('name', 'Alice', 'age', 30);
SELECT jsonb_build_array(1, 2, 3);

-- Extract keys/values
SELECT jsonb_object_keys(data) FROM t;
SELECT * FROM jsonb_each(data);          -- returns (key, value) rows
SELECT * FROM jsonb_each_text(data);     -- returns text values

-- Array length
SELECT jsonb_array_length(data -> 'tags');

-- Expand array to rows
SELECT * FROM jsonb_array_elements(data -> 'tags');
SELECT * FROM jsonb_array_elements_text(data -> 'tags');

-- Check type
SELECT jsonb_typeof(data -> 'age');  -- 'number', 'string', 'array', etc.

-- Pretty print
SELECT jsonb_pretty(data);
```

---

### Indexing (jsonb)

```sql
-- GIN index for @>, ?, ?|, ?& operators
CREATE INDEX idx_data ON t USING GIN (data);

-- GIN index on specific path
CREATE INDEX idx_name ON t USING GIN ((data -> 'tags'));

-- B-tree index on extracted value
CREATE INDEX idx_status ON t ((data ->> 'status'));
```

---

**Key tip:** Prefer `jsonb` over `json` — it's faster to query, supports indexing, and deduplicates keys. Use `json` only if you need to preserve exact input formatting or key order.
