# Terraform Overview
This tool is helpful for managing your infrastructure as code and platforms as code. Its suggested it may be slightly worst than Ansible with Paas, but it can still serve the purpose. 
This in accomplished through a declarative syntax, which means the code represents the desired state of what the user wants not the steps to accomplish that state. Writing out the steps to obtain the desired state would be imperative code.
Terrafrom will take the declarative code + the infrastructure state to create the imperative steps to provide the outcome.

## Documentation/Tutorials:
1. [Official Documentation](https://developer.hashicorp.com/terraform?product_intent=terraform)
2. [Officail Tutorials](https://developer.hashicorp.com/terraform/tutorials?product_intent=terraform)
3. [Youtube - Overview Tutorial](https://www.youtube.com/watch?v=l5k1ai_GBDE)
4. [Youtube - Basic Use Tutorial](https://www.youtube.com/watch?v=Gmrl8WkViX0)
5. [Terraform with AWS](https://developer.hashicorp.com/terraform/tutorials/aws-get-started)

## Concepts
These are the high-level important parts of Terraform
1. Providers - are the different service providers like AWS, Azure, and Kubernetes which Terraform can interact and work with
2. TF-config file - is the file containing the desired state of your infrastructure.
  a. It is 1 of 2 major inputs to Terraforms operations.
3. State - represents the current state of your infrastructure.
4. Core - the processing and acting part of Terraform responsible for taking the current to desired state for your infrastructure.
5. Declarative

## Use Case:
1. Update Production with the latest release, with easier rollback.
2. Standup Dev or Demo environments quickly.
 a. Use the destroy command to save on cost after development of demos.
3. Passing templates between teams.

## Terraform Actions:
1. **refresh** - query the infrastructure of providers to get their current state.
2. **plan** - create a execution plan to accomplished the desired state.
3. **apply** - execute the plan
4. **destroy** - delete/destroy the current infrastructure in the correct order.


## Basic Terraform File
```yaml
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.16"
    }
  }

  required_version = ">= 1.2.0"
}

provider "aws" {
    region = "us-east-1"
}

resource "aws_s3_bucket" "myTestTerraform" {
    bucket = "starbound-terraform-bucket"
    acl = "private"
}
```

---
## Teeraform States Across Dev, Test, Prod
No — each environment gets its own isolated state file. The `key` parameter is what separates them:

```
dev/terraform.tfstate        ← dev state
staging/terraform.tfstate    ← staging state  
production/terraform.tfstate ← production state
```

All three live in the **same S3 bucket** and use the **same DynamoDB lock table**, but because the `key` paths differ, Terraform treats them as completely independent state files. Changes to dev have zero effect on the production state, and vice versa.

## How you'd typically manage this

Since the `backend` block doesn't allow variables, there are two common patterns:

**Option 1 — Separate directories per environment (most explicit)**
```
infra/
├── dev/
│   └── main.tf        # backend key = "dev/terraform.tfstate"
├── staging/
│   └── main.tf        # backend key = "staging/terraform.tfstate"
└── production/
    └── main.tf        # backend key = "production/terraform.tfstate"
```

**Option 2 — `-backend-config` flag at init time (one codebase)**
```bash
# Same .tf files, different state per init
terraform init -backend-config="key=dev/terraform.tfstate"
terraform init -backend-config="key=staging/terraform.tfstate"
terraform init -backend-config="key=production/terraform.tfstate"
```
This lets you use a partial backend block in code and inject the key at runtime — common in CI/CD pipelines.

## What's shared vs. isolated

| Resource | Shared across envs? |
|---|---|
| S3 bucket | ✅ Yes (just a container) |
| DynamoDB lock table | ✅ Yes (locks are keyed by state path) |
| State file | ❌ No — isolated per `key` |
| Actual AWS resources | ❌ No — each env deploys its own |

The single-account setup means your IAM permissions, VPCs, and resource names need to be carefully namespaced (e.g. `dev-my-bucket`, `prod-my-bucket`) to avoid collisions — but the Terraform state isolation itself is solid with this approach.

---
## Terraform Backend (AWS)
Great question. Here's how Terraform uses both services under the hood:

## S3 — Stores the State File

The state file (`terraform.tfstate`) is a JSON snapshot of every resource Terraform manages. S3 is just an object store for this file.

**The read/write cycle on every Terraform operation:**
```
terraform plan/apply
       │
       ▼
1. Download state    → GET s3://ajlinhard-acct-terraform-state/dev/terraform.tfstate
2. Compare vs real   → API calls to AWS to inspect actual resources
3. Calculate diff    → What needs to change?
4. Apply changes     → Create/update/destroy resources
5. Upload new state  → PUT s3://ajlinhard-acct-terraform-state/dev/terraform.tfstate
```

The state file itself looks like this internally:
```json
{
  "version": 4,
  "terraform_version": "1.6.0",
  "serial": 42,          // increments every save — prevents overwriting newer state
  "lineage": "abc-123",  // unique ID for this state's lifetime
  "resources": [
    {
      "type": "aws_instance",
      "name": "web",
      "instances": [{ "attributes": { "id": "i-1234567890" } }]
    }
  ]
}
```

---

## DynamoDB — Handles the State Lock

The lock prevents two people (or two CI jobs) from running `terraform apply` at the same time, which would corrupt the state file.

**The lock lifecycle:**
```
terraform apply starts
       │
       ▼
1. LOCK   → PutItem to DynamoDB  { LockID: "dev/terraform.tfstate", who: "user@machine", time: "..." }
       │
       ▼
2. WORK   → Download state, make changes, upload new state
       │
       ▼
3. UNLOCK → DeleteItem from DynamoDB

# If someone else runs apply while locked:
→ ConditionalCheckFailedException → Terraform exits with:
  "Error: state file already locked: ID=abc123, Who=other-user"
```

**The DynamoDB table only needs one column:**
```hcl
resource "aws_dynamodb_table" "terraform_lock" {
  name         = "terraform-state-lock"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"          # ← Terraform hardcodes this key name

  attribute {
    name = "LockID"
    type = "S"
  }
}
```

Terraform hardcodes `LockID` as the partition key — that's the only schema requirement.

---

## How They Work Together — Full Flow

```
┌─────────────────────────────────────────────────────┐
│                  terraform apply                     │
└─────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────┐     Already locked?
│  DynamoDB: PutItem  │ ──────────────────────► STOP, show error
│  LockID = "dev/..."  │
└─────────────────────┘
          │ Lock acquired
          ▼
┌─────────────────────┐
│   S3: GetObject     │  ← pull current state
│   dev/tfstate       │
└─────────────────────┘
          │
          ▼
┌─────────────────────┐
│  AWS API calls      │  ← compare state vs reality
│  (plan/diff)        │
└─────────────────────┘
          │
          ▼
┌─────────────────────┐
│  Make AWS changes   │  ← create/update/destroy resources
└─────────────────────┘
          │
          ▼
┌─────────────────────┐
│   S3: PutObject     │  ← save updated state
│   dev/tfstate       │
└─────────────────────┘
          │
          ▼
┌─────────────────────┐
│ DynamoDB: DeleteItem│  ← release lock
└─────────────────────┘
```

---

## What Happens if Terraform Crashes Mid-Apply?

The lock is **not automatically released** — which is intentional. You'd see:

```bash
terraform force-unlock <LOCK_ID>
```

This is a safety net so you manually verify the state is clean before anyone else runs apply. The `LockID` value is shown in the error message when a lock is detected.
