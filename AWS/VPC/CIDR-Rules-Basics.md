# CIDR Rules Basics
CIDR notation is just "address + how many leading bits are fixed."

`10.0.0.0/24` means the first 24 bits are the fixed part; the remaining 8 bits are free to be anything. So the block covers `10.0.0.0` through `10.0.0.255` — 256 addresses. A packet matches a rule if its address shares those first N bits.

The counterintuitive part: **smaller prefix = bigger range.**

| CIDR | Addresses | Example span |
|---|---|---|
| `/32` | 1 | exactly `203.0.113.7` |
| `/28` | 16 | `.0`–`.15` |
| `/24` | 256 | `10.0.0.0`–`10.0.0.255` |
| `/16` | 65,536 | `10.0.0.0`–`10.0.255.255` |
| `/8` | 16.7M | all of `10.x.x.x` |
| `/0` | everything | any address |

The math is `2^(32 − prefix)`.

**Reading non-octet boundaries.** For something like `/26`, take `2^(8 − (26 mod 8))` = 64. That's the block size in the last octet, so valid blocks are `.0–.63`, `.64–.127`, `.128–.191`, `.192–.255`. The netmask octet is `256 − 64 = 192`, i.e. `255.255.255.192`.

**Where people get bitten:**

- **Blocks must be aligned.** `10.0.0.5/24` isn't meaningful — host bits should be zero. Some tools reject it, others silently round it down to `10.0.0.0/24`, which then allows far more than you intended.
- **Arbitrary ranges don't fit one block.** `.10` through `.20` can't be expressed as a single CIDR; you need several, or a tool that takes ranges.
- **Evaluation order varies by system.** AWS security groups are allow-only and take the union of all rules — there's no deny, and anything not explicitly allowed is dropped. Network ACLs are numbered, stateless, and first-match-wins, so a broad deny at rule 100 shadows a narrow allow at rule 200. `iptables` is also first match. Routing tables, by contrast, use *longest prefix match*, so the most specific route wins regardless of order.
- **`0.0.0.0/0` is "the entire internet."** Common in outbound rules, dangerous on inbound SSH.
- **IPv6 shifts the numbers.** `/128` is a single host, `/64` is a typical subnet, and `::/0` is everything.

A practical habit: when writing a deny rule, check whether your system is stateful. Security groups automatically allow return traffic; NACLs don't, so blocking an inbound range there can also break responses to your own outbound connections if the ephemeral port range isn't allowed back in.
