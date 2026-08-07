
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

This step is about establishing a trust relationship so AWS will accept tokens issued by Entra ID as proof of identity. Here's what's actually happening and what you need to have ready.

**Before you start (on the Entra ID side)**

You need an app registration in Entra ID for this integration, from which you'll get:
- **Tenant ID** (GUID) — from the Entra admin center → your tenant's Overview page
- **Application (client) ID** — from the app registration's Overview page

**Doing the registration in IAM**

1. In the AWS Console, go to IAM → Access management → **Identity providers** → **Add provider**.
2. Choose **OpenID Connect** as the provider type.
3. **Provider URL**: enter `https://login.microsoftonline.com/<tenant-id>/v2.0`, substituting your actual tenant ID. This has to match the `issuer` value Entra ID puts in its tokens and in its discovery document (you can sanity-check it by fetching `https://login.microsoftonline.com/<tenant-id>/v2.0/.well-known/openid-configuration`).
4. AWS will fetch a TLS certificate thumbprint from that URL automatically (this validates the certificate chain of the IdP's endpoint). For well-known providers like Microsoft, you generally don't need to supply this manually — AWS handles it.
5. **Audience**: enter the Application (client) ID from your Entra app registration. This must match the `aud` claim on ID tokens Entra issues, since that's what AWS checks the token against.
6. Save. This creates an IAM resource with an ARN like `arn:aws:iam::<account-id>:oidc-provider/login.microsoftonline.com/<tenant-id>/v2.0`.

**What this does — and doesn't — accomplish**

Registering the provider just tells AWS "I trust tokens signed by this issuer." It doesn't grant any access by itself. You still need an **IAM role** with a trust policy referencing this provider ARN, typically with a condition on the `aud` claim (and often `sub` or other claims) to control exactly who can assume the role.

---
## 4. **Cognito route:** 
Create an Identity Pool, add the OIDC provider ARN under authentication providers, let it generate (or attach) an authenticated IAM role. Cognito Identity Pool federation: an Identity Pool exchanges tokens for temporary AWS credentials, and one of its supported "login providers" is an OIDC provider that must first be registered in IAM exactly as described above. This is the pattern your step matches.

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

## Cognito route: Identity Pool federation

1. **Create an Identity Pool** (Cognito → Identity pools → Create identity pool). This is a distinct resource from a User Pool — it exists specifically to hand out temporary AWS credentials, not to manage user accounts or sign-in UI.

2. **Add the OIDC provider ARN under authentication providers.** In the Identity Pool's settings, under "Authentication providers," there's a **Custom** (or OpenID Connect) tab where you reference the IAM Identity Provider ARN from the previous step — `arn:aws:iam::<account-id>:oidc-provider/login.microsoftonline.com/<tenant-id>/v2.0`. This tells the Identity Pool "tokens from this issuer are a valid login source."

3. **Let it generate (or attach) an authenticated IAM role.** Every Identity Pool needs at least one IAM role for "authenticated" identities (and optionally one for "unauthenticated" guest access). Cognito can create a default role for you, or you attach an existing one. Cognito auto-inserts a trust policy on that role scoped to `cognito-identity.amazonaws.com`, with conditions tying it to your specific Identity Pool ID — so only credential requests that came through *this* Identity Pool can assume it.

4. **At runtime**, your app calls Cognito's `GetId` and `GetCredentialsForIdentity` APIs (or the Amplify/AWS SDK equivalents), passing the Entra ID token as the login. Cognito validates the token against the registered provider, maps the user to a Cognito "Identity ID" (a stable, federated identity), and returns temporary credentials for the attached role.

**Why choose this:** you get a persistent identity ID per user (useful if you're also using Cognito Sync, fine-grained per-user IAM policy variables like `cognito-identity.amazonaws.com:sub`, or mixing multiple identity providers under one roof), and there's a bit more built-in plumbing for role selection rules if different users should get different roles.

---
## 5. **Scope the role tightly.** 
These permissions are effectively public to every logged-in app user — least-privilege it (specific S3 prefixes, specific tables), never a broad managed policy. You need to pair certain users to certain roles in IAM. 

The trust relationship is: anyone holding a valid Entra ID token for your app can exchange it for credentials from this role. There's no per-user distinction baked in by default — User A and User B, after logging in, both get the exact same role, with the exact same permissions. Two concrete consequences:

- The app's UI is not a security boundary. Your React app might only ever call GetObject on the user's own folder — but the credentials sitting in that browser tab can call anything the role allows. Anyone can open devtools, pull the access key/secret/session token out of memory, and run aws s3 ls s3://your-bucket/ from the CLI with another user's data fully in scope, if the role permits it.
- One compromised session = every user's blast radius. If the app has an XSS bug, or a browser extension harvests the tab's memory, the attacker doesn't just get that user's access — they get whatever the shared role can touch, full stop.

### A scaling note

If you end up with many fine-grained permission tiers, proliferating a dozen near-identical IAM roles gets unwieldy. At that point, look into **ABAC (attribute-based access control)** — pass a session tag (e.g. `Department=Engineering`) when assuming the role, and write your resource policies with conditions like `"Condition": {"StringEquals": {"aws:PrincipalTag/Department": "Engineering"}}`. One role, many effective permission sets. For the direct STS route you pass tags explicitly as a parameter derived from your claims/DB lookup — it isn't automatic the way it is with SAML attribute mapping.

---
## 6. **Use the credentials** with AWS SDK v3 clients (`S3Client`, `DynamoDBClient`, etc.), and re-derive them before the ~1 hour expiry rather than reusing stale ones.

## What "use the credentials with SDK v3 clients" means

Once you have credentials (from `fromWebToken` or the Cognito Identity Pool), you pass them into a service client's constructor:

```js
import { S3Client, ListBucketsCommand } from "@aws-sdk/client-s3";

const s3 = new S3Client({
  region: "us-east-1",
  credentials: credentialsProviderOrObject,
});

await s3.send(new ListBucketsCommand({}));
```

`credentials` here can be either a plain object (`accessKeyId`, `secretAccessKey`, `sessionToken`, `expiration`) or — better — a **provider function**: `() => Promise<credentials>`. This distinction is the whole point of the "re-derive" instruction.

## Why this matters: two very different behaviors

**If you pass a resolved static object:** the client uses it for every request until it fails. Once the underlying STS credentials expire (default is 1 hour for `AssumeRoleWithWebIdentity`, extendable up to the IAM role's Max Session Duration setting, up to 12 hours), every subsequent call throws `ExpiredTokenException`.

**If you pass the provider function itself** (e.g. `credentials: fromWebToken({...})`), SDK v3's client middleware checks the `expiration` field on the cached credentials before each request. When it's within about 5 minutes of expiring, the client automatically re-invokes the provider function to get a fresh set — no manual timer or retry logic needed on your part.

So concretely:

```js
// ❌ Anti-pattern: resolves once, then goes stale after ~1hr
const creds = await fromWebToken({ roleArn, webIdentityToken, roleSessionName })();
const s3 = new S3Client({ region, credentials: creds });

// ✅ Correct: pass the provider, let the SDK refresh it automatically
const s3 = new S3Client({
  region,
  credentials: fromWebToken({ roleArn, webIdentityToken, roleSessionName }),
});
```

## The catch this doesn't fully solve: the Entra token itself expires too

Here's the part that trips people up, and it's a known limitation (there's an open [GitHub issue](https://github.com/aws/aws-sdk-js-v3/issues/5270) on this exact behavior): `fromWebToken` bakes in the `webIdentityToken` string you gave it *at creation time*. When the SDK "refreshes" by re-calling the provider, it re-runs `AssumeRoleWithWebIdentity` with that **same original Entra ID token** — but that token has its own expiry (also typically ~1 hour, set by Entra ID). So auto-refresh on the STS-credential side is useless if the underlying identity token has gone stale too; you'll get an `ExpiredTokenException` from STS regardless.

The fix is to wrap `fromWebToken` in your own provider function that re-acquires a fresh Entra token first:

```js
import { fromWebToken } from "@aws-sdk/credential-providers";

const credentialsProvider = async () => {
  // MSAL silently refreshes using its own refresh token if the cached one is stale
  const tokenResponse = await msalInstance.acquireTokenSilent({
    scopes: ["api://<your-app-client-id>/.default"],
    account: msalInstance.getActiveAccount(),
  });

  return fromWebToken({
    roleArn: "arn:aws:iam::<acct>:role/<role-name>",
    webIdentityToken: tokenResponse.idToken,
    roleSessionName: "webapp-session",
  })();
};

const s3 = new S3Client({ region: "us-east-1", credentials: credentialsProvider });
```

Because `acquireTokenSilent` handles Entra ID's own token refresh transparently (using MSAL's cached refresh token, or a silent iframe/redirect if needed), each call to `credentialsProvider` produces a genuinely fresh chain: new Entra token → fresh STS credentials. Just make sure this function itself returns an object with an `expiration` field (which `fromWebToken()()` does), so the SDK client still knows when to call it again.

## Summary of the practical rule

Never treat credentials as a one-time value you fetch and stash — treat credential *acquisition* as a repeatable function, and let the SDK's client-level caching decide when to call it again. If your flow involves a third-party identity token (like Entra's), that function needs to refresh the identity token too, not just re-call STS with a copy that's already gone bad.

---
## 7. **For per-user permission differences**, map Entra group/role claims to Cognito role-mapping rules or separate roles — don't default everyone into one broad "authenticated" role for convenience.


**1. Push role info into the token itself (Entra-side), so no DB lookup is needed at all**

In your Entra ID app registration, you can define **App Roles** (App registrations → your app → App roles → Create app role, e.g. `Admin`, `Editor`, `Viewer`). Then in Entra ID → Enterprise applications → your app → Users and groups, you assign specific users or Entra ID groups to those roles. Once that's set up, Entra ID adds a `roles` claim to the ID token:

```json
"roles": ["Admin"]
```

This pushes access control up into Entra ID, which is often exactly what an IT/security team wants — role assignment lives where the org already manages identity, and you avoid maintaining a shadow permissions table. The tradeoff: your app has less flexibility, and every role change requires an Entra admin action.

**2. Look up permissions in your own database, keyed on `oid`**

If your permission model is more granular than Entra ID's app roles support, or you want app-level control over it, decode the token, pull `oid`, and query your own table:

```
SELECT role FROM user_permissions WHERE entra_oid = '<oid-from-token>'
```

This is the more common pattern once permissions get complex (resource-level, multi-tenant, frequently changing).

## Wiring that decision into role selection

How you actually route to an IAM role differs by which route you're on:

**Cognito Identity Pool route** — this is a first-class feature, no custom code needed. Under Identity Pool → Authentication providers → your OIDC provider, you set **Role mapping type = Rules**, and define rules like "if claim `roles` equals `Admin`, use role X; if `roles` equals `Viewer`, use role Y." Up to 25 rules, evaluated in order, first match wins. This works cleanly with strategy #1 (Entra App Roles) since the claim is right there in the token. It's *not* built to do a database lookup — the matching only sees token claims, so if you need strategy #2, you'd need a Lambda-backed pre-token-generation step or handle role selection before you ever call Cognito.

### Entra ID gives you identity claims, but pick the right one

The ID token from Entra ID (a JWT) carries several identity-related claims. Not all are equally suited to a database lookup:

| Claim | What it is | Stable for lookups? |
|---|---|---|
| `oid` | Object ID — a GUID unique to the user within the tenant | **Yes — use this as your primary key** |
| `sub` | Subject identifier, scoped per-app | Yes, but changes if you reconfigure the app registration's identifier URI, and isn't shared across apps |
| `preferred_username` | Usually the UPN/email-like string | No — can change if the user is renamed/re-emailed |
| `email` | Email address, only present if requested/configured | No — same caveat, and not always populated |
| `name` | Display name | No — cosmetic only |

The common mistake is keying your permissions database on email or `preferred_username` because it's human-readable. Don't — Entra admins can and do change UPNs (marriage, department transfers, tenant renames). Use **`oid`** as your stable foreign key, and store email/name alongside it just for display purposes.

**Direct STS route** — there's no built-in mapping mechanism; your app owns the decision. Since the trust policy grants `AssumeRoleWithWebIdentity` to a *specific* role, "routing" just means your backend decodes the token, decides which role ARN applies (from a claim, a DB lookup, or both), and calls `fromWebToken` with that ARN:

```js
import { fromWebToken } from "@aws-sdk/credential-providers";
import { jwtDecode } from "jwt-decode";

const claims = jwtDecode(idTokenFromMsal);
const roleArn = await lookupRoleArn(claims.oid); // your DB lookup, or claims.roles[0]

const credentials = fromWebToken({
  roleArn,
  webIdentityToken: idTokenFromMsal,
  roleSessionName: claims.oid, // ties CloudTrail entries back to the user
});
```

Each candidate role's trust policy still needs the same `Federated` principal and `aud` condition from before — you're just choosing *which* pre-configured role to call at runtime. This route gives you full flexibility (any lookup logic you want) at the cost of writing that logic yourself.

---
**Risks specific to browser-side federation:**
- **XSS = credential theft.** Anything that runs JS in your origin can read the token/credentials in memory. Strict CSP and dependency hygiene matter a lot more once AWS creds live in the tab.
- **No server-side authorization check.** A valid Entra token is the *only* gate — no app-specific business logic (subscription tier, account status). For anything beyond low-risk reads, put a thin backend in between: it validates the token against Entra's JWKS, applies your own rules, then either proxies the AWS call or mints a narrower session.
- **sessionStorage vs localStorage** for the MSAL cache — localStorage persists across tabs/reboots but widens XSS blast radius; sessionStorage is the safer default.

---

**Cross-cutting risk:** once either integration exists, an Entra ID tenant compromise becomes an AWS compromise. Require phishing-resistant MFA/Conditional Access on any account able to edit these app registrations, and don't let permission sets or IAM roles drift toward "just give admin, fix it later" — that's the most common finding in audits of these setups after the fact.

I can save this as a markdown or Word reference doc if you want a copy to keep, and happy to go deeper on either the SAML/SCIM config or the JS credential-exchange code.Let me know if you'd like me to go deeper on either piece — e.g., the exact Entra token-configuration claims for group-based role mapping, a working Cognito Identity Pool + MSAL.js sample, or the SCIM attribute-mapping details for provisioning custom user attributes.
