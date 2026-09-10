# Pandas for Data Engineering: Performance, Memory & Scale

This sheet is aimed at production pipelines — cleaning up a notebook script
so it survives a 50GB file or a scheduled job.

```python
import numpy as np
import pandas as pd
```

---

## 1. Inspect Memory Usage First

```python
df.info(memory_usage="deep")          # accurate memory, including object columns
df.memory_usage(deep=True)              # per-column bytes
df.memory_usage(deep=True).sum() / 1e6   # total MB
```

`df.info()` without `memory_usage="deep"` **underestimates** memory for
`object` (string) columns — it reports pointer size, not string content.
Always use `deep=True` when sizing a real pipeline.

---

## 2. Dtype Optimization

Numeric columns default to 64-bit; most data doesn't need that range.

```python
df["id"] = pd.to_numeric(df["id"], downcast="integer")   # int64 -> smallest safe int type
df["price"] = pd.to_numeric(df["price"], downcast="float")  # float64 -> float32 if safe

# Automated downcast pass over all numeric columns
for col in df.select_dtypes(include="number").columns:
    df[col] = pd.to_numeric(df[col], downcast="integer")
```

### `category` dtype — huge wins on repeated strings

```python
df["region"].nunique() / len(df)     # low ratio (few distinct values, many rows) = good category candidate
df["region"] = df["region"].astype("category")
```

`category` stores each unique string once and represents rows as integer
codes — for a column like `country` or `status` with millions of rows but
a handful of distinct values, this can cut memory by 90%+ and speed up
`groupby`/`sort_values` substantially.

```python
df.memory_usage(deep=True)   # compare before/after astype("category")
```

**Gotcha:** operations that create *new* categories not in the original set
(`df["region"].cat.add_categories(...)`) need explicit handling — a plain
assignment of an unseen value raises or produces NaN depending on pandas
version. Check `.cat.categories` before assuming a value exists.

---

## 3. Nullable / Extension Dtypes

Traditional numpy int columns can't hold `NaN` (forces upcast to float).
Pandas's nullable dtypes fix this:

```python
pd.array([1, 2, None], dtype="Int64")     # capital "I" -> nullable integer, holds pd.NA
df["count"] = df["count"].astype("Int64")
df["flag"] = df["flag"].astype("boolean")  # nullable boolean
df["name"] = df["name"].astype("string")   # dedicated string dtype (vs generic object)
```

More on extension arrays in sheet 09.

---

## 4. Reading Large Files Efficiently

```python
# 1. Only load the columns you need
pd.read_csv("big.csv", usecols=["id", "amount", "date"])

# 2. Specify dtypes up front — skips pandas's type-inference pass entirely
dtypes = {"id": "int32", "amount": "float32", "region": "category"}
pd.read_csv("big.csv", dtype=dtypes, parse_dates=["date"])

# 3. Process in chunks when the file won't fit in memory
total = 0
for chunk in pd.read_csv("big.csv", chunksize=500_000):
    total += chunk["amount"].sum()

# 4. Chain filtering INSIDE the chunk loop to keep memory flat
filtered_chunks = []
for chunk in pd.read_csv("big.csv", chunksize=500_000):
    filtered_chunks.append(chunk[chunk["amount"] > 100])
result = pd.concat(filtered_chunks, ignore_index=True)
```

`low_memory=False` disables chunked type-guessing inside `read_csv` (fixes
the "mixed types in column" `DtypeWarning`) but uses more memory during the
read — pair it with explicit `dtype=` instead when possible.

---

## 5. File Format Choice

| Format | Read speed | Write speed | Size | Preserves dtypes | Use for |
|---|---|---|---|---|---|
| CSV | slow | slow | large | no (everything is text) | interchange, human-readable |
| Parquet | fast | fast | small (columnar + compressed) | yes | pipelines, data lakes |
| Feather | very fast | very fast | small | yes | fast local intermediate storage |
| Pickle | fast | fast | medium | yes (incl. Python objects) | Python-only caching, NOT long-term/cross-version storage |

```python
df.to_parquet("data.parquet", compression="snappy")
pd.read_parquet("data.parquet", columns=["id", "amount"])   # column pruning — reads only what you need

df.to_feather("data.feather")
pd.read_feather("data.feather")
```

**Default to Parquet** for anything that isn't the final human-facing
export — smaller files, faster I/O, and dtypes (including `category` and
datetime) round-trip exactly.

---

## 6. Vectorization vs `apply` vs `iterrows` — performance ladder

Slowest to fastest, roughly:

```python
# 1. iterrows() — avoid. Rebuilds a Series per row; very slow.
for idx, row in df.iterrows():
    df.at[idx, "total"] = row["price"] * row["qty"]

# 2. itertuples() — faster than iterrows, still a Python loop.
for row in df.itertuples():
    ...

# 3. apply(axis=1) — still a Python-level loop internally.
df["total"] = df.apply(lambda r: r["price"] * r["qty"], axis=1)

# 4. Vectorized — fastest, uses compiled NumPy operations.
df["total"] = df["price"] * df["qty"]
```

For anything expressible as arithmetic, comparisons, `np.where`, or
`.map()`/`.isin()`, vectorization is almost always available and is
routinely 10-1000x faster on large frames. Reach for `.apply()` only when
row logic genuinely can't be vectorized.

---

## 7. `eval()` and `query()` for Speed on Large Frames

```python
df.eval("total = price * qty", inplace=True)   # can avoid building intermediate temporary arrays
df.query("price > 100 and region == 'East'")    # often faster than boolean-mask indexing on big frames
```

Both use the `numexpr` engine when installed (`pip install numexpr`),
which evaluates expressions without materializing every intermediate
NumPy array — most noticeable on frames with 100k+ rows and complex
expressions.

---

## 8. Method Chaining & `pipe()`

Chaining keeps transformations readable and avoids intermediate variables
(and avoids `inplace=True` foot-guns):

```python
result = (
    df
    .query("amount > 0")
    .assign(amount_usd=lambda d: d["amount"] * d["fx_rate"])
    .groupby("region", as_index=False)
    .agg(total=("amount_usd", "sum"))
    .sort_values("total", ascending=False)
)
```

`pipe()` lets you insert a custom function into a chain without breaking
the flow:

```python
def add_fiscal_year(df, start_month=4):
    df = df.copy()
    df["fiscal_year"] = df["date"].dt.year + (df["date"].dt.month >= start_month).astype(int)
    return df

result = df.query("amount > 0").pipe(add_fiscal_year, start_month=4)
```

---

## 9. SQL Integration

```python
from sqlalchemy import create_engine

engine = create_engine("postgresql://user:pass@host:5432/dbname")

pd.read_sql("SELECT * FROM orders WHERE amount > 100", con=engine)
pd.read_sql_table("orders", con=engine)                 # whole table, no SQL needed
df.to_sql("orders_clean", con=engine, if_exists="replace", index=False, chunksize=10_000)
```

**Push filtering/aggregation into the SQL query itself** when possible —
`SELECT region, SUM(amount) FROM orders GROUP BY region` run in the
database is far cheaper than pulling every raw row into pandas first.

---

## 10. Beyond Pandas: When to Reach for Something Else

Pandas is single-threaded and in-memory. When a dataset doesn't fit in RAM
or a job needs to run across cores/machines, consider:

| Tool | When |
|---|---|
| **Dask** | pandas-like API, scales to multi-core / out-of-core / clusters, minimal code changes |
| **Polars** | single-machine, multi-threaded by default, often much faster than pandas, different (expression-based) API |
| **PySpark** | true distributed processing across a cluster, best for very large (100GB+) data or existing Spark infra |
| **DuckDB** | run SQL directly over pandas DataFrames or Parquet files, very fast for analytical queries, zero infra |

A common pattern: use pandas for exploration on a sample, then port the
final logic to Dask/Polars/Spark for the full-scale production run.

---

## 11. Quick Reference

| Task | Code |
|---|---|
| Check real memory usage | `df.info(memory_usage="deep")` |
| Shrink numeric dtypes | `pd.to_numeric(col, downcast="integer")` |
| Shrink repeated strings | `df[col].astype("category")` |
| Read only needed columns | `pd.read_csv(f, usecols=[...])` |
| Read in chunks | `pd.read_csv(f, chunksize=N)` |
| Fast typed storage | `df.to_parquet(path)` |
| Fast filter/compute | `df.query(...)`, `df.eval(...)` |
| Avoid Python-level row loops | vectorize, or at worst `itertuples()` |
| Chainable custom step | `df.pipe(my_func, **kwargs)` |

**Next:** `09_pandas_advanced_topics.md` — custom accessors, styling,
extension types, testing, and a pandas-vs-SQL cheat sheet.
