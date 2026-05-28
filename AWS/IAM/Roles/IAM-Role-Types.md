## AWS IAM Role – Trusted Entity Types

When you create an IAM Role in AWS, you must define a **Trusted Entity** — the entity allowed to assume that role. Here are the main types:

---

### 1. 🖥️ AWS Service
**Who it is:** An AWS service (like EC2, Lambda, ECS, etc.)

**Use cases:**
- Allow an **EC2 instance** to access S3 buckets (via Instance Profile)
- Allow a **Lambda function** to write logs to CloudWatch
- Allow **ECS tasks** to pull images from ECR or access Secrets Manager
- Allow **CodePipeline** to deploy to CloudFormation

**Example trust policy principal:**
```json
"Service": "ec2.amazonaws.com"
```

---

### 2. 👤 AWS Account (Another Account)
**Who it is:** An IAM user or role from a **different (or same) AWS account**

**Use cases:**
- **Cross-account access** — let a developer in Account A assume a role in Account B
- Centralized logging/security accounts accessing resources in member accounts
- Allowing a partner organization limited access to your AWS resources

**Example trust policy principal:**
```json
"AWS": "arn:aws:iam::123456789012:root"
```

---

### 3. 🌐 Web Identity (OIDC / Federated)
**Who it is:** Users authenticated via an **external identity provider** (IdP) using OpenID Connect (OIDC)

**Use cases:**
- **GitHub Actions** deploying to AWS without storing access keys
- **Kubernetes (EKS)** pods accessing AWS services via IRSA (IAM Roles for Service Accounts)
- Mobile/web apps using **Cognito, Google, Facebook, or Apple** login

**Example trust policy principal:**
```json
"Federated": "arn:aws:iam::123456789012:oidc-provider/token.actions.githubusercontent.com"
```

---

### 4. 🏢 SAML 2.0 Federation
**Who it is:** Users from a **corporate identity provider** (IdP) using SAML 2.0

**Use cases:**
- Enterprise **SSO** — employees log in with Active Directory (AD) / Okta / Azure AD credentials to access AWS Console
- Granting temporary AWS credentials to federated corporate users
- Avoiding managing individual IAM users for a large workforce

**Example trust policy principal:**
```json
"Federated": "arn:aws:iam::123456789012:saml-provider/MyCorpAD"
```

---

### 5. 🔑 IAM Identity Center (SSO) — Recommended for Organizations
**Who it is:** Users/groups managed in **AWS IAM Identity Center** (formerly AWS SSO)

**Use cases:**
- Centralized access management across **multiple AWS accounts** in an AWS Organization
- Assigning **permission sets** to teams or individuals
- Best practice for enterprise multi-account setups

---

## Quick Comparison Table

| Trusted Entity | Best For | Key Benefit |
|---|---|---|
| **AWS Service** | EC2, Lambda, ECS, etc. | No credentials needed in code |
| **AWS Account** | Cross-account access | Delegation between accounts |
| **Web Identity (OIDC)** | GitHub Actions, EKS, mobile | Keyless, short-lived tokens |
| **SAML 2.0** | Corporate SSO (AD/Okta) | Federated enterprise login |
| **IAM Identity Center** | Multi-account orgs | Centralized SSO management |

---

**General Rule of Thumb:** Always prefer **roles over long-lived access keys**, and use the most specific trusted entity type that fits your use case to follow the principle of least privilege.
