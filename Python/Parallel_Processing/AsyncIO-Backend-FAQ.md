# AsyncIO Backend FAQ
This document will cover some of the intermediate level questions developers commonly ask when learning async for their first few projects. No questions is a bad question, so if you have ones from your experience feel free to add.

---
## When using an async call in python does every function underneath need to be async for it to work correctly? 
In Python, when you make an async call, not every function underneath needs to be async for it to work correctly. Here's how the async/sync interaction works:

When a synchronous function is called from an asynchronous function:
- This works fine because the synchronous function blocks and returns a value normally
- The asynchronous context simply waits for the synchronous function to complete
- No special handling is needed

When an asynchronous function is called from a synchronous function:
- This is where complications arise
- You cannot directly `await` inside a synchronous function
- You need to use an event loop to run the async function to completion:
  - `asyncio.run()` for top-level code
  - `asyncio.get_event_loop().run_until_complete()` for nested calls
  - `asyncio.create_task()` to schedule without waiting

Here's a simple example to illustrate:

```python
import asyncio

# Regular synchronous function
def sync_function(value):
    print(f"Processing {value} synchronously")
    return value * 2

# Async function that calls a sync function
async def async_function():
    print("Starting async function")
    # This works fine - sync functions can be called directly
    result = sync_function(21)
    print(f"Got result: {result}")
    # We can also await other async functions
    await asyncio.sleep(1)
    return result

# Top-level synchronous code calling an async function
def main():
    # Need to use the event loop to call async functions from sync code
    result = asyncio.run(async_function())
    print(f"Final result: {result}")

if __name__ == "__main__":
    main()
```

### How about the reverse scenario, if a non-async calls a async function will the asynchronous call still work?
When a non-async (synchronous) function calls an async function, the asynchronous call won't work directly without special handling. This is a key limitation in Python's async model.

Here's what happens and how to handle it:

## The Problem

```python
def sync_function():
    result = async_function()  # This doesn't work as expected!
    print(result)  # This will print a coroutine object, not the actual result
```

If you try this, `async_function()` returns a coroutine object instead of executing and returning its result. The function doesn't actually run - it just creates a coroutine that needs to be executed by an event loop.

## Solutions

### 1. Using asyncio.run() (simplest, for top-level code)

```python
def sync_function():
    # Run the entire async function to completion
    result = asyncio.run(async_function())
    print(result)  # Now contains the actual result
```

### 2. Using an existing event loop

```python
def sync_function():
    # Get the current event loop and run the async function
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(async_function())
    print(result)
```

### 3. Creating a new event loop (useful in threaded environments)

```python
def sync_function():
    # Create and use a new event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(async_function())
        print(result)
    finally:
        loop.close()
```

### Important Considerations

1. Nested event loops can cause issues - you generally shouldn't call `asyncio.run()` from inside a function that's already part of an async context

2. In GUI applications or other event-driven systems, you need to be careful about how you integrate asyncio's event loop with the application's event loop

3. In multithreaded applications, each thread needs its own event loop

A complete example:

```python
import asyncio

# Async function
async def async_function():
    print("Inside async function")
    await asyncio.sleep(1)  # Simulate some async operation
    return "Async result"

# Sync function calling async function
def sync_function():
    print("Inside sync function")
    # Need to use event loop to run the async function
    result = asyncio.run(async_function())
    print(f"Got result: {result}")
    return result

# Main code
if __name__ == "__main__":
    sync_function()
```

The key point is that whenever a synchronous context needs to call an asynchronous function, you must explicitly run it through an event loop.

---
## When creating an Async version of a Package/Library what is the best practices? Do you simply wrap most calls in an async function?
In many cases, the async version of a library (like AsyncAnthropic) is essentially a wrapper around the synchronous version with some key differences. This is because problems can arise with nesting event loops and other optimization can be added to improve performance (aka not block the event loop).

## Typical Implementation Pattern

The async version typically:

1. **Wraps synchronous calls** in asynchronous functions that:
   - Run the synchronous calls in a thread pool using `asyncio.to_thread()` (newer Python) or `loop.run_in_executor()`
   - Return awaitable objects instead of direct results

2. **Provides non-blocking interfaces** for operations that would otherwise block the event loop

3. **Uses native async libraries** for network operations where possible:
   - `aiohttp` instead of `requests`
   - `asyncpg` instead of `psycopg2`
   - etc.

## Example: Anthropic Sync vs Async

Looking specifically at Anthropic's Python SDK:

```python
# Synchronous version
from anthropic import Anthropic
client = Anthropic()
response = client.messages.create(
    model="claude-3-opus-20240229",
    max_tokens=1000,
    messages=[{"role": "user", "content": "Hello"}]
)

# Asynchronous version
from anthropic.async_client import AsyncAnthropic
client = AsyncAnthropic()
response = await client.messages.create(
    model="claude-3-opus-20240229",
    max_tokens=1000,
    messages=[{"role": "user", "content": "Hello"}]
)
```

Behind the scenes, the AsyncAnthropic client likely:
- Uses an async HTTP library like `aiohttp` or `httpx` for API requests
- Returns awaitable coroutines instead of blocking on API calls
- Handles async context management for resources

## Benefits of Dedicated Async Libraries

While they could be simple wrappers, dedicated async libraries often:

1. **Optimize for async patterns** - special handling for connection pooling, retry logic, etc.
2. **Reduce overhead** - direct async implementations avoid the cost of thread switching
3. **Enable true concurrency** - multiple operations can be in flight simultaneously
4. **Provide async-native interfaces** - like async context managers (`async with`)

## Implementation Examples

Here's a simplified example of how AsyncAnthropic might wrap Anthropic:

```python
# Simplified pseudo-code
class AsyncAnthropic:
    def __init__(self, *args, **kwargs):
        # May initialize the sync client or share configuration
        self._sync_client = Anthropic(*args, **kwargs)
        # Or initialize async-specific resources
        self._async_http_client = aiohttp.ClientSession()
        
    async def messages_create(self, *args, **kwargs):
        # Option 1: Run sync in thread pool
        return await asyncio.to_thread(
            self._sync_client.messages_create, 
            *args, **kwargs
        )
        
        # Option 2: Native async implementation
        async with self._async_http_client.post(
            "https://api.anthropic.com/v1/messages",
            json=kwargs
        ) as response:
            return await response.json()
```

The best async libraries (like AsyncAnthropic) typically use the second approach with native async implementations rather than just wrapping sync code in threads, as this provides better performance and resource utilization.

### Real-World Example: Database Access
Let's compare approaches for database access, which is a common use case:

#### Wrapper Approach (using SQLAlchemy with asyncio):
```python
import asyncio
import sqlalchemy
from sqlalchemy import create_engine, text

class DatabaseClient:
    def __init__(self, connection_string):
        self.engine = create_engine(connection_string)
    
    def execute_query(self, query):
        with self.engine.connect() as conn:
            result = conn.execute(text(query))
            return [dict(row) for row in result]

class AsyncDatabaseWrapper:
    def __init__(self, connection_string):
        self.sync_client = DatabaseClient(connection_string)
    
    async def execute_query(self, query):
        return await asyncio.to_thread(
            self.sync_client.execute_query, query
        )

# Usage
async def main():
    db = AsyncDatabaseWrapper("sqlite:///example.db")
    users = await db.execute_query("SELECT * FROM users LIMIT 10")
    posts = await db.execute_query("SELECT * FROM posts WHERE user_id = 1")
    
    # Both queries run in separate threads, but still use connection pool inefficiently
```

#### Native Async Approach (using asyncpg):
```python
import asyncio
import asyncpg

class AsyncDatabaseClient:
    def __init__(self, connection_info):
        self.connection_info = connection_info
        self.pool = None
    
    async def initialize(self):
        self.pool = await asyncpg.create_pool(**self.connection_info)
    
    async def execute_query(self, query):
        if not self.pool:
            await self.initialize()
        
        async with self.pool.acquire() as connection:
            records = await connection.fetch(query)
            return [dict(record) for record in records]
    
    async def close(self):
        if self.pool:
            await self.pool.close()

# Usage
async def main():
    db = AsyncDatabaseClient({
        "host": "localhost", 
        "database": "example",
        "user": "postgres", 
        "password": "password"
    })
    
    # These run concurrently and efficiently share the connection pool
    users, posts = await asyncio.gather(
        db.execute_query("SELECT * FROM users LIMIT 10"),
        db.execute_query("SELECT * FROM posts WHERE user_id = 1")
    )
    
    await db.close()
```
