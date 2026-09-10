# Pandas Basics: Series, DataFrames & I/O

```python
import numpy as np
import pandas as pd
```

---

## 1. Series vs DataFrame

- **Series**: 1D labeled array (a single column + an index).
- **DataFrame**: 2D labeled table (a dict of Series sharing an index) —
  think "spreadsheet" or "SQL table."

```python
s = pd.Series([10, 20, 30], index=["a", "b", "c"], name="score")
s
# a    10
# b    20
# c    30
# Name: score, dtype: int64

df = pd.DataFrame({
    "name": ["Ana", "Bo", "Cy"],
    "age": [25, 31, 45],
    "city": ["NYC", "LA", "NYC"],
})
```

---

## 2. Creating DataFrames — every common way

```python
# From a dict of lists (most common)
pd.DataFrame({"a": [1, 2], "b": [3, 4]})

# From a list of dicts (row-oriented — common from JSON/APIs)
pd.DataFrame([{"a": 1, "b": 3}, {"a": 2, "b": 4}])

# From a NumPy array
pd.DataFrame(np.arange(6).reshape(2, 3), columns=["x", "y", "z"])

# From a list of tuples with explicit columns
pd.DataFrame([(1, "x"), (2, "y")], columns=["id", "label"])

# Empty frame with defined columns (useful as an accumulator target)
pd.DataFrame(columns=["id", "value"])
```

---

## 3. Core Attributes

```python
df.shape        # -> (rows, cols)
df.columns      # -> Index(['name', 'age', 'city'])
df.index        # -> RangeIndex(start=0, stop=3, step=1)
df.dtypes       # per-column dtype
df.values       # underlying NumPy array (loses column dtypes if mixed)
df.axes         # [index, columns]
df.size         # total cell count
df.empty        # True/False
```

---

## 4. First Look at Data

```python
df.head(3)          # first 3 rows
df.tail(3)           # last 3 rows
df.sample(2)          # 2 random rows (great for spot-checking)
df.info()             # dtypes, non-null counts, memory usage
df.describe()         # summary stats for numeric columns
df.describe(include="all")   # include categorical/object columns too
df.nunique()           # distinct value count per column
df["city"].value_counts()    # frequency table for one column
df["city"].unique()          # array of distinct values
```

---

## 5. Reading Data

```python
# CSV — the workhorse
pd.read_csv("file.csv")
pd.read_csv(
    "file.csv",
    sep=",",                 # delimiter
    header=0,                 # row to use as header
    index_col="id",           # column to use as the row index
    usecols=["id", "name"],   # only load these columns (saves memory)
    dtype={"id": "int32"},    # force dtypes on read (faster, less memory)
    parse_dates=["created_at"],
    na_values=["NA", "?"],    # extra strings to treat as NaN
    nrows=1000,                # only read first N rows (sampling)
    chunksize=10_000,          # returns an iterator of DataFrames (see sheet 08)
)

pd.read_excel("file.xlsx", sheet_name="Sheet1")     # needs openpyxl
pd.read_json("file.json")
pd.read_parquet("file.parquet")                      # needs pyarrow
pd.read_sql("SELECT * FROM users", con=engine)       # needs sqlalchemy
pd.read_html("page.html")                             # list of DataFrames from <table> tags
pd.read_clipboard()                                    # whatever's on your clipboard — handy in notebooks
```

---

## 6. Writing Data

```python
df.to_csv("out.csv", index=False)          # index=False avoids an extra unnamed column
df.to_excel("out.xlsx", index=False)
df.to_json("out.json", orient="records")
df.to_parquet("out.parquet")                # compact, typed, fast — preferred for pipelines
df.to_sql("table_name", con=engine, if_exists="replace", index=False)
```

**Rule of thumb:** use CSV for human-readable interchange, Parquet for
everything internal to a pipeline (smaller, preserves dtypes, much faster).

---

## 7. Selecting Columns (preview — full detail in sheet 03)

```python
df["age"]              # single column -> Series
df[["name", "age"]]    # multiple columns -> DataFrame (note the double brackets)
df.age                 # attribute access (works only if name is a valid identifier — avoid in real code)
```

---

## 8. Renaming

```python
df.rename(columns={"name": "full_name"})       # returns a new frame by default
df.rename(columns=str.upper)                     # apply a function to all column names
df.columns = ["a", "b", "c"]                      # brute-force full replacement
df.set_axis(["x", "y", "z"], axis=1)              # explicit, chainable version
```

---

## 9. Sorting

```python
df.sort_values("age")                       # ascending by default
df.sort_values("age", ascending=False)
df.sort_values(["city", "age"])              # multi-column sort
df.sort_values(["city", "age"], ascending=[True, False])
df.sort_index()                                # sort by the row index
```

---

## 10. Adding / Dropping Columns

```python
df["is_adult"] = df["age"] >= 18            # new column from a vectorized expression
df.assign(age_plus_1=df["age"] + 1)          # chainable, returns a new frame

df.drop(columns=["city"])                     # drop a column (returns new frame)
df.drop(index=[0, 1])                          # drop rows by index label
df.drop("city", axis=1, inplace=True)          # in-place — use sparingly, breaks chaining
```

---

## 11. `inplace=True` — why to mostly avoid it

`inplace=True` mutates the object and returns `None`. It:
- Prevents method chaining.
- Doesn't actually save memory in most pandas versions (it still builds a
  new result internally, then copies it back).
- Makes bugs harder to trace, since the original object silently changes.

Prefer `df = df.drop(columns=[...])` or chained `.pipe()`/`.assign()` style
(see sheet 08 on method chaining).

**Next:** `03_pandas_indexing_selection.md` — `loc`, `iloc`, boolean
filtering, and `MultiIndex` basics.
