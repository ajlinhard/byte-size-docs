
---
# Kafka Consumer Group Info
Here's how to retrieve the current consumer group IDs and their offsets in Python:

## Using kafka-python

```python
from kafka import KafkaAdminClient
from kafka.admin.consumer_group import list_consumer_groups, describe_consumer_groups, list_consumer_group_offsets

# Initialize the admin client
admin_client = KafkaAdminClient(bootstrap_servers=['localhost:9092'])

# List all consumer groups
consumer_groups = list_consumer_groups(admin_client)
group_ids = [group.group_id for group in consumer_groups]
print(f"Available consumer groups: {group_ids}")

# Get offsets for each consumer group
for group_id in group_ids:
    # Get offsets for all topics this consumer group is consuming
    offsets = list_consumer_group_offsets(admin_client, group_id)
    
    print(f"\nGroup: {group_id}")
    for tp, offset_info in offsets.items():
        print(f"  Topic: {tp.topic}, Partition: {tp.partition}, Offset: {offset_info.offset}")
        
        # Optional: Get lag by comparing with end offsets
        consumer_position = offset_info.offset
        end_offsets = admin_client.list_consumer_group_offsets(group_id)
        for tp_end, offset_end in end_offsets.items():
            if tp_end == tp:
                lag = offset_end.offset - consumer_position
                print(f"    Lag: {lag}")
```

## Using confluent-kafka (more comprehensive)

```python
from confluent_kafka.admin import AdminClient
from confluent_kafka import Consumer, TopicPartition, KafkaException

# Initialize the admin client
admin_client = AdminClient({'bootstrap.servers': 'localhost:9092'})

# List all consumer groups
consumer_groups = admin_client.list_consumer_groups()
group_ids = [group.group_id for group in consumer_groups.valid]
print(f"Available consumer groups: {group_ids}")

# Function to get offsets for a specific group
def get_group_offsets(group_id):
    # Create a temporary consumer to get topic info
    consumer = Consumer({
        'bootstrap.servers': 'localhost:9092',
        'group.id': 'offset-checker',  # Temporary group ID
        'enable.auto.commit': 'false'
    })
    
    results = {}
    
    try:
        # Get group metadata from the admin client
        group_metadata = admin_client.describe_consumer_groups([group_id])
        
        # The metadata contains active memberships that show topic assignments
        for member in group_metadata[group_id].members:
            try:
                # Get assigned topic partitions
                assignment = member.assignment
                for topic, partitions in assignment.topic_partitions.items():
                    
                    # Get committed offsets for each partition
                    for partition in partitions:
                        tp = TopicPartition(topic, partition)
                        
                        # Get group committed offset
                        committed = consumer.committed([tp], timeout=5.0)
                        if committed:
                            committed_offset = committed[0].offset
                        else:
                            committed_offset = -1  # No committed offset
                            
                        # Get partition end offset (high watermark)
                        watermarks = consumer.get_watermark_offsets(tp)
                        low_mark, high_mark = watermarks
                        
                        # Calculate lag
                        lag = high_mark - committed_offset if committed_offset >= 0 else -1
                        
                        results[(topic, partition)] = {
                            'committed_offset': committed_offset,
                            'high_watermark': high_mark,
                            'lag': lag,
                            'member_id': member.id
                        }
            except KafkaException as e:
                print(f"Error accessing assignment for member {member.id}: {e}")
                
    except Exception as e:
        print(f"Error describing consumer group {group_id}: {e}")
    finally:
        consumer.close()
        
    return results

# Get and display offsets for each group
for group_id in group_ids:
    print(f"\nGroup: {group_id}")
    offsets = get_group_offsets(group_id)
    
    for (topic, partition), info in offsets.items():
        print(f"  Topic: {topic}, Partition: {partition}")
        print(f"    Committed Offset: {info['committed_offset']}")
        print(f"    High Watermark: {info['high_watermark']}")
        print(f"    Lag: {info['lag']}")
        print(f"    Consumer: {info['member_id']}")
```

## Using the Kafka Command-Line Tools (Bonus)

If you prefer using the command-line tools that come with Kafka, you can do:

```bash
# List all consumer groups
kafka-consumer-groups.sh --bootstrap-server localhost:9092 --list

# Describe a specific consumer group
kafka-consumer-groups.sh --bootstrap-server localhost:9092 --describe --group my-group
```

The command-line output will look something like:

```
GROUP           TOPIC           PARTITION  CURRENT-OFFSET  LOG-END-OFFSET  LAG             CONSUMER-ID                                 HOST            CLIENT-ID
my-group        my-topic        0          45              100             55              consumer-1-9fabb49c-4be9-4f27-8a23-abc123   /172.17.0.1     consumer-1
my-group        my-topic        1          72              100             28              consumer-1-9fabb49c-4be9-4f27-8a23-abc123   /172.17.0.1     consumer-1
my-group        my-topic        2          98              100             2               consumer-2-9fabb49c-4be9-4f27-8a23-def456   /172.17.0.1     consumer-2
```

This shows:
- The current committed offset for each partition
- The log-end-offset (high watermark) for each partition
- The lag (how far behind the consumer is)
- Which consumer is handling which partition

---
# Kafka Scaling Many Consumer Groups
Scalability is always a concern for initial structure. There could indeed be performance and cost issues with creating many consumer instances at scale. Let me explain the potential problems:

### Problems with creating many consumers based on UUID

1. **Resource consumption**: Each Kafka consumer:
   - Creates a TCP connection to the Kafka brokers
   - Requires memory for buffering messages
   - Consumes CPU for polling and message processing
   - Maintains heartbeats with the broker

2. **Group coordination overhead**: 
   - Each unique consumer group triggers Kafka's group rebalancing protocol
   - As the number of consumer groups grows, the coordination overhead on the Kafka cluster increases

3. **Connection limits**:
   - Kafka brokers have connection limits (controlled by `max.connections` setting)
   - Many consumers could exhaust available connections

4. **Increased latency**: 
   - Many consumer groups create more load on the Kafka cluster's coordination process
   - This can lead to slower rebalances and increased latency

5. **Cost implications**:
   - In managed Kafka services (AWS MSK, Confluent Cloud), you often pay for throughput units
   - Multiple consumer groups reading the same data effectively multiplies your consumption costs

### Better approaches for scaling these patterns

Here are improved versions of both patterns to handle scale better:

1. **For Synchronous Pattern**: Use a single consumer with message filtering

```python
# Modified approach for Synchronous Pattern
class BetterSynchronousRequestReply:
    def __init__(self, bootstrap_servers):
        self.bootstrap_servers = bootstrap_servers
        self.request_topic = "request_topic"
        self.reply_topic = "reply_topic"
        
        # Create a shared consumer with a stable group ID
        self.consumer_config = {
            'bootstrap.servers': bootstrap_servers,
            'group.id': 'sync-reply-consumer',  # Stable consumer group ID
            'auto.offset.reset': 'latest',
        }
        self.consumer = Consumer(self.consumer_config)
        self.consumer.subscribe([self.reply_topic])
        
        # Producer config
        self.producer_config = {
            'bootstrap.servers': bootstrap_servers,
        }
        self.producer = Producer(self.producer_config)

    def send_request_and_wait(self, request_data, timeout=30):
        # Create a unique correlation ID for this request
        correlation_id = str(uuid.uuid4())
        
        # Prepare and send message
        message = {
            "payload": request_data,
            "correlation_id": correlation_id,
            "reply_topic": self.reply_topic,
            "timestamp": time.time()
        }
        
        self.producer.produce(
            self.request_topic,
            json.dumps(message).encode('utf-8')
        )
        self.producer.flush()
        
        # Poll for the response with our correlation ID
        start_time = time.time()
        while (time.time() - start_time) < timeout:
            msg = self.consumer.poll(1.0)
            
            if msg is None:
                continue
                
            if msg.error():
                print(f"Consumer error: {msg.error()}")
                continue
                
            try:
                reply_data = json.loads(msg.value().decode('utf-8'))
                
                # Check if this is our reply
                if reply_data.get('correlation_id') == correlation_id:
                    return reply_data.get('payload')
                    
            except Exception as e:
                print(f"Error processing message: {e}")
        
        # If we get here, we timed out
        raise TimeoutError(f"No reply received within {timeout} seconds")
```

2. **For Asynchronous Pattern**: Use a shared consumer thread pool

```python
class ScalableAsyncRequestReply:
    def __init__(self, bootstrap_servers, consumer_count=5):
        self.bootstrap_servers = bootstrap_servers
        self.request_topic = "request_topic"
        self.reply_topic = "reply_topic"
        
        # Store callbacks by correlation ID
        self.callbacks = {}
        self.callbacks_lock = threading.Lock()
        
        # Producer for requests
        self.producer_config = {
            'bootstrap.servers': bootstrap_servers,
        }
        self.producer = Producer(self.producer_config)
        
        # Start a pool of reply listener threads
        self.running = True
        self.consumer_count = consumer_count
        self.reply_threads = []
        
        # Create a thread pool for consumers
        for i in range(consumer_count):
            thread = threading.Thread(
                target=self._reply_listener,
                args=(f'async-reply-consumer-{i}',)  # Pass consumer group suffix
            )
            thread.daemon = True
            thread.start()
            self.reply_threads.append(thread)
    
    def send_request(self, request_data, callback):
        """Send request and register callback for the reply"""
        correlation_id = str(uuid.uuid4())
        
        # Register the callback (thread-safe)
        with self.callbacks_lock:
            self.callbacks[correlation_id] = {
                'callback': callback,
                'context': {
                    'request_data': request_data,
                    'timestamp': time.time()
                }
            }
        
        # Send message
        message = {
            "payload": request_data,
            "correlation_id": correlation_id,
            "reply_topic": self.reply_topic,
            "timestamp": time.time()
        }
        
        self.producer.produce(
            self.request_topic,
            json.dumps(message).encode('utf-8')
        )
        self.producer.flush()
        return correlation_id
    
    def _reply_listener(self, consumer_suffix):
        """Reply listener thread that processes replies"""
        # Each thread in the pool gets a stable consumer group ID
        consumer_config = {
            'bootstrap.servers': self.bootstrap_servers,
            'group.id': f'reply-consumer-{consumer_suffix}',
            'auto.offset.reset': 'latest',
        }
        
        consumer = Consumer(consumer_config)
        consumer.subscribe([self.reply_topic])
        
        try:
            while self.running:
                msg = consumer.poll(1.0)
                
                if msg is None:
                    continue
                    
                if msg.error():
                    print(f"Consumer error: {msg.error()}")
                    continue
                    
                try:
                    reply_data = json.loads(msg.value().decode('utf-8'))
                    correlation_id = reply_data.get('correlation_id')
                    
                    # Thread-safe check for correlation ID
                    callback_info = None
                    with self.callbacks_lock:
                        if correlation_id in self.callbacks:
                            callback_info = self.callbacks.pop(correlation_id)
                    
                    # If found, execute callback
                    if callback_info:
                        callback = callback_info['callback']
                        context = callback_info['context']
                        callback(reply_data.get('payload'), context)
                        
                except Exception as e:
                    print(f"Error processing message: {e}")
        
        finally:
            consumer.close()
```

### Additional Best Practices for Kafka Request-Reply at Scale

1. **Use partitioned reply topics**:
   - Create a reply topic with multiple partitions
   - Route replies to specific partitions using the hash of the correlation ID
   - Each consumer group handles specific partitions, improving parallelism

2. **Implement batching**:
   - For high-throughput scenarios, batch multiple requests into a single Kafka message
   - This reduces the number of network round-trips and improves throughput

3. **Use dedicated reply topics**:
   - For different services or request types, use dedicated reply topics
   - This improves message routing and reduces filtering overhead

4. **Consider timeout and cleanup**:
   - Implement a background thread to clean up callbacks that never receive replies
   - This prevents memory leaks from unclaimed correlation IDs

5. **Use a connection pool**:
   - Share Kafka producer instances across multiple requests
   - Limit the number of concurrent connections

These improvements would make the request-reply patterns much more scalable for high-volume production scenarios where potentially thousands of clients are making requests simultaneously.

---
# Kafka Starting at X Offset
Kafka provides several ways to start a consumer at a specific offset. This is a powerful feature that gives you precise control over message consumption. We want to understand a few concepts though, before looking at the code. These will help you understand how Kafka offsets are managed during processing.

### How Kafka stores Partitions and Offsets
In Kafka, offset values are **per partition**, not global. Each partition maintains its own independent sequence of offsets.

Key points about Kafka offsets:

1. **Partition Specific**: Every message within a partition has a unique, sequential offset value starting from 0.

2. **Independent Counters**: Offset values in one partition have no relation to offset values in another partition - even within the same topic.

3. **Consumer Tracking**: When a consumer reads from a topic, it tracks its position (offset) separately for each partition it consumes from.

4. **Consumer Group Offsets**: Kafka stores consumer group progress as a set of (topic, partition, offset) triplets, not as a single global value.

For example, in a topic with 3 partitions, you might have:
- Partition 0: Messages with offsets 0-1500
- Partition 1: Messages with offsets 0-2200
- Partition 2: Messages with offsets 0-1800

These offset values are completely independent of each other. A consumer might be at offset 1000 in one partition while at offset 500 in another.

This partition-level offset system is a fundamental design aspect of Kafka that enables:
- Parallel processing across partitions
- Independent consumption rates
- Precise message ordering guarantees within (but not across) partitions

When working with consumer groups, Kafka's group coordinator manages which consumer reads from which partition, but each consumer still tracks offsets at the partition level.

### Consumer Offsets in Kafka
Consumer commits in Kafka are indeed tracked per `group_id`, and understanding this is key to making `auto_offset_reset='latest'` work correctly. Here's how the offset tracking and `auto_offset_reset` parameter work together.

1. **Tracking by `group_id`**: 
   - Kafka stores consumer offsets in an internal topic called `__consumer_offsets`
   - These offsets are keyed by the combination of `group_id`, topic name, and partition number
   - Different consumer groups maintain separate offset positions for the same topic-partitions

2. **When `auto_offset_reset` is applied**:
   - `auto_offset_reset` is only used when a consumer group has NO committed offset for a partition OR when an explicit reset is requested
   - It does NOT override existing committed offsets for a consumer group

The key thing to remember is that `auto_offset_reset` is only used when Kafka can't find committed offsets for your consumer group or when you explicitly reset. If there are already committed offsets for your consumer group, Kafka will use those instead of applying the `auto_offset_reset` parameter.

### Consumer Group ID Commits (How they work):
Kafka consumer does not automatically commit offsets when polling for new records. The offset commitment is a separate process from polling, and how it happens depends on your consumer configuration and code implementation.

---
Here's how offset management works in Kafka:

1. **Manual vs. Automatic Commits**: 
   - With `enable.auto.commit=true` (default), the consumer automatically commits offsets periodically (based on `auto.commit.interval.ms`)
   - With `enable.auto.commit=false`, you must explicitly commit offsets in your code

2. **When Re-polling Occurs**:
   - Simply calling `poll()` again does not trigger a commit of previously processed records
   - If auto-commit is enabled, offsets are committed based on time intervals, not polling cycles
   - If auto-commit is disabled, you need to call `consumer.commitSync()` or `consumer.commitAsync()` explicitly

3. **Important Considerations**:
   - Auto-commit happens during `poll()` calls, but based on time passed since the last commit, not because you're polling again
   - Auto-commit commits the last offset returned by `poll()`, which might include records you haven't processed yet (if you're mid-processing when the commit timer fires)

Here's a simple example to illustrate:

```python
# Auto-commit enabled (default)
consumer = KafkaConsumer(
    'my-topic',
    bootstrap_servers=['localhost:9092'],
    group_id='my-group',
    enable_auto_commit=True,
    auto_commit_interval_ms=5000  # Commit every 5 seconds
)

# With auto-commit, records are committed periodically during polling
# regardless of whether you've processed them
for message in consumer:
    process_message(message)
    # No explicit commit needed, but offsets are only committed 
    # every 5 seconds during poll() calls
```

```python
# Manual commit
consumer = KafkaConsumer(
    'my-topic',
    bootstrap_servers=['localhost:9092'],
    group_id='my-group',
    enable_auto_commit=False
)

# With manual commit, you control exactly when offsets are committed
for message in consumer:
    process_message(message)
    # Explicitly commit after processing each message
    consumer.commit()  # or commitSync() or commitAsync()
```

The key takeaway is that re-polling itself does not trigger offset commitment - it's either time-based (auto-commit) or explicit (manual commit).

**Here are the main ways to control and set offsets:**
## 1. Using Seek Methods

The most direct way to start at a specific offset is using the `seek()` and related methods:

```python
from confluent_kafka import Consumer, TopicPartition

consumer = Consumer({
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'my-consumer-group'
})

# Subscribe to the topic
consumer.subscribe(['my-topic'])

# Get the assigned partitions after subscription
# This happens after the consumer rebalances
while True:
    assignments = consumer.assignment()
    if assignments:
        break
    consumer.poll(1.0)  # Poll to trigger partition assignment

# Now seek to a specific offset for each assigned partition
for partition in assignments:
    # Option 1: Seek to specific offset
    consumer.seek(TopicPartition(partition.topic, partition.partition, 1000))
    
    # Option 2: Seek to beginning
    # consumer.seek_to_beginning(partition)
    
    # Option 3: Seek to end
    # consumer.seek_to_end(partition)

# Continue with normal consumption
while True:
    msg = consumer.poll(1.0)
    if msg:
        # Process message
        print(f"Received message at offset: {msg.offset()}")
```

## 2. Using Consumer Configuration

You can configure the starting position using properties:

```python
# For new consumer groups or when no offsets are committed yet
consumer = Consumer({
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'my-consumer-group',
    'auto.offset.reset': 'earliest'  # or 'latest' or 'none'
})
```

- `auto.offset.reset`: Controls where consumption starts when there are no committed offsets:
  - `earliest`: Start from the beginning of the topic
  - `latest`: Start from the end of the topic (only new messages)
  - `none`: Throw an exception if no offset is found

## 3. Using Manual Offset Management

If you need to start from a specific timestamp or track offsets yourself:

```python
from confluent_kafka import Consumer, TopicPartition, OFFSET_BEGINNING
import time

consumer = Consumer({
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'my-consumer-group',
    'enable.auto.commit': False,  # Disable auto-commit for manual control
})

consumer.subscribe(['my-topic'])

# Wait for partition assignment
while True:
    assignments = consumer.assignment()
    if assignments:
        break
    consumer.poll(1.0)

# Option 1: Seek to a specific timestamp
timestamp_ms = int(time.time() * 1000) - (24 * 60 * 60 * 1000)  # 1 day ago
topic_partitions = [TopicPartition(tp.topic, tp.partition, timestamp_ms) for tp in assignments]
offsets_for_times = consumer.offsets_for_times(topic_partitions)

for tp in offsets_for_times:
    if tp.offset > -1:  # -1 means no offset was found for that timestamp
        consumer.seek(tp)

# Option 2: Seek to stored offset in external storage (e.g., database)
# Example: If you stored offsets in a database
for partition in assignments:
    stored_offset = get_offset_from_database(partition.topic, partition.partition)
    if stored_offset:
        consumer.seek(TopicPartition(partition.topic, partition.partition, stored_offset))
    else:
        consumer.seek_to_beginning(partition)  # Default if no stored offset
```

## 4. Using Specific Assignment Instead of Subscribe

If you need more control, you can manually assign partitions instead of subscribing:

```python
from confluent_kafka import Consumer, TopicPartition

consumer = Consumer({
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'my-consumer-group'
})

# Directly assign specific partitions with specific offsets
partitions = [
    TopicPartition('my-topic', 0, 1000),  # Partition 0, offset 1000
    TopicPartition('my-topic', 1, 2000),  # Partition 1, offset 2000
]

consumer.assign(partitions)

# Continue with normal consumption
while True:
    msg = consumer.poll(1.0)
    if msg:
        # Process message
        print(f"Received message at partition {msg.partition()}, offset: {msg.offset()}")
```

## Real-World Use Cases for Specific Offset Consumption

1. **Replay and Recovery**:
   - After a failure, restart processing from the last known good offset
   - Replay historical data for debugging or audit purposes

2. **Time-Based Processing**:
   - Start consuming messages from a specific point in time (using `offsets_for_times()`)
   - Process only messages created after a specific event

3. **Parallel Processing**:
   - Divide a large topic into chunks and process each chunk separately
   - Multiple consumers can process different ranges of the same partition

4. **Exactly-Once Processing**:
   - Track processed offsets in your application's transactional storage
   - Resume consumption from the last committed transaction

5. **Testing and Development**:
   - Start from known offsets to replicate specific scenarios
   - Reset to beginning to test with full dataset

Each approach has its own advantages depending on your specific use case. The manual seek methods give you the most control but require more complex management, while the configuration-based approach is simpler but less precise.
