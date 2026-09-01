# Amazon EKS: A Feature Deep Dive

**Last updated: August 2026**

A practical, in-depth guide to Amazon Elastic Kubernetes Service covering the four areas that matter most in production: the **container registry**, **setting up containers**, **orchestrating containers**, and **security**. Each section calls out the EKS-specific features involved, the upstream Kubernetes primitives they build on, and the surrounding AWS services you'll typically wire in.

Links go to [Amazon EKS documentation](https://docs.aws.amazon.com/eks/latest/userguide/) and [official Kubernetes documentation](https://kubernetes.io/docs/home/) throughout, because on EKS you are almost always operating at both layers at once.

---

## Table of Contents

1. [Orientation: What EKS Actually Manages](#1-orientation-what-eks-actually-manages)
2. [The Registry: Amazon ECR + Kubernetes Image Handling](#2-the-registry-amazon-ecr--kubernetes-image-handling)
3. [Setting Up Containers: Pods, Workloads, Config, Storage](#3-setting-up-containers-pods-workloads-config-storage)
4. [Orchestrating Containers: Scheduling, Scaling, Networking, Upgrades](#4-orchestrating-containers-scheduling-scaling-networking-upgrades)
5. [Security](#5-security)
6. [Reference: Service Pairing Matrix](#6-reference-service-pairing-matrix)
7. [Reference: Recent Feature Timeline (2025–2026)](#7-reference-recent-feature-timeline-20252026)
8. [Gotchas and Hard-Won Lessons](#8-gotchas-and-hard-won-lessons)
9. [Documentation Index](#9-documentation-index)

---

## 1. Orientation: What EKS Actually Manages

EKS runs an upstream-conformant Kubernetes [control plane](https://kubernetes.io/docs/concepts/overview/components/) — API server, etcd, scheduler, controller manager — across multiple Availability Zones in an AWS-owned account. You get a Kubernetes API endpoint. Everything above that line is AWS's problem; everything below it is yours.

That division is the single most important thing to internalize, because it means "EKS features" fall into two categories: things AWS built to reduce what's below the line (Auto Mode, managed add-ons, Pod Identity, access entries), and things that are just Kubernetes and work exactly as documented upstream.

**Reference:** [What is Amazon EKS?](https://docs.aws.amazon.com/eks/latest/userguide/what-is-eks.html) · [EKS features](https://aws.amazon.com/eks/features/) · [Kubernetes concepts](https://kubernetes.io/docs/concepts/)

### 1.1 Compute options

| Option | Who manages nodes | Best for |
|---|---|---|
| **EKS Auto Mode** | AWS, end to end — provisioning, patching, node replacement, and the core add-ons | Default choice for most new clusters. Managed Karpenter, managed CNI/LB/storage controllers, Bottlerocket nodes. |
| **Managed node groups** | AWS automates lifecycle; you pick instance types and AMI versions | Teams wanting predictable, group-based capacity with SSM/SSH access to nodes. |
| **Self-managed nodes / Karpenter** | You (ASG, AMI, Karpenter controller, NodePools, upgrades) | Maximum control: custom AMIs, unusual kernel settings, bespoke scheduling. |
| **AWS Fargate** | AWS, per pod | Small isolated workloads. Note the constraints: no DaemonSets, no privileged containers, no GPUs, no host networking. |
| **EKS Hybrid Nodes** | You, on-premises or at the edge | Data sovereignty, latency, existing hardware. AWS runs the control plane; your machines join it. |
| **EKS on Outposts / Local Zones / Wavelength** | AWS-managed infrastructure in your facility or at the edge | Low latency and data residency. |
| **EKS Anywhere / EKS Distro** | You, entirely | Air-gapped or fully self-hosted environments. |

**EKS Auto Mode** deserves elaboration because it changes the operating model most. It runs [Karpenter](https://karpenter.sh/docs/) **off-cluster**, managed by AWS — there is no Karpenter deployment in your namespace, no Helm chart, no controller HA to configure. Nodes run Bottlerocket, are immutable, have no SSH or SSM access, and are recycled on a bounded lifetime (21 days by default) so AMI drift can't accumulate. Auto Mode also manages the CNI, load balancer controller, block storage driver, and DNS. It ships two built-in NodePools (`system` and `general-purpose`) that you cannot modify; add your own [NodePool](https://docs.aws.amazon.com/eks/latest/userguide/create-node-pool.html) and NodeClass resources for anything else.

The tradeoff is a management fee of roughly 12% on top of EC2 On-Demand pricing per managed instance, billed per second. Compute Savings Plans and RIs discount the EC2 portion but not the surcharge. AWS reduced Auto Mode GPU fees effective July 1, 2026 — 35% for G-series, 60% for P-series and AWS Trainium — which meaningfully changes the math for ML fleets.

**Reference:** [EKS Auto Mode](https://docs.aws.amazon.com/eks/latest/userguide/automode.html) · [Managed node groups](https://docs.aws.amazon.com/eks/latest/userguide/managed-node-groups.html) · [Hybrid Nodes overview](https://docs.aws.amazon.com/eks/latest/userguide/hybrid-nodes-overview.html) · [Kubernetes nodes](https://kubernetes.io/docs/concepts/architecture/nodes/)

### 1.2 Version lifecycle

EKS gives each Kubernetes minor version **14 months of standard support** (matching upstream), then **12 months of extended support** — 26 months total. Standard support bills at $0.10 per cluster-hour; extended support at $0.60. That 6× jump is a deliberate forcing function.

Set `supportType` on the cluster to control what happens at the boundary: `STANDARD` auto-upgrades you at end of standard support, `EXTENDED` keeps you put and starts charging. During extended support you still receive control plane security patches plus critical patches for VPC CNI, kube-proxy, CoreDNS, EKS-optimized AMIs, and Fargate.

As of mid-2026, **Kubernetes 1.36** (June 2, 2026) is the newest version in EKS, alongside 1.35, 1.34, and 1.33 in standard support. Two 1.36 changes matter for this guide: [user namespaces](https://kubernetes.io/docs/concepts/workloads/pods/user-namespaces/) reached GA (mapping container root to an unprivileged host user, so a container breakout grants no node-level privileges), and [Mutating Admission Policies](https://kubernetes.io/docs/reference/access-authn-authz/mutating-admission-policy/) landed for CEL-based mutation in the API server without running webhook infrastructure.

**Version rollback** (July 2026) is the newest safety net: you can revert to the previous minor version within 7 days of an upgrade. EKS first evaluates rollback readiness insights — API compatibility, version skew, add-on compatibility, cluster health — and for Auto Mode clusters it rolls back worker nodes before the control plane, honoring your configured disruption controls.

**Reference:** [Kubernetes version lifecycle](https://docs.aws.amazon.com/eks/latest/userguide/kubernetes-versions.html) · [Extended support release notes](https://docs.aws.amazon.com/eks/latest/userguide/kubernetes-versions-extended.html) · [Cluster upgrade policy](https://docs.aws.amazon.com/eks/latest/userguide/view-upgrade-policy.html) · [Cluster insights](https://docs.aws.amazon.com/eks/latest/userguide/cluster-insights.html)

### 1.3 Add-ons

EKS **managed add-ons** are AWS-curated, version-tracked installs of cluster software, upgradable through the EKS API rather than Helm. The core set: VPC CNI, CoreDNS, kube-proxy, EKS Pod Identity Agent, EBS CSI driver, EFS CSI driver, Mountpoint for Amazon S3 CSI driver, snapshot controller, CloudWatch Observability agent, GuardDuty agent, and a growing marketplace of third-party add-ons.

**EKS Capabilities** (November 2025) goes a step further: fully managed cluster capabilities where AWS runs the controller itself in an AWS-managed account. The launch set covers **Argo CD** (declarative continuous deployment), **AWS Controllers for Kubernetes (ACK)** (manage AWS resources as Kubernetes objects), and **kro** (Kubernetes Resource Orchestrator, for resource composition). Since June 2026 these can be configured as **CloudWatch Vended Logs** delivery sources, so you can ship controller logs to CloudWatch Logs, S3, or **Kinesis Data Firehose**.

**Reference:** [EKS add-ons](https://docs.aws.amazon.com/eks/latest/userguide/eks-add-ons.html) · [EKS Capabilities](https://docs.aws.amazon.com/eks/latest/userguide/eks-capabilities.html) · [ACK](https://aws-controllers-k8s.github.io/community/) · [Argo CD](https://argo-cd.readthedocs.io/)

---

## 2. The Registry: Amazon ECR + Kubernetes Image Handling

The registry story on EKS is mostly the ECR story, plus a Kubernetes-specific layer covering how the kubelet authenticates, how you pin images, and how you *enforce* provenance at admission time.

**Reference:** [Amazon ECR User Guide](https://docs.aws.amazon.com/AmazonECR/latest/userguide/what-is-ecr.html) · [Kubernetes: Images](https://kubernetes.io/docs/concepts/containers/images/)

### 2.1 How the kubelet gets credentials

On EKS with EC2-backed nodes, the kubelet uses a built-in ECR credential provider and authenticates with the **node IAM role**. That role typically carries `AmazonEC2ContainerRegistryReadOnly` (or the newer `AmazonEC2ContainerRegistryPullOnly`), which means every pod scheduled on that node can pull any image the node can pull. That's usually acceptable, but it's worth recognizing as a shared-privilege surface.

For non-ECR registries you use a standard [`imagePullSecrets`](https://kubernetes.io/docs/tasks/configure-pod-container/pull-image-private-registry/) reference on the pod or service account. For cross-account ECR, either grant access via an **ECR repository policy** or use **pull-through cache** (below) to mirror into the local account's registry.

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: checkout
  namespace: production
imagePullSecrets:
  - name: ghcr-creds
```

**Involved services:** IAM, STS, Secrets Manager, External Secrets Operator (community) for syncing registry credentials into Kubernetes Secrets.

### 2.2 Repository hygiene

Everything here applies identically to EKS and ECS, but the blast radius on a Kubernetes cluster is larger because a single compromised base image can propagate across dozens of Deployments.

- **Tag immutability.** Set repositories to `IMMUTABLE` so a tag can never be reassigned to a different digest. Use **immutability exclusion patterns** to keep `latest` and `dev-*` mutable while locking release tags.
- **Lifecycle policies.** Expire untagged layers aggressively; keep a bounded number of release images. Preview with `aws ecr start-lifecycle-policy-preview` before applying, because rules evaluate in priority order and an image matched once isn't re-evaluated.
- **Automatic repository creation on push** (December 2025) with namespace-scoped creation templates, so CI never fails on a missing repository and every new repo inherits your encryption, immutability, and lifecycle settings.
- **Archive storage class** for images you must retain for compliance but rarely pull.
- **Encryption at rest** with SSE-S3 by default or a **KMS** customer-managed key. This is immutable after repository creation — decide up front.

**Reference:** [Lifecycle policies](https://docs.aws.amazon.com/AmazonECR/latest/userguide/LifecyclePolicies.html) · [Image tag mutability](https://docs.aws.amazon.com/AmazonECR/latest/userguide/image-tag-mutability.html) · [ECR encryption at rest](https://docs.aws.amazon.com/AmazonECR/latest/userguide/encryption-at-rest.html)

### 2.3 Replication vs pull-through cache

**Replication** is eager and push-based: a registry-level configuration copies matching images to other regions or accounts. Good for multi-region active/active clusters that need in-region pulls, and for a central build account fanning out to `dev`/`staging`/`prod`.

**Pull-through cache (PTC)** is lazy: it mirrors an upstream registry into your private ECR, caching only what's actually pulled, and re-syncs with upstream at least once every 24 hours. Supported upstreams include **Docker Hub, GitHub Container Registry, Quay, ECR Public, Azure Container Registry, GitLab, the Kubernetes registry, Chainguard** (March 2026), and **other ECR private registries** (ECR-to-ECR, March 2025).

For Kubernetes specifically, PTC solves three recurring problems at once:

1. **Docker Hub rate limits.** A cluster autoscaling from 10 to 200 nodes will pull the same base images hundreds of times. PTC makes that a non-event.
2. **Upstream outages.** Your cluster keeps scheduling pods even when a third-party registry is down.
3. **Governance.** Cached third-party images inherit your lifecycle policies, KMS encryption, and Inspector enhanced scanning — so `nginx:1.27` in your cluster is a scanned, controlled artifact rather than an unmanaged external dependency.

As of April 2026, PTC also **discovers and syncs OCI referrers** — signatures, SBOMs, and attestations — from upstream. Before this, listing referrers on a PTC repository returned nothing, which broke signature verification for cached images. Now admission-time verification works end to end against cached third-party images.

**Reference:** [Pull-through cache](https://docs.aws.amazon.com/AmazonECR/latest/userguide/pull-through-cache.html) · [Private registry replication](https://docs.aws.amazon.com/AmazonECR/latest/userguide/replication.html)

### 2.4 Scanning

**Basic scanning** is free and covers OS package CVEs, scan-on-push or manual. The older Clair-based engine was **fully deprecated on February 2, 2026**; all accounts now use Amazon's native engine. Scanning configuration is managed at the **registry level** — the repository-level `PutImageScanningConfiguration` API is deprecated.

**Enhanced scanning** is powered by **Amazon Inspector**: continuous rather than point-in-time, covering OS packages *and* language dependencies (Python, Java, Node.js, Go, .NET, Ruby, PHP, Rust). Recent expansions cover **scratch, distroless, and Chainguard** base images plus Go toolchains, Oracle JDK, Amazon Corretto, Apache Tomcat, and WordPress.

The Kubernetes-relevant part is **image usage insights**: Inspector shows which EKS (and ECS) clusters are running each image, when it was last pulled, and how many clusters reference it. On a fleet with hundreds of images and thousands of findings, this is what lets you triage by actual blast radius instead of raw CVSS.

```bash
aws ecr put-registry-scanning-configuration \
  --scan-type ENHANCED \
  --rules '[{
    "scanFrequency": "CONTINUOUS_SCAN",
    "repositoryFilters": [{"filter": "*", "filterType": "WILDCARD"}]
  }]'
```

Findings flow to **Amazon Inspector** → **AWS Security Hub** → **Amazon EventBridge**, where a **Lambda** can fail a build, quarantine an image, or open a ticket.

**Reference:** [ECR enhanced scanning](https://docs.aws.amazon.com/AmazonECR/latest/userguide/image-scanning-enhanced.html) · [Amazon Inspector for ECR](https://docs.aws.amazon.com/inspector/latest/user/scanning-ecr.html)

### 2.5 Signing and admission-time enforcement

ECR supports **managed container image signing**: on push, ECR signs the image with the identity of the pushing principal, with no signing infrastructure to operate. Signatures are stored as OCI referrer artifacts and billed per signature. **AWS Signer** with Notation remains available if you need custom trust policies.

Signing only matters if something *verifies*. On EKS that's an [admission controller](https://kubernetes.io/docs/reference/access-authn-authz/admission-controllers/). Common patterns:

- **Kyverno** or **Sigstore policy-controller** verifying signatures and attestations before a pod is admitted.
- **OPA Gatekeeper** or native [ValidatingAdmissionPolicy](https://kubernetes.io/docs/reference/access-authn-authz/validating-admission-policy/) (CEL, no webhook) to enforce "images must come from `<account>.dkr.ecr.<region>.amazonaws.com`" and "no `:latest` tags."

A CEL-based registry allowlist with no webhook to operate:

```yaml
apiVersion: admissionregistration.k8s.io/v1
kind: ValidatingAdmissionPolicy
metadata:
  name: require-ecr-images
spec:
  matchConstraints:
    resourceRules:
      - apiGroups: [""]
        apiVersions: ["v1"]
        operations: ["CREATE", "UPDATE"]
        resources: ["pods"]
  validations:
    - expression: >
        object.spec.containers.all(c,
          c.image.startsWith('123456789012.dkr.ecr.us-east-1.amazonaws.com/'))
      message: "Images must come from the approved ECR registry."
```

### 2.6 Pinning images

Set `imagePullPolicy` deliberately. Kubernetes defaults to `IfNotPresent` for tagged images and `Always` for `:latest` — which is part of why `:latest` is a production anti-pattern. The stronger control is to **pin by digest** in your manifests:

```yaml
image: 123456789012.dkr.ecr.us-east-1.amazonaws.com/checkout@sha256:abc123...
```

Combined with immutable tags in ECR, this eliminates the "which build is actually running in prod?" class of incident entirely. Tools like Kustomize image transformers, Argo CD Image Updater, or Renovate can keep digests current in Git.

### 2.7 CI/CD

**CodePipeline** or GitHub Actions → **CodeBuild** (multi-arch via `docker buildx`, ARM builds natively on Graviton) → push to **ECR** → GitOps sync. On EKS, the last step is usually **Argo CD** or **Flux** reconciling a Git repository rather than an imperative `kubectl apply`, and with **EKS Capabilities** you can now let AWS run the Argo CD control plane for you.

**Involved services this section:** ECR, IAM, KMS, S3, Amazon Inspector, AWS Signer, Security Hub, EventBridge, CloudTrail, Lambda, PrivateLink/VPC endpoints, CodeBuild, CodePipeline, Secrets Manager.

---

## 3. Setting Up Containers: Pods, Workloads, Config, Storage

This is the layer where EKS is *just Kubernetes*. The EKS-specific value shows up in the AWS-integrated pieces: CSI drivers, secrets injection, log routing, and identity.

### 3.1 Workload objects

| Object | Use |
|---|---|
| [Deployment](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/) | Stateless services. Rolling updates, replica management. |
| [StatefulSet](https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/) | Stable network identity and per-pod persistent volumes. Databases, queues. |
| [DaemonSet](https://kubernetes.io/docs/concepts/workloads/controllers/daemonset/) | One pod per node. Log collectors, CNI, security agents. **Not supported on Fargate.** |
| [Job](https://kubernetes.io/docs/concepts/workloads/controllers/job/) / [CronJob](https://kubernetes.io/docs/concepts/workloads/controllers/cron-jobs/) | Batch and scheduled work. |
| [ReplicaSet](https://kubernetes.io/docs/concepts/workloads/controllers/replicaset/) | Managed by Deployments; you rarely write these directly. |

### 3.2 A production-shaped pod spec

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: checkout-api
  namespace: production
spec:
  replicas: 3
  selector:
    matchLabels: { app: checkout-api }
  template:
    metadata:
      labels: { app: checkout-api }
    spec:
      serviceAccountName: checkout-api        # bound to an IAM role via Pod Identity
      automountServiceAccountToken: false     # unless the app calls the K8s API
      securityContext:
        runAsNonRoot: true
        runAsUser: 1001
        fsGroup: 1001
        seccompProfile: { type: RuntimeDefault }
      initContainers:
        - name: migrate
          image: 123456789012.dkr.ecr.us-east-1.amazonaws.com/checkout@sha256:def456...
          command: ["/app/migrate"]
        - name: otel-collector                # native sidecar (restartPolicy: Always)
          image: public.ecr.aws/aws-observability/aws-otel-collector:latest
          restartPolicy: Always
      containers:
        - name: app
          image: 123456789012.dkr.ecr.us-east-1.amazonaws.com/checkout@sha256:abc123...
          imagePullPolicy: IfNotPresent
          ports:
            - name: http
              containerPort: 8080
          env:
            - name: LOG_LEVEL
              value: info
          envFrom:
            - configMapRef: { name: checkout-config }
          resources:
            requests: { cpu: 500m, memory: 512Mi }
            limits:   { memory: 1Gi }          # note: no CPU limit — see below
          startupProbe:
            httpGet: { path: /healthz, port: http }
            failureThreshold: 30
            periodSeconds: 5
          readinessProbe:
            httpGet: { path: /ready, port: http }
            periodSeconds: 5
          livenessProbe:
            httpGet: { path: /healthz, port: http }
            periodSeconds: 15
          lifecycle:
            preStop:
              exec: { command: ["sleep", "10"] }   # let endpoints propagate
          securityContext:
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: true
            capabilities: { drop: ["ALL"] }
          volumeMounts:
            - name: tmp
              mountPath: /tmp
            - name: secrets
              mountPath: /mnt/secrets
              readOnly: true
      volumes:
        - name: tmp
          emptyDir: {}
        - name: secrets
          csi:
            driver: secrets-store.csi.k8s.io
            readOnly: true
            volumeAttributes:
              secretProviderClass: checkout-aws-secrets
      terminationGracePeriodSeconds: 45
      topologySpreadConstraints:
        - maxSkew: 1
          topologyKey: topology.kubernetes.io/zone
          whenUnsatisfiable: ScheduleAnyway
          labelSelector:
            matchLabels: { app: checkout-api }
```

The decisions worth defending:

- **Requests and limits.** Requests drive scheduling and [QoS class](https://kubernetes.io/docs/concepts/workloads/pods/pod-qos/); limits drive throttling and OOM-kills. Set memory requests equal to limits for `Guaranteed` QoS on critical workloads. **Omitting CPU limits** is a deliberate and widely-adopted choice: CFS throttling under a CPU limit causes latency spikes even when the node has idle capacity. Always set CPU *requests*.
- **Three probes, not two.** [`startupProbe`](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/) protects slow-starting apps from the liveness probe; `readinessProbe` controls endpoint membership; `livenessProbe` restarts genuinely wedged containers. Conflating readiness and liveness is the most common cause of self-inflicted restart storms.
- **`preStop` sleep.** Endpoint removal and `SIGTERM` are concurrent, not ordered. A short sleep gives kube-proxy and the load balancer time to stop sending traffic before your process exits. This is the standard fix for 502s during rolling updates.
- **Native sidecars.** Since Kubernetes 1.29, an init container with `restartPolicy: Always` is a [sidecar](https://kubernetes.io/docs/concepts/workloads/pods/sidecar-containers/): it starts before app containers, runs for the pod's lifetime, and — critically for Jobs — doesn't prevent the pod from completing. This replaced a decade of hacks around log shippers and proxies blocking Job completion.
- **`automountServiceAccountToken: false`** unless the workload actually talks to the Kubernetes API. Free reduction in attack surface.

**Reference:** [Pods](https://kubernetes.io/docs/concepts/workloads/pods/) · [Managing resources for containers](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/) · [Init containers](https://kubernetes.io/docs/concepts/workloads/pods/init-containers/) · [Pod lifecycle](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/) · [EKS best practices: reliability](https://docs.aws.amazon.com/eks/latest/best-practices/application.html)

### 3.3 Configuration and secrets

[ConfigMaps](https://kubernetes.io/docs/concepts/configuration/configmap/) handle non-sensitive config. For secrets, you have three options on EKS, in ascending order of preference:

1. **Native Kubernetes [Secrets](https://kubernetes.io/docs/concepts/configuration/secret/)** — base64, not encrypted, stored in etcd. Acceptable *only* with [envelope encryption via KMS](https://docs.aws.amazon.com/eks/latest/userguide/envelope-encryption.html) enabled and tight RBAC. Anyone with `get secrets` in a namespace reads them in plaintext.
2. **Secrets Store CSI Driver + AWS Secrets and Configuration Provider (ASCP)** — mounts values from **AWS Secrets Manager** or **SSM Parameter Store** as files in the pod, with optional sync to a Kubernetes Secret. Supports rotation and reconciliation.
3. **Fetch at runtime via the AWS SDK** using the pod's IAM identity — no secret material at rest in the cluster at all, and rotation is automatic.

```yaml
apiVersion: secrets-store.csi.x-k8s.io/v1
kind: SecretProviderClass
metadata:
  name: checkout-aws-secrets
  namespace: production
spec:
  provider: aws
  parameters:
    objects: |
      - objectName: "prod/checkout/db"
        objectType: "secretsmanager"
        jmesPath:
          - path: "password"
            objectAlias: "db-password"
```

**Reference:** [Secrets Store CSI Driver](https://secrets-store-csi-driver.sigs.k8s.io/) · [AWS Secrets Manager and EKS](https://docs.aws.amazon.com/secretsmanager/latest/userguide/integrating_csi_driver.html) · [Kubernetes: encrypting secret data at rest](https://kubernetes.io/docs/tasks/administer-cluster/encrypt-data/)

### 3.4 Storage

EKS integrates AWS storage through [CSI drivers](https://kubernetes.io/docs/concepts/storage/volumes/#csi), all available as managed add-ons:

| Driver | Backing service | Access mode | Use case |
|---|---|---|---|
| **EBS CSI** | Amazon EBS | `ReadWriteOnce`, single AZ | Databases, per-pod block storage. The default for StatefulSets. |
| **EFS CSI** | Amazon EFS | `ReadWriteMany`, multi-AZ | Shared config, uploads, WordPress-style workloads. |
| **FSx for Lustre CSI** | Amazon FSx | `ReadWriteMany`, high throughput | HPC, ML training datasets. |
| **Mountpoint for Amazon S3 CSI** | Amazon S3 | Read-heavy, file-like | Large datasets and model weights read sequentially. |
| **FSx for NetApp ONTAP / OpenZFS CSI** | Amazon FSx | Varies | Enterprise NAS migration. |

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: gp3-encrypted
provisioner: ebs.csi.aws.com
volumeBindingMode: WaitForFirstConsumer   # avoids AZ mismatch
allowVolumeExpansion: true
parameters:
  type: gp3
  iops: "3000"
  throughput: "125"
  encrypted: "true"
  kmsKeyId: arn:aws:kms:us-east-1:123456789012:key/abcd-1234
reclaimPolicy: Delete
```

`volumeBindingMode: WaitForFirstConsumer` is not optional in practice — without it, the volume is provisioned in an arbitrary AZ and the pod may be unschedulable. The **snapshot controller** add-on plus [VolumeSnapshot](https://kubernetes.io/docs/concepts/storage/volume-snapshots/) resources give you EBS snapshots as first-class Kubernetes objects, which pairs well with **AWS Backup**.

EKS Auto Mode manages the EBS CSI driver for you and expects you to define StorageClasses; it does not create a default one, which surprises people migrating from standard EKS.

**Reference:** [Storage on EKS](https://docs.aws.amazon.com/eks/latest/userguide/storage.html) · [EBS CSI driver](https://docs.aws.amazon.com/eks/latest/userguide/ebs-csi.html) · [Kubernetes persistent volumes](https://kubernetes.io/docs/concepts/storage/persistent-volumes/) · [Storage classes](https://kubernetes.io/docs/concepts/storage/storage-classes/)

### 3.5 Logging

Kubernetes itself has [no log aggregation](https://kubernetes.io/docs/concepts/cluster-administration/logging/) — the kubelet writes container stdout/stderr to node disk and rotates it. You supply the shipper.

On EKS, the standard options are:

- **CloudWatch Observability EKS add-on** — one-click install of the CloudWatch agent and Fluent Bit, giving you Container Insights metrics plus logs. Since 2026 it also supports **OTel Container Insights** (preview April 2026, GA June 2026), publishing OpenTelemetry metrics enriched with up to 150 labels and queryable with **PromQL** in CloudWatch Query Studio. It auto-detects NVIDIA GPUs, EFA, Trainium, and Inferentia.
- **Fluent Bit DaemonSet** routing to **CloudWatch Logs**, **Kinesis Data Firehose** (→ S3, OpenSearch, Redshift, or a Lambda transform), or **Kinesis Data Streams** for real-time consumers with replay.
- **AWS Distro for OpenTelemetry (ADOT)** for traces and metrics → **X-Ray**, **Amazon Managed Service for Prometheus**, **Amazon Managed Grafana**.

Firehose is the right target when logs feed an analytics pipeline; Kinesis Data Streams when you need multiple independent real-time consumers (fraud detection, live dashboards) with replayable ordering.

**Reference:** [CloudWatch Observability add-on](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/install-CloudWatch-Observability-EKS-addon.html) · [Fluent Bit for EKS](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/Container-Insights-setup-logs-FluentBit.html) · [ADOT](https://aws-otel.github.io/docs/introduction)

**Involved services this section:** ECR, Secrets Manager, SSM Parameter Store, KMS, EBS, EFS, FSx, S3, CloudWatch Logs, Kinesis Data Firehose, Kinesis Data Streams, OpenSearch, X-Ray, Managed Prometheus, Managed Grafana, AWS Backup.

---

## 4. Orchestrating Containers: Scheduling, Scaling, Networking, Upgrades

### 4.1 Scheduling

The [kube-scheduler](https://kubernetes.io/docs/concepts/scheduling-eviction/kube-scheduler/) places pods; your job is to constrain it correctly.

- [**nodeSelector / node affinity**](https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/) — require or prefer nodes by label (instance type, architecture, capacity type).
- [**Taints and tolerations**](https://kubernetes.io/docs/concepts/scheduling-eviction/taint-and-toleration/) — reserve nodes (GPU pools, tenant pools) so only tolerating pods land there.
- [**Topology spread constraints**](https://kubernetes.io/docs/concepts/scheduling-eviction/topology-spread-constraints/) — the modern replacement for pod anti-affinity for AZ and node spreading. Cheaper to evaluate at scale.
- [**PodDisruptionBudgets**](https://kubernetes.io/docs/concepts/workloads/pods/disruptions/) — bound how many replicas can be down during *voluntary* disruptions. This is what makes node consolidation, upgrades, and Spot rebalancing safe. Karpenter and Auto Mode both honor PDBs.
- [**PriorityClasses**](https://kubernetes.io/docs/concepts/scheduling-eviction/pod-priority-preemption/) — decide who gets evicted when a node is under pressure.

New in August 2026: EKS supports **configuring control plane parameters** for the scheduler, controller manager, and API server. You can tune pod placement strategy, how quickly HPA responds to demand changes, event retention, and more. A concrete example from the launch: setting the scheduler's node resource fit strategy to `MostAllocated` packs pods onto already-well-utilized nodes, letting you run the same workloads on fewer nodes.

**Reference:** [EKS control plane configuration](https://docs.aws.amazon.com/eks/latest/userguide/control-plane-config.html) · [Kubernetes scheduling](https://kubernetes.io/docs/concepts/scheduling-eviction/)

### 4.2 Node autoscaling: Karpenter and Auto Mode

[Karpenter](https://karpenter.sh/) replaced Cluster Autoscaler as the default answer. Rather than scaling predefined ASGs, it reads pending pods' actual requirements and launches right-sized instances directly through EC2 APIs — typically 45–60 seconds to a ready node. It then continuously **consolidates**, replacing underutilized nodes with cheaper ones.

Two resources define behaviour:

```yaml
apiVersion: karpenter.sh/v1
kind: NodePool
metadata:
  name: general
spec:
  template:
    spec:
      nodeClassRef:
        group: eks.amazonaws.com
        kind: NodeClass
        name: default
      requirements:
        - key: kubernetes.io/arch
          operator: In
          values: ["arm64", "amd64"]
        - key: karpenter.sh/capacity-type
          operator: In
          values: ["spot", "on-demand"]
        - key: eks.amazonaws.com/instance-category
          operator: In
          values: ["c", "m", "r"]
      expireAfter: 336h
  disruption:
    consolidationPolicy: WhenEmptyOrUnderutilized
    consolidateAfter: 1m
    budgets:
      - nodes: "10%"
  limits:
    cpu: "2000"
```

Both Auto Mode and self-managed Karpenter share this NodePool API and support:

- **Dynamic and static provisioning.** Dynamic scales with workload demand; **static capacity NodePools** (set `replicas`) hold a fixed node count to eliminate cold starts for latency-sensitive inference. You can mix both in one cluster. Static pools are excluded from consolidation, and once `replicas` is set on a NodePool you can't remove it or switch that pool to dynamic. For predictable AZ distribution, create one static pool per AZ rather than spanning zones.
- **All four purchase options** — On-Demand, Spot, Capacity Blocks, and On-Demand Capacity Reservations — always provisioning reserved capacity first, then Spot or On-Demand.
- **EFA and EC2 placement groups** (July 2026), so distributed training and inference workloads get the network topology they need. You can configure interfaces as EFA-only or standard ENI on EFA-capable instances, in both dynamic and static pools.

The difference is ownership: with Auto Mode, AWS runs the controller off-cluster and you never touch a Helm chart, but you also lose custom AMIs and node-level access. With self-managed Karpenter, you own the controller, its IAM, its upgrades, and its failure modes — in exchange for full flexibility.

**Reference:** [EKS Auto Mode node pools](https://docs.aws.amazon.com/eks/latest/userguide/create-node-pool.html) · [Compute for AI/ML with Auto Mode and Karpenter](https://docs.aws.amazon.com/eks/latest/userguide/ml-node-pools.html) · [Karpenter concepts](https://karpenter.sh/docs/concepts/) · [Kubernetes cluster autoscaling](https://kubernetes.io/docs/concepts/cluster-administration/cluster-autoscaling/)

### 4.3 Workload autoscaling

- [**HorizontalPodAutoscaler**](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/) — scales replicas on CPU, memory, or custom/external metrics. With the CloudWatch or Prometheus adapter, you can scale on ALB request count, SQS depth, or any application metric.
- [**VerticalPodAutoscaler**](https://github.com/kubernetes/autoscaler/tree/master/vertical-pod-autoscaler) — right-sizes requests. Run in `recommendation` mode first; automatic mode restarts pods. Note that [in-place pod resize](https://kubernetes.io/docs/tasks/configure-pod-container/resize-container-resources/) is maturing upstream and will change this calculus.
- **KEDA** — event-driven autoscaling with first-class scalers for **SQS**, **Kinesis**, **DynamoDB Streams**, **MSK**, **CloudWatch**, and dozens more. The standard choice for queue-driven consumers, including scale-to-zero.
- **Cluster Proportional Autoscaler** — for CoreDNS and other cluster services that should scale with node count.

The layering rule: HPA/KEDA scales pods, Karpenter/Auto Mode scales nodes. Get both right or you'll scale replicas into `Pending`.

### 4.4 Networking

**Pod networking — the [Amazon VPC CNI](https://github.com/aws/amazon-vpc-cni-k8s)** gives every pod a real VPC IP address. That's the source of EKS's biggest operational surprise: you run out of IPs long before you run out of CPU. Symptoms are `FailedCreatePodSandBox` events and `InsufficientFreeAddressesInSubnet` from EC2.

The mitigations, in rough order of adoption:

- **Prefix delegation** — assign `/28` prefixes (16 addresses) to ENIs instead of individual secondary IPs. This raises pod density dramatically and cuts EC2 API calls: a `c5.4xlarge` supports 110 pods with prefix delegation versus 58 in secondary-IP mode.
- **Custom networking (ENIConfig)** — place pods in a secondary VPC CIDR (e.g. `100.64.0.0/10`) separate from node subnets, so pod IPs don't consume routable address space.
- **Enhanced subnet discovery** — let the CNI allocate from other subnets in the same VPC and balance across AZs.
- **IPv6 clusters** — the durable fix if you can adopt it.

EKS Auto Mode handles this automatically: it defaults to prefix delegation with a warm pool that scales with scheduled pods, falls back to `/32` secondary IPs when it detects subnet fragmentation, and calculates max pods assuming worst-case fragmentation. You configure it through a **NodeClass** rather than CNI environment variables — the old VPC CNI settings do not apply to Auto Mode.

```bash
kubectl set env daemonset aws-node -n kube-system ENABLE_PREFIX_DELEGATION=true
kubectl set env daemonset aws-node -n kube-system WARM_PREFIX_TARGET=1
```

If you use managed node groups with a launch template that specifies an AMI ID, you must also update kubelet's `maxPods`; managed node groups without a custom AMI calculate it automatically.

**Reference:** [Pod networking (VPC CNI)](https://docs.aws.amazon.com/eks/latest/userguide/pod-networking.html) · [Prefix delegation](https://docs.aws.amazon.com/eks/latest/userguide/cni-increase-ip-addresses.html) · [Auto Mode VPC networking and load balancing](https://docs.aws.amazon.com/eks/latest/userguide/auto-networking.html) · [EKS networking best practices](https://docs.aws.amazon.com/eks/latest/best-practices/networking.html) · [Kubernetes cluster networking](https://kubernetes.io/docs/concepts/cluster-administration/networking/)

**Ingress and load balancing** — the [AWS Load Balancer Controller](https://kubernetes-sigs.github.io/aws-load-balancer-controller/) turns Kubernetes objects into AWS load balancers:

| Kubernetes object | AWS resource |
|---|---|
| [`Ingress`](https://kubernetes.io/docs/concepts/services-networking/ingress/) | **Application Load Balancer** — path/host routing, WebSockets, gRPC, OIDC/**Cognito** auth, **AWS WAF** attachment |
| [`Service` type `LoadBalancer`](https://kubernetes.io/docs/concepts/services-networking/service/#loadbalancer) | **Network Load Balancer** — TCP/UDP/TLS, static IPs, PrivateLink |
| [`Gateway` / `HTTPRoute`](https://kubernetes.io/docs/concepts/services-networking/gateway/) | ALB/NLB via the controller, **or** **Amazon VPC Lattice** via the AWS Gateway API Controller |

Use `target-type: ip` so the load balancer targets pod IPs directly, skipping the extra kube-proxy hop and enabling proper pod-level health checks.

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: checkout
  annotations:
    alb.ingress.kubernetes.io/scheme: internet-facing
    alb.ingress.kubernetes.io/target-type: ip
    alb.ingress.kubernetes.io/listen-ports: '[{"HTTPS":443}]'
    alb.ingress.kubernetes.io/certificate-arn: arn:aws:acm:us-east-1:123456789012:certificate/...
    alb.ingress.kubernetes.io/ssl-policy: ELBSecurityPolicy-TLS13-1-2-2021-06
    alb.ingress.kubernetes.io/wafv2-acl-arn: arn:aws:wafv2:us-east-1:123456789012:regional/webacl/...
    alb.ingress.kubernetes.io/healthcheck-path: /healthz
    alb.ingress.kubernetes.io/group.name: production   # share one ALB across Ingresses
spec:
  ingressClassName: alb
  rules:
    - host: checkout.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: checkout-api
                port: { number: 80 }
```

**Gateway API** support landed for both the AWS Load Balancer Controller and VPC Lattice in March 2026, giving you one configuration model for internet-facing and internal service-to-service routing. This matters now because **AWS App Mesh reaches end of support on September 30, 2026** — AWS's migration guidance points EKS customers to **VPC Lattice**, which handles cross-VPC and cross-account service networking with IAM auth policies and no peering or Transit Gateway. Teams wanting a full mesh generally run **Istio**, **Linkerd**, or **Cilium** instead.

Beyond the cluster edge you'll typically layer **Route 53** → **CloudFront** (+ **WAF**, **Shield Advanced**) → ALB, or front a private ALB/NLB with **API Gateway** via a **VPC Link** when you need throttling, API keys, usage plans, or per-route authorizers.

**Service discovery** is [CoreDNS](https://kubernetes.io/docs/concepts/services-networking/dns-pod-service/) as a managed add-on. Scale it with the cluster, and consider [NodeLocal DNSCache](https://kubernetes.io/docs/tasks/administer-cluster/nodelocaldns/) on large clusters — DNS is a top source of tail latency and of the notorious `conntrack` race conditions.

**Reference:** [EKS load balancing](https://docs.aws.amazon.com/eks/latest/userguide/eks-networking-add-ons.html) · [AWS Gateway API Controller for VPC Lattice](https://www.gateway-api-controller.eks.aws.dev/) · [Kubernetes Services](https://kubernetes.io/docs/concepts/services-networking/service/)

### 4.5 Event-driven and batch orchestration

| Pattern | Services |
|---|---|
| Queue-driven consumers | **SQS** + **KEDA**, scaling to zero when idle |
| Stream processing | **Kinesis Data Streams** / **MSK** + KEDA, one pod per shard/partition |
| Scheduled work | Kubernetes [CronJob](https://kubernetes.io/docs/concepts/workloads/controllers/cron-jobs/), or **EventBridge Scheduler** triggering a Job via a controller |
| ML/HPC batch | **Kubeflow**, **Volcano**, **Kueue**, or **AWS Batch on EKS** |
| Managing AWS resources from Kubernetes | **ACK** — declare an S3 bucket or DynamoDB table as a Kubernetes resource |
| Workflow orchestration | **Argo Workflows**, **Step Functions** (via ACK or EventBridge) |

### 4.6 Upgrades and fleet operations

The upgrade sequence that works: **cluster insights** → control plane → managed add-ons → nodes → workloads.

- [**Cluster insights**](https://docs.aws.amazon.com/eks/latest/userguide/cluster-insights.html) automatically flags deprecated API usage, version skew, add-on incompatibility, and misconfigurations *before* you upgrade. Run these against every cluster on a schedule, not just at upgrade time.
- **Managed add-on updates** are versioned through the EKS API with conflict resolution options.
- **Node upgrades** honor PDBs and drain gracefully. Auto Mode does this continuously via bounded node lifetime, so there's no separate "node upgrade" event.
- **Version rollback** (July 2026) gives you 7 days to revert a minor version upgrade, with readiness insights evaluated first.

For fleet visibility, the **Amazon EKS Dashboard** provides cross-account, cross-region views of cluster health, control plane cost projections, which node groups run which AMI versions, support-type distribution, and Cluster Insights findings across the fleet. Pair it with **CloudWatch cross-account observability** for a genuine single pane of glass.

### 4.7 Observability

- **Control plane logging** — ship API server, audit, authenticator, controller manager, and scheduler logs to **CloudWatch Logs**. Off by default; turn audit logs on before you need them.
- **Container Insights** with enhanced observability — cluster/node/pod/container metrics. The **OTel Container Insights** variant (GA June 2026) collects OpenTelemetry metrics enriched with up to 150 labels including Kubernetes metadata and custom labels like team or business unit, with curated dashboards and PromQL queries in CloudWatch Query Studio.
- **Container Network Observability** (November 2025) — service map, flow table, and a performance metrics endpoint, powered by **CloudWatch Network Flow Monitor**. Surfaces top talkers, cross-AZ flows, retransmissions, and retransmission timeouts. This closes a real blind spot: cross-AZ traffic is both a latency and a cost problem, and it was previously very hard to attribute to a workload.
- **Amazon Managed Service for Prometheus** + **Amazon Managed Grafana** for the open-source path.
- **AWS X-Ray** / **ADOT** for tracing; **CloudWatch Application Signals** for SLOs.
- **Auto Mode capability logs** (February 2026) — compute autoscaling, block storage, load balancing, and pod networking controllers as CloudWatch Vended Logs sources, at reduced cost versus standard CloudWatch Logs.

**Reference:** [EKS observability](https://docs.aws.amazon.com/eks/latest/userguide/eks-observe.html) · [Container Insights for EKS](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/ContainerInsights.html) · [Kubernetes monitoring architecture](https://kubernetes.io/docs/concepts/cluster-administration/system-metrics/)

**Involved services this section:** ELB (ALB/NLB), API Gateway, VPC Lattice, Route 53, CloudFront, ACM, CloudWatch (Logs, Container Insights, Network Flow Monitor, Application Signals), EventBridge, Step Functions, AWS Batch, SQS, MSK, Kinesis, EC2 Auto Scaling, X-Ray, Managed Prometheus, Managed Grafana, Systems Manager.

---

## 5. Security

EKS security layers as: **cluster access → workload identity → network → supply chain → runtime → governance**. Each assumes the layer before it may fail.

The threat model is concrete. Wiz Research reported in 2025 that a meaningful share of analyzed EKS clusters had publicly accessible API endpoints paired with overly permissive RBAC. The [OWASP Kubernetes Top 10](https://owasp.org/www-project-kubernetes-top-ten/) puts insecure workload configuration, missing network segmentation, and secrets management failures at the top of the exploited list.

**Reference:** [EKS security best practices guide](https://docs.aws.amazon.com/eks/latest/best-practices/security.html) · [AWS EKS Best Practices (GitHub)](https://aws.github.io/aws-eks-best-practices/security/docs/) · [Kubernetes security concepts](https://kubernetes.io/docs/concepts/security/)

### 5.1 Cluster access: authentication and authorization

EKS authenticates IAM principals and then authorizes them with Kubernetes [RBAC](https://kubernetes.io/docs/reference/access-authn-authz/rbac/).

The mapping mechanism changed. The **`aws-auth` ConfigMap is deprecated**, replaced by the **Cluster Access Management (CAM) API** with **access entries**. New clusters should use CAM; existing clusters should migrate. The advantages are real rather than cosmetic:

- Permissions are managed from *outside* the cluster via AWS APIs and **IAM Identity Center**, not by editing a ConfigMap that has historically been a one-typo-from-lockout resource.
- The cluster creator no longer implicitly gets permanent `cluster-admin`. You can grant it explicitly for break-glass only.
- Access entries are validated before they're applied.
- Access policies (`AmazonEKSClusterAdminPolicy`, `AmazonEKSAdminPolicy`, `AmazonEKSEditPolicy`, `AmazonEKSViewPolicy`) can be scoped to specific namespaces.

```bash
aws eks create-access-entry \
  --cluster-name prod \
  --principal-arn arn:aws:iam::123456789012:role/PlatformEngineers \
  --type STANDARD

aws eks associate-access-policy \
  --cluster-name prod \
  --principal-arn arn:aws:iam::123456789012:role/PlatformEngineers \
  --policy-arn arn:aws:eks::aws:cluster-access-policy/AmazonEKSEditPolicy \
  --access-scope type=namespace,namespaces=production
```

**API endpoint exposure.** EKS creates a public API endpoint by default. Either set the endpoint to private-only (access via VPN, Direct Connect, or a bastion), or keep it public with `publicAccessCidrs` restricted to known office and CI ranges. Combine with audit logging so you can see authentication attempts.

**Reference:** [Cluster access management](https://docs.aws.amazon.com/eks/latest/best-practices/cluster-access-management.html) · [Access entries](https://docs.aws.amazon.com/eks/latest/userguide/access-entries.html) · [Cluster endpoint access](https://docs.aws.amazon.com/eks/latest/userguide/cluster-endpoint.html) · [Kubernetes RBAC](https://kubernetes.io/docs/reference/access-authn-authz/rbac/)

### 5.2 Workload identity: EKS Pod Identity vs IRSA

The wrong approach is attaching broad AWS permissions to the **node IAM role**, because every pod on that node inherits them. Both correct approaches bind an IAM role to a Kubernetes [ServiceAccount](https://kubernetes.io/docs/concepts/security/service-accounts/).

| | **EKS Pod Identity** (recommended) | **IRSA** |
|---|---|---|
| Setup | Install the Pod Identity Agent add-on; create associations via the EKS API | Create and maintain an OIDC provider per cluster |
| Trust policy | Simple, reusable across clusters | Per-cluster OIDC issuer in every trust policy |
| Role reuse | One role across many clusters | Trust policy edit per cluster |
| Visibility | `ListPodIdentityAssociations` gives central inventory | Scattered across annotations and trust policies |
| ABAC | Supports session tags | Limited |
| Cross-account | Same-account role directly; cross-account via SDK profile or role chaining | Direct via OIDC trust |
| Outside EKS | No | Works with EKS Anywhere, self-managed Kubernetes |

AWS's own guidance is unambiguous: use **EKS Pod Identity** unless you have a specific reason for IRSA.

```bash
aws eks create-addon --cluster-name prod --addon-name eks-pod-identity-agent

aws eks create-pod-identity-association \
  --cluster-name prod \
  --namespace production \
  --service-account checkout-api \
  --role-arn arn:aws:iam::123456789012:role/checkout-api-role
```

No pod annotation is required and no application code changes are needed — supported AWS SDK versions discover the credentials through the standard provider chain.

One important hardening note from the AWS best practices guide: the **`aws-node` DaemonSet** (VPC CNI) defaults to using the *node* IAM role, which carries `AmazonEKS_CNI_Policy` and ECR read permissions. That effectively lets any pod on the node attach/detach ENIs and pull images. Move `aws-node` to its own scoped identity.

Note the parallel to the `iam:PassRole` requirement: whoever configures a Pod Identity association must have `iam:PassRole` for that role, which is your control point for preventing privilege escalation through association creation.

**Reference:** [EKS Pod Identity](https://docs.aws.amazon.com/eks/latest/userguide/pod-identities.html) · [IAM roles for service accounts](https://docs.aws.amazon.com/eks/latest/userguide/iam-roles-for-service-accounts.html) · [Identity and access management best practices](https://aws.github.io/aws-eks-best-practices/security/docs/iam/)

**IMDS hardening.** Even with Pod Identity, a pod that can reach `169.254.169.254` can try to steal the node role. Enforce IMDSv2 (`HttpTokens: required`) and set `HttpPutResponseHopLimit: 1` so containers can't reach it through the extra network hop. Auto Mode's Bottlerocket nodes handle this for you.

### 5.3 Pod-level hardening

[**Pod Security Standards**](https://kubernetes.io/docs/concepts/security/pod-security-standards/) define three profiles — `privileged`, `baseline`, `restricted` — enforced by the built-in [Pod Security Admission](https://kubernetes.io/docs/concepts/security/pod-security-admission/) controller via namespace labels:

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: production
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/enforce-version: latest
    pod-security.kubernetes.io/warn: restricted
    pod-security.kubernetes.io/audit: restricted
```

`restricted` requires non-root, `allowPrivilegeEscalation: false`, dropped capabilities, and a seccomp profile. Roll it out in `warn`/`audit` mode first, fix what breaks, then flip to `enforce`.

For policies PSA can't express — registry allowlists, required labels, resource-limit mandates — use [**ValidatingAdmissionPolicy**](https://kubernetes.io/docs/reference/access-authn-authz/validating-admission-policy/) (CEL, no webhook to operate, no availability risk) or **Kyverno**/**OPA Gatekeeper** for richer policy including mutation and image verification. Kubernetes 1.36 adds **MutatingAdmissionPolicy** for CEL-based mutation without webhooks too.

The per-container [`securityContext`](https://kubernetes.io/docs/tasks/configure-pod-container/security-context/) settings that matter most are in the §3.2 example: `runAsNonRoot`, `readOnlyRootFilesystem`, `allowPrivilegeEscalation: false`, `capabilities.drop: ["ALL"]`, and `seccompProfile: RuntimeDefault`.

New and worth adopting: [**user namespaces**](https://kubernetes.io/docs/concepts/workloads/pods/user-namespaces/) went GA in Kubernetes 1.36 (EKS, June 2026). Setting `hostUsers: false` maps container root to an unprivileged host user, so a container breakout grants no node-level privileges. This mitigates whole classes of runtime CVEs.

### 5.4 Network security

- [**NetworkPolicies**](https://kubernetes.io/docs/concepts/services-networking/network-policies/) — the VPC CNI enforces them natively with eBPF (no Calico required, though Calico and Cilium remain popular for richer policy). Default-deny per namespace, then allow explicitly:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-ingress
  namespace: production
spec:
  podSelector: {}
  policyTypes: [Ingress]
```

- **Security groups for pods** — attach EC2 security groups directly to pods via `SecurityGroupPolicy`, which is how you let a specific workload (and only that workload) reach an RDS instance whose security group references it. Bridges Kubernetes-native and VPC-native controls.
- **Private subnets and VPC endpoints (PrivateLink)** — for private clusters, interface endpoints for `ecr.api`, `ecr.dkr`, `sts`, `ec2`, `logs`, `elasticloadbalancing`, `autoscaling`, `ssm`, `ssmmessages`, `ec2messages`, `eks`, plus an **S3 gateway endpoint**. Removes NAT gateway cost and internet exposure at once.
- **VPC Flow Logs** and **Container Network Observability** for traffic visibility.
- **AWS WAF** on the ALB or CloudFront; **Shield Advanced** for DDoS.
- **VPC Lattice auth policies** for IAM-based service-to-service authorization across VPCs and accounts.
- **AWS Network Firewall** for egress domain filtering.
- **Service mesh mTLS** — Istio, Linkerd, or Cilium for in-cluster encryption in transit and identity-based authorization.

**Reference:** [Security groups for pods](https://docs.aws.amazon.com/eks/latest/userguide/security-groups-for-pods.html) · [Network policies on EKS](https://docs.aws.amazon.com/eks/latest/userguide/cni-network-policy.html) · [Kubernetes network policies](https://kubernetes.io/docs/concepts/services-networking/network-policies/)

### 5.5 Secrets at rest

Kubernetes Secrets are base64-encoded, not encrypted. Enable **envelope encryption with AWS KMS** so etcd contents are encrypted with a customer-managed key, and combine with:

- Tight RBAC — `get`/`list` on secrets is equivalent to reading them in plaintext.
- **Secrets Store CSI Driver + ASCP** so the source of truth is **Secrets Manager** or **SSM Parameter Store**, not etcd.
- Rotation via Secrets Manager, with the CSI driver reconciling mounted values.
- CloudTrail on the KMS key so decryption is auditable.

**Reference:** [EKS envelope encryption](https://docs.aws.amazon.com/eks/latest/userguide/envelope-encryption.html) · [Kubernetes: encrypting confidential data at rest](https://kubernetes.io/docs/tasks/administer-cluster/encrypt-data/)

### 5.6 Supply chain security

Everything in §2 is a security control. The production bar:

1. ECR repositories with **immutable tags** (narrow mutability exclusions only).
2. **Enhanced scanning** (Inspector) on continuously; findings to Security Hub; hard CI gate on criticals.
3. **Managed image signing** on push, **verified at admission** by Kyverno or policy-controller.
4. All third-party images pulled via **pull-through cache** — never directly from Docker Hub.
5. Manifests **pin digests**, never `:latest`.
6. Minimal base images (distroless, Chainguard, scratch) — Inspector scans these properly now.
7. Admission policy restricting images to your ECR registry (see §2.5).
8. SBOM generation in CI, stored as an OCI referrer alongside the image.

### 5.7 Runtime security and threat detection

**Amazon GuardDuty EKS Protection** has two independent layers, and you want both:

- **EKS Audit Log Monitoring** — analyzes Kubernetes audit logs pulled directly from the EKS control plane. **No agent, no DaemonSet.** Detects anonymous API access, known-malicious IPs interacting with the cluster, reconnaissance patterns, and suspicious RBAC changes. This is the cheapest meaningful security win available on EKS.
- **EKS Runtime Monitoring** — deploys the `aws-guardduty-agent` add-on as a DaemonSet, giving on-host visibility into file access, process execution, and network connections. Findings pinpoint the specific container with pod ID, image ID, cluster tags, executable path, and process lineage. It detects attempts to escalate from a container to the EC2 host and onward into the AWS environment.

```bash
aws guardduty create-detector --enable --features '[
  {"Name": "EKS_AUDIT_LOGS", "Status": "ENABLED"},
  {"Name": "EKS_RUNTIME_MONITORING", "Status": "ENABLED",
   "AdditionalConfiguration": [{"Name": "EKS_ADDON_MANAGEMENT", "Status": "ENABLED"}]}
]'
```

**GuardDuty Extended Threat Detection** for EKS goes further, correlating signals across EKS audit logs, runtime process behaviour, malware execution, and AWS API activity into a single **critical-severity attack sequence finding**. The canonical example is exactly the attack chain you'd worry about: a threat actor exploits a container application, obtains privileged service account tokens, then uses those elevated privileges to read Kubernetes secrets or reach AWS resources. Individual findings would miss the pattern; the correlated sequence catches it, with a timeline, actors, and impacted resources.

Findings route to **Security Hub**, **EventBridge**, and **Amazon Detective** for automated response and investigation — isolate the pod with a NetworkPolicy, cordon the node, snapshot for forensics, page on-call.

Complement with open-source runtime tooling where you need custom rules: **Falco**, **Tetragon**, or **Tracee**.

**Reference:** [GuardDuty EKS Runtime Monitoring](https://docs.aws.amazon.com/guardduty/latest/ug/eks-runtime-monitoring-guardduty.html) · [GuardDuty EKS Protection](https://docs.aws.amazon.com/guardduty/latest/ug/kubernetes-protection.html) · [EKS Workshop: GuardDuty](https://www.eksworkshop.com/docs/security/guardduty/)

### 5.8 Audit logging and governance

- [**Kubernetes audit logs**](https://kubernetes.io/docs/tasks/debug/debug-cluster/audit/) — enable the `audit` control plane log type and ship to **CloudWatch Logs**. Without it you cannot answer "who deleted that Deployment" or "which identity tried to read that Secret." Turn it on before you need it.
- **AWS CloudTrail** — every EKS API call: cluster creation, access entry changes, add-on updates.
- **IAM condition keys** — as of April 2026, EKS supports seven additional condition keys on cluster creation and configuration APIs, designed for **Service Control Policies** in multi-account organizations. Use them to mandate private endpoints, required encryption, or approved versions at the policy layer rather than through post-deployment scanning.
- **AWS Config** — managed rules like `eks-endpoint-no-public-access`, `eks-secrets-encrypted`, `eks-cluster-supported-version`, `eks-cluster-log-enabled`.
- **AWS Security Hub** — aggregates Inspector, GuardDuty, and Config findings against CIS AWS Foundations, AWS FSBP, and the **CIS Amazon EKS Benchmark**.
- **AWS Audit Manager** for SOC 2, PCI DSS, and HIPAA evidence collection.

### 5.9 A one-page security checklist

- [ ] **Cluster Access Management API** and access entries; `aws-auth` ConfigMap migrated off
- [ ] Cluster creator's implicit `cluster-admin` removed; break-glass role documented
- [ ] API endpoint private, or public with `publicAccessCidrs` restricted
- [ ] **Control plane audit logging** enabled to CloudWatch Logs
- [ ] **EKS Pod Identity** for every workload that calls AWS; node role carries node permissions only
- [ ] `aws-node` DaemonSet moved off the node instance role
- [ ] **IMDSv2 required**, hop limit 1
- [ ] **Pod Security Admission** at `restricted` on application namespaces
- [ ] `readOnlyRootFilesystem`, `runAsNonRoot`, `capabilities.drop: ALL`, `seccompProfile: RuntimeDefault` on every container
- [ ] `hostUsers: false` (user namespaces) where supported
- [ ] **Default-deny NetworkPolicies** per namespace; security groups for pods where VPC-level control is needed
- [ ] **KMS envelope encryption** for Secrets; Secrets Store CSI Driver as the source of truth
- [ ] ECR: **immutable tags**, **enhanced scanning**, **managed signing**, **pull-through cache** for all third-party images
- [ ] Manifests **pin digests**; admission policy restricts registries
- [ ] **GuardDuty EKS Audit Log Monitoring + Runtime Monitoring + Extended Threat Detection** enabled
- [ ] Private subnets + **VPC endpoints**; **WAF** on the ALB; **Shield Advanced** if internet-facing and critical
- [ ] **Security Hub**, **Config rules**, **CloudTrail**, **IAM condition keys** / SCPs for org-wide guardrails
- [ ] **PodDisruptionBudgets** on every production workload (availability *is* security)
- [ ] Cluster on a **standard-support** Kubernetes version, upgrade cadence scheduled

---

## 6. Reference: Service Pairing Matrix

| EKS concern | Primary AWS services | Kubernetes primitives |
|---|---|---|
| Image storage & distribution | **ECR** (private/public/PTC), S3, KMS | `imagePullPolicy`, `imagePullSecrets` |
| Image security | Amazon Inspector, AWS Signer, Security Hub, EventBridge | Admission controllers, ValidatingAdmissionPolicy |
| Build & deploy | CodeBuild, CodePipeline, ECR, EKS Capabilities (Argo CD) | Deployments, Argo CD / Flux |
| Compute | EKS Auto Mode, EC2 + managed node groups, Fargate, Hybrid Nodes, Outposts | Nodes, NodePool/NodeClass |
| Node autoscaling | EC2 Auto Scaling, EC2 Fleet, Capacity Reservations | Karpenter NodePools, Cluster Autoscaler |
| Pod autoscaling | CloudWatch, SQS, Kinesis, MSK (via KEDA) | HPA, VPA, KEDA `ScaledObject` |
| Ingress | ALB, NLB, API Gateway (+ VPC Link), CloudFront, Route 53, ACM | `Ingress`, `Service`, `Gateway`/`HTTPRoute` |
| Service-to-service | VPC Lattice, Cloud Map, PrivateLink | `Service`, CoreDNS, service mesh |
| Pod networking | VPC (CNI), PrivateLink, Transit Gateway | CNI, `NetworkPolicy` |
| Event-driven / batch | EventBridge, Step Functions, AWS Batch, SQS, MSK, **Kinesis** | `Job`, `CronJob`, Argo Workflows, Kueue |
| Logging | CloudWatch Logs, **Kinesis Data Firehose**, **Kinesis Data Streams**, OpenSearch, S3 | Fluent Bit DaemonSet |
| Metrics & tracing | CloudWatch Container Insights (incl. OTel), Network Flow Monitor, X-Ray, ADOT, Managed Prometheus, Managed Grafana | metrics-server, ServiceMonitor |
| Storage | EBS, EFS, FSx, S3 (Mountpoint), AWS Backup | CSI drivers, `PersistentVolumeClaim`, `StorageClass`, `VolumeSnapshot` |
| Secrets & config | Secrets Manager, SSM Parameter Store, KMS, AppConfig | `Secret`, `ConfigMap`, Secrets Store CSI Driver |
| Workload identity | IAM, STS, EKS Pod Identity | `ServiceAccount` |
| Cluster access | IAM, IAM Identity Center, EKS access entries | RBAC `Role`/`ClusterRoleBinding` |
| Runtime security | GuardDuty (EKS Protection, Extended Threat Detection), Detective, Inspector | Pod Security Admission, `securityContext` |
| Governance | Config, CloudTrail, Security Hub, Audit Manager, Organizations/SCPs, IAM condition keys | Audit policy, admission policies |
| AWS resources from K8s | ACK, kro, Crossplane | CRDs |

---

## 7. Reference: Recent Feature Timeline (2025–2026)

| Date | Feature |
|---|---|
| Nov 19, 2025 | **Container Network Observability** — service map, flow table, performance metrics, via CloudWatch Network Flow Monitor |
| Nov 21, 2025 | `AmazonEKSMCPReadOnlyAccess` managed policy for the **EKS MCP Server** (read-only observability and troubleshooting tooling) |
| Nov 30, 2025 | **EKS Capabilities** — fully managed Argo CD, AWS Controllers for Kubernetes (ACK), and kro |
| Jan 15, 2026 | `ec2:LockSnapshot` added to `AmazonEBSCSIDriverPolicy` |
| Jan 27, 2026 | **Kubernetes 1.35** available in EKS |
| Feb 2, 2026 | Auto Mode can validate custom instance profiles in NodeClasses without an `eks` name prefix |
| Feb 2, 2026 | (ECR) Clair-based basic scanning fully deprecated; Amazon native engine everywhere |
| Feb 10, 2026 | **Auto Mode enhanced logging** — compute autoscaling, block storage, load balancing, and pod networking as CloudWatch Vended Logs sources |
| Mar 2026 | (ECR) Pull-through cache supports **Chainguard** |
| Mar 31, 2026 | **Gateway API support** for the AWS Load Balancer Controller and Amazon VPC Lattice |
| Apr 2, 2026 | **OTel Container Insights for EKS** (preview) — OTLP metrics, 150 labels, PromQL in Query Studio |
| Apr 17, 2026 | (ECR) Pull-through cache discovers and syncs **OCI referrers** (signatures, SBOMs, attestations) |
| Apr 20, 2026 | **Seven additional IAM condition keys** for cluster creation/configuration APIs, for SCP-based governance |
| Apr 21, 2026 | **EKS Hybrid Nodes gateway** — automates VPC-to-on-prem pod networking without making on-prem pod networks routable |
| Jun 2, 2026 | **Kubernetes 1.36** in EKS and EKS Distro — user namespaces GA, Mutating Admission Policies |
| Jun 4, 2026 | **EKS Capabilities** support CloudWatch Vended Logs delivery |
| Jun 23, 2026 | **OTel Container Insights for EKS** generally available |
| Jul 1, 2026 | **Kubernetes version rollback** — revert a minor version within 7 days, with rollback readiness insights |
| Jul 1, 2026 | **Auto Mode GPU management fees reduced** — 35% G-series, 60% P-series and Trainium |
| Jul 22, 2026 | **EFA and EC2 placement group support** for Auto Mode and Karpenter node pools |
| Aug 12, 2026 | **Control plane configuration parameters** — tune scheduler, controller manager, and API server |
| Sep 30, 2026 | **AWS App Mesh end of support** — migrate to VPC Lattice or a self-managed mesh |

---

## 8. Gotchas and Hard-Won Lessons

**Networking**

- **IP exhaustion is the #1 EKS operational surprise.** A node with idle CPU refuses to schedule pods, events show `FailedCreatePodSandBox`, and EC2 returns `InsufficientFreeAddressesInSubnet`. Plan CIDRs for pod density from day one; enable prefix delegation early.
- In prefix mode, `InsufficientCidrBlocks` in the ipamd logs means no contiguous `/28` is available — fix with subnet CIDR reservations or a dedicated pod subnet, not by adding nodes.
- If you use a launch template with a custom AMI ID, you must set kubelet's `maxPods` yourself. Managed node groups without a custom AMI calculate it automatically.
- Auto Mode ignores VPC CNI environment variables entirely. Configure networking through NodeClass.
- Cross-AZ pod-to-pod traffic is billable and invisible until you look. Container Network Observability is how you find it.

**Workloads**

- **CPU limits cause latency spikes** through CFS throttling even on idle nodes. Set CPU requests; think hard before setting CPU limits. Always set memory limits.
- Using the liveness probe as a readiness probe produces restart storms under load. Use all three probe types.
- No `preStop` hook means 502s during every rolling update, because endpoint removal and `SIGTERM` race.
- Pods without **PodDisruptionBudgets** will be disrupted by node consolidation, upgrades, and Spot rebalancing. Karpenter honors PDBs; it can't honor one you didn't write.
- `WaitForFirstConsumer` on StorageClasses, or EBS volumes land in the wrong AZ.
- On Fargate: no DaemonSets, no privileged containers, no GPUs, no host networking. Sidecar-based logging only.

**Cluster operations**

- **Extended support is 6× the cluster cost.** $0.10/hr → $0.60/hr. Set `supportType` deliberately and schedule upgrades inside the 14-month window.
- Run **cluster insights** continuously, not just before upgrades — it catches deprecated API usage while you still have time to fix it.
- Version rollback is a 7-day window, not an indefinite escape hatch.
- The Auto Mode management fee (~12% of On-Demand) is **not** discounted by Savings Plans or RIs. At 100+ nodes it's a real line item; AWS notes pricing may differ above 150 Auto Mode managed nodes.
- Auto Mode gives no SSH or SSM access to nodes. If your troubleshooting runbook depends on shelling into a node, rewrite it before adopting Auto Mode.

**Security**

- Node IAM role permissions are shared by every pod on the node. This is the EKS equivalent of the ECS execution-role-vs-task-role confusion, and it's just as common.
- `aws-auth` ConfigMap edits have locked people out of their own clusters for years. Migrate to access entries.
- Audit logs are **off by default**. Enable before an incident, not during one.
- `get secrets` in a namespace is equivalent to reading every secret in it, regardless of KMS envelope encryption.
- Pod Security Admission at `restricted` will break workloads that assume root. Roll out in `warn` and `audit` first.

---

## 9. Documentation Index

**Amazon EKS**

- [EKS User Guide](https://docs.aws.amazon.com/eks/latest/userguide/what-is-eks.html)
- [EKS Best Practices Guides](https://docs.aws.amazon.com/eks/latest/best-practices/introduction.html) · [GitHub version](https://aws.github.io/aws-eks-best-practices/)
- [EKS Auto Mode](https://docs.aws.amazon.com/eks/latest/userguide/automode.html)
- [EKS node pools (Karpenter)](https://docs.aws.amazon.com/eks/latest/userguide/create-node-pool.html)
- [Compute for AI/ML workloads](https://docs.aws.amazon.com/eks/latest/userguide/ml-node-pools.html)
- [Auto Mode VPC networking and load balancing](https://docs.aws.amazon.com/eks/latest/userguide/auto-networking.html)
- [Cluster access management best practices](https://docs.aws.amazon.com/eks/latest/best-practices/cluster-access-management.html)
- [EKS Pod Identity](https://docs.aws.amazon.com/eks/latest/userguide/pod-identities.html)
- [Kubernetes version lifecycle](https://docs.aws.amazon.com/eks/latest/userguide/kubernetes-versions.html) · [Cluster upgrade policy](https://docs.aws.amazon.com/eks/latest/userguide/view-upgrade-policy.html)
- [Hybrid Nodes overview](https://docs.aws.amazon.com/eks/latest/userguide/hybrid-nodes-overview.html) · [Hybrid Nodes configuration](https://docs.aws.amazon.com/eks/latest/userguide/hybrid-nodes-configure.html)
- [EKS document history (what changed, when)](https://docs.aws.amazon.com/eks/latest/userguide/doc-history.html)
- [Amazon EKS Workshop](https://www.eksworkshop.com/)

**Related AWS services**

- [Amazon ECR User Guide](https://docs.aws.amazon.com/AmazonECR/latest/userguide/what-is-ecr.html) · [Pull-through cache](https://docs.aws.amazon.com/AmazonECR/latest/userguide/pull-through-cache.html) · [Enhanced scanning](https://docs.aws.amazon.com/AmazonECR/latest/userguide/image-scanning-enhanced.html)
- [GuardDuty EKS Protection](https://docs.aws.amazon.com/guardduty/latest/ug/kubernetes-protection.html) · [EKS Runtime Monitoring](https://docs.aws.amazon.com/guardduty/latest/ug/eks-runtime-monitoring-guardduty.html)
- [AWS Load Balancer Controller](https://kubernetes-sigs.github.io/aws-load-balancer-controller/)
- [AWS Gateway API Controller for VPC Lattice](https://www.gateway-api-controller.eks.aws.dev/)
- [Karpenter](https://karpenter.sh/docs/)
- [AWS Controllers for Kubernetes (ACK)](https://aws-controllers-k8s.github.io/community/)
- [AWS Distro for OpenTelemetry](https://aws-otel.github.io/docs/introduction)
- [Container Insights](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/ContainerInsights.html)

**Kubernetes (upstream)**

- [Concepts overview](https://kubernetes.io/docs/concepts/) · [Cluster components](https://kubernetes.io/docs/concepts/overview/components/)
- [Pods](https://kubernetes.io/docs/concepts/workloads/pods/) · [Pod lifecycle](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/) · [Init containers](https://kubernetes.io/docs/concepts/workloads/pods/init-containers/) · [Sidecar containers](https://kubernetes.io/docs/concepts/workloads/pods/sidecar-containers/)
- [Deployments](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/) · [StatefulSets](https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/) · [DaemonSets](https://kubernetes.io/docs/concepts/workloads/controllers/daemonset/) · [Jobs](https://kubernetes.io/docs/concepts/workloads/controllers/job/)
- [Managing resources for containers](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/) · [Probes](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/)
- [ConfigMaps](https://kubernetes.io/docs/concepts/configuration/configmap/) · [Secrets](https://kubernetes.io/docs/concepts/configuration/secret/) · [Encrypting data at rest](https://kubernetes.io/docs/tasks/administer-cluster/encrypt-data/)
- [Persistent volumes](https://kubernetes.io/docs/concepts/storage/persistent-volumes/) · [Storage classes](https://kubernetes.io/docs/concepts/storage/storage-classes/) · [Volume snapshots](https://kubernetes.io/docs/concepts/storage/volume-snapshots/)
- [Assigning pods to nodes](https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/) · [Taints and tolerations](https://kubernetes.io/docs/concepts/scheduling-eviction/taint-and-toleration/) · [Topology spread constraints](https://kubernetes.io/docs/concepts/scheduling-eviction/topology-spread-constraints/) · [Disruptions](https://kubernetes.io/docs/concepts/workloads/pods/disruptions/)
- [Horizontal Pod Autoscaling](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/) · [Cluster autoscaling](https://kubernetes.io/docs/concepts/cluster-administration/cluster-autoscaling/)
- [Services](https://kubernetes.io/docs/concepts/services-networking/service/) · [Ingress](https://kubernetes.io/docs/concepts/services-networking/ingress/) · [Gateway API](https://kubernetes.io/docs/concepts/services-networking/gateway/) · [DNS for services and pods](https://kubernetes.io/docs/concepts/services-networking/dns-pod-service/) · [Network policies](https://kubernetes.io/docs/concepts/services-networking/network-policies/)
- [RBAC](https://kubernetes.io/docs/reference/access-authn-authz/rbac/) · [Service accounts](https://kubernetes.io/docs/concepts/security/service-accounts/) · [Admission controllers](https://kubernetes.io/docs/reference/access-authn-authz/admission-controllers/) · [ValidatingAdmissionPolicy](https://kubernetes.io/docs/reference/access-authn-authz/validating-admission-policy/)
- [Pod Security Standards](https://kubernetes.io/docs/concepts/security/pod-security-standards/) · [Pod Security Admission](https://kubernetes.io/docs/concepts/security/pod-security-admission/) · [Security contexts](https://kubernetes.io/docs/tasks/configure-pod-container/security-context/) · [User namespaces](https://kubernetes.io/docs/concepts/workloads/pods/user-namespaces/)
- [Auditing](https://kubernetes.io/docs/tasks/debug/debug-cluster/audit/) · [Logging architecture](https://kubernetes.io/docs/concepts/cluster-administration/logging/)
- [Images](https://kubernetes.io/docs/concepts/containers/images/) · [Pull from a private registry](https://kubernetes.io/docs/tasks/configure-pod-container/pull-image-private-registry/)
