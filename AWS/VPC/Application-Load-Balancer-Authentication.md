# ALB Authentication (OIDC and JWT)
Short answer: there's no way to share one JWT config across rules — `jwt-validation` is a per-rule action, and there's no listener-level equivalent. So the efficiency win comes from **needing fewer rules**, not from making rules cheaper.

Two hard constraints shape the design:

- A rule may include **exactly one** authentication action — `authenticate-oidc`, `authenticate-cognito`, *or* `jwt-validation`. You can't chain JWT then Cognito on the same rule.
- Rules are **first-match-wins**. There's no fall-through, so a JWT rule that matches never reaches your Cognito rule.

### The setup that actually scales: split the audiences, not the paths

If machine traffic and browser traffic are separable by host or by a single prefix, you need one JWT rule, not N:

```
Priority 10   host-header: api.example.com     → jwt-validation → forward api-tg
Default rule  (no conditions)                  → authenticate-cognito → forward web-tg
```

The default rule *can* carry `authenticate-cognito` — that's the standard Cognito-on-ALB pattern — so your "last rule is cognito-auth" requirement is satisfied for free without consuming a rule slot.

### If the paths genuinely fan out to different target groups

Then you need one rule per target group and you will duplicate `JwksEndpoint` + `Issuer` in each. That's fine at runtime — the ALB caches JWKS, so N rules is not N key fetches per request. Handle the duplication in IaC:

```hcl
locals {
  jwt = {
    type = "jwt-validation"
    jwt_validation_config = {
      jwks_endpoint = "https://issuer.example.com/.well-known/jwks.json"
      issuer        = "https://issuer.example.com"
    }
  }
}

resource "aws_lb_listener_rule" "api" {
  for_each = { orders = "/orders/*", users = "/users/*", billing = "/billing/*" }
  # ... action = [local.jwt, { type = "forward", target_group_arn = ... }]
}
```

### Collapse paths that share a target group with regex

Since October 2025, `path-pattern` accepts regex, so one rule replaces several:

```json
{ "Field": "path-pattern",
  "PathPatternConfig": { "RegexValues": ["^/(orders|users|billing|inventory)(/.*)?$"] } }
```

This matters because the wildcard route hits limits fast — 5 condition values and 6 wildcards per rule. There's also a documented "match evaluations per rule: 5" quota whose exact interaction with regex alternation I'd verify against your real patterns before assuming a big regex is free.

### Ordering has a real cost

LCU rule-evaluation billing is `request rate × (rules processed − 10 free)`, and *processed* means rules evaluated until a match. Put your highest-traffic paths at the lowest priority numbers. Staying under 10 evaluated rules per request keeps that dimension at zero.

### One path serving both audiences

If an endpoint must accept both a service token and a browser session, gate on the header rather than duplicating the path:

```
Priority 10   path-pattern /reports/*  AND  http-header Authorization: "Bearer *"
              → jwt-validation → forward reports-tg
Priority 20   path-pattern /reports/*
              → authenticate-cognito → forward reports-tg
```

Costs an extra rule per dual-audience path, so use it sparingly.

### Two things to design around

**Failure modes differ.** JWT validation rejects with a 401; Cognito redirects with a 302 to a hosted login page. A browser wandering onto a JWT-guarded path gets an opaque 401, and a curl client hitting the Cognito default gets an HTML login page instead of JSON. Keep the boundary crisp — host-based separation is the cleanest way to guarantee that.

**Your app sees two different identity shapes.** The JWT path forwards the original token untouched in `Authorization`; the Cognito path injects `x-amzn-oidc-data`/`-accesstoken`/`-identity`. Your service needs both code paths — and on the JWT rules, nothing is populating or overwriting the `x-amzn-oidc-*` headers, so a client could supply their own. That's harmless *only if* you're verifying the signature on `x-amzn-oidc-data` and checking that its `signer` equals your ALB ARN, which you should be doing anyway.
