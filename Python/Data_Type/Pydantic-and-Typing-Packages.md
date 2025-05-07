# Typing and Pydantic in Python
Because of the dynamicness of python there can some annoyance when onboarding to code or catching bad values being passed to around. The dynamicness can be a strength as well, so use Pydantic/Typing to reign in data types for less dynamic cases.

## Python Typing

Python typing is a feature that allows you to add type hints to your Python code, indicating what types of values variables, function parameters, and return values should be.

### Purpose and Use Cases

```python
def add_numbers(a: int, b: int) -> int:
    return a + b

def process_user(name: str, age: int, is_active: bool = True) -> dict:
    return {"name": name, "age": age, "active": is_active}
```

Type hints serve several purposes:
- Documentation: They make code more readable by explicitly stating what types are expected
- IDE support: Better autocompletion and error detection in your editor
- Static type checking: Tools like mypy can check for type errors without running the code
- Enhanced refactoring: Makes it safer to modify code

### Pros of Python Typing

- Improves code readability and self-documentation
- Catches type-related bugs before runtime
- Better IDE support with intelligent code completion
- Easier maintenance of large codebases
- Helps onboarding new developers to a project

### Cons of Python Typing

- Adds verbosity to Python code
- Learning curve for developers new to type systems
- Type annotations are ignored at runtime (they're hints, not enforcement)
- Can be cumbersome for highly dynamic code
- May require additional tools (like mypy) to be truly effective

## Pydantic

Pydantic is a data validation library that uses Python type annotations to validate data and enforce type correctness at runtime.

### Basic Example

```python
from pydantic import BaseModel, EmailStr, ValidationError

class User(BaseModel):
    id: int
    name: str
    email: EmailStr
    age: int
    is_active: bool = True

# Valid user
try:
    user = User(id=1, name="John", email="john@example.com", age=30)
    print(user.model_dump())
except ValidationError as e:
    print(e)

# Invalid user - will raise ValidationError
try:
    invalid_user = User(id="not_an_int", name=123, email="not_an_email", age="thirty")
    print(invalid_user)
except ValidationError as e:
    print(e)
```

### Purpose and Use Cases

1. **API Data Validation**: Ensuring incoming API requests have the correct format and types
   ```python
   @app.post("/users/")
   async def create_user(user: User):  # Pydantic model validates automatically
       db.create_user(user)
       return {"status": "success"}
   ```

2. **Configuration Management**: Managing application settings with validation
   ```python
   class Settings(BaseModel):
       app_name: str
       database_url: str
       debug: bool = False
       max_connections: int = 100
   
   settings = Settings.model_validate(config_dict)  # Validates and loads config
   ```

3. **Data Parsing and Cleaning**: Converting and validating data from external sources
   ```python
   class SensorData(BaseModel):
       device_id: str
       temperature: float
       humidity: float
       timestamp: datetime
   
   # Will convert strings to appropriate types and validate
   clean_data = SensorData.model_validate_json(raw_json_data)
   ```

4. **ORM Integration**: Working with databases using Pydantic models
   ```python
   class UserInDB(User):
       hashed_password: str
       
   def get_user(db, user_id: int) -> UserInDB:
       db_user = db.query(...)
       return UserInDB.model_validate(db_user)
   ```

### Pros of Pydantic

- Runtime data validation that enforces type correctness
- Automatic conversion between types when possible (e.g., strings to ints)
- Rich set of validation rules beyond simple types
- Clean error messages when validation fails
- JSON Schema generation and validation
- Seamless integration with FastAPI and other frameworks
- Good performance through Rust-based implementation (in v2)

### Cons of Pydantic

- Adds runtime overhead for validation
- Can be overly strict for some use cases
- Learning curve to understand all features and behaviors
- Version 2 introduced breaking changes from version 1
- More complex than simple dataclasses for basic use cases
- Some edge cases can be tricky to handle

## Combining Typing and Pydantic

Pydantic builds on Python's typing system, so they work well together:

```python
from typing import List, Dict, Optional
from pydantic import BaseModel, Field

class Address(BaseModel):
    street: str
    city: str
    zipcode: str
    
class User(BaseModel):
    id: int
    name: str
    addresses: List[Address] = []
    metadata: Dict[str, str] = Field(default_factory=dict)
    profile_image: Optional[str] = None
```

This approach gives you the best of both worlds:
- Static type checking with tools like mypy
- Runtime validation with Pydantic
- Clear documentation of your data structures
- IDE support for autocompletion

## Advanced Features of Pydantic

```python
from pydantic import BaseModel, Field, validator, root_validator
from typing import List
import re

class Product(BaseModel):
    id: str = Field(..., description="Product ID")
    name: str = Field(..., min_length=3, max_length=50)
    price: float = Field(..., gt=0)
    tags: List[str] = []

    # Field-level validation
    @validator('id')
    def validate_id(cls, v):
        if not re.match(r'^PRD-\d{6}$', v):
            raise ValueError('ID must be in format PRD-XXXXXX')
        return v
    
    # Model-level validation
    @root_validator
    def check_premium_pricing(cls, values):
        if 'premium' in values.get('tags', []) and values.get('price', 0) < 100:
            raise ValueError('Premium products must cost at least $100')
        return values
```
