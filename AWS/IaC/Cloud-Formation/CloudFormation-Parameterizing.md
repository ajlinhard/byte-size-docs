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
