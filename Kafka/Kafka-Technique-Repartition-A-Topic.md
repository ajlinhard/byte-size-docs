# Repartitioning a Kafka Topic to Add Another Consumer

Unfortunately, Kafka doesn't support directly changing the number of partitions for an existing topic without data loss risk. You may have to do this as services scale and the number of consumers needed to keep up grows. But, first a small Kafka functionality thought excercise:

### What happens if you assign extra Consumers to the same partition?
When two or more consumers with the same consumer group ID are assigned to the same Kafka topic, they **will not** be assigned to the same partition. Kafka's consumer group protocol ensures that each partition is assigned to exactly one consumer within a consumer group at any given time.

Here's what actually happens:

1. Kafka's group coordinator (a specialized broker role) manages partition assignment among consumers in the same group.

2. When multiple consumers join the same consumer group, Kafka will distribute the partitions among them, with each partition being assigned to exactly one consumer.

3. If you have more consumers in a group than partitions in the topic, some consumers will be idle and won't receive any messages. For example:
   - If you have a topic with 3 partitions and 5 consumers in the same group
   - Only 3 consumers will be active (one per partition)
   - The remaining 2 consumers will be idle (no partitions assigned)

4. If a consumer fails or leaves the group, Kafka will detect this and trigger a rebalance, reassigning that consumer's partitions to the remaining active consumers in the group.

This one-to-one mapping between partitions and consumers (within a consumer group) is a fundamental aspect of Kafka's design and enables:
- Guaranteed message ordering within a partition
- Load balancing across consumers
- Horizontal scalability up to the number of partitions

This is why the number of partitions in a topic effectively sets the upper limit on how many consumers in a single consumer group can process messages from that topic in parallel.


Here are the approaches to effectively "repartition" a topic:

## Method 1: Create a New Topic with More Partitions

This is the safest approach:

```python
from kafka.admin import KafkaAdminClient, NewTopic
from kafka import KafkaProducer, KafkaConsumer
import json

# 1. Create a new topic with more partitions
admin_client = KafkaAdminClient(
    bootstrap_servers=['localhost:9092'],
    client_id='kafka-admin-client'
)

# Create new topic with increased partition count
original_topic = "user_events"
new_topic = "user_events_expanded"

topic_list = [
    NewTopic(
        name=new_topic,
        num_partitions=8,  # Increased from original count
        replication_factor=3
    )
]

admin_client.create_topics(new_topics=topic_list)
print(f"Created new topic {new_topic} with 8 partitions")

# 2. Set up a consumer-producer pipeline to move data
consumer = KafkaConsumer(
    original_topic,
    bootstrap_servers=['localhost:9092'],
    auto_offset_reset='earliest',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda x: json.dumps(x).encode('utf-8')
)

# 3. Transfer the data
for message in consumer:
    producer.send(
        new_topic,
        value=message.value,
        # Optional: include same key for maintaining related messages
        key=message.key
    )
    producer.flush()
```

## Method 2: Use Kafka's alter_configs API (Risky for Production)

```python
from kafka.admin import KafkaAdminClient, ConfigResource, ConfigResourceType

admin_client = KafkaAdminClient(
    bootstrap_servers=['localhost:9092']
)

# Increase partitions for an existing topic
topic_name = "user_events"
admin_client.create_partitions({
    topic_name: NewPartitions(total_count=8)  # New total partition count
})

print(f"Increased partitions for {topic_name} to 8")
```

Using confluent-kafka library:

```python
from confluent_kafka.admin import AdminClient, NewPartitions

admin = AdminClient({'bootstrap.servers': 'localhost:9092'})

# Create new partition assignment
topic_name = "user_events"
new_partitions = NewPartitions(8)  # New total count

# Apply the change
result = admin.create_partitions({topic_name: new_partitions})

# Check results
for topic, future in result.items():
    try:
        future.result()  # Wait for operation to complete
        print(f"Successfully increased partitions for {topic}")
    except Exception as e:
        print(f"Failed to increase partitions: {e}")
```

## Method 3: Use Kafka Streams for Repartitioning (Advanced)

```python
from confluent_kafka.streams import StreamsBuilder, KafkaStreams
import time

# Define topology
builder = StreamsBuilder()

# Read from original topic
stream = builder.stream("user_events")

# Write to new topic with repartitioning
stream.to("user_events_repartitioned")

# Build and start the Kafka Streams application
topology = builder.build()
streams = KafkaStreams(topology, {
    'bootstrap.servers': 'localhost:9092',
    'application.id': 'repartition-app'
})

streams.start()

# Let it run for some time to process all messages
try:
    time.sleep(60)  # Adjust based on data volume
finally:
    streams.close()
```

## Important Considerations:

1. **Data Ordering**: Adding partitions to an existing topic can break message ordering guarantees since the partitioning logic changes.

2. **Key Distribution**: If you're using keyed messages, repartitioning will redistribute messages with the same key to different partitions.

3. **Consumer Offset Management**: After repartitioning, consumer offsets need careful management.

4. **Production Impact**: For mission-critical systems, always test thoroughly in staging first.

5. **Downtime Consideration**: Some approaches may require temporarily pausing producers/consumers.

The safest approach is creating a new topic with more partitions and migrating your data and applications to use it, especially in production environments.
