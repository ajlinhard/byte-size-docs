# Spark & Databricks File Metadata Columns Cheatsheet

When working with files in Apache Spark (3.2.0+) and Databricks, you can access special metadata columns that provide information about source files. These are available as a hidden `_metadata` struct column.

## Platform Availability

| Platform | Version | Support Level |
|----------|---------|---------------|
| **Apache Spark** | 3.2.0+ | Core feature via SPARK-37273 |
| **Databricks** | All versions | Enhanced with Auto Loader extensions |

**Key Differences:**
- **Apache Spark**: Basic `_metadata` struct with core file information
- **Databricks**: Additional Auto Loader specific columns (`file_block_*`) and streaming support

## Metadata Columns Reference

| Column Name | Purpose | Parameters | Example | Availability |
|-------------|---------|------------|---------|--------------|
| `_metadata.file_path` | Full path to source file | String | `s3://my-bucket/data/sales_2024.json` | Spark 3.2+, Databricks |
| `_metadata.file_name` | Filename without directory path | String | `sales_2024.json` | Spark 3.2+, Databricks |
| `_metadata.file_size` | File size in bytes | Long | `1048576` (1MB) | Spark 3.2+, Databricks |
| `_metadata.file_modification_time` | Last modified timestamp | Timestamp | `2024-07-22 10:30:45.123` | Spark 3.2+, Databricks |
| `_metadata.file_block_start` | Starting byte position of block | Long | `0` | Databricks only |
| `_metadata.file_block_length` | Block length in bytes | Long | `134217728` (128MB) | Databricks only |

## Usage Examples

### Basic File Reading with Metadata
```sql
SELECT 
  customer_id,
  amount,
  _metadata.file_name as source_file,
  _metadata.file_modification_time as file_date
FROM json.`/path/to/files/*.json`
```

### Auto Loader Stream with Metadata
```python
df = (spark.readStream
  .format("cloudFiles")
  .option("cloudFiles.format", "json")
  .load("/path/to/files/")
  .select("*", "_metadata.file_path", "_metadata.file_size")
)
```

### COPY INTO with File Tracking
```sql
COPY INTO sales_table
FROM (
  SELECT 
    *,
    _metadata.file_path as source_file,
    current_timestamp() as ingestion_time
  FROM '/mnt/raw/sales/*.parquet'
)
FILEFORMAT = PARQUET
```

### Filtering by Metadata
```sql
SELECT *
FROM parquet.`/data/logs/`
WHERE _metadata.file_size > 1000000
  AND _metadata.file_modification_time >= '2024-07-01'
```

## Key Notes

- **Spark 3.2.0+ Required**: The `_metadata` struct was introduced in Spark 3.2.0 via SPARK-37273
- **Hidden Column**: Only visible when explicitly selected, doesn't appear in `SELECT *`
- **File Reading Only**: Available when reading files directly, not Delta/Iceberg tables
- **Case Sensitive**: Must use exact `_metadata.` prefix and field names
- **Schema Stability**: Databricks warns the struct schema may change in future releases
- **Streaming Support**: Limited in pure Spark, enhanced in Databricks with Auto Loader
- **Performance**: Minimal overhead, valuable for lineage and debugging
- **Best Practice**: Always capture `file_path` for debugging and lineage tracking
