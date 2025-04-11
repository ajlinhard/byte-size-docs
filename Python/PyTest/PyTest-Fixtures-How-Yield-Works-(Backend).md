# How pytest Uses `yield` to Share Fixture Values with Test Functions

Pytest's fixture system with `yield` creates a powerful mechanism for sharing setup values with test functions while ensuring proper cleanup. Let's explore the details of how this works:

## The Internal Mechanics

Under the hood, pytest does something quite clever with generators:

1. **Generator Creation**: When pytest encounters a fixture function with a `yield` statement, it recognizes it as a generator function.

2. **First Execution**: When a test requests this fixture, pytest calls the fixture function, which runs until it reaches the `yield` statement.

3. **Value Capturing**: The value provided to the `yield` statement is captured by pytest.

4. **Value Injection**: This captured value is then passed as an argument to any test function that declares the fixture as a parameter.

5. **Generator Suspension**: The generator (fixture function) is now paused at the `yield` point.

6. **Test Execution**: The test function runs with access to the fixture value.

7. **Generator Resumption**: After the test completes (whether successful or not), pytest resumes the generator to execute the teardown code after the `yield`.

## Detailed Example with Explanation:

```python
import pytest
import psycopg2

@pytest.fixture
def database_connection():
    # Setup phase
    print("Setting up database connection")
    connection = psycopg2.connect(
        dbname="test_db",
        user="test_user",
        password="password",
        host="localhost"
    )
    connection.autocommit = False
    
    # This value is returned to the test function
    yield connection
    
    # Teardown phase - runs after test completes
    print("Tearing down database connection")
    connection.rollback()  # Roll back any uncommitted changes
    connection.close()     # Close the connection

def test_database_operation(database_connection):
    # The database_connection parameter receives the yielded value
    cursor = database_connection.cursor()
    cursor.execute("CREATE TABLE test (id serial PRIMARY KEY, name VARCHAR);")
    cursor.execute("INSERT INTO test (name) VALUES (%s)", ("test_value",))
    
    # Verify operation
    cursor.execute("SELECT name FROM test WHERE name = %s", ("test_value",))
    result = cursor.fetchone()
    assert result[0] == "test_value"
    
    # After this test completes, pytest automatically 
    # resumes the fixture function to run teardown code
```

## The Request Flow:

1. When pytest discovers and prepares to run `test_database_operation`, it notices the function requires a parameter called `database_connection`.

2. It looks for a fixture with that name and finds the `database_connection` fixture function.

3. It executes the fixture function up to the `yield` statement, establishing a database connection.

4. The connection object is captured as the yield value.

5. The test function is called with `database_connection=connection`.

6. After the test function completes (whether by passing, failing, or raising an exception), control returns to the fixture function, which continues execution after the `yield` statement to perform cleanup.

## Scoping and State Preservation:

Pytest maintains the "paused" state of each fixture based on its scope:

```python
@pytest.fixture(scope="function")  # Default scope
def function_fixture():
    # Setup
    resource = create_resource()
    yield resource
    # Teardown - runs after each test function

@pytest.fixture(scope="module")
def module_fixture():
    # Setup
    resource = create_expensive_resource()
    yield resource
    # Teardown - runs once after all tests in the module
```

With different scopes, pytest carefully manages when to resume generator fixtures to perform teardown:

- `function`: After each test function completes
- `class`: After all tests in a class complete
- `module`: After all tests in a module complete
- `package`: After all tests in a package complete
- `session`: After all tests in the session complete

## Behind-the-Scenes Implementation:

Pytest implements this behavior using a technique similar to:

```python
def run_fixture_and_test(fixture_func, test_func):
    # Create the generator
    fixture_gen = fixture_func()
    
    try:
        # Get the value to pass to the test
        fixture_value = next(fixture_gen)
        
        try:
            # Run the test with the fixture value
            test_func(fixture_value)
        finally:
            # Always run teardown, even if test failed
            try:
                next(fixture_gen)  # Resume generator for cleanup
            except StopIteration:
                pass  # Expected when generator is exhausted
    except Exception as e:
        print(f"Error in fixture setup: {e}")
        raise
```

This pattern ensures that fixture teardown code always executes, providing reliable resource cleanup regardless of how tests behave.

The elegance of using `yield` in pytest fixtures is that it keeps the setup and teardown code logically together in the same function while still allowing pytest to run test code in between.
