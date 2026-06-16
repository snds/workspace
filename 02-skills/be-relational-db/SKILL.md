---
name: be-relational-db
description: >
  Relational database design, normalization, indexing strategy, query
  optimization, transaction isolation, and zero-downtime migration patterns
  for enterprise SaaS production databases. Use this skill whenever the
  conversation touches: normalization (1NF through BCNF), denormalization
  tradeoffs, index design (B-tree, partial, composite, GIN, covering indexes),
  query performance, EXPLAIN ANALYZE, join strategies, N+1 queries, CTE vs.
  subquery vs. join, window functions, transaction isolation levels (READ
  COMMITTED, REPEATABLE READ, SERIALIZABLE), locking (SELECT FOR UPDATE,
  advisory locks), zero-downtime migration patterns (expand/contract,
  CREATE INDEX CONCURRENTLY, NOT VALID constraints, batched backfills),
  table partitioning, index bloat, VACUUM, autovacuum tuning, or any
  question about making a relational database schema correct and performant
  under production load. Primarily PostgreSQL-focused with callouts for MySQL
  divergence where it matters. Not for: application-level entity modeling
  (be-data-modeling), analytical pipeline schema design (ds-data-engineering),
  or Redis/cache patterns (be-caching-performance).
aliases: [be-relational-db]
tier: spoke
domain: engineering
hub: lead-backend-engineer
prerequisites: [lead-backend-engineer]
spec_version: "2.0"
---

# Be: Relational Database

Specialist lens for relational database design and optimization in enterprise
SaaS production environments. Part of the backend engineering skill network.

---

## Domain Boundary

This skill owns: **schema normalization, index design, query optimization,
transaction semantics, and production migration strategies**.

- Application-layer entity modeling and multi-tenancy strategy → `be-data-modeling`
- Analytical schema design, warehouse modeling → `ds-data-engineering`
- Read replica routing, connection pooling, cache-aside patterns → `be-caching-performance`
- ORM configuration and N+1 in application code → addressed here, implementation detail in app layer

---

## Normalization

### Normal Forms — What Each One Eliminates

| Form | Requirement | Anomaly Prevented |
|------|------------|-------------------|
| 1NF | Atomic values, no repeating groups | Update anomalies from multi-valued cells |
| 2NF | No partial dependencies on composite key | Redundancy in tables with composite PKs |
| 3NF | No transitive dependencies | Redundancy from A→B→C chains |
| BCNF | Every determinant is a candidate key | Remaining update anomalies in 3NF tables |

In practice: design to 3NF or BCNF as the default. Most OLTP schemas don't need
to go further. The pathological cases that need BCNF beyond 3NF are uncommon.

### Deliberate Denormalization

Denormalize with intent and documentation. Valid reasons:

- **Read-heavy reporting tables**: pre-computed aggregates, flattened joins for
  dashboards that run against OLTP (before you have a dedicated analytics layer)
- **Materialized views**: PostgreSQL materialized views give you denormalized
  read performance with explicit refresh semantics — prefer these over manual
  denormalization when the source data is in the same database
- **Pre-computed aggregates**: `item_count`, `total_value` on header records
  when recomputing them on every read is prohibitively expensive

**Rule**: every denormalization decision gets a comment in the migration file
explaining why, and a trigger or application convention explaining how it stays
in sync. Denormalization without a sync strategy is just a future data integrity
bug.

---

## Index Design

### B-tree Indexes (the default)

B-tree is correct for: equality queries, range queries (`BETWEEN`, `>`, `<`),
`ORDER BY`, and any query where the planner can use the index for both filtering
and sorting.

Not appropriate for: JSONB containment queries, array operations, full-text search.

```sql
-- Standard B-tree on a foreign key (always index FKs in PostgreSQL — no implicit index)
CREATE INDEX idx_orders_tenant_id ON orders (tenant_id);

-- Covering index: include non-key columns to avoid heap fetches
CREATE INDEX idx_orders_tenant_created ON orders (tenant_id, created_at)
  INCLUDE (status, total_amount);
-- Planner can satisfy SELECT status, total_amount WHERE tenant_id = ? ORDER BY created_at
-- entirely from the index — no heap fetch needed
```

### Partial Indexes

Partial indexes filter with a WHERE clause. They are dramatically smaller and
faster for queries that always include that predicate.

```sql
-- Only index active records — if 95% of orders are archived, this is 20x smaller
CREATE INDEX idx_orders_active ON orders (tenant_id, created_at)
  WHERE status != 'archived';

-- Only index unprocessed events (frequently queried, small set)
CREATE INDEX idx_events_unprocessed ON events (created_at, tenant_id)
  WHERE processed_at IS NULL;
```

Anti-pattern: adding a partial index and then writing queries that don't include
the predicate, defeating the purpose.

### Composite Indexes — Column Order Matters

The leftmost prefix rule: the index can be used for queries that filter on a
prefix of the columns, in order.

```sql
-- Index: (tenant_id, status, created_at)
-- Useful for: WHERE tenant_id = ?
-- Useful for: WHERE tenant_id = ? AND status = ?
-- Useful for: WHERE tenant_id = ? AND status = ? ORDER BY created_at
-- NOT useful for: WHERE status = ? (no tenant_id)
-- NOT useful for: WHERE created_at > ? (skips tenant_id and status)
```

Order columns by: (1) equality predicates first, (2) range predicates last,
(3) sort columns after range predicates. Within equality predicates, higher
selectivity first improves the scan.

### GIN Indexes

GIN (Generalized Inverted Index) for: JSONB containment (`@>`), array operations,
full-text search (`tsvector`).

```sql
-- JSONB containment queries
CREATE INDEX idx_products_attributes ON products USING GIN (attributes jsonb_path_ops);
-- Enables: WHERE attributes @> '{"color": "red"}'

-- Full-text search
CREATE INDEX idx_documents_fts ON documents USING GIN (to_tsvector('english', body));
```

GIN indexes are slower to update than B-tree — appropriate when reads dominate
writes on the indexed column.

### Index Bloat

Write-heavy tables accumulate dead tuples from UPDATEs and DELETEs. PostgreSQL's
MVCC keeps old row versions for concurrent readers; VACUUM reclaims them.

Signs of index bloat: index size grows disproportionately to table size, queries
slow down despite the planner using the index.

```sql
-- Check for bloat
SELECT schemaname, tablename, n_dead_tup, n_live_tup,
       round(n_dead_tup::numeric / nullif(n_live_tup, 0) * 100, 2) AS dead_ratio
FROM pg_stat_user_tables
ORDER BY n_dead_tup DESC;
```

Autovacuum tuning for write-heavy tables (set at table level):
```sql
ALTER TABLE events SET (
  autovacuum_vacuum_scale_factor = 0.01,  -- vacuum at 1% dead tuples (default 20%)
  autovacuum_analyze_scale_factor = 0.005
);
```

`REINDEX CONCURRENTLY` to rebuild bloated indexes without locking.

---

## Query Optimization

### EXPLAIN ANALYZE — Reading the Plan

```sql
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT) SELECT ...;
```

Key things to look for:

| Node Type | Meaning | Good/Bad |
|-----------|---------|----------|
| `Seq Scan` | Full table scan | Bad for large tables; fine for small ones or when returning >20% of rows |
| `Index Scan` | Uses index, fetches heap for each row | Good; watch for many heap fetches |
| `Index Only Scan` | Uses covering index, no heap fetch | Best for read performance |
| `Bitmap Heap Scan` | Batches heap fetches from bitmap index scan | Good for medium selectivity |
| `Hash Join` | Builds hash table from smaller relation | Good for large equi-joins |
| `Nested Loop` | Iterates outer, probes inner per row | Good when inner is small and indexed |
| `Merge Join` | Both sides sorted, merge | Good when both sides have matching sort |

Rows estimate vs. actual: large discrepancy means stale statistics. Run
`ANALYZE tablename` or check `pg_stat_user_tables.last_analyze`.

### CTE vs. Subquery vs. Join

Before PostgreSQL 12: CTEs create an optimization fence — the planner cannot
push predicates into them. This causes full materialization even when unnecessary.

```sql
-- Pre-PG12: this materializes all active_orders before filtering by tenant
WITH active_orders AS (
  SELECT * FROM orders WHERE status = 'active'  -- optimization fence
)
SELECT * FROM active_orders WHERE tenant_id = ?;

-- Better (pre-PG12): inline subquery or join
SELECT * FROM orders WHERE status = 'active' AND tenant_id = ?;
```

PostgreSQL 12+: CTEs are inlined by default unless `MATERIALIZED` is explicitly
specified. Still, write CTEs for clarity only when the query plan is equivalent.

### N+1 Query Detection and Resolution

N+1 occurs when code loads a parent record, then issues one query per child
in a loop. Classic ORM footgun.

```python
# N+1: 1 query for orders + N queries for line items
orders = db.query("SELECT * FROM orders WHERE tenant_id = ?", tenant_id)
for order in orders:
    order.line_items = db.query("SELECT * FROM line_items WHERE order_id = ?", order.id)

# Correct: 2 queries with in-memory join
orders = db.query("SELECT * FROM orders WHERE tenant_id = ?", tenant_id)
order_ids = [o.id for o in orders]
line_items = db.query("SELECT * FROM line_items WHERE order_id = ANY(?)", order_ids)
# group line_items by order_id in memory
```

For GraphQL: DataLoader batches within a request cycle — required, not optional.
Without it, every nested field resolver is an N+1.

### Window Functions vs. Subqueries

Window functions outperform correlated subqueries for analytical queries over
partitioned data.

```sql
-- Correlated subquery: O(n) subquery executions
SELECT o.id, o.amount,
  (SELECT SUM(amount) FROM orders o2 WHERE o2.tenant_id = o.tenant_id) as tenant_total
FROM orders o;

-- Window function: single pass
SELECT id, amount,
  SUM(amount) OVER (PARTITION BY tenant_id) as tenant_total
FROM orders;
```

---

## Transaction Isolation

PostgreSQL defaults to READ COMMITTED. Most applications should understand what
that means before choosing a different level.

### Isolation Level Comparison

| Level | Dirty Read | Non-Repeatable Read | Phantom Read |
|-------|-----------|--------------------|-|
| READ COMMITTED (PG default) | No | Possible | Possible |
| REPEATABLE READ | No | No | No (PG uses snapshot) |
| SERIALIZABLE | No | No | No |

**READ COMMITTED**: each statement sees a snapshot as of statement start. Two
`SELECT`s in the same transaction can see different data if a concurrent
transaction commits between them. Fine for most operations.

**REPEATABLE READ**: snapshot is taken at transaction start. All reads within
the transaction see the same data. Required when you need consistent reads
across multiple queries in a transaction (e.g., reading a consistent view of
related records).

**SERIALIZABLE**: PostgreSQL uses SSI (Serializable Snapshot Isolation) — detects
and aborts serialization anomalies. Use for financial operations where you
need full isolation guarantees. Expect ~20-30% throughput reduction and retry
logic for serialization failures.

### Explicit Locking

```sql
-- Lock rows for update — blocks concurrent writes to the same rows
SELECT * FROM orders WHERE id = ? FOR UPDATE;

-- Skip locked rows — useful for work queue patterns (avoid lock contention)
SELECT * FROM jobs WHERE status = 'pending' LIMIT 10 FOR UPDATE SKIP LOCKED;

-- Advisory locks — application-level distributed lock without row-level coupling
SELECT pg_advisory_xact_lock(hashtext('migration-lock'));
```

`FOR UPDATE SKIP LOCKED` is the canonical pattern for distributed job processing
without a message queue — multiple workers can pull from the same jobs table
without blocking each other.

---

## Zero-Downtime Migration Strategies

Live enterprise traffic means migrations must never lock tables for more than
a few milliseconds. The expand/contract pattern and concurrent index creation
are the two most important tools.

### Expand/Contract (Additive-First)

Never rename a column, change its type, or make it NOT NULL in a single migration
while the app is running.

```
Phase 1 (Expand):  Add new_column (nullable, no default that requires table rewrite)
Phase 2 (Backfill): Populate new_column for existing rows (batched)
Phase 3 (Deploy):  Deploy code that writes to both old_column and new_column
Phase 4 (Verify):  Confirm new_column is fully populated and correct
Phase 5 (Switch):  Deploy code that reads from new_column, stops writing old_column
Phase 6 (Contract): Drop old_column (in a separate migration, after Phase 5 is stable)
```

Collapsing any two phases risks a window where old code reads null from new_column
or new code reads stale from old_column.

### CREATE INDEX CONCURRENTLY

```sql
-- Acquires only a ShareUpdateExclusiveLock — reads and writes proceed
CREATE INDEX CONCURRENTLY idx_orders_new ON orders (tenant_id, created_at);
-- Takes longer to build (two passes), fails if a concurrent transaction aborts
-- If it fails, leaves an INVALID index — clean up with DROP INDEX CONCURRENTLY
```

Never `CREATE INDEX` (non-concurrent) on a live production table above a few MB.
It acquires an AccessShareLock that blocks writes.

### NOT VALID Constraint Addition

```sql
-- Add constraint without validating existing rows (fast, no table scan)
ALTER TABLE orders ADD CONSTRAINT fk_orders_tenant
  FOREIGN KEY (tenant_id) REFERENCES tenants(id) NOT VALID;

-- Validate in a separate transaction (ShareUpdateExclusiveLock, not full lock)
ALTER TABLE orders VALIDATE CONSTRAINT fk_orders_tenant;
```

### Batched Backfills

Never `UPDATE orders SET new_column = compute(old_column)` for a large table.
It creates a long-running transaction, bloats WAL, and can cause replication lag.

```sql
-- Batched backfill: process in chunks with explicit commit between batches
DO $$
DECLARE
  batch_size INT := 1000;
  last_id BIGINT := 0;
  max_id BIGINT;
BEGIN
  SELECT MAX(id) INTO max_id FROM orders;
  WHILE last_id < max_id LOOP
    UPDATE orders
    SET new_column = compute(old_column)
    WHERE id > last_id AND id <= last_id + batch_size
      AND new_column IS NULL;
    last_id := last_id + batch_size;
    PERFORM pg_sleep(0.01);  -- yield to other transactions
    COMMIT;
  END LOOP;
END $$;
```

In application code, the backfill is typically a background job that processes
rows in batches with a rate limit, not a raw SQL script.

---

## Partitioning

Partitioning is useful when a table exceeds ~100M rows and queries consistently
target a subset of rows (e.g., by time range or tenant).

| Strategy | When to Use | Example |
|----------|-------------|---------|
| Range (time-based) | Append-mostly event/audit tables, archive old partitions | `events` partitioned by `created_at` monthly |
| List (tenant-based) | Large tenants need dedicated partitions for isolation | Highest-tier tenants get own partition |
| Hash | Even distribution, no natural range key | Partitioning by ID hash for parallel query |

**Partitioning anti-patterns**:
- Partitioning before you need it — adds DDL complexity for no benefit on small tables
- Partitioning by a column that doesn't appear in most queries (no partition pruning)
- Forgetting to add indexes on each partition (they don't inherit from parent)

Partition pruning only works if the query includes the partition key in the WHERE
clause. A full-table scan on a partitioned table is worse than on an unpartitioned
one (must scan all partition children).

---

## Cross-Spoke Routing

| Topic | Route To |
|-------|----------|
| Application-layer entity modeling, aggregate design | `be-data-modeling` |
| Multi-tenancy schema strategy | `be-data-modeling` |
| Connection pooling, read replica routing | `be-caching-performance` |
| Analytical queries on OLTP data | `ds-product-analytics` |
| OLTP schema as pipeline source | `ds-data-engineering` |
