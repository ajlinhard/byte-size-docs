# Git Commands

Here is Git command line cheatsheet that covers all the areas you requested. The cheatsheet includes:

**Quick Reference Table** - All essential Git commands with their parameters and descriptions for easy lookup.

**Detailed Sections** covering:
- Setting up new repositories (local and remote)
- Basic workflow for pulling and committing code
- Branch creation, management, and cleanup
- Merging strategies and workflows
- Comprehensive conflict resolution techniques
- Advanced scenarios like interactive rebasing, stashing, and cherry-picking

The examples progress from basic to advanced, showing real command sequences you'd use in typical development workflows. Each section includes practical scenarios you'll encounter when working with Git, from simple daily operations to complex conflict resolution situations.

The conflict resolution section is particularly detailed, covering manual resolution, merge tools, and strategies to prevent conflicts in the first place. This should give you a solid reference for handling even tricky merge situations.
---
# Git Command Line Cheatsheet

## Essential Git Commands Reference

| Command | Parameters | Description |
|---------|------------|-------------|
| `git init` | `[directory]` | Initialize a new Git repository |
| `git clone` | `<url> [directory]` | Clone a remote repository |
| `git add` | `<file>` or `.` or `-A` | Stage files for commit |
| `git commit` | `-m "message"` | Commit staged changes |
| `git status` | | Show working directory status |
| `git log` | `--oneline`, `--graph`, `-n <number>` | View commit history |
| `git diff` | `[file]`, `--staged` | Show changes between commits/staging |
| `git push` | `[remote] [branch]` | Push commits to remote repository |
| `git pull` | `[remote] [branch]` | Fetch and merge from remote |
| `git fetch` | `[remote]` | Download objects from remote |
| `git branch` | `[branch-name]`, `-d`, `-D`, `-a` | List, create, or delete branches |
| `git checkout` | `<branch>`, `-b <new-branch>` | Switch branches or create new |
| `git switch` | `<branch>`, `-c <new-branch>` | Modern way to switch branches |
| `git merge` | `<branch>` | Merge branch into current branch |
| `git rebase` | `<branch>`, `-i` | Reapply commits on another base |
| `git reset` | `--soft`, `--mixed`, `--hard` | Reset current HEAD |
| `git revert` | `<commit>` | Create new commit that undoes changes |
| `git stash` | `push`, `pop`, `list`, `drop` | Temporarily store changes |
| `git remote` | `add`, `remove`, `-v` | Manage remote repositories |

## Setting Up a New Repository

### Creating a new local repository
```bash
# Create and navigate to project directory
mkdir my-project
cd my-project

# Initialize Git repository
git init

# Create initial files
echo "# My Project" > README.md
echo "node_modules/" > .gitignore

# Stage and commit initial files
git add .
git commit -m "Initial commit"
```

### Connecting to a remote repository
```bash
# Add remote origin
git remote add origin https://github.com/username/my-project.git

# Verify remote
git remote -v

# Push to remote (set upstream)
git push -u origin main
```

### Cloning an existing repository
```bash
# Clone repository
git clone https://github.com/username/existing-project.git

# Navigate to cloned directory
cd existing-project

# Check status and remotes
git status
git remote -v
```

## Pulling and Committing Code

### Basic workflow for changes
```bash
# Check current status
git status

# Stage specific files
git add file1.js file2.css

# Or stage all changes
git add .

# Commit with message
git commit -m "Add new feature for user authentication"

# Push to remote
git push origin main
```

### Pulling latest changes
```bash
# Fetch and merge from remote
git pull origin main

# Or fetch first, then merge
git fetch origin
git merge origin/main
```

### Viewing changes before committing
```bash
# See unstaged changes
git diff

# See staged changes
git diff --staged

# View commit history
git log --oneline --graph -10
```

### Amending commits
```bash
# Modify the last commit message
git commit --amend -m "Corrected commit message"

# Add files to the last commit
git add forgotten-file.js
git commit --amend --no-edit
```

## Branching a Repository

### Creating and switching branches
```bash
# Create new branch and switch to it
git checkout -b feature/user-login

# Modern syntax (Git 2.23+)
git switch -c feature/user-login

# Create branch without switching
git branch feature/user-login

# Switch to existing branch
git checkout feature/user-login
git switch feature/user-login
```

### Working with branches
```bash
# List all branches
git branch -a

# List remote branches
git branch -r

# Delete local branch
git branch -d feature/user-login

# Force delete unmerged branch
git branch -D feature/user-login

# Delete remote branch
git push origin --delete feature/user-login
```

### Tracking remote branches
```bash
# Create local branch tracking remote
git checkout -b feature/user-login origin/feature/user-login

# Set upstream for existing branch
git branch --set-upstream-to=origin/feature/user-login feature/user-login

# Push new branch and set upstream
git push -u origin feature/user-login
```

## Merging Repositories

### Basic merge workflow
```bash
# Switch to target branch (usually main)
git checkout main

# Ensure you have latest changes
git pull origin main

# Merge feature branch
git merge feature/user-login

# Push merged changes
git push origin main

# Clean up - delete feature branch
git branch -d feature/user-login
git push origin --delete feature/user-login
```

### Merge strategies
```bash
# Fast-forward merge (default when possible)
git merge feature/user-login

# Create merge commit even if fast-forward is possible
git merge --no-ff feature/user-login

# Squash all commits into one
git merge --squash feature/user-login
git commit -m "Add user login feature"
```

### Alternative: Rebase instead of merge
```bash
# Switch to feature branch
git checkout feature/user-login

# Rebase onto main
git rebase main

# Switch back to main and merge
git checkout main
git merge feature/user-login
```

## Resolving Merge Conflicts

### When conflicts occur
```bash
# Attempt merge
git merge feature/user-login
# Auto-merging src/app.js
# CONFLICT (content): Merge conflict in src/app.js
# Automatic merge failed; fix conflicts and then commit the result.

# Check status
git status
# On branch main
# You have unmerged paths.
# Unmerged paths:
#   both modified:   src/app.js
```

### Resolving conflicts manually
```bash
# Open conflicted file in editor
# Look for conflict markers:
# <<<<<<< HEAD
# code from current branch
# =======
# code from merging branch
# >>>>>>> feature/user-login

# Edit file to resolve conflicts, then:
git add src/app.js
git commit -m "Resolve merge conflict in app.js"
```

### Using merge tools
```bash
# Configure merge tool (one-time setup)
git config --global merge.tool vimdiff
# or: code, meld, kdiff3, etc.

# Launch merge tool for conflicts
git mergetool

# After resolving, commit
git commit -m "Resolve merge conflicts"
```

### Advanced conflict resolution
```bash
# Show conflict in 3-way format
git checkout --conflict=diff3 src/app.js

# Abort merge and start over
git merge --abort

# Show what changed in each branch
git log --merge --left-right --oneline

# Choose one side entirely
git checkout --theirs src/app.js  # Use their version
git checkout --ours src/app.js    # Use our version
git add src/app.js
git commit -m "Resolve conflict using their/our changes"
```

### Preventing conflicts
```bash
# Rebase feature branch before merging
git checkout feature/user-login
git rebase main
git checkout main
git merge feature/user-login

# Use smaller, frequent commits
# Communicate with team about file changes
# Use .gitattributes for consistent line endings
```

## Advanced Scenarios

### Interactive rebase for cleaning history
```bash
# Interactive rebase last 3 commits
git rebase -i HEAD~3

# Options in interactive mode:
# pick = use commit
# reword = use commit, but edit message
# edit = use commit, but stop for amending
# squash = use commit, but meld into previous
# fixup = like squash, but discard log message
# drop = remove commit
```

### Stashing work in progress
```bash
# Stash current changes
git stash push -m "Work in progress on user auth"

# List stashes
git stash list

# Apply most recent stash
git stash pop

# Apply specific stash
git stash apply stash@{1}

# Drop specific stash
git stash drop stash@{1}
```

### Cherry-picking commits
```bash
# Apply specific commit to current branch
git cherry-pick abc1234

# Cherry-pick range of commits
git cherry-pick abc1234..def5678

# Cherry-pick without committing
git cherry-pick --no-commit abc1234
```

### Undoing changes
```bash
# Unstage files
git reset HEAD file.js

# Discard working directory changes
git checkout -- file.js

# Reset to previous commit (keep changes staged)
git reset --soft HEAD~1

# Reset to previous commit (discard changes)
git reset --hard HEAD~1

# Create new commit that undoes previous commit
git revert HEAD
```

## Quick Reference Tips

- Use `git status` frequently to understand repository state
- Always pull before pushing to avoid conflicts
- Write clear, descriptive commit messages
- Use branches for features and bug fixes
- Test code before committing
- Use `.gitignore` to exclude unnecessary files
- Configure Git with your name and email: `git config --global user.name "Your Name"` and `git config --global user.email "your.email@example.com"`
