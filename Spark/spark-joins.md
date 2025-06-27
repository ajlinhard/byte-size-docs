# Spark Joins
Here's a comprehensive example of multi-table joins in PySpark:This comprehensive example demonstrates various multi-table join patterns in PySpark:

**Key Examples Covered:**

1. **Basic 3-Table Join** - Simple inner joins across customers, orders, and products
2. **5-Table Complex Join** - Using different join types (left, inner) with proper null handling
3. **Aggregated Joins** - Combining joins with group by and aggregation functions
4. **Self-Joins** - Finding relationships within the same table
5. **Window Functions** - Rankings and analytics across joined tables
6. **Conditional Joins** - Complex filtering and business logic
7. **SQL-Style Joins** - Using Spark SQL syntax for complex multi-table operations

**Jump To Examples**
- [PySpark Examples](#Python-PySpark-Examples)
- [Spark SQL Examples](#Spark-SQL-Examples)

**Important Join Considerations:**

- **Join Types**: Choose the right type (inner, left, right, full outer) based on your data requirements
- **Performance**: Use `broadcast()` for small tables, cache frequently used DataFrames
- **Null Handling**: Use `coalesce()` and proper filtering for left joins
- **Column Disambiguation**: Use aliases when tables have same column names
- **Optimization**: Filter data before joins and consider partitioning strategies

The examples show real-world scenarios like customer order analysis, product performance tracking, and business intelligence queries that commonly require joining multiple tables.
---
# Python PySpark Examples:
```python
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
```
---
# Spark SQL Examples
```python
from pyspark.sql import SparkSession

# Initialize SparkSession
spark = SparkSession.builder \
    .appName("Spark SQL Multi-Table Joins") \
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

# Create DataFrames and register as temporary views
customers_df = spark.createDataFrame(customers_data, 
    ["customer_id", "name", "email", "state"])
customers_df.createOrReplaceTempView("customers")

orders_df = spark.createDataFrame(orders_data, 
    ["order_id", "customer_id", "order_date", "total_amount", "status"])
orders_df.createOrReplaceTempView("orders")

order_items_df = spark.createDataFrame(order_items_data, 
    ["item_id", "order_id", "product_id", "quantity", "unit_price"])
order_items_df.createOrReplaceTempView("order_items")

products_df = spark.createDataFrame(products_data, 
    ["product_id", "product_name", "category", "list_price"])
products_df.createOrReplaceTempView("products")

categories_df = spark.createDataFrame(categories_data, 
    ["category_name", "description"])
categories_df.createOrReplaceTempView("categories")

# =============================================================================
# EXAMPLE 1: Basic Multi-Table Join (3 tables)
# =============================================================================
print("=== EXAMPLE 1: Customer Orders with Product Details ===")

basic_join_sql = """
SELECT 
    o.order_id,
    c.name,
    o.order_date,
    p.product_name,
    oi.quantity,
    oi.unit_price,
    (oi.quantity * oi.unit_price) AS line_total
FROM orders o
INNER JOIN customers c ON o.customer_id = c.customer_id
INNER JOIN order_items oi ON o.order_id = oi.order_id
INNER JOIN products p ON oi.product_id = p.product_id
ORDER BY o.order_id, p.product_name
"""

spark.sql(basic_join_sql).show()

# =============================================================================
# EXAMPLE 2: Complex Multi-Table Join (5 tables) with Different Join Types
# =============================================================================
print("\n=== EXAMPLE 2: Complete Order Analysis (All 5 Tables) ===")

complete_analysis_sql = """
SELECT 
    c.name,
    c.state,
    COALESCE(o.order_id, 0) AS order_id,
    COALESCE(o.status, 'no_orders') AS order_status,
    COALESCE(p.product_name, 'N/A') AS product,
    COALESCE(cat.category_name, 'N/A') AS category,
    COALESCE(oi.quantity, 0) AS qty,
    COALESCE(oi.quantity * oi.unit_price, 0.0) AS line_total
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
LEFT JOIN order_items oi ON o.order_id = oi.order_id
LEFT JOIN products p ON oi.product_id = p.product_id
LEFT JOIN categories cat ON p.category = cat.category_name
ORDER BY c.name, o.order_id
"""

spark.sql(complete_analysis_sql).show(truncate=False)

# =============================================================================
# EXAMPLE 3: Aggregated Multi-Table Join
# =============================================================================
print("\n=== EXAMPLE 3: Customer Summary with Aggregations ===")

customer_summary_sql = """
SELECT 
    c.customer_id,
    c.name,
    c.state,
    COUNT(DISTINCT o.order_id) AS total_orders,
    COALESCE(SUM(oi.quantity * oi.unit_price), 0) AS total_spent,
    COALESCE(AVG(o.total_amount), 0) AS avg_order_value,
    COALESCE(MAX(o.order_date), 'Never') AS last_order_date
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
LEFT JOIN order_items oi ON o.order_id = oi.order_id
LEFT JOIN products p ON oi.product_id = p.product_id
GROUP BY c.customer_id, c.name, c.state
ORDER BY total_spent DESC
"""

spark.sql(customer_summary_sql).show()

# =============================================================================
# EXAMPLE 4: Self-Join with Multi-Table Context
# =============================================================================
print("\n=== EXAMPLE 4: Customers from Same State ===")

same_state_sql = """
SELECT 
    c1.name AS customer_1,
    c2.name AS customer_2,
    c1.state AS shared_state
FROM customers c1
INNER JOIN customers c2 
    ON c1.state = c2.state 
    AND c1.customer_id != c2.customer_id
ORDER BY c1.state, c1.name
"""

spark.sql(same_state_sql).show()

# =============================================================================
# EXAMPLE 5: Window Functions with Multi-Table Joins
# =============================================================================
print("\n=== EXAMPLE 5: Product Rankings by Category ===")

product_rankings_sql = """
WITH product_performance AS (
    SELECT 
        p.product_id,
        p.product_name,
        cat.category_name,
        SUM(oi.quantity) AS total_sold,
        SUM(oi.quantity * oi.unit_price) AS total_revenue
    FROM order_items oi
    INNER JOIN products p ON oi.product_id = p.product_id
    INNER JOIN categories cat ON p.category = cat.category_name
    GROUP BY p.product_id, p.product_name, cat.category_name
)
SELECT 
    product_name,
    category_name,
    total_sold,
    total_revenue,
    ROW_NUMBER() OVER (PARTITION BY category_name ORDER BY total_revenue DESC) AS revenue_rank,
    DENSE_RANK() OVER (PARTITION BY category_name ORDER BY total_revenue DESC) AS revenue_dense_rank
FROM product_performance
ORDER BY category_name, revenue_rank
"""

spark.sql(product_rankings_sql).show()

# =============================================================================
# EXAMPLE 6: Complex Conditional Joins with CTEs
# =============================================================================
print("\n=== EXAMPLE 6: High-Value Customer Analysis ===")

high_value_sql = """
WITH customer_category_spending AS (
    SELECT 
        c.customer_id,
        c.name,
        cat.category_name,
        SUM(oi.quantity * oi.unit_price) AS category_spending,
        COUNT(DISTINCT o.order_id) AS orders_in_category
    FROM customers c
    INNER JOIN orders o ON c.customer_id = o.customer_id
    INNER JOIN order_items oi ON o.order_id = oi.order_id
    INNER JOIN products p ON oi.product_id = p.product_id
    INNER JOIN categories cat ON p.category = cat.category_name
    WHERE o.status = 'completed'
    GROUP BY c.customer_id, c.name, cat.category_name
)
SELECT 
    customer_id,
    name,
    category_name,
    category_spending,
    orders_in_category
FROM customer_category_spending
WHERE category_spending > 100
ORDER BY category_spending DESC
"""

spark.sql(high_value_sql).show()

# =============================================================================
# EXAMPLE 7: Advanced Analytics with Multiple CTEs
# =============================================================================
print("\n=== EXAMPLE 7: Customer Lifetime Value Analysis ===")

clv_analysis_sql = """
WITH customer_orders AS (
    SELECT 
        c.customer_id,
        c.name,
        c.state,
        COUNT(DISTINCT o.order_id) AS total_orders,
        SUM(oi.quantity * oi.unit_price) AS total_spent,
        MIN(o.order_date) AS first_order_date,
        MAX(o.order_date) AS last_order_date
    FROM customers c
    LEFT JOIN orders o ON c.customer_id = o.customer_id
    LEFT JOIN order_items oi ON o.order_id = oi.order_id
    GROUP BY c.customer_id, c.name, c.state
),
category_preferences AS (
    SELECT 
        c.customer_id,
        cat.category_name,
        SUM(oi.quantity * oi.unit_price) AS category_spending,
        ROW_NUMBER() OVER (PARTITION BY c.customer_id ORDER BY SUM(oi.quantity * oi.unit_price) DESC) as pref_rank
    FROM customers c
    INNER JOIN orders o ON c.customer_id = o.customer_id
    INNER JOIN order_items oi ON o.order_id = oi.order_id
    INNER JOIN products p ON oi.product_id = p.product_id
    INNER JOIN categories cat ON p.category = cat.category_name
    WHERE o.status = 'completed'
    GROUP BY c.customer_id, cat.category_name
)
SELECT 
    co.customer_id,
    co.name,
    co.state,
    co.total_orders,
    co.total_spent,
    co.first_order_date,
    co.last_order_date,
    cp.category_name AS preferred_category,
    cp.category_spending AS preferred_category_spending,
    CASE 
        WHEN co.total_spent > 400 THEN 'High Value'
        WHEN co.total_spent > 200 THEN 'Medium Value'
        ELSE 'Low Value'
    END AS customer_segment
FROM customer_orders co
LEFT JOIN category_preferences cp ON co.customer_id = cp.customer_id AND cp.pref_rank = 1
ORDER BY co.total_spent DESC
"""

spark.sql(clv_analysis_sql).show(truncate=False)

# =============================================================================
# EXAMPLE 8: Cross Join and Cartesian Product
# =============================================================================
print("\n=== EXAMPLE 8: Product Availability by State (Cross Join) ===")

cross_join_sql = """
SELECT 
    DISTINCT c.state,
    p.product_name,
    p.category,
    CASE 
        WHEN orders_in_state.state IS NOT NULL THEN 'Sold'
        ELSE 'Not Sold'
    END AS availability_status
FROM customers c
CROSS JOIN products p
LEFT JOIN (
    SELECT DISTINCT 
        c2.state,
        p2.product_id
    FROM customers c2
    INNER JOIN orders o ON c2.customer_id = o.customer_id
    INNER JOIN order_items oi ON o.order_id = oi.order_id
    INNER JOIN products p2 ON oi.product_id = p2.product_id
) orders_in_state ON c.state = orders_in_state.state AND p.product_id = orders_in_state.product_id
ORDER BY c.state, p.category, p.product_name
"""

spark.sql(cross_join_sql).show(truncate=False)

# =============================================================================
# EXAMPLE 9: UNION with Multi-Table Joins
# =============================================================================
print("\n=== EXAMPLE 9: Order Status Summary with UNION ===")

union_sql = """
SELECT 'Completed Orders' AS report_type, 
       COUNT(*) AS count,
       SUM(oi.quantity * oi.unit_price) AS total_value
FROM orders o
INNER JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.status = 'completed'

UNION ALL

SELECT 'Pending Orders' AS report_type,
       COUNT(*) AS count, 
       SUM(oi.quantity * oi.unit_price) AS total_value
FROM orders o
INNER JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.status = 'pending'

UNION ALL

SELECT 'Cancelled Orders' AS report_type,
       COUNT(*) AS count,
       SUM(oi.quantity * oi.unit_price) AS total_value
FROM orders o
INNER JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.status = 'cancelled'

ORDER BY report_type
"""

spark.sql(union_sql).show()

# =============================================================================
# EXAMPLE 10: Pivot Table with Multi-Table Joins
# =============================================================================
print("\n=== EXAMPLE 10: Customer Spending by Category (Pivot) ===")

pivot_sql = """
SELECT *
FROM (
    SELECT 
        c.name,
        cat.category_name,
        SUM(oi.quantity * oi.unit_price) AS spending
    FROM customers c
    INNER JOIN orders o ON c.customer_id = o.customer_id
    INNER JOIN order_items oi ON o.order_id = oi.order_id
    INNER JOIN products p ON oi.product_id = p.product_id
    INNER JOIN categories cat ON p.category = cat.category_name
    WHERE o.status = 'completed'
    GROUP BY c.name, cat.category_name
)
PIVOT (
    SUM(spending)
    FOR category_name IN ('Electronics', 'Education', 'Office')
)
ORDER BY name
"""

spark.sql(pivot_sql).show()

# =============================================================================
# EXAMPLE 11: Subqueries with EXISTS and NOT EXISTS
# =============================================================================
print("\n=== EXAMPLE 11: Customers with/without Orders ===")

exists_sql = """
-- Customers who have placed orders
SELECT c.name, c.state, 'Has Orders' AS status
FROM customers c
WHERE EXISTS (
    SELECT 1 
    FROM orders o 
    WHERE o.customer_id = c.customer_id
)

UNION ALL

-- Customers who haven't placed orders
SELECT c.name, c.state, 'No Orders' AS status
FROM customers c
WHERE NOT EXISTS (
    SELECT 1 
    FROM orders o 
    WHERE o.customer_id = c.customer_id
)
ORDER BY status, name
"""

spark.sql(exists_sql).show()

# =============================================================================
# EXAMPLE 12: Lateral View (Array Functions)
# =============================================================================
print("\n=== EXAMPLE 12: Order Analysis with Array Functions ===")

# First create a summary table with arrays
array_prep_sql = """
CREATE OR REPLACE TEMPORARY VIEW order_summary AS
SELECT 
    c.customer_id,
    c.name,
    COLLECT_LIST(p.product_name) AS products_ordered,
    COLLECT_SET(p.category) AS categories_ordered,
    SUM(oi.quantity * oi.unit_price) AS total_spent
FROM customers c
INNER JOIN orders o ON c.customer_id = o.customer_id
INNER JOIN order_items oi ON o.order_id = oi.order_id
INNER JOIN products p ON oi.product_id = p.product_id
WHERE o.status = 'completed'
GROUP BY c.customer_id, c.name
"""

spark.sql(array_prep_sql)

# Now use LATERAL VIEW to explode arrays
lateral_view_sql = """
SELECT 
    name,
    total_spent,
    category,
    SIZE(products_ordered) AS total_products_ordered
FROM order_summary
LATERAL VIEW EXPLODE(categories_ordered) exploded_table AS category
ORDER BY name, category
"""

spark.sql(lateral_view_sql).show()

print("\n=== Spark SQL Join Performance Tips ===")
print("1. Use BROADCAST hints for small tables: /*+ BROADCAST(small_table) */")
print("2. Use CTEs for complex queries to improve readability")
print("3. Filter early in WHERE clauses before joins")
print("4. Use appropriate join types based on data requirements")
print("5. Consider partitioning and bucketing for large datasets")
print("6. Use EXPLAIN to analyze query execution plans")

# Example with broadcast hint
broadcast_hint_sql = """
SELECT /*+ BROADCAST(p) */ 
    o.order_id,
    c.name,
    p.product_name
FROM orders o
INNER JOIN customers c ON o.customer_id = c.customer_id
INNER JOIN products p ON o.order_id IN (
    SELECT order_id FROM order_items WHERE product_id = p.product_id
)
WHERE p.list_price > 100
"""

print("\n=== Query Execution Plan Example ===")
spark.sql("EXPLAIN " + broadcast_hint_sql).show(truncate=False)

# Clean up
spark.stop()
```

---
# More Examples
```python
# =============================================================================
# JOIN PRACTICE EXAMPLES
# =============================================================================

print("\n" + "="*60)
print("JOIN EXAMPLES")
print("="*60)

# 1. INNER JOIN - Customers with their orders
print("\n1. INNER JOIN - Customers with Orders:")
customers_orders = customers_df.join(orders_df, "customer_id", "inner")
customers_orders.select("customer_name", "order_id", "order_date", "total_amount").show()

# 2. LEFT JOIN - All customers, with or without orders
print("\n2. LEFT JOIN - All Customers (with/without orders):")
all_customers_orders = customers_df.join(orders_df, "customer_id", "left")
all_customers_orders.select("customer_name", "order_id", "total_amount").show()

# 3. RIGHT JOIN - All orders, even with invalid customer_id
print("\n3. RIGHT JOIN - All Orders (even with invalid customer_id):")
orders_customers = customers_df.join(orders_df, "customer_id", "right")
orders_customers.select("customer_name", "order_id", "total_amount").show()

# 4. FULL OUTER JOIN - All customers and all orders
print("\n4. FULL OUTER JOIN - All Customers and Orders:")
full_join = customers_df.join(orders_df, "customer_id", "full_outer")
full_join.select("customer_name", "order_id", "total_amount").show()

# 5. COMPLEX JOIN - Order details with customer and product info
print("\n5. COMPLEX JOIN - Complete Order Details:")
complete_orders = orders_df \
    .join(customers_df, "customer_id", "inner") \
    .join(order_items_df, "order_id", "inner") \
    .join(products_df, "product_id", "inner")

complete_orders.select(
    "customer_name", "order_date", "product_name", 
    "quantity", "price", "total_amount"
).show(20, truncate=False)

# 6. SELF JOIN - Employees with their managers
print("\n6. SELF JOIN - Employees with Managers:")
managers = employees_df.select(
    employees_df.employee_id.alias("mgr_id"),
    employees_df.employee_name.alias("manager_name")
)

emp_mgr = employees_df.join(
    managers, 
    employees_df.manager_id == managers.mgr_id, 
    "left"
)
emp_mgr.select("employee_name", "manager_name", "department").show()

# 7. ANTI JOIN - Customers with no orders
print("\n7. ANTI JOIN - Customers with No Orders:")
customers_no_orders = customers_df.join(orders_df, "customer_id", "left_anti")
customers_no_orders.show()

# 8. SEMI JOIN - Customers who have placed orders
print("\n8. SEMI JOIN - Customers Who Have Orders:")
customers_with_orders = customers_df.join(orders_df, "customer_id", "left_semi")
customers_with_orders.show()
```
