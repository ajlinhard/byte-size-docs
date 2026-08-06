# JS Cheatsheet 4 — Classes, Patterns & Project Setup

## 1. Class Syntax In Depth

```js
class Animal {
  species = 'unknown';           // instance field, set on every instance before the constructor body runs
  #secret = 'private';            // private field — only accessible inside this class

  static count = 0;               // static field — belongs to the class, not instances
  static #registry = [];          // private static field

  constructor(name) {
    this.name = name;
    Animal.count++;
    Animal.#registry.push(name);
  }

  speak() {                        // instance method
    return `${this.name} makes a sound.`;
  }

  #privateMethod() {                // private method — internal use only
    return this.#secret;
  }

  get displayName() {                // getter — accessed like a property, not called like a method
    return `[${this.name}]`;
  }
  set displayName(value) {           // setter
    this.name = value.replace(/[[\]]/g, '');
  }

  static create(name) {              // static method — called as Animal.create(...), not on instances
    return new Animal(name);
  }

  static {                            // static initialization block — runs once when the class is defined
    console.log('Animal class loaded');
  }
}

const cat = new Animal('Whiskers');
cat.displayName;             // '[Whiskers]' — getter, no parens
cat.displayName = 'Tom';      // setter
Animal.count;                  // static, accessed on the class
```

**Inheritance:**
```js
class Dog extends Animal {
  constructor(name, breed) {
    super(name);              // MUST call super() before using `this` in a subclass constructor
    this.breed = breed;
  }
  speak() {                    // overrides Animal.speak
    return `${super.speak()} Specifically, a bark.`;  // super.method() calls the parent version
  }
}

const rex = new Dog('Rex', 'Labrador');
rex instanceof Dog;      // true
rex instanceof Animal;    // true — inheritance chain
```

**Private fields (`#`)** are enforced by the language, not just convention — code outside the class genuinely cannot access `cat.#secret`. This is different from the old convention of naming things `_secret` (which is just a hint, not enforcement).

## 2. Common Class Patterns

**Factory function** — when you want object creation logic without the ceremony (or inheritance semantics) of a class:
```js
function createUser(name, role) {
  return {
    name,
    role,
    isAdmin: role === 'admin',
  };
}
```
Use a factory when objects don't need inheritance and you want plain, easily-serializable data. Use a class when you need shared behavior across many instances, inheritance, or private state.

**Singleton** — ensure only one instance ever exists (common for things like a config manager or a DB connection):
```js
class Config {
  static #instance;
  #settings = {};

  static getInstance() {
    if (!Config.#instance) {
      Config.#instance = new Config();
    }
    return Config.#instance;
  }
}
const config = Config.getInstance();
```
In modern JS, a module (see below) often replaces this pattern entirely — a module's top-level state is naturally singleton-like, since `import` always gives you the same instance.

**Mixins** — JS classes only support single inheritance (`extends` one class), so mixins simulate multiple inheritance by composing behavior:
```js
const Serializable = (Base) => class extends Base {
  serialize() { return JSON.stringify(this); }
};

class Model {}
class User extends Serializable(Model) {}
```

**Module pattern** — in modern JS, ES modules (below) do this natively. You rarely need the old closure-based version, but recognize it in legacy code:
```js
const counterModule = (function () {
  let count = 0;                       // private, closed over
  return {
    increment: () => ++count,
    getCount: () => count,
  };
})();
```

## 3. Modules (`import`/`export`) In Depth

```js
// utils.js
export function formatDate(date) { }         // named export
export const API_URL = 'https://...';         // named export
export default class ApiClient { }             // default export — one per file

// main.js
import ApiClient, { formatDate, API_URL } from './utils.js';   // default + named together
import * as utils from './utils.js';            // namespace import — utils.formatDate(...)
import { formatDate as fmt } from './utils.js';   // rename on import
```
**CommonJS (older Node style, still common)** — you'll see this in older codebases and some Node configs:
```js
// export
module.exports = { formatDate, API_URL };
// import
const { formatDate, API_URL } = require('./utils');
```
Whether a project uses ESM or CommonJS is controlled by `"type": "module"` in `package.json` (or `.mjs`/`.cjs` file extensions).

## 4. Setting Up a Project

```bash
mkdir my-project && cd my-project
npm init -y                  # generates package.json with defaults
```

**`package.json` anatomy:**
```json
{
  "name": "my-project",
  "version": "1.0.0",
  "type": "module",
  "main": "src/index.js",
  "scripts": {
    "start": "node src/index.js",
    "test": "node --test",
    "lint": "eslint ."
  },
  "dependencies": { "express": "^4.19.0" },
  "devDependencies": { "eslint": "^9.0.0" }
}
```

```bash
npm install express            # adds to dependencies, installs into node_modules/
npm install --save-dev eslint   # adds to devDependencies (build/lint tools, not shipped to prod)
npm run lint                    # runs the "lint" script
```

**Files you'll want:**
```
my-project/
  src/
    index.js
  tests/
  node_modules/     ← generated, never commit this
  package.json
  package-lock.json ← commit this, locks exact dependency versions
  .gitignore         ← should include node_modules/, .env, dist/
  .env               ← local secrets/config, never commit this
```

**`.gitignore` starter:**
```
node_modules/
.env
dist/
*.log
```

## 5. Tooling You'll Run Into (Overview Only)

You don't need to master these yet, but you should recognize the names:

| Tool | Purpose |
|---|---|
| **ESLint** | catches bugs and enforces code style rules |
| **Prettier** | auto-formats code consistently |
| **Vite** | fast dev server + bundler for frontend projects |
| **webpack** | older, more configurable bundler |
| **Babel** | transpiles modern JS to run on older environments |
| **TypeScript** | adds static types on top of JS (worth learning after you're solid on plain JS) |
| **Node's built-in test runner** (`node --test`) | no dependency needed for basic testing |
| **Vitest / Jest** | fuller-featured testing frameworks |

---
**That's the full set.** A sensible order to actually read them in: Sheet 1 → Sheet 2 → Sheet 3 → Sheet 4, since each one leans lightly on ideas from the last.
