"""Webhook example — the provider calls YOUR endpoint when an event happens.

Two roles:
  - provider (the service, e.g. Stripe): sends an HTTP POST on each event
  - consumer (you): expose an endpoint the provider is registered to call

    pip install flask requests
    python webhook.py           # run the receiver (your endpoint)
    python webhook.py send      # simulate the provider firing one event

You register the URL once; it then fires every time a matching event occurs.
"""
import sys
import json
import hmac
import hashlib
import requests
from flask import Flask, request, abort

SECRET = b"shared-secret-key"        # both sides know this

# ---- consumer side: the endpoint you expose ----
app = Flask(__name__)
seen_events = set()                   # remembered so we can ignore duplicates


@app.post("/webhooks/payments")
def handle_webhook():
    body = request.get_data()

    # 1. Verify it really came from the provider (not a random POST).
    expected = hmac.new(SECRET, body, hashlib.sha256).hexdigest()
    signature = request.headers.get("X-Signature", "")
    if not hmac.compare_digest(expected, signature):
        abort(401)

    event = request.get_json()

    # 2. Idempotency: providers retry, so the same event can arrive twice.
    if event["id"] in seen_events:
        return "", 200
    seen_events.add(event["id"])

    # 3. Do the real work.
    print(f"Payment of {event['amount']} received from {event['customer']}")
    return "", 200        # a 2xx tells the provider "got it, stop retrying"


# ---- provider side: simulate the service firing an event ----
def send_test_event():
    event = {"id": "evt_123", "customer": "Ada", "amount": "$9.99"}
    body = json.dumps(event).encode()
    signature = hmac.new(SECRET, body, hashlib.sha256).hexdigest()
    requests.post(
        "http://localhost:5000/webhooks/payments",
        data=body,
        headers={"Content-Type": "application/json", "X-Signature": signature},
    )
    print("event sent")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "send":
        send_test_event()
    else:
        app.run(port=5000)
