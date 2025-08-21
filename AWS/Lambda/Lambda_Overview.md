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
