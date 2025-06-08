# Broadcasting
Broadcasting in PySpark is an optimization technique that efficiently distributes read-only data to all worker nodes in a Spark cluster. Instead of sending data with each task, broadcasting sends the data once to each node, where it's cached in memory for reuse across multiple tasks.

## How Broadcasting Works

When you broadcast a variable, Spark:
1. Serializes the data once on the driver
2. Sends it to each executor node once
3. Caches it in memory on each node
4. Makes it available to all tasks running on that node

## When to Use Broadcasting

Broadcasting is most beneficial for:
- **Small datasets** (typically < 200MB) that need to be joined with large datasets
- **Lookup tables, dictionaries, or configuration data**
- **Reference data** used across multiple operations
- **Avoiding expensive shuffle operations** in joins

## Basic Broadcasting Example

```python
from pyspark.sql import SparkSession
from pyspark import broadcast

spark = SparkSession.builder.appName("Broadcasting").getOrCreate()
sc = spark.sparkContext

# Create a small lookup dictionary
lookup_dict = {"A": "Apple", "B": "Banana", "C": "Cherry"}

# Broadcast the dictionary
broadcast_lookup = sc.broadcast(lookup_dict)

# Use in transformations
def map_values(row):
    return (row[0], broadcast_lookup.value.get(row[1], "Unknown"))

rdd = sc.parallelize([("John", "A"), ("Jane", "B"), ("Bob", "X")])
result = rdd.map(map_values).collect()
# Result: [('John', 'Apple'), ('Jane', 'Banana'), ('Bob', 'Unknown')]
```

## DataFrame Broadcasting (Broadcast Joins)

```python
from pyspark.sql.functions import broadcast

# Large dataset
large_df = spark.range(1000000).toDF("id")

# Small lookup table
small_df = spark.createDataFrame([(1, "One"), (2, "Two"), (3, "Three")], ["id", "name"])

# Broadcast join - hint to broadcast the small DataFrame
result = large_df.join(broadcast(small_df), "id")
```

## Automatic Broadcasting

Spark automatically broadcasts small DataFrames in joins when:
- The DataFrame size is below `spark.sql.adaptive.autoBroadcastJoinThreshold` (default: 10MB)
- Adaptive Query Execution is enabled

## Broadcasting Best Practices

**Do:**
- Broadcast small, frequently-used reference data
- Use for dimension tables in star schema joins
- Monitor memory usage on executors

**Don't:**
- Broadcast large datasets (causes memory issues)
- Broadcast data that changes frequently
- Forget to unpersist broadcast variables when done

## Managing Broadcast Variables

```python
# Create broadcast variable
broadcast_var = sc.broadcast(my_data)

# Access the value
broadcast_var.value

# Clean up when done
broadcast_var.unpersist()

# Or unpersist all broadcast variables
sc.clearCache()
```

## Performance Benefits

Broadcasting can provide significant performance improvements by:
- **Eliminating shuffle operations** in joins
- **Reducing network traffic** (data sent once vs. with each task)
- **Improving join performance** for small-to-large table joins
- **Reducing memory usage** compared to Cartesian products

The key is identifying the right use cases where small, read-only data needs to be shared across many tasks in your Spark application.
---
# Fact + Dimensional Table Example
In data warehousing, a **star schema** is a database design pattern where you have:

1. **Fact table** - A large central table containing quantitative data (metrics, measurements)
2. **Dimension tables** - Smaller tables containing descriptive attributes that provide context

## Star Schema Structure

```
    Customer Dim     Product Dim     Time Dim
         |               |              |
         |               |              |
         +----------- Fact Table -------+
                    (Sales Data)
```

## Why Dimension Tables Are Perfect for Broadcasting

**Dimension tables are typically:**
- **Small** (thousands to millions of rows vs. billions in fact tables)
- **Read-only** during analysis
- **Frequently joined** with fact tables
- **Static or slowly changing**

**Fact tables are typically:**
- **Very large** (millions to billions of rows)
- **The main subject** of analysis
- **Partitioned** across many nodes

## Example: Sales Data Analysis

```python
# Large fact table (distributed across cluster)
sales_fact = spark.table("sales_fact")  # 100M+ rows
# Columns: sale_id, customer_id, product_id, date_id, quantity, amount

# Small dimension tables (perfect for broadcasting)
customer_dim = spark.table("customer_dim")  # 50K rows
product_dim = spark.table("product_dim")    # 10K rows
date_dim = spark.table("date_dim")          # 3K rows

# Without broadcasting - causes expensive shuffles
result = sales_fact \
    .join(customer_dim, "customer_id") \
    .join(product_dim, "product_id") \
    .join(date_dim, "date_id")

# With broadcasting - much more efficient
from pyspark.sql.functions import broadcast

result = sales_fact \
    .join(broadcast(customer_dim), "customer_id") \
    .join(broadcast(product_dim), "product_id") \
    .join(broadcast(date_dim), "date_id")
```

## Why This Is Efficient

**Without broadcasting:**
- Spark shuffles both the large fact table AND dimension tables across the network
- Data movement is proportional to the size of ALL tables
- Multiple expensive shuffle operations

**With broadcasting:**
- Dimension tables are sent once to each node and cached
- Only the fact table remains distributed (no shuffle needed)
- Each node can perform local joins using its cached dimension data

## Real-World Scenario

Imagine analyzing retail sales:

```python
# Fact table: 500 million sales transactions
sales_fact = spark.table("sales")

# Dimension tables (small reference data)
stores = broadcast(spark.table("stores"))        # 2,000 stores
products = broadcast(spark.table("products"))    # 50,000 products  
customers = broadcast(spark.table("customers"))  # 1 million customers

# Efficient star schema join
sales_analysis = sales_fact \
    .join(stores, "store_id") \
    .join(products, "product_id") \
    .join(customers, "customer_id") \
    .select("store_name", "product_name", "customer_segment", "sales_amount")
```

This pattern transforms what would be multiple expensive shuffle operations into efficient local joins, dramatically improving query performance in typical data warehouse scenarios.

The key insight is that in star schemas, you're usually enriching large fact data with small descriptive information - exactly the use case broadcasting was designed to optimize.
