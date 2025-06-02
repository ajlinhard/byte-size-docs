Here's a comprehensive cheatsheet for Python pandas window functions that correspond to SQL window functions:This cheatsheet covers all the major SQL window functions and their pandas equivalents. The key concepts to remember are:

**Ranking functions** use `.rank()` with different methods (`min`, `dense`, `average`), **offset functions** use `.shift()` for LAG/LEAD operations, **distribution functions** use `pd.qcut()` for NTILE, and **aggregate functions** use `.cumsum()`, `.expanding()`, or `.rolling()` for running calculations.

The most important pattern is using `.groupby()` combined with `.transform()` or direct aggregation methods to replicate SQL's `PARTITION BY` clause. Always remember to sort your data appropriately when order matters for your window function results.

### Helpful Pandas Docs:
- [Pandas sort_values()](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.sort_values.html)
- [Pandas GroupBy rank()](https://pandas.pydata.org/docs/reference/api/pandas.core.groupby.DataFrameGroupBy.rank.html#pandas.core.groupby.DataFrameGroupBy.rank)
- [Pandas GroupBy qcut()](https://pandas.pydata.org/docs/reference/api/pandas.qcut.html)

---
## Python Code Examples:
# Pandas Window Functions Cheatsheet

## Setup and Sample Data
```python
import pandas as pd
import numpy as np

# Sample DataFrame
df = pd.DataFrame({
    'department': ['Sales', 'Sales', 'Sales', 'Marketing', 'Marketing', 'IT', 'IT'],
    'employee': ['Alice', 'Bob', 'Charlie', 'David', 'Eve', 'Frank', 'Grace'],
    'salary': [50000, 60000, 55000, 65000, 70000, 80000, 75000],
    'hire_date': pd.to_datetime(['2020-01-15', '2019-03-10', '2021-07-20', 
                                '2018-11-05', '2020-09-12', '2017-05-30', '2019-12-01'])
})
```

## Ranking Functions

### ROW_NUMBER()
```python
# Basic row number
df['row_num'] = df.reset_index().index + 1

# Row number within groups (PARTITION BY)
df['row_num_dept'] = df.groupby('department').cumcount() + 1

# Row number with ordering
df['row_num_salary'] = df.sort_values('salary').reset_index(drop=True).index + 1

# Row number within groups with ordering
df['row_num_dept_salary'] = (df.sort_values(['department', 'salary'])
                             .groupby('department').cumcount() + 1)
```

### RANK()
```python
# Basic rank (ties get same rank, next rank skips)
df['rank_salary'] = df['salary'].rank(method='min', ascending=False)

# Rank within groups
df['rank_salary_dept'] = df.groupby('department')['salary'].rank(method='min', ascending=False)
```

### DENSE_RANK()
```python
# Dense rank (ties get same rank, next rank doesn't skip)
df['dense_rank_salary'] = df['salary'].rank(method='dense', ascending=False)

# Dense rank within groups
df['dense_rank_salary_dept'] = df.groupby('department')['salary'].rank(method='dense', ascending=False)
```

### PERCENT_RANK()
```python
# Percent rank
df['percent_rank'] = df['salary'].rank(pct=True, ascending=False)

# Percent rank within groups
df['percent_rank_dept'] = df.groupby('department')['salary'].rank(pct=True, ascending=False)
```

## Distribution Functions

### NTILE(n)
```python
# Divide into quartiles (4 groups)
df['quartile'] = pd.qcut(df['salary'], q=4, labels=['Q1', 'Q2', 'Q3', 'Q4'])

# Divide into n groups with equal counts
df['quintile'] = pd.qcut(df['salary'].rank(method='first'), q=5, labels=False) + 1

# NTILE within groups
df['quartile_dept'] = (df.groupby('department')['salary']
                       .apply(lambda x: pd.qcut(x.rank(method='first'), 
                                               q=min(4, len(x)), labels=False) + 1))
```

### CUME_DIST()
```python
# Cumulative distribution
df['cume_dist'] = df['salary'].rank(pct=True)

# Cumulative distribution within groups
df['cume_dist_dept'] = df.groupby('department')['salary'].rank(pct=True)
```

## Offset Functions

### LAG() and LEAD()
```python
# LAG - previous value
df_sorted = df.sort_values(['department', 'salary'])
df_sorted['prev_salary'] = df_sorted.groupby('department')['salary'].shift(1)

# LEAD - next value
df_sorted['next_salary'] = df_sorted.groupby('department')['salary'].shift(-1)

# LAG/LEAD with custom offset
df_sorted['salary_2_back'] = df_sorted.groupby('department')['salary'].shift(2)
df_sorted['salary_2_forward'] = df_sorted.groupby('department')['salary'].shift(-2)

# LAG/LEAD with default values
df_sorted['prev_salary_default'] = df_sorted.groupby('department')['salary'].shift(1).fillna(0)
```

### FIRST_VALUE() and LAST_VALUE()
```python
# First value in group
df['first_salary_dept'] = df.groupby('department')['salary'].transform('first')

# Last value in group
df['last_salary_dept'] = df.groupby('department')['salary'].transform('last')

# First/Last with ordering
df_sorted = df.sort_values(['department', 'salary'])
df_sorted['min_salary_dept'] = df_sorted.groupby('department')['salary'].transform('first')
df_sorted['max_salary_dept'] = df_sorted.groupby('department')['salary'].transform('last')
```

### NTH_VALUE()
```python
# Nth value in group (e.g., 2nd highest salary)
df_sorted = df.sort_values(['department', 'salary'], ascending=[True, False])
df_sorted['second_highest'] = df_sorted.groupby('department')['salary'].transform(lambda x: x.iloc[1] if len(x) > 1 else np.nan)

# Nth value with iloc
df_sorted['third_salary'] = df_sorted.groupby('department')['salary'].transform(lambda x: x.iloc[2] if len(x) > 2 else np.nan)
```

## Aggregate Window Functions

### Running Totals and Averages
```python
# Running sum (cumulative sum)
df_sorted = df.sort_values(['department', 'hire_date'])
df_sorted['running_total'] = df_sorted.groupby('department')['salary'].cumsum()

# Running average
df_sorted['running_avg'] = df_sorted.groupby('department')['salary'].expanding().mean().reset_index(drop=True)

# Running count
df_sorted['running_count'] = df_sorted.groupby('department').cumcount() + 1
```

### Moving Window Functions
```python
# Moving average (3-period)
df_sorted['moving_avg_3'] = df_sorted.groupby('department')['salary'].rolling(window=3, min_periods=1).mean().reset_index(drop=True)

# Moving sum
df_sorted['moving_sum_3'] = df_sorted.groupby('department')['salary'].rolling(window=3, min_periods=1).sum().reset_index(drop=True)

# Moving standard deviation
df_sorted['moving_std_3'] = df_sorted.groupby('department')['salary'].rolling(window=3, min_periods=1).std().reset_index(drop=True)
```

## Advanced Window Operations

### Custom Window Functions
```python
# Custom aggregation with transform
df['dept_salary_ratio'] = df['salary'] / df.groupby('department')['salary'].transform('mean')

# Multiple aggregations
df['salary_vs_dept'] = df.groupby('department')['salary'].transform(lambda x: (x - x.mean()) / x.std())

# Conditional window functions
df['above_dept_avg'] = df['salary'] > df.groupby('department')['salary'].transform('mean')
```

### Complex Partitioning
```python
# Multiple grouping columns
df['rank_by_dept_year'] = (df.assign(hire_year=df['hire_date'].dt.year)
                          .groupby(['department', 'hire_year'])['salary']
                          .rank(method='dense', ascending=False))
```

## SQL to Pandas Translation Examples

```sql
-- SQL: ROW_NUMBER() OVER (PARTITION BY department ORDER BY salary DESC)
```
```python
# Pandas equivalent:
df.sort_values(['department', 'salary'], ascending=[True, False]).groupby('department').cumcount() + 1
```

```sql
-- SQL: RANK() OVER (ORDER BY salary DESC)
```
```python
# Pandas equivalent:
df['salary'].rank(method='min', ascending=False)
```

```sql
-- SQL: NTILE(4) OVER (PARTITION BY department ORDER BY salary)
```
```python
# Pandas equivalent:
df.groupby('department')['salary'].apply(lambda x: pd.qcut(x.rank(method='first'), q=min(4, len(x)), labels=False) + 1)
```

```sql
-- SQL: LAG(salary, 1) OVER (PARTITION BY department ORDER BY hire_date)
```
```python
# Pandas equivalent:
df.sort_values(['department', 'hire_date']).groupby('department')['salary'].shift(1)
```

## Performance Tips

1. **Sort once**: Sort your DataFrame before applying multiple window functions
2. **Use transform()**: For group-wise operations that return the same shape
3. **Chain operations**: Combine multiple window functions in method chains
4. **Memory efficiency**: Use `rolling()` with appropriate window sizes for large datasets

## Common Gotchas

- **Index management**: Window functions can change DataFrame index; use `reset_index()` when needed
- **NaN handling**: LAG/LEAD operations introduce NaN values; use `fillna()` for defaults
- **Sorting**: Always sort data appropriately before applying ordered window functions
- **Group boundaries**: Window functions respect group boundaries defined by `groupby()`
