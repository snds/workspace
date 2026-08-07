---
tags: [design-systems, nathan-curtis, figma, slots, governance, enrichment]
created: 2026-08-07
updated: 2026-08-07
status: working
confidence: high
sources:
  - 07-projects/19-workspace-brain/reports/substack-enrichment-brief_v1.0_2026-08-07.md
  - nathanacurtis.substack.com (public posts 2026-08-07)
related_skills: [ds-advisor, design-engineer, figma-canvas-designer, design-system-ops, ux-component-library]
related_projects: [02-centricPLM, 09-figma-repo-sync-plugin]
---

# Nathan Curtis DS ops notes (Substack) — absorbed

## For future agent

Curtis's Substack ([nathanacurtis.substack.com](https://nathanacurtis.substack.com/)) is the
active public DS stream. Contracts/schemas and "as data" work are already in
[[component-contracts-and-schemas]] + framework 09. This note vaults the **next**
ops/Figma/governance ideas for Centric-shaped multi-library work.

## Already absorbed

Component contracts & schemas; components/examples as data; code-only props; states;
specs; token taxonomy; purposeful vs aesthetic naming — see framework 09 + related
knowledge.

## Absorbed now

### Configuration collapse (slots over prop sprawl)

**Make the common configurable; make the uncommon composable.** Figma native slots
push lean cores: keep behavioral/foundational props (`state`, `appearance`, `size`);
drop layout/visibility/hack props and brittle subcomponent trees in favor of slots +
ready-made examples. AI-authored Figma APIs need **predictable composition grammar**,
not hyper-config prop matrices.

Source: [Configuration Collapse](https://nathanacurtis.substack.com/p/configuration-collapse)
(+ slots series on the same publication)

**Land in practice:** when authoring Centric Figma components or agent-driven DS edits,
prefer slots/examples over new booleans; backlog prop sprawl as configuration debt.

### Figma component specs on command

Machine-readable library dumps at scale — treat as **testimony** until transformed into
a contract ([[component-contracts-and-schemas]] deletion/arbitration tests). Useful for
plugin / design-system-ops automation paths.

Source: [Figma Component Specs on Command](https://nathanacurtis.substack.com/p/figma-component-specs-on-command)

### Many core libraries

Multi-library sync and ownership — Centric-shaped (prototype / centric-ui / Figma DS).
Ops discipline lives in [[design-system-ops]] / [[ds-advisor]]; don't let federation
become an excuse for divergent truth without a sync contract.

Source: [Managing DS with Many Core Libraries](https://nathanacurtis.substack.com/p/managing-design-systems-that-make-many-core-libraries-28b80444865e)

### Fallacy of federated design systems

Org anti-pattern: "federated" without arbitration becomes N sources of truth.
Prefer clear ownership + contracts over hopeful federation.

Source: [Fallacy of Federated Design Systems](https://nathanacurtis.substack.com/p/the-fallacy-of-federated-design-systems-23b9a9a05542)

### Testing Figma components

Visual test cases / component testing as a **design-side Proofboard** — same spirit as
[[05-validation-harness]]: show-me evidence, not "looks fine in the sticker sheet."

Source: [Testing Figma Components](https://nathanacurtis.substack.com/p/testing-figma-components-a47fc978465f)

### Design System Generations (trilogy)

Versioning and big-bang generation changes — governance for when a library generation
turns over. Route through [[ds-advisor]] when planning major DS cuts.

Search the publication for the Generations trilogy titles when that work is live.

## Related workspace rules

- Real library components only (standing Figma rule)
- [[figma-ds-surface-authoring]] · [[figma-component-token-axes]]
- [[ds-ops-governance-notes]]
