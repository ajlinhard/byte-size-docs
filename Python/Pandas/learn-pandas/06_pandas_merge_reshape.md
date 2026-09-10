# Pandas Merging, Joining & Reshaping

```python
import numpy as np
import pandas as pd

customers = pd.DataFrame({
    "customer_id": [1, 2, 3, 4],
    "name": ["Ana", "Bo", "Cy", "Dee"],
})

orders = pd.DataFrame({
    "order_id": [101, 102, 103, 104, 105],
    "customer_id": [1, 2, 2, 5, 3],
    "amount": [50, 20, 30, 15, 90],
})
```

---

## 1. `concat` — stacking DataFrames

```python
pd.concat([df1, df2])                    # stack rows (axis=0, default) — like SQL UNION ALL
pd.concat([df1, df2], axis=1)             # stack columns side by side (aligns on index)
pd.concat([df1, df2], ignore_index=True)   # discard old indices, get a fresh RangeIndex
pd.concat([df1, df2], keys=["jan", "feb"]) # add a MultiIndex level to track origin
pd.concat([df1, df2], join="inner")         # keep only columns present in BOTH (default "outer" keeps all)
```

**Use `concat` when:** combining datasets with the *same schema* (e.g.
monthly CSVs to stitch into one table).

---

## 2. `merge` — SQL-style joins

```python
pd.merge(customers, orders, on="customer_id", how="inner")   # SQL INNER JOIN
pd.merge(customers, orders, on="customer_id", how="left")     # SQL LEFT JOIN — keep all customers
pd.merge(customers, orders, on="customer_id", how="right")     # SQL RIGHT JOIN — keep all orders
pd.merge(customers, orders, on="customer_id", how="outer")      # SQL FULL OUTER JOIN
pd.merge(customers, orders, on="customer_id", how="cross")       # cartesian product (no `on` needed)
```

### Join key column names differ

```python
pd.merge(customers, orders, left_on="customer_id", right_on="customer_id")
# or, if the column names literally differ:
pd.merge(df_a, df_b, left_on="cust_id", right_on="customer_id")
```

### Handling overlapping non-key column names

```python
pd.merge(df_a, df_b, on="id", suffixes=("_left", "_right"))
```

### Validating join cardinality (catches silent row-duplication bugs)

```python
pd.merge(customers, orders, on="customer_id", validate="one_to_many")
# raises MergeError if the assumption doesn't hold — validate before it ships
```

| `validate` option | Meaning |
|---|---|
| `"one_to_one"` | keys unique on both sides |
| `"one_to_many"` | keys unique on the left |
| `"many_to_one"` | keys unique on the right |
| `"many_to_many"` | no uniqueness check (default behavior) |

### `indicator=True` — see where each row came from

```python
merged = pd.merge(customers, orders, on="customer_id", how="outer", indicator=True)
merged["_merge"].value_counts()
# left_only / right_only / both
```

This is the standard trick for finding **unmatched rows** — e.g. customers
with no orders, or orders with no matching customer (orphaned foreign keys).

```python
unmatched_customers = merged[merged["_merge"] == "left_only"]
```

---

## 3. `join` — merge on the index

```python
customers.set_index("customer_id").join(orders.set_index("customer_id"), how="left")
```

`.join()` is `merge` specialized for index-based joins — convenient when
you've already set a shared index, but `merge` covers every case `join`
does and more, so most people default to `merge`.

---

## 4. `melt` — wide → long

```python
wide = pd.DataFrame({
    "student": ["Ana", "Bo"],
    "math": [90, 80],
    "science": [85, 95],
})

pd.melt(
    wide,
    id_vars="student",           # column(s) to keep as-is
    value_vars=["math", "science"],  # columns to unpivot
    var_name="subject",
    value_name="score",
)
#   student  subject  score
# 0     Ana     math     90
# 1      Bo     math     80
# 2     Ana  science     85
# 3      Bo  science     95
```

Use `melt` when your data is "one column per category" (wide, spreadsheet
style) but you need "one row per observation" (long, tidy/database style)
— the format most plotting and modeling libraries expect.

---

## 5. `pivot` — long → wide (no aggregation)

```python
long = pd.melt(wide, id_vars="student", var_name="subject", value_name="score")
long.pivot(index="student", columns="subject", values="score")   # reverses the melt above
```

`pivot` requires each (index, columns) combination to be unique — if there
could be duplicates, use `pivot_table` instead (sheet 05), which aggregates.

---

## 6. `stack` / `unstack` — MultiIndex reshaping

```python
multi = df.set_index(["region", "product"])["sales"].unstack("product")
# columns become product values, one column per product

multi.stack()   # reverses unstack — back to a long Series with a MultiIndex
```

- `unstack`: pivot an inner index level into columns (long → wide).
- `stack`: pivot columns into an inner index level (wide → long).

---

## 7. `get_dummies` — one-hot encoding

```python
pd.get_dummies(df["product"])                   # one column per category, 0/1
pd.get_dummies(df, columns=["product"], drop_first=True)  # drop_first avoids the dummy-variable trap for linear models
```

---

## 8. `explode` — expand list-valued cells into rows

```python
nested = pd.DataFrame({"id": [1, 2], "tags": [["a", "b"], ["c"]]})
nested.explode("tags")
#    id tags
# 0   1    a
# 0   1    b
# 1   2    c
```

Common after `read_json` when a field contains arrays (e.g. API responses
with a `tags` or `items` list per record).

---

## 9. Decision Cheat Sheet

| I need to... | Use |
|---|---|
| Stack same-shaped tables (rows) | `pd.concat([...])` |
| Combine tables side-by-side on a shared key | `pd.merge(..., on=...)` |
| Combine tables on their index | `df1.join(df2)` |
| Turn columns into rows (unpivot) | `pd.melt(...)` |
| Turn rows into columns (no aggregation) | `df.pivot(...)` |
| Turn rows into columns WITH aggregation | `pd.pivot_table(...)` |
| Move a MultiIndex level into/out of columns | `.stack()` / `.unstack()` |
| Encode a categorical column as 0/1 columns | `pd.get_dummies(...)` |
| Flatten list-valued cells into separate rows | `df.explode(...)` |

**Next:** `07_pandas_time_series.md` — dates, resampling, and rolling
time-based windows.
