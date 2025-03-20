# Python Kafka Cheatsheet

## Setup and Installation

```python
# Install kafka-python
pip install kafka-python

# For admin operations
pip install confluent-kafka
```

## Producer Operations

### Basic Producer

```python
from kafka import KafkaProducer

# Create a simple producer
producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Send a message
producer.send('my_topic', {'key': 'value'})

# Flush to ensure all messages are sent
producer.flush()

# Close producer
producer.close()
```

### Advanced Producer Settings

```python
from kafka import KafkaProducer
import json

# Configure producer with additional settings
producer = KafkaProducer(
    bootstrap_servers=['broker1:9092', 'broker2:9092'],
    client_id='my-producer',
    acks='all',                   # Wait for all replicas
    retries=3,                    # Retry failed requests
    retry_backoff_ms=100,         # Backoff time between retries
    max_in_flight_requests_per_connection=5,
    linger_ms=5,                  # Batch delay
    batch_size=16384,             # Batch size in bytes
    buffer_memory=33554432,       # 32MB buffer
    compression_type='snappy',    # Compression: 'gzip', 'snappy', 'lz4', or None
    key_serializer=lambda k: k.encode('utf-8') if k else None,
    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
    security_protocol='SSL',      # Options: PLAINTEXT, SSL, SASL_PLAINTEXT, SASL_SSL
    ssl_cafile='/path/to/ca.pem',
    ssl_certfile='/path/to/cert.pem',
    ssl_keyfile='/path/to/key.pem'
)
```

### Sending Messages with Callbacks

```python
from kafka import KafkaProducer

def on_send_success(record_metadata):
    print(f"Topic: {record_metadata.topic}")
    print(f"Partition: {record_metadata.partition}")
    print(f"Offset: {record_metadata.offset}")

def on_send_error(excp):
    print('Error sending message:', excp)

# Send with callback
future = producer.send('my_topic', key=b'my_key', value=b'my_value')
future.add_callback(on_send_success).add_errback(on_send_error)

# Or use synchronous sending
try:
    record_metadata = producer.send('my_topic', b'message').get(timeout=10)
    print(f"Message sent to {record_metadata.topic}-{record_metadata.partition} at offset {record_metadata.offset}")
except Exception as e:
    print(f"Failed to send message: {e}")
```

### Producer with Avro Serialization

```python
# Install dependencies
# pip install confluent-kafka confluent-kafka[avro] avro-python3

from confluent_kafka import avro
from confluent_kafka.avro import AvroProducer

value_schema_str = """
{
   "namespace": "my.test",
   "name": "value",
   "type": "record",
   "fields" : [
     {"name": "name", "type": "string"},
     {"name": "age", "type": "int"}
   ]
}
"""

key_schema_str = """
{
   "namespace": "my.test",
   "name": "key",
   "type": "record",
   "fields" : [
     {"name": "id", "type": "string"}
   ]
}
"""

value_schema = avro.loads(value_schema_str)
key_schema = avro.loads(key_schema_str)

avro_producer = AvroProducer({
    'bootstrap.servers': 'localhost:9092',
    'schema.registry.url': 'http://localhost:8081'
}, default_key_schema=key_schema, default_value_schema=value_schema)

avro_producer.produce(
    topic='my_topic',
    value={'name': 'John', 'age': 25},
    key={'id': '1'}
)
avro_producer.flush()
```

## Consumer Operations

### Basic Consumer

```python
from kafka import KafkaConsumer
import json

# Create a simple consumer
consumer = KafkaConsumer(
    'my_topic',
    bootstrap_servers=['localhost:9092'],
    auto_offset_reset='earliest',   # 'latest', 'earliest', 'none'
    enable_auto_commit=True,
    group_id='my-group',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

# Consume messages
for message in consumer:
    print(f"Topic: {message.topic}, Partition: {message.partition}, Offset: {message.offset}")
    print(f"Key: {message.key}, Value: {message.value}")
```

### Advanced Consumer Settings

```python
from kafka import KafkaConsumer
import json

# Configure consumer with additional settings
consumer = KafkaConsumer(
    'topic1', 'topic2',            # Multiple topics
    bootstrap_servers=['broker1:9092', 'broker2:9092'],
    client_id='my-consumer',
    group_id='my-group',
    enable_auto_commit=True,
    auto_commit_interval_ms=5000,  # Commit every 5 seconds
    auto_offset_reset='earliest',  # Start from beginning if no offset
    max_poll_records=500,          # Max records per poll
    max_poll_interval_ms=300000,   # Heartbeat timeout
    session_timeout_ms=10000,      # Session timeout
    heartbeat_interval_ms=3000,    # Heartbeat interval
    key_deserializer=lambda k: k.decode('utf-8') if k else None,
    value_deserializer=lambda v: json.loads(v.decode('utf-8')),
    fetch_max_bytes=52428800,      # 50MB
    max_partition_fetch_bytes=1048576,  # 1MB per partition
    security_protocol='SSL',
    ssl_cafile='/path/to/ca.pem',
    ssl_certfile='/path/to/cert.pem',
    ssl_keyfile='/path/to/key.pem'
)
```

### Manual Offset Management

```python
from kafka import KafkaConsumer, TopicPartition
import json

consumer = KafkaConsumer(
    bootstrap_servers=['localhost:9092'],
    auto_offset_reset='earliest',
    enable_auto_commit=False,      # Disable auto commit
    group_id='my-group',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

# Manually assign partitions
topic_partition = TopicPartition('my_topic', 0)  # Partition 0
consumer.assign([topic_partition])

# Seek to a specific offset
consumer.seek(topic_partition, 42)  # Start from offset 42

# Or seek to beginning/end
consumer.seek_to_beginning()  # All assigned partitions
# consumer.seek_to_beginning([topic_partition])  # Specific partition
# consumer.seek_to_end()

# Get current position
position = consumer.position(topic_partition)
print(f"Current position: {position}")

# Consume and manually commit
for message in consumer:
    print(f"Received: {message.value}")
    
    # Process message...
    
    # Commit offset manually
    consumer.commit()
    
    # Or commit specific offsets
    consumer.commit({
        TopicPartition(message.topic, message.partition): message.offset + 1
    })
```

### Consumer with Specific Partitions

```python
from kafka import KafkaConsumer, TopicPartition

# Create consumer without subscribing to topics
consumer = KafkaConsumer(
    bootstrap_servers=['localhost:9092'],
    group_id='my-group'
)

# Manually assign specific partitions
partition0 = TopicPartition('my_topic', 0)
partition1 = TopicPartition('my_topic', 1)
consumer.assign([partition0, partition1])

# Get beginning and end offsets
start_offsets = consumer.beginning_offsets([partition0, partition1])
end_offsets = consumer.end_offsets([partition0, partition1])

print(f"Start offsets: {start_offsets}")
print(f"End offsets: {end_offsets}")

# Consume messages
for message in consumer:
    print(f"Received: {message.value}")
```

### Consumer with Avro Deserialization

```python
from confluent_kafka.avro import AvroConsumer
from confluent_kafka.avro.serializer import SerializerError

avro_consumer = AvroConsumer({
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'my-group',
    'schema.registry.url': 'http://localhost:8081',
    'auto.offset.reset': 'earliest'
})

avro_consumer.subscribe(['my_topic'])

try:
    while True:
        msg = avro_consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            print(f"Consumer error: {msg.error()}")
            continue
            
        print(f"Key: {msg.key()}, Value: {msg.value()}")
except KeyboardInterrupt:
    pass
finally:
    avro_consumer.close()
```

## Admin Operations

### Create and Manage Topics

```python
from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError

# Create admin client
admin_client = KafkaAdminClient(
    bootstrap_servers=['localhost:9092'],
    client_id='admin-client'
)

# Create new topics
topic_list = [
    NewTopic(
        name="new_topic",
        num_partitions=3,
        replication_factor=2,
        topic_configs={"retention.ms": "86400000"}  # 1 day retention
    )
]

try:
    admin_client.create_topics(new_topics=topic_list)
    print("Topic created successfully")
except TopicAlreadyExistsError:
    print("Topic already exists")

# List topics
topics = admin_client.list_topics()
print(f"Topics: {topics}")

# Delete topics
admin_client.delete_topics(["topic_to_delete"])
```

### Using Confluent-Kafka for Advanced Admin Operations

```python
from confluent_kafka.admin import AdminClient, NewTopic, ConfigResource, ConfigSource
from confluent_kafka import KafkaException

# Create admin client
admin = AdminClient({'bootstrap.servers': 'localhost:9092'})

# Create topics
new_topics = [
    NewTopic(
        "new_topic",
        num_partitions=3,
        replication_factor=1,
        config={"cleanup.policy": "compact", "retention.ms": "86400000"}
    )
]

# Create topics
futures = admin.create_topics(new_topics)

# Wait for operation to complete
for topic, future in futures.items():
    try:
        future.result()  # Blocking call
        print(f"Topic {topic} created")
    except KafkaException as e:
        print(f"Failed to create topic {topic}: {e}")

# Describe configurations
config_resource = ConfigResource('TOPIC', 'my_topic')
futures = admin.describe_configs([config_resource])

for resource, future in futures.items():
    try:
        configs = future.result()
        for config in configs.items():
            print(f"{config[0]} = {config[1].value} (Default: {config[1].is_default})")
    except KafkaException as e:
        print(f"Failed to describe configs: {e}")

# Alter configurations
config_resource = ConfigResource('TOPIC', 'my_topic', {'retention.ms': '604800000'})  # 7 days
futures = admin.alter_configs([config_resource])

# Delete topics
futures = admin.delete_topics(['topic_to_delete'])
```

### Managing Consumer Groups

```python
from confluent_kafka.admin import AdminClient

admin = AdminClient({'bootstrap.servers': 'localhost:9092'})

# List consumer groups
groups = admin.list_consumer_groups()
print("Consumer groups:")
for group in groups.valid:
    print(f"  {group.group_id}")

# Describe consumer groups
results = admin.describe_consumer_groups(['my-group'])
for group_id, result in results.items():
    if result.error is not None:
        print(f"Error describing {group_id}: {result.error}")
        continue
    
    print(f"Group: {group_id}")
    for member in result.members:
        print(f"  Member: {member.member_id}, Client ID: {member.client_id}")
        print(f"  Assignment: {member.assignment.topic_partitions}")

# Delete consumer groups
results = admin.delete_consumer_groups(['group-to-delete'])
for group_id, result in results.items():
    if result.error is not None:
        print(f"Error deleting {group_id}: {result.error}")
    else:
        print(f"Successfully deleted {group_id}")
```

### Describe and Alter Partition Assignments

```python
from confluent_kafka.admin import AdminClient
from confluent_kafka import TopicPartition

admin = AdminClient({'bootstrap.servers': 'localhost:9092'})

# List consumer group offsets
result = admin.list_consumer_group_offsets('my-group')
if result.error is not None:
    print(f"Error: {result.error}")
else:
    for tp, offset in result.topic_partitions.items():
        print(f"Topic: {tp.topic}, Partition: {tp.partition}, Offset: {offset.offset}")

# Reset consumer group offsets (requires confluent-kafka>=1.5.0)
tps = [TopicPartition('my_topic', 0, 10)]  # Reset to offset 10
results = admin.alter_consumer_group_offsets('my-group', tps)
for tp, error in results.items():
    if error is not None:
        print(f"Error resetting {tp}: {error}")
    else:
        print(f"Successfully reset {tp}")
```

## Error Handling

```python
from kafka.errors import KafkaError, KafkaTimeoutError, NoBrokersAvailable

try:
    # Kafka operation
    producer.send('my_topic', value='test message').get(timeout=10)
except KafkaTimeoutError:
    print("Timeout error occurred")
except NoBrokersAvailable:
    print("No brokers available")
except KafkaError as e:
    print(f"Kafka error: {e}")
```

## Performance Tuning

### Producer Tuning

```python
# High throughput producer
producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    linger_ms=10,             # Batch messages for 10ms
    batch_size=32768,         # 32KB batches (default is 16KB)
    compression_type='snappy',# Use compression
    acks=1,                   # Only wait for leader acknowledgment
    max_in_flight_requests_per_connection=10,
    buffer_memory=67108864    # 64MB buffer (default is 32MB)
)

# High reliability producer
producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    acks='all',              # Wait for all replicas
    retries=5,               # Retry failed sends
    max_in_flight_requests_per_connection=1,  # Preserve order on retries
    enable_idempotence=True  # Exactly-once semantics
)
```

### Consumer Tuning

```python
# High throughput consumer
consumer = KafkaConsumer(
    'my_topic',
    bootstrap_servers=['localhost:9092'],
    group_id='high-throughput-group',
    max_poll_records=1000,             # Fetch more records per poll
    fetch_max_bytes=52428800,          # 50MB max fetch (default 50MB)
    max_partition_fetch_bytes=1048576, # 1MB per partition
    auto_commit_interval_ms=1000,      # Commit every second
    heartbeat_interval_ms=3000         # Send heartbeats every 3 seconds
)

# Batch processing
BATCH_SIZE = 100
batch = []

for message in consumer:
    batch.append(message)
    
    if len(batch) >= BATCH_SIZE:
        process_batch(batch)
        batch = []
        consumer.commit()
```

## Monitoring & Metrics

```python
from kafka import KafkaAdminClient
from kafka.metrics.stats import Avg, Count, Max, Rate

# Get client metrics
admin_client = KafkaAdminClient(
    bootstrap_servers=['localhost:9092'],
    client_id='metrics-client'
)

metrics = admin_client.metrics()

# Parse and print metrics
for metric_name, metric_value in metrics.items():
    print(f"{metric_name}: {metric_value.value}")

# Commonly useful metrics
important_metrics = [
    'kafka.consumer:type=consumer-fetch-manager-metrics,client-id={}'.format(client_id),
    'kafka.consumer:type=consumer-coordinator-metrics,client-id={}'.format(client_id),
    'kafka.producer:type=producer-metrics,client-id={}'.format(client_id)
]
```

## Transaction Support

```python
# Using confluent-kafka
from confluent_kafka import Producer

# Create transactional producer
producer = Producer({
    'bootstrap.servers': 'localhost:9092',
    'transactional.id': 'my-transactional-id',
    # Other configs...
})

# Initialize transactions
producer.init_transactions()

# Start transaction
producer.begin_transaction()

try:
    # Send messages in transaction
    producer.produce('topic1', key='key1', value='value1')
    producer.produce('topic2', key='key2', value='value2')
    
    # Commit transaction
    producer.commit_transaction()
except Exception as e:
    # Abort transaction on error
    producer.abort_transaction()
    print(f"Transaction aborted: {e}")
```
