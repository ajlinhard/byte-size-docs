# Spark UDTF aka Lateral View Functions
The title may be a little confusing, but the content below is referring to function which burst the tables row-wise. Meaning 1 row becomes 0 to N rows dependent on the data and function used.

I've created a comprehensive PySpark cheatsheet covering all the major table-producing functions. The cheatsheet includes:

**📊 Key Sections:**
- **Array/Map Explosion**: `explode`, `explode_outer`, `posexplode`, and map handling
- **Data Parsing**: `json_tuple`, `from_json`, `parse_url_tuple` 
- **Data Pivoting**: `stack()` function for column-to-row transformation
- **Advanced Functions**: `flatten()` and struct array manipulation
- **Complex Combinations**: Multiple LATERAL VIEWs and nested operations

**💡 Each function includes:**
- DataFrame API syntax
- SQL/LATERAL VIEW syntax  
- Practical examples with sample data
- Expected outputs

**🚀 Bonus Features:**
- Common patterns and tips
- Performance optimization advice
- Real-world use cases like JSON parsing + array explosion

This should serve as a quick reference for all your table-producing function needs in PySpark! The examples are copy-paste ready and demonstrate both DataFrame API and SQL approaches.

---
# PySpark Table-Producing Functions Cheatsheet

## Array/Map Explosion Functions

### `explode()` - Array to Rows
Converts array elements into separate rows. **Drops null/empty arrays.**

```python
from pyspark.sql.functions import explode, col

# Sample data
data = [("Alice", ["apple", "banana"]), ("Bob", ["orange"]), ("Charlie", [])]
df = spark.createDataFrame(data, ["name", "fruits"])

# DataFrame API
df.select("name", explode("fruits").alias("fruit")).show()
# +-----+------+
# | name| fruit|
# +-----+------+
# |Alice| apple|
# |Alice|banana|
# |  Bob|orange|
# +-----+------+

# SQL
df.createOrReplaceTempView("people")
spark.sql("SELECT name, fruit FROM people LATERAL VIEW explode(fruits) t AS fruit").show()
```

### `explode_outer()` - Array to Rows (Keep Nulls)
Same as explode but **keeps rows with null/empty arrays**.

```python
from pyspark.sql.functions import explode_outer

df.select("name", explode_outer("fruits").alias("fruit")).show()
# +-------+------+
# |   name| fruit|
# +-------+------+
# |  Alice| apple|
# |  Alice|banana|
# |    Bob|orange|
# |Charlie|  null|
# +-------+------+

# SQL
spark.sql("SELECT name, fruit FROM people LATERAL VIEW OUTER explode(fruits) t AS fruit").show()
```

### `posexplode()` - Array to Rows with Position
Returns both position (0-based) and value.

```python
from pyspark.sql.functions import posexplode

df.select("name", posexplode("fruits").alias("pos", "fruit")).show()
# +-----+---+------+
# | name|pos| fruit|
# +-----+---+------+
# |Alice|  0| apple|
# |Alice|  1|banana|
# |  Bob|  0|orange|
# +-----+---+------+

# SQL
spark.sql("SELECT name, pos, fruit FROM people LATERAL VIEW posexplode(fruits) t AS pos, fruit").show()
```

### `posexplode_outer()` - Array to Rows with Position (Keep Nulls)
```python
from pyspark.sql.functions import posexplode_outer

df.select("name", posexplode_outer("fruits").alias("pos", "fruit")).show()
# +-------+----+------+
# |   name| pos| fruit|
# +-------+----+------+
# |  Alice|   0| apple|
# |  Alice|   1|banana|
# |    Bob|   0|orange|
# |Charlie|null|  null|
# +-------+----+------+
```

### Map Explosion
```python
from pyspark.sql.functions import explode, create_map, lit

# Create map data
map_df = spark.createDataFrame([
    ("Alice", {"age": 25, "city": "NYC"}),
    ("Bob", {"age": 30, "city": "LA"})
], ["name", "info"])

# Explode map
map_df.select("name", explode("info").alias("key", "value")).show()
# +-----+----+-----+
# | name| key|value|
# +-----+----+-----+
# |Alice| age|   25|
# |Alice|city|  NYC|
# |  Bob| age|   30|
# |  Bob|city|   LA|
# +-----+----+-----+
```

## Data Parsing Functions

### `json_tuple()` - Extract Multiple JSON Fields
Extracts multiple fields from JSON string in one operation.

```python
from pyspark.sql.functions import json_tuple

json_data = [
    ("Alice", '{"age": 25, "city": "NYC", "salary": 50000}'),
    ("Bob", '{"age": 30, "city": "LA", "salary": 60000}')
]
json_df = spark.createDataFrame(json_data, ["name", "json_str"])

# DataFrame API
json_df.select("name", json_tuple("json_str", "age", "city", "salary").alias("age", "city", "salary")).show()
# +-----+---+----+-----+
# | name|age|city|salary|
# +-----+---+----+-----+
# |Alice| 25| NYC|50000|
# |  Bob| 30|  LA|60000|
# +-----+---+----+-----+

# SQL
json_df.createOrReplaceTempView("json_people")
spark.sql("""
    SELECT name, age, city, salary 
    FROM json_people 
    LATERAL VIEW json_tuple(json_str, 'age', 'city', 'salary') t AS age, city, salary
""").show()
```

### `from_json()` - Parse JSON to Struct
Converts JSON string to structured data.

```python
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StructField, StringType, IntegerType

# Define schema
json_schema = StructType([
    StructField("age", IntegerType()),
    StructField("city", StringType()),
    StructField("salary", IntegerType())
])

# Parse JSON
parsed_df = json_df.withColumn("parsed", from_json("json_str", json_schema))
parsed_df.select("name", "parsed.*").show()
# +-----+---+----+------+
# | name|age|city|salary|
# +-----+---+----+------+
# |Alice| 25| NYC| 50000|
# |  Bob| 30|  LA| 60000|
# +-----+---+----+------+
```

### `parse_url_tuple()` - Extract URL Components
Extracts multiple URL parts in one operation.

```python
from pyspark.sql.functions import parse_url_tuple

url_data = [
    ("req1", "https://example.com:8080/path/to/page?param1=value1&param2=value2"),
    ("req2", "http://test.org/home?user=alice")
]
url_df = spark.createDataFrame(url_data, ["request_id", "url"])

# Extract HOST, PATH, QUERY
url_df.select("request_id", 
              parse_url_tuple("url", "HOST", "PATH", "QUERY").alias("host", "path", "query")).show(truncate=False)
# +----------+-----------+-------------+---------------------------+
# |request_id|host       |path         |query                      |
# +----------+-----------+-------------+---------------------------+
# |req1      |example.com|/path/to/page|param1=value1&param2=value2|
# |req2      |test.org   |/home        |user=alice                 |
# +----------+-----------+-------------+---------------------------+

# SQL
url_df.createOrReplaceTempView("requests")
spark.sql("""
    SELECT request_id, host, path, query
    FROM requests 
    LATERAL VIEW parse_url_tuple(url, 'HOST', 'PATH', 'QUERY') t AS host, path, query
""").show(truncate=False)
```

## Data Pivoting Functions

### `stack()` - Pivot Columns to Rows
Converts multiple columns into key-value pairs.

```python
from pyspark.sql.functions import expr

# Sample wide data
metrics_data = [
    ("server1", 80.5, 65.2, 45.8, 12.1),
    ("server2", 75.3, 70.1, 50.2, 15.5)
]
metrics_df = spark.createDataFrame(metrics_data, ["server", "cpu", "memory", "disk", "network"])

# Using stack() in SQL
metrics_df.createOrReplaceTempView("metrics")
spark.sql("""
    SELECT server, metric_name, metric_value
    FROM metrics
    LATERAL VIEW stack(4, 
        'cpu_usage', cpu,
        'memory_usage', memory,
        'disk_usage', disk,
        'network_usage', network
    ) stacked AS metric_name, metric_value
""").show()
# +-------+------------+------------+
# | server| metric_name|metric_value|
# +-------+------------+------------+
# |server1|   cpu_usage|        80.5|
# |server1|memory_usage|        65.2|
# |server1|  disk_usage|        45.8|
# |server1|network_usage|       12.1|
# |server2|   cpu_usage|        75.3|
# |server2|memory_usage|        70.1|
# |server2|  disk_usage|        50.2|
# |server2|network_usage|       15.5|
# +-------+------------+------------+

# DataFrame API equivalent (more verbose)
from pyspark.sql.functions import lit, array, struct
metrics_df.select(
    "server",
    explode(array(
        struct(lit("cpu_usage").alias("metric_name"), col("cpu").alias("metric_value")),
        struct(lit("memory_usage").alias("metric_name"), col("memory").alias("metric_value")),
        struct(lit("disk_usage").alias("metric_name"), col("disk").alias("metric_value")),
        struct(lit("network_usage").alias("metric_name"), col("network").alias("metric_value"))
    )).alias("metric")
).select("server", "metric.*").show()
```

## Array/Struct Manipulation Functions

### `flatten()` - Flatten Nested Arrays
Converts array of arrays into a single flat array.

```python
from pyspark.sql.functions import flatten

nested_data = [
    ("Alice", [["apple", "banana"], ["orange"]]),
    ("Bob", [["grape"], ["kiwi", "mango"]])
]
nested_df = spark.createDataFrame(nested_data, ["name", "nested_fruits"])

# Flatten nested arrays
nested_df.select("name", flatten("nested_fruits").alias("all_fruits")).show(truncate=False)
# +-----+------------------------+
# | name|              all_fruits|
# +-----+------------------------+
# |Alice|[apple, banana, orange] |
# |  Bob|   [grape, kiwi, mango] |
# +-----+------------------------+

# Then explode if needed
nested_df.select("name", explode(flatten("nested_fruits")).alias("fruit")).show()
# +-----+------+
# | name| fruit|
# +-----+------+
# |Alice| apple|
# |Alice|banana|
# |Alice|orange|
# |  Bob| grape|
# |  Bob|  kiwi|
# |  Bob| mango|
# +-----+------+
```

### Working with Struct Arrays
```python
from pyspark.sql.functions import explode, col

# Struct array data
struct_data = [
    ("Alice", [{"name": "apple", "color": "red"}, {"name": "banana", "color": "yellow"}]),
    ("Bob", [{"name": "orange", "color": "orange"}])
]
struct_df = spark.createDataFrame(struct_data, ["person", "fruits"])

# Explode struct array and access fields
struct_df.select("person", explode("fruits").alias("fruit")) \
         .select("person", "fruit.name", "fruit.color").show()
# +------+------+------+
# |person|  name| color|
# +------+------+------+
# | Alice| apple|   red|
# | Alice|banana|yellow|
# |   Bob|orange|orange|
# +------+------+------+
```

## Advanced Combinations

### Multiple LATERAL VIEWs (Cartesian Product)
```python
# Multiple array explosion
multi_array_data = [
    ("ProductA", ["red", "blue"], ["S", "M", "L"]),
    ("ProductB", ["green"], ["M", "L"])
]
multi_df = spark.createDataFrame(multi_array_data, ["product", "colors", "sizes"])

multi_df.createOrReplaceTempView("products")
spark.sql("""
    SELECT product, color, size
    FROM products
    LATERAL VIEW explode(colors) color_table AS color
    LATERAL VIEW explode(sizes) size_table AS size
""").show()
# +--------+-----+----+
# | product|color|size|
# +--------+-----+----+
# |ProductA|  red|   S|
# |ProductA|  red|   M|
# |ProductA|  red|   L|
# |ProductA| blue|   S|
# |ProductA| blue|   M|
# |ProductA| blue|   L|
# |ProductB|green|   M|
# |ProductB|green|   L|
# +--------+-----+----+
```

### JSON + Array Explosion
```python
# Complex nested JSON with arrays
complex_json_data = [
    ("order1", '{"customer": "Alice", "items": ["apple", "banana"], "total": 15.50}'),
    ("order2", '{"customer": "Bob", "items": ["orange"], "total": 8.25}')
]
complex_df = spark.createDataFrame(complex_json_data, ["order_id", "order_json"])

# Parse JSON and explode items
from pyspark.sql.types import StructType, StructField, StringType, ArrayType, DoubleType

order_schema = StructType([
    StructField("customer", StringType()),
    StructField("items", ArrayType(StringType())),
    StructField("total", DoubleType())
])

complex_df.withColumn("parsed", from_json("order_json", order_schema)) \
          .select("order_id", "parsed.customer", explode("parsed.items").alias("item"), "parsed.total") \
          .show()
# +--------+--------+------+-----+
# |order_id|customer|  item|total|
# +--------+--------+------+-----+
# |  order1|   Alice| apple| 15.5|
# |  order1|   Alice|banana| 15.5|
# |  order2|     Bob|orange| 8.25|
# +--------+--------+------+-----+
```

## Common Patterns & Tips

### Pattern 1: Clean Data After Explosion
```python
# Remove null values after explosion
df.select("name", explode_outer("items").alias("item")) \
  .filter(col("item").isNotNull()) \
  .show()
```

### Pattern 2: Count Items After Explosion
```python
# Count exploded items per group
df.select("name", explode("items").alias("item")) \
  .groupBy("name") \
  .count() \
  .show()
```

### Pattern 3: Preserve Original Data
```python
# Keep original array alongside exploded values
df.withColumn("item", explode("items")) \
  .select("name", "items", "item") \
  .show()
```

### Pattern 4: Handle Empty Arrays Gracefully
```python
from pyspark.sql.functions import when, size

# Add default value for empty arrays
df.withColumn("items_safe", 
              when(size("items") == 0, array(lit("no_items")))
              .otherwise(col("items"))) \
  .select("name", explode("items_safe").alias("item")) \
  .show()
```

## Performance Tips

1. **Use `explode()` over `explode_outer()`** when you don't need null preservation
2. **Filter before explosion** when possible to reduce data size
3. **Use `json_tuple()` for simple JSON parsing** instead of `from_json()` when you only need a few fields
4. **Consider `flatten()` before `explode()`** for nested arrays
5. **Cache DataFrames** after expensive operations like JSON parsing
