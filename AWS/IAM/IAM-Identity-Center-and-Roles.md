# IAM Identity Center and Roles
Q: What is the difference between IAM Role and the IAM Identity Center Users/Groups with permissions sets?
This confuses a lot of people because they *overlap* but serve different layers. Here's how to think about it:

---

## The Core Distinction

| | IAM Roles | IAM Identity Center (Permission Sets) |
|---|---|---|
| **Lives in** | A specific AWS account | Centrally, across your whole AWS Organization |
| **Assumed by** | AWS services, apps, or federated users | Human users (workforce identity) |
| **Identity source** | No identity — it's just a set of permissions | Your IdP (Okta, Azure AD, etc.) or built-in user store |
| **Credential type** | Temporary STS tokens | Temporary STS tokens (also) |
| **Scope** | Single account | Can span multiple accounts |
| **Managed where** | IAM console, per account | IAM Identity Center console, org-wide |

---

## What Each One Actually Is

### IAM Role
A **permission container** inside a specific AWS account. It has:
- A **trust policy** — *who or what* is allowed to assume it (another AWS service, account, or federated identity)
- A **permissions policy** — *what actions* the role can take in that account

It has **no concept of a person's identity**. It doesn't know if it's "Alice" or "Bob" — it just knows something was allowed to assume it.

**Common uses:**
- EC2 instance needs to write to S3 → assign an instance role
- Lambda needs to read from DynamoDB → assign an execution role
- GitHub Actions needs to deploy → OIDC federation to a role
- One AWS account needs to access another → cross-account role assumption

---

### IAM Identity Center (Users/Groups + Permission Sets)
A **human identity management layer** that sits *above* IAM roles. It:
- Manages **who your people are** (synced from Okta/Azure AD or stored natively)
- Defines **Permission Sets** — which are just *templates* that get deployed as IAM roles into each account
- Controls **which people/groups get which permission set in which account**

> **Key insight:** When you assign a Permission Set to an account, IAM Identity Center **automatically creates an IAM Role in that account** behind the scenes. The Permission Set *is* an IAM Role — you're just managing it centrally.

---

## How They Relate — The Flow

```
[Alice in Okta] 
    → synced to IAM Identity Center 
    → assigned "DeveloperAccess" Permission Set in Dev account
    → Identity Center auto-creates an IAM Role in Dev account
    → Alice logs in via SSO portal
    → Assumes that auto-created IAM Role
    → Gets temporary credentials scoped to that role
```

So IAM Identity Center is essentially a **control plane** that manages IAM Roles across accounts for human users — so you don't have to manually create and manage those roles in every account yourself.

---

## Side-by-Side Scenario

**Without Identity Center (manual IAM Roles):**
- Create an IAM Role in Dev account
- Create an IAM Role in Staging account
- Create an IAM Role in Prod account
- Manage trust policies in each
- Somehow attach a human identity to each (messy)
- Repeat for every new hire

**With Identity Center:**
- Define one `DeveloperAccess` Permission Set once
- Assign it to Alice's group in Dev + Staging accounts
- Done — roles are auto-provisioned, Alice SSOs in and assumes them

---

## When to Use Which

| Scenario | Use |
|---|---|
| EC2/Lambda/ECS needs AWS permissions | **IAM Role** (service role) |
| Cross-account access between AWS services | **IAM Role** (cross-account trust) |
| CI/CD pipeline (GitHub Actions, etc.) | **IAM Role** (OIDC federation) |
| Human developers/admins logging in | **IAM Identity Center** + Permission Sets |
| Managing access across 5+ accounts for a team | **IAM Identity Center** — essential |

---

## TL;DR

- **IAM Role** = a permission set inside one account, assumed by *anything* (services, apps, pipelines, humans)
- **IAM Identity Center** = the human identity layer that centrally manages who your people are, and *automatically creates and manages IAM Roles* in your accounts on their behalf

Think of Identity Center as the **management console for human access**, and IAM Roles as the **actual enforcement mechanism** underneath it.
