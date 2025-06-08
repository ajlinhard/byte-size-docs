# Spark Write Data Overview
This page is a comprehensive PySpark data writing cheat sheet for you, covering tables, Parquet, CSV, and JSON formats with various options and configurations.I've created a comprehensive PySpark data writing cheat sheet that covers all the major output formats you requested. The cheat sheet includes:

**Key sections:**
- **Tables (Hive/Catalog)**: Writing to managed and external tables, partitioned tables, and advanced options
- **Parquet**: Basic and advanced Parquet writing with compression and partitioning
- **CSV**: CSV output with headers, custom delimiters, and various formatting options
- **JSON**: JSON writing with formatting and compression options

**Additional features:**
- Write modes explanation (overwrite, append, ignore, error)
- Performance optimization techniques
- Error handling patterns
- Best practices for data validation
- Common patterns like Delta Lake and multi-format output
- Dynamic partitioning examples

The cheat sheet provides practical examples for each format with commonly used options and configurations. It's designed to be a quick reference for the most frequent PySpark data writing scenarios you'll encounter in practice.

---
# PySpark Data Writing Cheat Sheet

## Basic Setup

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lit
from pyspark.sql.types import *

# Create SparkSession
spark = SparkSession.builder \
    .appName("Data Writing Example") \
    .enableHiveSupport() \
    .getOrCreate()

# Sample DataFrame for examples
df = spark.createDataFrame([
    (1, "Alice", 25.5, "2023-01-01"),
    (2, "Bob", 30.0, "2023-01-02"),
    (3, "Charlie", 35.2, "2023-01-03")
], ["id", "name", "value", "date"])
```

## Writing to Tables (Hive/Catalog)

### Basic Table Writing
```python
# Write to Hive table (create if not exists)
df.write \
  .mode("overwrite") \
  .saveAsTable("my_database.my_table")

# Write with specific mode
df.write \
  .mode("append") \
  .saveAsTable("my_table")

# Available modes: overwrite, append, ignore, error (default)
```

### Partitioned Table Writing
```python
# Write partitioned table
df.write \
  .mode("overwrite") \
  .partitionBy("date") \
  .saveAsTable("partitioned_table")

# Multiple partition columns
df.write \
  .mode("overwrite") \
  .partitionBy("date", "name") \
  .saveAsTable("multi_partitioned_table")
```

### Advanced Table Options
```python
# Write with specific format and options
df.write \
  .mode("overwrite") \
  .format("parquet") \
  .option("compression", "snappy") \
  .partitionBy("date") \
  .saveAsTable("optimized_table")

# Write with table properties
df.write \
  .mode("overwrite") \
  .option("path", "/custom/path/to/table") \
  .saveAsTable("external_table")
```

### Insert Into Existing Table
```python
# Insert into existing table
df.write \
  .mode("append") \
  .insertInto("existing_table")

# Insert into specific partitions
df.write \
  .mode("overwrite") \
  .insertInto("partitioned_table", overwrite=True)
```

## Writing to Parquet

### Basic Parquet Writing
```python
# Simple parquet write
df.write \
  .mode("overwrite") \
  .parquet("/path/to/output.parquet")

# With compression
df.write \
  .mode("overwrite") \
  .option("compression", "snappy") \
  .parquet("/path/to/compressed.parquet")

# Available compressions: none, snappy, gzip, lzo, brotli, lz4, zstd
```

### Partitioned Parquet
```python
# Partitioned parquet files
df.write \
  .mode("overwrite") \
  .partitionBy("date") \
  .parquet("/path/to/partitioned_parquet/")

# Multiple partitions
df.write \
  .mode("overwrite") \
  .partitionBy("date", "name") \
  .parquet("/path/to/multi_partitioned/")
```

### Advanced Parquet Options
```python
# Custom parquet options
df.write \
  .mode("overwrite") \
  .option("compression", "snappy") \
  .option("maxRecordsPerFile", 10000) \
  .option("maxPartitionBytes", 134217728) \
  .parquet("/path/to/optimized.parquet")

# Control file size
df.coalesce(1).write \
  .mode("overwrite") \
  .parquet("/path/to/single_file.parquet")
```

## Writing to CSV

### Basic CSV Writing
```python
# Simple CSV write
df.write \
  .mode("overwrite") \
  .csv("/path/to/output.csv")

# CSV with headers
df.write \
  .mode("overwrite") \
  .option("header", "true") \
  .csv("/path/to/output_with_headers.csv")
```

### CSV with Custom Options
```python
# Custom delimiter and options
df.write \
  .mode("overwrite") \
  .option("header", "true") \
  .option("sep", "|") \
  .option("quote", '"') \
  .option("escape", "\\") \
  .option("nullValue", "NULL") \
  .option("dateFormat", "yyyy-MM-dd") \
  .option("timestampFormat", "yyyy-MM-dd HH:mm:ss") \
  .csv("/path/to/custom.csv")

# Single CSV file
df.coalesce(1).write \
  .mode("overwrite") \
  .option("header", "true") \
  .csv("/path/to/single.csv")
```

### CSV Partitioned
```python
# Partitioned CSV files
df.write \
  .mode("overwrite") \
  .option("header", "true") \
  .partitionBy("date") \
  .csv("/path/to/partitioned_csv/")
```

### Common CSV Options
```python
# Comprehensive CSV options
df.write \
  .mode("overwrite") \
  .option("header", "true") \
  .option("sep", ",") \
  .option("quote", '"') \
  .option("escape", '"') \
  .option("quoteAll", "false") \
  .option("nullValue", "") \
  .option("emptyValue", "") \
  .option("dateFormat", "yyyy-MM-dd") \
  .option("timestampFormat", "yyyy-MM-dd'T'HH:mm:ss.SSSXXX") \
  .option("ignoreLeadingWhiteSpace", "true") \
  .option("ignoreTrailingWhiteSpace", "true") \
  .csv("/path/to/comprehensive.csv")
```

## Writing to JSON

### Basic JSON Writing
```python
# Simple JSON write
df.write \
  .mode("overwrite") \
  .json("/path/to/output.json")

# Single JSON file
df.coalesce(1).write \
  .mode("overwrite") \
  .json("/path/to/single.json")
```

### JSON with Options
```python
# JSON with custom options
df.write \
  .mode("overwrite") \
  .option("dateFormat", "yyyy-MM-dd") \
  .option("timestampFormat", "yyyy-MM-dd'T'HH:mm:ss.SSSXXX") \
  .option("compression", "gzip") \
  .json("/path/to/custom.json")

# Pretty printed JSON (not recommended for large files)
df.write \
  .mode("overwrite") \
  .option("pretty", "true") \
  .json("/path/to/pretty.json")
```

### Partitioned JSON
```python
# Partitioned JSON files
df.write \
  .mode("overwrite") \
  .partitionBy("date") \
  .json("/path/to/partitioned_json/")
```

## Write Modes Explained

```python
# Available write modes:
modes = {
    "overwrite": "Replace existing data completely",
    "append": "Add new data to existing data",
    "ignore": "Skip write if data already exists",
    "error": "Throw error if data already exists (default)"
}

# Examples
df.write.mode("overwrite").parquet("/path")    # Replace all
df.write.mode("append").parquet("/path")       # Add to existing
df.write.mode("ignore").parquet("/path")       # Skip if exists
df.write.mode("error").parquet("/path")        # Fail if exists
```

## Performance Optimization

### Controlling File Size and Partitions
```python
# Control number of output files
df.coalesce(1).write.parquet("/path")          # Single file
df.repartition(10).write.parquet("/path")      # 10 files

# Optimize partition size
df.write \
  .option("maxRecordsPerFile", 50000) \
  .parquet("/path")

# Bucket table for better joins
df.write \
  .mode("overwrite") \
  .bucketBy(10, "id") \
  .sortBy("id") \
  .saveAsTable("bucketed_table")
```

### Compression Options
```python
# Different compression formats by file type
compressions = {
    "parquet": ["none", "snappy", "gzip", "lzo", "brotli", "lz4", "zstd"],
    "json": ["none", "bzip2", "gzip", "lz4", "snappy", "deflate"],
    "csv": ["none", "bzip2", "gzip", "lz4", "snappy", "deflate"]
}

# Example with best compression
df.write \
  .option("compression", "snappy") \
  .parquet("/path")
```

## Error Handling and Best Practices

### Safe Writing Pattern
```python
try:
    df.write \
      .mode("overwrite") \
      .option("compression", "snappy") \
      .parquet("/safe/path")
    print("Write successful")
except Exception as e:
    print(f"Write failed: {e}")
```

### Validate Before Writing
```python
# Check data before writing
print(f"Row count: {df.count()}")
print(f"Columns: {df.columns}")
df.printSchema()

# Check for nulls in critical columns
null_counts = df.select([
    col(c).isNull().cast("int").alias(c) 
    for c in df.columns
]).groupBy().sum().collect()[0].asDict()
print(f"Null counts: {null_counts}")
```

### Temporary Views for Complex Writes
```python
# Create temporary view for complex operations
df.createOrReplaceTempView("temp_table")

# Write with SQL transformations
spark.sql("""
    SELECT id, name, value, date,
           CASE WHEN value > 30 THEN 'high' ELSE 'low' END as category
    FROM temp_table
""").write \
  .mode("overwrite") \
  .partitionBy("category") \
  .parquet("/path/to/categorized")
```

## Common Patterns

### Delta Lake (if available)
```python
# Write to Delta table
df.write \
  .format("delta") \
  .mode("overwrite") \
  .saveAsTable("delta_table")

# Write with merge operation
from delta.tables import DeltaTable

deltaTable = DeltaTable.forPath(spark, "/path/to/delta")
deltaTable.alias("target").merge(
    df.alias("source"),
    "target.id = source.id"
).whenMatchedUpdateAll().whenNotMatchedInsertAll().execute()
```

### Multiple Format Output
```python
# Write same data to multiple formats
output_path = "/path/to/output"

# Parquet for analytics
df.write.mode("overwrite").parquet(f"{output_path}/parquet")

# CSV for exports
df.coalesce(1).write.mode("overwrite") \
  .option("header", "true") \
  .csv(f"{output_path}/csv")

# JSON for APIs
df.coalesce(1).write.mode("overwrite") \
  .json(f"{output_path}/json")
```

### Dynamic Partitioning
```python
# Dynamic partition writing based on data
partition_columns = ["year", "month"]

# Add partition columns
df_with_partitions = df.withColumn("year", col("date").substr(1, 4)) \
                      .withColumn("month", col("date").substr(6, 2))

df_with_partitions.write \
  .mode("overwrite") \
  .partitionBy(*partition_columns) \
  .parquet("/path/to/time_partitioned")
```
