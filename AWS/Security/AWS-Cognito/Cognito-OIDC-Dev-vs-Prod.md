# AWS Cognito OIDC in Dev vs Prod
Good instinct to ask now rather than after you've hard-coded assumptions. Let me start with a reframe that makes the choice much easier, then walk the options.

## First: figure out how much fidelity you actually need

Look back at the flow. Everything from step 5 onward — Cognito's tokens, API Gateway validation, your backend claims — is **identical regardless of what's upstream**. Cognito normalizes it. So the only thing a fake Entra buys you is coverage of one narrow, rarely-changing seam:

| What varies with the upstream IdP | Do you need real Entra to test it? |
|---|---|
| Cognito attribute mapping config | Only need matching **claim names**, not real Entra |
| The `identities` claim shape in Cognito's ID token | Any OIDC provider produces this |
| Group/role claims and the overage problem | Need an IdP that can emit many groups |
| Conditional Access, MFA prompts, tenant policies | **Yes** — nothing else reproduces these |
| Consent screens, admin consent, app registration permissions | **Yes** |
| Everything downstream (API Gateway, backend, scopes) | **No** — never varies |

That last row is most of your day-to-day work. So the answer is almost certainly a *layered* setup, not one substitute.

## Option A — Your own free Entra tenant (highest fidelity)

You can create a personal Entra ID tenant for free from the Azure portal. Entra ID Free tier includes app registrations, OIDC/OAuth endpoints, users, and security groups — all the pieces this flow touches. You control it completely, so you can create `alice@yourdevtenant.onmicrosoft.com`, put her in groups, and script user creation via Microsoft Graph.

**This is the option I'd push for.** It's the only one where the URLs, claim names, `oid`/`tid` semantics, group GUID behavior, and error responses are the real thing.

Two caveats: Conditional Access and MFA enforcement need a P1/P2 license (there's a trial, and P2 features are what break auth in surprising ways), and the Microsoft 365 Developer Program that used to hand out free sandbox tenants tightened eligibility a while back — worth checking current terms rather than assuming.

Also worth a separate conversation: ask your identity team whether the org already has a non-prod tenant, or whether they'll issue you a **separate app registration in the prod tenant** scoped to dev redirect URIs. That's a common and reasonable ask, and it's often easier to get than people expect. "I need access to prod Entra" gets a no; "I need an app registration with `localhost` redirect URIs and three test accounts" often gets a yes.

## Option B — Cognito federating to a second Cognito user pool

Cognito can act as an OIDC provider to another Cognito user pool. Pool A is your "fake Entra," Pool B is your real app pool, federated to A.

It works, and it's all inside AWS with no new infrastructure to run. But the claims are wrong in ways that matter: no `oid`, no `tid`, `preferred_username` semantics differ, and group claims work completely differently. Your dev attribute mapping ends up **structurally different from prod**, which defeats a large part of the point — you'd be testing a config you don't ship.

Practical note if you try it: give Pool A's app client a secret (Cognito requires one for federation), and be prepared to enter the authorize/token/userinfo/JWKS endpoints manually rather than trusting auto-discovery to populate them.

I'd only pick this if you can't get any Entra tenant at all and you need the federation code path exercised.

## Option C — Self-hosted mock OIDC provider

Keycloak, Dex, or Navikt's `mock-oauth2-server` (the lightest of the three, purpose-built for tests) give you a fully controllable IdP. The big win: you can configure them to emit **exactly Entra's claim names** — `oid`, `tid`, `preferred_username`, `groups` — so your Cognito attribute mapping config is byte-identical to production. You can also generate 300 groups in a script to reproduce the overage behavior, which is genuinely hard to test otherwise.

**The constraint that trips everyone up:** Cognito reaches your IdP over the public internet, server-to-server. `localhost:8080` will never work. You need either a tunnel (ngrok, Cloudflare Tunnel) or the mock deployed somewhere reachable with valid TLS — App Runner or a small ECS service is enough. That's real infrastructure to maintain, which is the cost of this option.

## Option D — Skip federation in dev; use native Cognito users

Create ordinary users directly in your dev user pool. No IdP at all. Log in via the hosted UI or `USER_PASSWORD_AUTH`.

The tokens are ~95% identical to federated ones — the differences are the `identities` claim (absent) and the username format. Everything you're actually building against is the same.

This is unglamorous and it's what most teams end up doing for the inner loop, correctly. It's fast, free, scriptable, and has no moving parts. Pair it with something from A or C for the seam you're not covering.

## Option E — Bypass AWS entirely for the fastest loop

A local JWT issuer plus a local API, no Cognito, no API Gateway. Mint tokens with the same claim shape and validate them with a local JWKS. Sub-second feedback for backend logic.

The trap: you're now testing *your* validation code, not API Gateway's authorizer, and those disagree in real ways (ID vs access token expectations, scope enforcement, error format). Fine for unit-testing business logic that reads claims; not a substitute for integration testing. Note also that Cognito emulation in LocalStack is a paid-tier feature, so "just run it locally" isn't as cheap as it sounds.

## What I'd actually build

**Three tiers, and be deliberate about which one a given change needs:**

1. **Inner loop (all day, every day)** — native Cognito users in a dev pool, or local fixture tokens for pure backend work. Option D or E.
2. **Integration environment (CI, PR checks)** — dev Cognito pool federated to your own free Entra tenant, or to a hosted mock emitting Entra-shaped claims. Option A or C.
3. **Staging** — real corporate Entra via a dedicated app registration. This is where MFA, Conditional Access, and consent actually get exercised. Push for this even if it takes a few weeks of asking.

Three things that will save you pain regardless of which you pick:

**Parameterize the IdP config in IaC** (Terraform/CDK), so dev and prod differ only in issuer URL, client ID, and secret. If the *shape* of the config differs between environments, you're not testing what you ship.

**Capture a real Entra ID token as a redacted fixture** the first time you get access to any real tenant. Save the decoded claim structure into your repo and write a test asserting your mapping logic handles it. This catches "we assumed `email` would always be present" — it isn't, for guest accounts and some account types.

**Write down what you're knowingly not testing.** Conditional Access blocking a login, MFA challenge mid-flow, an expired Entra session, group overage, and guest/B2B accounts with weird claim shapes are the realistic production surprises. If they're on a list, they get handled at staging instead of at 2am.
