# Spark Datetime Manipulations
Below is a comprehensive Spark datetime manipulation cheat sheet for you, covering PySpark's datetime functions and operations. The cheat sheet includes:

**Key sections covered:**
- **Setup and basic datetime creation** - Converting strings to datetime objects
- **Current datetime functions** - Getting current timestamps and dates
- **Date/time extraction** - Extracting components like year, month, day, hour, etc.
- **Date arithmetic** - Adding/subtracting days, months, calculating differences
- **Timestamp arithmetic** - Working with intervals and timestamp calculations
- **Date formatting** - Converting dates to different string formats
- **String conversions** - Parsing various datetime string formats
- **Timezone operations** - Converting between timezones
- **Date filtering and ranges** - Filtering data by date criteria
- **Window functions** - Using datetime in window operations for analytics
- **Date truncation** - Truncating dates to year/month/quarter levels
- **Null handling** - Dealing with missing date values
- **Age calculations** - Computing age from birthdates
- **Performance tips** - Best practices for date operations
- **Common patterns** - Business days, seasons, first/last day of month
- **Troubleshooting** - Handling mixed formats and validation

This cheat sheet should serve as a quick reference for most datetime manipulation tasks in Spark. Each section includes practical examples that you can adapt to your specific use cases.
---
# Spark DateTime Manipulation Cheat Sheet

## Setup and Imports

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
import datetime

spark = SparkSession.builder.appName("DateTime").getOrCreate()
```

## Creating DateTime DataFrames

```python
# Sample data with different datetime formats
data = [
    ("2023-01-15 10:30:45", "2023-01-15", "10:30:45"),
    ("2023-02-20 14:15:30", "2023-02-20", "14:15:30"),
    ("2023-03-25 09:45:00", "2023-03-25", "09:45:00")
]

df = spark.createDataFrame(data, ["timestamp_str", "date_str", "time_str"])

# Convert string to timestamp/date
df = df.withColumn("timestamp_col", to_timestamp("timestamp_str", "yyyy-MM-dd HH:mm:ss")) \
      .withColumn("date_col", to_date("date_str", "yyyy-MM-dd"))
```

## Current DateTime Functions

```python
# Current datetime functions
df = df.withColumn("current_timestamp", current_timestamp()) \
      .withColumn("current_date", current_date()) \
      .withColumn("current_timezone", lit(spark.conf.get("spark.sql.session.timeZone")))

# Unix timestamp
df = df.withColumn("unix_timestamp", unix_timestamp()) \
      .withColumn("unix_from_string", unix_timestamp("timestamp_str", "yyyy-MM-dd HH:mm:ss"))
```

## Date/Time Extraction

```python
# Extract components from datetime
df = df.withColumn("year", year("timestamp_col")) \
      .withColumn("month", month("timestamp_col")) \
      .withColumn("day", dayofmonth("timestamp_col")) \
      .withColumn("hour", hour("timestamp_col")) \
      .withColumn("minute", minute("timestamp_col")) \
      .withColumn("second", second("timestamp_col")) \
      .withColumn("weekday", dayofweek("timestamp_col")) \
      .withColumn("day_of_year", dayofyear("timestamp_col")) \
      .withColumn("week_of_year", weekofyear("timestamp_col")) \
      .withColumn("quarter", quarter("timestamp_col"))
```

## Date Arithmetic

```python
# Add/subtract intervals
df = df.withColumn("add_days", date_add("date_col", 30)) \
      .withColumn("subtract_days", date_sub("date_col", 15)) \
      .withColumn("add_months", add_months("date_col", 6)) \
      .withColumn("next_day", next_day("date_col", "Monday")) \
      .withColumn("last_day", last_day("date_col"))

# Date difference
df = df.withColumn("days_diff", datediff("current_date", "date_col")) \
      .withColumn("months_between", months_between("current_date", "date_col"))
```

## Timestamp Arithmetic

```python
# Add intervals to timestamps
df = df.withColumn("add_seconds", col("timestamp_col") + expr("INTERVAL 3600 SECONDS")) \
      .withColumn("add_minutes", col("timestamp_col") + expr("INTERVAL 30 MINUTES")) \
      .withColumn("add_hours", col("timestamp_col") + expr("INTERVAL 5 HOURS")) \
      .withColumn("add_days_ts", col("timestamp_col") + expr("INTERVAL 10 DAYS"))

# Using date_add with timestamps (converts to date first)
df = df.withColumn("timestamp_plus_days", 
                   to_timestamp(date_add(to_date("timestamp_col"), 7).cast("string") + " " + 
                               date_format("timestamp_col", "HH:mm:ss")))
```

## Date Formatting

```python
# Format dates and timestamps
df = df.withColumn("formatted_date", date_format("date_col", "dd/MM/yyyy")) \
      .withColumn("formatted_timestamp", date_format("timestamp_col", "yyyy-MM-dd HH:mm:ss")) \
      .withColumn("month_name", date_format("date_col", "MMMM")) \
      .withColumn("day_name", date_format("date_col", "EEEE")) \
      .withColumn("iso_date", date_format("date_col", "yyyy-MM-dd'T'HH:mm:ss'Z'"))
```

## String to DateTime Conversions

```python
# Various string formats to timestamp
formats_df = spark.createDataFrame([
    ("2023-01-15T10:30:45Z",),
    ("01/15/2023 10:30:45 AM",),
    ("15-Jan-2023 22:30:45",),
    ("2023.01.15 10.30.45",)
], ["datetime_string"])

formats_df = formats_df.withColumn("iso_format", to_timestamp("datetime_string", "yyyy-MM-dd'T'HH:mm:ss'Z'")) \
                      .withColumn("us_format", to_timestamp("datetime_string", "MM/dd/yyyy hh:mm:ss a")) \
                      .withColumn("custom_format", to_timestamp("datetime_string", "dd-MMM-yyyy HH:mm:ss")) \
                      .withColumn("dot_format", to_timestamp("datetime_string", "yyyy.MM.dd HH.mm.ss"))
```

## Timezone Operations

```python
# Convert between timezones
df = df.withColumn("utc_timestamp", to_utc_timestamp("timestamp_col", "PST")) \
      .withColumn("local_timestamp", from_utc_timestamp("timestamp_col", "EST")) \
      .withColumn("timezone_offset", 
                  (unix_timestamp("timestamp_col") - unix_timestamp(to_utc_timestamp("timestamp_col", "PST"))) / 3600)
```

## Date Ranges and Filtering

```python
# Filter by date ranges
start_date = "2023-01-01"
end_date = "2023-12-31"

filtered_df = df.filter(col("date_col").between(start_date, end_date))

# Filter by relative dates
recent_df = df.filter(col("date_col") >= date_sub(current_date(), 30))  # Last 30 days
future_df = df.filter(col("date_col") > current_date())  # Future dates

# Filter by day of week
weekday_df = df.filter(dayofweek("date_col").isin([2, 3, 4, 5, 6]))  # Monday to Friday
```

## Window Functions with DateTime

```python
from pyspark.sql.window import Window

# Create sample data for window operations
sales_data = [
    ("2023-01-01", 100), ("2023-01-02", 150), ("2023-01-03", 200),
    ("2023-02-01", 120), ("2023-02-02", 180), ("2023-02-03", 250)
]
sales_df = spark.createDataFrame(sales_data, ["date", "sales"]) \
               .withColumn("date", to_date("date"))

# Window specifications
daily_window = Window.orderBy("date")
monthly_window = Window.partitionBy(month("date")).orderBy("date")

# Running totals and moving averages
sales_df = sales_df.withColumn("running_total", sum("sales").over(daily_window)) \
                  .withColumn("prev_day_sales", lag("sales", 1).over(daily_window)) \
                  .withColumn("next_day_sales", lead("sales", 1).over(daily_window)) \
                  .withColumn("3_day_avg", avg("sales").over(daily_window.rowsBetween(-1, 1))) \
                  .withColumn("monthly_rank", row_number().over(monthly_window))
```

## Date Truncation

```python
# Truncate dates to different levels
df = df.withColumn("trunc_year", trunc("date_col", "year")) \
      .withColumn("trunc_month", trunc("date_col", "month")) \
      .withColumn("trunc_quarter", trunc("date_col", "quarter")) \
      .withColumn("trunc_week", trunc("date_col", "week"))

# Date truncation for timestamps
df = df.withColumn("hour_trunc", date_trunc("hour", "timestamp_col")) \
      .withColumn("day_trunc", date_trunc("day", "timestamp_col")) \
      .withColumn("month_trunc", date_trunc("month", "timestamp_col"))
```

## Working with Null Dates

```python
# Handle null dates
df_with_nulls = df.withColumn("nullable_date", 
                             when(col("day") % 2 == 0, col("date_col")).otherwise(lit(None)))

# Fill null dates
df_filled = df_with_nulls.withColumn("filled_date", 
                                   coalesce("nullable_date", current_date()))

# Check for null dates
df_checked = df_with_nulls.withColumn("is_null_date", col("nullable_date").isNull())
```

## Age Calculations

```python
# Calculate age from birthdate
birthdate_data = [("1990-05-15",), ("1985-12-03",), ("2000-08-20",)]
birthdate_df = spark.createDataFrame(birthdate_data, ["birthdate"]) \
                   .withColumn("birthdate", to_date("birthdate"))

# Age in years
birthdate_df = birthdate_df.withColumn("age_years", 
                                     floor(datediff(current_date(), "birthdate") / 365.25))

# Age in days, months
birthdate_df = birthdate_df.withColumn("age_days", datediff(current_date(), "birthdate")) \
                          .withColumn("age_months", months_between(current_date(), "birthdate"))
```

## Performance Tips

```python
# Partitioning by date columns
df.write.partitionBy("year", "month").parquet("output_path")

# Pushdown predicates for date filters
# Use column references instead of string literals when possible
df.filter(col("date_col") >= lit("2023-01-01"))  # Better than string comparison

# Cache frequently accessed date computations
df_with_features = df.withColumn("year_month", date_format("date_col", "yyyy-MM")).cache()
```

## Common Date Patterns

```python
# Business days calculation (excluding weekends)
def business_days_between(start_col, end_col):
    return (datediff(end_col, start_col) - 
            2 * floor(datediff(end_col, start_col) / 7) -
            when(dayofweek(start_col) == 1, 1).otherwise(0) -
            when(dayofweek(end_col) == 7, 1).otherwise(0))

df = df.withColumn("business_days", business_days_between("date_col", current_date()))

# First/Last day of month
df = df.withColumn("first_day_month", trunc("date_col", "month")) \
      .withColumn("last_day_month", last_day("date_col"))

# Season calculation
df = df.withColumn("season", 
    when((month("date_col") >= 3) & (month("date_col") <= 5), "Spring")
    .when((month("date_col") >= 6) & (month("date_col") <= 8), "Summer")
    .when((month("date_col") >= 9) & (month("date_col") <= 11), "Fall")
    .otherwise("Winter"))
```

## Troubleshooting Common Issues

```python
# Handle different date formats in same column
mixed_formats_df = spark.createDataFrame([
    ("2023-01-15",), ("01/15/2023",), ("15-Jan-2023",)
], ["date_string"])

# Try multiple format patterns
mixed_formats_df = mixed_formats_df.withColumn("parsed_date",
    coalesce(
        to_date("date_string", "yyyy-MM-dd"),
        to_date("date_string", "MM/dd/yyyy"),
        to_date("date_string", "dd-MMM-yyyy")
    ))

# Validate date ranges
df = df.withColumn("is_valid_date", 
    (col("date_col") >= lit("1900-01-01")) & 
    (col("date_col") <= current_date()))
```
