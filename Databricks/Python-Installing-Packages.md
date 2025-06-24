# Python Installing Packages
If you want to install an additional library of a custom library to Databricks runtime here are your options.

## Method 1: Install from PyPI
If your package is published on PyPI, you can install it directly:
```python
%pip install your-package-name
```

## Method 2: Install from Git Repository
For packages hosted on GitHub or other Git platforms:
```python
%pip install git+https://github.com/username/your-package.git
```

## Method 3: Upload and Install Local Package
For local development packages:

1. **Create your package structure:**
```
my_package/
├── setup.py
├── my_package/
│   ├── __init__.py
│   └── module.py
```

2. **Create setup.py:**
```python
from setuptools import setup, find_packages

setup(
    name="my_package",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        # your dependencies
    ],
)
```

3. **Build the package locally:**
```bash
python setup.py sdist bdist_wheel
```

4. **Upload to Databricks:**
   - Upload the `.whl` file to DBFS using the Databricks UI
   - Or use the Databricks CLI: `databricks fs cp dist/my_package-0.1.0-py3-none-any.whl dbfs:/FileStore/jars/`

5. **Install in your notebook:**
```python
%pip install /dbfs/FileStore/jars/my_package-0.1.0-py3-none-any.whl
```

## Method 4: Direct File Upload (Simple Modules)
For simple single-file modules:

1. Upload your `.py` file to DBFS
2. Add it to the Python path:
```python
import sys
sys.path.append('/dbfs/FileStore/shared_uploads/your_email/')

import your_module
```

## Method 5: Cluster Libraries
For packages needed across multiple notebooks:

1. Go to your cluster configuration
2. Click "Libraries" tab
3. Install new library (PyPI, Maven, DBFS, etc.)
4. Restart cluster

## Method 6: Workspace Files (Databricks Runtime 11.0+)
You can also upload Python files directly to your workspace and import them:

1. Upload `.py` files to your workspace
2. Import using relative paths:
```python
from .my_module import my_function
```

The `%pip install` approach (Methods 1-3) is generally recommended as it properly handles dependencies and integrates well with Databricks' package management system.
