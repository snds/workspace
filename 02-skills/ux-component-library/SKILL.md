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
  touches a UI element, pattern, screen, or component name, use it. Complements snds:lead-ux-designer,
  snds:lead-ui-designer, snds:design-engineer, snds:ds-advisor, and snds:figma-canvas-designer.
aliases: [ux-component-library]
tier: spoke
domain: design
hub: lead-ux-designer
prerequisites: [lead-ux-designer]
spec_version: "2.0"
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
- A **live MCP** (`ux-components`) for current, queryable specifics.

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
