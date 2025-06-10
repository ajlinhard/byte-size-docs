# PySpark Math Functions Cheatsheet

## Quick Reference Table - Basic Math Functions

| Function | Purpose | Example | Usage |
|----------|---------|---------|-------|
| `F.abs(col)` | Absolute value | `F.abs(F.col("value"))` | `df.select(F.abs("value"))` |
| `F.round(col, n)` | Round to n decimals | `F.round(F.col("price"), 2)` | `df.select(F.round("price", 2))` |
| `F.ceil(col)` | Round up | `F.ceil(F.col("value"))` | `df.select(F.ceil("value"))` |
| `F.floor(col)` | Round down | `F.floor(F.col("value"))` | `df.select(F.floor("value"))` |
| `F.sqrt(col)` | Square root | `F.sqrt(F.col("area"))` | `df.select(F.sqrt("area"))` |
| `F.pow(col, n)` | Power | `F.pow(F.col("base"), 2)` | `df.select(F.pow("base", 2))` |
| `F.exp(col)` | Exponential (e^x) | `F.exp(F.col("rate"))` | `df.select(F.exp("rate"))` |
| `F.log(col)` | Natural logarithm | `F.log(F.col("value"))` | `df.select(F.log("value"))` |
| `F.log10(col)` | Base-10 logarithm | `F.log10(F.col("value"))` | `df.select(F.log10("value"))` |
| `F.greatest(*cols)` | Maximum of columns | `F.greatest("col1", "col2")` | `df.select(F.greatest("a", "b"))` |
| `F.least(*cols)` | Minimum of columns | `F.least("col1", "col2")` | `df.select(F.least("a", "b"))` |

## Quick Reference Table - Trigonometric Functions

| Function | Purpose | Example | Usage |
|----------|---------|---------|-------|
| `F.sin(col)` | Sine | `F.sin(F.col("angle"))` | `df.select(F.sin("angle"))` |
| `F.cos(col)` | Cosine | `F.cos(F.col("angle"))` | `df.select(F.cos("angle"))` |
| `F.tan(col)` | Tangent | `F.tan(F.col("angle"))` | `df.select(F.tan("angle"))` |
| `F.asin(col)` | Arcsine | `F.asin(F.col("value"))` | `df.select(F.asin("value"))` |
| `F.acos(col)` | Arccosine | `F.acos(F.col("value"))` | `df.select(F.acos("value"))` |
| `F.atan(col)` | Arctangent | `F.atan(F.col("value"))` | `df.select(F.atan("value"))` |
| `F.atan2(y, x)` | Two-arg arctangent | `F.atan2("y", "x")` | `df.select(F.atan2("y", "x"))` |
| `F.degrees(col)` | Radians to degrees | `F.degrees(F.col("radians"))` | `df.select(F.degrees("radians"))` |
| `F.radians(col)` | Degrees to radians | `F.radians(F.col("degrees"))` | `df.select(F.radians("degrees"))` |

## Quick Reference Table - Aggregate Functions

| Function | Purpose | Example | Usage |
|----------|---------|---------|-------|
| `F.sum(col)` | Sum of column | `F.sum("sales")` | `df.agg(F.sum("sales"))` |
| `F.avg(col)` | Average | `F.avg("price")` | `df.agg(F.avg("price"))` |
| `F.mean(col)` | Mean (same as avg) | `F.mean("value")` | `df.agg(F.mean("value"))` |
| `F.min(col)` | Minimum | `F.min("age")` | `df.agg(F.min("age"))` |
| `F.max(col)` | Maximum | `F.max("salary")` | `df.agg(F.max("salary"))` |
| `F.count(col)` | Count non-null | `F.count("id")` | `df.agg(F.count("id"))` |
| `F.countDistinct(col)` | Count unique | `F.countDistinct("category")` | `df.agg(F.countDistinct("category"))` |
| `F.stddev(col)` | Standard deviation | `F.stddev("score")` | `df.agg(F.stddev("score"))` |
| `F.variance(col)` | Variance | `F.variance("value")` | `df.agg(F.variance("value"))` |
| `F.skewness(col)` | Skewness | `F.skewness("distribution")` | `df.agg(F.skewness("dist"))` |
| `F.kurtosis(col)` | Kurtosis | `F.kurtosis("distribution")` | `df.agg(F.kurtosis("dist"))` |

## Quick Reference Table - Window Functions

| Function | Purpose | Example | Usage |
|----------|---------|---------|-------|
| `F.row_number()` | Row number | `F.row_number().over(window)` | Ranking within partition |
| `F.rank()` | Rank with gaps | `F.rank().over(window)` | Standard ranking |
| `F.dense_rank()` | Rank without gaps | `F.dense_rank().over(window)` | Dense ranking |
| `F.percent_rank()` | Percentage rank | `F.percent_rank().over(window)` | Percentile ranking |
| `F.lag(col, n)` | Previous row value | `F.lag("price", 1).over(window)` | Access previous row |
| `F.lead(col, n)` | Next row value | `F.lead("price", 1).over(window)` | Access next row |
| `F.first(col)` | First value in window | `F.first("value").over(window)` | First in partition |
| `F.last(col)` | Last value in window | `F.last("value").over(window)` | Last in partition |

## Code Examples

### Basic Setup and Data Creation

```python
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import *
from pyspark.sql.window import Window
import math

# Initialize Spark session
spark = SparkSession.builder \
    .appName("PySpark Math Functions") \
    .getOrCreate()

# Create sample DataFrame
data = [
    (1, 10.5, 25.0, 100, "A"),
    (2, -15.3, 36.0, 200, "B"),
    (3, 8.7, 49.0, 150, "A"),
    (4, 22.1, 64.0, 300, "B"),
    (5, -5.2, 81.0, 250, "A"),
    (6, 18.9, 16.0, 180, "B"),
    (7, 12.4, 9.0, 220, "A"),
    (8, -8.1, 4.0, 160, "B")
]

schema = StructType([
    StructField("id", IntegerType(), True),
    StructField("value", DoubleType(), True),
    StructField("square", DoubleType(), True),
    StructField("amount", IntegerType(), True),
    StructField("category", StringType(), True)
])

df = spark.createDataFrame(data, schema)
print("Sample DataFrame:")
df.show()
```

### Basic Math Functions

```python
# Basic mathematical operations
print("Basic Math Functions:")

# Absolute value, rounding, ceiling, floor
result = df.select(
    F.col("id"),
    F.col("value"),
    F.abs(F.col("value")).alias("abs_value"),
    F.round(F.col("value"), 1).alias("rounded"),
    F.ceil(F.col("value")).alias("ceiling"),
    F.floor(F.col("value")).alias("floor")
)
result.show()

# Square root, power, exponential, logarithm
print("\nAdvanced Math Functions:")
math_result = df.select(
    F.col("id"),
    F.col("square"),
    F.sqrt(F.col("square")).alias("sqrt"),
    F.pow(F.col("value"), 2).alias("value_squared"),
    F.exp(F.col("value") / 10).alias("exponential"),
    F.log(F.abs(F.col("value"))).alias("natural_log"),
    F.log10(F.abs(F.col("value"))).alias("log_base_10")
)
math_result.show()

# Greatest and least functions
print("\nGreatest and Least:")
comparison_result = df.select(
    F.col("id"),
    F.col("value"),
    F.col("amount"),
    F.greatest(F.col("value"), F.col("amount")).alias("greatest"),
    F.least(F.col("value"), F.col("amount")).alias("least")
)
comparison_result.show()
```

### Trigonometric Functions

```python
# Create DataFrame with angles
angle_data = [
    (1, 0.0),
    (2, math.pi/6),    # 30 degrees
    (3, math.pi/4),    # 45 degrees
    (4, math.pi/3),    # 60 degrees
    (5, math.pi/2),    # 90 degrees
    (6, math.pi),      # 180 degrees
]

angle_schema = StructType([
    StructField("id", IntegerType(), True),
    StructField("radians", DoubleType(), True)
])

angle_df = spark.createDataFrame(angle_data, angle_schema)

print("Trigonometric Functions:")
trig_result = angle_df.select(
    F.col("id"),
    F.col("radians"),
    F.degrees(F.col("radians")).alias("degrees"),
    F.sin(F.col("radians")).alias("sine"),
    F.cos(F.col("radians")).alias("cosine"),
    F.tan(F.col("radians")).alias("tangent")
)
trig_result.show()

# Inverse trigonometric functions
print("\nInverse Trigonometric Functions:")
# Create data for inverse functions (values between -1 and 1 for asin/acos)
inverse_data = [(i, i * 0.2) for i in range(-5, 6)]
inverse_schema = StructType([
    StructField("id", IntegerType(), True),
    StructField("value", DoubleType(), True)
])

inverse_df = spark.createDataFrame(inverse_data, inverse_schema)
inverse_result = inverse_df.select(
    F.col("id"),
    F.col("value"),
    F.asin(F.col("value")).alias("arcsine"),
    F.acos(F.abs(F.col("value"))).alias("arccosine"),  # abs to ensure valid domain
    F.atan(F.col("value")).alias("arctangent"),
    F.degrees(F.atan(F.col("value"))).alias("atan_degrees")
)
inverse_result.show()
```

### Aggregate Functions

```python
print("Aggregate Functions:")

# Basic aggregations
basic_agg = df.agg(
    F.sum("amount").alias("total_amount"),
    F.avg("value").alias("avg_value"),
    F.min("value").alias("min_value"),
    F.max("value").alias("max_value"),
    F.count("id").alias("count"),
    F.countDistinct("category").alias("distinct_categories")
)
basic_agg.show()

# Statistical aggregations
print("\nStatistical Aggregations:")
stats_agg = df.agg(
    F.stddev("value").alias("std_dev"),
    F.variance("value").alias("variance"),
    F.skewness("value").alias("skewness"),
    F.kurtosis("value").alias("kurtosis")
)
stats_agg.show()

# Group by aggregations
print("\nGroup By Aggregations:")
grouped_agg = df.groupBy("category").agg(
    F.sum("amount").alias("total_amount"),
    F.avg("value").alias("avg_value"),
    F.stddev("value").alias("std_dev"),
    F.min("value").alias("min_value"),
    F.max("value").alias("max_value"),
    F.count("id").alias("count")
)
grouped_agg.show()

# Multiple aggregations on same column
print("\nMultiple Aggregations:")
multi_agg = df.agg(
    F.expr("percentile_approx(value, 0.25)").alias("q1"),
    F.expr("percentile_approx(value, 0.5)").alias("median"),
    F.expr("percentile_approx(value, 0.75)").alias("q3"),
    F.expr("percentile_approx(value, 0.9)").alias("p90"),
    F.expr("percentile_approx(value, 0.95)").alias("p95")
)
multi_agg.show()
```

### Window Functions

```python
from pyspark.sql.window import Window

print("Window Functions:")

# Define window specifications
window_spec = Window.partitionBy("category").orderBy("value")
window_all = Window.orderBy("value")

# Ranking functions
print("\nRanking Functions:")
ranking_result = df.select(
    F.col("*"),
    F.row_number().over(window_spec).alias("row_num_by_category"),
    F.rank().over(window_spec).alias("rank_by_category"),
    F.dense_rank().over(window_spec).alias("dense_rank_by_category"),
    F.percent_rank().over(window_spec).alias("percent_rank"),
    F.rank().over(window_all).alias("overall_rank")
)
ranking_result.show()

# Lag and Lead functions
print("\nLag and Lead Functions:")
lag_lead_result = df.select(
    F.col("*"),
    F.lag("value", 1).over(window_spec).alias("prev_value"),
    F.lead("value", 1).over(window_spec).alias("next_value"),
    (F.col("value") - F.lag("value", 1).over(window_spec)).alias("value_diff")
)
lag_lead_result.show()

# Rolling window calculations
print("\nRolling Window Calculations:")
rolling_window = Window.partitionBy("category").orderBy("id").rowsBetween(-2, 0)

rolling_result = df.select(
    F.col("*"),
    F.avg("value").over(rolling_window).alias("rolling_avg_3"),
    F.sum("amount").over(rolling_window).alias("rolling_sum_3"),
    F.max("value").over(rolling_window).alias("rolling_max_3")
)
rolling_result.show()
```

### Advanced Mathematical Operations

```python
print("Advanced Mathematical Operations:")

# Complex mathematical expressions
advanced_math = df.select(
    F.col("id"),
    F.col("value"),
    F.col("amount"),
    # Compound calculations
    (F.pow(F.col("value"), 2) + F.sqrt(F.abs(F.col("amount")))).alias("complex_calc"),
    # Trigonometric calculation
    (F.sin(F.col("value")) * F.cos(F.col("value"))).alias("sin_cos_product"),
    # Logarithmic scaling
    F.log(F.col("amount") + 1).alias("log_scaled_amount"),
    # Normalization (z-score like)
    ((F.col("value") - F.lit(8.7)) / F.lit(12.5)).alias("normalized_value")
)
advanced_math.show()

# Conditional mathematical operations
print("\nConditional Mathematical Operations:")
conditional_math = df.select(
    F.col("*"),
    F.when(F.col("value") > 0, F.sqrt(F.col("value")))
     .otherwise(F.sqrt(F.abs(F.col("value"))) * -1).alias("conditional_sqrt"),
    F.when(F.col("amount") > 200, F.log(F.col("amount")))
     .otherwise(F.col("amount") / 100.0).alias("conditional_transform")
)
conditional_math.show()

# Financial calculations
print("\nFinancial Calculations:")
# Add some financial data
financial_data = [
    (1, 1000.0, 0.05, 12, 5),  # principal, rate, periods_per_year, years
    (2, 2000.0, 0.04, 12, 3),
    (3, 1500.0, 0.06, 4, 10),
    (4, 5000.0, 0.03, 1, 20)
]

financial_schema = StructType([
    StructField("id", IntegerType(), True),
    StructField("principal", DoubleType(), True),
    StructField("annual_rate", DoubleType(), True),
    StructField("periods_per_year", IntegerType(), True),
    StructField("years", IntegerType(), True)
])

financial_df = spark.createDataFrame(financial_data, financial_schema)

# Compound interest calculation: A = P(1 + r/n)^(nt)
compound_interest = financial_df.select(
    F.col("*"),
    (F.col("principal") * 
     F.pow(1 + (F.col("annual_rate") / F.col("periods_per_year")), 
           F.col("periods_per_year") * F.col("years"))).alias("compound_amount"),
    # Simple interest for comparison
    (F.col("principal") * (1 + F.col("annual_rate") * F.col("years"))).alias("simple_amount")
)
compound_interest.show()
```

### Statistical Analysis

```python
print("Statistical Analysis:")

# Generate more data for statistical analysis
import random
random.seed(42)

stat_data = [(i, random.gauss(50, 15), random.choice(['A', 'B', 'C'])) 
             for i in range(1, 101)]

stat_schema = StructType([
    StructField("id", IntegerType(), True),
    StructField("score", DoubleType(), True),
    StructField("group", StringType(), True)
])

stat_df = spark.createDataFrame(stat_data, stat_schema)

# Comprehensive statistical summary
print("\nComprehensive Statistical Summary:")
stat_summary = stat_df.agg(
    F.count("score").alias("count"),
    F.mean("score").alias("mean"),
    F.stddev("score").alias("std_dev"),
    F.variance("score").alias("variance"),
    F.min("score").alias("min"),
    F.max("score").alias("max"),
    F.skewness("score").alias("skewness"),
    F.kurtosis("score").alias("kurtosis"),
    F.expr("percentile_approx(score, 0.25)").alias("q1"),
    F.expr("percentile_approx(score, 0.5)").alias("median"),
    F.expr("percentile_approx(score, 0.75)").alias("q3")
)
stat_summary.show()

# Group-wise statistics
print("\nGroup-wise Statistics:")
group_stats = stat_df.groupBy("group").agg(
    F.count("score").alias("count"),
    F.mean("score").alias("mean"),
    F.stddev("score").alias("std_dev"),
    F.min("score").alias("min"),
    F.max("score").alias("max"),
    F.expr("percentile_approx(score, 0.5)").alias("median")
)
group_stats.show()

# Correlation analysis (requires pairing data)
print("\nCorrelation Analysis:")
# Create correlated data
corr_data = [(i, i * 2 + random.gauss(0, 5), i * -1.5 + random.gauss(0, 3)) 
             for i in range(1, 51)]

corr_schema = StructType([
    StructField("x", IntegerType(), True),
    StructField("y1", DoubleType(), True),
    StructField("y2", DoubleType(), True)
])

corr_df = spark.createDataFrame(corr_data, corr_schema)

# Calculate correlation
correlation_x_y1 = corr_df.agg(F.corr("x", "y1").alias("corr_x_y1")).collect()[0][0]
correlation_x_y2 = corr_df.agg(F.corr("x", "y2").alias("corr_x_y2")).collect()[0][0]
correlation_y1_y2 = corr_df.agg(F.corr("y1", "y2").alias("corr_y1_y2")).collect()[0][0]

print(f"Correlation x vs y1: {correlation_x_y1:.4f}")
print(f"Correlation x vs y2: {correlation_x_y2:.4f}")
print(f"Correlation y1 vs y2: {correlation_y1_y2:.4f}")
```

### Time Series Analysis

```python
from datetime import datetime, timedelta

print("Time Series Analysis:")

# Create time series data
start_date = datetime(2024, 1, 1)
ts_data = []
for i in range(30):
    date = start_date + timedelta(days=i)
    value = 100 + i * 2 + random.gauss(0, 5)  # Trend with noise
    ts_data.append((date, value))

ts_schema = StructType([
    StructField("date", DateType(), True),
    StructField("value", DoubleType(), True)
])

ts_df = spark.createDataFrame(ts_data, ts_schema)

# Add time-based calculations
window_ts = Window.orderBy("date")

ts_analysis = ts_df.select(
    F.col("*"),
    # Moving averages
    F.avg("value").over(window_ts.rowsBetween(-6, 0)).alias("ma_7"),
    F.avg("value").over(window_ts.rowsBetween(-13, 0)).alias("ma_14"),
    # Lag values for change calculations
    F.lag("value", 1).over(window_ts).alias("prev_value"),
    # Daily change
    (F.col("value") - F.lag("value", 1).over(window_ts)).alias("daily_change"),
    # Percentage change
    ((F.col("value") - F.lag("value", 1).over(window_ts)) / 
     F.lag("value", 1).over(window_ts) * 100).alias("pct_change")
)

print("Time Series with Moving Averages and Changes:")
ts_analysis.show()

# Volatility calculation (rolling standard deviation)
volatility_window = Window.orderBy("date").rowsBetween(-6, 0)
volatility_df = ts_analysis.select(
    F.col("date"),
    F.col("value"),
    F.col("daily_change"),
    F.stddev("daily_change").over(volatility_window).alias("volatility_7d")
)

print("Volatility Analysis:")
volatility_df.show()
```

### Performance Optimization Tips

```python
print("Performance Optimization Examples:")

# Cache frequently used DataFrames
df.cache()

# Use appropriate partitioning for large datasets
# df_partitioned = df.repartition(4, "category")

# Broadcast small lookup tables
# broadcast_df = F.broadcast(small_df)

# Use column expressions efficiently
# Instead of multiple selects, combine operations
optimized_calc = df.select(
    F.col("*"),
    # Combine multiple math operations in one expression
    (F.sqrt(F.abs(F.col("value"))) + 
     F.log(F.col("amount") + 1) * 
     F.sin(F.col("value") / 10)).alias("combined_calculation")
)

print("Optimized Combined Calculations:")
optimized_calc.show()

# Use SQL expressions for complex calculations
sql_expr = df.select(
    F.col("*"),
    F.expr("CASE WHEN value > 0 THEN sqrt(value) ELSE 0 END").alias("conditional_sqrt"),
    F.expr("power(value, 2) + sqrt(amount)").alias("power_sqrt_combo")
)

print("SQL Expression Examples:")
sql_expr.show()

# Cleanup
spark.stop()
```

## Key Differences from Pandas/NumPy

### Data Processing Model
- **Lazy Evaluation**: Operations are not executed immediately, but when an action is called
- **Distributed**: Computations are distributed across cluster nodes
- **Immutable**: DataFrames are immutable; operations return new DataFrames
- **Column-based**: Operations work on columns, not individual elements

### Performance Considerations
- **Caching**: Use `.cache()` or `.persist()` for DataFrames used multiple times
- **Partitioning**: Proper partitioning is crucial for performance
- **Broadcasting**: Use `F.broadcast()` for small lookup tables
- **Columnar Operations**: Vectorized operations are highly optimized

### Memory Management
- **Spill to Disk**: Spark automatically spills data to disk when memory is full
- **Resource Management**: Configure executor memory and cores appropriately
- **Garbage Collection**: JVM garbage collection affects performance

### Function Categories Summary

1. **Element-wise Functions**: Applied to each element (abs, sqrt, sin, etc.)
2. **Aggregate Functions**: Reduce multiple rows to single value (sum, avg, etc.)
3. **Window Functions**: Operate over a window of rows (lag, lead, rank, etc.)
4. **Conditional Functions**: Apply logic with when/otherwise
5. **Statistical Functions**: Advanced statistics (correlation, percentiles, etc.)

### Best Practices
- Use built-in functions instead of UDFs when possible
- Minimize shuffling operations
- Use appropriate data types
- Cache intermediate results that are reused
- Optimize join strategies
- Monitor Spark UI for performance tuning
