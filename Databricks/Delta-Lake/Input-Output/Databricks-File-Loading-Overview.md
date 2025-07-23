# Databricks File Loading Overview
When focused on data ingestion Databricks supports the Spark syntaxes in both SQL and python, as well as structured stream and the Delta Lake project syntaxes.
- SQL Batch
  - CTAS with USING or Direct Path
  - Temp View with USING or Direct Path
- Python Batch
  - spark.read.format()
  - spark.write.mode()
- Incremental Batch
  - COPY INTO (a sql-only syntax)
- Streaming
  - CREATE OR REFRESH STREAMING
  - spark.readStream
 
They all have different use cases based on whether you are loading for adhoc analysis or full refresh, vs. incremental processing, vs. streaming for near real-time.

## High-level Summary of Features
![image](https://github.com/user-attachments/assets/45e7cf59-9a52-4b3c-9a40-c566cf1b137e)

## CTAS (create table as select) and Temp View
These 2 mehtods have some subtly in their individual use cases, but they share the same functionality of reading all data everytime as directed by the query.

#### Links
- [Spark SQL File Loading Overview](https://github.com/ajlinhard/byte-size-docs/blob/main/Spark/SQL/Spark-SQL-File-Loading.md)

## PySpark  `spark.read` and `spark.write`
This version of reading and writing always do exactly what the settings for the path are. Meaning the will re-read or overwrite all data. Compared to COPY INTO and Streaming which are idempotent. Great for adhoc analysis, initial dev, or full refresh data.

#### Links
- [Spark Read Cheatsheet](https://github.com/ajlinhard/byte-size-docs/blob/main/Spark/Input-Output/Spark-File-Loading-Spark-Read.md)
- [Spark Write Overview](https://github.com/ajlinhard/byte-size-docs/blob/main/Spark/Input-Output/Spark-Write-Data-Overview.md)

## COPY INTO
Another loading method for the Spark SQL users, but this method has idempotency of all files loaded FROM <source data> INTO <output table>. The syntax works with Spark SQL, but requires the installation of Delta Lake and configuration of the spark session with the default storage method as "delta".

#### Links:
[Spark COPY INTO Overview](https://github.com/ajlinhard/byte-size-docs/blob/main/Spark/Input-Output/Spark-File-Loading-COPY-INTO.md)
[Databricks extension read_files()](https://docs.databricks.com/aws/en/sql/language-manual/functions/read_files)

## Auto Loader
Databricks auto loader is an extension of the Spark Core streaming functionality. The main area of extension is the format "cloudFiles", which as the name suggest is optimize for cloud storage options.
```spark.readStream.format("cloudFiles")```

#### Links
- [Databricks Auto Loader - Home Page](https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/)
- [Spark Streaming Cheatsheet](https://github.com/ajlinhard/byte-size-docs/blob/main/Spark/Input-Output/spark-streaming-cheatsheet.md)

---
# Spark vs Databricks Differences

Great question! These are two different approaches to handling malformed data, with some key distinctions:

## columnNameOfCorruptRecord (Standard Spark)

**Purpose**: Captures entire unparseable records as raw strings
**Scope**: Works with JSON and CSV readers
**Behavior**: 
- When a record can't be parsed according to the schema, the entire raw record is stored in this column
- Valid records have null in this column
- You must pre-define the column in your schema

```python
schema = StructType([
    StructField("name", StringType(), True),
    StructField("age", IntegerType(), True),
    StructField("_corrupt_record", StringType(), True)
])

df = spark.read \
    .option("columnNameOfCorruptRecord", "_corrupt_record") \
    .schema(schema) \
    .json("file.json")
```

## rescuedDataColumn (Databricks Feature)

**Purpose**: Captures data that doesn't fit the target schema but is still valid JSON/data
**Scope**: More comprehensive - works across multiple data sources and scenarios
**Behavior**:
- Captures "extra" fields that exist in the data but not in your target schema
- Stores partially parsed data (not just raw strings)
- Can capture schema evolution scenarios
- Automatically added without schema modification

```python
df = spark.read \
    .option("rescuedDataColumn", "_rescued_data") \
    .schema(target_schema) \
    .json("file.json")
```

## Key Differences

| Aspect | columnNameOfCorruptRecord | rescuedDataColumn |
|--------|---------------------------|-------------------|
| **Data Type** | Raw string of unparseable record | Structured data (map/struct) |
| **Use Case** | Completely malformed records | Schema mismatches, extra fields |
| **Availability** | Standard Apache Spark | Databricks-specific |
| **Schema Requirement** | Must define in schema | Auto-added |
| **Data Preservation** | Less structured | More queryable |

## When to Use Which

- **Use `columnNameOfCorruptRecord`** when you have genuinely malformed data that can't be parsed at all
- **Use `rescuedDataColumn`** when you have valid data that just doesn't match your expected schema (extra columns, schema evolution, etc.)

The Databricks `rescuedDataColumn` is generally more powerful for handling schema evolution and data quality scenarios, while `columnNameOfCorruptRecord` is better for catching truly corrupt data.
