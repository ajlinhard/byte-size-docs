# Entra ID Integration
## Part 1 — Workforce SSO: Entra ID → AWS Console/CLI (IAM Identity Center)

This lets staff log in once via Entra ID and land in the right AWS account/role, with no IAM users or long-lived access keys.

1. **Confirm prerequisites.** Entra ID tenant with Cloud/Global Application Administrator rights, AWS Organizations with IAM Identity Center enabled, and Entra ID **P1 or higher** — the Free tier supports SSO but not automatic (SCIM) provisioning.
   *Common mistake:* teams pilot on Entra ID Free, get SSO working, then discover provisioning isn't available and have to redo licensing.

2. **Enable IAM Identity Center and grab its SAML metadata.** Settings → Identity source → Change identity source → "External identity provider" gives you the ACS URL and Issuer you'll paste into Entra.
   *Risk:* changing identity source later can strand existing user/permission-set assignments — nail this down before scaling assignments.

3. **Create the Enterprise Application in Entra ID.** Identity → Applications → Enterprise applications → New application, then search the Microsoft Entra gallery for AWS IAM Identity Center and create it from the gallery result — this pre-fills SAML config and includes a ready SCIM connector.
   *Common mistake:* building a generic "non-gallery" SAML app instead — SSO works, but you lose the built-in SCIM template and have to hand-map attributes later.

4. **Configure SAML.** Set Identifier and Reply URL from AWS's ACS/Issuer values; confirm the NameID claim (usually UPN or email).
   *Common mistake:* a trailing slash or http/https mismatch between what AWS issued and what's typed into Entra — causes silent SAML validation failures.

5. **Import Entra's metadata into IAM Identity Center** (federation metadata XML, or SSO URL + Issuer + certificate).
   *Risk:* Entra's SAML signing cert auto-rotates roughly every 3 years with no notice to AWS. Prefer the auto-refreshing metadata URL over a static XML upload, or calendar the rotation.

6. **Lock down and test.** In the Entra app's Properties, set "Assignment required" to Yes so only explicitly assigned users/groups can even attempt sign-in, then test with one pilot user through the AWS access portal URL.
   *Risk:* leaving assignment open means anyone in the tenant can reach the AWS sign-in page, widening attack surface unnecessarily.

7. **Turn on SCIM provisioning.** In IAM Identity Center, enable automatic provisioning to get a SCIM endpoint + bearer token, then paste both into Entra's Provisioning tab and assign the same groups.
   *Common mistake:* assigning users for SSO but forgetting to also assign them under Provisioning — they can authenticate but have no synced AWS identity.
   *Risk:* that SCIM token can create/deactivate identities — treat it like a credential, rotate it periodically.

8. **Build Permission Sets** and assign them to accounts against Entra-synced groups.
   *Common mistake:* defaulting to AdministratorAccess "to get it working" and never tightening it. Start least-privilege.

9. **Watch nested groups.** If a user's access comes through a nested child group, SCIM may not flatten membership as expected — verify with a real nested-membership test user.

10. **Keep a break-glass path** — an Identity-Center-independent way into the management account (root with MFA, or a locked-down IAM user) in case Entra ID is unreachable or federation misconfigures.

---

