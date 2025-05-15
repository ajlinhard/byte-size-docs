# Python Enum Cheatsheet

## Basic Enum Definition

```python
from enum import Enum

class Color(Enum):
    RED = 1
    GREEN = 2
    BLUE = 3
```

## Accessing Enum Members

```python
# Access by name
red = Color.RED                  # Color.RED
red_alternative = Color['RED']   # Color.RED

# Access by value
color_by_value = Color(1)        # Color.RED

# Access name and value properties
print(Color.RED.name)            # 'RED'
print(Color.RED.value)           # 1
```

## Checking Enum Membership and Equality

```python
# Enum identity and equality
Color.RED is Color.RED           # True
Color.RED == Color.RED           # True
Color.RED is Color(1)            # True
Color.RED == Color(1)            # True
Color.RED is not Color.BLUE      # True
Color.RED != Color.BLUE          # True

# Check if value exists
try:
    Color(4)                     # Will raise ValueError
except ValueError:
    print("Not a valid color")
```

## Iterating Through Enums

```python
# Iterate through members
for color in Color:
    print(color)                 # Color.RED, Color.GREEN, Color.BLUE

# Get list of all enum members
all_colors = list(Color)         # [<Color.RED: 1>, <Color.GREEN: 2>, <Color.BLUE: 3>]

# Get all names
color_names = [color.name for color in Color]  # ['RED', 'GREEN', 'BLUE']

# Get all values
color_values = [color.value for color in Color] # [1, 2, 3]

# Access members dictionary
members_dict = Color.__members__  # OrderedDict([('RED', <Color.RED: 1>), ...])
```

## Auto Value Assignment

```python
from enum import Enum, auto

class Shape(Enum):
    CIRCLE = auto()      # 1
    SQUARE = auto()      # 2
    TRIANGLE = auto()    # 3
```

## Enum with String Values

```python
class Status(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    
# Can be used directly as strings
print(f"Status: {Status.PENDING}")  # "Status: pending"
```

## Enum with Integer Values

```python
class Priority(int, Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    
# Can be used in comparisons
if Priority.HIGH > Priority.LOW:
    print("High priority is greater than low")  # Will print
```

## Unique and Non-Unique Values

```python
# By default, values must be unique
class Planet(Enum):
    MERCURY = 1
    VENUS = 2
    EARTH = 3
    # DUPLICATE = 1  # Would raise an error

# Allow duplicate values with @_generate_next_value_
from enum import _generate_next_value_

class ConfusedPlanet(Enum):
    def _generate_next_value_(name, start, count, last_values):
        return name
    
    MERCURY = auto()  # 'MERCURY'
    VENUS = auto()    # 'VENUS' 
    EARTH = auto()    # 'EARTH'
```

## Flag Enums for Bitwise Operations

```python
from enum import Flag, auto

class Permissions(Flag):
    NONE = 0
    READ = auto()       # 1
    WRITE = auto()      # 2
    EXECUTE = auto()    # 4
    
    # Common combinations
    READ_WRITE = READ | WRITE                    # 3
    ALL = READ | WRITE | EXECUTE                 # 7
    
# Combine flags
user_perms = Permissions.READ | Permissions.WRITE  # Permissions.READ_WRITE (3)

# Check flags
if Permissions.READ in user_perms:
    print("Has read permission")                   # Will print
    
if user_perms & Permissions.WRITE:
    print("Has write permission")                  # Will print
    
# Remove a permission
user_perms &= ~Permissions.WRITE                  # Now only Permissions.READ (1)
```

## IntFlag for Integer Flag Operations

```python
from enum import IntFlag, auto

class FileMode(IntFlag):
    READ = 4
    WRITE = 2
    EXECUTE = 1
    
# Can mix with integers
mode = FileMode.READ | 2              # FileMode.READ|WRITE (6)
mode |= 1                             # FileMode.READ|WRITE|EXECUTE (7)
```

## Enum with Custom Methods

```python
class HTTPStatus(Enum):
    OK = 200
    NOT_FOUND = 404
    SERVER_ERROR = 500
    
    @property
    def is_error(self):
        return self.value >= 400
    
    def describe(self):
        descriptions = {
            HTTPStatus.OK: "Request succeeded",
            HTTPStatus.NOT_FOUND: "Resource not found",
            HTTPStatus.SERVER_ERROR: "Internal server error"
        }
        return descriptions.get(self)

# Usage
print(HTTPStatus.NOT_FOUND.is_error)       # True
print(HTTPStatus.OK.describe())            # "Request succeeded"
```

## Enum Value Validation

```python
class Temperature(float, Enum):
    CELSIUS = 1.0
    FAHRENHEIT = 2.0
    
    @classmethod
    def _missing_(cls, value):
        # Custom logic for handling missing values
        if isinstance(value, float):
            if abs(value - 1.0) < 0.01:
                return cls.CELSIUS
            elif abs(value - 2.0) < 0.01:
                return cls.FAHRENHEIT
        return None  # Or raise ValueError

# Usage
temp = Temperature(0.99)  # Will return Temperature.CELSIUS
```

## Functional API for Creating Enums

```python
from enum import Enum

# Create enum dynamically
Animal = Enum('Animal', ['DOG', 'CAT', 'BIRD'])

# With custom values
Color = Enum('Color', {'RED': 1, 'GREEN': 2, 'BLUE': 3})

# Auto-incrementing with start value
Size = Enum('Size', 'SMALL MEDIUM LARGE', start=10)  # 10, 11, 12
```

## ExtendedEnum - Adding ClassMethods

```python
class ExtendedEnum(Enum):
    @classmethod
    def list_names(cls):
        return list(map(lambda c: c.name, cls))
    
    @classmethod
    def list_values(cls):
        return list(map(lambda c: c.value, cls))
    
    @classmethod
    def to_dict(cls):
        return {member.name: member.value for member in cls}

class Direction(ExtendedEnum):
    NORTH = 'N'
    EAST = 'E'
    SOUTH = 'S'
    WEST = 'W'

# Usage
print(Direction.list_names())  # ['NORTH', 'EAST', 'SOUTH', 'WEST']
print(Direction.list_values()) # ['N', 'E', 'S', 'W']
print(Direction.to_dict())     # {'NORTH': 'N', 'EAST': 'E', 'SOUTH': 'S', 'WEST': 'W'}
```

## Using Decorators with Enums

```python
from enum import Enum
from functools import total_ordering

@total_ordering
class Grade(Enum):
    A = 5
    B = 4
    C = 3
    D = 2
    F = 1
    
    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.value < other.value
        return NotImplemented

# Now all comparison operators work
print(Grade.A > Grade.C)  # True
print(Grade.F <= Grade.D) # True
print(sorted(Grade))      # [<Grade.F: 1>, <Grade.D: 2>, <Grade.C: 3>, <Grade.B: 4>, <Grade.A: 5>]
```

## JSON Serialization

```python
import json
from enum import Enum

class Status(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    
# Direct serialization (for str, Enum)
json_str = json.dumps(Status.PENDING)  # "pending"

# Custom serialization
def serialize_enum(obj):
    if isinstance(obj, Enum):
        return obj.value
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

# Usage
task = {"id": 1, "status": Status.PENDING}
json_str = json.dumps(task, default=serialize_enum)  # {"id": 1, "status": "pending"}
```

## Common Use Cases

### State Machines
```python
class State(Enum):
    IDLE = auto()
    RUNNING = auto()
    PAUSED = auto()
    FINISHED = auto()
    ERROR = auto()
    
    def next_state(self, event):
        transitions = {
            State.IDLE: {
                'start': State.RUNNING,
                'error': State.ERROR
            },
            State.RUNNING: {
                'pause': State.PAUSED,
                'complete': State.FINISHED,
                'error': State.ERROR
            },
            State.PAUSED: {
                'resume': State.RUNNING,
                'stop': State.IDLE,
                'error': State.ERROR
            },
            State.ERROR: {
                'reset': State.IDLE
            },
            State.FINISHED: {
                'reset': State.IDLE
            }
        }
        
        return transitions.get(self, {}).get(event, self)
```

### Configuration Options
```python
class LogLevel(Enum):
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50
    
    @classmethod
    def from_string(cls, level_name):
        return cls.__members__.get(level_name.upper(), cls.INFO)

# Usage
config_level = "debug"
log_level = LogLevel.from_string(config_level)  # LogLevel.DEBUG
```

### API Status Codes
```python
class APIStatus(int, Enum):
    SUCCESS = 200
    CREATED = 201
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    NOT_FOUND = 404
    SERVER_ERROR = 500
    
    @property
    def is_success(self):
        return 200 <= self.value < 300
    
    @property
    def is_client_error(self):
        return 400 <= self.value < 500
    
    @property
    def is_server_error(self):
        return self.value >= 500
```

## Tips and Best Practices

1. **Choose meaningful names**: Use uppercase for enum members following Python's constant naming convention.

2. **Use functional styles** when creating enums dynamically or when you need to auto-generate values.

3. **Prefer `auto()` for sequential values** rather than hard-coding numbers that may need to change.

4. **Use `str` or `int` mix-ins** when you need enums to behave like those primitive types.

5. **Consider `Flag` or `IntFlag`** for permissions, options, or any bitwise operations.

6. **Extend `Enum` class** with utility methods for common operations.

7. **Document enum values** with descriptive comments, especially for domain-specific values.

8. **Be careful with mutability**: While enum members themselves are immutable, if their values are mutable objects (like lists), those can be changed.

9. **Avoid using `_value_`** directly; use the `.value` property instead.

10. **Consider performance implications** of complex enums with many custom methods in performance-critical code.
