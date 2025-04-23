# Python Regular Expressions Cheatsheet

## Basic Regex Symbols

| Symbol | Description | Example |
|--------|-------------|---------|
| `.` | Matches any character except newline | `a.c` matches "abc", "a2c", etc. |
| `^` | Matches start of string | `^hello` matches "hello world" |
| `$` | Matches end of string | `world$` matches "hello world" |
| `*` | Matches 0 or more repetitions | `ab*c` matches "ac", "abc", "abbc", etc. |
| `+` | Matches 1 or more repetitions | `ab+c` matches "abc", "abbc", but not "ac" |
| `?` | Matches 0 or 1 repetition | `ab?c` matches "ac" and "abc" |
| `\` | Escapes special characters | `\\.` matches "." |
| `[]` | Matches set of characters | `[abc]` matches "a", "b", or "c" |
| `[^]` | Matches characters NOT in set | `[^abc]` matches any character except "a", "b", or "c" |
| `\d` | Matches digits (equivalent to `[0-9]`) | `\d+` matches "123" |
| `\D` | Matches non-digits | `\D+` matches "abc" |
| `\w` | Matches word characters `[a-zA-Z0-9_]` | `\w+` matches "abc_123" |
| `\W` | Matches non-word characters | `\W+` matches "!@#" |
| `\s` | Matches whitespace characters | `\s+` matches spaces, tabs, newlines |
| `\S` | Matches non-whitespace | `\S+` matches any non-whitespace sequence |
| `\b` | Matches word boundary | `\bword\b` matches "word" but not "sword" or "wordsmith" |
| `\B` | Matches non-word boundary | `\Bword\B` matches "keyword" but not "word" |
| `|` | Alternation (OR operator) | `cat|dog` matches "cat" or "dog" |
| `()` | Creates capturing group | `(abc)+` matches "abc", "abcabc", etc. |
| `(?:)` | Creates non-capturing group | `(?:abc)+` like above but doesn't capture |

## Quantifiers

| Quantifier | Description | Example |
|------------|-------------|---------|
| `{n}` | Exactly n occurrences | `a{3}` matches "aaa" |
| `{n,}` | n or more occurrences | `a{2,}` matches "aa", "aaa", etc. |
| `{n,m}` | Between n and m occurrences | `a{2,4}` matches "aa", "aaa", "aaaa" |
| `*` | 0 or more occurrences (same as `{0,}`) | `a*` matches "", "a", "aa", etc. |
| `+` | 1 or more occurrences (same as `{1,}`) | `a+` matches "a", "aa", etc. |
| `?` | 0 or 1 occurrence (same as `{0,1}`) | `a?` matches "" or "a" |

## Character Classes

| Class | Description |
|-------|-------------|
| `[abc]` | Matches any of the characters a, b, or c |
| `[^abc]` | Matches any character except a, b, or c |
| `[a-z]` | Matches any character from a to z |
| `[A-Z]` | Matches any character from A to Z |
| `[0-9]` | Matches any digit from 0 to 9 |
| `[a-zA-Z0-9]` | Matches any alphanumeric character |

## Lookahead and Lookbehind Assertions

| Assertion | Description | Example |
|-----------|-------------|---------|
| `(?=...)` | Positive lookahead | `x(?=y)` matches "x" only if followed by "y" |
| `(?!...)` | Negative lookahead | `x(?!y)` matches "x" only if not followed by "y" |
| `(?<=...)` | Positive lookbehind | `(?<=y)x` matches "x" only if preceded by "y" |
| `(?<!...)` | Negative lookbehind | `(?<!y)x` matches "x" only if not preceded by "y" |

## Python `re` Module Functions

| Function | Description |
|----------|-------------|
| `re.search(pattern, string)` | Searches for pattern anywhere in string, returns first match |
| `re.match(pattern, string)` | Checks if pattern matches at the beginning of string |
| `re.fullmatch(pattern, string)` | Checks if pattern matches the entire string |
| `re.findall(pattern, string)` | Returns all non-overlapping matches as a list of strings |
| `re.finditer(pattern, string)` | Returns an iterator of match objects for all matches |
| `re.split(pattern, string)` | Splits string by pattern occurrences |
| `re.sub(pattern, repl, string)` | Replaces matches with replacement string |
| `re.subn(pattern, repl, string)` | Like `re.sub()` but returns tuple (new_string, count) |
| `re.escape(string)` | Escapes special regex characters in string |
| `re.compile(pattern)` | Compiles a pattern for reuse |

## Flags

| Flag | Description |
|------|-------------|
| `re.I` or `re.IGNORECASE` | Case-insensitive matching |
| `re.M` or `re.MULTILINE` | `^` and `$` match start/end of each line |
| `re.S` or `re.DOTALL` | `.` matches newline too |
| `re.X` or `re.VERBOSE` | Allows formatted expressions with comments |
| `re.A` or `re.ASCII` | Makes `\w`, `\W`, etc. match only ASCII |
| `re.U` or `re.UNICODE` | Makes `\w`, `\W`, etc. match Unicode (default in Python 3) |

## Simple Examples

### 1. Find all digits in a string
```python
import re
text = "abc123def456"
digits = re.findall(r'\d+', text)
print(digits)  # Output: ['123', '456']
```

### 2. Extract email addresses
```python
import re
text = "Contact us at support@example.com or info@company.org"
emails = re.findall(r'[\w\.-]+@[\w\.-]+', text)
print(emails)  # Output: ['support@example.com', 'info@company.org']
```

### 3. Validate a date format (MM/DD/YYYY)
```python
import re
def is_valid_date(date_str):
    pattern = r'^(0[1-9]|1[0-2])/(0[1-9]|[12][0-9]|3[01])/(19|20)\d\d$'
    return bool(re.match(pattern, date_str))

print(is_valid_date("12/25/2023"))  # Output: True
print(is_valid_date("13/25/2023"))  # Output: False
```

### 4. Split string by multiple delimiters
```python
import re
text = "apple,banana;cherry:grape"
fruits = re.split(r'[,;:]', text)
print(fruits)  # Output: ['apple', 'banana', 'cherry', 'grape']
```

## Intermediate Examples

### 5. Capture groups to extract components
```python
import re
text = "Name: John, Age: 30, City: New York"
pattern = r'Name: (.*?), Age: (\d+), City: (.*)'
match = re.search(pattern, text)
if match:
    name, age, city = match.groups()
    print(f"Name: {name}, Age: {age}, City: {city}")
    # Output: Name: John, Age: 30, City: New York
```

### 6. Named capture groups
```python
import re
text = "Name: John, Age: 30, City: New York"
pattern = r'Name: (?P<name>.*?), Age: (?P<age>\d+), City: (?P<city>.*)'
match = re.search(pattern, text)
if match:
    print(f"Name: {match['name']}, Age: {match['age']}, City: {match['city']}")
    # Output: Name: John, Age: 30, City: New York
```

### 7. Find words that start with 'p' and end with 'n'
```python
import re
text = "python is a programming language with pattern matching"
words = re.findall(r'\b[pP]\w*n\b', text)
print(words)  # Output: ['python', 'pattern']
```

### 8. Replace text with a function
```python
import re

def capitalize_match(match):
    return match.group(0).upper()

text = "Regular expressions are powerful tools"
result = re.sub(r'\b[a-z]{5,}\b', capitalize_match, text)
print(result)  # Output: "REGULAR EXPRESSIONS are POWERFUL TOOLS"
```

## Advanced Examples

### 9. Lookahead and lookbehind assertions
```python
import re
# Find numbers followed by 'px' but don't include 'px' in match
text = "Width: 100px, Height: 200px"
numbers = re.findall(r'\d+(?=px)', text)
print(numbers)  # Output: ['100', '200']

# Find numbers preceded by '$' but don't include '$' in match
text = "Prices: $50, $100, and $150"
numbers = re.findall(r'(?<=\$)\d+', text)
print(numbers)  # Output: ['50', '100', '150']
```

### 10. Password validation
```python
import re
def is_valid_password(password):
    # At least 8 chars, 1 uppercase, 1 lowercase, 1 digit, 1 special char
    pattern = r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[!@#$%^&*()_+]).{8,}$'
    return bool(re.match(pattern, password))

print(is_valid_password("Passw0rd!"))  # Output: True
print(is_valid_password("password"))   # Output: False
```

### 11. Extract URLs from text
```python
import re
text = "Visit our site at https://example.com or http://test.org"
urls = re.findall(r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', text)
print(urls)  # Output: ['https://example.com', 'http://test.org']
```

### 12. Parse CSV with regex
```python
import re
csv_line = '"John Doe","New York, NY",30,"Software Engineer"'
pattern = r'"([^"]*)"'
fields = re.findall(pattern, csv_line)
print(fields)  # Output: ['John Doe', 'New York, NY', '30', 'Software Engineer']
```

### 13. Multiline and comments with verbose mode
```python
import re
pattern = re.compile(r'''
    ^                 # Start of string
    (\d{3})           # Area code
    [-. ]?            # Optional separator
    (\d{3})           # First 3 digits
    [-. ]?            # Optional separator
    (\d{4})           # Last 4 digits
    $                 # End of string
''', re.VERBOSE)

print(bool(pattern.match("123-456-7890")))  # Output: True
print(bool(pattern.match("123.456.7890")))  # Output: True
print(bool(pattern.match("1234567890")))    # Output: True
```

## Tips and Best Practices

1. **Compile patterns** for reuse to improve performance
   ```python
   pattern = re.compile(r'\d+')
   result1 = pattern.findall("123 abc 456")
   result2 = pattern.findall("789 def 012")
   ```

2. **Use raw strings `r''`** for regex patterns to avoid having to double-escape backslashes

3. **Use non-capturing groups `(?:)`** when you don't need the matched content

4. **Be specific** with your patterns to avoid unexpected matches

5. **Test your patterns** with various inputs, including edge cases

6. **Use verbose mode `re.VERBOSE`** for complex patterns to improve readability

7. **Watch out for greediness** - `*` and `+` are greedy by default, use `*?` and `+?` for non-greedy matching
