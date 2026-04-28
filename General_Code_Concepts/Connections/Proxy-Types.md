# Prozy Types
A **proxy** is simply something that acts **on behalf of something else** — a middleman that sits between two parties.

---

## The Core Idea

```
Client  →→→  Proxy  →→→  Server
        ←←←         ←←←
```

Instead of the client talking directly to the server, the proxy intercepts the request, does something with it, and forwards it along. The response comes back through the proxy too.

---

## Common Types in Tech

### 🔵 Forward Proxy
Sits in front of **clients**. The server doesn't know who the real client is.
- **Use cases:** VPNs, hiding your IP, corporate internet filtering, bypassing geo-restrictions.
- *"The proxy fetches the web page on my behalf."*

### 🟢 Reverse Proxy
Sits in front of **servers**. The client doesn't know which server it's really talking to.
- **Use cases:** Load balancers (Nginx, HAProxy), CDNs (Cloudflare), SSL termination, API gateways.
- *"The proxy decides which backend server handles your request."*

### 🟡 Database Proxy / Connection Pooler
Sits between your **app and database** (like PgBouncer we just set up).
- **Use cases:** Reusing connections, limiting load on the DB, query routing.

### 🟠 HTTP / SOCKS Proxy
A general-purpose network proxy for routing internet traffic — often used in corporate networks or privacy tools.

### 🔴 Transparent Proxy
Intercepts traffic **without the client knowing**. Often used by ISPs or in enterprise security.

---

## Why Use a Proxy?

| Reason | Example |
|---|---|
| **Performance** | Cache responses, pool connections |
| **Security** | Hide real IPs, filter traffic, SSL offloading |
| **Scalability** | Spread load across many servers |
| **Control** | Log, throttle, or block certain requests |
| **Privacy** | Mask identity (VPN, Tor) |

---

## One-Line Summary

> A proxy is a middleman that **intercepts, inspects, and/or forwards** traffic between two systems — giving you control, visibility, or protection at that middle layer.

The word "proxy" comes from legal/diplomatic language — a proxy is someone authorized to act on your behalf, and it means exactly the same thing in tech.
