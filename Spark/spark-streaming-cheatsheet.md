# PySpark Streaming Data Cheatsheet

## Reading Stream Data

### Stream Sources

```python
# Create a streaming DataFrame from a source
stream_df = spark.readStream \
    .format("source_format") \
    .option("key", "value") \
    .load()
```

### Common Source Formats

| Format | Description | Key Options |
|--------|-------------|-------------|
| `kafka` | Read from Kafka topics | `kafka.bootstrap.servers`, `subscribe`, `startingOffsets` |
| `socket` | Read from socket connection | `host`, `port` |
| `rate` | Generate data at specified rate | `rowsPerSecond`, `numPartitions` |
| `file` | Read from files in directory | `path`, `maxFilesPerTrigger` |
| `delta` | Read from Delta Lake tables | `path` |
| `json` | Read JSON files | `path`, `schema` |
| `csv` | Read CSV files | `path`, `header`, `schema` |
| `parquet` | Read Parquet files | `path` |
| `orc` | Read ORC files | `path` |

### Kafka Specific Options

```python
# Reading from Kafka
kafka_stream = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "host1:port1,host2:port2") \
    .option("subscribe", "topic1,topic2") \
    .option("startingOffsets", "earliest") \
    .option("failOnDataLoss", "false") \
    .load()

# Alternative: subscribe to pattern
# .option("subscribePattern", "topic.*")

# Access fields in Kafka stream
processed_df = kafka_stream.selectExpr(
    "CAST(key AS STRING)",
    "CAST(value AS STRING)",
    "topic",
    "partition",
    "offset",
    "timestamp"
)
```

### File Source Options

```python
# Reading from files
file_stream = spark.readStream \
    .format("json") \
    .option("path", "data/input") \
    .option("maxFilesPerTrigger", 10) \
    .schema(schema) \
    .load()
```

### Socket Source

```python
# Read from socket
socket_stream = spark.readStream \
    .format("socket") \
    .option("host", "localhost") \
    .option("port", 9999) \
    .load()
```

### Rate Source (for testing)

```python
# Generate data for testing
rate_stream = spark.readStream \
    .format("rate") \
    .option("rowsPerSecond", 100) \
    .option("numPartitions", 4) \
    .load()
```

### Defining Schema

```python
# Define schema for streaming data
from pyspark.sql.types import *

schema = StructType([
    StructField("id", StringType()),
    StructField("timestamp", TimestampType()),
    StructField("value", DoubleType()),
    StructField("properties", MapType(StringType(), StringType()))
])
```

## Processing Stream Data

### Common Operations

```python
from pyspark.sql.functions import *
from pyspark.sql.window import Window

# Filter operations
filtered_df = stream_df.filter(col("value") > 100)

# Projection
projected_df = stream_df.select("id", "value")

# Aggregations
aggregated_df = stream_df \
    .groupBy(col("id"), window(col("timestamp"), "10 minutes", "5 minutes")) \
    .agg(avg("value").alias("avg_value"))

# Watermarking (for late data handling)
with_watermark = stream_df \
    .withWatermark("timestamp", "10 minutes") \
    .groupBy(window(col("timestamp"), "10 minutes"), col("id")) \
    .count()

# Join with static data
static_df = spark.read.parquet("reference/data")
joined_df = stream_df.join(static_df, "id")

# Join with another stream
joined_streams = stream1 \
    .withWatermark("timestamp1", "1 hour") \
    .join(
        stream2.withWatermark("timestamp2", "1 hour"),
        expr("id = otherId AND timestamp1 >= timestamp2 - interval 30 minutes AND timestamp1 <= timestamp2 + interval 30 minutes"),
        "inner"
    )
```

### Handling Complex Data

```python
# Parse JSON in strings
parsed_df = stream_df \
    .select(col("id"), from_json(col("value"), schema).alias("data")) \
    .select("id", "data.*")

# Convert to JSON strings
json_df = stream_df.select(to_json(struct(col("*"))).alias("value"))
```

## Writing Stream Data

### Stream Sinks

```python
query = processed_df.writeStream \
    .format("sink_format") \
    .outputMode("append") \
    .option("key", "value") \
    .trigger(processingTime="10 seconds") \
    .start()
```

### Output Modes

| Mode | Description | Supported Aggregations |
|------|-------------|------------------------|
| `append` | Only new rows are written | Supported with watermark for aggregations |
| `complete` | All result rows are written | Supported for all aggregations |
| `update` | Only rows that were updated are written | Supported for all aggregations |

### Common Sink Formats

| Format | Description | Key Options |
|--------|-------------|-------------|
| `console` | Print output to console | `numRows`, `truncate` |
| `kafka` | Write to Kafka topics | `kafka.bootstrap.servers`, `topic` |
| `file` | Write to files in directory | `path`, `checkpointLocation` |
| `delta` | Write to Delta Lake tables | `path`, `checkpointLocation` |
| `memory` | Store in in-memory table | `queryName` |
| `foreach` | Custom processing logic | - |
| `foreachBatch` | Custom batch processing | - |

### Console Sink (for debugging)

```python
query = stream_df.writeStream \
    .format("console") \
    .option("truncate", False) \
    .option("numRows", 50) \
    .start()
```

### Kafka Sink

```python
query = processed_df \
    .selectExpr("CAST(id AS STRING) AS key", "to_json(struct(*)) AS value") \
    .writeStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "host1:port1,host2:port2") \
    .option("topic", "output-topic") \
    .option("checkpointLocation", "checkpoint/dir") \
    .start()
```

### File Sink

```python
query = aggregated_df.writeStream \
    .format("parquet") \
    .option("path", "output/dir") \
    .option("checkpointLocation", "checkpoint/dir") \
    .partitionBy("year", "month", "day") \
    .start()
```

### ForeachBatch Sink (custom processing)

```python
def process_batch(batch_df, batch_id):
    """Custom processing logic for each batch"""
    # Persist the DataFrame for multiple operations
    batch_df.persist()
    
    # Write to multiple sinks
    batch_df.filter("type = 'A'").write.format("parquet").save("output/typeA")
    batch_df.filter("type = 'B'").write \
        .format("jdbc") \
        .option("url", jdbc_url) \
        .option("dbtable", "table_B") \
        .option("user", "username") \
        .option("password", "password") \
        .save()
    
    # Update metrics
    update_metrics(batch_df.count())
    
    # Unpersist the DataFrame
    batch_df.unpersist()

query = stream_df.writeStream \
    .foreachBatch(process_batch) \
    .option("checkpointLocation", "checkpoint/dir") \
    .start()
```

### Foreach Sink (row-by-row processing)

```python
class CustomForeachWriter:
    def open(self, partition_id, epoch_id):
        """Open connection for partition"""
        # Initialize connections, prepare resources
        return True
    
    def process(self, row):
        """Process each row"""
        # Custom processing logic for each row
        pass
    
    def close(self, error):
        """Close connection"""
        # Clean up resources
        pass

query = stream_df.writeStream \
    .foreach(CustomForeachWriter()) \
    .option("checkpointLocation", "checkpoint/dir") \
    .start()
```

## Stream Query Management

### Query Control

```python
# Start the query
query = stream_df.writeStream.format("...").start()

# Stop the query
query.stop()

# Await termination
query.awaitTermination()
query.awaitTermination(timeout_ms)

# Exception handling
query.exception()  # returns the exception if query has failed

# Query status
query.status
query.lastProgress
query.recentProgress
```

### Checkpoint Configuration

```python
# Set checkpoint location (required for most sinks)
query = stream_df.writeStream \
    .option("checkpointLocation", "hdfs://path/to/checkpoint/dir") \
    .start()
```

### Trigger Types

```python
# Process data as it arrives
.trigger(processingTime="0 seconds")

# Process in micro-batches
.trigger(processingTime="10 seconds")

# Process once and exit
.trigger(once=True)

# Process continuously with low latency (experimental)
.trigger(continuous="1 second")
```

## Performance Tuning

### Configuration Options

```python
# Set max offset fetch per trigger
.option("maxOffsetsPerTrigger", 10000)

# Configure number of partitions for shuffle
spark.conf.set("spark.sql.shuffle.partitions", "200")

# Adjust state store memory
spark.conf.set("spark.sql.streaming.stateStore.minDeltasForSnapshot", "10")
spark.conf.set("spark.sql.streaming.statefulOperator.useCompactedStateAndPeriodicFlush", "true")
```

### Kafka Performance Options

```python
# Tune Kafka consumer settings
.option("kafka.fetch.max.bytes", "52428800") \
.option("kafka.max.partition.fetch.bytes", "1048576") \
.option("fetchOffset.numRetries", "3") \
.option("fetchOffset.retryIntervalMs", "1000")
```

## Error Handling

### Recovery and Restart Options

```python
# Configure restart on failure
.option("failOnDataLoss", "false")

# Using queryName for recovery
.queryName("my_stream_query")

# Handling errors in foreachBatch
def safe_process_batch(batch_df, batch_id):
    try:
        # Process batch
        process_batch(batch_df, batch_id)
    except Exception as e:
        # Log error
        print(f"Error processing batch {batch_id}: {str(e)}")
        # Optionally take recovery action

query = stream_df.writeStream \
    .foreachBatch(safe_process_batch) \
    .option("checkpointLocation", "checkpoint/dir") \
    .start()
```

## Monitoring

### Metrics and Logging

```python
# Enable Dropwizard metrics
spark.conf.set("spark.sql.streaming.metricsEnabled", "true")

# Access recent progress information
print(query.lastProgress)
for progress in query.recentProgress:
    print(progress)

# Custom streaming query listener
from pyspark.sql.streaming import StreamingQueryListener

class CustomStreamingQueryListener(StreamingQueryListener):
    def onQueryStarted(self, event):
        print(f"Query started: {event.id}")
    
    def onQueryProgress(self, event):
        print(f"Query made progress: {event.progress}")
    
    def onQueryTerminated(self, event):
        print(f"Query terminated: {event.id}")

# Add listener
spark.streams.addListener(CustomStreamingQueryListener())
```

## Additional Tips

- Always specify a schema for file-based sources to avoid schema inference costs
- Use watermarking when performing aggregations or joins to manage state size
- For Kafka sources, always set appropriate starting offsets
- Use the console sink during development to debug stream processing
- Set appropriate checkpoint locations for recovery
- Monitor memory usage and state size for long-running queries
- Use foreachBatch for complex sink logic or writing to multiple destinations
- Import necessary functions from `pyspark.sql.functions` for transformations
- Use `col()` function for column references in PySpark
- Python string formatting and exception handling differ from Scala - use Python conventions
