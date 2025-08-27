# Managing Credentials in Python with Key Managers

Storing sensitive credentials like AWS keys or API tokens directly in your code is a security risk. Here's how to use various key management solutions with Python to securely handle your credentials.

## 1. AWS Secrets Manager

The most native solution for AWS credentials:

```python
import boto3
import json

def get_secret(secret_name, region_name="us-east-1"):
    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )
    
    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except Exception as e:
        # Handle exceptions
        raise e
    else:
        # Decrypts secret using the associated KMS key
        if 'SecretString' in get_secret_value_response:
            secret = get_secret_value_response['SecretString']
            return json.loads(secret)
        else:
            # If binary secret
            decoded_binary_secret = base64.b64decode(get_secret_value_response['SecretBinary'])
            return json.loads(decoded_binary_secret)

# Usage example
credentials = get_secret("my-api-credentials")
api_key = credentials['api_key']
api_secret = credentials['api_secret']
```

## 2. AWS Parameter Store (SSM)

A more cost-effective alternative to Secrets Manager:

```python
import boto3

def get_parameter(parameter_name, with_decryption=True):
    ssm = boto3.client('ssm')
    response = ssm.get_parameter(
        Name=parameter_name,
        WithDecryption=with_decryption  # Decrypt if it's a SecureString
    )
    return response['Parameter']['Value']

# Usage example
api_key = get_parameter('/app/production/api_key')
```

## 3. HashiCorp Vault

For multi-cloud or on-premises environments:

```python
import hvac

def get_vault_secret(path, key):
    # Initialize the Vault client
    client = hvac.Client(url='https://vault.example.com:8200')
    
    # Authenticate with token (other auth methods available)
    client.token = 'your-vault-token'  # Better to get from env var
    
    # Read the secret
    secret_response = client.secrets.kv.v2.read_secret_version(path=path)
    
    # Return the specific key
    return secret_response['data']['data'][key]

# Usage example
api_key = get_vault_secret('secret/data/my-app', 'api_key')
```

## 4. Environment Variables

Simple but effective approach, especially with containerized applications:

```python
import os
from dotenv import load_dotenv

# Load .env file if present (for local development)
load_dotenv()

# Get credentials from environment variables
aws_access_key = os.environ.get('AWS_ACCESS_KEY_ID')
aws_secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
api_key = os.environ.get('MY_API_KEY')

# Example AWS client using these credentials
import boto3
s3_client = boto3.client(
    's3',
    aws_access_key_id=aws_access_key,
    aws_secret_access_key=aws_secret_key
)
```

## 5. Microsoft Azure Key Vault

For Azure environments:

```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

def get_azure_secret(vault_url, secret_name):
    # Create a credential using DefaultAzureCredential
    credential = DefaultAzureCredential()
    
    # Create a secret client
    client = SecretClient(vault_url=vault_url, credential=credential)
    
    # Get the secret
    secret = client.get_secret(secret_name)
    
    return secret.value

# Usage example
api_key = get_azure_secret("https://my-keyvault.vault.azure.net/", "api-key")
```

## 6. Google Cloud Secret Manager

For GCP environments:

```python
from google.cloud import secretmanager

def get_gcp_secret(project_id, secret_id, version_id="latest"):
    # Create the Secret Manager client
    client = secretmanager.SecretManagerServiceClient()
    
    # Build the resource name
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
    
    # Access the secret version
    response = client.access_secret_version(request={"name": name})
    
    # Return the decoded payload
    return response.payload.data.decode("UTF-8")

# Usage example
api_key = get_gcp_secret("my-gcp-project", "my-api-key")
```

## 7. Local Solution: Python Keyring

For development environments or desktop applications:

```python
import keyring

# Set a password
keyring.set_password("my_application", "api_key", "secret-api-key-value")

# Get a password
api_key = keyring.get_password("my_application", "api_key")
```

## Best Practices

1. **Never hardcode credentials** in your source code
2. **Use IAM roles** when running on AWS resources (EC2, Lambda, etc.)
3. **Limit permissions** to only what your application needs
4. **Rotate credentials** regularly
5. **Encrypt credentials in transit and at rest**
6. **Log access** to sensitive credentials
7. **Set proper timeouts** for cached credentials
8. **Implement secret versioning** for seamless rotation
9. **Use different credentials** across environments (dev/staging/prod)
10. **Consider a fallback chain** (e.g., check Vault first, then env vars)

## Implementation Example with Fallback Chain

```python
def get_credentials(credential_name):
    """Get credentials with a fallback mechanism."""
    
    # Try AWS Secrets Manager first
    try:
        return get_secret(f"app/{credential_name}")
    except Exception:
        pass
    
    # Then try environment variables
    env_var = os.environ.get(f"APP_{credential_name.upper()}")
    if env_var:
        return env_var
    
    # Finally try local keyring (for development)
    try:
        return keyring.get_password("my_application", credential_name)
    except Exception:
        raise Exception(f"Could not find credentials for {credential_name}")

# Usage
api_key = get_credentials("api_key")
```

This multi-layered approach ensures your application can securely access credentials across different environments while maintaining good security practices.
