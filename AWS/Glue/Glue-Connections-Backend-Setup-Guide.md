# Glue Connections Backend Setup Guide:
Whwn setting up Glue within your application or system there are more items than code alone to considered. Like most cloud infrastructure Glue requires some configuration of network, security (IAM _ Sec. groups), and cost vs performance. To connect to different services and data infrastructure outside of S3 (and sometimes including S3) there are some need to knows.

### Documentation:
-[Connectivity / VPC Connection](https://docs.aws.amazon.com/glue/latest/dg/sap-odata-connectivity-vpc-connection.html)
- [Setting up Amazon VPC for JDBC connections to Amazon RDS](https://docs.aws.amazon.com/glue/latest/dg/setup-vpc-for-glue-access.html)
- [Troubleshooting Connections in AWS Glue](https://docs.aws.amazon.com/glue/latest/dg/troubleshooting-connection.html)
  - [Glue Connection Error Linke](https://repost.aws/knowledge-center/glue-test-connection-failed)
- [Create Glue Connector for Data Source](https://repost.aws/articles/ARvfm96gY-RlSb_A0Zx3lcSQ/how-to-create-a-aws-glue-connector-for-data-sources-in-vmware-cloud-on-aws)
- [Key Topics in Apache Spark](https://docs.aws.amazon.com/prescriptive-guidance/latest/tuning-aws-glue-for-apache-spark/key-topics-apache-spark.html)

## Other Glue Setup
Setup items not included in this sheet, but still required for Glue:
- Create a role for your glue job(s),  with access to the Glue Service Role, Glue Resources, and other cloud resources.
- Create other data resources like RDS, S3, Kinesis, etc.
- Grant users or federated role access to the glue role and service.
- write code for testing connection code.

---
## Connection Permissions
**Summary from Official AWS Documentation Page:**
AWS Glue requires a security group with a self-referencing inbound rule for all TCP ports to enable communication between Glue components. This self-referencing rule restricts the source to the same security group in the VPC and doesn't open it to all networks.

### Key AWS Documentation Links:

1. **Setting up VPC for JDBC connections to RDS:**
   https://docs.aws.amazon.com/glue/latest/dg/setup-vpc-for-glue-access.html
   
2. **Connecting to JDBC data stores in a VPC:**
   https://docs.aws.amazon.com/glue/latest/dg/connection-JDBC-VPC.html

3. **Setting up networking for development endpoints:**
   https://docs.aws.amazon.com/glue/latest/dg/start-development-endpoint.html

### What the Documentation Says:

When connecting to databases in Amazon RDS using JDBC, you need to specify a security group with a self-referencing inbound rule for all TCP ports to enable AWS Glue components to communicate with each other.

The required configuration includes:
- **Type:** All TCP
- **Protocol:** TCP  
- **Port Range:** All ports
- **Source:** The same security group ID (self-referencing)

At least one chosen security group must specify a self-referencing inbound rule for all TCP ports to allow AWS Glue components to communicate and prevent access from other networks.

### More Detail about Behind the Scenes
* General Requirement for All Glue Jobs**

Apache Spark requires bidirectional connectivity among driver and executor nodes. One of the security groups needs to allow ingress rules on all TCP ports. You can prevent it from being open to the world by restricting the source of the security group to itself with a self-referencing security group.

#### Specific to Connectors

AWS Glue requires special security group that allows all inbound traffic from itself. You can create a self-referencing rule that allows all traffic originating from the security group.

To enable AWS Glue to communicate between its components when using connectors, either select or create a security group with a self-referencing inbound rule for all TCP ports, specifically a rule of Type All TCP, Protocol TCP, Port Range includes all ports, and whose Source is the same security group name as the Group ID.

#### Why This is Required

This requirement applies to **all AWS Glue jobs that run in a VPC**, including:
- Jobs using JDBC connections (RDS, Redshift, etc.)
- Jobs using Glue connectors
- Development endpoints
- Any job that accesses VPC resources

The self-referencing rule is mandatory because the Glue Spark driver and executors need to communicate with each other to coordinate the distributed processing work, regardless of whether you're using a connector or not.

**Key Documentation Links:**
- Troubleshooting connections: https://docs.aws.amazon.com/glue/latest/dg/troubleshooting-connection.html
- SAP OData connectivity: https://docs.aws.amazon.com/glue/latest/dg/sap-odata-connectivity-vpc-connection.html

---
## VPC Connectors in General
Great question! The answer is different depending on whether your Glue job runs in a VPC or not.

## AWS Glue Jobs WITHOUT VPC (S3 to S3 Jobs)

If a job doesn't need to run in your virtual private cloud (VPC) subnet—for example, transforming data from Amazon S3 to Amazon S3—no additional configuration is needed.

**For normal Spark jobs accessing only S3, you do NOT need:**
- A VPC configuration
- Security groups at all
- Self-referencing rules

This is the most common scenario for simple ETL jobs that read from S3 and write to S3.

## AWS Glue Jobs WITH VPC (JDBC/Connector Jobs)

If a job needs to run in your VPC subnet—for example, transforming data from a JDBC data store in a private subnet—AWS Glue sets up elastic network interfaces that enable your jobs to connect securely to other resources within your VPC.

**You ONLY need self-referencing security groups when:**
- Using a JDBC connection (RDS, Redshift, etc.)
- Using Glue connectors
- Accessing resources inside a VPC
- Using development endpoints

### Why VPC Jobs Need S3 Endpoints

When you associate a connection with your Glue job, it causes the Glue job to be run within the VPC specified in the connection. So now your Glue job needs a way to connect to S3 (which is external to your VPC) from within the VPC.

Even though the job is in a VPC, Glue still needs to write scripts and temporary data to S3, so you need either:
- An S3 VPC Gateway Endpoint (recommended), OR
- A NAT Gateway

## Summary

| Scenario | Security Group Needed? | Self-Referencing Rule? |
|----------|----------------------|------------------------|
| S3 → S3 job (no VPC) | ❌ No | ❌ No |
| JDBC/Connector job (VPC) | ✅ Yes | ✅ Yes |
| Development endpoint | ✅ Yes | ✅ Yes |

**Documentation:** https://docs.aws.amazon.com/glue/latest/dg/start-connecting.html

---
## S3 Connections (with + without endpoints)
### Scenario 1: S3 Bucket with No Public Access (But Not in VPC)

If your S3 bucket simply has "Block Public Access" enabled (which is a best practice), your Glue job **still does NOT need a VPC, security groups, or self-referencing rules**.

- Glue jobs run in AWS-managed infrastructure that already has private access to S3
- "Block Public Access" only prevents access from the public internet
- AWS services like Glue can still access the bucket via IAM permissions

**You only need:** Proper IAM role permissions for the Glue job

### Scenario 2: S3 Bucket Restricted to VPC Only (VPC Endpoint Policy)

If you want to **force all S3 access to go through a specific VPC** (using S3 bucket policies that restrict access to a VPC endpoint), then **YES**:

✅ **Your Glue job must run in that VPC**
✅ **The VPC needs an S3 VPC Gateway Endpoint**
✅ **The Glue job needs a security group with self-referencing rules**

### Why Self-Referencing Rules Are Still Needed

Apache Spark requires bidirectional connectivity among driver and executor nodes. One of the security groups needs to allow ingress rules on all TCP ports.

Even for S3-only jobs running in a VPC, the Glue Spark driver and executors still need to communicate with each other, so the self-referencing rule is required.

### Configuration Example:

```
Glue Job Configuration:
├── VPC: your-vpc-id
├── Subnet: private-subnet-id
├── Security Group: glue-sg (with self-referencing All TCP rule)
└── IAM Role: with S3 permissions

VPC Requirements:
├── S3 Gateway Endpoint (attached to route table)
└── S3 Bucket Policy: Restrict to VPC endpoint only
```

## Summary

| S3 Access Requirement | Needs VPC? | Needs SG? | Self-Ref Rule? |
|----------------------|-----------|-----------|----------------|
| Block Public Access only | ❌ No | ❌ No | ❌ No |
| VPC endpoint restriction | ✅ Yes | ✅ Yes | ✅ Yes |

So, if you're enforcing that S3 traffic must stay within your VPC (via bucket policies), then you need the full VPC setup including self-referencing security groups.

---
# Glue Cost Optimizations
If not careful you could end up causing additional cost with Glue Connectors and setups! Lets break down some of the network costs and performance considerations:

## Network Costs for Glue → RDS Within a VPC

### Good News: Data Transfer Costs Are Minimal or Free

Data transferred between EC2 instances or containers, or Elastic Network Interfaces in the same availability zone and same VPC over private IPv4 or IPv6 addresses are free.

**Key Points:**

1. **Same AZ (Availability Zone) = FREE**
   - If your Glue job and RDS database are in the same AZ within the same VPC, there are **no data transfer charges**
   
2. **Cross-AZ within same VPC = $0.01/GB each direction**
   Data transferred between EC2 instances or containers, or Elastic Network Interfaces across availability zones is charged at $0.01 per GB for egress traffic and $0.01 per GB for ingress traffic.
   - If Glue runs in one AZ and RDS is in another AZ within the same VPC: **$0.02/GB total** (in + out)

3. **No charge for inbound to AWS**
   There is no charge for inbound data transfer across all services in all Regions. Data transfer into AWS is $0.00 per GB in all locations.

## Network Performance

### Performance is Generally Good

**Pros:**
- Private network within VPC is fast and low-latency
- No internet gateway or NAT gateway in the path (for same VPC)
- Direct elastic network interface (ENI) connections

**Potential Bottlenecks:**
- **RDS write throughput limits** - RDS instances have IOPS and throughput limits based on instance size
- **Glue parallelism** - Multiple Glue executors writing simultaneously could saturate RDS
- **Network bandwidth** - ENI bandwidth limits based on Glue worker types

## Cost Optimization Tips

Traffic that crosses an Availability Zone boundary typically incurs a data transfer charge. Use resources from the local Availability Zone whenever possible.

**To minimize costs:**
1. **Deploy Glue and RDS in the same AZ** → FREE data transfer
2. **Use RDS Multi-AZ carefully** - Replication between AZs for Multi-AZ RDS is free, but Glue accessing the standby would incur cross-AZ charges
3. **Batch operations** - Write in larger batches rather than row-by-row to reduce overhead

## Example Cost Calculation

**Scenario:** Loading 100GB from S3 to RDS via Glue (cross-AZ)
- Glue → RDS: 100GB × $0.01 = **$1.00** (egress from Glue)
- Glue ← RDS (acknowledgments): ~negligible

**Compare to Glue job costs:**
- 10 DPUs × 1 hour × $0.44 = **$4.40**
- Cross-AZ transfer: **$1.00**
- Total: **$5.40**

The data transfer is only about 18% of the job cost in this example.

## Bottom Line

**Network strain:** Moderate - depends on your RDS instance size and write patterns
**Network cost:** Very low - especially if same AZ ($0), or minimal if cross-AZ ($0.01-0.02/GB)

The Glue DPU costs will typically far exceed any data transfer costs for within-VPC transfers.
