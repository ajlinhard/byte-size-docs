# Serverless Application Model Command Line Interface (SAM CLI)
SAM CLI creates a local development environment that simulates AWS services on your machine. Here's how it works:

## **What SAM CLI Runs Locally**

### **Lambda Functions**
- Runs your Lambda code in Docker containers
- Simulates the Lambda runtime environment
- Supports all Lambda runtimes (Python, Node.js, Java, Go, etc.)

### **API Gateway**
- Creates a local HTTP server that mimics API Gateway
- Handles routing, request/response transformations
- Supports REST and HTTP APIs

### **DynamoDB Local**
- Runs Amazon's official DynamoDB Local
- Full DynamoDB functionality on your machine
- Separate from AWS - completely offline

## **Local Testing Examples**

### **1. Testing Lambda Functions Directly**
```bash
# Invoke a specific Lambda function
sam local invoke "HelloWorldFunction"

# Invoke with custom event data
sam local invoke "HelloWorldFunction" -e events/event.json

# Generate sample events
sam local generate-event s3 put > s3-event.json
sam local invoke "S3Handler" -e s3-event.json
```

### **2. Running Local API Gateway**
```bash
# Start local API server (usually on http://127.0.0.1:3000)
sam local start-api

# Now you can make HTTP requests:
curl http://127.0.0.1:3000/hello
curl -X POST http://127.0.0.1:3000/users -d '{"name": "John"}'
```

### **3. Running Local DynamoDB**
```bash
# Start DynamoDB Local (usually on port 8000)
sam local start-lambda --docker-network sam-local

# In another terminal, you can interact with local DynamoDB:
aws dynamodb list-tables --endpoint-url http://localhost:8000
aws dynamodb put-item --endpoint-url http://localhost:8000 \
  --table-name Users \
  --item '{"id": {"S": "123"}, "name": {"S": "John"}}'
```

## **Complete Local Development Example**

Here's a practical example showing how you can test everything locally:

**SAM Template (template.yaml)**:
```yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31

Resources:
  UsersTable:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: Users
      AttributeDefinitions:
        - AttributeName: id
          AttributeType: S
      KeySchema:
        - AttributeName: id
          KeyType: HASH
      BillingMode: PAY_PER_REQUEST

  GetUserFunction:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: src/
      Handler: app.get_user
      Runtime: python3.9
      Environment:
        Variables:
          USERS_TABLE: !Ref UsersTable
      Events:
        GetUser:
          Type: Api
          Properties:
            Path: /users/{id}
            Method: get
```

**Lambda Function (src/app.py)**:
```python
import json
import boto3
import os

def get_user(event, context):
    # This will connect to local DynamoDB when running locally
    dynamodb = boto3.resource('dynamodb', 
                             endpoint_url='http://host.docker.internal:8000' if os.environ.get('AWS_SAM_LOCAL') else None)
    
    table = dynamodb.Table(os.environ['USERS_TABLE'])
    user_id = event['pathParameters']['id']
    
    response = table.get_item(Key={'id': user_id})
    
    return {
        'statusCode': 200,
        'body': json.dumps(response.get('Item', {}))
    }
```

## **Local Testing Workflow**

### **Step 1: Start Local Services**
```bash
# Terminal 1: Start DynamoDB Local
sam local start-lambda --docker-network sam-local

# Terminal 2: Start API Gateway
sam local start-api --docker-network sam-local
```

### **Step 2: Create Local DynamoDB Table**
```bash
# Create the table locally
aws dynamodb create-table \
  --endpoint-url http://localhost:8000 \
  --table-name Users \
  --attribute-definitions AttributeName=id,AttributeType=S \
  --key-schema AttributeName=id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST
```

### **Step 3: Add Test Data**
```bash
# Insert test data
aws dynamodb put-item \
  --endpoint-url http://localhost:8000 \
  --table-name Users \
  --item '{"id": {"S": "123"}, "name": {"S": "John Doe"}, "email": {"S": "john@example.com"}}'
```

### **Step 4: Test Your API**
```bash
# Test the API endpoint
curl http://127.0.0.1:3000/users/123

# Response:
# {"id": "123", "name": "John Doe", "email": "john@example.com"}
```

## **Advanced Local Testing Features**

### **Environment Variables**
```bash
# Use local environment file
sam local start-api --env-vars env.json

# env.json
{
  "GetUserFunction": {
    "USERS_TABLE": "Users",
    "DEBUG": "true"
  }
}
```

### **Debugging**
```bash
# Debug Lambda function
sam local invoke -d 5858 "GetUserFunction"

# Then attach your IDE debugger to port 5858
```

### **Step Functions Local**
```bash
# Test Step Functions locally (requires additional setup)
sam local start-lambda
# Then use Step Functions Local to orchestrate
```

## **What's NOT Available Locally**

Some AWS services don't have local equivalents:
- **S3** (but you can use LocalStack or minio)
- **SQS/SNS** (LocalStack provides these)
- **CloudWatch** (logs go to console)
- **IAM** (permissions are simulated)

## **Benefits of Local Development**

1. **Fast iteration** - No deployment delays
2. **Cost savings** - No AWS charges during development
3. **Offline development** - Work without internet
4. **Easy debugging** - Full debugging capabilities
5. **Team consistency** - Same environment for all developers

## **Real-World Development Flow**

```bash
# 1. Initialize project
sam init

# 2. Develop locally
sam local start-api

# 3. Test locally
curl http://localhost:3000/api/endpoint

# 4. Build for deployment
sam build

# 5. Deploy to AWS
sam deploy
```

 SAM CLI creates a genuine local development environment where you can fully test your serverless applications before deploying to AWS!
