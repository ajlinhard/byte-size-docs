# Command Line Parser
There are 2 main methods of working with python calls off the command line argparse and sys.argv. The first is more formalized and the second is quicker with less docs and verifications built-in.

# Argparse
You can create a class that processes command line arguments using Python's `argparse` module. Here's a comprehensive example:

```python
import argparse
import sys

class DataProcessor:
    def __init__(self, input_file, output_file, verbose=False, batch_size=100):
        self.input_file = input_file
        self.output_file = output_file
        self.verbose = verbose
        self.batch_size = batch_size
        
    def process(self):
        """Main processing method"""
        if self.verbose:
            print(f"Processing {self.input_file} -> {self.output_file}")
            print(f"Batch size: {self.batch_size}")
        
        # Your actual processing logic here
        print("Processing complete!")
    
    @classmethod
    def from_args(cls):
        """Create instance from command line arguments"""
        parser = argparse.ArgumentParser(
            description="Process data files with configurable options"
        )
        
        # Required arguments
        parser.add_argument(
            'input_file',
            help='Input file path'
        )
        
        parser.add_argument(
            'output_file', 
            help='Output file path'
        )
        
        # Optional arguments
        parser.add_argument(
            '-v', '--verbose',
            action='store_true',
            help='Enable verbose output'
        )
        
        parser.add_argument(
            '-b', '--batch-size',
            type=int,
            default=100,
            help='Batch size for processing (default: 100)'
        )
        
        parser.add_argument(
            '--config',
            help='Configuration file path'
        )
        
        args = parser.parse_args()
        
        # Create and return instance with parsed arguments
        return cls(
            input_file=args.input_file,
            output_file=args.output_file,
            verbose=args.verbose,
            batch_size=args.batch_size
        )

def main():
    """Entry point when run as script"""
    try:
        processor = DataProcessor.from_args()
        processor.process()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

Here's an alternative approach using a dedicated argument parser class:

```python
import argparse
from pathlib import Path

class ArgumentParser:
    def __init__(self):
        self.parser = self._create_parser()
    
    def _create_parser(self):
        parser = argparse.ArgumentParser(
            description="Data processing utility",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  python script.py input.txt output.txt
  python script.py input.txt output.txt --verbose --batch-size 50
            """
        )
        
        parser.add_argument('input_file', type=Path, help='Input file')
        parser.add_argument('output_file', type=Path, help='Output file')
        parser.add_argument('-v', '--verbose', action='store_true')
        parser.add_argument('-b', '--batch-size', type=int, default=100)
        
        return parser
    
    def parse_args(self):
        return self.parser.parse_args()

class DataProcessor:
    def __init__(self, args):
        self.input_file = args.input_file
        self.output_file = args.output_file
        self.verbose = args.verbose
        self.batch_size = args.batch_size
        
        self._validate_args()
    
    def _validate_args(self):
        if not self.input_file.exists():
            raise FileNotFoundError(f"Input file not found: {self.input_file}")
        
        if self.batch_size <= 0:
            raise ValueError("Batch size must be positive")
    
    def process(self):
        if self.verbose:
            print(f"Processing: {self.input_file} -> {self.output_file}")
        # Processing logic here

def main():
    arg_parser = ArgumentParser()
    args = arg_parser.parse_args()
    
    processor = DataProcessor(args)
    processor.process()

if __name__ == "__main__":
    main()
```

Usage examples:

```bash
# Basic usage
python script.py input.txt output.txt

# With optional arguments
python script.py input.txt output.txt --verbose --batch-size 50

# Short form
python script.py input.txt output.txt -v -b 200

# Help
python script.py --help
```

Key features of this approach:

- **Class method factory**: `from_args()` creates instances directly from command line arguments
- **Argument validation**: Built-in type checking and custom validation
- **Flexible options**: Mix of required and optional arguments
- **Help generation**: Automatic help text generation
- **Error handling**: Graceful handling of parsing errors

The `argparse` module provides many other features like subcommands, argument groups, and custom actions if you need more complex command line interfaces.

---
#Sys.Argv
You can access command line arguments using `sys.argv`, which is a list containing the script name and all arguments passed to it. Here's how:

## Basic Usage

```python
import sys

# sys.argv[0] is always the script name
# sys.argv[1:] are the actual arguments

print("Script name:", sys.argv[0])
print("All arguments:", sys.argv)
print("Arguments without script name:", sys.argv[1:])
print("Number of arguments:", len(sys.argv) - 1)
```

## Simple Example

```python
import sys

def main():
    if len(sys.argv) < 2:
        print("Usage: python script.py <name> [age]")
        sys.exit(1)
    
    name = sys.argv[1]
    age = sys.argv[2] if len(sys.argv) > 2 else "unknown"
    
    print(f"Hello {name}, age: {age}")

if __name__ == "__main__":
    main()
```

Usage:
```bash
python script.py John 25
# Output: Hello John, age: 25

python script.py Alice
# Output: Hello Alice, age: unknown
```

## More Practical Example

```python
import sys

class FileProcessor:
    def __init__(self, input_file, output_file, options=None):
        self.input_file = input_file
        self.output_file = output_file
        self.options = options or {}
    
    def process(self):
        print(f"Processing {self.input_file} -> {self.output_file}")
        if self.options.get('verbose'):
            print("Verbose mode enabled")

def parse_arguments():
    args = sys.argv[1:]  # Skip script name
    
    if len(args) < 2:
        print("Usage: python script.py <input> <output> [--verbose]")
        sys.exit(1)
    
    input_file = args[0]
    output_file = args[1]
    
    # Parse optional flags
    options = {}
    if '--verbose' in args:
        options['verbose'] = True
    
    return input_file, output_file, options

def main():
    try:
        input_file, output_file, options = parse_arguments()
        processor = FileProcessor(input_file, output_file, options)
        processor.process()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

## Handling Different Argument Types

```python
import sys

def process_args():
    args = sys.argv[1:]
    
    # Convert string arguments to appropriate types
    try:
        name = args[0]
        age = int(args[1]) if len(args) > 1 else 0
        height = float(args[2]) if len(args) > 2 else 0.0
        is_student = args[3].lower() == 'true' if len(args) > 3 else False
        
        return name, age, height, is_student
    except (IndexError, ValueError) as e:
        print("Error parsing arguments:", e)
        sys.exit(1)

# Usage: python script.py John 25 5.9 true
name, age, height, is_student = process_args()
print(f"Name: {name}, Age: {age}, Height: {height}, Student: {is_student}")
```

## Key Points About sys.argv

- `sys.argv[0]` is always the script name/path
- `sys.argv[1:]` contains the actual command line arguments
- All arguments are strings - you need to convert them manually
- Arguments are split by spaces (unless quoted)
- No automatic help generation or validation

## Example with Error Handling

```python
import sys
import os

class ConfigProcessor:
    def __init__(self):
        self.config_file = None
        self.output_dir = None
        self.debug = False
    
    def parse_args(self):
        args = sys.argv[1:]
        
        if not args or '--help' in args or '-h' in args:
            self.show_help()
            sys.exit(0)
        
        # Simple argument parsing
        i = 0
        while i < len(args):
            if args[i] == '--config':
                if i + 1 < len(args):
                    self.config_file = args[i + 1]
                    i += 2
                else:
                    print("Error: --config requires a file path")
                    sys.exit(1)
            elif args[i] == '--output':
                if i + 1 < len(args):
                    self.output_dir = args[i + 1]
                    i += 2
                else:
                    print("Error: --output requires a directory path")
                    sys.exit(1)
            elif args[i] == '--debug':
                self.debug = True
                i += 1
            else:
                print(f"Unknown argument: {args[i]}")
                sys.exit(1)
        
        self.validate_args()
    
    def validate_args(self):
        if not self.config_file:
            print("Error: --config is required")
            sys.exit(1)
        
        if not os.path.exists(self.config_file):
            print(f"Error: Config file not found: {self.config_file}")
            sys.exit(1)
    
    def show_help(self):
        print("Usage: python script.py --config <file> [--output <dir>] [--debug]")
        print("Options:")
        print("  --config <file>  Configuration file path")
        print("  --output <dir>   Output directory (optional)")
        print("  --debug          Enable debug mode")

def main():
    processor = ConfigProcessor()
    processor.parse_args()
    
    print(f"Config: {processor.config_file}")
    print(f"Output: {processor.output_dir}")
    print(f"Debug: {processor.debug}")

if __name__ == "__main__":
    main()
```

While `sys.argv` works fine for simple cases, for more complex command line interfaces, consider using `argparse` as it provides better error handling, automatic help generation, and type conversion.

