# WeHook vs. WebSocket vs. Endpoint

These three get lumped together because they all involve services talking over HTTP, but they're actually answering different questions. Here's each one.

## Endpoint

An endpoint is the most basic of the three: it's just a specific URL where a service exposes some functionality. Something like `https://api.stripe.com/v1/charges` is an endpoint. You send a request to it and you get a response back.

The defining pattern is *request–response*, and it's *client-initiated*: your code decides when to reach out, the server answers, and then the exchange is over. This is what people usually mean by a "REST API endpoint." If you want fresh data, you have to ask again.

Use case: fetching or submitting data on demand — get a user's profile, create an order, search a database. Anything where *you* know when you need something.

The catch is that endpoints can't tell you when something changes on the server's side. Your only option is to keep asking ("polling"), which is wasteful if the answer is usually "nothing new."

## Webhook

A webhook flips the direction. Instead of you repeatedly asking a server "did anything happen yet?", you give the server *your* URL ahead of time, and it calls *you* when an event occurs. It's sometimes called a "reverse API" or a callback.

Concretely: you register a URL with, say, Stripe. When a payment succeeds, Stripe sends an HTTP POST to that URL with the event details. You didn't ask in that moment — the event triggered the message. It's *server-initiated* and *event-driven*, but each delivery is still a short one-way HTTP request, same as any other.

Use case: reacting to events you don't control the timing of — payment completed, code pushed to a repo, form submitted, shipping status changed.

### The subtle point worth internalizing: 
**the URL that receives a webhook is itself an endpoint.** A webhook isn't a different kind of thing from an endpoint so much as a *pattern for who calls whose endpoint, and when.*
What happens is: you (the consumer) create an endpoint on your own server — a URL you control, like https://myapp.com/webhooks/stripe. You then register that URL with the provider, usually once, through their dashboard or an API call. From that point on, the provider is the one making the calls. Whenever the relevant event happens on their side, they send an HTTP request to your URL.

So the direction of "who calls whom" is the opposite of a normal API request. In a normal request, you call the provider. With a webhook, the provider calls you. That's why it's sometimes called a "reverse API" or a "callback."

### Are Webhooks Re-used?
Yes, absolutely, webhooks fire repeatedly. This is the whole point and a common misconception worth clearing up. Registering the URL is a one-time setup, but the URL itself is persistent and gets called every single time a matching event occurs. If you register a webhook for "payment succeeded," Stripe will POST to your endpoint on the first payment, the hundredth, the ten-thousandth — for as long as the registration stands. A busy app might receive the same webhook thousands of times a day.

You register once; it fires forever (until you delete it). Think of it less like a single callback and more like a standing subscription: "whenever this happens, ping this URL." A few practical consequences fall out of that persistence:

## WebSocket

A WebSocket is a persistent, two-way channel. It starts as a normal HTTP request that gets "upgraded" into a long-lived connection, and once open, both sides can send messages to each other at any time without re-establishing anything.

This is different from the other two, which are both one-shot: a request happens, then it's done. A WebSocket stays open. The server can push to the client the instant something happens, the client can push back, and there's no per-message overhead of setting up a new connection.

Use case: real-time, continuous interaction — chat apps, live sports scores, multiplayer games, collaborative editors like Google Docs, trading dashboards.

## How they relate

The cleanest way to see it is a phone analogy:

- **Endpoint (REST):** you dial, ask one question, get an answer, hang up. *You* start it, it's brief, one round-trip.
- **Webhook:** you leave your number; they call you back when there's news. *They* start it, still brief, but now you find out about events without constantly re-dialing.
- **WebSocket:** you keep an open line where either of you can talk whenever, for as long as you want.

<img width="1440" height="840" alt="image" src="https://github.com/user-attachments/assets/ee16ef4f-b907-4345-905e-bbf869664567" />

Let me show the communication patterns side by side, since the whole distinction comes down to *who initiates, which direction messages flow, and how long the connection lives.*Here's how the three patterns compare — same client and server in each row, just different rules about who talks, which way, and for how long:The one thing worth remembering if it all blurs together: an **endpoint** is a *place* (a URL), while a **webhook** and a **WebSocket** are *patterns* for using endpoints. Webhooks and WebSockets both exist to solve the same underlying problem — a plain endpoint can't tell you when something changes, so you'd otherwise have to keep asking. A webhook solves that with occasional server-initiated pushes; a WebSocket solves it with a permanently open two-way line. You'd pick a webhook for infrequent events you react to, and a WebSocket when the interaction is continuous and real-time.

---
