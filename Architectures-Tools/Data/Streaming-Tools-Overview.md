# Streaming Tools Overview

---
## Live Update Streaming Tools
You can update values in streaming tables, but the behavior and mechanisms vary significantly depending on the streaming platform and your specific use case:

**Kafka Streams / Event Sourcing**
In true streaming systems like Kafka, you don't update records in place. Instead, you append new events that represent the update. The latest event for a given key represents the current state. Some systems provide "compacted topics" that automatically clean up old versions.

**Stream Processing Engines**
- **Apache Flink**: Supports updates through changelog streams and can maintain stateful operators that handle updates
- **Apache Storm/Spark Streaming**: Generally append-only, but you can implement update logic in your processing topology
- **Kafka Streams**: Uses changelog semantics where updates are new records with the same key

**Streaming Databases**
- **Apache Pinot**: Supports upserts in real-time tables through primary key-based updates
- **ClickHouse**: Has limited update/delete capabilities, mainly through mutations (which are asynchronous)
- **Apache Druid**: Traditionally append-only, though newer versions support some update scenarios

**Cloud Streaming Solutions**
- **Snowflake Streams**: Capture changes (including updates) as they happen
- **Delta Lake/Apache Hudi**: Support ACID transactions with updates and deletes on streaming data
- **BigQuery**: Streaming inserts are append-only, but you can use DML to update the underlying table

**Key Considerations**
- **Late-arriving data**: Updates might arrive out of order
- **Idempotency**: Your processing logic needs to handle duplicate updates
- **State management**: Maintaining current state while processing updates requires careful design

The approach depends heavily on whether you need exactly-once processing, how you handle out-of-order events, and your consistency requirements.
