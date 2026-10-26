# Chapter 8 — Integrations with Other Packages

**Level:** Advanced · **Prev:** [Application Architecture](07-architecture.md) · **Back to:** [Index](00-index.md)

---

## 8.1 Alembic — schema migrations

Alembic is SQLAlchemy's official migration tool, written by the same author. It
compares your models' `MetaData` with the live database and generates migration
scripts.

### Setup

```bash
pip install alembic
alembic init migrations              # or: alembic init -t async migrations (async template)
```

Edit `migrations/env.py` so Alembic sees your models and your URL:

```python
# migrations/env.py (relevant parts)
from app.core.config import settings
from app.core.db import Base
import app.models          # noqa: F401  — import every model module so metadata is complete

config.set_main_option("sqlalchemy.url", settings.database_url)
target_metadata = Base.metadata

def run_migrations_online():
    connectable = engine_from_config(config.get_section(config.config_ini_section), prefix="sqlalchemy.")
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,              # detect column type changes
            compare_server_default=True,    # detect server default changes
            render_as_batch=connection.dialect.name == "sqlite",   # SQLite ALTER workaround
        )
        with context.begin_transaction():
            context.run_migrations()
```

### Everyday workflow

```bash
alembic revision --autogenerate -m "add orders.status"   # generate from model diff
# → REVIEW the generated file in migrations/versions/ !
alembic upgrade head                                      # apply
alembic downgrade -1                                      # roll back one
alembic history --verbose
alembic current
alembic check            # exit non-zero if models and DB differ (great in CI)
```

### What autogenerate does and doesn't detect

Detects: tables, columns, nullability, indexes, unique/FK constraints, (with config)
types and server defaults.

Does **not** reliably detect: table or column **renames** (it sees drop + add — you'll
lose data if you don't edit it to `op.alter_column(..., new_column_name=...)`),
anonymous constraints (another reason for naming conventions), changes to `Enum` values
on PostgreSQL, views, triggers, functions, and data migrations.

### A reviewed migration

```python
"""add orders.status"""
from alembic import op
import sqlalchemy as sa

revision = "3f2a1c9b"
down_revision = "a1b2c3d4"

def upgrade() -> None:
    # 1. add as nullable with a server default so existing rows are valid
    op.add_column("orders", sa.Column("status", sa.String(20), server_default="open", nullable=True))
    # 2. backfill (data migration) — use Core, not ORM models (models change over time)
    op.execute("UPDATE orders SET status = 'open' WHERE status IS NULL")
    # 3. tighten
    op.alter_column("orders", "status", nullable=False)
    op.create_index("ix_orders_status", "orders", ["status"])

def downgrade() -> None:
    op.drop_index("ix_orders_status", table_name="orders")
    op.drop_column("orders", "status")
```

### Zero-downtime tips (PostgreSQL)

- Create indexes on big tables concurrently, outside a transaction:
  ```python
  with op.get_context().autocommit_block():
      op.create_index("ix_orders_user", "orders", ["user_id"], postgresql_concurrently=True)
  ```
- Add `NOT NULL` via a `CHECK (...) NOT VALID` constraint, `VALIDATE`, then set NOT NULL.
- Expand/contract: add new column → deploy code writing both → backfill → switch reads
  → drop old column in a later release.
- Set `lock_timeout` in migrations so they fail fast instead of blocking traffic.

### Multiple heads

When two branches each add a migration: `alembic heads` shows both;
`alembic merge -m "merge" <rev1> <rev2>` creates a merge revision.

---

## 8.2 FastAPI

### Sync (simple, works well with a threadpool)

```python
from typing import Annotated, Iterator
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

app = FastAPI()

def get_session() -> Iterator[Session]:
    with SessionLocal() as session:
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise

SessionDep = Annotated[Session, Depends(get_session)]

@app.get("/users/{user_id}", response_model=UserRead)
def read_user(user_id: int, session: SessionDep):
    user = session.get(User, user_id)
    if user is None:
        raise HTTPException(404)
    return user                              # Pydantic serializes via from_attributes
```

FastAPI runs `def` endpoints in a threadpool, so each request has its own thread and
its own Session. The default threadpool (40 threads) should be reconciled with your
pool size.

### Async

```python
from contextlib import asynccontextmanager
from typing import Annotated, AsyncIterator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

engine = create_async_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await engine.dispose()

app = FastAPI(lifespan=lifespan)

async def get_session() -> AsyncIterator[AsyncSession]:
    async with SessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise

SessionDep = Annotated[AsyncSession, Depends(get_session)]

@app.get("/users", response_model=list[UserWithAddresses])
async def list_users(session: SessionDep):
    result = await session.scalars(
        select(User).options(selectinload(User.addresses)).limit(100)
    )
    return result.all()
```

**Serialization gotcha:** Pydantic reads every field in `response_model`. If a field
maps to an unloaded relationship, that triggers a lazy load — `MissingGreenlet` in
async, N+1 in sync. Eager-load exactly what the response schema needs, and set
`lazy="raise"` on relationships so mismatches fail in tests.

**Commit timing:** with the dependency above, the commit runs after the endpoint
returns, and (in recent FastAPI versions) dependency teardown runs before the response
is sent, so a failed commit becomes a 500 instead of a false success. If you need the
committed state inside the handler (e.g. to return server-generated values), commit
explicitly in the endpoint/service.

---

## 8.3 Pydantic v2 — DTOs at the boundary

Keep ORM models and API schemas separate. ORM models describe storage; schemas
describe contracts (what clients send and receive).

```python
from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr

class AddressRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)   # read from ORM attributes
    id: int
    email_address: EmailStr

class UserCreate(BaseModel):
    name: str
    fullname: str | None = None

class UserUpdate(BaseModel):
    name: str | None = None
    fullname: str | None = None

class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    fullname: str | None
    created_at: datetime

class UserWithAddresses(UserRead):
    addresses: list[AddressRead]
```

Converting:

```python
# Request → ORM
user = User(**payload.model_dump())

# Partial update (PATCH): only fields the client actually sent
for field, value in payload.model_dump(exclude_unset=True).items():
    setattr(user, field, value)

# ORM → response
UserRead.model_validate(user)
```

Generating Pydantic models from SQLAlchemy models automatically (via
`sqlalchemy.inspect(Model).columns`) is possible, but hand-written schemas usually
age better because API and storage evolve independently.

---

## 8.4 SQLModel

SQLModel (by FastAPI's author) merges a Pydantic model and an SQLAlchemy model into one
class:

```python
from sqlmodel import Field, Session, SQLModel, create_engine, select

class Hero(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    age: int | None = None

engine = create_engine("sqlite://")
SQLModel.metadata.create_all(engine)

with Session(engine) as session:
    session.add(Hero(name="Deadpond"))
    session.commit()
    heroes = session.exec(select(Hero).where(Hero.age == None)).all()
```

**Trade-offs:**

- ✅ Less duplication for CRUD APIs; excellent FastAPI docs.
- ⚠️ Advanced SQLAlchemy features (complex relationships, inheritance, hybrid
  properties, loader options) work but often need `sa_column=` / `sa_relationship=`
  escape hatches.
- ⚠️ Version lag: as of October 2026 SQLModel still pins `SQLAlchemy <2.1`, so SQLModel
  projects are on the 2.0.x line until that pin is relaxed. Check
  [the release notes](https://sqlmodel.tiangolo.com/release-notes/) before upgrading.

A common middle ground: plain SQLAlchemy models + Pydantic schemas (§8.3), which is
what this guide recommends for anything beyond simple CRUD.

---

## 8.5 Flask-SQLAlchemy

```python
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql+psycopg://..."
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"pool_pre_ping": True, "pool_recycle": 1800}
db.init_app(app)

class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]

@app.get("/users/<int:uid>")
def get_user(uid):
    user = db.get_or_404(User, uid)
    return {"id": user.id, "name": user.name}

@app.post("/users")
def create_user():
    db.session.add(User(name=request.json["name"]))
    db.session.commit()
    return "", 201
```

Flask-SQLAlchemy 3.x provides a request-scoped `db.session` (removed at app-context
teardown), `db.paginate(select(...))`, and integrates with **Flask-Migrate** (a thin
Alembic wrapper: `flask db migrate`, `flask db upgrade`). Use the 2.x query style
(`db.session.execute(select(...))`); `Model.query` is legacy.

---

## 8.6 pandas / Polars / data tooling

```python
import pandas as pd
from sqlalchemy import select

# Read: accepts an Engine/Connection and a select() or SQL string
df = pd.read_sql(select(Order.id, Order.total, Order.created_at), engine)
df = pd.read_sql("SELECT * FROM orders WHERE total > %(t)s", engine, params={"t": 100})

# Write
df.to_sql(
    "orders_staging", engine,
    if_exists="append", index=False,
    method="multi", chunksize=5_000,
)
```

Tips:

- For large PostgreSQL loads, `to_sql` is slow; use psycopg's `COPY` through the raw
  connection (`engine.raw_connection()`), or `adbc` drivers.
- **Polars**: `pl.read_database(query=select(...), connection=engine)` and
  `df.write_database(table_name, connection=engine)`.
- Reading into dataframes bypasses the ORM — that's a feature for analytics.

---

## 8.7 Background jobs (Celery, RQ, Dramatiq, arq)

Rules:

1. **Create the engine per worker process.** With Celery's prefork pool, dispose
   inherited connections after fork:

   ```python
   from celery.signals import worker_process_init

   @worker_process_init.connect
   def _reset_pool(**_):
       engine.dispose(close=False)
   ```

2. **One session per task**, opened inside the task.
3. **Pass IDs, not ORM objects**, to tasks — objects don't survive serialization and
   would be stale anyway.
4. Enqueue tasks **after commit**, otherwise a worker may look for a row that isn't
   committed yet. Use an `after_commit` session event or the outbox pattern.

```python
@celery_app.task(bind=True, max_retries=3)
def send_receipt(self, order_id: int):
    with SessionLocal() as session:
        order = session.get(Order, order_id)
        if order is None:
            return
        mailer.send(order.user.email, render(order))
```

---

## 8.8 pytest & test tooling

Covered in depth in [Chapter 7 §7.10](07-architecture.md#710-testing). Useful
packages:

| Package | Purpose |
|---------|---------|
| `testcontainers` | Throwaway PostgreSQL/MySQL in Docker per test session |
| `pytest-postgresql` | Spin up a local PG process for tests |
| `factory_boy` / `polyfactory` | Model factories |
| `pytest-asyncio` / `anyio` | Async tests |
| `pytest-alembic` | Tests that migrations upgrade/downgrade cleanly and match models |

---

## 8.9 Observability

### OpenTelemetry

```bash
pip install opentelemetry-instrumentation-sqlalchemy
```

```python
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

SQLAlchemyInstrumentor().instrument(engine=engine, enable_commenter=True)
# async: instrument(engine=async_engine.sync_engine)
```

Every query becomes a span with the statement, duration, and DB attributes;
`enable_commenter` appends trace context as a SQL comment so you can correlate slow-log
entries with traces.

### Sentry, Datadog, New Relic

Their Python SDKs auto-instrument SQLAlchemy when the integration is enabled, recording
queries as spans and flagging N+1 patterns.

### Logging

```python
import logging
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)   # SQL statements
logging.getLogger("sqlalchemy.pool").setLevel(logging.DEBUG)    # checkouts/checkins
```

`echo=True` is the same as INFO on `sqlalchemy.engine` for that engine.

---

## 8.10 Domain-specific extensions

| Package | Adds |
|---------|------|
| **pgvector** (`pgvector.sqlalchemy.Vector`) | Vector columns and `l2_distance` / `cosine_distance` operators for embeddings / similarity search |
| **GeoAlchemy2** | PostGIS / SpatiaLite geometry & geography types and spatial functions |
| **SQLAlchemy-Utils** | Extra types (EmailType, URLType, ChoiceType), `database_exists`/`create_database` helpers |
| **sqlalchemy-continuum** | Versioning / history tables |
| **SQLAlchemy-Searchable** | PostgreSQL full-text search helpers |
| **sqladmin** / **Flask-Admin** | Admin UIs over your models |
| **dialects** for Snowflake, BigQuery, Databricks, DuckDB (`duckdb_engine`), ClickHouse, CockroachDB | Run Core (and often ORM) against analytics or distributed databases |

Example with pgvector:

```python
from pgvector.sqlalchemy import Vector

class Doc(Base):
    __tablename__ = "doc"
    id: Mapped[int] = mapped_column(primary_key=True)
    content: Mapped[str]
    embedding: Mapped[list[float]] = mapped_column(Vector(1536))

nearest = session.scalars(
    select(Doc).order_by(Doc.embedding.cosine_distance(query_vec)).limit(5)
).all()
```

Check each extension's compatibility notes before upgrading SQLAlchemy minor versions;
third-party dialects in particular may need updates for 2.1 (e.g. the new
`DOUBLE`-in-`CAST` float rendering and operator class validation).

---

## 8.11 Where to go next

- **Docs:** https://docs.sqlalchemy.org/en/21/ — especially the ORM Querying Guide and
  "Session Basics" FAQ.
- **2.1 migration notes:** https://docs.sqlalchemy.org/en/21/changelog/migration_21.html
- **Examples** shipped with SQLAlchemy (`examples/` in the repo): versioning,
  sharding, performance suites, syntax extensions.
- **GitHub Discussions** for questions: https://github.com/sqlalchemy/sqlalchemy/discussions

Back to the [Index](00-index.md).
