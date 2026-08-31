# AWS CodeSuite Overview
## The short version

These are two of the four pieces in AWS's "CodeSuite" — CodeCommit (source), CodeBuild (build/test), CodeDeploy (deploy), and CodePipeline (orchestration). CodeCommit and CodeBuild are the first two stages of a typical pipeline: one holds your Git repo, the other runs your compile/test/package step.

## Status note first, because it matters

CodeCommit's fate has whipsawed. AWS closed it to new customers in July 2024 and told people to migrate to GitHub/GitLab. Then in November 2025 AWS reversed course and returned CodeCommit to full General Availability, citing customer feedback that it was critical infrastructure rather than just another repo. Git LFS support was slated for early 2026, and it's available in 29 regions with more planned. So if you hit a blog post or even AWS doc pages saying it's closed, that's stale — but expect the ecosystem tooling and community mindshare to still lag behind, since a lot of teams already migrated away.

Worth knowing alongside that: Amazon CodeCatalyst moved to maintenance mode in the same announcement cycle, so it isn't the modern replacement path either.

---
## CodeCommit

A managed private Git host. Standard Git protocol, so your existing tooling works unchanged.

What makes it distinct from GitHub/GitLab is that it's an AWS-native resource rather than a third-party SaaS you connect to:

- **Auth is IAM**, not a separate user directory. Access control via IAM policies, roles, and resource-level permissions; HTTPS credentials or SSH keys derived from IAM users.
- **Network isolation** via VPC endpoints (PrivateLink) — traffic never leaves the AWS network.
- **Audit and encryption** through CloudTrail and KMS by default.
- **Pipeline triggers** are first-class: repo events publish to EventBridge, which starts CodePipeline executions, or fire SNS/Lambda triggers directly.

Feature-wise it's thin compared to GitHub — pull requests with approval rules exist, but there's no Actions equivalent, no package registry, no meaningful marketplace. It's a vault, not a collaboration platform. That's the tradeoff people accept in regulated environments.

---
## CodeBuild

Serverless build compute. You give it source plus a `buildspec.yml`, it spins up a container, runs your commands, and drops artifacts in S3 (or pushes an image to ECR). You pay per build-minute; nothing runs idle.

The buildspec is the core abstraction — phases (`install`, `pre_build`, `build`, `post_build`), plus artifact declarations, dependency caching, environment variables, and secrets pulled from Secrets Manager or Parameter Store.

Capabilities worth knowing about:

- **Environments**: AWS-managed images for common language stacks, or any custom Docker image from ECR. Linux x86 and ARM/Graviton, plus Windows and macOS fleets.
- **Compute options**: on-demand containers, Lambda-based compute for fast lightweight jobs, and reserved-capacity fleets when you want warm machines and predictable start times.
- **VPC support** so builds can reach private RDS instances, internal package mirrors, etc.
- **Test reports** — parse JUnit/Cucumber output into a native reports UI.
- **Batch builds** for fan-out matrix jobs.
- **GitHub Actions runners** — CodeBuild can act as self-hosted runners for Actions workflows, which is a common hybrid for teams on GitHub who want AWS-side compute and IAM.

CodeBuild also has its own webhook support, so it can run CI directly against a repo without CodePipeline at all. Plenty of teams use it standalone.

## How they compose into a pipeline

The canonical shape:

```
Git push → CodePipeline (source stage) → CodeBuild (build + test)
         → artifact to S3/ECR → CodeDeploy / ECS / Lambda / CloudFormation
```

CodePipeline is the orchestrator — stages containing actions, passing artifacts between them via an S3 bucket, with manual approval gates where you want them. Pipeline V2 added git tag and branch filters, pipeline-level variables, and stage-level conditions with automatic rollback.

If your source is GitHub, GitLab, or Bitbucket instead of CodeCommit, you wire it up through **CodeConnections** (formerly CodeStar Connections), which handles the OAuth/App installation and gives CodePipeline and CodeBuild a consistent source interface.

## Practical read

CodeBuild is genuinely good and worth using regardless of where your code lives — it's cheap, scales to zero, and the IAM integration means builds get AWS permissions without you managing long-lived keys.

CodeCommit is a narrower call. Choose it when IAM-only access, VPC isolation, and data residency inside your own AWS account are hard requirements — regulated industries, air-gapped-ish environments, government workloads. Otherwise, GitHub or GitLab as the source plus CodeBuild/CodePipeline for execution is the more common and better-supported setup, and the 2024 reversal-of-a-reversal is a fair reason to weigh platform-risk appetite before standardizing on it.

---
## CodeDeploy

The deployment engine. It takes a versioned artifact and gets it onto running infrastructure safely, with traffic shifting and automatic rollback.

**Compute platforms it targets:**
- **EC2 / on-premises** — requires the CodeDeploy agent on each host. This is its historical home and where it's still most differentiated.
- **Lambda** — shifts traffic between function aliases/versions. No agent.
- **ECS** — blue/green by swapping target groups behind an ALB. No agent.

**Core concepts:** an *application* is the logical unit; a *deployment group* is the target set (dev/staging/prod fleets, an ASG, an ECS service); a *deployment configuration* defines the rollout pattern; and an `appspec.yml` file declares what to copy where plus lifecycle hooks.

**Lifecycle hooks** are the real value for EC2 deployments — `BeforeInstall`, `AfterInstall`, `ApplicationStop`, `ApplicationStart`, `ValidateService`, and for blue/green, `BeforeAllowTraffic` / `AfterAllowTraffic`. You run arbitrary scripts at each point, so smoke tests and drain logic live in the deployment itself.

**Rollout strategies:** in-place (rolling, with configurable batch size — one at a time, half at a time, all at once), blue/green (stand up a fresh fleet, cut traffic over, keep the old one warm for rollback), and for Lambda/ECS, canary and linear traffic shifting. CloudWatch alarms can be wired to halt a deployment in progress and trigger automatic rollback. There's also an availability-zone-at-a-time mode for blast-radius control on large fleets.

**One important shift:** ECS added native canary and linear deployment strategies in October 2025, and AWS has updated its own guidance to recommend ECS-native deployments as the default for new container workloads rather than routing them through CodeDeploy. So CodeDeploy's center of gravity is increasingly EC2 and on-prem fleets — the places where nothing else orchestrates the rollout for you. If you're on ECS, EKS, or Lambda, the platform's own deployment primitives are often the better answer now.

It's also free — you pay nothing for EC2/Lambda/ECS deployments, only a small per-instance-update charge for on-premises hosts.

---
## CodePipeline

The orchestrator — the state machine that sequences everything else. It doesn't build or deploy anything itself; it invokes other services and passes artifacts between them.

**Model:** a pipeline is an ordered list of **stages**; each stage contains **actions**, which run in parallel or in declared `runOrder` sequence. Actions fall into categories: Source, Build, Test, Deploy, Approval, and Invoke. Artifacts move between stages through an S3 bucket you own.

**What plugs in:** source from CodeCommit, GitHub, ECR, or S3; builds and tests via CodeBuild; deployment through CodeDeploy, Elastic Beanstalk, ECS, or Fargate; plus CloudFormation actions to provision or update infrastructure as a pipeline step. Third-party sources connect through **CodeConnections**. Custom logic goes in via Lambda invoke actions or Step Functions actions.

**Pipeline type V2** is what you want for anything new — it added:
- Git trigger filters (branches, tags, file paths, PR events) instead of "any push to the tracked branch"
- Pipeline-level variables and parameterized executions
- **Stage conditions** — entry/on-success/on-failure rules with automatic rollback or retry of a failed stage only
- Queued/parallel execution modes rather than superseding

Note V2 bills per action-run-minute rather than the flat $1/pipeline/month of V1, so busy pipelines cost more.

**Where it's weak:** the model is coarse. Fan-out/fan-in beyond simple parallel actions is awkward, there's no expressive DSL, and complex conditional logic tends to get pushed down into CodeBuild scripts or Step Functions. Teams often end up with CodePipeline as a thin wrapper around a big buildspec, at which point the orchestration layer isn't earning much.

## Competitive landscape

The biggest structural difference: AWS splits CI/CD into four services, while most competitors collapse them into one product with one config file. That's the main tradeoff to weigh — composability and IAM granularity versus a single YAML and a single UI.

**Full-stack platforms** (cover all four layers at once):

| Platform | Source | Build/CI | Deploy | Orchestration |
|---|---|---|---|---|
| **GitHub** | GitHub Repos | Actions | Actions + Environments, or Deployments API | Actions workflows |
| **GitLab** | GitLab Repos | GitLab CI | GitLab CD, Auto DevOps, Agent for K8s | `.gitlab-ci.yml` pipelines |
| **Azure DevOps** | Azure Repos | Azure Pipelines (build) | Azure Pipelines (release) / Deployment Center | Azure Pipelines YAML |
| **Google Cloud** | Cloud Source Repos *(deprecated for new customers)* | Cloud Build | Cloud Deploy | Cloud Build + Cloud Deploy |
| **Bitbucket (Atlassian)** | Bitbucket | Pipelines | Pipelines + Deployments | `bitbucket-pipelines.yml` |
| **Harness** | — (BYO) | Harness CI | Harness CD (strong verification/rollback) | Harness Pipelines |

**Per-layer alternatives:**

- **Source control** — GitHub, GitLab, Bitbucket, Gitea/Forgejo (self-hosted, lightweight), Azure Repos, Perforce Helix (game dev, large binaries). Google shuttered Cloud Source Repositories to new customers, so GCP effectively has no first-party Git host — the same move AWS made and then reversed.

- **Build/CI** — Jenkins (still the incumbent in large enterprises; endlessly flexible, operationally heavy), GitHub Actions (the current default for most new projects), GitLab CI, CircleCI, Buildkite (hybrid — their control plane, your build agents, popular at scale), TeamCity, Drone/Woodpecker, Dagger (portable pipelines-as-code in containers), Depot and Blacksmith (faster drop-in runners for Actions).

- **Deploy** — this layer has fragmented by workload type:
  - *Kubernetes*: Argo CD and Flux dominate via GitOps; Argo Rollouts adds canary/blue-green primitives.
  - *Progressive delivery / verification*: Harness CD, Spinnaker (Netflix-origin, powerful, heavy), Codefresh, LaunchDarkly (feature-flag-driven release, a different model entirely).
  - *PaaS-style*: Vercel, Netlify, Render, Fly.io, Heroku, Cloudflare Workers — deployment as a byproduct of hosting.
  - *Infrastructure*: Terraform Cloud/HCP, Pulumi, Spacelift, env0.
  - *Azure/GCP native*: Azure Deployment Center, Google Cloud Deploy.

- **Orchestration** — GitHub Actions, GitLab CI, Azure Pipelines, Jenkins pipelines, Argo Workflows, Tekton (CNCF, the Kubernetes-native pipeline primitive that several vendors build on), Spinnaker, Harness, Temporal (for genuinely complex workflow logic).

**Practical read on the competitive position:** CodeBuild and CodeDeploy hold up well as components — CodeBuild's serverless economics and CodeDeploy's EC2 fleet handling are genuinely hard to replicate. CodeCommit and CodePipeline are the weaker links. Most teams have their code in GitHub or GitLab already, and once you're there, Actions or GitLab CI is a lower-friction orchestrator than CodePipeline. The common modern hybrid is GitHub for source and workflow definition, CodeBuild as the runner (via the self-hosted-runner integration, which gets you IAM roles and VPC access without long-lived keys), and either CodeDeploy or platform-native deployment at the end.
