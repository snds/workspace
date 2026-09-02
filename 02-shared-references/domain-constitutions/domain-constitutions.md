---
title: Domain constitutions
spec_version: "1.0"
status: canonical
tags: [shared-reference, ontology, domain-rigor]
created: 2026-09-02
updated: 2026-09-02
links:
  - "[[constitution-spec]]"
  - "[[13-domain-rigor-stack]]"
  - "[[dsds-constitution]]"
  - "[[agentic-domain-constitutions]]"
  - "[[workspace-ontology]]"
---

# Domain constitutions

Index of job-context ontology packs. Spec: [[constitution-spec]].
Machine registry: [`domains.yaml`](domains.yaml).

The design-systems pack is the template. Every authored row below has the same
intents (methods, complements, three graphs, combos, refuse, `for:`). Only
design-systems uses DSDS 0.20 as its portable file format.

## For future agent
- **TL;DR:** Load [[constitution-spec]] then the matching `dc-*.yaml`. Do not
  dump every domain. Do not mix the three graphs. `mapped` means no YAML yet.
- **As of:** 2026-09 · **Status:** current
- **Audience:** `for: agent`

## Authored

| Id | Job context | L1 | Foundation | Artifact file |
|---|---|---|---|---|
| design-systems | Design systems | #09 | `design-foundations` | [[dsds-constitution]] (DSDS 0.20) |
| ux-ui | UX, UI, visual, interaction | #02 + #01 | `design-foundations` | [`dc-ux-ui.yaml`](dc-ux-ui.yaml) |
| motion | Motion design | #02 | `design-foundations` | [`dc-motion.yaml`](dc-motion.yaml) |
| research | User research | #04 + #15 | `product-foundations` | [`dc-research.yaml`](dc-research.yaml) |
| engineering | Front-end and back-end | #14 | `eng-foundations` | [`dc-engineering.yaml`](dc-engineering.yaml) |
| game | Game design, development, engines | #12 + game-foundations | `game-foundations` | [`dc-game.yaml`](dc-game.yaml) |
| imaging | 3D, environment, photoreal | #12 | `imaging-foundations` | [`dc-imaging.yaml`](dc-imaging.yaml) |
| vision | Machine vision | #15 | `vision-foundations` | [`dc-vision.yaml`](dc-vision.yaml) |
| visual-qa | Visual QA | #06 + #10 | `design-foundations` | [`dc-visual-qa.yaml`](dc-visual-qa.yaml) |
| illustration | Illustration and graphic | #01 | `design-foundations` | [`dc-illustration.yaml`](dc-illustration.yaml) |
| architecture | Architecture and interior | #01 (borrowed) | `design-foundations` | [`dc-architecture.yaml`](dc-architecture.yaml) |

Visual craft that is true in every medium lives in `design-foundations`, not in
a twelfth constitution. UI applies it to screens. Graphic applies it to print
and illustration. Motion applies it in time.

## Mapped (no YAML)

| Id | Job context | Why mapped |
|---|---|---|
| product | Product management | `product-foundations` + #15 exist; methods not yet extracted |
| data | Data science and analytics | Same. Seed: [[experiment-validity-baseline]] |
| security | Security | #16 is a sideways quality lens on engineering, not a visual sibling |

Accessibility is a **cross-cutting lens** (`lead-accessibility-architect`,
`a11y-*`), not a job-context constitution. It appears in other domains'
`shared[]` and `measurement`.

## How to load

1. Match the job to a row.
2. Read the spec if the shape is unfamiliar.
3. Read that domain's YAML (or DSDS file).
4. Load the named foundation, then the named hub, then one spoke.
5. Do not load sibling constitutions unless the work actually crosses them
   (example: environment art loads **imaging** + **game**, not architecture).

## Related

- [[constitution-spec]]  -  shape and bans
- [[agentic-domain-constitutions]]  -  seven-layer remap across domains
- [[agentic-ds-context-model]]  -  DS-specific remap this pack generalizes
- [[13-domain-rigor-stack]]  -  L1–L5 completeness
- [[idempotent-design-decisions]]  -  DS methods only
