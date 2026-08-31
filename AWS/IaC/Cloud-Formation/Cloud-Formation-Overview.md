# AWS Cloud Formation Overview
AWS CloudFormation is a service that enables users to provision and manage AWS resources by treating infrastructure as code. It uses templates, typically written in JSON or YAML, to define the desired state of your infrastructure, and CloudFormation then handles the creation, updating, and deletion of those resources. 

### Documentation and Tutorials
- [AWS CloudFormation - Home Page](https://aws.amazon.com/cloudformation/)
- [Youtube CloudFormation Overview](https://www.youtube.com/watch?v=0Sh9OySCyb4)
- [AWS CloudFormation as IaC Tool](https://docs.aws.amazon.com/prescriptive-guidance/latest/choose-iac-tool/cloudformation.html)
- [AWS CloudFormation Artifacts](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/continuous-delivery-codepipeline-cfn-artifacts.html)

CloudFormation will feel familiar in shape but different in a few load-bearing ways. Here's the mapping first, since that's the fastest unlock:

| Terraform | CloudFormation |
|---|---|
| `.tf` files | Template (YAML/JSON) |
| `terraform.tfstate` + backend | **Stack** — state lives server-side, managed by AWS |
| `terraform plan` | Change set |
| `variable` | `Parameters` |
| `locals` | `Mappings` (static lookup tables only) |
| `output` | `Outputs` |
| `terraform_remote_state` | `Fn::ImportValue` + `Export` |
| `depends_on` | `DependsOn` |
| `lifecycle { prevent_destroy }` | `DeletionPolicy: Retain` |
| provider ecosystem | AWS resources only (plus custom resources) |
| `count` / `for_each` | ✗ — no real loops |

The single biggest mental shift: **the stack *is* the state**. There's no state file to store, lock, or corrupt. You can't `terraform import` casually, you can't hand-edit state, and you can't have two stacks own the same resource. Deleting a stack deletes its resources.

## Key concepts

**Template & Stack.** A template is a static document. A stack is one *instantiation* of it. Deploy the same template three times with different parameters and stack names, you get three independent stacks. That's how dev/prod is normally done — same template, different stacks, no workspaces needed.

**Resources** — the only required section. Each entry has a *logical ID* (your name for it, used for references within the template) and a *physical ID* (what AWS actually names it).

```yaml
Resources:
  UploadBucket:              # logical ID
    Type: AWS::S3::Bucket
    Properties:
      BucketName: my-app-uploads-dev   # physical ID
```

Changing a logical ID means CloudFormation deletes the old resource and creates a new one — it has no idea they're the same thing. Same trap as renaming a Terraform resource without `moved`.

**Parameters** — deploy-time inputs, with built-in validation:

```yaml
Parameters:
  Environment:
    Type: String
    AllowedValues: [dev, prod]
```

**Intrinsic functions.** `!Ref` is the one that will bite you. Against a parameter it returns the value; against a resource it returns that resource's "primary identifier" — which is *different for every resource type*. `!Ref` on a bucket gives the bucket name; on an IAM role it gives the role name; on an SNS topic it gives the full ARN. There's no consistency, you look it up in the "Return values" section of each resource's docs. When you want something specific, use `!GetAtt`:

```yaml
!Ref UploadBucket              # my-app-uploads-dev
!GetAtt UploadBucket.Arn       # arn:aws:s3:::my-app-uploads-dev
!Sub 'app-${Environment}-${AWS::AccountId}'
```

`AWS::AccountId`, `AWS::Region`, `AWS::StackName`, `AWS::Partition`, and `AWS::NoValue` are pseudo-parameters — always available, no declaration.

**Mappings** — static two-level lookup tables. This is the idiomatic way to vary config by environment:

```yaml
Mappings:
  EnvConfig:
    dev:  { MemorySize: 128, LogRetentionDays: 7 }
    prod: { MemorySize: 512, LogRetentionDays: 90 }
```

Read with `!FindInMap [EnvConfig, !Ref Environment, MemorySize]`. Keys must be literals — no computed values, no functions inside a mapping.

**Conditions** — first-class, and better than the `count = var.enabled ? 1 : 0` trick. Declare once, then use as a resource-level attribute or inline in any property:

```yaml
Conditions:
  IsProd: !Equals [!Ref Environment, prod]
```

**Outputs & Exports.** Outputs are readable via the API. Add `Export` and another stack can consume them with `!ImportValue`. Two caveats: export names must be unique per account per region, and you **cannot delete or modify an exported value while another stack imports it**. This creates hard coupling — many teams prefer writing values to SSM Parameter Store and reading them at deploy time instead.

**Change sets** = `terraform plan`, but with an important weakness: it tells you an update requires *replacement*, but it won't always tell you *why*, and it can't evaluate values that resolve at deploy time. Treat it as less precise than a Terraform plan.

**Rollback.** This has no Terraform equivalent and it's the thing that surprises people most. If a create fails, CloudFormation deletes everything it just made. If an *update* fails, it attempts to roll the entire stack back to the previous state. When the rollback itself fails you land in `UPDATE_ROLLBACK_FAILED` — a stuck state where you must call `continue-update-rollback`, sometimes skipping specific resources, before you can do anything else. Budget for hitting this.

**Deletion policies:**

```yaml
DeletionPolicy: Retain
UpdateReplacePolicy: Retain
```

You want both on stateful resources. `DeletionPolicy` covers stack deletion; `UpdateReplacePolicy` covers the case where a property change forces replacement.

**No loops.** There's no `for_each`. If you need ten similar queues, you write ten blocks, use nested stacks, or generate the template with CDK. (`Fn::ForEach` exists via the `AWS::LanguageExtensions` transform, but it's limited and best treated as an advanced tool.)

## The worked example

Let me build the template — an S3 bucket that triggers a Lambda on upload, deployable to dev and prod from one file.## The circular dependency — read this part twice

The comments flag it, but it's worth calling out because it will happen to you within your first week.

You'd naturally write the IAM policy resource as `!GetAtt UploadBucket.Arn`. That creates: bucket needs function ARN (for the notification) → function needs role ARN → role needs bucket ARN. CloudFormation detects the cycle and refuses to deploy, with an error that doesn't clearly say which reference caused it.

The fix is to **name resources deterministically and construct ARNs as strings**. Once `BucketName` is `!Sub '${AppName}-uploads-${Environment}-${AWS::AccountId}'`, you can build that ARN anywhere without referencing the bucket resource. `DependsOn: InvokePermission` then handles the ordering that the implicit graph no longer knows about.

This pattern — trade an implicit reference for a computed string plus an explicit `DependsOn` — is the standard escape hatch for cycles in CloudFormation.

## Deploying

```bash
# dev
aws cloudformation deploy \
  --template-file template.yaml \
  --stack-name fileproc-dev \
  --parameter-overrides Environment=dev AppName=fileproc \
  --capabilities CAPABILITY_IAM \
  --tags Environment=dev Owner=platform

# prod - same template, different stack, different params
aws cloudformation deploy \
  --template-file template.yaml \
  --stack-name fileproc-prod \
  --parameter-overrides Environment=prod AppName=fileproc AlarmEmail=oncall@example.com \
  --capabilities CAPABILITY_IAM \
  --tags Environment=prod Owner=platform
```

`--capabilities CAPABILITY_IAM` is mandatory whenever a template creates IAM resources — an explicit acknowledgement that you're granting permissions. Use `CAPABILITY_NAMED_IAM` if you set explicit role or policy names.

To see a plan before applying, skip `deploy` and drive change sets directly:

```bash
aws cloudformation deploy ... --no-execute-changeset   # creates, doesn't run
aws cloudformation describe-change-set --change-set-name <arn>
aws cloudformation execute-change-set --change-set-name <arn>
```

Test it with `aws s3 cp test.txt s3://fileproc-uploads-dev-<account>/incoming/`, then check CloudWatch Logs.

## Rollback (Auto?)
Yes there is an auto rollback — CloudFormation is declarative. You write a JSON or YAML template describing the desired end state, and the service figures out the create/update/delete actions and dependency ordering (with `DependsOn` and intrinsic functions like `Ref`/`GetAtt` for explicit ordering). The main structural difference from Terraform is that CloudFormation is AWS-only and AWS holds the state for you as a *stack* — there's no state file for you to store, lock, or corrupt.

**On rollback — this is actually where CloudFormation is stronger than Terraform.** It rolls back automatically by default:

- **Create failure:** the stack enters `ROLLBACK_IN_PROGRESS` and deletes everything it made. You can override with `--on-failure DO_NOTHING` (leave it for debugging) or `RETAIN`, or `--disable-rollback`.
- **Update failure:** `UPDATE_ROLLBACK_IN_PROGRESS` reverts resources to the last known-good template. No partial-apply mess to reconcile by hand.
- **Alarm-based rollback:** a stack's `RollbackConfiguration` can point at CloudWatch alarms with a monitoring period after the deploy completes — if an alarm fires within that window, CloudFormation reverses the update. That's a genuine deployment-health rollback, not just a failure rollback.

Terraform has nothing equivalent. A failed `apply` leaves you with partial state and you fix forward.

The one caveat worth knowing before you commit: rollback can itself fail (`UPDATE_ROLLBACK_FAILED`), typically when a resource can't return to its prior state — an S3 bucket that isn't empty, a security group still referenced elsewhere. You then have to call `continue-update-rollback`, sometimes with `--resources-to-skip`, and manually reconcile. When people complain about CloudFormation, this stuck-stack scenario is usually why.

**Altering and spinning down:**

| Task | CloudFormation | Terraform |
|---|---|---|
| Preview changes | Change Sets | `terraform plan` |
| Apply changes | `update-stack` / `deploy` | `terraform apply` |
| Tear down everything | `delete-stack` | `terraform destroy` |
| Detect manual drift | Drift detection | `plan` shows it |

`delete-stack` removes all resources in reverse dependency order. To protect things you don't want vaporized, set `DeletionPolicy: Retain` or `Snapshot` on individual resources (databases, buckets), and `UpdateReplacePolicy` for the case where an update would replace rather than modify. Enable termination protection on production stacks so an accidental delete is rejected outright.

For scaling down rather than deleting, you just change the template or a parameter — desired capacity, instance type, provisioned throughput — and run an update. Same declarative loop.

One practical note: if you're evaluating both, CDK is worth a look. It gives you TypeScript/Python that synthesizes CloudFormation templates, so you keep the rollback semantics while writing something less painful than raw YAML.

## Things that differ from Terraform in ways that cost time

**Stack-level tags propagate automatically.** `--tags` on the stack applies to every resource that supports tagging. No `default_tags` provider block needed.

**Prod isn't just different parameters, structurally.** Notice `ErrorAlarm` and `AlarmTopic` simply don't exist in the dev stack. Conditions remove resources from the graph entirely — closer to Terraform's `count = 0` than to a disabled flag.

**Updates that replace resources are silent-ish.** Each resource's docs list, per property, whether changing it causes *No interruption*, *Some interruption*, or *Replacement*. Changing `BucketName` replaces the bucket. Learn to check that column before shipping a change.

**Deleting a stack with a `Retain` bucket leaves the bucket behind.** The stack deletes fine, the bucket stays, and your next deploy fails with "bucket already exists" because names are globally unique. Empty and delete it manually, or drop the retain policy for dev.

**IAM policy changes are eventually consistent.** A Lambda can deploy successfully and still get `AccessDenied` for a few seconds. Not a CloudFormation bug.

## Where to go next

Once this clicks, look at **AWS SAM** — a transform (`Transform: AWS::Serverless-2016-10-31`) that adds serverless-specific resource types on top of CloudFormation. `AWS::Serverless::Function` collapses the role, log group, permission, and event source in this template into about eight lines. It compiles down to plain CloudFormation, so everything above still applies. If you want loops and real programming constructs, **CDK** generates templates from TypeScript or Python.

For multi-account or multi-region rollouts, **StackSets** deploys one template across an AWS Organization — the closest thing to running Terraform across many workspaces from one place.
