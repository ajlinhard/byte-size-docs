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

## Overview
This cheat sheet covers all configuration options that can be used with `SparkSession.builder.config()`. These properties control various aspects of Spark application behavior including memory management, execution, networking, and more.

## Usage
```python
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("MyApp") \
    .config("spark.executor.memory", "4g") \
    .config("spark.sql.adaptive.enabled", "true") \
    .getOrCreate()
```

---

## Application Properties

| Key | Purpose | Example Values | Default Value |
|-----|---------|---------------|---------------|
| `spark.app.name` | Application name displayed in UI and logs | `"MySparkApp"`, `"ETL Pipeline"` | no default |
| `spark.master` | Cluster manager to connect to | `"local[*]"`, `"yarn"`, `"spark://host:7077"` | no default |
| `spark.submit.deployMode` | Deploy mode for driver | `"client"`, `"cluster"` | `"client"` |
| `spark.driver.cores` | Number of cores for driver (cluster mode only) | `1`, `2`, `4` | `1` |
| `spark.driver.memory` | Memory for driver process | `"1g"`, `"2g"`, `"512m"` | `"1g"` |
| `spark.driver.memoryOverhead` | Non-heap memory for driver | `"384m"`, `"1g"` | `driverMemory * 0.10, min 384` |
| `spark.executor.memory` | Memory per executor process | `"1g"`, `"4g"`, `"8g"` | `"1g"` |
| `spark.executor.cores` | Number of cores per executor | `1`, `2`, `4`, `8` | `1` in YARN, all available in standalone` |
| `spark.executor.instances` | Number of executor instances | `2`, `10`, `50` | no default |
| `spark.executor.memoryOverhead` | Non-heap memory per executor | `"384m"`, `"1g"` | `executorMemory * 0.10, min 384` |
| `spark.default.parallelism` | Default number of partitions for RDDs | `100`, `200`, `1000` | depends on cluster manager |
| `spark.sql.shuffle.partitions` | Default partitions for shuffles | `200`, `400`, `800` | `200` |

---

## Memory Management

| Key | Purpose | Example Values | Default Value |
|-----|---------|---------------|---------------|
| `spark.memory.fraction` | Fraction of heap for execution and storage | `0.6`, `0.7`, `0.8` | `0.6` |
| `spark.memory.storageFraction` | Fraction of memory.fraction for storage | `0.5`, `0.3`, `0.7` | `0.5` |
| `spark.memory.offHeap.enabled` | Enable off-heap memory | `true`, `false` | `false` |
| `spark.memory.offHeap.size` | Size of off-heap memory | `"1g"`, `"2g"`, `"4g"` | `0` |
| `spark.executor.pyspark.memory` | Memory limit for PySpark per executor | `"1g"`, `"2g"` | no default |
| `spark.python.worker.memory` | Memory for Python worker processes | `"512m"`, `"1g"` | `"512m"` |
| `spark.storage.memoryMapThreshold` | Threshold for memory mapping | `"2m"`, `"4m"`, `"8m"` | `"2m"` |
| `spark.cleaner.periodicGC.interval` | Interval for periodic GC | `"30min"`, `"1h"` | no default |

---

## Execution Behavior

| Key | Purpose | Example Values | Default Value |
|-----|---------|---------------|---------------|
| `spark.task.cpus` | Number of CPUs per task | `1`, `2`, `4` | `1` |
| `spark.task.maxFailures` | Max task failures before failing job | `1`, `3`, `5` | `3` |
| `spark.speculation` | Enable speculative execution | `true`, `false` | `false` |
| `spark.speculation.interval` | Interval to check for speculation | `"100ms"`, `"1s"` | `"100ms"` |
| `spark.speculation.multiplier` | Multiplier for speculation threshold | `1.5`, `2.0`, `3.0` | `1.5` |
| `spark.broadcast.blockSize` | Block size for broadcast variables | `"4m"`, `"8m"`, `"16m"` | `"4m"` |
| `spark.files.fetchTimeout` | Timeout for fetching files | `"60s"`, `"120s"`, `"300s"` | `"60s"` |
| `spark.files.useFetchCache` | Use local cache for remote files | `true`, `false` | `true` |
| `spark.files.overwrite` | Overwrite files if they exist | `true`, `false` | `false` |

---

## Shuffle Behavior

| Key | Purpose | Example Values | Default Value |
|-----|---------|---------------|---------------|
| `spark.shuffle.compress` | Compress shuffle output files | `true`, `false` | `true` |
| `spark.shuffle.file.buffer` | Buffer size for shuffle files | `"32k"`, `"64k"`, `"128k"` | `"32k"` |
| `spark.shuffle.io.maxRetries` | Max retries for shuffle IO failures | `3`, `5`, `10` | `3` |
| `spark.shuffle.io.retryWait` | Wait time between shuffle retries | `"5s"`, `"10s"`, `"30s"` | `"5s"` |
| `spark.shuffle.service.enabled` | Enable external shuffle service | `true`, `false` | `false` |
| `spark.shuffle.service.port` | Port for external shuffle service | `7337`, `7338` | `7337` |
| `spark.shuffle.sort.bypassMergeThreshold` | Threshold to bypass merge sort | `200`, `400`, `800` | `200` |
| `spark.shuffle.spill.compress` | Compress spilled shuffle data | `true`, `false` | `true` |

---

## Storage Configuration
| Key | Purpose | Example Values | Default Value |
|-----|---------|---------------|---------------|
| `spark.storage.memoryFraction` | Fraction of memory for RDD storage | `"0.6"`, `"0.8"` |
| `spark.storage.unrollFraction` | Fraction of memory for unrolling blocks | `"0.2"`, `"0.3"` |
| `spark.storage.blockManagerHeartBeatMs` | Block manager heartbeat interval | `"10000"`, `"30000"` |

---

## Networking

| Key | Purpose | Example Values | Default Value |
|-----|---------|---------------|---------------|
| `spark.rpc.message.maxSize` | Max RPC message size | `"128"`, `"256"`, `"512"` | `"128"` (MB) |
| `spark.network.timeout` | Default network timeout | `"120s"`, `"300s"`, `"600s"` | `"120s"` |
| `spark.rpc.askTimeout` | Timeout for RPC ask operations | `"120s"`, `"300s"` | value of `spark.network.timeout` |
| `spark.rpc.lookupTimeout` | Timeout for RPC lookups | `"120s"`, `"300s"` | `"120s"` |
| `spark.blockManager.port` | Port for block managers | `random`, `8020`, `8021` | random |
| `spark.driver.port` | Port for driver to listen on | `random`, `4040`, `4041` | random |
| `spark.driver.host` | Hostname/IP for driver | `"localhost"`, `"10.0.0.1"` | local hostname |
| `spark.driver.bindAddress` | Address to bind listening sockets | `"0.0.0.0"`, `"10.0.0.1"` | value of `spark.driver.host` |

---

## Spark SQL

| Key | Purpose | Example Values | Default Value |
|-----|---------|---------------|---------------|
| `spark.sql.adaptive.enabled` | Enable adaptive query execution | `true`, `false` | `true` |
| `spark.sql.adaptive.coalescePartitions.enabled` | Coalesce shuffle partitions | `true`, `false` | `true` |
| `spark.sql.adaptive.skewJoin.enabled` | Handle skewed joins | `true`, `false` | `true` |
| `spark.sql.autoBroadcastJoinThreshold` | Broadcast join threshold | `"10MB"`, `"20MB"`, `"-1"` | `"10MB"` |
| `spark.sql.warehouse.dir` | Default warehouse directory | `"/path/to/warehouse"` | `$PWD/spark-warehouse` |
| `spark.sql.catalogImplementation` | Catalog implementation | `"hive"`, `"in-memory"` | `"in-memory"` |
| `spark.sql.hive.metastore.version` | Hive metastore version | `"2.3.9"`, `"3.1.2"` | `"2.3.9"` |
| `spark.sql.hive.metastore.jars` | Hive metastore JARs location | `"builtin"`, `"maven"`, `"/path/to/jars"` | `"builtin"` |
| `spark.sql.execution.arrow.pyspark.enabled` | Enable Arrow for PySpark | `true`, `false` | `false` |
| `spark.sql.repl.eagerEval.enabled` | Enable eager evaluation in REPL | `true`, `false` | `false` |

---

## Hive Configuration

| Key | Purpose | Example Values | Default Value |
|-----|---------|---------------|---------------|
| `hive.metastore.uris` | Hive metastore URI | `"thrift://localhost:9083"`, `"thrift://metastore:9083"` |
| `hive.metastore.warehouse.dir` | Hive warehouse directory | `"/user/hive/warehouse"`, `"s3a://bucket/warehouse"` |
| `hive.exec.dynamic.partition` | Enable dynamic partitioning | `"true"`, `"false"` |
| `hive.exec.dynamic.partition.mode` | Dynamic partition mode | `"nonstrict"`, `"strict"` |
| `hive.exec.max.dynamic.partitions` | Maximum dynamic partitions | `"1000"`, `"5000"` |

---

## Compression and Serialization

| Key | Purpose | Example Values | Default Value |
|-----|---------|---------------|---------------|
| `spark.serializer` | Serializer for RDD data | `"org.apache.spark.serializer.KryoSerializer"` | `"org.apache.spark.serializer.JavaSerializer"` |
| `spark.io.compression.codec` | Compression codec for internal data | `"lz4"`, `"lzf"`, `"snappy"`, `"zstd"` | `"lz4"` |
| `spark.broadcast.compress` | Compress broadcast variables | `true`, `false` | `true` |
| `spark.rdd.compress` | Compress serialized RDD partitions | `true`, `false` | `false` |
| `spark.kryo.registrationRequired` | Require Kryo registration | `true`, `false` | `false` |
| `spark.kryo.referenceTracking` | Track object references in Kryo | `true`, `false` | `true` |
| `spark.kryoserializer.buffer` | Initial Kryo buffer size | `"64k"`, `"128k"`, `"256k"` | `"64k"` |
| `spark.kryoserializer.buffer.max` | Max Kryo buffer size | `"64m"`, `"128m"`, `"256m"` | `"64m"` |

---

## Logging and UI

| Key | Purpose | Example Values | Default Value |
|-----|---------|---------------|---------------|
| `spark.logConf` | Log effective SparkConf at startup | `true`, `false` | `false` |
| `spark.ui.enabled` | Enable Spark web UI | `true`, `false` | `true` |
| `spark.ui.port` | Port for Spark web UI | `4040`, `4041`, `8080` | `4040` |
| `spark.ui.retainedJobs` | Number of jobs to retain in UI | `1000`, `2000`, `5000` | `1000` |
| `spark.ui.retainedStages` | Number of stages to retain in UI | `1000`, `2000`, `5000` | `1000` |
| `spark.ui.retainedTasks` | Number of tasks to retain in UI | `100000`, `200000` | `100000` |
| `spark.eventLog.enabled` | Enable event logging | `true`, `false` | `false` |
| `spark.eventLog.dir` | Directory for event logs | `"/tmp/spark-events"`, `"hdfs://logs"` | `"file:///tmp/spark-events"` |
| `spark.eventLog.compress` | Compress event logs | `true`, `false` | `false` |
| `spark.ui.showConsoleProgress` | Show progress in console | `true`, `false` | `false` (true in shell) |

---

## Dynamic Allocation

| Key | Purpose | Example Values | Default Value |
|-----|---------|---------------|---------------|
| `spark.dynamicAllocation.enabled` | Enable dynamic executor allocation | `true`, `false` | `false` |
| `spark.dynamicAllocation.minExecutors` | Minimum number of executors | `0`, `1`, `5` | `0` |
| `spark.dynamicAllocation.maxExecutors` | Maximum number of executors | `10`, `50`, `100` | `infinity` |
| `spark.dynamicAllocation.initialExecutors` | Initial number of executors | `1`, `5`, `10` | value of `spark.dynamicAllocation.minExecutors` |
| `spark.dynamicAllocation.executorIdleTimeout` | Timeout for idle executors | `"60s"`, `"300s"`, `"600s"` | `"60s"` |
| `spark.dynamicAllocation.cachedExecutorIdleTimeout` | Timeout for cached executors | `"infinity"`, `"1800s"` | `"infinity"` |
| `spark.dynamicAllocation.schedulerBacklogTimeout` | Backlog timeout before scaling up | `"1s"`, `"5s"`, `"10s"` | `"1s"` |
| `spark.dynamicAllocation.sustainedSchedulerBacklogTimeout` | Sustained backlog timeout | `"1s"`, `"5s"` | value of `schedulerBacklogTimeout` |

---

## Security

| Key | Purpose | Example Values | Default Value |
|-----|---------|---------------|---------------|
| `spark.authenticate` | Enable Spark authentication | `true`, `false` | `false` |
| `spark.authenticate.secret` | Shared secret for authentication | `"mysecret"`, `"abc123"` | no default |
| `spark.ssl.enabled` | Enable SSL | `true`, `false` | `false` |
| `spark.ssl.keyStore` | Path to SSL keystore | `"/path/to/keystore.jks"` | no default |
| `spark.ssl.keyStorePassword` | Keystore password | `"password123"` | no default |
| `spark.ssl.trustStore` | Path to SSL truststore | `"/path/to/truststore.jks"` | no default |
| `spark.ssl.trustStorePassword` | Truststore password | `"password123"` | no default |
| `spark.acls.enable` | Enable Spark ACLs | `true`, `false` | `false` |
| `spark.admin.acls` | Admin users for ACLs | `"admin1,admin2"` | no default |

---

## Checkpointing and Logging Configuration

| Key | Purpose | Example Values | Default Value |
|-----|---------|---------------|---------------|
| `spark.sql.streaming.checkpointLocation` | Checkpoint location for streaming | `"/tmp/checkpoints"`, `"s3a://bucket/checkpoints"` |
| `spark.sql.recovery.checkpointDir` | Directory for SQL recovery checkpoints | `"/tmp/recovery"`, `"hdfs://namenode/recovery"` |
| `spark.eventLog.enabled` | Enable event logging | `"true"`, `"false"` |
| `spark.eventLog.dir` | Directory for event logs | `"/tmp/spark-events"`, `"hdfs://namenode/spark-logs"` |
| `spark.eventLog.compress` | Compress event logs | `"true"`, `"false"` |
| `spark.history.fs.logDirectory` | History server log directory | `"/tmp/spark-events"`, `"s3a://bucket/spark-logs"` |

---
## Kubernetes Specific

| Key | Purpose | Example Values | Default Value |
|-----|---------|---------------|---------------|
| `spark.kubernetes.container.image` | Docker image for executors | `"spark:3.5.0"`, `"myregistry/spark:latest"` | no default |
| `spark.kubernetes.namespace` | Kubernetes namespace | `"default"`, `"spark-jobs"` | `"default"` |
| `spark.kubernetes.authenticate.driver.serviceAccountName` | Service account for driver | `"spark-driver"` | no default |
| `spark.kubernetes.executor.deleteOnTermination` | Delete executor pods on termination | `true`, `false` | `true` |
| `spark.kubernetes.executor.request.cores` | CPU request for executors | `"1"`, `"2"`, `"0.5"` | no default |
| `spark.kubernetes.executor.limit.cores` | CPU limit for executors | `"2"`, `"4"`, `"1"` | no default |
| `spark.kubernetes.driver.pod.name` | Name for driver pod | `"my-spark-driver"` | no default |

---

## YARN Specific

| Key | Purpose | Example Values | Default Value |
|-----|---------|---------------|---------------|
| `spark.yarn.queue` | YARN queue to submit to | `"default"`, `"production"`, `"batch"` | `"default"` |
| `spark.yarn.am.memory` | Memory for YARN Application Master | `"512m"`, `"1g"`, `"2g"` | `"512m"` |
| `spark.yarn.am.cores` | Cores for YARN Application Master | `1`, `2` | `1` |
| `spark.yarn.executor.memoryOverhead` | Memory overhead for executors | `"384m"`, `"1g"` | `max(384, .1 * spark.executor.memory)` |
| `spark.yarn.am.waitTime` | Wait time for AM to start | `"100s"`, `"300s"` | `"100s"` |
| `spark.yarn.submit.waitAppCompletion` | Wait for app completion | `true`, `false` | `true` |
| `spark.yarn.appMasterEnv.VARIABLE` | Environment variables for AM | `"value"` | no default |
| `spark.yarn.executorEnv.VARIABLE` | Environment variables for executors | `"value"` | no default |

---

## Data Sources

| Key | Purpose | Example Values | Default Value |
|-----|---------|---------------|---------------|
| `spark.sql.sources.default` | Default data source format | `"parquet"`, `"delta"`, `"json"` | `"parquet"` |
| `spark.sql.parquet.compression.codec` | Parquet compression codec | `"snappy"`, `"gzip"`, `"lzo"` | `"snappy"` |
| `spark.sql.parquet.enableVectorizedReader` | Enable vectorized Parquet reader | `true`, `false` | `true` |
| `spark.sql.orc.compression.codec` | ORC compression codec | `"snappy"`, `"zlib"`, `"lzo"` | `"snappy"` |
| `spark.sql.csv.filterPushdown.enabled` | Enable CSV filter pushdown | `true`, `false` | `true` |
| `spark.sql.json.filterPushdown.enabled` | Enable JSON filter pushdown | `true`, `false` | `true` |
| `spark.sql.files.maxPartitionBytes` | Max bytes per file partition | `"128MB"`, `"256MB"`, `"512MB"` | `"128MB"` |
| `spark.sql.files.maxRecordsPerFile` | Max records per output file | `0`, `10000`, `100000` | `0` (unlimited) |

---

## Connect (Spark 3.4+)

| Key | Purpose | Example Values | Default Value |
|-----|---------|---------------|---------------|
| `spark.connect.grpc.binding.port` | Port for Spark Connect server | `15002`, `15003` | `15002` |
| `spark.connect.grpc.maxInboundMessageSize` | Max gRPC message size | `134217728`, `268435456` | `134217728` |
| `spark.connect.grpc.arrow.maxBatchSize` | Max Arrow batch size | `"4m"`, `"8m"`, `"16m"` | `"4m"` |

---

## Advanced Configuration

| Key | Purpose | Example Values | Default Value |
|-----|---------|---------------|---------------|
| `spark.jars` | Additional JARs to include | `"/path/to/jar1.jar,/path/to/jar2.jar"` |
| `spark.jars.packages` | Maven packages to include | `"org.apache.spark:spark-avro_2.12:3.4.0"` |
| `spark.files` | Additional files to include | `"/path/to/file1.txt,/path/to/file2.conf"` |
| `spark.python.worker.reuse` | Reuse Python worker processes | `"true"`, `"false"` |
| `spark.python.worker.memory` | Memory for Python worker processes | `"512m"`, `"1g"` |
| `spark.task.maxFailures` | Maximum task failures before job fails | `"1"`, `"3"`, `"5"` |
| `spark.stage.maxConsecutiveAttempts` | Maximum consecutive stage attempts | `"4"`, `"8"` |

---
## Notes

### Time Formats
- `25ms` (milliseconds)
- `5s` (seconds) 
- `10m` or `10min` (minutes)
- `3h` (hours)
- `5d` (days)
- `1y` (years)

### Size Formats  
- `1b` (bytes)
- `1k` or `1kb` (kibibytes = 1024 bytes)
- `1m` or `1mb` (mebibytes = 1024 kibibytes) 
- `1g` or `1gb` (gibibytes = 1024 mebibytes)
- `1t` or `1tb` (tebibytes = 1024 gibibytes)
- `1p` or `1pb` (pebibytes = 1024 tebibytes)

### Configuration Precedence (highest to lowest)
1. `SparkConf` set programmatically
2. `--conf` flags passed to `spark-submit` 
3. `spark-defaults.conf` file
4. Default values

### Additional Resources
- [Official Spark Configuration Documentation](https://spark.apache.org/docs/latest/configuration.html)
- Use `spark.conf.getAll()` to view all current configurations
- Use `spark.conf.isModifiable("config.key")` to check if a config can be changed at runtime

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
