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

