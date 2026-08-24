# VPC Connecting To
Below is all about connecting to a VPC other than through the AWS Web Console.
This question actually has two different problems tangled inside it, and separating them makes everything clearer.VPN and Direct Connect solve "how do I get from my network into AWS." Peering solves "how do two AWS networks talk to each other." They aren't really alternatives to each other — most real architectures use one from each group.
<img width="1474" height="600" alt="image" src="https://github.com/user-attachments/assets/86c6c5ed-9270-4920-9796-027a4a789a72" />

## The three you asked about

| | Site-to-Site VPN | Direct Connect | VPC peering |
|---|---|---|---|
| Connects | On-prem ↔ VPC | On-prem ↔ VPC | VPC ↔ VPC |
| Path | Public internet | Dedicated fibre to an AWS DX location |AWS backbone |
| Encryption | IPsec, always | None by default (MACsec on some ports, or run VPN over it) | Encrypted at the physical layer by AWS |
| Bandwidth | ~1.25 Gbps per tunnel | 1/10/100 Gbps dedicated, or 50 Mbps–25 Gbps hosted | No added bottleneck |
| Latency | Variable — internet weather | Consistent, predictable | Very low |
| Time to set up | Minutes | Weeks to months (cross-connect, LOA-CFA, partner) |Minutes |
| Cost shape | ~$0.05/hr + standard data-out | Port-hours + much cheaper data-out | No hourly fee, just data transfer |

The economics flip at volume: DX has real fixed costs but a lower per-GB rate, so it wins once you're pushing steady, large traffic. A common production pattern is DX as primary with a VPN as automatic failover.

Two peering gotchas worth knowing up front. It's **non-transitive** — if A peers with B and B peers with C, A still cannot reach C. And there's no edge-to-edge routing, so you can't reach a peer's Direct Connect, VPN, or NAT gateway through the peering link. CIDR blocks also can't overlap. With more than a handful of VPCs, the n(n−1)/2 mesh becomes unmanageable, which is exactly why the next option exists.

## The other options

**Transit Gateway** is the one most people end up needing. It's a regional hub-and-spoke router: attach hundreds of VPCs, your VPNs, and your Direct Connect, and get transitive routing with route tables you actually control. TGWs can also peer across regions. You pay per attachment-hour plus per GB, which is the main reason simple two-VPC setups still use plain peering.

**Cloud WAN** sits a layer above that — a managed global network with policy-driven segmentation across regions, aimed at large multi-region estates that outgrow stitched-together TGWs.

**PrivateLink** is a different philosophy entirely: instead of routing networks together, you expose one specific service (behind an NLB) and consumers reach it through an interface endpoint in their own VPC. Traffic is one-directional, overlapping CIDRs don't matter, and nothing else on either network becomes reachable. It's the right answer for consuming a SaaS product or exposing an internal service to other teams. Gateway endpoints are the related, free variant for S3 and DynamoDB.

**Client VPN** covers the case people often conflate with Site-to-Site: individual laptops and remote users, OpenVPN-based, per-connection pricing. **Verified Access** is the zero-trust alternative — per-application access with identity checks and no VPN client at all.

A few more worth having in your vocabulary: **Direct Connect Gateway** lets a single DX reach VPCs in multiple regions and accounts; **VPC sharing** via Resource Access Manager lets several accounts deploy into the same subnets, sidestepping inter-VPC connectivity altogether; **VPC Lattice** handles service-to-service connectivity at the application layer, including across overlapping CIDRs; and **third-party appliances on EC2** (Palo Alto, Cisco, Fortinet) still make sense when you need feature parity with existing on-prem gear.

If you can share roughly how many VPCs and accounts you're dealing with, and whether the on-prem traffic is bulk data or latency-sensitive, I can narrow this to a concrete recommendation.

---
## Helpful Background Terms
**ENI — Elastic Network Interface**

A virtual network card that lives in a VPC subnet. It holds the things a physical NIC would: a primary private IPv4 address, optional secondary IPs, an IPv6 set, a MAC address, one or more security groups, and optionally an Elastic IP per private address. An ENI is pinned to a single subnet, and therefore to a single Availability Zone, for its whole life.

Instances get a primary ENI (`eth0`) that's created and destroyed with them. Secondary ENIs are independent objects — you can detach one from a failed instance and attach it to a replacement, and the IP, MAC, and security groups travel with it. That makes them useful for management/data plane separation, licence anchoring, and failover patterns.

The broader point is that an ENI is *the* mechanism by which anything acquires presence inside your VPC. When a NAT gateway, an interface VPC endpoint, a Lambda function configured for VPC access, an RDS instance, a Fargate task, an EFS mount target, or an ALB node shows up with a private IP in your subnet, what's actually been placed there is an ENI. If you've ever wondered why an interface endpoint consumes an IP in each subnet you enable, that's why.

**Route 53 Resolver**

The DNS service that AWS runs inside every VPC. It's reachable at the VPC's base CIDR plus two (so `10.0.0.2` in a `10.0.0.0/16` VPC) and at the link-local address `169.254.169.253`. It resolves public internet names, the internal `ec2.internal`/`compute.internal` names, and any Route 53 private hosted zones associated with the VPC. It's on by default and is what `AmazonProvidedDNS` in a DHCP option set points to.

The part worth knowing for hybrid setups is Resolver endpoints, which extend it across a VPN or Direct Connect:

- **Inbound endpoints** give the resolver a set of ENIs with routable private IPs, so your on-premises DNS servers can forward queries into AWS and resolve private hosted zone records.
- **Outbound endpoints**, paired with **resolver rules**, do the reverse: queries from your VPC for, say, `corp.internal` get forwarded to your on-prem DNS servers instead of going to public DNS.

Together they solve the bidirectional name resolution problem that otherwise bites people right after they finish building the network path — the routing works, but nothing can resolve anything on the other side. Two related features hang off the same service: **Resolver DNS Firewall**, for allow/block-listing domains, and **query logging**, which is often the fastest way to see what your workloads are actually looking up.
