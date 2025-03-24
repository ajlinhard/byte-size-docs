# Python Datetime Cheatsheet

## Importing Modules
```python
from datetime import datetime, date, time, timedelta
import pytz  # For timezone handling
import calendar
```

## Creating Datetime Objects

### Current Date and Time
```python
# Get current date and time
now = datetime.now()  # Local datetime
utc_now = datetime.utcnow()  # UTC datetime

# Get current date
today = date.today()

# Get current time
current_time = datetime.now().time()
```

### Creating Specific Dates and Times
```python
# Create a specific date (year, month, day)
specific_date = date(2025, 3, 24)

# Create a specific time (hour, minute, second, microsecond)
specific_time = time(13, 30, 5, 0)  # 1:30:05 PM

# Create a specific datetime (year, month, day, hour, minute, second, microsecond)
specific_dt = datetime(2025, 3, 24, 13, 30, 5, 0)  # March 24, 2025 1:30:05 PM
```

### Parsing Strings to Datetime
```python
# Parse string to datetime using strptime
date_string = "2025-03-24 13:30:05"
parsed_dt = datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")

# Common format codes:
# %Y - 4-digit year (2025)
# %y - 2-digit year (25)
# %m - month (01-12)
# %d - day (01-31)
# %H - 24-hour (00-23)
# %I - 12-hour (01-12)
# %M - minute (00-59)
# %S - second (00-59)
# %f - microsecond (000000-999999)
# %A - weekday name (Sunday)
# %a - abbreviated weekday (Sun)
# %B - month name (January)
# %b - abbreviated month (Jan)
# %p - AM/PM
# %z - UTC offset (+0000)
# %Z - timezone name (UTC)
```

## Formatting Datetime Objects

### Converting to Strings
```python
# Format datetime to string using strftime
now = datetime.now()
formatted_date = now.strftime("%Y-%m-%d")  # '2025-03-24'
formatted_datetime = now.strftime("%Y-%m-%d %H:%M:%S")  # '2025-03-24 13:30:05'
readable_date = now.strftime("%B %d, %Y")  # 'March 24, 2025'
time_with_am_pm = now.strftime("%I:%M %p")  # '01:30 PM'
```

### ISO Format
```python
# ISO 8601 format
iso_format = now.isoformat()  # '2025-03-24T13:30:05.123456'
date_iso = today.isoformat()  # '2025-03-24'
```

## Accessing Components

```python
dt = datetime(2025, 3, 24, 13, 30, 5)

# Access individual components
year = dt.year        # 2025
month = dt.month      # 3
day = dt.day          # 24
hour = dt.hour        # 13
minute = dt.minute    # 30
second = dt.second    # 5
microsecond = dt.microsecond  # 0

# Get day of week (0 = Monday, 6 = Sunday)
weekday = dt.weekday()  # If March 24, 2025 is Monday, returns 0
isoweekday = dt.isoweekday()  # If March 24, 2025 is Monday, returns 1 (1 = Monday, 7 = Sunday)

# Get day of year (1-366)
day_of_year = dt.timetuple().tm_yday
```

## Datetime Arithmetic

### Timedelta Objects
```python
# Create a timedelta
one_day = timedelta(days=1)
one_week = timedelta(weeks=1)  # 7 days
one_hour = timedelta(hours=1)
complex_delta = timedelta(days=2, hours=3, minutes=30, seconds=15)

# Access timedelta components
days = complex_delta.days  # 2
seconds = complex_delta.seconds  # 12,615 (3h 30m 15s in seconds)
total_seconds = complex_delta.total_seconds()  # 185,415 (2d 3h 30m 15s in seconds)
```

### Adding and Subtracting
```python
now = datetime.now()

# Add time
tomorrow = now + timedelta(days=1)
next_week = now + timedelta(weeks=1)
three_hours_later = now + timedelta(hours=3)

# Subtract time
yesterday = now - timedelta(days=1)
last_week = now - timedelta(weeks=1)
three_hours_ago = now - timedelta(hours=3)

# Time between two dates
date1 = datetime(2025, 3, 1)
date2 = datetime(2025, 3, 24)
difference = date2 - date1  # returns a timedelta
days_between = difference.days  # 23
```

### Date Ranges
```python
# Generate range of dates
start_date = date(2025, 3, 1)
end_date = date(2025, 3, 10)
date_range = []

current_date = start_date
while current_date <= end_date:
    date_range.append(current_date)
    current_date += timedelta(days=1)

# Alternative with list comprehension
date_range = [(start_date + timedelta(days=i)) for i in range((end_date - start_date).days + 1)]
```

## Timezone Handling with pytz

### Working with Timezones
```python
import pytz

# Common timezone objects
utc = pytz.UTC
eastern = pytz.timezone('US/Eastern')
pacific = pytz.timezone('US/Pacific')
paris = pytz.timezone('Europe/Paris')

# Get all available timezone names
all_timezones = pytz.all_timezones  # List of all timezone strings

# Localize a naive datetime (one without timezone info)
naive_dt = datetime(2025, 3, 24, 13, 30)
eastern_dt = eastern.localize(naive_dt)  # Add timezone info

# Convert from one timezone to another
paris_dt = eastern_dt.astimezone(paris)

# Get current time in specific timezone
now_in_paris = datetime.now(paris)
utc_now = datetime.now(pytz.UTC)
```

### Handling DST (Daylight Saving Time)
```python
# Check if a datetime is in DST
is_dst = eastern_dt.dst() != timedelta(0)

# Get UTC offset
utc_offset = eastern_dt.utcoffset()  # Returns a timedelta
```

## Useful Utilities

### Calendar Operations
```python
import calendar

# Check if year is leap year
is_leap = calendar.isleap(2024)  # True

# Get calendar for month
cal = calendar.month(2025, 3)  # Returns a string with calendar for March 2025

# Get number of days in month
days_in_march = calendar.monthrange(2025, 3)[1]  # 31

# First weekday of month (0 = Monday, 6 = Sunday)
first_day = calendar.monthrange(2025, 3)[0]
```

### Unix Timestamp Conversion
```python
# Datetime to Unix timestamp (seconds since Jan 1, 1970)
timestamp = datetime.now().timestamp()

# Unix timestamp to datetime
dt_from_timestamp = datetime.fromtimestamp(timestamp)
utc_from_timestamp = datetime.utcfromtimestamp(timestamp)
```

### Comparing Datetimes
```python
dt1 = datetime(2025, 3, 24)
dt2 = datetime(2025, 3, 25)

# Comparison operators
is_equal = dt1 == dt2  # False
is_earlier = dt1 < dt2  # True
is_later = dt1 > dt2  # False

# Get min/max
earlier_date = min(dt1, dt2)  # dt1
later_date = max(dt1, dt2)  # dt2
```

## Advanced Operations

### Replace Parts of Datetime
```python
dt = datetime(2025, 3, 24, 13, 30)

# Replace specific components
dt_new_year = dt.replace(year=2026)
dt_new_time = dt.replace(hour=15, minute=45)
```

### Date/Time vs Datetime
```python
# Combine date and time objects
d = date(2025, 3, 24)
t = time(13, 30)
dt = datetime.combine(d, t)

# Extract date or time from datetime
just_date = dt.date()
just_time = dt.time()
```

### Week-related Operations
```python
# Get ISO calendar: (ISO year, ISO week number, ISO weekday)
iso_calendar = dt.isocalendar()  # returns a tuple (2025, 13, 1) for March 24, 2025
iso_year = iso_calendar[0]
iso_week = iso_calendar[1]
iso_weekday = iso_calendar[2]  # 1=Monday, 7=Sunday

# First day of the week containing a date
start_of_week = dt - timedelta(days=dt.weekday())  # Monday
```

## Tips and Common Patterns

### Default Arguments
```python
# Avoid using datetime.now() as a default argument
# WRONG: It's evaluated only once when function is defined
def process_data(timestamp=datetime.now()):
    pass

# RIGHT: Use None and set inside function
def process_data(timestamp=None):
    if timestamp is None:
        timestamp = datetime.now()
    pass
```

### Time Zones Best Practices
```python
# Always store datetime in UTC
utc_time = datetime.now(pytz.UTC)

# Convert to local time only for display
local_time = utc_time.astimezone(pytz.timezone('US/Eastern'))
```

### Handling Time Spans
```python
# Get all dates in a month
def days_in_month(year, month):
    _, num_days = calendar.monthrange(year, month)
    return [date(year, month, day) for day in range(1, num_days + 1)]

# Get first/last day of month
first_day = date(2025, 3, 1)
last_day = date(2025, 3, calendar.monthrange(2025, 3)[1])
```
