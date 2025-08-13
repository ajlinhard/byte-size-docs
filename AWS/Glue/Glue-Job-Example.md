# Glue Job Example
Below is an example of loading data with PySpark in AWS Glue, adding it to the catalog, and exporting it as a Delta table. Note that Delta Lake support in AWS Glue requires some specific setup. Is complete with a companion script that shows how to set up the job parameters and run additional Delta Lake operations:

#### Jump to Scripts:
- [PySpark Delta Lake ETL Job](#PySpark-Delta-Lake-ETL-Job)
- [Job Setup with Delta Lake Config](#Job-Setup-with-Delta-Lake-Config)

## Key Points About This Example

**Delta Lake Integration**: The example shows how to configure AWS Glue 4.0 with Delta Lake support, including the required JAR files and Spark configurations.

**Complete ETL Pipeline**: The main script demonstrates loading data (from catalog or creating sample data), transforming it, writing to Delta Lake, and registering in the Glue Data Catalog.

**Catalog Integration**: The `register_table_in_catalog()` function explicitly adds the Delta table metadata to the Glue Data Catalog, including partition information and Delta-specific parameters.

**Data Quality**: Includes basic data quality checks and shows how to perform merge operations (upserts) with Delta Lake.

**Advanced Operations**: The second script shows time travel, optimization, schema evolution, and other Delta Lake features.

## Important Setup Requirements

**AWS Glue 4.0**: You must use Glue 4.0 or later for proper Delta Lake support with Spark 3.3.

**JAR Dependencies**: You need to upload Delta Lake JAR files to S3 and reference them in your job configuration.

**IAM Permissions**: Your Glue service role needs permissions for S3 access and Glue catalog operations.

**S3 Structure**: Delta Lake creates a `_delta_log` directory to track table versions and changes.

## Running the Job

1. Upload the main script to your Glue scripts S3 bucket
2. Upload required JAR files to S3
3. Create the Glue job with proper configuration (shown in the setup script)
4. Run the job with appropriate parameters

The result will be a Delta Lake table that's automatically registered in the Glue Data Catalog and can be queried through Athena, used in other Glue jobs, or accessed by any Delta Lake-compatible engine.

This approach gives you both the benefits of Delta Lake (ACID transactions, time travel, schema evolution) and integration with the AWS analytics ecosystem through the Glue Data Catalog.

# PySpark Delta Lake ETL Job
```python
import sys
import boto3
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql import DataFrame
from pyspark.sql.functions import *
from pyspark.sql.types import *
from delta.tables import *

# Get job parameters
args = getResolvedOptions(sys.argv, [
    'JOB_NAME',
    'source_database',
    'source_table', 
    'target_database',
    'target_table',
    'delta_table_path'
])

# Initialize Spark and Glue contexts
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Configure Spark for Delta Lake
spark.conf.set("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
spark.conf.set("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")

# Initialize Glue client for catalog operations
glue_client = boto3.client('glue')

def load_source_data():
    """
    Load data from Glue Data Catalog or directly from S3
    """
    try:
        # Option 1: Load from Glue Data Catalog
        datasource = glueContext.create_dynamic_frame.from_catalog(
            database = args['source_database'],
            table_name = args['source_table'],
            transformation_ctx = "datasource"
        )
        
        # Convert to Spark DataFrame
        df = datasource.toDF()
        
        print(f"Loaded {df.count()} records from catalog table: {args['source_database']}.{args['source_table']}")
        
    except Exception as e:
        print(f"Failed to load from catalog: {str(e)}")
        print("Loading sample data instead...")
        
        # Option 2: Create sample data if catalog source doesn't exist
        sample_data = [
            (1, "John Doe", "Engineering", 75000, "2023-01-15"),
            (2, "Jane Smith", "Marketing", 65000, "2023-02-01"),
            (3, "Bob Johnson", "Sales", 55000, "2023-01-20"),
            (4, "Alice Brown", "Engineering", 80000, "2023-03-01"),
            (5, "Charlie Davis", "HR", 60000, "2023-02-15")
        ]
        
        schema = StructType([
            StructField("employee_id", IntegerType(), True),
            StructField("name", StringType(), True),
            StructField("department", StringType(), True),
            StructField("salary", IntegerType(), True),
            StructField("hire_date", StringType(), True)
        ])
        
        df = spark.createDataFrame(sample_data, schema)
        
        # Convert hire_date to proper date format
        df = df.withColumn("hire_date", to_date(col("hire_date"), "yyyy-MM-dd"))
        
    return df

def transform_data(df):
    """
    Apply transformations to the data
    """
    # Add some computed columns
    transformed_df = df.withColumn(
        "annual_salary", col("salary") * 12
    ).withColumn(
        "tenure_days", datediff(current_date(), col("hire_date"))
    ).withColumn(
        "salary_band", 
        when(col("salary") >= 70000, "High")
        .when(col("salary") >= 60000, "Medium")
        .otherwise("Low")
    ).withColumn(
        "load_timestamp", current_timestamp()
    )
    
    print("Applied transformations:")
    transformed_df.printSchema()
    transformed_df.show(5)
    
    return transformed_df

def write_delta_table(df, table_path):
    """
    Write DataFrame as Delta table
    """
    try:
        # Check if Delta table already exists
        if DeltaTable.isDeltaTable(spark, table_path):
            print(f"Delta table exists at {table_path}. Performing merge operation...")
            
            # Load existing Delta table
            delta_table = DeltaTable.forPath(spark, table_path)
            
            # Perform merge (upsert) operation
            delta_table.alias("target").merge(
                df.alias("source"),
                "target.employee_id = source.employee_id"
            ).whenMatchedUpdateAll(
            ).whenNotMatchedInsertAll(
            ).execute()
            
            print("Merge operation completed successfully")
            
        else:
            print(f"Creating new Delta table at {table_path}")
            
            # Write as new Delta table with partitioning
            df.write \
                .format("delta") \
                .mode("overwrite") \
                .partitionBy("department") \
                .option("mergeSchema", "true") \
                .save(table_path)
            
            print("Delta table created successfully")
            
    except Exception as e:
        print(f"Error writing Delta table: {str(e)}")
        raise e

def register_table_in_catalog(table_path, database_name, table_name):
    """
    Register the Delta table in AWS Glue Data Catalog
    """
    try:
        # First, ensure database exists
        try:
            glue_client.get_database(Name=database_name)
            print(f"Database {database_name} already exists")
        except glue_client.exceptions.EntityNotFoundException:
            print(f"Creating database {database_name}")
            glue_client.create_database(
                DatabaseInput={
                    'Name': database_name,
                    'Description': 'Database for Delta Lake tables'
                }
            )
        
        # Read the Delta table to get schema information
        delta_df = spark.read.format("delta").load(table_path)
        
        # Convert Spark schema to Glue catalog format
        columns = []
        for field in delta_df.schema.fields:
            glue_type = convert_spark_to_glue_type(field.dataType)
            columns.append({
                'Name': field.name,
                'Type': glue_type,
                'Comment': f'Column {field.name}'
            })
        
        # Define table input for Glue catalog
        table_input = {
            'Name': table_name,
            'Description': 'Delta Lake table with employee data',
            'StorageDescriptor': {
                'Columns': columns,
                'Location': table_path,
                'InputFormat': 'org.apache.hadoop.mapred.TextInputFormat',
                'OutputFormat': 'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat',
                'SerdeInfo': {
                    'SerializationLibrary': 'org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe'
                }
            },
            'PartitionKeys': [
                {
                    'Name': 'department',
                    'Type': 'string',
                    'Comment': 'Partition by department'
                }
            ],
            'Parameters': {
                'classification': 'delta',
                'delta.table.path': table_path,
                'spark.sql.sources.provider': 'delta'
            }
        }
        
        # Try to create the table, update if it already exists
        try:
            glue_client.create_table(
                DatabaseName=database_name,
                TableInput=table_input
            )
            print(f"Created table {database_name}.{table_name} in Glue Data Catalog")
            
        except glue_client.exceptions.AlreadyExistsException:
            print(f"Table {database_name}.{table_name} already exists, updating...")
            glue_client.update_table(
                DatabaseName=database_name,
                TableInput=table_input
            )
            print(f"Updated table {database_name}.{table_name} in Glue Data Catalog")
            
    except Exception as e:
        print(f"Error registering table in catalog: {str(e)}")
        raise e

def convert_spark_to_glue_type(spark_type):
    """
    Convert Spark data types to Glue catalog types
    """
    type_mapping = {
        'IntegerType': 'int',
        'LongType': 'bigint',
        'DoubleType': 'double',
        'FloatType': 'float',
        'StringType': 'string',
        'BooleanType': 'boolean',
        'DateType': 'date',
        'TimestampType': 'timestamp'
    }
    
    spark_type_name = type(spark_type).__name__
    return type_mapping.get(spark_type_name, 'string')

def run_data_quality_checks(table_path):
    """
    Run basic data quality checks on the Delta table
    """
    print("Running data quality checks...")
    
    df = spark.read.format("delta").load(table_path)
    
    # Basic checks
    total_records = df.count()
    null_names = df.filter(col("name").isNull()).count()
    duplicate_ids = df.groupBy("employee_id").count().filter(col("count") > 1).count()
    
    print(f"Total records: {total_records}")
    print(f"Records with null names: {null_names}")
    print(f"Duplicate employee IDs: {duplicate_ids}")
    
    # Show some sample data
    print("Sample data from Delta table:")
    df.select("employee_id", "name", "department", "salary", "salary_band").show(10)
    
    return {
        'total_records': total_records,
        'null_names': null_names,
        'duplicate_ids': duplicate_ids
    }

# Main execution
def main():
    try:
        print("Starting ETL job...")
        
        # Step 1: Load source data
        print("Step 1: Loading source data...")
        source_df = load_source_data()
        
        # Step 2: Transform data
        print("Step 2: Transforming data...")
        transformed_df = transform_data(source_df)
        
        # Step 3: Write to Delta table
        print("Step 3: Writing to Delta table...")
        delta_path = args['delta_table_path']
        write_delta_table(transformed_df, delta_path)
        
        # Step 4: Register in Glue Data Catalog
        print("Step 4: Registering in Glue Data Catalog...")
        register_table_in_catalog(
            table_path=delta_path,
            database_name=args['target_database'],
            table_name=args['target_table']
        )
        
        # Step 5: Run data quality checks
        print("Step 5: Running data quality checks...")
        quality_results = run_data_quality_checks(delta_path)
        
        print("ETL job completed successfully!")
        print(f"Final quality check results: {quality_results}")
        
    except Exception as e:
        print(f"ETL job failed with error: {str(e)}")
        raise e

if __name__ == "__main__":
    main()

# Commit the job
job.commit()
```

# Job Setup with Delta Lake Config
```python
# Delta Lake Setup and Additional Operations
# This script shows how to configure and run the main ETL job

import boto3
import json

# AWS Glue Job Configuration
def create_glue_job():
    """
    Create the AWS Glue job with Delta Lake dependencies
    """
    glue_client = boto3.client('glue')
    
    job_definition = {
        'Name': 'delta-lake-etl-job',
        'Description': 'ETL job that processes data and saves as Delta Lake table',
        'Role': 'your-glue-service-role',  # Replace with your Glue service role ARN
        'Command': {
            'Name': 'glueetl',
            'ScriptLocation': 's3://your-glue-scripts-bucket/delta_etl_job.py',  # Upload the main script here
            'PythonVersion': '3'
        },
        'DefaultArguments': {
            '--job-language': 'python',
            '--job-bookmark-option': 'job-bookmark-enable',
            '--enable-continuous-cloudwatch-log': 'true',
            '--enable-metrics': 'true',
            '--enable-spark-ui': 'true',
            '--spark-event-logs-path': 's3://your-spark-logs-bucket/',
            '--additional-python-modules': 'delta-spark==2.4.0',  # Delta Lake for Spark 3.3
            '--conf': 'spark.sql.extensions=io.delta.sql.DeltaSparkSessionExtension --conf spark.sql.catalog.spark_catalog=org.apache.spark.sql.delta.catalog.DeltaCatalog',
            '--extra-jars': 's3://your-jars-bucket/delta-core_2.12-2.4.0.jar',  # Delta Lake JAR
            # Job-specific parameters
            '--source_database': 'source_db',
            '--source_table': 'employees_raw',
            '--target_database': 'analytics_db',
            '--target_table': 'employees_delta',
            '--delta_table_path': 's3://your-delta-lake-bucket/tables/employees/'
        },
        'MaxRetries': 1,
        'Timeout': 60,  # minutes
        'MaxCapacity': 10.0,  # DPUs
        'GlueVersion': '4.0',  # Latest Glue version with Spark 3.3
        'NumberOfWorkers': 4,
        'WorkerType': 'G.1X'
    }
    
    try:
        response = glue_client.create_job(**job_definition)
        print(f"Created Glue job: {response['Name']}")
        return response
    except Exception as e:
        print(f"Error creating Glue job: {str(e)}")
        return None

def run_glue_job(job_name):
    """
    Start the Glue job execution
    """
    glue_client = boto3.client('glue')
    
    try:
        response = glue_client.start_job_run(
            JobName=job_name,
            Arguments={
                '--source_database': 'source_db',
                '--source_table': 'employees_raw', 
                '--target_database': 'analytics_db',
                '--target_table': 'employees_delta',
                '--delta_table_path': 's3://your-delta-lake-bucket/tables/employees/'
            }
        )
        print(f"Started job run: {response['JobRunId']}")
        return response['JobRunId']
    except Exception as e:
        print(f"Error starting job: {str(e)}")
        return None

# Delta Lake Operations - Additional scripts you can run after the main ETL
def delta_lake_operations_example():
    """
    Example of additional Delta Lake operations you can perform
    """
    
    # This would be in a separate Glue job or notebook
    operations_script = """
from pyspark.sql import SparkSession
from delta.tables import *
from pyspark.sql.functions import *

# Initialize Spark with Delta Lake
spark = SparkSession.builder \\
    .appName("DeltaLakeOperations") \\
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \\
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \\
    .getOrCreate()

# Delta table path
delta_path = "s3://your-delta-lake-bucket/tables/employees/"

# 1. Time Travel - Query historical versions
print("=== Time Travel Examples ===")

# Query table as of specific timestamp
df_historical = spark.read.format("delta").option("timestampAsOf", "2023-12-01").load(delta_path)
print(f"Records as of 2023-12-01: {df_historical.count()}")

# Query table as of specific version
df_version = spark.read.format("delta").option("versionAsOf", 0).load(delta_path)
print(f"Records in version 0: {df_version.count()}")

# 2. Table History
print("\\n=== Table History ===")
delta_table = DeltaTable.forPath(spark, delta_path)
history_df = delta_table.history()
history_df.select("version", "timestamp", "operation", "operationMetrics").show(truncate=False)

# 3. Optimize Table (compaction)
print("\\n=== Optimizing Table ===")
delta_table.optimize().executeCompaction()
print("Table optimization completed")

# 4. Z-Order optimization (for better query performance)
delta_table.optimize().executeZOrderBy("department", "salary")
print("Z-Order optimization completed")

# 5. Vacuum old files (clean up)
print("\\n=== Vacuum Operation ===")
delta_table.vacuum(168)  # Keep 168 hours (7 days) of history
print("Vacuum operation completed")

# 6. Update records
print("\\n=== Update Operation ===")
delta_table.update(
    condition = col("department") == "Engineering",
    set = {"salary": col("salary") * 1.1}  # 10% raise for Engineering
)
print("Updated Engineering salaries")

# 7. Delete records
print("\\n=== Delete Operation ===")
delta_table.delete(condition = col("salary") < 50000)
print("Deleted records with salary < 50000")

# 8. Schema evolution example
print("\\n=== Schema Evolution ===")
new_data = [
    (6, "New Employee", "Data Science", 85000, "2024-01-01", "Senior", "Remote")
]

from pyspark.sql.types import *
new_schema = StructType([
    StructField("employee_id", IntegerType(), True),
    StructField("name", StringType(), True),
    StructField("department", StringType(), True),
    StructField("salary", IntegerType(), True),
    StructField("hire_date", StringType(), True),
    StructField("level", StringType(), True),  # New column
    StructField("work_mode", StringType(), True)  # New column
])

new_df = spark.createDataFrame(new_data, new_schema)
new_df = new_df.withColumn("hire_date", to_date(col("hire_date"), "yyyy-MM-dd"))

# Write with schema merge enabled
new_df.write \\
    .format("delta") \\
    .mode("append") \\
    .option("mergeSchema", "true") \\
    .save(delta_path)

print("Schema evolution completed - added new columns")

# 9. Show final table state
print("\\n=== Final Table State ===")
final_df = spark.read.format("delta").load(delta_path)
final_df.printSchema()
final_df.show(10)
print(f"Total records: {final_df.count()}")
"""
    
    return operations_script

# Crawler configuration for Delta Lake tables
def create_delta_crawler():
    """
    Create a crawler specifically configured for Delta Lake tables
    """
    glue_client = boto3.client('glue')
    
    crawler_config = {
        'Name': 'delta-lake-crawler',
        'Role': 'your-crawler-service-role',  # Replace with your crawler role ARN
        'DatabaseName': 'analytics_db',
        'Description': 'Crawler for Delta Lake tables',
        'Targets': {
            'DeltaTargets': [
                {
                    'DeltaTables': ['s3://your-delta-lake-bucket/tables/'],
                    'WriteManifest': True
                }
            ]
        },
        'SchemaChangePolicy': {
            'UpdateBehavior': 'UPDATE_IN_DATABASE',
            'DeleteBehavior': 'DELETE_FROM_DATABASE'
        },
        'Configuration': json.dumps({
            "Version": 1.0,
            "Grouping": {
                "TableGroupingPolicy": "CombineCompatibleSchemas"
            }
        })
    }
    
    try:
        response = glue_client.create_crawler(**crawler_config)
        print(f"Created Delta Lake crawler: {crawler_config['Name']}")
        return response
    except Exception as e:
        print(f"Error creating crawler: {str(e)}")
        return None

# Setup instructions
def setup_instructions():
    """
    Print setup instructions for Delta Lake in AWS Glue
    """
    instructions = """
    === DELTA LAKE SETUP INSTRUCTIONS ===
    
    1. Prerequisites:
       - AWS Glue 4.0 (Spark 3.3.0)
       - Delta Lake JAR files
       - Appropriate IAM roles
    
    2. Required JAR files to upload to S3:
       - delta-core_2.12-2.4.0.jar
       - delta-storage-2.4.0.jar
    
    3. IAM Permissions needed:
       - s3:GetObject, s3:PutObject on your Delta Lake bucket
       - s3:ListBucket on your Delta Lake bucket
       - glue:GetDatabase, glue:GetTable, glue:CreateTable, glue:UpdateTable
       - glue:GetPartitions, glue:BatchCreatePartition
    
    4. Job Parameters to configure:
       --additional-python-modules: delta-spark==2.4.0
       --extra-jars: s3://your-jars-bucket/delta-core_2.12-2.4.0.jar
       --conf: spark.sql.extensions=io.delta.sql.DeltaSparkSessionExtension
       --conf: spark.sql.catalog.spark_catalog=org.apache.spark.sql.delta.catalog.DeltaCatalog
    
    5. S3 Bucket Structure:
       your-delta-lake-bucket/
       ├── tables/
       │   ├── employees/
       │   │   ├── _delta_log/
       │   │   └── part-*.parquet
       │   └── other_tables/
       └── manifests/
    
    6. Querying from Athena:
       - Delta tables can be queried through Athena after cataloging
       - Use: SELECT * FROM analytics_db.employees_delta
    
    7. Monitoring:
       - Enable CloudWatch logs for job monitoring
       - Use Spark UI for performance tuning
       - Check Delta table history for audit trail
    """
    
    print(instructions)

if __name__ == "__main__":
    print("Delta Lake Setup and Configuration")
    print("=" * 50)
    
    # Show setup instructions
    setup_instructions()
    
    # Uncomment these lines to actually create resources
    # create_glue_job()
    # create_delta_crawler()
    # job_run_id = run_glue_job('delta-lake-etl-job')
    
    print("\nDelta Lake operations script:")
    print(delta_lake_operations_example())
```
