# Amazon ECS: A Feature Deep Dive

**Last updated: August 2026**

A practical, in-depth guide to Amazon Elastic Container Service covering the four areas that matter most in production: the **container registry**, **setting up containers**, **orchestrating containers**, and **security**. Each section calls out the ECS primitives involved and the surrounding AWS services you'll typically wire in.

---

## Table of Contents

1. [Orientation: The ECS Object Model](#1-orientation-the-ecs-object-model)
2. [The Registry: Amazon ECR](#2-the-registry-amazon-ecr)
3. [Setting Up Containers: Task Definitions](#3-setting-up-containers-task-definitions)
4. [Orchestrating Containers: Clusters, Services, Deployments, Scaling](#4-orchestrating-containers-clusters-services-deployments-scaling)
5. [Security](#5-security)
6. [Reference: Service Pairing Matrix](#6-reference-service-pairing-matrix)
7. [Reference: Recent Feature Timeline (2025–2026)](#7-reference-recent-feature-timeline-20252026)
8. [Gotchas and Hard-Won Lessons](#8-gotchas-and-hard-won-lessons)

---

## 1. Orientation: The ECS Object Model

Before diving in, it helps to have the vocabulary straight. ECS is a control plane — a "brain" that decides what runs where — not a server.

| Object | What it is |
|---|---|
| **Cluster** | A logical grouping of capacity and services. A namespace boundary, not a physical thing. |
| **Task definition** | An immutable, versioned blueprint (JSON) describing one or more containers that run together. |
| **Task** | A running instantiation of a task definition revision. The unit of scheduling. |
| **Service** | A long-running controller that maintains N healthy tasks, handles deployments, load balancer registration, and scaling. |
| **Container instance** | An EC2 instance registered into a cluster, running the ECS agent. (Not applicable to Fargate.) |
| **Capacity provider** | The interface between a service/task and the compute that runs it. |
| **Service revision** | An immutable snapshot of a service's exact configuration (task definition + LB config + Service Connect config), created on every create/update. |

### The four compute options

| Option | Who manages the host | Best for |
|---|---|---|
| **AWS Fargate** | AWS, entirely. Per-task micro-VM isolation. | Default choice. Stateless web/API, bursty jobs, teams without platform engineers. |
| **ECS Managed Instances** | AWS provisions/patches/replaces EC2 in *your* account | GPUs, network/storage-optimized instances, Reserved Instances/Savings Plans, without running the instance lifecycle yourself. Launched Sept 2025. |
| **EC2 launch type** | You (ASG, AMI, patching, bin packing) | Deep host access, custom AMIs, host-level daemons, maximum cost control. |
| **External (ECS Anywhere)** | You, on-premises or other clouds | Hybrid workloads managed through the ECS control plane via SSM. |

Fargate now supports task sizes up to **32 vCPU** with 60, 120, or 244 GiB of memory on both x86 and ARM/Graviton Linux — enough for large data processing and AI inference workloads that previously forced you onto EC2.

**A note on Express Mode:** ECS Express Mode (launched November 2025) is not a separate service. It's a front door to ECS that takes three inputs — a container image, a task execution role, and an infrastructure role — and provisions the Fargate service, ALB, HTTPS listener, target group, security groups, auto scaling policies, and a public `*.ecs.<region>.on.aws` URL for you. Up to 25 services can share a single ALB via host-header routing. As of mid-2026 it also accepts **custom task definitions**, so you can add observability/security sidecars, custom health checks, ulimits, and FireLens log routing while keeping the managed infrastructure. Use it to skip the undifferentiated setup; drop to full ECS when you need NLB ingress, multiple ALBs, or a Service Connect mesh.

---

## 2. The Registry: Amazon ECR

Amazon Elastic Container Registry is the OCI-compliant registry that sits at the head of every ECS supply chain. A compromised registry means an attacker controls what runs in production, so treat this section as both an operations and a security topic.

### 2.1 Registry, repository, image

- **Private registry**: every AWS account gets one per region, addressed as `<account-id>.dkr.ecr.<region>.amazonaws.com`.
- **Public registry**: ECR Public (`public.ecr.aws`) for distributing images to the world, backed by the ECR Public Gallery.
- **Repository**: a named collection of images (`my-app`), holding tagged and untagged manifests plus layers.
- **Image**: identified by digest (`sha256:...`) and zero or more tags.

Repositories can now be **created automatically on push** (launched December 2025) using a namespace-scoped creation template, which removes the "repo doesn't exist" failure from CI pipelines. Templates let you pre-apply encryption settings, tag immutability, lifecycle policy, and repository policy to every auto-created repo.

### 2.2 Authentication

There are no registry usernames or passwords. A client exchanges IAM credentials for a **12-hour authorization token** whose permission scope matches the IAM principal that requested it.

```bash
aws ecr get-login-password --region us-east-1 \
  | docker login --username AWS --password-stdin \
    123456789012.dkr.ecr.us-east-1.amazonaws.com
```

For ECS itself, the **task execution role** pulls the image — you never hand credentials to the task. For third-party or on-prem registries, ECS supports `repositoryCredentials` pointing at an **AWS Secrets Manager** secret.

**Involved services:** IAM (identity), Secrets Manager (external registry creds), STS (token exchange).

### 2.3 Tag immutability and mutability exclusions

Set a repository to `IMMUTABLE` and a tag can never be reassigned to a different digest. This is the single highest-value setting for supply-chain integrity: it means `my-app:v1.4.2` in your task definition can't silently become different code.

The pragmatic problem is that you usually want `latest`, `nightly`, or `dev-*` to stay mutable. ECR supports **immutability exclusion patterns** — configure the repository as immutable but exclude specific tag patterns (e.g. `latest`, `dev-*`) from the rule.

### 2.4 Lifecycle policies

Registry storage is billed per GB-month and untagged layers accumulate fast. Lifecycle policies are JSON rules evaluated on a schedule; expiry events land in **CloudTrail** for audit.

```json
{
  "rules": [
    {
      "rulePriority": 1,
      "description": "Keep last 30 release images",
      "selection": {
        "tagStatus": "tagged",
        "tagPrefixList": ["release-"],
        "countType": "imageCountMoreThan",
        "countNumber": 30
      },
      "action": { "type": "expire" }
    },
    {
      "rulePriority": 2,
      "description": "Expire untagged images after 7 days",
      "selection": {
        "tagStatus": "untagged",
        "countType": "sinceImagePushed",
        "countUnit": "days",
        "countNumber": 7
      },
      "action": { "type": "expire" }
    }
  ]
}
```

Rules evaluate lowest-priority-number first, and an image matched by an earlier rule is not re-evaluated. Always test with `aws ecr start-lifecycle-policy-preview` before applying.

**Related:** ECR also offers an **archive storage class** for images you must retain for compliance but rarely pull — cheaper storage in exchange for a restore step.

### 2.5 Replication

ECR supports **cross-region** and **cross-account** replication driven by a registry-level replication configuration and a service-linked role. Typical uses:

- Multi-region active/active ECS services pulling from an in-region replica (lower latency, no cross-region data transfer on pull).
- A central "build" account pushing once, replicating into `dev`/`staging`/`prod` accounts.
- Disaster recovery.

Replication is push-based and eager: everything matching the filter gets copied. Which brings us to the alternative.

### 2.6 Pull-through cache

Pull-through cache (PTC) rules lazily mirror an upstream registry into your private ECR, caching only images that are actually pulled. Supported upstreams now include **Docker Hub, GitHub Container Registry, Quay, ECR Public, Azure Container Registry, GitLab Container Registry, the Kubernetes registry, Chainguard** (added March 2026), and **other ECR private registries** (ECR-to-ECR, added March 2025).

Why it matters:

- **Docker Hub rate limits disappear** for your build fleet and your ECS task launches.
- **Availability**: an upstream outage doesn't stall your deployments.
- **Governance**: cached third-party images inherit your ECR lifecycle policies, encryption, and enhanced scanning.
- PTC keeps cached images in sync with upstream (syncing at least once every 24 hours), and auto-creates the downstream repository.

As of April 2026, PTC also **discovers and syncs OCI referrers** — signatures, SBOMs, and attestations — from the upstream registry. Before this, listing referrers on a PTC repository returned nothing and you had to fetch them manually. Now end-to-end signature verification and SBOM discovery work against cached repositories without client-side workarounds.

ECR-to-ECR PTC is often a better fit than replication for large registries: you get cross-region/cross-account distribution while paying to store only what's genuinely used.

### 2.7 Image scanning

Two modes, configured at the **registry level** (the old repository-level `PutImageScanningConfiguration` API is deprecated):

**Basic scanning** — free, OS package CVEs, scan-on-push or manual. Note that the older Clair-based engine was **fully deprecated on February 2, 2026**; all accounts now use Amazon's native scanning engine, which covers a broader set of operating systems with better findings.

**Enhanced scanning** — powered by **Amazon Inspector**. Continuous and automatic rather than point-in-time. Covers OS packages *and* language dependencies (Python, Java, Node.js, Go, .NET, Ruby, PHP, Rust). Recent expansions include support for **scratch, distroless (Debian/Ubuntu-based), and Chainguard images**, plus coverage for Go toolchains, Oracle JDK, Amazon Corretto, Apache Tomcat, and WordPress. Inspector also surfaces **image usage insights** — which ECS/EKS clusters are running an image, when it was last pulled, and how many clusters reference it — so you can triage by blast radius instead of raw CVSS score.

Findings flow to **Amazon Inspector** → **AWS Security Hub** → **Amazon EventBridge**, where you can trigger a **Lambda** function to fail a build, quarantine an image, or open a ticket.

```bash
# Registry-wide: enhanced continuous scanning on everything
aws ecr put-registry-scanning-configuration \
  --scan-type ENHANCED \
  --rules '[{
    "scanFrequency": "CONTINUOUS_SCAN",
    "repositoryFilters": [{"filter": "*", "filterType": "WILDCARD"}]
  }]'
```

### 2.8 Image signing

ECR supports **managed container image signing**: when an image is pushed, ECR can automatically sign it using the identity of the pushing principal, with no signing infrastructure for you to operate. Signatures are stored as OCI referrer artifacts alongside the image and are billed per signature. This eliminates the traditional setup burden of **AWS Signer** + Notation + key management, though that path remains available if you need custom trust policies.

Combined with PTC referrer sync (§2.6) and admission-time verification, this gives you a genuine provenance chain: *this image was pushed by this CI role, and nothing has modified it since.*

### 2.9 Encryption and network isolation

- **At rest:** AES-256 with S3-managed keys by default, or **AWS KMS** customer-managed keys (CMKs) for key rotation control, cross-account grants, and CloudTrail-logged key usage. Set at repository creation — it can't be changed later.
- **In transit:** TLS on all push and pull operations.
- **Private connectivity:** **VPC interface endpoints (AWS PrivateLink)** for `ecr.api` and `ecr.dkr`, plus an **S3 gateway endpoint** (layers live in S3). This lets tasks in private subnets pull images with no NAT gateway and no internet route — a cost saving as well as a security control. ECR endpoints now support **dual-stack IPv4/IPv6** (added November 2025).

### 2.10 CI/CD integration

A typical build path: **CodePipeline** (or GitHub Actions) → **CodeBuild** (docker build, multi-arch via buildx) → push to **ECR** → EventBridge rule on the `ECR Image Action` event → update the ECS service. **CodeBuild** can build ARM images natively on Graviton for cheaper Fargate runtime.

**Involved services this section:** IAM, KMS, S3, Amazon Inspector, AWS Signer, Security Hub, EventBridge, CloudTrail, CloudWatch, Lambda, PrivateLink/VPC endpoints, CodeBuild, CodePipeline, Secrets Manager.

---

## 3. Setting Up Containers: Task Definitions

The task definition is where nearly all container-level configuration lives. It's a **family** (name) with numbered, immutable **revisions**. Registering a new revision never mutates an old one, which is what makes rollback trivial.

### 3.1 Task-level fields

```jsonc
{
  "family": "checkout-api",
  "requiresCompatibilities": ["FARGATE"],
  "networkMode": "awsvpc",
  "cpu": "1024",                          // 1 vCPU
  "memory": "2048",                       // 2 GB
  "executionRoleArn": "arn:aws:iam::123456789012:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::123456789012:role/checkoutApiTaskRole",
  "runtimePlatform": {
    "cpuArchitecture": "ARM64",           // Graviton — cheaper per vCPU-hour
    "operatingSystemFamily": "LINUX"
  },
  "ephemeralStorage": { "sizeInGiB": 50 },
  "containerDefinitions": [ /* ... */ ]
}
```

**CPU/memory:** on Fargate these are fixed valid pairs (0.25 vCPU with 0.5–2 GB, up to 32 vCPU with 60/120/244 GB). On EC2 they're soft: task-level `cpu` becomes a CPU-share weighting, and container-level `memoryReservation` is the soft floor while `memory` is the hard kill limit.

**Network modes:**

| Mode | Behaviour |
|---|---|
| `awsvpc` | Each task gets its own ENI, private IP, and security groups. **Required on Fargate**, strongly recommended on EC2. |
| `bridge` | Docker's default virtual network on EC2. Needed for dynamic host port mapping with old-style ALB target groups. |
| `host` | Container binds the instance's network interface directly. Lowest overhead, no port flexibility. |
| `none` | No external connectivity. |

`awsvpc` is what makes per-task security groups, VPC Flow Logs per task, and PrivateLink-only egress possible. It's the foundation of the security section below.

### 3.2 Container definitions

```jsonc
{
  "name": "app",
  "image": "123456789012.dkr.ecr.us-east-1.amazonaws.com/checkout-api@sha256:abc123...",
  "essential": true,
  "cpu": 768,
  "memoryReservation": 1024,
  "portMappings": [
    { "name": "http", "containerPort": 8080, "protocol": "tcp", "appProtocol": "http" }
  ],
  "environment": [
    { "name": "LOG_LEVEL", "value": "info" }
  ],
  "environmentFiles": [
    { "type": "s3", "value": "arn:aws:s3:::my-config/checkout.env" }
  ],
  "secrets": [
    { "name": "DB_PASSWORD", "valueFrom": "arn:aws:secretsmanager:us-east-1:123456789012:secret:prod/db-AbCdEf" },
    { "name": "API_KEY",     "valueFrom": "arn:aws:ssm:us-east-1:123456789012:parameter/prod/api-key" }
  ],
  "healthCheck": {
    "command": ["CMD-SHELL", "curl -f http://localhost:8080/healthz || exit 1"],
    "interval": 15, "timeout": 5, "retries": 3, "startPeriod": 30
  },
  "readonlyRootFilesystem": true,
  "user": "1001:1001",
  "linuxParameters": {
    "initProcessEnabled": true,
    "capabilities": { "drop": ["ALL"] }
  },
  "ulimits": [{ "name": "nofile", "softLimit": 65536, "hardLimit": 65536 }],
  "stopTimeout": 30,
  "logConfiguration": {
    "logDriver": "awslogs",
    "options": {
      "awslogs-group": "/ecs/checkout-api",
      "awslogs-region": "us-east-1",
      "awslogs-stream-prefix": "app",
      "awslogs-create-group": "true"
    }
  }
}
```

Key points:

- **Pin by digest**, not by tag, in production. It removes an entire class of "which build is actually running?" incidents. (Tag immutability in ECR gets you most of the way, but digests are absolute.)
- **`essential`**: if an essential container exits, the whole task stops. Sidecars are usually non-essential — with the important exception of log routers and proxies, where you often *do* want the task to die if they're gone.
- **`environmentFiles`**: bulk env vars from an **S3** object, so you're not editing hundreds of JSON entries.
- **`secrets`** injects from **Secrets Manager** or **SSM Parameter Store** at container start. The values never appear in the task definition, in `DescribeTaskDefinition` output, or in the console.
- **`startPeriod`** on health checks is the most commonly missed field. Without it, slow-starting JVM or .NET apps get killed in a restart loop.
- **`stopTimeout`** (up to 120s on Fargate) is your graceful-shutdown window: ECS sends `SIGTERM`, waits, then `SIGKILL`.

### 3.3 Container dependencies and startup ordering

```jsonc
"dependsOn": [
  { "containerName": "config-init", "condition": "SUCCESS" },
  { "containerName": "envoy",       "condition": "HEALTHY" }
]
```

Conditions are `START`, `COMPLETE`, `SUCCESS`, and `HEALTHY`. This is how you build init containers (run a migration, exit 0, then the app starts) and how you guarantee a service mesh proxy is ready before the app sends its first request.

### 3.4 The sidecar patterns you'll actually use

| Sidecar | Purpose | AWS services involved |
|---|---|---|
| **FireLens (Fluent Bit)** | Route logs anywhere — filter, enrich, multi-destination | CloudWatch Logs, **Kinesis Data Firehose**, **Kinesis Data Streams**, OpenSearch, S3, Datadog/Splunk |
| **AWS Distro for OpenTelemetry (ADOT)** | Traces + metrics collection | X-Ray, CloudWatch, Amazon Managed Prometheus |
| **ECS Service Connect agent** | Managed Envoy proxy, injected automatically | Cloud Map, CloudWatch |
| **GuardDuty security agent** | Runtime threat detection, injected automatically | GuardDuty, Security Hub |
| **X-Ray daemon** | Legacy tracing (prefer ADOT for new work) | X-Ray |

FireLens deserves special mention because it's the standard answer to "how do I get container logs into an analytics pipeline." A minimal config:

```jsonc
{
  "name": "log_router",
  "image": "public.ecr.aws/aws-observability/aws-for-fluent-bit:stable",
  "essential": true,
  "firelensConfiguration": { "type": "fluentbit", "options": { "enable-ecs-log-metadata": "true" } },
  "memoryReservation": 128
}
```

Then on the app container:

```jsonc
"logConfiguration": {
  "logDriver": "awsfirelens",
  "options": {
    "Name": "kinesis_firehose",
    "region": "us-east-1",
    "delivery_stream": "app-logs-to-s3"
  }
}
```

From Firehose the logs can fan out to S3 (cheap long-term), OpenSearch (search), or a Lambda transform. If you need real-time consumers with replay — fraud detection, live dashboards — target **Kinesis Data Streams** instead.

### 3.5 Storage

| Volume type | Use case | Notes |
|---|---|---|
| **Ephemeral (task scratch)** | Temp files, caches | 20 GiB free on Fargate, configurable up to 200 GiB. Encrypted by default. |
| **Bind mounts** | Sharing a directory between containers in a task | The standard way to pass files from an init container to the app. |
| **Amazon EFS** | Shared, persistent, multi-AZ POSIX filesystem | Works on Fargate and EC2. Supports IAM authorization and TLS in transit via access points. |
| **Amazon EBS** | High-IOPS, task-scoped block storage | Attached at task launch: specify size, type, IOPS, throughput, KMS key, and optionally a snapshot ID in `RunTask`/`CreateService`/`UpdateService`. Great for ETL, media transcoding, ML inference. Now available in GovCloud too. |
| **Amazon FSx for Windows File Server** | SMB shares for Windows containers | EC2 launch type only. |
| **Docker volumes** | Local persistence on EC2 | EC2 only; ties the task to a host. |

The EBS integration is the one people miss. It gives a task a dedicated, encrypted, high-performance volume that can be pre-seeded from a snapshot — which is a very clean way to ship a large model or dataset to an inference task without a slow S3 sync on startup.

### 3.6 Platform-specific configuration

- **Graviton/ARM64**: set `runtimePlatform.cpuArchitecture` to `ARM64`. Roughly 20% cheaper per vCPU-hour on Fargate with typically better price-performance. Requires multi-arch images (build with `docker buildx`).
- **GPU**: on EC2 or ECS Managed Instances, request `resourceRequirements` of type `GPU`. Managed Instances surfaces **NVIDIA GPU metrics** — utilization, memory, temperature, hardware health — through **CloudWatch Container Insights with enhanced observability**, and automatically detects GPU hardware failures and replaces unhealthy instances. GPU management fees for Managed Instances dropped in July 2026 (35% for G-series, 60% for P-series and Trainium).
- **Windows**: `operatingSystemFamily` of `WINDOWS_SERVER_2019_CORE`, `WINDOWS_SERVER_2022_FULL`, etc. Supported on both Fargate and EC2, with a narrower feature set (no `awsvpc` trunking, no EFS on Fargate Windows).

### 3.7 ECS Exec: interactive debugging

`enableExecuteCommand` on the task/service opens an interactive shell into a running container through **AWS Systems Manager Session Manager** — no SSH, no bastion, no inbound ports.

```bash
aws ecs execute-command \
  --cluster prod \
  --task 1234abcd... \
  --container app \
  --interactive \
  --command "/bin/sh"
```

Requirements: the **task role** needs `ssmmessages:*` permissions, the SSM agent bits ship with the Fargate platform, and you need connectivity to the SSM endpoints (or PrivateLink endpoints for `ssm`, `ssmmessages`, `ec2messages`). Session activity can be logged to CloudWatch Logs or S3 with optional KMS encryption — audit this, because it's a legitimate path to production data.

**Involved services this section:** ECR, Secrets Manager, SSM Parameter Store, KMS, S3, CloudWatch Logs, Kinesis Data Firehose, Kinesis Data Streams, OpenSearch, EFS, EBS, FSx, X-Ray, Systems Manager, CloudWatch Container Insights.

---

## 4. Orchestrating Containers: Clusters, Services, Deployments, Scaling

### 4.1 Clusters and capacity providers

A cluster is a boundary for capacity, services, and (optionally) a Service Connect namespace. Capacity providers are the interface through which you attach compute.

Every cluster automatically has `FARGATE` and `FARGATE_SPOT`. You can add:

- **Auto Scaling group capacity providers** — an ASG plus optional **managed scaling** (ECS publishes a `CapacityProviderReservation` metric and drives the ASG to a target utilization) and **managed termination protection** (instances running tasks aren't scaled in).
- **ECS Managed Instances capacity providers** — you declare task requirements (vCPU, memory, architecture, optionally instance families) and ECS provisions, configures, patches, and operates cost-optimized EC2 instances in your account using AWS-controlled access. ECS first tries to bin-pack new tasks onto already-running managed instances, and only launches new instances for what won't fit.

A **capacity provider strategy** distributes tasks across providers with `base` and `weight`:

```json
"capacityProviderStrategy": [
  { "capacityProvider": "FARGATE",      "base": 4, "weight": 1 },
  { "capacityProvider": "FARGATE_SPOT", "base": 0, "weight": 4 }
]
```

This reads as: always keep at least 4 tasks on on-demand Fargate, then split additional tasks 1:4 in favour of Spot. This is the standard cost pattern — guaranteed baseline capacity plus cheap burst. Handle `SIGTERM` properly, because Spot interruption gives you a 2-minute warning delivered via **EventBridge**.

### 4.2 Scheduling: services vs. standalone tasks

**Services** (`REPLICA` strategy) maintain a desired count, replace unhealthy tasks, spread across AZs, and manage load balancer registration and deployments. **`DAEMON`** strategy runs exactly one task per container instance — for log collectors, monitoring agents, and node-level utilities on EC2. (There's also the newer concept of ECS **Managed Daemons** for AWS-provided node agents.)

**Standalone tasks** via `RunTask` are for batch and event-driven work. The common triggers:

| Trigger | Pattern |
|---|---|
| **EventBridge Scheduler** | Cron/rate-based jobs — nightly reports, cleanup, ETL |
| **EventBridge rules** | React to an S3 upload, an ECR push, a CodePipeline state change |
| **Step Functions** | `ecs:runTask.sync` as a step in a workflow, with retries, parallelism, and error handling. The best option for multi-stage pipelines. |
| **AWS Batch** | Queue-based array jobs with priorities and compute environments; Batch runs on ECS underneath |
| **SQS + service auto scaling** | Long-running consumer service scaled on queue depth (see §4.6) |
| **Lambda** | Calls `RunTask` when a job exceeds Lambda's 15-minute limit or needs >10 GB memory |

### 4.3 Task placement (EC2 and Managed Instances)

Fargate handles placement for you. On EC2, you control it:

**Placement strategies** — `spread` (across `attribute:ecs.availability-zone` or `instanceId` for HA), `binpack` (on `cpu` or `memory`, to minimize instance count and cost), `random`. They're evaluated in order, so a common production combination is spread across AZs, then binpack on memory.

**Placement constraints** — `distinctInstance` (no two tasks of this service on the same host) or a `memberOf` expression using the Cluster Query Language:

```
attribute:ecs.instance-type =~ c6i.* and attribute:ecs.os-type == linux
```

Custom attributes on container instances let you carve a shared cluster into pools (e.g. `attribute:workload == gpu-inference`).

### 4.4 Deployments

This is where ECS has changed most in the last 18 months.

Every create/update produces an immutable **service revision** capturing the task definition, load balancer configuration, and Service Connect configuration together — which is what makes rollback restore *exactly* the previous environment rather than just the previous task definition.

**Rolling update** (default). Governed by `minimumHealthyPercent` and `maximumPercent`. `100/200` means "double capacity, then drain the old" — safe, needs headroom. `50/100` means "kill half first" — cheap, briefly degraded.

**Blue/green** (built into ECS since July 2025 — no CodeDeploy required). ECS provisions the green revision alongside blue, lets you validate it, then shifts production traffic. Works with **ALB**, **NLB**, and **ECS Service Connect**.

**Linear and canary** strategies are also built in, shifting production traffic in increments rather than all at once.

The three controls that make these safe:

1. **Deployment lifecycle hooks** — synchronous **Lambda** functions ECS invokes at defined stages, which can *block* the deployment until validation passes. The six hook points are `pre-scale-up`, `post-scale-up`, `test-traffic-shift`, `post-test-traffic-shift`, `production-traffic-shift`, and `post-production-traffic-shift`. Use them for smoke tests, contract tests, manual approvals, or metric gates.
2. **Bake time** — how long instant rollback to blue stays available after production traffic shifts. Rollback here is fast because the blue tasks are still running; it's a listener-rule change, not a task launch.
3. **Automatic rollback** — the **deployment circuit breaker** (rolls back after repeated task launch failures) plus **CloudWatch alarms** attached to the deployment (rolls back on an error-rate or latency alarm).

A "dark canary" pattern falls out of this naturally: configure a **test listener** on the ALB with its own rule, send synthetic traffic to green through it, run your lifecycle-hook test suite, and only then shift real users.

One constraint worth knowing: you can change a service's deployment controller after creation, **unless** the service uses **VPC Lattice** or **Service Connect**.

**Deployment observability** got a significant upgrade in mid-2026. The ECS console now shows a **live deployment timeline** with phases, service events, and task launch/termination progress, plus real-time circuit breaker status (including failure proximity to the threshold), deployment alarm state, and health checks at both container and load-balancer level. Failed tasks appear inline with diagnostic context and deep links. Separately, **Action Logs** deliver timestamped records of the actions ECS takes on your behalf during service deployments and Managed Daemon updates — event name, log level, resource ARNs, and status reason — surfacing service-side operations that were previously invisible without opening a support case.

### 4.5 Load balancing and service networking

| Option | When |
|---|---|
| **Application Load Balancer (ALB)** | HTTP/HTTPS, path/host routing, WebSockets, gRPC, OIDC/Cognito auth at the edge, WAF attachment. The default for web services. |
| **Network Load Balancer (NLB)** | TCP/UDP/TLS, ultra-low latency, static IPs, PrivateLink service endpoints. |
| **API Gateway** | REST/HTTP APIs needing throttling, API keys, usage plans, request validation, or per-route Lambda authorizers. Fronts a private ALB/NLB via a **VPC Link**, or an NLB directly. |
| **VPC Lattice** | Application networking across VPCs and accounts with auth policies, without VPC peering or Transit Gateway. ECS services register as Lattice targets. |
| **ECS Service Connect** | Service-to-service inside/across clusters. |
| **AWS Cloud Map** | DNS-based service discovery (the older `serviceRegistries` integration). |

**Service Connect** is the recommended internal-networking approach. You declare a namespace and logical port names; ECS injects and manages an Envoy proxy sidecar, gives you a stable short DNS name (`http://checkout:8080`) regardless of task IPs, and adds client-side load balancing, automatic retries, outlier detection, and per-connection metrics in CloudWatch — without you running a control plane. Critically, it keeps service-to-service traffic correct *during* deployments, which is exactly where plain DNS-based discovery gets flaky due to caching.

```jsonc
"serviceConnectConfiguration": {
  "enabled": true,
  "namespace": "prod.internal",
  "services": [{
    "portName": "http",
    "discoveryName": "checkout",
    "clientAliases": [{ "port": 8080, "dnsName": "checkout" }]
  }]
}
```

A typical full ingress stack: **Route 53** → **CloudFront** (+ **AWS WAF**, **Shield**) → **ALB** (TLS cert from **ACM**) → ECS service, with internal calls going over **Service Connect**.

### 4.6 Scaling

**Service auto scaling** runs on **Application Auto Scaling** and adjusts `desiredCount`:

- **Target tracking** — keep a metric at a target (e.g. `ECSServiceAverageCPUUtilization` at 65%, or ALB `RequestCountPerTarget`). The default choice.
- **Step scaling** — thresholded steps on a CloudWatch alarm. Best for custom metrics like SQS `ApproximateNumberOfMessagesVisible` per task (use a math expression for backlog-per-task).
- **Scheduled scaling** — for known events: business hours, batch windows, a Black Friday ramp.
- **Predictive scaling** — forecasts recurring traffic patterns and scales ahead of them.

In June 2026 ECS shipped **high-resolution (20-second) metrics** for CPU and memory target tracking, alongside metric publishing optimizations. In AWS's benchmarks, time to trigger scale-out went from 363 seconds to 86 seconds (about 4.2× faster), and total time to scale and provision new tasks went from 386 seconds to 109 seconds (about 3.5× faster). The practical consequence: you can lower your baseline task count, because scale-out is now fast enough to absorb spikes without pre-padding capacity. It's available across Fargate, ECS Managed Instances, and EC2 in all commercial and GovCloud (US) regions. The feature itself is free, but high-resolution CloudWatch metrics are a billable dimension.

**Cluster capacity scaling** (EC2 path) is separate: capacity provider managed scaling drives the ASG so there's somewhere for new tasks to land. Get both layers right or your service scales out into `PROVISIONING` purgatory.

### 4.7 Observability

- **CloudWatch Container Insights** — cluster/service/task metrics; *enhanced observability* adds container-level granularity and, on Managed Instances, GPU device-level metrics.
- **CloudWatch Logs** — via the `awslogs` driver or FireLens.
- **CloudWatch Application Signals** — service-level objectives and dependency maps.
- **AWS X-Ray / ADOT** — distributed tracing; ADOT also exports to **Amazon Managed Service for Prometheus** and **Amazon Managed Grafana**.
- **EventBridge** — ECS emits task state change and deployment state change events. Route them to Lambda, SNS, or a Slack notifier.
- **Action Logs** and **console deployment observability** — see §4.4.

**Involved services this section:** ELB (ALB/NLB), API Gateway, VPC Lattice, Cloud Map, Route 53, CloudFront, ACM, Application Auto Scaling, CloudWatch (metrics, alarms, Logs, Container Insights, Application Signals), EventBridge, EventBridge Scheduler, Step Functions, AWS Batch, SQS, SNS, Lambda, EC2 Auto Scaling, X-Ray, Managed Prometheus, Managed Grafana.

---

## 5. Security

ECS security is layered. A useful mental model: **identity → network → supply chain → runtime → compliance**. Each layer assumes the one before it may fail.

The threat is not theoretical. In November 2025 GuardDuty detected an active campaign in which attackers used compromised IAM credentials to spin up 50+ ECS clusters per account and launch cryptomining Fargate tasks from a public Docker Hub image within ten minutes of initial access — while setting `disableApiTermination` to slow down cleanup. Every control below maps to a step in that kill chain.

### 5.1 Identity: the four roles you must keep straight

This is the most common source of over-privileged containers.

| Role | Assumed by | Grants |
|---|---|---|
| **Task role** (`taskRoleArn`) | **Your application code**, at runtime | Access to S3, DynamoDB, SQS, etc. Scope this tightly — it's what an app compromise gets the attacker. |
| **Task execution role** (`executionRoleArn`) | **The ECS agent / Fargate infrastructure**, before your container starts | Pull from ECR, write to CloudWatch Logs, read Secrets Manager/SSM values named in the task definition, manage the GuardDuty agent |
| **Container instance role** (EC2) | **The EC2 host's ECS agent** | Register into the cluster, report task state |
| **Service-linked role** (`AWSServiceRoleForECS`) | **ECS itself** | Manage ENIs, register targets with load balancers |

Two rules that prevent most incidents:

1. **Never put application permissions in the execution role.** They're distinct roles for a reason: the execution role runs with host-adjacent privilege before your code does.
2. **One task role per service**, not one shared role per cluster. Use condition keys to scope further:

```json
{
  "Effect": "Allow",
  "Action": "secretsmanager:GetSecretValue",
  "Resource": "arn:aws:secretsmanager:us-east-1:123456789012:secret:prod/checkout/*"
}
```

Credentials reach the container through a task-local **credential provider endpoint** (`169.254.170.2`) — short-lived and auto-rotated. Applications should use the AWS SDK's default credential chain and never handle static keys.

**IMDS hardening (EC2 only):** on the EC2 launch type, a container in `bridge` mode can potentially reach the instance metadata service and steal the *instance* role. Enforce IMDSv2 (`HttpTokens: required`), set `HttpPutResponseHopLimit: 1`, and prefer `awsvpc` mode. Fargate has no IMDS exposure of this kind.

### 5.2 Network security

- **`awsvpc` mode + per-task security groups.** Each task gets its own ENI, so you can write security groups that reference *other security groups* rather than CIDR ranges: "the checkout service SG may receive port 8080 from the API gateway service SG." Least privilege at the network layer.
- **Private subnets by default.** Tasks should have no public IP. Egress goes through a NAT gateway, or better, through VPC endpoints.
- **VPC endpoints (PrivateLink).** For a fully private task, you'll typically want interface endpoints for `ecr.api`, `ecr.dkr`, `logs`, `secretsmanager`, `ssm`, `ssmmessages`, `ec2messages`, `sts`, `ecs`, `ecs-agent`, `ecs-telemetry`, plus an **S3 gateway endpoint**. Endpoint policies add another authorization layer.
- **VPC Flow Logs** per ENI — with `awsvpc`, that means per-task network visibility.
- **AWS WAF** on the ALB or CloudFront for OWASP rules, rate limiting, and bot control. **AWS Shield Advanced** for DDoS.
- **VPC Lattice auth policies** for cross-VPC/cross-account service-to-service authorization using IAM, without network-level peering.
- **AWS Network Firewall** for egress filtering when you need to restrict which domains tasks may reach.

### 5.3 Secrets and configuration

Never bake secrets into images or plain `environment` variables — `DescribeTaskDefinition` is a broadly granted read permission, and env vars leak into logs and crash dumps.

Use the `secrets` block (§3.2) with **Secrets Manager** (automatic rotation, cross-region replication, KMS-encrypted, per-secret resource policies) or **SSM Parameter Store SecureString** (cheaper, good for config that's merely sensitive). The execution role needs `secretsmanager:GetSecretValue` / `ssm:GetParameters` **and** `kms:Decrypt` on the encrypting key.

For rotation, note that ECS injects secrets at container start — a rotated secret doesn't reach a running task. Either fetch at runtime via the SDK using the task role, or trigger a service redeployment from the Secrets Manager rotation Lambda via EventBridge.

### 5.4 Encryption

| Where | How |
|---|---|
| Images at rest | ECR: SSE-S3 by default, or KMS CMK |
| Ephemeral task storage (Fargate) | Encrypted by default with an AWS-managed key; customer-managed keys supported |
| EBS volumes attached to tasks | KMS key specified at attach time |
| EFS | KMS at rest, TLS in transit via `transitEncryption` in the volume config |
| Logs | CloudWatch Logs group encrypted with a KMS CMK |
| In transit, north-south | TLS terminated at ALB/NLB with an **ACM** certificate |
| In transit, east-west | Service Connect TLS using **AWS Private CA**, or application-level mTLS |

### 5.5 Supply chain security

Everything in §2 is a security control. The minimum production bar:

1. Repositories set to **immutable** tags (with narrow mutability exclusions).
2. **Enhanced scanning** (Inspector) on continuously, with findings in Security Hub and a hard build gate on critical CVEs.
3. **Managed image signing** on push, with verification before deploy.
4. All third-party base images pulled through **pull-through cache**, never directly from Docker Hub — so they inherit your scanning and are unaffected by upstream outages or tampering.
5. **Task definitions pin image digests**, not tags.
6. Minimal base images (distroless, Chainguard, scratch) — Inspector now scans these properly, so the old "we can't scan distroless" excuse is gone.
7. **KMS CMK** encryption on repositories holding sensitive images.

### 5.6 Runtime security

**Container hardening in the task definition** — the settings from §3.2 that matter most:

- `"readonlyRootFilesystem": true` — blocks the write-then-execute pattern most container malware relies on. Mount a small `tmpfs`/ephemeral volume for genuinely needed scratch paths.
- `"user": "1001:1001"` — never run as root.
- `"privileged": false` (the default; never set it true on shared clusters).
- `linuxParameters.capabilities.drop: ["ALL"]`, adding back only what's required.
- Resource limits on every container, so one compromised or looping container can't starve its neighbours.

**Amazon GuardDuty Runtime Monitoring** closes the gap that static scanning can't see: what happens *after* deployment. A lightweight, fully managed GuardDuty security agent runs as a sidecar (or on the EC2 host) and analyzes on-host behaviour — file access, process execution, network connections — to detect privilege escalation, use of exposed credentials, communication with known-malicious IPs and domains, cryptomining, reverse shells, and malware.

Practical requirements and limits:

- Fargate platform version **1.4.0 or later** (Linux); EC2 instances use the host-level agent.
- Fargate tasks **must have a task execution role**, since it's used to retrieve and manage the agent image from an ECR private repository.
- Tasks need a network path to that ECR repository — a **VPC endpoint for ECR** in private subnets, or a NAT gateway.
- Coverage is enabled per-cluster via a **predefined tag**; if your policies restrict actions by tag, grant explicit tagging permissions.
- The agent sidecar **does not count** toward the containers-per-task-definition quota, but the cluster tag **does** count toward the cluster tag quota.
- **ECS Exec cannot be used on the GuardDuty agent sidecar.**
- **Runtime Monitoring is not supported on ECS Managed Instances** — an important gap to plan around if you're adopting that compute option for GPU workloads.

Findings flow to **Security Hub** and **EventBridge** for automated response: isolate the task's security group, stop the task, snapshot for forensics, page on-call. **Amazon Detective** helps with the follow-up investigation.

**ECS Exec** is a security-relevant feature in both directions: it removes the need for SSH and bastion hosts, but it's also a direct path into production containers. Gate it with IAM (`ecs:ExecuteCommand` with condition keys on cluster/task tags), log every session to CloudWatch Logs or S3 with KMS encryption, and consider disabling it entirely in production services, enabling it only for the duration of an incident.

### 5.7 Compliance and governance

- **AWS Security Hub** — aggregates Inspector, GuardDuty, and Config findings against standards like CIS AWS Foundations and AWS FSBP. Control **[ECR.1]** ("ECR private repositories should have image scanning configured") is a good canary for registry hygiene.
- **AWS Config** — managed rules such as `ecs-task-definition-user-for-host-mode-check`, `ecs-containers-readonly-access`, `ecs-no-environment-secrets`, and `ecs-task-definition-nonroot-user`. Attach remediation actions.
- **AWS CloudTrail** — every ECS and ECR API call. Watch for `RegisterTaskDefinition` with unexpected images, `RunTask` in unusual regions, and `CreateCluster` bursts.
- **Service Control Policies (SCPs)** — deny `ecs:RegisterTaskDefinition` unless the image URI matches your ECR account, deny cluster creation outside approved regions.
- **AWS Audit Manager** — evidence collection for SOC 2, PCI DSS, HIPAA.
- **Amazon Inspector** image usage insights — prioritize CVE remediation by which images are actually running in which clusters.

### 5.8 A one-page security checklist

- [ ] Distinct, least-privilege **task role per service**; no app permissions in the execution role
- [ ] Tasks in **private subnets**, `awsvpc` mode, per-task security groups referencing other SGs
- [ ] **VPC endpoints** for ECR, Logs, Secrets Manager, SSM; S3 gateway endpoint
- [ ] Secrets via **Secrets Manager/SSM**, never in `environment` or the image
- [ ] **KMS CMKs** on ECR repos, log groups, EBS/EFS volumes
- [ ] ECR: **immutable tags**, **enhanced scanning**, **managed signing**, **pull-through cache** for all third-party images
- [ ] Task definitions **pin digests**
- [ ] `readonlyRootFilesystem: true`, non-root `user`, `capabilities.drop: ALL`, no `privileged`
- [ ] **GuardDuty Runtime Monitoring** enabled (note the Managed Instances gap)
- [ ] **ECS Exec** IAM-gated and session-logged, or disabled in prod
- [ ] IMDSv2 enforced with hop limit 1 on EC2 container instances
- [ ] **WAF** on the ALB/CloudFront; **Shield Advanced** if internet-facing and critical
- [ ] **Security Hub** + **Config rules** + **CloudTrail** with alerting on anomalous ECS API activity
- [ ] Deployment **circuit breaker** and **CloudWatch alarm rollback** configured (availability *is* security)

---

## 6. Reference: Service Pairing Matrix

| ECS concern | Primary AWS services |
|---|---|
| Image storage & distribution | **ECR** (private/public/PTC), S3, KMS |
| Image security | Amazon Inspector, AWS Signer, Security Hub, EventBridge |
| Build & deploy | CodeBuild, CodePipeline, CodeDeploy (legacy B/G), CloudFormation, CDK, Terraform |
| Compute | Fargate, ECS Managed Instances, EC2 + Auto Scaling, ECS Anywhere (SSM) |
| Ingress | ALB, NLB, API Gateway (+ VPC Link), CloudFront, Route 53, ACM |
| Service-to-service | Service Connect, Cloud Map, VPC Lattice |
| Scaling | Application Auto Scaling, CloudWatch alarms, EventBridge Scheduler |
| Event-driven / batch | EventBridge, Step Functions, AWS Batch, SQS, SNS, Lambda, **Kinesis Data Streams** |
| Logging | CloudWatch Logs, FireLens/Fluent Bit, **Kinesis Data Firehose**, OpenSearch, S3 |
| Metrics & tracing | CloudWatch Container Insights, X-Ray, ADOT, Managed Prometheus, Managed Grafana |
| Storage | EFS, EBS, FSx, S3 |
| Secrets & config | Secrets Manager, SSM Parameter Store, AppConfig, KMS |
| Identity | IAM, STS, Cognito (ALB/API Gateway auth) |
| Network security | VPC, Security Groups, PrivateLink, WAF, Shield, Network Firewall, Flow Logs |
| Runtime security | GuardDuty Runtime Monitoring, Detective, Systems Manager |
| Governance | Config, CloudTrail, Security Hub, Audit Manager, Organizations/SCPs |

---

## 7. Reference: Recent Feature Timeline (2025–2026)

| Date | Feature |
|---|---|
| Mar 2025 | ECR-to-ECR pull-through cache (cross-region/cross-account lazy sync) |
| Jul 2025 | **Built-in blue/green deployments** + six deployment lifecycle hooks + bake time; no CodeDeploy required; works with ALB, NLB, and Service Connect |
| Sep 2025 | **Amazon ECS Managed Instances** — managed EC2 capacity provider in your account |
| Nov 2025 | **ECS Express Mode** (re:Invent, session CNS379) — three inputs to a production HTTPS web service |
| Nov 2025 | ECR VPC endpoints support dual-stack IPv4/IPv6 |
| Dec 2025 | ECR automatic repository creation on push |
| Feb 2026 | Clair-based ECR basic scanning fully deprecated; all accounts on Amazon native scanning |
| Mar 2026 | ECR pull-through cache supports Chainguard as an upstream |
| Apr 2026 | ECR pull-through cache discovers and syncs **OCI referrers** (signatures, SBOMs, attestations) |
| Apr 2026 | ECS Managed Instances **NVIDIA GPU metrics** in Container Insights with enhanced observability |
| May 2026 | ECS + EBS volume integration reaches GovCloud regions |
| Jun 2026 | Fargate **32 vCPU** task sizes (60/120/244 GiB), x86 and ARM |
| Jun 2026 | **Faster service auto scaling** — 20-second high-resolution metrics; ~4.2× faster scale-out trigger |
| Jun 2026 | Express Mode expands to GovCloud (US-East, US-West) |
| Jul 2026 | Managed Instances GPU management fees cut (35% G-series, 60% P-series/Trainium) |
| Jul 2026 | **Real-time deployment observability** in the ECS console (live timeline, circuit breaker proximity, alarm state) |
| Jul 2026 | Express Mode supports **custom task definitions** (sidecars, FireLens, ulimits, custom health checks) |
| Jul 2026 | **Action Logs** — timestamped records of ECS-performed actions during deployments and Managed Daemon updates |
| Jul 2026 | Advanced deployment strategies (blue/green, linear, canary) in AWS European Sovereign Cloud |

---

## 8. Gotchas and Hard-Won Lessons

**Task definitions**

- Forgetting `startPeriod` on a health check turns a slow-starting app into a restart loop that looks like a crash bug.
- `memory` (hard limit) vs `memoryReservation` (soft limit) on EC2: setting only the hard limit wastes capacity; setting only the soft limit invites OOM kills of neighbours.
- Task definition revisions are never deleted by default and count toward quotas. Deregister aggressively in CI.
- `environmentFiles` from S3 requires the **execution** role to have `s3:GetObject` — a classic 5-minute debugging detour.

**Networking**

- `awsvpc` tasks consume ENIs, and ENI-per-instance limits are real on EC2. Enable ENI trunking on supported instance types, or you'll silently cap task density.
- Private subnets without VPC endpoints means every image pull crosses a NAT gateway. On a large fleet this is a meaningful and entirely avoidable line item.
- Service Connect and VPC Lattice both prevent changing the deployment controller after service creation. Decide early.

**Deployments and scaling**

- Service auto scaling scales *tasks*; capacity provider managed scaling scales *instances*. Configure both on EC2, or you'll scale into `PROVISIONING`.
- The deployment circuit breaker only catches tasks that fail to *start* or fail health checks. An app that starts fine and returns 500s needs a CloudWatch alarm attached to the deployment.
- Fargate Spot without proper `SIGTERM` handling will drop in-flight requests. You get a 2-minute warning via EventBridge — use it.
- ALB deregistration delay plus container `stopTimeout` plus your app's own drain time need to add up sensibly, or rolling deployments will produce 502s.

**Registry**

- Repository encryption (SSE-S3 vs KMS) is **immutable after creation**. Decide up front.
- Lifecycle rules evaluate in priority order and an image matched once isn't re-evaluated — always run the preview.
- Scanning configuration moved to the registry level; repository-level scanning API calls are deprecated and will quietly not do what you expect.

**Security**

- The execution role vs task role confusion is the single most common source of over-privileged ECS workloads. Audit both.
- GuardDuty Runtime Monitoring doesn't cover ECS Managed Instances. If you're moving GPU workloads there, plan compensating controls.
- `readonlyRootFilesystem: true` breaks apps that write to `/tmp`. Mount an ephemeral volume there rather than abandoning the setting.

---

## Further Reading

- [Amazon ECS Developer Guide](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/)
- [Amazon ECS Best Practices Guide](https://docs.aws.amazon.com/AmazonECS/latest/bestpracticesguide/)
- [Amazon ECR User Guide](https://docs.aws.amazon.com/AmazonECR/latest/userguide/)
- [ECS blue/green deployment implementation](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/blue-green-deployment-implementation.html)
- [Extending deployment pipelines with ECS blue/green deployments and lifecycle hooks](https://aws.amazon.com/blogs/containers/extending-deployment-pipelines-with-amazon-ecs-blue-green-deployments-and-lifecycle-hooks)
- [Deep dive: ECS Managed Instances provisioning and optimization](https://aws.amazon.com/blogs/containers/deep-dive-amazon-ecs-managed-instances-provisioning-and-optimization/)
- [ECS high-resolution metrics for faster auto scaling](https://aws.amazon.com/blogs/aws/amazon-ecs-introduces-new-high-resolution-metrics-for-faster-service-auto-scaling/)
- [Identify unauthorized behavior using GuardDuty Runtime Monitoring](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs-guard-duty-integration.html)
- [Streamline service-to-service communication with ECS Service Connect](https://aws.amazon.com/blogs/containers/streamline-service-to-service-communication-during-deployments-with-amazon-ecs-service-connect/)
