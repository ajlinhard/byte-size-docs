# 03 — Fields and Types

> **Level:** Beginner → Intermediate · **Prerequisite:** [02 — Models](02-models.md)

The annotation tells Pydantic *what type* a field is; `Field()` and `Annotated` metadata tell it *what else* to enforce or document. This chapter covers both, plus the large catalog of types Pydantic understands out of the box.

---

## 1. `Field()` — per-field configuration

```python
from pydantic import BaseModel, Field


class Product(BaseModel):
    name: str = Field(min_length=1, max_length=100, description="Display name")
    price: float = Field(gt=0, le=1_000_000, examples=[9.99])
    quantity: int = Field(default=0, ge=0, multiple_of=1)
    sku: str = Field(pattern=r"^[A-Z]{3}-\d{4}$")
    tags: list[str] = Field(default_factory=list, max_length=10)


print(Product(name="Mug", price=12.5, sku="MUG-0001"))
#> name='Mug' price=12.5 quantity=0 sku='MUG-0001' tags=[]
```

### Common `Field()` arguments

| Category | Arguments |
|---|---|
| **Defaults** | `default`, `default_factory` (callable; may take validated data as its single argument) |
| **Numeric constraints** | `gt`, `ge`, `lt`, `le`, `multiple_of`, `allow_inf_nan`, `max_digits`, `decimal_places` |
| **String / collection constraints** | `min_length`, `max_length`, `pattern` |
| **Aliases** | `alias`, `validation_alias`, `serialization_alias` (chapter 05/06) |
| **Behavior** | `strict`, `frozen`, `validate_default`, `exclude`, `exclude_if` (2.12+), `repr`, `init`, `init_var`, `kw_only`, `discriminator`, `union_mode`, `fail_fast` |
| **Docs / schema** | `title`, `description`, `examples`, `json_schema_extra`, `deprecated` |

### `default_factory` with validated data

A factory can look at the fields validated *before* it:

```python
from pydantic import BaseModel, Field


class User(BaseModel):
    email: str
    username: str = Field(default_factory=lambda data: data["email"].split("@")[0])


print(User(email="grace@navy.mil").username)
#> grace
```

### `validate_default`

Defaults are trusted and **not validated** by default. Turn validation on if a default might be invalid or needs coercion:

```python
from pydantic import BaseModel, Field


class M(BaseModel):
    port: int = Field(default="8080", validate_default=True)


print(M().port, type(M().port))
#> 8080 <class 'int'>
```

### Deprecating a field

```python
import warnings
from pydantic import BaseModel, Field


class Config(BaseModel):
    timeout: int = Field(default=30, deprecated="Use `timeout_seconds` instead")
    timeout_seconds: int = 30


with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always")
    Config().timeout
    print(w[0].category.__name__)
    #> DeprecationWarning
```

The field is also flagged `"deprecated": true` in the JSON Schema.

## 2. `Annotated` — the idiomatic way to attach metadata

`typing.Annotated[T, *metadata]` lets you attach constraints **to the type itself**, so they are reusable and work anywhere a type is accepted (function parameters, `list[...]` items, `TypeAdapter`, FastAPI params…).

```python
from typing import Annotated
from pydantic import BaseModel, Field

PositiveInt = Annotated[int, Field(gt=0)]
Username = Annotated[str, Field(min_length=3, max_length=20, pattern=r"^[a-z0-9_]+$")]


class Team(BaseModel):
    name: Username
    member_ids: list[PositiveInt]          # constraint applies to each item
    scores: dict[Username, PositiveInt]


print(Team(name="core_devs", member_ids=[1, 2], scores={"ada": 10}))
#> name='core_devs' member_ids=[1, 2] scores={'ada': 10}
```

Compare with `member_ids: list[int] = Field(gt=0)` — that would try to apply `gt` to the *list*, which is an error. **Put constraints where they belong using `Annotated`.**

### `annotated_types` and Pydantic constraint markers

Pydantic understands the [`annotated-types`](https://github.com/annotated-types/annotated-types) vocabulary as well as its own markers:

```python
from typing import Annotated
from annotated_types import Gt, Len, MaxLen
from pydantic import BaseModel, StringConstraints


class Doc(BaseModel):
    title: Annotated[str, StringConstraints(strip_whitespace=True, to_lower=True, min_length=1)]
    code: Annotated[str, StringConstraints(ascii_only=True, max_length=8)]  # ascii_only: 2.13+
    weight: Annotated[float, Gt(0)]
    authors: Annotated[list[str], Len(min_length=1, max_length=5)]
    summary: Annotated[str, MaxLen(280)] = ""


print(Doc(title="  Hello WORLD ", code="AB12", weight=1.5, authors=["me"]).title)
#> hello world
```

### Order of metadata matters

Metadata in `Annotated` is applied **left to right**, and validators wrap inner ones. This becomes important with functional validators (chapter 04).

## 3. The type catalog

### Standard scalars

| Annotation | Lax-mode inputs accepted (examples) |
|---|---|
| `int` | `int`, `"42"`, `42.0` (no fractional part), `True` is **rejected** in strict mode only |
| `float` | `float`, `int`, `"3.14"`, `"inf"` (unless `allow_inf_nan=False`) |
| `bool` | `True/False`, `0/1`, `"true"/"false"`, `"yes"/"no"`, `"on"/"off"`, `"t"/"f"`, `"y"/"n"` |
| `str` | `str`; `bytes` are **not** accepted in strict; numbers are **never** coerced to `str` by default (use `coerce_numbers_to_str` config) |
| `bytes` | `bytes`, `bytearray`, `str` |
| `Decimal` | `Decimal`, `int`, `float`, `str`, and (2.13+) a `(sign, digits, exponent)` tuple |
| `complex` | anything `complex()` accepts (2.13+ defers to the constructor) |
| `fractions.Fraction` | native in `pydantic-core` since 2.14 |
| `None` / `NoneType` | only `None` |

The authoritative reference is the **conversion table** in the docs, which lists every (type, input, mode) combination.

### Dates and times

```python
from datetime import date, datetime, time, timedelta
from pydantic import AwareDatetime, BaseModel, FutureDate, NaiveDatetime, PastDatetime


class Booking(BaseModel):
    day: date                  # "2026-10-15", date objects, unix timestamps (int)
    starts: AwareDatetime      # must include a timezone
    local: NaiveDatetime       # must NOT include a timezone
    duration: timedelta        # "PT1H30M" (ISO 8601), "01:30:00", seconds as number
    at: time
    created: PastDatetime
    due: FutureDate


b = Booking(
    day="2026-10-15",
    starts="2026-10-15T09:00:00+02:00",
    local="2026-10-15T09:00:00",
    duration="PT1H30M",
    at="09:00",
    created="2020-01-01T00:00:00",
    due="2999-01-01",
)
print(b.duration, b.starts.utcoffset())
#> 1:30:00 2:00:00
```

Related config: `ser_json_temporal` / `val_temporal_unit` (2.12+) control how temporal values are (de)serialized as numbers vs. ISO strings, and `ser_json_timedelta` controls timedelta JSON output.

### Collections

| Annotation | Notes |
|---|---|
| `list[T]`, `tuple[T, ...]`, `set[T]`, `frozenset[T]` | Accept lists, tuples, sets, generators (lax) |
| `tuple[int, str]` | Fixed-length, positional types |
| `dict[K, V]`, `Mapping[K, V]` | Keys and values validated |
| `Sequence[T]`, `Iterable[T]` | `Iterable` is validated **lazily** as consumed |
| `collections.deque`, `OrderedDict`, `Counter`, `defaultdict` | `deque`/`OrderedDict`/`Counter` are native core types since 2.14 |
| `frozendict[K, V]` | Python 3.15+, supported since 2.14 |
| `typing.NamedTuple`, `typing.TypedDict` | Field-level validation; `TypedDict` supports `Required`/`NotRequired`/`ReadOnly`, PEP 728 `closed`/`extra_items` |

```python
from typing import NamedTuple, NotRequired, TypedDict
from pydantic import TypeAdapter


class Coord(NamedTuple):
    lat: float
    lon: float


class Movie(TypedDict):
    title: str
    year: int
    rating: NotRequired[float]


print(TypeAdapter(Coord).validate_python(("51.5", "-0.12")))
#> Coord(lat=51.5, lon=-0.12)
print(TypeAdapter(list[Movie]).validate_python([{"title": "Alien", "year": "1979"}]))
#> [{'title': 'Alien', 'year': 1979}]
```

### Literal and Enum

```python
from enum import Enum, IntEnum
from typing import Literal
from pydantic import BaseModel


class Color(str, Enum):
    RED = "red"
    GREEN = "green"


class Priority(IntEnum):
    LOW = 1
    HIGH = 2


class Ticket(BaseModel):
    status: Literal["open", "closed"]
    color: Color
    priority: Priority


t = Ticket(status="open", color="red", priority=2)
print(t.color is Color.RED, repr(t.priority))
#> True <Priority.HIGH: 2>
print(t.model_dump(), t.model_dump(mode="json"))
#> {'status': 'open', 'color': <Color.RED: 'red'>, 'priority': <Priority.HIGH: 2>} {'status': 'open', 'color': 'red', 'priority': 2}
```

Set `use_enum_values=True` in config to store the raw `.value` instead of the enum member.

### Pydantic's own types

| Type | What it does |
|---|---|
| `EmailStr`, `NameEmail` | Email validation (requires `email-validator`) |
| `AnyUrl`, `HttpUrl`, `AnyHttpUrl`, `FileUrl`, `WebsocketUrl`… | URL parsing into a `Url` object with `.scheme`, `.host`, `.path`… |
| `PostgresDsn`, `RedisDsn`, `MongoDsn`, `KafkaDsn`, `MySQLDsn`… | Database/broker DSNs (`MultiHostUrl` where appropriate) |
| `IPvAnyAddress`, `IPvAnyNetwork`, `IPvAnyInterface` | IPv4/IPv6 |
| `SecretStr`, `SecretBytes`, `Secret[T]` | Masked in `repr`/dumps; `.get_secret_value()` to read; constant-time `==` (2.14+) |
| `PositiveInt`, `NegativeFloat`, `NonNegativeInt`, `FiniteFloat`… | Pre-constrained numerics |
| `UUID1`, `UUID4`, `UUID7`… | UUID with version check |
| `FilePath`, `DirectoryPath`, `NewPath`, `SocketPath` | Path that must (not) exist |
| `Json[T]` | Field arrives as a JSON **string** and is parsed into `T` |
| `ByteSize` | `"1.5 GiB"` → int bytes with `.human_readable()` |
| `Base64Str`, `Base64Bytes`, `Base64UrlStr`… | Base64 encode/decode |
| `ImportString` | `"math.cos"` → the imported object |
| `PaymentCardNumber` | deprecated; use `pydantic_extra_types.payment` |
| `ZoneInfo`, `Pattern`, `Path`, `UUID`, `IPv4Address`… | Standard library types |

```python
from pydantic import BaseModel, ByteSize, EmailStr, HttpUrl, Json, SecretStr


class Account(BaseModel):
    email: EmailStr
    homepage: HttpUrl
    password: SecretStr
    quota: ByteSize
    prefs: Json[dict[str, bool]]


a = Account(
    email="ADA@Example.com",
    homepage="https://example.com/ada",
    password="hunter2",
    quota="1.5 GiB",
    prefs='{"dark_mode": true}',
)
print(a.email, a.homepage.host, a.password, a.quota, a.prefs)
#> ADA@example.com example.com ********** 1610612736 {'dark_mode': True}
print(a.password.get_secret_value())
#> hunter2
```

`pydantic-extra-types` adds `Color`, `CountryAlpha2`, `PhoneNumber`, `Coordinate`, `MacAddress`, `ISBN`, `CurrencyCode`, `LanguageAlpha2`, `SemanticVersion`, `TimeZoneName`, `ULID`, `Pendulum` types and more.

### `Any`, `object`, and `InstanceOf`

```python
from typing import Any
from pydantic import BaseModel, ConfigDict, InstanceOf


class Engine:
    pass


class Car(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    payload: Any            # anything, unvalidated
    engine: Engine          # arbitrary class: isinstance check only (needs arbitrary_types_allowed)
    other: InstanceOf[Engine]  # explicit isinstance check; works without the config flag


print(Car(payload={"x": 1}, engine=Engine(), other=Engine()).payload)
#> {'x': 1}
```

## 4. The `MISSING` sentinel (stable in 2.14)

`None` means "explicitly null"; sometimes you need a third state: "not provided at all". `MISSING` is that state. Fields holding `MISSING` are **omitted from serialization** and not shown in JSON Schema.

```python
from pydantic import MISSING, BaseModel


class PatchUser(BaseModel):
    name: str | MISSING = MISSING
    bio: str | None | MISSING = MISSING      # three states: value, null, absent


p = PatchUser(bio=None)
print(p.model_dump())
#> {'bio': None}
print(p.name is MISSING)
#> True
```

This is cleaner than relying on `exclude_unset` for PATCH-style models because the "absent" state is part of the *type*. Static type checkers understand `MISSING` from pyright 1.1.414 / mypy 2.4.

## 5. Field ordering, `kw_only`, and `init`

Models are keyword-only at construction. Fields keep declaration order (parents first) in dumps and schemas. `init=False` / `init_var` / `kw_only` matter mostly for **Pydantic dataclasses** (chapter 08).

## 6. Computed fields

A `@computed_field` is a property that is **included in serialization and JSON Schema** (serialization mode):

```python
from functools import cached_property
from pydantic import BaseModel, computed_field


class Rectangle(BaseModel):
    width: float
    height: float

    @computed_field
    @property
    def area(self) -> float:
        return self.width * self.height

    @computed_field(exclude_if=lambda v: v is False)  # exclude_if on computed fields: 2.13+
    @cached_property
    def is_square(self) -> bool:
        return self.width == self.height


print(Rectangle(width=2, height=3).model_dump())
#> {'width': 2.0, 'height': 3.0, 'area': 6.0}
print(Rectangle(width=2, height=2).model_dump())
#> {'width': 2.0, 'height': 2.0, 'area': 4.0, 'is_square': True}
```

Always give computed fields a **return annotation** — Pydantic uses it for serialization and schema.

---

## Summary

- `Field()` sets defaults, constraints, aliases, docs and behavior for one field.
- Prefer `Annotated[T, ...]` to build reusable constrained types and to constrain *items* of containers.
- Pydantic supports nearly all standard-library types plus a rich set of its own (`EmailStr`, `HttpUrl`, `SecretStr`, `Json[T]` …).
- `MISSING` (stable since 2.14) models "not provided" distinctly from `None`.
- `@computed_field` exposes derived properties in dumps and schemas.

**Next:** [04 — Validators](04-validators.md)
