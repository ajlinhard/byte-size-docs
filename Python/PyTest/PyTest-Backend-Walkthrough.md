# Pytest Backend Walkthrough
How is PyTest processing fixtures and passing parameters to found test functions behind the scenes. When you execute pytest runs, the first step is scanning all the files in the folders pulling out conftest.py at each level, pulling in test files, parsing for "test_" functions. But then how does the actual fixtures (scope, params, etc) and passing of the fixtures + parameters work? The main thing to remmeber is pytest is an application which is executing, not just a static set of classes. We will start with fixtures and move towards the executor of pytest passing the values. This is a simplified version of how pytest works, NOT the actual code! You can look through that on your own.

---
# How is PyTest caching the yield and return values of fixtires?

The caching happens in pytest's internal `FixtureManager` and `FixtureRequest` classes. Here's how it works under the hood with example code:

## Pytest's Internal Caching Mechanism

**Core Cache Structure**
```python
# Simplified version of pytest's internal caching
class FixtureCache:
    def __init__(self):
        # The main cache - maps (argname, scope, param_index) -> cached_result
        self._cache = {}
        # Tracks active fixtures for proper teardown ordering
        self._active_fixtures = {}
    
    def get_cache_key(self, argname, scope, param_index=None):
        """Generate cache key for fixture"""
        return (argname, scope, param_index)
    
    def get_cached_result(self, argname, scope, param_index=None):
        """Retrieve cached fixture result"""
        cache_key = self.get_cache_key(argname, scope, param_index)
        return self._cache.get(cache_key)
    
    def cache_result(self, argname, scope, result, param_index=None):
        """Store fixture result in cache"""
        cache_key = self.get_cache_key(argname, scope, param_index)
        self._cache[cache_key] = result
        
        # Track for teardown
        if scope not in self._active_fixtures:
            self._active_fixtures[scope] = []
        self._active_fixtures[scope].append((cache_key, result))
```

**Fixture Resolution Process**
```python
class FixtureRequest:
    def __init__(self):
        self.fixture_cache = FixtureCache()
        self.scope_hierarchy = ['function', 'class', 'module', 'package', 'session']
    
    def get_fixture_value(self, argname, scope='function'):
        """Main fixture resolution method"""
        # 1. Check if already cached
        cached_result = self.fixture_cache.get_cached_result(argname, scope)
        if cached_result is not None:
            print(f"Cache HIT for {argname} (scope: {scope})")
            return cached_result
        
        print(f"Cache MISS for {argname} (scope: {scope}) - creating new instance")
        
        # 2. Execute fixture function
        fixture_func = self._get_fixture_function(argname)
        
        # 3. Handle generator fixtures (with yield)
        if self._is_generator_fixture(fixture_func):
            generator = fixture_func()
            result = next(generator)  # Get the yielded value
            
            # Store both the result AND the generator for later teardown
            self.fixture_cache.cache_result(argname, scope, {
                'value': result,
                'generator': generator,
                'executed': True
            })
            return result
        else:
            # 4. Handle regular fixtures
            result = fixture_func()
            self.fixture_cache.cache_result(argname, scope, {
                'value': result,
                'generator': None,
                'executed': True
            })
            return result
```

**Real Example Demonstrating Caching**
```python
# Example showing how the cache works in practice
cache = FixtureCache()

# Simulate session-scoped database fixture
def create_database_fixture():
    print("🔧 Creating expensive database connection...")
    return {"connection": "db_conn_12345", "queries_run": 0}

# First test requests the fixture
def test_user_creation():
    fixture_name = "database"
    scope = "session"
    
    # Check cache first
    cached = cache.get_cached_result(fixture_name, scope)
    if cached is None:
        # Cache miss - create new fixture
        db = create_database_fixture()
        cache.cache_result(fixture_name, scope, {
            'value': db,
            'generator': None,
            'executed': True
        })
        print("✅ Cached database fixture")
    else:
        db = cached['value']
        print("♻️  Retrieved database from cache")
    
    # Use the fixture
    db["queries_run"] += 1
    print(f"Database state: {db}")

# Second test requests same fixture
def test_user_deletion():
    fixture_name = "database"
    scope = "session"
    
    # This will be a cache hit
    cached = cache.get_cached_result(fixture_name, scope)
    if cached is None:
        db = create_database_fixture()
        cache.cache_result(fixture_name, scope, {
            'value': db,
            'generator': None,
            'executed': True
        })
    else:
        db = cached['value']
        print("♻️  Retrieved database from cache")
    
    # Notice the state persisted from previous test!
    db["queries_run"] += 1
    print(f"Database state: {db}")

# Run the simulation
print("=== Test Session Start ===")
test_user_creation()
print()
test_user_deletion()
print("=== Test Session End ===")
```

**Output:**
```
=== Test Session Start ===
🔧 Creating expensive database connection...
✅ Cached database fixture
Database state: {'connection': 'db_conn_12345', 'queries_run': 1}

♻️  Retrieved database from cache
Database state: {'connection': 'db_conn_12345', 'queries_run': 2}
=== Test Session End ===
```

**Cache with Teardown Handling**
```python
class AdvancedFixtureCache:
    def __init__(self):
        self._cache = {}
        self._teardown_stack = []  # LIFO for proper cleanup order
    
    def execute_fixture_with_teardown(self, argname, scope, fixture_func):
        cache_key = (argname, scope)
        
        if cache_key in self._cache:
            return self._cache[cache_key]['value']
        
        # Execute generator fixture
        generator = fixture_func()
        yielded_value = next(generator)
        
        # Cache the result
        self._cache[cache_key] = {
            'value': yielded_value,
            'generator': generator,
            'scope': scope
        }
        
        # Register for teardown
        self._teardown_stack.append((cache_key, generator))
        
        return yielded_value
    
    def teardown_fixtures(self, scope):
        """Execute teardown for fixtures of given scope"""
        remaining = []
        for cache_key, generator in reversed(self._teardown_stack):
            cached_scope = self._cache[cache_key]['scope']
            if cached_scope == scope:
                try:
                    next(generator)  # This runs the teardown code after yield
                except StopIteration:
                    pass  # Expected - generator is exhausted
                print(f"🧹 Tore down fixture: {cache_key[0]}")
            else:
                remaining.append((cache_key, generator))
        self._teardown_stack = list(reversed(remaining))
```

The key points:
- **Memory-based**: Everything lives in Python dictionaries/objects in the pytest process
- **Scope-aware**: Cache keys include scope information
- **Generator handling**: Special logic for yield-based fixtures to handle setup/teardown
- **Teardown tracking**: Maintains references to generators for proper cleanup
- **State persistence**: Objects remain in memory with all their mutations until teardown

This is why session-scoped fixtures can accidentally create test interdependencies - they're literally the same Python object instance shared across all tests!

---
# For cached values in fixtures how is the scope factored in?

Yes! Pytest's internal machinery determines exactly when to return cached values vs. create new ones based on **scope boundaries**. Here's how it works for each scope:

## Scope-Based Cache Management

```python
class ScopeAwareFixtureCache:
    def __init__(self):
        self._cache = {}
        self._scope_contexts = {
            'session': None,      # Lives for entire test run
            'package': {},        # One per package
            'module': {},         # One per test file
            'class': {},          # One per test class
            'function': {}        # New for each test function
        }
        self._active_scopes = set()
    
    def should_create_new_fixture(self, argname, scope, current_context):
        """Determine if we need a new fixture instance"""
        cache_key = self._get_cache_key(argname, scope, current_context)
        
        # Check if we have a cached version
        if cache_key not in self._cache:
            return True  # No cached version exists
        
        # Check if the scope boundary has been crossed
        return self._scope_boundary_crossed(scope, current_context)
    
    def _scope_boundary_crossed(self, scope, current_context):
        """Check if we've moved to a new scope context"""
        if scope == 'session':
            return False  # Session scope never crosses boundaries
        elif scope == 'module':
            return current_context['module'] != self._last_module
        elif scope == 'class':
            return current_context['class'] != self._last_class  
        elif scope == 'function':
            return True  # Always create new for function scope
        return False
```

## Real Examples by Scope

**1. Session Scope - Lives Entire Test Run**
```python
@pytest.fixture(scope="session")
def database_connection():
    print("🔧 Creating DB connection (session)")
    conn = {"id": "session_conn", "queries": 0}
    yield conn
    print("🧹 Closing DB connection (session)")

# This fixture is created ONCE and reused across ALL tests
# test_file1.py::test_a -> Cache MISS, create fixture
# test_file1.py::test_b -> Cache HIT, reuse same object
# test_file2.py::test_c -> Cache HIT, reuse same object  
# test_file2.py::test_d -> Cache HIT, reuse same object
# Only at very end: teardown runs
```

**2. Module Scope - New Per Test File**
```python
@pytest.fixture(scope="module") 
def api_client():
    print(f"🔧 Creating API client for module")
    client = {"module": "current", "requests": 0}
    yield client
    print(f"🧹 Tearing down API client for module")

# Pytest's internal logic:
# test_users.py::test_create_user -> Cache MISS, create new
# test_users.py::test_delete_user -> Cache HIT, reuse
# test_orders.py::test_create_order -> Cache MISS, create NEW (different module!)
# test_orders.py::test_cancel_order -> Cache HIT, reuse
```

**3. Class Scope - New Per Test Class**
```python
@pytest.fixture(scope="class")
def temp_directory():
    print("🔧 Creating temp directory for class")
    import tempfile
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    print("🧹 Cleaning up temp directory")

class TestFileOperations:
    def test_create_file(self, temp_directory):  # Cache MISS - creates fixture
        pass
    def test_read_file(self, temp_directory):    # Cache HIT - reuses same dir
        pass

class TestImageProcessing:
    def test_resize_image(self, temp_directory): # Cache MISS - NEW class, new fixture!
        pass
```

**4. Function Scope - New Every Test**
```python
@pytest.fixture(scope="function")  # Default scope
def user_data():
    print("🔧 Creating fresh user data")
    data = {"name": "test_user", "email": "test@example.com"}
    yield data
    print("🧹 Cleaning up user data")

def test_user_creation(user_data):     # Cache MISS - new fixture created
    pass

def test_user_validation(user_data):   # Cache MISS - new fixture created again!
    pass
```

## Pytest's Internal Decision Tree

```python
class FixtureResolver:
    def resolve_fixture(self, argname, scope, current_test_context):
        """Pytest's internal fixture resolution logic"""
        
        # Step 1: Generate cache key based on scope
        cache_key = self._generate_cache_key(argname, scope, current_test_context)
        
        # Step 2: Check if cached version exists and is still valid
        if cache_key in self._cache:
            cached_fixture = self._cache[cache_key]
            
            # Step 3: Validate scope boundaries
            if self._is_cache_valid_for_scope(cached_fixture, scope, current_test_context):
                print(f"♻️  REUSING {argname} (scope: {scope})")
                return cached_fixture['value']
            else:
                print(f"🔄 SCOPE BOUNDARY CROSSED for {argname} - invalidating cache")
                self._teardown_fixture(cached_fixture)
        
        # Step 4: Create new fixture instance
        print(f"🆕 CREATING NEW {argname} (scope: {scope})")
        return self._create_and_cache_fixture(argname, scope, current_test_context)
    
    def _is_cache_valid_for_scope(self, cached_fixture, scope, current_context):
        """Check if cached fixture is still valid for current scope"""
        if scope == 'session':
            return True  # Always valid until session ends
        elif scope == 'module':
            return cached_fixture['module_id'] == current_context['module_id']
        elif scope == 'class':
            return (cached_fixture['module_id'] == current_context['module_id'] and
                   cached_fixture['class_id'] == current_context['class_id'])
        elif scope == 'function':
            return False  # Never cache function-scoped fixtures
        return False
```

## Practical Example Showing All Scopes

```python
# test_example.py
import pytest

@pytest.fixture(scope="session")
def session_fixture():
    print("🌍 SESSION: Creating")
    yield "session_data"
    print("🌍 SESSION: Teardown")

@pytest.fixture(scope="module") 
def module_fixture():
    print("📁 MODULE: Creating")
    yield "module_data"
    print("📁 MODULE: Teardown")

@pytest.fixture(scope="class")
def class_fixture():
    print("🏫 CLASS: Creating") 
    yield "class_data"
    print("🏫 CLASS: Teardown")

@pytest.fixture(scope="function")
def function_fixture():
    print("⚡ FUNCTION: Creating")
    yield "function_data" 
    print("⚡ FUNCTION: Teardown")

class TestGroup1:
    def test_1(self, session_fixture, module_fixture, class_fixture, function_fixture):
        pass
    
    def test_2(self, session_fixture, module_fixture, class_fixture, function_fixture):
        pass

class TestGroup2:
    def test_3(self, session_fixture, module_fixture, class_fixture, function_fixture):
        pass
```

**Output shows pytest's caching decisions:**
```
🌍 SESSION: Creating     # Created once
📁 MODULE: Creating      # Created once  
🏫 CLASS: Creating       # Created for TestGroup1
⚡ FUNCTION: Creating    # Created for test_1
⚡ FUNCTION: Teardown    # Torn down after test_1

⚡ FUNCTION: Creating    # NEW for test_2 (function scope)
⚡ FUNCTION: Teardown    # Torn down after test_2

🏫 CLASS: Teardown       # TestGroup1 class done
🏫 CLASS: Creating       # NEW for TestGroup2 (class scope)
⚡ FUNCTION: Creating    # NEW for test_3 (function scope)
⚡ FUNCTION: Teardown    # Torn down after test_3

🏫 CLASS: Teardown       # TestGroup2 class done
📁 MODULE: Teardown      # Module done
🌍 SESSION: Teardown     # Session done
```

So yes, pytest's internal scope tracking determines exactly when to return cached values vs. execute the fixture function again. The `yield` happens based on these scope boundary crossings!

---
# How is pytest passing the cached values to each function that calls the fixtures as a value?
Great question! The yielded value gets passed to test functions through pytest's **dependency injection system**. Here's how the plumbing works:

## The Dependency Injection Flow

```python
# Simplified version of pytest's internal parameter resolution
class ParameterResolver:
    def __init__(self, fixture_manager):
        self.fixture_manager = fixture_manager
        self.fixture_cache = {}
    
    def resolve_test_parameters(self, test_function):
        """Main entry point - resolve all parameters for a test function"""
        import inspect
        
        # Get the function signature
        sig = inspect.signature(test_function)
        resolved_args = {}
        
        # For each parameter in the test function
        for param_name in sig.parameters:
            if param_name == 'self':  # Skip self for class methods
                continue
                
            print(f"🔍 Resolving parameter: {param_name}")
            
            # Look up the fixture and get its value
            fixture_value = self.get_fixture_value(param_name)
            resolved_args[param_name] = fixture_value
        
        return resolved_args
    
    def get_fixture_value(self, fixture_name):
        """Get the actual value from a fixture (handling yield)"""
        # Check cache first
        if fixture_name in self.fixture_cache:
            cached_result = self.fixture_cache[fixture_name]
            print(f"♻️  Using cached value for {fixture_name}: {cached_result}")
            return cached_result
        
        # Get the fixture definition
        fixture_def = self.fixture_manager.get_fixture_def(fixture_name)
        
        # Execute the fixture and handle yield
        if fixture_def.is_generator:
            generator = fixture_def.func()  # Execute the fixture function
            yielded_value = next(generator)  # Get the yielded value
            
            # Cache both the value AND the generator for teardown
            self.fixture_cache[fixture_name] = {
                'value': yielded_value,
                'generator': generator,
                'scope': fixture_def.scope
            }
            
            print(f"🆕 Created and cached {fixture_name}: {yielded_value}")
            return yielded_value
        else:
            # Regular fixture (no yield)
            result = fixture_def.func()
            self.fixture_cache[fixture_name] = {'value': result, 'generator': None}
            return result
```

## Step-by-Step Example

```python
# Let's trace through a complete example
import inspect

# Mock fixture definitions
class FixtureDef:
    def __init__(self, name, func, scope="function"):
        self.name = name
        self.func = func
        self.scope = scope
        self.is_generator = inspect.isgeneratorfunction(func)

# Example fixtures
def database_fixture():
    print("🔧 Setting up database")
    db_connection = {"host": "localhost", "port": 5432, "active": True}
    yield db_connection  # This is what gets passed to tests!
    print("🧹 Tearing down database")
    db_connection["active"] = False

def user_fixture():
    print("👤 Creating test user")
    user = {"id": 123, "name": "test_user"}
    yield user  # This gets passed to tests!
    print("🗑️ Cleaning up test user")

# Mock test function
def test_user_operations(database, user):
    """Test function that needs both fixtures"""
    print(f"🧪 Test running with database: {database}")
    print(f"🧪 Test running with user: {user}")
    
    # Test logic here...
    database["queries"] = database.get("queries", 0) + 1
    user["last_login"] = "2025-08-01"

# Pytest's parameter resolution in action
class TestExecutor:
    def __init__(self):
        self.fixture_defs = {
            'database': FixtureDef('database', database_fixture, 'session'),
            'user': FixtureDef('user', user_fixture, 'function')
        }
        self.fixture_cache = {}
        self.active_generators = {}  # Track generators for teardown
    
    def execute_test(self, test_func):
        """Execute a test function with dependency injection"""
        print(f"\n🚀 Executing: {test_func.__name__}")
        
        # Step 1: Inspect the test function's parameters
        sig = inspect.signature(test_func)
        print(f"📋 Parameters needed: {list(sig.parameters.keys())}")
        
        # Step 2: Resolve each parameter to a fixture value
        kwargs = {}
        for param_name in sig.parameters:
            fixture_value = self.resolve_fixture(param_name)
            kwargs[param_name] = fixture_value
        
        # Step 3: Call the test function with resolved parameters
        print("📞 Calling test function with resolved fixtures...")
        test_func(**kwargs)
        
        # Step 4: Handle function-scoped teardowns
        self.teardown_function_fixtures()
    
    def resolve_fixture(self, fixture_name):
        """Resolve a single fixture to its value"""
        fixture_def = self.fixture_defs[fixture_name]
        cache_key = (fixture_name, fixture_def.scope)
        
        # Check cache based on scope
        if cache_key in self.fixture_cache:
            cached_data = self.fixture_cache[cache_key]
            print(f"♻️  Cache hit for {fixture_name}: returning {cached_data['value']}")
            return cached_data['value']
        
        # Cache miss - create new fixture
        print(f"🆕 Cache miss for {fixture_name} - executing fixture function")
        
        if fixture_def.is_generator:
            # Execute generator fixture
            generator = fixture_def.func()
            yielded_value = next(generator)  # <-- THIS is the magic moment!
            
            # Store both the yielded value and generator
            self.fixture_cache[cache_key] = {
                'value': yielded_value,
                'generator': generator
            }
            self.active_generators[cache_key] = generator
            
            print(f"✨ Yielded value extracted: {yielded_value}")
            return yielded_value
        else:
            # Regular fixture
            result = fixture_def.func()
            self.fixture_cache[cache_key] = {'value': result, 'generator': None}
            return result
    
    def teardown_function_fixtures(self):
        """Run teardown for function-scoped fixtures"""
        for cache_key, generator in list(self.active_generators.items()):
            fixture_name, scope = cache_key
            if scope == 'function':
                print(f"🧹 Running teardown for {fixture_name}")
                try:
                    next(generator)  # This runs the code after yield
                except StopIteration:
                    pass  # Expected - generator exhausted
                
                # Remove from cache and active generators
                del self.fixture_cache[cache_key]
                del self.active_generators[cache_key]

# Demonstration
executor = TestExecutor()

# Run the test - watch the dependency injection happen
executor.execute_test(test_user_operations)

# Run another test to see caching in action
print("\n" + "="*50)
def test_database_query(database):
    print(f"🧪 Another test with database: {database}")
    database["queries"] = database.get("queries", 0) + 1

executor.execute_test(test_database_query)
```

**Output shows the complete flow:**
```
🚀 Executing: test_user_operations
📋 Parameters needed: ['database', 'user']
🆕 Cache miss for database - executing fixture function
🔧 Setting up database
✨ Yielded value extracted: {'host': 'localhost', 'port': 5432, 'active': True}
🆕 Cache miss for user - executing fixture function
👤 Creating test user
✨ Yielded value extracted: {'id': 123, 'name': 'test_user'}
📞 Calling test function with resolved fixtures...
🧪 Test running with database: {'host': 'localhost', 'port': 5432, 'active': True}
🧪 Test running with user: {'id': 123, 'name': 'test_user'}
🧹 Running teardown for user
🗑️ Cleaning up test user

==================================================
🚀 Executing: test_database_query
📋 Parameters needed: ['database']
♻️  Cache hit for database: returning {'host': 'localhost', 'port': 5432, 'active': True, 'queries': 1}
📞 Calling test function with resolved fixtures...
🧪 Another test with database: {'host': 'localhost', 'port': 5432, 'active': True, 'queries': 1}
```

## The Key Magic Moments

**1. Parameter Inspection**
```python
# pytest uses inspect.signature() to see what the test function needs
sig = inspect.signature(test_user_operations)
# Returns: ['database', 'user']
```

**2. Yield Value Extraction** 
```python
# When fixture is a generator, pytest calls next() to get the yielded value
generator = database_fixture()  # This returns a generator object
yielded_value = next(generator)  # This extracts: {'host': 'localhost', ...}
```

**3. Parameter Injection**
```python
# pytest builds a kwargs dict and passes it to the test
kwargs = {
    'database': {'host': 'localhost', 'port': 5432, 'active': True},
    'user': {'id': 123, 'name': 'test_user'}
}
test_user_operations(**kwargs)  # Unpacks the parameters
```

**4. Generator Preservation**
```python
# pytest keeps the generator alive for teardown
self.active_generators[cache_key] = generator
# Later, during teardown:
next(generator)  # Runs the code after yield
```

The genius is that pytest treats the yielded value as the "fixture result" that gets injected, while keeping the generator alive in the background for proper teardown. The test functions never see the generators - they only see the clean yielded values!
