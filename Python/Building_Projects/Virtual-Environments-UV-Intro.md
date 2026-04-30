## Setting Up and Using a UV Python Virtual Environment

**uv** is a fast Python package manager (written in Rust) that can manage virtual environments. Here's how to get started:

---

### 1. Install uv

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or via pip
pip install uv
```

---

### 2. Create a Virtual Environment

```bash
# Create a .venv in the current directory
uv venv

# Specify a custom name/path
uv venv my-env

# Use a specific Python version
uv venv --python 3.11
```

---

### 3. Activate the Environment

```bash
# macOS/Linux
source .venv/bin/activate

# Windows (CMD)
.venv\Scripts\activate.bat

# Windows (PowerShell)
.venv\Scripts\Activate.ps1
```

---

### 4. Install Packages

```bash
# Install a package (uv automatically uses the active venv)
uv pip install requests

# Install from a requirements file
uv pip install -r requirements.txt

# Install in editable mode (for local packages)
uv pip install -e .
```

---

### 5. Common Commands

| Command | Description |
|---|---|
| `uv pip list` | List installed packages |
| `uv pip freeze` | Output installed packages (requirements format) |
| `uv pip uninstall <pkg>` | Remove a package |
| `uv pip show <pkg>` | Show package details |
| `deactivate` | Exit the virtual environment |

---

### 6. Project Workflow (Recommended)

uv also supports a higher-level project workflow similar to `poetry` or `pipenv`:

```bash
# Initialize a new project (creates pyproject.toml)
uv init my-project
cd my-project

# Add dependencies (auto-manages the venv)
uv add requests pandas

# Remove a dependency
uv remove requests

# Run a script inside the managed environment
uv run python main.py

# Sync the environment to match pyproject.toml/uv.lock
uv sync
```

This approach is cleaner for projects since uv manages the venv for you and generates a `uv.lock` lockfile for reproducible installs.

---

### Key Advantages of uv

- **Speed** — 10–100x faster than pip for installs
- **Drop-in replacement** — `uv pip` commands mirror `pip` exactly
- **Built-in venv management** — no need for `virtualenv` separately
- **Lockfile support** — reproducible environments out of the box
