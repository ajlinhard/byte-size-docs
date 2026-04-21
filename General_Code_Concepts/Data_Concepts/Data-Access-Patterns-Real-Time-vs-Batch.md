# Data Access Patterns: Real-Time vs Batch

## Table of Contents

- [Batch Processing Patterns](#batch-processing-patterns)
  - [ETL (Extract, Transform, Load)](#etl-extract-transform-load)
  - [Micro-batching](#micro-batching)
  - [Partitioned Reads (Partition Pruning)](#partitioned-reads-partition-pruning)
  - [MapReduce](#mapreduce)
- [Real-Time / Streaming Patterns](#real-time--streaming-patterns)
  - [Event Streaming (Log-Based)](#event-streaming-log-based)
  - [Change Data Capture (CDC)](#change-data-capture-cdc)
  - [CQRS (Command Query Responsibility Segregation)](#cqrs-command-query-responsibility-segregation)
  - [Materialized Views / Push-Down Aggregation](#materialized-views--push-down-aggregation)
  - [Request-Response (OLTP)](#request-response-oltp)
- [Hybrid / Lambda & Kappa Architectures](#hybrid--lambda--kappa-architectures)
  - [Lambda Architecture](#lambda-architecture)
  - [Kappa Architecture](#kappa-architecture)
  - [HTAP (Hybrid Transactional/Analytical Processing)](#htap-hybrid-transactionalanalytical-processing)
- [The Core Tradeoffs to Keep in Mind](#the-core-tradeoffs-to-keep-in-mind)
- [Ranked by Data Staleness](#ranked-by-data-staleness)
- [Ranked by Complexity](#ranked-by-complexity)
- [Architecture Use Cases & Trade-offs](#architecture-use-cases--trade-offs)
  - [1. Request-Response (OLTP)](#1-request-response-oltp)
  - [2. ETL (Extract, Transform, Load)](#2-etl-extract-transform-load)
  - [3. MapReduce](#3-mapreduce)
  - [4. Micro-batching](#4-micro-batching)
  - [5. Event Streaming (Log-Based)](#5-event-streaming-log-based)
  - [6. Change Data Capture (CDC)](#6-change-data-capture-cdc)
  - [7. Materialized Views / Push-Down Aggregation](#7-materialized-views--push-down-aggregation)
  - [8. CQRS](#8-cqrs)
  - [9. Kappa Architecture](#9-kappa-architecture)
  - [10. Lambda Architecture](#10-lambda-architecture)

Here's a tour of the major patterns, grouped by their processing model.

---

## Batch Processing Patterns

**ETL (Extract, Transform, Load)**
The classic warehouse pattern. You pull data from sources on a schedule, reshape it, and load it into a destination. The key characteristic is that data is *stale by design* — you're always working with a snapshot. Good for reporting, ML training sets, and anything that doesn't need to be current.

**Micro-batching**
A middle ground between batch and real-time. Instead of running once a night, you run every few seconds or minutes. Spark Structured Streaming operates this way. You get near-real-time results without the complexity of true streaming, but you still have latency windows.

**Partitioned Reads (Partition Pruning)**
When querying large datasets, you structure your data by a dimension (date, region, tenant) so queries only scan relevant slices. Hive, Iceberg, and Delta Lake all leverage this heavily. The access pattern is "filter early, read less."

**MapReduce**
The foundational batch pattern: distribute data chunks across workers (Map), process locally, then aggregate results (Reduce). Hadoop pioneered this. It's largely been superseded, but the mental model — *move compute to data, not data to compute* — still underpins most distributed processing.

---

## Real-Time / Streaming Patterns

**Event Streaming (Log-Based)**
Tools like Kafka treat data as an immutable, ordered log of events. Consumers read from offsets and can replay history. The key insight is that the *log is the source of truth*, not any derived state. This decouples producers from consumers and makes the system highly resilient.

**Change Data Capture (CDC)**
Rather than applications explicitly publishing events, you tap into a database's write-ahead log (WAL) and stream every insert/update/delete downstream. Debezium is the classic tool. It's powerful because you get real-time changes without modifying application code.

**CQRS (Command Query Responsibility Segregation)**
You split writes and reads into separate models. The write side accepts commands and emits events; the read side maintains denormalized, pre-computed views optimized for specific queries. This lets you scale reads and writes independently and tailor each store to its workload.

**Materialized Views / Push-Down Aggregation**
Instead of computing aggregates at query time, you maintain them incrementally as data arrives. Every new event updates a running count, sum, or window. Systems like Flink and ksqlDB do this natively. The tradeoff is write amplification for dramatically faster reads.

**Request-Response (OLTP)**
The bread-and-butter pattern: a client asks, a server answers. Optimized for low-latency point lookups on indexed keys. Postgres, MySQL, DynamoDB. The access pattern assumes data is small in scope (one row, one document) and must be current.

---

## Hybrid / Lambda & Kappa Architectures

**Lambda Architecture**
Runs a batch layer (accurate, slow) and a speed layer (approximate, fast) in parallel, merging results at query time. Solves the problem that batch jobs can't catch up to real-time, but the cost is maintaining two separate codebases for the same logic.

**Kappa Architecture**
Eliminates the batch layer entirely — everything is a stream, including historical reprocessing (you just replay the log from the beginning). Simpler operationally, but requires your stream processor to handle both real-time and catch-up loads gracefully.

**HTAP (Hybrid Transactional/Analytical Processing)**
Systems like TiDB or SingleStore try to serve both OLTP and OLAP workloads from the same engine, using columnar and row-based storage together. The goal is to query fresh operational data analytically without a separate pipeline.

---

## The Core Tradeoffs to Keep in Mind

| Dimension | Batch | Real-Time |
|---|---|---|
| Latency | Minutes to hours | Milliseconds to seconds |
| Throughput | Very high | Moderate |
| Complexity | Lower | Higher |
| Cost | Cheaper per record | More expensive |
| Fault tolerance | Easy (re-run the job) | Requires careful offset/state management |

The most important architectural decision is usually: **what's the acceptable staleness of your data?** That answer almost entirely determines which patterns belong in your system.

---
## Ranked by Data Staleness
*1 = freshest, 10 = stalest*

| Rank | Pattern |
|---|---|
| 1 | Request-Response (OLTP) |
| 2 | CDC |
| 3 | Event Streaming |
| 4 | Materialized Views / Push-Down Aggregation |
| 5 | CQRS |
| 6 | HTAP |
| 7 | Kappa |
| 8 | Lambda |
| 9 | Micro-batching |
| 10 | ETL / MapReduce |

**Why this order:**
OLTP is ranked freshest because it reads directly from the source of truth with no intermediary — you're always seeing committed state. CDC is a close second because it captures changes at the database log level with sub-second lag, but there's an irreducible propagation delay between the commit and the downstream consumer seeing it. Event Streaming sits just below CDC because consumers read from a log that's always slightly behind the producer, and consumer lag can grow under load. Materialized Views and CQRS both introduce a derived layer that trails the write model — Materialized Views rank slightly higher because they update continuously, whereas CQRS read models can have configurable (sometimes deliberate) eventual consistency windows. HTAP sits in the middle because even though it targets freshness, the analytical engine still has to sync from the transactional store, introducing a small but non-trivial gap. Kappa beats Lambda because it has a single pipeline with no batch reconciliation step — its staleness is purely a function of streaming lag. Lambda is staler because the batch layer, which produces the authoritative results, runs on a schedule, and the speed layer is only an approximation until the batch catches up. Micro-batching is near the bottom because freshness is fundamentally bounded by the batch interval — even at 30 seconds, that's a hard floor on staleness. ETL and MapReduce share last because they are explicitly designed around scheduled, periodic runs — staleness is measured in hours or days by design, not as a flaw.

---

## Ranked by Complexity
*1 = simplest, 10 = most complex*

| Rank | Pattern |
|---|---|
| 1 | ETL |
| 2 | MapReduce |
| 3 | Request-Response (OLTP) |
| 4 | Micro-batching |
| 5 | Materialized Views |
| 6 | Event Streaming |
| 7 | CDC |
| 8 | CQRS |
| 9 | Kappa |
| 10 | Lambda |

**Why this order:**
ETL is the simplest because the mental model is linear and the failure modes are easy — if a job fails, you re-run it. There's no state to reason about between runs. MapReduce ranks just above it because distributing work across nodes adds operational overhead, but the programming model (map, shuffle, reduce) is still conceptually clean and deterministic. OLTP ranks third because while databases themselves are complex internally, the *access pattern* is simple — a developer just issues queries against an indexed store. Micro-batching edges past OLTP because now you're operating a streaming runtime (Spark, Flink) even if it's behaving batch-like, which adds scheduling, checkpointing, and deployment concerns. Materialized Views add incremental maintenance logic on top of streaming — you have to reason about partial updates, out-of-order events, and view correctness, which is non-trivial. Event Streaming introduces consumer group coordination, offset management, partition rebalancing, and schema evolution — each a distinct failure surface. CDC is harder than raw event streaming because you're coupling tightly to database internals (WAL formats, replication slots), which vary by vendor and break in subtle ways during schema changes or failovers. CQRS compounds event streaming complexity by requiring you to design and maintain two separate models — any time the read model falls out of sync with the write model, debugging is painful. Kappa ranks second-to-last because while it's conceptually simpler than Lambda, running a single streaming system that handles both real-time traffic *and* historical reprocessing at the same time demands deep expertise in backpressure, state management, and exactly-once semantics. Lambda is the most complex because it's essentially Kappa *plus* a full batch system, and you have to keep both correct and consistent — the same business logic expressed twice in different paradigms, with a merge layer on top.

---
## Architecture Use Cases & Trade-offs

---

### 1. Request-Response (OLTP)

**Use Cases**
- User authentication and session management — you need the current password hash and account state right now, not from 5 minutes ago
- E-commerce cart and inventory — stock levels must reflect the latest reservations to avoid overselling
- Financial transactions — account balances must be strongly consistent so debits and credits are always accurate
- Any user-facing feature where the person expects to see the effect of their own action immediately

**Trade-offs**

| Strength | Weakness |
|---|---|
| Guaranteed consistency — reads reflect latest committed writes | Terrible at aggregations across large datasets — full table scans destroy performance |
| Simple mental model for developers | Doesn't scale horizontally for reads without significant engineering (read replicas, sharding) |
| Mature tooling with decades of optimization | Write throughput hits a ceiling — a single primary node is a bottleneck |
| ACID guarantees make failure recovery predictable | Schema changes are painful and often require downtime or careful migration strategies |

---

### 2. ETL (Extract, Transform, Load)

**Use Cases**
- Nightly reporting pipelines feeding business intelligence dashboards that executives review in the morning
- Consolidating data from many source systems (CRM, ERP, support tools) into a single warehouse for cross-functional analysis
- Machine learning feature pipelines where training data is prepared overnight for next-day model runs
- Regulatory and compliance reporting where the requirement is a point-in-time snapshot, not a live view

**Trade-offs**

| Strength | Weakness |
|---|---|
| Simple to reason about — it's just a script that runs on a schedule | Data is stale by design — the window between runs is a blind spot |
| Easy to rerun and recover from failures | A failed job blocks all downstream consumers until it's fixed and rerun |
| Well-understood tooling (Airflow, dbt, Fivetran) with huge ecosystems | Load operations can put significant pressure on source systems during extraction windows |
| Transformations happen in bulk, which is computationally efficient | Poor fit for anything requiring freshness — you can't ETL your way to real-time |

---

### 3. MapReduce

**Use Cases**
- Processing petabytes of raw log files to extract structured signals — web crawls, clickstream analysis, ad impression aggregation
- Batch feature engineering at massive scale where you're joining terabytes across many datasets
- Index building for search engines, where the entire corpus is reprocessed periodically
- Scientific computing over enormous datasets — genomics, physics simulations, satellite imagery

**Trade-offs**

| Strength | Weakness |
|---|---|
| Scales horizontally to virtually any dataset size | Disk I/O heavy — every shuffle writes intermediate results to disk, making it slow |
| Fault tolerant by design — failed tasks are retried on other nodes | High latency — even simple jobs take minutes because of job startup and shuffle overhead |
| Commodity hardware — no special infrastructure required | Largely superseded by Spark, which keeps intermediate data in memory and is 10–100x faster |
| Deterministic and reproducible — same input always produces same output | Programming model is rigid — not everything maps cleanly to map and reduce phases |

---

### 4. Micro-batching

**Use Cases**
- Fraud detection where you need to flag suspicious transactions within seconds, but per-event latency isn't the constraint
- Aggregating IoT sensor readings every 30 seconds for monitoring dashboards
- Near-real-time ETL where the business needs fresher data than nightly but can tolerate a minute of lag
- A/B test metric collection where you want running totals updated frequently but not continuously

**Trade-offs**

| Strength | Weakness |
|---|---|
| Dramatically simpler than true streaming — the batch abstraction is easier to reason about | Latency has a hard floor — you can never do better than the batch interval, no matter what |
| Good throughput — batching amortizes per-record overhead | Bursty resource usage — compute spikes at the end of every interval rather than spreading evenly |
| Easier exactly-once semantics than event-at-a-time streaming | Feels like a compromise — you take on streaming complexity without getting true streaming freshness |
| Spark's Structured Streaming makes it approachable with familiar APIs | Windowing across batch boundaries requires careful state management |

---

### 5. Event Streaming (Log-Based)

**Use Cases**
- Decoupling microservices — a payment service emits an event, and fulfillment, notifications, and analytics all consume it independently without knowing about each other
- Activity feeds and audit logs where you need an immutable, ordered history of what happened
- Real-time analytics pipelines where multiple downstream systems need to consume the same event stream differently
- Event sourcing — storing the sequence of events as the system of record, with current state being derived by replaying them

**Trade-offs**

| Strength | Weakness |
|---|---|
| Decouples producers and consumers completely — each evolves independently | Consumer lag is a first-class operational concern you have to monitor and manage continuously |
| Replayability — you can reprocess history by rewinding the offset | Schema evolution is painful — a breaking change in an event schema can break all consumers |
| High throughput — Kafka handles millions of events per second | Ordering guarantees only hold within a partition, which creates complexity for globally ordered events |
| Consumers can scale independently by adding partition readers | Debugging is harder — the event log shows what happened but not why, and tracing across consumers requires correlation IDs and distributed tracing |

---

### 6. Change Data Capture (CDC)

**Use Cases**
- Keeping a search index (Elasticsearch) in sync with a Postgres database without application-level dual writes
- Replicating data from an operational database into a data warehouse in near real-time
- Invalidating caches precisely — instead of TTL-based expiry, you invalidate a cache entry the moment the underlying row changes
- Feeding downstream microservices with changes to a shared database without introducing tight coupling through direct queries

**Trade-offs**

| Strength | Weakness |
|---|---|
| Zero application code changes required — you tap the database log transparently | Deeply coupled to database internals — WAL format differences between Postgres, MySQL, and Oracle mean your CDC setup isn't portable |
| Captures every change including deletes, which application-level event publishing often misses | Schema changes (adding or renaming columns) can break the CDC pipeline in subtle and hard-to-debug ways |
| Sub-second propagation from source to consumers | Replication slots in Postgres hold back WAL cleanup — a lagging consumer can cause disk to fill on the source |
| Works with legacy systems that have no event publishing capability | Initial snapshot (bootstrapping) of existing data before streaming begins is operationally complex |

---

### 7. Materialized Views / Push-Down Aggregation

**Use Cases**
- Leaderboards and ranking systems — precompute top-N scores incrementally rather than running an expensive sort at query time
- Real-time dashboards with fixed metrics — active users, revenue in the last hour, error rates — where the query shape is known in advance
- Session aggregation — rolling up raw clickstream events into per-user session summaries continuously
- Precomputing joins across large tables so read queries hit a flat, denormalized structure instead of doing expensive joins at runtime

**Trade-offs**

| Strength | Weakness |
|---|---|
| Dramatically faster reads — the answer is precomputed, queries just look it up | Only works for queries you anticipated — ad hoc queries against the raw data bypass the view entirely |
| Incrementally maintained, so compute is spread evenly over time rather than spiking at query time | Write amplification — every incoming event may update multiple views, increasing write pressure |
| Can absorb out-of-order events by reprocessing affected windows | Views can become stale or incorrect if the logic changes — invalidation and rebuilding is expensive |
| Reduces load on upstream databases by serving reads from the derived store | State management for time windows gets complex — late-arriving data may require retroactive corrections |

---

### 8. CQRS

**Use Cases**
- High-traffic applications where reads vastly outnumber writes — social feeds, product catalogs — and you want to scale each independently
- Systems with fundamentally different read and write shapes — a write is a structured command, but reads are denormalized, user-specific, precomputed views
- Event sourcing systems where the write side is an append-only event log and the read side reconstructs views from that log
- Multi-tenant SaaS where different tenants need different read projections of the same underlying data

**Trade-offs**

| Strength | Weakness |
|---|---|
| Read and write sides scale independently — you can add read replicas without touching the write path | Eventual consistency between command and query models is a hard concept to communicate to product teams — users sometimes see stale data immediately after an action |
| Read models can be fully optimized for specific query patterns | Two codebaths to maintain — any business logic change may need to be reflected in both models |
| Failures on the read side don't affect writes | Debugging cross-model inconsistencies is painful and requires careful event tracing |
| Enables multiple specialized read models from a single write model | Significant upfront design investment — wrong event boundaries early on are expensive to refactor |

---

### 9. Kappa Architecture

**Use Cases**
- Unified pipelines where the same streaming logic handles both live traffic and historical reprocessing by replaying the log from offset zero
- Organizations that want to simplify away the dual-system complexity of Lambda while retaining reprocessing capability
- Real-time ML feature pipelines where features need to be computed consistently across both training (historical) and serving (live) contexts
- Systems where business logic changes frequently and you can't afford to maintain two separate implementations of the same transformation

**Trade-offs**

| Strength | Weakness |
|---|---|
| Single codebase for both real-time and batch — no logic duplication | Reprocessing historical data competes with live traffic for the same cluster resources |
| Simpler operationally than Lambda — one system to monitor and maintain | Requires your stream processor to support exactly-once semantics robustly, which is non-trivial to configure correctly |
| Log replay is a first-class feature — rollback and reprocessing are built in | Long retention in Kafka gets expensive — you need to store potentially years of data to enable full reprocessing |
| Encourages immutable, event-driven design throughout the stack | Not all transformations are naturally streamable — some batch operations (global sorts, full dataset joins) are awkward to express as streams |

---

### 10. Lambda Architecture

**Use Cases**
- Systems that need authoritative, accurate historical results (batch layer) but also need to show approximate real-time numbers while the batch catches up (speed layer)
- Large-scale analytics platforms at organizations with mature data teams who can sustain the operational overhead of two parallel systems
- Scenarios where reprocessing with corrected logic is a regular business requirement — you want the batch layer to periodically overwrite the speed layer's approximations
- Enterprises with existing batch infrastructure who want to add real-time capability incrementally without replacing the batch system

**Trade-offs**

| Strength | Weakness |
|---|---|
| Batch layer provides a reliable, accurate ground truth that can always be recomputed | The same business logic must be implemented twice — once in the batch layer and once in the speed layer — and keeping them in sync is a constant source of bugs |
| Speed layer lets you show something current without waiting for batch | Merging results at query time adds latency and complexity to every read |
| Proven at scale — companies like LinkedIn ran this pattern across petabytes | Operationally the most expensive pattern — two full systems to provision, monitor, and tune |
| Failure in one layer doesn't bring the whole system down | The speed layer's results are explicitly approximate — for some domains (finance, compliance) this is unacceptable |
