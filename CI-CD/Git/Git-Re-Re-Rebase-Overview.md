# Git Rebase
When you encounter merge conflicts during a merge request, you typically have these options:

Links:
- [GitLab Rebase](https://docs.gitlab.com/topics/git/git_rebase/#resolve-conflicts-from-the-command-line)

## **Main Options for Resolving Conflicts**

1. **Resolve locally** - Download the code to your machine and resolve conflicts there
2. **Resolve in the web interface** - Many platforms (GitLab, GitHub, Bitbucket) offer web-based conflict editors
3. **Accept theirs/ours** - Automatically take one side's changes entirely (if available)

## **How Resolving Locally Works**

Here's the typical workflow:

**1. Fetch and checkout the branch:**
```bash
git fetch origin
git checkout feature-branch
```

**2. Merge or rebase with the target branch:**
```bash
# Option A: Merge
git merge main

# Option B: Rebase (cleaner history)
git rebase main
```

**3. Git marks conflicts in files:**
```
<<<<<<< HEAD
your changes
=======
their changes
>>>>>>> main
```

**4. Manually edit files** to resolve conflicts - remove the markers and keep the code you want

**5. Mark as resolved:**
```bash
git add resolved-file.txt
```

**6. Complete the merge/rebase:**
```bash
# For merge:
git commit

# For rebase:
git rebase --continue
```

**7. Push back to remote:**
```bash
git push origin feature-branch
# Or force push if you rebased:
git push origin feature-branch --force-with-lease
```

**Benefits of resolving locally:**
- Use your preferred IDE/editor with better conflict visualization
- Test the code after resolving
- Handle complex conflicts more easily
- Use merge tools like `git mergetool`

## **What Happens During a Rebase**

Think of it like this: rebase "picks up" your commits and replays them on top of the latest version of the target branch.

**Before rebase:**
```
main:     A---B---C
               \
feature:        D---E---F
```

**After `git rebase main`:**
```
main:     A---B---C
                   \
feature:            D'---E'---F'
```

## **Behind the Scenes**

1. **Git temporarily saves your commits** - It identifies all commits unique to your branch (D, E, F)

2. **Moves your branch pointer** to the tip of main (commit C)

3. **Replays each commit one by one**:
   - Applies commit D's changes → creates new commit D'
   - Applies commit E's changes → creates new commit E'
   - Applies commit F's changes → creates new commit F'

4. **Creates new commit hashes** - D', E', F' are technically new commits (different SHA hashes) even though they contain the same logical changes

5. **If conflicts occur** during any replay, Git pauses and asks you to resolve them, then continues

## **Why Main Isn't Affected**

- Rebase is a **local operation** on your branch only
- Main's commit history never changes
- Your branch pointer moves; main's pointer stays put
- Main only gets updated later when you merge/push your feature branch

## **Important Note**

Since rebase creates new commits (D', E', F'), if you've already pushed your feature branch, you'll need to force push:
```bash
git push --force-with-lease origin feature-branch
```

This is why you should **never rebase branches that others are working on** - it rewrites history!

## **During a Rebase: The Terminology Flip**
This is **super confusing** because the labels seem backwards during a rebase!

When you run `git rebase main` from your feature branch:

**"Current" (or "Ours")** = The branch you're rebasing ONTO (main)
- The changes already in main
- The "base" you're building on top of

**"Incoming" (or "Theirs")** = YOUR branch's changes being replayed
- Your feature branch commits
- The changes being applied one by one

## **Why It's Backwards**

During rebase, Git temporarily:
1. Checks out the target branch (main) 
2. Then applies YOUR commits on top of it one at a time

So from Git's perspective, main becomes "current" and your changes become "incoming" even though it feels like the opposite!

## **Practical Example**

```bash
git rebase main  # Conflict occurs
```

If you see:
```
<<<<<<< HEAD (current)
function foo() { return 42; }  // from main
=======
function foo() { return 100; } // your change
>>>>>>> your-commit (incoming)
```

- **Accept Current** = Keep main's version (42)
- **Accept Incoming** = Keep your version (100)

## **Compare to Merge**

During a regular **merge**, it's intuitive:
```bash
git merge feature-branch
```
- **Current/Ours** = Your current branch
- **Incoming/Theirs** = The branch being merged in

## **Pro Tip**

Many developers find this confusing, so:
- Always double-check which is which before accepting
- Read the actual code, not just the labels
- Use `git rebase --abort` if you get confused and want to start over
