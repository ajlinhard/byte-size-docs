# Virtual Private Cloud (VPC)
VPCs are the basic building blocks for a cloud designed system. The VPC is the initial boundary and container for all the resources of an environment.

**External Notes**
[AWS Intro Notes](https://docs.google.com/document/d/14Mns0qcBsT2eeur1JwFq_GvyyT0qnBFs4dQEUcSnSPA/edit?tab=t.0#heading=h.ikequ5ghmh6l)

## Cost (Free vs Charges, update 5/22/2025) 
AWS VPC components have varying cost structures, with some being free and others having usage-based pricing:

**Free Components:**
- The VPC itself (no charge for creating or maintaining)
- Subnets
- Route tables
- Internet Gateways
- Security groups
- Network ACLs
- VPC endpoints for S3 and DynamoDB (Gateway endpoints)

**Paid Components:**

**NAT Gateways:** Around $0.045 per hour ($32.40/month) plus $0.045 per GB of data processed

**VPC Endpoints (Interface endpoints):** Approximately $0.01 per hour per endpoint ($7.20/month) plus $0.01 per GB of data processed

**VPN Connections:** About $0.05 per hour ($36/month) per VPN connection

**Transit Gateway:** Around $0.05 per hour per attachment ($36/month) plus $0.02 per GB of data processed

**Direct Connect:** Varies significantly by port speed and location, ranging from hundreds to thousands of dollars monthly

**VPC Peering:** Free for the connection itself, but you pay standard data transfer charges between regions (around $0.02 per GB)

**Elastic IPs:** Free while in use, but $0.005 per hour ($3.60/month) when not associated with a running instance

The biggest cost drivers are typically NAT Gateways and data transfer charges, especially for high-traffic applications. Many organizations can keep VPC costs low by using free components like Internet Gateways for public subnets and being strategic about NAT Gateway placement.

Prices vary slightly by AWS region and are subject to change, so check the current AWS pricing page for your specific region and use case.
