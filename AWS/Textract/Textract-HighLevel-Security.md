# Textract High Level Security
AWS Textract does have several security considerations when running it within a private VPC:

## Key Security Considerations

**VPC Endpoints (AWS PrivateLink)**
- Textract supports VPC endpoints, allowing you to keep traffic between your VPC and Textract entirely within the AWS network
- Without VPC endpoints, Textract API calls traverse the public internet (though still encrypted)
- VPC endpoints help meet compliance requirements for keeping data within private networks

**Data in Transit**
- All API calls to Textract are encrypted using TLS
- However, using VPC endpoints adds an extra layer of network isolation

**S3 Integration**
- Textract often reads documents from and writes results to S3
- You should use S3 VPC endpoints to keep this traffic private as well
- Ensure S3 buckets have proper access policies and aren't publicly accessible

**IAM Permissions**
- Use least-privilege IAM roles/policies
- Consider using VPC endpoint policies to restrict which actions can be performed through the endpoint
- Ensure only authorized services/users can invoke Textract

**Data Residency**
- Textract processes data in AWS data centers, so understand which regions you're using
- Documents are not retained by AWS after processing (per AWS's service terms)

**Network Controls**
- Use security groups and NACLs to control which resources can access the VPC endpoint
- Consider using AWS CloudTrail to log all Textract API calls for audit purposes

## Recommended Setup
For maximum security in a private VPC:
1. Create VPC endpoints for both Textract and S3
2. Configure security groups to allow only necessary traffic
3. Use IAM roles (not long-lived credentials) for authentication
4. Enable CloudTrail logging
5. Encrypt data at rest in S3 using KMS

Would you like guidance on setting up VPC endpoints for Textract specifically?
