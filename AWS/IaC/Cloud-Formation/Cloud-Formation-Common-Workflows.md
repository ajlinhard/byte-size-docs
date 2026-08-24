# Cloud Formation Common Workflows
Here are the common workflows for Cloud Formations Interactions

## Deploy a Stack
To Be Added

## Deployment Change-Sets
When you run `aws cloudformation deploy --no-execute-changeset`, it creates the change set but stops there — nothing gets applied to the stack. You then need to execute that change set explicitly.

**Step 1: Find (or set) the change set name**

If you didn't specify one, AWS CLI auto-generates a name. Find it with:

```bash
aws cloudformation list-change-sets --stack-name YOUR_STACK_NAME
```

Or, better, specify a predictable name up front next time:

```bash
aws cloudformation deploy \
  --stack-name YOUR_STACK_NAME \
  --template-file template.yaml \
  --no-execute-changeset \
  --change-set-name my-changeset
```

**Step 2 (optional but recommended): Review the change set before applying it**

```bash
aws cloudformation describe-change-set \
  --stack-name YOUR_STACK_NAME \
  --change-set-name CHANGE_SET_NAME
```

This shows exactly what will be added, modified, or deleted — the whole point of using `--no-execute-changeset` in the first place.

**Step 3: Execute it**

```bash
aws cloudformation execute-change-set \
  --stack-name YOUR_STACK_NAME \
  --change-set-name CHANGE_SET_NAME
```

This applies the change set and actually deploys the update.

A couple of things worth knowing:

- Just re-running `aws cloudformation deploy` (without `--no-execute-changeset`) will **not** execute your existing change set — it creates a brand-new one and executes that. So it works, but it doesn't use the change set you already reviewed, which somewhat defeats the purpose of reviewing it.
- If you needed IAM capabilities for the original changeset (e.g. `CAPABILITY_IAM`, `CAPABILITY_NAMED_IAM`), you don't need to pass them again for `execute-change-set` — those were already validated at changeset creation time.
- This pattern is common in CI/CD pipelines: a "plan" stage creates the change set with `--no-execute-changeset`, a human or gate reviews it, then a separate "apply" stage runs `execute-change-set`.
