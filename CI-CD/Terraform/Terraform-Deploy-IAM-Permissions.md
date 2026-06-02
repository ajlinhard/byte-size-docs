## ELI5: The PassRole Warning 🧸

### Simple Analogy

Imagine your office building has a **master keycard system**. You're a contractor and the building manager gives you:

> *"You can give YOUR keycard access level to ANY door in the building, for ANY reason, to ANY person."*

That's really dangerous! You could give someone access to the vault, the server room, the CEO's office — anything. The warning is saying: **"You shouldn't be able to hand out keys so freely."**

---

### What is `iam:PassRole`?

In AWS, **PassRole** is how you "hand a permission badge" to an AWS service. For example:

```
"Hey Lambda, here's an IAM Role — use it to access S3 and RDS"
```

Without PassRole, you can't assign roles to services. It's an important and powerful action.

---

### Why is this dangerous in your policy?

Look at this statement in your policy:

```json
{
  "Sid": "IAMFullAccess",
  "Effect": "Allow",
  "Action": ["iam:*"],   // ⬅ wildcard action (includes PassRole!)
  "Resource": "*"        // ⬅ wildcard resource (every role!)
}
```

`iam:*` includes `iam:PassRole`, and `Resource: *` means **every IAM role in your account**. So this principal can:

```
Pass ANY role → to ANY service → for ANY purpose
```

### The Privilege Escalation Risk 🚨

Here's the scary part — this is how an attacker (or accidental misuse) escalates privileges:

```
You only have Terraform access
        │
        ▼
But you can PassRole any role to Lambda...
        │
        ▼
You create a Lambda and attach the AdminRole to it
        │
        ▼
You invoke the Lambda → it now runs as Admin
        │
        ▼
🎉 You just gave yourself Admin access!
```

---

### How to Fix It

AWS recommends two approaches:

**Option 1 — Restrict to specific roles (ARNs):**
```json
{
  "Sid": "RestrictedPassRole",
  "Effect": "Allow",
  "Action": "iam:PassRole",
  "Resource": "arn:aws:iam::619071338293:role/terraform-*"
  // Only pass roles that start with "terraform-"
}
```

**Option 2 — Restrict to specific services (condition key):**
```json
{
  "Sid": "RestrictedPassRole",
  "Effect": "Allow",
  "Action": "iam:PassRole",
  "Resource": "*",
  "Condition": {
    "StringEquals": {
      "iam:PassedToService": [
        "ecs-tasks.amazonaws.com",
        "lambda.amazonaws.com"
      ]
    }
  }
  // Can only pass roles TO these specific services
}
```

---

### Your Bigger Issue ⚠️

Honestly, the PassRole warning is just the **tip of the iceberg** in this policy. You have full `*` access on:

| Service | Risk Level |
|---|---|
| `iam:*` | 🔴 Critical — can create/modify any role or user |
| `s3:*` on `*` | 🔴 Critical — can read/delete any bucket |
| `ec2:*` | 🟠 High — can spin up/destroy infrastructure |
| `rds:*` | 🟠 High — can delete databases |
| `lambda:*` | 🟠 High — can create/run arbitrary code |

This policy essentially gives **near-Admin access**. It's fine for a dev sandbox, but should never be used in production. The PassRole warning is AWS's way of waving a red flag at the most dangerous part.
---
# Additional IAM Permissions for Terraform

Beyond `iam:*`, there are some **related services and permissions** that Terraform commonly needs when managing IAM and the services that depend on it.

---

### 1. AWS Organizations (if using SCPs or multi-account)
```json
{
  "Sid": "OrganizationsReadAccess",
  "Effect": "Allow",
  "Action": [
    "organizations:DescribeOrganization",
    "organizations:ListAccounts",
    "organizations:ListPolicies",
    "organizations:DescribePolicy"
  ],
  "Resource": "*"
}
```
Needed if Terraform manages **Service Control Policies (SCPs)** or reads org structure.

---

### 2. IAM Access Analyzer
```json
{
  "Sid": "AccessAnalyzer",
  "Effect": "Allow",
  "Action": [
    "access-analyzer:*"
  ],
  "Resource": "*"
}
```
Useful if Terraform creates **Access Analyzers** to validate policies before applying them — catches issues like the PassRole warning automatically.

---

### 3. AWS SSO / Identity Center (common with Terraform IAM work)
```json
{
  "Sid": "SSOAccess",
  "Effect": "Allow",
  "Action": [
    "sso:*",
    "sso-admin:*",
    "identitystore:*"
  ],
  "Resource": "*"
}
```
Needed if you manage **permission sets, account assignments, or SSO groups** via Terraform.

---

### 4. Service-Linked Roles
```json
{
  "Sid": "ServiceLinkedRoles",
  "Effect": "Allow",
  "Action": [
    "iam:CreateServiceLinkedRole",
    "iam:DeleteServiceLinkedRole",
    "iam:GetServiceLinkedRoleDeletionStatus"
  ],
  "Resource": "arn:aws:iam::*:role/aws-service-role/*"
}
```
Many AWS services (ECS, RDS, ElasticSearch, etc.) need **service-linked roles** auto-created the first time Terraform provisions them. Without this, those `terraform apply` runs can fail.

---

### 5. Secrets Manager (often paired with IAM)
```json
{
  "Sid": "SecretsManagerAccess",
  "Effect": "Allow",
  "Action": [
    "secretsmanager:*"
  ],
  "Resource": "*"
}
```
Terraform frequently creates IAM roles alongside secrets — e.g., a role that grants a Lambda access to a specific secret.

---

### 6. STS (Security Token Service)
```json
{
  "Sid": "STSAccess",
  "Effect": "Allow",
  "Action": [
    "sts:AssumeRole",
    "sts:GetCallerIdentity",
    "sts:DecodeAuthorizationMessage"
  ],
  "Resource": "*"
}
```
Needed for:
- **`GetCallerIdentity`** — Terraform uses this constantly to confirm which account/role it's running as
- **`AssumeRole`** — Required for cross-account Terraform deployments
- **`DecodeAuthorizationMessage`** — Helps debug cryptic "access denied" errors

---

### Quick Reference: What You Likely Need

| Permission | When You Need It |
|---|---|
| `sts:GetCallerIdentity` | **Always** — Terraform calls this on every run |
| `iam:CreateServiceLinkedRole` | **Always** — ECS, RDS, Lambda all need it |
| `sts:AssumeRole` | Multi-account setups |
| `secretsmanager:*` | If storing credentials/secrets via Terraform |
| `access-analyzer:*` | Recommended for policy validation |
| `sso-admin:*` | If managing AWS SSO/Identity Center |
| `organizations:*` (read) | Multi-account org management |

---

### Most Critical Addition ⭐

If you take nothing else, add this — Terraform will silently fail on many resource creations without it:

```json
{
  "Sid": "STSCallerIdentityAndServiceLinkedRoles",
  "Effect": "Allow",
  "Action": [
    "sts:GetCallerIdentity",
    "iam:CreateServiceLinkedRole",
    "iam:DeleteServiceLinkedRole",
    "iam:GetServiceLinkedRoleDeletionStatus"
  ],
  "Resource": "*"
}
```
