# Python Design Patterns in Detail
### Table of Contents

### Abstract Class
- [Structure of Abstract Classes](#structure-of-abstract-classes)
- [Use Cases for Abstract Classes](#use-cases-for-abstract-classes)
- [Behaviors and Key Points](#behaviors-and-key-points)
- [Examples](#examples)

### Singleton Pattern
- [High-Level Explanation](#high-level-explanation)
- [Use Cases](#use-cases)
- [Code Example](#code-example)
- [Common Misconceptions/Misuses](#common-misconceptionsmisuses)

### Factory Pattern
- [High-Level Explanation](#high-level-explanation-1)
- [Use Cases](#use-cases-1)
- [Code Examples](#code-examples)
- [Common Misconceptions/Misuses](#common-misconceptionsmisuses-1)

### Observer Pattern
- [High-Level Explanation](#high-level-explanation-2)
- [Use Cases](#use-cases-2)
- [Code Examples](#code-examples-1)
- [Common Misconceptions/Misuses](#common-misconceptionsmisuses-2)

### Builder Pattern
- [High-Level Explanation](#high-level-explanation-3)
- [Use Cases](#use-cases-3)
- [Code Examples](#code-examples-2)
- [Common Misconceptions/Misuses](#common-misconceptionsmisuses-3)

---
## Abstract Class
---
Abstract classes in Python serve as blueprints for other classes, enforcing a contract that subclasses must fulfill. Let me break this down for you:

## Structure of Abstract Classes
1. **Import Requirements**:
   ```python
   from abc import ABC, abstractmethod
   ```

2. **Basic Structure**:
   ```python
   class AbstractClass(ABC):
       @abstractmethod
       def required_method(self):
           pass
           
       def regular_method(self):
           return "This is inherited as-is by subclasses"
   ```

3. **Key Components**:
   - Inherit from `ABC` (Abstract Base Class)
   - Use `@abstractmethod` decorator to define methods that must be implemented
   - Can include concrete (implemented) methods
   - Can include an `__init__` method (commonly implemented)

## Use Cases for Abstract Classes

1. **Enforcing Interfaces**: When you need to ensure certain methods exist in all derived classes
   
2. **Template Method Pattern**: Define the skeleton of an algorithm where specific steps are implemented by subclasses
   
3. **Common Behavior Sharing**: Provide common functionality while requiring specific implementations
   
4. **Design Patterns Implementation**:
   - Repository pattern (data access)
   - Factory pattern (object creation)
   - Strategy pattern (algorithm selection)

5. **Framework Development**: Creating extensible frameworks where users implement specific functionality

## Behaviors and Key Points

1. **Cannot Be Instantiated**: Abstract classes cannot be directly instantiated
   ```python
   # This will raise TypeError
   shape = Shape()
   ```

2. **All Abstract Methods Must Be Implemented**: Subclasses must implement all abstract methods to be instantiable

3. **Can Have Default Implementations**: Abstract methods can provide default behavior that subclasses can leverage with `super()`

4. **Can Have Constructor**: Often includes an `__init__` method that subclasses call with `super().__init__(...)`

5. **Mixing Abstract and Concrete Methods**: Allows a blend of required and provided behavior

6. **Method Resolution Order**: Follow Python's MRO for method inheritance and overriding

## Examples

I've created an artifact with comprehensive examples that showcase:

1. Basic shape hierarchy (Circle, Rectangle inheriting from Shape)
2. Repository pattern implementation (JSON file storage)
3. Abstract class with default implementations
4. Abstract Factory pattern

The code demonstrates different approaches to using abstract classes and how they enforce interfaces while providing shared functionality.

---
## Singleton Pattern
---

### High-Level Explanation
The Singleton pattern ensures that a class has only one instance throughout the application's lifecycle and provides a global point of access to it. This pattern restricts instantiation of a class to a single object, which can be particularly useful for coordinating actions across your system.

### Use Cases
- Database connection managers (to avoid opening multiple connections)
- Configuration managers (to ensure consistent settings throughout the app)
- Logger classes (to maintain a single log file handler)
- Hardware interface access (like printer spoolers)
- Cache implementations (to maintain a single shared cache)

### Code Example

```python
class Singleton:
    # Class variable to store the single instance
    _instance = None
    
    # Using __new__ to control instance creation
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            # Create the only instance
            cls._instance = super().__new__(cls)
            # Initialize here if needed
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, value=None):
        # Ensure initialization happens only once
        if not self._initialized:
            self.value = value
            self._initialized = True
    
    def get_value(self):
        return self.value
    
    def set_value(self, value):
        self.value = value

# Usage demonstration
singleton1 = Singleton("First")
singleton2 = Singleton("Second")  # This won't create a new instance

print(singleton1 is singleton2)  # True
print(singleton1.get_value())    # "First" (not "Second")
singleton2.set_value("Updated")
print(singleton1.get_value())    # "Updated" (both references point to same object)
```

Another common implementation using a metaclass:

```python
class SingletonMeta(type):
    _instances = {}
    
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class ConfigManager(metaclass=SingletonMeta):
    def __init__(self):
        self.settings = {}
        self.load_config()
    
    def load_config(self):
        # In reality, would load from file or environment
        self.settings = {
            'debug': True,
            'api_key': 'secret_key',
            'max_connections': 100
        }
    
    def get_setting(self, key):
        return self.settings.get(key)

# Both instances are the same
config1 = ConfigManager()
config2 = ConfigManager()
print(config1 is config2)  # True
```
The metaclass part of this singleton implementation involves Python's metaclass machinery to control class instantiation. Let me break it down:

1. **`SingletonMeta(type)`**: This defines a metaclass that inherits from `type`. In Python, `type` is itself a class and is the default metaclass for all classes. By inheriting from `type`, `SingletonMeta` becomes a metaclass.

2. **`_instances = {}`**: This class variable stores the singleton instances, with class objects as keys and their unique instances as values.

3. **`__call__(cls, *args, **kwargs)`**: This is where the magic happens. When you call a class to create an instance (like `ConfigManager()`), Python actually calls the `__call__` method of the class's metaclass.

   - The `cls` parameter represents the class being instantiated (e.g., `ConfigManager`)
   - If the class isn't already in `_instances`, it creates a new instance by calling `super().__call__(*args, **kwargs)`, which invokes the standard instance creation process
   - If the class is already in `_instances`, it returns the existing instance
   - This ensures only one instance of each class using this metaclass will ever exist

4. **`class ConfigManager(metaclass=SingletonMeta)`**: This line specifies that `ConfigManager` uses `SingletonMeta` as its metaclass instead of the default `type`. As a result, whenever code tries to instantiate `ConfigManager`, the `__call__` method of `SingletonMeta` controls the instantiation process.

The beauty of this approach is that the singleton behavior is completely encapsulated in the metaclass. Any class can become a singleton simply by specifying `metaclass=SingletonMeta`, without changing any of its internal implementation. This creates a clean separation between the singleton behavior and the actual functionality of the class.

### Common Misconceptions/Misuses

- **Misconception**: Singletons are just global variables with extra steps.
  - **Reality**: Unlike global variables, Singletons provide controlled access, lazy initialization, and can ensure proper instantiation order.

- **Misuse**: Overusing the Singleton pattern.
  - Singletons can make testing difficult because they maintain state across tests. They also introduce global state, which can lead to unexpected dependencies.

- **Misconception**: All Singleton implementations are thread-safe.
  - Basic implementations may have race conditions. Thread safety needs to be explicitly addressed:

```python
import threading

class ThreadSafeSingleton:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
        return cls._instance
```

- **Misuse**: Using Singletons where dependency injection would be more appropriate.
  - Dependency injection often leads to more maintainable and testable code.

---
## Factory Pattern
---

### High-Level Explanation
The Factory pattern provides an interface for creating objects without specifying their concrete classes. It encapsulates object creation logic, allowing you to create objects based on certain conditions without exposing the instantiation logic to the client.

### Use Cases
- When a class can't anticipate what kind of objects it needs to create
- When you want to centralize complex object creation logic
- When you need to create objects from a family of related classes based on conditions
- Creating objects in frameworks where components are registered at runtime
- Decoupling object creation from the system that uses the objects

### Code Examples

Simple Factory (not a full design pattern, but a common technique):

```python
class Animal:
    def speak(self):
        pass

class Dog(Animal):
    def speak(self):
        return "Woof!"

class Cat(Animal):
    def speak(self):
        return "Meow!"

class AnimalFactory:
    def create_animal(self, animal_type):
        if animal_type == "dog":
            return Dog()
        elif animal_type == "cat":
            return Cat()
        else:
            raise ValueError(f"Unknown animal type: {animal_type}")

# Usage
factory = AnimalFactory()
dog = factory.create_animal("dog")
cat = factory.create_animal("cat")

print(dog.speak())  # "Woof!"
print(cat.speak())  # "Meow!"
```

Factory Method Pattern (more formal implementation):

```python
from abc import ABC, abstractmethod

# Abstract creator
class LoggerFactory(ABC):
    @abstractmethod
    def create_logger(self):
        pass
    
    def log(self, message):
        # Factory Method is used here
        logger = self.create_logger()
        logger.log(message)

# Concrete creators
class FileLoggerFactory(LoggerFactory):
    def create_logger(self):
        return FileLogger()

class ConsoleLoggerFactory(LoggerFactory):
    def create_logger(self):
        return ConsoleLogger()

# Abstract product
class Logger(ABC):
    @abstractmethod
    def log(self, message):
        pass

# Concrete products
class FileLogger(Logger):
    def log(self, message):
        print(f"File: {message}")

class ConsoleLogger(Logger):
    def log(self, message):
        print(f"Console: {message}")

# Client code
def client_code(factory):
    factory.log("Important information")

# Usage
client_code(FileLoggerFactory())    # "File: Important information"
client_code(ConsoleLoggerFactory()) # "Console: Important information"
```

Abstract Factory Pattern (for families of related objects):

```python
from abc import ABC, abstractmethod

# Abstract products
class Button(ABC):
    @abstractmethod
    def render(self):
        pass

class Checkbox(ABC):
    @abstractmethod
    def render(self):
        pass

# Concrete products - Light theme
class LightButton(Button):
    def render(self):
        return "Rendering light button"

class LightCheckbox(Checkbox):
    def render(self):
        return "Rendering light checkbox"

# Concrete products - Dark theme
class DarkButton(Button):
    def render(self):
        return "Rendering dark button"

class DarkCheckbox(Checkbox):
    def render(self):
        return "Rendering dark checkbox"

# Abstract factory
class UIFactory(ABC):
    @abstractmethod
    def create_button(self):
        pass
    
    @abstractmethod
    def create_checkbox(self):
        pass

# Concrete factories
class LightThemeFactory(UIFactory):
    def create_button(self):
        return LightButton()
    
    def create_checkbox(self):
        return LightCheckbox()

class DarkThemeFactory(UIFactory):
    def create_button(self):
        return DarkButton()
    
    def create_checkbox(self):
        return DarkCheckbox()

# Client code
def create_ui(factory):
    button = factory.create_button()
    checkbox = factory.create_checkbox()
    
    return {
        "button": button.render(),
        "checkbox": checkbox.render()
    }

# Usage based on user preference
user_theme = "dark"  # This could come from user settings

if user_theme == "light":
    factory = LightThemeFactory()
else:
    factory = DarkThemeFactory()

ui_elements = create_ui(factory)
print(ui_elements)  # Dictionary with rendered UI elements
```

### Common Misconceptions/Misuses

- **Misconception**: Factory patterns are always overly complex for simple object creation.
  - **Reality**: There's a spectrum of factory implementations, from simple factory methods to abstract factories. Choose based on your needs.

- **Misuse**: Creating factories for everything, even when direct instantiation would be simpler.
  - The pattern adds value when there's complexity in object creation or you need to hide implementation details.

- **Misconception**: Factory patterns require interfaces or abstract classes.
  - While common in many languages, Python's duck typing means you can create factory patterns without formal interfaces.

- **Misuse**: Not considering other creational patterns that might be more suitable.
  - Sometimes Builder, Prototype, or even just simple constructors might be more appropriate.
 
### Similar to Factory Patterns
This example is mainly focused around the precise subclass to use in an inheritance tree, where inputs determine best class to use.
In Python, there are several patterns to determine which class in an inheritance tree to instantiate based on input parameters. Here are the most effective approaches:

### Factory Method Pattern

A class method that decides which subclass to instantiate:

```python
class Animal:
    @classmethod
    def create(cls, animal_type, *args, **kwargs):
        if animal_type == "dog":
            return Dog(*args, **kwargs)
        elif animal_type == "cat":
            return Cat(*args, **kwargs)
        else:
            return cls(*args, **kwargs)  # Default to base class

class Dog(Animal):
    def __init__(self, name, breed):
        self.name = name
        self.breed = breed

class Cat(Animal):
    def __init__(self, name, color):
        self.name = name
        self.color = color

# Usage
pet = Animal.create("dog", "Rex", "German Shepherd")
```

### Registry Pattern

More scalable approach using class registration:

```python
class AnimalRegistry:
    _registry = {}
    
    @classmethod
    def register(cls, animal_type):
        def decorator(subclass):
            cls._registry[animal_type] = subclass
            return subclass
        return decorator
    
    @classmethod
    def create(cls, animal_type, *args, **kwargs):
        if animal_type in cls._registry:
            return cls._registry[animal_type](*args, **kwargs)
        raise ValueError(f"Unknown animal type: {animal_type}")

@AnimalRegistry.register("dog")
class Dog:
    def __init__(self, name, breed):
        self.name = name
        self.breed = breed

@AnimalRegistry.register("cat")
class Cat:
    def __init__(self, name, color):
        self.name = name
        self.color = color

# Usage
pet = AnimalRegistry.create("dog", "Rex", "German Shepherd")
```

### Class Hierarchy Inspection

For more complex logic based on multiple parameters:

```python
class Shape:
    @classmethod
    def create(cls, dimensions, *args, **kwargs):
        subclasses = cls.__subclasses__()
        for subclass in subclasses:
            if hasattr(subclass, 'supports_dimensions') and subclass.supports_dimensions(dimensions):
                return subclass(*args, **kwargs)
        return cls(*args, **kwargs)  # Default

class TwoDimensional(Shape):
    @classmethod
    def supports_dimensions(cls, dimensions):
        return dimensions == 2

class ThreeDimensional(Shape):
    @classmethod
    def supports_dimensions(cls, dimensions):
        return dimensions == 3
```

The registry pattern is generally the most maintainable for complex hierarchies as it decouples the factory logic from the class definitions and scales well as you add more subclasses.

---
## Observer Pattern
---

### High-Level Explanation
The Observer pattern defines a one-to-many dependency between objects, where when one object (the subject) changes state, all its dependents (observers) are notified and updated automatically. This promotes loose coupling between the subject and its observers.

### Use Cases
- Event handling systems
- Implementing distributed event handling systems in distributed systems
- MVC (Model-View-Controller) architecture, where the model notifies views of changes
- Subscription services (like newsletters or notifications)
- GUI components that need to be updated when data changes
- Real-time data monitoring and dashboards

### Code Examples

Basic implementation:

```python
from abc import ABC, abstractmethod
from typing import List

# Subject interface
class Subject(ABC):
    @abstractmethod
    def attach(self, observer):
        pass
    
    @abstractmethod
    def detach(self, observer):
        pass
    
    @abstractmethod
    def notify(self):
        pass

# Observer interface
class Observer(ABC):
    @abstractmethod
    def update(self, subject):
        pass

# Concrete Subject
class WeatherStation(Subject):
    def __init__(self):
        self._observers: List[Observer] = []
        self._temperature = 0
    
    def attach(self, observer):
        if observer not in self._observers:
            self._observers.append(observer)
    
    def detach(self, observer):
        self._observers.remove(observer)
    
    def notify(self):
        for observer in self._observers:
            observer.update(self)
    
    def set_temperature(self, temperature):
        self._temperature = temperature
        self.notify()  # Notify observers when temperature changes
    
    @property
    def temperature(self):
        return self._temperature

# Concrete Observers
class TemperatureDisplay(Observer):
    def update(self, subject):
        print(f"Temperature Display: {subject.temperature}°C")

class PhoneApp(Observer):
    def update(self, subject):
        if subject.temperature > 30:
            print(f"Phone App Alert: High temperature - {subject.temperature}°C!")
        else:
            print(f"Phone App: Current temperature is {subject.temperature}°C")

# Usage
weather_station = WeatherStation()

# Create and register observers
display = TemperatureDisplay()
app = PhoneApp()

weather_station.attach(display)
weather_station.attach(app)

# Change the temperature
weather_station.set_temperature(25)  # Both observers will be notified

# Change again with a higher temperature
weather_station.set_temperature(32)  # Both get notified, but PhoneApp shows an alert

# Remove an observer
weather_station.detach(display)

# Only the app gets notified now
weather_station.set_temperature(28)
```

Using Python's built-in observer pattern with `Observable` (removed in Python 3, but shown for conceptual understanding):

```python
class Observable:
    def __init__(self):
        self._observers = []
    
    def add_observer(self, observer):
        if observer not in self._observers:
            self._observers.append(observer)
    
    def remove_observer(self, observer):
        try:
            self._observers.remove(observer)
        except ValueError:
            pass
    
    def notify_observers(self, *args, **kwargs):
        for observer in self._observers:
            observer(self, *args, **kwargs)

# Using with function callbacks
class StockMarket(Observable):
    def __init__(self):
        super().__init__()
        self._price = 0
    
    @property
    def price(self):
        return self._price
    
    @price.setter
    def price(self, new_price):
        self._price = new_price
        self.notify_observers(price=new_price)

# Observer functions
def price_alert(observable, **kwargs):
    price = kwargs.get('price', 0)
    print(f"Alert: Stock price changed to ${price}")

def log_price(observable, **kwargs):
    price = kwargs.get('price', 0)
    print(f"Logging: Stock price is ${price}")

# Usage
market = StockMarket()
market.add_observer(price_alert)
market.add_observer(log_price)

market.price = 101.23  # Both observer functions are called
market.price = 98.75   # Both are called again
```

### Common Misconceptions/Misuses

- **Misconception**: Observer pattern is only for GUI programming.
  - While common in UI frameworks, it's useful in any situation requiring event notification.

- **Misuse**: Creating tight coupling between observers and subjects.
  - Observers should ideally know about subject interfaces, not concrete implementations.

- **Misconception**: Performance isn't affected by the number of observers.
  - Having too many observers can cause performance issues, especially if update operations are costly.

- **Misuse**: Not properly managing observer lifecycles.
  - Failing to detach observers can lead to memory leaks or unexpected behavior:

```python
# Example of memory leak prevention
import weakref

class Subject:
    def __init__(self):
        # Using weak references to avoid memory leaks
        self._observers = weakref.WeakSet()
    
    def attach(self, observer):
        self._observers.add(observer)
    
    # No need for explicit detach method as weak references will
    # allow observers to be garbage collected when no longer used
```

## Builder Pattern

### High-Level Explanation
The Builder pattern separates the construction of a complex object from its representation, allowing the same construction process to create different representations. It helps when an object requires many optional parameters or when the construction involves multiple steps.

### Use Cases
- Creating objects with many optional parameters (avoiding "telescoping constructors")
- When object construction involves multiple steps that should be executed in a specific order
- When different representations of an object can be built using the same construction process
- To encapsulate complex object creation logic
- When immutable objects need multiple parameters

### Code Examples

Basic Builder Pattern:

```python
class House:
    def __init__(self):
        self.foundation = None
        self.structure = None
        self.roof = None
        self.interior = None
    
    def __str__(self):
        return f"House with {self.foundation} foundation, {self.structure} structure, {self.roof} roof, and {self.interior} interior."

class HouseBuilder:
    def __init__(self):
        self.house = House()
    
    def build_foundation(self, foundation_type):
        self.house.foundation = foundation_type
        return self
    
    def build_structure(self, structure_type):
        self.house.structure = structure_type
        return self
    
    def build_roof(self, roof_type):
        self.house.roof = roof_type
        return self
    
    def build_interior(self, interior_type):
        self.house.interior = interior_type
        return self
    
    def get_house(self):
        return self.house

# Client code
builder = HouseBuilder()
house = builder.build_foundation("concrete") \
               .build_structure("brick") \
               .build_roof("tile") \
               .build_interior("modern") \
               .get_house()

print(house)  # "House with concrete foundation, brick structure, tile roof, and modern interior."
```

Builder with Director (separating construction logic from client):

```python
from abc import ABC, abstractmethod

# Product
class Pizza:
    def __init__(self):
        self.dough = None
        self.sauce = None
        self.toppings = []
    
    def __str__(self):
        toppings_str = ", ".join(self.toppings) if self.toppings else "no toppings"
        return f"Pizza with {self.dough} dough, {self.sauce} sauce, and {toppings_str}."

# Abstract Builder
class PizzaBuilder(ABC):
    @abstractmethod
    def reset(self):
        pass
    
    @abstractmethod
    def build_dough(self):
        pass
    
    @abstractmethod
    def build_sauce(self):
        pass
    
    @abstractmethod
    def build_toppings(self):
        pass
    
    @abstractmethod
    def get_pizza(self):
        pass

# Concrete Builder
class MargheritaPizzaBuilder(PizzaBuilder):
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.pizza = Pizza()
    
    def build_dough(self):
        self.pizza.dough = "thin"
    
    def build_sauce(self):
        self.pizza.sauce = "tomato"
    
    def build_toppings(self):
        self.pizza.toppings = ["mozzarella", "basil"]
    
    def get_pizza(self):
        pizza = self.pizza
        self.reset()
        return pizza

class PepperoniPizzaBuilder(PizzaBuilder):
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.pizza = Pizza()
    
    def build_dough(self):
        self.pizza.dough = "thick"
    
    def build_sauce(self):
        self.pizza.sauce = "spicy tomato"
    
    def build_toppings(self):
        self.pizza.toppings = ["mozzarella", "pepperoni"]
    
    def get_pizza(self):
        pizza = self.pizza
        self.reset()
        return pizza

# Director
class PizzaDirector:
    def __init__(self, builder):
        self.builder = builder
    
    def change_builder(self, builder):
        self.builder = builder
    
    def make_pizza(self):
        self.builder.build_dough()
        self.builder.build_sauce()
        self.builder.build_toppings()
    
    # Could also have more specific methods like make_pizza_no_sauce()

# Usage
margherita_builder = MargheritaPizzaBuilder()
pepperoni_builder = PepperoniPizzaBuilder()

director = PizzaDirector(margherita_builder)
director.make_pizza()
margherita = margherita_builder.get_pizza()

director.change_builder(pepperoni_builder)
director.make_pizza()
pepperoni = pepperoni_builder.get_pizza()

print(margherita)  # "Pizza with thin dough, tomato sauce, and mozzarella, basil."
print(pepperoni)   # "Pizza with thick dough, spicy tomato sauce, and mozzarella, pepperoni."
```

Fluent Builder (method chaining) for immutable objects:

```python
class User:
    def __init__(self, name, age=None, email=None, address=None, phone=None):
        self.name = name
        self.age = age
        self.email = email
        self.address = address
        self.phone = phone
    
    def __str__(self):
        return f"User(name={self.name}, age={self.age}, email={self.email}, address={self.address}, phone={self.phone})"

class UserBuilder:
    def __init__(self, name):
        self.name = name
        self.age = None
        self.email = None
        self.address = None
        self.phone = None
    
    def with_age(self, age):
        self.age = age
        return self
    
    def with_email(self, email):
        self.email = email
        return self
    
    def with_address(self, address):
        self.address = address
        return self
    
    def with_phone(self, phone):
        self.phone = phone
        return self
    
    def build(self):
        # Create an immutable User instance
        return User(
            name=self.name,
            age=self.age,
            email=self.email,
            address=self.address,
            phone=self.phone
        )

# Usage - only specify what you need
minimal_user = UserBuilder("John").build()
print(minimal_user)  # User with only name set

detailed_user = UserBuilder("Jane") \
                .with_age(30) \
                .with_email("jane@example.com") \
                .with_phone("555-1234") \
                .build()
print(detailed_user)  # User with multiple fields set
```

### Common Misconceptions/Misuses

- **Misconception**: Builder is only useful for complex objects with many parameters.
  - While that's a common use case, it's also valuable for enforcing construction steps or creating different representations.

- **Misuse**: Creating builders for simple objects where a constructor with default arguments would suffice.
  - The pattern adds complexity, so it should provide clear benefits over simpler approaches.

- **Misconception**: Builders and factory patterns serve the same purpose.
  - Factories focus on what to create, while builders focus on how to create step by step.

- **Misuse**: Not making the builder methods return `self` for method chaining.
  - This breaks the fluent interface that makes builders convenient to use.

- **Misconception**: Every builder needs a director.
  - Directors are optional and are most useful when you have multiple complex construction sequences to reuse.

Each of these design patterns addresses specific problems in software design and provides structured solutions that encourage good practices like loose coupling, separation of concerns, and code reuse. The key is choosing the right pattern for your specific problem and applying it appropriately.
