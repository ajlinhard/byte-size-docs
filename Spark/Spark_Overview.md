

# Overview Links:
1. [Great Architecture Overview](https://www.youtube.com/watch?v=jDkLiqlyQaY)
2. [In-depth Architecture](https://www.youtube.com/watch?v=iXVIPQEGZ9Y)


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

### Resilient Distributed Dataset (RDD)


### Spark Context vs. Spark Sessions
A SparkContext and a SparkSession are both fundamental components in Apache Spark, but they serve different purposes and were introduced in different versions of Spark. Let me explain the key differences:

## SparkContext
SparkContext is the older, original entry point for Spark functionality:

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
