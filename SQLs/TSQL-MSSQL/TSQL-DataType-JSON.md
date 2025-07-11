# TSQL JSON
JSON support in TSQL is decent, but can have some difficult with speed and efficency as well as completeness for built-ins. For example, extracting and working with arrays in nested JSONS

## JSON Functions (SQL Server 2016+)

| Function Name | Purpose | Type | Example |
|---------------|---------|------|---------|
| JSON_VALUE | Extracts scalar value from JSON | Scalar | `SELECT JSON_VALUE('{"name":"John"}', '$.name')` → 'John' |
| JSON_QUERY | Extracts object/array from JSON | Scalar | `SELECT JSON_QUERY('{"items":[1,2]}', '$.items')` → '[1,2]' |
| JSON_MODIFY | Modifies JSON | Scalar | `SELECT JSON_MODIFY('{"name":"John"}', '$.age', 30)` |
| ISJSON | Checks if valid JSON | Scalar | `SELECT ISJSON('{"name":"John"}')` → 1 |
| OPENJSON | Parses JSON into table | Table | `SELECT * FROM OPENJSON('{"name":"John"}')` |

### Example Code
These are very basic uses of each function
```sql
drop table if exists #temp_json_str
select json_str = '{
  "user": {
    "id": 123,
    "name": "Alice Johnson",
    "contact": {
      "email": "alice@example.com",
      "phone": "+1-555-0123"
    },
    "preferences": {
      "theme": "dark",
      "notifications": true,
      "languages": ["en", "es"]
    }
  },
  "timestamp": "2025-07-11T10:30:00Z"
}'
into #temp_json_str


--Extract Values
select json_value(json_str, '$.user')
	,json_value(json_str, '$.user.contact.email')
	,json_value(json_str, '$.user.preferences.languages') --will be null since its an array
	,'--> JSON_QUERY'
	,json_query(json_str, '$.user.preferences.languages')
	,'--> ISJSON'
	,isjson(json_str)
	,isjson('')
	,isjson('{}')
	,'--> JSON_MODIFY'
	,json_modify(json_str, '$.user.id', 522)
from #temp_json_str

--- OPEN JSON
select *
from #temp_json_str a
cross apply OPENJSON(a.json_str) b
```

## OPENJSON Function Overview
OPENJSON is a table-valued function that parses JSON text and returns objects and properties from the JSON input as rows and columns.
OPENJSON is for bursting out JSONs layer by layer, or in one go if you want to mainly want to unpack each nested value. This is similar to LATERAL VIEW explode in Spark, Databricks, and Snowflake

**Key sections:**
- **Options table** - showing the three main syntax variations
- **Return column types** - explaining the default output structure
- **JSON type codes** - numeric codes for different JSON data types
- **Schema definition options** - data type mappings for the WITH clause

**Examples progress from basic to advanced:**
- Simple parsing and schema definition
- Nested object access with custom JSON paths
- Array processing 
- Mixed data types and NULL handling
- Cross Apply for multiple records
- Real-world use cases like configuration parsing

**Best practices and performance tips** are included at the end to help you use OPENJSON effectively in production scenarios.

The examples are all runnable and demonstrate common patterns you'll encounter when working with JSON data in SQL Server. Would you like me to expand on any particular aspect or add more examples for specific use cases?

## Syntax Options

| Option | Description | Example |
|--------|-------------|---------|
| `OPENJSON(jsonExpression)` | Basic parsing - returns key, value, type | `OPENJSON('{"name":"John","age":30}')` |
| `OPENJSON(jsonExpression, path)` | Parse specific JSON path | `OPENJSON(@json, '$.users')` |
| `OPENJSON(...) WITH (schema)` | Explicit schema definition | `OPENJSON(@json) WITH (name VARCHAR(50), age INT)` |

## Return Column Types (without WITH clause)

| Column | Type | Description |
|--------|------|-------------|
| `key` | nvarchar(4000) | Property name or array index |
| `value` | nvarchar(max) | Property value as string |
| `type` | int | JSON data type (see type codes below) |

## JSON Type Codes

| Type Code | JSON Type | Description |
|-----------|-----------|-------------|
| 0 | null | JSON null value |
| 1 | string | JSON string value |
| 2 | number | JSON number value |
| 3 | true/false | JSON boolean value |
| 4 | array | JSON array |
| 5 | object | JSON object |

## Schema Definition Options (WITH clause)

| Data Type | JSON Mapping | Notes |
|-----------|--------------|-------|
| `INT`, `BIGINT` | JSON number | Automatic conversion |
| `VARCHAR(n)`, `NVARCHAR(n)` | JSON string | Specify length |
| `BIT` | JSON boolean | true/false to 1/0 |
| `DATETIME2`, `DATE` | JSON string | ISO format recommended |
| `DECIMAL(p,s)` | JSON number | Precision and scale |
| `column_name TYPE '$.path'` | Custom JSON path | Map to specific JSON property |

## Basic Examples

### 1. Simple JSON Parsing
```sql
DECLARE @json NVARCHAR(MAX) = '{"name":"John","age":30,"city":"New York"}'

SELECT * FROM OPENJSON(@json)
```
**Result:**
```
key    value      type
name   John       1
age    30         2
city   New York   1
```

### 2. With Explicit Schema
```sql
DECLARE @json NVARCHAR(MAX) = '{"name":"John","age":30,"active":true}'

SELECT * FROM OPENJSON(@json) 
WITH (
    name VARCHAR(50),
    age INT,
    active BIT
)
```
**Result:**
```
name   age   active
John   30    1
```

### 3. Nested Object Access
```sql
DECLARE @json NVARCHAR(MAX) = '{
    "user": {
        "name": "Alice",
        "contact": {
            "email": "alice@example.com",
            "phone": "555-0123"
        }
    }
}'

SELECT * FROM OPENJSON(@json, '$.user') 
WITH (
    name VARCHAR(50),
    email VARCHAR(100) '$.contact.email',
    phone VARCHAR(20) '$.contact.phone'
)
```
**Result:**
```
name   email              phone
Alice  alice@example.com  555-0123
```

## Advanced Examples

### 4. Array Processing
```sql
DECLARE @json NVARCHAR(MAX) = '{
    "users": [
        {"id": 1, "name": "John", "age": 30},
        {"id": 2, "name": "Jane", "age": 25},
        {"id": 3, "name": "Bob", "age": 35}
    ]
}'

SELECT * FROM OPENJSON(@json, '$.users') 
WITH (
    id INT,
    name VARCHAR(50),
    age INT
)
```
**Result:**
```
id   name   age
1    John   30
2    Jane   25
3    Bob    35
```

### 5. Mixed Data Types
```sql
DECLARE @json NVARCHAR(MAX) = '{
    "order": {
        "id": 12345,
        "date": "2025-07-11T10:30:00Z",
        "total": 299.99,
        "shipped": false,
        "items": ["laptop", "mouse", "keyboard"]
    }
}'

SELECT * FROM OPENJSON(@json, '$.order') 
WITH (
    order_id INT '$.id',
    order_date DATETIME2 '$.date',
    total_amount DECIMAL(10,2) '$.total',
    is_shipped BIT '$.shipped',
    items NVARCHAR(MAX) '$.items' AS JSON
)
```

### 6. Handling NULL Values
```sql
DECLARE @json NVARCHAR(MAX) = '{
    "name": "John",
    "middle_name": null,
    "age": 30
}'

SELECT * FROM OPENJSON(@json) 
WITH (
    name VARCHAR(50),
    middle_name VARCHAR(50),
    age INT
)
```

### 7. Cross Apply for Multiple Records
```sql
DECLARE @data TABLE (id INT, json_data NVARCHAR(MAX))
INSERT INTO @data VALUES 
(1, '{"name":"John","age":30}'),
(2, '{"name":"Jane","age":25}')

SELECT 
    d.id,
    j.name,
    j.age
FROM @data d
CROSS APPLY OPENJSON(d.json_data) 
WITH (
    name VARCHAR(50),
    age INT
) j
```

## Common Use Cases

### 8. Configuration Settings
```sql
DECLARE @config NVARCHAR(MAX) = '{
    "database": {
        "timeout": 30,
        "retry_count": 3
    },
    "logging": {
        "level": "INFO",
        "enabled": true
    }
}'

SELECT 
    setting_type,
    setting_name,
    setting_value
FROM OPENJSON(@config) 
WITH (
    database NVARCHAR(MAX) AS JSON,
    logging NVARCHAR(MAX) AS JSON
) config
CROSS APPLY (
    SELECT 'database' as setting_type, * FROM OPENJSON(config.database)
    UNION ALL
    SELECT 'logging' as setting_type, * FROM OPENJSON(config.logging)
) settings(setting_type, setting_name, setting_value, value_type)
```

### 9. Dynamic Column Selection
```sql
DECLARE @json NVARCHAR(MAX) = '{"a":1,"b":2,"c":3,"d":4}'

-- Get only specific keys
SELECT [key], [value] 
FROM OPENJSON(@json) 
WHERE [key] IN ('a', 'c')
```

## Error Handling

### 10. Invalid JSON Handling
```sql
DECLARE @json NVARCHAR(MAX) = '{"name":"John"' -- Invalid JSON

SELECT 
    CASE 
        WHEN ISJSON(@json) = 1 THEN 'Valid JSON'
        ELSE 'Invalid JSON'
    END as json_status

-- Only parse if valid
IF ISJSON(@json) = 1
BEGIN
    SELECT * FROM OPENJSON(@json)
END
```

## Best Practices

1. **Always validate JSON first** using `ISJSON()` function
2. **Use explicit schema** with `WITH` clause for better performance
3. **Specify appropriate data types** and lengths
4. **Handle NULL values** appropriately in your schema
5. **Use JSON path expressions** for nested property access
6. **Consider indexing** JSON columns for better query performance
7. **Use `AS JSON`** when you need to preserve JSON structure in results

## Performance Tips

- Use `WITH` clause instead of parsing raw key-value pairs
- Index computed columns based on JSON properties for frequent queries
- Consider using `JSON_VALUE()` for single property extraction
- Use `JSON_QUERY()` for extracting JSON fragments
