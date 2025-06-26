# Spark UDFs Overview
In Spark you can create user defined functions similar to how you would in most database or data lake environments. The functions can help with common use cases like standardizing hygienes or transformations. Below will be methods for creating UDFs right in python, however, note these can have bad performance compared to built-in functions and other UDF methods ([More Info on UDF Performance](https://github.com/ajlinhard/byte-size-docs/blob/main/Spark/spark-UDF-Performance.md)

### Table of Contents

- [Spark UDFs Overview](#spark-udfs-overview)
- [Basic Examples](#basic-examples)
  - [1. Basic UDF with `@udf` Decorator](#1-basic-udf-with-udf-decorator)
  - [2. Register UDF with `spark.udf.register()`](#2-register-udf-with-sparkudfregister)
  - [3. Complex Return Types](#3-complex-return-types)
  - [4. UDF with Multiple Parameters](#4-udf-with-multiple-parameters)
  - [5. Using External Libraries in UDFs](#5-using-external-libraries-in-udfs)
  - [6. Error Handling in UDFs](#6-error-handling-in-udfs)
  - [Performance Tips](#performance-tips)
  - [Pandas UDF (Better Performance)](#pandas-udf-better-performance)
- [Examples Class/Import of UDFs](#examples-classimport-of-udfs)
  - [Method 1: Direct Import and Registration (Recommended)](#method-1-direct-import-and-registration-recommended)
  - [Method 2: Registration in SparkSession for SQL Usage](#method-2-registration-in-sparksession-for-sql-usage)
  - [Method 3: UDF Class Pattern (For Complex UDFs)](#method-3-udf-class-pattern-for-complex-udfs)
  - [Best Practices](#best-practices)

---
# Basic Examples
Here are the main ways to write Spark UDFs in PySpark:

## 1. Basic UDF with `@udf` Decorator
```python
from pyspark.sql.functions import udf
from pyspark.sql.types import StringType, IntegerType

@udf(returnType=StringType())
def categorize_age(age):
    if age < 18:
        return "Minor"
    elif age < 65:
        return "Adult"
    else:
        return "Senior"

# Use it
df.withColumn("age_category", categorize_age(col("age"))).show()
```

## 2. Register UDF with `spark.udf.register()`
```python
def calculate_bonus(salary, performance):
    if performance > 90:
        return salary * 0.2
    elif performance > 75:
        return salary * 0.1
    else:
        return 0

# Register for DataFrame use
bonus_udf = udf(calculate_bonus, returnType=DoubleType())
df.withColumn("bonus", bonus_udf(col("salary"), col("performance"))).show()

# Register for SQL use
spark.udf.register("calculate_bonus_sql", calculate_bonus, DoubleType())
spark.sql("SELECT *, calculate_bonus_sql(salary, performance) as bonus FROM employees").show()
```

## 3. Complex Return Types
```python
from pyspark.sql.types import StructType, StructField, ArrayType

# UDF returning a struct
@udf(returnType=StructType([
    StructField("first", StringType()),
    StructField("last", StringType())
]))
def split_name(full_name):
    parts = full_name.split(" ", 1)
    return (parts[0], parts[1] if len(parts) > 1 else "")

df.withColumn("name_parts", split_name(col("full_name"))).show()

# UDF returning an array
@udf(returnType=ArrayType(StringType()))
def extract_keywords(text):
    return text.lower().split()

df.withColumn("keywords", extract_keywords(col("description"))).show()
```

## 4. UDF with Multiple Parameters
```python
@udf(returnType=StringType())
def format_address(street, city, state, zip_code):
    return f"{street}, {city}, {state} {zip_code}"

df.withColumn("full_address", 
    format_address(col("street"), col("city"), col("state"), col("zip"))
).show()
```

## 5. Using External Libraries in UDFs
```python
import re

@udf(returnType=StringType())
def clean_phone(phone):
    # Remove all non-digits
    digits_only = re.sub(r'\D', '', phone)
    if len(digits_only) == 10:
        return f"({digits_only[:3]}) {digits_only[3:6]}-{digits_only[6:]}"
    return phone

df.withColumn("clean_phone", clean_phone(col("phone_number"))).show()
```

## 6. Error Handling in UDFs
```python
@udf(returnType=StringType())
def safe_divide(numerator, denominator):
    try:
        if denominator == 0:
            return "Division by zero"
        return str(numerator / denominator)
    except Exception as e:
        return f"Error: {str(e)}"

df.withColumn("division_result", safe_divide(col("num1"), col("num2"))).show()
```

## Performance Tips:
- UDFs are slower than built-in Spark functions
- Try to use built-in functions first: `when()`, `regexp_replace()`, `split()`, etc.
- Consider vectorized UDFs (Pandas UDFs) for better performance on large datasets

## Pandas UDF (Better Performance)
```python
from pyspark.sql.functions import pandas_udf
import pandas as pd

@pandas_udf(returnType=DoubleType())
def pandas_calculate_bonus(salary_series: pd.Series, perf_series: pd.Series) -> pd.Series:
    return salary_series * 0.1 * (perf_series / 100)

df.withColumn("bonus", pandas_calculate_bonus(col("salary"), col("performance"))).show()
```

The key is specifying the correct return type and handling null values appropriately in your UDF logic.

---
# Examples Class/Import of UDFs
To import and use custom UDFs from another Python file in your PySpark class, you have several approaches. Here's how to do it effectively:

## Method 1: Direct Import and Registration (Recommended)

**udfs.py** (your UDF definitions file):
```python
from pyspark.sql.functions import udf
from pyspark.sql.types import StringType, IntegerType, DoubleType

# Define your UDF functions
def clean_string(text):
    if text is None:
        return None
    return text.strip().lower()

def calculate_score(value1, value2):
    if value1 is None or value2 is None:
        return 0
    return (value1 + value2) / 2

def extract_domain(email):
    if email is None or '@' not in email:
        return None
    return email.split('@')[1]

# Create UDF objects (but don't register globally yet)
clean_string_udf = udf(clean_string, StringType())
calculate_score_udf = udf(calculate_score, DoubleType())
extract_domain_udf = udf(extract_domain, StringType())
```

**main_spark_class.py** (your main PySpark class):
```python
from pyspark.sql import SparkSession
from udfs import clean_string_udf, calculate_score_udf, extract_domain_udf

class MySparkProcessor:
    def __init__(self):
        self.spark = SparkSession.builder \
            .appName("UDF Example") \
            .enableHiveSupport() \
            .getOrCreate()
    
    def process_data(self, df):
        # Use imported UDFs directly
        result_df = df \
            .withColumn("clean_name", clean_string_udf(df.name)) \
            .withColumn("avg_score", calculate_score_udf(df.score1, df.score2)) \
            .withColumn("email_domain", extract_domain_udf(df.email))
        
        return result_df
```

## Method 2: Registration in SparkSession for SQL Usage

**udfs.py**:
```python
from pyspark.sql.functions import udf
from pyspark.sql.types import StringType, IntegerType, DoubleType

def clean_string(text):
    if text is None:
        return None
    return text.strip().lower()

def calculate_score(value1, value2):
    if value1 is None or value2 is None:
        return 0
    return (value1 + value2) / 2

# Function to register all UDFs with a SparkSession
def register_udfs(spark):
    spark.udf.register("clean_string", clean_string, StringType())
    spark.udf.register("calculate_score", calculate_score, DoubleType())
    return spark
```

**main_spark_class.py**:
```python
from pyspark.sql import SparkSession
from udfs import register_udfs, clean_string_udf, calculate_score_udf

class MySparkProcessor:
    def __init__(self):
        self.spark = SparkSession.builder \
            .appName("UDF Example") \
            .enableHiveSupport() \
            .getOrCreate()
        
        # Register UDFs for SQL usage
        register_udfs(self.spark)
    
    def process_data_with_sql(self, df):
        # Create temp view
        df.createOrReplaceTempView("temp_table")
        
        # Use registered UDFs in SQL
        result_df = self.spark.sql("""
            SELECT *,
                   clean_string(name) as clean_name,
                   calculate_score(score1, score2) as avg_score
            FROM temp_table
        """)
        
        return result_df
    
    def process_data_with_dataframe_api(self, df):
        # Still works with DataFrame API
        return df.withColumn("clean_name", clean_string_udf(df.name))
```

## Method 3: UDF Class Pattern (For Complex UDFs)

**udfs.py**:
```python
from pyspark.sql.functions import udf
from pyspark.sql.types import StringType, StructType, StructField, IntegerType
import json

class DataProcessingUDFs:
    @staticmethod
    def complex_json_parser(json_string):
        try:
            data = json.loads(json_string)
            return data.get('important_field', 'default')
        except:
            return 'error'
    
    @staticmethod
    def business_logic_calculator(val1, val2, multiplier):
        if any(x is None for x in [val1, val2, multiplier]):
            return 0
        return (val1 * val2) * multiplier
    
    @classmethod
    def get_udfs(cls):
        """Return dictionary of all UDFs"""
        return {
            'parse_json': udf(cls.complex_json_parser, StringType()),
            'calculate_business_metric': udf(cls.business_logic_calculator, IntegerType())
        }
    
    @classmethod
    def register_all(cls, spark):
        """Register all UDFs with SparkSession"""
        udfs = cls.get_udfs()
        for name, udf_func in udfs.items():
            spark.udf.register(name, udf_func.func, udf_func.returnType)
```

**main_spark_class.py**:
```python
from pyspark.sql import SparkSession
from udfs import DataProcessingUDFs

class MySparkProcessor:
    def __init__(self):
        self.spark = SparkSession.builder \
            .appName("UDF Class Example") \
            .enableHiveSupport() \
            .getOrCreate()
        
        # Get UDFs and register them
        self.udfs = DataProcessingUDFs.get_udfs()
        DataProcessingUDFs.register_all(self.spark)
    
    def process_data(self, df):
        # Use UDFs from the class
        result_df = df \
            .withColumn("parsed_data", self.udfs['parse_json'](df.json_column)) \
            .withColumn("business_metric", self.udfs['calculate_business_metric'](
                df.value1, df.value2, df.multiplier
            ))
        
        return result_df
```

## Best Practices:

1. **Import only what you need** to avoid unnecessary overhead
2. **Register UDFs once** during initialization to avoid re-registration
3. **Use type hints** in your UDF functions for better code clarity
4. **Handle null values** explicitly in your UDF logic
5. **Consider performance** - UDFs are slower than built-in Spark functions
6. **Test UDFs separately** before integrating them into your main class

The first method (direct import) is usually the most straightforward and efficient for most use cases, while the registration method is useful when you need to use UDFs in SQL queries.
