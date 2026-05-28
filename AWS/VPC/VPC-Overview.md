# Virtual Private Cloud (VPC)
VPCs are the basic building blocks for a cloud designed system. The VPC is the initial boundary and container for all the resources of an environment.

**External Notes**
[AWS Intro Notes](https://docs.google.com/document/d/14Mns0qcBsT2eeur1JwFq_GvyyT0qnBFs4dQEUcSnSPA/edit?tab=t.0#heading=h.ikequ5ghmh6l)

## AWS Default VPC — Cost Summary

**The default VPC itself is free.** You are not charged for creating or having a VPC (default or additional ones).

### What you *do* pay for inside a VPC:
AWS VPC components have varying cost structures, with some being free and others having usage-based pricing:

| Resource | Cost |
|---|---|
| **VPC itself** | Free (default and additional) |
| **Subnets** | Free |
| **Internet Gateway** | Free |
| **NAT Gateway** | 💰 Paid (~$0.045/hr + data transfer) |
| **VPN Gateway** | 💰 Paid |
| **VPC Peering** (data transfer) | 💰 Paid |
| **Elastic IPs** (unused) | 💰 Paid if not attached |
| **VPC Endpoints** (some types) | 💰 Paid (Interface endpoints ~$0.01/hr) |

### Default VPC specifics:

- **One default VPC per AWS region** — so if you use multiple regions, each gets its own default VPC.
- You can create **up to 5 VPCs per region** by default (soft limit, can be increased by requesting a quota increase).
- The default VPC comes pre-configured with a subnet in each Availability Zone, an Internet Gateway, and a default route table — all free.

### Bottom line:
Just having VPCs (default or extra) costs nothing. You're billed for the **resources and services running *inside* them** — EC2 instances, NAT Gateways, data transfer, etc.

**Free Components:**
- The VPC itself (no charge for creating or maintaining)
- Subnets
- Route tables
- Internet Gateways
- Security groups
- Network ACLs
- VPC endpoints for S3 and DynamoDB (Gateway endpoints)

The biggest cost drivers are typically NAT Gateways and data transfer charges, especially for high-traffic applications. Many organizations can keep VPC costs low by using free components like Internet Gateways for public subnets and being strategic about NAT Gateway placement.

Prices vary slightly by AWS region and are subject to change, so check the current AWS pricing page for your specific region and use case.

## Should You Use the Default VPC?

**Short answer: No, not for real applications.** It's fine for quick experiments, but you should create a custom VPC for anything serious.

---

### Problems with the Default VPC

**🔓 Security — the biggest concern**
- All default subnets are **public** (auto-assign public IPs is ON by default)
- Resources you launch get a public IP automatically — easy to accidentally expose things to the internet
- It's a shared "scratch pad" environment with looser defaults

**🏗️ No isolation between environments**
- If you're running dev, staging, and prod, they'd all share the same VPC with no separation
- Harder to enforce least-privilege networking

**📐 Inflexible IP addressing**
- The default VPC uses `172.31.0.0/16` — you can't change this CIDR
- Can cause conflicts if you ever need to peer with other VPCs or connect to on-premises networks via VPN

**🧹 It's a shared/messy space**
- Easy to accidentally deploy test resources alongside production
- Teams or services can step on each other
- Harder to audit what belongs where

**🔁 Accidental deletion risk**
- If someone deletes the default VPC (it happens), resources depending on it break and recreating it requires AWS support or CLI gymnastics

---

### What You Should Do Instead

Create a **custom VPC per environment** (e.g., dev, staging, prod) with:

- ✅ **Public subnets** — for load balancers, NAT gateways, bastion hosts
- ✅ **Private subnets** — for your app servers, databases, Lambda functions
- ✅ **Your own CIDR range** — planned to avoid conflicts (e.g. `10.0.0.0/16`)
- ✅ **NAT Gateway** — so private resources can reach the internet without being exposed
- ✅ **Proper security groups and NACLs** from the start

---

### When the Default VPC is Fine
- Quick one-off experiments / learning
- Throwaway demos
- Personal sandbox testing

---

### Rule of Thumb
> Treat the default VPC like a hotel lobby — okay to pass through, but you wouldn't set up your business there.

If you're building anything that will handle real users or data, spend the hour setting up a proper custom VPC. It's much harder to migrate out of the default VPC later than to start clean.
