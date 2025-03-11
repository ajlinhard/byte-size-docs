
---
# Python Project Elements, Structure, and Best Practices

In Python projects, there quite a few elements, structures, and mechanics at play. Some options are interchangable or more modern implementation of the same thing. For example, pytest.ini vs pytest configs in a project toml file. This walkthrough covers different python project mechanics.

## Sections
- **[Building Packages/Apps](#Building-PackagesApps)**
    - [Using a setuptools via setup.py (traditional method)](#Using-a-setuppy)
    - [Using pyproject.toml (modern standard)]
    - [Using Poetry]
    - Package Elements
        - __init__.py files
        - importing
            - into other modules
            - into unit test scripts
- **[Installing Packages/Apps](#Installing-PackagesApps)**
    - [Using pip install package](##Using-pip-install-package)
    - [Using Conda]
    - [Using pipene]
    - [Using Poetry]
- **[Running a Application/Elements](#Running a ApplicationElements)**
    - [Using an app.py](#Using-an-apppy)
    - [Running Unit Test](#Running Unit Test)

---
# Building Packages/Apps
## **Using a setup.py**

- **Purpose**: This file is used for packaging and distributing Python projects. It defines the metadata and dependencies of the project, allowing it to be installed or shared with others.
- **Key Features**:
    - Specifies package name, version, author, description, dependencies, etc.
    - Used with tools like `setuptools` to build (`python setup.py build`) or install (`python setup.py install`) the package.
    - Helps in creating distributable formats like `.tar.gz` or `.whl` for upload to PyPI.
- **Example**:

```python
from setuptools import setup, find_packages

setup(
    name='example_project',
    version='0.1.0',
    packages=find_packages(),
    install_requires=['flask'],  # Dependencies
)
```

- **Usage Context**: Primarily for library or package developers who want to distribute their code[^1][^3][^5].

---
### **3. __init__.py**

- **Purpose**: This file designates a directory as a Python package and allows for initialization code to run when the package is imported.
- **Key Features**:
    - Can be empty or contain code to initialize the package (e.g., setting up imports or configurations).
    - Enables relative imports within a package.
- **Example**:

```python
# Inside __init__.py
from .module1 import function1
from .module2 import function2
```

- **Usage Context**: Found in directories that are part of a Python package. It helps organize code into reusable modules and submodules[^6][^7].

---
# Installing Packages/Apps
There are several ways to install and build Python packages:

## Using pip install package

1. **Using pip** (Python's package installer):
   ```bash
   pip install package-name
   ```

2. **From a requirements file**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Directly from GitHub or other VCS**:
   ```bash
   pip install git+https://github.com/user/repository.git
   ```

4. **From local source**:
   ```bash
   pip install .  # Install from current directory
   pip install /path/to/package
   ```

5. **Using conda** (for Anaconda distributions):
   ```bash
   conda install package-name
   ```

6. **Using pipenv** for dependency management:
   ```bash
   pipenv install package-name
   ```

7. **Using poetry** for dependency management:
   ```bash
   poetry add package-name
   ```

---
# Running a Application/Elements

## **Using an app.py**

- **Purpose**: This file typically serves as the entry point for a Python application, especially in web development projects using frameworks like Flask.
- **Key Features**:
    - Contains the main logic of the application, such as route definitions and application configuration.
    - Often includes the `if __name__ == '__main__':` block to run the app when executed directly.
- **Example in Flask**:

```python
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Hello, World!"

if __name__ == '__main__':
    app.run(debug=True)
```

- **Usage Context**: Used in web applications or scripts where a single file manages the core logic or serves as the main entry point[^2][^4][^6].

## **Running Unit Test**
---
<div style="text-align: center">⁂</div>

[^1]: https://stackoverflow.com/questions/1471994/what-is-setup-py
[^2]: https://www.ramotion.com/blog/web-development-in-python/
[^3]: https://xebia.com/blog/a-practical-guide-to-using-setup-py/
[^4]: https://realpython.com/python-web-applications/
[^5]: https://packaging.python.org/guides/distributing-packages-using-setuptools/
[^6]: https://dev.to/nicholaswinst14/the-power-of-python-for-web-development-a-deep-dive-1dha
[^7]: https://packaging.python.org/tutorials/packaging-projects/
[^8]: https://www.python.org/about/apps/

