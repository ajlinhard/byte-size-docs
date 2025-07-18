
# Infrastructure as Code
Commonly for building out systems in the old days you were limited to building out bash setup scripts, but the cloud take over has changed the game. Now the hardware partitioning and setup by the cloud behind the scenes can be done with yaml/json files. The console isn't the only way to build out the cloud. From the IaC files with other tools like AWS Cloudformation, Terraform, Github Actions, etc. you can build out your system or sell deployments of your system.

### Documentation:
[How Cloudformation Works](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cloudformation-overview.html)

# The Basics
## The Code (yaml or json)
**The CloudFormation template I provided can be stored in either of these formats:

1. YAML format (.yaml or .yml file extension)

- This is what I showed you in my previous response
- YAML is generally preferred for CloudFormation templates because it's more human-readable
- Allows comments (using the # symbol)
- Less verbose than JSON (doesn't require as many quotes and braces)

2. JSON format (.json file extension)

- The same template could be converted to JSON
- Some developers prefer JSON for programmatic manipulation
- Better supported by some older tools

Most AWS users prefer YAML for CloudFormation templates because:
- It's more concise and easier to read
- It supports comments, which helps document your infrastructure
- It's less prone to syntax errors like missing commas or brackets

When you're ready to deploy your template, you can:
- Upload the file directly through the AWS Management Console
- Use the AWS CLI with the aws cloudformation create-stack command
- Store it in an S3 bucket and reference it during deployment
- Include it in a version control system like Git for tracking changes
Both formats are functionally identical to AWS CloudFormation - the choice between YAML and JSON is purely based on your preference and workflow requirements.**

## Creating the Files
1. You can create your files from scratch your self, but with the advent of AI IaC just got a lot easier.
2. Export the code in AWS CloudFormation Designer, AWS CDK, Erd Party Tools (like Terraform), AWS Config.
3. Directly, in most cloud platforms you can generate the code using there AI Agent
  - Claude is great as well (example prompt below)
    ```Please create the IaC for a cloudformation in AWS for an EMR setup within a VPC, create multiple S3 buckets for data, plus 3 different roles: 
    1. System Admin
    2. system read, write, and executor
    3. system reader and monitoring
    ```
### How AWS Console-to-Code Works

- **Recording Actions:** AWS Console-to-Code allows you to record your actions in the AWS Management Console, such as launching an EC2 instance.
- **Code Generation:** After you perform the desired actions, you can stop the recording and generate code in your preferred IaC format. Supported formats include AWS CloudFormation (YAML or JSON) and AWS Cloud Development Kit (CDK) in Java, Python, or TypeScript[1][2][4].
- **Preview and Export:** You can preview the generated code and copy or download it for use in automation, pipelines, or further customization[1][2][4].
- **No Need to Create Resources:** The "Preview code" feature lets you generate the IaC code for resources like EC2 instances or Auto Scaling groups without actually creating them in your account[1].

### Step-by-Step Process

1. **Access the EC2 Console:** Open the Amazon EC2 console.
2. **Start Recording:** Locate the AWS Console-to-Code widget and click **Start recording**.
3. **Perform Actions:** Launch an EC2 instance or perform other desired actions.
4. **Stop Recording:** Click **Stop** to end the recording session.
5. **Review and Export Code:** In the "Recorded actions" table, select the relevant actions and choose to generate code in AWS CLI, CloudFormation, or CDK formats. You can then copy or download the code[1][2][4].

### Supported Services

As of the latest updates, AWS Console-to-Code supports exporting actions for:
- Amazon EC2
- Amazon RDS
- Amazon VPC[1][2][4]

### Additional Notes

- **Quota:** There is a free quota for code generations in CDK and CloudFormation formats (25 per month). Beyond that, an Amazon Q Developer subscription is required[1].
- **Session Scope:** Recorded actions are only retained within the current browser tab and session. Refreshing the tab will lose the recorded actions[1].
- **Customization:** The generated code serves as a starting point and should be reviewed and customized before use in production[1][2][4].

### Alternative Approaches

For resources created outside of Console-to-Code, tools like the CloudFormation IaC Generator or third-party utilities (e.g., Terraforming) can help generate IaC definitions from existing AWS resources, but these are separate from the native AWS Management Console experience[3][5].

---
## Options for Existing Infrastructure
There are several ways to extract Infrastructure as Code (IaC) from existing AWS resources in the console. Here are the main methods:

### **1. CloudFormation Designer**
- Go to **CloudFormation** → **Designer**
- Create a new template or import existing resources
- Drag and drop resources to visually design your infrastructure
- Export as CloudFormation JSON/YAML

### **2. AWS CloudFormation Stack Sets (for existing stacks)**
- Navigate to **CloudFormation** → **Stacks**
- Select your existing stack
- Click **Template** tab to view the source template
- Download the template in JSON or YAML format

### **3. AWS CDK (Cloud Development Kit)**
- Use `cdk init` to create a new CDK project
- Use `cdk synth` to generate CloudFormation from CDK code
- View generated templates in the `cdk.out` directory

### **4. Former2 (Third-party tool)**
- Web-based tool: https://former2.com
- Scans your AWS account and generates IaC templates
- Supports CloudFormation, Terraform, CDK, and Pulumi
- **Note**: Requires AWS credentials with read permissions

### **5. AWS CLI with Resource Groups**
```bash
# List resources in a resource group
aws resource-groups list-group-resources --group-name your-group-name

# Get CloudFormation template for a stack
aws cloudformation get-template --stack-name your-stack-name
```

### **6. AWS Config (for compliance/documentation)**
- Go to **AWS Config** → **Resources**
- Search for specific resource types
- View resource configurations and relationships
- Export configuration history

### **7. Terraform Import (if using Terraform)**
```bash
# Import existing resources into Terraform state
terraform import aws_instance.example i-1234567890abcdef0
terraform show
```

### **8. AWS Systems Manager Application Manager**
- Navigate to **Systems Manager** → **Application Manager**
- View application components and their relationships
- Export resource configurations

### **9. AWS Well-Architected Tool**
- Create workload definitions
- Document your architecture
- Export architectural decisions and configurations

### **10. Manual Documentation via AWS CLI**
```bash
# Describe specific resources
aws ec2 describe-instances
aws s3api list-buckets
aws iam list-roles
aws emr list-clusters

# Output to files for documentation
aws ec2 describe-instances > ec2-instances.json
```

### **Best Practices for IaC Extraction:**

1. **Start with CloudFormation Designer** for visual learners
2. **Use Former2** for comprehensive account scanning
3. **Document resource dependencies** manually if needed
4. **Validate generated templates** before using in production
5. **Consider resource naming conventions** when extracting
6. **Group related resources** logically in your IaC

### **For Your EMR Setup Specifically:**
If you have an existing EMR cluster, you can:
1. Go to **EMR** → **Clusters** → Select your cluster
2. View the **Configuration** tab for cluster settings
3. Use Former2 to scan and generate CloudFormation for your existing EMR resources
4. Export security groups, VPC settings, and IAM roles separately
