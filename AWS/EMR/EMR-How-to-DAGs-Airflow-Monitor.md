# EMR How to Automate with Airflow, DAGs, Monitoring

## Multi-Step ETL Process with Spark on EMR

A typical ETL (Extract, Transform, Load) process on EMR can be structured as a series of steps:

### 1. Data Extraction (Extract)

```python
# PySpark example for extracting data from S3
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("EMR ETL Job") \
    .config("spark.dynamicAllocation.enabled", "true") \
    .getOrCreate()

# Extract data from various sources
raw_data = spark.read.format("csv") \
    .option("header", "true") \
    .option("inferSchema", "true") \
    .load("s3://my-bucket/raw-data/*.csv")

# Also possible to extract from databases using JDBC
db_data = spark.read.format("jdbc") \
    .option("url", "jdbc:mysql://myinstance.123456789012.us-east-1.rds.amazonaws.com:3306/mydb") \
    .option("dbtable", "customers") \
    .option("user", "username") \
    .option("password", "password") \
    .load()
```

### 2. Data Transformation (Transform)

```python
# Cleaning and transforming data
from pyspark.sql.functions import col, udf, when
from pyspark.sql.types import StringType

# Define transformations
cleaned_data = raw_data.filter(col("value") > 0) \
    .dropDuplicates() \
    .na.fill(0, ["quantity"]) \
    .withColumn("category", 
                when(col("type") == "A", "Premium")
                .when(col("type") == "B", "Standard")
                .otherwise("Basic"))

# Join with reference data
result = cleaned_data.join(
    reference_data,
    cleaned_data.product_id == reference_data.id,
    "left"
)

# Aggregate data
summary = result.groupBy("category", "region") \
    .agg({"value": "sum", "quantity": "avg"}) \
    .withColumnRenamed("sum(value)", "total_value") \
    .withColumnRenamed("avg(quantity)", "avg_quantity")
```

### 3. Data Loading (Load)

```python
# Write processed data to S3 in Parquet format
summary.write.mode("overwrite") \
    .partitionBy("category") \
    .parquet("s3://my-bucket/processed-data/")

# Optionally write to databases or other destinations
summary.write.format("jdbc") \
    .option("url", "jdbc:postgresql://myinstance.123456789012.us-east-1.rds.amazonaws.com:5432/analytics") \
    .option("dbtable", "sales_summary") \
    .option("user", "username") \
    .option("password", "password") \
    .mode("append") \
    .save()
```

### 4. Setting up a Multi-Step ETL Workflow

EMR supports chaining multiple steps in a single cluster:

```bash
aws emr add-steps \
    --cluster-id j-123456789ABC \
    --steps Type=Spark,Name="Extract Data",ActionOnFailure=CONTINUE,Args=[--class,com.example.Extract,s3://mybucket/code/etl.jar,s3://mybucket/raw/,s3://mybucket/stage/extract/] \
            Type=Spark,Name="Transform Data",ActionOnFailure=CONTINUE,Args=[--class,com.example.Transform,s3://mybucket/code/etl.jar,s3://mybucket/stage/extract/,s3://mybucket/stage/transform/] \
            Type=Spark,Name="Load Data",ActionOnFailure=CONTINUE,Args=[--class,com.example.Load,s3://mybucket/code/etl.jar,s3://mybucket/stage/transform/,s3://mybucket/processed/]
```

### 5. Orchestrating with Step Functions or Airflow

For more complex ETL workflows, you can use:

- **AWS Step Functions**: For serverless orchestration
- **Amazon MWAA (Managed Workflows for Apache Airflow)**: For complex DAGs

Example Airflow DAG:

```python
from airflow import DAG
from airflow.providers.amazon.aws.operators.emr_add_steps import EmrAddStepsOperator
from airflow.providers.amazon.aws.sensors.emr_step import EmrStepSensor
from datetime import datetime, timedelta

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

dag = DAG(
    'emr_spark_etl',
    default_args=default_args,
    description='ETL DAG using Spark on EMR',
    schedule_interval=timedelta(days=1),
    catchup=False
)

SPARK_STEPS = [
    {
        'Name': 'Extract data',
        'ActionOnFailure': 'CONTINUE',
        'HadoopJarStep': {
            'Jar': 'command-runner.jar',
            'Args': ['spark-submit', '--class', 'com.example.Extract', 
                     's3://mybucket/code/etl.jar', 
                     's3://mybucket/raw/', 's3://mybucket/stage/extract/']
        }
    },
    {
        'Name': 'Transform data',
        'ActionOnFailure': 'CONTINUE',
        'HadoopJarStep': {
            'Jar': 'command-runner.jar',
            'Args': ['spark-submit', '--class', 'com.example.Transform', 
                     's3://mybucket/code/etl.jar', 
                     's3://mybucket/stage/extract/', 's3://mybucket/stage/transform/']
        }
    },
    {
        'Name': 'Load data',
        'ActionOnFailure': 'CONTINUE',
        'HadoopJarStep': {
            'Jar': 'command-runner.jar',
            'Args': ['spark-submit', '--class', 'com.example.Load', 
                     's3://mybucket/code/etl.jar', 
                     's3://mybucket/stage/transform/', 's3://mybucket/processed/']
        }
    }
]

add_steps = EmrAddStepsOperator(
    task_id='add_steps',
    job_flow_id='j-123456789ABC',  # EMR cluster ID
    aws_conn_id='aws_default',
    steps=SPARK_STEPS,
    dag=dag
)

step_checker_extract = EmrStepSensor(
    task_id='watch_extract_step',
    job_flow_id='j-123456789ABC',
    step_id='{{ task_instance.xcom_pull("add_steps")[0] }}',
    aws_conn_id='aws_default',
    dag=dag
)

step_checker_transform = EmrStepSensor(
    task_id='watch_transform_step',
    job_flow_id='j-123456789ABC',
    step_id='{{ task_instance.xcom_pull("add_steps")[1] }}',
    aws_conn_id='aws_default',
    dag=dag
)

step_checker_load = EmrStepSensor(
    task_id='watch_load_step',
    job_flow_id='j-123456789ABC',
    step_id='{{ task_instance.xcom_pull("add_steps")[2] }}',
    aws_conn_id='aws_default',
    dag=dag
)

add_steps >> step_checker_extract >> step_checker_transform >> step_checker_load
```

## Submitting and Monitoring Spark Jobs

### Submitting Spark Jobs to EMR

#### 1. Using the EMR Step API

```bash
aws emr add-steps \
    --cluster-id j-123456789ABC \
    --steps Type=Spark,Name="Spark Application",ActionOnFailure=CONTINUE,Args=[--class,org.apache.spark.examples.SparkPi,/usr/lib/spark/examples/jars/spark-examples.jar,10]
```

#### 2. Using spark-submit Directly (via SSH to Master Node)

```bash
# SSH to master node
ssh -i /path/to/key.pem hadoop@ec2-xx-xx-xx-xx.compute-1.amazonaws.com

# Submit job
spark-submit \
    --class org.apache.spark.examples.SparkPi \
    --master yarn \
    --deploy-mode cluster \
    --executor-memory 1g \
    --num-executors 2 \
    /usr/lib/spark/examples/jars/spark-examples.jar 10
```

#### 3. Using EMR API with Python SDK (boto3)

```python
import boto3

client = boto3.client('emr', region_name='us-east-1')

response = client.add_job_flow_steps(
    JobFlowId='j-123456789ABC',
    Steps=[
        {
            'Name': 'Spark Application',
            'ActionOnFailure': 'CONTINUE',
            'HadoopJarStep': {
                'Jar': 'command-runner.jar',
                'Args': [
                    'spark-submit',
                    '--class', 'org.apache.spark.examples.SparkPi',
                    '--executor-memory', '1g',
                    '--num-executors', '2',
                    '/usr/lib/spark/examples/jars/spark-examples.jar',
                    '10'
                ]
            }
        }
    ]
)

print(f"Step ID: {response['StepIds'][0]}")
```

#### 4. For PySpark Applications

```bash
aws emr add-steps \
    --cluster-id j-123456789ABC \
    --steps Type=Spark,Name="PySpark ETL Job",ActionOnFailure=CONTINUE,Args=[--deploy-mode,cluster,s3://mybucket/scripts/etl_job.py,s3://mybucket/input/,s3://mybucket/output/]
```

### Monitoring Spark Jobs

#### 1. Through the AWS Management Console

- Navigate to EMR service > Clusters > YourCluster
- Check "Steps" tab for step status
- View application history and Spark UI through "Application history" tab
- Access logs in "Summary" tab under "Log files"

#### 2. Using AWS CLI

```bash
# Check step status
aws emr describe-step --cluster-id j-123456789ABC --step-id s-123456789ABC

# List all steps and their status
aws emr list-steps --cluster-id j-123456789ABC

# Describe cluster for overall status
aws emr describe-cluster --cluster-id j-123456789ABC
```

#### 3. Using Spark History Server

- Enable SSH tunneling to the master node:
```bash
ssh -i /path/to/key.pem -N -L 18080:localhost:18080 hadoop@master-node-dns
```
- Access Spark History Server at http://localhost:18080

#### 4. Using CloudWatch Metrics

- Monitor cluster-level metrics via CloudWatch
- Set up alarms for specific thresholds
- Create dashboards for visualizing cluster performance

#### 5. Accessing Logs

- Real-time logs on the master node:
```bash
# Application logs
less /var/log/spark/spark-history-server.log

# YARN logs
yarn logs -applicationId application_1234567890_0001
```

- Archived logs in S3 (if configured):
```bash
aws s3 ls s3://mybucket/logs/j-123456789ABC/steps/s-123456789ABC/
```
