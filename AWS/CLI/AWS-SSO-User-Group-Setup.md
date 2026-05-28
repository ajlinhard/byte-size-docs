# AWS SSO User or Group Setup
Here's a step-by-step guide to assigning a permission set to a user in IAM Identity Center:

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
   - Example: Terraform Policy
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
10. The make sure the permission set is associated with the user within the account
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
