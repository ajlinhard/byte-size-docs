# Avoiding AWS Lambda Cold Start Times

Cold starts happen when Lambda needs to initialize a new execution environment. Here are the most effective strategies:

## 1. Provisioned Concurrency (Most Effective)
```yaml
# serverless.yml
functions:
  myFunction:
    handler: handler.main
    provisionedConcurrency: 5  # Always-warm instances
```
- Keeps N instances **always initialized** — zero cold start for those slots
- You pay for provisioned concurrency even when idle
- Best for latency-sensitive production workloads

---

## 2. Scheduled Warmup Pings
```javascript
// Ping your Lambda every 5 minutes via EventBridge
export const warmer = async (event) => {
  if (event.source === 'warmup') {
    console.log('Warm-up ping — skipping logic');
    return { statusCode: 200, body: 'warmed' };
  }
  // ... real logic
};
```
- Use **EventBridge** (CloudWatch Events) to trigger the function periodically
- Free tier-friendly but doesn't guarantee zero cold starts under burst traffic

---

## 3. Reduce Cold Start Duration
Even when a cold start happens, make it faster:

### Minimize package size
```bash
# Use esbuild/webpack to tree-shake dependencies
esbuild handler.ts --bundle --platform=node --target=node20 --outfile=dist/handler.js
```

### Lazy-load heavy dependencies
```javascript
// ❌ Bad — loaded at cold start
import { DocumentClient } from '@aws-sdk/client-dynamodb';
const client = new DocumentClient();

// ✅ Good — loaded on first real invocation
let client;
const getClient = () => {
  if (!client) client = new DocumentClient();
  return client;
};
```

### Move DB connections outside the handler
```javascript
// Initialized once per container lifecycle
const db = new Pool({ connectionString: process.env.DB_URL });

export const handler = async (event) => {
  // db is already connected on warm invocations
  const result = await db.query('SELECT ...');
};
```

---

## 4. Choose the Right Runtime
| Runtime | Cold Start Speed |
|---|---|
| **Node.js / Python** | ✅ Fastest |
| **Java / .NET** | ❌ Slowest (JVM/CLR init) |
| **Go / Rust** | ✅ Very fast |

For Java, use **SnapStart** (Lambda-specific feature):
```yaml
functions:
  javaFn:
    handler: com.example.Handler
    snapStart: true  # Snapshots after init phase
```

---

## 5. Use Lambda Response Streaming
Not a cold start fix, but **perceived latency** drops because the client starts receiving data before the full response is ready:
```javascript
export const handler = awslambda.streamifyResponse(async (event, responseStream) => {
  responseStream.write('First chunk...');
  // ... stream more data
  responseStream.end();
});
```

---

## 6. Architecture-Level Solutions

- **Use Lambda@Edge or CloudFront Functions** for ultra-low latency at the edge (much lighter runtimes)
- **Switch to containers on ECS/Fargate** if cold starts are consistently problematic
- **Use `arm64` (Graviton2)** — slightly faster init + cheaper:
```yaml
architecture: arm64
```

---

## Quick Decision Guide

| Situation | Best Solution |
|---|---|
| Critical prod latency | **Provisioned Concurrency** |
| Low traffic / cost-sensitive | **Scheduled warmup pings** |
| Java runtime | **SnapStart** |
| Burst traffic spikes | Provisioned Concurrency + Auto Scaling |
| Consistently high traffic | Consider **ECS/Fargate** instead |

The **gold standard** is Provisioned Concurrency + small bundle size + connections initialized outside the handler.

---
# Lambda Latency Breakdown

---
# Latency Breakdown: Frontend → Warm Lambda API

## Full Request Stack (Typical Numbers)

```
Frontend (Browser)
     │
     │  DNS Lookup          ~10–100ms  (cached: ~1ms)
     ▼
CDN / CloudFront           ~1–5ms     (if used)
     │
     │  TLS Handshake       ~10–50ms   (resumed: ~1ms)
     ▼
API Gateway / ALB          ~5–15ms    (API GW adds more than ALB)
     │
     ▼
Warm Lambda Execution      ~1–50ms    (your code logic)
     │
     ▼
DB / External Service      ~1–20ms    (if in same VPC/region)
     │
     ▼
Response back to browser
```

---

## Realistic End-to-End Numbers (Same Region)

| Setup | Latency (P50) | Latency (P99) |
|---|---|---|
| **API GW + Warm Lambda (no DB)** | ~20–50ms | ~80–120ms |
| **API GW + Warm Lambda + DynamoDB** | ~30–70ms | ~100–150ms |
| **API GW + Warm Lambda + RDS** | ~50–150ms | ~200–400ms |
| **ALB + Warm Lambda (no DB)** | ~10–30ms | ~50–80ms |
| **CloudFront + API GW + Warm Lambda** | ~15–40ms | ~70–100ms |

---

## The Biggest Latency Culprits

### 1. API Gateway adds ~10–15ms overhead
```
ALB        → ~1–3ms overhead   ✅ faster
API Gateway → ~10–15ms overhead ❌ slower but more features
```

### 2. VPC adds ~1–3ms to Lambda init (warm: negligible)
```javascript
// If Lambda is in a VPC, first connection to RDS is slower
// but subsequent calls reuse the connection — near zero overhead
```

### 3. Geographic distance is huge
```
User in Europe → API in us-east-1:  +80–150ms (speed of light)
User in Europe → API in eu-west-1:  +5–20ms   ✅
```

### 4. Database is usually the bottleneck
```
DynamoDB  (same region):  ~1–5ms   ✅ fastest
ElastiCache Redis:        ~0.5–2ms ✅✅ fastest
Aurora Serverless v1:     ~20–30ms ❌ (cold connection)
RDS PostgreSQL:           ~2–10ms  ✅ (warm connection pool)
```

---

## Practical Benchmark (Real World)

```
Browser sends request
├── DNS (cached):           1ms
├── TLS resumption:         1ms
├── Network to AWS:        15ms   (US user → us-east-1)
├── API Gateway:           12ms
├── Warm Lambda:            3ms   (simple logic)
└── DynamoDB read:          4ms
                          ──────
Total P50:                ~36ms   ✅ feels instant
Total P99:                ~90ms   ✅ still good
```

---

## How to Measure Your Actual Latency

### From the browser (DevTools)
```
Network Tab → Select your API call:
├── TTFB (Time to First Byte) = full server latency
├── Content Download          = response size latency
```

### Add server-side timing headers
```javascript
export const handler = async (event) => {
  const start = Date.now();
  const data = await db.query('...');

  return {
    statusCode: 200,
    headers: {
      'Server-Timing': `db;dur=${Date.now() - start}`,
      'X-Lambda-Duration': `${Date.now() - start}ms`
    },
    body: JSON.stringify(data)
  };
};
```

### Use AWS X-Ray for tracing
```javascript
import { captureAWSv3Client } from 'aws-xray-sdk';
const ddb = captureAWSv3Client(new DynamoDBClient({}));
// X-Ray will break down every segment automatically
```

---

## Key Takeaways

| Rule | Impact |
|---|---|
| Warm Lambda execution itself | **~1–10ms** — not the problem |
| API Gateway overhead | **~10–15ms** — consider ALB for high perf |
| Network/geography | **Largest factor** — deploy close to users |
| Database calls | **Often the real bottleneck** — cache aggressively |
| Use CloudFront | Cuts TLS + network overhead significantly |

> **Bottom line:** A well-architected warm Lambda API feels like **30–60ms total** from a nearby user — well within the 100ms "instant" perception threshold.
