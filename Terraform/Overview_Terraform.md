# Terraform Overview
This tool is helpful for managing your infrastructure as code and platforms as code. Its suggested it may be slightly worst than Ansible with Paas, but it can still serve the purpose. 
This in accomplished through a declarative syntax, which means the code represents the desired state of what the user wants not the steps to accomplish that state. Writing out the steps to obtain the desired state would be imperative code.
Terrafrom will take the declarative code + the infrastructure state to create the imperative steps to provide the outcome.

## Documentation/Tutorials:
1. [Official Documentation](https://developer.hashicorp.com/terraform?product_intent=terraform)
2. [Officail Tutorials](https://developer.hashicorp.com/terraform/tutorials?product_intent=terraform)
3. [Youtube - Overview Tutorial](https://www.youtube.com/watch?v=l5k1ai_GBDE)
4. [Youtube - Basic Use Tutorial](https://www.youtube.com/watch?v=Gmrl8WkViX0)
5. [Terraform with AWS](https://developer.hashicorp.com/terraform/tutorials/aws-get-started)

## Concepts
These are the high-level important parts of Terraform
1. Providers - are the different service providers like AWS, Azure, and Kubernetes which Terraform can interact and work with
2. TF-config file - is the file containing the desired state of your infrastructure.
  a. It is 1 of 2 major inputs to Terraforms operations.
3. State - represents the current state of your infrastructure.
4. Core - the processing and acting part of Terraform responsible for taking the current to desired state for your infrastructure.
5. Declarative

## Use Case:
1. Update Production with the latest release, with easier rollback.
2. Standup Dev or Demo environments quickly.
 a. Use the destroy command to save on cost after development of demos.
3. Passing templates between teams.

## Terraform Actions:
1. **refresh** - query the infrastructure of providers to get their current state.
2. **plan** - create a execution plan to accomplished the desired state.
3. **apply** - execute the plan
4. **destroy** - delete/destroy the current infrastructure in the correct order.


## Basic Terraform File
```yaml
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.16"
    }
  }

  required_version = ">= 1.2.0"
}

provider "aws" {
    region = "us-east-1"
}

resource "aws_s3_bucket" "myTestTerraform" {
    bucket = "starbound-terraform-bucket"
    acl = "private"
}
```
