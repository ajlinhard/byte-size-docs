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
