# AWS Lambda Overview
AWS is a handy service for setting up simple task you need triggered when X occurs. 

** Quick Note **
- You can choose the language and runtime
- You can choose from or build the trigger
- The run is usually less than 15 minutes
- The system auto scales for all lambda functions being triggered.

## Documentation/Tutorials
1. [AWS Lambda Documentation](https://aws.amazon.com/pm/lambda/)
2. [Your First Lambda Function](https://www.youtube.com/watch?v=e1tkFsFOBHA)


## Use Cases:
There are an uncountable number of things you can do with lambda functions. Here is a short list:

1. Start a process or load a file when it arrives in an S3 bucket.
2. Kick-off an Airflow DAG based on the state of an AWS service.
3. Send Emails when a file arrives or a resource queue is overloaded.
