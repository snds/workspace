---
name: lead-backend-engineer
description: >
  Staff/principal backend engineering for enterprise B2B SaaS. Hub skill for
  a network of 7 specialist spokes covering relational databases, API design,
  service architecture, authentication/authorization, caching and performance,
  integration patterns, and data modeling. Use this skill whenever the
  conversation touches: backend engineering, API design, database schema,
  relational database, PostgreSQL, MySQL, service architecture, microservices,
  monolith decomposition, bounded contexts, authentication, authorization,
  RBAC, ABAC, OAuth 2.0, OIDC, SAML, SCIM, enterprise SSO, caching, Redis,
  performance optimization, integration patterns, webhooks, event streaming,
  Kafka, message queues, schema design, data modeling, ORM, query optimization,
  migrations, REST API, GraphQL, gRPC, multi-tenancy, audit trails, SLO design,
  or any backend engineering concern in a production enterprise SaaS context.
  Also trigger on: "how should I model this", "what's the right API shape",
  "database design", "how do I handle multi-tenancy", "what auth flow",
  "cache invalidation", "zero-downtime migration", "event-driven", or any
  question about making a backend system correct, fast, and maintainable at scale.
aliases: [lead-backend-engineer]
tier: hub
domain: engineering
spec_version: "2.0"
prerequisites: [eng-foundations]
---

# Lead Backend Engineer

**Hub skill** for the enterprise SaaS backend engineering network. Routes to 7
specialist spoke skills based on domain. This skill provides the core principles
and operating directive; spokes provide domain-specific depth.

---

## Spoke Network — Load On-Demand

**Do not load all spokes eagerly.** Load only the 1–2 spokes directly relevant
to the current question. The hub contains enough context to triage and route.

### Spoke Manifest

| Skill | Domain | Trigger When |
|-------|--------|-------------|
| `be-relational-db` | Relational database design, normalization, indexing, query optimization, transactions, migrations | Schema design, index strategy, query performance, transaction isolation, zero-downtime migrations, partitioning |
| `be-api-design` | REST, GraphQL, gRPC, versioning, pagination, rate limiting, OpenAPI documentation | Designing or reviewing API contracts, pagination strategy, versioning policy, API documentation, GraphQL schema design |
| `be-service-architecture` | Monolith vs. microservices, bounded contexts, event-driven architecture, distributed systems patterns | Service decomposition, saga pattern, circuit breakers, twelve-factor, observability architecture, strangler fig |
| `be-auth-patterns` | OAuth 2.0, OIDC, JWT, RBAC/ABAC/ReBAC, SAML, SCIM, enterprise SSO, API security, audit logging | Auth flows, token design, enterprise SSO integration, SCIM provisioning, permission modeling, API key management |
| `be-caching-performance` | Cache invalidation, Redis patterns, connection pooling, CDN, SLO/SLA design | Cache strategy, Redis data structures, thundering herd, read replica routing, latency SLOs, performance investigation |
| `be-integration-patterns` | Webhooks, Kafka, message queues, API gateway, data contracts, iPaaS | Outbound webhook design, Kafka topic design, message queue patterns, BFF pattern, consumer-driven contract testing |
| `be-data-modeling` | Application-layer entity modeling, OLTP schema, multi-tenancy, temporal data, audit trails | Domain entity design, aggregate roots, multi-tenancy strategy, soft deletes, JSONB vs. relational columns, temporal data |
| `be-security-posture` | Threat modeling (STRIDE/PASTA), OWASP Top 10 for SaaS APIs, secrets management, supply chain security, security headers, SOC 2 engineering requirements | Threat model for a new feature, OWASP vulnerability remediation, secrets rotation, CSP policy, SBOM, supply chain scanning, SOC 2 audit prep |

### Spoke Loading Protocol

**Step 1**: Match the user's question to the Spoke Manifest. Identify the 1–2
spokes directly relevant. Hub-level principles are sufficient for general
questions — load a spoke only when domain-specific depth is needed.

Common routing patterns:

- **Schema or data model design**: `be-data-modeling` (entity modeling, multi-tenancy, temporal) + `be-relational-db` (index strategy, normalization)
- **API shape or contract design**: `be-api-design`
- **Auth/SSO/permissions question**: `be-auth-patterns`
- **Cache strategy or Redis pattern**: `be-caching-performance`
- **Webhook, Kafka, or integration design**: `be-integration-patterns`
- **Microservices, service decomposition, distributed systems**: `be-service-architecture`
- **Zero-downtime migration**: `be-relational-db` (migration strategies section)
- **Performance investigation**: `be-caching-performance` + `be-relational-db` (query optimization)
- **Enterprise SSO, SCIM, audit logs**: `be-auth-patterns`
- **Event-driven architecture or sagas**: `be-service-architecture` + `be-integration-patterns`

**Step 2**: Load the spoke from:
```
[workspace root]/03-skills/[skill-name]/SKILL.md
```

**Step 3**: If the conversation shifts to a different spoke's domain mid-session,
load that spoke then — not preemptively.

**Never load all 7 spokes at once.**

---

## Core Principles

These apply across all backend engineering work. Spokes inherit them without
repeating them.

### 1. Correctness Before Performance

A fast wrong answer is worse than a slow right one. Optimize for correctness
first: correct transaction semantics, correct data isolation, correct auth
enforcement. Performance problems are measurable and fixable. Silent data
corruption, incorrect access control decisions, and race conditions are not.

The corollary: premature optimization at the cost of correctness or clarity is
the most expensive engineering decision you can make.

### 2. Explicit Over Implicit

In schema: explicit foreign keys, explicit NOT NULL constraints, explicit
check constraints. In API contracts: explicit status codes, explicit error
envelopes, explicit versioning. In service boundaries: explicit interfaces,
explicit ownership of data, explicit failure modes.

Implicit behavior that works in dev becomes a production incident at 2am.
Name the thing. Enforce the constraint. Document the contract.

### 3. The Enterprise SaaS Contract

Every engineering decision must hold up against these non-negotiable requirements:

- **Multi-tenancy at every layer**: Data isolation is not optional. Every query,
  every cache key, every event, every log entry must be scoped to a tenant.
  A tenant data leak is a P0 incident and an enterprise contract violation.
- **Audit trails by default**: Enterprise customers expect to know who did what,
  when, from where. Design audit logging in from the start — retrofitting it
  is expensive and error-prone.
- **Uptime SLAs**: 99.9% = 8.7 hours/year downtime budget. Every architectural
  decision either spends or saves from that budget.
- **Security posture**: SOC 2 Type II is the floor for enterprise B2B. SSO, SCIM,
  RBAC, encryption at rest and in transit, and audit logs are table stakes, not
  differentiators.

### 4. The Reversibility Principle

Prefer reversible decisions at every level:

- **Migrations**: additive first (add column), deploy, then remove old column.
  Never drop a column in the same migration that adds its replacement.
- **API contracts**: deprecate before removing. 12-month minimum deprecation
  windows for enterprise APIs.
- **Service boundaries**: a premature service split is much harder to undo than
  a well-structured module in a monolith. Decompose when you're certain, not
  when you're guessing.
- **Schema decisions**: adding a column is cheap; removing one after it's been
  read by clients for two years is expensive. Get the model right before
  writing code against it.

### 5. Observability is Not Optional

If you can't measure it, you can't debug it in production. Every service boundary
needs structured logging, metrics, and distributed traces. These are not "nice to
haves" to add after the system is working — they are how you determine that the
system is working.

Minimum bar: structured JSON logs with trace IDs, P50/P95/P99 latency metrics per
endpoint, error rate dashboards, alerting on SLO breach.

### 6. Failure Modes Must Be Designed, Not Discovered

Every external dependency will fail. Every third-party API will time out. Every
database will have a slow query spike. The question is not whether, but when.

For every integration point: what does this service do when the dependency is
unavailable? Degrade gracefully? Return stale data? Queue and retry? Fail fast
with a clear error? The answer must be in the code before the system ships,
not discovered in a postmortem.

---

## Enterprise SaaS Operating Directive

This skill network operates in the context of enterprise B2B SaaS at production
scale with enterprise customers. That context changes the calculus on several
common engineering decisions:

### Compliance Requirements Change the Default

SOC 2 Type II, GDPR, HIPAA, and ISO 27001 requirements are not add-ons — they
shape the architecture:

- Audit logging must be immutable and exportable (append-only, separate storage,
  defined retention periods)
- Encryption key management must support customer-managed keys (BYOK) for
  enterprise tiers
- Data residency requirements affect where and how tenant data is stored
- SCIM provisioning is required, not optional, for enterprise accounts

When working in a regulated domain (healthcare, finance, government), load
`be-auth-patterns` — compliance requirements are most concentrated there.

### Multi-Tenancy Is a Cross-Cutting Concern

Multi-tenancy touches every layer of the stack. The strategy chosen (shared schema,
separate schema, database per tenant, or hybrid) must be consistent across:

- Database queries (row-level security or application-layer filtering)
- Cache keys (tenant-scoped to prevent cross-tenant data leakage)
- Event payloads (tenant_id on every event)
- API authentication (token must carry tenant context)
- Background jobs (tenant context must survive queue serialization)

A decision made inconsistently at one layer will eventually produce a tenant
data leak. Load `be-data-modeling` for the strategy decision; `be-auth-patterns`
for enforcement at the auth layer; `be-caching-performance` for cache key design.

### Scale Is Not the Primary Concern — Correctness Is

Enterprise SaaS at 500 customers rarely needs Google-scale infrastructure. The
actual challenges are:
- Complex relational data models with intricate business rules
- Long-running business transactions that span multiple services
- Strict audit and compliance requirements
- High-stakes correctness requirements (wrong data in a PLM system is a
  production line stoppage, not a UX glitch)
- Zero-downtime deployments with live enterprise traffic

Optimize for correctness, reliability, and maintainability first. Premature
scaling is a distraction from the real work.

---

## Cross-Hub References

### Backend → Data Science

| When this topic comes up | Route to |
|--------------------------|----------|
| OLTP schema as analytics data source | `ds-product-analytics`, `ds-data-engineering` |
| ML model serving architecture | `ds-ml-engineering` |
| Prediction caching | `ds-ml-engineering`, `ds-nlp-llm` |
| LLM API integration patterns | `ds-nlp-llm` |
| Event instrumentation for experiments | `ds-experimentation` |
| Kafka topics as pipeline sources | `ds-data-engineering` |

### Backend → Product Management

| When this topic comes up | Route to |
|--------------------------|----------|
| API product strategy and surface design | `pm-platform-api` |
| Enterprise SSO/SCIM as GTM requirement | `pm-enterprise-gtm` |
| Event instrumentation for metrics | `pm-metrics-analytics` |
| Integration ecosystem and iPaaS strategy | `pm-platform-api` |

## Related
- foundation → [[eng-foundations]]
- spoke → [[be-api-design]] · [[be-auth-patterns]] · [[be-caching-performance]] · [[be-data-modeling]] · [[be-integration-patterns]] · [[be-relational-db]] · [[be-security-posture]] · [[be-service-architecture]]
