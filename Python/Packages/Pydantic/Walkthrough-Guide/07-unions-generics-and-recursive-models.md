# 07 — Unions, Generics, and Recursive Models

> **Level:** Intermediate → Advanced · **Prerequisite:** [06 — Configuration and Strict Mode](06-configuration-and-strict-mode.md)

Real-world data is polymorphic ("a payment is a card *or* a bank transfer *or* a voucher"), reusable ("a paginated response of *anything*"), and often recursive ("a comment has replies, which are comments"). This chapter covers the tools Pydantic gives you for each.

---

## 1. Unions

### Smart mode (the default)

For `A | B | C`, Pydantic's **smart** mode:

1. Tries every member in **strict** mode; if exactly one succeeds — or one matches the input type *exactly* — it wins.
2. Otherwise tries members in **lax** mode, and if several succeed, picks the one that validated the most fields (for models/dataclasses/TypedDicts) or the first successful one.
3. If all fail, reports the errors from every member.

```python
from uuid import UUID
from pydantic import BaseModel


class M(BaseModel):
    ident: int | str | UUID


print(repr(M(ident=123).ident))
#> 123
print(repr(M(ident="123").ident))          # str is an exact match → stays a str
#> '123'
print(repr(M(ident=UUID(int=1)).ident))
#> UUID('00000000-0000-0000-0000-000000000001')
```

### Left-to-right mode

```python
from pydantic import BaseModel, Field


class M(BaseModel):
    value: int | str = Field(union_mode="left_to_right")


print(repr(M(value="123").value))          # int is tried first and lax-coerces "123"
#> 123
```

Use left-to-right only when you want explicit priority ordering.

### Why unions of models get slow — and ambiguous

With `Cat | Dog | Lizard`, Pydantic may have to try every model on every input. Errors become noisy (one block per member), and if two models share fields the "wrong" one may match. The solution is **discriminated unions**.

## 2. Discriminated (tagged) unions

If each member has a `Literal` field with a unique value, tell Pydantic to dispatch on it:

```python
from typing import Annotated, Literal
from pydantic import BaseModel, Field, ValidationError


class Card(BaseModel):
    method: Literal["card"]
    number: str
    cvv: str


class BankTransfer(BaseModel):
    method: Literal["bank"]
    iban: str


class Voucher(BaseModel):
    method: Literal["voucher"]
    code: str


Payment = Annotated[Card | BankTransfer | Voucher, Field(discriminator="method")]


class Checkout(BaseModel):
    amount: float
    payment: Payment


c = Checkout.model_validate({"amount": 10, "payment": {"method": "bank", "iban": "DE89..."}})
print(type(c.payment).__name__)
#> BankTransfer

try:
    Checkout.model_validate({"amount": 10, "payment": {"method": "bank"}})
except ValidationError as e:
    print(e.errors()[0]["loc"])   # error points into the selected member only
    #> ('payment', 'bank', 'iban')

try:
    Checkout.model_validate({"amount": 10, "payment": {"method": "crypto"}})
except ValidationError as e:
    print(e.errors()[0]["type"])
    #> union_tag_invalid
```

Benefits: **O(1) dispatch**, precise errors, and a JSON Schema with `oneOf` + `discriminator.mapping` (which OpenAPI tooling and code generators understand).

The discriminator field can be a `Literal` of several values, an `Enum` member, or (2.13+) a `RootModel` with a `Literal` root. Discriminated unions can be **nested** (dispatch on `kind`, then on `subtype`).

### Callable discriminators

When there's no literal tag — or the tag lives somewhere unusual — compute it:

```python
from typing import Annotated, Any
from pydantic import BaseModel, Discriminator, Tag


class Circle(BaseModel):
    radius: float


class Rect(BaseModel):
    width: float
    height: float


def shape_tag(v: Any) -> str | None:
    if isinstance(v, dict):
        return "circle" if "radius" in v else "rect" if "width" in v else None
    return "circle" if isinstance(v, Circle) else "rect" if isinstance(v, Rect) else None


Shape = Annotated[
    Annotated[Circle, Tag("circle")] | Annotated[Rect, Tag("rect")],
    Discriminator(shape_tag),
]


class Drawing(BaseModel):
    shapes: list[Shape]


d = Drawing(shapes=[{"radius": 1}, {"width": 2, "height": 3}])
print([type(s).__name__ for s in d.shapes])
#> ['Circle', 'Rect']
```

Callable discriminators are also great for unions mixing models and primitives (e.g. `str | Config`).

## 3. Generic models

Generic models let you parametrize a model with types, just like `list[T]`.

```python
from typing import Generic, TypeVar
from pydantic import BaseModel

T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int = 1

    @property
    def has_next(self) -> bool:
        return self.page * len(self.items) < self.total


class User(BaseModel):
    id: int
    name: str


users = Page[User].model_validate({"items": [{"id": "1", "name": "Ada"}], "total": 10})
print(users.items[0], users.has_next)
#> id=1 name='Ada' True
print(Page[int](items=["1", "2"], total=2).items)
#> [1, 2]
print(Page[User].__name__)
#> Page[User]
```

### PEP 695 syntax (Python 3.12+)

```python
from pydantic import BaseModel


class Envelope[T](BaseModel):
    data: T
    error: str | None = None


print(Envelope[list[int]](data=["1", 2]).data)
#> [1, 2]
```

### Details worth knowing

- **Unparametrized** usage (`Page(items=...)`) treats `T` as its bound/constraints or `Any` — no validation of items. Parametrize to get validation.
- `TypeVar` **bounds, constraints, and defaults** (PEP 696) are respected: `T = TypeVar("T", bound=BaseModel)`.
- Partial parametrization works: `class Pair(BaseModel, Generic[K, V])` → `Pair[str, V]`.
- Subclass a parametrized generic to give it a nicer name: `class UserPage(Page[User]): ...`.
- Generic models combine with discriminated unions: `Page[Card | BankTransfer]`.
- Parametrized classes are cached, so `Page[User] is Page[User]`.

### Generic `RootModel` and `TypeAdapter`

```python
from typing import TypeVar
from pydantic import RootModel, TypeAdapter

T = TypeVar("T")


class Batch(RootModel[list[T]]):
    pass


print(Batch[int].model_validate(["1", "2"]).root)
#> [1, 2]
print(TypeAdapter(dict[str, list[int]]).validate_python({"a": ("1",)}))
#> {'a': [1]}
```

## 4. Recursive models and type aliases

### Self-referencing models

```python
from __future__ import annotations
from pydantic import BaseModel


class Comment(BaseModel):
    author: str
    text: str
    replies: list[Comment] = []

    def count(self) -> int:
        return 1 + sum(r.count() for r in self.replies)


thread = Comment.model_validate(
    {"author": "a", "text": "hi", "replies": [{"author": "b", "text": "yo", "replies": [{"author": "c", "text": "!"}]}]}
)
print(thread.count())
#> 3
schema = Comment.model_json_schema()      # recursion is expressed with $defs + $ref
print(schema["$ref"], schema["$defs"]["Comment"]["properties"]["replies"]["items"])
#> #/$defs/Comment {'$ref': '#/$defs/Comment'}
```

### Mutually recursive models across modules

Use string annotations / `from __future__ import annotations` and call `model_rebuild()` on the incomplete model once all types exist, or (Python 3.15+) `lazy from .other import Model`, supported since Pydantic 2.14.

### Recursive type aliases (`type` statement, Python 3.12+)

```python
from pydantic import TypeAdapter

type JSONValue = None | bool | int | float | str | list[JSONValue] | dict[str, JSONValue]

ta = TypeAdapter(JSONValue)
print(ta.validate_python({"a": [1, 2.5, None, {"b": True}]}))
#> {'a': [1, 2.5, None, {'b': True}]}
```

For older Python, use `typing_extensions.TypeAliasType("JSONValue", ...)`. Pydantic also ships `pydantic.JsonValue` for exactly this purpose.

### Cyclic *data*

Recursive *types* are fine, but cyclic *data* (an object that contains itself) raises a `recursion_loop` validation error rather than looping forever. Serialization of cyclic objects likewise errors out.

## 5. Putting it together: an event system

```python
from datetime import datetime
from typing import Annotated, Generic, Literal, TypeVar
from pydantic import BaseModel, Field

P = TypeVar("P", bound=BaseModel)


class UserCreated(BaseModel):
    type: Literal["user.created"] = "user.created"
    user_id: int
    email: str


class OrderPlaced(BaseModel):
    type: Literal["order.placed"] = "order.placed"
    order_id: int
    total: float


class Envelope(BaseModel, Generic[P]):
    id: str
    occurred_at: datetime
    payload: P


AnyEvent = Annotated[UserCreated | OrderPlaced, Field(discriminator="type")]
IncomingEnvelope = Envelope[AnyEvent]

msg = IncomingEnvelope.model_validate_json(
    '{"id": "evt_1", "occurred_at": "2026-10-15T08:00:00Z",'
    ' "payload": {"type": "order.placed", "order_id": 42, "total": 99.5}}'
)

match msg.payload:
    case OrderPlaced(order_id=oid, total=t):
        print(f"order {oid}: {t}")
    case UserCreated(user_id=uid):
        print(f"user {uid}")
#> order 42: 99.5
```

Pydantic models work with structural pattern matching (`match`/`case`) out of the box, which pairs naturally with discriminated unions.

---

## Summary

- Default **smart** unions prefer exact type matches; `union_mode="left_to_right"` gives priority ordering.
- Use **discriminated unions** (`Field(discriminator=...)` or `Discriminator(callable)` + `Tag`) for model unions: faster, clearer errors, better schemas.
- **Generic models** (`BaseModel, Generic[T]` or `class M[T](BaseModel)`) build reusable containers like pages and envelopes.
- Recursive models and recursive `type` aliases are supported; use `model_rebuild()` for cross-module references.

**Next:** [08 — TypeAdapter, Dataclasses, and `@validate_call`](08-typeadapter-dataclasses-validate-call.md)
