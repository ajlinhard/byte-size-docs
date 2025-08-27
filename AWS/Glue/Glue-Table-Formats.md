# Glue Table Formats
AWS Glue supports many different table formats for working with and building out data lakes. The stopped there support of governed tables to align with more widely used open-source table formats like Iceberg, Delta Lake, and Hudi at the end of 2024.

### Documentation
- [AWS Ending Governed Table Support - Blog Post]()



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
