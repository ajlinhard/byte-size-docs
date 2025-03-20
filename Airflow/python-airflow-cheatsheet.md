# Python & Airflow Pipeline Development Cheatsheet

## Python Basics for Data Processing

### Essential Libraries
```python
import pandas as pd            # Data manipulation
import numpy as np             # Numerical operations
import datetime as dt          # Date handling
import os                      # File/directory operations
import json                    # JSON processing
import requests                # API requests
import sqlalchemy              # Database connections
import logging                 # Logging
```

### Data Loading
```python
# CSV
df = pd.read_csv('file.csv')

# JSON
with open('file.json', 'r') as f:
    data = json.load(f)

# Database
from sqlalchemy import create_engine
engine = create_engine('postgresql://user:password@host:port/dbname')
df = pd.read_sql('SELECT * FROM table', engine)

# API
response = requests.get('https://api.example.com/data', 
                       headers={'Authorization': 'Bearer token'})
data = response.json()
```

### Data Transformation
```python
# Filtering
filtered_df = df[df['column'] > value]

# Grouping
grouped = df.groupby('category').agg({'value': ['sum', 'mean']})

# Joining
merged_df = pd.merge(df1, df2, on='key_column', how='left')

# Date handling
df['date'] = pd.to_datetime(df['date_str'])
df['year'] = df['date'].dt.year
df['month'] = df['date'].dt.month

# Apply functions
df['new_col'] = df['col'].apply(lambda x: my_function(x))
```

### Error Handling
```python
try:
    result = risky_operation()
except Exception as e:
    logging.error(f"Error occurred: {e}")
    # Handle error or re-raise
finally:
    # Cleanup code
```

## Apache Airflow Fundamentals

### Basic DAG Structure
```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 2, 27),
    'email': ['alerts@example.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'my_data_pipeline',
    default_args=default_args,
    description='A data processing pipeline',
    schedule_interval='0 0 * * *',  # Daily at midnight
    catchup=False,
    tags=['example'],
)

def my_processing_function(**context):
    # Your code here
    return "Success!"

task1 = PythonOperator(
    task_id='process_data',
    python_callable=my_processing_function,
    provide_context=True,
    dag=dag,
)

# Task dependencies
task1 >> task2 >> task3  # Linear workflow
task1 >> [task2, task3] >> task4  # Parallel tasks
```

### Common Operators

```python
# Python function
from airflow.operators.python import PythonOperator
python_task = PythonOperator(
    task_id='python_task',
    python_callable=my_python_function,
    op_kwargs={'param1': 'value1'},
    dag=dag,
)

# Bash command
from airflow.operators.bash import BashOperator
bash_task = BashOperator(
    task_id='bash_task',
    bash_command='echo "Hello World"',
    dag=dag,
)

# SQL query
from airflow.providers.postgres.operators.postgres import PostgresOperator
sql_task = PostgresOperator(
    task_id='sql_task',
    postgres_conn_id='postgres_default',
    sql="INSERT INTO table VALUES ('value')",
    dag=dag,
)

# Data transfer
from airflow.providers.google.cloud.transfers.postgres_to_gcs import PostgresToGCSOperator
transfer_task = PostgresToGCSOperator(
    task_id='postgres_to_gcs',
    sql='SELECT * FROM table',
    bucket='my-bucket',
    filename='data/output.json',
    postgres_conn_id='postgres_default',
    dag=dag,
)
```

### Passing Data Between Tasks

```python
# Using XCom
def task1_function(**context):
    value = compute_something()
    context['ti'].xcom_push(key='my_value', value=value)
    
def task2_function(**context):
    value = context['ti'].xcom_pull(task_ids='task1', key='my_value')
    # Process value
```

### Sensors

```python
# File sensor
from airflow.sensors.filesystem import FileSensor
file_sensor = FileSensor(
    task_id='wait_for_file',
    filepath='/path/to/file.csv',
    poke_interval=60,  # Check every minute
    timeout=60*60*5,   # Timeout after 5 hours
    mode='poke',       # Other modes: 'reschedule'
    dag=dag,
)

# External task sensor
from airflow.sensors.external_task import ExternalTaskSensor
wait_for_other_dag = ExternalTaskSensor(
    task_id='wait_for_other_dag',
    external_dag_id='other_dag',
    external_task_id='final_task',
    allowed_states=['success'],
    execution_delta=timedelta(hours=1),  # Task in other DAG completes 1 hour before
    dag=dag,
)

# Custom sensor
from airflow.sensors.base import BaseSensorOperator
class MyCustomSensor(BaseSensorOperator):
    def poke(self, context):
        # Return True when condition is met
        return check_condition()
```

## Airflow Best Practices

### Connection Management
```python
# In Airflow UI: Admin > Connections
# Or using environment variables:
# AIRFLOW_CONN_MY_CONN=my-conn-type://login:password@host:port/schema

# Using a connection in code
from airflow.hooks.base import BaseHook
conn = BaseHook.get_connection('my_conn_id')
```

### Secret Management
```python
# In Airflow UI: Admin > Variables
# Or using environment variables: AIRFLOW_VAR_MY_VAR=my_value

# Using a variable in code
from airflow.models import Variable
api_key = Variable.get("api_key", deserialize_json=False)
```

### Custom Hooks
```python
from airflow.hooks.base import BaseHook

class MyServiceHook(BaseHook):
    def __init__(self, my_conn_id='my_default_conn'):
        self.conn_id = my_conn_id
        self.connection = self.get_connection(self.conn_id)
        
    def my_method(self):
        # Implement service interactions
```

### Dynamic DAG Generation
```python
for dataset in ['sales', 'users', 'products']:
    task = PythonOperator(
        task_id=f'process_{dataset}',
        python_callable=process_data,
        op_kwargs={'dataset': dataset},
        dag=dag,
    )
    
    # Create dependencies
    upstream_task >> task >> downstream_task
```

### Task Groups
```python
from airflow.utils.task_group import TaskGroup

with TaskGroup(group_id='processing_tasks') as processing_group:
    task1 = PythonOperator(...)
    task2 = PythonOperator(...)
    task3 = PythonOperator(...)
    
    task1 >> [task2, task3]

# Reference the whole group in dependencies
start_task >> processing_group >> end_task
```

## Advanced Airflow Concepts

### Custom Operators
```python
from airflow.models.baseoperator import BaseOperator
from airflow.utils.decorators import apply_defaults

class MyCustomOperator(BaseOperator):
    @apply_defaults
    def __init__(self, my_param, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.my_param = my_param
        
    def execute(self, context):
        # Implement operator logic
        return result
```

### BranchPythonOperator (Conditional Paths)
```python
from airflow.operators.python import BranchPythonOperator

def branch_function(**context):
    if check_condition():
        return 'task_if_true'
    else:
        return 'task_if_false'
        
branch_task = BranchPythonOperator(
    task_id='branch_task',
    python_callable=branch_function,
    provide_context=True,
    dag=dag,
)

task_if_true = PythonOperator(...)
task_if_false = PythonOperator(...)

branch_task >> [task_if_true, task_if_false]
```

### Subdag Operations
```python
# Define a function that returns a DAG
def subdag_factory(parent_dag_id, child_dag_id, default_args):
    with DAG(
        dag_id=f'{parent_dag_id}.{child_dag_id}',
        default_args=default_args,
        schedule_interval=None,
    ) as dag:
        # Add tasks to the subdag
        task1 = PythonOperator(...)
        task2 = PythonOperator(...)
        
        task1 >> task2
        
    return dag

# Use the SubDagOperator
from airflow.operators.subdag import SubDagOperator
subdag_task = SubDagOperator(
    task_id='subdag',
    subdag=subdag_factory('parent_dag_id', 'subdag', default_args),
    dag=main_dag,
)
```

### Triggering DAGs
```python
# Trigger from another DAG
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
trigger_other_dag = TriggerDagRunOperator(
    task_id='trigger_other_dag',
    trigger_dag_id='other_dag_id',
    conf={'param': 'value'},  # Pass parameters
    dag=dag,
)

# Cross-DAG dependencies
from airflow.models.baseoperator import cross_downstreams
# Create dependencies between tasks in different DAGs
cross_downstreams([task1, task2], [task3, task4])
```

## Deployment & Scaling

### Docker Compose Setup
```yaml
# docker-compose.yml
version: '3'
services:
  postgres:
    image: postgres:13
    environment:
      - POSTGRES_USER=airflow
      - POSTGRES_PASSWORD=airflow
      - POSTGRES_DB=airflow
    
  webserver:
    image: apache/airflow:2.5.0
    depends_on:
      - postgres
    environment:
      - AIRFLOW__CORE__EXECUTOR=LocalExecutor
      - AIRFLOW__CORE__SQL_ALCHEMY_CONN=postgresql+psycopg2://airflow:airflow@postgres/airflow
    volumes:
      - ./dags:/opt/airflow/dags
      - ./plugins:/opt/airflow/plugins
    ports:
      - "8080:8080"
    command: webserver
    healthcheck:
      test: ["CMD", "curl", "--fail", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 5
```

### Environment Variables
```
AIRFLOW__CORE__FERNET_KEY=your_fernet_key
AIRFLOW__CORE__DAGS_FOLDER=/path/to/dags
AIRFLOW__CORE__LOAD_EXAMPLES=False
AIRFLOW__CORE__EXECUTOR=CeleryExecutor
AIRFLOW__CELERY__BROKER_URL=redis://redis:6379/0
```

### Executor Types
- **SequentialExecutor**: Default, runs one task at a time (development only)
- **LocalExecutor**: Parallelism on a single machine
- **CeleryExecutor**: Distributed task execution across worker nodes
- **KubernetesExecutor**: Dynamic worker pods in Kubernetes

### Scaling Considerations
1. Use appropriate executor for your workload
2. Increase worker count for CeleryExecutor
3. Configure resource limits (CPU/memory)
4. Enable pool for resource management
5. Control concurrency at DAG and task level
6. Use appropriate task queue assignment
7. Consider DAG serialization for many DAGs

## Monitoring & Troubleshooting

### Logging
```python
# In task function
import logging
logger = logging.getLogger(__name__)
logger.info("Processing started")
logger.error("Error occurred: %s", error_message)

# Access logs in Airflow UI:
# Browse > Task Instances > Select task > View Log
```

### Common Airflow CLI Commands
```bash
# Test a task without dependencies
airflow tasks test dag_id task_id execution_date

# Backfill DAG runs
airflow dags backfill dag_id -s 2023-01-01 -e 2023-01-31

# List DAGs
airflow dags list

# Pause/unpause a DAG
airflow dags pause/unpause dag_id

# Show DAG dependencies
airflow dags show dag_id

# Clear task instances
airflow tasks clear dag_id -t task_id -s 2023-01-01 -e 2023-01-31
```

### Health Checks
```python
# Add a health check DAG
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

with DAG('health_check', schedule_interval='*/10 * * * *', catchup=False) as dag:
    def check_connections():
        from airflow.hooks.base import BaseHook
        for conn_id in ['postgres', 'redis', 's3']:
            try:
                conn = BaseHook.get_connection(conn_id)
                # Test connection
            except Exception as e:
                raise Exception(f"Connection {conn_id} failed: {e}")
                
    health_check = PythonOperator(
        task_id='check_connections',
        python_callable=check_connections,
        dag=dag,
    )
```

### Performance Optimization
1. Use appropriate operator for the task
2. Avoid large XCom values
3. Use efficient data processing patterns
4. Implement proper error handling
5. Consider database connection pooling
6. Optimize SQL queries
7. Use appropriate catchup and backfill strategies
