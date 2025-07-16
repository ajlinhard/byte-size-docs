# Anaconda Command Line Cheatsheet

## Quick Reference Table

| Command Name | Purpose | Key Parameters | Concise Example |
|--------------|---------|----------------|-----------------|
| `conda create` | Create new environment | `-n`, `-c`, `--file` | `conda create -n myenv python=3.9` |
| `conda activate` | Activate environment | environment name | `conda activate myenv` |
| `conda deactivate` | Deactivate current environment | none | `conda deactivate` |
| `conda install` | Install packages | `-n`, `-c`, `--file` | `conda install numpy pandas` |
| `conda remove` | Remove packages/environments | `-n`, `--all` | `conda remove -n myenv --all` |
| `conda list` | List installed packages | `-n`, `--export` | `conda list -n myenv` |
| `conda env list` | List all environments | none | `conda env list` |
| `conda update` | Update packages/conda | `-n`, `--all` | `conda update --all` |
| `conda search` | Search for packages | `-c`, `--info` | `conda search scipy` |
| `conda info` | Display system information | `--envs`, `--system` | `conda info --envs` |
| `conda clean` | Remove unused packages/cache | `--all`, `--packages` | `conda clean --all` |
| `conda export` | Export environment | `--file`, `-n` | `conda env export > env.yml` |
| `conda env create` | Create from YAML file | `-f`, `-n` | `conda env create -f env.yml` |

---

## Detailed Command Breakdown

### `conda create`
**Purpose**: Create a new conda environment

**Parameters**:
- `-n, --name`: Name of the environment
  - Example: `-n myproject`
- `-c, --channel`: Additional channel to search for packages
  - Example: `-c conda-forge`
- `--file`: Create environment from requirements file
  - Example: `--file requirements.txt`
- `-y, --yes`: Do not ask for confirmation
  - Example: `-y`
- `--clone`: Create environment as copy of existing one
  - Example: `--clone base`

**Examples**:
```bash
# Basic environment with Python
conda create -n myenv python=3.9

# Environment with specific packages
conda create -n dataenv python=3.9 numpy pandas matplotlib

# From requirements.txt
conda create -n reqenv --file requirements.txt

# From conda-forge channel
conda create -n forgeenv -c conda-forge python=3.10 scikit-learn

# Clone existing environment
conda create -n newenv --clone myenv
```

### `conda activate`
**Purpose**: Activate a conda environment

**Parameters**:
- Environment name (positional argument)
  - Example: `myenv`

**Examples**:
```bash
# Activate named environment
conda activate myenv

# Activate base environment
conda activate base
```

### `conda deactivate`
**Purpose**: Deactivate the current environment

**Parameters**: None

**Examples**:
```bash
# Deactivate current environment
conda deactivate
```

### `conda install`
**Purpose**: Install packages in current or specified environment

**Parameters**:
- `-n, --name`: Target environment name
  - Example: `-n myenv`
- `-c, --channel`: Additional channel to search
  - Example: `-c conda-forge`
- `--file`: Install from requirements file
  - Example: `--file requirements.txt`
- `-y, --yes`: Do not ask for confirmation
  - Example: `-y`
- `--update-deps`: Update dependencies
  - Example: `--update-deps`

**Examples**:
```bash
# Install single package
conda install numpy

# Install multiple packages
conda install numpy pandas matplotlib

# Install in specific environment
conda install -n myenv scipy

# Install from conda-forge
conda install -c conda-forge seaborn

# Install from requirements.txt
conda install --file requirements.txt

# Install specific version
conda install python=3.9.5
```

### `conda remove`
**Purpose**: Remove packages or entire environments

**Parameters**:
- `-n, --name`: Target environment name
  - Example: `-n myenv`
- `--all`: Remove entire environment
  - Example: `--all`
- `-y, --yes`: Do not ask for confirmation
  - Example: `-y`

**Examples**:
```bash
# Remove package from current environment
conda remove numpy

# Remove package from specific environment
conda remove -n myenv pandas

# Remove entire environment
conda remove -n myenv --all

# Remove multiple packages
conda remove numpy scipy matplotlib
```

### `conda list`
**Purpose**: List installed packages in environment

**Parameters**:
- `-n, --name`: Target environment name
  - Example: `-n myenv`
- `--export`: Format suitable for requirements.txt
  - Example: `--export`
- `--json`: Output in JSON format
  - Example: `--json`
- `--explicit`: List explicit URLs
  - Example: `--explicit`

**Examples**:
```bash
# List packages in current environment
conda list

# List packages in specific environment
conda list -n myenv

# Export format for requirements
conda list --export > requirements.txt

# Search for specific package
conda list numpy
```

### `conda env list`
**Purpose**: List all conda environments

**Parameters**:
- `--json`: Output in JSON format
  - Example: `--json`

**Examples**:
```bash
# List all environments
conda env list

# Alternative command
conda info --envs
```

### `conda update`
**Purpose**: Update packages or conda itself

**Parameters**:
- `-n, --name`: Target environment name
  - Example: `-n myenv`
- `--all`: Update all packages
  - Example: `--all`
- `-c, --channel`: Additional channel
  - Example: `-c conda-forge`
- `-y, --yes`: Do not ask for confirmation
  - Example: `-y`

**Examples**:
```bash
# Update conda itself
conda update conda

# Update all packages in current environment
conda update --all

# Update specific package
conda update numpy

# Update in specific environment
conda update -n myenv --all
```

### `conda search`
**Purpose**: Search for packages in repositories

**Parameters**:
- `-c, --channel`: Search in specific channel
  - Example: `-c conda-forge`
- `--info`: Show detailed package information
  - Example: `--info`
- `--json`: Output in JSON format
  - Example: `--json`

**Examples**:
```bash
# Search for package
conda search tensorflow

# Search in specific channel
conda search -c conda-forge plotly

# Get detailed info
conda search --info numpy

# Search for specific version
conda search "python>=3.8"
```

### `conda info`
**Purpose**: Display conda system information

**Parameters**:
- `--envs`: List environments
  - Example: `--envs`
- `--system`: Show system information
  - Example: `--system`
- `--json`: Output in JSON format
  - Example: `--json`

**Examples**:
```bash
# General conda info
conda info

# List environments
conda info --envs

# System information
conda info --system

# Info about specific package
conda info numpy
```

### `conda clean`
**Purpose**: Remove unused packages and cache

**Parameters**:
- `--all`: Remove all unused cached packages
  - Example: `--all`
- `--packages`: Remove unused cached packages
  - Example: `--packages`
- `--tarballs`: Remove cached package tarballs
  - Example: `--tarballs`
- `--index-cache`: Remove index cache
  - Example: `--index-cache`
- `-y, --yes`: Do not ask for confirmation
  - Example: `-y`

**Examples**:
```bash
# Clean everything
conda clean --all

# Clean only packages
conda clean --packages

# Clean without confirmation
conda clean --all -y
```

### `conda env export`
**Purpose**: Export environment configuration to YAML file

**Parameters**:
- `-n, --name`: Source environment name
  - Example: `-n myenv`
- `-f, --file`: Output file name
  - Example: `-f environment.yml`
- `--no-builds`: Exclude build strings
  - Example: `--no-builds`
- `--from-history`: Only packages explicitly installed
  - Example: `--from-history`

**Examples**:
```bash
# Export current environment
conda env export > environment.yml

# Export specific environment
conda env export -n myenv -f myenv.yml

# Export without build strings
conda env export --no-builds > environment.yml

# Export only explicitly installed packages
conda env export --from-history > environment.yml
```

### `conda env create`
**Purpose**: Create environment from YAML configuration file

**Parameters**:
- `-f, --file`: YAML file path
  - Example: `-f environment.yml`
- `-n, --name`: Override environment name
  - Example: `-n newname`
- `--force`: Force creation if environment exists
  - Example: `--force`

**Examples**:
```bash
# Create from YAML file
conda env create -f environment.yml

# Create with different name
conda env create -f environment.yml -n mynewenv

# Force recreate existing environment
conda env create -f environment.yml --force
```

## Working with Requirements.txt

### Creating Environment from requirements.txt
```bash
# Method 1: During environment creation
conda create -n myenv --file requirements.txt

# Method 2: Create environment first, then install
conda create -n myenv python=3.9
conda activate myenv
conda install --file requirements.txt

# Method 3: Using pip within conda environment
conda create -n myenv python=3.9
conda activate myenv
pip install -r requirements.txt
```

### Generating requirements.txt from Conda Environment
```bash
# Export conda packages to requirements format
conda list --export > requirements.txt

# Export pip packages only
pip freeze > requirements.txt

# Export environment to YAML (recommended for conda)
conda env export > environment.yml
```

## Pro Tips

### Environment Management Best Practices
```bash
# Always work in named environments (not base)
conda create -n project_name python=3.9

# Keep base environment minimal
conda activate base
conda update conda

# Use environment.yml for complex projects
conda env export --from-history > environment.yml
```

### Channel Management
```bash
# Add conda-forge as default channel
conda config --add channels conda-forge

# Set channel priority
conda config --set channel_priority strict

# Show current configuration
conda config --show
```

### Performance Tips
```bash
# Use mamba for faster package resolution
conda install mamba -c conda-forge
mamba install package_name

# Clean regularly to save disk space
conda clean --all

# Use explicit package versions for reproducibility
conda install numpy=1.21.0 pandas=1.3.0
```
