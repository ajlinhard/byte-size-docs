# Major Differences Between Pydantic v1 and v2

## Key Changes

**1. Performance**
- v2 is 5-50x faster (rewritten in Rust core)

**2. Validation**
- v2 has stricter validation by default
- Better type checking and error messages

**3. Configuration Syntax** ⚠️
This is what affects your code:

### Pydantic v1:
```python
class MyModel(BaseModel):
    name: str
    
    class Config:
        orm_mode = True
        anystr_strip_whitespace = True
```

### Pydantic v2:
```python
from pydantic import ConfigDict

class MyModel(BaseModel):
    name: str
    
    model_config = ConfigDict(
        from_attributes=True,  # replaces orm_mode
        str_strip_whitespace=True  # replaces anystr_strip_whitespace
    )
```

## Your Specific Line

```python
model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)
```

**This is Pydantic v2 syntax.** In v1, it would be:

```python
class Config:
    orm_mode = True
    anystr_strip_whitespace = True
```

## Notable Config Renames

| Pydantic v1 | Pydantic v2 |
|-------------|-------------|
| `orm_mode` | `from_attributes` |
| `anystr_strip_whitespace` | `str_strip_whitespace` |
| `allow_population_by_field_name` | `populate_by_name` |
| `use_enum_values` | `use_enum_values` (same) |

## Other Important Changes

- `validator` → `field_validator`
- `root_validator` → `model_validator`
- `.dict()` → `.model_dump()`
- `.json()` → `.model_dump_json()`
- `.parse_obj()` → `.model_validate()`
