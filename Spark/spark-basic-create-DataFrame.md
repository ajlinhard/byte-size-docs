# Create DataFrame
When it comes to creating Data Frames there are examples ranging from simple to creative use cases.I've created a comprehensive PySpark `createDataFrame` cheat sheet that covers:

**Key Features:**
- **Detailed parameter table** with types, defaults, and descriptions
- **Multiple schema definition methods** (automatic, string, list, StructType)
- **Progressive examples** from simple to complex to creative
- **Best practices** and performance tips
- **Common errors** and their solutions

**Example Categories:**
- **Simple**: Basic lists, dictionaries, pandas DataFrames
- **Complex**: Nested structures, arrays, maps, RDDs with explicit schemas
- **Creative**: IoT sensor data, JSON-like structures, ML matrix data

The cheat sheet includes practical patterns like handling large datasets with sampling ratios, working with nested data structures, and performance optimization techniques. Each example is fully functional and demonstrates different aspects of the `createDataFrame` method.

This should serve as a comprehensive reference for anyone working with PySpark DataFrame creation, from beginners to advanced users dealing with complex data structures.
---
# PySpark createDataFrame Cheat Sheet

## Method Signature

```python
spark.createDataFrame(data, schema=None, samplingRatio=None, verifySchema=True)
```

## Parameter Details

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `data` | `RDD`, `list`, `pandas.DataFrame`, `numpy.ndarray` | Required | The data source for the DataFrame |
| `schema` | `pyspark.sql.types.StructType`, `list`, `str`, `None` | `None` | Schema definition for the DataFrame |
| `samplingRatio` | `float` | `None` | Sampling ratio for schema inference (0.0 to 1.0) |
| `verifySchema` | `bool` | `True` | Whether to verify the schema against the data |

## Schema Definition Options

### 1. Automatic Schema Inference (schema=None)
- PySpark automatically infers schema from data
- Works with lists of tuples, dictionaries, or pandas DataFrames
- May be slow for large datasets

### 2. String Schema
```python
schema = "name STRING, age INT, salary DOUBLE"
```

### 3. List of Column Names
```python
schema = ["name", "age", "salary"]  # All columns default to STRING type
```

### 4. StructType Schema (Most Flexible)
```python
from pyspark.sql.types import StructType, StructField, StringType, IntegerType

schema = StructType([
    StructField("name", StringType(), True),
    StructField("age", IntegerType(), True)
])
```

## Simple Examples

### From List of Tuples
```python
# Basic list of tuples
data = [("Alice", 25), ("Bob", 30), ("Charlie", 35)]
df = spark.createDataFrame(data, ["name", "age"])
df.show()
```

### From List of Dictionaries
```python
# List of dictionaries (automatic schema inference)
data = [
    {"name": "Alice", "age": 25, "city": "New York"},
    {"name": "Bob", "age": 30, "city": "San Francisco"},
    {"name": "Charlie", "age": 35, "city": "Chicago"}
]
df = spark.createDataFrame(data)
df.show()
```

### From Pandas DataFrame
```python
import pandas as pd

# Convert pandas DataFrame to Spark DataFrame
pdf = pd.DataFrame({
    'name': ['Alice', 'Bob', 'Charlie'],
    'age': [25, 30, 35],
    'salary': [50000.0, 60000.0, 70000.0]
})
df = spark.createDataFrame(pdf)
df.show()
```

## Complex Examples

### With Explicit Schema and Nested Data
```python
from pyspark.sql.types import *

# Complex schema with nested structures
schema = StructType([
    StructField("employee_id", IntegerType(), False),
    StructField("personal_info", StructType([
        StructField("name", StringType(), True),
        StructField("age", IntegerType(), True),
        StructField("email", StringType(), True)
    ]), True),
    StructField("skills", ArrayType(StringType()), True),
    StructField("salary", DoubleType(), True),
    StructField("hire_date", DateType(), True)
])

from datetime import date

data = [
    (1, ("Alice Johnson", 28, "alice@company.com"), ["Python", "SQL", "Spark"], 75000.0, date(2022, 1, 15)),
    (2, ("Bob Smith", 32, "bob@company.com"), ["Java", "Scala", "Kafka"], 85000.0, date(2021, 3, 10)),
    (3, ("Carol Davis", 29, "carol@company.com"), ["Python", "Machine Learning", "TensorFlow"], 90000.0, date(2020, 8, 22))
]

df = spark.createDataFrame(data, schema)
df.show(truncate=False)
df.printSchema()
```

### With Sampling Ratio for Large Datasets
```python
# For very large datasets, use sampling for schema inference
import random

# Generate large dataset
large_data = [
    {"id": i, "value": random.uniform(0, 100), "category": f"cat_{i%5}"}
    for i in range(100000)
]

# Use sampling ratio to speed up schema inference
df = spark.createDataFrame(large_data, samplingRatio=0.1)
df.show(5)
```

### From RDD
```python
# Create DataFrame from RDD
rdd = spark.sparkContext.parallelize([
    ("Alice", 25, "Engineer"),
    ("Bob", 30, "Manager"),
    ("Charlie", 35, "Analyst")
])

# With schema inference
df1 = spark.createDataFrame(rdd, ["name", "age", "role"])

# With explicit schema
schema = StructType([
    StructField("name", StringType(), True),
    StructField("age", IntegerType(), True),
    StructField("role", StringType(), True)
])
df2 = spark.createDataFrame(rdd, schema)
```

## Creative Examples

### Time Series Data with Complex Types
```python
from pyspark.sql.types import *
from datetime import datetime, timedelta
import random

# Schema for IoT sensor data
schema = StructType([
    StructField("sensor_id", StringType(), False),
    StructField("timestamp", TimestampType(), False),
    StructField("location", StructType([
        StructField("latitude", DoubleType(), True),
        StructField("longitude", DoubleType(), True),
        StructField("altitude", DoubleType(), True)
    ]), True),
    StructField("readings", MapType(StringType(), DoubleType()), True),
    StructField("status", StringType(), True)
])

# Generate synthetic IoT data
base_time = datetime.now()
data = []
for i in range(10):
    sensor_data = (
        f"sensor_{i:03d}",
        base_time + timedelta(minutes=i*5),
        (40.7128 + random.uniform(-0.1, 0.1), -74.0060 + random.uniform(-0.1, 0.1), random.uniform(0, 100)),
        {
            "temperature": round(random.uniform(20, 30), 2),
            "humidity": round(random.uniform(40, 60), 2),
            "pressure": round(random.uniform(1000, 1020), 2)
        },
        random.choice(["active", "inactive", "maintenance"])
    )
    data.append(sensor_data)

df = spark.createDataFrame(data, schema)
df.show(truncate=False)
```

### JSON-like Data with Dynamic Schema
```python
# Simulating JSON data with varying structures
json_like_data = [
    {
        "user_id": "user_001",
        "event_type": "login",
        "timestamp": "2023-01-01T10:00:00",
        "properties": {
            "device": "mobile",
            "os": "iOS",
            "version": "14.0"
        }
    },
    {
        "user_id": "user_002", 
        "event_type": "purchase",
        "timestamp": "2023-01-01T11:00:00",
        "properties": {
            "product_id": "prod_123",
            "amount": 29.99,
            "currency": "USD",
            "payment_method": "credit_card"
        }
    },
    {
        "user_id": "user_003",
        "event_type": "page_view",
        "timestamp": "2023-01-01T12:00:00", 
        "properties": {
            "page": "/products",
            "referrer": "google.com",
            "session_duration": 120
        }
    }
]

# Let PySpark infer the schema for flexible JSON-like data
df = spark.createDataFrame(json_like_data)
df.show(truncate=False)
df.printSchema()
```

### Matrix Data for Machine Learning
```python
import numpy as np
from pyspark.sql.types import *

# Create matrix-like data for ML workflows
np.random.seed(42)
n_samples = 1000
n_features = 10

# Generate feature matrix
features = np.random.randn(n_samples, n_features)
labels = np.random.randint(0, 3, n_samples)  # 3 classes

# Create DataFrame with array columns
schema = StructType([
    StructField("id", IntegerType(), False),
    StructField("features", ArrayType(DoubleType()), True),
    StructField("label", IntegerType(), True)
])

data = [
    (i, features[i].tolist(), int(labels[i])) 
    for i in range(n_samples)
]

ml_df = spark.createDataFrame(data, schema)
ml_df.show(5, truncate=False)
```

## Best Practices

### 1. Always Define Schema for Production
```python
# Good: Explicit schema for performance and reliability
schema = StructType([
    StructField("id", IntegerType(), False),
    StructField("name", StringType(), True),
    StructField("created_at", TimestampType(), True)
])
df = spark.createDataFrame(data, schema)
```

### 2. Use Sampling for Large Datasets
```python
# For large datasets, use sampling to speed up schema inference
df = spark.createDataFrame(large_data, samplingRatio=0.01)
```

### 3. Handle Null Values Explicitly
```python
# Define nullable fields appropriately
schema = StructType([
    StructField("id", IntegerType(), False),      # Non-nullable
    StructField("name", StringType(), True),     # Nullable
    StructField("email", StringType(), False)    # Non-nullable
])
```

### 4. Verify Schema When Needed
```python
# Disable verification for better performance when schema is guaranteed
df = spark.createDataFrame(data, schema, verifySchema=False)
```

## Common Errors and Solutions

### Error: "Can not merge type"
```python
# Problem: Inconsistent data types
data = [("Alice", 25), ("Bob", "thirty")]  # Mixed types

# Solution: Clean data or use explicit schema
cleaned_data = [("Alice", 25), ("Bob", 30)]
df = spark.createDataFrame(cleaned_data, ["name", "age"])
```

### Error: "Unsupported type"
```python
# Problem: Unsupported Python type
import datetime
data = [("Alice", datetime.datetime.now())]

# Solution: Use supported types or convert
from pyspark.sql.types import TimestampType
schema = StructType([
    StructField("name", StringType(), True),
    StructField("timestamp", TimestampType(), True)
])
df = spark.createDataFrame(data, schema)
```

## Performance Tips

1. **Use explicit schemas** to avoid inference overhead
2. **Set appropriate sampling ratios** for large datasets
3. **Disable schema verification** when data is guaranteed to be clean
4. **Use appropriate data types** to minimize memory usage
5. **Consider partitioning** for very large DataFrames

## Memory Considerations

```python
# For large datasets, consider creating DataFrame in chunks
def create_large_dataframe(data_generator, schema, chunk_size=10000):
    dfs = []
    chunk = []
    
    for item in data_generator:
        chunk.append(item)
        if len(chunk) >= chunk_size:
            dfs.append(spark.createDataFrame(chunk, schema))
            chunk = []
    
    if chunk:  # Handle remaining items
        dfs.append(spark.createDataFrame(chunk, schema))
    
    # Union all chunks
    result_df = dfs[0]
    for df in dfs[1:]:
        result_df = result_df.union(df)
    
    return result_df
```
