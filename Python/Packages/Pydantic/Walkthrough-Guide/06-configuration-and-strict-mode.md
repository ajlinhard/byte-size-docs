# 06 — Configuration and Strict Mode

> **Level:** Intermediate · **Prerequisite:** [05 — Serialization](05-serialization.md)

Almost every behavior you have seen so far — coercion, extra keys, aliases, mutability, string cleanup — can be tuned through **configuration**. This chapter shows where config lives, the options that matter most, and how to choose between Pydantic's **lax** and **strict** validation modes.

---

## 1. Where configuration lives

### On a model: `model_config`

```python
from pydantic import BaseModel, ConfigDict


class Strict(BaseModel):
    model_config = ConfigDict(
        strict=True,
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
    )
    name: str
```

`ConfigDict` is a `TypedDict`, so your IDE autocompletes keys and type-checkers catch typos.

### As class keyword arguments

```python
from pydantic import BaseModel


class Point(BaseModel, frozen=True, extra="forbid"):
    x: int
    y: int
```

Equivalent to `model_config = ConfigDict(frozen=True, extra="forbid")`. Use one style or the other, not both on the same class.

### For non-`BaseModel` types

| Target | How |
|---|---|
| Pydantic dataclass | `@dataclass(config=ConfigDict(...))` |
| stdlib dataclass / `TypedDict` | `@with_config(ConfigDict(...))` decorator, or `__pydantic_config__ = ConfigDict(...)` |
| `TypeAdapter` | `TypeAdapter(T, config=ConfigDict(...))` (only for types that can't carry their own config) |
| `@validate_call` | `@validate_call(config=ConfigDict(...))` |

### Inheritance and propagation

- Child models **merge** their config with parents'.
- Config does **not** propagate into *nested models* — each model uses its own `model_config`. (It *does* propagate into nested stdlib dataclasses and `TypedDict`s that don't define their own.)
- To share config across your codebase, define a project base class:

```python
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class ApiModel(BaseModel):
    """Base for every request/response schema in the project."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        validate_by_name=True,
        serialize_by_alias=True,
        extra="forbid",
        str_strip_whitespace=True,
        use_attribute_docstrings=True,
    )


class CreateOrder(ApiModel):
    customer_id: int
    """The customer placing the order."""   # becomes the field description (use_attribute_docstrings)


print(CreateOrder.model_validate({"customerId": 5}).model_dump())
#> {'customerId': 5}
print(CreateOrder.model_fields["customer_id"].description)
#> The customer placing the order.
```

## 2. The most useful options

### Validation behavior

| Option | Default | Purpose |
|---|---|---|
| `strict` | `False` | Disable type coercion globally for the model |
| `extra` | `'ignore'` | `'ignore'`, `'forbid'`, `'allow'` unknown keys |
| `frozen` | `False` | Immutable + hashable instances |
| `validate_assignment` | `False` | Re-validate on attribute assignment |
| `validate_default` | `False` | Validate default values |
| `revalidate_instances` | `'never'` | Re-validate model instances passed as input (`'always'`, `'subclass-instances'`) |
| `from_attributes` | `False` | Read data from object attributes (ORM mode) |
| `arbitrary_types_allowed` | `False` | Allow unknown classes (validated by `isinstance`) |
| `validate_by_alias` / `validate_by_name` | `True` / `False` | Which input keys are accepted |
| `coerce_numbers_to_str` | `False` | Allow `123` → `"123"` for `str` fields |
| `use_enum_values` | `False` | Store `.value` instead of enum members |
| `allow_inf_nan` | `True` | Accept `inf`/`nan` for floats |
| `regex_engine` | `'rust-regex'` | `'python-re'` to support look-arounds/backreferences |
| `val_json_bytes` | `'utf8'` | How bytes arrive in JSON: `'utf8'`, `'base64'`, `'hex'` |
| `val_temporal_unit` | `'infer'` | Interpret numeric datetimes as seconds/milliseconds (2.12+) |
| `url_preserve_empty_path` | `False` | Keep `https://x.com` as-is instead of `https://x.com/` (2.12+) |

### String normalization

`str_strip_whitespace`, `str_to_lower`, `str_to_upper`, `str_min_length`, `str_max_length` — applied to every `str` field.

### Serialization behavior

| Option | Purpose |
|---|---|
| `serialize_by_alias` | Dump with aliases by default |
| `ser_json_timedelta` | `'iso8601'` or `'float'` |
| `ser_json_temporal` | `'iso8601'`, `'seconds'`, `'milliseconds'` for datetimes (2.12+) |
| `ser_json_bytes` | `'utf8'`, `'base64'`, `'hex'` |
| `ser_json_inf_nan` | `'null'`, `'constants'`, `'strings'` |
| `polymorphic_serialization` | Serialize subclass instances with their own fields (2.13+) |

### Schema & docs

`title`, `json_schema_extra`, `json_schema_mode_override`, `json_schema_serialization_defaults_required`, `use_attribute_docstrings`, `field_title_generator`, `model_title_generator`.

### Performance / build

| Option | Purpose |
|---|---|
| `defer_build` | Delay building validators until first use (faster import for apps with many models) |
| `cache_strings` | String caching in JSON parsing (`True`, `'keys'`, `'none'`) |
| `protected_namespaces` | Names that can't be used for fields (default `('model_validate', 'model_dump')`) |
| `hide_input_in_errors` | Don't echo input values in error messages (sensitive data!) |

```python
from pydantic import BaseModel, ConfigDict, ValidationError


class Login(BaseModel):
    model_config = ConfigDict(hide_input_in_errors=True)
    pin: int


try:
    Login(pin="my-secret-1234")
except ValidationError as e:
    print("my-secret" in str(e))
    #> False
```

## 3. Lax vs. strict mode

By default Pydantic runs in **lax mode**: it accepts inputs that can be converted *unambiguously* and without data loss.

| Target type | Lax accepts | Strict accepts (Python input) |
|---|---|---|
| `int` | `5`, `"5"`, `5.0` | `5` only (`bool` rejected too) |
| `float` | `1.5`, `1`, `"1.5"` | `1.5`, `1` |
| `bool` | `True`, `1`, `"yes"`, `"true"` | `True` / `False` only |
| `str` | `"x"` | `"x"` (bytes rejected) |
| `datetime` | `datetime`, ISO string, unix timestamp | `datetime` instance only |
| `UUID` | `UUID`, string, bytes | `UUID` instance only |
| `Model` | dict, model instance | model instance only (unless JSON input) |
| `list[int]` | list, tuple, set, generator | list only |

**Important subtlety:** strictness is *relative to the input format*. In **JSON** there is no native `datetime`, `UUID`, `Decimal`, or `tuple`, so strict JSON validation still accepts ISO strings for `datetime`, strings for `UUID`, arrays for `tuple`, and objects for models. Strict mode only forbids conversions that JSON *could* have expressed precisely — e.g. the string `"5"` for an `int` is rejected because JSON has numbers.

```python
from datetime import datetime
from pydantic import BaseModel, ConfigDict, ValidationError


class Event(BaseModel):
    model_config = ConfigDict(strict=True)
    count: int
    at: datetime


# JSON: ISO datetime string is fine even in strict mode
print(Event.model_validate_json('{"count": 1, "at": "2026-10-15T10:00:00"}').at)
#> 2026-10-15 10:00:00

# Python: a string is not a datetime in strict mode
try:
    Event.model_validate({"count": "1", "at": "2026-10-15T10:00:00"})
except ValidationError as e:
    print([err["type"] for err in e.errors()])
    #> ['int_type', 'datetime_type']
```

### Granularity: where to turn strictness on

```python
from typing import Annotated
from pydantic import BaseModel, Field, Strict, StrictInt, StrictStr


class Mixed(BaseModel):
    a: StrictInt                              # predefined strict alias
    b: Annotated[int, Strict()]               # same, via metadata
    c: int = Field(strict=True)               # via Field
    d: StrictStr
    e: int                                    # lax (unless model/call is strict)


data = {"a": 1, "b": 2, "c": 3, "d": "x", "e": "5"}
print(Mixed.model_validate(data).e)          # lax field coerces "5"
#> 5

try:
    Mixed.model_validate(data, strict=True)  # per-call strict now applies to 'e' too
except Exception as e:
    print(e.errors()[0]["loc"])
    #> ('e',)

try:
    Mixed.model_validate({**data, "a": "1"})  # field-level strict always applies
except Exception as e:
    print(e.errors()[0]["type"])
    #> int_type
```

Order of precedence:

1. A **per-call** `strict=True` (e.g. `model_validate(data, strict=True)`) applies to every field — it even overrides `Field(strict=False)`.
2. Otherwise **field-level** settings (`Field(strict=...)`, `Strict()`, `StrictInt`…) win over the model config.
3. The **model config** `strict` is the fallback.

Predefined strict types: `StrictInt`, `StrictFloat`, `StrictStr`, `StrictBool`, `StrictBytes`.

### When to use which

- **Lax** is ideal at user-facing boundaries: forms, query strings, CSV, environment variables, legacy JSON with stringly-typed numbers.
- **Strict** is ideal for internal service contracts, typed RPC, event schemas, and anywhere silent coercion could hide bugs (`"0"` → `False`? `1.0` → `1`?).
- A common setup: strict models internally, lax request models at the API edge.

## 4. Union mode: `smart` vs. `left_to_right`

Unions have their own matching strategy (covered fully in chapter 07). In **smart mode** (default) Pydantic first looks for an *exact type match* in strict mode across members, then falls back to lax matching, picking the "best" result. `Field(union_mode="left_to_right")` tries members in order and returns the first success.

## 5. Fail-fast for large sequences

```python
from typing import Annotated
from pydantic import Field, TypeAdapter, ValidationError

ta = TypeAdapter(Annotated[list[int], Field(fail_fast=True)])
try:
    ta.validate_python(["x"] + ["y"] * 10_000)
except ValidationError as e:
    print(e.error_count())   # stops at the first bad item
    #> 1
```

## 6. Runtime overrides you can use per call

| Call | Overrides available |
|---|---|
| `model_validate*` | `strict`, `extra`, `from_attributes`, `context`, `by_alias`, `by_name` |
| `model_dump*` | `by_alias`, `exclude_*`, `round_trip`, `serialize_as_any`, `polymorphic_serialization`, `warnings`, `context`, `fallback` |
| `model_json_schema` | `by_alias`, `mode`, `schema_generator`, `ref_template`, `union_format` |

---

## Summary

- Put shared configuration in a project-wide base model; per-model tweaks via `model_config` or class kwargs.
- Key options: `extra`, `frozen`, `validate_assignment`, `from_attributes`, alias settings, string normalization, `hide_input_in_errors`, `defer_build`.
- Lax mode coerces unambiguous input; strict mode rejects conversion — but strict JSON still accepts JSON-native encodings for non-JSON types.
- Strictness can be set at model, call, or field level; the most specific wins.

**Next:** [07 — Unions, Generics, and Recursive Models](07-unions-generics-and-recursive-models.md)
