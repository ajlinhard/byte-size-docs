# Python JSON Cheatsheet

I've created a comprehensive Python JSON cheatsheet for you that covers the basics through advanced usage. Here's a quick overview of what's included:

## Key sections in the cheatsheet:

- Basic serialization and deserialization
- File operations (reading/writing JSON)
- Formatting options for pretty printing
- Type conversion between Python and JSON
- Error handling for common JSON issues
- Working with APIs and JSON

## Custom JSON Encoder/Decoder Example

The cheatsheet includes a detailed example of creating your own JSON encoder and decoder, which is particularly useful for handling Python types that aren't natively supported by JSON (like datetime objects and sets).

The custom encoder example shows how to:
- Create a class that inherits from `json.JSONEncoder`
- Override the `default()` method to handle special types
- Add type information to preserve data types during serialization

The custom decoder example demonstrates:
- Creating a class that inherits from `json.JSONDecoder`
- Using the `object_hook` parameter to process custom types
- Converting the JSON objects back into their original Python types

These custom encoder/decoder classes help maintain data integrity when working with complex Python objects that need to be serialized to JSON and back again.

# Python JSON Cheatsheet

## Basic JSON Operations

### Importing the JSON Module
```python
import json
```

### Python to JSON (Serialization)

| Python | JSON |
|--------|------|
| dict | object |
| list, tuple | array |
| str | string |
| int, float | number |
| True | true |
| False | false |
| None | null |

### Converting Python to JSON String
```python
# Convert Python dict to JSON string
data = {"name": "John", "age": 30, "city": "New York"}
json_string = json.dumps(data)
print(json_string)  # {"name": "John", "age": 30, "city": "New York"}

# Pretty printing with indentation
json_string = json.dumps(data, indent=4)
print(json_string)
# {
#     "name": "John",
#     "age": 30,
#     "city": "New York"
# }

# Sorting keys alphabetically
json_string = json.dumps(data, sort_keys=True)

# Other formatting options
json_string = json.dumps(data, indent=4, separators=(", ", ": "), sort_keys=True)
```

### Writing JSON to a File
```python
data = {"name": "John", "age": 30, "city": "New York"}
with open("data.json", "w") as f:
    json.dump(data, f, indent=4)
```

### JSON to Python (Deserialization)

| JSON | Python |
|------|--------|
| object | dict |
| array | list |
| string | str |
| number (int) | int |
| number (real) | float |
| true | True |
| false | False |
| null | None |

### Converting JSON String to Python
```python
json_string = '{"name": "John", "age": 30, "city": "New York"}'
data = json.loads(json_string)
print(data["name"])  # John
```

### Reading JSON from a File
```python
with open("data.json", "r") as f:
    data = json.load(f)
print(data)
```

## Advanced Usage

### Handling JSON Encoding Errors
```python
# Handle non-serializable objects
import datetime

data = {"date": datetime.datetime.now()}

# This will raise a TypeError
# json.dumps(data)

# Use default parameter to handle non-serializable types
def serialize_datetime(obj):
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")

json_string = json.dumps(data, default=serialize_datetime)
print(json_string)  # {"date": "2025-03-24T10:30:45.123456"}
```

### Working with Complex Data Types
```python
# Handling sets (not natively supported by JSON)
data = {"items": set([1, 2, 3])}

# Convert set to list for serialization
json_string = json.dumps(data, default=lambda obj: list(obj) if isinstance(obj, set) else obj)
print(json_string)  # {"items": [1, 2, 3]}
```

## Custom JSON Encoder and Decoder

### Custom JSON Encoder
```python
import json
import datetime

class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return {
                "_type": "datetime",
                "value": obj.isoformat()
            }
        elif isinstance(obj, set):
            return {
                "_type": "set",
                "value": list(obj)
            }
        return super().default(obj)

# Example data with custom types
data = {
    "name": "Conference",
    "date": datetime.datetime(2025, 4, 15, 9, 30),
    "attendees": set(["Alice", "Bob", "Charlie"])
}

# Serialize with custom encoder
json_string = json.dumps(data, cls=CustomEncoder, indent=4)
print(json_string)
# {
#     "name": "Conference",
#     "date": {
#         "_type": "datetime",
#         "value": "2025-04-15T09:30:00"
#     },
#     "attendees": {
#         "_type": "set",
#         "value": ["Alice", "Bob", "Charlie"]
#     }
# }
```

### Custom JSON Decoder
```python
import json
import datetime

class CustomDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)
    
    def object_hook(self, obj):
        if "_type" not in obj:
            return obj
        
        type_name = obj["_type"]
        if type_name == "datetime":
            return datetime.datetime.fromisoformat(obj["value"])
        elif type_name == "set":
            return set(obj["value"])
        return obj

# Deserialize with custom decoder
json_string = '''
{
    "name": "Conference",
    "date": {
        "_type": "datetime",
        "value": "2025-04-15T09:30:00"
    },
    "attendees": {
        "_type": "set",
        "value": ["Alice", "Bob", "Charlie"]
    }
}
'''

data = json.loads(json_string, cls=CustomDecoder)
print(type(data["date"]))  # <class 'datetime.datetime'>
print(type(data["attendees"]))  # <class 'set'>
print(data["date"])  # 2025-04-15 09:30:00
print(data["attendees"])  # {'Alice', 'Bob', 'Charlie'}
```

## Error Handling

### Common JSON Errors
```python
# Handling JSON decode errors
invalid_json = '{"name": "John", "age": 30, "city": New York}'  # Missing quotes around New York

try:
    data = json.loads(invalid_json)
except json.JSONDecodeError as e:
    print(f"JSON decode error: {e.msg} at line {e.lineno}, column {e.colno}")
```

## Working with APIs

### Fetching and Parsing JSON from an API
```python
import requests

response = requests.get("https://api.example.com/data")
if response.status_code == 200:
    data = response.json()  # requests has built-in JSON decoder
    print(data)
else:
    print(f"Error: {response.status_code}")
```

### Sending JSON to an API
```python
import requests

data = {"name": "John", "age": 30}
response = requests.post("https://api.example.com/users", json=data)
# The 'json' parameter automatically serializes the data and sets Content-Type header

if response.status_code == 201:
    new_user = response.json()
    print(f"Created user with ID: {new_user['id']}")
else:
    print(f"Error: {response.status_code}")
```

Circular references in JSON occur when an object contains a reference to itself, either directly or through a chain of references. This creates a cycle in the data structure that cannot be represented in standard JSON.

## Example of a Circular Reference

Here's a simple example in Python:

```python
# Create a dictionary
person = {
    "name": "Alice",
    "friends": []
}

# Create circular reference by adding itself to the friends list
person["friends"].append(person)

# Now person refers to itself inside its own structure
```

In this example, `person` contains a list of friends, and one of those friends is the `person` object itself. This creates an infinite loop in the structure.

## Why Circular References Are Problematic

Standard JSON doesn't support circular references for several reasons:

1. **Infinite Serialization**: When converting to JSON, the encoder would need to recursively process the object forever.

2. **JSON Specification Limitation**: The JSON specification doesn't include any mechanism for reference identities or pointers.

3. **Memory Concerns**: Processing such structures could lead to infinite memory consumption.

When you try to serialize an object with circular references using the standard JSON encoder:

```python
import json
json.dumps(person)  # This will raise: TypeError: Object of type dict is not JSON serializable
```

You'll get a `TypeError` or a recursion error.

## Solutions for Handling Circular References

1. **Custom Encoder with Object Tracking**:
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
               return {"$ref": "circular"}
           
           self.seen_objects.add(obj_id)
           
           if isinstance(obj, dict):
               result = {key: self.default(value) for key, value in obj.items()}
               self.seen_objects.remove(obj_id)
               return result
               
           # Handle other types...
           return super().default(obj)
   ```

2. **Using External Libraries**: Some libraries like `python-dill` or `jsonpickle` can handle circular references.

3. **Breaking the Circle Before Serialization**: 
   - Replace circular references with IDs or reference keys
   - Remove circular references entirely
   - Use a depth limit when traversing the structure

## Real-World Implications

Circular references commonly appear in:

- **Object-Relational Mappings**: Parent-child relationships, many-to-many relationships
- **Graph Data Structures**: Social networks, organization charts
- **DOM Trees**: Where parent elements contain references to children and vice versa

When working with systems that might contain circular references (like database ORM models), it's important to handle these cases carefully when serializing to JSON.

## Best Practices

1. Always use try-except blocks when parsing external JSON
2. Use context managers (`with` statement) when working with files
3. Consider using custom encoders/decoders for complex data types
4. Set appropriate content type headers in API requests (`application/json`)
5. Validate JSON schema when working with critical data
6. Be careful with large JSON files - consider streaming for big datasets
7. Use pretty printing during development for readability
8. Don't rely on key order in JSON objects (unless using `sort_keys=True`)
