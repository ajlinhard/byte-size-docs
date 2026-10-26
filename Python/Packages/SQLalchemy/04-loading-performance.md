# Chapter 4 — Loading Strategies & Query Efficiency

**Level:** Intermediate → Advanced · **Prev:** [Querying in Depth](03-querying.md) · **Next:** [Engines, Pooling & Transactions](05-engine-pooling-transactions.md)

Most ORM performance problems come from **how many queries** run and **how much data**
each one pulls — not from SQLAlchemy's own overhead. This chapter covers the tools for
controlling both.

---

## 4.1 Lazy loading and the N+1 problem

By default, relationships are **lazy**: `user.addresses` isn't loaded until you touch
it, and then it costs one SELECT.

```python
users = session.scalars(select(User)).all()     # 1 query
for u in users:
    print(u.name, len(u.addresses))             # +1 query PER USER
```

100 users → 101 queries. This is the **N+1 problem** and it's the #1 ORM performance
bug. It's invisible in development with 5 rows and devastating in production with
5,000.

Turn on `echo=True` (or the logging setup in §4.15) and watch for repeated near-identical
SELECTs — that's the signature.

---

## 4.2 Loader strategies overview

| Strategy | When SQL runs | SQL shape | Best for |
|----------|--------------|-----------|----------|
| `lazyload` (`lazy="select"`) | On first attribute access | 1 SELECT per parent | Rarely-accessed relationships |
| **`selectinload`** | Right after the main query | `SELECT ... WHERE fk IN (...)` (batched, 500 IDs per batch) | **Collections — the default choice** |
| **`joinedload`** | In the main query | `LEFT OUTER JOIN` | **Many-to-one / one-to-one** |
| `subqueryload` | Right after main query | Re-runs main query as subquery | Legacy; prefer selectinload |
| `immediateload` | Right after each object loads | 1 SELECT per parent | Rare |
| `noload` | Never | — | Rare; collection stays empty |
| **`raiseload`** | Never — raises on access | — | **Catching accidental lazy loads** |
| `write_only` / `dynamic` | You query it explicitly | — | Huge collections |

Apply them **per query** with options (preferred), or set a **default** on the
relationship with `lazy=...`.

---

## 4.3 `selectinload` — the workhorse for collections

```python
from sqlalchemy.orm import selectinload

users = session.scalars(
    select(User).options(selectinload(User.addresses))
).all()
# Query 1: SELECT ... FROM user_account
# Query 2: SELECT ... FROM address WHERE address.user_id IN (1, 2, 3, ...)
```

Two queries regardless of how many users. Why it's usually best for collections:

- No row multiplication (a JOIN to a collection repeats parent columns per child).
- Works cleanly with `LIMIT`/`OFFSET` on the parent query.
- Batches large IN lists automatically.

## 4.4 `joinedload` — the workhorse for many-to-one

```python
from sqlalchemy.orm import joinedload

addresses = session.scalars(
    select(Address).options(joinedload(Address.user))
).all()
# One query: SELECT address.*, user_account_1.* FROM address
#            LEFT OUTER JOIN user_account AS user_account_1 ON ...
```

For a scalar reference, a JOIN adds columns but not rows — one round trip, cheap.

**Gotchas with `joinedload` on collections:**

```python
# Must call .unique() — the JOIN produces one row per child
users = session.scalars(select(User).options(joinedload(User.addresses))).unique().all()
```

- Row multiplication: 1,000 users × 50 addresses = 50,000 rows over the wire.
- `LIMIT` is applied by wrapping the parent query in a subquery — it works, but SQL gets
  heavier.
- Use `joinedload(..., innerjoin=True)` when the FK is NOT NULL to get an INNER JOIN.

## 4.5 Chaining and combining options

```python
from sqlalchemy.orm import selectinload, joinedload

stmt = select(User).options(
    selectinload(User.orders).joinedload(Order.user),     # nested path
    selectinload(User.addresses),
)

# Shared prefix with Load.options()
stmt = select(User).options(
    selectinload(User.orders).options(
        joinedload(Order.user),
        selectinload(Order.items),
    )
)

# Wildcards
stmt = select(User).options(selectinload("*"))           # all relationships on User
```

> **🆕 2.1:** When the same object is reached via multiple paths in one query, the
> **shallowest path's** loader options now apply to later lazy loads on that object.
> In 2.0 it depended on which loader saw the object first. If you relied on deep-path
> options leaking upward, re-check those queries.

## 4.6 `raiseload` — make N+1 impossible

The best defensive habit: make lazy loading an *error* so you're forced to load what
you need explicitly.

```python
from sqlalchemy.orm import raiseload

stmt = select(User).options(selectinload(User.addresses), raiseload("*"))
user = session.scalars(stmt).first()
user.addresses     # fine, eagerly loaded
user.orders        # raises InvalidRequestError instead of silently querying
```

Or set it as the model default and opt *in* to loading per query:

```python
class User(Base):
    ...
    orders: Mapped[list["Order"]] = relationship(lazy="raise")
```

Use `raiseload("*", sql_only=True)` to still allow loads that can be satisfied from the
identity map without SQL (e.g. a many-to-one whose target is already loaded).

**Asyncio users:** lazy loading cannot work implicitly under asyncio
([Chapter 6](06-asyncio.md)), so `lazy="raise"` is an excellent default there.

## 4.7 `contains_eager` — filter on a join *and* populate from it

If you're already joining for filtering, reuse that JOIN to populate the relationship:

```python
from sqlalchemy.orm import contains_eager

stmt = (
    select(User)
    .join(User.addresses)
    .where(Address.email_address.like("%@krusty.com"))
    .options(contains_eager(User.addresses))
)
users = session.scalars(stmt).unique().all()
```

⚠️ `user.addresses` will contain **only the filtered addresses**. That's often what you
want, but it means the collection doesn't reflect the full DB state. Add
`.execution_options(populate_existing=True)` if those users may already be in the
Session with full collections.

## 4.8 Relationship-level defaults

```python
class User(Base):
    __tablename__ = "user_account"
    id: Mapped[int] = mapped_column(primary_key=True)

    # Always eager-load a small collection that you always need
    roles: Mapped[list["Role"]] = relationship(lazy="selectin")

    # Always JOIN in a many-to-one
    org: Mapped["Org"] = relationship(lazy="joined", innerjoin=True)

    # Never load implicitly
    audit_log: Mapped[list["AuditEntry"]] = relationship(lazy="raise")
```

Rule of thumb: keep model defaults conservative (`select` or `raise`) and specify eager
loading per query. Eager defaults on models tend to cascade into loading half the
database for queries that don't need it.

---

## 4.9 Huge collections: `WriteOnlyMapped`

For a collection that can hold thousands of rows (a user's events, a channel's
messages), never load it all. Use a **write-only** relationship:

```python
from sqlalchemy.orm import WriteOnlyMapped

class Channel(Base):
    __tablename__ = "channel"
    id: Mapped[int] = mapped_column(primary_key=True)
    messages: WriteOnlyMapped["Message"] = relationship(
        cascade="all, delete-orphan", passive_deletes=True
    )

ch = session.get(Channel, 1)
ch.messages.add(Message(body="hi"))                               # append, no load
recent = session.scalars(
    ch.messages.select().order_by(Message.id.desc()).limit(20)    # query on demand
).all()
count = session.scalar(select(func.count()).select_from(ch.messages.select().subquery()))
```

`write_only` replaces the legacy `lazy="dynamic"` (`DynamicMapped`), which isn't
compatible with asyncio.

---

## 4.10 Loading fewer columns

### Select only what you need

The cheapest optimization: if you're building a list view, don't load full entities.

```python
rows = session.execute(select(User.id, User.name)).all()     # Row tuples, no identity map, no tracking
```

Plain column rows skip identity-map work and change tracking entirely, so they're
substantially faster to process than full ORM objects.

### `load_only` and `defer`

When you do want entities but some columns are large (text blobs, JSON documents,
embeddings):

```python
from sqlalchemy.orm import load_only, defer, undefer

session.scalars(select(Article).options(load_only(Article.id, Article.title)))
session.scalars(select(Article).options(defer(Article.body)))
session.scalars(select(Article).options(defer(Article.body, raiseload=True)))  # error if accessed
```

Make a column deferred by default on the model:

```python
class Article(Base):
    __tablename__ = "article"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    body: Mapped[str] = mapped_column(deferred=True)
    # or group several: mapped_column(deferred=True, deferred_group="content")

# opt back in
session.scalars(select(Article).options(undefer(Article.body)))
```

### Bundles and DTO-shaped results

```python
from sqlalchemy.orm import Bundle

user_b = Bundle("user", User.id, User.name)
for row in session.execute(select(user_b, Address.email_address).join(User.addresses)):
    print(row.user.id, row.user.name, row.email_address)
```

---

## 4.11 Streaming large result sets

Iterating `.all()` on a million rows loads them all into memory first. Stream instead:

```python
# ORM: yield_per fetches & builds objects in batches, using a server-side cursor when supported
for user in session.scalars(select(User).execution_options(yield_per=1000)):
    process(user)

# Process in chunks
for batch in session.scalars(select(User).execution_options(yield_per=1000)).partitions():
    handle(batch)            # list of up to 1000 Users

# Core: stream_results uses a server-side cursor
with engine.connect() as conn:
    result = conn.execution_options(stream_results=True, max_row_buffer=1000).execute(select(user_table))
    for row in result:
        ...
```

Notes: `yield_per` is incompatible with collection eager loading via `joinedload`
(use `selectinload`); objects still pile up in the identity map, so for very long runs
call `session.expunge_all()` between batches or use Core.

---

## 4.12 Writing efficiently

| Approach | Rows/sec (relative) | Use when |
|----------|---------------------|----------|
| `session.add(obj)` per object + flush | Slowest | Business logic on each object, cascades, events |
| `session.add_all(objs)` + one flush | Better — the UoW batches INSERTs with insertmanyvalues | Moderate volumes of new objects |
| `session.execute(insert(Model), [dicts])` | Fast | Bulk loading; you don't need objects back |
| `conn.execute(insert(table), [dicts])` (Core) | Fastest in SQLAlchemy | ETL, imports |
| Native `COPY` (psycopg `cursor.copy`) | Fastest overall | Millions of rows into PostgreSQL |

Other write tips:

- Flush in batches for big imports (`if i % 1000 == 0: session.flush(); session.expunge_all()`).
- Use `update(...).where(...)` instead of loading objects just to change a field.
- Disable `expire_on_commit` if you'll reuse objects after commit — saves a refresh
  SELECT per object.
- Let the DB cascade deletes (`ondelete="CASCADE"` + `passive_deletes=True`).

---

## 4.13 Statement caching (and why `lambda_stmt` exists)

SQLAlchemy caches the **compiled form** of every statement, keyed by its structure
(not its parameter values). Building the Python `select()` object still costs time on
every call, but SQL compilation is skipped after the first time.

- Cache size: `create_engine(..., query_cache_size=500)` (default 500). With `echo=True`
  you'll see `[cached since 3.2s ago]` vs `[generated in 0.0001s]` in the logs.
- **Custom types and constructs must declare `cache_ok = True`** (TypeDecorator) or
  `inherit_cache = True` (custom ClauseElements), otherwise they disable caching for
  every statement that uses them and emit a warning.
- Dynamically generated statements whose *structure* varies wildly (e.g. `IN` with
  literal_binds, ad-hoc column lists) churn the cache. Bound parameters are cached
  fine; `in_()` uses "expanding" parameters so different list lengths share one entry.

For extremely hot code paths, `lambda_stmt` caches the *construction* of the
statement too:

```python
from sqlalchemy import lambda_stmt

def get_user(session, uid: int):
    stmt = lambda_stmt(lambda: select(User).where(User.id == uid))
    return session.scalars(stmt).one()
```

It's an advanced optimization with rules (closure variables become bound params; no
non-trivial Python logic inside). Profile before reaching for it.

---

## 4.14 Indexes, EXPLAIN, and the database side

The ORM can't fix a missing index. Check the plan:

```python
from sqlalchemy import text
stmt = select(Order).where(Order.user_id == 5, Order.status == "open")
compiled = stmt.compile(engine, compile_kwargs={"literal_binds": True})
print(session.execute(text(f"EXPLAIN ANALYZE {compiled}")).all())      # PostgreSQL
```

- Index every foreign key column you join or filter on (PostgreSQL doesn't do it
  automatically): `mapped_column(ForeignKey(...), index=True)`.
- Composite indexes should match your most common `WHERE` + `ORDER BY` combinations.
- PostgreSQL partial/expression indexes:
  `Index("ix_open_orders", Order.user_id, postgresql_where=Order.status == "open")`.

---

## 4.15 Measuring

### SQL logging with timing

```python
import logging, time
from sqlalchemy import event

logging.basicConfig()
log = logging.getLogger("sql.timing")
log.setLevel(logging.INFO)

@event.listens_for(engine, "before_cursor_execute")
def _start(conn, cursor, statement, params, context, executemany):
    conn.info.setdefault("t0", []).append(time.perf_counter())

@event.listens_for(engine, "after_cursor_execute")
def _end(conn, cursor, statement, params, context, executemany):
    elapsed = time.perf_counter() - conn.info["t0"].pop()
    if elapsed > 0.1:
        log.warning("slow query %.3fs: %s", elapsed, statement)
```

### Counting queries in tests (catch N+1 regressions)

```python
from contextlib import contextmanager

@contextmanager
def assert_max_queries(engine, n):
    count = 0
    def _count(*a, **k):
        nonlocal count
        count += 1
    event.listen(engine, "before_cursor_execute", _count)
    try:
        yield
    finally:
        event.remove(engine, "before_cursor_execute", _count)
    assert count <= n, f"expected <= {n} queries, got {count}"

with assert_max_queries(engine, 2):
    users = session.scalars(select(User).options(selectinload(User.addresses))).all()
    _ = [len(u.addresses) for u in users]
```

### Python profiling

`cProfile` + `snakeviz`, or `py-spy` in production. If time is in
`sqlalchemy/orm/loading.py`, you're building too many objects — select columns or
paginate. If it's in the DBAPI's `execute`, the database is the bottleneck.

---

## 4.16 Decision checklist

1. Am I loading a collection for many parents? → `selectinload`.
2. Am I loading a single related object? → `joinedload`.
3. Am I already joining to filter? → `contains_eager`.
4. Could this ever lazy-load by accident? → `raiseload("*")` / `lazy="raise"`.
5. Do I need whole objects? If not → select columns.
6. Is the collection unbounded? → `WriteOnlyMapped`.
7. Is the result huge? → `yield_per` / `stream_results`.
8. Am I writing many rows? → bulk `insert()` / `update()`, not per-object adds.
9. Is the DB using an index? → `EXPLAIN`.

Next: [Chapter 5](05-engine-pooling-transactions.md) — connections, pooling and
transactions.
