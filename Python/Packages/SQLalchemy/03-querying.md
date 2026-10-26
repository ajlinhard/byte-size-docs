# Chapter 3 — Querying in Depth

**Level:** Intermediate · **Prev:** [ORM Basics](02-orm-basics.md) · **Next:** [Loading Strategies & Query Efficiency](04-loading-performance.md)

All examples use the `User` / `Address` models from Chapter 2 plus these:

```python
from decimal import Decimal
from datetime import datetime
from sqlalchemy import ForeignKey, Numeric, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

class Order(Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user_account.id"))
    status: Mapped[str] = mapped_column(default="open")
    total: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    user: Mapped["User"] = relationship()
```

---

## 3.1 The one query API: `select()`

In 2.x, the same `select()` construct works for Core tables and ORM entities. You run
it through `session.execute()` or one of its shortcuts.

```python
from sqlalchemy import select

stmt = select(User).where(User.name == "spongebob")

session.execute(stmt)          # Result of Row objects: Row(User,)
session.scalars(stmt)          # ScalarResult of User objects  ← usually what you want
session.scalar(stmt)           # first User or None
```

What you put in `select()` determines the row shape:

```python
select(User)                          # rows of (User,)      → use .scalars()
select(User.name, User.fullname)      # rows of (str, str)
select(User, Address)                 # rows of (User, Address)
select(User.id, func.count(Order.id)) # rows of (int, int)
```

> **🆕 2.1 typing:** `select(User.id, User.name)` is now typed `Select[int, str]`
> (was `Select[Tuple[int, str]]`), and rows are `Row[int, str]`. Requires mypy ≥ 1.7.

### Result method cheat sheet (ORM)

```python
session.scalars(stmt).all()            # list[User]
session.scalars(stmt).first()          # User | None
session.scalars(stmt).one()            # exactly one, else raises
session.scalars(stmt).one_or_none()    # User | None, raises if >1
session.execute(stmt).mappings().all() # list of dict-like rows
session.get(User, 5)                   # PK lookup, checks identity map first, no SQL if cached
session.get_one(User, 5)               # like get() but raises if missing
```

### `where()` vs `filter_by()`

```python
select(User).where(User.name == "sandy", User.fullname.is_not(None))
select(User).filter_by(name="sandy")       # keyword shortcut, equality only
```

> **🆕 2.1:** `Select.filter_by()` searches *every* entity in the FROM clause. If a name
> exists in more than one (e.g. `id` after a join), it raises `AmbiguousColumnError` —
> use `where()` with explicit columns. (Legacy `Query.filter_by()` is unchanged.)

---

## 3.2 Joins

### Joining along a relationship (preferred)

```python
stmt = (
    select(User.name, Address.email_address)
    .join(User.addresses)                       # ON derived from the relationship
    .where(Address.email_address.like("%@krusty.com"))
)
```

### Other join forms

```python
select(User).join(Address)                                  # infer ON from the FK
select(User).join(Address, User.id == Address.user_id)      # explicit ON
select(User).outerjoin(User.addresses)                      # LEFT OUTER JOIN
select(User).join(Address, isouter=True, full=True)         # FULL OUTER JOIN
select(Address).join_from(User, Address)                    # explicit left side
select(User).join(User.addresses.and_(Address.email_address.like("%.org")))  # extra ON criteria
```

### Aliases (self-joins, joining the same table twice)

```python
from sqlalchemy.orm import aliased

a1 = aliased(Address)
a2 = aliased(Address)
stmt = (
    select(User)
    .join(a1, User.addresses)
    .join(a2, User.addresses)
    .where(a1.email_address == "a@x.com", a2.email_address == "b@x.com")
)
```

> **Joins ≠ eager loading.** `join()` lets you *filter or sort* by related tables; it
> does **not** populate `user.addresses`. To load related objects, use loader options
> ([Chapter 4](04-loading-performance.md)). To do both with one JOIN, use
> `contains_eager()`.

### EXISTS via relationships

```python
select(User).where(User.addresses.any(Address.email_address.like("%.org")))  # one-to-many
select(Address).where(Address.user.has(User.name == "sandy"))                # many-to-one
```

---

## 3.3 Ordering, limiting, pagination, distinct

```python
select(User).order_by(User.name.asc(), User.id.desc())
select(User).order_by(User.created_at.desc().nulls_last())
select(User).limit(20).offset(40)
select(User.name).distinct()
```

**Offset pagination** gets slow on large tables (the DB still scans skipped rows).
Prefer **keyset (cursor) pagination**:

```python
def page_after(session, last_seen_id: int | None, size: int = 50):
    stmt = select(User).order_by(User.id).limit(size)
    if last_seen_id is not None:
        stmt = stmt.where(User.id > last_seen_id)
    return session.scalars(stmt).all()

# Composite key (created_at, id) for non-unique sort columns:
from sqlalchemy import tuple_
stmt = stmt.where(tuple_(Order.created_at, Order.id) > (last_ts, last_id))
```

---

## 3.4 Aggregation and grouping

```python
from sqlalchemy import func

# count
session.scalar(select(func.count()).select_from(User))
session.scalar(select(func.count(User.id)).where(User.name.like("s%")))

# group by / having
stmt = (
    select(User.name, func.count(Order.id).label("n"), func.sum(Order.total).label("revenue"))
    .join(Order, Order.user_id == User.id)
    .group_by(User.name)
    .having(func.count(Order.id) > 2)
    .order_by(func.sum(Order.total).desc())
)
for name, n, revenue in session.execute(stmt):
    ...
```

Conditional aggregation with `case()` / `filter()`:

```python
from sqlalchemy import case

stmt = select(
    func.count().filter(Order.status == "paid").label("paid"),       # FILTER (WHERE ...) on PG/SQLite
    func.sum(case((Order.status == "open", 1), else_=0)).label("open"),  # portable
)
```

---

## 3.5 Subqueries and CTEs

### Scalar subquery (in a column or WHERE)

```python
order_count = (
    select(func.count(Order.id))
    .where(Order.user_id == User.id)       # correlates to the outer User automatically
    .scalar_subquery()
)
stmt = select(User.name, order_count.label("orders"))
```

### Subquery in FROM, joined back to an entity

```python
totals = (
    select(Order.user_id, func.sum(Order.total).label("spent"))
    .group_by(Order.user_id)
    .subquery()
)
stmt = (
    select(User, totals.c.spent)
    .join(totals, totals.c.user_id == User.id)
    .where(totals.c.spent > 1000)
)
```

### Mapping a subquery back to an entity

```python
recent = select(Order).where(Order.created_at > cutoff).subquery()
RecentOrder = aliased(Order, recent)
stmt = select(RecentOrder).order_by(RecentOrder.total.desc())
```

### Common Table Expressions

```python
big_spenders = (
    select(Order.user_id, func.sum(Order.total).label("spent"))
    .group_by(Order.user_id)
    .having(func.sum(Order.total) > 500)
    .cte("big_spenders")
)
stmt = select(User.name, big_spenders.c.spent).join(big_spenders, big_spenders.c.user_id == User.id)
```

### Recursive CTE (trees / hierarchies)

```python
class Category(Base):
    __tablename__ = "category"
    id: Mapped[int] = mapped_column(primary_key=True)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("category.id"))
    name: Mapped[str]

root = select(Category.id, Category.name, Category.parent_id).where(Category.id == 1)
tree = root.cte("tree", recursive=True)
tree = tree.union_all(
    select(Category.id, Category.name, Category.parent_id)
    .join(tree, Category.parent_id == tree.c.id)
)
descendants = session.execute(select(tree)).all()
```

### UNION / INTERSECT / EXCEPT

```python
from sqlalchemy import union_all
u = union_all(
    select(User.id).where(User.name == "sandy"),
    select(User.id).where(User.name == "patrick"),
)
# To get ORM entities from a UNION:
u_sub = u.subquery()
stmt = select(User).join(u_sub, User.id == u_sub.c.id)
```

---

## 3.6 Window functions

```python
stmt = select(
    Order.id,
    Order.user_id,
    Order.total,
    func.row_number().over(partition_by=Order.user_id, order_by=Order.total.desc()).label("rank"),
    func.sum(Order.total).over(partition_by=Order.user_id).label("user_total"),
)

# "Top 3 orders per user" — filter on the window result via a subquery
ranked = stmt.subquery()
top3 = select(ranked).where(ranked.c.rank <= 3)
```

> **🆕 2.1:** Non-integer `RANGE` frames (dates, intervals) are supported via
> `FrameClause`:
>
> ```python
> from datetime import timedelta
> from sqlalchemy import FrameClause, FrameClauseType
> func.sum(Order.total).over(
>     order_by=Order.created_at,
>     range_=FrameClause(
>         start=timedelta(days=7), end=None,
>         start_frame_type=FrameClauseType.PRECEDING,
>         end_frame_type=FrameClauseType.CURRENT,
>     ),
> )
> ```
>
> The database must support value-based RANGE frames: PostgreSQL does; SQLite only
> accepts numeric offsets and will reject the 7-day interval above.

---

## 3.7 ORM-enabled INSERT / UPDATE / DELETE

Changing objects one by one through the Unit of Work is convenient, but for many rows
it's slow (one object per row, change tracking, often one statement per row). SQLAlchemy
2.x lets you pass DML statements straight through the Session.

### Bulk INSERT

```python
from sqlalchemy import insert

session.execute(
    insert(User),
    [{"name": "a", "fullname": "A"}, {"name": "b", "fullname": "B"}],
)
```

This uses the "insertmanyvalues" batching — a few multi-row `INSERT ... VALUES (...),
(...)` statements rather than one per row. Add `.returning(User)` to get ORM objects
back:

```python
users = session.scalars(
    insert(User).returning(User),
    [{"name": "c"}, {"name": "d"}],
).all()
```

> **🆕 2.1 (PostgreSQL):** server-side monotonic defaults like `uuidv7()` can now take
> part in batched INSERT…RETURNING, so UUIDv7 primary keys work with bulk inserts and
> still return rows in the right order.

### Bulk UPDATE by primary key

Pass a list of dicts that *include the primary key*:

```python
from sqlalchemy import update
session.execute(update(User), [{"id": 1, "fullname": "X"}, {"id": 2, "fullname": "Y"}])
```

### UPDATE / DELETE with WHERE

```python
session.execute(
    update(Order)
    .where(Order.status == "open", Order.created_at < cutoff)
    .values(status="expired")
    .execution_options(synchronize_session="fetch")
)
session.execute(delete(Order).where(Order.status == "expired"))
```

`synchronize_session` controls whether objects already loaded in the Session are
updated to match:

| Value | Behaviour |
|-------|-----------|
| `"auto"` (default) | `"fetch"` if RETURNING is available, else `"evaluate"` |
| `"evaluate"` | Evaluate the WHERE in Python against loaded objects |
| `"fetch"` | Use RETURNING / a SELECT to find affected PKs |
| `False` | Don't sync; expire or discard the Session afterwards yourself |

### Upserts (INSERT … ON CONFLICT)

Dialect-specific constructs:

```python
from sqlalchemy.dialects.postgresql import insert as pg_insert   # also: sqlite, mysql

stmt = pg_insert(User).values([{"id": 1, "name": "a"}, {"id": 2, "name": "b"}])
stmt = stmt.on_conflict_do_update(
    index_elements=[User.id],
    set_={"name": stmt.excluded.name},
)
session.execute(stmt)

# MySQL/MariaDB:
from sqlalchemy.dialects.mysql import insert as my_insert
stmt = my_insert(User).values(id=1, name="a")
stmt = stmt.on_duplicate_key_update(name=stmt.inserted.name)
```

Combine with `.returning(User)` and `execution_options(populate_existing=True)` to
refresh already-loaded objects with the upserted values.

---

## 3.8 Raw SQL with the ORM

```python
from sqlalchemy import text

# Rows
rows = session.execute(text("SELECT id, name FROM user_account WHERE id > :x"), {"x": 1}).all()

# ORM entities from textual SQL
stmt = text("SELECT * FROM user_account ORDER BY id").columns(User.id, User.name, User.fullname, User.created_at)
users = session.scalars(select(User).from_statement(stmt)).all()
```

---

## 3.9 Reusable criteria and global filters

`with_loader_criteria` applies a WHERE condition to every occurrence of an entity in a
query, including relationship loads — the basis of soft-delete and multi-tenant
filters (see [Chapter 7](07-architecture.md)):

```python
from sqlalchemy.orm import with_loader_criteria

stmt = select(User).options(
    with_loader_criteria(Address, Address.email_address.not_like("%@spam.com"))
)
```

---

## 3.10 Legacy `Query` (recognize it, don't write it)

```python
# Legacy 1.x style                         # 2.x style
session.query(User).filter_by(id=5).first() # session.scalars(select(User).filter_by(id=5)).first()
session.query(User).get(5)                  # session.get(User, 5)
session.query(func.count(User.id)).scalar() # session.scalar(select(func.count(User.id)))
```

`Query` still works in 2.1 but receives no new features.

---

Next: [Chapter 4](04-loading-performance.md) — how related data gets loaded and how to
make queries fast.
