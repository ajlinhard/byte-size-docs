# 12 — Architecture Patterns and Performance

> **Level:** Advanced · **Prerequisite:** [11 — Internals](11-internals.md)

This chapter is about using Pydantic *well* in real applications: where models belong in a layered architecture, how to structure schemas so they evolve gracefully, how to keep secrets and errors safe, how to test, and how to make Pydantic fast.

---

## Part A — Architecture patterns

### 1. Validate at the boundaries

```
               ┌───────────────────────────────────────────────┐
HTTP / CLI ──► │  Interface layer:  Request/Response schemas   │ ◄── Pydantic (lax, aliases, docs)
Queue / Env    │       ↓ map                     ↑ map          │
               │  Application layer: use-cases / services       │
               │       ↓                         ↑               │
               │  Domain layer: entities, value objects, rules  │ ◄── plain classes / dataclasses,
               │       ↓                         ↑               │     or strict frozen Pydantic models
               │  Infrastructure: ORM rows, external API DTOs   │ ◄── ORM models / Pydantic DTOs
               └───────────────────────────────────────────────┘
```

Principles:

- **Parse at the edge.** Every byte entering the system passes through a Pydantic model (HTTP bodies, query params, env vars, queue messages, files, LLM outputs, third-party API responses).
- **Inside, trust types.** Don't re-validate; pass validated objects or domain objects.
- **Keep transport and domain separate** when they diverge. API schemas change for client reasons (camelCase, versioning, docs); domain models change for business reasons. Coupling them makes both harder to change.

Small apps can legitimately use one model per entity everywhere. Grow into separation when friction appears.

### 2. The schema family pattern (Create / Update / Read)

A single entity usually needs several shapes. Share the common part through inheritance:

```python
from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=1, max_length=100)


class UserCreate(UserBase):
    password: str = Field(min_length=12)


class UserUpdate(BaseModel):                     # PATCH: everything optional
    email: EmailStr | None = None
    full_name: str | None = Field(default=None, min_length=1, max_length=100)


class UserRead(UserBase):
    model_config = ConfigDict(from_attributes=True)   # build from ORM rows
    id: int
    created_at: datetime


# Applying a PATCH:
current = UserRead(id=1, email="a@x.org", full_name="Ada", created_at="2026-01-01T00:00:00")
patch = UserUpdate.model_validate({"full_name": "Ada Lovelace"})
updated = current.model_copy(update=patch.model_dump(exclude_unset=True))
print(updated.full_name, updated.email)
#> Ada Lovelace a@x.org
```

`exclude_unset=True` is what distinguishes "client set this to null" from "client didn't send it". The `MISSING` sentinel (stable in 2.14) is an alternative that makes "not sent" explicit in the type.

> `model_copy(update=...)` does **not** validate. Since `UserUpdate` already validated the values, that's acceptable here; otherwise re-validate.

### 3. Mapping between layers

```python
from dataclasses import dataclass
from decimal import Decimal
from pydantic import BaseModel, ConfigDict


@dataclass(frozen=True)
class Product:                      # domain entity: no Pydantic dependency
    sku: str
    price: Decimal
    active: bool

    def discounted(self, pct: int) -> Decimal:
        return self.price * (100 - pct) / 100


class ProductOut(BaseModel):        # API schema
    model_config = ConfigDict(from_attributes=True)
    sku: str
    price: Decimal


p = Product(sku="A1", price=Decimal("10.00"), active=True)
print(ProductOut.model_validate(p).model_dump_json())   # domain → API via from_attributes
#> {"sku":"A1","price":"10.00"}
```

Mapping options, in increasing explicitness: `from_attributes=True` (attribute-by-attribute), `Model.model_validate(obj.__dict__)`, or explicit mapper functions (`def to_out(p: Product) -> ProductOut`). Explicit mappers are the most refactor-friendly for complex cases.

### 4. Value objects with strict, frozen models

When you *do* use Pydantic in the domain, make value objects immutable and strict:

```python
from decimal import Decimal
from typing import Self
from pydantic import BaseModel, ConfigDict, Field, model_validator


class Money(BaseModel):
    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")
    amount: Decimal = Field(max_digits=12, decimal_places=2)
    currency: str = Field(pattern=r"^[A-Z]{3}$")

    def __add__(self, other: "Money") -> "Money":
        if other.currency != self.currency:
            raise ValueError("currency mismatch")
        return Money(amount=self.amount + other.amount, currency=self.currency)


a = Money(amount=Decimal("1.50"), currency="USD")
print(a + Money(amount=Decimal("2.25"), currency="USD"))
#> amount=Decimal('3.75') currency='USD'
print({a, a})           # hashable
#> {Money(amount=Decimal('1.50'), currency='USD')}
```

### 5. Versioned and evolving schemas

- **Additive changes** (new optional field with a default) are backward compatible. Combine with `extra="ignore"` on consumers so producers can add fields first.
- **Renames:** accept old and new names with `validation_alias=AliasChoices("new_name", "old_name")`; serialize the new one.
- **Breaking changes:** version explicitly — `EventV1`, `EventV2` — and use a discriminated union on a `version` field to read both:

```python
from typing import Annotated, Literal
from pydantic import BaseModel, Field, TypeAdapter


class OrderEventV1(BaseModel):
    version: Literal[1]
    amount_cents: int

    def upgrade(self) -> "OrderEventV2":
        return OrderEventV2(version=2, amount=self.amount_cents / 100, currency="USD")


class OrderEventV2(BaseModel):
    version: Literal[2]
    amount: float
    currency: str


AnyOrderEvent = TypeAdapter(Annotated[OrderEventV1 | OrderEventV2, Field(discriminator="version")])


def load(raw: str) -> OrderEventV2:
    evt = AnyOrderEvent.validate_json(raw)
    return evt.upgrade() if isinstance(evt, OrderEventV1) else evt


print(load('{"version": 1, "amount_cents": 1999}'))
#> version=2 amount=19.99 currency='USD'
```

- Store generated JSON Schemas in the repo and diff them in CI to catch accidental breaking changes.

### 6. Secrets and safe errors

- Use `SecretStr`/`SecretBytes`/`Secret[T]` for credentials: masked in `repr`, logs, and dumps (unless you explicitly serialize them).
- Set `hide_input_in_errors=True` on models that receive sensitive values, so `ValidationError` messages don't echo them.
- When returning errors to clients, build responses from `e.errors(include_input=False, include_url=False)`.
- Use `extra="forbid"` on write endpoints to catch typos and mass-assignment attempts (e.g. a client sending `is_admin: true`).

### 7. Configuration as a typed object

Load all configuration once at startup into a `pydantic-settings` object and inject it — never sprinkle `os.environ[...]` around the codebase. See [13 — Integration: pydantic-settings](13-integration-pydantic-settings.md).

### 8. Testing

- **Unit-test validators** directly through the model: valid examples, boundary values, and each error `type`.
- **Contract tests:** snapshot `model_json_schema()` output.
- **Property-based tests:** generate valid instances from types with Hypothesis (`st.builds(Model)` works with constrained types) or from the JSON Schema with `hypothesis-jsonschema`.
- **Factories:** `polyfactory` builds realistic instances of Pydantic models for tests.

```python
import pytest
from pydantic import BaseModel, Field, ValidationError


class Age(BaseModel):
    value: int = Field(ge=0, le=150)


@pytest.mark.parametrize("bad, err", [(-1, "greater_than_equal"), (151, "less_than_equal"), ("x", "int_parsing")])
def test_age_errors(bad, err):
    with pytest.raises(ValidationError) as exc:
        Age(value=bad)
    assert exc.value.errors()[0]["type"] == err
```

---

## Part B — Performance

Pydantic is fast by default. These guidelines matter when you validate millions of objects or define thousands of models.

### 1. Validate JSON with `model_validate_json`

```py
# slower: two passes, intermediate dicts
Model.model_validate(json.loads(raw))
# faster: one pass in Rust (jiter)
Model.model_validate_json(raw)
```

Same for output: `model_dump_json()` beats `json.dumps(model_dump())`.

### 2. Build `TypeAdapter`s once

Instantiate adapters at module scope; never inside loops or per-request.

### 3. Prefer native constraints to Python validators

`Field(ge=0, max_length=10, pattern=...)` and `StringConstraints` run inside Rust. A Python `@field_validator` doing the same check crosses into Python for every value.

### 4. Choose the cheapest container type

- `list` / `tuple` over `Sequence` / `Iterable` (abstract types need extra checks).
- `dict` over `Mapping`.
- `TypedDict` instead of nested `BaseModel` when you don't need model features — skips instance construction.
- Avoid `Any`-heavy or wide un-discriminated unions.

### 5. Use discriminated unions

`Field(discriminator="type")` turns an O(n) "try every member" into an O(1) lookup, and produces much clearer errors.

### 6. Avoid unnecessary wrap validators

Wrap validators force materializing data in Python. Use before/after where possible.

### 7. Skip validation for trusted data

`Model.model_construct(**trusted)` for data you produced yourself (e.g. re-hydrating from your own cache). Use cautiously.

### 8. `FailFast` for big sequences

`Annotated[list[T], FailFast()]` (or `Field(fail_fast=True)`) stops at the first invalid item.

### 9. Startup time: `defer_build` and fewer models

For large codebases (CLIs, serverless functions with cold starts):

```python
from pydantic import BaseModel, ConfigDict


class Lazy(BaseModel):
    model_config = ConfigDict(defer_build=True)   # validator built on first use
    x: int


print(Lazy.__pydantic_complete__)   # not built yet
#> False
Lazy(x=1)
print(Lazy.__pydantic_complete__)
#> True
```

Also: upgrade Pydantic — 2.11 through 2.14 each reduced schema build time significantly (2.14 alone shaves 5–20% per optimization on the team's benchmarks).

### 10. Measure

```python
import timeit
from pydantic import BaseModel, TypeAdapter
from typing import TypedDict


class PM(BaseModel):
    a: int
    b: str


class TD(TypedDict):
    a: int
    b: str


raw = b'{"a": 1, "b": "x"}'
td = TypeAdapter(TD)
t_model = timeit.timeit(lambda: PM.model_validate_json(raw), number=50_000)
t_td = timeit.timeit(lambda: td.validate_json(raw), number=50_000)
print(t_td < t_model * 1.5)   # TypedDict is typically at least as fast
#> True
```

Profile real workloads (e.g. with `py-spy`, `pyinstrument`, or Logfire's Pydantic instrumentation) before optimizing — validation is rarely the bottleneck compared to I/O.

---

## Summary

- Validate at system boundaries; separate transport schemas from domain models when they diverge.
- Use schema families (Create/Update/Read), explicit mapping, versioned discriminated unions for evolving data.
- Protect secrets with `SecretStr`, `hide_input_in_errors`, and `extra="forbid"`.
- For speed: JSON methods, reused adapters, native constraints, discriminated unions, `TypedDict`, `defer_build`.

**Next:** [13 — Integration: pydantic-settings](13-integration-pydantic-settings.md)
