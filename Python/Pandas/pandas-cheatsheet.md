# Pandas Cheatsheet - From Basics to Advanced

### Helpful Links:
- [Pandas User Guides](https://pandas.pydata.org/docs/user_guide/10min.html#time-series)
    - [10 Minutes to Pandas](https://pandas.pydata.org/docs/user_guide/10min.html)
    - [Group By Overview](https://pandas.pydata.org/docs/user_guide/groupby.html)
    - [Table Visualizations](https://pandas.pydata.org/docs/user_guide/style.html)
- [Pandas Compared to SQL](https://pandas.pydata.org/docs/getting_started/comparison/comparison_with_sql.html#)
- [Pandas API](https://pandas.pydata.org/docs/reference/index.html)
- [Pandas Ecosystem](https://pandas.pydata.org/community/ecosystem.html#out-of-core)


## Table of Contents
- [Installation and Setup](#installation-and-setup)
- [Basic Data Structures](#basic-data-structures)
- [Data Import and Export](#data-import-and-export)
- [Data Inspection](#data-inspection)
- [Data Selection](#data-selection)
- [Data Cleaning](#data-cleaning)
- [Data Manipulation](#data-manipulation)
- [Data Aggregation](#data-aggregation)
- [Time Series Operations](#time-series-operations)
- [Merging and Joining](#merging-and-joining)
- [Advanced Operations](#advanced-operations)
- [Performance Tips](#performance-tips)

## Installation and Setup

```python
# Install pandas
pip install pandas

# Import standard libraries
import pandas as pd
import numpy as np
```

## Basic Data Structures

### Series
A one-dimensional labeled array capable of holding any data type.

```python
# Create a Series from a list
s = pd.Series([1, 3, 5, np.nan, 6, 8])

# Create a Series with custom index
s = pd.Series([1, 3, 5, 6, 8], index=['a', 'b', 'c', 'd', 'e'])

# Create a Series from a dictionary
d = {'a': 1, 'b': 2, 'c': 3}
s = pd.Series(d)

# Access elements
value = s['a']    # Access by label
value = s[0]      # Access by position
```

### DataFrame
A two-dimensional labeled data structure with columns of potentially different types.

```python
# Create a DataFrame from a dictionary of Series
df = pd.DataFrame({
    'A': pd.Series([1, 2, 3]),
    'B': pd.Series([4, 5, 6])
})

# Create a DataFrame from a dictionary of lists
df = pd.DataFrame({
    'A': [1, 2, 3],
    'B': [4, 5, 6]
})

# Create a DataFrame from a list of lists
df = pd.DataFrame([
    [1, 4],
    [2, 5],
    [3, 6]
], columns=['A', 'B'])

# Create a DataFrame with a DatetimeIndex
df = pd.DataFrame({
    'A': [1, 2, 3],
    'B': [4, 5, 6]
}, index=pd.date_range('20230101', periods=3))
```

## Data Import and Export

### Reading Data

```python
# CSV
df = pd.read_csv('file.csv')
df = pd.read_csv('file.csv', index_col=0)  # Use first column as index
df = pd.read_csv('file.csv', header=None)  # No header row
df = pd.read_csv('file.csv', skiprows=2)   # Skip first 2 rows
df = pd.read_csv('file.csv', nrows=10)     # Read only 10 rows

# Excel
df = pd.read_excel('file.xlsx', sheet_name='Sheet1')

# JSON
df = pd.read_json('file.json')

# SQL
from sqlalchemy import create_engine
engine = create_engine('sqlite:///database.db')
df = pd.read_sql('SELECT * FROM table', engine)
df = pd.read_sql_table('table_name', engine)
df = pd.read_sql_query('SELECT * FROM table', engine)

# HTML Tables
df_list = pd.read_html('https://example.com/tables.html')
```

### Writing Data

```python
# CSV
df.to_csv('output.csv')
df.to_csv('output.csv', index=False)  # Don't write index

# Excel
df.to_excel('output.xlsx', sheet_name='Sheet1')

# JSON
df.to_json('output.json')

# SQL
df.to_sql('table_name', engine, if_exists='replace')
```

## Data Inspection

```python
# Basic dataframe info
df.shape       # Dimensions (rows, columns)
df.dtypes      # Column data types
df.info()      # Concise summary
df.describe()  # Statistical summary of numeric columns
df.describe(include='all')  # Summary of all columns

# Viewing data
df.head(n)     # First n rows (default 5)
df.tail(n)     # Last n rows (default 5)
df.sample(n)   # Random sample of n rows
df.columns     # Column labels
df.index       # Row labels

# Values
df.values      # Get numpy array of values
df.to_numpy()  # Convert to numpy array (preferred)

# Check for missing values
df.isna()      # Return boolean mask of NaN values
df.isnull()    # Alias for isna()
df.isna().sum()  # Count of NaN values in each column
```

## Data Selection

### Basic Selection

```python
# Selecting columns
df['A']        # Select single column (returns Series)
df[['A', 'B']]  # Select multiple columns (returns DataFrame)

# Selecting rows by position
df.iloc[0]     # First row (returns Series)
df.iloc[0:3]   # First three rows
df.iloc[[0, 2, 5]]  # Specific rows by position
df.iloc[0:3, 1:3]  # Rows 0-2, columns 1-2

# Selecting rows by label
df.loc['a']    # Row with label 'a'
df.loc['a':'c']  # Rows with labels 'a' to 'c'
df.loc[['a', 'c', 'd']]  # Specific rows by label

# Selecting both rows and columns by label
df.loc['a':'c', 'A':'C']  # Rows 'a'-'c', columns 'A'-'C'
```

### Boolean Indexing

```python
# Filter rows based on column value
df[df['A'] > 0]  # Rows where column A > 0
df[df['A'].isin([1, 2, 3])]  # Rows where A is in list
df[(df['A'] > 0) & (df['B'] < 10)]  # Multiple conditions with &
df[(df['A'] > 0) | (df['B'] < 10)]  # OR condition with |
```

### Advanced Selection

```python
# Query method for more readable filtering
df.query('A > 0 and B < 10')
df.query('A in [1, 2, 3]')

# Using str accessors for string operations
df[df['name'].str.contains('John')]
df[df['name'].str.startswith('J')]
df[df['name'].str.len() > 5]

# Using dt accessors for datetime operations
df[df['date'].dt.year == 2023]
df[df['date'].dt.month == 1]
```

## Data Cleaning

### Handling Missing Values

```python
# Check for missing values
df.isna().sum()  # Count of NaN values by column
df.isna().any()  # Check if any values are NaN in each column

# Drop missing values
df.dropna()      # Drop rows with any NaN values
df.dropna(axis=1)  # Drop columns with any NaN values
df.dropna(how='all')  # Drop rows where all values are NaN
df.dropna(thresh=2)  # Keep rows with at least 2 non-NaN values

# Fill missing values
df.fillna(0)     # Replace NaN with 0
df.fillna({'A': 0, 'B': 1})  # Replace NaN with different values by column
df.fillna(method='ffill')  # Forward fill (use previous value)
df.fillna(method='bfill')  # Backward fill (use next value)

# Interpolate missing values
df.interpolate()  # Linear interpolation
df.interpolate(method='polynomial', order=2)  # Polynomial interpolation
```

### Data Type Conversion

```python
# Convert data types
df['A'] = df['A'].astype('int64')
df['B'] = df['B'].astype('float64')
df['C'] = df['C'].astype('str')
df['D'] = df['D'].astype('category')

# Convert to datetime
df['date'] = pd.to_datetime(df['date'])
df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
df['date'] = pd.to_datetime(df['date'], errors='coerce')  # Invalid dates become NaT
```

### Removing Duplicates

```python
# Check for duplicates
df.duplicated()  # Boolean mask of duplicate rows
df.duplicated().sum()  # Count of duplicate rows

# Drop duplicates
df.drop_duplicates()  # Drop duplicate rows
df.drop_duplicates(subset=['A', 'B'])  # Consider only these columns
df.drop_duplicates(keep='last')  # Keep last occurrence
df.drop_duplicates(keep=False)  # Drop all duplicates
```

### String Operations

```python
# Apply string methods to a string column
df['name'] = df['name'].str.lower()
df['name'] = df['name'].str.upper()
df['name'] = df['name'].str.strip()
df['name'] = df['name'].str.replace('old', 'new')
df['name'] = df['name'].str.replace(r'^old.*$', 'new', regex=True)

# Split strings
df['first_name'] = df['name'].str.split(' ').str[0]
df[['first', 'last']] = df['name'].str.split(' ', expand=True)
```

## Data Manipulation

### Adding/Removing Columns

```python
# Add a new column
df['C'] = df['A'] + df['B']
df['D'] = 10
df.assign(E=df['A'] + 10, F=lambda x: x['A'] * 2)

# Delete columns
df.drop('C', axis=1)  # Drop single column
df.drop(['C', 'D'], axis=1)  # Drop multiple columns
del df['C']  # Delete using Python's del

# Rename columns
df.rename(columns={'A': 'a', 'B': 'b'})
df.columns = ['a', 'b', 'c']  # Rename all columns
```

### Adding/Removing Rows

```python
# Append rows
df2 = pd.DataFrame([[5, 6], [7, 8]], columns=['A', 'B'])
df = pd.concat([df, df2])

# Reset index
df.reset_index()  # Keep old index as column
df.reset_index(drop=True)  # Drop old index

# Drop rows
df.drop(0)  # Drop row by index
df.drop([0, 1])  # Drop multiple rows
```

### Apply Functions

```python
# Apply to columns (Series)
df['A'].apply(lambda x: x * 2)
df['A'].map({1: 'one', 2: 'two'})
df['A'].map(lambda x: x * 2)

# Apply to entire DataFrame
df.apply(lambda x: x * 2)
df.apply(lambda x: x.max() - x.min())
df.apply(np.square)

# Apply elementwise
df.applymap(lambda x: f"{x:.2f}" if isinstance(x, (int, float)) else x)
```

### Sorting

```python
# Sort by values
df.sort_values('A')  # Sort by column A
df.sort_values(['A', 'B'])  # Sort by multiple columns
df.sort_values('A', ascending=False)  # Sort descending

# Sort by index
df.sort_index()  # Sort by row labels
df.sort_index(axis=1)  # Sort by column labels
```

## Data Aggregation

### Basic Aggregation

```python
# Single aggregation
df['A'].sum()
df['A'].mean()
df['A'].median()
df['A'].min()
df['A'].max()
df['A'].std()
df['A'].var()
df['A'].count()  # Count non-NA values

# Multiple aggregations at once
df.agg(['sum', 'mean', 'max'])
df.agg({'A': ['sum', 'mean'], 'B': ['min', 'max']})
```

### Groupby Operations

```python
# Group by one column
grouped = df.groupby('A')
grouped.sum()
grouped.mean()
grouped.describe()

# Group by multiple columns
grouped = df.groupby(['A', 'B'])
grouped.sum()

# Access a specific group
grouped.get_group('group_name')

# Apply functions to groups
grouped.apply(lambda x: x.max() - x.min())
grouped.transform(lambda x: (x - x.mean()) / x.std())

# Custom aggregation
grouped.agg({'C': 'sum', 'D': 'mean'})
grouped.agg({
    'C': ['sum', 'mean', 'std'],
    'D': ['min', 'max']
})
```

### Pivot Tables

```python
# Simple pivot table
pivot = pd.pivot_table(df, values='D', index='A', columns='B', aggfunc='mean')

# Multi-level pivot table
pivot = pd.pivot_table(
    df,
    values=['D', 'E'],
    index=['A', 'B'],
    columns='C',
    aggfunc={'D': 'sum', 'E': 'mean'}
)

# Reshape using melt (opposite of pivot)
melted = pd.melt(df, id_vars=['A'], value_vars=['B', 'C'])
```

## Time Series Operations

### Date Ranges and Shifting

```python
# Create date ranges
dates = pd.date_range('20230101', periods=6)  # Daily frequency (default)
dates = pd.date_range('20230101', periods=6, freq='M')  # Monthly
dates = pd.date_range('20230101', periods=6, freq='H')  # Hourly
dates = pd.date_range('20230101', periods=6, freq='B')  # Business days

# Shift data
df.shift(1)  # Shift values down 1 row (forward in time)
df.shift(-1)  # Shift values up 1 row (backward in time)
df.shift(1, freq='D')  # Shift the index
```

### Resampling Time Series

```python
# Downsample to less frequent
df.resample('D').mean()  # Daily average
df.resample('M').sum()   # Monthly sum

# Upsample to more frequent
df.resample('H').ffill()  # Hourly, forward fill
df.resample('T').bfill()  # Minutely, backward fill

# Resampling with custom aggregation
df.resample('D').agg(['min', 'max', 'mean'])
```

### Rolling Windows

```python
# Rolling mean (moving average)
df.rolling(window=3).mean()
df.rolling(window=3, min_periods=1).mean()  # Include window with at least 1 value

# Rolling with custom function
df.rolling(window=3).apply(lambda x: x.max() - x.min())

# Expanding windows (cumulative)
df.expanding().mean()  # Cumulative mean
df.expanding().sum()   # Cumulative sum
```

## Merging and Joining

### Concatenation

```python
# Concatenate DataFrames
pd.concat([df1, df2])  # Vertically (rows)
pd.concat([df1, df2], axis=1)  # Horizontally (columns)
pd.concat([df1, df2], ignore_index=True)  # Reset index
pd.concat([df1, df2], keys=['df1', 'df2'])  # Create hierarchical index
```

### Merge and Join

```python
# Inner join (only matching keys)
pd.merge(df1, df2, on='key')
pd.merge(df1, df2, left_on='key1', right_on='key2')

# Outer join (all keys)
pd.merge(df1, df2, on='key', how='outer')

# Left join (all keys from left)
pd.merge(df1, df2, on='key', how='left')

# Right join (all keys from right)
pd.merge(df1, df2, on='key', how='right')

# Join on index
df1.join(df2)
df1.join(df2, how='outer')
```

## Advanced Operations

### Categorical Data

```python
# Convert to category
df['category'] = df['category'].astype('category')

# Create ordered category
df['size'] = pd.Categorical(
    df['size'],
    categories=['small', 'medium', 'large'],
    ordered=True
)

# Categorical operations
df['size'] < 'medium'  # Compare ordered categories
df.groupby('category').mean()  # Group by category
```

### MultiIndex / Hierarchical Indexing

```python
# Create MultiIndex DataFrame
arrays = [
    ['A', 'A', 'B', 'B'],
    [1, 2, 1, 2]
]
index = pd.MultiIndex.from_arrays(arrays, names=('letter', 'number'))
df = pd.DataFrame({'value': [10, 20, 30, 40]}, index=index)

# Select from MultiIndex
df.loc[('A', 1)]  # Select specific index values
df.loc['A']       # Select all 'A' rows
df.xs('A')        # Cross-section by level
df.xs(1, level='number')  # Cross-section by level name

# Unstacking and stacking
df.unstack()  # Pivot last level to columns
df.stack()    # Pivot innermost columns to index
```

### Window Functions

```python
# Cumulative operations
df.cumsum()
df.cumprod()
df.cummax()
df.cummin()

# Percent change and diff
df.pct_change()  # Percentage change
df.diff()        # Absolute difference
```

### Advanced Data Cleaning

```python
# Replace values
df.replace(to_replace=0, value=np.nan)
df.replace({0: np.nan, -1: 0})
df.replace(r'^old', 'new', regex=True)

# Value counts and unique values
df['A'].value_counts()  # Count of each unique value
df['A'].value_counts(normalize=True)  # Proportions
df['A'].unique()  # Array of unique values
df['A'].nunique()  # Count of unique values

# Dealing with outliers
q1 = df['A'].quantile(0.25)
q3 = df['A'].quantile(0.75)
iqr = q3 - q1
df_filtered = df[(df['A'] >= q1 - 1.5*iqr) & (df['A'] <= q3 + 1.5*iqr)]
```

## Performance Tips

```python
# Use efficient data types
df['id'] = df['id'].astype('int32')  # Smaller integer type
df['category'] = df['category'].astype('category')  # Category for repeated strings

# Vectorized operations (faster than loops)
df['C'] = df['A'] + df['B']  # Instead of loops

# Use query() for complex filters
df.query('A > 0 and B < 10')  # Faster than df[(df['A'] > 0) & (df['B'] < 10)]

# Use inplace=True when appropriate
df.fillna(0, inplace=True)  # Modify df directly

# Optimize memory usage
df.info(memory_usage='deep')  # Check memory usage
df_int = df.select_dtypes(include=['int'])  # Select only int columns
df_int = df_int.apply(pd.to_numeric, downcast='integer')  # Downcast

# Use method chaining
result = (df
          .drop(['C', 'D'], axis=1)
          .fillna(0)
          .query('A > 0')
          .groupby('B')
          .agg({'A': ['mean', 'sum']})
         )
```
