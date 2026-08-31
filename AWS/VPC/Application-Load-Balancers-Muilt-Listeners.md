# ALBs with multiple Listeners
The overwhelmingly common case is the first one; everything after it is a real but narrower reason.

**1. HTTP :80 + HTTPS :443 — the near-universal pattern.** The :80 listener exists purely to issue a 301 redirect to HTTPS. You need a separate listener because a listener is bound to one protocol/port pair, and you can't serve plaintext and TLS on the same port.

**2. Different TLS or client-auth requirements for different surfaces.** This is the strongest architectural reason. Several settings are *listener-level*, not rule-level:

- **mTLS mode and trust store.** You can't require client certs on `/admin` but not `/public` within one listener. If you need a cert-authenticated surface alongside an anonymous one, that's :443 (no mTLS) plus :8443 (verify mode with a trust store).
- **Security policy.** If a partner integration must be pinned to a FIPS or CNSA policy while your public site stays broadly compatible, that's two listeners.
- **Listener attributes** — HSTS, CSP, X-Frame-Options header values, mTLS header renaming — are all per-listener.

**3. Blue/green deployment with CodeDeploy.** The canonical setup uses a production listener (:443) and a separate test listener (:8443) pointed at the green target group, so you can validate the new version with real traffic patterns before the atomic swap.

**4. Distinct services on distinct ports.** A public API on :443 and an internal admin console on :8443 whose default rule is a `fixed-response` 403 with a `source-ip` condition allowing only your VPN CIDR. Port separation is cleaner than path separation when the two have different security postures, and it means a rule misconfiguration on one can't accidentally expose the other.

**5. Legacy port compatibility.** Clients hardcoded to :8080 during a migration, running alongside the modern :443 listener.

**6. gRPC alongside REST**, if you'd rather separate them by port than by path — gRPC needs HTTPS and a `GRPC` protocol-version target group, and forward is the only supported action there.

**Two things to watch:**

- The **100-rule quota is per load balancer, not per listener.** Two listeners split that 100 between them, which is exactly the trap in the EKS `group.name` consolidation pattern.
- If your only goal is serving multiple hostnames, **don't** add listeners — use SNI (up to 25 extra certs on one HTTPS listener) plus `host-header` rules. Adding listeners for that just burns ports and complicates security groups.
