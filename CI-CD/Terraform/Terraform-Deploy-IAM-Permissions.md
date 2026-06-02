# Additional IAM Permissions for Terraform

Yes! Beyond `iam:*`, there are some **related services and permissions** that Terraform commonly needs when managing IAM and the services that depend on it.

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
