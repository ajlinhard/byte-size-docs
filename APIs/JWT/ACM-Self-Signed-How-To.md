# ACM Self-Signed How To
**Short version: use ACM (Option A) unless something specifically forces you to IAM.** IAM server certificates are the pre-2016 mechanism that ACM replaced; AWS keeps them around mainly for edge cases.

## Option A — ACM import

**Pros**
- The intended path today. ALB listeners, CloudFront, API Gateway, and AppSync all consume ACM ARNs natively.
- Free. Imported certificates cost nothing (only ACM Private CA has a charge).
- Visible and manageable in the console, with proper tagging and resource-level IAM policies (`acm:ImportCertificate` on a specific ARN, etc.).
- Expiry monitoring for free — ACM emits EventBridge events and a `DaysToExpiry` metric, and AWS Config has a managed rule for it. Handy since your cert dies in 365 days.
- Re-importing a renewal against the same ARN keeps the ARN stable, so the ALB listener needs no change.

**Cons**
- **Regional.** The certificate must live in the same region as the ALB. Multi-region means importing once per region, each with its own ARN.
- No auto-renewal. ACM only renews certificates it issued; imported ones are your problem. (Irrelevant for a throwaway self-signed cert, but a trap if this pattern ever graduates to production.)
- Quotas are per-region — the default is on the order of a hundred imported certs, plus a cap on re-imports per year. Fine for you, occasionally annoying in busy shared accounts.

## Option B — IAM server certificate

**Pros**
- **Global.** One upload, usable by an ALB in any region of that account. Genuinely convenient for multi-region setups.
- Works in partitions/regions where ACM isn't available or isn't wired up — the historical reason this API still exists.
- You name it yourself (`entra-demo-basic-alb-selfsigned`), so the ARN is human-readable rather than a UUID.
- Still supported by ELB/ALB listeners; nothing is deprecated out from under you.

**Cons**
- No console UI. Everything is CLI/API (`aws iam list-server-certificates`), which makes it easy for a teammate to not realize the cert exists.
- No expiry notifications, no metrics, no Config rule. It quietly expires and your listener quietly starts failing handshakes.
- Low quota — 20 server certificates per account by default, and it's account-wide rather than per-region.
- IAM permissions are coarser, and deletion requires detaching from the listener first or you get a `DeleteConflict`.
- Effectively legacy. Newer integrations (ACM-only services, cert automation tooling) assume ACM ARNs.

## Two things to fix in your commands

**The profile is inconsistent.** Option B has `--profile va-vdi`; Option A doesn't. Without it, the ACM import goes to whatever your default profile points at — likely a different account entirely. Add `--profile va-vdi` to the ACM call.

**ACM needs the right region.** Add `--region <alb-region>` explicitly rather than trusting the profile default. Importing to us-east-1 and then trying to attach to a us-west-2 ALB produces a confusing "certificate not found" error.

The `fileb://` vs `file://` difference is fine as written — that's what each service's docs use, and both handle PEM correctly.

---
## Option A in Action
ACM doesn't have a name field — that's the one real ergonomic loss versus IAM. Certificates are identified solely by their ARN, and the UUID is generated for you. The convention is to attach a `Name` tag, which the ACM console surfaces as a Name column and which most tooling picks up.

## The command

```bash
aws acm import-certificate \
  --profile va-vdi \
  --region us-east-1 \
  --certificate fileb://cert.pem \
  --private-key fileb://key.pem \
  --tags Key=Name,Value=entra-demo-basic-alb-selfsigned
```

Swap `us-east-1` for whatever region your ALB lives in — the certificate has to be in the same one.

PowerShell equivalent (backticks instead of backslashes):

```powershell
aws acm import-certificate `
  --profile va-vdi `
  --region us-east-1 `
  --certificate fileb://cert.pem `
  --private-key fileb://key.pem `
  --tags Key=Name,Value=entra-demo-basic-alb-selfsigned
```

## Capturing the ARN

The import returns only the ARN, so grab it directly rather than copy-pasting:

```bash
CERT_ARN=$(aws acm import-certificate \
  --profile va-vdi --region us-east-1 \
  --certificate fileb://cert.pem --private-key fileb://key.pem \
  --tags Key=Name,Value=entra-demo-basic-alb-selfsigned \
  --query CertificateArn --output text)

echo $CERT_ARN
```
**Windows**
```powershell
$CertArn = aws acm import-certificate `
  --profile va-vdi `
  --region us-east-1 `
  --certificate fileb://cert.pem `
  --private-key fileb://key.pem `
  --tags Key=Name,Value=entra-demo-basic-alb-selfsigned `
  --query CertificateArn --output text

$CertArn
```


Then feed `$CERT_ARN` straight into your `create-listener` call.

## Two things worth knowing

**Tags apply on initial import only.** If you later re-import to replace an expiring cert (by passing `--certificate-arn`), the `--tags` argument is rejected. Use `aws acm add-tags-to-certificate` separately in that case.

**Finding it again by tag**, since you can't look it up by name:

```bash
aws acm list-certificates --profile va-vdi --region us-east-1 \
  --query "CertificateSummaryList[].CertificateArn" --output text
```

`list-certificates` doesn't return tags, so if you have several certs you'll need `aws acm list-tags-for-certificate --certificate-arn <arn>` to identify the right one — or just filter on the domain name, which is where `basic-alb.example.com` from your `-subj` ends up. That placeholder CN does earn its keep here as a label, even though it means nothing cryptographically.

Adding a couple more tags at import time (`Key=Environment,Value=demo`, `Key=Temporary,Value=true`) costs nothing and makes cleanup easier later.
