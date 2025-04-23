# Python Pandas File Loading Cheatsheet

## CSV Files

```python
# Basic loading
import pandas as pd
df = pd.read_csv('file.csv')

# Common parameters
df = pd.read_csv('file.csv',
                 sep=',',                # Delimiter to use (default is ',')
                 header=0,               # Row to use as column names (0-indexed, None = no header)
                 index_col=0,            # Column to use as index (0-indexed or name)
                 usecols=['A', 'B'],     # Only load specific columns
                 nrows=1000,             # Number of rows to read
                 skiprows=[0, 2],        # Skip specific rows (list or integer)
                 na_values=['NA', '?'],  # Additional strings to recognize as NaN
                 dtype={'A': 'float64'}, # Set data types for columns
                 low_memory=False,       # Better for mixed data types but uses more memory
                 compression='infer',    # For compressed files ('zip', 'gzip', 'bz2', 'xz')
                 encoding='utf-8',       # File encoding
                 decimal=',',            # Character to recognize as decimal point
                 thousands='.')          # Character to recognize as thousands separator

# Reading in chunks (for large files)
chunk_size = 10000
for chunk in pd.read_csv('file.csv', chunksize=chunk_size):
    # Process each chunk
    process_data(chunk)
```

## Fixed-Width Files

```python
# Basic loading
df = pd.read_fwf('file.txt')

# With specified widths
df = pd.read_fwf('file.txt',
                 widths=[10, 5, 8, 12],           # List of column widths
                 names=['name', 'id', 'price'],   # Column names
                 skiprows=3,                      # Skip rows at the beginning
                 header=None,                     # No header row
                 index_col=False,                 # Don't set an index column
                 dtype={'price': 'float'},        # Column data types
                 na_values=['*****'])             # Custom NA values

# With column positions
df = pd.read_fwf('file.txt',
                 colspecs=[(0, 10), (10, 15), (15, 23)],  # List of (start, end) column positions
                 names=['name', 'id', 'price'])           # Column names

# Infer column positions from the file
df = pd.read_fwf('file.txt', infer_nrows=10)  # Use 10 rows to infer column structure
```

## Parquet Files

```python
# Basic loading - requires pyarrow or fastparquet
df = pd.read_parquet('file.parquet')

# More options
df = pd.read_parquet('file.parquet',
                     engine='pyarrow',        # Engine: 'pyarrow' or 'fastparquet'
                     columns=['A', 'B'],      # Only load specific columns
                     filters=[('col', '==', 'value')],  # Predicate filtering (using pyarrow)
                     use_threads=True,        # Enable multithreading
                     storage_options={})      # Options for filesystems (e.g., S3)

# Handle partitioned Parquet datasets
df = pd.read_parquet('path/to/dataset/', 
                     engine='pyarrow',
                     filters=[('year', '==', 2023)])
```

## JSON Files

```python
# Basic loading
df = pd.read_json('file.json')

# Common parameters
df = pd.read_json('file.json',
                  orient='records',         # JSON structure: 'split', 'records', 'index', 'columns', 'values', 'table'
                  typ='frame',              # Return type: 'frame' or 'series'
                  lines=False,              # Read JSON Lines format (newline-delimited JSON)
                  encoding='utf-8',         # File encoding
                  precise_float=True,       # Use higher precision for floating point values
                  convert_dates=True,       # Convert dates
                  date_unit='ms',           # Specify time units for dates ('s', 'ms', 'us', 'ns')
                  dtype={'A': 'float64'})   # Set data types for columns

# JSON Lines format (each line is a valid JSON object)
df = pd.read_json('file.jsonl', lines=True)

# Nested JSON normalization
import json
from pandas.io.json import json_normalize

# Read JSON file with nested data
with open('nested.json', 'r') as f:
    data = json.load(f)

# Normalize nested JSON
df = pd.json_normalize(
    data,
    record_path=['records'],                     # Path to records
    meta=['id', ['info', 'created']],            # Metadata from other levels
    record_prefix='record_',                     # Prefix for record columns
    sep='.')                                     # Separator for nested columns
```

## Excel Files

```python
# Basic loading - requires openpyxl, xlrd, or pyxlsb
df = pd.read_excel('file.xlsx')

# Common parameters
df = pd.read_excel('file.xlsx',
                  sheet_name='Sheet1',      # Sheet to read (name, index, or list)
                  header=0,                 # Row to use as column names
                  names=['A', 'B'],         # Column names to use
                  index_col=0,              # Column to use as index
                  usecols='A:C',            # Columns to read (range, list, or callable)
                  skiprows=2,               # Rows to skip at the beginning
                  nrows=10,                 # Number of rows to read
                  dtype={'A': 'float64'},   # Set data types for columns
                  engine=None,              # Engine to use: 'openpyxl' (default for .xlsx), 'xlrd' (for .xls)
                  converters={'date': pd.to_datetime})  # Custom converters

# Reading multiple sheets
xlsx = pd.ExcelFile('file.xlsx')
sheet_names = xlsx.sheet_names  # Get sheet names

# Method 1: Dict of dataframes
dfs = pd.read_excel('file.xlsx', sheet_name=None)  # None = all sheets

# Method 2: Read sheets individually
df1 = pd.read_excel('file.xlsx', sheet_name='Sheet1')
df2 = pd.read_excel('file.xlsx', sheet_name='Sheet2')
```

## SQL Databases

```python
# Using SQLAlchemy - requires sqlalchemy and database-specific driver
from sqlalchemy import create_engine

# Create connection
engine = create_engine('postgresql://username:password@localhost:5432/mydatabase')

# Basic query
df = pd.read_sql('SELECT * FROM table', engine)

# Using parameters
df = pd.read_sql('SELECT * FROM table WHERE column = %s', engine, params=('value',))

# With more options
df = pd.read_sql('SELECT * FROM table',
                engine,
                index_col='id',          # Column to use as index
                columns=['A', 'B'],      # Columns to select
                parse_dates=['date'],    # Columns to parse as dates
                chunksize=1000)          # Read in chunks (returns iterator)

# Using SQLAlchemy expressions
from sqlalchemy import select, table, column
stmt = select([table('table_name')])
df = pd.read_sql(stmt, engine)

# Alternative: Direct table read
df = pd.read_sql_table('table_name', engine, schema='public')
```

## HDF5 Files

```python
# Requires tables package (PyTables)
# Writing HDF5
df.to_hdf('file.h5', key='df', mode='w')

# Reading HDF5
df = pd.read_hdf('file.h5', key='df')

# With more options
df = pd.read_hdf('file.h5',
                key='df',                # Group identifier in the store
                mode='r',                # Read mode ('r', 'r+', 'a')
                where='column > 0',      # PyTables query string
                start=0, stop=10,        # Row selection
                columns=['A', 'B'])      # Columns to read
```

## Feather Files

```python
# Requires pyarrow
# Writing Feather
df.to_feather('file.feather')

# Reading Feather
df = pd.read_feather('file.feather')

# With more options
df = pd.read_feather('file.feather',
                    columns=['A', 'B'],   # Columns to read
                    use_threads=True)     # Enable multithreading
```

## Tips for Efficient Loading

1. **Use appropriate dtypes**: Specify types with `dtype` parameter to reduce memory usage
2. **Chunking**: Use `chunksize` for large files to process data in smaller pieces
3. **Use filters**: When possible (e.g., with Parquet), filter data during loading
4. **Skip unnecessary columns**: Use `usecols` to load only what you need
5. **Set appropriate NA values**: Use `na_values` to properly handle missing data
6. **Consider compression**: Compressed files save space but may take longer to load

## Troubleshooting Common Issues

- **Encoding errors**: Try different encodings (utf-8, latin-1, cp1252)
- **Date parsing issues**: Use `parse_dates` or custom converters 
- **Memory errors**: Use chunking, reduce columns, optimize dtypes
- **Performance issues**: Consider using more efficient formats (Parquet over CSV)
- **Delimiter detection**: For messy CSVs, check the separator or use `sep=None` to auto-detect
