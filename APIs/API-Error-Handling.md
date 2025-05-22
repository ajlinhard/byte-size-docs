# Common HTTP Error Codes

HTTP error codes are standardized status codes returned by web servers in response to client requests. Here are the most important and commonly encountered HTTP error codes:

## Client Error Codes (4xx)
- **400 Bad Request**: The server cannot process the request due to a client error (malformed request syntax, invalid request message, etc.)
- **401 Unauthorized**: Authentication is required and has failed or not been provided
- **403 Forbidden**: The client does not have access rights to the content
- **404 Not Found**: The server cannot find the requested resource
- **429 Too Many Requests**: The user has sent too many requests in a given amount of time ("rate limiting")

## Server Error Codes (5xx)
- **500 Internal Server Error**: A generic error message when an unexpected condition was encountered
- **502 Bad Gateway**: The server was acting as a gateway or proxy and received an invalid response from the upstream server
- **503 Service Unavailable**: The server is not ready to handle the request, often due to maintenance or overloading
- **504 Gateway Timeout**: The server was acting as a gateway or proxy and did not receive a timely response from the upstream server

## For the specific requirement about 429:
When planning for handling a 429 "Too Many Requests" error, you should implement:
- Exponential backoff retry logic
- Request rate throttling
- Request queuing
- Proper logging of rate limit headers (if provided)
- Circuit breakers to prevent cascading failures

---
# Code Example:
Here's an example of Python exception handling specifically for POST requests, covering the same HTTP error codes with POST-specific considerations:

```python
import requests
import time
import logging
import json
from requests.exceptions import HTTPError, ConnectionError, Timeout, RequestException

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def post_to_api(url, data=None, json_data=None, headers=None, max_retries=3, backoff_factor=0.5):
    """
    Make a POST request to an API with proper error handling.
    
    Args:
        url (str): The API endpoint URL
        data (dict or str, optional): Form data or raw string data to send
        json_data (dict, optional): JSON data to send in the request body
        headers (dict, optional): Request headers
        max_retries (int): Maximum number of retry attempts for 429 errors or server errors
        backoff_factor (float): Exponential backoff factor for retries
        
    Returns:
        dict: JSON response data
        
    Raises:
        Exception: Various exceptions based on error type
    """
    headers = headers or {}
    
    # If sending JSON data, set the appropriate content type
    if json_data and 'Content-Type' not in headers:
        headers['Content-Type'] = 'application/json'
    
    retry_count = 0
    
    while True:
        try:
            if json_data:
                response = requests.post(url, json=json_data, headers=headers)
            else:
                response = requests.post(url, data=data, headers=headers)
            
            # Raise an HTTPError for bad responses (4xx and 5xx)
            response.raise_for_status()
            
            # If successful, return the JSON data (or raw response if not JSON)
            try:
                return response.json()
            except ValueError:
                # Not JSON, return text
                return response.text
            
        except HTTPError as http_err:
            status_code = http_err.response.status_code
            error_body = http_err.response.text
            
            try:
                # Try to parse error body as JSON for more details
                error_details = json.loads(error_body)
                error_message = error_details.get('message', error_details.get('error', ''))
            except (ValueError, json.JSONDecodeError):
                error_message = error_body[:100] if error_body else "No details provided"
            
            if status_code == 400:
                logger.error(f"400 Bad Request: {error_message}")
                # In POST requests, 400 often means invalid data format or validation failure
                logger.debug(f"Request data: {json_data or data}")
                raise ValueError(f"Bad request: {error_message}") from http_err
                
            elif status_code == 401:
                logger.error(f"401 Unauthorized: {error_message}")
                # For POST, this could be an expired token during a long-running operation
                raise PermissionError(f"Authentication failed: {error_message}") from http_err
                
            elif status_code == 403:
                logger.error(f"403 Forbidden: {error_message}")
                # For POST, this often means insufficient permissions for the specific operation
                raise PermissionError(f"Operation not permitted: {error_message}") from http_err
                
            elif status_code == 404:
                logger.error(f"404 Not Found: Endpoint {url} not found")
                raise FileNotFoundError(f"API endpoint not found: {url}") from http_err
                
            elif status_code == 409:
                # Special handling for conflict errors (common in POST operations)
                logger.error(f"409 Conflict: {error_message}")
                raise RuntimeError(f"Resource conflict: {error_message}") from http_err
                
            elif status_code == 413:
                # Special handling for payload too large (common in POST operations)
                logger.error("413 Payload Too Large")
                raise ValueError("Request payload too large") from http_err
                
            elif status_code == 429:
                retry_count += 1
                
                # Check if we've exceeded the maximum number of retries
                if retry_count > max_retries:
                    logger.error(f"429 Too Many Requests: Rate limit exceeded after {max_retries} retries")
                    raise RuntimeError("Rate limit exceeded. Please try again later.") from http_err
                
                # Get retry-after header, or use exponential backoff
                retry_after = int(http_err.response.headers.get('Retry-After', 
                                                               backoff_factor * (2 ** (retry_count - 1))))
                
                logger.warning(f"429 Too Many Requests: Rate limited, retrying in {retry_after} seconds (attempt {retry_count}/{max_retries})")
                time.sleep(retry_after)
                continue  # Retry the request
                
            elif 500 <= status_code < 600:
                # Server errors may be transient, so implement retry with backoff
                retry_count += 1
                
                if retry_count > max_retries:
                    logger.error(f"Server error {status_code} persisted after {max_retries} retries")
                    raise HTTPError(f"Server error: {error_message}") from http_err
                
                wait_time = backoff_factor * (2 ** (retry_count - 1))
                logger.warning(f"Server error {status_code}, retrying in {wait_time} seconds (attempt {retry_count}/{max_retries})")
                time.sleep(wait_time)
                continue  # Retry the request
                
            else:
                # Handle any other HTTP errors
                logger.error(f"HTTP Error {status_code}: {error_message}")
                raise http_err
        
        except ConnectionError as conn_err:
            # Network connectivity issues - consider retrying
            retry_count += 1
            if retry_count > max_retries:
                logger.error(f"Connection failed after {max_retries} attempts")
                raise RuntimeError("Failed to connect to the server. Please check your internet connection.") from conn_err
            
            wait_time = backoff_factor * (2 ** (retry_count - 1))
            logger.warning(f"Connection error, retrying in {wait_time} seconds (attempt {retry_count}/{max_retries})")
            time.sleep(wait_time)
            continue
            
        except Timeout as timeout_err:
            # Request timed out - POST operations can take longer, retry with longer timeout
            retry_count += 1
            if retry_count > max_retries:
                logger.error(f"Request timed out after {max_retries} attempts")
                raise RuntimeError("Request timed out. The server might be under heavy load.") from timeout_err
            
            wait_time = backoff_factor * (2 ** (retry_count - 1))
            logger.warning(f"Request timed out, retrying in {wait_time} seconds (attempt {retry_count}/{max_retries})")
            time.sleep(wait_time)
            continue
            
        except Exception as err:
            # Handle any other errors
            logger.error(f"Request failed: {err}")
            raise

# Example usage
try:
    api_url = "https://api.example.com/resources"
    headers = {
        "Authorization": "Bearer YOUR_API_TOKEN",
        "Accept": "application/json"
    }
    
    # Example JSON payload for a POST request
    payload = {
        "name": "New Resource",
        "description": "This is a new resource",
        "properties": {
            "color": "blue",
            "size": "medium"
        }
    }
    
    response = post_to_api(url=api_url, json_data=payload, headers=headers)
    print("Resource created successfully:", response)
    
except ValueError as err:
    print(f"Invalid request error: {err}")
    # Handle malformed request (400) or payload too large (413)
    
except PermissionError as err:
    print(f"Permission error: {err}")
    # Handle authentication or access issues (401, 403)
    
except FileNotFoundError as err:
    print(f"Resource not found: {err}")
    # Handle missing endpoint (404)
    
except RuntimeError as err:
    print(f"Rate limit or conflict error: {err}")
    # Handle rate limiting (429) or conflict (409) issues
    
except HTTPError as err:
    print(f"HTTP error: {err}")
    # Handle any other HTTP errors
    
except RequestException as err:
    print(f"Request error: {err}")
    # Handle any other requests-related errors
    
except Exception as err:
    print(f"Unexpected error: {err}")
    # Handle any other errors
```

This POST-specific example includes several important enhancements:

1. **Content Type Handling**:
   - Automatically sets the content-type header for JSON data
   - Handles both form data and JSON payload options

2. **Error Response Parsing**:
   - Attempts to parse error responses as JSON for more detailed error information
   - Includes relevant parts of the error message in exceptions

3. **POST-Specific Status Codes**:
   - Handles 409 Conflict (common when creating resources that already exist)
   - Handles 413 Payload Too Large (common when uploading data)

4. **Idempotency Considerations**:
   - Retries server errors that might be transient
   - Enhanced network error handling (connection errors, timeouts)

5. **Error Details**:
   - Provides more context in error messages by including details from the response body
   - Logs request data for debugging

This approach is particularly useful for POST requests because they:
1. Often involve more complex data validation
2. May have resource creation conflicts
3. Typically involve larger payloads
4. May take longer to process on the server side
5. Often need to be retried with care to avoid duplicate resource creation

The example demonstrates robust error handling that helps identify and troubleshoot API integration issues while providing appropriate retry mechanisms for transient failures.
