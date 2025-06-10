# Python Decorators: An Introduction

A decorator in Python is a design pattern that allows you to modify or extend the behavior of functions or classes without permanently changing their code. Think of decorators as "wrappers" that add functionality around your existing functions.

Decorators use Python's `@` syntax and are placed directly above the function they modify. When Python encounters a decorator, it automatically passes the decorated function to the decorator function, which can then add new behavior before, after, or around the original function's execution.

**Common uses for decorators include:**
- Adding logging or timing functionality to functions
- Implementing authentication and authorization checks
- Caching function results for performance
- Validating input parameters
- Handling exceptions or retries
- Adding debugging information

**Basic example:**
```python
@my_decorator
def my_function():
    print("Hello, world!")
```

The beauty of decorators lies in their ability to keep your core business logic clean while layering on cross-cutting concerns like logging, security, or performance monitoring. They promote code reusability by allowing you to apply the same functionality to multiple functions with a simple `@decorator_name` annotation, making your code more modular and easier to maintain.

## How Decorators Work (a breakdown)
**Code:**
```python
def your_decorator(step):
    def decorator(func):
        def wrapper(args,**kwargs):
            # Do stuff before func...
            print(f"Before func aka {step}!") 
            func(args,**kwargs)
            # Do stuff after func...
            print("After func!")
        return wrapper
    return decorator
```
The nested structure of parameterized decorators in Python exists because of how Python's decorator syntax works and the need to create a closure that captures the parameter values. Let me break this down step by step.

## Understanding the Decorator Syntax

When you write:
```python
@your_decorator("step1")
def my_function():
    pass
```

Python interprets this as:
```python
def my_function():
    pass
my_function = your_decorator("step1")(my_function)
```

Notice the **double function call**: `your_decorator("step1")` is called first, then its result is called with `my_function` as an argument.

## Why Three Levels of Nesting?

### Level 1: Parameter Capture
```python
def your_decorator(step):  # <-- This captures the parameter
```
This outermost function receives the decorator's parameter (`step`). Its job is to return the actual decorator function.

### Level 2: The Actual Decorator
```python
def decorator(func):  # <-- This receives the function being decorated
```
This middle function is the "real" decorator that receives the function you're decorating. It returns the wrapper function that will replace the original function.

### Level 3: The Wrapper Function
```python
def wrapper(*args, **kwargs):  # <-- This replaces the original function
```
This innermost function is what actually gets called when someone calls your decorated function. It has access to both the parameter (`step`) and the original function (`func`) through closures.

## How Closures Make This Work

Each nested function has access to variables from its enclosing scope:

```python
def your_decorator(step):
    # 'step' is available here
    
    def decorator(func):
        # Both 'step' and 'func' are available here
        
        def wrapper(*args, **kwargs):
            # 'step', 'func', 'args', and 'kwargs' are all available here
            print(f"Before func aka {step}!")  # Using 'step' from outer scope
            result = func(*args, **kwargs)     # Using 'func' from outer scope
            print("After func!")
            return result
        
        return wrapper
    return decorator
```

## What Happens Step by Step

1. **`@your_decorator("step1")`** calls `your_decorator("step1")`
2. This returns the `decorator` function (with `step="step1"` captured in its closure)
3. **The decorator syntax** then calls `decorator(my_function)`
4. This returns the `wrapper` function (with both `step="step1"` and `func=my_function` captured)
5. **The wrapper replaces the original function**, so `my_function` now points to `wrapper`

## Alternative: Using Classes

You can also implement parameterized decorators using classes, which some find clearer:

```python
class your_decorator:
    def __init__(self, step):
        self.step = step
    
    def __call__(self, func):
        def wrapper(*args, **kwargs):
            print(f"Before func aka {self.step}!")
            result = func(*args, **kwargs)
            print("After func!")
            return result
        return wrapper
```

## Why Not Just Two Levels?

You might wonder why we can't just have:
```python
def your_decorator(step, func):  # This won't work with @ syntax
    def wrapper(*args, **kwargs):
        print(f"Before func aka {step}!")
        result = func(*args, **kwargs)
        print("After func!")
        return result
    return wrapper
```

This won't work with the `@` syntax because the decorator syntax expects a single callable that takes one argument (the function). The three-level structure allows the decorator to be "curried" - first taking the parameters, then taking the function.

The nested structure essentially creates a decorator factory: `your_decorator(step)` creates and returns a decorator that can then be applied to functions.
