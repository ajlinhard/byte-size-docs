# The SQLAlchemy Guide (2.1 edition)

A progressive, beginner-to-advanced walkthrough of SQLAlchemy, the most widely used
database toolkit for Python. Every example targets **SQLAlchemy 2.1.x** (2.1.4 is the
current release as of October 2026) and uses the modern "2.0-style" APIs throughout.

## How to read this series

The chapters build on each other. If you're new, read them in order. If you already
use SQLAlchemy, skim chapter 1 and jump to whatever you need.

| # | Chapter | Level | What you'll learn |
|---|---------|-------|-------------------|
| 1 | [Fundamentals & Core](01-fundamentals-core.md) | Beginner | What SQLAlchemy is, Engine, Connection, MetaData/Table, the SQL Expression Language, `text()` and `tstring()` |
| 2 | [ORM Basics](02-orm-basics.md) | Beginner | Declarative models, `Mapped[]` typing, the Session, CRUD, relationships, dataclass mapping |
| 3 | [Querying in Depth](03-querying.md) | Intermediate | `select()`, joins, filters, aggregation, subqueries, CTEs, window functions, ORM-enabled bulk DML, upserts |
| 4 | [Loading Strategies & Query Efficiency](04-loading-performance.md) | Intermediate → Advanced | Lazy vs eager loading, `selectinload`, `joinedload`, `raiseload`, the N+1 problem, deferred columns, caching, bulk operations, profiling |
| 5 | [Engines, Connections, Pooling & Transactions](05-engine-pooling-transactions.md) | Intermediate → Advanced | Pool types and tuning, pre-ping/recycle, isolation levels, savepoints, session lifecycle, events, multi-database setups |
| 6 | [Asyncio](06-asyncio.md) | Advanced | `AsyncEngine`, `AsyncSession`, async drivers, the greenlet bridge, avoiding implicit IO, `AsyncAttrs` |
| 7 | [Application Architecture](07-architecture.md) | Advanced | Project layout, session-per-request, Unit of Work, Repository & Service layers, mixins, inheritance, multi-tenancy, testing |
| 8 | [Integrations](08-integrations.md) | Advanced | Alembic, FastAPI, Pydantic v2, SQLModel, Flask-SQLAlchemy, pandas, Celery/background jobs, pytest, observability |

## Version notes you should know up front

SQLAlchemy 2.1.0 was released on September 24, 2026; the 2.0 series continues as
the maintenance branch. The most important differences from 2.0 are:

- **Python 3.11+ is required.**
- **`greenlet` is no longer installed by default.** If you use asyncio, install
  `sqlalchemy[asyncio]`.
- **New default drivers.** A bare `postgresql://` URL now means **psycopg 3**
  (`postgresql+psycopg://`), and `oracle://` means **python-oracledb**. In 2.0 these
  were psycopg2 and cx_Oracle.
- **Session autoflush is unconditional** — it now fires before *every* execution,
  including `text()` statements.
- **New Core features:** `tstring()` (Python 3.14 template strings), `CreateView` /
  `CreateTableAs`, `Delete.using()`, typed `Table` columns via `TypedColumns`,
  `Select[int, str]` typing (no more `Tuple[...]`).
- **New ORM features:** session-level `execution_options`, `RegistryEvents`,
  `back_populates=lambda: Other.attr`, revised dataclass default handling.

Each chapter calls out 2.1-specific behaviour where it matters with a **🆕 2.1** marker.

> **Coming from 1.x?** The `session.query(...)` API still works but is "legacy".
> This guide uses `select()` + `session.execute()` / `session.scalars()` everywhere,
> which is the recommended style. Migrate to 2.0 first, then 2.1.

## Installation

```bash
# Core + ORM
pip install sqlalchemy                     # 2.1.x

# With asyncio support (pulls in greenlet)
pip install "sqlalchemy[asyncio]"

# Drivers (pick what you need)
pip install "psycopg[binary]"              # PostgreSQL (sync + async) — default PG driver in 2.1
pip install asyncpg                        # PostgreSQL, async-only, very fast
pip install pymysql  aiomysql              # MySQL / MariaDB
pip install aiosqlite                      # SQLite async
pip install oracledb                       # Oracle (default in 2.1)
pip install mssql-python                   # SQL Server, Microsoft's driver (new in 2.1)
```

Check your version:

```python
import sqlalchemy
print(sqlalchemy.__version__)   # e.g. 2.1.4
```

If you need to stay on 2.0 (for example because a dependency like SQLModel still pins
`<2.1`), pin it explicitly: `sqlalchemy>=2.0,<2.1`.

## Running the examples

Nearly every example uses an in-memory SQLite database (`sqlite://` or
`sqlite+pysqlite:///:memory:`) so you can paste it into a REPL with no setup. Pass
`echo=True` to `create_engine()` to see every SQL statement SQLAlchemy emits — this is
the single best learning tool in the library.

## Official references

- Docs: https://docs.sqlalchemy.org/en/21/
- What's new in 2.1: https://docs.sqlalchemy.org/en/21/changelog/migration_21.html
- Unified tutorial: https://docs.sqlalchemy.org/en/21/tutorial/
