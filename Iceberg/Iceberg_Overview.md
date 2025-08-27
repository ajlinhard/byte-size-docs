# Iceberg Overview:
Apache Iceberg is a rich metadata system that sits between your query engines and your data. It is capable of handling interactions between Hive, Spark, and MapReduce then interact with different storage types S3, HDFS, etc.
Additionally, Iceberg has metadata on its metadata overtime allowing for new features like schema evolution, partition evolution, data time travel, and more.

## Documentation/Tutorials:
1. [Apache Iceberg Official Page](https://iceberg.apache.org/)
2. [What is Iceberg? The Evolution of Data Management](https://www.youtube.com/watch?v=6tjSVXpHrE8&t=4s)
3. [Databricks Unity Catalog - Iceberg](https://www.databricks.com/blog/announcing-full-apache-iceberg-support-databricks)
4. [Datacamp Tutorial](https://www.datacamp.com/tutorial/apache-iceberg)
5. [Apache Iceberg Maintenance Docs](https://iceberg.apache.org/docs/1.5.1/maintenance/)
6. [Iceberg for Data Ops](https://www.phdata.io/blog/how-querying-apache-iceberg-metadata-can-elevate-your-dataops-strategy/)

Iceberg is a table format designed to handle massive datasets in data lakes. Think of it as a smart filing system that keeps track of where your data lives and what it looks like, even as you constantly add, modify, or delete information.

## The Basic Concept

Traditional data storage is like having files scattered across many folders with no central index. Iceberg creates a detailed catalog that tracks every piece of data, its location, and its structure. This catalog gets updated atomically - meaning changes either complete entirely or don't happen at all, preventing corruption.

## Core Components

**Metadata Layer**: Iceberg maintains three levels of metadata files. The catalog points to metadata files, which point to manifest files, which finally point to your actual data files. This hierarchy allows efficient tracking of changes without scanning entire datasets.

**Schema Evolution**: You can safely add, remove, or modify columns without rewriting existing data. Iceberg handles the mapping between old and new schemas automatically.

**Iceberg's Primary Use Cases:**
- Data lakes and lakehouses (not just traditional warehouses)
- Analytics workloads requiring ACID transactions
- Time travel and schema evolution scenarios
- Large-scale batch and streaming processing

**Streaming Data with Iceberg:**
You can absolutely write streaming data directly to Iceberg format. This is one of Iceberg's key strengths. Here's how it works:

**Streaming Writes to Iceberg:**
- **Apache Flink** has native Iceberg support for streaming writes
- **Apache Spark Structured Streaming** can write to Iceberg tables
- **Apache Kafka** can stream data that gets written to Iceberg via connectors
- Real-time ingestion frameworks like **Apache Pulsar** also support Iceberg

**Key Benefits for Streaming:**
1. **ACID transactions** - Each streaming micro-batch becomes an atomic commit
2. **Schema evolution** - Handle schema changes in streaming data gracefully  
3. **Time travel** - Query historical versions of your streaming data
4. **Compaction** - Automatically optimize small streaming files into larger ones
5. **Concurrent reads/writes** - Analytics can run while streaming continues

**Common Streaming Architecture:**
```
Streaming Source → Processing Engine → Iceberg Table → Analytics/BI Tools
    (Kafka)           (Flink/Spark)      (S3/HDFS)        (Trino/Spark)
```

So Iceberg isn't just for warehousing - it's excellent for modern data lake architectures where you want to combine streaming ingestion with analytical capabilities. The format handles both batch and streaming workloads seamlessly, making it ideal for real-time analytics use cases.

**Other Iceberg Features**
- [Iceberg Stored Procedures](https://iceberg.apache.org/docs/latest/spark-procedures/)
- [Iceberg Catalog Config](https://www.tabular.io/apache-iceberg-cookbook/getting-started-catalog-background/)

## Detailed Example: E-commerce Analytics

Imagine you're managing customer transaction data for a large e-commerce platform. Your table starts with columns like customer_id, product_id, purchase_amount, and timestamp.

**Initial Setup**: When you create your Iceberg table, it generates a metadata file containing the schema definition and points to manifest files. These manifest files catalog your actual parquet data files stored in S3 or similar storage.

**Daily Operations**: Each night, you ingest new transaction data. Instead of appending to existing files, Iceberg writes new data files and updates the manifest files to include them. The metadata file gets updated to point to the new manifest version. This happens atomically - other users either see the complete update or the previous version, never a partial state.

**Schema Changes**: Three months later, you need to add a "discount_applied" column. With traditional systems, you'd need to rewrite terabytes of historical data. Iceberg simply updates the schema in the metadata layer. When querying old data, it automatically provides null values for the new column. New data includes the actual discount values.

**Time Travel Queries**: Your data science team discovers an anomaly in last week's revenue report. They can query the exact state of the data from that time period using snapshot IDs or timestamps, even though the underlying data has been updated multiple times since then.

**Compaction and Maintenance**: As your table accumulates many small files from frequent updates, Iceberg can compact them into larger, more efficient files in the background. It updates the metadata to point to the new consolidated files and marks old files for deletion, but queries continue working seamlessly throughout this process.

This architecture enables reliable, scalable data management that supports both analytical workloads requiring historical consistency and operational needs for real-time updates.

---
## Iceberg As a Standalone System
Let me break down how Apache Iceberg works as a standalone system and how its metadata/system tables function:

## Apache Iceberg Can Be Standalone

**Yes, Apache Iceberg can operate as a standalone table format**, but it requires a catalog service to manage metadata. Iceberg is a technical catalog or metastore that plays an important role in tracking tables and their metadata. At a minimum, a catalog is the source of truth for a table's current metadata location.

### Documentation
- [Hive and Iceberg Quickstart](https://iceberg.apache.org/hive-quickstart/)
- [Iceberg Catalog Guide - Medium](https://medium.com/itversity/iceberg-catalogs-a-guide-for-data-engineers-a6190c7bf381)

## Iceberg Architecture Components

Apache Iceberg supports various catalog implementations to manage table metadata: Hive Metastore, Hadoop Catalog, AWS Glue Data Catalog, JDBC Catalog, and REST Catalog. You can even run a standalone Hive metastore service backed by MySQL to manage Iceberg tables.

## Iceberg's Built-in "System Tables"

**Iceberg comes with its own metadata tables** that function similarly to system tables, but they're **built into the table format itself** rather than being separate system tables in a traditional sense:

### Core Metadata Tables

Apache Iceberg exposes metadata as structured, queryable tables called metadata tables, including:

- **`table.snapshots`** - Known versions of the table with summary metadata
- **`table.manifests`** - Manifest files in the current snapshot tracking data and delete files  
- **`table.files`** - All data files with details like partition values, record counts, file sizes
- **`table.all_data_files`** - Detailed insights into every data file across all valid snapshots
- **`table.partitions`** - Partition-level information including record counts and file statistics
- **`table.history`** - Table metadata history and operations

### How to Query Them

To query a metadata table in Apache Spark, add the metadata table name as another part in the table identifier. For example: `SELECT snapshot_id, committed_at, operation FROM examples.nyc_taxi_yellow.snapshots`

## Integration vs. Standalone

### Standalone Deployment
Table state is maintained in metadata files. All changes to table state create a new metadata file and replace the old metadata with an atomic swap. The table metadata file tracks the table schema, partitioning config, custom properties, and snapshots.

### Integration with External Systems
When Iceberg integrates with external systems like Unity Catalog, it doesn't create new system tables but rather the existing system tables (like lineage and audit tables) accommodate all table formats including Iceberg.

## Key Takeaway

**Iceberg's metadata system is self-contained and format-native**. Unlike Hive or traditional file-based formats where gaining visibility into schema, partitioning, and file layout often depends on engine-specific logic or limited tooling, Iceberg exposes this information as structured, queryable metadata tables.

So while Iceberg can be standalone, it always needs some form of catalog service (even if just a simple file-based Hadoop catalog) to track the current metadata file locations. The "system tables" are actually built into each Iceberg table as queryable metadata views, making them portable across any catalog implementation.
