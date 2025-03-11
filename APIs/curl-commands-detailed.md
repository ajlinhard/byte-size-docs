# Comprehensive cURL Command Reference

## 1. Basic Request Types

### GET Requests
```bash
# Simple GET request
curl https://api.example.com/users

# GET with verbose output
curl -v https://api.example.com/users

# GET with specific headers
curl -H "Accept: application/json" https://api.example.com/users
```

### POST Requests
```bash
# Basic POST with JSON data
curl -X POST https://api.example.com/users \
     -H "Content-Type: application/json" \
     -d '{"name":"John Doe", "email":"john@example.com"}'

# POST from a JSON file
curl -X POST https://api.example.com/users \
     -d @user.json
```

## 2. Comprehensive Command Options

### Request Modification Options
```bash
# -X: Specify HTTP method
curl -X GET https://api.example.com/users

# -H: Add custom headers
curl -H "Authorization: Bearer token123" \
     -H "Content-Type: application/json" \
     https://api.example.com/users

# -d: Send POST data
curl -d "username=admin&password=secret" \
     https://api.example.com/login
```

### Output and Debugging
```bash
# -i: Include response headers
curl -i https://api.example.com/users

# -v: Verbose mode (shows full request/response)
curl -v https://api.example.com/users

# -s: Silent mode (hide progress meter)
curl -s https://api.example.com/users

# -o: Save output to a specific file
curl -o output.html https://example.com

# -O: Save file with original filename
curl -O https://example.com/file.zip
```

## 3. Authentication Methods

### Basic Authentication
```bash
# Username and password
curl -u username:password https://api.example.com/secure

# Basic auth with encoded credentials
curl -H "Authorization: Basic $(echo -n 'username:password' | base64)" \
     https://api.example.com/secure
```

### Token Authentication
```bash
# Bearer Token
curl -H "Authorization: Bearer TOKEN" \
     https://api.example.com/users

# Cookie-based Authentication
curl -b "session=123456" \
     https://api.example.com/dashboard
```

## 4. Advanced Interactions

### File Uploads
```bash
# Multipart file upload
curl -F "file=@/path/to/local/file.txt" \
     -F "description=File upload" \
     https://api.example.com/upload

# Multiple file upload
curl -F "files=@file1.txt" \
     -F "files=@file2.txt" \
     https://api.example.com/multiple-upload
```

### Complex API Requests
```bash
# Full API request with multiple options
curl -X POST https://api.example.com/orders \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer token123" \
     -d '{
         "items": [
             {"product_id": 1, "quantity": 2},
             {"product_id": 2, "quantity": 1}
         ],
         "customer_id": 456
     }' \
     -v
```

## 5. Network and Connection Options

### Proxy and Connection
```bash
# Use a proxy
curl -x http://proxy.example.com:8080 \
     https://api.example.com/users

# Set connection timeout
curl --connect-timeout 10 \
     https://api.example.com/users

# Follow redirects
curl -L https://example.com
```

### SSL/TLS Options
```bash
# Ignore SSL certificate errors
curl -k https://example.com

# Specify client certificate
curl --cert client.pem \
     --key key.pem \
     https://secure.example.com
```

## 6. Advanced Parsing and Output

### JSON Parsing with jq
```bash
# Pipe cURL output to jq for JSON parsing
curl https://api.example.com/users | jq '.[0].name'

# Extract specific fields
curl https://api.example.com/users | \
    jq '.[] | {name: .name, email: .email}'
```

### Cookie Handling
```bash
# Save cookies to a file
curl -c cookies.txt https://example.com

# Send cookies from a file
curl -b cookies.txt https://example.com
```

## Comprehensive Command Breakdown

### Command Structure
`curl [options] [URL]`

### Key Options Explained
- `-X`: HTTP method
- `-H`: Custom headers
- `-d`: Send data
- `-i`: Include headers
- `-v`: Verbose mode
- `-o`: Output to file
- `-u`: User authentication
- `-b`: Send cookies
- `-F`: Multipart/form-data

## Best Practices
1. Always use HTTPS
2. Secure sensitive data
3. Use environment variables for tokens
4. Add error handling
5. Be mindful of rate limits
```

## Detailed Explanation of cURL Commands

### 1. HTTP Methods
- **GET**: Retrieve data
- **POST**: Create new resources
- **PUT**: Update existing resources
- **DELETE**: Remove resources
- **PATCH**: Partial update

### 2. Common Use Cases
- API testing
- File downloads
- Authentication testing
- Network troubleshooting
- Scripting and automation

### 3. Key Considerations
- Understand API requirements
- Handle authentication properly
- Check response codes
- Manage headers and content types

Would you like me to elaborate on any specific cURL command or provide more context about its usage in different scenarios?

Some advanced tips:
- Combine multiple cURL options
- Use with shell scripting
- Integrate with other command-line tools
- Understand different authentication mechanisms