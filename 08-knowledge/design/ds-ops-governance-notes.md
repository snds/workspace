---
tags: [design, design-system, governance, tokens, operations, drift]
created: 2026-08-03
updated: 2026-09-02
status: working
confidence: medium
sources: [03-skills/design-system-ops/SKILL.md, 03-skills/design-system-ops/knowledge-notes/, 01-frameworks/09-component-and-pattern-framework.md, 01-frameworks/06-qa-operating-model.md, AGENTS.md]
related_skills: [design-system-ops, ds-advisor, design-engineer, ux-component-library, fe-design-tokens, figma-source-audit]
related_projects: []
relations:
  builds-on: ["[[radix-derived-color-system]]", "[[figma-tailwind-token-pipeline]]"]
  relates-to: ["[[centric-plm-design-system]]", "[[enterprise-saas-design-patterns]]", "[[figma-ds-surface-authoring]]", "[[llm-safe-design-system-expressiveness]]"]
---

# Design system ops: the workspace position on governance

## For future agent
- **TL;DR:** the workspace-side companion to the [[design-system-ops]] hub. The pack's 40+ nested
  skills are **vendored method**; this note holds what *we* hold about running a system, and it is
  what wins when the two disagree. Read it before any audit, drift check, deprecation, or
  governance review.
- **Key claims:**
  - *Timeless:* an audit is a diagnostic, not a mandate. Audit the target system on its own terms
    and backlog its gaps; do not silently rewrite it toward the tool's preferences.
  - *Timeless:* tier leakage (a component or semantic layer reaching past its tier to a raw value)
    is the recurring token defect, and it is a governance failure before it is a naming failure.
  - *Timeless:* a deprecation without a named replacement, a codemod, and comms is not a
    deprecation, it is an outage with a schedule.
  - *Pointer:* operation grammar and command routing live in [[design-system-ops]]; the universal
    component schema in [[09-component-and-pattern-framework]].
- **As of:** 2026-08 · **Status:** current (seeded from doctrine plus prior token-pipeline work)

---

## Why this note exists

`03-skills/design-system-ops/` is a 4.8 MB vendored pack. Its `knowledge-notes/` directory is
useful method background but carries **no provenance from work done here**, is not indexed in this
vault, and would be overwritten by an upstream sync. Durable insight therefore has to live on this
side of the boundary. This note is that anchor.

Marked `working` / `confidence: medium`: the token-architecture claims below rest on real prior
work ([[radix-derived-color-system]], [[figma-tailwind-token-pipeline]]); the governance claims are
doctrine awaiting the first full audit cycle run through the hub.

---

## Operations are a separate discipline from authoring

The pack's core insight is worth keeping: the work that keeps a system alive (audits, drift,
deprecation, adoption reporting, onboarding, governance documentation) is structurally different
from the work of designing and building components, and it fails quietly when it has no owner and
no cadence. The workspace splits it accordingly:

| Question | Owner |
|---|---|
| What state is the system in, and how do we run it? | [[design-system-ops]] |
| Which system, which primitives, which stack, what should the token architecture be? | [[ds-advisor]] |
| What should this component be, and how is it built? | [[design-engineer]], [[ux-component-library]] |

Ops audits **against** strategy. It does not set strategy. When an audit finding implies a strategy
change, that is a hand-off to [[ds-advisor]], not a unilateral fix.

Vendored method added 2026-09-02 (upstream 2026-08-22): `theme-audit` (mode coverage +
component-tier propagation) and `docs-coverage` (code as SSOT vs Storybook/docs). Grammar rows
live on the [[design-system-ops]] wrapper. Do not promote pack `knowledge-notes/` over this
note. Expressiveness / "CI is the contract" lives in [[llm-safe-design-system-expressiveness]],
not in the ops pack.

## Token architecture: what we already know

Three claims here are validated by real work in this workspace, not borrowed from the pack:

- **A single theme control point beats two.** Flat primitives plus themed semantics, with one place
  that swaps values. Two control points produce a split brain that no audit can resolve
  ([[figma-tailwind-token-pipeline]]).
- **Governance layers sit above primitives; they do not mutate them.** Contrast policy (APCA) is
  enforced as governance over the semantic layer rather than by bending the primitive ramp, which is
  what keeps the ramp reusable ([[radix-derived-color-system]]).
- **The design tool surfaces a subset of the code contract, deliberately.** Full compatibility in
  CSS, a curated design-surface subset in Figma. An audit that flags the gap as drift is
  misreading the contract. Confirm which layer owns a value before calling it a violation
  ([[figma-tailwind-token-pipeline]]).

Tier leakage is the defect to look for first: a component token bound to a raw hex, a semantic token
skipped entirely, or a one-off value introduced because the semantic layer had no slot for the case.
The last of those is a **backlog item against the system**, not a violation by the author.

## Drift is a signal, not a naughty list

Drift measures the distance between what the system offers and what teams actually needed. Read it
that way. A cluster of divergence in one area usually means a genuine gap in the system, and
reporting it as non-compliance both misses the finding and costs the goodwill you need to fix it.
This is [[06-qa-operating-model]]'s system-context fidelity rule applied to governance: work within
the target system, name its gaps, and route them.

## Deprecation: the anti-zombie rule has a design-system twin

The workspace contract forbids leaving a file superseded-but-live: archive with provenance,
generate the replacement, repoint every reference (see [[AGENTS]] and
[[08-workspace-contribution-framework]]). Component deprecation is the same shape:

1. Name the replacement and prove it covers the real usage, not the documented usage.
2. Ship the codemod, or accept that the migration will not happen.
3. Communicate before the removal, with the version and the date.
4. Only then remove.

A component marked deprecated in docs while still shipping, imported, and receiving fixes is a
zombie: consumers cannot tell which state it is in, so they do nothing.

## Audits are outputs, so they pass the output gate

An audit report, a scored health dashboard, and a stakeholder brief are deliverables. They go
through [[06-qa-operating-model]]'s pre-output gate and [[05-last-mile-craft-framework]] like any
other artifact. Specifically: severity honestly rated (do not inflate to look thorough or deflate to
be polite), findings expressed as remediations rather than observations, and the reader's actual
question answered in the first paragraph.

**Context profile is load-bearing here.** These operations mostly touch employer repositories. Under
`centric-engineering` there is no auto-commit, no self-merge, and no direct push: an audit is a
review artifact and a codemod is a proposal. Resolve the profile before acting, per [[AGENTS]].
