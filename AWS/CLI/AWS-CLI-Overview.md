# AWS Command Line Interface (CLI)

## Table of Contents

### AWS Command Line Interface (CLI)
- [What is AWS CLI?](#what-is-aws-cli)
- [Key Benefits for Developers](#key-benefits-for-developers)
- [Common Developer Use Cases](#common-developer-use-cases)
- [Installation & Basic Setup](#installation--basic-setup)
- [Example Commands](#example-commands)
- [Pro Tips](#pro-tips)

### AWS CloudShell
- [AWS CloudShell Features](#aws-cloudshell-features)
- [Key Benefits](#key-benefits)
- [What's Pre-installed](#whats-pre-installed)
- [Example Usage](#example-usage)
- [Limitations](#limitations)
- [Cost](#cost)

### Setup AWS CLI Access for a User
- [Step 1: Create Access Keys (if not done during user creation)](#step-1-create-access-keys-if-not-done-during-user-creation)
- [Step 2: Install AWS CLI](#step-2-install-aws-cli)
- [Step 3: Configure AWS CLI](#step-3-configure-aws-cli)
- [Step 4: Test Your Configuration](#step-4-test-your-configuration)
- [Alternative: Using Profiles](#alternative-using-profiles)
- [Security Best Practices](#security-best-practices)

---
# What is AWS CLI?
The AWS Command Line Interface (CLI) is a unified tool that provides a consistent interface for interacting with all parts of AWS. It enables developers to control multiple AWS services from the command line and automate them through scripts.

## Key Benefits for Developers
- **Automation**: Script repetitive tasks and integrate AWS operations into CI/CD pipelines
- **Speed**: Faster than clicking through the AWS Console for routine operations
- **Consistency**: Same commands work across different environments (local, CI/CD, servers)
- **Integration**: Easy to incorporate into existing development workflows and scripts

## Common Developer Use Cases

### Development & Testing
- **Quick resource provisioning**: Spin up EC2 instances, RDS databases, or S3 buckets for testing
- **Environment management**: Create, clone, or tear down entire environments
- **Configuration management**: Update application settings, environment variables, and parameters

### File & Data Operations
- **S3 operations**: Upload builds, sync static websites, backup databases
- **Database management**: Create snapshots, restore backups, run migrations
- **Log analysis**: Download and search CloudWatch logs for debugging

### Deployment & CI/CD
- **Application deployment**: Deploy to Lambda, ECS, or Elastic Beanstalk
- **Infrastructure as Code**: Work with CloudFormation stacks and templates
- **Container management**: Push images to ECR, update ECS services
- **Pipeline automation**: Trigger deployments, run tests, update configurations

### Monitoring & Troubleshooting
- **Real-time monitoring**: Check service status, view metrics, set alarms
- **Debugging**: Access logs, inspect configurations, trace requests
- **Performance optimization**: Analyze usage patterns and costs

### Security & Access Management
- **IAM management**: Create users, roles, and policies programmatically
- **Secret management**: Update secrets in AWS Secrets Manager or Parameter Store
- **Security auditing**: Review permissions, access patterns, and compliance

## Installation & Basic Setup
```bash
# Install (varies by OS)
pip install awscli  # or use package managers

# Configure credentials
aws configure

# Test installation
aws sts get-caller-identity
```

## Example Commands
```bash
# Deploy a Lambda function
aws lambda update-function-code --function-name myapp --zip-file fileb://myapp.zip

# Sync local files to S3
aws s3 sync ./build s3://my-website-bucket

# Get application logs
aws logs tail /aws/lambda/myapp --follow

# Update environment variables
aws lambda update-function-configuration --function-name myapp --environment Variables="{NODE_ENV=production}"
```

## Pro Tips
- Use **profiles** to manage multiple AWS accounts
- Leverage **output formats** (json, table, text) for different use cases
- Create **aliases** for frequently used commands
- Use **--dry-run** flags when available to test commands safely
- Combine with **jq** for powerful JSON processing

The AWS CLI transforms AWS from a point-and-click service into a scriptable, automatable platform that integrates seamlessly into modern development workflows.

---
# AWS CloudShell
AWS provides **AWS CloudShell**, which is a browser-based shell environment accessible directly from the AWS Management Console that comes with the AWS CLI pre-installed.

## AWS CloudShell Features

**What it is:**
- Browser-based Linux shell environment
- Launched directly from the AWS Console
- AWS CLI pre-installed and pre-configured with your credentials
- No setup required - uses your current AWS session

**How to access it:**
1. Sign in to AWS Management Console
2. Look for the **CloudShell icon** (terminal symbol) in the top navigation bar
3. Click it to launch a new CloudShell session
4. Wait a few seconds for the environment to initialize

## Key Benefits

- **No configuration needed** - automatically uses your current AWS session credentials
- **Persistent storage** - 1GB of storage per region that persists between sessions
- **Pre-installed tools** - AWS CLI, Python, Node.js, git, and other common tools
- **Multiple tabs** - Open multiple shell sessions
- **File upload/download** - Transfer files between your local machine and CloudShell

## What's Pre-installed
- AWS CLI (latest version)
- Python 3 and pip
- Node.js and npm
- Git
- Docker
- Various text editors (vim, nano)
- Common Linux utilities

## Example Usage
```bash
# These work immediately without aws configure
aws s3 ls
aws ec2 describe-instances
aws iam get-user

# Upload files via the Actions menu, then:
aws s3 cp myfile.txt s3://my-bucket/

# Install additional tools
pip install boto3
npm install -g serverless
```

## Limitations
- **1GB storage limit** per region
- **Session timeouts** after periods of inactivity
- **Regional** - storage is specific to the AWS region you're in
- **Limited compute** - not suitable for heavy processing tasks

## Cost
AWS CloudShell is **free** - no additional charges beyond the AWS services you interact with.

This is perfect for quick AWS operations when you don't want to set up CLI locally, need to run commands from anywhere, or want to avoid credential management hassles!

---
# Setup AWS CLI Access for a User
To create AWS CLI access for your admin IAM user, you'll need to configure programmatic access. Here's how:
<br>**Side Note [Best Practices for Access Keys](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html?icmpid=docs_iam_console#Using_CreateAccessKey)**

## Step 1: Create Access Keys (if not done during user creation)

1. Sign in to AWS Console with your root user
2. Go to **IAM** > **Users**
3. Click on your admin user
4. Go to **Security credentials** tab
5. Under "Access keys", click **Create access key**
6. Select **Command Line Interface (CLI)** as the use case
7. Add an optional description tag
8. Click **Create access key**
9. **Important**: Download the CSV file or copy both the Access Key ID and Secret Access Key - you won't see the secret again

## Step 2: Install AWS CLI

**On macOS:**
```bash
brew install awscli
```

**On Windows:**
Download from AWS website or use:
```cmd
msiexec.exe /i https://awscli.amazonaws.com/AWSCLIV2.msi
```

**On Linux:**
```bash
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
```

## Step 3: Configure AWS CLI

Run this command and enter your credentials:
```bash
aws configure
```

You'll be prompted for:
- **AWS Access Key ID**: [Enter your access key]
- **AWS Secret Access Key**: [Enter your secret key]
- **Default region name**: (e.g., `us-east-1`, `us-west-2`)
- **Default output format**: `json` (recommended)

## Step 4: Test Your Configuration

```bash
# Test basic connectivity
aws sts get-caller-identity

# List S3 buckets (if any exist)
aws s3 ls

# Check your identity
aws iam get-user
```

## Alternative: Using Profiles

If you want to manage multiple AWS accounts or users, you can use named profiles:

```bash
# Configure with a profile name
aws configure --profile admin-user

# Use the profile
aws s3 ls --profile admin-user

# Set as default profile
export AWS_PROFILE=admin-user  # Linux/macOS
set AWS_PROFILE=admin-user     # Windows
```

## Security Best Practices

1. **Rotate access keys regularly** (every 90 days recommended)
2. **Don't hardcode keys** in scripts - use environment variables or profiles
3. **Use least privilege** - consider creating specific roles for different tasks
4. **Monitor usage** with CloudTrail
5. **Delete unused access keys**

Your AWS CLI is now configured to use your admin IAM user instead of root credentials!
