I'll provide you with comprehensive PySpark code examples for reading from Kafka, both static and streaming, along with methods to store data in different databases.

This comprehensive PySpark code provides everything you need for Kafka integration with offset tracking and multiple database storage options. Here are the key features:

## **Static vs Streaming Reads**

**Static Read**: Reads all available messages at a point in time and stops. Good for batch processing historical data.

**Streaming Read**: Continuously processes new messages as they arrive. Includes automatic offset management through checkpointing.

## **Offset Tracking Methods**

1. **Built-in Checkpointing**: Uses Spark's native checkpoint mechanism to automatically track offsets
2. **Custom Offset Storage**: Save offsets to external databases for more control
3. **Manual Offset Management**: Resume from specific partition offsets

## **Storage Options**

- **MSSQL**: Uses JDBC connector with batch and streaming modes
- **Spark Tables/Parquet**: Native Spark storage with high performance
- **Cassandra**: NoSQL storage with automatic partitioning
- **MongoDB**: Document storage with flexible schema

## **Key Configuration Points**

Make sure to update these configurations for your environment:
- Kafka bootstrap servers and topic names
- Database connection strings and credentials
- Checkpoint and output paths
- Schema definitions to match your data

## **Production Considerations**

- Use appropriate trigger intervals based on your throughput requirements
- Monitor query progress and handle failures gracefully
- Set up proper error handling and alerting
- Consider resource allocation (memory, cores) based on data volume
- Use schema registry for production Kafka environments

The code includes monitoring utilities and cleanup functions to help manage your streaming applications effectively. Each storage method can be used independently or in combination for multi-sink architectures.

----
# Example Code
```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
import json

# Initialize Spark Session with required packages
spark = SparkSession.builder \
    .appName("KafkaSparkIntegration") \
    .config("spark.jars.packages", 
            "org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.0,"
            "com.microsoft.sqlserver:mssql-jdbc:11.2.3.jre8,"
            "com.datastax.spark:spark-cassandra-connector_2.12:3.4.0,"
            "org.mongodb.spark:mongo-spark-connector_2.12:10.1.1") \
    .config("spark.cassandra.connection.host", "localhost") \
    .config("spark.cassandra.connection.port", "9042") \
    .config("spark.mongodb.read.connection.uri", "mongodb://localhost:27017/") \
    .config("spark.mongodb.write.connection.uri", "mongodb://localhost:27017/") \
    .getOrCreate()

# Kafka configuration
kafka_config = {
    "kafka.bootstrap.servers": "localhost:9092",
    "subscribe": "your_topic_name",
    "startingOffsets": "earliest",  # or "latest"
    "failOnDataLoss": "false"
}

# =============================================================================
# 1. STATIC READ FROM KAFKA
# =============================================================================

def static_kafka_read():
    """
    Static read from Kafka - reads available data and stops
    """
    df = spark \
        .read \
        .format("kafka") \
        .option("kafka.bootstrap.servers", kafka_config["kafka.bootstrap.servers"]) \
        .option("subscribe", kafka_config["subscribe"]) \
        .option("startingOffsets", kafka_config["startingOffsets"]) \
        .option("endingOffsets", "latest") \
        .load()
    
    # Parse Kafka message
    parsed_df = df.select(
        col("partition"),
        col("offset"),
        col("timestamp"),
        col("key").cast("string"),
        col("value").cast("string")
    )
    
    return parsed_df

# =============================================================================
# 2. STREAMING READ FROM KAFKA WITH OFFSET TRACKING
# =============================================================================

def streaming_kafka_read_with_offset_tracking():
    """
    Streaming read from Kafka with offset tracking
    """
    # Read stream
    df = spark \
        .readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", kafka_config["kafka.bootstrap.servers"]) \
        .option("subscribe", kafka_config["subscribe"]) \
        .option("startingOffsets", kafka_config["startingOffsets"]) \
        .option("failOnDataLoss", kafka_config["failOnDataLoss"]) \
        .load()
    
    # Parse Kafka message and extract JSON data
    schema = StructType([
        StructField("id", StringType(), True),
        StructField("name", StringType(), True),
        StructField("timestamp", LongType(), True),
        StructField("value", DoubleType(), True)
    ])
    
    parsed_df = df.select(
        col("partition"),
        col("offset"),
        col("timestamp").alias("kafka_timestamp"),
        col("key").cast("string"),
        from_json(col("value").cast("string"), schema).alias("data")
    ).select(
        col("partition"),
        col("offset"),
        col("kafka_timestamp"),
        col("key"),
        col("data.*")
    )
    
    return parsed_df

# =============================================================================
# 3. OFFSET MANAGEMENT FUNCTIONS
# =============================================================================

def save_offsets_to_checkpoint(query, checkpoint_location):
    """
    Save offsets using Spark's built-in checkpointing
    """
    return query.option("checkpointLocation", checkpoint_location)

def get_last_committed_offsets(checkpoint_location):
    """
    Read last committed offsets from checkpoint
    """
    try:
        # Read offset information from checkpoint metadata
        offset_df = spark.read.json(f"{checkpoint_location}/offsets")
        return offset_df
    except Exception as e:
        print(f"Error reading offsets: {e}")
        return None

# Custom offset management in external storage
def save_offsets_to_database(batch_df, batch_id, connection_string):
    """
    Custom function to save offsets to external database
    """
    # Extract offset information
    offset_info = batch_df.select("partition", "offset").distinct()
    
    # Save to database (example with SQL Server)
    offset_info.write \
        .format("jdbc") \
        .option("url", connection_string) \
        .option("dbtable", "kafka_offsets") \
        .option("user", "username") \
        .option("password", "password") \
        .mode("overwrite") \
        .save()

# =============================================================================
# 4. STORAGE METHODS
# =============================================================================

# 4.1 MSSQL Storage
def store_to_mssql(df, mode="append"):
    """
    Store DataFrame to Microsoft SQL Server
    """
    mssql_config = {
        "url": "jdbc:sqlserver://localhost:1433;databaseName=your_database",
        "dbtable": "your_table",
        "user": "your_username",
        "password": "your_password",
        "driver": "com.microsoft.sqlserver.jdbc.SQLServerDriver"
    }
    
    df.write \
        .format("jdbc") \
        .option("url", mssql_config["url"]) \
        .option("dbtable", mssql_config["dbtable"]) \
        .option("user", mssql_config["user"]) \
        .option("password", mssql_config["password"]) \
        .option("driver", mssql_config["driver"]) \
        .mode(mode) \
        .save()

def store_streaming_to_mssql(streaming_df):
    """
    Store streaming DataFrame to MSSQL
    """
    def write_to_mssql(batch_df, batch_id):
        if not batch_df.isEmpty():
            store_to_mssql(batch_df, "append")
    
    query = streaming_df.writeStream \
        .foreachBatch(write_to_mssql) \
        .outputMode("append") \
        .trigger(processingTime='30 seconds') \
        .start()
    
    return query

# 4.2 Spark/Parquet Storage
def store_to_spark_tables(df, table_name, mode="append"):
    """
    Store DataFrame as Spark table (Parquet format)
    """
    df.write \
        .format("parquet") \
        .mode(mode) \
        .option("path", f"/path/to/spark/tables/{table_name}") \
        .saveAsTable(table_name)

def store_streaming_to_parquet(streaming_df, output_path):
    """
    Store streaming DataFrame to Parquet files
    """
    query = streaming_df.writeStream \
        .format("parquet") \
        .option("path", output_path) \
        .option("checkpointLocation", f"{output_path}/_checkpoint") \
        .outputMode("append") \
        .trigger(processingTime='1 minute') \
        .start()
    
    return query

# 4.3 Cassandra Storage
def store_to_cassandra(df, keyspace, table):
    """
    Store DataFrame to Cassandra
    """
    df.write \
        .format("org.apache.spark.sql.cassandra") \
        .option("keyspace", keyspace) \
        .option("table", table) \
        .mode("append") \
        .save()

def store_streaming_to_cassandra(streaming_df, keyspace, table):
    """
    Store streaming DataFrame to Cassandra
    """
    def write_to_cassandra(batch_df, batch_id):
        if not batch_df.isEmpty():
            store_to_cassandra(batch_df, keyspace, table)
    
    query = streaming_df.writeStream \
        .foreachBatch(write_to_cassandra) \
        .outputMode("append") \
        .trigger(processingTime='15 seconds') \
        .start()
    
    return query

# 4.4 MongoDB Storage
def store_to_mongodb(df, database, collection, mode="append"):
    """
    Store DataFrame to MongoDB
    """
    df.write \
        .format("mongodb") \
        .option("database", database) \
        .option("collection", collection) \
        .mode(mode) \
        .save()

def store_streaming_to_mongodb(streaming_df, database, collection):
    """
    Store streaming DataFrame to MongoDB
    """
    def write_to_mongodb(batch_df, batch_id):
        if not batch_df.isEmpty():
            store_to_mongodb(batch_df, database, collection, "append")
    
    query = streaming_df.writeStream \
        .foreachBatch(write_to_mongodb) \
        .outputMode("append") \
        .trigger(processingTime='20 seconds') \
        .start()
    
    return query

# =============================================================================
# 5. COMPLETE EXAMPLES
# =============================================================================

def example_static_processing():
    """
    Complete example of static Kafka processing
    """
    print("Starting static Kafka processing...")
    
    # Read static data
    df = static_kafka_read()
    
    # Show sample data
    df.show(10, truncate=False)
    
    # Store in different databases
    store_to_mssql(df)
    store_to_spark_tables(df, "kafka_static_data")
    store_to_cassandra(df, "your_keyspace", "kafka_data")
    store_to_mongodb(df, "your_database", "kafka_collection")
    
    print("Static processing completed!")

def example_streaming_processing_with_offset_tracking():
    """
    Complete example of streaming Kafka processing with offset tracking
    """
    print("Starting streaming Kafka processing...")
    
    # Read streaming data
    streaming_df = streaming_kafka_read_with_offset_tracking()
    
    # Checkpoint location for offset management
    checkpoint_location = "/path/to/checkpoint"
    
    # Start multiple streaming queries for different storage systems
    queries = []
    
    # Stream to MSSQL
    query1 = store_streaming_to_mssql(streaming_df) \
        .option("checkpointLocation", f"{checkpoint_location}/mssql")
    queries.append(query1)
    
    # Stream to Parquet
    query2 = store_streaming_to_parquet(streaming_df, "/path/to/parquet/output")
    queries.append(query2)
    
    # Stream to Cassandra
    query3 = store_streaming_to_cassandra(streaming_df, "your_keyspace", "streaming_data")
    queries.append(query3)
    
    # Stream to MongoDB
    query4 = store_streaming_to_mongodb(streaming_df, "your_database", "streaming_collection")
    queries.append(query4)
    
    # Console output for monitoring
    query5 = streaming_df.writeStream \
        .outputMode("append") \
        .format("console") \
        .option("truncate", False) \
        .option("numRows", 5) \
        .trigger(processingTime='30 seconds') \
        .start()
    queries.append(query5)
    
    return queries

def monitor_streaming_queries(queries):
    """
    Monitor streaming queries and handle offset tracking
    """
    try:
        # Wait for all queries to terminate
        for query in queries:
            query.awaitTermination()
    except KeyboardInterrupt:
        print("Stopping streaming queries...")
        for query in queries:
            query.stop()
        print("All queries stopped.")

# =============================================================================
# 6. ADVANCED OFFSET MANAGEMENT
# =============================================================================

def resume_from_specific_offsets():
    """
    Resume streaming from specific offsets
    """
    # Define specific starting offsets
    starting_offsets = """{
        "your_topic_name": {
            "0": 1000,
            "1": 2000,
            "2": 1500
        }
    }"""
    
    df = spark \
        .readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", kafka_config["kafka.bootstrap.servers"]) \
        .option("subscribe", kafka_config["subscribe"]) \
        .option("startingOffsets", starting_offsets) \
        .load()
    
    return df

# =============================================================================
# 7. MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":
    try:
        # Choose execution mode
        execution_mode = "streaming"  # or "static"
        
        if execution_mode == "static":
            example_static_processing()
        else:
            queries = example_streaming_processing_with_offset_tracking()
            monitor_streaming_queries(queries)
            
    except Exception as e:
        print(f"Error in main execution: {e}")
    finally:
        spark.stop()

# =============================================================================
# 8. UTILITY FUNCTIONS
# =============================================================================

def get_kafka_topic_info():
    """
    Get information about Kafka topic partitions and offsets
    """
    df = spark \
        .read \
        .format("kafka") \
        .option("kafka.bootstrap.servers", kafka_config["kafka.bootstrap.servers"]) \
        .option("subscribe", kafka_config["subscribe"]) \
        .option("startingOffsets", "earliest") \
        .option("endingOffsets", "latest") \
        .load()
    
    # Show partition and offset information
    df.select("partition", "offset").groupBy("partition").agg(
        min("offset").alias("min_offset"),
        max("offset").alias("max_offset"),
        count("*").alias("message_count")
    ).show()

def cleanup_checkpoint(checkpoint_location):
    """
    Clean up checkpoint directory
    """
    import shutil
    import os
    
    if os.path.exists(checkpoint_location):
        shutil.rmtree(checkpoint_location)
        print(f"Checkpoint directory {checkpoint_location} cleaned up.")
```
