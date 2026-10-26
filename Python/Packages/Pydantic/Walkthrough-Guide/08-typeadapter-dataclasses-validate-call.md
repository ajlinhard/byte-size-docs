# 08 — `TypeAdapter`, Dataclasses, and `@validate_call`

> **Level:** Intermediate · **Prerequisite:** [07 — Unions, Generics, and Recursive Models](07-unions-generics-and-recursive-models.md)

`BaseModel` is not the only entry point to Pydantic's engine. You can validate **any type**, decorate **standard dataclasses**, or validate **function arguments**. All of these share the same core, the same error format, and the same JSON Schema support.

---

## 1. `TypeAdapter` — validation for arbitrary types

```python
from datetime import date
from typing import Annotated
from pydantic import Field, TypeAdapter, ValidationError

DateList = TypeAdapter(list[date])

print(DateList.validate_python(["2026-01-01", date(2026, 2, 1)]))
#> [datetime.date(2026, 1, 1), datetime.date(2026, 2, 1)]
print(DateList.validate_json('["2026-03-01"]'))
#> [datetime.date(2026, 3, 1)]
print(DateList.dump_json([date(2026, 1, 1)]))
#> b'["2026-01-01"]'
print(DateList.dump_python([date(2026, 1, 1)], mode="json"))
#> ['2026-01-01']
print(DateList.json_schema())
#> {'items': {'format': 'date', 'type': 'string'}, 'type': 'array'}

Percent = TypeAdapter(Annotated[float, Field(ge=0, le=100)])
try:
    Percent.validate_python(150)
except ValidationError as e:
    print(e.errors()[0]["type"])
    #> less_than_equal
```

### API

| Method | Purpose |
|---|---|
| `validate_python(obj, *, strict, from_attributes, context, ...)` | validate Python data |
| `validate_json(data)` | parse + validate JSON |
| `validate_strings(obj)` | validate string-only data |
| `dump_python(value, *, mode, include, exclude, by_alias, ...)` | serialize to Python |
| `dump_json(value, ...)` | serialize to JSON **bytes** |
| `json_schema(mode=...)` | JSON Schema |
| `get_default_value()` | default, if the type has one |

### When to use it

- Top-level data that isn't an object: `list[Item]`, `dict[str, Rule]`, `int | None`.
- Validating `TypedDict`s, `NamedTuple`s, stdlib dataclasses without converting them to models.
- Discriminated unions at the top level (`TypeAdapter(Annotated[A | B, Field(discriminator="kind")])`).
- Producing JSON Schema for a function's return type or a union.

### Performance tip: create adapters once

Building a `TypeAdapter` compiles a validator — comparatively expensive. Create it **once** at module level and reuse it, not inside a hot loop or request handler.

```py
# ❌ rebuilds the validator on every call
def parse(items):
    return TypeAdapter(list[Item]).validate_python(items)

# ✅ build once
ITEMS = TypeAdapter(list[Item])
def parse(items):
    return ITEMS.validate_python(items)
```

Since 2.14 (using Python 3.15's `TypeForm` / pyright 1.1.412+ / mypy 2.2+), type checkers infer the return type of `validate_python` correctly even for union and `Annotated` forms (e.g. `TypeAdapter(int | str).validate_python(...)` is typed `int | str`).

## 2. Pydantic dataclasses

`pydantic.dataclasses.dataclass` is a drop-in replacement for `dataclasses.dataclass` that adds validation:

```python
from dataclasses import field
from pydantic import ConfigDict, Field, TypeAdapter, ValidationError
from pydantic.dataclasses import dataclass


@dataclass(config=ConfigDict(str_strip_whitespace=True))
class Book:
    title: str
    year: int = Field(ge=1450)                 # Pydantic Field works here
    authors: list[str] = field(default_factory=list)

    def __post_init__(self):                   # runs after validation
        self.title = self.title.title()


b = Book(title="  dune ", year="1965")
print(b)
#> Book(title='Dune', year=1965, authors=[])

try:
    Book(title="x", year=1000)
except ValidationError as e:
    print(e.errors()[0]["type"])
    #> greater_than_equal

# dataclasses don't have model_dump; use a TypeAdapter
print(TypeAdapter(Book).dump_json(b))
#> b'{"title":"Dune","year":1965,"authors":[]}'
```

### Dataclass vs `BaseModel`

| | `BaseModel` | Pydantic `@dataclass` |
|---|---|---|
| Positional init | ❌ keyword-only | ✅ |
| `model_dump`, `model_validate`… | ✅ methods | via `TypeAdapter` |
| `extra='allow'` storage | ✅ | limited (extras set as attributes) |
| Stdlib compatibility (`dataclasses.asdict`, `fields`, `replace`) | ❌ | ✅ |
| `slots=True`, `kw_only=True`, `InitVar` | — | ✅ |
| Validation on assignment | via config | via config |
| Recommended for | APIs, schemas, rich features | lightweight domain objects, stdlib interop |

### Standard-library dataclasses inside models

Plain `@dataclasses.dataclass` classes can be used as field types — Pydantic validates them (it builds a schema from their fields) but returns instances of the stdlib class:

```python
import dataclasses
from pydantic import BaseModel


@dataclasses.dataclass
class Money:
    amount: int
    currency: str


class Price(BaseModel):
    value: Money


print(Price(value={"amount": "5", "currency": "EUR"}).value)
#> Money(amount=5, currency='EUR')
```

## 3. `@validate_call` — validated functions

Validate arguments (and optionally the return value) of any function using its annotations:

```python
from datetime import date
from typing import Annotated
from pydantic import Field, ValidationError, validate_call


@validate_call
def schedule(title: Annotated[str, Field(min_length=1)], on: date, attendees: list[str] = [], *, remind: bool = True) -> str:
    return f"{title} on {on:%b %d} with {len(attendees)} attendees (remind={remind})"


print(schedule("Standup", "2026-10-16", ("ada", "grace"), remind="no"))
#> Standup on Oct 16 with 2 attendees (remind=False)

try:
    schedule("", "not-a-date")
except ValidationError as e:
    print([err["loc"] for err in e.errors()])
    #> [(0,), (1,)]
```

Options:

- `@validate_call(validate_return=True)` — also validate the return value.
- `@validate_call(config=ConfigDict(strict=True, arbitrary_types_allowed=True))`.
- Works with `async def`, methods (`self` is handled; it can even be used as a parameter name since 2.14), `*args`, `**kwargs` (including `Unpack[TypedDict]`), and positional-only / keyword-only parameters.
- Aliases via `Field(alias=...)`/`validation_alias` on parameters are respected.

**Cost:** each call validates every argument. Great for public library APIs, CLI entry points and plugin boundaries; avoid on hot internal paths.

## 4. Validating `TypedDict` and `NamedTuple` directly

Sometimes you want plain dicts out — no model class at all (e.g. for performance or JSON-in, JSON-out pipelines):

```python
from typing import NotRequired, TypedDict
from pydantic import TypeAdapter, with_config, ConfigDict


@with_config(ConfigDict(extra="forbid"))
class Point(TypedDict):
    x: int
    y: int
    label: NotRequired[str]


Points = TypeAdapter(list[Point])
pts = Points.validate_json('[{"x": 1, "y": "2"}]')
print(pts, type(pts[0]))
#> [{'x': 1, 'y': 2}] <class 'dict'>
```

Validating into `TypedDict` is typically faster than into `BaseModel` (no instance construction), at the cost of methods/properties.

## 5. Choosing the right tool

| Need | Use |
|---|---|
| A rich data object with methods, config, serialization | `BaseModel` |
| A stdlib-compatible, positional-arg class with validation | `pydantic.dataclasses.dataclass` |
| Validate a non-object type / a `TypedDict` / a union at top level | `TypeAdapter` |
| Validate the arguments of a function | `@validate_call` |
| Top-level non-object type with methods | `RootModel` |

---

## Summary

- `TypeAdapter(T)` brings validation, serialization and JSON Schema to **any** type. Build it once and reuse it.
- Pydantic dataclasses add validation to the familiar dataclass API; stdlib dataclasses are validated when used as field types.
- `@validate_call` validates function inputs (and outputs with `validate_return=True`).
- `TypedDict` + `TypeAdapter` is a fast, dict-in/dict-out alternative to models.

**Next:** [09 — JSON Schema](09-json-schema.md)
