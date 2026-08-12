# JWT Overview
Signing a JWT is a cryptographic operation, not just encoding — that's the part that actually makes it trustworthy. Let's break down issuing first, then verifying, then why the math behind it can't practically be forged.

**Issuing (signing) a token**The signing step is where the actual cryptography happens: the server runs the concatenated `header.payload` string through a signing algorithm (commonly HMAC-SHA256, or RSA/ECDSA for asymmetric setups) using a key only the server knows. The output is the signature — a fixed-length value that's practically impossible to reproduce without that exact key and that exact input.
<img width="1440" height="1080" alt="image" src="https://github.com/user-attachments/assets/a03188d1-feeb-4b75-a45f-8dfdec3137a3" />

**Verifying a token on a later request****Why this is actually secure**
<img width="1440" height="1060" alt="image" src="https://github.com/user-attachments/assets/0bb07914-1371-4014-b04b-b03aaaf7a815" />


The security rests on a property cryptographers call a **one-way function with a secret**: given the header, payload, and signature, it's computationally infeasible to work backward and figure out the key — even though verifying is trivial if you *have* the key.

- **HMAC (symmetric, e.g. HS256):** The signature is a keyed hash of the data. Without the secret, an attacker can change the payload all they want, but they can't produce a matching signature — brute-forcing a 256-bit key is astronomically out of reach with current computing power. The catch: every server that verifies tokens needs the same secret, so it has to be tightly controlled and never exposed to clients.
- **RSA/ECDSA (asymmetric, e.g. RS256, ES256):** Only the private key can *create* a valid signature; the public key can *verify* it but can't forge one. This is why asymmetric signing is preferred when many services need to check tokens — you can hand out the public key freely (even publish it) without giving anyone the ability to mint fake tokens.
- **Tamper-evidence, not confidentiality:** the payload is still just base64-encoded, readable by anyone. The signature doesn't hide data — it guarantees that if even a single byte of the header or payload changes after signing, the recomputed signature won't match and the server rejects it outright.
- **The whole system leans on key secrecy.** If a signing secret or private key ever leaks, an attacker can mint arbitrary valid tokens — impersonating any user, with any role, indefinitely (or until you rotate the key and invalidate everything signed with it). This is why weak secrets, hardcoded keys in source code, or committing keys to a repo are common real-world JWT breaches, not flaws in the algorithm itself.
- **Algorithm pinning matters.** A well-known attack tricks a lax verifier into trusting the `alg` field from the token itself — e.g., switching from RS256 to `none`, or from RSA to HMAC using the public key as the HMAC secret. Solid libraries hardcode the expected algorithm on the server side rather than trusting whatever the token claims.

So the strength of a JWT isn't in obscurity or encoding — it's standard applied cryptography: a secret (or private key) that's expensive to guess, and a signature that's expensive to forge without it.

### JWKS
The `kid` (key ID) field in the JWT's header tells you exactly which public key to use — you don't have to guess or try them all.A couple of things worth calling out on top of that walkthrough:

- **Never trust the `alg` field from the token itself to decide how to verify.** Pin your verifier to expect RS256 explicitly (that's what Cognito uses). If the header claims a different algorithm — like `none`, or HS256 using the public key as an HMAC secret — reject it outright. This is the algorithm-confusion attack we touched on earlier.
- **A malformed or unknown `kid` is not automatically an attack** — it's usually just a sign Cognito rotated its keys since your last fetch. The right response is to refresh your JWKS cache and try again once, not to assume something malicious.
- **In practice, you almost never write this from scratch.** AWS's own `aws-jwt-verify` library (or well-maintained equivalents in your language) handles the fetch-cache-match-verify dance for you — decoding, `kid` matching, caching, and claim checks all in one call. Hand-rolling JWT verification is one of the more common sources of real-world auth bugs, so leaning on a maintained library is the safer default.

## When JWTs need to be Verified
Yes, in the standard pattern — every request that needs authentication gets its JWT checked, independently, on every call. That's actually the entire point of using JWTs in the first place: statelessness. The server doesn't remember who you are between requests, so each request has to prove it on its own.

A few nuances worth knowing:

**It's usually not written per-endpoint by hand.** 
Almost every framework lets you put verification in a middleware/interceptor layer that runs before the request reaches your route handlers — so you write the check once, and it applies to every protected route automatically. Public endpoints (login, health checks, public docs) are explicitly excluded from that middleware.

**It can happen before it even reaches your app.** 
Many architectures verify the JWT at the edge — an API gateway, a load balancer, or a reverse proxy (like Envoy, Kong, or AWS API Gateway with a Lambda authorizer) checks the signature and claims, and only forwards the request to your backend if it's valid. Your application code might never touch raw verification logic at all.

**Verification is cheap.** 
Checking an HMAC or RSA/ECDSA signature is a fast, local, CPU-only operation — no database round trip, no network call. That's what makes doing it on every request practical at scale, unlike traditional session lookups that hit a session store each time.

**What you don't have to redo per request:** 
re-checking whether the *user* still exists, is still active, or hasn't been banned — that's only guaranteed as of when the token was issued. If you need real-time revocation (immediate logout, banning a user mid-session), you need something extra on top of pure JWT verification, like:

- A short token lifespan (a few minutes) plus frequent refresh, so stale permissions self-correct quickly.
- A blocklist/deny-list of revoked token IDs (`jti` claim) checked against a fast store like Redis — this reintroduces some statefulness but only for revocation, not for full session lookup.
- A "token version" or `iat` (issued-at) claim compared against a "valid since" timestamp stored per user, so changing that timestamp invalidates all previously issued tokens at once.

So: signature and expiry checks happen on essentially every call, but they don't have to mean a database hit every call — that's the tradeoff that makes JWTs attractive for high-traffic APIs in the first place.

---
# How the Algorithms Secure the System
The short answer: the two keys aren't independent secrets — they're mathematically linked by a **trapdoor function**, a calculation that's easy to do in one direction but computationally infeasible to reverse without extra information only the private key holder has.The two algorithms build that trapdoor differently, but the underlying idea is the same: sign and verify are algebraically related operations, while going from public key back to private key requires solving a math problem believed to take an infeasible amount of time.
<img width="1440" height="860" alt="image" src="https://github.com/user-attachments/assets/6937f97d-97a4-46ba-a71d-068c07a0562c" />

**RSA — built on the difficulty of factoring**

RSA keys are generated from two huge random prime numbers, `p` and `q`, which are multiplied together to get a modulus `n = p × q`. From `n` and its factors, you derive a public exponent `e` and a private exponent `d` that are mathematical inverses of each other *with respect to n* — meaning if you raise a number to the power `d` and then to the power `e` (both mod `n`), you get back the original number.

- **Signing:** the server computes `signature = hash(message)^d mod n` using the private exponent.
- **Verifying:** anyone computes `hash(message)^e mod n` using the public exponent and checks it matches.

The reason someone can't just compute `d` from the public `(e, n)` is that doing so requires knowing `p` and `q` — and factoring a 2048-bit `n` back into its two prime factors is a problem with no known efficient algorithm. It's not mathematically impossible, just impractical: current best methods would take longer than the age of the universe on realistic hardware for well-chosen key sizes.

**ECDSA — built on the difficulty of the discrete log problem on elliptic curves**

ECDSA works differently but has the same shape. You pick a random private key `d` (just a large integer), and the public key is a point on an elliptic curve computed as `Q = d × G`, where `G` is a fixed, publicly known starting point on the curve and `×` means "add G to itself d times" using the curve's special addition rules.

- Going from `d` to `Q` (private → public) is fast.
- Going from `Q` back to `d` (public → private) means solving the **elliptic curve discrete logarithm problem** — essentially, "how many times was G added to itself to land on Q?" — which has no efficient known solution for well-chosen curves.

Signing uses `d` plus a random nonce to produce a pair of numbers `(r, s)`. Verifying uses `Q`, `r`, `s`, and the public curve parameters to check an equation holds — an equation that only comes out true if the signature really was produced using the matching private key. ECDSA keys are much shorter than RSA keys for equivalent security (256-bit ECDSA ≈ 3072-bit RSA), which is why it's popular for mobile and IoT contexts.

**The common thread:** in both cases, the public key doesn't "contain" the private key in any extractable sense — it's the output of a one-way trapdoor calculation. Verification only needs to check that a specific mathematical relationship holds; it never needs to know or reconstruct the secret that produced it.
