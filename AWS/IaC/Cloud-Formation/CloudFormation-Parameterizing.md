# CloudFormation Parameterizing
What are my options for passing variables to cloud formation yaml files? command line, python AWS CDK, env file? 

## Options for passing variables to CloudFormation

CloudFormation itself never reads environment variables or code directly — it only accepts key/value **Parameters** at deploy time, however they're generated. So the real question is what generates and feeds those key/value pairs. Here's the landscape:

**1. Command line (`--parameter-overrides` / `--parameters`)**
- *Pros:* Zero extra tooling, transparent, easy to script and grep, works identically in any shell/CI runner.
- *Cons:* Gets unwieldy past ~5-6 parameters; secrets end up in shell history / CI logs unless masked; no validation until CFN itself rejects a bad value; easy to typo a parameter name silently (CFN errors, but only at deploy time).

**2. Parameter files (JSON or YAML, e.g. `parameters.json` / `samconfig.toml`)**
```bash
aws cloudformation deploy --template-file t.yaml --stack-name s \
  --parameter-overrides file://params.json
```
- *Pros:* Version-controlled alongside the template, diffable in PRs, supports per-environment files (`params-dev.json`, `params-prod.json`), keeps the CLI invocation short and consistent.
- *Cons:* Still static text — dynamic values (like your content hash) need a pre-processing step to inject them; another file to keep in sync with the template's actual parameter list; secrets shouldn't live here in plaintext.

**3. Environment variables**
- CFN doesn't consume these directly — you always interpolate them into `--parameter-overrides` or a parameter file yourself, as in the script above (`$Key`, `$Hash`).
- *Pros:* Natural fit for CI/CD secrets injection (GitHub Actions secrets, GitLab CI variables, etc.) without ever writing them to a file; keeps environment-specific config out of source control.
- *Cons:* Indirection — you're always one layer removed from CFN, so failures can be "was it the env var or the CFN parameter?"; easy to have subtly different var names/casing across scripts; no built-in typing or validation.

**4. AWS CDK (Python or other languages)**
```python
lambda_.Function(self, "ChatLambda",
    code=lambda_.Code.from_asset("build/chat-lambda"),  # CDK hashes + uploads automatically
    ...
)
```
- *Pros:* This actually solves your original drift problem *natively* — CDK's asset system automatically content-hashes local code, uploads it to its bootstrap S3 bucket, and injects the hash into the template as a parameter, so you get "option 1" from earlier for free without hand-rolling it. You also get real programming constructs (loops, conditionals, functions, type checking, IDE autocomplete) instead of parameter-passing gymnastics, and CDK synthesizes the CFN template + parameter values together so they can never drift apart from each other.
- *Cons:* Real learning curve and added toolchain (Node.js runtime required even for Python CDK, since the CLI itself is Node); requires a one-time bootstrap per account/region; an abstraction layer over CFN means debugging sometimes means reading generated template output to see what CDK actually produced; larger blast radius for a change since refactoring CDK code can unintentionally alter many resources' logical IDs and force replacements if you're not careful.

**5. SSM Parameter Store / Secrets Manager (dynamic references)**
```yaml
Parameters:
  ChatLambdaCodeS3Key:
    Type: AWS::SSM::Parameter::Value<String>
    Default: /chat-lambda/code-s3-key
```
or inline dynamic reference: `'{{resolve:ssm:/chat-lambda/code-s3-key:1}}'`
- *Pros:* No secrets/values need to pass through CLI args, CI logs, or parameter files at all — CFN resolves them itself at deploy time; central place to update a value used across multiple stacks; versioned automatically by SSM.
- *Cons:* Adds an extra AWS resource to manage and an extra step to update the parameter before/after deploy; less visible in a changeset (harder to eyeball "what value am I actually deploying" without a separate lookup); SSM API throttling/limits can bite at scale; secure strings (`SecureString`) can't be used directly in `Fn::Sub` outside dynamic references without extra config.

---

**For your specific use case** — the content-hash-of-a-zip pattern — the pragmatic ranking is:
- **Quick/simple pipeline, staying in raw CFN:** command line or parameter file, computed by a small wrapper script (what you already have).
- **Longer-term investment, willing to adopt new tooling:** CDK, since it eliminates the whole "remember to hash and pass the key" problem structurally rather than by convention.

---
# Parameterizing Example
## 1. Cross-stack references

**Order within the YAML file doesn't matter at all.** CloudFormation templates are declarative, not executed top-to-bottom. You can put `Outputs` at the top, bottom, or middle — the parser reads the whole document and builds a dependency graph from `Ref` / `!GetAtt` / `DependsOn`. Convention is Parameters → Mappings → Conditions → Resources → Outputs, but that's just readability.

What *does* matter is **stack deploy order**: the exporting stack must exist and be in a complete state before you create the importing stack.

**Exporting stack** (`network-stack`):

```yaml
Resources:
  MyVpc:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: 10.0.0.0/16
  PrivateSubnetA:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref MyVpc
      CidrBlock: 10.0.1.0/24

Outputs:
  VpcId:
    Value: !Ref MyVpc
    Export:
      Name: !Sub "${AWS::StackName}-VpcId"
  PrivateSubnets:
    Value: !Join [",", [!Ref PrivateSubnetA, !Ref PrivateSubnetB]]
    Export:
      Name: !Sub "${AWS::StackName}-PrivateSubnets"
```

**Importing stack:**

```yaml
Parameters:
  NetworkStackName:
    Type: String
    Default: network-stack

Resources:
  AppSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: App SG
      VpcId: !ImportValue
        "Fn::Sub": "${NetworkStackName}-VpcId"

  Asg:
    Type: AWS::AutoScaling::AutoScalingGroup
    Properties:
      VPCZoneIdentifier: !Split
        - ","
        - !ImportValue
            "Fn::Sub": "${NetworkStackName}-PrivateSubnets"
```

Parameterizing the stack name like that is worth doing — it lets you point dev/prod app stacks at different network stacks without editing the template.

Rules and gotchas worth knowing up front:

- Exports are **region- and account-scoped**, and export names must be globally unique within a region. Prefixing with `${AWS::StackName}` is the standard way to avoid collisions.
- You **cannot delete or modify an exported output** while another stack imports it. This is the big one — it means you can't easily change the network stack's outputs later. To break the link you have to update the consuming stack off the import first.
- You can't use `Fn::ImportValue` inside the `Export.Name` field, and you can't use it in `Fn::Sub` shorthand (`${...}`) — hence the slightly awkward nested `"Fn::Sub"` syntax above.
- Lists can't be exported directly; join to a string and `!Split` on the way in, as shown.

If you want the coupling without the rigidity, **nested stacks** are the other option: a parent template with `AWS::CloudFormation::Stack` resources, and children referenced via `!GetAtt NetworkStack.Outputs.VpcId`. No exports involved, so no deletion locking — but the children are then owned by the parent and not independently deployable.

## 2. Parameter types take IDs, not ARNs

`AWS::EC2::VPC::Id` and friends are a fixed, enumerated list of **AWS-specific parameter types** that CloudFormation understands. They're not a generic "any AWS resource" mechanism — you can't write `AWS::S3::Bucket::Arn` or invent new ones.

The value you pass is the **physical ID** in its native format:

| Type | Value you pass |
|---|---|
| `AWS::EC2::VPC::Id` | `vpc-0abc123def456` |
| `AWS::EC2::Subnet::Id` | `subnet-0aaa111` |
| `AWS::EC2::SecurityGroup::Id` | `sg-0bbb222` |
| `AWS::EC2::KeyPair::KeyName` | `my-keypair` |
| `AWS::EC2::AvailabilityZone::Name` | `us-west-2a` |
| `AWS::EC2::Image::Id` | `ami-0abc...` |
| `AWS::EC2::Instance::Id` | `i-0abc...` |
| `AWS::EC2::Volume::Id` | `vol-0abc...` |
| `AWS::Route53::HostedZone::Id` | `Z1D633PJN98FT9` |

Each also has a `List<...>` variant (`List<AWS::EC2::Subnet::Id>`, etc.), which is what you'd use for multi-AZ subnets.

The benefit of these over plain `String` is real: CloudFormation validates the ID exists in your account and region *before* starting the stack operation, and the console renders a dropdown instead of a free-text box. For a `List<AWS::EC2::Subnet::Id>` it renders a multi-select.

For anything not on the list — an ARN, a bucket name, an SNS topic — just use `Type: String` and add your own guardrails:

```yaml
Parameters:
  AlarmTopicArn:
    Type: String
    AllowedPattern: "^arn:aws:sns:[a-z0-9-]+:\\d{12}:.+$"
    ConstraintDescription: Must be a valid SNS topic ARN
```

One caveat with the AWS-specific types: because validation happens at submit time, they don't play well with `Conditions` where the resource might not be needed. If a parameter is conditionally unused, CloudFormation will still reject an empty or invalid value — so those often have to be `String`.
