# 13 — Integration: `pydantic-settings`

> **Level:** Intermediate → Advanced · **Package:** `pydantic-settings` (2.16 at time of writing) · **Prerequisite:** [06 — Configuration and Strict Mode](06-configuration-and-strict-mode.md)

`pydantic-settings` turns application configuration — environment variables, `.env` files, secret files, CLI arguments, JSON/YAML/TOML files, and cloud secret managers — into a **validated, typed object**. It is a separate package maintained by the Pydantic team.

```bash
pip install pydantic-settings
pip install "pydantic-settings[yaml]"        # YAML sources
pip install "pydantic-settings[toml]"        # TOML sources on Python < 3.11
pip install "pydantic-settings[aws-secrets-manager]"   # also: azure-key-vault, gcp-secret-manager
```

---

## 1. The basics

```python
import os
from pydantic import Field, PostgresDsn, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="APP_")

    debug: bool = False
    port: int = 8000
    database_url: PostgresDsn
    api_key: SecretStr
    allowed_hosts: list[str] = ["localhost"]    # complex types are parsed from JSON
    workers: int = Field(default=4, ge=1, le=64)


os.environ.update(
    {
        "APP_DEBUG": "true",
        "APP_DATABASE_URL": "postgres://user:pw@db:5432/app",
        "APP_API_KEY": "s3cr3t",
        "APP_ALLOWED_HOSTS": '["example.com", "api.example.com"]',
    }
)

settings = Settings()
print(settings.debug, settings.port, settings.allowed_hosts)
#> True 8000 ['example.com', 'api.example.com']
print(settings.database_url.hosts()[0]["host"])   # PostgresDsn is multi-host aware → .hosts()
#> db
print(settings.api_key)
#> **********
```

- `BaseSettings` is a `BaseModel` subclass: all validation, types, validators and serialization work the same.
- Field `database_url` reads env var `APP_DATABASE_URL` (prefix + field name). Matching is **case-insensitive** by default (`case_sensitive=True` to change).
- Missing required settings raise a `ValidationError` **at startup** — fail fast, not in the middle of a request.
- Complex types (`list`, `dict`, sub-models) are decoded from **JSON strings** by default.

## 2. Source priority

When the same setting is defined in several places, the default priority (highest first) is:

1. **Init kwargs** — `Settings(port=9000)`
2. **CLI arguments** (when CLI parsing is enabled)
3. **Environment variables**
4. **`.env` file(s)**
5. **Secrets directory** (`secrets_dir`)
6. **Field defaults**

You can reorder, remove, or add sources (section 7).

## 3. `.env` files

```py
class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", ".env.local"),   # later files override earlier ones
        env_file_encoding="utf-8",
        extra="ignore",                    # ignore unrelated vars in the .env
    )
```

You can override at runtime: `Settings(_env_file="prod.env")`. Real environment variables always beat `.env` values.

## 4. Nested settings

```python
import os
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseModel):          # sub-models are plain BaseModel
    host: str = "localhost"
    port: int = 5432
    pool_size: int = 5


class RedisSettings(BaseModel):
    url: str = "redis://localhost:6379/0"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_nested_delimiter="__")
    db: DatabaseSettings = DatabaseSettings()
    redis: RedisSettings = RedisSettings()


os.environ["DB__HOST"] = "db.internal"
os.environ["DB__POOL_SIZE"] = "20"
os.environ["REDIS"] = '{"url": "redis://cache:6379/1"}'     # whole sub-model as JSON also works

s = Settings()
print(s.db, s.redis.url)
#> host='db.internal' port=5432 pool_size=20 redis://cache:6379/1
```

Related options: `env_nested_max_split` (limit splitting, useful when field names contain the delimiter), `nested_model_default_partial_update=True` (env vars update a sub-model's default instead of replacing it).

## 5. Aliases and parsing details

```python
import os
from typing import Annotated
from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, NoDecode
from pydantic import field_validator


class Settings(BaseSettings):
    # read from REDIS_URL or, as a fallback, CACHE_URL (prefix is NOT applied to aliases)
    redis_url: str = Field(validation_alias=AliasChoices("REDIS_URL", "CACHE_URL"))
    # accept a comma-separated list instead of JSON
    features: Annotated[list[str], NoDecode] = []

    @field_validator("features", mode="before")
    @classmethod
    def split(cls, v):
        return [x.strip() for x in v.split(",")] if isinstance(v, str) else v


os.environ["CACHE_URL"] = "redis://legacy:6379"
os.environ["FEATURES"] = "search, billing"
print(Settings().model_dump())
#> {'redis_url': 'redis://legacy:6379', 'features': ['search', 'billing']}
```

- `NoDecode` disables JSON decoding for one field; `ForceDecode` does the opposite when `enable_decoding=False` globally.
- `env_parse_none_str="null"` makes the string `"null"` become `None`.
- `env_ignore_empty=True` treats empty env vars as unset.

## 6. Secrets: files and cloud secret managers

### Docker / Kubernetes secret files

```py
class Settings(BaseSettings):
    model_config = SettingsConfigDict(secrets_dir="/run/secrets")
    db_password: SecretStr      # read from the file /run/secrets/db_password
```

`NestedSecretsSettingsSource` supports nested directories mapped to nested models.

### Cloud providers

`pydantic-settings` ships sources for **AWS Secrets Manager**, **AWS Systems Manager Parameter Store**, **Azure Key Vault**, and **Google Secret Manager**. You enable them through `settings_customise_sources`:

```py
from pydantic_settings import (
    AWSSecretsManagerSettingsSource, BaseSettings, PydanticBaseSettingsSource,
)

class Settings(BaseSettings):
    db_password: str

    @classmethod
    def settings_customise_sources(cls, settings_cls, init_settings, env_settings,
                                   dotenv_settings, file_secret_settings):
        aws = AWSSecretsManagerSettingsSource(settings_cls, secret_id="prod/my-app")
        return (init_settings, env_settings, aws, dotenv_settings, file_secret_settings)
```

## 7. Customizing sources and adding config files

```python
import json, tempfile, os
from pydantic_settings import (
    BaseSettings,
    JsonConfigSettingsSource,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)

cfg = os.path.join(tempfile.mkdtemp(), "config.json")
with open(cfg, "w") as f:
    json.dump({"name": "from-json", "replicas": 3}, f)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(json_file=cfg)
    name: str = "default"
    replicas: int = 1

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        # env vars override the JSON file; the JSON file overrides defaults
        return (init_settings, env_settings, JsonConfigSettingsSource(settings_cls))


os.environ["REPLICAS"] = "5"
print(Settings().model_dump())
#> {'name': 'from-json', 'replicas': 5}
```

Built-in file sources: `JsonConfigSettingsSource`, `YamlConfigSettingsSource`, `TomlConfigSettingsSource`, `PyprojectTomlConfigSettingsSource` (reads `[tool.<your-app>]` from `pyproject.toml`). Write your own by subclassing `PydanticBaseSettingsSource` (e.g. Vault, Consul, a database table).

## 8. Command-line interfaces

`pydantic-settings` includes a full CLI layer: a settings class *is* an argparse-style CLI.

```python
from pydantic import Field
from pydantic_settings import BaseSettings, CliApp, CliPositionalArg, CliSubCommand
from pydantic import BaseModel


class Serve(BaseModel):
    """Start the server."""
    port: int = Field(default=8000, description="Port to listen on")
    reload: bool = False

    def cli_cmd(self) -> None:
        print(f"serving on {self.port} reload={self.reload}")


class Migrate(BaseModel):
    """Run database migrations."""
    target: CliPositionalArg[str]

    def cli_cmd(self) -> None:
        print(f"migrating to {self.target}")


class Tool(BaseSettings, cli_prog_name="tool"):
    serve: CliSubCommand[Serve]
    migrate: CliSubCommand[Migrate]

    def cli_cmd(self) -> None:
        CliApp.run_subcommand(self)


CliApp.run(Tool, cli_args=["serve", "--port", "9000", "--reload", "true"])
#> serving on 9000 reload=True
CliApp.run(Tool, cli_args=["migrate", "head"])
#> migrating to head
```

- `CliApp.run(Model)` parses `sys.argv` (or `cli_args`), validates, and calls `cli_cmd()`.
- Nested models become dotted flags (`--db.host`), `list` fields accept repeated flags or JSON, `--help` is generated from descriptions/docstrings.
- Extras: `CliPositionalArg`, `CliSubCommand`, `CliImplicitFlag`/`CliExplicitFlag`/`CliToggleFlag`, `CliMutuallyExclusiveGroup`, `CliUnknownArgs`, `CLI_SUPPRESS`, async `cli_cmd`.
- Or simply set `cli_parse_args=True` in config to let any settings class read CLI flags with highest priority after init kwargs.

## 9. Patterns for real applications

### A single cached settings instance

```py
from functools import lru_cache

@lru_cache
def get_settings() -> Settings:
    return Settings()
```

In FastAPI, inject with `Depends(get_settings)` and override in tests via `app.dependency_overrides[get_settings] = lambda: Settings(debug=True, ...)`.

### Per-environment configuration

```py
import os

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=f".env.{os.getenv('APP_ENV', 'dev')}")
```

### Testing

Construct settings with explicit kwargs (highest priority), or use `monkeypatch.setenv` in pytest. Pass `_env_file=None` to make sure a developer's local `.env` doesn't leak into tests.

### Reloading

`settings.__init__()` re-reads all sources in place (handy for config reload signals), though rebuilding a new instance is usually cleaner.

---

## Summary

- `BaseSettings` validates configuration from env vars, `.env`, secret files, config files, CLI, and cloud secret managers.
- Priority: init kwargs > CLI > env > `.env` > secrets > defaults — customizable via `settings_customise_sources`.
- Nested models via `env_nested_delimiter="__"`; complex values via JSON (or `NoDecode` + a validator).
- `CliApp` turns settings classes into full CLIs with subcommands.

**Next:** [14 — Integrations: Web Frameworks and Databases](14-integrations-web-and-databases.md)
