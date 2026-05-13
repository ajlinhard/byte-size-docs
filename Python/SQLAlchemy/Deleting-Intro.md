# A Beginner's Guide to Deleting Records in SQLAlchemy

SQLAlchemy gives you several ways to delete data from your database. This guide walks through all of them — from deleting a single object to bulk-deleting thousands of rows — with clear examples and explanations of when to use each approach.

---

## Prerequisites

This guide assumes you have a basic SQLAlchemy setup. Here's the example model used throughout:

```python
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.orm import DeclarativeBase, Session

engine = create_engine("sqlite:///example.db")

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id       = Column(Integer, primary_key=True)
    name     = Column(String)
    email    = Column(String)
    active   = Column(Boolean, default=True)
    age      = Column(Integer)
```

---

## 1. Deleting a Single Object (ORM-style)

The most straightforward way to delete a record is to fetch it first, then delete it through the Session.

```python
with Session(engine) as session:
    # Step 1: Fetch the object
    user = session.get(User, 42)  # get by primary key

    # Step 2: Mark it for deletion
    session.delete(user)

    # Step 3: Commit to apply the change
    session.commit()
```

**What happens under the hood:**
1. `session.get()` issues a `SELECT` to load the object into the session.
2. `session.delete(user)` marks it as "pending deletion" in memory.
3. `session.commit()` flushes the pending `DELETE` to the database.

> **Tip:** Always check that the object exists before deleting. If `session.get()` returns `None` and you try to delete it, you'll get an error.

```python
user = session.get(User, 42)
if user is None:
    print("User not found")
else:
    session.delete(user)
    session.commit()
```

---

## 2. Deleting After a Query

If you don't know the primary key, you can query for the object first:

```python
with Session(engine) as session:
    user = session.query(User).filter(User.email == "alice@example.com").first()

    if user:
        session.delete(user)
        session.commit()
```

Or using the newer **2.0-style** `select()`:

```python
from sqlalchemy import select

with Session(engine) as session:
    stmt = select(User).where(User.email == "alice@example.com")
    user = session.scalars(stmt).first()

    if user:
        session.delete(user)
        session.commit()
```

---

## 3. Bulk Deletes (Many Rows at Once)

Fetching objects one by one is slow when you need to delete many rows. SQLAlchemy provides two ways to issue a single `DELETE` statement for multiple rows.

### 3a. Legacy-style: `Query.delete()`

```python
with Session(engine) as session:
    deleted_count = (
        session.query(User)
        .filter(User.active == False)
        .delete(synchronize_session="fetch")
    )
    session.commit()
    print(f"Deleted {deleted_count} users")
```

### 3b. Modern-style (SQLAlchemy 2.0+): `delete()` statement

```python
from sqlalchemy import delete

with Session(engine) as session:
    stmt = delete(User).where(User.active == False)
    result = session.execute(stmt)
    session.commit()
    print(f"Deleted {result.rowcount} users")
```

> **Prefer the 2.0 style** for new projects. It's more explicit and aligns with SQLAlchemy's current direction.

---

## 4. Understanding `synchronize_session`

When you run a bulk delete, SQLAlchemy needs to decide what to do with any matching objects already loaded in the session's memory (its "identity map"). The `synchronize_session` parameter controls this.

| Value | What it does | Use when |
|---|---|---|
| `'evaluate'` | *(default)* Evaluates the WHERE clause in Python to remove matching in-memory objects. No extra query. | Simple WHERE clauses (equality checks, basic comparisons) |
| `'fetch'` | Runs a SELECT first to find affected rows, then removes them from memory. | Complex WHERE clauses, subqueries, or when `'evaluate'` raises an error |
| `False` | Does nothing to in-memory objects — leaves them stale. | You don't use those objects afterward, or you call `session.expire_all()` |

```python
# 'evaluate' (default) — no extra query, works for simple filters
session.query(User).filter(User.active == False).delete(synchronize_session="evaluate")

# 'fetch' — issues a SELECT first, safe for complex conditions
session.query(User).filter(User.age < 18).delete(synchronize_session="fetch")

# False — fastest, but leaves session state stale
session.query(User).filter(User.active == False).delete(synchronize_session=False)
session.expire_all()  # manually expire in-memory objects to avoid stale reads
```

---

## 5. Deleting All Rows in a Table

To wipe all records from a table:

```python
from sqlalchemy import delete

with Session(engine) as session:
    session.execute(delete(User))
    session.commit()
```

> **Warning:** This deletes every row with no undo. Double-check your filters before committing!

If you want to truncate the table at the SQL level (faster, resets auto-increment counters), you can use raw SQL:

```python
from sqlalchemy import text

with Session(engine) as session:
    session.execute(text("DELETE FROM users"))
    session.commit()
```

---

## 6. Cascading Deletes

If your model has relationships, you'll often want related records to be deleted automatically. There are two ways to set this up.

### Option A: ORM-level cascade (handled by SQLAlchemy)

```python
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"
    id    = Column(Integer, primary_key=True)
    name  = Column(String)
    posts = relationship("Post", cascade="all, delete-orphan")

class Post(Base):
    __tablename__ = "posts"
    id      = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title   = Column(String)
```

Now deleting a `User` automatically deletes their `Post` records too:

```python
with Session(engine) as session:
    user = session.get(User, 1)
    session.delete(user)  # also deletes all user.posts
    session.commit()
```

### Option B: Database-level cascade (handled by your DB)

```python
from sqlalchemy import ForeignKey

class Post(Base):
    __tablename__ = "posts"
    id      = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    title   = Column(String)
```

> **Tip:** Use database-level cascade for performance with bulk deletes, and ORM-level cascade when you need SQLAlchemy to fire hooks or events on deletion.

---

## 7. Soft Deletes (Not Actually Deleting)

Many applications don't permanently delete data. Instead, they mark records as deleted with a flag. This is called a **soft delete**.

```python
from sqlalchemy import DateTime
from datetime import datetime, timezone

class User(Base):
    __tablename__ = "users"
    id         = Column(Integer, primary_key=True)
    name       = Column(String)
    deleted_at = Column(DateTime, nullable=True)

# "Delete" a user (soft)
with Session(engine) as session:
    user = session.get(User, 1)
    user.deleted_at = datetime.now(timezone.utc)
    session.commit()

# Query only active (non-deleted) users
with Session(engine) as session:
    active_users = (
        session.query(User)
        .filter(User.deleted_at == None)
        .all()
    )
```

---

## 8. Rolling Back a Delete

If something goes wrong, you can roll back a delete before committing:

```python
with Session(engine) as session:
    try:
        user = session.get(User, 42)
        session.delete(user)
        # ... something fails here ...
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"Delete failed, rolled back: {e}")
```

Using the `Session` as a context manager (`with Session(...) as session`) will automatically roll back on an unhandled exception.

---

## Quick Reference

| Goal | Code |
|---|---|
| Delete one object | `session.delete(obj)` |
| Bulk delete (2.0 style) | `session.execute(delete(Model).where(...))` |
| Bulk delete (legacy style) | `session.query(Model).filter(...).delete()` |
| Delete all rows | `session.execute(delete(Model))` |
| Cascade delete children | `cascade="all, delete-orphan"` on relationship |
| Soft delete | Set a `deleted_at` timestamp column |
| Roll back | `session.rollback()` |

---

## Common Pitfalls

- **Forgetting to `commit()`** — your delete won't persist to the database until you call `session.commit()`.
- **Deleting a `None` object** — always check that your query returned a result before calling `session.delete()`.
- **Stale in-memory objects** — after a bulk delete with `synchronize_session=False`, objects already in the session may appear to still exist. Call `session.expire_all()` to force a fresh load on next access.
- **Missing cascade config** — deleting a parent without cascade set up will raise a foreign key constraint error if children exist.

## Deleting Effectively with `synchronize_session='fetch'` in SQLAlchemy

When you call `.delete()` on a query in SQLAlchemy, the `synchronize_session` parameter controls **how SQLAlchemy keeps the current Session's in-memory objects in sync** after the DELETE is executed in the database.

### The problem it solves

SQLAlchemy's Session acts as an **identity map** — it caches ORM objects in memory. If you run a bulk DELETE directly on the database, those in-memory objects don't automatically know they've been deleted. `synchronize_session` tells SQLAlchemy what to do about that.

---

### The three options

| Value | Behavior |
|---|---|
| `'fetch'` | Issues a **SELECT first** to find which rows will be deleted, then expires/removes those objects from the session |
| `'evaluate'` | **(default)** Tries to **evaluate the WHERE clause in Python** against in-memory objects and removes matches — no extra query, but can fail for complex conditions |
| `False` | **Does nothing** — in-memory objects are left stale. Safe only if you don't use those objects afterward |

---

### What `'fetch'` does step by step

```python
session.query(User).filter(User.active == False).delete(synchronize_session='fetch')
```

1. SQLAlchemy runs a **SELECT** to fetch the primary keys of all matching rows
2. It removes those objects from the Session's identity map
3. It runs the actual **DELETE** statement

---

### When to use `'fetch'`

Use `'fetch'` when:
- Your WHERE clause is **too complex** for `'evaluate'` to handle (e.g., subqueries, joins, DB functions)
- You need the session to be **accurately updated** and can tolerate an extra query
- You're seeing errors like `Could not evaluate ... in Python` with the default `'evaluate'`

Avoid it when deleting **huge numbers of rows**, since the pre-fetch SELECT can be expensive. In that case, `False` is fine if you immediately discard or expire the session afterward (e.g., `session.expire_all()`).
