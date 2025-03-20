# Python Lambda Functions: Cheat Sheet & Walkthrough

## Quick Reference

| Concept | Syntax | Example | Equivalent Function |
|---------|--------|---------|---------------------|
| Basic Lambda | `lambda args: expression` | `lambda x: x * 2` | `def func(x): return x * 2` |
| Multiple Args | `lambda x, y: expression` | `lambda x, y: x + y` | `def func(x, y): return x + y` |
| With `map()` | `map(lambda x: expr, iterable)` | `map(lambda x: x**2, [1, 2, 3])` | Returns: `[1, 4, 9]` |
| With `filter()` | `filter(lambda x: condition, iterable)` | `filter(lambda x: x > 5, [3, 8, 2, 7])` | Returns: `[8, 7]` |
| With `sorted()` | `sorted(iterable, key=lambda x: expr)` | `sorted(data, key=lambda x: x['name'])` | Sorts by specified key |
| With `reduce()` | `reduce(lambda x, y: expr, iterable)` | `reduce(lambda x, y: x * y, [1, 2, 3, 4])` | Returns: `24` |
| Conditional | `lambda x: a if condition else b` | `lambda x: "even" if x % 2 == 0 else "odd"` | Returns "even" or "odd" |

## What Are Lambda Functions?

Lambda functions are small, anonymous functions defined using the `lambda` keyword instead of the standard `def` statement. They are limited to a single expression and automatically return the result of that expression.

## Detailed Walkthrough

### 1. Basic Syntax

```python
lambda arguments: expression
```

- **arguments**: Variables that are passed to the function (comma-separated)
- **expression**: A single expression that's evaluated and returned

### 2. Simple Examples

```python
# A lambda that doubles a number
double = lambda x: x * 2
print(double(5))  # Output: 10

# A lambda that adds two numbers
add = lambda x, y: x + y
print(add(3, 4))  # Output: 7

# A lambda with no arguments
greeting = lambda: "Hello World"
print(greeting())  # Output: Hello World
```

### 3. When to Use Lambda Functions

Lambda functions shine in scenarios where:
- You need a simple function for a short period
- You're passing a function as an argument
- You want to define a function inline without naming it

### 4. Lambda with Built-in Functions

#### map()

`map()` applies a function to each item in an iterable:

```python
# Square each number in a list
numbers = [1, 2, 3, 4, 5]
squared = list(map(lambda x: x**2, numbers))
print(squared)  # Output: [1, 4, 9, 16, 25]

# Convert temperatures from Celsius to Fahrenheit
celsius = [0, 10, 20, 30, 40]
fahrenheit = list(map(lambda c: (c * 9/5) + 32, celsius))
print(fahrenheit)  # Output: [32.0, 50.0, 68.0, 86.0, 104.0]
```

#### filter()

`filter()` creates a new iterable with elements that satisfy a condition:

```python
# Get only even numbers
numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
evens = list(filter(lambda x: x % 2 == 0, numbers))
print(evens)  # Output: [2, 4, 6, 8, 10]

# Filter names that start with 'A'
names = ["Alice", "Bob", "Anna", "Charlie", "Andrew"]
a_names = list(filter(lambda name: name.startswith('A'), names))
print(a_names)  # Output: ['Alice', 'Anna', 'Andrew']
```

#### sorted()

`sorted()` with lambda allows sorting by custom criteria:

```python
# Sort strings by length
words = ["python", "is", "awesome", "and", "powerful"]
sorted_words = sorted(words, key=lambda x: len(x))
print(sorted_words)  # Output: ['is', 'and', 'python', 'awesome', 'powerful']

# Sort dictionaries by a specific key
students = [
    {"name": "Alice", "grade": 88},
    {"name": "Bob", "grade": 75},
    {"name": "Charlie", "grade": 93}
]
sorted_by_grade = sorted(students, key=lambda x: x["grade"], reverse=True)
print(sorted_by_grade)  # Sorted in descending order by grade
```

#### reduce()

`reduce()` from `functools` applies a function cumulatively to all items in an iterable:

```python
from functools import reduce

# Calculate product of all numbers in list
numbers = [1, 2, 3, 4]
product = reduce(lambda x, y: x * y, numbers)
print(product)  # Output: 24 (1*2*3*4)

# Concatenate strings
words = ["Lambda", "functions", "are", "powerful"]
sentence = reduce(lambda x, y: x + " " + y, words)
print(sentence)  # Output: Lambda functions are powerful
```

### 5. Conditional Expressions in Lambda

Lambda functions can include conditional expressions using the ternary operator:

```python
# Check if a number is even or odd
check_even_odd = lambda x: "even" if x % 2 == 0 else "odd"
print(check_even_odd(4))  # Output: even
print(check_even_odd(7))  # Output: odd

# Clamp a value between min and max
clamp = lambda val, min_val, max_val: min_val if val < min_val else max_val if val > max_val else val
print(clamp(15, 0, 10))  # Output: 10
print(clamp(5, 0, 10))   # Output: 5
```

### 6. Limitations

Lambda functions have important limitations:
- Can only contain a single expression (no multiple statements)
- Limited to simple operations (no assignments within the expression)
- No docstrings for documentation
- Generally less readable for complex operations

### 7. Real-World Use Cases

#### GUI Event Handlers

```python
import tkinter as tk

window = tk.Tk()
button = tk.Button(window, text="Click Me", 
                  command=lambda: print("Button clicked!"))
button.pack()
window.mainloop()
```

#### Custom Sorting

```python
# Sort movie data by year, then by rating
movies = [
    {"title": "Inception", "year": 2010, "rating": 8.8},
    {"title": "Interstellar", "year": 2014, "rating": 8.6},
    {"title": "The Dark Knight", "year": 2008, "rating": 9.0},
    {"title": "Dunkirk", "year": 2017, "rating": 7.9},
    {"title": "The Prestige", "year": 2006, "rating": 8.5}
]

# First by year (ascending), then by rating (descending)
sorted_movies = sorted(movies, key=lambda x: (x["year"], -x["rating"]))
```

#### Data Transformation in Pandas

```python
import pandas as pd

df = pd.DataFrame({
    'name': ['Alice', 'Bob', 'Charlie', 'David'],
    'surname': ['Smith', 'Johnson', 'Williams', 'Brown'],
    'age': [25, 30, 35, 40]
})

# Create a new column using lambda
df['full_name'] = df.apply(lambda row: f"{row['name']} {row['surname']}", axis=1)
```

### 8. When NOT to Use Lambdas

Avoid lambdas when:
- The function is complex or performs multiple operations
- The function needs to be reused in multiple places
- You need documentation for the function
- Readability is more important than brevity

### 9. Lambda vs. Regular Functions

| Feature | Lambda | Regular Function |
|---------|--------|------------------|
| Syntax | `lambda args: expression` | `def func(args): return result` |
| Name | Anonymous | Named |
| Length | Single expression | Multiple statements |
| Docstrings | Not allowed | Allowed |
| Return | Implicit | Explicit with `return` |
| Complexity | Limited | Unlimited |
| Readability | Lower for complex operations | Higher for complex operations |

### 10. Best Practices

1. Use lambda functions for simple, short operations
2. Prefer named functions for complex logic
3. Avoid nesting multiple lambda functions
4. Use descriptive parameter names for clarity
5. Consider readability over brevity when in doubt
6. Don't use lambda just to save a line of code
