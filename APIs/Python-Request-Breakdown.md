# Python Request Breakdown
This is the python functions we are breaking down as the bread and butter of python API calls get, post, put, and patch.

---
# POST
```python
import request

response = requests.post(
        FULL_URL,
        headers=headers,
        json=body,
        timeout=10,
        verify=verify,
        cert=cert_data
)
```
## `requests.post()` Parameters

**`FULL_URL`** (first positional argument)
- The complete endpoint URL where the POST request is sent
- Example: `"https://api.example.com/v1/users"`
- This is the destination server address

**`headers=headers`**
- HTTP headers to include in the request
- Typically a dictionary containing metadata like:
  - `Content-Type`: Specifies data format (e.g., `"application/json"`)
  - `Authorization`: Authentication tokens (e.g., `"Bearer token123"`)
  - Custom headers specific to the API
- Example: `{"Content-Type": "application/json", "Authorization": "Bearer xyz"}`

**`json=body`**
- The request payload/body data to send
- Automatically serializes a Python dictionary to JSON format
- Sets `Content-Type: application/json` header automatically
- Example: `{"name": "John", "email": "john@example.com"}`
- Alternative: use `data=` for non-JSON payloads

**`timeout=10`**
- Maximum time (in seconds) to wait for the server to respond
- Prevents the request from hanging indefinitely
- After 10 seconds, raises a `requests.exceptions.Timeout` exception
- Can be a tuple `(connect_timeout, read_timeout)` for finer control

**`verify=verify`**
- Controls SSL certificate verification
- `True` (default): Verifies the server's SSL certificate for security
- `False`: Skips verification (not recommended for production)
- Can also be a path to a CA bundle file for custom certificates
- Used when dealing with self-signed certificates or corporate proxies

**`cert=cert_data`**
- Client-side certificate for mutual TLS authentication
- Used when the server requires the client to authenticate with a certificate
- Can be:
  - A single file path: `"/path/to/cert.pem"` (cert and key combined)
  - A tuple: `("/path/to/cert.pem", "/path/to/key.pem")` (separate files)
- Required for APIs that use two-way SSL/TLS authentication

## Common Use Case

This configuration is typically used for secure API communication where:
- The API requires authentication (headers)
- You're sending structured data (json)
- You need timeout protection to avoid hanging
- You're dealing with custom SSL certificates (verify/cert)

---
