# AWS Secrets Manager vs. AWS Systems Manager Parameter Store

*A deep-dive feature reference, last checked against AWS documentation in September 2026.*

---

## 1. Quick Answer: Which One Do I Use?

Both services store data outside your code and let you fetch it at runtime over an API, both support encryption with AWS KMS, and both integrate with IAM, CloudFormation, ECS/Fargate, Lambda, and EC2. The difference is **purpose-built design**:

- **AWS Secrets Manager** is a *secrets lifecycle manager*. It exists to solve the hard problems around credentials specifically: automatic rotation against live databases/services, versioned staging (current/pending/previous), cross-region replication for DR, and fine-grained resource policies for cross-account sharing — all at a per-secret price.
- **AWS Parameter Store** (part of AWS Systems Manager) is a *general-purpose hierarchical configuration store* that also happens to support encrypted values (`SecureString`). It's built for large volumes of configuration data — feature flags, AMI IDs, endpoint URLs, and yes, low-churn secrets — organized in a folder-like namespace, at effectively no cost for the standard tier.

AWS's own guidance is direct: for **secrets such as database credentials, API keys, or tokens**, it recommends **Secrets Manager**, because it provides "purpose-built security controls including automatic rotation and cross-region replication." For everything else — configuration data — it points you to Parameter Store.

In practice, most well-architected AWS environments use **both**: Secrets Manager for anything that must rotate and be tightly audited, Parameter Store for the much larger volume of static configuration (and for secrets that are cheap, low-sensitivity, or don't need automatic rotation).

---

## 2. Similarities

| Capability | Both services support |
|---|---|
| Encryption at rest | AWS KMS (AWS managed key or customer-managed key) |
| Encryption in transit | TLS for all API calls |
| Access control | IAM identity-based and resource-based policies, condition keys, VPC endpoints (AWS PrivateLink) |
| Auditing | AWS CloudTrail logs every API call as a management event |
| Change notifications | Amazon EventBridge events on create/update/delete |
| Compute integration | Native retrieval from Lambda, ECS/Fargate task definitions, EC2, CodeBuild, CloudFormation, EKS (via CSI driver / External Secrets Operator) |
| Tagging | Cost-allocation and access-control tags |
| Regional scope | Data is regional; each AWS Region has its own store |
| API model | Simple `Get`/`Put`/`Describe`/`Delete`-style REST APIs, SDK and CLI support |

---

## 3. Key Differences (Use-Case View)

| Dimension | AWS Secrets Manager | AWS Parameter Store |
|---|---|---|
| **Primary purpose** | Manage the *lifecycle* of secrets (passwords, API keys, tokens) | Centralized store for configuration data, with secrets as a secondary use case |
| **Automatic rotation** | Built in — native Lambda rotation templates for RDS, Aurora, Redshift, DocumentDB, Neptune, plus "managed rotation" (no Lambda) for supported partner integrations, plus custom rotation functions | Not supported natively. AWS explicitly recommends Secrets Manager for rotation lifecycles |
| **Value size limit** | Up to 64 KB per secret | 4 KB (Standard tier) / 8 KB (Advanced tier) |
| **Data structure** | Flat secret name + JSON/binary blob; typically one secret = one credential set | Hierarchical namespace (`/app/env/component/key`) designed for thousands of related values |
| **Versioning** | Built-in staged versioning with labels (`AWSCURRENT`, `AWSPENDING`, `AWSPREVIOUS`, custom labels) — designed for safe rotation rollback | Simple sequential version numbers per parameter; no staging labels, no rotation rollback semantics |
| **Cross-region replication** | Native, one-click multi-Region replica secrets with automatic propagation of rotated values | Not built in — must be replicated manually or with a custom pipeline |
| **Cross-account sharing** | Resource-based policies attached directly to each secret | Advanced-tier parameters can be shared via AWS Resource Access Manager (RAM) |
| **Policy-based lifecycle rules** | N/A (rotation replaces this need) | Expiration, ExpirationNotification, NoChangeNotification parameter policies (Advanced tier only) |
| **Pricing model** | $0.40 per secret/month + $0.05 per 10,000 API calls (flat, no free tier) | Standard parameters: **free**. Advanced parameters: $0.05/parameter/month + API charges only if higher throughput is enabled |
| **Best for** | Database credentials, third-party API keys, OAuth tokens, anything that must rotate or be replicated for DR | App configuration, feature flags, AMI IDs, endpoint URLs, non-rotating secrets, large parameter volumes |
| **Native db/service rotation integrations** | Yes (RDS engines, Redshift, DocumentDB, Neptune, and growing "managed external secrets" partners) | No |
| **Managed external secrets** (partner rotation without Lambda) | Yes — Salesforce, Snowflake, BigID, MongoDB Atlas, Confluent Cloud (as of 2026) | No |

**Rule of thumb:** if a value needs to *rotate*, be *replicated across Regions*, or *shared cross-account with fine control*, use Secrets Manager. If a value is *configuration*, needs a *hierarchy*, or you have *thousands of items* and cost matters, use Parameter Store — including its `SecureString` type for lightweight secrets that don't need rotation.

---

## 4. AWS Secrets Manager — In Depth

**Docs home:** https://docs.aws.amazon.com/secretsmanager/

### 4.1 What It Does
AWS Secrets Manager helps you manage, retrieve, and rotate database credentials, application credentials, OAuth tokens, API keys, and other secrets throughout their lifecycle. Many AWS services store and use secrets in Secrets Manager, and the core value proposition is removing hard-coded credentials from application source code by replacing them with a runtime API call. ([What is AWS Secrets Manager?](https://docs.aws.amazon.com/secretsmanager/latest/userguide/intro.html))

For other categories of sensitive data, AWS explicitly redirects you elsewhere:
- AWS credentials → IAM
- Encryption keys → AWS KMS
- SSH keys → EC2 Instance Connect
- Private keys/certificates → AWS Certificate Manager

### 4.2 Secret Structure & Versioning
A secret in Secrets Manager bundles the encrypted secret value (a JSON key-value map, plain string, or binary blob up to 64 KB) with metadata: ARN, description, tags, rotation configuration, and resource policy.

Every time a secret's value changes, Secrets Manager creates a **new version** rather than overwriting the old one, and versions are tracked with **staging labels**:
- `AWSCURRENT` — the active version your application should retrieve
- `AWSPENDING` — a version being validated during rotation
- `AWSPREVIOUS` — the last known-good version, giving you a one-step rollback path if rotation fails
- Custom labels are also supported for advanced workflows

Secrets Manager retains up to 100 versions per secret and automatically prunes unlabeled versions beyond that (never removing versions created in the last 24 hours). ([Secrets Manager quotas](https://docs.aws.amazon.com/secretsmanager/latest/userguide/reference_limits.html))

### 4.3 Secret Types
The console offers dedicated, pre-wired secret types that simplify setup:
- Amazon RDS database credentials
- Amazon Aurora database credentials
- Amazon Redshift credentials
- Amazon DocumentDB credentials
- "Other type of secret" — arbitrary key-value pairs or raw JSON for API keys, OAuth tokens, or anything else

### 4.4 Automatic Rotation
This is Secrets Manager's headline feature. You can configure a rotation schedule (e.g., every 30 days) and AWS handles credential replacement end-to-end.

**How rotation works under the hood** — a four-step Lambda invocation:
1. `createSecret` — generates a new password/credential, stages it as `AWSPENDING`
2. `setSecret` — applies the new credential to the actual database or service
3. `testSecret` — verifies the new credential works
4. `finishSecret` — moves the `AWSCURRENT` label to the new version, demoting the old one to `AWSPREVIOUS`

**Rotation strategies:**
- **Single-user rotation** — the same database user's password is rotated in place (brief downtime risk during rotation window)
- **Alternating-users rotation** — two IAM/database users swap active status, eliminating downtime during rotation

**Pre-built rotation templates** exist (deployable via the Serverless Application Repository or referenced by ARN) for RDS MySQL, PostgreSQL, Oracle, and SQL Server, plus Redshift, DocumentDB, Neptune, and a generic HTTP endpoint template for anything else you script yourself.

**Managed rotation** (newer capability) skips the Lambda function entirely for certain partner integrations — AWS handles rotation logic on your behalf. As of 2026, **managed external secrets** cover:
- Salesforce
- Snowflake
- BigID
- MongoDB Atlas — database user secrets (SCRAM) and service-account (OAuth) secrets
- Confluent Cloud — API key rotation for service accounts, cluster-scoped and cloud resource management keys

All managed external secret integrations have automatic rotation **enabled by default**, removing the need to build or maintain custom Lambda rotation functions. ([Secrets Manager extends managed external secrets to MongoDB Atlas and Confluent Cloud](https://aws.amazon.com/about-aws/whats-new/2026/04/secrets-manager-managed-external-secrets-mongodb-confluent/), [Managed rotation docs](https://docs.aws.amazon.com/secretsmanager/latest/userguide/rotate-secrets_managed.html))

CLI example:
```bash
aws secretsmanager rotate-secret \
  --secret-id prod/app/db-credentials \
  --rotation-lambda-arn arn:aws:lambda:us-east-1:123456789012:function:SecretsManagerRDSPostgreSQLRotationSingleUser \
  --rotation-rules AutomaticallyAfterDays=30
```

Docs: [Rotate secrets](https://docs.aws.amazon.com/secretsmanager/latest/userguide/rotating-secrets.html) · [Set up alternating-users rotation](https://docs.aws.amazon.com/secretsmanager/latest/userguide/tutorials_rotation-alternating.html) · [Set up single-user rotation](https://docs.aws.amazon.com/secretsmanager/latest/userguide/tutorials_rotation-single.html)

### 4.5 Cross-Region Replication
Secrets Manager can replicate a secret to multiple Regions to support geographically distributed applications and disaster-recovery architectures. Key behavior:
- Replicas share the same ARN suffix as the primary, differing only in Region
- Secrets Manager replicates encrypted secret data **and** metadata (tags, resource policies)
- When rotation runs on the **primary** secret, the new value automatically propagates to every replica — you never manage rotation per-replica
- You can later **promote** a replica to a standalone secret and manage it independently
- Replication is not available between "specialized" partitions (e.g., GovCloud, China) and standard commercial Regions

```bash
aws secretsmanager replicate-secret-to-regions \
  --secret-id MySecret \
  --add-replica-regions Region=us-west-2,KmsKeyId=alias/my-replica-key
```

Docs: [Replicate secrets across Regions](https://docs.aws.amazon.com/secretsmanager/latest/userguide/add-regions.html)

### 4.6 Encryption
Every secret is encrypted at rest with AWS KMS. You can use the AWS-managed key `aws/secretsmanager` at no additional cost, or bring a customer-managed KMS key for tighter control over key policies, rotation, and cross-account grants (billed at standard KMS rates).

### 4.7 Access Control & Auditing
- **IAM identity-based policies** control which principals can call which Secrets Manager APIs
- **Resource-based (secret) policies** attached directly to a secret enable secure cross-account access without broad IAM grants
- **VPC endpoints (AWS PrivateLink)** let you call Secrets Manager without traversing the public internet
- **AWS CloudTrail** logs all API calls (including rotation events) as management events — the first copy is stored free
- **AWS Config rules** can continuously check secrets for compliance (e.g., rotation enabled, unused for N days)
- **Amazon EventBridge** can trigger workflows on secret creation, rotation, or deletion

Docs: [Control access to your secrets](https://docs.aws.amazon.com/secretsmanager/latest/userguide/auth-and-access.html) · [Monitor secrets for compliance](https://docs.aws.amazon.com/secretsmanager/latest/userguide/configuring-awsconfig-rules.html)

### 4.8 Retrieval & Caching
Applications call `GetSecretValue` at runtime. To avoid excessive API costs/throttling on hot paths, AWS provides **client-side caching libraries** (Secrets Manager Caching client for Java, Python, .NET, Go, JS) and a **Lambda extension** that caches secrets locally in the execution environment, refreshing on a TTL rather than on every invocation.

### 4.9 Compliance
Secrets Manager has undergone auditing for multiple compliance standards (SOC, PCI DSS, HIPAA eligibility, FedRAMP, ISO, and others depending on partition/Region), making it suitable as part of regulated workloads. Docs: [Compliance validation for Secrets Manager](https://docs.aws.amazon.com/secretsmanager/latest/userguide/secretsmanager-compliance.html)

### 4.10 Pricing (as of 2026)
- **$0.40 per secret per month**, prorated hourly (a secret deleted after 24 hours costs a fraction of the monthly rate)
- **$0.05 per 10,000 API calls** (covers `GetSecretValue`, `PutSecretValue`, and metadata calls alike)
- Secrets **marked for deletion incur no storage charge** during their recovery window
- **Cross-Region replicas are billed as separate secrets** — a secret replicated to 3 Regions costs roughly 3× the storage line
- Customer-managed KMS keys and Lambda-based rotation functions are billed separately at standard KMS/Lambda rates
- No setup fees, no minimum commitment, pricing is uniform across commercial Regions

Official pricing page: https://aws.amazon.com/secrets-manager/pricing/

### 4.11 Quotas Worth Knowing
- Max secret value size: **64 KB**
- Max versions retained per secret: **100** (unlabeled versions pruned automatically beyond that)
- Recommended: avoid calling `PutSecretValue`/`UpdateSecret` more than once every 10 minutes to avoid outrunning version cleanup
- `GetSecretValue` supports high-TPS read quotas per Region; control-plane APIs (create/update/rotate) have lower TPS quotas
- Quotas are per-Region and generally **adjustable** via Service Quotas

Docs: [Secrets Manager quotas](https://docs.aws.amazon.com/secretsmanager/latest/userguide/reference_limits.html)

### 4.12 Native Integrations
RDS, Aurora, Redshift, DocumentDB, Neptune credential rotation; ECS task definitions (`secrets` block); Lambda; CloudFormation (`AWS::SecretsManager::Secret`); AWS Config; CloudTrail; EventBridge; API Gateway; AppConfig; and growing SaaS "managed external secrets" partners.

---

## 5. AWS Systems Manager Parameter Store — In Depth

**Docs home:** https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-parameter-store.html

### 5.1 What It Does
Parameter Store provides secure, hierarchical storage for configuration data and lightweight secrets management. It standardizes how applications access critical data at runtime without hardcoding values or relying on fragmented storage solutions, helping teams maintain consistency, enforce governance, and build more secure and maintainable systems. AWS's own guidance: **for secrets such as database credentials, API keys, or tokens, use Secrets Manager instead**, which provides purpose-built rotation and replication controls. ([Parameter Store overview](https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-parameter-store.html))

### 5.2 Parameter Types
| Type | Use case |
|---|---|
| `String` | Plain-text values — environment names, endpoint URLs, resource identifiers |
| `StringList` | A comma-separated list of plain-text values, e.g. `subnet-123abc,subnet-456def,subnet-789ghi` |
| `SecureString` | Values requiring encryption via AWS KMS — service endpoints, account identifiers, low-churn credentials |

Note: you **cannot** change a parameter's type (e.g. `String` → `SecureString`) via the console after creation — you must use the CLI with `--overwrite`, or delete and recreate it. Docs: [Creating a Parameter Store parameter](https://docs.aws.amazon.com/systems-manager/latest/userguide/sysman-paramstore-su-create.html)

### 5.3 Hierarchies & Naming
Parameters are organized in a folder-like path structure, e.g. `/myapp/production/database-host`, `/myapp/production/database-password`. This hierarchy lets you:
- Group related configuration by application, environment, and component
- Grant IAM permissions scoped to a path prefix (e.g., allow access only to `/myapp/prod/*`)
- Retrieve an entire subtree at once with `GetParametersByPath`

```bash
# Get a single parameter
aws ssm get-parameter --name "/myapp/config/database-host" --query 'Parameter.Value' --output text

# Get a SecureString, decrypted
aws ssm get-parameter --name "/myapp/secrets/database-password" --with-decryption --query 'Parameter.Value' --output text

# Get multiple named parameters
aws ssm get-parameters --names "/myapp/config/database-host" "/myapp/config/database-port" --with-decryption
```

### 5.4 Parameter Tiers
Parameter Store offers **Standard**, **Advanced**, and **Intelligent-Tiering** (an auto-selecting default setting), configured per-parameter or as an account/Region default.

| Feature | Standard | Advanced |
|---|---|---|
| Use case | Most configuration data, low-scale workloads (default) | Higher limits, larger values, or parameter policies |
| Max parameters per account/Region | 10,000 | 100,000 |
| Max value size | 4 KB | 8 KB |
| Parameter policies | Not supported | Supported |
| Cross-account shareability | Not supported | Supported (via AWS RAM) |
| Upgrade/downgrade | Upgradeable to Advanced | **Cannot** be downgraded to Standard (would risk data loss/truncation and uses different encryption) |
| Cost | No additional charge | Charges apply |

`Intelligent-Tiering` as the account default automatically creates a parameter as Standard, and only promotes it to Advanced if it exceeds Standard's limits (size, policy usage, etc.) — giving you cost efficiency without manual tier management.

Docs: [Choosing parameter tiers](https://docs.aws.amazon.com/systems-manager/latest/userguide/parameter-store-advanced-parameters.html)

### 5.5 Versioning
Every update to a parameter's value creates a new sequential version. Parameter Store **retains the 100 most recently created versions**; once that limit is exceeded, the oldest version is deleted automatically when a new one is created. Unlike Secrets Manager, there are no `AWSCURRENT`/`AWSPENDING`-style staging labels — retrieval is by version number or, by default, the latest.

### 5.6 Parameter Policies (Advanced Tier Only)
Policies let you attach lifecycle rules to a parameter — useful for forcing periodic review of long-lived static credentials or configuration since Parameter Store has no native rotation:

- **`Expiration`** — automatically deletes the parameter at a specified timestamp
- **`ExpirationNotification`** — fires an EventBridge event a configurable number of days/hours *before* expiration
- **`NoChangeNotification`** — fires an EventBridge event if the parameter hasn't been modified within a specified window (e.g., flag a password that hasn't rotated in 60 days)

You can attach up to 10 policies to a single parameter, and policies are enforced via asynchronous periodic scans (no extra action needed after creation). AWS explicitly notes: **to implement true rotation lifecycles, use Secrets Manager** — policies only notify/expire, they don't rotate.

Example CloudFormation snippet:
```yaml
Policies: '[
  {"Type":"Expiration","Version":"1.0","Attributes":{"Timestamp":"2027-05-13T00:00:00.000Z"}},
  {"Type":"ExpirationNotification","Version":"1.0","Attributes":{"Before":"5","Unit":"Days"}},
  {"Type":"NoChangeNotification","Version":"1.0","Attributes":{"After":"60","Unit":"Days"}}
]'
```

Docs: [Assigning parameter policies](https://docs.aws.amazon.com/systems-manager/latest/userguide/parameter-store-policies.html)

### 5.7 Encryption
`SecureString` parameters are encrypted with AWS KMS — either the AWS-managed key or a customer-managed key for tighter access control. AWS recommends using a customer-managed key plus CloudTrail monitoring if you need fine-grained access control over `SecureString` parameters. Note that Standard and Advanced tier parameters use different underlying encryption mechanics, which is one reason Advanced parameters can't be downgraded.

### 5.8 Access Control
- IAM policies can scope access down to individual parameter paths (e.g., permit `ssm:GetParameter` only for names beginning with `prod-` or under `/prod/*`)
- Nodes/instances get access via attached IAM roles
- Resource-level and path-based conditions let you segregate dev/staging/prod configuration cleanly within one flat namespace

Docs: [Setting up Parameter Store](https://docs.aws.amazon.com/systems-manager/latest/userguide/parameter-store-setting-up.html)

### 5.9 Cross-Account Sharing
Advanced-tier parameters can be shared with other AWS accounts using **AWS Resource Access Manager (RAM)**, letting you centralize configuration in one account and share read access with accounts that need it. Standard-tier parameters do not support cross-account sharing.

Docs: [Working with shared parameters](https://docs.aws.amazon.com/systems-manager/latest/userguide/parameter-store-shared-parameters.html)

### 5.10 Throughput
By default, Parameter Store API interactions (Standard tier) are free regardless of volume. You can opt in to a **higher throughput** setting per account/Region, at which point **all** API interactions (Standard and Advanced) are billed per interaction. This is useful for high-frequency polling patterns but converts what's normally a free service into a metered one — worth watching if applications poll rather than cache.

### 5.11 Notifications
Parameter Store integrates with **Amazon EventBridge** to emit change events (parameter created/updated/deleted, or via the policies above), which you can route to Lambda, SNS, or other targets for automated response.

### 5.12 Pricing (as of 2026)
- **Standard parameters: free**, no limit on API calls at default throughput
- **Advanced parameters: $0.05 per parameter per month**, prorated hourly
- **Higher-throughput API interactions (if enabled): $0.05 per 10,000 interactions** — applies to both Standard and Advanced parameters once enabled
- A "Parameter Store API interaction" is counted per parameter touched — e.g., a `GetParameters` call returning 10 parameters counts as 10 interactions

Worked example from AWS's own pricing page: with 5,000 parameters (500 of them Advanced) and 20M monthly API interactions under higher throughput: 500 Advanced parameters × $0.05 = $25, plus 20M interactions × ($0.05/10,000) = $100 → **$125/month total**.

Official pricing page: https://aws.amazon.com/systems-manager/pricing/#Parameter_Store

### 5.13 Quotas Worth Knowing
- 10,000 Standard parameters / 100,000 Advanced parameters, per account per Region
- 4 KB (Standard) / 8 KB (Advanced) max value size
- Up to 100 versions retained per parameter (oldest auto-pruned)
- Up to 10 policies per parameter (Advanced only)
- Parameters are **not** referenceable or nestable inside the value of another parameter
- After deleting a parameter, wait at least 30 seconds before recreating one with the same name

Docs: [Systems Manager endpoints and quotas — Parameter Store](https://docs.aws.amazon.com/general/latest/gr/ssm.html#parameter-store)

### 5.14 Native Integrations
- **ECS/Fargate** — inject parameter values as container environment variables
- **AWS CloudFormation** — templates reference parameters directly (`AWS::SSM::Parameter`, `{{resolve:ssm:...}}` dynamic references)
- **AWS AppConfig** — configuration profiles can source values from Parameter Store, enabling gradual rollouts, alarm-based rollbacks, and validation
- **AWS CodeBuild** — build-time environment variables resolved from Parameter Store
- **Amazon EC2** — reference a parameter for an AMI ID instead of hardcoding it
- **AWS Lambda** — read parameters at cold start, or use the SSM/Secrets Manager Lambda extension for local caching

---

## 6. Side-by-Side Feature Matrix

| Feature | Secrets Manager | Parameter Store (Standard) | Parameter Store (Advanced) |
|---|---|---|---|
| Storage cost | $0.40/secret/month | Free | $0.05/parameter/month |
| API call cost | $0.05/10,000 calls | Free (unless higher throughput enabled) | Free (unless higher throughput enabled) |
| Max value size | 64 KB | 4 KB | 8 KB |
| Max items per account/Region | Effectively unlimited (quota-adjustable) | 10,000 | 100,000 |
| Encryption | KMS (always) | KMS (`SecureString` only) | KMS (`SecureString` only) |
| Automatic rotation | ✅ Native (Lambda templates + managed rotation) | ❌ | ❌ |
| Staged versioning (current/pending/previous) | ✅ | ❌ (sequential versions only) | ❌ (sequential versions only) |
| Cross-Region replication | ✅ Native, one click | ❌ Manual only | ❌ Manual only |
| Cross-account sharing | ✅ Resource policies | ❌ | ✅ Via AWS RAM |
| Lifecycle policies (expiration/notification) | N/A (rotation covers this) | ❌ | ✅ |
| Hierarchical namespace | ❌ (flat names) | ✅ | ✅ |
| Free tier / no-cost option | ❌ (no permanent free tier) | ✅ | ❌ |
| Ideal payload | Structured JSON credential sets | Small config strings, flags, IDs | Larger config blobs, policy-governed secrets |

---

## 7. Common Architecture Pattern

A typical production setup on AWS doesn't pick one exclusively — it splits by responsibility:

- **Secrets Manager**: RDS/Aurora master and app-user credentials (with alternating-user rotation), third-party API keys (Stripe, Twilio, etc.), OAuth client secrets, anything replicated for multi-Region failover.
- **Parameter Store**: feature flags, service endpoint URLs, AMI IDs, ECS/Fargate environment configuration, non-sensitive tuning values, and `SecureString` values for secrets that are numerous, low-sensitivity, or don't need automatic rotation (e.g., a shared read-only API key used by many services).

Tools like the **AWS Parameter and Secrets Lambda Extension** let a single caching layer read from both services interchangeably, so the choice of backend doesn't have to leak into application code.

---

## 8. Reference Links

**AWS Secrets Manager**
- Overview: https://docs.aws.amazon.com/secretsmanager/latest/userguide/intro.html
- Rotate secrets: https://docs.aws.amazon.com/secretsmanager/latest/userguide/rotating-secrets.html
- Managed rotation: https://docs.aws.amazon.com/secretsmanager/latest/userguide/rotate-secrets_managed.html
- Replicate secrets across Regions: https://docs.aws.amazon.com/secretsmanager/latest/userguide/add-regions.html
- Control access to secrets: https://docs.aws.amazon.com/secretsmanager/latest/userguide/auth-and-access.html
- Monitor secrets for compliance: https://docs.aws.amazon.com/secretsmanager/latest/userguide/configuring-awsconfig-rules.html
- Compliance validation: https://docs.aws.amazon.com/secretsmanager/latest/userguide/secretsmanager-compliance.html
- Quotas: https://docs.aws.amazon.com/secretsmanager/latest/userguide/reference_limits.html
- Pricing: https://aws.amazon.com/secrets-manager/pricing/
- What's new — managed external secrets (MongoDB Atlas, Confluent Cloud): https://aws.amazon.com/about-aws/whats-new/2026/04/secrets-manager-managed-external-secrets-mongodb-confluent/

**AWS Systems Manager Parameter Store**
- Overview: https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-parameter-store.html
- Creating parameters: https://docs.aws.amazon.com/systems-manager/latest/userguide/sysman-paramstore-su-create.html
- Choosing parameter tiers: https://docs.aws.amazon.com/systems-manager/latest/userguide/parameter-store-advanced-parameters.html
- Assigning parameter policies: https://docs.aws.amazon.com/systems-manager/latest/userguide/parameter-store-policies.html
- Setting up Parameter Store (IAM, EventBridge): https://docs.aws.amazon.com/systems-manager/latest/userguide/parameter-store-setting-up.html
- Working with shared parameters: https://docs.aws.amazon.com/systems-manager/latest/userguide/parameter-store-shared-parameters.html
- Systems Manager pricing (Parameter Store section): https://aws.amazon.com/systems-manager/pricing/#Parameter_Store
- Endpoints and quotas: https://docs.aws.amazon.com/general/latest/gr/ssm.html#parameter-store

---

*Pricing and quotas reflect publicly published AWS rates as of September 2026 and are subject to change — always confirm current figures on the official AWS pricing pages linked above before budgeting.*
