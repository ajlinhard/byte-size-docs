
# Airflow Control Flow Walkthrough
Apache Airflow provides several retry and control flow mechanisms to handle task failures and manage workflow execution. Here's a comprehensive overview:

## Retry and Control Flow Options

| Mechanism | Purpose | Scope | Key Parameters |
|-----------|---------|-------|----------------|
| **Task Retries** | Automatic retry on task failure | Individual tasks | `retries`, `retry_delay`, `retry_exponential_backoff` |
| **Task Dependencies** | Define execution order and conditions | Between tasks | `>>`, `<<`, `set_upstream()`, `set_downstream()` |
| **Branching** | Conditional task execution | Workflow paths | `BranchPythonOperator`, `@task.branch` |
| **Trigger Rules** | Control when tasks should run | Task execution logic | `trigger_rule` (all_success, one_failed, etc.) |
| **Sensors** | Wait for external conditions | External dependencies | `BaseSensorOperator`, `poke_interval`, `timeout` |
| **SubDAGs/TaskGroups** | Group related tasks | Task organization | `SubDagOperator`, `TaskGroup` |
| **XComs** | Pass data between tasks | Data sharing | `xcom_push()`, `xcom_pull()` |
| **Callbacks** | Execute code on task/DAG events | Event handling | `on_success_callback`, `on_failure_callback` |
| **SLAs** | Monitor task duration | Performance monitoring | `sla`, `sla_miss_callback` |

## Python Examples

### 1. Task Retries

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'data_team',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 3,  # Default retries for all tasks
    'retry_delay': timedelta(minutes=5),
    'retry_exponential_backoff': True,
    'max_retry_delay': timedelta(hours=1)
}

dag = DAG(
    'retry_example',
    default_args=default_args,
    description='Retry mechanisms example',
    schedule_interval=timedelta(days=1),
    catchup=False,
)

def unreliable_task():
    import random
    if random.random() < 0.7:  # 70% chance of failure
        raise Exception("Random failure occurred")
    return "Success!"

# Task with custom retry settings
task_with_retries = PythonOperator(
    task_id='unreliable_task',
    python_callable=unreliable_task,
    retries=5,  # Override default retries
    retry_delay=timedelta(seconds=30),
    dag=dag,
)
```

### 2. Branching and Conditional Execution

```python
from airflow.operators.python import BranchPythonOperator
from airflow.decorators import task

def choose_branch(**context):
    # Decision logic based on current day
    from datetime import datetime
    if datetime.now().weekday() < 5:  # Monday to Friday
        return 'weekday_task'
    else:
        return 'weekend_task'

# Traditional branching
branch_task = BranchPythonOperator(
    task_id='branch_decision',
    python_callable=choose_branch,
    dag=dag,
)

weekday_task = BashOperator(
    task_id='weekday_task',
    bash_command='echo "Processing weekday data"',
    dag=dag,
)

weekend_task = BashOperator(
    task_id='weekend_task',
    bash_command='echo "Processing weekend data"',
    dag=dag,
)

# Using TaskFlow API for branching
@task.branch
def branch_with_decorator(**context):
    # Check some condition
    data_size = context['dag_run'].conf.get('data_size', 0)
    if data_size > 1000:
        return 'large_data_processing'
    else:
        return 'small_data_processing'
```

### 3. Trigger Rules

```python
from airflow.utils.trigger_rule import TriggerRule

# Task that runs only if previous task fails
cleanup_task = BashOperator(
    task_id='cleanup_on_failure',
    bash_command='echo "Cleaning up after failure"',
    trigger_rule=TriggerRule.ONE_FAILED,
    dag=dag,
)

# Task that runs regardless of upstream success/failure
final_task = BashOperator(
    task_id='final_notification',
    bash_command='echo "DAG completed"',
    trigger_rule=TriggerRule.NONE_FAILED_MIN_ONE_SUCCESS,
    dag=dag,
)

# Available trigger rules:
# - ALL_SUCCESS (default)
# - ALL_FAILED
# - ALL_DONE
# - ONE_SUCCESS
# - ONE_FAILED
# - NONE_FAILED
# - NONE_SKIPPED
# - DUMMY
```

### 4. Sensors for External Dependencies

```python
from airflow.sensors.filesystem import FileSensor
from airflow.sensors.base import BaseSensorOperator

# Wait for file to appear
file_sensor = FileSensor(
    task_id='wait_for_file',
    filepath='/data/input/daily_file.csv',
    fs_conn_id='fs_default',
    poke_interval=30,  # Check every 30 seconds
    timeout=300,  # Timeout after 5 minutes
    soft_fail=True,  # Don't fail the entire DAG if timeout
    dag=dag,
)

# Custom sensor
class DatabaseRecordSensor(BaseSensorOperator):
    def __init__(self, table_name, expected_count, **kwargs):
        super().__init__(**kwargs)
        self.table_name = table_name
        self.expected_count = expected_count
    
    def poke(self, context):
        # Custom logic to check database
        # Return True when condition is met
        from airflow.hooks.postgres_hook import PostgresHook
        hook = PostgresHook(postgres_conn_id='postgres_default')
        count = hook.get_first("SELECT COUNT(*) FROM {}".format(self.table_name))[0]
        return count >= self.expected_count

db_sensor = DatabaseRecordSensor(
    task_id='wait_for_records',
    table_name='daily_data',
    expected_count=1000,
    poke_interval=60,
    timeout=1800,
    dag=dag,
)
```

### 5. XCom for Data Passing

```python
@task
def extract_data(**context):
    # Extract and return data
    data = {'records': 1500, 'status': 'complete'}
    return data

@task
def process_data(**context):
    # Pull data from previous task
    upstream_data = context['task_instance'].xcom_pull(task_ids='extract_data')
    records = upstream_data['records']
    
    # Process based on extracted data
    if records > 1000:
        return "Large dataset processed"
    else:
        return "Small dataset processed"

# Traditional XCom usage
def push_data(**context):
    context['task_instance'].xcom_push(key='my_key', value='my_value')

def pull_data(**context):
    value = context['task_instance'].xcom_pull(key='my_key', task_ids='push_task')
    print(f"Received: {value}")
```

### 6. Callbacks and Error Handling

```python
def task_success_callback(context):
    print(f"Task {context['task_instance'].task_id} succeeded!")
    # Send notification, update external system, etc.

def task_failure_callback(context):
    print(f"Task {context['task_instance'].task_id} failed!")
    # Send alert, trigger cleanup, etc.
    exception = context.get('exception')
    if exception:
        print(f"Error: {exception}")

def sla_miss_callback(dag, task_list, blocking_task_list, slas, blocking_tis):
    print(f"SLA missed for tasks: {[task.task_id for task in task_list]}")

# Apply callbacks to tasks
monitored_task = PythonOperator(
    task_id='monitored_task',
    python_callable=lambda: print("Task executed"),
    on_success_callback=task_success_callback,
    on_failure_callback=task_failure_callback,
    sla=timedelta(minutes=30),  # Task should complete within 30 minutes
    dag=dag,
)

# DAG-level callbacks
dag.sla_miss_callback = sla_miss_callback
```

### 7. Task Groups for Organization

```python
from airflow.utils.task_group import TaskGroup

with TaskGroup("data_processing_group", dag=dag) as processing_group:
    extract = BashOperator(
        task_id='extract',
        bash_command='echo "Extracting data"'
    )
    
    transform = BashOperator(
        task_id='transform',
        bash_command='echo "Transforming data"'
    )
    
    load = BashOperator(
        task_id='load',
        bash_command='echo "Loading data"'
    )
    
    extract >> transform >> load

with TaskGroup("validation_group", dag=dag) as validation_group:
    data_quality_check = BashOperator(
        task_id='quality_check',
        bash_command='echo "Checking data quality"'
    )
    
    schema_validation = BashOperator(
        task_id='schema_check',
        bash_command='echo "Validating schema"'
    )

# Set dependencies between groups
processing_group >> validation_group
```

### 8. Complete Example with Multiple Control Mechanisms

```python
from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.bash import BashOperator
from airflow.sensors.filesystem import FileSensor
from airflow.utils.trigger_rule import TriggerRule
from datetime import datetime, timedelta

def complex_dag_example():
    dag = DAG(
        'complex_control_flow',
        default_args={
            'owner': 'data_team',
            'retries': 2,
            'retry_delay': timedelta(minutes=5),
        },
        start_date=datetime(2024, 1, 1),
        schedule_interval='@daily',
        catchup=False,
    )
    
    # Sensor to wait for input file
    wait_for_file = FileSensor(
        task_id='wait_for_input',
        filepath='/data/input/{{ ds }}.csv',
        poke_interval=60,
        timeout=300,
        dag=dag,
    )
    
    # Branch based on file size
    def check_file_size(**context):
        import os
        filepath = f"/data/input/{context['ds']}.csv"
        if os.path.getsize(filepath) > 1000000:  # 1MB
            return 'large_file_processing'
        else:
            return 'small_file_processing'
    
    branch_by_size = BranchPythonOperator(
        task_id='check_file_size',
        python_callable=check_file_size,
        dag=dag,
    )
    
    # Different processing paths
    large_file_task = BashOperator(
        task_id='large_file_processing',
        bash_command='echo "Processing large file with distributed method"',
        retries=3,
        dag=dag,
    )
    
    small_file_task = BashOperator(
        task_id='small_file_processing',
        bash_command='echo "Processing small file with single node"',
        retries=1,
        dag=dag,
    )
    
    # Cleanup task that runs on any failure
    cleanup = BashOperator(
        task_id='cleanup_on_failure',
        bash_command='echo "Cleaning up resources"',
        trigger_rule=TriggerRule.ONE_FAILED,
        dag=dag,
    )
    
    # Final task that runs after successful processing
    final_task = BashOperator(
        task_id='final_step',
        bash_command='echo "Processing completed successfully"',
        trigger_rule=TriggerRule.NONE_FAILED_MIN_ONE_SUCCESS,
        dag=dag,
    )
    
    # Set up dependencies
    wait_for_file >> branch_by_size
    branch_by_size >> [large_file_task, small_file_task]
    [large_file_task, small_file_task] >> final_task
    [large_file_task, small_file_task] >> cleanup
    
    return dag

dag = complex_dag_example()
```

These examples demonstrate the rich set of control flow and retry mechanisms available in Airflow, allowing you to build robust, fault-tolerant data pipelines that can handle various failure scenarios and execution conditions.
