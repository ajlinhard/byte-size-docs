# AWS ARNs Protect or not to Protect?
Short answer: ARNs aren't secrets, but they're not nothing either — the risk is nuanced and depends on which resource type.

**Why ARNs aren't secrets:** An ARN is an identifier, not a credential. Knowing `arn:aws:s3:::my-bucket` or `arn:aws:iam::123456789012:role/my-role` doesn't grant anyone access — actual access is gated by IAM policies, resource policies, and trust relationships. This is fundamentally different from an access key, password, or session token, which *are* secrets and should never be in code.

**Why they're not fully harmless either:**

- **Account ID exposure** — every ARN embeds your 12-digit AWS account ID. AWS itself says account IDs aren't secret, but recommends not needlessly exposing them, since they're a stable identifier useful for social engineering (e.g., someone impersonating "AWS Support" for your specific account) and as a building block for reconnaissance.
- **Infrastructure fingerprinting** — a codebase full of ARNs reveals your resource naming conventions, regions, service topology, and account structure. Not dangerous on its own, but it lowers the cost of the next step for an attacker who's already gained a foothold somewhere.
- **Public repo risk** — if this code is or ever becomes public (or a private repo gets breached), you're handing over a map, even if none of it is directly exploitable.

**Nuance by resource type:**

| ARN type | Typical sensitivity | Why |
|---|---|---|
| S3 bucket | Low | Bucket names are often guessable/discoverable anyway; real risk is bucket policy, not name secrecy |
| IAM Role (esp. OIDC/cross-account) | Low, often intentionally public | Commonly published on purpose (e.g., GitHub Actions OIDC role ARNs in public workflow files) — the trust policy conditions are the actual control, not obscurity |
| Lambda function | Low | Invocation is gated by resource policy/IAM, not ARN secrecy |
| KMS key | Medium | Key policy still gates use, but KMS keys often protect high-value data, so many teams treat the ARN as worth minimizing exposure of, as defense-in-depth |
| Secrets Manager secret | Medium-ish | The ARN isn't the secret value, but it signals "valuable target here" to anyone doing recon with partial access |

**The bigger issue is usually engineering, not security:** hardcoding ARNs (which bake in account ID + region) breaks portability across dev/staging/prod. The standard fix — environment variables, SSM Parameter Store, Secrets Manager, or referencing IaC outputs (Terraform/CloudFormation) — solves the security-hygiene concern as a side effect of solving the "this breaks when I deploy to another account" problem.

**Bottom line:** don't panic if ARNs are in your code, but don't treat them as free either. Avoid hardcoding for maintainability reasons primarily, avoid unnecessary exposure in public repos as a mild security hygiene practice, and make sure your actual security posture rests on tightly scoped IAM/resource policies — never on the assumption that an ARN staying private is doing any real protective work.
