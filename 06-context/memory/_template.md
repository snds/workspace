---
type: fact            # fact | feedback | reference | decision
description:          # one-line summary — used to decide relevance during recall
created: YYYY-MM-DD
confidence: high      # high | medium | low
relations: {}         # optional typed edges — builds-on / relates-to / contradicts / refutes / exemplifies
                      # e.g.  relations: { refutes: ["[[old-slug]]"], builds-on: ["[[base-slug]]"] }
---

<!--
One durable fact per file. See 01-frameworks/08-workspace-contribution-framework.md
(Memory protocol) for when/how/why, and 02-shared-references/workspace-ontology.md
(routing map) for what belongs here vs. knowledge / context / preferences.
Typed edges + the retrieval preamble: 02-shared-references/vault-graph-conventions.md.
Freshness (timeless / dated / pointer): 02-shared-references/epistemic-standards.md §2.

- fact      → a durable, non-project truth about Sean's world (tools, accounts, environment).
- feedback  → accumulated working guidance/corrections. Add **Why:** and **How to apply:** lines.
- reference → a pointer to an external resource (URL, dashboard, ticket).
- decision  → an ADR: use the full structure below (Context / Decision / Rationale / Consequences).

Link related memories with [[their-slug]] and, where the relationship has meaning, a typed
`relations:` edge. Mark superseded claims with `refutes` (don't just delete). After adding a
file, add a one-line pointer to MEMORY.md. Do NOT store: project state (→ project-context),
session events (→ session-log), domain how-to (→ a skill), learned domain patterns (→ knowledge),
deliberate preferences (→ preferences).
-->

## For future agent
- **TL;DR:** _(the fact/decision in one line — its current bottom line.)_
- **As of:** YYYY-MM · **Status:** current   <!-- current | aging | stale; timeless facts omit the date -->

<!-- fact / feedback / reference: just state it in plain language below.
     For a DECISION, use the ADR structure: -->

## Context — what forced a choice
_(the situation and constraints that made a decision necessary.)_

## Decision — what we chose
_(the choice, stated plainly.)_

## Rationale — why, and what we rejected
_(the reasoning, and the alternatives considered and why they lost.)_

## Consequences — what this commits us to
_(the follow-on costs, obligations, and what's now harder or easier.)_
