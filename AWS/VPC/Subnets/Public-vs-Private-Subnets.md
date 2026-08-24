# Public vs Private Subnets
A **public subnet** and **private subnet** differ in their internet accessibility and routing configuration:

## Public Subnet
- Has a route table with a route to an Internet Gateway (IGW)
- Resources can have public IP addresses and direct internet access
- Can both receive inbound traffic from the internet and send outbound traffic
- Typically used for web servers, load balancers, bastion hosts

## Private Subnet
- No direct route to an Internet Gateway
- Resources cannot be directly accessed from the internet
- No public IP addresses assigned to instances
- Typically used for databases, application servers, internal services

** Short answer: it depends entirely on the route table, not the name and not the traffic rules. **

In AWS (and equivalently in Azure/GCP), a subnet is "private" if its route table has **no route to an Internet Gateway**. That's the whole definition. The name is just a label, and NACLs/security groups control what's permitted *once traffic can reach the subnet* — they don't create the path in the first place.

**1. Route table has no IGW route** (e.g., `0.0.0.0/0 → nat-xxxx`, or only the local VPC route) — still genuinely private. Instances can't be reached from the internet even with wide-open NACLs and security groups, because there's no return path for unsolicited inbound traffic. A NAT gateway is outbound-only by design.

**2. Route table has `0.0.0.0/0 → igw-xxxx`** — it's a public subnet no matter what you called it. Add a public IP on an instance plus allow-all rules, and it's directly exposed.

### Caveats
That said, "not reachable from the internet" isn't the same as "safe." Allow-all in a private subnet still leaves you open to anything that *can* route there: peered VPCs, Transit Gateway attachments, VPN/Direct Connect clients, other subnets in the same VPC, and anything fronted by a load balancer or bastion you've placed in the public tier. It also removes any containment if one instance gets compromised — lateral movement is unrestricted. And permissive egress is the usual path for data exfiltration and malware callbacks.

Worth checking too: `MapPublicIpOnLaunch` on the subnet, and whether IPv6 is in play (an egress-only internet gateway keeps things private; a plain IGW route for `::/0` does not).

So: verify the route table to answer the "is it private" question, then tighten the NACLs and security groups anyway, because defense in depth is the actual reason those controls exist.

### Security Checks
Removing the IGW eliminates *one* path: unsolicited inbound packets arriving directly from the internet. It doesn't make the system unreachable, and IAM isn't the remaining gate.

**Network paths that don't involve an IGW.** Anything you've attached to the VPC is a potential route in: peering connections, Transit Gateway, Site-to-Site VPN, Direct Connect, PrivateLink endpoint services. More commonly, it's your own architecture — an ALB in the public subnet forwarding to private targets means the internet reaches your application on purpose. Same for a bastion, or a Lambda in-VPC, or anything in a sibling subnet that got popped first. If your app has an SQL injection or RCE bug behind that load balancer, the attacker never touches IAM.

**Outbound is an inbound path.** A NAT gateway lets a compromised host call out. That's how most real intrusions actually work: malicious dependency, poisoned container image, compromised update server, then a reverse shell established from inside. The connection is outbound-initiated, so the "no inbound route" property is irrelevant.

**IAM cuts the other way too.** Leaked access keys or an over-permissive role let someone hit the AWS control plane from anywhere on the internet with no network path into your VPC at all. From there they can attach an IGW, modify route tables, share an EBS snapshot to their own account, or just read the S3 bucket — where a lot of the data you care about probably lives, entirely outside your VPC boundary. SSRF plus IMDSv1 is the classic bridge between the two planes: reach the app over HTTP, pull role credentials out of instance metadata, pivot to the control plane.

So the useful framing is that network isolation and IAM are independent layers protecting different things. No IGW is a good default and worth keeping — it just isn't a perimeter.

Practical follow-ups if you're hardening this: enforce IMDSv2, restrict egress rather than allowing `0.0.0.0/0` outbound, use VPC endpoints for AWS services so that traffic doesn't traverse NAT, scope roles narrowly, and turn on GuardDuty and VPC Flow Logs so you'd actually notice the lateral movement or the callback.

## Can Private Subnets Reach APIs?

**Yes, absolutely!** Private subnets can reach external APIs through several methods:

**1. NAT Gateway/Instance**
- Most common approach
- NAT Gateway in a public subnet allows outbound internet access
- Private subnet route table points to the NAT Gateway for internet destinations
- Enables API calls while keeping resources private

**2. VPC Endpoints**
- For AWS services (like S3, DynamoDB, Lambda)
- Private connection without going through the internet
- More secure and often faster than going through a NAT Gateway

**3. Direct Connect or VPN**
- For private APIs in other networks
- Establishes private connectivity without using the public internet

**Example scenario:** Your application servers in a private subnet can call external payment APIs, send emails through SendGrid, or fetch data from third-party REST APIs - they just route through a NAT Gateway rather than having direct internet access.

The key distinction is that private subnets can initiate outbound connections but cannot receive unsolicited inbound traffic from the internet.
