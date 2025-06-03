Here is a comprehensive pandas cheatsheet that covers joins and unions from basic to advanced scenarios. The cheatsheet is organized progressively:

**Basic Level:**
- Simple inner/left/right/outer joins
- Basic concatenation operations

**Intermediate Level:**
- Joining on different column names
- Multi-column joins
- Index-based operations
- Handling duplicate columns

**Advanced Level:**
- Cross joins and cartesian products
- Fuzzy/approximate joins with merge_asof
- Conditional joins
- Performance optimization techniques

**Practical Sections:**
- Common patterns and solutions
- Anti-joins for finding non-matches
- Handling multiple DataFrames
- Quick reference table

The cheatsheet includes working code examples with sample data, performance tips, and common gotchas to watch out for. Each section builds upon the previous one, making it easy to learn progressively or use as a quick reference guide.
---
# Pandas Joins and Unions Cheatsheet

## Sample DataFrames for Examples

```python
import pandas as pd

# Create sample dataframes
df1 = pd.DataFrame({
    'id': [1, 2, 3, 4],
    'name': ['Alice', 'Bob', 'Charlie', 'David'],
    'age': [25, 30, 35, 40]
})

df2 = pd.DataFrame({
    'id': [3, 4, 5, 6],
    'salary': [50000, 60000, 70000, 80000],
    'department': ['HR', 'IT', 'Finance', 'Marketing']
})

df3 = pd.DataFrame({
    'employee_id': [1, 2, 7, 8],
    'project': ['Project A', 'Project B', 'Project C', 'Project D']
})
```

## 1. Basic Joins (merge)

### Inner Join (Default)
```python
# Keep only rows where keys exist in both DataFrames
result = pd.merge(df1, df2, on='id')
# or
result = df1.merge(df2, on='id')
```

### Left Join
```python
# Keep all rows from left DataFrame
result = pd.merge(df1, df2, on='id', how='left')
```

### Right Join
```python
# Keep all rows from right DataFrame
result = pd.merge(df1, df2, on='id', how='right')
```

### Outer Join (Full Join)
```python
# Keep all rows from both DataFrames
result = pd.merge(df1, df2, on='id', how='outer')
```

## 2. Joining on Different Column Names

```python
# When key columns have different names
result = pd.merge(df1, df3, left_on='id', right_on='employee_id')

# Drop redundant column after merge
result = result.drop('employee_id', axis=1)
```

## 3. Joining on Multiple Columns

```python
# Create sample data with multiple keys
df_multi1 = pd.DataFrame({
    'dept': ['A', 'A', 'B', 'B'],
    'year': [2023, 2024, 2023, 2024],
    'revenue': [100, 110, 200, 220]
})

df_multi2 = pd.DataFrame({
    'dept': ['A', 'A', 'B', 'C'],
    'year': [2023, 2024, 2023, 2023],
    'expenses': [80, 85, 150, 90]
})

# Join on multiple columns
result = pd.merge(df_multi1, df_multi2, on=['dept', 'year'])
```

## 4. Index-based Joins

```python
# Set index before joining
df1_indexed = df1.set_index('id')
df2_indexed = df2.set_index('id')

# Join on index
result = df1_indexed.join(df2_indexed, how='inner')
# or
result = pd.merge(df1_indexed, df2_indexed, left_index=True, right_index=True)
```

## 5. Handling Duplicate Column Names

```python
# When both DataFrames have columns with same names
df_dup1 = pd.DataFrame({'id': [1, 2], 'value': [10, 20]})
df_dup2 = pd.DataFrame({'id': [1, 2], 'value': [100, 200]})

# Add suffixes to distinguish columns
result = pd.merge(df_dup1, df_dup2, on='id', suffixes=('_left', '_right'))
```

## 6. Unions (Concatenation)

### Simple Vertical Union (Row-wise)
```python
# Stack DataFrames vertically
df_union = pd.concat([df1, df1], ignore_index=True)
```

### Horizontal Union (Column-wise)
```python
# Combine DataFrames side by side
df_horizontal = pd.concat([df1, df2], axis=1)
```

### Union with Keys/Labels
```python
# Add labels to identify source DataFrames
df_labeled = pd.concat([df1, df2], keys=['table1', 'table2'])
```

## 7. Advanced Scenarios

### Cross Join (Cartesian Product)
```python
# Create all possible combinations
df_small1 = pd.DataFrame({'A': [1, 2]})
df_small2 = pd.DataFrame({'B': ['X', 'Y']})

# Method 1: Using merge with dummy key
df_small1['key'] = 1
df_small2['key'] = 1
cross_join = pd.merge(df_small1, df_small2, on='key').drop('key', axis=1)

# Method 2: Using cross merge (pandas 1.2+)
cross_join = df_small1.merge(df_small2, how='cross')
```

### Merge with Validation
```python
# Ensure merge keys are unique
try:
    result = pd.merge(df1, df2, on='id', validate='one_to_one')
except pd.errors.MergeError as e:
    print(f"Merge validation failed: {e}")
```

### Merge with Indicator
```python
# Add column showing merge source
result = pd.merge(df1, df2, on='id', how='outer', indicator=True)
print(result['_merge'].value_counts())
```

### Fuzzy/Approximate Joins
```python
# For approximate matching (requires additional setup)
# Using merge_asof for time-series like data
dates1 = pd.DataFrame({
    'date': pd.to_datetime(['2023-01-01', '2023-01-03', '2023-01-05']),
    'value1': [1, 2, 3]
})

dates2 = pd.DataFrame({
    'date': pd.to_datetime(['2023-01-02', '2023-01-04', '2023-01-06']),
    'value2': [10, 20, 30]
})

# Backward search (find nearest earlier date)
result = pd.merge_asof(dates1, dates2, on='date', direction='backward')
```

### Conditional Joins
```python
# Join with conditions beyond equality
# This requires more complex operations
df_cond1 = pd.DataFrame({'id': [1, 2, 3], 'min_val': [10, 20, 30]})
df_cond2 = pd.DataFrame({'id': [1, 2, 3], 'actual_val': [15, 18, 35]})

# Create all combinations then filter
merged = df_cond1.merge(df_cond2, on='id')
result = merged[merged['actual_val'] >= merged['min_val']]
```

## 8. Performance Tips

### Use Categories for Repeated String Values
```python
# Convert to category for memory efficiency
df1['name'] = df1['name'].astype('category')
df2['department'] = df2['department'].astype('category')
```

### Sort Before Merge for Large DataFrames
```python
# Sort both DataFrames by merge key for better performance
df1_sorted = df1.sort_values('id')
df2_sorted = df2.sort_values('id')
result = pd.merge(df1_sorted, df2_sorted, on='id')
```

### Use Index Joins When Possible
```python
# Index-based joins are generally faster
df1_idx = df1.set_index('id')
df2_idx = df2.set_index('id')
result = df1_idx.join(df2_idx)
```

## 9. Common Patterns and Solutions

### Remove Duplicates After Union
```python
# Union and remove duplicates
df_combined = pd.concat([df1, df2]).drop_duplicates().reset_index(drop=True)
```

### Merge Multiple DataFrames
```python
# Chain multiple merges
from functools import reduce

dfs = [df1, df2, df3]
result = reduce(lambda left, right: pd.merge(left, right, 
                left_on='id', right_on='employee_id' if 'employee_id' in right.columns else 'id'), 
                dfs)
```

### Handle Missing Values After Merge
```python
# Fill NaN values after outer join
result = pd.merge(df1, df2, on='id', how='outer')
result = result.fillna({'age': 0, 'salary': 0})
```

### Anti-Join (Find Non-Matching Records)
```python
# Find records in df1 that don't have matches in df2
anti_join = df1[~df1['id'].isin(df2['id'])]

# Or using merge with indicator
merged = pd.merge(df1, df2, on='id', how='left', indicator=True)
anti_join = merged[merged['_merge'] == 'left_only'].drop('_merge', axis=1)
```

## 10. Quick Reference Table

| Operation | Syntax | Use Case |
|-----------|--------|----------|
| Inner Join | `pd.merge(df1, df2, on='key')` | Keep only matching rows |
| Left Join | `pd.merge(df1, df2, on='key', how='left')` | Keep all left rows |
| Right Join | `pd.merge(df1, df2, on='key', how='right')` | Keep all right rows |
| Outer Join | `pd.merge(df1, df2, on='key', how='outer')` | Keep all rows |
| Vertical Union | `pd.concat([df1, df2])` | Stack DataFrames |
| Horizontal Union | `pd.concat([df1, df2], axis=1)` | Side-by-side combination |
| Index Join | `df1.join(df2)` | Join on index |
| Cross Join | `df1.merge(df2, how='cross')` | Cartesian product |

## Common Gotchas

1. **Column name conflicts**: Use `suffixes` parameter
2. **Index reset**: Use `ignore_index=True` in concat
3. **Memory usage**: Consider data types and chunking for large datasets
4. **Key validation**: Use `validate` parameter to catch data quality issues
5. **Sort order**: Joins don't preserve original order unless specified
