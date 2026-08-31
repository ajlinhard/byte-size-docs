# AWS VPC Web Traffic Services
There are a bunch of services and methods for routing traffic for a web applications in AWS. This is a high-level overview of some of the basic use cases and role of each service for the incoming web traffic.

## How they fit together

Here's the request path with all five in place:
<img width="1472" height="720" alt="image" src="https://github.com/user-attachments/assets/339ad5d8-32bf-4662-b5d4-7dc0909609ca" />

A few practical notes on the combination:

**Order matters.** WAF evaluates at the CloudFront edge before the cache lookup, so blocked requests never touch your origin or your cache. If you attach WAF to the ALB instead of CloudFront, attack traffic has already crossed the internet into your Region and you're paying for it.

**Close the bypass.** Attaching WAF to CloudFront is worthless if the origin is still publicly reachable. VPC origins, or Origin Access Control for S3, is what makes CloudFront the only way in.

**Config is the proof layer.** The other four services are configuration; Config is what verifies that the configuration is still what you think it is. Rules like "CloudFront distribution has a WAF web ACL attached" and "CloudFront uses TLS 1.2 minimum" are the ones worth turning on first.

**What's not on this list** but usually belongs in the same conversation: AWS Shield (network-layer DDoS, standard is automatic and free), AWS Network Firewall (layer 3–7 VPC traffic inspection, distinct from DNS Firewall), AWS Firewall Manager (org-wide policy for WAF, Shield, Network Firewall, and DNS Firewall rule groups), and GuardDuty (threat detection that consumes Route 53 Resolver query logs, among other sources).

---

## AWS WAF

**Purpose.** A layer-7 firewall that inspects every HTTP/HTTPS request before it reaches your application and decides whether to allow, block, count, present a CAPTCHA, or issue a silent browser challenge.

**Role in a web app.** WAF isn't a standalone box you route traffic through. You attach a *web ACL* to a resource that already terminates connections: CloudFront, Application Load Balancer, API Gateway, AppSync, Cognito user pools, App Runner, Amplify Hosting, and — as of June 2026 — Amazon Bedrock AgentCore Gateway, so the same IP controls, rate-based rules, and managed rule groups now cover agentic AI workloads. When attached to CloudFront, evaluation happens at the edge, so bad traffic dies before it costs you origin capacity.

**Key features:**
- **AWS Managed Rules** — maintained rule groups for the OWASP-style basics (SQL injection, XSS, known bad inputs, OS-specific exploits) plus the Anti-DDoS managed rule group. Note the big migration in flight: AWS is moving Shield Advanced's automatic application-layer mitigation onto the Anti-DDoS managed rule group, deployed in Count mode on eligible web ACLs on July 27, 2026 with an automatic upgrade in October, and Shield Advanced isn't required to use it.
- **Marketplace partner rule groups** — 2026 added several AI-aware ones. Salt Security's rule group covers API attack vectors like credential brute force, SSRF, and JWT anomalies, and it labels and can block unauthenticated Model Context Protocol traffic. Miggo's rule groups target vulnerabilities under active exploitation and appearing in the CISA KEV catalog, plus generative-AI stacks like LLM gateways and model-serving infrastructure.
- **Rate-based rules** — throttle by IP, header, cookie, or custom key.
- **Bot Control and Fraud Control** — bot classification, account takeover prevention, account creation fraud prevention.
- **Labels** — rules tag requests and later rules act on the tags. Since May 2026 you can interpolate an entire label namespace into custom request or response headers with `${namespace:}` syntax, and use synthetic labels resolved from request context including client IP and JA3/JA4 TLS fingerprints. That's how you get WAF signals into your app so it can, say, force MFA rather than hard-block.
- **Text transformations** — pre-parse transformations normalize the raw query string before WAF splits it into key-value pairs, closing HTTP parameter pollution and parser-differential evasion gaps, and ten new transformations were added in July 2026 including command-line and JavaScript decoding.
- **AI traffic monetization** — a genuinely new category. WAF can return a machine-readable HTTP 402 using the x402 protocol, letting publishers price, meter, and collect payment from AI bots and agents at the edge instead of just blocking them.

**Use cases.** Virtual patching when a CVE drops and you can't ship a fix today; blocking credential stuffing against a login endpoint; geo-restricting an admin path; rate-limiting a signup form; scraper and bot management; and now deciding whether AI crawlers get blocked, allowed, or billed.

**Watch out for:** pricing is per web ACL + per rule + per million requests, and each rule consumes WCUs against a capacity limit per web ACL. Managed rule groups are cheap to enable and expensive to enable *all* of.

---

## Amazon CloudFront

**Purpose.** A global CDN and, increasingly, the intended single front door for your application — caching, TLS termination, edge compute, and the attachment point for WAF.

**Role in a web app.** Route 53 points your domain at a CloudFront distribution. CloudFront terminates TLS at the nearest of hundreds of points of presence, serves cache hits locally, and rides the AWS backbone to your origin on misses. Origin can be S3, an ALB, EC2, a Lambda function URL, API Gateway, or any public HTTP endpoint.

**Key features:**
- **Origin cloaking** — Origin Access Control for S3, and **VPC origins** for everything else. VPC origins let ALBs, NLBs, and EC2 instances sit in private subnets reachable only through your CloudFront distribution, and since November 2025 the origin can live in a different AWS account, shared via AWS RAM. This is the single biggest security win available in CloudFront — it makes bypassing WAF structurally impossible rather than merely discouraged.
- **Edge compute** — CloudFront Functions for sub-millisecond JavaScript (header rewriting, redirects, A/B routing) and Lambda@Edge for heavier work. Origin modification in CloudFront Functions lets you conditionally change or override the origin per request without touching the distribution config, and functions can now read the serving edge location's airport code and the expected Regional Edge Cache, enabling geo-specific routing for things like GDPR compliance.
- **Caching controls** — cache policies, origin request policies, response headers policies, Origin Shield, invalidations, signed URLs and cookies for private content.
- **Observability** — standard logs to S3 and real-time logs, plus the security dashboard that surfaces WAF blocks and lets you block traffic patterns without writing rules.
- **Simplified onboarding** — the current console flow starts from the domain name, and when using Route 53 it automatically provisions the ACM certificate and DNS records with security defaults, so you don't bounce between ACM, Route 53, and WAF.
- **Pricing models** — pay-as-you-go, or flat-rate plans. The Premium plan now offers self-service monthly usage levels from 500 million to 6 billion requests and 50 TB to 600 TB, bundling content delivery, WAF and DDoS protection, bot management, Route 53 DNS, CloudWatch Logs ingestion, edge compute, and S3 credits with no overage charges.
- **SaaS Manager** — reusable configurations and parameters for providers delivering many tenant websites at scale.

**Use cases.** Static site and SPA hosting from S3; accelerating a dynamic app behind an ALB; API acceleration; video streaming; and hiding an origin entirely from the public internet.

---

## Amazon Route 53

**Purpose.** Authoritative DNS, domain registration, and DNS-based traffic management with health checking.

**Role in a web app.** This is the first thing that happens on any request. A viewer resolves `app.example.com`, Route 53 answers, and the answer determines which CloudFront distribution, load balancer, or Region the user actually reaches. Because it decides *where* traffic goes before any packets flow, it's also your cheapest failover and deployment-shifting mechanism.

**Key features:**
- **Hosted zones** — public for internet-facing records, private for VPC-internal names.
- **Alias records** — free, zone-apex-capable records pointing directly at CloudFront, ALB, S3 websites, and API Gateway. This is how `example.com` (not just `www`) can point at a CDN.
- **Routing policies** — simple, weighted, latency-based, geolocation, geoproximity, failover, multivalue answer, and IP-based. Route 53 routes users to the best endpoint based on geoproximity, latency, health, and other considerations, which also helps with data residency requirements.
- **Health checks** — endpoint, calculated, and CloudWatch-alarm-based, driving automatic failover.
- **DNSSEC** — signing for public hosted zones and validation in Route 53 Resolver.
- **Resolver** — inbound and outbound endpoints for hybrid DNS between on-premises and VPCs. Since May 2026, inbound endpoints support DNS64 to synthesize AAAA responses for IPv4-only domains, and outbound endpoints can forward to public IPv6 name servers through the internet gateway.
- **Profiles** — bundle private hosted zones, Resolver rules, and DNS Firewall rule groups into one shareable configuration applied across VPCs and accounts, with granular IAM added in March 2026 so you can scope permissions to specific resource types, hosted zone names, or VPC associations.
- **Accelerated recovery** — a 60-minute RTO for Route 53 control plane operations on public hosted zones during a us-east-1 disruption, available in commercial Regions at no extra charge. Worth enabling on the zones you'd need to edit during an incident.

**Use cases.** Multi-region active-active or warm standby failover; latency routing for a global user base; weighted records for canary and blue/green cutovers; splitting internal and external views of the same domain; registrar consolidation. Route 53 Domains added 34 new TLDs in May 2026 including .app, .dev, and .health.

---

## AWS Config

**Purpose.** Continuous recording, assessment, and auditing of your resource configurations. It is not in the request path at all — it's the governance and evidence layer.

**Role in a web app.** Config is what tells you that CloudFront distribution #14 has no WAF attached, that a security group opened port 22 to the world at 3am last Tuesday, or that someone disabled DNS query logging. It records a *configuration item* every time a resource changes, keeps the history, maps relationships between resources, and evaluates rules against them.

**Key features:**
- **Configuration history and timeline** — answers "what changed, when, and by whom" after an incident. Pair it with CloudTrail for the API-call side of the story.
- **Config rules** — AWS managed rules plus custom rules in Lambda or Guard. Coverage expanded sharply this year: 191 additional managed rules landed in July 2026 across Bedrock, SageMaker, ECS, EKS, RDS, Redshift, S3, and CloudTrail, evaluating encryption, logging, public access, and network security.
- **Conformance packs** — deployable bundles of rules mapped to frameworks like PCI DSS, HIPAA, and CIS, applied per account or across an organization.
- **Remediation** — attach SSM Automation documents to auto-fix non-compliant resources.
- **Aggregators** — one multi-account, multi-Region view; essential with Control Tower or any Organizations setup.
- **Advanced queries** — SQL over your resource inventory, plus natural-language querying that generates the SQL for you.
- **Resource coverage** — continuously growing; recent additions include Bedrock, Bedrock AgentCore, and SageMaker types in June 2026 and API Gateway, EC2 VPC encryption controls, and S3 Vectors in July.
- **Recording modes** — continuous versus daily periodic recording, which is the main lever for controlling cost.

**Use cases.** Audit evidence for SOC 2, PCI, or HIPAA; drift detection against a baseline; guardrails that flag or auto-remediate misconfiguration; forensic timeline reconstruction after a breach or outage; asset inventory.

**Watch out for:** billing is per configuration item recorded plus per rule evaluation. Recording all resource types continuously in an account with chatty resources (autoscaling groups, ephemeral ENIs) gets expensive fast. Scope recording deliberately.

---

## DNS and DNS Firewall

This is where most people's mental model breaks, so it's worth separating two completely different jobs.

**Authoritative DNS** is Route 53 hosted zones answering the world's questions *about your domain*. Inbound-facing, covered above.

**Recursive resolution** is your workloads asking questions *about everyone else's domains*. Inside a VPC that's the Route 53 Resolver at the `.2` address. **This is the direction DNS Firewall protects.**

**Purpose of DNS Firewall.** Filter outbound DNS queries leaving your VPCs, so a compromised instance can't resolve its command-and-control domain or exfiltrate data through DNS.

**Key features:**
- **Rule groups with domain lists** — your own lists plus AWS-managed and updated lists of known DNS threats, with the option of a strict allowlist limiting traffic to only trusted domains.
- **Actions** — allow, alert, or block, with block responses of NODATA, NXDOMAIN, or a CNAME override to a sinkhole. Rules are priority-ordered within a group.
- **Two tiers, renamed in May 2026.** Existing managed domain lists and your custom lists sit in the DNS Firewall Foundational tier, while DNS Firewall Advanced detects and blocks Domain Generation Algorithm and DNS tunneling traffic. Advanced expanded to include threat categories such as spam and phishing plus content categories including adult content and gambling, at no additional cost to Advanced customers.
- **Distribution** — associate rule groups to VPCs directly, or roll them out via AWS Firewall Manager, RAM, CloudFormation, or Route 53 Profiles.
- **Global Resolver** — the newest piece. Route 53 Global Resolver went GA in March 2026 across 30 Regions, an internet-reachable anycast resolver giving authorized clients resolution of public domains and private hosted zone domains from anywhere, with filtering for malicious domains, NSFW domains, DGA and tunneling threats, centralized query logging, and Dictionary DGA protection added at GA. It supports DoH and DoT, and accepts traffic only from authenticated clients, with token-based authentication beyond IP/CIDR allowlists. That extends the same policy to branch offices, data centers, and remote laptops rather than just VPCs.

**Use cases.** Blocking malware C2 callbacks; stopping DNS-tunnel data exfiltration; enforcing an egress allowlist for a regulated workload; content filtering for corporate networks; centralizing DNS policy across a hybrid estate.

**The key distinction:** WAF guards traffic coming *in* to your application. DNS Firewall guards queries going *out* from your compute. They are not substitutes and neither covers the other's direction.

---
