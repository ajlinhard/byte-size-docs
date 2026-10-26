# Chapter 1 — Fundamentals & SQLAlchemy Core

**Level:** Beginner · **Prev:** [Index](00-index.md) · **Next:** [ORM Basics](02-orm-basics.md)

---

## 1.1 What SQLAlchemy actually is

SQLAlchemy is two libraries layered on top of each other:

```
┌──────────────────────────────────────────────────┐
│  ORM  (sqlalchemy.orm)                            │
│  Classes ↔ rows, Session, Unit of Work,           │
│  relationships, identity map, loading strategies  │
├──────────────────────────────────────────────────┤
│  Core (sqlalchemy)                                │
│  Engine, Connection, connection Pool, Dialects,   │
│  MetaData/Table, SQL Expression Language          │
├──────────────────────────────────────────────────┤
│  DBAPI driver  (psycopg, asyncpg, pymysql,        │
│                 sqlite3, oracledb, ...)           │
├──────────────────────────────────────────────────┤
│  Database                                         │
└──────────────────────────────────────────────────┘
```

- **Core** is a Pythonic way to *build and run SQL*. You describe tables and write
  queries with Python objects; Core compiles them to the right SQL dialect, sends them
  through a pooled connection, and returns rows.
- **The ORM** is built *on* Core. It maps Python classes to tables and tracks changes to
  objects so it can write them back for you.

You can use Core alone (popular for analytics, ETL, and code that thinks in SQL), the
ORM (most web apps), or both — they interoperate freely, and ORM queries *are* Core
`select()` statements.

### Key vocabulary

| Term | Meaning |
|------|---------|
| **DBAPI** | The low-level driver that speaks to the database (PEP 249). SQLAlchemy never talks to the DB directly; it drives a DBAPI. |
| **Dialect** | SQLAlchemy's adapter for a database + driver combo. It knows how to render SQL and handle types for that backend. |
| **Engine** | The entry point. Holds a Dialect and a connection Pool. Create **one per database per process**. |
| **Connection** | A checked-out DBAPI connection wrapped with transaction handling. Short-lived. |
| **Pool** | Keeps DBAPI connections open and reuses them, because opening connections is expensive. |
| **MetaData** | A registry of `Table` objects describing your schema. |
| **Session** | (ORM) The workspace that tracks objects and turns changes into SQL. |

---

## 1.2 The Engine and database URLs

```python
from sqlalchemy import create_engine

engine = create_engine("sqlite+pysqlite:///:memory:", echo=True)
```

The URL format is:

```
dialect+driver://username:password@host:port/database?key=value
```

Common URLs:

```python
"sqlite:///app.db"                                   # file relative to cwd
"sqlite:////abs/path/app.db"                         # absolute path (4 slashes)
"sqlite://"                                          # in-memory
"postgresql://user:pw@localhost/mydb"                # 🆕 2.1: means psycopg (v3)
"postgresql+psycopg://user:pw@localhost/mydb"        # explicit psycopg 3
"postgresql+psycopg2://user:pw@localhost/mydb"       # legacy psycopg2
"postgresql+asyncpg://user:pw@localhost/mydb"        # async
"mysql+pymysql://user:pw@localhost/mydb?charset=utf8mb4"
"oracle://user:pw@host:1521/?service_name=XEPDB1"    # 🆕 2.1: means oracledb
"mssql+mssql_python://user:pw@host/db"               # 🆕 2.1: Microsoft's driver
```

> **🆕 2.1 driver change:** If your existing URLs say just `postgresql://` and you only
> have psycopg2 installed, upgrading to 2.1 will fail with an import error. Either
> install `psycopg` or write `postgresql+psycopg2://` explicitly.

**Passwords with special characters** (`@`, `/`, `%`) must be URL-escaped. The safest
approach is to build the URL programmatically:

```python
from sqlalchemy import URL, create_engine

url = URL.create(
    drivername="postgresql+psycopg",
    username="app",
    password="p@ss/w%rd",      # escaped for you
    host="db.internal",
    port=5432,
    database="orders",
)
engine = create_engine(url)
```

### Important `create_engine()` arguments

```python
engine = create_engine(
    url,
    echo=False,            # True logs all SQL; "debug" also logs result rows
    pool_size=5,           # persistent connections kept open (QueuePool)
    max_overflow=10,       # extra connections allowed under burst load
    pool_pre_ping=True,    # test connections on checkout (handles DB restarts)
    pool_recycle=1800,     # replace connections older than N seconds
    isolation_level=None,  # e.g. "READ COMMITTED", "SERIALIZABLE", "AUTOCOMMIT"
    connect_args={},       # passed straight to the DBAPI's connect()
)
```

Pooling is covered properly in [Chapter 5](05-engine-pooling-transactions.md).

> The engine is **lazy**: `create_engine()` does not connect. The first connection
> happens when you first use it.

---

## 1.3 Connections and the "commit as you go" model

```python
from sqlalchemy import text

with engine.connect() as conn:
    result = conn.execute(text("SELECT 'hello world'"))
    print(result.scalar())        # hello world
```

`engine.connect()` checks a connection out of the pool; leaving the `with` block
returns it. **Every connection starts a transaction implicitly** the first time you run
something. If you don't commit, it rolls back on exit. There are two styles:

**Commit as you go** — you decide when to commit:

```python
with engine.connect() as conn:
    conn.execute(text("CREATE TABLE some_table (x int, y int)"))
    conn.execute(
        text("INSERT INTO some_table (x, y) VALUES (:x, :y)"),
        [{"x": 1, "y": 1}, {"x": 2, "y": 4}],   # list of dicts = executemany
    )
    conn.commit()
```

**Begin once** — commit on success, rollback on exception, automatically:

```python
with engine.begin() as conn:
    conn.execute(
        text("INSERT INTO some_table (x, y) VALUES (:x, :y)"),
        [{"x": 6, "y": 8}, {"x": 9, "y": 10}],
    )
# committed here (or rolled back if an exception escaped)
```

Prefer `engine.begin()` for scripts and any block that's a single logical unit.

---

## 1.4 Working with results

`conn.execute()` returns a `Result`. It's an iterator of `Row` objects, which behave
like named tuples:

```python
with engine.connect() as conn:
    result = conn.execute(text("SELECT x, y FROM some_table"))
    for row in result:
        print(row.x, row.y)       # attribute access
        print(row[0], row[1])     # index access
        x, y = row                # tuple unpacking
```

The most useful `Result` methods:

| Method | Returns |
|--------|---------|
| `.all()` | list of all rows |
| `.first()` | first row or `None` (discards the rest) |
| `.one()` | exactly one row, else raises `NoResultFound` / `MultipleResultsFound` |
| `.one_or_none()` | one row or `None`; raises if more than one |
| `.scalar()` | first column of first row |
| `.scalar_one()` / `.scalar_one_or_none()` | strict versions of `.scalar()` |
| `.scalars()` | a view yielding just the first column of each row |
| `.mappings()` | rows as dict-like `RowMapping` objects |
| `.partitions(n)` | yields lists of `n` rows at a time |

```python
with engine.connect() as conn:
    xs = conn.execute(text("SELECT x FROM some_table")).scalars().all()   # [1, 2, 6, 9]
    dicts = conn.execute(text("SELECT x, y FROM some_table")).mappings().all()
    # [{'x': 1, 'y': 1}, ...]
```

> A `Result` is a cursor; you can only iterate it **once**, and it should be consumed
> before the connection closes.

### Bound parameters — never format SQL strings

```python
# ✅ Correct: bound parameter, driver escapes the value
conn.execute(text("SELECT * FROM users WHERE name = :name"), {"name": user_input})

# ❌ SQL injection risk
conn.execute(text(f"SELECT * FROM users WHERE name = '{user_input}'"))
```

---

## 1.5 🆕 Template strings: `tstring()` (Python 3.14+)

SQLAlchemy 2.1 adds `tstring()`, built on PEP 750 template strings (`t"..."`). It looks
like an f-string but is safe: interpolated Python values become **bound parameters**,
and interpolated SQLAlchemy objects (columns, tables, subqueries) are embedded as SQL.

```python
# Requires Python 3.14+
from sqlalchemy import tstring, table, column, literal, JSON

user_id = 42
stmt = tstring(t"SELECT * FROM users WHERE id = {user_id}")
# renders: SELECT * FROM users WHERE id = :param_1   (42 is bound, not inlined)

stmt = tstring(t"SELECT {column('q')} FROM {table('t')}")
# renders: SELECT q FROM t

payload = {"foo": "bar"}
stmt = tstring(t"SELECT {literal(payload, JSON)}")    # explicit SQL type
```

Like `text()`, it supports `.columns()` to declare result types. Statements with the
same shape but different values share a compiled-cache entry. (As of 2.1.2 the literal
parts of a t-string are *not* scanned for `:name` parameters — use interpolation.)

Use `text()` on older Pythons; use `tstring()` where you'd be tempted to use an
f-string.

---

## 1.6 Describing schema: MetaData, Table, Column

Raw SQL strings are fine, but SQLAlchemy's power comes from describing tables as
objects so you can build queries programmatically.

```python
from sqlalchemy import (
    MetaData, Table, Column, Integer, String, ForeignKey, DateTime, func,
)

metadata_obj = MetaData()

user_table = Table(
    "user_account",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("name", String(30), nullable=False),
    Column("fullname", String),
    Column("created_at", DateTime(timezone=True), server_default=func.now()),
)

address_table = Table(
    "address",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("user_id", ForeignKey("user_account.id", ondelete="CASCADE"), nullable=False),
    Column("email_address", String, nullable=False),
)

metadata_obj.create_all(engine)   # CREATE TABLE ... for anything missing
```

Things to notice:

- `ForeignKey("user_account.id")` infers the column type from the referenced column.
- `server_default=func.now()` becomes a SQL `DEFAULT now()` in the DDL.
  `default=...` (no "server") is a Python-side default applied by SQLAlchemy on INSERT.
- `create_all()` is great for tests and prototypes. **In production, use Alembic
  migrations** ([Chapter 8](08-integrations.md)).
- `table.c` is the column collection: `user_table.c.name`, `user_table.c["name"]`.

### Constraints, indexes, and naming conventions

```python
from sqlalchemy import UniqueConstraint, CheckConstraint, Index

product = Table(
    "product",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("sku", String(32), nullable=False),
    Column("price_cents", Integer, nullable=False),
    UniqueConstraint("sku"),
    CheckConstraint("price_cents >= 0", name="price_nonneg"),
    Index("ix_product_price", "price_cents"),
)
```

**Always set a naming convention** on your MetaData. Without one, databases generate
random constraint names, which makes migrations painful:

```python
metadata_obj = MetaData(naming_convention={
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
})
```

### Reflection — loading tables from an existing database

```python
some_table = Table("some_table", metadata_obj, autoload_with=engine)

# or everything at once
metadata_obj.reflect(bind=engine)

# or the inspector for introspection
from sqlalchemy import inspect
insp = inspect(engine)
insp.get_table_names()
insp.get_columns("some_table")
```

### 🆕 Typed tables with `TypedColumns` (2.1)

Plain `Table` columns are typed as `Column[Any]` by type checkers. 2.1 lets you declare
columns on a class so `table.c.x` and `select()` results are precisely typed:

```python
from sqlalchemy import Table, TypedColumns, Column, Integer, SmallInteger, MetaData, Named, select

class user_cols(TypedColumns):
    id = Column(Integer, primary_key=True)        # Column[int]
    name: Named[str]                              # NOT NULL String inferred
    age: Named[int | None] = Column(SmallInteger) # nullable SmallInteger
    __row_pos__: tuple[int, str, int | None]      # optional: types select(table)

metadata = MetaData()
user = Table("user", metadata, user_cols)

stmt = select(user.c.id, user.c.name)   # type checker sees Select[int, str]
```

---

## 1.7 The SQL Expression Language

This is the heart of Core. Column objects overload Python operators to produce SQL
expressions:

```python
>>> print(user_table.c.name == "spongebob")
user_account.name = :name_1
>>> print((user_table.c.id > 5) & (user_table.c.name.like("s%")))
user_account.id > :id_1 AND user_account.name LIKE :name_1
```

### SELECT

```python
from sqlalchemy import select

stmt = select(user_table).where(user_table.c.name == "spongebob")
print(stmt)
# SELECT user_account.id, user_account.name, user_account.fullname, user_account.created_at
# FROM user_account WHERE user_account.name = :name_1

with engine.connect() as conn:
    for row in conn.execute(stmt):
        print(row)
```

Statements are **immutable and generative**: each method returns a new statement, so
you can build them up conditionally:

```python
def search_users(name: str | None = None, limit: int = 50):
    stmt = select(user_table.c.id, user_table.c.name)
    if name:
        stmt = stmt.where(user_table.c.name.ilike(f"%{name}%"))
    return stmt.order_by(user_table.c.name).limit(limit)
```

### Operators cheat sheet

| Python | SQL |
|--------|-----|
| `col == 5`, `col != 5`, `<`, `>`, `<=`, `>=` | comparison |
| `col == None` / `col.is_(None)` | `IS NULL` |
| `col.is_not(None)` | `IS NOT NULL` |
| `col.in_([1, 2, 3])` / `col.not_in(...)` | `IN` (expands parameters efficiently) |
| `col.like("a%")`, `col.ilike("a%")` | `LIKE` / case-insensitive |
| `col.startswith("a")`, `col.contains("x")` | `LIKE 'a%'`, `LIKE '%x%'` |
| `col.between(1, 10)` | `BETWEEN` |
| `and_(a, b)`, `or_(a, b)`, `not_(a)` | boolean logic (also `&`, `|`, `~`) |
| `col.desc()`, `col.asc()`, `.nulls_last()` | ordering |
| `func.count(col)`, `func.lower(col)` | any SQL function via `func.<name>` |
| `cast(col, String)` | `CAST` |
| `case((cond, val), else_=other)` | `CASE WHEN` |

> `where()` with multiple arguments ANDs them: `.where(a == 1, b == 2)`.

### INSERT, UPDATE, DELETE

```python
from sqlalchemy import insert, update, delete

with engine.begin() as conn:
    # single row
    conn.execute(insert(user_table).values(name="spongebob", fullname="Spongebob Squarepants"))

    # many rows — pass a list of dicts as the 2nd argument (executemany / batched)
    conn.execute(
        insert(user_table),
        [
            {"name": "sandy", "fullname": "Sandy Cheeks"},
            {"name": "patrick", "fullname": "Patrick Star"},
        ],
    )

    # RETURNING (PostgreSQL, SQLite 3.35+, MariaDB 10.5+, SQL Server, Oracle)
    new_id = conn.execute(
        insert(user_table).values(name="squidward").returning(user_table.c.id)
    ).scalar_one()

    conn.execute(
        update(user_table)
        .where(user_table.c.name == "patrick")
        .values(fullname="Patrick the Star")
    )

    conn.execute(delete(user_table).where(user_table.c.name == "squidward"))
```

> **🆕 2.1:** `delete(t).using(other_join)` renders explicit multi-table
> `DELETE ... USING` on PostgreSQL and MySQL/MariaDB.

### Inspecting the SQL that will run

```python
from sqlalchemy.dialects import postgresql

stmt = select(user_table).where(user_table.c.id == 5)
print(stmt.compile(dialect=postgresql.dialect()))
print(stmt.compile(compile_kwargs={"literal_binds": True}))   # inline values (debug only!)
```

---

## 1.8 Types

SQLAlchemy has generic types that map to the best native type on each backend:

| Generic type | Python type | Notes |
|--------------|-------------|-------|
| `Integer`, `BigInteger`, `SmallInteger` | `int` | |
| `String(n)`, `Text` | `str` | Some DBs (MySQL) require a length for `String` |
| `Boolean` | `bool` | |
| `Numeric(p, s)` | `decimal.Decimal` | Use for money. `Float` returns `float`. |
| `Float`, `Double` | `float` | |
| `Date`, `Time`, `DateTime(timezone=True)` | `date`, `time`, `datetime` | Prefer timezone-aware |
| `Interval` | `timedelta` | |
| `LargeBinary` | `bytes` | |
| `JSON` | `dict` / `list` | Native on PG/MySQL/SQLite |
| `Uuid` | `uuid.UUID` | Native `UUID` on PG; `CHAR(32)` elsewhere |
| `Enum(PyEnum)` | an `enum.Enum` | |

Backend-specific types live in dialect modules, e.g.
`from sqlalchemy.dialects.postgresql import JSONB, ARRAY, INET, TSVECTOR`.

### Custom types with `TypeDecorator`

```python
from sqlalchemy.types import TypeDecorator, String

class LowercaseString(TypeDecorator):
    """Store emails normalized to lowercase."""
    impl = String
    cache_ok = True          # required: says this type is safe for the SQL cache

    def process_bind_param(self, value, dialect):
        return value.lower() if value is not None else None

    def process_result_value(self, value, dialect):
        return value
```

---

## 1.9 Recap & what's next

- One `Engine` per database per process; it owns a connection pool.
- Use `with engine.begin()` for transactional blocks, `engine.connect()` + `commit()`
  when you need finer control.
- Always use bound parameters (`text()` with `:name`, `tstring()`, or expression
  objects).
- `MetaData` + `Table` describe schema; `select/insert/update/delete` build statements.

Next, [Chapter 2](02-orm-basics.md) maps Python classes onto these tables with the ORM.
