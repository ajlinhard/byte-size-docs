#Git Merge Shortcuts
After running `git merge --continue`, Git opens your default text editor (like Vim, Nano, or whatever you've configured) to let you edit the merge commit message. The commands you see depend on which editor opens:

## If Vim Opens (most common)

You'll see the merge commit message with instructions at the bottom. Vim commands:

- **`i`** - Enter insert mode to edit the message
- **`Esc`** - Exit insert mode back to normal mode
- **`:wq`** or **`:x`** - Save and quit (complete the merge)
- **`:q!`** - Quit without saving (abort the merge)
- **`dd`** - Delete the current line (in normal mode)
- **`o`** - Open a new line below and enter insert mode

## If Nano Opens

You'll see commands at the bottom of the screen:

- **`Ctrl+O`** - Write out (save) the file
- **`Enter`** - Confirm the filename
- **`Ctrl+X`** - Exit Nano (completes the merge)
- **`Ctrl+K`** - Cut/delete a line
- **`Ctrl+G`** - Get help

## If VS Code or Another GUI Editor Opens

Just edit the message, save the file (`Ctrl+S` or `Cmd+S`), and close the editor window.

## Default Merge Message

The file typically contains something like:
```
Merge branch 'feature-branch' into main

# Please enter a commit message to explain why this merge is necessary,
# especially if it merges an updated upstream into a topic branch.
# Lines starting with '#' will be ignored, and an empty message aborts the commit.
```

You can keep the default message or customize it. Once you save and close the editor, the merge completes!
