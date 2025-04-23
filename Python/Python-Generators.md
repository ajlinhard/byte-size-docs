# Python Generators: A Simple to Complex Guide

Python generators are a powerful feature that allow you to create iterators in a simple, elegant way. They are memory-efficient for handling large datasets and are perfect for situations where you need to work with data that doesn't need to be fully loaded into memory at once. Let me explain them from simple to complex concepts.

## Basics of Generators

At their core, generators are functions that return an object that can be iterated over. Unlike regular functions that return a value and exit, generators use the `yield` keyword to provide a value and then "pause" their execution state until the next value is requested.

```python
def simple_generator():
    yield 1
    yield 2
    yield 3

# Using the generator
gen = simple_generator()
print(next(gen))  # 1
print(next(gen))  # 2
print(next(gen))  # 3
# print(next(gen))  # StopIteration error
```

You can also use generators in for loops:

```python
for value in simple_generator():
    print(value)  # Prints 1, 2, 3
```

## Generator Expressions

Similar to list comprehensions, generator expressions create generators on the fly:

```python
squares = (x*x for x in range(5))
# This doesn't compute all values immediately like a list comprehension would
# Instead, it generates values one at a time when needed
```

## Creating More Complex Generators

Generators can include logic, loops, and conditions:

```python
def fibonacci(limit):
    a, b = 0, 1
    while a < limit:
        yield a
        a, b = b, a + b

for num in fibonacci(100):
    print(num)  # 0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89
```

## Creating a Generator Class

Now let's look at how to implement generators within a class. There are two main approaches:

### 1. Using a Generator Method in a Class

```python
class NumberSequence:
    def __init__(self, start, end):
        self.start = start
        self.end = end
        
    def generate(self):
        # This is a generator method
        current = self.start
        while current <= self.end:
            yield current
            current += 1

# Usage
seq = NumberSequence(1, 5)
for num in seq.generate():
    print(num)  # 1, 2, 3, 4, 5
```

### 2. Making the Class Itself Iterable with a Generator

To make your class directly iterable using a generator, implement the `__iter__` method as a generator:

```python
class CountDown:
    def __init__(self, start):
        self.start = start
        
    def __iter__(self):
        # This makes the class itself iterable
        count = self.start
        while count > 0:
            yield count
            count -= 1

# Usage
for num in CountDown(5):
    print(num)  # 5, 4, 3, 2, 1
```

## Advanced Generator Techniques

### 1. Generator delegation with `yield from`

The `yield from` syntax delegates part of a generator's operations to another generator:

```python
def subgenerator(n):
    for i in range(n):
        yield i

def delegating_generator():
    yield from subgenerator(3)  # Yields 0, 1, 2
    yield from subgenerator(2)  # Yields 0, 1

for item in delegating_generator():
    print(item)  # 0, 1, 2, 0, 1
```

### 2. Bidirectional communication with generators using `.send()`

Generators can receive values from the caller using `.send()`:

```python
def echo_generator():
    value = yield "Ready"
    while True:
        value = yield f"Echo: {value}"

gen = echo_generator()
print(next(gen))  # "Ready" (must prime the generator first)
print(gen.send("Hello"))  # "Echo: Hello"
print(gen.send("World"))  # "Echo: World"
```

### 3. Generator with state tracking

```python
def stateful_generator():
    state = {"count": 0}
    
    while True:
        received = yield f"Current count: {state['count']}"
        
        if received == "increment":
            state["count"] += 1
        elif received == "reset":
            state["count"] = 0
        elif received == "exit":
            break

gen = stateful_generator()
print(next(gen))  # Prime the generator
print(gen.send("increment"))
print(gen.send("increment"))
print(gen.send("reset"))
```

### 4. Creating a Customizable Generator Class

Here's a more comprehensive generator class that demonstrates several advanced techniques:

```python
class CustomSequence:
    def __init__(self, start, end=None, step=1, transform_func=None):
        self.start = start
        self.end = end
        self.step = step
        self.transform = transform_func or (lambda x: x)
        
    def __iter__(self):
        current = self.start
        
        # Handle infinite sequences if end is None
        while self.end is None or current <= self.end:
            # Apply custom transformation before yielding
            yield self.transform(current)
            current += self.step
            
            # Safety check for infinite sequences
            if self.end is None and current > 10000:
                raise StopIteration("Safety limit reached")
    
    def filtered(self, filter_func):
        """Return a new generator with filtered values"""
        for value in self:
            if filter_func(value):
                yield value
                
    def map(self, map_func):
        """Return a new generator with transformed values"""
        for value in self:
            yield map_func(value)

# Example usage:
# Create a sequence of squares from 1 to 10
squares = CustomSequence(1, 10, transform_func=lambda x: x*x)

# Filter for only even squares
even_squares = squares.filtered(lambda x: x % 2 == 0)

# Get the square roots of the even squares
roots = even_squares.map(lambda x: x ** 0.5)

for item in roots:
    print(item)  # 2.0, 4.0, 6.0, 8.0, 10.0
```

This last example combines multiple concepts to create a flexible, composable generator class that can be customized in various ways.
