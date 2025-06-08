# Spark Create Table (SQL)
Commonly in data systems we need to create tables. While less common in Spark, if you start using spark with a standard data model you may start deploying create tables. Here isa comprehensive cheat sheet for Spark CREATE TABLE statements, covering all the advanced features you mentioned.I've created a comprehensive cheat sheet for Spark CREATE TABLE statements that covers all the advanced features you requested. The guide includes:

**Key Features Covered:**
- **Nullability**: Explicit NOT NULL constraints and nullable column handling
- **Default Values**: Column defaults with expressions and current_timestamp()
- **Constraints**: Primary keys, check constraints, and complex validation rules
- **Partitioning**: Single and multiple partition columns with constraint validation
- **Bucketing**: Performance optimization through clustering and sorting
- **Complex Data Types**: Arrays, Maps, Structs, and nested structures
- **Generated Columns**: Computed columns for derived values
- **Identity Columns**: Auto-increment functionality
- **Table Properties**: Delta Lake optimization settings and metadata

**Special Highlights:**
- Production-ready example showing how to combine all features
- Different storage formats (Delta, Parquet, JSON, Hive)
- Troubleshooting section for constraint violations
- Best practices for audit trails and data integrity

The cheat sheet focuses on Delta Lake syntax since it supports the most advanced features like constraints and generated columns, but also includes examples for other formats. Each section builds from simple to complex examples, making it easy to find the right pattern for your specific use case.
--
# Spark CREATE TABLE Statements Cheat Sheet

## Basic Table Creation

```python
# Simple table creation
spark.sql("""
CREATE TABLE employees (
    id BIGINT,
    name STRING,
    department STRING,
    salary DECIMAL(10,2),
    hire_date DATE
) USING DELTA
""")
```

## Handling Nullability

```python
# Explicit NULL/NOT NULL constraints
spark.sql("""
CREATE TABLE employees (
    id BIGINT NOT NULL,
    name STRING NOT NULL,
    email STRING,  -- nullable by default
    department STRING NOT NULL,
    salary DECIMAL(10,2),
    manager_id BIGINT  -- nullable foreign key
) USING DELTA
""")

# Using DataFrame API with nullable control
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, BooleanType

schema = StructType([
    StructField("id", IntegerType(), nullable=False),
    StructField("name", StringType(), nullable=False),
    StructField("email", StringType(), nullable=True),
    StructField("active", BooleanType(), nullable=False)
])

df = spark.createDataFrame([], schema)
df.write.saveAsTable("users")
```

## Default Values

```python
# Column defaults (Delta Lake specific)
spark.sql("""
CREATE TABLE products (
    id BIGINT NOT NULL,
    name STRING NOT NULL,
    price DECIMAL(10,2) DEFAULT 0.00,
    category STRING DEFAULT 'uncategorized',
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT current_timestamp(),
    updated_at TIMESTAMP DEFAULT current_timestamp()
) USING DELTA
""")

# Default values with expressions
spark.sql("""
CREATE TABLE orders (
    order_id BIGINT NOT NULL,
    customer_id BIGINT NOT NULL,
    order_date DATE DEFAULT current_date(),
    status STRING DEFAULT 'pending',
    total DECIMAL(12,2) DEFAULT 0.00,
    tax_rate DECIMAL(5,4) DEFAULT 0.0875
) USING DELTA
""")
```

## Primary Keys and Constraints

```python
# Primary key constraint (Delta Lake 2.0+)
spark.sql("""
CREATE TABLE customers (
    customer_id BIGINT NOT NULL,
    email STRING NOT NULL,
    first_name STRING NOT NULL,
    last_name STRING NOT NULL,
    created_at TIMESTAMP DEFAULT current_timestamp(),
    CONSTRAINT customers_pk PRIMARY KEY(customer_id)
) USING DELTA
""")

# Composite primary key
spark.sql("""
CREATE TABLE order_items (
    order_id BIGINT NOT NULL,
    product_id BIGINT NOT NULL,
    quantity INT NOT NULL DEFAULT 1,
    unit_price DECIMAL(10,2) NOT NULL,
    CONSTRAINT order_items_pk PRIMARY KEY(order_id, product_id)
) USING DELTA
""")
```

## Check Constraints

```python
# Single check constraint
spark.sql("""
CREATE TABLE products (
    id BIGINT NOT NULL,
    name STRING NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    CONSTRAINT price_positive CHECK (price > 0)
) USING DELTA
""")

# Multiple check constraints
spark.sql("""
CREATE TABLE employees (
    id BIGINT NOT NULL,
    name STRING NOT NULL,
    age INT,
    salary DECIMAL(10,2),
    department STRING,
    CONSTRAINT age_valid CHECK (age >= 18 AND age <= 100),
    CONSTRAINT salary_positive CHECK (salary > 0),
    CONSTRAINT dept_valid CHECK (department IN ('HR', 'Engineering', 'Sales', 'Marketing'))
) USING DELTA
""")

# Complex check constraints
spark.sql("""
CREATE TABLE transactions (
    id BIGINT NOT NULL,
    amount DECIMAL(12,2) NOT NULL,
    transaction_type STRING NOT NULL,
    fee DECIMAL(8,2) DEFAULT 0.00,
    CONSTRAINT amount_fee_valid CHECK (
        (transaction_type = 'credit' AND amount > 0) OR
        (transaction_type = 'debit' AND amount < 0)
    ),
    CONSTRAINT fee_reasonable CHECK (fee >= 0 AND fee < amount * 0.1)
) USING DELTA
""")
```

## Partitioned Tables

```python
# Single partition column
spark.sql("""
CREATE TABLE sales (
    id BIGINT NOT NULL,
    product_id BIGINT NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    sale_date DATE NOT NULL
) USING DELTA
PARTITIONED BY (sale_date)
""")

# Multiple partition columns
spark.sql("""
CREATE TABLE events (
    id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    event_type STRING NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    year INT NOT NULL,
    month INT NOT NULL,
    day INT NOT NULL
) USING DELTA
PARTITIONED BY (year, month, day)
""")

# Partition with constraints
spark.sql("""
CREATE TABLE logs (
    id BIGINT NOT NULL,
    message STRING NOT NULL,
    level STRING NOT NULL DEFAULT 'INFO',
    timestamp TIMESTAMP NOT NULL DEFAULT current_timestamp(),
    date_partition DATE NOT NULL,
    CONSTRAINT level_valid CHECK (level IN ('DEBUG', 'INFO', 'WARN', 'ERROR')),
    CONSTRAINT date_consistent CHECK (date_partition = DATE(timestamp))
) USING DELTA
PARTITIONED BY (date_partition)
""")
```

## Bucketed Tables

```python
# Bucketed table for performance
spark.sql("""
CREATE TABLE user_events (
    user_id BIGINT NOT NULL,
    event_id BIGINT NOT NULL,
    event_type STRING NOT NULL,
    timestamp TIMESTAMP NOT NULL
) USING DELTA
CLUSTERED BY (user_id) INTO 10 BUCKETS
""")

# Bucketed and sorted
spark.sql("""
CREATE TABLE large_dataset (
    id BIGINT NOT NULL,
    category STRING NOT NULL,
    value DOUBLE NOT NULL,
    created_at TIMESTAMP NOT NULL
) USING DELTA
CLUSTERED BY (category) SORTED BY (created_at) INTO 20 BUCKETS
""")
```

## Table Properties and Options

```python
# Table with properties
spark.sql("""
CREATE TABLE config_table (
    id BIGINT NOT NULL,
    config_key STRING NOT NULL,
    config_value STRING,
    updated_at TIMESTAMP DEFAULT current_timestamp()
) USING DELTA
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true',
    'delta.logRetentionDuration' = '30 days',
    'comment' = 'Configuration settings table'
)
""")

# Table with location
spark.sql("""
CREATE TABLE external_data (
    id BIGINT NOT NULL,
    data STRING NOT NULL
) USING DELTA
LOCATION '/path/to/external/table'
TBLPROPERTIES (
    'path' = '/path/to/external/table'
)
""")
```

## Complex Data Types

```python
# Arrays, Maps, and Structs
spark.sql("""
CREATE TABLE complex_data (
    id BIGINT NOT NULL,
    tags ARRAY<STRING>,
    metadata MAP<STRING, STRING>,
    address STRUCT<
        street: STRING,
        city: STRING,
        state: STRING,
        zip: STRING
    >,
    phone_numbers ARRAY<STRUCT<
        type: STRING,
        number: STRING
    >>
) USING DELTA
""")

# Nested structures with constraints
spark.sql("""
CREATE TABLE user_profiles (
    user_id BIGINT NOT NULL,
    profile STRUCT<
        first_name: STRING,
        last_name: STRING,
        age: INT,
        preferences: MAP<STRING, STRING>
    >,
    addresses ARRAY<STRUCT<
        type: STRING,
        street: STRING,
        city: STRING,
        country: STRING
    >>,
    CONSTRAINT user_id_positive CHECK (user_id > 0)
) USING DELTA
""")
```

## Generated Columns

```python
# Generated columns (Delta Lake specific)
spark.sql("""
CREATE TABLE sales_summary (
    id BIGINT NOT NULL,
    gross_amount DECIMAL(10,2) NOT NULL,
    tax_rate DECIMAL(5,4) NOT NULL DEFAULT 0.08,
    tax_amount DECIMAL(10,2) GENERATED ALWAYS AS (gross_amount * tax_rate),
    net_amount DECIMAL(10,2) GENERATED ALWAYS AS (gross_amount + tax_amount),
    sale_date DATE NOT NULL,
    year INT GENERATED ALWAYS AS (YEAR(sale_date)),
    month INT GENERATED ALWAYS AS (MONTH(sale_date))
) USING DELTA
PARTITIONED BY (year, month)
""")
```

## Identity Columns

```python
# Identity/Auto-increment columns (Delta Lake 2.4+)
spark.sql("""
CREATE TABLE auto_increment_example (
    id BIGINT GENERATED ALWAYS AS IDENTITY (START WITH 1 INCREMENT BY 1),
    name STRING NOT NULL,
    created_at TIMESTAMP DEFAULT current_timestamp()
) USING DELTA
""")

# Identity with custom settings
spark.sql("""
CREATE TABLE orders_with_id (
    order_id BIGINT GENERATED ALWAYS AS IDENTITY (START WITH 1000 INCREMENT BY 10),
    customer_id BIGINT NOT NULL,
    order_date DATE DEFAULT current_date(),
    total DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    CONSTRAINT total_positive CHECK (total >= 0)
) USING DELTA
""")
```

## Create Table As (CTAS)

```python
# Create table from query with constraints
spark.sql("""
CREATE TABLE monthly_summary
USING DELTA
AS
SELECT 
    YEAR(order_date) as year,
    MONTH(order_date) as month,
    SUM(total) as total_revenue,
    COUNT(*) as order_count,
    AVG(total) as avg_order_value
FROM orders 
GROUP BY YEAR(order_date), MONTH(order_date)
""")

# Add constraints after CTAS
spark.sql("ALTER TABLE monthly_summary ADD CONSTRAINT revenue_positive CHECK (total_revenue >= 0)")
```

## Different Storage Formats

```python
# Parquet table
spark.sql("""
CREATE TABLE parquet_table (
    id BIGINT NOT NULL,
    data STRING
) USING PARQUET
PARTITIONED BY (year INT, month INT)
""")

# JSON table
spark.sql("""
CREATE TABLE json_table (
    id BIGINT NOT NULL,
    payload STRING
) USING JSON
""")

# External Hive table
spark.sql("""
CREATE TABLE hive_external (
    id BIGINT,
    name STRING,
    value DOUBLE
) USING HIVE
LOCATION '/path/to/hive/table'
""")
```

## Best Practices Examples

```python
# Production-ready table with all features
spark.sql("""
CREATE TABLE production_orders (
    -- Primary key
    order_id BIGINT NOT NULL,
    
    -- Foreign keys
    customer_id BIGINT NOT NULL,
    product_id BIGINT NOT NULL,
    
    -- Business fields with defaults
    quantity INT NOT NULL DEFAULT 1,
    unit_price DECIMAL(10,2) NOT NULL,
    discount_rate DECIMAL(5,4) DEFAULT 0.0000,
    
    -- Calculated fields
    gross_amount DECIMAL(12,2) GENERATED ALWAYS AS (quantity * unit_price),
    discount_amount DECIMAL(12,2) GENERATED ALWAYS AS (gross_amount * discount_rate),
    net_amount DECIMAL(12,2) GENERATED ALWAYS AS (gross_amount - discount_amount),
    
    -- Audit fields
    created_at TIMESTAMP NOT NULL DEFAULT current_timestamp(),
    updated_at TIMESTAMP NOT NULL DEFAULT current_timestamp(),
    created_by STRING NOT NULL DEFAULT current_user(),
    
    -- Partition fields
    order_date DATE NOT NULL,
    year INT GENERATED ALWAYS AS (YEAR(order_date)),
    month INT GENERATED ALWAYS AS (MONTH(order_date)),
    
    -- Constraints
    CONSTRAINT orders_pk PRIMARY KEY (order_id),
    CONSTRAINT quantity_positive CHECK (quantity > 0),
    CONSTRAINT unit_price_positive CHECK (unit_price > 0),
    CONSTRAINT discount_valid CHECK (discount_rate >= 0 AND discount_rate <= 1),
    CONSTRAINT date_consistency CHECK (order_date = DATE(created_at))
    
) USING DELTA
PARTITIONED BY (year, month)
CLUSTERED BY (customer_id) INTO 50 BUCKETS
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true',
    'delta.deletedFileRetentionDuration' = '7 days',
    'comment' = 'Production orders table with full audit trail'
)
""")
```

## Troubleshooting Common Issues

```python
# Check table constraints
spark.sql("DESCRIBE DETAIL my_table").show()

# Verify constraint violations before insert
spark.sql("""
SELECT COUNT(*) as violation_count 
FROM source_data 
WHERE NOT (price > 0 AND quantity > 0)
""")

# Handle constraint violations
spark.sql("""
INSERT INTO target_table
SELECT * FROM source_data
WHERE price > 0 AND quantity > 0  -- Filter out constraint violations
""")
```
