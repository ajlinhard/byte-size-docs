# NumPy with DataFrames: Detailed Cheatsheet

## Table of Contents
1. [Introduction](#introduction)
2. [Basic Conversions](#basic-conversions)
3. [DataFrame Aggregations with NumPy](#dataframe-aggregations-with-numpy)
4. [Conditional Operations](#conditional-operations)
5. [Mapping Values](#mapping-values)
6. [Array Transformations](#array-transformations)
7. [Performance Optimization](#performance-optimization)
8. [Time Series Operations](#time-series-operations)
9. [Advanced Data Manipulation](#advanced-data-manipulation)
10. [Integration with PySpark DataFrames](#integration-with-pyspark-dataframes)

## Introduction

This cheatsheet focuses on using NumPy with pandas and PySpark DataFrames for data manipulation, transformation, and analysis.

```python
import numpy as np
import pandas as pd
```

## Basic Conversions

### NumPy to Pandas

```python
# 1D array to Series
arr_1d = np.array([1, 2, 3, 4, 5])
series = pd.Series(arr_1d)

# 2D array to DataFrame
arr_2d = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
df = pd.DataFrame(arr_2d, columns=['A', 'B', 'C'])

# With custom index
df_indexed = pd.DataFrame(
    arr_2d,
    columns=['A', 'B', 'C'],
    index=['row1', 'row2', 'row3']
)

# With datetime index
dates = pd.date_range('2023-01-01', periods=3)
df_dates = pd.DataFrame(arr_2d, columns=['A', 'B', 'C'], index=dates)

# From structured array
structured_arr = np.array([
    ('Alice', 25, 55.0),
    ('Bob', 30, 70.5),
    ('Charlie', 35, 85.2)
], dtype=[('name', 'U10'), ('age', 'i4'), ('weight', 'f4')])

df_structured = pd.DataFrame(structured_arr)
```

### Pandas to NumPy

```python
# Series to NumPy array
series = pd.Series([1, 2, 3, 4, 5])
arr_from_series = series.to_numpy()

# DataFrame to NumPy array
df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6], 'C': [7, 8, 9]})
arr_from_df = df.to_numpy()

# Convert specific columns
arr_specific = df[['A', 'B']].to_numpy()

# Convert to structured array
structured_arr = df.to_records(index=False)

# Handle mixed data types
df_mixed = pd.DataFrame({
    'A': [1, 2, 3],
    'B': ['a', 'b', 'c'],
    'C': [True, False, True]
})
arr_mixed = df_mixed.to_numpy()  # Creates an array of Python objects
```

## DataFrame Aggregations with NumPy

### Basic Aggregations

```python
df = pd.DataFrame(np.random.randn(1000, 5), columns=list('ABCDE'))

# Apply NumPy functions directly to DataFrames
mean_vals = np.mean(df)
median_vals = np.median(df)
std_vals = np.std(df)
var_vals = np.var(df)
min_vals = np.min(df)
max_vals = np.max(df)
sum_vals = np.sum(df)
prod_vals = np.prod(df)

# Aggregations along axis
row_means = np.mean(df, axis=1)
col_means = np.mean(df, axis=0)

# Multiple aggregations at once
stats_dict = {
    'mean': np.mean(df),
    'median': np.median(df),
    'std': np.std(df),
    'min': np.min(df),
    'max': np.max(df)
}
stats_df = pd.DataFrame(stats_dict)

# Using numpy with pandas agg
agg_df = df.agg([
    ('mean', np.mean),
    ('median', np.median),
    ('std', np.std),
    ('min', np.min),
    ('max', np.max)
])
```

### Custom Aggregations

```python
# Geometric mean using NumPy
def geometric_mean(x):
    return np.exp(np.mean(np.log(np.abs(x) + 1e-10)))

df.agg(geometric_mean)

# Trimmed mean
def trimmed_mean(x, prop=0.1):
    return np.mean(np.sort(x)[int(len(x)*prop):int(len(x)*(1-prop))])

df.agg(lambda x: trimmed_mean(x, 0.1))

# Harmonic mean
def harmonic_mean(x):
    return 1 / np.mean(1 / (np.abs(x) + 1e-10))

df.agg(harmonic_mean)

# Coefficient of variation
def coef_variation(x):
    return np.std(x) / np.mean(np.abs(x))

df.agg(coef_variation)

# Winsorize function (capping outliers)
def winsorize(x, limits=(0.05, 0.05)):
    lower_limit = np.percentile(x, limits[0] * 100)
    upper_limit = np.percentile(x, 100 - limits[1] * 100)
    return np.clip(x, lower_limit, upper_limit)

df.apply(lambda x: winsorize(x))
```

### Groupby Aggregations

```python
# Create a DataFrame with groups
df = pd.DataFrame({
    'group': ['A', 'A', 'B', 'B', 'C', 'C', 'C'],
    'value1': np.random.randn(7),
    'value2': np.random.randn(7)
})

# Basic groupby with NumPy functions
grouped_mean = df.groupby('group').agg(np.mean)
grouped_median = df.groupby('group').agg(np.median)

# Multiple aggregations with different functions for different columns
grouped_multi = df.groupby('group').agg({
    'value1': [np.mean, np.std, np.min, np.max],
    'value2': [np.sum, np.median]
})

# Custom aggregation functions
def range_stat(x):
    return np.max(x) - np.min(x)

def iqr_stat(x):
    return np.percentile(x, 75) - np.percentile(x, 25)

grouped_custom = df.groupby('group').agg({
    'value1': [np.mean, range_stat],
    'value2': [np.mean, iqr_stat]
})

# Calculate multiple statistics at once for all columns
def multi_stats(x):
    return pd.Series({
        'mean': np.mean(x),
        'median': np.median(x),
        'std': np.std(x),
        'iqr': np.percentile(x, 75) - np.percentile(x, 25),
        'skew': (np.mean(x) - np.median(x)) / (np.std(x) + 1e-10)
    })

df.groupby('group').apply(lambda x: x[['value1', 'value2']].apply(multi_stats))
```

### Rolling Window Aggregations

```python
# Create a time series DataFrame
dates = pd.date_range('2023-01-01', periods=100)
df = pd.DataFrame({
    'A': np.random.randn(100),
    'B': np.random.randn(100)
}, index=dates)

# Rolling window statistical functions
rolling_mean = df.rolling(window=7).apply(np.mean)
rolling_std = df.rolling(window=7).apply(np.std)

# Custom rolling window functions
def rolling_zscore(x):
    """Calculate z-score within rolling window"""
    return (x[-1] - np.mean(x)) / (np.std(x) + 1e-10)

df.rolling(window=20).apply(rolling_zscore)

# Exponentially weighted moving covariance
def ewm_cov(x):
    """Calculate exponentially weighted moving covariance between columns"""
    return np.cov(x[:, 0], x[:, 1], ddof=0)

# Apply to a rolling window of arrays
df.rolling(window=30).apply(
    lambda x: ewm_cov(x),
    raw=True  # Passes a NumPy array instead of a Series
)
```

## Conditional Operations

### Basic Conditions

```python
df = pd.DataFrame({
    'A': np.random.rand(10),
    'B': np.random.rand(10),
    'C': np.random.rand(10)
})

# Create boolean masks
mask1 = df['A'] > 0.5
mask2 = df['B'] > 0.5

# Combine masks with NumPy logic functions
combined_mask_and = np.logical_and(mask1, mask2)
combined_mask_or = np.logical_or(mask1, mask2)
combined_mask_not = np.logical_not(mask1)
combined_mask_xor = np.logical_xor(mask1, mask2)

# Apply masks to filter DataFrames
filtered_df = df[combined_mask_and]

# Count values matching condition
count_matching = np.sum(combined_mask_and)

# Check if any/all values match condition
any_match = np.any(mask1)
all_match = np.all(mask1)

# Find indices where condition is True
indices = np.where(mask1)[0]

# Apply different operations based on conditions
df['D'] = np.where(mask1, df['A'] * 2, df['A'] / 2)
```

### Advanced Conditions with Multiple Clauses

```python
# Create a DataFrame with different data types
df = pd.DataFrame({
    'A': np.random.rand(10),
    'B': np.random.randint(0, 100, 10),
    'C': np.random.choice(['X', 'Y', 'Z'], 10)
})

# Complex conditions with multiple clauses
condition1 = (df['A'] > 0.5) & (df['B'] < 50)
condition2 = (df['A'] <= 0.5) & (df['B'] >= 50)
condition3 = (df['C'] == 'X')

# Use NumPy's select for multiple conditions (like a switch statement)
df['D'] = np.select(
    [condition1, condition2, condition3],
    [1, 2, 3],
    default=0
)

# Using NumPy's piecewise function for numerical conditions
df['E'] = np.piecewise(
    df['A'].values,
    [df['A'] < 0.3, (df['A'] >= 0.3) & (df['A'] < 0.7), df['A'] >= 0.7],
    [lambda x: x*2, lambda x: x, lambda x: x/2]
)

# Checking if values are in a set
in_set = np.isin(df['B'], [10, 20, 30, 40, 50])
df['F'] = np.where(in_set, 'In set', 'Not in set')

# Find rows where any value is NaN
has_nan = np.isnan(df.select_dtypes(include=['float64']).values).any(axis=1)
df_without_nans = df[~has_nan]
```

### Working with Missing Values

```python
# Create a DataFrame with missing values
df = pd.DataFrame({
    'A': [1, 2, np.nan, 4, 5],
    'B': [np.nan, 2, 3, np.nan, 5],
    'C': [1, 2, 3, 4, 5]
})

# Find missing values
missing_mask = np.isnan(df.values)
missing_rows = np.any(missing_mask, axis=1)
missing_cols = np.any(missing_mask, axis=0)

# Count missing values
missing_count = np.sum(missing_mask)
row_missing_count = np.sum(missing_mask, axis=1)
col_missing_count = np.sum(missing_mask, axis=0)

# Replace missing values with column means
col_means = np.nanmean(df.values, axis=0)
df_filled = df.copy()
for i, col in enumerate(df.columns):
    df_filled[col] = np.where(np.isnan(df[col]), col_means[i], df[col])

# Fill missing values based on conditions
condition = df['A'] > 3
df['B'] = np.where(np.isnan(df['B']) & condition, 999, df['B'])

# Drop rows with any missing values using NumPy mask
df_no_missing = df[~np.any(np.isnan(df.values), axis=1)]
```

## Mapping Values

### Value Mapping and Transformation

```python
# Create a DataFrame
df = pd.DataFrame({
    'A': np.random.randint(1, 6, 10),
    'B': np.random.rand(10),
    'C': np.random.choice(['X', 'Y', 'Z'], 10)
})

# Map values using NumPy's where function
df['A_mapped'] = np.where(df['A'] <= 3, 'Low', 'High')

# Multiple conditions mapping
conditions = [
    df['A'] == 1,
    df['A'] == 2,
    df['A'] == 3,
    df['A'] == 4,
    df['A'] == 5
]
choices = ['Very Low', 'Low', 'Medium', 'High', 'Very High']
df['A_category'] = np.select(conditions, choices, default='Unknown')

# Binning continuous values
df['B_binned'] = np.digitize(df['B'], bins=[0.2, 0.4, 0.6, 0.8])

# Map with a dictionary using NumPy
mapping_dict = {'X': 10, 'Y': 20, 'Z': 30}
df['C_mapped'] = np.array([mapping_dict.get(x, 0) for x in df['C']])

# Advanced mapping with functions
def mapping_func(val):
    if val < 0.3:
        return val * 2
    elif val < 0.7:
        return val * 1.5
    else:
        return val

df['B_transformed'] = np.vectorize(mapping_func)(df['B'])
```

### Binning and Discretization

```python
# Create a DataFrame with continuous values
df = pd.DataFrame({
    'value': np.random.randn(1000) * 10 + 50  # Normal distribution around 50
})

# Simple binning with fixed width
bin_edges = np.arange(30, 80, 5)  # Bins from 30 to 75 with width 5
df['bin_idx'] = np.digitize(df['value'], bin_edges)
df['bin_label'] = df['bin_idx'].apply(lambda x: f'{bin_edges[x-1]}-{bin_edges[x]}' if x < len(bin_edges) else f'>{bin_edges[-1]}')

# Quantile-based binning
quantiles = np.percentile(df['value'], [0, 25, 50, 75, 100])
df['quantile_bin'] = np.digitize(df['value'], quantiles)

# Equal-frequency binning (each bin has same number of items)
n_bins = 5
bin_indices = np.linspace(0, len(df), n_bins + 1, dtype=int)
sorted_idx = np.argsort(df['value'])
bins = np.zeros(len(df), dtype=int)

for i in range(n_bins):
    bins[sorted_idx[bin_indices[i]:bin_indices[i+1]]] = i

df['equal_freq_bin'] = bins

# K-means binning
from sklearn.cluster import KMeans

values = df['value'].values.reshape(-1, 1)
kmeans = KMeans(n_clusters=5, random_state=0).fit(values)
df['kmeans_bin'] = kmeans.labels_

# Custom binning function
def custom_binning(values, n_bins=5, strategy='equal_width'):
    if strategy == 'equal_width':
        # Equal width binning
        bin_edges = np.linspace(min(values), max(values), n_bins + 1)
    elif strategy == 'equal_freq':
        # Equal frequency binning
        bin_edges = np.percentile(values, np.linspace(0, 100, n_bins + 1))
    else:
        raise ValueError("Strategy not recognized")
    
    # Get bin indices
    bin_indices = np.digitize(values, bin_edges[1:-1])
    
    # Create bin labels
    bin_labels = [f"{bin_edges[i]:.2f}-{bin_edges[i+1]:.2f}" for i in range(n_bins)]
    
    # Map indices to labels
    result_labels = np.array(bin_labels)[bin_indices]
    
    return bin_indices, result_labels, bin_edges

bin_idx, bin_labels, bin_edges = custom_binning(df['value'], n_bins=6)
df['custom_bin_idx'] = bin_idx
df['custom_bin_label'] = bin_labels
```

### Scaling and Normalization

```python
# Create a DataFrame with multiple features
df = pd.DataFrame({
    'A': np.random.randn(100) * 10 + 50,  # Mean 50, std 10
    'B': np.random.randn(100) * 5 + 20,   # Mean 20, std 5
    'C': np.random.randn(100) * 2 + 10    # Mean 10, std 2
})

# Min-Max scaling (normalize to [0, 1])
def min_max_scale(x):
    return (x - np.min(x)) / (np.max(x) - np.min(x))

df_minmax = df.apply(min_max_scale)

# Custom range scaling (normalize to [a, b])
def range_scale(x, a=0, b=1):
    return a + (b - a) * (x - np.min(x)) / (np.max(x) - np.min(x))

df_range = df.apply(lambda x: range_scale(x, -1, 1))

# Z-score normalization (standardization)
def z_scale(x):
    return (x - np.mean(x)) / np.std(x)

df_z = df.apply(z_scale)

# Robust scaling using quantiles (less sensitive to outliers)
def robust_scale(x):
    q25 = np.percentile(x, 25)
    q75 = np.percentile(x, 75)
    iqr = q75 - q25
    if iqr == 0:
        return np.zeros_like(x)
    return (x - np.median(x)) / iqr

df_robust = df.apply(robust_scale)

# Max Absolute scaling
def maxabs_scale(x):
    return x / np.max(np.abs(x))

df_maxabs = df.apply(maxabs_scale)

# Log transformation
def log_transform(x):
    # Add small constant to avoid log(0)
    min_val = np.min(x)
    if min_val <= 0:
        return np.log(x - min_val + 1)
    return np.log(x)

df_log = df.apply(log_transform)

# Box-Cox transformation
from scipy import stats

def boxcox_transform(x):
    # Ensure all values are positive
    min_val = np.min(x)
    if min_val <= 0:
        x_shifted = x - min_val + 1
    else:
        x_shifted = x
    
    # Find optimal lambda parameter
    x_boxcox, lambda_opt = stats.boxcox(x_shifted)
    
    return x_boxcox

# Apply Box-Cox to each column
df_boxcox = pd.DataFrame()
for col in df.columns:
    df_boxcox[col] = boxcox_transform(df[col])
```

## Array Transformations

### Reshaping DataFrames

```python
# Create a DataFrame
df = pd.DataFrame(np.random.rand(12).reshape(4, 3), columns=['A', 'B', 'C'])

# Reshape to 1D array
flat_array = df.values.flatten()
flat_array_ravel = np.ravel(df.values)  # Returns a view when possible

# Reshape to different dimensions
reshaped_2x6 = df.values.reshape(2, 6)
reshaped_6x2 = df.values.reshape(6, 2)
reshaped_auto = df.values.reshape(-1, 2)  # Automatically calculate rows

# Unstack a DataFrame to a higher dimensional array
multi_df = pd.DataFrame({
    'A': np.random.rand(12),
    'B': np.random.rand(12),
    'time': np.repeat(['t1', 't2', 't3', 't4'], 3),
    'category': np.tile(['X', 'Y', 'Z'], 4)
})

# Pivot to reshape from long to wide format
pivot_df = multi_df.pivot(index='time', columns='category', values=['A', 'B'])

# Convert to 3D NumPy array (time, category, variables)
array_3d = np.zeros((4, 3, 2))  # (4 times, 3 categories, 2 variables)
for i, t in enumerate(['t1', 't2', 't3', 't4']):
    for j, c in enumerate(['X', 'Y', 'Z']):
        time_cat_data = multi_df[(multi_df['time'] == t) & (multi_df['category'] == c)]
        if not time_cat_data.empty:
            array_3d[i, j, 0] = time_cat_data['A'].values[0]
            array_3d[i, j, 1] = time_cat_data['B'].values[0]

# Reshape back to DataFrame (from 3D to 2D)
flat_array = array_3d.reshape(-1, array_3d.shape[-1])
index_labels = [f"{t}_{c}" for t in ['t1', 't2', 't3', 't4'] for c in ['X', 'Y', 'Z']]
restored_df = pd.DataFrame(flat_array, index=index_labels, columns=['A', 'B'])
```

### Stacking and Tiling

```python
# Create sample DataFrames
df1 = pd.DataFrame(np.random.rand(3, 2), columns=['A', 'B'])
df2 = pd.DataFrame(np.random.rand(3, 2), columns=['A', 'B'])

# Vertical stacking (row-wise)
vertical_stack = np.vstack((df1.values, df2.values))
vstack_df = pd.DataFrame(vertical_stack, columns=df1.columns)

# Horizontal stacking (column-wise)
horizontal_stack = np.hstack((df1.values, df2.values))
hstack_df = pd.DataFrame(
    horizontal_stack,
    columns=[f"{col}_{i}" for i in range(1, 3) for col in df1.columns]
)

# Column binding with different column names
df3 = pd.DataFrame(np.random.rand(3, 2), columns=['C', 'D'])
combined_df = pd.DataFrame(
    np.hstack((df1.values, df3.values)),
    columns=list(df1.columns) + list(df3.columns)
)

# Repeating arrays
df_repeated = pd.DataFrame(
    np.tile(df1.values, (2, 3)),
    columns=[f"{col}_{i}" for i in range(1, 4) for col in df1.columns]
)

# Repeating along one axis
row_repeated = pd.DataFrame(
    np.repeat(df1.values, 2, axis=0),
    columns=df1.columns
)
col_repeated = pd.DataFrame(
    np.repeat(df1.values, 2, axis=1),
    columns=[f"{col}_{i}" for col in df1.columns for i in range(1, 3)]
)
```

### Advanced Transformations

```python
# Create a DataFrame
df = pd.DataFrame(np.random.rand(5, 3), columns=['A', 'B', 'C'])

# Apply NumPy transformations
df_sqrt = pd.DataFrame(np.sqrt(df.values), columns=df.columns)
df_log = pd.DataFrame(np.log1p(df.values), columns=df.columns)  # log(1+x)
df_exp = pd.DataFrame(np.exp(df.values), columns=df.columns)

# Element-wise operations
df_custom = pd.DataFrame(
    np.sin(df.values) * np.cos(df.values),
    columns=df.columns
)

# Matrix operations
df_matrix = pd.DataFrame(np.matmul(df.values, df.values.T))

# SVD decomposition
U, S, Vt = np.linalg.svd(df.values, full_matrices=False)
# Reconstruction
df_reconstructed = pd.DataFrame(
    np.matmul(np.matmul(U, np.diag(S)), Vt),
    columns=df.columns
)

# PCA using NumPy
# Center the data
centered_data = df.values - np.mean(df.values, axis=0)
# Calculate covariance matrix
cov_matrix = np.cov(centered_data, rowvar=False)
# Get eigenvalues and eigenvectors
eigenvalues, eigenvectors = np.linalg.eigh(cov_matrix)
# Sort by eigenvalues in descending order
idx = eigenvalues.argsort()[::-1]
eigenvalues = eigenvalues[idx]
eigenvectors = eigenvectors[:, idx]
# Project data onto principal components
n_components = 2
df_pca = pd.DataFrame(
    np.matmul(centered_data, eigenvectors[:, :n_components]),
    columns=['PC1', 'PC2']
)

# Fast Fourier Transform
df_fft = pd.DataFrame(
    np.abs(np.fft.fft(df.values, axis=0)),
    columns=[f"{col}_fft" for col in df.columns]
)

# Polynomial features
def polynomial_features(X, degree=2):
    """Generate polynomial features up to specified degree"""
    n_samples, n_features = X.shape
    n_output_features = 0
    for d in range(1, degree + 1):
        n_output_features += comb(n_features + d - 1, d, exact=True)
    
    result = np.empty((n_samples, n_output_features), dtype=X.dtype)
    col_idx = 0
    
    for d in range(1, degree + 1):
        combs = combinations_with_replacement(range(n_features), d)
        for comb in combs:
            result[:, col_idx] = np.prod(X[:, comb], axis=1)
            col_idx += 1
    
    return result

from itertools import combinations_with_replacement
from scipy.special import comb

df_poly = pd.DataFrame(
    polynomial_features(df.values, degree=2),
    columns=[f"poly_{i}" for i in range(1, 10)]  # Adjust column count based on formula
)
```

## Performance Optimization

### Vectorized Operations

```python
# Create a DataFrame with numerical data
df = pd.DataFrame({
    'A': np.random.rand(10000),
    'B': np.random.rand(10000),
    'C': np.random.rand(10000)
})

# Slow approach (avoid)
def slow_distance(df):
    result = []
    for i in range(len(df)):
        point1 = df.iloc[i].values
        distances = []
        for j in range(len(df)):
            point2 = df.iloc[j].values
            distance = np.sqrt(np.sum((point1 - point2) ** 2))
            distances.append(distance)
        result.append(np.mean(distances))
    return np.array(result)

# Fast vectorized approach
def fast_distance(df):
    # Extract values as numpy array
    points = df.values
    # Compute pairwise squared differences
    diff = points[:, np.newaxis, :] - points[np.newaxis, :, :]
    sq_diff = diff ** 2
    # Sum over feature axis and take square root
    distances = np.sqrt(np.sum(sq_diff, axis=2))
    # Compute mean distance for each point
    return np.mean(distances, axis=1)

# Compare speed with %timeit in Jupyter

# Apply vectorized functions to groups
def group_standardize(group_df):
    """Standardize values within each group"""
    values = group_df.values
    return (values - np.mean(values, axis=0)) / np.std(values, axis=0)

# Apply to groups
df['group'] = np.random.choice(['A', 'B', 'C', 'D'], size=len(df))
result = df.groupby('group').apply(
    lambda x: pd.DataFrame(
        group_standardize(x[['A', 'B', 'C']]),
        index=x.index,
        columns=['A_std', 'B_std', 'C_std']
    )
)
```

### Memory Optimization

```python
# Create a large DataFrame
df_large = pd.DataFrame(np.random.rand(100000, 10))

# Check memory usage
memory_usage = df_large.memory_usage(deep=True).sum() / (1024 * 1024)  # MB

# Use smaller datatypes
df_optimized = df_large.astype(np.float32)  # Reduce from float64 to float32
memory_saved = 1 - (df_optimized.memory_usage(deep=True).sum() / 
                     df_large.memory_usage(deep=True).sum())

# Process data in chunks
chunks = np.array_split(df_large.values, 10)  # Split into 10 chunks
results = []

for chunk in chunks:
    # Process each chunk
    processed = np.mean(chunk, axis=0)
    results.append(processed)

# Combine results
final_result = np.mean(results, axis=0)

# Optimize categorical data
categories = ['cat1', 'cat2', 'cat3', 'cat4', 'cat5']
df_large['category'] = np.random.choice(categories, size=len(df_large))

# Convert to categorical dtype
df_large['category'] = df_large['category'].astype('category')
memory_saved_cat = (df_large.memory_usage(deep=True).sum() / 
                    df_large.memory_usage(deep=True).sum(before='category'))

# Memory-efficient calculations on subsets
def memory_efficient_calc(df, cols, func):
    """Apply function to subset of columns without copying the entire dataframe"""
    return func(df[cols].values)

result = memory_efficient_calc(df_large, [0, 1, 2], np.mean)
```

## Time Series Operations

### Resampling and Rolling Statistics

```python
# Create a time series DataFrame
dates = pd.date_range('2023-01-01', periods=1000, freq='H')
df_ts = pd.DataFrame({
    'value': np.sin(np.linspace(0, 20*np.pi, 1000)) + np.random.randn(1000) * 0.2,
    'count': np.random.poisson(5, size=1000)
}, index=dates)

# Resample to daily frequency
daily_mean = df_ts.resample('D').mean()
daily_sum = df_ts.resample('D').sum()

# Apply NumPy functions to resampled data
daily_stats = df_ts.resample('D').agg({
    'value': [np.mean, np.std, np.min, np.max],
    'count': [np.sum, np.mean]
})

# Rolling window operations with NumPy functions
rolling_mean = df_ts.rolling(window=24).apply(np.mean)
rolling_std = df_ts.rolling(window=24).apply(np.std)

# Exponentially weighted calculations
def ewma(x, alpha=0.1):
    """Calculate exponentially weighted moving average"""
    # Initialize with mean of first window
    n = len(x)
    s = np.zeros(n)
    s[0] = x[0]
    for i in range(1, n):
        s[i] = alpha * x[i] + (1 - alpha) * s[i-1]
    return s

df_ts['ewma'] = ewma(df_ts['value'].values)

# Detect outliers using rolling Z-score
def rolling_zscore(x, window=24):
    """Calculate rolling Z-score"""
    rolling_mean = np.convolve(x, np.ones(window)/window, mode='valid')
    # Pad to match original size
    padded_mean = np.pad(rolling_mean, (window-1, 0), 'constant', constant_values=np.nan)
    
    # Calculate rolling standard deviation
    rolling_var = np.zeros_like(x)
    for i in range(window-1, len(x)):
        rolling_var[i] = np.std(x[i-(window-1):i+1])
    
    # Calculate Z-score
    zscore = np.zeros_like(x)
    for i in range(window-1, len(x)):
        if rolling_var[i] > 0:
            zscore[i] = (x[i] - padded_mean[i]) / rolling_var[i]
        else:
            zscore[i] = 0
    
    return zscore

df_ts['zscore'] = rolling_zscore(df_ts['value'].values)
df_ts['outlier'] = np.abs(df_ts['zscore']) > 3  # Mark as outlier if |z| > 3
```

### Seasonality and Trend Analysis

```python
# Create a seasonal time series
dates = pd.date_range('2023-01-01', periods=1000, freq='H')
time = np.arange(len(dates))

# Create components
trend = 0.1 * time / 100  # Upward trend
day_cycle = 24  # Hours
week_cycle = 24 * 7  # Hours
day_seasonal = 5 * np.sin(2 * np.pi * time / day_cycle)  # Daily seasonality
week_seasonal = 3 * np.sin(2 * np.pi * time / week_cycle)  # Weekly seasonality
noise = np.random.normal(0, 1, len(time))  # Random noise

# Combine components
signal = trend + day_seasonal + week_seasonal + noise

df_ts = pd.DataFrame({
    'value': signal
}, index=dates)

# Simple moving average to extract trend
def moving_average(x, window):
    """Compute the simple moving average"""
    return np.convolve(x, np.ones(window)/window, mode='same')

df_ts['trend_ma'] = moving_average(df_ts['value'].values, 24*7)  # 1-week moving average

# Detrending using moving average
df_ts['detrended'] = df_ts['value'] - df_ts['trend_ma']

# Seasonal decomposition using FFT
def fft_decompose(x, period, n_harmonics=3):
    """Extract seasonal component using FFT"""
    n = len(x)
    # Compute FFT
    fft_values = np.fft.rfft(x)
    frequencies = np.fft.rfftfreq(n)
    
    # Create mask for the fundamental frequency and harmonics
    mask = np.zeros(len(frequencies), dtype=bool)
    target_freq = 1.0 / period
    
    for i in range(1, n_harmonics + 1):
        # Find the index closest to the target frequency and its harmonics
        idx = np.argmin(np.abs(frequencies - i * target_freq))
        mask[idx] = True
    
    # Apply mask (keep only seasonal components)
    filtered_fft = np.zeros_like(fft_values)
    filtered_fft[mask] = fft_values[mask]
    
    # Inverse FFT to get seasonal component
    seasonal = np.fft.irfft(filtered_fft, n)
    
    return seasonal

# Extract daily and weekly seasonality
df_ts['daily_seasonal'] = fft_decompose(df_ts['detrended'].values, 24)
df_ts['weekly_seasonal'] = fft_decompose(df_ts['detrended'].values, 24*7)

# Calculate residuals
df_ts['residuals'] = df_ts['value'] - df_ts['trend_ma'] - df_ts['daily_seasonal'] - df_ts['weekly_seasonal']

# Autocorrelation analysis
def autocorrelation(x, lags):
    """Calculate autocorrelation for given lags"""
    n = len(x)
    # Subtract mean
    x_demean = x - np.mean(x)
    # Calculate variance (denominator)
    variance = np.sum(x_demean**2) / n
    
    # Calculate autocorrelation for each lag
    acf = np.zeros(lags)
    for lag in range(1, lags + 1):
        # Calculate cross-product
        cross_prod = np.sum(x_demean[:-lag] * x_demean[lag:])
        # Normalize by variance and sample size
        acf[lag-1] = cross_prod / ((n - lag) * variance)
    
    return acf

# Calculate autocorrelation up to 48 hours
acf_values = autocorrelation(df_ts['value'].values, 48)
acf_df = pd.DataFrame({'lag': np.arange(1, 49), 'acf': acf_values})
```

### Forecasting Models

```python
# Simple linear trend forecasting
def linear_trend_forecast(y, periods_ahead):
    """Forecast using linear trend"""
    n = len(y)
    x = np.arange(n)
    
    # Fit linear model: y = ax + b
    a, b = np.polyfit(x, y, 1)
    
    # Generate forecast
    forecast_x = np.arange(n, n + periods_ahead)
    forecast_y = a * forecast_x + b
    
    return forecast_y

# Exponential smoothing forecast
def exp_smoothing_forecast(y, periods_ahead, alpha=0.2):
    """Forecast using simple exponential smoothing"""
    n = len(y)
    # Initialize smoothed series
    s = np.zeros(n)
    s[0] = y[0]
    
    # Apply exponential smoothing
    for i in range(1, n):
        s[i] = alpha * y[i] + (1 - alpha) * s[i-1]
    
    # Generate forecast (last smoothed value repeated)
    forecast = np.ones(periods_ahead) * s[-1]
    
    return forecast

# Holt-Winters forecasting
def holt_winters_forecast(y, periods_ahead, season_length, 
                          alpha=0.2, beta=0.1, gamma=0.1):
    """
    Forecast using Holt-Winters method with additive seasonality
    """
    n = len(y)
    
    # Initialize level, trend, and seasonal components
    l = np.zeros(n)
    b = np.zeros(n)
    s = np.zeros(n)
    
    # Initialize first values
    l[0] = y[0]
    b[0] = y[1] - y[0]
    
    # Initialize seasonal component with simple average
    for i in range(season_length):
        if i < n:
            s[i] = y[i] - l[0]
    
    # Apply Holt-Winters method
    for i in range(1, n):
        # Update level, trend, and seasonal components
        if i >= season_length:
            l[i] = alpha * (y[i] - s[i-season_length]) + (1 - alpha) * (l[i-1] + b[i-1])
            b[i] = beta * (l[i] - l[i-1]) + (1 - beta) * b[i-1]
            s[i] = gamma * (y[i] - l[i]) + (1 - gamma) * s[i-season_length]
        else:
            l[i] = alpha * y[i] + (1 - alpha) * (l[i-1] + b[i-1])
            b[i] = beta * (l[i] - l[i-1]) + (1 - beta) * b[i-1]
    
    # Generate forecast
    forecast = np.zeros(periods_ahead)
    for i in range(periods_ahead):
        forecast[i] = l[-1] + (i+1) * b[-1] + s[-(season_length - ((i+1) % season_length))]
    
    return forecast

# Forecast examples
last_30_days = df_ts['value'][-30*24:].values
forecast_horizon = 7*24  # 7 days ahead

linear_forecast = linear_trend_forecast(last_30_days, forecast_horizon)
exp_forecast = exp_smoothing_forecast(last_30_days, forecast_horizon)
hw_forecast = holt_winters_forecast(last_30_days, forecast_horizon, 24)  # 24-hour seasonality

# Create DataFrame with forecasts
forecast_dates = pd.date_range(
    start=df_ts.index[-1] + pd.Timedelta(hours=1),
    periods=forecast_horizon,
    freq='H'
)

forecast_df = pd.DataFrame({
    'linear_forecast': linear_forecast,
    'exp_forecast': exp_forecast,
    'hw_forecast': hw_forecast
}, index=forecast_dates)
```

## Advanced Data Manipulation

### Matrix Operations

```python
# Create a DataFrame
df = pd.DataFrame(np.random.rand(5, 3), columns=['A', 'B', 'C'])

# Apply matrix operations
matrix = df.values

# Matrix multiplication
correlation_matrix = np.matmul(matrix.T, matrix)  # X'X correlation matrix
correlation_df = pd.DataFrame(
    correlation_matrix,
    index=df.columns,
    columns=df.columns
)

# Calculate Mahalanobis distance
def mahalanobis_distance(x, mean, cov_inv):
    """Calculate Mahalanobis distance for each row"""
    diff = x - mean
    return np.sqrt(np.sum(np.matmul(diff, cov_inv) * diff, axis=1))

# Calculate mean and covariance
mean_vec = np.mean(matrix, axis=0)
cov_matrix = np.cov(matrix, rowvar=False)
cov_inv = np.linalg.inv(cov_matrix)

# Add Mahalanobis distance
df['mahalanobis'] = mahalanobis_distance(matrix, mean_vec, cov_inv)

# Vector operations
norm = np.linalg.norm(matrix, axis=1)  # Euclidean norm of each row
df['norm'] = norm

# Row-wise and column-wise operations
row_min_col = np.argmin(matrix, axis=1)  # Index of min value in each row
col_max_row = np.argmax(matrix, axis=0)  # Index of max value in each column

df['min_col_idx'] = row_min_col
df_transposed = pd.DataFrame(
    matrix.T,
    index=df.columns,
    columns=df.index
)
df_transposed['max_row_idx'] = col_max_row

# Using numpy.linalg with DataFrames
eigenvalues, eigenvectors = np.linalg.eig(correlation_matrix)
eigen_df = pd.DataFrame({
    'eigenvalue': eigenvalues,
    'eigenvector_1': eigenvectors[:, 0],
    'eigenvector_2': eigenvectors[:, 1],
    'eigenvector_3': eigenvectors[:, 2]
}, index=df.columns)

# Singular Value Decomposition (SVD)
U, S, Vt = np.linalg.svd(matrix, full_matrices=False)
svd_df = pd.DataFrame({
    'U1': U[:, 0],
    'U2': U[:, 1],
    'U3': U[:, 2]
})
svd_df['singular_values'] = np.tile(S, (len(svd_df), 1))
```

### Distance Calculation and Similarity

```python
# Create two DataFrames
df1 = pd.DataFrame(np.random.rand(100, 5), columns=list('ABCDE'))
df2 = pd.DataFrame(np.random.rand(50, 5), columns=list('ABCDE'))

# Extract NumPy arrays
X1 = df1.values
X2 = df2.values

# Euclidean distance between all pairs of points
def pairwise_euclidean(X1, X2):
    """Calculate Euclidean distance between all pairs of points in X1 and X2"""
    # Squared norms of each point
    X1_sq_norm = np.sum(X1**2, axis=1).reshape(-1, 1)
    X2_sq_norm = np.sum(X2**2, axis=1).reshape(1, -1)
    
    # Use broadcasting to calculate squared distances
    # ||x-y||^2 = ||x||^2 + ||y||^2 - 2 x·y
    X1X2 = np.matmul(X1, X2.T)
    sq_distances = X1_sq_norm + X2_sq_norm - 2 * X1X2
    
    # Handle small negative values due to numerical precision
    sq_distances = np.maximum(sq_distances, 0)
    
    return np.sqrt(sq_distances)

distances = pairwise_euclidean(X1, X2)
distance_df = pd.DataFrame(
    distances,
    index=df1.index,
    columns=df2.index
)

# Cosine similarity between all pairs
def pairwise_cosine(X1, X2):
    """Calculate cosine similarity between all pairs of points in X1 and X2"""
    # Normalize each vector to unit length
    X1_normalized = X1 / np.linalg.norm(X1, axis=1, keepdims=True)
    X2_normalized = X2 / np.linalg.norm(X2, axis=1, keepdims=True)
    
    # Calculate dot product (which equals cosine similarity for normalized vectors)
    return np.matmul(X1_normalized, X2_normalized.T)

similarities = pairwise_cosine(X1, X2)
similarity_df = pd.DataFrame(
    similarities,
    index=df1.index,
    columns=df2.index
)

# Manhattan distance between all pairs
def pairwise_manhattan(X1, X2):
    """Calculate Manhattan (L1) distance between all pairs of points"""
    n1 = X1.shape[0]
    n2 = X2.shape[0]
    distances = np.zeros((n1, n2))
    
    for i in range(n1):
        for j in range(n2):
            distances[i, j] = np.sum(np.abs(X1[i] - X2[j]))
    
    return distances

manhattan_distances = pairwise_manhattan(X1, X2)

# Find k-nearest neighbors
def k_nearest_neighbors(X1, X2, k=5, metric='euclidean'):
    """Find k-nearest neighbors in X2 for each point in X1"""
    if metric == 'euclidean':
        distances = pairwise_euclidean(X1, X2)
    elif metric == 'cosine':
        # Convert similarity to distance: d = 1 - similarity
        distances = 1 - pairwise_cosine(X1, X2)
    elif metric == 'manhattan':
        distances = pairwise_manhattan(X1, X2)
    else:
        raise ValueError("Unsupported metric")
    
    # Find indices of k smallest distances for each row
    nearest_indices = np.argsort(distances, axis=1)[:, :k]
    nearest_distances = np.take_along_axis(distances, nearest_indices, axis=1)
    
    return nearest_indices, nearest_distances

nearest_idx, nearest_dist = k_nearest_neighbors(X1, X2, k=3)

# Create a DataFrame with nearest neighbor info
knn_df = pd.DataFrame()
for i in range(3):
    knn_df[f'nn_{i+1}_idx'] = nearest_idx[:, i]
    knn_df[f'nn_{i+1}_dist'] = nearest_dist[:, i]
```

### Data Imputation

```python
# Create a DataFrame with missing values
df = pd.DataFrame({
    'A': np.random.rand(100),
    'B': np.random.rand(100),
    'C': np.random.rand(100),
    'D': np.random.rand(100),
    'E': np.random.rand(100)
})

# Introduce some missing values
for col in df.columns:
    mask = np.random.random(size=len(df)) < 0.1  # 10% missing
    df.loc[mask, col] = np.nan

# Get a mask of missing values
missing_mask = np.isnan(df.values)

# 1. Simple imputation methods
# Mean imputation
def mean_imputation(X, missing_mask):
    """Impute missing values with column means"""
    X_imputed = X.copy()
    col_means = np.nanmean(X, axis=0)
    
    # Use NumPy's where function
    for j in range(X.shape[1]):
        X_imputed[:, j] = np.where(
            missing_mask[:, j],
            col_means[j],
            X[:, j]
        )
    
    return X_imputed

# Median imputation
def median_imputation(X, missing_mask):
    """Impute missing values with column medians"""
    X_imputed = X.copy()
    col_medians = np.nanmedian(X, axis=0)
    
    for j in range(X.shape[1]):
        X_imputed[:, j] = np.where(
            missing_mask[:, j],
            col_medians[j],
            X[:, j]
        )
    
    return X_imputed

# 2. KNN imputation
def knn_imputation(X, missing_mask, k=5):
    """Impute missing values using k-nearest neighbors"""
    X_imputed = X.copy()
    n_samples, n_features = X.shape
    
    # Find rows with missing values
    has_missing = np.any(missing_mask, axis=1)
    missing_rows = np.where(has_missing)[0]
    
    # For each row with missing values
    for i in missing_rows:
        # Find columns with missing values
        missing_cols = np.where(missing_mask[i])[0]
        
        # Find complete columns for this row
        valid_cols = np.where(~missing_mask[i])[0]
        
        # Skip if no valid columns
        if len(valid_cols) == 0:
            continue
        
        # Find rows without missing values in valid_cols
        valid_rows_mask = ~np.any(missing_mask[:, valid_cols], axis=1)
        valid_rows = np.where(valid_rows_mask)[0]
        
        # Skip if no valid rows
        if len(valid_rows) < k:
            continue
        
        # Calculate distances based on valid columns
        dists = np.zeros(len(valid_rows))
        for idx, j in enumerate(valid_rows):
            dists[idx] = np.sqrt(np.sum((X[i, valid_cols] - X[j, valid_cols])**2))
        
        # Find k nearest neighbors
        nn_idx = valid_rows[np.argsort(dists)[:k]]
        
        # Impute missing values with mean of neighbors
        for col in missing_cols:
            # Get values from neighbors (skip if they're also missing)
            nn_values = X[nn_idx, col]
            valid_nn = ~np.isnan(nn_values)
            
            if np.any(valid_nn):
                X_imputed[i, col] = np.mean(nn_values[valid_nn])
    
    return X_imputed

# Apply imputation methods
X = df.values
X_mean_imputed = mean_imputation(X, missing_mask)
X_median_imputed = median_imputation(X, missing_mask)
X_knn_imputed = knn_imputation(X, missing_mask, k=5)

# Convert back to DataFrames
df_mean_imputed = pd.DataFrame(X_mean_imputed, columns=df.columns)
df_median_imputed = pd.DataFrame(X_median_imputed, columns=df.columns)
df_knn_imputed = pd.DataFrame(X_knn_imputed, columns=df.columns)

# 3. Iterative imputation (simplified version)
def iterative_imputation(X, missing_mask, max_iter=10, tol=1e-3):
    """Impute missing values using iterative regression"""
    X_imputed = mean_imputation(X, missing_mask)  # Initial imputation
    
    for iteration in range(max_iter):
        X_previous = X_imputed.copy()
        
        # For each column with missing values
        for j in range(X.shape[1]):
            if np.any(missing_mask[:, j]):
                # Create mask for rows missing this feature
                mask_j = missing_mask[:, j]
                
                # Get other columns (predictors)
                other_cols = [col for col in range(X.shape[1]) if col != j]
                
                # Train model on complete rows
                X_train = X_imputed[~mask_j][:, other_cols]
                y_train = X_imputed[~mask_j][:, j]
                
                # Fit a linear model
                try:
                    # Solve linear system: X_train' X_train b = X_train' y_train
                    XtX = np.matmul(X_train.T, X_train)
                    Xty = np.matmul(X_train.T, y_train)
                    beta = np.linalg.solve(XtX, Xty)
                    
                    # Predict and impute missing values
                    X_test = X_imputed[mask_j][:, other_cols]
                    y_pred = np.matmul(X_test, beta)
                    X_imputed[mask_j, j] = y_pred
                except np.linalg.LinAlgError:
                    # If matrix is singular, keep previous imputation
                    pass
        
        # Check convergence
        diff = np.mean((X_imputed - X_previous)**2)
        if diff < tol:
            break
    
    return X_imputed

# Apply iterative imputation
X_iter_imputed = iterative_imputation(X, missing_mask)
df_iter_imputed = pd.DataFrame(X_iter_imputed, columns=df.columns)
```

## Integration with PySpark DataFrames

### NumPy-to-PySpark and Back

```python
from pyspark.sql import SparkSession
import pyspark.sql.functions as F
from pyspark.sql.types import *
import numpy as np

# Initialize SparkSession (in a real environment, this would connect to a Spark cluster)
spark = SparkSession.builder.appName("numpy-pyspark").getOrCreate()

# Create a NumPy array
arr = np.array([
    [1, 2, 3, 4, 5],
    [6, 7, 8, 9, 10],
    [11, 12, 13, 14, 15],
    [16, 17, 18, 19, 20]
])

# Convert NumPy array to Pandas DataFrame first
pandas_df = pd.DataFrame(arr, columns=['A', 'B', 'C', 'D', 'E'])

# Convert Pandas DataFrame to PySpark DataFrame
spark_df = spark.createDataFrame(pandas_df)

# Common operations with Spark DataFrames
# Note: These return Spark DataFrames, not NumPy arrays directly
spark_df_filtered = spark_df.filter(F.col('A') > 5)
spark_df_selected = spark_df.select('A', 'B', 'C')
spark_df_agg = spark_df.groupBy().agg(
    F.mean('A').alias('A_mean'),
    F.stddev('A').alias('A_std')
)

# Convert Spark DataFrame back to NumPy
# First to Pandas, then to NumPy
pandas_df_back = spark_df.toPandas()
arr_back = pandas_df_back.values

# Working with large datasets (using partitioning)
def process_in_partitions(spark_df, batch_size=1000):
    """Process a large Spark DataFrame in batches using NumPy"""
    # Get total count (might be expensive for very large datasets)
    total_count = spark_df.count()
    results = []
    
    # Process in batches
    for start in range(0, total_count, batch_size):
        end = min(start + batch_size, total_count)
        
        # Collect a batch to driver as NumPy array
        batch_df = spark_df.limit(batch_size).toPandas()
        batch_array = batch_df.values
        
        # Process the batch with NumPy operations
        processed_array = np.mean(batch_array, axis=0)  # Example operation
        results.append(processed_array)
    
    # Combine results
    return np.array(results)
```

### PySpark UDFs with NumPy

```python
from pyspark.sql.types import *
from pyspark.sql.functions import udf, pandas_udf
from pyspark.sql import functions as F
import numpy as np
import pandas as pd

# Regular UDF with NumPy (slower, transfers data as Python objects)
def normalize_array(arr):
    """Normalize an array to have zero mean and unit variance"""
    np_arr = np.array(arr)
    mean = np.mean(np_arr)
    std = np.std(np_arr)
    if std > 0:
        return (np_arr - mean) / std
    return np_arr

# Register UDF
normalize_udf = udf(normalize_array, ArrayType(DoubleType()))

# Apply to a DataFrame column
spark_df = spark_df.withColumn(
    'A_normalized',
    normalize_udf(F.array('A', 'B', 'C'))
)

# Pandas UDF (faster, leverages Apache Arrow)
@pandas_udf(ArrayType(DoubleType()))
def normalize_pandas_udf(arr_series):
    """Normalize arrays using pandas Series"""
    def normalize_single(arr):
        np_arr = np.array(arr)
        mean = np.mean(np_arr)
        std = np.std(np_arr)
        if std > 0:
            return (np_arr - mean) / std
        return np_arr
    
    return arr_series.apply(normalize_single)

# Apply Pandas UDF
spark_df = spark_df.withColumn(
    'A_normalized_fast',
    normalize_pandas_udf(F.array('A', 'B', 'C'))
)

# Vectorized UDF for multiple columns
@pandas_udf(
    "struct<A_norm: double, B_norm: double, C_norm: double>",
    PandasUDFType.SCALAR
)
def normalize_columns(A: pd.Series, B: pd.Series, C: pd.Series) -> pd.DataFrame:
    # Stack columns into a 2D array
    matrix = np.column_stack([A, B, C])
    
    # Normalize each column
    means = np.mean(matrix, axis=0)
    stds = np.std(matrix, axis=0)
    stds[stds == 0] = 1.0  # Avoid division by zero
    
    normalized = (matrix - means) / stds
    
    # Return as a DataFrame
    return pd.DataFrame({
        'A_norm': normalized[:, 0],
        'B_norm': normalized[:, 1],
        'C_norm': normalized[:, 2]
    })

# Apply vectorized UDF
normalized_df = spark_df.select(
    normalize_columns('A', 'B', 'C').alias('normalized')
).select(
    'normalized.*'  # Expand struct into separate columns
)

# Grouped aggregation with NumPy in Pandas UDF
@pandas_udf('double')
def group_zscore(v: pd.Series) -> float:
    """Calculate z-score for values within each group"""
    return (v - v.mean()) / v.std() if v.std() > 0 else 0.0

# Apply to grouped data
result_df = spark_df.groupBy('E').agg(
    group_zscore('A').alias('A_zscore')
)
```

### PySpark ML with NumPy

```python
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.stat import Correlation
from pyspark.ml.feature import PCA
from pyspark.ml.clustering import KMeans
import numpy as np

# Create a feature vector column from individual features
assembler = VectorAssembler(
    inputCols=['A', 'B', 'C', 'D', 'E'],
    outputCol='features'
)
vector_df = assembler.transform(
