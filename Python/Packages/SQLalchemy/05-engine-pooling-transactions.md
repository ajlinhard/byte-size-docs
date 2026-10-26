# Chapter 5 — Engines, Connections, Pooling & Transactions

**Level:** Intermediate → Advanced · **Prev:** [Loading & Efficiency](04-loading-performance.md) · **Next:** [Asyncio](06-asyncio.md)

---

## 5.1 The lifecycle of a connection

```
create_engine()           engine.connect() / session needs SQL
     │                            │
     ▼                            ▼
 ┌────────┐  checkout   ┌──────────────────┐   execute   ┌──────────┐
 │  Pool  │ ──────────► │ Connection (txn) │ ──────────► │ Database │
 └────────┘ ◄────────── └──────────────────┘             └──────────┘
             checkin
     (rollback-on-return resets state, connection stays open for reuse)
```

Key facts:

- The pool keeps DBAPI connections **open** between uses. Opening a PostgreSQL
  connection (TCP + TLS + auth) costs milliseconds; reusing one costs microseconds.
- On check-in, the pool issues a **rollback** to clear any transaction state
  (`pool_reset_on_return="rollback"`, the default).
- The pool is **per process**. Each Gunicorn/uvicorn worker, Celery worker, and
  multiprocessing child has its own.

---

## 5.2 Pool types

| Pool | Behaviour | Default for |
|------|-----------|-------------|
| `QueuePool` | Bounded pool: `pool_size` persistent + `max_overflow` temporary connections | Most DBs (sync) |
| `AsyncAdaptedQueuePool` | Same, asyncio-safe | Async engines |
| `NullPool` | No pooling: open on checkout, close on checkin | — |
| `StaticPool` | Exactly one connection, shared | — (useful for in-memory SQLite tests) |
| `SingletonThreadPool` | One connection per thread | Legacy SQLite `:memory:` |

```python
from sqlalchemy.pool import NullPool, StaticPool

# External pooler (PgBouncer, RDS Proxy) or serverless functions → let them pool
engine = create_engine(url, poolclass=NullPool)

# In-memory SQLite shared across threads in tests
engine = create_engine(
    "sqlite://",
    poolclass=StaticPool,
    connect_args={"check_same_thread": False},
)
```

### Sizing `QueuePool`

```python
engine = create_engine(
    url,
    pool_size=10,         # connections kept open
    max_overflow=20,      # extra connections under burst; closed when returned
    pool_timeout=30,      # seconds to wait for a free connection before TimeoutError
    pool_recycle=1800,    # close connections older than 30 min on checkout
    pool_pre_ping=True,   # cheap liveness check on checkout
    pool_use_lifo=True,   # reuse most-recent connections; lets idle ones time out server-side
)
```

**Do the arithmetic.** Max connections per process = `pool_size + max_overflow`.
Multiply by the number of processes, across every service using the database, and
compare with the server's `max_connections` (PostgreSQL defaults to 100):

```
4 pods × 4 gunicorn workers × (10 + 20) = 480 connections  ← over PG's default 100
```

For many small processes, run PgBouncer (transaction mode) or a managed proxy and
use smaller pools or `NullPool` in the app.

> **PgBouncer in transaction mode + psycopg/asyncpg:** disable server-side prepared
> statement caching, or you'll get "prepared statement does not exist" errors. For
> asyncpg: `connect_args={"statement_cache_size": 0, "prepared_statement_cache_size": 0}`
> (newer PgBouncer versions with `max_prepared_statements` support them).

### Dealing with dropped connections

Databases, load balancers and firewalls close idle connections. Symptoms:
`OperationalError: server closed the connection unexpectedly`, `MySQL server has gone away`.

- **`pool_pre_ping=True`** — runs a lightweight ping on checkout; reconnects
  transparently if dead. Small cost per checkout, eliminates most stale-connection
  errors. Recommended for nearly all production apps.
- **`pool_recycle=N`** — replace connections older than N seconds. Set below the
  server/proxy idle timeout (MySQL `wait_timeout` defaults to 8h; cloud LBs often
  ~350s–1h).
- When a "disconnect" error happens mid-transaction, SQLAlchemy **invalidates** the
  whole pool's older connections. The current operation still fails — wrap critical
  idempotent operations in a retry.

### Pools and `fork()`

A pooled connection must never be shared between a parent and a forked child (they'd
interleave bytes on the same socket). If you create an engine before forking (Gunicorn
`--preload`, multiprocessing, Celery prefork):

```python
# In the child, right after fork:
engine.dispose(close=False)   # drop the parent's connections without closing them
```

Or simply create the engine lazily inside each worker.

### Monitoring the pool

```python
print(engine.pool.status())
# Pool size: 10  Connections in pool: 7 Current Overflow: -3 Current Checked out connections: 3
```

Pool events (`connect`, `checkout`, `checkin`, `close`) let you export metrics, or use
OpenTelemetry instrumentation ([Chapter 8](08-integrations.md)).

---

## 5.3 Transactions in Core

### Isolation levels

```python
# Engine-wide
engine = create_engine(url, isolation_level="REPEATABLE READ")

# Per connection
with engine.connect().execution_options(isolation_level="SERIALIZABLE") as conn:
    ...

# A sibling engine sharing the same pool, with a different level
autocommit_engine = engine.execution_options(isolation_level="AUTOCOMMIT")
```

`AUTOCOMMIT` is needed for statements that can't run in a transaction
(`CREATE DATABASE`, `VACUUM`, `CREATE INDEX CONCURRENTLY`).

### Nested transactions (SAVEPOINT)

```python
with engine.begin() as conn:
    conn.execute(insert(user_table).values(name="a"))
    try:
        with conn.begin_nested():               # SAVEPOINT
            conn.execute(insert(user_table).values(name="dupe"))
            raise ValueError("oops")
    except ValueError:
        pass                                    # ROLLBACK TO SAVEPOINT; "a" survives
# COMMIT
```

### Two-phase and other specialties

`conn.begin_twophase()` exists for XA-style distributed transactions on supporting
backends; most apps should prefer an outbox pattern instead.

---

## 5.4 Transactions with the Session

The Session wraps a Core transaction. The pattern to standardize on:

```python
SessionLocal = sessionmaker(engine, expire_on_commit=False)

with SessionLocal.begin() as session:
    ...                          # commit on success, rollback on error, close
```

### Savepoints in the ORM

```python
with SessionLocal.begin() as session:
    session.add(User(name="keeper"))
    for row in incoming:
        try:
            with session.begin_nested():        # SAVEPOINT per row
                session.add(User(**row))
        except IntegrityError:
            log.warning("skipping duplicate %s", row)   # only this row rolled back
```

### Session-level execution options 🆕 2.1

Options now apply to everything the session runs, including flushes and eager loads:

```python
session = Session(
    engine,
    execution_options={"schema_translate_map": {None: "tenant_42"}},
)
```

Great for schema-per-tenant designs and for passing flags to your event hooks.

### Joining an external transaction (the testing pattern)

You can bind a Session to a Connection that already has a transaction, and have the
Session use savepoints so that its `commit()` never actually commits:

```python
conn = engine.connect()
outer = conn.begin()
session = Session(bind=conn, join_transaction_mode="create_savepoint")

session.add(User(name="test"))
session.commit()       # releases a SAVEPOINT, outer transaction still open

session.close()
outer.rollback()       # everything undone
conn.close()
```

This is the backbone of fast, isolated database tests ([Chapter 7](07-architecture.md#710-testing)).

### Locking

```python
# SELECT ... FOR UPDATE
acct = session.scalars(select(Account).where(Account.id == 1).with_for_update()).one()

# Variants
.with_for_update(nowait=True)          # fail instead of waiting
.with_for_update(skip_locked=True)     # job-queue pattern: grab unlocked rows only
.with_for_update(read=True)            # FOR SHARE
.with_for_update(of=Account)           # lock only some tables in a join
```

### Optimistic concurrency (version counters)

```python
class Document(Base):
    __tablename__ = "document"
    id: Mapped[int] = mapped_column(primary_key=True)
    body: Mapped[str]
    version: Mapped[int] = mapped_column(nullable=False)
    __mapper_args__ = {"version_id_col": version}
```

Every UPDATE adds `WHERE version = :old` and increments it. If another transaction
changed the row first, you get `StaleDataError` — retry or report a conflict.

### Retrying serialization failures

Under `SERIALIZABLE` (or with deadlocks), the DB may abort a transaction and expect
you to retry it whole:

```python
from sqlalchemy.exc import OperationalError, DBAPIError

def run_with_retry(fn, attempts=3):
    for i in range(attempts):
        try:
            with SessionLocal.begin() as session:
                return fn(session)
        except DBAPIError as e:
            if getattr(e.orig, "sqlstate", None) in ("40001", "40P01") and i < attempts - 1:
                continue        # serialization failure / deadlock → retry
            raise
```

---

## 5.5 Events

Events let you hook into almost every stage. Register with `event.listen()` or the
`@event.listens_for` decorator.

### Engine / connection events

```python
from sqlalchemy import event

@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_conn, record):
    cur = dbapi_conn.cursor()
    cur.execute("PRAGMA foreign_keys=ON")          # SQLite doesn't enforce FKs by default
    cur.execute("PRAGMA journal_mode=WAL")
    cur.close()

@event.listens_for(engine, "checkout")
def on_checkout(dbapi_conn, record, proxy):
    ...                                             # e.g. SET search_path / role per checkout
```

> **🆕 2.1:** Exceptions escaping `before_cursor_execute`/`after_cursor_execute` hooks
> that touch the raw DBAPI cursor are now routed through SQLAlchemy's error handling:
> the connection is properly invalidated and DBAPI errors are wrapped as
> `DBAPIError`.

### Mapper (per-class) events

```python
from datetime import datetime, timezone

@event.listens_for(Document, "before_update")
def touch(mapper, connection, target):
    target.updated_at = datetime.now(timezone.utc)
```

Inside mapper events you're mid-flush: modify the target's own column attributes only;
use the `connection` for extra SQL. Don't `session.add()` new objects here — do that in
`before_flush`.

### Session events

```python
from sqlalchemy.orm import Session

@event.listens_for(Session, "before_flush")
def audit(session, flush_context, instances):
    for obj in session.dirty:
        if session.is_modified(obj) and hasattr(obj, "audit_entries"):
            session.add(AuditEntry(target=repr(obj)))

@event.listens_for(Session, "after_commit")
def publish(session):
    for evt in session.info.pop("pending_events", []):
        bus.publish(evt)          # only after the data is durable
```

### ORM execute events — the most powerful hook

`do_orm_execute` intercepts every ORM statement, so you can add global criteria:

```python
from sqlalchemy.orm import with_loader_criteria

@event.listens_for(Session, "do_orm_execute")
def _soft_delete_filter(state):
    if (
        state.is_select
        and not state.is_column_load
        and not state.execution_options.get("include_deleted", False)
    ):
        state.statement = state.statement.options(
            with_loader_criteria(SoftDeleteMixin, lambda cls: cls.deleted_at.is_(None),
                                 include_aliases=True)
        )
```

### Registry events 🆕 2.1

```python
@event.listens_for(Base, "after_configured")
def mappings_ready(registry):
    print("all mappers configured")
```

---

## 5.6 Error handling

Exception hierarchy you'll actually catch:

```
SQLAlchemyError
├── DBAPIError                     (wraps driver errors; .orig is the driver exception)
│   ├── IntegrityError             unique/FK/check/NOT NULL violations
│   ├── OperationalError           connection lost, timeout, deadlock (driver dependent)
│   ├── ProgrammingError           bad SQL, missing table
│   └── DataError                  value out of range, bad type
├── InvalidRequestError            API misuse (e.g. raiseload hit)
├── NoResultFound / MultipleResultsFound
├── TimeoutError                   pool exhausted (pool_timeout)
└── orm.exc.StaleDataError         optimistic concurrency failure
```

After **any** exception during a flush, the Session's transaction is in a failed state —
you must `rollback()` before using it again (`PendingRollbackError` otherwise). The
`with ...begin()` pattern handles this for you.

---

## 5.7 Multiple databases

### Read replicas / routing

Subclass `Session` and override `get_bind`:

```python
writer = create_engine(PRIMARY_URL, pool_pre_ping=True)
reader = create_engine(REPLICA_URL, pool_pre_ping=True)

from sqlalchemy import Insert, Update, Delete

class RoutingSession(Session):
    def get_bind(self, mapper=None, clause=None, **kw):
        if self._flushing or isinstance(clause, (Insert, Update, Delete)):
            return writer                       # all writes go to the primary
        if self.info.get("use_primary"):
            return writer                       # request pinned after a write
        return reader

SessionLocal = sessionmaker(class_=RoutingSession)
```

Beware read-after-write: right after a commit, the replica may lag. Pin a request to
the primary after it writes (e.g. set `session.info["use_primary"] = True`).

### Different tables in different databases

```python
SessionLocal = sessionmaker(binds={User: users_engine, AnalyticsEvent: analytics_engine})

# Or bind whole base classes
class UsersBase(DeclarativeBase): ...
class AnalyticsBase(DeclarativeBase): ...
SessionLocal = sessionmaker(binds={UsersBase: users_engine, AnalyticsBase: analytics_engine})
```

> **🆕 2.1:** `session.binds` is now a public read-only mapping, and `AsyncSession`
> gains `bind_mapper()`, `bind_table()` and `get_async_bind()`.

Transactions across two databases are **not** atomic. Use the outbox pattern or
idempotent consumers when both must change.

### Horizontal sharding

`sqlalchemy.ext.horizontal_shard.ShardedSession` routes queries to shards by a
chooser function — powerful but complex; consider it only when partitioning in the
database (e.g. PostgreSQL declarative partitioning, Citus) isn't an option.

---

## 5.8 Production configuration template

```python
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

engine = create_engine(
    settings.database_url,             # e.g. postgresql+psycopg://...
    pool_size=settings.db_pool_size,   # 5–20 typical per process
    max_overflow=settings.db_max_overflow,
    pool_timeout=10,
    pool_recycle=1800,
    pool_pre_ping=True,
    pool_use_lifo=True,
    connect_args={
        "application_name": "orders-api",          # shows up in pg_stat_activity
        "options": "-c statement_timeout=15000",    # 15s server-side guard (psycopg)
    },
)

SessionLocal = sessionmaker(engine, expire_on_commit=False)
```

Next: [Chapter 6](06-asyncio.md) — doing all of this with `async`/`await`.
