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
