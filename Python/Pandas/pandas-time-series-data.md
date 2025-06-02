# Pandas Time-series Data
This comprehensive pandas timeseries cheatsheet covering all the essential functions and operations. The cheatsheet includes:

**Key sections covered:**
- Creating datetime objects and date ranges
- Frequency aliases for different time periods
- Setting up datetime indexes
- Filtering and slicing time series data
- Resampling for different time frequencies
- Rolling window operations
- Shifting and lagging data
- Timezone operations
- Time-based grouping
- Timedelta operations
- Business day calculations
- Common patterns and best practices

Each section includes practical examples you can copy and use directly in your code. The cheatsheet is organized to be a quick reference guide for the most commonly used pandas timeseries operations, from basic datetime creation to advanced resampling and rolling calculations.

---
# Pandas Timeseries Cheatsheet

## Creating Datetime Objects

### pd.to_datetime()
```python
# Convert strings to datetime
pd.to_datetime('2023-01-15')
pd.to_datetime(['2023-01-15', '2023-02-20'])

# Handle different formats
pd.to_datetime('15/01/2023', format='%d/%m/%Y')
pd.to_datetime('2023-01-15 14:30:00')

# Handle errors
pd.to_datetime(['2023-01-15', 'invalid'], errors='coerce')  # NaT for invalid
```

### pd.Timestamp
```python
# Create single timestamp
pd.Timestamp('2023-01-15')
pd.Timestamp(2023, 1, 15)
pd.Timestamp('2023-01-15 14:30:00')
```

### pd.date_range()
```python
# Generate date ranges
pd.date_range('2023-01-01', '2023-01-10')
pd.date_range('2023-01-01', periods=10)
pd.date_range('2023-01-01', periods=10, freq='D')  # Daily
pd.date_range('2023-01-01', periods=5, freq='W')   # Weekly
pd.date_range('2023-01-01', periods=12, freq='M')  # Monthly
```

## Frequency Aliases

| Alias | Description | Example |
|-------|-------------|---------|
| D | Daily | `freq='D'` |
| W | Weekly | `freq='W'` |
| M | Month end | `freq='M'` |
| MS | Month start | `freq='MS'` |
| Q | Quarter end | `freq='Q'` |
| QS | Quarter start | `freq='QS'` |
| Y | Year end | `freq='Y'` |
| YS | Year start | `freq='YS'` |
| H | Hourly | `freq='H'` |
| T/min | Minutely | `freq='T'` |
| S | Secondly | `freq='S'` |

## Datetime Indexing

### Setting DatetimeIndex
```python
# Create DataFrame with datetime index
df = pd.DataFrame({'value': [1, 2, 3]}, 
                  index=pd.date_range('2023-01-01', periods=3))

# Convert existing column to datetime index
df['date'] = pd.to_datetime(df['date'])
df.set_index('date', inplace=True)
```

### Accessing DateTime Components
```python
df.index.year        # Year
df.index.month       # Month
df.index.day         # Day
df.index.dayofweek   # Day of week (0=Monday)
df.index.dayofyear   # Day of year
df.index.quarter     # Quarter
df.index.hour        # Hour
df.index.minute      # Minute
```

## Filtering and Slicing

### Date-based Selection
```python
# Select by year
df['2023']

# Select by year and month
df['2023-01']

# Select date range
df['2023-01-01':'2023-01-15']

# Select using loc
df.loc['2023-01-01']
df.loc['2023-01-01':'2023-01-15']
```

### Boolean Indexing
```python
# Filter by date conditions
df[df.index.year == 2023]
df[df.index.month == 1]
df[df.index > '2023-01-15']
```

## Resampling

### Basic Resampling
```python
# Resample to different frequencies
df.resample('M').mean()      # Monthly mean
df.resample('Q').sum()       # Quarterly sum
df.resample('W').max()       # Weekly maximum
df.resample('D').first()     # Daily first value
df.resample('H').last()      # Hourly last value
```

### Aggregation Functions
```python
# Multiple aggregations
df.resample('M').agg(['mean', 'sum', 'std'])

# Custom aggregations
df.resample('M').agg({
    'column1': 'mean',
    'column2': 'sum',
    'column3': lambda x: x.max() - x.min()
})
```

### Upsampling and Downsampling
```python
# Upsample (increase frequency)
df.resample('D').interpolate()    # Fill with interpolation
df.resample('H').ffill()          # Forward fill
df.resample('H').bfill()          # Backward fill

# Downsample (decrease frequency)
df.resample('M').mean()
```

## Rolling Windows

### Basic Rolling Operations
```python
# Rolling mean
df.rolling(window=7).mean()      # 7-period moving average
df.rolling(window='7D').mean()   # 7-day moving average

# Other rolling functions
df.rolling(window=7).sum()
df.rolling(window=7).std()
df.rolling(window=7).min()
df.rolling(window=7).max()
```

### Rolling with Custom Functions
```python
# Custom rolling function
df.rolling(window=7).apply(lambda x: x.max() - x.min())

# Rolling quantiles
df.rolling(window=7).quantile(0.5)  # Median
df.rolling(window=7).quantile([0.25, 0.75])  # IQR
```

## Shifting and Lagging

### Basic Shifting
```python
# Shift values
df.shift(1)      # Shift forward by 1 period
df.shift(-1)     # Shift backward by 1 period
df.shift(7)      # Shift by 7 periods

# Shift index
df.shift(1, freq='D')    # Shift index by 1 day
df.shift(2, freq='H')    # Shift index by 2 hours
```

### Percent Change
```python
# Calculate percent change
df.pct_change()          # Period-over-period change
df.pct_change(periods=7) # 7-period change
```

## Time Zones

### Working with Timezones
```python
# Localize to timezone
df.tz_localize('UTC')
df.tz_localize('US/Eastern')

# Convert between timezones
df.tz_convert('US/Pacific')
df.tz_convert('Europe/London')

# Create timezone-aware dates
pd.date_range('2023-01-01', periods=5, tz='UTC')
```

## Grouping by Time

### GroupBy with Time Components
```python
# Group by time components
df.groupby(df.index.year).mean()
df.groupby(df.index.month).sum()
df.groupby(df.index.quarter).mean()
df.groupby(df.index.dayofweek).mean()

# Group by multiple time components
df.groupby([df.index.year, df.index.month]).mean()
```

### Grouper for Resampling
```python
# Using pd.Grouper for time-based grouping
df.groupby(pd.Grouper(freq='M')).mean()
df.groupby(pd.Grouper(freq='Q')).sum()
```

## Useful DateTime Methods

### DataFrame Methods
```python
# Between dates
df.between_time('09:00', '17:00')  # Between specific times
df.at_time('10:30')                # At specific time

# First and last
df.first('5D')   # First 5 days
df.last('2W')    # Last 2 weeks
```

### Series Methods
```python
# DateTime accessor
df['date_col'].dt.year
df['date_col'].dt.month
df['date_col'].dt.day_name()
df['date_col'].dt.month_name()
df['date_col'].dt.strftime('%Y-%m-%d')
```

## Time Deltas

### Creating Timedeltas
```python
# Create timedelta
pd.Timedelta('1 day')
pd.Timedelta(days=1, hours=2, minutes=30)
pd.to_timedelta('1 day 2 hours')

# Timedelta range
pd.timedelta_range('1 day', periods=5, freq='D')
```

### Arithmetic with Timedeltas
```python
# Add/subtract time
df.index + pd.Timedelta('1 day')
df.index - pd.Timedelta('2 hours')

# Calculate duration
duration = df.index[-1] - df.index[0]
```

## Business Day Operations

### Business Day Frequencies
```python
# Business day range
pd.date_range('2023-01-01', periods=10, freq='B')   # Business days
pd.date_range('2023-01-01', periods=10, freq='BM')  # Business month end
pd.date_range('2023-01-01', periods=10, freq='BQ')  # Business quarter end
```

### Business Day Calculations
```python
# Business day offset
from pandas.tseries.offsets import BDay
df.index + BDay(1)      # Add 1 business day
df.index - BDay(5)      # Subtract 5 business days
```

## Common Patterns

### Fill Missing Dates
```python
# Create complete date range and reindex
full_range = pd.date_range(df.index.min(), df.index.max(), freq='D')
df = df.reindex(full_range)
```

### Calculate Moving Statistics
```python
# Moving averages
df['MA_7'] = df['value'].rolling(window=7).mean()
df['MA_30'] = df['value'].rolling(window=30).mean()

# Exponential moving average
df['EMA'] = df['value'].ewm(span=7).mean()
```

### Seasonal Decomposition
```python
# Group by season/month for patterns
monthly_pattern = df.groupby(df.index.month).mean()
daily_pattern = df.groupby(df.index.hour).mean()
```
