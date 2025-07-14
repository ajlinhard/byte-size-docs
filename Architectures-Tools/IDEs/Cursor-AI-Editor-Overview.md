# Cursor AI Editor
As teams start to look to leverage AI the AI Code Editors seems to be taking off. The major editors are Cursor, Augment Code, and some other projects. Here is some info on getting started.

### Documents and Tutorials
- [Curosr Home Page](https://cursor.com/home)
- [Youtube - Cursor Tutorial (Volo Builds)](https://www.youtube.com/watch?v=3289vhOUdKA&t=536s)



## Cursor Rules
When using cursor rules (typically in a `.cursorrules` file), these are the three key settings you can configure:

## description
This is a human-readable explanation of what the rule does. It helps you and your team understand the purpose of each rule when reviewing or maintaining the cursor rules configuration.

```
description: "Enforce TypeScript strict mode and consistent naming conventions"
```

## globs
This specifies which files or file patterns the rule should apply to using glob patterns. It determines the scope of where the rule will be active.

```
globs: ["**/*.ts", "**/*.tsx", "src/**/*.js"]
```

Common glob patterns:
- `**/*.ts` - All TypeScript files recursively
- `src/**/*` - All files in the src directory and subdirectories
- `*.{js,jsx,ts,tsx}` - JavaScript and TypeScript files in current directory
- `!node_modules/**` - Exclude node_modules directory

## alwaysApply
This is a boolean setting that determines whether the rule should be applied even when it might conflict with other rules or user preferences. When set to `true`, the rule takes precedence.

```
alwaysApply: true
```

Here's an example of how these work together:

```yaml
rules:
  - description: "Use functional components and hooks in React files"
    globs: ["**/*.jsx", "**/*.tsx"]
    alwaysApply: false
    
  - description: "Enforce strict TypeScript configuration"
    globs: ["**/*.ts", "**/*.tsx"]
    alwaysApply: true
```

The `alwaysApply` setting is particularly useful for critical rules that should never be overridden, such as security practices or mandatory coding standards.
