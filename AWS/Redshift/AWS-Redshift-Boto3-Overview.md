# AWS Redshift - Boto3 Overview
Here is a comprehensive cheatsheet for working with AWS Redshift using Python and boto3, starting with a summary table of the most common functions.I've created a comprehensive AWS Redshift boto3 cheatsheet that includes:

**Key Features:**
- **Quick Reference Table** at the top with function names, parameters, purposes, and concise examples
- **Complete code examples** for all major Redshift operations
- **Production-ready patterns** with error handling and retry logic
- **Real-world scenarios** like cluster lifecycle management

**What's Covered:**
- **Cluster Management**: Create, modify, delete, and monitor clusters
- **Snapshot Operations**: Create, restore, and manage backups
- **Security**: Temporary credentials and parameter groups
- **SQL Execution**: Using Redshift Data API for serverless SQL execution
- **Monitoring**: Events, performance metrics, and status checking
- **Utility Functions**: Connection helpers and status waiters

**Advanced Features:**

---
# AWS Redshift Boto3 Python Cheatsheet

## Quick Reference Table

| Function Name | Key Parameters | Purpose | Example |
|---------------|----------------|---------|---------|
| `create_cluster()` | `ClusterIdentifier`, `NodeType`, `MasterUsername`, `MasterUserPassword` | Create a new Redshift cluster | `client.create_cluster(ClusterIdentifier='my-cluster', NodeType='dc2.large', MasterUsername='admin', MasterUserPassword='password123')` |
| `describe_clusters()` | `ClusterIdentifier` (optional) | Get cluster information | `client.describe_clusters(ClusterIdentifier='my-cluster')` |
| `modify_cluster()` | `ClusterIdentifier`, various modification params | Modify cluster settings | `client.modify_cluster(ClusterIdentifier='my-cluster', NodeType='dc2.8xlarge')` |
| `delete_cluster()` | `ClusterIdentifier`, `SkipFinalSnapshot` | Delete a cluster | `client.delete_cluster(ClusterIdentifier='my-cluster', SkipFinalSnapshot=True)` |
| `create_cluster_snapshot()` | `SnapshotIdentifier`, `ClusterIdentifier` | Create manual snapshot | `client.create_cluster_snapshot(SnapshotIdentifier='my-snapshot', ClusterIdentifier='my-cluster')` |
| `restore_from_cluster_snapshot()` | `ClusterIdentifier`, `SnapshotIdentifier` | Restore from snapshot | `client.restore_from_cluster_snapshot(ClusterIdentifier='restored-cluster', SnapshotIdentifier='my-snapshot')` |
| `get_cluster_credentials()` | `ClusterIdentifier`, `DbUser` | Get temporary credentials | `client.get_cluster_credentials(ClusterIdentifier='my-cluster', DbUser='temp_user')` |
| `authorize_cluster_security_group_ingress()` | `ClusterSecurityGroupName`, `CIDRIP` | Authorize inbound access | `client.authorize_cluster_security_group_ingress(ClusterSecurityGroupName='my-sg', CIDRIP='10.0.0.0/8')` |
| `create_cluster_parameter_group()` | `ParameterGroupName`, `ParameterGroupFamily` | Create parameter group | `client.create_cluster_parameter_group(ParameterGroupName='my-params', ParameterGroupFamily='redshift-1.0')` |
| `describe_cluster_parameters()` | `ParameterGroupName` | List parameter group settings | `client.describe_cluster_parameters(ParameterGroupName='my-params')` |
| `modify_cluster_parameter_group()` | `ParameterGroupName`, `Parameters` | Modify parameter settings | `client.modify_cluster_parameter_group(ParameterGroupName='my-params', Parameters=[...])` |
| `create_cluster_subnet_group()` | `ClusterSubnetGroupName`, `SubnetIds` | Create subnet group | `client.create_cluster_subnet_group(ClusterSubnetGroupName='my-subnet-group', SubnetIds=['subnet-123'])` |
| `describe_events()` | `SourceIdentifier`, `StartTime`, `EndTime` | Get cluster events | `client.describe_events(SourceIdentifier='my-cluster', StartTime=datetime.now() - timedelta(hours=1))` |
| `execute_statement()` | `ClusterIdentifier`, `Database`, `Sql` | Execute SQL statement | `client.execute_statement(ClusterIdentifier='my-cluster', Database='dev', Sql='SELECT 1')` |
| `describe_statement()` | `Id` | Get statement execution status | `client.describe_statement(Id='statement-id')` |
| `get_statement_result()` | `Id` | Get statement results | `client.get_statement_result(Id='statement-id')` |

## Setup and Configuration

### Installation and Imports

```python
# Install boto3
pip install boto3 psycopg2-binary pandas

# Basic imports
import boto3
import json
import pandas as pd
from datetime import datetime, timedelta
from botocore.exceptions import ClientError
```

### Initialize Redshift Client

```python
# Using default AWS credentials
redshift = boto3.client('redshift', region_name='us-east-1')

# Using specific credentials
redshift = boto3.client(
    'redshift',
    region_name='us-east-1',
    aws_access_key_id='YOUR_ACCESS_KEY',
    aws_secret_access_key='YOUR_SECRET_KEY'
)

# Using session with profile
session = boto3.Session(profile_name='your-profile')
redshift = session.client('redshift', region_name='us-east-1')

# Redshift Data API client (for SQL execution)
redshift_data = boto3.client('redshift-data', region_name='us-east-1')
```

## Cluster Management

### Create Cluster

```python
def create_redshift_cluster(cluster_id, node_type='dc2.large', num_nodes=2):
    """Create a new Redshift cluster"""
    try:
        response = redshift.create_cluster(
            ClusterIdentifier=cluster_id,
            NodeType=node_type,
            MasterUsername='admin',
            MasterUserPassword='SecurePassword123!',
            DBName='dev',
            ClusterType='multi-node' if num_nodes > 1 else 'single-node',
            NumberOfNodes=num_nodes,
            Port=5439,
            PubliclyAccessible=False,
            Encrypted=True,
            EnhancedVpcRouting=True,
            AutomatedSnapshotRetentionPeriod=7,
            PreferredMaintenanceWindow='sun:03:00-sun:04:00',
            Tags=[
                {'Key': 'Environment', 'Value': 'development'},
                {'Key': 'Project', 'Value': 'data-analytics'}
            ]
        )
        print(f"Cluster {cluster_id} creation initiated")
        return response
    except ClientError as e:
        print(f"Error creating cluster: {e}")
        return None

# Example usage
create_redshift_cluster('my-analytics-cluster', 'dc2.large', 2)
```

### Describe Clusters

```python
def get_cluster_info(cluster_id=None):
    """Get information about clusters"""
    try:
        if cluster_id:
            response = redshift.describe_clusters(ClusterIdentifier=cluster_id)
        else:
            response = redshift.describe_clusters()
        
        clusters = response['Clusters']
        cluster_info = []
        
        for cluster in clusters:
            info = {
                'ClusterIdentifier': cluster['ClusterIdentifier'],
                'ClusterStatus': cluster['ClusterStatus'],
                'NodeType': cluster['NodeType'],
                'NumberOfNodes': cluster['NumberOfNodes'],
                'Endpoint': cluster.get('Endpoint', {}).get('Address', 'N/A'),
                'Port': cluster.get('Endpoint', {}).get('Port', 'N/A'),
                'DBName': cluster['DBName'],
                'MasterUsername': cluster['MasterUsername'],
                'VpcId': cluster.get('VpcId', 'N/A'),
                'Encrypted': cluster['Encrypted'],
                'CreatedTime': cluster['ClusterCreateTime']
            }
            cluster_info.append(info)
        
        return cluster_info
    except ClientError as e:
        print(f"Error describing clusters: {e}")
        return []

# Example usage
clusters = get_cluster_info()
for cluster in clusters:
    print(f"Cluster: {cluster['ClusterIdentifier']}, Status: {cluster['ClusterStatus']}")
```

### Modify Cluster

```python
def modify_cluster_settings(cluster_id, **kwargs):
    """Modify cluster settings"""
    try:
        # Common modification parameters
        modify_params = {
            'ClusterIdentifier': cluster_id,
            'ApplyImmediately': kwargs.get('apply_immediately', True)
        }
        
        # Add parameters if provided
        if 'node_type' in kwargs:
            modify_params['NodeType'] = kwargs['node_type']
        if 'num_nodes' in kwargs:
            modify_params['NumberOfNodes'] = kwargs['num_nodes']
        if 'master_password' in kwargs:
            modify_params['MasterUserPassword'] = kwargs['master_password']
        if 'maintenance_window' in kwargs:
            modify_params['PreferredMaintenanceWindow'] = kwargs['maintenance_window']
        if 'automated_snapshot_retention' in kwargs:
            modify_params['AutomatedSnapshotRetentionPeriod'] = kwargs['automated_snapshot_retention']
        
        response = redshift.modify_cluster(**modify_params)
        print(f"Cluster {cluster_id} modification initiated")
        return response
    except ClientError as e:
        print(f"Error modifying cluster: {e}")
        return None

# Example usage
modify_cluster_settings(
    'my-analytics-cluster',
    node_type='dc2.8xlarge',
    num_nodes=4,
    apply_immediately=False
)
```

### Delete Cluster

```python
def delete_cluster(cluster_id, skip_final_snapshot=True, final_snapshot_id=None):
    """Delete a Redshift cluster"""
    try:
        params = {
            'ClusterIdentifier': cluster_id,
            'SkipFinalSnapshot': skip_final_snapshot
        }
        
        if not skip_final_snapshot and final_snapshot_id:
            params['FinalClusterSnapshotIdentifier'] = final_snapshot_id
        
        response = redshift.delete_cluster(**params)
        print(f"Cluster {cluster_id} deletion initiated")
        return response
    except ClientError as e:
        print(f"Error deleting cluster: {e}")
        return None

# Example usage
delete_cluster('my-analytics-cluster', skip_final_snapshot=False, 
               final_snapshot_id='my-final-snapshot')
```

## Snapshot Management

### Create Manual Snapshot

```python
def create_cluster_snapshot(cluster_id, snapshot_id):
    """Create a manual cluster snapshot"""
    try:
        response = redshift.create_cluster_snapshot(
            SnapshotIdentifier=snapshot_id,
            ClusterIdentifier=cluster_id,
            Tags=[
                {'Key': 'Type', 'Value': 'Manual'},
                {'Key': 'CreatedBy', 'Value': 'boto3-script'}
            ]
        )
        print(f"Snapshot {snapshot_id} creation initiated")
        return response
    except ClientError as e:
        print(f"Error creating snapshot: {e}")
        return None

# Example usage
create_cluster_snapshot('my-analytics-cluster', 'pre-upgrade-snapshot')
```

### List Snapshots

```python
def list_cluster_snapshots(cluster_id=None, snapshot_type='manual'):
    """List cluster snapshots"""
    try:
        params = {
            'SnapshotType': snapshot_type,  # 'automated' or 'manual'
            'MaxRecords': 100
        }
        
        if cluster_id:
            params['ClusterIdentifier'] = cluster_id
        
        response = redshift.describe_cluster_snapshots(**params)
        snapshots = response['Snapshots']
        
        snapshot_info = []
        for snapshot in snapshots:
            info = {
                'SnapshotIdentifier': snapshot['SnapshotIdentifier'],
                'ClusterIdentifier': snapshot['ClusterIdentifier'],
                'Status': snapshot['Status'],
                'SnapshotCreateTime': snapshot['SnapshotCreateTime'],
                'TotalBackupSizeInMegaBytes': snapshot.get('TotalBackupSizeInMegaBytes', 0),
                'SnapshotType': snapshot['SnapshotType']
            }
            snapshot_info.append(info)
        
        return snapshot_info
    except ClientError as e:
        print(f"Error listing snapshots: {e}")
        return []

# Example usage
snapshots = list_cluster_snapshots('my-analytics-cluster')
for snapshot in snapshots:
    print(f"Snapshot: {snapshot['SnapshotIdentifier']}, Status: {snapshot['Status']}")
```

### Restore from Snapshot

```python
def restore_from_snapshot(new_cluster_id, snapshot_id, node_type='dc2.large'):
    """Restore cluster from snapshot"""
    try:
        response = redshift.restore_from_cluster_snapshot(
            ClusterIdentifier=new_cluster_id,
            SnapshotIdentifier=snapshot_id,
            NodeType=node_type,
            Port=5439,
            PubliclyAccessible=False,
            Encrypted=True
        )
        print(f"Cluster {new_cluster_id} restoration from {snapshot_id} initiated")
        return response
    except ClientError as e:
        print(f"Error restoring from snapshot: {e}")
        return None

# Example usage
restore_from_snapshot('restored-cluster', 'pre-upgrade-snapshot', 'dc2.large')
```

## Security and Access Management

### Get Temporary Credentials

```python
def get_temporary_credentials(cluster_id, db_user, duration_seconds=3600):
    """Get temporary database credentials"""
    try:
        response = redshift.get_cluster_credentials(
            ClusterIdentifier=cluster_id,
            DbUser=db_user,
            DurationSeconds=duration_seconds,
            AutoCreate=True
        )
        
        return {
            'username': response['DbUser'],
            'password': response['DbPassword'],
            'expiration': response['Expiration']
        }
    except ClientError as e:
        print(f"Error getting credentials: {e}")
        return None

# Example usage
creds = get_temporary_credentials('my-analytics-cluster', 'temp_user')
if creds:
    print(f"Temporary user: {creds['username']}")
    print(f"Expires: {creds['expiration']}")
```

### Manage Parameter Groups

```python
def create_parameter_group(group_name, family='redshift-1.0', description='Custom parameter group'):
    """Create a cluster parameter group"""
    try:
        response = redshift.create_cluster_parameter_group(
            ParameterGroupName=group_name,
            ParameterGroupFamily=family,
            Description=description
        )
        print(f"Parameter group {group_name} created")
        return response
    except ClientError as e:
        print(f"Error creating parameter group: {e}")
        return None

def modify_parameter_group(group_name, parameters):
    """Modify parameter group settings"""
    try:
        response = redshift.modify_cluster_parameter_group(
            ParameterGroupName=group_name,
            Parameters=parameters
        )
        print(f"Parameter group {group_name} modified")
        return response
    except ClientError as e:
        print(f"Error modifying parameter group: {e}")
        return None

# Example usage
create_parameter_group('my-custom-params', description='Analytics workload parameters')

# Modify parameters
parameters = [
    {
        'ParameterName': 'enable_user_activity_logging',
        'ParameterValue': 'true',
        'ApplyType': 'static'
    },
    {
        'ParameterName': 'max_cursor_result_set_size',
        'ParameterValue': '1000',
        'ApplyType': 'dynamic'
    }
]
modify_parameter_group('my-custom-params', parameters)
```

## SQL Execution with Redshift Data API

### Execute SQL Statements

```python
def execute_sql(cluster_id, database, sql_statement, db_user=None):
    """Execute SQL using Redshift Data API"""
    try:
        params = {
            'ClusterIdentifier': cluster_id,
            'Database': database,
            'Sql': sql_statement
        }
        
        if db_user:
            params['DbUser'] = db_user
        else:
            # Use IAM authentication
            params['WithEvent'] = True
        
        response = redshift_data.execute_statement(**params)
        statement_id = response['Id']
        print(f"SQL execution started with ID: {statement_id}")
        return statement_id
    except ClientError as e:
        print(f"Error executing SQL: {e}")
        return None

def get_statement_status(statement_id):
    """Get status of SQL statement execution"""
    try:
        response = redshift_data.describe_statement(Id=statement_id)
        return {
            'status': response['Status'],
            'duration': response.get('Duration', 0),
            'result_rows': response.get('ResultRows', 0),
            'result_size': response.get('ResultSize', 0),
            'error': response.get('Error', None)
        }
    except ClientError as e:
        print(f"Error getting statement status: {e}")
        return None

def get_statement_results(statement_id):
    """Get results from SQL statement execution"""
    try:
        response = redshift_data.get_statement_result(Id=statement_id)
        
        # Extract column names
        columns = [col['name'] for col in response['ColumnMetadata']]
        
        # Extract data rows
        rows = []
        for record in response['Records']:
            row = []
            for field in record:
                # Handle different field types
                if 'stringValue' in field:
                    row.append(field['stringValue'])
                elif 'longValue' in field:
                    row.append(field['longValue'])
                elif 'doubleValue' in field:
                    row.append(field['doubleValue'])
                elif 'booleanValue' in field:
                    row.append(field['booleanValue'])
                elif 'isNull' in field:
                    row.append(None)
                else:
                    row.append(str(field))
            rows.append(row)
        
        return {
            'columns': columns,
            'rows': rows,
            'total_rows': len(rows)
        }
    except ClientError as e:
        print(f"Error getting statement results: {e}")
        return None

# Example usage
cluster_id = 'my-analytics-cluster'
database = 'dev'
sql = "SELECT schemaname, tablename, tableowner FROM pg_tables LIMIT 10"

# Execute SQL
statement_id = execute_sql(cluster_id, database, sql)

if statement_id:
    # Wait for completion and get results
    import time
    while True:
        status = get_statement_status(statement_id)
        if status['status'] in ['FINISHED', 'FAILED', 'ABORTED']:
            break
        time.sleep(1)
    
    if status['status'] == 'FINISHED':
        results = get_statement_results(statement_id)
        print(f"Query returned {results['total_rows']} rows")
        
        # Convert to DataFrame
        df = pd.DataFrame(results['rows'], columns=results['columns'])
        print(df.head())
```

### Batch SQL Operations

```python
def execute_batch_statements(cluster_id, database, sql_statements):
    """Execute multiple SQL statements"""
    try:
        response = redshift_data.batch_execute_statement(
            ClusterIdentifier=cluster_id,
            Database=database,
            Sqls=sql_statements
        )
        batch_id = response['Id']
        print(f"Batch execution started with ID: {batch_id}")
        return batch_id
    except ClientError as e:
        print(f"Error executing batch: {e}")
        return None

# Example usage
batch_sqls = [
    "CREATE TABLE IF NOT EXISTS test_table (id INT, name VARCHAR(50))",
    "INSERT INTO test_table VALUES (1, 'Alice'), (2, 'Bob')",
    "SELECT COUNT(*) FROM test_table"
]

batch_id = execute_batch_statements(cluster_id, database, batch_sqls)
```

## Monitoring and Events

### Get Cluster Events

```python
def get_cluster_events(cluster_id, start_time=None, end_time=None):
    """Get cluster events for monitoring"""
    try:
        params = {
            'SourceIdentifier': cluster_id,
            'SourceType': 'cluster',
            'MaxRecords': 100
        }
        
        if start_time:
            params['StartTime'] = start_time
        if end_time:
            params['EndTime'] = end_time
        
        response = redshift.describe_events(**params)
        events = response['Events']
        
        event_info = []
        for event in events:
            info = {
                'Date': event['Date'],
                'Message': event['Message'],
                'Severity': event['Severity'],
                'SourceId': event['SourceId'],
                'SourceType': event['SourceType']
            }
            event_info.append(info)
        
        return event_info
    except ClientError as e:
        print(f"Error getting events: {e}")
        return []

# Example usage - Get events from last 24 hours
start_time = datetime.now() - timedelta(days=1)
events = get_cluster_events('my-analytics-cluster', start_time=start_time)
for event in events:
    print(f"{event['Date']}: {event['Message']}")
```

### Performance Monitoring

```python
def get_cluster_performance_data(cluster_id):
    """Get performance metrics using CloudWatch"""
    cloudwatch = boto3.client('cloudwatch')
    
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=1)
    
    metrics = [
        'CPUUtilization',
        'DatabaseConnections',
        'NetworkReceiveThroughput',
        'NetworkTransmitThroughput',
        'ReadLatency',
        'WriteLatency'
    ]
    
    performance_data = {}
    
    for metric in metrics:
        try:
            response = cloudwatch.get_metric_statistics(
                Namespace='AWS/Redshift',
                MetricName=metric,
                Dimensions=[
                    {
                        'Name': 'ClusterIdentifier',
                        'Value': cluster_id
                    }
                ],
                StartTime=start_time,
                EndTime=end_time,
                Period=300,  # 5 minutes
                Statistics=['Average', 'Maximum']
            )
            performance_data[metric] = response['Datapoints']
        except ClientError as e:
            print(f"Error getting {metric}: {e}")
    
    return performance_data

# Example usage
perf_data = get_cluster_performance_data('my-analytics-cluster')
for metric, datapoints in perf_data.items():
    if datapoints:
        avg_value = sum(dp['Average'] for dp in datapoints) / len(datapoints)
        print(f"{metric}: Average = {avg_value:.2f}")
```

## Utility Functions

### Wait for Cluster Status

```python
def wait_for_cluster_status(cluster_id, desired_status='available', timeout=1800):
    """Wait for cluster to reach desired status"""
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            cluster_info = get_cluster_info(cluster_id)
            if cluster_info:
                current_status = cluster_info[0]['ClusterStatus']
                print(f"Current status: {current_status}")
                
                if current_status == desired_status:
                    print(f"Cluster {cluster_id} is now {desired_status}")
                    return True
                elif current_status in ['deleting', 'deleted']:
                    print(f"Cluster {cluster_id} is being deleted")
                    return False
                    
            time.sleep(30)  # Check every 30 seconds
        except Exception as e:
            print(f"Error checking cluster status: {e}")
            time.sleep(30)
    
    print(f"Timeout waiting for cluster {cluster_id} to reach {desired_status}")
    return False

# Example usage
wait_for_cluster_status('my-analytics-cluster', 'available')
```

### Connection Helper

```python
def get_connection_string(cluster_id):
    """Get connection string for cluster"""
    try:
        cluster_info = get_cluster_info(cluster_id)
        if cluster_info:
            cluster = cluster_info[0]
            endpoint = cluster['Endpoint']
            port = cluster['Port']
            database = cluster['DBName']
            
            conn_string = f"postgresql://{cluster['MasterUsername']}:[password]@{endpoint}:{port}/{database}"
            return conn_string
        return None
    except Exception as e:
        print(f"Error getting connection string: {e}")
        return None

# Example usage
conn_str = get_connection_string('my-analytics-cluster')
print(f"Connection string: {conn_str}")
```

## Error Handling and Best Practices

### Comprehensive Error Handling

```python
def safe_cluster_operation(operation_func, *args, **kwargs):
    """Wrapper for safe cluster operations with retry logic"""
    import time
    from botocore.exceptions import ClientError, BotoCoreError
    
    max_retries = 3
    base_delay = 1
    
    for attempt in range(max_retries):
        try:
            return operation_func(*args, **kwargs)
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            
            if error_code in ['Throttling', 'ThrottlingException']:
                if attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt)
                    print(f"Throttled, retrying in {delay} seconds...")
                    time.sleep(delay)
                    continue
            
            print(f"AWS Error [{error_code}]: {error_message}")
            return None
        except BotoCoreError as e:
            print(f"Boto3 Error: {e}")
            return None
        except Exception as e:
            print(f"Unexpected Error: {e}")
            return None
    
    print(f"Max retries exceeded for operation")
    return None

# Example usage
result = safe_cluster_operation(get_cluster_info, 'my-analytics-cluster')
```

### Configuration Management

```python
# config.py
REDSHIFT_CONFIG = {
    'region': 'us-east-1',
    'default_node_type': 'dc2.large',
    'default_port': 5439,
    'maintenance_window': 'sun:03:00-sun:04:00',
    'snapshot_retention_period': 7,
    'parameter_group_family': 'redshift-1.0'
}

# Use configuration
def create_cluster_with_config(cluster_id, **overrides):
    """Create cluster using configuration with overrides"""
    config = REDSHIFT_CONFIG.copy()
    config.update(overrides)
    
    return create_redshift_cluster(
        cluster_id=cluster_id,
        node_type=config['default_node_type'],
        **config
    )
```

## Complete Example: Cluster Lifecycle Management

```python
import boto3
import time
from datetime import datetime, timedelta

class RedshiftManager:
    def __init__(self, region='us-east-1'):
        self.redshift = boto3.client('redshift', region_name=region)
        self.redshift_data = boto3.client('redshift-data', region_name=region)
    
    def create_and_setup_cluster(self, cluster_id, setup_sql=None):
        """Complete cluster creation and setup"""
        print(f"Creating cluster: {cluster_id}")
        
        # Create cluster
        response = self.redshift.create_cluster(
            ClusterIdentifier=cluster_id,
            NodeType='dc2.large',
            MasterUsername='admin',
            MasterUserPassword='SecurePassword123!',
            DBName='analytics',
            ClusterType='single-node',
            PubliclyAccessible=False,
            Encrypted=True
        )
        
        # Wait for cluster to be available
        print("Waiting for cluster to be available...")
        if self.wait_for_cluster_status(cluster_id, 'available'):
            print("Cluster is ready!")
            
            # Run setup SQL if provided
            if setup_sql:
                print("Running setup SQL...")
                self.execute_sql_and_wait(cluster_id, 'analytics', setup_sql)
            
            return True
        
        return False
    
    def execute_sql_and_wait(self, cluster_id, database, sql):
        """Execute SQL and wait for completion"""
        statement_id = self.redshift_data.execute_statement(
            ClusterIdentifier=cluster_id,
            Database=database,
            Sql=sql
        )['Id']
        
        # Wait for completion
        while True:
            status = self.redshift_data.describe_statement(Id=statement_id)
            if status['Status'] in ['FINISHED', 'FAILED', 'ABORTED']:
                break
            time.sleep(2)
        
        if status['Status'] == 'FINISHED':
            print("SQL executed successfully")
            return True
        else:
            print(f"SQL execution failed: {status.get('Error', 'Unknown error')}")
            return False
    
    def wait_for_cluster_status(self, cluster_id, desired_status, timeout=1800):
        """Wait for cluster to reach desired status"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                response = self.redshift.describe_clusters(ClusterIdentifier=cluster_id)
                current_status = response['Clusters'][0]['ClusterStatus']
                
                if current_status == desired_status:
                    return True
                elif current_status in ['deleting', 'deleted']:
                    return False
                    
                time.sleep(30)
            except Exception as e:
                print(f"Error checking status: {e}")
                time.sleep(30)
        
        return False

# Usage example
manager = RedshiftManager()

setup_sql = """
CREATE SCHEMA IF NOT EXISTS analytics;
CREATE TABLE IF NOT EXISTS analytics.events (
    event_id BIGINT IDENTITY(1,1),
    event_time TIMESTAMP,
    user_id VARCHAR(50),
    event_type VARCHAR(100),
    properties JSON
);
"""

# Create cluster and run setup
success = manager.create_and_setup_cluster('my-analytics-cluster', setup_sql)
if success:
    print("Cluster created and configured successfully!")
```

This cheatsheet provides comprehensive coverage of AWS Redshift operations using boto3, from basic cluster management to advanced SQL execution and monitoring. Each section includes practical examples and error handling patterns for production use.
