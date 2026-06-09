# Snowflake Learning Path (SQL-Focused)

A progressive curriculum that moves from core concepts to advanced features. Each module lists what to learn, why it matters, and runnable SQL to practice with. Work top to bottom — later modules assume the earlier ones.

---

## Module 0 — Setup & Mental Model

Before writing SQL, understand what makes Snowflake different from a traditional database.

**Concepts**
- Separation of **storage** (your data) and **compute** (virtual warehouses). You can scale them independently.
- A **virtual warehouse** is just a compute cluster you turn on/off and resize. You pay while it runs.
- Object hierarchy: `Account` → `Database` → `Schema` → `Table/View/etc.`
- Everything is SQL-addressable, including admin tasks.

**First commands**

```sql
-- See who you are and what you're using
SELECT CURRENT_USER(), CURRENT_ROLE(), CURRENT_WAREHOUSE(), CURRENT_DATABASE();

-- Set your working context
USE ROLE SYSADMIN;
USE WAREHOUSE COMPUTE_WH;
USE DATABASE MY_DB;
USE SCHEMA PUBLIC;
```

---

## Module 1 — Creating Objects

**Concepts**: databases, schemas, tables, data types, the fully-qualified name `db.schema.object`.

```sql
CREATE DATABASE IF NOT EXISTS learn_db;
CREATE SCHEMA IF NOT EXISTS learn_db.sales;

CREATE OR REPLACE TABLE learn_db.sales.customers (
    customer_id   INTEGER       NOT NULL,
    first_name    STRING,
    last_name     STRING,
    email         STRING,
    signup_date   DATE,
    lifetime_value NUMBER(12,2),
    PRIMARY KEY (customer_id)   -- informational only in Snowflake, not enforced
);

-- Inspect structure
DESCRIBE TABLE learn_db.sales.customers;
SHOW TABLES IN SCHEMA learn_db.sales;
```

> Note: Snowflake does **not** enforce primary/foreign keys or uniqueness (except `NOT NULL`). They are metadata used by the optimizer and documentation.

---

## Module 2 — Loading & Inserting Data

**Concepts**: `INSERT`, multi-row inserts, `INSERT ... SELECT`, the basics of bulk loading.

```sql
-- Simple inserts
INSERT INTO learn_db.sales.customers
    (customer_id, first_name, last_name, email, signup_date, lifetime_value)
VALUES
    (1, 'Ada',   'Lovelace', 'ada@example.com',   '2023-01-15', 1200.00),
    (2, 'Alan',  'Turing',   'alan@example.com',  '2023-03-02',  850.50),
    (3, 'Grace', 'Hopper',   'grace@example.com', '2024-06-21', 3300.00);

-- Copy rows from a query
CREATE OR REPLACE TABLE learn_db.sales.vip_customers AS
SELECT * FROM learn_db.sales.customers
WHERE lifetime_value > 1000;
```

Bulk loading (skim now, master in Module 11):

```sql
-- Pattern: stage -> file format -> COPY INTO
COPY INTO learn_db.sales.customers
FROM @my_stage/customers.csv
FILE_FORMAT = (TYPE = CSV SKIP_HEADER = 1);
```

---

## Module 3 — Core SELECT (SQL Fundamentals)

**Concepts**: filtering, sorting, limiting, aliases, `DISTINCT`, basic expressions.

```sql
SELECT
    customer_id,
    first_name || ' ' || last_name AS full_name,
    lifetime_value,
    ROUND(lifetime_value * 0.1, 2) AS reward_points
FROM learn_db.sales.customers
WHERE signup_date >= '2023-01-01'
  AND lifetime_value IS NOT NULL
ORDER BY lifetime_value DESC
LIMIT 10;

SELECT DISTINCT EXTRACT(YEAR FROM signup_date) AS signup_year
FROM learn_db.sales.customers;
```

---

## Module 4 — Aggregations & Grouping

**Concepts**: `GROUP BY`, aggregate functions, `HAVING`, `GROUP BY` ordinals, conditional aggregation.

```sql
SELECT
    EXTRACT(YEAR FROM signup_date)      AS signup_year,
    COUNT(*)                            AS num_customers,
    AVG(lifetime_value)                 AS avg_ltv,
    SUM(lifetime_value)                 AS total_ltv,
    COUNT_IF(lifetime_value > 1000)     AS num_high_value
FROM learn_db.sales.customers
GROUP BY 1
HAVING COUNT(*) > 0
ORDER BY signup_year;
```

---

## Module 5 — Joins

**Concepts**: `INNER`, `LEFT`, `RIGHT`, `FULL` joins, multi-table joins, self joins.

```sql
CREATE OR REPLACE TABLE learn_db.sales.orders (
    order_id     INTEGER,
    customer_id  INTEGER,
    order_date   DATE,
    amount       NUMBER(10,2)
);

INSERT INTO learn_db.sales.orders VALUES
    (101, 1, '2024-01-10', 250.00),
    (102, 1, '2024-02-14', 130.00),
    (103, 3, '2024-05-01', 900.00);

SELECT
    c.customer_id,
    c.first_name,
    COUNT(o.order_id)          AS order_count,
    COALESCE(SUM(o.amount), 0) AS total_spent
FROM learn_db.sales.customers c
LEFT JOIN learn_db.sales.orders o
       ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.first_name
ORDER BY total_spent DESC;
```

---

## Module 6 — Subqueries & CTEs

**Concepts**: scalar/`IN`/correlated subqueries, common table expressions, chained CTEs for readability.

```sql
-- CTE chain
WITH customer_totals AS (
    SELECT customer_id, SUM(amount) AS total
    FROM learn_db.sales.orders
    GROUP BY customer_id
),
ranked AS (
    SELECT customer_id, total,
           total - AVG(total) OVER () AS diff_from_avg
    FROM customer_totals
)
SELECT * FROM ranked
WHERE total > (SELECT AVG(total) FROM customer_totals);
```

---

## Module 7 — Window Functions

**Concepts**: `OVER`, `PARTITION BY`, ranking (`ROW_NUMBER`, `RANK`, `DENSE_RANK`), `LAG`/`LEAD`, running totals, frames.

```sql
SELECT
    customer_id,
    order_date,
    amount,
    ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date)        AS order_seq,
    SUM(amount)  OVER (PARTITION BY customer_id ORDER BY order_date
                       ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)    AS running_total,
    LAG(amount)  OVER (PARTITION BY customer_id ORDER BY order_date)        AS prev_amount
FROM learn_db.sales.orders;
```

This is the single highest-leverage SQL skill for analytics work — spend real time here.

---

## Module 8 — Semi-Structured Data (VARIANT)

**Concepts**: the `VARIANT` type, loading JSON, dot/bracket path access, `FLATTEN`, casting.

```sql
CREATE OR REPLACE TABLE learn_db.sales.events (
    id INTEGER,
    payload VARIANT
);

INSERT INTO learn_db.sales.events
SELECT 1, PARSE_JSON('{"user": "ada", "items": [{"sku": "A1", "qty": 2}, {"sku": "B2", "qty": 1}]}');

-- Access nested fields and explode arrays
SELECT
    e.id,
    e.payload:user::STRING        AS user_name,
    f.value:sku::STRING           AS sku,
    f.value:qty::INTEGER          AS qty
FROM learn_db.sales.events e,
     LATERAL FLATTEN(input => e.payload:items) f;
```

JSON handling is one of Snowflake's standout strengths — worth learning well.

---

## Module 9 — Views, Materialized Views & UDFs

**Concepts**: standard views, secure views, materialized views, SQL user-defined functions.

```sql
CREATE OR REPLACE VIEW learn_db.sales.v_customer_summary AS
SELECT c.customer_id, c.first_name,
       COALESCE(SUM(o.amount), 0) AS total_spent
FROM learn_db.sales.customers c
LEFT JOIN learn_db.sales.orders o USING (customer_id)
GROUP BY 1, 2;

-- A scalar SQL UDF
CREATE OR REPLACE FUNCTION learn_db.sales.fn_tier(ltv NUMBER)
RETURNS STRING
AS
$$
    CASE WHEN ltv >= 2000 THEN 'Gold'
         WHEN ltv >= 1000 THEN 'Silver'
         ELSE 'Bronze' END
$$;

SELECT customer_id, learn_db.sales.fn_tier(lifetime_value) AS tier
FROM learn_db.sales.customers;
```

---

## Module 10 — Time Travel & Cloning

**Concepts**: querying historical data, restoring dropped objects, zero-copy clones. These are signature Snowflake features.

```sql
-- Query the table as it was 1 hour ago
SELECT * FROM learn_db.sales.orders AT (OFFSET => -3600);

-- Query before a specific statement ran
SELECT * FROM learn_db.sales.orders BEFORE (STATEMENT => '<query_id>');

-- Recover a dropped table
DROP TABLE learn_db.sales.orders;
UNDROP TABLE learn_db.sales.orders;

-- Zero-copy clone (instant, no extra storage until data changes)
CREATE TABLE learn_db.sales.orders_sandbox CLONE learn_db.sales.orders;
```

---

## Module 11 — Stages, File Formats & Bulk Loading

**Concepts**: internal vs external stages, named file formats, `COPY INTO`, basic `Snowpipe` awareness.

```sql
CREATE OR REPLACE FILE FORMAT learn_db.sales.csv_ff
    TYPE = CSV SKIP_HEADER = 1 FIELD_OPTIONALLY_ENCLOSED_BY = '"';

CREATE OR REPLACE STAGE learn_db.sales.my_stage
    FILE_FORMAT = learn_db.sales.csv_ff;

-- After PUTting a file to the stage:
COPY INTO learn_db.sales.customers
FROM @learn_db.sales.my_stage/customers.csv
ON_ERROR = 'CONTINUE';

-- Validate without loading
COPY INTO learn_db.sales.customers
FROM @learn_db.sales.my_stage/customers.csv
VALIDATION_MODE = 'RETURN_ERRORS';
```

---

## Module 12 — Streams & Tasks (Pipelines)

**Concepts**: change tracking with streams, scheduled/triggered automation with tasks, building incremental pipelines in pure SQL.

```sql
-- A stream tracks row-level changes on a table
CREATE OR REPLACE STREAM learn_db.sales.orders_stream
    ON TABLE learn_db.sales.orders;

-- A task runs SQL on a schedule
CREATE OR REPLACE TASK learn_db.sales.process_new_orders
    WAREHOUSE = COMPUTE_WH
    SCHEDULE  = '5 MINUTE'
WHEN SYSTEM$STREAM_HAS_DATA('learn_db.sales.orders_stream')
AS
    INSERT INTO learn_db.sales.orders_audit
    SELECT *, CURRENT_TIMESTAMP() FROM learn_db.sales.orders_stream;

ALTER TASK learn_db.sales.process_new_orders RESUME;
```

---

## Module 13 — Access Control (RBAC)

**Concepts**: role-based access control, the privilege model, granting/revoking, role hierarchy.

```sql
USE ROLE SECURITYADMIN;

CREATE ROLE IF NOT EXISTS analyst;

GRANT USAGE   ON DATABASE learn_db            TO ROLE analyst;
GRANT USAGE   ON SCHEMA   learn_db.sales      TO ROLE analyst;
GRANT SELECT  ON ALL TABLES IN SCHEMA learn_db.sales TO ROLE analyst;
GRANT USAGE   ON WAREHOUSE COMPUTE_WH         TO ROLE analyst;

GRANT ROLE analyst TO USER some_user;
```

---

## Module 14 — Performance & Cost Optimization

**Concepts**: micro-partitions, clustering, pruning, warehouse sizing, result caching, `QUERY_HISTORY`.

```sql
-- Inspect how a query performs (use the Query Profile in the UI alongside this)
SELECT *
FROM TABLE(INFORMATION_SCHEMA.QUERY_HISTORY())
ORDER BY total_elapsed_time DESC
LIMIT 20;

-- Clustering for very large tables that filter on a consistent key
ALTER TABLE learn_db.sales.orders CLUSTER BY (order_date);
SELECT SYSTEM$CLUSTERING_INFORMATION('learn_db.sales.orders', '(order_date)');

-- Right-size and auto-suspend warehouses to control cost
ALTER WAREHOUSE COMPUTE_WH SET
    WAREHOUSE_SIZE = 'SMALL'
    AUTO_SUSPEND   = 60
    AUTO_RESUME    = TRUE;
```

Key ideas to internalize:
- Snowflake auto-partitions data; you rarely need manual clustering until tables are large (multi-TB).
- Filtering on selective columns enables **partition pruning** — the main lever for fast queries.
- Bigger warehouses run faster but cost proportionally more per second; size for the workload, not the maximum.

---

## Module 15 — Advanced Patterns

**Concepts**: `MERGE` (upserts), `QUALIFY`, `PIVOT`/`UNPIVOT`, recursive CTEs, multi-table inserts.

```sql
-- Upsert
MERGE INTO learn_db.sales.customers t
USING staging_customers s
   ON t.customer_id = s.customer_id
WHEN MATCHED THEN UPDATE SET t.lifetime_value = s.lifetime_value
WHEN NOT MATCHED THEN INSERT (customer_id, first_name, lifetime_value)
                       VALUES (s.customer_id, s.first_name, s.lifetime_value);

-- QUALIFY: filter on a window function without a subquery
SELECT customer_id, order_date, amount
FROM learn_db.sales.orders
QUALIFY ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date DESC) = 1;

-- PIVOT
SELECT *
FROM (SELECT customer_id, EXTRACT(YEAR FROM order_date) AS yr, amount
      FROM learn_db.sales.orders)
PIVOT (SUM(amount) FOR yr IN (2023, 2024)) AS p;

-- Recursive CTE
WITH RECURSIVE nums (n) AS (
    SELECT 1
    UNION ALL
    SELECT n + 1 FROM nums WHERE n < 10
)
SELECT * FROM nums;
```

---

## Suggested Pace & Practice

| Phase | Modules | Focus |
|-------|---------|-------|
| Week 1 | 0–5   | Objects, loading, core SELECT, joins |
| Week 2 | 6–9   | CTEs, window functions, JSON, views/UDFs |
| Week 3 | 10–13 | Time Travel, pipelines, stages, security |
| Week 4 | 14–15 | Performance, cost, advanced patterns |

**Build something real**: pick a public dataset (e.g., a CSV of sales or events), load it via Module 11, transform it with Modules 3–8, automate a refresh with Module 12, and tune it with Module 14. Doing one end-to-end project cements more than any amount of isolated practice.

**Reference**: the official Snowflake documentation and the `SNOWFLAKE.ACCOUNT_USAGE` / `INFORMATION_SCHEMA` views are your best companions throughout.
