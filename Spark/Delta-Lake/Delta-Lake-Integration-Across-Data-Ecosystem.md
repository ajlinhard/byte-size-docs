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

---
## What Databricks Runtime Includes by Default
**Databricks runtime has mixed support for the delta-rs Python package**, and there are important distinctions to understand:

**Built-in Delta Lake Support:**
All tables created on Databricks use Delta Lake by default, and Delta Lake is the default for all reads, writes, and table creation commands in Databricks. This uses the **Spark-based Delta Lake implementation** (not delta-rs).

**Native Delta APIs Available:**
- `from delta.tables import DeltaTable` (Spark-based)
- Standard `df.write.format("delta")` operations
- Time travel, MERGE operations, etc.

## delta-rs (Python Package) Compatibility Issues

**Known Problems:**
There are documented issues using delta-rs on Databricks runtime, including authentication problems where Databricks clusters use IAM roles to access S3 buckets, but delta-rs fails with errors like "Failed to load checkpoint: Invalid JSON in checkpoint"

**Version Compatibility Conflicts:**
If you create Delta tables using the Databricks Spark Engine, the read & write version will be higher, and if you want to write to those delta tables created by Databricks, Python (delta-rs) is currently not supported with that

## Key Differences

**Databricks Native (Spark-based):**
```python
# This works seamlessly in Databricks
from delta.tables import DeltaTable
deltaTable = DeltaTable.forName(spark, "main.default.people_10m")
deltaTable.history().show()
```

**delta-rs (Rust-based):**
```python
# This may have compatibility issues in Databricks
from deltalake import DeltaTable
dt = DeltaTable("s3://bucket/path")  # May fail with auth/version issues
```

## Why the Conflicts Exist

**Different Implementations:**
The deltalake implementation (delta-rs) has no dependencies on Java, Spark, or Databricks, while "Delta Spark" refers to the Scala implementation that depends on Spark and Java

**Authentication Mechanisms:**
- Databricks uses Spark-integrated authentication
- delta-rs has its own authentication system that may not work with Databricks' IAM integration

## Recommendations

**For Databricks Users:**
1. **Use the built-in Spark-based Delta APIs** - they're optimized for Databricks
2. **Avoid delta-rs in Databricks runtime** unless you have specific use cases
3. **Use delta-rs outside of Databricks** for local development or non-Spark environments

**Best Practice:**
```python
# In Databricks - use this
from delta.tables import DeltaTable
deltaTable = DeltaTable.forPath(spark, "/path/to/table")

# Outside Databricks - use this  
from deltalake import DeltaTable
dt = DeltaTable("/path/to/table")
```

The general consensus is that while you *can* install delta-rs in Databricks runtime, it's not recommended due to compatibility issues and redundancy with the already excellent built-in Spark-based Delta Lake support.

---
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
