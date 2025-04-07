
---
# Pytest Overview
---
The pytest is a powerful testing framework for Python with wide spread adoption in the community.

### Pros
- Concise and readable syntax for writing tests[^1][^3]
- Powerful features like fixtures for test setup and teardown[^1][^3]
- Extensive plugin support for customization[^1][^3]
- Detailed output for easier debugging[^3]
-  Automated test detection is built-in.

### Cons
- Requires external installation (not part of Python standard library)[^3]
- Learning curve for advanced features[^3]

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
4. Pytest Alternatives/Comparisions
    - [Pytest vs UnitTest](https://www.softwaretestingstuff.com/unittest-vs-pytest/)

---
# PyTest Plug-ins
---
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
# Structuring Test Folder in a Project
---
## Test Folders
For packages with multiple sub-folders and complex fixture requirements, you'll want a more sophisticated structure. Here's how to organize that effectively:

## Example Hierarchical Project Structure

```
project_root/
├── src/
│   └── mypackage/
│       ├── __init__.py
│       ├── core/
│       │   ├── __init__.py
│       │   ├── module1.py
│       │   └── module2.py
│       ├── services/
│       │   ├── __init__.py
│       │   ├── service1.py
│       │   └── service2.py
│       └── utils/
│           ├── __init__.py
│           └── helpers.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py           # Project-wide fixtures
│   ├── core/
│   │   ├── __init__.py
│   │   ├── conftest.py       # Core-specific fixtures
│   │   ├── test_module1.py
│   │   └── test_module2.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── conftest.py       # Service-specific fixtures
│   │   ├── test_service1.py
│   │   └── test_service2.py
│   └── utils/
│       ├── __init__.py
│       ├── conftest.py       # Utils-specific fixtures
│       └── test_helpers.py
└── pytest.ini
```
# Pytest Fixtures
The pytest fixture is the basis for how many mechanics in the package work. They allow you to isolate setup or repeated code sections, to be used throughout your testing code.

## Scope Options in pytest.fixture

The `scope` parameter in `@pytest.fixture()` can have these values:

- `"function"` (default): The fixture is created for each test function
- `"class"`: Created once per test class
- `"module"`: Created once per test module (file)
- `"package"`: Created once per test package
- `"session"`: Created once for the entire test session

## Other Common pytest.fixture Parameters

- `autouse=True`: Run the fixture automatically without explicit reference
- `params=[...]`: Run the test multiple times with different fixture values
- `ids=[...]`: Custom IDs for parametrized fixture values
- `name="custom_name"`: Override the fixture name

For example:

```python
@pytest.fixture(scope="module", autouse=True, params=["sqlite", "postgres"])
def database(request):
    # Set up database based on request.param
    db = setup_db(request.param)
    yield db
    # Teardown after all tests using this fixture are done
    db.close()
```

The parameters allow you to control exactly how and when your fixtures run, which is a powerful way to optimize your test suite's performance and structure.
### Managing Fixtures at Different Levels

1. **Hierarchical `conftest.py` Files**:
   - Root `tests/conftest.py`: Global fixtures used across all tests
   - Subdirectory `conftest.py`: Fixtures specific to that module/component
   - Pytest automatically discovers and merges fixtures from all relevant `conftest.py` files

2. **Fixture Scoping and Sharing**:
   - Use appropriate scopes (`function`, `class`, `module`, `session`) to control fixture lifecycle
   - Fixtures defined in parent directories are available to tests in subdirectories
   - More specific fixtures in subdirectories can override parent fixtures of the same name

3. **Fixture Organization Strategies**:

   - **By Component**: Create fixtures in the `conftest.py` file closest to where they're needed
   - **By Dependency Level**: 
     - Database connections in root `conftest.py`
     - Service clients in `services/conftest.py`
     - Component-specific mocks in their respective directories

4. **Using Factory Fixtures**:
   ```python
   # In conftest.py
   @pytest.fixture
   def make_user():
       def _make_user(name="default", role="user"):
           return {"name": name, "role": role}
       return _make_user
   ```

5. **Parametrized Fixtures**:
   ```python
   @pytest.fixture(params=["sqlite", "postgres"])
   def db_connection(request):
       if request.param == "sqlite":
           # Setup sqlite
       else:
           # Setup postgres
       yield connection
       # Teardown
   ```

6. **Fixture Inheritance**:
   You can build fixtures that depend on other fixtures to create layers of setup:
   ```python
   @pytest.fixture
   def authenticated_client(client, user_token):
       client.set_token(user_token)
       return client
   ```

For extremely large projects, you might also consider:
- Using pytest plugins for very common fixtures
- Creating fixture libraries in separate modules
- Using markers to categorize tests that need specific fixtures

This structure gives you flexibility while keeping fixtures organized and available where needed, without polluting the global namespace.
---
# conftest.py
---
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

## Pytest Configuration Files
Configuring your python project structure and unit test folder too live outside the package code folder. This is the perferred structure in many cases and you can use one of 3 methods to make the test work seamlessly with your package structure.
**Note: All methods are focuesed on adjusting or adding the PYTHONPATH to the sys.path/PYTHON import mechanism. [info here](https://docs.pytest.org/en/7.1.x/explanation/pythonpath.html)**

### 1. pyproject.toml setting (modern method)
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

### 2. pytest.ini file (older but still valid approach)
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

---
# Example Pytest Scripts
---
I'll provide both a simple and complex example of what a `test_service1.py` file might look like in your hierarchical project structure.

## Simple Example

Here's a straightforward example testing a user service:

```python
# tests/services/test_service1.py

import pytest
from mypackage.services.service1 import UserService

# Simple test using a fixture from the local conftest.py
def test_get_user(mock_user_data):
    # Arrange
    service = UserService(db=mock_user_data)
    user_id = "user123"
    
    # Act
    result = service.get_user(user_id)
    
    # Assert
    assert result is not None
    assert result["id"] == user_id
    assert "name" in result
    assert "email" in result

# Testing an error case
def test_get_nonexistent_user(mock_user_data):
    service = UserService(db=mock_user_data)
    
    with pytest.raises(KeyError):
        service.get_user("nonexistent_id")

# Using parametrized tests for multiple cases
@pytest.mark.parametrize("user_id, expected_name", [
    ("user123", "John Doe"),
    ("user456", "Jane Smith"),
    ("user789", "Bob Johnson")
])
def test_user_names(mock_user_data, user_id, expected_name):
    service = UserService(db=mock_user_data)
    user = service.get_user(user_id)
    
    assert user["name"] == expected_name
```

## Complex Example

Here's a more complex example with multiple fixtures, async testing, and more sophisticated assertions:

```python
# tests/services/test_service1.py

import pytest
import asyncio
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

from mypackage.services.service1 import UserService
from mypackage.core.exceptions import AuthenticationError, RateLimitError

# Using class-based tests to group related tests
class TestUserService:
    
    # Setup method that runs before each test in this class
    def setup_method(self):
        self.logger = MagicMock()
    
    # Using a fixture from the root conftest.py (db_connection)
    # and a fixture from services/conftest.py (user_factory)
    @pytest.mark.usefixtures("db_transaction")
    def test_create_user(self, db_connection, user_factory):
        # Arrange
        service = UserService(db=db_connection, logger=self.logger)
        user_data = user_factory(role="admin")
        
        # Act
        user_id = service.create_user(user_data)
        created_user = service.get_user(user_id)
        
        # Assert
        assert created_user["id"] == user_id
        assert created_user["role"] == "admin"
        assert created_user["created_at"] is not None
        self.logger.info.assert_called_once()

    # Testing async methods
    @pytest.mark.asyncio
    async def test_async_fetch_user_activity(self, db_connection, activity_tracker_mock):
        # Arrange
        service = UserService(db=db_connection, logger=self.logger)
        user_id = "test_user"
        activity_tracker_mock.get_user_activity.return_value = [
            {"type": "login", "timestamp": datetime.now() - timedelta(days=1)},
            {"type": "profile_update", "timestamp": datetime.now() - timedelta(hours=5)}
        ]
        
        # Act
        activities = await service.fetch_user_activity(user_id, days=7)
        
        # Assert
        assert len(activities) == 2
        assert all(isinstance(a["timestamp"], datetime) for a in activities)
        assert activities[0]["type"] == "login"

    # Testing with mocked external dependencies
    @patch("mypackage.services.service1.NotificationClient")
    def test_user_notification(self, mock_notification_client, db_connection, user_factory):
        # Arrange
        mock_client = MagicMock()
        mock_notification_client.return_value = mock_client
        service = UserService(db=db_connection, logger=self.logger)
        user = user_factory(notifications_enabled=True)
        
        # Act
        service.notify_user(user["id"], "Test message")
        
        # Assert
        mock_client.send.assert_called_once_with(
            user["id"], 
            "Test message",
            channel=user.get("preferred_channel", "email")
        )

    # Testing error conditions and retry logic
    @pytest.mark.parametrize("exception,retry_count", [
        (ConnectionError, 3),
        (RateLimitError, 5),
        (AuthenticationError, 1)
    ])
    def test_service_retry_logic(self, exception, retry_count, db_connection, mocker):
        # Arrange
        mock_api = mocker.patch("mypackage.services.service1.ExternalAPI")
        mock_api.get_data.side_effect = [exception] * (retry_count - 1) + [{"data": "success"}]
        service = UserService(db=db_connection, logger=self.logger)
        
        # Act
        result = service.get_external_user_data("user123")
        
        # Assert
        assert result == {"data": "success"}
        assert mock_api.get_data.call_count == retry_count
        assert self.logger.warning.call_count == retry_count - 1

# Testing integration with real components (marked to run selectively)
@pytest.mark.integration
def test_user_service_with_cache(db_connection, redis_cache):
    # Test with actual cache implementation
    service = UserService(db=db_connection, cache=redis_cache)
    user_id = "integration_test_user"
    
    # First call should hit the database
    user1 = service.get_user(user_id)
    # Second call should be from cache
    user2 = service.get_user(user_id)
    
    assert user1 == user2
    assert redis_cache.get.call_count == 1
    assert redis_cache.set.call_count == 1
```

The complex example demonstrates:

1. Class-based test organization
2. Using fixtures from different levels of the conftest hierarchy
3. Testing asynchronous code
4. Mocking external dependencies
5. Parametrized tests for different scenarios
6. Testing retry logic and error handling
7. Integration testing with selective markers
8. Using transaction fixtures for database tests
9. Verifying logging and external service interactions

The fixtures referenced in these examples would be defined in the appropriate `conftest.py` files at different levels of your test hierarchy.
---
**References:**
[^3]: https://www.softwaretestingstuff.com/unittest-vs-pytest/
[^4]: https://pypi.org/project/pytest-cov/
[^10]: https://www.j-labs.pl/en/tech-blog/pytest-why-its-more-popular-than-unittest/
[^11]: https://www.askpython.com/python/examples/flake8-python
[^12]: https://dzone.com/articles/10-awesome-features-of-pytest
[^15]: https://realpython.com/pytest-python-testing/
[^16]: https://docs.pytest.org/en/stable/contents.html
[^22]: https://pytest-cov.readthedocs.io/en/latest/readme.html
[^48]: https://pytest-with-eric.com/pytest-best-practices/pytest-plugins/

