# Spark SQL JSONs
In Databricks, a JSON formatted string is simply a string that contains valid JSON data. It's stored as a regular string type in your tables or DataFrames, but the content follows JSON structure with key-value pairs, arrays, and nested objects.

For example, you might have a column containing strings like:
```json
{"name": "John", "age": 30, "city": "New York"}
```

Databricks provides several SQL functions to work with JSON strings:

## Key JSON Functions

**`get_json_object()`** - Extracts a single value from a JSON string using a JSONPath expression:
```sql
SELECT get_json_object(json_column, '$.name') as name,
       get_json_object(json_column, '$.age') as age
FROM your_table
```

**`json_extract()`** - Similar to get_json_object but with slightly different syntax:
```sql
SELECT json_extract(json_column, '$.name') as name
FROM your_table
```

**`from_json()`** - Parses a JSON string into a struct type, which you can then access with dot notation:
```sql
SELECT from_json(json_column, 'name STRING, age INT, city STRING') as parsed_json
FROM your_table
```

**`json_tuple()`** - Extracts multiple values at once:
```sql
SELECT json_tuple(json_column, 'name', 'age', 'city') as (name, age, city)
FROM your_table
```

## Working with Nested JSON

For nested objects, use dot notation in your JSONPath:
```sql
-- For JSON like: {"user": {"profile": {"name": "John"}}}
SELECT get_json_object(json_column, '$.user.profile.name') as name
FROM your_table
```

For arrays, use bracket notation:
```sql
-- For JSON like: {"items": ["apple", "banana"]}
SELECT get_json_object(json_column, '$.items[0]') as first_item
FROM your_table
```

## Schema Inference

You can also use `schema_of_json()` to automatically infer the schema of your JSON data:
```sql
SELECT schema_of_json('{"name": "John", "age": 30}') as inferred_schema
```

These functions make it easy to query and transform JSON data without needing to parse it in application code, keeping your data processing within SQL.
