# Amazon Athena SQL Commands Cheatsheet

## Creating Tables for Different Data Formats

### CSV Files
```sql
CREATE EXTERNAL TABLE csv_table (
    id INT,
    name STRING,
    age INT,
    email STRING
)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe'
WITH SERDEPROPERTIES (
    'serialization.format' = ',',
    'field.delim' = ','
) 
LOCATION 's3://your-bucket/csv-data/'
TBLPROPERTIES ('has_encrypted_data'='false');

-- CSV with headers
CREATE EXTERNAL TABLE csv_with_headers (
    id INT,
    name STRING,
    age INT
)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe'
WITH SERDEPROPERTIES (
    'serialization.format' = ',',
    'field.delim' = ',',
    'skip.header.line.count' = '1'
)
LOCATION 's3://your-bucket/csv-headers-data/';
```

### Parquet Files
```sql
CREATE EXTERNAL TABLE parquet_table (
    id BIGINT,
    name STRING,
    age INT,
    created_date DATE
)
STORED AS PARQUET
LOCATION 's3://your-bucket/parquet-data/';

-- Partitioned Parquet
CREATE EXTERNAL TABLE partitioned_parquet (
    id BIGINT,
    name STRING,
    age INT
)
PARTITIONED BY (
    year INT,
    month INT
)
STORED AS PARQUET
LOCATION 's3://your-bucket/partitioned-parquet/';
```

### Avro Files
```sql
CREATE EXTERNAL TABLE avro_table (
    id BIGINT,
    name STRING,
    age INT,
    metadata STRUCT<
        created_by: STRING,
        created_at: TIMESTAMP
    >
)
STORED AS AVRO
LOCATION 's3://your-bucket/avro-data/';
```

### JSON Files
```sql
CREATE EXTERNAL TABLE json_table (
    id BIGINT,
    name STRING,
    age INT,
    address STRUCT<
        street: STRING,
        city: STRING,
        zipcode: STRING
    >
)
ROW FORMAT SERDE 'org.openx.data.jsonserde.JsonSerDe'
LOCATION 's3://your-bucket/json-data/';
```

### Hive-Style Partitioned Data
```sql
CREATE EXTERNAL TABLE hive_partitioned (
    id BIGINT,
    name STRING,
    transaction_amount DECIMAL(10,2)
)
PARTITIONED BY (
    year STRING,
    month STRING,
    day STRING
)
STORED AS PARQUET
LOCATION 's3://your-bucket/hive-partitioned/';

-- Add partitions manually
ALTER TABLE hive_partitioned ADD PARTITION (year='2024', month='01', day='15')
LOCATION 's3://your-bucket/hive-partitioned/year=2024/month=01/day=15/';

-- Automatically discover partitions
MSCK REPAIR TABLE hive_partitioned;
```

## Reading Data (SELECT Operations)

### Basic SELECT
```sql
-- Simple select
SELECT * FROM my_table LIMIT 10;

-- Select specific columns
SELECT id, name, age FROM users WHERE age > 25;

-- With conditions and sorting
SELECT name, email, age 
FROM users 
WHERE age BETWEEN 25 AND 65 
    AND email LIKE '%@company.com'
ORDER BY age DESC
LIMIT 100;
```

### Aggregations
```sql
-- Count and group by
SELECT department, COUNT(*) as employee_count, AVG(salary) as avg_salary
FROM employees
GROUP BY department
HAVING COUNT(*) > 10;

-- Window functions
SELECT 
    name,
    salary,
    department,
    ROW_NUMBER() OVER (PARTITION BY department ORDER BY salary DESC) as rank_in_dept
FROM employees;
```

### Date/Time Operations
```sql
-- Date filtering and formatting
SELECT *
FROM transactions
WHERE date_parse(transaction_date, '%Y-%m-%d') >= DATE '2024-01-01'
    AND date_parse(transaction_date, '%Y-%m-%d') < DATE '2024-02-01';

-- Extract date parts
SELECT 
    transaction_id,
    YEAR(transaction_date) as year,
    MONTH(transaction_date) as month,
    DAY(transaction_date) as day
FROM transactions;
```

## JOIN Operations

### Inner Join
```sql
SELECT 
    u.name,
    u.email,
    o.order_id,
    o.total_amount
FROM users u
INNER JOIN orders o ON u.user_id = o.user_id
WHERE o.order_date >= DATE '2024-01-01';
```

### Left Join
```sql
SELECT 
    u.name,
    u.email,
    COALESCE(o.total_orders, 0) as total_orders
FROM users u
LEFT JOIN (
    SELECT user_id, COUNT(*) as total_orders
    FROM orders
    GROUP BY user_id
) o ON u.user_id = o.user_id;
```

### Multiple Joins
```sql
SELECT 
    u.name,
    o.order_id,
    p.product_name,
    oi.quantity
FROM users u
JOIN orders o ON u.user_id = o.user_id
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p ON oi.product_id = p.product_id
WHERE o.order_date >= DATE '2024-01-01';
```

## Writing Data (CTAS - Create Table As Select)

### Basic CTAS
```sql
-- Create new table from query results
CREATE TABLE processed_data AS
SELECT 
    user_id,
    COUNT(*) as order_count,
    SUM(total_amount) as total_spent,
    MAX(order_date) as last_order_date
FROM orders
WHERE order_date >= DATE '2024-01-01'
GROUP BY user_id;
```

### CTAS with Different Formats
```sql
-- Save as Parquet
CREATE TABLE sales_summary 
WITH (
    format = 'PARQUET',
    external_location = 's3://your-bucket/sales-summary/'
) AS
SELECT 
    product_category,
    YEAR(sale_date) as year,
    MONTH(sale_date) as month,
    SUM(amount) as total_sales
FROM sales
GROUP BY product_category, YEAR(sale_date), MONTH(sale_date);
```

### Partitioned CTAS
```sql
-- Create partitioned table
CREATE TABLE partitioned_sales
WITH (
    format = 'PARQUET',
    external_location = 's3://your-bucket/partitioned-sales/',
    partitioned_by = ARRAY['year', 'month']
) AS
SELECT 
    product_id,
    product_name,
    sale_amount,
    YEAR(sale_date) as year,
    MONTH(sale_date) as month
FROM sales
WHERE sale_date >= DATE '2024-01-01';
```

## INSERT Operations

### Insert with SELECT
```sql
INSERT INTO target_table
SELECT 
    col1,
    col2,
    col3,
    CURRENT_TIMESTAMP as created_at
FROM source_table
WHERE condition = 'value';
```

### Insert into Partitioned Table
```sql
INSERT INTO partitioned_table
SELECT 
    data_column1,
    data_column2,
    partition_column1,
    partition_column2
FROM source_table
WHERE date_column >= DATE '2024-01-01';
```

## Common Table Expressions (CTEs)

```sql
WITH recent_orders AS (
    SELECT user_id, COUNT(*) as order_count
    FROM orders
    WHERE order_date >= DATE '2024-01-01'
    GROUP BY user_id
),
high_value_users AS (
    SELECT user_id
    FROM recent_orders
    WHERE order_count >= 5
)
SELECT 
    u.name,
    u.email,
    ro.order_count
FROM users u
JOIN high_value_users hvu ON u.user_id = hvu.user_id
JOIN recent_orders ro ON u.user_id = ro.user_id;
```

## Working with Complex Data Types

### Arrays
```sql
-- Query arrays
SELECT 
    user_id,
    CARDINALITY(interests) as interest_count,
    ARRAY_JOIN(interests, ', ') as interests_list
FROM user_profiles
WHERE CONTAINS(interests, 'technology');
```

### Maps/Structs
```sql
-- Query nested structures
SELECT 
    user_id,
    address.street,
    address.city,
    address.zipcode
FROM users
WHERE address.city = 'New York';
```

## Utility Commands

### Table Management
```sql
-- Show tables
SHOW TABLES;

-- Describe table structure
DESCRIBE my_table;

-- Show table properties
SHOW TBLPROPERTIES my_table;

-- Show partitions
SHOW PARTITIONS my_partitioned_table;
```

### Performance Optimization
```sql
-- Analyze table for cost-based optimization
ANALYZE TABLE my_table COMPUTE STATISTICS;

-- Create table with compression
CREATE TABLE compressed_data
WITH (
    format = 'PARQUET',
    parquet_compression = 'SNAPPY'
) AS
SELECT * FROM source_table;
```

## Important Notes

- **No UPDATE/DELETE**: Athena doesn't support UPDATE or DELETE operations on existing data
- **Use CTAS**: To modify data, use CREATE TABLE AS SELECT with transformations
- **Partitioning**: Use partitioning for better performance on large datasets
- **Data Types**: Be careful with data type conversions, especially dates and timestamps
- **Cost Optimization**: Use columnar formats (Parquet) and partition pruning to reduce costs
- **Projections**: Only select columns you need to minimize data scanned
