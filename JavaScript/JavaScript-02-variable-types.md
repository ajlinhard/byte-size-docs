# JS Cheatsheet 2 — Variable Types

## 1. The Primitive Types

JS has 7 primitive types. Primitives are immutable and compared **by value**.

```js
typeof 'hello'      // 'string'
typeof 42            // 'number'
typeof 42n           // 'bigint'
typeof true           // 'boolean'
typeof undefined      // 'undefined'
typeof null           // 'object'  ← famous historical bug, null is NOT an object
typeof Symbol('id')   // 'symbol'
```

| Type | Example | Notes |
|---|---|---|
| `string` | `'hi'`, `"hi"`, `` `hi ${name}` `` | template literals support interpolation & multi-line |
| `number` | `42`, `3.14`, `NaN`, `Infinity` | one type for all numbers — no separate int/float |
| `bigint` | `42n` | for integers beyond `Number.MAX_SAFE_INTEGER` |
| `boolean` | `true`, `false` | |
| `undefined` | declared but not assigned | |
| `null` | explicitly "no value" — you assign this yourself | |
| `symbol` | `Symbol('desc')` | guaranteed-unique value, used as hidden object keys |

**`null` vs `undefined`:** `undefined` means "nothing was ever assigned." `null` means "someone deliberately assigned no value." Use `null` for intentional emptiness in your own code.

## 2. Type Coercion — Where Bugs Hide

```js
'5' + 3        // '53'   — string concatenation wins
'5' - 3        // 2      — minus forces numeric conversion
'5' == 5        // true    — loose equality coerces types
'5' === 5       // false   — strict equality does not
[] == false     // true   — coercion chains are genuinely unpredictable
Boolean('')     // false  — falsy: '', 0, -0, 0n, NaN, null, undefined, false
Boolean('0')    // true   — everything else, including the string '0', is truthy
```
**Rule:** always use `===`/`!==`. Never rely on `==`.

## 3. Numbers

```js
Number.isInteger(4)       // true
Number.parseInt('42px')    // 42 — parses leading digits, ignores rest
Number.parseFloat('3.14x') // 3.14
Number.isNaN(NaN)          // true — safer than global isNaN()
0.1 + 0.2                  // 0.30000000000000004 — floating point imprecision, use Number.EPSILON or round for comparisons
Number.MAX_SAFE_INTEGER    // 9007199254740991 — beyond this, use BigInt
```

## 4. Strings

Strings are immutable — every "modification" method returns a *new* string.
```js
const name = 'World';
`Hello, ${name}!`          // template literal — interpolation + multi-line
`Line 1
Line 2`
'abc'.at(-1)                // 'c' — negative indexing
```

## 5. Objects

```js
const user = {
  name: 'Ana',
  age: 30,
  'full-name': 'Ana Lopez',   // quotes needed for non-identifier keys
  greet() { return `Hi, ${this.name}`; },
};

user.name           // dot notation
user['full-name']    // bracket notation — required for dynamic or non-identifier keys
const key = 'age';
user[key]            // dynamic access

const { name, age, ...rest } = user;   // destructuring + rest
const merged = { ...user, age: 31 };    // spread — shallow copy with override
```
Objects are compared **by reference**, not value:
```js
{ a: 1 } === { a: 1 }   // false — different objects in memory
```

## 6. Arrays

Arrays are objects with numeric keys and a `length` property.
```js
const nums = [1, 2, 3];
const [first, , third] = nums;         // destructuring, can skip elements
const [head, ...tail] = nums;           // rest in destructuring
const combined = [...nums, 4, 5];       // spread
Array.isArray(nums)                     // true — typeof nums would just say 'object'
```

## 7. Advanced Types

### `Map` — key/value pairs, any type as key
```js
const scores = new Map();
scores.set('alice', 90);
scores.set(42, 'numeric key works too');
scores.get('alice');     // 90
scores.has('alice');     // true
scores.delete('alice');
scores.size;               // count

for (const [key, value] of scores) { }   // directly iterable, insertion order preserved
```
**Map vs plain object:**
| | `Map` | `Object` |
|---|---|---|
| Key types | any value | strings/symbols only |
| Iteration order | insertion order, guaranteed | mostly insertion order, but has quirks |
| Size | `.size` | manual `Object.keys().length` |
| Built-in iteration | yes | no (need `Object.entries()`) |
| Use when | keys are dynamic/unknown, or non-strings | fixed shape, JSON-serializable data |

### `Set` — unique values
```js
const ids = new Set([1, 2, 2, 3]);   // [1, 2, 3] — duplicates auto-removed
ids.add(4);
ids.has(2);      // true
[...ids]          // convert back to array
```
Common idiom: `[...new Set(array)]` to dedupe an array in one line.

### `WeakMap` / `WeakSet`
Like `Map`/`Set`, but keys must be objects and are held **weakly** — if nothing else references the key, it can be garbage collected. Used for attaching private/metadata to objects without causing memory leaks. Not iterable, no `.size`.

### `Date`
```js
const now = new Date();
new Date('2026-01-15');
new Date(2026, 0, 15);          // month is 0-indexed! January = 0
now.getFullYear();
now.getMonth();
now.toISOString();               // '2026-08-06T...' — standard format for storage/APIs
Date.now();                       // timestamp in ms, no Date object needed
```

### `RegExp`
```js
const pattern = /^\d{3}-\d{4}$/;
pattern.test('555-1234');          // true — boolean check
'555-1234'.match(/\d+/g);          // ['555', '1234'] — extraction
'hello world'.replace(/o/g, '0');   // 'hell0 w0rld'
```

### `JSON` — the format, not a JS-only type, but essential
```js
JSON.stringify({ a: 1, b: [1, 2] });     // '{"a":1,"b":[1,2]}'
JSON.stringify(data, null, 2);            // pretty-printed with 2-space indent
JSON.parse('{"a":1}');                    // { a: 1 }
```
**Gotchas:** `JSON.stringify` silently drops `undefined`, functions, and `Symbol` values; converts `Date` to an ISO string; throws on circular references (use `structuredClone` for those instead, see Sheet 3).

## 8. Type Checking Cheat Table

| Check | Use |
|---|---|
| `typeof x` | primitives (`'string'`, `'number'`, etc.) — but `typeof null === 'object'` |
| `Array.isArray(x)` | arrays specifically |
| `x instanceof ClassName` | class instances, including built-ins like `Map`, `Date` |
| `x === null` | explicit null check |
| `x == null` | the *one* accepted use of `==` — matches both `null` and `undefined` |

---
**Next:** Sheet 3 covers built-in functions and APIs — `console`, array/string/object methods, `fetch()`, and more, in depth.
