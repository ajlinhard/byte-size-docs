# Application Load Balancers (ALB) Overview


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
