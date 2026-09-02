# Engineering Operating Model

*Domain L1 for frontend, backend, DevOps, and mobile. Companion to [[13-domain-rigor-stack]]. Where `eng-foundations` answers "what is true of good systems?", this framework answers "in what order do we decide, verify, and ship, and when are we actually done?" It sits above every engineering skill; the leads and `/eng` execute it.*

---

## The core conviction

**Contracts first, reversible always, observable by default.** Implementation without a named contract, a rollback story, and a verification surface is not engineering delivery. It is hoping.

Three properties, in this order, decide whether a change is deliverable:

1. **Contracts-first.** Anything crossing a boundary (HTTP, queue, schema, module, package, screen) is a contract with explicit inputs, outputs, error taxonomy, and stability guarantee. Write it before the implementation, or discover it from a caller's incident.
2. **Observable.** A change nobody can see running is a change nobody can operate. If a behavior matters, it emits a log line, a metric, or a span that lets a stranger answer "is this working?" at 2am.
3. **Reversible.** Every change names its way back: flag off, previous artifact, reverse migration, restore, or remote kill switch. "We would fix forward" counts only when the fix-forward path is written before the deploy.

"It works locally" is not a verdict, and "the tests pass" is a different claim from "it behaves correctly in production." Both are stages, not finishes.

---

## When this framework invokes

Default-active for FE/BE/DevOps/mobile work, API and schema changes, CI/CD, migrations, incidents, performance work, and any change that crosses a trust or data boundary. It also fires when engineering feasibility is estimated for design or product work, because a feasibility claim is a contract claim.

Load with [[13-domain-rigor-stack]], [[06-qa-operating-model]] for UI surfaces and for the pre-output honesty gate, [[16-security-operating-model]] when auth or trust boundaries change, and [[11-anticipatory-failure-analysis]] before proposing any technique with a visible or operational failure surface. Load [[07-integration-and-review-framework]] when the work heads for a PR.

Operational surface: `/eng` (`03-skills/eng`). Foundation: [[eng-foundations]]. Leads: `lead-frontend-engineer`, `lead-backend-engineer`, `lead-devops-engineer`, `lead-mobile-engineer`. Multi-voice review: `arch-guild`. Measurement: `fe-perf-harness`, `a11y-audit-toolkit`, CI scanners.

---

## 1. Change contract (before implementation)

Four answers in writing before code. On a small change this is three lines in the PR description; on a structural change it is an ADR or RFC.

| Question | What it fixes |
|---|---|
| **What contract changes?** | The API shape, schema, event payload, module interface, or screen behavior callers depend on |
| **Who are the callers?** | Internal services, other teams, external customers, older mobile clients still in the field |
| **What is the reversibility class?** | Reversible, one-way, or destructive (below) |
| **What proves it worked?** | The specific signal, test, or measurement that will be cited at done |

### Reversibility classes

- **Reversible.** Behind a flag or a redeployable artifact. Way back: flip the flag, roll the deploy. Default target for all work.
- **One-way.** Data has moved, a column is populated, a public contract is published, a build is in a store. A way back exists but costs a migration, a deprecation window, or a forced upgrade. Requires a written plan.
- **Destructive.** Data deleted, contract removed, tenants merged. No way back without a restore. Requires verified backups and a named human approver before execution.

Silently escalating a change from reversible to one-way is the most common self-inflicted wound in this domain.

---

## 2. Pipeline

Five ordered stages, each with a done-gate. Skipping a stage is allowed only by naming which one and why. `/eng shape|implement|review|harden|ship` maps onto them.

### 1. Shape the contract
Name the interface before the implementation: OpenAPI or GraphQL schema, event contract, component props, infra module inputs and outputs, or mobile screen state machine. Write or update the ADR / RFC when the decision is structural. State the reversibility class here, not at deploy time.

**Done-gate:** contract artifact exists and is reviewable without reading the implementation; breaking changes are versioned or explicitly accepted with a deprecation window.

### 2. Implement behind the boundary
Code lands behind the contract, so the implementation stays swappable and callers depend on the contract rather than internals. Validate at every trust boundary ([[eng-foundations]]). Feature flags or dark launches when blast radius is high.

**Done-gate:** implementation matches the contract; no secrets in tree; errors fail closed with actionable signals.

### 3. Verify
Automated tests on the trust-critical paths; perf budgets for UI and API SLOs (`fe-perf-harness`); security scan and threat-model delta when boundaries moved ([[16-security-operating-model]]); a11y audit for interactive UI (`a11y-audit-toolkit`, `/qa --lens a11y`). `arch-guild` supplies multi-voice review for structural changes.

**Done-gate:** named checks green or waived with an owner and an expiry; measurement exists for anything claimed as "audit"; the evidence level is stated (see §4).

### 4. Ship with rollback
Migration forward *and* reverse, or expand and contract across separate deploys. Deploy strategy named (flag, canary, percentage rollout). Dashboards and alerts exist for the new failure modes before traffic arrives.

**Done-gate:** rollback rehearsed or documented as one command; on-call knows the signal to watch.

### 5. Observe and operate
Check the signal after deploy: does telemetry show the intended behavior and no new error class? Then SLOs, error budgets, runbooks. Feed failures back into #11 and the next contract revision.

**Done-gate:** at least one observable signal exists for the new path; silent degradation banned ([[silent-degradation-in-fenced-layers]]).

Stage 5 is where work is most often quietly incomplete. A merged PR with green CI and no post-deploy signal check is at stage 3.

---

## 3. Per-layer done-gates

"Ready for review" means every gate below that applies to the touched layer is satisfied or explicitly waived with a reason.

### API contract (REST, GraphQL, gRPC, events, public package)
- Specified in machine-readable form where the stack supports it (OpenAPI, SDL, schema registry, typed client).
- Error taxonomy explicit: which failures are expected and client-correctable, which are exceptional.
- Additive-first. Breaking changes carry a version and a deprecation window, never a coordinated flag day.
- Retries are safe: mutating endpoints are idempotent or accept an idempotency key.
- Pagination, limits, and timeouts stated rather than implied by today's dataset size.

### Schema migration safety
- Expand and contract in separate deploys: add, backfill, dual-read or dual-write, cut over, then remove. Never add a replacement and drop the original in one migration.
- Backfill is batched, resumable, and estimated against production table size, not a seed database.
- Lock and blast-radius impact stated for the largest affected table under live traffic.
- The down path is written: reverse migration, or a documented forward fix with the reason a revert is impossible.
- Multi-tenant scoping verified on every new query path and cache key.

### Service reliability and SLO
- The change names the user-visible SLI it affects (latency, availability, correctness, freshness) and whether it spends error budget.
- Latency claims cite P95/P99 under representative load, never a single local request.
- Every new external dependency states its timeout, retry policy, and degrade behavior when unavailable.
- New failure modes are alertable on symptoms users feel, not only on process health.

### Rollback and release
- A rollback story is named before deploy: flag, previous artifact, reverse migration, or restore.
- Risky changes ship dark or progressively unless the change is trivially reversible.
- Deploy artifacts are immutable and traceable to a commit; configuration is versioned like code.
- Mobile: release is not rollback. Store latency means a server-side kill switch or remote config, an honored minimum supported version, and the assumption that old clients persist for months.

### UI surface (frontend and mobile)
- Accessibility: keyboard reachable and operable, focus visible and managed, semantics and labels correct, automated checks clean on the touched surface, contrast verified. WCAG 2.2 AA is the target for new work. Automated checks are necessary and never sufficient: a hand keyboard pass is part of the gate.
- Performance budget respected for the touched surface (bundle delta, LCP/INP/CLS or the platform equivalent, virtualization above the stated row count), measured with `fe-perf-harness` rather than assumed.
- Every state implemented: loading, empty, partial, error, offline or degraded, permission-denied.
- Design system compliance: tokens and DS components consumed rather than reimplemented; DS gaps routed back instead of locally patched.
- Internationalization holds: no concatenated sentences, formatting through the platform Intl layer, layout survives long strings and RTL where supported.

### Trust boundary (new or changed)
- Threat-model delta for any new input path, authorization decision, secret, third-party dependency, or data export. Route to `sec-threat-modeling`; the gate is owned by [[16-security-operating-model]].
- Authorization enforced server-side at the data access layer, never only in the UI that hides the control.
- Secrets come from a manager, never from git, config files, or CI logs, and rotate without redeploying unrelated services.

---

## 4. Evidence hierarchy (engineering claims)

Highest trust to lowest. Cite the level you are actually at.

1. Production telemetry after the change, on real traffic (metric, trace, log query, error rate)
2. Measured in a production-like environment under representative load or data volume
3. Automated test exercising the contract and its edges, run in CI
4. Local measurement or manual exercise of the real code path
5. Code reading, type checking, reasoning about the diff
6. "It should work" (a hypothesis, not evidence)

A performance claim at level 5 is an opinion. A correctness claim at level 6 is a guess. Naming the level honestly is cheaper than being wrong during an incident.

---

## 5. Absolute bans

- Ship a new trust boundary without a threat-model delta (#16)
- Ship anything without a rollback story: no flag, no revert path, no restore plan, no written fix-forward
- "We'll add tests later" on auth, payments, tenancy, or data-deletion paths
- Swallow errors into empty defaults that look healthy (empty catch, bare `except: pass`, discarded rejections, ignored non-zero exits)
- Migrations without a rollback or expand-and-contract story, including add-and-drop in one deploy
- Break a published contract without a version and a deprecation window, including for mobile clients in the field
- Declare perf or a11y "fine" from gut feel when a harness exists, or cite a number measured on a seed database
- Merge a UI surface with no keyboard pass and no state coverage beyond the happy path
- Change production untraceably: hand-edited infrastructure, unversioned config, a deploy that maps to no commit
- Let plugin TDD/verification skills override #06 / #11 / #13 / this framework ([[AGENTS]] doctrine precedence)

---

## 6. Lead consumption

| Lead | Emphasizes |
|---|---|
| `lead-frontend-engineer` | Component contracts, CWV budgets (`fe-perf-harness`), a11y gate, state coverage, design-token fidelity; routes to `fe-*` and `fw-*` |
| `lead-backend-engineer` | API and schema contracts, migration safety, tenancy, authz, caching SLOs; routes to `be-*` |
| `lead-devops-engineer` | Pipelines, IaC, observability, cost, release engineering, the rollback gate; routes to `devops-*` |
| `lead-mobile-engineer` | Platform craft, offline and sync, store constraints, kill switch and minimum supported version; routes to `mobile-*` |
| `lead-security-architect` | Sideways lens on every stage; owns depth under [[16-security-operating-model]] |
| `arch-guild` | Multi-voice correctness and architecture review at `review` and `harden` |
| Reviewers | The done-gates are the review checklist: contract, evidence level, rollback, signal |

`/eng` owns the verb grammar (`shape`, `implement`, `review`, `harden`, `ship`) and defers to this framework for the gates. Where `/eng` is unavailable on a surface, the leads carry the identical sequence: the sequence is the contract, the command is convenience. `audit` requires measurement; judgment alone is `critique`.

Project-scoped work records its contracts in the repo: an ADR per structural decision, a runbook per operated service, and a plain-English evidence summary (Proofboard) when the deliverable is code Sean must verify without reading it.

---

## Relationship to other frameworks

| Framework | Role relative to #14 |
|---|---|
| #04 Research & Evidence | Confidence tiers behind estimates and feasibility claims |
| #06 QA Operating Model | Target-user bar and the pre-output honesty gate on every engineering report |
| #07 Integration & Review | How the change is partitioned, stacked, and landed so review stays cheap |
| #10 Perception Integrity | Native pixels when an engineering claim is visual (UI regression, chart, render) |
| #11 Anticipatory Failure Analysis | Failure-mode premortem before technique selection and again at the done-boundary |
| #13 Domain Rigor Stack | The meta-model this framework instantiates as engineering's L1 |
| #15 Analysis Operating Model | Instrumentation and event contracts that analysis depends on |
| #16 Security Operating Model | Owns the trust-boundary gate and fail-closed done-gates |
| `eng-foundations` | The context-free principles these gates operationalize |

---

## Operating habits

- Name the contract before naming the library.
- State the reversibility class in the first paragraph of any implementation plan.
- Build the boundary before the abstraction; an abstraction earns its keep only by hiding a decision likely to change.
- Instrument as you build, not after the incident.
- Cite the evidence level with every claim, and never round it up.
- Close with numbers: what was measured, at what load, on what data volume, and what the rollback is.

---

## Related

- [[13-domain-rigor-stack]]
- [[16-security-operating-model]]
- [[06-qa-operating-model]]
- [[07-integration-and-review-framework]]
- [[11-anticipatory-failure-analysis]]
- [[15-analysis-operating-model]]
- [[eng-foundations]]
- [[eng]]
- [[arch-guild]]
- [[lead-frontend-engineer]]
- [[lead-backend-engineer]]
- [[lead-devops-engineer]]
- [[silent-degradation-in-fenced-layers]]
