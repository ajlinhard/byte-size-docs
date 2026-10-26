# Chapter 6 — Asyncio

**Level:** Advanced · **Prev:** [Engines, Pooling & Transactions](05-engine-pooling-transactions.md) · **Next:** [Application Architecture](07-architecture.md)

---

## 6.1 Setup

```bash
pip install "sqlalchemy[asyncio]"   # 🆕 2.1: greenlet is NOT installed without this extra
pip install asyncpg                 # or: "psycopg[binary]", aiomysql, asyncmy, aiosqlite, oracledb
```

Async URLs name an async driver:

```python
"postgresql+asyncpg://user:pw@host/db"
"postgresql+psycopg://user:pw@host/db"     # psycopg 3 supports both sync and async
"mysql+aiomysql://user:pw@host/db"
"sqlite+aiosqlite:///app.db"
"oracle+oracledb://user:pw@host/?service_name=X"   # async via create_async_engine
```

---

## 6.2 How it works (and why it matters)

SQLAlchemy's internals are synchronous. The asyncio extension runs that sync code
inside a **greenlet** and, whenever the code would block on the database, switches
back to the event loop to `await` the async driver. You get real non-blocking IO with
the same ORM logic.

The consequence: **any IO must happen inside an awaited SQLAlchemy call.** Code that
would implicitly hit the DB from a plain attribute access — a lazy load, an expired
attribute refresh — can't `await`, so it raises `MissingGreenlet`:

```
sqlalchemy.exc.MissingGreenlet: greenlet_spawn has not been called;
can't call await_only() here. Was IO attempted in an unexpected place?
```

Nearly every asyncio difficulty is about avoiding implicit IO. §6.5 covers how.

---

## 6.3 Core with asyncio

```python
import asyncio
from sqlalchemy import text, select
from sqlalchemy.ext.asyncio import create_async_engine

engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=True)

async def main():
    async with engine.begin() as conn:
        await conn.run_sync(metadata_obj.create_all)       # run sync API (DDL) on the async conn
        await conn.execute(insert(user_table), [{"name": "a"}, {"name": "b"}])

    async with engine.connect() as conn:
        result = await conn.execute(select(user_table))
        print(result.all())                                # buffered result: no await needed

        # Streaming: server-side cursor, consume with async for
        stream = await conn.stream(select(user_table))
        async for row in stream:
            print(row)

    await engine.dispose()                                 # close pool at shutdown

asyncio.run(main())
```

---

## 6.4 ORM with `AsyncSession`

```python
from sqlalchemy.ext.asyncio import AsyncAttrs, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, selectinload

class Base(AsyncAttrs, DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "user_account"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    addresses: Mapped[list["Address"]] = relationship(back_populates="user", lazy="raise")

class Address(Base):
    __tablename__ = "address"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str]
    user_id: Mapped[int] = mapped_column(ForeignKey("user_account.id"))
    user: Mapped[User] = relationship(back_populates="addresses", lazy="raise")

engine = create_async_engine("postgresql+asyncpg://app:pw@localhost/app", pool_pre_ping=True)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)    # ← important

async def create_user(name: str, emails: list[str]) -> User:
    async with SessionLocal.begin() as session:
        user = User(name=name, addresses=[Address(email=e) for e in emails])
        session.add(user)
    return user                  # safe to read user.name: expire_on_commit=False

async def list_users() -> list[User]:
    async with SessionLocal() as session:
        result = await session.scalars(
            select(User).options(selectinload(User.addresses)).order_by(User.id)
        )
        return result.all()

async def rename(user_id: int, new: str) -> None:
    async with SessionLocal.begin() as session:
        user = await session.get(User, user_id)
        user.name = new         # flushed & committed at block exit
```

API mapping:

| Sync `Session` | `AsyncSession` |
|----------------|----------------|
| `session.execute(stmt)` | `await session.execute(stmt)` |
| `session.scalars(stmt)` | `await session.scalars(stmt)` |
| `session.get(M, pk)` | `await session.get(M, pk)` |
| `session.commit()` / `rollback()` / `flush()` | `await ...` |
| `session.refresh(obj)` | `await session.refresh(obj, ["attr"])` |
| `session.delete(obj)` | `await session.delete(obj)` |
| `session.add(obj)` | `session.add(obj)` (no IO, no await) |
| `session.stream(...)` | `await session.stream(stmt)` → `async for` |
| `session.connection()` | `await session.connection()` |

---

## 6.5 Avoiding implicit IO — the rules

1. **`expire_on_commit=False`** on `async_sessionmaker`. Otherwise every attribute
   access after commit tries to refresh from the DB → `MissingGreenlet`.

2. **Eager-load relationships** you'll touch: `selectinload` / `joinedload` in the
   query. Set `lazy="raise"` on relationships so mistakes fail loudly with a clear
   message instead of `MissingGreenlet`.

3. **Use `AsyncAttrs.awaitable_attrs`** when you genuinely want to lazy-load one
   attribute:

   ```python
   addresses = await user.awaitable_attrs.addresses
   ```

   (This doesn't work if the relationship is `lazy="raise"`; use explicit refresh.)

4. **Refresh explicitly**: `await session.refresh(user, ["addresses"])`.

5. **Server-generated values**: if a column has `server_default` or `onupdate` and you
   need it right after INSERT/UPDATE, either set
   `__mapper_args__ = {"eager_defaults": True}` (uses RETURNING) or
   `await session.refresh(obj)`.

6. **Big collections**: use `WriteOnlyMapped` and query explicitly. `lazy="dynamic"`
   is not supported in asyncio.

7. **Run sync code in a greenlet** when you need an existing sync helper:

   ```python
   def sync_helper(sync_session, user_id):
       u = sync_session.get(User, user_id)
       return [a.email for a in u.addresses]    # lazy loads are fine in here

   emails = await session.run_sync(sync_helper, 1)
   ```

---

## 6.6 Concurrency rules

- **One `AsyncSession` per task.** A Session (sync or async) is *not* safe to share
  between concurrent tasks. This is wrong:

  ```python
  # ❌ two tasks using one session concurrently
  await asyncio.gather(session.execute(q1), session.execute(q2))
  ```

  Do this:

  ```python
  async def run(q):
      async with SessionLocal() as s:
          return (await s.execute(q)).all()

  r1, r2 = await asyncio.gather(run(q1), run(q2))     # ✅ separate sessions/connections
  ```

- Mind the pool: 50 concurrent tasks against `pool_size=5, max_overflow=10` → 35 of
  them wait (up to `pool_timeout`). Bound concurrency with a semaphore if needed.

- **`async_scoped_session`** exists (scoped by `asyncio.current_task`), but explicit
  session passing / dependency injection is clearer and is what FastAPI apps do.

- Always `await engine.dispose()` on shutdown; otherwise you may see "event loop is
  closed" warnings as connections are garbage-collected.

- **Cancellation:** if a task is cancelled mid-query, the connection is invalidated
  rather than returned to the pool in an unknown state. This is correct behaviour; just
  be aware that frequent timeouts/cancellations cost reconnections.

---

## 6.7 Choosing an async PostgreSQL driver

| | **asyncpg** | **psycopg 3 (async)** |
|---|---|---|
| Speed | Very fast (binary protocol, Cython) | Fast; close in most workloads |
| Sync + async in one driver | No | **Yes** — same driver for app, scripts, Alembic |
| Prepared statements | Automatic (watch out with PgBouncer) | Configurable (`prepare_threshold`) |
| COPY support | Yes | Yes |
| SQLAlchemy 2.1 default for `postgresql://` | No | **Yes** (sync dialect) |

Both are good choices. psycopg 3 reduces the number of drivers in your stack; asyncpg
squeezes out more throughput in heavy-read services.

---

## 6.8 Testing async code

```python
# conftest.py — pytest + pytest-asyncio (or anyio)
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

@pytest.fixture(scope="session")
async def engine():
    eng = create_async_engine(TEST_DB_URL)
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield eng
    await eng.dispose()

@pytest.fixture
async def session(engine):
    async with engine.connect() as conn:
        trans = await conn.begin()
        async_session = AsyncSession(bind=conn, join_transaction_mode="create_savepoint",
                                     expire_on_commit=False)
        yield async_session
        await async_session.close()
        await trans.rollback()        # every test starts clean
```

Note: session-scoped async fixtures require your event loop to be session-scoped too
(e.g. `asyncio_default_fixture_loop_scope = "session"` in pytest-asyncio config).

Next: [Chapter 7](07-architecture.md) — structuring real applications.
