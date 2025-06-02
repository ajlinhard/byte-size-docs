I'll create a comprehensive cheatsheet and walkthrough for using `np.where` and `np.select` with pandas DataFrames.I've created a comprehensive cheatsheet and walkthrough for using `np.where` and `np.select` with pandas DataFrames. The guide covers:

**Key Highlights:**

- **np.where()** is perfect for binary conditions (if-else logic) and can be nested for multiple conditions
- **np.select()** shines when you have 3+ possible outcomes and complex multi-criteria logic
- **Performance**: `np.where` is generally faster for simple cases, while `np.select` is more readable and maintainable for complex scenarios

**The guide includes:**
- Syntax explanations and basic examples
- Real-world use cases like grading systems, business logic, and feature engineering
- Performance comparisons and best practices
- Quick reference table for choosing between the two methods

**Pro Tips from the guide:**
1. Use `np.where` for simple binary decisions
2. Use `np.select` when you have multiple conditions (like grade assignments A/B/C/D/F)
3. Always handle NaN values explicitly
4. Pre-compute complex conditions for better readability and potential performance gains

The examples progress from basic usage to complex real-world scenarios like risk assessment and customer categorization, making it practical for both beginners and advanced users.

---
## Python Code Examples:
```python
# NumPy where() and select() with Pandas DataFrames - Complete Guide

## Table of Contents
1. [np.where() Basics](#npwhere-basics)
2. [np.where() with Pandas](#npwhere-with-pandas)
3. [np.select() Basics](#npselect-basics)
4. [np.select() with Pandas](#npselect-with-pandas)
5. [Performance Comparison](#performance-comparison)
6. [Common Use Cases](#common-use-cases)
7. [Best Practices](#best-practices)

---

## np.where() Basics

### Syntax
```python
np.where(condition, x, y)
```
- **condition**: Boolean array or condition
- **x**: Values to use where condition is True
- **y**: Values to use where condition is False

### Simple Examples
```python
import numpy as np
import pandas as pd

# Basic usage
arr = np.array([1, 2, 3, 4, 5])
result = np.where(arr > 3, 'high', 'low')
# Result: ['low' 'low' 'low' 'high' 'high']

# With arrays
a = np.array([10, 20, 30])
b = np.array([1, 2, 3])
result = np.where(a > 15, a, b)
# Result: [1 20 30]
```

---

## np.where() with Pandas

### Basic DataFrame Operations
```python
# Sample DataFrame
df = pd.DataFrame({
    'score': [85, 92, 78, 96, 88],
    'age': [22, 25, 23, 24, 26],
    'department': ['A', 'B', 'A', 'C', 'B']
})

# Simple condition
df['grade'] = np.where(df['score'] >= 90, 'A', 'B')

# Multiple conditions with & and |
df['status'] = np.where((df['score'] >= 90) & (df['age'] < 25), 'Young High Performer', 'Other')

# Using string methods
df['dept_type'] = np.where(df['department'].str.contains('A'), 'Type A', 'Type Other')
```

### Nested np.where() for Multiple Conditions
```python
# Nested conditions (like if-elif-else)
df['performance'] = np.where(df['score'] >= 95, 'Excellent',
                    np.where(df['score'] >= 85, 'Good',
                    np.where(df['score'] >= 70, 'Average', 'Poor')))

# More complex nested example
df['category'] = np.where((df['score'] >= 90) & (df['age'] <= 24), 'Star',
                 np.where((df['score'] >= 85) & (df['age'] <= 26), 'Performer',
                 np.where(df['score'] >= 80, 'Average', 'Needs Improvement')))
```

### Working with Missing Values
```python
# Handle NaN values
df_with_nan = df.copy()
df_with_nan.loc[2, 'score'] = np.nan

# np.where with NaN handling
df_with_nan['grade_safe'] = np.where(df_with_nan['score'].isna(), 'Missing',
                           np.where(df_with_nan['score'] >= 90, 'A', 'B'))

# Using fillna() first
df_with_nan['grade_filled'] = np.where(df_with_nan['score'].fillna(0) >= 90, 'A', 'B')
```

---

## np.select() Basics

### Syntax
```python
np.select(condlist, choicelist, default=0)
```
- **condlist**: List of conditions
- **choicelist**: List of choices corresponding to conditions
- **default**: Value to use when no condition is met

### Simple Examples
```python
# Basic usage
scores = np.array([95, 87, 76, 92, 68])

conditions = [
    scores >= 90,
    scores >= 80,
    scores >= 70
]

choices = ['A', 'B', 'C']

grades = np.select(conditions, choices, default='F')
# Result: ['A' 'B' 'C' 'A' 'F']
```

---

## np.select() with Pandas

### Basic Usage
```python
# Sample DataFrame
df = pd.DataFrame({
    'score': [95, 87, 76, 92, 68, 83],
    'attendance': [0.95, 0.87, 0.92, 0.88, 0.75, 0.91],
    'participation': [8, 7, 6, 9, 5, 7]
})

# Grade assignment using np.select
conditions = [
    df['score'] >= 90,
    df['score'] >= 80,
    df['score'] >= 70,
    df['score'] >= 60
]

choices = ['A', 'B', 'C', 'D']

df['grade'] = np.select(conditions, choices, default='F')
```

### Complex Multi-Criteria Selection
```python
# Multi-criteria grading system
conditions = [
    (df['score'] >= 95) & (df['attendance'] >= 0.9) & (df['participation'] >= 8),
    (df['score'] >= 90) & (df['attendance'] >= 0.85),
    (df['score'] >= 85) & (df['attendance'] >= 0.8),
    (df['score'] >= 80) | ((df['score'] >= 75) & (df['participation'] >= 7)),
    df['score'] >= 70
]

choices = ['A+', 'A', 'B+', 'B', 'C']

df['final_grade'] = np.select(conditions, choices, default='F')
```

### String-based Conditions
```python
# Department and performance-based categories
df['department'] = ['Sales', 'Engineering', 'Marketing', 'Sales', 'HR', 'Engineering']

conditions = [
    (df['department'] == 'Sales') & (df['score'] >= 85),
    (df['department'] == 'Engineering') & (df['score'] >= 90),
    (df['department'] == 'Marketing') & (df['score'] >= 80),
    df['score'] >= 95  # Top performers regardless of department
]

choices = [
    'Sales Star',
    'Tech Lead',
    'Marketing Pro',
    'Company Champion'
]

df['recognition'] = np.select(conditions, choices, default='Standard')
```

---

## Performance Comparison

### Speed Test Example
```python
import time

# Large DataFrame for testing
large_df = pd.DataFrame({
    'score': np.random.randint(60, 100, 100000),
    'age': np.random.randint(20, 30, 100000)
})

# Method 1: Multiple np.where (nested)
start = time.time()
large_df['grade_where'] = np.where(large_df['score'] >= 95, 'A',
                          np.where(large_df['score'] >= 85, 'B',
                          np.where(large_df['score'] >= 75, 'C', 'D')))
time_where = time.time() - start

# Method 2: np.select
start = time.time()
conditions = [
    large_df['score'] >= 95,
    large_df['score'] >= 85,
    large_df['score'] >= 75
]
choices = ['A', 'B', 'C']
large_df['grade_select'] = np.select(conditions, choices, default='D')
time_select = time.time() - start

print(f"np.where time: {time_where:.4f} seconds")
print(f"np.select time: {time_select:.4f} seconds")
```

---

## Common Use Cases

### 1. Data Cleaning and Categorization
```python
# Outlier handling
df['score_cleaned'] = np.where((df['score'] < 0) | (df['score'] > 100), 
                               df['score'].median(), 
                               df['score'])

# Age group categorization
conditions = [
    df['age'] < 25,
    df['age'] < 35,
    df['age'] < 50
]
choices = ['Young', 'Middle', 'Mature']
df['age_group'] = np.select(conditions, choices, default='Senior')
```

### 2. Business Logic Implementation
```python
# Discount calculation
df['price'] = [100, 150, 200, 75, 300]
df['customer_type'] = ['regular', 'premium', 'regular', 'premium', 'vip']

conditions = [
    (df['customer_type'] == 'vip'),
    (df['customer_type'] == 'premium') & (df['price'] > 100),
    (df['customer_type'] == 'premium'),
    df['price'] > 200
]

choices = [0.20, 0.15, 0.10, 0.05]  # Discount percentages

df['discount'] = np.select(conditions, choices, default=0.0)
df['final_price'] = df['price'] * (1 - df['discount'])
```

### 3. Feature Engineering
```python
# Risk assessment
df['credit_score'] = [750, 680, 720, 650, 800]
df['income'] = [50000, 40000, 60000, 35000, 80000]
df['debt_ratio'] = [0.2, 0.4, 0.25, 0.5, 0.15]

conditions = [
    (df['credit_score'] >= 750) & (df['debt_ratio'] <= 0.2),
    (df['credit_score'] >= 700) & (df['debt_ratio'] <= 0.3),
    (df['credit_score'] >= 650) & (df['debt_ratio'] <= 0.4),
    df['credit_score'] >= 600
]

choices = ['Low Risk', 'Medium-Low Risk', 'Medium Risk', 'High Risk']

df['risk_category'] = np.select(conditions, choices, default='Very High Risk')
```

---

## Best Practices

### 1. Readability and Maintainability
```python
# Good: Clear variable names and structure
high_performer = (df['score'] >= 90) & (df['attendance'] >= 0.9)
good_performer = (df['score'] >= 80) & (df['attendance'] >= 0.8)
average_performer = df['score'] >= 70

conditions = [high_performer, good_performer, average_performer]
choices = ['Excellent', 'Good', 'Average']
df['performance'] = np.select(conditions, choices, default='Needs Improvement')

# Instead of hard-to-read nested np.where
```

### 2. Handle Edge Cases
```python
# Always consider NaN values and edge cases
df['safe_grade'] = np.select(
    [
        df['score'].isna(),
        df['score'] >= 90,
        df['score'] >= 80,
        df['score'] >= 70
    ],
    ['Incomplete', 'A', 'B', 'C'],
    default='F'
)
```

### 3. Use Appropriate Method
```python
# Use np.where for simple binary conditions
df['pass_fail'] = np.where(df['score'] >= 70, 'Pass', 'Fail')

# Use np.select for multiple conditions (3+ outcomes)
conditions = [df['score'] >= 90, df['score'] >= 80, df['score'] >= 70]
choices = ['A', 'B', 'C']
df['letter_grade'] = np.select(conditions, choices, default='F')

# Consider pandas methods for simple cases
df['grade_cut'] = pd.cut(df['score'], 
                        bins=[0, 70, 80, 90, 100], 
                        labels=['F', 'C', 'B', 'A'],
                        include_lowest=True)
```

### 4. Performance Tips
```python
# Pre-compute conditions for reuse
high_score = df['score'] >= 90
good_attendance = df['attendance'] >= 0.85

# Use vectorized operations
df['bonus_eligible'] = np.where(high_score & good_attendance, True, False)
df['recognition_level'] = np.select([high_score & good_attendance, high_score], 
                                   ['Gold', 'Silver'], 
                                   default='Bronze')
```

---

## Quick Reference

| Operation | np.where | np.select |
|-----------|----------|-----------|
| **Best for** | Binary conditions (2 outcomes) | Multiple conditions (3+ outcomes) |
| **Syntax** | `np.where(condition, if_true, if_false)` | `np.select(conditions_list, choices_list, default)` |
| **Nesting** | Can be nested but gets complex | Clean for multiple conditions |
| **Performance** | Faster for simple cases | Better for complex multi-condition logic |
| **Readability** | Good for 2-3 conditions | Excellent for 4+ conditions |

### Common Patterns
```python
# Binary classification
df['category'] = np.where(df['value'] > threshold, 'High', 'Low')

# Multi-class classification
conditions = [df['value'] > high_thresh, df['value'] > med_thresh]
choices = ['High', 'Medium']
df['category'] = np.select(conditions, choices, default='Low')

# Complex business rules with multiple criteria
conditions = [
    (df['A'] > x) & (df['B'] < y),
    (df['A'] > z) | (df['C'] == 'special'),
    df['D'].isin(['cat1', 'cat2'])
]
choices = ['Rule1', 'Rule2', 'Rule3']
df['result'] = np.select(conditions, choices, default='Default')
```
```
