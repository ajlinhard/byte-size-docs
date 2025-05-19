Great question! There are several methods clients use to stay linked with API servers for receiving information. Let me break this down:

## Connection Methods

### 1. Polling
**How it works:** The client periodically sends requests to the server asking "Do you have anything new for me?"
- **Simple polling:** Client checks at fixed intervals (e.g., every 30 seconds)
- **Long polling:** Client sends a request, server holds it open until new data arrives or timeout occurs
- **Advantages:** Simple to implement, works everywhere
- **Disadvantages:** Inefficient, creates unnecessary traffic, higher latency

### 2. WebSockets
**How it works:** Creates a persistent, bidirectional connection between client and server
```python
# Python WebSocket client example
import websocket

def on_message(ws, message):
    print(f"Received: {message}")

ws = websocket.WebSocketApp("ws://api.example.com/socket",
                            on_message=on_message)
ws.run_forever()
```
- **Advantages:** Real-time updates, reduced overhead, bidirectional
- **Disadvantages:** More complex, may have issues with some proxies/firewalls

### 3. Server-Sent Events (SSE)
**How it works:** HTTP connection that stays open for server to push updates
```python
# Python SSE client example
import sseclient
import requests

response = requests.get('http://api.example.com/events', stream=True)
client = sseclient.SSEClient(response)
for event in client.events():
    print(f"Event: {event.data}")
```
- **Advantages:** Simpler than WebSockets, standard HTTP
- **Disadvantages:** One-way communication (server to client only)

### 4. Webhooks
**How it works:** Client registers a URL, server makes HTTP requests to that URL when events occur
- **Advantages:** Efficient, no polling needed
- **Disadvantages:** Client needs to be publicly accessible

## Authentication & Session Management

To maintain a linked connection over time:

1. **API Keys/Tokens**
   - Long-lived API keys
   - Short-lived access tokens with refresh tokens

2. **Session Management**
   - Session IDs in cookies or headers
   - Keep-alive mechanisms for persistent connections

3. **Connection Resilience**
   - Automatic reconnection after disconnection
   - Exponential backoff for retry attempts
   - Message queuing to handle offline periods

## Real-world Example

For a robust client-server link in Python:

```python
import time
import websocket
import json
import threading
import random

# Configuration
API_URL = "wss://api.example.com/stream"
API_KEY = "your_api_key"
RECONNECT_DELAY_MIN = 1  # seconds
RECONNECT_DELAY_MAX = 30  # seconds

class APIClient:
    def __init__(self):
        self.ws = None
        self.connected = False
        self.reconnect_delay = RECONNECT_DELAY_MIN

    def on_message(self, ws, message):
        data = json.loads(message)
        print(f"Received: {data}")
        # Process the data here

    def on_error(self, ws, error):
        print(f"Error: {error}")

    def on_close(self, ws, close_status_code, close_msg):
        self.connected = False
        print(f"Connection closed: {close_msg}")
        self.schedule_reconnect()

    def on_open(self, ws):
        self.connected = True
        self.reconnect_delay = RECONNECT_DELAY_MIN  # Reset delay on successful connection
        print("Connection opened")
        # Authenticate
        auth_message = json.dumps({"type": "auth", "api_key": API_KEY})
        ws.send(auth_message)
        # Subscribe to required data streams
        subscribe_message = json.dumps({"type": "subscribe", "channels": ["updates", "alerts"]})
        ws.send(subscribe_message)

    def connect(self):
        # Set up WebSocket with automatic reconnection
        websocket.enableTrace(False)
        self.ws = websocket.WebSocketApp(API_URL,
                                         on_open=self.on_open,
                                         on_message=self.on_message,
                                         on_error=self.on_error,
                                         on_close=self.on_close)
        
        # Start WebSocket connection in a separate thread
        wst = threading.Thread(target=self.ws.run_forever)
        wst.daemon = True
        wst.start()

    def schedule_reconnect(self):
        # Exponential backoff with jitter for reconnection
        jitter = random.uniform(0, 0.5)
        delay = min(self.reconnect_delay * (1 + jitter), RECONNECT_DELAY_MAX)
        print(f"Reconnecting in {delay:.2f} seconds...")
        time.sleep(delay)
        self.reconnect_delay = min(self.reconnect_delay * 2, RECONNECT_DELAY_MAX)
        self.connect()

    def send_message(self, message):
        if self.connected and self.ws:
            self.ws.send(json.dumps(message))
            return True
        return False

# Usage
if __name__ == "__main__":
    client = APIClient()
    client.connect()
    
    # Keep the main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Exiting...")
```

This example demonstrates a robust WebSocket client that:
- Maintains persistent connection
- Handles authentication
- Automatically reconnects with exponential backoff
- Processes incoming messages
- Allows sending messages to the server

The choice of method depends on your specific requirements for latency, traffic volume, and the nature of the data being exchanged.
