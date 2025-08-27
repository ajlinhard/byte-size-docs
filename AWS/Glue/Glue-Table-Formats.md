# Glue Table Formats
AWS Glue supports many different table formats for working with and building out data lakes. The stopped there support of governed tables to align with more widely used open-source table formats like Iceberg, Delta Lake, and Hudi at the end of 2024.

### Documentation
- [AWS Ending Governed Table Support - Blog Post]()

### Table of Contents
- [Delta Lake Support](#Delta-Lake-Support)
- [Governed Tables (noe deprecated)(#Governed-Tables)

---
# Delta Lake Support
Yes, AWS Glue **does support Delta Lake format**! Here's what you need to know:

## **Native Support Since Glue 3.0**

AWS Glue 3.0 and later supports the Linux Foundation Delta Lake framework. This includes:

- **ACID transactions** for data consistency
- **Scalable metadata handling**
- **Unified streaming and batch data processing**
- **Read and write operations** on Delta Lake tables in Amazon S3

## **Supported Delta Lake Versions**

The following table lists the version of Delta Lake included in each AWS Glue version:

| AWS Glue Version | Delta Lake Version |
|-----------------|-------------------|
| Glue 3.0 | Delta Lake 1.2.1 |
| Glue 4.0 | Delta Lake 2.3.0 |
| Glue 5.0 | Delta Lake 3.0+ |

## **How to Enable Delta Lake in Glue**

**Job Configuration:**
Specify delta as a value for the --datalake-formats job parameter

**Required Spark Configuration:**
```
--conf spark.sql.extensions=io.delta.sql.DeltaSparkSessionExtension
--conf spark.sql.catalog.spark_catalog=org.apache.spark.sql.delta.catalog.DeltaCatalog  
--conf spark.delta.logStore.class=org.apache.spark.sql.delta.storage.S3SingleDriverLogStore
```

## **Supported Operations**

When you use Delta Lake tables, you also have the option to use methods from the Delta Lake Python library such as DeltaTable.forPath. This includes:

- **Table batch reads and writes**
- **Insert, update, and delete operations**
- **UPSERT operations** for change data capture (CDC)
- **Time travel queries**

## **Integration with AWS Services**

**Data Catalog Integration:**
- AWS Glue includes Delta crawler, a capability that makes discovering datasets simpler by scanning Delta Lake transaction logs in Amazon S3
- Native Delta Lake tables are accessible from Amazon Athena (engine version 3), AWS Glue for Apache Spark (Glue version 3.0 and later), Amazon EMR (release version 6.9.0 and later)

**Lake Formation Support:**
Lake Formation permission support for Delta tables is enabled by default for AWS Glue 4.0

## **Example Code**

Here's how to write Delta Lake tables in Glue:

```python
# Write a Delta Lake table to S3 and register in Glue Data Catalog
additional_options = {"path": "s3://<s3Path>"}

dataFrame.write \
    .format("delta") \
    .options(**additional_options) \
    .mode("append") \
    .partitionBy("<your_partitionkey_field>") \
    .saveAsTable("<your_database_name>.<your_table_name>")
```

## **Recent AWS Investment in Delta Lake**

AWS has enhanced support for these formats across various analytics services, including Amazon Athena, Amazon EMR, AWS Glue, and Amazon Redshift, and AWS made the decision to end support for Governed Tables, effective December 31, 2024, to focus on open source transactional table formats such as Apache Iceberg, Apache Hudi, and Linux Foundation Delta Lake.

So yes, AWS Glue has robust, native support for Delta Lake, making it a viable alternative to the Iceberg approach in your pipeline if you're working primarily within the AWS ecosystem!

---
# Governed Tables
AWS Glue Governed Tables was a now-deprecated AWS service that provided ACID transaction capabilities for data lakes before open-source table formats became mature. Here's what they were:

## **What Governed Tables Were**

**ACID Transactions for Data Lakes**: Governed Tables were AWS's proprietary solution to bring database-like ACID (Atomicity, Consistency, Isolation, Durability) transactions to data stored in Amazon S3. They allowed you to perform reliable updates, deletes, and inserts on data lake tables.

**Key Features**:
- **Transactional consistency** - Updates either completed fully or not at all
- **Concurrent access control** - Multiple users could safely read/write simultaneously  
- **Time travel** - Query historical versions of data
- **Schema evolution** - Add/modify columns without breaking existing queries
- **Automatic compaction** - Background optimization of data files

## **How They Worked**

Governed Tables used AWS Lake Formation as the transaction coordinator and metadata manager. When you performed operations:

1. **Transaction Management**: Lake Formation tracked all changes in a transaction log
2. **Metadata Handling**: Schema and partition information was managed centrally
3. **File Organization**: AWS automatically organized and optimized the underlying Parquet files
4. **Access Control**: Fine-grained permissions through Lake Formation's security model

## **Why AWS Deprecated Them**

After careful consideration, we have made the decision to end support for Governed Tables, effective December 31, 2024, to focus on open source transactional table formats such as Apache Iceberg, Apache Hudi, and Linux Foundation Delta Lake. This decision stems from customer preference for these open source solutions.

**Customer Preference for Open Standards**: Organizations preferred vendor-neutral, open-source solutions over AWS's proprietary format to avoid lock-in.

**Feature Parity**: Open source solutions, which offer ACID-compliant transactions, compaction, time travel, and other features previously provided by Governed Tables, became mature enough to replace the proprietary solution.

**Ecosystem Adoption**: The industry converged around Apache Iceberg, Delta Lake, and Apache Hudi as standard table formats.

## **Migration Path**

AWS now recommends using:
- **Apache Iceberg** for vendor-neutral, multi-engine compatibility
- **Delta Lake** for Spark-heavy workloads and Databricks integration  
- **Apache Hudi** for streaming and incremental data processing

**Enhanced AWS Support**: Amazon Web Services (AWS) has enhanced our support for these formats across various analytics services, including Amazon Athena, Amazon EMR, AWS Glue, and Amazon Redshift.

## **What This Means for Your Pipeline**

Since Governed Tables are now deprecated, your choice of using Apache Iceberg in your Firehose pipeline was prescient! You're already using the modern, open-source approach that AWS now officially recommends.

The deprecation of Governed Tables actually validates the industry trend toward open table formats like Iceberg and Delta Lake, rather than proprietary solutions. AWS essentially admitted that customers prefer the flexibility and ecosystem compatibility of open standards over vendor-specific implementations.
