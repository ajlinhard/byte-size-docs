## `git stash` behavior

By default, `git stash` saves **both** staged (git added) and unstaged changes — then reverts your working directory to the last commit (`HEAD`).

Here's exactly what it does with each state:

| File State | Default `git stash` | `git stash -u` | `git stash --index` |
|---|---|---|---|
| **Staged** (`git add`ed) | ✅ Stashed (but unstaged on pop) | ✅ Stashed | ✅ Stashed & staging preserved |
| **Unstaged (tracked)** | ✅ Stashed | ✅ Stashed | ✅ Stashed |
| **Untracked** (new files, not added) | ❌ Left alone | ✅ Stashed | ❌ Left alone |
| **Ignored files** | ❌ Left alone | ❌ Left alone | ❌ Left alone |

### Key nuance — staging is lost on pop

Even though staged files *are* stashed, when you run `git stash pop`, everything comes back as **unstaged** by default. To restore the staged/unstaged distinction, use:

```bash
git stash pop --index
# or when stashing:
git stash --index
```

### Common flags

```bash
git stash              # stash staged + unstaged tracked changes
git stash -u           # also stash untracked files
git stash -a           # stash everything including ignored files
git stash --index      # preserve the staged vs unstaged distinction
```

### What it never touches
- **Commits** — stash has no effect on your commit history whatsoever. It only operates on uncommitted changes (working tree + index).
