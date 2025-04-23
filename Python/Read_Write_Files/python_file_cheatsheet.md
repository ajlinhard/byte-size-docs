# Python File Handling Cheatsheet: with open() Syntax

## Basic Syntax

```python
with open(file_path, mode) as file_object:
    # operations on file_object
```

The `with` statement creates a context manager that automatically handles closing the file when you're done with it, even if exceptions occur.

## File Open Modes

| Mode | Description |
|------|-------------|
| `'r'` | **Read** - Default mode. Opens file for reading (text mode). |
| `'w'` | **Write** - Opens file for writing. Creates a new file or truncates existing file. |
| `'a'` | **Append** - Opens file for appending. Creates a new file if it doesn't exist. |
| `'x'` | **Exclusive creation** - Opens for writing, fails if file already exists. |
| `'b'` | **Binary mode** - Add to mode for binary operations (e.g., `'rb'`, `'wb'`). |
| `'t'` | **Text mode** - Default. File is handled as text. |
| `'+'` | **Update mode** - Opens for reading and writing (e.g., `'r+'`, `'w+'`). |

## Common File Operations

### Reading Files

```python
# Read entire file content as a string
with open('file.txt', 'r') as file:
    content = file.read()

# Read file line by line
with open('file.txt', 'r') as file:
    for line in file:
        print(line.strip())  # .strip() removes trailing newline

# Read all lines into a list
with open('file.txt', 'r') as file:
    lines = file.readlines()

# Read specific number of characters
with open('file.txt', 'r') as file:
    chunk = file.read(100)  # Reads first 100 characters
```

### Writing Files

```python
# Write a string to a file (overwrites existing content)
with open('file.txt', 'w') as file:
    file.write('Hello, world!')

# Write multiple lines to a file
with open('file.txt', 'w') as file:
    file.write('Line 1\n')
    file.write('Line 2\n')

# Write a list of strings to a file
lines = ['Line 1', 'Line 2', 'Line 3']
with open('file.txt', 'w') as file:
    file.writelines([line + '\n' for line in lines])
```

### Appending to Files

```python
# Append to an existing file
with open('file.txt', 'a') as file:
    file.write('This text will be added to the end of the file.')
```

### Binary Files

```python
# Read binary file (e.g., images)
with open('image.jpg', 'rb') as file:
    binary_data = file.read()

# Write binary file
with open('new_image.jpg', 'wb') as file:
    file.write(binary_data)
```

## File Pointer Operations

```python
with open('file.txt', 'r') as file:
    # Get current position
    position = file.tell()
    
    # Move to specific position (byte offset)
    file.seek(10)  # Move to 10th byte
    
    # Read from current position
    data = file.read(5)  # Read 5 bytes
    
    # Move relative to current position
    file.seek(5, 1)  # Move 5 bytes forward from current position
    
    # Move relative to end of file
    file.seek(-10, 2)  # Move 10 bytes before end of file
```

## Working with File and Directory Paths

```python
import os

# Join path components in a cross-platform way
file_path = os.path.join('folder', 'subfolder', 'file.txt')

# Get absolute path
abs_path = os.path.abspath(file_path)

# Check if file exists
exists = os.path.exists(file_path)

# Check if path is a file or directory
is_file = os.path.isfile(file_path)
is_dir = os.path.isdir('folder')
```

## Exception Handling with Files

```python
try:
    with open('nonexistent.txt', 'r') as file:
        content = file.read()
except FileNotFoundError:
    print("File not found!")
except PermissionError:
    print("Permission denied!")
except IOError as e:
    print(f"I/O error: {e}")
```

## Working with Different Encodings

```python
# Specify encoding when opening text files
with open('file.txt', 'r', encoding='utf-8') as file:
    content = file.read()

# Handle non-utf-8 files
with open('file.txt', 'r', encoding='latin-1') as file:
    content = file.read()
```

## Reading and Writing CSV Files

```python
import csv

# Reading CSV
with open('data.csv', 'r', newline='') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        print(row)  # row is a list of values

# Writing CSV
data = [
    ['Name', 'Age', 'Country'],
    ['Alice', '25', 'USA'],
    ['Bob', '30', 'Canada']
]
with open('output.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerows(data)
```

## Reading and Writing JSON Files

```python
import json

# Reading JSON
with open('data.json', 'r') as jsonfile:
    data = json.load(jsonfile)  # Parses JSON into Python dict/list

# Writing JSON
data = {'name': 'Alice', 'age': 25, 'scores': [85, 90, 92]}
with open('output.json', 'w') as jsonfile:
    json.dump(data, jsonfile, indent=4)  # Pretty-printed with indentation
```

## Best Practices

1. **Always use `with` statement** to ensure files are properly closed.
2. **Be explicit about encoding** for text files, using `encoding='utf-8'` is recommended.
3. **Use `newline=''`** when working with CSV files to handle line endings correctly.
4. **Use the appropriate mode** - don't open in write mode if you only need to read.
5. **Handle exceptions** related to file operations.
6. **Use binary mode** (`'b'`) for non-text files like images, videos, etc.
7. **Check if file exists** before opening in read mode if necessary.

## Real-world Examples

### Example 1: Log File Processing

```python
def process_log(log_path):
    error_count = 0
    with open(log_path, 'r', encoding='utf-8') as log_file:
        for line in log_file:
            if 'ERROR' in line:
                error_count += 1
                print(f"Found error: {line.strip()}")
    return error_count
```

### Example 2: Configuration File

```python
import json

def load_config(config_path='config.json'):
    try:
        with open(config_path, 'r') as config_file:
            return json.load(config_file)
    except FileNotFoundError:
        # Create default config if not found
        default_config = {'debug': False, 'log_level': 'INFO'}
        with open(config_path, 'w') as config_file:
            json.dump(default_config, config_file, indent=2)
        return default_config
```

### Example 3: Data Processing Pipeline

```python
import csv
import json

def convert_csv_to_json(csv_path, json_path):
    data = []
    # Read CSV
    with open(csv_path, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            data.append(row)
    
    # Write JSON
    with open(json_path, 'w', encoding='utf-8') as jsonfile:
        json.dump(data, jsonfile, indent=4)
```
