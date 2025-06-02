# Pandas String Manipulation Cheatsheet
This cheatsheet covers all the essential pandas string manipulation methods organized by category. It includes practical examples for common data cleaning tasks like phone numbers, emails, and names. The performance tips at the end will help you write more efficient code when working with large datasets.

The `.str` accessor is your gateway to all these string methods in pandas - just remember that it only works on Series objects containing strings!

## Basic String Operations

### Case Conversion
```python
df['column'].str.lower()           # Convert to lowercase
df['column'].str.upper()           # Convert to uppercase  
df['column'].str.title()           # Title case (first letter of each word)
df['column'].str.capitalize()      # Capitalize first letter only
df['column'].str.swapcase()        # Swap case of all letters
```

### String Length and Counting
```python
df['column'].str.len()             # Length of each string
df['column'].str.count('pattern')  # Count occurrences of pattern
df['column'].str.count('[aeiou]')  # Count vowels (regex)
```

## String Cleaning and Trimming

### Whitespace Removal
```python
df['column'].str.strip()           # Remove leading/trailing whitespace
df['column'].str.lstrip()          # Remove leading whitespace
df['column'].str.rstrip()          # Remove trailing whitespace
df['column'].str.strip('.,!?')     # Remove specific characters
```

### Padding
```python
df['column'].str.pad(10, side='left', fillchar='0')   # Left pad with zeros
df['column'].str.center(10, fillchar='*')             # Center with asterisks
df['column'].str.zfill(5)                             # Zero-fill to width 5
```

## String Searching and Testing

### Contains and Matching
```python
df['column'].str.contains('pattern')                  # Boolean mask for contains
df['column'].str.contains('pattern', case=False)     # Case-insensitive
df['column'].str.contains('^start')                   # Starts with (regex)
df['column'].str.contains('end$')                     # Ends with (regex)
df['column'].str.match('^pattern')                    # Match from beginning
df['column'].str.fullmatch('exact_pattern')          # Exact match only
```

### String Testing
```python
df['column'].str.startswith('prefix')     # Starts with string
df['column'].str.endswith('suffix')       # Ends with string
df['column'].str.isalpha()                # All alphabetic
df['column'].str.isdigit()                # All digits
df['column'].str.isalnum()                # All alphanumeric
df['column'].str.isnumeric()              # All numeric
df['column'].str.isdecimal()              # All decimal
df['column'].str.isspace()                # All whitespace
df['column'].str.islower()                # All lowercase
df['column'].str.isupper()                # All uppercase
df['column'].str.istitle()                # Title case format
```

## String Replacement and Substitution

### Basic Replacement
```python
df['column'].str.replace('old', 'new')              # Replace first occurrence
df['column'].str.replace('old', 'new', n=2)        # Replace first 2 occurrences
df['column'].str.replace('pattern', 'new', regex=True)  # Regex replacement
```

### Advanced Replacement
```python
# Replace multiple patterns
df['column'].str.replace('[.,!?]', '', regex=True)
# Replace with function
df['column'].str.replace(r'(\d+)', lambda x: str(int(x.group(1)) * 2), regex=True)
```

## String Splitting and Joining

### Splitting
```python
df['column'].str.split()                    # Split on whitespace
df['column'].str.split(',')                 # Split on comma
df['column'].str.split(',', n=2)            # Split into max 3 parts
df['column'].str.split(',', expand=True)    # Create new columns
df['column'].str.rsplit(',', n=1)           # Split from right
```

### Accessing Split Parts
```python
df['column'].str.split(',').str[0]          # First part
df['column'].str.split(',').str[-1]         # Last part
df['column'].str.split(',').str.get(1)      # Second part (safe indexing)
```

### Joining
```python
df['column'].str.cat()                      # Concatenate all values
df['column'].str.cat(sep=', ')              # Join with separator
df['col1'].str.cat(df['col2'], sep=' ')     # Join two columns
df['column'].str.cat(others=['a', 'b'])     # Join with list
```

## String Slicing and Indexing

### Slicing
```python
df['column'].str[0]           # First character
df['column'].str[-1]          # Last character
df['column'].str[1:4]         # Substring from index 1 to 3
df['column'].str[:3]          # First 3 characters
df['column'].str[2:]          # From 3rd character to end
df['column'].str[::2]         # Every 2nd character
```

### Get and Slice Methods
```python
df['column'].str.get(0)       # Get character at index 0 (safe)
df['column'].str.slice(1, 4)  # Slice from 1 to 4
df['column'].str.slice_replace(1, 3, 'XX')  # Replace slice with 'XX'
```

## Pattern Extraction and Finding

### Finding Positions
```python
df['column'].str.find('pattern')      # Find first occurrence position
df['column'].str.rfind('pattern')     # Find last occurrence position
df['column'].str.index('pattern')     # Like find but raises error if not found
```

### Extracting Patterns
```python
df['column'].str.extract(r'(\d+)')              # Extract first number
df['column'].str.extract(r'(\w+)\s+(\w+)')      # Extract two words
df['column'].str.extractall(r'(\d+)')           # Extract all numbers
df['column'].str.findall(r'\d+')                # Find all numbers as list
```

## String Normalization and Encoding

### Normalization
```python
df['column'].str.normalize('NFKC')    # Unicode normalization
df['column'].str.encode('utf-8')      # Encode to bytes
df['column'].str.decode('utf-8')      # Decode from bytes
```

### Removing Accents
```python
import unicodedata
df['column'].str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('ascii')
```

## Common Use Cases

### Cleaning Phone Numbers
```python
df['phone'].str.replace(r'[^\d]', '', regex=True)  # Keep only digits
df['phone'].str.replace(r'(\d{3})(\d{3})(\d{4})', r'(\1) \2-\3', regex=True)
```

### Extracting Email Components
```python
df['email'].str.extract(r'([^@]+)@([^.]+)\.(.+)')  # username, domain, extension
df['email'].str.contains(r'^[^@]+@[^@]+\.[^@]+$')  # Validate email format
```

### Cleaning Names
```python
df['name'].str.strip().str.title()                           # Clean and title case
df['name'].str.replace(r'\s+', ' ', regex=True)              # Multiple spaces to single
df['name'].str.extract(r'([^,]+),\s*(.+)').iloc[:, [1, 0]]  # "Last, First" to separate columns
```

### Working with URLs
```python
df['url'].str.extract(r'https?://([^/]+)')        # Extract domain
df['url'].str.contains(r'^https://')              # Check if HTTPS
df['url'].str.replace(r'^http://', 'https://')    # Convert HTTP to HTTPS
```

## Performance Tips

1. **Chain operations**: `df['col'].str.lower().str.strip().str.replace(' ', '_')`
2. **Use vectorized operations**: Avoid loops, use `.str` accessor
3. **Filter before operations**: `df[mask]['col'].str.operation()` is faster
4. **Consider categorical**: Convert to category if many repeated values
5. **Use regex wisely**: Simple string operations are often faster than regex

## Common Parameters

- `case=False`: Case-insensitive operations
- `regex=True`: Enable regex patterns
- `na=False`: How to handle NaN values
- `expand=True`: Create new columns from splits
- `n=1`: Limit number of operations (splits, replacements)
