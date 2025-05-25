I'll create Python examples for both Kafka messaging patterns. Let me implement both scenarios with clear code and explanations.

I've created a comprehensive Python implementation for both Kafka messaging patterns. Let me explain each scenario:

## Scenario 1: Synchronous Block Pattern

This implementation:
- Creates a unique correlation ID for each request
- Sends a request message to a Kafka topic
- Immediately sets up a consumer to poll for the reply
- Blocks the thread until a matching reply is received or timeout occurs
- Returns the response when found

Key features:
- Simple and straightforward implementation
- Thread that sends the request is the same thread that waits for and processes the reply
- Uses a unique consumer group ID to ensure this consumer gets all messages
- Includes timeout handling to prevent infinite blocking

The main limitation, as you noted, is that if the requester crashes while waiting, it's difficult to re-establish the blocked thread's state.

## Scenario 2: Asynchronous Callback Pattern

This implementation:
- Creates a separate thread that continuously listens for replies
- Maintains a dictionary of registered callbacks keyed by correlation ID
- When sending a request, stores the callback and context information
- When a reply arrives, looks up the appropriate callback and invokes it
- Preserves the original request context to help with processing the reply

Key features:
- Supports multiple concurrent requests without blocking
- Single reply listener thread can handle replies for multiple requests
- If the requester crashes, it can recover by simply restarting the reply thread
- Context mechanism allows the callback to "remember" what the original request was

I've also included a simple `RequestProcessor` service that can handle requests from either pattern and send appropriate replies.

## Code:
```python
# SCENARIO 1: Synchronous Block Pattern
# -----------------------------------------------------
from confluent_kafka import Producer, Consumer
import json
import uuid
import time

class SynchronousRequestReply:
    def __init__(self, bootstrap_servers):
        self.bootstrap_servers = bootstrap_servers
        self.request_topic = "request_topic"
        self.reply_topic = "reply_topic"
        self.correlation_id = None
        
        # Producer config
        self.producer_config = {
            'bootstrap.servers': bootstrap_servers,
        }
        
        # Consumer config
        self.consumer_config = {
            'bootstrap.servers': bootstrap_servers,
            'group.id': f'reply-consumer-{uuid.uuid4()}',  # Unique consumer group
            'auto.offset.reset': 'latest',                 # Only get new messages
        }
    
    def send_request_and_wait(self, request_data, timeout=30):
        """Send request and block until reply received or timeout"""
        # Create a unique correlation ID for this request
        self.correlation_id = str(uuid.uuid4())
        
        # Prepare the message
        message = {
            "payload": request_data,
            "correlation_id": self.correlation_id,
            "reply_topic": self.reply_topic,
            "timestamp": time.time()
        }
        
        # Create producer and send message
        producer = Producer(self.producer_config)
        producer.produce(
            self.request_topic,
            json.dumps(message).encode('utf-8')
        )
        producer.flush()
        print(f"Request sent with correlation_id: {self.correlation_id}")
        
        # Create consumer for replies
        consumer = Consumer(self.consumer_config)
        consumer.subscribe([self.reply_topic])
        
        # Poll for the response with our correlation ID
        start_time = time.time()
        while (time.time() - start_time) < timeout:
            msg = consumer.poll(1.0)  # Poll with 1 second timeout
            
            if msg is None:
                continue
                
            if msg.error():
                print(f"Consumer error: {msg.error()}")
                continue
                
            try:
                reply_data = json.loads(msg.value().decode('utf-8'))
                
                # Check if this is our reply
                if reply_data.get('correlation_id') == self.correlation_id:
                    consumer.close()
                    return reply_data.get('payload')
                    
            except Exception as e:
                print(f"Error processing message: {e}")
        
        # If we get here, we timed out
        consumer.close()
        raise TimeoutError(f"No reply received within {timeout} seconds")


# Usage example
if __name__ == "__main__":
    client = SynchronousRequestReply(bootstrap_servers="localhost:9092")
    
    try:
        # Send request and block until response
        request_data = {"action": "get_user", "user_id": 123}
        print("Sending request...")
        response = client.send_request_and_wait(request_data)
        print(f"Got response: {response}")
        
    except TimeoutError as e:
        print(f"Request failed: {e}")


# SCENARIO 2: Asynchronous Callback Pattern
# -----------------------------------------------------
from confluent_kafka import Producer, Consumer
import json
import uuid
import threading
import time

class AsyncRequestReply:
    def __init__(self, bootstrap_servers):
        self.bootstrap_servers = bootstrap_servers
        self.request_topic = "request_topic"
        self.reply_topic = "reply_topic"
        
        # Store callbacks by correlation ID
        self.callbacks = {}
        
        # Producer config
        self.producer_config = {
            'bootstrap.servers': bootstrap_servers,
        }
        
        # Consumer config for reply listener
        self.consumer_config = {
            'bootstrap.servers': bootstrap_servers,
            'group.id': f'reply-consumer-{uuid.uuid4()}',  # Unique consumer group
            'auto.offset.reset': 'latest',                 # Only get new messages
        }
        
        # Create producer
        self.producer = Producer(self.producer_config)
        
        # Start reply listener thread
        self.running = True
        self.reply_thread = threading.Thread(target=self._reply_listener)
        self.reply_thread.daemon = True
        self.reply_thread.start()
    
    def send_request(self, request_data, callback):
        """Send request and register callback for the reply"""
        # Create a unique correlation ID for this request
        correlation_id = str(uuid.uuid4())
        
        # Register the callback
        self.callbacks[correlation_id] = {
            'callback': callback,
            'context': {
                'request_data': request_data,
                'timestamp': time.time()
            }
        }
        
        # Prepare the message
        message = {
            "payload": request_data,
            "correlation_id": correlation_id,
            "reply_topic": self.reply_topic,
            "timestamp": time.time()
        }
        
        # Send message
        self.producer.produce(
            self.request_topic,
            json.dumps(message).encode('utf-8')
        )
        self.producer.flush()
        print(f"Request sent with correlation_id: {correlation_id}")
        return correlation_id
    
    def _reply_listener(self):
        """Thread that listens for replies and triggers callbacks"""
        consumer = Consumer(self.consumer_config)
        consumer.subscribe([self.reply_topic])
        
        try:
            while self.running:
                msg = consumer.poll(1.0)  # Poll with 1 second timeout
                
                if msg is None:
                    continue
                    
                if msg.error():
                    print(f"Consumer error: {msg.error()}")
                    continue
                    
                try:
                    reply_data = json.loads(msg.value().decode('utf-8'))
                    correlation_id = reply_data.get('correlation_id')
                    
                    # Check if we have a callback registered for this correlation ID
                    if correlation_id in self.callbacks:
                        # Get the callback and context
                        callback_info = self.callbacks.pop(correlation_id)
                        callback = callback_info['callback']
                        context = callback_info['context']
                        
                        # Call the callback with reply payload and original context
                        callback(reply_data.get('payload'), context)
                        
                except Exception as e:
                    print(f"Error processing message: {e}")
        
        finally:
            consumer.close()
            print("Reply listener stopped")
    
    def shutdown(self):
        """Stop the reply listener thread"""
        self.running = False
        if self.reply_thread.is_alive():
            self.reply_thread.join(timeout=5.0)


# Usage example
if __name__ == "__main__":
    client = AsyncRequestReply(bootstrap_servers="localhost:9092")
    
    # Define callback function
    def handle_reply(reply_payload, context):
        """Callback function that processes the reply"""
        original_request = context['request_data']
        request_time = context['timestamp']
        processing_time = time.time() - request_time
        
        print(f"Got reply for request: {original_request}")
        print(f"Reply data: {reply_payload}")
        print(f"Processing time: {processing_time:.2f} seconds")
    
    # Send multiple requests with the same callback
    requests = [
        {"action": "get_user", "user_id": 123},
        {"action": "get_product", "product_id": 456},
        {"action": "get_order", "order_id": 789}
    ]
    
    for request_data in requests:
        client.send_request(request_data, handle_reply)
    
    # Keep the main thread running to allow callbacks to be processed
    try:
        print("Waiting for replies. Press Ctrl+C to exit.")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down...")
    finally:
        client.shutdown()


# Example of a service that handles requests and sends replies
# -----------------------------------------------------
from confluent_kafka import Producer, Consumer
import json
import threading
import time

class RequestProcessor:
    def __init__(self, bootstrap_servers):
        self.bootstrap_servers = bootstrap_servers
        self.request_topic = "request_topic"
        
        # Producer config for sending replies
        self.producer_config = {
            'bootstrap.servers': bootstrap_servers,
        }
        
        # Consumer config for request listener
        self.consumer_config = {
            'bootstrap.servers': bootstrap_servers,
            'group.id': 'request-processor',  # Fixed group ID for the service
            'auto.offset.reset': 'earliest',  # Get all messages
        }
        
        # Create producer for replies
        self.producer = Producer(self.producer_config)
        
        # Start request listener thread
        self.running = True
        self.request_thread = threading.Thread(target=self._request_listener)
        self.request_thread.daemon = True
        self.request_thread.start()
    
    def _request_listener(self):
        """Thread that listens for requests and processes them"""
        consumer = Consumer(self.consumer_config)
        consumer.subscribe([self.request_topic])
        
        try:
            while self.running:
                msg = consumer.poll(1.0)  # Poll with 1 second timeout
                
                if msg is None:
                    continue
                    
                if msg.error():
                    print(f"Consumer error: {msg.error()}")
                    continue
                    
                try:
                    request_data = json.loads(msg.value().decode('utf-8'))
                    
                    # Extract message details
                    payload = request_data.get('payload')
                    correlation_id = request_data.get('correlation_id')
                    reply_topic = request_data.get('reply_topic')
                    
                    print(f"Processing request: {payload} (correlation_id: {correlation_id})")
                    
                    # Process the request (simulated with a delay)
                    response_payload = self._process_request(payload)
                    
                    # Create reply message
                    reply = {
                        "payload": response_payload,
                        "correlation_id": correlation_id,
                        "timestamp": time.time()
                    }
                    
                    # Send reply
                    self.producer.produce(
                        reply_topic,
                        json.dumps(reply).encode('utf-8')
                    )
                    self.producer.flush()
                    print(f"Reply sent for correlation_id: {correlation_id}")
                    
                except Exception as e:
                    print(f"Error processing request: {e}")
        
        finally:
            consumer.close()
            print("Request listener stopped")
    
    def _process_request(self, request):
        """Process the request and generate a response"""
        # Simulate processing time
        time.sleep(1)
        
        # Create a response based on the request
        if request.get('action') == 'get_user':
            return {
                "status": "success",
                "user": {
                    "id": request.get('user_id'),
                    "name": f"User {request.get('user_id')}",
                    "email": f"user{request.get('user_id')}@example.com"
                }
            }
        elif request.get('action') == 'get_product':
            return {
                "status": "success",
                "product": {
                    "id": request.get('product_id'),
                    "name": f"Product {request.get('product_id')}",
                    "price": 99.99
                }
            }
        elif request.get('action') == 'get_order':
            return {
                "status": "success",
                "order": {
                    "id": request.get('order_id'),
                    "items": 3,
                    "total": 299.97
                }
            }
        else:
            return {
                "status": "error",
                "message": "Unknown action"
            }
    
    def shutdown(self):
        """Stop the request listener thread"""
        self.running = False
        if self.request_thread.is_alive():
            self.request_thread.join(timeout=5.0)


# To run the service
if __name__ == "__main__":
    processor = RequestProcessor(bootstrap_servers="localhost:9092")
    
    try:
        print("Request processor running. Press Ctrl+C to exit.")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down...")
    finally:
        processor.shutdown()
```
