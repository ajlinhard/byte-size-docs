# JSON-RPC Explained

## First, the distinction: JSON vs JSON-RPC

These are two different kinds of things, which is the key to understanding your question.

**JSON** (JavaScript Object Notation) is a *data format*. It's just a way of representing structured data as text:

```json
{
  "name": "Alice",
  "age": 30,
  "hobbies": ["reading", "coding"]
}
```

JSON doesn't *do* anything. It's a syntax for describing data—like a file format. It has no notion of actions, requests, or communication. It's the vocabulary, not the conversation.

**JSON-RPC** is a *protocol* that happens to use JSON as its data format. RPC stands for **Remote Procedure Call**, and the whole point is to let one program call a function (a "procedure") that lives on another program or machine, as if it were calling a local function.

So the relationship is: JSON-RPC is a set of rules for structuring messages, and those messages are written in JSON. JSON is the raw material; JSON-RPC is a specific thing built out of that material for a specific purpose.

---

## What "Remote Procedure Call" actually means

Normally when you write code, calling a function is simple:

```python
result = add(2, 3)  # runs on your machine, returns 5
```

But what if the `add` function lives on a *different* computer (a server somewhere)? You can't just call it directly. You need to:

1. Package up "I want to call `add` with arguments 2 and 3" into a message
2. Send that message over the network
3. Have the server unpack it, run the real function, and package up the result
4. Send the result back to you

RPC is the general idea of making that whole round-trip *feel* like a normal function call. JSON-RPC is one specific, standardized way of doing it where the messages are formatted in JSON.

---

## What JSON-RPC adds on top of plain JSON

Plain JSON just gives you `{...}`. JSON-RPC says: "if you want to represent a function call, here's *exactly* what fields your JSON object must contain."

A JSON-RPC **request** looks like this:

```json
{
  "jsonrpc": "2.0",
  "method": "add",
  "params": [2, 3],
  "id": 1
}
```

Every field has a defined meaning:

- `jsonrpc` — the protocol version, so both sides agree on the rules
- `method` — the name of the function/procedure you want to call
- `params` — the arguments to pass to it
- `id` — a unique marker so you can match responses back to the requests that caused them

And the **response** comes back in a standardized shape too:

```json
{
  "jsonrpc": "2.0",
  "result": 5,
  "id": 1
}
```

Or, if something went wrong, a standardized **error** shape:

```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": -32601,
    "message": "Method not found"
  },
  "id": 1
}
```

Notice the `id` in the response matches the `id` in the request—that's how a client that fired off many calls at once knows which answer goes with which question. It also defines things plain JSON never could: standardized error codes, the ability to send **batches** (an array of requests at once), and **notifications** (requests with no `id`, meaning "do this but don't bother replying").

None of this structure exists in JSON itself. JSON would happily let you write `{"method": "add"}` or `{"do": "add", "with": [2,3]}` or anything else. JSON-RPC removes that ambiguity by mandating one agreed-upon shape.

---

## Why it was developed

The core problem: **JSON tells you how to write data, but not how two programs should talk to each other.**

If every developer invented their own JSON structure for "call this function," then no two systems could interoperate without custom glue code. One team's API might expect `{"function": ...}`, another's `{"cmd": ...}`, another's `{"action": ...}`. Chaos.

JSON-RPC (the 2.0 spec, which is the common one, was finalized around 2010) was developed to solve several things at once:

**Standardization.** Everyone agrees on the same request/response envelope, so a client library written once can talk to any JSON-RPC server. You don't reinvent the wheel for each API.

**Simplicity and lightness.** Before JSON-RPC, the dominant RPC standard was **XML-RPC** and its heavier cousin **SOAP**, which used verbose XML. Those were bulky and painful to work with. As JSON became the web's favorite data format (lighter, easier to read, native to JavaScript), a JSON-based RPC protocol was a natural, leaner replacement.

**Transport independence.** JSON-RPC deliberately doesn't care *how* the message gets from A to B. You can send it over HTTP, over raw TCP sockets, over WebSockets, over standard input/output between two local processes—the protocol only defines the *message shape*, not the delivery mechanism. That flexibility made it usable in many different contexts.

**Predictable error handling.** By defining standard error codes and a fixed error format, both sides always know how to interpret a failure, rather than each server inventing its own way of saying "that didn't work."

---

## Where you actually see it

JSON-RPC is widely used in practice. Blockchain nodes (Bitcoin, Ethereum) expose JSON-RPC APIs for querying and sending transactions. The Language Server Protocol (LSP)—which powers code intelligence like autocomplete and error-checking in editors such as VS Code—is built on JSON-RPC. More recently, the Model Context Protocol (MCP), which lets AI assistants connect to external tools and data, also uses JSON-RPC as its message format.

---

## The one-line summary

JSON is *how you write data down*. JSON-RPC is *a specific set of rules, written in JSON, for one program to ask another program to run a function and send back the result*—created to give the world a lightweight, standardized, transport-agnostic way to do remote function calls without everyone inventing their own incompatible conventions.

If it helps, think of it like this: JSON is the alphabet and grammar of a language. JSON-RPC is a *standardized business letter format* written in that language—with an agreed-upon place for the sender, the request, and the reply—so any two offices can correspond without confusion.
