# AWS Congnito OIDC Application Federation through an ALB
Below is the whole flow end to end. I'll use these fixed values throughout so you can follow one user through the system:

| Thing | Value |
|---|---|
| Your app | `https://app.example.com` |
| ALB ARN | `arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/my-alb/50dc6c495c0c9188` |
| Cognito user pool | `us-east-1_AbCdEfGhI` |
| Cognito hosted domain | `https://my-app.auth.us-east-1.amazoncognito.com` |
| Cognito app client ID | `7a1b2c3d4e5f6g7h8i9j0k1l2m` |
| Entra tenant ID | `11111111-2222-3333-4444-555555555555` |
| Entra app (client) ID | `aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee` |
| The human | Jane Doe, `jane.doe@contoso.com` |

## The cast of characters

```
Browser ──► ALB ──► Cognito ──► Entra ID
             │        │            │
             │        └─ Cognito is an OIDC *client* of Entra,
             │           and an OIDC *provider* to the ALB
             │
             └─ ALB is the OIDC *client* of Cognito, and the only
                thing that ever holds the real tokens
             │
             ▼
        Target group (your ECS task / EC2 / Lambda)
```

The key mental model: **this is two chained OIDC handshakes.** ALB↔Cognito is one, Cognito↔Entra is another. Your application code participates in neither — it just receives some headers at the end. The browser never sees a real token either; it only gets an opaque encrypted cookie.

---
## Front channel vs. back channel

This is the distinction that makes steps 7–9 make sense, so let's nail it first.

**Front channel** = communication that travels *through the user's browser*, using HTTP redirects. Party A doesn't talk to Party B directly; A sends a 302 to the browser, and the browser carries the message to B as a URL query string.

```
   ALB                    Browser                   Cognito
    │                        │                         │
    │──302 Location: ...────►│                         │
    │   ?code=abc            │───GET /...?code=abc────►│
    │                        │                         │
    └─ never touched Cognito ┘ ─ carried the message ──┘
```

**Back channel** = a direct, ordinary HTTPS request from one server to another. No browser, no redirect, no user involvement. The ALB opens a TCP connection to Cognito's public endpoint and does a plain `POST`, exactly like your code calling any REST API.

```
   ALB ═══════ POST /oauth2/token ═══════► Cognito
        (direct HTTPS, browser has no idea this happened)
```

Why the distinction matters enormously:

| | Front channel | Back channel |
|---|---|---|
| Visible in browser devtools | Yes | **No** |
| Lands in browser history | Yes | No |
| Leaks via `Referer` header | Yes | No |
| Ends up in proxy/CDN access logs | Yes | No |
| Can carry a client secret | **Never** | Yes |
| Size limit | ~2 KB (URL length) | None |
| Sender's identity proven | No | Yes (via secret/mTLS) |

The front channel is *untrusted transport*. Anything you put in it should be assumed to be readable by the user, loggable, and stealable. That's precisely why the authorization code flow exists: the front channel carries only a **code**, which is useless on its own, and the actual tokens are fetched over the back channel where a client secret proves who's asking.

Mapping this onto the flow you already have:

```
Step 2  front  ALB ──browser──► Cognito     (authorize request)
Step 3  front  Cognito ──browser──► Entra   (authorize request)
Step 4  front  Entra ──browser──► Cognito   (code returned)
Step 5  BACK   Cognito ═══════► Entra       (code → tokens)   ◄── no browser
Step 6  front  Cognito ──browser──► ALB     (code returned)
Step 7  BACK   ALB ═══════► Cognito         (code → tokens)   ◄── no browser
```

Steps 5 and 7 are the only two exchanges where real tokens move, and both are invisible to the browser.


---

# Part 1 — Logging in

## Step 1 — Browser hits the app with no session

**Browser → ALB**

```http
GET /dashboard HTTP/1.1
Host: app.example.com
Accept: text/html
# No AWSELBAuthSessionCookie present, so the ALB has no idea who this is.
```

## Step 2 — ALB kicks off OIDC handshake #1

The ALB listener rule has an `authenticate-cognito` action in front of the `forward` action. Since there's no session, the authenticate action fires.

**ALB → Browser**

```http
HTTP/1.1 302 Found
Location: https://my-app.auth.us-east-1.amazoncognito.com/oauth2/authorize
  ?client_id=7a1b2c3d4e5f6g7h8i9j0k1l2m
  &response_type=code
  &scope=openid+email
  &redirect_uri=https%3A%2F%2Fapp.example.com%2Foauth2%2Fidpresponse
  &state=eyJzdGF0ZSI6ICJ7XCJyZWRpcmVjdFVyaVwiOiBcImh0dHBzOi8vYXBwLm...
  &identity_provider=EntraID
Set-Cookie: AWSELBAuthNonce=Vk9tYlZ...; Path=/; Secure; HttpOnly; SameSite=None
```

Comments on each param:

- `response_type=code` — **authorization code flow**. The browser will only ever carry a short-lived, single-use code. Tokens are fetched over a separate back-channel HTTPS call the browser can't observe. This is the whole point of the code flow.
- `redirect_uri=.../oauth2/idpresponse` — this path is reserved and handled by the ALB itself; it never reaches your target group. You don't write a route for it.
- `state` — an opaque blob the ALB signed. It encodes the URL you originally asked for (`/dashboard`) plus a nonce that must match the `AWSELBAuthNonce` cookie. This is CSRF protection: an attacker can't forge a callback because they can't produce a matching state+nonce pair.
- `identity_provider=EntraID` — optional. This is set via `AuthenticationRequestExtraParams` on the ALB action. Including it makes Cognito skip its own login page and go straight to Entra. Without it, Jane sees the Cognito Hosted UI with a "Sign in with EntraID" button.
- `scope=openid email` — `openid` is mandatory; it's what makes this OIDC rather than plain OAuth2, and it's what causes an `id_token` to be issued.

## Step 3 — Cognito starts handshake #2 with Entra

Cognito's user pool has an identity provider of type OIDC configured, pointing at your Entra tenant. Cognito now flips roles: it was the *server* a moment ago, now it acts as a *client*.

**Browser → Cognito**, then **Cognito → Browser**

```http
HTTP/1.1 302 Found
Location: https://login.microsoftonline.com/11111111-2222-3333-4444-555555555555/oauth2/v2.0/authorize
  ?client_id=aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee
  &response_type=code
  &redirect_uri=https%3A%2F%2Fmy-app.auth.us-east-1.amazoncognito.com%2Foauth2%2Fidpresponse
  &scope=openid+profile+email
  &state=NDU2MzI2OWEtY2ExMy00...
  &nonce=e8f7a2c1b9d4
```

Note the `redirect_uri` is now the **Cognito** domain, not your app. Entra sends the user back to Cognito, and only later does Cognito send them back to the ALB. Each hop only knows about its immediate neighbours.

The `nonce` here is a different thing from the ALB's nonce cookie — it's an OIDC replay guard that Entra will echo inside the `id_token` so Cognito can confirm the token was minted for *this* request.

## Step 4 — Entra actually authenticates the human

This is the only step where a password, MFA prompt, Conditional Access check, or device compliance check happens. Entra evaluates its policies, then sets its own session cookies (`ESTSAUTH*`) on `login.microsoftonline.com` so the next app federated to Entra gets SSO for free.

**Entra ID → Browser**

```http
HTTP/1.1 302 Found
Location: https://my-app.auth.us-east-1.amazoncognito.com/oauth2/idpresponse
  ?code=0.AXoAqm7...truncated...&state=NDU2MzI2OWEtY2ExMy00...
```

That `code` is worthless to anyone who steals it — redeeming it requires Entra's client secret, which only Cognito has.

## Step 5 — Cognito redeems the Entra code (back channel)

**Cognito → Entra ID.** This is a direct server-to-server POST. No browser involved.

```http
POST /11111111-2222-3333-4444-555555555555/oauth2/v2.0/token HTTP/1.1
Host: login.microsoftonline.com
Content-Type: application/x-www-form-urlencoded

grant_type=authorization_code
&code=0.AXoAqm7...
&redirect_uri=https%3A%2F%2Fmy-app.auth.us-east-1.amazoncognito.com%2Foauth2%2Fidpresponse
&client_id=aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee
&client_secret=Xy8Q~verySecretValue
```

**Entra ID → Cognito**

```json
{
  "token_type": "Bearer",
  "scope": "openid profile email",
  "expires_in": 3599,
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsIng1dCI6...",
  "id_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImtpZCI6..."
}
```

The **Entra `id_token`**, base64-decoded payload:

```json
{
  "aud": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",   // Cognito's Entra app registration — proves the token was issued FOR Cognito
  "iss": "https://login.microsoftonline.com/11111111-2222-3333-4444-555555555555/v2.0",
  "iat": 1754899200,
  "nbf": 1754899200,
  "exp": 1754902800,                                // ~1 hour
  "nonce": "e8f7a2c1b9d4",                          // echoes step 3 — replay protection
  "sub": "Xy7kL9mN2pQ4rS6tU8vW0xY1zA3bC5dE7fG9hI",  // PAIRWISE: unique per app registration. Different app = different sub for the same Jane.
  "oid": "99999999-8888-7777-6666-555555555555",    // Jane's REAL, tenant-wide object ID. This is what matches Graph API / your directory.
  "tid": "11111111-2222-3333-4444-555555555555",    // tenant — check this if you're multi-tenant
  "email": "jane.doe@contoso.com",
  "name": "Jane Doe",
  "preferred_username": "jane.doe@contoso.com",     // human-friendly, MUTABLE — never use as a primary key
  "groups": ["8a0f1c2d-...", "3e4f5a6b-..."],       // only if you enabled group claims; these are group *object IDs*
  "ver": "2.0"
}
```

Cognito validates this token's signature against Entra's JWKS at `https://login.microsoftonline.com/{tenant}/discovery/v2.0/keys`, checks `aud`, `iss`, `exp`, and `nonce`, then maps the claims onto user pool attributes according to your attribute-mapping config (e.g. Entra `email` → Cognito `email`).

If this is Jane's first login, Cognito **creates a federated user record** in the pool at this moment.

## Step 6 — Cognito completes handshake #1

**Cognito → Browser**

```http
HTTP/1.1 302 Found
Location: https://app.example.com/oauth2/idpresponse
  ?code=b7e2f4a1-9c3d-4e5f-8a7b-1c2d3e4f5a6b
  &state=eyJzdGF0ZSI6ICJ7XCJyZWRpcmVjdFVyaVwiOiBcImh0dHBzOi8vYXBwLm...
```

Same `state` blob from step 2, handed back untouched. A brand new code — this one is Cognito's, not Entra's.

## Step 7 — ALB redeems the Cognito code (back channel)

**ALB → Cognito.** Again server-to-server.

```http
POST /oauth2/token HTTP/1.1
Host: my-app.auth.us-east-1.amazoncognito.com
Content-Type: application/x-www-form-urlencoded
Authorization: Basic N2ExYjJjM2Q0ZTVmNmc3aDhpOWowazFsMm06c2VjcmV0...
                # ^ base64(client_id ":" client_secret) — the ALB's copy of the app client secret

grant_type=authorization_code
&code=b7e2f4a1-9c3d-4e5f-8a7b-1c2d3e4f5a6b
&redirect_uri=https%3A%2F%2Fapp.example.com%2Foauth2%2Fidpresponse
```

**Cognito → ALB**

```json
{
  "id_token":      "eyJraWQiOiJLTzRVMWZ...",
  "access_token":  "eyJraWQiOiJkbmY4M0h...",
  "refresh_token": "eyJjdHkiOiJKV1QiLCJlbmMiOiJBMjU2R0NNIiwiYWxnIjoiUlNBLU9BRVAifQ...",
  "expires_in": 3600,
  "token_type": "Bearer"
}
```

**Cognito `id_token`** payload — *who Jane is*:

```json
{
  "sub": "a1b2c3d4-1111-2222-3333-444455556666",   // Cognito's OWN user ID. Stable. This is your app's primary key for Jane.
  "iss": "https://cognito-idp.us-east-1.amazonaws.com/us-east-1_AbCdEfGhI",
  "aud": "7a1b2c3d4e5f6g7h8i9j0k1l2m",             // the ALB's app client
  "token_use": "id",                                // MUST be "id" — see note below
  "cognito:username": "EntraID_99999999-8888-7777-6666-555555555555",
  "cognito:groups": ["us-east-1_AbCdEfGhI_EntraID"],
  "identities": [
    {
      "userId": "99999999-8888-7777-6666-555555555555",  // ← Entra's `oid`, preserved. Your bridge back to the directory.
      "providerName": "EntraID",
      "providerType": "OIDC",
      "primary": "true",
      "dateCreated": "1754899210000"
    }
  ],
  "email": "jane.doe@contoso.com",
  "email_verified": false,
  "auth_time": 1754899210,
  "iat": 1754899212,
  "exp": 1754902812
}
```

**Cognito `access_token`** payload — *what Jane may do*:

```json
{
  "sub": "a1b2c3d4-1111-2222-3333-444455556666",
  "iss": "https://cognito-idp.us-east-1.amazonaws.com/us-east-1_AbCdEfGhI",
  "token_use": "access",                            // MUST be "access"
  "client_id": "7a1b2c3d4e5f6g7h8i9j0k1l2m",       // note: access tokens have client_id, NOT aud
  "scope": "openid email api.example.com/orders.read",
  "username": "EntraID_99999999-8888-7777-6666-555555555555",
  "jti": "f0e1d2c3-b4a5-6789-0123-456789abcdef",
  "auth_time": 1754899210,
  "iat": 1754899212,
  "exp": 1754902812,
  "version": 2
}
```

The `id_token` vs `access_token` distinction trips up almost everyone new to this. The rule of thumb: **the ID token is for you to learn who logged in; the access token is for presenting to an API.** An API should never accept an ID token as a bearer credential, because the ID token's audience is your login client, not the API. Checking `token_use` is how you enforce that in Cognito's world.

Notice Entra's `groups` did **not** survive into the Cognito tokens. Federated claims only propagate if you explicitly map them to a custom attribute (e.g. `custom:groups`) and add that attribute to the app client's read scope. This is a very common surprise.

## Step 8 — ALB creates the session

The ALB stores those three tokens **server-side**, in its own session store, keyed by a random session ID. Only the key goes to the browser, AES-encrypted.

**ALB → Browser**

```http
HTTP/1.1 302 Found
Location: https://app.example.com/dashboard
Set-Cookie: AWSELBAuthSessionCookie-0=Ae3fQ9x...; Path=/; Secure; HttpOnly; SameSite=None; Max-Age=604800
Set-Cookie: AWSELBAuthSessionCookie-1=Kp2mZ7v...; Path=/; Secure; HttpOnly; SameSite=None
Set-Cookie: AWSELBAuthNonce=; Max-Age=0
```

Two cookies because browsers cap a cookie at ~4 KB; the ALB shards across `-0`, `-1`, `-2`… as needed. `HttpOnly` means your JavaScript **cannot read it**, which is deliberate and matters a lot for Part 2.

## Step 9 — The authenticated request finally reaches your code

**Browser → ALB → Target group**

```http
GET /dashboard HTTP/1.1
Host: app.example.com
Cookie: AWSELBAuthSessionCookie-0=Ae3fQ9x...; AWSELBAuthSessionCookie-1=Kp2mZ7v...
```

The ALB decrypts the cookie, looks up the session, confirms it's live, **strips the cookie's auth value from view of your app**, and injects three headers:

```http
GET /dashboard HTTP/1.1
Host: app.example.com
X-Forwarded-For: 203.0.113.42
X-Forwarded-Proto: https
x-amzn-oidc-identity: a1b2c3d4-1111-2222-3333-444455556666
x-amzn-oidc-accesstoken: eyJraWQiOiJkbmY4M0h...
x-amzn-oidc-data: eyJ0eXAiOiJKV1QiLCJraWQiOiIzOGMxYTNlNS0...
```

- `x-amzn-oidc-identity` — just the `sub` claim, plain text. Convenient, but **do not trust it on its own.**
- `x-amzn-oidc-accesstoken` — the raw Cognito access token, verbatim. Use this to call downstream APIs.
- `x-amzn-oidc-data` — a *new* JWT that the **ALB itself** minted and signed with ES256. Header:

```json
{
  "typ": "JWT",
  "alg": "ES256",
  "kid": "38c1a3e5-7b2f-4d6a-9c8e-1f0a2b3c4d5e",
  "iss": "https://cognito-idp.us-east-1.amazonaws.com/us-east-1_AbCdEfGhI",
  "client": "7a1b2c3d4e5f6g7h8i9j0k1l2m",
  "signer": "arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/my-alb/50dc6c495c0c9188",
  "exp": 1754899512
}
```

Payload (the user claims, sourced from Cognito's `/oauth2/userInfo`):

```json
{
  "sub": "a1b2c3d4-1111-2222-3333-444455556666",
  "email": "jane.doe@contoso.com",
  "username": "EntraID_99999999-8888-7777-6666-555555555555",
  "exp": 1754899512,
  "iss": "https://cognito-idp.us-east-1.amazonaws.com/us-east-1_AbCdEfGhI"
}
```

Note the very short `exp` — a few minutes. This token exists only for the ALB→target hop.

### Verifying it in your app

```python
import jwt, base64, json, requests

REGION = "us-east-1"
EXPECTED_SIGNER = "arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/my-alb/50dc6c495c0c9188"

def verify_alb_header(encoded_jwt: str) -> dict:
    # 1. Peek at the header to get kid + signer. NOT yet trusted.
    header_b64 = encoded_jwt.split(".")[0]
    header = json.loads(base64.urlsafe_b64decode(header_b64 + "=="))

    # 2. CRITICAL: confirm the claimed signer is YOUR load balancer.
    #    Without this, anyone with any ALB in any AWS account could mint
    #    a validly-signed token and impersonate your users.
    if header["signer"] != EXPECTED_SIGNER:
        raise ValueError("unexpected signer")

    # 3. Fetch the EC public key for that kid. Cache this — don't fetch per request.
    pem = requests.get(
        f"https://public-keys.auth.elb.{REGION}.amazonaws.com/{header['kid']}"
    ).text

    # 4. Verify signature + expiry. Only now are the claims trustworthy.
    return jwt.decode(encoded_jwt, pem, algorithms=["ES256"])
```

> **The single most important security note in this whole setup:** these headers are only trustworthy if requests *cannot reach your targets except through the ALB*. An attacker who can hit your ECS task or EC2 instance directly on port 8080 can simply set `x-amzn-oidc-identity` to whatever they like. Lock the target security group to accept traffic only from the ALB's security group, and treat `x-amzn-oidc-identity` as a convenience field you only use after `x-amzn-oidc-data` has verified.

---

# Part 2 — Calling a backend API with the right token

There are two shapes here and choosing the wrong one is the usual source of confusion.

## Scenario A — API is behind the same ALB

Your listener has a rule for `/api/*` pointing at a different target group, with the **same** `authenticate-cognito` action in front. This is the simplest setup and needs almost no code.

**Browser → ALB**

```js
// The session cookie is HttpOnly, so JS can't read it — but the browser
// will attach it automatically. `credentials: "include"` is required if
// the API is on a different origin; unnecessary if same-origin.
const res = await fetch("https://app.example.com/api/orders", {
  method: "GET",
  credentials: "include",
  headers: { "Accept": "application/json" }
});
```

```http
GET /api/orders HTTP/1.1
Host: app.example.com
Cookie: AWSELBAuthSessionCookie-0=Ae3fQ9x...; AWSELBAuthSessionCookie-1=Kp2mZ7v...
Accept: application/json
# No Authorization header. There's nothing for the browser to put in one —
# it never received a token. The cookie IS the credential.
```

**ALB → Orders service** (identical injection to step 9):

```http
GET /api/orders HTTP/1.1
Host: app.example.com
x-amzn-oidc-identity: a1b2c3d4-1111-2222-3333-444455556666
x-amzn-oidc-accesstoken: eyJraWQiOiJkbmY4M0h...
x-amzn-oidc-data: eyJ0eXAiOiJKV1QiLCJraWQiOiIzOGMxYTNlNS0...
```

The orders service runs the same `verify_alb_header()` and returns data.

One important gotcha: if the session has expired, the ALB responds to your `fetch` with a **302 to Cognito**, not a 401. `fetch` follows redirects transparently, and your JS ends up trying to `JSON.parse` an HTML login page. Handle it by checking `res.redirected` or `res.url`, or configure the ALB's `OnUnauthenticatedRequest` action to `deny` for `/api/*` paths so it returns a clean 401 instead.

## Scenario B — API is a separate service (API Gateway, another ALB, a partner service)

Now you need a real bearer token, and the browser doesn't have one. The pattern is: **your web tier forwards the access token it received from the ALB.**

**Web tier → Orders API**

```python
# Inside your /dashboard handler, running behind the ALB.
import requests

def call_orders_api(request):
    # The ALB handed us the raw Cognito access token. Pass it straight through.
    cognito_access_token = request.headers["x-amzn-oidc-accesstoken"]

    return requests.get(
        "https://api.example.com/orders",
        headers={
            "Authorization": f"Bearer {cognito_access_token}",
            # Do NOT forward x-amzn-oidc-data — its audience is this ALB->target
            # hop only, it expires in minutes, and the downstream service has
            # no reason to trust your ALB's ARN.
        },
    )
```

```http
GET /orders HTTP/1.1
Host: api.example.com
Authorization: Bearer eyJraWQiOiJkbmY4M0h1c...
Accept: application/json
```

**Orders API validates it** against Cognito's JWKS at
`https://cognito-idp.us-east-1.amazonaws.com/us-east-1_AbCdEfGhI/.well-known/jwks.json`:

```python
from jwt import PyJWKClient
import jwt

JWKS = PyJWKClient(
    "https://cognito-idp.us-east-1.amazonaws.com/us-east-1_AbCdEfGhI/.well-known/jwks.json"
)

def validate(bearer: str) -> dict:
    key = JWKS.get_signing_key_from_jwt(bearer).key
    claims = jwt.decode(
        bearer,
        key,
        algorithms=["RS256"],
        issuer="https://cognito-idp.us-east-1.amazonaws.com/us-east-1_AbCdEfGhI",
        options={"verify_aud": False},   # access tokens carry client_id, not aud
    )
    assert claims["token_use"] == "access"           # reject ID tokens outright
    assert claims["client_id"] == "7a1b2c3d4e5f6g7h8i9j0k1l2m"
    assert "api.example.com/orders.read" in claims["scope"].split()
    return claims
```

If the API is behind **API Gateway (HTTP API)**, you skip all that and declare a JWT authorizer instead:

```yaml
Authorizer:
  IdentitySource: "$request.header.Authorization"
  JwtConfiguration:
    Issuer: https://cognito-idp.us-east-1.amazonaws.com/us-east-1_AbCdEfGhI
    Audience:
      - 7a1b2c3d4e5f6g7h8i9j0k1l2m
Route:
  AuthorizationScopes:
    - api.example.com/orders.read
```

Those custom scopes like `api.example.com/orders.read` come from defining a **resource server** in the Cognito user pool and granting the scope to the app client. Without that, your access token's `scope` is just `openid email` and there's nothing meaningful to authorize against.

---

## Things worth knowing before you build this

**Token refresh is automatic and invisible.** When the Cognito access token nears expiry, the ALB uses the stored refresh token to get a new one without redirecting the browser. Your app just keeps seeing valid headers. This is controlled by `SessionTimeout` on the ALB action (default 7 days, max 7 days).

**Logout is three-legged and easy to get wrong.** Clearing the ALB cookie only ends the ALB session. Jane still has a live Cognito session and a live Entra session, so the next login is silent SSO and looks like logout failed. A full sign-out means: expire `AWSELBAuthSessionCookie-*`, then redirect to Cognito's `/logout?client_id=...&logout_uri=...`, and if you need it, on to Entra's `/oauth2/v2.0/logout`.

**Cookie size is a real constraint.** If you map lots of Entra claims (especially group memberships) into Cognito attributes, the ALB session cookie grows and shards across more cookies. Some proxies and older browsers choke past a handful. Prefer storing an Entra group ID list server-side keyed by `sub`, or use Cognito groups instead.

**`sub` values are not interchangeable.** Entra `sub` (pairwise, per-app), Entra `oid` (tenant-wide user ID), and Cognito `sub` (pool-local UUID) are three different identifiers for Jane. Your database should key on Cognito `sub`, and reach Entra's `oid` through the `identities[0].userId` claim when you need to call Microsoft Graph.

**Everything must be HTTPS.** ALB authentication actions are only available on HTTPS listeners, and every `redirect_uri` in the chain must exactly match what's registered — including trailing slashes.

----
