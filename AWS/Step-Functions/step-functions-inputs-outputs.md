AWS Step Functions Parameters & Context
A comprehensive guide to passing parameters in and out of Step Functions with examples for Lambda, DynamoDB, RDS, Kinesis, and more
1. Overview: Context vs Parameters
Step Functions executions have two ways data flows through the system:
Context
Automatically provided by Step Functions for every task. Contains execution metadata like the execution ID, state machine ARN, task token, etc.
Input/Output
Data explicitly passed through the state machine as parameters. This is the actual payload your workflow processes.


2. The Context Object
The context object is automatically available and contains metadata about the execution. Access it using $$.State.EntryPoint or in your Lambda code through the context parameter.
Available Context Fields:
{  "Execution": {    "Id": "arn:aws:states:us-east-1:123456789012:execution:MyStateMachine:uuid",    "RoleArn": "arn:aws:iam::123456789012:role/StepFunctionsRole",    "Name": "MyExecutionName",    "StartTime": "2024-01-15T10:30:45Z"  },  "StateMachine": {    "Id": "arn:aws:states:us-east-1:123456789012:stateMachine:MyStateMachine",    "Name": "MyStateMachine"  },  "State": {    "EntryPoint": true,    "Name": "MyState",    "RetryCount": 0,    "CatchCount": 0  },  "Task": {    "Token": "AAAAKgEVEMLFQH4A..."  }}

Example: Using Context in a State Definition
{  "MyState": {    "Type": "Task",    "Resource": "arn:aws:lambda:us-east-1:123456789012:function:MyFunction",    "Parameters": {      "executionId.$": "$$.Execution.Id",      "stateMachineName.$": "$$.StateMachine.Name",      "retryCount.$": "$$.State.RetryCount",      "payload.$": "$"    },    "End": true  }}
Explanation: The $$ symbol accesses context. The .$ suffix means JSONPath - it extracts values from the context object. Without the suffix, it's treated as a literal string.
3. Parameters: Static vs Dynamic
3a. Static Parameters
Fixed values that don't change based on input. Used for configuration.
{  "MyTask": {    "Type": "Task",    "Resource": "arn:aws:lambda:us-east-1:123456789012:function:MyFunction",    "Parameters": {      "environment": "production",      "timeout": 300,      "retryPolicy": "exponential",      "payload.$": "$"    },    "End": true  }}
Explanation: Values without the .$ suffix (environment, timeout, retryPolicy) are static literals. The payload.$ uses JSONPath to pass the entire input object.
3b. Dynamic Parameters (JSONPath)
Use JSONPath expressions (marked with .$) to extract values from input or context.
{  "MyTask": {    "Type": "Task",    "Resource": "arn:aws:lambda:us-east-1:123456789012:function:MyFunction",    "Parameters": {      "userId.$": "$.user.id",      "firstName.$": "$.user.firstName",      "orders.$": "$.user.orders[*].orderId",      "timestamp.$": "$$.State.EntryPoint",      "payload.$": "$"    },    "End": true  }}
Explanation: The .$ suffix enables JSONPath. $ represents entire input. $.user.id extracts the 'id' from a 'user' object. $.user.orders[*].orderId extracts all order IDs.
4. Receiving Parameters in Python Lambda
When Step Functions calls your Lambda, parameters are passed as the event object.
import jsonimport boto3def lambda_handler(event, context):    """    event: Dict with parameters from Step Functions    context: Lambda context object    """        # Extract static parameter    environment = event.get('environment', 'development')        # Extract dynamic parameters    user_id = event['user']['id']    first_name = event['user'].get('firstName', 'Unknown')        # Access Lambda context    print(f"RequestId: {context.request_id}")        # Return output - becomes next step input    return {        "statusCode": 200,        "userId": user_id,        "message": f"Processed for {first_name}"    }
Explanation: The event parameter contains everything from your Parameters block. The context gives Lambda metadata. Your return value becomes the output of this task.
5. Input/Output Processing: ResultPath & OutputPath
5a. ResultPath: What to do with task result
{  "PassResultAsOutput": {    "Type": "Task",    "Resource": "arn:aws:lambda:us-east-1:123456789012:function:MyFunction",    "ResultPath": "$",    "End": true  },  "AddResultToInput": {    "Type": "Task",    "Resource": "arn:aws:lambda:us-east-1:123456789012:function:MyFunction",    "ResultPath": "$.lambdaResult",    "Next": "NextState"  },  "DiscardResult": {    "Type": "Task",    "Resource": "arn:aws:lambda:us-east-1:123456789012:function:MyFunction",    "ResultPath": null,    "End": true  }}
Explanation: $ replaces entire input with output. $.path adds output to that location while preserving other fields. null discards output and passes original input. Default is $.
5b. OutputPath: Filter what passes to next step
{  "OnlySpecificFields": {    "Type": "Task",    "Resource": "arn:aws:lambda:us-east-1:123456789012:function:MyFunction",    "ResultPath": "$.result",    "OutputPath": "$.result.data",    "End": true  }}
Explanation: OutputPath filters output after ResultPath. Default is $ (pass everything). This prevents information bloat in complex workflows.
6. Service Integration Examples
6a. Lambda - Basic Call
{  "ProcessOrder": {    "Type": "Task",    "Resource": "arn:aws:lambda:us-east-1:123456789012:function:ProcessOrder",    "Parameters": {      "orderId.$": "$.order.id",      "customerId.$": "$.customer.id",      "items.$": "$.order.items"    },    "ResultPath": "$.processedOrder",    "End": true  }}
def lambda_handler(event, context):    order_id = event['orderId']    customer_id = event['customerId']    items = event['items']        total = sum(i['price'] * i['quantity'] for i in items)        return {        "orderId": order_id,        "totalPrice": total,        "itemCount": len(items)    }
Input: {"order": {"id": "ORD-123", "items": [{"price": 10, "quantity": 2}]}, "customer": {"id": "CUST-456"}}Output adds to input via ResultPath creating: {...original..., "processedOrder": {"orderId": "ORD-123", "totalPrice": 20}}
6b. DynamoDB - PutItem
{  "SaveToDatabase": {    "Type": "Task",    "Resource": "arn:aws:states:::dynamodb:putItem",    "Parameters": {      "TableName": "UserProfiles",      "Item": {        "userId": {"S.$": "$.user.id"},        "email": {"S.$": "$.user.email"},        "createdAt": {"S.$": "$.timestamp"}      }    },    "ResultPath": "$.dbResponse",    "End": true  }}
Explanation: DynamoDB calls use type annotations (S=String, N=Number, M=Map). ResultPath stores the DynamoDB response. Always include proper error handling for database calls.
6c. DynamoDB - GetItem
{  "FetchUserProfile": {    "Type": "Task",    "Resource": "arn:aws:states:::dynamodb:getItem",    "Parameters": {      "TableName": "UserProfiles",      "Key": {        "userId": {"S.$": "$.userId"}      }    },    "ResultPath": "$.userProfile",    "Next": "ProcessProfile"  }}
Explanation: GetItem returns results in DynamoDB format with type annotations. Use a Lambda to convert to clean JSON for subsequent steps.
6d. RDS (PostgreSQL) via Lambda
{  "QueryDatabase": {    "Type": "Task",    "Resource": "arn:aws:lambda:us-east-1:123456789012:function:QueryRDS",    "Parameters": {      "query": "SELECT * FROM users WHERE user_id = :userId",      "userId.$": "$.userId",      "database": "production"    },    "ResultPath": "$.queryResult",    "Retry": [      {        "ErrorEquals": ["States.TaskFailed"],        "IntervalSeconds": 3,        "MaxAttempts": 2,        "BackoffRate": 1.5      }    ],    "End": true  }}
import boto3rds = boto3.client('rds-data')def lambda_handler(event, context):    try:        response = rds.execute_statement(            resourceArn='arn:aws:rds:us-east-1:123456789012:cluster:my-cluster',            secretArn='arn:aws:secretsmanager:us-east-1:123456789012:secret:db-creds',            database=event['database'],            sql=event['query'],            parameters=[                {'name': 'userId', 'value': {'stringValue': event['userId']}}            ]        )                records = []        for record in response.get('records', []):            records.append({                'userId': record[0]['stringValue'],                'email': record[1]['stringValue']            })                return {"status": "success", "records": records}    except Exception as e:        raise Exception(f"Query failed: {str(e)}")
Explanation: RDS Data API uses parameterized queries for security. The Lambda converts DynamoDB-format responses to clean JSON. Always add Retry policies for database operations.
6e. Kinesis - PutRecord
{  "PublishToKinesis": {    "Type": "Task",    "Resource": "arn:aws:states:::aws-sdk:kinesis:putRecord",    "Parameters": {      "StreamName": "user-events",      "PartitionKey.$": "$.userId",      "Data.$": "States.JsonToString({        'userId.$': '$.userId',        'eventType': 'order_created',        'orderId.$': '$.orderId'      })"    },    "ResultPath": "$.kinesisResponse",    "End": true  }}
Explanation: PartitionKey determines shard routing. Use consistent keys to preserve ordering. States.JsonToString() converts objects to strings for the Data field.
6f. Kinesis - Consumer Lambda
import jsonimport base64def lambda_handler(event, context):    """Triggered by Kinesis stream"""    results = []        for record in event['Records']:        # Decode base64 data        payload = base64.b64decode(            record['kinesis']['data']        ).decode('utf-8')        event_data = json.loads(payload)                # Process        results.append({            'userId': event_data['userId'],            'processed': True        })        return {'count': len(results), 'results': results}
Explanation: Kinesis delivers base64-encoded records. Always decode before parsing. Multiple records can arrive in one invocation.
6g. SNS - Publish Message
{  "NotifyAdmins": {    "Type": "Task",    "Resource": "arn:aws:states:::sns:publish",    "Parameters": {      "TopicArn": "arn:aws:sns:us-east-1:123456789012:admin-alerts",      "Subject": "Order Alert",      "Message.$": "States.Format('Order {id} for {customer}', $.orderId, $.customer.name)"    },    "ResultPath": null,    "End": true  }}
Explanation: SNS publishes to topics. States.Format() provides string interpolation. ResultPath: null discards response, passing original input forward.
6h. S3 - PutObject
{  "SaveReport": {    "Type": "Task",    "Resource": "arn:aws:states:::aws-sdk:s3:putObject",    "Parameters": {      "Bucket": "my-reports",      "Key.$": "States.Format('reports/{date}/{id}.json', $.date, $.reportId)",      "Body.$": "States.JsonToString($.reportData)",      "ContentType": "application/json"    },    "ResultPath": "$.s3Upload",    "End": true  }}
Explanation: S3:putObject saves files. Key supports dynamic paths via States.Format(). Body must be a string, so use States.JsonToString() for objects.
6i. SQS - SendMessage
{  "QueueTask": {    "Type": "Task",    "Resource": "arn:aws:states:::sqs:sendMessage",    "Parameters": {      "QueueUrl": "https://sqs.us-east-1.amazonaws.com/123456789012/tasks",      "MessageBody.$": "States.JsonToString({        'taskId.$': '$.taskId',        'priority.$': '$.priority'      })",      "MessageAttributes": {        "Priority": {          "StringValue.$": "$.priority",          "DataType": "String"        }      }    },    "ResultPath": "$.sqsResponse",    "End": true  }}
Explanation: SQS:sendMessage queues async work. MessageBody must be string. MessageAttributes add metadata for filtering or routing.
7. JSONPath Quick Reference
$                          # Entire input$.field                    # Root level field$.user.name                # Nested access$.items[0]                 # First array element$.items[*]                 # All elements$.items[*].id              # Extract id from each$.items[0:2]               # Slice (first 2)$[?(@.status=='pending')]  # Filter by status$$.Execution.Id            # Context: execution ID$$.State.Name              # Context: state name$$.State.RetryCount        # Context: retry count$$.Task.Token              # Context: task token

8. Best Practices
✓ Manage state growth with ResultPath
Use ResultPath: null to discard outputs or ResultPath: "$.field" to place in specific locations. Prevents bloated state.
✓ Extract specific fields in Parameters
Instead of passing entire $ object, extract what's needed. Documents data flow and reduces security risks.
✓ Use context for runtime values
Use $$.Execution.Id for tracing, $$.State.RetryCount for retry logic. Context is auto-populated.
✓ Convert service response formats in Lambda
Direct integrations return native formats (DynamoDB type annotations). Use Lambda to convert to clean JSON.
✓ Always add Retry and Catch policies
Add Retry for transient failures (throttling, timeouts). Use Catch for expected errors.
✓ Validate input early
Add validation step at workflow start. Use Choice states to fail fast before expensive operations.
✓ Use States.Format() for strings
More readable than concatenation: States.Format('{name} has {count} items', $.name, $.count)
9. Common Issues & Debugging
Path does not exist in the JSONPath expression
Cause: JSONPath references missing field. Solution: Use .get() in Python for safe access.
ValidationException in DynamoDB calls
Cause: Incorrect type annotations or null values. Solution: Verify all values have types (S, N, M, L, etc.).
Lambda receives unexpected parameter format
Cause: Parameter structure mismatch. Solution: Add logging: print(json.dumps(event, indent=2)). Verify JSONPath extraction.
State output missing expected data
Cause: OutputPath or ResultPath filtering removed data. Solution: Use OutputPath: "$" to pass everything if unsure.
10. Parameter Syntax Reference
Syntax
Meaning
Example
"field": value
Static/literal value
"timeout": 300
"field.$": "$.path"
Extract from input via JSONPath
"userId.$": "$.user.id"
"field.$": "$$.Context.path"
Extract from context
"execId.$": "$$.Execution.Id"
ResultPath: "$.path"
Place output in path of input
ResultPath: "$.result"
ResultPath: "$"
Replace entire input with output
Default behavior
ResultPath: null
Discard output, pass input forward
For side-effect tasks


End of Cheatsheet
