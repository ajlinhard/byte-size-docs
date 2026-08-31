# GitHub or GitLab on AWS
This is a great practical question. Here's the full breakdown across your three use cases, covering both GitHub and GitLab.

---

## 🔑 The Foundation: How Authentication Works

Before diving into each use case, the most important concept is **how GitHub/GitLab proves its identity to AWS**. There are two approaches:

**Old way (avoid this):** Store `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` as CI/CD secrets. This is risky — using long-term secrets can expose your cloud account to a security incident. You might be just one exposed GitHub secret away from an AWS billing catastrophe.

**Modern way (use this): OIDC (OpenID Connect)** — When a GitHub Actions workflow runs, GitHub generates an OIDC token containing details like the repository name, branch, and workflow file. AWS validates this token against a pre-configured IAM trust policy, making sure that only workflows from authorized repositories and branches can assume the IAM role. This eliminates the risk of leaked credentials being reused, as the authentication is bound to the specific workflow that requested access.

The OIDC flow in plain terms:
1. You register GitHub/GitLab as a trusted **Identity Provider** in AWS IAM once
2. You create an **IAM Role** that GitHub/GitLab workflows can assume
3. In your pipeline, you request temporary credentials — no stored secrets

---

## Use Case 1: 🏗️ Pushing Terraform Code to Run in AWS

This is the most common integration pattern for infrastructure teams.

### GitHub Actions + Terraform

You set up the OIDC provider in IAM, create a role with a trust policy that restricts which repos and branches can assume it, and then in your GitHub Actions workflow you call `aws-actions/configure-aws-credentials` to assume the role. A typical workflow looks like this:

```yaml
# .github/workflows/terraform.yml
name: Terraform
on:
  push:
    branches: [main]
  pull_request:

permissions:
  id-token: write   # Required for OIDC
  contents: read

jobs:
  terraform:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Configure AWS credentials (OIDC)
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789:role/GitHubTerraformRole
          aws-region: us-east-1

      - uses: hashicorp/setup-terraform@v3

      - name: Terraform Init
        run: terraform init

      - name: Terraform Plan
        run: terraform plan

      - name: Terraform Apply
        if: github.ref == 'refs/heads/main'
        run: terraform apply -auto-approve
```

The key security rule: define IAM trust policies to allow role assumption only from specific repositories and branches — this ensures only approved workflows can authenticate with AWS, preventing unauthorized access. A development branch can have access to staging resources, while production deployments are restricted to workflows running on the main branch.

### GitLab CI + Terraform

GitLab uses the same OIDC concept with **ID tokens**. GitLab provides an enterprise DevOps blueprint for Terraform deployment to AWS with working example code and tutorials.

```yaml
# .gitlab-ci.yml
deploy:
  image: hashicorp/terraform:latest
  id_tokens:
    AWS_OIDC_TOKEN:
      aud: sts.amazonaws.com
  script:
    - export AWS_ROLE_ARN=arn:aws:iam::123456789:role/GitLabTerraformRole
    - export AWS_WEB_IDENTITY_TOKEN_FILE=/tmp/token
    - echo $AWS_OIDC_TOKEN > $AWS_WEB_IDENTITY_TOKEN_FILE
    - terraform init
    - terraform plan
    - terraform apply -auto-approve
  only:
    - main
```

**Terraform state** is stored in an **S3 bucket** with a **DynamoDB table for state locking** — both GitHub and GitLab workflows point their `backend "s3"` config at these.

---

## Use Case 2: 🤖 Pushing Code to Access in SageMaker

This typically means either triggering SageMaker training jobs, or making code/models available that SageMaker notebooks/endpoints pick up. There are two sub-patterns:

### Pattern A: Code → S3 → SageMaker (most common for training)

Your pipeline packages your ML code and pushes it to S3, then triggers a SageMaker Training Job via the AWS CLI or SDK.

```yaml
# GitHub Actions example
- name: Configure AWS
  uses: aws-actions/configure-aws-credentials@v4
  with:
    role-to-assume: arn:aws:iam::123456789:role/SageMakerDeployRole
    aws-region: us-east-1

- name: Package and upload code to S3
  run: |
    tar -czf code.tar.gz src/ requirements.txt
    aws s3 cp code.tar.gz s3://my-ml-bucket/training/code.tar.gz

- name: Start SageMaker Training Job
  run: |
    aws sagemaker create-training-job \
      --training-job-name "train-$(date +%Y%m%d-%H%M%S)" \
      --algorithm-specification TrainingImage=...,TrainingInputMode=File \
      --input-data-config '...' \
      --output-data-config S3OutputPath=s3://my-ml-bucket/output/ \
      --resource-config InstanceType=ml.m5.xlarge,InstanceCount=1,VolumeSizeInGB=30 \
      --role-arn arn:aws:iam::123456789:role/SageMakerExecutionRole
```

### Pattern B: Code → Docker Image → SageMaker (for custom containers)

Amazon SageMaker MLOps Projects are created via CodePipeline, and GitLab CodeStar Connections can be used as the source for those pipelines. The flow is: build a custom Docker training/inference image → push to ECR → SageMaker references it. This is covered in detail in Use Case 3 below.

### Pattern C: GitLab CI directly triggers SageMaker Pipelines

```yaml
# .gitlab-ci.yml
run_sagemaker_pipeline:
  image: python:3.11
  script:
    - pip install boto3 sagemaker
    - python scripts/trigger_sagemaker_pipeline.py
  only:
    - main
```

The IAM role assumed by the CI job needs permissions like `sagemaker:CreateTrainingJob`, `sagemaker:StartPipelineExecution`, `s3:PutObject`, and `ecr:GetAuthorizationToken`.

---

## Use Case 3: 🐳 Building Docker Images and Pushing to AWS ECR

This is the most commonly implemented pattern. The flow is: **Git push → CI builds Docker image → push to ECR → deploy (ECS/EKS/Lambda/SageMaker)**.

### GitHub Actions → ECR

```yaml
# .github/workflows/docker.yml
name: Build and Push to ECR
on:
  push:
    branches: [main]

permissions:
  id-token: write
  contents: read

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Configure AWS (OIDC)
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789:role/ECRPushRole
          aws-region: us-east-1

      - name: Login to Amazon ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v2

      - name: Build, tag, and push image
        env:
          ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
          IMAGE_TAG: ${{ github.sha }}
        run: |
          docker build -t $ECR_REGISTRY/my-app:$IMAGE_TAG .
          docker push $ECR_REGISTRY/my-app:$IMAGE_TAG
```

### GitLab CI → ECR

GitLab provides a Docker image that includes the AWS CLI for use in pipelines, and you can use it to push images to your ECR repository and automate deployments to Amazon ECS clusters.

```yaml
# .gitlab-ci.yml
build_and_push:
  image: docker:24
  services:
    - docker:24-dind
  variables:
    DOCKER_TLS_CERTDIR: "/certs"
  before_script:
    - apk add --no-cache aws-cli
    - aws ecr get-login-password --region $AWS_DEFAULT_REGION |
        docker login --username AWS --password-stdin
        $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com
  script:
    - docker build -t my-app:$CI_COMMIT_SHA .
    - docker tag my-app:$CI_COMMIT_SHA
        $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/my-app:$CI_COMMIT_SHA
    - docker push
        $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/my-app:$CI_COMMIT_SHA
  only:
    - main
```

---

## 🗺️ The Full Picture: How They All Connect

Here's how a mature team typically wires everything together end-to-end:

```
Developer pushes code
        │
        ▼
  GitHub / GitLab
        │
        ├─── Terraform repo ──► GitHub Actions/GitLab CI
        │                              │
        │                    terraform plan/apply
        │                              │
        │                         AWS IAM (via OIDC)
        │                              │
        │                    Provisions: VPC, ECS, ECR,
        │                    SageMaker, S3, DynamoDB...
        │
        ├─── App/ML code repo ──► GitHub Actions/GitLab CI
        │                              │
        │                    Build Docker image
        │                              │
        │                    Push to AWS ECR
        │                              │
        │              ┌──────────────┴──────────────┐
        │              ▼                             ▼
        │         ECS/EKS deploy            SageMaker Training Job
        │         (web apps)                (ML workloads)
```

The IAM role your CI assumes only needs the **minimum permissions** for each job type — separate roles for Terraform vs. ECR push vs. SageMaker are best practice.
