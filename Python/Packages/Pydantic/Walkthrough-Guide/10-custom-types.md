# 10 — Custom Types and the `Annotated` Pattern

> **Level:** Advanced · **Prerequisite:** [09 — JSON Schema](09-json-schema.md)

Sooner or later you will want Pydantic to understand a type it doesn't know: a `Money` value object, a third-party class (`numpy.ndarray`, `bson.ObjectId`, `pendulum.DateTime`), or a domain concept with rules and a specific wire format. This chapter goes from the simplest technique to full control over the generated core schema.

---

## Ladder of techniques

| # | Technique | Effort | Use when |
|---|---|---|---|
| 1 | `Annotated[T, Field/constraints]` | trivial | constrained versions of known types |
| 2 | `Annotated[T, *Validator, *Serializer]` | low | custom parsing/formatting of a known underlying type |
| 3 | `Annotated[T, WithJsonSchema(...)]` | low | fix the schema of 1–2 |
| 4 | `__get_pydantic_core_schema__` on **your** class | medium | domain classes that should "just work" anywhere |
| 5 | Annotated *marker class* with `__get_pydantic_core_schema__` | medium | adapting **third-party** classes you can't modify |
| 6 | `GetPydanticSchema` | low-medium | one-off inline core-schema customization |

Techniques 1–3 were covered in chapters 03–05 and 09. This chapter focuses on 4–6.

---

## 1. Recap: composing annotated types

```python
import re
from typing import Annotated
from pydantic import AfterValidator, BeforeValidator, Field, PlainSerializer, TypeAdapter, WithJsonSchema

_ISBN13 = re.compile(r"^97[89]\d{10}$")


def _normalize(v: object) -> object:
    return v.replace("-", "").replace(" ", "") if isinstance(v, str) else v


def _checksum(v: str) -> str:
    total = sum((3 if i % 2 else 1) * int(d) for i, d in enumerate(v[:12]))
    if (10 - total % 10) % 10 != int(v[12]):
        raise ValueError("invalid ISBN-13 checksum")
    return v


ISBN13 = Annotated[
    str,
    BeforeValidator(_normalize),
    Field(pattern=_ISBN13.pattern),
    AfterValidator(_checksum),
    PlainSerializer(lambda v: f"{v[:3]}-{v[3]}-{v[4:6]}-{v[6:12]}-{v[12]}", return_type=str),
    WithJsonSchema({"type": "string", "format": "isbn13", "examples": ["978-0-13-468599-1"]}),
]

ta = TypeAdapter(ISBN13)
v = ta.validate_python("978 0134685991")
print(v, ta.dump_python(v))
#> 9780134685991 978-0-13-468599-1
```

This covers the majority of real-world custom types — prefer it whenever the value can be represented by an existing type (`str`, `int`, `Decimal`…).

## 2. Background: what a core schema is

Pydantic works in two phases (detailed in [11 — Internals](11-internals.md)):

1. **Schema generation (Python):** inspects your annotations and builds a **core schema** — a nested dict describing how to validate and serialize (e.g. `{'type': 'int', 'gt': 0}`).
2. **Execution (Rust):** `pydantic-core` compiles the core schema into a `SchemaValidator` and `SchemaSerializer`.

Custom types plug into phase 1 by **returning a core schema** — built with helpers from `pydantic_core.core_schema`.

```python
from pydantic import TypeAdapter

print(TypeAdapter(int).core_schema)
#> {'type': 'int'}
```

## 3. Your own class: `__get_pydantic_core_schema__`

A value object that validates from a string or a dict, serializes to a string, and has a proper JSON Schema:

```python
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, GetCoreSchemaHandler, GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema


class Money:
    __slots__ = ("amount", "currency")

    def __init__(self, amount: Decimal, currency: str):
        self.amount = amount
        self.currency = currency

    def __repr__(self) -> str:
        return f"Money({self.amount} {self.currency})"

    def __str__(self) -> str:
        return f"{self.amount:.2f} {self.currency}"

    # ---- Pydantic integration -------------------------------------------
    @classmethod
    def _from_str(cls, value: str) -> "Money":
        try:
            amount, currency = value.split()
            return cls(Decimal(amount), currency.upper())
        except Exception as exc:
            raise ValueError("expected '<amount> <CUR>'") from exc

    @classmethod
    def _from_dict(cls, value: dict) -> "Money":
        return cls(Decimal(str(value["amount"])), str(value["currency"]).upper())

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler: GetCoreSchemaHandler) -> core_schema.CoreSchema:
        from_str = core_schema.chain_schema(
            [core_schema.str_schema(), core_schema.no_info_plain_validator_function(cls._from_str)]
        )
        from_dict = core_schema.chain_schema(
            [
                core_schema.typed_dict_schema(
                    {
                        "amount": core_schema.typed_dict_field(core_schema.decimal_schema()),
                        "currency": core_schema.typed_dict_field(core_schema.str_schema(min_length=3, max_length=3)),
                    }
                ),
                core_schema.no_info_plain_validator_function(cls._from_dict),
            ]
        )
        return core_schema.json_or_python_schema(
            # JSON input: string or object
            json_schema=core_schema.union_schema([from_str, from_dict]),
            # Python input: existing Money instance, string, or dict
            python_schema=core_schema.union_schema(
                [core_schema.is_instance_schema(cls), from_str, from_dict]
            ),
            serialization=core_schema.to_string_ser_schema(),   # uses __str__
        )

    @classmethod
    def __get_pydantic_json_schema__(cls, schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler) -> JsonSchemaValue:
        return {"type": "string", "pattern": r"^\d+(\.\d+)? [A-Z]{3}$", "examples": ["12.50 USD"]}


class Order(BaseModel):
    total: Money
    shipping: Money


o = Order(total="99.90 usd", shipping={"amount": 5, "currency": "usd"})
print(repr(o.total), repr(o.shipping))
#> Money(99.90 USD) Money(5 USD)
print(o.model_dump_json())
#> {"total":"99.90 USD","shipping":"5.00 USD"}
print(Order.model_json_schema()["properties"]["total"])
#> {'examples': ['12.50 USD'], 'pattern': '^\\d+(\\.\\d+)? [A-Z]{3}$', 'title': 'Total', 'type': 'string'}
```

Key building blocks from `pydantic_core.core_schema`:

| Helper | Purpose |
|---|---|
| `str_schema()`, `int_schema()`, `decimal_schema()`, `list_schema(items)`… | built-in validators with constraints |
| `chain_schema([a, b])` | run `a`, feed its output into `b` |
| `union_schema([...])` | try alternatives |
| `json_or_python_schema(json_schema=, python_schema=)` | different rules per input mode |
| `is_instance_schema(cls)` | `isinstance` check |
| `no_info_plain_validator_function(fn)` / `with_info_...` | call a Python function (with/without `ValidationInfo`) |
| `no_info_after_validator_function(fn, schema)` | run `schema` then `fn` |
| `plain_serializer_function_ser_schema(fn, when_used=...)` | custom serialization |
| `to_string_ser_schema()` | serialize via `str()` |

### Delegating to the handler

`handler(SomeType)` asks Pydantic to generate the schema for another type — use it to **wrap** standard behavior rather than rebuild it:

```python
from typing import Any
from pydantic import BaseModel, GetCoreSchemaHandler
from pydantic_core import core_schema


class Username(str):
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler: GetCoreSchemaHandler) -> core_schema.CoreSchema:
        return core_schema.no_info_after_validator_function(
            lambda v: cls(v.lower()),
            handler(str),   # reuse Pydantic's normal str validation (and its JSON Schema)
        )


class Account(BaseModel):
    username: Username


a = Account(username="AdaL")
print(repr(a.username), type(a.username).__name__)
#> 'adal' Username
```

## 4. Third-party classes: annotated adapters

You can't add methods to `numpy.ndarray` or `bson.ObjectId`, but you can put a **marker** in `Annotated` that carries `__get_pydantic_core_schema__`. Here's the pattern with a stand-in third-party class:

```python
from typing import Annotated, Any
from pydantic import BaseModel, GetCoreSchemaHandler, GetJsonSchemaHandler
from pydantic_core import core_schema


class ThirdPartyId:                       # pretend this comes from a library
    def __init__(self, hex_value: str):
        if len(hex_value) != 24:
            raise ValueError("id must be 24 hex chars")
        int(hex_value, 16)
        self.hex = hex_value

    def __str__(self):
        return self.hex


class _ThirdPartyIdAnnotation:
    @classmethod
    def __get_pydantic_core_schema__(cls, _source: Any, _handler: GetCoreSchemaHandler) -> core_schema.CoreSchema:
        from_str = core_schema.no_info_after_validator_function(ThirdPartyId, core_schema.str_schema())
        return core_schema.json_or_python_schema(
            json_schema=from_str,
            python_schema=core_schema.union_schema([core_schema.is_instance_schema(ThirdPartyId), from_str]),
            serialization=core_schema.to_string_ser_schema(),
        )

    @classmethod
    def __get_pydantic_json_schema__(cls, _schema, handler: GetJsonSchemaHandler):
        return {"type": "string", "pattern": "^[0-9a-f]{24}$"}


PyObjectId = Annotated[ThirdPartyId, _ThirdPartyIdAnnotation]


class Document(BaseModel):
    id: PyObjectId


d = Document(id="65f1a2b3c4d5e6f708192a3b")
print(type(d.id).__name__, d.model_dump_json())
#> ThirdPartyId {"id":"65f1a2b3c4d5e6f708192a3b"}
```

This is exactly how libraries like Beanie (MongoDB) and `pydantic-extra-types` integrate external types.

### The quick inline version: `GetPydanticSchema`

```python
from typing import Annotated
from pydantic import BaseModel, GetPydanticSchema
from pydantic_core import core_schema


class Opaque:
    pass


class Holder(BaseModel):
    obj: Annotated[Opaque, GetPydanticSchema(lambda tp, handler: core_schema.is_instance_schema(Opaque))]


print(type(Holder(obj=Opaque()).obj).__name__)
#> Opaque
```

(For a plain `isinstance` check, `InstanceOf[Opaque]` is even simpler.)

## 5. Example: NumPy arrays

```py
from typing import Annotated, Any
import numpy as np
from pydantic import BaseModel, GetCoreSchemaHandler
from pydantic_core import core_schema


class _NDArray:
    @classmethod
    def __get_pydantic_core_schema__(cls, _s: Any, _h: GetCoreSchemaHandler):
        def to_array(v: Any) -> np.ndarray:
            return v if isinstance(v, np.ndarray) else np.asarray(v, dtype=float)

        return core_schema.no_info_plain_validator_function(
            to_array,
            serialization=core_schema.plain_serializer_function_ser_schema(lambda a: a.tolist()),
            json_schema_input_schema=core_schema.list_schema(core_schema.float_schema()),
        )


NDArray = Annotated[np.ndarray, _NDArray]


class Signal(BaseModel):
    samples: NDArray

print(Signal(samples=[1, 2, 3]).model_dump_json())   # {"samples":[1.0,2.0,3.0]}
```

## 6. Experimental: the pipeline API

`pydantic.experimental.pipeline` offers a fluent, type-safe way to declare transformations and constraints:

```python
from typing import Annotated
from pydantic import BaseModel
from pydantic.experimental.pipeline import validate_as


class Signup(BaseModel):
    username: Annotated[str, validate_as(str).str_strip().str_lower().len(3, 20)]
    age: Annotated[int, validate_as(int).ge(13).le(120)]


print(Signup(username="  AdaL  ", age="36"))
#> username='adal' age=36
```

Since 2.14 numeric constraints in the pipeline are applied natively by `pydantic-core` and appear in the JSON Schema. The API is still marked **experimental** — expect changes.

---

## Summary

- Prefer `Annotated` composition (validators + serializers + `WithJsonSchema`) for most custom types.
- Implement `__get_pydantic_core_schema__` (and optionally `__get_pydantic_json_schema__`) on your own classes to make them first-class Pydantic citizens.
- Wrap third-party classes with an annotation marker class, or `GetPydanticSchema` for one-offs.
- Use `handler(...)` to reuse built-in schemas instead of re-implementing them.

**Next:** [11 — Internals: How Pydantic Works](11-internals.md)
