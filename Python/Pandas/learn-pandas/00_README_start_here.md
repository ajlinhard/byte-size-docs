# NumPy & Pandas: Beginner → Advanced Reference Series

A set of hands-on markdown cheat sheets covering NumPy and pandas for data
science and data engineering, in Python. Each sheet is self-contained,
code-first, and ordered by difficulty. Work through them in order, or jump
to whichever topic you need.

## How to use these sheets

- Every section has runnable Python snippets — paste them into a notebook or
  `.py` file and experiment.
- Comments in code explain *why*, prose explains *when*.
- "Gotcha" callouts flag the mistakes people actually make in production code.
- Sheets 8–9 are aimed specifically at **data engineering** concerns
  (memory, I/O, scale) rather than pure analysis.

## Reading order

| # | File | Level | Focus |
|---|------|-------|-------|
| 1 | `01_numpy_fundamentals.md` | Beginner | Arrays, broadcasting, vectorization, linear algebra |
| 2 | `02_pandas_basics.md` | Beginner | Series/DataFrame, I/O, first look at data |
| 3 | `03_pandas_indexing_selection.md` | Beginner–Intermediate | `loc`/`iloc`, boolean masks, MultiIndex basics |
| 4 | `04_pandas_data_cleaning.md` | Intermediate | Missing data, dtypes, strings, outliers |
| 5 | `05_pandas_groupby_transform.md` | Intermediate | Split-apply-combine, pivot tables, windows |
| 6 | `06_pandas_merge_reshape.md` | Intermediate | concat/merge/join, melt/pivot, stack/unstack |
| 7 | `07_pandas_time_series.md` | Intermediate–Advanced | Datetime indexing, resampling, rolling windows |
| 8 | `08_pandas_performance_data_engineering.md` | Advanced | Memory, dtypes, chunking, Parquet, SQL, `eval`/`query` |
| 9 | `09_pandas_advanced_topics.md` | Advanced | Custom accessors, styling, extension types, testing, pandas-vs-SQL |

## Setup

```bash
pip install numpy pandas pyarrow openpyxl sqlalchemy
```

```python
import numpy as np
import pandas as pd

# Version check — behavior below assumes pandas >= 2.0
print(np.__version__, pd.__version__)
```

## Conventions used throughout

- `df` = DataFrame, `s` = Series, `arr` = NumPy array.
- `# ->` comments show what a line returns/prints.
- Examples build small, throwaway data inline so every snippet runs standalone.
