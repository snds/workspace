---
title: A2UI Canonical Catalog — taxonomy projection
tags: [reference, design-systems, a2ui, agents, ai-context]
created: 2026-06-17
links:
  - "[[09-component-and-pattern-framework]]"
  - "[[ux-component-library]]"
---

# A2UI Canonical Catalog — a projection of the 62-component taxonomy

[`canonical-catalog.json`](canonical-catalog.json) is an **A2UI catalog** that projects the
Component & Pattern Framework's taxonomy onto Google's [A2UI](https://github.com/a2ui-project/a2ui)
agent-to-UI protocol. It is the concrete realization of framework **§11a** and skill ref
**`ai-ready-design-systems.md` §6**: A2UI deliberately leaves the *component vocabulary*, the
*per-component guidance*, and the *styling* unspecified — this catalog fills all three.

## What it does

- **Restricts agents to a trusted vocabulary.** An agent bound to this `catalogId` may only emit
  the 29 components defined here (15 from A2UI's Basic Catalog + 14 added) — not arbitrary UI.
- **Carries the framework's intelligence.** The top-level `instructions` field encodes the
  9-category model, the decision shortcuts, the async triad, name-resolution, and the accessibility
  laws. Each component's `description` carries its **canonical intent + when-to-use/avoid** — sourced
  from the `ux-components` MCP. This is what makes the agent pick the *right* component, not just a valid one.
- **Defers styling to the renderer.** A2UI has no token system; components expose only semantic
  `variant` hints. A project's **`DESIGN.md` tokens** become the renderer's CSS-variable defaults
  (the seam in §"Theming" below). Brand identity rides in `surfaceProperties`.

## How it plugs in (the four seams)

1. **Catalog ⟵ taxonomy** — this file (the mapping table below).
2. **MCP authors + serves it** — the `ux-components` MCP supplies each component's `description`
   `instructions` and is queried at generation time to choose the right component.
3. **DESIGN.md themes the renderer** — tokens → CSS variables; e.g. C8's `--sem-primary` styles
   every `Button variant:"primary"`. The agent never sends colors.
4. **The skill validates** — the `ux-component-library` skill owns the prompt → generate → validate loop.

## The full mapping (all 62 canonical components → A2UI)

**Legend:** **basic** = A2UI Basic Catalog · **added** = defined in this catalog · **composed** =
build from primitives (Row/Column/Button/Text + variants) · **gap** = no clean equivalent yet; extend the catalog or note the limitation.

| Category | Canonical | → A2UI | Status |
|---|---|---|---|
| Action | button | `Button` | basic |
| Action | toggle | `Button` (stateful) | composed |
| Action | toggle-group | `Row` of `Button` / `Tabs` | composed |
| Action | toolbar | `Row` of `Button` | composed |
| Form | input | `TextField` | basic |
| Form | textarea | `TextField variant:longText` | basic |
| Form | label | (intrinsic `label` prop) | n/a |
| Form | checkbox | `ChoicePicker variant:multipleSelection` | basic |
| Form | radio-group | `ChoicePicker variant:mutuallyExclusive` | basic |
| Form | select | `Select` | **added** |
| Form | combobox | `Combobox` | **added** |
| Form | switch | `Switch` | **added** |
| Form | slider | `Slider` | basic |
| Form | search | `TextField variant:search` | basic |
| Form | number-input | `TextField variant:number` | basic |
| Form | date-picker | `DateTimeInput variant:date` | basic |
| Form | time-picker | `DateTimeInput variant:time` | basic |
| Form | calendar | `DateTimeInput` (inline) | composed |
| Form | rating | `Row` of `Icon` + action | composed |
| Form | file-upload | — | gap |
| Form | color-picker | — | gap |
| Form | form | `Column` of fields + `Button` | composed |
| Navigation | link | `Text`/`Button variant:ghost` + action | composed |
| Navigation | tabs | `Tabs` | basic |
| Navigation | breadcrumb | `Row` of `Text` + actions | composed |
| Navigation | pagination | `Row` of `Button` | composed |
| Navigation | dropdown-menu | `Popover` + `List` of `Button` | composed |
| Navigation | navigation-menu | `Row`/`Column` of links | composed |
| Navigation | context-menu | — (no right-click in declarative stream) | gap |
| Navigation | menubar | — | gap |
| Navigation | stepper | `Row` of `Icon`+`Text` | composed |
| Feedback | alert | `Alert` | **added** |
| Feedback | toast | `Toast` | **added** |
| Feedback | banner | `Alert` (full-width) | **added** |
| Feedback | spinner | `Spinner` | **added** |
| Feedback | empty-state | `EmptyState` | **added** |
| Feedback | progress | — (compose; renderer) | gap |
| Feedback | skeleton | — (renderer loading concern) | gap |
| Feedback | meter | — | gap |
| Data Display | avatar | `Avatar` | **added** |
| Data Display | badge | `Badge` | **added** |
| Data Display | tag | `Tag` | **added** |
| Data Display | chip | `Tag removable:true` | **added** |
| Data Display | list | `List` | basic |
| Data Display | table | `Table` | **added** |
| Data Display | data-table | `Table` (+ bound rows, functions) | **added** |
| Data Display | tree-view | — | gap |
| Data Display | timeline | `Column` of `Row`(`Icon`+`Text`) | composed |
| Layout | card | `Card` | basic |
| Layout | separator | `Divider` | basic |
| Layout | scroll-area | (renderer concern) | n/a |
| Overlay | tooltip | `Tooltip` | **added** |
| Overlay | popover | `Popover` | **added** |
| Overlay | dialog | `Modal variant:dialog` | basic |
| Overlay | alert-dialog | `Modal variant:confirm` | basic |
| Overlay | hover-card | `Popover` (no hover in protocol) | gap |
| Overlay | sheet | `Modal`/`Popover` (no edge panel) | gap |
| Disclosure | accordion | `Accordion` | **added** |
| Disclosure | collapsible | `Accordion variant:single` | **added** |
| Content | image | `Image` | basic |
| Content | icon | `Icon` | basic |
| Content | carousel | `Row` (scroll-snap) | gap |

**Coverage:** of 62 canonical components — **~17 map directly** (basic), **~16 added** here, **~17
composed** from primitives, **~12 are gaps** (extend the catalog with a custom component, or render
via the renderer layer). `label` and `scroll-area` are structural/renderer concerns (n/a).

## Theming (DESIGN.md → renderer)

A2UI agents send no colors/sizes — only `variant` hints. Resolve them at the renderer:

```
Button variant:"primary"   →  background: var(--sem-primary);  color: var(--sem-primary-foreground)
Alert  variant:"error"     →  border/bg from var(--sem-destructive) family
Badge  variant:"success"   →  var(--sem-success) (+ icon — never color alone)
```

Export the project's `DESIGN.md` tokens (e.g. C8's `--cds-*` / `--sem-*`) as the renderer's CSS-variable
defaults; set brand identity via A2UI `surfaceProperties` (`iconUrl`, `agentDisplayName`). Because A2UI
v1.0 stripped brand colors from the protocol, **DESIGN.md is the correct and only home for tokens.**

## Extend / validate

- **Add a gap component** by appending a schema under `components` (mirror the `allOf` + `component.const`
  shape) and adding it to `$defs.anyComponent.oneOf`. Source its `description` from the MCP.
- **Functions:** four are defined (`required`, `email`, `length`, `openUrl`); the full A2UI Basic Catalog
  function set (`regex`, `numeric`, `formatDate`, `formatCurrency`, …) can be inherited/added as needed.
- **Validate** with A2UI's own tooling (`a2ui-project/a2ui` → `specification/scripts` / conformance suite)
  against the v1.0 schema. JSON validity + internal ref consistency were checked at authoring time
  (29 components, union resolves, every `component.const` matches its key).

## Caveats

A2UI is an **early preview** (production v0.9.1; v1.0 RC — "expect changes"). It carries only
`accessibility.{label,description}` per component — the deeper a11y/state/anatomy lives in the MCP,
not the wire. Treat this catalog as the *trusted vocabulary + intent* layer; the renderer + DESIGN.md
own the pixels; the framework + MCP own the semantics.
