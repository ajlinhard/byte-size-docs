# Spark SQL MERGE (aka MERGE INTO)
I've created a comprehensive cheat sheet for the MERGE statement in Spark SQL. The document covers:

**Structure Overview:**
- Basic syntax breakdown with clear explanations of each component
- Key concepts like target tables, source tables, and merge conditions

**Practical Examples:**
- Simple upsert operations
- Conditional updates and deletes
- Complex scenarios with subqueries and multiple conditions
- Both SQL and PySpark DataFrame API approaches

**Real-World Use Cases:**
- CDC (Change Data Capture) processing
- Slowly Changing Dimensions (SCD)
- Incremental data processing patterns

**Performance and Best Practices:**
- Optimization techniques for large datasets
- Common patterns for different scenarios
- Error handling and troubleshooting tips

**Requirements and Limitations:**
- Technical requirements (Delta Lake, Spark versions)
- Known limitations and workarounds

The cheat sheet is designed to be a practical reference that you can use for both learning MERGE operations and as a quick lookup guide during development. Each example includes realistic scenarios you might encounter in data engineering workflows.

---
# Spark SQL MERGE Command Cheat Sheet

## Overview
The MERGE statement in Spark SQL allows you to perform upsert operations (insert, update, delete) on Delta tables based on a join condition. It's particularly useful for CDC (Change Data Capture) scenarios and data synchronization.

## Basic Syntax Breakdown

```sql
MERGE INTO target_table AS target
USING source_table AS source
ON merge_condition
WHEN MATCHED [AND condition] THEN
  UPDATE SET column1 = value1, column2 = value2, ...
WHEN MATCHED [AND condition] THEN
  DELETE
WHEN NOT MATCHED [AND condition] THEN
  INSERT (column1, column2, ...) VALUES (value1, value2, ...)
```

### Key Components:
- **target_table**: The table being updated (must be a Delta table)
- **source_table**: The table/view/subquery providing new data
- **merge_condition**: JOIN condition to match records
- **WHEN MATCHED**: Actions for records that exist in both tables
- **WHEN NOT MATCHED**: Actions for records that exist only in source

## Python/PySpark Setup

```python
from pyspark.sql import SparkSession
from delta import *

# Create SparkSession with Delta support
spark = SparkSession.builder \
    .appName("MERGE Example") \
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
    .getOrCreate()

# Enable Delta table features
spark.sql("SET spark.sql.adaptive.enabled=true")
spark.sql("SET spark.sql.adaptive.coalescePartitions.enabled=true")
```

## Basic Examples

### Simple Upsert (Insert or Update)
```sql
MERGE INTO customers AS target
USING customer_updates AS source
ON target.customer_id = source.customer_id
WHEN MATCHED THEN
  UPDATE SET 
    name = source.name,
    email = source.email,
    updated_at = current_timestamp()
WHEN NOT MATCHED THEN
  INSERT (customer_id, name, email, created_at)
  VALUES (source.customer_id, source.name, source.email, current_timestamp())
```

### Conditional Update with Delete
```sql
MERGE INTO inventory AS target
USING inventory_changes AS source
ON target.product_id = source.product_id
WHEN MATCHED AND source.quantity = 0 THEN
  DELETE
WHEN MATCHED THEN
  UPDATE SET 
    quantity = source.quantity,
    last_updated = source.timestamp
WHEN NOT MATCHED THEN
  INSERT (product_id, quantity, last_updated)
  VALUES (source.product_id, source.quantity, source.timestamp)
```

## Advanced Examples

### Using Subquery as Source
```sql
MERGE INTO sales_summary AS target
USING (
  SELECT 
    product_id,
    SUM(quantity) as total_quantity,
    SUM(revenue) as total_revenue,
    COUNT(*) as order_count
  FROM daily_sales 
  WHERE sale_date = current_date()
  GROUP BY product_id
) AS source
ON target.product_id = source.product_id
WHEN MATCHED THEN
  UPDATE SET 
    total_quantity = target.total_quantity + source.total_quantity,
    total_revenue = target.total_revenue + source.total_revenue,
    order_count = target.order_count + source.order_count
WHEN NOT MATCHED THEN
  INSERT (product_id, total_quantity, total_revenue, order_count)
  VALUES (source.product_id, source.total_quantity, source.total_revenue, source.order_count)
```

### Multiple WHEN MATCHED Conditions
```sql
MERGE INTO employee_records AS target
USING employee_updates AS source
ON target.employee_id = source.employee_id
WHEN MATCHED AND source.status = 'TERMINATED' THEN
  UPDATE SET 
    status = source.status,
    termination_date = source.effective_date
WHEN MATCHED AND source.status = 'ACTIVE' THEN
  UPDATE SET 
    department = source.department,
    salary = source.salary,
    last_updated = current_timestamp()
WHEN NOT MATCHED AND source.status = 'ACTIVE' THEN
  INSERT (employee_id, name, department, salary, status, hire_date)
  VALUES (source.employee_id, source.name, source.department, source.salary, source.status, source.effective_date)
```

## PySpark DataFrame API Examples

### Basic MERGE with DeltaTable
```python
from delta.tables import DeltaTable

# Load Delta table
delta_table = DeltaTable.forPath(spark, "/path/to/delta/table")

# Perform merge
delta_table.alias("target") \
  .merge(
    source_df.alias("source"),
    "target.id = source.id"
  ) \
  .whenMatchedUpdate(set={
    "name": "source.name",
    "updated_at": "current_timestamp()"
  }) \
  .whenNotMatchedInsert(values={
    "id": "source.id",
    "name": "source.name",
    "created_at": "current_timestamp()"
  }) \
  .execute()
```

### Conditional MERGE with DataFrame API
```python
delta_table.alias("target") \
  .merge(
    updates_df.alias("source"),
    "target.product_id = source.product_id"
  ) \
  .whenMatchedUpdate(
    condition="source.quantity > 0",
    set={
      "quantity": "source.quantity",
      "last_updated": "source.timestamp"
    }
  ) \
  .whenMatchedDelete(
    condition="source.quantity = 0"
  ) \
  .whenNotMatchedInsert(
    condition="source.quantity > 0",
    values={
      "product_id": "source.product_id",
      "quantity": "source.quantity",
      "last_updated": "source.timestamp"
    }
  ) \
  .execute()
```

## Real-World Use Cases

### CDC (Change Data Capture) Processing
```sql
-- Process CDC events from a message queue
MERGE INTO customer_master AS target
USING (
  SELECT 
    customer_id,
    name,
    email,
    operation,  -- 'I' for insert, 'U' for update, 'D' for delete
    timestamp
  FROM cdc_events
  WHERE processed_date = current_date()
) AS source
ON target.customer_id = source.customer_id
WHEN MATCHED AND source.operation = 'D' THEN
  DELETE
WHEN MATCHED AND source.operation IN ('U', 'I') THEN
  UPDATE SET 
    name = source.name,
    email = source.email,
    last_modified = source.timestamp
WHEN NOT MATCHED AND source.operation = 'I' THEN
  INSERT (customer_id, name, email, created_at)
  VALUES (source.customer_id, source.name, source.email, source.timestamp)
```

### Slowly Changing Dimension (SCD) Type 2
```sql
MERGE INTO dim_customer AS target
USING (
  SELECT 
    customer_id,
    name,
    address,
    current_date() as effective_date,
    '9999-12-31' as end_date,
    true as is_current
  FROM customer_changes
) AS source
ON target.customer_id = source.customer_id AND target.is_current = true
WHEN MATCHED AND (target.name != source.name OR target.address != source.address) THEN
  UPDATE SET 
    end_date = date_sub(source.effective_date, 1),
    is_current = false
WHEN NOT MATCHED THEN
  INSERT (customer_id, name, address, effective_date, end_date, is_current)
  VALUES (source.customer_id, source.name, source.address, source.effective_date, source.end_date, source.is_current)
```

## Performance Optimization Tips

### 1. Optimize JOIN Conditions
```sql
-- Use partition columns in join condition when possible
MERGE INTO sales_partitioned AS target
USING sales_updates AS source
ON target.product_id = source.product_id 
   AND target.sale_date = source.sale_date  -- partition column
```

### 2. Use Efficient Source Queries
```python
# Pre-filter and deduplicate source data
source_df = spark.sql("""
  SELECT DISTINCT
    customer_id,
    name,
    email,
    row_number() OVER (PARTITION BY customer_id ORDER BY timestamp DESC) as rn
  FROM raw_updates
  WHERE date = current_date()
""").filter("rn = 1").drop("rn")
```

### 3. Partition Pruning
```sql
-- Include partition filters in MERGE when possible
MERGE INTO transactions AS target
USING (
  SELECT * FROM transaction_updates 
  WHERE partition_date >= '2023-01-01'
) AS source
ON target.transaction_id = source.transaction_id
```

## Common Patterns and Best Practices

### Pattern 1: Full Refresh with History
```sql
-- Keep history while refreshing current data
MERGE INTO product_catalog AS target
USING (
  SELECT *, current_timestamp() as load_timestamp
  FROM latest_product_data
) AS source
ON target.product_id = source.product_id
WHEN MATCHED THEN
  UPDATE SET *
WHEN NOT MATCHED THEN
  INSERT *
```

### Pattern 2: Incremental Updates with Watermark
```sql
MERGE INTO user_activity AS target
USING (
  SELECT 
    user_id,
    last_activity,
    activity_count
  FROM activity_stream
  WHERE last_activity > (SELECT MAX(last_activity) FROM user_activity)
) AS source
ON target.user_id = source.user_id
WHEN MATCHED THEN
  UPDATE SET 
    last_activity = GREATEST(target.last_activity, source.last_activity),
    activity_count = target.activity_count + source.activity_count
WHEN NOT MATCHED THEN
  INSERT (user_id, last_activity, activity_count)
  VALUES (source.user_id, source.last_activity, source.activity_count)
```

## Error Handling and Troubleshooting

### Common Issues and Solutions

```python
# Check table format
spark.sql("DESCRIBE DETAIL my_table").show()

# Enable merge schema evolution
spark.sql("SET spark.databricks.delta.schema.autoMerge.enabled=true")

# Handle schema conflicts
try:
    delta_table.merge(source_df, condition).execute()
except AnalysisException as e:
    print(f"Schema conflict: {e}")
    # Handle schema evolution or data type conflicts
```

### Validation Queries
```sql
-- Check merge results
SELECT 
  'target' as source, COUNT(*) as count 
FROM target_table
UNION ALL
SELECT 
  'source' as source, COUNT(*) as count 
FROM source_table;

-- Audit trail
SELECT 
  operation,
  COUNT(*) as record_count
FROM (
  SELECT 'updated' as operation FROM target_table WHERE last_updated = current_date()
  UNION ALL
  SELECT 'inserted' as operation FROM target_table WHERE created_at = current_date()
);
```

## Requirements and Limitations

### Requirements:
- Target table must be a Delta table
- Spark 3.0+ with Delta Lake support
- Proper permissions on target table

### Limitations:
- Cannot merge into a view
- Source can be any table/view/subquery
- MERGE operations are not atomic across multiple tables
- Complex nested conditions may impact performance

## Quick Reference Commands

```sql
-- Basic syntax template
MERGE INTO target USING source ON condition
WHEN MATCHED THEN UPDATE SET col = val
WHEN NOT MATCHED THEN INSERT VALUES (val1, val2)

-- Check Delta table history
DESCRIBE HISTORY target_table

-- Optimize after large merges
OPTIMIZE target_table

-- Vacuum old files
VACUUM target_table RETAIN 168 HOURS
```
