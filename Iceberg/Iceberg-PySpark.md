# Iceberg PySpark
Iceberg is an open source engine agnostic table format, so PySpark has implemented support for the format. Here is how to work with Iceberg in PySpark as well as some additional features Iceberg brings to the table.

## **Advanced Features Summary:**

### **1. Stored Procedures** 
Iceberg provides powerful stored procedures for maintenance operations like rollback, snapshot management, and cherry-picking changes. These require the Iceberg SQL extensions to be enabled.

### **2. Branching & Tagging**
Advanced time travel with branches and tags, allowing you to create named references to specific snapshots for experimentation or stable releases.

### **3. Incremental Reads** 
Read only the changes between two snapshots or since a specific point in time, which is crucial for ETL pipelines and change data capture.

### **4. Write-Audit-Publish (WAP)**
A pattern that allows you to stage writes for review before committing them to the main table.

### **5. Advanced Metadata Tables**
Beyond basic snapshots and files, Iceberg exposes detailed metadata through tables like `position_deletes`, `equality_deletes`, `manifests`, `entries`, and `refs`.

### **6. Distribution Modes**
Control how data is distributed across Spark tasks during writes - hash, range, or none modes for optimization.

### **7. Transform Functions**
Hidden partitioning with transform functions like years(), months(), days(), hours(), bucket(), and truncate() that automatically handle partitioning without exposing partition columns.

### **8. Copy-on-Write vs Merge-on-Read**
Different strategies for handling updates and deletes, trading off write performance vs read performance.

### **9. Migration Tools**
Procedures to migrate existing Hive/Spark tables to Iceberg format, create lightweight snapshots for testing, and add existing files.

### **10. Advanced Schema Evolution**
Beyond basic ADD/DROP columns, you can change column positions, add default values, modify nullability, and add comments.

These advanced features make Iceberg particularly powerful for:
- **Data Engineering**: Incremental processing, change tracking, and pipeline reliability
- **Data Science**: Reproducible experiments with branching and time travel
- **Data Governance**: Audit trails, rollback capabilities, and schema evolution
- **Performance Optimization**: File compaction, metadata optimization, and query planning

The syntax is consistent between PySpark and Glue - the main difference is that Glue 4.0+ has better built-in support for these features, while standalone PySpark requires explicit Iceberg extensions configuration.

---
# Apache Iceberg with PySpark & AWS Glue Cheatsheet

## Setup and Configuration

### PySpark (Local/EMR)
```python
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("IcebergApp") \
    .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.iceberg.spark.SparkSessionCatalog") \
    .config("spark.sql.catalog.spark_catalog.type", "hive") \
    .config("spark.sql.catalog.glue_catalog", "org.apache.iceberg.spark.SparkCatalog") \
    .config("spark.sql.catalog.glue_catalog.catalog-impl", "org.apache.iceberg.aws.glue.GlueCatalog") \
    .config("spark.sql.catalog.glue_catalog.warehouse", "s3://your-bucket/warehouse/") \
    .getOrCreate()
```

### AWS Glue (Job Script)
```python
import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job

args = getResolvedOptions(sys.argv, ['JOB_NAME'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session

# Iceberg configuration for Glue
spark.conf.set("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions")
spark.conf.set("spark.sql.catalog.glue_catalog", "org.apache.iceberg.spark.SparkCatalog")
spark.conf.set("spark.sql.catalog.glue_catalog.catalog-impl", "org.apache.iceberg.aws.glue.GlueCatalog")
spark.conf.set("spark.sql.catalog.glue_catalog.warehouse", "s3://your-bucket/warehouse/")

job = Job(glueContext)
job.init(args['JOB_NAME'], args)
```

## Creating Tables

### Creating via SQL (Same for both)
```sql
-- Create database
CREATE DATABASE IF NOT EXISTS glue_catalog.my_database;

-- Create table
CREATE TABLE glue_catalog.my_database.sales (
    id BIGINT,
    customer_id STRING,
    product_id STRING,
    amount DECIMAL(10,2),
    transaction_date DATE,
    created_at TIMESTAMP
) USING ICEBERG
PARTITIONED BY (days(transaction_date))
LOCATION 's3://your-bucket/warehouse/sales/'
TBLPROPERTIES (
    'write.target-file-size-bytes'='536870912',
    'write.parquet.compression-codec'='snappy'
);
```

### Creating via DataFrame API (Same for both)
```python
# Create DataFrame
df = spark.createDataFrame([
    (1, "cust1", "prod1", 100.0, "2024-01-01", "2024-01-01 10:00:00"),
    (2, "cust2", "prod2", 200.0, "2024-01-02", "2024-01-02 11:00:00")
], ["id", "customer_id", "product_id", "amount", "transaction_date", "created_at"])

# Write as Iceberg table
df.writeTo("glue_catalog.my_database.sales") \
  .using("iceberg") \
  .partitionedBy("transaction_date") \
  .createOrReplace()
```

## Reading Data

### Basic Read (Same for both)
```python
# Read entire table
df = spark.read.table("glue_catalog.my_database.sales")
df.show()

# Alternative syntax
df = spark.table("glue_catalog.my_database.sales")
```

### Time Travel Queries (Same for both)
```python
# Read specific snapshot
df = spark.read \
    .option("snapshot-id", "1234567890") \
    .table("glue_catalog.my_database.sales")

# Read as of timestamp
df = spark.read \
    .option("as-of-timestamp", "2024-01-01 00:00:00") \
    .table("glue_catalog.my_database.sales")

# SQL syntax
spark.sql("SELECT * FROM glue_catalog.my_database.sales TIMESTAMP AS OF '2024-01-01 00:00:00'")
```

## Writing Data

### Append Data (Same for both)
```python
new_data = spark.createDataFrame([
    (3, "cust3", "prod3", 300.0, "2024-01-03", "2024-01-03 12:00:00")
], ["id", "customer_id", "product_id", "amount", "transaction_date", "created_at"])

# Append mode
new_data.writeTo("glue_catalog.my_database.sales").append()

# Alternative
new_data.write.mode("append").saveAsTable("glue_catalog.my_database.sales")
```

### Overwrite Data (Same for both)
```python
# Overwrite entire table
df.writeTo("glue_catalog.my_database.sales").overwrite()

# Dynamic overwrite (only affected partitions)
df.write \
  .mode("overwrite") \
  .option("overwrite-mode", "dynamic") \
  .saveAsTable("glue_catalog.my_database.sales")
```

### Upsert/Merge Operations (Same for both)
```python
# SQL MERGE
spark.sql("""
MERGE INTO glue_catalog.my_database.sales AS target
USING (
    SELECT 1 as id, 'cust1' as customer_id, 'prod1' as product_id, 
           150.0 as amount, DATE('2024-01-01') as transaction_date,
           TIMESTAMP('2024-01-01 10:30:00') as created_at
) AS source
ON target.id = source.id
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *
""")
```

## Schema Evolution (Same for both)

```python
# Add column
spark.sql("ALTER TABLE glue_catalog.my_database.sales ADD COLUMN discount DECIMAL(5,2)")

# Drop column
spark.sql("ALTER TABLE glue_catalog.my_database.sales DROP COLUMN discount")

# Rename column
spark.sql("ALTER TABLE glue_catalog.my_database.sales RENAME COLUMN amount TO sale_amount")

# Change column type (compatible types only)
spark.sql("ALTER TABLE glue_catalog.my_database.sales ALTER COLUMN sale_amount TYPE DECIMAL(12,2)")
```

## Maintenance Operations

### Expire Snapshots (Same for both)
```python
# SQL
spark.sql("CALL glue_catalog.system.expire_snapshots('my_database.sales', TIMESTAMP '2024-01-01 00:00:00')")

# Keep last 10 snapshots
spark.sql("CALL glue_catalog.system.expire_snapshots(table => 'my_database.sales', retain_last => 10)")
```

### Remove Orphan Files (Same for both)
```python
spark.sql("CALL glue_catalog.system.remove_orphan_files('my_database.sales')")
```

### Rewrite Data Files (Same for both)
```python
# Compact small files
spark.sql("CALL glue_catalog.system.rewrite_data_files('my_database.sales')")

# With options
spark.sql("""
CALL glue_catalog.system.rewrite_data_files(
    table => 'my_database.sales',
    strategy => 'binpack',
    options => map('target-file-size-bytes', '536870912')
)
""")
```

## Metadata Queries (Same for both)

```python
# Show snapshots
spark.sql("SELECT * FROM glue_catalog.my_database.sales.snapshots").show()

# Show files
spark.sql("SELECT * FROM glue_catalog.my_database.sales.files").show()

# Show history
spark.sql("SELECT * FROM glue_catalog.my_database.sales.history").show()

# Show partitions
spark.sql("SELECT * FROM glue_catalog.my_database.sales.partitions").show()
```

## Key Differences Between PySpark and AWS Glue

### 1. Job Configuration

**PySpark:**
- Manual Spark session creation with Iceberg extensions
- Direct dependency management
- Flexible runtime configuration

**AWS Glue:**
- Use Glue job parameters: `--enable-glue-datacatalog`
- Managed Iceberg support in Glue 4.0+
- Built-in AWS service integrations

### 2. Catalog Configuration

**PySpark:**
```python
# More explicit catalog setup required
.config("spark.sql.catalog.glue_catalog.catalog-impl", "org.apache.iceberg.aws.glue.GlueCatalog")
```

**AWS Glue:**
```python
# Simplified with managed service
# Often works with default Glue catalog settings
```

### 3. Dependencies

**PySpark:**
```bash
# Manual JAR management
--packages org.apache.iceberg:iceberg-spark-runtime-3.4_2.12:1.4.2,org.apache.iceberg:iceberg-aws-bundle:1.4.2
```

**AWS Glue:**
- Built-in Iceberg support (Glue 4.0+)
- Managed dependencies
- Use job parameter: `--datalake-formats iceberg`

### 4. AWS Integration

**PySpark:**
- Manual AWS credentials configuration
- Explicit S3 and IAM setup

**AWS Glue:**
- Automatic AWS service integration
- Built-in IAM role support
- Native S3 optimization

## Best Practices

### Performance Optimization (Same for both)
```python
# Set appropriate file sizes
spark.conf.set("spark.sql.adaptive.enabled", "true")
spark.conf.set("spark.sql.adaptive.coalescePartitions.enabled", "true")

# Iceberg-specific optimizations
spark.sql("""
ALTER TABLE glue_catalog.my_database.sales 
SET TBLPROPERTIES (
    'write.target-file-size-bytes'='536870912',
    'write.delete.mode'='merge-on-read',
    'write.update.mode'='merge-on-read',
    'write.merge.mode'='merge-on-read'
)
""")
```

### Partitioning Strategy (Same for both)
```python
# Time-based partitioning
CREATE TABLE sales_partitioned (
    ...
) USING ICEBERG
PARTITIONED BY (years(transaction_date), months(transaction_date))

# Transform functions available:
# years(ts), months(ts), days(ts), hours(ts)
# bucket(N, col), truncate(L, col)
```

### Error Handling
```python
try:
    df.writeTo("glue_catalog.my_database.sales").append()
except Exception as e:
    print(f"Write failed: {e}")
    # Handle specific Iceberg exceptions
```

## Common Gotchas

1. **Catalog Names**: Always use the full catalog.database.table format
2. **Permissions**: Ensure S3 and Glue permissions are correctly configured
3. **Version Compatibility**: Match Iceberg version with Spark version
4. **File Formats**: Iceberg uses Parquet by default, but supports other formats
5. **Time Zones**: Be explicit about timestamp time zones in queries

## Advanced Iceberg Features & Procedures

### Stored Procedures (Requires Iceberg SQL Extensions)
```python
# Configure Spark with Iceberg extensions (required for procedures)
spark.conf.set("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions")

# Roll back to specific snapshot
spark.sql("CALL glue_catalog.system.rollback_to_snapshot('my_database.sales', 1234567890)")

# Roll back to specific timestamp
spark.sql("CALL glue_catalog.system.rollback_to_timestamp('my_database.sales', TIMESTAMP '2024-01-01 00:00:00')")

# Set current snapshot (doesn't need to be ancestor)
spark.sql("CALL glue_catalog.system.set_current_snapshot('my_database.sales', 9876543210)")

# Cherry-pick changes from another snapshot
spark.sql("CALL glue_catalog.system.cherry_pick_snapshot('my_database.sales', 1111111111)")

# Publish staged Write-Audit-Publish changes
spark.sql("CALL glue_catalog.system.publish_changes('my_database.sales', 'wap-id-12345')")
```

### Migration & Snapshot Procedures
```python
# Create snapshot table for testing (lightweight copy)
spark.sql("CALL glue_catalog.system.snapshot('source_catalog.db.table', 'glue_catalog.my_database.test_table')")

# Migrate existing Hive/Spark table to Iceberg
spark.sql("CALL glue_catalog.system.migrate('spark_catalog.db.old_table')")

# Add existing files to Iceberg table (use cautiously)
spark.sql("""
CALL glue_catalog.system.add_files(
    table => 'my_database.sales',
    source_table => '`parquet`.`s3://bucket/path/to/files/`'
)
""")
```

### Branching and Tagging (Advanced Time Travel)
```python
# Create branch from current snapshot
spark.sql("ALTER TABLE glue_catalog.my_database.sales CREATE BRANCH experiment_branch")

# Create branch from specific snapshot
spark.sql("ALTER TABLE glue_catalog.my_database.sales CREATE BRANCH fix_branch AS OF VERSION 1234567890")

# Create tag at current snapshot
spark.sql("ALTER TABLE glue_catalog.my_database.sales CREATE TAG stable_v1")

# Read from specific branch
df = spark.read.option("branch", "experiment_branch").table("glue_catalog.my_database.sales")

# Read from specific tag
df = spark.read.option("tag", "stable_v1").table("glue_catalog.my_database.sales")

# SQL syntax for branches and tags
spark.sql("SELECT * FROM glue_catalog.my_database.sales FOR SYSTEM_VERSION AS OF 'experiment_branch'")
spark.sql("SELECT * FROM glue_catalog.my_database.sales.`branch_experiment_branch`")
spark.sql("SELECT * FROM glue_catalog.my_database.sales.`tag_stable_v1`")

# Drop branch or tag
spark.sql("ALTER TABLE glue_catalog.my_database.sales DROP BRANCH experiment_branch")
spark.sql("ALTER TABLE glue_catalog.my_database.sales DROP TAG stable_v1")
```

### Incremental Reads
```python
# Read changes between two snapshots
df = spark.read \
    .format("iceberg") \
    .option("start-snapshot-id", "1234567890") \
    .option("end-snapshot-id", "9876543210") \
    .table("glue_catalog.my_database.sales")

# Read changes since specific timestamp
df = spark.read \
    .format("iceberg") \
    .option("start-snapshot-id", "1234567890") \
    .table("glue_catalog.my_database.sales")

# Incremental read with streaming (Structured Streaming)
df = spark.readStream \
    .format("iceberg") \
    .option("stream-from-timestamp", "2024-01-01 00:00:00") \
    .table("glue_catalog.my_database.sales")
```

### Write-Audit-Publish (WAP) Pattern
```python
# Enable WAP mode
spark.conf.set("spark.wap.enabled", "true")
spark.conf.set("spark.wap.id", "audit-2024-01-01")

# Write data in WAP mode (creates staged snapshot)
df.writeTo("glue_catalog.my_database.sales").append()

# Review staged changes
spark.sql("SELECT * FROM glue_catalog.my_database.sales FOR SYSTEM_VERSION AS OF 'audit-2024-01-01'")

# Publish staged changes
spark.sql("CALL glue_catalog.system.publish_changes('my_database.sales', 'audit-2024-01-01')")
```

### Advanced Maintenance Operations
```python
# Rewrite manifests (optimize metadata performance)
spark.sql("CALL glue_catalog.system.rewrite_manifests('my_database.sales')")

# Rewrite position deletes (optimize delete performance)
spark.sql("CALL glue_catalog.system.rewrite_position_deletes('my_database.sales')")

# Compact data files with specific strategy
spark.sql("""
CALL glue_catalog.system.rewrite_data_files(
    table => 'my_database.sales',
    strategy => 'sort',
    sort_order => 'transaction_date,customer_id'
)
""")

# Advanced expire snapshots with multiple options
spark.sql("""
CALL glue_catalog.system.expire_snapshots(
    table => 'my_database.sales',
    older_than => TIMESTAMP '2024-01-01',
    retain_last => 100,
    max_concurrent_deletes => 10,
    stream_results => false
)
""")
```

### Row-Level Operations with Copy-on-Write vs Merge-on-Read
```python
# Configure delete mode (copy-on-write is default)
spark.sql("ALTER TABLE glue_catalog.my_database.sales SET TBLPROPERTIES ('write.delete.mode'='copy-on-write')")

# Configure for merge-on-read (faster deletes, slower reads)
spark.sql("ALTER TABLE glue_catalog.my_database.sales SET TBLPROPERTIES ('write.delete.mode'='merge-on-read')")

# Configure update mode
spark.sql("ALTER TABLE glue_catalog.my_database.sales SET TBLPROPERTIES ('write.update.mode'='merge-on-read')")

# Configure merge mode
spark.sql("ALTER TABLE glue_catalog.my_database.sales SET TBLPROPERTIES ('write.merge.mode'='merge-on-read')")
```

### Distribution Modes for Writing
```python
# Hash distribution (default for partitioned tables in 1.5+)
spark.conf.set("spark.sql.sources.write.distribution-mode", "hash")

# Range distribution (good for sorted data)
spark.conf.set("spark.sql.sources.write.distribution-mode", "range")

# No distribution (manual control)
spark.conf.set("spark.sql.sources.write.distribution-mode", "none")

# Fan-out writing (keep all file handles open)
df.write \
  .option("fanout-enabled", "true") \
  .mode("append") \
  .saveAsTable("glue_catalog.my_database.sales")
```

### Advanced Metadata Queries
```python
# Show table metadata
spark.sql("DESCRIBE EXTENDED glue_catalog.my_database.sales").show(truncate=False)

# Show all snapshots
spark.sql("SELECT * FROM glue_catalog.my_database.sales.snapshots ORDER BY committed_at DESC").show()

# Show data files with metrics
spark.sql("SELECT * FROM glue_catalog.my_database.sales.data_files LIMIT 10").show()

# Show position delete files
spark.sql("SELECT * FROM glue_catalog.my_database.sales.position_deletes").show()

# Show equality delete files
spark.sql("SELECT * FROM glue_catalog.my_database.sales.equality_deletes").show()

# Show all files (data + delete files)
spark.sql("SELECT * FROM glue_catalog.my_database.sales.all_files").show()

# Show table entries (low-level metadata)
spark.sql("SELECT * FROM glue_catalog.my_database.sales.entries").show()

# Show manifests
spark.sql("SELECT * FROM glue_catalog.my_database.sales.manifests").show()

# Show partition information
spark.sql("SELECT * FROM glue_catalog.my_database.sales.partitions").show()

# Show refs (branches and tags)
spark.sql("SELECT * FROM glue_catalog.my_database.sales.refs").show()
```

### Advanced Schema Evolution
```python
# Add column with default value
spark.sql("ALTER TABLE glue_catalog.my_database.sales ADD COLUMN region STRING DEFAULT 'US'")

# Add column after specific column
spark.sql("ALTER TABLE glue_catalog.my_database.sales ADD COLUMN tax_rate DECIMAL(5,4) AFTER amount")

# Change column position
spark.sql("ALTER TABLE glue_catalog.my_database.sales ALTER COLUMN region FIRST")
spark.sql("ALTER TABLE glue_catalog.my_database.sales ALTER COLUMN region AFTER customer_id")

# Set column comment
spark.sql("ALTER TABLE glue_catalog.my_database.sales ALTER COLUMN amount COMMENT 'Sale amount in USD'")

# Change column nullability (widening only)
spark.sql("ALTER TABLE glue_catalog.my_database.sales ALTER COLUMN customer_id DROP NOT NULL")
```

### Transform Functions and Hidden Partitioning
```python
# Create table with transform functions
spark.sql("""
CREATE TABLE glue_catalog.my_database.events (
    event_id BIGINT,
    user_id STRING,
    event_time TIMESTAMP,
    event_data STRING
) USING ICEBERG
PARTITIONED BY (
    years(event_time),
    months(event_time),
    days(event_time),
    hours(event_time),
    bucket(16, user_id)
)
""")

# Available transform functions:
# - years(timestamp_col)
# - months(timestamp_col) 
# - days(timestamp_col)
# - hours(timestamp_col)
# - bucket(N, col) - hash bucket
# - truncate(L, string_col) - truncate strings to L characters
# - identity(col) - no transform
```

### Monitoring and Troubleshooting

```python
# Check table properties
spark.sql("DESCRIBE EXTENDED glue_catalog.my_database.sales").show(truncate=False)

# View execution plans
df = spark.table("glue_catalog.my_database.sales")
df.explain(True)

# Check Iceberg metadata
spark.sql("SELECT * FROM glue_catalog.my_database.sales.snapshots ORDER BY committed_at DESC LIMIT 5").show()

# Monitor file counts and sizes
spark.sql("""
SELECT 
    partition,
    COUNT(*) as file_count,
    SUM(file_size_in_bytes) / 1024 / 1024 / 1024 as total_gb
FROM glue_catalog.my_database.sales.data_files 
GROUP BY partition
ORDER BY total_gb DESC
""").show()

# Check snapshot lineage
spark.sql("""
SELECT 
    snapshot_id,
    parent_id,
    operation,
    summary
FROM glue_catalog.my_database.sales.snapshots 
ORDER BY committed_at DESC
""").show()
```
