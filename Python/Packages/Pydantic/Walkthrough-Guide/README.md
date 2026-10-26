# Pydantic in Python — A Complete Guide

From first model to internals, architecture, and the integration ecosystem — written for **Pydantic 2.14** (current as of October 2026) on **Python 3.10+**.

Every runnable code block in this guide was executed against Pydantic 2.14.1 / pydantic-core 2.50.1 on Python 3.13, and the `#>` comments show the actual output. Blocks marked as ` ```py ` (instead of ` ```python `) are illustrative snippets that need external services, API keys, or a surrounding project.

## How to read this guide

The chapters build on each other. Beginners should read 01–05 in order; experienced users can jump to the chapter they need.

| # | Chapter | Level | You will learn |
|---|---|---|---|
| 01 | [Introduction and Setup](01-introduction-and-setup.md) | 🟢 Beginner | What Pydantic is, installation, version landscape, first model, `ValidationError` |
| 02 | [Models (`BaseModel`)](02-models.md) | 🟢 Beginner | Defining, validating, inspecting, copying, nesting and inheriting models; extra data; private attributes; `RootModel`; `create_model` |
| 03 | [Fields and Types](03-fields-and-types.md) | 🟢 Beginner | `Field()`, `Annotated` constraints, the type catalog, `MISSING`, computed fields |
| 04 | [Validators](04-validators.md) | 🟢→🟡 | Before/after/plain/wrap validators, field vs model validators, custom errors, context |
| 05 | [Serialization](05-serialization.md) | 🟢→🟡 | `model_dump`/`model_dump_json`, include/exclude, aliases, custom serializers, polymorphic serialization |
| 06 | [Configuration and Strict Mode](06-configuration-and-strict-mode.md) | 🟡 Intermediate | `ConfigDict` options, project base models, lax vs strict validation |
| 07 | [Unions, Generics, and Recursive Models](07-unions-generics-and-recursive-models.md) | 🟡→🔴 | Smart unions, discriminated unions, generic models, recursive types |
| 08 | [TypeAdapter, Dataclasses, `@validate_call`](08-typeadapter-dataclasses-validate-call.md) | 🟡 Intermediate | Validating any type, Pydantic dataclasses, validated functions, `TypedDict` |
| 09 | [JSON Schema](09-json-schema.md) | 🟡→🔴 | Generating and customizing schemas, schema-first workflows, schemas for LLMs |
| 10 | [Custom Types](10-custom-types.md) | 🔴 Advanced | `Annotated` composition, `__get_pydantic_core_schema__`, adapting third-party types |
| 11 | [Internals: How Pydantic Works](11-internals.md) | 🔴 Advanced | `pydantic` vs `pydantic-core`, core schemas, model build & validation flow, plugins |
| 12 | [Architecture Patterns and Performance](12-architecture-patterns-and-performance.md) | 🔴 Advanced | Layering, schema families, versioning, security, testing, performance tuning |
| 13 | [Integration: pydantic-settings](13-integration-pydantic-settings.md) | 🟡→🔴 | Env vars, `.env`, secrets, config files, cloud secret managers, CLI apps |
| 14 | [Integrations: Web Frameworks and Databases](14-integrations-web-and-databases.md) | 🟡→🔴 | FastAPI, SQLAlchemy, SQLModel, Litestar, Django Ninja, ODMs, HTTP clients, queues |
| 15 | [Integrations: AI/LLMs and Tooling](15-integrations-ai-and-tooling.md) | 🟡→🔴 | Pydantic AI, structured LLM output, Logfire, mypy/pyright, Ruff, polyfactory, Hypothesis |
| 16 | [Migration (V1 → V2) and What's New](16-migration-and-whats-new.md) | 📖 Reference | V1→V2 mapping, behavior changes, release notes for 2.11–2.14, V3 readiness |

🟢 Beginner · 🟡 Intermediate · 🔴 Advanced · 📖 Reference

## Suggested learning paths

- **"I just need to validate some JSON"** → 01, 02, 03, 05 (section 1), 08 (section 1).
- **Building a FastAPI service** → 01–06, 07 (discriminated unions), 12 (Part A), 13, 14.
- **Building LLM / agent applications** → 01–05, 07, 09, 15.
- **Library author / power user** → 06–11, then 12 (Part B).
- **Upgrading an old codebase** → 16, then 06 and 05 for the behaviors that changed.

## Version snapshot (October 15, 2026)

| Package | Version used | Notes |
|---|---|---|
| `pydantic` | 2.14.1 | Python 3.10–3.15; `MISSING` stable; `pydantic.v1` not supported on 3.14+ |
| `pydantic-core` | 2.50.1 | Rust core; installed automatically with a pinned compatible version |
| `pydantic-settings` | 2.16.0 | Settings, secrets, cloud sources, CLI |
| `pydantic-ai` | 2.x | Agent framework (2.0 stable since June 2026) |
| FastAPI | 0.143 | Requires Pydantic v2 (since 0.128) |
| SQLModel | 0.0.48 | Pydantic v2 only |

## Official resources

- Documentation: <https://pydantic.dev/docs/validation/latest/get-started/>
- Changelog: <https://pydantic.dev/docs/validation/latest/get-started/changelog/>
- Release posts: [v2.14](https://pydantic.dev/articles/pydantic-v2-14-release) · [v2.13](https://pydantic.dev/articles/pydantic-v2-13-release) · [v2.12](https://pydantic.dev/articles/pydantic-v2-12-release)
- Source: <https://github.com/pydantic/pydantic>
- Error reference: `https://errors.pydantic.dev/<version>/v/<error_type>`
