# Pandas Work with NULL (aka NaN)
Below is a comprehensive pandas null handling cheatsheet that covers all the essential techniques you'll need for working with missing data. The cheatsheet includes:

**Key sections covered:**
- Understanding different null representations in pandas
- Detecting and counting null values
- Filtering data based on null values
- Various filling strategies (constants, statistics, forward/backward fill, interpolation)
- Handling nulls in different data types (numeric, categorical, datetime)
- Advanced techniques like conditional filling and creating null indicators
- Performance considerations and best practices
- Quick reference table for common operations

This cheatsheet should serve as a handy reference for all your null value handling needs in pandas. You can bookmark it and refer back to it whenever you're dealing with missing data in your DataFrames!
---
# Pandas Null Handling Cheatsheet

## Understanding Null Values in Pandas

Pandas uses several representations for missing data:
- `NaN` (Not a Number) - for numeric data
- `None` - Python's null object
- `pd.NA` - pandas extension array null value
- `pd.NaT` (Not a Time) - for datetime data

## Detecting Null Values

### Basic Detection
```python
# Check for null values
df.isnull()          # Returns boolean DataFrame
df.isna()            # Same as isnull()
df.notnull()         # Opposite of isnull()
df.notna()           # Same as notnull()

# Count null values
df.isnull().sum()              # Null count per column
df.isnull().sum().sum()        # Total null count
df.info()                      # Shows non-null count per column
```

### Advanced Detection
```python
# Check if entire DataFrame has any nulls
df.isnull().any().any()

# Check if specific column has nulls
df['column'].isnull().any()

# Get percentage of null values
(df.isnull().sum() / len(df)) * 100

# Find rows with any null values
df[df.isnull().any(axis=1)]

# Find rows with all null values
df[df.isnull().all(axis=1)]
```

## Filtering Based on Null Values

```python
# Drop rows with any null values
df.dropna()

# Drop rows with all null values
df.dropna(how='all')

# Drop rows with nulls in specific columns
df.dropna(subset=['col1', 'col2'])

# Drop columns with any null values
df.dropna(axis=1)

# Drop columns with more than 50% null values
df.dropna(axis=1, thresh=len(df)*0.5)

# Keep only rows with no null values
df[df.notnull().all(axis=1)]

# Keep only rows with null values in specific column
df[df['column'].isnull()]
```

## Filling Null Values

### Basic Filling
```python
# Fill with a constant value
df.fillna(0)                    # Fill all nulls with 0
df.fillna({'col1': 0, 'col2': 'Unknown'})  # Different values per column

# Fill with column statistics
df.fillna(df.mean())           # Fill with mean (numeric columns only)
df.fillna(df.median())         # Fill with median
df.fillna(df.mode().iloc[0])   # Fill with mode (first mode if multiple)
```

### Forward/Backward Fill
```python
# Forward fill (use previous value)
df.fillna(method='ffill')      # or method='pad'
df.fillna(method='ffill', limit=2)  # Limit to 2 consecutive fills

# Backward fill (use next value)
df.fillna(method='bfill')      # or method='backfill'

# Fill specific column only
df['column'].fillna(method='ffill')
```

### Interpolation
```python
# Linear interpolation
df.interpolate()

# Different interpolation methods
df.interpolate(method='polynomial', order=2)
df.interpolate(method='spline', order=3)
df.interpolate(method='time')  # For time series data

# Interpolate specific column
df['column'].interpolate()
```

## Replacing Values

```python
# Replace specific values with null
df.replace('', np.nan)         # Replace empty strings
df.replace([0, -999], np.nan)  # Replace multiple values
df.replace({'col1': {0: np.nan}})  # Replace in specific column

# Replace null with specific values
df.replace(np.nan, 'Missing')

# Replace using regex
df.replace(r'^\s*$', np.nan, regex=True)  # Replace whitespace-only strings
```

## Working with Different Data Types

### Numeric Data
```python
# Check for infinite values
df.isinf()
df.replace([np.inf, -np.inf], np.nan)

# Fill numeric nulls
df.fillna(df.mean())           # Mean imputation
df.fillna(df.median())         # Median imputation
df.fillna(0)                   # Zero imputation
```

### Categorical Data
```python
# Fill categorical nulls
df['category_col'].fillna('Unknown')
df['category_col'].fillna(df['category_col'].mode()[0])  # Most frequent

# Create "Missing" category
df['category_col'] = df['category_col'].cat.add_categories(['Missing'])
df['category_col'].fillna('Missing', inplace=True)
```

### DateTime Data
```python
# Fill datetime nulls
df['date_col'].fillna(pd.Timestamp('1900-01-01'))
df['date_col'].fillna(method='ffill')

# Check for NaT (Not a Time)
df['date_col'].isna()
```

## Advanced Null Handling Techniques

### Conditional Filling
```python
# Fill based on condition
df.loc[df['age'] < 18, 'income'] = df.loc[df['age'] < 18, 'income'].fillna(0)

# Fill using other columns
df['col1'].fillna(df['col2'], inplace=True)

# Fill with group statistics
df['value'] = df.groupby('group')['value'].transform(lambda x: x.fillna(x.mean()))
```

### Custom Fill Functions
```python
def custom_fill(series):
    if series.dtype == 'object':
        return series.fillna('Unknown')
    else:
        return series.fillna(series.median())

df = df.apply(custom_fill)
```

### Null Indicator Variables
```python
# Create indicator for missing values
df['col1_missing'] = df['col1'].isnull().astype(int)

# Add missing indicators for all columns
missing_indicators = df.isnull().astype(int)
missing_indicators.columns = [col + '_missing' for col in missing_indicators.columns]
df_with_indicators = pd.concat([df, missing_indicators], axis=1)
```

## Null Value Statistics and Visualization

### Summary Statistics
```python
# Null value summary
def null_summary(df):
    null_count = df.isnull().sum()
    null_percent = (null_count / len(df)) * 100
    return pd.DataFrame({
        'null_count': null_count,
        'null_percent': null_percent
    }).sort_values('null_count', ascending=False)

print(null_summary(df))
```

### Visualization Setup
```python
import matplotlib.pyplot as plt
import seaborn as sns

# Heatmap of null values
plt.figure(figsize=(12, 8))
sns.heatmap(df.isnull(), cbar=True, yticklabels=False, cmap='viridis')
plt.title('Missing Values Heatmap')
plt.show()

# Bar plot of null counts
null_counts = df.isnull().sum()
null_counts[null_counts > 0].plot(kind='bar')
plt.title('Null Value Counts by Column')
plt.show()
```

## Performance Considerations

### Memory Efficient Operations
```python
# Use inplace parameter to avoid copying
df.fillna(0, inplace=True)
df.dropna(inplace=True)

# For large datasets, process in chunks
def process_chunks(df, chunk_size=10000):
    for start in range(0, len(df), chunk_size):
        chunk = df.iloc[start:start+chunk_size]
        # Process chunk
        yield chunk.fillna(method='ffill')
```

### Nullable Integer and Boolean Types
```python
# Use nullable integer types
df['int_col'] = df['int_col'].astype('Int64')  # Nullable integer
df['bool_col'] = df['bool_col'].astype('boolean')  # Nullable boolean
```

## Common Patterns and Best Practices

### Data Quality Checks
```python
def data_quality_report(df):
    print(f"Dataset shape: {df.shape}")
    print(f"Total null values: {df.isnull().sum().sum()}")
    print(f"Columns with nulls: {df.isnull().any().sum()}")
    print(f"Rows with nulls: {df.isnull().any(axis=1).sum()}")
    
    # Detailed null information
    null_info = df.isnull().sum()
    null_info = null_info[null_info > 0].sort_values(ascending=False)
    if len(null_info) > 0:
        print("\nNull values by column:")
        print(null_info)
    else:
        print("\nNo null values found!")

data_quality_report(df)
```

### Handling Nulls in Groupby Operations
```python
# Include nulls in groupby
df.groupby('category', dropna=False).mean()

# Fill nulls before grouping
df.groupby(df['category'].fillna('Unknown')).mean()
```

### Chain Operations Safely
```python
# Safe chaining with null checks
result = (df
          .dropna(subset=['important_col'])
          .fillna(method='ffill')
          .groupby('category')
          .mean())
```

## Quick Reference Commands

| Operation | Command | Description |
|-----------|---------|-------------|
| Detect nulls | `df.isnull()` | Boolean mask of null values |
| Count nulls | `df.isnull().sum()` | Count nulls per column |
| Drop nulls | `df.dropna()` | Remove rows with nulls |
| Fill nulls | `df.fillna(value)` | Replace nulls with value |
| Forward fill | `df.fillna(method='ffill')` | Use previous non-null value |
| Interpolate | `df.interpolate()` | Fill with interpolated values |
| Replace values | `df.replace(old, new)` | Replace specific values |
| Check any nulls | `df.isnull().any().any()` | True if any nulls exist |
| Null percentage | `df.isnull().mean() * 100` | Percentage nulls per column |
