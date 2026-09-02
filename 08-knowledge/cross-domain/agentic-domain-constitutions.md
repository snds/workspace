---
tags: [ontology, knowledge-graph, context-model, domain-rigor, agentic]
created: 2026-09-02
updated: 2026-09-02
status: working
confidence: medium
sources:
  - "Workspace domain constitutions (vault, 2026-09-02)"
  - "Agentic DS context model (vault, 2026-09-01)"
  - "Domain Rigor Stack #13 (vault, current)"
related_skills: [design-foundations, game-foundations, imaging-foundations, vision-foundations, eng-foundations]
related_projects: [19-workspace-brain]
relations:
  builds-on:
    - "[[agentic-ds-context-model]]"
    - "[[13-domain-rigor-stack]]"
    - "[[constitution-spec]]"
  relates-to:
    - "[[domain-constitutions]]"
    - "[[dsds-constitution]]"
    - "[[workspace-ontology]]"
    - "[[perception-critique-stack]]"
    - "[[measured-visual-verdicts]]"
---

# Agentic domain constitutions

The design-system remap generalized. Same seven-layer loop, same three graphs,
same complements rule. One constitution pack per job context. DSDS 0.20 remains
the portable file format only where that spec fits (design systems).

## For future agent
- **TL;DR:** Do not invent a sixth schema per domain. Load
  [[constitution-spec]] + the matching `dc-*.yaml` (or [[dsds-constitution]]).
  Methods, not values. `mapped` means no YAML.
- **Key claims:**
  - The seven-layer remap is domain-agnostic. Only L3 artifact kinds and L4
    schema cells change by job context. (timeless)
  - Visual principles that are true everywhere stay in `design-foundations`.
    UI, graphic, motion, and 3D *apply* them. (timeless)
  - Architecture has no lead hub. Game environments are imaging + game, not
    architecture. Vision has no lead hub. Those gaps are named, not faked.
    (dated 2026-09-02)
- **As of:** 2026-09 · **Status:** working
- **Audience:** `for: agent`

## 1. What stays identical

From [[agentic-ds-context-model]]:

```
L0 Harness            request → policy → context builder → act → eval → human gate
L1 Profile + route    who owns / reviews; where a write belongs
L2 Intent delivery    framing / workflow / guidelines / constraints
L3 Three graphs       skill load · epistemic · domain artifact
L4 Schema stack       values · meaning · arbitration · look · runtime
L5 Memory             short = session · long = knowledge/memory · shared = Live handoff
L6 AgentOps           validators + prove now; cost/task later
```

Refuse, unchanged: general-purpose agent role; one always-loaded dump; mixing
the three graphs; treating documentation-as-data as the contract.

## 2. What changes per domain

| Cell | Design systems | Other job contexts |
|---|---|---|
| Artifact graph | DSDS 0.20 kinds | `domain-constitution/1.0` kinds (`shared` / `entry` / `combos`) |
| Values | DTCG / DESIGN.md | Engine version, dataset, brand mark, schema contents |
| Arbitration | component-contract-schema | cuespec, SLO, confidence tier, play-prove spec, dataset contract |
| Portable spec | DSDS (external) | Workspace spec only, until a real external schema exists |

Complements table is mandatory. Collapsing meaning into values is how hex and
Unity versions become fake law.

## 3. Domain map (authored 2026-09-02)

Index: [[domain-constitutions]].

| Cluster | Why it is a separate constitution |
|---|---|
| design-systems | Encoding meaning into tokens/components. Already canonical via DSDS. |
| ux-ui | Screen IA, interaction, visual hierarchy. Applies foundations to UI. |
| motion | Time, vestibular floor, compositor budget. Frames still compose first. |
| research | Confidence tiers and method/question fit. Stats stay on #15. |
| engineering | Contracts, rollback, observability. FE/BE share methods, split entries. |
| game | Loop, agency, feel. Engines are values. Legion is a testbed. |
| imaging | Light transport, topology, environment kits, #12 triple gate. |
| vision | Recover meaning from pixels. VLM ≠ Literal. No fake lead-vision hub. |
| visual-qa | Target-user bar, native pixels, measured vs attested, altitudes A–G. |
| illustration | Communication craft; upstream of UI. Not a second foundations file. |
| architecture | Built environment QA + #01. Explicitly not game space. |

Mapped only (no YAML): product, data, security. Accessibility is a lens.

## 4. Cross-domain combos (load two constitutions)

| Job | Load |
|---|---|
| Screen in a DS | ux-ui + design-systems |
| Animated UI | motion + ux-ui |
| Game environment | imaging + game (not architecture) |
| Literal UI recreation | visual-qa + ux-ui |
| Photoreal flythrough | imaging + visual-qa |
| CV on our renders | vision + visual-qa |
| FE implementing DS | engineering + design-systems |

Do not load the whole index.

## 5. Source watch

Design-systems already has `ds-source-watch`. Other domains list URLs in
`watch[]` as testimony. Hash change is not a law change. Do not auto-edit.

## 6. Working view

Interactive canvas (Cursor, not vault):
`/Users/snds/.cursor/projects/Users-snds-Projects-Workspace/canvases/domain-constitutions.canvas.tsx`

Coverage bars on that canvas are a 2026-09-02 judgment, not a measured benchmark.

## Related

- [[constitution-spec]]  -  shape and bans
- [[domain-constitutions]]  -  index
- [[agentic-ds-context-model]]  -  DS remap this generalizes
- [[13-domain-rigor-stack]]  -  L1–L5
- [[workspace-ontology]]  -  routing
