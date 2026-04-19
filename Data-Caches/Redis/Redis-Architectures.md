# Redis Architectures
**Redis** (Remote Dictionary Server) is an open-source, **in-memory data structure store** that can function simultaneously as a **database, cache, message broker, and streaming engine**.

**The core idea:** Instead of storing data on disk (like traditional databases), Redis keeps everything in RAM, making reads and writes **blazingly fast** — typically sub-millisecond latency.

### **What makes it more than just a cache:**

Unlike simple key-value stores (like Memcached), Redis understands rich **data structures** natively:
- **Strings** – simple values, counters
- **Hashes** – like a JSON object / dictionary
- **Lists** – ordered collections (queues, feeds)
- **Sets** – unique unordered collections
- **Sorted Sets** – ranked leaderboards, priority queues
- **Streams** – append-only log for event sourcing
- **Bitmaps / HyperLogLog / Geospatial** – specialized structures

### **Key capabilities:**
- **Persistence** – can snapshot data to disk (RDB) or log every write (AOF), so it survives restarts
- **Pub/Sub** – lightweight messaging between services
- **TTL (Time-to-Live)** – keys can auto-expire, perfect for sessions and caching
- **Lua scripting** – atomic, server-side logic execution
- **Clustering & Replication** – horizontal scaling and high availability

---

**The mental model:**

> Redis is like a **supercharged shared memory** that all your services can read from and write to — with the speed of RAM, the richness of a data structure library, and just enough durability to be trusted in production.

---

It's one of the most widely used pieces of infrastructure in the world, powering rate limiting, session storage, real-time leaderboards, job queues, and caching layers across virtually every major tech company.

---
## Redis is NOT a Mirror of Your Database

This is the key mindset shift. Redis is **not a second copy of your database that needs to stay in sync**. It's a **temporary, disposable cache of specific hot data**. Your database is always the source of truth. Redis just holds shortcuts to answers you've recently computed or fetched.

If Redis died right now, your app should still work — just slower.

---

## How the Patterns Actually Work

### Pattern 1: Cache-Aside (Most Common)
Your app manages the cache manually. The database is always the authority.

```
READ:
1. Check Redis → hit? Return it. Done.
2. Miss? Query the database.
3. Store result in Redis with a TTL.
4. Return result.

WRITE:
1. Write to the database.
2. DELETE (or update) the Redis key.
```

```python
def get_user(user_id):
    cached = redis.get(f"user:{user_id}")
    if cached:
        return deserialize(cached)

    # Cache miss — go to DB
    user = db.query("SELECT * FROM users WHERE id = ?", user_id)
    redis.setex(f"user:{user_id}", ttl=300, value=serialize(user))  # Cache 5 min
    return user

def update_user(user_id, data):
    db.execute("UPDATE users SET ... WHERE id = ?", user_id)
    redis.delete(f"user:{user_id}")  # Invalidate — next read will refresh from DB
```

On the write, you **delete** the Redis key rather than updating it. The next read will naturally repopulate it from the fresh DB data. This avoids subtle race conditions from trying to keep them in sync manually.

---

### Pattern 2: TTL-Based Expiry (Lazy Sync)
Instead of manually deleting on writes, you just let Redis keys expire. After the TTL, the next read fetches fresh data from the DB automatically.

This is simpler but means there's a window where Redis has **stale data**. That's acceptable for things like:
- A user's public profile
- Product descriptions
- Configuration data

It's **not** acceptable for things like:
- Account balances
- Inventory counts
- Anything where stale = wrong behavior

---

### Pattern 3: Write-Through (Redis + DB Together)
Every write goes to **both** Redis and the DB atomically. Reads always hit Redis first.

```python
def update_user(user_id, data):
    db.execute("UPDATE users ...")
    redis.setex(f"user:{user_id}", ttl=300, value=serialize(data))  # Update both
```

This keeps Redis warm and fresh, but adds write latency since you're writing twice. Good when reads are extremely frequent and cache misses are costly.

---

### Pattern 4: Write-Back / Write-Behind (Rare, Risky)
You write to Redis first, return success to the user, and flush to the DB asynchronously later. This is fast but dangerous — if Redis crashes before the flush, you lose data. Only use this if you deeply understand the tradeoffs (e.g., buffering analytics events).

---

## Answering Your Specific Questions

**"Do I have to flush Redis to the database?"**
No — and you generally shouldn't think about it that way. You write to your **database first**, always. Redis just holds a cached copy. There's nothing to flush *to* the DB because the DB already has the real data.

**"Do I need to refresh Redis?"**
Not manually in most cases. You either:
- Delete the key on write (cache-aside), and let the next read repopulate it, or
- Let the TTL expire naturally

**"How does data stay synced for the user?"**
It doesn't need to be perfectly synced — that's the point. You choose a TTL based on how stale you're willing to tolerate. For sensitive data, you invalidate immediately on write. For less critical data, a 60-second or 5-minute TTL is fine.

---

## Simple Mental Model

```
Database  →  source of truth, persistent, slower
Redis     →  disposable shortcut, fast, temporary

User request
    ↓
Redis hit? → return cached value (fast)
    ↓ miss
Query DB → store in Redis → return value
    ↓
User updates something?
    → Write to DB first
    → Delete or update Redis key
```

You're not syncing two databases. You're just avoiding redundant DB queries by remembering recent answers for a short while.

---
## Quick Setup
Lets cover both government-specific and cloud deployment angles.

---

## Redis in Iron Bank (DoD Government Projects)

Yes, there is a hardened Redis image in Iron Bank. Here's what you need to know:

**What Iron Bank Is:** Iron Bank is a central repository of digitally-signed container images, hardened to the DoD's exacting specifications. Approved containers have DoD-wide reciprocity across all classifications, accelerating a security process that can otherwise take months or years.

**Redis Availability:** There is an official Platform One Redis image in Iron Bank. A hardened version also exists from RapidFort — it is a functionally equivalent copy of the Platform One Redis Iron Bank image, optimized by removing unnecessary software components to reduce the attack surface, with vulnerability reports updated daily.

**Important Caveat on CVEs:** Even hardened images aren't perfect. An analysis of the 100 most downloaded images from Iron Bank revealed an average of 110 CVEs per image, highlighting the inherent complexity of maintaining a repository of container images even within a highly controlled environment. So "hardened" means reduced risk, not zero risk.

**How to Access It:** Go to [ironbank.dso.mil](https://ironbank.dso.mil) and register for a Platform One account. Every container image is scanned daily for vulnerabilities, and vendors can update and patch images as risks are identified.

**STIG Note:** There are STIG-hardened base images (like Ubuntu with CIS L2 and STIG hardening) approved by Platform One, which commercial partners can build upon for DoD use. Redis itself runs on top of one of these hardened base images.

---

## Setting Up Redis on AWS (ElastiCache)

AWS's managed Redis service is called **Amazon ElastiCache**. It's the right choice for almost all production use cases — don't run Redis on a raw EC2 instance if you can avoid it.

### Step 1 — Choose Your Mode

ElastiCache offers a serverless option (create a cache in under a minute with no capacity planning) or a node-based cluster where you choose node type, count, and placement across Availability Zones. For most apps, **serverless** is the fastest way to start.

> Note: As of March 2025, Redis 8.0 is licensed under AGPLv3, which many organizations avoid due to its copyleft provisions. AWS also supports Valkey (a fully open-source fork of Redis 7.2 under BSD licensing) as an alternative engine on ElastiCache. Check your org's license policy before choosing.

### Step 2 — Create the Cluster (Console)

1. Go to **AWS Console → ElastiCache → Create Cache**
2. Choose **Redis OSS** (or Valkey) as the engine
3. Pick **Serverless** for simplicity, or **Design your own** for more control
4. Place it in the **same VPC as your application** — this is critical, ElastiCache is not publicly accessible by default
5. Create or assign a **subnet group** spanning your AZs

### Step 3 — Security Group Rules

Add an inbound rule to the ElastiCache cluster's security group allowing custom TCP on port 6379, with the source set to the security group of your application EC2 instances. This ensures only your app servers can reach Redis, not the open internet.

### Step 4 — Connect From Your App

Once created, grab the **Primary Endpoint** from the ElastiCache console. Then connect from your app:

```python
import redis

r = redis.Redis(
    host='your-cluster.abc123.cache.amazonaws.com',
    port=6379,
    ssl=True  # ElastiCache Serverless requires TLS
)

r.set("key", "value", ex=300)
print(r.get("key"))
```

### Step 5 — Enable TLS + Auth (Production Must-Haves)

ElastiCache has built-in VPC support and offers encryption in-transit and at-rest, combined with native Redis AUTH for authentication and authorization. Always enable both for any non-dev environment.

---

### Quick Decision Guide

| Situation | Use |
|---|---|
| Government / DoD project | Iron Bank hardened Redis image via Platform One |
| AWS cloud app, no infra team | ElastiCache Serverless |
| AWS cloud app, need fine control | ElastiCache node-based cluster |
| License concerns (AGPLv3) | Valkey engine on ElastiCache |
| Self-managed on EC2 | Only if you have a specific reason (avoid this) |
