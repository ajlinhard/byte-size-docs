# Spark SQL File Loading Performance
When loading data Spark using Spark SQL there are 2 main choices CTAS (create table as select) or Temp View. Additionally, you can structure or use different technique to incur predicate pushdown and projection pushdown.

#### Topics:
- [CTAS vs Temp View](#CTAS-vs-Temp-View)
- [Direct Path vs. USING Syntax](#Direct-Path-vs.-USING-Syntax)
- [File Loading Schema Settings](#File-Loading-Schema-Settings)

---
# CTAS vs Temp View
## CTAS Syntax
```sql
CREATE TABLE [IF NOT EXISTS] table_name
[USING data_source]
[OPTIONS (key1=val1, key2=val2, ...)]
[PARTITIONED BY (col_name1, col_name2, ...)]
[LOCATION path]
AS SELECT ...
```

## Temp View Syntax
```sql
-- Create temporary view from CSV
CREATE OR REPLACE TEMPORARY VIEW csv_data
USING CSV
OPTIONS (
  path "path/to/file.csv",
  header "true",
  inferSchema "true"
);
```
## When to Use CTAS vs Temp View
The choice between CTAS (CREATE TABLE AS SELECT) and CREATE OR REPLACE TEMPORARY VIEW depends on your use case and requirements. Here's when to use each:

## Use CTAS when:

**You need persistent storage**
- Data should survive beyond the Spark session
- Multiple applications need to access the same data
- You want to create a permanent table in your catalog

**Performance optimization is important**
- Want to control storage format (Parquet, Delta, etc.)
- Need partitioning for better query performance
- Want to enable features like Z-ordering or table statistics

**Example:**
```sql
CREATE TABLE sales_parquet
USING PARQUET
PARTITIONED BY (year, month)
AS SELECT 
    product, amount, 
    YEAR(date) as year, 
    MONTH(date) as month
FROM raw_sales_data;
```

## Use CREATE OR REPLACE TEMPORARY VIEW when:

**Working with exploratory data analysis**
- Quick data exploration and prototyping
- One-time analysis that doesn't need persistence
- Testing queries before creating permanent tables

**Memory and storage efficiency**
- Don't want to duplicate data on disk
- Working with large files where copying would be expensive
- Just need a logical reference to existing data

**Session-scoped work**
- Data only needed during current Spark session
- Want to avoid cluttering the catalog with temporary tables
- Creating intermediate views for complex queries

**Example:**
```sql
CREATE OR REPLACE TEMPORARY VIEW sales_view
AS SELECT * FROM parquet.`/path/to/sales/data/*.parquet`
WHERE date >= '2024-01-01';
```

## Performance considerations:

**CTAS advantages:**
- Faster subsequent queries (data is optimized and potentially indexed)
- Can leverage table statistics for query optimization
- Better for repeated access patterns

**Temporary View advantages:**
- No initial data copying overhead
- Immediate availability
- No storage space consumed

## Common pattern:
Many workflows use both - temporary views for initial exploration and transformation, then CTAS for final, optimized tables:

```sql
-- Exploration phase
CREATE OR REPLACE TEMPORARY VIEW raw_data
AS SELECT * FROM json.`/path/to/raw/*.json`;

-- After validation, create optimized permanent table
CREATE TABLE clean_sales
USING DELTA
PARTITIONED BY (date)
AS SELECT 
    clean_product_name(product) as product,
    date,
    amount
FROM raw_data
WHERE amount > 0;
```

The key is matching the tool to your data lifecycle needs - temporary views for transient work, CTAS for durable assets.

---
# Direct Path vs. USING Syntax
Lets compare the following syntaxes used in both CTAS and Temp View.
**Direct Path**
```sql
CREATE OR REPLACE TEMPORARY VIEW sales_view AS
SELECT *
FROM parquet./path/to/sales/data/*.parquet
WHERE date >= '2024-01-01';
```

**USING + OPTIONS**
```sql
CREATE OR REPLACE TEMPORARY VIEW parquet_data
USING PARQUET
OPTIONS (
  path "path/to/file.parquet"
);
```
The main differences between these two Spark SQL syntaxes relate to **data source integration**, **performance characteristics**, and **flexibility**:

## Key Differences

### **Data Source Integration**
- **Option 1** uses the **direct file path syntax** (`parquet.`/path/`) which is a shorthand for reading Parquet files
- **Option 2** uses the **explicit USING clause** with OPTIONS, which is more formal and configurable

### **Performance Characteristics**

**Option 1 (Direct Path + WHERE):**
- **Predicate pushdown**: The `WHERE date >= '2024-01-01'` clause can be pushed down to the file scanning level
- **Partition pruning**: If your Parquet files are partitioned by date, Spark can skip entire files/partitions
- **Immediate filtering**: The filter is applied during the view creation, potentially reducing the data footprint

**Option 2 (USING + OPTIONS):**
- **Deferred filtering**: No built-in filtering mechanism - you'd need to filter when querying the view
- **More explicit configuration**: The OPTIONS block allows for additional Parquet-specific settings
- **Cleaner separation**: The data source definition is separate from any transformations

### **Flexibility and Configuration**

**Option 1 limitations:**
- Limited configuration options
- Wildcard pattern (`*.parquet`) for multiple files
- Less explicit about data source parameters

**Option 2 advantages:**
- More configuration options available through OPTIONS:
```sql
OPTIONS (
  path "path/to/file.parquet",
  mergeSchema "true",
  recursiveFileLookup "true"
)
```
- Better for complex data source configurations
- More maintainable for enterprise environments

### **Performance Recommendation**

**Use Option 1 when:**
- You need immediate filtering/transformation
- Working with partitioned data where predicate pushdown is beneficial
- Simple read scenarios with basic filtering

**Use Option 2 when:**
- You need fine-grained control over Parquet reading options
- Building reusable views that will be filtered differently in various queries
- Working in environments where explicit data source configuration is preferred

For your specific examples, **Option 1 would likely perform better** due to the immediate date filtering and potential partition pruning, assuming your Parquet files are organized by date.

---
# File Loading Schema Settings
Yes, you can specify schema when using `CREATE TEMPORARY VIEW` with `USING + OPTIONS`, but the approach varies by data source format. Here's how:

## Method 1: Using schema option (for some formats)

```sql
CREATE OR REPLACE TEMPORARY VIEW sales_with_schema
USING CSV
OPTIONS (
  path "/path/to/data.csv",
  header "true",
  schema "product STRING, date DATE, amount DECIMAL(10,2)"
)
```

## Method 2: Using individual column type options (CSV-specific)

```sql
CREATE OR REPLACE TEMPORARY VIEW sales_typed
USING CSV
OPTIONS (
  path "/path/to/data.csv",
  header "true",
  inferSchema "false",
  timestampFormat "yyyy-MM-dd HH:mm:ss",
  dateFormat "yyyy-MM-dd"
)
```

## Method 3: Combining USING with AS SELECT for schema control

```sql
CREATE OR REPLACE TEMPORARY VIEW sales_controlled
USING CSV
OPTIONS (
  path "/path/to/data.csv",
  header "true",
  inferSchema "false"
)
AS SELECT 
  CAST(_c0 AS STRING) as product,
  CAST(_c1 AS DATE) as date,
  CAST(_c2 AS DECIMAL(10,2)) as amount
```

## Method 4: For JSON with schema

```sql
CREATE OR REPLACE TEMPORARY VIEW json_with_schema
USING JSON
OPTIONS (
  path "/path/to/data.json",
  multiLine "true",
  schema "product STRING, date DATE, amount DECIMAL(10,2), metadata STRUCT<source:STRING, version:INT>"
)
```

## Method 5: For Parquet (schema usually preserved)

```sql
CREATE OR REPLACE TEMPORARY VIEW parquet_view
USING PARQUET
OPTIONS (
  path "/path/to/data.parquet"
)
-- Parquet already has schema embedded, but you can still cast:
AS SELECT 
  product,
  date,
  CAST(amount AS DECIMAL(12,2)) as amount  -- Change precision
FROM parquet.`/path/to/data.parquet`
```

## Format-specific schema options:

### CSV:
```sql
CREATE OR REPLACE TEMPORARY VIEW csv_strict
USING CSV
OPTIONS (
  path "/path/to/sales.csv",
  header "true",
  inferSchema "false",
  schema "product STRING NOT NULL, date DATE NOT NULL, amount DECIMAL(10,2)",
  mode "FAILFAST",  -- Fail on bad records
  columnNameOfCorruptRecord "_corrupt_record"
)
```

### Delta Lake:
```sql
CREATE OR REPLACE TEMPORARY VIEW delta_view
USING DELTA
OPTIONS (
  path "/path/to/delta/table"
)
-- Delta tables have enforced schema, but you can still transform:
AS SELECT 
  product,
  date,
  amount,
  CURRENT_TIMESTAMP() as loaded_at
```

## Limitations and considerations:

**1. Not all formats support direct schema specification:**
```sql
-- This works for CSV
CREATE OR REPLACE TEMPORARY VIEW csv_view
USING CSV
OPTIONS (schema "col1 STRING, col2 INT")

-- This may not work for all formats
CREATE OR REPLACE TEMPORARY VIEW parquet_view
USING PARQUET
OPTIONS (schema "col1 STRING, col2 INT")  -- May be ignored
```

**2. Best practice - combine with AS SELECT:**
```sql
CREATE OR REPLACE TEMPORARY VIEW robust_view
USING CSV
OPTIONS (
  path "/path/to/data.csv",
  header "true",
  inferSchema "false"
)
AS SELECT 
  CASE 
    WHEN _c0 IS NULL OR _c0 = '' THEN 'Unknown'
    ELSE CAST(_c0 AS STRING)
  END as product,
  TRY_CAST(_c1 AS DATE) as date,
  TRY_CAST(_c2 AS DECIMAL(10,2)) as amount
WHERE TRY_CAST(_c1 AS DATE) IS NOT NULL  -- Filter invalid dates
```

**3. Schema evolution handling:**
```sql
CREATE OR REPLACE TEMPORARY VIEW evolving_schema
USING JSON
OPTIONS (
  path "/path/to/data/*.json",
  multiLine "true"
)
AS SELECT 
  product,
  date,
  amount,
  -- Handle optional new columns
  COALESCE(category, 'uncategorized') as category,
  COALESCE(region, 'unknown') as region
```

The `USING + OPTIONS` approach is powerful for format-specific configurations, but combining it with `AS SELECT` gives you the most control over schema enforcement and data validation.
