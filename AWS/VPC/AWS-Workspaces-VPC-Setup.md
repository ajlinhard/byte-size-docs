# AWS Workspaces (VPC)
Are Amazon Workspaces automatically inside a VPN or Direct Connect with the VPCs for accounts you are sso'ed into?
No — those are two completely separate planes, and conflating them is a common source of surprise.

**Identity Center (SSO) does nothing for networking.** Signing into an account through IAM Identity Center gets you IAM credentials and console/API access. It creates no routes, no peering, no tunnels. You can be SSO'd into 40 accounts and still have zero network reachability to anything in their VPCs.

## Workspace VPC Basics
**A WorkSpace lives in exactly one VPC.** When you create a WorkSpaces directory, you designate a VPC and subnets in a specific account and region. The WorkSpace gets an ENI in those subnets, so it behaves like an EC2 instance sitting there: it can reach that VPC's CIDR subject to route tables, security groups, and NACLs, and nothing else by default.

(Side note: each WorkSpace actually has a second, management ENI in an AWS-owned address space used for the streaming protocol and health checks. That one isn't yours to route through and doesn't grant you access anywhere.)

**Reaching other VPCs or on-prem is entirely a property of the host VPC.** If the WorkSpaces VPC is attached to a Transit Gateway, peered, or has a VGW with Site-to-Site VPN or Direct Connect, then the WorkSpace inherits that reachability — same as any other instance in that VPC. If it isn't, the WorkSpace is isolated to its own VPC regardless of who's logged in or what permissions they hold. Cross-account VPCs specifically require TGW attachments (often with RAM sharing), peering, or PrivateLink, all of which someone has to build deliberately.

So the practical pattern most orgs land on: put WorkSpaces in a dedicated VPC, attach it to a Transit Gateway in a network account, and use TGW route tables to control which spoke VPCs and on-prem ranges WorkSpaces users can actually reach. That route table becomes your real access boundary — and it's worth noting it's a coarse one. TGW routing is per-VPC, not per-user, so every WorkSpace in that VPC gets the same reachability. If different user populations need different blast radii, you need separate WorkSpaces VPCs (or per-WorkSpace security groups, which is finer-grained but harder to manage at scale).

One more distinction worth keeping straight: the *client-to-WorkSpace* streaming connection (your laptop to the desktop) is a different path from the *WorkSpace-to-your-network* path. Streaming goes to AWS-managed regional gateways over public endpoints by default. There are configurations for carrying that traffic over Direct Connect instead of the internet, but the details have shifted over time — worth checking current AWS docs rather than assuming, since it's independent of whatever VPN or DX your WorkSpaces VPC already has.

---
## Workspace Networking
I want to know why I can see my private ALB DNS automatically in Amazon workspaces but not the public internet?

Two different things are happening, and it's worth separating them: **name resolution** and **packet reachability**.

**Reachability is the easy part.** Every VPC route table has an implicit `local` route covering the VPC CIDR. It can't be removed or overridden. Your WorkSpace has an ENI in that VPC, and the internal ALB has ENIs in that VPC, so traffic between them is routed at layer 3 by default — no NAT, no gateway, no route entry you had to create. The only thing that can stop it is a security group or NACL. That's the "automatically" you're seeing. From the public internet those same private IPs are simply not routable; RFC1918 space doesn't traverse the internet, and there's no listener anywhere public.

**Resolution depends on which name you're using**, and this is where people usually get surprised.

If you're hitting the AWS-assigned name — `internal-myapp-123456789.us-east-1.elb.amazonaws.com` — that record lives in *public* DNS. Anyone on the internet can resolve it and will get your private IPs back. It isn't secret. It's just useless to them, because they can't route to the answer. So if your mental model is "the public internet can't even see this name," that part isn't quite right.

The one wrinkle: some resolvers refuse to return private addresses from public zones as DNS-rebinding protection (dnsmasq's `stop-dns-rebind`, various ISP and home-router resolvers, some corporate filters). If you tested from your laptop at home and got NXDOMAIN or an empty answer, that's likely what you hit — a resolver policy, not an AWS boundary.

If instead you're using a friendly name like `app.internal.example.com` backed by a **Route 53 private hosted zone**, then resolution genuinely is VPC-scoped. A private hosted zone only answers for VPCs it's explicitly associated with. Your WorkSpaces VPC is presumably associated, so the WorkSpace resolves it; the internet has no path to that zone at all. That's a real resolution boundary rather than just a routing one.

To tell which case you're in, run `dig` or `nslookup` against the name from the WorkSpace and note whether the answer chain ends at an `elb.amazonaws.com` name, then try the same query from outside against a resolver you trust — `dig @1.1.1.1 <name>`. Public zone: you'll get private IPs back from both. Private zone: you'll get an answer inside and nothing outside.

One thing to flag regardless of which case applies: don't treat "it's an internal ALB" as the security control. The name and its addresses may well be public knowledge, and the actual boundary is your routing plus the ALB's security group. If that SG allows the whole VPC CIDR — or worse, `0.0.0.0/0` on a VPC that's peered or TGW-attached to a lot of other things — your effective exposure is wider than "internal" suggests. Scope it to the WorkSpaces security group specifically.

---
## How to tell where a Workspace is located?
Good instinct to check — WorkSpaces are frequently deployed in a dedicated end-user-computing account that's separate from the accounts you're SSO'd into, so "my VPC" may well be someone else's.

**Step 1: find the WorkSpace's real private IP.**

A Windows WorkSpace has two network adapters. One is yours; one is the AWS management interface used for the streaming protocol, and it sits in an AWS-reserved range (usually something in `198.19.x.x`, though the exact CIDR varies by region). Ignore that one.

```
ipconfig /all
```

On a Linux WorkSpace:

```
ip -4 addr
ip route
```

The address that looks like normal RFC1918 space — `10.x`, `172.16–31.x`, or `192.168.x` — is your ENI in a customer VPC. Note it, plus the default gateway and the DNS servers listed.

**Step 2: map that IP to an actual VPC.** This is the part that requires the AWS side, because a private IP alone proves nothing — overlapping `10.0.0.0/16` ranges across accounts are extremely common, and a CIDR that "matches" one of your VPCs may be coincidence.

If you have API access to the account hosting the directory:

```
aws workspaces describe-workspace-directories
aws ec2 describe-subnets --subnet-ids subnet-abc123 --query 'Subnets[].{VPC:VpcId,CIDR:CidrBlock,AZ:AvailabilityZone}'
```

The first call returns the directory's `SubnetIds`; the second resolves those to a VPC ID. Same information is in the console under WorkSpaces → Directories. That's the authoritative answer.

**If you can't reach that account**, you're inferring rather than confirming. The most useful signal is your DNS server addresses from `ipconfig /all`. If they're domain controller IPs, the WorkSpace is AD-joined and lives wherever that directory lives. If one is `<vpc-cidr-base>.2`, that's the VPC Resolver and the third octet tells you the VPC's base range. Either way, ask whoever runs the WorkSpaces deployment for the VPC ID — it's a one-line answer for them and guessing here isn't worth it.

There may also be a WorkSpace ID recorded locally under `HKLM\SOFTWARE\Amazon` (the WorkSpaces agent is called SkyLight), which would let an admin look it up directly. Worth a glance, but I wouldn't rely on it being there across bundle versions.

---

**Running the DNS queries.**

On a Windows WorkSpace, `dig` isn't installed. Use the built-ins — `Resolve-DnsName` in PowerShell is more readable than `nslookup`:

```powershell
Resolve-DnsName internal-myapp-123456789.us-east-1.elb.amazonaws.com
Get-DnsClientServerAddress -AddressFamily IPv4
Test-NetConnection internal-myapp-123456789.us-east-1.elb.amazonaws.com -Port 443
```

Or in cmd:

```
nslookup internal-myapp-123456789.us-east-1.elb.amazonaws.com
```

On a Linux WorkSpace, install the tools first if needed (`sudo yum install bind-utils` on Amazon Linux, `sudo apt install dnsutils` on Ubuntu), then:

```
dig +short internal-myapp-123456789.us-east-1.elb.amazonaws.com
curl -sv https://internal-myapp-123456789.us-east-1.elb.amazonaws.com -o /dev/null
```

**Reading the results.** In both `nslookup` and `dig`, the answering server is shown at the top — that tells you whether you went to the VPC Resolver, a domain controller, or somewhere else. If the name resolves to private IPs and `Test-NetConnection`/`curl` succeeds, you have both resolution and routing.

For the external comparison, run the query from a machine genuinely outside AWS rather than pointing the WorkSpace at a public resolver — outbound port 53 to the internet is often blocked in these VPCs, so a failure there would tell you nothing about DNS:

```
dig @1.1.1.1 internal-myapp-123456789.us-east-1.elb.amazonaws.com
```

Getting private IPs back from that is expected and normal for an ALB's AWS-assigned name. Getting nothing back means either a private hosted zone or your local resolver stripping the answer.

--
## Example
```
nslookup internal-entra-basic-basic-alb-dev-alb-1361623625.us-gov-west-1.elb.amazonaws.com

Server:  UnKnown
Address:  10.47.116.2
Non-authoritative answer:
Name:    internal-entra-basic-basic-alb-dev-alb-1361623625.us-gov-west-1.elb.amazonaws.com
Addresses:  10.52.99.251
          10.52.99.123
```
Three concrete things fall out of this.

**Your WorkSpace is in a customer VPC whose CIDR starts at 10.47.116.0.** The resolver at `10.47.116.2` is the VPC Resolver — AWS always places it at the VPC CIDR base plus two. `Server: UnKnown` isn't an error; it just means the reverse lookup for that address returned nothing, which is normal because the VPC Resolver has no PTR record. Had this been an AD domain controller doing your DNS, you'd typically see its hostname instead. So you're on AmazonProvidedDNS in a VPC based at `10.47.116.0/22` or narrower.

**The ALB is not in that VPC.** It answers with `10.52.99.251` and `10.52.99.123` — a different /16 entirely. That means the explanation I gave earlier about the implicit `local` route doesn't apply to your situation. You're crossing a boundary, so if you can actually reach it, someone deliberately built the path: a Transit Gateway attachment, VPC peering, or similar, plus matching route table entries on both sides and a security group on the ALB that permits your range. This is inherited plumbing, not something that happened automatically.

(Two addresses means the ALB has nodes in two Availability Zones — standard for an internal ALB, not significant here.)

**This resolution tells you nothing about privacy.** You queried the AWS-assigned name, which lives in public DNS. Your VPC Resolver forwarded it upstream and got back the private addresses. Anyone querying that same name from anywhere would get the same answer — the record isn't scoped to your VPC. If a Route 53 private hosted zone were involved you'd be using a friendly internal name, not this one. So the "internal" in the ALB name describes where its IPs are routable, not who can discover them.

**Resolution isn't reachability.** You've confirmed DNS works; you haven't confirmed packets flow. Test that separately:

```powershell
Test-NetConnection 10.52.99.251 -Port 443
```

If that succeeds, the cross-VPC path is real and the ALB's security group admits you. If it hangs or fails, you have name resolution without a route — which is exactly the failure mode this setup produces, and it points at TGW route tables or the ALB security group rather than at DNS.

Worth confirming the VPC ID properly rather than inferring from the CIDR, since `10.47.116.x` doesn't identify an account. `aws workspaces describe-workspace-directories` in the account hosting the directory, or asking whoever operates the WorkSpaces deployment, will settle it in one step.

## How is the Example AWS Workspace Communicates
Short Answer:  a transit gateway in your VPC jas a owner id is "shared"

Look at the TGW ARN to see a TGW whose owner account isn't yours: owner IDs are always 12-digit account numbers, never the literal string "shared." What you're likely looking at is either a different account number than the one you're in, or a console indicator marking the resource as shared with you.

**ARN structure.** Since you're in `us-gov-west-1`, note the partition is `aws-us-gov`, not `aws` — this trips people up in IAM policies constantly:

```
arn:aws-us-gov:ec2:us-gov-west-1:123456789012:transit-gateway/tgw-0a1b2c3d4e5f
 |      |       |        |            |              |            |
 |      |       |        |            |              |            └─ resource ID
 |      |       |        |            |              └─ resource type
 |      |       |        |            └─ account ID (the owner)
 |      |       |        └─ region
 |      |       └─ service namespace (TGWs live under ec2)
 |      └─ partition
 └─ literal "arn"
```

Related resources follow the same shape with different resource types: `transit-gateway-attachment/tgw-attach-…`, `transit-gateway-route-table/tgw-rtb-…`, `transit-gateway-connect-peer/…`.

**The account field is the ownership answer.** If it's not your account, the TGW lives in another account — almost certainly a central networking or shared-services account — and was shared to you through AWS Resource Access Manager. Check RAM → Shared with me → Resources to see the share and who sent it.

**What that ownership split actually means for you:**

You can attach your VPC to that TGW, and your attachment is a separate resource that *you* own. So it's normal to see two different account IDs side by side — the attachment ARN carrying your account, the TGW ARN carrying theirs.

What you can't do is control routing. TGW route tables belong to the owner. You can't view them, edit them, or add propagations. Whether your WorkSpaces VPC can reach that `10.52.99.x` ALB is decided entirely in the owning account, which is why it appeared to work "automatically" from your side — the plumbing predates you and isn't yours to inspect.

Attachment creation typically requires the owner to accept it, unless they've enabled auto-accept on the share.

**Practically:** The WorkSpace in `10.47.116.x` reaches the ALB in `10.52.99.x` because a shared TGW in another account has route table entries connecting them. If reachability ever breaks, or you need a new destination added, it's a request to the networking account rather than something you can fix in your own VPC. Worth identifying that team now if you haven't.
