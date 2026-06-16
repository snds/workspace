---
name: be-service-architecture
description: >
  Monolith vs. microservices tradeoffs, bounded contexts and Domain-Driven
  Design, event-driven architecture, distributed systems resilience patterns,
  and observability architecture for enterprise SaaS. Use this skill whenever
  the conversation touches: when to decompose a monolith, the strangler fig
  pattern, DDD bounded contexts, signs of a distributed monolith, event
  sourcing, CQRS, domain events vs. integration events, event schema evolution,
  the saga pattern (choreography vs. orchestration), compensating transactions,
  circuit breakers, bulkheads, retry budgets, graceful degradation, twelve-factor
  app for cloud deployment, distributed tracing, OpenTelemetry, structured
  logging strategy, Prometheus metrics, or any question about how services
  should be decomposed, communicate, and fail safely. Not for: Kafka and
  message queue implementation details (be-integration-patterns), API contract
  design (be-api-design), or authentication between services (be-auth-patterns).
---

# Be: Service Architecture

Specialist lens for service decomposition, event-driven architecture, distributed
systems resilience, and observability in enterprise SaaS. Part of the backend
engineering skill network.

---

## Domain Boundary

This skill owns: **service decomposition decisions, bounded context design,
event-driven patterns, distributed systems resilience, and observability
architecture**.

- Kafka, message queues, webhook implementation → `be-integration-patterns`
- API contract design between services → `be-api-design`
- Service-to-service auth (client credentials flow) → `be-auth-patterns`
- ML model serving as a service → `ds-ml-engineering`

---

## Monolith vs. Microservices

### The Monolith-First Principle

Don't decompose before you understand the domain boundaries. The cost of getting
bounded contexts wrong is paid twice: once to build the wrong service split, and
again to undo it. A well-structured monolith with clear module boundaries is
easier to maintain than a distributed monolith with shared databases.

**Premature microservices fail modes**:
- Services share a database → distributed monolith with distributed transaction overhead
- Services change together constantly → you have a monolith with network latency added
- Services can't be independently deployed → you've added complexity without benefit
- No team owns a service end-to-end → everyone has to coordinate every change

**When decomposition is genuinely warranted**:

| Signal | What It Means |
|--------|--------------|
| Radically different scaling requirements | One component needs 100x the throughput of another |
| Independent deployment frequency | Search index needs 20 deploys/day; billing needs 1/week |
| Genuine team ownership boundaries | Two separate teams own two distinct domains with clear interfaces |
| Technology heterogeneity | One component requires Python (ML); the rest is Go/Node |
| Fault isolation requirement | A payment processing failure must not affect browsing |

None of these signals alone is sufficient. All of them together make a compelling
case.

### Distributed Monolith Anti-Patterns

These are the failure modes to detect before committing to decomposition:

- **Shared database**: if two services both read and write the same tables, they
  are coupled at the data layer — decomposing the code doesn't help
- **Synchronous call chains**: Service A calls B which calls C. Any failure in C
  brings down A. The latency budget is the sum of all three. This is a monolith
  with network overhead.
- **Chatty interfaces**: 10+ API calls to render a single UI screen means the
  service boundaries don't match the UI's data access patterns — use BFF pattern
- **Shared libraries that change frequently**: a shared "models" library that all
  services depend on means all services redeploy together

---

## Domain-Driven Design for Service Boundaries

### Bounded Contexts

A bounded context is a explicit boundary within which a domain model is defined
and applicable. Different bounded contexts can use the same term with different
meanings — the key is that within a context, there is one unambiguous definition.

```
Order Management Context:     Order = confirmed, paid, ready to fulfill
Warehouse Context:            Order = pick list, physical items, shipping
Finance Context:              Order = revenue event, payment, receivable
```

Each context gets its own service (or module, if decomposition isn't yet warranted).
The interfaces between them are explicit and versioned.

**Context mapping patterns**:

| Pattern | When to Use |
|---------|------------|
| Partnership | Two teams that coordinate closely on changes |
| Customer-Supplier | Downstream depends on upstream; upstream controls the interface |
| Conformist | Downstream accepts upstream model as-is (e.g., integrating an external system) |
| Anti-Corruption Layer | Downstream translates upstream model to avoid contaminating its own model |
| Published Language | Both sides agree on a shared language (typically an event schema) |

For enterprise SaaS with multiple internal teams: Customer-Supplier or Published
Language are the most common. Anti-Corruption Layer is important when integrating
with the customer's external systems (ERP, PIM).

### The Strangler Fig Pattern

The only safe way to migrate a monolith to services: incrementally strangle
the monolith by routing specific functionality to new services, never a big-bang
rewrite.

```
Phase 1: Put a facade (API gateway or router) in front of the monolith
Phase 2: Identify a bounded context with clear boundaries and low coupling
Phase 3: Build the new service behind the facade (shadow mode — both run, compare)
Phase 4: Route traffic to the new service for that domain
Phase 5: Remove that code from the monolith
Phase 6: Repeat for the next context
```

A "big bang rewrite" alongside the running monolith is not a strangler fig — it's
a second system problem. The strangler fig requires continuous incremental progress
with the monolith still serving traffic.

---

## Event-Driven Architecture

### Domain Events vs. Integration Events

| Type | Scope | Audience | Schema Evolution |
|------|-------|----------|-----------------|
| Domain event | Within a bounded context | Internal to the service | Free — no external contract |
| Integration event | Crosses bounded context boundary | Other services, external consumers | Strict — breaking changes require versioning |

Domain events are implementation details. Integration events are API contracts.
Treat them accordingly.

### Event Sourcing

Event sourcing stores every state change as an immutable event. Current state is
derived by replaying events.

```
# Command: SubmitOrder
# Results in event: OrderSubmitted { orderId, tenantId, items, submittedAt }
# State: derived by replaying all events for this orderId
```

**When event sourcing is worth the complexity**:
- Audit trail is a hard requirement (regulated industries, compliance)
- Time travel queries are needed (what did this record look like on Jan 1?)
- Multiple independent projections from the same event stream are needed

**When it's over-engineering**:
- You just want an audit log → use an audit table (much simpler)
- You have a simple CRUD domain → append-only events buy you nothing
- Your team doesn't have experience with eventual consistency and projection maintenance

Event sourcing + CQRS without a clear reason is one of the most common
over-engineering traps in enterprise SaaS architecture.

### CQRS (Command Query Responsibility Segregation)

Separate the write model (commands, events) from the read model (queries, projections).
CQRS can be used without event sourcing: write to a normalized OLTP schema,
maintain a denormalized read model updated via triggers or application logic.

```
Write path: Order.submit() → validates business rules → persists to normalized tables
Read path:  OrderDetailView — denormalized, optimized for rendering the order detail screen
```

The benefit: write model enforces invariants cleanly; read model is optimized for
query patterns. The cost: eventual consistency (write and read model are slightly
out of sync), additional tables to maintain.

**When CQRS without event sourcing is justified**: your write and read access
patterns are genuinely incompatible (normalized OLTP for integrity, denormalized
for search/display), and the consistency lag is acceptable.

### Event Schema Evolution

Integration events are API contracts. The same evolution rules apply:

- **Additive changes**: new optional fields — backwards compatible, consumers that
  don't know the field ignore it
- **Required field changes**: never add a required field to an existing event type —
  create a new event type (v2)
- **Field removal**: mark deprecated, provide deprecation window, then remove in
  a new event schema version
- **Consumer-driven contract testing (Pact)**: consumers publish their expectations
  from a provider; providers verify they meet those expectations in CI. Prevents
  integration event schema regressions before they reach production.

---

## The Saga Pattern

Sagas coordinate distributed transactions across multiple services where a
traditional database transaction isn't possible. Each saga step has a corresponding
compensating transaction.

```
Order Placement Saga:
  1. Reserve inventory → compensate: release reservation
  2. Charge payment   → compensate: issue refund
  3. Create shipment  → compensate: cancel shipment
  4. Confirm order    → compensate: cancel order

If step 3 fails: execute compensating transactions for steps 2 and 1 (in reverse)
```

### Choreography vs. Orchestration

**Choreography**: each service listens for events and reacts. No central coordinator.

```
OrderService publishes OrderCreated
→ InventoryService listens, reserves stock, publishes StockReserved
→ PaymentService listens, charges card, publishes PaymentCharged
→ ShipmentService listens, creates shipment
```

Pros: loose coupling, no single point of failure.
Cons: business logic is distributed across services — hard to see the full flow,
hard to add a new step, hard to debug when something goes wrong.

**Orchestration**: a saga orchestrator drives the workflow.

```
OrderSaga:
  1. Send ReserveStock command to InventoryService, await response
  2. Send ChargePayment command to PaymentService, await response
  3. Send CreateShipment command to ShipmentService, await response
  4. Publish OrderConfirmed event
```

Pros: the full workflow is visible in one place, easy to add/modify steps, easier
to debug.
Cons: the orchestrator is a single point of failure (mitigate with persistence
and resumability), more coupling to the orchestrator.

**Default**: orchestration for complex flows with 3+ steps. Choreography only
when the flow is simple and the loose coupling benefit outweighs the observability cost.

---

## Resilience Patterns

### Circuit Breaker

The circuit breaker pattern prevents cascading failures when a downstream service
is degraded.

```
States:
  Closed:   requests pass through; failures are counted
  Open:     requests fail fast without hitting downstream; no retry
  Half-open: a probe request is allowed; if it succeeds, transition to closed

Transition rules:
  Closed → Open:     failure rate exceeds threshold (e.g., 50% in 30s window)
  Open → Half-open:  after a timeout period (e.g., 60 seconds)
  Half-open → Closed: probe succeeds
  Half-open → Open:  probe fails
```

Library: Resilience4j (Java), Polly (.NET), `opossum` (Node.js), `pybreaker` (Python).

### Retry with Exponential Backoff and Jitter

```python
def retry_with_backoff(func, max_retries=3, base_delay=1.0, max_delay=30.0):
    for attempt in range(max_retries + 1):
        try:
            return func()
        except TransientError as e:
            if attempt == max_retries:
                raise
            delay = min(base_delay * (2 ** attempt), max_delay)
            jitter = delay * 0.2 * random()  # ±20% jitter to prevent thundering herd
            time.sleep(delay + jitter)
```

**Only retry idempotent operations.** Retrying a non-idempotent POST without an
idempotency key can create duplicate records.

### Bulkhead Pattern

Isolate failure domains using separate thread pools or connection pools per
downstream dependency.

```
Without bulkhead: all API endpoints share one thread pool
  → slow downstream payment service exhausts all threads
  → entire API is unavailable

With bulkhead: payment calls use a dedicated thread pool (max 20 threads)
  → payment calls queue or fail when pool is exhausted
  → all other endpoints continue to serve traffic normally
```

### Graceful Degradation

Every service must define its behavior when each of its dependencies is unavailable:

| Dependency | Available | Degraded Behavior |
|-----------|-----------|------------------|
| Primary DB | Down | Read from replica (stale), queue writes |
| Cache | Down | Read through to DB (slower but correct) |
| Search service | Down | Disable search, return empty results with error message |
| Email service | Down | Queue emails, do not block the primary flow |
| Analytics service | Down | Drop events (non-critical), log locally |

The degraded behavior must be designed and tested, not discovered in a postmortem.

---

## Twelve-Factor App for Enterprise SaaS

| Factor | Enterprise SaaS Implication |
|--------|-----------------------------|
| Config in environment | Database URLs, API keys, feature flags via env vars or secrets manager. No config in code. |
| Stateless processes | Session state in Redis, not in-process. Any instance can serve any request. |
| Explicit dependencies | `requirements.txt`, `package.json`, `pom.xml`. No system-level implicit dependencies. |
| Disposable processes | Fast startup (<30s), graceful shutdown (drain in-flight requests). Enables autoscaling. |
| Dev/prod parity | Same database engine, same OS, same environment variables in dev and prod. Docker Compose. |
| Logs as event streams | Structured JSON to stdout/stderr. No log files. Collected by the platform. |
| Port binding | Services listen on a port, expose themselves via that port. No app server embedded in OS. |
| Admin processes | Database migrations, backfills as one-off processes in the same environment. |

---

## Observability Architecture

Observability is implemented at the service boundary, not as an afterthought.

### The Three Pillars

**Logs**: structured JSON, one object per line, to stdout.
```json
{
  "timestamp": "2024-01-01T00:00:00Z",
  "level": "info",
  "trace_id": "abc123",
  "span_id": "def456",
  "tenant_id": "t_789",          // always present — required for debugging tenant issues
  "request_id": "req_012",
  "message": "Order submitted",
  "order_id": "ord_345",
  "duration_ms": 145
}
```

**Metrics**: Prometheus-compatible, scraped by the platform.
- Request rate, error rate, duration (RED metrics) — per endpoint
- Saturation metrics: connection pool utilization, queue depth, cache hit rate

**Traces**: OpenTelemetry distributed traces propagated across service calls.
Every inbound request creates a span; every outbound call (database, external API,
message queue) creates a child span.

```python
# Instrument every service boundary
with tracer.start_as_current_span("order.submit") as span:
    span.set_attribute("tenant.id", tenant_id)
    span.set_attribute("order.id", order_id)
    result = process_order(order)
    span.set_attribute("order.status", result.status)
```

### What to Alert On

Alert on SLO breaches, not on symptoms:

- Error rate > 1% over 5 minutes → page
- P99 latency > SLO threshold → page
- Queue depth > N for > 10 minutes → page
- Circuit breaker open on critical dependency → page

Do not alert on CPU%, memory%, or other resource metrics directly — alert on the
user-facing symptoms they cause.

---

## Cross-Spoke Routing

| Topic | Route To |
|-------|----------|
| Kafka topic design, message queue patterns | `be-integration-patterns` |
| API contract between services | `be-api-design` |
| Service-to-service OAuth (client credentials) | `be-auth-patterns` |
| ML model serving as a microservice | `ds-ml-engineering` |
| Event data flowing to analytics pipeline | `ds-data-engineering` |
