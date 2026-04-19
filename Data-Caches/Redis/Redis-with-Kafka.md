# Redis with Kafka
## Using Redis in a Web Application

Redis is an in-memory data store that excels as a **cache, session store, and real-time data layer**. Here's how to think about it:

### 1. Caching
This is Redis's most common web use case. Instead of hitting your database on every request, store the result in Redis with a TTL (time-to-live):

```python
# Check cache first, fall back to DB
cached = redis.get("user:123:profile")
if cached:
    return json.loads(cached)

user = db.query("SELECT * FROM users WHERE id = 123")
redis.setex("user:123:profile", 3600, json.dumps(user))  # Cache for 1 hour
return user
```

### 2. Session Storage
Redis is ideal for storing user sessions because it's fast and supports expiry natively. Most web frameworks (Express, Django, Rails) have Redis session adapters out of the box.

### 3. Rate Limiting
Use Redis atomic increments to enforce API rate limits per user/IP:

```python
key = f"rate_limit:{user_id}"
count = redis.incr(key)
redis.expire(key, 60)  # Reset every 60s
if count > 100:
    raise TooManyRequestsError()
```

### 4. Pub/Sub & Real-Time Features
Redis Pub/Sub powers live notifications, chat, or feed updates without polling your DB.

### 5. Leaderboards & Counters
Redis **Sorted Sets** are perfect for real-time leaderboards — `ZADD`, `ZRANK`, and `ZRANGE` are O(log N) and extremely fast.

---

## Using Redis in a Kafka-Driven Pipeline

In a Kafka pipeline, Redis plays a **complementary role** — Kafka handles durable message streaming while Redis handles fast, ephemeral state lookups. Here are the key patterns:

### 1. Enrichment Cache (Most Common)
Kafka consumers often need to enrich events with reference data (e.g., user profiles, product metadata). Hitting a database per-message kills throughput. Redis sits as a hot cache:

```
Kafka Topic → Consumer → Redis Lookup (enrich event) → Processed Output
```

```java
// Inside your Kafka consumer
ConsumerRecord<String, Event> record = ...;
String userId = record.value().getUserId();

// Fast Redis lookup instead of DB call
UserProfile profile = redis.get("user:" + userId);
EnrichedEvent enriched = enrich(record.value(), profile);
producer.send("enriched-events", enriched);
```

### 2. Deduplication
Kafka can deliver messages more than once. Use Redis Sets or `SETNX` to deduplicate by event ID within a time window:

```python
event_id = message.headers["event_id"]
if redis.setnx(f"seen:{event_id}", 1):  # Only true if key didn't exist
    redis.expire(f"seen:{event_id}", 86400)  # Forget after 24h
    process(message)
# else: duplicate, skip
```

### 3. Stateful Aggregations (Windowed Counts)
When you need rolling metrics (e.g., "events per user in the last 5 minutes") that are too expensive to compute from Kafka directly:

```
Kafka Consumer → Redis INCR/EXPIRE → Aggregated State
```

### 4. Offset / Checkpoint Tracking
Instead of relying solely on Kafka's native offset commits, some pipelines write consumer offsets to Redis for finer control or cross-service coordination.

### 5. Dead Letter Queue Signaling
When a message fails processing, write its metadata to a Redis list or stream so a monitoring service can inspect and replay it without re-consuming from Kafka.

---

## Key Principle

Think of the two together like this:

| Concern | Use Kafka | Use Redis |
|---|---|---|
| Durable event log | ✅ | ❌ |
| Replay history | ✅ | ❌ |
| Fast per-event state lookup | ❌ | ✅ |
| Short-lived aggregations | ❌ | ✅ |
| Fan-out to many consumers | ✅ | Pub/Sub (small scale) |

Redis should never replace Kafka's durability guarantees — it complements them by making your consumers fast and stateful.
