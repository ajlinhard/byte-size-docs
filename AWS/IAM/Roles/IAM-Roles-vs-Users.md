# IAM Roles vs. Users
Q: When setting up an AWS Account for a team is it better to setup role for certain types of users to assume or individual accounts?
Great question — this is a foundational decision in AWS account governance. The short answer is: **use IAM roles** (not individual IAM users) in almost every scenario. Here's why, and how to think about it:

## Roles vs. Individual IAM Users

### Why Roles Win

**Security**
- Roles use **temporary credentials** (short-lived tokens via STS), so there are no long-lived access keys to rotate, leak, or forget about.
- IAM users with static access keys are a major source of credential exposure incidents.

**Scalability**
- Adding/removing team members doesn't require creating/deleting IAM users in each account. You manage identity in one place (your IdP or AWS IAM Identity Center) and map to roles.

**Auditability**
- CloudTrail logs show *who assumed which role*, giving you clean attribution without managing per-user policies across accounts.

**Least Privilege by Job Function**
- You define roles like `Developer`, `ReadOnly`, `DataEngineer`, `SecurityAuditor` — and people assume the role appropriate to their task, not a permanent permission set.

---

## The Recommended Modern Setup

**AWS IAM Identity Center (formerly SSO)** + **Roles** is the gold standard for teams:

1. **Connect your Identity Provider** (Okta, Azure AD, Google Workspace, etc.) to IAM Identity Center.
2. **Define Permission Sets** (these become roles behind the scenes) — e.g., `AdminAccess`, `DeveloperAccess`, `ReadOnlyAccess`.
3. **Assign groups from your IdP** to permission sets per account.
4. Team members log in via SSO and **assume the appropriate role** — no static keys, no per-user IAM config.

---

## Multi-Account vs. Single Account

For teams, a **multi-account strategy** with AWS Organizations is best practice:

| Account | Purpose |
|---|---|
| Management/Root | Billing, org-level policies only |
| Dev | Developer sandboxes |
| Staging | Pre-production testing |
| Production | Live workloads |
| Security/Logging | Centralized CloudTrail, GuardDuty |

Roles are then defined per account, and IAM Identity Center manages who can assume which role in which account — all from one control plane.

---

## When Individual IAM Users Are Still Valid

- **Break-glass / emergency accounts** — a tightly locked IAM user with MFA for when SSO is unavailable.
- **Service accounts / CI-CD pipelines** — though even here, prefer IAM roles for EC2/Lambda, or OIDC federation for GitHub Actions.
- **Very small solo setups** where SSO overhead isn't worth it.

---

## TL;DR

| | IAM Roles | IAM Users |
|---|---|---|
| Credentials | Temporary ✅ | Static (long-lived) ❌ |
| Scalability | High ✅ | Low ❌ |
| Best for humans | ✅ (via Identity Center) | ❌ |
| Best for services | ✅ (instance/task roles) | Sometimes |

Roles + IAM Identity Center is the path AWS recommends and what security-conscious teams use. Individual IAM users should be the exception, not the rule.
