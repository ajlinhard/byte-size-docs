# Spark CSV File I/O Overview
The csv is a classic raw file data type, also sometime referred to as delimited fiile. These files can be quick and easy to process or some of the dirtiest hard to parse files you can find. Either way they ability to load them is a requirement in any data processing engine.

## Common Issues:
- TLDR; Not following standard CSV/delimited file conventions ([click here](https://en.wikipedia.org/wiki/Comma-separated_values#RFC_4180_and_MIME_standards)).
- No qualifying quotes when delimiter is present within data columns.
- Variable number of columns per record.
- newline characters within the data.

## Documentation:
- [Spark Official CSV Options](https://spark.apache.org/docs/latest/sql-data-sources-csv.html)
- Spark Offical API .csv
  - [Reader](https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.DataFrameReader.csv.html)
  - [Writer](https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.DataFrameWriter.csv.html)
- [Example Loading Code/Notebook](https://github.com/ajlinhard/PythonExplorer/blob/main/Spark/DF_Load_CSV_TXT.ipynb)


# Understanding Spark CSV Functions: DataFrameReader/Writer vs. Column-Level Functions
In Spark, there are two different approaches for working with CSV data, and they're designed for different use cases. Let me explain the difference between the DataFrame-level methods (`read.option().csv()` and `write.option().csv()`) and the column-level functions (`from_csv`, `to_csv`, and `schema_of_csv`).

## DataFrame-Level CSV Operations 

The `read.option().csv()` and `write.option().csv()` methods operate at the **DataFrame level** - they're used to read entire CSV files into DataFrames or write entire DataFrames to CSV files.

```python
from pyspark.sql import SparkSession

# Create SparkSession with Hive support (as mentioned in your cheat sheet)
spark = SparkSession.builder \
    .appName("DataFrame CSV Example") \
    .enableHiveSupport() \
    .getOrCreate()

# Reading a CSV file into a DataFrame
df = spark.read \
    .option("header", "true") \
    .option("delimiter", ",") \
    .option("inferSchema", "true") \
    .csv("/path/to/file.csv")

# Writing a DataFrame to a CSV file
df.write \
    .option("header", "true") \
    .option("delimiter", ",") \
    .mode("overwrite") \
    .csv("/path/to/output/")
```

## Column-Level CSV Operations

The functions `from_csv`, `to_csv`, and `schema_of_csv` operate at the **column level** - they're used to parse or generate CSV strings within individual columns of a DataFrame.

```python
from pyspark.sql.functions import from_csv, to_csv, schema_of_csv, col, struct
from pyspark.sql.types import StructType, StructField, StringType, IntegerType

# Define a schema for our CSV string
schema = StructType([
    StructField("id", IntegerType()),
    StructField("name", StringType()),
    StructField("age", IntegerType())
])

# Example DataFrame with a column containing CSV strings
data = [("1,John,30",), ("2,Alice,25",), ("3,Bob,35",)]
df = spark.createDataFrame(data, ["csv_column"])

# Parse the CSV strings into structured columns using from_csv
parsed_df = df.withColumn(
    "parsed_data", 
    from_csv(col("csv_column"), schema)
)

# Now we can extract the individual fields
parsed_df = parsed_df.withColumn("id", col("parsed_data.id")) \
    .withColumn("name", col("parsed_data.name")) \
    .withColumn("age", col("parsed_data.age"))

# Convert structured columns back to CSV strings using to_csv
result_df = parsed_df.withColumn(
    "new_csv_column", 
    to_csv(struct(col("id"), col("name"), col("age")))
)

# Infer a schema from CSV data using schema_of_csv
inferred_schema = spark.sql("SELECT schema_of_csv('1,John,30')").collect()[0][0]
print(inferred_schema)
```

## Key Differences and Why Both Exist

1. **Scope of Operation**:
   - DataFrame-level: Reads/writes entire files
   - Column-level: Works on individual columns within a DataFrame

2. **Use Cases**:
   - DataFrame-level: Used when you need to load or save entire datasets
   - Column-level: Used when you have CSV strings embedded within columns of a DataFrame

3. **Common Applications for Column-level Functions**:
   - Processing data that contains CSV strings in database fields
   - Handling nested CSV data in JSON or complex data structures
   - Performing ETL operations where only certain columns need CSV parsing

## Real-World Example

Imagine you have a table in Hive that stores event logs, and one column contains comma-separated values with additional details:

```python
# Create a sample DataFrame with a column containing CSV strings
log_data = [
    (1, "2023-01-01", "user_login", "userid=123,browser=chrome,device=mobile"),
    (2, "2023-01-01", "page_view", "pageid=home,duration=45,scroll=75"),
    (3, "2023-01-02", "purchase", "product=shirt,quantity=2,price=29.99")
]

logs_df = spark.createDataFrame(log_data, ["id", "date", "event_type", "event_details"])

# Define schema for the CSV data in event_details
details_schema = schema_of_csv("userid=123,browser=chrome,device=mobile", 
                             options={"delimiter": ",", "header": "false"})

# Parse the CSV strings in the event_details column
parsed_logs = logs_df.withColumn(
    "parsed_details", 
    from_csv(col("event_details"), details_schema, {"delimiter": ","})
)

# Now you can query specific fields from the previously CSV-encoded data
parsed_logs.createOrReplaceTempView("parsed_logs")
mobile_users = spark.sql("""
    SELECT id, date, event_type, parsed_details.userid 
    FROM parsed_logs 
    WHERE parsed_details.device = 'mobile'
""")
```

### Summary
Both approaches serve important but different purposes:

- Use `read.csv()` and `write.csv()` when working with entire CSV files
- Use `from_csv()`, `to_csv()`, and `schema_of_csv()` when working with CSV data contained within DataFrame columns

This flexibility lets you handle both traditional CSV file processing and more complex scenarios where CSV data is embedded within other structures - giving you the best of both worlds depending on your specific data processing needs.
