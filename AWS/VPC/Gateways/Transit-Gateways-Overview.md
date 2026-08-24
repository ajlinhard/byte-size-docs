# Transit Gateways Overview
A Transit Gateway (TGW) is AWS's managed, regional network hub that connects multiple VPCs, VPNs, and Direct Connect links through a single point instead of a mesh of individual peering connections.

**What it solves.** Without it, connecting N VPCs directly requires roughly N² peering connections, and VPC peering is non-transitive, so every pair needs its own explicit link. A TGW replaces that mesh with a hub-and-spoke model: each VPC or connection attaches once to the TGW, and the TGW routes between them.

**Core components:**
- **Attachments** — the things connected to it: VPCs, VPN connections, Direct Connect gateways, and peering to TGWs in other regions.
- **Route tables** — control which attachments can reach which. A TGW can have multiple route tables, letting you segment traffic (e.g., prod attachments in one table, dev in another, with no route between them).
- **Association** — which route table an attachment uses to route *its own* outbound traffic.
- **Propagation** — which route tables learn an attachment's CIDR as a destination.

**Key properties:**
- Transitive by design: A→TGW→C works even without a direct A↔C relationship, unlike VPC peering.
- Operates at Layer 3 (routing) only — no security groups, NACLs, or stateful filtering happen at the TGW itself.
- Scales to thousands of attachments and tens of Gbps per attachment.
- Can peer across regions and be shared across AWS accounts via AWS RAM.

**Typical use cases:** hub-and-spoke VPC architectures, centralized egress or inspection VPCs, connecting on-prem networks (via VPN/Direct Connect) to many VPCs at once, and multi-account/multi-region network topologies in an AWS Organization.

The trade-off, as covered above, is that its convenience (automatic full connectivity by default) is also its main security risk if left unconfigured — it centralizes routing but not enforcement, so segmentation has to be built deliberately through separate route tables rather than assumed.

---
## How can an TGW be a security hole?
Because a Transit Gateway is a **router, not a firewall** — and its defaults are permissive.

**Default association and propagation is the main one.** When you create a TGW, `DefaultRouteTableAssociation` and `DefaultRouteTablePropagation` are enabled. Every new attachment lands in the same route table and propagates its CIDR into it. So VPC A, VPC B, the VPN to the office, and the dev account someone attached last week are all in one flat routing domain. Two subnets that are private in the sense of having no IGW are now fully mutually reachable, and nobody made an explicit decision that they should be. Segmentation on a TGW is expressed *only* through separate route tables, and you get that only if you turn the defaults off and build it deliberately.

**Transitivity removes a property people were relying on.** VPC peering is non-transitive — A↔B and B↔C never gives you A→C. That accidental containment is often the only thing keeping environments apart. TGW is transitive by design, so a shared-services or egress VPC in the middle becomes a path from anything to anything. Same with an on-prem VPN attachment: a laptop on the corporate LAN can now route to prod databases.

**There are no security groups or NACLs at the attachment.** TGW route tables control *reachability*, not *permission*, and their granularity is a CIDR and a blackhole. All actual filtering falls back to security groups and NACLs inside each VPC — and cross-VPC over TGW you can't use security-group references, so people write CIDR rules, and CIDR rules drift toward `10.0.0.0/8`. That's how "allow all inbound" in a private subnet stops being harmless.

**Cross-account attachments shift trust.** Share a TGW via RAM and other accounts can attach their VPCs. If `auto-accept-shared-attachments` is on, they attach without you approving it. Their security posture is now your blast radius, and you don't administer their VPC.

**Asymmetric routing breaks inspection.** If you route traffic through a firewall appliance in an inspection VPC and haven't enabled appliance mode, TGW can hash forward and return flows to appliance ENIs in different AZs. The stateful device sees half a conversation — traffic gets dropped, or worse, someone "fixes" it by relaxing the inspection rules.

**And it's one API call away.** `AssociateTransitGatewayRouteTable` or `CreateTransitGatewayRoute` collapses your segmentation instantly. TGW APIs frequently live in a networking account with looser guardrails than the workload accounts, and route table changes tend not to be reviewed like security group changes are.

For hardening: disable both default-route-table settings, run one route table per segment with explicit propagation, require manual attachment acceptance, put an inspection VPC or AWS Network Firewall in the path with appliance mode enabled, scope the RAM share, restrict the `ec2:*TransitGateway*` actions in IAM, and enable TGW Flow Logs — VPC Flow Logs alone won't show you what the gateway is doing.
