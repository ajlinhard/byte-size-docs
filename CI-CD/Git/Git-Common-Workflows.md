# Git Common Workflows
These are some common workflows developers commonly encounter of 

## 1. Create Repository with Permissions

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

## 1: Refresh Your Code Branch
To pull the latest code from a remote git branch and update your local code, here are the steps:

### Basic Pull (if you're already on the correct branch)

```bash
git pull origin <branch-name>
```

For example, if you want to pull from the `main` branch:
```bash
git pull origin main
```

### Complete Workflow

1. **Check your current branch:**
   ```bash
   git branch
   ```

2. **Switch to the branch you want to update (if needed):**
   ```bash
   git checkout <branch-name>
   ```

3. **Pull the latest changes:**
   ```bash
   git pull origin <branch-name>
   ```

### Alternative Approach (Fetch + Merge)

You can also do this in two steps for more control:

```bash
# Fetch all remote changes
git fetch origin

# Merge the remote branch into your local branch
git merge origin/<branch-name>
```

### Handling Conflicts

If you have local changes that conflict with the remote changes:

1. **Stash your local changes first:**
   ```bash
   git stash
   git pull origin <branch-name>
   git stash pop
   ```

2. **Or commit your changes first:**
   ```bash
   git add .
   git commit -m "Your commit message"
   git pull origin <branch-name>
   ```

### Quick Tips

- `git pull` is essentially `git fetch` + `git merge`
- If you want to see what changes will be pulled without applying them, use `git fetch` followed by `git diff HEAD origin/<branch-name>`

## 2. Branch Repository

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

## 3. Clone Repository

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

## 4. Check-in Code to Branch

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

## 5. Merging Two Branches

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

## 6. Rebase Workflow

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

## 7. Handling Merge Conflicts

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

## 8. Release Management with Tags

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

## 9. Hotfix Workflow

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

## 10. Stashing Work in Progress

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

## 11. Undoing Changes

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

## 12. Working with Remote Repositories

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

- Use `git status` to check if your local branch is behind the remote

The most common command you'll use is simply `git pull origin main` (or whatever your main branch is called).
