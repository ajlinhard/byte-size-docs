# Git Commands

Here is Git command line cheatsheet that covers all the areas you requested. The cheatsheet includes:

**Main Components:**
1. **Core Commands Table** - All essential Git commands with their purposes and examples
2. **Detailed Parameter Tables** - For each major command, showing all the important options and flags
3. **Complete Workflows** - Step-by-step guides for 12 common development scenarios

**Key Workflows Covered:**
- Creating repositories with proper permissions
- Branching strategies
- Cloning repositories
- Committing code to branches
- Merging branches (including squash merges)
- Rebasing (both interactive and standard)
- Handling merge conflicts
- Release management with tags
- Hotfix workflows
- Stashing work in progress
- Undoing changes safely
- Managing multiple remotes

The cheatsheet is designed to be practical and reference-friendly, with real examples you can copy and paste. Each workflow includes the actual commands you'd run, along with explanations of what they do. The parameter tables help you understand all the options available for each command, so you can customize them for your specific needs.

This should serve as a complete reference for Git operations in your development workflow!

### Documentation
- [An Intro to Git (hubspot)](https://product.hubspot.com/blog/git-and-github-tutorial-for-beginners)
- [Git Branching Stratgies](https://graphite.dev/guides/git-branching-strategies)

---
# Git Command Cheatsheet

## Core Git Commands

| Command | Purpose | Example |
|---------|---------|---------|
| `git init` | Initialize a new Git repository | `git init my-project` |
| `git clone` | Clone a remote repository | `git clone https://github.com/user/repo.git` |
| `git add` | Stage files for commit | `git add file.txt` or `git add .` |
| `git commit` | Create a commit with staged changes | `git commit -m "Add new feature"` |
| `git status` | Show working directory status | `git status` |
| `git log` | View commit history | `git log --oneline` |
| `git diff` | Show changes between commits/files | `git diff HEAD~1` |
| `git branch` | List, create, or delete branches | `git branch feature-login` |
| `git checkout` | Switch branches or restore files | `git checkout main` |
| `git switch` | Switch branches (newer alternative) | `git switch feature-branch` |
| `git merge` | Merge branches | `git merge feature-branch` |
| `git rebase` | Reapply commits on top of another branch | `git rebase main` |
| `git push` | Upload commits to remote repository | `git push origin main` |
| `git pull` | Download and merge remote changes | `git pull origin main` |
| `git fetch` | Download remote changes without merging | `git fetch origin` |
| `git remote` | Manage remote repositories | `git remote add origin <url>` |
| `git reset` | Reset current HEAD to specified state | `git reset --hard HEAD~1` |
| `git revert` | Create new commit that undoes changes | `git revert HEAD` |
| `git stash` | Temporarily save uncommitted changes | `git stash push -m "WIP"` |
| `git tag` | Create, list, or delete tags | `git tag v1.0.0` |

## Command Parameters

### git init
| Parameter | Purpose | Example Values |
|-----------|---------|----------------|
| `--bare` | Create bare repository (no working directory) | `git init --bare` |
| `--template` | Use custom template directory | `git init --template=/path/to/template` |
| `--separate-git-dir` | Create git directory elsewhere | `git init --separate-git-dir=/path/to/git-dir` |

### git clone
| Parameter | Purpose | Example Values |
|-----------|---------|----------------|
| `--branch` or `-b` | Clone specific branch | `git clone -b develop <url>` |
| `--depth` | Create shallow clone with limited history | `git clone --depth 1 <url>` |
| `--recursive` | Clone with submodules | `git clone --recursive <url>` |
| `--origin` or `-o` | Set name for remote | `git clone -o upstream <url>` |

### git add
| Parameter | Purpose | Example Values |
|-----------|---------|----------------|
| `.` | Add all files in current directory | `git add .` |
| `-A` or `--all` | Add all files in repository | `git add -A` |
| `-p` or `--patch` | Interactively stage parts of files | `git add -p file.txt` |
| `-u` or `--update` | Add only tracked files | `git add -u` |

### git commit
| Parameter | Purpose | Example Values |
|-----------|---------|----------------|
| `-m` | Commit message | `git commit -m "Fix bug"` |
| `-a` | Automatically stage tracked files | `git commit -a -m "Update"` |
| `--amend` | Modify last commit | `git commit --amend -m "New message"` |
| `--no-edit` | Use previous commit message | `git commit --amend --no-edit` |

### git log
| Parameter | Purpose | Example Values |
|-----------|---------|----------------|
| `--oneline` | Show commits in single line format | `git log --oneline` |
| `--graph` | Show branch/merge history graphically | `git log --graph` |
| `-n` | Limit number of commits shown | `git log -5` |
| `--since` | Show commits after date | `git log --since="2 weeks ago"` |
| `--author` | Filter by author | `git log --author="John"` |

### git branch
| Parameter | Purpose | Example Values |
|-----------|---------|----------------|
| `-a` | Show all branches (local and remote) | `git branch -a` |
| `-d` | Delete branch | `git branch -d feature-branch` |
| `-D` | Force delete branch | `git branch -D feature-branch` |
| `-m` | Rename branch | `git branch -m old-name new-name` |
| `-r` | Show remote branches only | `git branch -r` |

### git checkout
| Parameter | Purpose | Example Values |
|-----------|---------|----------------|
| `-b` | Create and switch to new branch | `git checkout -b feature-login` |
| `-B` | Create/reset and switch to branch | `git checkout -B hotfix` |
| `--` | Restore files from HEAD | `git checkout -- file.txt` |
| `-t` | Set up tracking branch | `git checkout -t origin/feature` |

### git merge
| Parameter | Purpose | Example Values |
|-----------|---------|----------------|
| `--no-ff` | Create merge commit even for fast-forward | `git merge --no-ff feature` |
| `--squash` | Combine all commits into single commit | `git merge --squash feature` |
| `--abort` | Abort merge in progress | `git merge --abort` |
| `-X` | Use merge strategy option | `git merge -X theirs feature` |

### git rebase
| Parameter | Purpose | Example Values |
|-----------|---------|----------------|
| `-i` | Interactive rebase | `git rebase -i HEAD~3` |
| `--onto` | Rebase onto different branch | `git rebase --onto main dev feature` |
| `--abort` | Abort rebase in progress | `git rebase --abort` |
| `--continue` | Continue rebase after resolving conflicts | `git rebase --continue` |

### git push
| Parameter | Purpose | Example Values |
|-----------|---------|----------------|
| `-u` | Set upstream tracking branch | `git push -u origin main` |
| `--force` | Force push (overwrites remote) | `git push --force` |
| `--force-with-lease` | Safer force push | `git push --force-with-lease` |
| `--tags` | Push tags along with commits | `git push --tags` |
| `--delete` | Delete remote branch | `git push --delete origin feature` |

### git pull
| Parameter | Purpose | Example Values |
|-----------|---------|----------------|
| `--rebase` | Rebase instead of merge | `git pull --rebase` |
| `--no-commit` | Don't automatically commit merge | `git pull --no-commit` |
| `--ff-only` | Only allow fast-forward merges | `git pull --ff-only` |

### git reset
| Parameter | Purpose | Example Values |
|-----------|---------|----------------|
| `--soft` | Reset HEAD only, keep changes staged | `git reset --soft HEAD~1` |
| `--mixed` | Reset HEAD and index (default) | `git reset --mixed HEAD~1` |
| `--hard` | Reset HEAD, index, and working directory | `git reset --hard HEAD~1` |

### git stash
| Parameter | Purpose | Example Values |
|-----------|---------|----------------|
| `push` | Save current changes | `git stash push -m "Work in progress"` |
| `pop` | Apply and remove latest stash | `git stash pop` |
| `list` | Show all stashes | `git stash list` |
| `drop` | Delete specific stash | `git stash drop stash@{0}` |
| `-u` | Include untracked files | `git stash push -u` |

## Common Development Workflows

### 1. Create Repository with Permissions

**Local Repository:**
```bash
# Initialize new repository
git init my-project
cd my-project

# Set user configuration (if not set globally)
git config user.name "Your Name"
git config user.email "your.email@example.com"

# Create initial commit
echo "# My Project" > README.md
git add README.md
git commit -m "Initial commit"
```

**Remote Repository (GitHub/GitLab):**
```bash
# Add remote origin
git remote add origin https://github.com/username/my-project.git

# Push to remote and set upstream
git push -u origin main

# Set branch protection (done via web interface)
# - Require pull request reviews
# - Require status checks
# - Restrict pushes to main branch
```

### 2. Branch Repository

```bash
# Create and switch to new branch
git checkout -b feature/user-authentication

# Or using newer syntax
git switch -c feature/user-authentication

# Push branch to remote and set upstream
git push -u origin feature/user-authentication

# List all branches
git branch -a
```

### 3. Clone Repository

```bash
# Clone repository
git clone https://github.com/username/project.git

# Clone specific branch
git clone -b develop https://github.com/username/project.git

# Clone with limited history (faster)
git clone --depth 1 https://github.com/username/project.git

# Navigate to cloned directory
cd project

# Verify remote configuration
git remote -v
```

### 4. Check-in Code to Branch

```bash
# Check current status
git status

# Stage specific files
git add src/auth.js src/login.html

# Or stage all changes
git add .

# Commit with descriptive message
git commit -m "feat: implement user authentication

- Add login form validation
- Integrate with OAuth provider
- Add session management"

# Push to remote branch
git push origin feature/user-authentication
```

### 5. Merging Two Branches

**Method 1: Merge Commit**
```bash
# Switch to target branch (usually main)
git checkout main

# Pull latest changes
git pull origin main

# Merge feature branch
git merge feature/user-authentication

# Push merged changes
git push origin main

# Delete feature branch (optional)
git branch -d feature/user-authentication
git push --delete origin feature/user-authentication
```

**Method 2: Squash Merge**
```bash
# Switch to main branch
git checkout main

# Squash merge (combines all commits into one)
git merge --squash feature/user-authentication

# Commit the squashed changes
git commit -m "feat: add user authentication system"

# Push changes
git push origin main
```

### 6. Rebase Workflow

**Interactive Rebase (Clean Up Commits):**
```bash
# Interactive rebase for last 3 commits
git rebase -i HEAD~3

# In the editor, you can:
# - pick: keep commit as-is
# - squash: combine with previous commit
# - reword: change commit message
# - drop: remove commit entirely
```

**Rebase Feature Branch onto Main:**
```bash
# Switch to feature branch
git checkout feature/user-authentication

# Fetch latest changes
git fetch origin

# Rebase onto main
git rebase origin/main

# If conflicts occur:
# 1. Resolve conflicts in files
# 2. Stage resolved files: git add .
# 3. Continue rebase: git rebase --continue

# Force push rebased branch (rewrites history)
git push --force-with-lease origin feature/user-authentication
```

### 7. Handling Merge Conflicts

```bash
# When merge/rebase fails due to conflicts
git status  # Shows conflicted files

# Edit conflicted files, remove conflict markers:
# <<<<<<< HEAD
# Your changes
# =======
# Their changes
# >>>>>>> branch-name

# Stage resolved files
git add conflicted-file.js

# Complete the merge
git commit  # For merge
# OR
git rebase --continue  # For rebase
```

### 8. Release Management with Tags

```bash
# Create annotated tag for release
git tag -a v1.0.0 -m "Release version 1.0.0"

# Push tags to remote
git push --tags

# List all tags
git tag -l

# Create tag from specific commit
git tag -a v1.0.1 9fceb02 -m "Hotfix release"

# Delete tag
git tag -d v1.0.0
git push --delete origin v1.0.0
```

### 9. Hotfix Workflow

```bash
# Create hotfix branch from main
git checkout main
git pull origin main
git checkout -b hotfix/critical-security-fix

# Make necessary fixes
git add .
git commit -m "fix: resolve security vulnerability"

# Push hotfix branch
git push -u origin hotfix/critical-security-fix

# Merge into main
git checkout main
git merge hotfix/critical-security-fix
git push origin main

# Also merge into develop (if using GitFlow)
git checkout develop
git merge hotfix/critical-security-fix
git push origin develop

# Clean up hotfix branch
git branch -d hotfix/critical-security-fix
git push --delete origin hotfix/critical-security-fix
```

### 10. Stashing Work in Progress

```bash
# Save current work without committing
git stash push -m "WIP: working on user profile page"

# Or include untracked files
git stash push -u -m "WIP: with new files"

# List all stashes
git stash list

# Apply latest stash and remove it
git stash pop

# Apply specific stash without removing
git stash apply stash@{1}

# Drop specific stash
git stash drop stash@{0}

# Clear all stashes
git stash clear
```

### 11. Undoing Changes

**Undo Last Commit (Keep Changes):**
```bash
git reset --soft HEAD~1
```

**Undo Last Commit (Discard Changes):**
```bash
git reset --hard HEAD~1
```

**Undo Changes to Specific File:**
```bash
git checkout -- filename.txt
# Or newer syntax:
git restore filename.txt
```

**Create Commit that Reverses Changes:**
```bash
git revert HEAD  # Revert last commit
git revert HEAD~2  # Revert commit from two commits ago
```

### 12. Working with Remote Repositories

```bash
# Add multiple remotes
git remote add upstream https://github.com/original/repo.git
git remote add origin https://github.com/yourfork/repo.git

# Fetch from upstream
git fetch upstream

# Sync fork with upstream
git checkout main
git merge upstream/main
git push origin main

# Change remote URL
git remote set-url origin https://github.com/newuser/repo.git
```

## Best Practices

- **Commit Messages**: Use conventional commits format (feat:, fix:, docs:, etc.)
- **Branch Naming**: Use descriptive names like `feature/user-auth` or `bugfix/login-error`
- **Pull Before Push**: Always `git pull` before pushing to avoid conflicts
- **Small Commits**: Make frequent, small commits rather than large ones
- **Review Changes**: Use `git diff` to review changes before committing
- **Backup Important Work**: Push branches to remote frequently
