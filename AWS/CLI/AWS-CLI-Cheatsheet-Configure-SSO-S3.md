# AWS CLI Cheatsheet (Configure, SSO, S3)

A practical reference for AWS CLI **v2**. Covers the three families you touch on almost every project: credential setup (`aws configure`), identity federation (`aws sso`), and object storage (`aws s3`).

**Mental model:** the CLI has two layers. *API-level* commands (`aws s3api`, `aws ec2`, ...) map 1:1 to service API operations. *High-level* commands (`aws s3`, `aws sso`) are hand-written conveniences that wrap many API calls behind one verb — `aws s3 sync` alone can fire thousands of requests. When a high-level command can't express what you need, drop to the `api` variant.

---

## Service Family Overview

The **Family** column links to that family's full section — this table doubles as the table of contents.

| Start Syntax | Family | Domain / What It Covers |
|---|---|---|
| `aws [options]` | [Global Options](#global-options) | Flags accepted by *every* command: profile, region, output shape, JMESPath filtering, endpoint overrides, timeouts. Learn these once and they pay off everywhere. |
| `aws configure ...` | [aws configure](#aws-configure) | Local credential and settings management. Reads/writes `~/.aws/credentials` and `~/.aws/config`. Purely client-side — no network calls, no IAM permissions needed. |
| `aws sso ...` | [aws sso](#aws-sso) | Browser-based login against AWS IAM Identity Center (formerly AWS SSO). Issues short-lived credentials cached in `~/.aws/sso/cache`. The modern replacement for long-lived access keys. |
| `aws s3 ...` | [aws s3](#aws-s3) | High-level object storage operations: buckets, uploads, downloads, recursive copies, directory sync, presigned URLs. Handles multipart transfers and parallelism for you. |

---

## Global Options

**Insight:** these come *after* `aws` or after the subcommand — position doesn't matter. `--query` runs client-side (after the response arrives), so it saves you `jq`, not bandwidth. `--profile` is the single most useful flag here; make it a habit rather than relying on a default profile you'll eventually forget you set.

```bash
# List buckets as plain text, using a named profile
aws s3api list-buckets --profile prod --output text --query 'Buckets[].Name'

# Point at LocalStack instead of real AWS
aws s3 ls --endpoint-url http://localhost:4566

# Read a public bucket with no credentials at all
aws s3 ls s3://commoncrawl/ --no-sign-request

# Stop the pager from swallowing output in scripts
aws ec2 describe-instances --no-cli-pager
```

| Parameter | Description | Req/Opt | Default | Example Values |
|---|---|---|---|---|
| `--profile` | Named profile from `~/.aws/config` to use for credentials and settings. | Optional | `default` (or `$AWS_PROFILE`) | `prod`, `dev-sso`, `sandbox` |
| `--region` | AWS region to target. Overrides profile and env var. | Optional | Profile's `region` / `$AWS_DEFAULT_REGION` | `us-east-1`, `eu-west-2` |
| `--output` | Response format. | Optional | `json` | `json`, `text`, `table`, `yaml`, `yaml-stream` |
| `--query` | JMESPath expression filtering the response client-side. | Optional | — | `'Reservations[].Instances[].InstanceId'` |
| `--endpoint-url` | Override the service endpoint (local emulators, VPC endpoints, S3-compatible stores). | Optional | Service default | `http://localhost:4566` |
| `--no-sign-request` | Skip credential signing entirely — anonymous access. | Optional | Off (requests signed) | flag only |
| `--no-verify-ssl` | Skip TLS certificate verification. Debugging only; never in prod. | Optional | Off | flag only |
| `--ca-bundle` | Path to a custom CA cert bundle (corporate MITM proxies). | Optional | System bundle | `/etc/ssl/corp-ca.pem` |
| `--debug` | Full wire-level logging to stderr. Verbose but the fastest way to see the actual request. | Optional | Off | flag only |
| `--no-paginate` | Return only the first page instead of auto-following pagination tokens. | Optional | Off (auto-paginates) | flag only |
| `--page-size` | Items requested per API call while paginating. Lower it if a service throttles you. | Optional | Service-defined (often 1000) | `100`, `500` |
| `--max-items` | Stop after N total items across pages. | Optional | Unlimited | `50` |
| `--cli-read-timeout` | Socket read timeout, seconds. `0` disables. | Optional | `60` | `0`, `120` |
| `--cli-connect-timeout` | Connection timeout, seconds. `0` disables. | Optional | `60` | `10` |
| `--cli-binary-format` | How blob parameters are interpreted. v2 changed this default — set `raw-in-base64-out` if porting v1 scripts. | Optional | `base64` | `base64`, `raw-in-base64-out` |
| `--cli-auto-prompt` | Interactive prompting for commands/params. Great for exploration. | Optional | Off | flag only |
| `--no-cli-pager` | Disable the pager (`less`) for output. Essential in CI. | Optional | Pager on in v2 | flag only |
| `--color` | Colorize output. | Optional | `auto` | `on`, `off`, `auto` |
| `--cli-input-json` / `--cli-input-yaml` | Supply all parameters from a file instead of flags. | Optional | — | `file://params.json` |
| `--generate-cli-skeleton` | Emit a parameter template instead of executing. | Optional | — | `input`, `output`, `yaml-input` |
| `--version` | Print CLI version and exit. | Optional | — | flag only |

---

## aws configure

**Domain:** everything about *local* credential and settings files. Nothing here talks to AWS (with the exception of `aws configure sso`, which does an Identity Center handshake).

**Insight:** credentials live in `~/.aws/credentials`, everything else in `~/.aws/config`. In `config`, non-default profiles need the literal prefix `[profile name]`; in `credentials` they're just `[name]`. This inconsistency trips up nearly everyone once. Precedence runs: command-line flag → environment variable → profile in config files → IMDS/container role.

Bare `aws configure` prompts for four values and writes them to the profile:

```bash
# Interactive setup of the default profile
aws configure

# Interactive setup of a named profile
aws configure --profile staging

# Show which settings are active and where each one came from
aws configure list

# List every profile name defined locally
aws configure list-profiles

# Read a single value
aws configure get region --profile staging

# Write a single value without prompts (ideal for scripts/dotfiles)
aws configure set region us-west-2 --profile staging
aws configure set output table --profile staging

# Set a nested/subkey value (role assumption)
aws configure set profile.staging.role_arn arn:aws:iam::111122223333:role/Deploy
aws configure set profile.staging.source_profile default

# Import keys from the CSV that the IAM console hands you
aws configure import --csv file://new_user_credentials.csv

# Hand credentials to another tool (Terraform, Docker, etc.)
aws configure export-credentials --profile prod --format env
eval "$(aws configure export-credentials --profile prod --format env)"

# Guided IAM Identity Center profile setup
aws configure sso --profile dev-sso
```

### `aws configure` (interactive)

| Parameter | Description | Req/Opt | Default | Example Values |
|---|---|---|---|---|
| `--profile` | Profile to create or overwrite. | Optional | `default` | `staging`, `client-a` |
| *AWS Access Key ID* (prompt) | Long-lived IAM access key. Press Enter to keep existing. | Prompted | Existing value | `AKIAIOSFODNN7EXAMPLE` |
| *AWS Secret Access Key* (prompt) | Matching secret. Press Enter to keep existing. | Prompted | Existing value | `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY` |
| *Default region name* (prompt) | Region used when `--region` is absent. | Prompted | Existing value | `us-east-1` |
| *Default output format* (prompt) | Output shape when `--output` is absent. | Prompted | `json` | `json`, `text`, `table`, `yaml` |

### `aws configure list`

Prints the resolved value, its type, and its origin for each of the four core settings. Values are truncated — a deliberate safety feature, not a bug.

| Parameter | Description | Req/Opt | Default | Example Values |
|---|---|---|---|---|
| `--profile` | Profile to inspect. | Optional | `default` | `prod` |

### `aws configure list-profiles`

Takes no arguments beyond globals. Emits one profile name per line — pipe it into `fzf` for a quick profile switcher.

### `aws configure get`

| Parameter | Description | Req/Opt | Default | Example Values |
|---|---|---|---|---|
| `varname` (positional) | Setting to read. Dotted paths reach into other profiles. | **Required** | — | `region`, `output`, `aws_access_key_id`, `profile.prod.role_arn` |
| `--profile` | Profile to read from. | Optional | `default` | `staging` |

> Exit code is `1` if the setting is unset — handy for `if aws configure get ... >/dev/null; then`.

### `aws configure set`

| Parameter | Description | Req/Opt | Default | Example Values |
|---|---|---|---|---|
| `varname` (positional) | Setting to write. Dotted paths target another profile. | **Required** | — | `region`, `cli_pager`, `profile.dev.role_arn` |
| `value` (positional) | Value to write. Creates the profile/file if missing. | **Required** | — | `eu-central-1`, `table`, `""` |
| `--profile` | Profile to write to. | Optional | `default` | `dev` |

### `aws configure import`

| Parameter | Description | Req/Opt | Default | Example Values |
|---|---|---|---|---|
| `--csv` | Path to the IAM-generated credentials CSV. Must use the `file://` prefix. | **Required** | — | `file://credentials.csv` |
| `--profile-prefix` | String prepended to each imported profile name (profiles are named after the IAM user). | Optional | None | `client-`, `prod-` |
| `--skip-invalid` | Skip rows whose keys are invalid instead of aborting the whole import. | Optional | Off (fails fast) | flag only |

### `aws configure export-credentials`

Resolves credentials by the full chain (including SSO and assumed roles) and prints them. The bridge for tools that can't do SSO themselves.

| Parameter | Description | Req/Opt | Default | Example Values |
|---|---|---|---|---|
| `--profile` | Profile whose credentials to resolve. | Optional | `default` | `prod-sso` |
| `--format` | Output shape. `process` is the credential_process JSON contract. | Optional | `process` | `process`, `env`, `env-no-export`, `powershell`, `windows-cmd` |

### `aws configure sso` / `aws configure sso-session`

Interactive wizards that open a browser, then write an Identity Center profile. `sso-session` creates a reusable named session block that multiple profiles can share — the right choice when you have many accounts behind one login.

| Parameter | Description | Req/Opt | Default | Example Values |
|---|---|---|---|---|
| `--profile` | Profile to create (`configure sso` only). | Optional | `default` | `dev-sso` |
| `--use-device-code` | Use the device-code flow instead of the auth-code flow. | Optional | Off | flag only |
| `--no-browser` | Print the URL rather than launching a browser. Required over SSH. | Optional | Off | flag only |
| *SSO session name* (prompt) | Name of the reusable session block. | Prompted | — | `my-company` |
| *SSO start URL* (prompt) | Your Identity Center portal URL. | Prompted | — | `https://my-company.awsapps.com/start` |
| *SSO region* (prompt) | Region where Identity Center is deployed — often *not* your workload region. | Prompted | — | `us-east-1` |
| *SSO registration scopes* (prompt) | OAuth scopes requested. | Prompted | `sso:account:access` | `sso:account:access` |

---

## aws sso

**Domain:** obtaining and discarding short-lived credentials from IAM Identity Center.

**Insight:** `aws sso login` authenticates a *session*, not a profile — log in once and every profile sharing that `sso_session` works. Tokens land in `~/.aws/sso/cache` and typically expire in 8 hours (configurable by your admin). Note the asymmetry: `logout` clears the local cache but **does not** revoke the token server-side. On a shared or compromised machine, deleting the file is not enough; an admin must revoke the session in the Identity Center console.

The `list-*` and `get-role-credentials` subcommands are thin API wrappers requiring a raw `--access-token`. In day-to-day work you'll rarely reach for them — they exist for scripting portal enumeration.

```bash
# Log in for a session shared across profiles (preferred)
aws sso login --sso-session my-company

# Log in via a specific profile's session
aws sso login --profile dev-sso

# Headless / SSH box — print the URL instead of opening a browser
aws sso login --profile dev-sso --no-browser

# Verify it worked
aws sts get-caller-identity --profile dev-sso

# Clear cached tokens for all sessions on this machine
aws sso logout

# Scripting: enumerate what the logged-in user can reach
TOKEN=$(jq -r '.accessToken' ~/.aws/sso/cache/*.json | head -1)
aws sso list-accounts --access-token "$TOKEN" --region us-east-1
aws sso list-account-roles --account-id 111122223333 --access-token "$TOKEN" --region us-east-1
aws sso get-role-credentials --role-name ReadOnly --account-id 111122223333 \
  --access-token "$TOKEN" --region us-east-1
```

### `aws sso login`

| Parameter | Description | Req/Opt | Default | Example Values |
|---|---|---|---|---|
| `--sso-session` | Named session block from `~/.aws/config` to authenticate. | Optional* | — | `my-company` |
| `--profile` | Profile whose session to authenticate. *One of this or `--sso-session` is needed.* | Optional* | `default` | `dev-sso` |
| `--no-browser` | Print the verification URL instead of auto-opening a browser. | Optional | Off | flag only |
| `--use-device-code` | Force the legacy device-code grant. | Optional | Off (auth code w/ PKCE) | flag only |

> Already-valid cached token? The command exits immediately without a browser round trip — safe to call at the top of any script.

### `aws sso logout`

No parameters beyond globals. Wipes `~/.aws/sso/cache` and the cached role credentials in `~/.aws/cli/cache` for **all** sessions — not just the current profile.

### `aws sso list-accounts`

| Parameter | Description | Req/Opt | Default | Example Values |
|---|---|---|---|---|
| `--access-token` | Bearer token from the SSO cache. | **Required** | — | `eyJlbmMiOiJBMjU2R0NN...` |
| `--region` | Must be the *Identity Center* region, not your workload region. | **Required** (effectively) | Profile region | `us-east-1` |
| `--max-items` / `--page-size` / `--starting-token` | Standard pagination controls. | Optional | Service default | `20` |

### `aws sso list-account-roles`

| Parameter | Description | Req/Opt | Default | Example Values |
|---|---|---|---|---|
| `--account-id` | 12-digit account to enumerate roles in. | **Required** | — | `111122223333` |
| `--access-token` | Bearer token from the SSO cache. | **Required** | — | `eyJlbmMiOiJBMjU2R0NN...` |
| `--region` | Identity Center region. | **Required** (effectively) | Profile region | `us-east-1` |
| `--max-items` / `--page-size` / `--starting-token` | Pagination controls. | Optional | Service default | `20` |

### `aws sso get-role-credentials`

| Parameter | Description | Req/Opt | Default | Example Values |
|---|---|---|---|---|
| `--role-name` | Permission set / role to assume. | **Required** | — | `ReadOnly`, `AdministratorAccess` |
| `--account-id` | Account the role lives in. | **Required** | — | `111122223333` |
| `--access-token` | Bearer token from the SSO cache. | **Required** | — | `eyJlbmMiOiJBMjU2R0NN...` |
| `--region` | Identity Center region. | **Required** (effectively) | Profile region | `us-east-1` |

Returns `accessKeyId`, `secretAccessKey`, `sessionToken`, and `expiration` (epoch milliseconds).

---

## aws s3

**Domain:** high-level object storage. Buckets, objects, recursive transfers, directory sync, presigned URLs.

**Insight:** `aws s3` is not the S3 API — it's a transfer manager. It automatically chunks large files into multipart uploads, runs transfers in parallel, and retries. That convenience costs you precision: for bucket policies, versioning, lifecycle rules, or object tagging, use `aws s3api`. Tune throughput via `~/.aws/config`, not flags:

```ini
[profile prod]
s3 =
  max_concurrent_requests = 20
  multipart_threshold = 64MB
  multipart_chunksize = 16MB
```

**Filter gotcha:** `--exclude` and `--include` are evaluated **in order**, each overriding the last. The exclude-all-then-include-some pattern is the only one that reliably works:

```bash
aws s3 cp . s3://bucket/ --recursive --exclude "*" --include "*.log"
```

Reversing those two flags silently uploads everything.

```bash
# Buckets and listings
aws s3 ls
aws s3 ls s3://my-bucket/logs/ --human-readable --summarize
aws s3 ls s3://my-bucket/ --recursive

# Create / delete buckets
aws s3 mb s3://my-new-bucket --region eu-west-1
aws s3 rb s3://my-old-bucket              # must already be empty
aws s3 rb s3://my-old-bucket --force      # empties it first

# Copy
aws s3 cp report.pdf s3://my-bucket/reports/
aws s3 cp s3://my-bucket/reports/report.pdf ./
aws s3 cp s3://bucket-a/data/ s3://bucket-b/data/ --recursive
aws s3 cp ./build s3://my-bucket/site --recursive --acl public-read

# Stream to and from stdio
aws s3 cp - s3://my-bucket/log.txt < app.log
aws s3 cp s3://my-bucket/big.gz - | gunzip | head

# Move (copy + delete source)
aws s3 mv s3://my-bucket/tmp/file.txt s3://my-bucket/archive/file.txt

# Delete
aws s3 rm s3://my-bucket/tmp/file.txt
aws s3 rm s3://my-bucket/tmp/ --recursive --exclude "*" --include "*.tmp"

# Sync — always dry-run first when --delete is involved
aws s3 sync ./dist s3://my-bucket/site --delete --dryrun
aws s3 sync ./dist s3://my-bucket/site --delete
aws s3 sync s3://bucket-a s3://bucket-b --source-region us-east-1

# Encryption and storage class
aws s3 cp secrets.tar s3://my-bucket/ --sse aws:kms \
  --sse-kms-key-id arn:aws:kms:us-east-1:111122223333:key/abcd-1234
aws s3 cp archive.zip s3://my-bucket/ --storage-class GLACIER

# Time-limited download link (7 days = max for sigv4)
aws s3 presign s3://my-bucket/report.pdf --expires-in 604800

# Static website hosting
aws s3 website s3://my-bucket --index-document index.html --error-document 404.html
```

### Parameters shared by `cp`, `mv`, `rm`, `sync`

| Parameter | Description | Req/Opt | Default | Example Values |
|---|---|---|---|---|
| `<source>` (positional) | Local path, `s3://` URI, or `-` for stdin. | **Required** | — | `./dist`, `s3://bucket/key`, `-` |
| `<destination>` (positional) | Local path, `s3://` URI, or `-` for stdout. Not used by `rm`. | **Required** (except `rm`) | — | `s3://bucket/prefix/`, `./out` |
| `--recursive` | Apply to all keys under the prefix / all files under the directory. Not accepted by `sync` (implicit). | Optional | Off | flag only |
| `--dryrun` | Print what *would* happen, change nothing. Use it before every `--delete`. | Optional | Off | flag only |
| `--exclude` | Glob to exclude. Repeatable; order-sensitive. | Optional | None | `"*.tmp"`, `".git/*"`, `"*"` |
| `--include` | Glob to re-include after an exclude. Repeatable; order-sensitive. | Optional | None | `"*.js"`, `"2026-*"` |
| `--acl` | Canned ACL on written objects. No-op on buckets with ACLs disabled (the modern default). | Optional | `private` | `private`, `public-read`, `bucket-owner-full-control` |
| `--storage-class` | Storage tier for new objects. | Optional | `STANDARD` | `STANDARD_IA`, `INTELLIGENT_TIERING`, `GLACIER`, `GLACIER_IR`, `DEEP_ARCHIVE`, `ONEZONE_IA` |
| `--sse` | Server-side encryption mode. | Optional | Bucket default | `AES256`, `aws:kms`, `aws:kms:dsse` |
| `--sse-kms-key-id` | CMK to use when `--sse aws:kms`. | Optional | AWS-managed `aws/s3` key | `arn:aws:kms:...:key/abcd-1234`, `alias/my-key` |
| `--sse-c` | Customer-provided encryption algorithm for the destination. | Optional | None | `AES256` |
| `--sse-c-key` | The customer key itself (base64 or raw per `--cli-binary-format`). | Optional | — | `$(openssl rand -base64 32)` |
| `--sse-c-copy-source` / `--sse-c-copy-source-key` | Same, for decrypting an SSE-C *source* object. | Optional | — | `AES256` |
| `--metadata` | User metadata map on new objects. | Optional | None | `'{"env":"prod","team":"data"}'` |
| `--metadata-directive` | Whether a copy reuses source metadata or replaces it. | Optional | `COPY` | `COPY`, `REPLACE` |
| `--content-type` | Explicit MIME type. Wrong types break browser rendering — set it for `.js`/`.css`/`.svg` if guessing fails. | Optional | Guessed from extension | `text/html`, `application/json` |
| `--cache-control` | `Cache-Control` header on new objects. | Optional | None | `max-age=31536000,public` |
| `--content-disposition` | `Content-Disposition` header. | Optional | None | `attachment; filename="report.pdf"` |
| `--content-encoding` | `Content-Encoding` header. | Optional | None | `gzip` |
| `--content-language` | `Content-Language` header. | Optional | None | `en-US` |
| `--expires` | Expiry timestamp header (ISO 8601). Unrelated to lifecycle deletion. | Optional | None | `2026-12-31T00:00:00Z` |
| `--website-redirect` | Redirect target for website-hosted objects. | Optional | None | `/new-path.html` |
| `--no-guess-mime-type` | Send `application/octet-stream` instead of guessing. | Optional | Off (guesses) | flag only |
| `--grants` | Explicit ACL grants. | Optional | None | `read=uri=http://acs.amazonaws.com/groups/global/AllUsers` |
| `--follow-symlinks` / `--no-follow-symlinks` | Whether to traverse symlinked files and dirs. | Optional | `--follow-symlinks` | flag only |
| `--source-region` | Region of the source bucket in cross-region copies. | Optional | `--region` value | `us-east-1` |
| `--expected-size` | Byte size hint when streaming from stdin — required above ~50 GB so chunk sizing is correct. | Optional | — | `53687091200` |
| `--request-payer` | Acknowledge requester-pays charges. | Optional | None | `requester` |
| `--checksum-algorithm` | Additional integrity checksum on upload. | Optional | Service default | `CRC32`, `CRC32C`, `SHA1`, `SHA256` |
| `--checksum-mode` | Validate checksums on download. | Optional | Off | `ENABLED` |
| `--ignore-glacier-warnings` | Silence warnings about skipped archived objects. | Optional | Off | flag only |
| `--force-glacier-transfer` | Attempt transfer of Glacier objects (fails unless already restored). | Optional | Off | flag only |
| `--only-show-errors` | Suppress progress and success lines; errors only. | Optional | Off | flag only |
| `--quiet` | Suppress per-file output entirely. | Optional | Off | flag only |
| `--no-progress` | Keep result lines, drop the progress bar. Good for CI logs. | Optional | Off | flag only |
| `--page-size` | Keys per `ListObjectsV2` call while walking a bucket. | Optional | `1000` | `100` |

### `aws s3 ls`

| Parameter | Description | Req/Opt | Default | Example Values |
|---|---|---|---|---|
| `<path>` (positional) | Bucket or prefix. Omit to list all buckets in the account. | Optional | — | `s3://my-bucket/logs/` |
| `--recursive` | Walk all keys beneath the prefix. | Optional | Off | flag only |
| `--human-readable` | Print sizes as KiB/MiB/GiB. | Optional | Off (bytes) | flag only |
| `--summarize` | Append total object count and total size. | Optional | Off | flag only |
| `--page-size` | Keys per API call. | Optional | `1000` | `100` |
| `--request-payer` | Acknowledge requester-pays charges. | Optional | None | `requester` |

> `ls` without `--recursive` shows `PRE prefix/` entries. Those are display conveniences — S3 has no real directories, only keys with slashes in them.

### `aws s3 mb`

| Parameter | Description | Req/Opt | Default | Example Values |
|---|---|---|---|---|
| `<path>` (positional) | Bucket URI. Names are globally unique across all of AWS. | **Required** | — | `s3://my-unique-bucket-2026` |
| `--region` | Region to create the bucket in. | Optional | Profile region | `eu-west-1` |

### `aws s3 rb`

| Parameter | Description | Req/Opt | Default | Example Values |
|---|---|---|---|---|
| `<path>` (positional) | Bucket URI to delete. | **Required** | — | `s3://my-old-bucket` |
| `--force` | Delete all objects first, then the bucket. Irreversible and unprompted. | Optional | Off (fails if non-empty) | flag only |

> `--force` does **not** remove non-current versions or delete markers. On a versioned bucket it will appear to succeed at emptying, then fail to delete the bucket. Use `aws s3api delete-objects` with a version listing, or a lifecycle rule.

### `aws s3 sync`

Syncs by comparing size and mtime — not content. Two files of identical size and timestamp are considered equal even if the bytes differ.

| Parameter | Description | Req/Opt | Default | Example Values |
|---|---|---|---|---|
| `<source>` / `<destination>` (positional) | Local dir or `s3://` prefix, in either direction, or S3→S3. | **Required** | — | `./dist`, `s3://bucket/site` |
| `--delete` | Remove destination files that no longer exist at the source. | Optional | Off | flag only |
| `--exact-timestamps` | On downloads, re-transfer unless timestamps match exactly. | Optional | Off | flag only |
| `--size-only` | Compare size alone, ignoring mtime. Useful when timestamps are unreliable (CI checkouts). | Optional | Off | flag only |
| *(all shared transfer flags above)* | `--exclude`, `--include`, `--dryrun`, `--acl`, `--sse`, `--storage-class`, etc. | Optional | — | — |

### `aws s3 presign`

| Parameter | Description | Req/Opt | Default | Example Values |
|---|---|---|---|---|
| `<path>` (positional) | Object URI to sign. | **Required** | — | `s3://my-bucket/report.pdf` |
| `--expires-in` | Lifetime in seconds. Max 604800 (7 days) for SigV4. | Optional | `3600` | `300`, `604800` |

> The URL can never outlive the credentials that signed it. Sign with a 1-hour SSO session and your "7-day" link dies in an hour — use a long-lived IAM user or an instance role for durable links.

### `aws s3 website`

| Parameter | Description | Req/Opt | Default | Example Values |
|---|---|---|---|---|
| `<path>` (positional) | Bucket URI to configure for static hosting. | **Required** | — | `s3://my-bucket` |
| `--index-document` | Suffix served for directory-style requests. | Optional | None | `index.html` |
| `--error-document` | Key returned on 4xx errors. | Optional | None | `error.html`, `404.html` |

> This only flips the website flag. You still need a public bucket policy and Block Public Access disabled — and for anything real, CloudFront in front for TLS.

---

## Quick Reference

| Task | Command |
|---|---|
| Who am I? | `aws sts get-caller-identity` |
| Which profiles exist? | `aws configure list-profiles` |
| Where is this setting from? | `aws configure list` |
| Refresh expired SSO login | `aws sso login --profile <name>` |
| Total size of a prefix | `aws s3 ls s3://bucket/prefix/ --recursive --human-readable --summarize` |
| Deploy a static site | `aws s3 sync ./dist s3://bucket --delete` |
| Temporary share link | `aws s3 presign s3://bucket/key --expires-in 3600` |
| Credentials for another tool | `eval "$(aws configure export-credentials --profile p --format env)"` |
| See the raw HTTP request | append `--debug` |

**Config file locations:** `~/.aws/credentials`, `~/.aws/config`, `~/.aws/sso/cache/`, `~/.aws/cli/cache/`
**Key env vars:** `AWS_PROFILE`, `AWS_REGION`, `AWS_DEFAULT_REGION`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_SESSION_TOKEN`, `AWS_CONFIG_FILE`, `AWS_SHARED_CREDENTIALS_FILE`, `AWS_PAGER`
