---
title: Domain constitution spec
spec_version: "1.0"
status: canonical
tags: [shared-reference, ontology, domain-rigor, dsds]
created: 2026-09-02
updated: 2026-09-02
links:
  - "[[domain-constitutions]]"
  - "[[13-domain-rigor-stack]]"
  - "[[workspace-ontology]]"
  - "[[dsds-constitution]]"
  - "[[agentic-ds-context-model]]"
  - "[[agentic-domain-constitutions]]"
---

# Domain constitution spec

`schemaVersion: domain-constitution/1.0`

The workspace-native documentation view for a **job context**. Same intents as the
design-system constitution ([[dsds-constitution]]), projected onto a format that
does not force DSDS kinds (`token` / `theme` / `component`) onto game engines,
vision pipelines, or research protocols.

This is **not** a sixth design-system schema. DSDS 0.20 remains the portable
view for the design-systems domain because an external spec exists. Every other
domain uses this file's shape. Do not invent a per-domain schema.

## For future agent
- **TL;DR:** One spec. One registry ([[domain-constitutions]]). One YAML per
  authored domain. Methods, not project values. Three graphs still do not mix.
- **Key claims:**
  - Complements stay complements: values · meaning · arbitration · look · runtime.
    (timeless)
  - DSDS is the DS *instance*. This spec is the isomorphic view for other job
    contexts. (dated 2026-09-02)
  - Foundations, L1 frameworks, and hubs already exist. A constitution names
    them and encodes standing methods. It does not replace them. (timeless)
  - `mapped` is an honest gap. Empty YAML is a stub and is banned. (timeless)
- **As of:** 2026-09 · **Status:** current
- **Audience:** `for: all` on the shape; `for: agent` on routing notes

## What a constitution is

A project-independent pack for one job context:

| Piece | Owns |
|---|---|
| `shared[]` | Standing **methods** that survive a change of brand, repo, engine, or study |
| `entries[]` | Named pipelines, combo owners, refuse surfaces |
| `combos[]` | must / must-not pairings (machine form of composition laws) |
| `complements` | Which layer owns values vs meaning vs arbitration vs look vs runtime |
| `graphs` | Pointers into the three graphs. Never a fourth edge vocabulary |
| `watch[]` | Upstream URLs. Report-first. Never auto-edit ontology from a fetch |

A project's `DESIGN.md`, `RENDER.md`, ADR, cuespec, or study plan **extends**
the constitution. It does not fork it. Engine versions, hex, brand typefaces,
dataset paths, and Unity/Unreal release numbers are values. They do not live here.

## Complements (required table, domain-specific cells)

| Concern | Question the cell answers |
|---|---|
| **Values** | What is allowed to change when the brand / engine / repo / study changes? |
| **Meaning** | Where is usage and method stated? (this constitution + L1) |
| **Arbitration** | What can refuse deterministically? (contract, cuespec, SLO, confidence tier) |
| **Look / identity** | Where does the project's visual or narrative identity live? |
| **Runtime** | Wire format, engine, implemented UI, deployed model. Not the ontology. |

Copy the table. Fill the cells. Do not collapse two cells into one file.

## Three graphs (do not cross)

1. **Skill-load**  -  `## Related` on skills. Foundation → hub → spoke.
2. **Epistemic**  -  `relations:` on knowledge and decisions.
3. **Domain artifact**  -  this YAML's `system` / `shared` / `entry` / `combos`.
   For design-systems the artifact graph **is** DSDS 0.20. For other domains it
   is `domain-constitution/1.0`. Same intents. Different kind names only where
   DSDS kinds would lie.

Do not put `builds-on` on a skill. Do not put `hub:` in a knowledge entry. Do
not treat a constitution `combo` as a skill load-chain.

## Relation to Domain Rigor (#13)

| #13 layer | Constitution role |
|---|---|
| L1 operating model | Named in `l1`. The framework stays the pipeline. |
| L2 command / contract | Named in `command` and `complements.arbitration`. |
| L3 measurement | Named in `measurement`. Audit without this cell is critique. |
| L4 load chain | Named in `graphs.skillLoad` and `foundation` / `leads`. |
| L5 doctrine routing | `refuse[]` + `defers_to` on wrapper skills. Plugins do not override L1. |

A constitution that restates a hub's spoke table is noise. Point, then encode
only the methods and combos that must travel with every job in that context.

## Status

| Status | Meaning | Allowed YAML |
|---|---|---|
| `canonical` | External schema instance exists (today: DSDS for design-systems) | That schema's file, not a fork |
| `authored` | Full `domain-constitution/1.0` with methods, combos, refuse, complements | Required |
| `mapped` | L1 / foundation / leads named in [[domain-constitutions]] only | **No** YAML. Do not stub. |

Promote `mapped` → `authored` when methods can be extracted from existing L1
and knowledge without inventing law. Do not author a constitution to look busy.

## File layout

```
02-shared-references/domain-constitutions/
  constitution-spec.md      ← this file
  domain-constitutions.md   ← index
  domains.yaml              ← machine registry
  dc-<id>.yaml              ← authored instances
```

Design-systems instance stays at `02-shared-references/dsds/` (DSDS 0.20).
The registry points at it. Do not duplicate it here.

## YAML shape

Required top-level keys on an authored file: `schemaVersion`, `id`, `name`,
`status`, `l1`, `foundation`, `leads`, `measurement`, `command`, `complements`,
`graphs`, `shared`, `entries`, `combos`, `refuse`.

Optional: `watch`, `notes`.

`shared[].items[].level` is `must` | `must-not` | `should`.
Audience on a shared block or entry: `for: human | agent | all`.

## Idempotent methods vs project values

Same rule as [[idempotent-design-decisions]], generalized:

| Belongs in the constitution | Does not belong |
|---|---|
| Method that stays true if the brand, engine, or study changes | Hex, typeface, engine version, dataset path, product hue |
| How to decide / measure / refuse | What Legion's hull metalness is this week |
| Pointers to validated knowledge | A second copy of those entries |

DS methods stay in [[idempotent-design-decisions]] plus DSDS `shared[]`.
Other domains keep methods in their `dc-*.yaml` `shared[]` until a cluster
grows long enough to earn its own `idempotent-<domain>-decisions.md`. Do not
dump every domain into the DS methods file.

## Source watch

`watch[]` is testimony: URLs that can change the constitution. Review with the
same report-first rule as `ds-source-watch`. Hash change is not a law change.
A human judges. Do not auto-edit ontology from a fetch.

Per-domain fetch wiring is additive. Until a domain is in
`02-shared-references/ds-source-watch.json` (or a later generalized registry),
`watch[]` is a backlog of sources, not a cron.

## Always-on ban

Constitutions load **on domain trigger**, the same way foundations do. They are
not always-on. The Atlassian field test still forbids one dump of every job
context. Depth lives in skills, MCP, and knowledge, retrieved on demand.

## Authoring checklist

Before calling a domain `authored`:

1. L1 exists, or the constitution **names** the borrowed L1 (architecture
   borrows #01; it does not pretend to have #17).
2. Foundation → hub → spoke resolves in `skills.registry.json`.
3. Every `shared` item is a method extracted from L1, a foundation, or
   validated knowledge. No invented floors.
4. Complements table has five distinct cells.
5. `refuse[]` names at least the domain's known shallow override.
6. No TODO, no unfilled token, no "TBD combo".
7. Index row + registry row + this spec stay in sync.

## Related

- [[domain-constitutions]]  -  index of job contexts
- [[13-domain-rigor-stack]]  -  L1–L5 completeness
- [[workspace-ontology]]  -  routing map
- [[dsds-constitution]]  -  DS instance of the same intents
- [[idempotent-design-decisions]]  -  DS methods
- [[agentic-domain-constitutions]]  -  context-model remap across domains
- [[vault-graph-conventions]]  -  `for:` stamps and epistemic edges
