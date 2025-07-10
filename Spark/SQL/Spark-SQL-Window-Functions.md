# Spark SQL Window Functions
This will cover all the essential window functions with practical examples.I've created a comprehensive cheat sheet for Spark SQL window functions! This covers all the essential window functions with practical examples that you can run immediately.

The cheat sheet includes:

**Core Topics:**
- **Ranking Functions**: ROW_NUMBER(), RANK(), DENSE_RANK(), PERCENT_RANK(), NTILE()
- **Aggregate Window Functions**: SUM(), AVG(), COUNT(), MIN(), MAX()
- **Value Functions**: LAG(), LEAD(), FIRST_VALUE(), LAST_VALUE()
- **Frame Specifications**: ROWS vs RANGE, different frame boundaries

**Practical Examples:**
- Top N per group queries
- Salary percentiles and comparisons
- Gap analysis between consecutive values
- Department statistics and analysis
- Time series analysis
- Data quality checks

**Advanced Topics:**
- Performance optimization tips
- Common patterns and use cases
- Error handling and best practices
- Memory considerations

Each example includes both the SQL syntax and practical business use cases. The sample data setup at the beginning lets you run all the examples immediately in your Spark environment.

Would you like me to expand on any particular section or add examples for specific use cases you're working with?

---
# Spark SQL Window Functions Cheat Sheet

## Window Function Basics

Window functions perform calculations across a set of rows that are related to the current row. They don't reduce the number of rows like aggregate functions.

### Basic Window Syntax
```sql
SELECT 
    column1,
    column2,
    window_function() OVER (
        [PARTITION BY partition_column]
        [ORDER BY order_column [ASC|DESC]]
        [ROWS/RANGE frame_specification]
    ) AS window_result
FROM table_name
```

## Setting Up Sample Data

```python
# Create sample data for examples
from pyspark.sql import SparkSession
from pyspark.sql.types import *

spark = SparkSession.builder.appName("WindowFunctions").getOrCreate()

# Sample employee data
data = [
    (1, "John", "Engineering", 75000, "2020-01-15"),
    (2, "Jane", "Engineering", 80000, "2019-03-10"),
    (3, "Bob", "Sales", 65000, "2021-06-20"),
    (4, "Alice", "Sales", 70000, "2020-11-05"),
    (5, "Charlie", "Marketing", 60000, "2022-01-10"),
    (6, "David", "Engineering", 85000, "2018-07-15"),
    (7, "Eve", "Marketing", 62000, "2021-09-30"),
    (8, "Frank", "Sales", 68000, "2019-12-01")
]

schema = StructType([
    StructField("id", IntegerType(), True),
    StructField("name", StringType(), True),
    StructField("department", StringType(), True),
    StructField("salary", IntegerType(), True),
    StructField("hire_date", StringType(), True)
])

df = spark.createDataFrame(data, schema)
df.createOrReplaceTempView("employees")
```

## 1. Ranking Functions

### ROW_NUMBER()
Assigns a unique sequential number to each row within a partition.

```sql
-- Basic row numbering
SELECT 
    name, 
    department, 
    salary,
    ROW_NUMBER() OVER (ORDER BY salary DESC) AS overall_rank
FROM employees;

-- Row numbering within departments
SELECT 
    name, 
    department, 
    salary,
    ROW_NUMBER() OVER (PARTITION BY department ORDER BY salary DESC) AS dept_rank
FROM employees;
```

### RANK()
Assigns ranks with gaps when there are ties.

```sql
-- Rank employees by salary (with gaps for ties)
SELECT 
    name, 
    department, 
    salary,
    RANK() OVER (ORDER BY salary DESC) AS salary_rank
FROM employees;

-- Rank within departments
SELECT 
    name, 
    department, 
    salary,
    RANK() OVER (PARTITION BY department ORDER BY salary DESC) AS dept_salary_rank
FROM employees;
```

### DENSE_RANK()
Assigns ranks without gaps when there are ties.

```sql
-- Dense rank (no gaps)
SELECT 
    name, 
    department, 
    salary,
    DENSE_RANK() OVER (ORDER BY salary DESC) AS dense_rank
FROM employees;
```

### PERCENT_RANK()
Calculates the relative rank as a percentage.

```sql
-- Percentile rank
SELECT 
    name, 
    department, 
    salary,
    PERCENT_RANK() OVER (ORDER BY salary) AS percentile_rank
FROM employees;
```

### NTILE()
Divides rows into specified number of groups.

```sql
-- Divide employees into 3 salary groups
SELECT 
    name, 
    department, 
    salary,
    NTILE(3) OVER (ORDER BY salary) AS salary_tier
FROM employees;

-- Quartiles within each department
SELECT 
    name, 
    department, 
    salary,
    NTILE(4) OVER (PARTITION BY department ORDER BY salary) AS salary_quartile
FROM employees;
```

## 2. Aggregate Window Functions

### SUM()
```sql
-- Running total of salaries
SELECT 
    name, 
    department, 
    salary,
    SUM(salary) OVER (ORDER BY hire_date ROWS UNBOUNDED PRECEDING) AS running_total
FROM employees;

-- Department total salary
SELECT 
    name, 
    department, 
    salary,
    SUM(salary) OVER (PARTITION BY department) AS dept_total_salary
FROM employees;
```

### AVG()
```sql
-- Moving average of last 3 salaries
SELECT 
    name, 
    department, 
    salary,
    AVG(salary) OVER (ORDER BY hire_date ROWS 2 PRECEDING) AS moving_avg_3
FROM employees;

-- Compare individual salary to department average
SELECT 
    name, 
    department, 
    salary,
    AVG(salary) OVER (PARTITION BY department) AS dept_avg_salary,
    salary - AVG(salary) OVER (PARTITION BY department) AS salary_diff_from_avg
FROM employees;
```

### COUNT()
```sql
-- Count employees hired before each employee
SELECT 
    name, 
    hire_date,
    COUNT(*) OVER (ORDER BY hire_date ROWS UNBOUNDED PRECEDING) AS employees_hired_before
FROM employees;

-- Count employees in each department
SELECT 
    name, 
    department,
    COUNT(*) OVER (PARTITION BY department) AS dept_employee_count
FROM employees;
```

### MIN() and MAX()
```sql
-- Department salary range
SELECT 
    name, 
    department, 
    salary,
    MIN(salary) OVER (PARTITION BY department) AS dept_min_salary,
    MAX(salary) OVER (PARTITION BY department) AS dept_max_salary
FROM employees;
```

## 3. Value Functions

### LAG()
Access previous row values.

```sql
-- Compare salary with previous employee (by hire date)
SELECT 
    name, 
    hire_date,
    salary,
    LAG(salary, 1) OVER (ORDER BY hire_date) AS prev_salary,
    salary - LAG(salary, 1) OVER (ORDER BY hire_date) AS salary_change
FROM employees;

-- Previous salary within same department
SELECT 
    name, 
    department,
    salary,
    LAG(salary, 1) OVER (PARTITION BY department ORDER BY hire_date) AS prev_dept_salary
FROM employees;
```

### LEAD()
Access following row values.

```sql
-- Compare with next employee's salary
SELECT 
    name, 
    hire_date,
    salary,
    LEAD(salary, 1) OVER (ORDER BY hire_date) AS next_salary
FROM employees;
```

### FIRST_VALUE()
Get the first value in the window.

```sql
-- First hired employee in each department
SELECT 
    name, 
    department,
    hire_date,
    FIRST_VALUE(name) OVER (PARTITION BY department ORDER BY hire_date) AS first_hired
FROM employees;

-- Highest salary in each department
SELECT 
    name, 
    department, 
    salary,
    FIRST_VALUE(salary) OVER (PARTITION BY department ORDER BY salary DESC) AS highest_dept_salary
FROM employees;
```

### LAST_VALUE()
Get the last value in the window.

```sql
-- Last hired employee in each department
SELECT 
    name, 
    department,
    hire_date,
    LAST_VALUE(name) OVER (
        PARTITION BY department 
        ORDER BY hire_date 
        ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
    ) AS last_hired
FROM employees;
```

## 4. Window Frame Specifications

### ROWS vs RANGE
```sql
-- ROWS: Physical number of rows
SELECT 
    name, 
    salary,
    AVG(salary) OVER (ORDER BY salary ROWS BETWEEN 1 PRECEDING AND 1 FOLLOWING) AS avg_3_rows
FROM employees;

-- RANGE: Logical range of values
SELECT 
    name, 
    salary,
    AVG(salary) OVER (ORDER BY salary RANGE BETWEEN 5000 PRECEDING AND 5000 FOLLOWING) AS avg_salary_range
FROM employees;
```

### Common Frame Specifications
```sql
-- Running totals and averages
SELECT 
    name, 
    salary,
    -- Running sum from beginning to current row
    SUM(salary) OVER (ORDER BY salary ROWS UNBOUNDED PRECEDING) AS running_sum,
    
    -- Average of current and previous 2 rows
    AVG(salary) OVER (ORDER BY salary ROWS 2 PRECEDING) AS avg_last_3,
    
    -- Sum of current row and next row
    SUM(salary) OVER (ORDER BY salary ROWS BETWEEN CURRENT ROW AND 1 FOLLOWING) AS sum_current_next,
    
    -- Average of entire partition
    AVG(salary) OVER (ORDER BY salary ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS overall_avg
FROM employees;
```

## 5. Practical Examples

### Top N Per Group
```sql
-- Top 2 highest paid employees per department
SELECT *
FROM (
    SELECT 
        name, 
        department, 
        salary,
        ROW_NUMBER() OVER (PARTITION BY department ORDER BY salary DESC) as rn
    FROM employees
) ranked
WHERE rn <= 2;
```

### Salary Percentiles
```sql
-- Salary percentiles and comparison
SELECT 
    name, 
    department, 
    salary,
    PERCENT_RANK() OVER (ORDER BY salary) AS salary_percentile,
    CASE 
        WHEN PERCENT_RANK() OVER (ORDER BY salary) >= 0.8 THEN 'Top 20%'
        WHEN PERCENT_RANK() OVER (ORDER BY salary) >= 0.5 THEN 'Above Average'
        ELSE 'Below Average'
    END AS salary_category
FROM employees;
```

### Gap Analysis
```sql
-- Find gaps between consecutive salaries
SELECT 
    name, 
    salary,
    LAG(salary) OVER (ORDER BY salary) AS prev_salary,
    salary - LAG(salary) OVER (ORDER BY salary) AS salary_gap
FROM employees
ORDER BY salary;
```

### Department Statistics
```sql
-- Comprehensive department analysis
SELECT 
    name, 
    department, 
    salary,
    COUNT(*) OVER (PARTITION BY department) AS dept_size,
    AVG(salary) OVER (PARTITION BY department) AS dept_avg_salary,
    salary - AVG(salary) OVER (PARTITION BY department) AS diff_from_dept_avg,
    RANK() OVER (PARTITION BY department ORDER BY salary DESC) AS dept_salary_rank,
    PERCENT_RANK() OVER (PARTITION BY department ORDER BY salary) AS dept_salary_percentile
FROM employees;
```

### Time Series Analysis
```sql
-- Monthly hiring trends (if you have date data)
SELECT 
    hire_date,
    COUNT(*) OVER (ORDER BY hire_date ROWS UNBOUNDED PRECEDING) AS cumulative_hires,
    AVG(salary) OVER (ORDER BY hire_date ROWS 2 PRECEDING) AS avg_salary_last_3_hires
FROM employees
ORDER BY hire_date;
```

## 6. Performance Tips

### Optimize Window Functions
```sql
-- Use LIMIT with window functions efficiently
SELECT *
FROM (
    SELECT 
        name, 
        department, 
        salary,
        ROW_NUMBER() OVER (PARTITION BY department ORDER BY salary DESC) as rn
    FROM employees
) ranked
WHERE rn <= 3;  -- More efficient than LIMIT on the outer query
```

### Combine Multiple Window Functions
```sql
-- Efficient: Multiple window functions with same OVER clause
SELECT 
    name, 
    department, 
    salary,
    ROW_NUMBER() OVER w AS rn,
    RANK() OVER w AS rank,
    DENSE_RANK() OVER w AS dense_rank
FROM employees
WINDOW w AS (PARTITION BY department ORDER BY salary DESC);
```

## 7. Common Patterns and Use Cases

### Data Quality Checks
```sql
-- Find duplicate records
SELECT 
    name, 
    department, 
    salary,
    COUNT(*) OVER (PARTITION BY name, department) AS duplicate_count
FROM employees;
```

### Cohort Analysis
```sql
-- Employee cohorts by hire year
SELECT 
    name,
    YEAR(hire_date) AS hire_year,
    COUNT(*) OVER (PARTITION BY YEAR(hire_date)) AS cohort_size,
    ROW_NUMBER() OVER (PARTITION BY YEAR(hire_date) ORDER BY salary DESC) AS salary_rank_in_cohort
FROM employees;
```

### Running Calculations
```sql
-- Running calculations with reset
SELECT 
    name,
    department,
    salary,
    SUM(salary) OVER (PARTITION BY department ORDER BY hire_date) AS running_dept_salary,
    AVG(salary) OVER (PARTITION BY department ORDER BY hire_date) AS running_dept_avg
FROM employees;
```

## 8. Error Handling and Best Practices

### Handle NULL Values
```sql
-- Handle NULLs in window functions
SELECT 
    name, 
    salary,
    LAG(salary, 1, 0) OVER (ORDER BY hire_date) AS prev_salary_with_default,
    COALESCE(LAG(salary) OVER (ORDER BY hire_date), 0) AS prev_salary_coalesce
FROM employees;
```

### Memory Considerations
```sql
-- Be careful with unbounded windows on large datasets
-- This can consume significant memory
SELECT 
    name, 
    salary,
    -- Use bounded windows when possible
    AVG(salary) OVER (ORDER BY hire_date ROWS 100 PRECEDING) AS bounded_avg
FROM employees;
```

## Common Window Function Combinations

```sql
-- Comprehensive employee analysis
SELECT 
    name,
    department,
    salary,
    hire_date,
    -- Ranking within department
    ROW_NUMBER() OVER (PARTITION BY department ORDER BY salary DESC) as dept_salary_rank,
    -- Overall percentile
    PERCENT_RANK() OVER (ORDER BY salary) as overall_percentile,
    -- Department statistics
    COUNT(*) OVER (PARTITION BY department) as dept_size,
    AVG(salary) OVER (PARTITION BY department) as dept_avg_salary,
    -- Comparison with previous hire
    LAG(salary) OVER (ORDER BY hire_date) as prev_hire_salary,
    -- Running totals
    SUM(salary) OVER (ORDER BY hire_date ROWS UNBOUNDED PRECEDING) as running_payroll
FROM employees
ORDER BY department, salary DESC;
```

This cheat sheet covers the most important window functions in Spark SQL with practical examples you can run immediately!
