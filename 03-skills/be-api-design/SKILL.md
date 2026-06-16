---
name: be-api-design
description: >
  REST API design, GraphQL schema design, gRPC/Protobuf for internal services,
  API versioning, pagination patterns, rate limiting, and OpenAPI documentation
  standards for enterprise B2B SaaS. Use this skill whenever the conversation
  touches: REST resource modeling, HTTP semantics and status codes, request and
  response envelope design, HATEOAS tradeoffs, GraphQL type system, DataLoader
  and N+1 in GraphQL, query complexity limits, schema-first vs. code-first
  GraphQL, gRPC streaming patterns, Protobuf field numbering and backwards
  compatibility, API versioning strategies (URL vs. header, breaking vs.
  additive changes, deprecation windows), pagination (offset vs. cursor vs.
  keyset), rate limiting algorithms (token bucket, leaky bucket), OpenAPI 3.x
  documentation and schema-first generation, Sunset headers (RFC 8594), or any
  question about the right API contract shape for a feature. Not for:
  authentication and authorization in APIs (be-auth-patterns), backend service
  decomposition (be-service-architecture), or ML prediction endpoint design
  (ds-ml-engineering, though cross-referenced here).
aliases: [be-api-design]
tier: spoke
domain: engineering
hub: lead-backend-engineer
prerequisites: [lead-backend-engineer]
spec_version: "2.0"
---

# Be: API Design

Specialist lens for API contract design, protocol selection, versioning strategy,
and documentation standards for enterprise SaaS. Part of the backend engineering
skill network.

---

## Domain Boundary

This skill owns: **API contract design, protocol selection, versioning,
pagination, rate limiting, and documentation standards**.

- Authentication and authorization in APIs → `be-auth-patterns`
- Service-to-service architecture decisions → `be-service-architecture`
- ML prediction API versioning and stability → `ds-ml-engineering`
- Platform API strategy and product decisions → `pm-platform-api`

---

## REST API Design

### Resource Modeling

Resources are nouns, not verbs. The HTTP method carries the verb.

```
# Correct
POST   /orders              # create
GET    /orders/{id}         # read
PATCH  /orders/{id}         # partial update
DELETE /orders/{id}         # delete
POST   /orders/{id}/submit  # action verb as sub-resource (necessary for non-CRUD)

# Wrong
POST /createOrder
GET  /getOrderById
POST /submitOrder
```

**Nested resources**: use nesting when the child has no identity outside the
parent (strong ownership).

```
GET /customers/{id}/addresses     # address belongs to one customer
GET /orders/{id}/line-items       # line items belong to one order
```

**Flat resources**: when the relationship is many-to-many or the resource has
independent identity across the system.

```
GET /products?category_id=123     # products exist independently of categories
GET /users/{id}/roles             # roles are independent, but membership is user-scoped
```

### HTTP Semantics

| Method | Safe | Idempotent | Use For |
|--------|------|-----------|---------|
| GET | Yes | Yes | Read, no side effects |
| HEAD | Yes | Yes | Check existence/metadata |
| OPTIONS | Yes | Yes | CORS preflight |
| PUT | No | Yes | Replace entire resource |
| PATCH | No | No* | Partial update |
| POST | No | No | Create, non-idempotent actions |
| DELETE | No | Yes | Delete (204 on success, 404 or 204 if already gone) |

*PATCH can be made idempotent with conditional requests (`If-Match`), but it's not
required to be. Document whether your PATCH is idempotent.

### Status Codes That Are Commonly Misused

```
200 OK           — read succeeded, or update succeeded with body returned
201 Created      — resource created, include Location: header with new resource URL
204 No Content   — action succeeded, no body (DELETE, PUT/PATCH with no response body)

400 Bad Request  — malformed request syntax, invalid JSON
422 Unprocessable Entity — valid syntax, but semantic validation failed
                           (field required, value out of range, business rule violation)
                           422 > 400 for validation errors — the distinction matters for clients

401 Unauthorized — not authenticated (confusing name, but it means auth required)
403 Forbidden    — authenticated but not authorized
404 Not Found    — resource doesn't exist, OR you're hiding existence for security
410 Gone         — resource existed and was permanently deleted (use for explicitly-deleted resources)
409 Conflict     — optimistic concurrency failure, duplicate creation, state conflict
429 Too Many Requests — rate limited, always include Retry-After header
503 Service Unavailable — downstream dependency unavailable, include Retry-After if known
```

Never return 200 with an error body. Pick the right status code.

### Request/Response Envelope Design

Choose a convention and enforce it across the entire API. Mixing envelope styles
in the same API is a maintenance debt that grows forever.

```json
// Option A: JSON:API style — verbose but machine-readable
{
  "data": { "type": "order", "id": "123", "attributes": { ... } },
  "meta": { "total": 100, "page": 1 },
  "errors": [{ "code": "VALIDATION_ERROR", "detail": "...", "source": { "pointer": "/data/attributes/email" } }]
}

// Option B: Simpler envelope (most enterprise APIs use this)
{
  "data": { "id": "123", "status": "active", ... },
  "meta": { "request_id": "abc123", "timestamp": "2024-01-01T00:00:00Z" }
}

// Error response — always consistent, always machine-readable
{
  "error": {
    "code": "VALIDATION_ERROR",        // stable machine-readable code
    "message": "Human-readable text",  // may change, don't key on this
    "details": [
      { "field": "email", "message": "is required" }
    ],
    "request_id": "abc123"             // correlate to logs
  }
}
```

`request_id` on every response (including errors) is non-negotiable in
enterprise SaaS — it's how support teams debug customer issues.

### HATEOAS

HATEOAS (Hypermedia as the Engine of Application State) embeds links to related
resources in responses. Valuable for: discovery-driven generic clients, API
explorers, HAL browsers.

In practice for enterprise SaaS: the clients are purpose-built and know the URL
structure. HATEOAS adds response size and implementation complexity without
benefit. Skip it unless you're building a public hypermedia API.

---

## GraphQL Schema Design

### Type System Decisions

```graphql
# Use interfaces when multiple types share a contract
interface Node {
  id: ID!
}

# Use unions when types have no shared fields but can appear in the same position
union SearchResult = Product | Order | Customer

# Use scalars for domain-specific types (validate at boundary)
scalar DateTime   # ISO 8601, validated on parse
scalar UUID       # validated UUID format
scalar Money      # cents as integer, or BigDecimal string
```

**Nullable vs. non-null**: err on the side of non-null for fields that will
always be present. Nullable fields force clients to handle null in every field
access. But: making a field non-null is a breaking change if you later need to
return null — be deliberate.

### DataLoader — Required, Not Optional

Every field resolver that touches a database must go through DataLoader or an
equivalent batching mechanism.

```javascript
// Without DataLoader: N+1 — 1 query per order.customer field
orders.map(order => db.query('SELECT * FROM customers WHERE id = ?', order.customerId))

// With DataLoader: 1 query for all customers needed in this request
const customerLoader = new DataLoader(async (ids) => {
  const customers = await db.query('SELECT * FROM customers WHERE id = ANY(?)', [ids]);
  return ids.map(id => customers.find(c => c.id === id));
});

// In resolver:
resolve: (order) => customerLoader.load(order.customerId)
```

DataLoader batches within a single request tick. It also memoizes within the
request — the same ID is only fetched once.

### Query Complexity and Depth Limits

Unbounded GraphQL queries are a DoS vector. Required for any production GraphQL API:

```javascript
// Depth limit: prevent deeply nested queries
const depthLimit = require('graphql-depth-limit');
const validationRules = [depthLimit(7)];  // tune to your schema

// Complexity limit: assign cost scores to fields
const { createComplexityLimitRule } = require('graphql-validation-complexity');
const complexityRule = createComplexityLimitRule(1000, {
  onCost: (cost) => console.log('Query cost:', cost),
  scalarCost: 1,
  objectCost: 10,
  listFactor: 10,  // lists multiply cost by this factor
});
```

Reject queries that exceed the limit at validation time, before execution.

### Schema-First vs. Code-First

| Approach | Pros | Cons |
|----------|------|------|
| Schema-first (SDL) | Schema is the source of truth, language-agnostic, easy to review in PRs | Implementation drift, resolver types not auto-generated (use codegen) |
| Code-first (decorators/builders) | Type safety from the start, schema generated from code | Schema as implementation artifact, harder to review API surface |

For enterprise SaaS: **schema-first** if your API is customer-facing or if
multiple teams consume it. The SDL file becomes the contract, reviewable in PRs
without understanding the implementation. Use GraphQL Code Generator to produce
TypeScript types from the schema.

---

## gRPC and Protobuf for Internal Services

### When gRPC Over REST

Use gRPC for internal service-to-service communication when:
- Streaming is needed (server push, bidirectional)
- You need strongly-typed contracts and don't want to maintain OpenAPI for internal APIs
- The performance difference matters (binary serialization, HTTP/2 multiplexing)

Use REST for internal services when: the service may be called by third-party
clients, the team isn't familiar with gRPC tooling, or simplicity of curl-testing
matters.

### Protobuf Field Numbering — Backwards Compatibility

```protobuf
message Order {
  string id = 1;           // field numbers are permanent — never reuse
  string tenant_id = 2;
  OrderStatus status = 3;
  // string old_field = 4;  // DO NOT reuse 4 after removing old_field
                            // Use reserved to prevent accidental reuse
  reserved 4;
  reserved "old_field";
  
  // Adding new fields: always optional, new number
  string reference_number = 5;  // backwards compatible — old clients ignore
}
```

**Backwards compatibility rules**:
- Adding optional fields: backwards compatible
- Removing fields: mark as `reserved`, never reuse the number
- Changing field type: breaking change — never do this in a live service
- Renaming fields: compatible at wire level (Protobuf ignores names), breaking for JSON mapping

### Streaming Patterns

```
Server-side streaming:  client sends one request, server sends many responses
                        (real-time updates, large result sets, export)
Client-side streaming:  client sends many requests, server sends one response
                        (bulk upload, log ingestion)
Bidirectional:          both sides stream independently
                        (chat, real-time collaboration, live dashboards)
```

For most "real-time" enterprise SaaS features: SSE (Server-Sent Events) over REST
is simpler than gRPC streaming and sufficient for server→client push. Reserve
gRPC streaming for high-throughput internal data pipelines.

---

## API Versioning

### Strategy Comparison

| Strategy | URL Shape | Enterprise Suitability | Notes |
|----------|-----------|----------------------|-------|
| URL path (`/v1/`, `/v2/`) | `api.example.com/v1/orders` | High — visible, simple to test with curl | URL pollution, but negligible in practice |
| Subdomain (`v1.api.example.com`) | — | Medium — DNS management overhead | Uncommon for most APIs |
| Header (`Accept: application/vnd.api+json;version=2`) | Clean URLs | Medium — hard to test manually | Common in large platforms (GitHub) |
| Query param (`?version=2`) | `api.example.com/orders?version=2` | Low — pollutes query params, cacheable problems | Use only for gradual client migration |

**Default**: URL path versioning. Simple, visible, works with every HTTP client,
no ambiguity in logs.

### Breaking vs. Additive Changes

**Non-breaking (additive-only) — do not require a version bump**:
- New optional request fields
- New response fields
- New endpoints
- New values in enums (clients should use default/unknown handling)
- New optional headers

**Breaking — require a new version**:
- Removing or renaming fields
- Changing field types
- Changing semantics of existing fields
- Required fields that weren't required before
- Removing endpoints
- Changing pagination mechanism

### Deprecation Windows

Enterprise SaaS minimum: **12 months deprecation notice** before removing a
version. Many enterprise customers have procurement cycles, change freezes, and
internal approval processes — they cannot move faster than their process allows.

```http
# RFC 8594 Sunset header — signals when the endpoint will be removed
HTTP/1.1 200 OK
Deprecation: Sat, 01 Jan 2025 00:00:00 GMT
Sunset: Mon, 01 Jan 2026 00:00:00 GMT
Link: <https://api.example.com/v2/orders>; rel="successor-version"
```

Add `Deprecation` and `Sunset` headers to every response from deprecated endpoints.
Log which tenants are still calling deprecated endpoints — you'll need this data
to drive the migration.

---

## Pagination

### Pattern Comparison

| Pattern | Consistency Under Mutations | DB Cost | Jump to Arbitrary Page | Use When |
|---------|---------------------------|---------|----------------------|----------|
| Offset | Poor — inserts shift pages | O(offset) row scan | Yes | Simple admin UIs, small datasets |
| Cursor | Good — consistent per cursor position | O(1) from cursor | No | Large datasets, real-time feeds |
| Keyset | Good | O(1) | No (by design) | Maximum efficiency, sortable unique key available |

**Cursor pagination** (preferred for large datasets):
```json
// Response
{
  "data": [...],
  "pagination": {
    "next_cursor": "eyJpZCI6MTIzfQ==",  // opaque, base64-encoded position
    "has_more": true
  }
}
// Next request: GET /orders?cursor=eyJpZCI6MTIzfQ==&limit=20
```

The cursor encodes enough state to resume from the exact position — typically
the sort key and tie-breaking ID of the last returned record.

**Keyset pagination** (maximum efficiency):
```sql
-- First page
SELECT * FROM orders WHERE tenant_id = ?
ORDER BY created_at DESC, id DESC LIMIT 20;

-- Next page: use last row's values as the cursor
SELECT * FROM orders WHERE tenant_id = ?
  AND (created_at, id) < ('2024-01-15 10:30:00', 456)  -- row tuple comparison
ORDER BY created_at DESC, id DESC LIMIT 20;
```

---

## Rate Limiting

### Algorithm Selection

**Token bucket**: refills at a fixed rate, allows bursts up to bucket size.
Best for: APIs where short bursts are acceptable, normal usage pattern.

**Leaky bucket (fixed window)**: requests drain at a fixed rate. Best for:
strict rate enforcement, preventing any burst. Less forgiving.

**Sliding window**: more accurate than fixed window, prevents "boundary burst"
problem. Best for: public APIs where fairness matters.

### Rate Limit Dimensions

Rate limit at multiple dimensions for enterprise SaaS:

- **Per API key / per user**: protect against runaway clients
- **Per tenant / per account**: prevent one large tenant from starving others
- **Per endpoint**: expensive endpoints (bulk export, search) need tighter limits

```http
# Required headers on 429 response
HTTP/1.1 429 Too Many Requests
Retry-After: 60
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1704067200  # Unix timestamp when the window resets
```

Never return 429 without `Retry-After`. Clients that don't know when to retry
will hammer the rate limiter, making the problem worse.

---

## OpenAPI 3.x Documentation

Schema-first API documentation for enterprise SaaS is not optional — enterprise
buyers evaluate API documentation quality as part of procurement.

```yaml
# Minimum required per endpoint
paths:
  /orders:
    post:
      summary: Create an order
      operationId: createOrder          # stable identifier for SDK generation
      tags: [Orders]
      security: [{ BearerAuth: [] }]
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CreateOrderRequest'
            examples:
              basic:
                summary: Minimal order
                value: { "tenant_id": "t_123", "items": [...] }
      responses:
        '201':
          description: Order created
          headers:
            Location:
              schema: { type: string }
              description: URL of the created order
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Order'
        '422':
          $ref: '#/components/responses/ValidationError'
        '429':
          $ref: '#/components/responses/RateLimited'
```

Generate server stubs and client SDKs from the spec — don't maintain them
separately. The spec is the source of truth.

---

## Cross-Spoke Routing

| Topic | Route To |
|-------|----------|
| API authentication, OAuth flows, JWT | `be-auth-patterns` |
| Service decomposition, BFF pattern | `be-service-architecture` |
| ML prediction endpoints | `ds-ml-engineering` |
| LLM streaming API integration | `ds-nlp-llm` |
| API product strategy | `pm-platform-api` |

## Related
- hub → [[lead-backend-engineer]]
