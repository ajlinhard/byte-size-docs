# Git Config File Types
---

## `.gitignore`
Tells Git which files/folders to completely ignore and never track.

```gitignore
# Dependencies
node_modules/
vendor/

# Build output
dist/
*.exe
*.o

# Environment / secrets
.env
.env.local
*.pem

# OS junk
.DS_Store
Thumbs.db

# Logs
*.log
logs/
```

**Pattern rules:**
| Pattern | Meaning |
|---|---|
| `*.log` | Any file ending in `.log` |
| `logs/` | A directory named `logs` |
| `!important.log` | Un-ignore (negate) a specific file |
| `**/temp` | `temp` folder anywhere in the tree |
| `doc/*.txt` | Only `.txt` files directly in `doc/` |
| `#` | Comment |

---

## `.gitattributes`
Controls how Git treats files — line endings, diffs, merges, and more.

```gitattributes
# Force LF line endings for these types
*.sh        text eol=lf
*.sql       text eol=lf
*.yml       text eol=lf

# Force CRLF (e.g. Windows batch files)
*.bat       text eol=crlf
*.cmd       text eol=crlf

# Mark as binary (no line ending conversion, no text diffs)
*.png       binary
*.jpg       binary
*.pdf       binary
*.zip       binary

# Use a custom diff driver for a file type
*.json      diff=json

# Exclude files from `git archive` exports
.gitignore  export-ignore
docs/       export-ignore

# Mark generated files so GitHub collapses their diffs
*.min.js    linguist-generated=true

# Tell GitHub to not count a file toward language stats
vendor/**   linguist-vendored=true
```

**Key attributes:**
| Attribute | Meaning |
|---|---|
| `text` | Treat as text; Git normalizes line endings |
| `text eol=lf` | Always store/checkout with LF |
| `text eol=crlf` | Always store/checkout with CRLF |
| `binary` | Shorthand for `-text -diff` — no conversion, no text diff |
| `-text` | Disable line ending normalization |
| `diff=<driver>` | Use a named diff driver |
| `merge=<driver>` | Use a custom merge strategy |
| `export-ignore` | Exclude from `git archive` (e.g. release zips) |
| `linguist-generated` | GitHub hides from diffs and language stats |
| `linguist-vendored` | GitHub excludes from language stats |
| `linguist-language` | Override what language GitHub detects |

---

## `.gitmodules`
Defines **submodules** — other Git repos nested inside your repo.

```ini
[submodule "libs/somelibrary"]
    path = libs/somelibrary
    url = https://github.com/example/somelibrary.git
    branch = main

[submodule "tools/mytool"]
    path = tools/mytool
    url = git@github.com:example/mytool.git
```

**Options:**
| Option | Meaning |
|---|---|
| `path` | Where the submodule is checked out locally |
| `url` | Remote URL of the submodule repo |
| `branch` | Branch to track (optional) |
| `shallow` | Set to `true` to do a shallow clone |
| `update` | Strategy: `checkout`, `rebase`, `merge` |

You don't usually edit this by hand — it's managed via `git submodule add`.

---

## `.gitconfig` / `.git/config`
Repository-level Git configuration (overrides global `~/.gitconfig` for this repo only).

```ini
[core]
    autocrlf = false
    fileMode = false
    ignorecase = false

[remote "origin"]
    url = git@github.com:yourname/yourrepo.git
    fetch = +refs/heads/*:refs/remotes/origin/*

[branch "main"]
    remote = origin
    merge = refs/heads/main

[user]
    email = work@company.com   # override personal global config

[alias]
    lg = log --oneline --graph --decorate
```

This file lives at `.git/config` (inside the `.git` folder) and is not committed — it's local to your machine.

---

## `.mailmap`
Normalizes author names/emails in `git log` and `git shortlog` — useful when someone has committed under multiple identities.

```
# Canonical Name <canonical@email.com> <old@email.com>
Jane Doe <jane@company.com> <jane@oldcompany.com>
Jane Doe <jane@company.com> <jdoe@gmail.com>
```

---

## `.gitkeep`
Not an official Git file — just a convention. Git can't track empty directories, so developers drop an empty `.gitkeep` file inside them as a placeholder.

```
logs/
└── .gitkeep    ← keeps the empty folder tracked
```

---

## Summary

| File | Committed? | Purpose |
|---|---|---|
| `.gitignore` | ✅ | Ignore files from tracking |
| `.gitattributes` | ✅ | Line endings, diffs, merge behavior |
| `.gitmodules` | ✅ | Submodule definitions |
| `.mailmap` | ✅ | Normalize author identities |
| `.gitkeep` | ✅ | Placeholder for empty directories |
| `.git/config` | ❌ | Local repo settings (not shared) |

The ones you'll use most often day-to-day are `.gitignore` and `.gitattributes`.
