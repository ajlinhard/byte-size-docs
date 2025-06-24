# Airflow Overview
Apache Airflow is an open-source platform for developing, scheduling, and monitoring workflows. It's designed to programmatically author, schedule, and monitor data pipelines and complex workflows.

# Table of Contents
- [Airflow Overview](#airflow-overview)
  - [Core Concepts](#core-concepts)
  - [Key Features](#key-features)
  - [Example Use Cases](#example-use-cases)
- [Operators](#operators)
  - [Hooks](#hooks)
  - [Sensors](#sensors)
  - [Executors](#executors)

## Core Concepts

**DAGs (Directed Acyclic Graphs)** are the fundamental building blocks of Airflow. A DAG represents a workflow as a collection of tasks with dependencies between them. The "acyclic" nature means there are no circular dependencies - tasks flow in one direction without loops.

**Tasks** are the individual units of work within a DAG. Each task represents a single operation, such as running a Python function, executing a SQL query, or transferring files. Tasks are defined using operators and have states like queued, running, success, failed, or skipped.

**Operators** define what actually gets executed. Airflow provides many built-in operators including BashOperator for shell commands, PythonOperator for Python functions, SQLOperator for database queries, and EmailOperator for sending notifications. You can also create custom operators.

**Task Dependencies** define the order of execution. Dependencies are set using bitshift operators (`>>` and `<<`) or methods like `set_upstream()` and `set_downstream()`. This creates the directed graph structure.

**Scheduler** is responsible for triggering workflow execution based on defined schedules and dependencies. It continuously monitors DAGs and queues tasks when their dependencies are met and schedule conditions are satisfied.

**Executor** determines how and where tasks run. Options include SequentialExecutor (single-threaded), LocalExecutor (multi-process), CeleryExecutor (distributed), and KubernetesExecutor (container-based).

**Workers** are the processes that actually execute tasks. In distributed setups, workers can run on multiple machines to provide scalability and fault tolerance.

## Key Features

**Web Interface** provides a rich UI for monitoring workflows, viewing task logs, managing connections, and manually triggering DAGs. The interface includes gantt charts, tree views, and graph visualizations of workflows.

**Extensibility** allows custom operators, hooks, sensors, and executors. The plugin system enables integration with virtually any system or service.

**Robust Scheduling** supports cron-based scheduling, time-based triggers, and complex scheduling logic. You can define start dates, end dates, catchup behavior, and timezone handling.

**Monitoring and Alerting** includes comprehensive logging, email notifications, Slack integration, and webhook support. Task failure handling includes retry logic and escalation procedures.

**Connection Management** centralizes credentials and connection details for external systems. Connections can be managed through the UI or configured via environment variables.

**Templating** uses Jinja2 templating to make workflows dynamic. You can parameterize SQL queries, file paths, and other task parameters using variables and macros.

## Example Use Cases

**ETL Data Pipelines** are perhaps the most common use case. A typical pipeline might extract data from multiple sources (APIs, databases, files), transform it using Python or SQL, and load it into a data warehouse. For example, daily processing of customer transaction data from various payment systems, applying business rules and data quality checks, then loading into a analytics database for reporting.

**Machine Learning Workflows** can orchestrate the entire ML lifecycle. This includes data preprocessing, feature engineering, model training, validation, and deployment. A practical example would be retraining a recommendation model weekly using new user interaction data, evaluating performance against holdout sets, and automatically deploying improved models.

**Data Quality Monitoring** workflows can run regular checks on data freshness, completeness, and accuracy. These might include verifying that daily data loads completed successfully, checking for anomalies in key metrics, and alerting stakeholders when issues are detected.

**Batch Processing Jobs** for large-scale data processing tasks. This could involve processing log files, generating reports, or performing complex calculations on large datasets. For instance, monthly financial reconciliation processes that aggregate transactions across multiple systems and generate compliance reports.

**System Maintenance Tasks** like database cleanup, log rotation, backup procedures, and infrastructure monitoring. A workflow might include nightly database backups, archiving old data, updating system configurations, and health checking critical services.

**Multi-System Integration** workflows coordinate activities across different platforms. This might involve synchronizing data between CRM and marketing automation systems, updating inventory across e-commerce platforms, or coordinating deployment processes across development environments.

**Reporting and Analytics** automation generates and distributes regular reports. Examples include daily executive dashboards, weekly performance summaries sent to stakeholders, or monthly financial reports that pull data from multiple sources and format results for different audiences.

The power of Airflow lies in its ability to handle complex dependencies, provide visibility into workflow execution, and offer robust error handling and recovery mechanisms. This makes it particularly valuable for mission-critical data operations where reliability and observability are essential.

---
## Operators

Operators define what actually gets executed in Airflow tasks. They're the building blocks that perform the actual work.

**Core Operators** handle fundamental operations. The BashOperator executes shell commands and scripts, making it useful for running system commands, calling external programs, or executing shell scripts. The PythonOperator runs Python functions, allowing you to execute custom Python code with access to task context and parameters. The EmailOperator sends emails with customizable recipients, subjects, and content, often used for notifications and alerts.

**Database Operators** interact with various database systems. The SQLOperator executes SQL queries against databases, supporting templating for dynamic queries. Specific database operators like PostgresOperator, MySqlOperator, and SqliteOperator provide database-specific functionality. The SQLCheckOperator performs data quality checks by running SQL queries and validating results against expected conditions.

**Transfer Operators** move data between systems. The S3ToRedshiftOperator transfers data from Amazon S3 to Redshift data warehouse. The MySqlToS3Operator exports MySQL query results to S3. The GenericTransfer operator provides a template for custom data transfers between any two systems.

**Cloud Provider Operators** integrate with major cloud platforms. AWS operators include S3FileTransformOperator for processing S3 files, EMRAddStepsOperator for running Spark jobs on EMR, and LambdaInvokeFunctionOperator for triggering Lambda functions. Google Cloud operators cover BigQuery operations, Dataflow job management, and Compute Engine instance control. Azure operators handle Blob Storage, Data Factory, and Virtual Machine operations.

**Container and Orchestration Operators** work with containerized workloads. The DockerOperator runs tasks in Docker containers, providing isolation and environment consistency. The KubernetesPodOperator executes tasks as Kubernetes pods, offering scalability and resource management. The ECSOperator runs tasks on Amazon ECS for managed container execution.

**HTTP and API Operators** handle web service interactions. The SimpleHttpOperator makes HTTP requests to REST APIs, supporting various authentication methods and response handling. The HttpSensor waits for HTTP endpoints to return specific responses before proceeding.

**File and Data Processing Operators** handle file operations and data manipulation. The FileSensor monitors file systems for file presence or changes. The PapermillOperator executes Jupyter notebooks as part of workflows, useful for data science pipelines.

## Hooks

Hooks provide interfaces to external systems and abstract away connection details and authentication.

**Database Hooks** manage database connections and operations. The PostgresHook handles PostgreSQL connections, providing methods for executing queries, bulk operations, and transaction management. The MySqlHook offers similar functionality for MySQL databases. The SqliteHook manages SQLite connections for lightweight database operations.

**Cloud Storage Hooks** interact with cloud storage services. The S3Hook manages Amazon S3 operations including file uploads, downloads, listing objects, and managing bucket policies. The GCSHook provides similar functionality for Google Cloud Storage. The AzureBlobStorageHook handles Azure Blob Storage operations.

**HTTP Hooks** manage web service communications. The HttpHook handles REST API interactions, managing authentication, request formatting, and response parsing. It supports various authentication methods including basic auth, OAuth, and custom headers.

**Big Data Hooks** integrate with big data platforms. The HiveHook connects to Apache Hive for data warehouse operations. The SparkHook manages Spark job submission and monitoring. The HdfsHook interacts with Hadoop Distributed File System for file operations.

**Message Queue Hooks** work with messaging systems. The SqsHook interacts with Amazon SQS for message queue operations. The RabbitMqHook manages RabbitMQ connections for message publishing and consuming.

**Monitoring and Logging Hooks** integrate with observability platforms. The SlackHook sends messages to Slack channels for notifications. The DatadogHook submits metrics and events to Datadog for monitoring.

## Sensors

Sensors are special operators that wait for certain conditions to be met before allowing downstream tasks to proceed.

**File Sensors** monitor file systems and storage. The FileSensor waits for files to appear in specified locations, useful for triggering workflows when data arrives. The S3KeySensor monitors Amazon S3 for object creation or modification. The GCSObjectExistenceSensor checks for objects in Google Cloud Storage. The HdfsSensor monitors Hadoop file systems for file presence.

**Time-based Sensors** handle temporal conditions. The TimeSensor waits until a specific time of day before proceeding. The TimeDeltaSensor waits for a specified time duration. These are useful for coordinating workflows across time zones or ensuring tasks run at optimal times.

**Database Sensors** monitor database conditions. The SqlSensor executes SQL queries and waits for specific results, useful for data availability checks. The NamedHivePartitionSensor waits for Hive partitions to become available before processing.

**HTTP Sensors** monitor web services and APIs. The HttpSensor polls HTTP endpoints waiting for specific responses, status codes, or content. This is valuable for waiting on external API availability or data processing completion.

**Custom Condition Sensors** handle complex logic. The PythonSensor executes custom Python functions that return boolean values, allowing for complex conditional logic. This provides maximum flexibility for custom waiting conditions.

**External System Sensors** monitor various external systems. The SqsSensor monitors Amazon SQS queues for messages. The S3PrefixSensor waits for objects with specific prefixes in S3 buckets. The DateTimeSensor waits until a specific datetime is reached.

## Executors

Executors determine how and where tasks are executed, affecting scalability, performance, and resource utilization.

**SequentialExecutor** runs tasks one at a time in a single process. It's the simplest executor, suitable for development, testing, and very small workflows. Since it can't run tasks in parallel, it's not appropriate for production use with complex workflows.

**LocalExecutor** runs tasks in parallel using multiple processes on a single machine. It's suitable for single-machine deployments with moderate workloads. The LocalExecutor can be configured to limit the number of concurrent processes and is good for development environments that need parallelism.

**CeleryExecutor** distributes tasks across multiple worker machines using Celery as the distributed task queue. This executor requires a message broker like Redis or RabbitMQ and supports horizontal scaling by adding more worker nodes. It's ideal for production environments with high task volumes and provides fault tolerance through worker redundancy.

**CeleryKubernetesExecutor** combines Celery for most tasks with Kubernetes pods for specific workloads. This hybrid approach allows using Celery workers for regular tasks while leveraging Kubernetes for resource-intensive or isolated tasks.

**KubernetesExecutor** runs each task as a separate Kubernetes pod. This provides excellent isolation, resource management, and scalability. Each task gets its own container environment with specified resource limits. It's particularly useful for heterogeneous workloads requiring different runtime environments or resource requirements.

**DebugExecutor** runs tasks locally with enhanced debugging capabilities. It's designed for development and troubleshooting, providing detailed logging and easier debugging of task execution.

**DaskExecutor** integrates with Dask distributed computing framework, allowing tasks to run on Dask clusters. This is useful for data science workloads and computationally intensive tasks that can benefit from Dask's parallel computing capabilities.

The choice of executor significantly impacts your Airflow deployment's scalability, resource utilization, and operational complexity. Production environments typically use CeleryExecutor or KubernetesExecutor depending on infrastructure preferences and scaling requirements.
