# CQRS: Command Query Responsibility Segregation

## The Core Idea

CQRS is an architectural pattern that splits a system's operations into two distinct sides:

- **Commands** — operations that *change* state (write, update, delete). They return nothing (or just an acknowledgment).
- **Queries** — operations that *read* state. They return data but change nothing.

The insight is simple but powerful: **the model you use to mutate data is rarely the ideal model for reading it.** Forcing both through the same interface creates friction at every layer — the database, the API, the service logic, and the UI.

---

## The Basics

In a traditional CRUD system, a single model handles everything:

```
User → Repository → Database
         ↑
    (reads & writes)
```

In CQRS, you split this:

```
User
 ├── Command → CommandHandler → Write Model → Write DB
 └── Query  → QueryHandler  → Read Model  → Read DB
```

**Commands** are intention-expressing objects:
```typescript
// A command expresses intent, carries only what's needed to act
class PlaceOrderCommand {
  customerId: string;
  items: OrderItem[];
  shippingAddress: Address;
}
```

**Queries** are specific data requests:
```typescript
// A query expresses a precise data need
class GetOrderSummaryQuery {
  customerId: string;
  dateRange: DateRange;
}
```

Each is handled by a dedicated handler with a single responsibility. This alone — even without separate databases — cleans up a surprising amount of complexity.

---

## More Complex Features

### 1. Separate Read and Write Stores

Once commands and queries are split in code, you can split the *storage* too. The write side uses a normalized, integrity-focused model (e.g., relational DB). The read side uses a denormalized, query-optimized model (e.g., document store, Redis, Elasticsearch, or even flat materialized views).

```
Write Side                    Read Side
──────────────────────        ─────────────────────────────
PostgreSQL (normalized)  →→→  MongoDB / Redis / Elasticsearch
  orders table                  order_summary_view (pre-joined,
  order_items table             pre-aggregated, ready to serve)
  products table
```

The read store is rebuilt/updated by listening to events from the write side.

---

### 2. Event Sourcing (Natural Companion)

CQRS pairs extremely well with **Event Sourcing**, where instead of storing current state, you store a *log of events* that produced that state:

```
Events stored:
  OrderPlaced      { orderId, items, customerId }
  PaymentReceived  { orderId, amount }
  OrderShipped     { orderId, trackingNumber }

Current state = replay of all events
```

This gives you a complete audit trail, the ability to time-travel to any past state, and the ability to build new read models retroactively by replaying events.

---

### 3. Eventual Consistency

When write and read stores are separate, they aren't always in sync. A command succeeds, an event is published, and the read model *eventually* catches up — usually in milliseconds, but not instantly. This is a deliberate trade-off: you gain massive read scalability at the cost of immediate consistency.

---

### 4. Scalability Asymmetry

Most systems read far more than they write. CQRS lets you scale them independently:
- Scale read replicas horizontally without touching the write path
- Add caching layers only on the query side
- Use CDN-friendly, pre-rendered read projections

---

## Use Cases

| Scenario | Why CQRS Helps |
|---|---|
| High read/write ratio | Scale read and write sides independently |
| Complex domain logic | Commands stay clean; no read concerns bleeding in |
| Audit/compliance requirements | Event sourcing pairs naturally |
| Reporting & analytics | Read models built specifically for the query shape |
| Collaborative/real-time apps | Events fan out to multiple read projections |
| Microservices | Services communicate via commands/events, not shared DB |

It's worth noting CQRS is **overkill for simple CRUD apps**. The added complexity only pays off when your read and write shapes genuinely diverge.

---

## CQRS and Frontend Data: The Aggregation Problem

This is where CQRS really shines for product teams. Frontend UIs almost never want *raw normalized data* — they want **pre-shaped aggregations** that map to what the user actually sees.

### The Classic Problem

Imagine a dashboard that shows:

```
┌─────────────────────────────────────────────┐
│ Customer: Acme Corp                         │
│ Total Orders: 142   |  Revenue: $84,320     │
│ Last Order: 2 days ago                      │
│ Top Product: Widget Pro (38 orders)         │
│ Open Support Tickets: 3                     │
└─────────────────────────────────────────────┘
```

In a traditional system, the frontend (or BFF) must:
1. Fetch customer record
2. Fetch all orders, aggregate count and revenue
3. Find the most recent order
4. Group order items, find the top product
5. Fetch support tickets, filter for open ones

This means multiple round trips, joins in application code, and N+1 query problems. Or you write a massive SQL query that's brittle and hard to maintain. Either way, the read concern leaks into your domain model.

---

### The CQRS Solution: Purpose-Built Read Models

With CQRS, you create a **read model (projection)** that is built *specifically* for this view:

```typescript
// This is maintained as a dedicated read model — updated via events
interface CustomerDashboardProjection {
  customerId: string;
  name: string;
  totalOrders: number;
  totalRevenue: Money;
  lastOrderDate: Date;
  topProduct: { name: string; orderCount: number };
  openSupportTickets: number;
  // ...whatever the UI needs
}
```

This projection is kept up to date by reacting to events from multiple domains:

```
OrderPlaced      → update totalOrders, totalRevenue, topProduct
OrderCompleted   → update lastOrderDate
TicketOpened     → increment openSupportTickets
TicketClosed     → decrement openSupportTickets
```

The frontend query becomes trivially simple:

```typescript
// One query, one document, no joins, no aggregation at request time
GET /queries/customer-dashboard?customerId=acme-corp
→ Returns the CustomerDashboardProjection directly
```

---

### Multiple Projections for Multiple Views

The same underlying domain events can power *different* projections for different UI contexts:

```
Domain Events
     │
     ├──→ CustomerDashboardProjection   (account overview page)
     ├──→ CustomerListProjection        (admin table with sortable columns)
     ├──→ CustomerRevenueReportProjection (finance export)
     └──→ CustomerActivityFeedProjection  (recent actions timeline)
```

Each projection is shaped *exactly* for its consumer. The finance team gets pre-formatted numbers. The admin table gets pre-sorted, pre-paginated records. The UI never has to reshape data.

---

### Frontend-Specific Benefits

**Pagination & filtering are pre-computed.** Because read models are built for the query, you can store data in whatever order or index makes sense for the UI — no expensive `ORDER BY` + `OFFSET` at request time.

**Real-time updates become straightforward.** Since the read model is event-driven, you can push updates to the frontend over WebSockets or SSE the moment a relevant event fires — not on a polling interval.

**BFF (Backend for Frontend) pattern complements this perfectly.** A BFF layer issues commands and queries on behalf of the UI, but with CQRS, the query responses are already shaped for the frontend — the BFF becomes thin routing logic rather than a data transformation layer.

**Offline / optimistic UI.** On the write side, commands can be queued and replayed. The frontend can apply optimistic updates immediately, knowing the eventual consistent read model will catch up.

---

### Summary

```
Traditional           CQRS
──────────────────    ────────────────────────────────────────
Write = Read model    Write model ≠ Read model
Joins at query time   Joins at write time (pre-aggregated)
One DB for all        Polyglot persistence per use case
Scaling is coupled    Read/write scale independently
UI reshapes data      Data pre-shaped for the UI consumer
```

CQRS, at its heart, is about acknowledging that **asking a question** and **giving an order** are fundamentally different acts — and that your architecture should reflect that difference rather than paper over it.
