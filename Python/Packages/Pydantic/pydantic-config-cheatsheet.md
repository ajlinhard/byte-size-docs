# Pydantic Config Cheatsheet
The configuration of setting for the BaseModel in pydantic can be set 1 of 2 way:

## Choose one approach

**Option 1: Use Pydantic v2 syntax (recommended)**
```python
from pydantic import BaseModel, Field, ConfigDict

class TaskAI(Task):
    # Rename your field to avoid conflict
    ai_config: AIModelConfig = Field(
        default_factory=AIModelConfig,
        description="Configuration for the AI model"
    )
    
    # Use v2 configuration syntax
    model_config = ConfigDict(arbitrary_types_allowed=True)
```

**Option 2: Keep v1 syntax (rename your field)**
```python
class TaskAI(Task):
    # Rename to avoid the reserved name
    ai_model_config: AIModelConfig = Field(
        default_factory=AIModelConfig,
        description="Configuration for the AI model"
    )
    
    class Config:
        arbitrary_types_allowed = True
```

### Error If Trying Both
The following error can occur if using both methods of config across your pydantic models:
```
PydanticUserError: "Config" and "model_config" cannot be used together
```
This error indicates you're actually using **Pydantic v2**, not v1! In Pydantic v2, you cannot use both the old `class Config` syntax and the new `model_config` attribute together.

Here's what's happening and how to fix it:

## The Problem
```python
class TaskAI(Task):
    # This field name conflicts with Pydantic v2's reserved attribute
    model_config: AIModelConfig = Field(...)  # ❌ Conflicts!
    
    class Config:  # ❌ Old v1 syntax
        arbitrary_types_allowed = True
```

** Why this happens **
In Pydantic v2, `model_config` became a reserved attribute name for model configuration, so using it as a field name creates a naming conflict with the internal Pydantic machinery.

The quickest fix is to rename your field from `model_config` to something like `ai_config`, `llm_config`, or `ai_model_config`.

---
## Pydantic Config Settings Cheatsheet
Below in the table is a comprehensive cheatsheet for Pydantic v2 `model_config` settings. The table includes all the major configuration parameters with their definitions and default values.

Some key things to note:

- **Most commonly used**: `arbitrary_types_allowed`, `extra`, `validate_assignment`, `frozen`, `str_strip_whitespace`
- **For APIs**: `populate_by_name`, `from_attributes`, `use_enum_values` are very useful
- **For strict validation**: Use `extra='forbid'`, `validate_assignment=True`, `frozen=True`
- **For flexibility**: Use `extra='allow'`, `arbitrary_types_allowed=True`

The example combinations at the bottom show typical patterns for different use cases. Let me know if you need clarification on any specific parameter!

### Setting Parameters 
| Parameter Name | Definition | Default Value |
|---|---|---|
| **arbitrary_types_allowed** | Allow fields with arbitrary types (non-standard Python types) | `False` |
| **str_max_length** | Maximum length for string fields | `None` |
| **str_min_length** | Minimum length for string fields | `0` |
| **str_strip_whitespace** | Strip leading/trailing whitespace from strings | `False` |
| **json_schema_extra** | Extra information to add to JSON schema | `None` |
| **json_encoders** | Custom JSON encoders for specific types | `{}` |
| **validate_assignment** | Validate field values when they are assigned after model creation | `False` |
| **use_enum_values** | Use enum values instead of enum objects in validation | `False` |
| **validate_default** | Validate default values during model creation | `False` |
| **extra** | How to handle extra fields (`'ignore'`, `'allow'`, `'forbid'`) | `'ignore'` |
| **frozen** | Make model immutable (no field updates allowed) | `False` |
| **populate_by_name** | Allow population by field name in addition to alias | `False` |
| **use_attribute_docstrings** | Use attribute docstrings for field descriptions | `False` |
| **ignored_types** | Types to ignore during model creation | `()` |
| **allow_inf_nan** | Allow `inf`, `-inf`, `nan` values for float fields | `True` |
| **json_schema_mode** | JSON schema generation mode (`'validation'` or `'serialization'`) | `'validation'` |
| **json_schema_serialization_defaults_required** | Include fields with defaults as required in JSON schema | `False` |
| **hide_input_in_errors** | Hide input data in validation error messages | `False` |
| **defer_build** | Defer model building until first use | `False` |
| **experimental_defer_build_mode** | Experimental defer build mode | `None` |
| **plugin_settings** | Settings for Pydantic plugins | `None` |
| **tagged_union_resolver** | Custom resolver for tagged unions | `None` |
| **json_schema_mode_override** | Override JSON schema mode for specific cases | `None` |
| **coerce_numbers_to_str** | Coerce numbers to strings when field expects string | `False` |
| **ser_json_timedelta** | How to serialize timedelta in JSON (`'iso8601'`, `'float'`) | `'iso8601'` |
| **ser_json_bytes** | How to serialize bytes in JSON (`'utf8'`, `'base64'`) | `'utf8'` |
| **ser_json_inf_nan** | How to handle inf/nan in JSON serialization (`'null'`, `'constants'`) | `'null'` |
| **title** | Title for the model schema | Model class name |
| **str_to_lower** | Convert string inputs to lowercase | `False` |
| **str_to_upper** | Convert string inputs to uppercase | `False` |
| **from_attributes** | Allow model creation from object attributes (not just dicts) | `False` |
| **loc_by_alias** | Use field aliases in error locations | `True` |
| **alias_generator** | Function to generate field aliases | `None` |
| **ignored_types** | Tuple of types to ignore during field discovery | `()` |
| **allow_reuse** | Allow reuse of validators | `True` |
| **fields** | Override field definitions | `None` |

## Usage Example

```python
from pydantic import BaseModel, ConfigDict

class MyModel(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        str_strip_whitespace=True,
        validate_assignment=True,
        frozen=True,
        extra='forbid'
    )
    
    name: str
    age: int
```

## Common Combinations

**Strict Mode:**
```python
model_config = ConfigDict(
    extra='forbid',
    validate_assignment=True,
    frozen=True
)
```

**Flexible Mode:**
```python
model_config = ConfigDict(
    extra='allow',
    arbitrary_types_allowed=True,
    str_strip_whitespace=True
)
```

**API Response Model:**
```python
model_config = ConfigDict(
    populate_by_name=True,
    use_enum_values=True,
    from_attributes=True
)
```
