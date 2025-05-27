# Kafka
If you have heard anything about event-driven architectures or real-time data, then some one has mentioned Kakfa to you. There are a couple flavors of Kafka out there Apcahe Kafka and Confluent Kafka, but both come from the same origins. The Confluent version is build upon the company Confluent with additional features, but the overall concepts are topics, brokers, producers, and consumers:

### Table of Contents:
- [Documentation](#Documentations)
- [Quickstart with Docker](#Quickstart-with-Docker)
- [Kafka Core Concepts](#Kafka-Core-Concepts)
  - [Main Components](#Main-Components)
  - [Other Important Concepts](#Other-Important-Concepts)
- [Common Issues/Questions](#Common-Issues-and-Questions)

## Documentation
- [Apache Kafka](https://kafka.apache.org/)
- [Confluent Kafka](https://www.confluent.io/)
  - [What is Kafka?](https://developer.confluent.io/what-is-apache-kafka/)
  - [Developer Training Articles](https://developer.confluent.io/learn/?utm_medium=sem&utm_source=google&utm_campaign=ch.sem_br.nonbrand_tp.prs_tgt.dsa_mt.dsa_rgn.namer_lng.eng_dv.all_con.confluent-developer&utm_term=&creative=&device=c&placement=&gad_source=1&gclid=CjwKCAjwyfe4BhAWEiwAkIL8sIkJ2IYv8tJOS1vODWU2t593IBuaYb-RAIuXG65UdGXjuF2WNbqzuxoCW0MQAvD_BwE)
  - [Developer Videos](https://developer.confluent.io/courses/apache-kafka/consumers/)
  - [Kafka and Flink](https://docs.confluent.io/platform/current/flink/overview.html)
- Helpful Videos
  - [Apache Kafke Summit Videos](https://kafka.apache.org/videos)
  - [Kafka Overview - TechWorld with Nana](https://www.youtube.com/watch?v=QkdkLdMBuL0&list=PLS04ayi90zF1PrKLib5PsS7zSde8LftNp)

## Quickstart with Docker
https://kafka.apache.org/quickstart

1. Setup/download a docker image via command line:
```bash
    docker pull apache/kafka:3.8.0
```
    ** can also use docker hub to download **
2. Spin up the docker image into a container via the command line:
```bash
    docker run -p 9092:9092 apache/kafka:3.8.0
```
    Note: the terminal will now be owned by the docker containers stdin/out
3. Open a new command line or go to docker hub.
4. Enter the docker containers command line
```bash
    docker exec -it happy_vaughan bash
```
    Docker Hub: Container -> Exec (tab)
5. cd down to the /opt/kafka folder
```bash
  cd /opt/kafka
```
    Note: The Apache Kafka quickstart leaves out this fact.
6. Run the following command to create a topic:
```bash
    bin/kafka-topics.sh --create --topic quickstart-events --bootstrap-server localhost:9092
```
7. Producer thread
```bash
    bin/kafka-console-producer.sh --topic quickstart-events --bootstrap-server localhost:9092
```
8. Consumer thread
```bash
    bin/kafka-console-consumer.sh --topic quickstart-events --from-beginning --bootstrap-server localhost:9092
```

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

---
## Kafka vs. Confluent Kafka for Python: Preferred Library and Differences
---

**Preferred Library for Python**

For Python applications interfacing with Kafka, the two main libraries are:

- **confluent-kafka** (also known as Confluent Kafka Python client)
- **kafka-python**

The preferred library for most modern, production-grade applications is **confluent-kafka**. This is primarily due to its superior performance, feature completeness, and active maintenance by Confluent, the company founded by the creators of Apache Kafka[1][2].

**Key Reasons for Preference:**

- **Performance:** confluent-kafka is a wrapper around the high-performance C/C++ library `librdkafka`, offering much better throughput and lower latency than the pure Python implementation of kafka-python[1][2].
- **Feature Set:** confluent-kafka supports advanced Kafka and Confluent features, including transactions, Schema Registry, message compression, and more, making it suitable for enterprise and high-throughput scenarios[1][2].
- **Maintenance and Support:** confluent-kafka is actively maintained and often provides early support for new Kafka features. kafka-python, while stable, is not updated as frequently and may lag behind in supporting new Kafka capabilities[2][3].

kafka-python is still used for smaller projects or where a pure Python solution is desired, but it lacks some advanced features and is generally slower[1][2].

## Differences Between confluent-kafka and kafka-python

| Feature/Aspect           | confluent-kafka                  | kafka-python              |
|-------------------------|----------------------------------|--------------------------|
| Implementation          | Wrapper around C/C++ (librdkafka)| Pure Python              |
| Performance             | High throughput, low latency     | Slower, higher overhead  |
| Feature Completeness    | Advanced features (transactions, Schema Registry, compression, etc.) | Basic Kafka features, lacks some advanced capabilities |
| Installation            | Requires binary dependencies     | Pure pip install         |
| Maintenance             | Actively maintained by Confluent | Stable, but less active  |
| Community/Support       | Large, backed by Confluent       | Smaller, community-driven|
| Kafka Version Support   | Early support for new versions   | May lag behind           |

## Relationship Between Apache Kafka and Confluent Kafka

- **Apache Kafka** is the open-source core platform for distributed event streaming, maintained by the Apache Software Foundation.
- **Confluent** is a company founded by the creators of Apache Kafka and is the main contributor to the open-source Kafka project[4].
- **Confluent Kafka** (or Confluent Platform) refers to the ecosystem of tools and enhancements built by Confluent on top of Apache Kafka. This includes additional features like Schema Registry, Kafka Connect, ksqlDB, and enterprise-grade security and management tools[4].
- The **confluent-kafka Python client** is open source and can connect to any Kafka broker (including pure Apache Kafka), but it is optimized for and integrates best with the broader Confluent ecosystem[1][2][4].

> "Confluent adds additional tools on top of Apache Kafka. Those tools are offered as Confluent Open Source and Confluent Enterprise which both ship with Apache Kafka[4]

## Summary

- **confluent-kafka** is generally the preferred Python library for Kafka due to its performance, features, and support.
- **kafka-python** is suitable for simpler or smaller-scale use cases where pure Python is a requirement.
- **Confluent** is the company behind Kafka and adds value on top of the open-source Kafka core, but both libraries can connect to open-source Kafka brokers.
- The open-source Kafka project and Confluent's offerings are closely linked, with Confluent leading much of the development and enhancement of the Kafka ecosystem[4].

Citations:
[1] https://quix.io/blog/choosing-python-kafka-client-comparative-analysis
[2] https://stackshare.io/stackups/pypi-confluent-kafka-vs-pypi-kafka-python
[3] https://www.reddit.com/r/apachekafka/comments/ul5rtt/using_kafka_with_python_is_confluent_the_only/
[4] https://stackoverflow.com/questions/41955467/relationship-between-apache-kafka-and-confluent
[5] https://stackoverflow.com/questions/73049329/python-kafka-consumer-library-that-supports-scalability-and-recoverability
[6] https://www.openlogic.com/blog/apache-kafka-vs-confluent-kafka-whats-best-your-organization
[7] https://www.confluent.io/apache-kafka-vs-confluent/
[8] https://dattell.com/data-architecture-blog/comparing-confluent-kafka-and-apache-kafka/
[9] https://discuss.python.org/t/python-library-for-connecting-kafka-message-queue-client-side-and-server-side-programming/13308
[10] https://docs.confluent.io/kafka-clients/python/current/overview.html
[11] https://stackoverflow.com/questions/60457993/kafka-different-partitions-are-selected-python-confluent-kafka-library-v-s-apach
[12] https://stackoverflow.com/questions/35896524/is-the-confluent-platform-based-on-kafka-free-open-source
[13] https://docs.confluent.io/platform/current/get-started/kafka-basics.html
[14] https://www.reddit.com/r/mlops/comments/10di684/which_kafka_python_libraries_do_you_use_a/
[15] https://pypi.org/project/kafka-python/
[16] https://kafkaide.com/learn/how-to-start-using-apache-kafka-in-python/
[17] https://dev.to/sats268842/best-practices-for-kafka-in-python-2me5
[18] https://matthewrocklin.com/blog/work/2017/10/10/kafka-python
[19] https://stackoverflow.com/questions/65983009/difference-between-faust-vs-kafka-python
[20] https://stackoverflow.com/questions/62865621/is-there-any-drawbacks-of-using-apache-kafka-with-python-instead-of-java
[21] https://github.com/confluentinc/confluent-kafka-python/issues/418
[22] https://www.reddit.com/r/apachekafka/comments/o393gd/confluent_cloud_vs_kafka_open_source/
[23] https://www.youtube.com/watch?v=woFROrd3iTw
[24] https://sidgs.com/why-enterprises-are-moving-from-open-source-kafka-to-confluent-platform/
[25] https://docs.confluent.io/platform/current/connect/index.html

---
# Common Issues and Questions
---
There are many behaviors in Kafka when initially learning the system many users are perplexed by. Especially, before you master the complex, but useful interactions behind the scenes of kafka backend/engine. Hopefully, some of the questions and links below help.

### Why does leaving a kafka consumer idle for a few minutes result in no records from its next poll, even if one new record/event was published? If you rerun it immediately one is found?
This behavior with Kafka consumers is actually quite common and relates to how Kafka's consumer group protocol works. Let me explain what's happening.

When a Kafka consumer is idle for a few minutes and then polls, it might not receive records immediately due to several factors:

1. **Session timeout**: When a consumer is idle, it stops sending heartbeats to the Kafka broker. If the idle period exceeds the `session.timeout.ms` setting (typically 10-30 seconds by default), the broker assumes the consumer has failed and triggers a rebalance of partitions among remaining consumers in the group.

2. **Rebalance process**: When you poll again after being idle, the consumer first needs to rejoin the consumer group and participate in a rebalance. During this first poll, it's primarily focused on group coordination rather than fetching records.

3. **Offset commit/fetch**: After a rebalance, the consumer needs to determine where to start consuming from. It may need to fetch committed offsets from the __consumer_offsets topic.

4. **Minimum fetch size**: If you have configured `fetch.min.bytes` to something greater than the size of your single message, Kafka will wait until that threshold is met or until `fetch.max.wait.ms` is reached.

When you run the poll operation a second time immediately afterward, you get the record because:
- The consumer has now rejoined the group
- Partition assignments are complete
- Offset positions are established
- The consumer can now fetch actual records

To avoid this behavior, you could:
- Decrease your `session.timeout.ms` value
- Adjust your `heartbeat.interval.ms` to be lower
- Make sure your poll loop continues running, even if processing is idle
- Use a longer `poll()` timeout value
