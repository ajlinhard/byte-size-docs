# Spark File Loading COPY INTO
The COPY INTO command in spark has some useful perks as a file loading method. The most important is idempotency or incremental file loading, which requires the installation/configuration of Delta Lake. The syntax is only available in Spark SQL.

## The Basics
### **Basic Structure:**
Here's the basic structure and examples of the COPY INTO statement in Spark:Key points about COPY INTO in Spark:

- `COPY INTO target_table` - destination Delta table
- `FROM source_location` - file path or directory
- `FILEFORMAT` - CSV, JSON, PARQUET, etc.
- `FORMAT_OPTIONS` - file format specific settings
- `COPY_OPTIONS` - copy behavior settings

### **Important Features:**
- **Idempotent by default** - won't reprocess files unless `force = true`
- **Automatic schema inference** - can detect schema from files
- **Pattern matching** - supports wildcards in file paths
- **Transformation support** - can include SELECT statements for data transformation
- **Schema evolution** - handles schema changes with `mergeSchema`

### **Typical Use Cases:**
- Incremental data loading from data lakes
- ETL processes that need to avoid duplicate processing
- Loading data with schema evolution over time
- Batch processing of files in cloud storage

The statement tracks processed files automatically, making it ideal for incremental data pipelines.

---
## Backend Processing Walkthrough

### Table Creation
**The table does not need to exist already.** COPY INTO will automatically create the table if it doesn't exist.

Here's how it works:

**When table doesn't exist:**
- COPY INTO creates a new Delta table
- Schema is inferred from the source files
- Table location is determined by the catalog/database settings
- Uses default table properties

**When table exists:**
- Data is appended to existing table
- Schema must be compatible (unless using `mergeSchema = true`)
- Maintains existing table properties and metadata

**Example of creating a new table:**
```sql
-- This will create the table if it doesn't exist
COPY INTO my_database.new_table
FROM '/path/to/csv/files/'
FILEFORMAT = CSV
FORMAT_OPTIONS ('header' = 'true');
```

**Controlling table creation:**
```sql
-- For more control, you can create the table first
CREATE TABLE my_database.sales_data (
  id BIGINT,
  product_name STRING,
  price DECIMAL(10,2),
  sale_date DATE
) USING DELTA;

-- Then use COPY INTO
COPY INTO my_database.sales_data
FROM '/path/to/sales/*.csv'
FILEFORMAT = CSV
FORMAT_OPTIONS ('header' = 'true');
```

**Best practices:**
- Let COPY INTO create the table for simple cases
- Pre-create the table when you need specific data types, constraints, or table properties
- Use `mergeSchema = true` if source schema might evolve over time

This auto-creation feature makes COPY INTO very convenient for quick data ingestion workflows.

---
## Data Copying/Flow
COPY INTO reads from existing source files and writes to the target Delta table's location.

Here's what actually happens:

**Source files:**
- COPY INTO reads from the source location you specify
- Source files remain unchanged and in their original location
- No new folder is created for the source data

**Target table storage:**
- Data is written to the Delta table's storage location
- This follows your catalog/database configuration
- The Delta table folder structure is managed automatically

**Example flow:**
```sql
-- Source files exist here: /raw-data/sales/2024/07/
-- Target table will be stored in Delta table location
COPY INTO my_database.sales_data
FROM '/raw-data/sales/2024/07/*.csv'
FILEFORMAT = CSV;
```

**What happens:**
1. Reads CSV files from `/raw-data/sales/2024/07/`
2. Writes Delta format files to the table's location (e.g., `/delta-tables/my_database/sales_data/`)
3. Source CSV files remain untouched
4. Creates Delta log files for transaction tracking

**Storage locations:**
- **Source:** Your original data files (CSV, JSON, Parquet, etc.)
- **Target:** Delta table storage location (Parquet + Delta logs)
- **Metadata:** Delta transaction log in `_delta_log` subfolder

The operation is essentially a **read-and-transform** process - it reads from source files and writes to a Delta table format, but doesn't create any new folders in the source location.

---
## Example Code
```sql
-- Basic COPY INTO syntax structure
COPY INTO target_table
FROM source_location
[FILEFORMAT = file_format]
[FORMAT_OPTIONS (option_key = 'option_value', ...)]
[COPY_OPTIONS (option_key = 'option_value', ...)]

-- Example 1: Basic CSV copy
COPY INTO my_database.sales_data
FROM '/path/to/csv/files/'
FILEFORMAT = CSV
FORMAT_OPTIONS (
  'header' = 'true',
  'delimiter' = ',',
  'inferSchema' = 'true'
);

-- Example 2: JSON files with options
COPY INTO my_database.user_events
FROM 's3://my-bucket/json-data/'
FILEFORMAT = JSON
FORMAT_OPTIONS (
  'multiLine' = 'true',
  'timestampFormat' = 'yyyy-MM-dd HH:mm:ss'
)
COPY_OPTIONS (
  'mergeSchema' = 'true',
  'force' = 'false'
);

-- Example 3: Parquet files with pattern matching
COPY INTO my_database.product_catalog
FROM '/data/products/*.parquet'
FILEFORMAT = PARQUET;

-- Example 4: With transformation using SELECT
COPY INTO my_database.cleaned_data
FROM (
  SELECT 
    id,
    UPPER(name) as name,
    price * 1.1 as adjusted_price,
    current_timestamp() as load_time
  FROM '/path/to/source/'
)
FILEFORMAT = CSV
FORMAT_OPTIONS ('header' = 'true');

-- Example 5: With file pattern and partition filtering
COPY INTO my_database.daily_logs
FROM '/logs/year=2024/month=07/day=*/hour=*/*.json'
FILEFORMAT = JSON
COPY_OPTIONS (
  'force' = 'false',  -- Skip files already loaded
  'mergeSchema' = 'true'
);

-- Example 6: Cloud storage with credentials (if not using IAM roles)
COPY INTO my_database.external_data
FROM 's3://bucket/path/'
FILEFORMAT = CSV
FORMAT_OPTIONS (
  'header' = 'true',
  'escape' = '"'
)
COPY_OPTIONS (
  'force' = 'false'
);

-- Common FORMAT_OPTIONS by file type:
-- CSV: 'header', 'delimiter', 'quote', 'escape', 'nullValue', 'dateFormat'
-- JSON: 'multiLine', 'timestampFormat', 'dateFormat'
-- PARQUET: Generally no format options needed

-- Common COPY_OPTIONS:
-- 'force' = 'true'/'false' (reprocess files already loaded)
-- 'mergeSchema' = 'true'/'false' (merge schema evolution)
-- 'validate' = 'true'/'false' (validate before copy)
```
