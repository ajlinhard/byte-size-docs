## AWS User/Group IAM Role Permissions:
**Question: How do I setup a AWS sso user + permission set, which can assume an IAM role when logging in through SSO?**

When you use IAM Identity Center (the current name for AWS SSO), **logging in already means assuming a role**. A permission set gets provisioned into each assigned account as an IAM role named `AWSReservedSSO_<PermissionSetName>_<hash>`. So if all you need is "user logs in and gets these permissions in account X," you don't need a separate IAM role at all.

The extra work only appears if you want the SSO session to then *assume a different, pre-existing IAM role* (role chaining) — e.g. a role you already share with CI, or a cross-account role.

## Part 1 — Basic setup (user → permission set → account)

1. **Enable IAM Identity Center** in your management account, in the region you want as the identity region.
2. **Create the user**: Identity Center → Users → Add user. Or connect an external IdP (Okta/Entra/Google) via SAML + SCIM instead.
3. **Create a group** (e.g. `Developers`) and put the user in it. Always assign via groups, not individual users — it saves pain later.
4. **Create a permission set**: Identity Center → Permission sets → Create. You can attach AWS managed policies, customer managed policies (must exist in each target account by that name), and/or an inline policy. Set the session duration here too (default 1 hour, up to 12).
5. **Assign**: Identity Center → AWS accounts → select account(s) → Assign users or groups → pick the group → pick the permission set. This provisions the `AWSReservedSSO_*` role into each selected account.
6. **Log in**: user goes to the access portal URL (`https://d-xxxxxxxxxx.awsapps.com/start`), or CLI:

```bash
aws configure sso
# SSO start URL, SSO region, then pick account + role
aws sso login --profile myprofile
```

## Part 2 — Making that SSO session assume another IAM role

Two halves must line up:

**A. Permission set must allow the call.** Add an inline policy to the permission set:

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": "sts:AssumeRole",
    "Resource": "arn:aws:iam::222222222222:role/MyTargetRole"
  }]
}
```

**B. Target role must trust the SSO role.** This is the part that trips people up: the SSO role name has a random suffix and lives under the path `/aws-reserved/sso.amazonaws.com/`. Trust policies **cannot wildcard the principal ARN**, so you have two options:

*Option 1 — trust the exact role ARN* (look it up after provisioning; note the path is omitted in the ARN when used as a principal):

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": { "AWS": "arn:aws:iam::111111111111:role/aws-reserved/sso.amazonaws.com/AWSReservedSSO_Developers_abc123def456" },
    "Action": "sts:AssumeRole"
  }]
}
```

*Option 2 — trust the account root, then filter with a condition* (survives permission-set re-provisioning, which can change the hash):

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": { "AWS": "arn:aws:iam::111111111111:root" },
    "Action": "sts:AssumeRole",
    "Condition": {
      "ArnLike": {
        "aws:PrincipalArn": "arn:aws:iam::111111111111:role/aws-reserved/sso.amazonaws.com/*/AWSReservedSSO_Developers_*"
      }
    }
  }]
}
```

Option 2 is generally what you want. Trusting root means "any principal in account 111111111111 that has been granted `sts:AssumeRole` on this role" — the condition narrows it to the SSO role family.

**C. Wire it up in the CLI** via a chained profile:

```ini
[profile sso-base]
sso_session = mysso
sso_account_id = 111111111111
sso_role_name = Developers
region = us-east-1

[sso-session mysso]
sso_start_url = https://d-xxxxxxxxxx.awsapps.com/start
sso_region = us-east-1
sso_registration_scopes = sso:account:access

[profile target]
role_arn = arn:aws:iam::222222222222:role/MyTargetRole
source_profile = sso-base
region = us-east-1
```

Then `aws sso login --profile sso-base` once, and use `--profile target` for the chained calls.

## Gotchas

- **Role chaining caps sessions at 1 hour**, regardless of the target role's `MaxSessionDuration`. Not configurable.
- If the target role's trust uses the exact ARN (Option 1), re-provisioning the permission set can rotate the hash and silently break it.
- Customer managed policies referenced in a permission set must already exist, with identical names, in *every* account you assign to — otherwise provisioning fails.
- Permission set changes require re-provisioning to reach already-assigned accounts; Identity Center usually prompts, but check the "Accounts" tab for a stale status.

If you tell me whether the target role is in the same account or a different one, I can tighten the trust policy example.
