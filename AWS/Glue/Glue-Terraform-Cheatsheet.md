# Terraform AWS Glue Infrastructure Cheatsheet

## Table of Contents
- [Provider Configuration](#provider-configuration)
- [IAM Roles & Policies](#iam-roles--policies)
- [Glue Database](#glue-database)
- [Glue Tables](#glue-tables)
- [Glue Jobs](#glue-jobs)
- [Glue Crawlers](#glue-crawlers)
- [Glue Triggers](#glue-triggers)
- [Glue Workflows](#glue-workflows)
- [Glue Connections](#glue-connections)
- [Security Configuration](#security-configuration)
- [Data Quality](#data-quality)
- [Variables & Outputs](#variables--outputs)
- [Best Practices](#best-practices)

## Provider Configuration

```hcl
terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}
```

## IAM Roles & Policies

### Glue Service Role
```hcl
# IAM Role for Glue Jobs
resource "aws_iam_role" "glue_role" {
  name = "${var.project_name}-glue-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "glue.amazonaws.com"
        }
      }
    ]
  })

  tags = var.tags
}

# Attach AWS managed policy
resource "aws_iam_role_policy_attachment" "glue_service_role" {
  role       = aws_iam_role.glue_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole"
}

# Custom policy for S3 access
resource "aws_iam_role_policy" "glue_s3_policy" {
  name = "${var.project_name}-glue-s3-policy"
  role = aws_iam_role.glue_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ]
        Resource = [
          "${aws_s3_bucket.data_bucket.arn}",
          "${aws_s3_bucket.data_bucket.arn}/*",
          "${aws_s3_bucket.scripts_bucket.arn}",
          "${aws_s3_bucket.scripts_bucket.arn}/*"
        ]
      }
    ]
  })
}
```

### Crawler Role
```hcl
resource "aws_iam_role" "glue_crawler_role" {
  name = "${var.project_name}-glue-crawler-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "glue.amazonaws.com"
        }
      }
    ]
  })

  tags = var.tags
}

resource "aws_iam_role_policy_attachment" "glue_crawler_service_role" {
  role       = aws_iam_role.glue_crawler_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole"
}
```

## Glue Database

```hcl
resource "aws_glue_catalog_database" "database" {
  name         = var.database_name
  description  = "Database for ${var.project_name} data catalog"
  
  create_table_default_permission {
    permissions = ["ALL"]
    principal   = aws_iam_role.glue_role.arn
  }

  target_database {
    catalog_id    = data.aws_caller_identity.current.account_id
    database_name = var.database_name
  }

  tags = var.tags
}
```

## Glue Tables

### Manually Defined Table
```hcl
resource "aws_glue_catalog_table" "customers_table" {
  name          = "customers"
  database_name = aws_glue_catalog_database.database.name
  description   = "Customer data table"

  table_type = "EXTERNAL_TABLE"

  parameters = {
    "classification"         = "parquet"
    "compressionType"       = "gzip"
    "typeOfData"           = "file"
    "skip.header.line.count" = "0"
  }

  storage_descriptor {
    location      = "s3://${aws_s3_bucket.data_bucket.bucket}/customers/"
    input_format  = "org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat"
    output_format = "org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat"

    ser_de_info {
      name                  = "ParquetHiveSerDe"
      serialization_library = "org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe"
    }

    columns {
      name = "customer_id"
      type = "bigint"
    }

    columns {
      name = "name"
      type = "string"
    }

    columns {
      name = "email"
      type = "string"
    }

    columns {
      name = "created_date"
      type = "timestamp"
    }
  }

  partition_keys {
    name = "year"
    type = "string"
  }

  partition_keys {
    name = "month"
    type = "string"
  }

  tags = var.tags
}
```

### Partitions
```hcl
resource "aws_glue_partition" "customers_partition" {
  database_name = aws_glue_catalog_database.database.name
  table_name    = aws_glue_catalog_table.customers_table.name

  partition_values = ["2024", "01"]

  storage_descriptor {
    location      = "s3://${aws_s3_bucket.data_bucket.bucket}/customers/year=2024/month=01/"
    input_format  = "org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat"
    output_format = "org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat"

    ser_de_info {
      serialization_library = "org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe"
    }
  }
}
```

## Glue Jobs

### PySpark ETL Job
```hcl
resource "aws_glue_job" "etl_job" {
  name         = "${var.project_name}-etl-job"
  description  = "ETL job for processing customer data"
  role_arn     = aws_iam_role.glue_role.arn
  glue_version = "4.0"

  command {
    script_location = "s3://${aws_s3_bucket.scripts_bucket.bucket}/scripts/etl_job.py"
    python_version  = "3"
  }

  default_arguments = {
    "--job-language"                     = "python"
    "--job-bookmark-option"             = "job-bookmark-enable"
    "--enable-metrics"                  = "true"
    "--enable-continuous-cloudwatch-log" = "true"
    "--enable-continuous-log-filter"    = "true"
    "--enable-spark-ui"                 = "true"
    "--spark-event-logs-path"           = "s3://${aws_s3_bucket.logs_bucket.bucket}/spark-logs/"
    "--TempDir"                         = "s3://${aws_s3_bucket.temp_bucket.bucket}/temp/"
    "--additional-python-modules"       = "pandas==1.5.3,numpy==1.24.3"
    "--extra-py-files"                  = "s3://${aws_s3_bucket.scripts_bucket.bucket}/libs/utils.py"
    
    # Custom arguments
    "--SOURCE_DATABASE"    = aws_glue_catalog_database.database.name
    "--SOURCE_TABLE"       = "raw_customers"
    "--TARGET_DATABASE"    = aws_glue_catalog_database.database.name
    "--TARGET_TABLE"       = "processed_customers"
    "--TARGET_S3_PATH"     = "s3://${aws_s3_bucket.data_bucket.bucket}/processed/"
  }

  execution_property {
    max_concurrent_runs = 2
  }

  max_retries = 1
  timeout     = 60

  worker_type       = "G.1X"
  number_of_workers = 2

  security_configuration = aws_glue_security_configuration.security_config.name

  tags = var.tags
}
```

### Streaming Job
```hcl
resource "aws_glue_job" "streaming_job" {
  name         = "${var.project_name}-streaming-job"
  description  = "Streaming job for real-time data processing"
  role_arn     = aws_iam_role.glue_role.arn
  glue_version = "4.0"

  command {
    name            = "gluestreaming"
    script_location = "s3://${aws_s3_bucket.scripts_bucket.bucket}/scripts/streaming_job.py"
    python_version  = "3"
  }

  default_arguments = {
    "--job-language"           = "python"
    "--enable-metrics"         = "true"
    "--enable-continuous-cloudwatch-log" = "true"
    "--window-size"            = "100"
    "--checkpoint-location"    = "s3://${aws_s3_bucket.temp_bucket.bucket}/checkpoints/"
  }

  worker_type       = "G.1X"
  number_of_workers = 2

  tags = var.tags
}
```

### Ray Job
```hcl
resource "aws_glue_job" "ray_job" {
  name         = "${var.project_name}-ray-job"
  description  = "Ray job for distributed ML processing"
  role_arn     = aws_iam_role.glue_role.arn
  glue_version = "4.0"

  command {
    name            = "glueray"
    script_location = "s3://${aws_s3_bucket.scripts_bucket.bucket}/scripts/ray_job.py"
    python_version  = "3.9"
  }

  default_arguments = {
    "--job-language" = "python"
    "--min-workers"  = "1"
    "--max-workers"  = "5"
  }

  worker_type       = "Z.2X"
  number_of_workers = 3

  tags = var.tags
}
```

## Glue Crawlers

### S3 Crawler
```hcl
resource "aws_glue_crawler" "s3_crawler" {
  database_name = aws_glue_catalog_database.database.name
  name          = "${var.project_name}-s3-crawler"
  role          = aws_iam_role.glue_crawler_role.arn
  description   = "Crawler for S3 data sources"

  s3_target {
    path = "s3://${aws_s3_bucket.data_bucket.bucket}/raw/"
    
    exclusions = [
      "**.tmp",
      "**/_temporary/**"
    ]
  }

  s3_target {
    path       = "s3://${aws_s3_bucket.data_bucket.bucket}/processed/"
    sample_size = 1
  }

  configuration = jsonencode({
    Version = 1.0
    CrawlerOutput = {
      Partitions = {
        AddOrUpdateBehavior = "InheritFromTable"
      }
      Tables = {
        AddOrUpdateBehavior = "MergeNewColumns"
      }
    }
    Grouping = {
      TableGroupingPolicy = "CombineCompatibleSchemas"
    }
  })

  schema_change_policy {
    update_behavior = "UPDATE_IN_DATABASE"
    delete_behavior = "LOG"
  }

  recrawl_policy {
    recrawl_behavior = "CRAWL_EVERYTHING"
  }

  lineage_configuration {
    crawler_lineage_settings = "ENABLE"
  }

  schedule = "cron(0 6 * * ? *)"  # Daily at 6 AM UTC

  tags = var.tags
}
```

### JDBC Crawler
```hcl
resource "aws_glue_crawler" "jdbc_crawler" {
  database_name = aws_glue_catalog_database.database.name
  name          = "${var.project_name}-jdbc-crawler"
  role          = aws_iam_role.glue_crawler_role.arn

  jdbc_target {
    connection_name = aws_glue_connection.rds_connection.name
    path            = "myschema/%"
    exclusions      = [
      "myschema/temp_%",
      "myschema/backup_%"
    ]
  }

  configuration = jsonencode({
    Version = 1.0
    CrawlerOutput = {
      Partitions = {
        AddOrUpdateBehavior = "InheritFromTable"
      }
    }
  })

  tags = var.tags
}
```

## Glue Triggers

### Scheduled Trigger
```hcl
resource "aws_glue_trigger" "scheduled_trigger" {
  name     = "${var.project_name}-scheduled-trigger"
  type     = "SCHEDULED"
  schedule = "cron(0 8 * * ? *)"  # Daily at 8 AM UTC
  
  description = "Daily ETL job trigger"
  enabled     = true

  actions {
    job_name = aws_glue_job.etl_job.name
    
    arguments = {
      "--run_date" = "{{ ds }}"
    }
    
    timeout               = 60
    security_configuration = aws_glue_security_configuration.security_config.name
  }

  tags = var.tags
}
```

### Job Completion Trigger
```hcl
resource "aws_glue_trigger" "job_completion_trigger" {
  name = "${var.project_name}-completion-trigger"
  type = "CONDITIONAL"
  
  description = "Trigger after crawler completion"
  enabled     = true

  predicate {
    conditions {
      job_name         = aws_glue_job.etl_job.name
      logical_operator = "EQUALS"
      state           = "SUCCEEDED"
    }
  }

  actions {
    job_name = aws_glue_job.streaming_job.name
  }

  tags = var.tags
}
```

### On-Demand Trigger
```hcl
resource "aws_glue_trigger" "on_demand_trigger" {
  name = "${var.project_name}-on-demand-trigger"
  type = "ON_DEMAND"
  
  description = "Manual trigger for testing"
  enabled     = true

  actions {
    crawler_name = aws_glue_crawler.s3_crawler.name
  }

  tags = var.tags
}
```

## Glue Workflows

```hcl
resource "aws_glue_workflow" "etl_workflow" {
  name        = "${var.project_name}-etl-workflow"
  description = "Complete ETL workflow"

  default_run_properties = {
    "glue:workflow.targetDatabase" = aws_glue_catalog_database.database.name
    "glue:workflow.sourceS3Path"   = "s3://${aws_s3_bucket.data_bucket.bucket}/raw/"
    "glue:workflow.targetS3Path"   = "s3://${aws_s3_bucket.data_bucket.bucket}/processed/"
  }

  tags = var.tags
}

# Workflow triggers
resource "aws_glue_trigger" "workflow_start" {
  name         = "${var.project_name}-workflow-start"
  type         = "ON_DEMAND"
  workflow_name = aws_glue_workflow.etl_workflow.name

  actions {
    crawler_name = aws_glue_crawler.s3_crawler.name
  }
}

resource "aws_glue_trigger" "workflow_job" {
  name         = "${var.project_name}-workflow-job"
  type         = "CONDITIONAL"
  workflow_name = aws_glue_workflow.etl_workflow.name

  predicate {
    conditions {
      crawler_name     = aws_glue_crawler.s3_crawler.name
      crawl_state     = "SUCCEEDED"
      logical_operator = "EQUALS"
    }
  }

  actions {
    job_name = aws_glue_job.etl_job.name
  }
}
```

## Glue Connections

### RDS Connection
```hcl
resource "aws_glue_connection" "rds_connection" {
  name = "${var.project_name}-rds-connection"

  connection_properties = {
    JDBC_CONNECTION_URL = "jdbc:postgresql://${aws_db_instance.postgres.endpoint}/${aws_db_instance.postgres.db_name}"
    USERNAME           = var.db_username
    PASSWORD           = var.db_password
  }

  physical_connection_requirements {
    availability_zone      = var.availability_zone
    security_group_id_list = [aws_security_group.glue_sg.id]
    subnet_id             = aws_subnet.private.id
  }

  tags = var.tags
}
```

### MongoDB Connection
```hcl
resource "aws_glue_connection" "mongodb_connection" {
  name = "${var.project_name}-mongodb-connection"

  connection_properties = {
    JDBC_CONNECTION_URL = "mongodb://${var.mongodb_host}:${var.mongodb_port}/${var.mongodb_database}"
    USERNAME           = var.mongodb_username
    PASSWORD           = var.mongodb_password
  }

  physical_connection_requirements {
    security_group_id_list = [aws_security_group.glue_sg.id]
    subnet_id             = aws_subnet.private.id
  }

  tags = var.tags
}
```

## Security Configuration

```hcl
resource "aws_glue_security_configuration" "security_config" {
  name = "${var.project_name}-security-config"

  encryption_configuration {
    cloudwatch_encryption {
      cloudwatch_encryption_mode = "SSE-KMS"
      kms_key_arn                = aws_kms_key.glue_key.arn
    }

    job_bookmarks_encryption {
      job_bookmarks_encryption_mode = "CSE-KMS"
      kms_key_arn                  = aws_kms_key.glue_key.arn
    }

    s3_encryption {
      kms_key_arn        = aws_kms_key.glue_key.arn
      s3_encryption_mode = "SSE-KMS"
    }
  }
}

# KMS Key for Glue encryption
resource "aws_kms_key" "glue_key" {
  description             = "KMS key for Glue encryption"
  deletion_window_in_days = 7

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "Enable IAM User Permissions"
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
        }
        Action   = "kms:*"
        Resource = "*"
      },
      {
        Sid    = "Allow Glue Service"
        Effect = "Allow"
        Principal = {
          Service = "glue.amazonaws.com"
        }
        Action = [
          "kms:Decrypt",
          "kms:GenerateDataKey"
        ]
        Resource = "*"
      }
    ]
  })

  tags = var.tags
}

resource "aws_kms_alias" "glue_key_alias" {
  name          = "alias/${var.project_name}-glue-key"
  target_key_id = aws_kms_key.glue_key.key_id
}
```

## Data Quality

```hcl
resource "aws_glue_data_quality_ruleset" "data_quality_rules" {
  name        = "${var.project_name}-data-quality-rules"
  description = "Data quality rules for customer data"
  ruleset     = file("${path.module}/data_quality_rules.txt")

  target_table {
    database_name = aws_glue_catalog_database.database.name
    table_name    = aws_glue_catalog_table.customers_table.name
  }

  tags = var.tags
}
```

## Variables & Outputs

### Variables
```hcl
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
  validation {
    condition     = can(regex("^[a-z0-9-]+$", var.project_name))
    error_message = "Project name must contain only lowercase letters, numbers, and hyphens."
  }
}

variable "database_name" {
  description = "Glue catalog database name"
  type        = string
  default     = "default"
}

variable "environment" {
  description = "Environment (dev, staging, prod)"
  type        = string
  default     = "dev"
  
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}

variable "tags" {
  description = "Tags to apply to all resources"
  type        = map(string)
  default = {
    Project     = "data-platform"
    Environment = "dev"
    ManagedBy   = "terraform"
  }
}

# Networking variables
variable "vpc_id" {
  description = "VPC ID for Glue connections"
  type        = string
  default     = ""
}

variable "subnet_ids" {
  description = "Subnet IDs for Glue connections"
  type        = list(string)
  default     = []
}

variable "availability_zone" {
  description = "Availability zone for Glue connections"
  type        = string
  default     = "us-east-1a"
}

# Database connection variables
variable "db_username" {
  description = "Database username"
  type        = string
  sensitive   = true
}

variable "db_password" {
  description = "Database password"
  type        = string
  sensitive   = true
}
```

### Outputs
```hcl
output "glue_database_name" {
  description = "Name of the Glue catalog database"
  value       = aws_glue_catalog_database.database.name
}

output "glue_database_arn" {
  description = "ARN of the Glue catalog database"
  value       = aws_glue_catalog_database.database.arn
}

output "glue_role_arn" {
  description = "ARN of the Glue service role"
  value       = aws_iam_role.glue_role.arn
}

output "glue_crawler_role_arn" {
  description = "ARN of the Glue crawler role"
  value       = aws_iam_role.glue_crawler_role.arn
}

output "etl_job_name" {
  description = "Name of the ETL job"
  value       = aws_glue_job.etl_job.name
}

output "etl_job_arn" {
  description = "ARN of the ETL job"
  value       = aws_glue_job.etl_job.arn
}

output "s3_crawler_name" {
  description = "Name of the S3 crawler"
  value       = aws_glue_crawler.s3_crawler.name
}

output "s3_crawler_arn" {
  description = "ARN of the S3 crawler"
  value       = aws_glue_crawler.s3_crawler.arn
}

output "workflow_name" {
  description = "Name of the Glue workflow"
  value       = aws_glue_workflow.etl_workflow.name
}

output "workflow_arn" {
  description = "ARN of the Glue workflow"
  value       = aws_glue_workflow.etl_workflow.arn
}

output "security_configuration_name" {
  description = "Name of the Glue security configuration"
  value       = aws_glue_security_configuration.security_config.name
}

output "data_bucket_name" {
  description = "Name of the data S3 bucket"
  value       = aws_s3_bucket.data_bucket.bucket
}

output "scripts_bucket_name" {
  description = "Name of the scripts S3 bucket"
  value       = aws_s3_bucket.scripts_bucket.bucket
}
```

## Best Practices

### 1. Resource Naming
```hcl
locals {
  name_prefix = "${var.project_name}-${var.environment}"
  
  common_tags = merge(var.tags, {
    Environment = var.environment
    Project     = var.project_name
    ManagedBy   = "terraform"
  })
}

# Use consistent naming
resource "aws_glue_job" "example" {
  name = "${local.name_prefix}-example-job"
  # ...
  tags = local.common_tags
}
```

### 2. Environment-Specific Configuration
```hcl
locals {
  environment_config = {
    dev = {
      worker_type       = "G.1X"
      number_of_workers = 2
      max_concurrent_runs = 1
    }
    staging = {
      worker_type       = "G.1X"  
      number_of_workers = 5
      max_concurrent_runs = 2
    }
    prod = {
      worker_type       = "G.2X"
      number_of_workers = 10
      max_concurrent_runs = 5
    }
  }
  
  config = local.environment_config[var.environment]
}

resource "aws_glue_job" "etl_job" {
  worker_type       = local.config.worker_type
  number_of_workers = local.config.number_of_workers
  
  execution_property {
    max_concurrent_runs = local.config.max_concurrent_runs
  }
}
```

### 3. Security Best Practices
```hcl
# Separate roles for different functions
resource "aws_iam_role" "glue_etl_role" {
  name = "${local.name_prefix}-glue-etl-role"
  # Minimal permissions for ETL jobs
}

resource "aws_iam_role" "glue_crawler_role" {
  name = "${local.name_prefix}-glue-crawler-role"
  # Minimal permissions for crawlers
}

# Use least privilege principle
resource "aws_iam_role_policy" "s3_specific_access" {
  name = "${local.name_prefix}-s3-specific-access"
  role = aws_iam_role.glue_etl_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject"
        ]
        Resource = [
          "${aws_s3_bucket.data_bucket.arn}/processed/*"
        ]
      }
    ]
  })
}
```

### 4. Data Source Organization
```hcl
# Use modules for different data sources
module "customer_data_pipeline" {
  source = "./modules/glue-pipeline"
  
  pipeline_name    = "customer-data"
  database_name    = aws_glue_catalog_database.database.name
  source_s3_path   = "s3://${aws_s3_bucket.data_bucket.bucket}/customers/"
  target_s3_path   = "s3://${aws_s3_bucket.processed_bucket.bucket}/customers/"
  glue_role_arn    = aws_iam_role.glue_role.arn
  
  tags = local.common_tags
}

module "product_data_pipeline" {
  source = "./modules/glue-pipeline"
  
  pipeline_name    = "product-data"
  database_name    = aws_glue_catalog_database.database.name
  source_s3_path   = "s3://${aws_s3_bucket.data_bucket.bucket}/products/"
  target_s3_path   = "s3://${aws_s3_bucket.processed_bucket.bucket}/products/"
  glue_role_arn    = aws_iam_role.glue_role.arn
  
  tags = local.common_tags
}
```

### 5. Monitoring and Logging
```hcl
# CloudWatch Log Groups
resource "aws_cloudwatch_log_group" "glue_job_logs" {
  name              = "/aws-glue/jobs/${aws_glue_job.etl_job.name}"
  retention_in_days = 30
  
  tags = local.common_tags
}

# CloudWatch Alarms
resource "aws_cloudwatch_metric_alarm" "job_failure_alarm" {
  alarm_name          = "${local.name_prefix}-glue-job-failures"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "glue.driver.aggregate.numFailedTasks"
  namespace           = "Glue"
  period              = "300"
  statistic           = "Sum"
  threshold           = "0"
  alarm_description   = "This metric monitors glue job failures"

  dimensions = {
    JobName = aws_glue_job.etl_job.name
  }

  tags = local.common_tags
}
```

### 6. S3 Bucket Configuration
```hcl
# Separate buckets for different purposes
resource "aws_s3_bucket" "data_bucket" {
  bucket = "${local.name_prefix}-data-${random_suffix.bucket_suffix.result}"
  tags   = local.common_tags
}

resource "aws_s3_bucket" "scripts_bucket" {
  bucket = "${local.name_prefix}-scripts-${random_suffix.bucket_suffix.result}"
  tags   = local.common_tags
}

resource "aws_s3_bucket" "temp_bucket" {
  bucket = "${local.name_prefix}-temp-${random_suffix.bucket_suffix.result}"
  tags   = local.common_tags
}

resource "aws_s3_bucket" "logs_bucket" {
  bucket
