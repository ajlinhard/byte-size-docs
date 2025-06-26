
# T-SQL Windows Functions
T-SQL has very similar window function capabilities, including `ROWS BETWEEN` and rolling averages. In fact, Spark SQL's window function syntax is largely based on the SQL standard that T-SQL also implements.

## T-SQL Window Functions - Nearly Identical Syntax

### 1. Rolling Average with ROWS BETWEEN
```sql
-- T-SQL syntax (almost identical to Spark SQL)
SELECT 
    salesperson,
    quarter,
    amount,
    AVG(CAST(amount AS FLOAT)) OVER (
        PARTITION BY salesperson 
        ORDER BY quarter 
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ) as rolling_avg_3
FROM sales;
```

### 2. Running Totals
```sql
SELECT 
    salesperson,
    quarter,
    amount,
    SUM(amount) OVER (
        PARTITION BY salesperson 
        ORDER BY quarter 
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) as running_total
FROM sales;
```

### 3. LAG/LEAD Functions
```sql
SELECT 
    salesperson,
    quarter,
    amount,
    LAG(amount, 1) OVER (PARTITION BY salesperson ORDER BY quarter) as prev_quarter,
    LEAD(amount, 1) OVER (PARTITION BY salesperson ORDER BY quarter) as next_quarter
FROM sales;
```

## Key Differences Between T-SQL and Spark SQL

### 1. **Data Type Handling**
```sql
-- T-SQL: Often need explicit casting for averages
AVG(CAST(amount AS FLOAT)) OVER (...)

-- Spark SQL: Automatic type promotion
AVG(amount) OVER (...)
```

### 2. **WINDOW Clause Support**
```sql
-- T-SQL: Full support for WINDOW clause (SQL Server 2022+)
SELECT 
    salesperson,
    amount,
    AVG(CAST(amount AS FLOAT)) OVER w as rolling_avg,
    SUM(amount) OVER w as rolling_sum
FROM sales
WINDOW w AS (PARTITION BY salesperson ORDER BY quarter ROWS BETWEEN 2 PRECEDING AND CURRENT ROW);

-- Earlier T-SQL versions: Must repeat window specification
SELECT 
    salesperson,
    amount,
    AVG(CAST(amount AS FLOAT)) OVER (PARTITION BY salesperson ORDER BY quarter ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) as rolling_avg,
    SUM(amount) OVER (PARTITION BY salesperson ORDER BY quarter ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) as rolling_sum
FROM sales;
```

### 3. **Date/Time RANGE BETWEEN**
```sql
-- T-SQL: Uses RANGE with date intervals
SELECT 
    date,
    amount,
    SUM(amount) OVER (
        ORDER BY date 
        RANGE BETWEEN INTERVAL '2' DAY PRECEDING AND CURRENT ROW
    ) as sum_last_3_days
FROM daily_sales;

-- Spark SQL: Similar but slightly different syntax
SELECT 
    date,
    amount,
    SUM(amount) OVER (
        ORDER BY date 
        RANGE BETWEEN INTERVAL 2 DAYS PRECEDING AND CURRENT ROW
    ) as sum_last_3_days
FROM daily_sales;
```

## T-SQL Specific Features

### 1. **ROWS vs RANGE - More explicit in T-SQL**
```sql
-- ROWS: Physical row-based window
SELECT 
    salesperson,
    amount,
    AVG(CAST(amount AS FLOAT)) OVER (
        PARTITION BY salesperson 
        ORDER BY quarter 
        ROWS BETWEEN 1 PRECEDING AND 1 FOLLOWING
    ) as avg_3_rows
FROM sales;

-- RANGE: Value-based window (logical)
SELECT 
    date,
    amount,
    SUM(amount) OVER (
        ORDER BY date 
        RANGE BETWEEN INTERVAL '1' DAY PRECEDING AND INTERVAL '1' DAY FOLLOWING
    ) as sum_3_day_range
FROM daily_sales;
```

### 2. **Additional T-SQL Window Functions**
```sql
-- CUME_DIST and PERCENT_RANK
SELECT 
    salesperson,
    amount,
    CUME_DIST() OVER (PARTITION BY salesperson ORDER BY amount) as cumulative_dist,
    PERCENT_RANK() OVER (PARTITION BY salesperson ORDER BY amount) as percent_rank
FROM sales;

-- PERCENTILE functions
SELECT 
    salesperson,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY amount) OVER (PARTITION BY salesperson) as median
FROM sales;
```

## Complete T-SQL Example
```sql
-- T-SQL rolling analytics example
WITH sales_data AS (
    SELECT 'Alice' as salesperson, '2024-Q1' as quarter, 1000 as amount
    UNION ALL SELECT 'Alice', '2024-Q2', 1200
    UNION ALL SELECT 'Alice', '2024-Q3', 900
    UNION ALL SELECT 'Alice', '2024-Q4', 1500
    UNION ALL SELECT 'Bob', '2024-Q1', 800
    UNION ALL SELECT 'Bob', '2024-Q2', 1100
    UNION ALL SELECT 'Bob', '2024-Q3', 1300
    UNION ALL SELECT 'Bob', '2024-Q4', 1000
)
SELECT 
    salesperson,
    quarter,
    amount,
    
    -- Rolling 3-quarter average
    AVG(CAST(amount AS FLOAT)) OVER (
        PARTITION BY salesperson 
        ORDER BY quarter 
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ) as rolling_avg_3q,
    
    -- Running total
    SUM(amount) OVER (
        PARTITION BY salesperson 
        ORDER BY quarter 
        ROWS UNBOUNDED PRECEDING
    ) as running_total,
    
    -- Previous quarter comparison
    amount - LAG(amount, 1) OVER (PARTITION BY salesperson ORDER BY quarter) as quarter_change,
    
    -- Ranking
    ROW_NUMBER() OVER (PARTITION BY salesperson ORDER BY amount DESC) as performance_rank
    
FROM sales_data
ORDER BY salesperson, quarter;
```

## Summary

**Similarities:**
- Nearly identical `ROWS BETWEEN` syntax
- Same window functions: `LAG`, `LEAD`, `ROW_NUMBER`, `RANK`, `SUM`, `AVG`, etc.
- Same partitioning and ordering concepts
- Similar performance optimizations for window coalescing

**Differences:**
- T-SQL may require explicit casting for certain operations
- WINDOW clause support varies by T-SQL version
- Slight syntax differences in date/time intervals
- T-SQL has some additional statistical functions

Overall, if you know window functions in Spark SQL, you'll be very comfortable with T-SQL window functions - they're 95% the same!
