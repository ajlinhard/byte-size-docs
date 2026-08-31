# YAML IaC Checks
If you want to check the yaml file build for some AWS Cloudformation here is the command and an explanation below:
```powershell
python -m pip install --quiet pyyaml 2>&1 | tail -5

python - <<'EOF'
import yaml

def multi_constructor(loader, tag_suffix, node):
    if isinstance(node, yaml.ScalarNode):
        return loader.construct_scalar(node)
    if isinstance(node, yaml.SequenceNode):
        return loader.construct_sequence(node)
    return loader.construct_mapping(node)

class CfnLoader(yaml.SafeLoader):
    pass

CfnLoader.add_multi_constructor('!', multi_constructor)

with open('infra/template-basic-alb.yaml') as f:
    doc = yaml.load(f, Loader=CfnLoader)

resources = doc['Resources']
print("Resource count:", len(resources))

for name in ['ChatLambdaFunction', 'ChatTargetGroup', 'ChatLambdaInvokePermission', 'ChatListenerRule']:
    print(name, '->', resources[name]['Type'])

print("Params has ChatLambdaCodeS3Key:", 'ChatLambdaCodeS3Key' in doc['Parameters'])
print("Outputs has Chat ones:", 'ChatLambdaFunctionName' in doc['Outputs'], 'ChatLambdaFunctionArn' in doc['Outputs'])
print("ChatTargetGroup name value:", resources['ChatTargetGroup']['Properties']['Name'])
print("ChatListenerRule priority:", resources['ChatListenerRule']['Properties']['Priority'])
EOF
```

## High-level summary

This is a shell + Python script that installs `pyyaml`, then parses an AWS CloudFormation template (`infra/template-basic-alb.yaml`) and prints a quick sanity-check report about it: how many resources it defines, the types of a few specific "Chat"-prefixed resources, whether certain parameters/outputs exist, and a couple of specific property values (a target group name and a listener rule priority). It's essentially a debugging/inspection script to verify that a CloudFormation template contains the expected Lambda + ALB (Application Load Balancer) wiring for something called "Chat" — likely a Lambda function fronted by an ALB via a target group and listener rule.

## Breakdown

**1. Setup**
```bash
python -m pip install --quiet pyyaml 2>&1 | tail -5
```
Installs the `pyyaml` library quietly, showing only the last 5 lines of output (in case of errors). This is needed because CloudFormation YAML uses custom tags (like `!Ref`, `!Sub`, `!GetAtt`) that plain YAML parsers choke on.

```bash
python - <<'EOF'
...
EOF
```
Runs the following Python code as an inline script via heredoc.

**2. Custom YAML tag handling**
```python
def multi_constructor(loader, tag_suffix, node):
    if isinstance(node, yaml.ScalarNode):
        return loader.construct_scalar(node)
    if isinstance(node, yaml.SequenceNode):
        return loader.construct_sequence(node)
    return loader.construct_mapping(node)

class CfnLoader(yaml.SafeLoader):
    pass

CfnLoader.add_multi_constructor('!', multi_constructor)
```
CloudFormation templates use short-form intrinsic functions like `!Ref MyResource`, `!Sub "${Var}"`, `!GetAtt Resource.Attr`. Standard YAML doesn't know these tags. This code:
- Defines a generic constructor that handles any `!`-prefixed tag by just returning its underlying scalar, sequence, or mapping value (rather than resolving the actual CloudFormation function logic).
- Creates a `CfnLoader` subclass of `SafeLoader`.
- Registers that constructor for **all** tags starting with `!` (`add_multi_constructor('!', ...)` catches any tag with that prefix), so the parser won't crash on `!Ref`, `!Sub`, `!GetAtt`, etc. — it just captures their raw content instead of evaluating them.

**3. Load the template**
```python
with open('infra/template-basic-alb.yaml') as f:
    doc = yaml.load(f, Loader=CfnLoader)
```
Opens and parses the CloudFormation template into a Python dict using the custom loader.

**4. Resource count**
```python
resources = doc['Resources']
print("Resource count:", len(resources))
```
Pulls out the `Resources` section (the core of any CFN template) and prints how many resources are defined.

**5. Check specific resource types**
```python
for name in ['ChatLambdaFunction', 'ChatTargetGroup', 'ChatLambdaInvokePermission', 'ChatListenerRule']:
    print(name, '->', resources[name]['Type'])
```
For four specific expected resources, prints their CloudFormation `Type` (e.g. `AWS::Lambda::Function`, `AWS::ElasticLoadBalancingV2::TargetGroup`, `AWS::Lambda::Permission`, `AWS::ElasticLoadBalancingV2::ListenerRule`). This confirms these resources exist and are the right kind — this pattern is the standard "Lambda behind an ALB" wiring: a Lambda function, a target group pointing at it, a permission letting the ALB invoke it, and a listener rule routing traffic to that target group.

**6. Check parameters and outputs exist**
```python
print("Params has ChatLambdaCodeS3Key:", 'ChatLambdaCodeS3Key' in doc['Parameters'])
print("Outputs has Chat ones:", 'ChatLambdaFunctionName' in doc['Outputs'], 'ChatLambdaFunctionArn' in doc['Outputs'])
```
Verifies the template has a parameter for the Lambda's S3 code location, and outputs exposing the Lambda's name and ARN (useful for other stacks/scripts to reference after deployment).

**7. Spot-check specific property values**
```python
print("ChatTargetGroup name value:", resources['ChatTargetGroup']['Properties']['Name'])
print("ChatListenerRule priority:", resources['ChatListenerRule']['Properties']['Priority'])
```
Prints the actual configured name of the target group and the priority number of the listener rule (listener rules need unique priorities to determine routing order among multiple rules).

**Net effect:** it's a quick, no-fuss integration check — "did I correctly add the Chat Lambda/ALB resources to this template, with the right types, params, outputs, and key property values?" — without needing `cfn-lint` or an actual AWS deploy to verify.
