## IAM Role Trusted Entity Types for Terraform

These are the **5 trust entity options** you see in the AWS Console when creating a role. Here's what each means for Terraform:

---

### 🏆 Best Choice for Terraform via SSO
**→ AWS Account**

---

### Breakdown of Each Option

| Trust Type | Use for Terraform? | When to Use |
|---|---|---|
| **AWS Service** | ❌ No | For AWS services (EC2, Lambda, ECS) to assume the role — not for human/pipeline Terraform runs |
| **AWS Account** | ✅ **Yes (SSO)** | Allows IAM users/roles from an AWS account to assume it — this is what SSO permission sets use under the hood |
| **Web Identity** | ✅ Yes (CI/CD) | For GitHub Actions, GitLab CI, BitBucket — OIDC-based, no static credentials |
| **SAML 2.0** | ⚠️ Rarely | For enterprise identity providers (Okta, AD FS) federating directly — SSO handles this better now |
| **Custom Trust Policy** | ✅ Advanced | Write the JSON trust policy manually — use for cross-account, complex conditions, or combining multiple principals |

---

### For Your SSO Use Case → **AWS Account**

When you set up IAM Identity Center, it automatically creates roles in your account that look like:
```
arn:aws:iam::123456789012:role/AWSReservedSSO_TerraformDeployRole_xxxx
```

The trust policy it generates is an **AWS Account** type pointing back to the IAM Identity Center service. You don't create this manually — IAM Identity Center manages it.

**If you're creating the role manually** to be assumed via SSO, pick **AWS Account** and specify:

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {
      "AWS": "arn:aws:iam::123456789012:root"
    },
    "Action": "sts:AssumeRole"
  }]
}
```

---

### Quick Decision Guide

```
Are you running Terraform locally with aws sso login?
  → AWS Account

Are you running Terraform in GitHub/GitLab CI?
  → Web Identity (OIDC)

Is Terraform running on an EC2/ECS/Lambda?
  → AWS Service

Using Okta or Active Directory directly?
  → SAML 2.0

Need cross-account or multiple principals?
  → Custom Trust Policy
```

---

Since you're using SSO, **AWS Account** is your answer. Want help setting up the exact trust + permission policy for your account?
