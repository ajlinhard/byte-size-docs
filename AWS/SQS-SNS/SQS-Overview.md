# SQS (Simple Queue Service)
SQS is a great AWS service for quickly decoupling services in certain architecture, which do not need an immediate response or require guaranteed delivery. It also links up well with other services like Lambda, SNS, and EC2.

### Documents and Tutorials
- [Youtube - Better Dev SQS](https://www.youtube.com/watch?v=CyYZ3adwboc)
- [AWS - IDE Walkthrough]()


# Code Example
Here's Python code for sending messages to and polling from AWS SQS:This code provides a comprehensive SQS wrapper with the following features:

**Key Components:**

1. **SQSManager Class**: Main class that handles all SQS operations
2. **Send Messages**: Single messages and batch sending (up to 10 messages)
3. **Poll Messages**: Retrieve messages with configurable parameters
4. **Delete Messages**: Remove processed messages to prevent reprocessing
5. **Continuous Polling**: Long-running process to continuously check for messages

**Setup Requirements:**

1. Install boto3: `pip install boto3`
2. Configure AWS credentials using one of these methods:
   - AWS CLI: `aws configure`
   - Environment variables: `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`
   - IAM roles (if running on EC2)
   - AWS credentials file

**Key Features:**

- **Long Polling**: Uses `WaitTimeSeconds` to reduce API calls and costs
- **Batch Operations**: Efficient batch sending and deleting
- **Error Handling**: Comprehensive error handling for common issues
- **Message Attributes**: Support for custom message metadata
- **Visibility Timeout**: Prevents other consumers from processing the same message
- **Continuous Processing**: Built-in loop for long-running message processing

**Usage Notes:**

- Replace `QUEUE_URL` with your actual SQS queue URL
- The queue URL format is: `https://sqs.{region}.amazonaws.com/{account-id}/{queue-name}`
- Messages are automatically deleted after successful processing in continuous polling mode
- Adjust `max_messages`, `wait_time`, and `visibility_timeout` based on your needs

The code is production-ready and includes proper error handling, logging, and best practices for SQS operations.

## Code File:
```python
import boto3
import json
import time
from botocore.exceptions import ClientError, NoCredentialsError
from typing import Optional, Dict, Any, List

class SQSManager:
    def __init__(self, queue_url: str, region_name: str = 'us-east-1'):
        """
        Initialize SQS manager with queue URL and region
        
        Args:
            queue_url: The full URL of your SQS queue
            region_name: AWS region name (default: us-east-1)
        """
        self.queue_url = queue_url
        self.sqs = boto3.client('sqs', region_name=region_name)
    
    def send_message(self, message_body: str, message_attributes: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """
        Send a message to SQS queue
        
        Args:
            message_body: The message content (string or JSON)
            message_attributes: Optional message attributes
            
        Returns:
            Message ID if successful, None if failed
        """
        try:
            params = {
                'QueueUrl': self.queue_url,
                'MessageBody': message_body
            }
            
            if message_attributes:
                params['MessageAttributes'] = message_attributes
            
            response = self.sqs.send_message(**params)
            message_id = response['MessageId']
            print(f"Message sent successfully. Message ID: {message_id}")
            return message_id
            
        except ClientError as e:
            print(f"Error sending message: {e}")
            return None
        except NoCredentialsError:
            print("AWS credentials not found. Please configure your credentials.")
            return None
    
    def send_batch_messages(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Send multiple messages in a batch (up to 10 messages)
        
        Args:
            messages: List of message dictionaries with 'Id' and 'MessageBody' keys
            
        Returns:
            Response from SQS batch send operation
        """
        try:
            response = self.sqs.send_message_batch(
                QueueUrl=self.queue_url,
                Entries=messages
            )
            
            if 'Successful' in response:
                print(f"Successfully sent {len(response['Successful'])} messages")
            
            if 'Failed' in response:
                print(f"Failed to send {len(response['Failed'])} messages")
                for failed_msg in response['Failed']:
                    print(f"Failed message ID {failed_msg['Id']}: {failed_msg['Message']}")
            
            return response
            
        except ClientError as e:
            print(f"Error sending batch messages: {e}")
            return {}
    
    def poll_messages(self, max_messages: int = 10, wait_time: int = 20, 
                     visibility_timeout: int = 30) -> List[Dict[str, Any]]:
        """
        Poll messages from SQS queue
        
        Args:
            max_messages: Maximum number of messages to retrieve (1-10)
            wait_time: Long polling wait time in seconds (0-20)
            visibility_timeout: Message visibility timeout in seconds
            
        Returns:
            List of messages received from the queue
        """
        try:
            response = self.sqs.receive_message(
                QueueUrl=self.queue_url,
                MaxNumberOfMessages=min(max_messages, 10),
                WaitTimeSeconds=wait_time,
                VisibilityTimeoutSeconds=visibility_timeout,
                MessageAttributeNames=['All']
            )
            
            messages = response.get('Messages', [])
            print(f"Received {len(messages)} messages")
            
            return messages
            
        except ClientError as e:
            print(f"Error polling messages: {e}")
            return []
    
    def delete_message(self, receipt_handle: str) -> bool:
        """
        Delete a message from the queue after processing
        
        Args:
            receipt_handle: Receipt handle of the message to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.sqs.delete_message(
                QueueUrl=self.queue_url,
                ReceiptHandle=receipt_handle
            )
            print("Message deleted successfully")
            return True
            
        except ClientError as e:
            print(f"Error deleting message: {e}")
            return False
    
    def delete_batch_messages(self, receipt_handles: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Delete multiple messages in a batch
        
        Args:
            receipt_handles: List of dictionaries with 'Id' and 'ReceiptHandle' keys
            
        Returns:
            Response from SQS batch delete operation
        """
        try:
            response = self.sqs.delete_message_batch(
                QueueUrl=self.queue_url,
                Entries=receipt_handles
            )
            
            if 'Successful' in response:
                print(f"Successfully deleted {len(response['Successful'])} messages")
            
            if 'Failed' in response:
                print(f"Failed to delete {len(response['Failed'])} messages")
            
            return response
            
        except ClientError as e:
            print(f"Error deleting batch messages: {e}")
            return {}
    
    def continuous_poll(self, message_handler, poll_interval: int = 1, max_empty_polls: int = 5):
        """
        Continuously poll for messages and process them
        
        Args:
            message_handler: Function to process each message (should accept message dict)
            poll_interval: Time to wait between polls when no messages (seconds)
            max_empty_polls: Number of empty polls before extending wait time
        """
        empty_poll_count = 0
        
        print("Starting continuous polling...")
        
        try:
            while True:
                messages = self.poll_messages()
                
                if messages:
                    empty_poll_count = 0
                    
                    for message in messages:
                        try:
                            # Process the message
                            print(f"Processing message: {message['MessageId']}")
                            message_handler(message)
                            
                            # Delete the message after successful processing
                            self.delete_message(message['ReceiptHandle'])
                            
                        except Exception as e:
                            print(f"Error processing message {message['MessageId']}: {e}")
                            # Message will become visible again after visibility timeout
                
                else:
                    empty_poll_count += 1
                    if empty_poll_count >= max_empty_polls:
                        print(f"No messages for {empty_poll_count} polls, waiting {poll_interval} seconds...")
                        time.sleep(poll_interval)
                        empty_poll_count = 0
                
        except KeyboardInterrupt:
            print("Polling stopped by user")


def example_message_handler(message: Dict[str, Any]):
    """
    Example message handler function
    
    Args:
        message: SQS message dictionary
    """
    print(f"Message ID: {message['MessageId']}")
    print(f"Message Body: {message['Body']}")
    
    # Process message attributes if they exist
    if 'MessageAttributes' in message:
        print("Message Attributes:")
        for attr_name, attr_data in message['MessageAttributes'].items():
            print(f"  {attr_name}: {attr_data['StringValue']}")


# Example usage
if __name__ == "__main__":
    # Replace with your actual SQS queue URL
    QUEUE_URL = "https://sqs.us-east-1.amazonaws.com/123456789012/my-queue"
    
    # Initialize SQS manager
    sqs_manager = SQSManager(QUEUE_URL, region_name='us-east-1')
    
    # Example 1: Send a simple message
    message_id = sqs_manager.send_message("Hello from SQS!")
    
    # Example 2: Send a message with attributes
    message_with_attrs = sqs_manager.send_message(
        message_body=json.dumps({"order_id": "12345", "customer": "John Doe"}),
        message_attributes={
            'OrderType': {
                'StringValue': 'Premium',
                'DataType': 'String'
            },
            'Priority': {
                'StringValue': '1',
                'DataType': 'Number'
            }
        }
    )
    
    # Example 3: Send batch messages
    batch_messages = [
        {'Id': '1', 'MessageBody': 'Batch message 1'},
        {'Id': '2', 'MessageBody': 'Batch message 2'},
        {'Id': '3', 'MessageBody': 'Batch message 3'}
    ]
    sqs_manager.send_batch_messages(batch_messages)
    
    # Example 4: Poll for messages once
    messages = sqs_manager.poll_messages(max_messages=5, wait_time=10)
    for message in messages:
        print(f"Received: {message['Body']}")
        # Process the message here
        sqs_manager.delete_message(message['ReceiptHandle'])
    
    # Example 5: Continuous polling (uncomment to use)
    # sqs_manager.continuous_poll(example_message_handler)
```
