# Kinesis vs Kafka

## Amazon Kinesis Overview

Kinesis is AWS's managed streaming data service. It lets you collect, process, and analyze real-time data streams at scale — think application logs, clickstreams, IoT telemetry, financial transactions, etc.

### Core Concepts

**Streams** are the top-level resource (analogous to a Kafka topic). Each stream is divided into **shards**, which are the unit of throughput and parallelism.

| Concept | Kinesis | Kafka Equivalent |
|---|---|---|
| Stream | Kinesis Data Stream | Topic |
| Shard | Shard | Partition |
| Record | Record | Message / Event |
| Producer | PutRecord / KPL | Producer |
| Consumer | GetRecords / KCL | Consumer Group |
| Sequence Number | Sequence Number | Offset |
| Retention | 24h–365 days | Configurable |

---

### How Kinesis Compares to Kafka

**Similarities:**
- Both are **distributed, ordered, immutable logs** — records are appended and retained for a configurable window
- Both use **partitioning** (shards vs. partitions) for parallelism and ordering guarantees within a partition
- Both support **multiple independent consumers** replaying from the same stream
- Both guarantee **ordering within a shard/partition** via a partition key

**Key Differences:**

| | Kinesis | Kafka |
|---|---|---|
| **Management** | Fully managed by AWS | Self-managed or Confluent Cloud |
| **Scaling** | Manual shard splitting/merging (or on-demand mode) | Add brokers/partitions |
| **Throughput** | 1 MB/s write, 2 MB/s read *per shard* | Higher, more flexible |
| **Retention max** | 365 days | Unlimited (disk-bound) |
| **Ordering** | Per-shard | Per-partition |
| **Consumer model** | Pull-based (or Lambda trigger) | Pull-based |
| **Ecosystem** | Deep AWS integration (Lambda, Firehose, S3, etc.) | Broad connector ecosystem |

---

### Python Examples in AWS Lambda

#### ✍️ Writing to Kinesis (Producer Lambda)

```python
import boto3
import json
import os

kinesis = boto3.client("kinesis", region_name=os.environ["AWS_REGION"])
STREAM_NAME = os.environ["STREAM_NAME"]  # e.g. "my-data-stream"

def lambda_handler(event, context):
    records = [
        {"user_id": "u123", "action": "page_view", "page": "/home"},
        {"user_id": "u456", "action": "purchase",  "item_id": "item_789"},
    ]

    for record in records:
        response = kinesis.put_record(
            StreamName=STREAM_NAME,
            Data=json.dumps(record),          # Must be bytes or str
            PartitionKey=record["user_id"],   # Determines which shard receives it
                                              # Same key → same shard → ordered
        )
        print(f"Shard: {response['ShardId']}, Seq#: {response['SequenceNumber']}")

    return {"statusCode": 200, "body": f"Published {len(records)} records"}
```

> 💡 Use `put_records()` (batch) instead of `put_record()` in production for efficiency — up to 500 records per call.

---

#### 📖 Reading from Kinesis (Consumer Lambda via trigger)

The easiest way to consume in Lambda is to set up a **Kinesis trigger** in the Lambda console. AWS handles the polling and checkpointing for you. Your handler receives a batch of records:

```python
import base64
import json

def lambda_handler(event, context):
    """
    Triggered automatically by Kinesis. 'event' contains a batch of records
    from one or more shards.
    """
    for kinesis_record in event["Records"]:
        # Kinesis data is base64-encoded
        raw = kinesis_record["kinesis"]["data"]
        decoded = base64.b64decode(raw).decode("utf-8")
        record = json.loads(decoded)

        shard_id   = kinesis_record["eventID"]         # shard ID + sequence number
        seq_num    = kinesis_record["kinesis"]["sequenceNumber"]
        partition  = kinesis_record["kinesis"]["partitionKey"]
        timestamp  = kinesis_record["kinesis"]["approximateArrivalTimestamp"]

        print(f"Shard: {shard_id} | Seq: {seq_num} | Key: {partition}")
        print(f"Payload: {record}")

        # Your business logic here
        process_record(record)

def process_record(record):
    print(f"Processing action '{record.get('action')}' for user {record.get('user_id')}")
```

---

#### 🔧 Manual Consumer (without trigger)

If you need more control over shard iteration:

```python
import boto3, json, time, os

kinesis = boto3.client("kinesis", region_name=os.environ["AWS_REGION"])
STREAM_NAME = "my-data-stream"

def lambda_handler(event, context):
    shards = kinesis.list_shards(StreamName=STREAM_NAME)["Shards"]

    for shard in shards:
        iterator_resp = kinesis.get_shard_iterator(
            StreamName=STREAM_NAME,
            ShardId=shard["ShardId"],
            ShardIteratorType="TRIM_HORIZON",  # Start from oldest available record
            # Other options: LATEST, AT_SEQUENCE_NUMBER, AFTER_SEQUENCE_NUMBER, AT_TIMESTAMP
        )
        iterator = iterator_resp["ShardIterator"]

        resp = kinesis.get_records(ShardIterator=iterator, Limit=100)

        for record in resp["Records"]:
            data = json.loads(record["Data"])
            print(f"Got record: {data}")
```

> ⚠️ The manual approach is better suited for one-off backfills. For continuous consumption, prefer the **Lambda trigger** or the **Kinesis Client Library (KCL)** which handles checkpointing, retries, and shard rebalancing — similar to Kafka's consumer group protocol.

---

### Key Gotchas

- **Data is base64-encoded** in Lambda trigger events — always decode it
- **Partition key** determines shard assignment — hot keys cause hot shards (same problem as Kafka partition skew)
- **Ordering is per-shard only** — if you need global order, use a single shard (limits throughput)
- **On-demand mode** auto-scales shards; provisioned mode gives you fixed, predictable throughput
- Lambda trigger **checkpoints automatically** via a DynamoDB table under the hood — similar to Kafka's `__consumer_offsets`
