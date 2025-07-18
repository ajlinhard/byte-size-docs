# UV Python Package Manager Cheatsheet
I've created a comprehensive `uv` cheatsheet that covers all the essential commands and workflows. The cheatsheet is organized into logical sections covering everything from basic package installation to advanced project management features.

Key highlights include:
- **Drop-in pip replacement** commands that work exactly like pip
- **Virtual environment** management 
- **Dependency compilation** and resolution (similar to pip-tools)
- **Project management** features for newer uv versions
- **Performance optimizations** and caching options
- **Common workflows** for typical development scenarios

The cheatsheet should serve as a quick reference for both newcomers to `uv` and experienced users looking to leverage its advanced features. You can bookmark this and refer to it whenever you need to remember a specific `uv` command or workflow.

## Installation
```bash
# Install uv
pip install uv
brew install uv                    # macOS
cargo install --git https://github.com/astral-sh/uv uv
```

## Package Installation
```bash
# Install a package
uv pip install package_name

# Install specific version
uv pip install package_name==1.2.3

# Install from requirements file
uv pip install -r requirements.txt

# Install with extras
uv pip install "package_name[extra1,extra2]"

# Install from git
uv pip install git+https://github.com/user/repo.git

# Install editable package
uv pip install -e .
uv pip install -e path/to/package

# Install with constraints
uv pip install -c constraints.txt package_name
```

## Package Management
```bash
# Uninstall package
uv pip uninstall package_name

# Uninstall multiple packages
uv pip uninstall package1 package2

# Upgrade package
uv pip install --upgrade package_name

# Upgrade all packages
uv pip install --upgrade-package package_name

# Show package info
uv pip show package_name

# List installed packages
uv pip list

# List outdated packages
uv pip list --outdated

# Freeze current environment
uv pip freeze

# Generate requirements.txt
uv pip freeze > requirements.txt
```

## Virtual Environment Management
```bash
# Create virtual environment
uv venv
uv venv venv_name
uv venv --python 3.11

# Activate virtual environment (same as standard venv)
source .venv/bin/activate        # Linux/macOS
.venv\Scripts\activate          # Windows

# Install in specific virtual environment
uv pip install --python path/to/python package_name
```

## Dependency Resolution & Compilation
```bash
# Compile requirements.in to requirements.txt
uv pip compile requirements.in

# Compile with specific Python version
uv pip compile --python-version 3.11 requirements.in

# Compile with upgrade strategy
uv pip compile --upgrade requirements.in
uv pip compile --upgrade-package package_name requirements.in

# Compile with extras
uv pip compile requirements.in --extra dev,test

# Generate lock file
uv pip compile requirements.in --generate-hashes

# Sync environment with requirements
uv pip sync requirements.txt
```

## Advanced Features
```bash
# Install with specific index
uv pip install --index-url https://pypi.org/simple/ package_name

# Install with extra index
uv pip install --extra-index-url https://extra-index.com/simple/ package_name

# Install with trusted host
uv pip install --trusted-host pypi.org package_name

# Install without binary wheels
uv pip install --no-binary package_name

# Install only binary wheels
uv pip install --only-binary package_name

# Dry run (show what would be installed)
uv pip install --dry-run package_name
```

## Caching & Performance
```bash
# Clear cache
uv cache clean

# Show cache info
uv cache info

# Install without cache
uv pip install --no-cache package_name

# Precompile packages
uv pip compile --prerelease=allow requirements.in
```

## Configuration & Settings
```bash
# Show uv version
uv --version

# Get help
uv --help
uv pip --help
uv pip install --help

# Verbose output
uv pip install -v package_name

# Quiet output
uv pip install -q package_name

# Show what files would be installed
uv pip install --dry-run --report package_name
```

## Project Management (uv 0.1.0+)
```bash
# Initialize new project
uv init project_name

# Add dependency
uv add package_name

# Add development dependency
uv add --dev package_name

# Remove dependency
uv remove package_name

# Run command in project environment
uv run python script.py
uv run pytest

# Install project dependencies
uv sync

# Lock dependencies
uv lock
```

## Common Workflows

### Setting up a new project
```bash
python -m venv .venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

### Updating dependencies
```bash
uv pip compile --upgrade requirements.in
uv pip sync requirements.txt
```

### Creating reproducible environment
```bash
uv pip compile requirements.in --generate-hashes
uv pip install -r requirements.txt --require-hashes
```

## Tips & Best Practices
- Use `uv pip compile` instead of `pip-tools` for faster dependency resolution
- Always pin versions in production with `requirements.txt`
- Use `--upgrade-package` for selective upgrades
- Leverage caching for faster repeated installations
- Use `uv sync` to ensure environment matches requirements exactly
- Consider using `uv run` for project-specific commands
