#Same Region Replication
Here's a step-by-step guide to set up Same-Region Replication (SRR) between two S3 buckets:

Jump to: [SSR verse Cross Region Replication (CRR) and DataSync](#SSR-verse-Cross-Region-Replication-(CRR)-and-DataSync)

## Prerequisites

1. **Two S3 buckets in the same AWS region**
2. **Versioning enabled on both buckets** (required for replication)
3. **Appropriate IAM permissions**

## Step 1: Enable Versioning on Both Buckets

### Via AWS Console:
1. Go to S3 Console
2. Select your source bucket → **Properties** tab
3. Find **Bucket Versioning** → Click **Edit**
4. Select **Enable** → **Save changes**
5. Repeat for destination bucket

### Via AWS CLI:
```bash
# Enable versioning on source bucket
aws s3api put-bucket-versioning --bucket your-source-bucket \
  --versioning-configuration Status=Enabled

# Enable versioning on destination bucket  
aws s3api put-bucket-versioning --bucket your-destination-bucket \
  --versioning-configuration Status=Enabled
```

## Step 2: Create IAM Role for Replication

### Trust Policy (srr-trust-policy.json):
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "s3.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
```

### Permission Policy (srr-policy.json):
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetReplicationConfiguration",
        "s3:ListBucket",
        "s3:GetObjectVersion",
        "s3:GetObject"
      ],
      "Resource": [
        "arn:aws:s3:::your-source-bucket",
        "arn:aws:s3:::your-source-bucket/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:ReplicateObject",
        "s3:ReplicateDelete",
        "s3:ReplicateTags"
      ],
      "Resource": "arn:aws:s3:::your-destination-bucket/*"
    }
  ]
}
```

### Create the IAM role:
```bash
# Create role
aws iam create-role --role-name SRRReplicationRole \
  --assume-role-policy-document file://srr-trust-policy.json

# Attach policy
aws iam put-role-policy --role-name SRRReplicationRole \
  --policy-name SRRPolicy --policy-document file://srr-policy.json
```

## Step 3: Configure SRR via AWS Console

1. **Navigate to S3 Console**
2. **Select your source bucket**
3. **Go to Management tab**
4. **Click "Create replication rule"**

### Configure the replication rule:
- **Rule name**: Enter a descriptive name (e.g., "SRR-to-backup-bucket")
- **Status**: Enabled
- **Priority**: 1 (if you have multiple rules)
- **Rule scope**: 
  - Choose "Apply to all objects in the bucket" OR
  - "Limit the scope" and add filters (prefix/tags)

### Destination settings:
- **Specify a bucket in this account**: Select your destination bucket
- **Destination storage class**: Choose storage class (S3 Standard recommended for SRR)
- **IAM Role**: Select the role you created

### Additional options (optional):
- **Replication Time Control (RTC)**: Enable for 15-minute SLA
- **Replication metrics**: Enable for monitoring
- **Delete marker replication**: Enable to keep buckets in sync
- **Replica modification sync**: Enable for bi-directional sync

5. **Click "Save"**

## Step 4: Configure SRR via AWS CLI (Alternative)

### Create replication configuration file (srr-config.json):
```json
{
  "Role": "arn:aws:iam::YOUR-ACCOUNT-ID:role/SRRReplicationRole",
  "Rules": [
    {
      "ID": "SRR-Rule-1",
      "Status": "Enabled",
      "Priority": 1,
      "Filter": {},
      "Destination": {
        "Bucket": "arn:aws:s3:::your-destination-bucket",
        "StorageClass": "STANDARD"
      }
    }
  ]
}
```

### Apply the configuration:
```bash
aws s3api put-bucket-replication --bucket your-source-bucket \
  --replication-configuration file://srr-config.json
```

## Step 5: Test the Replication

1. **Upload a test file** to your source bucket:
```bash
echo "Test SRR" > test-srr.txt
aws s3 cp test-srr.txt s3://your-source-bucket/
```

2. **Check the destination bucket** (may take a few minutes):
```bash
aws s3 ls s3://your-destination-bucket/
```

3. **Verify replication status**:
   - In AWS Console, go to source bucket
   - Find your uploaded object
   - Check the **Properties** tab for replication status

## Step 6: Monitor Replication

### Enable CloudWatch metrics (optional):
- Go to source bucket → **Metrics** tab
- Enable **Replication metrics**
- Monitor replication progress in CloudWatch

### Check replication configuration:
```bash
aws s3api get-bucket-replication --bucket your-source-bucket
```

## Important Notes

- **SRR only replicates new objects** uploaded after replication is configured
- **No data transfer costs** for same-region replication
- **Storage costs apply** for both source and destination buckets  
- **Request costs apply** for PUT operations during replication
- For existing objects, use **S3 Batch Replication** as a separate process

Your SRR setup is now complete! New objects uploaded to your source bucket will automatically replicate to your destination bucket within minutes.

---
# SSR verse Cross Region Replication (CRR) and DataSync

The cost comparison between S3 Replication (SRR/CRR) and DataSync depends heavily on your specific use case, but here's a detailed breakdown:

## Cost Components Comparison

### DataSync Costs:
- $0.0125 per GB for Basic mode transfers  
- $0.015 per GB for Enhanced mode transfers plus $0.55 per task execution
- Plus standard S3 request charges (LIST, HEAD, GET, PUT operations)
- No upfront costs and no minimum charges

### S3 Replication Costs:

**Same-Region Replication (SRR):**
- Transferring data between S3 buckets in the same region is free
- Storage costs for both source and destination buckets
- PUT request costs: $0.005 per 1,000 requests for S3 Standard
- No data transfer charges

**Cross-Region Replication (CRR):**  
- Storage costs for both buckets
- Data transfer charges: $0.01-$0.02 per GB for most US/Canada/Europe regions
- Higher data transfer costs for Asia/Middle East: $0.085-$0.14 per GB
- PUT request costs
- Optional: S3 RTC: additional $0.015 per GB for 15-minute replication guarantee

## Cost Analysis Example

For a **100 GB daily replication** scenario:

### DataSync (Enhanced mode):
$0.015 per GB × 100 GB + $0.55 per execution = $2.05 per day
**Monthly cost: ~$61.50**

### S3 Same-Region Replication:
- Data transfer: $0 (free within same region)
- Storage: Double storage costs (source + destination)
- Requests: Minimal PUT costs
**Monthly cost: Primarily just doubled storage costs**

### S3 Cross-Region Replication:
Example: 100 GB CRR from N. Virginia to N. California = $2.00 data transfer + storage + requests = ~$6.60 total
**Monthly cost: ~$198**

## When Each is More Cost-Effective

**S3 SRR is cheapest when:**
- Both buckets in same region
- Continuous replication needs
- No data transfer charges apply

**S3 CRR is better when:**
- Need real-time replication across regions
- Lower frequency of data changes
- Can accept the ~$0.02/GB transfer cost

**DataSync is better when:**  
- Need advanced features (filtering, verification, scheduling)
- Infrequent bulk transfers
- Transferring more than 25 million objects (DataSync limit between AWS services)
- Need to preserve complex metadata

## Bottom Line

For **frequent, real-time syncing**:
- **SRR is significantly cheaper** than DataSync  
- **CRR can be cheaper** than DataSync depending on transfer frequency and regions

For **scheduled bulk transfers** with advanced features:
- **DataSync may be more cost-effective** despite higher per-GB costs due to its verification, filtering, and automation capabilities

The key factor is **transfer frequency** - S3 replication charges are ongoing for storage but minimal for actual replication, while DataSync charges per transfer operation.
