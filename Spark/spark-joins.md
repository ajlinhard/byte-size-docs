from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when, coalesce, lit
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType

# Initialize SparkSession
spark = SparkSession.builder \
    .appName("Multi-Table Joins") \
    .getOrCreate()

# Sample data creation
customers_data = [
    (1, "John Doe", "john@email.com", "New York"),
    (2, "Jane Smith", "jane@email.com", "California"),
    (3, "Bob Johnson", "bob@email.com", "Texas"),
    (4, "Alice Brown", "alice@email.com", "Florida")
]

orders_data = [
    (101, 1, "2023-01-15", 250.00, "completed"),
    (102, 2, "2023-01-16", 180.50, "completed"),
    (103, 1, "2023-01-17", 320.75, "pending"),
    (104, 3, "2023-01-18", 95.25, "completed"),
    (105, 2, "2023-01-19", 450.00, "cancelled")
]

order_items_data = [
    (1, 101, 201, 2, 50.00),
    (2, 101, 202, 1, 150.00),
    (3, 102, 201, 3, 50.00),
    (4, 102, 203, 1, 30.50),
    (5, 103, 202, 2, 150.00),
    (6, 103, 204, 1, 20.75),
    (7, 104, 201, 1, 50.00),
    (8, 104, 205, 2, 22.63),
    (9, 105, 202, 3, 150.00)
]

products_data = [
    (201, "Laptop", "Electronics", 1200.00),
    (202, "Headphones", "Electronics", 150.00),
    (203, "Book", "Education", 30.50),
    (204, "Notebook", "Office", 20.75),
    (205, "Pen", "Office", 22.63)
]

categories_data = [
    ("Electronics", "Tech products and gadgets"),
    ("Education", "Books and learning materials"),
    ("Office", "Office supplies and stationery")
]

# Create DataFrames
customers = spark.createDataFrame(customers_data, 
    ["customer_id", "name", "email", "state"])

orders = spark.createDataFrame(orders_data, 
    ["order_id", "customer_id", "order_date", "total_amount", "status"])

order_items = spark.createDataFrame(order_items_data, 
    ["item_id", "order_id", "product_id", "quantity", "unit_price"])

products = spark.createDataFrame(products_data, 
    ["product_id", "product_name", "category", "list_price"])

categories = spark.createDataFrame(categories_data, 
    ["category_name", "description"])

# =============================================================================
# EXAMPLE 1: Basic Multi-Table Join (3 tables)
# =============================================================================
print("=== EXAMPLE 1: Customer Orders with Product Details ===")

basic_join = orders \
    .join(customers, "customer_id") \
    .join(order_items, "order_id") \
    .join(products, "product_id") \
    .select(
        "order_id",
        "name",
        "order_date", 
        "product_name",
        "quantity",
        "unit_price",
        (col("quantity") * col("unit_price")).alias("line_total")
    )

basic_join.show()

# =============================================================================
# EXAMPLE 2: Complex Multi-Table Join (5 tables) with Different Join Types
# =============================================================================
print("\n=== EXAMPLE 2: Complete Order Analysis (All 5 Tables) ===")

complete_analysis = customers \
    .join(orders, "customer_id", "left") \
    .join(order_items, "order_id", "left") \
    .join(products, "product_id", "left") \
    .join(categories, products.category == categories.category_name, "left") \
    .select(
        customers.name,
        customers.state,
        coalesce(orders.order_id, lit(0)).alias("order_id"),
        coalesce(orders.status, lit("no_orders")).alias("order_status"),
        coalesce(products.product_name, lit("N/A")).alias("product"),
        coalesce(categories.category_name, lit("N/A")).alias("category"),
        coalesce(order_items.quantity, lit(0)).alias("qty"),
        coalesce(
            col("quantity") * col("unit_price"), 
            lit(0.0)
        ).alias("line_total")
    )

complete_analysis.show(truncate=False)

# =============================================================================
# EXAMPLE 3: Aggregated Multi-Table Join
# =============================================================================
print("\n=== EXAMPLE 3: Customer Summary with Aggregations ===")

from pyspark.sql.functions import sum, count, avg, max

customer_summary = customers \
    .join(orders, "customer_id", "left") \
    .join(order_items, "order_id", "left") \
    .join(products, "product_id", "left") \
    .groupBy(
        customers.customer_id,
        customers.name,
        customers.state
    ) \
    .agg(
        count(orders.order_id).alias("total_orders"),
        coalesce(sum(col("quantity") * col("unit_price")), lit(0)).alias("total_spent"),
        coalesce(avg(orders.total_amount), lit(0)).alias("avg_order_value"),
        coalesce(max(orders.order_date), lit("Never")).alias("last_order_date")
    )

customer_summary.show()

# =============================================================================
# EXAMPLE 4: Self-Join with Multi-Table Context
# =============================================================================
print("\n=== EXAMPLE 4: Customers from Same State ===")

# Self-join to find customers from the same state
same_state_customers = customers.alias("c1") \
    .join(
        customers.alias("c2"), 
        (col("c1.state") == col("c2.state")) & (col("c1.customer_id") != col("c2.customer_id"))
    ) \
    .select(
        col("c1.name").alias("customer_1"),
        col("c2.name").alias("customer_2"),
        col("c1.state").alias("shared_state")
    )

same_state_customers.show()

# =============================================================================
# EXAMPLE 5: Window Functions with Multi-Table Joins
# =============================================================================
print("\n=== EXAMPLE 5: Product Rankings by Category ===")

from pyspark.sql.window import Window
from pyspark.sql.functions import row_number, dense_rank

# Calculate product performance across orders
product_performance = order_items \
    .join(products, "product_id") \
    .join(categories, products.category == categories.category_name) \
    .groupBy(
        "product_id",
        "product_name", 
        "category_name"
    ) \
    .agg(
        sum("quantity").alias("total_sold"),
        sum(col("quantity") * col("unit_price")).alias("total_revenue")
    )

# Add rankings within each category
window_spec = Window.partitionBy("category_name").orderBy(col("total_revenue").desc())

ranked_products = product_performance \
    .withColumn("revenue_rank", row_number().over(window_spec)) \
    .withColumn("revenue_dense_rank", dense_rank().over(window_spec))

ranked_products.show()

# =============================================================================
# EXAMPLE 6: Complex Conditional Joins
# =============================================================================
print("\n=== EXAMPLE 6: High-Value Customer Analysis ===")

# Identify high-value customers and their preferred categories
high_value_analysis = customers \
    .join(orders, "customer_id") \
    .join(order_items, "order_id") \
    .join(products, "product_id") \
    .join(categories, products.category == categories.category_name) \
    .filter(orders.status == "completed") \
    .groupBy(
        customers.customer_id,
        customers.name,
        categories.category_name
    ) \
    .agg(
        sum(col("quantity") * col("unit_price")).alias("category_spending"),
        count("order_id").alias("orders_in_category")
    ) \
    .filter(col("category_spending") > 100) \
    .orderBy(col("category_spending").desc())

high_value_analysis.show()

# =============================================================================
# EXAMPLE 7: Using SQL-style joins
# =============================================================================
print("\n=== EXAMPLE 7: SQL-Style Multi-Table Join ===")

# Register tables as temporary views
customers.createOrReplaceTempView("customers")
orders.createOrReplaceTempView("orders")
order_items.createOrReplaceTempView("order_items")
products.createOrReplaceTempView("products")
categories.createOrReplaceTempView("categories")

sql_result = spark.sql("""
    SELECT 
        c.name as customer_name,
        c.state,
        o.order_date,
        p.product_name,
        cat.category_name,
        oi.quantity,
        oi.unit_price,
        (oi.quantity * oi.unit_price) as line_total,
        o.status
    FROM customers c
    INNER JOIN orders o ON c.customer_id = o.customer_id
    INNER JOIN order_items oi ON o.order_id = oi.order_id  
    INNER JOIN products p ON oi.product_id = p.product_id
    LEFT JOIN categories cat ON p.category = cat.category_name
    WHERE o.status = 'completed'
    ORDER BY c.name, o.order_date
""")

sql_result.show(truncate=False)

# Performance tip: Cache frequently used DataFrames
customers.cache()
orders.cache()

print("\n=== Join Performance Tips ===")
print("1. Use broadcast joins for small tables")
print("2. Cache frequently accessed DataFrames")  
print("3. Consider bucketing for large tables with frequent joins")
print("4. Use appropriate join types (inner, left, right, full)")
print("5. Filter data before joins when possible")

# Example of broadcast join
from pyspark.sql.functions import broadcast

broadcast_example = orders.join(broadcast(products.filter(col("list_price") > 100)), 
                                products.product_id == order_items.product_id)

# Clean up
spark.stop()
