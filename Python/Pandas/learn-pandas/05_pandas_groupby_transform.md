# Pandas GroupBy, Aggregation & Window Functions

```python
import numpy as np
import pandas as pd

df = pd.DataFrame({
    "region": ["East", "East", "West", "West", "East", "West"],
    "product": ["A", "B", "A", "B", "A", "A"],
    "sales": [100, 150, 200, 130, 90, 175],
    "units": [10, 15, 20, 13, 9, 17],
})
```

---

## 1. Split-Apply-Combine Mental Model

`groupby` doesn't compute anything by itself — it just describes how to
**split** the data. You then **apply** a function per group, and pandas
**combines** the results back into one object.

```python
grouped = df.groupby("region")   # nothing computed yet — a GroupBy object
grouped.sum()                     # NOW it splits, sums each group, combines
```

```python
grouped.groups                    # dict: group label -> row indices
grouped.get_group("East")          # pull out one group as a DataFrame
for name, group_df in grouped:      # iterate over groups
    print(name, len(group_df))
```

---

## 2. Basic Aggregation

```python
df.groupby("region")["sales"].sum()
df.groupby("region")["sales"].mean()
df.groupby("region")["sales"].agg(["sum", "mean", "count", "std"])

df.groupby("region").agg({
    "sales": "sum",
    "units": "mean",
})

df.groupby(["region", "product"]).sum(numeric_only=True)   # multiple keys -> MultiIndex result
```

### Named aggregation — clean, explicit output columns

```python
df.groupby("region").agg(
    total_sales=("sales", "sum"),
    avg_units=("units", "mean"),
    n_orders=("sales", "count"),
)
```

### Custom aggregation functions

```python
df.groupby("region")["sales"].agg(lambda x: x.max() - x.min())   # range per group

def q90(x):
    return x.quantile(0.9)

df.groupby("region")["sales"].agg(q90)
```

---

## 3. `transform` vs `apply` vs `filter`

| Method | Input → Output | Use for |
|---|---|---|
| `agg` | group → scalar | summarizing (one row per group) |
| `transform` | group → same-length result | broadcasting a group stat back onto every row |
| `apply` | group → anything | flexible/custom logic, can return scalar, Series, or DataFrame |
| `filter` | group → bool | keeping/dropping whole groups based on a group-level condition |

```python
# transform: add each row's deviation from its group's mean, same row count as df
df["sales_vs_region_avg"] = df["sales"] - df.groupby("region")["sales"].transform("mean")

# apply: fully custom per-group logic
df.groupby("region").apply(lambda g: g.nlargest(1, "sales"))   # top sale per region

# filter: keep only groups matching a group-level condition
df.groupby("product").filter(lambda g: g["sales"].sum() > 300)
```

**Rule of thumb:** if you need a value back on every original row (e.g.
"% of region total"), use `transform`. If you need one summary row per
group, use `agg`. Reach for `apply` only when neither fits.

```python
# Common pattern: percent of group total
df["pct_of_region"] = df["sales"] / df.groupby("region")["sales"].transform("sum")
```

---

## 4. Multiple Grouping Keys & `as_index`

```python
df.groupby(["region", "product"])["sales"].sum()
# -> MultiIndex Series

df.groupby(["region", "product"], as_index=False)["sales"].sum()
# -> flat DataFrame instead of MultiIndex (often easier for downstream code/exporting)
```

---

## 5. `pivot_table` — groupby + reshape in one step

```python
pd.pivot_table(
    df,
    values="sales",
    index="region",
    columns="product",
    aggfunc="sum",
    fill_value=0,
    margins=True,          # adds row/column totals
    margins_name="Total",
)
```

`pivot_table` is essentially `groupby(["region", "product"]).sum()` followed
by `.unstack("product")` — but with built-in handling for missing
combinations (`fill_value`) and grand totals (`margins`).

---

## 6. `crosstab` — frequency tables

```python
pd.crosstab(df["region"], df["product"])                 # counts by default
pd.crosstab(df["region"], df["product"], values=df["sales"], aggfunc="sum")
pd.crosstab(df["region"], df["product"], normalize="index")  # row percentages
```

---

## 7. Window Functions: `rolling`, `expanding`, `ewm`

These compute a statistic over a **moving** window of rows — essential for
time series and running metrics.

```python
s = pd.Series([1, 2, 3, 4, 5, 6, 7])

s.rolling(window=3).mean()      # simple moving average, window of 3 rows
s.rolling(window=3, min_periods=1).mean()   # allow partial windows at the start
s.rolling(window=3).sum()
s.rolling(window=3).std()

s.expanding().mean()             # cumulative mean (window grows from the start)
s.expanding().sum()               # equivalent to cumsum()

s.ewm(span=3).mean()              # exponentially weighted moving average (recent rows weighted more)
```

### Rolling/expanding **within groups**

```python
df.sort_values(["region", "product"]).groupby("region")["sales"].transform(
    lambda x: x.rolling(2).mean()
)
```

---

## 8. `groupby` + Multiple Custom Aggregations Per Column

```python
df.groupby("region").agg(
    total_sales=("sales", "sum"),
    max_units=("units", "max"),
    sales_range=("sales", lambda x: x.max() - x.min()),
)
```

---

## 9. Quick Reference

| Task | Code |
|---|---|
| Sum per group | `df.groupby("k")["col"].sum()` |
| Multiple stats per group | `df.groupby("k")["col"].agg(["sum","mean"])` |
| Named/clean output columns | `df.groupby("k").agg(total=("col","sum"))` |
| Broadcast group stat to every row | `df.groupby("k")["col"].transform("mean")` |
| Keep/drop whole groups | `df.groupby("k").filter(lambda g: ...)` |
| Reshape group results into a grid | `pd.pivot_table(df, values=..., index=..., columns=...)` |
| Frequency cross-tab | `pd.crosstab(df.a, df.b)` |
| Moving average | `df["col"].rolling(n).mean()` |

**Next:** `06_pandas_merge_reshape.md` — combining and reshaping
DataFrames (`concat`, `merge`, `melt`, `stack`/`unstack`).
