# Pandas Data Cleaning

```python
import numpy as np
import pandas as pd

df = pd.DataFrame({
    "name": [" Ana", "Bo ", "cy", "Dee", "Ana"],
    "age": [25, np.nan, 45, 29, 25],
    "salary": ["50000", "62,000", "N/A", "71000", "50000"],
    "signup": ["2023-01-05", "2023/02/10", None, "2023-04-01", "2023-01-05"],
})
```

---

## 1. Missing Data

Pandas represents missing values as `NaN` (float), `None` (object columns),
`NaT` (datetime), or `pd.NA` (nullable dtypes — see sheet 08).

```python
df.isna()               # boolean mask, True where missing
df.isna().sum()          # count of missing values per column
df.notna()                # inverse of isna()
df["age"].isna().mean()   # fraction missing (great for a quick data-quality check)
```

### Dropping missing data

```python
df.dropna()                       # drop any row with ANY NaN
df.dropna(how="all")               # drop only rows where EVERY value is NaN
df.dropna(subset=["age"])          # drop rows missing specifically in "age"
df.dropna(axis=1)                   # drop columns instead of rows
df.dropna(thresh=3)                  # keep rows with at least 3 non-null values
```

### Filling missing data

```python
df["age"].fillna(0)                          # constant fill
df["age"].fillna(df["age"].mean())            # statistical fill
df["age"].fillna(method="ffill")               # forward-fill (carry last valid value)
df["age"].fillna(method="bfill")               # backward-fill
df["age"].interpolate()                         # linear interpolation between known points
df.fillna({"age": 0, "salary": "unknown"})       # per-column fill values
```

**Gotcha:** `df["age"].mean()` ignores NaNs by default (`skipna=True`) —
good for stats, but don't assume every aggregation silently drops NaNs the
same way; check the docs for less common methods.

---

## 2. Duplicates

```python
df.duplicated()                    # boolean mask, True for repeat rows (keeps first occurrence)
df.duplicated(subset=["name"])       # duplicate check on specific columns only
df.duplicated(keep="last")            # mark all but the LAST occurrence as duplicate
df.duplicated(keep=False)              # mark ALL occurrences of duplicates as True

df.drop_duplicates()                   # remove duplicate rows
df.drop_duplicates(subset=["name"], keep="first")
```

---

## 3. Type Conversion

```python
df["age"] = df["age"].astype("Int64")     # nullable integer (capital I) — survives NaN
pd.to_numeric(df["salary"], errors="coerce")  # non-numeric strings -> NaN instead of raising
pd.to_datetime(df["signup"], errors="coerce")  # parse mixed date formats -> NaT on failure
df.infer_objects()                          # let pandas re-guess dtypes after manual edits
```

```python
# Cleaning the messy "salary" column end to end
df["salary_clean"] = (
    df["salary"]
    .str.replace(",", "", regex=False)   # strip thousands separators
    .replace("N/A", np.nan)               # normalize sentinel values
    .astype(float)
)
```

**`errors=` parameter cheat sheet** (applies to `to_numeric`, `to_datetime`,
`astype` in some contexts):

| Value | Behavior |
|---|---|
| `"raise"` (default) | throws on the first bad value |
| `"coerce"` | bad values become `NaN`/`NaT` |
| `"ignore"` | leaves the whole column untouched if *any* value fails (deprecated in newer pandas — prefer `coerce` + explicit handling) |

---

## 4. String Cleaning — the `.str` accessor

```python
df["name"].str.strip()             # remove leading/trailing whitespace
df["name"].str.lower()              # -> "ana"
df["name"].str.upper()
df["name"].str.title()               # -> "Ana"
df["name"].str.len()                  # length of each string
df["name"].str.contains("a", case=False)   # boolean mask
df["name"].str.startswith("A")
df["name"].str.replace(r"\s+", "", regex=True)   # regex replace
df["name"].str.split(" ")             # -> lists
df["name"].str.split(" ", expand=True)  # -> separate columns
df["name"].str.extract(r"(\d+)")        # regex capture group -> new column
df["name"].str.cat(sep=", ")             # join all values into one string
df["name"].str.pad(10, fillchar="*")
```

**Always chain `.str.strip().str.lower()` early** in a cleaning pipeline —
whitespace and casing inconsistencies are the #1 cause of "duplicate"
categories that `groupby`/`value_counts` treat as distinct.

---

## 5. Applying Functions

```python
df["age"].map(lambda x: x * 2)               # Series -> Series, element-wise
df["age"].map({25: "young", 45: "older"})     # map() also works as a dict lookup

df.apply(lambda row: row["age"] + 1, axis=1)   # row-wise on a DataFrame (axis=1)
df.apply(lambda col: col.max(), axis=0)         # column-wise (axis=0, default)

df.applymap(lambda x: str(x))                    # element-wise over the WHOLE DataFrame (deprecated name; use df.map in pandas 2.1+)
```

**Performance note:** `.apply()` with `axis=1` loops in Python under the
hood and is often 10-100x slower than a vectorized expression. Prefer:

```python
# Slow
df["age_bucket"] = df.apply(lambda r: "adult" if r["age"] >= 18 else "minor", axis=1)

# Fast — vectorized
df["age_bucket"] = np.where(df["age"] >= 18, "adult", "minor")
```

Reach for `.apply()` only when the logic genuinely can't be vectorized
(e.g., calling an external API per row, complex conditional branching).

---

## 6. Replacing & Conditional Values

```python
df.replace("N/A", np.nan)                    # value -> value
df.replace({"salary": {"N/A": np.nan}})       # per-column replacement map
df["age"].where(df["age"] > 18, 0)             # keep value where True, else 0 (opposite of np.where's arg order feel)
df["age"].mask(df["age"] > 40, 0)               # opposite of where(): replace where condition is True
```

---

## 7. Outlier Detection & Capping

```python
# IQR method
q1, q3 = df["age"].quantile([0.25, 0.75])
iqr = q3 - q1
lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
outliers = df[(df["age"] < lower) | (df["age"] > upper)]

# Z-score method
z = (df["age"] - df["age"].mean()) / df["age"].std()
outliers = df[z.abs() > 3]

# Capping instead of dropping
df["age_capped"] = df["age"].clip(lower=lower, upper=upper)
```

---

## 8. Cleaning Column Names

```python
df.columns = (
    df.columns
    .str.strip()
    .str.lower()
    .str.replace(" ", "_")
    .str.replace(r"[^\w]", "", regex=True)
)
```

---

## 9. End-to-End Cleaning Checklist

1. `df.info()` / `df.isna().sum()` — see what you're dealing with.
2. Strip/lower/normalize string columns.
3. Fix dtypes (`astype`, `to_numeric`, `to_datetime`) with `errors="coerce"`.
4. Handle missing values deliberately (drop vs fill — document the choice).
5. Drop or flag duplicates.
6. Check for outliers before aggregating (a single bad row can wreck a mean).
7. Re-run `df.describe()` / `df.info()` to confirm the fix worked.

**Next:** `05_pandas_groupby_transform.md` — split-apply-combine, pivot
tables, and window functions.
