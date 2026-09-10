# Pandas Advanced Topics

```python
import numpy as np
import pandas as pd
```

---

## 1. Advanced MultiIndex Operations

```python
df = pd.DataFrame({
    "region": ["East", "East", "West", "West"],
    "product": ["A", "B", "A", "B"],
    "sales": [100, 150, 200, 130],
}).set_index(["region", "product"])

df.reorder_levels(["product", "region"])     # change level order without changing data
df.droplevel("product")                        # remove a level entirely
df.index.names                                  # -> FrozenList(['region', 'product'])

# Cartesian product of possible index values — useful to find MISSING combinations
full_index = pd.MultiIndex.from_product(
    [["East", "West"], ["A", "B", "C"]], names=["region", "product"]
)
df.reindex(full_index)   # rows for combinations not in original data appear as NaN
```

---

## 2. Custom Accessors

Pandas lets you register your own `.namespace` accessor on Series/DataFrame
— useful for packaging domain-specific logic (e.g. a `geo` or `finance`
accessor) that reads like a built-in method.

```python
@pd.api.extensions.register_dataframe_accessor("finance")
class FinanceAccessor:
    def __init__(self, pandas_obj):
        self._df = pandas_obj

    def margin(self, revenue_col, cost_col):
        return (self._df[revenue_col] - self._df[cost_col]) / self._df[revenue_col]

df = pd.DataFrame({"revenue": [100, 200], "cost": [60, 90]})
df.finance.margin("revenue", "cost")   # calls straight through, chains like any other method
```

---

## 3. Styling DataFrames (`.style`)

For notebook/report display — not for saving data:

```python
(
    df.style
    .format({"revenue": "${:,.0f}"})
    .background_gradient(subset=["revenue"], cmap="Blues")
    .highlight_max(subset=["revenue"], color="lightgreen")
    .highlight_null(color="red")
    .bar(subset=["cost"], color="lightblue")
)

# Export a styled table to Excel with formatting preserved
df.style.format({"revenue": "${:,.0f}"}).to_excel("styled.xlsx", engine="openpyxl")
```

---

## 4. Categorical Data — Deep Dive

```python
cat = pd.Categorical(["low", "high", "medium", "low"],
                      categories=["low", "medium", "high"],
                      ordered=True)
s = pd.Series(cat)

s.cat.codes                 # underlying integer codes -> [0 2 1 0]
s.cat.categories              # -> Index(['low', 'medium', 'high'])
s > "low"                      # ordered comparisons work! -> [False True True False]
s.sort_values()                 # sorts by CATEGORY ORDER, not alphabetically
s.cat.add_categories(["very_high"])
s.cat.remove_unused_categories()
s.cat.rename_categories({"low": "L", "medium": "M", "high": "H"})
```

`ordered=True` categoricals are the correct way to represent survey scales,
grades, or any ranked-but-non-numeric variable — `sort_values` and
comparison operators respect the defined order instead of falling back to
string sorting.

---

## 5. Extension Arrays & Sparse Data

```python
# Nullable numeric/boolean/string dtypes (see also sheet 08)
pd.array([1, 2, None], dtype="Int64")
pd.array([True, False, None], dtype="boolean")

# Sparse dtype — huge memory savings when a column is mostly one repeated value (often 0 or NaN)
sparse = pd.arrays.SparseArray([0, 0, 0, 1, 0, 0, 2, 0])
sparse.density        # fraction of non-fill values
s = pd.Series(sparse)
s.memory_usage()        # much lower than a dense equivalent for mostly-zero data
```

---

## 6. Testing Pandas Code

```python
import pandas.testing as pdt

pdt.assert_frame_equal(df1, df2)                 # raises AssertionError with a readable diff if not equal
pdt.assert_frame_equal(df1, df2, check_dtype=False)   # ignore dtype mismatches
pdt.assert_series_equal(s1, s2, rtol=1e-3)        # tolerance for floating-point comparisons
```

```python
# Example pytest test for a cleaning function
def clean_ages(df):
    df = df.copy()
    df["age"] = df["age"].clip(lower=0)
    return df

def test_clean_ages_clips_negative_values():
    input_df = pd.DataFrame({"age": [-5, 10, 25]})
    expected = pd.DataFrame({"age": [0, 10, 25]})
    pdt.assert_frame_equal(clean_ages(input_df), expected)
```

Always test transformation functions in isolation with small, hand-built
DataFrames — it catches dtype/edge-case regressions that a "did the
notebook run without erroring" check misses.

---

## 7. Method Chaining Patterns (recap + extension)

```python
def summarize(df):
    return (
        df
        .pipe(lambda d: d[d["amount"] > 0])          # filter step as part of the chain
        .assign(month=lambda d: d["date"].dt.to_period("M"))
        .groupby("month", as_index=False)
        .agg(total=("amount", "sum"), n=("amount", "count"))
        .sort_values("month")
    )
```

Chains read top-to-bottom like a pipeline description, are easy to test
(`assert summarize(sample_df).equals(expected)`), and avoid the
`inplace=True` / re-assignment bugs common in step-by-step scripts.

---

## 8. Common Pitfalls & Best Practices Summary

| Pitfall | Fix |
|---|---|
| `SettingWithCopyWarning` | `.copy()` explicitly, or combine filter+assign into one `.loc[]` call |
| Silent `merge` row duplication | pass `validate="one_to_one"` (or the appropriate cardinality) |
| Comparing tz-naive vs tz-aware timestamps | normalize both sides first |
| `apply(axis=1)` on large frames | vectorize with arithmetic / `np.where` / `.map()` |
| Chained `inplace=True` calls | reassign (`df = df.method(...)`) or use chaining/`pipe` |
| `int` column that should allow missing values | use nullable `"Int64"` instead of falling back to `float` |
| Reading a huge CSV without `dtype=`/`usecols=` | specify both explicitly, or `chunksize=` |
| Assuming `.mean()`/`.sum()` behave identically re: NaN across all methods | check `skipna` default per method when in doubt |
| String column stays `object` forever, slowing everything down | `.astype("category")` when cardinality is low |

---

## 9. Pandas ↔ SQL Cheat Sheet

| SQL | Pandas |
|---|---|
| `SELECT col1, col2 FROM t` | `df[["col1", "col2"]]` |
| `SELECT * FROM t WHERE x > 5` | `df[df["x"] > 5]` or `df.query("x > 5")` |
| `SELECT DISTINCT col FROM t` | `df["col"].unique()` |
| `SELECT col, COUNT(*) FROM t GROUP BY col` | `df.groupby("col").size()` |
| `SELECT col, SUM(x) FROM t GROUP BY col` | `df.groupby("col")["x"].sum()` |
| `t1 INNER JOIN t2 ON t1.id = t2.id` | `pd.merge(t1, t2, on="id", how="inner")` |
| `t1 LEFT JOIN t2 ON t1.id = t2.id` | `pd.merge(t1, t2, on="id", how="left")` |
| `ORDER BY col DESC` | `df.sort_values("col", ascending=False)` |
| `LIMIT 10` | `df.head(10)` |
| `UNION ALL` | `pd.concat([t1, t2])` |
| Window function `AVG(x) OVER (PARTITION BY g)` | `df.groupby("g")["x"].transform("mean")` |
| `HAVING SUM(x) > 100` | `df.groupby("g").filter(lambda d: d["x"].sum() > 100)` |

---

## 10. Further Resources

- Official docs: https://pandas.pydata.org/docs/
- pandas "Cookbook" (official recipes for real-world tasks)
- Polars docs — worth learning next for a faster, expression-based
  alternative once pandas fundamentals feel comfortable
- `pandas.testing` module docs for building a real test suite around
  data pipelines

---

This completes the series. Suggested path if revisiting: sheets 1-3 for
daily analysis work, 4-7 for a real cleaning/transformation project, 8-9
when a pipeline needs to run reliably at scale or in production.
