# Lakeflow Jobs Infrastructure as Code Cheatsheet

## Job Structure Overview

### Complete Job Definition Structure
```yaml
name: "job-name"
description: "Job description"
tags:
  environment: "prod"
  team: "data-engineering"

# Job-level configuration
timeout_seconds: 3600
max_concurrent_runs: 1
email_notifications:
  on_start: ["team@company.com"]
  on_success: ["team@company.com"]
  on_failure: ["team@company.com", "oncall@company.com"]

# Parameters (runtime variables)
parameters:
  - name: environment
    type: string
    default: "dev"
  - name: processing_date
    type: string
  - name: batch_size
    type: int
    default: 1000

# Job cluster configuration
job_clusters:
  - job_cluster_key: "main-cluster"
    new_cluster:
      spark_version: "13.3.x-scala2.12"
      node_type_id: "i3.xlarge"
      num_workers: 2
      spark_conf:
        "spark.sql.adaptive.enabled": "true"
        "spark.sql.adaptive.coalescePartitions.enabled": "true"

# Task definitions
tasks:
  - task_key: "extract"
    job_cluster_key: "main-cluster"
    notebook_task:
      notebook_path: "/path/to/extract_notebook"
      base_parameters:
        env: "${parameters.environment}"
        date: "${parameters.processing_date}"
    
  - task_key: "transform"
    depends_on:
      - task_key: "extract"
    job_cluster_key: "main-cluster"
    spark_python_task:
      python_file: "/path/to/transform.py"
      parameters:
        - "--input-path"
        - "/tmp/extracted_data"
        - "--batch-size"
        - "${parameters.batch_size}"

# Scheduling
schedule:
  quartz_cron_expression: "0 0 2 * * ?"  # Daily at 2 AM
  timezone_id: "UTC"
  pause_status: "UNPAUSED"
```

## Core Elements Breakdown

### 1. Job Metadata
```yaml
name: "my-data-pipeline"
description: "Daily ETL pipeline for customer data"
tags:
  environment: "production"
  team: "analytics"
  cost_center: "engineering"
```

### 2. Runtime Configuration
```yaml
timeout_seconds: 7200        # 2 hours
max_concurrent_runs: 1       # Prevent overlapping runs
retry_on_timeout: false
```

### 3. Notifications
```yaml
email_notifications:
  on_start: []
  on_success: ["success@company.com"]
  on_failure: ["alerts@company.com", "oncall@company.com"]
  no_alert_for_skipped_runs: false

webhook_notifications:
  on_success:
    - id: "slack-webhook"
      url: "https://hooks.slack.com/services/..."
```

### 4. Cluster Configuration
```yaml
job_clusters:
  - job_cluster_key: "small-cluster"
    new_cluster:
      spark_version: "13.3.x-scala2.12"
      node_type_id: "i3.large"
      num_workers: 1
      
  - job_cluster_key: "large-cluster"
    new_cluster:
      spark_version: "13.3.x-scala2.12"
      node_type_id: "i3.xlarge"
      num_workers: 5
      autoscale:
        min_workers: 2
        max_workers: 10
```

### 5. Task Types
```yaml
tasks:
  # Notebook Task
  - task_key: "notebook-task"
    notebook_task:
      notebook_path: "/Shared/notebooks/etl_notebook"
      base_parameters:
        param1: "value1"
        param2: "${parameters.dynamic_value}"
    
  # Python Script Task
  - task_key: "python-task"
    spark_python_task:
      python_file: "/FileStore/scripts/process_data.py"
      parameters: ["--date", "${parameters.processing_date}"]
    
  # SQL Task
  - task_key: "sql-task"
    sql_task:
      query:
        query_id: "query-uuid-here"
      parameters:
        date_param: "${parameters.processing_date}"
    
  # JAR Task
  - task_key: "jar-task"
    spark_jar_task:
      main_class_name: "com.company.DataProcessor"
      jar_uri: "/FileStore/jars/processor.jar"
      parameters: ["${parameters.environment}", "${parameters.batch_size}"]
```

## Static Parameters Examples

### Basic Static Configuration
```yaml
name: "static-etl-job"
parameters:
  - name: source_table
    type: string
    default: "raw_events"
  - name: target_table
    type: string
    default: "processed_events"
  - name: batch_size
    type: int
    default: 10000

tasks:
  - task_key: "process"
    notebook_task:
      notebook_path: "/etl/process_events"
      base_parameters:
        source: "${parameters.source_table}"
        target: "${parameters.target_table}"
        batch: "${parameters.batch_size}"
```

### Environment-Specific Static Parameters
```yaml
name: "multi-env-job"
parameters:
  - name: environment
    type: string
    default: "dev"
  - name: database_name
    type: string
    default: "analytics_dev"
  - name: s3_bucket
    type: string
    default: "company-data-dev"

tasks:
  - task_key: "extract"
    spark_python_task:
      python_file: "/scripts/extract.py"
      parameters:
        - "--env"
        - "${parameters.environment}"
        - "--database"
        - "${parameters.database_name}"
        - "--bucket" 
        - "${parameters.s3_bucket}"
```

## Dynamic Parameters Examples

### Date-Based Dynamic Parameters
```yaml
name: "daily-processing-job"
parameters:
  - name: processing_date
    type: string
    default: "${date_format(current_date(), 'yyyy-MM-dd')}"
  - name: lookback_days
    type: int
    default: 7
  - name: partition_date
    type: string
    default: "${date_format(date_sub(current_date(), 1), 'yyyy/MM/dd')}"

tasks:
  - task_key: "extract_daily_data"
    notebook_task:
      notebook_path: "/etl/daily_extract"
      base_parameters:
        start_date: "${date_sub(parameters.processing_date, parameters.lookback_days)}"
        end_date: "${parameters.processing_date}"
        partition_path: "s3://bucket/data/${parameters.partition_date}/"
```

### Calculated Dynamic Parameters
```yaml
name: "scalable-processing-job"
parameters:
  - name: data_volume_gb
    type: int
    default: 100
  - name: base_workers
    type: int
    default: 2
  - name: memory_per_worker
    type: string
    default: "8g"

job_clusters:
  - job_cluster_key: "dynamic-cluster"
    new_cluster:
      spark_version: "13.3.x-scala2.12"
      node_type_id: "i3.xlarge"
      # Dynamic worker calculation: 1 worker per 50GB of data, minimum 2
      num_workers: "${max(parameters.base_workers, ceil(parameters.data_volume_gb / 50))}"
      spark_conf:
        # Dynamic memory allocation
        "spark.executor.memory": "${parameters.memory_per_worker}"
        "spark.executor.instances": "${max(parameters.base_workers, ceil(parameters.data_volume_gb / 50))}"

tasks:
  - task_key: "process_large_dataset"
    job_cluster_key: "dynamic-cluster"
    spark_python_task:
      python_file: "/scripts/process_large.py"
      parameters:
        - "--data-size-gb"
        - "${parameters.data_volume_gb}"
        - "--parallelism"
        - "${max(parameters.base_workers, ceil(parameters.data_volume_gb / 50)) * 4}"
```

### Conditional Dynamic Parameters
```yaml
name: "environment-aware-job"
parameters:
  - name: environment
    type: string
    default: "dev"
  - name: is_production
    type: boolean
    default: "${parameters.environment == 'prod'}"
  - name: enable_optimization
    type: boolean
    default: "${parameters.is_production}"

job_clusters:
  - job_cluster_key: "env-cluster"
    new_cluster:
      spark_version: "13.3.x-scala2.12"
      # Production gets larger instances
      node_type_id: "${parameters.is_production ? 'i3.2xlarge' : 'i3.large'}"
      # Production gets more workers
      num_workers: "${parameters.is_production ? 8 : 2}"
      spark_conf:
        # Enable adaptive query execution in production
        "spark.sql.adaptive.enabled": "${parameters.enable_optimization}"
        "spark.sql.adaptive.coalescePartitions.enabled": "${parameters.enable_optimization}"

tasks:
  - task_key: "conditional_processing"
    job_cluster_key: "env-cluster"
    notebook_task:
      notebook_path: "/etl/main_processing"
      base_parameters:
        optimization_level: "${parameters.is_production ? 'high' : 'basic'}"
        cache_enabled: "${parameters.is_production}"
        debug_mode: "${!parameters.is_production}"
```

### Complex Dynamic Workflows
```yaml
name: "dynamic-workflow-job"
parameters:
  - name: process_type
    type: string
    default: "incremental"  # Options: full, incremental, backfill
  - name: backfill_start_date
    type: string
    default: "2024-01-01"
  - name: backfill_end_date
    type: string
    default: "2024-01-31"

tasks:
  # Conditional task execution based on process type
  - task_key: "full_refresh"
    condition: "${parameters.process_type == 'full'}"
    notebook_task:
      notebook_path: "/etl/full_refresh"
      base_parameters:
        truncate_target: "true"
  
  - task_key: "incremental_load"
    condition: "${parameters.process_type == 'incremental'}"
    notebook_task:
      notebook_path: "/etl/incremental_load"
      base_parameters:
        processing_date: "${date_format(current_date(), 'yyyy-MM-dd')}"
  
  - task_key: "backfill_process"
    condition: "${parameters.process_type == 'backfill'}"
    notebook_task:
      notebook_path: "/etl/backfill_processor"
      base_parameters:
        start_date: "${parameters.backfill_start_date}"
        end_date: "${parameters.backfill_end_date}"
        # Calculate days to process
        total_days: "${date_diff(parameters.backfill_end_date, parameters.backfill_start_date)}"

  # Common validation task that runs after any of the above
  - task_key: "validate_results"
    depends_on:
      - task_key: "full_refresh"
        outcome: "SUCCESS"
      - task_key: "incremental_load"
        outcome: "SUCCESS"  
      - task_key: "backfill_process"
        outcome: "SUCCESS"
    notebook_task:
      notebook_path: "/etl/validation"
      base_parameters:
        process_type: "${parameters.process_type}"
```

## Common Dynamic Functions

### Date Functions
```yaml
# Current date/time
current_date: "${current_date()}"                    # 2024-01-15
current_timestamp: "${current_timestamp()}"          # 2024-01-15T10:30:00Z

# Date arithmetic
yesterday: "${date_sub(current_date(), 1)}"          # 2024-01-14
last_week: "${date_sub(current_date(), 7)}"          # 2024-01-08
next_month: "${date_add(current_date(), 30)}"        # 2024-02-14

# Date formatting
formatted_date: "${date_format(current_date(), 'yyyy-MM-dd')}"      # 2024-01-15
partition_date: "${date_format(current_date(), 'yyyy/MM/dd')}"      # 2024/01/15
file_timestamp: "${date_format(current_timestamp(), 'yyyyMMdd_HHmmss')}"  # 20240115_103000
```

### Mathematical Functions
```yaml
# Basic math
doubled_batch: "${parameters.batch_size * 2}"
half_workers: "${parameters.worker_count / 2}"
total_memory: "${parameters.memory_per_worker * parameters.worker_count}"

# Rounding functions
rounded_up: "${ceil(parameters.data_size_gb / 10.0)}"      # Round up
rounded_down: "${floor(parameters.data_size_gb / 10.0)}"   # Round down
rounded: "${round(parameters.average_processing_time)}"     # Round to nearest

# Min/Max
min_workers: "${max(2, parameters.calculated_workers)}"     # At least 2 workers
max_timeout: "${min(3600, parameters.timeout_seconds)}"    # At most 1 hour
```

### String Functions
```yaml
# String manipulation
uppercase_env: "${upper(parameters.environment)}"           # DEV -> DEV
lowercase_env: "${lower(parameters.environment)}"           # DEV -> dev
table_suffix: "${concat(parameters.base_table, '_', parameters.environment)}"  # events_dev

# String conditionals
database_name: "${parameters.environment == 'prod' ? 'analytics' : concat('analytics_', parameters.environment)}"
```

## Deployment Commands

### Using Databricks CLI
```bash
# Deploy job
databricks jobs create --json-file job.json

# Update existing job
databricks jobs reset --job-id 123 --json-file job.json

# Deploy with parameter override
databricks jobs run-now --job-id 123 --json-params '{"environment": "staging"}'
```

### Using Terraform
```hcl
resource "databricks_job" "etl_job" {
  name = "ETL Pipeline"
  
  dynamic "parameter" {
    for_each = var.job_parameters
    content {
      name    = parameter.key
      default = parameter.value
    }
  }
  
  job_cluster {
    job_cluster_key = "main"
    new_cluster {
      num_workers   = var.cluster_size
      spark_version = "13.3.x-scala2.12"
      node_type_id  = "i3.xlarge"
    }
  }
  
  task {
    task_key = "main_task"
    job_cluster_key = "main"
    
    notebook_task {
      notebook_path = var.notebook_path
      base_parameters = var.notebook_parameters
    }
  }
}
```

## Best Practices

### Parameter Naming
- Use snake_case for parameter names
- Include type information in name when helpful (`date_string`, `count_int`)
- Group related parameters with prefixes (`source_table`, `source_database`)

### Dynamic Parameter Tips
- Always provide sensible defaults
- Use conditional logic to handle different environments
- Validate parameter combinations in your notebooks/scripts
- Document parameter dependencies and valid ranges

### Security Considerations
- Never put secrets in parameters - use Databricks secrets instead
- Use parameter validation to prevent injection attacks
- Limit parameter scope to minimum required permissions

---
---
---
---
# Notifications In-depth
# Lakeflow Jobs Notifications Infrastructure as Code Cheatsheet

## Notification Structure Overview

### Complete Notification Configuration
```yaml
name: "data-pipeline-with-notifications"

# Job-level notifications
email_notifications:
  on_start: ["team-lead@company.com"]
  on_success: ["team@company.com"] 
  on_failure: ["team@company.com", "oncall@company.com", "manager@company.com"]
  no_alert_for_skipped_runs: false

webhook_notifications:
  on_start:
    - id: "slack-start"
      url: "https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX"
  on_success:
    - id: "slack-success"
      url: "https://hooks.slack.com/services/T00000000/B00000000/YYYYYYYYYYYYYYYYYYYYYYYY"
  on_failure:
    - id: "slack-failure" 
      url: "https://hooks.slack.com/services/T00000000/B00000000/ZZZZZZZZZZZZZZZZZZZZZZZZ"
    - id: "pagerduty-critical"
      url: "https://events.pagerduty.com/integration/abcdefghijklmnopqrstuvwxyz/enqueue"

tasks:
  - task_key: "critical_task"
    # Task-level notifications override job-level
    email_notifications:
      on_failure: ["critical-alerts@company.com", "cto@company.com"]
    webhook_notifications:
      on_failure:
        - id: "critical-slack"
          url: "https://hooks.slack.com/services/T00000000/B00000000/CRITICAL_WEBHOOK"
    
    notebook_task:
      notebook_path: "/critical/processing"
```

## Job-Level Notifications

### Basic Email Notifications
```yaml
name: "basic-etl-job"

# Simple email configuration
email_notifications:
  on_start: []                                    # No emails on start
  on_success: ["data-team@company.com"]          # Success notifications
  on_failure: ["data-team@company.com", "oncall@company.com"]  # Failure alerts
  no_alert_for_skipped_runs: true               # Skip notifications for skipped runs
```

### Advanced Email Notifications
```yaml
name: "production-etl-job"

email_notifications:
  # Notify different groups for different events
  on_start: ["job-monitor@company.com"]
  on_success: 
    - "data-team@company.com"
    - "business-users@company.com"
  on_failure:
    - "data-team@company.com"           # Always notify data team
    - "oncall-engineer@company.com"     # Page on-call
    - "manager@company.com"             # Notify management
    - "infrastructure@company.com"      # Infrastructure team for debugging
  
  # Don't spam for expected skipped runs
  no_alert_for_skipped_runs: true
```

### Webhook Notifications (Slack Integration)
```yaml
name: "slack-integrated-job"

webhook_notifications:
  on_start:
    - id: "slack-job-start"
      url: "${secrets.slack_webhook_general}"  # Use secret for webhook URL
      
  on_success:
    - id: "slack-job-success"
      url: "${secrets.slack_webhook_data_team}"
      
  on_failure:
    - id: "slack-job-failure"
      url: "${secrets.slack_webhook_alerts}"
    - id: "slack-job-failure-general"
      url: "${secrets.slack_webhook_general}"
```

### Multi-Channel Webhook Notifications
```yaml
name: "multi-channel-notifications"

webhook_notifications:
  on_failure:
    # Slack notification
    - id: "slack-data-team"
      url: "${secrets.slack_webhook_data}"
      
    # Microsoft Teams notification  
    - id: "teams-engineering"
      url: "${secrets.teams_webhook_engineering}"
      
    # PagerDuty for critical alerts
    - id: "pagerduty-critical"
      url: "${secrets.pagerduty_integration_url}"
      
    # Custom internal webhook
    - id: "internal-monitoring"
      url: "https://monitoring.company.com/api/alerts/databricks"
```

### Environment-Specific Notifications
```yaml
name: "environment-aware-notifications"

parameters:
  - name: environment
    type: string
    default: "dev"
  - name: is_production
    type: boolean
    default: "${parameters.environment == 'prod'}"

# Conditional notifications based on environment
email_notifications:
  on_start: "${parameters.is_production ? ['prod-monitor@company.com'] : []}"
  on_success: 
    # Production: notify business users, Dev: just data team
    - "${parameters.is_production ? 'business-users@company.com' : 'dev-team@company.com'}"
  on_failure:
    # Production gets more aggressive alerting
    - "data-team@company.com"
    - "${parameters.is_production ? 'oncall@company.com' : 'dev-lead@company.com'}"
    - "${parameters.is_production ? 'manager@company.com' : ''}"

webhook_notifications:
  on_failure:
    # Different Slack channels per environment
    - id: "slack-env-specific"
      url: "${parameters.environment == 'prod' ? secrets.slack_prod_alerts : secrets.slack_dev_alerts}"
```
