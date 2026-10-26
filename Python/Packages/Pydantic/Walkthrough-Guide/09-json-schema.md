# 09 — JSON Schema

> **Level:** Intermediate → Advanced · **Prerequisite:** [08 — TypeAdapter, Dataclasses, and `@validate_call`](08-typeadapter-dataclasses-validate-call.md)

Every Pydantic type can describe itself as **JSON Schema** (Draft 2020-12, compatible with OpenAPI 3.1). This is what powers FastAPI's interactive docs, LLM "structured output" / tool calling, form generators, and contract testing.

---

## 1. Generating a schema

```python
import json
from typing import Literal
from pydantic import BaseModel, Field


class Address(BaseModel):
    street: str
    city: str


class User(BaseModel):
    """A registered user."""

    id: int = Field(ge=1, description="Primary key")
    name: str = Field(min_length=1, examples=["Ada Lovelace"])
    role: Literal["admin", "member"] = "member"
    address: Address | None = None


print(json.dumps(User.model_json_schema(), indent=2))
```

```json
{
  "$defs": {
    "Address": {
      "properties": {
        "street": {"title": "Street", "type": "string"},
        "city": {"title": "City", "type": "string"}
      },
      "required": ["street", "city"],
      "title": "Address",
      "type": "object"
    }
  },
  "description": "A registered user.",
  "properties": {
    "id": {"description": "Primary key", "minimum": 1, "title": "Id", "type": "integer"},
    "name": {"examples": ["Ada Lovelace"], "minLength": 1, "title": "Name", "type": "string"},
    "role": {"default": "member", "enum": ["admin", "member"], "title": "Role", "type": "string"},
    "address": {"anyOf": [{"$ref": "#/$defs/Address"}, {"type": "null"}], "default": null}
  },
  "required": ["id", "name"],
  "title": "User",
  "type": "object"
}
```

Observations:

- The class docstring becomes `description`; `Field(description=...)` documents fields (or use `use_attribute_docstrings=True`).
- Nested models go into `$defs` and are referenced with `$ref`.
- Constraints map to JSON Schema keywords (`ge` → `minimum`, `min_length` → `minLength`, `pattern` → `pattern`).
- `Literal` → `enum` (or `const` for one value); `X | None` → `anyOf` with `null`.

For other types use `TypeAdapter(T).json_schema()`. For several models sharing `$defs` (e.g. an OpenAPI document), use `pydantic.json_schema.models_json_schema([(A, "validation"), (B, "serialization")])`.

## 2. Validation vs. serialization schemas

Input and output shapes can differ — computed fields, aliases, serializers, defaults:

```python
from pydantic import BaseModel, Field, computed_field


class Item(BaseModel):
    price: float
    qty: int = 1
    internal: str = Field(default="", exclude=True)

    @computed_field
    @property
    def total(self) -> float:
        return self.price * self.qty


print(Item.model_json_schema(mode="validation")["required"])
#> ['price']
ser = Item.model_json_schema(mode="serialization")
print(sorted(ser["properties"]), ser["required"])
#> ['price', 'qty', 'total'] ['price', 'total']
```

FastAPI uses the *validation* schema for request bodies and the *serialization* schema for responses. Set `json_schema_serialization_defaults_required=True` to mark defaulted fields as required in serialization schemas (they're always present in output).

## 3. Customizing the schema

### Per field

```python
from pydantic import BaseModel, Field


class Upload(BaseModel):
    filename: str = Field(
        title="File name",
        description="Name including extension",
        examples=["report.pdf"],
        json_schema_extra={"x-ui-widget": "file"},
    )
    legacy_id: int | None = Field(default=None, deprecated=True)


props = Upload.model_json_schema()["properties"]
print(props["filename"]["x-ui-widget"], props["legacy_id"]["deprecated"])
#> file True
```

### Per model

```python
from typing import Any
from pydantic import BaseModel, ConfigDict


def add_examples(schema: dict[str, Any], cls: type) -> None:
    schema["examples"] = [{"sku": "ABC-1", "qty": 2}]
    schema["properties"].pop("debug", None)       # hide a field from docs


class Line(BaseModel):
    model_config = ConfigDict(title="OrderLine", json_schema_extra=add_examples)
    sku: str
    qty: int
    debug: bool = False


s = Line.model_json_schema()
print(s["title"], "debug" in s["properties"], s["examples"])
#> OrderLine False [{'qty': 2, 'sku': 'ABC-1'}]
```

### Per type, with `WithJsonSchema` or `Field(json_schema_extra=...)`

```python
from typing import Annotated
from pydantic import PlainValidator, TypeAdapter, WithJsonSchema

HexColor = Annotated[
    str,
    PlainValidator(lambda v: v if str(v).startswith("#") else f"#{v}"),
    WithJsonSchema({"type": "string", "pattern": "^#[0-9a-fA-F]{6}$", "format": "color"}),
]
print(TypeAdapter(HexColor).json_schema())
#> {'format': 'color', 'pattern': '^#[0-9a-fA-F]{6}$', 'type': 'string'}
```

`WithJsonSchema` is essential when a `PlainValidator` hides the underlying type from schema generation.

### Globally, by subclassing `GenerateJsonSchema`

```python
from pydantic import BaseModel
from pydantic.json_schema import GenerateJsonSchema


class NoTitles(GenerateJsonSchema):
    def field_title_should_be_set(self, schema) -> bool:
        return False

    def generate(self, schema, mode="validation"):
        result = super().generate(schema, mode=mode)
        result["$schema"] = self.schema_dialect
        return result


class P(BaseModel):
    x: int


print(P.model_json_schema(schema_generator=NoTitles))
#> {'properties': {'x': {'type': 'integer'}}, 'required': ['x'], 'title': 'P', 'type': 'object', '$schema': 'https://json-schema.org/draft/2020-12/schema'}
```

You can override handlers for specific core-schema kinds (e.g. `def decimal_schema(self, schema)`) to change how a type is rendered. Since 2.14, the regex `pattern` for `Decimal` is no longer emitted by default; a custom generator can add it back.

### Other knobs

| Option | Effect |
|---|---|
| `model_json_schema(by_alias=False)` | use Python field names instead of aliases |
| `ref_template="#/components/schemas/{model}"` | OpenAPI-style refs |
| `union_format="primitive_type_array"` (2.12+) | render `int \| str` as `{"type": ["integer", "string"]}` instead of `anyOf` |
| `field_title_generator` / `model_title_generator` config | compute titles |
| `json_schema_mode_override` config | force validation/serialization mode for a model |

## 4. Schema-first workflows

### Code from schema: `datamodel-code-generator`

```bash
pip install datamodel-code-generator
datamodel-codegen --input openapi.yaml --input-file-type openapi \
                  --output-model-type pydantic_v2.BaseModel --output models.py
```

Generates Pydantic v2 models from JSON Schema, OpenAPI, GraphQL, or raw JSON/YAML samples — ideal for consuming third-party APIs.

### Schema from code: publishing contracts

Export schemas in CI and diff them to catch breaking API changes:

```python
import json
from pathlib import Path
from pydantic import BaseModel


class EventV1(BaseModel):
    id: str
    amount: float


out = Path("schemas")
out.mkdir(exist_ok=True)
(out / "event.v1.json").write_text(json.dumps(EventV1.model_json_schema(), indent=2, sort_keys=True))
print((out / "event.v1.json").exists())
#> True
```

## 5. JSON Schema for LLMs

LLM providers accept JSON Schema to constrain outputs ("structured outputs") and to describe tools. Pydantic models are the de-facto way to write these schemas in Python:

```python
from typing import Literal
from pydantic import BaseModel, Field


class SentimentResult(BaseModel):
    """Classify the sentiment of a product review."""

    sentiment: Literal["positive", "neutral", "negative"]
    confidence: float = Field(ge=0, le=1)
    key_phrases: list[str] = Field(description="Short phrases that drove the decision", max_length=5)


schema = SentimentResult.model_json_schema()
# send `schema` as the response format / tool input schema, then:
llm_output = '{"sentiment": "positive", "confidence": 0.93, "key_phrases": ["fast shipping"]}'
print(SentimentResult.model_validate_json(llm_output))
#> sentiment='positive' confidence=0.93 key_phrases=['fast shipping']
```

Tips for LLM-facing schemas:

- Write good **docstrings and field descriptions** — they are effectively part of the prompt.
- Prefer `Literal`/`Enum` over free text for categorical outputs.
- Some providers' strict modes require `additionalProperties: false` (`extra="forbid"`) and all fields required; check your provider's supported subset.
- Always **validate** the response — even "guaranteed" structured outputs can violate value constraints.

See [15 — Integrations: AI and Tooling](15-integrations-ai-and-tooling.md) for Pydantic AI, which automates all of this.

---

## Summary

- `Model.model_json_schema()` / `TypeAdapter(T).json_schema()` produce Draft 2020-12 schemas, with separate validation and serialization modes.
- Customize at field (`Field(...)`, `json_schema_extra`), type (`WithJsonSchema`), model (`json_schema_extra` config), or global (`GenerateJsonSchema` subclass) level.
- JSON Schema powers OpenAPI docs, code generation, contract tests, and LLM structured output.

**Next:** [10 — Custom Types and the `Annotated` Pattern](10-custom-types.md)
