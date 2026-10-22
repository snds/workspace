---
title: Design, UX and design-system skills — overlap assessment and proposed architecture
status: decided
date: 2026-10-22
tags: [skills, design-systems, ux, architecture, routing, harness]
related_projects: [19-workspace-brain, 26-synapse]
---

# Design, UX and design-system skills: overlap assessment

**Answer.** Yes, rearchitect, but by **consolidating ownership**, not by adding hubs. Every
subspecialty should have exactly one home, reachable by its own triggers. Today most
subspecialties are present but hard to reach: in a battery of 19 everyday asks, only **2** loaded
the skill that owns the answer, and **9** loaded nothing. The worst knot is design systems:
**six hubs** plus 44 vendored skills share one area, and the hub that answers most design-system
asks is 6,743 words long.

Asked by Sean, 2026-10-22, after the component-spec harness showed the design-system skills
scattered across hubs. **Decided and built the same day** (see [Outcome](#7-outcome-2026-10-22));
sections 1–6 are the assessment as it was proposed.

---

## 1. What was measured

- **The design domain:** 125 skills in `domain: design` (25 hubs), plus the accessibility hub and
  the 44 skills bundled under `design-system-ops/skills/` (outside the registry).
- **Concept coverage:** for 18 subspecialties, which skills claim them, by description and
  triggers.
- **Routing battery:** 19 ordinary subspecialty asks through `skill-loadset.py` (Layer 0, the same
  router every surface and the harness compiler use).
- **Size:** words per hub (a proxy for tokens each time it loads).

## 2. Routing battery: subspecialties can't be reached

| Ask | Owner today | Loaded |
|---|---|---|
| Enumerate the states this combobox needs | `ux-design-systems` | nothing |
| Should this be a variant or a prop (a phrase in `ds`'s own description) | `ds` / `ux-design-systems` | nothing |
| Help me name these semantic tokens | `token-architecture` | `design-engineer` |
| Is this token architecture sound | `token-architecture` | `ds-advisor` (6,743 words) |
| Dialog vs sheet vs popover | `ux-component-library` | nothing |
| Define chart tokens for our design system | `infod-design-system-patterns` | `ds-advisor` |
| Write the empty state copy | `ux-writing` | nothing |
| Navigation for a complex enterprise app | `ia-navigation-systems` | nothing |
| Plan the deprecation of this component | `design-system-ops` | nothing |
| Generate a design system for shadcn and Tailwind | `ds-generation-pipeline` | `ds-advisor` + `ds-generation-pipeline` |
| Focus order for this dialog | `a11y-*` | nothing |
| Is this modal accessible | `ux-accessibility` / `a11y-*` | nothing |
| Set up Code Connect for the button | `figma-code-connect` | ✓ `figma` → `figma-code-connect` |
| Variant or boolean property in Figma | `figma-modes-for-variants` | `design-engineer`, `figma`, `figma-canvas-designer` |
| Design the drag-and-drop reordering interaction | `ux-interaction-design` | nothing |
| Dark mode palette for this dashboard | `uid-color-for-ui` | `lead-ui-designer` (hub only) |
| Layout for an executive dashboard | `infod-dashboard-patterns` | `found-composition` |
| Make our design system AI-ready | `ai-design-systems` | `ds-advisor` |
| Component API for a data table | `design-engineer` / `ux-design-systems` | ✓ `design-engineer` |

**Why:** many spokes carry no `triggers` of their own (their trigger phrases live only in prose
descriptions, which Layer 0 doesn't read), and broad hubs claim the words first. Agents with the
descriptions in context may still find a spoke by reading, but the deterministic router, the
harness compiler and every surface without the descriptions can't.

## 3. Where the overlaps are

### Design systems: six hubs for one area

| Skill | Tier | Words | Claims |
|---|---|---|---|
| `ds` | hub, command hub | 1,063 | Decisions, token architecture, component anatomy, governance, handoff, DDRs |
| `ds-advisor` | hub | 6,743 | Strategy, audits, triage, tokens, anatomy, variants and states, handoff, a11y rationale, stakeholders |
| `design-system-ops` | hub, command hub | 421 (+44 bundled) | Token audits, drift, governance, deprecation, health |
| `design-engineer` | hub | 3,202 | Component architecture and API, tokens, Figma authoring, governance, React patterns |
| `ds-generation-pipeline` | hub | 1,260 | Generating DS artifacts per stack |
| `gen-manifest` | hub | 1,270 | Order of operations for DS generation |

Also claiming design-system subspecialties: `ux-design-systems` (variants, states, behavior, API;
2,514 words, under `lead-ux-designer`), `ux-component-library` (component selection),
`figma-component-generation` / `figma-modes-for-variants` / `figma-ds-generation-pipeline` (4,844
words), `infod-design-system-patterns` (charts in a DS), `token-architecture` and
`ai-design-systems` (under `ds-advisor`).

**Effect:** three hubs answer "tokens"; four answer "variants and states"; three answer
generation. None of the six declares itself the area's hub, so the harness compiler had to guess
(it found `ds-advisor` by words).

### Duplicated subspecialties across UX and the specialist hubs

| Subspecialty | Specialist home | Duplicate |
|---|---|---|
| Information architecture | `lead-information-architect` (7 `ia-*` spokes) | `ux-information-architecture` (2,425 words) |
| Data visualization | `lead-information-designer` (7 `infod-*`) | `ux-data-visualization` (2,562 words) |
| Accessibility | `lead-accessibility-architect` (7 `a11y-*`) | `ux-accessibility` (2,813), `a11y-visual` (2,571), `motion-accessibility`, bundled `accessibility-per-component` |
| Type | `lead-type-designer` (type design) | `type` hub (type systems and typesetting) |
| Motion | `lead-motion-designer` (9 spokes) | `motion` hub (implementation) |

The type and motion pairs are a **doctrine hub vs. implementation command hub** split, which is
fine if stated; today neither says which owns what. Colour and typography appearing in
foundations, UI, graphic and info design is **intended layering** (foundation → application), not
duplication.

### A prefix collision

`ds-` means **data science** (`ds-experimentation`, `ds-ml-engineering`, nine more under
`lead-data-scientist`) and **design system** (`ds`, `ds-advisor`, `ds-source-watch`,
`ds-generation-pipeline`). The compiler would have added `ds-anatomy` and friends to the
collision. Renames are refused by the workspace rules (paths are hard-coded), so new design-system
spokes need another prefix.

## 4. Proposed architecture

**Principles**

1. **One home per subspecialty.** A discipline hub owns its spokes; others link with `related`,
   never a second copy.
2. **Three kinds of hub, each declared:** *discipline* hubs own doctrine and spokes (UI, UX, IA,
   information design, design systems, accessibility, motion, type, graphic, icon, 3D);
   *command* hubs own a verb grammar over tooling and defer to the discipline for doctrine
   (`figma`, `motion`, `type`, `redesign`, `design-system-ops`); *lenses* judge after the work
   (`lead-visual-qa`, `visual-qa-*`, `a11y-visual`).
3. **Thin hubs.** A hub routes and holds the area's standards in about 1,500 words or fewer; depth
   lives in spokes that load only when asked for.
4. **Every subspecialty spoke has its own triggers**, so an ask reaches it directly (the load chain
   still brings its hub and foundation first).
5. **The areas are written down.** A design `domain` node lists each area and its hub (model v1's
   `domain.areas`); the router, the harness resolver and the compiler read it before guessing.

**Design systems, concretely**

| Today | Proposed |
|---|---|
| `ds`, `ds-advisor` both hubs | **`ds` is the design-system hub** (area `design-system`, command verbs). `ds-advisor`'s 6.7k words split: its routing moves to `ds`; strategy, triage and stakeholder work become one spoke; its knowledge pointers stay as `related` |
| `ux-design-systems` under UX | **Re-homed under `ds`** as the component-spec spoke: variants, states, behavior, API. This is what the component-spec harness's c2, c3 and c6 need: one move instead of three new drafts |
| `token-architecture`, `ai-design-systems`, `canonical-docs-voice`, `ds-source-watch` under `ds-advisor` | Under `ds` |
| `design-system-ops` (hub + 44 bundled) | A command spoke of `ds`: the ops wrapper over the vendored pack (governance, audits, deprecation), keeping its `defers_to` |
| `ds-generation-pipeline` + `gen-manifest` | One generation spoke under `ds` (the manifest becomes its order-of-operations section); `figma-ds-generation-pipeline` stays under `figma` for Figma mechanics |
| `design-engineer` as a hub | A **lens** for design × code (cross-cutting), not an owner of tokens, governance or Figma authoring; its Figma triggers move to `figma` |
| `ux-component-library` | Stays under UX (choosing components is a UX call), `related` to `ds` |
| `infod-design-system-patterns` | Stays under information design, `related` to `ds` |

**The other duplicates:** fold `ux-information-architecture` into `lead-information-architect`,
`ux-data-visualization` into `lead-information-designer`, and `ux-accessibility` into the `a11y-*`
spokes (each kept as an alias so links survive), leaving `lead-ux-designer` as the hub for
interaction, flows, research synthesis, writing and service design. Write one line in `type` and
`motion` saying they're the implementation command hubs and defer to their discipline hubs.

## 5. How this lands (each step reviewed, nothing deleted)

| Phase | Work | Proves |
|---|---|---|
| 0 | The 19-ask battery added to `skill-routing-cases.jsonl` as expected routes | It fails today (2 of 19) |
| 1 | Design-system cluster: `ds` as hub with `area: design-system`; re-home spokes; split `ds-advisor`; triggers on every spoke | DS asks in the battery reach their spoke; supply for `design-system.component-spec` rises from 5 of 12 |
| 2 | Duplicates folded (IA, dataviz, accessibility), aliases kept, originals archived with provenance | No dangling link; the battery holds |
| 3 | A design `domain` node with its areas; a generated subspecialty index | The compiler and resolver find every area's hub without guessing |
| — | Measure | Battery 17 of 19 or better; words loaded for a typical DS ask down from about 7,250 (design-foundations + ds-advisor) to under 3,000 |

Archiving, splitting and re-homing need Sean's sign-off under the workspace rules; every step is a
reviewed change with the rebuild and validators green.

## 6. Decisions for Sean

1. **Rearchitect along these lines?** (Recommended.) Or only the routing fixes (triggers on
   spokes), leaving ownership as it is.
2. **`ds` or `ds-advisor` as the design-system hub?** Recommended `ds`: it's already the command
   hub and a fifth the size; `ds-advisor`'s depth moves into spokes.
3. **The new design-system spoke prefix,** given `ds-` is data science: `dsys-`, `system-`, or
   keep `ds-` and accept the collision.
4. **The component-spec plan:** re-home `ux-design-systems` under the design-system hub (one
   move) instead of drafting `ds-anatomy`, `ds-variants` and `ds-component-api`. Recommended.

## 7. Outcome (2026-10-22)

Sean: "merge both and rearchitect, ds as hub, use dsci- for data science to remove the "ds-"
collision. ds- should ALWAYS refer to design systems. If other "DS" domains materialize, refer to
"dsci-" as guidance for how to setup skill prefixes. Yes move ux-design-systems under the main
design-systems hub."

| Decision | Answer | Built |
|---|---|---|
| 1. Rearchitect? | Yes | Phases 0–3 of section 5 |
| 2. Which hub | `ds` | `area: design-system`; `ds-advisor` a spoke (4,158 words; visual foundations moved to its `references/`) |
| 3. Prefix | Keep `ds-` for design systems; data science renamed `dsci-` | Ten spokes renamed; [[decision-skill-prefixes]] |
| 4. Component-spec plan | Re-home `ux-design-systems` | Now `ds-component-spec` under `ds` (alias kept) |

**Measured after:** battery 19 of 19 (was 2); a token ask loads 2,983 words (was about 7,250);
component-spec supply 75% before any plan, with no new spokes needed. Every area and its hub:
[skill-areas](../../../02-shared-references/skill-areas.md). Decision record:
[[decision-design-skill-architecture]].

## Related
- [[13-domain-rigor-stack]] · [[skill-frontmatter]] · [[ds-advisor]] · [[ds]] · [[lead-ux-designer]]
