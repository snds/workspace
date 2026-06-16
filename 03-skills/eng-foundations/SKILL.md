---
name: eng-foundations
description: >
  Context-free engineering first principles shared across frontend, backend, and
  platform/devops work — complexity and data structures, naming and abstraction,
  interface contracts (idempotency, versioning, error taxonomy), caching and
  invalidation, the testing pyramid, and failure/resilience thinking. Load BEFORE
  any engineering discipline hub or spoke. Triggers: software design, complexity,
  abstraction, API contract, idempotency, caching, testing strategy, resilience.
aliases: [eng-foundations]
triggers: [software design, complexity, abstraction, naming, api contract, idempotency, versioning, caching, invalidation, testing pyramid, resilience, error handling]
tier: foundation
domain: engineering
surfaces: ["*"]
spec_version: "2.0"
---

# Engineering Foundations

The principles that hold whether you're writing a React component, a service, or a deployment pipeline.
Frontend/backend/devops apply them in a stack; this owns the **why it's true anywhere**. Stack-specific
mechanics (hooks, query planners, container runtimes) live in the discipline spokes.

## Complexity + data structures
The cost model is the design tool: know the time/space complexity of your access patterns before
choosing a structure. Most "it got slow" problems are an O(n) (or O(n²)) operation on a hot path that
a map/index/precompute makes O(1). Choose the structure that makes the **common operation** cheap.

## Naming + abstraction
Names are the interface to intent — name for *what/why*, not *how*. **An abstraction earns its keep
only when it hides a decision that's likely to change** (or removes real duplication). Premature
abstraction and copy-paste are both failures; the rule of three is a decent threshold. Prefer composition
over inheritance; prefer pure, testable units over hidden state.

## Interface contracts
Anything crossing a boundary (function, API, queue, file) is a contract: explicit inputs/outputs, an
**error taxonomy** (expected vs. exceptional), and stability guarantees. Principles true at every layer:
**idempotency** (safe to retry), **versioning** (evolve without breaking callers), **validate at the
boundary** (trust nothing from outside), and *fail loudly at the edge, degrade gracefully in the core*.

## Caching + invalidation
A cache is a correctness/latency trade. The hard part is **invalidation** — stale data is a bug. Decide
the staleness budget explicitly (TTL, write-through, event-driven) before adding the cache; an unbounded
or never-invalidated cache is a latent incident.

## Testing strategy
Test behavior, not implementation. The **pyramid** (many fast unit tests, fewer integration, fewest E2E)
is an economics argument: push coverage to the cheapest layer that can catch the class of bug. Test the
contract and the edges (empty, boundary, failure, concurrency), not the happy path alone.

## Failure + resilience
Everything fails; design for it. Timeouts, retries-with-backoff, circuit breakers, idempotent
operations, and **observability** (you can't fix what you can't see) are universal. Make failure modes
explicit and recoverable rather than assuming success.

## Applies in
- [[lead-frontend-engineer]] — the UI runtime · [[lead-backend-engineer]] — services + data ·
  [[lead-devops-engineer]] — build, deploy, operate.

## Related
- applies-in ← [[lead-backend-engineer]] · [[lead-devops-engineer]] · [[lead-frontend-engineer]] · [[lead-security-architect]]
