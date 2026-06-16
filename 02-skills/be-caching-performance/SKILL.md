---
name: be-caching-performance
description: >
  Cache invalidation strategies, Redis data structure patterns, database
  connection pooling, CDN and edge caching, and SLO design for enterprise
  SaaS production systems. Use this skill whenever the conversation touches:
  TTL vs. write-through vs. cache-aside vs. event-driven invalidation, the
  thundering herd / cache stampede problem, probabilistic early expiry (PER),
  Redis strings, hashes, sorted sets, pub/sub, streams, Lua scripts, Redis
  Cluster and hash slot routing, N+1 query elimination at the application layer,
  connection pool sizing, PgBouncer, read replica routing, CDN Cache-Control
  headers (max-age, s-maxage, stale-while-revalidate, no-store vs. no-cache),
  cache key design for multi-tenant APIs, invalidation on deploy, P50/P95/P99
  latency percentiles, error budget, SLO design by operation type, performance
  investigation methodology, or any question about making a service faster or
  more resilient under load. Not for: database schema design for query performance
  (be-relational-db handles query optimization, cross-reference here for
  application-layer decisions), prediction caching for ML inference
  (ds-ml-engineering), or semantic caching for LLM responses (ds-nlp-llm).
---

# Be: Caching & Performance

Specialist lens for cache strategy, Redis patterns, performance architecture,
and SLO design in enterprise SaaS. Part of the backend engineering skill network.

---

## Domain Boundary

This skill owns: **cache invalidation strategy, Redis patterns, connection
pool management, CDN configuration, and latency SLO design**.

- Database query optimization (EXPLAIN ANALYZE, index design) → `be-relational-db`
- ML prediction caching → `ds-ml-engineering`
- LLM prompt/response semantic caching → `ds-nlp-llm`
- Cache key design decisions overlap with multi-tenancy → `be-data-modeling`

---

## Cache Invalidation Strategies

Cache invalidation is one of the genuinely hard problems. The strategy you choose
determines the consistency guarantees your system provides.

### Strategy Comparison

| Strategy | Consistency | Complexity | Best For |
|----------|-------------|------------|---------|
| TTL only | Eventual (stale up to TTL) | Lowest | Reference data, configuration, slowly-changing external data |
| Cache-aside (lazy) | Eventual | Low | Most application caches |
| Write-through | Strong (if write + cache succeed together) | Medium | Data where staleness is unacceptable |
| Write-behind (async) | Eventual + risk of data loss | High | Rarely appropriate in enterprise SaaS |
| Event-driven invalidation | Strong (when events are reliable) | High | When cache-aside + TTL is too stale |

### Cache-Aside (Lazy Loading) — The Default Pattern

```python
def get_order(order_id: str, tenant_id: str) -> Order:
    cache_key = f"order:{tenant_id}:{order_id}"   # always tenant-scoped
    cached = redis.get(cache_key)
    if cached:
        return deserialize(cached)
    
    order = db.query("SELECT * FROM orders WHERE id = ? AND tenant_id = ?",
                     order_id, tenant_id)
    if order:
        redis.setex(cache_key, ttl=300, value=serialize(order))
    return order
```

**Cache-aside problems**:
- Cold start: first request after deploy or cache eviction hits the database
- Thundering herd: if the cache key expires and 1000 concurrent requests all miss
  simultaneously, all 1000 hit the database at once
- Stale data window: cache is only invalidated by TTL, not by writes

### Write-Through

On every write, update the cache and the database atomically (or as close as
possible).

```python
def update_order(order_id: str, tenant_id: str, updates: dict) -> Order:
    updated_order = db.update("UPDATE orders SET ... WHERE id = ? AND tenant_id = ?",
                              order_id, tenant_id)
    cache_key = f"order:{tenant_id}:{order_id}"
    redis.setex(cache_key, ttl=300, value=serialize(updated_order))
    return updated_order
```

**Write-through problems**: every write pays the cache update cost, even for
data that will never be read from cache. Cache population on writes that are
never followed by reads is waste.

### Event-Driven Invalidation

Listen to domain events and invalidate on write, without TTL dependency.

```python
# Publisher (on order update)
def update_order(order):
    db.update(order)
    event_bus.publish("order.updated", { "order_id": order.id, "tenant_id": order.tenant_id })

# Cache invalidation consumer
@event_handler("order.updated")
def handle_order_updated(event):
    cache_key = f"order:{event['tenant_id']}:{event['order_id']}"
    redis.delete(cache_key)
    # Next read will populate from DB
```

Event-driven invalidation eliminates the stale window but introduces event
processing lag (typically milliseconds). It requires a reliable event bus —
if events are dropped, cache entries go stale indefinitely. Use a dead letter
queue to catch missed invalidation events.

### The Thundering Herd Problem

When a popular cache key expires, all concurrent requests miss simultaneously.
Solutions:

**Probabilistic Early Expiry (PER algorithm)**:
```python
def get_with_per(key: str, compute_fn, ttl: int, beta: float = 1.0):
    value, expiry = redis.get_with_expiry(key)
    if value is None:
        value = compute_fn()
        redis.setex(key, ttl, serialize(value))
        return value
    
    # Compute whether to early-refresh based on remaining TTL
    remaining = expiry - time.time()
    threshold = -beta * math.log(random.random()) * compute_time_estimate
    if remaining < threshold:
        # Refresh proactively before expiry — only ~1 in N requests triggers this
        value = compute_fn()
        redis.setex(key, ttl, serialize(value))
    return value
```

**Distributed lock on cache miss** (simpler, sufficient for most cases):
```python
def get_with_lock(key: str, compute_fn, ttl: int):
    value = redis.get(key)
    if value:
        return deserialize(value)
    
    # Only one process recomputes; others wait
    lock_key = f"lock:{key}"
    if redis.set(lock_key, "1", nx=True, ex=10):  # acquire lock
        try:
            value = compute_fn()
            redis.setex(key, ttl, serialize(value))
        finally:
            redis.delete(lock_key)
    else:
        # Another process is computing — wait briefly and retry
        time.sleep(0.05)
        value = redis.get(key)
    return deserialize(value) if value else compute_fn()
```

---

## Redis Patterns for Enterprise SaaS

### Choosing the Right Data Structure

| Structure | Use For | Key Command(s) |
|-----------|---------|---------------|
| String | Simple K/V, counters, serialized objects, distributed locks | GET/SET, INCR, SET NX PX |
| Hash | Object caching with partial updates, field-level reads | HGET/HSET/HMGET |
| List | Simple queues (use Streams for reliable queues) | LPUSH/RPOP, LLEN |
| Set | Unique membership, set operations | SADD/SMEMBERS/SISMEMBER |
| Sorted Set | Leaderboards, rate limiting windows, time-ordered data | ZADD/ZRANGE, ZRANGEBYSCORE |
| Pub/Sub | Simple broadcast (at-most-once, no persistence) | PUBLISH/SUBSCRIBE |
| Streams | Reliable event log, consumer groups, replay | XADD/XREAD/XREADGROUP |

### Distributed Locks with Redlock

```python
# Simple lock (single Redis instance)
lock_key = f"lock:tenant:{tenant_id}:migration"
acquired = redis.set(lock_key, worker_id, nx=True, px=30000)  # 30s TTL
if acquired:
    try:
        run_migration()
    finally:
        # Only release if we still own it
        script = """
        if redis.call("get", KEYS[1]) == ARGV[1] then
            return redis.call("del", KEYS[1])
        else return 0 end
        """
        redis.eval(script, 1, lock_key, worker_id)
```

For multi-node Redis, use the Redlock algorithm (implemented in `redlock-py`,
`redlock-rb`, etc.). Single-instance locks are fine for most cases where Redis
itself is highly available.

### Sorted Sets for Rate Limiting (Sliding Window)

```python
def check_rate_limit(tenant_id: str, endpoint: str, limit: int, window_sec: int) -> bool:
    now = time.time()
    window_start = now - window_sec
    key = f"ratelimit:{tenant_id}:{endpoint}"
    
    pipe = redis.pipeline()
    pipe.zremrangebyscore(key, 0, window_start)  # remove old entries
    pipe.zadd(key, {str(uuid4()): now})           # record this request
    pipe.zcard(key)                               # count requests in window
    pipe.expire(key, window_sec + 1)
    _, _, count, _ = pipe.execute()
    
    return count <= limit
```

### Redis Streams for Reliable Event Log

Prefer Streams over Pub/Sub when delivery guarantees matter:

```python
# Producer
redis.xadd("events:orders", {
    "event_type": "order.created",
    "tenant_id": tenant_id,
    "order_id": order_id,
    "timestamp": datetime.utcnow().isoformat()
})

# Consumer with consumer group (competing consumers, at-least-once processing)
redis.xgroup_create("events:orders", "notification-service", id="$", mkstream=True)

while True:
    messages = redis.xreadgroup(
        groupname="notification-service",
        consumername=f"worker-{worker_id}",
        streams={"events:orders": ">"},
        count=10,
        block=1000
    )
    for stream, msgs in messages:
        for msg_id, data in msgs:
            process_event(data)
            redis.xack("events:orders", "notification-service", msg_id)
```

Streams provide: message persistence, consumer group semantics (each message
delivered to one consumer in the group), and replay from any offset.

### Lua Scripts for Atomic Multi-Step Operations

When you need multiple Redis operations to be atomic (no other client can
interleave), use a Lua script:

```lua
-- Atomic: check rate limit AND increment (not achievable with MULTI/EXEC + read)
local key = KEYS[1]
local limit = tonumber(ARGV[1])
local ttl = tonumber(ARGV[2])

local count = redis.call('INCR', key)
if count == 1 then
    redis.call('EXPIRE', key, ttl)  -- only set TTL on first increment
end
if count > limit then
    return 0  -- rejected
end
return 1  -- allowed
```

Scripts execute atomically — the entire script runs without other commands
executing between steps. Scripts must not have side effects that can't be
replayed (no random, no time calls that matter).

### Redis Cluster Constraints

Redis Cluster routes keys by hash slot (16384 slots, distributed across nodes).
Cross-slot operations (`MGET` across different slots, transactions, Lua scripts
accessing multiple keys) fail if keys hash to different slots.

Use hash tags to force related keys to the same slot:
```
{tenant:t_123}:orders:active    ← all keys with tag {tenant:t_123} go to same slot
{tenant:t_123}:orders:count
```

This enables MGET and Lua scripts across related keys, at the cost of potential
hot slot issues if one tenant is extremely large.

---

## Database Performance at the Application Layer

### Connection Pool Sizing

The relationship between connection pool size and performance is non-linear:
too small → threads wait for connections; too large → database overloaded with
connections, context switching, lock contention.

```
PostgreSQL rule of thumb: pool_size = (num_cpu_cores * 2) + num_disk_spindles
For a 4-core Postgres instance: ~9-10 connections per app server

With PgBouncer (transaction mode):
  Database pool: 20-40 connections to Postgres
  App server pool: 100-200 connections to PgBouncer
  PgBouncer multiplexes: 100+ app connections to 20-40 DB connections
```

PgBouncer transaction-mode pooling is required when running many application
instances — it prevents connection exhaustion without sacrificing throughput.

**Anti-pattern**: setting connection pool size to 1000 because "connections are cheap."
Each idle PostgreSQL connection consumes ~5-10MB of memory. 1000 connections =
5-10GB just for connection overhead, before any queries run.

### Read Replica Routing

```python
class DatabaseRouter:
    def __init__(self, primary_url, replica_url):
        self.primary = create_engine(primary_url, pool_size=10)
        self.replica = create_engine(replica_url, pool_size=20)
    
    def get_db(self, write: bool = False):
        # Never route writes to replica
        if write:
            return self.primary
        # Route reads to replica — accept slight staleness
        return self.replica

# Usage
@app.get("/orders")
def list_orders(db = Depends(lambda: router.get_db(write=False))):
    return db.execute("SELECT * FROM orders WHERE tenant_id = ?", tenant_id)

@app.post("/orders")
def create_order(db = Depends(lambda: router.get_db(write=True))):
    return db.execute("INSERT INTO orders ...")
```

**Replication lag awareness**: reads after writes must go to the primary if
the read must see the just-committed write. Use `SET synchronous_commit = local`
on the primary to verify the write is durable before returning, and route the
subsequent read to primary within a short window.

---

## CDN and Edge Caching

### Cache-Control Headers — What Each Directive Does

```http
# Static assets (immutable content, content-hashed filenames)
Cache-Control: public, max-age=31536000, immutable

# API responses (tenant-specific — never cache at CDN)
Cache-Control: private, no-cache

# Public, cacheable API responses (non-tenant data)
Cache-Control: public, max-age=60, s-maxage=300, stale-while-revalidate=600
# Meaning:
#   Browsers cache for 60 seconds (max-age)
#   CDN caches for 300 seconds (s-maxage overrides for shared caches)
#   Serve stale for up to 600 additional seconds while revalidating (best-effort freshness)

# No CDN cache, allow browser cache
Cache-Control: private, max-age=300

# No caching anywhere
Cache-Control: no-store
```

`no-cache` ≠ no caching. `no-cache` means "must revalidate before serving cached
copy." `no-store` means "do not cache at all."

### Multi-Tenant Cache Key Design

For APIs serving tenant-specific data, ensure CDN caching never serves one
tenant's data to another:

```
# Correct: tenant-scoped cache key
Cache-Control: private, max-age=300  ← private = browser only, no CDN

# If CDN caching is needed for a multi-tenant API:
Vary: Authorization  ← vary cache by auth token (essentially disables CDN for auth'd content)
# Better: put tenant-agnostic data on a separate path:
GET /public/pricing-tiers  ← cacheable
GET /api/orders            ← private, no CDN
```

### Cache Busting for Static Assets

Content hash in filename is the correct approach:
```
app.abc123.js     ← deploy new version: app.def456.js
                  ← old filename becomes 404, no manual invalidation needed
```

CDN path-based invalidation (invalidating `/app.js`) is expensive and sometimes
slow. Content-hashed filenames are instant and reliable.

---

## SLO Design for Latency

### Percentiles, Not Averages

Average latency hides the user experience at the tail.

```
Scenario: 1000 requests
  999 complete in 50ms
  1 completes in 30,000ms

Average: ~80ms  ← "looks fine"
P99:     30,000ms  ← 1 in 100 users waits 30 seconds
```

Design SLOs around P99. Monitor P95 as an early warning indicator.

### SLO by Operation Type

| Operation | Suggested P99 SLO | Rationale |
|-----------|------------------|-----------|
| Simple DB read (single row, indexed) | 50ms | User expects instant |
| Complex DB read (joins, aggregations) | 200ms | Acceptable for data loading |
| DB write (single record) | 100ms | User action confirmation |
| External API call (timeout budget) | 2,000ms | With retry, keeps total under 5s |
| Background job (async, queued) | Throughput SLO, not latency | User not waiting synchronously |
| Bulk export (>1000 records) | Async — do not impose latency SLO | Must be async |

### Error Budget

```
Availability SLO: 99.9%
Error budget per month: 0.1% of (30 days * 24 hours * 60 minutes) = 43.2 minutes

Spend it intentionally:
- Planned maintenance: 20 minutes
- Unexpected incidents: budget remaining = 23.2 minutes
- When budget exhausted: freeze new deployments until next SLO period
```

Track error budget consumption in a dashboard. Alert at 50% consumed (with 50%
of the period remaining) — that's a signal that the burn rate is too high.

---

## Cross-Spoke Routing

| Topic | Route To |
|-------|----------|
| Database query optimization, index design | `be-relational-db` |
| Multi-tenant cache key strategy | `be-data-modeling` |
| ML prediction result caching | `ds-ml-engineering` |
| LLM prompt/response semantic caching | `ds-nlp-llm` |
| API rate limiting implementation | `be-api-design` |
