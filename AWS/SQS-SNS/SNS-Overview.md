# SNS (Simple Notification Service)


### Documents and Tutorials
- [AWS Official API](https://docs.aws.amazon.com/sns/latest/api/API_Publish.html)
- [Youtube SNS Series](https://www.youtube.com/watch?v=CdlsQ37Pjr4)

# Code Example
Here's a simple AWS SNS Python example that demonstrates the basic operations:This example demonstrates the core AWS SNS operations:

**Prerequisites:**
- Install boto3: `pip install boto3`
- Configure AWS credentials (AWS CLI, environment variables, or IAM roles)
- Ensure your AWS account has SNS permissions

**Key Features:**
- **Create Topic**: Creates a new SNS topic
- **Subscribe Email**: Adds email subscriptions (requires email confirmation)
- **Publish Messages**: Sends both simple text and JSON-structured messages
- **List Topics**: Shows all available topics
- **Delete Topic**: Cleanup functionality

**Usage:**
1. Replace `your-email@example.com` with your actual email address
2. Update the region in `create_sns_client()` if needed
3. Run the script: `python sns_example.py`

The script will create a topic, subscribe your email, send test messages, and list all topics. You'll receive a confirmation email that you need to click to activate the subscription. Once confirmed, you'll receive the test messages via email.

##Code File:

```python
import boto3
import json
from botocore.exceptions import ClientError

def create_sns_client():
    """Create and return an SNS client"""
    return boto3.client('sns', region_name='us-east-1')

def create_topic(sns_client, topic_name):
    """Create an SNS topic and return its ARN"""
    try:
        response = sns_client.create_topic(Name=topic_name)
        topic_arn = response['TopicArn']
        print(f"Topic created successfully: {topic_arn}")
        return topic_arn
    except ClientError as e:
        print(f"Error creating topic: {e}")
        return None

def subscribe_email(sns_client, topic_arn, email_address):
    """Subscribe an email address to the topic"""
    try:
        response = sns_client.subscribe(
            TopicArn=topic_arn,
            Protocol='email',
            Endpoint=email_address
        )
        subscription_arn = response['SubscriptionArn']
        print(f"Email subscription created: {subscription_arn}")
        print(f"Check {email_address} for confirmation email")
        return subscription_arn
    except ClientError as e:
        print(f"Error subscribing email: {e}")
        return None

def publish_message(sns_client, topic_arn, subject, message):
    """Publish a message to the topic"""
    try:
        response = sns_client.publish(
            TopicArn=topic_arn,
            Subject=subject,
            Message=message
        )
        message_id = response['MessageId']
        print(f"Message published successfully: {message_id}")
        return message_id
    except ClientError as e:
        print(f"Error publishing message: {e}")
        return None

def publish_json_message(sns_client, topic_arn, message_data):
    """Publish a JSON message with different content for different protocols"""
    try:
        # Create message structure for different protocols
        message_structure = {
            "default": "Default message",
            "email": f"Email: {message_data['content']}",
            "sms": f"SMS: {message_data['content'][:160]}"  # SMS limit
        }
        
        response = sns_client.publish(
            TopicArn=topic_arn,
            Subject=message_data.get('subject', 'Notification'),
            Message=json.dumps(message_structure),
            MessageStructure='json'
        )
        message_id = response['MessageId']
        print(f"JSON message published successfully: {message_id}")
        return message_id
    except ClientError as e:
        print(f"Error publishing JSON message: {e}")
        return None

def list_topics(sns_client):
    """List all SNS topics"""
    try:
        response = sns_client.list_topics()
        topics = response.get('Topics', [])
        print("Available topics:")
        for topic in topics:
            print(f"  - {topic['TopicArn']}")
        return topics
    except ClientError as e:
        print(f"Error listing topics: {e}")
        return []

def delete_topic(sns_client, topic_arn):
    """Delete an SNS topic"""
    try:
        sns_client.delete_topic(TopicArn=topic_arn)
        print(f"Topic deleted successfully: {topic_arn}")
        return True
    except ClientError as e:
        print(f"Error deleting topic: {e}")
        return False

def main():
    """Main function demonstrating SNS operations"""
    # Initialize SNS client
    sns = create_sns_client()
    
    # Configuration
    topic_name = "MyTestTopic"
    email_address = "your-email@example.com"  # Replace with your email
    
    print("=== AWS SNS Python Example ===\n")
    
    # 1. Create a topic
    print("1. Creating topic...")
    topic_arn = create_topic(sns, topic_name)
    if not topic_arn:
        return
    
    # 2. Subscribe email to topic
    print("\n2. Subscribing email to topic...")
    subscription_arn = subscribe_email(sns, topic_arn, email_address)
    
    # 3. List all topics
    print("\n3. Listing all topics...")
    list_topics(sns)
    
    # 4. Publish a simple message
    print("\n4. Publishing simple message...")
    publish_message(
        sns, 
        topic_arn, 
        "Test Subject", 
        "This is a test message from AWS SNS!"
    )
    
    # 5. Publish a JSON message
    print("\n5. Publishing JSON message...")
    message_data = {
        "subject": "JSON Test",
        "content": "This is a JSON structured message with different content for different protocols."
    }
    publish_json_message(sns, topic_arn, message_data)
    
    # 6. Clean up (optional - uncomment to delete topic)
    print("\n6. Cleanup...")
    print("Topic cleanup skipped. Uncomment the line below to delete the topic.")
    # delete_topic(sns, topic_arn)

if __name__ == "__main__":
    # Note: Make sure to configure AWS credentials before running
    # You can do this via:
    # 1. AWS CLI: aws configure
    # 2. Environment variables: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
    # 3. IAM roles (if running on EC2)
    # 4. AWS credentials file
    
    main()
```
