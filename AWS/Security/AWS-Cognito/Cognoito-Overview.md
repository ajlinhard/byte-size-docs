# Amazon Cognito User Pools — In-Depth Feature Guide

> **Scope note.** This document covers **Amazon Cognito user pools**. The features requested
> — user pools, users and groups, custom attributes, WAF, threat protection, and log streaming —
> are Cognito features, not Application Load Balancer features. ALB's relationship to them is the
> `authenticate-cognito` listener action, which is covered in [Section 10](#10-application-load-balancer-integration).
>
> Researched against AWS documentation current as of **August 2026**. Pricing and quota numbers
> change; verify against the [Cognito pricing page](https://aws.amazon.com/cognito/pricing) and the
> Service Quotas console before making commitments.

---

## Table of contents

1. [What a user pool is](#1-what-a-user-pool-is)
2. [Feature plans: Lite, Essentials, Plus](#2-feature-plans-lite-essentials-plus)
3. [User pool anatomy](#3-user-pool-anatomy)
4. [Users](#4-users)
5. [Groups](#5-groups)
6. [Attributes and custom attributes](#6-attributes-and-custom-attributes)
7. [Security: AWS WAF](#7-security-aws-waf)
8. [Security: threat protection](#8-security-threat-protection)
9. [Security: log streaming and export](#9-security-log-streaming-and-export)
10. [Application Load Balancer integration](#10-application-load-balancer-integration)
11. [Recent changes worth knowing](#11-recent-changes-worth-knowing)
12. [Design checklist and common traps](#12-design-checklist-and-common-traps)
13. [References](#13-references)

---

## 1. What a user pool is

A user pool is a managed user directory that doubles as an **OpenID Connect identity provider**.
From your application's perspective it is an OIDC issuer: your app performs an OAuth 2.0 /
OIDC flow and gets back JWTs.

Two kinds of user live in a pool:

| Kind | Origin | Notes |
|---|---|---|
| **Local users** | Signed up directly, or created by an administrator | Password and MFA factors stored in Cognito |
| **Federated users** | Signed in via a third-party IdP (Google, Apple, Facebook, Amazon, any SAML 2.0 or OIDC provider) | Cognito auto-generates a `username`; the profile is a projection of IdP claims |

The value of federation here is normalization: Cognito accepts assertions and tokens from
external IdPs, maps their claims into a single token format, and hands your app one consistent
set of JWTs regardless of how the user signed in.

**User pools vs. identity pools.** These are separate halves of Cognito and are frequently confused.

- **User pool** — authentication and a user directory. Issues JWTs (ID, access, refresh).
- **Identity pool** (federated identities) — authorization *to AWS services*. Exchanges a token
  (from a user pool or another provider) for temporary IAM credentials via STS.

You need an identity pool only when the client itself must call AWS APIs directly (S3, DynamoDB,
etc.). If your backend does that work, a user pool alone is enough.

### Tokens

| Token | Purpose | Notable claims |
|---|---|---|
| **ID token** | Identity of the user; consumed by your app | Standard OIDC claims, custom attributes (always serialized as strings), `cognito:groups`, `cognito:preferred_role`, `cognito:roles` |
| **Access token** | Authorization; sent to APIs | `scope`, `client_id`, `username`, `cognito:groups` |
| **Refresh token** | Obtain new ID/access tokens | Rotation supported since April 2025 |

---

## 2. Feature plans: Lite, Essentials, Plus

In November 2024 Cognito replaced the old "advanced security features" (ASF) add-on pricing with
three per-pool feature plans. **The plan is a property of the user pool, not the account and not the
app client.** Different pools in the same account can use different plans, and you can switch a
pool between plans at any time — though switching down requires you to first turn off any features
the lower plan doesn't include.

| Plan | Positioning |
|---|---|
| **Lite** | Basic directory and authentication. Everything user pools could do before Nov 22, 2024, minus ASF. Classic hosted UI only. |
| **Essentials** | **Default for new pools.** All current authentication features: managed login, passkeys, email OTP, choice-based sign-in, access-token customization, password-reuse prevention. |
| **Plus** | Essentials + threat protection: compromised-credentials detection, adaptive authentication, user activity logging and log export. |

### Features by plan

Taken from the AWS feature-plan comparison table:

| Feature | Plan |
|---|---|
| Protect against unsafe passwords (compromised-credentials detection) | **Plus** |
| Protect against malicious sign-in attempts (adaptive auth) | **Plus** |
| Log and analyze user activity (session properties + risk scores) | **Plus** |
| Export user activity logs to an external AWS service | **Plus** |
| Managed login visual branding editor | Essentials, Plus |
| MFA with email one-time codes | Essentials, Plus |
| Customize **access** token scopes and claims at runtime | Essentials, Plus |
| Passwordless sign-in with email/SMS one-time codes | Essentials, Plus |
| Passkey (FIDO2) sign-in | Essentials, Plus |
| Sign-up and sign-in | All |
| **User groups** | All |
| Social, SAML, and OIDC federation | All |
| OAuth 2.0 / OIDC authorization server | All |
| Login pages (classic hosted UI all plans; managed login Essentials+) | All |
| Password, custom, SRP, refresh-token auth | All |
| M2M with client credentials | All |
| Resource servers and custom scopes | All |
| User import (CSV) and just-in-time migration | All |
| MFA with authenticator apps and SMS | All |
| Customize **ID** token claims at runtime | All |
| Lambda triggers | All |
| Managed login CSS customization | All |

Two things people trip on:

- **Access-token customization is Essentials+, ID-token customization is on every plan.** If you
  need custom scopes injected into access tokens at runtime, you need at least Essentials
  (pre-token-generation trigger event versions V2/V3).
- **Groups are available on every plan**, including Lite. Group-based authorization does not
  require an upgrade.

### Setting the plan

```bash
# Create
aws cognito-idp create-user-pool \
  --pool-name my-pool \
  --user-pool-tier PLUS

# Switch an existing pool
aws cognito-idp update-user-pool \
  --user-pool-id us-west-2_EXAMPLE \
  --user-pool-tier ESSENTIALS
```

The API parameter is `UserPoolTier` with values `LITE | ESSENTIALS | PLUS`. If you omit it, the pool
defaults to `ESSENTIALS`. If you set `AdvancedSecurityMode` to `AUDIT` or `ENFORCED`, the pool must
be — and will default to — `PLUS`.

### Pricing shape

Billing is by **monthly active user** (MAU): a user with authentication, update, or query activity
in the month. Dormant accounts cost nothing. Cost drivers:

- The plan you choose
- MAU count, with separate (higher) rates for SAML/OIDC federated MAUs
- App clients and pools doing M2M client-credentials grants
- Requests per second above the default rate limit (provisioned capacity)

Lite and Essentials both have a free tier that does not expire. Note the significant gotcha:
pools created before November 22, 2024 had a **50,000 MAU** free tier, while the current free tier
is **10,000 MAU**. Changing the plan on a legacy pool can drop it to the smaller free tier — a
40,000-MAU app can go from $0 to several hundred dollars a month on a plan switch. Check this before
touching the tier on an old pool.

---

## 3. User pool anatomy

### Immutable-at-creation decisions

These cannot be changed after the pool is created. Getting them wrong means building a new pool and
migrating users with a `UserMigration` Lambda trigger.

| Decision | Why it's permanent |
|---|---|
| **Sign-in identifiers** (username / email / phone / preferred_username; alias vs. username attributes) | Fixed at create time |
| **Required standard attributes** | You can't switch an attribute between required and not-required afterward |
| **Case sensitivity of usernames** | Fixed at create time |

Everything else — app clients, IdPs, Lambda triggers, MFA settings, custom attributes (additive
only), branding, feature plan — is changeable later.

### Alias attributes vs. username attributes

| Requirement | Alias attributes | Username attributes |
|---|---|---|
| Users have multiple sign-in identifiers | Yes (username, email, phone, preferred_username) | No (email or phone only) |
| Must verify email/phone before signing in with it | Yes | No |
| Avoids `UsernameExistsException` on sign-up with duplicate email/phone | Yes | No |
| Same email/phone value on more than one account | Yes — but only the last user to verify it can sign in with it | No |

Critical rule regardless of which you pick: **never key your application data on a sign-in
attribute.** `email`, `phone_number`, and `preferred_username` can all change or transfer between
accounts. `sub` is the only stable identifier. Also, don't strictly validate `sub` as an RFC UUID —
Cognito generates it in a Cognito-specific format.

An alias transfer scenario worth understanding: if user B verifies an email address that is already
a verified alias on user A's account, Cognito moves the alias to B and marks it unverified on A.
Via `VerifyUserAttribute` this happens silently, with no `AliasExistsException`.

### App clients

An app client is a per-application set of rules against the same directory. Each client
independently configures:

- Allowed authentication flows (SRP, password, custom, refresh, passwordless, passkey)
- OAuth grants, callback/logout URLs, and allowed scopes
- Supported identity providers
- Token validity (ID, access, refresh) and refresh-token rotation
- **Attribute read/write permissions** (see [Section 6](#6-attributes-and-custom-attributes))
- Optionally, its own threat-protection configuration

Confidential clients have a secret; public clients (SPAs, mobile) should not.

### Domains and login pages

- **Classic hosted UI** — the older, minimally customizable sign-in pages. Available on all plans.
- **Managed login** — the successor, with a no-code visual branding editor. Requires Essentials or Plus.

Both are served from either a Cognito prefix domain (`https://<prefix>.auth.<region>.amazoncognito.com`)
or a custom domain with an ACM certificate.

### Lambda triggers

Available on every plan (except that pre-token-generation V2/V3 event versions require Essentials+):

| Category | Triggers |
|---|---|
| Sign-up | Pre sign-up, Post confirmation, Custom message |
| Authentication | Pre authentication, Post authentication, Pre token generation |
| Custom auth | Define auth challenge, Create auth challenge, Verify auth challenge response |
| Migration | User migration |
| Messaging | Custom SMS sender, Custom email sender |

The **pre sign-up** trigger is the standard place to sanitize or validate attribute values before
they enter the directory.

### Resource servers, scopes, and M2M

Define a resource server with an identifier (typically your API's URL) and custom scopes in
`resource-server-id/scope-name` format. App clients configured for the client-credentials grant get
access tokens carrying those scopes — this is the machine-to-machine path, and it's billed separately
from MAU.

### Rate limits and provisioned capacity

Cognito enforces request-rate quotas per Region per account, grouped into operation categories
(`UserAuthentication`, `UserCreation`, `UserRead`, and so on). Since **July 6, 2026**, the console
has a **Provisioned limits** tab at the account level, letting you raise or lower provisioned
capacity on demand with changes taking effect immediately. You're billed for provisioned capacity
above the default whether or not you use it. Separately, Service Quotas holds the account-level
ceiling — raising the ceiling is free, and roughly 90% of increase requests are auto-approved
within minutes.

This replaced a support-ticket process that used to take up to two weeks — relevant if you're
planning for a launch or seasonal traffic spike.

### Multi-Region replication

Since **May 2026**, user pools support multi-Region replication: user profiles, credentials, pool
configuration, and federation setup sync in near real time to a standby pool in a secondary Region.
Replication is one-directional, primary to secondary. On a regional disruption you redirect traffic
to the secondary; signed-in users keep their sessions and registered users sign in with existing
credentials. This runs on a next-generation storage backend and supports customer-managed KMS keys.

Before this, DR for Cognito meant hand-rolling a replication pipeline. If you have an existing
custom pipeline, this is worth revisiting.

---

## 4. Users

### Lifecycle and status

| Status | Meaning |
|---|---|
| `UNCONFIRMED` | Signed up, not yet confirmed |
| `CONFIRMED` | Normal, active |
| `FORCE_CHANGE_PASSWORD` | Created by an admin with a temporary password |
| `RESET_REQUIRED` | Must reset password before signing in — **this is what threat protection sets when it blocks a compromised credential** |
| `EXTERNAL_PROVIDER` | Federated user |
| `ARCHIVED` / `COMPROMISED` / `UNKNOWN` | Legacy or system-assigned states |

`Enabled` is a separate boolean from status: disabling a user blocks sign-in without deleting the profile.

### Self-service vs. administrative APIs

| Operation | Self-service (access token) | Administrative (IAM credentials) |
|---|---|---|
| Create | `SignUp` | `AdminCreateUser` |
| Confirm | `ConfirmSignUp` | `AdminConfirmSignUp` |
| Read | `GetUser` | `AdminGetUser` |
| Update attributes | `UpdateUserAttributes` | `AdminUpdateUserAttributes` |
| Password reset | `ForgotPassword` → `ConfirmForgotPassword` | `AdminSetUserPassword` |
| Sign out | `GlobalSignOut` | `AdminUserGlobalSignOut` |
| Delete | `DeleteUser` | `AdminDeleteUser` |

Two behavioral differences that matter:

- `GetUser` returns only attributes the **calling app client** can read. Attribute permissions are
  enforced at read time, not just write time.
- `AdminCreateUser` can create a user **without values for required attributes** — the only way to
  bypass that constraint.
- Admins can force `email_verified` / `phone_number_verified` to `true` via
  `AdminUpdateUserAttributes`. App clients can never be granted write access to those two attributes.

### Searching for users

`ListUsers` supports filters on standard attributes. Two constraints to design around:

- **You cannot filter `ListUsers` by custom attributes.** If you need to query users by a custom
  field, mirror it into DynamoDB or another store.
- If the pool uses username attributes (email/phone as username), filtering by `username` requires
  the generated UUID, not the email address. Filter on `email` or `phone_number` instead.

### Getting users in

- **CSV import** — `CreateUserImportJob`, using a header template retrieved from
  `GetCSVHeader`. Imported users land in `RESET_REQUIRED`; passwords cannot be imported.
- **Just-in-time migration** — a `UserMigration` Lambda trigger fires on first sign-in or first
  forgot-password, letting you validate credentials against a legacy system and create the Cognito
  profile transparently. This is the tool for migrating between pools when you need to change an
  immutable setting.

---

## 5. Groups

Groups are a lightweight, flat authorization primitive. Available on **all plans**.

### Properties

| Property | Description |
|---|---|
| `GroupName` | Unique within the pool; immutable |
| `Description` | Free text |
| `Precedence` | Non-negative integer; **0 is the highest precedence**. Default `null`. Max `2^31 - 1` |
| `RoleArn` | IAM role associated with the group, for identity-pool credential decisions |

### How groups reach your application

Membership appears in **both the ID token and the access token**:

```json
{
  "cognito:groups": ["admins", "beta-testers"],
  "cognito:roles": ["arn:aws:iam::111122223333:role/AdminRole"],
  "cognito:preferred_role": "arn:aws:iam::111122223333:role/AdminRole"
}
```

- `cognito:groups` — every group the user belongs to. Present in ID **and** access tokens.
- `cognito:roles` — the role ARNs of those groups.
- `cognito:preferred_role` — the role ARN of the **lowest-precedence-value** group.

Because groups are in the access token, they're directly usable for API authorization — API Gateway
Cognito authorizers, custom JWT authorizers on HTTP APIs, ALB-forwarded claims, or a policy engine
like Amazon Verified Permissions.

### Precedence rules

Lower value wins. Groups with a numeric precedence beat groups with `null`.

Tie-breaking is specific and easy to get wrong:

- Two groups with the **same precedence** → neither wins.
- Same precedence, **same role ARN** → that role is used for `cognito:preferred_role`.
- Same precedence, **different role ARNs** → `cognito:preferred_role` is **omitted entirely** from
  the token. Application code that assumes the claim exists will break.

Leave deliberate gaps in your precedence numbering (0, 10, 20, 30) so you can insert groups later.

An identity pool can also be told to use a specific role via the `CustomRoleARN` parameter of
`GetCredentialsForIdentity`, as long as that role is one available to the user.

### Limitations

- **No nesting.** The hierarchy is flat.
- **You cannot search for users within a group.** `ListUsersInGroup` paginates; it doesn't filter.
- **You cannot search for groups by name** — only list them.
- Group count is bounded by Cognito service quotas (check the Service Quotas console for the
  current default in your Region).

For anything requiring hierarchy, attribute-based rules, or fine-grained resource permissions,
groups are the wrong tool — use Amazon Verified Permissions or your own authorization layer, and
treat the group claim as one input.

### Managing groups

```bash
aws cognito-idp create-group \
  --user-pool-id us-west-2_EXAMPLE \
  --group-name admins \
  --description "Application administrators" \
  --precedence 0 \
  --role-arn arn:aws:iam::111122223333:role/CognitoAdminRole

aws cognito-idp admin-add-user-to-group \
  --user-pool-id us-west-2_EXAMPLE \
  --username jane@example.com \
  --group-name admins
```

CloudFormation resource: `AWS::Cognito::UserPoolGroup`. CDK: `cognito.UserPoolGroup` or
`userPool.addGroup()`.

---

## 6. Attributes and custom attributes

### Standard attributes

Drawn from the OpenID Connect standard claims:

`name`, `family_name`, `given_name`, `middle_name`, `nickname`, `preferred_username`, `profile`,
`picture`, `website`, `gender`, `birthdate`, `zoneinfo`, `locale`, `updated_at`, `address`,
`email`, `phone_number`, `sub`

Defaults and constraints:

- Values may be any string up to **2048 characters** unless the attribute has a format restriction.
- Every attribute except `sub` is **optional by default**.
- Only `email` and `phone_number` can be **verified**.
- `birthdate` must be exactly `YYYY-MM-DD` (10 characters).
- `phone_number` must be `+` followed by country code and digits only — no spaces, parentheses, or
  dashes. `+14325551212`, not `+1 (432) 555-1212`.
- **You cannot change an attribute between required and not-required after pool creation.**

You can modify standard-attribute *properties* (data type, mutability, length constraints, required)
only via the `Schema` parameter of `CreateUserPool` — the console won't let you do it.

`username` is separate from `name` and is immutable after creation. `preferred_username` exists
precisely so users can have a changeable display/sign-in handle.

### Custom attributes

The core deep-dive. Custom attributes carry a mandatory `custom:` prefix in tokens, IAM RBAC rules,
and API calls.

**Limits and rules**

| Rule | Detail |
|---|---|
| Maximum count | **50 per user pool** |
| Value length | Configurable min/max, but never more than **2048 characters** |
| Name length | Bounded by Cognito quotas; the name must match the `SchemaAttributeType.Name` regex |
| Data types | `String`, `Number`, `Boolean`, `DateTime` |
| Can be required? | **No.** You can never require a value for a custom attribute |
| Deletable? | **No.** Never. |
| Renameable? | **No.** |
| Type changeable? | **No.** |
| Batch size | `AddCustomAttributes` accepts up to **25** attributes per call |

**The console only offers String and Number.** `Boolean` and `DateTime` are available exclusively
through the `SchemaAttributes` property of `CreateUserPool` / `UpdateUserPool` API requests. Also
note that regardless of declared type, **Cognito writes custom attribute values into the ID token
as strings** — `"custom:isMember": "true"`, `"custom:yearsAsMember": "12"`. Your app must coerce
types on read.

**Mutable vs. immutable**

- **Mutable** — value can be changed at any time by anyone with write permission on that app client.
- **Immutable** — value can be written **exactly once, at user creation**. Three ways to populate one:
  1. `SignUp`, from an app client with write access to the attribute
  2. `AdminCreateUser`, providing the value
  3. IdP attribute mapping on first federated sign-in

That third path is a trap. If you map an IdP claim to an **immutable** attribute, Cognito attempts
to rewrite it on *every* subsequent sign-in and throws an error, permanently locking the user out
after their first session. **Any attribute that receives an IdP claim mapping must be mutable.**

**Creating them**

```bash
aws cognito-idp add-custom-attributes \
  --user-pool-id us-west-2_EXAMPLE \
  --custom-attributes \
    'Name=department,AttributeDataType=String,Mutable=true,StringAttributeConstraints={MinLength=2,MaxLength=64}' \
    'Name=tenantId,AttributeDataType=String,Mutable=false,StringAttributeConstraints={MinLength=1,MaxLength=64}'
```

CloudFormation, including the types the console won't give you:

```yaml
Resources:
  MyUserPool:
    Type: AWS::Cognito::UserPool
    Properties:
      UserPoolName: production-user-pool
      Schema:
        - Name: email
          AttributeDataType: String
          Required: true
          Mutable: true
        - Name: department          # becomes custom:department
          AttributeDataType: String
          Mutable: true
          StringAttributeConstraints:
            MinLength: "2"
            MaxLength: "64"
        - Name: employeeId          # becomes custom:employeeId
          AttributeDataType: Number
          Mutable: false
          NumberAttributeConstraints:
            MinValue: "1000"
            MaxValue: "999999"
        - Name: onboardedAt         # API/CFN only — not available in console
          AttributeDataType: DateTime
          Mutable: true
```

Reading and writing:

```bash
# Admin write
aws cognito-idp admin-update-user-attributes \
  --user-pool-id us-west-2_EXAMPLE \
  --username jane@example.com \
  --user-attributes Name="custom:department",Value="engineering"
```

**Developer-only attributes (`dev:`)** are a legacy feature. They're read-only to all app clients
and writable only with IAM-authenticated calls. AWS explicitly recommends app-client `WriteAttributes`
permissions instead. Don't use `dev:` in new designs — and note they can only be created at
`CreateUserPool` time.

### Attribute permissions and scopes

Per app client, every standard and custom attribute has independent **read** and **write** permissions.

- New app clients default to read + write on everything. Tighten this deliberately.
- **New custom attributes are unavailable to an app client until you explicitly grant permissions** —
  add the attribute, then update every app client that needs it. This is the single most common
  "why is my custom attribute missing from the token" cause.
- A write to an unauthorized attribute returns `NotAuthorizedException`.
- `GetUser` returns only readable attributes; the ID token contains only claims for readable attributes.
- `email_verified` and `phone_number_verified` can never be app-client-writable.
- `DescribeUserPoolClient` returns `ReadAttributes` / `WriteAttributes` **only** when you've
  configured something other than the default — an empty response means "everything," not "nothing."

**Scope shorthand.** Via SDK, CDK, CLI, or REST (not the console), you can set `ReadAttributes` or
`WriteAttributes` to `oidc:profile`, which covers `name`, `family_name`, `given_name`, `middle_name`,
`nickname`, `preferred_username`, `profile`, `picture`, `website`, `gender`, `birthdate`, `zoneinfo`,
and `locale` — the OIDC profile scope minus `email`, `phone_number`, `sub`, and `address`. You can
combine it with individually named attributes.

Attribute permissions **can** be changed after pool creation, on a live pool.

### What not to put in attributes

AWS's own guidance: don't store everything about a user in attributes. Keep frequently changing data
(usage counters, scores, session state, large JSON blobs) in DynamoDB or similar, and store only a
reference in Cognito.

Practical reasons this matters more than it sounds:

- The 50-attribute cap is permanent and unrecoverable — you can never free a slot.
- You can't query users by custom attribute.
- Every readable attribute inflates the ID token, and oversized tokens break headers and cookies —
  including ALB's `AWSELBAuthSessionCookie`, which is sharded across multiple cookies as it grows.

Sanitize attribute string values before submitting them. A pre sign-up Lambda trigger is the
recommended interception point.

---

## 7. Security: AWS WAF

You can associate a **regional AWS WAFv2 web ACL** directly with a user pool. Cognito forwards
selected non-confidential headers and request content to WAF, WAF evaluates its rules, and returns a
verdict.

WAF support for **managed login** endpoints was added June 26, 2025 — before that, coverage was
narrower.

### What gets inspected

- All user pool endpoints, including managed login and the classic hosted UI
- Requests from your app to the Cognito API that are **not** authorized with AWS credentials
  (i.e., unauthenticated public API operations — sign-up, sign-in, forgot-password)

Requests using IAM-signed admin APIs are not in scope.

### Constraints you must design around

1. **PII is not available to WAF.** You cannot write rules matching usernames, passwords, phone
   numbers, or email addresses in user pool requests. Match on IP address, user agent, path, headers,
   and the requested API operation instead.
2. **ATP is incompatible.** A web ACL using AWS WAF Fraud Control **account takeover prevention**
   (the `AWSManagedRulesATPRuleSet` managed rule group) **cannot be associated with a user pool**.
   Check for it before associating. Cognito's own threat protection covers overlapping ground.
3. **CAPTCHA breaks TOTP registration.** A rule presenting a CAPTCHA action can cause an
   unrecoverable error during managed login TOTP MFA enrollment. AWS documents a specific rule
   pattern to avoid this — follow it if you need CAPTCHA.
4. **Custom block responses only apply to the first request.** Rule conditions can return a custom
   block response only on a user's first request to an interactive managed login page. Subsequent
   matches return your custom status code, headers, and redirect, but a default block message body.
5. **Blocked requests don't consume rate quota.** The WAF handler runs *before* API-level throttling,
   so WAF-blocked requests don't count against your request-rate quotas. This makes WAF an effective
   shield for quota exhaustion attacks.
6. **Propagation delay.** A newly created web ACL takes a short time to propagate before Cognito
   can use it.

### Recommended rule composition

- **Rate-based rules** — the primary defense against credential stuffing and enumeration
- **`AWSManagedRulesAmazonIpReputationList`** — known malicious sources
- **`AWSManagedRulesCommonRuleSet`** — general web exploits
- **`AWSManagedRulesBotControlRuleSet`** — automated traffic (mind the ATP exclusion)
- **Geo-match rules** — if your user base is geographically bounded
- Custom rules keyed on the requested API operation, to rate-limit `SignUp` or `ForgotPassword`
  far more aggressively than `InitiateAuth`

### Associating

Console: WAF console → create web ACL with **Resource type: Regional resources** in the pool's
Region → **Associated AWS Resources** → **Add AWS resources** → resource type **Amazon Cognito
user pool** → select the pool.

CLI:

```bash
aws wafv2 associate-web-acl \
  --web-acl-arn arn:aws:wafv2:us-west-2:111122223333:regional/webacl/cognito-acl/EXAMPLE \
  --resource-arn arn:aws:cognito-idp:us-west-2:111122223333:userpool/us-west-2_EXAMPLE
```

**There is no WAF association by default.** Prowler, CIS-style benchmarks, and most compliance
tooling flag an unassociated pool. Deploy in count mode first, review the WAF logs, then flip to
block — auth endpoints are unforgiving of false positives.

---

## 8. Security: threat protection

**Requires the Plus feature plan.** This is the feature formerly sold as *advanced security
features* (ASF), renamed and folded into Plus in November 2024, at up to 60% lower cost than the
old ASF pricing.

Two capabilities: **compromised-credentials detection** and **adaptive authentication**.

### Enforcement modes

| Mode | Behavior |
|---|---|
| **Audit only** | Detects and scores, gathers user-level logs and CloudWatch metrics, takes no action |
| **Full function** (enforced) | Detects and applies your configured automated responses |
| **Off** | Disabled |

You can set **different enforcement modes for standard authentication and custom authentication
flows**, though in full-function mode both share the same automated-response configuration.

Configuration can be global to the pool or **overridden per app client** — in the console, select the
app client under **App integration** and choose *Use client-level settings*. Useful for enforcing
strictly on a customer-facing client while auditing on an internal one.

### Compromised-credentials detection

Checks plaintext passwords against indicators of compromise from public breach data. Cognito
evaluates local users signing in with username and password, through managed login and through the API.

**Where it can check:**

| Event | Coverage |
|---|---|
| Sign-up | Passwords submitted via `SignUp` and the managed login sign-up form |
| Sign-in | `ADMIN_USER_PASSWORD_AUTH` (AdminInitiateAuth), `USER_PASSWORD_AUTH` (InitiateAuth), and the `PASSWORD` option of `USER_AUTH` in both |
| Password change | Password update operations |

**Where it cannot:** SRP flows. SRP transmits a hashed proof of password rather than the password
itself, so Cognito has no plaintext to evaluate. This is a genuine tension — AWS recommends SRP as
the best-practice flow for custom-built apps, but SRP is precisely the flow compromised-credentials
detection can't inspect. Decide which you want and configure `Event detection` accordingly.

**Responses:**

- **Allow sign-in** — permit and record. Review evaluations in CloudWatch Logs and threat
  protection metrics. The right starting point.
- **Block sign-in** — prevent authentication and set the user's `UserStatus` to `RESET_REQUIRED`.
  The user must change their password before signing in again. Make sure your app handles
  `PasswordResetRequiredException` gracefully, or blocked users hit a dead end.

### Adaptive authentication

For every sign-in attempt, Cognito computes a **risk score** from device and session signals your
app supplies plus signals it derives from the request itself:

- IP address and IP reputation
- User agent
- Geographic distance from previous sign-in attempts
- **Impossible travel** — sign-ins from two locations too far apart for the elapsed time (added
  August 2024)
- New device / new location relative to the user's history
- Custom authentication flow signals (also added August 2024)

Risk is bucketed into severity levels, and you configure a response per level:

| Response | Effect |
|---|---|
| Allow | Permit normally |
| Optional MFA | Offer a second factor |
| Require MFA | Force a second factor |
| Block | Deny the attempt |

Adaptive auth can **turn on MFA for a user who hasn't yet chosen a method**, prompting them to enrol
mid-session. Once MFA is active for a user, they're always challenged regardless of risk level.

Choosing **Cognito defaults** rather than custom actions blocks sign-in at **all** risk levels and
sends no user notification — a much more aggressive posture than most teams expect. Configure
custom actions deliberately.

You can also customize the notification email templates users receive when risk is detected.

### IP allowlists and denylists

Independent of risk scoring, you can configure always-allow and always-block IP ranges — useful for
office egress ranges, known-good automation, and confirmed-bad sources.

### Configuring

Console: user pool → **Threat protection** (older console: **Advanced security** tab → **Activate**)
→ choose *Standard and custom authentication* → set enforcement mode → configure compromised
credentials and adaptive authentication responses.

API: `SetRiskConfiguration` / `DescribeRiskConfiguration`, with
`CompromisedCredentialsRiskConfiguration`, `AccountTakeoverRiskConfiguration`, and
`RiskExceptionConfiguration` (the IP lists). Pool-level `AdvancedSecurityMode` is `OFF | AUDIT | ENFORCED`.

### Metrics

Cognito publishes sign-in attempt counts, risk levels, and failed-challenge metrics to CloudWatch.
Build alarms on these before you switch from audit to enforced — a sudden spike in high-risk
classifications in enforced mode is an outage.

### Rollout sequence

1. Switch the pool to **Plus**.
2. Enable threat protection in **Audit only**.
3. Run for at least two weeks; watch CloudWatch metrics and exported logs.
4. Tune risk responses. Add IP exceptions for known-good sources.
5. Enable **full function** on one app client first.
6. Expand.

---

## 9. Security: log streaming and export

Cognito's log delivery configuration handles two independent, differently-scoped log streams.

### The two event sources

| `EventSource` | `LogLevel` | Contents | Destinations | Plan |
|---|---|---|---|---|
| `userNotification` | `ERROR` | Email and SMS message-delivery errors | **CloudWatch Logs only** | Any plan |
| `userAuthEvents` | `INFO` | Threat protection user activity: session properties and risk evaluations | **CloudWatch Logs, Amazon Data Firehose, or Amazon S3** | **Plus only** |

`userAuthEvents` additionally requires threat protection to be active in **audit-only or
full-function** mode. Plus alone isn't enough — the feature has to be on.

A pool can have **multiple simultaneous log configurations**, one per event source.

### Configuring

```bash
aws cognito-idp set-log-delivery-configuration \
  --user-pool-id us-west-2_EXAMPLE \
  --log-configurations \
    'EventSource=userNotification,LogLevel=ERROR,CloudWatchLogsConfiguration={LogGroupArn=arn:aws:logs:us-west-2:111122223333:log-group:cognito-notifications}' \
    'EventSource=userAuthEvents,LogLevel=INFO,S3Configuration={BucketArn=arn:aws:s3:::my-cognito-activity-logs}'
```

Firehose instead of S3:

```json
{
  "EventSource": "userAuthEvents",
  "LogLevel": "INFO",
  "FirehoseConfiguration": {
    "StreamArn": "arn:aws:firehose:us-west-2:111122223333:deliverystream/cognito-activity"
  }
}
```

CloudFormation: `AWS::Cognito::LogDeliveryConfiguration`.
API: `SetLogDeliveryConfiguration` / `GetLogDeliveryConfiguration`.

### Prerequisites that bite

For **CloudWatch Logs** destinations:

- The caller needs `logs:CreateLogDelivery`, `logs:PutResourcePolicy`, `logs:DescribeResourcePolicies`,
  and `logs:DescribeLogGroups`.
- The target log group must be in the **same AWS account** as the user pool.
- The target log group **must not be KMS-encrypted**. This one catches teams with an
  encrypt-everything policy — you'll need an exception or a different destination.

For **Firehose** and **S3**, configure the stream/bucket policy per the Cognito log export
prerequisites before enabling delivery. Destinations and their permissions are configured outside
Cognito; the API will not create them for you.

### Choosing a destination

| Destination | Use when |
|---|---|
| **CloudWatch Logs** | Real-time alarms, Logs Insights queries, small-to-moderate volume |
| **Firehose** | Fan-out to OpenSearch, Splunk, Datadog, or a third-party SIEM; transformation en route |
| **S3** | Cheap long-term retention, compliance archives, Athena querying |

Firehose is the usual answer for SIEM integration. S3 plus Athena is the usual answer for
"we need 7 years of auth logs for auditors."

### The alternative you probably don't need anymore

Before native export existed, the pattern was processing **CloudTrail** logs for authentication
events and correlating them yourself. AWS's own security blog on the subject now carries a note
recommending native export for Plus customers instead. CloudTrail still has its place — it records
Cognito **API requests**, including requests to managed login, and is the right source for
control-plane auditing (who changed the pool config). But for user activity and risk signals,
`userAuthEvents` export is the supported path.

### Full observability picture

| Signal | Source |
|---|---|
| Control-plane API calls | CloudTrail |
| Message delivery failures | `userNotification` log export |
| User activity and risk scores | `userAuthEvents` log export (Plus) |
| Threat protection metrics | CloudWatch metrics |
| Request-rate quota consumption | Service Quotas console |
| Custom application-level events | Lambda triggers writing to CloudWatch |
| WAF rule matches | WAF logging (separate configuration) |
| Device/session analytics | Amazon Pinpoint integration |

---

## 10. Application Load Balancer integration

This is where ALB actually enters the picture. ALB can terminate authentication itself, so your
backend never implements an OAuth flow.

### `authenticate-cognito`

An HTTPS listener rule can carry **one** user-authentication action —
`authenticate-oidc`, `authenticate-cognito`, or `jwt-validation` — before its terminal routing
action (`forward`, `redirect`, or `fixed-response`).

`AuthenticateCognitoConfig` parameters:

| Parameter | Notes |
|---|---|
| `UserPoolArn` | The pool |
| `UserPoolClientId` | The app client |
| `UserPoolDomain` | Prefix or fully qualified custom domain |
| `Scope` | Default `openid`. Add `email`, `profile`, or custom resource-server scopes |
| `SessionCookieName` | Default `AWSELBAuthSessionCookie` |
| `SessionTimeout` | Default `604800` seconds (7 days) |
| `OnUnauthenticatedRequest` | `authenticate` (default, redirect to IdP), `allow` (pass through), or `deny` (HTTP 401) |
| `AuthenticationRequestExtraParams` | Up to 10 extra query parameters on the authorization redirect |

Flow: unauthenticated request → ALB redirects to the Cognito authorization endpoint → user signs in →
Cognito redirects to `https://<alb-dns>/oauth2/idpresponse` → ALB exchanges the code, sets the
session cookie, and forwards the request to the target with these headers:

- `x-amzn-oidc-accesstoken`
- `x-amzn-oidc-identity` (the `sub`)
- `x-amzn-oidc-data` (a signed JWT of user claims)

**Your backend must verify the signature on `x-amzn-oidc-data`.** Trusting the header blindly means
anyone who can reach the target directly can impersonate any user — lock target security groups down
to the ALB, and validate regardless.

Practical notes:

- Request `openid` explicitly, or Cognito won't return an ID token.
- The app client's callback URL must include `https://<alb-domain>/oauth2/idpresponse`.
- Groups and custom attributes flow through in the ID token claims, so ALB path-based routing can be
  combined with group-based access decisions in your backend.
- Large token payloads shard the session cookie across multiple cookies — another argument for
  keeping app-client readable attributes minimal.

### `jwt-validation` (newer)

A separate action type for **service-to-service and machine-to-machine** traffic, where there is no
human and no redirect. ALB validates the token signature against a JWKS endpoint you configure and
forwards the request with the token intact if valid, rejecting it otherwise.

- Mandatory claim validation: `iss` and `exp`
- Also validated when present: `nbf` and `iat`
- Up to **10 additional claims** can be configured for validation
- Works with **any** issuer, not just Cognito — but pairs naturally with a Cognito resource server
  and client-credentials grant
- There are size limits on the IdP's JWKS endpoint; very large key sets require validating in
  application code instead

Terraform exposes this as `type = "jwt-validation"` with a `jwt_validation` block on
`aws_lb_listener` and `aws_lb_listener_rule`. The AWS Load Balancer Controller supports it via
ingress annotations.

### Choosing between them

| Situation | Action |
|---|---|
| Human users, Cognito user pool | `authenticate-cognito` |
| Human users, external OIDC IdP (Okta, Entra, Google) | `authenticate-oidc` |
| Machine clients presenting a bearer token | `jwt-validation` |

---

## 11. Recent changes worth knowing

| Date | Change |
|---|---|
| Aug 2024 | ASF gains impossible-travel detection and custom-auth-flow risk detection |
| Nov 21–22, 2024 | Managed login, passkeys/FIDO2, email and SMS OTP passwordless sign-in; Lite/Essentials/Plus feature plans; ASF renamed **threat protection** and folded into Plus |
| Jan 2025 | Native export of threat protection user activity logs |
| Mar 2025 | Essentials and Plus reach AWS GovCloud (US) |
| Apr 22, 2025 | OAuth 2.0 refresh token rotation |
| Jun 26, 2025 | **AWS WAF support for managed login** |
| Oct 27, 2025 | OAuth 2.0 resource indicators |
| Nov 4, 2025 | Private connectivity via AWS PrivateLink |
| Nov 30, 2025 | End of the legacy-pricing Essentials upgrade window for eligible existing customers |
| May 28 / Jun 2026 | **Multi-Region replication** with customer-managed KMS keys |
| Jul 6, 2026 | **Provisioned limits** for self-service rate limit management |
| Jul 30, 2026 | Amazon Cognito Sync closed to new customers (use AWS AppSync) |

---

## 12. Design checklist and common traps

### Before creating a pool

- [ ] Sign-in identifiers decided — **permanent**
- [ ] Alias vs. username attributes decided — **permanent**
- [ ] Required standard attributes decided — **permanent**
- [ ] Username case sensitivity decided — **permanent**
- [ ] Custom attribute schema planned against the hard 50-attribute cap
- [ ] Boolean/DateTime attributes created via API or CloudFormation, since the console can't
- [ ] Any attribute receiving an IdP claim mapping marked **mutable**
- [ ] Feature plan chosen — and, on a pre-Nov-2024 pool, free-tier impact of switching checked
- [ ] Multi-Region replication considered if auth is on the critical path

### Security baseline

- [ ] WAF web ACL associated (there is none by default), with no ATP rule group
- [ ] Rate-based WAF rules on `SignUp` and `ForgotPassword`
- [ ] WAF deployed in count mode first
- [ ] Threat protection in audit-only, with CloudWatch alarms, before enforcing
- [ ] `PasswordResetRequiredException` handled in the app (compromised-credentials block sets `RESET_REQUIRED`)
- [ ] `userNotification` logs going to CloudWatch — silent email/SMS failures look like user error
- [ ] `userAuthEvents` exported to SIEM or S3 if on Plus
- [ ] Target log group not KMS-encrypted, and in the same account
- [ ] App-client attribute permissions tightened from the default of read/write on everything
- [ ] `x-amzn-oidc-data` signature verified in the backend if using ALB authentication
- [ ] Targets reachable only from the ALB

### Traps, ranked by how often they land

1. **Custom attribute added but not showing up in tokens** — you didn't grant the app client read
   permission. New custom attributes are unavailable to app clients until explicitly permitted.
2. **Federated user locked out after first sign-in** — an IdP claim is mapped to an immutable attribute.
3. **`cognito:preferred_role` missing** — two groups share a precedence value with different role ARNs.
4. **Compromised-credentials detection appears not to work** — you're using SRP, which sends no plaintext password.
5. **Adaptive auth blocking everyone** — Cognito defaults block at all risk levels with no notification.
6. **Log delivery failing silently** — the destination log group is KMS-encrypted or in another account.
7. **WAF association fails** — the web ACL contains the ATP managed rule group.
8. **TOTP enrollment breaks** — a WAF CAPTCHA rule interferes with managed login TOTP registration.
9. **Bill jumps after a tier change** — a legacy pool dropped from the 50,000-MAU free tier to 10,000.
10. **Need to change a required attribute** — you can't. New pool plus `UserMigration` trigger.
11. **Can't find users by custom attribute** — `ListUsers` doesn't support it. Mirror to DynamoDB.
12. **`sub` fails UUID validation** — it isn't RFC-format. Don't validate it.

---

## 13. References

**Core documentation**
- [Amazon Cognito user pools](https://docs.aws.amazon.com/cognito/latest/developerguide/cognito-user-pools.html)
- [User pool feature plans](https://docs.aws.amazon.com/cognito/latest/developerguide/cognito-sign-in-feature-plans.html)
- [Working with user attributes](https://docs.aws.amazon.com/cognito/latest/developerguide/user-pool-settings-attributes.html)
- [Adding groups to a user pool](https://docs.aws.amazon.com/cognito/latest/developerguide/cognito-user-pools-user-groups.html)
- [Managing users in your user pool](https://docs.aws.amazon.com/cognito/latest/developerguide/managing-users.html)
- [Application-specific settings with app clients](https://docs.aws.amazon.com/cognito/latest/developerguide/user-pool-settings-client-apps.html)
- [Quotas in Amazon Cognito](https://docs.aws.amazon.com/cognito/latest/developerguide/limits.html)

**Security**
- [Associate an AWS WAF web ACL with a user pool](https://docs.aws.amazon.com/cognito/latest/developerguide/user-pool-waf.html)
- [Threat protection](https://docs.aws.amazon.com/cognito/latest/developerguide/cognito-user-pool-settings-advanced-security-threat-protection.html)
- [Working with adaptive authentication](https://docs.aws.amazon.com/cognito/latest/developerguide/cognito-user-pool-settings-adaptive-authentication.html)
- [Working with compromised-credentials detection](https://docs.aws.amazon.com/cognito/latest/developerguide/cognito-user-pool-settings-compromised-credentials.html)

**API reference**
- [SetLogDeliveryConfiguration](https://docs.aws.amazon.com/cognito-user-identity-pools/latest/APIReference/API_SetLogDeliveryConfiguration.html)
- [LogConfigurationType](https://docs.aws.amazon.com/cognito-user-identity-pools/latest/APIReference/API_LogConfigurationType.html)
- [SchemaAttributeType](https://docs.aws.amazon.com/cognito-user-identity-pools/latest/APIReference/API_SchemaAttributeType.html)
- [AddCustomAttributes](https://docs.aws.amazon.com/cognito-user-identity-pools/latest/APIReference/API_AddCustomAttributes.html)
- [UpdateGroup](https://docs.aws.amazon.com/cognito-user-identity-pools/latest/APIReference/API_UpdateGroup.html)

**ALB**
- [Verify JWTs using an Application Load Balancer](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/listener-verify-jwt.html)
- [ELBv2 Action reference](https://docs.aws.amazon.com/elasticloadbalancing/latest/APIReference/API_Action.html)

**Announcements and pricing**
- [Amazon Cognito pricing](https://aws.amazon.com/cognito/pricing)
- [New feature tiers: Essentials and Plus](https://aws.amazon.com/about-aws/whats-new/2024/11/new-feature-tiers-essentials-plus-amazon-cognito)
- [AWS WAF support for Managed Login](https://aws.amazon.com/about-aws/whats-new/2025/06/amazon-cognito-aws-waf-managed-login)
- [Multi-Region replication](https://aws.amazon.com/about-aws/whats-new/2026/06/amazon-cognito-multi-region/)
- [Provisioned limits for self-service rate limit management](https://aws.amazon.com/blogs/security/from-2-weeks-to-2-minutes-amazon-cognito-launches-provisioned-limits-for-self-service-rate-limit-management/)
