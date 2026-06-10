# Terraform Init Workspace
For the following set of Terraform commands walk me through what they do high level and behind the scenes:

```
terraform init -backend-config=backend-dev.hcl

# 2. Create your workspace
terraform workspace new dev-<yourname>

```
## Terraform Command Walkthrough

### Command 1: `terraform init -backend-config=backend-dev.hcl`

**High Level:** Initializes your Terraform working directory and configures where state will be stored.

**Behind the Scenes:**

1. **Reads your `.tf` files** — Terraform scans the current directory for configuration files to understand what providers and modules are needed.

2. **Loads the backend config** — The `-backend-config=backend-dev.hcl` flag injects additional backend configuration at runtime rather than hardcoding it in your `.tf` files. The `.hcl` file typically contains environment-specific values like:
   ```hcl
   bucket         = "my-dev-terraform-state"
   key            = "dev/terraform.tfstate"
   region         = "us-east-1"
   ```

3. **Initializes the backend** — Terraform connects to the remote backend (e.g. S3, GCS, Azure Blob) and verifies it's accessible. This is where your **state file will live**.

4. **Downloads providers** — Any providers declared in your config (e.g. `aws`, `google`) are downloaded from the Terraform Registry into `.terraform/providers/`.

5. **Downloads modules** — Any remote modules referenced are fetched and cached in `.terraform/modules/`.

6. **Creates `.terraform.lock.hcl`** — A dependency lock file is written/updated to pin exact provider versions for consistency across your team.

---

### Command 2: `terraform workspace new dev-<yourname>`

**High Level:** Creates an isolated, named environment so your state doesn't collide with teammates' infrastructure.

**Behind the Scenes:**

1. **Creates a new workspace entry** — Terraform registers a new workspace named `dev-<yourname>` within the configured backend.

2. **Isolates state** — Each workspace gets its **own state file**. On a remote backend like S3 this typically looks like:
   ```
   env:/dev-<yourname>/terraform.tfstate   # your workspace
   env:/dev-alice/terraform.tfstate        # a teammate's workspace
   terraform.tfstate                       # the "default" workspace
   ```

3. **Switches your active context** — After creation, Terraform automatically **switches into** the new workspace. It's equivalent to running `terraform workspace select dev-<yourname>`.

4. **Exposes `terraform.workspace` variable** — Your `.tf` configs can now reference `terraform.workspace` to dynamically change behavior (e.g. instance sizes, naming, tags) based on which workspace is active.

---

### The Big Picture

```
terraform init                        terraform workspace new dev-you
      │                                           │
      ▼                                           ▼
 Downloads providers              Creates isolated state path
 Connects to backend         →    so your plan/apply only affects
 Locks dependency versions         YOUR infrastructure, not a teammate's
```

The pattern — shared backend config + personal workspaces — is a common team workflow that lets everyone work against the same backend (e.g. same S3 bucket) without stepping on each other's state.
