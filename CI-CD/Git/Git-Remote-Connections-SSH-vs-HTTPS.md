# Git Remote Connections SSH vs. HTTPS
!: What is the difference of connecting to SSH vs HTTPS in terms of managing your remote Git repository?<br>
A: Both let you push/pull to the same remote repos — the difference is entirely in how you authenticate and a few practical tradeoffs.

## HTTPS

**URL format:** `https://github.com/username/repo.git`

**How auth works:** Username + password/token. GitHub, GitLab, etc. no longer accept your account password for git operations — you need a **personal access token (PAT)** instead. That token gets cached by a credential helper (Keychain on Mac, Credential Manager on Windows, etc.) so you're not typing it every time.

**Pros:**
- Works out of the box, no key setup needed
- Works through most corporate firewalls/proxies (it's just port 443, same as normal web traffic)
- Easier for beginners — no key generation, no agent to configure

**Cons:**
- Tokens can expire and need regenerating/rotating
- If a credential helper isn't configured, you may get prompted for username/token on every push/pull
- Slightly more fiddly to manage per-repo or per-account credentials if you work across multiple accounts

## SSH

**URL format:** `git@github.com:username/repo.git`

**How auth works:** A public/private SSH key pair. You generate a key (`ssh-keygen`), upload the **public** key to GitHub/GitLab, and keep the **private** key on your machine (protected by `ssh-agent`, optionally with a passphrase).

**Pros:**
- No typing credentials once set up — just works
- Considered more secure for long-term use (private key never leaves your machine, no token to leak in plaintext)
- Easier to manage multiple accounts cleanly via SSH config aliases (e.g. separate keys for work/personal GitHub)
- Keys don't need periodic rotation like short-lived tokens (though you can rotate them if you want)

**Cons:**
- Slightly more setup: generate key, add to agent, upload public key to the platform
- Can be blocked on some corporate/restrictive networks (SSH usually runs over port 22, which firewalls sometimes close) — though GitHub also offers SSH-over-443 as a workaround
- A bit more to understand conceptually if you're new to it

## Quick summary

| | HTTPS | SSH |
|---|---|---|
| Setup effort | Low | Moderate (one-time) |
| Day-to-day friction | Low, if credential helper is set up | Very low |
| Firewall friendliness | Better | Can be blocked (port 22) |
| Multi-account management | Clunkier | Cleaner (via SSH config) |
| Typical choice for | Beginners, restrictive networks, CI/CD with tokens | Regular contributors, personal dev machines |

**In practice:** most individual developers set up SSH once and never think about auth again. HTTPS is common in CI/CD pipelines (using tokens) or in environments where SSH ports are blocked.

You can check which one a repo is using with `git remote -v`, and switch between them anytime with `git remote set-url origin <new-url>` — it doesn't affect your commit history either way.
