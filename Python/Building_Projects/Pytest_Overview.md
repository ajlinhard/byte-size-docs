
---
# pytest

pytest is a powerful testing framework for Python.

## Documentation
1. [Official Documentation](https://docs.pytest.org/en/7.1.x/contents.html)
    - [Pytest API](https://docs.pytest.org/en/stable/reference/reference.html#)
2. Integration
    - [Pytest Official Good Intg. Practices](https://docs.pytest.org/en/stable/explanation/goodpractices.html)
    - [Pytest with Eric (blog)](https://pytest-with-eric.com/pytest-best-practices/pytest-ini/)
    - [Pytest with Eric pytest.ini (blog)](https://pytest-with-eric.com/introduction/pytest-pythonpath/#Project-Set-Up)
3. Running Pytest
    - [How to Invoke Pytest](https://docs.pytest.org/en/stable/how-to/usage.html)
    - [Running non-python test](https://docs.pytest.org/en/stable/example/nonpython.html)

### Use Cases
- Writing and running unit tests, integration tests, and functional tests
- Automating test discovery and execution

### Pros
- Concise and readable syntax for writing tests[^1][^3]
- Powerful features like fixtures for test setup and teardown[^1][^3]
- Extensive plugin support for customization[^1][^3]
- Detailed output for easier debugging[^3]

### Cons
- Requires external installation (not part of Python standard library)[^3]
- Learning curve for advanced features[^3]


## pytest-cov

pytest-cov is a plugin for pytest that adds code coverage measurement capabilities.

### Use Cases

- Measuring code coverage during test execution
- Generating coverage reports

### Pros

- Integrates seamlessly with pytest
- Supports subprocess coverage measurement[^4]
- Compatible with pytest-xdist for distributed testing[^4]

### Cons

- Requires additional setup and configuration
- May slightly increase test execution time due to coverage measurement

---
# Pytest Help

## Structuring Test Folder in a Project
Depending on your python project structure your unit test folder may live outside the package code folder. If this case arises, the you can use one of 3 methods.
**Note: All 3 methods are focuesed on adjusting or adding the PYTHONPATH to the sys.path/PYTHON import mechanism. [info here](https://docs.pytest.org/en/7.1.x/explanation/pythonpath.html)**

### 1. pytest.ini file (older but still valid approach)
```bash
[pytest]
python_paths = ./
               ./src/Book_API
```
**example project uses:**
- https://github.com/ajlinhard/DragonRegen/blob/main/pytest.ini.block

#### Reason it is considered an old method
The latest version of pytest-pythonpath is 0.7.4, which was released in March 2021. This package hasn't been updated in over 3 years, which raises some concerns about its ongoing support and maintenance.

Since pytest 7.0.0+ now has built-in support for modifying the Python path through the `pythonpath` option in the pytest.ini configuration or the `tool.pytest.ini_options` section in pyproject.toml, many users have moved away from using pytest-pythonpath.

If you're using a recent version of pytest (7.0.0 or newer), it's generally recommended to use the built-in functionality rather than this plugin:

```toml
[tool.pytest.ini_options]
pythonpath = ["src", "src/Book_API"]
```

Or in pytest.ini:
```ini
[pytest]
pythonpath = src src/Book_API
```

This built-in approach is more future-proof than relying on a plugin that may not be actively maintained.

### 2. pyproject.toml setting (modern method)
This method allows for the construction and adjustments of the unit testing in the same file as other python project settings. The syntax is similar to the pytest.ini file. However, note the file host more functionalities for your project outside of unit testing. Unlike the pytest.ini. See [Python Project pyproject toml](Python\Python Project Elements Structure and Best Practices.md) for more info, or [Pythons offical project file documentation](https://packaging.python.org/en/latest/tutorials/packaging-projects/#creating-the-package-files).
```toml
[tool.pytest.ini_options]
python_paths = [
    ".",
    "src",
    "src/Book_API"
]
```
After you build your toml file, remember to install you package into your enviornment via pip:
```bash
conda activate Your-Env
cd /To/Your/Project/Root
pip install -e .
```
**example project uses:**
- https://github.com/ajlinhard/DragonRegen/blob/main/pyproject.toml

### 3. conftest.py
The conftest.py file in pytest allows you to configure and customize your test environment by defining fixtures, hooks, and other settings that apply across multiple test files within a directory. Below is an overview of how to use it to adjust pytest settings effectively:

```python
# conftest.py
import pytest

def pytest_addoption(parser):
    parser.addoption("--custom-option", action="store", default="default_value", help="Custom option description")

@pytest.fixture
def custom_option(request):
    return request.config.getoption("--custom-option")
```
---
<div style="text-align: center">⁂</div>

[^3]: https://www.softwaretestingstuff.com/unittest-vs-pytest/
[^4]: https://pypi.org/project/pytest-cov/
[^10]: https://www.j-labs.pl/en/tech-blog/pytest-why-its-more-popular-than-unittest/
[^11]: https://www.askpython.com/python/examples/flake8-python
[^12]: https://dzone.com/articles/10-awesome-features-of-pytest
[^15]: https://realpython.com/pytest-python-testing/
[^16]: https://docs.pytest.org/en/stable/contents.html
[^22]: https://pytest-cov.readthedocs.io/en/latest/readme.html
[^48]: https://pytest-with-eric.com/pytest-best-practices/pytest-plugins/

