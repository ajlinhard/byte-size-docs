# 04 — Validators

> **Level:** Beginner → Intermediate · **Prerequisite:** [03 — Fields and Types](03-fields-and-types.md)

Type annotations and constraints cover most needs. When they don't — "end date must be after start date", "normalize phone numbers", "reject reserved usernames" — you write **validators**: plain Python functions that Pydantic calls at specific points in the validation pipeline.

---

## 1. The four modes

Every validator (field or model level) runs in one of four **modes**, relative to Pydantic's built-in type validation:

```
          ┌────────────── wrap ───────────────┐
input ──► │ before ─► [ Pydantic core type     │ ─► after ──► value
          │           validation ]             │
          └────────────────────────────────────┘
plain = replaces the core validation entirely
```

| Mode | Receives | Typical use | Pitfall |
|---|---|---|---|
| **after** (default) | the already-typed value | business rules on clean data | — the safest choice |
| **before** | the **raw** input (could be anything) | normalize/reshape input before parsing | must handle any input type |
| **plain** | the raw input; core validation is **skipped** | fully custom parsing | you lose type coercion & checks |
| **wrap** | raw input + a `handler` to call the core validation | try/except around core validation, conditional logic, fallbacks | most flexible, most complex |

**Rule of thumb:** use *after* unless you have a reason not to.

## 2. Field validators with the decorator

```python
from pydantic import BaseModel, ValidationError, field_validator


class SignUp(BaseModel):
    username: str
    password: str
    tags: list[str] = []

    @field_validator("username")              # mode='after' is the default
    @classmethod
    def not_reserved(cls, value: str) -> str:
        if value.lower() in {"admin", "root"}:
            raise ValueError("username is reserved")
        return value

    @field_validator("tags", mode="before")
    @classmethod
    def split_csv(cls, value):
        if isinstance(value, str):            # accept "a,b,c" as well as a list
            return [t.strip() for t in value.split(",") if t.strip()]
        return value

    @field_validator("username", "password")  # one validator, several fields
    @classmethod
    def no_spaces(cls, value: str) -> str:
        if " " in value:
            raise ValueError("must not contain spaces")
        return value


print(SignUp(username="ada", password="x", tags="python, rust").tags)
#> ['python', 'rust']

try:
    SignUp(username="admin", password="a b")
except ValidationError as e:
    for err in e.errors():
        print(err["loc"], err["msg"])
    #> ('username',) Value error, username is reserved
    #> ('password',) Value error, must not contain spaces
```

Rules:

- Decorate with `@field_validator(...)` **then** `@classmethod` (Pydantic adds it if you forget, but being explicit helps type-checkers).
- **Always return** the value (possibly modified). Returning nothing sets the field to `None`!
- Signal failure by raising `ValueError` or `AssertionError` (assertions are skipped under `python -O`; prefer `ValueError`), or `PydanticCustomError` for a custom error type.
- `"*"` matches all fields.
- Do **not** raise `TypeError` or `ValidationError` from validators — they are not converted into validation errors.

### Accessing other fields: `ValidationInfo`

```python
from pydantic import BaseModel, ValidationInfo, field_validator


class PasswordChange(BaseModel):
    password: str
    confirm: str

    @field_validator("confirm")
    @classmethod
    def matches(cls, value: str, info: ValidationInfo) -> str:
        # info.data holds fields validated *before* this one (declaration order!)
        if "password" in info.data and value != info.data["password"]:
            raise ValueError("passwords do not match")
        return value
```

`info` also exposes `info.field_name`, `info.mode` (`'python'`, `'json'`, `'strings'`), `info.context`, and `info.config`. For cross-field rules a **model validator** is usually clearer.

## 3. Annotated (functional) validators

Instead of decorators on the model, attach validators to the **type**. This makes them reusable across models, functions and `TypeAdapter`s.

```python
from typing import Annotated
from pydantic import AfterValidator, BaseModel, BeforeValidator, PlainValidator, WrapValidator


def strip_and_lower(v: object) -> object:
    return v.strip().lower() if isinstance(v, str) else v


def check_slug(v: str) -> str:
    if not v.replace("-", "").isalnum():
        raise ValueError("slug must be alphanumeric with dashes")
    return v


Slug = Annotated[str, BeforeValidator(strip_and_lower), AfterValidator(check_slug)]


class Post(BaseModel):
    slug: Slug
    related: list[Slug] = []


print(Post(slug="  Hello-World ", related=["Foo-Bar"]))
#> slug='hello-world' related=['foo-bar']
```

### Execution order with multiple annotated validators

- **before** and **wrap** validators run **right-to-left** (the outermost — last in the list — runs first).
- **after** validators run **left-to-right**.

```python
from typing import Annotated
from pydantic import AfterValidator, BeforeValidator, TypeAdapter

log = []
T = Annotated[
    int,
    BeforeValidator(lambda v: log.append("before-1") or v),
    AfterValidator(lambda v: log.append("after-1") or v),
    BeforeValidator(lambda v: log.append("before-2") or v),
    AfterValidator(lambda v: log.append("after-2") or v),
]
TypeAdapter(T).validate_python(1)
print(log)
#> ['before-2', 'before-1', 'after-1', 'after-2']
```

### Wrap validators

A wrap validator receives a `handler` that runs the inner (core) validation. Use it for fallbacks, error translation or timing:

```python
from datetime import datetime
from typing import Annotated, Any
from pydantic import TypeAdapter, ValidationError, ValidatorFunctionWrapHandler, WrapValidator


def lenient_datetime(value: Any, handler: ValidatorFunctionWrapHandler) -> datetime:
    if value == "now":
        return datetime(2026, 10, 15, 12, 0)   # fixed for reproducibility
    try:
        return handler(value)
    except ValidationError:
        # fall back to a legacy format "15/10/2026"
        return datetime.strptime(value, "%d/%m/%Y")


Flexible = Annotated[datetime, WrapValidator(lenient_datetime)]
ta = TypeAdapter(Flexible)
print(ta.validate_python("now"))
#> 2026-10-15 12:00:00
print(ta.validate_python("15/10/2026"))
#> 2026-10-15 00:00:00
```

### Plain validators

```python
from typing import Annotated
from pydantic import BaseModel, PlainValidator


def parse_bool_strictly(v):
    if v in ("Y", "N"):
        return v == "Y"
    raise ValueError("expected 'Y' or 'N'")


class Flags(BaseModel):
    active: Annotated[bool, PlainValidator(parse_bool_strictly)]


print(Flags(active="Y").active)
#> True
```

Because core validation is skipped, a plain validator returning the wrong type is **not** caught. Use sparingly.

### Decorator or `Annotated`?

| Use the decorator (`@field_validator`) when… | Use `Annotated` validators when… |
|---|---|
| logic is specific to one model | the rule belongs to a *concept* (Slug, Money, PhoneNumber) |
| you need `cls` (e.g. class-level constants) | you want reuse across models, function args, FastAPI params |
| you apply one rule to many fields by name | you want the rule on container items: `list[Slug]` |

## 4. Model validators

Model validators see the **whole** input or object — ideal for cross-field rules.

```python
from datetime import date
from typing import Any, Self
from pydantic import BaseModel, ValidationError, model_validator


class DateRange(BaseModel):
    start: date
    end: date

    @model_validator(mode="before")
    @classmethod
    def accept_tuple(cls, data: Any) -> Any:
        # allow DateRange.model_validate(("2026-01-01", "2026-12-31"))
        if isinstance(data, (tuple, list)) and len(data) == 2:
            return {"start": data[0], "end": data[1]}
        return data

    @model_validator(mode="after")
    def check_order(self) -> Self:        # instance method, returns self
        if self.end < self.start:
            raise ValueError("end must be on or after start")
        return self


print(DateRange.model_validate(("2026-01-01", "2026-12-31")))
#> start=datetime.date(2026, 1, 1) end=datetime.date(2026, 12, 31)

try:
    DateRange(start="2026-05-01", end="2026-01-01")
except ValidationError as e:
    print(e.errors()[0]["msg"])
    #> Value error, end must be on or after start
```

Notes:

- `mode="before"` validators are **classmethods** and receive raw input (`dict`, object, anything).
- `mode="after"` validators are **instance methods** and must return `self`. (Using a classmethod for *after* validators emits a deprecation warning since 2.12.)
- `mode="wrap"` validators are classmethods receiving `(data, handler)`.
- After-model-validators also run on `validate_assignment` — after each assignment.
- `typing.Self` needs Python 3.11+; on 3.10 import it from `typing_extensions` (already a Pydantic dependency).

## 5. Custom error types and messages

`PydanticCustomError` gives you a stable error `type`, a templated message, and context:

```python
from pydantic import BaseModel, ValidationError, field_validator
from pydantic_core import PydanticCustomError


class Order(BaseModel):
    quantity: int

    @field_validator("quantity")
    @classmethod
    def max_qty(cls, v: int) -> int:
        if v > 100:
            raise PydanticCustomError(
                "quantity_too_large",                         # error type
                "Quantity {qty} exceeds the limit of {limit}",  # message template
                {"qty": v, "limit": 100},                     # context
            )
        return v


try:
    Order(quantity=500)
except ValidationError as e:
    err = e.errors()[0]
    print(err["type"], "|", err["msg"], "|", err["ctx"])
    #> quantity_too_large | Quantity 500 exceeds the limit of 100 | {'qty': 500, 'limit': 100}
```

### Rewriting messages for end users (i18n)

Error `type`s are stable, so you can translate them centrally:

```python
from pydantic import BaseModel, ValidationError

MESSAGES_ES = {
    "missing": "Campo obligatorio",
    "int_parsing": "Debe ser un número entero",
}


def translate(e: ValidationError) -> list[dict]:
    return [
        {"field": ".".join(map(str, err["loc"])), "message": MESSAGES_ES.get(err["type"], err["msg"])}
        for err in e.errors()
    ]


class Form(BaseModel):
    age: int
    name: str


try:
    Form(age="x")
except ValidationError as e:
    print(translate(e))
    #> [{'field': 'age', 'message': 'Debe ser un número entero'}, {'field': 'name', 'message': 'Campo obligatorio'}]
```

`e.errors(include_url=False, include_input=False, include_context=False)` lets you strip noise (and avoid echoing sensitive input) when returning errors to clients.

## 6. Validation context

Pass runtime data (current user, allowed values, feature flags) into validators without global state:

```python
from pydantic import BaseModel, ValidationInfo, field_validator


class Upload(BaseModel):
    filename: str

    @field_validator("filename")
    @classmethod
    def allowed_ext(cls, v: str, info: ValidationInfo) -> str:
        allowed = (info.context or {}).get("allowed_ext", {".png", ".jpg"})
        if not any(v.endswith(ext) for ext in allowed):
            raise ValueError(f"extension not in {sorted(allowed)}")
        return v


print(Upload.model_validate({"filename": "a.pdf"}, context={"allowed_ext": {".pdf"}}))
#> filename='a.pdf'
```

## 7. Validating the default and assignment

- Validators don't run on defaults unless `validate_default=True` (field) or config `validate_default=True`.
- With `validate_assignment=True`, field validators run on each assignment, followed by *after* model validators.

## 8. Practical recipes

**Normalize then constrain:**

```python
from typing import Annotated
from pydantic import AfterValidator, BeforeValidator, Field, TypeAdapter

PhoneUS = Annotated[
    str,
    BeforeValidator(lambda v: "".join(ch for ch in str(v) if ch.isdigit())),
    Field(pattern=r"^1?\d{10}$"),
    AfterValidator(lambda v: v[-10:]),
]
print(TypeAdapter(PhoneUS).validate_python("+1 (555) 010-9999"))
#> 5550109999
```

**Mutually exclusive fields:**

```python
from typing import Self
from pydantic import BaseModel, model_validator


class Auth(BaseModel):
    api_key: str | None = None
    token: str | None = None

    @model_validator(mode="after")
    def exactly_one(self) -> Self:
        if (self.api_key is None) == (self.token is None):
            raise ValueError("provide exactly one of api_key or token")
        return self
```

**Async / I/O checks:** validators are synchronous and should stay pure and fast. Do database lookups ("does this user ID exist?") in your service layer *after* validation, not inside validators.

---

## Summary

- Validators run in **after** (default), **before**, **plain**, or **wrap** mode.
- Use `@field_validator` / `@model_validator` for model-specific rules; use `Annotated[..., AfterValidator(...)]` for reusable types.
- Raise `ValueError` or `PydanticCustomError`; always return the value (or `self`).
- `ValidationInfo` gives access to earlier fields, context, mode, and field name.
- Keep validators pure; do I/O elsewhere.

**Next:** [05 — Serialization](05-serialization.md)
