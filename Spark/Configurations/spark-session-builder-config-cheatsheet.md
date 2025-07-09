# Spark Session Builder Config Cheatsheet
Below is a comprehensive cheatsheet of Spark session builder configuration options organized into logical categories. The table includes the configuration key, its purpose, and example values for each setting.

The cheatsheet covers:

- **Application Settings** - Basic app configuration
- **Driver & Executor Configuration** - Resource allocation
- **Dynamic Allocation** - Auto-scaling settings
- **Serialization** - Object serialization options
- **Shuffle Configuration** - Data shuffle optimization
- **Storage Configuration** - Memory and storage settings
- **Network Configuration** - Timeout and connection settings
- **SQL Configuration** - Spark SQL and adaptive query execution
- **Hive Configuration** - Hive metastore integration
- **Checkpointing** - Fault tolerance settings
- **Logging Configuration** - Event logging and history
- **Security Configuration** - Authentication and SSL
- **Resource Management** - Kubernetes and YARN settings
- **Advanced Configuration** - Additional JARs, files, and worker settings
- **Monitoring and Metrics** - UI and metrics configuration

I've also included three common configuration examples at the end for different use cases: local development, production cluster with Hive, and streaming applications. This should give you a solid reference for configuring Spark sessions for various scenarios.

---
# Spark Session Builder Configuration Options Cheatsheet

| Key | Purpose | Example Values |
|-----|---------|----------------|
| **Application Settings** | | |
| `spark.app.name` | Sets the application name shown in Spark UI | `"MySparkApp"`, `"ETL Pipeline"` |
| `spark.app.id` | Unique identifier for the application | `"app-20231201-1234"` |
| | | |
| **Driver Configuration** | | |
| `spark.driver.memory` | Memory allocated to the driver process | `"2g"`, `"4g"`, `"8g"` |
| `spark.driver.cores` | Number of cores allocated to driver | `"1"`, `"2"`, `"4"` |
| `spark.driver.maxResultSize` | Maximum size of results collected to driver | `"1g"`, `"2g"`, `"0"` (unlimited) |
| `spark.driver.host` | Hostname or IP address for the driver | `"localhost"`, `"192.168.1.100"` |
| `spark.driver.port` | Port for the driver to listen on | `"7077"`, `"4040"` |
| | | |
| **Executor Configuration** | | |
| `spark.executor.memory` | Memory allocated per executor | `"2g"`, `"4g"`, `"8g"` |
| `spark.executor.cores` | Number of cores per executor | `"2"`, `"4"`, `"8"` |
| `spark.executor.instances` | Number of executor instances | `"2"`, `"10"`, `"50"` |
| `spark.executor.memoryFraction` | Fraction of executor memory for caching | `"0.6"`, `"0.8"` |
| `spark.executor.heartbeatInterval` | Interval for executor heartbeats | `"10s"`, `"30s"` |
| `spark.executor.logs.rolling.strategy` | Rolling strategy for executor logs | `"time"`, `"size"` |
| | | |
| **Dynamic Allocation** | | |
| `spark.dynamicAllocation.enabled` | Enable dynamic allocation of executors | `"true"`, `"false"` |
| `spark.dynamicAllocation.minExecutors` | Minimum number of executors | `"1"`, `"2"`, `"5"` |
| `spark.dynamicAllocation.maxExecutors` | Maximum number of executors | `"10"`, `"50"`, `"100"` |
| `spark.dynamicAllocation.initialExecutors` | Initial number of executors | `"2"`, `"5"`, `"10"` |
| `spark.dynamicAllocation.executorIdleTimeout` | Timeout for idle executors | `"60s"`, `"300s"` |
| | | |
| **Serialization** | | |
| `spark.serializer` | Serializer class for objects | `"org.apache.spark.serializer.KryoSerializer"` |
| `spark.serializer.objectStreamReset` | Reset object stream periodically | `"100"`, `"10000"` |
| `spark.kryoserializer.buffer.max` | Maximum Kryo serialization buffer size | `"64m"`, `"128m"`, `"256m"` |
| | | |
| **Shuffle Configuration** | | |
| `spark.shuffle.service.enabled` | Enable external shuffle service | `"true"`, `"false"` |
| `spark.shuffle.service.port` | Port for external shuffle service | `"7337"`, `"7338"` |
| `spark.shuffle.compress` | Compress shuffle output | `"true"`, `"false"` |
| `spark.shuffle.spill.compress` | Compress spilled data during shuffle | `"true"`, `"false"` |
| `spark.shuffle.file.buffer` | Buffer size for shuffle files | `"32k"`, `"64k"`, `"128k"` |
| | | |
| **Storage Configuration** | | |
| `spark.storage.memoryFraction` | Fraction of memory for RDD storage | `"0.6"`, `"0.8"` |
| `spark.storage.unrollFraction` | Fraction of memory for unrolling blocks | `"0.2"`, `"0.3"` |
| `spark.storage.blockManagerHeartBeatMs` | Block manager heartbeat interval | `"10000"`, `"30000"` |
| | | |
| **Network Configuration** | | |
| `spark.network.timeout` | Default network timeout | `"120s"`, `"300s"` |
| `spark.rpc.askTimeout` | Timeout for RPC ask operations | `"120s"`, `"300s"` |
| `spark.rpc.lookupTimeout` | Timeout for RPC lookup operations | `"120s"`, `"300s"` |
| `spark.port.maxRetries` | Maximum retries for port binding | `"16"`, `"100"` |
| | | |
| **SQL Configuration** | | |
| `spark.sql.adaptive.enabled` | Enable adaptive query execution | `"true"`, `"false"` |
| `spark.sql.adaptive.coalescePartitions.enabled` | Enable partition coalescing | `"true"`, `"false"` |
| `spark.sql.adaptive.skewJoin.enabled` | Enable skew join optimization | `"true"`, `"false"` |
| `spark.sql.warehouse.dir` | Default warehouse directory | `"/user/hive/warehouse"`, `"s3a://bucket/warehouse"` |
| `spark.sql.hive.metastore.version` | Hive metastore version | `"2.3.7"`, `"3.1.2"` |
| `spark.sql.hive.metastore.jars` | Hive metastore JARs | `"builtin"`, `"maven"`, `"path"` |
| `spark.sql.catalogImplementation` | Catalog implementation | `"hive"`, `"in-memory"` |
| `spark.sql.execution.arrow.pyspark.enabled` | Enable Arrow-based columnar data transfers | `"true"`, `"false"` |
| | | |
| **Hive Configuration** | | |
| `hive.metastore.uris` | Hive metastore URI | `"thrift://localhost:9083"`, `"thrift://metastore:9083"` |
| `hive.metastore.warehouse.dir` | Hive warehouse directory | `"/user/hive/warehouse"`, `"s3a://bucket/warehouse"` |
| `hive.exec.dynamic.partition` | Enable dynamic partitioning | `"true"`, `"false"` |
| `hive.exec.dynamic.partition.mode` | Dynamic partition mode | `"nonstrict"`, `"strict"` |
| `hive.exec.max.dynamic.partitions` | Maximum dynamic partitions | `"1000"`, `"5000"` |
| | | |
| **Checkpointing** | | |
| `spark.sql.streaming.checkpointLocation` | Checkpoint location for streaming | `"/tmp/checkpoints"`, `"s3a://bucket/checkpoints"` |
| `spark.sql.recovery.checkpointDir` | Directory for SQL recovery checkpoints | `"/tmp/recovery"`, `"hdfs://namenode/recovery"` |
| | | |
| **Logging Configuration** | | |
| `spark.eventLog.enabled` | Enable event logging | `"true"`, `"false"` |
| `spark.eventLog.dir` | Directory for event logs | `"/tmp/spark-events"`, `"hdfs://namenode/spark-logs"` |
| `spark.eventLog.compress` | Compress event logs | `"true"`, `"false"` |
| `spark.history.fs.logDirectory` | History server log directory | `"/tmp/spark-events"`, `"s3a://bucket/spark-logs"` |
| | | |
| **Security Configuration** | | |
| `spark.authenticate` | Enable authentication | `"true"`, `"false"` |
| `spark.authenticate.secret` | Authentication secret | `"my-secret-key"` |
| `spark.ssl.enabled` | Enable SSL | `"true"`, `"false"` |
| `spark.ssl.keyStore` | SSL keystore path | `"/path/to/keystore.jks"` |
| `spark.ssl.keyStorePassword` | SSL keystore password | `"password123"` |
| | | |
| **Resource Management** | | |
| `spark.kubernetes.namespace` | Kubernetes namespace | `"default"`, `"spark-jobs"` |
| `spark.kubernetes.container.image` | Container image for Kubernetes | `"spark:3.4.0"`, `"my-registry/spark:latest"` |
| `spark.yarn.queue` | YARN queue name | `"default"`, `"production"` |
| `spark.yarn.am.memory` | YARN Application Master memory | `"512m"`, `"1g"` |
| `spark.yarn.am.cores` | YARN Application Master cores | `"1"`, `"2"` |
| | | |
| **Advanced Configuration** | | |
| `spark.jars` | Additional JARs to include | `"/path/to/jar1.jar,/path/to/jar2.jar"` |
| `spark.jars.packages` | Maven packages to include | `"org.apache.spark:spark-avro_2.12:3.4.0"` |
| `spark.files` | Additional files to include | `"/path/to/file1.txt,/path/to/file2.conf"` |
| `spark.python.worker.reuse` | Reuse Python worker processes | `"true"`, `"false"` |
| `spark.python.worker.memory` | Memory for Python worker processes | `"512m"`, `"1g"` |
| `spark.task.maxFailures` | Maximum task failures before job fails | `"1"`, `"3"`, `"5"` |
| `spark.stage.maxConsecutiveAttempts` | Maximum consecutive stage attempts | `"4"`, `"8"` |
| | | |
| **Monitoring and Metrics** | | |
| `spark.ui.enabled` | Enable Spark web UI | `"true"`, `"false"` |
| `spark.ui.port` | Port for Spark web UI | `"4040"`, `"8080"` |
| `spark.ui.killEnabled` | Enable killing jobs from UI | `"true"`, `"false"` |
| `spark.metrics.conf` | Metrics configuration file | `"/path/to/metrics.properties"` |
| `spark.sql.ui.explainMode` | Explain mode for SQL UI | `"simple"`, `"extended"`, `"formatted"` |

## Common Configuration Examples

### Basic Local Development
```python
spark = SparkSession.builder \
    .appName("Local Development") \
    .config("spark.driver.memory", "4g") \
    .config("spark.executor.memory", "2g") \
    .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer") \
    .getOrCreate()
```

### Production Cluster with Hive
```python
spark = SparkSession.builder \
    .appName("Production ETL") \
    .enableHiveSupport() \
    .config("spark.executor.instances", "20") \
    .config("spark.executor.memory", "8g") \
    .config("spark.executor.cores", "4") \
    .config("spark.driver.memory", "4g") \
    .config("spark.sql.adaptive.enabled", "true") \
    .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
    .config("hive.metastore.uris", "thrift://metastore:9083") \
    .config("spark.eventLog.enabled", "true") \
    .config("spark.eventLog.dir", "/tmp/spark-events") \
    .getOrCreate()
```

### Streaming Application
```python
spark = SparkSession.builder \
    .appName("Streaming Job") \
    .config("spark.streaming.backpressure.enabled", "true") \
    .config("spark.sql.streaming.checkpointLocation", "/tmp/checkpoints") \
    .config("spark.sql.adaptive.enabled", "true") \
    .config("spark.dynamicAllocation.enabled", "false") \
    .getOrCreate()
```
