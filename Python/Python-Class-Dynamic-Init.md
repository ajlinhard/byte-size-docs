# Python Class Dynamic `__init__`
In python is there a good way in a class which is going to be inherited to allow for any amount of parameters that will be turned into class variable of the same name as the arguement?

Yes! The cleanest way is using `**kwargs` in `__init__` and iterating over them with `setattr`:

```python
class Base:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class Child(Base):
    def __init__(self, extra, **kwargs):
        super().__init__(**kwargs)
        self.extra = extra


c = Child(extra="hello", name="Alice", age=30, active=True)
print(c.name)    # Alice
print(c.age)     # 30
print(c.active)  # True
print(c.extra)   # hello
```

A few variations worth knowing:

**With default values** — pass a defaults dict so subclasses can declare expected attributes:
```python
class Base:
    defaults = {}

    def __init__(self, **kwargs):
        for key, value in {**self.defaults, **kwargs}.items():
            setattr(self, key, value)


class Child(Base):
    defaults = {"color": "red", "size": 10}


c = Child(size=99)
print(c.color)  # red  (from defaults)
print(c.size)   # 99   (overridden)
```

**With validation** — reject unexpected keys to catch typos early:
```python
class Base:
    allowed = None  # None means allow all

    def __init__(self, **kwargs):
        if self.allowed is not None:
            unexpected = set(kwargs) - set(self.allowed)
            if unexpected:
                raise TypeError(f"Unexpected arguments: {unexpected}")
        for key, value in kwargs.items():
            setattr(self, key, value)
```

**Using `__init_subclass__`** — for a more declarative style, define expected fields on the class itself:
```python
class Base:
    fields: tuple = ()

    def __init__(self, **kwargs):
        for field in self.fields:
            setattr(self, field, kwargs.get(field))
        for key, value in kwargs.items():
            setattr(self, key, value)


class Child(Base):
    fields = ("name", "age")  # documents the expected ones


c = Child(name="Alice", age=30, bonus="extra")
```

**The quick rule of thumb:**
- Use `setattr(self, key, value)` in a `**kwargs` loop — it's the most flexible and readable pattern.
- Prefer `**kwargs` + `super().__init__(**kwargs)` in every layer of the hierarchy so parameters flow cleanly up the chain.

---
## When is Dynamic Init a good practice?

---
It's a **legitimate but situational** pattern — not bad practice inherently, but it has real tradeoffs.

## When it's a good fit

- **Configuration/settings objects** — where fields vary by deployment or user input
- **ORM / data mapping layers** — like SQLAlchemy's model base, where columns become attributes dynamically
- **Plugin or framework base classes** — where the framework can't know what subclasses will need
- **Rapid prototyping** — when the shape of your data is still evolving

These are cases where the *flexibility is the point*, not a shortcut.

---

## The tradeoffs vs. explicit attributes

| | Dynamic (`**kwargs` + `setattr`) | Explicit attributes |
|---|---|---|
| **Readability** | Hard to know what attributes exist without reading all subclasses | Self-documenting at a glance |
| **IDE support** | No autocomplete, no "go to definition" | Full autocomplete & navigation |
| **Static analysis** | `mypy`/`pyright` can't type-check them | Fully type-checkable |
| **Error catching** | Typos in kwarg names silently create wrong attributes | Typos are caught at definition time |
| **Onboarding** | New devs have to trace the code to understand the shape | New devs read the class and know immediately |
| **Flexibility** | High — trivial to add new fields | Low — every new field needs a line |

---

## The practical argument for explicit attributes

```python
# A new dev reads this and knows everything instantly
class Connection:
    def __init__(self, host: str, port: int, timeout: float = 30.0):
        self.host = host
        self.port = port
        self.timeout = timeout
```

vs.

```python
# A new dev has to hunt down every call site to know what's possible
class Connection(Base):
    pass  # attributes set dynamically from kwargs... somewhere
```

The explicit version also gives you free type hints, default values in one place, and a clear contract for subclasses.

---

## The verdict

Use dynamic `**kwargs`/`setattr` when **the set of attributes genuinely can't be known ahead of time** (e.g. user-defined config, database columns, plugin systems). 

If you *do* know the attributes — even roughly — **explicit is almost always better**. The small cost of typing a few extra lines pays for itself immediately in clarity, tooling support, and catching bugs early. Python's own philosophy agrees: *"Explicit is better than implicit"* (PEP 20).

A common middle ground is using Python `dataclasses`, which gives you explicit, typed, documented fields with minimal boilerplate:

```python
from dataclasses import dataclass, field

@dataclass
class Base:
    name: str
    active: bool = True

@dataclass
class Child(Base):
    role: str = "user"
```

You get explicitness, type hints, auto-generated `__init__`, and clean inheritance — best of all worlds for most cases.
