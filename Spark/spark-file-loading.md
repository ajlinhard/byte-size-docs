# Spark File Loading Cheat Sheet

## Basic SparkSession Setup

```python
from pyspark.sql import SparkSession
from pyspark.sql.types import *

# Create SparkSession
spark = SparkSession.builder \
    .appName("File Loading Example") \
    .config("spark.sql.adaptive.enabled", "true") \
    .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
    .getOrCreate()
```

## CSV Files

### Basic CSV Loading
```python
# Simple CSV load
df = spark.read.csv("path/to/file.csv", header=True, inferSchema=True)

# With explicit options
df = spark.read \
    .option("header", "true") \
    .option("inferSchema", "true") \
    .option("delimiter", ",") \
    .option("quote", '"') \
    .option("escape", "\\") \
    .csv("path/to/file.csv")
```

### Advanced CSV Options
```python
# Handle bad records and null values
df = spark.read \
    .option("header", "true") \
    .option("inferSchema", "true") \
    .option("nullValue", "NULL") \
    .option("emptyValue", "") \
    .option("nanValue", "NaN") \
    .option("mode", "PERMISSIVE") \
    .option("columnNameOfCorruptRecord", "_corrupt_record") \
    .option("multiLine", "true") \
    .option("escape", '"') \
    .csv("path/to/file.csv")

# With custom schema
schema = StructType([
    StructField("id", IntegerType(), True),
    StructField("name", StringType(), True),
    StructField("value", DoubleType(), True),
    StructField("date", DateType(), True)
])

df = spark.read \
    .option("header", "true") \
    .schema(schema) \
    .csv("path/to/file.csv")
```

### Multiple CSV Files
```python
# Load multiple CSV files
df = spark.read.csv(["file1.csv", "file2.csv"], header=True, inferSchema=True)

# Load all CSV files in a directory
df = spark.read.csv("path/to/directory/*.csv", header=True, inferSchema=True)

# With filename column
df = spark.read \
    .option("header", "true") \
    .option("inferSchema", "true") \
    .option("pathGlobFilter", "*.csv") \
    .csv("path/to/directory/") \
    .withColumn("filename", input_file_name())
```

## Parquet Files

### Basic Parquet Loading
```python
# Simple Parquet load
df = spark.read.parquet("path/to/file.parquet")

# Multiple Parquet files
df = spark.read.parquet("path/to/directory/*.parquet")
df = spark.read.parquet(["file1.parquet", "file2.parquet"])
```

### Parquet with Schema Evolution
```python
# Enable schema merging for different schemas
df = spark.read \
    .option("mergeSchema", "true") \
    .parquet("path/to/directory/")

# Read specific columns only
df = spark.read.parquet("path/to/file.parquet").select("col1", "col2")
```

### Partitioned Parquet
```python
# Read partitioned Parquet (automatically discovers partitions)
df = spark.read.parquet("path/to/partitioned_table/")

# Read specific partitions
df = spark.read.parquet("path/to/partitioned_table/year=2023/month=01/")

# Discover partitions with custom schema
df = spark.read \
    .option("basePath", "path/to/partitioned_table/") \
    .parquet("path/to/partitioned_table/year=2023/")
```

## JSON Files

### Basic JSON Loading
```python
# Simple JSON load
df = spark.read.json("path/to/file.json")

# Multiple JSON files
df = spark.read.json(["file1.json", "file2.json"])
df = spark.read.json("path/to/directory/*.json")
```

### JSON with Options
```python
# Handle malformed JSON
df = spark.read \
    .option("mode", "PERMISSIVE") \
    .option("columnNameOfCorruptRecord", "_corrupt_record") \
    .json("path/to/file.json")

# Multi-line JSON
df = spark.read \
    .option("multiLine", "true") \
    .option("mode", "PERMISSIVE") \
    .json("path/to/file.json")

# Custom date format
df = spark.read \
    .option("timestampFormat", "yyyy-MM-dd HH:mm:ss") \
    .option("dateFormat", "yyyy-MM-dd") \
    .json("path/to/file.json")
```

### JSON with Schema
```python
# Define schema for JSON
schema = StructType([
    StructField("id", IntegerType(), True),
    StructField("user", StructType([
        StructField("name", StringType(), True),
        StructField("age", IntegerType(), True)
    ]), True),
    StructField("tags", ArrayType(StringType()), True)
])

df = spark.read.schema(schema).json("path/to/file.json")
```

## Avro Files

### Basic Avro Loading
```python
# Simple Avro load (requires spark-avro package)
df = spark.read.format("avro").load("path/to/file.avro")

# Multiple Avro files
df = spark.read.format("avro").load("path/to/directory/*.avro")
df = spark.read.format("avro").load(["file1.avro", "file2.avro"])
```

### Avro with Schema Registry
```python
# Load Avro with external schema
df = spark.read \
    .format("avro") \
    .option("avroSchema", schema_string) \
    .load("path/to/file.avro")

# Load Avro with schema from registry (Confluent Schema Registry)
df = spark.read \
    .format("avro") \
    .option("schemaRegistryUrl", "http://schema-registry:8081") \
    .option("schemaId", "123") \
    .load("path/to/file.avro")
```

## Common Patterns and Best Practices

### Error Handling and Data Quality
```python
# Count corrupt records
corrupt_count = df.filter(col("_corrupt_record").isNotNull()).count()

# Show sample of corrupt records
df.filter(col("_corrupt_record").isNotNull()).select("_corrupt_record").show(5, truncate=False)

# Drop corrupt records
clean_df = df.filter(col("_corrupt_record").isNull()).drop("_corrupt_record")
```

### Performance Optimization
```python
# Repartition for better performance
df = spark.read.parquet("path/to/large_file.parquet").repartition(200)

# Coalesce small files
df = spark.read.csv("path/to/many_small_files/*.csv").coalesce(10)

# Cache frequently accessed data
df.cache()
df.count()  # Trigger caching
```

### Dynamic File Loading
```python
from pyspark.sql.functions import *

# Load files with metadata
df = spark.read.json("path/to/directory/*.json") \
    .withColumn("file_name", input_file_name()) \
    .withColumn("file_modification_time", from_unixtime(unix_timestamp()))

# Filter by file modification time
recent_files_df = df.filter(col("file_modification_time") > "2023-01-01")
```

### Schema Validation
```python
# Validate expected columns exist
expected_columns = {"id", "name", "value"}
actual_columns = set(df.columns)
missing_columns = expected_columns - actual_columns

if missing_columns:
    raise ValueError(f"Missing columns: {missing_columns}")

# Validate data types
expected_schema = {
    "id": "int",
    "name": "string", 
    "value": "double"
}

for col_name, expected_type in expected_schema.items():
    actual_type = dict(df.dtypes)[col_name]
    if actual_type != expected_type:
        print(f"Warning: {col_name} is {actual_type}, expected {expected_type}")
```

### File Format Detection
```python
def detect_and_load_file(file_path):
    """Automatically detect file format and load appropriately"""
    if file_path.endswith('.csv'):
        return spark.read.csv(file_path, header=True, inferSchema=True)
    elif file_path.endswith('.parquet'):
        return spark.read.parquet(file_path)
    elif file_path.endswith('.json'):
        return spark.read.json(file_path)
    elif file_path.endswith('.avro'):
        return spark.read.format("avro").load(file_path)
    else:
        raise ValueError(f"Unsupported file format: {file_path}")

# Usage
df = detect_and_load_file("data/myfile.parquet")
```

## Useful DataFrame Operations After Loading

```python
# Quick data exploration
df.printSchema()
df.show(5)
df.describe().show()
df.count()

# Column operations
df.columns
df.dtypes
df.select("col1", "col2").show()

# Sample data
df.sample(0.1).show()  # 10% sample
df.limit(100).show()   # First 100 rows
```

## Troubleshooting Common Issues

```python
# Handle OutOfMemoryError
spark.conf.set("spark.sql.adaptive.enabled", "true")
spark.conf.set("spark.sql.adaptive.coalescePartitions.enabled", "true")

# Debug partition count
print(f"Number of partitions: {df.rdd.getNumPartitions()}")

# Check for skewed data
df.groupBy("partition_column").count().orderBy(desc("count")).show()

# Handle timezone issues for timestamps
spark.conf.set("spark.sql.session.timeZone", "UTC")
```
