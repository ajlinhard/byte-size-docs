# Postgres SQL Window Functions
# PostgreSQL Window Functions Cheatsheet

Window functions perform calculations across a set of rows **related to the current row** — without collapsing rows like `GROUP BY` does.

```sql
function_name(...) OVER (
  [PARTITION BY col1, col2, ...]
  [ORDER BY col3 [ASC|DESC], ...]
  [frame_clause]
)
```

---

## Anatomy of an OVER Clause

| Clause | Purpose |
|---|---|
| `PARTITION BY` | Divides rows into independent groups (like GROUP BY, but keeps all rows) |
| `ORDER BY` | Defines row order within each partition |
| `frame_clause` | Restricts which rows are included in the window frame |

### Frame Clause Syntax

```sql
{ ROWS | RANGE | GROUPS }
BETWEEN frame_start AND frame_end
```

| Keyword | Meaning |
|---|---|
| `UNBOUNDED PRECEDING` | Start of the partition |
| `N PRECEDING` | N rows/range units before current row |
| `CURRENT ROW` | The current row |
| `N FOLLOWING` | N rows/range units after current row |
| `UNBOUNDED FOLLOWING` | End of the partition |

**Default frame** (when `ORDER BY` is present): `RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW`

---

## Ranking Functions

| Function | Description |
|---|---|
| `ROW_NUMBER()` | Unique sequential integer, no ties (1, 2, 3, 4…) |
| `RANK()` | Rank with gaps on ties (1, 2, 2, 4…) |
| `DENSE_RANK()` | Rank without gaps on ties (1, 2, 2, 3…) |
| `NTILE(n)` | Divides rows into `n` buckets, returns bucket number |
| `PERCENT_RANK()` | Relative rank as a fraction: `(rank - 1) / (total rows - 1)` |
| `CUME_DIST()` | Cumulative distribution: fraction of rows ≤ current row |

```sql
-- Example: rank employees by salary within each department
SELECT
  name,
  department,
  salary,
  RANK()        OVER (PARTITION BY department ORDER BY salary DESC) AS rank,
  DENSE_RANK()  OVER (PARTITION BY department ORDER BY salary DESC) AS dense_rank,
  ROW_NUMBER()  OVER (PARTITION BY department ORDER BY salary DESC) AS row_num,
  NTILE(4)      OVER (PARTITION BY department ORDER BY salary DESC) AS quartile
FROM employees;
```

---

## Offset Functions

Access a different row relative to the current one.

| Function | Description |
|---|---|
| `LAG(col, n, default)` | Value from `n` rows **before** current row |
| `LEAD(col, n, default)` | Value from `n` rows **after** current row |
| `FIRST_VALUE(col)` | First value in the window frame |
| `LAST_VALUE(col)` | Last value in the window frame |
| `NTH_VALUE(col, n)` | nth value in the window frame |

> ⚠️ `LAST_VALUE` and `NTH_VALUE` require an explicit frame of `ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING` to work as expected, since the default frame stops at the current row.

```sql
-- Month-over-month revenue change
SELECT
  month,
  revenue,
  LAG(revenue, 1, 0)  OVER (ORDER BY month) AS prev_revenue,
  LEAD(revenue, 1, 0) OVER (ORDER BY month) AS next_revenue,
  revenue - LAG(revenue) OVER (ORDER BY month) AS change
FROM monthly_revenue;

-- First and last sale in each category
SELECT
  category,
  sale_date,
  amount,
  FIRST_VALUE(amount) OVER (PARTITION BY category ORDER BY sale_date
    ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS first_sale,
  LAST_VALUE(amount)  OVER (PARTITION BY category ORDER BY sale_date
    ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_sale
FROM sales;
```

---

## Aggregate Window Functions

Any aggregate can be used as a window function by adding `OVER (...)`.

| Function | Description |
|---|---|
| `SUM(col)` | Running or partitioned sum |
| `AVG(col)` | Running or partitioned average |
| `COUNT(col)` | Running or partitioned count |
| `MIN(col)` | Minimum within the frame |
| `MAX(col)` | Maximum within the frame |

```sql
-- Running total and moving 3-row average
SELECT
  sale_date,
  amount,
  SUM(amount) OVER (ORDER BY sale_date
    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_total,
  AVG(amount) OVER (ORDER BY sale_date
    ROWS BETWEEN 2 PRECEDING AND CURRENT ROW)         AS moving_avg_3
FROM sales;

-- Percentage of department total
SELECT
  name,
  department,
  salary,
  ROUND(100.0 * salary / SUM(salary) OVER (PARTITION BY department), 2) AS pct_of_dept
FROM employees;
```

---

## Statistical Functions

| Function | Description |
|---|---|
| `CORR(y, x)` | Pearson correlation coefficient |
| `COVAR_POP(y, x)` | Population covariance |
| `COVAR_SAMP(y, x)` | Sample covariance |
| `STDDEV_POP(col)` | Population standard deviation |
| `STDDEV_SAMP(col)` | Sample standard deviation |
| `VAR_POP(col)` | Population variance |
| `VAR_SAMP(col)` | Sample variance |
| `REGR_SLOPE(y, x)` | Slope of a linear regression line |
| `REGR_INTERCEPT(y, x)` | Intercept of a linear regression line |

```sql
SELECT
  department,
  salary,
  ROUND(AVG(salary)         OVER (PARTITION BY department)::numeric, 2) AS dept_avg,
  ROUND(STDDEV_POP(salary)  OVER (PARTITION BY department)::numeric, 2) AS dept_stddev
FROM employees;
```

---

## Named Windows (WINDOW clause)

Reuse window definitions to avoid repetition.

```sql
SELECT
  name,
  salary,
  RANK()        OVER w AS rank,
  DENSE_RANK()  OVER w AS dense_rank,
  AVG(salary)   OVER w AS dept_avg
FROM employees
WINDOW w AS (PARTITION BY department ORDER BY salary DESC);
```

You can also extend a named window inline:

```sql
WINDOW w AS (PARTITION BY department)
-- then use:
SUM(salary) OVER (w ORDER BY hire_date)
```

---

## FILTER with Window Functions

```sql
-- Sum only rows where status = 'completed'
SELECT
  month,
  SUM(amount) FILTER (WHERE status = 'completed')
    OVER (ORDER BY month) AS running_completed_total
FROM orders;
```

---

## Common Patterns

### De-duplicate: keep latest record per group
```sql
SELECT * FROM (
  SELECT *, ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY created_at DESC) AS rn
  FROM events
) t WHERE rn = 1;
```

### Top-N per group
```sql
SELECT * FROM (
  SELECT *, RANK() OVER (PARTITION BY department ORDER BY salary DESC) AS rnk
  FROM employees
) t WHERE rnk <= 3;
```

### Gap detection (find missing sequence values)
```sql
SELECT id + 1 AS gap_start
FROM (
  SELECT id, LEAD(id) OVER (ORDER BY id) AS next_id
  FROM orders
) t
WHERE next_id - id > 1;
```

### Sessionization (group events into sessions)
```sql
SELECT
  user_id,
  event_time,
  SUM(is_new_session) OVER (PARTITION BY user_id ORDER BY event_time) AS session_id
FROM (
  SELECT *,
    CASE WHEN event_time - LAG(event_time) OVER (PARTITION BY user_id ORDER BY event_time)
              > INTERVAL '30 minutes'
         THEN 1 ELSE 0
    END AS is_new_session
  FROM events
) t;
```

---

## Quick Reference: ROWS vs RANGE vs GROUPS

| Mode | Frame unit | Notes |
|---|---|---|
| `ROWS` | Physical rows | Precise; ignores ties |
| `RANGE` | Logical range based on ORDER BY value | Default; groups tied values |
| `GROUPS` | Groups of tied ORDER BY values | Available since Postgres 11 |

---

## Performance Tips

- Window functions run **after** `WHERE`, `GROUP BY`, and `HAVING` — filter early to reduce the working set.
- An index on `(PARTITION BY col, ORDER BY col)` can eliminate a sort step.
- Use `EXPLAIN ANALYZE` — look for `WindowAgg` and `Sort` nodes.
- Avoid computing the same window multiple times; use a `WINDOW` clause or a CTE.
- For very large partitions, `ROWS` mode is usually faster than `RANGE`.
