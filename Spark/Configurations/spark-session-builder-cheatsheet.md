# SparkSession.builder Cheat Sheet

## Basic Creation
```python
from pyspark.sql import SparkSession

# Most basic initialization
spark = SparkSession.builder.getOrCreate()

# Common standard initialization
spark = SparkSession.builder \
    .appName("My Application") \
    .master("local[*]") \
    .getOrCreate()
```

## Core Configuration Methods

### Essential Settings
| Method | Description | Example |
|--------|-------------|---------|
| `.appName(name)` | Set application name | `.appName("Data Processing App")` |
| `.master(url)` | Set master URL | `.master("local[4]")` or `.master("spark://host:7077")` |
| `.config(key, value)` | Set configuration property | `.config("spark.executor.memory", "4g")` |
| `.getOrCreate()` | Get existing or create new session | Required as final call to build the session |
| `.enableHiveSupport()` | Enable Hive support | `.enableHiveSupport()` |

### Master URL Options
| Value | Description |
|-------|-------------|
| `local` | Run Spark locally with 1 worker thread |
| `local[n]` | Run locally with n worker threads |
| `local[*]` | Run locally with as many threads as logical cores |
| `spark://host:port` | Connect to Spark standalone cluster |
| `yarn` | Connect to YARN cluster |
| `k8s://host:port` | Connect to Kubernetes cluster |

## Common Configuration Properties

### Memory Management
```python
spark = SparkSession.builder \
    .config("spark.driver.memory", "4g") \
    .config("spark.executor.memory", "4g") \
    .config("spark.memory.offHeap.enabled", "true") \
    .config("spark.memory.offHeap.size", "2g") \
    .getOrCreate()
```

### Performance Tuning
```python
spark = SparkSession.builder \
    .config("spark.default.parallelism", 100) \
    .config("spark.sql.shuffle.partitions", 100) \
    .config("spark.executor.cores", 4) \
    .config("spark.executor.instances", 10) \
    .config("spark.dynamicAllocation.enabled", "true") \
    .config("spark.dynamicAllocation.minExecutors", 5) \
    .config("spark.dynamicAllocation.maxExecutors", 20) \
    .getOrCreate()
```

### Serialization
```python
spark = SparkSession.builder \
    .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer") \
    .config("spark.kryo.registrationRequired", "false") \
    .config("spark.kryo.registrator", "com.example.MyRegistrator") \
    .getOrCreate()
```

### Storage and I/O
```python
spark = SparkSession.builder \
    .config("spark.sql.files.maxPartitionBytes", 134217728) \  # 128MB
    .config("spark.sql.files.openCostInBytes", 4194304) \      # 4MB
    .config("spark.sql.broadcastTimeout", 300) \               # seconds
    .config("spark.sql.autoBroadcastJoinThreshold", 10485760) \ # 10MB
    .getOrCreate()
```

### SQL Specific Settings
```python
spark = SparkSession.builder \
    .config("spark.sql.warehouse.dir", "/path/to/warehouse") \
    .config("spark.sql.shuffle.partitions", 200) \
    .config("spark.sql.adaptive.enabled", "true") \
    .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
    .config("spark.sql.adaptive.skewJoin.enabled", "true") \
    .config("spark.sql.caseSensitive", "false") \
    .getOrCreate()
```

### Logging Configuration
```python
spark = SparkSession.builder \
    .config("spark.eventLog.enabled", "true") \
    .config("spark.eventLog.dir", "hdfs://namenode:8021/directory") \
    .config("spark.driver.extraJavaOptions", "-Dlog4j.configuration=file:log4j.properties") \
    .getOrCreate()
```

### Security
```python
spark = SparkSession.builder \
    .config("spark.authenticate", "true") \
    .config("spark.authenticate.secret", "your-secret") \
    .config("spark.network.crypto.enabled", "true") \
    .config("spark.acls.enable", "true") \
    .config("spark.ui.view.acls", "user1,user2") \
    .getOrCreate()
```

### Miscellaneous
```python
spark = SparkSession.builder \
    .config("spark.ui.port", 4040) \
    .config("spark.ui.enabled", "true") \
    .config("spark.ui.reverseProxy", "true") \
    .config("spark.driver.extraClassPath", "/path/to/jars") \
    .config("spark.executor.extraClassPath", "/path/to/jars") \
    .getOrCreate()
```

## Setting Multiple Configurations

### From Dictionary
```python
conf = {
    "spark.driver.memory": "4g",
    "spark.executor.memory": "4g",
    "spark.executor.cores": "2",
    "spark.dynamicAllocation.enabled": "true"
}

spark = SparkSession.builder \
    .appName("ConfigFromDict") \
    .master("yarn") \
    .config(conf=conf) \  # Pass dictionary of configs
    .getOrCreate()
```

### From SparkConf Object
```python
from pyspark import SparkConf

conf = SparkConf() \
    .setAppName("ConfigFromSparkConf") \
    .setMaster("local[*]") \
    .set("spark.driver.memory", "4g") \
    .set("spark.executor.memory", "4g")

spark = SparkSession.builder \
    .config(conf=conf) \
    .getOrCreate()
```

## Advanced Patterns

### Using Environment Variables
```python
import os

# Get config from environment variables
app_name = os.environ.get("SPARK_APP_NAME", "DefaultApp")
master_url = os.environ.get("SPARK_MASTER_URL", "local[*]")

spark = SparkSession.builder \
    .appName(app_name) \
    .master(master_url) \
    .getOrCreate()
```

### Temporary Session with Stop
```python
spark = SparkSession.builder \
    .appName("TemporarySession") \
    .master("local[*]") \
    .getOrCreate()

# Do work...

# Stop the session when done
spark.stop()
```

### Multiple Sessions (Advanced)
```python
# First session
spark1 = SparkSession.builder \
    .appName("Session1") \
    .config("spark.sql.warehouse.dir", "/warehouse1") \
    .getOrCreate()

# Create a new session with different configurations
spark2 = SparkSession.builder \
    .appName("Session2") \
    .config("spark.sql.warehouse.dir", "/warehouse2") \
    .newSession()
```
