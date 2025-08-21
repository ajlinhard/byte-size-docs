# Bastion Host - Servers
A bastion host in AWS is a special-purpose server that acts as a secure gateway to access resources in private subnets within your Virtual Private Cloud (VPC). Here's how it works:

**Purpose and Function:**
A bastion host sits in a public subnet and serves as a "jump box" or intermediary server that allows you to securely connect to EC2 instances or other resources located in private subnets. Private subnet resources don't have direct internet access, so the bastion provides a controlled entry point.

**Typical Architecture:**
- Bastion host is placed in a public subnet with a public IP address
- Your private EC2 instances are in private subnets (no direct internet access)
- You SSH into the bastion first, then from there SSH into your private instances

**Security Benefits:**
- Reduces attack surface by limiting direct internet access to private resources
- Centralizes access control and logging
- Allows you to apply strict security rules to a single entry point
- Can be configured with multi-factor authentication

**Common Setup:**
1. Launch a small EC2 instance (often t2.micro) in a public subnet
2. Configure security groups to allow SSH (port 22) from your IP addresses
3. Use SSH agent forwarding or SSH tunneling to reach private instances
4. Apply restrictive security groups to private instances that only allow access from the bastion

**Modern Alternatives:**
AWS now offers Session Manager (part of Systems Manager) which can eliminate the need for bastion hosts by providing browser-based shell access to private instances without requiring SSH keys or open ports.

The term "bastion" comes from fortress architecture, where a bastion was a defensive structure that projected outward to provide protection - similar to how this server protects your private infrastructure.
