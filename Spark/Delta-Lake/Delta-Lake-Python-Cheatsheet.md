# Delta Lake Python Cheatsheet
This Delta Lake Python cheat sheet is covering PySpark session configuration, common functions, and practical examples.I've created a comprehensive Delta Lake Python cheat sheet that covers everything you need to work with Delta Lake data. The cheat sheet includes:

**Key Sections:**
1. **PySpark Session Configuration** - Two methods for setting up Spark with Delta Lake support
2. **Common Functions Table** - All essential Delta Lake functions with their purposes and parameters
3. **Practical Examples** - Detailed walkthroughs of each function category including:
   - Basic operations (creating, reading, writing)
   - Advanced operations (merge, update, delete)
   - Schema evolution and management
   - Time travel capabilities
   - Streaming integration
   - Table conversion and maintenance
   - Best practices and SQL operations

**Highlights:**
- **CRUD Operations**: Complete examples for Create, Read, Update, Delete operations
- **UPSERT Support**: Detailed merge operations for handling data updates
- **Time Travel**: Version-based and timestamp-based historical data access
- **Schema Evolution**: Handling schema changes safely
- **Streaming Integration**: Real-time data processing with Delta Lake
- **Optimization**: Vacuum, compaction, and Z-ordering for performance
- **Error Handling**: Common issues and debugging approaches

The cheat sheet is designed to be a practical reference that you can use for both learning Delta Lake concepts and as a quick reference during development. Each example includes working code that you can adapt to your specific use cases.

---
# Delta Lake Python Cheat Sheet

## PySpark Session Configuration for Delta Lake

```python
from pyspark.sql import SparkSession
from delta import configure_spark_with_delta_pip

# Method 1: Using delta configure_spark_with_delta_pip (Recommended)
builder = SparkSession.builder \
    .appName("Delta Lake Example") \
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
    .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer") \
    .config("spark.sql.adaptive.enabled", "true") \
    .config("spark.sql.adaptive.coalescePartitions.enabled", "true")

spark = configure_spark_with_delta_pip(builder).getOrCreate()

# Method 2: Manual configuration with Delta JAR
spark = SparkSession.builder \
    .appName("Delta Lake Example") \
    .config("spark.jars.packages", "io.delta:delta-core_2.12:2.4.0") \
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
    .getOrCreate()
```

## Common Delta Lake Functions

| Function Name | Purpose | Parameters |
|---------------|---------|------------|
| `DeltaTable.forPath()` | Load existing Delta table from path | `sparkSession, path` |
| `DeltaTable.forName()` | Load existing Delta table by name | `sparkSession, tableName` |
| `DeltaTable.create()` | Create new Delta table | `sparkSession` + builder methods |
| `DeltaTable.createIfNotExists()` | Create table if it doesn't exist | `sparkSession` + builder methods |
| `deltaTable.history()` | Get table history/audit log | `limit=None` |
| `deltaTable.detail()` | Get table details and metadata | None |
| `deltaTable.vacuum()` | Clean up old files | `retentionHours=None` |
| `deltaTable.optimize()` | Optimize table (compaction) | None |
| `deltaTable.merge()` | Merge data (UPSERT operation) | `source, condition` |
| `deltaTable.update()` | Update existing records | `condition, set` |
| `deltaTable.delete()` | Delete records | `condition` |
| `deltaTable.restoreToVersion()` | Time travel to specific version | `version` |
| `deltaTable.restoreToTimestamp()` | Time travel to timestamp | `timestamp` |
| `deltaTable.generate()` | Generate manifest files | `mode` |
| `deltaTable.convertToDelta()` | Convert Parquet to Delta | `sparkSession, identifier` |

## Basic Delta Lake Operations

### Creating and Writing Delta Tables

```python
from delta.tables import DeltaTable
from pyspark.sql.functions import *

# Create sample data
data = [(1, "Alice", 25, "2023-01-01"),
        (2, "Bob", 30, "2023-01-01"),
        (3, "Charlie", 35, "2023-01-01")]

df = spark.createDataFrame(data, ["id", "name", "age", "date"])

# Write as Delta table
df.write.format("delta").mode("overwrite").save("/path/to/delta-table")

# Write as managed table
df.write.format("delta").mode("overwrite").saveAsTable("my_delta_table")

# Write with partitioning
df.write.format("delta").mode("overwrite").partitionBy("date").save("/path/to/partitioned-table")
```

### Reading Delta Tables

```python
# Read Delta table by path
df = spark.read.format("delta").load("/path/to/delta-table")

# Read Delta table by name
df = spark.read.table("my_delta_table")

# Read with time travel (version)
df = spark.read.format("delta").option("versionAsOf", 1).load("/path/to/delta-table")

# Read with time travel (timestamp)
df = spark.read.format("delta").option("timestampAsOf", "2023-01-01").load("/path/to/delta-table")
```

### DeltaTable Operations

```python
# Load existing Delta table
deltaTable = DeltaTable.forPath(spark, "/path/to/delta-table")
# or
deltaTable = DeltaTable.forName(spark, "my_delta_table")

# Get table history
history = deltaTable.history().show()

# Get table details
details = deltaTable.detail().show()

# Vacuum old files (default 7 days retention)
deltaTable.vacuum()

# Vacuum with custom retention (use with caution)
deltaTable.vacuum(retentionHours=24)

# Optimize table (compaction)
deltaTable.optimize().executeCompaction()

# Optimize with Z-ordering
deltaTable.optimize().executeZOrderBy("id", "name")
```

## Advanced Delta Operations

### Merge (UPSERT) Operations

```python
# Prepare source data for merge
updates = [(1, "Alice Updated", 26, "2023-01-02"),
           (4, "David", 28, "2023-01-02")]

source_df = spark.createDataFrame(updates, ["id", "name", "age", "date"])

# Merge operation
deltaTable.alias("target").merge(
    source_df.alias("source"),
    "target.id = source.id"
).whenMatchedUpdate(set={
    "name": "source.name",
    "age": "source.age",
    "date": "source.date"
}).whenNotMatchedInsert(values={
    "id": "source.id",
    "name": "source.name",
    "age": "source.age",
    "date": "source.date"
}).execute()
```

### Update Operations

```python
# Update specific records
deltaTable.update(
    condition="age > 30",
    set={"age": expr("age + 1")}
)

# Update with multiple conditions
deltaTable.update(
    condition="name = 'Alice' AND age > 25",
    set={
        "age": expr("age + 5"),
        "name": lit("Alice Senior")
    }
)
```

### Delete Operations

```python
# Delete records with condition
deltaTable.delete("age < 25")

# Delete with complex condition
deltaTable.delete("name LIKE '%test%' OR age IS NULL")
```

## Schema Evolution and Management

```python
# Enable schema evolution
df.write.format("delta") \
    .mode("append") \
    .option("mergeSchema", "true") \
    .save("/path/to/delta-table")

# Add new columns explicitly
spark.sql("ALTER TABLE my_delta_table ADD COLUMN new_column STRING")

# Check current schema
deltaTable.detail().select("schema").show(truncate=False)

# Schema enforcement example
try:
    # This will fail if schema doesn't match
    incompatible_df.write.format("delta").mode("append").save("/path/to/delta-table")
except Exception as e:
    print(f"Schema enforcement error: {e}")
```

## Time Travel Examples

```python
# Read historical versions
v0 = spark.read.format("delta").option("versionAsOf", 0).load("/path/to/delta-table")
v1 = spark.read.format("delta").option("versionAsOf", 1).load("/path/to/delta-table")

# Read by timestamp
yesterday = spark.read.format("delta") \
    .option("timestampAsOf", "2023-01-01 00:00:00") \
    .load("/path/to/delta-table")

# Restore to previous version
deltaTable.restoreToVersion(1)

# Restore to timestamp
deltaTable.restoreToTimestamp("2023-01-01")
```

## Streaming with Delta Lake

```python
# Streaming write to Delta
streaming_df = spark.readStream.format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "my-topic") \
    .load()

query = streaming_df.writeStream \
    .format("delta") \
    .outputMode("append") \
    .option("checkpointLocation", "/path/to/checkpoint") \
    .start("/path/to/delta-table")

# Streaming read from Delta
stream = spark.readStream.format("delta").load("/path/to/delta-table")
```

## Converting Existing Tables to Delta

```python
# Convert Parquet table to Delta
DeltaTable.convertToDelta(spark, "parquet.`/path/to/parquet-table`")

# Convert partitioned Parquet table
DeltaTable.convertToDelta(
    spark, 
    "parquet.`/path/to/partitioned-table`",
    "date DATE"
)

# Convert Hive table to Delta
spark.sql("CONVERT TO DELTA my_hive_table")
```

## Monitoring and Maintenance

```python
# Check table statistics
spark.sql("DESCRIBE DETAIL my_delta_table").show()

# Generate manifest files for external tools
deltaTable.generate("symlink_format_manifest")

# Get file-level information
spark.sql("DESCRIBE HISTORY my_delta_table").show()

# Check table constraints
spark.sql("SHOW TBLPROPERTIES my_delta_table").show()
```

## Best Practices

```python
# 1. Use appropriate partition columns
df.write.format("delta").partitionBy("date", "region").save("/path/to/table")

# 2. Set table properties for optimization
spark.sql("""
    ALTER TABLE my_delta_table SET TBLPROPERTIES (
        'delta.autoOptimize.optimizeWrite' = 'true',
        'delta.autoOptimize.autoCompact' = 'true'
    )
""")

# 3. Use Z-ordering for better performance
deltaTable.optimize().executeZOrderBy("frequently_queried_column")

# 4. Monitor table size and vacuum regularly
deltaTable.vacuum(retentionHours=168)  # 7 days

# 5. Use structured streaming for real-time processing
streaming_query = df.writeStream \
    .format("delta") \
    .outputMode("append") \
    .trigger(processingTime="1 minute") \
    .start("/path/to/delta-table")
```

## Common SQL Operations

```python
# Create Delta table with SQL
spark.sql("""
    CREATE TABLE my_delta_table (
        id INT,
        name STRING,
        age INT,
        date DATE
    ) USING DELTA
    PARTITIONED BY (date)
    LOCATION '/path/to/delta-table'
""")

# Insert data with SQL
spark.sql("""
    INSERT INTO my_delta_table VALUES
    (1, 'Alice', 25, '2023-01-01'),
    (2, 'Bob', 30, '2023-01-01')
""")

# Merge with SQL
spark.sql("""
    MERGE INTO my_delta_table AS target
    USING updates AS source
    ON target.id = source.id
    WHEN MATCHED THEN UPDATE SET *
    WHEN NOT MATCHED THEN INSERT *
""")
```

## Error Handling and Debugging

```python
# Check for concurrent writes
try:
    deltaTable.update(condition="id = 1", set={"name": "Updated"})
except Exception as e:
    if "ConcurrentAppendException" in str(e):
        print("Concurrent write detected, retrying...")
        # Implement retry logic
    else:
        raise e

# Validate Delta table
try:
    deltaTable.detail().count()
    print("Delta table is valid")
except Exception as e:
    print(f"Delta table validation failed: {e}")
```

## Delta Streaming
Structured Streaming is part of **Apache Spark core**, not the Delta Lake package, but you can add Delta to Streaming. Here's the breakdown:

## Package Origins

**Structured Streaming** (`pyspark.sql.streaming`):
- Part of **Apache Spark core** since Spark 2.0
- Available whenever you have PySpark installed
- No additional packages needed

**Delta Lake** (`delta`):
- Separate package that **extends** Structured Streaming
- Adds Delta-specific capabilities to streaming
- Requires `delta-core` or `pyspark[sql]` with Delta configuration

## How They Work Together

```python
# Basic Structured Streaming (Spark core)
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("Streaming").getOrCreate()

# This is pure Spark - no Delta needed
streaming_df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .load()

# Write to any format (Parquet, JSON, etc.)
query = streaming_df.writeStream \
    .format("parquet") \
    .start("/path/to/output")
```

```python
# Delta Lake + Structured Streaming
from delta import configure_spark_with_delta_pip
from pyspark.sql import SparkSession

# Delta configuration required for Delta streaming
spark = configure_spark_with_delta_pip(
    SparkSession.builder.appName("Delta Streaming")
).getOrCreate()

# Now you can stream to/from Delta tables
query = streaming_df.writeStream \
    .format("delta") \  # This requires Delta Lake
    .start("/path/to/delta-table")
```

## What Delta Lake Adds to Streaming

Delta Lake enhances Structured Streaming with:
- **ACID transactions** for streaming writes
- **Schema enforcement** in streams
- **Exactly-once processing** guarantees
- **Time travel** on streaming data
- **Concurrent read/write** support

So while the streaming engine is Spark core, Delta Lake provides the transactional storage layer that makes streaming more robust and reliable.
