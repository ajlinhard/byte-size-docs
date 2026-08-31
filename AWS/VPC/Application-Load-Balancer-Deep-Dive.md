# AWS Application Load Balancer (ALB) — A Thorough Breakdown

*Current as of August 2026. Feature dates cited from the ELB documentation history and AWS "What's New" announcements.*

---

## Table of Contents

1. [High-Level: What an ALB Actually Is](#1-high-level-what-an-alb-actually-is)
2. [Vocabulary and Features](#2-vocabulary-and-features)
3. [Common Configuration Patterns with Other Services](#3-common-configuration-patterns-with-other-services)
4. [Security Configurations](#4-security-configurations)
5. [Common Mistakes](#5-common-mistakes)
6. [Quick Reference Tables](#6-quick-reference-tables)

---

## 1. High-Level: What an ALB Actually Is

An Application Load Balancer is a **fully managed, horizontally-scaling Layer 7 reverse proxy** in the Elastic Load Balancing (ELB) family. It terminates client connections, parses HTTP semantics, decides where each *request* should go, and opens (or reuses) a separate connection to a backend target.

The critical mental model: **an ALB is not a network appliance that forwards packets.** It is a proxy that speaks HTTP. Every request is parsed, evaluated against rules, potentially rewritten, and re-issued. This is why ALBs can route on paths and headers, and also why they can't preserve the client's source IP at the TCP level (you get `X-Forwarded-For` instead), can't give you a static IP, and add a small amount of latency compared to an NLB.

### The request lifecycle

```
Client
  │  1. DNS resolves the ALB's name to node IPs (multiple, per-AZ, rotating)
  ▼
ALB node in AZ-a ──────────────────────────────────────────┐
  │  2. TCP connect + TLS handshake (server cert via SNI)   │
  │  3. Optional mTLS client cert verification              │  All of this
  │  4. HTTP request parsed; desync guardian inspects       │  happens inside
  │  5. Listener rules evaluated in priority order          │  the load
  │  6. Pre-routing action (auth / JWT validation) runs     │  balancer
  │  7. Transforms rewrite host header / URL                │
  │  8. Routing action: forward | redirect | fixed-response │
  │  9. Target selected from target group by algorithm      │
  ▼                                                          │
Target (EC2 / ECS task / EKS pod / IP / Lambda / other ALB) ─┘
```

Two important consequences of step 5–9:

- **Rules match on the *original* request.** Transforms happen after the routing decision, so rewriting a path does not re-trigger rule evaluation.
- **The first matching rule wins.** Rules are evaluated lowest priority number first; the default rule always runs last.

### Where the ALB sits relative to its siblings

| Need | Use |
|---|---|
| HTTP/HTTPS routing on paths, hosts, headers, methods, query strings | **ALB** |
| gRPC, WebSockets, HTTP/2 to targets | **ALB** |
| Native OIDC/Cognito login, or JWT validation at the edge | **ALB** |
| Raw TCP/UDP/TLS, static IPs, extreme connection rates, ultra-low latency | **NLB** |
| Transparent insertion of third-party firewalls/IDS appliances | **Gateway Load Balancer** |
| Global caching, edge TLS, DDoS absorption in front of the region | **CloudFront** (usually *with* an ALB behind it) |
| Full API management: usage plans, per-key throttling, request/response mapping | **API Gateway** |
| Service-to-service mesh routing inside/between VPCs without an internet path | **VPC Lattice** |

An ALB is regional and AZ-aware: it places a node (an ENI) in each enabled subnet, and its DNS name resolves to addresses across those AZs. **You must enable at least two Availability Zones.**

### Pricing model in one paragraph

You pay an hourly rate per ALB plus **Load Balancer Capacity Units (LCUs)**. An LCU measures four dimensions, averaged hourly, and **you're billed only on the highest one**:

| Dimension | Included per LCU |
|---|---|
| New connections | 25 / second |
| Active connections | 3,000 / minute (**1,500 with mTLS**) |
| Processed bytes | 1 GB / hour (0.4 GB/hr for Lambda targets) |
| Rule evaluations | 1,000 / second — **first 10 rules per request are free** |

This is why LCU cost is workload-shaped: a media site bills on processed bytes, a chatty API on new connections, and a heavily-ruled multi-tenant ALB on rule evaluations. Note that mTLS also inflates processed bytes, since the certificate metadata inserted into headers counts toward the byte total.

---

## 2. Vocabulary and Features

### 2.1 The load balancer object

| Term | Meaning |
|---|---|
| **Scheme** | `internet-facing` (public IPs on the nodes, resolvable publicly) or `internal` (private IPs only). Cannot be changed after creation. |
| **Subnets / AZs** | Minimum two AZs. ALB places an ENI in each enabled subnet; needs at least 8 free IPs per subnet (`/28` minimum, `/27` recommended) to allow for scaling. |
| **Security groups** | Unlike an NLB, an ALB *always* has security groups. Applies to both inbound client traffic and outbound traffic to targets. |
| **DNS name** | `name-hash.region.elb.amazonaws.com`. **The IPs behind it change.** Never hardcode them. Resolve fresh; honor the DNS TTL (60s). |
| **IP address type** | `ipv4`, `dualstack`, or `dualstack-without-public-ipv4` (IPv6-only for clients, launched May 2024 — avoids public IPv4 charges while still using private IPv4 to targets). |
| **IPAM pools** | You can source the ALB's public IPv4 addresses from an Amazon VPC IPAM pool (including BYOIP ranges) instead of the AWS pool. ALB-managed IPs don't count against your EIP quota. |
| **Deletion protection** | `deletion_protection.enabled` — blocks accidental `delete-load-balancer`. On by default in no configuration; turn it on for anything production. |
| **Idle timeout** | `idle_timeout.timeout_seconds`, default **60s**, range 1–4000. Applies to both front-end and back-end connections. |
| **LCU reservation** | Set a guaranteed minimum capacity (Nov 2024). Replaces the old "open a support case to pre-warm" workflow. Useful for ticket drops, product launches, migrations. |

**Load balancer attributes worth knowing** (set via `modify-load-balancer-attributes`):

```
routing.http.desync_mitigation_mode              monitor | defensive | strictest   (default: defensive)
routing.http.drop_invalid_header_fields.enabled  true | false                       (default: false)
routing.http.preserve_host_header.enabled        true | false                       (default: false)
routing.http.xff_header_processing.mode          append | preserve | remove         (default: append)
routing.http.xff_client_port.enabled             true | false                       (default: false)
routing.http.x_amzn_tls_version_and_cipher_suite.enabled
routing.http.response.server.enabled             true | false   (suppress "server: awselb/2.0")
routing.http2.enabled                            true | false                       (default: true)
waf.fail_open.enabled                            true | false                       (default: false)
access_logs.s3.enabled / .bucket / .prefix
connection_logs.s3.enabled / .bucket / .prefix
zonal_shift.config.enabled
```

### 2.2 Listeners

A **listener** is a protocol + port the ALB accepts connections on (HTTP or HTTPS). Without at least one listener, the ALB accepts nothing.

**HTTPS listeners** additionally carry:

- **Certificates.** One default certificate plus up to 25 additional (adjustable). Multiple certs are selected by **SNI**. ACM-issued or imported; RSA 2048/3072/4096 and all ECDSA sizes supported.
- **Security policy.** The TLS version + cipher suite set. Options include TLS 1.3 policies (Mar 2023), forward-secrecy policies, FIPS 140-3 policies (Nov 2023), and **RFC 9151 / CNSA 1.0 policies (Aug 2026)** for US national-security requirements.
- **Mutual TLS (mTLS).** See §2.6.

**Listener attributes** let you inject security response headers and rename mTLS headers, e.g.:

```
routing.http.response.hsts.header_value
routing.http.response.x_frame_options.header_value
routing.http.response.content_security_policy.header_value
routing.http.request.x_amzn_mtls_clientcert_subject.header_name
```

HTTP header modification was extended to **all response codes** in February 2025 (previously 2xx/3xx only).

### 2.3 Rules: conditions → transforms → actions

Every listener has a **default rule** (no conditions, always last, cannot be deleted). Additional rules have a **priority** (1–50000, unique per listener), one or more **conditions**, optional **transforms**, and one or more **actions**.

#### Conditions

| Condition | Cardinality per rule | Notes |
|---|---|---|
| `host-header` | 0 or 1 | Wildcards `*` `?`; **regex supported** since Oct 2025 |
| `path-pattern` | 0 or 1 | Matches path only — *not* the query string; regex supported |
| `http-request-method` | 0 or 1 | `GET`, `POST`, custom methods |
| `source-ip` | 0 or 1 | CIDR. **Uses the actual TCP source IP, not `X-Forwarded-For`** |
| `http-header` | 0 or more | Any header name; regex supported |
| `query-string` | 0 or more | Key/value pairs or bare values |

All conditions on a rule are ANDed. Values within a condition are ORed. **Limits: 5 condition values per rule, 6 wildcards per rule, 5 match evaluations per rule.**

#### Transforms (launched October 2025)

Transforms rewrite the request *after* the routing decision, before it reaches the target. This eliminated the single most common reason teams put an NGINX/Envoy sidecar in front of their app.

| Type | What it does |
|---|---|
| `host-header-rewrite` | Regex match + replace on the Host header |
| `url-rewrite` | Regex match + replace on path and/or query string |

```json
[
  {
    "Type": "url-rewrite",
    "UrlRewriteConfig": {
      "Rewrites": [
        { "Regex": "^/api/v1/(.*)$", "Replace": "/$1" }
      ]
    }
  }
]
```

Rules of the road:
- One host-header-rewrite and one url-rewrite per rule, max.
- **Cannot be added to the default rule.**
- No pattern match → the original request is forwarded unchanged.
- Pattern matches but the transform fails → the ALB returns **HTTP 500**.
- You can change path and query string only — **not protocol or port**.
- Rewriting does not re-evaluate rules.

#### Actions

| Action | Notes |
|---|---|
| `forward` | To one target group, or several with **weights** (canary/blue-green). Max 5 target groups per action. |
| `redirect` | HTTP 301/302 with variable substitution: `#{protocol}`, `#{host}`, `#{port}`, `#{path}`, `#{query}` |
| `fixed-response` | Return a 2xx/4xx/5xx with a body, no target needed. Great as a default-deny. |
| `authenticate-oidc` | HTTPS listeners only. Browser redirect flow against any OIDC IdP. |
| `authenticate-cognito` | HTTPS listeners only. Cognito user pool flow. |
| `jwt-validation` | HTTPS listeners only. Validate a bearer JWT (Nov 2025). |

**Structural rule:** exactly one of `forward` / `redirect` / `fixed-response`, and it must be last. An authentication or JWT-validation action may precede it. `gRPC` and `HTTP/2` protocol-version target groups support **forward actions only**.

### 2.4 Target groups

| Target type | Registered as | Notes |
|---|---|---|
| `instance` | EC2 instance ID | ALB routes to the instance's primary private IP |
| `ip` | IP address | VPC CIDRs, RFC 1918 space, or on-prem via VPN/DX. Required for Fargate (`awsvpc`). |
| `lambda` | Function ARN | Max 1 function per target group. Sync invocation. |
| `alb` | Another ALB's ARN | Used when an NLB fronts an ALB (see §3.7) |

**Protocol version:** `HTTP1` (default), `HTTP2`, or `GRPC`. This governs the ALB→target leg. Front-end HTTP/2 is on by default and is downgraded to HTTP/1.1 to targets unless you choose `HTTP2`/`GRPC`.

**Routing algorithms** (`load_balancing.algorithm.type`):

| Algorithm | Best for | Restrictions |
|---|---|---|
| `round_robin` (default) | Uniform, short requests | — |
| `least_outstanding_requests` | Variable request cost, long-lived requests, WebSockets | **Cannot use slow start** |
| `weighted_random` | Enabling ATW anomaly mitigation | **Cannot use slow start or sticky sessions** |

**Automatic Target Weights (ATW)** — Nov 2023. Anomaly *detection* is always on for HTTP/HTTPS target groups with ≥3 healthy targets and cannot be disabled; it watches for targets returning a disproportionate share of 5xx / TCP / TLS errors — the "gray failure" case where a target passes health checks but is actually broken. Anomaly *mitigation* (reducing traffic to those targets, re-evaluated roughly every 5 seconds) requires `weighted_random` and `load_balancing.algorithm.anomaly_mitigation=on`. Not supported for Lambda targets.

**Key target group attributes:**

```
deregistration_delay.timeout_seconds           0–3600, default 300
slow_start.duration_seconds                    30–900, default 0 (off)
stickiness.enabled / stickiness.type           lb_cookie (AWSALB) | app_cookie (AWSALBAPP)
stickiness.app_cookie.cookie_name              cannot start with AWSALB, AWSALBAPP, AWSALBTG
load_balancing.cross_zone.enabled              true | false | use_load_balancer_configuration
target_group_health.dns_failover.minimum_healthy_targets.count / .percentage
target_group_health.unhealthy_state_routing.minimum_healthy_targets.count / .percentage
```

**Target group health** (Nov 2022) is underused and valuable. It lets you say: *if fewer than N (or N%) of targets in a zone are healthy, mark the zone unhealthy in DNS* (DNS failover), and *if fewer than N are healthy overall, start distributing across all targets including unhealthy ones rather than hammering the survivors* (unhealthy-state routing). This is the difference between a graceful partial degradation and a cascading failure where the last two healthy hosts get 100% of traffic and die.

**Target Optimizer** (Nov 2025) is the newest addition: it enforces a **maximum concurrent request count per target**. You create the target group with a *target control port* and run an AWS-provided agent on the targets that reports concurrency. For inference or heavy data-processing workloads where a target can genuinely only handle one request at a time, this replaces a lot of homegrown queueing. It consumes more LCUs than a normal target group.

### 2.5 Health checks

Per target group. Configurable protocol, path, port (`traffic-port` or an override), interval, timeout, healthy/unhealthy thresholds, and success matcher.

- HTTP/HTTPS default matcher: `200`. Range 200–499.
- Lambda targets: 200–499, default 200.
- gRPC default path: `/AWS.ALB/healthcheck`; matcher is gRPC status codes (default `12`).
- Health checks originate from the ALB's ENIs and must be allowed by the target's security group.

### 2.6 Authentication and identity features

This is where ALB has grown the most, and where the vocabulary gets confusing because there are now **three distinct mechanisms**.

#### (a) `authenticate-oidc` / `authenticate-cognito` — for humans

Browser-based redirect flow. The ALB handles the authorization-code exchange, sets a session cookie (`AWSELBAuthSessionCookie`), and injects three headers into the request to your target:

| Header | Signed? | Contents |
|---|---|---|
| `x-amzn-oidc-data` | **Yes** (JWT, signed by the ALB) | User claims |
| `x-amzn-oidc-accesstoken` | No — plaintext | Raw access token from the IdP |
| `x-amzn-oidc-identity` | No — plaintext | `sub` from the userinfo endpoint |

> **Security-critical:** Only `x-amzn-oidc-data` is signed. Your application **must** verify its signature *and* confirm the `signer` field in the JWT header equals your ALB's ARN before trusting any claim. Failing to check `signer` is exactly the flaw behind **CVE-2024-10125** — if targets are also reachable from the internet, an attacker can present a self-signed JWT and impersonate a federated session. Use `aws-jwt-verify`'s `AlbJwtVerifier` (or the equivalent) rather than hand-rolling this.
>
> Also note: ALB's OIDC JWTs are **not spec-compliant** — they include base64 padding. Many standard JWT libraries decode them successfully but then re-encode without padding before signature verification, which fails. If you're seeing mystifying signature errors, this is usually why.

Session timeout interacts with IdP session timeout: whichever is shorter wins from the user's perspective, and authorization codes are single-use even when no re-login prompt is shown.

#### (b) `jwt-validation` — for machines (Nov 2025)

Native JWT verification for service-to-service and machine-to-machine calls, aimed at OAuth 2.0 **client-credentials flow**. The ALB fetches the IdP's public keys from a JWKS endpoint you configure and validates the token in the request header.

| Property | Value |
|---|---|
| Listener requirement | **HTTPS only** |
| Signing algorithm | **RS256 only** |
| Mandatory claims validated | `iss`, `exp` |
| Validated if present | `nbf`, `iat` |
| Additional claims | Up to **10**, in three formats: single string, string array (max 10 values), space-separated values (max 10 values) |
| On success | Request forwarded **with the token unchanged** |
| On failure | Request rejected |

CLI shape:

```json
[
  {
    "Type": "jwt-validation",
    "JwtValidationConfig": {
      "JwksEndpoint": "https://issuer.example.com/.well-known/jwks.json",
      "Issuer": "https://issuer.example.com",
      "AdditionalClaims": [
        { "Name": "scope", "Format": "space-separated", "Values": ["orders:read"] }
      ]
    }
  },
  { "Type": "forward", "TargetGroupArn": "arn:aws:elasticloadbalancing:..." }
]
```

Two known rough edges from early adopters: the `iss` claim must match your configured issuer **exactly** (trailing slashes matter), and intermittent `JWTValidationInternalError` / `JWKSRequestFailed` failures have been reported — one widely-documented case traced to the presence of an `Accept-Encoding` header. Enable access logs and check the failure reason field before debugging your application.

#### (c) Mutual TLS — for certificate-based identity (Nov 2023)

Two modes on an HTTPS listener:

| Mode | ALB behavior | Who validates |
|---|---|---|
| **passthrough** | Accepts any client cert, forwards the full chain in `X-Amzn-Mtls-Clientcert` (URL-encoded PEM) | Your application |
| **verify** | Performs X.509 client cert authentication during the handshake against a **trust store**; rejects untrusted clients at the edge | The ALB |

In verify mode you create a **trust store** resource holding a CA bundle (from AWS Private CA, ACM, or your own CA) and optionally **CRLs stored in S3**, which the ALB imports rather than fetching per-request. Options include `advertise_trust_store_ca_names` (send CA names in the handshake so clients can pick the right cert) and `ignore_client_certificate_expiry`.

Headers passed to targets include `X-Amzn-Mtls-Clientcert`, `-Clientcert-Leaf`, `-Clientcert-Subject`, `-Clientcert-Issuer`, `-Clientcert-Serial-Number`, and `-Clientcert-Validity`. All are renameable via listener attributes.

Connection logs surface mTLS failure reasons: `ClientCertUntrusted`, `ClientCertExpired`, `ClientCertNotYetValid`, `ClientCertPurposeInvalid`.

**Important limitation:** mTLS is a **listener-level** setting. You cannot require client certs on `/admin` but not on `/public` within one listener. Use two domains/listeners, or passthrough plus in-app enforcement.

### 2.7 Observability

| Source | What it gives you |
|---|---|
| **Access logs** | Per-request: client IP/port, target, processing times, status codes, rule ARN, TLS version/cipher, `actions_executed`, error reason codes. **Free to S3**; disabled by default. |
| **Connection logs** | Per-connection TLS handshake detail — invaluable for mTLS and TLS negotiation debugging. |
| **CloudWatch Logs (vended)** | As of **July 2026**, ALB access, connection, and health-check logs can be delivered directly to CloudWatch Logs, queryable with Logs Insights, usable with metric filters and Live Tail. Also supports Firehose, and S3 with Parquet conversion. Org-wide telemetry enablement rules can auto-configure logging on new ALBs. |
| **CloudWatch metrics** | `RequestCount`, `TargetResponseTime` (percentiles supported), `HTTPCode_ELB_5XX_Count` vs `HTTPCode_Target_5XX_Count`, `RejectedConnectionCount`, `TargetConnectionErrorCount`, `UnHealthyHostCount`, `ConsumedLCUs`, `PeakLCUs`, `ActiveConnectionCount`, `ClientTLSNegotiationErrorCount` |
| **Request tracing** | `X-Amzn-Trace-Id` injected on every request; propagates to X-Ray. |
| **Resource map** | Console visualization of LB → listener → rule → target group → targets (Mar 2024). Fastest way to answer "why is this request going there?" |

The single most useful metric distinction: **`HTTPCode_ELB_5XX_Count` means the ALB generated the error** (no healthy targets, request timeout, rule failure). **`HTTPCode_Target_5XX_Count` means your app did.** Alarming on the combined total conflates two very different incidents.

### 2.8 Resilience features

- **Cross-zone load balancing**: on by default for ALB; can be turned off at the LB or per target group (Nov 2022). Turning it off keeps traffic zonal (better for AZ-isolation architectures) but requires even capacity per AZ.
- **Zonal shift / zonal autoshift**: via Amazon Application Recovery Controller, drain traffic away from a single impaired AZ with one API call. Requires `zonal_shift.config.enabled`.
- **Slow start**: linearly ramp traffic to newly healthy targets over 30–900s. Round-robin only.
- **Deregistration delay (connection draining)**: default 300s. If a target closes connections before the delay elapses, clients see 5xx.

---

## 3. Common Configuration Patterns with Other Services

### 3.1 ALB + ECS / Fargate

The canonical container pattern.

- **Fargate (`awsvpc` mode) requires `target-type: ip`.** EC2 launch type with `awsvpc` also requires `ip`; only `bridge`/`host` networking uses `instance`.
- ECS registers and deregisters tasks with the target group automatically as the service scales. It also honors the deregistration delay during rolling deploys — set it *shorter* than your ECS deployment's stop timeout, or deploys crawl.
- ECS's `healthCheckGracePeriodSeconds` must exceed your app's cold start, or ECS will kill tasks that are still booting because the ALB reports them unhealthy.
- **Blue/green with CodeDeploy** uses two target groups on one listener (or a production + test listener) and swaps them atomically.

### 3.2 ALB + EKS

Managed by the **AWS Load Balancer Controller**, which watches `Ingress` (or Gateway API `HTTPRoute`) resources and provisions ALBs.

```yaml
metadata:
  annotations:
    alb.ingress.kubernetes.io/scheme: internal
    alb.ingress.kubernetes.io/target-type: ip
    alb.ingress.kubernetes.io/listen-ports: '[{"HTTPS":443}]'
    alb.ingress.kubernetes.io/ssl-redirect: "443"
    alb.ingress.kubernetes.io/group.name: shared-prod   # share one ALB across Ingresses
    alb.ingress.kubernetes.io/transforms.api-service: >
      [{ "type": "url-rewrite",
         "urlRewriteConfig": { "rewrites": [{ "regex": "^/api/(.+)$", "replace": "/$1" }] } }]
```

- **`group.name` is the key cost lever.** Without it, every Ingress creates its own ALB (~$22/month base each, plus per-AZ public IPs). Grouping consolidates them onto one ALB, but the 100-rule quota then becomes your real ceiling.
- Native `transforms` support (2025) removed the need for an NGINX ingress sidecar in most path-stripping cases.
- Use `target-type: ip` to route directly to pod IPs, skipping the kube-proxy hop.

### 3.3 ALB + EC2 Auto Scaling

Attach the ASG to the target group. ASG registers new instances and deregisters terminating ones automatically. Two settings that matter:

- **ELB health check type** on the ASG (not just EC2 status checks) — otherwise a hung web server that still passes EC2 status checks never gets replaced.
- **Health check grace period** long enough for user-data/bootstrapping.

### 3.4 ALB + Lambda

Register a function as a target for lightweight HTTP endpoints without API Gateway. One function per target group. The ALB synchronously invokes the function with a specific event shape and expects `statusCode`, `headers`, `body`, `isBase64Encoded` back. Cheaper than API Gateway at volume; lacks usage plans, request validation, and per-key throttling. Note the smaller LCU allowance (0.4 GB/hr processed bytes) and that ATW doesn't apply.

### 3.5 ALB + CloudFront (+ WAF) — the front-door pattern

Three generations of this pattern, in ascending order of security:

1. **Public ALB, security group open to the world.** CloudFront in front for caching. Anyone who finds the ALB DNS name bypasses CloudFront, WAF, geo-restrictions, and rate limiting entirely. **Don't do this.**
2. **Public ALB restricted to the `com.amazonaws.global.cloudfront.origin-facing` managed prefix list**, plus a secret custom origin header validated by an ALB listener rule. Better — but the prefix list is shared by *all* CloudFront customers, so the secret header is doing the real work, and you now own rotating it.
3. **CloudFront VPC Origins (Nov 2024)** — the current best practice. CloudFront reaches an **internal** ALB in a private subnet through an AWS-managed connection. No public IP, no prefix list maintenance, no shared secret, and origin bypass becomes structurally impossible. Cross-account VPC origins via RAM landed Nov 2025; WebSocket support May 2026.

There is also a **one-click CloudFront + WAF integration** from the ALB console (Nov 2024) that provisions the distribution, a baseline WAF WebACL, and optionally a security group limited to CloudFront.

Certificate gotcha: the CloudFront viewer certificate must be in **ACM us-east-1**; the ALB's certificate must be in the ALB's own region.

### 3.6 ALB + AWS WAF

Attach a WebACL directly to the ALB. Behavioral notes:

- `waf.fail_open.enabled` (default `false`) controls what happens if the ALB can't reach WAF: `false` = fail closed (reject), `true` = forward anyway. Fail-closed is the safe default; only flip it if availability genuinely outranks inspection for that workload.
- **WAF inspects after ALB rule evaluation, including transforms.** If you rewrite `/api/v1/x` → `/x`, WAF sampled requests show the rewritten path. Rules that inspect URI paths must account for this — or place WAF on CloudFront so it inspects the original request.
- WAF processing consumes additional ALB capacity, which affects LCU scaling.

### 3.7 NLB → ALB (static IPs and PrivateLink)

An ALB can be a target of an NLB (target type `alb`, Sept 2021). This gives you:
- **Static IPs / Elastic IPs** in front of Layer 7 routing.
- **AWS PrivateLink** exposure — VPC endpoint services require an NLB or GWLB, so this is how you offer an HTTP-routing SaaS endpoint privately to consumers.

Cost: an extra hop and an extra load balancer. Quota note: an ALB registered as an NLB target counts as 50 targets (100 if cross-zone is enabled).

### 3.8 ALB + Route 53

Always use an **alias A/AAAA record** pointing at the ALB, never a CNAME to the DNS name and never an IP. Alias records are free, resolve at the zone apex (which CNAMEs can't), and track the ALB's changing IPs. Combine with health checks for regional failover, or use **Global Accelerator** in front of ALBs in multiple regions for anycast entry points and faster failover than DNS.

### 3.9 ALB + API Gateway / private APIs

An ALB with mTLS verify mode in front of a **private** API Gateway (via a VPC endpoint) gives you certificate-based client authentication that API Gateway's own mTLS can't do for private endpoints. Pair with an API Gateway resource policy allowing only the VPC endpoint, and a security group on the endpoint allowing only the ALB — otherwise clients can bypass mTLS by hitting the endpoint directly.

### 3.10 Canary and progressive delivery

Weighted target groups (Nov 2019) let one forward action split traffic across up to 5 target groups by weight:

```bash
aws elbv2 modify-rule --rule-arn "$RULE" --actions '[{
  "Type": "forward",
  "ForwardConfig": {
    "TargetGroups": [
      {"TargetGroupArn": "'"$TG_V1"'", "Weight": 95},
      {"TargetGroupArn": "'"$TG_V2"'", "Weight": 5}
    ],
    "TargetGroupStickinessConfig": {"Enabled": true, "DurationSeconds": 3600}
  }
}]'
```

Enable `TargetGroupStickinessConfig` for canaries, or a user will bounce between v1 and v2 across requests and your per-session metrics become meaningless. Note that ATW anomaly mitigation operates *within* a target group and will not pull traffic off a canary group that is uniformly bad — that's your CloudWatch-driven automation's job.

---

## 4. Security Configurations

### 4.1 Transport security

```bash
# HTTP listener that only redirects
aws elbv2 create-listener --load-balancer-arn "$ALB" --protocol HTTP --port 80 \
  --default-actions '[{
    "Type": "redirect",
    "RedirectConfig": {"Protocol":"HTTPS","Port":"443","StatusCode":"HTTP_301"}
  }]'

# HTTPS listener with a modern policy
aws elbv2 create-listener --load-balancer-arn "$ALB" --protocol HTTPS --port 443 \
  --certificates CertificateArn="$CERT" \
  --ssl-policy ELBSecurityPolicy-TLS13-1-2-Res-2021-06 \
  --default-actions '[{"Type":"forward","TargetGroupArn":"'"$TG"'"}]'
```

- Prefer a **TLS 1.3 policy**; require TLS 1.2 as the floor. `ELBSecurityPolicy-2016-08` (the console default in many wizards) still permits TLS 1.0/1.1.
- Use **FIPS 140-3 policies** where required; **RFC 9151 / CNSA 1.0 policies** (Aug 2026) for NSA CNSA compliance, with interoperability variants for gradual client migration.
- ACM certificates auto-renew *only if* validation still resolves — a deleted CNAME validation record silently breaks renewal months before expiry.
- Backend encryption: an HTTPS target group encrypts ALB→target. The ALB **does not validate the target's certificate**, so self-signed certs are fine there.

### 4.2 Request-smuggling and header hygiene

```bash
aws elbv2 modify-load-balancer-attributes --load-balancer-arn "$ALB" --attributes \
  Key=routing.http.desync_mitigation_mode,Value=strictest \
  Key=routing.http.drop_invalid_header_fields.enabled,Value=true \
  Key=routing.http.response.server.enabled,Value=false \
  Key=deletion_protection.enabled,Value=true
```

- **Desync mitigation** uses the open-source `http_desync_guardian` library. `defensive` is the default; `strictest` rejects anything RFC-ambiguous. Test `strictest` in staging — legacy clients that send non-compliant requests will break, which is the point, but it should be a decision rather than a surprise.
- **`drop_invalid_header_fields.enabled` defaults to `false`**, meaning headers with characters outside `[-A-Za-z0-9]` are forwarded to targets as-is. AWS Security Hub, AWS Config (`alb-http-drop-invalid-header-enabled`), and most CSPM tools flag this. Set it to `true`.
- These two attributes overlap; you don't need both, but enabling both is the conservative choice.

### 4.3 Client IP and header spoofing

The ALB *appends* to `X-Forwarded-For` by default. It does **not** sanitize an incoming XFF header — a client can send `X-Forwarded-For: 1.2.3.4` and the ALB will append the real IP, producing `1.2.3.4, <real-ip>`.

- If your app takes the **first** XFF entry as the client IP, an attacker controls it. Take the **rightmost untrusted** entry, or count back a known number of hops.
- `routing.http.xff_header_processing.mode=remove` strips it entirely; `preserve` passes it through unchanged (only safe when a trusted proxy sits in front); `append` is the default.
- The `source-ip` **rule condition uses the real TCP source IP**, not XFF — so IP allow-listing via listener rules is not spoofable. But behind CloudFront, the TCP source is CloudFront, so `source-ip` rules become useless there. Do geo/IP restriction at CloudFront instead.
- Same caution applies to any header your app trusts (`X-Forwarded-Proto`, `X-Forwarded-Host`, or custom auth headers) — **the ALB does not strip client-supplied copies.** If your app trusts `X-Internal-Admin`, a client can just send it.

### 4.4 Network exposure

- **Security groups:** inbound only 80/443 from the intended source (0.0.0.0/0 for a public site, the CloudFront prefix list or nothing at all for a CloudFront-fronted app). Target security groups should allow inbound **only from the ALB's security group ID**, not a CIDR.
- **Never give targets public IPs.** This is the second half of CVE-2024-10125: if targets are internet-reachable, ALB-enforced auth is bypassable by hitting the target directly. It also nullifies mTLS verify mode and WAF.
- **Prefer internal ALBs + CloudFront VPC Origins** for internet-facing workloads.
- Consider **VPC Block Public Access** to structurally prevent public-subnet placement.

### 4.5 Authentication hardening checklist

- [ ] Verify the signature of `x-amzn-oidc-data` **and** that its `signer` header equals your ALB ARN.
- [ ] Never trust `x-amzn-oidc-accesstoken` or `x-amzn-oidc-identity` — they're unsigned.
- [ ] Strip client-supplied `x-amzn-*` headers at the edge if targets are ever reachable outside the ALB path.
- [ ] For `jwt-validation`, pin the exact `iss` and validate at least one authorization claim (e.g. `scope` or `aud`), not just signature + expiry.
- [ ] Use mTLS **verify** mode, not passthrough, unless you have a specific reason to validate in-app. Passthrough enforces nothing at the load balancer.
- [ ] Keep trust store CRLs current; a revoked client cert without a CRL update is still accepted.

### 4.6 Logging, IAM, and governance

- Enable **access logs** (free to S3) and **connection logs**. Without them, debugging 502s, mTLS failures, and JWT rejections is guesswork. As of Sept 2025 the modern S3 bucket policy works in all regions.
- Route logs to **CloudWatch Logs as vended logs** (July 2026) if you want Logs Insights and metric filters, and use **telemetry enablement rules** to enforce logging org-wide on new ALBs.
- Scope IAM tightly: `elasticloadbalancing:ModifyRule`, `ModifyListener`, `SetSecurityGroups`, and `DeleteLoadBalancer` are all effectively "redirect production traffic" permissions. Resource-level permissions and tag conditions are supported.
- Useful AWS Config rules: `alb-http-drop-invalid-header-enabled`, `alb-http-to-https-redirection-check`, `alb-waf-enabled`, `elb-deletion-protection-enabled`, `elb-logging-enabled`.

---

## 5. Common Mistakes

### Architecture and routing

**Treating `path-pattern` as if it matched the query string.** It matches the path only. `/search?q=x` matches `/search`, not `/search*?*`. Use a `query-string` condition for the rest.

**Assuming path-based routing strips the prefix.** Before transforms existed, `/api/*` → target group meant your app received `/api/users`, not `/users`. Teams either rewrote the app or inserted a proxy. Since Oct 2025, use a `url-rewrite` transform instead — but remember that the transform runs *after* matching, so the rule condition still matches the original path.

**Hitting the 100-rule quota by surprise.** It's **per load balancer**, not per listener. With HTTP and HTTPS listeners you're splitting 100 rules between them. Regex conditions (Oct 2025) collapse many rules into one and are the first thing to reach for; consolidating hosts with wildcards is second; a quota increase is third.

**Forgetting the 5-target-group-per-action and 100-per-ALB limits.** Neither is adjustable. Multi-tenant platforms hit "target groups per ALB: 100" well before they hit the rule limit.

**Deploying into a single AZ or into `/28` subnets with no headroom.** ALB requires ≥2 AZs and needs free IPs in each subnet to scale out. A subnet that's nearly full silently caps your ALB's scaling.

**Hardcoding the ALB's IP addresses.** They change without notice. Use the DNS name, or an NLB in front if you truly need static IPs.

### Health and failure behavior

**Pointing health checks at `/` when `/` is expensive or requires auth.** A health check that hits your database on every probe amplifies load during exactly the wrong moment. Use a dedicated shallow `/healthz`.

**Health checking a path behind an auth rule.** Health checks come from the ALB and don't carry cookies or tokens; if the ALB's auth action or your app returns 302/401, every target is unhealthy. Health checks are evaluated against the target group directly and bypass listener rules — but if your *app* requires auth on that path, you'll still get 401s.

**Health check grace periods shorter than cold start.** ECS/ASG kills booting tasks in a loop. Symptom: perpetual deploy churn with no obvious error.

**Ignoring `target_group_health` settings.** Default behavior when most targets are unhealthy is to send everything to the few that remain, which usually kills them too. Configure `unhealthy_state_routing.minimum_healthy_targets` so the ALB spreads load rather than concentrating it, and `dns_failover` so an unhealthy AZ drops out of DNS.

**Deregistration delay mismatches.** Default 300s. If your ECS stop timeout or ASG lifecycle hook is shorter, targets get killed mid-drain and clients see 5xx. If it's much longer than needed, deploys take forever.

### Timeouts

**ALB idle timeout longer than the target's keep-alive timeout.** This is the #1 cause of sporadic **502s**. The target closes an idle connection the ALB still believes is open, the ALB reuses it, the connection resets. **Fix: set your application/web-server keep-alive timeout *greater* than the ALB idle timeout** (e.g. ALB 60s → NGINX `keepalive_timeout 75s`, Node `server.keepAliveTimeout = 65000`).

**ALB idle timeout shorter than the request duration.** Causes **504 Gateway Timeout** on long-running requests. Raise `idle_timeout.timeout_seconds` (up to 4000) or make the operation async.

**Not understanding 502 vs 503 vs 504.**

| Code | Usual meaning |
|---|---|
| **502** | Target closed the connection, sent a malformed response, or keep-alive mismatch |
| **503** | No healthy targets in the target group |
| **504** | Target didn't respond within the idle timeout |

### Security

**Leaving `drop_invalid_header_fields` at its `false` default.** Flagged by every compliance framework; enables header-smuggling classes of attack.

**Trusting `X-Forwarded-For[0]`.** Spoofable. See §4.3.

**Trusting `x-amzn-oidc-*` headers without signature and `signer` verification.** See CVE-2024-10125.

**Using mTLS passthrough and assuming the ALB is enforcing something.** It isn't. Passthrough accepts any certificate — including self-signed ones from anybody.

**Public ALB behind CloudFront with no origin protection.** The ALB DNS name is discoverable via certificate transparency logs and passive DNS. Anyone who finds it bypasses your entire edge security posture. Use VPC Origins.

**Leaving TLS 1.0/1.1 enabled** by accepting the default security policy in the console wizard.

**Forgetting that WAF sees post-transform URIs.** A WAF rule blocking suspicious paths may see only the rewritten path. Verify with WAF sampled requests.

### Operations and cost

**Orphaned ALBs.** A load balancer with zero healthy targets and zero requests still costs the hourly base rate. Audit for `UnHealthyHostCount == target count` or `RequestCount == 0`.

**One ALB per Kubernetes Ingress.** Use `alb.ingress.kubernetes.io/group.name`.

**Not enabling access logs until you have an incident.** They're free to S3 and you can't retroactively generate them.

**Not enabling deletion protection.** A single Terraform `destroy` against the wrong workspace ends the outage conversation early.

**Expecting instant scaling.** ALB roughly doubles capacity every ~5 minutes. For flash traffic (ticket sales, launches, migrations) use **LCU reservation** to set a minimum ahead of time rather than hoping the reactive scaler keeps up.

**Combining incompatible target group settings.** `weighted_random` excludes both slow start and sticky sessions; `least_outstanding_requests` excludes slow start. Terraform/CDK will surface an error, but the error message ("cannot enable both slow start and weighted random") is confusing when you never explicitly set slow start.

**Sticky-session cookie name collisions.** Application cookie names cannot begin with `AWSALB`, `AWSALBAPP`, or `AWSALBTG`.

---

## 6. Quick Reference Tables

### Quotas (defaults)

| Quota | Default | Adjustable |
|---|---|---|
| ALBs per Region | 50 | Yes |
| Listeners per ALB | 50 | Yes |
| Certificates per ALB (excl. default) | 25 | Yes |
| **Rules per ALB (excl. default)** | **100** | Yes |
| Condition values per rule | 5 | No |
| Condition wildcards per rule | 6 | No |
| Match evaluations per rule | 5 | No |
| Target groups per ALB | 100 | **No** |
| Target groups per action | 5 | **No** |
| Targets per ALB | 1,000 | Yes |
| Targets per target group | 1,000 (Lambda: 1) | Yes / No |
| Load balancers per target group | 1 | **No** |
| Target groups per Region | 3,000 (shared with NLB) | Yes |
| Trust stores per account | 20 | Yes |

### Feature timeline (selected, newest first)

| Date | Feature |
|---|---|
| Aug 2026 | RFC 9151 / CNSA 1.0 security policies |
| Jul 2026 | ALB logs as CloudWatch vended logs; telemetry enablement rules |
| Nov 2025 | **JWT verification** (`jwt-validation` action) |
| Nov 2025 | **Target Optimizer** (max concurrent requests per target) |
| Oct 2025 | **Transforms** — URL and host header rewrite; regex conditions |
| Feb 2025 | HTTP header modification for all response codes |
| Nov 2024 | LCU (Capacity Unit) reservation |
| Nov 2024 | CloudFront VPC Origins; one-click CloudFront + WAF integration |
| May 2024 | Dual-stack without public IPv4 |
| Mar 2024 | Resource map |
| Nov 2023 | **Mutual TLS**; **Automatic Target Weights**; FIPS 140-3 policies |
| Mar 2023 | TLS 1.3 security policies |
| Nov 2022 | Zonal shift; target group health; cross-zone LB toggle |
| Oct 2020 | gRPC and end-to-end HTTP/2 |
| Aug 2020 | Desync mitigation mode |
| Nov 2019 | Least outstanding requests; weighted target groups |
| Nov 2018 | Lambda targets |
| Jul 2018 | Redirect and fixed-response actions |
| May 2018 | OIDC / Cognito user authentication |

### Hardening baseline (copy/paste starting point)

```bash
ALB=arn:aws:elasticloadbalancing:...

aws elbv2 modify-load-balancer-attributes --load-balancer-arn "$ALB" --attributes \
  Key=routing.http.desync_mitigation_mode,Value=strictest \
  Key=routing.http.drop_invalid_header_fields.enabled,Value=true \
  Key=routing.http.response.server.enabled,Value=false \
  Key=deletion_protection.enabled,Value=true \
  Key=access_logs.s3.enabled,Value=true \
  Key=access_logs.s3.bucket,Value=my-alb-logs \
  Key=connection_logs.s3.enabled,Value=true \
  Key=connection_logs.s3.bucket,Value=my-alb-logs \
  Key=zonal_shift.config.enabled,Value=true \
  Key=idle_timeout.timeout_seconds,Value=60
```

Plus: TLS 1.2/1.3-only security policy, HTTP→HTTPS redirect on port 80, WAF attached with `waf.fail_open.enabled=false`, targets with no public IPs and security groups referencing the ALB's SG, and either a CloudFront VPC Origin or a tightly-scoped inbound rule.

---

### Primary sources

- [Application Load Balancers User Guide](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/introduction.html)
- [Document history for Application Load Balancers](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/doc-history.html)
- [Transforms for listener rules](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/rule-transforms.html)
- [Verify JWTs using an Application Load Balancer](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/listener-verify-jwt.html)
- [Authenticate users using an Application Load Balancer](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/listener-authenticate-users.html)
- [Mutual authentication with TLS](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/mutual-authentication.html)
- [Edit target group attributes](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/edit-target-group-attributes.html)
- [Quotas for your Application Load Balancers](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/load-balancer-limits.html)
- [Elastic Load Balancing pricing](https://aws.amazon.com/elasticloadbalancing/pricing/)
- [AWS Security Bulletin AWS-2024-012 (CVE-2024-10125)](https://aws.amazon.com/security/security-bulletins/AWS-2024-012)
