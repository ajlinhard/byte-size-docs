# Authentication Methods - Code Examples
Here are simple Python examples for each authentication method. Please note there are more best practices to safely store and pull the certificates, tokens, and passwords which should be considered.

## **1. Certificate-based Authentication (mTLS)**

```python
import requests

# Using client certificate and private key
cert_file = '/path/to/client-cert.pem'
key_file = '/path/to/client-key.pem'
ca_bundle = '/path/to/ca-bundle.pem'  # Optional: CA bundle to verify server

response = requests.get(
    'https://api.example.com/secure-endpoint',
    cert=(cert_file, key_file),  # Client certificate and key
    verify=ca_bundle  # Verify server's certificate
)

print(response.json())

# Alternative: Combined cert+key in one file
combined_cert = '/path/to/client-cert-and-key.pem'
response = requests.get(
    'https://api.example.com/secure-endpoint',
    cert=combined_cert
)
```

## **2. Token-based Authentication**

```python
import requests
import jwt
from datetime import datetime, timedelta

# --- Example A: Simple Bearer Token (API Key) ---
token = 'your-api-token-here'

response = requests.get(
    'https://api.example.com/data',
    headers={'Authorization': f'Bearer {token}'}
)

print(response.json())


# --- Example B: JWT Token (creating and using) ---
# Creating a JWT
secret_key = 'your-secret-key'
payload = {
    'user_id': '123',
    'exp': datetime.utcnow() + timedelta(hours=1)
}
jwt_token = jwt.encode(payload, secret_key, algorithm='HS256')

# Using the JWT
response = requests.get(
    'https://api.example.com/data',
    headers={'Authorization': f'Bearer {jwt_token}'}
)


# --- Example C: OAuth 2.0 Flow ---
# Step 1: Get access token
auth_response = requests.post(
    'https://oauth.example.com/token',
    data={
        'grant_type': 'client_credentials',
        'client_id': 'your-client-id',
        'client_secret': 'your-client-secret'
    }
)
access_token = auth_response.json()['access_token']

# Step 2: Use access token for API calls
response = requests.get(
    'https://api.example.com/data',
    headers={'Authorization': f'Bearer {access_token}'}
)
```

## **3. SAML-based Authentication**

```python
import requests
from lxml import etree
import base64
from onelogin.saml2.auth import OneLogin_Saml2_Auth

# --- Example A: Using python3-saml library ---
# This is typically used in a web application context

def init_saml_auth(req):
    """Initialize SAML auth with settings"""
    auth = OneLogin_Saml2_Auth(req, custom_base_path='saml_settings/')
    return auth

# Simplified example of SAML flow
def saml_login():
    # Step 1: Initiate SAML request
    auth = init_saml_auth(request_data)
    return auth.login()  # Redirects to IdP

def saml_callback():
    # Step 2: Process SAML response from IdP
    auth = init_saml_auth(request_data)
    auth.process_response()
    
    if auth.is_authenticated():
        # Get user attributes from SAML assertion
        user_data = auth.get_attributes()
        session_token = auth.get_nameid()
        
        # Step 3: Use session/token for API calls
        response = requests.get(
            'https://api.example.com/data',
            headers={'Authorization': f'Bearer {session_token}'}
        )
        return response.json()


# --- Example B: Manual SAML assertion handling ---
# (Less common - usually you'd use a library)

def parse_saml_response(saml_response_b64):
    """Decode and parse SAML response"""
    saml_response = base64.b64decode(saml_response_b64)
    root = etree.fromstring(saml_response)
    
    # Extract assertion (simplified)
    namespaces = {
        'saml': 'urn:oasis:names:tc:SAML:2.0:assertion'
    }
    assertion = root.find('.//saml:Assertion', namespaces)
    
    return assertion

# After SAML authentication, typically convert to token
saml_response = 'base64-encoded-saml-response'
assertion = parse_saml_response(saml_response)

# Exchange SAML assertion for API token
token_response = requests.post(
    'https://api.example.com/auth/saml',
    data={'saml_assertion': assertion}
)
api_token = token_response.json()['access_token']

# Use token for subsequent API calls
response = requests.get(
    'https://api.example.com/data',
    headers={'Authorization': f'Bearer {api_token}'}
)
```

## **Required Libraries**

```bash
# For all examples
pip install requests

# For JWT
pip install pyjwt

# For SAML
pip install python3-saml lxml
```

## **Key Takeaways**

- **Certificates**: Passed via `cert` parameter in requests - requires PEM files
- **Tokens**: Passed in `Authorization` header - simplest to implement
- **SAML**: Complex flow involving IdP, typically results in a token for actual API use

Token-based is by far the most common for modern APIs. Certificate-based is used for high-security scenarios. SAML is primarily for enterprise SSO and web applications rather than direct API calls.
