# Spark Basic Operations
These are the basic spark action for working with data

### Table of Contents
- [Selects](#Selects)
- [Cast and Converts](#Cast-and-Converts)
- [Array Functions](#Helpful-Array-Functions)

---
# Selects
Here's a comprehensive comparison of `select()` vs `selectExpr()` in PySpark:

## **select()**

### **Syntax & Usage:**
```python
from pyspark.sql.functions import col, lit, upper, when

# Column references
df.select('name', 'age')
df.select(col('name'), col('age'))

# With functions
df.select(col('name'), 
          upper(col('name')).alias('upper_name'),
          (col('age') + 1).alias('age_plus_one'))

# With complex expressions
df.select(when(col('age') > 18, 'Adult').otherwise('Minor').alias('category'))
```

### **Pros:**
- **Type safety**: Column references are validated at compile time
- **IDE support**: Better autocomplete and error detection
- **Function library**: Access to rich PySpark functions library
- **Readable**: Clear separation between column names and transformations
- **Debugging**: Easier to debug complex expressions step by step

### **Cons:**
- **Verbose**: Requires more imports and longer syntax
- **Learning curve**: Need to know PySpark function names

---

## **selectExpr()**

### **Syntax & Usage:**
```python
# Simple expressions
df.selectExpr('name', 'age')

# SQL expressions as strings
df.selectExpr('name', 
              'UPPER(name) as upper_name',
              'age + 1 as age_plus_one')

# Complex SQL expressions
df.selectExpr('*',
              'CASE WHEN age > 18 THEN "Adult" ELSE "Minor" END as category',
              'price * quantity as total_amount')
```

### **Pros:**
- **Concise**: Shorter syntax for simple expressions
- **SQL familiar**: Natural for those comfortable with SQL
- **String flexibility**: Can build expressions dynamically
- **Complex expressions**: Easier for complex SQL logic

### **Cons:**
- **No type safety**: Expressions are strings, errors caught at runtime
- **No IDE support**: No autocomplete or syntax validation
- **Limited debugging**: Harder to debug string expressions
- **SQL dependency**: Need to know SQL syntax

---

## **Use Cases Comparison:**

### **Use `select()` when:**

**1. Type safety is important:**
```python
# This will catch column name errors early
df.select(col('customer_name'), col('order_total'))
```

**2. Complex PySpark functions:**
```python
from pyspark.sql.functions import regexp_replace, split, explode

df.select(col('name'),
          explode(split(col('tags'), ',')).alias('tag'),
          regexp_replace(col('phone'), r'[^\d]', '').alias('clean_phone'))
```

**3. Building expressions programmatically:**
```python
columns_to_select = ['name', 'age', 'city']
df.select([col(c) for c in columns_to_select])
```

### **Use `selectExpr()` when:**

**1. Simple SQL expressions:**
```python
# Clean and concise
df.selectExpr('name', 'age * 12 as age_months', 'salary / 12 as monthly_salary')
```

**2. Complex CASE statements:**
```python
df.selectExpr('*',
              '''CASE 
                   WHEN score >= 90 THEN "A"
                   WHEN score >= 80 THEN "B" 
                   WHEN score >= 70 THEN "C"
                   ELSE "F" 
                 END as grade''')
```

**3. Dynamic SQL generation:**
```python
# Building expressions from strings
calculations = ['price * 1.1 as price_with_tax', 'quantity * price as total']
df.selectExpr('*', *calculations)
```

---

## **Performance:**
Both compile to the same Catalyst expressions, so **performance is identical**.

## **Best Practices:**

**Combine both approaches:**
```python
# Use selectExpr for simple math, select() for complex logic
df.selectExpr('name', 'price * quantity as total') \
  .select('*', 
          when(col('total') > 1000, 'Premium')
          .otherwise('Standard').alias('tier'))
```

**Choose based on team preference:**
- **SQL-heavy teams**: Prefer `selectExpr()`
- **Python-focused teams**: Prefer `select()`
- **Mixed teams**: Use `select()` for type safety, `selectExpr()` for simple expressions

The key is consistency within your codebase and choosing the approach that makes your code most readable and maintainable for your specific use case.

---
# Cast and Converts
Here are practical examples of using `cast` and `convert` functions in PySpark:This comprehensive example covers both `cast` and data conversion operations in PySpark:

## Key Cast Operations:
- **Basic casting**: Using `.cast(DataType())` or `.cast("string_type")`
- **Safe casting**: With null handling using `when().otherwise()`
- **Date/timestamp casting**: Using `to_date()` and `to_timestamp()`
- **Decimal precision**: Specifying precision with `DecimalType(10,2)`

## Key Conversion Patterns:
- **String cleaning**: Using `regexp_replace()` before casting
- **Conditional conversion**: Using `when().otherwise()` for complex logic
- **Array conversion**: Using `split()` for comma-separated strings
- **JSON parsing**: Using `from_json()` with defined schema
- **Numeric formatting**: Using `format_number()` and `round()`

## Best Practices Shown:
1. **Always handle nulls** when casting to avoid errors
2. **Validate data** before casting using regex patterns
3. **Use appropriate data types** (DecimalType for money, DateType for dates)
4. **Batch operations** for multiple column conversions
5. **Error handling** with conditional logic

The examples demonstrate real-world scenarios like cleaning messy data, converting between different formats, and safely handling edge cases that commonly occur in data processing pipelines.

## Code Examples:
```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, cast, when, regexp_replace, to_date, to_timestamp
from pyspark.sql.types import *
import pyspark.sql.functions as F

# Initialize Spark session
spark = SparkSession.builder.appName("CastConvertExamples").getOrCreate()

# Sample data
data = [
    ("1", "John", "25.5", "2023-01-15", "true", "1000.50"),
    ("2", "Jane", "30", "2023-02-20", "false", "2500.75"),
    ("3", "Bob", "invalid", "2023-03-25", "1", "abc"),
    ("4", "Alice", "28.7", "invalid-date", "0", "3500.25")
]

columns = ["id", "name", "age_str", "date_str", "is_active_str", "salary_str"]
df = spark.createDataFrame(data, columns)

print("Original DataFrame:")
df.show()
df.printSchema()

# =============================================================================
# CAST FUNCTION EXAMPLES
# =============================================================================

print("\n" + "="*50)
print("CAST FUNCTION EXAMPLES")
print("="*50)

# 1. Basic casting with cast() function
print("\n1. Basic casting examples:")
df_cast = df.select(
    col("id").cast(IntegerType()).alias("id_int"),
    col("name"),
    col("age_str").cast(DoubleType()).alias("age_double"),
    col("salary_str").cast(DecimalType(10,2)).alias("salary_decimal"),
    col("is_active_str").cast(BooleanType()).alias("is_active_bool")
)
df_cast.show()
df_cast.printSchema()

# 2. Cast using string type names (alternative syntax)
print("\n2. Cast using string type names:")
df_cast_str = df.select(
    col("id").cast("int").alias("id_int"),
    col("age_str").cast("double").alias("age_double"),
    col("salary_str").cast("decimal(10,2)").alias("salary_decimal"),
    col("is_active_str").cast("boolean").alias("is_active_bool")
)
df_cast_str.show()

# 3. Safe casting with error handling
print("\n3. Safe casting with null handling:")
df_safe_cast = df.select(
    col("id").cast(IntegerType()).alias("id_int"),
    col("name"),
    # Use when() to handle invalid values before casting
    when(col("age_str").rlike("^[0-9]*\\.?[0-9]+$"), 
         col("age_str").cast(DoubleType())).otherwise(None).alias("age_safe"),
    when(col("salary_str").rlike("^[0-9]*\\.?[0-9]+$"), 
         col("salary_str").cast(DecimalType(10,2))).otherwise(None).alias("salary_safe")
)
df_safe_cast.show()

# 4. Date and timestamp casting
print("\n4. Date and timestamp casting:")
df_dates = df.select(
    col("name"),
    col("date_str"),
    # Cast string to date
    to_date(col("date_str"), "yyyy-MM-dd").alias("date_converted"),
    # Cast string to timestamp
    to_timestamp(col("date_str"), "yyyy-MM-dd").alias("timestamp_converted"),
    # Alternative casting approach
    col("date_str").cast(DateType()).alias("date_cast")
)
df_dates.show()

# =============================================================================
# DATA TYPE CONVERSION EXAMPLES
# =============================================================================

print("\n" + "="*50)
print("DATA TYPE CONVERSION EXAMPLES")
print("="*50)

# 1. String manipulations and conversions
print("\n1. String cleaning and conversion:")
df_string_convert = df.select(
    col("name"),
    # Clean and convert salary
    regexp_replace(col("salary_str"), "[^0-9.]", "").cast(DoubleType()).alias("salary_cleaned"),
    # Convert boolean strings
    when(col("is_active_str").isin("true", "1", "yes"), True)
    .when(col("is_active_str").isin("false", "0", "no"), False)
    .otherwise(None).alias("is_active_converted"),
    # Pad ID with zeros
    F.lpad(col("id"), 5, "0").alias("id_padded")
)
df_string_convert.show()

# 2. Numeric conversions and formatting
print("\n2. Numeric conversions:")
numeric_data = [
    (1, 1234.5678, 1000000),
    (2, 2345.1234, 2500000),
    (3, 0.12345, 500)
]
df_numeric = spark.createDataFrame(numeric_data, ["id", "decimal_val", "big_number"])

df_numeric_convert = df_numeric.select(
    col("id"),
    # Round decimal
    F.round(col("decimal_val"), 2).alias("rounded_decimal"),
    # Convert to integer
    col("decimal_val").cast(IntegerType()).alias("decimal_as_int"),
    # Format large numbers
    F.format_number(col("big_number"), 0).alias("formatted_number"),
    # Convert to scientific notation (as string)
    F.format_string("%.2e", col("big_number")).alias("scientific_notation")
)
df_numeric_convert.show()

# 3. Array and complex type conversions
print("\n3. Complex type conversions:")
complex_data = [
    (1, "apple,banana,cherry", '{"name": "John", "age": 25}'),
    (2, "dog,cat,bird", '{"name": "Jane", "age": 30}'),
    (3, "red,green,blue", '{"name": "Bob", "age": 35}')
]
df_complex = spark.createDataFrame(complex_data, ["id", "items_str", "json_str"])

df_complex_convert = df_complex.select(
    col("id"),
    # Convert comma-separated string to array
    F.split(col("items_str"), ",").alias("items_array"),
    # Parse JSON string (requires from_json with schema)
    F.from_json(col("json_str"), 
               StructType([
                   StructField("name", StringType(), True),
                   StructField("age", IntegerType(), True)
               ])).alias("parsed_json")
)
df_complex_convert.show(truncate=False)

# Extract fields from parsed JSON
df_json_extract = df_complex_convert.select(
    col("id"),
    col("items_array"),
    col("parsed_json.name").alias("person_name"),
    col("parsed_json.age").alias("person_age")
)
df_json_extract.show()

# 4. Conditional conversions
print("\n4. Conditional conversions:")
conditional_data = [
    (1, "ACTIVE", "2023-01-15", "PREMIUM"),
    (2, "INACTIVE", "2022-12-01", "BASIC"),
    (3, "PENDING", "2023-03-20", "PREMIUM"),
    (4, "ACTIVE", "2021-06-15", "BASIC")
]
df_conditional = spark.createDataFrame(conditional_data, ["id", "status", "join_date", "plan"])

df_conditional_convert = df_conditional.select(
    col("id"),
    # Convert status to numeric code
    when(col("status") == "ACTIVE", 1)
    .when(col("status") == "INACTIVE", 0)
    .when(col("status") == "PENDING", 2)
    .otherwise(-1).alias("status_code"),
    
    # Convert date and calculate days since joining
    to_date(col("join_date")).alias("join_date_converted"),
    F.datediff(F.current_date(), to_date(col("join_date"))).alias("days_since_join"),
    
    # Convert plan to priority level
    when(col("plan") == "PREMIUM", "HIGH")
    .when(col("plan") == "BASIC", "LOW")
    .otherwise("MEDIUM").alias("priority_level")
)
df_conditional_convert.show()

# =============================================================================
# BEST PRACTICES AND ERROR HANDLING
# =============================================================================

print("\n" + "="*50)
print("BEST PRACTICES AND ERROR HANDLING")
print("="*50)

# 1. Handling null values during conversion
print("\n1. Null handling during conversion:")
null_data = [
    (1, "25", "1000.50"),
    (2, None, "2500.75"),
    (3, "invalid", None),
    (4, "30", "3500.25")
]
df_nulls = spark.createDataFrame(null_data, ["id", "age_str", "salary_str"])

df_null_handling = df_nulls.select(
    col("id"),
    # Safe conversion with null preservation
    col("age_str").cast(IntegerType()).alias("age_direct_cast"),
    # Conditional conversion with default values
    when(col("age_str").isNull(), 0)
    .otherwise(col("age_str").cast(IntegerType())).alias("age_with_default"),
    # Try-catch equivalent using when/otherwise
    when(col("salary_str").rlike("^[0-9]*\\.?[0-9]+$"), 
         col("salary_str").cast(DoubleType()))
    .otherwise(0.0).alias("salary_safe_convert")
)
df_null_handling.show()

# 2. Batch conversion function
def safe_cast_columns(df, cast_dict):
    """
    Safely cast multiple columns with error handling
    cast_dict: {"column_name": "target_type"}
    """
    for col_name, target_type in cast_dict.items():
        if col_name in df.columns:
            df = df.withColumn(f"{col_name}_converted", 
                             col(col_name).cast(target_type))
    return df

# Example usage
cast_mapping = {
    "id": "int",
    "age_str": "double", 
    "salary_str": "decimal(10,2)"
}

df_batch_converted = safe_cast_columns(df, cast_mapping)
print("\n2. Batch conversion result:")
df_batch_converted.select("id", "id_converted", "age_str", "age_str_converted", 
                         "salary_str", "salary_str_converted").show()

print("\nConversion complete! Remember to handle invalid data and null values appropriately.")

# Clean up
spark.stop()
```

---
# Helpful Array Functions
I'll explain these PySpark functions with their parameters and provide detailed examples showing the differences between them.Here's a detailed breakdown of the key parameters and differences:

## **SIZE vs LENGTH**

**`size(col)`**
- **Parameters**: Single column containing array or map
- **Returns**: Integer count of elements (-1 for null arrays)
- **Use case**: Count array/map elements

**`length(col)`**
- **Parameters**: Single column containing string
- **Returns**: Integer character count (null for null strings, 0 for empty)
- **Use case**: Count string characters

## **COLLECT_LIST vs COLLECT_SET**

**`collect_list(col)`**
- **Parameters**: Column to aggregate (used in groupBy operations)
- **Behavior**: Preserves ALL values including duplicates and maintains order
- **Returns**: Array with all collected values
- **Use case**: When you need complete history/all occurrences

**`collect_set(col)`**
- **Parameters**: Column to aggregate (used in groupBy operations) 
- **Behavior**: Returns only UNIQUE values, removes duplicates
- **Returns**: Array with distinct values (no guaranteed order)
- **Use case**: When you need unique values only

## **EXPLODE vs LATERAL VIEW EXPLODE**

**Key Differences:**

1. **`explode(col)`** (DataFrame API)
   - Drops rows with null/empty arrays entirely
   - Simpler syntax for basic use cases
   - Better performance for simple operations

2. **`explode_outer(col)`** (DataFrame API)
   - Preserves rows with null/empty arrays as null values
   - Maintains row count relationship with original data

3. **`LATERAL VIEW EXPLODE`** (SQL syntax)
   - More flexible for complex queries
   - Allows multiple explodes in same query
   - Enables combining with JOINs and complex SQL operations
   - `OUTER` variant preserves null/empty arrays

4. **`posexplode(col)`** (DataFrame API)
   - Returns both position index AND value
   - Useful when order/position matters

## **When to Use Each:**

- **Use `explode()`**: Simple array flattening, don't need null/empty preservation
- **Use `explode_outer()`**: Need to preserve all original rows
- **Use `LATERAL VIEW`**: Complex SQL queries, multiple arrays, need SQL flexibility
- **Use `posexplode()`**: When position/index information is important
- **Use `collect_list()`**: Need all values including duplicates
- **Use `collect_set()`**: Need only unique values for deduplication

The code examples demonstrate these differences with practical scenarios showing how each function behaves with null values, empty arrays, and duplicate data.

## Code Examples
```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
import pyspark.sql.functions as F

# Initialize Spark session
spark = SparkSession.builder.appName("ArrayFunctions").getOrCreate()

# =============================================================================
# SIZE AND LENGTH FUNCTIONS
# =============================================================================

print("="*60)
print("SIZE AND LENGTH FUNCTIONS")
print("="*60)

# Sample data with arrays and strings
array_data = [
    (1, "John", ["apple", "banana", "cherry"], "Hello World", None),
    (2, "Jane", ["dog", "cat"], "PySpark", []),
    (3, "Bob", ["red", "green", "blue", "yellow"], "Data Engineering", ["item1"]),
    (4, "Alice", None, "", ["a", "b", "c", "d", "e"])
]

df_arrays = spark.createDataFrame(array_data, 
    ["id", "name", "fruits", "text", "items"])

print("\nOriginal DataFrame:")
df_arrays.show(truncate=False)

# SIZE function - returns number of elements in array/map
# Parameters: size(col) - takes a column containing array or map
print("\n1. SIZE function examples:")
df_size = df_arrays.select(
    col("id"),
    col("name"),
    col("fruits"),
    size(col("fruits")).alias("fruits_size"),  # Number of elements in array
    col("items"),
    size(col("items")).alias("items_size"),
    # Size returns -1 for null arrays
    when(col("fruits").isNull(), "NULL ARRAY").otherwise(size(col("fruits")).cast("string")).alias("fruits_size_with_null_check")
)
df_size.show(truncate=False)

# LENGTH function - returns length of string
# Parameters: length(col) - takes a column containing string
print("\n2. LENGTH function examples:")
df_length = df_arrays.select(
    col("id"),
    col("name"),
    col("text"),
    length(col("text")).alias("text_length"),    # Length of string
    length(col("name")).alias("name_length"),
    # Length returns null for null strings, 0 for empty strings
    when(col("text").isNull(), "NULL STRING")
    .when(length(col("text")) == 0, "EMPTY STRING")
    .otherwise(length(col("text")).cast("string")).alias("text_length_detailed")
)
df_length.show(truncate=False)

# =============================================================================
# COLLECT_LIST AND COLLECT_SET FUNCTIONS
# =============================================================================

print("\n" + "="*60)
print("COLLECT_LIST AND COLLECT_SET FUNCTIONS")
print("="*60)

# Sample data for aggregation
sales_data = [
    ("John", "Electronics", "Laptop", 1000),
    ("John", "Electronics", "Mouse", 25),
    ("John", "Books", "Python Guide", 50),
    ("Jane", "Electronics", "Laptop", 1000),
    ("Jane", "Electronics", "Keyboard", 75),
    ("Jane", "Books", "Data Science", 60),
    ("Bob", "Electronics", "Mouse", 25),
    ("Bob", "Electronics", "Mouse", 25),  # Duplicate
    ("Alice", "Books", "AI Handbook", 80)
]

df_sales = spark.createDataFrame(sales_data, 
    ["person", "category", "product", "price"])

print("\nSales DataFrame:")
df_sales.show()

# COLLECT_LIST function - collects all values into a list (preserves duplicates)
# Parameters: collect_list(col) - aggregation function, preserves order and duplicates
print("\n3. COLLECT_LIST examples:")
df_collect_list = df_sales.groupBy("person").agg(
    collect_list("product").alias("all_products"),           # All products (with duplicates)
    collect_list("price").alias("all_prices"),               # All prices
    collect_list("category").alias("all_categories"),        # All categories
    count("*").alias("total_purchases")
)
df_collect_list.show(truncate=False)

# COLLECT_SET function - collects unique values into a set (removes duplicates)
# Parameters: collect_set(col) - aggregation function, removes duplicates, no guaranteed order
print("\n4. COLLECT_SET examples:")
df_collect_set = df_sales.groupBy("person").agg(
    collect_set("product").alias("unique_products"),         # Unique products only
    collect_set("price").alias("unique_prices"),             # Unique prices only
    collect_set("category").alias("unique_categories"),      # Unique categories only
    count("*").alias("total_purchases")
)
df_collect_set.show(truncate=False)

# Comparison: collect_list vs collect_set
print("\n5. COLLECT_LIST vs COLLECT_SET comparison:")
df_comparison = df_sales.groupBy("person").agg(
    collect_list("product").alias("products_with_duplicates"),
    collect_set("product").alias("products_unique_only"),
    size(collect_list("product")).alias("total_count"),
    size(collect_set("product")).alias("unique_count")
)
df_comparison.show(truncate=False)

# Advanced aggregation with multiple columns
print("\n6. Advanced COLLECT operations:")
df_advanced_collect = df_sales.groupBy("category").agg(
    collect_list(struct("person", "product", "price")).alias("detailed_sales"),
    collect_set("person").alias("customers"),
    avg("price").alias("avg_price"),
    sum("price").alias("total_revenue")
)
df_advanced_collect.show(truncate=False)

# =============================================================================
# EXPLODE VS LATERAL VIEW EXPLODE
# =============================================================================

print("\n" + "="*60)
print("EXPLODE VS LATERAL VIEW EXPLODE")
print("="*60)

# Sample data with arrays for exploding
explode_data = [
    (1, "John", ["apple", "banana", "cherry"], {"color": "red", "size": "large"}),
    (2, "Jane", ["dog", "cat"], {"color": "blue", "size": "medium"}),
    (3, "Bob", [], {"color": "green", "size": "small"}),  # Empty array
    (4, "Alice", None, {"color": "yellow", "size": "large"}),  # Null array
    (5, "Charlie", ["single_item"], {"color": "purple", "size": "tiny"})
]

df_explode = spark.createDataFrame(explode_data, 
    ["id", "name", "items", "metadata"])

print("\nOriginal DataFrame for exploding:")
df_explode.show(truncate=False)

# EXPLODE function - creates new row for each array element
# Parameters: explode(col) - takes array/map column, creates new rows
print("\n7. Basic EXPLODE examples:")
df_basic_explode = df_explode.select(
    col("id"),
    col("name"),
    explode(col("items")).alias("item")  # Creates new row for each array element
)
print("Basic explode (drops rows with null/empty arrays):")
df_basic_explode.show()

# EXPLODE_OUTER function - includes null/empty arrays as null values
# Parameters: explode_outer(col) - like explode but preserves null/empty
print("\n8. EXPLODE_OUTER examples:")
df_explode_outer = df_explode.select(
    col("id"),
    col("name"),
    explode_outer(col("items")).alias("item")  # Preserves null/empty as null
)
print("Explode outer (preserves rows with null/empty arrays):")
df_explode_outer.show()

# POSEXPLODE function - includes position index
# Parameters: posexplode(col) - returns (position, value) for each element
print("\n9. POSEXPLODE examples:")
df_posexplode = df_explode.select(
    col("id"),
    col("name"),
    posexplode(col("items")).alias("pos", "item")  # Returns position and value
)
print("Posexplode (includes position index):")
df_posexplode.show()

# =============================================================================
# LATERAL VIEW EXPLODE (SQL syntax)
# =============================================================================

print("\n10. LATERAL VIEW EXPLODE (SQL syntax):")

# Register DataFrame as temporary view for SQL
df_explode.createOrReplaceTempView("explode_table")

# LATERAL VIEW EXPLODE - SQL syntax equivalent
print("Using LATERAL VIEW EXPLODE in SQL:")
df_lateral_view = spark.sql("""
    SELECT 
        id,
        name,
        item
    FROM explode_table
    LATERAL VIEW EXPLODE(items) AS item
""")
df_lateral_view.show()

# LATERAL VIEW OUTER EXPLODE - preserves null/empty arrays
print("\nUsing LATERAL VIEW OUTER EXPLODE in SQL:")
df_lateral_view_outer = spark.sql("""
    SELECT 
        id,
        name,
        item
    FROM explode_table
    LATERAL VIEW OUTER EXPLODE(items) AS item
""")
df_lateral_view_outer.show()

# Multiple LATERAL VIEW EXPLODE
print("\n11. Multiple LATERAL VIEW EXPLODE:")
multi_array_data = [
    (1, "John", ["apple", "banana"], ["red", "yellow"]),
    (2, "Jane", ["cat", "dog"], ["black", "white"]),
    (3, "Bob", ["book"], ["blue"])
]

df_multi = spark.createDataFrame(multi_array_data, ["id", "name", "items1", "items2"])
df_multi.createOrReplaceTempView("multi_table")

# Explode multiple arrays simultaneously
df_multi_lateral = spark.sql("""
    SELECT 
        id,
        name,
        item1,
        item2
    FROM multi_table
    LATERAL VIEW EXPLODE(items1) AS item1
    LATERAL VIEW EXPLODE(items2) AS item2
""")
print("Multiple lateral view explode (Cartesian product):")
df_multi_lateral.show()

# =============================================================================
# PRACTICAL COMPARISON AND USE CASES
# =============================================================================

print("\n" + "="*60)
print("PRACTICAL COMPARISON AND USE CASES")
print("="*60)

# Create comprehensive comparison
comparison_data = [
    (1, "John", ["A", "B", "C"], "John has items"),
    (2, "Jane", [], "Jane has no items"),
    (3, "Bob", None, "Bob has null items"),
    (4, "Alice", ["X"], "Alice has one item")
]

df_comparison_test = spark.createDataFrame(comparison_data, ["id", "name", "items", "description"])

print("\n12. Comprehensive comparison:")
print("Original data:")
df_comparison_test.show(truncate=False)

print("\nUsing explode() - drops null/empty:")
df_comparison_test.select("id", "name", "description", explode("items").alias("item")).show()

print("\nUsing explode_outer() - preserves null/empty:")
df_comparison_test.select("id", "name", "description", explode_outer("items").alias("item")).show()

# Performance and memory considerations
print("\n13. Performance considerations:")
large_array_data = [(i, f"user_{i}", list(range(i, i+10))) for i in range(1, 6)]
df_large = spark.createDataFrame(large_array_data, ["id", "name", "numbers"])

print("Before explode:")
print(f"Row count: {df_large.count()}")
df_large.show()

df_exploded_large = df_large.select("id", "name", explode("numbers").alias("number"))
print("\nAfter explode:")
print(f"Row count: {df_exploded_large.count()}")
df_exploded_large.show()

# =============================================================================
# SUMMARY OF KEY DIFFERENCES
# =============================================================================

print("\n" + "="*60)
print("SUMMARY OF KEY DIFFERENCES")
print("="*60)

print("""
SIZE vs LENGTH:
- size(): Returns number of elements in array/map (-1 for null)
- length(): Returns character count in string (null for null strings)

COLLECT_LIST vs COLLECT_SET:
- collect_list(): Preserves duplicates and order, returns all values
- collect_set(): Removes duplicates, no guaranteed order, returns unique values

EXPLODE vs LATERAL VIEW EXPLODE:
- explode(): DataFrame API function, drops null/empty arrays
- explode_outer(): DataFrame API function, preserves null/empty as null
- posexplode(): DataFrame API function, includes position index
- LATERAL VIEW EXPLODE: SQL syntax, equivalent to explode()
- LATERAL VIEW OUTER EXPLODE: SQL syntax, equivalent to explode_outer()

Key Differences:
1. explode() drops rows with null/empty arrays
2. explode_outer() preserves rows with null/empty arrays as null values
3. LATERAL VIEW allows multiple explodes and complex SQL joins
4. posexplode() provides both position and value
5. Performance: explode() is generally faster than LATERAL VIEW for simple cases
""")

# Clean up
spark.stop()
```
