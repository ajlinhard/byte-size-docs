# ALB Role Based Access Controls (RBAC)
I'll lay out where role data can come from and where you can enforce it, since those are two separate decisions in this stack.

## What ALB actually hands your Lambda

When ALB is configured with an `authenticate-cognito` action, it injects three headers into the request before invoking your Lambda target:

- `x-amzn-oidc-identity` — the Cognito `sub`
- `x-amzn-oidc-accesstoken` — the raw Cognito **access token** (a JWT)
- `x-amzn-oidc-data` — a JWT that ALB itself signs (ES256), whose payload is the claims from Cognito's `/oauth2/userInfo` endpoint

The gotcha that trips most people up: **`cognito:groups` is not in the userinfo response**, so it will not appear in `x-amzn-oidc-data`. It *is* in the access token. If you want to use Cognito Groups as your role mechanism, you must read and verify `x-amzn-oidc-accesstoken`, not the convenient ALB-signed one.

Also note ALB has no equivalent of an API Gateway Lambda authorizer. Listener rules can route on path, host, method, and header values, but cannot inspect JWT claims. So ALB can do authentication and coarse path routing; it cannot do role-based routing on its own.# Where the role can live

**1. Cognito Groups.** Create groups (`admin`, `analyst`, `viewer`), attach users, read `cognito:groups` from the access token in Lambda. Zero extra infrastructure, and groups can carry a precedence value and an IAM role if you ever need to hand out temporary AWS credentials via an identity pool. The downsides: it's coarse (a flat list of strings), Cognito is now your authorization store as well as your identity store, and membership changes don't take effect until a new token is issued.

**2. Cognito custom attributes.** `custom:role`, `custom:tenant_id`. These *do* appear in `x-amzn-oidc-data` provided the app client has read permission on the attribute and the relevant scope is requested, so it's the one option that works with the header ALB gives you natively. Constraints: 50 custom attributes max, string values only, immutable-or-mutable is fixed at creation time, and no good story for multi-valued permissions.

**3. Pre-token-generation Lambda trigger.** The source of truth stays in Postgres; the trigger queries it at sign-in and injects claims into the token. The V2 trigger can modify access-token claims and group membership, not just the ID token. This gets you rich, DB-driven roles delivered as claims, at the cost of a DB hit on the login path and the same staleness window. Note it does not affect the userinfo response, so the claims land in `x-amzn-oidc-accesstoken`, not `x-amzn-oidc-data`.

**4. Postgres as the authoritative store, queried per request.** The token carries only identity; the Lambda maps `sub` to a user row and loads roles/permissions/tenant scope. This is the most flexible option and the only one that's immediately consistent — a revoked permission takes effect on the next request rather than the next token. It's also the only one that handles resource-level authorization ("can this user edit *this* document"), which no token claim can express. The cost is a query per request, which you mitigate with RDS Proxy, a short-TTL cache in the warm container, or DynamoDB/ElastiCache as a read-through cache.

The hybrid is usually right: a coarse role in the token for fast rejection and routing, fine-grained permissions in Postgres for anything resource-scoped.

# Where you enforce it

**ALB listener rules.** Useful only for path segregation, not role logic. What it *does* buy you is separate target groups — `/admin/*` to one Lambda, `/api/*` to another — so the admin Lambda can have its own IAM execution role and its own Postgres user with narrower grants. That's real defence in depth even though ALB itself can't check the role. Never route on a client-supplied header; the browser controls those.

**Lambda middleware.** The common pattern: a wrapper that verifies the token, builds a principal object, and exposes a `require(permission)` check that each handler calls. Roles map to permission sets either in code (a constant map, redeployed on change) or in Postgres (`roles`, `permissions`, `role_permissions`, `user_roles` — changeable without deploy). Return 403 for authenticated-but-forbidden, and 404 instead of 403 when even the existence of a resource is sensitive.

**Amazon Verified Permissions.** If your rules start growing conditionals (time of day, ownership, tenant, attribute comparisons), externalizing them into Cedar policies is worth considering. It has a Cognito identity-source integration and `IsAuthorizedWithToken` accepts the Cognito token directly, mapping `cognito:groups` onto Cedar groups. You pay a per-request API call and some latency. The lighter-weight alternative is embedding OPA/Cedar evaluation in the Lambda itself and keeping policies in S3 or the database.

**Postgres row-level security.** Underrated here. Instead of filtering in application code, define policies on the tables and set a session variable per request:

```sql
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON orders
  USING (tenant_id = current_setting('app.tenant_id')::uuid);
```

Then in the Lambda, inside a transaction: `SET LOCAL app.tenant_id = $1`. This makes tenant and ownership scoping structurally impossible to forget in a query. Use `SET LOCAL` rather than `SET`, because with RDS Proxy a bare `SET` pins the connection and you lose pooling. You can also go further and use distinct Postgres roles per application role with `SET LOCAL ROLE`, so column-level `GRANT`s enforce which fields a role can even read.

**Response shaping.** For "same endpoint, different response body," a serializer layer keyed off the permission set is cleaner than conditionals sprinkled through handlers: define per-role field allowlists, and pass the response object through a filter before returning. Column-level grants plus RLS gives you a DB-enforced version of the same thing if the stakes are high.

# Gotchas worth knowing up front

- **Verify, don't just decode.** `x-amzn-oidc-data` is signed with ES256; fetch the key from `https://public-keys.auth.elb.<region>.amazonaws.com/<kid>` and — this part is frequently skipped — check that the `signer` field matches your own load balancer's ARN. Otherwise anyone with an ALB in that region can mint a token your Lambda will accept. If you're reading `x-amzn-oidc-accesstoken` for groups, validate it against the Cognito JWKS and check `iss`, `client_id`, `token_use: access`, and `exp`.
- **Don't let the Lambda be reachable except through the ALB.** No function URL, and a resource policy that only permits `elasticloadbalancing.amazonaws.com` with a source ARN condition.
- **Staleness has two layers.** The Cognito token TTL *and* the ALB session cookie (`SessionTimeout`, default 7 days). A Cognito global sign-out does not clear the ALB cookie, so a user can keep hitting your backend after you think you've kicked them out. If revocation matters, either shorten the session timeout or maintain a revocation/version check in Postgres that the Lambda consults.
- **Large group lists break things.** ALB stores session state in cookies (sharded as `AWSELBAuthSessionCookie-N`), and a user in dozens of groups can push you into header-size limits. Another argument for keeping the token coarse and the detail in Postgres.
- **ALB-to-Lambda has a 1 MB request/response limit** and requires the `statusCode`/`headers`/`body`/`isBase64Encoded` response shape — relevant if role-based responses ever return large payloads.

If you tell me whether roles are mostly static (a handful of fixed personas) or dynamic and tenant-scoped, I can narrow this to a single recommended shape.
