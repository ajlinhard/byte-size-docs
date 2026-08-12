# JWT Common Vocabulary

Here are some common terms you will hear about when talking about JWTs. Right below is very high level helpful context, then we will explain concepts in more detail.
- **Claims** is the parent category — **`aud`** and **`nonce`** are specific claims
- **JWKS** is how you verify the token carrying those claims
- **Bearer token** is how the token travels
- **JIT** is unrelated to token mechanics — it's about user records

A note on one: it's **nonce** (number used once), not "nounce" — common typo, worth knowing since you'll grep for it in logs.

---

## JIT (Just-In-Time provisioning)

Creating the local user record at the moment of first login, rather than pre-syncing a directory.

**Purpose:** you don't run SCIM, nightly LDAP syncs, or a CSV import to keep Cognito's user list matching Entra's. Alice exists in Entra; the first time she authenticates, Cognito creates her. Deprovisioning is the flip side and the catch — revoking her in Entra stops new logins, but the Cognito record lingers.

In your flow this happens at step 6, when Cognito redeems Entra's code:

```json
// Entra's id_token arrives with:
{
  "oid": "9a8b7c6d-1122-3344-5566-778899aabbcc",
  "email": "alice@contoso.com",
  "name": "Alice Chen"
}
```

```
// Cognito applies attribute_mapping and creates, on the spot:
Username:  EntraID_9a8b7c6d-1122-3344-5566-778899aabbcc
email:     alice@contoso.com
name:      Alice Chen
identities: [{ providerName: "EntraID", providerType: "OIDC" }]
```

No admin action, no pre-registration. Second login updates the same record instead of creating another.

---

## Bearer token

A credential where possession alone is authority — "whoever *bears* it may use it." No signature over the request, no proof the sender is the party it was issued to.

**Purpose:** stateless authorization. The API doesn't look up a session; it verifies the token and proceeds.

```http
GET /api/orders HTTP/1.1
Host: api.example.com
Authorization: Bearer eyJraWQiOiJhYmMxMjMiLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiI4ZjRl...
```

The security consequence is the whole reason for HTTPS-only, short `exp`, and never logging the `Authorization` header: a stolen bearer token is *fully usable by the thief* until it expires. Contrast DPoP or mTLS, where the client must additionally prove it holds a private key.

```js
// Sending one
await fetch('/api/orders', {
  headers: { Authorization: `Bearer ${accessToken}` }
});
```

```js
// Extracting one — the scheme prefix is required and case-insensitive
const token = req.header('authorization')?.match(/^Bearer (.+)$/i)?.[1];
```

---

## JWKS (JSON Web Key Set)

A JSON document of **public** keys, published at a well-known URL, that lets anyone verify an issuer's signatures.

**Purpose:** asymmetric verification without shared secrets and without calling the issuer per request. Cognito signs with a private key it never publishes; your API fetches the public half once, caches it, and verifies offline forever after.

```
GET https://cognito-idp.us-east-1.amazonaws.com/us-east-1_AbCdEf/.well-known/jwks.json
```

```json
{
  "keys": [
    {
      "kid": "abc123def456=",           // key id — matches the JWT header
      "alg": "RS256",
      "kty": "RSA",
      "use": "sig",
      "n": "0vx7agoebGcQSuuPiLJXZptN9nnd...",   // RSA modulus
      "e": "AQAB"                                // RSA exponent (65537)
    },
    { "kid": "xyz789...", "alg": "RS256", "kty": "RSA", "use": "sig", "n": "...", "e": "AQAB" }
  ]
}
```

Two keys are published so the issuer can rotate without breaking tokens signed by the outgoing key. Matching is by `kid`:

```js
const { kid } = JSON.parse(Buffer.from(token.split('.')[0], 'base64url'));
const key = jwks.keys.find(k => k.kid === kid);   // then verify signature with it
```

**Cache it.** Fetching per request adds latency and will get you rate-limited. Refresh only on an unrecognised `kid`. (Your ALB's ES256 endpoint is the odd one out — `https://public-keys.auth.elb.<region>.amazonaws.com/<kid>` returns a bare PEM, not a JWKS document.)

---

## Claims

The individual statements in a token's payload. A claim is just a key/value assertion the issuer is vouching for.

**Purpose:** carry identity and authorization facts inside the token so the API needs no database lookup to know who's calling and what they may do.

Three tiers:

| Tier | Examples | Who defines |
|---|---|---|
| Registered | `iss`, `sub`, `aud`, `exp`, `iat`, `nbf`, `jti` | RFC 7519 |
| Public | `email`, `name`, `groups` | OIDC / IANA registry |
| Private | `cognito:groups`, `custom:tenant_id` | You and your issuer |

A Cognito **access token**, decoded:

```json
{
  "sub": "8f4e1c22-1a3b-4c5d-9e0f-112233445566",  // subject — the user
  "iss": "https://cognito-idp.us-east-1.amazonaws.com/us-east-1_AbCdEf",
  "client_id": "3n4b5m6k7j8h9g0f1d2s3a",
  "token_use": "access",
  "scope": "openid email https://api.example.com/read",
  "cognito:groups": ["OrderAdmins", "Auditors"],
  "iat": 1754835600,      // issued at
  "exp": 1754839200,      // expires — Unix seconds, UTC
  "jti": "b1f0c9d8-..."   // unique token id, for revocation lists
}
```

```js
const isAdmin = claims['cognito:groups']?.includes('OrderAdmins');
const canRead = claims.scope.split(' ').includes('https://api.example.com/read');
```

Claims are only trustworthy *after* signature verification. Decoding a JWT is just base64 — anyone can write whatever they like in the payload.

---

## nonce

A random, single-use value the client generates before login and checks when the token comes back.

**Purpose:** binds an ID token to *this* specific authentication request from *this* browser. Without it, an attacker who captured an ID token issued for a different session could inject it into yours (token replay / token injection).

```js
// 1. Before redirecting, generate and stash
const nonce = crypto.randomUUID();
sessionStorage.setItem('nonce', nonce);
```

```
// 2. Send it on the authorize request
GET /oauth2/authorize?response_type=code&client_id=...&nonce=7f3a9c21-...
```

```json
// 3. The IdP embeds it in the id_token it issues
{
  "sub": "8f4e1c22-...",
  "aud": "3n4b5m6k7j8h9g0f1d2s3a",
  "nonce": "7f3a9c21-...",
  "exp": 1754839200
}
```

```js
// 4. Compare, then discard
if (claims.nonce !== sessionStorage.getItem('nonce')) throw new Error('nonce mismatch');
sessionStorage.removeItem('nonce');   // "used once" — never accept it twice
```

Don't confuse it with **`state`**, which sits next to it in the same request and looks similar:

- `state` → CSRF protection on the **redirect**, checked at the callback
- `nonce` → replay protection on the **token**, checked inside the JWT

In your architecture both are generated and validated by Cognito and by the ALB — your app code never sees them.

---

## `aud` (audience)

The registered claim naming who the token is **for**. The recipient must reject any token whose `aud` isn't itself.

**Purpose:** stops a token issued for one party being accepted by another. This single check is what prevents a *confused deputy* — service B honouring a token that service A was meant to receive.

```json
// ID token — audience is the app client that requested login
{
  "aud": "3n4b5m6k7j8h9g0f1d2s3a",
  "iss": "https://cognito-idp.us-east-1.amazonaws.com/us-east-1_AbCdEf",
  "token_use": "id",
  "email": "alice@contoso.com"
}
```

```js
jwt.verify(idToken, key, {
  audience: '3n4b5m6k7j8h9g0f1d2s3a',   // reject anything else
  issuer: `https://cognito-idp.${REGION}.amazonaws.com/${POOL_ID}`,
});
```

`aud` may also be an array (`"aud": ["api://orders", "api://billing"]`), and verification passes if your identifier appears anywhere in it.

**The Cognito quirk worth memorising:** Cognito **access tokens have no `aud` claim at all** — they carry `client_id` instead. That's why your verifier config had `audience: null` and an explicit `client_id` comparison:

```js
if (claims.token_use !== 'access') throw new Error('wrong token_use');
if (claims.client_id !== CLIENT_ID) throw new Error('wrong client');
```

This is exactly the trap from the ID-token-to-the-API mistake. The ID token's `aud` is your *frontend*. An API that accepts it is accepting a token that was never issued for it — and if `aud` isn't checked, it'll accept ID tokens minted for entirely different applications in the same pool.

---

## Where each shows up in your flow

| Term | Appears at |
|---|---|
| nonce | Steps 2–3, generated by ALB and Cognito on each authorize hop |
| JIT | Step 6, Cognito creating the federated user from Entra's claims |
| aud / claims | Step 8, inside the tokens the ALB receives from Cognito |
| Bearer token | Step 9 onward, or `x-amzn-oidc-accesstoken` in the ALB pattern |
| JWKS | Step 9, your backend verifying signatures offline |
