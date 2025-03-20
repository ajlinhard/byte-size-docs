# Apache Spark Streaming Data Cheatsheet

## Reading Stream Data

### Stream Sources

```scala
// Create a streaming DataFrame from a source
val streamDF = spark.readStream
  .format("source_format")  // kafka, socket, rate, etc.
  .option("key", "value")   // source-specific options
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

```scala
// Reading from Kafka
val kafkaStream = spark.readStream
  .format("kafka")
  .option("kafka.bootstrap.servers", "host1:port1,host2:port2")
  .option("subscribe", "topic1,topic2")  // OR .option("subscribePattern", "topic.*")
  .option("startingOffsets", "earliest")  // "latest" or JSON string with offsets
  .option("failOnDataLoss", "false")
  .load()

// Access fields in Kafka stream
val processedDF = kafkaStream.selectExpr(
  "CAST(key AS STRING)",
  "CAST(value AS STRING)",
  "topic",
  "partition",
  "offset",
  "timestamp"
)
```

### File Source Options

```scala
// Reading from files
val fileStream = spark.readStream
  .format("json")  // or csv, parquet, etc.
  .option("path", "data/input")
  .option("maxFilesPerTrigger", 10)  // limit files per batch
  .schema(schema)  // must specify schema for file sources
  .load()
```

### Socket Source

```scala
// Read from socket
val socketStream = spark.readStream
  .format("socket")
  .option("host", "localhost")
  .option("port", 9999)
  .load()
```

### Rate Source (for testing)

```scala
// Generate data for testing
val rateStream = spark.readStream
  .format("rate")
  .option("rowsPerSecond", 100)
  .option("numPartitions", 4)
  .load()
```

### Defining Schema

```scala
// Define schema for streaming data
import org.apache.spark.sql.types._

val schema = StructType(Array(
  StructField("id", StringType),
  StructField("timestamp", TimestampType),
  StructField("value", DoubleType),
  StructField("properties", MapType(StringType, StringType))
))
```

## Processing Stream Data

### Common Operations

```scala
// Filter operations
val filteredDF = streamDF.filter($"value" > 100)

// Projection
val projectedDF = streamDF.select("id", "value")

// Aggregations
val aggregatedDF = streamDF
  .groupBy($"id", window($"timestamp", "10 minutes", "5 minutes"))
  .agg(avg("value").as("avg_value"))

// Watermarking (for late data handling)
val withWatermark = streamDF
  .withWatermark("timestamp", "10 minutes")
  .groupBy(window($"timestamp", "10 minutes"), $"id")
  .count()

// Join with static data
val staticDF = spark.read.parquet("reference/data")
val joinedDF = streamDF.join(staticDF, "id")

// Join with another stream
val joinedStreams = stream1
  .withWatermark("timestamp1", "1 hour")
  .join(
    stream2.withWatermark("timestamp2", "1 hour"),
    expr("id = otherId AND timestamp1 >= timestamp2 - interval 30 minutes AND timestamp1 <= timestamp2 + interval 30 minutes"),
    "inner"
  )
```

### Handling Complex Data

```scala
// Parse JSON in strings
val parsedDF = streamDF
  .select($"id", from_json($"value", schema).as("data"))
  .select("id", "data.*")

// Convert to JSON strings
val jsonDF = streamDF.select(to_json(struct($"*")).as("value"))
```

## Writing Stream Data

### Stream Sinks

```scala
val query = processedDF.writeStream
  .format("sink_format")     // console, kafka, file, etc.
  .outputMode("append")      // append, update, complete
  .option("key", "value")    // sink-specific options
  .trigger(Trigger.ProcessingTime("10 seconds"))  // batch interval
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

```scala
val query = streamDF.writeStream
  .format("console")
  .option("truncate", false)
  .option("numRows", 50)
  .start()
```

### Kafka Sink

```scala
val query = processedDF
  .selectExpr("CAST(id AS STRING) AS key", "to_json(struct(*)) AS value")
  .writeStream
  .format("kafka")
  .option("kafka.bootstrap.servers", "host1:port1,host2:port2")
  .option("topic", "output-topic")
  .option("checkpointLocation", "checkpoint/dir")
  .start()
```

### File Sink

```scala
val query = aggregatedDF.writeStream
  .format("parquet")  // or json, csv, orc
  .option("path", "output/dir")
  .option("checkpointLocation", "checkpoint/dir")
  .partitionBy("year", "month", "day")
  .start()
```

### ForeachBatch Sink (custom processing)

```scala
val query = streamDF.writeStream
  .foreachBatch { (batchDF: DataFrame, batchId: Long) =>
    // Custom processing logic
    batchDF.persist()
    
    // Write to multiple sinks
    batchDF.filter("type = 'A'").write.format("parquet").save("output/typeA")
    batchDF.filter("type = 'B'").write.jdbc(jdbcUrl, "table_B", jdbcProperties)
    
    // Update metrics
    updateMetrics(batchDF.count())
    
    batchDF.unpersist()
  }
  .option("checkpointLocation", "checkpoint/dir")
  .start()
```

### Foreach Sink (row-by-row processing)

```scala
import org.apache.spark.sql.ForeachWriter

val query = streamDF.writeStream
  .foreach(new ForeachWriter[Row] {
    override def open(partitionId: Long, epochId: Long): Boolean = {
      // Open connection
      true
    }
    
    override def process(value: Row): Unit = {
      // Process each row
    }
    
    override def close(errorOrNull: Throwable): Unit = {
      // Close connection
    }
  })
  .option("checkpointLocation", "checkpoint/dir")
  .start()
```

## Stream Query Management

### Query Control

```scala
// Start the query
val query = streamDF.writeStream.format("...").start()

// Stop the query
query.stop()

// Await termination
query.awaitTermination()
query.awaitTermination(timeoutMs)

// Exception handling
query.exception  // returns the exception if query has failed

// Query status
query.status
query.lastProgress
query.recentProgress
```

### Checkpoint Configuration

```scala
// Set checkpoint location (required for most sinks)
val query = streamDF.writeStream
  .option("checkpointLocation", "hdfs://path/to/checkpoint/dir")
  .start()
```

### Trigger Types

```scala
import org.apache.spark.sql.streaming.Trigger

// Process data as it arrives
.trigger(Trigger.ProcessingTime("0 seconds"))

// Process in micro-batches
.trigger(Trigger.ProcessingTime("10 seconds"))

// Process once and exit
.trigger(Trigger.Once())

// Process continuously with low latency
.trigger(Trigger.Continuous("1 second"))  // experimental
```

## Performance Tuning

### Configuration Options

```scala
// Set max offset fetch per trigger
.option("maxOffsetsPerTrigger", 10000)

// Configure number of partitions for shuffle
spark.conf.set("spark.sql.shuffle.partitions", 200)

// Adjust state store memory
spark.conf.set("spark.sql.streaming.stateStore.minDeltasForSnapshot", 10)
spark.conf.set("spark.sql.streaming.statefulOperator.useCompactedStateAndPeriodicFlush", true)
```

### Kafka Performance Options

```scala
// Tune Kafka consumer settings
.option("kafka.fetch.max.bytes", "52428800")
.option("kafka.max.partition.fetch.bytes", "1048576")
.option("fetchOffset.numRetries", 3)
.option("fetchOffset.retryIntervalMs", 1000)
```

## Error Handling

### Recovery and Restart Options

```scala
// Configure restart on failure
.option("failOnDataLoss", false)

// Using queryName for recovery
.queryName("my_stream_query")

// Handling errors in foreachBatch
.foreachBatch { (batchDF, batchId) =>
  try {
    // Process batch
  } catch {
    case e: Exception =>
      // Log error
      log.error(s"Error processing batch $batchId", e)
      // Optionally take recovery action
  }
}
```

## Monitoring

### Metrics and Logging

```scala
// Enable Dropwizard metrics
spark.conf.set("spark.sql.streaming.metricsEnabled", "true")

// Access recent progress information
query.lastProgress
query.recentProgress.foreach(println)

// Register listener
spark.streams.addListener(new StreamingQueryListener() {
  override def onQueryStarted(event: QueryStartedEvent): Unit = {
    println(s"Query started: ${event.id}")
  }
  override def onQueryProgress(event: QueryProgressEvent): Unit = {
    println(s"Query made progress: ${event.progress}")
  }
  override def onQueryTerminated(event: QueryTerminatedEvent): Unit = {
    println(s"Query terminated: ${event.id}")
  }
})
```

## Additional Tips

- Always specify a schema for file-based sources to avoid schema inference costs
- Use watermarking when performing aggregations or joins to manage state size
- For Kafka sources, always set appropriate starting offsets
- Use the console sink during development to debug stream processing
- Set appropriate checkpoint locations for recovery
- Monitor memory usage and state size for long-running queries
- Use foreachBatch for complex sink logic or writing to multiple destinations
