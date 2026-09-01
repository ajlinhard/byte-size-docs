# NACL vs. Security Groups
## Purpose

Both are virtual firewalls in a VPC, but they sit at different layers:

- **Security Groups** attach to elastic network interfaces (so effectively to instances, RDS databases, Lambda ENIs, load balancers). They're the *last* line of defense before traffic reaches the resource.
- **Network ACLs** attach to subnets. Every resource in that subnet is covered automatically, so NACLs act as a coarse, subnet-wide guard rail.

Traffic entering a subnet hits the NACL first, then the security group. Outbound, the order reverses: security group first, then NACL.

## Default rules

**Default security group** (the one AWS creates with the VPC):
- Inbound: allow all traffic where the source is the same security group — i.e. members can talk to each other, nothing else gets in.
- Outbound: allow all traffic.

**A security group you create yourself:**
- Inbound: no rules at all, which means everything is denied.
- Outbound: one rule allowing all traffic to 0.0.0.0/0.

**Default NACL** (created with the VPC):
- Inbound: rule 100 — allow all traffic from 0.0.0.0/0; then rule `*` — deny all.
- Outbound: identical. Net effect: wide open.

**A NACL you create yourself:**
- Inbound and outbound contain only the `*` deny-all rule. Nothing passes until you add rules.

## Stateful vs stateless

**Security groups are stateful.** If you allow inbound traffic on port 443, the response is automatically permitted back out, regardless of your outbound rules. You never need to think about return traffic.

**NACLs are stateless.** Each direction is evaluated independently, so allowing inbound 443 does *not* allow the reply. The reply leaves from an ephemeral source port, so your outbound NACL rules must permit ports 1024–65535 (AWS's recommended range; Linux typically uses 32768–60999, Windows 49152–65535). Forgetting this is the single most common cause of "my NACL is blocking things and I don't know why."

## Other differences worth knowing

| | Security Group | NACL |
|---|---|---|
| Scope | ENI / resource | Subnet |
| Rule types | Allow only | Allow and deny |
| Evaluation | All rules considered together | Numbered order, lowest first, first match wins |
| State | Stateful | Stateless |
| Assignment | Must be explicitly attached | Applies automatically to the subnet |

## How they relate in practice

Think of them as complementary rather than redundant. Because NACLs support explicit denies, they're the right tool for blanket blocks — banning a malicious IP range across an entire subnet, for instance, which security groups can't express at all. Security groups handle the fine-grained work: this app tier may reach that database tier on port 5432, referenced by group ID rather than IP.

For traffic to reach a resource, it must pass *both*. A common debugging trap is a permissive security group paired with a custom NACL that was never given rules, or one that allows inbound but not the ephemeral return range.
