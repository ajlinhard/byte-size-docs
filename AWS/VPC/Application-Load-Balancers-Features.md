# AWS Application Load Balancer (ALB) — Feature Reference

**Last updated:** August 2026
**Scope:** Elastic Load Balancing v2 — `application` type load balancers.

---

## Table of Contents

1. [Overview](#1-overview)
2. [Core Components & Request Flow](#2-core-components--request-flow)
3. [Load Balancer Level Configuration](#3-load-balancer-level-configuration)
4. [Listeners](#4-listeners)
5. [Listener Rules (Deep Dive)](#5-listener-rules-deep-dive)
6. [Common Rule Patterns](#6-common-rule-patterns)
7. [Target Groups](#7-target-groups)
8. [ALB Integrations](#8-alb-integrations)
9. [Observability](#9-observability)
10. [Security Features](#10-security-features)
11. [Pricing & Capacity (LCUs)](#11-pricing--capacity-lcus)
12. [Quotas & Limits](#12-quotas--limits)
13. [Gotchas & Anti-Patterns](#13-gotchas--anti-patterns)
14. [Feature Timeline](#14-feature-timeline)
15. [IaC Reference Snippets](#15-iac-reference-snippets)

---

## 1. Overview

An Application Load Balancer is a managed **Layer 7 (HTTP/HTTPS)** reverse proxy. It parses requests, evaluates rules against request content (host, path, headers, method, query string, source IP), optionally authenticates the caller, optionally rewrites the request, then forwards it to a target group.

ALB launched in August 2016 as the L7 successor to the Classic Load Balancer.

### When to pick ALB vs. the alternatives

| Need | Use |
|---|---|
| HTTP/HTTPS, content-based routing, TLS termination, auth, WebSockets, gRPC | **ALB** |
| Ultra-low latency, static IPs, TCP/UDP, TLS passthrough, extreme PPS | **NLB** |
| Transparent insertion of third-party firewall/IDS appliances | **GWLB** |
| Legacy EC2-Classic workloads | **CLB** (avoid for new work) |
| Static IPs *and* L7 routing | **NLB → ALB** (register ALB as an NLB target) |
| Global anycast entry, DDoS/edge caching in front of L7 | **Global Accelerator** or **CloudFront** → ALB |

### What ALB is *not*

- Not an API gateway — no API key management, no usage plans, no request/response body transformation, no built-in rate limiting (that's AWS WAF).
- Not a cache — pair with CloudFront.
- Not a service mesh — no per-hop mTLS to targets, no retries/circuit breaking, no outlier ejection (beyond anomaly mitigation).
- No static IP addresses — resolve via DNS name only.

---

## 2. Core Components & Request Flow

```
Client
  │
  ▼
[ Load Balancer ]  ── scheme, subnets/AZs, security groups, IP address type, attributes
  │
  ▼
[ Listener ]       ── protocol + port, certificates, security policy, mTLS, listener attributes
  │
  ▼
[ Rules ]          ── priority-ordered: conditions → transforms → actions
  │                    (name + tags for identification)
  ▼
[ Target Group ]   ── protocol, port, protocol version, algorithm, stickiness, health checks
  │
  ▼
[ Targets ]        ── instance | ip | lambda
```

**Evaluation order inside the ALB:**

1. TLS handshake (cert selection via SNI, security policy, optional mTLS client-cert verification).
2. Request parsing + URI normalization + desync mitigation checks.
3. AWS WAF web ACL evaluation (if associated).
4. Rules evaluated in **priority order, lowest number first**. First match wins.
5. Matched rule's **transforms** applied (rewrite host header / URL).
6. Matched rule's **actions** run in `Order` — pre-routing (auth/JWT) first, routing action last.
7. Target selection within the target group (algorithm + stickiness + health).
8. Request forwarded, `X-Forwarded-*` and tracing headers applied.

> ⚠️ Ordering nuance: because transforms are applied during rule evaluation, WAF (which sits upstream of routing) inspects the **original** URI, not the rewritten one. If your rewrite is meant to normalize hostile paths, WAF still sees the raw path — which is usually what you want, but surprises people.

---

## 3. Load Balancer Level Configuration

### 3.1 Scheme

| Scheme | Description |
|---|---|
| `internet-facing` | Nodes get public IPs; DNS resolves to public addresses. Requires public subnets with an IGW route. |
| `internal` | Private IPs only; reachable from within the VPC / peered / VPN / Direct Connect. |

### 3.2 Subnets & Availability Zones

- Minimum **two AZs**, one subnet each. Each subnet needs at least a `/27` and 8 free IPs for scaling headroom.
- If a subnet runs out of usable IPs while the ALB attempts to scale, the load balancer runs with insufficient capacity — old nodes keep serving, but the stalled scale-out can produce 5xx errors or connection timeouts.
- **Local Zones** and **Outposts** subnets are supported with restrictions (Outposts requires two large instances for LB nodes; supported instance families include c5/c5d, m5/m5d, r5/r5d, c7i, m7i, r7i, scaled large → xlarge → 2xlarge → 4xlarge, then horizontally).
- **Cross-zone load balancing is on by default** for ALB at the LB level and cannot be disabled there — but it *can* be turned off per target group (`load_balancing.cross_zone.enabled`).

### 3.3 IP address type

| Type | Client side | Target side |
|---|---|---|
| `ipv4` | IPv4 only | IPv4 |
| `dualstack` | A + AAAA records | IPv4 or IPv6 target groups |
| `dualstack-without-public-ipv4` | AAAA only (IPv6-only clients) | still dual-stack internally |

`dualstack-without-public-ipv4` (May 2024) exists mostly to dodge public IPv4 address charges. Clients resolve only AAAA records.

### 3.4 Security groups

ALB **requires** security groups (unlike NLB, where they're optional). Standard hardening: for an internet-facing ALB fronted by CloudFront, allow inbound only from the `com.amazonaws.global.cloudfront.origin-facing` managed prefix list and remove every other inbound rule.

There is also a `deny_all_igw_traffic` attribute to block Internet Gateway traffic (defaults true for internal LBs).

### 3.5 Load balancer attributes

| Attribute | Default | Notes |
|---|---|---|
| `idle_timeout.timeout_seconds` | 60 | Range 1–4000. Set the app's idle timeout *higher* than the LB's, or you'll see 502s. HTTP/2 PING frames do **not** reset this timer. |
| `client_keep_alive.seconds` | 3600 | Range 60–604800 (1 min–7 days). |
| `routing.http.desync_mitigation_mode` | `defensive` | `monitor` \| `defensive` \| `strictest`. HTTP desync/request-smuggling protection. |
| `routing.http.drop_invalid_header_fields.enabled` | `false` | Drops headers whose names don't match `[A-Za-z0-9-]`. |
| `routing.http.preserve_host_header.enabled` | `false` | When true, the original `Host` reaches the target unmodified. |
| `routing.http.x_amzn_tls_version_and_cipher_suite.enabled` | `false` | Adds `X-Amzn-Tls-Version` / `X-Amzn-Tls-Cipher-Suite`. |
| `routing.http.xff_client_port.enabled` | `false` | Appends the client's source port to `X-Forwarded-For`. |
| `routing.http.xff_header_processing.mode` | `append` | `append` \| `preserve` \| `remove`. Critical when ALB sits behind another proxy. |
| `routing.http2.enabled` | `true` | Allows HTTP/2 on the client side. |
| `waf.fail_open.enabled` | `false` | If false and WAF is unreachable → HTTP 500. If true, forward anyway. |
| `deletion_protection.enabled` | `false` | Blocks accidental deletion. |
| `access_logs.s3.*` | disabled | Bucket, prefix, enabled. |
| `connection_logs.s3.*` | disabled | Bucket, prefix, enabled. |
| `health_check_logs.s3.*` | disabled | Bucket, prefix, enabled (Nov 2025). |
| `zonal_shift.config.enabled` | `false` | Allows ARC zonal shift/autoshift. |

### 3.6 Capacity Unit (LCU) Reservation

Launched Nov 2024. Reserves a **minimum** capacity floor so the ALB doesn't have to scale from cold during a spike.

- Minimum reservation: **100 LCUs**. Maximum is account-quota bound (default 15,000 per ALB).
- Capacity is reserved regionally and distributed evenly across AZs — make sure targets are evenly spread too.
- Reservation status: `pending` → `provisioned`, or `failed`, or `rebalancing` (when an AZ is added/removed).
- You can **increase** as often as you like, but **decrease only twice per day**.
- Fulfilment is first-come-first-served against zonal capacity; usually minutes, occasionally hours.
- Size it using the **`PeakLCUs`** metric (per-minute `Sum`), *not* `ConsumedLCUs` — the latter only reflects billing dimensions.
- Monitor with `ReservedLCUs` (per-minute) vs. `PeakLCUs`.

Use cases: ticket on-sales, product launches, scheduled content drops, load tests.

```bash
aws elbv2 modify-capacity-reservation \
  --load-balancer-arn "$LB_ARN" \
  --minimum-load-balancer-capacity CapacityUnits=3000

aws elbv2 describe-capacity-reservation --load-balancer-arn "$LB_ARN"
```

### 3.7 Resource map

Console-only visual graph of listener → rule → target group → target relationships. Genuinely useful for auditing a large rule set (March 2024).

---

## 4. Listeners

A listener is a process that checks for connection requests on a configured protocol and port. **An ALB with no listener cannot receive traffic.**

### 4.1 Protocols and ports

- **Protocols:** `HTTP`, `HTTPS` only.
- **Ports:** 1–65535.
- Up to **50 listeners** per ALB (adjustable).

If you need targets (not the LB) to terminate TLS, ALB can't do it — use an NLB with a TCP listener on 443.

### 4.2 HTTPS listeners

**Certificates**
- One **default certificate**, plus a **certificate list** of up to 25 additional certs (adjustable).
- **SNI** selects among them at handshake time (supported since Oct 2017).
- Sources: ACM (recommended, auto-renewal) or IAM.
- Supported: RSA 2048/3072/4096-bit and all ECDSA certs. **ED25519 keys are not supported.**

**Security policies**
Predefined policy families:

| Family | Notes |
|---|---|
| `ELBSecurityPolicy-2016-08` | Legacy default; broad compatibility. |
| `ELBSecurityPolicy-TLS13-*-2021-06` | TLS 1.3 policies (Mar 2023). `TLS13-1-2-2021-06` is the modern sane default. |
| `ELBSecurityPolicy-FS-*` | Forward-secrecy-only cipher sets. |
| `ELBSecurityPolicy-TLS13-1-2-FIPS-*` | FIPS 140-3 validated modules (Nov 2023). |
| RFC 9151 / CNSA 1.0 policies | **New Aug 2026** — NSA Commercial National Security Algorithm suite compliance for TLS 1.2/1.3, plus broader-interoperability variants so you can default to CNSA while non-CNSA clients migrate. |

**HTTP/2**
- Native on HTTPS listeners. Up to **128 concurrent streams per connection**.
- **No server push.**
- Works with mTLS in both passthrough and verify modes.

**WebSockets**
- Native, on both HTTP and HTTPS listeners, via HTTP/1.1 `Upgrade`.
- The TCP connection becomes a persistent WS tunnel through the LB.
- ⚠️ **Not supported for target groups with Target Optimizer enabled.**

**Mutual TLS (mTLS)** — Nov 2023

| Mode | Behaviour |
|---|---|
| `off` | Standard one-way TLS. |
| `passthrough` | Accepts any client cert, forwards the whole chain to targets in `X-Amzn-Mtls-Clientcert` headers. Target does the validation. |
| `verify` | ALB validates against a **Trust Store** (CA bundle in S3 + optional CRLs) and rejects the handshake on failure. |

- X.509v3 required (v1 client certs are rejected).
- Max cert chain depth 4; CA cert ≤16 KB; ≤25 CA certs per trust store (adjustable); up to 30 revocation lists / 500,000 revocation entries per trust store.
- **Only 2 listeners per LB may use verify mode.** 20 trust stores per account (adjustable).
- Options: `AdvertiseTrustStoreCaNames`, `IgnoreClientCertificateExpiry`, `TrustStoreAssociationStatus`.

### 4.3 Listener attributes

Two families — mTLS/TLS **request-header renaming**, and **response-header injection**.

**Request header name overrides** (useful when a target already uses those header names):
```
routing.http.request.x_amzn_mtls_clientcert.header_name
routing.http.request.x_amzn_mtls_clientcert_leaf.header_name
routing.http.request.x_amzn_mtls_clientcert_subject.header_name
routing.http.request.x_amzn_mtls_clientcert_issuer.header_name
routing.http.request.x_amzn_mtls_clientcert_serial_number.header_name
routing.http.request.x_amzn_mtls_clientcert_validity.header_name
routing.http.request.x_amzn_tls_version.header_name
routing.http.request.x_amzn_tls_cipher_suite.header_name
```

**Response header injection** — ALB can add security/CORS headers so your app doesn't have to. As of **Feb 2025** these apply to *all* response codes (previously only 2xx/3xx):

```
routing.http.response.server.enabled                                # strip the "Server" header
routing.http.response.strict_transport_security.header_value        # HSTS
routing.http.response.content_security_policy.header_value          # CSP
routing.http.response.x_content_type_options.header_value           # nosniff
routing.http.response.x_frame_options.header_value                  # DENY / SAMEORIGIN
routing.http.response.access_control_allow_origin.header_value
routing.http.response.access_control_allow_methods.header_value
routing.http.response.access_control_allow_headers.header_value
routing.http.response.access_control_allow_credentials.header_value
routing.http.response.access_control_expose_headers.header_value
routing.http.response.access_control_max_age.header_value
```

This is one of the highest-ROI, lowest-effort ALB features — it lets you enforce HSTS/CSP/CORS uniformly across every service behind the LB.

### 4.4 Default action (the default rule)

Every listener has a default rule. It:
- Cannot be deleted.
- **Cannot have conditions.**
- **Cannot have transforms.**
- Is always evaluated **last** (matches everything that no other rule matched).

Typical default actions: forward to a catch-all target group, `fixed-response` 404, or `redirect` HTTP→HTTPS.

### 4.5 X-Forwarded headers

| Header | Content |
|---|---|
| `X-Forwarded-For` | Client IP (behaviour governed by `xff_header_processing.mode`; optionally with client port) |
| `X-Forwarded-Proto` | `http` or `https` — what the client used |
| `X-Forwarded-Port` | Listener port |
| `X-Amzn-Trace-Id` | Request tracing ID (X-Ray-compatible) |

---

## 5. Listener Rules (Deep Dive)

A rule = **priority** + **name/tags** + **conditions (If)** + **transforms (optional)** + **actions (Then)**.

Console flow mirrors exactly this: *Name and tags → Conditions → Transforms → Pre-routing action → Routing action → Priority*.

### 5.1 Priority

- Integer **1 – 50,000**, unique per listener.
- Evaluated **lowest first**; the **first matching rule wins** and evaluation stops.
- The default rule is implicitly last.
- **Leave gaps** (10, 20, 30…) so you can insert rules later without renumbering. Reordering rules is a `set-rule-priorities` call; renumbering a dense list is painful.

Rule updates are **not instantaneous** — requests may route via the previous configuration briefly after a change. In-flight requests complete.

### 5.2 Name and tags

Rules support an optional **Name** plus arbitrary **tags** (key/value). In the console these live under *Name and tags* at the top of the rule editor.

Why this matters more than it looks:

- Rule ARNs are opaque (`.../listener-rule/app/my-lb/50dc.../f2f7.../9683...`). Without names, a 60-rule listener is unreadable in the console.
- Names/tags give you a stable human handle for **cost allocation**, **ownership** (`team=payments`), **change management** (`ticket=JIRA-4412`), and **automated cleanup** (`ephemeral=true`, `expires=2026-09-01`).
- Tags participate in **IAM resource-level permissions and tagging condition keys**, so you can scope who may modify which rules (e.g. `aws:ResourceTag/team`).
- Useful convention: name rules by *intent + target*, e.g. `canary-checkout-5pct`, `legacy-api-v1-rewrite`, `blocklist-abusive-cidrs`, `maintenance-mode-fixed-503`.

```bash
aws elbv2 add-tags \
  --resource-arns "$RULE_ARN" \
  --tags Key=Name,Value=canary-checkout-5pct Key=team,Value=payments Key=expires,Value=2026-09-01
```

> Note: a rule's **Name** is implemented as the `Name` tag. Tag limits for ELB resources apply (50 tags per resource).

### 5.3 Conditions (the "If")

Six condition types:

| Field | Matching | Case sensitivity | Wildcards | Regex |
|---|---|---|---|---|
| `host-header` | Host name | Insensitive | `*` `?` | ✅ |
| `path-pattern` | URL path only (not query) | **Sensitive** | `*` `?` | ✅ |
| `http-header` | Named header's value | Insensitive | `*` `?` in value only | ✅ |
| `http-request-method` | Method verb | **Sensitive** | ❌ | ❌ |
| `query-string` | Key/value pairs or bare values | Insensitive | `*` `?` | ❌ |
| `source-ip` | Client IP in CIDR | n/a | ❌ | ❌ |

#### Cardinality rules

- **Zero or one** each of: `host-header`, `http-request-method`, `path-pattern`, `source-ip`.
- **Zero or more** each of: `http-header`, `query-string`.
- Multiple conditions on one rule are **AND**-ed.
- Multiple values *within* one condition are **OR**-ed. To require all of several strings, split into one condition per string.
- Max **3 match evaluations per condition**, max **5 match evaluations per rule**, max **5 condition values per rule**.
- Wildcard budget per rule: the conditions doc states **5 wildcard characters per rule**; the quotas table lists **6**. Treat 5 as the safe planning number.
- Rules apply only to **visible ASCII**; control characters (`0x00`–`0x1f`, `0x7f`) are excluded.
- Path conditions are evaluated **after URI normalization**.

#### Value matching vs. regex matching

`host-header`, `http-header`, and `path-pattern` support **either** glob-style value matching **or** regex matching (`RegexValues`). Max 128 chars either way.

**Unsupported regex features** (same restriction applies to transforms): lookaheads, lookbehinds, backreferences, atomic groups, possessive quantifiers, subroutines, recursion, and Unicode character classes such as `\p{L}`.

```jsonc
// Value matching
[{ "Field": "host-header",
   "HostHeaderConfig": { "Values": ["*.example.com"] } }]

// Regex matching
[{ "Field": "host-header",
   "HostHeaderConfig": { "RegexValues": ["^(.*)\\.example\\.com$"] } }]

// Path — regex
[{ "Field": "path-pattern",
   "PathPatternConfig": { "RegexValues": ["^\\/api\\/v[0-9]+\\/(.*)$"] } }]

// Header — value matching, up to 3 evaluations (OR)
[{ "Field": "http-header",
   "HttpHeaderConfig": { "HttpHeaderName": "User-Agent",
                         "Values": ["*Chrome*", "*Safari*"] } }]

// Query string — key/value pair OR bare value
[{ "Field": "query-string",
   "QueryStringConfig": { "Values": [ {"Key":"version","Value":"v1"},
                                      {"Value":"*example*"} ] } }]

// Source IP — CIDR, IPv4 and IPv6
[{ "Field": "source-ip",
   "SourceIpConfig": { "Values": ["192.0.2.0/24", "2001:db8::/32"] } }]
```

#### Condition specifics worth knowing

- **`host-header`**: must contain at least one `.`; only alphabetic characters after the final `.`. `*.example.com` matches `test.example.com` but **not** `example.com` — you need both values to cover apex + subdomains.
- **`path-pattern`**: allowed chars `A-Za-z0-9 _ - . $ / ~ " ' @ : + &` (as `&amp;`) plus `*` `?`. It routes but never *alters* the request — `/img/*` forwards `/img/pic.jpg` as `/img/pic.jpg`. Use a **transform** if you need it changed.
- **gRPC path patterns** are `/package`, `/package.service`, `/package.service/method`.
- **`http-request-method`**: exact, case-sensitive, `A-Z - _`, max 40 chars. Custom verbs allowed. AWS recommends routing `GET` and `HEAD` identically because `HEAD` responses may be cached.
- **`http-header`**: wildcards work in the *value*, not the header *name*. If `routing.http.drop_invalid_header_fields` is on, non-conforming header names are dropped before evaluation.
- **`source-ip`**: this is the **immediate peer's** IP. Behind CloudFront or any proxy, that's the proxy — use an `http-header` condition on `X-Forwarded-For` instead. `255.255.255.255/32` is disallowed.

### 5.4 Transforms

**Launched October 15, 2025.** A transform **rewrites the inbound request before it is routed to the target**. It does *not* change the routing decision — conditions are evaluated against the original request.

This eliminated the most common reason people put NGINX/Envoy between the ALB and their services.

#### Two transform types

| Type | Rewrites |
|---|---|
| `host-header-rewrite` | The `Host` header (domain name) |
| `url-rewrite` | The URL **path and/or query string** — *not* protocol or port |

#### Transform rules

- **One `host-header-rewrite` + one `url-rewrite` per rule**, max.
- **Cannot be added to the default rule.**
- Regex `Regex` → `Replace`, with `$1`, `$2`… capture group references.
- **No pattern match → the original request is forwarded unchanged.**
- **Pattern matched but transform fails → HTTP 500.**
- Same regex feature restrictions as conditions (no lookarounds, backreferences, atomic groups, possessive quantifiers, subroutines, recursion, `\p{...}`).
- The console includes a **rule tester** for both regex conditions and rewrite transforms — use it.

#### Examples

Host header rewrite — public hostname → internal endpoint:

```json
[
  {
    "Type": "host-header-rewrite",
    "HostHeaderRewriteConfig": {
      "Rewrites": [
        { "Regex": "^mywebsite-(.+).com$", "Replace": "internal.dev.$1.myweb.com" }
      ]
    }
  }
]
```
`https://mywebsite-example.com/project-a` → target sees Host `internal.dev.example.myweb.com`.

URL rewrite — pretty path → legacy query string:

```json
[
  {
    "Type": "url-rewrite",
    "UrlRewriteConfig": {
      "Rewrites": [
        { "Regex": "^/dp/([A-Za-z0-9]+)/?$", "Replace": "/product.php?id=$1" }
      ]
    }
  }
]
```
`https://www.example.com/dp/B09G3HRMW` → `/product.php?id=B09G3HRMW`.

Strip an API version prefix:

```json
[
  {
    "Type": "url-rewrite",
    "UrlRewriteConfig": {
      "Rewrites": [ { "Regex": "^/api/v1/(.*)$", "Replace": "/$1" } ]
    }
  }
]
```

#### Rewrite vs. Redirect — pick correctly

| | **Redirect** (action) | **Rewrite** (transform) |
|---|---|---|
| Browser address bar | Changes | Unchanged |
| Status code | 301 / 302 | None (transparent) |
| Where it happens | Client-side round trip | Server-side, in the ALB |
| Extra RTT | Yes | No |
| Typical use | Domain moves, HTTP→HTTPS, consolidations, fixing broken links | Clean/SEO URLs, hiding internal structure, legacy URL mapping, prefix stripping |

#### Interaction gotcha

Transforms execute during rule evaluation, which is *after* WAF inspection. AWS WAF sampled requests will show the **original** URI. Don't rely on a rewrite to sanitize input for WAF.

### 5.5 Actions (the "Then")

Actions determine how the LB handles matching requests. Each action has a `Type`, a config object, and an `Order`.

#### Action catalogue

| Type | Category | Listener requirement |
|---|---|---|
| `authenticate-oidc` | Pre-routing (auth) | HTTPS only |
| `authenticate-cognito` | Pre-routing (auth) | HTTPS only |
| `jwt-validation` | Pre-routing (auth) | HTTPS only |
| `forward` | **Routing** | HTTP or HTTPS |
| `redirect` | **Routing** | HTTP or HTTPS |
| `fixed-response` | **Routing** | HTTP or HTTPS |

#### Action rules

- **Exactly one** routing action (`forward` | `redirect` | `fixed-response`) per rule, and it must be **last**.
- An HTTPS listener rule may combine **one** authentication action (`authenticate-oidc`, `authenticate-cognito`, or `jwt-validation`) with the routing action.
- With multiple actions, the one with the **lowest `Order` runs first**.
- If the target group's protocol version is **HTTP/2 or gRPC, only `forward` is supported.**

---

#### `forward`

Routes to one or more target groups.

- Up to **5 target groups per forward action**.
- Each target group gets a **weight, 0–999**. Traffic splits proportionally. Two groups at weight 10 → 50/50; weights 10 and 20 → 1:2.
- **No automatic failover** between weighted target groups. If one is empty or all-unhealthy, ALB does *not* shift its share elsewhere. This is the #1 canary-deployment footgun.

**Target group stickiness (`AWSALBTG` cookie)**

Weighted forwarding does **not** honour stickiness by default. Enable `TargetGroupStickinessConfig` and the LB issues an encrypted `AWSALBTG` cookie recording the chosen target group; subsequent requests carrying it go to that group.

- If *any* target group in the forward action has target-level stickiness enabled, you **must** enable group-level stickiness.
- URL-encoded cookie values are **not** supported.
- For CORS requests, some browsers need `SameSite=None; Secure` — ALB then also emits **`AWSALBTGCORS`** with the same payload plus that attribute. Clients receive both.

```json
[
  {
    "Type": "forward",
    "ForwardConfig": {
      "TargetGroups": [
        { "TargetGroupArn": "arn:...:targetgroup/blue-targets/73e2d6bc24d8a067",  "Weight": 90 },
        { "TargetGroupArn": "arn:...:targetgroup/green-targets/09966783158cda59", "Weight": 10 }
      ],
      "TargetGroupStickinessConfig": { "Enabled": true, "DurationSeconds": 1000 }
    }
  }
]
```

---

#### `redirect`

Redirects the client from one URL to another. URI components: `protocol://hostname:port/path?query`.

- Status: `HTTP_301` (permanent) or `HTTP_302` (temporary).
- **You must modify at least one of protocol, hostname, port, or path** or you create a redirect loop. Unmodified components retain their original values.
- HTTP→HTTP, HTTP→HTTPS, HTTPS→HTTPS are allowed. **HTTPS→HTTP is not.**
- Reserved keywords for reusing original components:

| Keyword | Retains | Valid in |
|---|---|---|
| `#{protocol}` | Protocol | protocol, query |
| `#{host}` | Domain | hostname, path, query |
| `#{port}` | Port | port, path, query |
| `#{path}` | Path (no leading `/`) | path, query |
| `#{query}` | Query string | query |

- Limits: hostname ≤128 chars (`A-Za-z0-9 - * ?`), path ≤128 chars and case-sensitive, query ≤128 chars, port 1–65535.
- Metric: **`HTTP_Redirect_Count`**. Also recorded in access logs.

```json
[
  {
    "Type": "redirect",
    "RedirectConfig": {
      "Protocol": "HTTPS", "Port": "443",
      "Host": "#{host}", "Path": "/#{path}", "Query": "#{query}",
      "StatusCode": "HTTP_301"
    }
  }
]
```

---

#### `fixed-response`

Drops the request and returns a canned HTTP response.

- Status codes: **2xx, 4xx, or 5xx** (no 3xx — use `redirect`).
- Optional `ContentType` and `MessageBody`.
- Metric: **`HTTP_Fixed_Response_Count`**. Recorded in access logs.

```json
[
  {
    "Type": "fixed-response",
    "FixedResponseConfig": {
      "StatusCode": "200",
      "ContentType": "text/plain",
      "MessageBody": "Hello world"
    }
  }
]
```

---

#### `authenticate-oidc` / `authenticate-cognito`

Offloads **interactive user login** to the ALB before the request ever reaches your app (May 2018).

- HTTPS listeners only.
- `authenticate-cognito` → Amazon Cognito user pools (which can federate to social/SAML IdPs).
- `authenticate-oidc` → any OIDC-compliant IdP (Okta, Auth0, Entra ID, Google, Ping…). You supply `Issuer`, `AuthorizationEndpoint`, `TokenEndpoint`, `UserInfoEndpoint`, `ClientId`, `ClientSecret`.
- Session managed via the **`AWSELBAuthSessionCookie`** cookie; `SessionTimeout` and `Scope` configurable.
- `OnUnauthenticatedRequest`: `authenticate` (redirect to IdP) | `deny` (401) | `allow` (pass through).
- ALB passes claims to the target as `x-amzn-oidc-accesstoken`, `x-amzn-oidc-identity`, and `x-amzn-oidc-data` (a signed JWT).

> 🔐 **Security requirement:** targets must **verify the signature** of `x-amzn-oidc-data` and confirm the `signer` field equals the expected ALB ARN before trusting any claim. Skipping this was the root of CVE-2024-10125. Also keep targets off public IPs.

#### `jwt-validation`

**Launched November 21, 2025.** Validates JWT access tokens for **service-to-service (S2S) / machine-to-machine (M2M)** calls — no human, no redirect, no cookie.

- HTTPS listeners only.
- Required config: **`Issuer`** and **`JwksEndpoint`** (full HTTPS URL, ≤256 chars each).
- ALB validates the **signature** plus mandatory claims **`iss`** and **`exp`**; if present, it also validates **`nbf`** and **`iat`**.
- Up to **10 additional claims** validated, in three formats: single-string, space-separated (≤10 values), string-array (≤10 values).
- **Only RS256 is supported.**
- JWKS endpoint response must be **≤150 KB** and contain **≤10 keys**, or requests won't be forwarded.
- Valid token → request forwarded **with the token unchanged**. Invalid → rejected.

```bash
aws elbv2 create-rule \
  --listener-arn "$LISTENER_ARN" \
  --priority 10 \
  --conditions Field=path-pattern,Values="/api/*" \
  --actions '[
    { "Type":"jwt-validation",
      "JwtValidationConfig":{
        "JwksEndpoint":"https://issuer.example.com/.well-known/jwks.json",
        "Issuer":"https://issuer.example.com",
        "AdditionalClaims":[
          { "Format":"string-array", "Name":"scope", "Values":["orders:read","orders:write"] }
        ]
      },
      "Order":1 },
    { "Type":"forward", "TargetGroupArn":"'"$TG_ARN"'", "Order":2 }
  ]'
```

---

## 6. Common Rule Patterns

### 6.1 Force HTTPS (canonical)

HTTP:80 listener, **default action**:

```bash
aws elbv2 modify-listener --listener-arn "$HTTP_LISTENER" \
  --default-actions '[{"Type":"redirect","RedirectConfig":{
      "Protocol":"HTTPS","Port":"443","Host":"#{host}",
      "Path":"/#{path}","Query":"#{query}","StatusCode":"HTTP_301"}}]'
```
Pair with the `strict_transport_security` listener attribute on the HTTPS listener.

### 6.2 Path-based microservice routing

| Priority | Condition | Action |
|---|---|---|
| 10 | `path-pattern = /api/users/*` | forward → `tg-users` |
| 20 | `path-pattern = /api/orders/*` | forward → `tg-orders` |
| 30 | `path-pattern = /static/*` | forward → `tg-static` |
| default | — | fixed-response 404 |

### 6.3 Host-based multi-tenant / multi-brand

| Priority | Condition | Action |
|---|---|---|
| 10 | `host-header = api.example.com` | forward → `tg-api` |
| 20 | `host-header = admin.example.com` + `source-ip = <office CIDRs>` | forward → `tg-admin` |
| 21 | `host-header = admin.example.com` | fixed-response 403 |
| 30 | `host-header = *.example.com` | forward → `tg-tenant-app` |

Note the 20/21 pairing: because conditions AND together and there's no NOT operator, you express "deny everyone else" as a **lower-priority catch-all** immediately after the allow rule.

### 6.4 Canary / weighted blue-green

```json
{ "Type":"forward","ForwardConfig":{
  "TargetGroups":[
    {"TargetGroupArn":"...blue","Weight":95},
    {"TargetGroupArn":"...green","Weight":5}],
  "TargetGroupStickinessConfig":{"Enabled":true,"DurationSeconds":3600}}}
```
Progress 95/5 → 75/25 → 50/50 → 0/100. **Watch for the no-failover behaviour** — always gate progression on `HTTPCode_Target_5XX_Count` and `UnHealthyHostCount` for the green group.

### 6.5 Header-based canary (opt-in dogfooding)

| Priority | Condition | Action |
|---|---|---|
| 5 | `http-header X-Canary = true` | forward → `tg-green` |
| 10 | (none/host) | forward → `tg-blue` (weighted 100/0) |

Lets internal users and synthetic tests hit the new version deterministically before you shift real traffic.

### 6.6 Maintenance mode with an escape hatch

| Priority | Condition | Action |
|---|---|---|
| 1 | `source-ip = <ops CIDRs>` | forward → `tg-app` |
| 2 | `path-pattern = /health` | fixed-response 200 |
| 3 | (no condition possible on non-default rules → use `path-pattern=/*`) | fixed-response 503 + HTML body |

Flip maintenance mode by changing rule 3's priority or action — no deploy, no DNS change.

### 6.7 IP allow/deny list

| Priority | Condition | Action |
|---|---|---|
| 1 | `source-ip = 192.168.1.0/24, 10.0.0.0/16` | fixed-response 403 "Access denied" |

For anything beyond a handful of CIDRs, or for rate limiting / bot control / geo, use **AWS WAF** instead — ALB caps you at 5 condition values per rule.

### 6.8 Mobile vs. desktop split

```json
[{ "Field":"http-header",
   "HttpHeaderConfig":{ "HttpHeaderName":"User-Agent",
     "Values":["*Mobile*","*Android*","*iPhone*"] } }]
```
→ `redirect` to `m.example.com` (HTTP_302), or forward to a mobile target group.

### 6.9 Legacy URL migration without breaking bookmarks

Two complementary approaches:

- **Rewrite** (invisible, no extra RTT): condition `path-pattern ^/old/(.*)$`, transform `url-rewrite` `^/old/(.*)$` → `/new/$1`.
- **Redirect** (updates bookmarks and SEO): `redirect` with `Path: /new/#{path}` and `HTTP_301`.

Use rewrite when the *backend* changed; redirect when the *canonical public URL* changed.

### 6.10 Strip the version prefix before the backend sees it

Backend serves `/users`, public API is `/api/v2/users`:

- Condition: `path-pattern` regex `^/api/v2/(.*)$`
- Transform: `url-rewrite` `^/api/v2/(.*)$` → `/$1`
- Action: forward → `tg-users-v2`

This is the pattern that removed NGINX sidecars from a lot of ECS/EKS stacks.

### 6.11 Single external hostname, many internal hosts

- Condition: `host-header = api.example.com` + `path-pattern = /billing/*`
- Transform: `host-header-rewrite` `^api\.example\.com$` → `billing.internal.svc`
- Transform: `url-rewrite` `^/billing/(.*)$` → `/$1`
- Action: forward → `tg-billing`

Vhost-based backends (S3 website endpoints, SaaS origins, legacy apps that key off `Host`) work without touching app code.

### 6.12 CloudFront-only enforcement

1. Security group: inbound only from the CloudFront origin-facing managed prefix list.
2. CloudFront adds a secret custom header (e.g. `X-Origin-Verify: <random>`).
3. ALB rule priority 1: `http-header X-Origin-Verify = <random>` → forward.
4. ALB rule priority 2: `path-pattern /*` → fixed-response 403.

Belt and braces: prefix list stops network-level bypass, header stops anyone who somehow gets a CloudFront distribution pointed at you.

### 6.13 API auth at the edge (S2S)

- Priority 10: `path-pattern /api/*` → `jwt-validation` (Order 1) + `forward` (Order 2).
- Priority 20: `path-pattern /internal/*` + `source-ip <vpc cidr>` → forward.
- Priority 30: `path-pattern /app/*` → `authenticate-oidc` (Order 1) + `forward` (Order 2).

One listener serving machine clients (JWT), internal clients (network trust), and humans (OIDC redirect flow).

### 6.14 Serverless + container hybrid

- `path-pattern /thumbnails/*` → forward → **Lambda** target group
- `path-pattern /*` → forward → ECS/EKS IP target group

### 6.15 gRPC service routing

- Listener: HTTPS, target group protocol version `GRPC`.
- Conditions: `path-pattern = /myco.orders.OrderService/*`.
- **Only `forward` actions are valid.**
- Health check must be a custom `/package.service/method` path with expected gRPC status codes.

### 6.16 A/B testing by query string

```json
[{ "Field":"query-string",
   "QueryStringConfig":{ "Values":[{"Key":"variant","Value":"b"}] } }]
```
→ forward → `tg-variant-b`.

### 6.17 Method-based split (read/write separation)

| Priority | Condition | Action |
|---|---|---|
| 10 | `http-request-method = GET, HEAD` + `path-pattern /api/*` | forward → `tg-read-replicas` |
| 20 | `path-pattern /api/*` | forward → `tg-primary` |

Keep `GET` and `HEAD` on the same path, per AWS guidance.

### 6.18 Kill-switch for an abusive endpoint

Priority 1, `path-pattern = /expensive-report`, `fixed-response` 429 with `Retry-After` in the body. Instant, no deploy, reversible.

---

## 7. Target Groups

### 7.1 Routing configuration

- Protocols **HTTP, HTTPS**; ports 1–65535. Port can be overridden per registered target.
- For HTTPS target groups or HTTPS health checks: if any HTTPS listener uses a TLS 1.3 policy, `ELBSecurityPolicy-TLS13-1-0-2021-06` is used for target connections; otherwise `ELBSecurityPolicy-2016-08`.
- **ALB does not validate target certificates** — self-signed and expired certs work. Traffic inside the VPC is authenticated at the packet level, so this isn't the exposure it looks like, but traffic leaving AWS needs separate protection.

### 7.2 Target types

| Type | Registers | Notes |
|---|---|---|
| `instance` | EC2 instance ID | Routes to the primary private IP of the primary ENI. Works with ASG auto-registration. |
| `ip` | IP address | Any private IP from any ENI → multiple apps per instance on the same port. Used by ECS `awsvpc`, EKS, on-prem via DX/VPN, peered VPCs, RDS-adjacent services. |
| `lambda` | One Lambda function | Exactly one function per target group. |

Allowed `ip` CIDRs: the target group VPC's subnets, `10.0.0.0/8`, `100.64.0.0/10`, `172.16.0.0/12`, `192.168.0.0/16`. **Publicly routable IPs are not allowed.**

**Registration limits:**
- Cannot register IPs of **another ALB in the same VPC** (allowed if it's in a peered VPC).
- Cannot register **instances by ID** across a VPC peering boundary — register by IP instead.
- For ALBs in a Local Zone, `ip` targets must be in the **same Local Zone**.

### 7.3 IP address type

`ipv4` or `ipv6`. An IPv6 target group can't be used with an `ipv4` load balancer, and **Lambda cannot be registered in an IPv6 target group**.

### 7.4 Protocol version

Default `HTTP1`. Options: `HTTP1`, `HTTP2`, `GRPC`.

| Request protocol | TG protocol version | Result |
|---|---|---|
| HTTP/1.1 | HTTP1 | ✅ |
| HTTP/2 | HTTP1 | ✅ |
| gRPC | HTTP1 | ❌ |
| HTTP/1.1 | HTTP2 | ❌ |
| HTTP/2 | HTTP2 | ✅ |
| gRPC | HTTP2 | ✅ if targets support gRPC |
| HTTP/1.1 | GRPC | ❌ |
| HTTP/2 | GRPC | ✅ if POST |
| gRPC | GRPC | ✅ |

**gRPC / HTTP2 protocol version constraints:** HTTPS listener only, `forward` actions only, `instance` and `ip` target types only, no Lambda. gRPC supports unary and all three streaming modes; requires a custom health check method `/package.service/method` plus expected gRPC status codes. HTTP/2 max 128 streams per client connection.

### 7.5 Load balancing algorithms

| `load_balancing.algorithm.type` | Behaviour |
|---|---|
| `round_robin` *(default)* | Even rotation. |
| `least_outstanding_requests` | Sends to the target with fewest in-flight requests. Best for uneven request cost / long-lived connections. |
| `weighted_random` | Weighted random selection; the prerequisite for anomaly mitigation. |

**Automatic Target Weights (ATW) / anomaly mitigation** — `load_balancing.algorithm.anomaly_mitigation = on|off`, only valid with `weighted_random`. ALB detects targets with anomalous error rates and reduces their share automatically (Nov 2023).

### 7.6 Stickiness

| Attribute | Notes |
|---|---|
| `stickiness.enabled` | Default `false`. |
| `stickiness.type` | `lb_cookie` or `app_cookie`. |
| `stickiness.lb_cookie.duration_seconds` | 1s–7 days; default 1 day. Cookie: `AWSALB`. |
| `stickiness.app_cookie.cookie_name` | Your app's cookie. **Cannot start with `AWSALB`, `AWSALBAPP`, or `AWSALBTG`** (reserved). |
| `stickiness.app_cookie.duration_seconds` | 1s–7 days; default 1 day. |

Cookie cheat sheet: `AWSALB`/`AWSALBCORS` = duration stickiness · `AWSALBAPP` = app-cookie stickiness · `AWSALBTG`/`AWSALBTGCORS` = target-**group** stickiness · `AWSELBAuthSessionCookie` = ALB OIDC/Cognito session.

### 7.7 Other target group attributes

| Attribute | Default | Notes |
|---|---|---|
| `deregistration_delay.timeout_seconds` | 300 | 0–3600. Connection draining window. |
| `slow_start.duration_seconds` | 0 (off) | 30–900. Linearly ramps traffic to newly registered targets (JIT/JVM warm-up, cache fill). |
| `load_balancing.cross_zone.enabled` | `use_load_balancer_configuration` | `true` \| `false` \| inherit. This is where you turn cross-zone off for ALB. |
| `lambda.multi_value_headers.enabled` | `false` | Lambda TGs only — arrays vs. strings for headers/query params. |

### 7.8 Health checks

Per target group. Configurable: protocol, port (or `traffic-port`), path, healthy/unhealthy thresholds, timeout, interval, matcher (HTTP codes, or gRPC status codes for gRPC target groups).

A newly registered target starts receiving traffic **as soon as it passes the first health check**, regardless of the configured healthy threshold.

Deregistration moves a target to `draining` until in-flight requests finish.

### 7.9 Target group health (availability thresholds)

By default a target group is "healthy" with **one** healthy target — inadequate for large fleets. Configure minimum count *or* percentage thresholds and two independent actions:

| Attribute | Default |
|---|---|
| `target_group_health.dns_failover.minimum_healthy_targets.count` | 1 |
| `target_group_health.dns_failover.minimum_healthy_targets.percentage` | `off` |
| `target_group_health.unhealthy_state_routing.minimum_healthy_targets.count` | 1 |
| `target_group_health.unhealthy_state_routing.minimum_healthy_targets.percentage` | `off` |

- **DNS failover** — below threshold in a zone, that zone's node IPs are marked unhealthy in DNS so clients stop resolving to it. (Client DNS caches may hold the address until the **60-second** TTL expires.)
- **Routing failover** — below threshold, the node sends traffic to **all** targets including unhealthy ones. Counterintuitive but correct: better a degraded target than a stampede onto the survivors.

Constraints:
- Not supported for **Lambda** target groups.
- **Do not configure a DNS failover threshold if the ALB is a target of an NLB or Global Accelerator.**
- If both count and percentage are set, the action fires when **either** is breached.
- The DNS failover threshold must be **≥** the routing failover threshold.
- Percentages are computed against the target population as seen by the node — which depends on whether cross-zone is on or off.
- If **all** zones are unhealthy, ALB fails open and sends traffic everywhere.
- With multiple target groups, a zone passes DNS health checks if **at least one** target group is healthy there.

### 7.10 Target Optimizer

**Launched November 20, 2025.** Enforces a **maximum number of concurrent requests per target** — as low as 1.

- Enabled by specifying a **target control port** at target group creation.
- Requires an **AWS-provided agent** running on each target, which tracks concurrency and communicates with the LB over the control port.
- **Can only be enabled at target group creation**; the control port is immutable afterwards.
- Set the health check port equal to the port in `TARGET_CONTROL_DATA_ADDRESS` so an unhealthy agent fails the target out.
- ⚠️ **WebSockets are not supported** on target groups with Target Optimizer enabled.

Built for compute-bound work — LLM inference, video transcoding, heavy analytics — where queuing at the target destroys tail latency and `least_outstanding_requests` isn't a hard enough guarantee.

### 7.11 Lambda targets

- One function per target group; ALB invokes it synchronously with an ALB-shaped event.
- `lambda.multi_value_headers.enabled` controls array-vs-string header encoding.
- Not compatible with: IPv6 target groups, gRPC/HTTP2 protocol versions, target group health thresholds.
- Watch the ALB→Lambda response size limit (1 MB) and Lambda concurrency.

---

## 8. ALB Integrations

The console surfaces these under the load balancer's **Integrations** tab. AWS documents five first-class integrations, plus a wider ecosystem.

### 8.1 Documented "Integrations" tab

#### Amazon Application Recovery Controller (ARC) — Zonal Shift
Shift traffic away from an impaired AZ to healthy AZs in the same Region, reducing the blast radius of power, hardware, or software failures in one zone. Supports **zonal autoshift** (AWS-initiated on your behalf). Requires `zonal_shift.config.enabled`.

#### Amazon CloudFront + AWS WAF (one-click)
A single console action creates a CloudFront distribution with recommended AWS WAF protections and associates it with the ALB (Nov 2024). You get edge caching (honouring your `Cache-Control` headers), global reach, and inline WAF filtering, plus the **CloudFront security dashboard**.

Best practice pairing: restrict the ALB's security group to the CloudFront managed prefix list, and add a secret custom header at CloudFront that an ALB rule checks.

> ⚠️ CloudFront only supports ACM certificates in **us-east-1**. If your ALB's ACM cert lives elsewhere, either switch the CloudFront origin protocol to HTTP or provision a second cert in us-east-1 for the distribution.

#### AWS Global Accelerator
Creates an accelerator with **static anycast IPs** as fixed entry points, routing over the AWS backbone from the edge nearest the client. Includes AWS Shield Standard. Solves ALB's "no static IP" limitation for clients that require IP allow-listing.

#### AWS Config
Records ALB configuration state and relationships over time for audit, compliance, and drift detection.

#### AWS WAF
Associate a web ACL directly with the ALB (no CloudFront needed).

- **Fail-open behaviour:** by default, if the LB can't reach WAF it returns HTTP 500 and drops the request. `waf.fail_open.enabled = true` forwards instead. Choose deliberately — availability vs. security.
- **One-click WAF** (Feb 2024) creates a web ACL with three AWS managed rule groups:
  - `AWSManagedRulesAmazonIpReputationList` — blocks IPs associated with bots/threats.
  - `AWSManagedRulesCommonRuleSet` — OWASP Top 10-style core rule set.
  - `AWSManagedRulesKnownBadInputsRuleSet` — known-invalid exploit patterns.
- **WAF HTTP/2 traffic inspection behavior** — configured on the **target group** attributes page; controls when WAF inspects HTTP/2 request bodies. Affects both security coverage and compatibility with streaming/long-request patterns.

### 8.2 Compute & orchestration

| Service | Integration |
|---|---|
| **EC2 Auto Scaling** | Attach a target group to an ASG; instances auto-register on launch and auto-deregister on termination. |
| **Amazon ECS** | Service load balancing; `awsvpc` tasks register as `ip` targets. Supports blue/green and linear/canary deployment strategies with alternate target groups driven by a production listener rule. |
| **Amazon EKS** | **AWS Load Balancer Controller** provisions ALBs from `Ingress` resources or the **Gateway API**. `ListenerRuleConfiguration` CRD exposes conditions, actions, and transforms. |
| **AWS Lambda** | Direct `lambda` target type. |
| **AWS App Runner / Elastic Beanstalk** | Beanstalk provisions and manages ALBs for web tiers. |
| **AWS Outposts / Local Zones** | Deploy ALB on-prem or in metro Local Zones (with restrictions). |

### 8.3 Networking & delivery

| Service | Integration |
|---|---|
| **Route 53** | Alias records to the ALB DNS name; `EvaluateTargetHealth` uses target group health; failover routing policies. |
| **AWS PrivateLink (via NLB)** | Register an ALB as an NLB target (Sept 2021) to expose L7 routing through a VPC endpoint service, and to get static IPs. |
| **Amazon API Gateway (HTTP API)** | Private integration to an ALB listener via a VPC Link. |
| **AWS Transit Gateway / Direct Connect / VPN** | Register on-prem servers as `ip` targets. |

### 8.4 Security & identity

| Service | Integration |
|---|---|
| **AWS Certificate Manager** | Public/private certs with automatic renewal; SNI cert lists. |
| **Amazon Cognito** | `authenticate-cognito` action. |
| **Any OIDC IdP** | `authenticate-oidc` action; `jwt-validation` for M2M. |
| **AWS Private CA** | Issue client certs and build mTLS trust store bundles. |
| **AWS Shield Advanced** | DDoS protection with cost protection and DRT access. |
| **AWS Secrets Manager** | Store the OIDC client secret. |
| **IAM** | Resource-level permissions and tagging condition keys on load balancers, listeners, rules, and target groups (May 2018). |

### 8.5 Observability & delivery pipeline

| Service | Integration |
|---|---|
| **Amazon CloudWatch** | Metrics (`AWS/ApplicationELB`), alarms, dashboards. |
| **Amazon CloudWatch Logs** | **New July 23, 2026** — ALB access, connection, and health check logs supported as **vended logs**, delivered directly to CloudWatch Logs. Enables Logs Insights queries, metric filters, and Live Tail. Telemetry enablement rules can auto-configure logging org-wide. |
| **Amazon S3** | Access / connection / health check log delivery. |
| **Amazon Athena / OpenSearch** | Query archived logs. |
| **AWS CloudTrail** | ELB API call auditing. |
| **AWS X-Ray** | `X-Amzn-Trace-Id` request tracing. |
| **AWS CodeDeploy** | Blue/green EC2 and ECS deployments driven through ALB target groups. |
| **AWS CloudFormation / CDK / Terraform** | Full IaC coverage. Transforms landed in the Terraform AWS provider **v6.19.0**. |

---

## 9. Observability

### 9.1 CloudWatch metrics (`AWS/ApplicationELB`)

Metrics are emitted in 60-second intervals **only when requests are flowing**, and **exclude health check requests**.

**Load balancer metrics (selected):**

| Metric | Use |
|---|---|
| `RequestCount` | Volume. |
| `ActiveConnectionCount` / `NewConnectionCount` | Connection churn and concurrency. |
| `TargetResponseTime` | Backend latency; supports **percentile statistics** (p50/p90/p99). |
| `HTTPCode_ELB_4XX_Count` / `HTTPCode_ELB_5XX_Count` | Errors generated **by the LB**. |
| `HTTPCode_Target_2XX/3XX/4XX/5XX_Count` | Errors from **targets**. |
| `HTTPCode_ELB_502/503/504_Count` | 502 = bad gateway/target closed; 503 = no healthy targets; 504 = target timeout. |
| `TargetConnectionErrorCount` | LB→target connect failures. |
| `RejectedConnectionCount` | Hit the connection ceiling. |
| `ClientTLSNegotiationErrorCount` / `TargetTLSNegotiationErrorCount` | TLS problems. |
| `HTTP_Redirect_Count` / `HTTP_Fixed_Response_Count` | Rule action counters. |
| `ConsumedLCUs` / `PeakLCUs` / `ReservedLCUs` | Capacity. Use `PeakLCUs` for reservation sizing. |
| `ELBAuthSuccess` / `ELBAuthError` / `ELBAuthLatency` / `ELBAuthUserClaimsSizeExceeded` | OIDC/Cognito auth health. |
| `DesyncMitigationMode_NonCompliant_Request_Count` | Desync candidates. |
| `BYoIPUtilPercentage` | BYoIP pool usage. |

**Target group metrics:** `HealthyHostCount`, `UnHealthyHostCount`, `RequestCountPerTarget`, `TargetResponseTime`, plus target-group-health metrics (`UnhealthyRoutingRequestCount`, `HealthyStateDNS`, `HealthyStateRouting`).

### 9.2 Access logs

Per-request records to S3 (or now CloudWatch Logs). Includes timestamps, client IP/port, target IP/port, processing times, status codes, sent/received bytes, request line, user agent, TLS cipher/protocol, target group ARN, trace ID, matched rule ARN, and the action taken (including redirect/fixed-response).

S3 key format:
```
bucket[/prefix]/AWSLogs/{account}/elasticloadbalancing/{region}/{yyyy}/{mm}/{dd}/
  {account}_elasticloadbalancing_{region}_app.{lb-id}_{end-time}_{ip}_{random}.log.gz
```

Delivered every 5 minutes; eventually consistent; duplicates possible on high-traffic sites. Best-effort — not a billing-grade accounting of every request.

Since **September 10, 2025**, the modern bucket policy works in all Regions (the legacy pre-August-2022 policy still works).

### 9.3 Connection logs

Per-**connection** (not per-request) records: client IP/port, client certificate details, connection result, TLS cipher negotiated. Essential for debugging mTLS handshake failures and TLS negotiation errors, which never appear in access logs because the request never happened.

### 9.4 Health check logs

**Launched November 21, 2025.** Detailed per-health-check records to S3: status, timestamp, target identification, and **specific failure reasons**. Delivered every 5 minutes; no charge beyond S3 storage.

This closed a real gap — previously, "why exactly did this target flap?" often required an AWS Support case.

### 9.5 Request tracing

ALB injects `X-Amzn-Trace-Id` on every request. If the header already exists, ALB preserves the `Root=` value and appends its own `Self=`. Wire it into X-Ray or your APM.

---

## 10. Security Features

| Layer | Capability |
|---|---|
| **Network** | Security groups (mandatory), internal scheme, `deny_all_igw_traffic`, CloudFront prefix-list restriction. |
| **Transport** | TLS 1.2/1.3 policies, FIPS 140-3 policies, RFC 9151/CNSA 1.0 policies (Aug 2026), forward-secrecy policies, SNI, ACM-managed rotation. |
| **Client identity** | mTLS passthrough / verify with trust stores + CRLs. |
| **User identity** | `authenticate-oidc`, `authenticate-cognito`. |
| **Service identity** | `jwt-validation` (RS256, JWKS, `iss`/`exp` mandatory, `nbf`/`iat` if present, ≤10 extra claims). |
| **Application** | AWS WAF web ACL, fail-open toggle, managed rule groups, HTTP/2 body inspection behaviour. |
| **Protocol** | Desync mitigation (`monitor`/`defensive`/`strictest`), `drop_invalid_header_fields`. |
| **Response hardening** | HSTS, CSP, X-Frame-Options, X-Content-Type-Options, CORS via listener attributes. |
| **Access control** | IAM resource-level permissions + tag-based conditions on rules and target groups. |
| **Audit** | CloudTrail, AWS Config, access/connection/health check logs. |
| **DDoS** | Shield Standard by default; Shield Advanced optionally; Global Accelerator / CloudFront absorption. |

**Header size limits:** request line 16 K · single header 16 K · entire request header 64 K · entire response header 32 K. None adjustable.

---

## 11. Pricing & Capacity (LCUs)

ALB billing = **hourly charge** + **LCU-hours**.

An **LCU** measures four dimensions; you are billed on the **highest one consumed per hour**:

| Dimension | Per 1 LCU |
|---|---|
| **New connections** | 25 new connections/sec |
| **Active connections** | 3,000 active connections/min |
| **Processed bytes** | 1 GB/hour (EC2/containers/IP targets); 0.4 GB/hour for Lambda targets |
| **Rule evaluations** | 1,000 rule evaluations/sec (first 10 processed rules are free) |

Practical consequences:

- **Rule count affects cost.** Rule evaluations = request rate × (processed rules − 10). A 100-rule listener where most requests fall through to the default rule is far more expensive than a 10-rule listener. **Put your highest-volume rules at the lowest priority numbers.**
- Lambda targets consume LCUs 2.5× faster per byte.
- **LCU reservations** are billed for reserved capacity whether used or not, plus overage above the reservation. Terminate reservations when the event ends.
- Additional costs: public IPv4 addresses (avoidable with `dualstack-without-public-ipv4`), S3 log storage, CloudWatch Logs ingestion, WAF, Global Accelerator, cross-AZ data transfer (billing for inter-AZ transfer changed across 2025–2026 — verify current rates).

---

## 12. Quotas & Limits

### Load balancers
| Quota | Default | Adjustable |
|---|---|---|
| Application Load Balancers per Region | 50 | ✅ |
| Listeners per ALB | 50 | ✅ |
| Certificates per ALB (excluding default) | 25 | ✅ |
| Target Groups per ALB | 100 | ❌ |
| Target Groups per Action per ALB | 5 | ❌ |
| Targets per ALB | 1,000 | ✅ |

### Rules
| Quota | Default | Adjustable |
|---|---|---|
| **Rules per ALB (excluding default)** | **100** | ✅ |
| Condition Values per Rule | 5 | ❌ |
| Condition Wildcards per Rule | 6 * | ❌ |
| Match evaluations per rule | 5 | ❌ |
| Rule priority range | 1–50,000 | — |

\* The condition-types documentation states a limit of **five** wildcard characters per rule while the quotas table lists six. Plan for five.

### Target groups
| Quota | Default | Adjustable |
|---|---|---|
| Target Groups per Region | 3,000 (shared with NLB) | ✅ |
| Targets per Target Group per Region (instances/IPs) | 1,000 | ✅ |
| Targets per Target Group (Lambda) | 1 | ❌ |
| Load balancers per target group | 1 | ❌ |

### Trust stores / certificates (mTLS)
| Quota | Default | Adjustable |
|---|---|---|
| Trust stores per account | 20 | ✅ |
| Listeners using mTLS **verify** mode per LB | 2 | ❌ |
| CA certificates per trust store | 25 | ✅ |
| CA certificate size | 16 KB | ❌ |
| Max certificate chain depth | 4 | ❌ |
| Revocation lists per trust store | 30 | ✅ |
| Revocation entries per trust store | 500,000 | ✅ |
| Revocation list file size | 50 MB | ❌ |
| TLS message size | 64 K | ❌ |

### HTTP header sizes
Request line 16 K · single header 16 K · entire request header 64 K · entire response header 32 K. None adjustable.

### Capacity units
| Quota | Default | Adjustable |
|---|---|---|
| Reserved ALB LCUs per ALB | 15,000 | ✅ |
| Reserved ALB LCUs per Region | 0 (request to raise) | ✅ |
| Minimum reservation request | 100 LCU | — |

### JWT validation
- ≤10 additional claims; ≤10 values per array/space-separated claim.
- JWKS response ≤150 KB, ≤10 keys.
- `Issuer` and `JwksEndpoint` ≤256 chars.
- RS256 only.

---

## 13. Gotchas & Anti-Patterns

1. **`source-ip` behind a proxy.** It matches the immediate peer. Behind CloudFront/NAT/another LB, use an `http-header` condition on `X-Forwarded-For`.
2. **No NOT operator, no OR across condition types.** Conditions AND together. Express negation as a lower-priority catch-all rule.
3. **Weighted target groups don't fail over.** An empty or fully-unhealthy target group in a weighted forward will happily black-hole its share. Alarm on it.
4. **Path patterns are case-sensitive; host headers are not.** People trip on this constantly.
5. **`*.example.com` excludes `example.com`.** List the apex separately.
6. **Rules are evaluated after URI normalization.** Don't build security rules on unnormalized path assumptions.
7. **Transforms happen after WAF.** WAF sees the original URI. Rewrites don't launder input.
8. **No transforms on the default rule** and no conditions on it either.
9. **Redirect loops.** You must change protocol, host, port, or path.
10. **HTTPS → HTTP redirect is not allowed.**
11. **`HTTP_301` is cached hard by browsers.** Test with `302` first.
12. **Idle timeout mismatch → 502s.** Keep the app's keep-alive timeout above the ALB's (default 60s).
13. **HTTP/2 PING frames don't reset the idle timer.**
14. **Subnet IP exhaustion silently degrades scaling** into `active_impaired` with 5xx/timeouts. Size subnets generously.
15. **Rule count drives LCU cost.** Order rules by traffic volume, not by logical grouping.
16. **Target Optimizer breaks WebSockets** and can't be enabled after target group creation.
17. **WAF fail-open default is closed** — a WAF outage returns 500 unless you opt in.
18. **Reserved LCUs bill whether used or not**, and you can only decrease twice a day.
19. **DNS failover thresholds + NLB/Global Accelerator front-ends don't mix.** Explicitly documented as unsupported.
20. **Verify the `signer` field in `x-amzn-oidc-data`.** Trusting ALB-injected claims without signature verification is the CVE-2024-10125 pattern.
21. **App cookie names can't start with `AWSALB`, `AWSALBAPP`, or `AWSALBTG`.**
22. **URL-encoded stickiness cookie values are unsupported.**
23. **ED25519 certificate keys are unsupported.**
24. **X.509v1 client certs fail** against mTLS trust stores.
25. **Only 2 listeners per ALB can use mTLS verify mode.**
26. **gRPC/HTTP2 target groups only support `forward`** — no redirects, no fixed responses, no auth actions.
27. **Rule changes aren't instantaneous.** Brief windows of old-configuration routing are normal.
28. **CloudFront needs its ACM cert in us-east-1**, regardless of where the ALB lives.

---

## 14. Feature Timeline

| Date | Release |
|---|---|
| **Aug 4, 2026** | RFC 9151 / CNSA 1.0 compliant TLS security policies (ALB + NLB) |
| **Jul 23, 2026** | ALB access, connection, and health check logs as **CloudWatch Logs vended logs** |
| **Nov 21, 2025** | **Access token validation (`jwt-validation` action)** |
| **Nov 21, 2025** | **Health check logs** |
| **Nov 20, 2025** | **Target Optimizer** (max concurrent requests per target) |
| **Oct 15, 2025** | **Transforms** — URL rewrite and host header rewrite |
| Sep 10, 2025 | Modern S3 bucket policy for access/connection logs in all Regions |
| Feb 28, 2025 | HTTP header modification extended to **all** response codes |
| Nov 20, 2024 | **Capacity Unit (LCU) reservation** |
| Nov 15, 2024 | One-click **CloudFront + WAF** integration |
| May 16, 2024 | Dual-stack **without public IPv4** |
| Mar 8, 2024 | Resource map |
| Feb 6, 2024 | One-click WAF |
| Nov 26, 2023 | **Mutual TLS (mTLS)** |
| Nov 26, 2023 | **Automatic Target Weights** / anomaly mitigation |
| Nov 20, 2023 | FIPS 140-3 TLS termination policies |
| Oct 2, 2023 | Register instances addressed by IPv6 |
| Mar 22, 2023 | TLS 1.3 predefined security policies |
| Nov 28, 2022 | **Zonal shift** (ARC) |
| Nov 28, 2022 | **Target group health** thresholds |
| Nov 28, 2022 | Turn off cross-zone load balancing |
| Nov 17, 2022 | Cross-zone LB configurable at target group level |
| Nov 23, 2021 | IPv6 target groups; IPv6 internal load balancers |
| Sep 27, 2021 | **ALB as an NLB target** (PrivateLink + static IPs) |
| Jul 29, 2021 | Client port preservation |
| Jul 21, 2021 | TLS version/cipher headers |
| Jul 14, 2021 | RSA 3072/4096 and all ECDSA certificates |
| Feb 8, 2021 | Application-based stickiness |
| Nov 13, 2020 | WAF fail-open |
| Oct 29, 2020 | **gRPC and end-to-end HTTP/2** |
| Sep 8, 2020 | AWS Outposts support |
| Aug 17, 2020 | Desync mitigation mode |
| Nov 25, 2019 | Least outstanding requests |
| Nov 19, 2019 | **Weighted target groups** |
| Nov 15, 2019 | `drop_invalid_header_fields` |
| Mar 27, 2019 | **Advanced request routing** (header, method, query string, source IP conditions) |
| Nov 29, 2018 | **Lambda functions as targets** |
| Jul 25, 2018 | **Redirect and fixed-response actions** |
| May 30, 2018 | **User authentication (OIDC / Cognito)** |
| May 10, 2018 | Resource-level permissions and tagging conditions |
| Mar 24, 2018 | Slow start mode |
| Oct 10, 2017 | **SNI** |
| Aug 31, 2017 | IP addresses as targets |
| Apr 5, 2017 | **Host-based routing** (rule limit raised to 75) |
| Jan 25, 2017 | IPv6 |
| Nov 22, 2016 | Request tracing |
| **Aug 11, 2016** | **Application Load Balancer launches** |

---

## 15. IaC Reference Snippets

### 15.1 AWS CLI

**Create a rule with a forward action and host-header condition**
```bash
aws elbv2 create-rule \
  --listener-arn "$LISTENER_ARN" \
  --priority 10 \
  --conditions "Field=host-header,Values=example.com,www.example.com" \
  --actions "Type=forward,TargetGroupArn=$TG_ARN"
```

**Weighted forward (canary)**
```bash
aws elbv2 create-rule \
  --listener-arn "$LISTENER_ARN" --priority 20 \
  --conditions '[{"Field":"path-pattern","PathPatternConfig":{"Values":["/checkout/*"]}}]' \
  --actions '[{
    "Type":"forward",
    "ForwardConfig":{
      "TargetGroups":[
        {"TargetGroupArn":"'"$BLUE"'","Weight":90},
        {"TargetGroupArn":"'"$GREEN"'","Weight":10}],
      "TargetGroupStickinessConfig":{"Enabled":true,"DurationSeconds":3600}}}]'
```

**Fixed response gated on source IP**
```bash
aws elbv2 create-rule \
  --listener-arn "$LISTENER_ARN" --priority 1 \
  --conditions '[{"Field":"source-ip","SourceIpConfig":{"Values":["192.168.1.0/24","10.0.0.0/16"]}}]' \
  --actions "Type=fixed-response,FixedResponseConfig={StatusCode=403,ContentType=text/plain,MessageBody='Access denied'}"
```

**Rule with a URL rewrite transform**
```bash
aws elbv2 create-rule \
  --listener-arn "$LISTENER_ARN" --priority 30 \
  --conditions '[{"Field":"path-pattern","PathPatternConfig":{"RegexValues":["^\\/api\\/v1\\/(.*)$"]}}]' \
  --transforms '[{
    "Type":"url-rewrite",
    "UrlRewriteConfig":{"Rewrites":[{"Regex":"^/api/v1/(.*)$","Replace":"/$1"}]}}]' \
  --actions "Type=forward,TargetGroupArn=$TG_ARN"
```

**Reorder rules**
```bash
aws elbv2 set-rule-priorities \
  --rule-priorities RuleArn="$RULE_A",Priority=10 RuleArn="$RULE_B",Priority=20
```

**Listener response-header hardening**
```bash
aws elbv2 modify-listener-attributes \
  --listener-arn "$LISTENER_ARN" \
  --attributes \
    Key=routing.http.response.strict_transport_security.header_value,Value="max-age=31536000; includeSubDomains" \
    Key=routing.http.response.x_content_type_options.header_value,Value="nosniff" \
    Key=routing.http.response.x_frame_options.header_value,Value="SAMEORIGIN" \
    Key=routing.http.response.server.enabled,Value=false
```

### 15.2 CloudFormation

```yaml
Resources:
  MyForwardRule:
    Type: AWS::ElasticLoadBalancingV2::ListenerRule
    Properties:
      ListenerArn: !Ref MyListener
      Priority: 10
      Conditions:
        - Field: host-header
          Values: [example.com, www.example.com]
      Actions:
        - Type: forward
          TargetGroupArn: !Ref MyTargetGroup
      Tags:
        - { Key: Name,  Value: apex-and-www }
        - { Key: team,  Value: platform }

  MyMobileRedirect:
    Type: AWS::ElasticLoadBalancingV2::ListenerRule
    Properties:
      ListenerArn: !Ref MyListener
      Priority: 30
      Conditions:
        - Field: http-header
          HttpHeaderConfig:
            HttpHeaderName: User-Agent
            Values: ["*Mobile*", "*Android*", "*iPhone*"]
      Actions:
        - Type: redirect
          RedirectConfig:
            Host: m.example.com
            StatusCode: HTTP_302

  MyLoadBalancer:
    Type: AWS::ElasticLoadBalancingV2::LoadBalancer
    Properties:
      Name: my-alb
      Type: application
      Scheme: internal
      Subnets: [!Ref SubnetAZ1, !Ref SubnetAZ2]
      SecurityGroups: [!Ref MySecurityGroup]
      MinimumLoadBalancerCapacity:
        CapacityUnits: 3000
```

> Note: `Transforms` on `AWS::ElasticLoadBalancingV2::ListenerRule` lagged the API launch. Verify current CloudFormation coverage before committing; the CLI/SDK path has supported transforms since October 2025.

### 15.3 Terraform

```hcl
resource "aws_lb_listener_rule" "api_v2_rewrite" {
  listener_arn = aws_lb_listener.https.arn
  priority     = 30

  condition {
    path_pattern { values = ["/api/v2/*"] }
  }

  # requires AWS provider >= 6.19.0
  transform {
    type = "url-rewrite"
    url_rewrite_config {
      rewrites {
        regex   = "^/api/v2/(.*)$"
        replace = "/$1"
      }
    }
  }

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.api_v2.arn
  }

  tags = {
    Name = "api-v2-strip-prefix"
    team = "platform"
  }
}

resource "aws_lb_listener_rule" "canary" {
  listener_arn = aws_lb_listener.https.arn
  priority     = 10

  condition {
    http_header {
      http_header_name = "X-Canary"
      values           = ["true"]
    }
  }

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.green.arn
  }

  tags = { Name = "canary-optin-header" }
}
```

---

## Further Reading

- ALB User Guide — <https://docs.aws.amazon.com/elasticloadbalancing/latest/application/>
- Condition types — <https://docs.aws.amazon.com/elasticloadbalancing/latest/application/rule-condition-types.html>
- Action types — <https://docs.aws.amazon.com/elasticloadbalancing/latest/application/rule-action-types.html>
- Transforms — <https://docs.aws.amazon.com/elasticloadbalancing/latest/application/rule-transforms.html>
- Integrations — <https://docs.aws.amazon.com/elasticloadbalancing/latest/application/load-balancer-integrations.html>
- JWT verification — <https://docs.aws.amazon.com/elasticloadbalancing/latest/application/listener-verify-jwt.html>
- Quotas — <https://docs.aws.amazon.com/elasticloadbalancing/latest/application/load-balancer-limits.html>
- Document history — <https://docs.aws.amazon.com/elasticloadbalancing/latest/application/doc-history.html>
- Advanced request routing demo — <https://exampleloadbalancer.com/advanced_request_routing_demo.html>
