# AWS Lambda Overview
AWS is a handy service for setting up simple task you need triggered when X occurs. 

** Quick Note **
- You can choose the language and runtime
- You can choose from or build the trigger
- The run is usually less than 15 minutes
- The system auto scales for all lambda functions being triggered.

## Documentation/Tutorials
1. [AWS Lambda Documentation](https://aws.amazon.com/pm/lambda/)
2. [Youtube - Lambda Overview](https://www.youtube.com/watch?v=UsaiOEFdfs0)
   <br>a. [Full Udemy Lambda Course](https://www.udemy.com/course/aws-lambda-a-practical-guide/?referralCode=F6D1A50467E579C65372&couponCode=ST16MT230625G1) 
3. [Youtube - Your First Lambda Function](https://www.youtube.com/watch?v=e1tkFsFOBHA)


## Use Cases:
There are an uncountable number of things you can do with lambda functions. Here is a short list:

1. Start a process or load a file when it arrives in an S3 bucket.
2. Kick-off an Airflow DAG based on the state of an AWS service.
3. Send Emails when a file arrives or a resource queue is overloaded.

I'll research the HTTPS and FIPS compliance aspects of pulling PDFs from APIs to S3 buckets via Lambda. This involves several AWS services and security standards, so let me gather comprehensive information.Based on my research, I can confirm that pulling a PDF from an API to an S3 bucket via Lambda is **both HTTPS and FIPS compliant** when properly configured. Here's the detailed explanation with sources:

## AWS Managed Service Network
When you **don't assign a Lambda function to a VPC**, it runs in AWS's **managed service network**.

**Where Lambda lives:**
- AWS's own internal, managed infrastructure
- Not in your VPC at all
- AWS handles all the networking behind the scenes

**Key characteristics:**
- **Has internet access by default** - can call external APIs, download packages, etc.
- **Gets a dynamic public IP** - changes with each execution
- **No VPC networking costs** - no NAT Gateway fees
- **Faster cold starts** - no ENI (Elastic Network Interface) setup time
- **Can access AWS services** - S3, DynamoDB, SES, etc. through AWS's backbone

## What It Can Access

✅ **Can reach:**
- External APIs and websites
- AWS services (S3, DynamoDB, SQS, etc.)
- Any publicly accessible endpoints

❌ **Cannot reach:**
- Resources inside your VPC (private RDS, EC2 instances, etc.)
- Private subnets
- On-premises resources connected via VPN/Direct Connect

## When to Use Each Approach

**No VPC (AWS managed):**
- Simple functions that only need internet access
- Calling external APIs
- Processing S3 events, SQS messages
- Most common use case

**VPC-attached:**
- Need to access private resources (RDS in private subnet)
- Need static IP addresses (through NAT Gateway)
- Security requirements to isolate from internet
- Access on-premises resources

So by default, Lambda functions live in AWS's managed network with built-in internet access - no NAT Gateway needed!

## Lambda Security Model

**Lambda functions are not web servers** - they don't have public endpoints by default. Even though they can reach the internet, the internet cannot reach them.
**Therefore, no external people cannot directly access your Lambda function** even when it runs in AWS's managed network. Here's why:

## How to Make Lambda Accessible

To allow external access, you need to explicitly create an entry point:

**1. API Gateway**
```
Internet → API Gateway → Lambda Function
```
- Most common approach
- Creates REST/HTTP APIs
- Handles authentication, rate limiting, etc.

**2. Function URLs**
```
Internet → Function URL → Lambda Function  
```
- Direct HTTPS endpoint for your Lambda
- Simpler than API Gateway but fewer features

**3. Application Load Balancer**
```
Internet → ALB → Lambda Function
```
- Can route HTTP requests to Lambda as a target

**4. Other AWS Services**
- CloudFront (CDN)
- AWS AppSync (GraphQL)

## Key Point

**Lambda's internet access ≠ Internet access to Lambda**

- Lambda can make outbound calls (to APIs, databases, etc.)
- But inbound access requires you to explicitly configure a trigger/endpoint

## Security Benefits

This design is actually a security feature:
- Functions are private by default
- You control exactly how they can be invoked
- No risk of accidental exposure
- You can add authentication, authorization, rate limiting at the gateway level

So your Lambda function can call external APIs safely without being directly accessible from the internet unless you specifically set up an entry point.

---
## HTTPS Compliance

**AWS Lambda uses HTTPS-only endpoints by default:**

Lambda API endpoints only support secure connections over HTTPS, and when you manage Lambda resources with the AWS Management Console, AWS SDK, or the Lambda API, all communication is encrypted with Transport Layer Security (TLS).

As of February 27, 2024, AWS has completed global updates requiring a minimum of TLS 1.2 for all AWS service API endpoints. This means all Lambda communications are automatically encrypted in transit using modern TLS standards.

**API calls from Lambda are HTTPS:**
When Lambda makes API calls to external services to pull PDFs, these calls use HTTPS protocols with TLS encryption, ensuring data is encrypted during transmission from the external API to your Lambda function.

## FIPS Compliance

**AWS Lambda FIPS endpoints are available:**

AWS Lambda offers FIPS endpoints: lambda-fips.us-east-1.amazonaws.com, lambda-fips.us-east-2.amazonaws.com, lambda-fips.us-west-1.amazonaws.com, lambda-fips.us-west-2.amazonaws.com for US East/West regions, and lambda-fips.us-gov-east-1.amazonaws.com, lambda-fips.us-gov-west-1.amazonaws.com for GovCloud regions.

## Implementation Requirements

To ensure FIPS compliance for your PDF download workflow:

1. **Configure Lambda to use FIPS endpoints** by setting the AWS SDK to use FIPS endpoints when making AWS API calls
2. **Use S3 FIPS endpoints** for uploading the PDF files
3. **Deploy in supported regions** - FIPS endpoints are available in US East/West, GovCloud, and Canada Central/West regions

**Sources:**
- [AWS Lambda Data Protection Documentation](https://docs.aws.amazon.com/lambda/latest/dg/security-dataprotection.html)
- [AWS TLS 1.2 Requirements](https://aws.amazon.com/blogs/security/tls-1-2-required-for-aws-endpoints/)
