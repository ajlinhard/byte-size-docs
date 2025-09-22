
# Cloud Object Naming Convention

## **Functional Naming**
- `{environment}-{system/application}-{purpose}-{resource-type}`
- Example: `prod-dashboard-eb-frontend-lb`, `dev-dashboard-data-processing-lambda`

### For Adhoc / Temp Resources
`{purpose}-{user name}-{YYYYMMDD}`

## **Tagging Strategy**
- Use consistent tags across all related resources:
  - `Application`: `ecommerce-api`
  - `Environment`: `production`
  - `Sub-system`: `dashboard-request`
  - `Owner`: `platform-team`
- Tag-based automation for grouping and management

### Environment
|Naming String|Object Name|Description|
|`prod`| Production | for objects in the production environment.|
|`dev`| Development | for objects in the production environment.|

### System/Applications
|Naming String|Object Name|Description|
|`dash`| Dashboard | The visual dashboard for the VA to monitor metrics for the AICES program|

## Best Practices

- Keep names under cloud provider limits (typically 64-255 characters)
- Use lowercase with hyphens rather than underscores for better compatibility
- Avoid special characters that might cause issues in different contexts
- Include versioning where appropriate (`-v1`, `-v2`)
- Use abbreviations consistently (`db` not `database` sometimes and `db` others)

# AWS Resource Abbreviations Reference

This document provides standardized abbreviations for common AWS resources and services.

## Compute Resources

| Naming String | Object Name | Description |
|---------------|-------------|-------------|
| `-ec2` | EC2 Instance | Elastic Compute Cloud virtual server |
| `-asg` | Auto Scaling Group | Automatically scales EC2 instances |
| `-lc` | Launch Configuration | Template for Auto Scaling Group instances |
| `-lt` | Launch Template | Enhanced template for EC2 instances |
| `-lambda` | Lambda Function | Serverless compute service |
| `-ecs` | ECS Service | Elastic Container Service |
| `-task` | ECS Task Definition | Container task configuration |
| `-cluster` | ECS/EKS Cluster | Container orchestration cluster |
| `-eks` | EKS Cluster | Elastic Kubernetes Service |
| `-batch` | Batch Job | AWS Batch compute job |

## Storage Resources

| Naming String | Object Name | Description |
|---------------|-------------|-------------|
| `-s3` | S3 Bucket | Simple Storage Service bucket |
| `-ebs` | EBS Volume | Elastic Block Store volume |
| `-efs` | EFS File System | Elastic File System |
| `-fsx` | FSx File System | High-performance file system |
| `-glacier` | Glacier Vault | Long-term archival storage |
| `-snapshot` | EBS Snapshot | Point-in-time volume backup |
| `-backup` | Backup Vault | AWS Backup service vault |

## Networking Resources

| Naming String | Object Name | Description |
|---------------|-------------|-------------|
| `-vpc` | VPC | Virtual Private Cloud |
| `-subnet` | Subnet | VPC network subdivision |
| `-igw` | Internet Gateway | VPC internet access |
| `-natgw` | NAT Gateway | Network Address Translation |
| `-nat` | NAT Instance | EC2-based NAT solution |
| `-sg` | Security Group | Instance-level firewall |
| `-nacl` | Network ACL | Subnet-level access control |
| `-rt` | Route Table | Network routing rules |
| `-eip` | Elastic IP | Static public IP address |
| `-eni` | Elastic Network Interface | Virtual network interface |
| `-vpce` | VPC Endpoint | Private service connection |
| `-tgw` | Transit Gateway | Multi-VPC connectivity hub |
| `-cgw` | Customer Gateway | VPN customer endpoint |
| `-vgw` | Virtual Private Gateway | VPN AWS endpoint |
| `-dx` | Direct Connect | Dedicated network connection |
| `-peering` | VPC Peering Connection | Direct VPC-to-VPC connection |

## Load Balancing

| Naming String | Object Name | Description |
|---------------|-------------|-------------|
| `-alb` | Application Load Balancer | Layer 7 HTTP/HTTPS load balancer |
| `-nlb` | Network Load Balancer | Layer 4 TCP/UDP load balancer |
| `-clb` | Classic Load Balancer | Legacy load balancer |
| `-tg` | Target Group | Load balancer target collection |
| `-listener` | Listener | Load balancer traffic routing rule |

## Database Resources

| Naming String | Object Name | Description |
|---------------|-------------|-------------|
| `-rds` | RDS Instance | Relational Database Service |
| `-aurora` | Aurora Cluster | Amazon Aurora database |
| `-dynamodb` | DynamoDB Table | NoSQL database table |
| `-docdb` | DocumentDB Cluster | MongoDB-compatible database |
| `-neptune` | Neptune Cluster | Graph database |
| `-redshift` | Redshift Cluster | Data warehouse |
| `-elasticache` | ElastiCache Cluster | In-memory caching |
| `-redis` | ElastiCache Redis | Redis cache cluster |
| `-memcached` | ElastiCache Memcached | Memcached cache cluster |
| `-dbsubnet` | DB Subnet Group | Database subnet collection |
| `-dbpg` | DB Parameter Group | Database configuration |
| `-dbog` | DB Option Group | Database feature options |

## Identity and Access Management

| Naming String | Object Name | Description |
|---------------|-------------|-------------|
| `-role` | IAM Role | AWS service or cross-account role |
| `-policy` | IAM Policy | Permissions policy document |
| `-user` | IAM User | Individual user account |
| `-group` | IAM Group | User collection with shared permissions |
| `-instanceprofile` | Instance Profile | EC2 role attachment |
| `-saml` | SAML Provider | SAML identity provider |
| `-oidc` | OIDC Provider | OpenID Connect identity provider |

## Monitoring and Logging

| Naming String | Object Name | Description |
|---------------|-------------|-------------|
| `-cw` | CloudWatch | Monitoring service |
| `-cwlogs` | CloudWatch Logs | Log management service |
| `-loggroup` | Log Group | CloudWatch log collection |
| `-logstream` | Log Stream | Individual log sequence |
| `-alarm` | CloudWatch Alarm | Metric-based alert |
| `-dashboard` | CloudWatch Dashboard | Metrics visualization |
| `-metric` | Custom Metric | Application-specific metric |
| `-trail` | CloudTrail | API activity logging |
| `-xray` | X-Ray | Distributed tracing service |

## DNS and Content Delivery

| Naming String | Object Name | Description |
|---------------|-------------|-------------|
| `-r53` | Route 53 Hosted Zone | DNS management service |
| `-record` | DNS Record | Domain name record |
| `-cf` | CloudFront Distribution | Content delivery network |
| `-oai` | Origin Access Identity | CloudFront S3 access control |

## Container Services

| Naming String | Object Name | Description |
|---------------|-------------|-------------|
| `-ecr` | ECR Repository | Elastic Container Registry |
| `-ecs-service` | ECS Service | Container service definition |
| `-ecs-cluster` | ECS Cluster | Container orchestration cluster |
| `-taskdef` | Task Definition | ECS container specification |
| `-fargate` | Fargate Service | Serverless container service |

## Messaging and Integration

| Naming String | Object Name | Description |
|---------------|-------------|-------------|
| `-sqs` | SQS Queue | Simple Queue Service |
| `-sns` | SNS Topic | Simple Notification Service |
| `-kinesis` | Kinesis Stream | Real-time data streaming |
| `-firehose` | Kinesis Firehose | Data delivery stream |
| `-eventbridge` | EventBridge Rule | Event routing service |
| `-stepfunctions` | Step Functions | Workflow orchestration |

## API and Application Services

| Naming String | Object Name | Description |
|---------------|-------------|-------------|
| `-apigw` | API Gateway | REST API management |
| `-apikey` | API Key | API access credential |
| `-stage` | API Gateway Stage | API deployment stage |
| `-resource` | API Resource | API endpoint path |
| `-method` | API Method | HTTP method configuration |
| `-authorizer` | API Authorizer | API authentication function |

## Security Services

| Naming String | Object Name | Description |
|---------------|-------------|-------------|
| `-kms` | KMS Key | Key Management Service encryption key |
| `-secret` | Secrets Manager Secret | Stored sensitive data |
| `-ssm` | Systems Manager Parameter | Configuration parameter |
| `-acm` | ACM Certificate | SSL/TLS certificate |
| `-waf` | WAF Web ACL | Web Application Firewall |
| `-shield` | Shield Protection | DDoS protection |
| `-guardduty` | GuardDuty Detector | Threat detection service |
| `-inspector` | Inspector Assessment | Security assessment |
| `-macie` | Macie | Data security and privacy |

## Analytics and Big Data

| Naming String | Object Name | Description |
|---------------|-------------|-------------|
| `-emr` | EMR Cluster | Elastic MapReduce cluster |
| `-glue` | Glue Job | ETL service job |
| `-athena` | Athena Workgroup | Query service workgroup |
| `-quicksight` | QuickSight Dashboard | Business intelligence |
| `-elasticsearch` | Elasticsearch Domain | Search and analytics |

## DevOps and CI/CD

| Naming String | Object Name | Description |
|---------------|-------------|-------------|
| `-codebuild` | CodeBuild Project | Build service project |
| `-codedeploy` | CodeDeploy Application | Deployment service |
| `-codepipeline` | CodePipeline | CI/CD pipeline |
| `-codecommit` | CodeCommit Repository | Git repository |
| `-artifact` | S3 Artifact Store | Pipeline artifact storage |
| `-cloudformation` | CloudFormation Stack | Infrastructure as code |
| `-sam` | SAM Application | Serverless application model |

## Machine Learning

| Naming String | Object Name | Description |
|---------------|-------------|-------------|
| `-sagemaker` | SageMaker | Machine learning platform |
| `-model` | SageMaker Model | ML model deployment |
| `-endpoint` | SageMaker Endpoint | ML inference endpoint |
| `-notebook` | SageMaker Notebook | Jupyter notebook instance |


## Usage Guidelines

1. Use lowercase letters and hyphens for consistency
2. Include environment prefix when applicable
3. Use descriptive service/tier names (web, api, db, cache)
4. Keep resource names under AWS limits (typically 63-255 characters)
5. Be consistent across your AWS organization
6. Consider using AWS resource tags for additional metadata
7. Follow AWS naming best practices for each service type
