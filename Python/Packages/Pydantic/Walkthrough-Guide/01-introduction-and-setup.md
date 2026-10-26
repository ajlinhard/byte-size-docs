# 01 — Introduction and Setup

> **Level:** Beginner · **Pydantic version covered:** 2.14.x (latest stable as of October 2026) · **Python:** 3.10+

## What Pydantic is

Pydantic is a **data validation and serialization library driven by Python type hints**. You describe the *shape* of your data using ordinary annotations (`int`, `str`, `list[float]`, `datetime | None` …) and Pydantic guarantees that, after construction, an object actually has that shape — or it raises a detailed error explaining exactly what is wrong.

It solves three problems at once:

| Problem | What Pydantic does |
|---|---|
| **Parsing / coercion** | Turns messy external input (JSON, form data, env vars, DB rows) into proper Python objects. `"42"` becomes `42`, `"2026-10-15"` becomes a `date`. |
| **Validation** | Enforces constraints (types, ranges, lengths, regexes, custom rules) and reports *all* errors at once with precise locations. |
| **Serialization** | Converts objects back to `dict` / JSON, with control over aliases, excluded fields, formats, and more. It can also emit **JSON Schema**. |

Because the rules live in type hints, the same declaration also gives you IDE autocomplete and static type-checking (mypy, pyright, pyrefly) for free.

### Why it is so widely used

- **Speed.** The validation engine, `pydantic-core`, is written in Rust. Since v2 it is typically 5–50× faster than v1.
- **Ecosystem.** FastAPI, SQLModel, Litestar, Django Ninja, LangChain, Pydantic AI, the OpenAI / Anthropic SDKs, Prefect, Beanie, and thousands more are built on it.
- **One mental model.** Validation, serialization, settings, CLI parsing, LLM structured output and API docs all reuse the same model definitions.

### "Parse, don't validate"

A useful way to think about Pydantic: it doesn't merely *check* data, it *transforms* untrusted input into trusted, typed objects at the boundary of your system. Inside your application you then work only with validated objects and never re-check them.

```
untrusted world          boundary                 your code
───────────────   ─────────────────────   ──────────────────────
JSON / env / DB  ──►  Model.model_validate  ──►  typed, valid objects
                    (raises ValidationError
                     on bad input)
```

## Installation

```bash
pip install -U pydantic
# or, with uv
uv add pydantic
```

Optional extras:

```bash
pip install "pydantic[email]"      # EmailStr / NameEmail (installs email-validator)
pip install "pydantic[timezone]"   # tzdata for ZoneInfo on Windows
pip install pydantic-settings      # BaseSettings: env vars, .env, secrets, CLI
pip install pydantic-extra-types   # Color, Country, PhoneNumber, ULID, ...
```

Check what you have:

```python
import pydantic
from pydantic.version import version_info

print(pydantic.VERSION)   # e.g. 2.14.1
print(version_info())     # full report: pydantic-core version, Python, OS, related packages
```

### Version notes (as of October 2026)

- **Pydantic 2.14** (Oct 8, 2026; 2.14.1 on Oct 11) is the current release. It **drops Python 3.9** and adds Python 3.15 support (lazy imports, `TypeForm`, `frozendict`), and **stabilizes the `MISSING` sentinel**.
- **Pydantic 2.13** (Apr 2026) added polymorphic serialization, `exclude_if` on computed fields, and `ascii_only` string constraints. The `pydantic-core` source moved into the main `pydantic` repository (it is still published as a separate package).
- **Pydantic V1** lives on only as `pydantic.v1` for migration purposes and is **not supported on Python 3.14+**. FastAPI ≥ 0.128 requires Pydantic v2. New code should never use V1.
- Pydantic follows semantic-ish versioning: minor releases may contain small, documented behavior changes — always read the release notes before upgrading (see [16 — Migration and What's New](16-migration-and-whats-new.md)).

## Your first model

```python
from datetime import datetime
from pydantic import BaseModel


class User(BaseModel):
    id: int
    name: str = "Jane Doe"          # default value → field is optional
    signup_ts: datetime | None = None
    friends: list[int] = []         # mutable defaults are safe in Pydantic (copied per instance)


external_data = {
    "id": "123",                    # string → coerced to int
    "signup_ts": "2026-06-01 12:22",  # string → datetime
    "friends": [1, "2", b"3"],      # mixed → list[int]
}

user = User(**external_data)
print(user)
#> id=123 name='Jane Doe' signup_ts=datetime.datetime(2026, 6, 1, 12, 22) friends=[1, 2, 3]
print(user.id, type(user.id))
#> 123 <class 'int'>
print(user.model_dump())
#> {'id': 123, 'name': 'Jane Doe', 'signup_ts': datetime.datetime(2026, 6, 1, 12, 22), 'friends': [1, 2, 3]}
```

Things to notice:

1. You subclass `BaseModel` and annotate class attributes. Each annotation becomes a **field**.
2. A field with no default is **required**; a field with a default is **optional**.
3. Input is **coerced** where it is safe and unambiguous (`"123"` → `123`). This is called *lax mode*; you can switch to *strict mode* to forbid coercion (see [06 — Configuration and Strict Mode](06-configuration-and-strict-mode.md)).
4. Unlike plain Python, a mutable default like `[]` is **not shared** between instances — Pydantic deep-copies non-hashable defaults.

## When validation fails

```python
from pydantic import BaseModel, ValidationError


class User(BaseModel):
    id: int
    name: str
    age: int


try:
    User(id="not a number", age=-1.5)
except ValidationError as e:
    print(e.error_count())
    #> 3
    print(e)
```

Output:

```text
3 validation errors for User
id
  Input should be a valid integer, unable to parse string as an integer [type=int_parsing, input_value='not a number', input_type=str]
name
  Field required [type=missing, input_value={'id': 'not a number', 'age': -1.5}, input_type=dict]
age
  Input should be a valid integer, got a number with a fractional part [type=int_from_float, input_value=-1.5, input_type=float]
```

Key properties of `ValidationError`:

- **All** errors are collected, not just the first.
- Each error has a `loc` (location path), `type` (a stable machine-readable code), `msg`, and `input`.
- `e.errors()` returns a list of dicts; `e.json()` returns JSON — ideal for API responses.

```python
from pydantic import BaseModel, ValidationError


class Item(BaseModel):
    price: float


class Order(BaseModel):
    items: list[Item]


try:
    Order(items=[{"price": 1}, {"price": "free"}])
except ValidationError as e:
    err = e.errors()[0]
    print(err["loc"], err["type"])
    #> ('items', 1, 'price') float_parsing
```

The `loc` tuple `('items', 1, 'price')` pinpoints the exact nested position — the second item's `price`.

## Pydantic vs. the alternatives

| Tool | Validation at runtime | Coercion | JSON Schema | Speed | Typical use |
|---|---|---|---|---|---|
| `dataclasses` (stdlib) | ❌ | ❌ | ❌ | fastest construction | internal data containers |
| `attrs` + `cattrs` | opt-in validators | via cattrs | ❌ (3rd-party) | fast | internal domain objects |
| `msgspec` | ✅ (strict-ish) | limited | ✅ | very fast | high-throughput (de)serialization |
| **Pydantic** | ✅ rich | ✅ lax or strict | ✅ first-class | fast (Rust core) | boundaries: APIs, config, files, LLMs |
| `marshmallow` | ✅ (schema objects) | ✅ | via plugin | slower | legacy Flask apps |

**Rule of thumb:** use Pydantic at the **edges** of your system where untrusted data enters or leaves. Inside the core, lightweight dataclasses or plain objects are often enough (we revisit this in [12 — Architecture Patterns and Performance](12-architecture-patterns-and-performance.md)).

## The core API at a glance

Everything Pydantic offers on a model starts with the `model_` prefix (so it never collides with your field names):

| Method / attribute | Purpose |
|---|---|
| `Model(**kwargs)` | Validate keyword arguments and construct |
| `Model.model_validate(obj)` | Validate a dict / object |
| `Model.model_validate_json(str_or_bytes)` | Parse + validate JSON in one fast step (Rust) |
| `Model.model_validate_strings(obj)` | Validate a dict of strings (e.g. form/query data) |
| `m.model_dump()` / `m.model_dump_json()` | Serialize to dict / JSON string |
| `Model.model_json_schema()` | Produce JSON Schema |
| `m.model_copy(update=...)` | Copy with optional changes |
| `Model.model_construct(**kwargs)` | Build **without** validation (trusted data only) |
| `Model.model_fields` / `m.model_fields_set` | Field metadata / which fields were explicitly set |
| `Model.model_rebuild()` | Resolve forward references later |

## What's next

The rest of this guide builds up progressively:

- **02–05 (Beginner):** models, fields & types, validators, serialization
- **06–10 (Intermediate → Advanced):** configuration & strict mode, unions/generics/recursive models, `TypeAdapter`/dataclasses/`@validate_call`, JSON Schema, custom types
- **11–12 (Advanced):** internal architecture of Pydantic (`pydantic-core`, core schemas) and architecture patterns + performance
- **13–16 (Integrations & migration):** `pydantic-settings`, FastAPI / SQLAlchemy / SQLModel / Django / Litestar, Pydantic AI & LLMs, tooling, migration

Continue with **[02 — Models](02-models.md)**.
