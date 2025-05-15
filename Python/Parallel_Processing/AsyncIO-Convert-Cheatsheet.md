# Cheatsheet: Converting Synchronous Python to Asynchronous
I've created a comprehensive checklist for converting synchronous code to asynchronous in the attached artifact. The checklist covers each phase of the conversion process, from preparation to optimization, with specific items to check off as you go.

## Core Conversion Patterns

| Synchronous Pattern | Asynchronous Equivalent | Notes |
|---------------------|-------------------------|-------|
| `def function_name():` | `async def function_name():` | Mark functions that contain awaits as async |
| `result = func()` | `result = await func()` | Must await coroutines to get their results |
| `return value` | `return value` | Return statements stay the same |
| `with resource():` | `async with resource():` | For async context managers |
| `for item in iterable:` | `async for item in async_iterable:` | For async iterators |
| `time.sleep(seconds)` | `await asyncio.sleep(seconds)` | Non-blocking sleep |

## Library Replacements

| Synchronous Library | Asynchronous Alternative | Common Use Case |
|--------------------|--------------------------|----------------|
| `requests` | `aiohttp`, `httpx` | HTTP requests |
| `psycopg2` | `asyncpg` | PostgreSQL |
| `pymysql` | `aiomysql` | MySQL |
| `redis` | `aioredis` | Redis |
| `pymongo` | `motor` | MongoDB |
| `boto3` | `aioboto3` | AWS services |
| `sqlite3` | `aiosqlite` | SQLite |
| `smtplib` | `aiosmtplib` | Email |
| `open()` | `aiofiles.open()` | File I/O |

## I/O Operation Conversions

| Synchronous I/O | Asynchronous Equivalent |
|-----------------|-------------------------|
| `open(file).read()` | `async with aiofiles.open(file) as f: await f.read()` |
| `open(file).write(data)` | `async with aiofiles.open(file, 'w') as f: await f.write(data)` |
| `requests.get(url)` | `async with aiohttp.ClientSession() as session: await session.get(url)` |
| `socket.recv()` | `await reader.read()` (with `asyncio.StreamReader`) |
| `subprocess.run()` | `await asyncio.create_subprocess_exec()` |

## Running Async Code from Sync Contexts

| Pattern | Example | When to Use |
|---------|---------|-------------|
| Top-level entry point | `asyncio.run(main())` | Program entry point |
| Inside a function | `loop = asyncio.get_event_loop(); loop.run_until_complete(coro())` | When in an existing sync function |
| Run in thread pool | `await asyncio.to_thread(sync_func)` | Convert sync function to awaitable |
| New event loop | `new_loop = asyncio.new_event_loop(); new_loop.run_until_complete(coro())` | In threaded apps |

## Concurrency Patterns

| Synchronous | Asynchronous | Purpose |
|-------------|--------------|---------|
| `[func() for x in items]` | `await asyncio.gather(*[func(x) for x in items])` | Parallel execution |
| `ThreadPoolExecutor` | `asyncio.gather()` | Concurrent tasks |
| `thread.start()` | `asyncio.create_task(coro())` | Background tasks |
| `queue.Queue()` | `asyncio.Queue()` | Task coordination |
| `threading.Event()` | `asyncio.Event()` | Synchronization |
| `threading.Lock()` | `asyncio.Lock()` | Mutual exclusion |

## Code Transformation Examples

### Example 1: Basic HTTP Client

**Synchronous Version:**
```python
import requests

def get_user_data(user_id):
    response = requests.get(f"https://api.example.com/users/{user_id}")
    response.raise_for_status()
    return response.json()

def get_multiple_users(user_ids):
    return [get_user_data(user_id) for user_id in user_ids]

# Usage
users = get_multiple_users([1, 2, 3])
```

**Asynchronous Version:**
```python
import asyncio
import aiohttp

async def get_user_data(session, user_id):
    async with session.get(f"https://api.example.com/users/{user_id}") as response:
        response.raise_for_status()
        return await response.json()

async def get_multiple_users(user_ids):
    async with aiohttp.ClientSession() as session:
        tasks = [get_user_data(session, user_id) for user_id in user_ids]
        return await asyncio.gather(*tasks)

# Usage
users = asyncio.run(get_multiple_users([1, 2, 3]))
```

### Example 2: Database Operations

**Synchronous Version:**
```python
import psycopg2

def get_user(user_id):
    conn = psycopg2.connect("dbname=example user=postgres")
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    return user

def update_user(user_id, data):
    conn = psycopg2.connect("dbname=example user=postgres")
    cur = conn.cursor()
    cur.execute("UPDATE users SET name = %s WHERE id = %s", 
                (data['name'], user_id))
    conn.commit()
    cur.close()
    conn.close()
```

**Asynchronous Version:**
```python
import asyncpg

async def get_user(user_id):
    conn = await asyncpg.connect("postgresql://postgres@localhost/example")
    user = await conn.fetchrow("SELECT * FROM users WHERE id = $1", user_id)
    await conn.close()
    return user

async def update_user(user_id, data):
    conn = await asyncpg.connect("postgresql://postgres@localhost/example")
    await conn.execute("UPDATE users SET name = $1 WHERE id = $2", 
                      data['name'], user_id)
    await conn.close()
```

### Example 3: File Processing

**Synchronous Version:**
```python
def process_log_file(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
    
    errors = []
    for line in lines:
        if "ERROR" in line:
            errors.append(line)
    
    with open('errors.log', 'w') as f:
        f.writelines(errors)
```

**Asynchronous Version:**
```python
import aiofiles

async def process_log_file(filename):
    async with aiofiles.open(filename, 'r') as f:
        lines = await f.readlines()
    
    errors = [line for line in lines if "ERROR" in line]
    
    async with aiofiles.open('errors.log', 'w') as f:
        await f.writelines(errors)
```

