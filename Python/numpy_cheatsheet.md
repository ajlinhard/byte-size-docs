# NumPy Comprehensive Cheatsheet

## Table of Contents
1. [Introduction](#introduction)
2. [Arrays Creation](#arrays-creation)
3. [Array Indexing and Slicing](#array-indexing-and-slicing)
4. [Array Manipulation](#array-manipulation)
5. [Mathematical Operations](#mathematical-operations)
6. [Linear Algebra](#linear-algebra)
7. [Statistical Functions](#statistical-functions)
8. [Random Number Generation](#random-number-generation)
9. [NumPy with Pandas](#numpy-with-pandas)
10. [NumPy with PySpark](#numpy-with-pyspark)
11. [Advanced Techniques](#advanced-techniques)

## Introduction

NumPy is the fundamental package for scientific computing in Python. It provides:
- A powerful N-dimensional array object
- Sophisticated broadcasting functions
- Tools for integrating C/C++ code
- Linear algebra, Fourier transform, and random number capabilities

```python
import numpy as np
```

## Arrays Creation

### Basic Arrays

```python
# 1D array
arr1 = np.array([1, 2, 3, 4, 5])

# 2D array
arr2 = np.array([[1, 2, 3], [4, 5, 6]])

# 3D array
arr3 = np.array([[[1, 2], [3, 4]], [[5, 6], [7, 8]]])

# Check dimensions
print(arr1.ndim)  # 1
print(arr2.ndim)  # 2
print(arr3.ndim)  # 3

# Check shape
print(arr1.shape)  # (5,)
print(arr2.shape)  # (2, 3)
print(arr3.shape)  # (2, 2, 2)

# Get data type
print(arr1.dtype)  # int64
```

### Arrays with Specific Values

```python
# Zeros
zeros = np.zeros((2, 3))  # 2x3 array of zeros

# Ones
ones = np.ones((2, 3))  # 2x3 array of ones

# Full (filled with specific value)
full = np.full((2, 3), 7)  # 2x3 array of 7's

# Identity matrix
identity = np.eye(3)  # 3x3 identity matrix

# Diagonal matrix
diag = np.diag([1, 2, 3, 4])  # Diagonal matrix with values [1, 2, 3, 4]

# Empty (uninitialized, values depend on memory state)
empty = np.empty((2, 3))
```

### Sequences and Ranges

```python
# Evenly spaced values within a given interval
arange = np.arange(0, 10, 2)  # [0, 2, 4, 6, 8]

# Evenly spaced numbers over a specified interval
linspace = np.linspace(0, 1, 5)  # [0., 0.25, 0.5, 0.75, 1.]

# Logarithmic spaced numbers
logspace = np.logspace(0, 2, 5)  # [1., 3.16227766, 10., 31.6227766, 100.]

# Meshgrid (creates coordinate matrices from coordinate vectors)
x = np.array([1, 2, 3])
y = np.array([4, 5, 6])
xx, yy = np.meshgrid(x, y)
# xx = [[1, 2, 3], [1, 2, 3], [1, 2, 3]]
# yy = [[4, 4, 4], [5, 5, 5], [6, 6, 6]]
```

### Creating Arrays from Existing Data

```python
# Copy an array
arr_copy = np.copy(arr1)

# Create view (shares memory with original array)
arr_view = arr1.view()

# Create from list
list_data = [1, 2, 3, 4]
arr_from_list = np.asarray(list_data)

# Create from file
arr_from_file = np.loadtxt('data.txt')  # Load from text file
arr_from_csv = np.genfromtxt('data.csv', delimiter=',')  # Load from CSV
```

## Array Indexing and Slicing

### Basic Indexing

```python
# 1D array indexing
arr = np.array([1, 2, 3, 4, 5])
print(arr[0])     # 1 (first element)
print(arr[-1])    # 5 (last element)

# 2D array indexing
arr2d = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
print(arr2d[0, 0])   # 1 (first row, first column)
print(arr2d[1, 2])   # 6 (second row, third column)
print(arr2d[0])      # [1, 2, 3] (first row)
```

### Slicing

```python
# 1D slicing
arr = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
print(arr[2:5])       # [2, 3, 4]
print(arr[:5])        # [0, 1, 2, 3, 4]
print(arr[5:])        # [5, 6, 7, 8, 9]
print(arr[::2])       # [0, 2, 4, 6, 8] (every second element)
print(arr[::-1])      # [9, 8, 7, 6, 5, 4, 3, 2, 1, 0] (reversed)

# 2D slicing
arr2d = np.array([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]])
print(arr2d[:2, 1:3])  # [[2, 3], [6, 7]] (first two rows, columns 1-2)
print(arr2d[:, 1])     # [2, 6, 10] (all rows, column 1)
print(arr2d[1, :])     # [5, 6, 7, 8] (row 1, all columns)
```

### Advanced Indexing

```python
# Boolean indexing
arr = np.array([1, 2, 3, 4, 5])
mask = arr > 2
print(mask)         # [False, False, True, True, True]
print(arr[mask])    # [3, 4, 5]
print(arr[arr > 2]) # [3, 4, 5]

# Fancy indexing
arr = np.array([10, 20, 30, 40, 50])
indices = np.array([1, 3, 4])
print(arr[indices])  # [20, 40, 50]

# Combined indexing
arr2d = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
rows = np.array([0, 2])
cols = np.array([0, 2])
print(arr2d[rows[:, np.newaxis], cols])  # [[1, 3], [7, 9]]
```

## Array Manipulation

### Reshaping

```python
# Reshape
arr = np.arange(12)
reshaped = arr.reshape(3, 4)  # Reshape to 3x4 array
reshaped2 = arr.reshape(2, -1)  # Reshape to 2 rows, columns automatically calculated

# Flatten and ravel
flattened = reshaped.flatten()  # Creates a copy
raveled = reshaped.ravel()      # Returns a view when possible

# Transpose
transposed = reshaped.T  # Transpose rows and columns
```

### Joining and Splitting

```python
# Joining arrays
a = np.array([[1, 2], [3, 4]])
b = np.array([[5, 6], [7, 8]])

# Stack vertically
vertical = np.vstack((a, b))
# [[1, 2], [3, 4], [5, 6], [7, 8]]

# Stack horizontally
horizontal = np.hstack((a, b))
# [[1, 2, 5, 6], [3, 4, 7, 8]]

# Deep stack (along new axis)
deep = np.dstack((a, b))
# [[[1, 5], [2, 6]], [[3, 7], [4, 8]]]

# Concatenate (more general)
concat1 = np.concatenate((a, b), axis=0)  # Same as vstack
concat2 = np.concatenate((a, b), axis=1)  # Same as hstack

# Splitting arrays
arr = np.arange(16).reshape(4, 4)

# Split horizontally
hsplit = np.hsplit(arr, 2)  # Split into 2 arrays horizontally
# [array([[ 0,  1], [ 4,  5], [ 8,  9], [12, 13]]), 
#  array([[ 2,  3], [ 6,  7], [10, 11], [14, 15]])]

# Split vertically
vsplit = np.vsplit(arr, 2)  # Split into 2 arrays vertically
# [array([[0, 1, 2, 3], [4, 5, 6, 7]]), 
#  array([[ 8,  9, 10, 11], [12, 13, 14, 15]])]

# Array split (more general)
split1 = np.array_split(arr, 3)  # Split into 3 arrays (not equal sizes)
```

### Adding and Removing Elements

```python
# Append
arr = np.array([1, 2, 3, 4])
appended = np.append(arr, [5, 6, 7])  # [1, 2, 3, 4, 5, 6, 7]

# Insert
inserted = np.insert(arr, 1, 99)  # [1, 99, 2, 3, 4]
inserted_multi = np.insert(arr, [1, 3], [99, 88])  # [1, 99, 2, 3, 88, 4]

# Delete
deleted = np.delete(arr, 1)  # [1, 3, 4]
deleted_multi = np.delete(arr, [1, 3])  # [1, 3]

# Resize
resized = np.resize(arr, (2, 3))  # Resize to shape (2, 3), recycling values if needed
```

### Broadcasting

```python
# Broadcasting allows NumPy to work with arrays of different shapes
arr = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])

# Add scalar
result1 = arr + 10  # Adds 10 to each element

# Add vector to each row
row_vector = np.array([10, 20, 30])
result2 = arr + row_vector  # [[11, 22, 33], [14, 25, 36], [17, 28, 39]]

# Add vector to each column
col_vector = np.array([[10], [20], [30]])
result3 = arr + col_vector  # [[11, 12, 13], [24, 25, 26], [37, 38, 39]]
```

## Mathematical Operations

### Element-wise Operations

```python
a = np.array([1, 2, 3, 4])
b = np.array([5, 6, 7, 8])

# Addition
add = a + b  # [6, 8, 10, 12]
add_func = np.add(a, b)  # Same as a + b

# Subtraction
sub = a - b  # [-4, -4, -4, -4]
sub_func = np.subtract(a, b)  # Same as a - b

# Multiplication
mul = a * b  # [5, 12, 21, 32]
mul_func = np.multiply(a, b)  # Same as a * b

# Division
div = a / b  # [0.2, 0.33333333, 0.42857143, 0.5]
div_func = np.divide(a, b)  # Same as a / b

# Integer division
idiv = a // b  # [0, 0, 0, 0]
idiv_func = np.floor_divide(a, b)  # Same as a // b

# Modulus
mod = a % b  # [1, 2, 3, 4]
mod_func = np.mod(a, b)  # Same as a % b

# Power
pow = a ** 2  # [1, 4, 9, 16]
pow_func = np.power(a, 2)  # Same as a ** 2
```

### Universal Functions (ufuncs)

```python
# Trigonometric functions
angles = np.array([0, np.pi/4, np.pi/2, np.pi])
sin_vals = np.sin(angles)  # [0.0, 0.70710678, 1.0, 0.0]
cos_vals = np.cos(angles)  # [1.0, 0.70710678, 0.0, -1.0]
tan_vals = np.tan(angles)  # [0.0, 1.0, 16331239353195370.0, -0.0]

# Exponential and logarithmic functions
exp_vals = np.exp(np.array([0, 1, 2]))  # [1.0, 2.71828183, 7.3890561]
log_vals = np.log(np.array([1, np.e, np.e**2]))  # [0.0, 1.0, 2.0]
log10_vals = np.log10(np.array([1, 10, 100]))  # [0.0, 1.0, 2.0]
log2_vals = np.log2(np.array([1, 2, 4]))  # [0.0, 1.0, 2.0]

# Rounding
a = np.array([1.2, 1.5, 1.7, 2.2])
rounded = np.round(a)  # [1.0, 2.0, 2.0, 2.0]
ceil_vals = np.ceil(a)  # [2.0, 2.0, 2.0, 3.0]
floor_vals = np.floor(a)  # [1.0, 1.0, 1.0, 2.0]
```

### Aggregation Functions

```python
arr = np.array([[1, 2, 3], [4, 5, 6]])

# Sum
total = np.sum(arr)  # 21
row_sum = np.sum(arr, axis=1)  # [6, 15]
col_sum = np.sum(arr, axis=0)  # [5, 7, 9]

# Product
prod = np.prod(arr)  # 720
row_prod = np.prod(arr, axis=1)  # [6, 120]
col_prod = np.prod(arr, axis=0)  # [4, 10, 18]

# Min/Max
min_val = np.min(arr)  # 1
max_val = np.max(arr)  # 6
row_min = np.min(arr, axis=1)  # [1, 4]
col_max = np.max(arr, axis=0)  # [4, 5, 6]

# Index of min/max
argmin_val = np.argmin(arr)  # 0 (flattened index)
argmax_val = np.argmax(arr)  # 5 (flattened index)
row_argmin = np.argmin(arr, axis=1)  # [0, 0]
col_argmax = np.argmax(arr, axis=0)  # [1, 1, 1]

# Cumulative operations
cumsum = np.cumsum(arr)  # [1, 3, 6, 10, 15, 21]
cumprod = np.cumprod(arr)  # [1, 2, 6, 24, 120, 720]
row_cumsum = np.cumsum(arr, axis=1)  # [[1, 3, 6], [4, 9, 15]]
```

## Linear Algebra

```python
# Matrix multiplication
a = np.array([[1, 2], [3, 4]])
b = np.array([[5, 6], [7, 8]])

dot_product = np.dot(a, b)  # [[19, 22], [43, 50]]
matmul = a @ b  # Same as np.dot for 2D arrays

# Outer product
outer = np.outer([1, 2, 3], [4, 5])  # [[4, 5], [8, 10], [12, 15]]

# Inner product
inner = np.inner([1, 2, 3], [4, 5, 6])  # 32 (1*4 + 2*5 + 3*6)

# Cross product
cross = np.cross([1, 2, 3], [4, 5, 6])  # [-3, 6, -3]

# Determinant
det = np.linalg.det(a)  # -2.0

# Matrix inverse
inv = np.linalg.inv(a)  # [[-2.0, 1.0], [1.5, -0.5]]

# Eigenvalues and eigenvectors
eigenvals, eigenvecs = np.linalg.eig(a)

# Solve linear equations Ax = b
A = np.array([[1, 2], [3, 4]])
b = np.array([5, 6])
x = np.linalg.solve(A, b)  # [-4.,  4.5]

# Moore-Penrose pseudo-inverse (for non-square matrices)
A = np.array([[1, 2, 3], [4, 5, 6]])
pinv = np.linalg.pinv(A)

# SVD decomposition
U, S, Vh = np.linalg.svd(A)

# QR decomposition
q, r = np.linalg.qr(A)

# Matrix norm
norm = np.linalg.norm(A)  # Frobenius norm by default
```

## Statistical Functions

```python
data = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

# Basic statistics
mean = np.mean(data)  # 5.5
median = np.median(data)  # 5.5
var = np.var(data)  # 8.25 (variance)
std = np.std(data)  # 2.8722813232690143 (standard deviation)
min_val = np.min(data)  # 1
max_val = np.max(data)  # 10
ptp = np.ptp(data)  # 9 (peak-to-peak, max - min)

# Percentiles and quantiles
percentile_25 = np.percentile(data, 25)  # 3.25 (25th percentile)
percentile_75 = np.percentile(data, 75)  # 7.75 (75th percentile)
quantile_25 = np.quantile(data, 0.25)  # 3.25 (same as 25th percentile)

# Histogram
hist, bin_edges = np.histogram(data, bins=5)
# hist: [2, 2, 2, 2, 2] (count in each bin)
# bin_edges: [1., 2.8, 4.6, 6.4, 8.2, 10.] (bin boundaries)

# Correlation and covariance
a = np.array([1, 2, 3, 4])
b = np.array([4, 3, 2, 1])
correlation = np.corrcoef(a, b)  # 2x2 correlation matrix, [1, -1; -1, 1]
covariance = np.cov(a, b)  # 2x2 covariance matrix

# Weighted average
weights = np.array([0.1, 0.2, 0.3, 0.4])
weighted_avg = np.average(data[:4], weights=weights)  # 3.0
```

## Random Number Generation

```python
# Set random seed for reproducibility
np.random.seed(42)

# Random integers
random_int = np.random.randint(1, 100, size=5)  # 5 random integers from 1 to 99

# Random floats (uniform distribution)
random_uniform = np.random.rand(3, 3)  # 3x3 array of random floats in [0,1)
random_uniform2 = np.random.uniform(0, 10, size=5)  # 5 random floats in [0,10)

# Random floats (normal/Gaussian distribution)
random_normal = np.random.randn(3, 3)  # 3x3 array from standard normal distribution
random_normal2 = np.random.normal(loc=5, scale=2, size=5)  # mean=5, std=2

# Random choice from array
choices = np.random.choice([1, 2, 3, 4], size=10)  # with replacement
choices_no_replace = np.random.choice([1, 2, 3, 4], size=3, replace=False)  # no replacement
weighted_choices = np.random.choice([1, 2, 3], size=10, p=[0.1, 0.3, 0.6])  # with probabilities

# Shuffle array
arr = np.arange(10)
np.random.shuffle(arr)  # Shuffles in-place

# Permutation
permutation = np.random.permutation(10)  # Returns a shuffled array

# Generate samples from distributions
poisson_samples = np.random.poisson(lam=5, size=10)  # Poisson distribution
binomial_samples = np.random.binomial(n=10, p=0.5, size=10)  # Binomial distribution
exponential_samples = np.random.exponential(scale=1.0, size=10)  # Exponential distribution
```

## NumPy with Pandas

### Converting Between NumPy and Pandas

```python
import pandas as pd

# NumPy array to Pandas DataFrame
arr = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
df = pd.DataFrame(arr, columns=['A', 'B', 'C'])

# NumPy array to Pandas Series
series = pd.Series(np.array([1, 2, 3, 4]))

# Pandas DataFrame to NumPy array
arr_from_df = df.to_numpy()
arr_from_df_values = df.values  # Deprecated but still works

# Pandas Series to NumPy array
arr_from_series = series.to_numpy()
arr_from_series_values = series.values  # Deprecated but still works
```

### Operations with NumPy and Pandas

```python
# Apply NumPy functions to DataFrame
df = pd.DataFrame(np.random.randn(5, 3), columns=['A', 'B', 'C'])

# Element-wise operations
df_sin = np.sin(df)
df_log = np.log(np.abs(df))

# Aggregation with NumPy functions
col_means = np.mean(df, axis=0)  # Mean of each column
row_sums = np.sum(df, axis=1)    # Sum of each row

# Use NumPy functions directly on DataFrame
df_norm = df / np.linalg.norm(df)

# Using NumPy's where with Pandas
df_filtered = df.where(df > 0, np.nan)  # Replace values <= 0 with NaN

# Vectorized calculations
df['D'] = np.sqrt(np.sum(df**2, axis=1))  # Calculate Euclidean norm as new column
```

### Advanced Pandas with NumPy

```python
# Create multi-dimensional arrays from Panel data
dates = pd.date_range('20230101', periods=6)
df = pd.DataFrame(np.random.randn(6, 4), index=dates, columns=list('ABCD'))

# Reshaping with NumPy
stacked = df.stack().to_numpy().reshape((6, 2, 2))

# Custom aggregations with NumPy
df.groupby('A').agg(
    custom_metric=('B', lambda x: np.sqrt(np.mean(x**2)))
)

# Using NumPy's masked arrays with Pandas
import numpy.ma as ma
masked_arr = ma.masked_where(df.to_numpy() < 0, df.to_numpy())
df_masked = pd.DataFrame(masked_arr, index=df.index, columns=df.columns)

# Time-series operations
df_returns = np.log(df / df.shift(1))  # Log returns
df_volatility = df_returns.rolling(window=5).apply(np.std)  # Rolling volatility
```

## NumPy with PySpark

### Converting Between NumPy and PySpark

```python
from pyspark.sql import SparkSession
import pyspark.sql.functions as F
from pyspark.ml.linalg import Vectors
import numpy as np

# Initialize SparkSession
spark = SparkSession.builder.getOrCreate()

# NumPy array to PySpark DataFrame
arr = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
df = spark.createDataFrame(
    [(arr[i, 0], arr[i, 1], arr[i, 2]) for i in range(arr.shape[0])],
    ["col1", "col2", "col3"]
)

# PySpark DataFrame to NumPy array
pandas_df = df.toPandas()
arr_from_spark = pandas_df.to_numpy()

# Create PySpark vectors from NumPy arrays
dense_vectors = spark.createDataFrame(
    [(Vectors.dense(row),) for row in arr],
    ["features"]
)
```

### PySpark UDFs with NumPy

```python
import pyspark.sql.functions as F
from pyspark.sql.types import ArrayType, DoubleType
import numpy as np

# Create NumPy-powered UDFs
@F.udf(returnType=ArrayType(DoubleType()))
def normalize_vector(vec):
    # Convert to NumPy array
    np_vec = np.array(vec)
    # Normalize
    norm = np.linalg.norm(np_vec)
    if norm == 0:
        return vec
    return (np_vec / norm).tolist()  # Convert back to Python list

# Apply UDF to DataFrame
df_with_features = spark.createDataFrame([
    ([1.0, 2.0, 3.0],),
    ([4.0, 5.0, 6.0],),
    ([7.0, 8.0, 9.0],)
], ["features"])

normalized_df = df_with_features.withColumn(
    "normalized_features",
    normalize_vector(F.col("features"))
)
```

### PySpark ML with NumPy

```python
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.stat import Correlation
import numpy as np

# Create a DataFrame with features
data = [(np.array([1.0, 2.0, 3.0]),),
        (np.array([4.0, 5.0, 6.0]),),
        (np.array([7.0, 8.0, 9.0]),)]
df = spark.createDataFrame(data, ["features"])

# Calculate correlation matrix
corr_matrix = Correlation.corr(df, "features").collect()[0][0]
np_corr_matrix = np.array(corr_matrix.toArray())  # Convert to NumPy array

# Work with the correlation matrix using NumPy
eigenvalues, eigenvectors = np.linalg.eig(np_corr_matrix)
```

## Advanced Techniques

### Vectorization

```python
# Always prefer vectorized operations over loops!

# Bad (slow) approach
def slow_distance(points):
    n = len(points)
    result = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            delta = points[i] - points[j]
            result[i, j] = np.sqrt(np.sum(delta**2))
    return result

# Good (fast) vectorized approach
def fast_distance(points):
    # Broadcasting to calculate pairwise distances
    diff = points[:, np.newaxis, :] - points[np.newaxis, :, :]
    return np.sqrt(np.sum(diff**2, axis=2))

# Example usage
points = np.random.rand(1000, 3)  # 1000 3D points
# fast_distance(points) is MUCH faster than slow_distance(points)
```

### Memory Management

```python
# Check memory usage
arr = np.ones((1000, 1000), dtype=np.float64)
size_bytes = arr.nbytes  # 8000000 bytes (8MB)

# Change data type to save memory
arr_small = np.ones((1000, 1000), dtype=np.float32)  # 4MB instead of 8MB

# View vs. Copy
a = np.arange(10)
b = a  # b is a view of a (shares memory)
b[0] = 99  # Changes a[0] as well
print(a[0])  # 99

c = a.copy()  # c is a copy of a (separate memory)
c[0] = 42  # Doesn't change a[0]
print(a[0])  # Still 99

# Using np.ascontiguousarray for faster operations
non_contig = np.ones((100, 100), order='F')  # Column-major order
contig = np.ascontiguousarray(non_contig)    # Convert to row-major for faster operations
```

### Masked Arrays

```python
# Create a masked array to handle missing values
data = np.array([1, 2, -999, 4, 5, -999, 7])
mask = data == -999  # [False, False, True, False, False, True, False]
masked_data = np.ma.masked_array(data, mask=mask)

# Operations automatically ignore masked values
mean = np.ma.mean(masked_data)  # 3.8 (ignores -999 values)
std = np.ma.std(masked_data)    # 2.135 (ignores -999 values)

# Fill masked values
filled_data = masked_data.filled(0)  # Replace masked values with 0
```

### Structured Arrays

```python
# Create structured array (similar to a table with named columns)
dt = np.dtype([('name', 'U10'), ('age', 'i4'), ('weight', 'f4')])