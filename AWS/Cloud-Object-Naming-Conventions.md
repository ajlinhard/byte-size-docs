
## Cloud Object Naming Convention

**Functional Naming**
- `{environment}-{system/application}-{purpose}-{resource-type}`
- Example: `prod-dashboard-eb-frontend-lb`, `dev-dashboard-data-processing-lambda`

**Team/Owner Based**
- `{team}-{system/application}-{environment}-{resource}`
- Example: `platform-auth-prod-cluster`, `data-ml-staging-bucket`

### **Standardized Prefixes/Suffixes**
- Consistent resource type indicators: `-sg` for security groups, `-role` for IAM roles, `-lb` for load balancers
- Environment suffixes: `-prod`, `-dev`, `-staging`

### For Adhoc / Temp Resources
`{purpose}-{user name}-{YYYYMMDD}`

## **Tagging Strategy**
- Use consistent tags across all related resources:
  - `Application`: `ecommerce-api`
  - `Environment`: `production`
  - `Sub-system`: `dashboard-request`
  - `Owner`: `platform-team`
- Tag-based automation for grouping and management

**Resource References**
- Infrastructure as Code (Terraform, CloudFormation) naturally creates these links
- Use outputs/exports to reference resources between stacks
- Resource ARNs in descriptions or tags

**Documentation and Metadata**
- Maintain resource inventories with relationship mappings
- Use cloud provider resource groups or resource tags for logical grouping
- Service catalogs for standardized deployments

## Best Practices

- Keep names under cloud provider limits (typically 64-255 characters)
- Use lowercase with hyphens rather than underscores for better compatibility
- Avoid special characters that might cause issues in different contexts
- Include versioning where appropriate (`-v1`, `-v2`)
- Use abbreviations consistently (`db` not `database` sometimes and `db` others)
