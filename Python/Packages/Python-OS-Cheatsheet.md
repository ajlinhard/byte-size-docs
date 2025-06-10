# OS Cheatsheet
This cheatsheet covers the most commonly used functions in Python's `os` module, starting with a quick reference table followed by detailed examples. The examples are organized by functionality and include practical use cases you'll encounter in real-world programming.

The cheatsheet covers:
- Directory operations (creating, listing, removing)
- File operations (checking existence, getting info, renaming, deleting)
- Path manipulations (joining, splitting, getting absolute paths)
- Environment variables
- Directory tree walking
- System information
- Best practices and common patterns

Each section includes working code examples that you can run directly. The examples also demonstrate proper error handling and cross-platform compatibility considerations.

# Python OS Module Cheatsheet

## Quick Reference Table

| Function/Attribute | Description | Example Usage |
|-------------------|-------------|---------------|
| `os.getcwd()` | Get current working directory | `os.getcwd()` |
| `os.chdir(path)` | Change current directory | `os.chdir('/home/user')` |
| `os.listdir(path)` | List directory contents | `os.listdir('.')` |
| `os.mkdir(path)` | Create a directory | `os.mkdir('new_folder')` |
| `os.makedirs(path)` | Create directories recursively | `os.makedirs('path/to/folder')` |
| `os.rmdir(path)` | Remove empty directory | `os.rmdir('empty_folder')` |
| `os.removedirs(path)` | Remove directories recursively | `os.removedirs('path/to/folder')` |
| `os.remove(path)` | Delete a file | `os.remove('file.txt')` |
| `os.unlink(path)` | Delete a file (alias for remove) | `os.unlink('file.txt')` |
| `os.rename(src, dst)` | Rename file/directory | `os.rename('old.txt', 'new.txt')` |
| `os.path.exists(path)` | Check if path exists | `os.path.exists('file.txt')` |
| `os.path.isfile(path)` | Check if path is a file | `os.path.isfile('file.txt')` |
| `os.path.isdir(path)` | Check if path is a directory | `os.path.isdir('folder')` |
| `os.path.join()` | Join path components | `os.path.join('folder', 'file.txt')` |
| `os.path.split(path)` | Split path into directory and file | `os.path.split('/path/file.txt')` |
| `os.path.basename(path)` | Get filename from path | `os.path.basename('/path/file.txt')` |
| `os.path.dirname(path)` | Get directory from path | `os.path.dirname('/path/file.txt')` |
| `os.path.abspath(path)` | Get absolute path | `os.path.abspath('file.txt')` |
| `os.path.getsize(path)` | Get file size in bytes | `os.path.getsize('file.txt')` |
| `os.stat(path)` | Get file/directory statistics | `os.stat('file.txt')` |
| `os.walk(path)` | Walk directory tree | `os.walk('/path')` |
| `os.environ` | Environment variables dictionary | `os.environ['HOME']` |
| `os.getenv(key)` | Get environment variable | `os.getenv('PATH')` |
| `os.system(command)` | Execute system command | `os.system('ls -l')` |
| `os.name` | Operating system name | `os.name` |
| `os.sep` | Path separator | `os.sep` |

## Detailed Examples

### Working with Directories

```python
import os

# Get current working directory
current_dir = os.getcwd()
print(f"Current directory: {current_dir}")

# Change directory
os.chdir('/tmp')
print(f"Changed to: {os.getcwd()}")

# List directory contents
files = os.listdir('.')
print(f"Files in current directory: {files}")

# Create a single directory
os.mkdir('test_folder')

# Create nested directories
os.makedirs('path/to/nested/folder', exist_ok=True)

# Remove empty directory
os.rmdir('test_folder')

# Remove nested directories (only if empty)
os.removedirs('path/to/nested/folder')
```

### Working with Files

```python
import os

# Check if file exists
if os.path.exists('example.txt'):
    print("File exists")
else:
    print("File does not exist")

# Create a file and work with it
with open('test_file.txt', 'w') as f:
    f.write("Hello, World!")

# Get file information
file_stats = os.stat('test_file.txt')
print(f"File size: {file_stats.st_size} bytes")
print(f"Last modified: {file_stats.st_mtime}")

# Alternative way to get file size
file_size = os.path.getsize('test_file.txt')
print(f"File size: {file_size} bytes")

# Rename file
os.rename('test_file.txt', 'renamed_file.txt')

# Delete file
os.remove('renamed_file.txt')
```

### Path Operations

```python
import os

# Join paths (cross-platform)
file_path = os.path.join('folder', 'subfolder', 'file.txt')
print(f"Joined path: {file_path}")

# Split path
directory, filename = os.path.split('/home/user/documents/file.txt')
print(f"Directory: {directory}")
print(f"Filename: {filename}")

# Get just the filename
basename = os.path.basename('/home/user/documents/file.txt')
print(f"Basename: {basename}")

# Get just the directory
dirname = os.path.dirname('/home/user/documents/file.txt')
print(f"Directory name: {dirname}")

# Get absolute path
abs_path = os.path.abspath('relative_file.txt')
print(f"Absolute path: {abs_path}")

# Split filename and extension
name, ext = os.path.splitext('document.pdf')
print(f"Name: {name}, Extension: {ext}")
```

### Environment Variables

```python
import os

# Access all environment variables
print("All environment variables:")
for key, value in os.environ.items():
    print(f"{key}: {value}")

# Get specific environment variable
home_dir = os.environ.get('HOME')  # Unix/Linux/Mac
# home_dir = os.environ.get('USERPROFILE')  # Windows
print(f"Home directory: {home_dir}")

# Get environment variable with default
path_var = os.getenv('PATH', 'Not found')
print(f"PATH variable: {path_var}")

# Set environment variable (for current process only)
os.environ['MY_VARIABLE'] = 'my_value'
print(f"My variable: {os.getenv('MY_VARIABLE')}")
```

### Walking Directory Trees

```python
import os

# Walk through all subdirectories
for root, dirs, files in os.walk('/path/to/directory'):
    print(f"Current directory: {root}")
    print(f"Subdirectories: {dirs}")
    print(f"Files: {files}")
    print("-" * 40)

# Example: Find all Python files
def find_python_files(directory):
    python_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    return python_files

py_files = find_python_files('.')
print(f"Python files found: {py_files}")
```

### System Information

```python
import os

# Operating system name
print(f"OS name: {os.name}")  # 'posix' for Unix/Linux/Mac, 'nt' for Windows

# Path separator
print(f"Path separator: '{os.sep}'")  # '/' for Unix, '\' for Windows

# Line separator
print(f"Line separator: {repr(os.linesep)}")

# Current user (if available)
try:
    username = os.getlogin()
    print(f"Current user: {username}")
except OSError:
    print("Unable to get current user")
```

### Executing System Commands

```python
import os

# Execute system command (returns exit status)
exit_status = os.system('echo "Hello from system command"')
print(f"Command exit status: {exit_status}")

# Better alternative: use subprocess module
import subprocess

# More secure and flexible way to run commands
result = subprocess.run(['ls', '-l'], capture_output=True, text=True)
print(f"Command output:\n{result.stdout}")
```

### File Permissions and Timestamps

```python
import os
import time

# Get detailed file statistics
file_stats = os.stat('example.txt')

print(f"File mode: {oct(file_stats.st_mode)}")
print(f"File size: {file_stats.st_size} bytes")
print(f"Last accessed: {time.ctime(file_stats.st_atime)}")
print(f"Last modified: {time.ctime(file_stats.st_mtime)}")
print(f"Created: {time.ctime(file_stats.st_ctime)}")

# Check file permissions
if os.access('example.txt', os.R_OK):
    print("File is readable")
if os.access('example.txt', os.W_OK):
    print("File is writable")
if os.access('example.txt', os.X_OK):
    print("File is executable")
```

### Common Patterns and Best Practices

```python
import os

# Safe file operations with error handling
def safe_remove_file(filepath):
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
            print(f"Removed {filepath}")
        else:
            print(f"File {filepath} does not exist")
    except OSError as e:
        print(f"Error removing {filepath}: {e}")

# Create directory if it doesn't exist
def ensure_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Created directory: {directory}")
    else:
        print(f"Directory already exists: {directory}")

# Get all files with specific extension
def get_files_by_extension(directory, extension):
    files = []
    for filename in os.listdir(directory):
        if filename.endswith(extension):
            files.append(os.path.join(directory, filename))
    return files

# Usage examples
safe_remove_file('unwanted_file.txt')
ensure_directory('logs')
txt_files = get_files_by_extension('.', '.txt')
print(f"Text files: {txt_files}")
```

## Important Notes

- Always use `os.path.join()` for cross-platform path handling
- Use `os.path.exists()` before file operations to avoid errors
- The `os.makedirs()` function with `exist_ok=True` won't raise an error if the directory already exists
- For more advanced file operations, consider using the `pathlib` module (Python 3.4+)
- For running system commands, `subprocess` module is preferred over `os.system()`
- Environment variable changes with `os.environ` only affect the current process and its children
