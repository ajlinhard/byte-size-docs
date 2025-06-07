# Catalogs Create and Manage
Here are the ways to create catalogs and databases (schemas) in Spark:

## Creating Catalogs

Catalogs are typically configured at the SparkSession level and depend on the catalog implementation you're using:

### Delta Lake Catalog
```python
# Configure catalog in SparkSession
spark = SparkSession.builder \
    .appName("Catalog Creation") \
    .config("spark.sql.catalog.my_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
    .config("spark.sql.catalog.my_catalog.warehouse", "/path/to/warehouse") \
    .getOrCreate()

# The catalog is now available for use
spark.sql("SHOW CATALOGS").show()
```

### Hive Catalog
```python
# Configure Hive catalog
spark = SparkSession.builder \
    .appName("Hive Catalog") \
    .config("spark.sql.catalog.hive_catalog", "org.apache.spark.sql.hive.catalog.HiveCatalog") \
    .config("spark.sql.catalog.hive_catalog.warehouse", "/path/to/hive/warehouse") \
    .enableHiveSupport() \
    .getOrCreate()
```

### JDBC Catalog (for databases like PostgreSQL)
```python
spark = SparkSession.builder \
    .appName("JDBC Catalog") \
    .config("spark.sql.catalog.postgres_catalog", "org.apache.spark.sql.connector.catalog.jdbc.JDBCTableCatalog") \
    .config("spark.sql.catalog.postgres_catalog.url", "jdbc:postgresql://localhost:5432/mydb") \
    .config("spark.sql.catalog.postgres_catalog.driver", "org.postgresql.Driver") \
    .config("spark.sql.catalog.postgres_catalog.user", "username") \
    .config("spark.sql.catalog.postgres_catalog.password", "password") \
    .getOrCreate()
```

## Creating Databases/Schemas

Once you have a catalog, you can create databases (schemas) within it:

### Using SQL
```python
# Create database in default catalog
spark.sql("CREATE DATABASE IF NOT EXISTS my_database")

# Create database in specific catalog
spark.sql("CREATE SCHEMA IF NOT EXISTS my_catalog.my_database")

# Create database with additional properties
spark.sql("""
CREATE DATABASE IF NOT EXISTS my_catalog.my_database
COMMENT 'My database description'
LOCATION '/path/to/database/location'
WITH DBPROPERTIES (
    'owner' = 'data_team',
    'created_date' = '2024-01-01'
)
""")
```

### Using Catalog API
```python
# Switch to specific catalog first
spark.sql("USE CATALOG my_catalog")

# Create database
spark.sql("CREATE DATABASE my_new_database LOCATION '/path/to/db'")

# Or create with full qualification
spark.sql("CREATE DATABASE my_catalog.my_new_database")
```

## Complete Example

Here's a complete example creating a catalog and database:

```python
from pyspark.sql import SparkSession

# Create SparkSession with catalog configuration
spark = SparkSession.builder \
    .appName("Catalog and Database Creation") \
    .config("spark.sql.catalog.my_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
    .config("spark.sql.catalog.my_catalog.warehouse", "/tmp/my_catalog_warehouse") \
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
    .getOrCreate()

# Verify catalog exists
print("Available catalogs:")
spark.sql("SHOW CATALOGS").show()

# Create database in the new catalog
spark.sql("""
CREATE DATABASE IF NOT EXISTS my_catalog.analytics
COMMENT 'Analytics database for reporting'
LOCATION '/tmp/my_catalog_warehouse/analytics'
""")

# Verify database was created
print("Databases in my_catalog:")
spark.sql("SHOW DATABASES IN my_catalog").show()

# Switch context to the new catalog and database
spark.sql("USE CATALOG my_catalog")
spark.sql("USE DATABASE analytics")

# Create a table to test
spark.sql("""
CREATE TABLE test_table (
    id INT,
    name STRING,
    created_date DATE
) USING DELTA
""")

# Verify table creation
spark.sql("SHOW TABLES").show()
```

## Verification Commands

```python
# List all catalogs
spark.sql("SHOW CATALOGS").show()

# List databases in specific catalog
spark.sql("SHOW DATABASES IN my_catalog").show()

# Get current catalog and database
current_catalog = spark.sql("SELECT current_catalog()").collect()[0][0]
current_database = spark.sql("SELECT current_database()").collect()[0][0]
print(f"Current catalog: {current_catalog}")
print(f"Current database: {current_database}")

# Describe database
spark.sql("DESCRIBE DATABASE EXTENDED my_catalog.my_database").show()
```

## Important Notes

1. **Catalog Types**: The catalog implementation depends on your storage format (Delta, Hive, JDBC, etc.)
2. **Permissions**: You need appropriate permissions to create catalogs and databases
3. **Storage Location**: Specify appropriate storage locations for your databases
4. **Dependencies**: Make sure you have the required JAR files for your chosen catalog implementation

The exact steps may vary depending on your Spark environment and the catalog implementations available in your setup.

---
# Create a New Catalog
To add a second catalog called `new_catalog`, you would add additional configuration lines to the SparkSession builder. Here's how:

```python
# Configure both Hive catalog and new_catalog
spark = SparkSession.builder \
    .appName("Multiple Catalogs") \
    .config("spark.sql.catalog.hive_catalog", "org.apache.spark.sql.hive.catalog.HiveCatalog") \
    .config("spark.sql.catalog.hive_catalog.warehouse", "/path/to/hive/warehouse") \
    .config("spark.sql.catalog.new_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
    .config("spark.sql.catalog.new_catalog.warehouse", "/path/to/new/warehouse") \
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
    .enableHiveSupport() \
    .getOrCreate()
```

## What Line Adds the Catalog:

```python
.config("spark.sql.catalog.new_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
```
- Registers a catalog named `new_catalog` using Delta Lake implementation

```python
.config("spark.sql.catalog.new_catalog.warehouse", "/path/to/new/warehouse")
```
- Sets the warehouse location for the new catalog

```python
.config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
```
- Enables Delta Lake extensions (needed if using Delta catalog)

## Alternative Catalog Types

You could also create `new_catalog` using other implementations:

### Another Hive Catalog (pointing to different metastore):
```python
.config("spark.sql.catalog.new_catalog", "org.apache.spark.sql.hive.catalog.HiveCatalog") \
.config("spark.sql.catalog.new_catalog.warehouse", "/path/to/different/warehouse") \
.config("spark.sql.catalog.new_catalog.hive.metastore.uris", "thrift://different-metastore:9083") \
```

### JDBC Catalog:
```python
.config("spark.sql.catalog.new_catalog", "org.apache.spark.sql.connector.catalog.jdbc.JDBCTableCatalog") \
.config("spark.sql.catalog.new_catalog.url", "jdbc:postgresql://localhost:5432/mydb") \
.config("spark.sql.catalog.new_catalog.driver", "org.postgresql.Driver") \
.config("spark.sql.catalog.new_catalog.user", "username") \
.config("spark.sql.catalog.new_catalog.password", "password") \
```

## Verify Both Catalogs:

```python
# Check that both catalogs are available
spark.sql("SHOW CATALOGS").show()

# Use the new catalog
spark.sql("CREATE DATABASE new_catalog.test_db")
spark.sql("SHOW DATABASES IN new_catalog").show()

# Use the hive catalog
spark.sql("SHOW DATABASES IN hive_catalog").show()
```

The key pattern is: for each catalog you want to register, add the configuration lines with the catalog name as part of the config key (`spark.sql.catalog.CATALOG_NAME.*`).
