## Setting Up Your `govcloud` AWS SSO Profile

You'll use the `aws configure sso` command to create this profile. Here's how:

---

### Step 1 — Open Your Terminal and Run

```
aws configure sso
```

It will ask you a series of questions. Here's what each one means and what to type:

---

### Step 2 — Answer the Prompts

```
SSO session name (Recommended): govcloud-session
```
This is just a nickname for the login session. Type anything descriptive — `govcloud-session` works fine.

---

```
SSO start URL [None]: https://your-company.awsapps.com/start
```
This is your **company's SSO login portal URL**. You won't know this off the top of your head — you need to **ask your IT/DevOps team** for it. It usually looks something like:
- `https://your-company.awsapps.com/start`
- `https://d-xxxxxxxxxx.awsapps.com/start`
**Find this in the AWS Idenity Center => Dashboard by looking for "AWS access portal URLs" on the dashboard page.**
---

```
SSO region [None]: us-gov-east-1
```
Since this is a **GovCloud** account, the region is likely `us-gov-east-1` or `us-gov-west-1`. Ask your team which one they use.

---

```
SSO registration scopes [sso:account:access]:
```
Just press **Enter** to accept the default.

---

### Step 3 — Browser Login Popup

At this point, AWS will open your browser and ask you to log in with your work credentials. Do that, then come back to the terminal.

---

### Step 4 — Select Your Account and Role

After logging in, the terminal will show a list of AWS accounts you have access to. It will look something like:

```
There are 2 AWS accounts available to you.
> ######## (GovCloud Prod)
  123456789012 (Sandbox)
```

Use the **arrow keys** to select `########` (the GovCloud account from your instructions) and press **Enter**.

Then it will ask which **role** to use:
```
Using the account ID -########]:
There are 2 roles available to you.
> ReadOnlyAccess
  PowerUserAccess
```
Select whichever role your team tells you to use.

---

### Step 5 — Name Your Profile

```
CLI profile name [ReadOnlyAccess-########]: govcloud
```
This is the important part — **type `govcloud` here** so it matches the name used in your project's instructions, then press **Enter**.

---

### Step 6 — Verify It Worked

Run this to confirm the profile exists:
```
aws configure list-profiles
```
You should see `govcloud` in the list. ✅

---

### You're Done!

Now go back to the original three commands from your instructions — they should work:
```
aws sso login --profile govcloud
export AWS_PROFILE=govcloud
bash scripts/some_base_script.sh
```

> 💡 **Key things to get from your IT/DevOps team before starting:**
> - The SSO start URL
> - The SSO region (`us-gov-east-1` or `us-gov-west-1`)
> - Which role to select

---
## Logging into Your AWS Account (First Timer's Guide)

These instructions use **AWS SSO (Single Sign-On)** — a way to log in through your browser instead of typing a password into the terminal. Here's what each step means and how to do it:

---
## Just the Login
### Step 1 — Log In via SSO

```
aws sso login --profile govcloud
```

**What this does:** This tells AWS CLI to log you in using a profile called `govcloud` (a pre-configured set of credentials for your organization's GovCloud account). When you run this:

1. Your **terminal will show a URL and a code**, like:
   ```
   Opening the SSO authorization page in your default browser...
   https://device.sso.us-gov-east-1.amazonaws.com/
   Then enter the code: ABCD-1234
   ```
2. Your browser may open automatically — if not, copy and paste that URL manually.
3. In the browser, **log in with your work credentials** (likely your company email/password or an identity provider like Okta/Azure AD).
4. Confirm the code shown matches what's in your terminal, then click **Allow**.
5. Go back to your terminal — it should say login was successful.

> ⚠️ If you get an error saying the `govcloud` profile doesn't exist, you'll need to ask your team for the SSO configuration or run `aws configure sso` to set it up first.

---

### Step 2 — Set Your Active Profile

```
export AWS_PROFILE=<profile-name>

echo %AWS_PROFILE%
```

**What this does:** This tells your terminal "for all AWS commands I run from now on, use the `govcloud` credentials." Think of it like selecting which account to use. This only lasts for your current terminal session — you'll need to run it again if you open a new terminal window.

---

### Step 3 — Run the Bootstrap Script

```
bash scripts/some_base_script.sh
```

---

### If Something Goes Wrong

| Error | Likely Cause |
|---|---|
| `profile not found` | The `govcloud` profile isn't set up on your machine yet |
| `Access Denied` | Your account hasn't been granted permission to the S3 buckets |
| `command not found: aws` | AWS CLI isn't installed |

For access issues, you'll need to contact whoever manages your team's AWS account `603664648583` and ask them to grant you read access to the `vis-project-nlp` and `vis-project-docs` buckets.
