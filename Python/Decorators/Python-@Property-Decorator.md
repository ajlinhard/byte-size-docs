# Using the @property Decorator in Python

The `@property` decorator in Python transforms a method into a getter for a property, allowing you to access the method as if it were an attribute. This pattern provides several key benefits:

## Main Use Cases

1. **Controlled attribute access**: Create read-only attributes or add validation when setting values
2. **Computed properties**: Define attributes that are calculated on demand
3. **Encapsulation**: Change the internal implementation without changing the public API
4. **Backward compatibility**: Convert existing attributes to properties without breaking code

Let me demonstrate these with examples:

### 1. Controlled Attribute Access

```python
class Person:
    def __init__(self, name, age):
        self._name = name
        self._age = age
    
    @property
    def age(self):
        return self._age
    
    @age.setter
    def age(self, value):
        if not isinstance(value, int):
            raise TypeError("Age must be an integer")
        if value < 0 or value > 150:
            raise ValueError("Age must be between 0 and 150")
        self._age = value
    
    @property
    def name(self):
        return self._name  # Read-only property (no setter defined)

# Usage
person = Person("Alice", 30)
print(person.age)  # Calls the getter: 30
person.age = 35    # Calls the setter with validation
# person.age = -5  # Would raise ValueError
# person.name = "Bob"  # Would raise AttributeError: can't set attribute
```

### 2. Computed Properties

```python
from datetime import date

class Employee:
    def __init__(self, first_name, last_name, birth_year):
        self.first_name = first_name
        self.last_name = last_name
        self.birth_year = birth_year
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def age(self):
        return date.today().year - self.birth_year

# Usage
employee = Employee("John", "Doe", 1985)
print(employee.full_name)  # John Doe
print(employee.age)  # Calculated based on current year
```

### 3. Encapsulation

```python
class Circle:
    def __init__(self, radius):
        self._radius = radius
    
    @property
    def radius(self):
        return self._radius
    
    @radius.setter
    def radius(self, value):
        if value < 0:
            raise ValueError("Radius cannot be negative")
        self._radius = value
    
    @property
    def area(self):
        # Internal implementation can change without affecting how
        # clients use the Circle class
        return 3.14159 * self._radius ** 2
    
    @property
    def diameter(self):
        return self._radius * 2

# Usage
circle = Circle(5)
print(circle.radius)   # 5
print(circle.area)     # 78.53975
print(circle.diameter) # 10

circle.radius = 10
# Internal state changes, but the API remains the same
print(circle.area)     # 314.159
```

### 4. Backward Compatibility

```python
class Temperature:
    def __init__(self):
        # Original implementation stored celsius
        self._celsius = 25
    
    # Later we want to change to store in kelvin internally,
    # but keep the same API
    @property
    def celsius(self):
        # Convert from internal kelvin to celsius for API compatibility
        return self._kelvin - 273.15
    
    @celsius.setter
    def celsius(self, value):
        # Store as kelvin internally
        self._kelvin = value + 273.15
    
    @property
    def kelvin(self):
        return self._kelvin

# Existing code still works the same way
temp = Temperature()
print(f"Temperature: {temp.celsius}°C")
temp.celsius = 30
print(f"New temperature: {temp.celsius}°C")
```

The `@property` decorator is a powerful tool for creating clean, intuitive interfaces while maintaining control over data access and manipulation in your Python classes.

---
# Python @property and @setter Decorators
---

The `@property` and `@setter` decorators in Python allow you to create managed attributes, giving you control over how attributes are accessed and modified without changing your public interface.

## Purpose of @property

The `@property` decorator transforms a method into an attribute-like accessor (getter), allowing you to:

1. Access the method as if it were an attribute (without parentheses)
2. Add validation logic when getting a value
3. Calculate values dynamically
4. Maintain backward compatibility when implementation details change

## Purpose of @setter

The `@setter` decorator creates a method to control how an attribute is modified, allowing you to:

1. Validate inputs before assignment
2. Transform values during assignment
3. Trigger side effects when values change
4. Prevent direct attribute modification

## Simple Use Case: Temperature Conversion

```python
class Celsius:
    def __init__(self, temperature=0):
        self._temperature = temperature

    @property
    def temperature(self):
        return self._temperature

    @temperature.setter
    def temperature(self, value):
        if value < -273.15:
            raise ValueError("Temperature below absolute zero is not possible")
        self._temperature = value

    @property
    def fahrenheit(self):
        return (self._temperature * 9/5) + 32
    
    @fahrenheit.setter
    def fahrenheit(self, value):
        self._temperature = (value - 32) * 5/9
```

Usage:
```python
c = Celsius(25)
print(c.temperature)  # 25
print(c.fahrenheit)   # 77.0

c.temperature = 30
print(c.fahrenheit)   # 86.0

c.fahrenheit = 68
print(c.temperature)  # 20.0

# This raises ValueError
# c.temperature = -300
```

## Complex Use Case: Database Integration

```python
class User:
    def __init__(self, user_id=None):
        self._id = user_id
        self._name = None
        self._email = None
        self._cached_transactions = None
        self._last_fetch = None
        
        if user_id:
            self._load_user_data()
    
    def _load_user_data(self):
        # Simulate database fetch
        database = {
            1: {"name": "Alice Smith", "email": "alice@example.com"},
            2: {"name": "Bob Jones", "email": "bob@example.com"}
        }
        if self._id in database:
            user_data = database[self._id]
            self._name = user_data["name"]
            self._email = user_data["email"]
    
    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, value):
        if not value or len(value) < 2:
            raise ValueError("Name must be at least 2 characters")
        
        # In real app, this would update the database
        print(f"Updating name in database: {value}")
        self._name = value
    
    @property
    def email(self):
        return self._email
    
    @email.setter
    def email(self, value):
        if not '@' in value:
            raise ValueError("Invalid email format")
            
        # In real app, this would update the database
        print(f"Updating email in database: {value}")
        self._email = value
    
    @property
    def transactions(self):
        # Lazy loading with caching
        current_time = 12345  # This would be actual timestamp
        
        # If cache is empty or older than 5 minutes, refresh it
        if (self._cached_transactions is None or 
                self._last_fetch is None or 
                current_time - self._last_fetch > 300):
            print("Fetching fresh transaction data...")
            # Simulate expensive database operation
            self._cached_transactions = [
                {"id": 101, "amount": 99.95, "date": "2025-05-14"},
                {"id": 102, "amount": 45.00, "date": "2025-05-15"}
            ]
            self._last_fetch = current_time
        
        return self._cached_transactions
```

Usage:
```python
user = User(1)
print(user.name)       # "Alice Smith"
print(user.email)      # "alice@example.com"

user.name = "Alice Johnson"  # Triggers database update logic
user.email = "alice.j@example.com"  # Triggers database update logic

# First access fetches from "database"
transactions = user.transactions
print(f"Transaction count: {len(transactions)}")

# Second access uses cached data (no message about fetching)
transactions_again = user.transactions
```

## Additional Advanced Use Cases

1. **Read-only properties**: Create attributes that can't be modified

```python
class Circle:
    def __init__(self, radius):
        self._radius = radius
        
    @property
    def radius(self):
        return self._radius
        
    @property
    def area(self):
        return 3.14159 * self._radius ** 2
    
    @property
    def circumference(self):
        return 2 * 3.14159 * self._radius
```

2. **Attribute dependencies**: Ensure related attributes stay in sync

```python
class Rectangle:
    def __init__(self, width, height):
        self._width = width
        self._height = height
        self._area = width * height
    
    @property
    def width(self):
        return self._width
    
    @width.setter
    def width(self, value):
        self._width = value
        self._area = value * self._height
    
    @property
    def height(self):
        return self._height
    
    @height.setter
    def height(self, value):
        self._height = value
        self._area = self._width * value
    
    @property
    def area(self):
        return self._area
```

3. **Deprecation warnings**: Smooth transition when changing APIs

```python
import warnings

class ApiClient:
    def __init__(self):
        self._api_key = None
    
    @property
    def api_key(self):
        return self._api_key
    
    @api_key.setter
    def api_key(self, value):
        self._api_key = value
    
    @property
    def auth_token(self):
        warnings.warn("auth_token is deprecated, use api_key instead", 
                      DeprecationWarning, stacklevel=2)
        return self._api_key
    
    @auth_token.setter
    def auth_token(self, value):
        warnings.warn("auth_token is deprecated, use api_key instead", 
                      DeprecationWarning, stacklevel=2)
        self._api_key = value
```

Properties and setters are powerful tools in Python that help you write more maintainable and robust code by encapsulating implementation details while preserving a clean public interface.
