# Spark Aggregations (GroupBy)
Below is PySpark aggregations cheat sheet with a detailed table of common aggregation functions.I've created a comprehensive PySpark aggregations cheat sheet that includes:

**Key Features:**
- **Detailed function table** with 19+ common aggregation functions, their purposes, input parameters, and output data types
- **Percentile and quantile functions** in a separate table
- **Practical examples** for each major category:
  - Basic aggregations
  - Group by operations
  - Window functions
  - Advanced patterns with conditional logic
  - Custom aggregation functions (UDAF)

**The table covers essential functions like:**
- Basic stats: `count()`, `sum()`, `avg()`, `min()`, `max()`
- Distribution metrics: `stddev()`, `variance()`, `skewness()`, `kurtosis()`
- Collection functions: `collect_list()`, `collect_set()`
- Statistical relationships: `corr()`, `covar_samp()`, `covar_pop()`
- Performance-optimized: `approx_count_distinct()`, `percentile_approx()`

**Additional sections include:**
- Performance tips for large datasets
- Advanced aggregation patterns with `cube()`, `rollup()`, and `pivot()`
- Custom aggregation functions using pandas UDFs
- Window function examples with moving averages and running totals

This cheat sheet should serve as a quick reference for most PySpark aggregation needs, from simple counts to complex statistical analysis.
---
# PySpark Aggregations Cheat Sheet

## Basic Setup

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *

spark = SparkSession.builder.appName("Aggregations").getOrCreate()
```

## Common Aggregation Functions

| Function | Purpose | Input Parameters | Output Data Type | Example |
|----------|---------|------------------|------------------|---------|
| `count()` | Count non-null values | Column or "*" | LongType | `df.agg(count("*"))` |
| `countDistinct()` | Count distinct values | Column(s) | LongType | `df.agg(countDistinct("name"))` |
| `sum()` | Sum of values | Numeric column | Same as input | `df.agg(sum("amount"))` |
| `avg()` / `mean()` | Average of values | Numeric column | DoubleType | `df.agg(avg("salary"))` |
| `min()` | Minimum value | Any comparable column | Same as input | `df.agg(min("date"))` |
| `max()` | Maximum value | Any comparable column | Same as input | `df.agg(max("score"))` |
| `first()` | First non-null value | Any column, optional ignoreNulls | Same as input | `df.agg(first("name"))` |
| `last()` | Last non-null value | Any column, optional ignoreNulls | Same as input | `df.agg(last("status"))` |
| `collect_list()` | Collect values into array | Any column | ArrayType | `df.agg(collect_list("tags"))` |
| `collect_set()` | Collect distinct values into array | Any column | ArrayType | `df.agg(collect_set("category"))` |
| `stddev()` / `stddev_samp()` | Sample standard deviation | Numeric column | DoubleType | `df.agg(stddev("price"))` |
| `stddev_pop()` | Population standard deviation | Numeric column | DoubleType | `df.agg(stddev_pop("price"))` |
| `variance()` / `var_samp()` | Sample variance | Numeric column | DoubleType | `df.agg(variance("amount"))` |
| `var_pop()` | Population variance | Numeric column | DoubleType | `df.agg(var_pop("amount"))` |
| `skewness()` | Skewness of values | Numeric column | DoubleType | `df.agg(skewness("distribution"))` |
| `kurtosis()` | Kurtosis of values | Numeric column | DoubleType | `df.agg(kurtosis("distribution"))` |
| `corr()` | Correlation coefficient | Two numeric columns | DoubleType | `df.agg(corr("x", "y"))` |
| `covar_samp()` | Sample covariance | Two numeric columns | DoubleType | `df.agg(covar_samp("x", "y"))` |
| `covar_pop()` | Population covariance | Two numeric columns | DoubleType | `df.agg(covar_pop("x", "y"))` |
| `approx_count_distinct()` | Approximate distinct count | Column, optional rsd | LongType | `df.agg(approx_count_distinct("id"))` |
| `sumDistinct()` | Sum of distinct values | Numeric column | Same as input | `df.agg(sumDistinct("value"))` |

## Percentile and Quantile Functions

| Function | Purpose | Input Parameters | Output Data Type | Example |
|----------|---------|------------------|------------------|---------|
| `percentile_approx()` | Approximate percentile | Column, percentile (0-1), optional accuracy | DoubleType | `df.agg(percentile_approx("salary", 0.5))` |
| `expr("percentile(col, 0.5)")` | Exact percentile (via SQL) | Column, percentile | Same as input | `df.agg(expr("percentile(age, 0.25)"))` |

## Basic Aggregation Examples

```python
# Sample DataFrame
data = [
    ("Alice", "Engineering", 75000, 28),
    ("Bob", "Engineering", 80000, 32),
    ("Charlie", "Marketing", 60000, 25),
    ("Diana", "Marketing", 65000, 29),
    ("Eve", "Engineering", 90000, 35)
]
df = spark.createDataFrame(data, ["name", "department", "salary", "age"])

# Simple aggregations
df.agg(
    count("*").alias("total_employees"),
    avg("salary").alias("avg_salary"),
    min("age").alias("min_age"),
    max("salary").alias("max_salary")
).show()

# Multiple aggregations on same column
df.agg(
    sum("salary").alias("total_payroll"),
    avg("salary").alias("average_salary"),
    stddev("salary").alias("salary_stddev"),
    collect_list("name").alias("all_names")
).show()
```

## Group By Aggregations

```python
# Group by single column
df.groupBy("department").agg(
    count("*").alias("employee_count"),
    avg("salary").alias("avg_salary"),
    min("salary").alias("min_salary"),
    max("salary").alias("max_salary")
).show()

# Group by multiple columns
df.groupBy("department", col("age") > 30).agg(
    count("*").alias("count"),
    avg("salary").alias("avg_salary")
).show()

# Using agg() with dictionary
df.groupBy("department").agg({
    "salary": "avg",
    "age": "max",
    "*": "count"
}).show()
```

## Window Functions with Aggregations

```python
from pyspark.sql.window import Window

# Define window specification
windowSpec = Window.partitionBy("department").orderBy("salary")

# Window aggregations
df.select(
    "*",
    row_number().over(windowSpec).alias("rank"),
    avg("salary").over(windowSpec.rowsBetween(-1, 1)).alias("moving_avg"),
    sum("salary").over(windowSpec.rangeBetween(Window.unboundedPreceding, Window.currentRow)).alias("running_total")
).show()
```

## Advanced Aggregation Patterns

```python
# Conditional aggregations
df.agg(
    sum(when(col("department") == "Engineering", col("salary")).otherwise(0)).alias("eng_total_salary"),
    count(when(col("age") > 30, 1)).alias("employees_over_30"),
    avg(when(col("department") == "Marketing", col("salary"))).alias("marketing_avg_salary")
).show()

# Aggregating arrays
array_df = df.select("department", split(col("name"), "").alias("name_chars"))
array_df.agg(
    size(collect_list("name_chars")).alias("total_arrays"),
    size(flatten(collect_list("name_chars"))).alias("total_chars")
).show()

# Statistical aggregations
df.agg(
    corr("salary", "age").alias("salary_age_correlation"),
    covar_samp("salary", "age").alias("salary_age_covariance"),
    percentile_approx("salary", 0.5).alias("median_salary"),
    skewness("salary").alias("salary_skewness"),
    kurtosis("salary").alias("salary_kurtosis")
).show()
```

## Performance Tips

```python
# Use approximate functions for large datasets
df.agg(approx_count_distinct("id")).show()  # Faster than countDistinct for large data

# Cache DataFrames when doing multiple aggregations
df.cache()
df.groupBy("department").count().show()
df.groupBy("department").avg("salary").show()

# Use collect_list() sparingly - can cause memory issues
# Consider using collect_set() if you only need unique values

# For percentiles on large datasets, use percentile_approx()
df.agg(percentile_approx("salary", [0.25, 0.5, 0.75])).show()
```

## Custom Aggregation Functions (UDAF)

```python
# Example of using pandas UDF for custom aggregation
from pyspark.sql.functions import pandas_udf
from pyspark.sql.types import DoubleType
import pandas as pd

@pandas_udf(returnType=DoubleType())
def geometric_mean(values: pd.Series) -> float:
    return values.prod() ** (1.0 / len(values))

# Use custom aggregation
df.groupBy("department").agg(
    geometric_mean("salary").alias("geo_mean_salary")
).show()
```

## Common Patterns and Best Practices

```python
# Multiple aggregations with different groupings
# Instead of multiple groupBy operations, use cube() or rollup()
df.cube("department", "age" > 30).agg(
    count("*").alias("count"),
    avg("salary").alias("avg_salary")
).show()

# Rollup for hierarchical aggregations
df.rollup("department").agg(
    count("*").alias("total_count"),
    sum("salary").alias("total_salary")
).show()

# Pivot tables
df.groupBy("department").pivot("age" > 30).agg(
    count("*").alias("count"),
    avg("salary").alias("avg_salary")
).show()
```
