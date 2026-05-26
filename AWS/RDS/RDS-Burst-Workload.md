# RDS Burst Workload
If you have a database in RDS which has a burst of read write processing then some light read write  the rest of the day that is 5-10% the burst amount. What are options for the solution?

This is a classic **spiky workload pattern**. Here are your options, from simplest to most sophisticated:

---

## 1. Aurora Serverless v2 ⭐ (Best fit for this pattern)

**How it works:** Aurora automatically scales compute capacity up and down based on actual load — you pay per ACU (Aurora Capacity Unit) per second.

- Scales from minimum to maximum ACUs within seconds
- During burst → scales up rapidly
- During quiet periods → scales down to near-zero
- No manual intervention needed

**Best for:** Unpredictable or spiky workloads where you don't want to over-provision

**Trade-off:** Slightly higher per-unit cost than provisioned, but overall cheaper due to scale-down

---

## 2. RDS with Read Replicas + Load Balancing

**How it works:** Offload read traffic to one or more read replicas during bursts.

- Primary instance handles writes
- Read replicas absorb the read burst
- Use **Route 53 or a proxy** to route reads to replicas
- Can pre-warm replicas before known burst windows

**Best for:** Read-heavy bursts where writes are moderate

**Trade-off:** Replicas run 24/7, so you pay for them even during quiet hours

---

## 3. RDS Proxy

**How it works:** Sits between your app and RDS, pooling and managing database connections.

- During bursts, prevents connection storms that can overwhelm RDS
- Queues excess connections instead of dropping them
- Reduces failover time
- Works with existing RDS or Aurora

**Best for:** Apps that open many short-lived connections (Lambda, microservices) during bursts

**Trade-off:** Doesn't scale compute — just protects against connection overload

---

## 4. Scheduled Scaling (RDS + Auto Scaling Read Replicas)

**How it works:** If your burst is **predictable** (e.g., 9–10 AM every morning), you can schedule replica scaling.

- Aurora Auto Scaling adds/removes replicas on a schedule or based on CPU/connection metrics
- Scale up before the burst, scale down after

**Best for:** Known, recurring burst windows (batch jobs, business hours, reporting runs)

**Trade-off:** Doesn't help with *unexpected* bursts

---

## 5. Caching Layer (ElastiCache Redis/Memcached)

**How it works:** Cache frequent read results in-memory so they never hit RDS.

- Cache hit → RDS gets no load at all
- Dramatically reduces read burst impact
- Works for reads of relatively stable data (product catalogs, user profiles, config)

**Best for:** Repeated reads of the same data during bursts

**Trade-off:** Cache invalidation complexity; only helps reads, not writes

---

## 6. SQS Queue for Write Bursts

**How it works:** Instead of writing directly to RDS during a burst, writes go into an SQS queue and are consumed at a controlled rate.

- Burst of writes → lands in queue (near-instant)
- Lambda or a worker drains the queue at a pace RDS can handle
- RDS never sees the spike

**Best for:** Write-heavy bursts where slight write delay is acceptable

**Trade-off:** Writes are not immediately consistent; adds latency and complexity

---

## 7. Vertical Scaling (Scheduled Instance Resizing)

**How it works:** Resize your RDS instance class up before the burst window and down after.

- Automate via Lambda + CloudWatch Events / EventBridge
- e.g., Scale from `db.t3.medium` → `db.r6g.xlarge` at 8 AM, revert at 11 AM

**Best for:** Predictable burst windows where other options are too complex

**Trade-off:** Requires a ~5–10 min downtime during resize; not dynamic

---

## Decision Framework

```
Is the burst predictable?
├── YES → Scheduled Scaling or Scheduled Vertical Scaling
└── NO  → Aurora Serverless v2

Is it read-heavy?
├── YES → Read Replicas + ElastiCache
└── NO (write-heavy) → SQS Queue buffer

Are you getting connection storms?
└── YES → Add RDS Proxy regardless of other choices
```

---

## Recommended Architecture for Most Cases

```
App / Lambda
     │
  RDS Proxy          ← handles connection bursts
     │
Aurora Serverless v2 ← scales compute automatically
     │
ElastiCache Redis    ← absorbs repeated reads
     │
SQS (if write-heavy) ← smooths write spikes
```

This combination covers both read and write bursts, scales down to near-zero cost during quiet periods, and requires the least operational overhead.
