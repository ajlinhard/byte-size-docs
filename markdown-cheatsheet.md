# Markdown Syntax Cheatsheet

## Basic Text Formatting

| Element | Syntax | Example |
|---------|--------|---------|
| Heading 1 | `# Heading 1` | <h1>Heading 1</h1> |
| Heading 2 | `## Heading 2` | <h2>Heading 2</h2> |
| Heading 3 | `### Heading 3` | <h3>Heading 3</h3> |
| Heading 4 | `#### Heading 4` | <h4>Heading 4</h4> |
| Heading 5 | `##### Heading 5` | <h5>Heading 5</h5> |
| Heading 6 | `###### Heading 6` | <h6>Heading 6</h6> |
| Bold | `**bold text**` or `__bold text__` | **bold text** |
| Italic | `*italic text*` or `_italic text_` | *italic text* |
| Bold & Italic | `***bold and italic***` | ***bold and italic*** |
| Strikethrough | `~~strikethrough~~` | ~~strikethrough~~ |

## Links and Images

| Element | Syntax | Example |
|---------|--------|---------|
| Link | `[link text](URL)` | [link text](https://example.com) |
| Image | `![alt text](URL)` | ![alt text](image.jpg) |
| Link with Title | `[link text](URL "title")` | [link text](https://example.com "title") |
| Reference-style Link | `[link text][reference]` then `[reference]: URL` | [link text][1] |
| | | [1]: https://example.com |

## Lists

| Element | Syntax | Example |
|---------|--------|---------|
| Unordered List | `- Item` or `* Item` or `+ Item` | • Item |
| Ordered List | `1. Item` | 1. Item |
| Nested List | Indent with spaces | • Main item<br>&nbsp;&nbsp;• Sub-item |
| Task List | `- [ ] Task` or `- [x] Completed Task` | ☐ Task<br>☑ Completed Task |

## Code

| Element | Syntax | Example |
|---------|--------|---------|
| Inline Code | `` `code` `` | `code` |
| Code Block | ``````` <br> ```language <br> code block <br> ``` <br> ``````` | ```python<br>print("Hello World")<br>``` |

## Blockquotes and Horizontal Rules

| Element | Syntax | Example |
|---------|--------|---------|
| Blockquote | `> quote` | > This is a blockquote |
| Nested Blockquote | `> quote` <br> `>> nested quote` | > Quote <br> >> Nested quote |
| Horizontal Rule | `---` or `***` or `___` | --- |

## Tables

```
| Header 1 | Header 2 |
|----------|----------|
| Cell 1   | Cell 2   |
| Cell 3   | Cell 4   |
```

| Header 1 | Header 2 |
|----------|----------|
| Cell 1   | Cell 2   |
| Cell 3   | Cell 4   |

### Table Alignment

```
| Left-aligned | Center-aligned | Right-aligned |
|:-------------|:--------------:|---------------:|
| Left         | Center         | Right          |
```

## Escaping Characters

Use backslash `\` to escape characters like: \* \_ \` \# \[ \] \( \) \+ \- \. \! \|

## Extended Syntax (Note: Support varies by platform)

| Element | Syntax | Example |
|---------|--------|---------|
| Footnote | `Text[^1]` and `[^1]: Footnote content` | Text[^1] |
| | | [^1]: This is a footnote |
| Definition List | `Term` <br> `: Definition` | Term<br>: Definition |
| Highlighted Text | `==highlighted text==` | ==highlighted text== |
| Subscript | `H~2~O` | H~2~O |
| Superscript | `X^2^` | X^2^ |
| Emoji | `:emoji_code:` | :smile: |
| Comment | `[comment]: # (This is a comment)` | <!-- This is a comment --> |

---
## Making Anchors and Table of Contents
To create links to sections within the same Markdown document, you use what are called "anchor links" or "fragment identifiers." Here's how to do it:

1. Identify the section heading you want to link to
2. Create an ID based on that heading by:
   - Converting to lowercase
   - Replacing spaces with hyphens
   - Removing punctuation

Then create a link using that ID with a hash (#) symbol.

For example, if you have a heading in your document:

```markdown
## Installation Instructions
```

You can link to it from elsewhere in the document with:

```markdown
[Go to installation section](#installation-instructions)
```

### Examples

**Linking to sections:**
```markdown
# My Document

## Table of Contents
- [Introduction](#introduction)
- [Getting Started](#getting-started)
- [Advanced Usage](#advanced-usage)

## Introduction
Content here...

## Getting Started
Content here...

## Advanced Usage
Content here...
```

**For headings with punctuation:**
If you have a heading like `## What's New?`, the ID would typically be `#whats-new`.

**Manual ID assignment:**
Some Markdown processors allow you to manually assign IDs to headings:

```markdown
## Installation {#custom-id}

[Link to installation](#custom-id)
```

Note that the exact formatting of auto-generated IDs can vary slightly between different Markdown processors, but the general approach is the same. If the link isn't working, check how your specific Markdown processor handles heading IDs.

## Links to Other Markdown Project Files
Yes, you can link to another Markdown file within the same project. The method for doing this depends on the relative location of the files. Here are the different approaches:

### Basic Linking to Other Markdown Files

```markdown
[Link text](filename.md)
```

### Linking Based on File Location

**For files in the same directory:**
```markdown
[Link text](filename.md)
```

**For files in subdirectories:**
```markdown
[Link text](subfolder/filename.md)
```

**For files in parent directories:**
```markdown
[Link text](../filename.md)
```

**For files in sibling directories:**
```markdown
[Link text](../other-folder/filename.md)
```

### Linking to Specific Sections in Other Files

You can also link to specific sections in other Markdown files by combining the file path with section anchors:

```markdown
[Link text](filename.md#section-name)
[Link text](subfolder/filename.md#section-name)
```

### Important Notes

1. Most Markdown renderers (like GitHub, GitLab, etc.) will automatically handle these links correctly.
2. When rendered to HTML, some platforms will convert the `.md` extension to `.html`, so your links will still work properly.
3. For documentation websites generated from Markdown (like MkDocs, Jekyll, etc.), the way paths are resolved might vary based on the configuration.
4. Some systems might require you to omit the `.md` extension, depending on how they process Markdown.
5. File and directory paths are case-sensitive on most systems, so ensure your capitalization matches exactly.

These relative links are especially useful in Git repositories and documentation projects where maintaining a consistent structure between Markdown files is important.