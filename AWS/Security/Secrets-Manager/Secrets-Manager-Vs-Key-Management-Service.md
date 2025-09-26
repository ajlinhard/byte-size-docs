# Secret Manager Vs. Key Management Service (KMS)

AWS Secrets Manager and AWS Key Management Service (KMS) serve different but complementary purposes in AWS security:

### Documentation:
- [AWS KMS Key Rotation](https://docs.aws.amazon.com/kms/latest/developerguide/rotate-keys.html)

**AWS Key Management Service (KMS):**
- **Purpose**: Creates and manages cryptographic keys used for encryption/decryption
- **What it stores**: Encryption keys themselves (symmetric and asymmetric keys)
- **Primary use cases**:
  - Encrypting data at rest (S3 buckets, EBS volumes, RDS databases)
  - Encrypting data in transit
  - Digital signing and verification
  - Envelope encryption for large datasets
  - Integration with other AWS services for automatic encryption

**AWS Secrets Manager:**
- **Purpose**: Stores, retrieves, and automatically rotates sensitive information
- **What it stores**: Complete secrets like database passwords, API keys, OAuth tokens, license keys
- **Primary use cases**:
  - Database credential management with automatic rotation
  - API key storage and retrieval
  - Third-party service credentials
  - Application configuration secrets
  - Centralized secret distribution to applications

**Key Differences:**

1. **Scope**: KMS handles the keys that encrypt/decrypt data, while Secrets Manager handles the actual sensitive data that needs protection

2. **Rotation**: Secrets Manager offers automatic rotation of stored secrets; KMS keys are typically long-lived and rotated less frequently

3. **Integration**: KMS integrates deeply with AWS services for transparent encryption; Secrets Manager integrates with applications that need to retrieve credentials

4. **Use together**: They often work in tandem - Secrets Manager uses KMS keys to encrypt the secrets it stores, providing layered security

Think of KMS as the "locksmith" that creates and manages the locks (encryption keys), while Secrets Manager is the "safe" that stores your valuables (credentials) using those locks for protection.
