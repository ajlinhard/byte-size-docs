# NACL Common Configurations
## Common features and settings

**Rule anatomy.** Each NACL rule has five parts: a rule number, a protocol (or a named type like HTTP/SSH which fills in the protocol and port for you), a port range, a source (inbound) or destination (outbound) CIDR, and an allow/deny action. There is no "referenced NACL" concept — unlike security groups, you cannot point at another group or a prefix list. Only CIDR blocks.

**Rule numbers and evaluation order.** Valid numbers are 1–32766. Rules are evaluated lowest-first and **the first match wins** — evaluation stops there, so a permissive rule at 100 will shadow a deny at 200. This is the opposite of security groups, where every rule is considered. Conventions worth adopting:

- Increment by 100 so you can insert later without renumbering.
- Put explicit denies in a low band (1–99) so they always win over the allow rules below them.
- Keep inbound and outbound numbering symmetric where they're logically paired; it makes review much easier.

**The implicit deny.** Every NACL ends with rule `*`, an uneditable deny-all. Anything not matched is dropped.

**Association.** A subnet has exactly one NACL, but one NACL can be associated with many subnets — this is how you apply a single ruleset to all your private subnets across AZs. If you disassociate a subnet's custom NACL, it silently reverts to the VPC's default NACL (which is wide open), so removal is not the same as tightening.

**IPv4 and IPv6 are separate.** A rule with an IPv4 CIDR does nothing for IPv6 traffic. If your subnet is dual-stack you need a parallel set of rules using `::/0` and specific IPv6 blocks, which roughly doubles your rule count.

**Limits.** 20 rules per direction by default (adjustable to 40, but AWS warns of network performance impact), and 200 NACLs per VPC. The 20-rule ceiling is the real design constraint — it's why NACLs are best used for coarse rules and why you should not try to encode per-application policy in them.

**Ephemeral ports.** Because NACLs are stateless, return traffic needs its own rule. Which range depends on what's originating the connection:

| Originator | Ephemeral range |
|---|---|
| Linux kernel default | 32768–60999 |
| Windows Server 2008+ | 49152–65535 |
| NAT Gateway | 1024–65535 |
| ELB / Lambda / other AWS services | 1024–65535 |

Practically everyone allows **1024–65535**, since NAT Gateways and managed services use the full range and there's no way to be tighter without breaking them.

**Things NACLs don't filter.** Traffic to and from the Amazon DNS resolver (the VPC+2 address), DHCP, instance metadata at 169.254.169.254, and Windows license activation all bypass NACLs. Also note NACLs apply only to traffic crossing the subnet boundary — two instances in the *same* subnet talk to each other without any NACL evaluation, so a NACL will never isolate same-subnet peers. Only security groups can do that.

**Debugging.** VPC Flow Logs are the tool. A NACL rejection shows as `REJECT` on a flow record; a security group rejection also shows `REJECT`, so distinguish them by direction — because security groups are stateful, an SG block on the return leg never appears in the logs, whereas a NACL block produces a visible REJECT in that direction. In newer flow log formats you can add the `reject-reason` field to disambiguate.

---

## Public subnet

Resources with a route to an Internet Gateway: load balancers, bastion hosts, NAT Gateways.

**Inbound**

| # | Type | Port | Source | Action |
|---|---|---|---|---|
| 100 | HTTP | 80 | 0.0.0.0/0 | ALLOW |
| 110 | HTTPS | 443 | 0.0.0.0/0 | ALLOW |
| 120 | SSH | 22 | your office CIDR | ALLOW |
| 130 | Custom TCP | 1024–65535 | 0.0.0.0/0 | ALLOW |
| * | all | all | 0.0.0.0/0 | DENY |

**Outbound**

| # | Type | Port | Destination | Action |
|---|---|---|---|---|
| 100 | HTTP | 80 | 0.0.0.0/0 | ALLOW |
| 110 | HTTPS | 443 | 0.0.0.0/0 | ALLOW |
| 120 | Custom TCP | 1024–65535 | 0.0.0.0/0 | ALLOW |
| 130 | Custom TCP | <app port> | private subnet CIDR | ALLOW |
| * | all | all | 0.0.0.0/0 | DENY |

Rule 130 inbound is the one people forget: it's the return traffic for connections your instances *initiate* outbound (yum updates, API calls). Outbound 120 is the return traffic for connections the internet initiates *inbound*. Both directions need an ephemeral rule, for different reasons.

If this subnet holds a NAT Gateway, you additionally need inbound from the private subnet CIDR on whatever ports those instances use outbound (80/443 typically), and outbound ephemeral back to the private CIDR.

---

## Completely private (isolated, no internet at all)

Database subnets, internal-only services, anything with no NAT and no IGW route. This is the tightest and simplest case: every legitimate packet has a VPC-internal address on at least one end.

**Inbound**

| # | Type | Port | Source | Action |
|---|---|---|---|---|
| 100 | Custom TCP | 5432 | app tier subnet CIDR | ALLOW |
| 110 | Custom TCP | 1024–65535 | VPC CIDR | ALLOW |
| * | all | all | 0.0.0.0/0 | DENY |

**Outbound**

| # | Type | Port | Destination | Action |
|---|---|---|---|---|
| 100 | Custom TCP | 1024–65535 | app tier subnet CIDR | ALLOW |
| 110 | Custom TCP | 443 | VPC CIDR | ALLOW |
| * | all | all | 0.0.0.0/0 | DENY |

Note that nothing here mentions 0.0.0.0/0 as an allow. That's the defining property of a truly isolated subnet, and it's a useful thing to assert in a Config rule or SCP. Outbound 443 to the VPC CIDR covers Interface VPC Endpoints (Secrets Manager, KMS, SSM), which live inside your VPC as ENIs and so match your own CIDR. Gateway endpoints for S3 and DynamoDB are the exception — their traffic goes to AWS public IP ranges, so if you use them you need outbound 443 to the relevant `com.amazonaws.<region>.s3` prefix list ranges plus inbound ephemeral from them, which is awkward given NACLs can't reference prefix lists. Many teams accept a broad `443 to 0.0.0.0/0` for that reason and enforce the real restriction with endpoint policies instead.

---

## Private with NAT egress

The most common "private" subnet in practice: no inbound internet, but outbound for patching and third-party APIs.

**Inbound**

| # | Type | Port | Source | Action |
|---|---|---|---|---|
| 100 | Custom TCP | 8080 | public/ALB subnet CIDR | ALLOW |
| 110 | SSH | 22 | bastion subnet CIDR | ALLOW |
| 120 | Custom TCP | 1024–65535 | 0.0.0.0/0 | ALLOW |
| * | all | all | 0.0.0.0/0 | DENY |

**Outbound**

| # | Type | Port | Destination | Action |
|---|---|---|---|---|
| 100 | HTTP | 80 | 0.0.0.0/0 | ALLOW |
| 110 | HTTPS | 443 | 0.0.0.0/0 | ALLOW |
| 120 | Custom TCP | 5432 | DB subnet CIDR | ALLOW |
| 130 | Custom TCP | 1024–65535 | VPC CIDR | ALLOW |
| * | all | all | 0.0.0.0/0 | DENY |

Inbound 120 has to be `0.0.0.0/0` rather than a narrower CIDR, because the responses returning through the NAT Gateway carry the *original internet server's* source address. This is the point where NACLs stop being a meaningful inbound control for private subnets — you're allowing 64,000 ports from the whole internet — and it's the strongest argument for treating NACLs as a blunt instrument and putting real policy in security groups.

---

## "Mixed" public + private

Worth being direct about this: **you cannot apply two NACLs to one subnet**, and NACLs can't distinguish resources inside a subnet. So a mixed subnet has no good NACL story. Your options:

**Split the subnets (the right answer).** Public and private resources go in separate subnets with separate NACLs, per the recipes above. This is why the standard VPC layout has 2–3 subnet tiers per AZ. The NACL then genuinely means something, and route tables reinforce it — the private subnet's lack of an IGW route is doing most of the actual security work.

**If you're stuck with a shared subnet**, the NACL must be the *union* of what both workloads need, which means it degenerates to roughly the public ruleset. In that case, be honest that the NACL provides essentially no protection for the private resources and put all your effort into security groups: reference-by-group-ID rules so the database SG accepts 5432 only from the app SG, never a CIDR. Use the NACL only for what SGs can't do — explicit denies of known-bad CIDRs at rule numbers 1–99.

**A middle path** some teams use: keep one NACL that's permissive for the shared tier, but carve the private resources into a `/28` and add a low-numbered deny rule blocking inbound 0.0.0.0/0 to that range on sensitive ports. It works, but it's fragile — it depends on IP assignment discipline that nothing enforces, and it burns scarce rule slots. Splitting subnets is cheaper in every sense.

---

A closing thought on how to think about the pair: NACLs are best treated as a **blast-radius control and a compliance artifact**, not as your primary access policy. They stop a misconfigured security group from exposing an entire subnet, they give you the explicit-deny capability SGs lack, and they're easy for an auditor to read. But the 20-rule limit, the CIDR-only matching, and the ephemeral-port requirement all mean that any attempt to express detailed application policy in a NACL will end up either broken or so permissive it isn't protecting anything.
