# PostgreSQL Materialized Views: A Deep Dive

## Table of Contents

1. [What Is a Materialized View?](#what-is-a-materialized-view)
2. [Regular Views vs. Materialized Views](#regular-views-vs-materialized-views)
3. [Creating and Managing Materialized Views](#creating-and-managing-materialized-views)
4. [Refreshing Strategies](#refreshing-strategies)
5. [Indexing Materialized Views](#indexing-materialized-views)
6. [Use Cases](#use-cases)
7. [Trade-offs](#trade-offs)
8. [Advanced Patterns](#advanced-patterns)
9. [Optimization Techniques](#optimization-techniques)
10. [Monitoring and Maintenance](#monitoring-and-maintenance)
11. [Common Pitfalls](#common-pitfalls)

---

## What Is a Materialized View?

A **materialized view** is a database object that contains the results of a query stored physically on disk — unlike a regular view, which is just a named query that executes at runtime. Think of it as a snapshot of a query's results, cached and queryable like a table.

```sql
-- A materialized view persists the result of this query to disk
CREATE MATERIALIZED VIEW monthly_revenue AS
SELECT
    DATE_TRUNC('month', order_date) AS month,
    SUM(total_amount)               AS revenue,
    COUNT(*)                        AS order_count
FROM orders
GROUP BY DATE_TRUNC('month', order_date);
```

After creation, `monthly_revenue` behaves like a table. Querying it never touches the `orders` table — it reads the pre-computed rows directly.

---

## Regular Views vs. Materialized Views

| Feature | Regular View | Materialized View |
|---|---|---|
| Data storage | None — executes on read | Physical rows on disk |
| Query performance | Same as base query | Dramatically faster (pre-computed) |
| Data freshness | Always current | Stale until refreshed |
| Indexable | No | Yes |
| Write-through | Via rules/triggers | No |
| Storage cost | None | Proportional to result size |

```sql
-- Regular view: re-runs the full aggregation every time you query it
CREATE VIEW monthly_revenue_view AS
SELECT DATE_TRUNC('month', order_date) AS month, SUM(total_amount) AS revenue
FROM orders
GROUP BY 1;

-- Materialized view: runs once, stores the rows
CREATE MATERIALIZED VIEW monthly_revenue_mat AS
SELECT DATE_TRUNC('month', order_date) AS month, SUM(total_amount) AS revenue
FROM orders
GROUP BY 1;
```

The first query against `monthly_revenue_view` on a 100M-row `orders` table will perform a full scan and aggregation. The equivalent query against `monthly_revenue_mat` returns a handful of pre-computed rows instantly.

---

## Creating and Managing Materialized Views

### Basic Creation

```sql
CREATE MATERIALIZED VIEW view_name AS
query
[WITH [NO] DATA];
```

The `WITH NO DATA` clause creates the structure without populating it — useful when you want to define the view before data is ready or want to add indexes before the first populate.

```sql
-- Create empty (no data loaded yet)
CREATE MATERIALIZED VIEW sales_summary WITH NO DATA AS
SELECT
    product_id,
    region,
    SUM(amount)    AS total_sales,
    AVG(amount)    AS avg_sale,
    COUNT(*)       AS sale_count
FROM sales
GROUP BY product_id, region;

-- Add indexes while the view is empty (fast, no data to index)
CREATE INDEX ON sales_summary (product_id);
CREATE INDEX ON sales_summary (region);

-- Now populate it
REFRESH MATERIALIZED VIEW sales_summary;
```

### Dropping a Materialized View

```sql
-- Drop the view
DROP MATERIALIZED VIEW monthly_revenue;

-- Drop if it exists (no error if absent)
DROP MATERIALIZED VIEW IF EXISTS monthly_revenue;

-- Cascade: also drops dependent objects
DROP MATERIALIZED VIEW monthly_revenue CASCADE;
```

### Inspecting Materialized Views

```sql
-- List all materialized views in the current database
SELECT
    schemaname,
    matviewname,
    matviewowner,
    ispopulated,
    definition
FROM pg_matviews
ORDER BY schemaname, matviewname;
```

---

## Refreshing Strategies

This is the most operationally critical aspect of materialized views. Data becomes stale the moment the underlying tables change; `REFRESH` re-runs the defining query and replaces stored data.

### Basic Refresh

```sql
REFRESH MATERIALIZED VIEW monthly_revenue;
```

By default this acquires an `ExclusiveLock`, which **blocks all reads** for the duration of the refresh. On a large view, this can mean seconds or minutes of downtime.

### Concurrent Refresh (No Read Blocking)

```sql
REFRESH MATERIALIZED VIEW CONCURRENTLY monthly_revenue;
```

`CONCURRENTLY` swaps in the new data without blocking reads. The trade-off: it requires at least one `UNIQUE` index on the view, and it takes longer because Postgres must diff the old and new data sets.

```sql
-- Prerequisite: unique index for concurrent refresh
CREATE UNIQUE INDEX ON monthly_revenue (month);

-- Now this can run without blocking readers
REFRESH MATERIALIZED VIEW CONCURRENTLY monthly_revenue;
```

### Refresh Approaches by Use Case

**Scheduled refresh (cron / pg_cron)**

```sql
-- Using pg_cron extension (install once per database)
CREATE EXTENSION pg_cron;

-- Refresh every hour at :05
SELECT cron.schedule(
    'refresh-monthly-revenue',
    '5 * * * *',
    'REFRESH MATERIALIZED VIEW CONCURRENTLY monthly_revenue'
);
```

**Trigger-based refresh (near real-time)**

```sql
-- A function that refreshes the view
CREATE OR REPLACE FUNCTION refresh_monthly_revenue()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY monthly_revenue;
    RETURN NULL;
END;
$$;

-- Trigger fires after any change to the orders table
CREATE TRIGGER trg_refresh_monthly_revenue
AFTER INSERT OR UPDATE OR DELETE ON orders
FOR EACH STATEMENT EXECUTE FUNCTION refresh_monthly_revenue();
```

> **Warning:** Trigger-based refresh couples write latency directly to refresh time. Only appropriate for small views or low-write-volume tables.

**Application-controlled refresh**

Rather than automating refresh at the database level, many teams refresh explicitly after known bulk operations:

```sql
-- After loading yesterday's data
BEGIN;
  CALL load_orders_batch(:batch_date);
  REFRESH MATERIALIZED VIEW CONCURRENTLY monthly_revenue;
  REFRESH MATERIALIZED VIEW CONCURRENTLY product_rankings;
COMMIT;
```

### Checking Freshness

```sql
-- pg_stat_user_tables tracks last autovacuum / analyze but not mat view refreshes.
-- Track refresh times manually:
CREATE TABLE matview_refresh_log (
    view_name   TEXT        NOT NULL,
    refreshed_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Call after each refresh
INSERT INTO matview_refresh_log (view_name) VALUES ('monthly_revenue');

-- Query to see how stale each view is
SELECT
    view_name,
    refreshed_at,
    NOW() - refreshed_at AS age
FROM matview_refresh_log
ORDER BY refreshed_at DESC;
```

---

## Indexing Materialized Views

Indexing is one of the most powerful features distinguishing materialized views from regular views.

### B-Tree Indexes (Most Common)

```sql
CREATE MATERIALIZED VIEW orders_summary AS
SELECT
    customer_id,
    product_category,
    DATE_TRUNC('month', order_date) AS month,
    SUM(amount)                     AS total
FROM orders
GROUP BY 1, 2, 3;

-- Support fast lookups by customer
CREATE INDEX ON orders_summary (customer_id);

-- Support fast lookups by category and month
CREATE INDEX ON orders_summary (product_category, month DESC);
```

### Unique Indexes (Required for Concurrent Refresh)

```sql
-- Unique index is mandatory for CONCURRENTLY refresh
-- Choose a column or combination that is truly unique in the result set
CREATE UNIQUE INDEX ON orders_summary (customer_id, product_category, month);
```

### Partial Indexes

```sql
-- Index only recent data — much smaller, faster to maintain
CREATE INDEX ON orders_summary (customer_id)
WHERE month >= DATE_TRUNC('month', NOW() - INTERVAL '3 months');
```

### Expression Indexes

```sql
-- Case-insensitive lookups on a text column
CREATE INDEX ON orders_summary (LOWER(product_category));
```

---

## Use Cases

### 1. Reporting and Business Intelligence Dashboards

The canonical use case. Dashboards typically query aggregated data over large time windows. Materializing those aggregations eliminates repeated full-table scans.

```sql
CREATE MATERIALIZED VIEW kpi_dashboard AS
SELECT
    DATE_TRUNC('day', created_at)                       AS day,
    COUNT(*)                                            AS new_users,
    COUNT(*) FILTER (WHERE subscription_tier = 'pro')  AS new_pro_users,
    SUM(lifetime_value)                                 AS total_ltv
FROM users
GROUP BY DATE_TRUNC('day', created_at)
ORDER BY day;

CREATE UNIQUE INDEX ON kpi_dashboard (day);
```

### 2. Expensive JOIN Pre-computation

When multiple tables must be joined repeatedly (especially across schemas or servers via FDW), materializing the join can drastically reduce latency.

```sql
CREATE MATERIALIZED VIEW enriched_orders AS
SELECT
    o.id            AS order_id,
    o.created_at,
    c.name          AS customer_name,
    c.country,
    p.name          AS product_name,
    p.category,
    o.quantity,
    o.unit_price,
    o.quantity * o.unit_price AS line_total
FROM orders o
JOIN customers c ON c.id = o.customer_id
JOIN products  p ON p.id = o.product_id;

CREATE INDEX ON enriched_orders (customer_name);
CREATE INDEX ON enriched_orders (category, created_at DESC);
```

### 3. Full-Text Search

Pre-building `tsvector` columns avoids regenerating them on every search.

```sql
CREATE MATERIALIZED VIEW article_search AS
SELECT
    id,
    title,
    to_tsvector('english', title || ' ' || body) AS search_vector
FROM articles;

CREATE INDEX ON article_search USING GIN (search_vector);

-- Fast full-text search, no on-the-fly tsvector generation
SELECT id, title
FROM article_search
WHERE search_vector @@ plainto_tsquery('english', 'postgres performance');
```

### 4. Geospatial Query Caching (PostGIS)

PostGIS operations like `ST_Within` or `ST_Distance` are expensive. Materializing results is a common pattern.

```sql
CREATE MATERIALIZED VIEW stores_in_metro_areas AS
SELECT
    s.id,
    s.name,
    s.location,
    m.metro_name
FROM stores s
JOIN metro_areas m ON ST_Within(s.location, m.boundary);

CREATE INDEX ON stores_in_metro_areas USING GIST (location);
```

### 5. API Response Caching at the Database Layer

Rather than caching JSON in Redis, some architectures serialize results directly into a materialized view.

```sql
CREATE MATERIALIZED VIEW product_catalog_json AS
SELECT
    category,
    JSON_AGG(
        JSON_BUILD_OBJECT(
            'id',    id,
            'name',  name,
            'price', price,
            'sku',   sku
        ) ORDER BY name
    ) AS products
FROM products
WHERE active = TRUE
GROUP BY category;

CREATE UNIQUE INDEX ON product_catalog_json (category);
```

---

## Trade-offs

### Staleness

This is the fundamental tension. The moment the underlying data changes, the materialized view is out of sync. Teams must decide:

- **How stale is acceptable?** Hourly reporting can tolerate an hour-old snapshot. Real-time fraud detection cannot.
- **What is the cost of refresh?** A 1TB materialized view can take 10+ minutes to refresh even with good I/O.

### Storage Cost

Materialized views duplicate data. A view that joins and aggregates a 500GB table may itself be 5GB or 500GB depending on reduction ratio. Factor this into storage planning and backup/restore time.

### Refresh Contention

Even `CONCURRENTLY` refresh takes a `ShareUpdateExclusiveLock`, preventing concurrent refreshes on the same view. If refresh takes 2 minutes and you schedule it every minute, locks will queue up.

```sql
-- Safe pattern: skip refresh if one is already running
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_locks l
        JOIN pg_class c ON c.oid = l.relation
        WHERE c.relname = 'monthly_revenue'
          AND l.mode = 'ShareUpdateExclusiveLock'
    ) THEN
        REFRESH MATERIALIZED VIEW CONCURRENTLY monthly_revenue;
    END IF;
END $$;
```

### No Write-Through

You cannot `INSERT`, `UPDATE`, or `DELETE` rows in a materialized view. All writes go to base tables; the view only reflects them after refresh.

### Query Planner Awareness

The Postgres query planner will not automatically route a query against a base table to a materialized view even if the view would be faster. Queries must explicitly target the materialized view by name.

---

## Advanced Patterns

### Layered / Chained Materialized Views

You can build materialized views on top of other materialized views. This is useful for multi-level rollups but creates a dependency chain: refreshing must happen bottom-up.

```sql
-- Level 1: Daily rollup
CREATE MATERIALIZED VIEW sales_daily AS
SELECT DATE_TRUNC('day', sold_at) AS day, product_id, SUM(amount) AS total
FROM sales
GROUP BY 1, 2;

CREATE UNIQUE INDEX ON sales_daily (day, product_id);

-- Level 2: Monthly rollup from the daily rollup
CREATE MATERIALIZED VIEW sales_monthly AS
SELECT DATE_TRUNC('month', day) AS month, product_id, SUM(total) AS total
FROM sales_daily
GROUP BY 1, 2;

CREATE UNIQUE INDEX ON sales_monthly (month, product_id);

-- Refresh order matters: daily first, then monthly
REFRESH MATERIALIZED VIEW CONCURRENTLY sales_daily;
REFRESH MATERIALIZED VIEW CONCURRENTLY sales_monthly;
```

### Incremental-Style Refresh with Watermarks

Postgres lacks native incremental refresh (Oracle and Snowflake have it), but you can simulate it for append-only datasets.

```sql
-- Track the last-processed ID or timestamp
CREATE TABLE matview_watermarks (
    view_name    TEXT PRIMARY KEY,
    last_id      BIGINT,
    updated_at   TIMESTAMPTZ DEFAULT NOW()
);

INSERT INTO matview_watermarks VALUES ('sales_daily_incremental', 0, NOW());

-- "Incremental" refresh function: only processes new rows
CREATE OR REPLACE FUNCTION refresh_sales_incremental() RETURNS VOID AS $$
DECLARE
    v_last_id BIGINT;
BEGIN
    SELECT last_id INTO v_last_id
    FROM matview_watermarks
    WHERE view_name = 'sales_daily_incremental';

    -- Insert only the new rows
    INSERT INTO sales_daily_incremental
    SELECT DATE_TRUNC('day', sold_at) AS day, product_id, SUM(amount) AS total
    FROM sales
    WHERE id > v_last_id
    GROUP BY 1, 2
    ON CONFLICT (day, product_id)
    DO UPDATE SET total = sales_daily_incremental.total + EXCLUDED.total;

    -- Advance the watermark
    UPDATE matview_watermarks
    SET last_id = (SELECT MAX(id) FROM sales),
        updated_at = NOW()
    WHERE view_name = 'sales_daily_incremental';
END;
$$ LANGUAGE plpgsql;
```

> Note: This pattern only works correctly for strictly append-only sources. Updates to historical records require a full refresh or more complex delta tracking.

### Partitioned Base Tables + Materialized Views

When the underlying table is partitioned (e.g., by month), you can build a materialized view per partition for parallelized refresh.

```sql
-- Partition-scoped views
CREATE MATERIALIZED VIEW revenue_2024_01 AS
SELECT product_id, SUM(amount) AS total
FROM orders_2024_01  -- a specific partition
GROUP BY product_id;

CREATE MATERIALIZED VIEW revenue_2024_02 AS
SELECT product_id, SUM(amount) AS total
FROM orders_2024_02
GROUP BY product_id;

-- Only the current month's view needs frequent refresh
-- Historical partitions rarely change after the month closes
REFRESH MATERIALIZED VIEW CONCURRENTLY revenue_2024_02;
```

### Using Materialized Views with Foreign Data Wrappers (FDW)

One of the highest-value use cases: materializing results from remote sources to avoid repeated network round-trips.

```sql
-- Remote table via postgres_fdw
CREATE SERVER analytics_server FOREIGN DATA WRAPPER postgres_fdw
OPTIONS (host 'analytics-db.internal', dbname 'analytics');

CREATE FOREIGN TABLE remote_events (
    event_id   BIGINT,
    event_type TEXT,
    occurred_at TIMESTAMPTZ
) SERVER analytics_server OPTIONS (table_name 'events');

-- Materialize a local cache of the remote data
CREATE MATERIALIZED VIEW local_events_cache AS
SELECT * FROM remote_events
WHERE occurred_at >= NOW() - INTERVAL '30 days';

CREATE INDEX ON local_events_cache (event_type, occurred_at DESC);
```

### Schema-Level Isolation

Keeping materialized views in a dedicated schema aids organization and permission management.

```sql
CREATE SCHEMA reporting;

CREATE MATERIALIZED VIEW reporting.revenue_by_region AS
SELECT region, SUM(amount) AS total
FROM sales
GROUP BY region;

-- Grant read access to the reporting role without touching base tables
GRANT USAGE ON SCHEMA reporting TO reporting_role;
GRANT SELECT ON ALL TABLES IN SCHEMA reporting TO reporting_role;
```

---

## Optimization Techniques

### 1. Right-size the Granularity

Avoid materializing raw data when you only need aggregates. The finer the granularity, the larger the view and the longer the refresh.

```sql
-- Bad: materializing row-level data with minor transforms
CREATE MATERIALIZED VIEW orders_with_tax AS
SELECT *, amount * 1.08 AS amount_with_tax FROM orders;
-- This is the same size as orders! Just use a regular view.

-- Good: materializing a meaningful aggregation
CREATE MATERIALIZED VIEW orders_tax_summary AS
SELECT
    DATE_TRUNC('week', created_at) AS week,
    SUM(amount)                    AS subtotal,
    SUM(amount * 0.08)             AS tax,
    SUM(amount * 1.08)             AS total
FROM orders
GROUP BY 1;
```

### 2. Filter Aggressively with WHERE Clauses

If queries only ever look at recent or active data, restrict the materialized view to that slice.

```sql
-- Only materialize the last 90 days — much faster refresh, smaller storage
CREATE MATERIALIZED VIEW recent_signups AS
SELECT user_id, plan, created_at, referral_source
FROM users
WHERE created_at >= NOW() - INTERVAL '90 days'
  AND status = 'active';
```

### 3. Choose the Right Index Types

| Access Pattern | Best Index |
|---|---|
| Equality lookups (`=`) | B-tree |
| Range queries (`>`, `BETWEEN`) | B-tree |
| Full-text search | GIN on `tsvector` |
| Array contains / overlap | GIN |
| Geospatial (`ST_Within`, etc.) | GiST |
| Low-cardinality bitmask queries | BRIN (append-only data) |

```sql
-- Composite index: put equality-tested columns first, range-tested columns last
CREATE INDEX ON orders_summary (region, product_category, month DESC);
```

### 4. Avoid SELECT *

Only materialize the columns you actually query. This reduces storage, refresh time, and makes the query planner's job easier.

```sql
-- Bad: includes 40+ columns, most never queried in reports
CREATE MATERIALIZED VIEW customer_activity AS
SELECT * FROM customers JOIN activity_log USING (customer_id);

-- Good: only what reporting needs
CREATE MATERIALIZED VIEW customer_activity AS
SELECT
    c.id,
    c.country,
    COUNT(a.id)              AS event_count,
    MAX(a.occurred_at)       AS last_active_at
FROM customers c
JOIN activity_log a ON a.customer_id = c.id
GROUP BY c.id, c.country;
```

### 5. Parallel Refresh with `max_parallel_workers_per_gather`

Materialized view refresh can use parallel query workers if configured.

```sql
-- Allow more parallel workers for the refresh session
SET max_parallel_workers_per_gather = 8;
REFRESH MATERIALIZED VIEW CONCURRENTLY large_aggregation;
RESET max_parallel_workers_per_gather;
```

### 6. Analyze After Refresh

After a refresh, Postgres statistics are stale. Run `ANALYZE` so the query planner has accurate row counts and column histograms.

```sql
REFRESH MATERIALIZED VIEW CONCURRENTLY orders_summary;
ANALYZE orders_summary;
```

### 7. VACUUM to Reclaim Space

`REFRESH MATERIALIZED VIEW` (non-concurrent) truncates and re-populates, which is clean. `CONCURRENTLY` leaves dead tuples from the diff process — these need vacuuming.

```sql
-- After several concurrent refreshes, bloat can accumulate
VACUUM (ANALYZE) orders_summary;
```

### 8. Use `EXPLAIN (ANALYZE, BUFFERS)` to Confirm the View Is Being Used

```sql
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT region, SUM(total_sales)
FROM orders_summary
WHERE month >= '2024-01-01'
GROUP BY region;
```

Look for `Seq Scan` or `Index Scan on orders_summary` (good) rather than the planner somehow expanding to base tables.

---

## Monitoring and Maintenance

### Track View Size and Bloat

```sql
SELECT
    schemaname || '.' || matviewname                    AS view,
    pg_size_pretty(pg_total_relation_size(
        (schemaname || '.' || matviewname)::regclass))  AS total_size,
    pg_size_pretty(pg_relation_size(
        (schemaname || '.' || matviewname)::regclass))  AS data_size
FROM pg_matviews
ORDER BY pg_total_relation_size(
    (schemaname || '.' || matviewname)::regclass) DESC;
```

### Monitor Long-Running Refreshes

```sql
-- See active refresh operations
SELECT
    pid,
    now() - pg_stat_activity.query_start AS duration,
    query
FROM pg_stat_activity
WHERE query ILIKE '%REFRESH MATERIALIZED VIEW%'
  AND state = 'active';
```

### Detect Lock Contention During Refresh

```sql
SELECT
    blocked.pid          AS blocked_pid,
    blocked.query        AS blocked_query,
    blocker.pid          AS blocker_pid,
    blocker.query        AS blocking_query
FROM pg_locks          bl
JOIN pg_stat_activity  blocked ON blocked.pid = bl.pid
JOIN pg_locks          bl2     ON bl2.transactionid = bl.transactionid
                               AND bl2.pid != bl.pid
JOIN pg_stat_activity  blocker ON blocker.pid = bl2.pid
WHERE NOT bl.granted;
```

---

## Common Pitfalls

**Refreshing inside a transaction block.** `REFRESH MATERIALIZED VIEW CONCURRENTLY` cannot run inside an explicit transaction (`BEGIN ... COMMIT`). It will error immediately. Non-concurrent refresh can run inside a transaction but holds the exclusive lock for the full transaction duration.

```sql
-- This will fail:
BEGIN;
  REFRESH MATERIALIZED VIEW CONCURRENTLY monthly_revenue;  -- ERROR
COMMIT;

-- Do this instead:
REFRESH MATERIALIZED VIEW CONCURRENTLY monthly_revenue;  -- outside transaction
```

**Forgetting the unique index before switching to CONCURRENTLY.** If you add a `UNIQUE` index after creation but forget to run `ANALYZE`, the planner may make poor decisions during the diff phase of concurrent refresh.

**Chained views refreshed in the wrong order.** If `view_b` depends on `view_a`, refreshing `view_b` first gives you stale results derived from stale data — both layers are stale.

**High-frequency trigger-based refreshes tanking write throughput.** A trigger that refreshes a 10-second view on every single row insert serializes all inserts behind sequential refreshes. Batch the refresh using `pg_cron` instead.

**Not accounting for `WITH NO DATA` views in application startup.** A view created `WITH NO DATA` and `ispopulated = false` will return zero rows and no errors — this can silently break application features that depend on it at startup.

```sql
-- Defensive check at application startup
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_matviews
        WHERE matviewname = 'monthly_revenue'
          AND NOT ispopulated
    ) THEN
        RAISE EXCEPTION 'Materialized view monthly_revenue is not populated!';
    END IF;
END $$;
```

---

## Summary

Materialized views sit at the intersection of query performance and operational complexity. Their power is proportional to the expensiveness of the underlying query and inversely proportional to how fresh the data needs to be.

| Scenario | Recommendation |
|---|---|
| Dashboard over large aggregations | Excellent fit — schedule hourly/daily refresh |
| Real-time analytics | Poor fit — consider regular views or live aggregation |
| Full-text search pre-indexing | Excellent fit |
| Caching remote FDW data | Excellent fit |
| Simple computed columns | Use a regular view — materialization overhead not worth it |
| Highly write-heavy base tables | Use CONCURRENTLY + pg_cron, not triggers |
| Multi-level rollups | Use chained views with explicit refresh ordering |

The golden rule: **measure before materializing**. Profile the query you intend to materialize, understand the acceptable staleness window, and plan the refresh strategy before creating the view. Retrofitting a good refresh strategy onto a poorly-planned materialized view is significantly harder than designing it correctly from the start.
