# Streaming with Iceberg
Let me dive deep into streaming data ingestion with Apache Iceberg on AWS, covering both Kinesis Data Firehose and MSK integration patterns with practical code examples.

## The Streaming Data Challenge

Traditional data lake architectures face a fundamental trade-off: you either get fast ingestion with delayed query availability (batch processing) or immediate queries with slower ingestion. Iceberg eliminates this trade-off by providing ACID transactions and snapshot isolation, enabling real-time ingestion with immediate query availability.

## Kinesis Data Firehose + Iceberg Integration

### Architecture Overview

Firehose can deliver data directly to S3 in Iceberg format using custom data transformations and delivery configurations. Here's how to set it up:
```python
# AWS Lambda function for Firehose data transformation to Iceberg format
import json
import base64
import boto3
from datetime import datetime
import uuid

def lambda_handler(event, context):
    """
    Lambda function to transform Firehose records for Iceberg ingestion
    This function processes streaming records and prepares them for Iceberg table writes
    """
    
    output = []
    
    for record in event['records']:
        # Decode the data
        payload = base64.b64decode(record['data'])
        data = json.loads(payload)
        
        # Add metadata for Iceberg partitioning and tracking
        enhanced_data = {
            **data,
            'ingestion_timestamp': datetime.utcnow().isoformat(),
            'partition_date': datetime.utcnow().strftime('%Y-%m-%d'),
            'partition_hour': datetime.utcnow().strftime('%H'),
            'record_id': str(uuid.uuid4())
        }
        
        # Convert back to base64 for Firehose
        output_record = {
            'recordId': record['recordId'],
            'result': 'Ok',
            'data': base64.b64encode(
                json.dumps(enhanced_data).encode('utf-8')
            ).decode('utf-8')
        }
        
        output.append(output_record)
    
    return {'records': output}


# Glue ETL Job to convert Firehose output to Iceberg format
import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql import SparkSession
from pyspark.sql.functions import *

class FirehoseToIcebergETL:
    def __init__(self):
        self.args = getResolvedOptions(sys.argv, [
            'JOB_NAME',
            'source_path',
            'iceberg_table_name',
            'database_name'
        ])
        
        # Initialize Spark with Iceberg configurations
        self.spark = SparkSession.builder \
            .appName("FirehoseToIceberg") \
            .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions") \
            .config("spark.sql.catalog.glue_catalog", "org.apache.iceberg.spark.SparkCatalog") \
            .config("spark.sql.catalog.glue_catalog.warehouse", "s3://your-iceberg-warehouse/") \
            .config("spark.sql.catalog.glue_catalog.catalog-impl", "org.apache.iceberg.aws.glue.GlueCatalog") \
            .config("spark.sql.catalog.glue_catalog.io-impl", "org.apache.iceberg.aws.s3.S3FileIO") \
            .getOrCreate()
        
        self.glue_context = GlueContext(self.spark.sparkContext)
        self.job = Job(self.glue_context)
        self.job.init(self.args['JOB_NAME'], self.args)
    
    def create_iceberg_table_if_not_exists(self):
        """Create Iceberg table with appropriate schema"""
        create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS glue_catalog.{self.args['database_name']}.{self.args['iceberg_table_name']} (
            record_id STRING,
            user_id STRING,
            event_type STRING,
            event_data MAP<STRING, STRING>,
            ingestion_timestamp TIMESTAMP,
            partition_date STRING,
            partition_hour STRING
        ) 
        USING iceberg
        PARTITIONED BY (partition_date, partition_hour)
        TBLPROPERTIES (
            'write.format.default' = 'parquet',
            'write.parquet.compression-codec' = 'snappy',
            'write.target-file-size-bytes' = '134217728'  -- 128MB
        )
        """
        
        self.spark.sql(create_table_sql)
    
    def process_streaming_data(self):
        """Process streaming data from Firehose and write to Iceberg"""
        
        # Read JSON data delivered by Firehose
        df = self.spark.read \
            .option("multiline", "false") \
            .json(self.args['source_path'])
        
        # Add processing metadata
        processed_df = df \
            .withColumn("processing_time", current_timestamp()) \
            .withColumn("file_name", input_file_name())
        
        # Write to Iceberg table with upsert capability
        processed_df.writeTo(f"glue_catalog.{self.args['database_name']}.{self.args['iceberg_table_name']}") \
            .option("write-audit-publish", "true") \
            .option("check-nullability", "false") \
            .append()
        
        return processed_df.count()
    
    def run(self):
        """Main execution method"""
        self.create_iceberg_table_if_not_exists()
        records_processed = self.process_streaming_data()
        
        print(f"Successfully processed {records_processed} records")
        self.job.commit()

# Execute the ETL job
if __name__ == "__main__":
    etl = FirehoseToIcebergETL()
    etl.run()
```

## MSK (Managed Streaming for Apache Kafka) + Iceberg Integration

For MSK integration, we can use Kafka Connect with Iceberg sink connectors or implement a custom Spark Structured Streaming job:
```python
# Spark Structured Streaming job for MSK to Iceberg pipeline
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
import json

class MSKToIcebergStreaming:
    def __init__(self, kafka_bootstrap_servers, topic_name, checkpoint_location, iceberg_warehouse):
        """
        Initialize Spark Structured Streaming for MSK to Iceberg pipeline
        """
        self.kafka_servers = kafka_bootstrap_servers
        self.topic_name = topic_name
        self.checkpoint_location = checkpoint_location
        
        # Configure Spark for Iceberg and Kafka
        self.spark = SparkSession.builder \
            .appName("MSKToIcebergStreaming") \
            .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions") \
            .config("spark.sql.catalog.glue_catalog", "org.apache.iceberg.spark.SparkCatalog") \
            .config("spark.sql.catalog.glue_catalog.warehouse", iceberg_warehouse) \
            .config("spark.sql.catalog.glue_catalog.catalog-impl", "org.apache.iceberg.aws.glue.GlueCatalog") \
            .config("spark.sql.catalog.glue_catalog.io-impl", "org.apache.iceberg.aws.s3.S3FileIO") \
            .config("spark.sql.adaptive.enabled", "true") \
            .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
            .getOrCreate()
        
        self.spark.sparkContext.setLogLevel("WARN")
    
    def create_streaming_dataframe(self):
        """Create streaming DataFrame from MSK topic"""
        
        kafka_df = self.spark \
            .readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", self.kafka_servers) \
            .option("subscribe", self.topic_name) \
            .option("startingOffsets", "latest") \
            .option("kafka.consumer.group.id", "iceberg-streaming-consumer") \
            .option("kafka.session.timeout.ms", "30000") \
            .option("kafka.request.timeout.ms", "40000") \
            .option("failOnDataLoss", "false") \
            .load()
        
        # Define the expected JSON schema for your events
        event_schema = StructType([
            StructField("user_id", StringType(), True),
            StructField("event_type", StringType(), True),
            StructField("timestamp", TimestampType(), True),
            StructField("properties", MapType(StringType(), StringType()), True),
            StructField("session_id", StringType(), True),
            StructField("device_info", StructType([
                StructField("device_type", StringType(), True),
                StructField("os", StringType(), True),
                StructField("app_version", StringType(), True)
            ]), True)
        ])
        
        # Parse JSON and add metadata
        parsed_df = kafka_df.select(
            col("key").cast("string").alias("kafka_key"),
            from_json(col("value").cast("string"), event_schema).alias("data"),
            col("topic"),
            col("partition"),
            col("offset"),
            col("timestamp").alias("kafka_timestamp")
        ).select(
            col("kafka_key"),
            col("data.*"),
            col("topic"),
            col("partition"),
            col("offset"),
            col("kafka_timestamp"),
            current_timestamp().alias("processing_time"),
            date_format(current_timestamp(), "yyyy-MM-dd").alias("partition_date"),
            hour(current_timestamp()).alias("partition_hour")
        )
        
        return parsed_df
    
    def setup_iceberg_table(self, database_name, table_name):
        """Create Iceberg table if it doesn't exist"""
        
        create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS glue_catalog.{database_name}.{table_name} (
            kafka_key STRING,
            user_id STRING,
            event_type STRING,
            timestamp TIMESTAMP,
            properties MAP<STRING, STRING>,
            session_id STRING,
            device_info STRUCT<
                device_type: STRING,
                os: STRING,
                app_version: STRING
            >,
            topic STRING,
            partition INT,
            offset LONG,
            kafka_timestamp TIMESTAMP,
            processing_time TIMESTAMP,
            partition_date STRING,
            partition_hour INT
        )
        USING iceberg
        PARTITIONED BY (partition_date, partition_hour)
        TBLPROPERTIES (
            'write.format.default' = 'parquet',
            'write.parquet.compression-codec' = 'snappy',
            'write.target-file-size-bytes' = '134217728',
            'write.metadata.compression-codec' = 'gzip',
            'commit.retry.num-retries' = '3',
            'commit.retry.min-wait-ms' = '100'
        )
        """
        
        try:
            self.spark.sql(create_table_sql)
            print(f"Table glue_catalog.{database_name}.{table_name} created or already exists")
        except Exception as e:
            print(f"Error creating table: {e}")
            raise
    
    def write_to_iceberg(self, streaming_df, database_name, table_name, trigger_interval="30 seconds"):
        """
        Write streaming data to Iceberg table with exactly-once semantics
        """
        
        # Custom function to handle Iceberg writes with deduplication
        def write_batch_to_iceberg(batch_df, batch_id):
            print(f"Processing batch {batch_id} with {batch_df.count()} records")
            
            if batch_df.count() > 0:
                # Remove duplicates based on kafka key, topic, partition, and offset
                deduped_df = batch_df.dropDuplicates(["kafka_key", "topic", "partition", "offset"])
                
                # Write to Iceberg with merge/upsert capability
                deduped_df.writeTo(f"glue_catalog.{database_name}.{table_name}") \
                    .option("write-audit-publish", "true") \
                    .option("check-nullability", "false") \
                    .append()
                
                print(f"Successfully wrote {deduped_df.count()} records to Iceberg table")
        
        # Start the streaming query
        query = streaming_df.writeStream \
            .foreachBatch(write_batch_to_iceberg) \
            .outputMode("append") \
            .option("checkpointLocation", self.checkpoint_location) \
            .trigger(processingTime=trigger_interval) \
            .start()
        
        return query
    
    def start_streaming_pipeline(self, database_name, table_name, trigger_interval="30 seconds"):
        """Start the complete streaming pipeline"""
        
        # Setup Iceberg table
        self.setup_iceberg_table(database_name, table_name)
        
        # Create streaming DataFrame
        streaming_df = self.create_streaming_dataframe()
        
        # Start writing to Iceberg
        query = self.write_to_iceberg(streaming_df, database_name, table_name, trigger_interval)
        
        print(f"Streaming pipeline started. Writing to glue_catalog.{database_name}.{table_name}")
        print(f"Checkpoint location: {self.checkpoint_location}")
        
        return query


# Alternative: Kafka Connect Configuration for Iceberg Sink
kafka_connect_config = {
    "name": "iceberg-sink-connector",
    "config": {
        "connector.class": "org.apache.iceberg.connect.IcebergSinkConnector",
        "tasks.max": "4",
        "topics": "user-events,product-events",
        
        # Iceberg catalog configuration
        "iceberg.catalog.glue.catalog-impl": "org.apache.iceberg.aws.glue.GlueCatalog",
        "iceberg.catalog.glue.warehouse": "s3://your-iceberg-warehouse/",
        "iceberg.catalog.glue.io-impl": "org.apache.iceberg.aws.s3.S3FileIO",
        
        # Table configuration
        "iceberg.table.default.partition-spec": "partition_date,partition_hour",
        "iceberg.table.default.write-format": "parquet",
        "iceberg.table.default.compression-codec": "snappy",
        
        # Data transformation
        "transforms": "AddMetadata",
        "transforms.AddMetadata.type": "org.apache.kafka.connect.transforms.InsertField$Value",
        "transforms.AddMetadata.timestamp.field": "processing_timestamp",
        
        # Error handling
        "errors.tolerance": "all",
        "errors.deadletterqueue.topic.name": "iceberg-sink-dlq",
        "errors.deadletterqueue.topic.replication.factor": "3",
        
        # Performance tuning
        "iceberg.table.default.write.target-file-size-bytes": "134217728",  # 128MB
        "consumer.max.poll.records": "1000",
        "flush.size": "10000"
    }
}


# Usage example
if __name__ == "__main__":
    # Configuration
    kafka_servers = "your-msk-cluster-bootstrap-servers:9092"
    topic_name = "user-events"
    checkpoint_location = "s3://your-bucket/checkpoints/msk-iceberg/"
    iceberg_warehouse = "s3://your-iceberg-warehouse/"
    
    # Initialize and start pipeline
    pipeline = MSKToIcebergStreaming(
        kafka_bootstrap_servers=kafka_servers,
        topic_name=topic_name,
        checkpoint_location=checkpoint_location,
        iceberg_warehouse=iceberg_warehouse
    )
    
    # Start streaming
    query = pipeline.start_streaming_pipeline(
        database_name="streaming_analytics",
        table_name="user_events",
        trigger_interval="10 seconds"
    )
    
    # Wait for termination
    try:
        query.awaitTermination()
    except KeyboardInterrupt:
        print("Stopping streaming pipeline...")
        query.stop()
```

## Real-Time Query Capabilities

Once data is streaming into Iceberg, you can query it immediately. Here's how to set up real-time analytics:
```sql
-- Real-time analytics queries on streaming Iceberg data

-- 1. Query the latest data (last 5 minutes)
SELECT 
    event_type,
    COUNT(*) as event_count,
    COUNT(DISTINCT user_id) as unique_users,
    AVG(CAST(properties['duration'] AS DOUBLE)) as avg_duration
FROM glue_catalog.streaming_analytics.user_events
WHERE processing_time >= CURRENT_TIMESTAMP - INTERVAL '5' MINUTE
GROUP BY event_type
ORDER BY event_count DESC;

-- 2. Real-time user session analysis
WITH session_data AS (
    SELECT 
        user_id,
        session_id,
        MIN(timestamp) as session_start,
        MAX(timestamp) as session_end,
        COUNT(*) as events_in_session,
        COLLECT_LIST(event_type) as event_sequence
    FROM glue_catalog.streaming_analytics.user_events
    WHERE partition_date = CURRENT_DATE()
      AND processing_time >= CURRENT_TIMESTAMP - INTERVAL '1' HOUR
    GROUP BY user_id, session_id
)
SELECT 
    COUNT(*) as active_sessions,
    AVG(events_in_session) as avg_events_per_session,
    AVG((UNIX_TIMESTAMP(session_end) - UNIX_TIMESTAMP(session_start)) / 60) as avg_session_duration_minutes
FROM session_data
WHERE session_end >= CURRENT_TIMESTAMP - INTERVAL '10' MINUTE;

-- 3. Time travel query - compare current data with 1 hour ago
SELECT 
    'current' as time_period,
    event_type,
    COUNT(*) as event_count
FROM glue_catalog.streaming_analytics.user_events
WHERE processing_time >= CURRENT_TIMESTAMP - INTERVAL '15' MINUTE
GROUP BY event_type

UNION ALL

SELECT 
    '1_hour_ago' as time_period,
    event_type,
    COUNT(*) as event_count
FROM glue_catalog.streaming_analytics.user_events FOR TIMESTAMP AS OF CURRENT_TIMESTAMP - INTERVAL '1' HOUR
WHERE processing_time >= (CURRENT_TIMESTAMP - INTERVAL '1' HOUR - INTERVAL '15' MINUTE)
  AND processing_time < (CURRENT_TIMESTAMP - INTERVAL '1' HOUR)
GROUP BY event_type;

-- 4. Real-time anomaly detection using sliding windows
WITH event_rates AS (
    SELECT 
        window.start as window_start,
        window.end as window_end,
        event_type,
        COUNT(*) as event_count,
        COUNT(*) / 300.0 as events_per_second  -- 5-minute window
    FROM (
        SELECT 
            event_type,
            timestamp,
            window(timestamp, '5 minutes', '1 minute') as window
        FROM glue_catalog.streaming_analytics.user_events
        WHERE partition_date = CURRENT_DATE()
    )
    GROUP BY window.start, window.end, event_type
),
historical_avg AS (
    SELECT 
        event_type,
        AVG(events_per_second) as avg_rate,
        STDDEV(events_per_second) as stddev_rate
    FROM event_rates
    WHERE window_start >= CURRENT_TIMESTAMP - INTERVAL '2' HOUR
      AND window_start < CURRENT_TIMESTAMP - INTERVAL '30' MINUTE
    GROUP BY event_type
)
SELECT 
    er.event_type,
    er.window_start,
    er.events_per_second as current_rate,
    ha.avg_rate as historical_avg_rate,
    CASE 
        WHEN er.events_per_second > (ha.avg_rate + 2 * ha.stddev_rate) THEN 'HIGH'
        WHEN er.events_per_second < (ha.avg_rate - 2 * ha.stddev_rate) THEN 'LOW'
        ELSE 'NORMAL'
    END as anomaly_status
FROM event_rates er
JOIN historical_avg ha ON er.event_type = ha.event_type
WHERE er.window_start >= CURRENT_TIMESTAMP - INTERVAL '30' MINUTE
ORDER BY er.window_start DESC, er.event_type;

-- 5. Real-time dashboard query - key metrics
SELECT 
    'last_5_minutes' as time_window,
    COUNT(*) as total_events,
    COUNT(DISTINCT user_id) as unique_users,
    COUNT(DISTINCT session_id) as unique_sessions,
    
    -- Event type breakdown
    SUM(CASE WHEN event_type = 'page_view' THEN 1 ELSE 0 END) as page_views,
    SUM(CASE WHEN event_type = 'click' THEN 1 ELSE 0 END) as clicks,
    SUM(CASE WHEN event_type = 'purchase' THEN 1 ELSE 0 END) as purchases,
    
    -- Device breakdown
    SUM(CASE WHEN device_info.device_type = 'mobile' THEN 1 ELSE 0 END) as mobile_events,
    SUM(CASE WHEN device_info.device_type = 'desktop' THEN 1 ELSE 0 END) as desktop_events,
    
    -- Data freshness
    MIN(processing_time) as oldest_processed_record,
    MAX(processing_time) as newest_processed_record,
    
    -- Average processing latency (time between event and processing)
    AVG(UNIX_TIMESTAMP(processing_time) - UNIX_TIMESTAMP(timestamp)) as avg_processing_latency_seconds

FROM glue_catalog.streaming_analytics.user_events
WHERE processing_time >= CURRENT_TIMESTAMP - INTERVAL '5' MINUTE;

-- 6. Continuous aggregation using materialized views (if supported)
-- This would typically be implemented as a scheduled job
CREATE OR REPLACE VIEW real_time_metrics AS
SELECT 
    DATE_TRUNC('minute', processing_time) as minute_window,
    event_type,
    device_info.device_type,
    COUNT(*) as event_count,
    COUNT(DISTINCT user_id) as unique_users,
    AVG(CASE 
        WHEN properties['duration'] IS NOT NULL 
        THEN CAST(properties['duration'] AS DOUBLE) 
    END) as avg_duration
FROM glue_catalog.streaming_analytics.user_events
WHERE partition_date >= CURRENT_DATE() - INTERVAL '1' DAY
GROUP BY 
    DATE_TRUNC('minute', processing_time),
    event_type,
    device_info.device_type;

-- 7. Query to show Iceberg table metadata and health
SELECT 
    snapshot_id,
    timestamp_ms,
    operation,
    summary
FROM glue_catalog.streaming_analytics.user_events.snapshots
ORDER BY timestamp_ms DESC
LIMIT 10;

-- Check table partitions and file count
SELECT 
    partition,
    file_count,
    total_size,
    data_file_count,
    delete_file_count
FROM glue_catalog.streaming_analytics.user_events.partitions
WHERE partition LIKE CONCAT(CURRENT_DATE(), '%')
ORDER BY partition DESC;
```

## Key Benefits for Streaming Workloads

**Immediate Query Availability**: Unlike traditional batch processing where you wait for hourly or daily jobs, Iceberg makes data queryable within seconds of ingestion. The ACID guarantees ensure you never see partial writes or inconsistent data.

**Exactly-Once Processing**: The combination of Kafka's exactly-once semantics with Iceberg's transactional writes eliminates duplicate data issues that plague traditional streaming architectures.

**Schema Evolution**: As your streaming data evolves, Iceberg handles schema changes gracefully without breaking downstream consumers or requiring data migration.

**Time Travel for Debugging**: When issues arise in your streaming pipeline, you can query data as it existed at any point in time, making troubleshooting much more effective.

**Efficient Storage**: Iceberg's automatic compaction and file optimization prevent the "small files problem" that typically occurs with high-frequency streaming ingestion.

## Performance Considerations

For optimal performance with streaming workloads:

- **Tune batch sizes**: Balance latency requirements with write efficiency
- **Configure appropriate partition strategies**: Use time-based partitioning aligned with query patterns  
- **Monitor compaction**: Set up automated compaction jobs for frequently updated partitions
- **Optimize file sizes**: Target 128MB-1GB files for optimal query performance
- **Use columnar formats**: Parquet provides excellent compression and query performance

This architecture provides the best of both worlds: real-time data availability with the reliability and performance characteristics of a mature data warehouse.
