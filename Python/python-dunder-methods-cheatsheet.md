# Python Dunder Methods Overview

Dunder methods (short for "double underscore" methods) are special methods in Python that have double underscores at the beginning and end of their names (e.g., `__init__`). They're also called "magic methods" because they enable Python objects to implement and customize standard language behaviors.

These methods allow you to define how your objects behave with built-in operations, such as:
- Object initialization and deletion
- Representation as strings
- Comparison operations
- Mathematical operations
- Container-like behaviors
- Attribute access
- Callable objects
- Context managers



# Python Dunder Methods Cheatsheet

## Initialization and Deletion

### `__init__(self, [args...])`
**Description:** Initializes a new instance of the class.  
**Use case:** Set up a new object with required attributes.
```python
class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age

person = Person("Alice", 30)  # Creates a new Person with name="Alice", age=30
```

### `__new__(cls, [args...])`
**Description:** Creates a new instance of the class (before `__init__` is called).  
**Use case:** Control instance creation, implement singletons or custom instance behaviors.
```python
class Singleton:
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

# Creates only one instance
s1 = Singleton()
s2 = Singleton()
print(s1 is s2)  # True
```

### `__del__(self)`
**Description:** Called when the object is about to be destroyed.  
**Use case:** Resource cleanup beyond garbage collection.
```python
class FileHandler:
    def __init__(self, filename):
        self.file = open(filename, 'w')
        
    def __del__(self):
        print("Closing file")
        self.file.close()

# When handler goes out of scope, the file will be closed
handler = FileHandler("example.txt")
```

## String Representation

### `__str__(self)`
**Description:** Returns a human-readable string representation.  
**Use case:** Display object in a user-friendly format; used by `str()` and `print()`.
```python
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __str__(self):
        return f"Point({self.x}, {self.y})"

p = Point(3, 4)
print(p)  # Output: Point(3, 4)
```

### `__repr__(self)`
**Description:** Returns an unambiguous string representation that should ideally be valid Python code.  
**Use case:** Debugging, logging, and displaying the object in the Python REPL.
```python
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __repr__(self):
        return f"Point({self.x}, {self.y})"

p = Point(3, 4)
print(repr(p))  # Output: Point(3, 4)
```

### `__format__(self, format_spec)`
**Description:** Defines behavior for string formatting with `format()` and f-strings.  
**Use case:** Custom formatting of object representation.
```python
class Money:
    def __init__(self, amount):
        self.amount = amount
    
    def __format__(self, format_spec):
        if format_spec == 'USD':
            return f"${self.amount:.2f}"
        elif format_spec == 'EUR':
            return f"€{self.amount:.2f}"
        return str(self.amount)

money = Money(42.5)
print(f"{money:USD}")  # Output: $42.50
print(f"{money:EUR}")  # Output: €42.50
```

## Comparison Operations

### `__eq__(self, other)`
**Description:** Defines behavior for the equality operator `==`.  
**Use case:** Custom equality checking.
```python
class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age
    
    def __eq__(self, other):
        if not isinstance(other, Person):
            return False
        return self.name == other.name and self.age == other.age

p1 = Person("Alice", 30)
p2 = Person("Alice", 30)
print(p1 == p2)  # True
```

### `__lt__(self, other)`
**Description:** Defines behavior for the less-than operator `<`.  
**Use case:** Enable sorting and comparison.
```python
class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age
    
    def __lt__(self, other):
        return self.age < other.age

people = [Person("Alice", 30), Person("Bob", 25)]
sorted_people = sorted(people)  # Sorts by age
print([p.name for p in sorted_people])  # Output: ['Bob', 'Alice']
```

### Other comparison methods
- `__gt__(self, other)`: Greater than (`>`)
- `__le__(self, other)`: Less than or equal (`<=`)
- `__ge__(self, other)`: Greater than or equal (`>=`)
- `__ne__(self, other)`: Not equal (`!=`)

## Mathematical Operations

### `__add__(self, other)`
**Description:** Defines behavior for the addition operator `+`.  
**Use case:** Custom addition logic.
```python
class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)
    
    def __str__(self):
        return f"Vector({self.x}, {self.y})"

v1 = Vector(1, 2)
v2 = Vector(3, 4)
print(v1 + v2)  # Output: Vector(4, 6)
```

### `__radd__(self, other)`
**Description:** Defines behavior for reflected addition (when the left operand doesn't support addition).  
**Use case:** Handle addition when your object is on the right side.
```python
class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __radd__(self, other):
        if other == 0:  # For sum() function compatibility
            return self
        return NotImplemented
    
    def __str__(self):
        return f"Vector({self.x}, {self.y})"

vectors = [Vector(1, 2), Vector(3, 4)]
print(sum(vectors))  # Output: Vector(4, 6)
```

### Other arithmetic methods
- `__sub__(self, other)` and `__rsub__(self, other)`: Subtraction (`-`)
- `__mul__(self, other)` and `__rmul__(self, other)`: Multiplication (`*`)
- `__truediv__(self, other)` and `__rtruediv__(self, other)`: Division (`/`)
- `__floordiv__(self, other)` and `__rfloordiv__(self, other)`: Floor division (`//`)
- `__mod__(self, other)` and `__rmod__(self, other)`: Modulo (`%`)
- `__pow__(self, other)` and `__rpow__(self, other)`: Power (`**`)

## Container Methods

### `__len__(self)`
**Description:** Returns the length of the container.  
**Use case:** Make an object compatible with the `len()` function.
```python
class Deck:
    def __init__(self):
        self.cards = [i for i in range(52)]
    
    def __len__(self):
        return len(self.cards)

deck = Deck()
print(len(deck))  # Output: 52
```

### `__getitem__(self, key)`
**Description:** Defines behavior for accessing elements with `object[key]`.  
**Use case:** Allow indexing or key-based access to your object.
```python
class Deck:
    def __init__(self):
        self.cards = [i for i in range(52)]
    
    def __getitem__(self, position):
        return self.cards[position]

deck = Deck()
print(deck[0])      # Output: 0
print(deck[10:15])  # Output: [10, 11, 12, 13, 14]
```

### `__setitem__(self, key, value)`
**Description:** Defines behavior for setting values with `object[key] = value`.  
**Use case:** Allow modification of elements in your object.
```python
class Deck:
    def __init__(self):
        self.cards = [i for i in range(52)]
    
    def __setitem__(self, position, card):
        self.cards[position] = card

deck = Deck()
deck[0] = 100
print(deck[0])  # Output: 100
```

### `__contains__(self, item)`
**Description:** Defines behavior for the `in` operator.  
**Use case:** Check if an item exists in your container.
```python
class Deck:
    def __init__(self):
        self.cards = [i for i in range(52)]
    
    def __contains__(self, card):
        return card in self.cards

deck = Deck()
print(51 in deck)  # Output: True
print(100 in deck)  # Output: False
```

### `__iter__(self)`
**Description:** Returns an iterator for the container.  
**Use case:** Make your object iterable in for loops.
```python
class Deck:
    def __init__(self):
        self.cards = [i for i in range(52)]
    
    def __iter__(self):
        return iter(self.cards)

deck = Deck()
for card in deck:
    if card < 3:
        print(card)  # Output: 0, 1, 2
```

## Attribute Access

### `__getattr__(self, name)`
**Description:** Called when an attribute access fails.  
**Use case:** Handle undefined attributes or provide dynamic attributes.
```python
class Person:
    def __init__(self, name):
        self.name = name
    
    def __getattr__(self, attr):
        return f"No attribute named {attr}"

person = Person("Alice")
print(person.name)      # Output: Alice
print(person.undefined)  # Output: No attribute named undefined
```

### `__setattr__(self, name, value)`
**Description:** Called when setting an attribute.  
**Use case:** Validate or transform attribute values before assigning them.
```python
class Person:
    def __setattr__(self, name, value):
        if name == "age" and value < 0:
            value = 0
        super().__setattr__(name, value)

person = Person()
person.age = -5
print(person.age)  # Output: 0
```

### `__delattr__(self, name)`
**Description:** Called when deleting an attribute.  
**Use case:** Custom behavior when attributes are deleted.
```python
class ProtectedAttrs:
    def __init__(self):
        self.regular = "Can delete"
        self.protected = "Can't delete"
    
    def __delattr__(self, name):
        if name == "protected":
            print("Cannot delete protected attribute")
        else:
            super().__delattr__(name)

obj = ProtectedAttrs()
del obj.regular    # Deletes regular
del obj.protected  # Prints: Cannot delete protected attribute
```

## Callable Objects

### `__call__(self, [args...])`
**Description:** Makes the object callable like a function.  
**Use case:** Create function-like objects or implement callback functionality.
```python
class Multiplier:
    def __init__(self, factor):
        self.factor = factor
    
    def __call__(self, x):
        return x * self.factor

double = Multiplier(2)
print(double(5))  # Output: 10
```

## Context Managers

### `__enter__(self)`
**Description:** Called at the start of a with-statement block.  
**Use case:** Set up resources or a specific environment.
```python
class TempDir:
    def __enter__(self):
        import tempfile
        self.temp_dir = tempfile.TemporaryDirectory()
        return self.temp_dir.name
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.temp_dir.cleanup()

with TempDir() as dir_path:
    print(f"Working in {dir_path}")
# Directory is automatically cleaned up after the block
```

### `__exit__(self, exc_type, exc_val, exc_tb)`
**Description:** Called at the end of a with-statement block.  
**Use case:** Clean up resources, handle exceptions.
```python
class FileHandler:
    def __init__(self, filename, mode):
        self.filename = filename
        self.mode = mode
        
    def __enter__(self):
        self.file = open(self.filename, self.mode)
        return self.file
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.file.close()
        
        # Return True to suppress exceptions
        if exc_type is not None:
            print(f"Handled {exc_type} exception")
            return True

with FileHandler("example.txt", "w") as f:
    f.write("Hello, World!")
    # raise ValueError("Test exception")  # Uncomment to test exception handling
```

## Descriptor Methods

### `__get__(self, instance, owner)`
**Description:** Called when the descriptor's attribute is accessed.  
**Use case:** Custom attribute access behaviors.
```python
class Validator:
    def __init__(self, min_value=None, max_value=None):
        self.min_value = min_value
        self.max_value = max_value
        self.name = None
    
    def __set_name__(self, owner, name):
        self.name = name
    
    def __get__(self, instance, owner):
        if instance is None:
            return self
        return instance.__dict__[self.name]
    
    def __set__(self, instance, value):
        if self.min_value is not None and value < self.min_value:
            raise ValueError(f"{self.name} must be >= {self.min_value}")
        if self.max_value is not None and value > self.max_value:
            raise ValueError(f"{self.name} must be <= {self.max_value}")
        instance.__dict__[self.name] = value

class Person:
    age = Validator(min_value=0, max_value=120)
    
    def __init__(self, name, age):
        self.name = name
        self.age = age

# This works
person = Person("Alice", 30)
print(person.age)  # Output: 30

# This raises ValueError
try:
    person = Person("Bob", -5)
except ValueError as e:
    print(e)  # Output: age must be >= 0
```

## Class Customization

### `__new__(cls, [args...])`
**Description:** Called to create a new instance of the class (before `__init__` is called).  
**Use case:** Control instance creation and implement patterns like singletons.
```python
class Singleton:
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

s1 = Singleton()
s2 = Singleton()
print(s1 is s2)  # Output: True
```

### `__init_subclass__(cls, **kwargs)`
**Description:** Called when a class is subclassed.  
**Use case:** Register subclasses, validate subclass implementation.
```python
class Plugin:
    plugins = {}
    
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.plugins[cls.__name__] = cls
    
    @classmethod
    def get_plugins(cls):
        return cls.plugins

class AudioPlugin(Plugin):
    pass

class VideoPlugin(Plugin):
    pass

print(Plugin.get_plugins())  # Output: {'AudioPlugin': <class 'AudioPlugin'>, 'VideoPlugin': <class 'VideoPlugin'>}
```


I've created a comprehensive overview and cheatsheet for Python dunder methods. The cheatsheet is organized by categories and includes:

- Detailed descriptions of what each method does
- Common use cases for each method
- Practical code examples that demonstrate implementation
- Expected outputs where relevant

The cheatsheet covers the most important dunder methods across these categories:

1. Initialization and deletion methods
2. String representation methods
3. Comparison operations
4. Mathematical operations
5. Container methods (for sequence and mapping behaviors)
6. Attribute access methods
7. Callable object methods
8. Context manager methods
9. Descriptor methods
10. Class customization methods

Each example demonstrates a practical implementation of the dunder method in a way that shows its functionality. Would you like me to explain any specific category or method in more detail?
