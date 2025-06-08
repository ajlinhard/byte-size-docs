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
---
# Altering Broadcasted Data Properly
**You cannot and should not alter broadcast tables while a join is running.** Here's why and what happens:

## Why You Can't Alter Broadcast Data

**Broadcast variables are immutable by design:**
- Once created, the broadcast variable's content cannot be modified
- This immutability is crucial for consistency across distributed tasks
- Tasks running on different nodes must see the same data

## What Happens If You Try

```python
from pyspark import broadcast

# Create broadcast variable
lookup_dict = {"A": "Apple", "B": "Banana"}
broadcast_lookup = sc.broadcast(lookup_dict)

# This WON'T affect the broadcast variable
lookup_dict["C"] = "Cherry"  # Only changes local dict, not broadcast

# The broadcast variable still contains the original data
print(broadcast_lookup.value)  # Still {"A": "Apple", "B": "Banana"}
```

## Race Conditions and Consistency Issues

If broadcast data could be modified during execution:
- **Inconsistent results**: Different tasks might see different versions
- **Race conditions**: Tasks starting at different times would get different data
- **Unpredictable behavior**: Results would depend on timing rather than logic

## Proper Way to Update Broadcast Data

```python
# Step 1: Complete current operations
current_result = large_df.join(broadcast(old_dim_table), "id").collect()

# Step 2: Unpersist old broadcast variable
old_broadcast.unpersist()

# Step 3: Create new broadcast variable with updated data
updated_dim_table = spark.table("updated_dimension_table")
new_broadcast = broadcast(updated_dim_table)

# Step 4: Use new broadcast variable in subsequent operations
new_result = large_df.join(new_broadcast, "id")
```

## Best Practices for Dynamic Dimension Data

If you need to handle changing dimension data:

**1. Batch Updates:**
```python
# Process in batches, updating broadcast variables between batches
for batch in data_batches:
    # Refresh dimension data
    current_dims = spark.table("dimensions").cache()
    
    # Process batch with current dimensions
    result = batch.join(broadcast(current_dims), "key")
    
    # Save results
    result.write.mode("append").saveAsTable("results")
```

**2. Version-Based Approach:**
```python
# Use timestamp or version in your logic
current_time = datetime.now()
dim_table = spark.table("dimensions").filter(f"valid_from <= '{current_time}'")
broadcast_dims = broadcast(dim_table)
```

**3. Check and Refresh Pattern:**
```python
def get_fresh_broadcast_dims():
    # Check if dimension data has changed
    latest_version = get_dimension_version()
    
    if latest_version != current_version:
        # Unpersist old broadcast
        if 'old_broadcast' in globals():
            old_broadcast.unpersist()
        
        # Create new broadcast
        fresh_dims = spark.table("dimensions")
        return broadcast(fresh_dims)
    
    return current_broadcast_dims
```

## Monitoring Long-Running Jobs

For long-running streaming jobs:

```python
# In streaming applications, recreate broadcast variables periodically
def process_batch(batch_df, batch_id):
    # Refresh broadcast data every N batches
    if batch_id % 100 == 0:
        global broadcast_lookup
        broadcast_lookup.unpersist()
        fresh_lookup = spark.table("lookup_table")
        broadcast_lookup = broadcast(fresh_lookup)
    
    # Use current broadcast variable
    return batch_df.join(broadcast_lookup, "key")
```

The key principle is: **complete your current operations, then refresh your broadcast variables** rather than trying to modify them mid-execution.
