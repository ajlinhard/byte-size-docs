# S3 IAM Permissions Cheatsheet
AWS S3 has numerous IAM actions that you can use to grant granular permissions. Here are the main categories:

## Bucket-Level Actions

**Bucket Management:**
- `s3:CreateBucket` - Create new buckets
- `s3:DeleteBucket` - Delete buckets
- `s3:ListBucket` - List objects in a bucket
- `s3:ListBucketVersions` - List object versions
- `s3:ListBucketMultipartUploads` - List multipart uploads

**Bucket Configuration:**
- `s3:PutBucketPolicy` / `s3:GetBucketPolicy` / `s3:DeleteBucketPolicy`
- `s3:PutBucketAcl` / `s3:GetBucketAcl`
- `s3:PutBucketVersioning` / `s3:GetBucketVersioning`
- `s3:PutBucketLogging` / `s3:GetBucketLogging`
- `s3:PutEncryptionConfiguration` / `s3:GetEncryptionConfiguration`
- `s3:PutBucketCORS` / `s3:GetBucketCORS`
- `s3:PutLifecycleConfiguration` / `s3:GetLifecycleConfiguration`
- `s3:PutReplicationConfiguration` / `s3:GetReplicationConfiguration`

## Object-Level Actions

**Basic Object Operations:**
- `s3:GetObject` - Read/download objects
- `s3:PutObject` - Upload/write objects
- `s3:DeleteObject` - Delete objects
- `s3:GetObjectVersion` / `s3:DeleteObjectVersion`

**Object Metadata:**
- `s3:GetObjectAcl` / `s3:PutObjectAcl`
- `s3:GetObjectAttributes`
- `s3:GetObjectTagging` / `s3:PutObjectTagging` / `s3:DeleteObjectTagging`

**Advanced Object Operations:**
- `s3:RestoreObject` - Restore from Glacier
- `s3:AbortMultipartUpload`
- `s3:ListMultipartUploadParts`

## Common Wildcard Actions

- `s3:*` - All S3 actions
- `s3:Get*` - All read operations
- `s3:Put*` - All write operations
- `s3:List*` - All list operations

## Typical Use Cases

**Read-only access:**
```json
"Action": ["s3:GetObject", "s3:ListBucket"]
```

**Full bucket access:**
```json
"Action": "s3:*"
```

**Upload-only:**
```json
"Action": "s3:PutObject"
```

Would you like me to provide an example IAM policy for a specific use case?
