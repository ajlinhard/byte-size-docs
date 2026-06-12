## Enhanced Fan-Out (EFO) in AWS Kinesis

### The Problem It Solves

In standard Kinesis, all consumers **share** the shard's read throughput of 2 MB/sec. If you have 3 consumers reading the same shard, they're competing for that same 2 MB/sec — they "starve" each other.

### What EFO Does

EFO gives **each registered consumer its own dedicated 2 MB/sec pipe** per shard, completely isolated from other consumers.

| | Standard (polling) | Enhanced Fan-Out |
|---|---|---|
| Throughput | Shared 2 MB/s per shard | Dedicated 2 MB/s **per consumer** per shard |
| Model | Pull (`GetRecords`) | Push (`SubscribeToShard`) |
| Latency | ~200ms | ~70ms |
| Cost | Lower | Higher (per-consumer-shard-hour fee) |

### The HTTP/2 Push Model

Instead of your consumer **polling** Kinesis ("do you have data for me?"), Kinesis **pushes** records to your consumer over a persistent HTTP/2 connection the moment they arrive. This is what drives the low ~70ms latency.

### A Concrete Example

Say you have a Kinesis stream with 4 shards, and 3 independent services consuming it (analytics, billing, alerts):

**Without EFO:** All 3 share 2 MB/s → each effectively gets ~667 KB/s per shard. Under high load, consumers fall behind.

**With EFO:** Each of the 3 consumers gets its own 2 MB/s per shard → 6 MB/s total read capacity on that stream, no contention.

### When to Use It

- ✅ Multiple independent consumers on the same stream
- ✅ Latency-sensitive workloads (near real-time alerting, etc.)
- ✅ Consumers that process at different speeds and shouldn't block each other
- ❌ Single consumer — standard polling is cheaper and sufficient
- ❌ Cost-sensitive workloads with low throughput needs

The "starve each other" phrasing refers to how, without EFO, a slow or busy consumer eating up read quota can cause other consumers to throttle and fall behind.

---
## Does kinesis really have a ~200ms latency? 
The ~200ms figure needs some context to make sense.Good instinct to question that — the ~200ms figure is commonly misunderstood. It's **not** about connection overhead or per-record network speed. It's a consequence of the **polling model**.

### Why Standard Consumers Have ~200ms Latency

The `GetRecords` API has a limit of **5 reads per second per shard**. With a single consumer, the best you can do is poll every 200ms — hence the ~200ms latency figure. It's essentially the minimum interval between polls, not the time it takes to transmit a record.

So the latency isn't "the network is slow" — it's "your consumer is sitting idle waiting for the next poll window to open."

### It Gets Worse With More Consumers

With five consumers sharing a shard, each can only poll once per second and gets less than 400 KB/s of throughput. The 5 reads/sec limit is shared across all standard consumers on the shard.

### The Real End-to-End Latency Is Actually Sub-Second

The KCL (Kinesis Client Library) defaults to polling every 1 second, which results in average propagation delays typically below 1 second. So in practice most apps see latency well under a second, not exactly 200ms.

If you want to push toward the 200ms floor, you can tune the polling interval down to between 200–250ms — but you'll burn through your 5 reads/sec limit fast if you have multiple consumers doing this.

### So Is Kinesis Fast?

Yes — the **data ingestion** side (writes from producers) is very fast, and the **data availability** is in milliseconds. The latency figure is really about the consumer polling mechanism, not the system's throughput or network speed. EFO sidesteps this entirely by switching to a push model, which is why it achieves ~70ms regardless of how many consumers you have.
