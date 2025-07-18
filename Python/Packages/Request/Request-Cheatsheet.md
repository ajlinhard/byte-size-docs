# Python Requests Package Cheatsheet
This cheatsheet for the Python requests package that covers everything from basic HTTP methods to advanced features like sessions, authentication, and error handling. The cheatsheet is organized in a logical flow:

1. **Common Functions Table** - Quick reference for the most frequently used HTTP methods
2. **Response Object Properties** - Essential attributes you'll use to handle responses
3. **Less Common Functions** - Advanced features like sessions, file uploads, and authentication
4. **Complete Examples** - Five real-world scenarios showing practical implementations

The examples demonstrate common use cases like building REST API clients, downloading files with progress tracking, web scraping with authentication, implementing retry logic for rate limiting, and streaming large JSON responses.

This should serve as both a quick reference for syntax and a guide for implementing more complex HTTP interactions in Python!

## Common Functions

| Function Name | Purpose | Key Parameters | Concise Example |
|---------------|---------|----------------|-----------------|
| `requests.get()` | Retrieve data from URL | `url`, `params`, `headers`, `timeout` | `requests.get('https://api.github.com/users/octocat')` |
| `requests.post()` | Send data to server | `url`, `data`, `json`, `headers` | `requests.post('https://api.example.com/users', json={'name': 'John'})` |
| `requests.put()` | Update/replace resource | `url`, `data`, `json`, `headers` | `requests.put('https://api.example.com/users/1', json={'name': 'Jane'})` |
| `requests.patch()` | Partially update resource | `url`, `data`, `json`, `headers` | `requests.patch('https://api.example.com/users/1', json={'email': 'new@email.com'})` |
| `requests.delete()` | Remove resource | `url`, `headers` | `requests.delete('https://api.example.com/users/1')` |
| `requests.head()` | Get headers only | `url`, `headers` | `requests.head('https://example.com')` |
| `requests.options()` | Get allowed methods | `url`, `headers` | `requests.options('https://api.example.com/users')` |

## Response Object Properties

| Property | Purpose | Example |
|----------|---------|---------|
| `.status_code` | HTTP status code | `response.status_code == 200` |
| `.text` | Response content as string | `response.text` |
| `.json()` | Parse JSON response | `data = response.json()` |
| `.content` | Raw bytes content | `response.content` |
| `.headers` | Response headers | `response.headers['Content-Type']` |
| `.url` | Final URL after redirects | `response.url` |
| `.cookies` | Response cookies | `response.cookies['session_id']` |
| `.elapsed` | Request duration | `response.elapsed.total_seconds()` |

## Less Common Functions and Features

### Session Objects
```python
session = requests.Session()
session.headers.update({'User-Agent': 'MyApp/1.0'})
session.auth = ('username', 'password')
response = session.get('https://api.example.com/data')
```

### File Uploads
```python
files = {'file': open('report.pdf', 'rb')}
response = requests.post('https://api.example.com/upload', files=files)

# Multiple files
files = {'file1': open('file1.txt', 'rb'), 'file2': open('file2.txt', 'rb')}
response = requests.post('https://api.example.com/upload', files=files)
```

### Authentication Methods
```python
# Basic Auth
response = requests.get('https://api.example.com/data', auth=('user', 'pass'))

# Bearer Token
headers = {'Authorization': 'Bearer your_token_here'}
response = requests.get('https://api.example.com/data', headers=headers)

# Custom Auth
from requests.auth import HTTPDigestAuth
response = requests.get('https://api.example.com/data', auth=HTTPDigestAuth('user', 'pass'))
```

### Advanced Parameters

| Parameter | Purpose | Example |
|-----------|---------|---------|
| `timeout` | Request timeout (seconds) | `requests.get(url, timeout=5)` |
| `allow_redirects` | Follow redirects | `requests.get(url, allow_redirects=False)` |
| `verify` | SSL certificate verification | `requests.get(url, verify=False)` |
| `cert` | Client certificate | `requests.get(url, cert=('/path/client.cert', '/path/client.key'))` |
| `proxies` | Proxy configuration | `requests.get(url, proxies={'http': 'http://proxy:8080'})` |
| `stream` | Stream response | `requests.get(url, stream=True)` |
| `cookies` | Send cookies | `requests.get(url, cookies={'session': 'abc123'})` |

### Error Handling
```python
try:
    response = requests.get('https://api.example.com/data', timeout=5)
    response.raise_for_status()  # Raises HTTPError for bad status codes
except requests.exceptions.RequestException as e:
    print(f"Request failed: {e}")
except requests.exceptions.Timeout:
    print("Request timed out")
except requests.exceptions.ConnectionError:
    print("Connection error")
```

## Complete Examples

### Example 1: REST API Client
```python
import requests
import json

class APIClient:
    def __init__(self, base_url, token=None):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        if token:
            self.session.headers.update({'Authorization': f'Bearer {token}'})
    
    def get_user(self, user_id):
        response = self.session.get(f'{self.base_url}/users/{user_id}')
        response.raise_for_status()
        return response.json()
    
    def create_user(self, user_data):
        response = self.session.post(f'{self.base_url}/users', json=user_data)
        response.raise_for_status()
        return response.json()
    
    def update_user(self, user_id, user_data):
        response = self.session.patch(f'{self.base_url}/users/{user_id}', json=user_data)
        response.raise_for_status()
        return response.json()

# Usage
client = APIClient('https://api.example.com', token='your_token')
user = client.get_user(123)
new_user = client.create_user({'name': 'John Doe', 'email': 'john@example.com'})
```

### Example 2: File Download with Progress
```python
import requests
from pathlib import Path

def download_file(url, filename):
    with requests.get(url, stream=True) as response:
        response.raise_for_status()
        total_size = int(response.headers.get('content-length', 0))
        
        with open(filename, 'wb') as file:
            downloaded = 0
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    file.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        print(f"\rDownload progress: {percent:.1f}%", end='')
        print(f"\nDownload complete: {filename}")

download_file('https://example.com/large-file.zip', 'downloaded-file.zip')
```

### Example 3: Web Scraping with Session
```python
import requests
from bs4 import BeautifulSoup

def scrape_with_login(login_url, target_url, username, password):
    session = requests.Session()
    
    # Get login page to extract CSRF token
    login_page = session.get(login_url)
    soup = BeautifulSoup(login_page.text, 'html.parser')
    csrf_token = soup.find('input', {'name': 'csrf_token'})['value']
    
    # Login
    login_data = {
        'username': username,
        'password': password,
        'csrf_token': csrf_token
    }
    session.post(login_url, data=login_data)
    
    # Access protected page
    protected_page = session.get(target_url)
    return protected_page.text

# Usage
content = scrape_with_login(
    'https://example.com/login',
    'https://example.com/protected-data',
    'myusername',
    'mypassword'
)
```

### Example 4: API Rate Limiting and Retry
```python
import requests
import time
from functools import wraps

def retry_on_rate_limit(max_retries=3, backoff_factor=1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries + 1):
                try:
                    response = func(*args, **kwargs)
                    if response.status_code == 429:  # Rate limited
                        if attempt < max_retries:
                            wait_time = backoff_factor * (2 ** attempt)
                            print(f"Rate limited. Waiting {wait_time} seconds...")
                            time.sleep(wait_time)
                            continue
                    return response
                except requests.exceptions.RequestException as e:
                    if attempt < max_retries:
                        wait_time = backoff_factor * (2 ** attempt)
                        print(f"Request failed. Retrying in {wait_time} seconds...")
                        time.sleep(wait_time)
                        continue
                    raise e
            return response
        return wrapper
    return decorator

@retry_on_rate_limit(max_retries=3)
def api_call(url):
    return requests.get(url, timeout=10)

# Usage
response = api_call('https://api.example.com/data')
```

### Example 5: Streaming JSON Data
```python
import requests
import json

def stream_json_data(url):
    """Stream and process large JSON responses line by line"""
    with requests.get(url, stream=True) as response:
        response.raise_for_status()
        
        buffer = ""
        for chunk in response.iter_content(chunk_size=1024, decode_unicode=True):
            if chunk:
                buffer += chunk
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    if line.strip():
                        try:
                            data = json.loads(line)
                            yield data
                        except json.JSONDecodeError:
                            continue
        
        # Process remaining buffer
        if buffer.strip():
            try:
                data = json.loads(buffer)
                yield data
            except json.JSONDecodeError:
                pass

# Usage
for item in stream_json_data('https://api.example.com/streaming-data'):
    print(f"Processed item: {item['id']}")
```

## Quick Reference

### Common Status Codes
- `200` - OK
- `201` - Created
- `204` - No Content
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `429` - Too Many Requests
- `500` - Internal Server Error

### Best Practices
1. Always use `response.raise_for_status()` to check for HTTP errors
2. Set timeouts to avoid hanging requests
3. Use sessions for multiple requests to the same host
4. Handle exceptions appropriately
5. Use `stream=True` for large files
6. Close files and sessions when done
7. Respect rate limits and implement backoff strategies
