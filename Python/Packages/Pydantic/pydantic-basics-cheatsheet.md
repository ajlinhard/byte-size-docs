# Pydantic Cheatsheet - From Basics to Advanced

### Docs and Tutorials:
- [Pydantic Home Page](https://docs.pydantic.dev/latest/)
- [Intro Walkthrough](https://www.youtube.com/watch?v=7aBRk_JP-qY)

## Use Cases
Pydantic is widely used outside of API contexts! While it's famously associated with FastAPI, it's actually a general-purpose data validation library with many other applications:

**Common non-API use cases:**

1. **Configuration Management** - Validating and parsing config files (YAML, JSON, TOML) with type checking and environment variables
   
2. **Data Engineering Pipelines** - Validating data schemas in ETL/ELT processes, ensuring data quality between pipeline stages

3. **CLI Applications** - Validating command-line arguments and options

4. **Settings/Environment Variables** - Type-safe application settings with `pydantic-settings`

5. **Data Parsing** - Converting and validating data from various sources (files, databases, message queues) into Python objects

6. **Machine Learning** - Validating model configs, training parameters, and input/output data schemas

7. **Business Logic** - Ensuring domain objects meet business rules and constraints

8. **Testing** - Creating validated test fixtures and mock data

**Why people use it outside APIs:**
- Runtime validation with clear error messages
- Type hints that actually enforce types
- Automatic data coercion and parsing
- Easy serialization/deserialization
- Better than dataclasses when you need validation
- Reduces boilerplate validation code

So yes, it's a general-purpose validation tool that happens to be particularly popular in the API world!

## Installation
```bash
pip install pydantic
```

## 1. Basic Models

### Simple Model Definition
```python
from pydantic import BaseModel

class User(BaseModel):
    name: str
    age: int
    email: str

# Usage
user = User(name="Alice", age=30, email="alice@example.com")
print(user.name)  # Alice
print(user.model_dump())  # {'name': 'Alice', 'age': 30, 'email': 'alice@example.com'}
```

### Optional Fields and Defaults
```python
from typing import Optional
from pydantic import BaseModel, Field

class User(BaseModel):
    name: str
    age: int = 18  # Default value
    email: Optional[str] = None  # Optional field
    is_active: bool = Field(default=True, description="User active status")

user = User(name="Bob")
print(user.age)  # 18
print(user.is_active)  # True
```

## 2. Data Validation

### Built-in Validators
```python
from pydantic import BaseModel, EmailStr, HttpUrl, validator
from typing import List

class User(BaseModel):
    name: str
    email: EmailStr  # Validates email format
    website: HttpUrl  # Validates URL format
    tags: List[str] = []

    @validator('name')
    def name_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Name cannot be empty')
        return v.title()  # Capitalize name

# Usage
user = User(
    name="john doe",
    email="john@example.com",
    website="https://johndoe.com"
)
print(user.name)  # John Doe
```

### Custom Validators
```python
from pydantic import BaseModel, validator, root_validator

class Password(BaseModel):
    password: str
    confirm_password: str

    @validator('password')
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain uppercase letter')
        return v

    @root_validator
    def passwords_match(cls, values):
        password = values.get('password')
        confirm_password = values.get('confirm_password')
        if password != confirm_password:
            raise ValueError('Passwords do not match')
        return values
```

## 3. Field Configuration

### Advanced Field Options
```python
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class Product(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="Product name")
    price: float = Field(..., gt=0, description="Price must be positive")
    quantity: int = Field(default=0, ge=0, le=1000, description="Stock quantity")
    created_at: datetime = Field(default_factory=datetime.now)
    tags: Optional[str] = Field(None, regex=r'^[a-zA-Z0-9,\s]+$')

# Field constraints:
# ... = required field
# gt/gte = greater than / greater than or equal
# lt/lte = less than / less than or equal
# min_length/max_length = string length constraints
# regex = regular expression validation
```

### Common additions to Pydantic classes:
While Pydantic classes are primarily used for data validation and parsing, they're still regular Python classes, so people commonly add various types of methods to them:

**3a. Business Logic Methods**
```python
from pydantic import BaseModel

class User(BaseModel):
    first_name: str
    last_name: str
    age: int
    
    def get_full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
    
    def is_adult(self) -> bool:
        return self.age >= 18
```

**3b. Computed Properties**
```python
class Product(BaseModel):
    name: str
    price: float
    tax_rate: float = 0.08
    
    @property
    def total_price(self) -> float:
        return self.price * (1 + self.tax_rate)
```

**3c. Serialization/Transformation Methods**
```python
class Record(BaseModel):
    id: int
    created_at: datetime
    
    def to_dict_for_api(self) -> dict:
        return {
            "id": str(self.id),
            "timestamp": self.created_at.isoformat()
        }
```

**3d. Factory/Constructor Methods**
```python
class Config(BaseModel):
    host: str
    port: int
    
    @classmethod
    def from_env(cls) -> "Config":
        return cls(
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT"))
        )
```

**3e. Comparison/Query Methods**
```python
class Transaction(BaseModel):
    amount: float
    status: str
    
    def is_complete(self) -> bool:
        return self.status == "completed"
    
    def is_large_transaction(self, threshold: float = 1000) -> bool:
        return self.amount > threshold
```

This approach keeps your data validation tight while still allowing you to build rich domain models!

## 4. Custom Data Types

### Using Enums
```python
from enum import Enum
from pydantic import BaseModel

class Status(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"

class User(BaseModel):
    name: str
    status: Status = Status.ACTIVE

user = User(name="Alice", status="pending")  # Auto-converts string to enum
print(user.status)  # Status.PENDING
```

### Custom Type with Validation
```python
from pydantic import BaseModel, validator
from typing import Any

class PhoneNumber(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v: Any) -> str:
        if not isinstance(v, str):
            raise TypeError('String required')
        
        # Remove non-digit characters
        digits = ''.join(filter(str.isdigit, v))
        
        if len(digits) != 10:
            raise ValueError('Phone number must have 10 digits')
        
        # Format as (XXX) XXX-XXXX
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"

class Contact(BaseModel):
    name: str
    phone: PhoneNumber

contact = Contact(name="John", phone="1234567890")
print(contact.phone)  # (123) 456-7890
```

### UUID and Date Types
```python
from pydantic import BaseModel
from uuid import UUID, uuid4
from datetime import date, datetime
from typing import Optional

class Record(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    created_date: date
    updated_at: Optional[datetime] = None
    
    class Config:
        # Allow UUID to be passed as string
        json_encoders = {
            UUID: str,
            datetime: lambda v: v.isoformat()
        }

record = Record(created_date="2023-12-01")  # String automatically converted
print(record.id)  # UUID object
```

## 5. Nested Models

### Basic Nesting
```python
from pydantic import BaseModel
from typing import List, Optional

class Address(BaseModel):
    street: str
    city: str
    country: str = "USA"
    zip_code: Optional[str] = None

class User(BaseModel):
    name: str
    age: int
    address: Address  # Nested model
    
user_data = {
    "name": "Alice",
    "age": 30,
    "address": {
        "street": "123 Main St",
        "city": "New York",
        "zip_code": "10001"
    }
}

user = User(**user_data)
print(user.address.city)  # New York
```

### Complex Nesting with Lists
```python
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class Tag(BaseModel):
    name: str
    color: str = "blue"

class Comment(BaseModel):
    author: str
    content: str
    created_at: datetime = Field(default_factory=datetime.now)

class Post(BaseModel):
    title: str
    content: str
    author: str
    tags: List[Tag] = []
    comments: List[Comment] = []
    
    def add_comment(self, author: str, content: str):
        comment = Comment(author=author, content=content)
        self.comments.append(comment)

# Usage
post = Post(
    title="My Blog Post",
    content="This is my first post",
    author="Alice",
    tags=[
        {"name": "python", "color": "green"},
        {"name": "tutorial"}
    ]
)

post.add_comment("Bob", "Great post!")
print(len(post.comments))  # 1
```

### Self-Referencing Models
```python
from pydantic import BaseModel
from typing import List, Optional
from __future__ import annotations  # For forward references

class Category(BaseModel):
    name: str
    parent: Optional[Category] = None
    children: List[Category] = []
    
    def add_child(self, child: Category):
        child.parent = self
        self.children.append(child)

# Update forward references
Category.model_rebuild()

# Usage
electronics = Category(name="Electronics")
phones = Category(name="Phones")
smartphones = Category(name="Smartphones")

electronics.add_child(phones)
phones.add_child(smartphones)

print(smartphones.parent.parent.name)  # Electronics
```

## 6. Model Configuration

### Config Class Options
```python
from pydantic import BaseModel, Field

class User(BaseModel):
    first_name: str = Field(alias="firstName")
    last_name: str = Field(alias="lastName")
    age: int
    
    class Config:
        # Allow field population by alias
        allow_population_by_field_name = True
        
        # Case-insensitive field matching
        case_sensitive = False
        
        # Validate assignment after model creation
        validate_assignment = True
        
        # Use enum values instead of names
        use_enum_values = True
        
        # JSON schema customization
        schema_extra = {
            "example": {
                "firstName": "John",
                "lastName": "Doe",
                "age": 30
            }
        }

# Can use either field name or alias
user1 = User(first_name="John", last_name="Doe", age=30)
user2 = User(firstName="Jane", lastName="Smith", age=25)
```

## 7. Serialization and Deserialization

### JSON Operations
```python
from pydantic import BaseModel
from typing import Dict, Any
import json

class User(BaseModel):
    name: str
    age: int
    metadata: Dict[str, Any] = {}

# From JSON string
json_data = '{"name": "Alice", "age": 30, "metadata": {"role": "admin"}}'
user = User.model_validate_json(json_data)

# To JSON string
json_output = user.model_dump_json(indent=2)
print(json_output)

# To dictionary
dict_output = user.model_dump()
print(dict_output)

# Exclude/include specific fields
limited_output = user.model_dump(exclude={"metadata"})
only_name = user.model_dump(include={"name"})
```

### Custom Serializers
```python
from pydantic import BaseModel, Field, field_serializer
from datetime import datetime
from typing import Optional

class Event(BaseModel):
    name: str
    start_time: datetime
    duration_minutes: int
    
    @field_serializer('start_time')
    def serialize_start_time(self, value: datetime) -> str:
        return value.strftime("%Y-%m-%d %H:%M")
    
    @property
    def end_time(self) -> datetime:
        from datetime import timedelta
        return self.start_time + timedelta(minutes=self.duration_minutes)

event = Event(
    name="Meeting",
    start_time=datetime(2023, 12, 1, 14, 30),
    duration_minutes=60
)

print(event.model_dump_json())
# Outputs formatted datetime string
```

## 8. Advanced Patterns

### Generic Models
```python
from pydantic import BaseModel
from typing import Generic, TypeVar, List

T = TypeVar('T')

class Response(BaseModel, Generic[T]):
    success: bool
    data: T
    message: str = ""

class User(BaseModel):
    name: str
    email: str

class UserListResponse(Response[List[User]]):
    pass

class UserResponse(Response[User]):
    pass

# Usage
users = [User(name="Alice", email="alice@example.com")]
response = UserListResponse(
    success=True,
    data=users,
    message="Users retrieved successfully"
)
```

### Dynamic Model Creation
```python
from pydantic import BaseModel, create_model
from typing import Dict, Any

def create_dynamic_model(fields: Dict[str, Any]) -> BaseModel:
    return create_model('DynamicModel', **fields)

# Create model dynamically
fields = {
    'name': (str, ...),  # (type, default) - ... means required
    'age': (int, 18),    # default value of 18
    'email': (str, None) # optional field
}

DynamicUser = create_dynamic_model(fields)
user = DynamicUser(name="Bob", email="bob@example.com")
print(user.age)  # 18 (default value)
```

### Model Inheritance
```python
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class BaseEntity(BaseModel):
    id: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    
    def touch(self):
        self.updated_at = datetime.now()

class User(BaseEntity):
    name: str
    email: str
    
class Product(BaseEntity):
    name: str
    price: float
    category: str

user = User(name="Alice", email="alice@example.com")
user.touch()  # Updates updated_at timestamp
print(user.updated_at)
```

## 9. Error Handling

### Validation Errors
```python
from pydantic import BaseModel, ValidationError
from typing import List

class User(BaseModel):
    name: str
    age: int
    emails: List[str]

try:
    user = User(
        name="",  # Invalid: empty name
        age="not_a_number",  # Invalid: not an integer
        emails="not_a_list"  # Invalid: not a list
    )
except ValidationError as e:
    print(e.json(indent=2))
    # Detailed error information for each field
    
    for error in e.errors():
        print(f"Field: {error['loc']}")
        print(f"Message: {error['msg']}")
        print(f"Type: {error['type']}")
```

## 10. Real-World Example

### Complete API Model Structure
```python
from pydantic import BaseModel, Field, EmailStr, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
import uuid

class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"
    MODERATOR = "moderator"

class Address(BaseModel):
    street: str
    city: str
    state: str = Field(..., min_length=2, max_length=2)
    zip_code: str = Field(..., regex=r'^\d{5}(-\d{4})?$')
    country: str = "USA"

class UserProfile(BaseModel):
    bio: Optional[str] = Field(None, max_length=500)
    website: Optional[str] = None
    social_links: Dict[str, str] = {}

class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str = Field(..., min_length=3, max_length=20, regex=r'^[a-zA-Z0-9_]+$')
    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=100)
    role: UserRole = UserRole.USER
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)
    last_login: Optional[datetime] = None
    address: Optional[Address] = None
    profile: UserProfile = Field(default_factory=UserProfile)
    tags: List[str] = []
    
    @validator('username')
    def username_lowercase(cls, v):
        return v.lower()
    
    @validator('tags')
    def limit_tags(cls, v):
        if len(v) > 10:
            raise ValueError('Maximum 10 tags allowed')
        return v
    
    class Config:
        validate_assignment = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        schema_extra = {
            "example": {
                "username": "johndoe",
                "email": "john@example.com",
                "full_name": "John Doe",
                "address": {
                    "street": "123 Main St",
                    "city": "New York",
                    "state": "NY",
                    "zip_code": "10001"
                }
            }
        }

# API Response Models
class UserResponse(BaseModel):
    success: bool
    data: User
    message: str = "User retrieved successfully"

class UserListResponse(BaseModel):
    success: bool
    data: List[User]
    total: int
    page: int = 1
    per_page: int = 10

# Usage Example
user_data = {
    "username": "JohnDoe123",
    "email": "john@example.com",
    "full_name": "John Doe",
    "address": {
        "street": "123 Main St",
        "city": "New York",
        "state": "NY",
        "zip_code": "10001"
    },
    "tags": ["python", "developer"]
}

user = User(**user_data)
print(f"Created user: {user.username} ({user.email})")
print(f"User ID: {user.id}")

# Serialize for API response
response = UserResponse(success=True, data=user)
print(response.model_dump_json(indent=2))
```

## Common Patterns & Tips

1. **Use Field() for complex validation and metadata**
2. **Leverage Config class for model-wide settings**
3. **Create base models for common fields (id, timestamps)**
4. **Use Enums for controlled vocabularies**
5. **Implement custom validators for business logic**
6. **Use aliases for API field name mapping**
7. **Handle optional fields properly with Union and Optional**
8. **Use model_validate() and model_dump() for serialization**
9. **Implement proper error handling with ValidationError**
10. **Consider performance with large nested models**
