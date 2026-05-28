# Terraform Introduction for Beginners
# Terraform for AWS: A First-Timer's Complete Guide

Let's build this from the ground up. Before touching any code, let's make sure the core concepts click.

---

## What is Terraform, really?

Terraform is an **Infrastructure as Code (IaC)** tool. Instead of clicking around the AWS console to create a VPC or Lambda function, you describe what you want in `.tf` files, run a command, and Terraform figures out how to make AWS match your description.

The magic is that Terraform tracks **state** — it remembers what it already created, so on your next run it only changes what's different. Think of it like a git diff, but for cloud infrastructure.

---

## Core Concepts Before You Write a Line

**Providers** tell Terraform which cloud to talk to. For AWS, you use the `hashicorp/aws` provider — it's essentially a plugin that knows how to speak AWS's API.

**Resources** are the actual things you're creating — an RDS instance, a Lambda function, a VPC, etc. Each resource has a type (`aws_lambda_function`) and a name you make up (`my_api`).

**Variables** let you parameterize your config so the same code can deploy differently to dev vs prod (e.g., a `db.t3.micro` in dev and a `db.r6g.large` in prod).

**Outputs** are values Terraform prints after applying — like a database endpoint or Lambda ARN — useful for wiring things together or for humans to see.

**State** is a `.tfstate` file (or remote equivalent) that Terraform uses to track what it owns. You should **never edit this by hand**.

**Modules** are reusable bundles of resources — like a function you call in programming. You write a VPC module once and call it three times for dev, staging, and prod.

---

## Project Structure

Here's the folder layout you'll build toward. This pattern is called **workspaces-with-modules** and is one of the most practical approaches for multi-environment setups:

```
my-project/
├── environments/
│   ├── dev/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── terraform.tfvars
│   ├── staging/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── terraform.tfvars
│   └── prod/
│       ├── main.tf
│       ├── variables.tf
│       └── terraform.tfvars
└── modules/
    ├── networking/       # VPC, subnets, security groups
    ├── database/         # RDS
    ├── compute/          # Lambda
    └── iam/              # Roles and policies
```

Each environment folder is completely independent — running `terraform apply` in `dev/` touches only dev infrastructure. The `modules/` folder contains the shared blueprints each environment uses.

---
## Step 0: Setup AWS Account with Terraform
Look at the steps and figure out the point you are at with your AWS account:
1. Setup account in AWS
2. Make a Admin Users using the AWS default: arn:aws:iam::aws:policy/AdministratorAccess
3. Next look to create a Terraform User called ==> terraform-deployer-user
	a. Start by going to IAM to create an IAM Policy called terraform-deployer-policy (since it commonly uses over the 10 max policies)

	b. The go to IAM user to create the user and attach the policy.
	Example: [Terraform-Policy-Example](https://github.com/ajlinhard/byte-size-docs/blob/main/CI-CD/Terraform/Terraform-IAM-Policy-Example.json)

     c. Make suure to setup with no AWS Console Access to manage access by Least Privelage.

**A few things to note:**
- VPC access is via ec2:* — VPC is part of the EC2 API surface
- IAM full access is powerful — if you want to lock it down, you can restrict it to iam:PassRole + specific actions Terraform actually needs
- This counts as 1 policy, solving your quota problem entirely
- AWS has a 6,144 character limit on inline policies — this JSON is well within that limit as a managed policy (which has a 6,144 character limit too, but managed policies can request a quota increase if needed)

## Step 1: Install AWS CLI and Terraform

```powershell
winget install Amazon.AWSCLI
winget install Hashicorp.Terraform

# Verify
terraform -v
```

For AWS credentials, the simplest approach locally is the AWS CLI:

```bash
aws configure
# Enter your Access Key ID, Secret Access Key, region (e.g. us-east-1), output format (json)
```

Terraform automatically picks up credentials from `~/.aws/credentials`. In CI/CD pipelines you'd use environment variables (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`) or IAM roles.

---

## Step 2: Remote State (Do This First — Don't Skip It)

By default, Terraform saves state to a local file. This breaks the moment two people work on the same project. You need **remote state** in S3 with a **DynamoDB lock table** to prevent two applies from running simultaneously.

Create this once manually (it's a chicken-and-egg situation — you can't use Terraform to create the bucket that Terraform state lives in):

```bash
# Create the S3 bucket for state
aws s3api create-bucket \
  --bucket my-project-terraform-state \
  --region us-east-1

# Enable versioning so you can recover from bad state
aws s3api put-bucket-versioning \
  --bucket my-project-terraform-state \
  --versioning-configuration Status=Enabled

# Create DynamoDB table for state locking
aws dynamodb create-table \
  --table-name terraform-state-lock \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST
```

---

## Step 3: The Networking Module

This module creates the VPC, public/private subnets, and an internet gateway. Everything else lives inside this network.

**`modules/networking/main.tf`**
```hcl
# The VPC is your private network in AWS — like your own isolated data center
resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr        # e.g. "10.0.0.0/16" — 65k IPs
  enable_dns_hostnames = true                # Lets resources get DNS names
  enable_dns_support   = true

  tags = {
    Name        = "${var.project}-${var.environment}-vpc"
    Environment = var.environment
  }
}

# Public subnets — resources here can reach the internet directly
# We create one per availability zone for redundancy
resource "aws_subnet" "public" {
  count             = length(var.availability_zones)
  vpc_id            = aws_vpc.main.id
  cidr_block        = var.public_subnet_cidrs[count.index]
  availability_zone = var.availability_zones[count.index]

  map_public_ip_on_launch = true  # Instances here get a public IP automatically

  tags = {
    Name        = "${var.project}-${var.environment}-public-${count.index + 1}"
    Environment = var.environment
  }
}

# Private subnets — Lambda and RDS live here, no direct internet access
resource "aws_subnet" "private" {
  count             = length(var.availability_zones)
  vpc_id            = aws_vpc.main.id
  cidr_block        = var.private_subnet_cidrs[count.index]
  availability_zone = var.availability_zones[count.index]

  tags = {
    Name        = "${var.project}-${var.environment}-private-${count.index + 1}"
    Environment = var.environment
  }
}

# Internet Gateway — the door between your VPC and the public internet
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "${var.project}-${var.environment}-igw"
  }
}

# Route table for public subnets — sends internet-bound traffic to the IGW
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"                    # All traffic not destined for the VPC...
    gateway_id = aws_internet_gateway.main.id    # ...goes out through the internet gateway
  }

  tags = {
    Name = "${var.project}-${var.environment}-public-rt"
  }
}

# Associate the public route table with each public subnet
resource "aws_route_table_association" "public" {
  count          = length(aws_subnet.public)
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

# NAT Gateway — lets private subnet resources reach the internet (for updates, API calls)
# but blocks inbound connections. Requires an Elastic IP.
resource "aws_eip" "nat" {
  count  = var.enable_nat_gateway ? 1 : 0   # Skip in dev to save money
  domain = "vpc"
}

resource "aws_nat_gateway" "main" {
  count         = var.enable_nat_gateway ? 1 : 0
  allocation_id = aws_eip.nat[0].id
  subnet_id     = aws_subnet.public[0].id   # NAT gateway lives in a PUBLIC subnet

  tags = {
    Name = "${var.project}-${var.environment}-nat"
  }
}

# Route table for private subnets — sends internet traffic through NAT
resource "aws_route_table" "private" {
  count  = var.enable_nat_gateway ? 1 : 0
  vpc_id = aws_vpc.main.id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.main[0].id
  }

  tags = {
    Name = "${var.project}-${var.environment}-private-rt"
  }
}

resource "aws_route_table_association" "private" {
  count          = var.enable_nat_gateway ? length(aws_subnet.private) : 0
  subnet_id      = aws_subnet.private[count.index].id
  route_table_id = aws_route_table.private[0].id
}
```

**`modules/networking/variables.tf`**
```hcl
variable "project"             { type = string }
variable "environment"         { type = string }
variable "vpc_cidr"            { type = string }
variable "availability_zones"  { type = list(string) }
variable "public_subnet_cidrs" { type = list(string) }
variable "private_subnet_cidrs" { type = list(string) }
variable "enable_nat_gateway"  {
  type    = bool
  default = true
}
```

**`modules/networking/outputs.tf`**
```hcl
output "vpc_id"             { value = aws_vpc.main.id }
output "public_subnet_ids"  { value = aws_subnet.public[*].id }
output "private_subnet_ids" { value = aws_subnet.private[*].id }
```

---

## Step 4: The IAM Module

IAM is how you control *what* can do *what* in AWS. A Lambda function needs a **role** (its identity) and **policies** (its permissions).

**`modules/iam/main.tf`**
```hcl
# The Lambda execution role — this is the identity Lambda assumes when it runs
resource "aws_iam_role" "lambda_execution" {
  name = "${var.project}-${var.environment}-lambda-role"

  # Trust policy: says "only Lambda service can assume this role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}

# Attach AWS's managed policy for basic Lambda logging to CloudWatch
resource "aws_iam_role_policy_attachment" "lambda_basic" {
  role       = aws_iam_role.lambda_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Attach VPC access policy — required if Lambda runs inside your VPC
resource "aws_iam_role_policy_attachment" "lambda_vpc" {
  role       = aws_iam_role.lambda_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
}

# A custom inline policy — add whatever permissions your Lambda actually needs
resource "aws_iam_role_policy" "lambda_custom" {
  name = "${var.project}-${var.environment}-lambda-policy"
  role = aws_iam_role.lambda_execution.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["secretsmanager:GetSecretValue"]   # e.g., to fetch DB credentials
        Resource = var.secrets_arns
      }
    ]
  })
}
```

**`modules/iam/outputs.tf`**
```hcl
output "lambda_role_arn"  { value = aws_iam_role.lambda_execution.arn }
output "lambda_role_name" { value = aws_iam_role.lambda_execution.name }
```

---

## Step 5: The Database Module (RDS)

RDS instances should always live in private subnets and require a **subnet group** (telling RDS which subnets it can use) and a **security group** (its firewall rules).

**`modules/database/main.tf`**
```hcl
# Security group for RDS — controls who can connect to the database
resource "aws_security_group" "rds" {
  name        = "${var.project}-${var.environment}-rds-sg"
  description = "Security group for RDS"
  vpc_id      = var.vpc_id

  # Only allow inbound PostgreSQL (5432) from the Lambda security group
  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [var.lambda_security_group_id]
  }

  # No direct egress needed for RDS
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "${var.project}-${var.environment}-rds-sg"
    Environment = var.environment
  }
}

# Subnet group — tells RDS which subnets it can place instances in
# Multi-AZ requires subnets in at least 2 availability zones
resource "aws_db_subnet_group" "main" {
  name       = "${var.project}-${var.environment}-db-subnet-group"
  subnet_ids = var.private_subnet_ids

  tags = {
    Name        = "${var.project}-${var.environment}-db-subnet-group"
    Environment = var.environment
  }
}

# The RDS instance itself
resource "aws_db_instance" "main" {
  identifier = "${var.project}-${var.environment}-db"

  engine         = "postgres"
  engine_version = "15.4"
  instance_class = var.db_instance_class   # e.g. "db.t3.micro" in dev, "db.r6g.large" in prod

  allocated_storage     = var.db_storage
  max_allocated_storage = var.db_max_storage   # Enables autoscaling up to this limit
  storage_encrypted     = true                  # Always encrypt your data at rest

  db_name  = var.db_name
  username = var.db_username
  password = var.db_password   # In practice, use aws_secretsmanager_secret instead

  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.rds.id]

  multi_az            = var.multi_az          # true in prod, false in dev/staging
  publicly_accessible = false                  # NEVER true — always keep DB private
  skip_final_snapshot = var.environment != "prod"  # Always snapshot prod before destroy

  backup_retention_period = var.environment == "prod" ? 7 : 1
  deletion_protection     = var.environment == "prod"  # Prevents accidental terraform destroy

  tags = {
    Environment = var.environment
  }
}
```

**`modules/database/variables.tf`**
```hcl
variable "project"                  { type = string }
variable "environment"              { type = string }
variable "vpc_id"                   { type = string }
variable "private_subnet_ids"       { type = list(string) }
variable "lambda_security_group_id" { type = string }
variable "db_instance_class"        { type = string }
variable "db_storage"               { type = number }
variable "db_max_storage"           { type = number }
variable "db_name"                  { type = string }
variable "db_username"              { type = string }
variable "db_password"              { type = string; sensitive = true }
variable "multi_az"                 { type = bool; default = false }
```

**`modules/database/outputs.tf`**
```hcl
output "db_endpoint"         { value = aws_db_instance.main.endpoint }
output "db_name"             { value = aws_db_instance.main.db_name }
output "rds_security_group_id" { value = aws_security_group.rds.id }
```

---

## Step 6: The Compute Module (Lambda)

**`modules/compute/main.tf`**
```hcl
# Security group for Lambda — controls outbound connections Lambda can make
resource "aws_security_group" "lambda" {
  name        = "${var.project}-${var.environment}-lambda-sg"
  description = "Security group for Lambda functions"
  vpc_id      = var.vpc_id

  # Lambda needs to make outbound calls (to RDS, AWS APIs, etc.)
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "${var.project}-${var.environment}-lambda-sg"
    Environment = var.environment
  }
}

# Package your Lambda code into a zip file
# In practice, you might build this in CI and reference a pre-built S3 artifact
data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = var.lambda_source_path
  output_path = "${path.module}/lambda.zip"
}

resource "aws_lambda_function" "api" {
  function_name = "${var.project}-${var.environment}-api"
  role          = var.lambda_role_arn

  # Where your code comes from
  filename         = data.archive_file.lambda_zip.output_path
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256  # Forces redeploy on change
  handler          = "index.handler"   # filename.exportedFunctionName
  runtime          = "nodejs20.x"

  # Tune these per environment
  memory_size = var.lambda_memory
  timeout     = var.lambda_timeout

  # Run Lambda inside the VPC so it can reach RDS
  vpc_config {
    subnet_ids         = var.private_subnet_ids
    security_group_ids = [aws_security_group.lambda.id]
  }

  # Pass environment-specific config to your function
  environment {
    variables = {
      ENVIRONMENT = var.environment
      DB_HOST     = var.db_endpoint
      DB_NAME     = var.db_name
      NODE_ENV    = var.environment == "prod" ? "production" : "development"
    }
  }

  tags = {
    Environment = var.environment
  }
}

# Optional: Function URL — gives Lambda a public HTTPS endpoint without API Gateway
resource "aws_lambda_function_url" "api" {
  count              = var.create_function_url ? 1 : 0
  function_name      = aws_lambda_function.api.function_name
  authorization_type = "NONE"   # or "AWS_IAM" for authenticated access
}
```

**`modules/compute/outputs.tf`**
```hcl
output "lambda_security_group_id" { value = aws_security_group.lambda.id }
output "lambda_function_name"     { value = aws_lambda_function.api.function_name }
output "lambda_function_arn"      { value = aws_lambda_function.api.arn }
output "lambda_function_url"      { value = var.create_function_url ? aws_lambda_function_url.api[0].function_url : null }
```

---

## Step 7: Wiring It Together in Each Environment

Now each environment's `main.tf` just calls the modules with different values. This is the payoff for all that module work.

**`environments/dev/main.tf`**
```hcl
terraform {
  required_version = ">= 1.6"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # Remote state — each environment gets its own state file
  backend "s3" {
    bucket         = "my-project-terraform-state"
    key            = "dev/terraform.tfstate"   # <-- changes per environment
    region         = "us-east-1"
    dynamodb_table = "terraform-state-lock"
    encrypt        = true
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = var.project
      Environment = var.environment
      ManagedBy   = "terraform"
    }
  }
}

# 1. Network layer — everything else depends on this
module "networking" {
  source = "../../modules/networking"

  project      = var.project
  environment  = var.environment
  vpc_cidr     = "10.0.0.0/16"

  availability_zones   = ["us-east-1a", "us-east-1b"]
  public_subnet_cidrs  = ["10.0.1.0/24", "10.0.2.0/24"]
  private_subnet_cidrs = ["10.0.10.0/24", "10.0.11.0/24"]

  enable_nat_gateway = false   # Save ~$35/mo in dev — Lambda in VPC can skip NAT
                                # if you use VPC endpoints for AWS services
}

# 2. IAM — Lambda needs its role before it can exist
module "iam" {
  source = "../../modules/iam"

  project     = var.project
  environment = var.environment
  secrets_arns = ["*"]   # In prod, lock this down to specific secret ARNs
}

# 3. Compute — we need the security group ID before creating the DB
module "compute" {
  source = "../../modules/compute"

  project     = var.project
  environment = var.environment

  vpc_id              = module.networking.vpc_id
  private_subnet_ids  = module.networking.private_subnet_ids
  lambda_role_arn     = module.iam.lambda_role_arn
  lambda_source_path  = "../../../src"   # path to your actual code
  lambda_memory       = 256
  lambda_timeout      = 30
  db_endpoint         = module.database.db_endpoint
  db_name             = var.db_name
  create_function_url = true
}

# 4. Database — references Lambda's security group to allow inbound connections
module "database" {
  source = "../../modules/database"

  project     = var.project
  environment = var.environment

  vpc_id                   = module.networking.vpc_id
  private_subnet_ids       = module.networking.private_subnet_ids
  lambda_security_group_id = module.compute.lambda_security_group_id

  db_instance_class = "db.t3.micro"   # Small and cheap for dev
  db_storage        = 20
  db_max_storage    = 50
  db_name           = var.db_name
  db_username       = var.db_username
  db_password       = var.db_password
  multi_az          = false
}
```

**`environments/dev/terraform.tfvars`**
```hcl
project     = "my-project"
environment = "dev"
aws_region  = "us-east-1"
db_name     = "myapp"
db_username = "admin"
# db_password is kept out of tfvars — pass via env var: TF_VAR_db_password=...
```

For **staging**, you'd copy this structure and change:
- The backend `key` to `staging/terraform.tfstate`
- `enable_nat_gateway = true`
- `db_instance_class = "db.t3.small"`
- `lambda_memory = 512`

For **prod**:
- `enable_nat_gateway = true`
- `db_instance_class = "db.r6g.large"`
- `multi_az = true`
- `lambda_memory = 1024`
- `deletion_protection = true`

---

## Step 8: The Workflow

```bash
cd environments/dev

# Download providers and modules (do this once and after any module changes)
terraform init

# Preview every change Terraform will make — read this carefully!
terraform plan

# Apply the changes (Terraform will ask for confirmation)
terraform apply

# When you're done with dev resources (optional)
terraform destroy
```

**The plan output** is your safety net. It shows `+` for creates, `~` for updates, and `-` for destroys. Always read it before applying, especially in prod.

---

## Key Things to Get Right From the Start

**Never commit secrets.** Add `*.tfvars` to `.gitignore` if it contains passwords. Use `TF_VAR_db_password` environment variables or AWS Secrets Manager instead.

**Lock your provider versions.** `~> 5.0` means "any 5.x version" — this prevents surprise breaking changes. Run `terraform init -upgrade` intentionally when you want to update.

**Terraform is declarative, not procedural.** The order you write resources doesn't matter — Terraform builds a dependency graph automatically. It knows to create the VPC before the subnets because the subnet references `aws_vpc.main.id`.

**The `depends_on` escape hatch.** Terraform usually figures out ordering from references, but occasionally you need explicit ordering. Use `depends_on = [module.networking]` sparingly.

**State is sacred.** Never delete your S3 state bucket. If state gets corrupted, you lose track of what Terraform owns, and you'll have to manually import resources back or risk duplicate infrastructure.

---

This structure scales well — you can add more modules (S3, CloudFront, ElastiCache), add more environments, or promote the same module version through dev → staging → prod as part of a CI/CD pipeline. The key insight is that the modules stay the same; only the values passed into them change per environment.
