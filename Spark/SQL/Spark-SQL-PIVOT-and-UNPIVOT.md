# Spark SQL PIVOT and UNPIVOT Cheat Sheet

## Overview

PIVOT and UNPIVOT are powerful SQL operations that transform data between row and column formats:
- **PIVOT**: Transforms rows into columns (wide format)
- **UNPIVOT**: Transforms columns into rows (long format)

## PIVOT Syntax

### Basic PIVOT Syntax
```sql
SELECT *
FROM (
    SELECT column1, column2, value_column
    FROM table_name
) AS source_table
PIVOT (
    aggregate_function(value_column)
    FOR pivot_column IN (value1, value2, value3, ...)
) AS pivot_table
```

### Alternative PIVOT Syntax (Spark 3.4+)
```sql
SELECT *
FROM table_name
PIVOT (
    aggregate_function(value_column)
    FOR pivot_column IN (value1, value2, value3)
)
```

## UNPIVOT Syntax

### Basic UNPIVOT Syntax (Spark 3.4+)
```sql
SELECT *
FROM table_name
UNPIVOT (
    value_column
    FOR pivot_column IN (col1, col2, col3)
)
```

### Alternative UNPIVOT with Column Aliases
```sql
SELECT *
FROM table_name
UNPIVOT (
    value_column
    FOR pivot_column IN (
        col1 AS 'label1',
        col2 AS 'label2',
        col3 AS 'label3'
    )
)
```

## PIVOT Examples

### Example 1: Sales Data by Quarter
```sql
-- Sample data: sales by salesperson and quarter
-- Original table: sales_data
-- | salesperson | quarter | sales_amount |
-- |-------------|---------|--------------|
-- | John        | Q1      | 1000         |
-- | John        | Q2      | 1500         |
-- | Jane        | Q1      | 1200         |
-- | Jane        | Q2      | 1800         |

-- PIVOT to show quarters as columns
SELECT *
FROM (
    SELECT salesperson, quarter, sales_amount
    FROM sales_data
) AS source
PIVOT (
    SUM(sales_amount)
    FOR quarter IN ('Q1', 'Q2', 'Q3', 'Q4')
) AS pivoted

-- Result:
-- | salesperson | Q1   | Q2   | Q3   | Q4   |
-- |-------------|------|------|------|------|
-- | John        | 1000 | 1500 | NULL | NULL |
-- | Jane        | 1200 | 1800 | NULL | NULL |
```

### Example 2: Product Ratings by Category
```sql
-- PIVOT with multiple aggregate functions
SELECT *
FROM (
    SELECT product_category, rating_type, rating_value
    FROM product_ratings
) AS source
PIVOT (
    AVG(rating_value)
    FOR rating_type IN ('quality', 'price', 'service')
) AS pivoted

-- Alternative with column aliases
SELECT *
FROM (
    SELECT product_category, rating_type, rating_value
    FROM product_ratings
) AS source
PIVOT (
    AVG(rating_value)
    FOR rating_type IN (
        'quality' AS quality_avg,
        'price' AS price_avg,
        'service' AS service_avg
    )
) AS pivoted
```

### Example 3: Dynamic PIVOT with Multiple Aggregations
```sql
-- Multiple aggregate functions in PIVOT
SELECT *
FROM (
    SELECT region, product, sales_amount, order_count
    FROM regional_sales
) AS source
PIVOT (
    SUM(sales_amount) AS total_sales,
    COUNT(order_count) AS total_orders
    FOR product IN ('ProductA', 'ProductB', 'ProductC')
) AS pivoted

-- Result columns: region, ProductA_total_sales, ProductA_total_orders, ProductB_total_sales, etc.
```

## UNPIVOT Examples

### Example 1: Quarterly Sales to Monthly View
```sql
-- Original pivoted table: quarterly_sales
-- | salesperson | Q1   | Q2   | Q3   | Q4   |
-- |-------------|------|------|------|------|
-- | John        | 1000 | 1500 | 1800 | 2000 |
-- | Jane        | 1200 | 1800 | 1600 | 2200 |

-- UNPIVOT to convert quarters back to rows
SELECT *
FROM quarterly_sales
UNPIVOT (
    sales_amount
    FOR quarter IN (Q1, Q2, Q3, Q4)
) AS unpivoted

-- Result:
-- | salesperson | quarter | sales_amount |
-- |-------------|---------|--------------|
-- | John        | Q1      | 1000         |
-- | John        | Q2      | 1500         |
-- | Jane        | Q1      | 1200         |
-- | Jane        | Q2      | 1800         |
```

### Example 2: Multiple Metrics UNPIVOT
```sql
-- UNPIVOT multiple related columns
SELECT *
FROM product_metrics
UNPIVOT (
    (sales_value, order_count)
    FOR time_period IN (
        (jan_sales, jan_orders) AS 'January',
        (feb_sales, feb_orders) AS 'February',
        (mar_sales, mar_orders) AS 'March'
    )
) AS unpivoted
```

### Example 3: Excluding NULL Values
```sql
-- UNPIVOT with NULL exclusion (default behavior)
SELECT *
FROM monthly_data
UNPIVOT EXCLUDE NULLS (
    metric_value
    FOR metric_name IN (
        revenue AS 'Revenue',
        profit AS 'Profit',
        orders AS 'Orders'
    )
)

-- Alternative: Include NULLs explicitly
SELECT *
FROM monthly_data
UNPIVOT INCLUDE NULLS (
    metric_value
    FOR metric_name IN (revenue, profit, orders)
)
```

## Advanced Use Cases

### Conditional PIVOT
```sql
-- PIVOT with conditional aggregation
SELECT *
FROM (
    SELECT customer_id, product_category, 
           CASE WHEN order_date >= '2023-01-01' THEN sales_amount ELSE 0 END as current_year_sales
    FROM orders
) AS source
PIVOT (
    SUM(current_year_sales)
    FOR product_category IN ('Electronics', 'Clothing', 'Books')
) AS pivoted
```

### PIVOT with Calculated Columns
```sql
-- PIVOT with expression in aggregate
SELECT *
FROM (
    SELECT region, month, revenue, costs
    FROM financial_data
) AS source
PIVOT (
    SUM(revenue - costs) AS net_profit
    FOR month IN ('Jan', 'Feb', 'Mar', 'Apr')
) AS pivoted
```

### Nested PIVOT Operations
```sql
-- First PIVOT by quarter, then by region
WITH quarterly_pivot AS (
    SELECT *
    FROM (
        SELECT region, quarter, product, sales_amount
        FROM sales_data
    ) AS source
    PIVOT (
        SUM(sales_amount)
        FOR quarter IN ('Q1', 'Q2', 'Q3', 'Q4')
    )
)
SELECT *
FROM quarterly_pivot
PIVOT (
    SUM(Q1) AS Q1_total,
    SUM(Q2) AS Q2_total
    FOR region IN ('North', 'South', 'East', 'West')
)
```

## PySpark DataFrame API Equivalents

### PIVOT in PySpark
```python
# Using DataFrame API
df.groupBy("salesperson") \
  .pivot("quarter") \
  .sum("sales_amount") \
  .show()

# With specific values
df.groupBy("salesperson") \
  .pivot("quarter", ["Q1", "Q2", "Q3", "Q4"]) \
  .sum("sales_amount") \
  .show()
```

### UNPIVOT in PySpark
```python
# Using SQL expression
df.selectExpr("salesperson", "stack(4, 'Q1', Q1, 'Q2', Q2, 'Q3', Q3, 'Q4', Q4) as (quarter, sales_amount)") \
  .where("sales_amount is not null") \
  .show()

# Using melt (if available)
from pyspark.sql.functions import expr
df.select("salesperson", 
          expr("stack(4, 'Q1', Q1, 'Q2', Q2, 'Q3', Q3, 'Q4', Q4) as (quarter, sales_amount)")) \
  .show()
```

## Common Patterns and Tips

### 1. Handle NULL Values
```sql
-- Replace NULLs with default values in PIVOT
SELECT *
FROM (
    SELECT salesperson, quarter, COALESCE(sales_amount, 0) as sales_amount
    FROM sales_data
) AS source
PIVOT (
    SUM(sales_amount)
    FOR quarter IN ('Q1', 'Q2', 'Q3', 'Q4')
)
```

### 2. Dynamic Column Names
```sql
-- Use variables for dynamic pivot columns (requires dynamic SQL construction)
-- Note: Spark SQL doesn't support dynamic PIVOT directly
-- Alternative: Use PySpark with dynamically generated column lists
```

### 3. Multiple Grouping Columns
```sql
-- PIVOT with multiple grouping columns
SELECT *
FROM (
    SELECT region, salesperson, quarter, sales_amount
    FROM sales_data
) AS source
PIVOT (
    SUM(sales_amount)
    FOR quarter IN ('Q1', 'Q2', 'Q3', 'Q4')
) AS pivoted
-- Results grouped by both region and salesperson
```

### 4. Combining PIVOT and UNPIVOT
```sql
-- Transform data format multiple times
WITH pivoted_data AS (
    SELECT *
    FROM sales_data
    PIVOT (SUM(sales_amount) FOR quarter IN ('Q1', 'Q2', 'Q3', 'Q4'))
),
unpivoted_data AS (
    SELECT *
    FROM pivoted_data
    UNPIVOT (sales_amount FOR quarter IN (Q1, Q2, Q3, Q4))
)
SELECT * FROM unpivoted_data
```

## Performance Considerations

- **PIVOT**: Can be memory-intensive for large datasets with many distinct pivot values
- **UNPIVOT**: Generally more efficient than PIVOT operations
- Use `LIMIT` on pivot values when possible to control output size
- Consider partitioning data before PIVOT operations for better performance
- Cache intermediate results for complex nested operations

## Version Compatibility

- **Spark 2.4+**: Basic PIVOT support
- **Spark 3.4+**: Enhanced UNPIVOT support with better syntax
- **Spark 3.5+**: Improved performance optimizations for both operations

---
# Examples with Sample Data
```sql
-- Create the product_metrics table with sample data
CREATE TABLE product_metrics (
    product_id STRING,
    product_name STRING,
    category STRING,
    jan_sales DECIMAL(10,2),
    jan_orders INT,
    feb_sales DECIMAL(10,2),
    feb_orders INT,
    mar_sales DECIMAL(10,2),
    mar_orders INT
);

-- Insert sample data
INSERT INTO product_metrics VALUES
('P001', 'Wireless Headphones', 'Electronics', 15000.00, 150, 18000.00, 180, 22000.00, 220),
('P002', 'Coffee Maker', 'Appliances', 8500.00, 85, 9200.00, 92, 11000.00, 110),
('P003', 'Running Shoes', 'Sports', 12000.00, 120, 14500.00, 145, 16800.00, 168),
('P004', 'Office Chair', 'Furniture', 25000.00, 100, 23000.00, 92, 28000.00, 112),
('P005', 'Smartphone Case', 'Electronics', 3200.00, 320, 3800.00, 380, 4100.00, 410),
('P006', 'Yoga Mat', 'Sports', 1800.00, 180, 2100.00, 210, 2400.00, 240),
('P007', 'Kitchen Blender', 'Appliances', 6500.00, 65, 7200.00, 72, 8000.00, 80),
('P008', 'Gaming Mouse', 'Electronics', 4200.00, 140, 4800.00, 160, 5400.00, 180);

-- View the original pivoted data
SELECT * FROM product_metrics;

-- Your UNPIVOT query
SELECT * FROM product_metrics 
UNPIVOT ( 
    (sales_value, order_count) 
    FOR time_period IN ( 
        (jan_sales, jan_orders) AS 'January', 
        (feb_sales, feb_orders) AS 'February', 
        (mar_sales, mar_orders) AS 'March' 
    ) 
) AS unpivoted
ORDER BY product_id, time_period;

-- Alternative: View results with better formatting
SELECT 
    product_id,
    product_name,
    category,
    time_period,
    sales_value,
    order_count,
    ROUND(sales_value / order_count, 2) as avg_order_value
FROM product_metrics 
UNPIVOT ( 
    (sales_value, order_count) 
    FOR time_period IN ( 
        (jan_sales, jan_orders) AS 'January', 
        (feb_sales, feb_orders) AS 'February', 
        (mar_sales, mar_orders) AS 'March' 
    ) 
) AS unpivoted
ORDER BY product_id, 
         CASE time_period 
             WHEN 'January' THEN 1 
             WHEN 'February' THEN 2 
             WHEN 'March' THEN 3 
         END;
```
