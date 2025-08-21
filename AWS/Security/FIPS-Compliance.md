# FIPS Compliance

## Examples
I'll show you how to set up a Lambda function and S3 bucket with FIPS endpoints. This involves configuring your AWS SDK to use FIPS endpoints and ensuring proper deployment.The setup I've provided ensures both HTTPS and FIPS compliance for your PDF download workflow. Here are the key points:

## FIPS Compliance Configuration

**1. AWS SDK Configuration**: The critical part is setting `use_fips_endpoint=True` (Python) or `useFipsEndpoint=true` (Node.js) in your AWS SDK configuration. This automatically routes all AWS API calls through FIPS-validated endpoints.

**2. Region Selection**: You must deploy in FIPS-supported regions:
- US Commercial: us-east-1, us-east-2, us-west-1, us-west-2
- US GovCloud: us-gov-east-1, us-gov-west-1  
- Canada: ca-central-1, ca-west-1

**3. Encryption**: Use AWS KMS encryption (`ServerSideEncryption: 'aws:kms'`) which uses FIPS 140-2 validated cryptographic modules.

## HTTPS Compliance

**1. External API Calls**: Use `verify=True` in Python requests or native HTTPS in Node.js to ensure SSL certificate validation.

**2. AWS Communications**: All AWS SDK calls automatically use HTTPS with TLS 1.2+ when using FIPS endpoints.

## Key Benefits of This Setup

- **Automatic FIPS routing**: SDK configuration handles endpoint selection
- **End-to-end encryption**: TLS for external calls, KMS encryption for S3 storage
- **Compliance logging**: CloudTrail tracks all API calls for audit purposes
- **Infrastructure as Code**: Terraform and CloudFormation examples for reproducible deployments

The Lambda function will download PDFs from external APIs over HTTPS, then upload them to S3 using FIPS-compliant endpoints with KMS encryption, ensuring your entire data pipeline meets federal compliance requirements.

# Setting Up Lambda Function and S3 Bucket with FIPS Endpoints

## Prerequisites

- AWS CLI configured with appropriate permissions
- Target one of the supported FIPS regions:
  - **US Commercial**: us-east-1, us-east-2, us-west-1, us-west-2
  - **US GovCloud**: us-gov-east-1, us-gov-west-1
  - **Canada**: ca-central-1, ca-west-1

## 1. Create S3 Bucket with FIPS Configuration

### Using AWS CLI
```bash
# Create S3 bucket in a FIPS-supported region
aws s3api create-bucket \
    --bucket your-fips-compliant-bucket \
    --region us-east-1 \
    --endpoint-url https://s3-fips.us-east-1.amazonaws.com

# Enable versioning (recommended for compliance)
aws s3api put-bucket-versioning \
    --bucket your-fips-compliant-bucket \
    --versioning-configuration Status=Enabled \
    --endpoint-url https://s3-fips.us-east-1.amazonaws.com

# Enable server-side encryption with KMS (FIPS compliant)
aws s3api put-bucket-encryption \
    --bucket your-fips-compliant-bucket \
    --server-side-encryption-configuration '{
        "Rules": [{
            "ApplyServerSideEncryptionByDefault": {
                "SSEAlgorithm": "aws:kms",
                "KMSMasterKeyID": "alias/aws/s3"
            }
        }]
    }' \
    --endpoint-url https://s3-fips.us-east-1.amazonaws.com
```

### Using CloudFormation
```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'FIPS-compliant S3 bucket'

Resources:
  FIPSCompliantBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: your-fips-compliant-bucket
      VersioningConfiguration:
        Status: Enabled
      BucketEncryption:
        ServerSideEncryptionConfiguration:
          - ServerSideEncryptionByDefault:
              SSEAlgorithm: aws:kms
              KMSMasterKeyID: alias/aws/s3
      PublicAccessBlockConfiguration:
        BlockPublicAcls: true
        BlockPublicPolicy: true
        IgnorePublicAcls: true
        RestrictPublicBuckets: true

Outputs:
  BucketName:
    Description: 'FIPS-compliant S3 bucket name'
    Value: !Ref FIPSCompliantBucket
```

## 2. Lambda Function Code with FIPS Endpoints

### Python Example
```python
import json
import boto3
import requests
from botocore.config import Config
import os

def lambda_handler(event, context):
    # Configure AWS clients to use FIPS endpoints
    fips_config = Config(
        region_name=os.environ['AWS_REGION'],
        use_fips_endpoint=True,  # This automatically uses FIPS endpoints
        retries={'max_attempts': 3}
    )
    
    # Create S3 client with FIPS configuration
    s3_client = boto3.client('s3', config=fips_config)
    
    try:
        # Extract PDF URL from event
        pdf_url = event.get('pdf_url')
        bucket_name = os.environ['S3_BUCKET_NAME']
        object_key = event.get('object_key', 'downloaded-file.pdf')
        
        if not pdf_url:
            raise ValueError("PDF URL is required")
        
        # Download PDF from external API using HTTPS
        print(f"Downloading PDF from: {pdf_url}")
        response = requests.get(pdf_url, stream=True, verify=True)  # verify=True ensures SSL cert validation
        response.raise_for_status()
        
        # Verify content type
        content_type = response.headers.get('content-type', '')
        if 'pdf' not in content_type.lower():
            print(f"Warning: Content-Type is {content_type}, expected PDF")
        
        # Upload to S3 using FIPS endpoint
        print(f"Uploading to S3 bucket: {bucket_name}, key: {object_key}")
        s3_client.put_object(
            Bucket=bucket_name,
            Key=object_key,
            Body=response.content,
            ContentType='application/pdf',
            ServerSideEncryption='aws:kms',  # Use KMS encryption (FIPS compliant)
            Metadata={
                'source-url': pdf_url,
                'upload-timestamp': str(context.aws_request_id)
            }
        )
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'PDF successfully downloaded and uploaded',
                'bucket': bucket_name,
                'key': object_key,
                'size': len(response.content)
            })
        }
        
    except requests.exceptions.RequestException as e:
        print(f"Error downloading PDF: {str(e)}")
        return {
            'statusCode': 400,
            'body': json.dumps({'error': f'Failed to download PDF: {str(e)}'})
        }
    
    except Exception as e:
        print(f"Error processing request: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f'Internal error: {str(e)}'})
        }
```

### Node.js Example
```javascript
const AWS = require('aws-sdk');
const https = require('https');

// Configure AWS SDK to use FIPS endpoints
AWS.config.update({
    region: process.env.AWS_REGION,
    useFipsEndpoint: true
});

const s3 = new AWS.S3();

exports.handler = async (event, context) => {
    try {
        const pdfUrl = event.pdf_url;
        const bucketName = process.env.S3_BUCKET_NAME;
        const objectKey = event.object_key || 'downloaded-file.pdf';
        
        if (!pdfUrl) {
            throw new Error('PDF URL is required');
        }
        
        console.log(`Downloading PDF from: ${pdfUrl}`);
        
        // Download PDF using HTTPS
        const pdfBuffer = await downloadPdf(pdfUrl);
        
        // Upload to S3 using FIPS endpoint
        console.log(`Uploading to S3 bucket: ${bucketName}, key: ${objectKey}`);
        
        const uploadParams = {
            Bucket: bucketName,
            Key: objectKey,
            Body: pdfBuffer,
            ContentType: 'application/pdf',
            ServerSideEncryption: 'aws:kms',
            Metadata: {
                'source-url': pdfUrl,
                'upload-timestamp': context.awsRequestId
            }
        };
        
        const result = await s3.upload(uploadParams).promise();
        
        return {
            statusCode: 200,
            body: JSON.stringify({
                message: 'PDF successfully downloaded and uploaded',
                bucket: bucketName,
                key: objectKey,
                location: result.Location
            })
        };
        
    } catch (error) {
        console.error('Error:', error);
        return {
            statusCode: 500,
            body: JSON.stringify({
                error: error.message
            })
        };
    }
};

function downloadPdf(url) {
    return new Promise((resolve, reject) => {
        https.get(url, (response) => {
            if (response.statusCode !== 200) {
                reject(new Error(`HTTP ${response.statusCode}: ${response.statusMessage}`));
                return;
            }
            
            const chunks = [];
            response.on('data', chunk => chunks.push(chunk));
            response.on('end', () => resolve(Buffer.concat(chunks)));
            response.on('error', reject);
        }).on('error', reject);
    });
}
```

## 3. Deploy Lambda Function with FIPS Configuration

### Using AWS CLI
```bash
# Create deployment package
zip -r lambda-function.zip lambda_function.py

# Create IAM role for Lambda
aws iam create-role \
    --role-name FIPSLambdaExecutionRole \
    --assume-role-policy-document '{
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Principal": {"Service": "lambda.amazonaws.com"},
            "Action": "sts:AssumeRole"
        }]
    }'

# Attach basic Lambda execution policy
aws iam attach-role-policy \
    --role-name FIPSLambdaExecutionRole \
    --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

# Create custom policy for S3 access
aws iam put-role-policy \
    --role-name FIPSLambdaExecutionRole \
    --policy-name S3AccessPolicy \
    --policy-document '{
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Action": [
                "s3:PutObject",
                "s3:PutObjectAcl",
                "kms:Encrypt",
                "kms:Decrypt",
                "kms:ReEncrypt*",
                "kms:GenerateDataKey*",
                "kms:DescribeKey"
            ],
            "Resource": [
                "arn:aws:s3:::your-fips-compliant-bucket/*",
                "arn:aws:kms:*:*:key/*"
            ]
        }]
    }'

# Create Lambda function
aws lambda create-function \
    --function-name FIPSPDFDownloader \
    --runtime python3.9 \
    --role arn:aws:iam::ACCOUNT-ID:role/FIPSLambdaExecutionRole \
    --handler lambda_function.lambda_handler \
    --zip-file fileb://lambda-function.zip \
    --environment Variables='{
        "S3_BUCKET_NAME":"your-fips-compliant-bucket"
    }' \
    --region us-east-1 \
    --endpoint-url https://lambda-fips.us-east-1.amazonaws.com
```

### Using Terraform
```hcl
# terraform/main.tf
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
  
  # Use FIPS endpoints
  use_fips_endpoint = true
}

# S3 Bucket
resource "aws_s3_bucket" "fips_compliant_bucket" {
  bucket = "your-fips-compliant-bucket"
}

resource "aws_s3_bucket_versioning" "fips_bucket_versioning" {
  bucket = aws_s3_bucket.fips_compliant_bucket.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "fips_bucket_encryption" {
  bucket = aws_s3_bucket.fips_compliant_bucket.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = "alias/aws/s3"
    }
  }
}

# IAM Role for Lambda
resource "aws_iam_role" "lambda_execution_role" {
  name = "FIPSLambdaExecutionRole"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_basic_execution" {
  role       = aws_iam_role.lambda_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy" "lambda_s3_policy" {
  name = "S3AccessPolicy"
  role = aws_iam_role.lambda_execution_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = [
        "s3:PutObject",
        "s3:PutObjectAcl",
        "kms:Encrypt",
        "kms:Decrypt",
        "kms:ReEncrypt*",
        "kms:GenerateDataKey*",
        "kms:DescribeKey"
      ]
      Resource = [
        "${aws_s3_bucket.fips_compliant_bucket.arn}/*",
        "arn:aws:kms:*:*:key/*"
      ]
    }]
  })
}

# Lambda Function
resource "aws_lambda_function" "fips_pdf_downloader" {
  filename         = "lambda-function.zip"
  function_name    = "FIPSPDFDownloader"
  role            = aws_iam_role.lambda_execution_role.arn
  handler         = "lambda_function.lambda_handler"
  runtime         = "python3.9"
  timeout         = 60

  environment {
    variables = {
      S3_BUCKET_NAME = aws_s3_bucket.fips_compliant_bucket.bucket
    }
  }
}
```

## 4. Test the Setup

### Test Event
```json
{
  "pdf_url": "https://example.com/sample.pdf",
  "object_key": "documents/sample-downloaded.pdf"
}
```

### Test using AWS CLI
```bash
# Invoke the Lambda function
aws lambda invoke \
    --function-name FIPSPDFDownloader \
    --payload '{"pdf_url": "https://example.com/sample.pdf", "object_key": "test-file.pdf"}' \
    --region us-east-1 \
    --endpoint-url https://lambda-fips.us-east-1.amazonaws.com \
    response.json

# Check the response
cat response.json
```

## 5. Verify FIPS Compliance

### Check Lambda Configuration
```bash
# Verify Lambda function uses FIPS endpoint
aws lambda get-function \
    --function-name FIPSPDFDownloader \
    --region us-east-1 \
    --endpoint-url https://lambda-fips.us-east-1.amazonaws.com
```

### Check S3 Configuration
```bash
# Verify S3 bucket encryption
aws s3api get-bucket-encryption \
    --bucket your-fips-compliant-bucket \
    --endpoint-url https://s3-fips.us-east-1.amazonaws.com
```

### Monitor CloudTrail for FIPS Endpoint Usage
```bash
# Check CloudTrail logs to verify FIPS endpoints are being used
aws logs filter-log-events \
    --log-group-name /aws/lambda/FIPSPDFDownloader \
    --start-time $(date -d '1 hour ago' +%s)000
```

## Important Notes

1. **Region Requirements**: FIPS endpoints are only available in US East/West, GovCloud, and Canada regions
2. **SDK Configuration**: Always set `use_fips_endpoint=True` or `useFipsEndpoint=true` in your AWS SDK configuration
3. **KMS Encryption**: Use AWS KMS for encryption as it's FIPS 140-2 validated
4. **SSL/TLS**: All external API calls should use HTTPS with certificate verification
5. **Monitoring**: Use CloudTrail and CloudWatch to monitor and verify FIPS endpoint usage

## Troubleshooting

- **Error: FIPS endpoint not found**: Ensure you're deploying in a FIPS-supported region
- **SSL Certificate issues**: Verify external APIs use valid SSL certificates
- **Access denied**: Check IAM permissions for KMS and S3 access
- **Timeout errors**: Increase Lambda timeout for large PDF downloads
