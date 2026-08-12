# Application Load Balancers (ALB) Overview
## An ALB is a reverse proxy, not a network device

This is the thing that makes the rest click. A Network Load Balancer operates at layer 4 — it shovels TCP packets toward a target and mostly doesn't know or care what's inside them. An **Application** Load Balancer operates at layer 7 and behaves like nginx or Envoy:

- It terminates the TLS connection itself (that's why the cert lives on the listener).
- It parses the full HTTP request — method, path, headers, cookies, host.
- It then **decides** what to do, and one entirely legitimate decision is *"answer this myself and never contact a backend at all."*

So the ALB was never obligated to forward your request. Forwarding is just one of several action types it can take. Others include `redirect`, `fixed-response`, and — the one that matters here — `authenticate-cognito`.

## Rules, Target Groups, and Targets
They're a chain, each layer answering a different question:

```
Load Balancer
  └─ Listener (port 443, HTTPS)
       ├─ Rule  #10  if host = api.example.com   → forward to TG-api
       ├─ Rule  #20  if path = /images/*         → forward to TG-static
       └─ Rule default (no conditions)           → forward to TG-web
                                                      └─ Targets: i-abc:8080, i-def:8080
```

**Rules** live on a listener and decide *where a request goes*. Each has conditions and actions, and they're evaluated in priority order (1 = highest), first match wins. Every listener has a default rule with no conditions that catches whatever falls through.

Conditions can match on host header, path pattern, HTTP header, HTTP method, query string, or source IP — up to 5 conditions per rule. Multiple values inside one condition are OR'd; separate conditions are AND'd.

Actions are `forward`, `redirect` (e.g. HTTP→HTTPS), `fixed-response` (a canned 503 or maintenance page), or the OIDC/Cognito auth actions. Only one terminal action per rule; auth actions run before the forward. A single forward can also split across multiple target groups with weights, which is how you do blue/green and canary shifts.

**Target groups** are the routing destination and, more importantly, *the unit of health checking*. A target group carries the protocol and port, the load-balancing algorithm (round robin, least outstanding requests, weighted random), stickiness settings, deregistration delay, slow start, and the health check config — path, interval, timeout, thresholds, and the success matcher (`200`, or a range like `200-299`). Target groups are independent objects: one can be referenced by several listeners or even several load balancers, and a target can belong to more than one group.

**Targets** are the actual endpoints registered in a group. Three types for ALB:

- `instance` — EC2 instance IDs; traffic goes to the instance's private IP on the group's port
- `ip` — raw IPs, which is what you need for on-prem endpoints, peered VPCs, or containers with their own ENIs
- `lambda` — a function, invoked with a synthetic HTTP event

Only targets passing health checks receive traffic. If every target in a group is unhealthy, ALB fails open and distributes to all of them rather than returning errors.

**Things that trip people up:**

- Target group type is fixed at creation. Switching from `instance` to `ip` means a new group.
- The health check port defaults to the traffic port but can be overridden — useful when your app serves `/healthz` on a sidecar port.
- Health check failures are usually security groups, not the app. The target's SG must allow the ALB's SG on both the traffic port *and* the health check port. Reference the ALB's security group ID rather than a CIDR here — it tracks the ALB's ENIs automatically as they change across AZs.
- Rule priority gaps matter. Leave space (10, 20, 30) so you can insert later without renumbering.
- Path patterns are case-sensitive and don't match the query string. `/images/*` won't match `/images` exactly — you need both patterns if you want the bare path.
- The `source-ip` condition sees the immediate client IP. Behind CloudFront or another proxy, that's the proxy's address; you'd match on the `X-Forwarded-For` header instead.

---
## ALB Authentication
How initial request get routed to authentication can be entirely the ALB, and specifically one **listener rule**. Nothing else in your stack was involved. Let me unpack exactly what "the ALB" means here, because the word hides a lot of machinery.

## The structure that made the decision

```
Load Balancer
 └── Listener (port 443, HTTPS, ACM cert attached)
      ├── Rule priority 10  ── conditions ──► actions
      ├── Rule priority 20  ── conditions ──► actions
      └── Default rule      ── (no conditions) ──► actions
```

Every request that arrives on the listener is evaluated against the rules **in ascending priority order**, and the **first rule whose conditions all match wins**. Evaluation stops there. If nothing matches, the default rule handles it.

Your `GET /dashboard` hit this rule:

```yaml
Priority: 10
Conditions:
  - Field: path-pattern
    Values: ["/*"]              # matches everything, including /dashboard
Actions:
  - Type: authenticate-cognito
    Order: 1                    # ◄── runs FIRST
    AuthenticateCognitoConfig:
      UserPoolArn:      arn:aws:cognito-idp:us-east-1:123456789012:userpool/us-east-1_AbCdEfGhI
      UserPoolClientId: 7a1b2c3d4e5f6g7h8i9j0k1l2m
      UserPoolDomain:   my-app
      Scope:            "openid email"
      SessionCookieName: AWSELBAuthSessionCookie
      SessionTimeout:   604800
      OnUnauthenticatedRequest: authenticate
  - Type: forward
    Order: 2                    # ◄── runs only if Order 1 lets it
    TargetGroupArn: arn:aws:elasticloadbalancing:...:targetgroup/web-tg/abc123
```

The `Order` field is the whole answer to your question. A rule holds a **chain** of actions, executed in order, and any action in the chain can terminate the request. `authenticate-cognito` must always be `Order: 1`, and the chain must always end in a terminating action (`forward`, `redirect`, or `fixed-response`).

## What the authenticate action actually evaluates

```
Request arrives at Order 1 (authenticate-cognito)
        │
        ├─ Is the path /oauth2/idpresponse ?
        │     └─ YES ──► This is the OIDC callback. Redeem the code (step 7),
        │                 mint session cookies, 302 to the saved state URL.
        │                 ✋ Order 2 never runs. Backend never contacted.
        │
        ├─ Is there an AWSELBAuthSessionCookie-* ?
        │     └─ NO ───► ✋ 302 to Cognito /oauth2/authorize.  ← THIS IS YOUR STEP 2
        │                 Order 2 never runs. Backend never contacted.
        │
        ├─ Does it decrypt with my key, and is the session unexpired?
        │     └─ NO ───► ✋ Same 302. Start over.
        │
        ├─ Is the access token near expiry?
        │     └─ YES ──► Silent back-channel refresh, then continue.
        │
        ▼
   Inject x-amzn-oidc-identity / -accesstoken / -data
        │
        ▼
   Fall through to Order 2 (forward) ──► your target group   ← STEP 9
```

Your original `GET /dashboard` fell into the second branch. No cookie → the ALB generated a `302` **itself**, as the origin server, and the response went straight back down the same connection the browser had opened. Your target group's health checks were passing the whole time and it received nothing.

## Where the redirect URL came from

The ALB doesn't have Cognito's authorize endpoint hardcoded. Given `UserPoolDomain: my-app` and the pool's region, it resolves the OIDC discovery document:

```
https://cognito-idp.us-east-1.amazonaws.com/us-east-1_AbCdEfGhI/.well-known/openid-configuration
```

```json
{
  "authorization_endpoint": "https://my-app.auth.us-east-1.amazoncognito.com/oauth2/authorize",
  "token_endpoint":         "https://my-app.auth.us-east-1.amazoncognito.com/oauth2/token",
  "userInfo_endpoint":      "https://my-app.auth.us-east-1.amazoncognito.com/oauth2/userInfo",
  "jwks_uri":               "https://cognito-idp.us-east-1.amazonaws.com/us-east-1_AbCdEfGhI/.well-known/jwks.json"
}
```

That's where `authorization_endpoint` in step 2 and `token_endpoint` in step 7 come from. With the generic `authenticate-oidc` action you supply all four URLs by hand; the Cognito-specific action just discovers them for you.

The `redirect_uri` it sends is likewise derived, not configured: **the request's own scheme and host, plus the hardcoded path `/oauth2/idpresponse`**. That's why it came out as `https://app.example.com/oauth2/idpresponse` — the ALB built it from the `Host` header of your original request. It's also why the same ALB serving two hostnames needs both callback URLs registered in the Cognito app client.

## The `OnUnauthenticatedRequest` knob

This single field decides what "no valid session" means:

| Value | Behavior | Use for |
|---|---|---|
| `authenticate` | 302 to the IdP (the default) | Browser traffic — HTML pages |
| `deny` | `401 Unauthorized`, empty body | API paths — a `fetch` gets a clean 401 instead of an HTML login page |
| `allow` | Forward anyway, **with no identity headers** | Public pages that show extra content when signed in |

This is how you'd fix the gotcha from Part 2 Scenario A: a second rule at a lower priority number for `/api/*` with `OnUnauthenticatedRequest: deny`.

## Practical consequences worth knowing

**Rule priority is a real footgun.** If a broad `path-pattern: ["/*"]` rule sits at priority 10 and your unauthenticated `/health` or `/public/*` rule sits at priority 50, the broad rule wins and everything gets forced through login. Public routes need *lower* priority numbers.

**The default rule is separate.** It has no priority and is evaluated last. Putting `authenticate-cognito` on priority-10 rules but forgetting the default rule leaves an unauthenticated hole for any path that didn't match.

**Health checks bypass all of this.** They're issued by the ALB directly to targets and never traverse listener rules, so your health endpoint won't get redirect-looped.

**HTTPS listeners only.** Authenticate actions are rejected on port 80 listeners. Standard setup is a port 80 listener whose only action is `redirect` to 443.

**The ALB needs IAM permissions.** Specifically `cognito-idp:DescribeUserPoolClient`. If that's missing you get a `561` error code in the access logs, which is an ALB-specific status meaning authentication failed.

**Your app can't opt out.** There's no way for the backend to say "this one request doesn't need auth" — the decision was made before your code was reachable. Granularity comes from writing more listener rules, not from application logic.

## The contrast that makes it concrete

Had you built this without the ALB action, *your* code would own steps 2 through 8:

```python
@app.route("/login")                    # you write this
def login(): return redirect(build_authorize_url())

@app.route("/callback")                 # and this
def callback():
    validate_state(request.args["state"])
    tokens = exchange_code(request.args["code"])   # you hold the client secret
    claims = verify_jwt(tokens["id_token"])        # you fetch and cache JWKS
    session["user"] = claims["sub"]                # you run a session store

@app.before_request                     # and this
def require_auth():
    if "user" not in session: return redirect("/login")
```

Plus refresh-token rotation, session storage shared across instances, and secret management. The ALB action replaces all of it with a listener rule — and in exchange, your app trusts three headers and verifies one signature.

---
# ALBs vs API Gateways
They solve different problems that happen to overlap at "HTTP in front of Lambda."

**API Gateway is an API management layer.** Its value is everything *around* the request: authentication (IAM/SigV4, Cognito, custom Lambda authorizers), per-client throttling and usage plans with API keys, request validation, request/response transformation via VTL (REST APIs), response caching, stages and canary deployments, OpenAPI import/export, and per-caller usage metering. It's serverless — no VPC presence required, no idle cost, priced purely per request.

**ALB is a load balancer that learned to invoke Lambda.** Its value is being a single L7 entry point in your VPC that can fan out to EC2, ECS, IPs, *and* Lambda behind the same hostname and rule set. It has no concept of API consumers — no keys, no per-client rate limits, no transformation. Auth is limited to the OIDC/Cognito listener action. You pay hourly plus LCUs regardless of traffic.

| | API Gateway (HTTP API) | ALB |
|---|---|---|
| Cost shape | per request, no floor | hourly + LCU, cheap at volume |
| Crossover point | — | roughly high-thousands of req/sec sustained |
| Auth | IAM, JWT, Lambda authorizers | OIDC / Cognito only |
| Throttling | per-stage, per-key, per-route | none |
| Transformation | yes (REST APIs) | none |
| Request payload | ~10 MB | 1 MB |
| Timeout | 30s (REST can be raised via quota) | idle timeout, configurable much higher |
| Mixed backends | Lambda, HTTP, AWS services | Lambda + EC2 + ECS + IPs together |
| VPC | not required | required |

Note that quotas here move around — worth confirming current limits against the service quotas page before designing around a specific number.

## Both fronting the same function

Yes, and it's a legitimate pattern in a few situations:

**Internal vs. external planes.** An internal ALB serves callers inside the VPC or arriving over Direct Connect — no internet path, no auth ceremony. A public API Gateway serves partners with API keys, throttling, and usage metering. Same business logic, two very different sets of consumers.

**Cost tiering.** A chatty internal service generating millions of requests goes through the ALB you're already paying for; the low-volume public surface stays on API Gateway where the management features earn their per-request price.

**Migration.** Dual-running both during a cutover in either direction, shifting traffic by DNS weight, is far safer than a flip.

**Consolidation.** You already have an ALB routing `/app/*` to ECS. Adding `/app/reports` → Lambda keeps one hostname and one TLS cert instead of standing up a separate API and CORS story.

**Different auth models.** ALB's Cognito action does the browser redirect flow and sets a session cookie — good for humans. API Gateway with SigV4 is better for machine clients. Same handler, two front doors.

## What actually bites you

The event shapes are different, and this is the real work. ALB sends `path`, `httpMethod`, `queryStringParameters`, and `requestContext.elb`. API Gateway v2 sends `rawPath`, `requestContext.http.method`, and `version: "2.0"`. The fix is a small adapter at the top of the handler that sniffs the shape and normalizes to your own internal request object — do this before you have two front doors, not after.

Responses diverge too. ALB requires an explicit `{statusCode, headers, body, isBase64Encoded}` object every time; API Gateway v2 has the convenience format where returning a plain object becomes a 200 with JSON. Emit the explicit form always and both are satisfied.

A few smaller ones:

- Each front door needs its own `lambda:InvokeFunction` resource policy statement — one for `elasticloadbalancing.amazonaws.com`, one for `apigateway.amazonaws.com`. Adding the second is easy to forget.
- If you enable header handling on the ALB target group, it's `multiValueHeaders` *or* `headers`, not both, and flipping it changes the event shape your adapter sees.
- ALB has no throttle. A traffic spike or a retry storm on that path translates directly into Lambda concurrency, which can starve every other function in the account sharing the same concurrency pool. Set reserved concurrency on the function if the ALB side is exposed to anything unpredictable.
- Health checks on a Lambda target group are off by default. If you turn them on, ALB invokes your function on a schedule and you pay for it — and the handler needs to recognize and cheaply answer that probe.
- The 1 MB ALB payload ceiling is lower than API Gateway's. A request that works on one path can fail on the other, which is a confusing bug to chase if you didn't know the limits differed.
