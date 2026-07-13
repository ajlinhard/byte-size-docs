# Setting Environment Variables with `venv` and `uv`

There are a few approaches depending on your needs:

---

## Method 1: Using `.env` Files (Recommended)

### **Setup for Both `venv` and `uv`**

1. **Create a `.env` file in your project root:**

```
API_KEY=your_api_key_here
DATABASE_URL=postgresql://user:password@localhost/dbname
DEBUG=True
SECRET_KEY=your_secret_key
```

2. **Install `python-dotenv`:**

```bash
# With venv (after activation)
pip install python-dotenv

# With uv
uv pip install python-dotenv
```

3. **Load variables in your Python code:**

```python
from dotenv import load_dotenv
import os

# Load .env file
load_dotenv()

# Access variables
api_key = os.getenv("API_KEY")
database_url = os.getenv("DATABASE_URL")
debug = os.getenv("DEBUG") == "True"

print(f"API Key: {api_key}")
print(f"Database: {database_url}")
```

4. **Add `.env` to `.gitignore` so secrets aren't committed:**

```
.env
.venv
__pycache__/
*.pyc
```

---

## Method 2: Activation Scripts (System-Level Environment Variables)

### **For `venv` on macOS/Linux:**

Create `my_env/bin/activate.local` (custom activation script):

```bash
export API_KEY="your_api_key"
export DATABASE_URL="postgresql://user:password@localhost/dbname"
export DEBUG="True"
```

Then activate normally:
```bash
source my_env/bin/activate
# Variables are now available globally in your shell
```

### **For `venv` on Windows:**

Create `my_env\Scripts\activate.bat`:

```batch
@echo off
set API_KEY=your_api_key
set DATABASE_URL=postgresql://user:password@localhost/dbname
set DEBUG=True
```

Then activate:
```powershell
my_env\Scripts\activate
```

### **For `uv`:**

After creating `.venv`, use the same approach:

```bash
# On macOS/Linux
echo 'export API_KEY="your_api_key"' >> .venv/bin/activate

# On Windows
echo set API_KEY=your_api_key >> .venv\Scripts\activate.bat
```

---

## Method 3: Using `uv` with `pyproject.toml`

`uv` can manage environment variables via configuration:

1. **Create `pyproject.toml`:**

```toml
[project]
name = "my_project"
version = "0.1.0"

[tool.uv]
# Environment variables for this project
env = {
    "API_KEY" = "your_api_key",
    "DATABASE_URL" = "postgresql://user:password@localhost/dbname",
    "DEBUG" = "true"
}
```

2. **Load in your Python code:**

```python
import os

api_key = os.getenv("API_KEY")
```

---

## Method 4: Command-Line (One-Off Variables)

### **Set variable before running:**

**macOS/Linux:**
```bash
API_KEY=your_key python your_script.py
```

**Windows:**
```powershell
$env:API_KEY="your_key"; python your_script.py
```

---

## Full Example Project Structure

```
my_project/
├── .env                 # Store secrets here (add to .gitignore)
├── .gitignore          # Exclude .env from git
├── pyproject.toml      # Project config
├── requirements.txt    # Dependencies
├── main.py             # Your Python script
└── .venv/              # Virtual environment
```

**main.py:**
```python
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("API_KEY")
db_url = os.getenv("DATABASE_URL")

print(f"Connected to: {db_url}")
print(f"Using API: {api_key}")
```

**requirements.txt:**
```
python-dotenv==1.0.0
requests==2.31.0
```

**Setup:**
```bash
# Create venv
python -m venv .venv
source .venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Run your app
python main.py
```

---

## Best Practices

✅ **Do:**
- Use `.env` for local development
- Add `.env` to `.gitignore`
- Use `os.getenv("KEY", "default_value")` for optional variables
- Use different `.env` files for different environments (`.env.local`, `.env.prod`)

❌ **Don't:**
- Commit `.env` files with secrets
- Hardcode API keys in your code
- Use the same secrets across environments

---

**Which method do you prefer?** I'd recommend **Method 1 (.env files)** for most projects—it's simple, secure, and works with both `venv` and `uv`.
