# JS Cheatsheet 3 — Built-in Functions & APIs

## 1. `console` — More Than `.log()`

```js
console.log('basic output', someVar);
console.warn('shows as a warning');
console.error('shows as an error, includes stack trace');
console.info('informational');
console.debug('debug-level, often filtered out by default');

console.table([{ name: 'Ana', age: 30 }, { name: 'Ravi', age: 25 }]); // renders a data grid
console.group('Request details');    // indents subsequent logs
console.log('url:', url);
console.groupEnd();

console.time('fetchUsers');
await fetchUsers();
console.timeEnd('fetchUsers');       // prints elapsed time

console.count('renderCalled');        // auto-incrementing counter per label
console.assert(user.age > 0, 'Age must be positive'); // logs only if condition is false
console.trace('how did we get here'); // prints a stack trace
```
**String formatting:** `console.log('%s is %d years old', name, age)` — `%s` string, `%d`/`%i` integer, `%f` float, `%o`/`%O` object, `%c` CSS styling (browser only).

## 2. Array Methods — The Ones You'll Use Constantly

```js
const nums = [1, 2, 3, 4, 5];

nums.map(n => n * 2);                 // [2,4,6,8,10] — transform each element, new array
nums.filter(n => n % 2 === 0);         // [2,4] — keep matching elements
nums.reduce((acc, n) => acc + n, 0);    // 15 — fold to a single value; 0 is the initial accumulator
nums.forEach(n => console.log(n));      // no return value — just side effects
nums.find(n => n > 3);                  // 4 — first match, or undefined
nums.findIndex(n => n > 3);             // 3 — index of first match, or -1
nums.some(n => n > 4);                  // true — at least one matches
nums.every(n => n > 0);                 // true — all match
nums.includes(3);                       // true
nums.sort((a, b) => a - b);              // MUTATES the array; default sort is lexicographic (string) order — always pass a comparator for numbers
nums.reverse();                          // MUTATES

nums.slice(1, 3);                        // [2,3] — non-mutating, extracts a copy
nums.splice(1, 2, 'x', 'y');             // MUTATES — removes/inserts in place, returns removed items

nums.flat();                             // flattens one level of nested arrays
nums.flatMap(n => [n, n * 2]);           // map then flatten one level
nums.join('-');                          // '1-2-3-4-5'
nums.concat([6, 7]);                     // non-mutating merge

Array.from({ length: 5 }, (_, i) => i);  // [0,1,2,3,4] — build array from array-like/iterable
Array.of(7);                             // [7] — vs Array(7) which makes an empty array of length 7
```
**`reduce` deep dive** (the one people find hardest):
```js
const cart = [{ price: 10 }, { price: 20 }];
const total = cart.reduce((sum, item) => sum + item.price, 0);
// sum starts at 0, each call returns the new accumulator for the next iteration
```
**Mutating vs non-mutating — memorize this list.** Mutating: `push`, `pop`, `shift`, `unshift`, `splice`, `sort`, `reverse`, `fill`. Everything else returns a new array/value.

## 3. String Methods

```js
const s = '  Hello World  ';
s.trim();                     // 'Hello World' — also trimStart()/trimEnd()
s.toLowerCase();               // '  hello world  '
s.includes('World');            // true
s.startsWith('  He');           // true
s.split(' ');                    // ['', '', 'Hello', 'World', '', '']
s.replace('World', 'JS');        // replaces first match
s.replaceAll('l', 'L');          // replaces all matches
s.slice(2, 7);                   // 'Hello' — supports negative indices
s.padStart(20, '*');             // pads to length 20
s.repeat(3);
[..."hello"];                     // ['h','e','l','l','o'] — strings are iterable
```

## 4. Object Methods

```js
const obj = { a: 1, b: 2 };

Object.keys(obj);           // ['a', 'b']
Object.values(obj);          // [1, 2]
Object.entries(obj);         // [['a',1], ['b',2]] — pairs with for...of
for (const [key, value] of Object.entries(obj)) { }

Object.assign({}, obj, { c: 3 });   // shallow merge into a new object (prefer spread {...obj, c:3} in modern code)
Object.freeze(obj);                  // prevents any modification (shallow)
Object.isFrozen(obj);
Object.fromEntries([['a', 1], ['b', 2]]);   // {a:1, b:2} — inverse of entries()
Object.create(protoObj);              // new object with protoObj as its prototype
```

## 5. `JSON`

```js
JSON.stringify(value);
JSON.stringify(value, null, 2);                    // pretty print
JSON.stringify(value, ['a', 'b']);                  // replacer array — only include these keys
JSON.parse(text);
JSON.parse(text, (key, value) =>                     // reviver — transform values while parsing
  key === 'date' ? new Date(value) : value
);
```

## 6. `Math`

```js
Math.random();                 // [0, 1)
Math.floor(Math.random() * 10); // random int 0-9
Math.round(4.5);
Math.ceil(4.1);
Math.min(1, 2, 3); Math.max(1, 2, 3);
Math.min(...arr); Math.max(...arr);   // spread for arrays
Math.abs(-5);
Math.pow(2, 10); 2 ** 10;              // equivalent
Math.sqrt(16);
```

## 7. Timers & the Event Loop

```js
const id = setTimeout(() => console.log('later'), 1000);
clearTimeout(id);

const intervalId = setInterval(() => console.log('tick'), 1000);
clearInterval(intervalId);

queueMicrotask(() => console.log('runs before setTimeout, after sync code'));
```
**Ordering rule:** synchronous code → microtasks (Promises, `queueMicrotask`) → macrotasks (`setTimeout`, `setInterval`). This is why `Promise.resolve().then(...)` fires before a `setTimeout(..., 0)`.

## 8. Promises & `async`/`await`

A `Promise` represents a value that isn't ready yet.
```js
const promise = new Promise((resolve, reject) => {
  doSomethingAsync((err, result) => {
    if (err) reject(err);
    else resolve(result);
  });
});

promise
  .then(result => console.log(result))
  .catch(err => console.error(err))
  .finally(() => console.log('always runs'));
```
`async`/`await` is syntax sugar over the same mechanism — cleaner to read:
```js
async function loadUser(id) {
  try {
    const user = await getUser(id);   // pauses here until the promise settles
    return user;
  } catch (err) {
    console.error('failed:', err);
    throw err;                          // re-throw if the caller should also handle it
  }
}
```
**Combinators:**
```js
await Promise.all([p1, p2, p3]);           // all must succeed; rejects fast on first failure
await Promise.allSettled([p1, p2, p3]);     // waits for all, gives {status, value|reason} per item
await Promise.race([p1, p2]);               // resolves/rejects as soon as the first settles
await Promise.any([p1, p2]);                // resolves as soon as the first succeeds
```

## 9. `fetch()` — Deep Dive

`fetch()` is the standard way to make HTTP requests in browsers and modern Node (18+).

**Basic GET:**
```js
async function getUsers() {
  const response = await fetch('https://api.example.com/users');
  if (!response.ok) {                          // fetch does NOT reject on 404/500 — you must check this yourself
    throw new Error(`HTTP ${response.status}`);
  }
  const data = await response.json();           // parses the body as JSON — also returns a promise
  return data;
}
```

**Response object essentials:**
| Property/method | What it gives you |
|---|---|
| `response.ok` | `true` for status 200-299 |
| `response.status` | numeric status code |
| `response.statusText` | e.g. `'Not Found'` |
| `response.headers` | a `Headers` object — `response.headers.get('Content-Type')` |
| `response.json()` | parses body as JSON (async) |
| `response.text()` | body as plain text (async) |
| `response.blob()` | body as binary blob, for files/images (async) |

**POST with a JSON body:**
```js
const response = await fetch('https://api.example.com/users', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ name: 'Ana', age: 30 }),
});
```

**Other options:** `method` (GET/POST/PUT/PATCH/DELETE), `headers`, `body`, `credentials` (`'include'` to send cookies cross-origin), `mode` (`'cors'`/`'no-cors'`/`'same-origin'`), `signal` (for cancellation, below).

**Cancelling a request with `AbortController`:**
```js
const controller = new AbortController();
const timeoutId = setTimeout(() => controller.abort(), 5000);   // 5s timeout

try {
  const response = await fetch(url, { signal: controller.signal });
  clearTimeout(timeoutId);
} catch (err) {
  if (err.name === 'AbortError') console.log('request timed out');
}
```

**A reusable fetch wrapper (common real-world pattern):**
```js
async function apiRequest(path, options = {}) {
  const response = await fetch(`https://api.example.com${path}`, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  });
  if (!response.ok) {
    const body = await response.text().catch(() => '');
    throw new Error(`API error ${response.status}: ${body}`);
  }
  return response.status === 204 ? null : response.json();   // handle "no content" responses
}
```

**Common `fetch()` mistakes to avoid:**
- Forgetting to check `response.ok` (a 404 still "succeeds" as a fetch, it just returns a Response with bad status).
- Forgetting `await` on `.json()`/`.text()` — they return promises too, not the parsed value directly.
- Not setting `Content-Type: application/json` on POST/PUT — many servers won't parse the body correctly without it.

## 10. Other Handy Globals

```js
structuredClone(obj);                 // true deep clone, handles Dates/Maps/circular refs (unlike JSON.stringify/parse)
crypto.randomUUID();                   // generates a UUID string
encodeURIComponent('a b&c');            // 'a%20b%26c' — safely encode for URLs
decodeURIComponent('a%20b%26c');
new URL('https://x.com/path?q=1').searchParams.get('q');   // parse URLs and query params properly
```

---
**Next:** Sheet 4 covers classes in depth — full syntax, inheritance, common design patterns, and how to structure a real project.
