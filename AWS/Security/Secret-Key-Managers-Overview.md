# Secret Key Managers
Secret key management is a critical aspect of application security that involves storing, accessing, and using sensitive configuration data like API keys, database passwords, encryption keys, and other credentials. Let me walk you through the concepts and provide practical Python examples.
[Intro Video/Tutorial](https://www.youtube.com/watch?v=GwVWWn2ZKj0)

## The Problem with Hardcoded Secrets

First, let's look at what NOT to do:

```python
# BAD - Never do this!
import requests

# Hardcoded secrets are a major security risk
API_KEY = "sk-1234567890abcdef"
DATABASE_URL = "postgresql://user:password123@localhost/mydb"

def call_external_api():
    headers = {"Authorization": f"Bearer {API_KEY}"}
    return requests.get("https://api.example.com/data", headers=headers)
```

This approach is problematic because secrets end up in version control, are visible to anyone with code access, and can't be changed without code deployments.

## Environment Variables - The Foundation

The most common approach uses environment variables to externalize secrets:

```python
import os
import requests
from urllib.parse import urlparse

# Good - Reading from environment variables
API_KEY = os.getenv('API_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')
SECRET_KEY = os.getenv('SECRET_KEY')

# Always validate that required secrets are present
if not API_KEY:
    raise ValueError("API_KEY environment variable is required")

def call_external_api():
    headers = {"Authorization": f"Bearer {API_KEY}"}
    return requests.get("https://api.example.com/data", headers=headers)

# For database connections
def get_db_connection():
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL environment variable is required")
    
    # Parse the URL for connection details
    parsed = urlparse(DATABASE_URL)
    return {
        'host': parsed.hostname,
        'port': parsed.port,
        'database': parsed.path[1:],  # Remove leading slash
        'username': parsed.username,
        'password': parsed.password
    }
```

## Development Environment Setup

For development, you typically use `.env` files with the `python-dotenv` library:

```python
# config.py
import os
from dotenv import load_dotenv

# Load environment variables from .env file in development
load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DATABASE_URL = os.getenv('DATABASE_URL') or 'sqlite:///app.db'
    API_KEY = os.getenv('API_KEY')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # Environment-specific settings
    ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
    
    @classmethod
    def validate(cls):
        """Validate that required configuration is present"""
        required_vars = ['SECRET_KEY']
        if cls.ENVIRONMENT == 'production':
            required_vars.extend(['DATABASE_URL', 'API_KEY'])
        
        missing = [var for var in required_vars if not getattr(cls, var)]
        if missing:
            raise ValueError(f"Missing required environment variables: {missing}")

# Validate configuration on import
Config.validate()
```

Your `.env` file (never committed to version control):

```bash
# .env
SECRET_KEY=your-development-secret-key
DATABASE_URL=postgresql://user:password@localhost/devdb
API_KEY=your-dev-api-key
DEBUG=true
ENVIRONMENT=development
```

## Production Secret Management

In production, you typically use dedicated secret management services:

```python
# secrets_manager.py
import os
import json
import boto3
from functools import lru_cache

class SecretsManager:
    def __init__(self):
        self.environment = os.getenv('ENVIRONMENT', 'development')
        
    @lru_cache(maxsize=128)
    def get_secret(self, secret_name):
        """Get secret from appropriate source based on environment"""
        if self.environment == 'development':
            return self._get_from_env(secret_name)
        elif self.environment == 'production':
            return self._get_from_aws_secrets_manager(secret_name)
        else:
            raise ValueError(f"Unknown environment: {self.environment}")
    
    def _get_from_env(self, secret_name):
        """Get secret from environment variables (development)"""
        return os.getenv(secret_name)
    
    def _get_from_aws_secrets_manager(self, secret_name):
        """Get secret from AWS Secrets Manager (production)"""
        try:
            session = boto3.session.Session()
            client = session.client('secretsmanager')
            
            response = client.get_secret_value(SecretId=secret_name)
            
            # Secrets can be stored as JSON strings
            try:
                return json.loads(response['SecretString'])
            except json.JSONDecodeError:
                return response['SecretString']
                
        except Exception as e:
            raise RuntimeError(f"Failed to retrieve secret {secret_name}: {e}")

# Usage
secrets = SecretsManager()

# For simple string secrets
API_KEY = secrets.get_secret('api-key')

# For complex secrets stored as JSON
db_credentials = secrets.get_secret('database-credentials')
if isinstance(db_credentials, dict):
    DATABASE_URL = f"postgresql://{db_credentials['username']}:{db_credentials['password']}@{db_credentials['host']}/{db_credentials['database']}"
```

## Advanced Configuration Pattern

Here's a more sophisticated approach that handles multiple environments:

```python
# app_config.py
import os
import logging
from dataclasses import dataclass
from typing import Optional
from secrets_manager import SecretsManager

@dataclass
class DatabaseConfig:
    url: str
    pool_size: int = 10
    max_overflow: int = 20
    
@dataclass
class APIConfig:
    key: str
    base_url: str
    timeout: int = 30

@dataclass
class AppConfig:
    secret_key: str
    debug: bool
    environment: str
    database: DatabaseConfig
    external_api: APIConfig
    log_level: str = 'INFO'

class ConfigurationManager:
    def __init__(self):
        self.secrets = SecretsManager()
        self.environment = os.getenv('ENVIRONMENT', 'development')
        
    def load_config(self) -> AppConfig:
        """Load configuration based on environment"""
        
        # Get database configuration
        if self.environment == 'production':
            db_secrets = self.secrets.get_secret('production/database')
            db_config = DatabaseConfig(
                url=db_secrets['url'],
                pool_size=int(db_secrets.get('pool_size', 20)),
                max_overflow=int(db_secrets.get('max_overflow', 40))
            )
        else:
            db_config = DatabaseConfig(
                url=os.getenv('DATABASE_URL', 'sqlite:///dev.db'),
                pool_size=5,
                max_overflow=10
            )
        
        # Get API configuration
        api_key = self.secrets.get_secret('external-api-key')
        if not api_key:
            raise ValueError("External API key is required")
            
        api_config = APIConfig(
            key=api_key,
            base_url=os.getenv('API_BASE_URL', 'https://api.example.com'),
            timeout=int(os.getenv('API_TIMEOUT', '30'))
        )
        
        # Main application config
        return AppConfig(
            secret_key=self.secrets.get_secret('SECRET_KEY') or self._generate_secret_key(),
            debug=os.getenv('DEBUG', 'False').lower() == 'true',
            environment=self.environment,
            database=db_config,
            external_api=api_config,
            log_level=os.getenv('LOG_LEVEL', 'INFO')
        )
    
    def _generate_secret_key(self) -> str:
        """Generate a random secret key for development"""
        if self.environment == 'production':
            raise ValueError("SECRET_KEY must be explicitly set in production")
        
        import secrets
        return secrets.token_urlsafe(32)

# Initialize configuration
config_manager = ConfigurationManager()
config = config_manager.load_config()

# Configure logging
logging.basicConfig(level=getattr(logging, config.log_level))
```

## Using Configuration in Your Application

```python
# app.py
from flask import Flask
from app_config import config
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = config.secret_key

# Database setup using configuration
from sqlalchemy import create_engine
engine = create_engine(
    config.database.url,
    pool_size=config.database.pool_size,
    max_overflow=config.database.max_overflow
)

# API client using configuration
class ExternalAPIClient:
    def __init__(self):
        self.api_key = config.external_api.key
        self.base_url = config.external_api.base_url
        self.timeout = config.external_api.timeout
    
    def make_request(self, endpoint, **kwargs):
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            response = requests.get(
                url, 
                headers=headers, 
                timeout=self.timeout,
                **kwargs
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logging.error(f"API request failed: {e}")
            raise

api_client = ExternalAPIClient()
```

## Secret Rotation and Security Best Practices

```python
# secret_rotation.py
import logging
from datetime import datetime, timedelta
from secrets_manager import SecretsManager

class SecretRotationManager:
    def __init__(self):
        self.secrets = SecretsManager()
        
    def rotate_api_key(self, old_key: str, new_key: str):
        """Safely rotate API keys with overlap period"""
        
        # 1. Add new key to secrets manager
        self.secrets.update_secret('api-key-new', new_key)
        
        # 2. Update application to accept both keys during transition
        # This would typically involve updating your API client
        # to try the new key first, fall back to old key
        
        # 3. After validation period, remove old key
        logging.info("API key rotation completed")
        
    def check_secret_age(self, secret_name: str, max_age_days: int = 90):
        """Check if a secret needs rotation"""
        metadata = self.secrets.get_secret_metadata(secret_name)
        
        if metadata and 'created_date' in metadata:
            created = datetime.fromisoformat(metadata['created_date'])
            age = datetime.now() - created
            
            if age > timedelta(days=max_age_days):
                logging.warning(f"Secret {secret_name} is {age.days} days old and may need rotation")
                return True
        return False

# Health check for secrets
def validate_secrets_health():
    """Validate that all required secrets are accessible and valid"""
    try:
        secrets = SecretsManager()
        
        # Test each critical secret
        critical_secrets = ['SECRET_KEY', 'api-key', 'database-credentials']
        
        for secret_name in critical_secrets:
            value = secrets.get_secret(secret_name)
            if not value:
                raise ValueError(f"Critical secret {secret_name} is missing")
        
        logging.info("All secrets validation passed")
        return True
        
    except Exception as e:
        logging.error(f"Secrets validation failed: {e}")
        return False
```

## Key Takeaways

1. **Never hardcode secrets** in your source code
2. **Use environment variables** as the primary interface for configuration
3. **Implement different strategies** for development vs production environments
4. **Validate configuration** early in application startup
5. **Use dedicated secret management services** in production (AWS Secrets Manager, HashiCorp Vault, Azure Key Vault)
6. **Implement secret rotation** for long-lived applications
7. **Log secret access** (but never log the actual secret values)
8. **Use least privilege access** for secret retrieval
9. **Monitor and alert** on secret access patterns
10. **Have a plan for secret compromise** scenarios

This approach ensures your secrets remain secure while providing flexibility across different deployment environments.
