# Databricks with Airflow
Databricks has built-in automation functionality which for self contained processing within Databricks makes something like Airflow overkill. Now there are pipelines where you might want to string a process together with Databricks, or there is an arguement for a single automation tool (centralized). In these case you have options for how you want to run the Databricks operations. [More on when to use Airflow](#When-to-use-Airflow)

You can use Apache Airflow to orchestrate and execute Databricks workbooks and code through several methods. Here are the main approaches:

## Method 1: Using Databricks Airflow Provider (Recommended)

First, install the Databricks provider:
```bash
pip install apache-airflow-providers-databricks
```

### Basic DAG Structure:
```python
from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.databricks.operators.databricks import DatabricksSubmitRunOperator
from airflow.providers.databricks.hooks.databricks import DatabricksHook

default_args = {
    'owner': 'data-team',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5)
}

dag = DAG(
    'databricks_workflow',
    default_args=default_args,
    description='Execute Databricks notebooks',
    schedule_interval='@daily',
    catchup=False
)
```

### Execute Notebook:
```python
notebook_task = DatabricksSubmitRunOperator(
    task_id='run_data_processing_notebook',
    databricks_conn_id='databricks_default',
    new_cluster={
        'spark_version': '13.3.x-scala2.12',
        'node_type_id': 'i3.xlarge',
        'num_workers': 2,
        'driver_node_type_id': 'i3.xlarge',
    },
    notebook_task={
        'notebook_path': '/Users/your-email@company.com/data_processing',
        'base_parameters': {
            'input_date': '{{ ds }}',
            'environment': 'production'
        }
    },
    dag=dag
)
```

### Execute Python Script:
```python
python_task = DatabricksSubmitRunOperator(
    task_id='run_python_script',
    databricks_conn_id='databricks_default',
    existing_cluster_id='your-cluster-id',  # Use existing cluster
    spark_python_task={
        'python_file': 'dbfs:/FileStore/scripts/data_pipeline.py',
        'parameters': ['--date', '{{ ds }}', '--env', 'prod']
    },
    dag=dag
)
```

### Execute JAR Job:
```python
jar_task = DatabricksSubmitRunOperator(
    task_id='run_jar_job',
    databricks_conn_id='databricks_default',
    new_cluster={
        'spark_version': '13.3.x-scala2.12',
        'node_type_id': 'i3.xlarge',
        'num_workers': 1
    },
    spark_jar_task={
        'main_class_name': 'com.company.DataProcessor',
        'parameters': ['{{ ds }}']
    },
    libraries=[
        {'jar': 'dbfs:/FileStore/jars/your-app.jar'}
    ],
    dag=dag
)
```

## Method 2: Using REST API Calls

```python
from airflow.providers.http.operators.http import SimpleHttpOperator
import json

# Submit job via REST API
submit_job = SimpleHttpOperator(
    task_id='submit_databricks_job',
    http_conn_id='databricks_api',
    endpoint='api/2.1/jobs/runs/submit',
    method='POST',
    headers={'Content-Type': 'application/json'},
    data=json.dumps({
        'run_name': 'Airflow triggered job {{ ds }}',
        'new_cluster': {
            'spark_version': '13.3.x-scala2.12',
            'node_type_id': 'i3.xlarge',
            'num_workers': 2
        },
        'notebook_task': {
            'notebook_path': '/Users/your-email/notebook',
            'base_parameters': {
                'date': '{{ ds }}'
            }
        }
    }),
    dag=dag
)
```

## Method 3: Using Databricks CLI in BashOperator

```python
from airflow.operators.bash import BashOperator

databricks_cli_task = BashOperator(
    task_id='run_databricks_cli',
    bash_command='''
    databricks runs submit \
        --json '{
            "run_name": "CLI Job {{ ds }}",
            "new_cluster": {
                "spark_version": "13.3.x-scala2.12",
                "node_type_id": "i3.xlarge",
                "num_workers": 1
            },
            "notebook_task": {
                "notebook_path": "/Users/your-email/notebook"
            }
        }'
    ''',
    dag=dag
)
```

## Configuration Setup

### 1. Create Databricks Connection in Airflow:
```python
# In Airflow UI: Admin > Connections
# Connection Id: databricks_default
# Connection Type: Databricks
# Host: https://your-workspace.cloud.databricks.com
# Login: your-email@company.com
# Password: your-databricks-token
```

### 2. Using Airflow Variables:
```python
from airflow.models import Variable

# Store sensitive data as Airflow Variables
databricks_token = Variable.get("databricks_token")
cluster_id = Variable.get("databricks_cluster_id")
```

## Advanced Example: Multi-Step Pipeline

```python
from airflow.providers.databricks.operators.databricks import (
    DatabricksSubmitRunOperator,
    DatabricksRunNowOperator
)

# Data ingestion notebook
ingest_data = DatabricksSubmitRunOperator(
    task_id='ingest_data',
    databricks_conn_id='databricks_default',
    existing_cluster_id='{{ var.value.databricks_cluster_id }}',
    notebook_task={
        'notebook_path': '/Workflows/01_data_ingestion',
        'base_parameters': {
            'source_path': 's3://your-bucket/raw-data/',
            'target_path': 's3://your-bucket/processed-data/',
            'date': '{{ ds }}'
        }
    },
    dag=dag
)

# Data transformation
transform_data = DatabricksSubmitRunOperator(
    task_id='transform_data',
    databricks_conn_id='databricks_default',
    existing_cluster_id='{{ var.value.databricks_cluster_id }}',
    notebook_task={
        'notebook_path': '/Workflows/02_data_transformation',
        'base_parameters': {
            'input_date': '{{ ds }}',
            'output_format': 'delta'
        }
    },
    dag=dag
)

# Run existing Databricks job
trigger_ml_job = DatabricksRunNowOperator(
    task_id='trigger_ml_training',
    databricks_conn_id='databricks_default',
    job_id=12345,  # Existing job ID in Databricks
    notebook_params={
        'training_date': '{{ ds }}',
        'model_version': 'v2.1'
    },
    dag=dag
)

# Set dependencies
ingest_data >> transform_data >> trigger_ml_job
```

## Best Practices:

1. **Use existing clusters** when possible to reduce startup time
2. **Parameterize notebooks** using Airflow templating (`{{ ds }}`, `{{ var.value.variable_name }}`)
3. **Handle failures** with appropriate retry logic and alerts
4. **Monitor costs** by setting timeouts and using appropriate cluster sizes
5. **Use secrets management** for tokens and sensitive data
6. **Test thoroughly** in development environments first

This approach gives you full control over your Databricks workloads through Airflow's scheduling and monitoring capabilities.

---
# When to Use Airflow
Great question! While Databricks workflows are powerful for Spark-centric pipelines, there are several compelling reasons to choose Airflow for orchestration:

## Multi-Platform Orchestration

**Airflow excels when you need to coordinate across multiple systems:**
- Orchestrate Databricks jobs alongside AWS Lambda, Kubernetes pods, traditional databases, APIs, and on-premise systems
- Manage complex workflows that span cloud providers (AWS + Azure + GCP)
- Integrate with legacy systems that Databricks can't directly connect to
- Coordinate between different compute engines (Databricks, Snowflake, BigQuery, etc.)

## Advanced Workflow Control

**More sophisticated branching and conditional logic:**
```python
# Complex branching based on data quality checks
data_quality_check >> [good_data_path, bad_data_path, quarantine_path]

# Dynamic task generation based on runtime conditions
for region in get_active_regions():
    create_databricks_task(region)
```

**Better handling of:**
- Complex dependencies with multiple conditions
- Dynamic workflows that change based on data or external factors
- Parallel processing with sophisticated join logic

## Enterprise Integration & Governance

**Stronger enterprise features:**
- **RBAC (Role-Based Access Control)**: Granular permissions for teams, projects, and environments
- **Audit logging**: Comprehensive tracking of who ran what, when, and why
- **Integration with enterprise auth**: LDAP, Active Directory, OAuth, SAML
- **Compliance requirements**: Better support for SOX, GDPR, HIPAA workflows
- **Change management**: Version control integration, approval workflows for production deployments

## Operational Flexibility

**More control over execution environment:**
- Run on your own infrastructure (on-premise, private cloud)
- Custom resource allocation and scaling policies
- Integration with existing monitoring and alerting systems (Datadog, New Relic, PagerDuty)
- Custom plugins and operators for specialized needs

## Cost Management & Resource Optimization

**Better cost control:**
- More granular control over when clusters spin up/down
- Ability to use spot instances and preemptible VMs more effectively
- Cross-platform resource optimization
- Better handling of long-running vs. short-burst workloads

## Specific Use Cases Where Airflow Wins

### 1. **Multi-Cloud Data Pipelines**
```python
# Extract from Salesforce API
extract_salesforce >> 
# Process in Databricks
process_in_databricks >> 
# Load to Snowflake
load_to_snowflake >> 
# Update dashboard in Tableau
refresh_tableau >> 
# Send email notifications
send_notifications
```

### 2. **Legacy System Integration**
- ETL from mainframe systems
- Integration with Oracle/SQL Server databases
- File-based workflows with SFTP/FTP
- Custom API integrations that require specialized authentication

### 3. **Complex Business Logic**
```python
# Business rule: Only run ML training if data quality > 95%
data_quality_check >> BranchPythonOperator(
    python_callable=check_quality_threshold
) >> [run_ml_training, send_quality_alert]
```

### 4. **Regulatory Compliance Workflows**
- Financial data processing with audit trails
- Healthcare data pipelines with HIPAA compliance
- Manufacturing quality control with traceability requirements

### 5. **Mixed Workload Orchestration**
- Real-time streaming (Kafka) + batch processing (Databricks)
- ML model training (Databricks) + deployment (Kubernetes)
- Data processing + report generation + email distribution

## Development & Debugging Experience

**Better for complex debugging:**
- More detailed logging and error tracking
- Ability to rerun individual tasks without rerunning entire workflow
- Better integration with IDEs and version control
- More flexible testing frameworks

## When Databricks Workflows Are Better

**Databricks workflows excel when:**
- Pure Spark/Delta Lake pipelines
- Tight integration with Databricks features (MLflow, Delta Live Tables)
- Simpler linear workflows
- Teams primarily focused on data science/analytics
- Want minimal operational overhead

## Hybrid Approach

Many organizations use both:
- **Airflow**: High-level orchestration and cross-system coordination
- **Databricks Workflows**: Databricks-specific data processing pipelines
- **Pattern**: Airflow triggers Databricks workflows as part of larger enterprise workflows

The choice often comes down to complexity, integration requirements, and organizational preferences. If your workflows extend beyond Databricks or require enterprise-grade governance, Airflow typically provides more flexibility and control.
