---
name: ux-design-systems
description: >
  Component design decisions, variant and state coverage, behavior specification, and
  pattern library thinking for enterprise design systems — from the UX design side.
  Use this skill when working on: deciding what variants a component needs, enumerating
  the states a component must cover, defining the interaction contract for interactive
  components, documenting component behavior for engineering handoff, distinguishing
  patterns from components, writing pattern documentation, designing the overflow and
  edge case behavior of components, component API surface decisions (what props to
  expose), or reviewing whether a component design is complete. Also trigger on:
  "what states does this component need", "is this a component or a pattern",
  "how should this component behave when X", "what variants should I create",
  "how do I annotate this for engineers", or any question about the design-side
  decisions in a design system. Token architecture, Figma ops, and DS strategy live
  in `ds-advisor` — route there for those topics.
aliases: [ux-design-systems]
tier: spoke
domain: design
hub: lead-ux-designer
prerequisites: [lead-ux-designer]
spec_version: "2.0"
---

# UX — Design Systems (Component Behavior Layer)

Spoke skill in the `lead-ux-designer` network. Owns the design *decision-making*
layer of design systems: what variants to create, what states to cover, how components
behave, what each component does for the user, and how to specify components for
engineering implementation.

**IMPORTANT SCOPE BOUNDARY**: Token architecture (global → semantic → component
token layers), Figma ops (auto-layout, variables, publish workflows), DDR format,
and DS strategy live in `ds-advisor`. Load `ds-advisor` for those topics.
This spoke owns the UX behavior layer — not the implementation infrastructure layer.

Also does not own: the design/code bridge and implementation patterns (→ `design-engineer`),
ARIA implementation requirements (→ `ux-accessibility` for design spec, `fe-accessibility`
for implementation).

---

## Component Design Decision Framework

Before creating a component, run it through the necessity test. Most unnecessary
components come from skipping this step.

### Necessity test

1. **Is it a reusable interaction pattern, or a one-off layout?**
   - Reusable pattern: appears in 3+ contexts with the same behavior → component candidate
   - One-off layout: unique to a specific screen → compose from existing components, don't create a new one

2. **What is the right abstraction level?**
   - Too specific: a "Product Name Table Row" component only works in one context. The abstraction should be "Table Row" with a slot for content.
   - Too generic: a "Box" component that just wraps a div with padding. This encapsulates nothing useful — it's just a styled div. Not a component.
   - The right level: encapsulates a specific interaction behavior or consistent visual pattern that would be inconsistently implemented without abstraction.

3. **What is the component's minimum viable API surface?**
   Every prop is a promise. A prop that exists must be maintained — renaming or removing it is a breaking change. Minimize the exposed surface:
   - Start with the minimum set of props that makes the component work in its most common case
   - Default everything possible to the most common value
   - Only add a prop when there is a real use case for variation — not "we might need this"

4. **The "good defaults" principle:**
   A component with no props applied should work correctly in the most common case.
   If a component requires 5 required props to render correctly, the defaults are wrong.
   Required props should be limited to the truly necessary (an `id` for a form field,
   a `label` for a button). Everything else should have a sensible default.

---

## Variant Coverage

Variants are not free. Every variant is a maintenance commitment. Create variants
that correspond to real, distinct use cases — not speculative ones.

### Functional variants

Variants that change the component's behavior, not just its appearance. These are
required when the interaction differs based on context.

Examples:
- A `Select` component with single-select vs. multi-select mode (different keyboard behavior, different value storage)
- An `Input` with `type="text"` vs. `type="number"` vs. `type="password"` (different keyboard, different masking)
- A `DatePicker` with a single date vs. date range mode

Functional variants must be documented with their behavioral differences, not just
their visual differences. An engineer reading the spec must understand that single-
select and multi-select have different keyboard interaction models.

### Visual variants

Variants that change appearance without changing behavior. Define these relative to
the design system's visual language, not individually.

| Variant Type | Enterprise Examples | What It Communicates |
|-------------|---------------------|----------------------|
| **Primary** | Solid filled button, prominent alert | The most important action or status on this surface |
| **Secondary** | Outlined button, subtle badge | A supported but non-primary action |
| **Ghost / Tertiary** | Text-only button, minimal border | A low-emphasis action that exists but shouldn't compete visually |
| **Destructive** | Red-tinted button, danger badge | Irreversible or high-stakes action — use sparingly |
| **Branded** | First-level CTA with brand color | Conversion-oriented, marketing-adjacent |

Visual variants are not about aesthetics — they are about communicating relative
importance to the user. A page with three primary buttons has no primary button.

### Size variants

Components that appear in multiple density contexts need size variants. The contexts
where each size applies must be enumerated, not left to designer judgment.

| Size | Density context | Typical height | Use in |
|------|----------------|---------------|--------|
| XS | Inline in dense tables | 24px | Data table actions, tag chips inside cells |
| SM (compact) | Compact density mode, secondary toolbars | 28–32px | Filter chips, compact form fields |
| MD (default) | Default page layouts | 36–40px | Standard forms, primary toolbars |
| LG (comfortable) | Spacious layouts, key CTAs | 44–48px | Hero actions, prominent form sections |

If the design system only has one size: the designer will hand-roll sizes in each
context. This is size variant debt — the inconsistency that accumulates before
anyone defines the system.

### State coverage: the complete matrix

For every interactive component, all states are required. "The designer forgot about
the disabled loading state" is a class of bug that originates in incomplete state design.

| State | Description | Always required? |
|-------|-------------|-----------------|
| **Default** | Component at rest, no interaction | Yes |
| **Hover** | Pointer over the element | Yes for all interactive elements |
| **Focus** | Keyboard focus | Yes — must be visually distinct |
| **Active** | Pressed/activated (momentary) | Yes for clickable elements |
| **Disabled** | Not interactive, present but unavailable | Yes for form elements |
| **Loading** | Async operation in progress | Yes for elements that trigger async actions |
| **Error** | Validation or system error | Yes for form elements |
| **Success** | Confirmation of a completed action | Situational — required for form submits |
| **Selected** | Item is selected in a set | Yes for selectable elements |
| **Readonly** | Value present but not editable | Required for form elements in review contexts |

### Combined states

The failure mode of state design is designing each state in isolation and never
considering combinations. Required combined states to verify for every interactive component:

- **Error + Disabled**: a field that has an error but has been disabled (e.g., by a
  form-level lock). Does the error state override the disabled appearance? Is the
  error still communicated?
- **Loading + Selected**: a selected item in a list that is being processed. Does
  the loading indicator appear on the selected item? Does selection remain visible?
- **Focus + Error**: keyboard focus on an errored field. Does the focus ring compete
  with the error indicator? Are both visible?
- **Hover + Disabled**: does the hover state appear on a disabled element? It should not —
  disabled elements must not respond to hover.

---

## Pattern Library Thinking

### Pattern vs. component distinction

**Component**: a UI element that encapsulates a specific visual and/or interaction pattern.
(Button, Input, Select, Modal, Tooltip)

**Pattern**: a composition of components that solves a recurring design problem.
(Empty state, Filter panel, Inline edit, Confirmation dialog, Detail sidebar, Step form)

Components are reusable atoms and molecules. Patterns are reusable solutions to
specific UX problems. Both need documentation. The documentation has different content.

### Pattern documentation format

A pattern spec includes:
1. **Problem solved**: what recurring design problem does this pattern address? Be specific.
2. **When to use**: the conditions under which this pattern is appropriate
3. **When not to use**: the conditions under which this pattern is wrong (and what to use instead)
4. **Anatomy**: the components it uses and how they're composed
5. **Behavior notes**: how the pattern behaves — transitions, state changes, loading treatment
6. **Variants**: whether the pattern has meaningful variations (e.g., a filter panel can be
   a sidebar panel or a popover — these are two pattern variants, not two components)
7. **Anti-pattern documentation**: what people commonly reach for that doesn't work, and why

Example: the "Inline Edit" pattern. Problem: users need to edit a value without
leaving the current context. When to use: for quick edits to individual field values
in a record view. When not to use: when editing requires validation against other fields
or when multiple fields are commonly edited together (use a modal or drawer instead).

### Anti-pattern documentation

Documenting what doesn't work is as important as documenting what does. Without it,
the same incorrect solution gets reinvented by every designer who encounters the same
problem. Anti-pattern documentation prevents institutional knowledge from being tribal.

Format: "Do not use [pattern] for [scenario] because [reason]. Instead, use [alternative]."

---

## Component Behavior Specification

### Interaction contract

Every interactive component has an interaction contract: what happens on each interaction
event. For a button: click → trigger action; keyboard Enter/Space → trigger action;
focus → show focus ring; disabled → no interaction events.

For complex widgets, the interaction contract is the entire specification. A combobox
that doesn't specify keyboard behavior is not specified — it will be implemented
inconsistently across the product.

Required interaction events to specify for interactive components:
- **Click / tap**: primary activation
- **Keyboard activation**: Enter, Space, arrow keys, Escape — as applicable
- **Focus / blur**: what happens to the component's visual state
- **Hover**: tooltip delay? Hover state appearance?
- **Long press** (mobile): if applicable
- **Drag** (for draggable elements): drag start, drag over valid/invalid targets, drop

### Responsive behavior

For every component that appears across breakpoints, specify:
- **At which breakpoints does the component change behavior?**
- **How does it adapt?** (collapse, scroll, truncate, wrap, reorder, hide)
- **Does the touch interaction model differ from the pointer model?**

For tables: at narrow widths, does the table scroll horizontally, collapse to cards,
or hide secondary columns? All three are valid — choose and specify.

### Content constraints

- **Minimum content length**: what is the minimum meaningful content? (A button must have a label.)
- **Maximum content length**: what is the maximum before truncation? (A table cell label truncates at 1 line with an ellipsis and a tooltip on hover.)
- **Truncation behavior**: where does truncation occur? (End truncation for names, middle truncation for file paths, custom truncation for emails)
- **Line clamp**: how many lines before clamping? What happens on overflow?

Specify all three. "It wraps" is not a specification. "It clamps at 2 lines with an
ellipsis; the full content is available on hover in a tooltip" is a specification.

### Overflow behavior

Every container has a maximum. When its content exceeds the maximum, something happens.
Specify what:
- **Scroll**: the container scrolls; the overflow is accessible
- **Truncate**: content is cut; the rest is hidden (require disclosure mechanism if content is important)
- **Clip**: content is cut without disclosure (appropriate only for decorative content)
- **Expand**: the container grows to accommodate content (appropriate when unbounded growth is acceptable)
- **Wrap**: content wraps to the next line (appropriate for tag chips, not for table cells)

"It depends on the context" is not an acceptable specification. The component must
have defined default overflow behavior. Context-specific overrides are additive.

---

## Engineering Handoff

### Annotate states explicitly

Engineers implement what is annotated. Implied states — states that "should be obvious"
from the default state — will be inconsistently implemented. If the focus ring must be
2px solid blue, annotate it on the focused state. Don't rely on the engineer inferring it.

Required annotations for every interactive component:
- All states (default, hover, focus, active, disabled, error, loading)
- Interactive trigger areas (what is clickable vs. what is not)
- Animation specifications: duration, easing, properties animated
- Focus order within the component (for composite components)
- ARIA roles and labels (for engineering; cross-reference `ux-accessibility`)

### Spec interactive behaviors

- Animation: duration and easing for each transition (not "smooth transition" — specify milliseconds and easing function)
- Hover delay for tooltips (typically 300–500ms — specify the value)
- Focus ring: width, color, offset, border-radius
- Ripple / press effect: radius, duration (if applicable)

### Flag design/implementation gaps early

If a component behavior requires new technical capability — a new hook, a new state
management pattern, a new backend endpoint — identify it during design and flag it
in the spec before the sprint starts. A component spec that requires a backend API
change is not ready for engineering until that API change is planned.

---

## Cross-Links

- `ds-advisor` — token architecture, DDR format, Figma ops layer; token/color system decisions
- `design-engineer` — design/code bridge; implementation-specific component patterns; code-connected design
- `fe-component-architecture` — implementation side; component API design; rendering constraints
- `fe-accessibility` — ARIA implementation requirements that inform component behavior spec
- `ux-accessibility` — state coverage for accessible design; focus state requirements; ARIA APG keyboard patterns
- `ux-interaction-design` — interaction patterns that use components; behavioral logic within workflows

---

## References

- ARIA Authoring Practices Guide — keyboard interaction patterns: https://www.w3.org/WAI/ARIA/apg/patterns/
- Carbon Design System — component documentation as a reference for spec format: https://carbondesignsystem.com/
- Radix UI Primitives — component API surface design reference: https://www.radix-ui.com/primitives
- Atlassian Design System — pattern documentation format: https://atlassian.design/components
- Nathan Curtis — Documenting Components (article): https://medium.com/eightshapes-llc/documenting-components-9fe59b80c015

## Related
- hub → [[lead-ux-designer]]
