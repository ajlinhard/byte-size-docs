# =============================================================================
# DEV ENVIRONMENT - Andrew Linhard (per-developer RDS instance)
# =============================================================================
# Usage:
#   terraform workspace select dev-alinhard
#   terraform apply -var-file="environments/dev-alinhard.tfvars"
# =============================================================================

aws_region = "us-gov-east-1"

# Tag policy compliance: workspace is "dev-alinhard" but AWS tag policy only allows "dev"
environment_tag = "dev"

# Map workspace name to account ID (needed by locals in main.tf)
account_ids = {
  dev-alinhard = "532429412559"
}

# VPC Configuration
vpc_id             = "vpc-0b4cc20a498c20fc1"
subnet_ids         = []
security_group_ids = []

lambda_role_arn = "arn:aws-us-gov:iam::532429412559:role/claims-api-role"

# Third-party layers (empty - not needed for container-based Lambda)
third_party_standard_layers = []
third_party_soap_layers     = []

# Override Lambda function maps to EMPTY — this workspace is RDS-only.
# The existing 'dev' workspace handles all Lambda infrastructure.
# Without this override, Terraform would try to create duplicate Lambdas/SQS.
lambda_functions       = {}
adhoc_lambda_functions = {}
lambda_env_vars        = {}

environment_config = {
  log_level       = "DEBUG"
  lambda_alias    = "DEV"
  publish_version = false
}

# =============================================================================
# RDS DEV - LAYER 1: Long-lived infra (ECR, Lambda, IAM, log group)
# =============================================================================
# Layer 1 is owned by the dev-rds-shared workspace (see issue #378). This
# per-developer workspace consumes those resources via data lookups in
# rds_dev.tf — no creation, no AlreadyExists noise on first apply.

enable_rds_infra = false

# =============================================================================
# RDS DEV - LAYER 2: Ephemeral RDS instance (toggle to spin up/tear down)
# =============================================================================
# Set to true when you need a database, false when you're done.
# This only affects the RDS instance — Lambda/ECR/IAM stay intact.

enable_rds_instance = false

rds_dev_config = {
  identifier     = "claims-api-dev-alinhard"
  instance_class = "db.t3.micro"
  engine_version = "17.4"
  database_name  = "claims"
  owner          = "alinhard"
  purpose        = "dev-sandbox"
}

# Existing security groups (already have correct cross-referenced ingress/egress rules)
rds_security_group_id    = "sg-0f158360aa8636520" # mdc-dev-rds
lambda_security_group_id = "sg-05a4c132c420183b5" # mdc-dev-lambda

# RDS subnets (2 AZs for db_subnet_group)
rds_subnet_ids = [
  "subnet-0efd3ef3fbc82c402", # mdc-dev-app-rds-az1-subnet (us-gov-east-1a)
  "subnet-0adf4bada7950f218"  # mdc-dev-app-rds-az2-subnet (us-gov-east-1b)
]

# Lambda subnets (Lambda initializer runs in these)
lambda_subnet_ids = [
  "subnet-0c238697e3adb3eda", # mdc-dev-app-lambda-az1-subnet (us-gov-east-1a)
  "subnet-055871b7ee5db9476"  # mdc-dev-app-lambda-az2-subnet (us-gov-east-1b)
]

# Additional CIDR blocks for RDS access (VPN, etc.)
rds_additional_ingress_cidrs = []

# Lambda initializer - deploy but don't auto-invoke (run manually when ready)
run_rds_initializer       = false
rds_initializer_image_uri = "532429412559.dkr.ecr.us-gov-east-1.amazonaws.com/claims-api-dev-rds-initializer:latest"

# =============================================================================
# AURORA DEV - LAYER 2: Ephemeral Aurora PostgreSQL cluster (toggle on/off)
# =============================================================================
# Independent of the RDS instance above. Uses the same VPC subnets + security
# group. Reuses the shared rds_initializer Lambda from dev-rds-shared.
# See issue #390 (TX-007).
#
# Workflow:
#   1. Set enable_aurora_instance = true, apply -> cluster + 2 instances come
#      up (~10 min total).
#   2. Set run_aurora_initializer = true on the next apply -> sql_build runs
#      against the writer endpoint.
#   3. Set both back to false when done -> cluster tears down. Shared Layer 1
#      in dev-rds-shared is untouched.

enable_aurora_instance = false
run_aurora_initializer = false

aurora_dev_config = {
  cluster_identifier = "claims-api-aurora-dev-alinhard"
  # Aurora Serverless v2: cluster autoscales between min/max ACUs (1 ACU ≈ 2 GB
  # RAM). 0.5 is the AWS minimum; bump max_acu if you need to burst higher.
  min_acu        = 0.5
  max_acu        = 4
  engine_version = "17.4"
  database_name  = "claims"
  owner          = "alinhard"
  purpose        = "aurora-dev-sandbox"
}

# Additional databases inside the cluster. RESERVED FOR TX-008 (#391) — leave
# empty until that work lands.
aurora_additional_databases = []
