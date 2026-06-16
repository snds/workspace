---
name: devops-observability
description: >
  Observability stack design, SLO engineering, and on-call operations for
  enterprise SaaS. Specialist spoke in the lead-devops-engineer network. Use
  this skill whenever the conversation touches: Prometheus, PromQL, metric types,
  Counter, Gauge, Histogram, Summary, recording rules, alerting rules,
  Alertmanager, remote write, Thanos, VictoriaMetrics, Grafana Mimir,
  OpenTelemetry, OTel, distributed tracing, automatic instrumentation, manual
  instrumentation, W3C TraceContext, trace propagation, sampling strategy,
  head-based sampling, tail-based sampling, Jaeger, Tempo, Honeycomb, Datadog,
  Lightstep, structured logging, JSON logging, log correlation, trace_id in logs,
  Loki, Promtail, Elasticsearch, OpenSearch, Fluentd, Fluent Bit, Grafana
  dashboards, exemplars, SLO, error budget, burn rate alerting, multi-window
  multi-burn-rate, on-call design, runbook structure, alert fatigue, PagerDuty,
  OpsGenie, Pyroscope, Parca, continuous profiling.
  Not for: Kubernetes metrics routing (Prometheus ServiceMonitor setup in the
  cluster) — that's at the boundary with devops-container-orchestration. Not for:
  CI build time metrics — route to devops-ci-cd. Not for: cost attribution — route
  to devops-cost-optimization.
---

# DevOps: Observability

Specialist lens for observability stack design, SLO engineering, and on-call
operations in enterprise SaaS. Part of the lead-devops-engineer skill network.

---

## Domain Boundary

This skill owns: **metrics (Prometheus + PromQL), distributed tracing (OTel),
structured logging, Grafana, SLO engineering, and on-call design**.

- Kubernetes metrics infrastructure (ServiceMonitor CRDs, mesh metrics) → `devops-container-orchestration`
- Observability cost (cardinality, sampling rates as a cost lever) → `devops-cost-optimization`
- Logging infrastructure provisioning in IaC → `devops-infrastructure-as-code`

---

## The Three Pillars (Plus One)

**Metrics** answer: is something wrong? Are we meeting our SLOs? What's the rate?
**Logs** answer: what happened? What was the request context when it failed?
**Traces** answer: where did the time go? Which service in the call chain was slow?
**Profiles** (the fourth pillar): which line of code is consuming the CPU/memory?

The four are most powerful when correlated. A Grafana dashboard that shows a
latency spike → links to the exemplar trace → links to the log lines from that
trace request → links to the CPU profile from that time window is the goal.
The individual pillar is just the entry point.

---

## Prometheus

### Metric Types — When to Use Each

**Counter**: a value that only goes up (request count, error count, bytes sent).
Never use a counter for something that can decrease.

```
http_requests_total{method="GET", status="200"} 14230
```

**Gauge**: a value that goes up and down (current connections, queue depth, memory usage).

```
active_connections{service="api"} 47
```

**Histogram**: samples observations into buckets, exposing `_count`, `_sum`,
and `_bucket`. Use for latency, request size, response size. Allows quantile
calculation at query time.

```
http_request_duration_seconds_bucket{le="0.1"} 4800
http_request_duration_seconds_bucket{le="0.5"} 9200
http_request_duration_seconds_bucket{le="1.0"} 9950
http_request_duration_seconds_bucket{le="+Inf"} 10000
http_request_duration_seconds_count 10000
http_request_duration_seconds_sum 1247.3
```

**Summary**: pre-calculates quantiles at the instrumentation side (in the application).
**Almost always use Histogram instead of Summary.** Summary cannot be aggregated
across instances (each instance calculates its own quantiles independently), making
it useless for multi-replica services. Histogram quantiles are calculated at query
time across all instances.

Summary is only appropriate when you need accurate quantiles in a single-process
context where cardinality-free pre-computation is valuable (rare).

### PromQL Patterns

```promql
# Request rate (per second, 5-minute window)
rate(http_requests_total[5m])

# Error rate as a fraction
sum(rate(http_requests_total{status=~"5.."}[5m]))
/
sum(rate(http_requests_total[5m]))

# P99 latency from histogram
histogram_quantile(0.99,
  sum by (le) (
    rate(http_request_duration_seconds_bucket[5m])
  )
)

# irate vs rate:
# rate(): average over the entire window — smoother, better for alerts
# irate(): instant rate using last two points — more reactive, better for graphs showing spikes

# increase() vs rate():
# increase(counter[5m]) = rate(counter[5m]) * 300 — total count over window, not per-second rate
# Use increase() for "how many X happened in the last 5 minutes" questions
```

### Recording Rules

Pre-compute expensive queries as new metrics written back to Prometheus:

```yaml
# prometheus/rules/api-server-rules.yaml
groups:
  - name: api_server_aggregations
    interval: 30s
    rules:
      - record: job:http_request_duration_seconds:p99_5m
        expr: |
          histogram_quantile(0.99,
            sum by (le, job) (
              rate(http_request_duration_seconds_bucket[5m])
            )
          )
      - record: job:http_requests_error_rate:rate5m
        expr: |
          sum by (job) (rate(http_requests_total{status=~"5.."}[5m]))
          /
          sum by (job) (rate(http_requests_total[5m]))
```

Use recording rules when:
- A PromQL expression is used in multiple dashboards or alerts (DRY for queries)
- A query is expensive (high cardinality, long range) and runs frequently (dashboard auto-refresh)
- You need to compute aggregations across label dimensions to reduce cardinality

### Alertmanager Routing

```yaml
# alertmanager/config.yaml
route:
  receiver: default-slack
  group_by: [alertname, service]
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 4h
  routes:
    - match:
        severity: critical
      receiver: pagerduty-on-call
      continue: false
    - match:
        severity: warning
      receiver: slack-warnings
    - match:
        team: data-platform
      receiver: data-team-slack

receivers:
  - name: pagerduty-on-call
    pagerduty_configs:
      - service_key: $PAGERDUTY_SERVICE_KEY
  - name: slack-warnings
    slack_configs:
      - channel: #alerts-warning

inhibit_rules:
  # Suppress warning alerts when a critical alert for the same service fires
  - source_match:
      severity: critical
    target_match:
      severity: warning
    equal: [service]
```

### Remote Write for Long-Term Storage

Prometheus's local storage is not designed for long-term retention. Use remote write:

```yaml
# prometheus/config.yaml
remote_write:
  - url: https://thanos-receive.example.com/api/v1/receive
    # OR VictoriaMetrics:
  - url: http://victoria-metrics:8428/api/v1/write
```

**Thanos**: horizontally scalable, multi-cluster aggregation, deduplication, object
storage (S3/GCS) for long-term data. Use when you have multiple Prometheus instances
and need a unified query view.

**VictoriaMetrics**: single-binary alternative to Thanos, lower operational complexity,
excellent compression, drop-in PromQL compatible. Use for simpler setups or when
Thanos operational overhead is not justified.

**Grafana Mimir**: the cloud-native multi-tenant variant. Use if you're already on
Grafana Cloud or running the LGTM stack (Loki, Grafana, Tempo, Mimir).

---

## OpenTelemetry

### The OTel Model

```
Application (SDK) → OTel Collector → Backend (Jaeger, Tempo, Honeycomb, Datadog)
```

The Collector is the decoupling layer: applications emit to a local collector,
the collector enriches, samples, batches, and exports to one or more backends.
Changing the backend (from Jaeger to Honeycomb) requires only a collector config
change, not an application change.

### Instrumentation: Auto vs. Manual

**Automatic (zero-code) instrumentation**: language agents that instrument framework
calls (HTTP, database queries, message queues) without code changes.

```bash
# Node.js: use @opentelemetry/auto-instrumentations-node
node --require @opentelemetry/auto-instrumentations-node/register app.js

# Python: opentelemetry-instrument
opentelemetry-instrument --service-name=api-server python app.py

# Java: -javaagent
java -javaagent:opentelemetry-javaagent.jar -jar app.jar
```

Automatic instrumentation covers: HTTP client/server, database queries (pg, mysql,
redis), gRPC, messaging (Kafka, RabbitMQ). Provides good coverage with no developer
effort — start here.

**Manual instrumentation**: add spans for custom business logic:

```typescript
import { trace, context } from "@opentelemetry/api";

const tracer = trace.getTracer("order-service");

async function processOrder(orderId: string) {
  const span = tracer.startSpan("processOrder");
  span.setAttribute("order.id", orderId);
  span.setAttribute("order.tenant_id", ctx.tenantId);

  try {
    const result = await doWork();
    span.setStatus({ code: SpanStatusCode.OK });
    return result;
  } catch (err) {
    span.setStatus({ code: SpanStatusCode.ERROR, message: err.message });
    span.recordException(err);
    throw err;
  } finally {
    span.end();
  }
}
```

Add spans for: business logic operations (not just HTTP calls), batch job processing,
expensive computation, external API calls not covered by auto-instrumentation.

### Propagation

W3C TraceContext (`traceparent` header) is the standard. Set it automatically by
the OTel SDK. Ensure every service passes `traceparent` downstream and reads it from
upstream requests.

Failure mode: a service that generates a new trace ID instead of inheriting the
incoming `traceparent` breaks the trace chain. All services in the call graph must
participate in propagation for end-to-end traces.

### Sampling Strategies

**Head-based sampling**: decision made at trace start (first service). Simple but
problematic — you don't know if the trace is interesting until it completes.
Low-volume production: 100%. High-volume: fixed 10-20% of all traces.

**Tail-based sampling**: decision made after the trace completes. Can sample
based on outcome (always sample errors, always sample slow traces, sample 1% of fast
successful traces). Requires the collector to hold traces in memory until they complete.

```yaml
# OTel Collector tail-based sampler
processors:
  tail_sampling:
    decision_wait: 10s        # wait for all spans before deciding
    num_traces: 100000
    policies:
      - name: errors-policy
        type: status_code
        status_code: {status_codes: [ERROR]}
      - name: slow-traces
        type: latency
        latency: {threshold_ms: 1000}
      - name: probabilistic-normal
        type: probabilistic
        probabilistic: {sampling_percentage: 5}
```

Tail-based sampling is worth the complexity for high-volume services. You capture
100% of error traces and slow traces — exactly what you need for debugging — while
sampling down healthy fast traces.

### Collector Pipeline

```yaml
# otelcol-config.yaml
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317
      http:
        endpoint: 0.0.0.0:4318

processors:
  batch:
    timeout: 10s
    send_batch_size: 1000
  memory_limiter:
    limit_mib: 512
  resource:
    attributes:
      - key: environment
        value: production
        action: upsert

exporters:
  otlp:
    endpoint: tempo:4317    # Grafana Tempo
  prometheus:
    endpoint: 0.0.0.0:8889  # expose metrics from spans for Prometheus scrape

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [memory_limiter, resource, batch]
      exporters: [otlp]
    metrics:
      receivers: [otlp]
      processors: [batch]
      exporters: [prometheus]
```

---

## Structured Logging

### Mandatory Fields

Every log line must include:

```json
{
  "timestamp": "2025-03-15T10:30:00.123Z",
  "level": "info",
  "service": "order-service",
  "version": "1.4.2",
  "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736",
  "span_id": "00f067aa0ba902b7",
  "request_id": "req_abc123xyz",
  "tenant_id": "t_789",
  "message": "Order processed successfully",
  "order_id": "ord_456",
  "duration_ms": 143
}
```

`trace_id` and `span_id` are injected automatically by the OTel SDK when a span is
active. Extract them with:

```typescript
import { trace, context } from "@opentelemetry/api";

function getTraceContext() {
  const span = trace.getActiveSpan();
  if (!span) return {};
  const ctx = span.spanContext();
  return { trace_id: ctx.traceId, span_id: ctx.spanId };
}
```

### Log Levels

| Level | Use when | Production default |
|-------|----------|-------------------|
| `error` | Something failed that requires attention — a request errored, an expected resource was missing | Always on |
| `warn` | Something unexpected happened but the system recovered — a retry succeeded, a fallback was used | Always on |
| `info` | Normal operations worth recording — request completed, job started/finished | Always on |
| `debug` | Detailed diagnostic data — intermediate values, branch decisions | Off in production |

**Never log at DEBUG level in production at scale.** A high-traffic service logging
every request at DEBUG generates terabytes of logs/day and makes the logs useless by
volume. If you need DEBUG for an investigation, sample it: log 1% of requests at DEBUG
via a feature flag, not a global log level change.

### Log Correlation: Trace → Logs

The key workflow: you see a latency spike in a Grafana trace, click a span, click
"Logs from this request" — Grafana uses `trace_id` to query Loki/Elasticsearch for
all logs with that trace ID. This only works if `trace_id` is in every log line.

```yaml
# Grafana data source linking (Loki → Tempo)
derivedFields:
  - name: TraceID
    matcherRegex: '"trace_id":"([a-f0-9]+)"'
    url: http://tempo:3200/trace/$${__value.raw}
    urlDisplayLabel: View trace
```

### Log Aggregation Options

| Stack | Use when |
|-------|---------|
| Loki + Promtail | Already using Grafana stack. Low cost. Label-based indexing (not full-text). Good for tail-based log queries. |
| Elasticsearch + Fluentd/Fluent Bit | Need full-text search, complex field queries, rich analytics. Higher cost and operational complexity. |
| Datadog Logs | Already using Datadog for metrics/APM. Tight integration. Premium cost. |
| Cloud-native (CloudWatch, Stackdriver) | Simple setups on a single cloud. Avoid for multi-cloud or when cost control is a priority. |

---

## Grafana Dashboards

### Dashboard Design Principles

- **One metric per panel.** Two metrics on one graph require two Y-axes or normalized
  scales — both hurt readability. If you need comparison, use linked panels side-by-side.
- **Consistent time ranges** across all panels in a dashboard. Mixed time ranges
  hide causation relationships.
- **Annotation layers** for deployments: mark every production deploy on your dashboards
  with a vertical annotation. This makes the question "did this metric change after the
  last deploy?" answerable in 2 seconds.
- **Row hierarchy**: organize top-to-bottom as Overview → Service Health → Errors →
  Latency → Saturation → Dependencies. The overview row should be readable without scrolling.

### Exemplars — Linking Metrics to Traces

Exemplars attach a specific trace ID to a histogram observation:

```typescript
// In your metrics instrumentation:
histogram.record(durationMs, {
  attributes: { method: "GET", route: "/api/orders" },
  // OTel attaches the current trace_id as exemplar automatically when a span is active
});
```

In Grafana: enable exemplars on the Prometheus datasource. When viewing a P99
latency histogram, click a spike → Grafana shows the exemplar trace ID → click to
open the trace in Tempo. This is the most powerful cross-pillar correlation available.

---

## SLO Engineering

### Error Budget Calculation

```
Availability target: 99.9%
Error budget per 30-day window:
  = (1 - 0.999) × 30 × 24 × 60 = 43.2 minutes of allowed downtime

Error budget as request error rate:
  If you serve 1M requests/month:
  = 0.001 × 1,000,000 = 1,000 allowed failing requests/month
```

### Multi-Window Multi-Burn-Rate Alerting

The Google SRE burn rate model. A single threshold alert on error rate misses both
slow burns (gradual degradation that won't exhaust budget for days) and fast burns
(sudden complete outage that exhausts budget in an hour).

The solution: multiple windows, each catching a different failure mode.

| Window | Burn rate | Meaning | Alert severity |
|--------|-----------|---------|---------------|
| 1h / 5m | 14× | 1h window burning at 14× = 2% budget consumed — page now | Critical (page) |
| 6h / 30m | 6× | Significant burn over several hours | Critical (page) |
| 3d / 6h | 1× | Budget burn tracked, not critical yet | Warning (ticket) |

```yaml
# Prometheus alerting rule: fast burn
- alert: SLOFastBurn
  expr: |
    (
      sum(rate(http_requests_total{status=~"5.."}[1h])) / sum(rate(http_requests_total[1h]))
    ) > (14 * 0.001)    # 14x burn rate on 99.9% SLO
    AND
    (
      sum(rate(http_requests_total{status=~"5.."}[5m])) / sum(rate(http_requests_total[5m]))
    ) > (14 * 0.001)
  for: 2m
  labels:
    severity: critical
  annotations:
    summary: "High error rate — burning error budget fast"
```

### SLO as a Product Decision

The SLO target is not an engineering decision alone. It encodes a promise to customers
and a constraint on engineering velocity. Higher availability = smaller error budget =
slower deployment cadence + more investment in reliability.

The conversation with product:
- "99.9% means we can afford one 43-minute outage per month before customers get SLA
  credits. 99.99% means 4 minutes. That difference costs $X in engineering and $Y in
  slower feature velocity. Is the customer segment willing to pay for 99.99%?"
- SLO targets should appear in the product roadmap, not just the ops runbook.

---

## On-Call Design

### Runbook Structure

Every alert must have a runbook. The runbook follows this template:

```markdown
# Alert: [Alert Name]

## Symptoms
- What the user experiences
- What metrics triggered this alert

## Diagnosis Steps
1. Check [dashboard link] — look for [specific pattern]
2. Run: `kubectl logs -n production deploy/api-server --since=10m | grep ERROR`
3. Check [external dependency] status at [status page URL]
4. If X, suspect Y → jump to Section 3

## Remediation
### Option A: Restart the affected pods (safe, try first)
```kubectl rollout restart deploy/api-server -n production```
Expected result: pods restart within 2 minutes, error rate drops

### Option B: Roll back the last deploy
```./scripts/rollback.sh production $PREVIOUS_SHA```

## Escalation Path
- 15 minutes without resolution → escalate to [team/person]
- If customer impact confirmed → notify [customer success channel]

## Post-Incident
- Link to post-mortem template: [link]
```

### The 95% Actionability Rule

An alert is only worth having if ≥95% of the time it fires, a human can take an action
that improves the situation. An alert that fires and the response is "looks like noise,
snooze" is not an alert — it's alert fatigue.

Audit your alerts quarterly:
- Any alert that was snoozed more than 3 times in the past month: either improve the
  condition (add a stabilization period, tighten the threshold) or delete it.
- Any alert that fired without a runbook entry: add the runbook before the next on-call
  rotation. The person who investigated this alert knows what to do — capture it now.

### PagerDuty / OpsGenie Routing

```
Alert fires (Alertmanager) →
  CRITICAL → PagerDuty primary on-call (immediate page)
  WARNING → Slack #alerts-warning (no page; reviewed next business day)
  INFO → suppressed or Slack #alerts-noise (review weekly)

PagerDuty:
  Primary on-call: 5-minute response time expectation
  Escalation after 15 min: secondary on-call
  Escalation after 30 min: engineering manager
```

On-call rotation design:
- Follow-the-sun for global teams: regional primary on-call during business hours only
- 1-week rotations with an explicit "off-call week" per engineer
- Shadow rotation for new engineers (observe before going primary)
- Incident review as the primary learning mechanism — not blame-oriented post-mortems

---

## Cross-Spoke Routing

| Topic | Route To |
|-------|----------|
| Prometheus ServiceMonitor CRDs in k8s | `devops-container-orchestration` |
| Observability cardinality as a cost problem | `devops-cost-optimization` |
| IaC for observability infrastructure | `devops-infrastructure-as-code` |
| OTel instrumentation in the backend service | `be-service-architecture` (twelve-factor, observability architecture) |
| SLO target as product strategy | product management context |
| CI/CD build metrics | `devops-ci-cd` |
