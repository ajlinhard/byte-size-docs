
# CTEs (Common Table Expressions)
CTEs (Common Table Expressions) are fully supported in Spark SQL! CTEs are very useful for breaking down complex queries into readable, reusable parts.

## Basic CTE Syntax

```sql
WITH cte_name AS (
    SELECT column1, column2 FROM table_name WHERE condition
)
SELECT * FROM cte_name;
```

## Simple CTE Examples

**Spark SQL:**
```sql
-- Basic CTE
WITH high_value_items AS (
    SELECT id, name, value, category
    FROM my_database.sales_data
    WHERE value > 1000
)
SELECT category, COUNT(*) as item_count, AVG(value) as avg_value
FROM high_value_items
GROUP BY category;
```

**PySpark (using spark.sql()):**
```python
result = spark.sql("""
    WITH high_value_items AS (
        SELECT id, name, value, category
        FROM my_database.sales_data
        WHERE value > 1000
    )
    SELECT category, COUNT(*) as item_count, AVG(value) as avg_value
    FROM high_value_items
    GROUP BY category
""")
result.show()
```

## Multiple CTEs

```sql
-- Multiple CTEs
WITH 
high_performers AS (
    SELECT employee_id, name, department, salary
    FROM employees
    WHERE performance_rating >= 4
),
dept_averages AS (
    SELECT department, AVG(salary) as avg_dept_salary
    FROM employees
    GROUP BY department
)
SELECT 
    hp.name,
    hp.department,
    hp.salary,
    da.avg_dept_salary,
    hp.salary - da.avg_dept_salary as salary_diff
FROM high_performers hp
JOIN dept_averages da ON hp.department = da.department
ORDER BY salary_diff DESC;
```

## Nested/Recursive CTEs

```sql
-- CTE referencing another CTE
WITH 
monthly_sales AS (
    SELECT 
        DATE_TRUNC('month', sale_date) as month,
        product_id,
        SUM(amount) as monthly_amount
    FROM sales
    GROUP BY DATE_TRUNC('month', sale_date), product_id
),
product_trends AS (
    SELECT 
        product_id,
        month,
        monthly_amount,
        LAG(monthly_amount) OVER (PARTITION BY product_id ORDER BY month) as prev_month_amount
    FROM monthly_sales
),
growth_analysis AS (
    SELECT 
        product_id,
        month,
        monthly_amount,
        prev_month_amount,
        CASE 
            WHEN prev_month_amount IS NULL THEN NULL
            ELSE ((monthly_amount - prev_month_amount) / prev_month_amount) * 100
        END as growth_rate
    FROM product_trends
)
SELECT * FROM growth_analysis
WHERE growth_rate > 10
ORDER BY growth_rate DESC;
```

## CTEs with Window Functions

```python
query = """
WITH ranked_employees AS (
    SELECT 
        employee_id,
        name,
        department,
        salary,
        ROW_NUMBER() OVER (PARTITION BY department ORDER BY salary DESC) as dept_rank,
        DENSE_RANK() OVER (ORDER BY salary DESC) as overall_rank
    FROM employees
),
top_earners AS (
    SELECT *
    FROM ranked_employees
    WHERE dept_rank <= 3
)
SELECT 
    department,
    name,
    salary,
    dept_rank,
    overall_rank
FROM top_earners
ORDER BY department, dept_rank
"""

result = spark.sql(query)
result.show()
```

## CTEs for Data Quality Checks

```sql
WITH 
null_checks AS (
    SELECT 
        'customer_id' as column_name,
        COUNT(*) as total_rows,
        COUNT(customer_id) as non_null_rows,
        COUNT(*) - COUNT(customer_id) as null_rows
    FROM customers
    
    UNION ALL
    
    SELECT 
        'email' as column_name,
        COUNT(*) as total_rows,
        COUNT(email) as non_null_rows,
        COUNT(*) - COUNT(email) as null_rows
    FROM customers
),
duplicate_checks AS (
    SELECT 
        email,
        COUNT(*) as duplicate_count
    FROM customers
    WHERE email IS NOT NULL
    GROUP BY email
    HAVING COUNT(*) > 1
)
SELECT 
    'Null Analysis' as check_type,
    column_name,
    total_rows,
    null_rows,
    ROUND((null_rows * 100.0 / total_rows), 2) as null_percentage
FROM null_checks

UNION ALL

SELECT 
    'Duplicate Analysis' as check_type,
    'email' as column_name,
    COUNT(*) as total_duplicates,
    SUM(duplicate_count) as total_duplicate_rows,
    NULL as null_percentage
FROM duplicate_checks;
```

## CTEs in View Creation

```python
# Create a view using CTEs
spark.sql("""
    CREATE OR REPLACE VIEW my_database.customer_summary_view AS
    WITH 
    customer_orders AS (
        SELECT 
            customer_id,
            COUNT(*) as order_count,
            SUM(total_amount) as total_spent,
            MAX(order_date) as last_order_date
        FROM orders
        GROUP BY customer_id
    ),
    customer_categories AS (
        SELECT 
            customer_id,
            order_count,
            total_spent,
            last_order_date,
            CASE 
                WHEN total_spent >= 10000 THEN 'VIP'
                WHEN total_spent >= 5000 THEN 'Premium'
                WHEN total_spent >= 1000 THEN 'Regular'
                ELSE 'New'
            END as customer_tier
        FROM customer_orders
    )
    SELECT 
        c.customer_id,
        c.name,
        c.email,
        cc.order_count,
        cc.total_spent,
        cc.last_order_date,
        cc.customer_tier
    FROM customers c
    JOIN customer_categories cc ON c.customer_id = cc.customer_id
""")
```

## CTE with Aggregations and Joins

```python
complex_query = """
WITH 
product_metrics AS (
    SELECT 
        product_id,
        COUNT(DISTINCT customer_id) as unique_customers,
        COUNT(*) as total_orders,
        SUM(quantity) as total_quantity_sold,
        AVG(unit_price) as avg_unit_price
    FROM order_items oi
    JOIN orders o ON oi.order_id = o.order_id
    WHERE o.order_date >= '2024-01-01'
    GROUP BY product_id
),
category_performance AS (
    SELECT 
        p.category,
        COUNT(DISTINCT pm.product_id) as products_in_category,
        SUM(pm.unique_customers) as total_unique_customers,
        SUM(pm.total_quantity_sold) as category_quantity_sold,
        AVG(pm.avg_unit_price) as avg_category_price
    FROM product_metrics pm
    JOIN products p ON pm.product_id = p.product_id
    GROUP BY p.category
)
SELECT 
    category,
    products_in_category,
    total_unique_customers,
    category_quantity_sold,
    ROUND(avg_category_price, 2) as avg_category_price,
    ROUND(category_quantity_sold * avg_category_price, 2) as estimated_revenue
FROM category_performance
ORDER BY estimated_revenue DESC
"""

result = spark.sql(complex_query)
result.show()
```

## Key Benefits of CTEs in Spark SQL:

1. **Readability**: Break complex queries into logical steps
2. **Reusability**: Reference the same subquery multiple times
3. **Maintainability**: Easier to debug and modify
4. **Performance**: Spark can optimize the execution plan
5. **Modularity**: Each CTE represents a clear business logic step

CTEs are particularly useful in Spark SQL for data engineering tasks, complex analytics, and when building views or creating reusable query patterns.
