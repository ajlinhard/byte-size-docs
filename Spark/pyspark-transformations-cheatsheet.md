# PySpark Transformations Cheatsheet

## Contents
- Transformation items
    - ltrim rtrim
    - substring
    - patindex or pattern matching
    - cast/convert
    - standard deviation, count, count-distinct, average
    - over statements for using row_number() or dense_rank()
    - Apply a python function to a spark column

---
# Important Concept of Column Objects vs. Dataframe-tied column references
When working with Spark DataFrames, there are indeed two main ways to reference columns: the direct dot notation (`df.column_name`) and the `col()` function approach. The difference in usage comes down to the context and capabilities of each method.
```Python
# Both work: The first is a DataFrame-tied column references, the "col('column_name')" is a column object. The second one is more reliable.
df_movie_corrupt.filter(df_movie_corrupt.corrupt_vals.isNotNull()).show(10, truncate=False)
df_movie_corrupt.filter(col('corrupt_vals').isNotNull()).show(10, truncate=False)
```

### Dot Notation (`df.column_name`)

The dot notation is convenient for simple operations, especially in filters and selects. For example:

```python
df_movie_corrupt.filter(df_movie_corrupt.corrupt_vals.isNotNull())
```

This approach works well because:
- It's concise and readable for simple expressions
- It explicitly ties the column to its parent DataFrame
- It works well with column operations that don't require complex transformations

### Column Function (`col('column_name')`)

The `col()` function approach is more versatile and is required in many contexts:

```python
df_movie_fixed = df_movie_corrupt.withColumn('FullTitle', split_col_udf(col('corrupt_vals'), lit(2)))
```

This approach is necessary when:
- You're using complex transformations or UDFs
- Working with functions that expect column objects rather than expressions
- Performing operations where column independence from a specific DataFrame is important
- Building complex expressions with multiple columns and literals

### Why the Difference?

The main reasons for these differences are:

1. **Type of operation**: Some operations in Spark's API were designed to work with column references while others work with column expressions.

2. **DataFrame context**: The dot notation inherently ties the column to a specific DataFrame, which works for filtering that same DataFrame but can be problematic when applying transformations that should be DataFrame-agnostic.

3. **Function composition**: When building complex expressions with multiple operations, the `col()` function provides more flexibility for combining with other functions like `lit()`, `concat()`, etc.

4. **Historical API evolution**: As PySpark evolved, different approaches to column references were implemented at different times.

In your example, the UDF-based transformation in `withColumn()` requires column objects rather than DataFrame-tied column references, which is why `col('corrupt_vals')` is used instead of `df_movie_corrupt.corrupt_vals`.

For maximum flexibility, many Spark developers prefer consistently using the `col()` function approach, especially in complex data pipelines.
---
## String Functions

### LTRIM & RTRIM

**PySpark Python API:**
```python
from pyspark.sql.functions import ltrim, rtrim, trim

# Left trim
df = df.withColumn("trimmed_left", ltrim(df["column"]))

# Right trim
df = df.withColumn("trimmed_right", rtrim(df["column"]))

# Both sides trim
df = df.withColumn("trimmed_both", trim(df["column"]))
```

**Spark SQL:**
```python
# Left trim
spark.sql("SELECT LTRIM(column) as trimmed_left FROM table")

# Right trim
spark.sql("SELECT RTRIM(column) as trimmed_right FROM table")

# Both sides trim
spark.sql("SELECT TRIM(column) as trimmed_both FROM table")
```

### SUBSTRING

**PySpark Python API:**
```python
from pyspark.sql.functions import substring

# Extract characters from position 3, length 5
df = df.withColumn("substring_col", substring(df["column"], 3, 5))
```

**Spark SQL:**
```python
# Note: In SQL, positions are 1-based
spark.sql("SELECT SUBSTRING(column, 3, 5) as substring_col FROM table")
```

## Pattern Matching

**PySpark Python API:**
```python
from pyspark.sql.functions import regexp_extract, locate, instr

# Extract the first occurrence of a pattern (like PATINDEX)
df = df.withColumn("pattern_pos", locate("pattern", df["column"]))

# Alternative using instr
df = df.withColumn("pattern_pos", instr(df["column"], "pattern"))

# Extract pattern using regex
df = df.withColumn("pattern_match", regexp_extract(df["column"], "regex_pattern", 0))

# Filter rows with pattern
df = df.filter(df["column"].rlike("regex_pattern"))
```

**Spark SQL:**
```python
# Position of first occurrence (like PATINDEX)
spark.sql("SELECT INSTR(column, 'pattern') as pattern_pos FROM table")

# Extract using regex
spark.sql("SELECT REGEXP_EXTRACT(column, 'regex_pattern', 0) as pattern_match FROM table")

# Filter with pattern
spark.sql("SELECT * FROM table WHERE column RLIKE 'regex_pattern'")
```

## Type Conversion

**PySpark Python API:**
```python
from pyspark.sql.functions import col, cast
from pyspark.sql.types import IntegerType, DoubleType, StringType, DateType

# Cast to integer
df = df.withColumn("int_col", col("column").cast(IntegerType()))

# Cast to double
df = df.withColumn("double_col", col("column").cast(DoubleType()))

# Cast to string
df = df.withColumn("string_col", col("column").cast(StringType()))

# Cast to date
df = df.withColumn("date_col", col("column").cast(DateType()))
```

**Spark SQL:**
```python
# Cast to integer
spark.sql("SELECT CAST(column AS INT) as int_col FROM table")

# Cast to double
spark.sql("SELECT CAST(column AS DOUBLE) as double_col FROM table")

# Cast to string
spark.sql("SELECT CAST(column AS STRING) as string_col FROM table")

# Cast to date
spark.sql("SELECT CAST(column AS DATE) as date_col FROM table")
```

## Aggregate Functions

**PySpark Python API:**
```python
from pyspark.sql.functions import stddev, count, countDistinct, avg

# Standard deviation
df = df.agg(stddev("column").alias("std_dev"))

# Count
df = df.agg(count("column").alias("count_col"))

# Count distinct
df = df.agg(countDistinct("column").alias("distinct_count"))

# Average
df = df.agg(avg("column").alias("avg_col"))

# Multiple aggregations
result = df.agg(
    stddev("column").alias("std_dev"),
    count("column").alias("count_col"),
    countDistinct("column").alias("distinct_count"),
    avg("column").alias("avg_col")
)
```

**Spark SQL:**
```python
# Standard deviation
spark.sql("SELECT STDDEV(column) as std_dev FROM table")

# Count
spark.sql("SELECT COUNT(column) as count_col FROM table")

# Count distinct
spark.sql("SELECT COUNT(DISTINCT column) as distinct_count FROM table")

# Average
spark.sql("SELECT AVG(column) as avg_col FROM table")

# Multiple aggregations
spark.sql("""
    SELECT 
        STDDEV(column) as std_dev,
        COUNT(column) as count_col,
        COUNT(DISTINCT column) as distinct_count,
        AVG(column) as avg_col
    FROM table
""")
```

## Window Functions

**PySpark Python API:**
```python
from pyspark.sql.functions import row_number, dense_rank
from pyspark.sql.window import Window

# Define window specification
window_spec = Window.partitionBy("department").orderBy("salary")

# Add row number
df = df.withColumn("row_num", row_number().over(window_spec))

# Add dense rank
df = df.withColumn("dense_rank_val", dense_rank().over(window_spec))

# Multiple window functions
df = df.withColumn("row_num", row_number().over(window_spec)) \
       .withColumn("dense_rank_val", dense_rank().over(window_spec))
```

**Spark SQL:**
```python
# Row number
spark.sql("""
    SELECT 
        *,
        ROW_NUMBER() OVER (PARTITION BY department ORDER BY salary) as row_num
    FROM table
""")

# Dense rank
spark.sql("""
    SELECT 
        *,
        DENSE_RANK() OVER (PARTITION BY department ORDER BY salary) as dense_rank_val
    FROM table
""")

# Both row number and dense rank
spark.sql("""
    SELECT 
        *,
        ROW_NUMBER() OVER (PARTITION BY department ORDER BY salary) as row_num,
        DENSE_RANK() OVER (PARTITION BY department ORDER BY salary) as dense_rank_val
    FROM table
""")
```

## Apply Python Function to Spark Column

**PySpark Python API:**
```python
from pyspark.sql.functions import udf
from pyspark.sql.types import StringType, IntegerType

# Define a Python function
def my_function(x):
    # Your custom logic here
    return x.upper() if x else None

# Convert to UDF (User Defined Function)
my_udf = udf(my_function, StringType())

# Apply UDF to column
df = df.withColumn("transformed_col", my_udf(df["column"]))

# Pandas UDF (Vectorized UDF) - more efficient for numerical operations
from pyspark.sql.functions import pandas_udf
from pyspark.sql.types import DoubleType

@pandas_udf(DoubleType())
def pandas_my_function(s):
    # Process pandas Series
    return s * 2

# Apply pandas UDF
df = df.withColumn("doubled_col", pandas_my_function(df["numeric_column"]))
```

**Spark SQL:**
```python
# Register UDF for use in SQL
spark.udf.register("my_sql_udf", my_function, StringType())

# Use in SQL query
spark.sql("SELECT my_sql_udf(column) as transformed_col FROM table")

# Register pandas UDF
spark.udf.register("pandas_double", pandas_my_function, DoubleType())

# Use pandas UDF in SQL
spark.sql("SELECT pandas_double(numeric_column) as doubled_col FROM table")
```
