#WebHook Security
The key thing to internalize first: your webhook endpoint is a public URL, so *anyone* on the internet can send a POST to it. You cannot trust that a request is from the provider just because it arrived, looks well-formed, or claims to be. The source IP can be forged, and the payload can be fabricated. So authenticity has to come from something the attacker can't reproduce — a cryptographic proof carried *in the request itself*, tied to a secret only you and the provider share.

## The primary defense: signature verification (HMAC)

This is what nearly every major provider uses. When you register the webhook, the provider gives you a signing secret. On every delivery, the provider computes an HMAC of the request body using that secret and puts the result in a header (Stripe calls it `Stripe-Signature`, GitHub uses `X-Hub-Signature-256`, etc.). Your endpoint recomputes the same HMAC over the body you received and checks that it matches. An attacker who doesn't have the secret can send a body, but can't produce a matching signature — so the check fails.

Three details make or break this, and they're the ones people get wrong:

Sign the **raw bytes** of the body, exactly as received — not a re-serialized version. Many frameworks auto-parse JSON for you, and if you re-encode that parsed object to recompute the signature, the bytes shift (key order, whitespace) and every signature mismatches. Grab the raw body before anything touches it.

Use a **constant-time comparison** (`hmac.compare_digest` in Python), never `==`. A normal string comparison returns faster when it fails early, which leaks information an attacker can use to guess the signature byte by byte. Constant-time comparison closes that timing side channel.

And **reject anything without a valid signature** — missing header, wrong length, no match all mean 401. Fail closed.

## Replay protection

A valid signed request that an attacker captured (say, from a leaked log) could be re-sent later. To stop that, providers include a **timestamp in the signed data** and you reject deliveries outside a tolerance window (a few minutes). Since the timestamp is part of what's signed, an attacker can't just update it without breaking the signature. The idempotency tracking from earlier doubles as a second layer here: if you remember event IDs you've already processed, a replayed event gets dropped even if it's within the window.

Here's the hardened version of the earlier receiver — signature plus replay check:

```python
import hmac, hashlib, time
from flask import request, abort

SECRET = b"whsec_..."          # loaded from a secret manager, never hard-coded
TOLERANCE = 300                # seconds

def verify(req):
    raw = req.get_data()                       # raw bytes, BEFORE any parsing
    header = req.headers.get("X-Signature", "")
    parts = dict(p.split("=", 1) for p in header.split(",") if "=" in p)
    timestamp, sig = parts.get("t", ""), parts.get("v1", "")

    # 1. reject stale/replayed deliveries
    if not timestamp or abs(time.time() - int(timestamp)) > TOLERANCE:
        abort(401)

    # 2. recompute HMAC over "timestamp.body" and compare in constant time
    signed = f"{timestamp}.".encode() + raw
    expected = hmac.new(SECRET, signed, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, sig):
        abort(401)
```

## Transport and secret handling

Serve the endpoint over **HTTPS only** — TLS keeps the body and signature from being read or tampered with in transit, and prevents an eavesdropper from capturing a valid signature to replay. Keep the signing secret in an environment variable or secret manager, not in code or version control. And design for **rotation**: when you rotate the secret, accept both the old and new one for a short overlap window so in-flight deliveries signed with the old secret still verify, then retire the old one.

## Stronger and complementary options

HMAC uses a shared secret, which means both sides hold the same key. Some providers instead use **asymmetric signatures** — they sign with a private key and publish a public key you verify against (Ed25519 or RSA, sometimes as a JWT). The advantage is there's no shared secret on your side to leak; you only ever hold the public key.

Beyond signatures, a few network-level controls act as defense in depth, not replacements: **mTLS**, where the provider presents a client certificate you validate, and **IP allowlisting** against the provider's published ranges. Treat IP allowlisting as a supplement only — IPs change and can be spoofed in some setups, so it should never be your sole check.

Finally, the strongest architectural move ties back to the thin-payload pattern from before: **treat the webhook body as an untrusted hint, not as truth.** If your handler responds to "order 123 changed" by calling the provider's authenticated REST API to fetch the real state, then even a forged notification that somehow slipped through can't inject false data — the worst it does is make you ask the real API a question. Verifying the signature stops spoofing at the door; re-fetching from the authenticated API means a spoof can't do damage even if it gets in.

---
## Walkthrough Security Example:
This is where seeing the raw HTTP makes it click. One thing to flag up front, because it trips people up: there are **two different secrets** doing two different jobs in opposite directions. Your **API key** authenticates *you → provider* (when you register, and later when you fetch). The **signing secret** authenticates *provider → you* (on each delivery). Watch which one appears in each step.

Let me compute a real signature so the numbers actually match across the steps.All the values below are internally consistent — the signature in step 3 really is the HMAC of the step-3 body with the secret from step 1.

## Step 1 — You register the webhook (you → provider)

Here you authenticate with **your API key**. You tell the provider which URL to call and hand over a secret you generate (or, with many providers, they generate and return it).

```http
POST /v1/webhook_endpoints HTTP/1.1
Host: api.provider.com
Authorization: Bearer sk_live_YOURAPIKEY        ← your API key (you → provider)
Content-Type: application/json

{
  "url": "https://myapp.com/webhooks/payments",
  "events": ["payment.succeeded"]
}
```

Response — the provider confirms and returns the **signing secret**. This is the key used to prove future deliveries are real. It's typically shown only once, so you store it immediately (secret manager, not code).

```http
HTTP/1.1 201 Created
Content-Type: application/json

{
  "id": "we_9f2b",
  "url": "https://myapp.com/webhooks/payments",
  "events": ["payment.succeeded"],
  "signing_secret": "whsec_5f8a2c1e9b4d7a6f3e2d1c0b9a8f7e6d"
}
```

At this point two keys exist: `sk_live_...` (yours, for calling them) and `whsec_...` (for verifying their calls to you).

## Step 2 — An event occurs

Something happens on the provider's side — a customer's payment clears. You don't make a call here; this is just the trigger. The provider creates an event object (`evt_28a7c9`) and looks up which registered URLs care about `payment.succeeded`.

## Step 3 — The provider calls your webhook (provider → you)

The provider computes `HMAC_SHA256(signing_secret, "<timestamp>.<raw_body>")` and puts the timestamp and result in a header, then POSTs to your URL. This is the one moment the signing secret is used on the wire — indirectly, as a signature, never sent in the request.

```http
POST /webhooks/payments HTTP/1.1
Host: myapp.com
Content-Type: application/json
X-Signature: t=1700000000,v1=e3aed392ea929f8674526218b7e7c1233c592a388f332e0df465927cedda869e

{"id":"evt_28a7c9","type":"payment.succeeded","data":{"order_id":"ord_123","amount":"$9.99"}}
```

The `t=` is the timestamp (for replay protection) and `v1=` is the signature. Both are part of what was signed, so neither can be altered without breaking the match.

## Step 4 — You verify, then respond (your endpoint)

Your handler recomputes the HMAC over `t` + `.` + the exact raw body, using the stored secret, and compares it constant-time to `v1`. With the values above, your recomputation produces the identical `e3aed392...`, so it matches — the request is authentic.

```python
raw = request.get_data()                            # exact bytes received
t, v1 = parse("X-Signature")                         # "1700000000", "e3aed392..."
signed = t.encode() + b"." + raw
expected = hmac.new(SECRET, signed, hashlib.sha256).hexdigest()

if abs(time.time() - int(t)) > 300:  abort(401)      # reject if stale (replay)
if not hmac.compare_digest(expected, v1):  abort(401) # reject if signature wrong
# expected == v1  →  authentic
```

You return a 2xx to acknowledge. That tells the provider "received" so it won't retry.

```http
HTTP/1.1 200 OK
```

A spoofer who POSTs to `https://myapp.com/webhooks/payments` without `whsec_...` cannot produce a matching `v1`, so their request dies at the `compare_digest` check with a 401. If they replay a genuine captured request, the stale-timestamp check (or your record of already-seen `evt_28a7c9`) drops it.

## Step 5 — (optional) You fetch the real state (you → provider)

Because the delivery was thin, your verified handler often calls back to confirm the full details — and here you're using **your API key** again, not the signing secret.

```http
GET /v1/orders/ord_123 HTTP/1.1
Host: api.provider.com
Authorization: Bearer sk_live_YOURAPIKEY        ← your API key again
```

```http
HTTP/1.1 200 OK
Content-Type: application/json

{"id":"ord_123","status":"paid","amount":"$9.99","customer":"Ada"}
```

So across the whole lifecycle: your API key goes out in steps 1 and 5 (you calling them), and the signing secret guards step 3 (them calling you) — verified in step 4 without ever transmitting the secret itself.
