---
name: devops-release-engineering
description: >
  Feature flags, deployment strategies, and progressive delivery for enterprise
  SaaS. Specialist spoke in the lead-devops-engineer network. Use this skill
  whenever the conversation touches: blue-green deployment, canary deployment,
  progressive delivery, rolling update, recreate deployment, A/B testing, Argo
  Rollouts, analysis template, shadow deployment, traffic mirroring, feature
  flags, LaunchDarkly, Unleash, Flagsmith, GrowthBook, flag lifecycle, flag
  technical debt, flag targeting rules, percentage rollout, database migrations
  in CI/CD, expand contract pattern, zero-downtime schema changes, forward
  compatible migrations, Flyway, Liquibase, Alembic, dual-write, rollback
  strategy, artifact immutability, rollback by redeploy, release trains, release
  freeze, hotfix policy, deployment windows.
  Not for: CI pipeline design — route to devops-ci-cd. Not for: Kubernetes
  resource mechanics for traffic routing — route to devops-container-orchestration
  for Istio VirtualService and DestinationRule specifics.
aliases: [devops-release-engineering]
tier: spoke
domain: engineering
hub: lead-devops-engineer
prerequisites: [lead-devops-engineer]
spec_version: "2.0"
---

# DevOps: Release Engineering

Specialist lens for deployment strategies, feature flags, and progressive delivery
in enterprise SaaS. Part of the lead-devops-engineer skill network.

---

## Domain Boundary

This skill owns: **deployment strategy selection and implementation, feature flag
design and lifecycle, database migrations in CI/CD, rollback strategy, and
release management (release trains, freezes, hotfix policies)**.

- Kubernetes Istio/VirtualService configuration for weighted routing → `devops-container-orchestration`
- CI pipeline stages, smoke tests → `devops-ci-cd`
- Metrics for automated promotion/rollback decisions → `devops-observability`

---

## Deployment Strategy Comparison

### Decision Matrix

| Strategy | Downtime | Rollback speed | Infrastructure cost | Traffic routing required | Best for |
|----------|----------|---------------|---------------------|-------------------------|---------|
| Recreate | Yes | N/A (redeploy) | Low | No | Dev/internal tools only |
| Rolling update | No | Slow (roll forward) | Low | No | Stateless services with backward-compatible changes |
| Blue-green | No | Instant (DNS/LB flip) | 2× at cutover | Load balancer or DNS | Changes with high rollback risk, schema changes |
| Canary | No | Fast (shift traffic back) | Low–medium | Service mesh or ingress | High-traffic services, user-impact validation |
| A/B test | No | Fast | Low–medium | Service mesh + analytics | UX experiments, business hypothesis validation |

### When to Use Each

**Rolling update**: the Kubernetes default. Good when: the change is backward-compatible,
you can tolerate some pods on old version and some on new simultaneously, and the acceptable
rollback path is "roll forward" rather than "roll back."

**Blue-green**: required when you need instant, clean rollback; when schema changes make
mixed-version coexistence impossible; or when smoke testing against the exact production
traffic pattern matters before cutover.

**Canary**: required when validating changes against real user traffic before full rollout;
when the blast radius of a bad deploy must be limited; when you need data on real-world
error rates and latency before committing.

**A/B testing**: distinct from canary. Canary validates stability (error rates, latency).
A/B testing validates a business hypothesis (conversion rate, engagement). Use feature
flags (not traffic routing) for A/B when the split is by user segment, not traffic percentage.

---

## Blue-Green Implementation

### Load Balancer-Based

```yaml
# AWS ALB: two target groups (blue = current, green = new)
# Normal state:
#   Listener rule: 100% → blue-target-group

# During deploy:
#   1. Deploy new version to green target group
#   2. Run smoke tests against green directly (using test header bypass rule)
#   3. Shift listener: 100% → green-target-group
#   4. Monitor error rate and latency for 10 minutes
#   5. Rollback: shift listener back to blue-target-group (< 30 seconds)
#   6. After confidence period: terminate blue pods to save cost
```

### Service Mesh-Based (Istio)

```yaml
# VirtualService: 100% to stable, 0% to new
spec:
  http:
    - route:
        - destination:
            host: api-server
            subset: stable
          weight: 100
        - destination:
            host: api-server
            subset: green
          weight: 0

# Cutover: update weights to 0/100
# Rollback: revert weights to 100/0
```

### Database Compatibility Requirement

Blue-green requires the new version's schema to work against both the old and new
application code simultaneously during the transition window.

**Rule**: deploy the schema change before deploying the new application code.
The schema must be forward-compatible (old application code reads the new schema
without errors).

This is achieved with the expand/contract pattern (see Database Migrations section).

---

## Canary Implementation

### Argo Rollouts (Reference Implementation)

Argo Rollouts is the Kubernetes-native progressive delivery controller.

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: api-server
spec:
  replicas: 10
  strategy:
    canary:
      steps:
        - setWeight: 10      # 10% traffic to canary
        - pause: {duration: 5m}
        - analysis:
            templates:
              - templateName: error-rate-check
        - setWeight: 50
        - pause: {duration: 10m}
        - analysis:
            templates:
              - templateName: error-rate-check
              - templateName: latency-p99-check
        - setWeight: 100     # full rollout if analysis passes
```

### Analysis Templates — Automated Promotion/Rollback

```yaml
apiVersion: argoproj.io/v1alpha1
kind: AnalysisTemplate
metadata:
  name: error-rate-check
spec:
  metrics:
    - name: error-rate
      interval: 1m
      successCondition: result[0] < 0.01    # < 1% error rate
      failureLimit: 3                        # 3 consecutive failures → abort rollout
      provider:
        prometheus:
          address: http://prometheus:9090
          query: |
            sum(rate(http_requests_total{status=~"5..",rollouts_pod_template_hash="{{args.latest-pod-hash}}"}[5m]))
            /
            sum(rate(http_requests_total{rollouts_pod_template_hash="{{args.latest-pod-hash}}"}[5m]))

---
apiVersion: argoproj.io/v1alpha1
kind: AnalysisTemplate
metadata:
  name: latency-p99-check
spec:
  metrics:
    - name: latency-p99
      interval: 2m
      successCondition: result[0] < 500     # P99 < 500ms
      failureLimit: 2
      provider:
        prometheus:
          address: http://prometheus:9090
          query: |
            histogram_quantile(0.99,
              rate(http_request_duration_seconds_bucket{
                rollouts_pod_template_hash="{{args.latest-pod-hash}}"
              }[5m])
            ) * 1000
```

When analysis fails: Argo Rollouts automatically rolls back to the previous stable
version. No human intervention required for the initial detection and rollback.
Human review is still required to understand and fix the root cause.

### Shadow Deployments (Traffic Mirroring)

Mirror production traffic to the new version without affecting user responses:

```yaml
# Istio: mirror traffic to canary (async, responses discarded)
spec:
  http:
    - route:
        - destination:
            host: api-server
            subset: stable
          weight: 100
      mirror:
        host: api-server
        subset: canary
      mirrorPercentage:
        value: 100.0    # mirror 100% of traffic to canary
```

Shadow mode: canary receives real traffic, processes it, but its responses are
discarded. Metrics from the canary are still recorded. Use shadow mode when you
want to validate the canary's behavior against real production traffic before
exposing any real users to it. Zero risk, maximum signal.

---

## Feature Flags

### Tool Selection

| Tool | Use when |
|------|---------|
| LaunchDarkly | Enterprise-grade targeting, SDK for all languages, real-time flag evaluation, analytics integration. Worth the cost for teams doing frequent releases. |
| Unleash | Open-source, self-hosted, solid feature set. Use when data sovereignty or cost is a constraint. |
| Flagsmith | Open-source with SaaS option, feature flags + remote config. Good middle ground. |
| GrowthBook | Feature flags + A/B testing analytics in one tool. Use when you need experimentation infrastructure. |
| Custom (DB-backed) | Only for the simplest use case (boolean flags, no targeting). You'll reimplement LaunchDarkly eventually. |

### Flag Types

```typescript
// Boolean: on/off
const isEnabled = ldClient.variation("new-checkout-flow", user, false);

// Multivariate: select one of several values
const algorithm = ldClient.variation("recommendation-algorithm",
  user, "collaborative-filtering");
// returns: "collaborative-filtering" | "content-based" | "hybrid"

// Experiment (A/B): controlled split with analytics tracking
const variant = ldClient.variation("pricing-page-experiment", user, "control");
// Track outcome:
ldClient.track("signup-completed", user, { variant });
```

### Flag Lifecycle

```
Draft → Active → Launched → Archived
  ↑        ↑          ↑          ↑
Defined  Enabled   100% on   Cleaned up
in code  for some  for all,   from code
          users    code path  and tool
                   still
                   conditional
```

**Launched** is not the same as **Archived**. A flag that's 100% on but still in
the code is technical debt. The code path for the "off" state is dead code — it
accumulates tests, it confuses readers, it may silently break if the flag evaluation
returns an unexpected value.

**Flag cleanup SLA**: every flag gets a cleanup ticket created when it goes to 100%.
The cleanup deadline is 2 sprints from launch. Flag proliferation is the most common
failure mode — teams add flags and never remove them.

### Flag Evaluation in the Request Path

Flag evaluation adds latency if done synchronously with a network call. All major
SDK implementations use local evaluation (flags synced to a local cache, evaluated
in microseconds). Understand your SDK's caching model:

- LaunchDarkly SDK: streaming connection keeps local cache live (sub-millisecond evaluation)
- Unleash SDK: polling interval (default 15s) — flag changes take up to 15s to propagate
- Custom DB-backed flags: query on every request — this is the performance antipattern

For latency-sensitive paths: pre-evaluate flags at request ingress and pass the
evaluated values as context. Never evaluate feature flags in a hot inner loop.

### Targeting Rules

```
Segment: "enterprise-beta"
  - User email domain in [acme.com, globex.com]
  - Account plan == "enterprise"

Rollout rule:
  1. Internal users (email @company.com) → 100% on
  2. Segment "enterprise-beta" → 100% on
  3. All other users → 10% on (by user ID hash for consistency)
  4. Default → off
```

Percentage rollouts: always hash on a stable user identifier (user ID), not a
session ID or request ID. The same user must consistently get the same variant
across requests.

---

## Database Migrations in CI/CD

### The Expand/Contract Pattern

Zero-downtime schema changes require two migration deployments, not one.

**Scenario**: rename column `user_name` to `display_name`.

**Wrong (single-migration approach — causes downtime):**
```sql
-- Migration 1 (BAD): renames column while old app version still reads user_name
ALTER TABLE users RENAME COLUMN user_name TO display_name;
```
Result: old pods still reading `user_name` throw errors during the rolling update window.

**Correct (expand/contract):**

```sql
-- Migration 1 (EXPAND): add new column, backfill, dual-write period
ALTER TABLE users ADD COLUMN display_name TEXT;
UPDATE users SET display_name = user_name;   -- backfill

-- Application deploy: write to BOTH user_name and display_name
-- Read from display_name (with fallback to user_name)
```

```sql
-- Migration 2 (CONTRACT): remove old column — only after old code is fully retired
-- Deployed in the NEXT release cycle
ALTER TABLE users DROP COLUMN user_name;
-- NOT NULL constraint added now that all rows have display_name
ALTER TABLE users ALTER COLUMN display_name SET NOT NULL;
```

The dual-write period lasts for one complete release cycle. Both old and new code
must work with both columns present. This is the price of zero-downtime migrations.

### Migration Tools

| Tool | Language ecosystem | Migration strategy |
|------|-------------------|-------------------|
| Flyway | Java/JVM, but polyglot via CLI | Versioned migrations (V1__, V2__) + repeatable (R__) |
| Liquibase | Java/JVM, polyglot | Changelog-based, XML/YAML/SQL, rollback support |
| Alembic | Python / SQLAlchemy | Auto-generate from model diff, supports async (for FastAPI etc.) |
| golang-migrate | Go, polyglot via CLI | Simple versioned SQL files, widely used in Go services |
| Prisma Migrate | TypeScript/Node.js | Schema-diff-based, tightly coupled to Prisma ORM |

Run migrations as a **pre-deploy hook** (Helm pre-upgrade hook or k8s Job) — after
the schema change is safe but before the new application pods start.

```yaml
# Helm pre-upgrade hook: run migration job
annotations:
  "helm.sh/hook": pre-upgrade
  "helm.sh/hook-weight": "-5"
  "helm.sh/hook-delete-policy": before-hook-creation,hook-succeeded
```

If the migration job fails: the Helm upgrade is aborted. The old pods continue
running against the old schema. No downtime, no broken state.

---

## Rollback Strategy

### Rollback Is a Re-Deploy of the Previous Artifact

Artifact immutability makes rollback mechanical:

```bash
# Rollback = redeploy the last known-good artifact
# The rollback command should be in every runbook:

# Kubernetes (Helm):
helm rollback api-server 0   # roll back to previous revision

# Argo Rollouts:
kubectl argo rollouts undo api-server   # abort and revert to stable

# Kubernetes (native):
kubectl rollout undo deployment/api-server
# OR pin to a specific image:
kubectl set image deployment/api-server api-server=ghcr.io/example/api:PREVIOUS_SHA
```

### What Rollback Cannot Fix

| Scenario | Rollback behavior |
|----------|------------------|
| Code change only | Rollback works: redeploy previous image |
| Forward migration only (added column) | Rollback works: old code ignores new column |
| Migration that dropped/renamed a column | Rollback breaks: old code expects old column, it's gone |
| External state written by new version | Partially works: external state may be inconsistent |
| Cache poisoned by new version | Rollback may not help until cache expires |

The runbook entry for every deployment must include the rollback command AND whether
rollback is safe given the migration state.

### Pre-Deployment Rollback Verification

Before every production deploy, answer:
1. **Is the migration reversible?** If not, what is the rollback path?
2. **What's the rollback command?** Write it out. Don't derive it under pressure.
3. **What state does rollback leave us in?** Is there any cleanup required?

---

## Release Trains and Freezes

### Scheduled Release Windows for Enterprise SaaS

Enterprise customers (especially regulated industries) need predictable change windows:

```
Standard release schedule:
  Tuesday + Thursday: feature releases (following CI/CD pipeline)
  Saturday 02:00–06:00 UTC: maintenance window (infra changes, major migrations)

Freeze periods:
  Last 2 weeks of fiscal quarter: code freeze — no new features, bugfixes only
  Black Friday / year-end: extended freeze per customer agreement
```

### Code Freeze Process

```
T-5 days: freeze announcement to all engineering teams
T-3 days: last merge deadline for scheduled release
T-0: freeze active — only Sev1/Sev2 bugfixes bypass freeze
Freeze lift: explicit notification + "all clear" Slack message
```

**Freeze enforcement**: protect the production branch in the deploy repo (not just main).
During freeze, deploys to production require a second approval from an engineering manager.

### Hotfix Policy

Hotfixes bypass the release train for Sev1 customer-impacting issues:

```
1. Create branch from current production tag (not main — main may have unreleased features)
2. Minimal fix only — the smallest change that addresses the root cause
3. Expedited review: 1 approver (not the normal 2), within 30 minutes
4. Deploy to staging → smoke test → production
5. Cherry-pick to main immediately after production deploy
6. Postmortem within 48 hours
```

**Hotfix antipattern**: deploying an unreleased feature as part of a hotfix because it
"happened to be in the branch." Hotfix branches must contain exactly the fix and nothing
else. Audit the diff before merging.

---

## Cross-Spoke Routing

| Topic | Route To |
|-------|----------|
| Istio VirtualService for canary traffic | `devops-container-orchestration` |
| CI pipeline for the release stages | `devops-ci-cd` |
| Smoke tests and rollback triggers in CI | `devops-ci-cd` |
| Metrics for automated canary analysis | `devops-observability` |
| Helm lifecycle hooks for migrations | `devops-container-orchestration` |
| IaC for release infrastructure | `devops-infrastructure-as-code` |

## Related
- hub → [[lead-devops-engineer]]
