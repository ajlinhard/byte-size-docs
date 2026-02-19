# Git Policies:

## Branch Strategy
- Each sub-team lead will branches off `main`, to create a sub-team branch which can be the base for the weeks push of development.
- Then each team member will branch off the Sub-Team root for individual development items and merge back to the root. 
  - Team members should keep branches short-lived (ideally 1-3 days max), and merges back frequently. Long-lived branches are where pain lives.
- Merge between Sub-Teams weekly. (See Sub-Team Coordination below for more detail)
 
#### Sub-Teams
- T1: APIs / VA ETL
- T2: System Metadata and Document ETL
- T3: AI Workflow

### Branch Naming Convention
**Sub-Team Roots:**
Sub-Team branches should be called ==> {Sub-Team#}/{YYYYMMDD}  
Ex: T3/20260219

**Development Branched:**
These are for tickets or items you are developing for your sub-team ==> {Sub-Team#}/{YYYYMMDD}/{Name}-{Issue # / Item}
Ex: T3/20260219/Andrew-522

**Hotfixes**
When we need to patch something really faster we create a hotfix branch: HotFix/{YYYYMMDD}-{Issue #}
Example: HotFix/20260218-522

## Merge Frequency

The biggest rule: Try to **merge at least every 2 days**. If a branch lives longer than 3-4 days, it's accumulating conflict debt. Encourage your sub-team leads to check for stale branches weekly. GitLab's branch list makes this easy to audit.

Use **feature flags** to enable merging incomplete features safely. This lets people merge working-but-not-yet-live code without blocking a release.

## Merge Request (MR) Rules

Set these as protected rules in GitLab:

- At least **1-2 approvals** required before merging to `main`. For cross-team changes, require an approval from the affected team's lead.
- **Pipelines must pass** before merge — no exceptions once developed, we will try to keep the runtime low to avoid CI bottlenecks.
- **Delete branches on merge** automatically (GitLab has a setting for this).
- Keep MRs small.
  - New scripts or Dev can have large changes, review frequently with someone else.
  - A good rule of thumb is under 400-800 lines changed. Big MRs get rubber-stamped; small ones get real review.

## Sub-Team Coordination

With 3-4 sub-teams, the biggest risk is teams stepping on each other. A few things to help:

- Each sub-team lead should do a quick daily check of open MRs — stale MRs are a sign of a blocked teammate.
- Use GitLab's **CODEOWNERS** file to auto-assign reviewers based on which files are touched. This reduces the "who do I ask to review this?" friction.
- Schedule a weekly 15-minute sync just to surface cross-team dependencies before they become merge conflicts. Architects do not need to be included.
- At the end of each week (or first thing Monday) we will attempt to merge/rebase Sub-team branches, only to ignoring this for specific approved reasons.
  - Upcoming Demo, Conflicts due to R&D efforts, or unfinished features which will break the other teams build/dev.

## Handling Conflicts

When conflicts happen (and they will), the author of the *newer* branch is responsible for resolving them — not the person who merged first. Make this a team norm so there's no ambiguity. Rebase over merge commits keeps history cleaner, though this is a matter of preference.

## A Few GitLab-Specific Settings Worth Enabling

- **Squash commits on merge** — keeps `main` history readable
- **Auto-close issues from MR descriptions** using `Closes #123` syntax
- Set merge request templates so everyone includes context, testing notes, and a checklist by default

The core philosophy is: small, frequent, reviewed. Most team dysfunction around merging comes from branches that live too long.


---
# Lead Level Rules:
---

## Protecting `main`

Lock `main` so no one can push directly — all changes go through MRs. You can do the same for `develop` if you use a staging branch. Designate yourself and sub-team leads as Maintainers in GitLab so you control who can actually merge to protected branches.
