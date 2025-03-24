# Spark Date and DateTime Operations Cheatsheet

I'll create a comprehensive guide for working with dates and datetimes in Apache Spark, showing common operations and conversions.

Here's a breakdown of key date and datetime operations in Spark:

## Converting Strings to Date/DateTime

- **Default format (yyyy-MM-dd)**:
  ```python
  df = df.withColumn("date_column", F.to_date("string_column"))
  ```

- **Custom format**:
  ```python
  df = df.withColumn("date_column", F.to_date("string_column", "MM/dd/yyyy"))
  ```

- **UTC format to timestamp**:
  ```python
  df = df.withColumn("timestamp_column", 
                    F.to_timestamp("utc_string", "yyyy-MM-dd'T'HH:mm:ss.SSS'Z'"))
  ```

## Date Extraction

- **Components**: 
  ```python
  df = df.withColumn("year", F.year("date"))
         .withColumn("month", F.month("date"))
         .withColumn("day", F.dayofmonth("date"))
         .withColumn("weekday", F.dayofweek("date"))
  ```

## Date Arithmetic

- **Add/subtract days**:
  ```python
  df = df.withColumn("tomorrow", F.date_add("date", 1))
         .withColumn("yesterday", F.date_sub("date", 1))
  ```

- **Add/subtract months**:
  ```python
  df = df.withColumn("next_month", F.add_months("date", 1))
         .withColumn("last_month", F.add_months("date", -1))
  ```

- **Add intervals to timestamp**:
  ```python
  df = df.withColumn("plus_hour", F.expr("timestamp + interval 1 hour"))
         .withColumn("complex", F.expr("timestamp + interval 2 days 3 hours"))
  ```

## Date Differences

- **Between dates (days)**:
  ```python
  df = df.withColumn("days_between", F.datediff("end_date", "start_date"))
  ```

- **Between dates (months)**:
  ```python
  df = df.withColumn("months_between", F.months_between("end_date", "start_date"))
  ```

## Formatting

- **To string**:
  ```python
  df = df.withColumn("formatted", F.date_format("date", "dd-MMM-yyyy"))
  ```

## Time Zone Operations

- **Convert from UTC**:
  ```python
  df = df.withColumn("local_time", 
                    F.from_utc_timestamp("utc_timestamp", "America/Los_Angeles"))
  ```

- **Convert to UTC**:
  ```python
  df = df.withColumn("utc_time", 
                    F.to_utc_timestamp("local_timestamp", "America/New_York"))
  ```

The artifact I've created contains a full working example with many more operations, including:
- Working with current date/time
- Truncating dates/times to specific units
- Window functions with dates
- Handling null dates
- Date filtering techniques

You can refer to the artifact for complete code examples and more complex scenarios.
