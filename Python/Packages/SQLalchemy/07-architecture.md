# Chapter 7 — Application Architecture

**Level:** Advanced · **Prev:** [Asyncio](06-asyncio.md) · **Next:** [Integrations](08-integrations.md)

SQLAlchemy is unopinionated about how you structure an application. This chapter
collects patterns that hold up as codebases and teams grow.

---

## 7.1 The two non-negotiable rules

1. **One `Engine` per database URL per process**, created at startup and disposed at
   shutdown. Never create engines per request.
2. **One `Session` per unit of work** (typically per request, per job, or per
   command), never global, never shared across threads or tasks. The Session's
   lifecycle should be **controlled from outside** the business logic that uses it.

The SQLAlchemy docs summarize rule 2 as: *keep the lifecycle of the session separate
and external from functions and objects that access and/or manipulate database data.*

```python
# ❌ Each function opens and commits its own session — no shared transaction
def create_order(data):
    with SessionLocal.begin() as s:
        s.add(Order(**data))

def charge(order_id):
    with SessionLocal.begin() as s:
        ...

# ✅ The caller owns the transaction; functions accept a session
def create_order(session: Session, data) -> Order:
    order = Order(**data)
    session.add(order)
    return order

def charge(session: Session, order: Order) -> None:
    ...

with SessionLocal.begin() as session:      # one atomic unit
    order = create_order(session, data)
    charge(session, order)
```

---

## 7.2 Project layout

A layout that scales from small to large services:

```
app/
├── core/
│   ├── config.py            # settings (pydantic-settings)
│   └── db.py                # engine, sessionmaker, Base, naming conventions
├── models/                  # ORM classes, one module per aggregate
│   ├── __init__.py          # imports all models so metadata is complete (for Alembic)
│   ├── mixins.py
│   ├── user.py
│   └── order.py
├── repositories/            # optional: query encapsulation
│   ├── user_repo.py
│   └── order_repo.py
├── services/                # business logic; owns no sessions, receives them
│   └── checkout.py
├── schemas/                 # Pydantic DTOs for the API boundary
├── api/                     # FastAPI/Flask routes: open session, call service, map to DTO
└── migrations/              # Alembic
tests/
```

### `core/db.py`

```python
from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)

engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(engine, expire_on_commit=False)
```

**Circular imports between model modules:** use string names in relationships
(`relationship("Order")`) or `back_populates=lambda: Order.user` (🆕 2.1), and under
`TYPE_CHECKING` import the other class only for annotations:

```python
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .order import Order

class User(Base):
    orders: Mapped[list[Order]] = relationship(back_populates="user")
```

---

## 7.3 Reusable mixins

```python
from datetime import datetime
import uuid
from sqlalchemy import func, Uuid
from sqlalchemy.orm import Mapped, mapped_column, declared_attr

class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

class UUIDPkMixin:
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)

class SoftDeleteMixin:
    deleted_at: Mapped[datetime | None] = mapped_column(default=None, index=True)

class TableNameMixin:
    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

class Product(TableNameMixin, UUIDPkMixin, TimestampMixin, Base):
    name: Mapped[str]
```

Mixins with `ForeignKey` or `relationship()` must use `@declared_attr` so each subclass
gets its own copy.

> **UUIDv7 primary keys** sort by creation time, which keeps B-tree indexes compact
> (random UUIDv4 keys fragment them). Python 3.14 has `uuid.uuid7()`; PostgreSQL 18
> has `uuidv7()`. 🆕 2.1 supports server-side `uuidv7()` defaults in batched
> INSERT…RETURNING.

---

## 7.4 Repository pattern

A repository wraps query construction for one aggregate. It improves reuse and gives
tests a seam, but **don't let it hide the Session or commit**:

```python
from typing import Generic, TypeVar, Sequence
from sqlalchemy import select
from sqlalchemy.orm import Session

M = TypeVar("M", bound=Base)

class Repository(Generic[M]):
    model: type[M]

    def __init__(self, session: Session):
        self.session = session

    def get(self, pk) -> M | None:
        return self.session.get(self.model, pk)

    def add(self, obj: M) -> M:
        self.session.add(obj)
        return obj

    def list(self, *, limit: int = 100, offset: int = 0) -> Sequence[M]:
        return self.session.scalars(select(self.model).limit(limit).offset(offset)).all()


class OrderRepository(Repository[Order]):
    model = Order

    def open_for_user(self, user_id: int) -> Sequence[Order]:
        stmt = (
            select(Order)
            .where(Order.user_id == user_id, Order.status == "open")
            .options(selectinload(Order.items))
            .order_by(Order.created_at.desc())
        )
        return self.session.scalars(stmt).all()
```

**When to skip repositories:** the Session already *is* a repository + unit of work. In
small apps, a module of query functions (`def open_orders(session, user_id): ...`) is
simpler and just as testable. Avoid generic repositories that re-wrap every Session
method — they add indirection without value.

---

## 7.5 Service layer and the Unit of Work

Services orchestrate business operations; the caller (route, job, CLI) owns the
transaction:

```python
class CheckoutService:
    def __init__(self, session: Session):
        self.session = session
        self.orders = OrderRepository(session)

    def checkout(self, user_id: int, cart: list[CartLine]) -> Order:
        order = Order(user_id=user_id, status="pending")
        for line in cart:
            product = self.session.get(Product, line.product_id, with_for_update=True)
            if product.stock < line.qty:
                raise OutOfStock(product.id)
            product.stock -= line.qty
            order.items.append(OrderItem(product=product, qty=line.qty, price=product.price))
        self.orders.add(order)
        self.session.flush()                 # get order.id; still uncommitted
        self.session.info.setdefault("events", []).append(OrderPlaced(order.id))
        return order

# Route / job:
with SessionLocal.begin() as session:
    order = CheckoutService(session).checkout(user_id, cart)
# commit happened; an after_commit hook publishes queued events
```

This is the **Unit of Work** pattern: all changes for the business operation commit
together or not at all. SQLAlchemy's Session implements it natively.

### Transactional outbox

To publish messages reliably, write them to an `outbox` table in the *same*
transaction, and have a separate relay deliver and mark them sent. This avoids "DB
committed but message lost" (or vice versa).

---

## 7.6 Inheritance mapping

| Strategy | Tables | Pros | Cons |
|----------|--------|------|------|
| **Single table** | One table, discriminator column | Fast, simple queries | Nullable subclass columns |
| **Joined table** | Base table + one per subclass | Normalized, constraints per subclass | JOINs on every load |
| **Concrete table** | One full table per subclass | No joins for subclass queries | Polymorphic queries need UNION |

```python
# Single table
class Employee(Base):
    __tablename__ = "employee"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    type: Mapped[str]
    __mapper_args__ = {"polymorphic_on": "type", "polymorphic_identity": "employee"}

class Engineer(Employee):
    language: Mapped[str | None]                       # column added to "employee"
    __mapper_args__ = {"polymorphic_identity": "engineer"}

# Joined table: give the subclass its own table and a FK primary key
class Manager(Employee):
    __tablename__ = "manager"
    id: Mapped[int] = mapped_column(ForeignKey("employee.id"), primary_key=True)
    budget: Mapped[int]
    __mapper_args__ = {"polymorphic_identity": "manager"}

session.scalars(select(Employee))           # returns Engineer / Manager instances
session.scalars(select(Engineer))           # filters by discriminator
```

Use `selectin_polymorphic` / `with_polymorphic` to control how subclass columns load.
Prefer single-table unless subclasses diverge significantly.

---

## 7.7 Soft delete

Combine the `SoftDeleteMixin` above with a `do_orm_execute` hook so deleted rows are
filtered everywhere, including relationship loads:

```python
from sqlalchemy import event
from sqlalchemy.orm import Session, with_loader_criteria

@event.listens_for(Session, "do_orm_execute")
def _filter_soft_deleted(state):
    if (
        state.is_select
        and not state.is_column_load            # skip deferred-column / refresh loads
        and not state.is_relationship_load      # criteria already propagate to these
        and not state.execution_options.get("include_deleted", False)
    ):
        state.statement = state.statement.options(
            with_loader_criteria(
                SoftDeleteMixin,
                lambda cls: cls.deleted_at.is_(None),
                include_aliases=True,
            )
        )

# opt out when you need everything
session.scalars(select(User).execution_options(include_deleted=True))
```

Because `with_loader_criteria` is attached to the top-level statement, the same
criteria are carried into the lazy and eager loads of relationships made from the
objects it returns.

Also add a partial unique index so a deleted row doesn't block re-creation, e.g.
`Index("uq_user_email_live", "email", unique=True, postgresql_where=text("deleted_at IS NULL"))`.

---

## 7.8 Multi-tenancy

| Approach | How with SQLAlchemy |
|----------|--------------------|
| **Shared tables + `tenant_id` column** | `TenantMixin` + `do_orm_execute` + `with_loader_criteria(TenantMixin, lambda cls: cls.tenant_id == current_tenant())`. Back it with PostgreSQL Row-Level Security for defense in depth. |
| **Schema per tenant** | 🆕 2.1 `Session(engine, execution_options={"schema_translate_map": {None: tenant_schema}})` — now also applies to flushes. |
| **Database per tenant** | An engine per tenant (cached), chosen in `get_bind` or when creating the session. Watch total pool sizes. |

Use a `contextvars.ContextVar` to hold the current tenant so it works with threads and
asyncio.

---

## 7.9 Configuration & dependency injection

Avoid module-level sessions. Create the engine at app startup, store the factory on
the app (or in a DI container), and inject sessions per request. Frameworks:

- **FastAPI**: `Depends(get_session)` (see [Chapter 8](08-integrations.md#82-fastapi)).
- **Flask**: Flask-SQLAlchemy's `db.session` (a request-scoped `scoped_session`).
- **Scripts/CLI**: `with SessionLocal.begin() as session:` in `main()`.
- **Background jobs**: open a session *inside* each job; never pass ORM objects
  between processes — pass IDs.

### `scoped_session` (thread-local sessions)

```python
from sqlalchemy.orm import scoped_session
Session = scoped_session(sessionmaker(engine))
Session().add(obj)       # same session within a thread
Session.remove()         # call at request end
```

Useful for frameworks that expect a global, but explicit passing is clearer and is
required for asyncio.

---

## 7.10 Testing

### Strategy

- **Use the real database engine you run in production** (PostgreSQL in Docker /
  Testcontainers). SQLite differs in types, constraints, and locking.
- Create schema once per test session (`create_all` or run Alembic `upgrade head`).
- Wrap **each test in a transaction that is rolled back**, binding the Session with
  `join_transaction_mode="create_savepoint"` so app code can call `commit()` freely.

```python
# conftest.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from testcontainers.postgres import PostgresContainer

@pytest.fixture(scope="session")
def engine():
    with PostgresContainer("postgres:17") as pg:
        eng = create_engine(pg.get_connection_url().replace("psycopg2", "psycopg"))
        Base.metadata.create_all(eng)
        yield eng
        eng.dispose()

@pytest.fixture
def session(engine):
    conn = engine.connect()
    trans = conn.begin()
    sess = Session(bind=conn, join_transaction_mode="create_savepoint", expire_on_commit=False)
    yield sess
    sess.close()
    trans.rollback()
    conn.close()
```

### Factories

`factory_boy` with `SQLAlchemyModelFactory` (or `polyfactory`) creates realistic test
objects:

```python
import factory

class UserFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = User
        sqlalchemy_session_persistence = "flush"
    name = factory.Faker("user_name")
```

Set `UserFactory._meta.sqlalchemy_session = session` in a fixture.

### Guarding performance

Use the `assert_max_queries` helper from [Chapter 4](04-loading-performance.md#415-measuring)
in tests for key endpoints so N+1 regressions fail CI.

---

## 7.11 Anti-patterns checklist

- ❌ Global `session = Session()` at module import.
- ❌ Creating an engine per request or per function call.
- ❌ Committing inside repositories/helpers (breaks atomicity of the caller).
- ❌ Returning ORM objects out of a closed session and lazily touching relationships.
- ❌ Passing ORM objects to threads, processes or Celery tasks (pass primary keys).
- ❌ `Base.metadata.create_all()` in production startup instead of migrations.
- ❌ Catching exceptions around `flush()` and continuing without `rollback()`.
- ❌ Eager-loading defaults (`lazy="joined"`) on every relationship "to be safe".
- ❌ String-formatting user input into `text()`.

Next: [Chapter 8](08-integrations.md) — integrating with the wider ecosystem.
