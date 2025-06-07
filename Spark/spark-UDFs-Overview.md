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
