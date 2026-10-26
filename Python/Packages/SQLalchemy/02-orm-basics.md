# Chapter 2 — ORM Basics

**Level:** Beginner · **Prev:** [Fundamentals & Core](01-fundamentals-core.md) · **Next:** [Querying in Depth](03-querying.md)

---

## 2.1 What the ORM adds

The ORM lets you work with *objects* instead of rows:

- **Mapping:** a Python class ↔ a `Table`. Attributes ↔ columns.
- **Identity map:** within one Session, a given primary key is always the *same* Python
  object. Load `User` id 5 twice → you get the identical instance.
- **Unit of Work:** you change attributes and add/delete objects; at flush time the
  Session works out the INSERT/UPDATE/DELETE statements in the correct dependency order.
- **Relationships:** `user.addresses` loads related rows for you, following foreign keys.

---

## 2.2 Declaring models (Annotated Declarative)

```python
from datetime import datetime
from typing import Optional

from sqlalchemy import ForeignKey, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "user_account"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    fullname: Mapped[Optional[str]]
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    addresses: Mapped[list["Address"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, name={self.name!r})"


class Address(Base):
    __tablename__ = "address"

    id: Mapped[int] = mapped_column(primary_key=True)
    email_address: Mapped[str]
    user_id: Mapped[int] = mapped_column(ForeignKey("user_account.id"))

    user: Mapped["User"] = relationship(back_populates="addresses")
```

### How the annotations work

`Mapped[...]` tells both SQLAlchemy and your type checker what the attribute holds:

| Annotation | Resulting column |
|------------|------------------|
| `Mapped[int]` | `INTEGER NOT NULL` |
| `Mapped[str]` | `VARCHAR NOT NULL` |
| `Mapped[Optional[str]]` or `Mapped[str \| None]` | `VARCHAR NULL` |
| `Mapped[datetime]` | `DATETIME NOT NULL` |
| `Mapped[Decimal]` | `NUMERIC NOT NULL` |
| `Mapped[uuid.UUID]` | `UUID` / `CHAR(32)` |
| `Mapped[MyEnum]` | `Enum(MyEnum)` |

- **Nullability comes from `Optional`** unless you override it with
  `mapped_column(nullable=...)`.
- A bare annotation (`fullname: Mapped[Optional[str]]`) needs no `mapped_column()` at all.
- Pass a SQL type to `mapped_column()` only when you need specifics (`String(30)`,
  `Numeric(10, 2)`, `JSONB`).

### Customising the type map

You can make annotations map to specific SQL types project-wide:

```python
from decimal import Decimal
from typing import Annotated
from sqlalchemy import Numeric, String, BigInteger
from sqlalchemy.orm import DeclarativeBase

str50 = Annotated[str, 50]
money = Annotated[Decimal, "money"]

class Base(DeclarativeBase):
    type_annotation_map = {
        int: BigInteger,
        str50: String(50),
        money: Numeric(12, 2),
    }

# Reusable column presets with Annotated + mapped_column
from sqlalchemy.orm import mapped_column
intpk = Annotated[int, mapped_column(primary_key=True)]
timestamp = Annotated[datetime, mapped_column(server_default=func.now())]

class Order(Base):
    __tablename__ = "order"
    id: Mapped[intpk]
    total: Mapped[money]
    created_at: Mapped[timestamp]
```

> **🆕 2.1:** `RegistryEvents.resolve_type_annotation` lets you resolve annotations to
> SQL types programmatically (including PEP 695 `type` aliases) via
> `@event.listens_for(Base, "resolve_type_annotation")`.

### Table-level configuration

```python
from sqlalchemy import Index, UniqueConstraint

class Membership(Base):
    __tablename__ = "membership"
    __table_args__ = (
        UniqueConstraint("user_id", "org_id"),
        Index("ix_membership_org", "org_id"),
        {"schema": "auth"},           # optional dict goes last
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user_account.id"))
    org_id: Mapped[int]
```

Create the tables (for tests/prototypes):

```python
from sqlalchemy import create_engine
engine = create_engine("sqlite://", echo=True)
Base.metadata.create_all(engine)
```

---

## 2.3 The Session

The `Session` is your workspace. It holds a connection (lazily), tracks every object
you load or add, and turns changes into SQL.

```python
from sqlalchemy.orm import Session, sessionmaker

# A factory configured once, at startup
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

with SessionLocal() as session:
    ...
```

### Object states

Every mapped object is in one of these states:

```
                session.add()          flush()
   Transient ────────────────► Pending ─────────► Persistent
   (new, no session)          (in session,       (has a row; in identity map)
                               no row yet)              │
                                                         │ session.close()/expunge()
                                                         ▼
                                                     Detached
                                         (has a row, no session — lazy loads fail)
   Persistent ──session.delete()+flush──► Deleted ──commit──► Detached
```

Check with `sqlalchemy.inspect(obj)`: `.transient`, `.pending`, `.persistent`,
`.detached`, `.deleted`.

### CRUD

```python
from sqlalchemy import select

# CREATE
with SessionLocal() as session:
    spongebob = User(
        name="spongebob",
        fullname="Spongebob Squarepants",
        addresses=[Address(email_address="spongebob@sqlalchemy.org")],
    )
    sandy = User(name="sandy", fullname="Sandy Cheeks")
    session.add_all([spongebob, sandy])
    session.commit()                   # INSERTs user + address (cascade), COMMIT
    print(spongebob.id)                # primary key populated after flush

# READ
with SessionLocal() as session:
    user = session.get(User, 1)                                   # by primary key (uses identity map first)
    user = session.scalars(select(User).where(User.name == "sandy")).one()
    users = session.scalars(select(User).order_by(User.id)).all()

# UPDATE — just change attributes
with SessionLocal() as session:
    sandy = session.scalars(select(User).filter_by(name="sandy")).one()
    sandy.fullname = "Sandy Squirrel"
    session.commit()                   # UPDATE user_account SET fullname=... WHERE id=...

# DELETE
with SessionLocal() as session:
    user = session.get(User, 2)
    session.delete(user)
    session.commit()
```

### The transaction pattern you'll use most

```python
with SessionLocal.begin() as session:    # begin a transaction
    session.add(User(name="patrick"))
# commits on success, rolls back on exception, closes the session
```

Equivalent long form:

```python
with SessionLocal() as session:
    try:
        session.add(User(name="patrick"))
        session.commit()
    except Exception:
        session.rollback()
        raise
```

### Flush vs commit

- **`flush()`** sends pending changes to the DB *within the current transaction*.
  Generated primary keys and server defaults become available. Nothing is permanent.
- **`commit()`** flushes, then commits the transaction.
- **Autoflush:** before running a query, the Session flushes automatically so queries
  see your pending changes. **🆕 2.1:** autoflush now happens before *every* execution,
  including `session.execute(text(...))`; in 2.0 it only fired for ORM statements.
  Temporarily disable with `with session.no_autoflush: ...`.

### Expiration and `expire_on_commit`

After `commit()`, the Session **expires** all loaded objects by default: their
attributes are cleared and will be reloaded from the DB on next access. That
guarantees you see fresh data in the next transaction, but it bites when you use the
object *after the session closes*:

```python
with Session(engine) as session:          # expire_on_commit=True (default)
    u = User(name="gary")
    session.add(u)
    session.commit()
print(u.name)   # DetachedInstanceError: tries to refresh, but there's no session
```

Two fixes:

1. `sessionmaker(..., expire_on_commit=False)` — very common in web apps and **required
   in practice for asyncio**.
2. Access/serialize what you need *before* the session closes.

Related tools: `session.refresh(obj)` reloads now; `session.expire(obj)` marks stale;
`session.expunge(obj)` detaches one object; `session.merge(obj)` copies state from a
detached object onto the persistent one.

---

## 2.4 Relationships

### One-to-many / many-to-one

The model above shows the canonical pair: `User.addresses` (one-to-many, a list) and
`Address.user` (many-to-one, scalar), linked by `back_populates` so both sides stay in
sync in Python before flushing:

```python
u = User(name="squidward")
a = Address(email_address="squid@krusty.com")
u.addresses.append(a)
assert a.user is u          # back_populates kept the other side in sync
```

> **🆕 2.1:** `back_populates` accepts a direct attribute or a lambda for IDE-friendly
> linking: `relationship(back_populates=lambda: Address.user)`.

The foreign key column on the "many" side (`Address.user_id`) is what the relationship
uses. If there are multiple FKs between two tables, disambiguate with
`relationship(foreign_keys=[Address.billing_user_id])`.

### One-to-one

A one-to-many where the collection side is a scalar:

```python
class Profile(Base):
    __tablename__ = "profile"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user_account.id"), unique=True)
    user: Mapped["User"] = relationship(back_populates="profile")

# on User:
#   profile: Mapped[Optional["Profile"]] = relationship(back_populates="user")
```

A non-list `Mapped[...]` annotation sets `uselist=False` automatically.

### Many-to-many

Use an **association table** (a Core `Table`, no class) via `secondary=`:

```python
from sqlalchemy import Table, Column

post_tag = Table(
    "post_tag",
    Base.metadata,
    Column("post_id", ForeignKey("post.id"), primary_key=True),
    Column("tag_id", ForeignKey("tag.id"), primary_key=True),
)

class Post(Base):
    __tablename__ = "post"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    tags: Mapped[list["Tag"]] = relationship(secondary=post_tag, back_populates="posts")

class Tag(Base):
    __tablename__ = "tag"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    posts: Mapped[list["Post"]] = relationship(secondary=post_tag, back_populates="tags")
```

If the link itself has data (a role, a timestamp), use the **association object**
pattern: make the link a mapped class with two many-to-one relationships. The
`association_proxy` extension can then give you a convenient `post.tag_names` view.

### Cascades

`cascade` controls which Session operations propagate from parent to children:

| Setting | Effect |
|---------|--------|
| `"save-update, merge"` | **Default.** Adding the parent adds its children. |
| `"all"` | save-update, merge, refresh-expire, expunge, delete |
| `"all, delete-orphan"` | Plus: removing a child from the collection deletes it. Use for owned children. |

For large child collections, also consider letting the **database** do deletes:

```python
addresses: Mapped[list["Address"]] = relationship(
    back_populates="user",
    cascade="all, delete-orphan",
    passive_deletes=True,   # trust ON DELETE CASCADE instead of loading children
)
# and on Address.user_id: ForeignKey("user_account.id", ondelete="CASCADE")
```

### Collection types

`Mapped[list[X]]` is the default. You can use `Mapped[set[X]]`, or dictionary
collections with `attribute_keyed_dict`:

```python
from sqlalchemy.orm import attribute_keyed_dict

notes: Mapped[dict[str, "Note"]] = relationship(
    collection_class=attribute_keyed_dict("keyword")
)
```

---

## 2.5 Mapped dataclasses

Add `MappedAsDataclass` and your models get a generated `__init__`, `__repr__` and
`__eq__` that type checkers understand:

```python
from sqlalchemy.orm import MappedAsDataclass, DeclarativeBase

class Base(MappedAsDataclass, DeclarativeBase):
    pass

class Customer(Base):
    __tablename__ = "customer"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)   # not in __init__
    name: Mapped[str]
    status: Mapped[str] = mapped_column(default="active")
    orders: Mapped[list["Order"]] = relationship(
        default_factory=list, back_populates="customer"
    )

c = Customer(name="Ada")          # status="active" via default
```

Rules: fields without defaults must come before fields with defaults (normal dataclass
ordering); use `init=False` for DB-generated fields; use `kw_only=True` on the base to
avoid ordering headaches.

> **🆕 2.1 behaviour change:** Dataclass defaults are no longer written into the
> instance `__dict__`. They're delivered by the attribute descriptor and applied as the
> column default on INSERT. This fixes the 2.0 gotcha where `Parent(related_id=5)` would
> also set `related=None` and silently INSERT `NULL`. Related rules:
> `relationship(default=...)` only accepts `None` and only on many-to-one;
> `mapped_column(default=...)` and `insert_default=...` are mutually exclusive.

---

## 2.6 Hybrid properties and column properties

**Hybrid properties** work both on instances (Python) and in queries (SQL):

```python
from sqlalchemy.ext.hybrid import hybrid_property

class Person(Base):
    __tablename__ = "person"
    id: Mapped[int] = mapped_column(primary_key=True)
    first: Mapped[str]
    last: Mapped[str]

    @hybrid_property
    def full_name(self) -> str:
        return f"{self.first} {self.last}"

    @full_name.inplace.expression
    @classmethod
    def _full_name_expr(cls):
        return cls.first + " " + cls.last

# Python: person.full_name
# SQL:    select(Person).where(Person.full_name == "Ada Lovelace")
```

**`column_property`** maps a SQL expression (even a correlated subquery) as a
read-only attribute loaded with the object:

```python
from sqlalchemy.orm import column_property

# Book (with an author_id FK) must already be defined, because the
# expression below references Book.id directly at class-creation time.
class Author(Base):
    __tablename__ = "author"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    book_count: Mapped[int] = column_property(
        select(func.count(Book.id)).where(Book.author_id == id).scalar_subquery(),
        deferred=True,      # only load when accessed (see Chapter 4)
    )
```

---

## 2.7 Validation and events on models

```python
from sqlalchemy.orm import validates

class Account(Base):
    __tablename__ = "account"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str]

    @validates("email")
    def _check_email(self, key, value):
        if "@" not in value:
            raise ValueError("invalid email")
        return value.lower()
```

Mapper events (`before_insert`, `before_update`, `after_delete`...) and session events
(`before_flush`, `after_commit`) are covered in
[Chapter 5](05-engine-pooling-transactions.md#55-events).

---

## 2.8 Recap

- Inherit from `DeclarativeBase`; declare columns with `Mapped[...]` + `mapped_column()`.
- Use a `sessionmaker` factory; scope sessions with `with ... .begin()`.
- Understand object states and expiration — most beginner errors
  (`DetachedInstanceError`) come from using objects after their session closed.
- `relationship()` + `back_populates` for links; choose cascades deliberately.

Next: [Chapter 3](03-querying.md) goes deep on writing queries.
