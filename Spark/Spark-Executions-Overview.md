# Spark Executions Overview:
When running Spark as a data processing engine you are going to hear 3 main charateristics about its execution:
1. [Lazy Evolution/Evaluation[(#Lazy-Evolution-Evaluation)
2. [In-Memory Processing](In-Memory-Processing)
3. [Fault Tolerance](Fault-Tolerance)
While each of these truely are wonderful characteristics of Spark, like any tool they have there issues and nuances. This article will cover some of the issues of each characteristics.
<br>
Before we begin, please not 2 high-level major helpers.
1. You can examine the Spark execution plan at any point in a process with [explain()](https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.DataFrame.explain.html) to see what's happening:
```python
df_new = df.drop("problem_column")
df_new.explain(True)  # Shows the full logical and physical plan
```
2. Without needing to understand exactly what is happening you can use [cache()](https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.DataFrame.cache.html) at a point in the process you know works. This forces Spark to materialize the dataframe. Trade-off is more memory usage, but can fix execution plan finickiness or issues.
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


## In-Memory Processing
The power of the In-memory execution plans of Spark lead to the fast run times. The method saves on the disk I/O of other systems like OLTP databases or Hadoop/Hive. There is a reason for this though. Spark is designed for fast big data processing/batch workloads. So, in certain senarios the other data engines will beat spark:
OLTP databases:
When there are many threads/users interacting with data frequently (100s or 1000s+ of users) with small transactions, then In-memory processing is overkill. The OLTP database are optimized for these quick and frequent transactions, especially singular record seeks, updates, or inserts. The data page/storage structures and indexing features these systems have that Spark does not, allow them to better handle these interactions. Correct, spark does not have indexing, but does have partitioning, bucketing, and other structures optimize smaller data interactions: (see this article)

## Fault Tolerance
The processing of data in Spark is fault tolerent, however, do not confuse this will Spark being ACID compliant. Within a job itself Spark is "ACID compliant" in a way. If you are trying to update or insert incremental data from many separate jobs at the same moment in Spark, then the data may not turn out as you expect. This can be navigated with techniques and other packages like Delta Lake, but requires care and unit testing to confirm success. Other options managed Spark platforms like Databricks or Snowflake handle more ACID like transactions for you.
