
# General Rule for Pydantic
**For Boundary Crossings, NOT for bulk processing**

Pydantic is built to check that each individual record is well-formed as it crosses a boundary: an API request, a message from a queue, a config file, a response from another service. Bulk pipelines and analysis work on whole sets of data at once, and creating one Pydantic object per row costs time and memory without telling you much that set-level checks can't.

The same goes for the ORM. Loading 5 million rows as `Order` objects and changing them one at a time is far slower than one set-based statement. In bulk work you usually skip both layers:

```python
# Instead of loading rows and mutating them in a loop:
session.execute(
    update(Order)
    .where(Order.status == "pending", Order.created_at < cutoff)
    .values(status="cancelled")
)

# Bulk insert with Core: plain dicts, no ORM objects, no Pydantic
session.execute(insert(Order), list_of_dicts)
```

For analysis, the tools are SQL itself, pandas, polars, or DuckDB, which operate on whole columns rather than individual objects.

**Where Pydantic still helps in pipelines**

The rule isn't "never in bulk work". It's "use it at the edges", and a pipeline has edges too.

- **Ingesting external data.** Pulling records from a vendor API, CSV drops, or JSON files is a boundary, and bad records are common there. Validating each one at intake, and routing failures to a quarantine table instead of crashing the job, is a good use of Pydantic. Pydantic v2's validation core is written in Rust, so this is often fast enough for thousands to low millions of records. `TypeAdapter(list[RecordIn]).validate_json(raw_bytes)` validates a whole payload in one call.
- **Pipeline configuration.** Job parameters, connection settings, and run options benefit from Pydantic, and `pydantic-settings` exists for exactly this.
- **Output contracts.** If the pipeline publishes summary records to another system, a schema for that output documents and enforces the contract.

**For in-pipeline data quality, use column-level tools**

When the data is already in a DataFrame or table, check it as a whole rather than row by row:

- **Database constraints** (`NOT NULL`, `CHECK`, foreign keys) are still your last line of defense, even for bulk loads.
- **Pandera** declares a schema for pandas or polars DataFrames and checks it on whole columns at once.
- **Polars and Arrow schemas** enforce types when you load the data.
- **Plain SQL checks**, such as `SELECT count(*) WHERE total_amount < 0`, run as a step in the pipeline.

**Rough guide**

| Situation | Tool |
|---|---|
| One request, message, or record in or out | Pydantic + ORM row |
| Multi-step change to a few related rows | ORM row inside one transaction |
| Ingesting messy external records | Pydantic per record, quarantine failures |
| Changing many rows by the same rule | Set-based SQL (`update`/`insert` in Core) |
| Analysis and aggregation | SQL, pandas/polars, DuckDB |
| Data quality on a whole table or frame | DB constraints, Pandera, SQL checks |

So your instinct is right. Pydantic and ORM rows are for working with individual records, and bulk work is better done with tools that operate on whole sets.

# For Use Alongside SQL Alchemy
Keep them separate. Your instinct is right: validate with Pydantic, then apply the validated values to the SQLAlchemy row and let the session persist it. That is the standard pattern.

DO NOT: Go from SQL Alchemy Row => Pydantic Object => Alter the data in the Pydantic Object => Update/Merge to SQL Alchemy Object (Just update in the SQL Alchemy Row)

**Why keep them separate**

The two do different jobs:

- **Pydantic models** sit at the edges of your app. They validate input from the outside world (API requests, files, user input) and shape output going back out.
- **SQLAlchemy rows** are persistence objects. They're tied to a session, track changes, lazy-load relationships, and map to your table.

Merging them into one class (which is roughly what SQLModel does) works for simple CRUD. It gets awkward once the API shape and the table shape start to differ. Common cases are hidden columns like `password_hash`, computed fields, different fields for create versus update, and nested responses.

**The typical flow**

```python
from pydantic import BaseModel, ConfigDict

# --- Schemas (edges) ---
class UserCreate(BaseModel):
    email: str
    name: str

class UserUpdate(BaseModel):
    email: str | None = None
    name: str | None = None

class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: str
    name: str

# --- Service layer ---
def create_user(session, data: UserCreate) -> UserRead:
    user = User(**data.model_dump())          # ORM row
    session.add(user)
    session.commit()
    session.refresh(user)
    return UserRead.model_validate(user)      # row -> schema on the way out

def update_user(session, user_id: int, data: UserUpdate) -> UserRead:
    user = session.get(User, user_id)
    if user is None:
        raise NotFound()
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(user, field, value)           # edit the row in place
    session.commit()
    session.refresh(user)
    return UserRead.model_validate(user)
```

**Things that matter in practice**

- **Use `exclude_unset=True` for updates.** It distinguishes "field not sent" from "field explicitly set to null," which is what PATCH semantics need.
- **Let the schema be the whitelist.** Only fields defined on `UserUpdate` can reach `setattr`, so a client can't sneak in `is_admin=True`. Don't do `setattr` from a raw dict.
- **Convert to a Read schema before leaving the session.** Returning raw ORM rows past the session scope invites `DetachedInstanceError` and surprise lazy-load queries during serialization.
- **Keep data-integrity rules in the database too.** Pydantic checks shape and format, but uniqueness, foreign keys, and NOT NULL belong in DB constraints, because Pydantic can't see other rows or concurrent writes. SQLAlchemy's `@validates` is useful for invariants that should hold no matter where a write comes from.
- **Put the "apply schema to row" logic in one place**, such as a service or repository function, not scattered across route handlers.

The one pattern to avoid is the reverse: building a Pydantic object, then constructing a fresh ORM object from it for an update and `merge()`-ing it in. That loses change tracking and can overwrite columns you didn't mean to touch. Loading the existing row and mutating it, as you described, is the cleaner approach.
