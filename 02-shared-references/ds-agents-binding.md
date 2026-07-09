---
title: Design-System AGENTS.md Binding
tags: [reference, design-systems, agents, ai-context]
created: 2026-06-17
links:
  - "[[09-component-and-pattern-framework]]"
  - "[[ux-component-library]]"
---

# Design-System `AGENTS.md` Binding

The **enforcement layer** of the Component & Pattern system ([[09-component-and-pattern-framework]]).
It costs ~0 tokens at rest, points agents at the other layers, and prevents the failure modes the
framework is built around (re-implementation, naming drift, dropped states, color-only status).

Drop the block below into a project's root `AGENTS.md` (and/or `.cursor/rules`, `CLAUDE.md`). It is the
**Constraints** intent type in Wolosin's model — deterministic guardrails + routing + trust levels.

---

## The block (copy-paste)

```markdown
## Design system context

**Routing — load the right layer for the job:**
- The *why* (component schema, taxonomy, decision trees, laws) → the Component & Pattern Framework.
- *How to operate* (choose, author, document) → the `ux-component-library` skill.
- Per-component data (intent / states / anatomy / aliases) → query the `ux-components` MCP **on demand**.
- This project's *visual identity* (tokens + brand prose) → `./DESIGN.md`.

**Always-on rules (foundations — never truncate these):**
- Resolve any component name to its CANONICAL BEHAVIOR before using it. Names lie; behavior doesn't.
- Choose the LOWEST-INTENSITY component that works; exactly one primary action per section.
- Cover every state: default / hover / focus / disabled, plus filled / error / loading / empty / selected
  where relevant. Model states as separate concerns (`state` enum + `disabled`/`readonly` booleans + `validation`).
- IMPORT existing components; never re-implement. Design↔code binding via Code Connect.
- Honor `./DESIGN.md` tokens. Components consume the SEMANTIC token layer only — never raw primitives or hex.
- If no `DESIGN.md` exists and UI work is starting, run the gap-detection protocol (framework §12a) and
  self-prompt to author one from real tokens (never invent values).
- Accessibility is non-negotiable: visible labels, focus management + return, correct ARIA roles,
  component-specific keyboard patterns, no color-alone, WCAG 2.2 AA.
- Work WITHIN this project's system: if it lacks a token/feature you need, derive minimally inside
  its constraints and record the gap (backlog / Known Gaps / DDR) — never import another design
  system's conventions to fill it. Token gaps are backloggable; a11y compliance is never deferred.

**Trust levels:**
- Deterministic (trust): MCP data, DESIGN.md tokens, Code Connect mappings, lint output.
- Generative (verify): prose rationale, AI-drafted docs, AI-as-user A/B results (directional only).

**Validation (≈0 token cost):**
- `npx @google/design.md lint DESIGN.md` — token refs, WCAG contrast, section order.
- Frontend lint rules enforce token usage + a11y for humans and agents alike.
```

---

## Notes

- **Three-tier architecture this assumes:** always-on foundation rules (above) + on-demand MCP for
  components + this `AGENTS.md` as the orchestration/governance layer. (Framework §11; `ai-ready-design-systems.md` §2.)
- **Why it works:** structured, deterministic routing beats a single always-loaded context dump — the
  configuration Atlassian's field test found *beat* a monolithic `DESIGN.md` on tokens, time, and correctness.
- **Per-project tailoring:** add the project's component import root, the DESIGN.md path if non-standard,
  and any project-specific anti-patterns (e.g. for Centric C8: "don't default every workflow to a data table").
- **Keep it short.** This block is guardrails + routing, not documentation. Depth lives in the framework,
  the skill references, and the MCP.
