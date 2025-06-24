# APIs (Application Programming Interface)
APIs (Application Programming Interfaces) commonly are first thought of as web-base APIs.
An API (Application Programming Interface) is essentially a set of rules and protocols that defines how different software components can communicate with each other. Think of it as a contract that specifies what requests you can make, how to make them, what data formats to use, and what responses you'll get back.

At its core, an API acts as an intermediary layer that allows one piece of software to access the functionality or data of another without needing to understand the internal workings. It's like a waiter in a restaurant - you don't need to know how the kitchen operates, you just need to know how to order from the menu (the API) and you'll get your food back.

The terminology can vary based on context:
- "Interface" is the general term for any boundary where different components meet and interact
- "API" usually refers to a more formalized set of methods/functions meant for programmers
- Some fields use terms like "protocol," "contract," or "integration point"

So no, APIs don't have to be websites - they're fundamentally about defining how different software components can communicate with each other, regardless of where those components are located.

## Types of APIs

**Web APIs (REST, GraphQL, SOAP):** These operate over HTTP/HTTPS and are the most common type you'll encounter. REST APIs use standard HTTP methods (GET, POST, PUT, DELETE) and are widely used for web services. GraphQL allows clients to request specific data structures, while SOAP uses XML messaging.

**Library/Framework APIs:** These are programming interfaces within software libraries or frameworks. For example, when you use functions from a Python library like `requests.get()`, you're using the library's API.

**Operating System APIs:** These allow applications to interact with the underlying OS. Windows API, POSIX APIs on Unix-like systems, or mobile APIs like iOS and Android APIs fall into this category.

**Database APIs:** These provide standardized ways to interact with databases, like SQL APIs or specific database driver APIs.

**Hardware APIs:** These allow software to communicate with hardware components, such as graphics APIs (OpenGL, DirectX) or device driver APIs.

**Internal/Module APIs**: Interfaces between different components or modules within the same application. These define how different parts of your program communicate.

**IPC (Inter-Process Communication)**: Mechanisms for different processes to communicate, including pipes, sockets, shared memory, message queues, etc.

**RPC (Remote Procedure Call)**: Allows a program to execute code on another system, often used in distributed systems.

**Plugin/Extension APIs**: Interfaces that allow third-party code to extend an application's functionality.

## Server-Client Architecture

Not all APIs follow a traditional server-client architecture. While web APIs typically do (your app is the client, the API endpoint is the server), many other types don't:

- Library APIs operate within the same process as your application
- Hardware APIs often involve direct system calls rather than network communication
- Some APIs use peer-to-peer architectures
- Event-driven or callback-based APIs might not have a clear client-server relationship

The server-client model is dominant in web-based APIs because of the distributed nature of web applications, but it's just one architectural pattern among many that APIs can use.

---
# REST API (Representational State Transfer)
A REST API (Representational State Transfer) is a type of web API that follows a specific architectural style for designing networked applications. It's built around the idea of treating data and functionality as "resources" that can be accessed and manipulated using standard HTTP methods.

## Core Principles

**Stateless:** Each request from client to server must contain all the information needed to process that request. The server doesn't store any client context between requests.

**Resource-based:** Everything is treated as a resource, identified by URLs. For example, `/users/123` represents user with ID 123, `/products` represents a collection of products.

**HTTP Methods:** REST uses standard HTTP verbs to perform operations:
- GET: Retrieve data
- POST: Create new resources
- PUT: Update/replace existing resources
- DELETE: Remove resources
- PATCH: Partially update resources

**Uniform Interface:** Resources are accessed through a consistent interface, typically using URLs and HTTP methods.

## How It Works

Instead of calling remote functions (like older RPC-style APIs), you interact with resources. For example:

- `GET /api/users` - Get all users
- `GET /api/users/123` - Get user with ID 123
- `POST /api/users` - Create a new user
- `PUT /api/users/123` - Update user 123
- `DELETE /api/users/123` - Delete user 123

## Data Format

REST APIs commonly use JSON for data exchange, though they can technically use any format. A typical response might look like:

```json
{
  "id": 123,
  "name": "John Doe",
  "email": "john@example.com"
}
```

## Why REST is Popular

REST became dominant because it leverages existing web infrastructure (HTTP), is relatively simple to understand and implement, works well with web browsers and mobile apps, and provides good scalability due to its stateless nature. It's intuitive - if you understand how websites work, REST APIs follow similar patterns but return data instead of HTML pages.

The simplicity and alignment with web standards made REST the go-to choice for most web APIs, though newer alternatives like GraphQL are gaining traction for specific use cases.

---
# GraphQL
GraphQL is a query language and runtime for APIs that allows clients to request exactly the data they need, nothing more, nothing less. Unlike REST APIs where you get fixed data structures from predefined endpoints, GraphQL gives clients the power to specify precisely what data they want in a single request.

## How GraphQL Works

GraphQL APIs typically expose a single endpoint (usually `/graphql`) and use POST requests. Instead of multiple REST endpoints, you send queries that describe your data requirements:

```graphql
query {
  user(id: "123") {
    name
    email
    posts {
      title
      createdAt
    }
  }
}
```

This query fetches a user's name, email, and their posts' titles and creation dates - all in one request. The response matches the query structure:

```json
{
  "data": {
    "user": {
      "name": "John Doe",
      "email": "john@example.com",
      "posts": [
        {
          "title": "My First Post",
          "createdAt": "2024-01-15"
        }
      ]
    }
  }
}
```

## Key Features

**Single Request, Multiple Resources:** Instead of making separate REST calls to `/users/123`, `/users/123/posts`, etc., one GraphQL query can fetch related data across multiple resources.

**No Over-fetching or Under-fetching:** You get exactly what you ask for. If you only need a user's name, you only get the name - not their entire profile.

**Strong Type System:** GraphQL APIs are built around a schema that defines available data types, fields, and operations. This provides excellent tooling and documentation.

**Three Operation Types:**
- **Queries:** Read data (like GET in REST)
- **Mutations:** Modify data (like POST/PUT/DELETE in REST)
- **Subscriptions:** Real-time updates via WebSockets

## Advantages Over REST

GraphQL shines in scenarios where you need flexible data fetching, especially for mobile apps with limited bandwidth or complex UIs that need data from multiple sources. It reduces the number of network requests and gives frontend developers more control over data fetching without requiring backend changes.

The self-documenting nature of GraphQL schemas and excellent developer tools also make it attractive for teams building complex applications.

## Trade-offs

While powerful, GraphQL has more complexity in implementation, caching can be trickier than with REST, and it may be overkill for simple CRUD applications. It's particularly valuable when you have diverse clients (web, mobile, different apps) that need different data subsets from the same backend.

