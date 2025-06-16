# Apache Spark Resource Configuration Cheatsheet

## Core Concepts

| Term | Description |
|------|-------------|
| **Driver** | The process running the main() function and creating the SparkContext |
| **Executor** | Worker processes that run tasks and store data |
| **Worker** | Physical or virtual machine that hosts executors |
| **Core** | CPU core assigned for computation |
| **Memory** | RAM allocated to executors or drivers |

# Apache Spark Resource Configuration Cheatsheet

## Core Concepts

| Term | Description |
|------|-------------|
| **Driver** | The process running the main() function and creating the SparkContext |
| **Executor** | Worker processes that run tasks and store data |
| **Worker** | Physical or virtual machine that hosts executors |
| **Core** | CPU core assigned for computation |
| **Memory** | RAM allocated to executors or drivers |

## Modifying Number of Workers

### Standalone Mode

#### Submit-time Configuration
```bash
# Start an application with 5 workers
spark-submit --master spark://master:7077 \
  --num-executors 5 \
  --class YourMainClass yourapp.jar
```

#### Cluster Setup
```bash
# In spark-env.sh on each worker node
export SPARK_WORKER_INSTANCES=3  # Run 3 worker instances on this machine
```

### YARN Mode

```bash
# Set number of executors (workers)
spark-submit --master yarn \
  --num-executors 10 \
  --class YourMainClass yourapp.jar
```

### Kubernetes Mode

```bash
# Specify number of executors
spark-submit --master k8s://https://kubernetes-api:443 \
  --deploy-mode cluster \
  --conf spark.executor.instances=10 \
  --class YourMainClass yourapp.jar
```

### Dynamic Allocation

```bash
# Enable dynamic allocation in spark-defaults.conf
spark.dynamicAllocation.enabled true
spark.dynamicAllocation.minExecutors 5
spark.dynamicAllocation.maxExecutors 20
spark.dynamicAllocation.initialExecutors 10
```

## Modifying Worker Resources

### CPU (Cores)

#### Standalone Mode
```bash
# In spark-env.sh on each worker
export SPARK_WORKER_CORES=16  # Total cores on this worker

# At submit time
spark-submit --master spark://master:7077 \
  --executor-cores 4 \  # Cores per executor
  --class YourMainClass yourapp.jar
```

#### YARN Mode
```bash
spark-submit --master yarn \
  --executor-cores 4 \  # Cores per executor
  --driver-cores 2 \    # Cores for driver
  --class YourMainClass yourapp.jar
```

#### Kubernetes Mode
```bash
spark-submit --master k8s://https://kubernetes-api:443 \
  --conf spark.executor.cores=4 \
  --conf spark.driver.cores=2 \
  --class YourMainClass yourapp.jar
```

### Memory

#### Standalone Mode
```bash
# In spark-env.sh on each worker
export SPARK_WORKER_MEMORY=64g  # Total memory on this worker

# At submit time
spark-submit --master spark://master:7077 \
  --executor-memory 8g \  # Memory per executor
  --driver-memory 4g \    # Memory for driver
  --class YourMainClass yourapp.jar
```

#### YARN Mode
```bash
spark-submit --master yarn \
  --executor-memory 8g \  # Memory per executor
  --driver-memory 4g \    # Memory for driver
  --conf spark.yarn.executor.memoryOverhead=2g \  # Off-heap memory
  --class YourMainClass yourapp.jar
```

#### Kubernetes Mode
```bash
spark-submit --master k8s://https://kubernetes-api:443 \
  --conf spark.executor.memory=8g \
  --conf spark.driver.memory=4g \
  --conf spark.executor.memoryOverhead=2g \
  --class YourMainClass yourapp.jar
```

## Using SparkConf/SparkSession API

```python
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("ResourceExample") \
    .master("spark://master:7077") \
    .config("spark.executor.instances", 10) \
    .config("spark.executor.cores", 4) \
    .config("spark.executor.memory", "8g") \
    .config("spark.driver.memory", "4g") \
    .getOrCreate()
```

## Memory Management for Spark Tasks

```bash
# Configure memory fractions
spark-submit \
  --conf spark.memory.fraction=0.8 \  # Fraction of heap used for execution and storage
  --conf spark.memory.storageFraction=0.3 \  # Fraction of spark.memory.fraction for storage
  --class YourMainClass yourapp.jar
```

## Advanced Configurations

### Custom Resource Scheduling

```bash
# Configure scheduling mode
spark-submit \
  --conf spark.scheduler.mode=FAIR \  # FAIR or FIFO
  --class YourMainClass yourapp.jar
```

### Local Mode Resources

```bash
# Set resources in local mode
spark-submit --master local[8] \  # Use 8 cores
  --driver-memory 8g \
  --class YourMainClass yourapp.jar
```

### Off-Heap Memory

```bash
# Configure off-heap memory
spark-submit \
  --conf spark.memory.offHeap.enabled=true \
  --conf spark.memory.offHeap.size=4g \
  --class YourMainClass yourapp.jar
```


# Spark Resource Configuration Explained

Apache Spark lets you control the number and resources of worker nodes (executors) through various configuration options, depending on your deployment mode. Here's a detailed explanation:

## Understanding Spark's Architecture

First, it's important to understand the components:

- **Master node**: Coordinates the job and resource allocation
- **Worker nodes**: Execute tasks in parallel
- **Executors**: JVM processes running on worker nodes that execute tasks
- **Cores**: CPU cores assigned to each executor
- **Memory**: RAM allocated to each executor

## Ways to Modify Worker Resources

### 1. Deployment Mode Consideration

The method for configuring resources varies based on how you're running Spark:

- **Standalone cluster**: Spark manages its own resources
- **YARN**: Hadoop's resource manager handles allocation
- **Kubernetes**: Container orchestration manages resources
- **Mesos**: Another cluster manager option
- **Local mode**: For testing, runs everything on one machine

When running Spark locally, the base resource negotiator (also known as the cluster manager) is the **Standalone mode** or more specifically, the **local mode**.

  ### 0. Local Mode (Default for Local Execution)
  
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

### 2. Number of Workers/Executors

You can control how many executors (workers) run your tasks:

- In standalone mode: `--num-executors` or `spark.executor.instances`
- In YARN: `--num-executors` or enable dynamic allocation
- In Kubernetes: `spark.executor.instances`

Dynamic allocation automatically adjusts the number of executors based on workload:

```
spark.dynamicAllocation.enabled true
spark.dynamicAllocation.minExecutors 5
spark.dynamicAllocation.maxExecutors 20
```

### 3. CPU Resources

Control how many CPU cores each executor uses:

- `--executor-cores` or `spark.executor.cores`: Cores per executor
- `--driver-cores` or `spark.driver.cores`: Cores for the driver program

Example effect: If you have 10 executors with 4 cores each, you can run 40 tasks in parallel.

### 4. Memory Resources

Configure memory allocation:

- `--executor-memory` or `spark.executor.memory`: RAM per executor
- `--driver-memory` or `spark.driver.memory`: RAM for driver
- `spark.memory.fraction`: Portion of heap used for execution and storage (default 0.6)
- `spark.memory.storageFraction`: Portion of execution memory used for storage (default 0.5)

Memory overhead (off-heap memory) can be configured with:
- `spark.yarn.executor.memoryOverhead` (YARN)
- `spark.executor.memoryOverhead` (K8s)

## Common Configuration Scenarios

### Scenario 1: Large Data Processing

For processing large datasets that don't fit in memory:
- Increase number of executors
- Use moderate memory per executor
- Focus on I/O optimization

### Scenario 2: Complex Computations

For computation-heavy jobs:
- Allocate more cores per executor
- Ensure adequate memory for in-memory processing
- Consider increasing driver memory if collecting large results

### Scenario 3: Memory-Intensive Operations

For jobs with large shuffles, joins, or aggregations:
- Increase executor memory
- Consider adjusting `spark.memory.fraction` upward
- Monitor for spills to disk, which indicate memory pressure

## Best Practices

1. **Monitor and tune**: Use Spark UI to identify bottlenecks
2. **Balance resources**: Don't allocate too much memory per executor, as it can lead to inefficient garbage collection
3. **Consider data size**: Match total executor memory to at least your dataset size for best performance
4. **Start conservative**: Begin with default settings and adjust based on performance metrics
5. **Remember overhead**: Account for OS and JVM overhead when allocating resources

Would you like me to elaborate on any specific aspect of Spark resource configuration?


## Modifying Number of Workers

### Standalone Mode

#### Submit-time Configuration
```bash
# Start an application with 5 workers
spark-submit --master spark://master:7077 \
  --num-executors 5 \
  --class YourMainClass yourapp.jar
```

#### Cluster Setup
```bash
# In spark-env.sh on each worker node
export SPARK_WORKER_INSTANCES=3  # Run 3 worker instances on this machine
```

### YARN Mode

```bash
# Set number of executors (workers)
spark-submit --master yarn \
  --num-executors 10 \
  --class YourMainClass yourapp.jar
```

### Kubernetes Mode

```bash
# Specify number of executors
spark-submit --master k8s://https://kubernetes-api:443 \
  --deploy-mode cluster \
  --conf spark.executor.instances=10 \
  --class YourMainClass yourapp.jar
```

### Dynamic Allocation

```bash
# Enable dynamic allocation in spark-defaults.conf
spark.dynamicAllocation.enabled true
spark.dynamicAllocation.minExecutors 5
spark.dynamicAllocation.maxExecutors 20
spark.dynamicAllocation.initialExecutors 10
```

## Modifying Worker Resources

### CPU (Cores)

#### Standalone Mode
```bash
# In spark-env.sh on each worker
export SPARK_WORKER_CORES=16  # Total cores on this worker

# At submit time
spark-submit --master spark://master:7077 \
  --executor-cores 4 \  # Cores per executor
  --class YourMainClass yourapp.jar
```

#### YARN Mode
```bash
spark-submit --master yarn \
  --executor-cores 4 \  # Cores per executor
  --driver-cores 2 \    # Cores for driver
  --class YourMainClass yourapp.jar
```

#### Kubernetes Mode
```bash
spark-submit --master k8s://https://kubernetes-api:443 \
  --conf spark.executor.cores=4 \
  --conf spark.driver.cores=2 \
  --class YourMainClass yourapp.jar
```

### Memory

#### Standalone Mode
```bash
# In spark-env.sh on each worker
export SPARK_WORKER_MEMORY=64g  # Total memory on this worker

# At submit time
spark-submit --master spark://master:7077 \
  --executor-memory 8g \  # Memory per executor
  --driver-memory 4g \    # Memory for driver
  --class YourMainClass yourapp.jar
```

#### YARN Mode
```bash
spark-submit --master yarn \
  --executor-memory 8g \  # Memory per executor
  --driver-memory 4g \    # Memory for driver
  --conf spark.yarn.executor.memoryOverhead=2g \  # Off-heap memory
  --class YourMainClass yourapp.jar
```

#### Kubernetes Mode
```bash
spark-submit --master k8s://https://kubernetes-api:443 \
  --conf spark.executor.memory=8g \
  --conf spark.driver.memory=4g \
  --conf spark.executor.memoryOverhead=2g \
  --class YourMainClass yourapp.jar
```

## Using SparkConf/SparkSession API

```python
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("ResourceExample") \
    .master("spark://master:7077") \
    .config("spark.executor.instances", 10) \
    .config("spark.executor.cores", 4) \
    .config("spark.executor.memory", "8g") \
    .config("spark.driver.memory", "4g") \
    .getOrCreate()
```

## Memory Management for Spark Tasks

```bash
# Configure memory fractions
spark-submit \
  --conf spark.memory.fraction=0.8 \  # Fraction of heap used for execution and storage
  --conf spark.memory.storageFraction=0.3 \  # Fraction of spark.memory.fraction for storage
  --class YourMainClass yourapp.jar
```

## Advanced Configurations

### Custom Resource Scheduling

```bash
# Configure scheduling mode
spark-submit \
  --conf spark.scheduler.mode=FAIR \  # FAIR or FIFO
  --class YourMainClass yourapp.jar
```

### Local Mode Resources

```bash
# Set resources in local mode
spark-submit --master local[8] \  # Use 8 cores
  --driver-memory 8g \
  --class YourMainClass yourapp.jar
```

### Off-Heap Memory

```bash
# Configure off-heap memory
spark-submit \
  --conf spark.memory.offHeap.enabled=true \
  --conf spark.memory.offHeap.size=4g \
  --class YourMainClass yourapp.jar
```
