---
name: be-integration-patterns
description: >
  Webhook design for enterprise, event streaming with Kafka, message queue
  patterns, API gateway and Backend for Frontend (BFF) architecture, data
  contract evolution, and iPaaS integration strategy for enterprise SaaS.
  Use this skill whenever the conversation touches: outbound webhook delivery
  guarantees, HMAC-SHA256 signature verification, webhook retry and dead letter
  queues, fat vs. thin event payloads, webhook management UI requirements,
  Kafka topic design and partition strategy, consumer group patterns, Kafka
  offset management and at-least-once processing, schema registry (Avro,
  Protobuf), Kafka exactly-once semantics, topic retention policy, compacted
  topics, RabbitMQ work queues, SQS/SNS fan-out, dead letter queues, priority
  queues, BFF pattern, API aggregation gateway, consumer-driven contract testing
  with Pact, additive vs. breaking data contract changes, iPaaS platforms
  (Zapier, Workato, MuleSoft, Boomi), or any question about how your system
  integrates with other systems, customers, and data pipelines. Not for:
  API contract design for your own REST/GraphQL API (be-api-design), or
  event-driven architecture patterns within your service boundary
  (be-service-architecture covers sagas and CQRS).
---

# Be: Integration Patterns

Specialist lens for outbound integrations, event streaming infrastructure,
messaging patterns, and data contract evolution in enterprise SaaS. Part of
the backend engineering skill network.

---

## Domain Boundary

This skill owns: **webhook delivery, Kafka and message queue infrastructure,
API gateway patterns, data contract evolution, and iPaaS strategy**.

- REST/GraphQL API design for your own API surface → `be-api-design`
- Sagas, choreography, CQRS within service boundaries → `be-service-architecture`
- Kafka as observability event source → cross-reference `ds-data-engineering`
- Experiment event tracking infrastructure → `ds-experimentation`

---

## Webhook Design for Enterprise

### Delivery Guarantees — At-Least-Once with Idempotency Keys

Webhooks are inherently unreliable (network, consumer availability). Design for
at-least-once delivery. Consumers must be idempotent.

```python
# Producer: deliver with retry and idempotency key
def deliver_webhook(endpoint_id: str, event: dict):
    payload = {
        "id": str(uuid4()),              # idempotency key — consumer deduplicates on this
        "type": "order.created",
        "created_at": utcnow().isoformat(),
        "data": { "order_id": event["order_id"], ... }
    }
    signature = compute_signature(payload, endpoint.secret)
    
    for attempt in range(5):
        try:
            response = requests.post(
                endpoint.url, json=payload,
                headers={
                    "X-Webhook-Signature": f"sha256={signature}",
                    "X-Webhook-Id": payload["id"],
                    "X-Webhook-Timestamp": payload["created_at"]
                },
                timeout=30
            )
            if response.status_code < 500:  # don't retry 4xx — consumer rejected it
                break
        except requests.RequestException:
            pass
        time.sleep(min(2 ** attempt * 5, 300))  # exponential backoff, cap at 5 minutes
    else:
        dlq.publish(payload)  # dead letter after max retries
```

### HMAC-SHA256 Signature Verification

```python
# Consumer: verify before processing
import hmac, hashlib, time

def verify_webhook(payload_body: bytes, signature_header: str,
                   timestamp_header: str, secret: str) -> bool:
    # Reject if timestamp is too old (replay attack prevention)
    timestamp = int(timestamp_header)
    if abs(time.time() - timestamp) > 300:  # 5-minute window
        return False
    
    # Compute expected signature
    signed_payload = f"{timestamp}.{payload_body.decode()}"
    expected = hmac.new(
        secret.encode(), signed_payload.encode(), hashlib.sha256
    ).hexdigest()
    
    # Constant-time comparison (prevents timing attacks)
    received = signature_header.split("sha256=")[-1]
    return hmac.compare_digest(expected, received)
```

**Anti-pattern**: checking the signature with `==` instead of `hmac.compare_digest`.
Timing attacks on string comparison can reveal signature bytes incrementally.

### Event Payload Design — Fat vs. Thin Events

| Style | Payload | Pros | Cons |
|-------|---------|------|------|
| Thin event | Event type + resource ID only | Small payload, consumer fetches current state | Extra API call per event, possible race condition (resource updated between event and fetch) |
| Fat event | Full resource state at event time | Self-contained, no callback needed | Large payload, state may be stale for delayed consumers |
| Delta event | Changed fields only | Efficient, explicit about what changed | Consumer must reconstruct full state |

**Default for enterprise webhooks**: fat events. Enterprise customers build
integrations that need the full resource state. The extra payload size is worth
the simplicity — consumers don't need API credentials to fetch the object.

```json
{
  "id": "evt_abc123",
  "type": "order.status_changed",
  "created_at": "2024-01-15T10:30:00Z",
  "data": {
    "order": {
      "id": "ord_456",
      "tenant_id": "t_789",
      "status": "fulfilled",
      "previous_status": "confirmed",   ← include delta context in fat event
      "items": [...],
      "updated_at": "2024-01-15T10:30:00Z"
    }
  }
}
```

### Webhook Management Requirements for Enterprise

Enterprise customers require a webhook management UI. Without it, they cannot
self-service integrations:

- **Endpoint registration**: URL, events to subscribe, active/inactive toggle
- **Secret management**: generate, rotate, view redacted current secret
- **Delivery log**: last N deliveries with timestamp, event type, HTTP status, response body
- **Retry controls**: manually retry failed deliveries
- **Test event**: send a sample payload to verify endpoint is receiving

This is not optional for enterprise tier. Every major enterprise SaaS platform
provides this.

---

## Event Streaming with Kafka

### Topic Design Principles

```
Topic naming convention: {environment}.{domain}.{entity}.{event_type}
  prod.orders.order.created
  prod.inventory.stock.updated
  prod.users.user.deactivated

Topic per event type: cleaner schemas, easier consumer filtering, more topics to manage
Topic per domain entity: fewer topics, mixed schemas, requires consumer-side filtering

Default choice: topic per event type for integration events
               topic per entity for internal event sourcing
```

### Partition Strategy

Partitions determine ordering and throughput scaling. Within a partition, messages
are strictly ordered.

```
Partition by tenant_id:
  → all events for a tenant are ordered and processed in sequence
  → prevents: order.created processed before order.submitted for same order
  → risk: hot partition if one tenant has extreme volume

Partition by entity_id (e.g., order_id):
  → all events for one order are ordered
  → better distribution across tenants
  → use when intra-entity ordering matters more than cross-entity tenant ordering

Hash-based partitioning:
  producer.send("events.orders", key=order_id.encode())
  → Kafka hashes key to partition — same key always → same partition
```

### Consumer Group Patterns

```
Competing consumers (one consumer group):
  All instances of "notification-service" share one group
  → each message delivered to exactly one instance
  → horizontal scaling: add more instances, work distributes

Multiple independent consumer groups:
  "notification-service" group + "audit-service" group
  → each group gets its own copy of every message
  → consumer groups are independent — one slow consumer doesn't block others
```

**Anti-pattern**: one consumer reading from a topic and republishing to multiple
queues. Instead, create multiple consumer groups. Each group reads independently
from Kafka's distributed log — no fan-out middleware needed.

### Schema Registry and Compatibility

```python
# Avro schema with schema registry (Confluent)
from confluent_kafka.avro import AvroProducer

schema_str = """
{
  "type": "record",
  "name": "OrderCreated",
  "namespace": "com.example.orders",
  "fields": [
    {"name": "order_id", "type": "string"},
    {"name": "tenant_id", "type": "string"},
    {"name": "created_at", "type": "string"},
    {"name": "items_count", "type": "int", "default": 0}  ← default required for BACKWARD compat
  ]
}
"""
# Schema registry enforces compatibility mode:
# BACKWARD: new schema can read old data (safe for producers to update)
# FORWARD: old schema can read new data (safe for consumers to update)
# FULL: both — most restrictive, recommended for long-lived schemas
```

Evolution rules for Avro:
- Adding a field with a default: BACKWARD compatible
- Removing a field with a default: FORWARD compatible
- Adding a field without a default: NOT compatible (breaking)
- Changing a field type: NOT compatible (breaking) — use a new field name

### Exactly-Once Semantics — When You Actually Need It

Kafka exactly-once involves idempotent producers + transactional APIs + consumer
offsets committed within the same transaction. It adds:
- ~20-30% throughput reduction
- Application complexity (transactional producer setup)
- Only works within Kafka-to-Kafka processing (not Kafka-to-database)

In practice: most enterprise SaaS workflows are better served by **at-least-once
delivery + idempotent consumers**. Design your consumers to handle duplicate
messages correctly, which is simpler and more portable than exactly-once semantics.

```python
# Idempotent consumer pattern
def process_order_created(event: dict):
    order_id = event["order_id"]
    # Check if already processed (use event ID as idempotency key)
    if ProcessedEvents.exists(event["id"]):
        return  # already processed, skip
    
    with transaction:
        create_fulfillment_record(order_id)
        ProcessedEvents.insert(event["id"])
```

---

## Message Queue Patterns

### Work Queue — Competing Consumers

```python
# SQS work queue: competing consumers for background job distribution
import boto3
sqs = boto3.client('sqs')

# Producer
sqs.send_message(
    QueueUrl=QUEUE_URL,
    MessageBody=json.dumps({ "job_type": "export", "tenant_id": tenant_id, "params": {...} }),
    MessageGroupId=tenant_id  # FIFO queue: maintain order per tenant
)

# Consumer
while True:
    response = sqs.receive_message(QueueUrl=QUEUE_URL, MaxNumberOfMessages=10,
                                   VisibilityTimeout=300)  # 5-minute processing window
    for message in response.get("Messages", []):
        try:
            job = json.loads(message["Body"])
            process_job(job)
            sqs.delete_message(QueueUrl=QUEUE_URL, ReceiptHandle=message["ReceiptHandle"])
        except Exception:
            # Don't delete — SQS will redeliver after visibility timeout expires
            log.error("Job failed", job_id=job["id"])
```

**Visibility timeout**: how long a message is "invisible" to other consumers
while being processed. Must be greater than your maximum processing time, with
headroom. If processing takes >5 minutes, set timeout to 10 minutes.

### Dead Letter Queues — Required, Not Optional

Configure a DLQ for every queue. After `maxReceiveCount` delivery attempts (typically 3-5),
failed messages move to the DLQ automatically.

```
DLQ responsibilities:
  1. Alert on DLQ depth > 0 (messages are failing and need investigation)
  2. Inspect failed messages (payload, exception logs)
  3. Fix the consumer bug
  4. Replay from DLQ (move messages back to main queue after fix)
```

Without a DLQ, failed messages either disappear (if you delete on failure) or
loop infinitely (if you never delete). Both are wrong.

### SNS + SQS Fan-Out

```
Architecture:
  SNS Topic: "order.events"
  → SQS Queue: "notifications-queue"     (notification service subscribes)
  → SQS Queue: "audit-queue"             (audit service subscribes)
  → SQS Queue: "search-index-queue"      (search indexer subscribes)

Benefits:
  - Publisher sends one message to SNS
  - SNS delivers independently to each subscriber queue
  - Each subscriber queue has its own DLQ, retry policy, and consumer
  - Adding a new subscriber doesn't require changes to the publisher
```

Use SNS+SQS fan-out over Kafka when: you're in AWS, the scale is moderate
(thousands not millions of events/day), and you want managed infrastructure
without Kafka operational overhead.

---

## API Gateway Patterns

### Backend for Frontend (BFF)

A BFF is a dedicated API layer per client type that aggregates backend service
calls and shapes the response for that client's needs.

```
Mobile BFF      → optimized for bandwidth-constrained clients, fewer fields
Web BFF         → full detail, supports dashboard aggregation patterns
Partner API     → public API surface, stable versioning, rate limited
Internal admin  → wide permissions, audit logged, different auth mechanism
```

```python
# Web BFF: aggregate order detail in one call instead of 5
@app.get("/api/web/orders/{order_id}")
async def get_order_detail(order_id: str, user: User = Depends(auth)):
    # Parallel calls to backend services
    order, line_items, shipments, audit_trail = await asyncio.gather(
        order_service.get(order_id),
        order_service.get_line_items(order_id),
        shipment_service.get_by_order(order_id),
        audit_service.get_recent(entity_type="order", entity_id=order_id, limit=10)
    )
    return { "order": order, "line_items": line_items,
             "shipments": shipments, "audit_trail": audit_trail }
```

The BFF pattern prevents N+1 patterns at the API level — the client makes one
request, the BFF handles the fan-out internally where network latency is lower.

---

## Data Contract Evolution

### Compatibility Rules

```
Additive change (always safe):
  New optional field in request body → old clients don't send it, new default applies
  New optional field in response → old clients ignore unknown fields (if they're written to)
  New endpoint → old clients don't call it

Breaking change (requires new version or deprecation):
  Removing a field from request or response
  Changing field type
  Making an optional field required
  Changing the meaning of a field value
  Changing status codes for existing scenarios
```

**The "must ignore unknown fields" requirement**: your clients should be written
to ignore fields they don't know about. Fail loudly on this in code reviews.
A client that breaks on unknown response fields will break every time you add
a new field to the response — it's a fragile client, not a strict API.

### Consumer-Driven Contract Testing (Pact)

Consumer-driven contracts prevent breaking changes from reaching production:

```
1. Consumer team defines pacts (interaction expectations):
   "When I call GET /orders/{id}, I expect a response with {id, status, items}"
   The pact does NOT include all fields — only the fields the consumer uses

2. Provider team runs consumer pacts in their test suite:
   The provider's test verifies it can satisfy every consumer pact
   Pact broker stores and versions pacts, CI enforces "can I deploy?" checks

3. Contract verified: provider knows it hasn't broken the consumer
   Consumer can deploy knowing the provider still satisfies their expectations
```

Pact is especially valuable in microservices where teams deploy independently
and integration tests between services are slow or brittle.

---

## iPaaS for Enterprise SaaS

### When iPaaS Support Is Required

Enterprise customers need integrations your team will never build natively
(HR systems, ERPs, PDMs, custom internal tools). iPaaS platforms let customers
build those integrations themselves.

| Platform | Customer Tier | Integration Pattern | When to Prioritize |
|----------|--------------|--------------------|--------------------|
| Zapier | SMB, mid-market | Polling (every 15 min), simple triggers/actions | Broad market reach |
| Make (Integromat) | SMB, mid-market | Polling + webhooks, more complex flows | SMB users needing richer logic |
| Workato | Enterprise | Real-time, complex transformations, enterprise connectors | Enterprise deals >$50k ARR |
| MuleSoft | Large enterprise | Full integration platform, custom mappings | Fortune 500, IT-managed integrations |
| Boomi | Large enterprise | Similar to MuleSoft | SAP ecosystem customers |

### What Your Platform Must Provide for iPaaS to Work

iPaaS platforms build connectors on top of your public API. Without these,
your connector will be unusable:

| Requirement | Why It's Required |
|-------------|-----------------|
| OAuth 2.0 support | iPaaS needs to authenticate on behalf of the customer's account |
| Stable public REST API | Connector breaks if you rename fields or remove endpoints |
| Webhook support | Real-time triggers require webhooks; polling is 15-min delay |
| Paginated list endpoints | Connectors need to enumerate all records |
| Filter/search parameters | Useful triggers need to filter by date, status, tenant |
| Webhook event catalog | Documentation of all event types with example payloads |

The order matters: OAuth 2.0 first, then stable REST endpoints with pagination,
then webhooks for real-time. Without OAuth 2.0, customers must use API keys,
which iPaaS platforms support but it's a worse enterprise experience.

---

## Cross-Spoke Routing

| Topic | Route To |
|-------|----------|
| REST/GraphQL API design | `be-api-design` |
| Saga pattern, CQRS, event sourcing | `be-service-architecture` |
| Kafka topics as analytics pipeline sources | `ds-data-engineering` |
| Event instrumentation for experiment tracking | `ds-experimentation` |
| Event instrumentation for product metrics | `ds-product-analytics` |
| Platform integration strategy (roadmap) | `pm-platform-api` |
| Event-driven metrics requirements | `pm-metrics-analytics` |
