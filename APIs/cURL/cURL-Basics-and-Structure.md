# Understanding curl Requests for Web APIs

A curl request is a command-line tool used to transfer data to or from a server, making it perfect for interacting with web-based APIs. Let me walk you through the components and payloads of curl requests, from basic to complex.

## Basic curl Request

The simplest curl request just specifies a URL:

```bash
curl https://api.example.com/endpoint
```

This performs a GET request to the specified endpoint. By default, curl will output the response to your terminal.

## Essential Components

### HTTP Methods

You can specify different HTTP methods using the `-X` flag:

```bash
curl -X GET https://api.example.com/users
curl -X POST https://api.example.com/users
curl -X PUT https://api.example.com/users/123
curl -X DELETE https://api.example.com/users/123
curl -X PATCH https://api.example.com/users/123
```

### Headers

Headers are added with the `-H` flag:

```bash
curl -H "Content-Type: application/json" https://api.example.com/users
```

Common headers include:
- Content-Type: Specifies the format of the data you're sending
- Authorization: Used for authentication
- Accept: Indicates what format you expect the response in

### Request Body

For methods like POST, PUT, or PATCH, you'll often need to send data:

```bash
curl -X POST https://api.example.com/users \
  -H "Content-Type: application/json" \
  -d '{"name": "John Doe", "email": "john@example.com"}'
```

The `-d` flag specifies data to send. For larger payloads, you can use `@` to reference a file:

```bash
curl -X POST https://api.example.com/users \
  -H "Content-Type: application/json" \
  -d @user-data.json
```

## Intermediate Features

### Authentication

#### Basic Auth
```bash
curl -u username:password https://api.example.com/secure-endpoint
```

#### Bearer Token
```bash
curl -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." https://api.example.com/secure-endpoint
```

### Handling Responses

Save the response to a file:
```bash
curl https://api.example.com/large-dataset -o data.json
```

See detailed information about the request/response:
```bash
curl -v https://api.example.com/users
```

Just see response headers:
```bash
curl -I https://api.example.com/users
```

### URL Parameters

For GET requests with query parameters:
```bash
curl "https://api.example.com/search?query=keyword&limit=10"
```

Note the quotes around the URL to prevent the shell from interpreting special characters.

## Advanced Features

### Cookies

Send cookies:
```bash
curl -b "session=abc123; user_id=456" https://api.example.com/profile
```

Save and send cookies:
```bash
curl -c cookies.txt https://api.example.com/login -d "username=user&password=pass"
curl -b cookies.txt https://api.example.com/dashboard
```

### Timeouts

Set connection timeout:
```bash
curl --connect-timeout 10 https://api.example.com/endpoint
```

Set maximum time for the whole operation:
```bash
curl --max-time 30 https://api.example.com/large-dataset
```

### Redirects

Follow redirects:
```bash
curl -L https://api.example.com/redirecting-endpoint
```

### Multipart Form Data (File Uploads)

```bash
curl -X POST https://api.example.com/upload \
  -F "profile_pic=@image.jpg" \
  -F "name=John Doe"
```

### Multiple Requests

Make multiple requests in one command:
```bash
curl https://api.example.com/endpoint1 \
     https://api.example.com/endpoint2
```

### HTTP/2 and HTTP/3

Use HTTP/2:
```bash
curl --http2 https://api.example.com/endpoint
```

Use HTTP/3 (if supported):
```bash
curl --http3 https://api.example.com/endpoint
```

## Real-World Examples

### Complete REST API Example

```bash
curl -X POST https://api.example.com/v1/orders \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Accept: application/json" \
  -d '{
    "customer_id": "cust_123456",
    "items": [
      {"product_id": "prod_789", "quantity": 2},
      {"product_id": "prod_101", "quantity": 1}
    ],
    "shipping_address": {
      "street": "123 Main St",
      "city": "Anytown",
      "state": "CA",
      "zip": "12345"
    },
    "payment_method": "pm_card_visa"
  }' \
  -v
```

### GraphQL API Request

```bash
curl -X POST https://api.example.com/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -d '{
    "query": "query { user(id: \"123\") { id name email orders { id total_amount } } }"
  }'
```
