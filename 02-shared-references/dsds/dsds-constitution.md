---
title: Workspace DSDS constitution
tags: [reference, design-systems, dsds, ontology, agents]
created: 2026-09-01
updated: 2026-09-01
links:
  - "[[idempotent-design-decisions]]"
  - "[[agentic-ds-context-model]]"
  - "[[09-component-and-pattern-framework]]"
  - "[[ds-agents-binding]]"
---

# Workspace DSDS constitution

[`workspace-ds-constitution.dsds.yaml`](workspace-ds-constitution.dsds.yaml) is a
**DSDS 0.20 document** for this workspace's design-system *operating model*. It is
project-independent. It is a **view** of facets 1–17 and the standing method
decisions, not a second schema and not a product catalog.

## For future agent
- **TL;DR:** Portable documentation-as-data for the vault DS constitution. Values stay
  in DTCG / a project's DESIGN.md. Arbitration stays in [[component-contract-schema]].
- **As of:** 2026-09 · **Status:** current
- **Audience:** `for: all` on laws; `for: agent` on routing notes

## What it contains

| Kind | What is in the file | What is not |
|---|---|---|
| `system` | The constitution: intent layers, three graphs, complements | Per-project tokens or screens |
| `shared` | APCA/color method, overlay emphasis, one-light elevation, a11y floors | Hex / alpha percentages as law |
| `entry` | Composition laws, async triad, escalation ladders | 62-component anatomy (MCP owns that) |
| `combos` | must / must-not pairings from framework #09 | Usage essays |

A project that needs its own DSDS file **extends** this one (`rel: extends`) and
adds its `token` / `theme` / `component` entries that point at *its* DTCG, CEM,
Storybook, and Figma. Do not fork the constitution per project.

## Complements

| Concern | Source of truth |
|---|---|
| Token values | DTCG / project DESIGN.md |
| Meaning and usage | This document + framework #09 |
| Arbitration | [[component-contract-schema]] |
| Per-component depth | `ux-components` MCP |
| Agent-to-UI runtime | [A2UI catalog](../a2ui/README.md) |

## Regeneration

Hand-authored for now. If a generator is added later, this YAML is the emit target
and the vault files above remain the source. Never the reverse.

Review upstream spec drift with the `ds-source-watch` skill.

Sibling packs for other job contexts (same intents, not DSDS kinds):
[[domain-constitutions]]. Spec: [[constitution-spec]].
