# Dataricks File Loading CTAS
When loading data into Databricks there are 3 high level methods: Batch, Incremental Batch, and Streaming. Additionally, there are multiple syntaxes for accomplishing each depending on the use case.

## Batch or Incremental Batch
All Spark Syntaxes are support in Databricks. So, CTAS, spark.read + spark.write, Temp View are all supported. Additionally, Databricks has extend this with its own loading method and engine for ease of use and performance gains.

### CTAS + read_files()
CTAS with `read_files()` is the additionally supported loading syntax in Databricks! This is a very common and powerful pattern for creating tables directly from files without first creating external tables.

Your syntax example is correct:

```sql
CREATE TABLE new_table AS
SELECT *
FROM read_files(
    '/path/to/files/',
    format => 'parquet'
);
```

The `read_files()` function supports many formats and options:

```sql
-- CSV example
CREATE TABLE csv_table AS
SELECT *
FROM read_files(
    '/path/to/csv/files/',
    format => 'csv',
    header => true,
    inferSchema => true
);

-- JSON example  
CREATE TABLE json_table AS
SELECT *
FROM read_files(
    '/path/to/json/files/',
    format => 'json',
    multiLine => true
);

-- With schema enforcement
CREATE TABLE structured_table AS
SELECT 
    col1::string,
    col2::int,
    col3::timestamp
FROM read_files(
    '/path/to/files/',
    format => 'parquet'
);
```

This approach is particularly useful because:
- It automatically handles file discovery and schema inference
- Works with partitioned data
- Supports wildcards in paths
- Can read from various cloud storage locations
- Creates Delta tables by default in Databricks

The `read_files()` function is a Databricks-specific enhancement to Spark SQL that makes file ingestion much more streamlined than traditional Spark approaches.

## Native Spark SQL vs Databricks
The `read_files()` function is **not** part of native Spark SQL - it's a Databricks-specific enhancement. This is an important distinction.

**Native Spark SQL** for reading files in CTAS would use more verbose syntax:
```sql
-- Native Spark SQL approach
CREATE TABLE new_table 
USING PARQUET
LOCATION '/path/to/files/'
AS SELECT * FROM parquet.`/path/to/files/`;
```

**Databricks `read_files()`** is more powerful because it provides:

1. **Unified interface for multiple formats** - one function handles CSV, JSON, Parquet, Avro, etc.
2. **Advanced schema inference** - better at handling complex nested structures and mixed data types
3. **Intelligent file discovery** - automatically finds all files in directories and subdirectories
4. **Built-in error handling** - more graceful handling of malformed files
5. **Streaming integration** - can easily transition from batch to streaming with same syntax
6. **Cloud-optimized** - better performance with cloud storage systems (S3, ADLS, GCS)
7. **Automatic partitioning detection** - recognizes partitioned directory structures
8. **Flexible schema evolution** - handles schema changes across files more elegantly
9. ##Delta by Default** -Creates Delta tables by default in Databricks

So if you're using pure Apache Spark (not Databricks), you'd need to use the more traditional approaches like `spark.read.format()` or direct format functions like `parquet.` or `json.` in SQL.

The `read_files()` function is part of Databricks' value-add on top of open-source Spark, making data ingestion significantly more streamlined.

---
## CTAS + read_files() vs Pyspark (spark.read())
The performance comparison between Databricks `read_files()` and PySpark `spark.read` is nuanced - they're not necessarily faster/slower than each other, but rather optimized for different use cases.

## Performance Characteristics

**Databricks `read_files()` advantages:**
- **Cloud-optimized I/O** - better integration with cloud storage APIs and caching
- **Automatic file pruning** - intelligently skips files that don't match query predicates
- **Vectorized reading** - uses optimized C++ readers for formats like Parquet
- **Built-in caching** - leverages Databricks' Delta Cache more effectively
- **Parallel schema inference** - faster when dealing with many files with varying schemas

**PySpark `spark.read` advantages:**
- **Lower overhead** - no additional abstraction layer
- **More predictable** - standard Spark optimization rules apply
- **Better for large single files** - less overhead when reading few, large files
- **Explicit control** - you can tune specific reader options more granularly

## When `read_files()` is typically faster:

```python
# Scenario 1: Many small files with schema inference
df = spark.sql("""
    SELECT * FROM read_files(
        '/path/with/thousands/of/files/',
        format => 'json'
    )
""")

# Scenario 2: Partitioned data with predicate pushdown
df = spark.sql("""
    SELECT * FROM read_files(
        '/partitioned/data/',
        format => 'parquet'
    ) WHERE year = 2023
""")
```

## When `spark.read` might be faster:

```python
# Large single files with known schema
df = spark.read.schema(known_schema).parquet("/path/to/large/file.parquet")

# When you need specific reader configurations
df = spark.read.option("multiline", "true").option("maxColumnsPerLine", 1000).json("/path")
```

## Bottom Line

`read_files()` is generally more performant for typical data lake scenarios (many files, cloud storage, unknown schemas), while `spark.read` can be faster for simpler, more controlled reading scenarios. The performance difference usually isn't dramatic - choose based on your specific use case and environment.
