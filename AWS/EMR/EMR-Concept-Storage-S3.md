# EMR Concept: Storage on S3
The storage of a data lake or large data processing with EMR clusters are commonly stored on S3 for the EMRFS (EMR File System). This is counter to what a lot of developers might think since S3 is slower on read and write than block storage commonly used for HDFS. S3 is oddly optimized for how most large Spark or EMR worklods operate. So we are talking most about OLAP, DDS, and ML moderate and large data processing, not OLTP or real-time data.<br>
<br>
**Also, below is info about how AWS Glue + S3 integrate well with EMR + S3 [(jump to section)](#AWS-Glue-and-EMR)**

## Why S3 works well with EMR
Amazon EMR moved to using EMRFS (EMR File System) with S3 as the default storage layer instead of HDFS for several compelling technical and operational reasons, particularly beneficial for Spark workloads:

**Decoupling Storage from Compute:**
The fundamental shift was moving from tightly coupled storage-compute clusters (HDFS) to a decoupled architecture. With HDFS, you needed to keep clusters running to maintain data availability, even when not processing. EMRFS allows you to spin up clusters on-demand, process data stored persistently in S3, then terminate clusters - dramatically reducing costs.

**Cost Economics:**
S3 storage costs significantly less than keeping HDFS clusters running 24/7. For Spark jobs that don't run continuously, paying for persistent compute just to maintain data storage became economically inefficient. S3 provides durable storage at a fraction of the cost.

**Elasticity and Auto-scaling:**
Spark workloads often have variable resource requirements. With EMRFS/S3, you can launch clusters with exactly the compute resources needed for each job, then scale down or terminate. HDFS required maintaining minimum cluster sizes for data replication, limiting elasticity.

**Fault Tolerance and Durability:**
S3 provides 11 9's of durability through automatic replication across availability zones. HDFS required manual management of replication factors and dealing with node failures. For Spark applications, this means less operational overhead and better reliability.

**Multi-cluster Access:**
Multiple EMR clusters can simultaneously read from the same S3 datasets, enabling better resource utilization and parallel processing scenarios that would be complex with HDFS.

**Spark-Specific Benefits:**
Spark's architecture actually works well with S3's eventual consistency model (now strong consistency). Spark's lazy evaluation and immutable RDDs align with S3's object storage paradigm. The Spark catalyst optimizer can also push down predicates effectively when reading Parquet files from S3.

The trade-off is network latency - S3 access is slower than local HDFS reads. However, for most analytical workloads, the cost savings and operational simplicity outweigh the performance impact, especially when using columnar formats like Parquet that minimize data transfer.

## S3 Eventual Consistency and Spark Lazy Evaluation
Let me break down how Spark's architectural characteristics align perfectly with S3's object storage model:

**Spark's Lazy Evaluation and S3 Object Immutability**

Spark uses lazy evaluation, meaning transformations aren't executed immediately when called - they're just recorded as a lineage graph until an action triggers computation. This pairs beautifully with S3's immutable objects. When Spark reads a file from S3, it knows that object won't change during the computation lifecycle. The lazy evaluation means Spark can safely plan the entire computation graph knowing the input data is stable.

For example, when you do:
```scala
val df = spark.read.parquet("s3://bucket/data/")
val filtered = df.filter(col("status") === "active")
val result = filtered.groupBy("category").count()
```

Nothing actually reads from S3 until you call an action like `result.collect()`. By that time, Spark has optimized the entire plan and knows exactly what data it needs, reading only the required Parquet files/partitions.

**Immutable RDDs and Object Storage Philosophy**

RDDs (Resilient Distributed Datasets) are immutable by design - once created, they can't be modified, only transformed into new RDDs. This immutability model mirrors S3's object storage where objects are written once and read many times. 

In HDFS, you might append to files or modify them in place, but with S3, you write complete objects. Spark's functional programming model naturally aligns with this - instead of mutating data structures, you create new ones through transformations.

**How Eventual Consistency Worked (Historical Context)**

Before S3 achieved strong consistency in December 2020, it had eventual consistency for overwrites and deletes. Spark's architecture actually handled this well because:

1. **Read-after-write consistency**: New objects were immediately readable, which worked fine for Spark jobs writing output files
2. **Lineage-based recovery**: If Spark encountered inconsistent reads (rare), it could recompute from the lineage graph rather than relying on immediately consistent file states
3. **Partitioned output**: Spark typically writes many small files in parallel rather than overwriting single large files, minimizing eventual consistency issues

**Strong Consistency Benefits (Current State)**

Now that S3 has strong consistency, Spark gains additional benefits:

- **Immediate read-after-write**: Output files are immediately visible to subsequent stages
- **Reliable metadata operations**: Operations like `spark.sql("MSCK REPAIR TABLE")` work reliably with partitioned tables stored in S3
- **Better support for streaming**: Spark Structured Streaming can more reliably track processed files

**Practical Example**

Consider a typical Spark ETL pipeline:
```scala
// Read raw data (S3 objects are immutable - safe for lazy evaluation)
val rawData = spark.read.parquet("s3://raw-bucket/events/")

// Transform (creates new RDD lineage, doesn't modify S3 objects)
val cleaned = rawData.filter($"timestamp" > yesterday)
                    .withColumn("processed_date", current_date())

// Write (creates new immutable objects in S3)
cleaned.write.partitionBy("date")
       .parquet("s3://processed-bucket/clean-events/")
```

The immutable nature of both RDDs and S3 objects means Spark never needs to worry about data changing underneath it during computation, and the lazy evaluation ensures efficient access patterns that work well with S3's network-based storage model.

---
# AWS Glue and EMR
The automatic access between EMR Spark clusters and AWS Glue works through several integrated mechanisms that go beyond just S3 bucket access:

**Built-in Glue Integration in EMR**

EMR clusters come pre-configured with AWS Glue integration enabled by default. When you launch an EMR cluster, it automatically includes:
- Glue libraries and connectors
- Pre-configured Hive metastore that can read from Glue Catalog
- Spark SQL engine configured to use Glue as the default catalog

This isn't just about S3 access - it's about metadata discovery and schema management.

**How the Glue Catalog Integration Works**

The Glue Data Catalog acts as a centralized Hive-compatible metastore. When your Spark application runs queries like:
```sql
SELECT * FROM my_database.my_table
```

Here's what happens behind the scenes:

1. **Metadata Lookup**: Spark contacts the Glue Catalog API to get table metadata (schema, partition info, S3 location)
2. **Path Resolution**: Glue returns the S3 paths where the actual data files are stored
3. **Schema Application**: Spark uses the schema information from Glue to properly read and parse the data files
4. **Partition Pruning**: For partitioned tables, Glue provides partition locations for query optimization

**IAM Roles and Permissions**

The EMR cluster's EC2 instances run with an IAM role (EMR_EC2_DefaultRole by default) that includes permissions to:
- Access Glue Catalog APIs (`glue:GetDatabase`, `glue:GetTable`, `glue:GetPartitions`, etc.)
- Read from S3 buckets where the data is stored
- Access other AWS services as needed

**Beyond Just S3 Bucket Attachment**

While S3 access is necessary, the Glue integration provides much more:

**Schema Evolution**: Glue tracks schema changes over time, allowing Spark to handle evolving data structures gracefully.

**Partition Management**: For large datasets partitioned by date/region/etc., Glue maintains partition metadata so Spark can efficiently query only relevant partitions:
```sql
SELECT * FROM sales_data 
WHERE year = '2024' AND month = '06'
-- Spark only reads files in s3://bucket/sales/year=2024/month=06/
```

**Cross-Service Compatibility**: Tables cataloged in Glue can be accessed by multiple services (EMR, Athena, Redshift Spectrum, SageMaker) with consistent schemas.

**Practical Example**

Consider this workflow:
1. AWS Glue Crawler scans S3 bucket `s3://data-lake/customer-events/` and discovers Parquet files
2. Crawler creates table `events.customer_activity` in Glue Catalog with schema and partition information
3. EMR Spark cluster can immediately query this table:

```python
df = spark.sql("SELECT * FROM events.customer_activity WHERE date >= '2024-01-01'")
```

Spark automatically:
- Contacts Glue to get table metadata
- Discovers the table points to S3 locations
- Reads only the relevant partition files
- Applies the correct schema from Glue

**Configuration Details**

EMR enables this through configuration properties like:
```
spark.sql.catalogImplementation=hive
javax.jdo.option.ConnectionURL=jdbc:mysql://glue-catalog-endpoint
```

The key insight is that Glue Catalog serves as the "phone book" - it tells Spark where to find data and how to interpret it, while the actual data access still goes through S3. This separation of metadata management from data storage is what makes the modern data lake architecture so powerful and flexible.
