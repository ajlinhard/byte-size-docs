# Spark SQL File Loading
This file loading cheat sheet uses pure Spark SQL syntax instead of Python/PySpark. These are included in any Spark SQL implementation such as Databricks.

## Basic Syntaxes
### CTAS
```sql
CREATE TABLE [IF NOT EXISTS] table_name
[USING data_source]
[OPTIONS (key1=val1, key2=val2, ...)]
[PARTITIONED BY (col_name1, col_name2, ...)]
[LOCATION path]
AS SELECT ...
```

### CTAS + Direct Path
```sql
-- This will fail if 'sales' table already exists
CREATE TABLE sales AS
SELECT *
FROM parquet.`/path/to/data/`;
```

### Temp View
```sql
CREATE [OR REPLACE] TEMPORARY VIEW view_name
USING data_source_format
OPTIONS (
  key1 "value1",
  key2 "value2"
)
[AS SELECT ...]
```

### Temp View + Direct Path
```sql
-- Use view for current data access
CREATE OR REPLACE TEMPORARY VIEW current_sales 
AS SELECT * FROM parquet.`/path/to/sales/`
WHERE YEAR(sale_date) = 2024;
```

---
# Temp View Code
**Key Features:**
- **Pure SQL Syntax**: All examples use `CREATE TEMPORARY VIEW` and standard SQL queries
- **CSV Files**: Basic and advanced loading with OPTIONS, schema definition, multiple files
- **Parquet Files**: Simple loading, partitioned data, schema merging
- **JSON Files**: Basic and advanced options, nested JSON querying, array handling
- **AVRO Files**: Basic loading, schema definition, multiple files
- **Hive Tables**: Direct querying, partitioned tables, metadata operations
- **Delta Tables**: Basic queries and time travel features

**Additional SQL-focused sections:**
- Advanced querying patterns (UNION, window functions, pivots)
- Data quality checks using SQL aggregations
- Performance optimization with SQL configurations
- Error handling with corrupt record management
- Common ETL patterns in pure SQL
- Caching and performance tuning

All examples now use standard Spark SQL syntax that you can run directly in Spark SQL, Databricks notebooks, or any Spark SQL environment without requiring Python knowledge.

# Code
# Spark SQL File Loading Cheat Sheet

## Basic Setup

```sql
-- Set Spark SQL configurations
SET spark.sql.adaptive.enabled = true;
SET spark.sql.adaptive.coalescePartitions.enabled = true;
SET spark.sql.files.maxPartitionBytes = 134217728;
```

## CSV Files

### Basic CSV Loading
```sql
-- Create temporary view from CSV
CREATE OR REPLACE TEMPORARY VIEW csv_data
USING CSV
OPTIONS (
  path "path/to/file.csv",
  header "true",
  inferSchema "true"
);

-- Query the CSV data
SELECT * FROM csv_data;
```

### Advanced CSV Options
```sql
-- CSV with detailed options
CREATE OR REPLACE TEMPORARY VIEW csv_advanced
USING CSV
OPTIONS (
  path "path/to/file.csv",
  header "true",
  inferSchema "true",
  sep ",",
  quote '"',
  escape "\\",
  nullValue "NULL",
  dateFormat "yyyy-MM-dd",
  timestampFormat "yyyy-MM-dd HH:mm:ss",
  multiLine "true",
  ignoreLeadingWhiteSpace "true",
  ignoreTrailingWhiteSpace "true",
  encoding "UTF-8"
);

-- Query with transformations
SELECT 
  id,
  UPPER(name) as name_upper,
  CAST(value AS DOUBLE) as value_double
FROM csv_advanced
WHERE id IS NOT NULL;
```

### CSV with Schema Definition
```sql
-- Create table with explicit schema
CREATE OR REPLACE TEMPORARY VIEW csv_with_schema (
  id INT,
  name STRING,
  value DOUBLE,
  created_date DATE
)
USING CSV
OPTIONS (
  path "path/to/file.csv",
  header "true",
  dateFormat "yyyy-MM-dd"
);
```

### Multiple CSV Files
```sql
-- Load multiple CSV files
CREATE OR REPLACE TEMPORARY VIEW multi_csv
USING CSV
OPTIONS (
  path "path/to/directory/*.csv",
  header "true",
  inferSchema "true"
);

-- Load with pattern matching
CREATE OR REPLACE TEMPORARY VIEW pattern_csv
USING CSV
OPTIONS (
  path "path/to/data_*.csv",
  header "true",
  inferSchema "true"
);
```

## Parquet Files

### Basic Parquet Loading
```sql
-- Simple Parquet load
CREATE OR REPLACE TEMPORARY VIEW parquet_data
USING PARQUET
OPTIONS (
  path "path/to/file.parquet"
);

-- Query Parquet data
SELECT * FROM parquet_data;
```

### Parquet with Multiple Files
```sql
-- Load multiple Parquet files
CREATE OR REPLACE TEMPORARY VIEW multi_parquet
USING PARQUET
OPTIONS (
  path "path/to/directory/*.parquet"
);

-- Load directory with automatic partition discovery
CREATE OR REPLACE TEMPORARY VIEW partitioned_parquet
USING PARQUET
OPTIONS (
  path "path/to/partitioned_table/"
);
```

### Parquet with Schema Merging
```sql
-- Parquet with schema evolution
CREATE OR REPLACE TEMPORARY VIEW merged_parquet
USING PARQUET
OPTIONS (
  path "path/to/file.parquet",
  mergeSchema "true"
);
```

### Querying Partitioned Parquet
```sql
-- Create view for partitioned data
CREATE OR REPLACE TEMPORARY VIEW sales_data
USING PARQUET
OPTIONS (
  path "path/to/sales_partitioned/"
);

-- Query with partition pruning
SELECT * FROM sales_data
WHERE year = 2023 AND month = 1;

-- Aggregate by partition
SELECT 
  year,
  month,
  COUNT(*) as record_count,
  SUM(amount) as total_amount
FROM sales_data
WHERE year >= 2022
GROUP BY year, month
ORDER BY year, month;
```

## JSON Files

### Basic JSON Loading
```sql
-- Simple JSON load
CREATE OR REPLACE TEMPORARY VIEW json_data
USING JSON
OPTIONS (
  path "path/to/file.json"
);

-- Query JSON data
SELECT * FROM json_data;
```

### Advanced JSON Options
```sql
-- JSON with advanced options
CREATE OR REPLACE TEMPORARY VIEW json_advanced
USING JSON
OPTIONS (
  path "path/to/file.json",
  multiLine "true",
  allowComments "true",
  allowUnquotedFieldNames "true",
  allowSingleQuotes "true",
  allowNumericLeadingZeros "true",
  allowBackslashEscapingAnyCharacter "true",
  dateFormat "yyyy-MM-dd",
  timestampFormat "yyyy-MM-dd HH:mm:ss"
);
```

### JSON with Schema
```sql
-- JSON with predefined schema
CREATE OR REPLACE TEMPORARY VIEW json_schema (
  id BIGINT,
  name STRING,
  metadata STRUCT<
    created_at: STRING,
    updated_at: STRING,
    tags: ARRAY<STRING>
  >
)
USING JSON
OPTIONS (
  path "path/to/file.json"
);
```

### Nested JSON Querying
```sql
-- Create view for nested JSON
CREATE OR REPLACE TEMPORARY VIEW nested_json
USING JSON
OPTIONS (
  path "path/to/nested.json"
);

-- Query nested fields
SELECT 
  id,
  name,
  metadata.created_at,
  metadata.updated_at
FROM nested_json;

-- Explode arrays
SELECT 
  id,
  name,
  explode(metadata.tags) as tag
FROM nested_json;

-- Complex nested queries
SELECT 
  id,
  name,
  size(metadata.tags) as tag_count,
  array_contains(metadata.tags, 'important') as is_important
FROM nested_json;
```

## AVRO Files

### Basic AVRO Loading
```sql
-- Simple AVRO load
CREATE OR REPLACE TEMPORARY VIEW avro_data
USING AVRO
OPTIONS (
  path "path/to/file.avro"
);

-- Query AVRO data
SELECT * FROM avro_data;
```

### AVRO with Schema
```sql
-- AVRO with explicit schema
CREATE OR REPLACE TEMPORARY VIEW avro_with_schema
USING AVRO
OPTIONS (
  path "path/to/file.avro",
  avroSchema '{
    "type": "record",
    "name": "User",
    "fields": [
      {"name": "id", "type": "long"},
      {"name": "name", "type": "string"},
      {"name": "email", "type": "string"}
    ]
  }'
);
```

### Multiple AVRO Files
```sql
-- Load multiple AVRO files
CREATE OR REPLACE TEMPORARY VIEW multi_avro
USING AVRO
OPTIONS (
  path "path/to/directory/*.avro"
);

-- AVRO with namespace and record name
CREATE OR REPLACE TEMPORARY VIEW avro_advanced
USING AVRO
OPTIONS (
  path "path/to/file.avro",
  recordNamespace "com.example",
  recordName "MyRecord"
);
```

## Hive Tables

### Basic Table Queries
```sql
-- Query Hive table directly
SELECT * FROM database.table_name;

-- Query with database context
USE database_name;
SELECT * FROM table_name;

-- Query external table
SELECT * FROM external_table;
```

### Partitioned Hive Tables
```sql
-- Query specific partition
SELECT * FROM my_table 
WHERE dt = '2023-01-01';

-- Query multiple partitions
SELECT * FROM my_table 
WHERE dt BETWEEN '2023-01-01' AND '2023-01-31';

-- Query with partition pruning
SELECT * FROM sales_table
WHERE year = 2023 AND month = 1 AND day = 15;

-- Dynamic partition query
SELECT 
  year,
  month,
  COUNT(*) as record_count
FROM sales_table
WHERE year >= 2022
GROUP BY year, month
ORDER BY year, month;
```

### Hive Table Metadata
```sql
-- Describe table structure
DESCRIBE my_table;

-- Detailed table information
DESCRIBE FORMATTED my_table;

-- Show table partitions
SHOW PARTITIONS my_table;

-- Show table creation DDL
SHOW CREATE TABLE my_table;

-- Show table properties
SHOW TBLPROPERTIES my_table;

-- List all tables in database
SHOW TABLES IN database_name;

-- List all databases
SHOW DATABASES;
```

### Hive Table Operations
```sql
-- Refresh table metadata
REFRESH TABLE my_table;

-- Repair table partitions
MSCK REPAIR TABLE my_table;

-- Analyze table statistics
ANALYZE TABLE my_table COMPUTE STATISTICS;

-- Analyze column statistics
ANALYZE TABLE my_table COMPUTE STATISTICS FOR COLUMNS id, name, value;
```

## Delta Tables

### Basic Delta Queries
```sql
-- Create Delta table view
CREATE OR REPLACE TEMPORARY VIEW delta_table
USING DELTA
OPTIONS (
  path "path/to/delta-table"
);

-- Query Delta table
SELECT * FROM delta_table;
```

### Delta Time Travel
```sql
-- Query specific version
CREATE OR REPLACE TEMPORARY VIEW delta_version
USING DELTA
OPTIONS (
  path "path/to/delta-table",
  versionAsOf "0"
);

-- Query at specific timestamp
CREATE OR REPLACE TEMPORARY VIEW delta_timestamp
USING DELTA
OPTIONS (
  path "path/to/delta-table",
  timestampAsOf "2023-01-01 00:00:00"
);

-- Show Delta table history
DESCRIBE HISTORY delta_table;
```

## Advanced Querying Patterns

### Union Multiple Sources
```sql
-- Union CSV and Parquet data
SELECT id, name, value FROM csv_data
UNION ALL
SELECT id, name, value FROM parquet_data;

-- Union with type casting
SELECT 
  CAST(id AS BIGINT) as id,
  name,
  CAST(value AS DOUBLE) as value,
  'csv' as source
FROM csv_data
UNION ALL
SELECT 
  id,
  name,
  value,
  'parquet' as source
FROM parquet_data;
```

### Complex Aggregations
```sql
-- Window functions across file sources
SELECT 
  *,
  ROW_NUMBER() OVER (PARTITION BY category ORDER BY value DESC) as rank
FROM (
  SELECT * FROM csv_data
  UNION ALL
  SELECT * FROM parquet_data
);

-- Pivot data from JSON
SELECT *
FROM (
  SELECT id, explode(metadata.tags) as tag
  FROM json_data
)
PIVOT (
  COUNT(*) FOR tag IN ('important', 'urgent', 'review')
);
```

### Data Quality Checks
```sql
-- Check for nulls across sources
SELECT 
  'csv' as source,
  COUNT(*) as total_records,
  COUNT(id) as non_null_ids,
  COUNT(DISTINCT id) as unique_ids
FROM csv_data
UNION ALL
SELECT 
  'parquet' as source,
  COUNT(*) as total_records,
  COUNT(id) as non_null_ids,
  COUNT(DISTINCT id) as unique_ids
FROM parquet_data;

-- Data profiling
SELECT 
  COUNT(*) as total_records,
  COUNT(DISTINCT id) as unique_ids,
  MIN(value) as min_value,
  MAX(value) as max_value,
  AVG(value) as avg_value,
  STDDEV(value) as stddev_value
FROM csv_data;
```

## Performance Optimization

### Caching Views
```sql
-- Cache frequently used view
CACHE TABLE csv_data;

-- Uncache table
UNCACHE TABLE csv_data;

-- Clear all cache
CLEAR CACHE;
```

### Partitioning and Bucketing
```sql
-- Create partitioned table from source
CREATE TABLE partitioned_output
USING PARQUET
PARTITIONED BY (year, month)
AS SELECT *, 
  YEAR(date_column) as year,
  MONTH(date_column) as month
FROM csv_data;

-- Create bucketed table
CREATE TABLE bucketed_output
USING PARQUET
CLUSTERED BY (id) INTO 10 BUCKETS
AS SELECT * FROM csv_data;
```

### Configuration Settings
```sql
-- Optimize for small files
SET spark.sql.files.maxPartitionBytes = 134217728;
SET spark.sql.adaptive.coalescePartitions.enabled = true;

-- Enable adaptive query execution
SET spark.sql.adaptive.enabled = true;
SET spark.sql.adaptive.skewJoin.enabled = true;

-- Optimize shuffle partitions
SET spark.sql.adaptive.advisoryPartitionSizeInBytes = 67108864;

-- Enable predicate pushdown
SET spark.sql.parquet.filterPushdown = true;
SET spark.sql.parquet.aggregatePushdown = true;
```

## Error Handling

### Handling Corrupt Records
```sql
-- CSV with corrupt record handling
CREATE OR REPLACE TEMPORARY VIEW csv_with_errors
USING CSV
OPTIONS (
  path "path/to/file.csv",
  header "true",
  mode "PERMISSIVE",
  columnNameOfCorruptRecord "_corrupt_record"
);

-- Query and filter corrupt records
SELECT * FROM csv_with_errors
WHERE _corrupt_record IS NOT NULL;

-- JSON with error handling
CREATE OR REPLACE TEMPORARY VIEW json_permissive
USING JSON
OPTIONS (
  path "path/to/file.json",
  mode "PERMISSIVE",
  columnNameOfCorruptRecord "_corrupt_record"
);
```

### Schema Validation
```sql
-- Check schema compatibility
SELECT 
  'csv' as source,
  COUNT(*) as record_count,
  COUNT(CASE WHEN id IS NULL THEN 1 END) as null_ids
FROM csv_data
UNION ALL
SELECT 
  'json' as source,
  COUNT(*) as record_count,
  COUNT(CASE WHEN id IS NULL THEN 1 END) as null_ids
FROM json_data;
```

## Common Use Cases

### ETL Pipeline
```sql
-- Extract, Transform, Load pattern
CREATE OR REPLACE TEMPORARY VIEW raw_data
USING CSV
OPTIONS (
  path "path/to/raw/*.csv",
  header "true",
  inferSchema "true"
);

-- Transform data
CREATE OR REPLACE TEMPORARY VIEW transformed_data AS
SELECT 
  id,
  UPPER(TRIM(name)) as name,
  CAST(value AS DECIMAL(10,2)) as value,
  CURRENT_TIMESTAMP() as processed_at
FROM raw_data
WHERE id IS NOT NULL AND value > 0;

-- Load to target table
INSERT INTO target_table
SELECT * FROM transformed_data;
```

### Data Validation
```sql
-- Cross-format validation
SELECT 
  COUNT(*) as csv_count
FROM csv_data
UNION ALL
SELECT 
  COUNT(*) as parquet_count
FROM parquet_data;

-- Data quality report
SELECT 
  'Data Quality Report' as report,
  COUNT(*) as total_records,
  COUNT(DISTINCT id) as unique_records,
  SUM(CASE WHEN name IS NULL THEN 1 ELSE 0 END) as null_names,
  SUM(CASE WHEN value < 0 THEN 1 ELSE 0 END) as negative_values
FROM csv_data;
```
