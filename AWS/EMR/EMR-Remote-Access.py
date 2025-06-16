import boto3
import paramiko
import time
from botocore.exceptions import ClientError

class EMRManager:
    def __init__(self, region_name='us-east-1'):
        self.emr_client = boto3.client('emr', region_name=region_name)
        self.ec2_client = boto3.client('ec2', region_name=region_name)
        
    def list_clusters(self, states=['WAITING', 'RUNNING']):
        """List active EMR clusters"""
        try:
            response = self.emr_client.list_clusters(ClusterStates=states)
            return response['Clusters']
        except ClientError as e:
            print(f"Error listing clusters: {e}")
            return []
    
    def get_cluster_details(self, cluster_id):
        """Get detailed information about a specific cluster"""
        try:
            response = self.emr_client.describe_cluster(ClusterId=cluster_id)
            return response['Cluster']
        except ClientError as e:
            print(f"Error getting cluster details: {e}")
            return None
    
    def get_master_dns(self, cluster_id):
        """Get the master node public DNS name"""
        cluster = self.get_cluster_details(cluster_id)
        if cluster:
            return cluster.get('MasterPublicDnsName')
        return None
    
    def submit_spark_step(self, cluster_id, step_name, spark_script_path):
        """Submit a Spark job step to the cluster"""
        step = {
            'Name': step_name,
            'ActionOnFailure': 'CONTINUE',
            'HadoopJarStep': {
                'Jar': 'command-runner.jar',
                'Args': [
                    'spark-submit',
                    '--deploy-mode', 'cluster',
                    spark_script_path
                ]
            }
        }
        
        try:
            response = self.emr_client.add_job_flow_steps(
                JobFlowId=cluster_id,
                Steps=[step]
            )
            return response['StepIds'][0]
        except ClientError as e:
            print(f"Error submitting step: {e}")
            return None
    
    def get_step_status(self, cluster_id, step_id):
        """Get the status of a submitted step"""
        try:
            response = self.emr_client.describe_step(
                ClusterId=cluster_id,
                StepId=step_id
            )
            return response['Step']['Status']
        except ClientError as e:
            print(f"Error getting step status: {e}")
            return None

class EMRSSHManager:
    def __init__(self, key_file_path, username='hadoop'):
        self.key_file_path = key_file_path
        self.username = username
        self.ssh_client = None
    
    def connect(self, hostname):
        """Connect to EMR master node via SSH"""
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        try:
            self.ssh_client.connect(
                hostname=hostname,
                username=self.username,
                key_filename=self.key_file_path
            )
            print(f"Successfully connected to {hostname}")
            return True
        except Exception as e:
            print(f"Failed to connect: {e}")
            return False
    
    def execute_command(self, command):
        """Execute a command on the remote EMR cluster"""
        if not self.ssh_client:
            print("Not connected to EMR cluster")
            return None
        
        try:
            stdin, stdout, stderr = self.ssh_client.exec_command(command)
            output = stdout.read().decode('utf-8')
            error = stderr.read().decode('utf-8')
            
            return {
                'output': output,
                'error': error,
                'exit_code': stdout.channel.recv_exit_status()
            }
        except Exception as e:
            print(f"Error executing command: {e}")
            return None
    
    def upload_file(self, local_path, remote_path):
        """Upload a file to the EMR cluster"""
        if not self.ssh_client:
            print("Not connected to EMR cluster")
            return False
        
        try:
            sftp = self.ssh_client.open_sftp()
            sftp.put(local_path, remote_path)
            sftp.close()
            print(f"Successfully uploaded {local_path} to {remote_path}")
            return True
        except Exception as e:
            print(f"Error uploading file: {e}")
            return False
    
    def close(self):
        """Close SSH connection"""
        if self.ssh_client:
            self.ssh_client.close()

# Example usage
def main():
    # Initialize EMR manager
    emr = EMRManager(region_name='us-east-1')
    
    # List active clusters
    clusters = emr.list_clusters()
    if not clusters:
        print("No active clusters found")
        return
    
    # Use the first cluster (or specify your cluster ID)
    cluster_id = clusters[0]['Id']
    cluster_name = clusters[0]['Name']
    print(f"Using cluster: {cluster_name} ({cluster_id})")
    
    # Get master node DNS
    master_dns = emr.get_master_dns(cluster_id)
    if not master_dns:
        print("Could not get master node DNS")
        return
    
    print(f"Master node DNS: {master_dns}")
    
    # SSH connection example
    ssh_manager = EMRSSHManager('~/.ssh/my-emr-key.pem')
    
    if ssh_manager.connect(master_dns):
        # Execute some commands
        result = ssh_manager.execute_command('hadoop version')
        if result:
            print("Hadoop version:")
            print(result['output'])
        
        result = ssh_manager.execute_command('spark-submit --version')
        if result:
            print("Spark version:")
            print(result['output'])
        
        # Upload and run a simple Spark job
        spark_script = '''
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("TestApp").getOrCreate()
df = spark.range(1000)
print(f"Count: {df.count()}")
spark.stop()
'''
        
        # Save script locally first
        with open('/tmp/test_spark.py', 'w') as f:
            f.write(spark_script)
        
        # Upload to cluster
        ssh_manager.upload_file('/tmp/test_spark.py', '/home/hadoop/test_spark.py')
        
        # Run the script
        result = ssh_manager.execute_command('spark-submit /home/hadoop/test_spark.py')
        if result:
            print("Spark job output:")
            print(result['output'])
        
        ssh_manager.close()

if __name__ == "__main__":
    main()
