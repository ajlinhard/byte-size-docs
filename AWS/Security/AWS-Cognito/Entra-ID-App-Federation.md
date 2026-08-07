
# App-level federation: JS webapp users → temporary AWS credentials

Users authenticate to Entra ID from the browser via MSAL.js (Authorization Code + PKCE), get an ID token, exchange it for short-lived AWS credentials tied to a narrow IAM role, and use those with AWS SDK v3.

**Two ways to do the exchange:**
- **Cognito Identity Pools** — AWS-managed; takes claims from your SAML/OAuth/OIDC provider and turns them into an AssumeRoleWithWebIdentity call on your behalf, handing back short-term credentials.
- **Direct STS federation** — fewer moving parts, no Cognito resource, but you own the plumbing.

---
## 1. **Register the SPA in Entra ID.**
App registrations → New registration → Platform = Single-page application, with redirect URIs per environment. Leave client secret alone — SPAs are public clients, and a secret embedded in browser JS is a leaked credential. Add `openid`, `profile`, `email` scopes.



---
## 2. **Wire up MSAL.js** (`npm install @azure/msal-browser`):
```js
import { PublicClientApplication } from "@azure/msal-browser";
const msalInstance = new PublicClientApplication({
  auth: {
    clientId: "<entra-app-client-id>",
    authority: "https://login.microsoftonline.com/<tenant-id>",
    redirectUri: "https://yourapp.example.com",
  },
  cache: { cacheLocation: "sessionStorage" }, // safer than localStorage against XSS token theft
});
```
   Log in with `loginPopup`/`loginRedirect`, read the ID token, and call `acquireTokenSilent` before each AWS credential exchange since Entra tokens are short-lived (~1 hr).
   *Common mistake:* configuring the legacy implicit flow instead of MSAL's default Authorization Code + PKCE — implicit tokens are more exposed.

---
## 3. **Register Entra ID as an OIDC provider in AWS IAM.** 
IAM → Identity providers → Add provider → OpenID Connect, provider URL `https://login.microsoftonline.com/<tenant-id>/v2.0`, audience = your Entra client ID.

---
## 4. **Cognito route:** 
Create an Identity Pool, add the OIDC provider ARN under authentication providers, let it generate (or attach) an authenticated IAM role.

   **Direct STS route:** trust policy on your IAM role:
```json
{
  "Effect": "Allow",
  "Principal": { "Federated": "arn:aws:iam::<acct>:oidc-provider/login.microsoftonline.com/<tenant-id>/v2.0" },
  "Action": "sts:AssumeRoleWithWebIdentity",
  "Condition": { "StringEquals": {
    "login.microsoftonline.com/<tenant-id>/v2.0:aud": "<entra-app-client-id>"
  }}
}
```
```js
import { fromWebToken } from "@aws-sdk/credential-providers";
const credentials = fromWebToken({
  roleArn: "arn:aws:iam::<acct>:role/<role-name>",
  webIdentityToken: idTokenFromMsal,
  roleSessionName: "webapp-session",
});
```
   *Common mistake:* leaving the `aud` condition off entirely — any app in that Entra tenant could then assume the role, not just yours.

---
## 5. **Scope the role tightly.** 
These permissions are effectively public to every logged-in app user — least-privilege it (specific S3 prefixes, specific tables), never a broad managed policy.


---
## 6. **Use the credentials** with AWS SDK v3 clients (`S3Client`, `DynamoDBClient`, etc.), and re-derive them before the ~1 hour expiry rather than reusing stale ones.

---
## 7. **For per-user permission differences**, map Entra group/role claims to Cognito role-mapping rules or separate roles — don't default everyone into one broad "authenticated" role for convenience.

**Risks specific to browser-side federation:**
- **XSS = credential theft.** Anything that runs JS in your origin can read the token/credentials in memory. Strict CSP and dependency hygiene matter a lot more once AWS creds live in the tab.
- **No server-side authorization check.** A valid Entra token is the *only* gate — no app-specific business logic (subscription tier, account status). For anything beyond low-risk reads, put a thin backend in between: it validates the token against Entra's JWKS, applies your own rules, then either proxies the AWS call or mints a narrower session.
- **sessionStorage vs localStorage** for the MSAL cache — localStorage persists across tabs/reboots but widens XSS blast radius; sessionStorage is the safer default.

---

**Cross-cutting risk:** once either integration exists, an Entra ID tenant compromise becomes an AWS compromise. Require phishing-resistant MFA/Conditional Access on any account able to edit these app registrations, and don't let permission sets or IAM roles drift toward "just give admin, fix it later" — that's the most common finding in audits of these setups after the fact.

I can save this as a markdown or Word reference doc if you want a copy to keep, and happy to go deeper on either the SAML/SCIM config or the JS credential-exchange code.Let me know if you'd like me to go deeper on either piece — e.g., the exact Entra token-configuration claims for group-based role mapping, a working Cognito Identity Pool + MSAL.js sample, or the SCIM attribute-mapping details for provisioning custom user attributes.
