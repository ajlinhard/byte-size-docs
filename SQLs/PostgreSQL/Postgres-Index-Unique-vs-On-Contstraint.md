# Postgres Unique Indexs and Unique Constraints (ON CONFLICT)
In PostgreSQL's `ON CONFLICT` clause, you can reference an **index** as the conflict target — not just a named constraint. Here's how both approaches work:

---

## Two Ways to Specify the Conflict Target

### 1. Using a Named Constraint (`ON CONSTRAINT`)
```sql
INSERT INTO users (email, name)
VALUES ('alice@example.com', 'Alice')
ON CONFLICT ON CONSTRAINT users_email_key
DO UPDATE SET name = EXCLUDED.name;
```
This requires a **named unique constraint** (created via `UNIQUE` or `PRIMARY KEY`).

---

### 2. Using an Index (Column/Expression-Based)
```sql
INSERT INTO users (email, name)
VALUES ('alice@example.com', 'Alice')
ON CONFLICT (email)
DO UPDATE SET name = EXCLUDED.name;
```
Here, `(email)` refers to the **unique index on that column**, not the constraint name directly. PostgreSQL infers the conflict target by finding a matching unique index.

---

## Partial Indexes — The Key Advantage of Index-Based Targeting

This is where index-based targeting really shines. You can target a **partial unique index** (one with a `WHERE` clause):

```sql
-- The partial unique index
CREATE UNIQUE INDEX active_users_email_idx
  ON users (email)
  WHERE deleted_at IS NULL;

-- Now reference it in ON CONFLICT using the index predicate
INSERT INTO users (email, name, deleted_at)
VALUES ('alice@example.com', 'Alice', NULL)
ON CONFLICT (email) WHERE deleted_at IS NULL
DO UPDATE SET name = EXCLUDED.name;
```

The `WHERE deleted_at IS NULL` in the `ON CONFLICT` clause **matches the partial index**, so PostgreSQL knows exactly which index to use. You **cannot** do this with `ON CONSTRAINT`, since partial indexes don't create a named constraint.

---

## Expression Indexes Too

You can also target **expression-based unique indexes**:

```sql
-- Case-insensitive unique index
CREATE UNIQUE INDEX users_lower_email_idx ON users (lower(email));

-- Target it in ON CONFLICT
INSERT INTO users (email, name)
VALUES ('Alice@Example.com', 'Alice')
ON CONFLICT (lower(email))
DO UPDATE SET name = EXCLUDED.name;
```

---

## Quick Comparison

| Feature | `ON CONSTRAINT` | Index-based `(col)` |
|---|---|---|
| Named constraint required | ✅ Yes | ❌ No |
| Works with partial indexes | ❌ No | ✅ Yes |
| Works with expression indexes | ❌ No | ✅ Yes |
| Explicit & unambiguous | ✅ Yes | Depends on index match |

---

**Key rule:** When using the index-based approach, PostgreSQL must be able to find a **unique or primary key index** that matches the columns/expressions and optional `WHERE` predicate you specify — otherwise it throws an error. So the index must already exist.

---
### Does the indexed version have performance trade-offs verse the constraint?
Great question — and the answer is a bit nuanced. At **runtime query execution**, there's essentially no meaningful difference. The real distinctions are at the **planning and maintenance** level.

## Runtime Performance — Effectively Identical

Under the hood, both approaches resolve to the **same index scan**. PostgreSQL's `ON CONFLICT` handler always works through the underlying index regardless of how you specified the conflict target:

- `ON CONSTRAINT` → looks up the constraint → finds its backing index → uses it
- `(col)` → finds the matching index directly

The actual conflict detection and upsert execution are the same B-tree lookup either way.

---

## Where Real Differences Exist

### 1. Planning Overhead (Negligible but Real)
The index-based form requires PostgreSQL to do **index inference** at plan time — it scans `pg_index` to find a unique index matching your columns/expressions/predicate. With `ON CONSTRAINT`, it jumps straight to the constraint's index.

In practice this is **microseconds** and never a bottleneck, but it's worth knowing it exists.

---

### 2. Ambiguity Can Force a Planning Error
If you have **multiple unique indexes** on the same column(s), the index-based form can fail entirely:

```sql
-- Two unique indexes on the same column (unusual but possible)
CREATE UNIQUE INDEX idx_a ON orders (order_ref);
CREATE UNIQUE INDEX idx_b ON orders (order_ref) WHERE status = 'active';

-- This may be ambiguous depending on what PostgreSQL infers
ON CONFLICT (order_ref) DO UPDATE ...
```

`ON CONSTRAINT` has **zero ambiguity** — it's a direct named lookup. With complex schemas, this can avoid subtle bugs.

---

### 3. Index Maintenance — No Difference
Both a standalone unique index and a constraint's backing index are maintained identically by the write path. There's no extra cost to writes for one vs the other.

---

### 4. Where Partial Indexes Can *Improve* Performance
This is actually a case where the **index-based approach wins** over a full constraint:

```sql
-- Full unique constraint — enforced across ALL rows
ALTER TABLE events ADD CONSTRAINT unique_email UNIQUE (email);

-- Partial unique index — only enforced on active rows
CREATE UNIQUE INDEX idx_active_email ON events (email) WHERE archived = false;
```

The partial index is **smaller**, fits better in cache, and its uniqueness checks only scan the filtered subset. If your uniqueness requirement is conditional, a partial index outperforms a full constraint both in `ON CONFLICT` resolution and in general write overhead.

---

## Summary

| Concern | `ON CONSTRAINT` | Index-based |
|---|---|---|
| Runtime conflict detection | Same | Same |
| Plan-time inference cost | None | Tiny (index scan at plan time) |
| Ambiguity risk | None | Possible with overlapping indexes |
| Partial index support | ❌ | ✅ (and can be faster) |
| Write maintenance cost | Same | Same |

**Bottom line:** Don't choose between them based on performance — they're equivalent in practice. Choose based on **clarity** (`ON CONSTRAINT` is more explicit and refactor-safe) vs **flexibility** (index-based unlocks partial and expression indexes, which can genuinely improve performance when your uniqueness is conditional).
