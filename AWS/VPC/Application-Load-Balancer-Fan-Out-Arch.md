# ALB Fan Out Architexture 
Path-based fan-out to distinct target groups is the standard microservices-behind-one-ALB shape. It's a good default, but the costs are mostly *coupling* costs that don't show up until the ALB is shared by several teams.

## What you gain

**One edge to secure and operate.** A single DNS name, one ACM certificate, one WAF WebACL, one set of TLS policies, one place where auth actions live. Adding a service means adding a rule, not provisioning and hardening a new front door.

**Real cost consolidation.** Each additional ALB is roughly $22/month base plus per-AZ public IPv4 charges before any traffic. Ten services on one ALB versus ten ALBs is a meaningful difference at small scale, and it's why the EKS `group.name` annotation exists.

**Genuine per-service isolation where it matters.** Target groups are the unit of independence: separate health checks, deregistration delays, routing algorithms, stickiness, slow start, and target group health thresholds. A service failing health checks returns 503 for its own paths only — the rest of the ALB is unaffected.

**Per-service progressive delivery.** Weighted target groups let you canary one service without touching the others. Each team ships on its own cadence against a shared listener.

## What you pay

**Listener-level settings are shared, and several of them matter.** This is the constraint people discover too late:

| Setting | Scope | Consequence |
|---|---|---|
| `idle_timeout` | Load balancer | One long-poll or SSE service forces the timeout up for everyone |
| TLS security policy | Listener | Can't be strict for a partner API and permissive for a legacy client |
| mTLS mode + trust store | Listener | Can't require client certs on one path only |
| `desync_mitigation_mode`, `drop_invalid_header_fields` | Load balancer | Going `strictest` for one service breaks non-compliant clients of another |
| HSTS / CSP / X-Frame-Options values | Listener | One header value for all services |
| WAF WebACL | Load balancer | Shared managed rule groups; rate limits apply LB-wide unless you scope each rule by URI |

If two services have genuinely different security postures, that's the signal to split — not a thing to work around.

**Hard quotas you can't buy your way out of.** Target groups per ALB is **100 and not adjustable**; target groups per action is **5 and not adjustable**; targets per ALB defaults to 1,000. The rule limit (100) *is* adjustable and regex conditions relieve it, but the target-group ceiling is a wall. Multi-tenant platforms hit it well before they hit the rule count.

**Shared capacity and shared scaling.** All services draw on one LCU pool. A traffic spike on one path drives the ALB's scaling behavior — and its scaling is reactive, roughly doubling every five minutes. LCU reservation is per-load-balancer, so pre-warming for one team's launch pre-warms for everyone, and bills accordingly.

**Rule ordering becomes a cross-team coupling.** Priorities are a single global namespace per listener. Two teams reserving priority 100 collide. Someone inserting a broad regex at priority 5 can silently shadow another team's rule — first-match-wins means the shadowed rule simply never fires, with no error anywhere. Reserve priority bands per service (100–199, 200–299) and enforce them in IaC.

**Rule evaluation is a billing dimension.** `request rate × (rules processed − 10 free)`. Deep rule lists on high-traffic ALBs are a real line item. Order by traffic volume, not alphabetically.

**Attribution gets harder.** Target-side metrics are per-target-group, but the LB-side ones you care about during an incident — `HTTPCode_ELB_5XX_Count`, `ConsumedLCUs`, `RejectedConnectionCount`, `ClientTLSNegotiationErrorCount` — are per-load-balancer. When the ALB itself is generating 5xx, you can't tell from metrics alone which service caused it. You'll be in access logs correlating by `rule_arn` and `target_group_arn`.

**IaC ownership.** The listener is one resource. Either one team owns it and becomes a bottleneck, or every team writes `aws_lb_listener_rule` against a shared listener ARN and you get state contention and race conditions on priority assignment.

## Where the "fan-out" specifically bites

**Path prefixes leak into your services** unless you rewrite. Transforms (Oct 2025) solved this cleanly, but note the failure mode: a transform that matches its regex and then fails returns **HTTP 500** — an error class your service never sees and can't log. Test transforms against real traffic shapes, not just the console regex tester.

**Path-based routing is more fragile than host-based** for tenant or service separation. `/orders/*` and `/order-history/*` are one careless wildcard away from overlapping; `orders.example.com` and `history.example.com` aren't. If you're already at 25 certs' worth of SNI headroom, prefer host-based conditions and reserve paths for routing *within* a service.

## When to split instead

Split into multiple ALBs when any of these are true:

- Two services need different TLS policies, mTLS, or idle timeouts
- Services belong to different compliance boundaries or AWS accounts
- You're approaching 100 target groups
- One service's traffic profile would distort scaling or LCU reservation for the rest
- Blast radius of a listener misconfiguration is unacceptable for a tier-0 service

A reasonable middle ground most teams land on: **one ALB per bounded context or per environment tier**, host-based routing at the top level, path-based fan-out within each host. That keeps the quota and coupling costs bounded while still avoiding an ALB per service.

For east-west service-to-service traffic specifically, VPC Lattice is worth evaluating rather than piling internal calls onto the same ALB — it's built for that shape and doesn't share the listener-level constraints above.
