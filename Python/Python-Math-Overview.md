# Python Math Functions Cheatsheet

## Quick Reference Table

| Function | Purpose | Example | Result |
|----------|---------|---------|---------|
| `abs(x)` | Absolute value | `abs(-5)` | `5` |
| `round(x, n)` | Round to n decimals | `round(3.14159, 2)` | `3.14` |
| `pow(x, y)` | x raised to power y | `pow(2, 3)` | `8` |
| `min(x, y, ...)` | Minimum value | `min(1, 5, 3)` | `1` |
| `max(x, y, ...)` | Maximum value | `max(1, 5, 3)` | `5` |
| `sum(iterable)` | Sum of sequence | `sum([1, 2, 3])` | `6` |
| `divmod(x, y)` | Quotient and remainder | `divmod(17, 5)` | `(3, 2)` |

### Math Module Functions

| Function | Purpose | Example | Result |
|----------|---------|---------|---------|
| `math.sqrt(x)` | Square root | `math.sqrt(16)` | `4.0` |
| `math.ceil(x)` | Round up | `math.ceil(4.3)` | `5` |
| `math.floor(x)` | Round down | `math.floor(4.8)` | `4` |
| `math.sin(x)` | Sine (radians) | `math.sin(math.pi/2)` | `1.0` |
| `math.cos(x)` | Cosine (radians) | `math.cos(0)` | `1.0` |
| `math.tan(x)` | Tangent (radians) | `math.tan(math.pi/4)` | `1.0` |
| `math.log(x)` | Natural logarithm | `math.log(math.e)` | `1.0` |
| `math.log10(x)` | Base-10 logarithm | `math.log10(100)` | `2.0` |
| `math.exp(x)` | e^x | `math.exp(1)` | `2.718...` |
| `math.factorial(x)` | Factorial | `math.factorial(5)` | `120` |

## Code Examples

### Built-in Math Functions

```python
# Basic arithmetic operations
print(abs(-42))           # 42
print(abs(-3.14))         # 3.14

# Rounding
print(round(3.14159))     # 3
print(round(3.14159, 2))  # 3.14
print(round(3.14159, 4))  # 3.1416

# Power operations
print(pow(2, 3))          # 8
print(pow(4, 0.5))        # 2.0 (square root)
print(2 ** 3)             # 8 (alternative syntax)

# Min/Max operations
numbers = [10, 5, 8, 20, 3]
print(min(numbers))       # 3
print(max(numbers))       # 20
print(min(5, 10, 3))      # 3
print(max(5, 10, 3))      # 10

# Sum operations
print(sum([1, 2, 3, 4]))  # 10
print(sum(range(1, 6)))   # 15 (sum of 1-5)

# Division with quotient and remainder
quotient, remainder = divmod(17, 5)
print(f"17 ÷ 5 = {quotient} remainder {remainder}")  # 17 ÷ 5 = 3 remainder 2
```

### Math Module Functions

```python
import math

# Square root and power functions
print(math.sqrt(25))      # 5.0
print(math.pow(2, 3))     # 8.0 (same as pow but returns float)

# Ceiling and floor
print(math.ceil(4.1))     # 5
print(math.ceil(4.9))     # 5
print(math.floor(4.1))    # 4
print(math.floor(4.9))    # 4

# Trigonometric functions (angles in radians)
print(math.sin(math.pi/2))    # 1.0
print(math.cos(0))            # 1.0
print(math.tan(math.pi/4))    # 1.0

# Convert degrees to radians
angle_degrees = 90
angle_radians = math.radians(angle_degrees)
print(math.sin(angle_radians))  # 1.0

# Convert radians to degrees
print(math.degrees(math.pi))    # 180.0

# Logarithmic functions
print(math.log(math.e))       # 1.0 (natural log)
print(math.log10(100))        # 2.0 (base-10 log)
print(math.log(8, 2))         # 3.0 (log base 2)

# Exponential functions
print(math.exp(1))            # 2.718281828459045 (e^1)
print(math.exp(0))            # 1.0

# Factorial
print(math.factorial(5))      # 120
print(math.factorial(0))      # 1

# Constants
print(math.pi)                # 3.141592653589793
print(math.e)                 # 2.718281828459045
```

### Advanced Math Operations

```python
import math

# Hyperbolic functions
print(math.sinh(0))           # 0.0
print(math.cosh(0))           # 1.0
print(math.tanh(0))           # 0.0

# Inverse trigonometric functions
print(math.asin(1))           # 1.5707... (π/2)
print(math.acos(0))           # 1.5707... (π/2)
print(math.atan(1))           # 0.7853... (π/4)

# Two-argument arctangent
print(math.atan2(1, 1))       # 0.7853... (π/4)

# Distance and magnitude
print(math.hypot(3, 4))       # 5.0 (hypotenuse)
print(math.hypot(1, 1))       # 1.414... (√2)

# Special functions
print(math.gcd(48, 18))       # 6 (greatest common divisor)
print(math.isqrt(10))         # 3 (integer square root)

# Check for special values
print(math.isfinite(42))      # True
print(math.isfinite(float('inf')))  # False
print(math.isnan(float('nan')))     # True
print(math.isinf(float('inf')))     # True
```

### Practical Examples

```python
import math

# Calculate compound interest
def compound_interest(principal, rate, time, n=1):
    """Calculate compound interest"""
    amount = principal * (1 + rate/n) ** (n * time)
    return round(amount, 2)

principal = 1000
rate = 0.05  # 5%
time = 3     # years
result = compound_interest(principal, rate, time, 12)  # monthly compounding
print(f"${principal} at {rate*100}% for {time} years = ${result}")

# Calculate distance between two points
def distance(x1, y1, x2, y2):
    """Calculate Euclidean distance between two points"""
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

dist = distance(0, 0, 3, 4)
print(f"Distance: {dist}")  # 5.0

# Convert temperature
def celsius_to_fahrenheit(celsius):
    """Convert Celsius to Fahrenheit"""
    return (celsius * 9/5) + 32

def fahrenheit_to_celsius(fahrenheit):
    """Convert Fahrenheit to Celsius"""
    return (fahrenheit - 32) * 5/9

print(f"100°C = {celsius_to_fahrenheit(100)}°F")  # 212.0°F
print(f"32°F = {fahrenheit_to_celsius(32)}°C")    # 0.0°C

# Statistical calculations
def mean(numbers):
    """Calculate arithmetic mean"""
    return sum(numbers) / len(numbers)

def median(numbers):
    """Calculate median"""
    sorted_nums = sorted(numbers)
    n = len(sorted_nums)
    if n % 2 == 0:
        return (sorted_nums[n//2 - 1] + sorted_nums[n//2]) / 2
    else:
        return sorted_nums[n//2]

data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
print(f"Mean: {mean(data)}")      # 5.5
print(f"Median: {median(data)}")  # 5.5
```

### Working with Random Numbers

```python
import random
import math

# Generate random numbers
print(random.random())           # Random float between 0 and 1
print(random.randint(1, 10))     # Random integer between 1 and 10
print(random.uniform(1.5, 10.5)) # Random float between 1.5 and 10.5

# Random selection
colors = ['red', 'blue', 'green', 'yellow']
print(random.choice(colors))     # Random choice from list

# Shuffle a list
numbers = [1, 2, 3, 4, 5]
random.shuffle(numbers)
print(numbers)                   # Shuffled list

# Generate random sample
sample = random.sample(range(1, 51), 5)  # 5 random numbers from 1-50
print(sample)

# Set seed for reproducible results
random.seed(42)
print(random.random())           # Same result every time with seed 42
```

## Tips and Best Practices

1. **Import the math module**: Most advanced functions require `import math`
2. **Handle edge cases**: Check for division by zero, negative square roots, etc.
3. **Use appropriate precision**: Consider using `decimal` module for financial calculations
4. **Angles in radians**: Trigonometric functions expect radians, not degrees
5. **Performance**: Built-in functions are usually faster than custom implementations
