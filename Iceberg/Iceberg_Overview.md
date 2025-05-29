# Iceberg Overview:
Apache Iceberg is a rich metadata system that sits between your query engines and your data. It is capable of handling interactions between Hive, Spark, and MapReduce then interact with different storage types S3, HDFS, etc.
Additionally, Iceberg has metadata on its metadata overtime allowing for new features like schema evolution, partition evolution, data time travel, and more.

## Documentation/Tutorials:
1. [Apache Iceberg Official Page](https://iceberg.apache.org/)
2. [What is Iceberg? The Evolution of Data Management](https://www.youtube.com/watch?v=6tjSVXpHrE8&t=4s)

Iceberg is a table format designed to handle massive datasets in data lakes. Think of it as a smart filing system that keeps track of where your data lives and what it looks like, even as you constantly add, modify, or delete information.

## The Basic Concept

Traditional data storage is like having files scattered across many folders with no central index. Iceberg creates a detailed catalog that tracks every piece of data, its location, and its structure. This catalog gets updated atomically - meaning changes either complete entirely or don't happen at all, preventing corruption.

## Core Components

**Metadata Layer**: Iceberg maintains three levels of metadata files. The catalog points to metadata files, which point to manifest files, which finally point to your actual data files. This hierarchy allows efficient tracking of changes without scanning entire datasets.

**Schema Evolution**: You can safely add, remove, or modify columns without rewriting existing data. Iceberg handles the mapping between old and new schemas automatically.

**Time Travel**: Every change creates a new snapshot while preserving previous versions. You can query your data as it existed at any point in time.

## Detailed Example: E-commerce Analytics

Imagine you're managing customer transaction data for a large e-commerce platform. Your table starts with columns like customer_id, product_id, purchase_amount, and timestamp.

**Initial Setup**: When you create your Iceberg table, it generates a metadata file containing the schema definition and points to manifest files. These manifest files catalog your actual parquet data files stored in S3 or similar storage.

**Daily Operations**: Each night, you ingest new transaction data. Instead of appending to existing files, Iceberg writes new data files and updates the manifest files to include them. The metadata file gets updated to point to the new manifest version. This happens atomically - other users either see the complete update or the previous version, never a partial state.

**Schema Changes**: Three months later, you need to add a "discount_applied" column. With traditional systems, you'd need to rewrite terabytes of historical data. Iceberg simply updates the schema in the metadata layer. When querying old data, it automatically provides null values for the new column. New data includes the actual discount values.

**Time Travel Queries**: Your data science team discovers an anomaly in last week's revenue report. They can query the exact state of the data from that time period using snapshot IDs or timestamps, even though the underlying data has been updated multiple times since then.

**Compaction and Maintenance**: As your table accumulates many small files from frequent updates, Iceberg can compact them into larger, more efficient files in the background. It updates the metadata to point to the new consolidated files and marks old files for deletion, but queries continue working seamlessly throughout this process.

This architecture enables reliable, scalable data management that supports both analytical workloads requiring historical consistency and operational needs for real-time updates.
