# POLARS DATA ANALYSIS CHEATSHEET
```python
import polars as pl
import polars.selectors as cs

# ============================================================================
# CREATING DATAFRAMES
# ============================================================================

# From dictionary
df = pl.DataFrame({
    'name': ['Alice', 'Bob', 'Charlie'],
    'age': [25, 30, 35],
    'city': ['NYC', 'LA', 'Chicago']
})

# From CSV
df = pl.read_csv('data.csv')
df = pl.scan_csv('data.csv')  # Lazy - doesn't load until needed

# From other formats
df = pl.read_parquet('data.parquet')
df = pl.read_json('data.json')
df = pl.read_excel('data.xlsx')

# From pandas
import pandas as pd
df = pl.from_pandas(pd_df)

# ============================================================================
# VIEWING DATA
# ============================================================================

df.head(10)           # First 10 rows
df.tail(5)            # Last 5 rows
df.sample(n=100)      # Random sample
df.describe()         # Summary statistics
df.glimpse()          # Overview of data types and values
df.shape              # (rows, columns)
df.columns            # Column names
df.dtypes             # Data types
df.schema             # Column names and types

# ============================================================================
# SELECTING COLUMNS
# ============================================================================

df.select('name')                        # Single column
df.select(['name', 'age'])               # Multiple columns
df.select(pl.col('name'))                # Using pl.col
df.select(pl.all())                      # All columns
df.select(pl.all().exclude('name'))      # All except specified
df.select(cs.numeric())                  # All numeric columns
df.select(cs.string())                   # All string columns
df.select(cs.by_dtype(pl.Int64))         # By data type
df.select(pl.col('^.*_id$'))             # Regex pattern

# ============================================================================
# FILTERING ROWS
# ============================================================================

df.filter(pl.col('age') > 25)
df.filter((pl.col('age') > 25) & (pl.col('city') == 'NYC'))
df.filter(pl.col('age').is_between(25, 35))
df.filter(pl.col('name').is_in(['Alice', 'Bob']))
df.filter(pl.col('name').str.contains('Al'))
df.filter(pl.col('value').is_not_null())
df.filter(pl.col('value').is_null())

# ============================================================================
# ADDING/MODIFYING COLUMNS
# ============================================================================

df.with_columns([
    pl.col('age').alias('age_copy'),
    (pl.col('age') * 2).alias('age_doubled'),
    pl.lit(100).alias('constant_col')
])

# Conditional column
df.with_columns(
    pl.when(pl.col('age') > 30)
      .then(pl.lit('Senior'))
      .otherwise(pl.lit('Junior'))
      .alias('category')
)

# Multiple conditions
df.with_columns(
    pl.when(pl.col('age') < 25).then('Young')
      .when(pl.col('age') < 35).then('Mid')
      .otherwise('Senior')
      .alias('age_group')
)

# ============================================================================
# AGGREGATIONS
# ============================================================================

df.select([
    pl.col('age').mean().alias('avg_age'),
    pl.col('age').median(),
    pl.col('age').std(),
    pl.col('age').min(),
    pl.col('age').max(),
    pl.col('age').sum(),
    pl.col('name').n_unique(),
    pl.col('name').count()
])

# ============================================================================
# GROUP BY
# ============================================================================

df.group_by('city').agg([
    pl.col('age').mean().alias('avg_age'),
    pl.col('age').max().alias('max_age'),
    pl.count().alias('count')
])

# Multiple grouping columns
df.group_by(['city', 'category']).agg(pl.col('value').sum())

# Aggregating all numeric columns
df.group_by('city').agg(cs.numeric().mean())

# ============================================================================
# SORTING
# ============================================================================

df.sort('age')                           # Ascending
df.sort('age', descending=True)          # Descending
df.sort(['city', 'age'])                 # Multiple columns
df.sort(pl.col('age'), nulls_last=True)  # Handle nulls

# ============================================================================
# JOINS
# ============================================================================

df1.join(df2, on='id', how='inner')      # Inner join
df1.join(df2, on='id', how='left')       # Left join
df1.join(df2, on='id', how='outer')      # Outer join
df1.join(df2, on='id', how='cross')      # Cross join
df1.join(df2, on='id', how='semi')       # Semi join (filters df1)
df1.join(df2, on='id', how='anti')       # Anti join (opposite of semi)

# Different column names
df1.join(df2, left_on='id1', right_on='id2')

# Multiple keys
df1.join(df2, on=['id', 'date'])

# ============================================================================
# STRING OPERATIONS
# ============================================================================

df.with_columns([
    pl.col('name').str.to_lowercase().alias('lower'),
    pl.col('name').str.to_uppercase().alias('upper'),
    pl.col('name').str.strip_chars().alias('stripped'),
    pl.col('name').str.replace('old', 'new').alias('replaced'),
    pl.col('name').str.slice(0, 3).alias('first_3'),
    pl.col('name').str.contains('pattern').alias('has_pattern'),
    pl.col('name').str.starts_with('A').alias('starts_a'),
    pl.col('name').str.ends_with('e').alias('ends_e'),
    pl.col('name').str.len_chars().alias('length')
])

# Split strings
df.with_columns(pl.col('full_name').str.split(' ').alias('name_parts'))

# ============================================================================
# DATE/TIME OPERATIONS
# ============================================================================

df.with_columns([
    pl.col('date').dt.year().alias('year'),
    pl.col('date').dt.month().alias('month'),
    pl.col('date').dt.day().alias('day'),
    pl.col('date').dt.weekday().alias('weekday'),
    pl.col('date').dt.hour().alias('hour'),
    pl.col('date').dt.strftime('%Y-%m-%d').alias('formatted')
])

# Date arithmetic
df.with_columns(
    (pl.col('date') + pl.duration(days=7)).alias('next_week')
)

# Parse dates
df.with_columns(
    pl.col('date_string').str.to_date('%Y-%m-%d').alias('parsed_date')
)

# ============================================================================
# WINDOW FUNCTIONS
# ============================================================================

# Cumulative sum
df.with_columns(
    pl.col('value').cum_sum().over('group').alias('cumsum')
)

# Rank
df.with_columns(
    pl.col('value').rank().over('category').alias('rank')
)

# Row number
df.with_columns(
    pl.col('value').cum_count().over('group').alias('row_num')
)

# Moving average
df.with_columns(
    pl.col('value').rolling_mean(window_size=3).alias('ma_3')
)

# Shift (lag/lead)
df.with_columns([
    pl.col('value').shift(1).over('group').alias('prev_value'),
    pl.col('value').shift(-1).over('group').alias('next_value')
])

# ============================================================================
# PIVOTING & UNPIVOTING
# ============================================================================

# Pivot
df.pivot(values='value', index='date', columns='category')

# Unpivot (melt)
df.unpivot(index='id', on=['col1', 'col2'])

# ============================================================================
# HANDLING MISSING VALUES
# ============================================================================

df.drop_nulls()                          # Drop rows with any null
df.drop_nulls(subset=['age'])            # Drop if specific column null
df.fill_null(0)                          # Fill nulls with value
df.fill_null(strategy='forward')         # Forward fill
df.fill_null(strategy='backward')        # Backward fill
df.fill_null(pl.col('age').mean())       # Fill with mean

# ============================================================================
# UNIQUE & DUPLICATES
# ============================================================================

df.unique()                              # Remove duplicate rows
df.unique(subset=['name'])               # Based on specific columns
df.unique(keep='first')                  # Keep first occurrence
df.unique(keep='last')                   # Keep last occurrence
df.is_duplicated()                       # Boolean mask for duplicates
df.n_unique()                            # Count unique rows

# ============================================================================
# COMBINING DATAFRAMES
# ============================================================================

pl.concat([df1, df2], how='vertical')    # Stack vertically (union)
pl.concat([df1, df2], how='horizontal')  # Stack horizontally
pl.concat([df1, df2], how='diagonal')    # Combine with null fills

# ============================================================================
# EXPORTING DATA
# ============================================================================

df.write_csv('output.csv')
df.write_parquet('output.parquet')
df.write_json('output.json')
df.write_excel('output.xlsx')
df.to_pandas()                           # Convert to pandas

# ============================================================================
# LAZY EVALUATION (OPTIMIZATION)
# ============================================================================

# Start lazy
lazy_df = pl.scan_csv('data.csv')

# Build query
result = (lazy_df
    .filter(pl.col('age') > 25)
    .group_by('city')
    .agg(pl.col('value').sum())
    .sort('city')
)

# Execute
result.collect()                         # Run the optimized query

# Show query plan
result.explain()

# ============================================================================
# EXPRESSIONS & CHAINING
# ============================================================================

# Method chaining
result = (df
    .filter(pl.col('age') > 25)
    .with_columns((pl.col('age') * 2).alias('age_2x'))
    .group_by('city')
    .agg([
        pl.col('age').mean().alias('avg_age'),
        pl.count().alias('count')
    ])
    .sort('avg_age', descending=True)
)

# ============================================================================
# PERFORMANCE TIPS
# ============================================================================

# 1. Use lazy evaluation with scan_* functions for large files
# 2. Use pl.col() instead of string names in expressions
# 3. Filter early in the pipeline
# 4. Use Parquet format for better performance
# 5. Leverage expression chaining for query optimization
# 6. Use categorical types for low-cardinality string columns
```
