# JWT Role Specific Users
Same mechanism, just with an extra check after signature verification: the JWT carries the role (or roles) as a claim in the payload, and your middleware checks that claim against what the endpoint requires.A few things worth knowing about how this is typically built:
<img width="1440" height="1060" alt="image" src="https://github.com/user-attachments/assets/c11098be-b6b7-4209-9e7b-6c4eb8282d90" />

**The role claim is just data in the payload — but it's tamper-proof.** Since the payload is inside the signed portion of the token, a user can't just edit their own JWT to say `role: admin` — doing so breaks the signature, and verification (step 1 above) rejects the token before the role check even runs. This is why you covered signature integrity earlier — it's exactly what makes the role claim trustworthy in the first place.

**Common ways to model roles in the token:**
- A single string: `"role": "editor"`
- Multiple roles: `"roles": ["editor", "reviewer"]`
- Fine-grained permissions instead of (or alongside) roles: `"permissions": ["posts:write", "posts:delete"]` — this scales better than roles alone once you have many narrow capabilities, since you're not creating a new role every time you need a new permission combination.
- OAuth-style scopes: `"scope": "read:posts write:posts"` — the standard approach if you're building on OAuth2, where scopes represent what the token is allowed to do rather than who the user is.

**Where the endpoint-to-role mapping usually lives:** most frameworks let you declare it declaratively, right at the route level — a decorator, annotation, or middleware chain entry like `@RequireRole("admin")` on a route, or a config table mapping paths to allowed roles. That keeps the authorization rule next to the code it protects, rather than scattered through business logic.

**Layering matters for defense in depth.** Role checks are commonly done in two places: coarse-grained at the gateway/middleware level (does this role have any access to this route at all?), and finer-grained inside the business logic (can this specific user edit this specific resource they own?). JWT roles handle the first; the second usually needs an extra database check, since "can edit posts" and "can edit *this* post" are different questions the token alone can't answer.

**One gotcha:** since the token is issued once and roles are baked in at that moment, a role change (promotion, demotion, revoked access) doesn't take effect until the token expires or is refreshed — same tradeoff as the revocation issue we discussed earlier. Short-lived tokens keep this lag small.
