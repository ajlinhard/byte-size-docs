## AWS User/Group IAM Role Permissions:
**Question: How do I setup a AWS sso user + permission set, which can assume an IAM role when logging in through SSO?**

When you use IAM Identity Center (the current name for AWS SSO), **logging in already means assuming a role**. A permission set gets provisioned into each assigned account as an IAM role named `AWSReservedSSO_<PermissionSetName>_<hash>`. So if all you need is "user logs in and gets these permissions in account X," you don't need a separate IAM role at all.

The extra work only appears if you want the SSO session to then *assume a different, pre-existing IAM role* (role chaining) — e.g. a role you already share with CI, or a cross-account role.

## High-Level Setup (user → permission set → account)

1. **Enable IAM Identity Center** in your management account, in the region you want as the identity region.
2. **Create the user**: Identity Center → Users → Add user. Or connect an external IdP (Okta/Entra/Google) via SAML + SCIM instead.
3. **Create a group** (e.g. `Developers`) and put the user in it. Always assign via groups, not individual users — it saves pain later.
4. **Create a permission set**: Identity Center → Permission sets → Create. You can attach AWS managed policies, customer managed policies (must exist in each target account by that name), and/or an inline policy. Set the session duration here too (default 1 hour, up to 12).
5. **Assign**: Identity Center → AWS accounts → select account(s) → Assign users or groups → pick the group → pick the permission set. This provisions the `AWSReservedSSO_*` role into each selected account.
6. **Log in**: user goes to the access portal URL (`https://d-xxxxxxxxxx.awsapps.com/start`), or CLI:
7. Setup Role based chained profles.

```bash
aws configure sso
# SSO start URL, SSO region, then pick account + role
aws sso login --profile myprofile
```
#### Identity Center
- Permissions Sets => This is what is used to anchor Groups and Users to individual AWS IAM Account policies.
- Users => these are the unique user (unique on email) who are registered in the Identity Center. These users can come from a federated 3rd party Adminstrator.
- Groups => these are groups of users in the Identity Center. These users can come from a federated 3rd party Adminstrator.
- Accounts => these are the accounts the IAM Identity Center has access to manage permissions for.

#### IAM
- Policy => the account level permission rules which can be assigned to different permission management entities: IAM roles, IAM users, Identity Center Permission Sets.
- Role => account level roles which are temporary credentials for a process to assume. (See AWS docs for a better definition)
- User => within the account users without the ability to have SSO access.

---
## Detailed Setup
---

1. Create an AWS Identity Center User (not an IAM User): AWS Identity Center => User => Add User
2. Attach the new User to the AWS Account: AWS Identity Center => AWS Accounts => <your acccount name> => Assign Users or Groups
3. Next create a group and attached the user to the group. Name the group based on the use case.
4. Repeat Step 2 , but with the new Group instead.
** IAM Policy Time
5. Got to AWS IAM and Create a managed policy for the Group:
    Options:
    A. Direct Policy where you attached the services and access rules directly to a policy and then Identity Center Permissons Set.
    B. Role Based Policies where you create an SSO group/user with no direct access, but can assume a set of roles which has access to the specific areas and services.


### Direct Policy
1. Create a custom managed policy with the select permission you want the group/user to have access to.
2. Research AWS pre-created managed policies for example: AWSBedrockFullAccess you may want to directly attach.
3. Go to the Identity Center under Permission Sets.
4. Click the "Create Permission Set" then select "Custom Permission Set"
5. Attach the managed policies from step 1 + 2
6. Finish the Review + Creation of the Permission Set.
7. Go  to AWS Identity Center => AWS Accounts => Change Permission Set
8. In here you will assign the Permission Set to the Group or User.
9. Test the permissions by trying an SSO Login to AWS
10. Once setup do a quick boto3 client/session check for the expected services in your policy.

### Role Base Policy Chain
1. Go to the Identity Center under Permission Sets.
2. Click the "Create Permission Set" then select "Custom Permission Set"
3. Attach the managed policies from step 1 + 2
4. Finish the Review + Creation of the Permission Set.
5. Go  to AWS Identity Center => AWS Accounts => Change Permission Set
6. In here you will assign the Permission Set to the Group or User.
**Role Creation Time**
7. Go to IAM Roles to create a new role.
8. Add as a trusted entity the Permission Set ARN (will be an IAM role named "AWSReservedSSO_%")
9. In a separate window 
    a. Create a custom managed policy with the select permission you want the group/user to have access to.
    b. Research AWS pre-created managed policies for example: AWSBedrockFullAccess you may want to directly attach.
10. Add the policies to the role
11. Repeat 7 - 10 for however many roles you want to create.
12. Create a final policy called "<your identity center group name>-assumable-roles-policy" including all role ARNs created.
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "Statement1",
            "Effect": "Allow",
            "Action": [
                "sts:AssumeRole"
            ],
            "Resource": [
                "arn:aws:iam::11111111111:role/terraform-deployer-role",
                "arn:aws:iam::11111111111:role/bedrock-ai-lead-role"
            ]
        }
    ]
}
```
13. Go back to the Identity Center to attach this new policy to you permission set.
** SSO Time (with a small trick) **
14. Complete your normal CLI SSO configure
15. Next access the .aws/config file and alter to allow for a chained role based login in.
**Example:**
```bash
# Linux
cat ~/.aws/config
# Windows
notepad .aws\config
```
16. Alter the file  to have the base "sso-session" for you Identity Center user, then add the "profiles" per role ARN you want to assume.
```text
[default]
region = us-east-1
output = json
[sso-session learn-terraform]
sso_start_url = https://d-xxxxxxxxxx.awsapps.com/start
sso_region = us-east-1
sso_registration_scopes = sso:account:access
[profile learn-terraform]
sso_session = learn-terraform
sso_account_id = 11111111111
sso_role_name = terraform-deployer-permission
region = us-east-1
output = json
[profile learn-bedrock]
role_arn = arn:aws:iam::xxxxxxxxxx:role/bedrock-ai-lead-role
source_profile = learn-terraform
region = us-east-1
output = json
```
17. The SSO login is still => ```aws sso login --profile <base sso-session>```
18. The python or other language code is what changes before creating the AWS client.
```python
import boto3
session = boto3.Session(profile_name="<your sso profile>")
client = session.client("bedrock-runtime", region_name="us-east-1")
```

----
## References — Making that SSO session assume another IAM role

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
