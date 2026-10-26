# 16 — Migration (V1 → V2) and What's New

> **Level:** Reference · Current version: **Pydantic 2.14.1** (released October 11, 2026)

This chapter is a reference for two audiences: teams still carrying Pydantic V1 code, and V2 users who want to know what changed in recent minor releases.

---

## Part A — Migrating from V1 to V2

### Why migrate now

- Pydantic V1 is **not supported on Python 3.14+**, and the bundled `pydantic.v1` namespace is a migration aid only.
- **FastAPI ≥ 0.128** and current **SQLModel** require Pydantic v2 models; the temporary support for `pydantic.v1` models in FastAPI (0.119–0.127) has been removed.
- V2 is dramatically faster and has features V1 lacks (discriminated unions everywhere, strict mode, `TypeAdapter`, JSON Schema 2020-12, serialization control, `MISSING`, partial JSON parsing…).

### Strategy

1. **Upgrade the package** to V2 and change imports to `from pydantic.v1 import ...` everywhere — the app keeps working on V1 semantics (Python ≤ 3.13 only).
2. **Run `bump-pydantic`** to rewrite most mechanical changes:
   ```bash
   pip install bump-pydantic
   bump-pydantic my_package/        # use --diff to preview
   ```
3. **Migrate module by module** to `from pydantic import ...`, fixing what the tool couldn't (custom validators, config, custom types).
4. **Turn deprecation warnings into errors in CI** (`-W error::pydantic.warnings.PydanticDeprecatedSince20`) once done, to stop regressions.

### API mapping

| V1 | V2 |
|---|---|
| `class Config:` | `model_config = ConfigDict(...)` |
| `orm_mode = True` | `from_attributes=True` |
| `allow_population_by_field_name` | `validate_by_name=True` (2.11+; `populate_by_name` before) |
| `anystr_strip_whitespace`, `min_anystr_length` | `str_strip_whitespace`, `str_min_length` |
| `allow_mutation = False` | `frozen=True` |
| `schema_extra` | `json_schema_extra` |
| `underscore_attrs_are_private` | always on |
| `.dict()` | `.model_dump()` |
| `.json()` | `.model_dump_json()` |
| `.parse_obj()` | `.model_validate()` |
| `.parse_raw()` | `.model_validate_json()` |
| `.parse_file()` | read the file, then `.model_validate_json()` |
| `.from_orm()` | `.model_validate(obj)` with `from_attributes` |
| `.construct()` | `.model_construct()` |
| `.copy()` | `.model_copy()` |
| `.schema()` / `.schema_json()` | `.model_json_schema()` (+ `json.dumps`) |
| `.update_forward_refs()` | `.model_rebuild()` |
| `__fields__` | `model_fields` (class access) |
| `__fields_set__` | `model_fields_set` |
| `@validator` | `@field_validator` (signature changed, see below) |
| `@root_validator` | `@model_validator(mode="before" \| "after")` |
| `each_item=True` | `list[Annotated[T, AfterValidator(f)]]` |
| `pre=True` | `mode="before"` |
| `always=True` | `Field(validate_default=True)` |
| `values` argument | `info: ValidationInfo` → `info.data` |
| `__root__` field | `RootModel[T]` |
| `parse_obj_as(T, data)` | `TypeAdapter(T).validate_python(data)` |
| `schema_of(T)` | `TypeAdapter(T).json_schema()` |
| `GenericModel` | `BaseModel, Generic[T]` |
| `constr(...)`, `conint(...)` | `Annotated[str, StringConstraints(...)]`, `Annotated[int, Field(...)]` |
| `Field(regex=...)` | `Field(pattern=...)` |
| `Field(const=True)` | `Literal[...]` |
| `Field(min_items=, max_items=)` | `Field(min_length=, max_length=)` |
| `Field(allow_mutation=False)` | `Field(frozen=True)` |
| `__get_validators__` | `__get_pydantic_core_schema__` |
| `__modify_schema__` | `__get_pydantic_json_schema__` |
| `json_encoders` config | `@field_serializer` / `PlainSerializer` (`json_encoders` still works but is deprecated) |
| `BaseSettings` from `pydantic` | `pip install pydantic-settings`; `from pydantic_settings import BaseSettings` |
| `@validate_arguments` | `@validate_call` |

### Behavior changes that bite

| Topic | V1 | V2 |
|---|---|---|
| `Optional[int]` without default | optional (defaults to `None`) | **required**, nullable |
| `int` from `"3.7"` / `3.7` | truncates to 3 | **error** (fractional part) |
| Numbers → `str` field | coerced (`1` → `"1"`) | **error** unless `coerce_numbers_to_str=True` |
| Unions | left-to-right, first success | **smart** mode (exact-type first) |
| Subclass instances in fields | dumped with subclass fields | dumped as **declared** type (use `polymorphic_serialization` / `SerializeAsAny`) |
| Model equality | compared dicts (could equal a `dict`) | requires same type; never equal to a `dict` |
| Instances passed to fields | revalidated/copied | reused as-is (`revalidate_instances` config) |
| Validators on defaults | `always=True` | `validate_default=True` |
| `TypeError` in validators | converted to validation error | **not** converted — raise `ValueError` |
| URL types | `str` subclasses | `Url` objects — use `str(url)` |
| JSON Schema | Draft 7-ish, `definitions` | Draft 2020-12, `$defs` |

### Before / after example

```py
# ---------- V1 ----------
from typing import Optional
from pydantic import BaseModel, validator, root_validator

class User(BaseModel):
    name: str
    email: Optional[str]
    tags: list[str] = []

    class Config:
        orm_mode = True
        allow_population_by_field_name = True

    @validator("tags", each_item=True, pre=True)
    def lower(cls, v):
        return v.lower()

    @root_validator
    def check(cls, values):
        if values.get("name") == "root" and not values.get("email"):
            raise ValueError("root needs an email")
        return values

user = User.parse_obj(data); user.dict()
```

```python
# ---------- V2 ----------
from typing import Annotated, Self
from pydantic import BaseModel, BeforeValidator, ConfigDict, model_validator


def lower(v: object) -> object:
    return v.lower() if isinstance(v, str) else v


class User(BaseModel):
    model_config = ConfigDict(from_attributes=True, validate_by_name=True)

    name: str
    email: str | None = None                  # explicit default to keep V1 "optional" semantics
    tags: list[Annotated[str, BeforeValidator(lower)]] = []

    @model_validator(mode="after")
    def check(self) -> Self:
        if self.name == "root" and not self.email:
            raise ValueError("root needs an email")
        return self


user = User.model_validate({"name": "ada", "tags": ["PY", "Rust"]})
print(user.model_dump())
#> {'name': 'ada', 'email': None, 'tags': ['py', 'rust']}
```

---

## Part B — What's new in recent V2 releases

Recent minor versions have shipped roughly every six months. Minor releases can include small documented behavior changes ("non-breaking" per the version policy) — read each release's *Changes* section before upgrading.

### 2.14 (October 8, 2026; 2.14.1 on October 11)

- **Python:** drops 3.9, adds **3.15** support.
- **`MISSING` sentinel is stable** — `from pydantic import MISSING`; fields set to it are omitted from output and from JSON Schema.
- **Lazy imports** (PEP 810, Python 3.15) supported for cross-module model references.
- **`TypeForm`** (PEP 747): type checkers infer `TypeAdapter(...)` return types for unions/`Annotated` forms.
- **`frozendict`** (PEP 814) supported.
- `create_model(..., __namespace__={...})` to add methods/computed fields/validators (`__validators__` to be deprecated in V3).
- Native core schemas for `Fraction`, named tuples, `deque`, `OrderedDict`, `Counter`; `multiple_of` for `Fraction`/`timedelta`.
- **Changes:** `model_config` is no longer mutated by Pydantic; `Decimal` JSON Schema no longer includes a regex `pattern`; `TypeAdapter` config is used for JSON Schema; signature uses field names when `validate_by_alias=False`; non-positive `multiple_of` errors at definition time; wrap serializer `handler(self, info)` misuse now errors; `SecretStr`/`SecretBytes` comparisons are constant-time; `model_copy()` only deep-copies non-updated fields.
- **Performance:** many schema-generation optimizations (5–20% each on benchmarks), schema gathering moved to Rust; 2.14.1 trims allocations during model validation.

### 2.13 (April 13, 2026)

- **Polymorphic serialization** (`model_dump(polymorphic_serialization=True)` / config) — serialize model subclasses with their own fields, fixing the 2.12 `serialize_as_any` breakage.
- `exclude_if` on `@computed_field`; `ascii_only` in `StringConstraints`.
- Private attribute `default_factory` can take validated data.
- `Decimal` accepts `(sign, digits, exponent)` tuples; `complex` validation defers to `complex()`.
- **Changes:** union serialization fixes; extra fields set after init are tracked in `model_fields_set`; shallow `model_copy()` of `RootModel` copies the root; `@field_serializer` field names validated; `PydanticUserError` is now a `RuntimeError`; `NamedTuple` subclasses follow Python semantics.
- `pydantic-core` source merged into the main repository; `pydantic.v1` updated to 1.10.26 (Python 3.14 support for V1 namespace).
- New unified docs site at pydantic.dev/docs.

### 2.12 (October 7, 2025)

- Initial **Python 3.14** support; experimental `MISSING` sentinel.
- `exclude_if` for fields; `ValidateAs` helper; PEP 728 (`closed`/`extra_items` TypedDict) support.
- Temporal config: `val_temporal_unit`, `ser_json_temporal`; `url_preserve_empty_path`.
- Per-call `extra=` on validate methods; `exclude_computed_fields` serialization option; `union_format` for JSON Schema; `__pydantic_on_complete__` hook; `__qualname__` in `create_model`.
- `serialize_as_any` behavior unified with `SerializeAsAny` (later complemented by 2.13's polymorphic serialization).
- *After* model validators as classmethods deprecated.

### 2.11 (March 2025)

- Big **schema-build performance and memory** improvements.
- `validate_by_alias` / `validate_by_name` / `serialize_by_alias` config (and `by_alias`/`by_name` per call) replacing `populate_by_name`.
- Accessing `model_fields` on instances deprecated.

### Earlier V2 highlights

| Version | Highlights |
|---|---|
| 2.10 (Nov 2024) | `default_factory` taking validated data, partial JSON validation (`experimental_allow_partial`), PEP 695/696 generics improvements |
| 2.9 (Sep 2024) | `complex` type support, `val_json_bytes` config |
| 2.8 (Jul 2024) | `FailFast` / `fail_fast`, experimental pipeline API |
| 2.7 (Apr 2024) | Partial JSON parsing in `pydantic-core`, `Secret[T]`, `serialize_as_any`, `use_attribute_docstrings` |
| 2.5 (Nov 2023) | `JsonValue` type |
| 2.0 (Jun 2023) | Rust core rewrite, new API (`model_*`), strict mode, `TypeAdapter`, serialization decorators |

### Looking ahead: V3

The maintainers have signalled a future V3 that removes long-deprecated V1-era APIs (e.g. `__validators__` in `create_model`, `json_encoders`, the `PydanticDeprecatedSince20` shims). No release date has been announced. To be V3-ready:

- Fix every `PydanticDeprecatedSince2x` warning.
- Use `validate_by_name`/`validate_by_alias` instead of `populate_by_name`.
- Use `__namespace__` in `create_model`, serializers instead of `json_encoders`, instance-method *after* model validators.
- Use `MISSING` instead of private sentinels.

---

## Upgrade checklist for minor versions

1. Read the release blog post's **Changes** section.
2. Upgrade in a branch; run tests with `-W error::DeprecationWarning` for Pydantic.
3. Diff your exported JSON Schemas (chapter 09) — 2.14 changed several schema details.
4. Check serialization output snapshots (unions, subclasses, temporal types).
5. Pin both `pydantic` and (implicitly) `pydantic-core` in your lock file; upgrade them together.

---

**Back to:** [Index](README.md)
