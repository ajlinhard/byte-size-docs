# Setting Up Alembic with SQLAlchemy for PostgreSQL

Alembic is a database migration tool for SQLAlchemy. Think of it like "version control for your database schema" — every time you change your tables, Alembic tracks it so your schema stays in sync across environments and teammates.

---

## 1. Install Dependencies

```bash
pip install alembic sqlalchemy psycopg2-binary
```

---

## 2. Initialize Alembic

Run this in the root of your project:

```bash
alembic init alembic
```

This creates the following structure:

```
your-project/
├── alembic/
│   ├── env.py           ← The brain — connects Alembic to your DB & models
│   ├── script.py.mako   ← Template for new migration files
│   └── versions/        ← Your migration history lives here
├── alembic.ini          ← Main config file
```

---

## 3. Set Up Multi-Environment Support

Instead of hardcoding a single database URL in `alembic.ini`, you'll use environment variables so the same code points to dev, test, or prod depending on context.

**`alembic.ini`** — remove or comment out the default `sqlalchemy.url` line:

```ini
[alembic]
script_location = alembic
# sqlalchemy.url is intentionally omitted — set via environment variable
```

**Create a `.env`-style config or use shell exports.** A clean pattern is to have separate `.env` files:

```
.env.dev   → DATABASE_URL=postgresql://user:pass@localhost:5432/myapp_dev
.env.test  → DATABASE_URL=postgresql://user:pass@localhost:5432/myapp_test
.env.prod  → DATABASE_URL=postgresql://user:pass@prod-host:5432/myapp_prod
```

---

## 4. Configure `env.py`

This is the most important file. Edit `alembic/env.py` to:
1. Read the DB URL from an environment variable
2. Import your SQLAlchemy models so Alembic can detect schema changes automatically

```python
import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# ── Import your models' Base here ──────────────────────────────────────────
from app.models import Base  # adjust this import to match your project structure

# Alembic config object
config = context.config

# Set up Python logging from alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Point Alembic at your models for autogenerate support
target_metadata = Base.metadata

# ── Read DB URL from environment variable ───────────────────────────────────
def get_url():
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise ValueError("DATABASE_URL environment variable is not set!")
    return url


def run_migrations_offline() -> None:
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_url()

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

---

## 5. Define Your Models

Here's a simple example so Alembic has something to detect:

```python
# app/models.py
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, nullable=False, unique=True)
    name = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
```

---

## 6. Create Your First Migration

```bash
# Point to your dev database
export DATABASE_URL="postgresql://user:pass@localhost:5432/myapp_dev"

# Auto-generate a migration by comparing your models to the DB
alembic revision --autogenerate -m "create users table"
```

This creates a file in `alembic/versions/` that looks like:

```python
def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )

def downgrade() -> None:
    op.drop_table('users')
```

> **Always review the generated file before running it.** Autogenerate is smart but not perfect — it can miss things like indexes or server defaults.

---

## 7. Run Migrations Per Environment

```bash
# Dev
export DATABASE_URL="postgresql://user:pass@localhost:5432/myapp_dev"
alembic upgrade head

# Test
export DATABASE_URL="postgresql://user:pass@localhost:5432/myapp_test"
alembic upgrade head

# Prod
export DATABASE_URL="postgresql://user:pass@prod-host:5432/myapp_prod"
alembic upgrade head
```

You can also wrap this in a Makefile or script:

```makefile
migrate-dev:
    DATABASE_URL=postgresql://user:pass@localhost:5432/myapp_dev alembic upgrade head

migrate-prod:
    DATABASE_URL=postgresql://user:pass@prod-host:5432/myapp_prod alembic upgrade head
```

---

## Essential Commands Cheat Sheet

| Command | What it does |
|---|---|
| `alembic revision --autogenerate -m "msg"` | Generate a migration from model changes |
| `alembic upgrade head` | Apply all pending migrations |
| `alembic downgrade -1` | Roll back the last migration |
| `alembic history` | See all migration history |
| `alembic current` | See which migration your DB is on |
| `alembic show <rev_id>` | Inspect a specific migration |

---

## Key Things to Remember

- **Never edit a migration after it's been applied** to a shared environment. Create a new one instead.
- **Always commit your `versions/` folder** to git — it's your schema history.
- **`--autogenerate` doesn't catch everything** — things like `CHECK` constraints or partial indexes often need to be written manually.
- Add `.env.*` files to `.gitignore` so you never accidentally commit credentials.
