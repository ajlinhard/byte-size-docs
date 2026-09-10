# Pandas Time Series

```python
import numpy as np
import pandas as pd
```

---

## 1. Core Time Types

| Type | Represents | Analogous to |
|---|---|---|
| `pd.Timestamp` | a specific point in time | Python `datetime` |
| `pd.Period` | a span of time (e.g. "March 2023") | a calendar period |
| `pd.Timedelta` | a duration | Python `timedelta` |
| `pd.DatetimeIndex` | an index of Timestamps | array of dates as row labels |

```python
pd.Timestamp("2023-03-15")
pd.Timestamp("2023-03-15 14:30:00")
pd.Timedelta(days=3, hours=4)
pd.Period("2023-03", freq="M")
```

---

## 2. Parsing Dates: `pd.to_datetime`

```python
pd.to_datetime("2023-03-15")
pd.to_datetime(["2023-01-01", "2023/02/10", "March 3, 2023"])   # handles mixed formats
pd.to_datetime(df["date_col"], format="%Y-%m-%d", errors="coerce")  # explicit format = much faster + safer
pd.to_datetime(df["date_col"], errors="coerce")   # unparseable values -> NaT instead of raising
```

**Always pass `format=` explicitly in production pipelines** — inferring
formats row-by-row is slow and occasionally ambiguous (`01/02/03`?).

---

## 3. Building a `DatetimeIndex`

```python
pd.date_range(start="2023-01-01", end="2023-01-10", freq="D")   # daily
pd.date_range(start="2023-01-01", periods=5, freq="M")            # 5 month-end dates
pd.date_range(start="2023-01-01", periods=24, freq="H")            # hourly

df = pd.DataFrame(
    {"value": np.random.default_rng(0).integers(0, 100, 10)},
    index=pd.date_range("2023-01-01", periods=10, freq="D"),
)
```

### Common `freq` codes

| Code | Meaning |
|---|---|
| `D` | calendar day |
| `B` | business day |
| `W` | weekly |
| `M` | month end |
| `MS` | month start |
| `Q` | quarter end |
| `A`/`Y` | year end |
| `H` | hourly |
| `T`/`min` | minute |
| `S` | second |

---

## 4. Extracting Date Parts — the `.dt` accessor

```python
df["date"] = df.index
df["date"].dt.year
df["date"].dt.month
df["date"].dt.day
df["date"].dt.dayofweek     # 0 = Monday
df["date"].dt.day_name()     # -> "Monday"
df["date"].dt.quarter
df["date"].dt.is_month_end
df["date"].dt.isocalendar().week
```

---

## 5. Selecting/Slicing Time Series Data

With a `DatetimeIndex`, you can slice using partial date strings:

```python
df.loc["2023-01"]              # every row in January 2023
df.loc["2023-01-05":"2023-01-08"]   # inclusive range slice
df.loc["2023"]                   # every row in 2023
df.first("3D")                    # first 3 days of data
df.last("2D")                      # last 2 days of data
```

---

## 6. Resampling — changing frequency

`resample` is `groupby` for time — it buckets rows into time intervals and
lets you aggregate each bucket.

```python
df["value"].resample("W").sum()     # daily -> weekly totals (downsampling)
df["value"].resample("M").mean()     # daily -> monthly average
df["value"].resample("6H").ffill()    # daily -> 6-hourly, forward-filling gaps (upsampling)

df.resample("W").agg({"value": ["sum", "mean", "max"]})
```

**Downsampling** (fine → coarse, e.g. daily → monthly) needs an aggregation
(`sum`, `mean`...). **Upsampling** (coarse → fine, e.g. daily → hourly)
creates new rows that need to be filled (`ffill`, `bfill`, `interpolate`).

---

## 7. Shifting, Lagging & Percent Change

```python
df["value"].shift(1)                # lag by 1 period (previous row's value)
df["value"].shift(-1)                # lead by 1 period (next row's value)
df["value"].diff()                    # value[t] - value[t-1]
df["value"].diff(periods=7)            # week-over-week change (if daily data)
df["value"].pct_change()                # (value[t] - value[t-1]) / value[t-1]
df["value"].pct_change(periods=7) * 100  # week-over-week % change
```

Classic pattern — flag rows where a value dropped from the previous row:

```python
df["dropped"] = df["value"].diff() < 0
```

---

## 8. Rolling Windows on Time Series

```python
df["value"].rolling(window=3).mean()            # 3-row moving average
df["value"].rolling(window="3D").mean()           # TIME-based window: last 3 calendar days (needs a DatetimeIndex)
df["value"].rolling(window=3, center=True).mean()  # centered window instead of trailing
```

Time-based windows (`"3D"`, `"7D"`) are safer than row-count windows
(`window=3`) on irregular time series, since they account for gaps.

---

## 9. Timezones

```python
df.index.tz_localize("UTC")                # attach a timezone to naive timestamps
df.index.tz_convert("America/New_York")      # convert an already-aware index to another zone
pd.Timestamp("2023-01-01", tz="UTC")
pd.Timestamp.now(tz="UTC")
```

**Gotcha:** you cannot compare or merge a tz-naive and tz-aware Timestamp —
normalize both sides to the same awareness before joining time series from
different sources (e.g. a UTC API vs a local-time log file).

---

## 10. Business Day / Custom Offsets

```python
from pandas.tseries.offsets import BDay, MonthEnd

pd.Timestamp("2023-01-01") + BDay(5)     # 5 business days later, skipping weekends
pd.Timestamp("2023-01-15") + MonthEnd(1)  # roll forward to month end
pd.bdate_range("2023-01-01", "2023-01-31")  # business-day range (no weekends)
```

---

## 11. `asfreq` vs `resample`

```python
df.asfreq("D")          # reindex to a fixed frequency, no aggregation — just fills the grid
df.resample("D").mean()  # regularize AND aggregate if multiple original rows fall in a bucket
```

Use `asfreq` when you just need a regular grid (e.g. before `ffill`); use
`resample` when multiple raw rows might collapse into one output row.

---

## 12. Quick Reference

| Task | Code |
|---|---|
| Parse strings to datetime | `pd.to_datetime(col, format=..., errors="coerce")` |
| Build a date index | `pd.date_range(start, end, freq="D")` |
| Slice by partial date | `df.loc["2023-01"]` |
| Change frequency + aggregate | `df.resample("M").sum()` |
| Lag/lead a column | `df["x"].shift(1)` |
| % change over time | `df["x"].pct_change()` |
| Moving average (time-aware) | `df["x"].rolling("7D").mean()` |
| Localize/convert timezone | `.dt.tz_localize()` / `.dt.tz_convert()` |

**Next:** `08_pandas_performance_data_engineering.md` — memory, dtypes,
chunked I/O, Parquet, and SQL for production-scale pandas.
