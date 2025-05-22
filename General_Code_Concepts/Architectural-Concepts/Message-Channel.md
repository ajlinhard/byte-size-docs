# Message Channel
Below is Python code that demonstrates a Message Channel pattern where applications communicate through dedicated channels for specific types of information. This pattern allows applications to exchange information without directly knowing about each other, using channels as intermediaries.

```python
import queue
import threading
import time
import uuid
from typing import Dict, Any, List, Callable

class MessageChannel:
    """
    A channel that allows applications to publish and subscribe to specific types of messages.
    """
    def __init__(self, name: str):
        self.name = name
        self.queue = queue.Queue()
        self.subscribers = []
        self._running = True
        
    def publish(self, message: Dict[str, Any]) -> None:
        """Publish a message to this channel"""
        message['timestamp'] = time.time()
        message['id'] = str(uuid.uuid4())
        self.queue.put(message)
        
    def subscribe(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        """Subscribe to messages on this channel"""
        self.subscribers.append(callback)
        
    def start_processing(self) -> None:
        """Start processing messages in a separate thread"""
        def process_messages():
            while self._running:
                try:
                    message = self.queue.get(timeout=1)
                    for subscriber in self.subscribers:
                        subscriber(message)
                    self.queue.task_done()
                except queue.Empty:
                    pass
                
        thread = threading.Thread(target=process_messages)
        thread.daemon = True
        thread.start()
        
    def stop_processing(self) -> None:
        """Stop processing messages"""
        self._running = False


class MessageBroker:
    """
    A message broker that manages multiple channels.
    """
    def __init__(self):
        self.channels = {}
        
    def create_channel(self, name: str) -> MessageChannel:
        """Create a new channel with the given name"""
        if name not in self.channels:
            self.channels[name] = MessageChannel(name)
            self.channels[name].start_processing()
        return self.channels[name]
    
    def get_channel(self, name: str) -> MessageChannel:
        """Get an existing channel by name"""
        if name not in self.channels:
            raise ValueError(f"Channel '{name}' does not exist")
        return self.channels[name]
    
    def list_channels(self) -> List[str]:
        """List all available channels"""
        return list(self.channels.keys())


class Application:
    """
    Base class for applications that can send and receive messages.
    """
    def __init__(self, name: str, broker: MessageBroker):
        self.name = name
        self.broker = broker
        self.subscribed_channels = []
        
    def publish_to(self, channel_name: str, data: Dict[str, Any]) -> None:
        """Publish data to a specific channel"""
        try:
            channel = self.broker.get_channel(channel_name)
            message = {
                'sender': self.name,
                'data': data
            }
            channel.publish(message)
            print(f"{self.name} published to '{channel_name}': {data}")
        except ValueError as e:
            print(f"Error: {e}")
    
    def subscribe_to(self, channel_name: str, callback: Callable = None) -> None:
        """Subscribe to a specific channel"""
        try:
            channel = self.broker.get_channel(channel_name)
            
            if callback is None:
                # Default callback if none provided
                callback = self._default_message_handler
                
            channel.subscribe(callback)
            self.subscribed_channels.append(channel_name)
            print(f"{self.name} subscribed to '{channel_name}'")
        except ValueError as e:
            print(f"Error: {e}")
            
    def _default_message_handler(self, message: Dict[str, Any]) -> None:
        """Default message handler that prints messages"""
        print(f"{self.name} received on '{message.get('channel', 'unknown')}': {message}")


# Example usage
def demo():
    # Create a message broker
    broker = MessageBroker()
    
    # Create channels for different types of information
    broker.create_channel("orders")
    broker.create_channel("inventory")
    broker.create_channel("shipping")
    
    # Create applications
    order_processor = Application("OrderProcessor", broker)
    inventory_manager = Application("InventoryManager", broker)
    shipping_service = Application("ShippingService", broker)
    
    # Subscribe applications to relevant channels
    inventory_manager.subscribe_to("orders", 
        lambda msg: inventory_manager.publish_to("inventory", {
            "order_id": msg["data"]["order_id"],
            "items_reserved": True,
            "in_stock": msg["data"]["items"]
        }))
    
    shipping_service.subscribe_to("inventory", 
        lambda msg: shipping_service.publish_to("shipping", {
            "order_id": msg["data"]["order_id"],
            "status": "ready_for_shipment" if msg["data"]["items_reserved"] else "waiting"
        }))
    
    order_processor.subscribe_to("shipping")
    
    # Order processor creates a new order
    order_processor.publish_to("orders", {
        "order_id": "12345",
        "customer": "John Doe",
        "items": ["book", "pen"]
    })

    # Wait a bit for messages to be processed
    time.sleep(2)


if __name__ == "__main__":
    demo()
```

This code demonstrates the Message Channel pattern with the following components:

1. **MessageChannel** - A dedicated channel for a specific type of information with publish/subscribe functionality.

2. **MessageBroker** - Manages multiple channels, allowing applications to discover and access them.

3. **Application** - Base class for applications that can publish to and subscribe from specific channels.

4. **Demo Flow**:
   - Three applications (OrderProcessor, InventoryManager, ShippingService)
   - Three channels (orders, inventory, shipping) for different types of information
   - Applications communicate without direct knowledge of each other:
     - OrderProcessor publishes an order
     - InventoryManager listens on the "orders" channel, processes it, and publishes to the "inventory" channel
     - ShippingService listens on the "inventory" channel, processes it, and publishes to the "shipping" channel
     - OrderProcessor listens on the "shipping" channel to track the order status

This pattern follows your requirements where:
- Applications communicate through dedicated channels
- Publishers don't know which specific applications will consume their messages
- Channels are organized by the type of information they carry
- Applications select which channels to use based on the information they need
