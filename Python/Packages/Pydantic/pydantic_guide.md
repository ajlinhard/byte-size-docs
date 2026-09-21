# The Complete Pydantic Guide: Beginner to Advanced

> Covers **Pydantic v2** (the current major version). Notes on v1 differences are called out where they matter. All examples are tested against Pydantic `2.13`.

## Table of Contents

1. [Introduction & Setup](#1-introduction--setup)
2. [Beginner: Core Concepts](#2-beginner-core-concepts)
3. [Intermediate: Validation & Configuration](#3-intermediate-validation--configuration)
4. [Advanced: Type System & Internals](#4-advanced-type-system--internals)
5. [Settings Management](#5-settings-management-pydantic-settings)
6. [Common Use Cases](#6-common-use-cases)
7. [Complex / Advanced Use Cases](#7-complex--advanced-use-cases)
8. [Cheat Sheet](#8-cheat-sheet)
9. [Common Pitfalls](#9-common-pitfalls)
10. [Further Resources](#10-further-resources)

---

## 1. Introduction & Setup

**Pydantic** is a data validation and settings-management library that uses Python type hints to define schemas. You describe the *shape* of your data as a class, and Pydantic validates, coerces, and serializes data against that shape at runtime — something plain type hints don't do on their own.

Core value proposition:
- Turns type hints into runtime validators
- Coerces compatible types automatically (e.g. `"123"` → `123`) or rejects them in strict mode
- Generates JSON Schema automatically
- Produces clear, structured error messages
- Powers FastAPI, and is used heavily in data pipelines, config management, and LLM tool-calling schemas

### Installation

```bash
pip install pydantic
# For settings/env-var management:
pip install pydantic-settings
```

### v1 vs v2 — why it matters

Pydantic v2 (2023+) was a near-total rewrite with a Rust core (`pydantic-core`), roughly 5-50x faster than v1. The API changed meaningfully:

| Concept | v1 | v2 |
|---|---|---|
| Base class | `BaseModel` | `BaseModel` (same) |
| Parse dict | `Model.parse_obj(d)` | `Model.model_validate(d)` |
| Parse JSON | `Model.parse_raw(s)` | `Model.model_validate_json(s)` |
| To dict | `model.dict()` | `model.model_dump()` |
| To JSON | `model.json()` | `model.model_dump_json()` |
| Field validator | `@validator` | `@field_validator` |
| Root validator | `@root_validator` | `@model_validator` |
| Config | inner `class Config:` | `model_config = ConfigDict(...)` |

This guide is v2-only. If you see `@validator` or `.dict()` in older tutorials or Stack Overflow answers, that's v1 syntax — it still works via a compatibility shim but is deprecated.

---

## 2. Beginner: Core Concepts

### 2.1 Your First Model

A `BaseModel` subclass with type-annotated class attributes defines a schema. Instantiating it validates the input.

```python
from pydantic import BaseModel

class User(BaseModel):
    id: int
    name: str
    is_active: bool = True   # field with a default

user = User(id=1, name="Ada")
print(user)
# id=1 name='Ada' is_active=True

print(user.id, user.name)
```

### 2.2 Type Coercion ("lax mode" by default)

By default, Pydantic tries to **coerce** input into the declared type rather than rejecting anything that isn't an exact match. This is convenient for data coming from JSON, forms, or query strings where everything might arrive as a string.

```python
class Order(BaseModel):
    quantity: int
    price: float

o = Order(quantity="5", price="19.99")   # strings coerced to int/float
print(o)
# quantity=5 price=19.99
print(type(o.quantity))  # <class 'int'>
```

If coercion isn't possible, you get a `ValidationError` (see [2.11](#211-handling-validationerror)). If you want *no* coercion at all, see [Strict mode](#43-strict-vs-lax-mode).

### 2.3 Optional Fields, Defaults, and Required Fields

A field is **required** if it has no default value. Adding `= something` makes it optional.

```python
from typing import Optional

class Profile(BaseModel):
    username: str                     # required
    bio: Optional[str] = None         # optional, defaults to None
    age: int = 0                      # optional, defaults to 0
```

> **Gotcha:** `Optional[str]` only means the value *can be* `None` — it does **not** make the field optional to pass. `bio: Optional[str]` (no `= None`) is still *required*, just nullable. You must supply `= None` explicitly to make it optional.

For mutable defaults (lists, dicts, other models), never write `= []` — use `default_factory`:

```python
from pydantic import Field

class Team(BaseModel):
    members: list[str] = Field(default_factory=list)
```

### 2.4 `Field()` — Constraints and Metadata

`Field()` lets you attach validation constraints, defaults, aliases, and documentation metadata to a field.

```python
from pydantic import BaseModel, Field

class Product(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    price: float = Field(gt=0, description="Price in USD, must be positive")
    quantity: int = Field(default=1, ge=0, le=10_000)
    sku: str = Field(pattern=r"^[A-Z]{3}-\d{4}$")
```

Common `Field()` constraints:

| Constraint | Applies to | Meaning |
|---|---|---|
| `gt`, `ge`, `lt`, `le` | numbers | greater/less than (or equal) |
| `multiple_of` | numbers | must be a multiple of |
| `min_length`, `max_length` | str, list, etc. | length bounds |
| `pattern` | str | must match this regex |
| `default` | any | default value |
| `default_factory` | any | callable that builds the default |
| `alias` | any | alternate name for input/output |
| `description`, `title`, `examples` | any | JSON Schema metadata |
| `frozen` | any | field can't be reassigned after creation |

### 2.5 Nested Models

Models can contain other models. Pydantic validates recursively.

```python
class Address(BaseModel):
    street: str
    city: str
    zip_code: str

class Customer(BaseModel):
    name: str
    address: Address    # nested model

c = Customer(name="Grace", address={"street": "1 Infinite Loop", "city": "Cupertino", "zip_code": "95014"})
print(c.address.city)  # Cupertino
print(c.model_dump())
# {'name': 'Grace', 'address': {'street': '1 Infinite Loop', 'city': 'Cupertino', 'zip_code': '95014'}}
```

Pydantic accepts a plain `dict` for a nested model field and builds the sub-model automatically — you don't need to construct `Address(...)` yourself.

### 2.6 Collections: List, Dict, Set, Tuple

```python
from typing import Dict, List, Set, Tuple

class Inventory(BaseModel):
    tags: List[str]
    stock_by_location: Dict[str, int]
    unique_ids: Set[int]
    dimensions: Tuple[float, float, float]   # fixed-length, fixed-type tuple

inv = Inventory(
    tags=["new", "sale"],
    stock_by_location={"NYC": 10, "SF": 5},
    unique_ids=[1, 2, 2, 3],          # de-duplicated into a set: {1,2,3}
    dimensions=(10.0, 5.0, 2.0),
)
```

In modern Python (3.9+) you can use built-in generics directly: `list[str]`, `dict[str, int]`, etc. — no need to import from `typing`.

### 2.7 Enums and Literals

Use `Enum` for a closed set of named values, or `Literal` for a closed set of raw values without an enum class.

```python
from enum import Enum
from typing import Literal

class Status(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    CLOSED = "closed"

class Ticket(BaseModel):
    status: Status
    priority: Literal["low", "medium", "high"]

t = Ticket(status="active", priority="high")
print(t.status)             # Status.ACTIVE
print(t.status.value)       # "active"
```

`Literal` is often preferred for simple string tags because it needs no extra class and shows up cleanly in JSON Schema (`enum: [...]`).

### 2.8 Parsing Data In

| Method | Use for |
|---|---|
| `Model(**kwargs)` | keyword arguments |
| `Model.model_validate(obj)` | a `dict` (or any mapping-like object) |
| `Model.model_validate_json(json_str)` | a raw JSON string/bytes (faster — skips a manual `json.loads`) |

```python
data = {"id": 1, "name": "Ada"}
u1 = User(**data)
u2 = User.model_validate(data)
u3 = User.model_validate_json('{"id": 1, "name": "Ada"}')
```

### 2.9 Serializing Data Out

| Method | Produces |
|---|---|
| `model.model_dump()` | a Python `dict` |
| `model.model_dump_json()` | a JSON string |
| `dict(model)` | a shallow dict-like iteration (rarely used directly) |

```python
u = User(id=1, name="Ada")
print(u.model_dump())         # {'id': 1, 'name': 'Ada', 'is_active': True}
print(u.model_dump_json())    # '{"id":1,"name":"Ada","is_active":true}'

# Useful options:
u.model_dump(exclude={"is_active"})     # drop specific fields
u.model_dump(include={"id"})            # keep only specific fields
u.model_dump(exclude_none=True)         # drop fields that are None
u.model_dump(exclude_unset=True)        # only fields explicitly passed in (great for PATCH endpoints)
```

### 2.10 Docstrings and `model_fields`

You can introspect a model's schema at runtime:

```python
print(User.model_fields.keys())
# dict_keys(['id', 'name', 'is_active'])
print(User.model_fields["name"].annotation)
# <class 'str'>
```

### 2.11 Handling `ValidationError`

Invalid input raises `pydantic.ValidationError`, which bundles *every* failing field into one structured, iterable error object — not just the first failure.

```python
from pydantic import ValidationError

try:
    User(id="not-an-int", name=123)
except ValidationError as e:
    print(e.error_count())      # number of individual errors
    for err in e.errors():
        print(err["loc"], err["msg"], err["type"])
    # ('id',) Input should be a valid integer, unable to parse string as an integer int_parsing
```

Each error dict has `loc` (field path, as a tuple — useful for nested models), `msg` (human-readable), `type` (a stable machine-readable error code), and `input` (the offending value). `e.errors()` accepts `include_url=False` to omit the documentation links.

---

## 3. Intermediate: Validation & Configuration

### 3.1 Custom Field Validators

`@field_validator` runs custom logic on one field. It supports two modes:

- `mode="after"` (default): runs *after* Pydantic's built-in type coercion — you receive an already-typed value.
- `mode="before"`: runs *before* coercion — you receive the raw input (any type) and can transform it before Pydantic validates the type.

```python
from pydantic import BaseModel, field_validator

class User(BaseModel):
    name: str
    age: int = Field(gt=0, le=120)

    @field_validator("name")
    @classmethod
    def name_must_not_be_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("name must not be blank")
        return v.title()   # you can transform the value too

    @field_validator("age", mode="before")
    @classmethod
    def coerce_age_string(cls, v):
        if isinstance(v, str) and v.isdigit():
            return int(v)
        return v

u = User(name="alice", age=30)
print(u)   # name='Alice' age=30
```

A validator can target multiple fields: `@field_validator("field_a", "field_b")`, or all fields with `@field_validator("*")`.

### 3.2 Model-Level Validators

`@model_validator` sees *all* fields at once — essential for cross-field rules (e.g. "start_date must be before end_date").

```python
from pydantic import model_validator

class DateRange(BaseModel):
    start: str
    end: str

    @model_validator(mode="after")
    def check_order(self) -> "DateRange":
        if self.start > self.end:
            raise ValueError("start must be before end")
        return self
```

`mode="before"` gives you the raw input dict (before any field validation), useful for renaming/restructuring incoming data:

```python
class Legacy(BaseModel):
    full_name: str

    @model_validator(mode="before")
    @classmethod
    def combine_names(cls, data):
        if isinstance(data, dict) and "first" in data and "last" in data:
            data["full_name"] = f"{data.pop('first')} {data.pop('last')}"
        return data

print(Legacy(first="Ada", last="Lovelace"))  # full_name='Ada Lovelace'
```

### 3.3 Model Configuration (`model_config`)

Every model can be configured with `model_config = ConfigDict(...)` (replaces v1's inner `class Config:`).

```python
from pydantic import BaseModel, ConfigDict

class Strict(BaseModel):
    model_config = ConfigDict(
        extra="forbid",           # reject unknown fields (default: "ignore")
        strict=True,               # disable type coercion globally for this model
        frozen=True,                # make instances immutable & hashable
        str_strip_whitespace=True,  # auto .strip() all strings
        validate_assignment=True,   # re-validate on `model.field = value`
        populate_by_name=True,      # allow both alias and field name on input
    )
    a: int
```

Common `extra` settings:

| Value | Behavior |
|---|---|
| `"ignore"` (default) | unknown keys are silently dropped |
| `"forbid"` | unknown keys raise a `ValidationError` |
| `"allow"` | unknown keys are kept and accessible as attributes |

### 3.4 Aliases

Aliases let a field be named one thing in Python and another thing on the wire (very common for camelCase JSON APIs).

```python
class Product(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    item_id: int = Field(alias="itemId")
    price_usd: float = Field(alias="priceUsd")

p = Product(itemId=1, priceUsd=9.99)         # input uses the alias
print(p.item_id)                              # 1 — access uses the Python name
print(p.model_dump(by_alias=True))
# {'itemId': 1, 'priceUsd': 9.99}
print(p.model_dump())
# {'item_id': 1, 'price_usd': 9.99}  -- without by_alias, Python names are used
```

For a whole model, use `alias_generator` instead of tagging every field:

```python
from pydantic.alias_generators import to_camel

class Camel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)
    first_name: str
    last_name: str

c = Camel(firstName="Ada", lastName="Lovelace")
print(c.model_dump(by_alias=True))
# {'firstName': 'Ada', 'lastName': 'Lovelace'}
```

You can also set `validation_alias` and `serialization_alias` independently, when the input name and output name should differ.

### 3.5 Computed Fields

`@computed_field` exposes a derived `@property` as if it were a real field — it appears in `model_dump()` and the JSON Schema, but isn't settable as input.

```python
from pydantic import computed_field

class Rectangle(BaseModel):
    width: float
    height: float

    @computed_field
    @property
    def area(self) -> float:
        return self.width * self.height

r = Rectangle(width=2, height=3)
print(r.model_dump())
# {'width': 2.0, 'height': 3.0, 'area': 6.0}
```

### 3.6 Custom Serializers

`@field_serializer` and `@model_serializer` let you control exactly how a value is turned into dict/JSON output — useful for formatting money, dates, or redacting secrets.

```python
from pydantic import field_serializer

class Money(BaseModel):
    cents: int

    @field_serializer("cents")
    def ser_cents(self, v: int) -> str:
        return f"${v / 100:.2f}"

print(Money(cents=1099).model_dump())
# {'cents': '$10.99'}
```

### 3.7 Union Types and Discriminated Unions

A plain `Union` tries each member type in order (in "smart mode", Pydantic actually picks the *best* match, not just the first that coerces). For performance and unambiguous errors on tagged data, use a **discriminated union**: a shared "tag" field tells Pydantic exactly which variant to validate against, skipping the trial-and-error entirely.

```python
from typing import Literal, Union
from pydantic import Field

class Cat(BaseModel):
    pet_type: Literal["cat"]
    meow_volume: int

class Dog(BaseModel):
    pet_type: Literal["dog"]
    bark_volume: int

class Owner(BaseModel):
    pet: Union[Cat, Dog] = Field(discriminator="pet_type")

o = Owner(pet={"pet_type": "dog", "bark_volume": 5})
print(o)
# pet=Dog(pet_type='dog', bark_volume=5)
```

This pattern is the backbone of validating polymorphic payloads like webhook events or plugin configs (see [7.1](#71-discriminated-unions-for-polymorphic-event-payloads)).

### 3.8 Custom Types via `Annotated` + Validators

Rather than repeating a `@field_validator` on every model that needs it, package the rule once into a reusable annotated type using `BeforeValidator` / `AfterValidator`.

```python
from typing import Annotated
from pydantic import AfterValidator

def must_be_even(v: int) -> int:
    if v % 2 != 0:
        raise ValueError("must be even")
    return v

EvenInt = Annotated[int, AfterValidator(must_be_even)]

class Box(BaseModel):
    count: EvenInt   # reusable across any model
```

`WrapValidator` gives full control — you get the "next" validator as a callable, so you can catch its errors, retry, or fall back to a default:

```python
from pydantic import WrapValidator

def fallback_to_zero(v, handler, info):
    try:
        return handler(v)          # run normal validation
    except Exception:
        return 0                    # swallow bad input instead of raising

SafeInt = Annotated[int, WrapValidator(fallback_to_zero)]

class Safe(BaseModel):
    n: SafeInt

print(Safe(n="not a number"))   # n=0  (no exception raised)
```

### 3.9 Self-Referencing (Recursive) Models

Models can reference themselves for tree-like data (comment threads, file systems, org charts). Use a forward-reference string (or `from __future__ import annotations`).

```python
from __future__ import annotations
from pydantic import Field

class Comment(BaseModel):
    text: str
    replies: list[Comment] = Field(default_factory=list)

c = Comment(text="top", replies=[
    {"text": "reply 1"},
    {"text": "reply 2", "replies": [{"text": "nested reply"}]},
])
print(c.model_dump())
```

Without `from __future__ import annotations`, quote the self-reference: `replies: list["Comment"] = ...` and Pydantic resolves it automatically (call `Comment.model_rebuild()` manually only if you hit a `NameError` in edge cases like circular imports across modules).

---

## 4. Advanced: Type System & Internals

### 4.1 Generic Models

Generic models let you write one schema shape and parameterize it with different inner types — perfect for API envelopes.

```python
from typing import Generic, TypeVar

T = TypeVar("T")

class Response(BaseModel, Generic[T]):
    data: T
    status: str = "ok"

class Item(BaseModel):
    id: int

resp = Response[Item](data={"id": 1})
print(resp)
# data=Item(id=1) status='ok'

resp2 = Response[list[int]](data=[1, 2, 3])
```

### 4.2 `RootModel` — Validating Non-Dict Top-Level Data

Sometimes the "model" you want isn't a dict of fields at all — it's a bare list, a bare string, or a mapping. `RootModel` wraps a single value instead of a set of named fields (this replaces v1's `__root__` trick).

```python
from pydantic import RootModel

class IntList(RootModel[list[int]]):
    pass

il = IntList([1, 2, 3])
print(il.model_dump())   # [1, 2, 3]
print(il.root)            # [1, 2, 3] -- access the wrapped value via `.root`
```

### 4.3 Strict vs. Lax Mode

By default Pydantic is *lax*: it coerces reasonable inputs (`"5"` → `5`). Set `strict=True` (globally via `model_config`, per-field via `Field(strict=True)`, or per-call via `model.model_validate(data, strict=True)`) to demand exact types.

```python
class Strict(BaseModel):
    model_config = ConfigDict(strict=True)
    n: int

Strict(n=5)          # OK
Strict(n="5")        # raises ValidationError: input should be a valid integer (str not accepted)
```

Rule of thumb: use lax mode for data coming from the outside world (HTTP query params, CSV, forms — everything is stringly typed there anyway); use strict mode for internal, already-typed data where a `str` sneaking into an `int` field usually signals a real bug.

### 4.4 `TypeAdapter` — Validating Without a `BaseModel`

Not everything you want to validate is naturally a class. `TypeAdapter` gives you Pydantic's validation/serialization for *any* type — a bare `list[int]`, a `TypedDict`, a `Union`, even a single scalar — without wrapping it in a model.

```python
from pydantic import TypeAdapter

ta = TypeAdapter(list[int])
print(ta.validate_python(["1", "2", "3"]))   # [1, 2, 3]

ta_json = TypeAdapter(dict[str, float])
print(ta_json.validate_json('{"a": "1.5", "b": "2.0"}'))   # {'a': 1.5, 'b': 2.0}
```

Build a `TypeAdapter` once at module scope and reuse it — constructing one has overhead you don't want to pay per-call in a hot loop.

### 4.5 Pydantic Dataclasses

If you like `dataclasses.dataclass` ergonomics but want Pydantic validation, use `pydantic.dataclasses.dataclass` — a drop-in decorator, no `BaseModel` inheritance needed.

```python
import pydantic.dataclasses as pdc

@pdc.dataclass
class Coord:
    lat: float
    lon: float

print(Coord(lat="1.5", lon=2.5))   # Coord(lat=1.5, lon=2.5) -- "1.5" was coerced
```

Useful when integrating into a codebase that already uses stdlib dataclasses, or when you specifically want dataclass semantics (e.g. `__eq__` based on fields, positional args) rather than `BaseModel`'s.

### 4.6 Immutability, Hashing, and `model_construct`

```python
class Point(BaseModel):
    model_config = ConfigDict(frozen=True)
    x: int
    y: int

p1 = Point(x=1, y=2)
hash(p1)          # works -- frozen models are hashable, usable as dict/set keys
p1.x = 5           # raises ValidationError: Instance is frozen
```

For performance-critical paths where you've *already validated* data (e.g. reading from your own trusted database) and want to skip re-validation entirely, use `model_construct` — it builds the instance directly without running validators:

```python
fast = Point.model_construct(x=999, y=999)   # no validation performed
```

Use this sparingly — it bypasses every guarantee Pydantic normally gives you, including type coercion and custom validators.

### 4.7 Validation Context

Pass extra, non-field data into validators via `context=` — useful when a validation rule depends on something outside the payload itself (the current user, a feature flag, request metadata).

```python
from pydantic import ValidationInfo

class Ctx(BaseModel):
    value: int

    @field_validator("value")
    @classmethod
    def check_ctx(cls, v, info: ValidationInfo):
        max_allowed = (info.context or {}).get("max_allowed", 100)
        if v > max_allowed:
            raise ValueError(f"value exceeds {max_allowed}")
        return v

Ctx.model_validate({"value": 50}, context={"max_allowed": 10})  # raises ValidationError
```

### 4.8 JSON Schema Generation

Every model can emit a JSON Schema, which is what powers FastAPI's auto-generated OpenAPI docs and is increasingly used for LLM structured-output / tool-calling schemas.

```python
class Sample(BaseModel):
    """A sample model."""
    name: str = Field(description="The name", examples=["Alice"])
    age: int = Field(default=18, ge=0, le=150)

print(Sample.model_json_schema())
```

```json
{
  "description": "A sample model.",
  "properties": {
    "name": {"description": "The name", "examples": ["Alice"], "title": "Name", "type": "string"},
    "age": {"default": 18, "maximum": 150, "minimum": 0, "title": "Age", "type": "integer"}
  },
  "required": ["name"],
  "title": "Sample",
  "type": "object"
}
```

The docstring becomes `"description"`; `Field(description=..., examples=...)` map directly into schema keys. You can customize schema generation further with `json_schema_extra` on `Field()`, or by overriding `__get_pydantic_json_schema__` on custom types.

### 4.9 Arbitrary / Third-Party Types

For types Pydantic doesn't know how to validate natively (e.g. a third-party class, `numpy.ndarray`, a custom C-extension object), you have two options:

1. Allow it through unchecked: `model_config = ConfigDict(arbitrary_types_allowed=True)` — Pydantic will `isinstance()`-check it but won't coerce or introspect it.
2. Teach Pydantic how, by implementing `__get_pydantic_core_schema__` on the type — the fully general (and more involved) mechanism used by libraries that ship first-class Pydantic support.

```python
class Config:
    model_config = ConfigDict(arbitrary_types_allowed=True)
```

### 4.10 Performance Tips

- Reuse `TypeAdapter` instances instead of recreating them per call.
- Prefer `model_validate_json()` over `json.loads()` + `model_validate()` — it parses and validates in one Rust-side pass.
- Use `model_construct()` only for data you've already validated elsewhere (e.g. straight from your own database), never for untrusted input.
- Discriminated unions are meaningfully faster than plain unions on large tagged payloads, since Pydantic doesn't need to try every variant.
- Avoid deeply nested `Union` chains where possible; discriminate or restructure instead.

---

## 5. Settings Management (`pydantic-settings`)

`BaseSettings` (moved to the separate `pydantic-settings` package in v2) reads configuration from environment variables, `.env` files, and secrets directories — with the same validation machinery as any other model.

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="APP_", env_file=".env")

    name: str = "default"
    debug: bool = False
    database_url: str

# Given env vars APP_NAME=MyApp and APP_DEBUG=true:
s = Settings(database_url="postgres://localhost/db")
print(s)
# name='MyApp' debug=True database_url='postgres://localhost/db'
```

Key points:
- `env_prefix` is prepended to the **field name** (uppercased) to find the matching env var — `name` → `APP_NAME`.
- `env_file=".env"` auto-loads a dotenv file if present; real environment variables still take priority over the file.
- Nested settings models work too — by default, nested fields are set via `APP_SUBSECTION__FIELD` (double underscore as the delimiter, configurable via `env_nested_delimiter`).
- Secrets can be loaded from files in a directory via `secrets_dir`, matching Docker/Kubernetes secret-mounting conventions.

```python
class DBSettings(BaseModel):
    host: str
    port: int = 5432

class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(env_nested_delimiter="__")
    db: DBSettings

# APP env vars: DB__HOST=localhost DB__PORT=5433
```

This is the standard pattern for twelve-factor-style config: define one `Settings` class, instantiate it once at startup (`settings = Settings()`), and import that singleton everywhere instead of scattering `os.environ.get(...)` calls throughout the codebase.

---

## 6. Common Use Cases

### 6.1 API Request/Response Validation

The most common real-world use: validating incoming request bodies and shaping outgoing responses (this is exactly what FastAPI does under the hood with your route type hints).

```python
class CreateUserRequest(BaseModel):
    email: str = Field(pattern=r"^[^@]+@[^@]+\.[^@]+$")
    password: str = Field(min_length=8)

class UserResponse(BaseModel):
    id: int
    email: str
    # note: password is intentionally excluded from the response model
```

Using *separate* request and response models (rather than one shared model) is a deliberate best practice — it stops you from accidentally leaking fields like password hashes back to the client.

### 6.2 Layered Config Loading

Combine `BaseSettings` with explicit precedence: defaults → config file → environment variables → CLI args. `pydantic-settings` supports this natively via multiple settings sources, or you can layer it manually:

```python
import json

class Config(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="APP_")
    workers: int = 4
    timeout: float = 30.0

file_overrides = json.load(open("config.json")) if Path("config.json").exists() else {}
config = Config(**file_overrides)   # env vars still override these via BaseSettings' own resolution
```

### 6.3 Data Cleaning / ETL Pipelines

Pydantic models make excellent row-level validators when ingesting messy CSV/JSON data — invalid rows fail loudly and individually instead of corrupting a whole batch.

```python
class Row(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    user_id: int
    signup_date: str
    revenue: float = Field(ge=0)

good, bad = [], []
for raw_row in raw_rows:
    try:
        good.append(Row.model_validate(raw_row))
    except ValidationError as e:
        bad.append((raw_row, e.errors()))
```

### 6.4 Form / Query-Param Validation

Lax coercion is exactly what you want for HTML form data or URL query strings, where every value technically arrives as a string:

```python
class SearchParams(BaseModel):
    query: str
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, le=100)

# from a query string like ?page=2&per_page=50
params = SearchParams(query="pydantic", page="2", per_page="50")
```

---

## 7. Complex / Advanced Use Cases

### 7.1 Discriminated Unions for Polymorphic Event Payloads

A very common real-world pattern: a webhook or event bus sends different shaped payloads under one endpoint, tagged by an `event_type` field.

```python
from typing import Literal, Union, Annotated

class UserCreated(BaseModel):
    event_type: Literal["user.created"]
    user_id: int
    email: str

class UserDeleted(BaseModel):
    event_type: Literal["user.deleted"]
    user_id: int

class OrderPlaced(BaseModel):
    event_type: Literal["order.placed"]
    order_id: int
    total: float

Event = Annotated[
    Union[UserCreated, UserDeleted, OrderPlaced],
    Field(discriminator="event_type"),
]

class Webhook(BaseModel):
    event: Event

w = Webhook(event={"event_type": "order.placed", "order_id": 42, "total": 19.99})
print(w.event)   # OrderPlaced(event_type='order.placed', order_id=42, total=19.99)
```

Adding a new event type is then just adding a new model to the `Union` — the discriminator ensures each payload is validated against exactly the right variant, and validation errors point at the *correct* model instead of a confusing "didn't match any of 6 unrelated schemas" dump.

### 7.2 Partial / PATCH Models Generated Dynamically

REST `PATCH` semantics need "every field optional, but only apply what was actually sent." Rather than hand-maintaining a second, all-optional copy of every model, generate it programmatically with `create_model`:

```python
from typing import Optional
from pydantic import create_model

def make_partial(model: type[BaseModel]) -> type[BaseModel]:
    fields = {
        name: (Optional[f.annotation], None)
        for name, f in model.model_fields.items()
    }
    return create_model(f"Partial{model.__name__}", **fields)

class Item(BaseModel):
    name: str
    price: float

PartialItem = make_partial(Item)
patch = PartialItem(name="only updating the name")
print(patch)  # name='only updating the name' price=None

# Combine with exclude_unset to apply only fields the client actually sent:
raw_patch = PartialItem.model_validate({"name": "New Name"})
updates = raw_patch.model_dump(exclude_unset=True)   # {'name': 'New Name'}
```

### 7.3 Generic API Envelopes with Nested Discriminated Unions

Combining [Generic Models](#41-generic-models) with discriminated unions gives you a single, reusable "envelope" shape across an entire API surface — a pattern common in job queues, GraphQL-like result types, and RPC frameworks.

```python
from typing import Generic, TypeVar

T = TypeVar("T")

class Success(BaseModel, Generic[T]):
    ok: Literal[True] = True
    data: T

class Failure(BaseModel):
    ok: Literal[False] = False
    error: str

Result = Annotated[Union[Success[T], Failure], Field(discriminator="ok")]

class Envelope(BaseModel, Generic[T]):
    result: Result

# Envelope[Item] validates either {"result": {"ok": true, "data": {...}}}
# or {"result": {"ok": false, "error": "..."}}
```

### 7.4 Recursive Tree Structures with Depth-Limited Validation

Extending the [self-referencing model](#39-self-referencing-recursive-models) pattern with a `model_validator` that enforces business rules across the whole tree — e.g. capping nesting depth to prevent abuse in user-submitted comment trees:

```python
class Comment(BaseModel):
    text: str
    replies: list["Comment"] = Field(default_factory=list)

    @model_validator(mode="after")
    def check_depth(self, info=None) -> "Comment":
        def depth(node: "Comment") -> int:
            if not node.replies:
                return 1
            return 1 + max(depth(r) for r in node.replies)
        if depth(self) > 5:
            raise ValueError("comment thread nested too deeply")
        return self
```

### 7.5 Schema Versioning / Migration

When a stored data format evolves, a `model_validator(mode="before")` can detect and upgrade old shapes transparently on load:

```python
class UserV2(BaseModel):
    """Current schema. Older records may still have `full_name` instead of first/last."""
    first_name: str
    last_name: str

    @model_validator(mode="before")
    @classmethod
    def migrate_v1(cls, data):
        if isinstance(data, dict) and "full_name" in data:
            first, _, last = data.pop("full_name").partition(" ")
            data.setdefault("first_name", first)
            data.setdefault("last_name", last)
        return data

# Old record: {"full_name": "Ada Lovelace"}
# New record: {"first_name": "Ada", "last_name": "Lovelace"}
# Both validate cleanly against UserV2.
```

### 7.6 Structured Output Schemas for LLM Tool-Calling

Because `model_json_schema()` produces standard JSON Schema, Pydantic models are the de facto way to define structured-output / function-calling schemas for LLM APIs (including Anthropic's tool-use format) — define the model once, pass its schema to the API, then validate the model's response back into the same class.

```python
class ExtractedInvoice(BaseModel):
    vendor: str
    total: float = Field(ge=0)
    line_items: list[str]

schema = ExtractedInvoice.model_json_schema()
# ... pass `schema` as a tool/function definition to an LLM call ...
# ... then validate whatever JSON comes back: ...
invoice = ExtractedInvoice.model_validate_json(llm_response_text)
```

---

## 8. Cheat Sheet

### Parsing / Serializing

```python
Model(**kwargs)                       # from keyword args
Model.model_validate(obj)             # from a dict-like object
Model.model_validate_json(json_str)   # from a raw JSON string/bytes
Model.model_construct(**kwargs)       # build WITHOUT validation (trusted data only)

model.model_dump()                    # -> dict
model.model_dump_json()               # -> JSON str
model.model_dump(exclude={"x"})       # drop a field
model.model_dump(include={"x"})       # keep only a field
model.model_dump(exclude_none=True)   # drop None fields
model.model_dump(exclude_unset=True)  # only fields explicitly provided
model.model_dump(by_alias=True)       # use field aliases as keys
model.model_copy(update={"x": 1})     # copy with overrides
```

### Field Constraints Quick Reference

| Type | Constraints available |
|---|---|
| `int` / `float` | `gt`, `ge`, `lt`, `le`, `multiple_of` |
| `str` | `min_length`, `max_length`, `pattern` |
| `list` / `set` / `dict` | `min_length`, `max_length` |
| any | `default`, `default_factory`, `alias`, `description`, `frozen`, `strict` |

### Decorators

| Decorator | Purpose |
|---|---|
| `@field_validator("f", mode="before"/"after")` | validate/transform one field |
| `@model_validator(mode="before"/"after")` | validate across the whole model |
| `@field_serializer("f")` | custom output for one field |
| `@model_serializer` | custom output for the whole model |
| `@computed_field` (+ `@property`) | derived, read-only output field |

### Config Keys (`ConfigDict`)

| Key | Effect |
|---|---|
| `extra` | `"ignore"` / `"forbid"` / `"allow"` unknown fields |
| `strict` | disable type coercion |
| `frozen` | immutable + hashable |
| `str_strip_whitespace` | auto-strip strings |
| `validate_assignment` | re-validate on attribute assignment |
| `populate_by_name` | accept both alias and field name as input |
| `alias_generator` | auto-derive aliases (e.g. `to_camel`) |
| `arbitrary_types_allowed` | allow non-Pydantic types via `isinstance` check |

### Key Imports

```python
from pydantic import (
    BaseModel, Field, ConfigDict,
    field_validator, model_validator,
    field_serializer, model_serializer, computed_field,
    ValidationError, ValidationInfo,
    RootModel, TypeAdapter, create_model,
    BeforeValidator, AfterValidator, WrapValidator, PlainValidator,
)
from pydantic_settings import BaseSettings, SettingsConfigDict
import pydantic.dataclasses as pdc
```

---

## 9. Common Pitfalls

- **`Optional[X]` ≠ "not required."** It only allows `None` as a value. Pair it with `= None` to actually make the field optional.
- **Mutable defaults.** Never write `field: list = []` — use `Field(default_factory=list)`. A bare mutable literal default is shared across every instance in v1-style dataclasses/stdlib classes; Pydantic v2 actually guards against this specific footgun for its own fields, but the habit matters the moment you write a `default_factory` for anything more complex, like a nested model.
- **Confusing `model_dump()` with `by_alias`.** If your model uses aliases for a JSON API, forgetting `by_alias=True` silently emits Python-style field names instead of the API's expected keys.
- **`extra="ignore"` hiding typos.** The default setting silently drops unrecognized fields — a typo'd key in incoming data (`emial` instead of `email`) won't error, it'll just vanish. Use `extra="forbid"` during development/testing of request models to catch this.
- **Validators not returning a value.** `@field_validator`/`@model_validator` must `return` the (possibly transformed) value — forgetting the `return` silently sets the field to `None`.
- **`model_construct()` skipping validation entirely.** It's fast but gives zero guarantees — never use it on untrusted input.
- **Comparing enums to raw strings.** `Status.ACTIVE == "active"` works if the enum subclasses `str` (`class Status(str, Enum)`), but **not** for a plain `class Status(Enum)` — decide deliberately which one you want.
- **Union order matters less than you think, but discriminators still help.** Pydantic v2's "smart mode" union validation tries to pick the *best* matching member rather than the first coercible one, but for tagged/polymorphic data a discriminated union is still faster and gives far better error messages.

---

## 10. Further Resources

- Official docs: https://docs.pydantic.dev
- Migration guide (v1 → v2): https://docs.pydantic.dev/latest/migration/
- `pydantic-settings`: https://docs.pydantic.dev/latest/concepts/pydantic_settings/
- JSON Schema generation details: https://docs.pydantic.dev/latest/concepts/json_schema/
- Source: https://github.com/pydantic/pydantic
