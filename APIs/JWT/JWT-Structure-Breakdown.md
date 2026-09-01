# JWT Structure Breakdown
Here's the full breakdown, part by part, in the order they're actually built and processed.
<img width="1474" height="440" alt="image" src="https://github.com/user-attachments/assets/3547ca96-d48e-4272-9213-16ce978f04a1" />


## 1. Header — *how* the token was signed

The header is metadata about the token itself, not about the user. It tells the verifier what cryptographic method to expect before it even looks at the payload.

```json
{
  "alg": "RS256",
  "typ": "JWT"
}
```

- **`alg`** — the signing algorithm. Two common choices:
  - `RS256` — RSA + SHA-256, *asymmetric*. The issuer signs with a private key; anyone can verify with the corresponding public key. This is what Entra ID and most OIDC providers use, since it lets any API verify tokens without ever holding a secret.
  - `HS256` — HMAC + SHA-256, *symmetric*. Both sides must share the same secret. Simpler, but only safe when signer and verifier are the same trusted party (or share a secret out of band).
- **`typ`** — the token type, almost always the literal string `"JWT"`. Mostly there for tooling/parsers to recognize the format.

This JSON gets base64url-encoded to become the **first** segment of the token.

## 2. Payload — *who* and *what*

This is where claims actually live — statements about the subject (the user) and about the token's own scope of validity.

```json
{
  "iss": "https://login.microsoftonline.com/{tenant}/v2.0",
  "sub": "AAAAAAAAAAAAAAAAAAAAAIkzqFVrSaSaFHy782bbtaQ",
  "aud": "6731de76-14a6-49ae-97bc-6eba6914391e",
  "exp": 1690000000,
  "iat": 1689996400,
  "jti": "b4d1e2-9f0a",
  "email": "alex@example.com",
  "name": "Alex Rivera",
  "roles": ["editor", "billing_admin"]
}
```

**Registered claims** (standardized, so any system reading the token knows what they mean):

- **`iss`** (issuer) — who created and signed this token. Lets the verifier confirm the token came from a trusted authority, not somewhere spoofed.
- **`sub`** (subject) — a unique, stable ID for the token's subject. Used as the real primary key for the user, since things like email can change but this generally doesn't.
- **`aud`** (audience) — who the token is meant for. Stops a token issued for one app from being replayed against a different app's API — the API checks that `aud` matches its own identifier.
- **`exp`** (expiration) — timestamp after which the token is dead. Bounds the damage if a token leaks; this is why access tokens are usually short-lived.
- **`iat`** (issued at) — when the token was created. Useful for freshness checks and auditing.
- **`nbf`** (not before) — the token isn't valid until this time. Less common, but useful for pre-issued tokens meant to activate later.
- **`jti`** (JWT ID) — a unique ID for this specific token instance. Lets a server maintain a revocation/replay list.

**OIDC identity claims** (from the ID token specifically):

- **`email`, `name`, `given_name`, `picture`** — describe *who the user is*, so the app doesn't need a separate profile lookup just to greet them.

**Private/custom claims** (app-specific, not standardized):

- **`roles` / `permissions`** — describe *what the user is allowed to do*. This is what a backend actually checks for authorization decisions.

This JSON gets base64url-encoded into the **second** segment.

## 3. Signature — proof the first two haven't been touched

Unlike the header and payload, the signature isn't a JSON object with keys — it's a single cryptographic value.

It's computed roughly as:

```
signature = Sign(
  base64url(header) + "." + base64url(payload),
  private_key_or_secret
)
```

- For `HS256`, that's an HMAC using a shared secret.
- For `RS256`, that's an RSA signature using the issuer's private key.

The receiving server verifies by recomputing the same signature over the received header+payload (using the issuer's *public* key, typically fetched from a `/.well-known/jwks.json` endpoint) and checking it matches. If a single character in the header or payload changed after signing, the signature won't match, and the token is rejected.

## How it all comes together

The three base64url segments get joined with dots:

```
base64url(header) . base64url(payload) . base64url(signature)
```

The logical flow is: **header decides how** to verify → **payload carries who and what** → **signature proves the first two are genuine and untampered**. Anyone can decode and read the header and payload (they're not encrypted) — the signature is the only thing standing between "readable" and "trustworthy."

---
# More Complex Examples
---
The header and (especially) the payload can get considerably more complex than the minimal examples. The signature is the one part that stays structurally simple within JWS, but there's a related case where the *whole token* changes shape. Walking through each:

## Header — gets more complex with key rotation

The base example had just `alg` and `typ`. In practice, issuers like Entra ID rotate their signing keys periodically and publish several valid public keys at once (via a JWKS endpoint). The header needs to say *which* key was used:

```json
{
  "typ": "JWT",
  "alg": "RS256",
  "kid": "nOo3ZDrODXEK1jKWhXslHR_KXEg",
  "x5t": "nOo3ZDrODXEK1jKWhXslHR_KXEg"
}
```

- **`kid`** (Key ID) — points the verifier at the exact key in the issuer's published key set, instead of forcing it to try every published key until one works.
- **`x5t`** — an x.509 certificate thumbprint, an alternate way of identifying the signing key when certificates (not just raw keys) are involved.
- **`typ`** can also get more specific: RFC 9068 defines `at+jwt` as the type for OAuth access tokens specifically, so an API that might receive either an ID token or an access token can tell which one it's looking at before even parsing the payload.

## Payload — this is where real complexity lives

The base example was a clean, flat object. Real Entra ID tokens carry a lot more, and some claims aren't flat at all.

**A closer-to-real Entra ID ID token:**

```json
{
  "ver": "2.0",
  "iss": "https://login.microsoftonline.com/{tenant}/v2.0",
  "sub": "AAAAAAAAAAAAAAAAAAAAAIkzqFVrSaSaFHy782bbtaQ",
  "aud": "6731de76-14a6-49ae-97bc-6eba6914391e",
  "exp": 1690000000,
  "iat": 1689996400,
  "tid": "9188040d-6c67-4c5b-b112-36a304b66dad",
  "oid": "00000000-0000-0000-66f3-3332eca7ea81",
  "preferred_username": "alex@example.com",
  "nonce": "defaultNonce",
  "at_hash": "H1_37dSl7B7JBUCoTeYQ7g",
  "amr": ["pwd", "mfa"],
  "azp": "6731de76-14a6-49ae-97bc-6eba6914391e"
}
```

New pieces and why they exist:

- **`tid`** — tenant ID. In a multi-tenant app, you need to know *which* organization's directory actually issued this token before trusting anything else in it.
- **`oid`** — the immutable object ID of the user in the directory. More stable across apps than `sub`, which can be app-specific (pairwise).
- **`nonce`** — echoes back a random value your app sent in the original sign-in request. Confirms this ID token was issued in response to *your* specific request, not replayed from somewhere else.
- **`at_hash`** — a hash of the access token issued alongside this ID token. Lets your app cryptographically confirm the two tokens actually belong together, rather than one being swapped in.
- **`amr`** (authentication methods references) — an array describing *how* the user proved their identity, e.g. `["pwd", "mfa"]`. Useful if parts of your app require step-up authentication.
- **`azp`** — which client ID the token was issued to, relevant when it could differ from `aud`.

**The clearest example of a claim genuinely changing shape: group overage.** If a user belongs to more groups than fit safely in a token (Entra ID's threshold is 200), the `groups` claim isn't just truncated — it's replaced entirely:

```json
{
  "_claim_names": { "groups": "src1" },
  "_claim_sources": {
    "src1": { "endpoint": "https://graph.microsoft.com/v1.0/users/{oid}/getMemberObjects" }
  }
}
```

Instead of an inline array, you get a pointer telling your app to go fetch the group list from a separate Graph API call. This is a real structural fork, not just added verbosity — code that expects `groups` to always be an array will break for users in large orgs unless it also handles this overage case.

**Nested object claims** also exist in the OIDC spec itself — `address` isn't a string, it's an object:

```json
"address": {
  "street_address": "123 Main St",
  "locality": "Springfield",
  "region": "IL",
  "postal_code": "62704",
  "country": "US"
}
```

**Access tokens carry a different claim set than ID tokens** — worth knowing since it's easy to conflate them:

```json
{
  "scp": "User.Read Mail.Read",
  "roles": ["Admin.Write"],
  "appid": "6731de76-14a6-49ae-97bc-6eba6914391e"
}
```

- **`scp`** — space-separated delegated permissions, used when the app acts *on behalf of* a signed-in user.
- **`roles`** — application permissions, used when the app acts as itself (service-to-service, no user present). Note this is Microsoft's standardized meaning of `roles`; if your own backend adds a custom `roles` claim for its own authorization logic, that's a different, app-defined thing with the same name — worth namespacing to avoid confusion, e.g. `"https://myapp.example.com/roles": [...]`.

## Signature — stays simple, but the whole token can change shape around it

Within JWS (a signed JWT — everything above), the signature is always just one opaque base64url value, regardless of algorithm. It doesn't grow more complex the way the payload does.

But there's a related case worth knowing: if the token needs to be *encrypted*, not just signed — so that even an intermediary holding the token can't read certain claims — you're no longer dealing with JWS at all, you're dealing with **JWE**, and the token structure itself expands to five segments instead of three:

```
header.encrypted_key.iv.ciphertext.auth_tag
```

This shows up in "nested JWT" patterns, where a signed JWT (JWS) is itself encrypted and wrapped inside a JWE — common when an ID token passes through a frontend that shouldn't be able to read sensitive claims inside it, only forward the opaque encrypted blob along.
