# 02 — Models (`BaseModel`)

> **Level:** Beginner · **Prerequisite:** [01 — Introduction and Setup](01-introduction-and-setup.md)

A **model** is a class that inherits from `pydantic.BaseModel`. It is the primary way to define a data shape in Pydantic. This chapter covers how models are created, validated, inspected, copied, nested, inherited, and extended with private state.

---

## 1. Defining a model

```python
from pydantic import BaseModel


class Address(BaseModel):
    street: str
    city: str
    country: str = "US"


class Person(BaseModel):
    name: str
    age: int
    address: Address               # nested model
    tags: set[str] = set()
    nickname: str | None = None    # optional AND nullable


p = Person(
    name="Ada",
    age=36,
    address={"street": "1 Analytical Way", "city": "London", "country": "UK"},
)
print(p.address.city)
#> London
print(type(p.address))
#> <class '__main__.Address'>
```

Rules worth memorising:

| Declaration | Required? | Accepts `None`? |
|---|---|---|
| `x: int` | yes | no |
| `x: int = 0` | no | no |
| `x: int \| None` | **yes** (must be passed, may be `None`) | yes |
| `x: int \| None = None` | no | yes |

That third row surprises people coming from V1: `Optional[int]` / `int | None` **only means "nullable"**, it does *not* make the field optional. Only a default does.

## 2. Ways to create (validate) an instance

```python
from pydantic import BaseModel


class Point(BaseModel):
    x: int
    y: int


# 1) keyword arguments
a = Point(x=1, y=2)

# 2) from a dict (or any mapping / object, see from_attributes below)
b = Point.model_validate({"x": "1", "y": 2})

# 3) straight from JSON — parsing happens in Rust; faster than json.loads + model_validate
c = Point.model_validate_json('{"x": 1, "y": 2}')

# 4) from a dict whose values are all strings (query params, CSV rows, form data)
d = Point.model_validate_strings({"x": "1", "y": "2"})

assert a == b == c == d
```

### Prefer `model_validate_json` for JSON

`Point.model_validate(json.loads(raw))` parses into Python objects first, then validates. `model_validate_json(raw)` does both in one pass inside `pydantic-core` and is measurably faster; it also understands JSON-specific inputs (e.g. date strings in strict mode).

### Validating arbitrary objects (`from_attributes`)

To build a model from an ORM row, a dataclass, or any object with attributes, enable `from_attributes`:

```python
from pydantic import BaseModel, ConfigDict


class UserRow:                      # imagine a SQLAlchemy object
    def __init__(self):
        self.id = 7
        self.email = "a@b.com"
        self.password_hash = "secret"


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: str


print(UserOut.model_validate(UserRow()))
#> id=7 email='a@b.com'

# or per call, without changing config:
print(UserOut.model_validate(UserRow(), from_attributes=True).id)
#> 7
```

### Runtime validation options

`model_validate*` accepts per-call options:

- `strict=True` — disable coercion for this call.
- `from_attributes=True` — read attributes instead of keys.
- `context={...}` — pass arbitrary context to validators (see chapter 04).
- `by_alias=` / `by_name=` — control whether aliases and/or field names are accepted (2.11+).
- `extra='ignore' | 'allow' | 'forbid'` — override the extra-fields behavior for this call (2.12+).

```python
from pydantic import BaseModel, ValidationError


class M(BaseModel):
    a: int


try:
    M.model_validate({"a": 1, "unexpected": True}, extra="forbid")
except ValidationError as e:
    print(e.errors()[0]["type"])
    #> extra_forbidden
```

## 3. Inspecting models

```python
from pydantic import BaseModel, Field


class Product(BaseModel):
    sku: str
    price: float = Field(gt=0, description="Unit price in USD")
    stock: int = 0


print(list(Product.model_fields))
#> ['sku', 'price', 'stock']
info = Product.model_fields["price"]
print(info.annotation, info.is_required(), info.description)
#> <class 'float'> True Unit price in USD

p = Product(sku="A1", price=9.99)
print(sorted(p.model_fields_set))   # fields the caller explicitly supplied
#> ['price', 'sku']
```

`model_fields_set` is the key to *partial updates* (PATCH semantics): `p.model_dump(exclude_unset=True)` emits only the fields the client actually sent.

> **Note:** `model_fields` and `model_computed_fields` should be accessed on the **class**. Accessing them on instances was deprecated in 2.11.

## 4. Mutability, assignment, and equality

By default models are **mutable** and **assignment is not validated**:

```python
from pydantic import BaseModel, ConfigDict, ValidationError


class Loose(BaseModel):
    n: int


m = Loose(n=1)
m.n = "not an int"       # allowed! no validation on assignment by default
print(m.n)
#> not an int


class Careful(BaseModel):
    model_config = ConfigDict(validate_assignment=True)
    n: int


c = Careful(n=1)
c.n = "2"                # coerced
print(c.n)
#> 2
try:
    c.n = "nope"
except ValidationError as e:
    print(e.errors()[0]["type"])
    #> int_parsing


class Frozen(BaseModel):
    model_config = ConfigDict(frozen=True)
    n: int


f = Frozen(n=1)
print(hash(f) == hash(Frozen(n=1)))   # frozen models are hashable
#> True
```

**Equality:** two instances are equal if they are the same type and have the same field values, the same extra values, and the same private attribute values. Which fields were explicitly set (`model_fields_set`) does not matter. Comparing a model with a `dict` is always `False`.

## 5. Copying

```python
from pydantic import BaseModel


class Settings(BaseModel):
    host: str
    port: int
    tags: list[str] = []


base = Settings(host="localhost", port=8000)
prod = base.model_copy(update={"host": "api.example.com"})
print(prod)
#> host='api.example.com' port=8000 tags=[]

deep = base.model_copy(deep=True)
deep.tags.append("x")
print(base.tags)        # original untouched
#> []
```

⚠️ `model_copy(update=...)` **does not validate** the update values. If you need validation, do `Settings.model_validate(base.model_dump() | changes)`.

## 6. Nested models and collections of models

Nesting works recursively for any container type:

```python
from pydantic import BaseModel


class LineItem(BaseModel):
    product: str
    qty: int
    unit_price: float


class Invoice(BaseModel):
    number: str
    items: list[LineItem]
    metadata: dict[str, str] = {}

    @property
    def total(self) -> float:
        return sum(i.qty * i.unit_price for i in self.items)


inv = Invoice.model_validate_json(
    """{
        "number": "INV-001",
        "items": [
            {"product": "widget", "qty": 2, "unit_price": 3.5},
            {"product": "gadget", "qty": "1", "unit_price": "10"}
        ]
    }"""
)
print(inv.total)
#> 17.0
```

You can pass **model instances** instead of dicts too. By default an instance of the exact class is reused as-is (not re-validated); this is controlled by the `revalidate_instances` config (`'never'` default, `'always'`, `'subclass-instances'`).

## 7. Inheritance

Fields, config, and validators are inherited and can be overridden:

```python
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class TimestampedModel(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    created_at: datetime = datetime(2026, 1, 1)


class Article(TimestampedModel):
    title: str
    body: str


a = Article(title="  Hello  ", body="...")
print(repr(a.title), a.created_at.year)
#> 'Hello' 2026
print(list(Article.model_fields))   # parent fields come first
#> ['created_at', 'title', 'body']
```

Config dicts are **merged**: the child's `model_config` overrides keys from the parent's but keeps the rest. (Since 2.14, `model_config` always reflects exactly what you set, merged with parents — Pydantic no longer injects derived keys into it.)

## 8. Extra data

What happens to keys that don't correspond to fields? It's governed by the `extra` config:

| `extra=` | Behavior |
|---|---|
| `'ignore'` (default) | silently dropped |
| `'forbid'` | `ValidationError` (`extra_forbidden`) |
| `'allow'` | kept, accessible as attributes and in `model_extra` / dumps |

```python
from pydantic import BaseModel, ConfigDict


class Event(BaseModel):
    model_config = ConfigDict(extra="allow")
    name: str


e = Event(name="deploy", region="us-east-1", attempt=2)
print(e.region, e.model_extra)
#> us-east-1 {'region': 'us-east-1', 'attempt': 2}
print(e.model_dump())
#> {'name': 'deploy', 'region': 'us-east-1', 'attempt': 2}
```

You can also **type** the extras by annotating `__pydantic_extra__`:

```python
from pydantic import BaseModel, ConfigDict, Field


class Metrics(BaseModel):
    model_config = ConfigDict(extra="allow")
    __pydantic_extra__: dict[str, float] = Field(init=False)
    host: str


print(Metrics(host="db1", cpu="0.5", mem=0.75).model_extra)
#> {'cpu': 0.5, 'mem': 0.75}
```

## 9. Private attributes

Attributes whose names start with an underscore are **private**: not validated, not part of the schema, not serialized. Use them for caches, handles, and internal state.

```python
from datetime import datetime, timezone
from pydantic import BaseModel, PrivateAttr


class Session(BaseModel):
    user_id: int
    _created: datetime = PrivateAttr(default_factory=lambda: datetime.now(timezone.utc))
    _cache: dict = PrivateAttr(default_factory=dict)


s = Session(user_id=1)
s._cache["k"] = "v"
print(s.model_dump())
#> {'user_id': 1}
```

Since 2.13 a private attribute's `default_factory` can receive the **validated data**:

```python
from pydantic import BaseModel, PrivateAttr


class Model(BaseModel):
    foo: int
    _double: int = PrivateAttr(default_factory=lambda data: data["foo"] * 2)


print(Model(foo=21)._double)
#> 42
```

## 10. Post-init hook: `model_post_init`

Runs after validation, before the instance is returned — handy for initialising private state:

```python
from typing import Any
from pydantic import BaseModel, PrivateAttr


class Connection(BaseModel):
    dsn: str
    _parts: list[str] = PrivateAttr()

    def model_post_init(self, context: Any, /) -> None:
        self._parts = self.dsn.split("://")


print(Connection(dsn="postgres://localhost")._parts)
#> ['postgres', 'localhost']
```

For *validation* logic (checking cross-field rules) prefer `@model_validator(mode="after")` — see chapter 04.

## 11. Skipping validation: `model_construct`

```python
from pydantic import BaseModel


class Row(BaseModel):
    id: int
    name: str


# Trusted, already-validated data (e.g. from your own DB): skip validation for speed
r = Row.model_construct(id=1, name="x")
print(r, sorted(r.model_fields_set))
#> id=1 name='x' ['id', 'name']

bad = Row.model_construct(id="not an int")   # no error! garbage in, garbage out
print(bad.id)
#> not an int
```

Use it only for data you fully trust. Defaults are still applied; nothing else is checked.

## 12. Forward references and self-referencing models

Annotations can refer to classes defined later. Pydantic resolves them when possible, otherwise the model stays "incomplete" until you call `model_rebuild()`.

```python
from __future__ import annotations
from pydantic import BaseModel


class Node(BaseModel):
    value: int
    children: list[Node] = []      # self-reference works automatically


tree = Node.model_validate({"value": 1, "children": [{"value": 2}, {"value": 3, "children": [{"value": 4}]}]})
print(tree.children[1].children[0].value)
#> 4


class Parent(BaseModel):
    child: Child                   # Child not defined yet


class Child(BaseModel):
    name: str


Parent.model_rebuild()             # resolve 'Child' now
print(Parent(child={"name": "kid"}))
#> child=Child(name='kid')
```

In practice Pydantic usually rebuilds automatically on first use; explicit `model_rebuild()` is needed mostly when types live in other modules or are defined inside functions. Python 3.15's `lazy import` statement is also supported (2.14+) for breaking import cycles between model modules.

## 13. Dynamic models: `create_model`

Generate models at runtime (from config files, DB metadata, user-defined forms):

```python
from pydantic import Field, computed_field, create_model


def full_name(self) -> str:
    return f"{self.first} {self.last}"


Person = create_model(
    "Person",
    first=str,                                   # required
    last=(str, "Doe"),                           # (type, default)
    age=(int, Field(ge=0, default=0)),           # (type, FieldInfo)
    __namespace__={"full_name": computed_field(property(full_name))},  # 2.14+
)

print(Person(first="John").model_dump())
#> {'first': 'John', 'last': 'Doe', 'age': 0, 'full_name': 'John Doe'}
```

Other dunder kwargs: `__base__` (parent class), `__config__`, `__doc__`, `__module__`, `__qualname__`, and the legacy `__validators__` (prefer `__namespace__`; `__validators__` is slated for deprecation in V3).

## 14. `RootModel`: models that aren't objects

When the top-level data is a list, a scalar, or a dict with arbitrary keys, use `RootModel`:

```python
from pydantic import RootModel


class Tags(RootModel[list[str]]):
    def __iter__(self):
        return iter(self.root)

    def __getitem__(self, i):
        return self.root[i]


t = Tags.model_validate_json('["a", "b"]')
print(t.root, list(t), t[0])
#> ['a', 'b'] ['a', 'b'] a
print(t.model_dump_json())
#> ["a","b"]
```

If you only need validation (not a class with methods), a `TypeAdapter(list[str])` is lighter — see chapter 08.

---

## Summary

- Subclass `BaseModel`, annotate fields; defaults make fields optional, `| None` makes them nullable.
- Create with `Model(...)`, `model_validate`, `model_validate_json` (fastest for JSON), `model_validate_strings`.
- Configure behavior with `model_config = ConfigDict(...)`: `frozen`, `validate_assignment`, `extra`, `from_attributes` …
- Use private attributes for internal state, `model_post_init` for setup, `model_construct` for trusted data.
- `RootModel` wraps non-object top-level data; `create_model` builds models dynamically.

**Next:** [03 — Fields and Types](03-fields-and-types.md)
