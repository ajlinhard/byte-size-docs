# JS Cheatsheet 1 — Syntax, Execution & Functions

## 1. How JavaScript Actually Runs

JS runs in two main environments: the **browser** and **Node.js**. Same language core, different globals (`window`/`document` in browser, `process`/`module` in Node).

**Browser:**
```html
<script src="app.js"></script>                 <!-- blocks HTML parsing -->
<script src="app.js" defer></script>            <!-- runs after HTML parsed, in order -->
<script src="app.js" async></script>            <!-- runs as soon as loaded, order not guaranteed -->
<script type="module" src="app.js"></script>    <!-- enables import/export, deferred by default -->
```

**Node:**
```bash
node app.js
```
Set `"type": "module"` in `package.json` to use `import`/`export` instead of `require`.

**Strict mode** — catches silent errors (undeclared vars, duplicate params, etc.). Modules are strict by default; elsewhere opt in explicitly:
```js
'use strict';
```

## 2. Comments & Statement Termination

```js
// single line
/* multi
   line */
```

Semicolons are technically optional (Automatic Semicolon Insertion inserts them for you), but ASI has edge cases that break code — e.g. a `return` followed by a newline silently returns `undefined`:
```js
function broken() {
  return
  { value: 1 };   // unreachable — ASI inserted a semicolon after `return`
}
```
**Recommendation:** always write semicolons explicitly. It removes an entire category of bugs.

## 3. Variables — Quick Preview (full detail in Sheet 2)

```js
let x = 1;        // block-scoped, reassignable
const y = 2;       // block-scoped, cannot be reassigned (but object/array contents can mutate)
var z = 3;         // function-scoped, hoisted — avoid in modern code
```

- `let`/`const` are hoisted but live in a **"temporal dead zone"** until their declaration line — accessing early throws `ReferenceError`, unlike `var` which just gives `undefined`.
- Default to `const`. Use `let` only when you know you'll reassign. Avoid `var`.

## 4. Operators

| Category | Operators | Notes |
|---|---|---|
| Arithmetic | `+ - * / % **` | `**` is exponentiation |
| Comparison | `== === != !== > < >= <=` | **Always use `===`/`!==`** — `==` does type coercion (`0 == '0'` is `true`) |
| Logical | `&& \|\| !` | short-circuiting |
| Nullish coalescing | `??` | returns right side only if left is `null`/`undefined` (unlike `\|\|`, which also triggers on `0`, `''`, `false`) |
| Optional chaining | `?.` | `user?.address?.city` — stops and returns `undefined` if any link is nullish |
| Ternary | `cond ? a : b` | inline if/else |
| Logical assignment | `\|\|= &&= ??=` | e.g. `count ??= 0` |

```js
const name = user?.name ?? 'Anonymous'; // very common modern pattern
```

## 5. Control Flow

```js
if (score > 90) {
  grade = 'A';
} else if (score > 80) {
  grade = 'B';
} else {
  grade = 'C';
}

switch (status) {
  case 'pending':
    handlePending();
    break;
  case 'done':
    handleDone();
    break;
  default:
    handleUnknown();
}
```

**Loops:**
```js
for (let i = 0; i < 5; i++) { }          // classic counting loop
for (const item of iterable) { }          // values — arrays, strings, Maps, Sets
for (const key in object) { }             // keys — objects (avoid for arrays)
while (condition) { }
do { } while (condition);                 // runs at least once

outer: for (const a of listA) {
  for (const b of listB) {
    if (a === b) continue outer;          // labeled continue/break
  }
}
```
**Rule of thumb:** `for...of` for arrays/iterables, `Object.entries()` + `for...of` for objects (see Sheet 3), plain `for` when you need the index and control over stepping.

## 6. Scope & Closures

JS uses **lexical scoping** — a function can access variables from where it was *defined*, not where it's *called*.

```js
function makeCounter() {
  let count = 0;               // private to this closure
  return function () {
    count++;
    return count;
  };
}

const counter = makeCounter();
counter(); // 1
counter(); // 2 — count persisted between calls, and is inaccessible from outside
```
This is the mechanism behind private state, memoization, and the module pattern (Sheet 4).

## 7. Functions

```js
function add(a, b) { return a + b; }              // declaration — hoisted, can call before definition

const add2 = function (a, b) { return a + b; };    // expression — not hoisted

const add3 = (a, b) => a + b;                      // arrow — implicit return for single expression

const add4 = (a, b) => {                           // arrow with block body — needs explicit return
  return a + b;
};

function greet(name = 'friend') { }                // default parameter
function sum(...nums) { return nums.reduce((a, b) => a + b, 0); } // rest parameter — collects args into array
```

**Arrow functions vs regular functions — the key difference is `this`:**
```js
const obj = {
  name: 'Widget',
  regular() { console.log(this.name); },          // `this` = obj when called as obj.regular()
  arrow: () => { console.log(this.name); },        // `this` = enclosing scope, NOT obj — usually wrong here
};
```
Arrow functions don't have their own `this`, `arguments`, or `super` — they inherit from the enclosing scope. This makes them great for callbacks inside methods (see below) but wrong for object methods that need `this`.

```js
class Timer {
  seconds = 0;
  start() {
    // arrow function here inherits `this` from start() — correctly refers to the instance
    setInterval(() => { this.seconds++; }, 1000);
  }
}
```

**IIFE (Immediately Invoked Function Expression)** — runs once, creates an isolated scope. Mostly legacy now that modules exist, but you'll still see it:
```js
(function () {
  // private scope
})();
```

**Higher-order functions** — functions that take/return other functions. This is the backbone of array methods in Sheet 3:
```js
function withLogging(fn) {
  return (...args) => {
    console.log('calling with', args);
    return fn(...args);
  };
}
```

## 8. The `this` Keyword — Quick Reference

| Context | `this` refers to |
|---|---|
| Global scope (non-strict) | global object |
| Regular function (non-strict) | global object |
| Regular function (strict / module) | `undefined` |
| Object method | the object it was called on |
| Arrow function | enclosing lexical scope |
| Class method | the instance |
| `fn.call(obj)` / `fn.apply(obj)` | explicitly `obj` |
| `fn.bind(obj)` | returns new function permanently bound to `obj` |

```js
function whoAmI() { console.log(this.name); }
const person = { name: 'Ana' };
whoAmI.call(person);   // 'Ana'
const bound = whoAmI.bind(person);
bound();                // 'Ana'
```

## 9. Classes — Quick Preview (full detail in Sheet 4)

```js
class Animal {
  constructor(name) {
    this.name = name;
  }
  speak() {
    return `${this.name} makes a sound.`;
  }
}

const dog = new Animal('Rex');
dog.speak(); // "Rex makes a sound."
```

## 10. Modules — Quick Preview (full detail in Sheet 4)

```js
// math.js
export function add(a, b) { return a + b; }
export const PI = 3.14159;

// main.js
import { add, PI } from './math.js';
```

---
**Next:** Sheet 2 covers variable types in depth — primitives, objects, arrays, and advanced types like `Map` and `JSON`.
