# Postgres Indexes
Here's a comprehensive breakdown of PostgreSQL's index types, how they work under the hood, and how they map to SQL Server equivalents.

**Links:**
- [CodeCamp - Practical Guide](https://www.freecodecamp.org/news/how-database-indexes-work-a-practical-guide-with-postgresql-examples/)

---

## The index types at a glance---

## B-Tree — the universal default

B-Tree is PostgreSQL's workhorse index. Every `CREATE INDEX` without a type specification produces one. Internally it's a balanced tree where leaf nodes hold the indexed values plus pointers (heap TIDs) to the actual rows. The tree stays balanced through page splits, keeping read depth logarithmic regardless of table size.

B-Tree supports `=`, `<`, `>`, `<=`, `>=`, `BETWEEN`, `IN`, `LIKE 'foo%'` (prefix only), `IS NULL`, and `ORDER BY` without a sort step.

```sql
CREATE INDEX idx_orders_customer ON orders(customer_id);
CREATE INDEX idx_orders_date ON orders(created_at DESC);
```

**SQL Server parallel:** This is the direct equivalent of SQL Server's *nonclustered* index (and structurally identical to the b-tree within a *clustered* index). PostgreSQL doesn't have a "clustered index" concept in the SQL Server sense — all Postgres tables are heap-organized and every index is secondary. The closest analog to a SQL Server clustered index is a `CLUSTER` command (a one-time rewrite) or the `pg_partman` pattern of keeping data physically sorted.

---

## Hash — equality-only speed

Hash indexes store a hash of the indexed value and map it directly to a bucket containing the heap TID. They're slightly faster than B-Tree for pure equality lookups (`=`) because they bypass tree traversal, but they're useless for ranges, sorting, or `LIKE`. Before PostgreSQL 10, hash indexes weren't WAL-logged and couldn't survive crashes — they're now safe to use.

```sql
CREATE INDEX idx_sessions_token ON sessions USING HASH (session_token);
```

**SQL Server parallel:** SQL Server has no on-disk hash index for row-store tables. In-memory OLTP tables (`MEMORY_OPTIMIZED`) do have hash indexes, which are the conceptual equivalent. For regular tables, SQL Server leans on B-Tree for equality, relying on the optimizer to recognize when range information isn't needed.

---

## GIN — inverted indexes for multi-valued data

GIN (Generalized Inverted Index) is PostgreSQL's answer to multi-valued columns. It builds an index where each *element* of a value (each array item, each JSONB key, each lexeme in a text search vector) is a key pointing to all rows that contain it. This is identical in concept to a full-text search inverted index.

GIN is the go-to for:
- `JSONB` columns with `@>`, `?`, `?|`, `?&`
- Arrays with `&&`, `@>`
- Full-text search with `tsvector` / `@@`

```sql
CREATE INDEX idx_products_tags ON products USING GIN (tags);
CREATE INDEX idx_docs_fts ON documents USING GIN (to_tsvector('english', body));
```

**SQL Server parallel:** SQL Server's *Full-Text Index* is architecturally the same inverted index concept. For JSONB, SQL Server has no direct equivalent — JSON is stored as `NVARCHAR` and indexed via computed columns or full-text, which is far less ergonomic.

---

## GiST — a framework for geometric and fuzzy queries

GiST (Generalized Search Tree) is not a single data structure but a framework that lets extension authors plug in custom index strategies. Built-in strategies cover geometric types (`point`, `box`, `polygon`, `circle`), range types (`daterange`, `int4range`), and full-text search (as an alternative to GIN with faster updates but slower searches).

GiST supports operators like `&&` (overlap), `@>` (contains), `<->` (distance), and nearest-neighbor (`ORDER BY ... <-> point`).

```sql
CREATE INDEX idx_locations_geo ON locations USING GIST (position);
-- Nearest neighbor: find 10 closest to a point
SELECT * FROM locations ORDER BY position <-> '(40.7,-74.0)' LIMIT 10;
```

**SQL Server parallel:** SQL Server's *spatial index* covers a similar use case for `geometry` and `geography` types, using a hierarchical grid decomposition (tessellation). The concepts align but the implementation differs — SQL Server's spatial index requires you to specify a bounding box, while GiST adapts dynamically.

---

## SP-GiST — partitioned space trees

SP-GiST (Space-Partitioned GiST) is also a framework, but for non-balanced, space-partitioning structures like quadtrees, k-d trees, and tries. It shines when data has a natural recursive partitioning — like IP address ranges (tries), 2D point clouds (quadtrees), or phone number prefixes.

```sql
CREATE INDEX idx_ips ON network_events USING SPGIST (ip_address inet_ops);
```

**SQL Server parallel:** No direct equivalent. SQL Server's spatial index is the closest for point data, but the trie and k-d tree strategies have no analog in SQL Server's index repertoire.

---

## BRIN — the tiny index for naturally ordered big tables

BRIN (Block Range Index) is radically different from the others. Instead of indexing individual values, it stores just the *min* and *max* value for each range of physical disk blocks (128 blocks by default). When queried, it prunes blocks whose range cannot possibly contain matching rows.

BRIN is tiny (often 100–1000x smaller than a B-Tree) but only works when the table's physical storage order correlates with the indexed column — like an append-only events table where `created_at` increases monotonically.

```sql
-- Perfect use case: IoT sensor data loaded in time order
CREATE INDEX idx_sensor_time ON sensor_readings USING BRIN (recorded_at);
```

**SQL Server parallel:** The philosophical kin is SQL Server's *columnstore index*, which also uses compressed min/max metadata per segment to skip irrelevant data during scans. They're not architecturally identical but serve a similar "reduce I/O on massive ordered data" purpose. SQL Server also has *partition elimination*, which achieves a similar skip-based effect for partitioned tables.

---

## Partial indexes — index a subset of rows

A partial index adds a `WHERE` clause to the index definition. Only rows satisfying the condition are indexed, making the index smaller, faster to maintain, and cheaper to cache.

```sql
-- Only index active users — deleted/inactive users never queried by ID
CREATE INDEX idx_users_active ON users(email) WHERE is_deleted = false;

-- Only index unfulfilled orders
CREATE INDEX idx_orders_open ON orders(created_at) WHERE status = 'pending';
```

**SQL Server parallel:** This is a direct match to SQL Server's *filtered index*, introduced in SQL Server 2008. Syntax is nearly identical: `CREATE INDEX ... ON ... WHERE ...`.

---

## Expression indexes — index a computed value

An expression index stores the result of a function or expression rather than a raw column value. The optimizer will use it when the query's `WHERE` clause contains the same expression.

```sql
-- Case-insensitive email lookups
CREATE INDEX idx_users_email_lower ON users(lower(email));
-- Query must match exactly:
SELECT * FROM users WHERE lower(email) = 'alice@example.com';

-- Index on extracted JSON field
CREATE INDEX idx_orders_status ON orders((payload->>'status'));
```

**SQL Server parallel:** SQL Server achieves this through *computed columns* — you add a persisted computed column to the table, then index it. PostgreSQL bakes it directly into the index without altering the table schema, which is cleaner.

---

## Covering indexes — avoid heap lookups entirely

When all columns a query needs are present in the index, PostgreSQL can answer from the index alone (an *index-only scan*), never touching the heap. You include non-key columns with `INCLUDE`:

```sql
CREATE INDEX idx_orders_covering
  ON orders(customer_id)
  INCLUDE (status, total_amount, created_at);

-- This query now never touches the heap:
SELECT status, total_amount, created_at
FROM orders
WHERE customer_id = 42;
```

**SQL Server parallel:** Identical feature, identical syntax. SQL Server has supported `INCLUDE` on nonclustered indexes since SQL Server 2005. The concept and performance characteristics are the same — included columns live in the leaf level of the index b-tree without being key columns.

---

## Quick comparison table

| PostgreSQL | SQL Server | Key difference |
|---|---|---|
| B-Tree | Clustered / nonclustered b-tree | PG tables are always heap; no true clustered index |
| Hash | In-memory hash (OLTP only) | SQL Server lacks on-disk hash for row-store |
| GIN | Full-text index | GIN is more general; works on arrays & JSONB natively |
| GiST | Spatial index | SQL Server spatial needs explicit bounding box |
| SP-GiST | No equivalent | Trie/k-d tree structures not in SQL Server |
| BRIN | Columnstore (philosophically) | Columnstore is far richer; BRIN is extremely lightweight |
| Partial | Filtered index | Near-identical feature and syntax |
| Expression | Computed column index | PG doesn't require altering the table schema |
| Covering (`INCLUDE`) | Covering index (`INCLUDE`) | Identical concept and syntax |

The biggest takeaway: PostgreSQL's index system is far more *extensible* — GiST and SP-GiST let extensions like PostGIS, pgvector, and pg_trgm plug in entirely custom index strategies. SQL Server's index types are fixed by the engine, making PostgreSQL the stronger fit for non-relational data shapes (geospatial, full-text, vectors, JSON).
