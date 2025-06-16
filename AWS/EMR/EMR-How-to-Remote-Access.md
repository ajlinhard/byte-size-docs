Here's a comprehensive walkthrough to access an EMR cluster from your local machine:

## Prerequisites Setup

**Install Required Tools:**
```bash
# Install AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Install Python packages
pip install boto3 paramiko scp
```

## 1. Configure AWS Credentials

```bash
# Configure AWS CLI with your credentials
aws configure
# Enter: Access Key ID, Secret Access Key, Default region, Output format (json)

# Verify configuration
aws sts get-caller-identity
```

## 2. Locate Your EMR Cluster

```bash
# List all EMR clusters
aws emr list-clusters --active

# Get detailed cluster info
aws emr describe-cluster --cluster-id j-XXXXXXXXXXXXX
```

## 3. Set Up SSH Access

**Create/Configure Key Pair:**
```bash
# If you need to create a new key pair
aws ec2 create-key-pair --key-name my-emr-key --query 'KeyMaterial' --output text > ~/.ssh/my-emr-key.pem
chmod 400 ~/.ssh/my-emr-key.pem

# Get master node public DNS
aws emr describe-cluster --cluster-id j-XXXXXXXXXXXXX --query 'Cluster.MasterPublicDnsName'
```

**SSH into Master Node:**
```bash
ssh -i ~/.ssh/my-emr-key.pem hadoop@ec2-xx-xx-xx-xx.compute-1.amazonaws.com
```

## 4. Set Up Port Forwarding for Web UIs

```bash
# Forward ports for Spark, Yarn, and Jupyter
ssh -i ~/.ssh/my-emr-key.pem -L 8080:localhost:8080 -L 8088:localhost:8088 -L 8888:localhost:8888 hadoop@your-master-dns
```

## 5. Python Access via Boto3

**Create a Python script for EMR interaction:**
[Python Code](https://github.com/ajlinhard/byte-size-docs/blob/main/AWS/EMR/EMR-Remote-Access.py)

## 6. VS Code Configuration

**Install VS Code Extensions:**
- Python
- Remote - SSH
- AWS Toolkit

**Configure Remote SSH in VS Code:**

1. Open Command Palette (Ctrl+Shift+P)
2. Type "Remote-SSH: Add New SSH Host"
3. Enter: `ssh -i ~/.ssh/my-emr-key.pem hadoop@your-master-dns`
4. Save to SSH config file

**Create VS Code settings for EMR development:**
```yaml
{
    "python.defaultInterpreterPath": "/usr/bin/python3",
    "python.terminal.activateEnvironment": false,
    "files.associations": {
        "*.py": "python"
    },
    "terminal.integrated.env.linux": {
        "SPARK_HOME": "/usr/lib/spark",
        "HADOOP_HOME": "/usr/lib/hadoop",
        "PYTHONPATH": "/usr/lib/spark/python:/usr/lib/spark/python/lib/py4j-src.zip",
        "PYSPARK_PYTHON": "python3"
    },
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "aws.telemetry": false,
    "files.exclude": {
        "**/.git": true,
        "**/.DS_Store": true,
        "**/node_modules": true,
        "**/__pycache__": true
    }
}
```
## 7. Jupyter Notebook Access

**Start Jupyter on EMR cluster:**
```bash
# SSH into cluster and start Jupyter
ssh -i ~/.ssh/my-emr-key.pem -L 8888:localhost:8888 hadoop@your-master-dns

# On the cluster, install and start Jupyter
sudo pip install jupyter
jupyter notebook --no-browser --port=8888 --ip=0.0.0.0
```

Access Jupyter at `http://localhost:8888` in your local browser.

## 8. Common EMR Operations

**Submit Spark jobs remotely:**
```python
# Using the EMRManager class from above
emr = EMRManager()
step_id = emr.submit_spark_step(
    cluster_id='j-XXXXXXXXXXXXX',
    step_name='My Spark Job',
    spark_script_path='s3://my-bucket/spark-script.py'
)
```

**Monitor cluster and jobs:**
```bash
# Check cluster status
aws emr describe-cluster --cluster-id j-XXXXXXXXXXXXX --query 'Cluster.Status'

# List running steps
aws emr list-steps --cluster-id j-XXXXXXXXXXXXX --step-states RUNNING
```

## 9. Security Best Practices

- Store your private key securely with proper permissions (chmod 400)
- Use IAM roles instead of hardcoded credentials when possible
- Consider using AWS Systems Manager Session Manager for SSH access
- Restrict security group rules to only necessary ports and IP ranges
- Enable CloudTrail for API call logging

## 10. Troubleshooting Tips

**Common connection issues:**
- Verify security group allows SSH (port 22) from your IP
- Check that the key pair matches what was used to create the cluster
- Ensure the cluster is in WAITING or RUNNING state
- Verify the master node has a public IP (EMR in public subnet)

**For private clusters:**
- Use a bastion host or VPN connection
- Configure NAT gateway for outbound internet access
- Set up VPC endpoints for AWS services

This setup gives you full programmatic and interactive access to your EMR cluster from your local development environment.
