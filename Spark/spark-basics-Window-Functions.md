# Spark Window Functions
Here is a PySpark Window functions cheatsheet with detailed examples and a reference table.I've created a comprehensive PySpark Window functions cheat sheet that includes:

**Key Sections:**
- **Basic Setup** - Imports and SparkSession creation
- **Window Specifications** - How to define window frames and partitions
- **Common Patterns** - Ranking, aggregates, and analytic functions with examples
- **Frame Specifications** - Different types of window frames (rows vs range)
- **Practical Examples** - Real-world scenarios like top N per group, running totals, moving averages
- **Reference Table** - Complete list of window functions organized by category
- **Performance Tips** - Best practices for optimization
- **Common Patterns** - Deduplication, time series analysis, and outlier detection

The reference table categorizes all window functions into three main types:
1. **Ranking Functions** - row_number(), rank(), dense_rank(), etc.
2. **Aggregate Functions** - sum(), avg(), count(), min(), max(), etc.  
3. **Analytic Functions** - lead(), lag(), first(), last(), nth_value()

- [Common Issues](#Common-Issues)

Each function includes practical examples showing the syntax and common use cases. The cheat sheet also covers important concepts like frame specifications (rows vs range) and performance optimization techniques.

---
# PySpark Window Functions Cheat Sheet

## Basic Setup and Imports

```python
from pyspark.sql import SparkSession
from pyspark.sql.window import Window
from pyspark.sql.functions import *

# Create SparkSession
spark = SparkSession.builder.appName("Window Functions").getOrCreate()
```

## Window Specification Basics

```python
# Basic window specification
window = Window.partitionBy("department").orderBy("salary")

# Window with frame specification
window_frame = Window.partitionBy("department") \
    .orderBy("salary") \
    .rowsBetween(Window.unboundedPreceding, Window.currentRow)

# Range-based window
range_window = Window.partitionBy("department") \
    .orderBy("salary") \
    .rangeBetween(-1000, 1000)
```

## Common Window Function Patterns

### Ranking Functions

```python
# Row number - unique sequential number
df.withColumn("row_num", row_number().over(window))

# Rank - same values get same rank, gaps in sequence
df.withColumn("rank", rank().over(window))

# Dense rank - same values get same rank, no gaps
df.withColumn("dense_rank", dense_rank().over(window))

# Percent rank - relative rank as percentage
df.withColumn("percent_rank", percent_rank().over(window))

# Ntile - divide into n buckets
df.withColumn("quartile", ntile(4).over(window))
```

### Aggregate Functions

```python
# Running sum
df.withColumn("running_sum", sum("salary").over(window_frame))

# Running average
df.withColumn("running_avg", avg("salary").over(window_frame))

# Running count
df.withColumn("running_count", count("*").over(window_frame))

# Running min/max
df.withColumn("running_min", min("salary").over(window_frame))
df.withColumn("running_max", max("salary").over(window_frame))
```

### Analytic Functions

```python
# Lead - value from next row
df.withColumn("next_salary", lead("salary", 1).over(window))

# Lag - value from previous row
df.withColumn("prev_salary", lag("salary", 1).over(window))

# First value in window
df.withColumn("first_salary", first("salary").over(window))

# Last value in window
df.withColumn("last_salary", last("salary").over(window))

# Nth value
df.withColumn("second_highest", nth_value("salary", 2).over(window))
```

## Frame Specifications

```python
# Unbounded frames
Window.unboundedPreceding  # Start of partition
Window.unboundedFollowing  # End of partition
Window.currentRow          # Current row

# Row-based frames (physical rows)
rows_window = Window.partitionBy("dept") \
    .orderBy("salary") \
    .rowsBetween(-2, 2)  # 2 rows before to 2 rows after

# Range-based frames (logical range based on order column)
range_window = Window.partitionBy("dept") \
    .orderBy("salary") \
    .rangeBetween(-1000, 1000)  # Salary within ±1000
```

## Practical Examples

### Top N per Group

```python
# Get top 3 highest paid employees per department
top_n_window = Window.partitionBy("department").orderBy(desc("salary"))

result = df.withColumn("rank", row_number().over(top_n_window)) \
    .filter(col("rank") <= 3)
```

### Running Totals and Moving Averages

```python
# Running total
running_total_window = Window.partitionBy("account_id") \
    .orderBy("transaction_date") \
    .rowsBetween(Window.unboundedPreceding, Window.currentRow)

df.withColumn("running_balance", 
              sum("amount").over(running_total_window))

# 7-day moving average
moving_avg_window = Window.partitionBy("stock_symbol") \
    .orderBy("date") \
    .rowsBetween(-6, 0)

df.withColumn("moving_avg_7d", 
              avg("price").over(moving_avg_window))
```

### Percentage of Total

```python
# Calculate percentage of department total
dept_total_window = Window.partitionBy("department")

df.withColumn("dept_total", sum("salary").over(dept_total_window)) \
  .withColumn("pct_of_dept", (col("salary") / col("dept_total")) * 100)
```

### Gap Analysis

```python
# Find gaps between consecutive values
gap_window = Window.partitionBy("customer_id").orderBy("order_date")

df.withColumn("prev_order_date", lag("order_date").over(gap_window)) \
  .withColumn("days_since_last_order", 
              datediff("order_date", "prev_order_date"))
```

## Window Functions Reference Table

| Function Category | Function | Description | Example Usage |
|------------------|----------|-------------|---------------|
| **Ranking** | `row_number()` | Unique sequential number for each row | `row_number().over(window)` |
| | `rank()` | Rank with gaps for ties | `rank().over(window)` |
| | `dense_rank()` | Rank without gaps for ties | `dense_rank().over(window)` |
| | `percent_rank()` | Relative rank as percentage (0-1) | `percent_rank().over(window)` |
| | `ntile(n)` | Divide rows into n buckets | `ntile(4).over(window)` |
| **Aggregate** | `sum()` | Running/windowed sum | `sum("col").over(window)` |
| | `avg()` | Running/windowed average | `avg("col").over(window)` |
| | `count()` | Running/windowed count | `count("*").over(window)` |
| | `min()` | Running/windowed minimum | `min("col").over(window)` |
| | `max()` | Running/windowed maximum | `max("col").over(window)` |
| | `stddev()` | Standard deviation in window | `stddev("col").over(window)` |
| | `variance()` | Variance in window | `variance("col").over(window)` |
| **Analytic** | `lead(col, n)` | Value from n rows ahead | `lead("col", 1).over(window)` |
| | `lag(col, n)` | Value from n rows behind | `lag("col", 1).over(window)` |
| | `first(col)` | First value in window | `first("col").over(window)` |
| | `last(col)` | Last value in window | `last("col").over(window)` |
| | `nth_value(col, n)` | Nth value in window | `nth_value("col", 2).over(window)` |

## Frame Types Summary

| Frame Type | Syntax | Description |
|------------|--------|-------------|
| **Rows Frame** | `.rowsBetween(start, end)` | Physical number of rows |
| **Range Frame** | `.rangeBetween(start, end)` | Logical range based on ORDER BY column |
| **Unbounded** | `Window.unboundedPreceding` | From start of partition |
| | `Window.unboundedFollowing` | To end of partition |
| | `Window.currentRow` | Current row only |

## Performance Tips

```python
# Cache frequently used windows
common_window = Window.partitionBy("department").orderBy("salary")
# Reuse this window spec across multiple operations

# Avoid unnecessary sorting when possible
# Use partitionBy without orderBy for simple aggregations
simple_window = Window.partitionBy("department")

# Use appropriate frame bounds
# Default frame is RANGE UNBOUNDED PRECEDING AND CURRENT ROW
# Specify explicit bounds when different behavior is needed

# Consider using repartition() before window operations for better performance
df.repartition("department").withColumn("rank", rank().over(window))
```

## Common Patterns

### Deduplication

```python
# Remove duplicates keeping the latest record
dedup_window = Window.partitionBy("id").orderBy(desc("timestamp"))
df.withColumn("rn", row_number().over(dedup_window)) \
  .filter(col("rn") == 1) \
  .drop("rn")
```

### Time Series Analysis

```python
# Calculate period-over-period growth
growth_window = Window.partitionBy("product_id").orderBy("month")
df.withColumn("prev_sales", lag("sales").over(growth_window)) \
  .withColumn("growth_rate", 
              (col("sales") - col("prev_sales")) / col("prev_sales") * 100)
```

### Outlier Detection

```python
# Identify outliers using standard deviation
stats_window = Window.partitionBy("category")
df.withColumn("avg_price", avg("price").over(stats_window)) \
  .withColumn("stddev_price", stddev("price").over(stats_window)) \
  .withColumn("is_outlier", 
              abs(col("price") - col("avg_price")) > 2 * col("stddev_price"))
```

---
# Common Issues
## Using Multiple Windows Functions in Same withColumn Chain
When working with a set of windows functions and you want to chain a column created by a windows function into another windows function (Common in time-series data), you cannot create both columns in the same withColumn chain. This is different from stacking column hygiene operations for pyspark withColumn chains
**Example Hygiene withColumn Stack**
```python
df_coast = df.withColumn("latitude_block", round(col("location.latitude"), 4)) \
    .withColumn("region", when(col("latitude_block").between(40.7, 40.8), "East Coast") \
        .when(col("latitude_block").between(40.6, 40.7), "Central") \
        .when(col("latitude_block").between(40.5, 40.6), "West Coast") \
        .otherwise("Out-of-Bounds")) 

df_coast.show(truncate=False)
```

**Bad Code:**
```python
from pyspark.sql.functions import *
from pyspark.sql.window import Window

time_window = Window.partitionBy("sensor_id").orderBy("timestamp").rowsBetween(-11,0) # a rolling hours

df_timestats = df.withColumn("rolliing_avg_temp", avg(col("readings.temperature")).over(time_window)) \
    .withColumn("lat_change", col("location.latitude") - lag("location.latitude").over(Window.partitionBy("sensor_id").orderBy("timestamp"))) \
    .withColumn("lat_change_hr", col("lat_change").over(time_window))
```
**Error (First Line is Most Important**
```
AnalysisException: [UNSUPPORTED_EXPR_FOR_WINDOW] Expression "lat_change" not supported within a window function.;
Project [sensor_id#31, timestamp#32, location#33, readings#34, status#35, minute_15_bucket#211, rolliing_avg_temp#285, lat_change#295, lat_change_hr#308]
+- Project [sensor_id#31, timestamp#32, location#33, readings#34, status#35, minute_15_bucket#211, rolliing_avg_temp#285, lat_change#295, lat_change_hr#308, lat_change_hr#308]
   +- Window [lat_change#295 windowspecdefinition(sensor_id#31, timestamp#32 ASC NULLS FIRST, specifiedwindowframe(RowFrame, -11, currentrow$())) AS lat_change_hr#308], [sensor_id#31], [timestamp#32 ASC NULLS FIRST]
      +- Project [sensor_id#31, timestamp#32, location#33, readings#34, status#35, minute_15_bucket#211, rolliing_avg_temp#285, lat_change#295]
         +- Project [sensor_id#31, timestamp#32, location#33, readings#34, status#35, minute_15_bucket#211, rolliing_avg_temp#285, lat_change#295]
            +- Project [sensor_id#31, timestamp#32, location#33, readings#34, status#35, minute_15_bucket#211, rolliing_avg_temp#285, _w0#298, _we0#299, (location#33.latitude - _we0#299) AS lat_change#295]
               +- Window [lag(_w0#298, -1, null) windowspecdefinition(sensor_id#31, timestamp#32 ASC NULLS FIRST, specifiedwindowframe(RowFrame, -1, -1)) AS _we0#299], [sensor_id#31], [timestamp#32 ASC NULLS FIRST]
                  +- Project [sensor_id#31, timestamp#32, location#33, readings#34, status#35, minute_15_bucket#211, rolliing_avg_temp#285, location#33.latitude AS _w0#298]
                     +- Project [sensor_id#31, timestamp#32, location#33, readings#34, status#35, minute_15_bucket#211, rolliing_avg_temp#285]
                        +- Project [sensor_id#31, timestamp#32, location#33, readings#34, status#35, minute_15_bucket#211, _w0#287, rolliing_avg_temp#285, rolliing_avg_temp#285]
                           +- Window [avg(_w0#287) windowspecdefinition(sensor_id#31, timestamp#32 ASC NULLS FIRST, specifiedwindowframe(RowFrame, -11, currentrow$())) AS rolliing_avg_temp#285], [sensor_id#31], [timestamp#32 ASC NULLS FIRST]
                              +- Project [sensor_id#31, timestamp#32, location#33, readings#34, status#35, minute_15_bucket#211, readings#34[temperature] AS _w0#287]
                                 +- Project [sensor_id#31, timestamp#32, location#33, readings#34, status#35, cast(from_unixtime((FLOOR((cast(unix_timestamp(timestamp#32, yyyy-MM-dd HH:mm:ss, Some(America/New_York), false) as double) / cast(900 as double))) * cast(900 as bigint)), yyyy-MM-dd HH:mm:ss, Some(America/New_York)) as timestamp) AS minute_15_bucket#211]
                                    +- LogicalRDD [sensor_id#31, timestamp#32, location#33, readings#34, status#35], false
```
