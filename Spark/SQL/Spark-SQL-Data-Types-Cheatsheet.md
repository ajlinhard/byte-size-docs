# Spark SQL Data Types Cheatsheet
I've created a comprehensive Spark SQL data types cheatsheet that covers all the essential information you'll need. The cheatsheet includes:

**Key sections covered:**
- **Numeric types** (integers, floats, decimals) with size and range information
- **String types** (STRING, VARCHAR, CHAR) 
- **Date/time types** including the newer timestamp variants
- **Complex types** (arrays, maps, structs) with syntax examples
- **Type conversion** methods and implicit conversions
- **Common functions** organized by data type category
- **Schema definition** examples for both SQL and PySpark
- **Performance tips** for optimal data type usage

The cheatsheet is structured as a reference document that you can quickly scan to find the right data type for your needs, along with practical examples and common operations for each type. It's particularly useful for understanding the complex data types (arrays, maps, structs) which are powerful features of Spark SQL.

---
# Spark SQL Data Types Cheatsheet

## Numeric Data Types

### Integer Types
| Type | Size | Range | Example |
|------|------|-------|---------|
| `TINYINT` | 1 byte | -128 to 127 | `CAST(5 AS TINYINT)` |
| `SMALLINT` | 2 bytes | -32,768 to 32,767 | `CAST(1000 AS SMALLINT)` |
| `INT` / `INTEGER` | 4 bytes | -2,147,483,648 to 2,147,483,647 | `CAST(100000 AS INT)` |
| `BIGINT` | 8 bytes | -9,223,372,036,854,775,808 to 9,223,372,036,854,775,807 | `CAST(9999999999 AS BIGINT)` |

### Floating Point Types
| Type | Size | Precision | Example |
|------|------|-----------|---------|
| `FLOAT` | 4 bytes | Single precision | `CAST(3.14 AS FLOAT)` |
| `DOUBLE` | 8 bytes | Double precision | `CAST(3.14159265 AS DOUBLE)` |

### Decimal Type
| Type | Description | Example |
|------|-------------|---------|
| `DECIMAL(p,s)` | Fixed precision and scale | `DECIMAL(10,2)` for currency |
| `NUMERIC(p,s)` | Alias for DECIMAL | `NUMERIC(18,4)` |

## String Data Types

| Type | Description | Example |
|------|-------------|---------|
| `STRING` | Variable-length character string | `'Hello World'` |
| `VARCHAR(n)` | Variable-length with max length n | `VARCHAR(100)` |
| `CHAR(n)` | Fixed-length character string | `CHAR(10)` |

## Boolean Data Type

| Type | Values | Example |
|------|--------|---------|
| `BOOLEAN` | `TRUE`, `FALSE`, `NULL` | `CAST(1 AS BOOLEAN)` |

## Date and Time Data Types

| Type | Description | Format | Example |
|------|-------------|--------|---------|
| `DATE` | Calendar date | `YYYY-MM-DD` | `DATE '2024-01-15'` |
| `TIMESTAMP` | Date and time | `YYYY-MM-DD HH:MM:SS` | `TIMESTAMP '2024-01-15 14:30:00'` |
| `TIMESTAMP_LTZ` | Timestamp with local time zone | Same as TIMESTAMP | `TIMESTAMP_LTZ '2024-01-15 14:30:00'` |
| `TIMESTAMP_NTZ` | Timestamp without time zone | Same as TIMESTAMP | `TIMESTAMP_NTZ '2024-01-15 14:30:00'` |

## Binary Data Type

| Type | Description | Example |
|------|-------------|---------|
| `BINARY` | Fixed-length binary data | `CAST('hello' AS BINARY)` |

## Complex Data Types

### Array Type
```sql
-- Array of integers
ARRAY<INT>
-- Example: [1, 2, 3, 4]
SELECT ARRAY(1, 2, 3, 4) AS int_array;

-- Array of strings
ARRAY<STRING>
-- Example: ['apple', 'banana', 'orange']
SELECT ARRAY('apple', 'banana', 'orange') AS fruit_array;
```

### Map Type
```sql
-- Map with string keys and integer values
MAP<STRING, INT>
-- Example: {'key1': 1, 'key2': 2}
SELECT MAP('key1', 1, 'key2', 2) AS string_int_map;

-- Map with string keys and string values
MAP<STRING, STRING>
-- Example: {'name': 'John', 'city': 'NYC'}
SELECT MAP('name', 'John', 'city', 'NYC') AS info_map;
```

### Struct Type
```sql
-- Struct with named fields
STRUCT<field1: INT, field2: STRING>
-- Example: {field1: 123, field2: 'hello'}
SELECT STRUCT(123 AS field1, 'hello' AS field2) AS my_struct;

-- Nested struct
STRUCT<name: STRING, address: STRUCT<street: STRING, city: STRING>>
```

## Data Type Conversion

### Casting Functions
```sql
-- Basic casting
CAST(value AS target_type)
CAST('123' AS INT)
CAST(3.14 AS STRING)

-- Type conversion functions
INT(value)          -- Convert to integer
DOUBLE(value)       -- Convert to double
STRING(value)       -- Convert to string
BOOLEAN(value)      -- Convert to boolean
DATE(value)         -- Convert to date
TIMESTAMP(value)    -- Convert to timestamp
```

### Implicit Conversions
Spark SQL automatically converts between compatible types:
- Numeric types: `TINYINT` → `SMALLINT` → `INT` → `BIGINT` → `FLOAT` → `DOUBLE`
- String types: `CHAR` → `VARCHAR` → `STRING`
- Date/Time: `DATE` → `TIMESTAMP`

## Common Functions by Data Type

### String Functions
```sql
LENGTH(string)           -- String length
UPPER(string)           -- Convert to uppercase
LOWER(string)           -- Convert to lowercase
SUBSTR(string, pos, len) -- Extract substring
CONCAT(str1, str2, ...)  -- Concatenate strings
TRIM(string)            -- Remove leading/trailing spaces
```

### Numeric Functions
```sql
ABS(number)             -- Absolute value
ROUND(number, decimals) -- Round to specified decimals
CEIL(number)            -- Ceiling function
FLOOR(number)           -- Floor function
MOD(number, divisor)    -- Modulo operation
```

### Date/Time Functions
```sql
CURRENT_DATE()          -- Current date
CURRENT_TIMESTAMP()     -- Current timestamp
YEAR(date)              -- Extract year
MONTH(date)             -- Extract month
DAY(date)               -- Extract day
DATE_ADD(date, days)    -- Add days to date
DATE_SUB(date, days)    -- Subtract days from date
```

### Array Functions
```sql
SIZE(array)             -- Array size
ARRAY_CONTAINS(array, value) -- Check if array contains value
EXPLODE(array)          -- Convert array to rows
SORT_ARRAY(array)       -- Sort array elements
```

### Map Functions
```sql
MAP_KEYS(map)           -- Get map keys as array
MAP_VALUES(map)         -- Get map values as array
SIZE(map)               -- Number of key-value pairs
```

## NULL Handling

All Spark SQL data types can contain `NULL` values:
```sql
-- Check for NULL
IS NULL
IS NOT NULL

-- Handle NULL values
COALESCE(value1, value2, default_value)
ISNULL(value)
NULLIF(value1, value2)
```

## Schema Definition Examples

### Creating Tables
```sql
CREATE TABLE employees (
    id BIGINT,
    name STRING,
    salary DECIMAL(10,2),
    hire_date DATE,
    is_active BOOLEAN,
    skills ARRAY<STRING>,
    metadata MAP<STRING, STRING>,
    address STRUCT<street: STRING, city: STRING, zipcode: STRING>
);
```

### DataFrame Schema (PySpark)
```python
from pyspark.sql.types import *

schema = StructType([
    StructField("id", LongType(), True),
    StructField("name", StringType(), True),
    StructField("salary", DecimalType(10,2), True),
    StructField("hire_date", DateType(), True),
    StructField("is_active", BooleanType(), True),
    StructField("skills", ArrayType(StringType()), True),
    StructField("metadata", MapType(StringType(), StringType()), True),
    StructField("address", StructType([
        StructField("street", StringType(), True),
        StructField("city", StringType(), True),
        StructField("zipcode", StringType(), True)
    ]), True)
])
```

## Performance Tips

1. **Use appropriate data types**: Choose the smallest data type that can hold your data
2. **Avoid STRING for numeric data**: Use proper numeric types for better performance
3. **Consider DECIMAL for financial data**: More precise than FLOAT/DOUBLE
4. **Use partitioning with DATE columns**: Improves query performance on time-based data
5. **Be careful with complex types**: Arrays, Maps, and Structs can impact performance if overused
