# Spark Schema Evolution
When appending to a table in PySpark and the schema has changes, you have several strategies to handle this. Here's a comprehensive guide:

## 1. Schema Evolution with `mergeSchema` Option

The most straightforward approach for file-based tables (Parquet, Delta):

```python
# Enable schema merging when writing
df.write \
    .mode("append") \
    .option("mergeSchema", "true") \
    .saveAsTable("my_table")

# Or for file paths
df.write \
    .mode("append") \
    .option("mergeSchema", "true") \
    .parquet("/path/to/table")
```

## 2. Manual Schema Alignment

Align schemas before appending:

```python
from pyspark.sql.functions import lit, col
from pyspark.sql.types import *

# Get existing table schema
existing_schema = spark.table("my_table").schema
existing_columns = set([field.name for field in existing_schema.fields])

# Get new DataFrame schema
new_columns = set(df.columns)

# Add missing columns to new DataFrame with null values
missing_in_new = existing_columns - new_columns
for col_name in missing_in_new:
    # Get the data type from existing schema
    col_type = next(field.dataType for field in existing_schema.fields if field.name == col_name)
    df = df.withColumn(col_name, lit(None).cast(col_type))

# Reorder columns to match existing table
df = df.select([col(c) for c in [field.name for field in existing_schema.fields]])

# Now append
df.write.mode("append").saveAsTable("my_table")
```

## 3. Handle New Columns in Existing Table

If new DataFrame has additional columns:

```python
def align_schemas(df, table_name):
    # Get existing table schema
    existing_df = spark.table(table_name)
    existing_schema = existing_df.schema
    existing_columns = [field.name for field in existing_schema.fields]
    
    # Get new columns that don't exist in target table
    new_columns = set(df.columns) - set(existing_columns)
    
    if new_columns:
        # Option 1: Add new columns to existing table first
        for col_name in new_columns:
            col_type = dict(df.dtypes)[col_name]
            spark.sql(f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_type}")
        
        # Refresh table metadata
        spark.catalog.refreshTable(table_name)
    
    # Option 2: Or drop new columns from DataFrame
    # df = df.select(existing_columns)
    
    return df

# Use the function
df_aligned = align_schemas(df, "my_table")
df_aligned.write.mode("append").saveAsTable("my_table")
```

## 4. Type-Safe Schema Evolution

Handle data type changes safely:

```python
def safe_schema_evolution(df, table_name):
    existing_df = spark.table(table_name)
    existing_schema = {field.name: field.dataType for field in existing_df.schema.fields}
    
    for col_name in df.columns:
        if col_name in existing_schema:
            existing_type = existing_schema[col_name]
            new_type = dict(df.dtypes)[col_name]
            
            # Handle type conversions
            if str(existing_type) != new_type:
                print(f"Type mismatch for {col_name}: {new_type} -> {existing_type}")
                # Cast to existing type
                df = df.withColumn(col_name, col(col_name).cast(existing_type))
    
    return df
```

## 5. Using Delta Lake (Recommended)

If you're using Delta Lake, schema evolution is much easier:

```python
# Delta Lake automatically handles schema evolution
df.write \
    .format("delta") \
    .mode("append") \
    .option("mergeSchema", "true") \
    .saveAsTable("my_delta_table")

# Or explicitly allow schema evolution
spark.conf.set("spark.databricks.delta.schema.autoMerge.enabled", "true")
```

## 6. Pre-flight Schema Check

Always validate before appending:

```python
def validate_schema_compatibility(df, table_name):
    try:
        existing_df = spark.table(table_name)
        existing_schema = existing_df.schema
        new_schema = df.schema
        
        # Check for incompatible changes
        for field in new_schema.fields:
            if field.name in [f.name for f in existing_schema.fields]:
                existing_field = next(f for f in existing_schema.fields if f.name == field.name)
                if field.dataType != existing_field.dataType:
                    print(f"Warning: Type change for {field.name}: {existing_field.dataType} -> {field.dataType}")
        
        return True
    except Exception as e:
        print(f"Schema validation failed: {e}")
        return False

# Use before appending
if validate_schema_compatibility(df, "my_table"):
    # Proceed with append
    pass
```

## 7. Complete Example with Error Handling

```python
def safe_append_with_schema_evolution(df, table_name):
    try:
        # Check if table exists
        if spark.catalog.tableExists(table_name):
            # Get existing schema
            existing_df = spark.table(table_name)
            existing_schema = existing_df.schema
            existing_cols = [field.name for field in existing_schema.fields]
            
            # Align schemas
            df_aligned = df
            
            # Add missing columns with appropriate defaults
            missing_cols = set(existing_cols) - set(df.columns)
            for col_name in missing_cols:
                field_type = next(f.dataType for f in existing_schema.fields if f.name == col_name)
                df_aligned = df_aligned.withColumn(col_name, lit(None).cast(field_type))
            
            # Reorder columns to match existing table
            df_aligned = df_aligned.select(existing_cols)
            
            # Append
            df_aligned.write.mode("append").saveAsTable(table_name)
        else:
            # Create new table
            df.write.mode("overwrite").saveAsTable(table_name)
            
        print(f"Successfully appended to {table_name}")
        
    except Exception as e:
        print(f"Error appending to table: {e}")
        raise

# Usage
safe_append_with_schema_evolution(df, "my_table")
```

## Best Practices:

1. **Use Delta Lake** when possible for automatic schema evolution
2. **Always validate schemas** before appending in production
3. **Handle type conversions explicitly** rather than relying on implicit casting
4. **Document schema changes** and have a rollback plan
5. **Test schema evolution** in development environments first
6. **Monitor for performance impacts** as schema evolution can affect query performance

Choose the approach that best fits your use case and data format requirements.
