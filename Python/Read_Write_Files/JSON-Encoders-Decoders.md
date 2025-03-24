# In-Depth Guide to JSON Encoders & Decoders in Python

## Understanding JSON Encoders and Decoders

### How JSON Encoding Works

The Python `json` module uses encoders to convert Python objects to JSON strings. At its core, the encoding process follows these steps:

1. **Initial Type Check**: The encoder first checks if the object is a basic type (dict, list, string, number, etc.) that has a direct JSON equivalent.
2. **Conversion**: If it's a basic type, it's directly converted to its JSON representation.
3. **Complex Type Handling**: If it's not a basic type, the encoder looks for additional handling methods:
   - For custom encoders, the `default()` method is called
   - The result from `default()` is then encoded recursively

### How JSON Decoding Works

Decoding follows a similar but reverse process:

1. **Parse JSON**: The JSON string is parsed into a basic structure (dicts, lists, strings, etc.)
2. **Custom Processing**: If using a custom decoder with `object_hook`, each dictionary object is passed through this function
3. **Type Reconstruction**: The `object_hook` function can transform dictionaries into custom Python objects

## Advanced Custom Encoder Techniques

### Method 1: Using the `default` Parameter

For simple cases, you can use the `default` parameter with `json.dumps()`:

```python
import json
import datetime

def custom_encoder(obj):
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()
    elif isinstance(obj, complex):
        return {"real": obj.real, "imag": obj.imag, "_type": "complex"}
    else:
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

data = {
    "timestamp": datetime.datetime.now(),
    "value": complex(1, 2)
}

json_string = json.dumps(data, default=custom_encoder, indent=2)
```

### Method 2: Creating a Full Encoder Class

For more complex scenarios, subclass `json.JSONEncoder`:

```python
import json
import datetime
import uuid
import decimal

class AdvancedJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        # Handle various special types
        if isinstance(obj, datetime.datetime):
            return {
                "_type": "datetime",
                "value": obj.isoformat()
            }
        elif isinstance(obj, uuid.UUID):
            return {
                "_type": "uuid",
                "value": str(obj)
            }
        elif isinstance(obj, decimal.Decimal):
            return {
                "_type": "decimal",
                "value": str(obj)
            }
        elif hasattr(obj, "__dict__"):
            # Handle custom classes by converting to dict
            obj_dict = obj.__dict__.copy()
            obj_dict["_type"] = obj.__class__.__name__
            return obj_dict
        
        # Let the base class raise the TypeError
        return super().default(obj)
```

### Handling Circular References

Standard JSON encoding fails with circular references. You can implement a solution:

```python
import json

class CircularReferenceEncoder(json.JSONEncoder):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.seen_objects = set()
    
    def default(self, obj):
        # Get object ID to track it
        obj_id = id(obj)
        
        # If we've seen this object already
        if obj_id in self.seen_objects:
            return {"_circular_ref": True}
        
        self.seen_objects.add(obj_id)
        
        # Handle dictionaries specially to track all nested objects
        if isinstance(obj, dict):
            result = {key: self.default(value) for key, value in obj.items()}
            self.seen_objects.remove(obj_id)
            return result
            
        # Handle other iterables
        if hasattr(obj, "__iter__") and not isinstance(obj, str):
            result = [self.default(item) for item in obj]
            self.seen_objects.remove(obj_id)
            return result
            
        # For other objects, use standard handling
        try:
            result = super().default(obj)
            self.seen_objects.remove(obj_id)
            return result
        except TypeError:
            if hasattr(obj, "__dict__"):
                result = {key: self.default(value) for key, value in obj.__dict__.items()}
                result["_type"] = obj.__class__.__name__
                self.seen_objects.remove(obj_id)
                return result
            raise
```

## Advanced Custom Decoder Techniques

### Method 1: Using `object_hook`

The simplest approach is using the `object_hook` parameter:

```python
import json
import datetime

def custom_decoder(obj):
    if "_type" in obj:
        type_name = obj["_type"]
        if type_name == "datetime":
            return datetime.datetime.fromisoformat(obj["value"])
        elif type_name == "complex":
            return complex(obj["real"], obj["imag"])
    return obj

json_string = '{"timestamp": {"_type": "datetime", "value": "2025-03-24T12:34:56"}, "value": {"_type": "complex", "real": 1, "imag": 2}}'
data = json.loads(json_string, object_hook=custom_decoder)
```

### Method 2: Full Decoder Class

For more control, create a custom decoder class:

```python
import json
import datetime
import uuid
import decimal

class AdvancedJSONDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        # Remove any custom kwargs we use before passing to parent
        self.custom_types = kwargs.pop('custom_types', {})
        # Set up the object_hook
        kwargs['object_hook'] = self.object_hook
        super().__init__(*args, **kwargs)
    
    def object_hook(self, obj):
        # Check if this is a typed object
        if "_type" not in obj:
            return obj
            
        type_name = obj["_type"]
        
        # Handle built-in types
        if type_name == "datetime":
            return datetime.datetime.fromisoformat(obj["value"])
        elif type_name == "uuid":
            return uuid.UUID(obj["value"])
        elif type_name == "decimal":
            return decimal.Decimal(obj["value"])
        elif type_name == "set":
            return set(obj["value"])
            
        # Handle custom registered types
        if type_name in self.custom_types:
            class_type = self.custom_types[type_name]
            instance = class_type.__new__(class_type)
            
            # Copy all properties except _type
            for key, value in obj.items():
                if key != "_type":
                    setattr(instance, key, value)
                    
            # Call __init__ if it's expected to be called without args
            if hasattr(instance, "__init__") and getattr(instance.__init__, "__code__", None) and instance.__init__.__code__.co_argcount == 1:
                instance.__init__()
                
            return instance
                
        return obj
```

## Performance Considerations

### Optimizing JSON Encoding/Decoding

1. **Use `ujson` or `orjson` for speed**: These third-party libraries can be much faster than the standard `json` module:

   ```python
   # Using ujson
   import ujson
   json_str = ujson.dumps(data)
   data = ujson.loads(json_str)
   
   # Using orjson (even faster, but returns bytes)
   import orjson
   json_bytes = orjson.dumps(data)
   json_str = json_bytes.decode('utf-8')
   data = orjson.loads(json_bytes)
   ```

2. **Batch processing for large datasets**: Instead of encoding/decoding an entire large dataset at once, process it in chunks.

3. **Stream processing for files**: For very large JSON files, use streaming:

   ```python
   import json
   
   # Streaming large JSON array
   def json_array_stream(file_obj):
       decoder = json.JSONDecoder()
       buffer = ''
       
       for chunk in iter(lambda: file_obj.read(4096), ''):
           buffer += chunk
           try:
               obj, idx = decoder.raw_decode(buffer)
               buffer = buffer[idx:].lstrip()
               yield obj
           except json.JSONDecodeError:
               # Not enough data yet, continue reading
               pass
   
   with open('large_file.json') as f:
       for item in json_array_stream(f):
           process_item(item)
   ```

# Framework-Specific JSON Handling

## Pandas JSON Support

Pandas provides built-in methods for reading and writing JSON:

### Reading JSON

```python
import pandas as pd

# Basic JSON to DataFrame
df = pd.read_json('data.json')

# JSON lines (one JSON object per line)
df = pd.read_json('data.jsonl', lines=True)

# Reading from URL
df = pd.read_json('https://api.example.com/data')

# Reading nested JSON with normalization
df = pd.json_normalize(json_data)

# Reading with custom orientation
df = pd.read_json('data.json', orient='records')
```

### Writing JSON

```python
# Basic DataFrame to JSON
df.to_json('output.json')

# JSON lines format
df.to_json('output.jsonl', orient='records', lines=True)

# Different orientations
df.to_json('output.json', orient='columns')
df.to_json('output.json', orient='records')
df.to_json('output.json', orient='index')
df.to_json('output.json', orient='split')
df.to_json('output.json', orient='table')

# Get JSON string instead of writing to file
json_str = df.to_json(orient='records')
```

### Custom Encoding in Pandas

Pandas integrates with the standard JSON module, so you can use custom encoders:

```python
import pandas as pd
import json
import datetime

class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        return super().default(obj)

# Using custom encoder with pandas
df = pd.DataFrame({
    'date': [datetime.datetime.now()],
    'value': [42]
})

json_str = df.to_json(date_format='iso', default_handler=lambda obj: obj.isoformat() if isinstance(obj, datetime.datetime) else None)
```

## Apache Spark JSON Support

Spark provides built-in capabilities for reading and writing JSON:

### Reading JSON

```python
from pyspark.sql import SparkSession

# Initialize Spark
spark = SparkSession.builder.appName("JSON_Processing").getOrCreate()

# Read JSON file into DataFrame
df = spark.read.json("data.json")

# Read multiple JSON files
df = spark.read.json("data_folder/*.json")

# Read with schema inference options
df = spark.read.option("inferSchema", "true").json("data.json")

# Read with explicit schema
from pyspark.sql.types import StructType, StructField, StringType, IntegerType
schema = StructType([
    StructField("name", StringType(), True),
    StructField("age", IntegerType(), True)
])
df = spark.read.schema(schema).json("data.json")

# Read multi-line JSON
df = spark.read.option("multiline", "true").json("data.json")
```

### Writing JSON

```python
# Write DataFrame to JSON files
df.write.json("output_folder")

# Write as a single file
df.coalesce(1).write.json("output_folder")

# Write with compression
df.write.option("compression", "gzip").json("compressed_output")

# Write with specific mode (overwrite, append, etc.)
df.write.mode("overwrite").json("output_folder")
```

### Custom JSON Handling in Spark

Spark uses its own optimized JSON serialization/deserialization system, but you can implement custom handling using UDFs (User Defined Functions):

```python
from pyspark.sql.functions import udf
from pyspark.sql.types import StringType, StructType, StructField, StringType
import json

# Create UDF for custom JSON serialization
@udf(StringType())
def serialize_complex_data(data):
    class CustomEncoder(json.JSONEncoder):
        def default(self, obj):
            # Custom encoding logic
            return super().default(obj)
    
    return json.dumps(data, cls=CustomEncoder)

# Apply UDF to a column
df_with_json = df.withColumn("json_data", serialize_complex_data("complex_column"))
```

## Apache Kafka JSON Handling

Kafka itself doesn't directly handle JSON encoding/decoding, but it provides serializers and deserializers that can be used for JSON:

### Using Kafka's JSON Serializer/Deserializer

```python
from kafka import KafkaProducer, KafkaConsumer
import json

# Producer with JSON serialization
producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Send JSON data
producer.send('topic_name', {'key': 'value'})

# Consumer with JSON deserialization
consumer = KafkaConsumer(
    'topic_name',
    bootstrap_servers=['localhost:9092'],
    value_deserializer=lambda v: json.loads(v.decode('utf-8'))
)

# Consume JSON messages
for message in consumer:
    data = message.value
    print(data)
```

### Using Confluent's Schema Registry with JSON

For more advanced scenarios, you can use Confluent's JSON Schema Registry:

```python
from confluent_kafka import Producer, Consumer
from confluent_kafka.serialization import SerializationContext, MessageField
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.json_schema import JSONSerializer, JSONDeserializer

# Schema Registry client
schema_registry_client = SchemaRegistryClient({'url': 'http://localhost:8081'})

# JSON schema
json_schema = """
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "User",
  "type": "object",
  "properties": {
    "name": {"type": "string"},
    "age": {"type": "integer"}
  }
}
"""

# Create JSON serializer
json_serializer = JSONSerializer(json_schema, schema_registry_client)

# Producer with JSON Schema serializer
producer = Producer({'bootstrap.servers': 'localhost:9092'})

# Serialize and produce
user = {"name": "John", "age": 30}
producer.produce(
    topic='users',
    value=json_serializer(user, SerializationContext('users', MessageField.VALUE)),
    on_delivery=lambda err, msg: print(f'Delivered: {msg.value().decode()}')
)
producer.flush()

# JSON Deserializer
json_deserializer = JSONDeserializer(json_schema)

# Consumer with JSON Schema deserializer
consumer = Consumer({
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'user-group'
})
consumer.subscribe(['users'])

# Consume and deserialize
while True:
    msg = consumer.poll(1.0)
    if msg is None:
        continue
    user = json_deserializer(msg.value(), SerializationContext('users', MessageField.VALUE))
    print(f"Received user: {user}")
```

## Custom JSON Handlers for All Three Frameworks

### Universal Custom JSON Handler

You can create a universal JSON handler that works across frameworks:

```python
import json
import datetime
import decimal
import uuid

class UniversalJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return {"_type": "datetime", "value": obj.isoformat()}
        elif isinstance(obj, decimal.Decimal):
            return {"_type": "decimal", "value": str(obj)}
        elif isinstance(obj, uuid.UUID):
            return {"_type": "uuid", "value": str(obj)}
        elif hasattr(obj, "__dict__"):
            return {"_type": obj.__class__.__name__, **obj.__dict__}
        return super().default(obj)

class UniversalJSONDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        kwargs['object_hook'] = self.object_hook
        super().__init__(*args, **kwargs)
    
    def object_hook(self, obj):
        if "_type" not in obj:
            return obj
            
        type_name = obj["_type"]
        if type_name == "datetime":
            return datetime.datetime.fromisoformat(obj["value"])
        elif type_name == "decimal":
            return decimal.Decimal(obj["value"])
        elif type_name == "uuid":
            return uuid.UUID(obj["value"])
        return obj
```

### Using with Pandas

```python
import pandas as pd

# Serialize with custom encoder
df = pd.DataFrame({"timestamp": [datetime.datetime.now()]})
json_str = df.to_json(default_handler=lambda obj: UniversalJSONEncoder().default(obj))

# Deserialize
from io import StringIO
json_data = StringIO(json_str)
df = pd.read_json(json_data)
```

### Using with Spark

```python
from pyspark.sql.functions import udf, from_json
from pyspark.sql.types import StringType, MapType, StringType

# Create UDFs for handling JSON
@udf(StringType())
def universal_json_encode(data):
    return json.dumps(data, cls=UniversalJSONEncoder)

# Apply encoding
df_encoded = df.withColumn("json_data", universal_json_encode("data_column"))

# For decoding, you would use a Python UDF or process after collecting
def universal_json_decode(json_str):
    return json.loads(json_str, cls=UniversalJSONDecoder)

# Apply after collecting (for smaller datasets)
decoded_data = df.select("json_column").collect()
decoded_data = [universal_json_decode(row["json_column"]) for row in decoded_data]
```

### Using with Kafka

```python
from kafka import KafkaProducer, KafkaConsumer

# Producer with universal encoder
producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v, cls=UniversalJSONEncoder).encode('utf-8')
)

# Consumer with universal decoder
consumer = KafkaConsumer(
    'topic_name',
    bootstrap_servers=['localhost:9092'],
    value_deserializer=lambda v: json.loads(v.decode('utf-8'), cls=UniversalJSONDecoder)
)
```
