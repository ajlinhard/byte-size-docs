# AWS SSO User or Group Setup
Here's a step-by-step guide to assigning a permission set to a user in IAM Identity Center:

During Steps 2 and 3 a IAM policy and IAM User /Group will need to be made. Info in links below.
---

## Step 1: Open IAM Identity Center
1. Log into the **AWS Console** with an admin account
2. Search for **"IAM Identity Center"** in the top search bar
3. Make sure you're in the **correct region** where your Identity Center is configured

---

## Step 2: (If Needed) Create a Permission Set
If a permission set doesn't exist yet:

1. In the left sidebar, click **"Permission sets"**
2. Click **"Create permission set"**
3. Choose a type:
   - **Predefined** — use an AWS managed policy (e.g., `AdministratorAccess`, `ReadOnlyAccess`, `PowerUserAccess`)
   - **Custom** — define your own inline/managed policies
   - [Example: Terraform Policy](https://github.com/ajlinhard/byte-size-docs/blob/main/CI-CD/Terraform/Terraform-IAM-Policy-Example.json)
   - [Permission Warnings!](https://github.com/ajlinhard/byte-size-docs/blob/main/CI-CD/Terraform/Terraform-Deploy-IAM-Permissions.md)
4. Give it a name (e.g., `TerraformDeployer`)
5. Set a **session duration** (how long credentials last, e.g., 8 hours)
6. Click through and **Create**

---

## Step 3: Assign the User to an AWS Account
This is the critical step that grants access:

1. In the left sidebar, click **"AWS accounts"**
2. You'll see a list of accounts in your AWS Organization — **check the box** next to the account(s) you want the user to access
3. Click **"Assign users or groups"**
4. On the **Users** tab, search for and select your user
5. Click **Next**
6. Select the **permission set** you want to assign (e.g., `TerraformDeployer`)
7. Click **Next** → **Submit**
8. Go back to your AWS Account in IAM Identity Center to confirm group or user is attached.
9. If NO, click add user/group then add the account you just made.
10. If YES, create a group by completing these sub-steps:
   a. create group with the use-case name exaple: terraform-deployer
   b. Attached the Identity Center user(s)
   c. Click "Create Group" button
   d. Go to the new Group "terraform-deployer" the assign an AWS Account under: IAM Identity Center => AWS Organizations: AWS accounts => <your account name> => Assign users and groups
   e Make sure to be under "Groups" not "Users" then select your new group and the permission set from "Step 2"
12. The make sure the permission set is associated with the user within the account
<img width="2848" height="1564" alt="image" src="https://github.com/user-attachments/assets/59bfa429-9252-4bf4-8726-5b64676e35d2" />


---

## Step 4: Re-run AWS SSO Configure
Back on the machine, run the SSO login again:
```powershell
aws configure sso
```
Or if already configured, just login:
```powershell
aws sso login --profile <your-profile-name>
```

You should now see the account listed and can complete the profile setup.

---

## Quick Checklist
| Step | What to verify |
|------|---------------|
| Permission set exists | IAM Identity Center → Permission sets |
| User exists | IAM Identity Center → Users |
| Assignment exists | IAM Identity Center → AWS accounts → select account → Assigned users |
| Correct region | Identity Center region matches `aws configure sso` region |

> **Tip:** If you're using an external IdP (Okta, Azure AD), you may need to assign access via a **Group** rather than directly to the user — ask your IdP admin to add the user to the appropriate group.

---
# You Don't Always Need a Separate IAM Role (When Do I?)

If you attach the policy **directly to the Permission Set** in IAM Identity Center, it works fine for Terraform. The separate IAM role step is optional. Here's the distinction:

---

### How It Works Without a Separate Role

When a user logs in via SSO, IAM Identity Center **automatically creates a temporary role** behind the scenes tied to the Permission Set. So you're still using a role — AWS just manages it for you.

```
You (SSO login) → Permission Set (with TerraformExecutionPolicy attached)
                        ↓
         AWS auto-generates a temporary session role
                        ↓
              Terraform uses those credentials
```

Your Terraform provider config stays the same:

```hcl
provider "aws" {
  region  = "us-east-1"
  profile = "terraform-dev"   # the SSO profile you configured
}
```

**This is completely valid and works.**

---

### So When Would You Create a Separate IAM Role?

The manual role setup is useful in specific situations:

| Scenario | Separate Role Needed? |
|---|---|
| Human dev running Terraform locally via SSO | ❌ No — Permission Set policy is enough |
| CI/CD pipeline (GitHub Actions, Jenkins, etc.) | ✅ Yes — needs a role to assume |
| Terraform managing **multiple AWS accounts** | ✅ Yes — needs cross-account role assumption |
| You want stricter separation / auditing per tool | ✅ Yes — gives more control |
| Team sharing one SSO group for Terraform | ❌ No — Permission Set handles it |

---

### The Simpler Setup (No Manual Role)

If you're a developer running Terraform locally, just do this:

1. **Create a Permission Set** in IAM Identity Center
2. **Attach your Terraform policy** directly to the Permission Set
3. **Assign it** to your user or group for the target account
4. Run `aws configure sso` → `aws sso login` → done

No manual IAM role creation needed. The SSO-managed temporary role handles everything transparently.

---

### The Key Tradeoff

- **Permission Set only** → simpler, great for individuals/small teams running Terraform locally
- **Separate IAM Role** → more flexibility, required for automation, cross-account setups, or when non-SSO identities (like CI bots) need the same access
