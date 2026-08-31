# AWS Fargate — In-Depth Feature Guide

*Last updated: August 31, 2026*

---

## 1. Overview

### 1.1 What is AWS Fargate?

[AWS Fargate](https://aws.amazon.com/fargate/) is a **serverless, pay-as-you-go compute engine for containers**. It works with both major AWS container orchestrators — [Amazon Elastic Container Service (ECS)](https://aws.amazon.com/ecs/) and [Amazon Elastic Kubernetes Service (EKS)](https://aws.amazon.com/eks/) — and removes the need to provision, patch, or scale the EC2 instances that would otherwise host your containers.

Fargate isn't a replacement for ECS or EKS — it's a **compute layer** underneath them. You still define tasks (ECS) or pods (EKS) the same way; you simply choose `FARGATE` as the launch type / compute type instead of managing your own EC2 fleet. AWS handles the underlying host, capacity, OS patching, and isolation.

Fargate was announced at re:Invent in November 2017 for Amazon ECS, with Amazon EKS support following in 2019. As of 2026 it remains AWS's primary "serverless containers" offering, sitting alongside — and increasingly complemented by — the newer [Amazon ECS Managed Instances](https://aws.amazon.com/about-aws/whats-new/2025/09/amazon-ecs-managed-instances) option (see [Section 6](#6-fargate-vs-alternatives)).

### 1.2 Core Purpose

Fargate exists to eliminate the "undifferentiated heavy lifting" of container infrastructure:

- No EC2 instances to size, patch, or right-size
- No cluster capacity planning or Auto Scaling Group management
- No node-level OS or container-runtime maintenance
- Billing tied directly to the resources a task/pod actually consumes, per second

This lets engineering teams focus on the container image and application logic while AWS manages placement, scaling, isolation, and the host operating system.

### 1.3 Official AWS Documentation

| Resource | Link |
|---|---|
| Fargate product overview | https://aws.amazon.com/fargate/ |
| Fargate features page | https://aws.amazon.com/fargate/features/ |
| Fargate pricing | https://aws.amazon.com/fargate/pricing/ |
| Fargate getting started | https://aws.amazon.com/fargate/getting-started/ |
| Fargate FAQs | https://aws.amazon.com/fargate/faqs/ |
| ECS Developer Guide — "AWS Fargate for Amazon ECS" | https://docs.aws.amazon.com/AmazonECS/latest/developerguide/AWS_Fargate.html |
| EKS User Guide — "AWS Fargate" | https://docs.aws.amazon.com/eks/latest/userguide/fargate.html |
| Amazon Route 53 documentation | https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/Welcome.html |
| AWS Cloud Map documentation | https://docs.aws.amazon.com/cloud-map/latest/dg/what-is-cloud-map.html |
| ECS Service Discovery guide | https://docs.aws.amazon.com/AmazonECS/latest/developerguide/service-discovery.html |

### 1.4 Primary Use Cases

Straight from AWS's own framing of the service:

- **Web apps, APIs, and microservices** — build and deploy applications with the speed and immutability of containers, without owning the compute lifecycle underneath them.
- **Data processing and batch workloads** — run and scale containerized ETL, batch, and event-driven processing jobs, scaling out only for the duration of the job.
- **AI/ML training and development environments** — create flexible, portable environments to train, test, and deploy models, scaling compute up and down without over-provisioning.
- **Windows application modernization** — migrate legacy .NET / Windows Server applications into Windows containers on ECS/Fargate without rearchitecting them, while shedding Windows Server license and patching overhead.
- **Regulated and multi-tenant workloads** — take advantage of Fargate's hard isolation boundary (see [Section 4.4](#44-security-isolation-and-compliance)) for workloads that need strong tenant separation, such as SaaS platforms or compliance-sensitive systems.

---

## 2. How Fargate Works

1. You define a **task definition** (ECS) or **pod spec** (EKS) — the container image(s), CPU/memory, networking, IAM permissions, and storage requirements.
2. You choose the `FARGATE` launch type (ECS) or associate the namespace/pods with a **Fargate profile** (EKS).
3. AWS Fargate provisions right-sized, isolated compute behind the scenes, pulls your container image(s), and starts the task/pod.
4. Billing begins when the image starts downloading and ends when the task/pod terminates, metered per second.

Under the hood, each ECS task or EKS pod on Fargate runs inside its own dedicated **Firecracker microVM** — the same lightweight virtual-machine technology that underpins AWS Lambda. This gives every task kernel-level isolation rather than just container/namespace-level isolation, while still booting in roughly the same order of magnitude of time as a container. More detail in [Section 4.4](#44-security-isolation-and-compliance).

---

## 3. Feature Deep Dive

### 3.1 Serverless Compute and Resource Allocation

Fargate lets you deploy any [OCI-compliant](https://opencontainers.org/) container image without managing servers, clusters, or the runtime host. You declare CPU and memory independently at the task (ECS) or pod (EKS) level, and Fargate matches that request to isolated compute automatically.

**Supported vCPU / memory combinations (Amazon ECS, Linux):**

| vCPU | Memory range |
|---|---|
| 0.25 vCPU | 0.5 GB, 1 GB, 2 GB |
| 0.5 vCPU | 1–4 GB (1 GB increments) |
| 1 vCPU | 2–8 GB (1 GB increments) |
| 2 vCPU | 4–16 GB (1 GB increments) |
| 4 vCPU | 8–30 GB (1 GB increments) |
| 8 vCPU | 16–60 GB (4 GB increments) |
| 16 vCPU | 32–120 GB (8 GB increments) |
| **32 vCPU** *(new, June 2026)* | 60 GB, 120 GB, or 244 GB |

The **32 vCPU tier** was added to Amazon ECS on Fargate in [June 2026](https://aws.amazon.com/about-aws/whats-new/2026/06/amazon-ecs-fargate-32vcpu/), for both x86 and ARM (Graviton) Linux workloads, explicitly targeting high-performance computing, large-scale data processing, and AI inference use cases that previously outgrew Fargate's task size ceiling.

Other resource-related capabilities:

- **Ephemeral (task) storage** — 20 GB is included free with every task/pod; additional storage up to a configurable maximum can be requested and is billed separately. See [task storage documentation](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/fargate-task-storage.html).
- **tmpfs mounts** *(new, January 2026)* — Linux tasks on Fargate (and ECS Managed Instances) can now mount memory-backed `tmpfs` filesystems inside the container for scratch space, caches, or short-lived secrets that shouldn't persist to disk. See the [announcement](https://aws.amazon.com/about-aws/whats-new/2026/01/amazon-ecs-tmpfs-mounts-aws-fargate-managed-instances/).
- **Stateful workloads via Amazon EFS** — Fargate tasks/pods can mount [Amazon EFS](https://aws.amazon.com/efs/) file systems to externalize data outside the ephemeral task lifecycle, which is the standard pattern for stateful containers on Fargate since it does not support directly attached EBS volumes.

### 3.2 Networking, Load Balancing, and Service Discovery (Route 53)

Fargate tasks and pods use **`awsvpc` networking mode**: every task/pod gets its own Elastic Network Interface (ENI) directly inside your VPC, with its own private IP address, rather than sharing the network namespace of a host instance. This gives each task the same security-group-level control as an EC2 instance.

- **VPC integration** — tasks connect to your existing VPC design, and traffic can be inspected with [VPC Flow Logs](https://docs.aws.amazon.com/vpc/latest/userguide/flow-logs.html) and controlled with [VPC security groups](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-security-groups.html).
- **Load balancing** — ECS services on Fargate support Application Load Balancer and Network Load Balancer target-group integration for distributing traffic across tasks.
- **ECS Service Connect** — a built-in, client-side, DNS-based approach for service-to-service traffic within a cluster, giving you built-in traffic observability without deploying a separate service mesh. Docs: https://docs.aws.amazon.com/AmazonECS/latest/developerguide/service-connect.html
- **EKS Fargate networking constraint** — pods on Fargate are **not assigned public IP addresses** and must run in **private subnets with NAT gateway access**; there is no direct route to an internet gateway. See https://docs.aws.amazon.com/eks/latest/userguide/fargate-profile.html

#### Service Discovery via AWS Cloud Map and Amazon Route 53

For ECS specifically, **Service Discovery** lets a service register a predictable, queryable DNS name automatically, so other services can find it without a load balancer or a hardcoded IP:

- Service Discovery is implemented through **[AWS Cloud Map](https://docs.aws.amazon.com/cloud-map/latest/dg/what-is-cloud-map.html)**, which manages a **service registry** of instances, ports, and custom attributes (availability zone, cluster name, service name, and so on) for each ECS task.
- When you create a Cloud Map **private DNS namespace**, AWS automatically provisions a corresponding **[Amazon Route 53 private hosted zone](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/hosted-zones-private.html)**. As tasks scale up or down, or fail health checks, Route 53's records for that namespace are kept current, so dependent services always resolve to healthy endpoints.
- Because record management goes through Route 53, DNS lookups can be issued either as standard DNS queries or via the Cloud Map / `servicediscovery` API (`discover-instances`).
- **Quota note:** services configured for Service Discovery are limited to 1,000 tasks per service — a limit inherited from Route 53 itself.
- Fargate tasks require **platform version 1.1.0 or later** to use Service Discovery.
- The VPC hosting your Fargate tasks must have its [DNS attributes](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-dns.html) (`enableDnsHostnames`, `enableDnsSupport`) enabled for resolution to work.

Key documentation:
- ECS Service Discovery overview — https://docs.aws.amazon.com/AmazonECS/latest/developerguide/service-discovery.html
- Tutorial: creating an ECS service that uses Service Discovery — https://docs.aws.amazon.com/AmazonECS/latest/developerguide/create-service-discovery.html
- AWS Cloud Map documentation home — https://docs.aws.amazon.com/cloud-map/latest/dg/what-is-cloud-map.html
- Amazon Route 53 Developer Guide — https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/Welcome.html
- Route 53 private hosted zones — https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/hosted-zones-private.html

This Route 53/Cloud Map pairing is the standard mechanism for internal, DNS-based service-to-service discovery for microservices running on Fargate — distinct from Service Connect, which is a newer, more integrated alternative for the same general problem.

### 3.3 Auto Scaling

Fargate is designed to scale capacity in step with your application rather than pre-provisioned nodes:

- **AWS Application Auto Scaling** for ECS services — supports [target tracking](https://docs.aws.amazon.com/autoscaling/application/userguide/application-auto-scaling-target-tracking.html), [step scaling](https://docs.aws.amazon.com/autoscaling/application/userguide/application-auto-scaling-step-scaling-policies.html), and [scheduled scaling](https://docs.aws.amazon.com/autoscaling/application/userguide/application-auto-scaling-scheduled-scaling.html) policies.
- **Kubernetes-native autoscaling on EKS Fargate** — the [Horizontal Pod Autoscaler (HPA)](https://docs.aws.amazon.com/eks/latest/userguide/horizontal-pod-autoscaler.html) and [Vertical Pod Autoscaler (VPA)](https://docs.aws.amazon.com/eks/latest/userguide/vertical-pod-autoscaler.html) both work against Fargate pods.
- **AWS Compute Optimizer** analyzes historical utilization and recommends right-sized task/pod CPU and memory settings to cut waste — see https://aws.amazon.com/compute-optimizer/

Because there's no underlying node group, scaling a Fargate-backed service simply means launching or terminating tasks/pods — there's no "wait for a new EC2 instance to join the cluster" step in the critical path.

### 3.4 Security, Isolation, and Compliance

- **Hardware-level isolation via Firecracker** — each ECS task or EKS pod on Fargate runs on a dedicated, single-tenant Firecracker microVM. Firecracker is the open-source KVM-based virtual machine monitor AWS also uses for Lambda; it was purpose-built to give containers/functions the security boundary of a full VM with startup times measured in tens to low hundreds of milliseconds. This is what AWS means by "secure isolation by design" between tasks/pods, even on shared physical hardware.
- **IAM integration** — ECS tasks use a **task role** for the permissions your application code needs, separate from the **task execution role** used by the Fargate agent to pull images and write logs. On EKS, the equivalent is the **[Pod execution role](https://docs.aws.amazon.com/eks/latest/userguide/pod-execution-role.html)**, which lets the Fargate infrastructure register as a node and pull from Amazon ECR on the pod's behalf (application-level AWS permissions still require [IAM Roles for Service Accounts](https://docs.aws.amazon.com/eks/latest/userguide/iam-roles-for-service-accounts.html), since containers can't assume the pod execution role directly).
- **Secure interactive debugging** — [Amazon ECS Exec](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs-exec.html) provides a shell into a running container without SSH access to any underlying host; every Exec session is logged to AWS CloudTrail and can be streamed to CloudWatch for audit purposes.
- **Compliance coverage** — Fargate is in scope for numerous [AWS compliance programs](https://aws.amazon.com/compliance/services-in-scope/), including HIPAA, PCI DSS, and FedRAMP, and is available in [AWS GovCloud (US)](https://aws.amazon.com/govcloud-us/) regions for regulated government workloads.

### 3.5 Observability and Monitoring

- **[Amazon CloudWatch Container Insights](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/ContainerInsights.html)** — collects, aggregates, and summarizes metrics and logs for containerized applications, including Fargate tasks/pods, without additional agents to manage.
- **CloudWatch Logs** — the standard `awslogs` log driver ships container stdout/stderr straight to CloudWatch Logs (billed separately as standard CloudWatch usage).
- **Health monitoring / auto-recovery** — Amazon ECS now continuously monitors agent connectivity between tasks and the control plane and raises an `AGENT_CONNECTIVITY` health event; on Fargate this is handled automatically (draining and replacing affected tasks), announced in [AWS's August 2026 weekly roundup](https://aws.amazon.com/blogs/aws/aws-weekly-roundup-welcome-ducklabs-to-the-team-agentic-resource-discovery-ard-and-more-august-31-2026/).
- **Third-party tooling** — because logs/metrics are exposed through standard AWS services, common third-party observability platforms can also be wired in.

### 3.6 Compute Flexibility: CPU Architecture, OS, and Task Sizing

- **x86 and Arm/Graviton** — Fargate supports both x86_64 and Arm-based [AWS Graviton](https://aws.amazon.com/ec2/graviton/) processors for better price-performance on compatible workloads. Note: ARM CPU architecture is currently available for **Amazon ECS only**, not EKS Fargate.
- **Windows containers** — supported on Amazon ECS with Fargate (x86 only), letting teams run Windows Server-based containers without managing Windows Server EC2 instances or licenses directly.
- **Platform versions** — a Fargate "platform version" identifies the specific combination of kernel and container runtime a task runs on. AWS periodically patches and eventually retires older platform versions; tasks on a retired platform version are migrated or relaunched on a newer one. See https://docs.aws.amazon.com/AmazonECS/latest/developerguide/platform_versions.html and [task retirement and maintenance](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task-retirement.html).

### 3.7 EKS-Specific: Fargate Profiles

On EKS, which pods run on Fargate is controlled by a **Fargate profile**:

- A profile contains up to five **selectors**, each pairing a Kubernetes namespace with optional labels. Any pod matching a selector is scheduled onto Fargate.
- Every profile must reference a **Pod execution role** (`AmazonEKSFargatePodExecutionRolePolicy`), which is added to the cluster's Kubernetes RBAC so the Fargate kubelet can register as a node.
- Fargate profiles are **immutable** — changes require creating a new profile and retiring the old one.
- Pods on Fargate only run in **private subnets**, and Kubernetes affinity/anti-affinity rules don't apply (each pod effectively gets its own dedicated node).

Docs: https://docs.aws.amazon.com/eks/latest/userguide/fargate-profile.html and https://docs.aws.amazon.com/eks/latest/userguide/pod-execution-role.html

### 3.8 Pricing and Cost Optimization

Fargate bills for the **vCPU, memory, OS, CPU architecture, and storage** actually requested by a task/pod, from image pull until termination, rounded up to the nearest second (5-minute minimum for Windows). Full pricing detail: https://aws.amazon.com/fargate/pricing/

- **Fargate Spot** — runs interruption-tolerant ECS tasks on spare capacity at **up to a 70% discount** versus standard Fargate pricing (2-minute interruption warning). Currently Linux/x86/ARM only, ECS only.
- **Compute Savings Plans** — commit to a consistent dollar-per-hour compute spend over a 1- or 3-year term for **up to 50% savings** across Fargate usage. https://aws.amazon.com/savingsplans/compute-pricing/
- **Graviton (ARM)** — typically cheaper per vCPU-second than x86 for compatible workloads.
- **Cost allocation tags** — tagging tasks lets you break down spend per workload in [AWS Cost Explorer](https://aws.amazon.com/aws-cost-management/aws-cost-explorer/).
- **Additional charges** — CloudWatch Logs usage, data transfer, and public IPv4 addresses attached to tasks/pods are billed separately from compute.

**Illustrative example** (US East, N. Virginia pricing): 5 ECS tasks running 10 minutes/day for 30 days, each using 1 vCPU / 2 GB RAM / 30 GB ephemeral storage on Linux/x86, costs roughly **$1.26/month** in compute; the same workload on Graviton (Linux/ARM) comes out to roughly **$1.02/month**. These are AWS's own published worked examples and will vary by region and by current published rates.

---

## 4. Fargate vs. Alternatives

| | **AWS Fargate** | **Amazon ECS Managed Instances** | **Self-managed EC2 (ECS/EKS on EC2)** | **AWS Lambda** |
|---|---|---|---|---|
| Server management | None | None (AWS auto-selects/optimizes EC2 instances) | You manage instances/AMIs/patching | None |
| Instance type control | No (declare vCPU/memory only) | Yes — full EC2 instance-type flexibility | Yes — full control | N/A |
| GPU support | **No** | **Yes** | Yes | No (general purpose) |
| Privileged containers / eBPF agents | **No** | **Yes** | Yes | No |
| Max task size (2026) | 32 vCPU / 244 GB | Bound by chosen EC2 instance type | Bound by chosen EC2 instance type | Function-level, much smaller |
| Spot support | Fargate Spot (ECS) | EC2 Spot (added Dec 2025) | EC2 Spot | N/A |
| Best fit | Steady-state services, APIs, microservices, standard batch/ML jobs | GPU workloads, privileged workloads, memory > 244 GB, deep EC2 customization with less ops burden than raw EC2 | Maximum control, specialized hardware, cost optimization at large scale | Short-lived, event-driven, bursty functions |

[Amazon ECS Managed Instances](https://aws.amazon.com/about-aws/whats-new/2025/09/amazon-ecs-managed-instances) launched in September 2025 as a *complementary* option to Fargate rather than a replacement — it targets exactly the workloads Fargate structurally can't run (GPUs, privileged/eBPF workloads, >244 GB memory) while still removing most infrastructure management, using [Bottlerocket](https://aws.amazon.com/bottlerocket/) as its container-optimized OS. As of this writing, AWS states most new containerized workloads on ECS still default to Fargate, with Managed Instances reserved for workloads Fargate cannot serve.

For a pure function-as-a-service model (small, event-driven, sub-15-minute executions), AWS Lambda remains the better fit than either container option.

---

## 5. Notable 2026 Updates

- **32 vCPU / up to 244 GB task sizes** for ECS on Fargate (Linux, x86 & ARM) — June 2026. [Announcement](https://aws.amazon.com/about-aws/whats-new/2026/06/amazon-ecs-fargate-32vcpu/)
- **`tmpfs` mounts** for Linux tasks on Fargate — January 2026. [Announcement](https://aws.amazon.com/about-aws/whats-new/2026/01/amazon-ecs-tmpfs-mounts-aws-fargate-managed-instances/)
- **Automatic `AGENT_CONNECTIVITY` detection and recovery** across Fargate, Managed Instances, and EC2 — draining and replacing tasks automatically on Fargate — surfaced in AWS's August 2026 weekly roundup. [Post](https://aws.amazon.com/blogs/aws/aws-weekly-roundup-welcome-ducklabs-to-the-team-agentic-resource-discovery-ard-and-more-august-31-2026/)
- **Amazon ECS Managed Instances** general availability (Sept 2025) and subsequent **EC2 Spot support** (Dec 2025), expanding the broader ECS compute portfolio around Fargate. [GA announcement](https://aws.amazon.com/blogs/aws/announcing-amazon-ecs-managed-instances-for-containerized-applications/) · [Spot announcement](https://aws.amazon.com/about-aws/whats-new/2025/12/amazon-ecs-managed-instances-ec2-spot-instances)

Because platform versions, quotas, and regional availability change over time, always cross-check current limits against the live [ECS](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/AWS_Fargate.html) and [EKS](https://docs.aws.amazon.com/eks/latest/userguide/fargate.html) documentation before designing around them.

---

## 6. Current Limitations

- **No GPU support** — GPU-bound inference/training workloads need EC2, ECS Managed Instances, or another compute option.
- **No privileged containers or kernel-level eBPF agents** — some security/observability agents that need privileged mode won't run on Fargate.
- **Memory ceiling** — 244 GB per task/pod even at the largest (32 vCPU) size tier.
- **ARM and Windows availability** — Graviton (ARM) and Windows containers are currently ECS-only, not available on EKS Fargate.
- **EKS Fargate networking** — pods can't have public IPs and require private-subnet/NAT egress, which adds a networking prerequisite for internet-facing workloads.
- **No direct EBS attachment** — stateful data must go through Amazon EFS or an external store rather than an attached block volume.

---

## 7. Getting Started

- [Fargate Getting Started guide](https://aws.amazon.com/fargate/getting-started/)
- [ECS "AWS Fargate" developer guide (architecture, platform versions, task retirement)](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/AWS_Fargate.html)
- [EKS "Fargate profile" guide](https://docs.aws.amazon.com/eks/latest/userguide/fargate-profile.html)
- [AWS Pricing Calculator for Fargate](https://calculator.aws/#/createCalculator/Fargate)
- [AWS Containers landing page](https://aws.amazon.com/containers/)
