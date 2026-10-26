# 15 — Integrations: AI/LLMs and Developer Tooling

> **Level:** Intermediate → Advanced · **Prerequisite:** [09 — JSON Schema](09-json-schema.md)
>
> Versions referenced (October 2026): Pydantic AI 2.x (stable 2.0 released June 2026), Logfire, mypy 2.x, pyright, polyfactory 3.x, Hypothesis 6.x.

Pydantic has become the standard way to give LLMs a **contract**: JSON Schema in, validated objects out. This chapter covers Pydantic AI (the Pydantic team's agent framework), structured output with provider SDKs and other frameworks, observability with Logfire, and the developer tooling around Pydantic.

---

## Part A — AI and LLMs

### 1. Why Pydantic fits LLM work

LLMs produce text; applications need typed data. Pydantic closes the gap in both directions:

1. **Describe** — `model_json_schema()` turns your model (including docstrings, field descriptions, enums, constraints) into the schema the model is asked to follow, or into tool definitions.
2. **Validate** — `model_validate_json()` checks the model's answer. On failure, the `ValidationError` text is a precise, LLM-readable explanation of what to fix, which frameworks feed back for an automatic retry.
3. **Stream** — `pydantic_core.from_json(..., allow_partial=True)` and `TypeAdapter.validate_json(..., experimental_allow_partial=True)` parse incomplete JSON, enabling partial structured results while tokens stream.

### 2. Pydantic AI

[Pydantic AI](https://pydantic.dev/docs/ai/) is a model-agnostic agent framework built on Pydantic (OpenAI, Anthropic, Google, Mistral, Groq, Bedrock, Ollama, OpenRouter and more). Its 2.0 stable release landed in June 2026.

```bash
pip install pydantic-ai          # all providers
pip install "pydantic-ai-slim[anthropic]"   # or only what you need
```

#### Structured output, dependencies, tools

```python
import os
from dataclasses import dataclass

from pydantic import BaseModel, Field
from pydantic_ai import Agent, ModelRetry, RunContext
from pydantic_ai.models.test import TestModel

os.environ.setdefault("PYDANTIC_AI_NO_BANNER", "1")


@dataclass
class SupportDeps:                        # injected per run: DB handles, user info, HTTP clients…
    customer_name: str
    balances: dict[str, float]


class SupportReply(BaseModel):
    """Reply to send to the customer."""

    reply: str = Field(description="Message shown to the customer")
    escalate: bool = Field(description="True if a human must take over")
    risk: int = Field(ge=0, le=10, description="Fraud/abuse risk score")


support_agent = Agent(
    "anthropic:claude-sonnet-5-5",        # any supported "provider:model" string
    deps_type=SupportDeps,
    output_type=SupportReply,             # the agent must return a validated SupportReply
    instructions="You are a bank support agent. Be concise.",
    defer_model_check=True,               # don't require API keys at import time (for this demo)
)


@support_agent.instructions
def personalise(ctx: RunContext[SupportDeps]) -> str:
    return f"The customer's name is {ctx.deps.customer_name}."


@support_agent.tool
def account_balance(ctx: RunContext[SupportDeps], account: str) -> float:
    """Return the current balance of the given account."""   # docstring → tool description
    if account not in ctx.deps.balances:
        raise ModelRetry(f"Unknown account {account!r}; valid: {list(ctx.deps.balances)}")
    return ctx.deps.balances[account]


# Tests/demo: swap in a deterministic fake model instead of calling a real LLM
fake = TestModel(call_tools=[], custom_output_args={"reply": "Hi Ada, your balance is $123.45.", "escalate": False, "risk": 1})
with support_agent.override(model=fake):
    result = support_agent.run_sync("What's my balance?", deps=SupportDeps("Ada", {"checking": 123.45}))

print(result.output)
#> reply='Hi Ada, your balance is $123.45.' escalate=False risk=1
print(type(result.output).__name__)
#> SupportReply
```

What Pydantic does under the hood:

- `output_type=SupportReply` → its JSON Schema becomes an **output tool** (or native structured-output / prompted mode — selectable with `ToolOutput`, `NativeOutput`, `PromptedOutput`). The response is validated; on `ValidationError` the errors are sent back to the model to retry (up to `retries`).
- Tool function **signatures** are converted to JSON Schema with Pydantic (parameter types, defaults, docstring descriptions). Arguments the model sends are validated before your function runs. Raise `ModelRetry` to ask the model to try again.
- Message history is (de)serializable with `ModelMessagesTypeAdapter` — a `TypeAdapter` — for storing conversations.
- `output_type` can be a union (`SupportReply | Refusal`), a `list[...]`, a `TypedDict`, a primitive, or a function whose arguments are validated.

Other notable features: streaming of validated partial output (`run_stream` / `stream_output`), multi-agent delegation, MCP client/server support, durable execution integrations, human-in-the-loop tool approval, and **Pydantic Evals** for systematic evaluation.

#### Testing agents

`TestModel` (used above) and `FunctionModel` (where you script responses in Python) let you unit-test agents with no network calls; `Agent.override(model=..., deps=...)` swaps them in without changing application code. Set `ALLOW_MODEL_REQUESTS = False` in `pydantic_ai.models` in your test suite to forbid accidental real calls.

### 3. Provider SDKs directly

Official SDKs accept Pydantic models for structured outputs. Illustrative shapes (check your SDK version's docs for exact method names):

```py
# OpenAI Python SDK
from openai import OpenAI
client = OpenAI()
completion = client.chat.completions.parse(
    model="gpt-5",
    messages=[{"role": "user", "content": "Extract the event: Lunch with Bo on Friday"}],
    response_format=CalendarEvent,            # a Pydantic model
)
event: CalendarEvent = completion.choices[0].message.parsed

# Anthropic Python SDK — tool definitions from a model's schema
import anthropic
client = anthropic.Anthropic()
msg = client.messages.create(
    model="claude-sonnet-5-5",
    max_tokens=1024,
    tools=[{"name": "record_event", "description": CalendarEvent.__doc__,
            "input_schema": CalendarEvent.model_json_schema()}],
    tool_choice={"type": "tool", "name": "record_event"},
    messages=[{"role": "user", "content": "Lunch with Bo on Friday"}],
)
tool_use = next(b for b in msg.content if b.type == "tool_use")
event = CalendarEvent.model_validate(tool_use.input)   # always validate
```

The SDKs themselves model their request/response types with Pydantic, so responses are objects you can `.model_dump()`.

### 4. Other frameworks

| Library | Pydantic role |
|---|---|
| **Instructor** | Patches provider clients so `response_model=MyModel` returns validated instances, with automatic retries on validation errors |
| **LangChain / LangGraph** | `llm.with_structured_output(MyModel)`; tool args schemas; graph state can be a Pydantic model |
| **LlamaIndex** | Structured outputs and program classes from Pydantic models |
| **DSPy** | Typed signatures/predictors validated with Pydantic |
| **Outlines** | Constrained decoding from a Pydantic model's JSON Schema (guaranteed-valid JSON for local models) |
| **MCP Python SDK / FastMCP** | Tool input/output schemas generated from type hints & Pydantic models |

### 5. Designing models for LLMs — checklist

- Docstrings and `Field(description=...)` are **prompts**. Be explicit about units, formats, and edge cases.
- Prefer `Literal[...]` / `Enum` for categorical values; keep nesting shallow.
- Add an escape hatch (`answer: X | None`, or a `Refusal` variant in a union) so the model isn't forced to hallucinate.
- Use constraints (`ge`, `le`, `max_length`) — validation failures become retry feedback.
- Keep `extra="forbid"` for providers' strict schema modes.
- Log every validation failure (Logfire, below) to find prompts/schemas that confuse the model.

### 6. Observability: Logfire

[Logfire](https://pydantic.dev/logfire) is Pydantic's OpenTelemetry-based observability platform with first-class Pydantic and Pydantic AI integrations:

```py
import logfire

logfire.configure()                         # token from env / `logfire auth`
logfire.instrument_pydantic()               # trace every model validation (or record="failure")
logfire.instrument_pydantic_ai()            # trace agent runs, tool calls, tokens, cost
logfire.instrument_fastapi(app)             # requests, with validation errors attached
```

Because it is built on OpenTelemetry, data can also be exported to other OTel backends.

---

## Part B — Developer tooling

### 7. Static type checking

Pydantic models are valid typed Python, and Pydantic uses `@dataclass_transform` (PEP 681), so **pyright/Pylance, mypy, and pyrefly** understand `Model(...)` signatures natively.

**mypy plugin** — adds stricter checks (e.g. init argument types, `Field` defaults, `from_attributes`):

```toml
# pyproject.toml
[tool.mypy]
plugins = ["pydantic.mypy"]

[tool.pydantic-mypy]
init_forbid_extra = true
init_typed = true                # flag Model(x="1") where x: int (disables lax-mode coercion in type-checking)
warn_required_dynamic_aliases = true
```

Notes: `MISSING` is understood from pyright 1.1.414 / mypy 2.4, and `TypeAdapter` return types are inferred from `TypeForm` from pyright 1.1.412 / mypy 2.2. Pydantic only supports the latest mypy release with its plugin.

### 8. Linting

**Ruff** has Pydantic-aware behavior: configure `lint.flake8-type-checking.runtime-evaluated-base-classes = ["pydantic.BaseModel", "pydantic_settings.BaseSettings"]` so Ruff doesn't move imports needed at runtime by Pydantic into `TYPE_CHECKING` blocks. Rules like `RUF012` (mutable class defaults) understand Pydantic models.

### 9. IDEs

- **VS Code / Pylance** and **PyCharm** (built-in Pydantic support) autocomplete fields and constructor arguments and flag type errors.
- Pydantic also publishes official **agent skills** (2026) to teach AI coding assistants current Pydantic idioms.

### 10. Testing helpers

```python
from typing import Annotated
from hypothesis import given, settings, strategies as st
from polyfactory.factories.pydantic_factory import ModelFactory
from pydantic import BaseModel, EmailStr, Field


class User(BaseModel):
    id: Annotated[int, Field(gt=0)]
    email: EmailStr
    tags: list[str] = Field(default=[], max_length=3)


# polyfactory: realistic instances that respect constraints
class UserFactory(ModelFactory[User]):
    __random_seed__ = 42


users = UserFactory.batch(5)
print(all(u.id > 0 and len(u.tags) <= 3 for u in users))
#> True


# Hypothesis: property-based testing. st.builds understands annotated constraints on
# standard types; Pydantic-specific types like EmailStr need an explicit strategy.
@settings(max_examples=25)
@given(st.builds(User, email=st.emails()))
def test_roundtrip(user: User):
    assert User.model_validate_json(user.model_dump_json()) == user


test_roundtrip()
print("round-trip property holds")
#> round-trip property holds
```

### 11. Code generation and conversion

| Tool | Direction |
|---|---|
| **datamodel-code-generator** | JSON Schema / OpenAPI / JSON / YAML / GraphQL → Pydantic v2 models |
| **bump-pydantic** | Automated V1 → V2 code migration (see chapter 16) |
| **pydantic-to-typescript** & JSON-Schema-to-TS tools | Pydantic → TypeScript interfaces via JSON Schema |
| `model_json_schema()` | Pydantic → JSON Schema for any other language's generators |

### 12. Debugging and display

- **devtools** (`from devtools import debug; debug(model)`) pretty-prints models with types.
- **Rich** renders models nicely (`rich.print(model)`, `rich.pretty`) via `__rich_repr__`.
- `pydantic.version.version_info()` — paste into bug reports.
- Every error message includes a docs URL (`https://errors.pydantic.dev/<version>/v/<error_type>`) explaining the error type.

---

## Summary

- Pydantic is the contract layer for LLM apps: schema out, validation in, errors as retry feedback.
- Pydantic AI (2.x stable) builds agents around Pydantic output types, validated tools, and dependency injection; `TestModel`/`FunctionModel` make agents testable offline.
- Provider SDKs, Instructor, LangChain, Outlines, and MCP SDKs all accept Pydantic models.
- Logfire instruments Pydantic, Pydantic AI and web frameworks via OpenTelemetry.
- Tooling: mypy plugin / pyright / pyrefly, Ruff config, polyfactory & Hypothesis for tests, datamodel-code-generator for codegen.

**Next:** [16 — Migration (V1 → V2) and What's New](16-migration-and-whats-new.md)
