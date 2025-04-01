# Spark Data Types:
I've created a comprehensive PySpark Data Types cheatsheet for you that covers all the requested data types with definitions, code examples for creating each type, and common transformations.

The cheatsheet is organized into these sections:
1. **Simple Data Types** - Includes StringType, CharType, VarcharType, BooleanType, and BinaryType
2. **Numeric Data Types** - Covers ByteType, ShortType, IntegerType, LongType, FloatType, DoubleType, and DecimalType
3. **Date and Time Data Types** - Contains DateType, TimestampType, TimestampNTZType, DayTimeIntervalType, and YearMonthIntervalType
4. **Complex Data Types** - Explains ArrayType, MapType, StructType/StructField, and NullType
5. **DataType Base Class** - Brief explanation of the base class
6. **Type Conversions** - Examples of converting between different data types

# PySpark Data Types Cheatsheet

## Importing Data Types
```python
from pyspark.sql.types import *
```

## Simple Data Types

### StringType
**Definition:** Represents string values in PySpark.

```python
# Creating a schema with StringType
from pyspark.sql.types import StructType, StructField, StringType

# Create a DataFrame with StringType
schema = StructType([StructField("name", StringType(), False)])
data = [("John",), ("Alice",)]
df = spark.createDataFrame(data, schema)

# Transformations
from pyspark.sql.functions import col, upper, concat, length

# Convert to uppercase
df = df.withColumn("name_upper", upper(col("name")))

# Get string length
df = df.withColumn("name_length", length(col("name")))

# Concatenate strings
df = df.withColumn("greeting", concat(col("name"), lit(" says hello!")))
```

### CharType
**Definition:** Fixed-length character string.

```python
# Creating a schema with CharType
from pyspark.sql.types import CharType

schema = StructType([StructField("code", CharType(2), False)])
data = [("US",), ("UK",)]
df = spark.createDataFrame(data, schema)

# Transformations similar to StringType
# Note: CharType will pad strings shorter than the specified length
```

### VarcharType
**Definition:** Variable-length character string with maximum length.

```python
# Creating a schema with VarcharType
from pyspark.sql.types import VarcharType

schema = StructType([StructField("name", VarcharType(10), False)])
data = [("John",), ("Alexander",)]  # "Alexander" will be truncated to length 10
df = spark.createDataFrame(data, schema)

# Transformations similar to StringType
```

### BooleanType
**Definition:** Represents boolean (true/false) values.

```python
# Creating a schema with BooleanType
schema = StructType([StructField("is_active", BooleanType(), False)])
data = [(True,), (False,)]
df = spark.createDataFrame(data, schema)

# Transformations
from pyspark.sql.functions import not

# Logical NOT
df = df.withColumn("is_inactive", ~col("is_active"))

# Filter based on boolean
active_users = df.filter(col("is_active") == True)
```

### BinaryType
**Definition:** Represents binary (byte array) data.

```python
# Creating a schema with BinaryType
import array

schema = StructType([StructField("data", BinaryType(), False)])
data = [(bytearray([65, 66, 67]),)]  # ABC in ASCII
df = spark.createDataFrame(data, schema)

# Transformations
from pyspark.sql.functions import base64, unbase64

# Convert binary to base64 string
df = df.withColumn("data_base64", base64(col("data")))

# Convert base64 back to binary
df = df.withColumn("data_decoded", unbase64(col("data_base64")))
```

## Numeric Data Types

### ByteType
**Definition:** 1-byte signed integer (-128 to 127).

```python
# Creating a schema with ByteType
schema = StructType([StructField("value", ByteType(), False)])
data = [(100,), (-10,)]
df = spark.createDataFrame(data, schema)

# Transformations
df = df.withColumn("double_value", col("value") * 2)
df = df.withColumn("abs_value", abs(col("value")))
```

### ShortType
**Definition:** 2-byte signed integer (-32,768 to 32,767).

```python
# Creating a schema with ShortType
schema = StructType([StructField("value", ShortType(), False)])
data = [(1000,), (-1000,)]
df = spark.createDataFrame(data, schema)

# Transformations (similar to ByteType)
```

### IntegerType
**Definition:** 4-byte signed integer (-2,147,483,648 to 2,147,483,647).

```python
# Creating a schema with IntegerType
schema = StructType([StructField("value", IntegerType(), False)])
data = [(100000,), (-100000,)]
df = spark.createDataFrame(data, schema)

# Transformations
from pyspark.sql.functions import expr

df = df.withColumn("squared", col("value") * col("value"))
df = df.withColumn("mod_10", expr("value % 10"))
```

### LongType
**Definition:** 8-byte signed integer (-9,223,372,036,854,775,808 to 9,223,372,036,854,775,807).

```python
# Creating a schema with LongType
schema = StructType([StructField("value", LongType(), False)])
data = [(9999999999,), (-9999999999,)]
df = spark.createDataFrame(data, schema)

# Transformations (similar to IntegerType)
```

### FloatType
**Definition:** 4-byte single-precision floating point number.

```python
# Creating a schema with FloatType
schema = StructType([StructField("value", FloatType(), False)])
data = [(3.14,), (-2.718,)]
df = spark.createDataFrame(data, schema)

# Transformations
from pyspark.sql.functions import round, ceil, floor

df = df.withColumn("rounded", round(col("value"), 1))
df = df.withColumn("ceiling", ceil(col("value")))
df = df.withColumn("floor", floor(col("value")))
```

### DoubleType
**Definition:** 8-byte double-precision floating point number.

```python
# Creating a schema with DoubleType
schema = StructType([StructField("value", DoubleType(), False)])
data = [(3.14159265359,), (-2.7182818284,)]
df = spark.createDataFrame(data, schema)

# Transformations (similar to FloatType)
from pyspark.sql.functions import log, exp, pow

df = df.withColumn("log_value", log(abs(col("value"))))
df = df.withColumn("exp_value", exp(col("value")))
df = df.withColumn("power", pow(col("value"), 2))
```

### DecimalType
**Definition:** Arbitrary-precision decimal numbers with user-defined precision and scale.

```python
# Creating a schema with DecimalType
from decimal import Decimal

# DecimalType(precision, scale) - precision is total digits, scale is decimal digits
schema = StructType([StructField("value", DecimalType(10, 2), False)])
data = [(Decimal("1234.56"),), (Decimal("-789.01"),)]
df = spark.createDataFrame(data, schema)

# Transformations
df = df.withColumn("multiplied", col("value") * 2)
df = df.withColumn("divided", col("value") / 2)

# Convert between decimal and other types
df = df.withColumn("as_double", col("value").cast(DoubleType()))
df = df.withColumn("as_integer", col("value").cast(IntegerType()))
```

## Date and Time Data Types

### DateType
**Definition:** Represents a date (year, month, day).

```python
# Creating a schema with DateType
from datetime import date

schema = StructType([StructField("date", DateType(), False)])
data = [(date(2023, 1, 1),), (date(2023, 12, 31),)]
df = spark.createDataFrame(data, schema)

# Transformations
from pyspark.sql.functions import current_date, datediff, add_months, date_format, year, month, dayofmonth

# Current date
df = df.withColumn("current", current_date())

# Date difference in days
df = df.withColumn("days_diff", datediff(current_date(), col("date")))

# Add months
df = df.withColumn("plus_3_months", add_months(col("date"), 3))

# Format date as string
df = df.withColumn("formatted", date_format(col("date"), "yyyy-MM-dd"))

# Extract components
df = df.withColumn("year", year(col("date")))
df = df.withColumn("month", month(col("date")))
df = df.withColumn("day", dayofmonth(col("date")))
```

### TimestampType
**Definition:** Represents a timestamp (date and time) with timezone awareness.

```python
# Creating a schema with TimestampType
from datetime import datetime

schema = StructType([StructField("timestamp", TimestampType(), False)])
data = [(datetime(2023, 1, 1, 12, 0, 0),), (datetime(2023, 12, 31, 23, 59, 59),)]
df = spark.createDataFrame(data, schema)

# Transformations
from pyspark.sql.functions import current_timestamp, unix_timestamp, from_unixtime, hour, minute, second

# Current timestamp
df = df.withColumn("current", current_timestamp())

# Convert to Unix timestamp (seconds since epoch)
df = df.withColumn("unix_time", unix_timestamp(col("timestamp")))

# Convert from Unix timestamp back to timestamp
df = df.withColumn("from_unix", from_unixtime(col("unix_time")))

# Extract components
df = df.withColumn("date_part", col("timestamp").cast(DateType()))
df = df.withColumn("hour", hour(col("timestamp")))
df = df.withColumn("minute", minute(col("timestamp")))
df = df.withColumn("second", second(col("timestamp")))
```

### TimestampNTZType
**Definition:** Represents a timestamp (date and time) without timezone awareness.

```python
# Creating a schema with TimestampNTZType
from datetime import datetime

schema = StructType([StructField("timestamp_ntz", TimestampNTZType(), False)])
data = [(datetime(2023, 1, 1, 12, 0, 0),), (datetime(2023, 12, 31, 23, 59, 59),)]
df = spark.createDataFrame(data, schema)

# Transformations similar to TimestampType
# The main difference is TimestampNTZType doesn't account for timezone conversions
```

### DayTimeIntervalType
**Definition:** Represents a day-time interval (days, hours, minutes, seconds).

```python
# Creating a schema with DayTimeIntervalType
from pyspark.sql.functions import make_interval

schema = StructType([StructField("interval", DayTimeIntervalType(), False)])
# Creating intervals using make_interval function
df = spark.createDataFrame([(1,)], ["dummy"])
df = df.withColumn("interval", make_interval(0, 0, 2, 12, 30, 0))  # 2 days, 12 hours, 30 minutes

# Transformations
from pyspark.sql.functions import col

# Add interval to timestamp
df = df.withColumn("timestamp", current_timestamp())
df = df.withColumn("future_time", col("timestamp") + col("interval"))
```

### YearMonthIntervalType
**Definition:** Represents a year-month interval (years, months).

```python
# Creating a schema with YearMonthIntervalType
from pyspark.sql.functions import make_interval

schema = StructType([StructField("interval", YearMonthIntervalType(), False)])
# Creating intervals using make_interval function
df = spark.createDataFrame([(1,)], ["dummy"])
df = df.withColumn("interval", make_interval(2, 6, 0, 0, 0, 0))  # 2 years, 6 months

# Transformations
# Add interval to date
df = df.withColumn("date", current_date())
df = df.withColumn("future_date", add_months(col("date"), col("interval") / make_interval(0, 1, 0, 0, 0, 0)))
```

## Complex Data Types

### ArrayType
**Definition:** Represents an array of elements of specific data type.

```python
# Creating a schema with ArrayType
schema = StructType([StructField("values", ArrayType(IntegerType()), False)])
data = [([1, 2, 3],), ([4, 5],)]
df = spark.createDataFrame(data, schema)

# Transformations
from pyspark.sql.functions import array, array_contains, explode, size, element_at

# Create array from columns
df = df.withColumn("doubled", array([col("values")[i] * 2 for i in range(3)]))

# Check if array contains element
df = df.withColumn("contains_2", array_contains(col("values"), 2))

# Get array size
df = df.withColumn("array_size", size(col("values")))

# Get element at position (1-based indexing)
df = df.withColumn("first_element", element_at(col("values"), 1))

# Explode array into rows
exploded_df = df.select("*", explode("values").alias("single_value"))
```

### MapType
**Definition:** Represents a map of key-value pairs with specified key and value data types.

```python
# Creating a schema with MapType
schema = StructType([StructField("attributes", MapType(StringType(), IntegerType()), False)])
data = [({"age": 30, "id": 123},), ({"age": 25, "id": 456},)]
df = spark.createDataFrame(data, schema)

# Transformations
from pyspark.sql.functions import map_keys, map_values, create_map, explode_outer

# Get map keys/values
df = df.withColumn("keys", map_keys(col("attributes")))
df = df.withColumn("values", map_values(col("attributes")))

# Access specific key
df = df.withColumn("age", col("attributes")["age"])

# Create map from columns
df = df.withColumn("id_map", create_map(lit("user_id"), col("attributes")["id"]))

# Explode map into rows of key-value pairs
exploded_df = df.select("*", explode_outer("attributes").alias("key", "value"))
```

### StructType and StructField
**Definition:** 
- **StructType:** Represents a complex structure like a record with multiple fields.
- **StructField:** Represents a field in a StructType with name, data type, and nullable flag.

```python
# Creating a schema with nested StructType
from pyspark.sql.types import StructType, StructField, StringType, IntegerType

# Define address struct type
address_struct = StructType([
    StructField("street", StringType(), True),
    StructField("city", StringType(), True),
    StructField("zip", StringType(), True)
])

# Define person struct type with nested address
person_struct = StructType([
    StructField("name", StringType(), False),
    StructField("age", IntegerType(), True),
    StructField("address", address_struct, True)
])

# Create data with nested structures
data = [
    ("John", 30, ("123 Main St", "New York", "10001")),
    ("Alice", 25, ("456 Elm St", "Boston", "02101"))
]

df = spark.createDataFrame(data, person_struct)

# Transformations
# Access nested fields
df = df.withColumn("city", col("address.city"))

# Create new struct
from pyspark.sql.functions import struct

df = df.withColumn("name_age", struct(col("name"), col("age")))

# Select specific struct fields
df = df.select("name", "address.*")  # Flatten address struct
```

### NullType
**Definition:** Represents null values. Rarely used explicitly but important for handling nulls.

```python
# Working with nulls
from pyspark.sql.functions import lit, isnull, when

# Create column with null values
df = df.withColumn("nullable_column", lit(None).cast(StringType()))

# Check for nulls
df = df.withColumn("is_null", isnull(col("nullable_column")))

# Replace nulls
df = df.withColumn("with_default", when(col("nullable_column").isNull(), "DEFAULT").otherwise(col("nullable_column")))

# Drop rows with nulls
df_no_nulls = df.na.drop()

# Fill nulls
df_filled = df.na.fill("UNKNOWN", ["nullable_column"])
```

## DataType (Base Class)
**Definition:** The base class for all data types in PySpark. Not typically used directly but useful for type checking.

```python
# Type checking example
def is_numeric_type(data_type):
    return isinstance(data_type, (ByteType, ShortType, IntegerType, LongType, FloatType, DoubleType, DecimalType))

# Check schema for numeric fields
numeric_fields = [field.name for field in df.schema.fields if is_numeric_type(field.dataType)]
```

## Type Conversions

```python
# Cast between types
df = df.withColumn("string_to_int", col("string_column").cast(IntegerType()))
df = df.withColumn("int_to_double", col("int_column").cast(DoubleType()))
df = df.withColumn("timestamp_to_date", col("timestamp_column").cast(DateType()))

# Complex type conversions
from pyspark.sql.functions import from_json, to_json, schema_of_json

# JSON string to struct
json_schema = schema_of_json(lit('{"name":"John", "age":30}'))
df = df.withColumn("parsed_json", from_json(col("json_string"), json_schema))

# Struct to JSON string
df = df.withColumn("json_output", to_json(col("struct_column")))
```
