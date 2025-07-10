# Spark SQL - Group By
Here is a comprehensive Spark SQL GROUP BY cheat sheet that covers:

**Key Features:**
- Basic GROUP BY syntax and common aggregate functions
- Multiple column grouping and HAVING clauses
- Advanced operations like ROLLUP, CUBE, and GROUPING SETS
- Date-based grouping and statistical functions
- Complex conditional aggregations
- Both SQL and PySpark DataFrame examples

**Practical Examples Include:**
- Employee salary analysis by department
- Sales data aggregation by time periods
- Top N records per group
- Running totals and percentiles
- String aggregation and collection functions

**Performance Tips:**
- Query optimization techniques
- Adaptive query execution settings
- Common patterns for efficient grouping

The cheat sheet is structured to be both a quick reference and a learning resource, with sample data setup included for testing the examples. Each section builds from basic concepts to more advanced use cases you'd encounter in real-world data analysis.

---
# Spark SQL GROUP BY Operations Cheat Sheet

## Basic GROUP BY Syntax

```sql
SELECT column1, aggregate_function(column2)
FROM table_name
GROUP BY column1
```

## Common Aggregate Functions

### Count Operations
```sql
-- Count all rows per group
SELECT department, COUNT(*) as employee_count
FROM employees
GROUP BY department;

-- Count non-null values
SELECT department, COUNT(salary) as employees_with_salary
FROM employees
GROUP BY department;

-- Count distinct values
SELECT department, COUNT(DISTINCT job_title) as unique_jobs
FROM employees
GROUP BY department;
```

### Sum and Average
```sql
-- Sum values
SELECT department, SUM(salary) as total_salary
FROM employees
GROUP BY department;

-- Average values
SELECT department, AVG(salary) as avg_salary
FROM employees
GROUP BY department;

-- Multiple aggregations
SELECT department, 
       COUNT(*) as employee_count,
       SUM(salary) as total_salary,
       AVG(salary) as avg_salary,
       MIN(salary) as min_salary,
       MAX(salary) as max_salary
FROM employees
GROUP BY department;
```

### Min/Max Operations
```sql
-- Find extremes
SELECT department, 
       MIN(hire_date) as first_hire,
       MAX(hire_date) as last_hire
FROM employees
GROUP BY department;
```

## Multiple Column GROUP BY

```sql
-- Group by multiple columns
SELECT department, job_title, COUNT(*) as count
FROM employees
GROUP BY department, job_title;

-- Group by computed columns
SELECT YEAR(hire_date) as hire_year, 
       department, 
       COUNT(*) as hires_count
FROM employees
GROUP BY YEAR(hire_date), department;
```

## HAVING Clause (Filter Groups)

```sql
-- Filter groups after aggregation
SELECT department, COUNT(*) as employee_count
FROM employees
GROUP BY department
HAVING COUNT(*) > 10;

-- Multiple conditions in HAVING
SELECT department, AVG(salary) as avg_salary
FROM employees
GROUP BY department
HAVING AVG(salary) > 50000 AND COUNT(*) >= 5;
```

## Advanced GROUP BY with Window Functions

```sql
-- Group by with ranking
SELECT department, 
       employee_name,
       salary,
       RANK() OVER (PARTITION BY department ORDER BY salary DESC) as salary_rank
FROM employees;

-- Running totals within groups
SELECT department, 
       employee_name,
       salary,
       SUM(salary) OVER (PARTITION BY department ORDER BY salary) as running_total
FROM employees;
```

## GROUP BY with CASE Statements

```sql
-- Conditional grouping
SELECT 
    CASE 
        WHEN salary < 40000 THEN 'Low'
        WHEN salary BETWEEN 40000 AND 80000 THEN 'Medium'
        ELSE 'High'
    END as salary_range,
    COUNT(*) as employee_count
FROM employees
GROUP BY 
    CASE 
        WHEN salary < 40000 THEN 'Low'
        WHEN salary BETWEEN 40000 AND 80000 THEN 'Medium'
        ELSE 'High'
    END;
```

## GROUP BY with Date Functions

```sql
-- Group by date parts
SELECT YEAR(order_date) as order_year, 
       MONTH(order_date) as order_month,
       SUM(amount) as monthly_sales
FROM orders
GROUP BY YEAR(order_date), MONTH(order_date)
ORDER BY order_year, order_month;

-- Group by date ranges
SELECT DATE_TRUNC('week', order_date) as week_start,
       COUNT(*) as orders_count,
       SUM(amount) as weekly_sales
FROM orders
GROUP BY DATE_TRUNC('week', order_date);
```

## ROLLUP and CUBE Operations

```sql
-- ROLLUP: Creates subtotals and grand totals
SELECT department, job_title, COUNT(*) as count
FROM employees
GROUP BY ROLLUP(department, job_title);

-- CUBE: Creates all possible combinations
SELECT department, job_title, COUNT(*) as count
FROM employees
GROUP BY CUBE(department, job_title);

-- GROUPING SETS: Custom grouping combinations
SELECT department, job_title, COUNT(*) as count
FROM employees
GROUP BY GROUPING SETS (
    (department, job_title),
    (department),
    ()
);
```

## Collecting Values within Groups

```sql
-- Collect all values in a group
SELECT department, 
       COLLECT_LIST(employee_name) as employees
FROM employees
GROUP BY department;

-- Collect distinct values
SELECT department, 
       COLLECT_SET(job_title) as unique_jobs
FROM employees
GROUP BY department;
```

## Percentiles and Statistical Functions

```sql
-- Calculate percentiles
SELECT department,
       PERCENTILE_APPROX(salary, 0.5) as median_salary,
       PERCENTILE_APPROX(salary, 0.25) as q1_salary,
       PERCENTILE_APPROX(salary, 0.75) as q3_salary
FROM employees
GROUP BY department;

-- Standard deviation and variance
SELECT department,
       STDDEV(salary) as salary_stddev,
       VARIANCE(salary) as salary_variance
FROM employees
GROUP BY department;
```

## Complex Aggregations with Expressions

```sql
-- Conditional aggregation
SELECT department,
       COUNT(*) as total_employees,
       SUM(CASE WHEN salary > 50000 THEN 1 ELSE 0 END) as high_earners,
       AVG(CASE WHEN job_title = 'Manager' THEN salary END) as avg_manager_salary
FROM employees
GROUP BY department;

-- String aggregation
SELECT department,
       COUNT(*) as employee_count,
       CONCAT_WS(', ', COLLECT_LIST(employee_name)) as employee_names
FROM employees
GROUP BY department;
```

## PySpark DataFrame GROUP BY Examples

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import *

# Basic grouping
df.groupBy("department").count().show()

# Multiple aggregations
df.groupBy("department").agg(
    count("*").alias("employee_count"),
    avg("salary").alias("avg_salary"),
    max("salary").alias("max_salary")
).show()

# Group by multiple columns
df.groupBy("department", "job_title").agg(
    count("*").alias("count"),
    avg("salary").alias("avg_salary")
).show()

# Conditional aggregation
df.groupBy("department").agg(
    count("*").alias("total_count"),
    sum(when(col("salary") > 50000, 1).otherwise(0)).alias("high_earners")
).show()
```

## Performance Tips

### Optimize GROUP BY Performance
```sql
-- Use appropriate data types
-- Partition tables by frequently grouped columns
-- Consider bucketing for large datasets
-- Use broadcast joins when grouping with small lookup tables

-- Enable adaptive query execution
SET spark.sql.adaptive.enabled=true;
SET spark.sql.adaptive.coalescePartitions.enabled=true;
```

### Common GROUP BY Patterns
```sql
-- Top N per group
SELECT *
FROM (
    SELECT department, employee_name, salary,
           ROW_NUMBER() OVER (PARTITION BY department ORDER BY salary DESC) as rn
    FROM employees
) ranked
WHERE rn <= 3;

-- Running totals
SELECT department, employee_name, salary,
       SUM(salary) OVER (PARTITION BY department ORDER BY salary 
                        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) as running_total
FROM employees;
```

## Error Handling and Common Issues

```sql
-- Handle NULL values in grouping
SELECT COALESCE(department, 'Unknown') as department,
       COUNT(*) as count
FROM employees
GROUP BY COALESCE(department, 'Unknown');

-- Ensure proper ordering with aggregations
SELECT department, AVG(salary) as avg_salary
FROM employees
GROUP BY department
ORDER BY avg_salary DESC;
```

## Sample Data Setup for Testing

```sql
-- Create sample table
CREATE TABLE employees (
    employee_id INT,
    employee_name STRING,
    department STRING,
    job_title STRING,
    salary DECIMAL(10,2),
    hire_date DATE
);

-- Insert sample data
INSERT INTO employees VALUES
(1, 'John Doe', 'Engineering', 'Developer', 75000, '2020-01-15'),
(2, 'Jane Smith', 'Engineering', 'Manager', 95000, '2019-03-20'),
(3, 'Bob Johnson', 'Sales', 'Representative', 45000, '2021-06-10'),
(4, 'Alice Brown', 'Sales', 'Manager', 85000, '2018-11-05'),
(5, 'Charlie Wilson', 'Marketing', 'Analyst', 55000, '2020-09-12');
```
