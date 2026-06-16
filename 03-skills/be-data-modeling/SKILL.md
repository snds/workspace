---
name: be-data-modeling
description: >
  Application-layer entity modeling, OLTP schema design for enterprise SaaS,
  multi-tenancy strategy, temporal data modeling, soft deletes, audit column
  patterns, and audit trail architecture. Use this skill whenever the
  conversation touches: aggregate root pattern, value objects vs. entities,
  ubiquitous language, OLTP schema design, multi-tenancy approaches (shared
  schema vs. separate schema vs. database per tenant vs. hybrid), soft deletes
  (deleted_at vs. boolean vs. archive table), surrogate keys (UUID v4 vs. v7
  vs. BIGSERIAL), polymorphic associations (STI, CTI, polymorphic FK, concrete
  table inheritance), JSONB vs. relational columns decision, valid time vs.
  transaction time vs. bitemporal modeling, temporal tables, audit log schema
  design (append-only, trigger-based vs. application-layer), compliance audit
  requirements, or any question about how to model domain entities and their
  relationships in the database. Not for: query optimization and index design
  on an existing schema (be-relational-db), authentication data models
  (be-auth-patterns), or analytical/warehouse schema (ds-data-engineering).
aliases: [be-data-modeling]
tier: spoke
domain: engineering
hub: lead-backend-engineer
prerequisites: [lead-backend-engineer]
spec_version: "2.0"
---

# Be: Data Modeling

Specialist lens for application-layer entity design, OLTP schema patterns,
and data modeling for enterprise SaaS compliance and multi-tenancy requirements.
Part of the backend engineering skill network.

---

## Domain Boundary

This skill owns: **domain entity design, OLTP schema patterns, multi-tenancy
strategy, temporal data, and audit trail architecture**.

- Index design, query optimization on the schema → `be-relational-db`
- Authentication-related data models (users, tokens, API keys) → `be-auth-patterns`
- Warehouse/analytical schema design → `ds-data-engineering`
- Cache key design for multi-tenant data → `be-caching-performance`

---

## Domain-Driven Entity Modeling

### Aggregate Root Pattern

An aggregate root is the entry point to a cluster of related domain objects.
All interactions with the cluster go through the root. The root enforces the
invariants that must hold across the entire cluster.

```
Order aggregate:
  Aggregate root: Order
  Contained: LineItem (no meaningful existence without Order)
             ShippingAddress (embedded in Order)
  Invariants enforced by root:
    - Total price = sum of line item prices
    - Cannot submit an order with no items
    - Cannot add items to a submitted order

Product aggregate:
  Aggregate root: Product
  Contained: ProductVariant, PricingRule
  NOT contained: Order (separate aggregate, referenced by ID only)
```

**Aggregate boundaries in the database**:
- Entities within an aggregate share a transaction boundary
- Cross-aggregate references use foreign keys (IDs), not joins
- Never load one aggregate to update another — each aggregate has its own
  repository/service

```sql
-- Correct: line_items reference order by ID (within same aggregate)
line_items (id, order_id, product_id, quantity, unit_price, ...)
-- order_id FK is fine — line_item is owned by order

-- Correct: order references product by ID (cross-aggregate reference)
order_items (id, order_id, product_id, ...)
-- product_id FK is fine — read-only reference, no cross-aggregate mutation
```

### Value Objects vs. Entities

| | Entity | Value Object |
|--|--------|-------------|
| Identity | Has a unique ID | Identified by its values |
| Equality | Two orders with same ID are the same order | Two addresses with same fields are the same address |
| Mutability | Mutable — entity changes over time | Immutable — replace, don't modify |
| Storage | Own table with primary key | Embedded columns or separate table without meaningful PK |

```sql
-- Entity: has its own identity, exists independently
CREATE TABLE orders (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL,
  status TEXT NOT NULL,
  ...
);

-- Value object: embedded columns, no meaningful own ID
-- Shipping address is a value object — it's meaningful as a whole, not by ID
CREATE TABLE orders (
  ...
  ship_to_name TEXT,
  ship_to_street TEXT,
  ship_to_city TEXT,
  ship_to_postal_code TEXT,
  ship_to_country_code CHAR(2)
  -- if address reuse matters, extract to a table and reference by FK
);
```

### Ubiquitous Language

Model names, field names, and enum values must reflect the domain language
as used by domain experts — not the implementation, not technical jargon.

```sql
-- Wrong: technical/generic names
status SMALLINT NOT NULL  -- what do 0, 1, 2, 3 mean?
type VARCHAR(50)          -- type of what?
is_deleted BOOLEAN        -- which layer handles this?

-- Correct: domain language
status TEXT NOT NULL CHECK (status IN ('draft', 'submitted', 'under_review', 'approved', 'rejected'))
document_type TEXT NOT NULL CHECK (document_type IN ('specification', 'drawing', 'bill_of_materials'))
-- soft delete → see soft delete section below, not is_deleted
```

The ubiquitous language should be consistent from the database schema through
the domain model to the API and UI. If sales calls it a "quote" and engineering
calls it an "order_draft," that's a domain boundary problem.

---

## OLTP Schema Design for Enterprise SaaS

### Multi-Tenancy Approaches

| Strategy | Isolation | Operational Complexity | Cost | Use When |
|----------|-----------|----------------------|------|---------|
| Shared schema (row-level) | Application-enforced | Low | Lowest | Most tenants; default starting point |
| Separate schema per tenant | Good | Medium (migration per tenant) | Medium | Regulated tenants, enterprise tier |
| Database per tenant | Maximum | High (one DB per tenant) | Highest | HIPAA/FedRAMP, strict data residency |
| Hybrid | Variable | Medium-High | Variable | Most large SaaS platforms |

**Shared schema with row-level security (PostgreSQL)**:
```sql
-- Enable RLS on every tenant-scoped table
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation ON orders
  USING (tenant_id = current_setting('app.tenant_id')::uuid);

-- Set at connection/request time
SET LOCAL app.tenant_id = 'f47ac10b-58cc-4372-a567-0e02b2c3d479';
-- All subsequent queries on this connection automatically filter by tenant_id
```

RLS is defense-in-depth. Application code should also enforce tenant_id in every
query — never rely on RLS alone, but use it as a safety net that prevents
cross-tenant queries even if application code is wrong.

**The hybrid model** (most mature SaaS platforms eventually reach this):
```
Tier            | Strategy
----------------|------------------
Standard/Growth | Shared schema, row-level isolation
Enterprise      | Separate schema per tenant
Enterprise+     | Dedicated database for highest-tier or regulated customers
```

### Soft Deletes

Three approaches with different query implications:

```sql
-- Option A: deleted_at timestamp (most flexible)
ALTER TABLE products ADD COLUMN deleted_at TIMESTAMPTZ;
-- Active records: WHERE deleted_at IS NULL
-- Deleted at time: WHERE deleted_at IS NOT NULL
-- Deleted before date: WHERE deleted_at < '2024-01-01'
-- Supports: partial index on deleted_at IS NULL for efficient active queries
CREATE INDEX idx_products_active ON products (tenant_id, id) WHERE deleted_at IS NULL;

-- Option B: boolean (simple, loses temporal information)
ALTER TABLE products ADD COLUMN deleted BOOLEAN NOT NULL DEFAULT FALSE;
-- Same partial index pattern
-- Loses: when was it deleted?

-- Option C: archive table (cleanest active queries, complex archaeology)
CREATE TABLE products_archived AS SELECT * FROM products WHERE FALSE;  -- same schema
-- Move rows: INSERT INTO products_archived SELECT * FROM products WHERE id = ?
--            DELETE FROM products WHERE id = ?
-- Active queries: no filter needed — archived rows are physically removed
-- Historical: JOIN products_archived when needed
```

**Default recommendation**: `deleted_at TIMESTAMPTZ` + partial index on active records.
It's reversible (set `deleted_at = NULL` to restore), supports temporal queries,
and keeps data for audit requirements. The partial index keeps active-record queries
efficient.

### Audit Columns — Mandatory on Every Mutable Table

```sql
-- Minimum audit columns on every table that can be changed
CREATE TABLE products (
  id          UUID NOT NULL DEFAULT gen_random_uuid(),
  tenant_id   UUID NOT NULL,
  
  -- domain columns ...
  
  created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  created_by  UUID REFERENCES users(id),   -- NULL for system-created records
  updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_by  UUID REFERENCES users(id),

  PRIMARY KEY (id)
);

-- Auto-update updated_at (or handle in application layer — be consistent)
CREATE TRIGGER set_updated_at
  BEFORE UPDATE ON products
  FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();
```

Index `created_at` — it's almost always used in range queries for list endpoints.

### Surrogate Keys — UUID v7 vs. v4 vs. BIGSERIAL

| Key Type | Sortable | Index-Friendly | Globally Unique | Use When |
|----------|----------|---------------|-----------------|---------|
| BIGSERIAL | Yes (sequential) | Best (B-tree fill, no fragmentation) | No (per-table) | Single-DB systems, high-volume tables |
| UUID v4 | No (random) | Poor (fragmented B-tree, random inserts) | Yes | Distributed systems, exposed to clients |
| UUID v7 | Yes (time-ordered) | Good (monotonically increasing) | Yes | Best default for modern systems |

```sql
-- UUID v7: time-ordered, globally unique, index-friendly
-- PostgreSQL 17+: gen_random_uuid() is v4; v7 requires extension or application generation
-- Application-level generation:
import uuid_utils  # Python: uuid-utils library supports v7
id = str(uuid_utils.uuid7())

-- If you're on older PostgreSQL and need sequential IDs:
id BIGSERIAL PRIMARY KEY  -- efficient, but not externally sharable (reveals record count)
-- Add a separate external_id UUID for API exposure if needed
```

**Expose UUIDs in APIs, keep internal integer IDs if needed for performance**.
This pattern gives you sequential internal keys (efficient indexes) and opaque
external identifiers (don't leak business intelligence through sequential IDs).

---

## Polymorphic Associations

When multiple entity types share a relationship (e.g., comments on both orders and products):

### Approach Comparison

| Pattern | Referential Integrity | Query Complexity | NULL Proliferation | Use When |
|---------|----------------------|-----------------|-------------------|---------|
| STI (Single Table Inheritance) | One FK per table | Simple | High | 2-3 types, mostly shared fields |
| CTI (Class Table Inheritance) | Proper FK per child | Medium (JOIN parent+child) | None | Clean schema, stable type set |
| Polymorphic FK (type+id) | None (no DB FK) | Simple | None | Dynamic type set, accept no FK |
| Concrete table inheritance | Proper FK | Simple | None | Truly separate types, no shared queries |

```sql
-- STI: one table, type discriminator
CREATE TABLE documents (
  id UUID PRIMARY KEY,
  tenant_id UUID NOT NULL,
  document_type TEXT NOT NULL,  -- 'specification' | 'drawing' | 'bom'
  title TEXT NOT NULL,
  -- specification-only columns (NULL for drawings/bom)
  revision_level TEXT,
  -- drawing-only columns (NULL for specifications/bom)
  scale_factor NUMERIC,
  paper_size TEXT,
  -- bom-only columns
  bom_level INT
);
-- Problem: NULL proliferation, growing table as types are added

-- CTI: shared table + type-specific tables
CREATE TABLE documents (
  id UUID PRIMARY KEY,
  tenant_id UUID NOT NULL,
  document_type TEXT NOT NULL,
  title TEXT NOT NULL
);
CREATE TABLE specifications (
  document_id UUID PRIMARY KEY REFERENCES documents(id),
  revision_level TEXT
);
CREATE TABLE drawings (
  document_id UUID PRIMARY KEY REFERENCES documents(id),
  scale_factor NUMERIC,
  paper_size TEXT
);
-- Pro: clean schema, proper FKs, no NULLs
-- Con: JOIN required to get full object

-- Polymorphic FK: no DB-level referential integrity
CREATE TABLE comments (
  id UUID PRIMARY KEY,
  commentable_type TEXT NOT NULL,  -- 'order' | 'product' | 'specification'
  commentable_id UUID NOT NULL,    -- no FK constraint — references different tables
  content TEXT NOT NULL
);
-- Index: (commentable_type, commentable_id)
-- Pro: any entity can have comments without schema changes
-- Con: no FK constraint, orphaned comments possible, hard to clean up
```

**Default choice**: CTI for 2-3 known types with clean schemas. Polymorphic FK
only when the set of types is truly dynamic or unknown at design time.

---

## JSONB vs. Relational Columns

### Decision Framework

```
Use JSONB for:
  ✓ Semi-structured data with variable schema per tenant or per record
  ✓ EAV (entity-attribute-value) problems — product attributes that vary by category
  ✓ Configuration objects with variable keys
  ✓ External system payloads that you store but don't query internally
  ✓ Metadata that's display-only and never filtered/joined on

Don't use JSONB for:
  ✗ Data you filter on in queries (WHERE attributes->>'color' = 'red' is slower than a column)
  ✗ Data with a fixed, known schema — use relational columns
  ✗ Data you join on — no FK constraints on JSONB values
  ✗ High-cardinality filtering data — GIN index helps, but relational > JSON for indexed lookups
  ✗ Anything that needs a foreign key constraint
```

```sql
-- Good JSONB use: product attributes that vary by category
CREATE TABLE products (
  id UUID PRIMARY KEY,
  tenant_id UUID NOT NULL,
  name TEXT NOT NULL,
  category TEXT NOT NULL,
  -- PLM example: fabric has color/material/weight, electronics has voltage/amperage
  attributes JSONB NOT NULL DEFAULT '{}'
);
CREATE INDEX idx_products_attrs ON products USING GIN (attributes jsonb_path_ops);
-- Query: WHERE attributes @> '{"color": "red", "material": "cotton"}'

-- Bad JSONB use: status is always present and always filtered on
-- Don't do: attributes->>'status' = 'active'
-- Do:       status TEXT NOT NULL (relational column)
```

### Atomic JSONB Updates

Avoid read-modify-write for JSONB columns:

```sql
-- Read-modify-write (race condition on concurrent updates)
SELECT attributes FROM products WHERE id = ?;
-- application modifies JSON
UPDATE products SET attributes = ? WHERE id = ?;

-- Atomic update with jsonb_set (no read required)
UPDATE products
SET attributes = jsonb_set(attributes, '{color}', '"red"')
WHERE id = ? AND tenant_id = ?;

-- Remove a key atomically
UPDATE products
SET attributes = attributes - 'deprecated_field'
WHERE id = ? AND tenant_id = ?;
```

---

## Temporal Data Modeling

### Time Types

| Type | What It Records | Example |
|------|----------------|---------|
| Valid time | When a fact was true in the real world | Price was $100 from Jan to March |
| Transaction time | When the database recorded the fact | Row was inserted on Feb 5 |
| Bitemporal | Both simultaneously | As-of queries with audit trail |

```sql
-- Valid-time versioning: one active version at a time
CREATE TABLE product_prices (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  product_id  UUID NOT NULL REFERENCES products(id),
  tenant_id   UUID NOT NULL,
  price_cents INT NOT NULL,
  valid_from  TIMESTAMPTZ NOT NULL,
  valid_to    TIMESTAMPTZ,          -- NULL means "current" (open-ended)
  
  -- Ensure no overlapping intervals for the same product
  CONSTRAINT no_overlap EXCLUDE USING gist (
    product_id WITH =,
    tstzrange(valid_from, valid_to) WITH &&
  )
);

-- Current price
SELECT price_cents FROM product_prices
WHERE product_id = ? AND valid_to IS NULL;

-- Price at a specific point in time
SELECT price_cents FROM product_prices
WHERE product_id = ?
  AND valid_from <= '2024-03-15' AND (valid_to IS NULL OR valid_to > '2024-03-15');
```

**Bitemporal** (PostgreSQL 16+ with temporal table syntax, or manual implementation):
required for regulated industries (healthcare, finance) where you must answer
"what did the system know, as of when it was recorded, about what was true when?"

---

## Audit Trail Architecture

### Append-Only Audit Log

```sql
CREATE TABLE audit_log (
  id              BIGSERIAL PRIMARY KEY,           -- sequential for ordering
  tenant_id       UUID NOT NULL,
  actor_id        UUID,                            -- NULL for system actions
  actor_type      TEXT NOT NULL DEFAULT 'user',    -- 'user' | 'api_key' | 'system'
  action          TEXT NOT NULL,                   -- 'product.created', 'price.updated'
  resource_type   TEXT NOT NULL,
  resource_id     TEXT NOT NULL,                   -- TEXT to accommodate UUIDs and integers
  before_state    JSONB,
  after_state     JSONB,
  diff            JSONB,                           -- changed fields only (computed at write)
  ip_address      INET,
  user_agent      TEXT,
  request_id      TEXT,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
)
PARTITION BY RANGE (created_at);                   -- monthly partitions

-- Indexes for common queries
CREATE INDEX idx_audit_tenant_resource ON audit_log (tenant_id, resource_type, resource_id);
CREATE INDEX idx_audit_tenant_actor ON audit_log (tenant_id, actor_id, created_at DESC);
CREATE INDEX idx_audit_created_at ON audit_log (created_at);  -- for retention/archival queries
```

### Application-Layer vs. Trigger-Based Auditing

| Approach | Pros | Cons |
|----------|------|------|
| Application-layer | Explicit, carries actor context (who did it), can include business context | Requires discipline — easy to miss in bulk updates, must be in every code path |
| Trigger-based | Catches all changes including direct SQL, database-level consistency | No actor context (DB doesn't know which user), hard to debug, tightly coupled to schema |
| Hybrid | Triggers as safety net, application for rich context | Complexity, potential duplicate entries |

**Default**: application-layer auditing with strict code review enforcement.
Write a `AuditService.record(actor, action, resource, before, after)` helper and
require it in every state-modifying service method.

Add a database-level trigger that logs changes to a separate "raw_changes" table
as a safety net for direct SQL migrations and backfills — but don't rely on it
as the primary audit record.

### Compliance Requirements for Audit Logs

| Requirement | Implementation |
|-------------|---------------|
| Immutability | No UPDATE/DELETE on audit_log; separate DB user with INSERT-only privileges |
| Tamper-evidence | Hash chaining (each row includes hash of previous row) for strong guarantee, or archive to WORM storage |
| Retention | Monthly partition archival to cold storage (S3 Glacier), retention policy enforced by partition drop after retention period |
| Exportability | API endpoint: `GET /api/audit-logs?from=&to=&resource_type=&actor_id=` with CSV export |
| Searchability | Tenant-scoped index on resource_type + resource_id for entity history, actor_id for user activity |

---

## Cross-Spoke Routing

| Topic | Route To |
|-------|----------|
| Index design for the schema | `be-relational-db` |
| Zero-downtime migration of the schema | `be-relational-db` |
| Authentication-related data models | `be-auth-patterns` |
| Cache key design for tenant-scoped data | `be-caching-performance` |
| Analytical schema design, warehouse modeling | `ds-data-engineering` |
| Multi-tenancy in data pipelines | `ds-data-engineering` |

## Related
- hub → [[lead-backend-engineer]]
