# Base64 Data
Base64 is an encoding scheme that converts binary data into a text format using only 64 printable ASCII characters: A-Z, a-z, 0-9, plus (+), and slash (/), with equals (=) used for padding.

## How it works

Base64 takes binary data and represents it using only these safe, printable characters. It works by:
1. Taking input data in 8-bit bytes
2. Regrouping it into 6-bit chunks
3. Mapping each 6-bit value (0-63) to one of the 64 characters
4. Adding padding with = characters if needed

This creates about 33% size overhead - every 3 bytes of input becomes 4 characters of output.

## Why it's used

The main reason is **data safety and compatibility**. Many systems, protocols, and formats were designed to handle only text, not arbitrary binary data. Binary data can contain control characters, null bytes, or other values that might be interpreted as commands or cause transmission errors. Base64 ensures data can pass through text-only systems unchanged.

## Common use cases

**Web and APIs**: Embedding images directly in HTML/CSS (`data:image/png;base64,...`), sending binary files through JSON APIs, and handling file uploads in web forms.

**Email**: MIME encoding for attachments and non-ASCII text in email headers and bodies.

**Authentication**: Encoding tokens, API keys, and credentials. HTTP Basic Authentication uses base64 for username:password pairs.

**Configuration and storage**: Storing binary data like certificates, keys, or serialized objects in text-based config files, databases, or environment variables.

**Data transmission**: Sending binary data through protocols designed for text, like XML-RPC or when binary data needs to pass through systems that might corrupt non-printable characters.

**Cryptography**: Representing encrypted data, digital signatures, and cryptographic keys in a portable text format.

Base64 isn't compression or encryption - it's purely an encoding method to make binary data "text-safe" for systems that can't handle raw binary data reliably.

# Code Examples:
Here are practical examples of using base64 in Python for both cryptography and web/API scenarios:

## Cryptography Example

```python
import base64
from cryptography.fernet import Fernet
import os

# Generate a key for encryption
key = Fernet.generate_key()
cipher_suite = Fernet(key)

# Original message
message = "This is a secret message that needs encryption"
message_bytes = message.encode('utf-8')

# Encrypt the message
encrypted_data = cipher_suite.encrypt(message_bytes)

# Convert encrypted binary data to base64 for safe storage/transmission
encrypted_b64 = base64.b64encode(encrypted_data).decode('utf-8')
key_b64 = base64.b64encode(key).decode('utf-8')

print(f"Original message: {message}")
print(f"Encryption key (base64): {key_b64}")
print(f"Encrypted data (base64): {encrypted_b64}")

# Later: retrieve and decrypt
# Convert base64 back to binary
key_from_b64 = base64.b64decode(key_b64.encode('utf-8'))
encrypted_from_b64 = base64.b64decode(encrypted_b64.encode('utf-8'))

# Decrypt
cipher_suite_decrypt = Fernet(key_from_b64)
decrypted_message = cipher_suite_decrypt.decrypt(encrypted_from_b64)

print(f"Decrypted message: {decrypted_message.decode('utf-8')}")
```

## Web/API Example

```python
import base64
import requests
import json
from io import BytesIO
from PIL import Image

# Example 1: Sending an image file through a JSON API
def send_image_via_api(image_path, api_url):
    # Read image file as binary
    with open(image_path, 'rb') as image_file:
        image_data = image_file.read()
    
    # Encode to base64 for JSON transmission
    image_b64 = base64.b64encode(image_data).decode('utf-8')
    
    # Create JSON payload
    payload = {
        "image_data": image_b64,
        "filename": "uploaded_image.jpg",
        "description": "Image uploaded via API"
    }
    
    # Send to API
    response = requests.post(api_url, json=payload)
    return response

# Example 2: Receiving and processing base64 image data
def process_base64_image(b64_string):
    # Decode base64 back to binary
    image_data = base64.b64decode(b64_string)
    
    # Create image object from binary data
    image = Image.open(BytesIO(image_data))
    
    # Process image (resize, convert, etc.)
    resized_image = image.resize((300, 300))
    
    # Convert back to base64 for response
    buffer = BytesIO()
    resized_image.save(buffer, format='JPEG')
    processed_image_b64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    return processed_image_b64

# Example 3: Creating data URLs for HTML embedding
def create_data_url(file_path, mime_type):
    with open(file_path, 'rb') as file:
        file_data = file.read()
    
    b64_data = base64.b64encode(file_data).decode('utf-8')
    data_url = f"data:{mime_type};base64,{b64_data}"
    
    return data_url

# Usage examples:
if __name__ == "__main__":
    # Create a data URL for embedding in HTML
    # data_url = create_data_url("logo.png", "image/png")
    # print(f"Data URL: {data_url[:100]}...")  # Show first 100 chars
    
    # Example of API authentication using base64
    username = "api_user"
    password = "secret_password"
    credentials = f"{username}:{password}"
    auth_header = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')
    
    headers = {
        "Authorization": f"Basic {auth_header}",
        "Content-Type": "application/json"
    }
    
    print(f"Basic Auth header: Basic {auth_header}")
```

## Key Points

**Cryptography example**: Shows how encrypted binary data is converted to base64 for safe storage in databases, config files, or transmission through text-based systems. The encryption key itself is also base64-encoded for portability.

**Web/API example**: Demonstrates three common scenarios - sending binary files through JSON APIs, processing received base64 data, and creating data URLs for direct HTML embedding. Also shows HTTP Basic Authentication, which uses base64 encoding.

In both cases, base64 solves the fundamental problem of representing binary data in text-only contexts while maintaining data integrity across different systems and protocols.
