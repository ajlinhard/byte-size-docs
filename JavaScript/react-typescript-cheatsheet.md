# React + TypeScript Cheatsheet (Beginner → Intermediate)

A reference guide covering core concepts with step-by-step explanations and real use cases. Bookmark this and come back as you build.

---

## Part 1: TypeScript Fundamentals

### 1. Basic Types

**What it is:** TypeScript lets you label variables, function parameters, and return values with a type, so the compiler catches mismatches before your code ever runs.

**Step-by-step:**
1. Write your variable as usual: `let age = 25`
2. Add a colon and the type: `let age: number = 25`
3. TypeScript now errors if you try `age = "twenty-five"`

```typescript
let username: string = "sara";
let age: number = 28;
let isActive: boolean = true;
let tags: string[] = ["admin", "user"];
let coords: [number, number] = [40.7, -74.0]; // tuple: fixed length/order
```

**Use case:** Catching typos and wrong data types (e.g., passing a string where an ID number is expected) before deployment, instead of discovering it in production.

---

### 2. Interfaces and Type Aliases

**What it is:** Both describe the "shape" of an object — what properties it has and their types. `interface` and `type` are similar; `interface` is more common for objects, `type` is more flexible (unions, primitives).

**Step-by-step:**
1. Define the shape once: `interface User { name: string; age: number }`
2. Use it to type any variable or function parameter of that shape
3. TypeScript enforces that objects match the shape exactly (no missing required fields)

```typescript
interface User {
  name: string;
  age: number;
  email?: string; // optional (see below)
}

type Status = "loading" | "success" | "error"; // type alias for a union

const user: User = { name: "Sara", age: 28 };
```

**Use case:** Defining the shape of API response data (e.g., a `User` or `Product` object) so every component using that data gets autocomplete and error-checking.

---

### 3. Optional and Readonly Properties

**What it is:** A `?` marks a property as optional (may or may not be present). `readonly` prevents a property from being reassigned after creation.

**Step-by-step:**
1. Add `?` after the property name if it's not always required: `email?: string`
2. Add `readonly` before a property you never want mutated: `readonly id: string`
3. TypeScript will error if code tries to change a `readonly` field later

```typescript
interface Product {
  readonly id: string;
  name: string;
  discount?: number;
}
```

**Use case:** Modeling database records where `id` should never change after creation, but fields like `discount` might not apply to every product.

---

### 4. Union Types

**What it is:** A variable that can be one of several specific types, joined with `|`.

**Step-by-step:**
1. List the allowed types separated by `|`: `string | number`
2. TypeScript narrows the type based on checks you write (`typeof`, comparisons)
3. Inside an `if` block that checks the type, TypeScript "knows" which type you're working with

```typescript
function printId(id: string | number) {
  if (typeof id === "string") {
    console.log(id.toUpperCase()); // TS knows it's a string here
  } else {
    console.log(id.toFixed(2)); // TS knows it's a number here
  }
}
```

**Use case:** A component that accepts either a numeric ID or a string slug for routing, or a status field that can only ever be `"pending" | "shipped" | "delivered"`.

---

### 5. Generics

**What it is:** A way to write reusable functions/components that work with multiple types while still preserving type safety, using a placeholder like `<T>`.

**Step-by-step:**
1. Add `<T>` after the function name to declare a type placeholder
2. Use `T` anywhere you'd normally use a concrete type
3. When you call the function, TypeScript infers or you specify what `T` should be

```typescript
function getFirstItem<T>(list: T[]): T {
  return list[0];
}

const firstNum = getFirstItem<number>([1, 2, 3]);     // number
const firstName = getFirstItem<string>(["a", "b"]);   // string
```

**Use case:** A reusable `useFetch<T>()` custom hook that can fetch and type any API resource — `useFetch<User>()` or `useFetch<Product>()` — without rewriting the hook.

---

### 6. Type Assertions

**What it is:** Telling TypeScript "trust me, I know this is type X" when you know more about a value than the compiler can infer — used sparingly.

**Step-by-step:**
1. Use `as` after the value: `value as string`
2. Only use this when you're certain — it bypasses type checking, it doesn't convert the value
3. Common with DOM elements, where TypeScript can't know the exact element type

```typescript
const input = document.getElementById("email") as HTMLInputElement;
console.log(input.value); // TS now knows .value exists
```

**Use case:** Working with the DOM API or third-party libraries with loose typings, where you know the actual shape of the data better than TypeScript does.

---

## Part 2: React Fundamentals

### 7. Components and JSX

**What it is:** React UIs are built from components — functions that return JSX (HTML-like syntax written inside JavaScript/TypeScript).

**Step-by-step:**
1. Write a function that returns JSX
2. Capitalize the function name (React treats lowercase tags as HTML, capitalized as components)
3. Export it so other files can import and render it

```tsx
function Greeting() {
  return <h1>Hello, welcome back!</h1>;
}

export default Greeting;
```

**Use case:** Every visual piece of a React app — buttons, cards, forms, entire pages — is a component. This is the fundamental building block.

---

### 8. Props (with TypeScript)

**What it is:** Props are how you pass data into a component from its parent — like function arguments, but for components. TypeScript lets you define exactly what props a component expects.

**Step-by-step:**
1. Define an interface describing the props: `interface Props { name: string }`
2. Type the function parameter with that interface
3. Pass values when you render the component: `<Greeting name="Sara" />`

```tsx
interface GreetingProps {
  name: string;
  isAdmin?: boolean;
}

function Greeting({ name, isAdmin = false }: GreetingProps) {
  return <h1>Hello, {name}{isAdmin ? " (admin)" : ""}</h1>;
}

// usage:
<Greeting name="Sara" isAdmin={true} />
```

**Use case:** A reusable `<Button label="Save" onClick={handleSave} />` or `<UserCard user={userObject} />` — passing dynamic data into presentation components.

---

### 9. useState

**What it is:** A React Hook that lets a component hold and update its own local data ("state"). When state changes, React re-renders the component.

**Step-by-step:**
1. Import it: `import { useState } from "react"`
2. Call it inside the component: `const [count, setCount] = useState(0)`
3. Read `count` in your JSX, and call `setCount(newValue)` to update it and trigger a re-render

```tsx
import { useState } from "react";

function Counter() {
  const [count, setCount] = useState<number>(0);

  return (
    <button onClick={() => setCount(count + 1)}>
      Clicked {count} times
    </button>
  );
}
```

**Use case:** Form inputs, toggles (open/closed menus), counters, tracking whether a modal is visible — any data that changes over time within one component.

---

### 10. useEffect

**What it is:** A Hook for running "side effects" — code that reaches outside the component, like fetching data, subscribing to events, or setting timers — usually after render.

**Step-by-step:**
1. Import it: `import { useEffect } from "react"`
2. Call it with a function and a dependency array: `useEffect(() => { ... }, [dependency])`
3. The effect runs after render, and re-runs whenever a value in the dependency array changes
4. An empty array `[]` means "run once, on mount"

```tsx
import { useEffect, useState } from "react";

function UserProfile({ userId }: { userId: string }) {
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    fetch(`/api/users/${userId}`)
      .then((res) => res.json())
      .then((data) => setUser(data));
  }, [userId]); // re-fetch if userId changes

  return <div>{user ? user.name : "Loading..."}</div>;
}
```

**Use case:** Fetching data from an API when a component loads, syncing with `localStorage`, setting up a websocket connection, or starting/clearing a timer.

---

### 11. Event Handling (Typed)

**What it is:** Handling user interactions (clicks, typing, submitting) with correctly typed event objects so you get autocomplete on things like `event.target.value`.

**Step-by-step:**
1. Write a handler function
2. Type the event parameter using React's built-in event types (e.g., `React.ChangeEvent<HTMLInputElement>`)
3. Attach it to the JSX element: `onChange={handleChange}`

```tsx
function SearchBox() {
  const [query, setQuery] = useState<string>("");

  function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
    setQuery(e.target.value);
  }

  return <input value={query} onChange={handleChange} />;
}
```

**Use case:** Text inputs, form submissions, button clicks, dropdown selections — anything the user directly interacts with.

---

### 12. Conditional Rendering

**What it is:** Showing different JSX depending on a condition — React doesn't have special syntax for this, it's just JavaScript inside JSX.

**Step-by-step:**
1. Use a ternary (`condition ? a : b`) for either/or cases
2. Use `&&` to render something only if a condition is true
3. Use early `return`s inside the component for bigger branching logic

```tsx
function StatusBadge({ isOnline }: { isOnline: boolean }) {
  return (
    <span>
      {isOnline ? "🟢 Online" : "⚪ Offline"}
      {isOnline && <span> (active now)</span>}
    </span>
  );
}
```

**Use case:** Showing a loading spinner while data fetches, displaying an error message only if one exists, showing/hiding admin-only UI elements.

---

### 13. Rendering Lists and Keys

**What it is:** Turning an array of data into an array of JSX elements using `.map()`. Each element needs a unique `key` prop so React can track it efficiently.

**Step-by-step:**
1. Call `.map()` on your array
2. Return JSX for each item
3. Add a `key` prop using a stable, unique identifier (not the array index, if avoidable)

```tsx
interface Todo {
  id: string;
  text: string;
}

function TodoList({ todos }: { todos: Todo[] }) {
  return (
    <ul>
      {todos.map((todo) => (
        <li key={todo.id}>{todo.text}</li>
      ))}
    </ul>
  );
}
```

**Use case:** Rendering a list of products, comments, search results, or table rows from an array of API data.

---

### 14. useRef

**What it is:** A Hook that gives you a persistent, mutable reference that doesn't trigger a re-render when it changes — commonly used to directly access a DOM element.

**Step-by-step:**
1. Create the ref: `const inputRef = useRef<HTMLInputElement>(null)`
2. Attach it to a JSX element: `<input ref={inputRef} />`
3. Access the underlying DOM node via `.current`: `inputRef.current?.focus()`

```tsx
function SearchInput() {
  const inputRef = useRef<HTMLInputElement>(null);

  function focusInput() {
    inputRef.current?.focus();
  }

  return (
    <>
      <input ref={inputRef} />
      <button onClick={focusInput}>Focus the input</button>
    </>
  );
}
```

**Use case:** Auto-focusing an input on page load, measuring an element's size, integrating with non-React libraries (like a chart library) that need a raw DOM node.

---

### 15. Children Props

**What it is:** A special prop, `children`, that lets a component wrap and render whatever is placed between its opening and closing tags — key for building reusable layout/wrapper components.

**Step-by-step:**
1. Type the prop as `React.ReactNode` (covers text, elements, arrays of elements, etc.)
2. Render `{children}` wherever you want the nested content to appear
3. Use the component by placing content between its tags

```tsx
interface CardProps {
  title: string;
  children: React.ReactNode;
}

function Card({ title, children }: CardProps) {
  return (
    <div className="card">
      <h2>{title}</h2>
      <div className="card-body">{children}</div>
    </div>
  );
}

// usage:
<Card title="Profile">
  <p>Any content here becomes "children"</p>
</Card>
```

**Use case:** Layout wrappers, modals, cards, buttons with icons — any component meant to wrap arbitrary content passed in by whoever uses it.

---

## Part 3: Intermediate Concepts

### 16. Custom Hooks

**What it is:** A function starting with `use` that packages up reusable stateful logic (built from other Hooks), so multiple components can share behavior without duplicating code.

**Step-by-step:**
1. Create a function starting with `use` (required naming convention)
2. Use built-in Hooks (`useState`, `useEffect`, etc.) inside it
3. Return whatever the consuming component needs
4. Call it in any component just like a built-in Hook

```tsx
function useWindowWidth(): number {
  const [width, setWidth] = useState<number>(window.innerWidth);

  useEffect(() => {
    function handleResize() {
      setWidth(window.innerWidth);
    }
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  return width;
}

// usage in any component:
function Layout() {
  const width = useWindowWidth();
  return <div>{width < 768 ? "Mobile view" : "Desktop view"}</div>;
}
```

**Use case:** Sharing logic like data fetching (`useFetch`), form handling (`useForm`), authentication state (`useAuth`), or responsive breakpoints across many components.

---

### 17. useContext

**What it is:** A Hook for sharing data across many components without manually passing props down through every level ("prop drilling") — pairs with `createContext`.

**Step-by-step:**
1. Create a context: `const ThemeContext = createContext<Theme | undefined>(undefined)`
2. Wrap the part of your app that needs the data in a `<ThemeContext.Provider value={theme}>`
3. Any nested component calls `useContext(ThemeContext)` to read the value directly

```tsx
type Theme = "light" | "dark";
const ThemeContext = createContext<Theme>("light");

function App() {
  return (
    <ThemeContext.Provider value="dark">
      <Toolbar />
    </ThemeContext.Provider>
  );
}

function Toolbar() {
  const theme = useContext(ThemeContext); // no prop drilling needed
  return <div className={theme}>Toolbar</div>;
}
```

**Use case:** App-wide theme (light/dark mode), current logged-in user, language/locale settings — data many components need without passing it through every intermediate layer.

---

### 18. useMemo and useCallback

**What it is:** Performance Hooks that "memoize" (cache) a computed value (`useMemo`) or a function (`useCallback`) so it isn't recreated on every render unless its dependencies change.

**Step-by-step:**
1. Wrap an expensive calculation in `useMemo(() => computeIt(), [dependencies])`
2. Wrap a function passed to child components in `useCallback((...) => { ... }, [dependencies])`
3. React skips recomputing/recreating unless a listed dependency changes

```tsx
function ProductList({ products, query }: { products: Product[]; query: string }) {
  const filtered = useMemo(
    () => products.filter((p) => p.name.includes(query)),
    [products, query]
  );

  const handleSelect = useCallback((id: string) => {
    console.log("Selected:", id);
  }, []);

  return (
    <ul>
      {filtered.map((p) => (
        <li key={p.id} onClick={() => handleSelect(p.id)}>{p.name}</li>
      ))}
    </ul>
  );
}
```

**Use case:** Avoiding expensive re-filtering/re-sorting of large lists on every render, or preventing unnecessary re-renders of child components that receive functions as props. Don't reach for these by default — only add them once you notice an actual performance issue.

---

## Quick Reference Table

| Concept | Purpose | One-line trigger |
|---|---|---|
| `interface` / `type` | Define object shapes | "This data has fields X, Y, Z" |
| `useState` | Local component data | "This value changes over time" |
| `useEffect` | Side effects | "Do this after render / when X changes" |
| Props | Parent → child data | "Pass this data into a component" |
| `children` | Wrapper components | "Render whatever's nested inside" |
| `useRef` | Direct DOM access | "I need the actual DOM node" |
| `useContext` | Avoid prop drilling | "Many components need this value" |
| Custom Hooks | Reusable logic | "Multiple components need this behavior" |
| `useMemo`/`useCallback` | Performance | "This is genuinely slow — measured, not guessed" |

---

*Tip: Start with components, props, and `useState`/`useEffect` — those four cover the majority of real-world React code. Add the rest as you run into the problems they solve.*
