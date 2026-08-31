# Lambda Code Deploy Triggers
Problem: With Lambda if the underlying code changes the cloudformation template has not changed, so the new code is not triggers. 
Here's the root cause and the fixes.
**Why it doesn't notice:** CloudFormation only pushes a new `AWS::Lambda::Function` deployment when it detects a *diff in the template's `Code` property values* (S3 bucket, S3 key, or object version). It doesn't inspect the actual bytes at that S3 location — it just compares the template string. So if you overwrite the zip at the same S3 key, CFN sees `ChatLambdaCodeS3Key: chat-lambda.zip` before and after, concludes nothing changed, and skips updating the function entirely.

## Fix options, from most to least "proper"
To solve this here are some common methods to trigger a redployment of the code over manual execution. Some include good rollback mechanics as well.

**1. Content-hash the S3 key (recommended)**

Make the key itself change whenever the code changes, by embedding a hash of the zip in the filename:

```bash
HASH=$(sha256sum build/chat-lambda.zip | cut -d' ' -f1)
KEY="lambda-code/chat-lambda-${HASH}.zip"
aws s3 cp build/chat-lambda.zip "s3://your-bucket/${KEY}"

aws cloudformation deploy \
  --template-file infra/template-basic-alb.yaml \
  --stack-name your-stack \
  --parameter-overrides ChatLambdaCodeS3Key="${KEY}" \
  --capabilities CAPABILITY_IAM
```

Since `ChatLambdaCodeS3Key` is already a parameter in your template, this slots in directly. Every real code change produces a new hash → new key → CFN sees a genuine property diff → it redeploys. No-op deploys don't touch the function at all, which is exactly what you want. This is what SAM (`sam deploy`) and CDK do under the hood automatically.

**2. Use `S3ObjectVersion` instead of changing the key**

If your bucket has versioning enabled, you can keep the key constant and instead pass the new object's version ID:

```yaml
Code:
  S3Bucket: !Ref ChatLambdaCodeS3Bucket
  S3Key: !Ref ChatLambdaCodeS3Key
  S3ObjectVersion: !Ref ChatLambdaCodeS3ObjectVersion
```

```bash
VERSION_ID=$(aws s3api put-object --bucket your-bucket --key chat-lambda.zip \
  --body build/chat-lambda.zip --query VersionId --output text)

aws cloudformation deploy ... \
  --parameter-overrides ChatLambdaCodeS3ObjectVersion="${VERSION_ID}"
```

Same underlying idea — a value in the template actually changes — just without dirtying up your bucket with many differently-named objects.

**3. Bypass CFN for the code push (fast, but creates drift)**

For quick hotfixes you can do `aws lambda update-function-code` directly and skip CFN entirely. This works and is common for hotfixes, but it desyncs the stack from reality: `aws cloudformation detect-stack-drift` will flag `ChatLambdaFunction`, and if you ever change the `ChatLambdaCodeS3Key` parameter later without also bumping the actual deployed code, you can end up confused about which version is live. Treat this as a stopgap, not a workflow.

**4. Inline `ZipFile` (only for tiny functions)**

If the Lambda is small enough to use `Code.ZipFile` inline in the template, any code change is literally a template diff, so this problem doesn't occur at all. Not viable past ~4KB of code, so probably not useful for a real Chat Lambda, but worth knowing.

---

For a CI/CD pipeline, option 1 (content-hashed key) is the standard, durable fix — it makes deploys idempotent (no-op when nothing changed, guaranteed update when something did) without any manual bookkeeping.

---
## PowerShell conversion

```powershell
$Hash = (Get-FileHash -Path "build/chat-lambda.zip" -Algorithm SHA256).Hash.ToLower()
$Key = "lambda-code/chat-lambda-$Hash.zip"

aws s3 cp build/chat-lambda.zip "s3://your-bucket/$Key"

aws cloudformation deploy `
  --template-file infra/template-basic-alb.yaml `
  --stack-name your-stack `
  --parameter-overrides "ChatLambdaCodeS3Key=$Key" `
  --capabilities CAPABILITY_IAM
```

Notes on the conversion:
- `sha256sum` → `Get-FileHash -Algorithm SHA256`. PowerShell returns the hash in **uppercase** hex by default, so I added `.ToLower()` to match sha256sum's output convention (not functionally required, just keeps naming consistent with what you had).
- Backtick `` ` `` is PowerShell's line-continuation character, equivalent to bash's `\`.
- String interpolation uses `$Variable` directly inside double-quoted strings — no `${}` needed unless there's ambiguity with surrounding text (e.g., `"${Var}zip"` vs `"$Varzip"`), though `${Hash}` also works if you prefer the explicit form.
- If you're on PowerShell 5.1 (Windows PowerShell, not Core), `aws` CLI calls work the same way since it's just invoking the executable.

---
