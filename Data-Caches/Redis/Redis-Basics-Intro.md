# Redis: A Complete Beginner's Guide

## What is Redis?

Redis (Remote Dictionary Server) is an **in-memory data store** — think of it as a supercharged dictionary that lives in RAM instead of on disk. This makes it blazingly fast (sub-millisecond reads/writes), but it means you use it differently than a traditional database like Postgres.

**The mental model:** Redis is not a replacement for your main database. It's a *companion* to it. You use Redis for things that need to be:
- **Fast** (caching, sessions, rate limiting)
- **Temporary** (data with an expiration)
- **Shared** (between multiple servers or Lambda functions)

---

## Core Concepts

### 1. Keys and Values
Everything in Redis is a **key → value** pair. The key is always a string. The value can be one of several data types.

### 2. Data Types
| Type | Like in Python | Best For |
|---|---|---|
| String | `str` / `int` | Caching, counters, flags |
| Hash | `dict` | Storing objects/records |
| List | `list` (linked) | Queues, activity feeds |
| Set | `set` | Unique items, tags |
| Sorted Set | `dict` with scores | Leaderboards, rankings |
| TTL | — | Expiring any key automatically |

### 3. TTL (Time To Live)
You can tell Redis to **automatically delete a key** after N seconds. This is one of Redis's most powerful features — no cleanup code needed.

---

## Setup

### Install the Python client
```bash
pip install redis
```

There are two main clients:
- `redis` — the classic, synchronous client
- `redis[asyncio]` — for async code (better for Lambda with async handlers)

### Running Redis locally
```bash
# With Docker (easiest)
docker run -d -p 6379:6379 redis

# Or install directly
brew install redis && redis-server  # Mac
```

### In production (AWS)
Use **ElastiCache for Redis** (AWS managed Redis). You point your Lambda at the ElastiCache endpoint instead of `localhost`.

> ⚠️ **Lambda + ElastiCache requires your Lambda to be inside a VPC** — the same VPC as your ElastiCache cluster. This is the most common gotcha for first-timers.

---

## Connecting

```python
import redis

# Local development
r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# ElastiCache (production)
r = redis.Redis(
    host='your-cluster.abc123.ng.0001.use1.cache.amazonaws.com',
    port=6379,
    db=0,
    decode_responses=True  # Returns strings instead of bytes
)

# Test the connection
r.ping()  # Returns True
```

> `decode_responses=True` is almost always what you want — without it, Redis returns raw `bytes` instead of strings.

### Lambda-specific pattern: Connection reuse
Lambda reuses execution environments between invocations. You should initialize the Redis client **outside the handler** so it's reused (not reconnected on every request):

```python
import redis
import os

# Runs once per Lambda container — reused across warm invocations
r = redis.Redis(
    host=os.environ['REDIS_HOST'],
    port=6379,
    decode_responses=True
)

def handler(event, context):
    # r is already connected — just use it
    value = r.get('some_key')
    return {'statusCode': 200, 'body': value}
```

---

## The Common Data Types & Syntax

### 🔤 Strings — The workhorse
Used for caching API responses, storing single values, counters.

```python
# SET and GET
r.set('username', 'alice')
r.get('username')          # → 'alice'

# With expiration (TTL)
r.set('session:abc123', 'user_data', ex=3600)  # expires in 1 hour
r.setex('token:xyz', 300, 'some_token')        # same thing, different syntax

# Check time remaining
r.ttl('session:abc123')   # → seconds remaining, -1 = no expiry, -2 = gone

# Only set if key does NOT exist (great for distributed locks)
r.setnx('lock:job', 'worker-1')   # Returns True if set, False if already exists

# Counters
r.set('page_views', 0)
r.incr('page_views')       # → 1
r.incr('page_views')       # → 2
r.incrby('page_views', 5)  # → 7
r.decr('page_views')       # → 6

# Delete
r.delete('username')
```

---

### 📦 Hashes — Storing objects
A Hash lets you store a dictionary under one key. Perfect for user profiles, product records, etc.

```python
# Store an object
r.hset('user:1001', mapping={
    'name': 'Alice',
    'email': 'alice@example.com',
    'plan': 'pro'
})

# Get one field
r.hget('user:1001', 'name')         # → 'Alice'

# Get all fields
r.hgetall('user:1001')              # → {'name': 'Alice', 'email': '...', 'plan': 'pro'}

# Update one field (without touching others)
r.hset('user:1001', 'plan', 'enterprise')

# Check if field exists
r.hexists('user:1001', 'email')     # → True

# Delete a field
r.hdel('user:1001', 'plan')

# Increment a numeric field
r.hincrby('user:1001', 'login_count', 1)
```

---

### 📋 Lists — Queues and feeds
Lists are ordered sequences. You can push/pop from either end, making them perfect for job queues.

```python
# Push to the right (end)
r.rpush('jobs', 'job_1', 'job_2', 'job_3')

# Push to the left (front)
r.lpush('jobs', 'urgent_job')

# View items (without removing)
r.lrange('jobs', 0, -1)   # -1 means "to the end" → ['urgent_job', 'job_1', 'job_2', 'job_3']

# Pop from left (FIFO queue — take oldest item)
r.lpop('jobs')             # → 'urgent_job'

# Pop from right (LIFO / stack)
r.rpop('jobs')             # → 'job_3'

# Length
r.llen('jobs')             # → 2

# Blocking pop (waits up to 10s for an item — great for workers)
r.blpop('jobs', timeout=10)
```

---

### 🔵 Sets — Unique collections
Sets hold unique values with no order. Great for tagging, tracking unique visitors, permissions.

```python
# Add members
r.sadd('tags:post:42', 'python', 'redis', 'aws')
r.sadd('tags:post:42', 'python')   # Duplicate — silently ignored

# Get all members
r.smembers('tags:post:42')         # → {'python', 'redis', 'aws'}

# Check membership
r.sismember('tags:post:42', 'redis')   # → True

# Remove a member
r.srem('tags:post:42', 'aws')

# Count
r.scard('tags:post:42')            # → 2

# Set operations (great for "find common interests" etc.)
r.sadd('user:1:interests', 'python', 'hiking', 'coffee')
r.sadd('user:2:interests', 'python', 'gaming', 'coffee')

r.sinter('user:1:interests', 'user:2:interests')   # → {'python', 'coffee'}
r.sunion('user:1:interests', 'user:2:interests')   # → all interests combined
r.sdiff('user:1:interests', 'user:2:interests')    # → {'hiking'} (in 1 but not 2)
```

---

### 🏆 Sorted Sets — Leaderboards & rankings
Like a Set, but every member has a **score**. Members are always sorted by score.

```python
# Add members with scores
r.zadd('leaderboard', {'alice': 1500, 'bob': 2300, 'carol': 1800})

# Get top 3 (highest scores)
r.zrevrange('leaderboard', 0, 2, withscores=True)
# → [('bob', 2300.0), ('carol', 1800.0), ('alice', 1500.0)]

# Get rank (0-indexed, lowest score = rank 0)
r.zrank('leaderboard', 'alice')      # → 0 (lowest)
r.zrevrank('leaderboard', 'alice')   # → 2 (from top)

# Update score
r.zincrby('leaderboard', 200, 'alice')   # alice now has 1700

# Get score
r.zscore('leaderboard', 'bob')       # → 2300.0

# Get members in a score range
r.zrangebyscore('leaderboard', 1700, 2500, withscores=True)
```

---

## Real-World Patterns

### Pattern 1: Caching an expensive API/DB call
```python
import json

def get_user_profile(user_id):
    cache_key = f'user:profile:{user_id}'
    
    # Try cache first
    cached = r.get(cache_key)
    if cached:
        return json.loads(cached)
    
    # Cache miss — fetch from DB
    profile = db.query(f"SELECT * FROM users WHERE id = {user_id}")
    
    # Store in cache for 10 minutes
    r.set(cache_key, json.dumps(profile), ex=600)
    return profile
```

### Pattern 2: Rate limiting in a Lambda
```python
def check_rate_limit(user_id, limit=100, window_seconds=60):
    key = f'rate:{user_id}:{int(time.time() // window_seconds)}'
    
    count = r.incr(key)
    if count == 1:
        r.expire(key, window_seconds)  # Set TTL on first hit
    
    return count <= limit

def handler(event, context):
    user_id = event['requestContext']['identity']['sourceIp']
    
    if not check_rate_limit(user_id):
        return {'statusCode': 429, 'body': 'Too many requests'}
    
    # ... rest of handler
```

### Pattern 3: Distributed lock (prevent duplicate Lambda executions)
```python
import uuid

def acquire_lock(lock_name, ttl=30):
    lock_id = str(uuid.uuid4())
    # NX = only set if Not eXists, EX = expire in ttl seconds
    acquired = r.set(f'lock:{lock_name}', lock_id, nx=True, ex=ttl)
    return lock_id if acquired else None

def release_lock(lock_name, lock_id):
    # Only delete if WE own the lock
    current = r.get(f'lock:{lock_name}')
    if current == lock_id:
        r.delete(f'lock:{lock_name}')

def handler(event, context):
    lock_id = acquire_lock('nightly_job')
    if not lock_id:
        return {'body': 'Job already running'}
    
    try:
        run_job()
    finally:
        release_lock('nightly_job', lock_id)
```

### Pattern 4: Session storage
```python
def create_session(user_id):
    session_id = str(uuid.uuid4())
    r.hset(f'session:{session_id}', mapping={
        'user_id': user_id,
        'created_at': time.time()
    })
    r.expire(f'session:{session_id}', 86400)  # 24 hours
    return session_id

def get_session(session_id):
    return r.hgetall(f'session:{session_id}')  # {} if expired/missing
```

---

## Key Naming Conventions

Redis has no namespacing built in, so the community convention is to use **colons as separators**:

```
user:1001              → a user record
user:1001:sessions     → sessions for user 1001
rate:192.168.1.1:60    → rate limit bucket
lock:job:nightly       → a distributed lock
cache:product:SKU-999  → cached product data
```

This keeps keys organized and makes it easy to understand what each key holds at a glance.

---

## Things to Watch Out For

1. **Redis is not durable by default** — a restart can lose data. For Lambda caching this is fine. For anything critical, enable Redis persistence (RDB/AOF) or use ElastiCache with Multi-AZ.

2. **Everything is in memory** — Redis will evict keys when it runs out of RAM. Set a `maxmemory-policy` (e.g., `allkeys-lru`) so it evicts least-recently-used keys gracefully.

3. **Lambda cold starts** — On a cold start your Lambda will re-create the Redis connection. This adds ~50–100ms. Warm invocations reuse the connection for free.

4. **Don't store huge values** — Redis is fast because data is small. Avoid storing multi-MB blobs. Store an S3 key in Redis and the actual file in S3.

5. **Key expiry is eventual** — Expired keys aren't deleted *instantly* — Redis cleans them up lazily or periodically. They won't be *returned* after expiry, but they may briefly consume memory.

---
# Storing Structures:
## Storing Per-User Data in Redis

The core answer is: **your key includes the user ID**. That's the entire namespacing system. There's no "folder" concept — you just bake the user identifier into every key.

---

## The Key Pattern

```
{data_type}:{user_id}:{field}
```

So for 1 million users, you'd have 1 million separate keys — and that's completely normal and expected.

```python
# User 101's data
"user:101:profile"
"user:101:cart"
"user:101:sessions"

# User 202's same data — totally separate keys
"user:202:profile"
"user:202:cart"
"user:202:sessions"
```

---

## Storing Each Python Type

### Storing a Dictionary (user profile, settings, etc.)

**Option A — Redis Hash (best for flat dicts)**

A Hash natively stores a dict under one key. You can update individual fields without rewriting the whole thing.

```python
user_id = 101

# Store
r.hset(f'user:{user_id}:profile', mapping={
    'name': 'Alice',
    'email': 'alice@example.com',
    'plan': 'pro',
    'credits': 50
})

# Read the whole dict back
profile = r.hgetall(f'user:{user_id}:profile')
# → {'name': 'Alice', 'email': 'alice@example.com', ...}

# Read one field
r.hget(f'user:{user_id}:profile', 'plan')   # → 'pro'

# Update ONE field without touching the rest
r.hset(f'user:{user_id}:profile', 'plan', 'enterprise')

# Increment a numeric field
r.hincrby(f'user:{user_id}:profile', 'credits', 10)  # → 60
```

> ⚠️ Hashes only support **flat** key-value pairs — values must be strings or numbers. No nested dicts or lists inside a Hash.

---

**Option B — JSON string (best for nested/complex dicts)**

For nested dicts, serialize to JSON and store as a String.

```python
import json

user_id = 101

user_settings = {
    'theme': 'dark',
    'notifications': {
        'email': True,
        'sms': False
    },
    'preferred_tags': ['python', 'redis']
}

# Store
r.set(f'user:{user_id}:settings', json.dumps(user_settings), ex=3600)

# Read
raw = r.get(f'user:{user_id}:settings')
settings = json.loads(raw) if raw else {}

# Modify and write back (you must rewrite the whole thing)
settings['theme'] = 'light'
r.set(f'user:{user_id}:settings', json.dumps(settings), ex=3600)
```

> The tradeoff: JSON strings require rewriting the whole value to change one field. Redis Hashes let you update individual fields in place.

---

### Storing a List (cart items, activity feed, history)

```python
user_id = 101

# Add items to a user's cart
r.rpush(f'user:{user_id}:cart', 'SKU-001', 'SKU-002', 'SKU-003')

# Read the whole list
cart = r.lrange(f'user:{user_id}:cart', 0, -1)
# → ['SKU-001', 'SKU-002', 'SKU-003']

# Add a new item
r.rpush(f'user:{user_id}:cart', 'SKU-004')

# Remove an item by value (removes up to 1 occurrence)
r.lrem(f'user:{user_id}:cart', 1, 'SKU-002')

# Clear the cart
r.delete(f'user:{user_id}:cart')
```

**For lists of complex objects** (e.g. order history with multiple fields), serialize each item as JSON:

```python
import json

order = {'id': 'ORD-999', 'total': 49.99, 'status': 'shipped'}

# Append to history
r.rpush(f'user:{user_id}:orders', json.dumps(order))

# Read back and deserialize
raw_orders = r.lrange(f'user:{user_id}:orders', 0, -1)
orders = [json.loads(o) for o in raw_orders]
```

---

### Storing a Set (tags, liked posts, permissions, unique visitors)

```python
user_id = 101

# Add to a set (duplicates are ignored automatically)
r.sadd(f'user:{user_id}:liked_posts', 'post:55', 'post:89', 'post:102')

# Check membership (great for "has user liked this post?")
r.sismember(f'user:{user_id}:liked_posts', 'post:89')  # → True

# Get all
r.smembers(f'user:{user_id}:liked_posts')  # → {'post:55', 'post:89', 'post:102'}

# Remove
r.srem(f'user:{user_id}:liked_posts', 'post:55')
```

---

### Storing a Single Value (flag, score, token)

```python
user_id = 101

# A counter
r.set(f'user:{user_id}:credits', 100)
r.incr(f'user:{user_id}:credits')       # 101
r.decrby(f'user:{user_id}:credits', 10) # 91

# A simple flag
r.set(f'user:{user_id}:verified', 'true')
r.set(f'user:{user_id}:verified', 'false')

# A temporary token (with expiry)
r.set(f'user:{user_id}:reset_token', 'abc123xyz', ex=900)  # 15 min
```

---

## Handling Many Users — Practical Example

Here's what a realistic user data layer looks like with multiple data types together:

```python
import json
import redis

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

class UserStore:

    # --- Profile (flat dict → Redis Hash) ---
    def set_profile(self, user_id, profile: dict):
        r.hset(f'user:{user_id}:profile', mapping=profile)

    def get_profile(self, user_id) -> dict:
        return r.hgetall(f'user:{user_id}:profile')  # {} if not found

    def update_profile_field(self, user_id, field, value):
        r.hset(f'user:{user_id}:profile', field, value)

    # --- Settings (nested dict → JSON string) ---
    def set_settings(self, user_id, settings: dict):
        r.set(f'user:{user_id}:settings', json.dumps(settings))

    def get_settings(self, user_id) -> dict:
        raw = r.get(f'user:{user_id}:settings')
        return json.loads(raw) if raw else {}

    # --- Cart (list of SKUs) ---
    def add_to_cart(self, user_id, sku: str):
        r.rpush(f'user:{user_id}:cart', sku)

    def get_cart(self, user_id) -> list:
        return r.lrange(f'user:{user_id}:cart', 0, -1)

    def clear_cart(self, user_id):
        r.delete(f'user:{user_id}:cart')

    # --- Liked posts (set) ---
    def like_post(self, user_id, post_id: str):
        r.sadd(f'user:{user_id}:liked', post_id)

    def unlike_post(self, user_id, post_id: str):
        r.srem(f'user:{user_id}:liked', post_id)

    def has_liked(self, user_id, post_id: str) -> bool:
        return r.sismember(f'user:{user_id}:liked', post_id)

    # --- Credits (counter) ---
    def add_credits(self, user_id, amount: int):
        r.incrby(f'user:{user_id}:credits', amount)

    def get_credits(self, user_id) -> int:
        val = r.get(f'user:{user_id}:credits')
        return int(val) if val else 0

    # --- Delete all data for a user ---
    def delete_user(self, user_id):
        keys = r.keys(f'user:{user_id}:*')  # find all their keys
        if keys:
            r.delete(*keys)
```

Usage:

```python
store = UserStore()

store.set_profile(101, {'name': 'Alice', 'email': 'alice@example.com', 'plan': 'pro'})
store.add_to_cart(101, 'SKU-001')
store.add_to_cart(101, 'SKU-002')
store.like_post(101, 'post:77')
store.add_credits(101, 50)

print(store.get_profile(101))   # {'name': 'Alice', ...}
print(store.get_cart(101))      # ['SKU-001', 'SKU-002']
print(store.has_liked(101, 'post:77'))  # True
print(store.get_credits(101))   # 50
```

---

## One Important Warning: `r.keys()` in Production

```python
# ❌ NEVER do this in production on a large dataset
r.keys('user:*')   # Scans ALL keys — blocks Redis while running

# ✅ Use SCAN instead — iterates in small batches, non-blocking
for key in r.scan_iter('user:101:*'):
    print(key)
```

`r.keys()` is fine locally for debugging, but on a Redis instance with millions of keys it will block everything for seconds. `scan_iter` does the same thing safely.

---

The best way to get comfortable is to spin up Redis locally with Docker and just experiment with the Python client in a REPL. The `redis-cli` tool is also great for inspecting what's actually in your store while you're developing.
