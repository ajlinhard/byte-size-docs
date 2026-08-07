
# App-level federation: JS webapp users → temporary AWS credentials

Users authenticate to Entra ID from the browser via MSAL.js (Authorization Code + PKCE), get an ID token, exchange it for short-lived AWS credentials tied to a narrow IAM role, and use those with AWS SDK v3.

**Two ways to do the exchange:**
- **Cognito Identity Pools** — AWS-managed; takes claims from your SAML/OAuth/OIDC provider and turns them into an AssumeRoleWithWebIdentity call on your behalf, handing back short-term credentials.
- **Direct STS federation** — fewer moving parts, no Cognito resource, but you own the plumbing.

---
## Some Important Background
Good questions — these are foundational terms for this whole topic.

### SPA (Single-Page Application)

A web app architecture where the browser loads one HTML page, and JavaScript handles all the rendering and navigation from there — think React, Vue, or Angular apps. Instead of the server sending a fresh HTML page for every click, the JS running in your browser fetches data (usually via API calls) and updates the page dynamically.

Why it matters for auth: **everything runs client-side, in code the user's browser can fully see and inspect.** There's no trusted backend server sitting between the user and the identity provider holding secrets safely. This is why SPAs are treated differently in OAuth — they're a "public client," not a "confidential client."

### PKCE (Proof Key for Code Exchange, pronounced "pixy")

PKCE solves a specific problem: in the standard OAuth Authorization Code flow, after the user logs in, the identity provider (Entra ID) redirects back to your app with a temporary **authorization code**. Your app then exchanges that code for the real tokens (ID token, access token).

The vulnerability: if a malicious app on the same device can intercept that redirect (e.g., via a malicious browser extension, or on mobile via URI-scheme hijacking), it could steal the authorization code and exchange it for tokens itself — impersonating the user.

Traditionally, this exchange step was protected by a client secret — only the "real" app knew the secret, so only it could redeem the code. But SPAs can't hold a secret (see above). PKCE replaces the static secret with a **dynamically generated, one-time proof**:

1. Before redirecting the user to log in, your app generates a random string (the **code verifier**) and hashes it (the **code challenge**).
2. Your app sends the *hash* to Entra ID along with the login request.
3. Entra ID stores that hash and later returns the authorization code.
4. When your app exchanges the code for tokens, it must also send the original **unhashed verifier**.
5. Entra ID hashes what it received and checks it matches the challenge from step 2.

Since the verifier is generated fresh each login and never leaves your app until the final exchange, an attacker who intercepts just the authorization code can't complete the exchange — they don't have the verifier. It's a secret invented per-login instead of one baked permanently into the app.

### OAuth vs OIDC

These get conflated constantly, so it's worth being precise:

**OAuth 2.0** is an **authorization** framework — it's about granting access to resources. It answers: "Can this app access this data/API on the user's behalf?" The output is an **access token**, which is essentially a permission slip an API can check. Critically, OAuth was never designed to tell you *who the user is* — access tokens are opaque-ish and meant for resource servers (APIs), not for identifying the person.

**OpenID Connect (OIDC)** is a thin **authentication** layer built on top of OAuth 2.0. It answers: "Who is this user?" It adds:
- The `openid` scope, which signals "I want identity info, not just an access token"
- A new token type: the **ID token** — a signed JWT containing claims about the user (their ID, name, email, etc., depending on scopes)
- Standardized endpoints (like `/userinfo`) and a predictable, standardized way to get identity claims

So in practice:
- **OAuth alone** → "here's a token, go call this API"
- **OIDC** → "here's proof of who this person is, plus an OAuth token if you also need API access"

In your Entra ID registration, this is exactly why `openid` is a required scope — it's the flag that says "I'm doing OIDC (authentication), not just bare OAuth (authorization)." The `profile` and `email` scopes then tell Entra ID which extra claims to stuff into that ID token.

---
## 1. **Register the SPA in Entra ID.**
App registrations → New registration → Platform = Single-page application, with redirect URIs per environment. Leave client secret alone — SPAs are public clients, and a secret embedded in browser JS is a leaked credential. Add `openid`, `profile`, `email` scopes.

This is the first setup step in a federation chain: **Entra ID (Microsoft's identity provider) → AWS Cognito (identity broker) → your app**. Before Cognito can hand off authentication to Entra ID, Entra ID needs to know your app exists and trust it. Here's what each piece means:

**"Register the SPA in Entra ID"** — Entra ID (formerly Azure AD) requires every application that wants to authenticate against it to have an "app registration" — essentially a record that says "this application exists, here's its identity, and here's what it's allowed to do." You create this under **App registrations → New registration** in the Entra admin portal.

**"Platform = Single-page application"** — When you register an app, Entra ID asks what *kind* of client it is (SPA, web app, mobile/desktop, etc.). This isn't cosmetic — it changes the underlying auth mechanics. Selecting "Single-page application" configures the registration to use the Authorization Code flow with PKCE, which is the secure pattern for apps running entirely in the browser (no backend to hold secrets). It also affects how Entra ID handles the redirect response (SPA platform uses the fragment/CORS-friendly response mode suited to JS apps).

**"Redirect URIs per environment"** — After login, Entra ID sends the user back to a specific URL, and it will *only* redirect to URLs you've explicitly whitelisted (this prevents attackers from redirecting auth codes/tokens to malicious sites). Since you likely have different URLs for local dev, staging, and production, you register each one separately — e.g. `http://localhost:3000/callback`, `https://staging.yourapp.com/callback`, `https://yourapp.com/callback`.

**"Leave client secret alone — SPAs are public clients"** — This is the key security point. In OAuth/OIDC terms, a "confidential client" (like a server-side app) can safely hold a secret because the code runs somewhere users can't inspect. A "public client" (SPA, mobile app) runs entirely on the user's device — anyone can open dev tools, view the JS bundle, or inspect network traffic and pull out any secret you embedded. So a "client secret" baked into browser code isn't secret at all — it's just a credential you've handed to every visitor. That's why SPAs rely on PKCE instead: a per-session dynamically generated proof, rather than a static shared secret.

**"Add `openid`, `profile`, `email` scopes"** — These are standard OpenID Connect scopes that determine what identity information comes back in the token:
- `openid` — required to trigger OIDC at all; it's what gets you an ID token (not just an OAuth access token)
- `profile` — includes basic profile claims like name
- `email` — includes the user's email address claim

Once this registration exists, you'd take the resulting **Application (client) ID** and the **Entra tenant's OIDC endpoint** and plug them into Cognito as an OIDC identity provider — that's the "federation" half, where Cognito acts as the broker between your app and Entra ID.

---
## 2. **Wire up MSAL.js** (`npm install @azure/msal-browser`):
Log in with `loginPopup`/`loginRedirect`, read the ID token, and call `acquireTokenSilent` before each AWS credential exchange since Entra tokens are short-lived (~1 hr).
   *Common mistake:* configuring the legacy implicit flow instead of MSAL's default Authorization Code + PKCE — implicit tokens are more exposed.
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
This snippet is where you actually implement the login flow in your SPA's code, using Microsoft's own client library to talk to Entra ID. Let's go through it piece by piece.

### MSAL.js

**MSAL** = **M**icrosoft **A**uthentication **L**ibrary. It's Microsoft's official JS SDK for handling the OIDC/OAuth dance with Entra ID from a browser app, so you don't have to hand-roll redirect logic, PKCE code generation, token parsing, and token refresh yourself. `@azure/msal-browser` is the flavor built specifically for SPAs (public clients, no secret).

### `PublicClientApplication`

This is the core object MSAL gives you to manage auth. Naming it "public" client application is MSAL explicitly encoding the concept from before — it knows this is a browser app with no secret, so internally it will always use the Authorization Code + PKCE flow rather than anything that assumes a confidential client.

### The `auth` config block

- **`clientId`** — the Application (client) ID you got back when you registered the SPA in Entra ID. This tells Entra ID which registered app is making the request.
- **`authority`** — the URL of your specific Entra tenant's login endpoint. `login.microsoftonline.com/<tenant-id>` scopes the login to *your organization's* Entra ID instance (as opposed to allowing any Microsoft account). This is where MSAL actually sends the user to authenticate.
- **`redirectUri`** — must exactly match one of the redirect URIs you registered earlier. After the user logs in at Microsoft's site, this is where they get sent back to, carrying the authorization code.

### `cache: { cacheLocation: "sessionStorage" }`

This tells MSAL where to store tokens once it has them (ID token, access token, refresh token if applicable). MSAL supports two options:

- **`localStorage`** — persists across browser tabs and even after the browser closes/reopens. More convenient (user stays logged in longer), but also means tokens sit around indefinitely and are shared across every tab.
- **`sessionStorage`** — tied to a single tab; cleared when that tab closes.

The comment explains the security tradeoff: both are readable by JavaScript running on your page, so if your app has an **XSS (cross-site scripting)** vulnerability — malicious script gets injected and runs with the same privileges as your app's own code — that script can read whatever's in storage and steal the tokens. `sessionStorage` limits the blast radius: a compromised tab only exposes that tab's tokens, and there's a smaller time window since tokens don't persist indefinitely. It's not immune to XSS (nothing JS-readable is), but it's the more conservative default MSAL's own docs recommend.

### Where this fits in the bigger federation picture

This is worth flagging because it's a subtlety in your original question about "in-app federation": this code talks **directly to Entra ID**, not to Cognito's hosted login UI. That's a specific architectural choice — instead of redirecting the user to a Cognito Hosted UI page (which itself redirects to Entra), your app handles the Entra login itself via MSAL, gets back an ID token directly from Entra, and *then* hands that token to Cognito (typically to a Cognito Identity Pool, using `CognitoIdentityClient` with the Entra ID token as the credential) to get AWS credentials.

This is what "in-app" federation means as opposed to "hosted UI" federation: the login experience stays inside your own app's UI (MSAL can do this as a popup or silent redirect within your page) rather than bouncing the user out to an AWS-branded Cognito login screen. Cognito's role shifts from "identity broker doing the OIDC handshake" to "credential vendor that trusts tokens Entra already issued directly to your app."

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
