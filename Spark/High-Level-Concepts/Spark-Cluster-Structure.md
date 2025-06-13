# Spark Cluster Structure
Whether your spark cluster is setup locally on your machine, in an on-premises server farm, or the cloud via EMR or Containers. There is plenty to understand about how the distributed infrastructure of Spark works.

### Basic Setups
- [Local Build](https://github.com/ajlinhard/byte-size-docs/blob/main/Spark/High-Level-Concepts/Spark-Setup-Local.md)
- [Cloud Builds (AWS)](https://catalog.us-east-1.prod.workshops.aws/workshops/c86bd131-f6bf-4e8f-b798-58fd450d3c44/en-US)
  - Note: Cloud9 has be discontinued, so use AWS CLI and [AWS IDE Tool Kits]([https://aws.amazon.com/visualstudiocode/](https://aws.amazon.com/developer/tools/#IDE_and_IDE_Toolkits) to access infrastructure

---
# Cluster Managers
When running Spark locally, the base resource negotiator (also known as the cluster manager) is the **Standalone mode** or more specifically, the **local mode**.

## Local Mode (Default for Local Execution)

In local mode, Spark runs in a single JVM process and doesn't need an external cluster manager. You specify local mode with configurations like:
- `local` - runs with 1 thread
- `local[*]` - runs with as many threads as logical cores
- `local[n]` - runs with n threads

```python
spark = SparkSession.builder \
    .appName("Local App") \
    .master("local[*]") \
    .getOrCreate()
```

## Other Cluster Manager Options

Spark supports several other cluster managers beyond local mode:

### 1. **Spark Standalone**
Spark's own built-in cluster manager for dedicated Spark clusters.
```python
.master("spark://master-host:7077")
```

### 2. **Apache Mesos**
A general-purpose cluster manager that can run Spark alongside other frameworks.
```python
.master("mesos://mesos-master:5050")
```

### 3. **Hadoop YARN**
Hadoop's resource manager, commonly used in Hadoop ecosystems.
```python
.master("yarn")
```

### 4. **Kubernetes**
For containerized Spark applications.
```python
.master("k8s://https://kubernetes-api-server:443")
```

### 5. **Local Cluster Mode**
Simulates a cluster on a single machine (useful for testing cluster behavior locally).
```python
.master("local-cluster[2,1,1024]")  # 2 workers, 1 core each, 1GB memory each
```

For truly local development and testing, most developers use `local[*]` which automatically uses all available CPU cores on the machine.


---
# Storage

## Strogage On-Cloud (HDFS vs S3)
Amazon EMR moved to using EMRFS (EMR File System) with S3 as the default storage layer instead of HDFS for several compelling technical and operational reasons, particularly beneficial for Spark workloads:

**Decoupling Storage from Compute**
The fundamental shift was moving from tightly coupled storage-compute clusters (HDFS) to a decoupled architecture. With HDFS, you needed to keep clusters running to maintain data availability, even when not processing. EMRFS allows you to spin up clusters on-demand, process data stored persistently in S3, then terminate clusters - dramatically reducing costs.

**Cost Economics**
S3 storage costs significantly less than keeping HDFS clusters running 24/7. For Spark jobs that don't run continuously, paying for persistent compute just to maintain data storage became economically inefficient. S3 provides durable storage at a fraction of the cost.

**Elasticity and Auto-scaling**
Spark workloads often have variable resource requirements. With EMRFS/S3, you can launch clusters with exactly the compute resources needed for each job, then scale down or terminate. HDFS required maintaining minimum cluster sizes for data replication, limiting elasticity.

**Fault Tolerance and Durability**
S3 provides 11 9's of durability through automatic replication across availability zones. HDFS required manual management of replication factors and dealing with node failures. For Spark applications, this means less operational overhead and better reliability.

**Multi-cluster Access**
Multiple EMR clusters can simultaneously read from the same S3 datasets, enabling better resource utilization and parallel processing scenarios that would be complex with HDFS.

**Spark-Specific Benefits**
Spark's architecture actually works well with S3's eventual consistency model (now strong consistency). Spark's lazy evaluation and immutable RDDs align with S3's object storage paradigm. The Spark catalyst optimizer can also push down predicates effectively when reading Parquet files from S3.

The trade-off is network latency - S3 access is slower than local HDFS reads. However, for most analytical workloads, the cost savings and operational simplicity outweigh the performance impact, especially when using columnar formats like Parquet that minimize data transfer.
