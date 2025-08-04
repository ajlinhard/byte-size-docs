# Pydantic Config Cheatsheet
The configuration of setting for the BaseModel in pydantic can be set 1 of 2 way:

## Solution: Choose one approach

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
