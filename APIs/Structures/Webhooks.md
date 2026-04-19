# Webhooks
A **webhook** is a way for one application to automatically notify another when something happens — instead of constantly asking "did anything change?", the app just gets a message the moment it does.

Think of the difference between calling a restaurant every 10 minutes to ask "is my table ready?" vs. giving them your phone number so they call *you* when it's ready. That's polling vs. webhooks.Here's how webhooks work step by step:
<img width="1440" height="1102" alt="image" src="https://github.com/user-attachments/assets/604f0367-105f-41e3-8446-2e19ef266c3a" />

1. **Registration** — Your app tells the external service "when something happens, send it to this URL." That URL is your webhook endpoint.
2. **Event occurs** — A payment goes through, a file finishes processing, a form is submitted — whatever the service monitors.
3. **HTTP POST sent** — The service immediately sends a POST request to your URL with a JSON payload describing the event.
4. **Your app handles it** — You receive the data and do something: send a confirmation email, update a database, trigger a workflow. Then respond with `200 OK` to acknowledge receipt.

The key benefit over polling is **immediacy and efficiency** — you only do work when something actually happens, and you find out instantly rather than on the next check cycle.

### How your App handles Step 3
When Stripe (or any service) fires off an HTTP POST to your `/webhook` URL, Flask catches it and automatically calls your `webhook()` function. You never call that function yourself — it just sits there waiting.

The flow is:

```
Stripe sends POST → hits your /webhook URL → Flask routes it → webhook() runs
```

This is why it's called "event-driven" — your code is idle until something on the other side triggers it. Flask's `@app.route("/webhook", methods=["POST"])` decorator is what wires the URL to the function. So your API server acts as the single entry point, then routes the event internally to wherever it needs to go. For example:

```
Stripe POST → /webhook → your API server → route to correct user/service
```

What happens after routing depends on your architecture:

- **Simple app** — just update the database and maybe trigger a function directly
- **Microservices** — forward the event to the relevant internal service (e.g. an orders service, a notifications service)
- **Queue-based** — push the event onto a message queue (e.g. RabbitMQ, SQS) and let workers pick it up asynchronously

The key responsibility of your webhook endpoint is really just three things:

1. **Verify** the signature
2. **Acknowledge** with a 200 OK immediately
3. **Hand off** the work elsewhere — don't do heavy processing inside the webhook handler itself, because if it times out the service will think delivery failed and retry

That last point is important — your webhook function should be as thin as possible. Receive, verify, enqueue, respond. The actual business logic lives downstream.

---
# Simple Example:
To run it, install Flask and start the server:

```bash
pip install flask
python webhook_example.py
```

Your webhook endpoint will be listening at `http://localhost:5000/webhook`.

A few things worth noting about the code:

**Signature verification** is the most important security step. The sending service includes an `X-Signature-256` header — a hash of the payload signed with a shared secret. You verify it before trusting any data. Skipping this means anyone could send fake events to your endpoint.

**Always return 200 OK** promptly, even if your processing fails. Most services will retry the webhook if they don't get a 200, which can cause duplicate processing. A common pattern is to acknowledge immediately, then do heavier work in a background job.

**Expose your local server** for testing with a tool like [ngrok](https://ngrok.com), which gives you a public URL that tunnels to your machine:

```bash
ngrok http 5000
# Gives you something like: https://abc123.ngrok.io/webhook
```

Paste that URL into whatever service you're integrating with (Stripe, GitHub, etc.) as your webhook endpoint.
```python
from flask import Flask, request, jsonify
import hmac
import hashlib

app = Flask(__name__)

WEBHOOK_SECRET = "your_secret_key"  # Shared secret from the service sending events


def verify_signature(payload: bytes, signature: str) -> bool:
    """Verify the webhook came from a trusted source."""
    expected = hmac.new(WEBHOOK_SECRET.encode(), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(f"sha256={expected}", signature)


@app.route("/webhook", methods=["POST"])
def webhook():
    # 1. Verify the signature (important for security)
    signature = request.headers.get("X-Signature-256", "")
    if not verify_signature(request.data, signature):
        return jsonify({"error": "Invalid signature"}), 401

    # 2. Parse the JSON payload
    payload = request.json
    event_type = payload.get("event")

    # 3. Handle different event types
    if event_type == "payment.succeeded":
        amount = payload.get("amount")
        customer = payload.get("customer")
        print(f"Payment of ${amount / 100:.2f} received from {customer}")

    elif event_type == "payment.failed":
        customer = payload.get("customer")
        print(f"Payment failed for customer {customer}")

    else:
        print(f"Unhandled event type: {event_type}")

    # 4. Always return 200 OK to acknowledge receipt
    return jsonify({"status": "received"}), 200


if __name__ == "__main__":
    app.run(port=5000)
```

---
## Managing the URLs / Internal Traffic
No, you don't have to vary the URL per user — that's one option, but it's usually not the best one. There are a few common patterns:

---

**Option 1: Embed user ID in the URL (simplest)**
```
POST /webhook/user/42
```
```python
@app.route("/webhook/user/<int:user_id>", methods=["POST"])
def webhook(user_id):
    user = db.get_user(user_id)
    # process for this specific user
```
Easy to set up, but exposes your internal IDs in a public URL, and some services only allow one webhook URL.

---

**Option 2: Payload contains the user ID (most common)**

Most services include account/customer identifiers in the payload itself. You look up which user that maps to in your own database.

```python
@app.route("/webhook", methods=["POST"])
def webhook():
    payload = request.json

    # e.g. Stripe sends a customer ID, you map it to your user
    stripe_customer_id = payload["customer"]
    user = db.query("SELECT * FROM users WHERE stripe_customer_id = ?", stripe_customer_id)

    # now process for that specific user
```
This is how Stripe, GitHub, and most major services work — one URL for all events, you route internally.

---

**Option 3: Unique token per user in the URL (secure + flexible)**

Generate a secret token when a user connects an integration, store it, and use it to route:

```
POST /webhook/abc9f3e1  ← unique token for user 42
POST /webhook/7dc4a201  ← unique token for user 91
```

```python
@app.route("/webhook/<token>", methods=["POST"])
def webhook(token):
    user = db.query("SELECT * FROM users WHERE webhook_token = ?", token)
    if not user:
        return jsonify({"error": "Unknown token"}), 404

    # process for this user
```

This is useful when the payload doesn't contain any user-identifying info, and it's the approach tools like Zapier use.

---

**Which to use?**

| Situation | Best approach |
|---|---|
| The payload includes a customer/account ID | Option 2 — look it up in your DB |
| You control both sides of the integration | Option 1 or 3 |
| Third-party service, no user ID in payload | Option 3 — token in the URL |
| One webhook URL allowed by the service | Option 2 or 3 |

In practice, **Option 2 is the most common** because services like Stripe, GitHub, and Twilio always include their own account identifiers in the payload. You just need a mapping table (`stripe_customer_id → your user`) set up at the time the user connects their account.
