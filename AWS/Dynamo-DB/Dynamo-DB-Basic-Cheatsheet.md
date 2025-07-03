# Dynamo-DB Basic Cheatsheet
You can interact with DynamoDB using both SQL-like syntax and Python. Here are examples of each:

## SQL with DynamoDB (PartiQL)

DynamoDB supports PartiQL, a SQL-compatible query language. You can use it through the AWS Console, CLI, or SDKs.

**Basic SELECT Operations**
```sql
-- Get all items from a table
SELECT * FROM Users

-- Get specific attributes
SELECT Name, Email FROM Users WHERE UserID = 'user123'

-- Query with conditions
SELECT * FROM Users WHERE Age > 25 AND Status = 'active'

-- Query with BETWEEN
SELECT * FROM Orders WHERE OrderDate BETWEEN '2024-01-01' AND '2024-12-31'
```

**INSERT Operations**
```sql
-- Insert a new item
INSERT INTO Users VALUE {
    'UserID': 'user456',
    'Name': 'Jane Smith',
    'Email': 'jane@example.com',
    'Age': 28
}
```

**UPDATE Operations**
```sql
-- Update specific fields
UPDATE Users 
SET Age = 29, Status = 'premium' 
WHERE UserID = 'user456'

-- Increment a counter
UPDATE Products 
SET ViewCount = ViewCount + 1 
WHERE ProductID = 'prod123'
```

**DELETE Operations**
```sql
-- Delete an item
DELETE FROM Users WHERE UserID = 'user456'
```

## Python with Boto3

The primary way to interact with DynamoDB from Python is using the AWS SDK (boto3).

**Setup and Connection**
```python
import boto3
from boto3.dynamodb.conditions import Key, Attr

# Create DynamoDB resource
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('Users')

# Or use client for lower-level access
client = boto3.client('dynamodb', region_name='us-east-1')
```

**Insert Operations**
```python
# Put a single item
response = table.put_item(
    Item={
        'UserID': 'user123',
        'Name': 'John Doe',
        'Email': 'john@example.com',
        'Age': 30,
        'Skills': ['Python', 'AWS', 'SQL']
    }
)

# Conditional put (only if item doesn't exist)
table.put_item(
    Item={
        'UserID': 'user456',
        'Name': 'Jane Smith'
    },
    ConditionExpression='attribute_not_exists(UserID)'
)

# Batch insert
with table.batch_writer() as batch:
    for i in range(100):
        batch.put_item(
            Item={
                'UserID': f'user{i}',
                'Name': f'User {i}',
                'Age': 20 + (i % 40)
            }
        )
```

**Query Operations**
```python
# Query by partition key
response = table.query(
    KeyConditionExpression=Key('UserID').eq('user123')
)
items = response['Items']

# Query with sort key conditions (composite key table)
response = table.query(
    KeyConditionExpression=Key('UserID').eq('user123') & 
                          Key('Timestamp').between('2024-01-01', '2024-12-31')
)

# Query with filters
response = table.query(
    KeyConditionExpression=Key('UserID').eq('user123'),
    FilterExpression=Attr('Age').gt(25) & Attr('Status').eq('active')
)

# Query using GSI
response = table.query(
    IndexName='Email-index',
    KeyConditionExpression=Key('Email').eq('john@example.com')
)
```

**Scan Operations**
```python
# Scan entire table
response = table.scan()
items = response['Items']

# Scan with filter
response = table.scan(
    FilterExpression=Attr('Age').between(25, 35)
)

# Paginated scan
scan_kwargs = {
    'FilterExpression': Attr('Age').gt(25)
}

done = False
start_key = None

while not done:
    if start_key:
        scan_kwargs['ExclusiveStartKey'] = start_key
    
    response = table.scan(**scan_kwargs)
    items = response.get('Items', [])
    
    # Process items
    for item in items:
        print(item)
    
    start_key = response.get('LastEvaluatedKey', None)
    done = start_key is None
```

**Update Operations**
```python
# Update specific attributes
table.update_item(
    Key={'UserID': 'user123'},
    UpdateExpression='SET Age = :age, #status = :status',
    ExpressionAttributeValues={
        ':age': 31,
        ':status': 'premium'
    },
    ExpressionAttributeNames={
        '#status': 'Status'  # 'Status' is a reserved word
    }
)

# Atomic counter increment
table.update_item(
    Key={'UserID': 'user123'},
    UpdateExpression='ADD ViewCount :inc',
    ExpressionAttributeValues={':inc': 1}
)

# Add to a list
table.update_item(
    Key={'UserID': 'user123'},
    UpdateExpression='SET Skills = list_append(Skills, :skill)',
    ExpressionAttributeValues={':skill': ['JavaScript']}
)

# Conditional update
table.update_item(
    Key={'UserID': 'user123'},
    UpdateExpression='SET Age = :age',
    ConditionExpression='Age < :max_age',
    ExpressionAttributeValues={
        ':age': 32,
        ':max_age': 65
    }
)
```

**Delete Operations**
```python
# Delete an item
table.delete_item(
    Key={'UserID': 'user123'}
)

# Conditional delete
table.delete_item(
    Key={'UserID': 'user123'},
    ConditionExpression='attribute_exists(UserID)'
)

# Batch delete
with table.batch_writer() as batch:
    for user_id in ['user1', 'user2', 'user3']:
        batch.delete_item(Key={'UserID': user_id})
```

**Transaction Operations**
```python
# Transaction write
dynamodb.meta.client.transact_write_items(
    TransactItems=[
        {
            'Put': {
                'TableName': 'Orders',
                'Item': {
                    'OrderID': {'S': 'order123'},
                    'Amount': {'N': '100'}
                }
            }
        },
        {
            'Update': {
                'TableName': 'Inventory',
                'Key': {'ProductID': {'S': 'prod123'}},
                'UpdateExpression': 'ADD Quantity :dec',
                'ExpressionAttributeValues': {':dec': {'N': '-1'}}
            }
        }
    ]
)
```

**Using PartiQL in Python**
```python
# Execute PartiQL statements
response = client.execute_statement(
    Statement="SELECT * FROM Users WHERE Age > ?",
    Parameters=[{'N': '25'}]
)

# PartiQL insert
client.execute_statement(
    Statement="INSERT INTO Users VALUE {'UserID': ?, 'Name': ?}",
    Parameters=[{'S': 'user789'}, {'S': 'Bob Wilson'}]
)
```

**Error Handling**
```python
from botocore.exceptions import ClientError

try:
    table.put_item(
        Item={'UserID': 'user123', 'Name': 'John'},
        ConditionExpression='attribute_not_exists(UserID)'
    )
except ClientError as e:
    if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
        print("Item already exists")
    else:
        print(f"Error: {e.response['Error']['Message']}")
```

## Key Differences

**PartiQL Limitations:**
- Limited JOIN support (only within single items)
- No complex aggregations
- Still requires understanding of DynamoDB's partition/sort key model

**Python Advantages:**
- Full programmatic control
- Better error handling
- Batch operations
- Integration with application logic
- Type conversion handled automatically

Both approaches are valid, with Python/boto3 being more common for production applications due to its flexibility and comprehensive feature support.
