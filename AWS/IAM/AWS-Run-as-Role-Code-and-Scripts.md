There are several ways to run a Python script on an EC2 instance under a specific IAM role. Here are the main approaches:

## 1. Instance Profile (Recommended)

The most secure and common approach is to attach an IAM role to the EC2 instance via an instance profile.

### Setting Up the IAM Role and Instance Profile

```bash
# Create the IAM role
aws iam create-role \
    --role-name EC2-SecretsAccess-Role \
    --assume-role-policy-document '{
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "ec2.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }'

# Attach policies to the role
aws iam attach-role-policy \
    --role-name EC2-SecretsAccess-Role \
    --policy-arn arn:aws:iam::aws:policy/SecretsManagerReadWrite

# Create instance profile
aws iam create-instance-profile \
    --instance-profile-name EC2-SecretsAccess-Profile

# Add role to instance profile
aws iam add-role-to-instance-profile \
    --instance-profile-name EC2-SecretsAccess-Profile \
    --role-name EC2-SecretsAccess-Role
```

### Launching EC2 with Instance Profile

```bash
# Launch EC2 instance with the instance profile
aws ec2 run-instances \
    --image-id ami-0abcdef1234567890 \
    --instance-type t3.micro \
    --iam-instance-profile Name=EC2-SecretsAccess-Profile \
    --security-group-ids sg-12345678 \
    --subnet-id subnet-12345678 \
    --user-data file://user-data.sh
```

### Python Script Using Instance Profile

```python
# app.py
import boto3
import json
from botocore.exceptions import ClientError, NoCredentialsError

def get_secrets():
    """Get secrets using instance profile - no credentials needed in code"""
    try:
        # boto3 automatically uses instance profile credentials
        client = boto3.client('secretsmanager', region_name='us-east-1')
        
        # Get database credentials
        db_secret = client.get_secret_value(SecretId='production/database')
        db_config = json.loads(db_secret['SecretString'])
        
        # Get API key
        api_secret = client.get_secret_value(SecretId='production/api-key')
        api_key = api_secret['SecretString']
        
        return {
            'database': db_config,
            'api_key': api_key
        }
        
    except NoCredentialsError:
        print("No AWS credentials found. Make sure instance has proper IAM role.")
        raise
    except ClientError as e:
        print(f"Error accessing secrets: {e}")
        raise

def main():
    try:
        secrets = get_secrets()
        print("Successfully retrieved secrets")
        
        # Use secrets in your application
        # connect_to_database(secrets['database'])
        # call_external_api(secrets['api_key'])
        
    except Exception as e:
        print(f"Application error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
```

## 2. Assume Role from Instance Profile

If you need to assume a different role than the one attached to the instance:

```python
# assume_role_app.py
import boto3
import json
from botocore.exceptions import ClientError
from datetime import datetime, timedelta

class RoleManager:
    def __init__(self):
        self.sts_client = boto3.client('sts')
        self.assumed_credentials = None
        self.credentials_expire = None
    
    def assume_role(self, role_arn, session_name=None):
        """Assume a specific role"""
        if not session_name:
            session_name = f"python-script-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        try:
            response = self.sts_client.assume_role(
                RoleArn=role_arn,
                RoleSessionName=session_name,
                DurationSeconds=3600  # 1 hour
            )
            
            self.assumed_credentials = response['Credentials']
            self.credentials_expire = response['Credentials']['Expiration']
            
            return self.assumed_credentials
            
        except ClientError as e:
            print(f"Failed to assume role {role_arn}: {e}")
            raise
    
    def get_client_with_assumed_role(self, service_name, role_arn, region='us-east-1'):
        """Get AWS client using assumed role credentials"""
        
        # Check if we need to refresh credentials
        if (not self.assumed_credentials or 
            datetime.now(self.credentials_expire.tzinfo) >= self.credentials_expire - timedelta(minutes=5)):
            
            self.assume_role(role_arn)
        
        return boto3.client(
            service_name,
            region_name=region,
            aws_access_key_id=self.assumed_credentials['AccessKeyId'],
            aws_secret_access_key=self.assumed_credentials['SecretAccessKey'],
            aws_session_token=self.assumed_credentials['SessionToken']
        )

def main():
    role_manager = RoleManager()
    
    # Assume specific role for secrets access
    secrets_role_arn = "arn:aws:iam::123456789012:role/ProductionSecretsRole"
    
    try:
        # Get secrets manager client with assumed role
        secrets_client = role_manager.get_client_with_assumed_role(
            'secretsmanager', 
            secrets_role_arn
        )
        
        # Now use the client with assumed role permissions
        response = secrets_client.get_secret_value(SecretId='production/database')
        secrets = json.loads(response['SecretString'])
        
        print("Successfully retrieved secrets with assumed role")
        
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
```

## 3. Cross-Account Role Assumption

For accessing resources in different AWS accounts:

```python
# cross_account_app.py
import boto3
import json
import os
from botocore.exceptions import ClientError

class CrossAccountRoleManager:
    def __init__(self):
        self.sts_client = boto3.client('sts')
    
    def assume_cross_account_role(self, role_arn, external_id=None):
        """Assume role in different AWS account"""
        
        assume_role_kwargs = {
            'RoleArn': role_arn,
            'RoleSessionName': f'cross-account-{os.getenv("HOSTNAME", "unknown")}',
            'DurationSeconds': 3600
        }
        
        # Add external ID if provided (for additional security)
        if external_id:
            assume_role_kwargs['ExternalId'] = external_id
        
        try:
            response = self.sts_client.assume_role(**assume_role_kwargs)
            return response['Credentials']
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'AccessDenied':
                print("Access denied. Check role trust policy and permissions.")
            elif error_code == 'InvalidUserID.NotFound':
                print("Role ARN not found or invalid.")
            else:
                print(f"Error assuming role: {e}")
            raise
    
    def get_secrets_from_account(self, role_arn, secret_name, region='us-east-1', external_id=None):
        """Get secrets from different AWS account"""
        
        # Assume role in target account
        credentials = self.assume_cross_account_role(role_arn, external_id)
        
        # Create secrets manager client with assumed role credentials
        secrets_client = boto3.client(
            'secretsmanager',
            region_name=region,
            aws_access_key_id=credentials['AccessKeyId'],
            aws_secret_access_key=credentials['SecretAccessKey'],
            aws_session_token=credentials['SessionToken']
        )
        
        # Get the secret
        try:
            response = secrets_client.get_secret_value(SecretId=secret_name)
            return json.loads(response['SecretString'])
        except json.JSONDecodeError:
            return response['SecretString']

def main():
    # Configuration
    target_account_role = "arn:aws:iam::987654321098:role/CrossAccountSecretsRole"
    secret_name = "production/shared-database"
    external_id = os.getenv('EXTERNAL_ID')  # Optional additional security
    
    role_manager = CrossAccountRoleManager()
    
    try:
        secrets = role_manager.get_secrets_from_account(
            role_arn=target_account_role,
            secret_name=secret_name,
            external_id=external_id
        )
        
        print("Successfully retrieved cross-account secrets")
        # Use secrets...
        
    except Exception as e:
        print(f"Failed to get cross-account secrets: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
```

## 4. Running Script with Systemd Service

Create a systemd service to run your Python script with proper logging and restart policies:

```ini
# /etc/systemd/system/myapp.service
[Unit]
Description=My Python Application
After=network.target
StartLimitIntervalSec=0

[Service]
Type=simple
Restart=always
RestartSec=1
User=myapp
Group=myapp
WorkingDirectory=/opt/myapp
Environment=PYTHONPATH=/opt/myapp
Environment=AWS_DEFAULT_REGION=us-east-1
ExecStart=/opt/myapp/venv/bin/python /opt/myapp/app.py
StandardOutput=journal
StandardError=journal
SyslogIdentifier=myapp

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/opt/myapp/logs

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start the service
sudo systemctl daemon-reload
sudo systemctl enable myapp.service
sudo systemctl start myapp.service

# Check status
sudo systemctl status myapp.service

# View logs
sudo journalctl -u myapp.service -f
```

## 5. User Data Script for Automated Setup

```bash
#!/bin/bash
# user-data.sh - Runs when EC2 instance starts

# Update system
yum update -y

# Install Python and pip
yum install -y python3 python3-pip git

# Create application user
useradd -m -s /bin/bash myapp

# Create application directory
mkdir -p /opt/myapp
chown myapp:myapp /opt/myapp

# Clone application code (or copy from S3)
sudo -u myapp git clone https://github.com/yourorg/yourapp.git /opt/myapp

# Install Python dependencies
cd /opt/myapp
sudo -u myapp python3 -m venv venv
sudo -u myapp ./venv/bin/pip install -r requirements.txt

# Install application as systemd service
cp /opt/myapp/deploy/myapp.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable myapp.service
systemctl start myapp.service

# Install CloudWatch agent for logging
wget https://s3.amazonaws.com/amazoncloudwatch-agent/amazon_linux/amd64/latest/amazon-cloudwatch-agent.rpm
rpm -U ./amazon-cloudwatch-agent.rpm

# Configure CloudWatch agent
cat > /opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json << 'EOF'
{
    "logs": {
        "logs_collected": {
            "files": {
                "collect_list": [
                    {
                        "file_path": "/var/log/messages",
                        "log_group_name": "/aws/ec2/myapp",
                        "log_stream_name": "{instance_id}/system"
                    }
                ]
            }
        }
    }
}
EOF

# Start CloudWatch agent
/opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
    -a fetch-config -m ec2 -s \
    -c file:/opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json
```

## 6. Terraform Configuration

```hcl
# main.tf
# IAM Role for EC2
resource "aws_iam_role" "ec2_role" {
  name = "ec2-python-app-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })
}

# IAM Policy for Secrets Manager
resource "aws_iam_policy" "secrets_policy" {
  name = "ec2-secrets-policy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Resource = [
          "arn:aws:secretsmanager:${var.aws_region}:${data.aws_caller_identity.current.account_id}:secret:production/*"
        ]
      }
    ]
  })
}

# Attach policy to role
resource "aws_iam_role_policy_attachment" "secrets_policy_attachment" {
  role       = aws_iam_role.ec2_role.name
  policy_arn = aws_iam_policy.secrets_policy.arn
}

# Instance Profile
resource "aws_iam_instance_profile" "ec2_profile" {
  name = "ec2-python-app-profile"
  role = aws_iam_role.ec2_role.name
}

# EC2 Instance
resource "aws_instance" "python_app" {
  ami                    = data.aws_ami.amazon_linux.id
  instance_type          = "t3.micro"
  iam_instance_profile   = aws_iam_instance_profile.ec2_profile.name
  vpc_security_group_ids = [aws_security_group.app_sg.id]
  subnet_id              = var.subnet_id
  
  user_data = base64encode(file("user-data.sh"))
  
  tags = {
    Name = "python-app-server"
  }
}

# Data sources
data "aws_caller_identity" "current" {}

data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]
  
  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }
}
```

## Key Best Practices

1. **Use Instance Profiles** - Most secure, no credentials in code
2. **Principle of Least Privilege** - Grant only necessary permissions
3. **Monitor Role Usage** - Set up CloudTrail logging
4. **Rotate Credentials** - Even with roles, rotate regularly
5. **Environment Separation** - Different roles for dev/staging/production
6. **Error Handling** - Graceful handling of credential/permission errors
7. **Logging** - Log access patterns but never log credentials
8. **Health Checks** - Verify role permissions at startup

The instance profile method is the gold standard for running Python scripts on EC2 with proper IAM roles, as it eliminates the need to manage credentials entirely.
