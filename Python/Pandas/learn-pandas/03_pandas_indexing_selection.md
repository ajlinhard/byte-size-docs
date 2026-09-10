# Pandas Indexing & Selection

```python
import numpy as np
import pandas as pd

df = pd.DataFrame({
    "name": ["Ana", "Bo", "Cy", "Dee"],
    "age": [25, 31, 45, 29],
    "city": ["NYC", "LA", "NYC", "SF"],
}, index=["r1", "r2", "r3", "r4"])
```

---

## 1. The Golden Rule: `loc` = labels, `iloc` = positions

| Selector | Basis | Example |
|---|---|---|
| `df.loc[...]` | Label-based (row/column *names*) | `df.loc["r1", "age"]` |
| `df.iloc[...]` | Position-based (integer index, 0-based) | `df.iloc[0, 1]` |
| `df.at[...]` | Label-based, single scalar (fast) | `df.at["r1", "age"]` |
| `df.iat[...]` | Position-based, single scalar (fast) | `df.iat[0, 1]` |

```python
df.loc["r1"]               # row by label -> Series
df.loc["r1", "age"]        # single cell by label
df.loc[["r1", "r3"], ["name", "age"]]   # rows & columns by label lists
df.loc["r1":"r3"]          # label slicing is INCLUSIVE of the endpoint

df.iloc[0]                  # first row by position
df.iloc[0, 1]                # cell at row 0, col 1
df.iloc[0:2, 0:2]            # position slicing is EXCLUSIVE of the endpoint (like Python lists)
df.iloc[-1]                   # last row
```

**Gotcha:** `loc` slices are inclusive on both ends; `iloc` slices behave
like normal Python slicing (exclusive on the end). This trips up almost
everyone at least once.

---

## 2. Boolean Indexing

```python
df[df["age"] > 28]                       # rows where condition is True
df[(df["age"] > 28) & (df["city"] == "NYC")]   # combine with & / | — always parenthesize
df[~(df["city"] == "NYC")]                # negate with ~
df.loc[df["age"] > 28, "name"]            # filter rows AND select a column in one call
df.loc[df["age"] > 28, ["name", "city"]]  # filter rows AND select multiple columns
```

---

## 3. `query()` — readable filters as strings

```python
df.query("age > 28 and city == 'NYC'")
df.query("age > @threshold")     # reference external Python variables with @
threshold = 30
df.query("age > @threshold")
```

`query()` is often faster on large frames (uses `numexpr` under the hood if
installed) and reads closer to SQL.

---

## 4. `isin`, `between`, `filter`

```python
df[df["city"].isin(["NYC", "SF"])]          # membership test
df[df["age"].between(25, 40)]                # inclusive range check
df.filter(items=["name", "age"])              # select columns by name
df.filter(like="a")                            # columns whose name CONTAINS "a"
df.filter(regex="^c")                          # columns matching a regex
```

---

## 5. Setting Values

```python
df.loc["r1", "age"] = 26                 # single cell
df.loc[df["age"] > 40, "city"] = "Other" # conditional bulk update
df["age"] = df["age"] + 1                 # whole-column vectorized update
```

### The `SettingWithCopyWarning`

```python
# DANGEROUS: subset may be a view OR a copy — pandas can't guarantee which
subset = df[df["age"] > 28]
subset["age"] = 0   # -> SettingWithCopyWarning, may silently not update df

# SAFE: be explicit about copying, or do it in one loc call
subset = df[df["age"] > 28].copy()
subset["age"] = 0                          # fine — subset is independent now

df.loc[df["age"] > 28, "age"] = 0          # fine — single, unambiguous operation
```

**Rule:** if you're going to filter *then* mutate, either `.copy()` the
filtered result, or fold filter + assignment into one `.loc[...]` call.

---

## 6. `reset_index` / `set_index`

```python
df.reset_index()                     # move the index back into a column, get a fresh RangeIndex
df.reset_index(drop=True)             # discard the old index entirely
df.set_index("name")                  # promote a column to be the index
df.set_index(["city", "name"])        # -> MultiIndex (see below)
```

---

## 7. MultiIndex (Hierarchical Indexing)

```python
multi = df.set_index(["city", "name"])
multi
#                age
# city name
# NYC  Ana        25
# LA   Bo         31
# NYC  Cy         45
# SF   Dee        29

multi.loc["NYC"]                    # all rows where city == NYC
multi.loc[("NYC", "Ana")]           # a specific (city, name) row
multi.loc[("NYC", "Ana"), "age"]    # a specific cell

multi.index.get_level_values(0)     # -> outer level values
multi.index.get_level_values("city")

multi.swaplevel()                    # swap level order
multi.sort_index(level="city")       # sort by a specific level
```

### `xs` — cross-section without dropping into tuples

```python
multi.xs("NYC", level="city")        # all rows at city == NYC, drops that level
```

### `pd.IndexSlice` — slicing a MultiIndex on both levels at once

```python
idx = pd.IndexSlice
multi.loc[idx["NYC":"SF", :], :]     # slice on the outer level, keep all of inner
```

---

## 8. Index Alignment

Pandas automatically aligns on the index during arithmetic — this is
powerful but surprises newcomers:

```python
s1 = pd.Series([1, 2, 3], index=["a", "b", "c"])
s2 = pd.Series([10, 20, 30], index=["b", "c", "d"])

s1 + s2
# a     NaN   <- "a" only in s1
# b    12.0
# c    23.0
# d     NaN   <- "d" only in s2
```

Use `.add(s2, fill_value=0)` to treat missing labels as 0 instead of
producing `NaN`:

```python
s1.add(s2, fill_value=0)
```

---

## 9. Quick Reference Table

| Task | Code |
|---|---|
| Single column | `df["col"]` |
| Multiple columns | `df[["col1", "col2"]]` |
| Row by label | `df.loc["label"]` |
| Row by position | `df.iloc[0]` |
| Cell by label (fast) | `df.at["label", "col"]` |
| Cell by position (fast) | `df.iat[0, 0]` |
| Filter rows | `df[df["col"] > x]` |
| Filter rows + select cols | `df.loc[df["col"] > x, ["a", "b"]]` |
| Readable filter | `df.query("col > 5")` |
| Membership filter | `df[df["col"].isin([...])]` |

**Next:** `04_pandas_data_cleaning.md` — missing data, dtypes, string
cleanup, duplicates, and outliers.
