# Git Repo Local Management
Workin with git locally on your machine can start to require a little ogranization, if you are working across a few repos at once. If using github you can simply use github desktop for simplicity, but there are limitations here. If using the command line here are some basic tips:

## How Git Determines Which Repo to Work With

Git looks for a `.git` folder in your current directory (or walks up the directory tree until it finds one). This `.git` folder contains all the repository metadata, history, and configuration.

---
## Working with Multiple Repos
You do need to navigate between folders to work with different repositories:

```bash
# Working with repo 1
cd ~/projects/my-website
git status
git pull origin main
git add .
git commit -m "Update homepage"

# Switch to different repo
cd ~/projects/my-api
git status
git pull upstream develop
git checkout -b new-feature
```

## Directory Structure Example

```
~/projects/
├── my-website/          # Repository 1
│   ├── .git/           # Git metadata for this repo
│   ├── index.html
│   └── styles.css
├── my-api/             # Repository 2  
│   ├── .git/           # Different Git metadata
│   ├── server.js
│   └── package.json
└── shared-library/     # Repository 3
    ├── .git/           # Yet another separate repo
    └── lib.js
```

## Tips for Managing Multiple Repos

**Use terminal tabs/windows:**
- Keep different repos open in separate terminal tabs
- Use tools like `tmux` for session management

**IDE workspace management:**
- Most IDEs can handle multiple Git repos in one workspace
- VS Code, IntelliJ, etc. detect each `.git` folder automatically

**Git worktrees (advanced):**
```bash
# Work with multiple branches of same repo in different folders
git worktree add ../feature-branch feature-branch
```

So yes, you're constantly `cd`-ing between project folders when working with multiple repositories via command line!

## Repo Alias
In Git, you can work with multiple remote repositories simultaneously by adding multiple remotes to your local repository. Here's how:

## Adding Multiple Remotes

```bash
# Add additional remotes (origin is typically added automatically)
git remote add upstream https://github.com/original/repo.git
git remote add fork https://github.com/yourfork/repo.git
git remote add staging https://github.com/company/staging-repo.git

# View all remotes
git remote -v
```

When you run `git remote -v`, you'll see:
```
origin     https://github.com/myuser/myrepo.git (fetch)
origin     https://github.com/myuser/myrepo.git (push)
upstream   https://github.com/originaluser/originalrepo.git (fetch)
upstream   https://github.com/originaluser/originalrepo.git (push)
production https://github.com/company/prod-repo.git (fetch)
production https://github.com/company/prod-repo.git (push)
```

### Using the Aliases
Instead of typing the full URL every time:
```bash
# Without alias (tedious)
git push https://github.com/myuser/myrepo.git main

# With alias (simple)
git push origin main
git pull upstream main
git fetch production
```

### Common Naming Conventions

- `origin` - your main repository (default when you clone)
- `upstream` - the original repository you forked from
- `fork` - your personal fork
- `production`/`staging`/`dev` - different deployment environments
- Team member names - `alice`, `bob` for collaborator repos

The alias names are completely up to you - they're just convenient shortcuts to avoid typing long URLs repeatedly.

## Common Multi-Remote Workflows

**Fetching from multiple remotes:**
```bash
git fetch origin
git fetch upstream
git fetch --all  # fetch from all remotes at once
```

**Pushing to specific remotes:**
```bash
git push origin main
git push fork feature-branch
git push staging develop
```

**Pulling from different remotes:**
```bash
git pull upstream main  # pull from upstream's main branch
git pull origin develop
```

## Typical Use Cases

**Fork workflow:** You might have `origin` (your fork) and `upstream` (original repo) to keep your fork synchronized while contributing.

**Multi-environment deployment:** Different remotes for `production`, `staging`, and `development` environments.

**Team collaboration:** Different remotes for different team members' repositories or organizational forks.

---
## Branch Switching
Often you will want to commit changes before switching branches or work in a separate folder. However, if toggling back and forth Git handles uncommitted changes in a few different ways when you try to switch branches:

## 1. Changes Carry Over (Most Common)

If your uncommitted changes don't conflict with the target branch, Git carries them over:

```bash
# On main branch, edit some files
echo "new content" >> file.txt
git status  # Shows modified file.txt

# Switch branches - changes come with you
git checkout feature-branch
git status  # Still shows modified file.txt
```

This works when the files you modified exist and are the same on both branches.

## 2. Git Blocks the Switch (Conflicts)

If your changes would conflict with the target branch, Git prevents the switch:

```bash
# You modified file.txt on main
git checkout feature-branch
# Error: Your local changes would be overwritten by checkout
```

You'll need to handle this by:

**Option A: Commit your changes**
```bash
git add .
git commit -m "WIP: working on feature"
git checkout feature-branch
```

**Option B: Stash your changes**
```bash
git stash push -m "temporary work"
git checkout feature-branch
# Later: git stash pop to restore changes
```

**Option C: Force switch (loses changes)**
```bash
git checkout --force feature-branch  # Discards uncommitted changes!
```

## 3. Git Stash - Temporary Storage

Stash is like a temporary clipboard for uncommitted work:

```bash
# Save current work temporarily
git stash push -m "half-finished login form"

# Switch branches freely
git checkout other-branch
# Do some work...

# Come back and restore your stashed work
git checkout original-branch
git stash pop  # Restores and removes from stash
# or
git stash apply  # Restores but keeps in stash
```

## Best Practices

- **Commit often** - even small, incomplete changes
- **Use descriptive stash messages** - `git stash push -m "description"`
- **Check status before switching** - `git status` shows what's uncommitted
- **Use WIP commits** - you can always amend or squash commits later

Git's pretty smart about preserving your work, but it's safest to commit or stash before major branch switches.

---
## Managing Branches with Multiple Remotes

```bash
# Create a branch tracking a specific remote
git checkout -b feature origin/feature
git checkout -b hotfix upstream/main

# Push to a specific remote and set tracking
git push -u fork new-feature
```

You can also configure different push/fetch URLs for the same remote name if needed using `git remote set-url`.

