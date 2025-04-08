# Kafka
If you have heard anything about event-driven architectures or real-time data, then some one has mentioned Kakfa to you. There are a couple flavors of Kafka out there Apcahe Kafka and Confluent Kafka, but both come from the same origins. The Confluent version is build upon the company Confluent with additional features, but the overall concepts are topics, brokers, producers, and consumers:

### Table of Contents:
- [Documentation](#Documentations)
- [Quickstart with Docker](#Quickstart-with-Docker)
- [Kafka Core Concepts](#Kafka-Core-Concepts)
  - [Main Components](#Main-Components)
  - [Other Important Concepts](#Other-Important-Concepts)

## Documentation
- [Apache Kafka](https://kafka.apache.org/)
- [Confluent Kafka](https://www.confluent.io/)
- Helpful Videos
  - [Apache Kafke Summit Videos](https://kafka.apache.org/videos)
  - [Kafka Overview - TechWorld with Nana](https://www.youtube.com/watch?v=QkdkLdMBuL0&list=PLS04ayi90zF1PrKLib5PsS7zSde8LftNp)

## Quickstart with Docker
https://kafka.apache.org/quickstart

1. Setup/download a docker image via command line:
    docker pull apache/kafka:3.8.0
    ** can also use docker hub to download **
2. Spin up the docker image into a container via the command line:
    docker run -p 9092:9092 apache/kafka:3.8.0
    Note: the terminal will now be owned by the docker containers stdin/out
3. Open a new command line or go to docker hub.
4. Enter the docker containers command line
    Command Line: docker exec -it happy_vaughan bash
    Docker Hub: Container -> Exec (tab)
5. cd down to the /opt/kafka folder
    Note: The Apache Kafka quickstart leaves out this fact.
6. Run the following command to create a topic:
    bin/kafka-topics.sh --create --topic quickstart-events --bootstrap-server localhost:9092
7. Producer thread
    bin/kafka-console-producer.sh --topic quickstart-events --bootstrap-server localhost:9092
8. Consumer thread
    bin/kafka-console-consumer.sh --topic quickstart-events --from-beginning --bootstrap-server localhost:9092


---
# Kafka Core Concepts
---
## Main Components
### Topic
- A **topic** is a category or feed name to which records are published
- Topics are divided into **partitions** for scalability
- Each partition is an ordered, immutable sequence of records that keeps being appended to
- Records in partitions are assigned sequential IDs called **offsets**
- Topics can have multiple producers and consumers

### Brokers
- **Brokers** are the servers that make up a Kafka cluster
- Each broker hosts some of the topic partitions
- Brokers manage the persistence and replication of message data
- A typical cluster has multiple brokers for redundancy (3-5 is common)
- One broker serves as the **controller** which manages administrative operations

### Producers
- **Producers** publish data to topics of their choice
- Producers can choose which partition to send messages to or use a load-balancing algorithm
- Producers can operate with different reliability guarantees:
  - Fire-and-forget
  - Synchronous sends (wait for acknowledgment)
  - Fully asynchronous operation

### Consumers
- **Consumers** read data from topics by subscribing to them
- Consumers track their location within each partition using **offsets**
- Consumers operate within **consumer groups** for scalability
- Each partition is consumed by exactly one consumer within a group

## Other Important Concepts

### Consumer Groups
- A **consumer group** is a set of consumers sharing the workload of consuming a topic
- Each partition is assigned to exactly one consumer within a group
- This enables horizontal scaling of consumption
- If there are more consumers than partitions, some consumers will be idle

### Partitions
- **Partitions** divide topics for parallel processing
- Each partition can only be consumed by one consumer in a consumer group
- Partitions enable both scalability and ordered delivery guarantees
- Data within a partition is ordered, but there's no ordering guarantee across partitions
- The number of partitions determines the maximum parallelism of consumption

### Offsets
- **Offsets** are sequential IDs assigned to messages in a partition
- Consumers use offsets to track their position
- Offset management can be automatic or manual
- Kafka stores offset information in an internal topic called `__consumer_offsets`

### Replication
- **Replication** is how Kafka provides fault tolerance
- Each partition can have multiple **replicas**
- One replica is the **leader** which handles all reads and writes
- Others are **followers** which replicate the leader
- If a leader fails, a follower becomes the new leader

### Retention
- Kafka can be configured to retain data based on:
  - Time (e.g., 7 days)
  - Size (e.g., 1GB per partition)
  - Both
- This makes Kafka suitable for both streaming and storage

### Compaction
- **Compaction** is an alternative retention mechanism
- Instead of deleting old messages, Kafka keeps the latest value for each key
- Useful for event sourcing and maintaining state

### Connect API
- **Kafka Connect** is a framework for connecting Kafka with external systems
- Provides standardized integration with databases, key-value stores, search indices, and file systems

### Streams API
- **Kafka Streams** is a client library for building applications and microservices
- Enables transformation and enrichment of data within Kafka

### Schema Registry
- While not part of core Kafka, the **Schema Registry** is commonly used
- Manages schemas for Kafka data (often using Avro, Protobuf, or JSON Schema)
- Enforces compatibility between producers and consumers

These concepts together form the foundation of Kafka's architecture, enabling its key characteristics: high throughput, fault tolerance, horizontal scalability, and durability.
