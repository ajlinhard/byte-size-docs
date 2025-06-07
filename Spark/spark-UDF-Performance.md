# UDF Performance
Here are several strategies to improve Spark UDF performance:

## 1. Use Pandas UDFs (Vectorized UDFs)
```python
from pyspark.sql.functions import pandas_udf
import pandas as pd

# Much faster than regular UDF
@pandas_udf(returnType=DoubleType())
def vectorized_calculation(values: pd.Series) -> pd.Series:
    return values * 2 + 10

# vs regular UDF (slower)
@udf(returnType=DoubleType())
def regular_calculation(value):
    return value * 2 + 10
```

## 2. Use Built-in Functions Instead
```python
from pyspark.sql.functions import *

# Instead of UDF for simple operations
# Bad:
@udf(returnType=StringType())
def categorize_age_udf(age):
    return "Adult" if age >= 18 else "Minor"

# Good: Use built-in when() function
df.withColumn("category", 
    when(col("age") >= 18, "Adult").otherwise("Minor")
)

# Instead of UDF for string operations
# Bad:
@udf(returnType=StringType())
def upper_case_udf(text):
    return text.upper()

# Good: Use built-in upper()
df.withColumn("upper_text", upper(col("text")))
```

## 3. Batch Processing with Grouped Map UDFs
```python
from pyspark.sql.types import *

# Process groups of data together
schema = StructType([
    StructField("id", IntegerType()),
    StructField("processed_value", DoubleType())
])

@pandas_udf(returnType=schema, functionType=PandasUDFType.GROUPED_MAP)
def process_group(pdf):
    # Process entire group at once
    pdf['processed_value'] = pdf['value'] * pdf['multiplier'].mean()
    return pdf[['id', 'processed_value']]

df.groupby("group_id").apply(process_group)
```

## 4. Minimize Data Serialization
```python
# Bad: Multiple UDF calls
df.withColumn("col1", udf1(col("input"))) \
  .withColumn("col2", udf2(col("input"))) \
  .withColumn("col3", udf3(col("input")))

# Good: Single UDF returning struct
from pyspark.sql.types import StructType, StructField

@udf(returnType=StructType([
    StructField("col1", StringType()),
    StructField("col2", IntegerType()),
    StructField("col3", DoubleType())
]))
def combined_processing(input_val):
    # Do all processing in one function
    return (process1(input_val), process2(input_val), process3(input_val))

df.withColumn("results", combined_processing(col("input"))) \
  .select("*", "results.col1", "results.col2", "results.col3")
```

## 5. Use Broadcast Variables for Lookups
```python
# Bad: Large dictionary in UDF closure
lookup_dict = {"A": 1, "B": 2, ...}  # Large dict

@udf(returnType=IntegerType())
def lookup_udf(key):
    return lookup_dict.get(key, 0)

# Good: Broadcast the lookup data
broadcast_lookup = spark.sparkContext.broadcast(lookup_dict)

@udf(returnType=IntegerType())
def broadcast_lookup_udf(key):
    return broadcast_lookup.value.get(key, 0)
```

## 6. Filter Before UDF Application
```python
# Bad: Apply UDF to all rows
df.withColumn("processed", expensive_udf(col("data")))

# Good: Filter first, then apply UDF
df.withColumn("processed", 
    when(col("should_process") == True, expensive_udf(col("data")))
    .otherwise(col("data"))
)
```

## 7. Use Iterator of Pandas UDFs for Large Datasets
```python
@pandas_udf(returnType=DoubleType(), functionType=PandasUDFType.SCALAR_ITER)
def process_batches(iterator):
    for batch in iterator:
        # Process batch of data
        yield batch * 2 + expensive_computation(batch)

df.withColumn("result", process_batches(col("values")))
```

## 8. Optimize Data Types
```python
# Use appropriate data types to reduce memory
@udf(returnType=IntegerType())  # Instead of StringType if returning numbers
def optimized_udf(value):
    return int(value * 100)
```

## 9. Cache Intermediate Results
```python
# Cache DataFrames before expensive UDF operations
df_filtered = df.filter(col("important_flag") == True).cache()
result = df_filtered.withColumn("expensive_calc", expensive_udf(col("data")))
```

## 10. Use SQL Functions When Possible
```python
# Many operations can be done in SQL without UDFs
spark.sql("""
    SELECT *,
           CASE WHEN age >= 18 THEN 'Adult' ELSE 'Minor' END as category,
           regexp_replace(phone, '[^0-9]', '') as clean_phone
    FROM my_table
""")
```

## Performance Hierarchy (Fastest to Slowest):
1. **Built-in Spark SQL functions** (fastest)
2. **Pandas UDFs / Vectorized UDFs**
3. **Python UDFs with broadcast variables**
4. **Regular Python UDFs** (slowest)

The key is to always try built-in functions first, then move to Pandas UDFs if custom logic is needed, and only use regular UDFs as a last resort.
