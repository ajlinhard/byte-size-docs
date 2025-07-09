# Delta Lake Integration Across the Data Ecosystem
**Many projects beyond Spark have integrated Delta Lake!** The ecosystem has grown significantly, with Delta Lake offering two main approaches for integration:

## Native Delta Lake Integrations (Non-Spark)

### **Query Engines & Databases**
Delta Lake has connectors for Apache Spark™, PrestoDB, Flink, Trino, and Hive, plus APIs for compute engines including Snowflake, Google BigQuery, Athena, Redshift, Databricks, and Azure Fabric:

- **Apache Flink** - Write operations (preview)
- **Trino** - Read and write operations  
- **PrestoDB** - Read operations
- **Apache Hive** - Via Delta Standalone
- **DuckDB** - Via delta-rs integration
- **Snowflake, BigQuery, Athena, Redshift** - Native support

### **Python Data Libraries (via delta-rs)**
The delta-rs library lets you read, write, and manage Delta Lake tables with Python or Rust without Spark or Java, using Apache Arrow under the hood, making it compatible with pandas, DuckDB, Polars, Dask, Daft, and other Arrow-integrated libraries:

- **pandas** - Read/write Delta tables directly
- **Polars** - Built-in `read_delta()` and `write_delta()` methods
- **DuckDB** - Query Delta tables via delta-rs
- **Dask** - Via dask-deltatable library
- **Daft** - High-performance distributed Delta reading

### **Cloud Services**
Delta Lake integrates with managed services including AWS Athena (native support starting with Athena SQL 3.0), Amazon EMR (starting with release 6.9.0), AWS Glue (3.0 and later supports Delta Lake), and Azure Stream Analytics (provides native write support)

## Two Integration Approaches

**1. Delta Standalone (JVM-based):**
- For Java/Scala projects
- Used by Flink, Hive, PrestoDB, Trino
- Requires JVM but no Spark dependency

**2. delta-rs (Rust-based):**
- Uses Apache Arrow, avoiding JVM entirely
- Python and Rust APIs
- Powers integrations with pandas, Polars, DuckDB, etc.

## Example Usage (Non-Spark)

**Polars (built-in Delta support):**
```python
import polars as pl

# Read Delta table
df = pl.read_delta("s3://my-bucket/delta-table")

# Write Delta table  
df.write_delta("path/to/delta-table")
```

**pandas via delta-rs:**
```python
from deltalake import DeltaTable, write_deltalake
import pandas as pd

# Write pandas DataFrame to Delta
write_deltalake("./data/delta", df)

# Read Delta table to pandas
dt = DeltaTable("./data/delta")
df = dt.to_pandas()
```

**DuckDB:**
```python
import duckdb
from deltalake import DeltaTable

# Read Delta table into DuckDB
dt = DeltaTable("delta-table-path")
duckdb.sql("SELECT * FROM dt.to_pyarrow_dataset()")
```

## Performance Benefits

Recent benchmarks show that specialized tools can significantly outperform traditional approaches - for example, Daft's Delta Lake reader is 2x faster than Polars, 15.8x faster than pandas, and 2.3x faster than DuckDB for partitioned Delta Lake tables.

The ecosystem has evolved from Spark-centric to supporting diverse compute engines, making Delta Lake accessible across modern data stacks without requiring Spark infrastructure.
