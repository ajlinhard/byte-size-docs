# 05 — Serialization

> **Level:** Beginner → Intermediate · **Prerequisite:** [04 — Validators](04-validators.md)

Validation turns external data **into** models. Serialization turns models **back out** — to Python dicts, JSON strings, API responses, files, message queues. Pydantic's serializer is also implemented in Rust and is highly configurable.

---

## 1. `model_dump` and `model_dump_json`

```python
from datetime import datetime
from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel


class Payment(BaseModel):
    id: UUID
    amount: Decimal
    paid_at: datetime
    note: str | None = None


p = Payment(id="12345678-1234-5678-1234-567812345678", amount="19.99", paid_at="2026-10-15T10:00:00Z")

print(p.model_dump())                 # Python mode: keeps rich Python objects
#> {'id': UUID('12345678-1234-5678-1234-567812345678'), 'amount': Decimal('19.99'), 'paid_at': datetime.datetime(2026, 10, 15, 10, 0, tzinfo=TzInfo(0)), 'note': None}

print(p.model_dump(mode="json"))      # JSON-compatible Python primitives
#> {'id': '12345678-1234-5678-1234-567812345678', 'amount': '19.99', 'paid_at': '2026-10-15T10:00:00Z', 'note': None}

print(p.model_dump_json(indent=2))    # a JSON string, produced directly in Rust
```

| Method | Returns | Use for |
|---|---|---|
| `model_dump()` | `dict` with Python objects | passing to other Python code, ORMs |
| `model_dump(mode="json")` | `dict` with JSON-safe values | `json.dumps` with extra options, templating, YAML |
| `model_dump_json()` | `str` | HTTP responses, files, queues — **fastest path to JSON** |

> Avoid `json.dumps(m.model_dump())` — it fails on `datetime`, `UUID`, `Decimal`. Use `model_dump_json()` or `mode="json"`.

## 2. Selecting what to output

All of these work for both `model_dump` and `model_dump_json`:

| Argument | Effect |
|---|---|
| `include` / `exclude` | sets or nested dicts of fields to keep / drop |
| `exclude_unset=True` | only fields explicitly provided at creation (or assigned) |
| `exclude_defaults=True` | drop fields equal to their default |
| `exclude_none=True` | drop fields whose value is `None` |
| `exclude_computed_fields=True` | drop `@computed_field`s (2.12+) |
| `by_alias=True` | use serialization aliases as keys |
| `round_trip=True` | output that can be re-validated into the same model (e.g. `Json[T]` re-encoded) |
| `serialize_as_any=True` | serialize every value by its runtime type (duck-typing) |
| `polymorphic_serialization=True` | serialize model *subclass* instances with all their fields (2.13+) |
| `warnings=` | `True`/`'warn'`, `'error'`, or `False` for serialization type warnings |
| `fallback=` | callable for values the serializer doesn't know |
| `context=` | arbitrary data available to custom serializers |

```python
from pydantic import BaseModel


class Address(BaseModel):
    city: str
    zip: str
    secret_note: str = ""


class User(BaseModel):
    id: int
    name: str
    email: str | None = None
    address: Address
    role: str = "member"


u = User(id=1, name="Ada", address={"city": "London", "zip": "N1"})

print(u.model_dump(exclude={"address": {"secret_note"}}, exclude_none=True))
#> {'id': 1, 'name': 'Ada', 'address': {'city': 'London', 'zip': 'N1'}, 'role': 'member'}

print(u.model_dump(include={"id": True, "address": {"city"}}))
#> {'id': 1, 'address': {'city': 'London'}}

print(u.model_dump(exclude_unset=True))      # PATCH-friendly
#> {'id': 1, 'name': 'Ada', 'address': {'city': 'London', 'zip': 'N1'}}

print(u.model_dump(exclude_defaults=True))
#> {'id': 1, 'name': 'Ada', 'address': {'city': 'London', 'zip': 'N1'}}
```

For list fields, `include`/`exclude` accept integer indices or `"__all__"`: `exclude={"items": {"__all__": {"internal_id"}}}`.

### Field-level exclusion

```python
from pydantic import BaseModel, Field


class Account(BaseModel):
    username: str
    password_hash: str = Field(exclude=True)              # never serialized
    nickname: str | None = Field(default=None, exclude_if=lambda v: v is None)  # 2.12+


print(Account(username="ada", password_hash="xyz").model_dump())
#> {'username': 'ada'}
```

## 3. Aliases

Aliases decouple **Python attribute names** from **external key names** (camelCase APIs, legacy schemas, reserved words).

```python
from pydantic import AliasChoices, AliasPath, BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class Customer(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,     # first_name ↔ firstName for everything…
        validate_by_name=True,        # …but also accept snake_case input
        serialize_by_alias=True,      # dump with aliases by default (2.11+)
    )

    first_name: str
    last_name: str
    # override: accept several input keys, serialize as "mail"
    email: str = Field(validation_alias=AliasChoices("email", "mail", "e_mail"), serialization_alias="mail")
    # pull a nested value out of the input: {"meta": {"tier": [ "gold" ]}}
    tier: str = Field(validation_alias=AliasPath("meta", "tier", 0))


c = Customer.model_validate(
    {"firstName": "Ada", "last_name": "Lovelace", "e_mail": "ada@x.org", "meta": {"tier": ["gold"]}}
)
print(c.first_name, c.email, c.tier)
#> Ada ada@x.org gold
print(c.model_dump())
#> {'firstName': 'Ada', 'lastName': 'Lovelace', 'mail': 'ada@x.org', 'tier': 'gold'}
print(c.model_dump(by_alias=False))
#> {'first_name': 'Ada', 'last_name': 'Lovelace', 'email': 'ada@x.org', 'tier': 'gold'}
```

| Setting | Meaning |
|---|---|
| `alias` | used for **both** validation and serialization |
| `validation_alias` | input only; may be `str`, `AliasPath`, or `AliasChoices` |
| `serialization_alias` | output only |
| `alias_generator` | function or `AliasGenerator(validation_alias=..., serialization_alias=...)` applied to all fields |
| `validate_by_alias` (default `True`) / `validate_by_name` (default `False`) | which input keys are accepted (2.11+, replaces `populate_by_name`) |
| `serialize_by_alias` (default `False`) | whether dumps use aliases by default (2.11+) |

Built-in generators: `to_camel`, `to_pascal`, `to_snake` in `pydantic.alias_generators`.

## 4. Custom serializers

### Field serializers

```python
from datetime import datetime, timezone
from decimal import Decimal
from pydantic import BaseModel, field_serializer


class Invoice(BaseModel):
    total: Decimal
    issued: datetime

    @field_serializer("total")
    def money(self, v: Decimal) -> str:
        return f"${v:,.2f}"

    @field_serializer("issued", when_used="json")   # only in JSON mode
    def epoch(self, v: datetime) -> int:
        return int(v.timestamp())


inv = Invoice(total="1234.5", issued=datetime(2026, 10, 15, tzinfo=timezone.utc))
print(inv.model_dump())
#> {'total': '$1,234.50', 'issued': datetime.datetime(2026, 10, 15, 0, 0, tzinfo=datetime.timezone.utc)}
print(inv.model_dump_json())
#> {"total":"$1,234.50","issued":1792022400}
```

`when_used` options: `'always'` (default), `'unless-none'`, `'json'`, `'json-unless-none'`.

Like validators, serializers come in **plain** (default — replaces the output) and **wrap** modes (receive a `handler` for the default output):

```python
from typing import Any
from pydantic import BaseModel, SerializerFunctionWrapHandler, field_serializer


class Reading(BaseModel):
    values: list[float]

    @field_serializer("values", mode="wrap")
    def rounded(self, v: list[float], handler: SerializerFunctionWrapHandler) -> Any:
        return [round(x, 1) for x in handler(v)]


print(Reading(values=[1.234, 5.678]).model_dump())
#> {'values': [1.2, 5.7]}
```

### Annotated serializers (reusable)

```python
from decimal import Decimal
from typing import Annotated
from pydantic import BaseModel, PlainSerializer

Money = Annotated[Decimal, PlainSerializer(lambda v: f"{v:.2f}", return_type=str, when_used="json")]


class Cart(BaseModel):
    subtotal: Money
    tax: Money


print(Cart(subtotal="10", tax="0.825").model_dump_json())
#> {"subtotal":"10.00","tax":"0.82"}
```

`WrapSerializer` is the wrap-mode equivalent. Supplying `return_type` keeps the JSON Schema (serialization mode) accurate.

### Model serializers

Take full control of a model's output shape:

```python
from typing import Any
from pydantic import BaseModel, SerializerFunctionWrapHandler, model_serializer


class Envelope(BaseModel):
    kind: str
    payload: dict

    @model_serializer(mode="wrap")
    def add_version(self, handler: SerializerFunctionWrapHandler) -> dict[str, Any]:
        data = handler(self)          # default serialization
        data["schema_version"] = 2
        return data


print(Envelope(kind="ping", payload={}).model_dump())
#> {'kind': 'ping', 'payload': {}, 'schema_version': 2}
```

> Since 2.14, calling `handler(self, info)` (passing a second, non-`int`/`str` argument) raises an error; call `handler(self)`.

### Serialization context

```python
from pydantic import BaseModel, SerializationInfo, field_serializer


class Profile(BaseModel):
    email: str

    @field_serializer("email")
    def mask(self, v: str, info: SerializationInfo) -> str:
        if (info.context or {}).get("public"):
            user, _, domain = v.partition("@")
            return f"{user[0]}***@{domain}"
        return v


print(Profile(email="ada@x.org").model_dump(context={"public": True}))
#> {'email': 'a***@x.org'}
```

## 5. Subclasses and polymorphism

By default, a field annotated with a **parent** model is serialized using the **parent's** fields, even if the value is a subclass instance. This is deliberate: it prevents leaking data (e.g. a password on a subclass).

```python
from pydantic import BaseModel, SerializeAsAny


class User(BaseModel):
    name: str


class UserLogin(User):
    password: str


class Outer(BaseModel):
    user: User


o = Outer(user=UserLogin(name="pydantic", password="pw"))
print(o.model_dump())
#> {'user': {'name': 'pydantic'}}
print(o.model_dump(polymorphic_serialization=True))   # 2.13+: subclass-aware for models/dataclasses
#> {'user': {'name': 'pydantic', 'password': 'pw'}}


class OuterAny(BaseModel):
    user: SerializeAsAny[User]                         # opt in per field


print(OuterAny(user=UserLogin(name="p", password="pw")).model_dump())
#> {'user': {'name': 'p', 'password': 'pw'}}
```

- `polymorphic_serialization` (2.13+) is the recommended switch when you want "serialize the actual subclass" for **models and dataclasses**.
- `serialize_as_any` / `SerializeAsAny` is broader: duck-type serialization for **all** values.

## 6. Pickling, copying, and `__repr__`

- Models are picklable (if their field values are).
- `repr=False` on `Field()` hides a field from `repr()` (useful for large blobs).
- `__repr_args__` can be overridden for fully custom reprs.

## 7. Round-tripping and stable contracts

When serialized data must be validated again (caches, queues, event sourcing):

```python
from pydantic import BaseModel, Json


class Cached(BaseModel):
    raw: Json[list[int]]


c = Cached(raw="[1, 2]")
print(c.model_dump())                    # parsed value
#> {'raw': [1, 2]}
dumped = c.model_dump_json(round_trip=True)
print(dumped)                            # re-encoded as a JSON string, so it validates back
#> {"raw":"[1,2]"}
assert Cached.model_validate_json(dumped) == c
```

---

## Summary

- `model_dump()` → Python objects; `model_dump(mode="json")` → JSON-safe dict; `model_dump_json()` → JSON string (fastest).
- Select output with `include`/`exclude`, `exclude_unset`/`_defaults`/`_none`, `Field(exclude=...)`, `exclude_if`.
- Aliases map Python names ↔ external keys; `alias_generator=to_camel` + `validate_by_name` + `serialize_by_alias` is a common API setup.
- Customize with `@field_serializer`, `@model_serializer`, `PlainSerializer`, `WrapSerializer`.
- Subclass instances serialize as their declared type unless you use `polymorphic_serialization` or `SerializeAsAny`.

**Next:** [06 — Configuration and Strict Mode](06-configuration-and-strict-mode.md)
