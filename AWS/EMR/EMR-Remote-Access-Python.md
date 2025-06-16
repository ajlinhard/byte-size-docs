# EMR Remote Access Python
Here are several ways to access your EMR cluster from your local desktop using Python:

## 1. SSH Tunnel + PySpark (Most Common)

### **Step 1: Set up SSH Tunnel**
```bash
# Create SSH tunnel to EMR master node
ssh -i /path/to/your-key.pem -N -L 8998:localhost:8998 hadoop@your-emr-master-public-dns

# For Jupyter/Zeppelin access
ssh -i /path/to/your-key.pem -N -L 8888:localhost:8888 hadoop@your-emr-master-public-dns
```

### **Step 2: Connect via Livy REST API**
```python
import requests
import json

# Livy endpoint through SSH tunnel
livy_url = "http://localhost:8998"

# Create a new Spark session
session_data = {
    "kind": "pyspark",
    "conf": {
        "spark.sql.catalogImplementation": "hive"
    }
}

response = requests.post(f"{livy_url}/sessions", 
                        data=json.dumps(session_data),
                        headers={"Content-Type": "application/json"})
session_id = response.json()["id"]

# Execute code
code_data = {
    "code": "spark.sql('SHOW DATABASES').show()"
}

requests.post(f"{livy_url}/sessions/{session_id}/statements",
              data=json.dumps(code_data),
              headers={"Content-Type": "application/json"})
```

## 2. Direct PySpark Connection

### **Install PySpark Locally**
```bash
pip install pyspark boto3
```

### **Configure Spark to Connect to EMR**
```python
from pyspark.sql import SparkSession
import os

# Set AWS credentials
os.environ['AWS_ACCESS_KEY_ID'] = 'your-access-key'
os.environ['AWS_SECRET_ACCESS_KEY'] = 'your-secret-key'

# Create SparkSession pointing to EMR
spark = SparkSession.builder \
    .appName("EMR Remote Connection") \
    .config("spark.sql.catalogImplementation", "hive") \
    .config("hive.metastore.uris", "thrift://emr-master-private-ip:9083") \
    .config("spark.sql.warehouse.dir", "s3a://your-bucket/warehouse/") \
    .config("spark.hadoop.fs.s3a.access.key", "your-access-key") \
    .config("spark.hadoop.fs.s3a.secret.key", "your-secret-key") \
    .getOrCreate()
```

## 3. Using EMR Notebooks API

### **Connect to EMR Notebooks**
```python
import boto3

# Create EMR client
emr_client = boto3.client('emr', region_name='us-east-1')

# List EMR clusters
clusters = emr_client.list_clusters(ClusterStates=['RUNNING', 'WAITING'])

# Create notebook execution
notebook_execution = emr_client.start_notebook_execution(
    EditorId='your-notebook-editor-id',
    RelativePath='your-notebook.ipynb',
    ExecutionEngine={
        'Id': 'your-cluster-id',
        'Type': 'EMR'
    },
    ServiceRole='EMR_Notebooks_DefaultRole'
)
```

## 4. AWS SDK + Spark Submit

### **Submit Jobs Remotely**
```python
import boto3

def submit_spark_job(cluster_id, script_s3_path):
    emr_client = boto3.client('emr')
    
    step = {
        'Name': 'Remote Spark Job',
        'ActionOnFailure': 'CONTINUE',
        'HadoopJarStep': {
            'Jar': 'command-runner.jar',
            'Args': [
                'spark-submit',
                '--deploy-mode', 'cluster',
                script_s3_path
            ]
        }
    }
    
    response = emr_client.add_job_flow_steps(
        JobFlowId=cluster_id,
        Steps=[step]
    )
    
    return response['StepIds'][0]

# Usage
step_id = submit_spark_job('j-XXXXXXXXXXXXX', 's3://my-bucket/scripts/my_job.py')
```

## 5. Using SparkMagic (Jupyter Integration)

### **Install SparkMagic**
```bash
pip install sparkmagic
jupyter nbextension enable --py --sys-prefix widgetsnbextension
```

### **Configure SparkMagic**
```json
# ~/.sparkmagic/config.json
{
  "session_configs": {
    "driverMemory": "1000M",
    "executorCores": 2
  },
  "kernel_python_credentials": {
    "username": "",
    "password": "",
    "url": "http://localhost:8998",
    "auth": "None"
  }
}
```

### **Use in Jupyter**
```python
# In Jupyter cell
%%spark
df = spark.sql("SHOW DATABASES")
df.show()
```

## 6. Complete Example: SSH + Remote Spark

```python
import subprocess
import time
from pyspark.sql import SparkSession

class EMRConnection:
    def __init__(self, key_path, master_dns, local_port=8998):
        self.key_path = key_path
        self.master_dns = master_dns
        self.local_port = local_port
        self.ssh_process = None
        
    def create_tunnel(self):
        """Create SSH tunnel to EMR cluster"""
        cmd = [
            'ssh', '-i', self.key_path,
            '-N', '-L', f'{self.local_port}:localhost:{self.local_port}',
            f'hadoop@{self.master_dns}'
        ]
        
        self.ssh_process = subprocess.Popen(cmd)
        time.sleep(5)  # Wait for tunnel to establish
        
    def get_spark_session(self):
        """Get SparkSession through Livy"""
        # This would use the Livy REST API
        # Implementation depends on your specific setup
        pass
        
    def close_tunnel(self):
        """Close SSH tunnel"""
        if self.ssh_process:
            self.ssh_process.terminate()

# Usage
emr = EMRConnection('/path/to/key.pem', 'ec2-xx-xx-xx-xx.compute-1.amazonaws.com')
emr.create_tunnel()

try:
    # Your Spark operations here
    spark = emr.get_spark_session()
    spark.sql("SHOW DATABASES").show()
finally:
    emr.close_tunnel()
```

## Security Considerations

### **VPC and Security Groups**
- Ensure EMR cluster security groups allow connections on required ports (8998 for Livy, 9083 for Hive Metastore)
- Consider using VPN or private subnets for production

### **Authentication**
```python
# Use IAM roles instead of access keys when possible
spark = SparkSession.builder \
    .config("spark.hadoop.fs.s3a.aws.credentials.provider", 
            "com.amazonaws.auth.InstanceProfileCredentialsProvider") \
    .getOrCreate()
```

The SSH tunnel approach is most commonly used for development, while the EMR Steps API is better for production job submission. Choose the method that best fits your use case and security requirements.
