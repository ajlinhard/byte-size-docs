# Terraform Workspace Overview
### What Workspaces Are Actually For

Workspaces were designed for **ephemeral, lightweight environment isolation** — think personal sandbox testing, not long-lived environment promotion pipelines. The `dev-<yourname>` pattern you saw is actually their **sweet spot**.

---

### Personal / Feature Testing (Good Use Case ✅)

```
env:/dev-alice/terraform.tfstate
env:/dev-bob/terraform.tfstate
env:/dev-charlie/terraform.tfstate
```

Each developer spins up their own copy of infrastructure, tests changes, then destroys it. This is exactly what workspaces were built for — **cheap, isolated, throwaway environments**.

---

### Dev / Staging / Prod — Should You Use Workspaces?

**The honest answer: usually no, and HashiCorp themselves advise against it.**

Here's why workspaces fall short for promotion pipelines:

| Concern | Problem |
|---|---|
| **Single backend** | All workspaces share the same backend config — hard to give staging/prod their own isolated storage |
| **No access control** | Workspaces have **zero native RBAC** — nothing stops a developer from running `terraform workspace select prod` and doing `terraform destroy` |
| **Same codebase** | All workspaces use identical code, so environment-specific differences get messy |
| **State proximity** | Prod and dev state living in the same bucket is a blast radius problem |

---

### The Right Pattern for Dev / Staging / Prod

The industry standard is **separate state files via separate backends** — typically achieved through one of two approaches:

**Option A — Separate directories/repos per environment**
```
infra/
├── dev/
│   ├── main.tf
│   └── backend.tf        ← points to dev S3 bucket
├── staging/
│   ├── main.tf
│   └── backend.tf        ← points to staging S3 bucket
└── prod/
    ├── main.tf
    └── backend.tf        ← points to prod S3 bucket
```
Each environment has its **own state file in its own backend**, completely isolated.

**Option B — Terragrunt (wrapper tool)**
Terragrunt can DRY up the above pattern so you're not copy-pasting `main.tf` across directories, while still keeping backends fully separate.

---

### Access Control — How Teams Actually Restrict This

Since workspaces have no native RBAC, access control happens at **layers outside of Terraform itself**:

**1. Cloud IAM (Most Common)**
```
dev  IAM role  → read/write dev state bucket only
prod IAM role  → read/write prod state bucket only
```
Developers assume the dev role, only CI/CD (e.g. GitHub Actions) can assume the prod role. Humans physically cannot touch prod state.

**2. Terraform Cloud / HCP Terraform**
The managed platform adds proper workspace-level RBAC:
- Assign teams `read`, `plan`, or `apply` permissions per workspace
- Prod workspace → only senior engineers + CI can apply
- Dev workspace → everyone can apply

**3. CI/CD as the Gatekeeper**
```
developer pushes code
      │
      ▼
PR opened → terraform plan runs (read only)
      │
      ▼
PR merged to main → terraform apply runs (dev/staging only)
      │
      ▼
Release tagged → terraform apply runs (prod, requires approval)
```
Humans never run `terraform apply` against prod directly — the pipeline owns it.

---

### The Mental Model

```
Workspaces                    Separate Backends
─────────────────             ─────────────────────────────
Great for...                  Great for...

Personal sandboxes            Dev → Staging → Prod pipelines
Feature branch infra          Strong access boundaries
Throwaway testing             Audit/compliance requirements
Same code, diff state         Different configs per environment
```

The short version: **workspaces = same repo, same backend, different state. Environments = different backends, different access controls, different everything.**

---
# Workspace Setup for Teams
## Setting Up Separate Backends

### The Folder Structure

```
infra/
├── modules/                    ← shared reusable modules
│   ├── networking/
│   ├── compute/
│   └── database/
├── envs/
│   ├── dev-sandboxes/          ← personal workspaces live here
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── backend.tf
│   │   └── backend-configs/
│   │       ├── backend-alice.hcl
│   │       ├── backend-bob.hcl
│   │       └── backend-charlie.hcl
│   ├── dev/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── backend.tf
│   ├── staging/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── backend.tf
│   └── prod/
│       ├── main.tf
│       ├── variables.tf
│       └── backend.tf
└── backends/
    ├── dev-sandboxes.hcl
    ├── dev.hcl
    ├── staging.hcl
    └── prod.hcl
```

---

### Step 1 — Create Your S3 Buckets (one per environment)

You want completely separate buckets so blast radius is contained:

```hcl
# This is typically a one-time bootstrap, done manually or via a separate "foundation" Terraform config

aws s3api create-bucket --bucket myapp-tfstate-dev-sandboxes --region us-east-1
aws s3api create-bucket --bucket myapp-tfstate-dev            --region us-east-1
aws s3api create-bucket --bucket myapp-tfstate-staging        --region us-east-1
aws s3api create-bucket --bucket myapp-tfstate-prod           --region us-east-1

# Enable versioning on all of them (critical for state recovery)
aws s3api put-bucket-versioning --bucket myapp-tfstate-prod \
  --versioning-configuration Status=Enabled
```

---

### Step 2 — Backend Config Files

These are the `.hcl` files that get passed to `terraform init`:

```hcl
# backends/dev-sandboxes.hcl
bucket         = "myapp-tfstate-dev-sandboxes"
key            = "sandbox/terraform.tfstate"
region         = "us-east-1"
dynamodb_table = "myapp-tfstate-dev-sandboxes-lock"
encrypt        = true
```

```hcl
# backends/dev.hcl
bucket         = "myapp-tfstate-dev"
key            = "dev/terraform.tfstate"
region         = "us-east-1"
dynamodb_table = "myapp-tfstate-dev-lock"
encrypt        = true
```

```hcl
# backends/staging.hcl
bucket         = "myapp-tfstate-staging"
key            = "staging/terraform.tfstate"
region         = "us-east-1"
dynamodb_table = "myapp-tfstate-staging-lock"
encrypt        = true
```

```hcl
# backends/prod.hcl
bucket         = "myapp-tfstate-prod"
key            = "prod/terraform.tfstate"
region         = "us-east-1"
dynamodb_table = "myapp-tfstate-prod-lock"
encrypt        = true
```

---

### Step 3 — Backend Declaration in Each Environment

Each environment's `backend.tf` declares the **type** only — the actual values come in at init time:

```hcl
# envs/dev/backend.tf  (same pattern for staging and prod)
terraform {
  backend "s3" {}   # intentionally empty — values injected via -backend-config
}
```

---

### Step 4 — Environment-Specific Variables

Each environment has its own `terraform.tfvars` so configs differ where needed:

```hcl
# envs/dev/terraform.tfvars
environment    = "dev"
instance_type  = "t3.micro"
min_capacity   = 1
max_capacity   = 2
```

```hcl
# envs/prod/terraform.tfvars
environment    = "prod"
instance_type  = "m5.large"
min_capacity   = 3
max_capacity   = 10
```

---

### Step 5 — IAM Roles Per Environment (Access Control)

This is what physically prevents developers from touching staging/prod:

```hcl
# One role per environment, each scoped to its own bucket only

resource "aws_iam_policy" "dev_sandbox_state" {
  name = "terraform-state-dev-sandboxes"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["s3:GetObject", "s3:PutObject", "s3:DeleteObject", "s3:ListBucket"]
        Resource = [
          "arn:aws:s3:::myapp-tfstate-dev-sandboxes",
          "arn:aws:s3:::myapp-tfstate-dev-sandboxes/*"
        ]
      }
    ]
  })
}

# Prod policy — only CI/CD role gets this attached, never developers
resource "aws_iam_policy" "prod_state" {
  name = "terraform-state-prod"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["s3:GetObject", "s3:PutObject", "s3:DeleteObject", "s3:ListBucket"]
        Resource = [
          "arn:aws:s3:::myapp-tfstate-prod",
          "arn:aws:s3:::myapp-tfstate-prod/*"
        ]
      }
    ]
  })
}
```

---

### Step 6 — Personal Sandbox Workspaces

For dev sandboxes, workspaces make sense here since they share the same backend and the same dev-level permissions:

```bash
# Each developer does this once in envs/dev-sandboxes/
cd envs/dev-sandboxes

terraform init -backend-config=../../backends/dev-sandboxes.hcl

terraform workspace new dev-alice
# or
terraform workspace new dev-bob
```

Their state ends up namespaced automatically:
```
myapp-tfstate-dev-sandboxes/
└── env:/
    ├── dev-alice/terraform.tfstate
    ├── dev-bob/terraform.tfstate
    └── dev-charlie/terraform.tfstate
```

---

### Step 7 — Initializing Each Named Environment

```bash
# Dev
cd envs/dev
terraform init -backend-config=../../backends/dev.hcl
terraform apply -var-file=terraform.tfvars

# Staging
cd envs/staging
terraform init -backend-config=../../backends/staging.hcl
terraform apply -var-file=terraform.tfvars

# Prod — only runs in CI/CD, never locally
cd envs/prod
terraform init -backend-config=../../backends/prod.hcl
terraform apply -var-file=terraform.tfvars
```

---

### The Full Picture

```
Developer laptop                CI/CD Pipeline
─────────────────               ──────────────────────────────
Can assume:                     Can assume:
  dev-sandbox IAM role            dev IAM role    (on PR merge)
  dev IAM role                    staging IAM role (on PR merge)
                                  prod IAM role   (on release tag)

Cannot assume:
  staging IAM role  ← enforced by AWS, not by Terraform
  prod IAM role     ← enforced by AWS, not by Terraform
```

The key insight is that **Terraform itself doesn't enforce access** — AWS IAM does. Terraform just consumes whatever credentials it's given, so controlling which credentials can reach which bucket is what actually protects your environments.
