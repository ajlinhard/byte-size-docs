
# Spark (PySpark)
Apache Spark is a modern day large data process on OLAP and DSS systems. Systems requiring more traditional transactional update, small inserts, and logging other traditional databases like dynamo, cassandra, etc.

## Table of Contents

- [Spark (PySpark)](#spark-pyspark)
  - [Documentation/Tutorials](#documentation-tutorials)
  - [Spark Links](#spark-links)
  - [To Study Spark Items](#to-study-spark-items)
- [Key Spark Concepts](#key-spark-concepts)
  - [Spark Context vs. Spark Sessions](#spark-context-vs-spark-sessions)
    - [SparkContext](#sparkcontext)
    - [SparkSession](#sparksession)
    - [Key Differences](#key-differences)
  - [Data Architecture Layers](#data-architecture-layers)
  - [RDD (Resilient Distributed Dataset)](#rdd-resilient-distributed-dataset)
  - [DataFrame](#dataframe)
  - [Table](#table)
  - [Key Differences](#key-differences-1)
- [Important Error Help](#important-error-help)
  - [Mismatch Python Versions for Driver vs. Worker](#mismatch-python-versions-for-driver-vs-worker)

## Documentation/ Tutorials:
1. [Great Architecture Overview](https://www.youtube.com/watch?v=jDkLiqlyQaY)
2. [In-depth Architecture](https://www.youtube.com/watch?v=iXVIPQEGZ9Y)
3. [Spark By Examples Help](https://sparkbyexamples.com/)
   <br>b. [Spark Use/RDD](https://sparkbyexamples.com/pyspark-rdd/))
   <br>b. [AWS Implementations](https://sparkbyexamples.com/apache-spark-on-amazon-web-services/)
   <br>c. [Kafka Streaming](https://sparkbyexamples.com/apache-spark-streaming-tutorial/)

# Spark Links
1. Loading Files Options
    https://spark.apache.org/docs/latest/sql-data-sources-csv.html#data-source-option
2. Spark SQL Guide
    https://spark.apache.org/docs/latest/sql-getting-started.html
3. Pandas API on Spark
    https://spark.apache.org/docs/latest/api/python/user_guide/pandas_on_spark/index.html
4. Quick Start Dataframes
    https://spark.apache.org/docs/latest/api/python/getting_started/quickstart_df.html
5. Column Scalar and Aggragate functions
    a. [Built-in Scalar Functions](https://spark.apache.org/docs/latest/sql-ref-functions.html#scalar-functions)
    b. [User Defined Functions(UDF) Scalar](https://spark.apache.org/docs/latest/sql-ref-functions-udf-scalar.html)
    c. [Built-in Aggregate Functions](https://spark.apache.org/docs/latest/sql-ref-functions-builtin.html#aggregate-functions)
    d. [User Defined Functions(UDF) Aggregate](https://spark.apache.org/docs/latest/sql-ref-functions-udf-aggregate.html)

# To Study Spark Items
- Loading Data
    - Avro, JSON, parquet
    - multiple files in a folder
    - odd CSVs
- Flow actions
    - drop table
    - check if table exists
    - joins
        - tables stored on the server
        - dataframes in memory
- Different write and read modes
Next
- Creating new catalogs
    - creating additional db/schema, separate from default.
- Creating spark jobs and threads
---
# Key Spark Concepts

### Spark Context vs. Spark Sessions
A SparkContext and a SparkSession are both fundamental components in Apache Spark, but they serve different purposes and were introduced in different versions of Spark. Let me explain the key differences:

## SparkContext
SparkContext is the older original entry point for Spark functionality:

- Only 1 SparkContext instance should exists per JVM. Best practices to stop() the context before creating a new one.
- It connects your application to a Spark cluster
- It's used primarily for creating RDDs (Resilient Distributed Datasets)
- It was the main entry point in Spark 1.x
- Each JVM can only have one active SparkContext at a time
- It's focused on lower-level operations and core Spark functionality
- You configure cluster connection parameters through SparkContext

Example creation:
```python
from pyspark import SparkConf, SparkContext
conf = SparkConf().setAppName("MyApp").setMaster("local")
sc = SparkContext(conf=conf)
```

## SparkSession

SparkSession is the newer, unified entry point introduced in Spark 2.0:

- It encapsulates SparkContext, SQLContext, HiveContext, and other contexts
- It provides a single point of entry to interact with all Spark functionality
- It's designed to work with the DataFrame and Dataset APIs
- It simplifies working with structured data
- It has built-in SQL capabilities
- Multiple SparkSessions can exist within the same application

Example creation:
```python
from pyspark.sql import SparkSession
spark = SparkSession.builder \
    .appName("MyApp") \
    .master("local") \
    .getOrCreate()

# Access the underlying SparkContext if needed
sc = spark.sparkContext
```

## Key Differences

1. **Hierarchy**: SparkSession is higher-level and internally contains a SparkContext
2. **API Focus**: SparkContext focuses on RDD operations, while SparkSession focuses on DataFrame/Dataset/SQL operations
3. **Evolution**: SparkSession represents the modern Spark programming model
4. **Convenience**: SparkSession provides more integrated functionality and is generally easier to work with
5. **Multiple Instances**: You can have multiple SparkSessions but only one SparkContext per JVM

In modern Spark applications (2.0 and later), you typically create a SparkSession and access the SparkContext through it when needed for RDD operations. This gives you the best of both worlds - structured data processing with DataFrames and direct access to RDDs when necessary.

## Data Architecture Layers
These three abstractions represent different ways to organize and work with data in Apache Spark, each with increasing levels of structure and optimization.

1. **RDD (Base Layer)**
   - The foundational distributed data structure in Spark
   - Provides fault tolerance and distributed computation model
   - When you execute DataFrame or Table operations, they're ultimately compiled down to RDD operations

2. **DataFrame (Mid Layer)**
   - Built on top of RDDs but adds a schema and columnar format
   - Under the hood, a DataFrame is essentially an RDD of Row objects with a schema
   - The Catalyst optimizer works with this layer to optimize query execution
   - When you call `df.rdd`, you're accessing the underlying RDD representation

3. **Table (Top Layer)**
   - A logical abstraction on top of DataFrames
   - Tables register DataFrames in a catalog with metadata
   - When you query a table with SQL, it's translated to DataFrame operations, which are then translated to RDD operations

## Evidence in Implementation

You can see this relationship in how data flows through the system:

1. When you execute a DataFrame operation, the query planner converts it to an optimized physical plan
2. This physical plan consists of RDD transformations
3. You can observe this by examining the execution plan:

```python
df = spark.createDataFrame([(1, "Alice"), (2, "Bob")], ["id", "name"])
df.filter(df.id > 1).explain(True)  # Shows the logical and physical plans
```

This layered architecture allows Spark to provide high-level, user-friendly APIs (DataFrames and SQL) while maintaining the flexibility and power of the core RDD model for distributed computation.

## RDD (Resilient Distributed Dataset)

RDDs are the most fundamental data structure in Spark - a distributed collection of elements that can be processed in parallel. RDDs are collections of objects similar to a list in Python; the difference is that RDD is computed on several processes scattered across multiple physical servers, also called nodes in a cluster, while a Python collection lives and processes in just one process. PySpark RDDs are immutable in nature meaning, once RDDs are created you cannot modify them. When we apply transformations on RDD, PySpark creates a new RDD and maintains the RDD Lineage.

**Key characteristics:**
- Low-level API with fine-grained control
- No predefined schema or structure
- Type-safe (compile-time type checking)
- Immutable and fault-tolerant

### Helpfule Links:
- [Apache Spark: RDD Programming Guide](https://spark.apache.org/docs/latest/rdd-programming-guide.html)
- [Apache Spark: RDD Pyspark API](https://spark.apache.org/docs/latest/api/python/reference/api/pyspark.RDD.html#pyspark.RDD)
- [What is an RDDs?](https://sparkbyexamples.com/pyspark-rdd/)
- [Practice RDD Code/Notebook](https://github.com/ajlinhard/PythonExplorer/blob/main/Spark/RDD_Basics.ipynb)

**Ways to create RDDs:**
```python
# From collection
rdd = sc.parallelize([1, 2, 3, 4, 5])

# From external storage
rdd = sc.textFile("hdfs://path/to/file.txt")

# From another RDD
filtered_rdd = rdd.filter(lambda x: x > 2)

# From Hadoop InputFormat
rdd = sc.hadoopFile("hdfs://path/to/file", "org.apache.hadoop.mapred.TextInputFormat")
```

## DataFrame

DataFrames are distributed collections of data organized into named columns, similar to tables in a relational database.

**Key characteristics:**
- Higher-level API with more optimization
- Schema-based with column names and types
- Catalyst optimizer for query optimization
- Better for structured/semi-structured data

**Ways to create DataFrames:**
```python
# From RDD
schema = StructType([StructField("id", IntegerType()), StructField("name", StringType())])
df = spark.createDataFrame(rdd, schema)

# From external data sources
df = spark.read.csv("path/to/file.csv", header=True, inferSchema=True)
df = spark.read.json("path/to/file.json")
df = spark.read.parquet("path/to/file.parquet")

# From Pandas DataFrame
pandas_df = pd.DataFrame({"id": [1, 2, 3], "name": ["Alice", "Bob", "Charlie"]})
spark_df = spark.createDataFrame(pandas_df)

# From literal data
df = spark.createDataFrame([(1, "Alice"), (2, "Bob")], ["id", "name"])
```

## Table

Tables in Spark are logical abstractions on top of DataFrames, managed through the catalog for persistent data.

**Key characteristics:**
- Registered in a catalog/metastore
- Can be queried with SQL
- Can be temporary or permanent
- Can have additional metadata like partitioning info

**Ways to create Tables:**
```python
# From DataFrame
df.write.saveAsTable("my_table")
df.createOrReplaceTempView("temp_table")  # Temporary table
df.createGlobalTempView("global_temp_table")  # Global temporary table

# Using SQL
spark.sql("CREATE TABLE table_name (id INT, name STRING) USING parquet")
spark.sql("CREATE TABLE table_name AS SELECT * FROM another_table")

# From external data source
spark.sql("CREATE TABLE ext_table USING csv OPTIONS (path 'path/to/file.csv', header 'true')")
```

## Key Differences

1. **Structure level**: RDD (unstructured) → DataFrame (structured) → Table (structured with metadata)
2. **API type**: RDD (functional) → DataFrame (domain-specific) → Table (SQL)
3. **Optimization**: More structure allows more optimization, with Tables benefiting from the most Catalyst optimization
4. **Persistence**: RDDs and DataFrames are transient by default; Tables can be made persistent

Would you like me to explain any specific aspect in more detail?
---
# Important Error Help

## Mismatch Python Versions for Driver  vs. Worker
This error occurs when you are trying to run PySpark, but your Driver(your code/execution environment) and the pyspark worker(whatever is running your spark system) are different. This error typically happens when you have multiple Python versions installed on your system and PySpark is picking up different versions for the driver and workers. Setting these environment variables ensures both components use the same Python interpreter.

```text
Py4JJavaError: An error occurred while calling o84.saveAsTable.
: org.apache.spark.SparkException: Job aborted due to stage failure: Task 1 in stage 2.0 failed 1 times, most recent failure: Lost task 1.0 in stage 2.0 (TID 3) (Andrew-PC.myfiosgateway.com executor driver): org.apache.spark.api.python.PythonException: Traceback (most recent call last):
  File "C:\Users\dalej\Documents\AllSpark\spark-3.5.1\python\lib\pyspark.zip\pyspark\worker.py", line 1100, in main
pyspark.errors.exceptions.base.PySparkRuntimeError: [PYTHON_VERSION_MISMATCH] Python in worker has different version (3, 8) than that in driver 3.11, PySpark cannot run with different minor versions.
Please check environment variables PYSPARK_PYTHON and PYSPARK_DRIVER_PYTHON are correctly set.
```

You can fix it manually:
```Bash
# For Windows
set PYSPARK_PYTHON=python3.11
set PYSPARK_DRIVER_PYTHON=python3.11

# For Linux/Mac
export PYSPARK_PYTHON=python3.11
export PYSPARK_DRIVER_PYTHON=python3.11
```

Or try and fix it before the script, but your machines local variables can override this depending if you have the set and execution method.
```python
import os
os.environ['PYSPARK_PYTHON'] = 'python3.11'
os.environ['PYSPARK_DRIVER_PYTHON'] = 'python3.11'

# Then create your SparkSession
```
