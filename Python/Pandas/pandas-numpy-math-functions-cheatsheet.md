# Pandas & NumPy Math Functions Cheatsheet
Here is info for pandas DataFrames and NumPy arrays with the same format - quick reference tables followed by detailed code examples.I've created a comprehensive pandas and NumPy math functions cheatsheet following the same format as the Python math cheatsheet. It includes:

**Quick Reference Tables** covering:
- NumPy array operations (basic and advanced functions)
- Pandas DataFrame operations (aggregations and groupby functions)

**Detailed Code Examples** organized into sections:
- Basic NumPy array mathematics (statistics, element-wise operations, trigonometry)
- Advanced NumPy operations (cumulative functions, correlations, boolean operations)
- Pandas DataFrame mathematics (basic stats, describe(), column operations)
- Advanced Pandas operations (groupby, rolling windows, correlations)
- Element-wise operations and broadcasting
- Time series and financial calculations
- Statistical analysis and comparisons
- Performance tips and best practices

The cheatsheet covers both libraries comprehensively, showing how to perform mathematical operations on arrays and DataFrames, including practical examples like financial calculations, moving averages, and statistical analysis. It also includes performance tips to help you write efficient code.

This should serve as a complete reference for mathematical operations in both NumPy and pandas!

## Quick Reference Table - NumPy Arrays

| Function | Purpose | Example | Result |
|----------|---------|---------|---------|
| `np.sum(arr)` | Sum of elements | `np.sum([1, 2, 3])` | `6` |
| `np.mean(arr)` | Average | `np.mean([1, 2, 3])` | `2.0` |
| `np.median(arr)` | Median value | `np.median([1, 2, 3])` | `2.0` |
| `np.std(arr)` | Standard deviation | `np.std([1, 2, 3])` | `0.816...` |
| `np.min(arr)` | Minimum value | `np.min([1, 2, 3])` | `1` |
| `np.max(arr)` | Maximum value | `np.max([1, 2, 3])` | `3` |
| `np.sqrt(arr)` | Square root | `np.sqrt([4, 9, 16])` | `[2, 3, 4]` |
| `np.abs(arr)` | Absolute value | `np.abs([-1, 2, -3])` | `[1, 2, 3]` |
| `np.round(arr, n)` | Round to n decimals | `np.round([1.23, 2.67], 1)` | `[1.2, 2.7]` |
| `np.log(arr)` | Natural logarithm | `np.log([1, np.e])` | `[0, 1]` |

### NumPy Trigonometric & Advanced Functions

| Function | Purpose | Example | Result |
|----------|---------|---------|---------|
| `np.sin(arr)` | Sine | `np.sin([0, np.pi/2])` | `[0, 1]` |
| `np.cos(arr)` | Cosine | `np.cos([0, np.pi])` | `[1, -1]` |
| `np.exp(arr)` | Exponential (e^x) | `np.exp([0, 1])` | `[1, 2.718...]` |
| `np.power(arr, n)` | Power | `np.power([2, 3], 2)` | `[4, 9]` |
| `np.cumsum(arr)` | Cumulative sum | `np.cumsum([1, 2, 3])` | `[1, 3, 6]` |
| `np.diff(arr)` | Differences | `np.diff([1, 3, 6])` | `[2, 3]` |
| `np.percentile(arr, q)` | Percentile | `np.percentile([1,2,3,4], 50)` | `2.5` |
| `np.corrcoef(x, y)` | Correlation | `np.corrcoef([1,2], [2,4])` | `[[1, 1], [1, 1]]` |

## Quick Reference Table - Pandas DataFrames

| Function | Purpose | Example | Result |
|----------|---------|---------|---------|
| `df.sum()` | Sum by column | `df.sum()` | Series of sums |
| `df.mean()` | Average by column | `df.mean()` | Series of means |
| `df.median()` | Median by column | `df.median()` | Series of medians |
| `df.std()` | Standard deviation | `df.std()` | Series of std devs |
| `df.min()` | Minimum by column | `df.min()` | Series of minimums |
| `df.max()` | Maximum by column | `df.max()` | Series of maximums |
| `df.count()` | Non-null count | `df.count()` | Series of counts |
| `df.describe()` | Summary statistics | `df.describe()` | Statistical summary |
| `df.corr()` | Correlation matrix | `df.corr()` | Correlation DataFrame |
| `df.cumsum()` | Cumulative sum | `df.cumsum()` | DataFrame with cum sums |

### Pandas Groupby & Advanced Operations

| Function | Purpose | Example | Result |
|----------|---------|---------|---------|
| `df.groupby('col').sum()` | Group and sum | `df.groupby('category').sum()` | Grouped sums |
| `df.groupby('col').agg()` | Multiple aggregations | `df.groupby('cat').agg(['mean', 'std'])` | Multi-stat summary |
| `df.rolling(n).mean()` | Rolling average | `df.rolling(3).mean()` | Moving averages |
| `df.pct_change()` | Percent change | `df.pct_change()` | Period-over-period change |
| `df.rank()` | Rank values | `df.rank()` | Rankings by column |
| `df.quantile(q)` | Quantiles | `df.quantile(0.5)` | 50th percentile |

## Code Examples

### NumPy Array Mathematics

```python
import numpy as np

# Create sample arrays
arr1 = np.array([1, 2, 3, 4, 5])
arr2 = np.array([10, 20, 30, 40, 50])
matrix = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])

# Basic statistics
print("Array:", arr1)
print(f"Sum: {np.sum(arr1)}")           # 15
print(f"Mean: {np.mean(arr1)}")         # 3.0
print(f"Median: {np.median(arr1)}")     # 3.0
print(f"Std Dev: {np.std(arr1)}")       # 1.4142135623730951
print(f"Variance: {np.var(arr1)}")      # 2.0
print(f"Min: {np.min(arr1)}")           # 1
print(f"Max: {np.max(arr1)}")           # 5

# Element-wise operations
print("\nElement-wise operations:")
print(f"Square root: {np.sqrt(arr1)}")                    # [1. 1.414... 1.732... 2. 2.236...]
print(f"Absolute: {np.abs([-1, -2, 3, -4])}")           # [1 2 3 4]
print(f"Power of 2: {np.power(arr1, 2)}")               # [1 4 9 16 25]
print(f"Exponential: {np.exp([0, 1, 2])}")              # [1. 2.718... 7.389...]
print(f"Natural log: {np.log([1, np.e, np.e**2])}")     # [0. 1. 2.]

# Trigonometric functions
angles = np.array([0, np.pi/4, np.pi/2, np.pi])
print(f"\nAngles: {angles}")
print(f"Sine: {np.sin(angles)}")        # [0. 0.707... 1. 0.]
print(f"Cosine: {np.cos(angles)}")      # [1. 0.707... 0. -1.]
print(f"Tangent: {np.tan(angles[:3])}")  # [0. 1. inf] (excluding π to avoid division issues)

# Array operations with axis
print(f"\nMatrix:\n{matrix}")
print(f"Sum all: {np.sum(matrix)}")                    # 45
print(f"Sum by rows: {np.sum(matrix, axis=1)}")       # [6 15 24]
print(f"Sum by columns: {np.sum(matrix, axis=0)}")    # [12 15 18]
print(f"Mean by rows: {np.mean(matrix, axis=1)}")     # [2. 5. 8.]
```

### Advanced NumPy Operations

```python
# Cumulative operations
data = np.array([1, 3, 2, 8, 5])
print(f"Data: {data}")
print(f"Cumulative sum: {np.cumsum(data)}")           # [1 4 6 14 19]
print(f"Cumulative product: {np.cumprod(data)}")      # [1 3 6 48 240]
print(f"Differences: {np.diff(data)}")                # [2 -1 6 -3]

# Statistical functions
print(f"\nPercentiles:")
print(f"25th percentile: {np.percentile(data, 25)}")   # 2.0
print(f"50th percentile: {np.percentile(data, 50)}")   # 3.0
print(f"75th percentile: {np.percentile(data, 75)}")   # 5.0

# Correlation and covariance
x = np.array([1, 2, 3, 4, 5])
y = np.array([2, 4, 6, 8, 10])
print(f"\nCorrelation coefficient: {np.corrcoef(x, y)[0, 1]}")  # 1.0 (perfect correlation)
print(f"Covariance: {np.cov(x, y)[0, 1]}")                     # 5.0

# Sorting and searching
unsorted = np.array([3, 1, 4, 1, 5, 9, 2, 6])
print(f"\nUnsorted: {unsorted}")
print(f"Sorted: {np.sort(unsorted)}")                          # [1 1 2 3 4 5 6 9]
print(f"Argsort (indices): {np.argsort(unsorted)}")            # [1 3 6 0 2 4 7 5]
print(f"Unique values: {np.unique(unsorted)}")                 # [1 2 3 4 5 6 9]

# Boolean operations
print(f"Values > 3: {unsorted[unsorted > 3]}")                 # [4 5 9 6]
print(f"Count > 3: {np.sum(unsorted > 3)}")                    # 4
print(f"Any > 8: {np.any(unsorted > 8)}")                      # True
print(f"All > 0: {np.all(unsorted > 0)}")                      # True
```

### Pandas DataFrame Mathematics

```python
import pandas as pd
import numpy as np

# Create sample DataFrame
data = {
    'A': [1, 2, 3, 4, 5],
    'B': [10, 20, 30, 40, 50],
    'C': [100, 200, 300, 400, 500],
    'Category': ['X', 'Y', 'X', 'Y', 'X']
}
df = pd.DataFrame(data)
print("DataFrame:")
print(df)

# Basic statistics
print(f"\nBasic Statistics:")
print(f"Sum by column:\n{df.sum()}")
print(f"\nMean by column:\n{df.mean()}")
print(f"\nMedian by column:\n{df.median()}")
print(f"\nStandard deviation:\n{df.std()}")
print(f"\nMin/Max:")
print(f"Min:\n{df.min()}")
print(f"Max:\n{df.max()}")

# Comprehensive statistics
print(f"\nDescriptive Statistics:")
print(df.describe())

# Column-specific operations
print(f"\nColumn A statistics:")
print(f"Sum: {df['A'].sum()}")                    # 15
print(f"Mean: {df['A'].mean()}")                  # 3.0
print(f"Std: {df['A'].std()}")                    # 1.58...
print(f"Quantiles:\n{df['A'].quantile([0.25, 0.5, 0.75])}")
```

### Advanced Pandas Operations

```python
# Correlation matrix
print("Correlation Matrix:")
correlation_matrix = df[['A', 'B', 'C']].corr()
print(correlation_matrix)

# Cumulative operations
print(f"\nCumulative Operations:")
print("Cumulative sum:")
print(df[['A', 'B', 'C']].cumsum())
print("\nCumulative max:")
print(df[['A', 'B', 'C']].cummax())

# Percent change
print(f"\nPercent Change:")
print(df[['A', 'B', 'C']].pct_change())

# Rolling statistics (moving averages)
print(f"\nRolling 3-period mean:")
print(df[['A', 'B', 'C']].rolling(window=3).mean())

# Ranking
print(f"\nRankings:")
print(df[['A', 'B', 'C']].rank())

# GroupBy operations
print(f"\nGroupBy Operations:")
grouped = df.groupby('Category')[['A', 'B', 'C']].agg(['mean', 'sum', 'std'])
print(grouped)

# Custom aggregations
print(f"\nCustom Aggregations:")
custom_agg = df.groupby('Category').agg({
    'A': ['mean', 'sum'],
    'B': ['min', 'max'],
    'C': ['std', 'count']
})
print(custom_agg)
```

### Element-wise Operations and Broadcasting

```python
# Element-wise operations on DataFrame
df_numeric = df[['A', 'B', 'C']]

print("Original DataFrame:")
print(df_numeric)

# Mathematical operations
print(f"\nSquare root:")
print(np.sqrt(df_numeric))

print(f"\nSquare:")
print(df_numeric ** 2)

print(f"\nLogarithm (base 10):")
print(np.log10(df_numeric))

print(f"\nAbsolute value (after making some negative):")
df_with_negatives = df_numeric.copy()
df_with_negatives.loc[1, 'A'] = -2
print(df_with_negatives.abs())

# Broadcasting operations
print(f"\nBroadcasting - Add 10 to all values:")
print(df_numeric + 10)

print(f"\nBroadcasting - Multiply each column by different value:")
multipliers = pd.Series([2, 3, 4], index=['A', 'B', 'C'])
print(df_numeric * multipliers)

# Conditional operations
print(f"\nConditional operations:")
print("Values where A > 2:")
print(df_numeric.where(df_numeric['A'] > 2))

print(f"\nReplace values where A <= 2 with 999:")
print(df_numeric.where(df_numeric['A'] > 2, 999))
```

### Time Series and Financial Calculations

```python
# Create time series data
dates = pd.date_range('2024-01-01', periods=10, freq='D')
ts_data = pd.DataFrame({
    'price': [100, 102, 98, 105, 103, 107, 104, 108, 106, 110],
    'volume': [1000, 1200, 800, 1500, 1100, 1300, 900, 1400, 1000, 1600]
}, index=dates)

print("Time Series Data:")
print(ts_data)

# Financial calculations
print(f"\nFinancial Calculations:")
# Daily returns
ts_data['daily_return'] = ts_data['price'].pct_change()
print("Daily returns:")
print(ts_data['daily_return'])

# Moving averages
ts_data['ma_3'] = ts_data['price'].rolling(window=3).mean()
ts_data['ma_5'] = ts_data['price'].rolling(window=5).mean()
print(f"\nWith moving averages:")
print(ts_data[['price', 'ma_3', 'ma_5']])

# Volatility (rolling standard deviation)
ts_data['volatility'] = ts_data['daily_return'].rolling(window=5).std()
print(f"\nVolatility (5-day rolling std of returns):")
print(ts_data['volatility'])

# Cumulative returns
ts_data['cumulative_return'] = (1 + ts_data['daily_return']).cumprod() - 1
print(f"\nCumulative returns:")
print(ts_data['cumulative_return'])
```

### Statistical Analysis and Comparison

```python
# Create sample datasets for comparison
np.random.seed(42)
df_stats = pd.DataFrame({
    'Group_A': np.random.normal(50, 10, 100),
    'Group_B': np.random.normal(55, 12, 100),
    'Group_C': np.random.normal(48, 8, 100)
})

print("Statistical Analysis:")
print(f"Basic stats:\n{df_stats.describe()}")

# Advanced statistical measures
print(f"\nSkewness:")
print(df_stats.skew())

print(f"\nKurtosis:")
print(df_stats.kurtosis())

# Correlation analysis
print(f"\nCorrelation Matrix:")
print(df_stats.corr())

# Pairwise correlations
print(f"\nPairwise correlations:")
for col1 in df_stats.columns:
    for col2 in df_stats.columns:
        if col1 < col2:  # Avoid duplicates
            corr = df_stats[col1].corr(df_stats[col2])
            print(f"{col1} vs {col2}: {corr:.4f}")

# Percentile calculations
print(f"\nPercentiles:")
percentiles = [10, 25, 50, 75, 90, 95, 99]
print(df_stats.quantile([p/100 for p in percentiles]))

# Z-scores (standardization)
print(f"\nZ-scores (first 5 rows):")
z_scores = (df_stats - df_stats.mean()) / df_stats.std()
print(z_scores.head())
```

## Performance Tips and Best Practices

### NumPy Performance

```python
# Vectorized operations are much faster than loops
# Good - vectorized
large_array = np.random.randn(1000000)
result = np.sqrt(large_array)  # Fast

# Avoid - Python loop
# result = [math.sqrt(x) for x in large_array]  # Slow

# Use appropriate data types
int_array = np.array([1, 2, 3], dtype=np.int32)     # Uses less memory
float_array = np.array([1, 2, 3], dtype=np.float64) # Higher precision

# Use views instead of copies when possible
subset = large_array[100:200]  # View (fast, shares memory)
copy_subset = large_array[100:200].copy()  # Copy (slower, new memory)
```

### Pandas Performance

```python
# Use vectorized operations instead of apply when possible
# Good
df['new_col'] = df['A'] * df['B']

# Less efficient
# df['new_col'] = df.apply(lambda row: row['A'] * row['B'], axis=1)

# Use categorical data for repeated string values
df['Category'] = df['Category'].astype('category')  # More memory efficient

# Use appropriate aggregation methods
# For multiple statistics on same groupby
grouped_stats = df.groupby('Category').agg({
    'A': ['mean', 'std', 'count'],
    'B': ['sum', 'min', 'max']
})

# Chain operations efficiently
result = (df
    .groupby('Category')
    .agg({'A': 'mean', 'B': 'sum'})
    .round(2)
    .sort_values('A', ascending=False)
)
```

## Key Differences Summary

- **NumPy**: Better for numerical computations, homogeneous data, linear algebra
- **Pandas**: Better for data analysis, heterogeneous data, data manipulation
- **Memory**: NumPy arrays are more memory efficient
- **Functionality**: Pandas has more built-in data analysis tools
- **Performance**: NumPy is faster for pure mathematical operations
- **Indexing**: Pandas has more sophisticated indexing and selection capabilities
