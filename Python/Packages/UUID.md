# Python UUID Package Explained

The UUID (Universally Unique Identifier) package in Python is used to generate unique identifiers following the UUID standard. These IDs are 128-bit values designed to be unique across space and time.
[Python Docs for UUID](https://docs.python.org/3/library/uuid.html)

## How UUID Works

The `uuid` module in Python implements the UUID standard as defined in RFC 4122. It provides functions to generate UUIDs of different versions:

1. **UUID1**: Generated using the computer's MAC address and current timestamp
2. **UUID3**: Generated using an MD5 hash of a namespace identifier and name
3. **UUID4**: Generated using random numbers
4. **UUID5**: Generated using an SHA-1 hash of a namespace identifier and name

Under the hood, the module creates a 128-bit number represented as a 32-character hexadecimal string in the format: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`

## UUID Cheatsheet

```python
import uuid

# Generate a UUID based on host ID and time (UUID1)
id1 = uuid.uuid1()
print(id1)  # e.g. 12345678-1234-1234-1234-123456789abc

# Generate a UUID using MD5 hash (UUID3)
id3 = uuid.uuid3(uuid.NAMESPACE_DNS, "example.com")
print(id3)  # always the same for the same namespace and name

# Generate a random UUID (UUID4) - most commonly used
id4 = uuid.uuid4()
print(id4)  # different every time

# Generate a UUID using SHA-1 hash (UUID5)
id5 = uuid.uuid5(uuid.NAMESPACE_DNS, "example.com")
print(id5)  # always the same for the same namespace and name

# Convert UUID to string
str_uuid = str(id4)
print(str_uuid)  # '12345678-1234-1234-1234-123456789abc'

# Create UUID from string
from_str = uuid.UUID(str_uuid)
print(from_str)  # same as id4

# Access UUID components
print(id4.hex)  # 32-character hex string without dashes
print(id4.int)  # 128-bit integer
print(id4.version)  # version number (1, 3, 4, or 5)
print(id4.variant)  # variant (identifies layout of UUID)
print(id4.bytes)  # 16 bytes representation

# Built-in namespaces for version 3 and 5
print(uuid.NAMESPACE_DNS)  # for domain names
print(uuid.NAMESPACE_URL)  # for URLs
print(uuid.NAMESPACE_OID)  # for ISO OIDs
print(uuid.NAMESPACE_X500)  # for X.500 DNs
```

## Common Use Cases

- Database primary keys
- Distributed systems where unique identifiers are needed
- Session IDs in web applications
- Randomly generated filenames
- Tracking unique events or transactions
