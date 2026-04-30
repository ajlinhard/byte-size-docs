# Breaking Down `env.py` — Online vs Offline

---

## The Top Section (Shared Setup)

```python
import os
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
```
Just imports. `context` is Alembic's global object that knows everything about the current migration run — what mode it's in, what the target DB is, etc.

```python
from app.models import Base
```
This is how Alembic knows what your schema *should* look like. `Base.metadata` holds a map of all your SQLAlchemy model classes and their columns. Without this, `--autogenerate` has nothing to compare against.

```python
config = context.config
```
This reads `alembic.ini`. Think of it as loading your settings file into a Python object.

```python
if config.config_file_name is not None:
    fileConfig(config.config_file_name)
```
Wires up Python's standard logging using the log settings defined in `alembic.ini`. This is what makes Alembic print messages like `Running upgrade abc123 -> def456` to your terminal.

```python
target_metadata = Base.metadata
```
Hands Alembic your models' schema so it can diff them against the real database during `--autogenerate`.

```python
def get_url():
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise ValueError("DATABASE_URL environment variable is not set!")
    return url
```
Reads the database URL from your environment. Fails loudly if it's missing rather than silently connecting to the wrong place.

---

## The Core Difference: Online vs Offline

The simplest way to think about it:

| | Offline | Online |
|---|---|---|
| **Connects to DB?** | ❌ No | ✅ Yes |
| **Output** | SQL text to stdout/file | Executes directly on DB |
| **Use case** | DBA review, auditing, air-gapped prod | Normal day-to-day usage |
| **How to trigger** | `alembic upgrade head --sql` | `alembic upgrade head` |

---

## Offline Mode

```python
def run_migrations_offline() -> None:
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,            # renders actual values instead of :param placeholders
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()
```

**Offline mode does NOT open a real database connection.** Instead of executing SQL, it *generates* the SQL and prints it out (or writes it to a file). The URL is only needed so Alembic knows which SQL dialect to use (PostgreSQL syntax vs MySQL syntax, etc.).

You trigger it with the `--sql` flag:
```bash
alembic upgrade head --sql > migration.sql
```

That `migration.sql` file will contain something like:
```sql
BEGIN;
CREATE TABLE users (
    id SERIAL NOT NULL,
    email VARCHAR NOT NULL,
    PRIMARY KEY (id)
);
UPDATE alembic_version SET version_num='abc123def456';
COMMIT;
```

**When would you use this?**
- Your DBA needs to review and approve SQL before it touches prod
- You're in a regulated environment where no automated tool can directly touch the database
- You want to inspect exactly what Alembic is going to do before it does it

---

## Online Mode

```python
def run_migrations_online() -> None:
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_url()   # inject the URL at runtime

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,    # don't reuse connections — migrations are one-shot
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()
```

**Online mode opens a real connection and executes the SQL directly against your database.** This is what you use the vast majority of the time.

A few things worth noting:
- `pool.NullPool` means every migration gets a fresh connection and it's closed immediately after. This is intentional — migrations aren't like normal app queries that benefit from connection pooling.
- The whole migration runs inside a single transaction (`begin_transaction`). If anything fails midway, the entire migration rolls back and your DB stays in its previous state.

You trigger it with the normal command (no `--sql` flag):
```bash
alembic upgrade head
```

---

## The Decision at the Bottom

```python
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

This is just the entry point. Alembic sets `is_offline_mode()` to `True` automatically when you pass `--sql`. You never change this line — it's a router that calls the right function based on how you invoked the command.

---

## Summary

In 99% of cases you're using **online mode** — just run `alembic upgrade head` and it connects and executes. **Offline mode** is a specialized tool for when you need a human or a separate process to review and run the SQL manually, which is common in enterprise or regulated environments.
