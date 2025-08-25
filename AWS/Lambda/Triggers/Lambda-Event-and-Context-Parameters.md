# Lambda Event and Context Parameters
In AWS Lambda, the `event` and `context` parameters are automatically provided by the Lambda runtime when your function is invoked:

## Event Parameter
The `event` parameter contains data about the triggering event. Its structure varies based on what triggers your Lambda:

**API Gateway:**
```python
{
    "httpMethod": "POST",
    "path": "/api/users",
    "headers": {"Authorization": "Bearer token"},
    "body": "{\"name\": \"John\"}",
    "queryStringParameters": {"page": "1"},
    "pathParameters": {"id": "123"}
}
```

**S3 Event:**
```python
{
    "Records": [{
        "eventName": "ObjectCreated:Put",
        "s3": {
            "bucket": {"name": "my-bucket"},
            "object": {"key": "file.pdf"}
        }
    }]
}
```

**CloudWatch Events/EventBridge:**
```python
{
    "source": "aws.ec2",
    "detail-type": "EC2 Instance State-change Notification",
    "detail": {
        "state": "running",
        "instance-id": "i-1234567890abcdef0"
    }
}
```

**Manual Invocation (Test Event):**
```python
{
    "key1": "value1",
    "key2": "value2"
}
```

## Context Parameter
The `context` parameter provides runtime information about the Lambda execution:

```python
def lambda_handler(event, context):
    print(f"Function name: {context.function_name}")
    print(f"Function version: {context.function_version}")
    print(f"Request ID: {context.aws_request_id}")
    print(f"Memory limit: {context.memory_limit_in_mb}")
    print(f"Time remaining: {context.get_remaining_time_in_millis()}")
    print(f"Log group: {context.log_group_name}")
    print(f"Log stream: {context.log_stream_name}")
```

**Common Context Properties:**
- `function_name` - Name of the Lambda function
- `function_version` - Version being executed
- `aws_request_id` - Unique request identifier
- `memory_limit_in_mb` - Memory allocated to function
- `get_remaining_time_in_millis()` - Milliseconds left before timeout
- `log_group_name` - CloudWatch log group
- `log_stream_name` - CloudWatch log stream

## Practical Usage Examples

**Processing API requests:**
```python
def lambda_handler(event, context):
    # Extract data from API Gateway event
    http_method = event['httpMethod']
    body = json.loads(event.get('body', '{}'))
    query_params = event.get('queryStringParameters', {})
    
    if http_method == 'POST':
        # Process POST data
        return process_user_data(body)
```

**Handling S3 events:**
```python
def lambda_handler(event, context):
    # Process each S3 record
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']
        
        # Process the uploaded file
        process_s3_file(bucket, key)
```

**Using context for monitoring:**
```python
def lambda_handler(event, context):
    start_time = time.time()
    
    try:
        # Your processing logic
        result = process_data(event)
        
        # Log execution metrics
        execution_time = time.time() - start_time
        remaining_time = context.get_remaining_time_in_millis() / 1000
        
        print(f"Execution took {execution_time:.2f}s, {remaining_time:.2f}s remaining")
        
        return result
        
    except Exception as e:
        print(f"Error in request {context.aws_request_id}: {str(e)}")
        raise
```

The `event` structure is your main input data, while `context` provides metadata about the execution environment - both are essential for building robust Lambda functions that can handle different triggers and monitor their own performance.
