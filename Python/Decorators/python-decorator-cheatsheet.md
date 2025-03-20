# Python Built-in Decorators Cheatsheet
# Python Built-in Decorators Cheatsheet

## 1. @classmethod

Converts a method to a class method that receives the class as its first argument (`cls`) instead of the instance (`self`).

**Use Cases:**
- Alternative constructors
- Factory methods
- Methods that modify class state

```python
class Person:
    count = 0
    
    def __init__(self, name, age):
        self.name = name
        self.age = age
        Person.count += 1
    
    @classmethod
    def from_birth_year(cls, name, birth_year):
        """Alternative constructor that calculates age from birth year"""
        import datetime
        current_year = datetime.datetime.now().year
        return cls(name, current_year - birth_year)
    
    @classmethod
    def get_count(cls):
        """Returns the number of Person instances created"""
        return cls.count

# Using the regular constructor
person1 = Person("Alice", 30)

# Using the class method as an alternative constructor
person2 = Person.from_birth_year("Bob", 1990)

# Using class method to access class state
print(Person.get_count())  # Output: 2
```

## 2. @staticmethod

Defines a method that doesn't receive any special first argument. It behaves like a regular function but belongs to the class's namespace.

**Use Cases:**
- Utility functions related to the class
- Methods that don't need access to instance or class state

```python
class MathOperations:
    def __init__(self, value):
        self.value = value
    
    def add(self, other):
        return self.value + other
    
    @staticmethod
    def is_even(num):
        """Check if a number is even"""
        return num % 2 == 0
    
    @staticmethod
    def add_numbers(x, y):
        """Simple utility function"""
        return x + y

# Using instance method
math_op = MathOperations(5)
print(math_op.add(3))  # Output: 8

# Using static methods (can be called on class or instance)
print(MathOperations.is_even(4))  # Output: True
print(math_op.is_even(4))         # Output: True (same result)
print(MathOperations.add_numbers(10, 20))  # Output: 30
```

## 3. @property

Converts a method into a read-only attribute (getter).

**Use Cases:**
- Computed properties
- Controlled attribute access
- Backward compatibility when changing implementation

```python
class Circle:
    def __init__(self, radius):
        self._radius = radius
    
    @property
    def radius(self):
        """Getter for radius"""
        return self._radius
    
    @property
    def diameter(self):
        """Computed property: diameter = 2 * radius"""
        return 2 * self._radius
    
    @property
    def area(self):
        """Computed property: area = π * radius²"""
        import math
        return math.pi * (self._radius ** 2)

# Create a circle with radius 5
circle = Circle(5)

# Access properties as if they were attributes
print(circle.radius)    # Output: 5
print(circle.diameter)  # Output: 10
print(circle.area)      # Output: 78.53981633974483

# This will raise an AttributeError (read-only property)
# circle.radius = 10
```

## 4. @property.setter

Defines a setter method for a property, allowing assignment to the property.

**Use Cases:**
- Input validation
- Computed or dependent attributes
- Triggering actions on value change

```python
class Temperature:
    def __init__(self, celsius=0):
        self._celsius = celsius
    
    @property
    def celsius(self):
        """Getter for celsius"""
        return self._celsius
    
    @celsius.setter
    def celsius(self, value):
        """Setter for celsius with validation"""
        if value < -273.15:
            raise ValueError("Temperature below absolute zero is not possible")
        self._celsius = value
    
    @property
    def fahrenheit(self):
        """Getter for fahrenheit"""
        return (self._celsius * 9/5) + 32
    
    @fahrenheit.setter
    def fahrenheit(self, value):
        """Setter for fahrenheit (converts to celsius)"""
        celsius = (value - 32) * 5/9
        if celsius < -273.15:
            raise ValueError("Temperature below absolute zero is not possible")
        self._celsius = celsius

# Create a temperature object
temp = Temperature(25)

# Use getters
print(temp.celsius)     # Output: 25
print(temp.fahrenheit)  # Output: 77.0

# Use setters
temp.celsius = 30
print(temp.celsius)     # Output: 30
print(temp.fahrenheit)  # Output: 86.0

temp.fahrenheit = 68
print(temp.celsius)     # Output: 20.0
print(temp.fahrenheit)  # Output: 68.0

# This will raise a ValueError
# temp.celsius = -300
```

## 5. @property.deleter

Defines a deleter method for a property to customize behavior when the property is deleted.

**Use Cases:**
- Resource cleanup
- Resetting to default values
- Custom delete behavior

```python
class User:
    def __init__(self, username, password):
        self._username = username
        self._password = password
        self._is_active = True
    
    @property
    def username(self):
        return self._username
    
    @property
    def is_active(self):
        return self._is_active
    
    @property
    def password(self):
        raise AttributeError("Password cannot be accessed directly")
    
    @password.setter
    def password(self, new_password):
        if len(new_password) < 8:
            raise ValueError("Password must be at least 8 characters long")
        self._password = new_password
    
    @password.deleter
    def password(self):
        """Reset password when deleted"""
        print("Password has been reset to default")
        self._password = "default_password"
    
    @username.deleter
    def username(self):
        """Deactivate account when username is deleted"""
        print(f"Deactivating account for {self._username}")
        self._is_active = False
        self._username = None

# Create a user
user = User("john_doe", "secure_password123")

# Change password
user.password = "new_secure_password"

# Delete password (reset to default)
del user.password

# Delete username (deactivate account)
del user.username
print(f"Account active: {user.is_active}")  # Output: Account active: False
```

## 6. functools.lru_cache

Caches the results of function calls to avoid redundant calculations.

**Use Cases:**
- Expensive computations
- API calls
- Database queries

```python
import functools
import time

@functools.lru_cache(maxsize=128)
def fibonacci(n):
    """Calculate the nth Fibonacci number (recursive implementation)"""
    if n <= 1:
        return n
    print(f"Computing fibonacci({n})")
    return fibonacci(n-1) + fibonacci(n-2)

# First call: will compute and cache all sub-calculations
start = time.time()
print(f"fibonacci(30) = {fibonacci(30)}")
end = time.time()
print(f"First call took {end - start:.4f} seconds")

# Second call: will use cached result
start = time.time()
print(f"fibonacci(30) = {fibonacci(30)}")
end = time.time()
print(f"Second call took {end - start:.4f} seconds")

# Information about cache performance
print(fibonacci.cache_info())
```

## 7. functools.partial

Creates a new function with some arguments preset.

**Use Cases:**
- Creating specialized versions of existing functions
- Function factories
- Callbacks with preset arguments

```python
import functools

def power(base, exponent):
    return base ** exponent

# Create specialized versions of the power function
square = functools.partial(power, exponent=2)
cube = functools.partial(power, exponent=3)
power_of_two = functools.partial(power, base=2)

# Usage
print(square(5))       # Output: 25 (5^2)
print(cube(5))         # Output: 125 (5^3)
print(power_of_two(8)) # Output: 256 (2^8)

# Partial functions can be useful with higher-order functions
numbers = [1, 2, 3, 4, 5]
squares = list(map(square, numbers))
print(squares)  # Output: [1, 4, 9, 16, 25]
```

## 8. functools.wraps

Preserves metadata of the original function when creating decorators.

**Use Cases:**
- Creating decorators that preserve function metadata
- Maintaining documentation and type hints

```python
import functools
import time

def timing_decorator(func):
    @functools.wraps(func)  # Preserves metadata of the original function
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"{func.__name__} executed in {end_time - start_time:.4f} seconds")
        return result
    return wrapper

@timing_decorator
def slow_function(n):
    """This function demonstrates the timing decorator by sleeping for n seconds."""
    time.sleep(n)
    return n * n

# Call the function
result = slow_function(2)
print(f"Result: {result}")

# Metadata is preserved
print(f"Function name: {slow_function.__name__}")
print(f"Docstring: {slow_function.__doc__}")

# Without @wraps, the function name would be 'wrapper' and docstring would be lost
```

## 9. @abstractmethod (from abc module)

Marks a method as abstract, requiring subclasses to implement it.

**Use Cases:**
- Defining interfaces
- Enforcing implementations in subclasses
- Creating abstract base classes

```python
from abc import ABC, abstractmethod

class Shape(ABC):
    @abstractmethod
    def area(self):
        """Calculate the area of the shape"""
        pass
    
    @abstractmethod
    def perimeter(self):
        """Calculate the perimeter of the shape"""
        pass
    
    def description(self):
        """Non-abstract method with default implementation"""
        return f"A shape with area {self.area()} and perimeter {self.perimeter()}"

class Rectangle(Shape):
    def __init__(self, width, height):
        self.width = width
        self.height = height
    
    def area(self):
        return self.width * self.height
    
    def perimeter(self):
        return 2 * (self.width + self.height)

class Circle(Shape):
    def __init__(self, radius):
        self.radius = radius
    
    def area(self):
        import math
        return math.pi * (self.radius ** 2)
    
    def perimeter(self):
        import math
        return 2 * math.pi * self.radius

# This would raise TypeError: Can't instantiate abstract class Shape with abstract methods area, perimeter
# shape = Shape()

# Concrete implementations can be instantiated
rectangle = Rectangle(5, 3)
print(f"Rectangle area: {rectangle.area()}")
print(f"Rectangle description: {rectangle.description()}")

circle = Circle(4)
print(f"Circle area: {circle.area()}")
print(f"Circle perimeter: {circle.perimeter()}")
```

## 10. @total_ordering (from functools)

Automatically generates comparison methods based on a single comparison method.

**Use Cases:**
- Classes that need all comparison operators
- Reducing boilerplate code for ordered classes

```python
import functools

@functools.total_ordering
class Version:
    def __init__(self, major, minor, patch):
        self.major = major
        self.minor = minor
        self.patch = patch
    
    def __eq__(self, other):
        if not isinstance(other, Version):
            return NotImplemented
        return (self.major, self.minor, self.patch) == (other.major, other.minor, other.patch)
    
    def __lt__(self, other):
        if not isinstance(other, Version):
            return NotImplemented
        return (self.major, self.minor, self.patch) < (other.major, other.minor, other.patch)
    
    def __repr__(self):
        return f"Version({self.major}, {self.minor}, {self.patch})"

# Create version objects
v1 = Version(1, 0, 0)
v2 = Version(1, 2, 3)
v3 = Version(1, 2, 3)
v4 = Version(2, 0, 0)

# Test equality
print(f"{v1} == {v2}: {v1 == v2}")  # False
print(f"{v2} == {v3}: {v2 == v3}")  # True

# Test generated comparison methods
print(f"{v1} < {v2}: {v1 < v2}")    # True
print(f"{v1} <= {v2}: {v1 <= v2}")  # True
print(f"{v2} > {v1}: {v2 > v1}")    # True
print(f"{v2} >= {v3}: {v2 >= v3}")  # True
print(f"{v4} > {v2}: {v4 > v2}")    # True
```

## 11. contextlib.contextmanager

Converts a generator function into a context manager.

**Use Cases:**
- Resource management
- Creating simple context managers
- Temporary state changes

```python
import contextlib
import time

@contextlib.contextmanager
def timer(name):
    """Context manager for timing code blocks"""
    start_time = time.time()
    try:
        yield  # This is where the with-block's code executes
    finally:
        end_time = time.time()
        print(f"{name} took {end_time - start_time:.4f} seconds")

@contextlib.contextmanager
def temp_file(content, filename):
    """Context manager that creates a temporary file"""
    import os
    
    # Setup: create the file
    with open(filename, 'w') as f:
        f.write(content)
    print(f"Created temporary file: {filename}")
    
    try:
        yield filename  # This allows the with-block code to access the filename
    finally:
        # Cleanup: delete the file
        os.remove(filename)
        print(f"Removed temporary file: {filename}")

# Using the timer context manager
with timer("Sleep operation"):
    time.sleep(1)

# Using the temp_file context manager
with temp_file("Hello, World!", "temp.txt") as filename:
    # Code that uses the temporary file
    with open(filename, 'r') as f:
        content = f.read()
        print(f"File content: {content}")
    
    # The file will be automatically deleted after the with block
```

## 12. @dataclass (Python 3.7+)

Automatically generates special methods like `__init__`, `__repr__`, and `__eq__` for classes.

**Use Cases:**
- Data container classes
- Reducing boilerplate code
- Simple model classes

```python
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class Person:
    name: str
    age: int
    email: str = field(default="")
    phone: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    
    def is_adult(self):
        return self.age >= 18

@dataclass(frozen=True)  # Immutable dataclass
class Point:
    x: float
    y: float
    
    def distance_from_origin(self):
        return (self.x ** 2 + self.y ** 2) ** 0.5

# Create instances
person1 = Person("Alice", 30, "alice@example.com")
person2 = Person("Bob", 25, tags=["employee", "engineering"])
person3 = Person("Alice", 30, "alice@example.com")

# Automatic __repr__
print(person1)  # Person(name='Alice', age=30, email='alice@example.com', phone=None, tags=[])

# Automatic __eq__
print(f"person1 == person3: {person1 == person3}")  # True

# Custom methods still work
print(f"Is {person1.name} an adult? {person1.is_adult()}")  # True

# Frozen dataclass
point = Point(3, 4)
print(f"Distance from origin: {point.distance_from_origin()}")  # 5.0

# This raises an exception because the dataclass is frozen (immutable)
# point.x = 5
```

## 13. typing.overload (Python 3.5+)

Provides type hints for functions that can accept multiple argument types.

**Use Cases:**
- Type checking for polymorphic functions
- Functions with multiple valid call signatures
- Improved IDE support and static analysis

```python
from typing import overload, Union, List, Tuple, Optional

class Database:
    def __init__(self):
        self.data = {}
    
    @overload
    def get(self, id: int) -> dict: ...
    
    @overload
    def get(self, name: str) -> List[dict]: ...
    
    @overload
    def get(self, query: dict) -> List[dict]: ...
    
    def get(self, identifier):
        """
        Get records from database by different identifiers:
        - id (int): Returns a single record by ID
        - name (str): Returns a list of records matching the name
        - query (dict): Returns a list of records matching the query
        """
        if isinstance(identifier, int):
            # Return a single record by ID
            return self.data.get(identifier, {})
        elif isinstance(identifier, str):
            # Return records matching the name
            return [record for record in self.data.values() if record.get("name") == identifier]
        elif isinstance(identifier, dict):
            # Return records matching all criteria in the query
            result = []
            for record in self.data.values():
                match = True
                for key, value in identifier.items():
                    if record.get(key) != value:
                        match = False
                        break
                if match:
                    result.append(record)
            return result
        else:
            raise TypeError("Invalid identifier type")

# Note: The actual implementation is the final one.
# The @overload decorators are only for type checkers and don't affect runtime behavior.
```

## 14. functools.cached_property (Python 3.8+)

Combines @property and @lru_cache to create a cached property that's computed once per instance and then cached.

**Use Cases:**
- Expensive computed properties
- Lazy-loaded attributes
- Performance optimization

```python
import functools
import time

class DataAnalyzer:
    def __init__(self, data):
        self.data = data
    
    @functools.cached_property
    def sorted_data(self):
        """Expensive operation: sort the data"""
        print("Sorting data...")
        time.sleep(1)  # Simulate an expensive operation
        return sorted(self.data)
    
    @functools.cached_property
    def average(self):
        """Expensive operation: calculate average"""
        print("Calculating average...")
        time.sleep(1)  # Simulate an expensive operation
        return sum(self.data) / len(self.data)

# Create an analyzer with some data
analyzer = DataAnalyzer([3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5])

# First access: will compute and cache
print("First access to sorted_data:")
print(analyzer.sorted_data[:5])  # Display first 5 elements

# Second access: will use cached value
print("\nSecond access to sorted_data:")
print(analyzer.sorted_data[:5])  # No sorting message, uses cached value

# Access another cached property
print("\nAccessing average:")
print(f"Average: {analyzer.average}")

# Accessing again uses cached value
print("\nAccessing average again:")
print(f"Average: {analyzer.average}")

# Creating a new instance resets the cache
print("\nCreating new instance:")
analyzer2 = DataAnalyzer([7, 3, 8, 2, 1])
print(analyzer2.sorted_data)  # Will compute again for new instance
```

## 15. functools.singledispatch (Python 3.4+)

Enables function overloading based on the type of the first argument.

**Use Cases:**
- Type-specific behavior
- Polymorphic functions
- Extending functionality for different types

```python
import functools
from datetime import datetime, timedelta

@functools.singledispatch
def format_output(obj):
    """Default implementation for types without specific handlers"""
    return str(obj)

@format_output.register
def _(obj: int):
    """Format integers with commas as thousand separators"""
    return f"{obj:,}"

@format_output.register
def _(obj: float):
    """Format floats with 2 decimal places and commas"""
    return f"{obj:,.2f}"

@format_output.register
def _(obj: list):
    """Format lists as bulleted items"""
    if not obj:
        return "Empty list"
    return "\n".join(f"• {format_output(item)}" for item in obj)

@format_output.register
def _(obj: dict):
    """Format dictionaries as key-value pairs"""
    if not obj:
        return "Empty dictionary"
    return "\n".join(f"{k}: {format_output(v)}" for k, v in obj.items())

@format_output.register(datetime)
def _(obj):
    """Format datetime objects"""
    return obj.strftime("%Y-%m-%d %H:%M:%S")

# Usage with different types
print(format_output(1234567))
print(format_output(1234.5678))
print(format_output(["apple", 42, 3.14]))
print(format_output({"name": "John", "age": 30, "balance": 1234.56}))
print(format_output(datetime.now()))
print(format_output("Just a string"))  # Uses default implementation
```


I've created a comprehensive cheatsheet for Python's built-in decorators with practical code examples for each one.

The cheatsheet covers 15 key built-in decorators:

1. **@classmethod** - For methods that operate on the class itself
2. **@staticmethod** - For utility methods that don't need class/instance access
3. **@property** - For getter methods that act like attributes
4. **@property.setter** - For setter methods with validation
5. **@property.deleter** - For custom deletion behavior
6. **@functools.lru_cache** - For caching function results
7. **@functools.partial** - For creating specialized versions of functions
8. **@functools.wraps** - For preserving metadata in decorators
9. **@abstractmethod** - For defining abstract interfaces
10. **@functools.total_ordering** - For generating comparison methods
11. **@contextlib.contextmanager** - For creating context managers
12. **@dataclass** - For creating data container classes
13. **@typing.overload** - For type hints with multiple signatures
14. **@functools.cached_property** - For cached computed properties
15. **@functools.singledispatch** - For type-based function overloading

Each section includes:
- A clear explanation of what the decorator does
- Common use cases
- Practical code examples showing real-world application
- Expected outputs where relevant

## 1. @classmethod

Converts a method to a class method that receives the class as its first argument (`cls`) instead of the instance (`self`).

**Use Cases:**
- Alternative constructors
- Factory methods
- Methods that modify class state

```python
class Person:
    count = 0
    
    def __init__(self, name, age):
        self.name = name
        self.age = age
        Person.count += 1
    
    @classmethod
    def from_birth_year(cls, name, birth_year):
        """Alternative constructor that calculates age from birth year"""
        import datetime
        current_year = datetime.datetime.now().year
        return cls(name, current_year - birth_year)
    
    @classmethod
    def get_count(cls):
        """Returns the number of Person instances created"""
        return cls.count

# Using the regular constructor
person1 = Person("Alice", 30)

# Using the class method as an alternative constructor
person2 = Person.from_birth_year("Bob", 1990)

# Using class method to access class state
print(Person.get_count())  # Output: 2
```

## 2. @staticmethod

Defines a method that doesn't receive any special first argument. It behaves like a regular function but belongs to the class's namespace.

**Use Cases:**
- Utility functions related to the class
- Methods that don't need access to instance or class state

```python
class MathOperations:
    def __init__(self, value):
        self.value = value
    
    def add(self, other):
        return self.value + other
    
    @staticmethod
    def is_even(num):
        """Check if a number is even"""
        return num % 2 == 0
    
    @staticmethod
    def add_numbers(x, y):
        """Simple utility function"""
        return x + y

# Using instance method
math_op = MathOperations(5)
print(math_op.add(3))  # Output: 8

# Using static methods (can be called on class or instance)
print(MathOperations.is_even(4))  # Output: True
print(math_op.is_even(4))         # Output: True (same result)
print(MathOperations.add_numbers(10, 20))  # Output: 30
```

## 3. @property

Converts a method into a read-only attribute (getter).

**Use Cases:**
- Computed properties
- Controlled attribute access
- Backward compatibility when changing implementation

```python
class Circle:
    def __init__(self, radius):
        self._radius = radius
    
    @property
    def radius(self):
        """Getter for radius"""
        return self._radius
    
    @property
    def diameter(self):
        """Computed property: diameter = 2 * radius"""
        return 2 * self._radius
    
    @property
    def area(self):
        """Computed property: area = π * radius²"""
        import math
        return math.pi * (self._radius ** 2)

# Create a circle with radius 5
circle = Circle(5)

# Access properties as if they were attributes
print(circle.radius)    # Output: 5
print(circle.diameter)  # Output: 10
print(circle.area)      # Output: 78.53981633974483

# This will raise an AttributeError (read-only property)
# circle.radius = 10
```

## 4. @property.setter

Defines a setter method for a property, allowing assignment to the property.

**Use Cases:**
- Input validation
- Computed or dependent attributes
- Triggering actions on value change

```python
class Temperature:
    def __init__(self, celsius=0):
        self._celsius = celsius
    
    @property
    def celsius(self):
        """Getter for celsius"""
        return self._celsius
    
    @celsius.setter
    def celsius(self, value):
        """Setter for celsius with validation"""
        if value < -273.15:
            raise ValueError("Temperature below absolute zero is not possible")
        self._celsius = value
    
    @property
    def fahrenheit(self):
        """Getter for fahrenheit"""
        return (self._celsius * 9/5) + 32
    
    @fahrenheit.setter
    def fahrenheit(self, value):
        """Setter for fahrenheit (converts to celsius)"""
        celsius = (value - 32) * 5/9
        if celsius < -273.15:
            raise ValueError("Temperature below absolute zero is not possible")
        self._celsius = celsius

# Create a temperature object
temp = Temperature(25)

# Use getters
print(temp.celsius)     # Output: 25
print(temp.fahrenheit)  # Output: 77.0

# Use setters
temp.celsius = 30
print(temp.celsius)     # Output: 30
print(temp.fahrenheit)  # Output: 86.0

temp.fahrenheit = 68
print(temp.celsius)     # Output: 20.0
print(temp.fahrenheit)  # Output: 68.0

# This will raise a ValueError
# temp.celsius = -300
```

## 5. @property.deleter

Defines a deleter method for a property to customize behavior when the property is deleted.

**Use Cases:**
- Resource cleanup
- Resetting to default values
- Custom delete behavior

```python
class User:
    def __init__(self, username, password):
        self._username = username
        self._password = password
        self._is_active = True
    
    @property
    def username(self):
        return self._username
    
    @property
    def is_active(self):
        return self._is_active
    
    @property
    def password(self):
        raise AttributeError("Password cannot be accessed directly")
    
    @password.setter
    def password(self, new_password):
        if len(new_password) < 8:
            raise ValueError("Password must be at least 8 characters long")
        self._password = new_password
    
    @password.deleter
    def password(self):
        """Reset password when deleted"""
        print("Password has been reset to default")
        self._password = "default_password"
    
    @username.deleter
    def username(self):
        """Deactivate account when username is deleted"""
        print(f"Deactivating account for {self._username}")
        self._is_active = False
        self._username = None

# Create a user
user = User("john_doe", "secure_password123")

# Change password
user.password = "new_secure_password"

# Delete password (reset to default)
del user.password

# Delete username (deactivate account)
del user.username
print(f"Account active: {user.is_active}")  # Output: Account active: False
```

## 6. functools.lru_cache

Caches the results of function calls to avoid redundant calculations.

**Use Cases:**
- Expensive computations
- API calls
- Database queries

```python
import functools
import time

@functools.lru_cache(maxsize=128)
def fibonacci(n):
    """Calculate the nth Fibonacci number (recursive implementation)"""
    if n <= 1:
        return n
    print(f"Computing fibonacci({n})")
    return fibonacci(n-1) + fibonacci(n-2)

# First call: will compute and cache all sub-calculations
start = time.time()
print(f"fibonacci(30) = {fibonacci(30)}")
end = time.time()
print(f"First call took {end - start:.4f} seconds")

# Second call: will use cached result
start = time.time()
print(f"fibonacci(30) = {fibonacci(30)}")
end = time.time()
print(f"Second call took {end - start:.4f} seconds")

# Information about cache performance
print(fibonacci.cache_info())
```

## 7. functools.partial

Creates a new function with some arguments preset.

**Use Cases:**
- Creating specialized versions of existing functions
- Function factories
- Callbacks with preset arguments

```python
import functools

def power(base, exponent):
    return base ** exponent

# Create specialized versions of the power function
square = functools.partial(power, exponent=2)
cube = functools.partial(power, exponent=3)
power_of_two = functools.partial(power, base=2)

# Usage
print(square(5))       # Output: 25 (5^2)
print(cube(5))         # Output: 125 (5^3)
print(power_of_two(8)) # Output: 256 (2^8)

# Partial functions can be useful with higher-order functions
numbers = [1, 2, 3, 4, 5]
squares = list(map(square, numbers))
print(squares)  # Output: [1, 4, 9, 16, 25]
```

## 8. functools.wraps

Preserves metadata of the original function when creating decorators.

**Use Cases:**
- Creating decorators that preserve function metadata
- Maintaining documentation and type hints

```python
import functools
import time

def timing_decorator(func):
    @functools.wraps(func)  # Preserves metadata of the original function
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"{func.__name__} executed in {end_time - start_time:.4f} seconds")
        return result
    return wrapper

@timing_decorator
def slow_function(n):
    """This function demonstrates the timing decorator by sleeping for n seconds."""
    time.sleep(n)
    return n * n

# Call the function
result = slow_function(2)
print(f"Result: {result}")

# Metadata is preserved
print(f"Function name: {slow_function.__name__}")
print(f"Docstring: {slow_function.__doc__}")

# Without @wraps, the function name would be 'wrapper' and docstring would be lost
```

## 9. @abstractmethod (from abc module)

Marks a method as abstract, requiring subclasses to implement it.

**Use Cases:**
- Defining interfaces
- Enforcing implementations in subclasses
- Creating abstract base classes

```python
from abc import ABC, abstractmethod

class Shape(ABC):
    @abstractmethod
    def area(self):
        """Calculate the area of the shape"""
        pass
    
    @abstractmethod
    def perimeter(self):
        """Calculate the perimeter of the shape"""
        pass
    
    def description(self):
        """Non-abstract method with default implementation"""
        return f"A shape with area {self.area()} and perimeter {self.perimeter()}"

class Rectangle(Shape):
    def __init__(self, width, height):
        self.width = width
        self.height = height
    
    def area(self):
        return self.width * self.height
    
    def perimeter(self):
        return 2 * (self.width + self.height)

class Circle(Shape):
    def __init__(self, radius):
        self.radius = radius
    
    def area(self):
        import math
        return math.pi * (self.radius ** 2)
    
    def perimeter(self):
        import math
        return 2 * math.pi * self.radius

# This would raise TypeError: Can't instantiate abstract class Shape with abstract methods area, perimeter
# shape = Shape()

# Concrete implementations can be instantiated
rectangle = Rectangle(5, 3)
print(f"Rectangle area: {rectangle.area()}")
print(f"Rectangle description: {rectangle.description()}")

circle = Circle(4)
print(f"Circle area: {circle.area()}")
print(f"Circle perimeter: {circle.perimeter()}")
```

## 10. @total_ordering (from functools)

Automatically generates comparison methods based on a single comparison method.

**Use Cases:**
- Classes that need all comparison operators
- Reducing boilerplate code for ordered classes

```python
import functools

@functools.total_ordering
class Version:
    def __init__(self, major, minor, patch):
        self.major = major
        self.minor = minor
        self.patch = patch
    
    def __eq__(self, other):
        if not isinstance(other, Version):
            return NotImplemented
        return (self.major, self.minor, self.patch) == (other.major, other.minor, other.patch)
    
    def __lt__(self, other):
        if not isinstance(other, Version):
            return NotImplemented
        return (self.major, self.minor, self.patch) < (other.major, other.minor, other.patch)
    
    def __repr__(self):
        return f"Version({self.major}, {self.minor}, {self.patch})"

# Create version objects
v1 = Version(1, 0, 0)
v2 = Version(1, 2, 3)
v3 = Version(1, 2, 3)
v4 = Version(2, 0, 0)

# Test equality
print(f"{v1} == {v2}: {v1 == v2}")  # False
print(f"{v2} == {v3}: {v2 == v3}")  # True

# Test generated comparison methods
print(f"{v1} < {v2}: {v1 < v2}")    # True
print(f"{v1} <= {v2}: {v1 <= v2}")  # True
print(f"{v2} > {v1}: {v2 > v1}")    # True
print(f"{v2} >= {v3}: {v2 >= v3}")  # True
print(f"{v4} > {v2}: {v4 > v2}")    # True
```

## 11. contextlib.contextmanager

Converts a generator function into a context manager.

**Use Cases:**
- Resource management
- Creating simple context managers
- Temporary state changes

```python
import contextlib
import time

@contextlib.contextmanager
def timer(name):
    """Context manager for timing code blocks"""
    start_time = time.time()
    try:
        yield  # This is where the with-block's code executes
    finally:
        end_time = time.time()
        print(f"{name} took {end_time - start_time:.4f} seconds")

@contextlib.contextmanager
def temp_file(content, filename):
    """Context manager that creates a temporary file"""
    import os
    
    # Setup: create the file
    with open(filename, 'w') as f:
        f.write(content)
    print(f"Created temporary file: {filename}")
    
    try:
        yield filename  # This allows the with-block code to access the filename
    finally:
        # Cleanup: delete the file
        os.remove(filename)
        print(f"Removed temporary file: {filename}")

# Using the timer context manager
with timer("Sleep operation"):
    time.sleep(1)

# Using the temp_file context manager
with temp_file("Hello, World!", "temp.txt") as filename:
    # Code that uses the temporary file
    with open(filename, 'r') as f:
        content = f.read()
        print(f"File content: {content}")
    
    # The file will be automatically deleted after the with block
```

## 12. @dataclass (Python 3.7+)

Automatically generates special methods like `__init__`, `__repr__`, and `__eq__` for classes.

**Use Cases:**
- Data container classes
- Reducing boilerplate code
- Simple model classes

```python
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class Person:
    name: str
    age: int
    email: str = field(default="")
    phone: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    
    def is_adult(self):
        return self.age >= 18

@dataclass(frozen=True)  # Immutable dataclass
class Point:
    x: float
    y: float
    
    def distance_from_origin(self):
        return (self.x ** 2 + self.y ** 2) ** 0.5

# Create instances
person1 = Person("Alice", 30, "alice@example.com")
person2 = Person("Bob", 25, tags=["employee", "engineering"])
person3 = Person("Alice", 30, "alice@example.com")

# Automatic __repr__
print(person1)  # Person(name='Alice', age=30, email='alice@example.com', phone=None, tags=[])

# Automatic __eq__
print(f"person1 == person3: {person1 == person3}")  # True

# Custom methods still work
print(f"Is {person1.name} an adult? {person1.is_adult()}")  # True

# Frozen dataclass
point = Point(3, 4)
print(f"Distance from origin: {point.distance_from_origin()}")  # 5.0

# This raises an exception because the dataclass is frozen (immutable)
# point.x = 5
```

## 13. typing.overload (Python 3.5+)

Provides type hints for functions that can accept multiple argument types.

**Use Cases:**
- Type checking for polymorphic functions
- Functions with multiple valid call signatures
- Improved IDE support and static analysis

```python
from typing import overload, Union, List, Tuple, Optional

class Database:
    def __init__(self):
        self.data = {}
    
    @overload
    def get(self, id: int) -> dict: ...
    
    @overload
    def get(self, name: str) -> List[dict]: ...
    
    @overload
    def get(self, query: dict) -> List[dict]: ...
    
    def get(self, identifier):
        """
        Get records from database by different identifiers:
        - id (int): Returns a single record by ID
        - name (str): Returns a list of records matching the name
        - query (dict): Returns a list of records matching the query
        """
        if isinstance(identifier, int):
            # Return a single record by ID
            return self.data.get(identifier, {})
        elif isinstance(identifier, str):
            # Return records matching the name
            return [record for record in self.data.values() if record.get("name") == identifier]
        elif isinstance(identifier, dict):
            # Return records matching all criteria in the query
            result = []
            for record in self.data.values():
                match = True
                for key, value in identifier.items():
                    if record.get(key) != value:
                        match = False
                        break
                if match:
                    result.append(record)
            return result
        else:
            raise TypeError("Invalid identifier type")

# Note: The actual implementation is the final one.
# The @overload decorators are only for type checkers and don't affect runtime behavior.
```

## 14. functools.cached_property (Python 3.8+)

Combines @property and @lru_cache to create a cached property that's computed once per instance and then cached.

**Use Cases:**
- Expensive computed properties
- Lazy-loaded attributes
- Performance optimization

```python
import functools
import time

class DataAnalyzer:
    def __init__(self, data):
        self.data = data
    
    @functools.cached_property
    def sorted_data(self):
        """Expensive operation: sort the data"""
        print("Sorting data...")
        time.sleep(1)  # Simulate an expensive operation
        return sorted(self.data)
    
    @functools.cached_property
    def average(self):
        """Expensive operation: calculate average"""
        print("Calculating average...")
        time.sleep(1)  # Simulate an expensive operation
        return sum(self.data) / len(self.data)

# Create an analyzer with some data
analyzer = DataAnalyzer([3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5])

# First access: will compute and cache
print("First access to sorted_data:")
print(analyzer.sorted_data[:5])  # Display first 5 elements

# Second access: will use cached value
print("\nSecond access to sorted_data:")
print(analyzer.sorted_data[:5])  # No sorting message, uses cached value

# Access another cached property
print("\nAccessing average:")
print(f"Average: {analyzer.average}")

# Accessing again uses cached value
print("\nAccessing average again:")
print(f"Average: {analyzer.average}")

# Creating a new instance resets the cache
print("\nCreating new instance:")
analyzer2 = DataAnalyzer([7, 3, 8, 2, 1])
print(analyzer2.sorted_data)  # Will compute again for new instance
```

## 15. functools.singledispatch (Python 3.4+)

Enables function overloading based on the type of the first argument.

**Use Cases:**
- Type-specific behavior
- Polymorphic functions
- Extending functionality for different types

```python
import functools
from datetime import datetime, timedelta

@functools.singledispatch
def format_output(obj):
    """Default implementation for types without specific handlers"""
    return str(obj)

@format_output.register
def _(obj: int):
    """Format integers with commas as thousand separators"""
    return f"{obj:,}"

@format_output.register
def _(obj: float):
    """Format floats with 2 decimal places and commas"""
    return f"{obj:,.2f}"

@format_output.register
def _(obj: list):
    """Format lists as bulleted items"""
    if not obj:
        return "Empty list"
    return "\n".join(f"• {format_output(item)}" for item in obj)

@format_output.register
def _(obj: dict):
    """Format dictionaries as key-value pairs"""
    if not obj:
        return "Empty dictionary"
    return "\n".join(f"{k}: {format_output(v)}" for k, v in obj.items())

@format_output.register(datetime)
def _(obj):
    """Format datetime objects"""
    return obj.strftime("%Y-%m-%d %H:%M:%S")

# Usage with different types
print(format_output(1234567))
print(format_output(1234.5678))
print(format_output(["apple", 42, 3.14]))
print(format_output({"name": "John", "age": 30, "balance": 1234.56}))
print(format_output(datetime.now()))
print(format_output("Just a string"))  # Uses default implementation
```
