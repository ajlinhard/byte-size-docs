# 11 — Internals: How Pydantic Works

> **Level:** Advanced · **Prerequisite:** [10 — Custom Types](10-custom-types.md)

You can use Pydantic productively without knowing any of this. But understanding the architecture explains its performance characteristics, its error messages, why import time matters, and how integrations (FastAPI, Logfire, Pydantic AI) hook in.

---

## 1. Two packages, two languages

```
┌──────────────────────────── pydantic (Python) ────────────────────────────┐
│  BaseModel / dataclasses / TypeAdapter / validate_call / Field / config  │
│  ModelMetaclass ─► field collection ─► GenerateSchema ─► core schema      │
│  JSON Schema generation (GenerateJsonSchema)                              │
└───────────────────────────────────┬──────────────────────────────────────┘
                                    │  core schema (plain dicts)
┌───────────────────────────────────▼─────── pydantic-core (Rust, PyO3) ───┐
│  SchemaValidator  ── validators tree ── jiter (JSON parser)              │
│  SchemaSerializer ── serializers tree ── JSON writer                     │
│  ValidationError, PydanticCustomError, Url, MultiHostUrl, TzInfo …       │
└──────────────────────────────────────────────────────────────────────────┘
```

- **`pydantic`** (pure Python) understands Python typing: annotations, generics, forward references, `Annotated` metadata, decorators, config. Its job is to **translate** all of that into a *core schema*.
- **`pydantic-core`** (Rust, exposed via PyO3) knows nothing about type hints. It takes a core schema and builds a fast **tree of validators and serializers**. It also contains `jiter`, Pydantic's own JSON parser.

Since v2.13 both live in the same GitHub repository (`pydantic/pydantic`), but `pydantic-core` is still released as a separate wheel and each `pydantic` version pins an exact compatible `pydantic-core` (an incompatible pair raises an error at import since 2.12).

## 2. What happens when you define a model

```python
from pydantic import BaseModel, field_validator


class User(BaseModel):
    id: int
    name: str = "anon"

    @field_validator("name")
    @classmethod
    def strip(cls, v: str) -> str:
        return v.strip()


# Artifacts attached to the class by the metaclass:
print(type(User.__pydantic_validator__).__name__)
#> SchemaValidator
print(type(User.__pydantic_serializer__).__name__)
#> SchemaSerializer
print(User.__pydantic_complete__)
#> True
print(list(User.__pydantic_decorators__.field_validators))
#> ['strip']
```

Step by step, `ModelMetaclass.__new__`:

1. **Collects the namespace** — separates fields (annotated attributes), private attributes (`_x`), class vars, and decorated functions (`@field_validator` etc. are stored as `PydanticDescriptorProxy` objects and gathered into `__pydantic_decorators__`).
2. **Builds `FieldInfo` objects** — merging annotations, defaults, `Field()` and `Annotated` metadata, and inherited fields from bases.
3. **Resolves annotations** — evaluates forward references using the module namespace (and parent frames when defined inside functions). If a name can't be resolved yet, the model is marked **incomplete**.
4. **Generates the core schema** via `GenerateSchema` — walking every field type and dispatching on it (`int` → `int_schema`, a `BaseModel` → `model_schema`, `list[T]` → `list_schema(...)`, `Annotated` metadata → constraints/validators). Types can override this through `__get_pydantic_core_schema__`.
5. **Cleans/simplifies** the schema (inlining definitions used once, collecting recursive ones as `definitions`). Much of this "gathering" moved into Rust in 2.14 for faster builds.
6. **Compiles** with `SchemaValidator(core_schema, config)` and `SchemaSerializer(...)`, storing them on the class.
7. Sets `__signature__`, `__pydantic_fields__`, `__pydantic_computed_fields__`, and finally calls the `__pydantic_on_complete__()` hook (2.12+) once the class is fully usable.

If the model is incomplete (unresolved forward refs) or `defer_build=True`, steps 4–6 are replaced by **mock** validator/serializer objects (`MockValSer`) that try to rebuild on first use — or raise a helpful `PydanticUserError` pointing you to `model_rebuild()`.

## 3. Looking at a core schema

```python
from typing import Annotated
from pydantic import BaseModel, Field


class Item(BaseModel):
    qty: Annotated[int, Field(gt=0)]
    tags: list[str] = []


schema = Item.__pydantic_core_schema__
print(schema["type"], schema["schema"]["type"])
#> model model-fields
fields = schema["schema"]["fields"]
print(fields["qty"]["schema"])
#> {'type': 'int', 'gt': 0}
print(fields["tags"]["schema"]["type"], fields["tags"]["schema"]["schema"]["type"])
#> default list
```

Every Pydantic feature is ultimately a node in this tree: `model`, `model-fields`, `default`, `nullable`, `union`, `tagged-union`, `function-before` / `function-after` / `function-wrap` / `function-plain`, `chain`, `json-or-python`, `definitions` + `definition-ref` (recursion), and so on. Reading the core schema is the best debugging tool when a custom type or validator does something unexpected.

## 4. What happens when you validate

```
User(**data)
 └─ BaseModel.__init__
     └─ __pydantic_validator__.validate_python(data, self_instance=self)   (Rust)
         ├─ model validator: input → dict/attributes lookup
         ├─ for each field: look up key (alias/name) → run field's validator subtree
         │     (before fns → core type check/coercion → constraints → after fns)
         ├─ collect ALL errors (line errors with loc paths)
         ├─ run model 'after' validators
         └─ set __dict__, __pydantic_fields_set__, __pydantic_extra__, __pydantic_private__
```

- `model_validate_json` feeds bytes directly to **jiter**, which parses and validates in one pass, without first building a Python `dict` — that's why it's faster than `json.loads` + `model_validate`.
- Python-function validators (`@field_validator` etc.) are calls *back* from Rust into Python. Each one costs a boundary crossing — fine in moderation, but a model with dozens of Python validators is slower than one using native constraints.
- Errors are accumulated as "line errors" and raised as one `ValidationError` (a Rust type subclassing `ValueError`).

Serialization mirrors this: `model_dump` → `__pydantic_serializer__.to_python(self, ...)` and `model_dump_json` → `.to_json(...)`, which writes JSON bytes directly in Rust.

## 5. Inspecting and using `pydantic-core` directly

You rarely need to, but `pydantic-core` can be used on its own — useful for understanding or for ultra-specialized validators:

```python
from pydantic_core import SchemaValidator, ValidationError, core_schema

v = SchemaValidator(
    core_schema.typed_dict_schema(
        {
            "name": core_schema.typed_dict_field(core_schema.str_schema(min_length=1)),
            "age": core_schema.typed_dict_field(core_schema.int_schema(ge=0)),
        }
    )
)
print(v.validate_json('{"name": "Ada", "age": "36"}'))
#> {'name': 'Ada', 'age': 36}
try:
    v.validate_python({"name": "", "age": -1})
except ValidationError as e:
    print(e.error_count())
    #> 2
```

`pydantic_core.from_json(data, allow_partial=True)` and `to_json(obj)` are also handy — the former parses **incomplete JSON** (e.g. streamed LLM output) and is what powers partial validation (`experimental_allow_partial` on `TypeAdapter.validate_json`).

## 6. Annotation resolution in detail

Pydantic must turn annotation *strings* (from `from __future__ import annotations` or quoted names) into real types. It uses:

- the **module globals** of the class,
- the **parent frame locals** (for models defined inside functions),
- the **class namespace** itself (for self-references),
- and, for `model_rebuild(_types_namespace=...)`, any namespace you pass explicitly.

On Python 3.14+, annotations are evaluated lazily (PEP 649/749); Pydantic uses `annotationlib` formats (trying `VALUE` before `FORWARDREF` since 2.14) and supports Python 3.15 `lazy import`s. Pydantic 2.14 removed the `eval_type_backport` fallback that allowed `X | Y` syntax on very old Pythons — irrelevant now that 3.10 is the minimum.

## 7. Plugins and observability hooks

`pydantic.plugin` exposes a plugin protocol: a plugin is notified whenever a validator is created and can wrap `validate_python` / `validate_json` / `validate_strings` calls with `on_enter` / `on_success` / `on_error` handlers. Plugins are discovered through the `pydantic` entry-point group.

This is how **Logfire** records every validation (inputs, durations, errors) with one line:

```py
import logfire
logfire.configure()
logfire.instrument_pydantic()   # or record='failure' to log only failed validations
```

## 8. Concurrency and free-threading

- Validators and serializers are immutable once built and safe to share across threads.
- `pydantic-core` ships wheels for **free-threaded** CPython (3.13t/3.14t), and 2.13–2.14 fixed several race conditions (including thread-safe model rebuilding).
- Model instances are ordinary Python objects: mutating a shared instance across threads needs your usual synchronization (or use `frozen=True`).

## 9. Memory and performance internals worth knowing

- **Schema building dominates import time** in large apps (hundreds of models). 2.11–2.14 brought large build-time improvements (schema reuse, faster `FieldInfo` construction, Rust-side schema gathering). `defer_build=True` moves the cost to first use.
- **Generic parametrizations are cached**, so `Page[User]` is built once.
- **Model instances** store data in `__dict__` plus `__pydantic_fields_set__`, `__pydantic_extra__`, `__pydantic_private__`. The Pydantic team has been exploring bitset-based `fields_set` tracking to reduce per-instance memory.
- **Strings** in JSON parsing are cached (`cache_strings` config) to reduce allocations for repeated keys/values.

---

## Summary

- `pydantic` (Python) translates type hints into a **core schema**; `pydantic-core` (Rust) compiles it into validator/serializer trees.
- Model definition triggers field collection → annotation resolution → schema generation → compilation; incomplete models get mock validators until rebuilt.
- `model_validate_json` uses jiter for single-pass parse + validate.
- Python validators call back across the Rust/Python boundary — native constraints are faster.
- The plugin API powers observability tools like Logfire.

**Next:** [12 — Architecture Patterns and Performance](12-architecture-patterns-and-performance.md)
