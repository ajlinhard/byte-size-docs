# 14 — Integrations: Web Frameworks and Databases

> **Level:** Intermediate → Advanced · **Prerequisite:** [12 — Architecture Patterns](12-architecture-patterns-and-performance.md)
>
> Versions used for the examples (October 2026): FastAPI 0.143, Starlette 1.6, SQLAlchemy 2.1, SQLModel 0.0.48, Litestar 2.24, Django 6.1 + Django Ninja 1.7, HTTPX.

Pydantic is the data layer of a large part of the Python web ecosystem. This chapter shows idiomatic usage with the most common frameworks and databases.

---

## 1. FastAPI

FastAPI uses Pydantic for **request parsing, validation, response serialization, and OpenAPI generation**. Recent FastAPI releases (≥ 0.128) **require Pydantic v2** — support for `pydantic.v1` models was removed.

### Request bodies, params, and response models

```python
from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.testclient import TestClient
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    email: EmailStr
    name: str = Field(min_length=1, max_length=50)
    password: str = Field(min_length=12)


class UserOut(BaseModel):
    id: int
    email: EmailStr
    name: str


class Pagination(BaseModel):
    limit: int = Field(10, ge=1, le=100)
    offset: int = Field(0, ge=0)


app = FastAPI()
DB: dict[int, dict] = {}


@app.post("/users", response_model=UserOut, status_code=201)
def create_user(body: UserCreate):
    uid = len(DB) + 1
    DB[uid] = {"id": uid, **body.model_dump()}
    return DB[uid]                 # password is filtered out by response_model


@app.get("/users", response_model=list[UserOut])
def list_users(page: Annotated[Pagination, Query()]):      # query params from a model
    return list(DB.values())[page.offset : page.offset + page.limit]


@app.get("/users/{user_id}")
def get_user(user_id: Annotated[int, Field(gt=0)]) -> UserOut:   # return annotation = response model
    if user_id not in DB:
        raise HTTPException(404)
    return UserOut.model_validate(DB[user_id])


client = TestClient(app)
r = client.post("/users", json={"email": "ada@x.org", "name": "Ada", "password": "correct-horse-battery"})
print(r.status_code, r.json())
#> 201 {'id': 1, 'email': 'ada@x.org', 'name': 'Ada'}

r = client.post("/users", json={"email": "nope", "name": "", "password": "short", "admin": True})
print(r.status_code, [e["type"] for e in r.json()["detail"]])
#> 422 ['value_error', 'string_too_short', 'string_too_short', 'extra_forbidden']

print(client.get("/users", params={"limit": 5}).json())
#> [{'id': 1, 'email': 'ada@x.org', 'name': 'Ada'}]
```

How it maps:

| FastAPI concept | Pydantic mechanism |
|---|---|
| JSON body parameter (`body: UserCreate`) | `model_validate_json` on the request body |
| Path/query/header params with constraints | `Annotated[int, Field(gt=0)]`, `Query()` models |
| `response_model=` or return annotation | validation + `model_dump` filtering of the return value |
| 422 error body | `ValidationError.errors()` |
| `/docs` and `/openapi.json` | `model_json_schema` (validation mode for inputs, serialization mode for outputs) |

### Useful patterns

- **Hide fields from output** by returning through a narrower `response_model` (`UserOut` without `password`), not by deleting keys manually.
- **`response_model_exclude_unset=True`** for sparse outputs.
- **Custom 422 format:** register an exception handler for `RequestValidationError` and translate `exc.errors()`.
- **Settings:** inject a `pydantic-settings` object via `Depends(get_settings)` (chapter 13).
- **Return models directly** (`return UserOut(...)`) — FastAPI serializes them with Pydantic's Rust serializer.

## 2. SQLAlchemy 2.x

SQLAlchemy owns persistence; Pydantic owns the API contract. Bridge them with `from_attributes=True`.

```python
from datetime import datetime
from sqlalchemy import ForeignKey, String, create_engine, func, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship
from pydantic import BaseModel, ConfigDict


# ---------- ORM (infrastructure) ----------
class Base(DeclarativeBase):
    pass


class AuthorRow(Base):
    __tablename__ = "authors"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    books: Mapped[list["BookRow"]] = relationship(back_populates="author")


class BookRow(Base):
    __tablename__ = "books"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    author_id: Mapped[int] = mapped_column(ForeignKey("authors.id"))
    author: Mapped[AuthorRow] = relationship(back_populates="books")


# ---------- Pydantic (API schemas) ----------
class BookOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str


class AuthorOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    books: list[BookOut]          # nested relationship read via attributes


class BookIn(BaseModel):
    title: str
    author_id: int


engine = create_engine("sqlite://")
Base.metadata.create_all(engine)

with Session(engine) as s:
    s.add(AuthorRow(name="Le Guin"))
    s.flush()
    payload = BookIn.model_validate({"title": "The Dispossessed", "author_id": 1})
    s.add(BookRow(**payload.model_dump()))          # Pydantic → ORM
    s.commit()

    author = s.scalars(select(AuthorRow)).one()
    print(AuthorOut.model_validate(author).model_dump())   # ORM → Pydantic
    #> {'id': 1, 'name': 'Le Guin', 'books': [{'id': 1, 'title': 'The Dispossessed'}]}
```

Tips:

- Serialize **inside** the session (or eager-load relationships with `selectinload`) — accessing lazy relationships after the session closes raises `DetachedInstanceError`.
- Beware of N+1 queries: `from_attributes` happily triggers lazy loads for every nested relationship it touches.
- Keep ORM classes and Pydantic schemas separate; the schema family pattern (`Create`/`Update`/`Read`) from chapter 12 applies directly.
- For JSON columns, validate their contents with a `TypeAdapter` on read/write.

## 3. SQLModel

SQLModel (by FastAPI's author) merges SQLAlchemy tables and Pydantic models into one class. Models declared with `table=True` are tables; models without it are pure Pydantic schemas. Current releases support Pydantic v2 only.

```python
from sqlmodel import Field, Session, SQLModel, create_engine, select


class HeroBase(SQLModel):
    name: str = Field(index=True, min_length=1)
    age: int | None = Field(default=None, ge=0)


class Hero(HeroBase, table=True):          # a DB table
    id: int | None = Field(default=None, primary_key=True)
    secret_name: str


class HeroCreate(HeroBase):                # request schema (not a table)
    secret_name: str


class HeroPublic(HeroBase):                # response schema
    id: int


engine = create_engine("sqlite://")
SQLModel.metadata.create_all(engine)

with Session(engine) as session:
    data = HeroCreate(name="Deadpond", secret_name="Dive Wilson", age=30)
    hero = Hero.model_validate(data)       # schema → table model
    session.add(hero)
    session.commit()
    session.refresh(hero)
    row = session.exec(select(Hero).where(Hero.name == "Deadpond")).one()
    print(HeroPublic.model_validate(row))
    #> name='Deadpond' age=30 id=1
```

⚠️ **Table models (`table=True`) do not validate on `__init__`** — they behave like SQLAlchemy objects for performance and ORM compatibility. Validate input with a non-table schema and convert via `Table.model_validate(schema)`, as above.

**SQLModel vs. SQLAlchemy + Pydantic:** SQLModel removes duplication for CRUD-heavy apps and pairs naturally with FastAPI. Plain SQLAlchemy + separate Pydantic schemas gives more control (advanced mappings, complex relationships, a strict layer boundary).

## 4. Litestar

Litestar supports Pydantic models natively for request/response bodies and OpenAPI, plus DTOs for field filtering:

```python
from litestar import Litestar, post
from litestar.testing import TestClient
from pydantic import BaseModel, Field


class Note(BaseModel):
    title: str = Field(min_length=1)
    body: str = ""


@post("/notes")
async def create_note(data: Note) -> Note:
    return data.model_copy(update={"title": data.title.upper()})


app = Litestar([create_note])
with TestClient(app) as client:
    r = client.post("/notes", json={"title": "hello"})
    print(r.status_code, r.json())
    #> 201 {'title': 'HELLO', 'body': ''}
    print(client.post("/notes", json={"title": ""}).status_code)
    #> 400
```

`litestar.plugins.pydantic.PydanticDTO` lets you exclude/rename fields per route without writing separate schemas.

## 5. Django: Django Ninja

Django Ninja brings FastAPI-style, Pydantic-powered APIs to Django. Its `Schema` is a Pydantic `BaseModel` subclass, and `ModelSchema` generates schemas from Django models:

```py
# api.py (inside a configured Django project)
from ninja import ModelSchema, NinjaAPI, Schema
from .models import Article

api = NinjaAPI()

class ArticleIn(Schema):
    title: str
    body: str

class ArticleOut(ModelSchema):
    class Meta:
        model = Article
        fields = ["id", "title", "body", "created_at"]

@api.post("/articles", response={201: ArticleOut})
def create_article(request, payload: ArticleIn):
    return 201, Article.objects.create(**payload.model_dump())

@api.get("/articles", response=list[ArticleOut])
def list_articles(request):
    return Article.objects.all()       # validated via from_attributes
```

For Django REST Framework projects, Pydantic is commonly used for validating external API payloads, JSONField contents, and settings, even when DRF serializers remain the API layer.

## 6. Other databases and ODMs

| Library | Store | How Pydantic is used |
|---|---|---|
| **Beanie** | MongoDB (async) | Documents are Pydantic models; queries return validated models |
| **ODMantic** | MongoDB | Pydantic-based ODM with typed queries |
| **Redis OM Python** | Redis | Pydantic `HashModel` / `JsonModel` |
| **asyncpg / psycopg** | PostgreSQL | Validate rows with `Model.model_validate(dict(row))` or `TypeAdapter(list[Model])` |
| **Piccolo**, **Tortoise ORM** | SQL | Generate Pydantic models from tables (`create_pydantic_model`, `pydantic_model_creator`) |
| **Polars / pandas** | dataframes | Validate rows via `TypeAdapter(list[RowModel]).validate_python(df.to_dicts())`; for column-level validation see `pandera` (which has Pydantic integration) |

### Raw SQL rows

```python
import sqlite3
from pydantic import BaseModel, TypeAdapter


class Row(BaseModel):
    id: int
    email: str
    active: bool


conn = sqlite3.connect(":memory:")
conn.row_factory = sqlite3.Row
conn.execute("create table users (id int, email text, active int)")
conn.execute("insert into users values (1, 'a@x.org', 1)")
rows = TypeAdapter(list[Row]).validate_python([dict(r) for r in conn.execute("select * from users")])
print(rows)
#> [Row(id=1, email='a@x.org', active=True)]
```

## 7. HTTP clients: validating third-party APIs

Never trust external APIs blindly. Validate responses at the boundary:

```python
import httpx
from pydantic import BaseModel, ConfigDict


class GithubRepo(BaseModel):
    model_config = ConfigDict(extra="ignore")     # tolerate new fields the API adds
    full_name: str
    stargazers_count: int
    private: bool


def fake_transport(request: httpx.Request) -> httpx.Response:   # stand-in for the real API
    return httpx.Response(200, json={"full_name": "pydantic/pydantic", "stargazers_count": 25000, "private": False, "x": 1})


with httpx.Client(transport=httpx.MockTransport(fake_transport)) as client:
    resp = client.get("https://api.github.com/repos/pydantic/pydantic")
    repo = GithubRepo.model_validate_json(resp.content)       # parse bytes directly
    print(repo)
    #> full_name='pydantic/pydantic' stargazers_count=25000 private=False
```

## 8. Message queues and task runners

The pattern is identical everywhere — **serialize with `model_dump_json()`, validate with `model_validate_json()`**:

```py
# Producer (Kafka / RabbitMQ / SQS / Redis Streams …)
producer.send("orders", OrderPlaced(order_id=42, total=99.5).model_dump_json().encode())

# Consumer
evt = AnyEvent.validate_json(message.value)   # discriminated-union TypeAdapter (chapter 07)
```

- **Celery:** pass `model.model_dump(mode="json")` as task arguments and re-validate inside the task (Celery ≥ 5.5 can also validate task arguments annotated with Pydantic models when the task is declared with `pydantic=True`).
- **FastStream** (Kafka/RabbitMQ/NATS/Redis) and **Prefect** use Pydantic natively for message/parameter validation.
- **AWS Lambda:** validate the event dict at the top of the handler; consider `defer_build=True` to reduce cold-start time (and AWS Lambda Powertools' parser utilities, which are Pydantic-based).

---

## Summary

- FastAPI: request/response models, `Annotated` params, `Query()` models, return-type response models; Pydantic v2 only.
- SQLAlchemy: keep ORM and schemas separate; bridge with `from_attributes=True`; beware lazy loading.
- SQLModel: one class for table + schema; table models skip `__init__` validation — validate with a separate schema.
- Litestar, Django Ninja, Beanie, Redis OM and many more are Pydantic-native.
- Validate third-party API responses and queue messages with `model_validate_json`.

**Next:** [15 — Integrations: AI and Tooling](15-integrations-ai-and-tooling.md)
