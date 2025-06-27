# Spark Basic Union
In PySpark, `unionAll()` combines two or more DataFrames by stacking their rows together. It's equivalent to SQL's `UNION ALL` operation.

## Key Points about unionAll():

**Important Note**: `unionAll()` was deprecated in Spark 2.0+ and replaced with `union()`. The current `union()` method behaves like the old `unionAll()` (keeps duplicates).

## Current Syntax:
```python
# Modern approach (Spark 2.0+)
result_df = df1.union(df2)

# Old syntax (deprecated but still works)
result_df = df1.unionAll(df2)
```

## Characteristics:
- **Keeps duplicates** (unlike SQL's `UNION` which removes duplicates)
- **Position-based**: Combines columns by position, not by name
- **Same number of columns**: DataFrames must have the same number of columns
- **Compatible data types**: Column types should be compatible

## Examples:## Summary:

**unionAll() vs union():**
- `unionAll()` is **deprecated** since Spark 2.0
- Use `union()` instead - it behaves like the old `unionAll()` (keeps duplicates)
- If you want to remove duplicates, use `union().distinct()`

**Key Methods:**
- `df1.union(df2)` - Combines DataFrames, keeps duplicates
- `df1.union(df2).distinct()` - Combines and removes duplicates  
- `df1.unionByName(df2)` - Combines by column names (Spark 3.1+)

**Requirements:**
- Same number of columns
- Compatible data types
- Position-based matching (unless using `unionByName`)

**Common Use Cases:**
- Combining data from different time periods
- Merging data from different regions/sources  
- Consolidating partitioned data
- Appending new data to existing datasets

The examples show various scenarios including handling different schemas, multiple DataFrames, and performance considerations.

---
```python
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType

# Initialize Spark Session
spark = SparkSession.builder \
    .appName("Union Examples") \
    .getOrCreate()

# =============================================================================
# BASIC UNION EXAMPLE
# =============================================================================

# Create first DataFrame
df1_data = [
    (1, "Alice", "Engineering"),
    (2, "Bob", "Sales"),
    (3, "Charlie", "Marketing")
]

df1 = spark.createDataFrame(df1_data, ["id", "name", "department"])

# Create second DataFrame
df2_data = [
    (4, "Diana", "HR"),
    (5, "Eve", "Engineering"),
    (2, "Bob", "Sales")  # Duplicate row
]

df2 = spark.createDataFrame(df2_data, ["id", "name", "department"])

print("=== DataFrame 1 ===")
df1.show()

print("=== DataFrame 2 ===")
df2.show()

# Union (keeps duplicates - like UNION ALL)
print("=== UNION (keeps duplicates) ===")
union_result = df1.union(df2)
union_result.show()

print(f"Total rows after union: {union_result.count()}")

# =============================================================================
# UNION vs DISTINCT
# =============================================================================

print("=== UNION with DISTINCT (removes duplicates) ===")
union_distinct = df1.union(df2).distinct()
union_distinct.show()

print(f"Total rows after union + distinct: {union_distinct.count()}")

# =============================================================================
# MULTIPLE DATAFRAMES UNION
# =============================================================================

# Create third DataFrame
df3_data = [
    (6, "Frank", "Finance"),
    (7, "Grace", "Legal")
]

df3 = spark.createDataFrame(df3_data, ["id", "name", "department"])

print("=== DataFrame 3 ===")
df3.show()

# Union multiple DataFrames
print("=== UNION of 3 DataFrames ===")
multi_union = df1.union(df2).union(df3)
multi_union.show()

# Alternative: Using reduce for multiple unions
from functools import reduce
dataframes = [df1, df2, df3]
multi_union_alt = reduce(lambda x, y: x.union(y), dataframes)
print("=== Alternative Multi-Union ===")
multi_union_alt.show()

# =============================================================================
# UNION BY NAME (Spark 3.1+)
# =============================================================================

# Create DataFrames with different column orders
df_ordered1 = spark.createDataFrame([
    (1, "Alice", "Engineering")
], ["id", "name", "department"])

df_ordered2 = spark.createDataFrame([
    ("Bob", 2, "Sales")  # Different column order
], ["name", "id", "department"])

print("=== DataFrame with different column order ===")
df_ordered1.show()
df_ordered2.show()

# Regular union (position-based) - WRONG RESULT
print("=== Regular Union (Position-based) - INCORRECT ===")
try:
    wrong_union = df_ordered1.union(df_ordered2)
    wrong_union.show()
except Exception as e:
    print(f"Error: {e}")

# UnionByName (Spark 3.1+) - matches by column names
print("=== Union By Name (Correct) ===")
try:
    correct_union = df_ordered1.unionByName(df_ordered2)
    correct_union.show()
except Exception as e:
    print(f"unionByName not available in this Spark version: {e}")

# =============================================================================
# HANDLING DIFFERENT SCHEMAS
# =============================================================================

# DataFrames with different schemas
df_schema1 = spark.createDataFrame([
    (1, "Alice", 25)
], ["id", "name", "age"])

df_schema2 = spark.createDataFrame([
    (2, "Bob", "Engineering")
], ["id", "name", "department"])

print("=== Different Schemas ===")
df_schema1.show()
df_schema2.show()

# This will fail - different schemas
print("=== Union with Different Schemas (Will Fail) ===")
try:
    bad_union = df_schema1.union(df_schema2)
    bad_union.show()
except Exception as e:
    print(f"Error as expected: {e}")

# Solution: Add missing columns with null values
from pyspark.sql.functions import lit

print("=== Solution: Add Missing Columns ===")
df_schema1_fixed = df_schema1.withColumn("department", lit(None).cast(StringType()))
df_schema2_fixed = df_schema2.withColumn("age", lit(None).cast(IntegerType()))

# Reorder columns to match
df_schema1_fixed = df_schema1_fixed.select("id", "name", "age", "department")
df_schema2_fixed = df_schema2_fixed.select("id", "name", "age", "department")

fixed_union = df_schema1_fixed.union(df_schema2_fixed)
fixed_union.show()

# =============================================================================
# PRACTICAL EXAMPLE: COMBINING DATA FROM DIFFERENT SOURCES
# =============================================================================

print("=== PRACTICAL EXAMPLE: Sales Data from Different Regions ===")

# Sales data from North region
north_sales = spark.createDataFrame([
    ("2024-01-15", "Laptop", 1200.00, "North"),
    ("2024-01-16", "Mouse", 25.99, "North"),
    ("2024-01-17", "Keyboard", 79.99, "North")
], ["date", "product", "amount", "region"])

# Sales data from South region
south_sales = spark.createDataFrame([
    ("2024-01-15", "Monitor", 299.99, "South"),
    ("2024-01-16", "Laptop", 1200.00, "South"),  # Same product, different region
    ("2024-01-18", "Headphones", 89.99, "South")
], ["date", "product", "amount", "region"])

print("North Sales:")
north_sales.show()

print("South Sales:")
south_sales.show()

# Combine all sales data
print("Combined Sales Data:")
all_sales = north_sales.union(south_sales)
all_sales.show()

# Analysis on combined data
print("Total Sales by Region:")
all_sales.groupBy("region").sum("amount").show()

print("Total Sales by Product:")
all_sales.groupBy("product").sum("amount").show()

# =============================================================================
# PERFORMANCE TIPS
# =============================================================================

print("\n" + "="*60)
print("PERFORMANCE TIPS:")
print("="*60)
print("1. union() is more efficient than unionAll() (deprecated)")
print("2. Consider repartitioning after union for better parallelism:")
print("   df1.union(df2).repartition(10)")
print("3. Use unionByName() when column orders might differ")
print("4. For large datasets, consider coalesce() after union:")
print("   df1.union(df2).coalesce(5)")
print("5. Cache the result if you'll use it multiple times:")
print("   result = df1.union(df2).cache()")
print("="*60)

# Example of repartitioning after union
print("\nPartition info before union:")
print(f"df1 partitions: {df1.rdd.getNumPartitions()}")
print(f"df2 partitions: {df2.rdd.getNumPartitions()}")

union_result = df1.union(df2)
print(f"After union partitions: {union_result.rdd.getNumPartitions()}")

# Repartition for better performance
repartitioned = union_result.repartition(4)
print(f"After repartition: {repartitioned.rdd.getNumPartitions()}")
```
