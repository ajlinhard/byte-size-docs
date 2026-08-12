# API Gateway Overview
An API Gateway enhances security when using Lambda to access external APIs in several key ways:

## Request Validation and Filtering
API Gateway acts as a front door that validates incoming requests before they even reach your Lambda function. It can check for proper formatting, required parameters, and reject malformed requests immediately, reducing the attack surface.

## Authentication and Authorization
API Gateway can handle authentication mechanisms like API keys, OAuth tokens, or AWS IAM credentials. This means your Lambda function doesn't need to implement this logic, and unauthorized requests never make it through. You can also integrate with Amazon Cognito for user authentication.

## Rate Limiting and Throttling
It protects your Lambda functions (and by extension, the external APIs they call) from abuse by limiting the number of requests per second. This prevents DDoS attacks and helps you stay within external API rate limits, avoiding additional costs or service disruptions.

## Private Network Integration
When accessing external APIs, you can configure Lambda to run inside a VPC with API Gateway as the public entry point. This keeps your Lambda functions in a private network while still allowing controlled public access through the gateway.

## Hiding Internal Architecture
API Gateway abstracts away your implementation details. External clients only see the gateway endpoint, not your Lambda functions or the external APIs you're calling. This makes it harder for attackers to understand and exploit your architecture.

## Request/Response Transformation
You can strip sensitive data from responses or sanitize inputs before they reach Lambda, adding an extra security layer between the client and your business logic.

## Logging and Monitoring
API Gateway integrates with CloudWatch to provide detailed logs of all requests, making it easier to detect suspicious patterns or security incidents.

Think of API Gateway as a security checkpoint—it handles the heavy lifting of access control and validation so your Lambda can focus on business logic rather than security concerns.

---
## Public and Private API Gateways
**Fully private (VPC-only)**

A private API has no publicly reachable invoke endpoint; the only way to call it is through an interface VPC endpoint inside your VPC, or through a private network connection to that VPC. You create an interface endpoint for the `execute-api` service, then set the API's endpoint type to `PRIVATE` and attach a resource policy. The resource policy specifies which principals can access the API, and you can additionally attach a VPC endpoint policy specifying who can access the VPC endpoint and which APIs can be called through it — useful for restricting to specific accounts or org IDs. Callers from on-prem reach it over Direct Connect/VPN, typically with a Route 53 resolver inbound endpoint for DNS.

Important caveat: this only works with REST APIs (v1). HTTP APIs (v2) don't support the PRIVATE endpoint type or VPC endpoint policies. If you've built on HTTP APIs and need a private endpoint, you either migrate to REST or front an internal ALB/NLB yourself.

Don't confuse this with **VPC Link**, which is the opposite direction — a public-facing API reaching *into* your VPC for the backend integration. VPC Link connects API Gateway to HTTP(S) resources inside your VPC via a Network Load Balancer without exposing them to the internet.

**Public but IP-restricted**

For a regional or edge-optimized API, use a resource policy with a `Deny` on `NotIpAddress` matching `aws:SourceIp`. Two gotchas: on edge-optimized APIs the source IP seen is CloudFront's, not the client's, so IP policies behave unexpectedly — use regional endpoints for this. And a resource policy denies *after* the request reaches API Gateway, so you're still billed for rejected calls. AWS WAF with an IP set attached to the stage is generally the better tool: it blocks earlier, supports rate limiting, and is easier to manage as the allowlist changes.

**Rough equivalents elsewhere:** Azure API Management has an internal-VNet mode plus private endpoints; GCP uses Private Service Connect with internal Application Load Balancers (API Gateway there has no true private endpoint mode); Kong/Apigee hybrid you deploy into your own network directly.

Which one fits depends on whether "limit by IP" is a compliance checkbox or actual defense — if the callers are all inside AWS or on your corporate network, private + PrivateLink is meaningfully stronger than an allowlist.

---
## API Gateays v1/v2 question

They aren't a setting, and v2 isn't an upgrade of v1. They're two separate products that happen to live under the same service name and are managed by two different control-plane APIs:

- **`apigateway`** (v1) manages **REST APIs**
- **`apigatewayv2`** manages **HTTP APIs** and **WebSocket APIs**

You'll never see a version dropdown. In the console you pick "REST API," "HTTP API," or "WebSocket API" at creation. In Terraform it's `aws_api_gateway_rest_api` vs `aws_apigatewayv2_api`; in CloudFormation, `AWS::ApiGateway::RestApi` vs `AWS::ApiGatewayV2::Api`; in CDK, `RestApi` vs `HttpApi`.

The "v2" label is misleading. HTTP APIs (2019) came later, but they were a **deliberate feature-stripped rewrite** aimed at cheaper, lower-latency Lambda-backed APIs — not a successor. AWS's own framing is that REST APIs support more features, while HTTP APIs are designed with minimal features so they can be offered at a lower price. REST APIs are not deprecated and remain the fuller product.

Practical consequence: **there is no conversion path.** You can't flip an HTTP API to a REST API. You'd create a new REST API and rebuild — an OpenAPI export/import gets you routes, but authorizers, integrations, and stage config don't map cleanly.

## Why HTTP APIs can't be private

"Private" isn't a thing you turn on; it's an **endpoint type**, and endpoint types are a REST API concept. REST APIs have three (edge-optimized, regional, private); HTTP APIs have exactly one — regional and public. AWS's comparison table lists private endpoints as supported for REST APIs and not for HTTP APIs, alongside edge-optimized.

The second half compounds it. Making a private REST API actually secure depends on a **resource policy** — that's what restricts invocation to a specific VPC endpoint ID or account. HTTP APIs don't support resource policies at all. So even setting the endpoint aside, HTTP APIs have no mechanism for "only these callers."

Which means the fallback also fails: AWS WAF is likewise listed as REST-only, so you can't attach an IP set to an HTTP API stage either. (One recent blog claims AWS added native WAF for HTTP APIs in 2025, but the current AWS comparison doc still says otherwise — worth checking your console before relying on it.)

**Net: for both of your original requirements — VPC-only, or IP allowlisting — HTTP APIs give you neither.** Your options there are all "put something else in front": CloudFront + WAF, or an internal ALB with WAF attached, or a Lambda authorizer inspecting source IP (fragile, and it runs after the request is already billed).

## One trap worth knowing

The `execute-api` interface VPC endpoint, with private DNS enabled, takes over `*.execute-api.<region>.amazonaws.com` resolution inside that VPC. That's why connecting to private and public APIs simultaneously from the same VPC often fails depending on the private-DNS setting. Workloads in that VPC calling *public* API Gateway endpoints — including your HTTP APIs — will start returning 403s. The fix is a custom domain name for the public APIs, or a Route 53 private hosted zone. Teams hit this weeks after enabling private APIs and rarely connect the two events.
