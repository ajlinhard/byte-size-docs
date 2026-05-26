## Lambda vs SageMaker: Latency to a Container Endpoint

The latency profile differs significantly depending on the invocation path, warm/cold state, and network topology. Here's a breakdown:

---

### 🔷 Lambda → Container Endpoint

This typically means Lambda invoking an **ECS/Fargate**, **ALB-fronted container**, or **another Lambda container image**.

| Scenario | Latency |
|---|---|
| **Warm Lambda → Warm ECS/Fargate (same VPC, internal ALB)** | ~1–5 ms (network) + container processing time |
| **Warm Lambda → Warm ECS via public ALB** | ~5–20 ms overhead |
| **Cold Lambda + Cold Container (Fargate)** | 1–10+ **seconds** (Lambda cold start ~100–500ms + Fargate cold start ~5–10s) |
| **Lambda Container Image cold start** | ~1–3s (larger images = slower; SnapStart can help on Java) |
| **Lambda → Lambda (container image, invoke)** | ~5–50ms warm, ~500ms–3s cold |

**Key factors:**
- Lambda cold starts add ~100–500ms (non-VPC), ~300ms–1s (VPC, without Provisioned Concurrency)
- Fargate cold starts are the bottleneck (~5–15s without pre-warmed tasks)
- Same-VPC calls via internal ALB/NLB are fastest (~1–3ms network)

---

### 🔶 SageMaker → Container Endpoint

SageMaker **hosts** the container as a real-time inference endpoint. The latency here is the **invocation overhead** added by SageMaker on top of your model's processing time.

| Scenario | Latency |
|---|---|
| **Warm SageMaker Real-Time Endpoint (invoke)** | ~5–15 ms overhead (SageMaker routing + serialization) |
| **SageMaker Serverless Inference (cold)** | ~1–3 seconds cold start |
| **SageMaker Serverless Inference (warm)** | ~10–50 ms overhead |
| **SageMaker Async Inference** | Seconds to minutes (designed for batch, not real-time) |
| **SageMaker Multi-Model Endpoint (model not loaded)** | ~1–5s to load model into container |

**Key factors:**
- SageMaker real-time endpoints keep containers **always warm** on dedicated instances (ml.* instances) — no cold start unless scaling from 0
- The SageMaker control plane adds ~5–15ms overhead per invocation (HTTP routing, authn, logging)
- Calling a SageMaker endpoint from Lambda adds ~5–20ms network latency (they communicate over AWS backbone if in same region)

---

### ⚡ Head-to-Head Comparison

| Dimension | Lambda → Container | SageMaker Endpoint |
|---|---|---|
| **Warm latency overhead** | 1–5ms (VPC) | 5–15ms |
| **Cold start** | 500ms–10s+ | ~0 (dedicated) or 1–3s (serverless) |
| **Scaling to zero** | Yes (serverless by nature) | Only with Serverless Inference |
| **Predictability** | Variable (cold starts) | High (dedicated instances) |
| **Best for** | General APIs, event-driven | ML inference, consistent low-latency |

---

### 🏁 Practical Guidance

- **Lowest warm-path latency**: Lambda → container on same VPC via internal NLB/ALB (~1–5ms network). SageMaker adds slightly more overhead per call.
- **Most predictable P99 latency**: **SageMaker real-time endpoint** on a dedicated instance — no cold starts, consistent routing.
- **Avoid** SageMaker **Serverless Inference** if sub-100ms P99 matters — cold starts will spike latency.
- **Provisioned Concurrency** on Lambda eliminates Lambda cold starts if you need serverless + low latency.
- For **ML workloads specifically**, SageMaker's overhead is worth it for the managed GPU/CPU fleet, auto-scaling, and model monitoring features.
