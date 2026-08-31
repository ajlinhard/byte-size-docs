# VPC Origins Bypass
What is Origin Access Control? VPC Origins? Why does it matter?

Both solve the same problem, for different origin types. The problem is worth stating first, because it's the thing that makes the rest matter.

## What is an Origin?
In CDN terms, the **origin** is the authoritative source of your content — the server CloudFront goes to when it doesn't already have what a viewer asked for.

The mental model: CloudFront is a copy. The origin is the original.

A request plays out like this. A viewer asks an edge location for `/logo.png`. If that edge location has a fresh copy cached, it hands it back and your origin never hears about the request. If it doesn't — a cache miss — CloudFront turns around and fetches it from the origin, serves it to the viewer, and keeps a copy for the next person who asks.

So the origin is where your stuff actually lives. In practice it's one of:

- an **S3 bucket** holding static files
- an **Application or Network Load Balancer** in front of your app servers
- an **EC2 instance** running a web server directly
- a **Lambda function URL**
- an **API Gateway** endpoint
- any **public HTTP server**, including one not on AWS at all

A distribution can have several origins and route between them by path pattern — `/api/*` to your ALB, everything else to S3. You can also group two origins together so CloudFront fails over to the second if the first returns errors.

Two things that follow from this and explain the previous answers:

**The origin is a real, addressable server.** It existed before CloudFront and it keeps existing after. That's precisely why bypass is possible — CloudFront doesn't stand between the viewer and the origin the way a physical gate does; it's a separate service that *also* knows how to reach your origin. If the origin remains publicly reachable, so does the back door. OAC and VPC origins are the two ways to close it.

**Cache hits never touch the origin.** This is the whole performance argument. A well-tuned cache means most requests are answered a few milliseconds from the user, and your origin only sees the fraction that genuinely needs it. It's also a cost argument: origin requests cost you compute, data transfer, and database load; edge hits don't.

The related term you'll see is **origin request** — the fetch CloudFront makes on a miss — as distinct from a **viewer request**, the one the browser makes. Cache policies control what CloudFront caches; origin request policies control what it forwards upstream. They're separate on purpose, so you can forward a header to your app without fragmenting your cache on it.


## The problem: origin bypass

When you put CloudFront in front of an application, you've built a front door. But unless you do something extra, the back door is still standing wide open. An S3 bucket configured as a website endpoint is publicly readable. An internet-facing ALB has a public DNS name that anyone can resolve and hit directly.

So an attacker who finds `my-alb-1234567890.us-east-1.elb.amazonaws.com` — and they will, via certificate transparency logs, DNS history sites, or an old cached record — can skip your CDN entirely:Everything you configured at the edge — WAF rules, geo restrictions, rate limits, signed URLs, TLS policy, bot control, DDoS absorption — is decoration if this path exists.

## Origin Access Control

OAC makes CloudFront authenticate to your origin as an AWS principal, so the origin can refuse everyone else.

Mechanically: when CloudFront gets a cache miss, it signs the origin request with SigV4 using short-lived credentials. Your S3 bucket policy then grants access only to the `cloudfront.amazonaws.com` service principal, with a condition restricting it to your specific distribution ARN. Block Public Access stays on. Direct requests to the bucket get a 403.

It replaces the older Origin Access Identity, which had real gaps: OAI didn't support granular policy configurations, POST requests in Regions requiring SigV4, or SSE-KMS integration. OAC also works with buckets in all Regions including opt-in Regions launched after December 2022, and supports SSE-KMS. Use OAC on anything new; OAI is legacy.

Supported origin types are S3, Lambda function URLs, MediaStore, and MediaPackage v2 — and as of August 20, 2026, S3 Multi-Region Access Points, which previously required computing your own SigV4a authorization header via a custom Lambda@Edge function.

Two configuration details that bite people:
- Signing behavior has three settings. "Sign requests" is the one you want in almost all cases. "Do not override authorization header" exists for when your viewers pass their own auth.
- For S3 bucket origins with OAC, Object Ownership must be set to "Bucket owner enforced" — the default for new buckets, but not for old ones.

## VPC Origins

OAC doesn't cover load balancers or EC2. That's the gap VPC origins fills, and it fills it differently: instead of adding authentication, it removes reachability.

With a VPC origin, your ALB, NLB, or EC2 instance lives in a **private subnet** with no route to the internet. CloudFront reaches it through an AWS-managed private connection. There is no public IP, no public DNS name, nothing to discover. The bypass path in the diagram above doesn't get blocked — it stops existing.

What's landed since launch:
- **Cross-account support** (Nov 2025) — the origin can sit in a different account from the distribution, shared via AWS RAM, within or outside your AWS Organizations and OUs. This matters because most real estates separate the networking/edge account from workload accounts, and before this you had to choose between VPC origins and your account structure.
- **WebSocket support** (May 2026) — real-time applications served over WebSockets can now live entirely in private subnets, where previously WebSocket servers had to sit in public subnets.
- **Origin modification in CloudFront Functions** — you can route between VPC origins and origin groups dynamically per request, weighting traffic across backends without redeploying the distribution.

There's no extra charge for VPC origins.

## Why it matters

**The alternative approaches are worse.** The common pre-VPC-origins pattern was to keep the ALB public and add a secret custom header that CloudFront injects and an ALB listener rule requires. The trade-off is that the ALB's public endpoint is always one leaked header away from being reachable, and you carry the operational burden of rotating that secret. The other pattern — allowlisting CloudFront's published IP ranges in a security group — means maintaining a list that changes, and it doesn't distinguish *your* distribution from anyone else's CloudFront distribution. Someone can point their own distribution at your ALB.

**It changes your security posture from "policy" to "topology."** A WAF rule is a control someone can misconfigure, and a header secret is a control someone can leak. A resource that has no public address is not a control at all — it's a property of the network. That's a categorically stronger guarantee, and it's the reason this is usually the first thing to fix in a CloudFront architecture review.

**It makes the rest of your spend worthwhile.** If you're paying for WAF managed rule groups, Bot Control, or Shield Advanced, an open origin means you're paying for protection an attacker can route around.

**It's auditable.** This is where AWS Config earns its keep — rules like `S3_BUCKET_PUBLIC_READ_PROHIBITED` and `CLOUDFRONT_S3_ORIGIN_ACCESS_CONTROL_ENABLED` catch the case where someone creates the fourteenth bucket and forgets.

## Which to use

| Origin | Mechanism |
|---|---|
| S3 bucket, S3 MRAP | OAC |
| Lambda function URL | OAC |
| MediaStore, MediaPackage v2 | OAC |
| ALB, NLB, EC2 | VPC origins |
| API Gateway | VPC origins via a private endpoint, or a custom header on a regional endpoint |
| Third-party / external HTTP | Custom header secret; nothing better available |

One caveat worth knowing: IPv6-only and dual-stack origin connectivity is available for custom origins but excludes S3 and VPC origins, so if end-to-end IPv6 to the origin is a hard requirement, that constrains the choice.
