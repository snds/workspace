---
name: ux-component-library
description: >
  Component-selection and pattern framework distilled from the UX Components dataset
  (62 components, 9 categories, 68 design systems, 1,900+ naming mappings) plus the live
  ux-components MCP. Use this skill for ANY design or UI work — even when the task is
  product/feature work rather than design-system work. Trigger whenever the conversation
  involves: choosing or naming a UI component or pattern; designing a screen, view, page,
  layout, form, flow, or user workflow; deciding between similar components (dialog vs sheet
  vs popover, select vs combobox, toast vs alert vs banner, tabs vs accordion, switch vs
  checkbox vs toggle, tag vs chip vs badge, table vs list, etc.); transliterating headless/
  coded components into Figma components, variants, states, or tokens; building or auditing
  UI; mapping a component's name across design systems (Material, Atlassian, Carbon, Bootstrap,
  Ant, shadcn/Radix, Fluent, Polaris, Spectrum, GOV.UK, and 50+ more); reasoning about
  contextual use, designed intent, anatomy, states, accessibility, or which pattern fits a
  user need. Also trigger on "which component", "what pattern", "how should this work",
  "design this screen", "build this layout", "put this in Figma", component audits, and any
  enterprise/product UI decision. This is the default component-reasoning lens — if the topic
  touches a UI element, pattern, screen, or component name, use it. Also covers authoring and
  documenting components *as data* (anatomy/props/states/examples), code-only props in Figma, the
  token taxonomy & purposeful-vs-aesthetic naming, DESIGN.md authoring + linting + gap-detection,
  AI-ready / agentic design-system setup, and A2UI catalog integration. Complements snds:lead-ux-designer,
  snds:lead-ui-designer, snds:design-engineer, snds:ds-advisor, and snds:figma-canvas-designer.
aliases: [ux-component-library]
tier: spoke
domain: design
hub: lead-ux-designer
prerequisites: [lead-ux-designer]
framework: "09-component-and-pattern-framework"
spec_version: "2.1"
---

# UX Component Library & Pattern Framework

A visual, structural, contextual, and intent-based framework for choosing the right UI
component or pattern for any design task — and for translating between code, design systems,
and Figma. Built from a complete read-through of the **ux-components.com** dataset.

## What this gives you

- **62 canonical components** across **9 categories**, each with its designed intent,
  when-to-use, when-to-avoid, states, anatomy, and cross-system aliases →
  [`references/component-inventory.md`](references/component-inventory.md)
- **Decision frameworks, naming-divergence lessons, design-system philosophies, universal
  accessibility laws, and application playbooks** →
  [`references/cross-system-patterns.md`](references/cross-system-patterns.md)
- **Authoring components *as data*** — anatomy/props/states/examples, the 3-bucket prop model,
  code-only props in Figma, the 8-section spec, the canonical state model →
  [`references/component-authoring.md`](references/component-authoring.md)
- **Tokens & naming** — the Namespace→Object→Base→Modifier grammar, purposeful-vs-aesthetic
  naming, the 9 authoring principles, DTCG → [`references/tokens-and-naming.md`](references/tokens-and-naming.md)
- **AI-ready & agentic setup** — the AI-ready checklist, 3-tier agent context, DESIGN.md
  authoring + lint + gap-detection, AI doc-generation, A2UI integration →
  [`references/ai-ready-design-systems.md`](references/ai-ready-design-systems.md)
- A **live MCP** (`ux-components`) for current, queryable specifics.

## The framework & the delivery system

This skill is the **procedural / workflow layer** of a five-part system governed by the
**Component & Pattern Framework** ([[09-component-and-pattern-framework]], workspace `01-frameworks/`)
— the *why* (universal schema, taxonomy, laws). The layers, and when to reach for each:

| Layer | Use it for |
|---|---|
| **Framework** (the hub) | the durable *why* — schema, taxonomy, decision trees, cross-cutting laws |
| **This skill** (procedure) | *how to operate* — run the trees, author/document components, the playbooks |
| **`ux-components` MCP** | per-component data on demand (intent/states/anatomy/aliases) |
| **`DESIGN.md`** | a project's portable *visual identity* (tokens + brand prose) |
| **`AGENTS.md` + lint** | enforcement (import-don't-reimplement, a11y, honor DESIGN.md) |

Wolosin's rule governs the split: *context is intent* — deliver the right intent, at the right
moment, in the right form. Heavy per-component depth stays **on demand** (MCP); the durable why
stays in the **framework**; only the lean visual snapshot lives in **`DESIGN.md`**.

## How to use it (read order)

1. **Name the question.** Map the need to one of the 9 categories — each answers one question
   (Action=do, Form=collect, Navigation=go/command, Feedback=tell, Data Display=show,
   Layout=group, Overlay=temporary surface, Disclosure=hide-until-asked, Content=media).
   See §1 of `cross-system-patterns.md`.
2. **Run the decision tree** for that cluster (§2 of `cross-system-patterns.md`) — overlays,
   single-choice, binary, messaging, loading, labels, data display, content organization,
   menus/nav. The trees encode the load-bearing thresholds (≈5 / ≈15 options, instant vs
   deferred, modal vs non-modal, known vs unknown duration).
3. **Pull the component detail** from `component-inventory.md` (intent, states, anatomy,
   aliases, pitfalls) — or query the live MCP for current/exhaustive data.
4. **Apply the universal laws** (§5) — accessibility, the 300ms rule, one-primary-per-section,
   lowest-intensity-that-works, and the full state matrix as a QA checklist.

## The decision shortcuts (memorize these forks)

- **Overlay** = modality × trigger: Tooltip → Popover (when interactive) → Dialog (when blocking)
  → Alert Dialog (when irreversible); Sheet/Drawer when keeping context with no decision.
- **Single-choice** = option count: Radio (2–5) → Select (5–15) → Combobox (>15 / unknown name).
- **Binary** = when it applies: Switch (instant) / Checkbox (form-submitted) / Toggle (toolbar, stateful).
- **Messaging** = escalation ladder: Toast (ignorable) → Alert (persistent) → Banner (prominent)
  → Alert Dialog (blocking). Use the lowest rung.
- **Loading** = known duration?: Progress (yes) / Spinner (no, inline) / Skeleton (initial, known layout) / Meter (static range).
- **Labels** = interactivity: Badge (numeric/status) / Tag (textual) / Chip (interactive token).
- **Menus** = navigate vs command: Dropdown/Context/Menubar use *menu* semantics; Select/Combobox use *form-input* semantics. Never cross them.

## Live MCP tools (server: `ux-components`)

Use when you need current or exhaustive data; use the static refs for fast reasoning.

- `lookup "<component>"` — full guidance, or `lookup "what is a toast called in Atlassian"` for naming.
- `recommend "<plain scenario>"` — best component + alternatives + states + watch-outs.
- `compare "a vs b vs c"` — live decision table (regenerate any tree above).
- `lookup "<category> components"` — full category roster (e.g. "Form components").
- `smart_query "<anything>"` — auto-routes to the right tool.

## Working modes

- **Choosing patterns for product/feature work:** run the trees; default to the lowest-intensity
  component; cover every state before "done."
- **Designing workflows screen by screen:** see playbook §7.1 — name the job, pick the one
  primary action, resolve each input and each data display, then transitions/messaging, then
  wayfinding, then complete the empty/loading/error states.
- **Building layouts:** see §7.2 — Cards for one-subject groups, whitespace before Separator,
  Scroll Area for overflow, overlays only for temporary surfaces.
- **Transliterating headless code → Figma:** see §6 — States→variant props, Anatomy→layers/slots,
  Variants→axes, Tokens→Figma variables; name by the team's vocabulary but keep the canonical
  concept in the description, and carry the when-to-use/avoid into the component description.
  Pair with `snds:figma-canvas-designer` + `figma-use` for canvas writes and `figma-code-connect`
  for code mapping.
- **Auditing UI:** see §7.3 — check lowest-intensity correctness, the state matrix, semantics
  (is the "menu" really a Select? the "toggle" really a Switch?), and naming drift.
- **Authoring / documenting a component (as data):** see `component-authoring.md` — define it once
  as `anatomy / props / default / variants / examples`; tag every prop Figma-only / shared / code-only;
  model states as separate concerns (`state` enum `rest|hover|active|focus` + booleans + `validation`);
  carry code-only props in the hidden `Code only props` Figma layer; harvest examples from an
  `Examples` section. Write the 8-section spec (how to make) separately from usage guidelines (how to use).
- **Naming tokens & components:** see `tokens-and-naming.md` — assemble names from the
  Namespace→Object→Base→Modifier grammar; default to **purposeful** over aesthetic naming; never mix
  both into one enum; promote tokens outward only after reuse; keep components on the semantic layer.
- **Authoring a DESIGN.md (and the gap-detection protocol):** see `ai-ready-design-systems.md` §3 +
  framework §12a — when UI work starts on a project with no visual-identity anchor, run detect→judge→act
  and **self-prompt** to author one from real tokens (never invent); specific reference > adjectives;
  negative constraints are first-class; lint with `npx @google/design.md lint`; keep it lean and defer
  component semantics to the framework + MCP.
- **Making a system AI-ready / agentic:** see `ai-ready-design-systems.md` §1–2, §4 — score against the
  4-pillar checklist; ship `*.meta.json` per component; JSON over prose; AI drafts docs, humans verify
  (the Overview→Usage→Variants→Behaviors→A11y→Content→TL;DR template).
- **Integrating A2UI:** see `ai-ready-design-systems.md` §6 — project the canonical taxonomy into an
  A2UI **catalog**, serve component definitions + `instructions` from the MCP, and style the renderer
  from DESIGN.md tokens (A2UI has no token system of its own). Note coverage gaps (combobox, popover,
  toast… have no basic-catalog equivalent).

## Critical caution: names lie, behavior doesn't

The same name means different components across systems ("Toggle"=Switch in Atlassian/Carbon;
"Select"=Combobox in Atlassian; "Tag"=Badge in Carbon), and the same component has many names
(Sheet = Drawer / Offcanvas / Tray / Flyout / Side Panel). Always resolve a named component to
its **canonical behavior** (modality, trigger, semantics, when-the-change-applies) before
reasoning. Use MCP `lookup` to translate any specific system's vocabulary. Full divergence map:
§3 of `cross-system-patterns.md`.

## Coverage caveat

Components mapped to many systems are universal and safe to assume (Button, Dialog, Checkbox,
Tabs, Table, Tooltip). Components mapped to few systems are specialized — verify the target
system has them or plan to compose them: Hover Card, Color Picker, Scroll Area, Timeline, Meter,
Data Table, Tree View, Rating. The dataset also does NOT model Command Palette, Aspect Ratio,
Resizable, dedicated Drawer/Multi-select/Video — compose from the nearest primitive and note the gap.

## Related
- hub → [[lead-ux-designer]]
