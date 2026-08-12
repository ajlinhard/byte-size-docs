# AWS Cognito App Federation through API Gateway

**Yes, this is a solid, conventional architecture.** An OIDC like Entra ID holds the corporate identity, Cognito acts as a broker that turns Entra's identity into its own tokens, and API Gateway validates those tokens before anything touches your code. I'll flag at the end when it's *more* than you need.

## The cast of characters

The thing that trips up most people new to this: there are **two separate OAuth handshakes stacked on top of each other**, and each one produces its own set of tokens that must not be confused.

| Entity | Role | Issues tokens? |
|---|---|---|
| **Your app** (SPA/mobile) | OAuth *client*. Holds no secrets. | No |
| **Cognito User Pool** | Both an *identity provider* (to your app) and a *client* (to Entra). The broker. | Yes — the ones your API trusts |
| **Entra ID** | The upstream *identity provider*. Owns passwords, MFA, Conditional Access. | Yes — but only Cognito ever sees these |
| **API Gateway** | The *bouncer*. Validates Cognito's tokens; rejects bad requests before invoking your backend. | No |
| **Backend** (Lambda/ECS) | Receives already-validated identity as plain JSON. | No |

The single most important rule: **Entra's tokens never reach your app or your API.** They stop at Cognito. Your API only ever trusts one issuer — your Cognito user pool.---

# Phase 1 — Login

### Step 1 · Your app → Cognito

The app never shows its own username/password box. It just redirects the browser. Before redirecting, it generates a PKCE pair — a random `code_verifier` it keeps in memory, and its SHA-256 hash (`code_challenge`) which it sends. This proves later that whoever redeems the code is the same app that started the flow.

```http
GET https://auth.example.com/oauth2/authorize
  ?response_type=code                      # "Authorization Code flow" — give me a code, not a token
  &client_id=7h9k2m4n6p8q0r2s4t6u8v        # which app client in the Cognito user pool
  &redirect_uri=https://app.example.com/callback   # must EXACTLY match an allowed URL in Cognito
  &scope=openid+profile+email+orders.read  # openid = "I want an ID token"; orders.read = custom API scope
  &state=Kx8sPq2mN                         # random value; app checks it comes back unchanged (CSRF guard)
  &code_challenge=E9Melhoa2Ow...           # SHA-256 of the secret the app kept
  &code_challenge_method=S256
  &identity_provider=EntraID               # optional: skip Cognito's "pick a provider" screen
```

**Who's hit:** Cognito's hosted UI domain. Nothing has been authenticated yet.

### Step 2 · Cognito → Entra ID

Cognito doesn't know who you are, so it starts *its own, separate* OAuth flow — this time Cognito is the client and Entra is the server. Notice the `redirect_uri` is now Cognito's own callback, not your app's.

```http
HTTP/1.1 302 Found
Location: https://login.microsoftonline.com/11111111-2222-3333-4444-555555555555/oauth2/v2.0/authorize
  ?client_id=99999999-8888-7777-6666-555555555555   # the App Registration you made in Entra
  &response_type=code
  &redirect_uri=https://auth.example.com/oauth2/idpresponse   # Cognito's fixed federation callback
  &scope=openid%20profile%20email
  &response_mode=query
  &state=eyJ2ZXJzaW9uIjoi...                # Cognito's own state, remembering your app's request
```

**Who's hit:** `login.microsoftonline.com`. This is where the human actually types a password, does MFA, and gets evaluated by Conditional Access policies.

### Step 3 · Entra ID → Cognito

Entra sends the browser back with a short-lived, single-use code.

```http
HTTP/1.1 302 Found
Location: https://auth.example.com/oauth2/idpresponse
  ?code=0.AXoAo1x8...          # Entra's code — Cognito will redeem this
  &state=eyJ2ZXJzaW9uIjoi...   # returned untouched so Cognito can resume your app's request
```

### Step 4 · Cognito → Entra ID (back channel)

This one is **server-to-server** — no browser involved, and it carries Cognito's client secret. This is why the token never leaks to the user's device.

```http
POST https://login.microsoftonline.com/11111111-.../oauth2/v2.0/token
Content-Type: application/x-www-form-urlencoded

grant_type=authorization_code
&code=0.AXoAo1x8...
&client_id=99999999-8888-7777-6666-555555555555
&client_secret=abc~SECRET~xyz          # proves this is really Cognito, not an attacker with a stolen code
&redirect_uri=https://auth.example.com/oauth2/idpresponse
```

Entra responds:

```json
{
  "token_type": "Bearer",
  "expires_in": 3599,
  "access_token": "eyJ0eXAi...",   // for calling Microsoft Graph — Cognito mostly ignores this
  "id_token": "eyJ0eXAi..."        // THIS is what Cognito cares about: who the user is
}
```

Decoding Entra's `id_token` payload — **this is the last time you'll see these claims; they stop here at Cognito:**

```json
{
  "iss": "https://login.microsoftonline.com/11111111-2222-3333-4444-555555555555/v2.0",
  "aud": "99999999-8888-7777-6666-555555555555",  // issued FOR Cognito, not for your API
  "sub": "AAAAAAAAAAAAAAAAAAAAAIkzqFVrSaSaFHy782bbtaQ",  // stable per app+user
  "oid": "7d5b1c9e-...",              // the user's object ID in your tenant — the real user key
  "tid": "11111111-...",              // tenant ID
  "preferred_username": "jane.doe@contoso.com",
  "name": "Jane Doe",
  "email": "jane.doe@contoso.com",
  "groups": ["a1b2c3d4-...", "e5f6a7b8-..."],  // Entra security groups, as GUIDs (if configured)
  "exp": 1755000000, "iat": 1754996400
}
```

### Step 5 · Cognito does its work

No network call — this is internal. Cognito applies your **attribute mapping** (e.g. Entra `email` → Cognito `email`, Entra `oid` → `custom:entra_oid`), and on first login it **just-in-time creates a user** in the user pool with a username like `EntraID_7d5b1c9e-...`. Then it issues *your app's* authorization code:

```http
HTTP/1.1 302 Found
Location: https://app.example.com/callback
  ?code=a1b2c3d4-e5f6-7890-abcd-ef1234567890   # Cognito's code, unrelated to Entra's
  &state=Kx8sPq2mN                             # your app verifies this matches step 1
```

### Step 6 · Your app → Cognito (token exchange)

The app redeems the code. There's **no client secret** here — public clients (SPAs, mobile) can't keep one. The `code_verifier` takes its place.

```http
POST https://auth.example.com/oauth2/token
Content-Type: application/x-www-form-urlencoded

grant_type=authorization_code
&client_id=7h9k2m4n6p8q0r2s4t6u8v
&code=a1b2c3d4-e5f6-7890-abcd-ef1234567890
&redirect_uri=https://app.example.com/callback   # must match step 1 exactly, again
&code_verifier=dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk   # the secret from step 1
```

```json
{
  "id_token": "eyJraWQiOiJ...",       // WHO the user is — for your UI (show name, avatar)
  "access_token": "eyJraWQiOiJ...",   // WHAT they may do — this is what you send to the API
  "refresh_token": "eyJjdHkiOiJ...",  // opaque-ish, long-lived, used to get new tokens silently
  "expires_in": 3600,
  "token_type": "Bearer"
}
```

### Step 7 · The tokens, decoded

Both are JWTs signed by Cognito with RS256. **Note the issuer — this is the only issuer your API will ever trust.**

```json
// ID TOKEN payload — identity. Do NOT use this for API authorization.
{
  "sub": "9f8e7d6c-5b4a-3210-fedc-ba9876543210",   // Cognito's own user ID (≠ Entra's sub/oid)
  "iss": "https://cognito-idp.us-east-1.amazonaws.com/us-east-1_AbCdEf123",
  "aud": "7h9k2m4n6p8q0r2s4t6u8v",                 // audience = your app client
  "token_use": "id",                               // Cognito-specific; guards against token confusion
  "identities": [{
    "userId": "7d5b1c9e-...",                      // the Entra oid — your link back to the source of truth
    "providerName": "EntraID",
    "providerType": "OIDC",
    "primary": "true"
  }],
  "cognito:username": "EntraID_7d5b1c9e-...",
  "cognito:groups": ["Finance-Approvers"],         // Cognito groups (see gotchas — not automatic from Entra)
  "email": "jane.doe@contoso.com",
  "name": "Jane Doe",
  "auth_time": 1754996400,
  "exp": 1755000000, "iat": 1754996400
}
```

```json
// ACCESS TOKEN payload — authorization. This is the one you put in the Authorization header.
{
  "sub": "9f8e7d6c-5b4a-3210-fedc-ba9876543210",
  "iss": "https://cognito-idp.us-east-1.amazonaws.com/us-east-1_AbCdEf123",
  "client_id": "7h9k2m4n6p8q0r2s4t6u8v",   // note: client_id, not aud
  "token_use": "access",
  "scope": "openid profile email orders.read",  // the permissions API Gateway will enforce
  "username": "EntraID_7d5b1c9e-...",
  "jti": "0e4f...", "origin_jti": "aa11...",    // IDs used for revocation
  "exp": 1755000000, "iat": 1754996400
}
```

---

# Phase 2 — Calling the backend API

### Step 8 · Your app → API Gateway

```http
GET https://api.example.com/v1/orders?limit=10
Host: api.example.com
Authorization: Bearer eyJraWQiOiJhYmMxMjMi...   # the ACCESS token from step 6
Accept: application/json
```

**Who's hit:** API Gateway's edge. Your Lambda/container has not run yet and will not run if this fails.

### Step 9 · API Gateway validates (no code of yours involved)

The authorizer does this automatically, and caches aggressively:

1. Reads the JWT header to get `kid` (key ID):
   ```json
   { "alg": "RS256", "kid": "abc123def456=" }
   ```
2. Fetches the public keys — once, then caches:
   ```http
   GET https://cognito-idp.us-east-1.amazonaws.com/us-east-1_AbCdEf123/.well-known/jwks.json
   ```
   ```json
   { "keys": [{ "kid": "abc123def456=", "alg": "RS256", "kty": "RSA",
                "n": "sXchDaQe...", "e": "AQAB", "use": "sig" }] }
   ```
3. Verifies the signature, then checks `exp` (not expired), `iss` (matches your pool), `client_id`/`aud` (matches your app client), and that the required scope `orders.read` is present.

Failures look like this — and your backend never sees the request:

```json
// Missing or malformed header
HTTP/1.1 401 Unauthorized
{ "message": "Unauthorized" }

// Valid token, but missing the orders.read scope
HTTP/1.1 403 Forbidden
{ "message": "Forbidden" }
```

### Step 10 · API Gateway → Backend

The token is *not* re-verified by your code. API Gateway hands over the already-validated claims as plain JSON. For an **HTTP API with a JWT authorizer**:

```json
{
  "version": "2.0",
  "routeKey": "GET /v1/orders",
  "rawPath": "/v1/orders",
  "queryStringParameters": { "limit": "10" },
  "headers": { "authorization": "Bearer eyJraWQ...", "host": "api.example.com" },
  "requestContext": {
    "http": { "method": "GET", "sourceIp": "203.0.113.42" },
    "authorizer": {
      "jwt": {
        "claims": {
          "sub": "9f8e7d6c-5b4a-3210-fedc-ba9876543210",   // trust this — it's verified
          "username": "EntraID_7d5b1c9e-...",
          "client_id": "7h9k2m4n6p8q0r2s4t6u8v",
          "token_use": "access",
          "exp": "1755000000"
        },
        "scopes": ["orders.read"]
      }
    }
  }
}
```

For a **REST API with a `COGNITO_USER_POOLS` authorizer**, the shape differs slightly — claims land at `event.requestContext.authorizer.claims` and are flat:

```json
{ "requestContext": { "authorizer": { "claims": {
    "sub": "9f8e7d6c-...", "email": "jane.doe@contoso.com",
    "cognito:groups": "Finance-Approvers", "token_use": "id"
}}}}
```

### Step 11 · Backend logic and response

Your code reads the claims and scopes data — it does **not** ask "is this user logged in?", only "what may *this* user see?"

```js
const userId = event.requestContext.authorizer.jwt.claims.sub;
const orders = await db.query("SELECT * FROM orders WHERE owner_id = $1", [userId]);
return { statusCode: 200, body: JSON.stringify({ orders }) };
```

```json
HTTP/1.1 200 OK
{ "orders": [ { "id": "ord_881", "total": 42.50, "status": "shipped" } ] }
```

---

### Step 12 · When the hour is up

The access token expires after (by default) 60 minutes. The app refreshes silently — **no redirect, no Entra round-trip, the user sees nothing:**

```http
POST https://auth.example.com/oauth2/token
grant_type=refresh_token
&client_id=7h9k2m4n6p8q0r2s4t6u8v
&refresh_token=eyJjdHkiOiJKV1Qi...
```

```json
{ "id_token": "eyJ...", "access_token": "eyJ...", "expires_in": 3600, "token_type": "Bearer" }
// Note: no new refresh_token unless rotation is enabled
```

When the refresh token itself expires (default 30 days), or you call `GET /logout`, the user goes all the way back to step 1 — including Entra.

---

## Gotchas that bite newcomers here

**Groups don't flow through by themselves.** Entra's `groups` claim contains GUIDs, and Cognito won't turn them into `cognito:groups`. You either map them into a custom attribute (which has a 2048-character limit — large group memberships will blow past it, and Entra will send a `hasgroups` overage claim instead of the list) or use a **Pre Token Generation Lambda** to inject the right groups/scopes. Plan for this before you build authorization logic on top.

**ID token vs access token.** For API authorization, use the **access token** — it carries scopes and is intended for a resource server. The ID token is about the user and is meant for your app. One wrinkle: REST APIs with a Cognito authorizer historically expect the ID token, while HTTP API JWT authorizers expect the access token. Pick one API type and be consistent; mixing them is a classic source of mysterious 401s.

**Scopes require a Resource Server.** `orders.read` doesn't exist until you define a Resource Server in the user pool and enable that scope on the app client. Otherwise your `scope=` parameter is silently dropped.

**Mapped attributes must be mutable.** If you mark a mapped attribute immutable, Cognito sets it once at user creation and Entra's later changes (name change, email change) never propagate.

**Sign-out is two logouts.** Hitting Cognito's `/logout` kills the Cognito session but leaves the Entra session alive — the user clicks "log in" and sails straight back in without a prompt. If you need real sign-out, chain to Entra's `end_session_endpoint`.

**Is Cognito even necessary?** API Gateway's JWT authorizer can point directly at Entra as the issuer, cutting Cognito out entirely. Cognito earns its place when you need: a second user type (customers, contractors, social login) alongside employees, temporary AWS credentials via an Identity Pool, custom auth challenges, or a stable token shape while you swap IdPs behind it. If it's Entra employees only, forever, and no AWS credentials — Cognito is a layer you'll maintain for little gain. Worth deciding deliberately rather than by default.
