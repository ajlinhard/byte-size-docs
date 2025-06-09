# Date Data Formats

**Unix Timestamps**
Unix timestamps are sometimes represented in seconds as well milliseconds, especially in JavaScript and some APIs.

**Millisecond timestamps** are 13 digits (vs 10 digits for seconds):
- Seconds: `1672531200` (10 digits)
- Milliseconds: `1672531200000` (13 digits)

**Converting to datetime in Python:**

For **seconds** (standard Unix timestamp):
```python
import datetime

timestamp = 1672531200
dt = datetime.datetime.fromtimestamp(timestamp)
print(dt)  # 2023-01-01 00:00:00
```

For **milliseconds** timestamp:
```python
import datetime

timestamp_ms = 1672531200000
# Divide by 1000 to convert to seconds
dt = datetime.datetime.fromtimestamp(timestamp_ms / 1000)
print(dt)  # 2023-01-01 00:00:00
```

**Alternative using UTC:**
```python
# For UTC time (recommended for consistency)
dt_utc = datetime.datetime.utcfromtimestamp(timestamp_ms / 1000)

# Or with timezone awareness (Python 3.6+)
dt_aware = datetime.datetime.fromtimestamp(timestamp_ms / 1000, tz=datetime.timezone.utc)
```

**Quick way to identify the format:**
- If the timestamp is ~10 digits: seconds
- If the timestamp is ~13 digits: milliseconds
- You can also check: if `timestamp > 1e10`, it's likely milliseconds

Most databases and Unix systems use seconds, but web APIs (especially JavaScript-based ones) often use milliseconds.

## **UTC (Coordinated Universal Time)**
- A **time standard/timezone** - the primary time standard by which the world regulates clocks
- UTC is essentially the same as GMT but more precisely defined
- It's the "zero offset" timezone (UTC+0)
- Not a format, but rather a reference point

```python
import datetime

# Various datetime objects
now = datetime.datetime.now()
utc_now = datetime.datetime.now(datetime.timezone.utc)
specific_date = datetime.datetime(2023, 12, 25, 15, 30, 45)

# Convert to Unix timestamps
print(f"Now: {now.timestamp()}")
print(f"Now: {int(now.timestamp())}")
print(f"UTC Now: {int(utc_now.timestamp())}")
print(f"Specific: {int(specific_date.timestamp())}")
```

Unix timestamps are **inherently tied to UTC**.

**Unix timestamps are always in UTC:**
- A Unix timestamp represents the number of seconds since January 1, 1970, 00:00:00 **UTC**
- This is called the "Unix epoch" or "POSIX epoch"
- Regardless of your local timezone, a Unix timestamp always refers to the same absolute moment in UTC

**Example:**
```python
import datetime

# Unix timestamp
timestamp = 1672531200

# This represents the same moment worldwide:
# January 1, 2023, 00:00:00 UTC

# Convert to different timezones for display
utc_time = datetime.datetime.fromtimestamp(timestamp, tz=datetime.timezone.utc)
print(f"UTC: {utc_time}")  # UTC: 2023-01-01 00:00:00+00:00

# Same timestamp, shown in Eastern Time
import zoneinfo  # Python 3.9+
eastern_time = datetime.datetime.fromtimestamp(timestamp, tz=zoneinfo.ZoneInfo("America/New_York"))
print(f"Eastern: {eastern_time}")  # Eastern: 2022-12-31 19:00:00-05:00
```

**Key points:**
- The Unix timestamp `1672531200` always means the same absolute moment
- When you display it, you can choose any timezone
- But the timestamp itself is always counting from the UTC epoch
- This is why Unix timestamps are timezone-independent and portable across systems

**Common confusion:** When you use `datetime.fromtimestamp()` without specifying a timezone, Python assumes your local timezone for display, but the underlying timestamp is still UTC-based.

## **ISO Format (ISO 8601)**
- A **standardized string format** for representing dates and times
- Defines how to write dates/times as strings
- The most common format: `YYYY-MM-DDTHH:MM:SSZ` or `YYYY-MM-DDTHH:MM:SS+00:00`

**Examples:**

ISO format in UTC timezone:
```
2023-12-25T15:30:45Z          # Z indicates UTC
2023-12-25T15:30:45+00:00     # +00:00 also indicates UTC
2023-12-25T15:30:45.123Z      # With milliseconds
```

ISO format in other timezones:
```
2023-12-25T10:30:45-05:00     # Eastern Time (UTC-5)
2023-12-25T16:30:45+01:00     # Central European Time (UTC+1)
```

**In Python:**
```python
import datetime

# Current time in UTC
utc_now = datetime.datetime.now(datetime.timezone.utc)

# Convert to ISO format string
iso_string = utc_now.isoformat()
print(iso_string)  # 2023-12-25T15:30:45.123456+00:00

# Parse ISO string back to datetime
parsed = datetime.datetime.fromisoformat(iso_string)
```

**Key difference:** UTC is *where* in time (the timezone), ISO 8601 is *how* you write it down (the format). You can have ISO format timestamps in any timezone, but when you see "UTC" it usually means the time is in the UTC timezone.
