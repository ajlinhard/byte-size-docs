# Spark Executions Overview:
When running Spark as a data processing engine you are going to hear 3 main charateristics about its execution:
1. [Lazy Evolution/Evaluation](#Lazy-Evolution-Evaluation)
2. [In-Memory Processing](#In-Memory-Processing)
3. [Fault Tolerance](#Fault-Tolerance)
4. [How Spark Compiles/Executed Backend](How-Spark-Compiles/Executed-Backend)
While each of these truely are wonderful characteristics of Spark, like any tool they have there issues and nuances. This article will cover some of the issues of each characteristics.

Before we begin, please not 2 high-level major helpers.
1. You can examine the Spark execution plan at any point in a process with [explain](https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.DataFrame.explain.html) to see what's happening:
```python
df_new = df.drop("problem_column")
df_new.explain(True)  # Shows the full logical and physical plan
```
2. Without needing to understand exactly what is happening you can use [cache](https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.DataFrame.cache.html) at a point in the process you know works. This forces Spark to materialize the dataframe. Trade-off is more memory usage, but can fix execution plan finickiness or issues.
```python
df_good_action_series = df_good_action_series.withColumnRenamed({"col1": "ID", "col2:"FullAddress"})
df_good_action_series = df_good_action_series.cache()
```
**Other Quick Tips**
1. Create column names upfront or as early on as possible.
2. Cast data to the correct type as early as possible.
3. After using UDFs or complex transformations cache the data set before dropping data.
4. The Medallion Architecture is helpful: Mainly with raw data save the data after basic transformations (column names, data types, lite trimming or replaces)

## Lazy Evolution/Evaluation
Lazy evaluation is the one that is brought up the most and refers to Spark not actually executing any processing of data until triggered. This allows you to build out a complex series of actions, transformations, and aggregations with no actual execution. Then when trigger an evaluation with functions like collect(), show(), count(), cache(), etc. Spark will create an optimized DAG for efficient execution on the data. This creates some of the amazing runtimes you can see in Spark. However, this can lead to issues if the change of actions is long or in particular situations/versions of spark. Below are the high-level issues, then we will cover some examples:

### Column Dependencies
Columns in Spark DataFrames can indeed be "dependent" on each other in certain scenarios, which might explain why dropping a specific column is causing your entire DataFrame to appear blank.
1. **Generated Columns**: If the column you're dropping was used to generate other columns through transformations, those derived columns might be affected.
2. **View Definitions**: If you're working with a view rather than a physical DataFrame, the view definition might depend on that column.
3. **Partitioning Column**: If you're dropping a column that's used for partitioning, it can disrupt the DataFrame structure.
4. **Join Key**: If the column is a key used in a previously performed join operation, dropping it might interfere with how Spark maintains the DataFrame internally.
5. **Column Used in Filtering**: If previous operations filtered based on this column, dropping it might cause execution plan issues.

### Issue 01: Bad Data Column dependency on CorruptData Column:
#### **Scenario:**
We are loading a data set into Spark with a bad csv format. The last column has commas in the data, but the delimiter is a single comma with no quoting. Therefore the decision is made to load the data using the option columnNameOfCorruptRecord into the column names "corrupt_val"
```python
# You can for it to read all records
from pyspark.sql.types import StructType, StructField, StringType
s_data_files_path = os.path.join(s_raw_root_path, r'Delimited\movie_titles.csv')

schema = StructType([
    StructField("col1", StringType(), True),
    StructField("col2", StringType(), True),
    StructField("col3", StringType(), True),
    StructField("corrupt_vals", StringType(), True),
])
df_movie_corrupt = spark.read \
    .option("mode", "PERMISSIVE") \
    .option("columnNameOfCorruptRecord", "corrupt_vals") \
    .option("delimiter", ",") \
    .schema(schema) \
    .csv(s_data_files_path)
df_movie_corrupt.show(10, truncate=False)
```
Then we try to fix the last column by parsing the "corrupt_vals" column ourselves, then replacing the "col3" with the new fixed column. Finally, we want to drop "col3" and look at the dataframe with show().
```python
from pyspark.sql.functions import coalesce, split
df_movie_fixed = df_movie_corrupt.withColumn('FullTitle', split(df_movie_corrupt['corrupt_vals'], ',', 3).getItem(2))
# The FullTitle column is not null for these results
df_movie_fixed.filter(df_movie_fixed.corrupt_vals.isNotNull()).show(5, truncate=False)
df_movie_fixed.filter(df_movie_fixed.col1 == 72).show(5)
df_movie_fixed.filter(df_movie_fixed.col1 == 264).show(5)
df_movie_fixed = df_movie_fixed.withColumnsRenamed({'col1':'id', 'col2':'Year'}).withColumn('TitleFixed', coalesce(col('FullTitle'),col('col3')))

df_movie_fixed_fnl = df_movie_fixed.drop('col3')
# The FullTitle column is null for these results
df_movie_fixed_fnl.show(5)
df_movie_fixed_fnl.filter(df_movie_fixed_fnl.id == 72).show(5)
df_movie_fixed_fnl.filter(df_movie_fixed_fnl.id == 264).show(5)

df_movie_fixed_fnl.filter(df_movie_fixed_fnl.FullTitle.isNotNull()).show(5, truncate=False)
```
#### **Issue:**
In this scenario, when Spark loads data with corrupt record handling options (like `mode="PERMISSIVE"` with `columnNameOfCorruptRecord="corrupt_vals"`), it creates an internal relationship between the corrupt records column and the source data parsing.

In more detail, here's what happens:
```bash
== Parsed Logical Plan ==
Filter isnotnull(FullTitle#6156)
+- Project [col1#977, col2#978, corrupt_vals#980, FullTitle#6156]
+- Project [col1#977, col2#978, col3#979, corrupt_vals#980, split_col(corrupt_vals#980, 2)#6155 AS FullTitle#6156]
+- Relation [col1#977,col2#978,col3#979,corrupt_vals#980] csv

== Analyzed Logical Plan ==
col1: string, col2: string, corrupt_vals: string, FullTitle: string Filter isnotnull(FullTitle#6156)
+- Project [col1#977, col2#978, corrupt_vals#980, FullTitle#6156]
+- Project [col1#977, col2#978, col3#979, corrupt_vals#980, split_col(corrupt_vals#980, 2)#6155 AS FullTitle#6156]
+- Relation [col1#977,col2#978,col3#979,corrupt_vals#980] csv

== Optimized Logical Plan ==
Project [col1#977, col2#978, corrupt_vals#980, pythonUDF0#6308 AS FullTitle#6156]
+- BatchEvalPython [split_col(corrupt_vals#980, 2)#6155], [pythonUDF0#6308]
+- Project [col1#977, col2#978, corrupt_vals#980]
+- Filter isnotnull(pythonUDF0#6307)
+- BatchEvalPython [split_col(corrupt_vals#980, 2)#6155], [pythonUDF0#6307] +- Project [col1#977, col2#978, corrupt_vals#980] +- Relation [col1#977,col2#978,col3#979,corrupt_vals#980] csv

== Physical Plan ==
*(2) Project [col1#977, col2#978, corrupt_vals#980, pythonUDF0#6308 AS FullTitle#6156]
+- BatchEvalPython [split_col(corrupt_vals#980, 2)#6155], [pythonUDF0#6308]
+- *(1) Project [col1#977, col2#978, corrupt_vals#980]
+- *(1) Filter isnotnull(pythonUDF0#6307)
+- BatchEvalPython [split_col(corrupt_vals#980, 2)#6155], [pythonUDF0#6307]
+- FileScan csv [col1#977,col2#978,corrupt_vals#980] Batched: false, DataFilters: [], Format: CSV, Location: InMemoryFileIndex(1 paths)[file:/F:/DataSamples/ExampleFiles/Delimited/movie_titles.csv], PartitionFilters: [], PushedFilters: [], ReadSchema: struct<col1:string,col2:string,corrupt_vals:string>
```

The execution plan clearly shows the issue that's occurring. Looking at the plan, especially the Physical Plan section, you can identify several key points that explain the problem:

1. **Column Dependency**: In the Physical Plan, notice how `FullTitle#6156` is created using a Python UDF (`pythonUDF0#6308`) which takes `corrupt_vals#980` as input. This creates a direct dependency between these columns.

2. **Schema Pruning**: At the bottom of the Physical Plan, you can see:
   ```
   FileScan csv [col1#977,col2#978,corrupt_vals#980]
   ```
   Spark has already pruned `col3#979` from the read schema, even though it's in the Parsed Logical Plan.

3. **UDF Evaluation**: The execution uses `BatchEvalPython` for the `split_col` function, which is operating on `corrupt_vals#980`. This UDF evaluation creates a complex dependency that might be affected when the execution plan changes.

4. **Filter Operation**: There's a `Filter isnotnull(pythonUDF0#6307)` operation which suggests that the plan is filtering based on non-null UDF results, potentially complicating the dependencies further.

When you subsequently modify the DataFrame structure (like dropping columns), Spark might re-optimize its execution plan. This optimization can sometimes break the chain of dependencies that track corrupt records, especially because the `corrupt_vals` column is likely linked to how Spark handles corrupted data during file reading.

#### **Solution:**
Use caching right after loading or the UDF to help - it forces Spark to materialize the corrupt records and all derived columns before you dropped `col3`, preserving their values regardless of any subsequent plan optimizations.
```python
from pyspark.sql.functions import coalesce, split
df_movie_fixed = df_movie_corrupt.withColumn('FullTitle', split(df_movie_corrupt['corrupt_vals'], ',', 3).getItem(2))
# The FullTitle column is not null for these results
df_movie_fixed.filter(df_movie_fixed.corrupt_vals.isNotNull()).show(5, truncate=False)
df_movie_fixed.filter(df_movie_fixed.col1 == 72).show(5)
df_movie_fixed.filter(df_movie_fixed.col1 == 264).show(5)
df_movie_fixed = df_movie_fixed.withColumnsRenamed({'col1':'id', 'col2':'Year'}).withColumn('TitleFixed', coalesce(col('FullTitle'),col('col3')))
# Required to remove the dependency of col3 of the corrupt_vals column used in the UDF. The .drop("col3") will cause "col3" to be removed from the initial file load.
df_movie_fixed = df_movie_fixed.cache()

df_movie_fixed_fnl = df_movie_fixed.drop('col3')
# The FullTitle column is null for these results
df_movie_fixed_fnl.show(5)
df_movie_fixed_fnl.filter(df_movie_fixed_fnl.id == 72).show(5)
df_movie_fixed_fnl.filter(df_movie_fixed_fnl.id == 264).show(5)

df_movie_fixed_fnl.filter(df_movie_fixed_fnl.FullTitle.isNotNull()).show(5, truncate=False)
```
If you're working with corrupt record handling, it's generally a good practice to:

1. Cache the DataFrame after initial loading and corrupt record handling
2. Perform any cleanup or extraction from corrupt records
3. Create a new "clean" DataFrame without the corrupt record handling dependencies
4. Unpersist the original cached DataFrame when you no longer need it

This approach gives you more predictable behavior when working with corrupt data.

---
## In-Memory Processing
The power of the In-memory execution plans of Spark lead to the fast run times. The method saves on the disk I/O of other systems like OLTP databases or Hadoop/Hive. There is a reason for this though. Spark is designed for fast big data processing/batch workloads. So, in certain senarios the other data engines will beat spark:
**OLTP databases:**
When there are many threads/users interacting with data frequently (100s or 1000s+ of users) with small transactions, then In-memory processing is overkill. The OLTP database are optimized for these quick and frequent transactions, especially singular record seeks, updates, or inserts. The data page/storage structures and indexing features these systems have that Spark does not, allow them to better handle these interactions. Correct, spark does not have indexing, but does have partitioning, bucketing, and other structures optimize smaller data interactions: ([more info this article](https://github.com/ajlinhard/byte-size-docs/blob/main/Spark/Spark-Index-Subs-Structuring-Data.md))

---
**Hadoop/Hive**
Hive is also a big data processing engine as well. Some features of Hadoop and Hive are used within Spark itself. Then main difference is these system have significantly more disk I/O than Spark, but use less memory overall. This approach results in Hadoop/Hive having longer runtimes and is part of the reason the engine fell out of favor (not an expert here so I'm sure there is more). However, a team may want to use Hive over Spark if there system Hardware has less memory(RAM). Spark can choke at certain memory levels depending on your data plus processing needs. Hive can be the answer in this system which may be designed this way for lower cost (RAM/GPU cost > Disk cost) or because its a legacy system.


## Fault Tolerance
The processing of data in Spark is fault tolerent, however, do not confuse this will Spark being ACID compliant. Within a job itself Spark is "ACID compliant" in a way. If you are trying to update or insert incremental data from many separate jobs at the same moment in Spark, then the data may not turn out as you expect. This can be navigated with techniques and other packages like Delta Lake, but requires care and unit testing to confirm success. Other options managed Spark platforms like Databricks or Snowflake handle more ACID like transactions for you.

----
#
I'll explain how Spark query executions work in both Spark SQL and Python functions, and how they're processed on the backend.

When you work with Spark, whether you're using SQL queries or DataFrame/Dataset API functions in Python, both approaches ultimately get transformed into the same underlying execution plan. Here's how it works:

## The Execution Pipeline

Both SQL queries and DataFrame operations go through similar processing stages:

1. **Query/API Parsing**: The entry point differs (SQL text vs Python function calls), but both get parsed into a logical plan

2. **Logical Plan Creation**: Both approaches create what's called a logical plan - an abstract representation of the operations to be performed 

3. **Optimization**: The logical plan undergoes optimization using Catalyst (Spark's query optimizer)

4. **Physical Plan Generation**: The optimized logical plan gets converted to a physical execution plan

5. **Code Generation**: Spark uses code generation (with Tungsten) to compile parts of the query to JVM bytecode

6. **Execution**: The physical plan is executed on the cluster

## SQL to Python or Python to SQL?

It's neither exactly. Both SQL and Python DataFrame APIs are high-level interfaces that get converted to the same intermediate representation:

- **SQL queries** are parsed by Spark's SQL parser into an Abstract Syntax Tree (AST), which is then converted to a logical plan
- **Python DataFrame operations** get translated through the PySpark API into logical plan operations

Both of these logical plans are then passed to the Catalyst optimizer and follow the same execution path afterward.

## The Role of Java/Scala

This is a key part of your question. PySpark is essentially a Python wrapper around Spark's Java/Scala core:

1. When you call Python functions or write SQL in PySpark, these commands get translated to Java/Scala calls using Py4J (a bridge between Python and Java)

2. The actual processing engine of Spark is written in Scala and runs on the JVM

3. Python UDFs (User Defined Functions) involve serialization/deserialization between Python and JVM, which can impact performance (though Arrow-based UDFs improve this)

## Example Flow

Let's trace what happens with a simple query using both approaches:

**SQL Approach**:
```python
result = spark.sql("SELECT COUNT(*) FROM my_table WHERE value > 10")
```

**DataFrame API Approach**:
```python
result = spark.table("my_table").filter("value > 10").count()
```

Both of these get converted to the same logical plan, which represents "count the rows in my_table where value > 10". The execution engine doesn't care whether this came from SQL or a DataFrame operation.

## Real-world Implications

The unified backend means:

1. Performance should be similar between SQL and DataFrame APIs for the same operations
2. Optimizations apply equally to both interfaces
3. You can mix and match approaches based on what's more readable or maintainable

According to your Hive Metastore cheat sheet, both SQL and DataFrame catalog operations (like `spark.catalog.listTables()` or `spark.sql("SHOW TABLES")`) interact with the same underlying Hive metastore client, which is written in Java.
