# Spark SQL Temp Data
Great question! In Spark SQL, there are several options for creating temporary data structures, each with different scopes and behaviors:

## Temporary Views vs Other Options

### 1. **Temporary Views** (Session-scoped)
```sql
-- These are session-scoped and disappear when session ends
CREATE OR REPLACE TEMPORARY VIEW my_temp_view
USING CSV
OPTIONS (path "file.csv", header "true");

-- Can be accessed anywhere in the session
SELECT * FROM my_temp_view;
```

### 2. **Global Temporary Views** (Application-scoped)
```sql
-- These persist across multiple SparkSessions within the same application
CREATE OR REPLACE GLOBAL TEMPORARY VIEW my_global_view
USING PARQUET
OPTIONS (path "file.parquet");

-- Must be accessed with global_temp prefix
SELECT * FROM global_temp.my_global_view;
```

### 3. **Common Table Expressions (CTEs)** (Query-scoped)
```sql
-- These only exist within a single query
WITH temp_data AS (
  SELECT * FROM csv_data WHERE value > 100
),
aggregated AS (
  SELECT category, SUM(value) as total
  FROM temp_data
  GROUP BY category
)
SELECT * FROM aggregated;
```

### 4. **Cached Tables** (Performance-focused temporary storage)
```sql
-- Create a view and cache it in memory
CREATE OR REPLACE TEMPORARY VIEW cached_data
USING PARQUET OPTIONS (path "large_file.parquet");

-- Cache the view for better performance
CACHE TABLE cached_data;

-- Use the cached data
SELECT * FROM cached_data;

-- Remove from cache when done
UNCACHE TABLE cached_data;
```

### 5. **Temporary Tables** (Delta/Hive-style, if supported)
```sql
-- Some environments support CREATE TEMPORARY TABLE
-- (availability depends on catalog implementation)
CREATE TEMPORARY TABLE temp_table (
  id INT,
  name STRING,
  value DOUBLE
) USING DELTA;

-- Insert data
INSERT INTO temp_table VALUES (1, 'test', 10.5);
```

## Key Differences:

| Type | Scope | Persistence | Access Pattern |
|------|-------|-------------|----------------|
| Temporary View | Session | Until session ends | Direct name |
| Global Temporary View | Application | Until application ends | `global_temp.name` |
| CTE | Single Query | Query execution only | Within WITH clause |
| Cached Table | Session | Until uncached/session ends | Direct name + memory storage |
| Temporary Table | Session | Until session ends | Direct name (if supported) |

## Best Practices:

**Use Temporary Views when:**
- You need to reference data multiple times in a session
- Working with file-based data sources
- Need session-level persistence

**Use CTEs when:**
- Breaking down complex queries
- Need temporary results within a single query
- Want to improve query readability

**Use Global Temporary Views when:**
- Sharing data across multiple SparkSessions
- Working in environments with multiple concurrent sessions

**Use Cached Tables when:**
- Working with large datasets accessed multiple times
- Need to optimize performance for repeated access

So **temporary views are indeed the primary "temporary tables" of Spark SQL**, but you have these other options depending on your specific needs for scope, persistence, and performance.

---
# Using Pyspark
Great question! Here's how to work with temporary data structures in PySpark, showing the different options and their scopes:Here's the comprehensive PySpark version covering all temporary data structure options:

## Key Differences in PySpark:

| Type | PySpark Method | Scope | Access Pattern |
|------|----------------|-------|----------------|
| **Temporary View** | `df.createOrReplaceTempView("name")` | Session | `spark.sql()` or `spark.table()` |
| **Global Temporary View** | `df.createGlobalTempView("name")` | Application | `spark.table("global_temp.name")` |
| **CTE** | SQL within `spark.sql()` or DataFrame chaining | Single Query | Within query only |
| **Cached DataFrame** | `df.cache()` or `df.persist()` | Session | Direct DataFrame reference |
| **Temporary Table** | `spark.sql("CREATE TEMPORARY TABLE...")` | Session | `spark.sql()` or `spark.table()` |

## Key PySpark-Specific Features:

1. **DataFrame Methods**: Use `.createOrReplaceTempView()` and `.createGlobalTempView()` directly on DataFrames
2. **Catalog Operations**: Rich catalog API with `.listTables()`, `.tableExists()`, `.dropTempView()`
3. **Caching Control**: Fine-grained control with `StorageLevel` options
4. **Error Handling**: Python try/catch blocks for robust temporary view management
5. **Lifecycle Management**: Custom classes to manage temporary view cleanup

The main advantage of PySpark is the programmatic control - you can build sophisticated temporary view management systems, error handling, and cleanup routines that integrate well with your Python data pipeline code.

**So yes, temporary views are the primary "temporary tables" in PySpark**, but you have these additional options for different scopes and use cases, plus much more programmatic control over their lifecycle.

## Code Examples
```python
# PySpark Temporary Data Structures Guide

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum as spark_sum

# Initialize SparkSession
spark = SparkSession.builder \
    .appName("Temporary Structures Example") \
    .getOrCreate()

# Sample data for examples
data = [(1, "Alice", 100.0), (2, "Bob", 200.0), (3, "Charlie", 150.0)]
columns = ["id", "name", "value"]
df = spark.createDataFrame(data, columns)

## 1. TEMPORARY VIEWS (Session-scoped)
# These are session-scoped and disappear when session ends

# Create temporary view from DataFrame
df.createOrReplaceTempView("my_temp_view")

# Create temporary view from file
csv_df = spark.read.csv("file.csv", header=True, inferSchema=True)
csv_df.createOrReplaceTempView("csv_temp_view")

# Create temporary view from Parquet
parquet_df = spark.read.parquet("file.parquet")
parquet_df.createOrReplaceTempView("parquet_temp_view")

# Access temporary view with SQL
result = spark.sql("SELECT * FROM my_temp_view WHERE value > 100")
result.show()

# Access temporary view with DataFrame API
temp_view_df = spark.table("my_temp_view")
filtered_df = temp_view_df.filter(col("value") > 100)
filtered_df.show()

# Check if view exists
if spark.catalog.tableExists("my_temp_view"):
    print("Temporary view exists")

# Drop temporary view
spark.catalog.dropTempView("my_temp_view")


## 2. GLOBAL TEMPORARY VIEWS (Application-scoped)
# These persist across multiple SparkSessions within the same application

# Create global temporary view
df.createGlobalTempView("my_global_view")

# Access global temporary view (must use global_temp prefix)
global_result = spark.sql("SELECT * FROM global_temp.my_global_view")
global_result.show()

# Access from DataFrame API
global_df = spark.table("global_temp.my_global_view")
global_df.show()

# Create another SparkSession in same application
spark2 = SparkSession.builder \
    .appName("Second Session") \
    .getOrCreate()

# Global view is accessible from new session
spark2.sql("SELECT COUNT(*) FROM global_temp.my_global_view").show()

# Drop global temporary view
spark.catalog.dropGlobalTempView("my_global_view")


## 3. COMMON TABLE EXPRESSIONS (CTEs) - Query-scoped
# These only exist within a single query

# CTE with SQL
cte_result = spark.sql("""
    WITH temp_data AS (
        SELECT * FROM my_temp_view WHERE value > 100
    ),
    aggregated AS (
        SELECT name, value * 2 as double_value
        FROM temp_data
    )
    SELECT * FROM aggregated
""")
cte_result.show()

# DataFrame equivalent (chaining operations)
temp_data = df.filter(col("value") > 100)
aggregated = temp_data.select(col("name"), (col("value") * 2).alias("double_value"))
aggregated.show()


## 4. CACHED DATAFRAMES/TABLES (Performance-focused temporary storage)
# Cache in memory for better performance on repeated access

# Cache DataFrame
df.cache()
# Alternative: df.persist()

# Create temporary view and cache it
df.createOrReplaceTempView("cached_data")
spark.sql("CACHE TABLE cached_data")

# Use cached data multiple times (benefits from caching)
result1 = spark.sql("SELECT COUNT(*) FROM cached_data")
result2 = spark.sql("SELECT AVG(value) FROM cached_data")
result1.show()
result2.show()

# Check cache status
print(f"Is DataFrame cached: {df.is_cached}")

# Uncache when done
df.unpersist()
spark.sql("UNCACHE TABLE cached_data")

# Different storage levels for caching
from pyspark import StorageLevel

# Cache with specific storage level
df.persist(StorageLevel.MEMORY_AND_DISK)
df.persist(StorageLevel.MEMORY_ONLY)
df.persist(StorageLevel.DISK_ONLY)


## 5. TEMPORARY TABLES (Delta/Database-style, if supported)
# Availability depends on catalog implementation

try:
    # Create temporary table with schema
    spark.sql("""
        CREATE TEMPORARY TABLE temp_table (
            id INT,
            name STRING,
            value DOUBLE
        ) USING DELTA
    """)
    
    # Insert data
    spark.sql("INSERT INTO temp_table VALUES (1, 'test', 10.5)")
    
    # Query temporary table
    spark.sql("SELECT * FROM temp_table").show()
    
except Exception as e:
    print(f"Temporary table creation not supported: {e}")


## 6. ADVANCED TEMPORARY VIEW PATTERNS

# Create temporary view from multiple sources
# Union multiple DataFrames
df1 = spark.read.csv("file1.csv", header=True)
df2 = spark.read.parquet("file2.parquet")

# Assuming same schema
union_df = df1.union(df2)
union_df.createOrReplaceTempView("combined_data")

# Create temporary view with transformations
transformed_df = df.select(
    col("id"),
    col("name").alias("customer_name"),
    (col("value") * 1.1).alias("value_with_tax")
)
transformed_df.createOrReplaceTempView("transformed_view")

# Create temporary view from aggregation
agg_df = df.groupBy("name").agg(spark_sum("value").alias("total_value"))
agg_df.createOrReplaceTempView("aggregated_view")

# Create temporary view from join
# Assuming we have another DataFrame
other_data = [(1, "Engineering"), (2, "Sales"), (3, "Marketing")]
dept_df = spark.createDataFrame(other_data, ["id", "department"])
dept_df.createOrReplaceTempView("departments")

joined_df = spark.sql("""
    SELECT d.*, dept.department
    FROM my_temp_view d
    JOIN departments dept ON d.id = dept.id
""")
joined_df.createOrReplaceTempView("joined_view")


## 7. CATALOG OPERATIONS

# List all temporary views
temp_views = spark.catalog.listTables()
for view in temp_views:
    if view.tableType == "TEMPORARY":
        print(f"Temporary view: {view.name}")

# Get table metadata
table_info = spark.catalog.listColumns("my_temp_view")
for col_info in table_info:
    print(f"Column: {col_info.name}, Type: {col_info.dataType}")

# Check if table/view exists
if spark.catalog.tableExists("my_temp_view"):
    print("View exists")

# Refresh table metadata (useful for file-based sources)
spark.catalog.refreshTable("my_temp_view")

# Clear catalog cache
spark.catalog.clearCache()


## 8. PERFORMANCE CONSIDERATIONS

# Create temporary view with repartitioning for better performance
df.repartition(4).createOrReplaceTempView("repartitioned_view")

# Create temporary view with specific partitioning
df.repartition(col("name")).createOrReplaceTempView("partitioned_by_name")

# Create temporary view with coalescing (reduce partitions)
df.coalesce(2).createOrReplaceTempView("coalesced_view")

# Monitor cache usage
def show_cache_status():
    cached_tables = [table for table in spark.catalog.listTables() 
                    if spark.table(table.name).is_cached]
    print(f"Cached tables: {[t.name for t in cached_tables]}")

show_cache_status()


## 9. ERROR HANDLING AND BEST PRACTICES

def safe_create_temp_view(df, view_name):
    """Safely create temporary view with error handling"""
    try:
        # Drop if exists
        if spark.catalog.tableExists(view_name):
            spark.catalog.dropTempView(view_name)
        
        # Create new view
        df.createOrReplaceTempView(view_name)
        print(f"Successfully created temporary view: {view_name}")
        
    except Exception as e:
        print(f"Error creating temporary view {view_name}: {e}")

def cleanup_temp_views(view_names):
    """Clean up multiple temporary views"""
    for view_name in view_names:
        try:
            if spark.catalog.tableExists(view_name):
                spark.catalog.dropTempView(view_name)
                print(f"Dropped temporary view: {view_name}")
        except Exception as e:
            print(f"Error dropping view {view_name}: {e}")

# Usage
safe_create_temp_view(df, "safe_temp_view")
cleanup_temp_views(["view1", "view2", "view3"])


## 10. TEMPORARY VIEW LIFECYCLE MANAGEMENT

class TempViewManager:
    def __init__(self, spark_session):
        self.spark = spark_session
        self.created_views = set()
    
    def create_view(self, df, view_name, cache=False):
        """Create temporary view with optional caching"""
        df.createOrReplaceTempView(view_name)
        self.created_views.add(view_name)
        
        if cache:
            self.spark.sql(f"CACHE TABLE {view_name}")
        
        print(f"Created temporary view: {view_name}")
    
    def cleanup_all(self):
        """Clean up all created views"""
        for view_name in self.created_views:
            try:
                if self.spark.catalog.tableExists(view_name):
                    self.spark.sql(f"UNCACHE TABLE {view_name}")
                    self.spark.catalog.dropTempView(view_name)
            except Exception as e:
                print(f"Error cleaning up {view_name}: {e}")
        
        self.created_views.clear()
        print("Cleaned up all temporary views")

# Usage
view_manager = TempViewManager(spark)
view_manager.create_view(df, "managed_view", cache=True)
view_manager.cleanup_all()

# Don't forget to stop SparkSession when done
spark.stop()
```
