# PySpark JSON/Array Manipulations Cheat Sheet
I've created a comprehensive PySpark cheat sheet for JSON and array manipulations! This covers all the essential operations you'll need when working with complex data structures in PySpark, including:
Key sections covered:

JSON string parsing and schema handling
Array creation, manipulation, and aggregation
Exploding arrays and structs into rows
Advanced nested JSON operations
Array filtering and transformation with lambda functions
Working with maps (key-value pairs)
Performance optimization tips
Common patterns and best practices

The cheat sheet includes practical examples for each operation, from basic array operations like array_contains() and array_sort() to more advanced scenarios like processing complex nested JSON log data.
This should serve as a handy reference for all your PySpark JSON and array manipulation needs! The examples are designed to be copy-pasteable and easily adaptable to your specific use cases.

## Setup and Imports

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
import json

spark = SparkSession.builder.appName("JSON Array Operations").getOrCreate()
```

## Working with JSON Strings

### Parsing JSON from String Column

```python
# Sample data with JSON strings
json_data = [
    ('{"name": "John", "age": 30, "city": "NYC"}',),
    ('{"name": "Jane", "age": 25, "city": "LA"}',),
]
df = spark.createDataFrame(json_data, ["json_str"])

# Parse JSON string to struct
df_parsed = df.select(
    from_json(col("json_str"), 
              StructType([
                  StructField("name", StringType()),
                  StructField("age", IntegerType()),
                  StructField("city", StringType())
              ])).alias("parsed_json")
)

# Extract fields from parsed JSON
df_extracted = df_parsed.select(
    col("parsed_json.name").alias("name"),
    col("parsed_json.age").alias("age"),
    col("parsed_json.city").alias("city")
)
```

### Auto-infer JSON Schema

```python
# Let Spark infer the schema
sample_json = '{"name": "John", "age": 30, "address": {"street": "123 Main St", "zip": "10001"}}'
schema = spark.read.json(spark.sparkContext.parallelize([sample_json])).schema

# Use inferred schema
df_with_schema = df.select(from_json(col("json_str"), schema).alias("data"))
```

### Converting Struct to JSON String

```python
# Convert struct back to JSON string
df_to_json = df_extracted.select(
    to_json(struct("name", "age", "city")).alias("json_output")
)
```

## Array Operations

### Creating Arrays

```python
# Create array from multiple columns
df_arrays = spark.createDataFrame([
    ("John", 25, 30),
    ("Jane", 22, 28),
], ["name", "score1", "score2"])

df_with_array = df_arrays.select(
    col("name"),
    array(col("score1"), col("score2")).alias("scores")
)

# Create array with literals
df_literal_array = df_arrays.select(
    col("name"),
    array(lit(1), lit(2), lit(3)).alias("fixed_array")
)
```

### Array Manipulation Functions

```python
# Array size
df.select(size(col("scores")).alias("array_size"))

# Check if array contains element
df.select(array_contains(col("scores"), 25).alias("contains_25"))

# Get array element by index (0-based)
df.select(col("scores")[0].alias("first_score"))

# Sort array
df.select(array_sort(col("scores")).alias("sorted_scores"))

# Remove duplicates from array
df.select(array_distinct(col("scores")).alias("unique_scores"))

# Array intersection
df.select(array_intersect(col("scores"), array(lit(25), lit(30))).alias("intersection"))

# Array union
df.select(array_union(col("scores"), array(lit(35))).alias("union_scores"))

# Array except (difference)
df.select(array_except(col("scores"), array(lit(25))).alias("except_25"))
```

### Working with Array of Structs

```python
# Sample data with array of structs
complex_data = [
    ("John", [{"course": "Math", "grade": 85}, {"course": "Science", "grade": 92}]),
    ("Jane", [{"course": "Math", "grade": 78}, {"course": "Science", "grade": 88}]),
]

schema = StructType([
    StructField("name", StringType()),
    StructField("grades", ArrayType(StructType([
        StructField("course", StringType()),
        StructField("grade", IntegerType())
    ])))
])

df_complex = spark.createDataFrame(complex_data, schema)

# Access nested fields in array of structs
df_complex.select(
    col("name"),
    col("grades")[0].course.alias("first_course"),
    col("grades")[0].grade.alias("first_grade")
).show()
```

## Exploding Arrays and Structs

### Basic Explode Operations

```python
# Explode array to multiple rows
df_exploded = df_with_array.select(
    col("name"),
    explode(col("scores")).alias("individual_score")
)

# Explode with position (index)
df_exploded_pos = df_with_array.select(
    col("name"),
    posexplode(col("scores")).alias("pos", "score")
)

# Explode array of structs
df_grades_exploded = df_complex.select(
    col("name"),
    explode(col("grades")).alias("grade_info")
).select(
    col("name"),
    col("grade_info.course"),
    col("grade_info.grade")
)
```

### Outer Explode (includes nulls)

```python
# explode_outer keeps rows even if array is null/empty
df_with_nulls = spark.createDataFrame([
    ("John", [1, 2, 3]),
    ("Jane", None),
    ("Bob", [])
], ["name", "numbers"])

df_outer_exploded = df_with_nulls.select(
    col("name"),
    explode_outer(col("numbers")).alias("number")
)
```

## Advanced JSON Operations

### Working with Nested JSON

```python
# Complex nested JSON
nested_json_data = [
    ('{"user": {"name": "John", "profile": {"age": 30, "skills": ["Python", "Spark"]}}}',),
    ('{"user": {"name": "Jane", "profile": {"age": 25, "skills": ["Java", "Scala"]}}}',)
]

df_nested = spark.createDataFrame(nested_json_data, ["json_str"])

# Define nested schema
nested_schema = StructType([
    StructField("user", StructType([
        StructField("name", StringType()),
        StructField("profile", StructType([
            StructField("age", IntegerType()),
            StructField("skills", ArrayType(StringType()))
        ]))
    ]))
])

# Parse and extract nested data
df_nested_parsed = df_nested.select(
    from_json(col("json_str"), nested_schema).alias("data")
).select(
    col("data.user.name").alias("name"),
    col("data.user.profile.age").alias("age"),
    col("data.user.profile.skills").alias("skills")
)
```

### JSON Path Extraction

```python
# Extract using get_json_object (JSONPath)
df_json_path = df_nested.select(
    get_json_object(col("json_str"), "$.user.name").alias("name"),
    get_json_object(col("json_str"), "$.user.profile.age").alias("age"),
    get_json_object(col("json_str"), "$.user.profile.skills[0]").alias("first_skill")
)

# Extract multiple values using json_tuple
df_json_tuple = df_nested.select(
    json_tuple(col("json_str"), "user.name", "user.profile.age").alias("name", "age")
)
```

## Array Aggregations

### Collect Operations

```python
# Sample data for aggregation
agg_data = [
    ("Math", "John", 85),
    ("Math", "Jane", 78),
    ("Science", "John", 92),
    ("Science", "Jane", 88),
]

df_agg = spark.createDataFrame(agg_data, ["subject", "student", "grade"])

# Collect list (with duplicates)
df_collected = df_agg.groupBy("subject").agg(
    collect_list("student").alias("students"),
    collect_list("grade").alias("grades")
)

# Collect set (unique values only)
df_collected_set = df_agg.groupBy("subject").agg(
    collect_set("student").alias("unique_students")
)
```

### Array Aggregation Functions

```python
# Sample data with arrays
array_agg_data = [
    ("John", [85, 92, 78]),
    ("Jane", [88, 76, 82]),
]

df_array_agg = spark.createDataFrame(array_agg_data, ["name", "scores"])

# Aggregate functions on arrays
df_array_stats = df_array_agg.select(
    col("name"),
    array_max(col("scores")).alias("max_score"),
    array_min(col("scores")).alias("min_score"),
    size(col("scores")).alias("num_scores")
)

# Custom aggregation with aggregate function
df_sum_scores = df_array_agg.select(
    col("name"),
    aggregate(
        col("scores"),
        lit(0),  # initial value
        lambda acc, x: acc + x  # merge function
    ).alias("total_score")
)
```

## Filtering and Transforming Arrays

### Array Filtering

```python
# Filter array elements
df_filtered = df_array_agg.select(
    col("name"),
    filter(col("scores"), lambda x: x > 80).alias("high_scores")
)

# Check if any element satisfies condition
df_exists = df_array_agg.select(
    col("name"),
    exists(col("scores"), lambda x: x > 90).alias("has_high_score")
)

# Check if all elements satisfy condition
df_forall = df_array_agg.select(
    col("name"),
    forall(col("scores"), lambda x: x > 70).alias("all_passing")
)
```

### Array Transformation

```python
# Transform array elements
df_transformed = df_array_agg.select(
    col("name"),
    transform(col("scores"), lambda x: x * 1.1).alias("curved_scores")
)

# Map with index
df_map_with_index = df_array_agg.select(
    col("name"),
    transform(
        sequence(lit(0), size(col("scores")) - 1),
        lambda i: struct(
            (i + 1).alias("position"),
            col("scores")[i].alias("score")
        )
    ).alias("indexed_scores")
)
```

## Working with Maps (Key-Value Pairs)

### Creating and Manipulating Maps

```python
# Create map from arrays
map_data = [
    ("John", ["math", "science"], [85, 92]),
    ("Jane", ["math", "science"], [78, 88]),
]

df_map = spark.createDataFrame(map_data, ["name", "subjects", "grades"])

df_with_map = df_map.select(
    col("name"),
    map_from_arrays(col("subjects"), col("grades")).alias("grade_map")
)

# Access map values
df_map_access = df_with_map.select(
    col("name"),
    col("grade_map")["math"].alias("math_grade"),
    map_keys(col("grade_map")).alias("subjects"),
    map_values(col("grade_map")).alias("grades")
)

# Convert map to array of structs
df_map_to_array = df_with_map.select(
    col("name"),
    map_entries(col("grade_map")).alias("grade_entries")
)
```

## Combining JSON and Array Operations

### Real-world Example: Processing Log Data

```python
# Sample log data with JSON
log_data = [
    ('{"timestamp": "2023-01-01T10:00:00", "events": [{"type": "click", "count": 5}, {"type": "view", "count": 10}]}',),
    ('{"timestamp": "2023-01-01T11:00:00", "events": [{"type": "click", "count": 3}, {"type": "purchase", "count": 1}]}',)
]

df_logs = spark.createDataFrame(log_data, ["log_json"])

# Define schema for log data
log_schema = StructType([
    StructField("timestamp", StringType()),
    StructField("events", ArrayType(StructType([
        StructField("type", StringType()),
        StructField("count", IntegerType())
    ])))
])

# Parse and process log data
df_processed_logs = df_logs.select(
    from_json(col("log_json"), log_schema).alias("log_data")
).select(
    col("log_data.timestamp"),
    explode(col("log_data.events")).alias("event")
).select(
    col("timestamp"),
    col("event.type").alias("event_type"),
    col("event.count").alias("event_count")
)

# Aggregate by event type
df_event_summary = df_processed_logs.groupBy("event_type").agg(
    sum("event_count").alias("total_count"),
    collect_list("timestamp").alias("timestamps")
)
```

## Performance Tips

```python
# Cache frequently accessed DataFrames with complex operations
df_complex.cache()

# Use broadcast for small lookup tables
broadcast_df = broadcast(small_lookup_df)
result = large_df.join(broadcast_df, "key")

# Repartition before expensive operations
df_repartitioned = df.repartition(200, "partition_key")

# Use coalesce for small result sets
df_result.coalesce(1).write.mode("overwrite").json("output_path")
```

## Common Patterns and Best Practices

```python
# Pattern 1: Safely handle null arrays
df.select(
    col("name"),
    when(col("scores").isNull(), array()).otherwise(col("scores")).alias("safe_scores")
)

# Pattern 2: Flatten nested arrays
df.select(
    col("name"),
    flatten(col("nested_arrays")).alias("flattened")
)

# Pattern 3: Create struct from multiple columns for JSON conversion
df.select(
    to_json(struct("*")).alias("row_as_json")
)

# Pattern 4: Handle schema evolution with try-catch equivalent
df.select(
    col("name"),
    when(col("data").isNotNull(), 
         from_json(col("data"), target_schema)).alias("parsed_data")
)
```
