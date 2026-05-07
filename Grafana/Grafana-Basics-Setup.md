# Grafana Basics and Setup
I have a solid picture of the current state of Grafana + AWS + OTel. Let me walk you through this end-to-end.

---

## What is Grafana?

Grafana is an **observability and visualization platform**. Think of it as the "single pane of glass" for understanding what your systems are doing — not just showing pretty dashboards, but actively helping you debug, monitor, and alert on your applications.

The key mental model: Grafana itself **doesn't store your data**. It connects to data sources (databases, cloud services, collectors) and visualizes them. This is why it's so popular — it works with almost everything.

---

## The LGTM Stack — Grafana's Core Ecosystem

When people say "Grafana," they often mean the full stack of Grafana Labs tools:

**L — Loki** (logs): Like Elasticsearch but cheaper and label-based. Stores log lines and lets you query them with LogQL.

**G — Grafana** (visualization): The UI layer. Dashboards, alerts, explore mode.

**T — Tempo** (traces): Stores distributed traces — the full journey of a request through your system.

**M — Mimir** (metrics): A horizontally scalable Prometheus-compatible metrics store.

You can use **Grafana Cloud** (hosted, free tier available) so you don't have to run any of this yourself — highly recommended for a first project.

---

## What is OpenTelemetry (OTel)?

OpenTelemetry is the **open standard** for instrumentation. It defines how your code emits three types of telemetry:

- **Traces** — the path a single request takes through your system (e.g., Lambda A → SQS → Lambda B → DynamoDB)
- **Metrics** — numeric measurements over time (invocation count, duration, error rate)
- **Logs** — timestamped text events

The beauty of OTel is that it's **vendor-neutral**. You instrument your code once, and you can send the data to Grafana, Datadog, Jaeger, or anything else — without changing your code. This avoids lock-in.

The three pieces of OTel you'll work with:

- **SDK** — the library you add to your code to emit telemetry
- **Collector** — a sidecar/agent that receives, processes, and exports telemetry (the OTLP Collector)
- **OTLP** — the wire protocol data travels over (usually gRPC port 4317 or HTTP port 4318)

---

## Why Lambda Makes This Tricky

Lambda is different from traditional servers in a few key ways: you have no direct server access to install agents, the architecture is highly distributed across components like API Gateway and DynamoDB, and functions are ephemeral — they may exist only for a single request, so telemetry must be exported quickly.

In the Lambda execution model, functions are called directly and the environment is frozen afterward. You're only billed for actual execution time, so keeping the function alive until metrics can be collected isn't really an option. And different invocations will have completely separate contexts and won't necessarily know about all other executions happening simultaneously.

The solution is **Lambda Extension Layers**.

---

## The Architecture — How It All Fits Together

Here's the data flow for a typical AWS pipeline with Grafana:

```
Your Lambda (instrumented with OTel SDK)
        ↓  OTLP (localhost:4317)
OTel Collector Extension Layer  ← runs alongside your Lambda
        ↓  OTLP/HTTPS
Grafana Cloud (or self-hosted)
    ├── Loki     ← logs
    ├── Tempo    ← traces
    └── Mimir    ← metrics
        ↓
Grafana UI ← dashboards, alerts, explore
```

For pipelines with multiple Lambdas (e.g., SQS-triggered chains), **trace context is propagated** via headers so Tempo can stitch the full journey together.

---

## Step 1 — Set Up Grafana Cloud

1. Sign up at [grafana.com](https://grafana.com) — the free tier gives you 50GB of logs, 10K series of metrics, and 50GB of traces per month, which is plenty to start.
2. Go to your stack → click **OpenTelemetry** card. Note down:
   - Your **OTLP endpoint** (e.g., `otlp-gateway-prod-us-east-0.grafana.net:443`)
   - Your **Instance ID**
   - Generate an **API key** with MetricsPublisher + LogsPublisher + TracesPublisher scopes

---

## Step 2 — Instrument Your Lambda

Here's a Node.js Lambda with OTel SDK:

```bash
npm install @opentelemetry/sdk-node \
            @opentelemetry/auto-instrumentations-node \
            @opentelemetry/exporter-trace-otlp-grpc
```

Create a `tracing.js` init file (loaded before your handler):

```js
const { NodeSDK } = require('@opentelemetry/sdk-node');
const { OTLPTraceExporter } = require('@opentelemetry/exporter-trace-otlp-grpc');
const { getNodeAutoInstrumentations } = require('@opentelemetry/auto-instrumentations-node');

const sdk = new NodeSDK({
  traceExporter: new OTLPTraceExporter({
    // Points to the local OTel Collector Extension Layer
    url: 'grpc://localhost:4317',
  }),
  instrumentations: [getNodeAutoInstrumentations()],
});

sdk.start();
```

Then in your Lambda handler, wrap it:

```js
// handler.js
require('./tracing'); // initialize OTel first

exports.handler = async (event) => {
  // Your existing code — OTel auto-instruments AWS SDK, HTTP calls, etc.
  const result = await someDBCall();
  return result;
};
```

The `auto-instrumentations-node` package automatically instruments AWS SDK v3 calls, HTTP requests, and more — **zero manual span creation needed to start**.

For manual spans (when you want to trace a specific block of business logic):

```js
const { trace } = require('@opentelemetry/api');
const tracer = trace.getTracer('my-lambda');

exports.handler = async (event) => {
  const span = tracer.startSpan('process-order');
  try {
    span.setAttribute('order.id', event.orderId);
    await processOrder(event);
    span.setStatus({ code: SpanStatusCode.OK });
  } catch (err) {
    span.recordException(err);
    span.setStatus({ code: SpanStatusCode.ERROR });
    throw err;
  } finally {
    span.end(); // critical — always end spans
  }
};
```

---

## Step 3 — Add the OTel Collector Extension Layer

Grafana built a distribution of the OTel Lambda extension layer that bundles a simple configuration file, receives data from the Lambda telemetry API, and sends it to the Grafana Cloud OpenTelemetry endpoint. Everything is configurable through environment variables.

In your Lambda config (via console, CDK, or Terraform), add the layer ARN from [github.com/grafana/collector-lambda-extension](https://github.com/grafana/collector-lambda-extension) for your region, then set these environment variables:

```bash
GRAFANA_CLOUD_INSTANCE_ID=650111          # your stack ID
GRAFANA_CLOUD_API_KEY_ARN=arn:aws:secretsmanager:us-east-1:...:secret:grafana-token
```

The `GRAFANA_CLOUD_API_KEY_ARN` needs to be a reference to an existing secret in AWS Secrets Manager, and you need to add the `secretsmanager:GetSecretValue` permission to the executing Lambda role.

The **decouple processor** is the clever part here: it separates the receiving and exporting components while interfacing with the Lambda lifecycle. This allows the Lambda to return even if not all data has been sent. At the next invocation (or on shutdown), the collector continues shipping the data while your function does its thing — compared to sending data directly from the application, this reduces billed time significantly on repeated requests.

---

## Step 4 — Connecting to AWS Data Pipelines

For multi-Lambda pipelines (e.g., API Gateway → Lambda A → SQS → Lambda B → DynamoDB), **trace propagation** is what connects them into one end-to-end trace. OTel's auto-instrumentation handles this automatically for AWS SDK v3 calls by injecting the `traceparent` header into SQS message attributes.

You just need each Lambda to have the OTel layer + env vars configured. Tempo will automatically stitch the spans into a waterfall view.

For other AWS pipeline components:

- **SQS / SNS** — trace context flows through message attributes automatically with auto-instrumentation
- **API Gateway** — use the `X-Amzn-Trace-Id` propagator or standard W3C `traceparent` headers
- **DynamoDB / S3** — AWS SDK v3 auto-instrumentation captures these as child spans
- **Step Functions** — requires manual span creation in each Lambda state

For **log correlation** (so you can jump from a log line to its trace in Grafana), add the trace ID to your log output:

```js
const { trace } = require('@opentelemetry/api');

exports.handler = async (event) => {
  const spanContext = trace.getActiveSpan()?.spanContext();
  console.log(JSON.stringify({
    message: 'Processing event',
    traceId: spanContext?.traceId,
    spanId: spanContext?.spanId,
    orderId: event.orderId,
  }));
};
```

Loki will ingest these JSON logs and Grafana can auto-link between them and Tempo traces.

---

## Step 5 — Building Dashboards in Grafana

Once data is flowing, you'll use three main views in Grafana:

**Explore** — ad-hoc querying. Use this first to verify data is arriving:
- Loki query: `{service_name="my-lambda"} |= "error"`
- Tempo: search by service name, status code, or duration
- Mimir: `rate(http_server_duration_milliseconds_count[5m])`

**Dashboards** — saved panels. For a Lambda pipeline, a good starter dashboard has:
- Invocation rate (metric)
- Error rate (metric)
- P99 duration (metric)
- Recent error logs (Loki)
- Slow traces table (Tempo)

**Alerting** — set thresholds on any query. E.g., alert if error rate exceeds 1% for 5 minutes.

---

## The Collector YAML (If You Self-Host or Customize)

If you want full control (e.g., self-hosted OTel Collector on ECS or EC2 as a central gateway), the config looks like this:

```yaml
# collector.yaml
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: "0.0.0.0:4317"
      http:
        endpoint: "0.0.0.0:4318"

exporters:
  otlp:
    endpoint: otlp-gateway-prod-us-east-0.grafana.net:443
    headers:
      authorization: "Basic <base64(instanceId:apiKey)>"

service:
  pipelines:
    traces:
      receivers: [otlp]
      exporters: [otlp]
    metrics:
      receivers: [otlp]
      exporters: [otlp]
    logs:
      receivers: [otlp]
      exporters: [otlp]
```

---

## Quick Reference — Which Tool Does What

| Layer | Tool | Purpose |
|---|---|---|
| Instrumentation | OTel SDK | Emit traces, metrics, logs from your code |
| Collection | OTel Collector (Lambda Layer) | Buffer & forward telemetry from Lambda |
| Logs storage | Grafana Loki | Query with LogQL |
| Trace storage | Grafana Tempo | Full request traces |
| Metrics storage | Grafana Mimir | Time-series metrics, PromQL |
| Visualization | Grafana | Dashboards, alerts, explore |

---

## Recommended Starting Path

1. **Sign up for Grafana Cloud** (free tier is plenty)
2. **Add the Grafana Lambda extension layer ARN** to one Lambda
3. **Set the 2 env vars** (instance ID + Secrets Manager ARN)
4. **Invoke the Lambda** a few times, then open Grafana → Explore → Loki and search for your service name
5. Once logs appear, add the OTel SDK for traces
6. Build your first dashboard from the Lambda Monitoring template Grafana provides out of the box

The cold-start overhead of the extension layer is minimal, and once it clicks, having full traces across an entire Lambda pipeline is a genuinely game-changing debugging experience — especially when you're chasing a bug that only manifests 3 hops deep in an async SQS chain.
