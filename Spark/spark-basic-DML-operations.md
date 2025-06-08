# Spark DML Operations
I'll show you how to perform SELECT INTO, INSERT INTO, UPDATE, and DELETE operations in Spark using both PySpark DataFrame API and Spark SQL.Here's a comprehensive guide to performing DML operations in Spark. Key points to remember:

**SELECT INTO**: Use `CREATE TABLE AS SELECT` (CTAS) in SQL or `DataFrame.write.saveAsTable()` in PySpark to create new tables from query results.

**INSERT INTO**: Use `INSERT INTO` statements in SQL or `DataFrame.write.insertInto()` in PySpark. Spark supports both append and overwrite modes.

**UPDATE/DELETE**: These operations work differently depending on your table format:
- **Delta Lake tables**: Support native UPDATE/DELETE operations with ACID guarantees
- **Standard Hive tables**: Require the INSERT OVERWRITE pattern to simulate updates and deletes

**Important considerations**:
1. **Delta Lake** is recommended for true ACID transactions and native UPDATE/DELETE support
2. For standard Hive tables, use **INSERT OVERWRITE** with filtered/transformed data
3. **Partitioned tables** can be more efficient for large-scale operations
4. Always consider performance implications and use appropriate file formats (Parquet, Delta)

The examples show both PySpark DataFrame API and Spark SQL approaches, so you can use whichever fits better with your existing codebase and preferences.
---
# Spark DML Operations: SELECT INTO, INSERT, UPDATE, DELETE

## Setup

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import *

spark = SparkSession.builder \
    .appName("DML Operations") \
    .enableHiveSupport() \
    .getOrCreate()
```

## 1. SELECT INTO Operations

### PySpark DataFrame API

```python
# Read source data
source_df = spark.table("source_table")

# Method 1: Create new table from DataFrame
source_df.write \
    .mode("overwrite") \
    .saveAsTable("new_table")

# Method 2: Create table with specific format
source_df.select("id", "name", "value") \
    .where(col("value") > 100) \
    .write \
    .mode("overwrite") \
    .format("parquet") \
    .option("path", "/path/to/table") \
    .saveAsTable("filtered_table")

# Method 3: Create temporary view and save
source_df.createOrReplaceTempView("temp_view")
result_df = spark.sql("SELECT * FROM temp_view WHERE status = 'active'")
result_df.write.mode("overwrite").saveAsTable("active_records")
```

### Spark SQL

```sql
-- Create table as select (CTAS)
CREATE TABLE new_table
USING PARQUET
LOCATION '/path/to/new_table'
AS SELECT id, name, value 
FROM source_table 
WHERE value > 100;

-- Create table with specific schema
CREATE TABLE employees_backup (
    emp_id INT,
    name STRING,
    department STRING,
    salary DOUBLE
) USING DELTA
LOCATION '/path/to/backup';

INSERT INTO employees_backup
SELECT emp_id, name, department, salary 
FROM employees 
WHERE hire_date >= '2023-01-01';
```

## 2. INSERT INTO Operations

### PySpark DataFrame API

```python
# Method 1: Insert from DataFrame
new_data = spark.createDataFrame([
    (1, "John", "Engineering", 75000),
    (2, "Jane", "Marketing", 65000)
], ["emp_id", "name", "department", "salary"])

new_data.write \
    .mode("append") \
    .insertInto("employees")

# Method 2: Insert with transformation
source_df.select(
    col("id").alias("emp_id"),
    col("full_name").alias("name"),
    col("dept").alias("department"),
    col("pay").alias("salary")
).write \
.mode("append") \
.insertInto("employees")

# Method 3: Insert into partitioned table
new_data.write \
    .mode("append") \
    .partitionBy("department") \
    .insertInto("employees_partitioned")
```

### Spark SQL

```sql
-- Basic insert
INSERT INTO employees 
VALUES 
    (1, 'John Doe', 'Engineering', 75000),
    (2, 'Jane Smith', 'Marketing', 65000);

-- Insert from select
INSERT INTO employees (emp_id, name, department, salary)
SELECT id, full_name, dept, pay 
FROM temp_employees 
WHERE status = 'approved';

-- Insert overwrite
INSERT OVERWRITE employees
SELECT * FROM employees_staging;

-- Insert into partitioned table
INSERT INTO employees_partitioned PARTITION(department='Engineering')
SELECT emp_id, name, salary 
FROM new_hires 
WHERE dept = 'Engineering';

-- Dynamic partition insert
INSERT INTO employees_partitioned PARTITION(department)
SELECT emp_id, name, salary, department
FROM new_hires;
```

## 3. UPDATE Operations

**Note: Traditional UPDATE is only supported in Delta Lake tables. For standard Hive tables, you need to use INSERT OVERWRITE pattern.**

### Delta Lake Updates

```python
# PySpark with Delta Lake
from delta.tables import DeltaTable

# Load Delta table
delta_table = DeltaTable.forName(spark, "employees_delta")

# Update operation
delta_table.update(
    condition = col("department") == "Engineering",
    set = {"salary": col("salary") * 1.1}
)

# Conditional update
delta_table.update(
    condition = (col("hire_date") < "2020-01-01") & (col("performance") == "excellent"),
    set = {
        "salary": col("salary") * 1.15,
        "bonus": lit(5000)
    }
)
```

```sql
-- Spark SQL with Delta Lake
UPDATE employees_delta 
SET salary = salary * 1.1 
WHERE department = 'Engineering';

UPDATE employees_delta 
SET salary = salary * 1.15, bonus = 5000
WHERE hire_date < '2020-01-01' AND performance = 'excellent';
```

### Standard Hive Tables (INSERT OVERWRITE Pattern)

```python
# PySpark: Simulate UPDATE with INSERT OVERWRITE
employees_df = spark.table("employees")

# Update records
updated_df = employees_df.withColumn(
    "salary",
    when(col("department") == "Engineering", col("salary") * 1.1)
    .otherwise(col("salary"))
)

# Overwrite the table
updated_df.write \
    .mode("overwrite") \
    .saveAsTable("employees")
```

```sql
-- Spark SQL: Simulate UPDATE with INSERT OVERWRITE
INSERT OVERWRITE employees
SELECT 
    emp_id,
    name,
    department,
    CASE 
        WHEN department = 'Engineering' THEN salary * 1.1
        ELSE salary
    END as salary
FROM employees;
```

## 4. DELETE Operations

### Delta Lake Deletes

```python
# PySpark with Delta Lake
delta_table = DeltaTable.forName(spark, "employees_delta")

# Delete operation
delta_table.delete(col("status") == "terminated")

# Conditional delete
delta_table.delete(
    (col("last_login") < "2022-01-01") & 
    (col("status") == "inactive")
)
```

```sql
-- Spark SQL with Delta Lake
DELETE FROM employees_delta 
WHERE status = 'terminated';

DELETE FROM employees_delta 
WHERE last_login < '2022-01-01' AND status = 'inactive';
```

### Standard Hive Tables (INSERT OVERWRITE Pattern)

```python
# PySpark: Simulate DELETE with INSERT OVERWRITE
employees_df = spark.table("employees")

# Filter out records to "delete"
filtered_df = employees_df.filter(col("status") != "terminated")

# Overwrite the table
filtered_df.write \
    .mode("overwrite") \
    .saveAsTable("employees")
```

```sql
-- Spark SQL: Simulate DELETE with INSERT OVERWRITE
INSERT OVERWRITE employees
SELECT * FROM employees 
WHERE status != 'terminated';
```

## 5. Advanced Patterns

### Upsert (Merge) Operations

```python
# Delta Lake MERGE operation
delta_table.alias("target").merge(
    source_df.alias("source"),
    "target.emp_id = source.emp_id"
).whenMatchedUpdate(set = {
    "name": "source.name",
    "salary": "source.salary"
}).whenNotMatchedInsert(values = {
    "emp_id": "source.emp_id",
    "name": "source.name",
    "department": "source.department",
    "salary": "source.salary"
}).execute()
```

```sql
-- Delta Lake MERGE in SQL
MERGE INTO employees_delta AS target
USING employee_updates AS source
ON target.emp_id = source.emp_id
WHEN MATCHED THEN
    UPDATE SET 
        name = source.name,
        salary = source.salary
WHEN NOT MATCHED THEN
    INSERT (emp_id, name, department, salary)
    VALUES (source.emp_id, source.name, source.department, source.salary);
```

### Bulk Operations with Partitions

```python
# Efficient partition-wise operations
# Insert into specific partition
new_data.write \
    .mode("overwrite") \
    .option("partitionOverwriteMode", "dynamic") \
    .insertInto("partitioned_table")

# Process each partition separately
partitions = spark.sql("SHOW PARTITIONS partitioned_table").collect()
for partition in partitions:
    partition_filter = partition['partition']
    # Process each partition
    spark.sql(f"""
        INSERT OVERWRITE partitioned_table PARTITION({partition_filter})
        SELECT * FROM staging_table 
        WHERE {partition_filter}
    """)
```

## 6. Best Practices

### Performance Optimization

```python
# Use appropriate file format
df.write \
    .mode("overwrite") \
    .format("delta")  # or "parquet" for better performance
    .option("overwriteSchema", "true") \
    .saveAsTable("optimized_table")

# Partition large tables appropriately
df.write \
    .mode("overwrite") \
    .partitionBy("year", "month") \
    .saveAsTable("time_partitioned_table")

# Use broadcast joins for small lookup tables
large_df.join(broadcast(small_df), "key").write.saveAsTable("joined_table")
```

### Error Handling

```python
try:
    # DML operation
    df.write.mode("append").saveAsTable("target_table")
    print("Insert successful")
except Exception as e:
    print(f"Insert failed: {str(e)}")
    # Rollback or error handling logic
```

### Transaction Management (Delta Lake)

```python
# Atomic operations with Delta Lake
with delta_table.createTransaction() as txn:
    # Multiple operations in single transaction
    txn.update(condition=..., set=...)
    txn.delete(condition=...)
    txn.commit()
```
