# Streaming Kafka to MSSQL: Multiple Approaches

I'll show you various approaches to stream data from Kafka to Microsoft SQL Server (MSSQL) using Python-based frameworks like PySpark, Flink, and other options. Similar concepts can be used by replacing MSSQL with whatever backend database you want to send data to.

## Comparison of Approaches

| Approach | Pros | Cons |
|---------|------|------|
| [PySpark](#1-using-pyspark-structured-streaming) | - Scalable processing<br>- Built-in fault tolerance<br>- Rich transformations | - Requires Spark cluster<br>- Higher resource overhead |
| [PyFlink](#2-using-apache-flink-with-pyflink) | - Exactly-once semantics<br>- Stateful processing<br>- Low latency | - Steeper learning curve<br>- Requires Flink cluster |
| [Kafka Connect]((#3-using-kafka-connect-with-jdbc-connector)) | - Production-ready<br>- Many pre-built connectors<br>- No coding required | - Less flexibility<br>- Requires Kafka Connect setup |
| [Custom Solution](#4-custom-python-producer-consumer-solution)) | - Full control<br>- Lightweight<br>- Simple to understand | - Must handle failures manually<br>- Limited scalability |
| [SQLAlchemy](#5-using-kafka-python-and-sql-alchemy) | - Pythonic database access<br>- ORM capabilities<br>- Database independence | - Potential performance overhead<br>- Must handle concurrency |
** Some more below with [Best Practices](#best-practices) **

## 1. Using PySpark Structured Streaming

PySpark provides excellent support for streaming Kafka data to external databases:

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StructField, StringType, IntegerType

# Define your schema based on the Kafka message format
kafka_schema = StructType([
    StructField("id", IntegerType(), True),
    StructField("name", StringType(), True),
    StructField("value", StringType(), True),
    # Add other fields as needed
])

# Initialize Spark Session
spark = SparkSession.builder \
    .appName("KafkaToMSSQL") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0,com.microsoft.sqlserver:mssql-jdbc:9.4.1.jre8") \
    .getOrCreate()

# Read from Kafka
kafka_stream = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "your-topic") \
    .option("startingOffsets", "latest") \
    .load()

# Parse the Kafka messages
parsed_stream = kafka_stream \
    .selectExpr("CAST(value AS STRING)") \
    .select(from_json(col("value"), kafka_schema).alias("data")) \
    .select("data.*")

# Write to MSSQL using foreachBatch
def write_to_mssql(batch_df, batch_id):
    # Set up JDBC URL and properties
    jdbc_url = "jdbc:sqlserver://your-server:1433;databaseName=your-db"
    connection_properties = {
        "user": "username",
        "password": "password",
        "driver": "com.microsoft.sqlserver.jdbc.SQLServerDriver"
    }
    
    # Write batch to MSSQL
    batch_df.write \
        .format("jdbc") \
        .option("url", jdbc_url) \
        .option("dbtable", "your_table") \
        .option("user", "username") \
        .option("password", "password") \
        .mode("append") \
        .save()

# Execute the streaming query
query = parsed_stream \
    .writeStream \
    .foreachBatch(write_to_mssql) \
    .outputMode("update") \
    .option("checkpointLocation", "/tmp/checkpoint") \
    .start()

query.awaitTermination()
```

## 2. Using Apache Flink with PyFlink

Flink provides powerful streaming capabilities with exactly-once semantics:

```python
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import StreamTableEnvironment, EnvironmentSettings
from pyflink.table.descriptors import Kafka, Json, Schema, Rowtime
from pyflink.table.window import Tumble

# Create execution environment
env = StreamExecutionEnvironment.get_execution_environment()
env.set_parallelism(1)

# Add required JAR files to the environment
env.add_jars("file:///path/to/flink-connector-kafka-2.12-1.15.0.jar",
             "file:///path/to/kafka-clients-2.8.1.jar",
             "file:///path/to/flink-connector-jdbc-1.15.0.jar",
             "file:///path/to/mssql-jdbc-9.4.1.jre8.jar")

# Create table environment
settings = EnvironmentSettings.new_instance().in_streaming_mode().build()
tbl_env = StreamTableEnvironment.create(env, settings)

# Register a Kafka source
tbl_env.connect(Kafka()
              .version("universal")
              .topic("your-topic")
              .start_from_latest()
              .property("bootstrap.servers", "kafka:9092")
              .property("group.id", "flink-kafka-mssql-connector")) \
    .with_format(Json()
               .fail_on_missing_field(False)
               .schema(Schema()
                     .field("id", "INT")
                     .field("name", "STRING")
                     .field("value", "STRING"))) \
    .with_schema(Schema()
               .field("id", "INT")
               .field("name", "STRING")
               .field("value", "STRING")) \
    .create_temporary_table("kafka_source")

# Register MSSQL sink
jdbcDDL = """
    CREATE TABLE mssql_sink (
        id INT,
        name STRING,
        value STRING
    ) WITH (
        'connector' = 'jdbc',
        'url' = 'jdbc:sqlserver://your-server:1433;databaseName=your-db',
        'table-name' = 'your_table',
        'username' = 'username',
        'password' = 'password',
        'driver' = 'com.microsoft.sqlserver.jdbc.SQLServerDriver'
    )
"""
tbl_env.execute_sql(jdbcDDL)

# Execute the job
tbl_env.from_path("kafka_source").execute_insert("mssql_sink").wait()
```

## 3. Using Kafka Connect with JDBC Connector

Kafka Connect is the most production-ready option (not directly Python, but can be configured via Python):

```python
import requests
import json

# Configure and start Kafka Connect with JDBC connector via REST API
def setup_jdbc_connector():
    connector_config = {
        "name": "mssql-sink",
        "config": {
            "connector.class": "io.confluent.connect.jdbc.JdbcSinkConnector",
            "tasks.max": "1",
            "topics": "your-topic",
            "connection.url": "jdbc:sqlserver://your-server:1433;databaseName=your-db",
            "connection.user": "username",
            "connection.password": "password",
            "auto.create": "true",
            "auto.evolve": "true",
            "insert.mode": "upsert",
            "pk.mode": "record_key",
            "pk.fields": "id",
            "table.name.format": "your_table",
            "transforms": "unwrap",
            "transforms.unwrap.type": "io.debezium.transforms.ExtractField$Value",
            "transforms.unwrap.field": "after"
        }
    }
    
    response = requests.post(
        "http://localhost:8083/connectors",
        headers={"Content-Type": "application/json"},
        data=json.dumps(connector_config)
    )
    
    if response.status_code == 201:
        print("JDBC connector created successfully")
    else:
        print(f"Failed to create connector: {response.text}")

if __name__ == "__main__":
    setup_jdbc_connector()
```

## 4. Custom Python Producer-Consumer Solution

For more control, you can build a custom solution:

```python
from kafka import KafkaConsumer
import json
import pyodbc
import time
from threading import Thread

class KafkaToMSSQLStreamer:
    def __init__(self, bootstrap_servers, topic, db_conn_string, table_name, batch_size=100):
        self.consumer = KafkaConsumer(
            topic,
            bootstrap_servers=bootstrap_servers,
            value_deserializer=lambda x: json.loads(x.decode('utf-8')),
            auto_offset_reset='latest',
            enable_auto_commit=False,
            group_id='kafka-mssql-streamer'
        )
        self.db_conn_string = db_conn_string
        self.table_name = table_name
        self.batch_size = batch_size
        self.running = False
        
    def _get_db_connection(self):
        return pyodbc.connect(self.db_conn_string)
    
    def _create_insert_query(self, message):
        # Customize this based on your message structure and table schema
        columns = ", ".join(message.keys())
        placeholders = ", ".join(["?" for _ in message.keys()])
        values = list(message.values())
        
        return f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders})", values
    
    def _process_batch(self, messages):
        if not messages:
            return
            
        conn = self._get_db_connection()
        cursor = conn.cursor()
        
        try:
            for msg in messages:
                query, values = self._create_insert_query(msg.value)
                cursor.execute(query, values)
            
            # Commit the transaction
            conn.commit()
            
            # Commit Kafka offsets after successful database commit
            self.consumer.commit()
            
        except Exception as e:
            print(f"Error processing batch: {e}")
            conn.rollback()
        finally:
            cursor.close()
            conn.close()
    
    def start(self):
        self.running = True
        thread = Thread(target=self._stream_data)
        thread.daemon = True
        thread.start()
        return thread
    
    def stop(self):
        self.running = False
    
    def _stream_data(self):
        batch = []
        
        while self.running:
            messages = self.consumer.poll(timeout_ms=1000, max_records=self.batch_size)
            
            for _, msgs in messages.items():
                batch.extend(msgs)
                
                if len(batch) >= self.batch_size:
                    self._process_batch(batch)
                    batch = []
            
            # Process any remaining messages in the batch
            if batch:
                self._process_batch(batch)
                batch = []

# Example usage
if __name__ == "__main__":
    conn_string = (
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=your-server,1433;"
        "DATABASE=your-db;"
        "UID=username;"
        "PWD=password"
    )
    
    streamer = KafkaToMSSQLStreamer(
        bootstrap_servers=['kafka:9092'],
        topic='your-topic',
        db_conn_string=conn_string,
        table_name='your_table',
        batch_size=100
    )
    
    stream_thread = streamer.start()
    
    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping streamer...")
        streamer.stop()
        stream_thread.join()
```

## 5. Using Kafka-Python and SQL Alchemy

A more Pythonic approach using SQLAlchemy:

```python
from kafka import KafkaConsumer
import json
from sqlalchemy import create_engine, Table, MetaData, Column, Integer, String
from sqlalchemy.dialects.mssql import insert
import time
from threading import Thread

class KafkaSQLAlchemyStreamer:
    def __init__(self, bootstrap_servers, topic, db_url, table_name, batch_size=100):
        # Kafka Consumer setup
        self.consumer = KafkaConsumer(
            topic,
            bootstrap_servers=bootstrap_servers,
            value_deserializer=lambda x: json.loads(x.decode('utf-8')),
            auto_offset_reset='latest',
            enable_auto_commit=False,
            group_id='kafka-sqlalchemy-streamer'
        )
        
        # SQLAlchemy setup
        self.engine = create_engine(db_url)
        self.metadata = MetaData()
        self.table = self._get_or_create_table(table_name)
        
        self.batch_size = batch_size
        self.running = False
    
    def _get_or_create_table(self, table_name):
        # This is a simplified example - in a real scenario you'd define the table
        # based on your actual schema or use reflection to get existing schema
        try:
            return Table(table_name, self.metadata, autoload_with=self.engine)
        except:
            # If table doesn't exist, create a simple one
            # Customize this based on your Kafka message schema
            table = Table(
                table_name, 
                self.metadata,
                Column('id', Integer, primary_key=True),
                Column('name', String(255)),
                Column('value', String(255))
            )
            self.metadata.create_all(self.engine)
            return table
            
    def _process_batch(self, messages):
        if not messages:
            return
            
        # Start a transaction
        with self.engine.begin() as connection:
            # Process each message
            for msg in messages:
                # Create an upsert (insert or update) query
                # This is MSSQL specific (using MERGE equivalent)
                stmt = insert(self.table).values(msg.value)
                stmt = stmt.on_duplicate_key_update(msg.value)
                connection.execute(stmt)
            
        # Commit Kafka offsets after successful database commit
        self.consumer.commit()
    
    def start(self):
        self.running = True
        thread = Thread(target=self._stream_data)
        thread.daemon = True
        thread.start()
        return thread
    
    def stop(self):
        self.running = False
    
    def _stream_data(self):
        batch = []
        
        while self.running:
            try:
                messages = self.consumer.poll(timeout_ms=1000, max_records=self.batch_size)
                
                for _, msgs in messages.items():
                    batch.extend(msgs)
                    
                    if len(batch) >= self.batch_size:
                        self._process_batch(batch)
                        batch = []
                
                # Process any remaining messages in the batch
                if batch:
                    self._process_batch(batch)
                    batch = []
                    
            except Exception as e:
                print(f"Error in streaming: {e}")
                time.sleep(5)  # Backoff before retrying

# Example usage
if __name__ == "__main__":
    db_url = "mssql+pyodbc://username:password@your-server:1433/your-db?driver=ODBC+Driver+17+for+SQL+Server"
    
    streamer = KafkaSQLAlchemyStreamer(
        bootstrap_servers=['kafka:9092'],
        topic='your-topic',
        db_url=db_url,
        table_name='your_table',
        batch_size=100
    )
    
    stream_thread = streamer.start()
    
    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping streamer...")
        streamer.stop()
        stream_thread.join()
```

## Best Practices

1. **Error Handling**: All approaches should include robust error handling and retry logic.

2. **Batching**: For better performance, process Kafka messages in batches.

3. **Transactions**: Use database transactions to ensure consistency.

4. **Monitoring**: Add metrics collection and monitoring to track performance.

5. **Schema Evolution**: Handle schema changes gracefully between Kafka and MSSQL.
