# AsyncIO Overview:
AsyncIO is a great package for processing parallel processing where the processing is non-blocking IO bound operations.

## Documentation/Tutorials
- [Python Official Docs](https://docs.python.org/3/library/asyncio.html)
  - [AsyncIO Sync. Primatives (Lock, Event, Semaphore, etc)](https://docs.python.org/3/library/asyncio-sync.html)
- [Behind the Scenes Concepts](https://jacobpadilla.com/articles/recreating-asyncio)


# AsyncIO: A Deep Dive

## Architecture & Behind-the-Scenes Mechanics

AsyncIO provides a framework for single-threaded concurrent programming using an event loop and coroutines. Here's how it works:

### Core Components

1. **Event Loop**
   - The central execution mechanism that:
     - Manages all running tasks and callbacks
     - Handles I/O operations
     - Processes future events
     - Schedules and executes coroutines

2. **Coroutines**
   - Functions defined with `async def`
   - Can be paused with `await` to yield control back to the event loop
   - Resume execution when awaited operation completes
   - Don't block the event loop while waiting

3. **Futures/Tasks**
   - Futures: Placeholders for results that will be available later
   - Tasks: Special futures that wrap coroutines, enabling scheduling

4. **Transport and Protocols**
   - Lower-level APIs for network communications
   - Transports: Abstract communication channels
   - Protocols: Process data received through transports

### Execution Flow

1. The event loop maintains multiple queues:
   - Ready queue: Coroutines ready to execute
   - Scheduled queue: Callbacks to run at specific times
   - I/O waiting queue: Tasks awaiting I/O completion

2. When a coroutine calls `await`:
   - It yields control to the event loop
   - The event loop notes what the coroutine is waiting for
   - The coroutine is moved to the appropriate waiting queue

3. When a waited-on event completes:
   - The event loop moves the waiting coroutine to the ready queue
   - When its turn comes, the coroutine resumes execution

4. The event loop continuously:
   - Runs ready coroutines
   - Checks for completed I/O
   - Processes due scheduled callbacks

This design enables concurrent execution without the overhead of threads or the complexity of locks, all within a single thread.

## Examples

### Example 1: Basic Asynchronous Functions

```python
import asyncio

async def say_after(delay, message):
    await asyncio.sleep(delay)
    print(message)

async def main():
    # These will run concurrently
    task1 = asyncio.create_task(say_after(1, "Hello"))
    task2 = asyncio.create_task(say_after(2, "World"))
    
    print("Started tasks")
    
    # Wait for both tasks to complete
    await task1
    await task2
    
    print("All tasks completed")

asyncio.run(main())
```

**What's happening:**
- `asyncio.create_task()` schedules coroutines to run concurrently
- `asyncio.sleep()` pauses execution without blocking the event loop
- The event loop handles both tasks concurrently, switching between them

### Example 2: Asynchronous Web Requests

```python
import asyncio
import aiohttp
import time

async def fetch_url(session, url):
    async with session.get(url) as response:
        return await response.text()

async def fetch_all(urls):
    async with aiohttp.ClientSession() as session:
        tasks = [asyncio.create_task(fetch_url(session, url)) for url in urls]
        results = await asyncio.gather(*tasks)
        return results

async def main():
    urls = [
        "https://example.com",
        "https://python.org",
        "https://github.com",
        "https://stackoverflow.com"
    ]
    
    start = time.time()
    results = await fetch_all(urls)
    end = time.time()
    
    print(f"Fetched {len(results)} sites in {end - start:.2f} seconds")
    for i, result in enumerate(results):
        print(f"Site {i+1}: {len(result)} characters")

asyncio.run(main())
```

**What's happening:**
- Multiple HTTP requests run concurrently
- While waiting for network responses, the event loop can process other tasks
- `asyncio.gather()` collects all task results when they complete

### Example 3: Complex Producer-Consumer Pattern

```python
import asyncio
import random
from collections import deque

class AsyncQueue:
    def __init__(self, maxsize=0):
        self.items = deque()
        self.maxsize = maxsize
        self.producers_done = False
        self._get_event = asyncio.Event()
        self._put_event = asyncio.Event()
        self._put_event.set()  # Can put items initially
        
    async def put(self, item):
        while self.maxsize > 0 and len(self.items) >= self.maxsize:
            self._put_event.clear()
            await self._put_event.wait()
            
        self.items.append(item)
        self._get_event.set()  # Signal items available
        
    async def get(self):
        while not self.items:
            if self.producers_done:
                return None  # Queue is empty and no more items coming
            self._get_event.clear()
            await self._get_event.wait()
            
        item = self.items.popleft()
        self._put_event.set()  # Signal space available
        return item
        
    def mark_producers_done(self):
        self.producers_done = True
        self._get_event.set()  # Wake up any waiting consumers

async def producer(queue, id, items):
    for i in range(items):
        item = f"Producer {id}: Item {i}"
        await queue.put(item)
        print(f"Produced: {item}")
        await asyncio.sleep(random.uniform(0.1, 0.5))
    print(f"Producer {id} done")

async def consumer(queue, id):
    while True:
        item = await queue.get()
        if item is None:
            break
        print(f"Consumer {id} got: {item}")
        await asyncio.sleep(random.uniform(0.2, 0.7))
    print(f"Consumer {id} done")

async def main():
    queue = AsyncQueue(maxsize=5)  # Buffer size of 5
    
    # Create producers and consumers
    producers = [asyncio.create_task(producer(queue, i, 10)) for i in range(3)]
    consumers = [asyncio.create_task(consumer(queue, i)) for i in range(2)]
    
    # Wait for all producers to finish
    await asyncio.gather(*producers)
    queue.mark_producers_done()
    
    # Wait for all consumers to finish
    await asyncio.gather(*consumers)
    
    print("All done!")

asyncio.run(main())
```

**What's happening:**
- Implements a bounded buffer with asynchronous producers and consumers
- Uses asyncio.Event for coordination between producers and consumers
- Demonstrates complex coordination patterns without locks or threads
- Shows proper cleanup and shutdown sequences

## AsyncIO Cheatsheet

### Setup and Basics

```python
# Main entry point
asyncio.run(main())  # Python 3.7+

# Creating tasks
task = asyncio.create_task(some_coroutine())  # Python 3.7+
task = asyncio.ensure_future(some_coroutine())  # Older alternative

# Waiting
await asyncio.sleep(1)  # Non-blocking sleep
result = await coroutine_or_future  # Wait for completion
```

### Task Management

```python
# Run multiple coroutines concurrently
results = await asyncio.gather(coro1(), coro2(), coro3())

# Run first completed
done, pending = await asyncio.wait(
    [coro1(), coro2()],
    return_when=asyncio.FIRST_COMPLETED
)

# Wait with timeout
try:
    result = await asyncio.wait_for(slow_operation(), timeout=1.0)
except asyncio.TimeoutError:
    print("Operation timed out")

# Shield from cancellation
task = asyncio.shield(important_operation())
```

### Synchronization Primitives

```python
# Event - signal between tasks
event = asyncio.Event()
await event.wait()  # Wait until set
event.set()  # Set the event, wake waiters
event.clear()  # Clear event

# Lock - mutual exclusion
lock = asyncio.Lock()
async with lock:  # Acquire and release automatically
    # Critical section here
    
# Semaphore - limit concurrent access
sem = asyncio.Semaphore(5)  # Allow 5 concurrent operations
async with sem:
    # Limited access section
    
# Condition - more complex synchronization
cond = asyncio.Condition()
async with cond:
    await cond.wait()  # Wait for notification
    # ... do something ...
    cond.notify(1)  # Wake one waiter
    cond.notify_all()  # Wake all waiters
```

### Queues

```python
# Basic FIFO queue
queue = asyncio.Queue(maxsize=10)
await queue.put(item)  # Put item, blocks if full
item = await queue.get()  # Get item, blocks if empty
queue.task_done()  # Mark task complete

# Priority queue
pq = asyncio.PriorityQueue()
await pq.put((1, 'high priority'))  # Lower number = higher priority
await pq.put((10, 'low priority'))

# LIFO queue (stack)
stack = asyncio.LifoQueue()
```

### Error Handling

```python
# Handling exceptions in gathered tasks
try:
    await asyncio.gather(
        coro1(), coro2(), coro3(),
        return_exceptions=False  # Default, raises first exception
    )
except Exception as e:
    print(f"One task failed: {e}")

# Catch exceptions individually
results = await asyncio.gather(
    coro1(), coro2(), coro3(),
    return_exceptions=True  # Returns exceptions as results
)
for result in results:
    if isinstance(result, Exception):
        print(f"Task failed: {result}")
    else:
        print(f"Task succeeded: {result}")
```

### Cancellation

```python
# Cancelling a task
task = asyncio.create_task(long_running())
# ...later...
task.cancel()

# Handling cancellation
async def cancelable():
    try:
        while True:
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        # Cleanup code here
        raise  # Re-raise to propagate cancellation
```

### Debugging

```python
# Enable debug mode
asyncio.run(main(), debug=True)

# Or set environment variable
# PYTHONASYNCIODEBUG=1

# See all running tasks
for task in asyncio.all_tasks():
    print(task)

# Get current task
current = asyncio.current_task()
```

This cheatsheet covers the most commonly used AsyncIO features, but AsyncIO's API is quite extensive with additional utilities for specific use cases.
