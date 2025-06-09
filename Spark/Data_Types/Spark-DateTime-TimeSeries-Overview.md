# Spark Time Series Data
Here is a PySpark time series cheat sheet for you based on common patterns and operations.I've created a comprehensive PySpark time series cheat sheet that covers the most common operations you'll need when working with time-based data. The cheat sheet includes:

**Key sections covered:**
- Basic setup and date/time parsing
- Date extraction and manipulation
- Time-based filtering and querying
- Time series aggregations (daily, monthly, weekly, hourly)
- Window functions for rolling calculations
- Time bucketing and resampling
- Gap detection and data quality checks
- Time series joins with tolerance
- Performance optimization techniques
- Common calculations like moving averages and percentage changes
- Handling irregular time series data

The examples are practical and ready to use in your PySpark applications. Each section includes multiple approaches to solve common time series problems, from basic date parsing to advanced window functions and performance optimizations.

Is there any specific time series operation or use case you'd like me to expand on or add to the cheat sheet?
---
# Code Examples:
# PySpark Time Series Data Cheat Sheet

## Basic Setup and Imports

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
from pyspark.sql.window import Window

# Create SparkSession
spark = SparkSession.builder \
    .appName("TimeSeries Analysis") \
    .getOrCreate()
```

## Date/Time Data Types and Parsing

```python
# Common timestamp formats
df = spark.createDataFrame([
    ("2023-01-15 10:30:00", "2023-01-15", "10:30:00"),
    ("2023-02-20 14:45:30", "2023-02-20", "14:45:30")
], ["timestamp_str", "date_str", "time_str"])

# Parse string to timestamp
df = df.withColumn("timestamp", to_timestamp("timestamp_str", "yyyy-MM-dd HH:mm:ss"))
df = df.withColumn("date", to_date("date_str", "yyyy-MM-dd"))

# Alternative parsing methods
df = df.withColumn("ts_unix", unix_timestamp("timestamp_str", "yyyy-MM-dd HH:mm:ss"))
df = df.withColumn("ts_from_unix", from_unixtime("ts_unix"))

# Handle different date formats
df = df.withColumn("custom_date", to_date("date_str", "dd/MM/yyyy"))
```

## Date/Time Extraction and Manipulation

```python
# Extract date/time components
df = df.withColumn("year", year("timestamp")) \
       .withColumn("month", month("timestamp")) \
       .withColumn("day", dayofmonth("timestamp")) \
       .withColumn("hour", hour("timestamp")) \
       .withColumn("minute", minute("timestamp")) \
       .withColumn("second", second("timestamp")) \
       .withColumn("dayofweek", dayofweek("timestamp")) \
       .withColumn("dayofyear", dayofyear("timestamp")) \
       .withColumn("weekofyear", weekofyear("timestamp"))

# Date arithmetic
df = df.withColumn("date_plus_30", date_add("date", 30)) \
       .withColumn("date_minus_7", date_sub("date", 7)) \
       .withColumn("months_between", months_between("date", lit("2023-01-01"))) \
       .withColumn("next_monday", next_day("date", "Monday"))

# Time zone conversions
df = df.withColumn("utc_time", to_utc_timestamp("timestamp", "PST")) \
       .withColumn("local_time", from_utc_timestamp("utc_time", "EST"))
```

## Time-based Filtering and Querying

```python
# Filter by date range
start_date = "2023-01-01"
end_date = "2023-12-31"
filtered_df = df.filter((col("date") >= start_date) & (col("date") <= end_date))

# Filter by time components
recent_data = df.filter(col("timestamp") > date_sub(current_date(), 30))
business_hours = df.filter((hour("timestamp") >= 9) & (hour("timestamp") <= 17))
weekdays_only = df.filter(dayofweek("timestamp").between(2, 6))  # Monday=2, Sunday=1

# Dynamic date filtering
df.filter(col("date") >= date_sub(current_date(), 90))  # Last 90 days
df.filter(year("timestamp") == 2023)  # Specific year
df.filter(month("timestamp").isin([6, 7, 8]))  # Summer months
```

## Time Series Aggregations

```python
# Group by time periods
daily_agg = df.groupBy(to_date("timestamp").alias("date")) \
              .agg(count("*").alias("count"), 
                   avg("value").alias("avg_value"),
                   sum("amount").alias("total_amount"))

# Monthly aggregations
monthly_agg = df.groupBy(year("timestamp").alias("year"), 
                        month("timestamp").alias("month")) \
                .agg(sum("revenue").alias("monthly_revenue"))

# Weekly aggregations
weekly_agg = df.groupBy(weekofyear("timestamp").alias("week"), 
                       year("timestamp").alias("year")) \
               .agg(avg("price").alias("avg_weekly_price"))

# Hourly patterns
hourly_pattern = df.groupBy(hour("timestamp").alias("hour")) \
                   .agg(count("*").alias("transactions_per_hour")) \
                   .orderBy("hour")
```

## Window Functions for Time Series

```python
# Define time-based window
time_window = Window.partitionBy("category") \
                   .orderBy("timestamp") \
                   .rowsBetween(-6, 0)  # 7-day rolling window

# Rolling aggregations
df = df.withColumn("rolling_avg", avg("value").over(time_window)) \
       .withColumn("rolling_sum", sum("amount").over(time_window)) \
       .withColumn("rolling_count", count("*").over(time_window)) \
       .withColumn("rolling_max", max("value").over(time_window)) \
       .withColumn("rolling_min", min("value").over(time_window))

# Lag and lead operations
df = df.withColumn("prev_value", lag("value", 1).over(Window.partitionBy("id").orderBy("timestamp"))) \
       .withColumn("next_value", lead("value", 1).over(Window.partitionBy("id").orderBy("timestamp"))) \
       .withColumn("value_change", col("value") - col("prev_value"))

# Cumulative calculations
df = df.withColumn("cumulative_sum", sum("amount").over(Window.partitionBy("category").orderBy("timestamp").rowsBetween(Window.unboundedPreceding, 0))) \
       .withColumn("running_count", count("*").over(Window.partitionBy("category").orderBy("timestamp").rowsBetween(Window.unboundedPreceding, 0)))
```

## Time Series Resampling and Bucketing

```python
# Time bucketing
df = df.withColumn("hour_bucket", 
                   from_unixtime(
                       floor(unix_timestamp("timestamp") / 3600) * 3600
                   ).cast("timestamp"))

# 15-minute intervals
df = df.withColumn("minute_15_bucket", 
                   from_unixtime(
                       floor(unix_timestamp("timestamp") / (15 * 60)) * (15 * 60)
                   ).cast("timestamp"))

# Daily buckets
df = df.withColumn("daily_bucket", to_date("timestamp"))

# Custom time windows using window function
windowed_df = df.groupBy(
    window("timestamp", "1 hour"),  # 1-hour windows
    "product_id"
).agg(
    sum("sales").alias("hourly_sales"),
    count("*").alias("transaction_count")
)

# Multiple window sizes
multi_window = df.select(
    "*",
    window("timestamp", "10 minutes").alias("window_10min"),
    window("timestamp", "1 hour").alias("window_1hour"),
    window("timestamp", "1 day").alias("window_1day")
)
```

## Gap Detection and Data Quality

```python
# Find missing timestamps in sequence
from pyspark.sql.functions import explode, sequence

# Generate expected time range
expected_times = spark.range(
    spark.sql("SELECT min(unix_timestamp(timestamp)) as min_ts FROM df").collect()[0][0],
    spark.sql("SELECT max(unix_timestamp(timestamp)) as max_ts FROM df").collect()[0][0],
    3600  # 1 hour intervals
).select(from_unixtime("id").cast("timestamp").alias("expected_timestamp"))

# Find gaps
gaps = expected_times.join(df, expected_times.expected_timestamp == df.timestamp, "left_anti")

# Detect duplicates by timestamp
duplicates = df.groupBy("timestamp", "id").count().filter("count > 1")

# Data completeness by time period
completeness = df.groupBy(to_date("timestamp").alias("date")) \
                 .agg(count("*").alias("records_per_day")) \
                 .orderBy("date")
```

## Time Series Joins and Alignment

```python
# Join two time series with tolerance
df1 = spark.createDataFrame([("2023-01-01 10:00:00", 100)], ["timestamp", "value1"])
df2 = spark.createDataFrame([("2023-01-01 10:05:00", 200)], ["timestamp", "value2"])

# Convert to Unix timestamp for tolerance-based join
df1_unix = df1.withColumn("ts_unix", unix_timestamp("timestamp"))
df2_unix = df2.withColumn("ts_unix", unix_timestamp("timestamp"))

# Join with 5-minute tolerance
tolerance = 300  # 5 minutes in seconds
joined = df1_unix.join(
    df2_unix,
    abs(df1_unix.ts_unix - df2_unix.ts_unix) <= tolerance,
    "inner"
)

# Forward fill missing values
window_spec = Window.partitionBy("id").orderBy("timestamp")
df_filled = df.withColumn("filled_value", 
                         last("value", ignorenulls=True).over(
                             window_spec.rowsBetween(Window.unboundedPreceding, 0)
                         ))
```

## Performance Optimization for Time Series

```python
# Partition by date for better performance
df.write \
  .partitionBy("year", "month") \
  .mode("overwrite") \
  .parquet("/path/to/timeseries/data")

# Optimize for time range queries
df.repartition(col("date")).write.mode("overwrite").parquet("/path/to/data")

# Cache frequently accessed time series
df.cache()

# Use broadcast for small lookup tables
broadcast_df = broadcast(small_lookup_df)
result = large_ts_df.join(broadcast_df, "key")

# Predicate pushdown for Parquet
filtered_df = spark.read.parquet("/path/to/data") \
                   .filter((col("date") >= "2023-01-01") & 
                          (col("date") <= "2023-12-31"))
```

## Common Time Series Calculations

```python
# Calculate time differences
df = df.withColumn("time_diff_seconds", 
                   col("current_timestamp").cast("long") - col("previous_timestamp").cast("long"))

# Moving averages with different windows
ma_window_7 = Window.partitionBy("symbol").orderBy("timestamp").rowsBetween(-6, 0)
ma_window_30 = Window.partitionBy("symbol").orderBy("timestamp").rowsBetween(-29, 0)

df = df.withColumn("ma_7", avg("price").over(ma_window_7)) \
       .withColumn("ma_30", avg("price").over(ma_window_30))

# Percentage change
df = df.withColumn("pct_change", 
                   (col("current_value") - col("prev_value")) / col("prev_value") * 100)

# Seasonal decomposition helper
df = df.withColumn("day_of_week", dayofweek("timestamp")) \
       .withColumn("hour_of_day", hour("timestamp")) \
       .withColumn("is_weekend", when(dayofweek("timestamp").isin([1, 7]), 1).otherwise(0))
```

## Handling Irregular Time Series

```python
# Interpolation for missing values (linear approximation)
window_spec = Window.partitionBy("id").orderBy("timestamp")

df_with_interpolation = df.withColumn("row_num", row_number().over(window_spec)) \
                          .withColumn("prev_value", lag("value").over(window_spec)) \
                          .withColumn("next_value", lead("value").over(window_spec)) \
                          .withColumn("interpolated_value", 
                                     when(col("value").isNull(), 
                                          (col("prev_value") + col("next_value")) / 2)
                                     .otherwise(col("value")))

# Downsampling high-frequency data
downsampled = df.groupBy(
    window("timestamp", "5 minutes"),
    "sensor_id"
).agg(
    avg("reading").alias("avg_reading"),
    max("reading").alias("max_reading"),
    min("reading").alias("min_reading"),
    first("reading").alias("first_reading"),
    last("reading").alias("last_reading")
)
```
