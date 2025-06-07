# PySpark Catalog & Schema Management Cheat Sheet
I've created a comprehensive PySpark cheat sheet that covers all the areas you requested:

### Key sections include:
[Catalog/Schema Context Management](#catalogschema-context-management) - Commands to switch between databases, list schemas, and manage context
[Table Definition Creation](#table-definition-creation) - Both PySpark DataFrame API and Spark SQL approaches for creating tables with various options
[View Definition Creation](#view-definition-creation) - Creating temporary, global, and permanent views
[Column and Data Type Inspection](#column-and-data-type-inspection) - Multiple approaches to iterate over columns, inspect schemas, and analyze data types
[Table Metadata and Properties](#table-metadata-and-properties) - Getting detailed table information, properties, and statistics
[Utility Functions](#utility-functions) - Helper functions for common metadata operations
[Quick Reference Commands](#quick-reference-commands) - Essential one-liner commands

Each section provides both PySpark Python code and Spark SQL examples as requested. The cheat sheet includes practical examples for:

- Managing database context and navigation
- Creating tables with different storage formats and partitioning
- Building views with complex SQL logic
- Programmatically inspecting table schemas and column properties
- Advanced metadata analysis and table comparisons

This should give you a solid reference for managing catalogs, schemas, and table definitions in PySpark environments!

## Catalog/Schema Context Management

### Change Database/Schema Context

**PySpark:**
```python
# Set current database
spark.catalog.setCurrentDatabase("my_database")

# Get current database
current_db = spark.catalog.currentDatabase()

# Use database in SQL context
spark.sql("USE my_database")
```

**Spark SQL:**
```sql
USE my_database;
USE CATALOG my_catalog;
USE SCHEMA my_schema;
```

### List and Browse Catalogs/Schemas

**PySpark:**
```python
# List all databases/schemas
databases = spark.catalog.listDatabases()
databases.show()

# Get database names as list
db_names = [db.name for db in spark.catalog.listDatabases().collect()]

# Check if database exists
db_exists = spark.catalog.databaseExists("my_database")

# List tables in current database
tables = spark.catalog.listTables()

# List tables in specific database
tables_in_db = spark.catalog.listTables("my_database")
```

**Spark SQL:**
```sql
SHOW DATABASES;
SHOW SCHEMAS;
SHOW TABLES;
SHOW TABLES IN my_database;
```

## Table Definition Creation

### Create Tables

**PySpark:**
```python
# Create table from DataFrame
df.write.mode("overwrite").saveAsTable("my_database.my_table")

# Create empty table with schema
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType

schema = StructType([
    StructField("id", IntegerType(), True),
    StructField("name", StringType(), True),
    StructField("value", DoubleType(), True),
    StructField("category", StringType(), True)
])

empty_df = spark.createDataFrame([], schema)
empty_df.write.mode("overwrite").saveAsTable("my_database.my_table")

# Create partitioned table
df.write \
  .mode("overwrite") \
  .partitionBy("category") \
  .saveAsTable("my_database.partitioned_table")

# Create table with specific options
df.write \
  .mode("overwrite") \
  .option("path", "/path/to/table") \
  .saveAsTable("my_database.external_table")
```

**Spark SQL:**
```sql
-- Create table with explicit schema
CREATE TABLE my_database.my_table (
    id INT,
    name STRING,
    value DOUBLE,
    category STRING
) USING DELTA
PARTITIONED BY (category);

-- Create table from query
CREATE TABLE my_database.my_table AS
SELECT * FROM source_table WHERE condition = true;

-- Create external table
CREATE TABLE my_database.external_table (
    id INT,
    name STRING
) USING PARQUET
LOCATION '/path/to/data';

-- Create temporary table
CREATE TEMPORARY VIEW temp_table AS
SELECT * FROM my_database.my_table;
```

### Drop Tables

**PySpark:**
```python
# Drop table
spark.sql("DROP TABLE IF EXISTS my_database.my_table")

# Check if table exists first
if spark.catalog.tableExists("my_database.my_table"):
    spark.sql("DROP TABLE my_database.my_table")
```

**Spark SQL:**
```sql
DROP TABLE IF EXISTS my_database.my_table;
DROP VIEW IF EXISTS my_view;
```

## View Definition Creation

### Create Views

**PySpark:**
```python
# Create temporary view from DataFrame
df.createOrReplaceTempView("my_temp_view")

# Create global temporary view
df.createGlobalTempView("my_global_view")

# Create view using SQL
spark.sql("""
    CREATE OR REPLACE VIEW my_database.my_view AS
    SELECT id, name, value * 2 as doubled_value
    FROM my_database.my_table
    WHERE value > 0
""")

# Create view from DataFrame with SQL logic
filtered_df = df.filter(df.value > 0).select("id", "name", (df.value * 2).alias("doubled_value"))
filtered_df.createOrReplaceTempView("calculated_view")
```

**Spark SQL:**
```sql
-- Create permanent view
CREATE OR REPLACE VIEW my_database.my_view AS
SELECT 
    id,
    name,
    value * 2 as doubled_value,
    CASE 
        WHEN value > 100 THEN 'high'
        WHEN value > 50 THEN 'medium'
        ELSE 'low'
    END as value_category
FROM my_database.my_table
WHERE value IS NOT NULL;

-- Create temporary view
CREATE OR REPLACE TEMPORARY VIEW temp_aggregated AS
SELECT 
    category,
    COUNT(*) as count,
    AVG(value) as avg_value,
    MAX(value) as max_value
FROM my_database.my_table
GROUP BY category;
```

## Column and Data Type Inspection

### Iterate Over Table Columns

**PySpark:**
```python
# Get table as DataFrame
df = spark.table("my_database.my_table")

# Get column names
column_names = df.columns
print("Columns:", column_names)

# Get schema/data types
schema = df.schema
print("Schema:", schema)

# Iterate over columns with data types
for field in df.schema.fields:
    print(f"Column: {field.name}, Type: {field.dataType}, Nullable: {field.nullable}")

# Get detailed column information using catalog
columns_info = spark.catalog.listColumns("my_database.my_table")
columns_info.show(truncate=False)

# Convert to list for iteration
columns_list = columns_info.collect()
for col in columns_list:
    print(f"Column: {col.name}, Type: {col.dataType}, Nullable: {col.nullable}")

# Get column statistics
column_stats = df.describe().collect()
for stat in column_stats:
    print(stat)
```

**Spark SQL:**
```sql
-- Describe table structure
DESCRIBE my_database.my_table;

-- Get detailed table information
DESCRIBE EXTENDED my_database.my_table;

-- Show column details
SHOW COLUMNS IN my_database.my_table;

-- Get column statistics
DESCRIBE EXTENDED my_database.my_table column_name;
```

### Advanced Column Analysis

**PySpark:**
```python
# Get data types as dictionary
dtype_dict = dict(df.dtypes)
print("Data types:", dtype_dict)

# Filter columns by data type
string_columns = [field.name for field in df.schema.fields if str(field.dataType) == 'StringType()']
numeric_columns = [field.name for field in df.schema.fields if 'Type()' in str(field.dataType) and str(field.dataType) in ['IntegerType()', 'DoubleType()', 'FloatType()', 'LongType()']]

print("String columns:", string_columns)
print("Numeric columns:", numeric_columns)

# Check for null values in each column
from pyspark.sql.functions import col, sum as spark_sum, isnan, when, count

null_counts = df.select([
    spark_sum(when(col(c).isNull() | isnan(col(c)), 1).otherwise(0)).alias(c)
    for c in df.columns
]).collect()[0].asDict()

print("Null counts per column:", null_counts)

# Get column cardinality (distinct values)
distinct_counts = {}
for column in df.columns:
    distinct_count = df.select(column).distinct().count()
    distinct_counts[column] = distinct_count
    
print("Distinct counts:", distinct_counts)
```

## Table Metadata and Properties

### Inspect Table Details

**PySpark:**
```python
# Get table metadata
table_info = spark.sql("DESCRIBE EXTENDED my_database.my_table").collect()
for row in table_info:
    print(f"{row.col_name}: {row.data_type}")

# Get table properties
table_props = spark.sql("SHOW TBLPROPERTIES my_database.my_table").collect()
for prop in table_props:
    print(f"{prop.key}: {prop.value}")

# Check table format
table_details = spark.sql("SHOW CREATE TABLE my_database.my_table").collect()
print("Table DDL:", table_details[0].createtab_stmt)

# Get partition information
if spark.sql("SHOW PARTITIONS my_database.my_table").count() > 0:
    partitions = spark.sql("SHOW PARTITIONS my_database.my_table").collect()
    print("Partitions:", [p.partition for p in partitions])
```

**Spark SQL:**
```sql
-- Get comprehensive table information
SHOW CREATE TABLE my_database.my_table;

-- Show table properties
SHOW TBLPROPERTIES my_database.my_table;

-- Show partitions
SHOW PARTITIONS my_database.my_table;

-- Get table statistics
ANALYZE TABLE my_database.my_table COMPUTE STATISTICS;
ANALYZE TABLE my_database.my_table COMPUTE STATISTICS FOR COLUMNS id, name, value;
```

## Utility Functions

### Helper Functions for Metadata Operations

**PySpark:**
```python
def get_table_info(database, table):
    """Get comprehensive table information"""
    if not spark.catalog.tableExists(f"{database}.{table}"):
        return f"Table {database}.{table} does not exist"
    
    df = spark.table(f"{database}.{table}")
    
    info = {
        'row_count': df.count(),
        'column_count': len(df.columns),
        'columns': df.columns,
        'schema': [(field.name, str(field.dataType), field.nullable) for field in df.schema.fields],
        'data_types': dict(df.dtypes)
    }
    
    return info

def list_all_tables_with_info():
    """List all tables across all databases with basic info"""
    result = []
    for db in spark.catalog.listDatabases().collect():
        db_name = db.name
        for table in spark.catalog.listTables(db_name).collect():
            table_info = {
                'database': db_name,
                'table': table.name,
                'type': table.tableType,
                'is_temporary': table.isTemporary
            }
            result.append(table_info)
    return result

def compare_schemas(table1, table2):
    """Compare schemas of two tables"""
    df1 = spark.table(table1)
    df2 = spark.table(table2)
    
    schema1_dict = {field.name: str(field.dataType) for field in df1.schema.fields}
    schema2_dict = {field.name: str(field.dataType) for field in df2.schema.fields}
    
    common_cols = set(schema1_dict.keys()) & set(schema2_dict.keys())
    only_in_table1 = set(schema1_dict.keys()) - set(schema2_dict.keys())
    only_in_table2 = set(schema2_dict.keys()) - set(schema1_dict.keys())
    
    type_differences = {
        col: (schema1_dict[col], schema2_dict[col]) 
        for col in common_cols 
        if schema1_dict[col] != schema2_dict[col]
    }
    
    return {
        'common_columns': list(common_cols),
        'only_in_table1': list(only_in_table1),
        'only_in_table2': list(only_in_table2),
        'type_differences': type_differences
    }

# Usage examples
table_info = get_table_info("my_database", "my_table")
all_tables = list_all_tables_with_info()
schema_comparison = compare_schemas("db1.table1", "db2.table2")
```

## Quick Reference Commands

```python
# Essential one-liners
spark.catalog.listDatabases().show()                    # List all databases
spark.catalog.listTables("db_name").show()              # List tables in database  
spark.catalog.listColumns("table_name").show()          # List columns in table
spark.catalog.setCurrentDatabase("my_db")               # Switch database context
spark.table("my_table").printSchema()                   # Print table schema
spark.table("my_table").dtypes                          # Get column data types
spark.sql("DESCRIBE EXTENDED my_table").show()          # Detailed table info
df.createOrReplaceTempView("temp_view")                  # Create temporary view
spark.catalog.tableExists("my_table")                   # Check if table exists
spark.catalog.refreshTable("my_table")                  # Refresh table metadata
```
