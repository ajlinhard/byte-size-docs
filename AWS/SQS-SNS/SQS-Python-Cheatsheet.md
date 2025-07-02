# AWS SQS Python Cheatsheet
This cheatsheet covers all the essential SQS functions with their parameters, plus a detailed breakdown of the message object structure you'll encounter when polling. The key sections include:

**Core Functions:**
- `send_message()` and `send_message_batch()` for sending
- `receive_message()` for polling
- `delete_message()` and `delete_message_batch()` for cleanup
- `change_message_visibility()` for extending processing time
- `get_queue_attributes()` for monitoring

**Message Structure:**
- Complete object breakdown with all possible fields
- Essential fields you'll use most often
- How to work with custom message attributes
- System attributes for metadata and monitoring

**Best Practices:**
- Long polling configuration
- Batch operations for efficiency
- Proper error handling patterns
- FIFO queue specifics

The cheatsheet is designed to be a quick reference you can keep handy while working with SQS in Python!

## Core SQS Functions & Parameters

### 🚀 **send_message()**
Send a single message to the queue
```python
sqs.send_message(
    QueueUrl='string',                    # Required: Queue URL
    MessageBody='string',                 # Required: Message content
    DelaySeconds=123,                     # Optional: 0-900 seconds delay
    MessageAttributes={                   # Optional: Custom attributes
        'AttributeName': {
            'StringValue': 'string',
            'BinaryValue': b'bytes',
            'DataType': 'String'          # String, Number, Binary
        }
    },
    MessageSystemAttributes={             # Optional: System attributes
        'AWSTraceHeader': {
            'StringValue': 'string',
            'DataType': 'String'
        }
    },
    MessageDeduplicationId='string',      # Required for FIFO queues
    MessageGroupId='string'               # Required for FIFO queues
)
```

### 📦 **send_message_batch()**
Send up to 10 messages in a single request
```python
sqs.send_message_batch(
    QueueUrl='string',                    # Required: Queue URL
    Entries=[                            # Required: List of messages (max 10)
        {
            'Id': 'string',              # Required: Unique batch ID
            'MessageBody': 'string',     # Required: Message content
            'DelaySeconds': 123,         # Optional: 0-900 seconds
            'MessageAttributes': {...},   # Optional: Same as send_message
            'MessageDeduplicationId': 'string',  # FIFO only
            'MessageGroupId': 'string'   # FIFO only
        }
    ]
)
```

### 📥 **receive_message()**
Poll for messages from the queue
```python
sqs.receive_message(
    QueueUrl='string',                    # Required: Queue URL
    AttributeNames=[                      # Optional: Message attributes to return
        'All',                           # All attributes
        'ApproximateReceiveCount',       # How many times received
        'ApproximateFirstReceiveTimestamp',
        'SenderId',
        'SentTimestamp'
    ],
    MessageAttributeNames=[               # Optional: Custom attributes to return
        'All',                           # All custom attributes
        'AttributeName'                  # Specific attribute name
    ],
    MaxNumberOfMessages=123,              # Optional: 1-10 messages (default: 1)
    VisibilityTimeoutSeconds=123,         # Optional: 0-43200 seconds (12 hours)
    WaitTimeSeconds=123,                  # Optional: 0-20 seconds (long polling)
    ReceiveRequestAttemptId='string'      # Optional: FIFO deduplication
)
```

### 🗑️ **delete_message()**
Delete a message after processing
```python
sqs.delete_message(
    QueueUrl='string',                    # Required: Queue URL
    ReceiptHandle='string'                # Required: From received message
)
```

### 🗑️📦 **delete_message_batch()**
Delete up to 10 messages in a single request
```python
sqs.delete_message_batch(
    QueueUrl='string',                    # Required: Queue URL
    Entries=[                            # Required: List of messages (max 10)
        {
            'Id': 'string',              # Required: Unique batch ID
            'ReceiptHandle': 'string'    # Required: From received message
        }
    ]
)
```

### 🔄 **change_message_visibility()**
Change visibility timeout for a message
```python
sqs.change_message_visibility(
    QueueUrl='string',                    # Required: Queue URL
    ReceiptHandle='string',               # Required: From received message
    VisibilityTimeoutSeconds=123          # Required: 0-43200 seconds
)
```

### 📊 **get_queue_attributes()**
Get queue configuration and statistics
```python
sqs.get_queue_attributes(
    QueueUrl='string',                    # Required: Queue URL
    AttributeNames=[                      # Optional: Attributes to retrieve
        'All',                           # All attributes
        'ApproximateNumberOfMessages',   # Messages available
        'ApproximateNumberOfMessagesNotVisible',  # In-flight messages
        'VisibilityTimeoutSeconds',      # Default visibility timeout
        'CreatedTimestamp',              # Queue creation time
        'LastModifiedTimestamp',         # Last modification time
        'QueueArn',                      # Queue ARN
        'ApproximateNumberOfMessagesDelayed',  # Delayed messages
        'DelaySeconds',                  # Default delay
        'ReceiveMessageWaitTimeSeconds', # Long polling setting
        'RedrivePolicy',                 # Dead letter queue config
        'MessageRetentionPeriod',        # Message retention (seconds)
        'MaxReceiveCount'                # Max receives before DLQ
    ]
)
```

---

## 📨 Message Object Structure

When you receive messages from SQS, each message has the following structure:

### **Complete Message Object**
```python
{
    'MessageId': 'string',                    # Unique message identifier
    'ReceiptHandle': 'string',                # Required for delete/visibility operations
    'MD5OfBody': 'string',                    # MD5 hash of message body
    'Body': 'string',                         # Actual message content
    'Attributes': {                           # System attributes (if requested)
        'SenderId': 'string',                 # Sender's ID
        'SentTimestamp': 'string',            # When message was sent (epoch ms)
        'ApproximateReceiveCount': 'string',  # How many times received
        'ApproximateFirstReceiveTimestamp': 'string'  # First receive time
    },
    'MD5OfMessageAttributes': 'string',       # MD5 hash of message attributes
    'MessageAttributes': {                    # Custom attributes (if any)
        'AttributeName': {
            'StringValue': 'string',          # String value
            'BinaryValue': b'bytes',          # Binary value
            'StringListValues': ['string'],   # List of strings
            'BinaryListValues': [b'bytes'],   # List of binary values
            'DataType': 'string'              # String, Number, Binary, etc.
        }
    }
}
```

### **Essential Fields for Processing**
```python
# Most commonly used fields
message_id = message['MessageId']           # For logging/tracking
receipt_handle = message['ReceiptHandle']   # REQUIRED for delete/visibility
body = message['Body']                      # Your actual message content

# Parse JSON body if needed
import json
if message['Body'].startswith('{'):
    data = json.loads(message['Body'])
```

### **Working with Message Attributes**
```python
# Check if message has custom attributes
if 'MessageAttributes' in message:
    attributes = message['MessageAttributes']
    
    # Get specific attribute
    if 'Priority' in attributes:
        priority = attributes['Priority']['StringValue']
    
    # Get all attribute names
    attr_names = list(attributes.keys())
    
    # Iterate through all attributes
    for name, attr_data in attributes.items():
        data_type = attr_data['DataType']
        if data_type == 'String':
            value = attr_data['StringValue']
        elif data_type == 'Number':
            value = float(attr_data['StringValue'])
        elif data_type == 'Binary':
            value = attr_data['BinaryValue']
```

### **System Attributes (Metadata)**
```python
if 'Attributes' in message:
    attrs = message['Attributes']
    
    # How many times this message has been received
    receive_count = int(attrs['ApproximateReceiveCount'])
    
    # When message was originally sent (timestamp in milliseconds)
    sent_timestamp = int(attrs['SentTimestamp'])
    sent_datetime = datetime.fromtimestamp(sent_timestamp / 1000)
    
    # First time this message was received
    first_receive = int(attrs['ApproximateFirstReceiveTimestamp'])
    
    # Who sent the message
    sender_id = attrs['SenderId']
```

---

## 💡 Quick Tips

### **Long Polling Best Practice**
```python
# Use long polling to reduce API calls and costs
messages = sqs.receive_message(
    QueueUrl=queue_url,
    WaitTimeSeconds=20,        # Maximum long polling time
    MaxNumberOfMessages=10     # Get up to 10 messages at once
)
```

### **Batch Operations for Efficiency**
```python
# Delete multiple messages efficiently
delete_entries = []
for i, message in enumerate(messages):
    delete_entries.append({
        'Id': str(i),
        'ReceiptHandle': message['ReceiptHandle']
    })

sqs.delete_message_batch(QueueUrl=queue_url, Entries=delete_entries)
```

### **Error Handling Pattern**
```python
try:
    response = sqs.receive_message(QueueUrl=queue_url)
    messages = response.get('Messages', [])
    
    for message in messages:
        # Process message
        process_message(message['Body'])
        
        # Delete only after successful processing
        sqs.delete_message(
            QueueUrl=queue_url,
            ReceiptHandle=message['ReceiptHandle']
        )
        
except ClientError as e:
    print(f"SQS Error: {e.response['Error']['Code']}")
except Exception as e:
    print(f"Processing Error: {e}")
```

### **FIFO Queue Specifics**
```python
# For FIFO queues (.fifo suffix)
sqs.send_message(
    QueueUrl='https://sqs.region.amazonaws.com/account/queue.fifo',
    MessageBody='content',
    MessageGroupId='group1',          # Required: Logical grouping
    MessageDeduplicationId='unique'   # Required: Prevents duplicates
)
```
