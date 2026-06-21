---
title: Component & Pattern Framework
tags: [framework, design-systems, components, patterns, tokens, accessibility, ai-context]
created: 2026-06-17
updated: 2026-06-17
links:
  - "[[01-aesthetic-lens]]"
  - "[[02-ui-ux-operational-framework]]"
  - "[[05-last-mile-craft-framework]]"
  - "[[06-qa-operating-model]]"
  - "[[ux-component-library]]"
---

# Component & Pattern Framework

*The foundational lens for understanding, choosing, documenting, and composing **every component and pattern** a design system needs — and for making that understanding legible to humans, design tools, and AI agents alike. Where [[01-aesthetic-lens|Aesthetic Lens]] answers "why does this feel right?" and [[02-ui-ux-operational-framework|UI/UX Operational]] answers "how do we decide systematically?", this framework answers: **"what is each component **for**, when do I reach for it, why, and how do they work best together?"** It sits at the top tier, above any project-specific skill, and is the design-domain hub the README's "design-system work → 01, 02, 05, 06" row has been routing toward.*

---

## The core conviction

**A design system is not a kit of parts; it is a body of *intent*.** The pixels of a Button are the least interesting thing about it. What matters — and what is almost always lost — is *why it exists, when it is the right answer, what it means semantically, what it is made of, and how it composes with everything around it.* A component without its intent is a liability: it gets misused, re-implemented, named three different things, and quietly drifts.

This framework treats every component as a **structured unit of intent** documented against one universal schema, organized by the *question it answers*, governed by a small set of invariant laws, and delivered to whoever needs it — a designer, a Figma file, or an AI agent — in the right form at the right moment. The throughline, borrowed from Diana Wolosin's *Intent-Driven Context for AI Design Systems*: **"Context is not documentation. Context is intent."**

> **Reading order.** §1 sets the mental model and the delivery system. §2 the invariants. §3–4 the structure (layers + taxonomy). **§5 is the heart — the Universal Component Schema.** §6–7 are *how to choose* and *how to compose*. §8 the cross-cutting laws (with the citable rationale). §9–10 naming and lineages. §11–12 the AI-legible layer and the `DESIGN.md` protocol. §13 playbooks. §14 the operating model. §15 the resource canon. Appendices: the 62-component quick reference, the blank schema + JSON, and the canonical-vs-alias map.

---

## 1. The mental model: context is intent

More documentation does not make a system more usable — it makes it noisier. The fix is to classify every piece of design-system knowledge by *why it exists* (its intent), then deliver each kind in the form best suited to it. Wolosin's four intent types map almost one-to-one onto four delivery mechanisms — which is exactly the interconnected system this framework governs:

| Intent type (Wolosin) | The question it answers | Best delivery form | Artifact in this system |
|---|---|---|---|
| **Framing context** — the *why* | "Why does this exist, and how should it shape my decision?" | Durable prose, loaded as needed | **This framework** (the hub) |
| **Workflow context** — procedure | "What are the steps to do this well, right now?" | Procedural, progressive disclosure | **The skill** ([[ux-component-library]]) |
| **Guidelines** — deterministic answers | "What exactly is component X — its states, anatomy, names?" | Structured, typed, **on-demand** | **The MCP** (`ux-components`) |
| **Constraints** — guardrails + token values | "What must always/never happen? What does our brand look like?" | Rules + portable token file | **`AGENTS.md` rules + `DESIGN.md`** |

```
                        ┌───────────────────────────────────────────┐
                        │   ⓵  COMPONENT & PATTERN FRAMEWORK (this)  │  framing context
                        │   the universal schema · taxonomy ·        │  — the durable WHY,
                        │   decision trees · laws · the constitution │     the hub everything
                        └───────────────┬───────────────────────────┘     points back to
                  ┌─────────────────────┼──────────────────────┬───────────────────────┐
                  ▼                     ▼                      ▼                       ▼
        ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐   ┌────────────────────┐
        │ ⓶ SKILL          │  │ ⓷ MCP            │  │ ⓸ DESIGN.md      │   │ ⓹ RULES / AGENTS.md│
        │ ux-component-lib │  │ ux-components    │  │ visual identity  │   │ + lint             │
        │ HOW to operate   │  │ per-component    │  │ tokens + brand   │   │ guardrails,        │
        │ (procedure)      │  │ data on demand   │  │ prose snapshot   │   │ ~0 tokens at rest  │
        └──────────────────┘  └──────────────────┘  └──────────────────┘   └────────────────────┘
          workflow context      guidelines             constraints (look)     constraints (rules)
```

**Why this layering and not one big file.** Google's `DESIGN.md` and Atlassian's field test of it (see §11–12) proved the failure mode of collapsing everything into a single always-loaded document: token bloat, early context truncation, forced omission of guidance, and agents *re-implementing* components instead of importing them. The cure is to put each intent type where it belongs — heavy per-component depth **on demand** (MCP), procedure in a **skill**, the durable reasoning **here**, and only the lean visual-identity snapshot in **`DESIGN.md`**. Right intent, right moment, right form.

---

## 2. First principles (the invariants)

These hold across all 62 components and every system. They are the load-bearing throughlines — memorize them; they resolve most decisions before you reach for a tree.

1. **Behavior is invariant; names are not.** The same name means different components across systems, and the same component has many names. Always resolve a named thing to its *canonical behavior* — modality, trigger, semantics, *when the change applies* — before reasoning (§9).
2. **Pick the lowest-intensity component that works.** Whitespace before a Separator; Toast before Dialog; Tooltip before Popover; Collapsible before Accordion; Select before Combobox; Table before Data Table. Escalate only when the simpler one demonstrably fails.
3. **One primary action per section.** Over-emphasis dilutes hierarchy. Exactly one primary Button per logical region; everything else is secondary/ghost/link.
4. **Cover every state.** A component isn't "done" until default / hover / focus / disabled — plus, where relevant, filled / error / read-only / loading / empty / selected / indeterminate — are all designed. The state matrix is the QA checklist (§5, §8).
5. **Intent travels with the component.** The *when-to-use / when-to-avoid* must be attached to the artifact — Figma description, code doc, MCP record — not stranded in a wiki. A component whose intent doesn't travel will be misused.
6. **Accessibility is non-negotiable and encoded in semantics.** The right ARIA role *is* the intent made machine-readable (§8). Choosing the wrong family (menu vs. form-input) breaks both a11y and user expectation.
7. **A specific reference beats a pile of adjectives** (the `DESIGN.md` lesson). "A 1970s graduate lecture handout" carries its own negative constraints for free; "modern, clean, premium" evokes nothing and yields generic output. Specificity is compression.
8. **Names that travel between design, code, and conversation must be one name.** Code identifier, Figma page title, nav label, and spoken name should resolve to the same canonical concept (§9, §11).

---

## 3. The layered model — where everything sits

A design system stacks. Each layer constrains the one above and is composed from the one below. Knowing the layer a thing belongs to is half of placing it correctly.

```
  Pages / Screens        real content in a template — validates the system with live data
  ────────────────
  Templates              page-level structure, slots, no real content      (Atomic: Templates/Pages)
  Patterns               goal-driven compositions ("checkout", "empty→loading→error")
  Components             content-agnostic, reusable units (Button, Dialog)  (Atomic: molecules/organisms)
  Primitives             unstyled behavior + a11y (headless)                (Atomic: atoms)
  ────────────────
  Tokens                 named decisions: global → semantic/alias → component   (sub-atomic)
  Foundations            color, type, space, grid, motion, elevation, a11y, voice
```

- **Atomic-design mapping** (Brad Frost): atoms ≈ primitives, molecules + organisms ≈ components, templates/pages ≈ templates/screens. Tokens sit *below* atoms as "sub-atomic particles." Frost's reuse gradient is useful downstream: **Components** (agnostic, max reuse) → **Recipes** (product-specific compositions, e.g. `ProductCard`) → **Snowflakes** (one-offs). Name and govern each tier differently.
- **The component ↔ pattern boundary** is the most useful line in the stack: a **component is content-agnostic**; a **pattern is a composition aimed at a user goal or flow** (Polaris: "preferred solutions to common merchant goals"; Carbon governs patterns separately). If it solves a *job*, it's a pattern (§7). If it's a *part*, it's a component.
- **The three-tier token model** (Spectrum's global / alias / component; Curtis's Options → Decisions): **Global/primitive** (raw `blue-600`) → **Semantic/alias** (`color-action-primary`, carries intent) → **Component** (`button-bg-primary`, local decision). Rule: only use a global token when no alias exists; start a token *inside* a component and **promote** it outward only after repeated reuse. Tokens are DTCG-shaped JSON (§11) so they round-trip to Figma variables, Tailwind, and `DESIGN.md`.
- **Token names are assembled from a grammar** (Curtis): `[Namespace] · [Object] · [Base: category + concept + property] · [Modifier: variant/state/scale/mode]` — e.g. `esds-color-feedback-background-error`. Include only the levels needed to distinguish intent; keep `theme` (brand) and `mode` (light/dark) as *orthogonal* axes. **Default to *purposeful* (semantic) naming over *aesthetic* (literal)** — `error` not `red`, `primary` not `blue-600` — and never mix both in one enum. Depth: skill ref `tokens-and-naming.md`.
- **The field disagrees on one thing** — whether tokens live *inside* foundations (Atlassian) or *beside* them (Polaris), and whether to start with foundations at all (Dan Mall's "Folly of Design System Foundations" argues to treat color/type "as components like everything else"). Pick a stance per project; don't pretend it's settled.

---

## 4. The taxonomy: 9 categories = 9 questions

Every UI need maps to one category, and each category answers exactly one question. When unsure which component, **name the question first** — it narrows 62 options to a handful; the trees in §6 finish the job.

| Category | The question it answers | Components (canonical count) |
|---|---|---|
| **Action** | "I want the user to *do* something." | button, toggle, toggle-group, toolbar (4) |
| **Form** | "I need to *collect* a value." | input, textarea, label, checkbox, radio-group, select, combobox, switch, slider, rating, file-upload, search, number-input, date-picker, time-picker, calendar, color-picker, form (18) |
| **Navigation** | "I need the user to *get somewhere* or *reach a command*." | link, breadcrumb, tabs, pagination, dropdown-menu, context-menu, menubar, navigation-menu, stepper (9) |
| **Feedback** | "I need to *tell* the user what's happening." | alert, toast, banner, progress, spinner, skeleton, empty-state, meter (8) |
| **Data Display** | "I need to *show* records, entities, or metadata." | avatar, badge, tag, chip, list, table, data-table, tree-view, timeline (9) |
| **Layout** | "I need to *group or separate* content." | card, separator, scroll-area (3) |
| **Overlay** | "I need a *temporary surface* above the page." | tooltip, hover-card, popover, dialog, alert-dialog, sheet (6) |
| **Disclosure** | "I need to *hide content until asked*." | accordion, collapsible (2) |
| **Content** | "I need to *present media or symbols*." | carousel, image, icon (3) |

**Coverage signal** (how safe is an assumption): components mapped to *many* systems are universal — Button (80+), Dialog (85), Checkbox/Tabs/Radio (82), Table (73), Tooltip (76). Components mapped to *few* are specialized — verify the target system has them or plan to compose: Hover Card (6), Color Picker (7), Scroll Area (7), Timeline (9), Meter (10), Data Table (11), Tree View (13), Rating (14).

**Known gaps** (commonly expected, absent from the canonical 62 — compose from the nearest primitive and *flag the gap*): Command Palette, Aspect Ratio, Resizable panels, dedicated Drawer (= Sheet), dedicated Multi-select (= Combobox/Chip pattern), Video (folded into Carousel/Image), KBD, Code block.

Full per-component reference: Appendix A here, [[ux-component-library]]'s `component-inventory.md`, or the live MCP (`lookup "<category> components"`).

---

## 5. The Universal Component Schema — the heart

Every component, regardless of category, is understood and documented against the **same set of facets**. This is the schema that makes "understanding any component" a repeatable act rather than an ad-hoc one. It is the synthesis of Nathan Curtis's 8-section spec + separate usage guidelines, Open UI's research schema, Storybook's CSF surface, the live MCP record shape, and the visual-decision dimensions from Material/Carbon/Apple.

Each facet answers a question, and — critically — each is **authored in a specific layer** of the delivery system (this is what keeps the system DRY and non-bloating):

| # | Facet | The question it answers | Authored in |
|---|---|---|---|
| 1 | **Identity** | What is its one canonical name, its aliases, its category, its maturity? | Framework + MCP |
| 2 | **Intent / purpose** | What job does it do — what problem does it solve? | MCP (`description`/`overview`) |
| 3 | **Context** | Where and when does it appear; what environment fits it? | MCP + Skill |
| 4 | **When to use / when to avoid** | What are the decision boundaries, and the alternatives at each edge? | MCP (`when_to_use`/`when_to_avoid`) |
| 5 | **Semantics** | What ARIA role/contract encodes its meaning? | Framework (law) + code |
| 6 | **Anatomy** | What named parts / slots is it made of? | MCP + Figma layers |
| 7 | **States** | What is the full state matrix to cover? | MCP (`states`) |
| 8 | **Variants** | What axes vary it — hierarchy, size, tone, style? | MCP + Figma variant props |
| 9 | **Behavior & interaction** | Keyboard map, focus management, timing? | Framework (laws) + code |
| 10 | **Content & microcopy** | Label voice, truncation, i18n/RTL? | DESIGN.md (voice) + Skill |
| 11 | **Visual-design decisions** | Color/tone, type, spacing, radius, elevation, motion, density, focus? | **DESIGN.md** (brand) + tokens |
| 12 | **Tokens** | Which component-token bindings (DTCG)? | DESIGN.md / tokens.json |
| 13 | **Composition & relationships** | Composes-from, pairs-with, confused-with, escalates-to? | Framework + MCP (`related`) |
| 14 | **Responsive & platform** | How does it adapt across breakpoint and platform? | Framework + DESIGN.md |
| 15 | **Accessibility specifics** | Roles, keyboard, contrast, focus return? | Framework (APG) + code |
| 16 | **Quality / Definition of Done** | What is the build/QA checklist? | Framework + [[06-qa-operating-model]] |
| 17 | **Governance** | Status, version, owner, **code binding** (import path/symbol)? | Code Connect + MCP |
| 18 | **Machine-readable intent record** | The JSON the AI layer consumes (rolls up 1–17)? | MCP / component JSON (§11) |

### The facet model, expanded

- **Identity.** One name in design, code, and conversation. Carry the canonical concept in the description even when the *displayed* name is the team's vocabulary (a Radix `Sheet` shown as the team's "Drawer," description noting "Sheet / Drawer / Side Panel").
- **Intent.** A verb-led, ≤~144-char statement of the job — *not* the implementation. "The primary mechanism for user-initiated actions," not "a styled `<button>`."
- **When-to-use / when-to-avoid.** Each *avoid* names the failure mode **and the component to use instead** — this is what makes the boundary actionable (e.g. Button → *avoid for navigation; use Link*).
- **Semantics.** The role is the intent in machine form: `role="switch"` (instant) vs `aria-pressed` Toggle (stateful) vs `role="radiogroup"` (single-choice). Get this wrong and the component lies to assistive tech.
- **Anatomy.** Named parts become Figma layers/slots and code sub-components. (Input = Label · Field · Placeholder · Hint · Error. Accordion = Container · Trigger · Indicator · Panel.)
- **States.** The variant axes you *must* cover. Interactive minimum: default / hover / focus / disabled. Inputs add filled / error / read-only. Async adds loading / empty / error. Selection adds selected / indeterminate.
- **Variants.** Orthogonal axes: Button = `variant`(primary/secondary/ghost/destructive) × `size`(sm/md/lg); Tabs = `style`(line/pill); Toggle Group = `mode`(single/multi).
- **Visual-design decisions (facet 11)** — the dimensions every component must resolve, with their rationale, live in §8. This is where `DESIGN.md` does its work.

### The schema as a fill-in template

A blank template (Appendix B) and the machine-readable JSON schema (§11, Appendix B) accompany this. Worked example — **Button**, every facet populated — showing the schema is real, not aspirational:

```
Identity      Button · aka "CTA" (Nucleus), "Primary Button" (Canvas) · Action · Stable
Intent        The primary mechanism for user-initiated actions; label is always a verb/verb-phrase.
Context       Form submit, dialog/drawer trigger, primary CTA, confirm/cancel — anywhere state changes.
Use           Submitting forms; triggering overlays; the one primary CTA; confirm/cancel.
Avoid         Navigation → use Link. >1 primary per section. Vague labels ("Click here"). Disabled w/o reason.
Semantics     <button>; icon-only requires aria-label/Tooltip; loading sets aria-busy + non-interactive.
Anatomy       [leading icon] · Label · [trailing icon]; spinner replaces/【accompanies label when loading.
States        Default · Hover · Active/Pressed · Focused(visible ring) · Disabled · Loading.
Variants      variant: primary|secondary|ghost|destructive  ×  size: sm|md|lg.
Behavior      Enter/Space activate; visible focus ring; loading blocks re-entry.
Content       Verb-led, sentence case, specific ("Add apps" not "Submit"). No period.
Visual (§8)   tone via semantic color role + on-color pair · radius token · state layer on hover/press · no shadow unless elevated.
Tokens        {button-bg-primary} → {color.action.primary}; {button-radius} → {rounded.md}.
Relationships compose: Icon, Spinner · pairs: Form, Dialog · confused-with: Link, Toggle, Dropdown Menu.
A11y          role=button; focus-visible ring ≥3:1; disabled explained; min target 44×44pt.
DoD           all 6 states; one-primary check; a11y name on icon-only; tokens bound; loading non-interactive.
Governance    status: stable · v: 2.x · owner: DS · code: import { Button } from "@ds/button".
```

---

## 6. Decision frameworks — *how to choose* (the "which one?" trees)

The highest-value output of cross-system analysis: the recurring forks where designers pick wrong. Run the tree for the cluster after naming the category.

**Overlays** — by *modality* × *trigger*:
```
Plain text, ≤1 sentence, non-essential ........ Tooltip      (hover/focus, never interactive)
Rich preview on hover, desktop, non-critical .. Hover Card   (needs tap fallback)
Rich/interactive, must NOT block the page ..... Popover      (non-modal, no focus trap)
Focused bounded task, block the page .......... Dialog       (modal, focus trap, scroll lock)
Destructive/irreversible, must acknowledge .... Alert Dialog (modal + confirm/cancel)
Edge-anchored secondary content, keep context . Sheet        (a.k.a. Drawer)
```
Rule: Tooltip→Popover the moment content is interactive. Dialog→Alert Dialog the moment it's irreversible. Dialog→Sheet when no decision is needed and context should persist. Dialog→page when the form is long/complex.

**Single-choice input** — by *option count*: 2–5 visible → **Radio Group** · 5–15 fixed → **Select** · >15 / unknown name → **Combobox** · mutually-exclusive *view* switch → **Toggle Group / Tabs**. The thresholds (≈5, ≈15) are load-bearing.

**Binary control** — by *when the change applies*: instant → **Switch** (`role="switch"`) · submitted with a form → **Checkbox** · stateful button in a toolbar → **Toggle** (`aria-pressed`). The semantic test is *timing*.

**Messaging** — the escalation ladder, use the lowest rung: **Toast** (ignorable) → **Alert** (persistent inline) → **Banner** (page-wide) → **Alert Dialog** (blocking). Over-escalation causes fatigue.

**Loading** — by *known duration / layout*: known → **Progress** · unknown, inline → **Spinner** · initial load, known layout → **Skeleton** · static measurement → **Meter**. Below ~300ms show nothing (§8).

**Labels & metadata** — by *interactivity*: numeric/status, decorative → **Badge** · textual, removable → **Tag** · interactive token, in groups → **Chip**.

**Data** — one meaningful column → **List** · multi-column, relationships matter → **Table** · sort+filter+paginate+select → **Data Table** · hierarchical → **Tree View** · chronological → **Timeline** · one-subject groups → **Card** grid.

**Content organization** — parallel, labels always visible → **Tabs** · stacked, scan-and-expand → **Accordion** · single optional section → **Collapsible** · sequential with progress → **Stepper** · equivalent media to cycle → **Carousel** (sparingly).

**Menus & nav** — the deepest distinction in the whole set: **Dropdown / Context / Menubar use *menu* semantics (actions)**; **Select / Combobox use *form-input* semantics (values)**. Never cross them. Navigate-between-pages → Navigation Menu; "you are here" → Breadcrumb; page a dataset → Pagination.

---

## 7. How components work best together — *composition*

Choosing the right component is half the job; the other half is how they combine. Components are designed to *compose* — and most real UI is patterns, not lone components.

**Composition rules.**
- **Compose from primitives, don't fork.** A multi-select is a Combobox + Chips, not a new widget. A date range is two Calendars in a Popover. Reach for the nearest modeled primitive (§4 gaps) before inventing.
- **Respect the semantic family at every level.** A menu inside a toolbar is still `menu` semantics; a value-picker inside a dialog is still `form-input`. Nesting doesn't change a component's contract.
- **One overlay layer at a time.** Avoid nested Popovers/Dialogs; escalate to a page or a Sheet instead. Overlays are temporary surfaces — never build primary content into one.
- **Lowest-intensity wins at the composition level too.** Group one-subject content into **Cards**; separate sections with **whitespace first, Separator only if needed**; constrain overflow with **Scroll Area** while keeping page scroll native.

**The patterns every product needs** (goal-driven compositions — name the job, then assemble):

| Pattern | Job | Typical composition |
|---|---|---|
| **Form / data entry** | Collect and validate values | Form → Inputs/Selects/Checkboxes (per §6 trees) → one primary Button → inline Alert on error |
| **Master–detail** | Browse a set, inspect one | List/Table (master) → Sheet or panel (detail) → contextual Toolbar |
| **Dashboard** | Show status at a glance | Card grid → Badge/Meter/Progress → Skeleton on load → Empty state when no data |
| **Wizard / multi-step** | Sequence a long task | Stepper (position) → Form per step → Progress (single task) → Toast/Alert on completion |
| **The async triad** | Survive every data condition | **Skeleton/Spinner** (loading) → content → **Empty state** (no data) → **Alert** (error). *Every* data view needs all three. |
| **Confirmation** | Prevent costly mistakes | Action → Alert Dialog (irreversible) *or* Toast + Undo (reversible) — pick by reversibility |
| **Filtering** | Narrow a large set | Search/Combobox → Chips (active filters, removable) → Toolbar → results Table |

**The escalation ladders** (when one component graduates to another): Select→Combobox (list grows past ~15); Table→Data Table (needs sort/filter/paginate); Tooltip→Popover (content becomes interactive); Toast→Alert→Banner→Alert Dialog (urgency rises); Collapsible→Accordion (one section becomes many). Climb only one rung at a time, and only on evidence.

**Recipes vs. snowflakes.** A composition reused across the product (a `ProductCard`, a `FilterBar`) is a **recipe** — name it, document it, govern it like a component. A genuine one-off is a **snowflake** — allowed, but labeled as such so it doesn't masquerade as a system primitive.

---

## 8. Cross-cutting foundations & universal laws

These held across all 62 components. They are the rationale behind the trees — and the citable "why" that `DESIGN.md` prose and component docs should carry. (Facet 11 of the schema resolves *per component* against these dimensions.)

### 8a. Accessibility (non-negotiable; the semantics layer)
1. **Every input has a visible Label** associated via `for`/`id`. Placeholder is never a label.
2. **Focus management for overlays:** modal surfaces (Dialog, Alert Dialog, modal Sheet) **trap focus and return it to the trigger** on close; non-modal (Popover) doesn't trap but closes when focus leaves. (WAI-ARIA APG: dialog = `role="dialog"` + `aria-modal`, Esc closes, focus returns.)
3. **Correct ARIA roles encode intent:** `role="switch"`, `aria-pressed` (Toggle), `radiogroup`, menu/menuitem, `role="dialog"`, `role="tooltip"`+`aria-describedby`, `role="progressbar"`, `aria-current="page"`, `aria-sort`, `aria-live`/`role="alert"`.
4. **Keyboard patterns are component-specific and expected:** arrow keys move *within* a group (Radio, Tabs via **roving tabindex**, Menu, Tree, Slider, Calendar); Tab moves *between* widgets; type-ahead in Select; Escape closes overlays. Combobox keeps DOM focus on the input and points to the active option with `aria-activedescendant`.
5. **Never rely on color alone.** Pair color with text/icon/shape (Badge, Alert, status).
6. **Icon-only controls must have an accessible name** (Tooltip / `aria-label`).
7. **A visible focus indicator is always present** and distinguishable from the selected state (≥3:1 contrast against adjacent colors), or keyboard and low-vision users lose their place.

### 8b. Timing & perception (the citable numbers)
- **The 300ms rule:** below ~300ms, show no loader — the flash is worse than the wait; above it, Spinner/Skeleton/Progress.
- **The Doherty Threshold (~400ms, IBM 1982):** keep system response under 400ms and productivity climbs — this is the budget for loading states, optimistic UI, and motion.
- **Overlay open-delays:** Tooltip 400–600ms; Hover Card 300–500ms + close grace period; Toast auto-dismiss ≥4s, pause on hover.

### 8c. The visual-design decision dimensions (facet 11)
Every component must resolve each of these. The defaults below are the cross-system consensus with rationale; a project's `DESIGN.md` overrides the *values*, this framework owns the *dimensions*.

| Dimension | Resolve to | Rationale / citable defaults |
|---|---|---|
| **Color / tone** | A semantic *role* + its *on-color* pair, not a hex | Roles (`primary`/`on-primary`, `surface`/`on-surface`, `outline`) generate correct light/dark/contrast values from one palette (Material 3). Never grey text on a colored bg — use a low-contrast variant of the bg's own hue (Refactoring UI). Author in HSL/OKLCH, not hex. |
| **Typography** | A token bundling size/weight/line-height | ~9–15 type levels; limit to ~2 weights (Refactoring UI); emphasize by de-emphasizing competitors. |
| **Spacing** | A value on a constrained non-linear scale | 4, 8, 12, 16, 24, 32, 48, 64, 96, 128 (Refactoring UI); or Carbon's 8px mini-unit (multiples of 2/4/8) so spacing and grid never fight. |
| **Radius** | A `rounded` token (none→sm→md→lg→xl→full) | Consistency over per-component choice. |
| **Elevation / depth** | A level **or** a tonal layer | Two solved ways: **shadow** (large soft ambient + tight direct, consistent top-down light; larger/blurrier = higher — Refactoring UI/Apple) **or** **tonal surface** (Material 3: dp 0/1/3/6/8/12 expressed as tonal overlay, because shadows vanish on dark surfaces). Pick one per system. |
| **Motion** | A duration + easing token, split by intent | M3: short 50–200 / medium 250–400 / long 450–600 ms; standard easing `cubic-bezier(0.2,0,0,1)`. Carbon: fast-01 70, moderate-01 150, slow-01 400; **productive vs expressive** (subtle for repeated task moments, vibrant for rare significant ones). Cap UI transitions ~300ms; honor `prefers-reduced-motion`. |
| **State layers** | An overlay opacity per state | M3: hover 8% · focus 10% · pressed 10% · dragged 16% of the on-color — one systematic overlay, theme-adaptive. |
| **Density / touch target** | A comfortable minimum | ≥44×44pt (Apple HIG) / 48×48dp (Material); enterprise data-dense UIs (Carbon) trade padding for rows but never below the target. |
| **Focus** | A visible indicator + a management model | See 8a.7 and roving-tabindex vs `aria-activedescendant`. |

### 8d. Hierarchy, restraint, content
- **One primary action per section** (law 3); emphasize by de-emphasizing the rest (Refactoring UI; Aesthetic-Usability and Peak-End effects reward polish at peak/final moments).
- **Hick's / Miller's / Fitts's laws** translate directly: shorten menus and use progressive disclosure (Hick); chunk to ~7±2 but don't cap arbitrarily (Miller); make targets big, close, well-spaced (Fitts).
- **Microcopy:** buttons start with a verb; sentence case for headings/buttons; errors state *what's wrong + what to do*, don't over-apologize, avoid "invalid" (Polaris). **Same voice always, tone shifts with the reader's emotional state** (Mailchimp).

**State modeling (escape "the sorry state of states").** "States" is overloaded — design tools cram everything into one enum, code uses many booleans, and the two break on handoff. Model the concerns **separately**: an interaction enum `state` = `rest | hover | active | focus`; configuration **booleans** `disabled`, `readonly` (never members of the state enum); a `validation` enum = `none | error | success`; selection `selected` / `indeterminate`. Normalize synonyms (`default / enabled / resting` → `rest`), and support valid cross-concern combinations a single enum can't (`readonly + focus`, `hover + error`). Depth: skill ref `component-authoring.md`.

> The full state matrix per component is the build/QA gate. Run it through [[06-qa-operating-model|QA Operating Model]] — no curated subsets; every component, every variant, every state.

### 8e. Variant architecture & total tokenization (the authoring laws)

These two laws govern *how a component is constructed* in any variable-capable tool (Figma variables/modes, DTCG, code themes). They are non-negotiable and apply **wherever possible**.

**1 — Mode-first variant architecture.** A component's *varying primitives* — intent/tone colors, size, density — belong in **variable modes** on a component-scoped collection (`Button — Variant`, `Button — Sizes`, `Avatar — Sizes`, `… — Badge`), **not** in physical variants. Bind each part to role tokens (`background/*`, `foreground/*`, `border/*`, `ring/*`; `height`, `paddingX`, `gap`, `radius`, `iconSize`) that resolve **per mode**; switching the instance's mode re-themes/re-sizes it. Decide each axis with this litmus, in order:
- Can a **variable** carry the value (a color or number)? → **mode + role token**.
- Is it the **presence/absence** of a part (icon, label, badge, shortcut, close)? → **boolean property** bound to layer `visible`.
- Is it genuinely different **structure** (different layers/anatomy) or a **non-bindable** property (e.g. a link's underline — `textDecoration` can't be a variable)? → **physical variant** (the *only* justified use).

This collapses combinatorial explosions: an intent×state Button is **7 state variants × N intent modes**, not 6×7 = 42 physical variants; the same role tokens then give free light/dark/brand theming on the same machinery. Physical-variant intent duplicates a mode system and is a defect to refactor. **Decide the axis mechanism (mode / boolean / variant) BEFORE authoring, and reuse existing infrastructure** — check for a component-scoped collection first (a `Button — Variant` with 11 ready modes existed while the component was nonetheless built as 42 physical variants — pure rework). `width`/`height` *are* variable-bindable, so size→mode is valid; just put any absolutely-positioned child on MAX/MAX constraints so it tracks the resize. The exception that *keeps* a physical variant: a tone whose variants carry **distinct icon glyphs** (Alert/Toast info/triangle/check) — an instance-swap can't be a mode, so the variant correctly bundles color + glyph. *(Plan note: modes/collection are plan-capped — Enterprise allows 40. If a collection genuinely needs more modes than the file's tier allows, that — not aesthetics — is the signal to split components into separate library files, §3.)*

**2 — Total tokenization (no raw values, ever).** Every property that *can* bind to a variable **must**: fills, strokes, stroke-weight, corner radius, padding, gap/item-spacing, font size / line-height / letter-spacing. This explicitly includes **zero and blank** values — they are not exempt:
- padding/gap `0` → `space-0` · radius `0` → `radius-none` · stroke-weight `0` → `border-width-0`
- a transparent fill/stroke → the **`transparent`** color token (a bound zero-alpha paint), **never** an empty paint array.

A raw literal anywhere is a defect to be bound. If a parameter type lacks a "0 / none / transparent" helper token, **create it** (primitive value ← semantic alias) rather than leaving the value raw — never work around a missing token with a hardcode. Sanctioned exceptions, which must be *noted*, not silently left: tool **chrome** (Figma section backgrounds/borders — organizational, not design) and deliberate **negative** values (e.g. an avatar group's −8 item-spacing overlap) for which no token can exist.

> Both laws are enforced at the [[05-last-mile-craft-framework|last-mile]] gate and audited by [[06-qa-operating-model|QA]]: a component is not "done" until its primitives are mode-driven, its optional parts are booleans, physical variants exist only for true structure, and **100% of bindable values resolve to tokens** (zeros and blanks included).

---

## 9. The naming problem — names lie, behavior doesn't

1,900+ name mappings exist because the same concept has many names and the same name means different things. Resolve to the canonical concept *before* reasoning.

**Same name → different component (false friends):**
- **"Toggle"** = stateful button (canonical), but **= Switch** in Atlassian/Carbon/Nord/Clarity.
- **"Select"** = single dropdown (canonical), but **= Combobox** in Atlassian/PatternFly/Flowbite.
- **"Tag"** = textual metadata (canonical), but **= Badge** in Carbon/USWDS/GOV.UK, **= Chip** in Fluent/Ant/Chakra.
- **"Tooltip"** = plain hover label, but **= Popover** in USWDS/Lightning/Duet.
- **"Banner"** = page-wide message, but **= Alert** in Canvas/Polaris/Cedar.
- **"Menu"** = Dropdown *and* Context *and* Navigation menu, depending on system.

**Different name → same component (synonyms):** Sheet → Drawer / Offcanvas / Side Panel / Tray / Flyout / Bottom Sheet. Dialog → Modal / Layer. Toast → Snackbar / Flag / Flashbar / Notification. Toggle Group → Segmented Control / Content Switcher / Button Group. Spinner → Loader / Busy Indicator. Combobox → AutoComplete / Autosuggest / Super Select. Separator → Divider / HR / Rule. Stepper → Steps / Wizard / Progress Indicator.

**The rule:** when someone names a component, silently ask *which of the canonical concepts is this, by behavior?* Behavior (modality, trigger, semantics, when-the-change-applies) is invariant; names are not. Use the MCP `lookup "what is <x> called in <system>"` to resolve any mapping on demand. Full map: Appendix C and [[ux-component-library]]'s `cross-system-patterns.md` §3.

---

## 10. Design-system lineages — read the lineage, infer the defaults

When a team says "we follow X," the lineage predicts naming, density, and coverage:

- **Primitive-first (Radix / shadcn / Ariakit / React Aria / Base Web).** Unstyled behavior + a11y; the canonical names here largely follow this lineage. Best mental model for *transliteration* — states/anatomy are explicit.
- **Material (Google).** Snackbar (Toast), Side Sheet, Chip first-class, Date Pickers (covers Calendar); motion-forward, elevation/FAB.
- **Atlassian.** Flag (Toast), Drawer (Sheet), Section message (Alert), Dynamic table (Data Table); calls Combobox "Select."
- **Carbon (IBM).** Enterprise/data-dense: Tile (Card), Content Switcher (Toggle Group), Structured List, Data Table flagship, Notification (Toast); 2x grid, productive/expressive motion.
- **Ant.** Admin/console: AutoComplete (Combobox), Message (Toast), rich tables/forms.
- **Bootstrap.** Offcanvas (Sheet), Form Control/Check, Modal, Navbar; class-driven.
- **Government (GOV.UK / USWDS / NHS).** Plain pluralized names ("Radios"), accessibility-first, error-summary patterns — the best a11y reference.
- **Enterprise vendors (Spectrum, Fluent, Polaris, Lightning, Cloudscape, Fiori).** Signature vocab (Spectrum "Picker"/"Tray"; Fluent "SpinButton"/"Message bar"; Cloudscape "Flashbar"). Expect that vocabulary and density.

---

## 11. The AI-legible layer — making the framework machine-consumable

The same intent that helps a designer helps an agent — *if* it's delivered as structured context, not prose to be re-parsed. The 2024–2026 consensus: **re-encode the system as data carrying intent, constraints, and code mapping.**

**Stack:** DTCG tokens (data) → component intent JSON (semantics) → Code Connect (design↔code bridge) → MCP (delivery), with always-on foundations + `AGENTS.md` governance.

**JSON over prose.** Benchmarks (Indeed's machine-readable DS; Figma's MCP work) found JSON gives equal-or-better agent accuracy at **~80% fewer tokens**, and semantic token names improve code accuracy materially. So: serve per-component data as one schema-validated JSON object **on demand**, keep foundations always-on, and bind each component to a real code symbol (Code Connect) so agents *import* instead of *re-implement*.

**The component intent record** (rolls up facet 18; this is the shape the `ux-components` MCP already returns and the contract any component JSON should meet):

```jsonc
{
  "id": "button",
  "name": "Button",
  "aliases": ["CTA", "Primary Button"],
  "category": "Action",
  "intent": "The primary mechanism for user-initiated actions.",
  "whenToUse": ["submit a form", "trigger a dialog", "the one primary CTA"],
  "whenToAvoid": [{ "case": "navigation", "use": "Link" },
                  { "case": ">1 primary per section", "use": "secondary/ghost" }],
  "states": ["default","hover","active","focused","disabled","loading"],
  "anatomy": ["leadingIcon","label","trailingIcon","spinner"],
  "variants": { "variant": ["primary","secondary","ghost","destructive"], "size": ["sm","md","lg"] },
  "a11y": { "role": "button", "keyboard": ["Enter","Space"], "iconOnlyNeeds": "aria-label", "minTarget": "44pt" },
  "tokens": ["button-bg-primary","button-radius","button-focus-ring"],
  "related": ["link","toggle","dropdown-menu"],
  "codeBinding": { "import": "@ds/button", "symbol": "Button" },
  "meta": { "status": "stable", "version": "2.x", "owner": "DS" }
}
```

**The AI-ready checklist** — audit a system against four pillars: **(1) code-first single source of truth** (agents read code/JSON far better than Figma; *misalignment between sources is the #1 cause of inconsistent AI output*); **(2) well-structured docs, one file one job** — *Foundations describe intent · Tokens describe vocabulary · Specs describe contracts · Governance describes process*; **(3) coded components / design-to-code parity**; **(4) documentation & governance** (naming conventions, extension rules, request process).

**Author the record *as data*.** A component is defined once as `anatomy · props · default · variants · examples` (Curtis), shipped as `Component.meta.json` + `Component.tokens.css` beside the implementation. Props are tagged Figma-only / shared / **code-only** (a11y, handlers, ids); **examples are composition** (`instanceExamples` + `slotContentExamples`), captured distinctly from variants; token names are "reasonable English," each with a `$description`. Depth: skill refs `component-authoring.md`, `tokens-and-naming.md`, `ai-ready-design-systems.md`.

**Why `DESIGN.md` alone is not enough for production** (Atlassian's field test, the evidence that shaped this system): a single `DESIGN.md` loaded everything at once (token bloat, early truncation), forced omission to fit size (their 50+ components compressed to ~10.7k tokens; agents had to read source for the cut guidance), and — lacking code bindings — pushed agents to *recreate* components. Benchmarked, it cost +92% tokens vs. the MCP for a login screen. **The cure is this layered system:** depth on demand (MCP), procedure in the skill, the durable why here, code bindings via Code Connect, and `DESIGN.md` kept lean for the one thing it's excellent at — portable visual identity (§12).

### 11a. A2UI — the agent-to-UI runtime layer

When an agent must *render* UI (not just reason about it), **A2UI** (Google; open, Apache-2.0) is the emerging contract: the agent streams a declarative JSON description of UI *intent*, and a client renderer maps it to its own pre-approved component library. It is the **payload** layer atop the **A2A** agent-to-agent transport, and is also servable over **MCP**. A2UI defines components in a swappable **Catalog**, expresses layout flexbox-style — and **leaves styling to the renderer; it has no token system of its own.** That is exactly the shape this system fills:

| A2UI leaves open | This system supplies |
|---|---|
| the **Catalog** (trusted component vocabulary) | a projection of the canonical 62-component taxonomy into an A2UI catalog — note coverage gaps (combobox, popover, toast… have no basic-catalog equivalent → add as custom components) |
| component **`instructions`** + selection at generation time | the `ux-components` MCP (intent / states / anatomy / a11y) authors the catalog and serves it on demand |
| **styling** (renderer-controlled, CSS-variable themed) | `DESIGN.md` tokens → the renderer's CSS-variable defaults; brand via `surfaceProperties` |
| the **prompt → generate → validate** loop | the `ux-component-library` skill (catalog selection, generation guidance, schema validation) |

A2UI owns the wire format + streaming + data-binding + security model; this framework owns the components, semantics, and tokens it deliberately omits — complementary layers, not competitors. (Early preview — expect spec churn.) Depth: skill ref `ai-ready-design-systems.md` §6.

---

## 12. The `DESIGN.md` protocol

`DESIGN.md` (Google) is a **portable snapshot of a project's visual identity** for coding agents: YAML token frontmatter + Markdown rationale, lintable (`npx @google/design.md lint` — checks broken refs, WCAG contrast, section order), round-tripping to `tokens.json` / Figma variables / Tailwind. Its philosophy is the §2.7 principle: **prose, not tokens, is the focus** — *"the quality of a generated design is determined less by the precision of its values than by how clearly the intent is described,"* and a specific reference carries its negative constraints for free.

**Canonical structure** (sections in this order; omit any, never reorder):
`Overview (Brand & Style) → Colors → Typography → Layout → Elevation & Depth → Shapes → Components → Do's and Don'ts`.
Token groups: `colors`, `typography`, `rounded`, `spacing`, `components` (+ any custom key — `motion`, `iconography` — the format accepts it). Color roles: `primary`, `secondary`, `tertiary`, `neutral`. References use `{path.to.token}`.

**When `DESIGN.md` is the right tool:** portable visual identity across tools/sessions/agents; quick prototyping in an unfamiliar environment; customer/brand theming; artistic direction. **When it is *not*:** as the system of record for component usage/anatomy/states (→ this framework + MCP); as the code-integration contract (→ Code Connect); as an always-on context dump (→ on-demand MCP). `DESIGN.md` answers *"what does our brand look and feel like?"* and **defers component semantics back to this framework + the MCP** — that deferral is what prevents the re-implementation failure.

### 12a. The gap-detection & self-prompting protocol

The framework must notice when a project *should* have a `DESIGN.md` and doesn't — and act. On entering design/build work for a project, run this check:

```
1. DETECT — Does a DESIGN.md (or equivalent token+rationale source) exist for this project?
   • Look for: DESIGN.md, design-tokens, a theme file, a Storybook theme, a brand doc.
   • If a token source exists but no rationale (the "why"), treat as PARTIAL.

2. JUDGE — Do this project's context and intent WARRANT one?  Warrant = YES when any hold:
   • The work will generate UI (screens, components, prototypes) for this project, AND
   • there is a distinct brand/visual identity to stay faithful to, OR
   • multiple agents/tools/sessions will touch the visual layer (portability matters), OR
   • output is drifting toward generic "slop" for lack of a visual-intent anchor.
   Warrant = NO for: throwaway one-offs, pure logic/back-end work, or projects whose
   identity is fully and freshly carried by an always-on source already in context.

3. ACT —
   • EXISTS & sufficient → load it; bind component work to its tokens; proceed.
   • PARTIAL → offer to enrich (add the missing rationale/Do's-and-Don'ts prose).
   • ABSENT & WARRANTED → SELF-PROMPT (below). Do not silently proceed to generate
     unbranded UI — surface the gap first.
   • ABSENT & NOT warranted → note the decision in one line and proceed.
```

**Self-prompt template** (what the agent raises, unprompted, when ABSENT & WARRANTED):

> *"This project (`<name>`) is about to generate UI but has no `DESIGN.md` to anchor its visual identity — which risks generic output and cross-session drift. I can author one from `<detected source: e.g. the Storybook theme / token package / brand doc>`: tokens (color, type, spacing, radius, elevation, motion) in the frontmatter, plus the brand prose and Do's/Don'ts that carry the intent. Want me to generate `DESIGN.md` now so all subsequent work stays on-brand?"*

On approval: extract real tokens from the detected source (never invent), write the prose against a *specific* reference (§2.7), lint it (`npx @google/design.md lint`), and place it at the project root. From then on, component work for that project binds to it.

> **Worked example:** Centric **C8 PLM** → `c8-plm/DESIGN.md`, authored via this protocol from the real CDS tokens (`cds-tokens.css` + the foundations docs), end-to-end (detect → warrant → generate from real tokens → lint: **0 errors**; remaining warnings are benign orphaned role-tokens + real AA findings now documented in the file's Do's/Don'ts). The authoring guide + annotated template live in skill ref `ai-ready-design-systems.md` §3.

---

## 13. Application playbooks

**Designing a screen / workflow** — name the user's job (JTBD) → the one primary action (your single primary Button) → run the Form trees (§6) for each value collected → run the Data trees for each value shown → choose overlays/messaging at the lowest rung → place exactly one primary nav pattern → **cover every state** (the async triad, §7) before "done."

**Building a layout** — group one-subject content into Cards; whitespace before Separator; Scroll Area for overflow (page scroll stays native); overlays only for temporary surfaces; Tabs vs Accordion by whether labels must always be visible.

**Auditing / triaging UI** — for each control: *is this the lowest-intensity correct component?* (Dialog where a Toast suffices; Combobox where a Select suffices; Carousel hiding important content; Switch where a Save-confirm Checkbox belonged; color-only status). Check the state matrix for gaps; check semantics (is the "menu" actually a Select? the "toggle" actually a Switch?); flag naming drift against the team's vocabulary. Run through [[06-qa-operating-model]].

**Transliterating headless code → Figma** — States → variant props; Anatomy → layers/slots; Variants → variant axes; Tokens → Figma variables (bind, don't hardcode); reconcile the *name* to the team's vocabulary but keep the canonical concept in the description; **carry the when-to-use/avoid into the component description** so intent travels. Pair with `figma-canvas-designer` + `figma-use` for canvas writes and `figma-code-connect` for the code binding.

---

## 14. The operating model — how the layers are consulted

```
Designer / agent has a UI need
      │
      ├─▶ name the QUESTION (§4) ───▶ run the TREE (§6) ──▶ candidate component
      │
      ├─▶ need exact states/anatomy/aliases? ──▶ query the MCP  (guidelines, on-demand)
      ├─▶ need the procedure/playbook? ─────────▶ the SKILL     (workflow)
      ├─▶ need the WHY / a law / the schema? ────▶ THIS FRAMEWORK (framing)
      ├─▶ need the brand's tokens & look? ───────▶ DESIGN.md     (constraints: look)
      └─▶ enforce "use DS / import not reimplement / a11y" ─▶ AGENTS.md + lint (constraints: rules)
```

**The binding** (drop into a project's `AGENTS.md`):

```markdown
## Design system context
- Resolve any component name to its CANONICAL BEHAVIOR before using it (see the
  Component & Pattern Framework §9). Names lie; behavior doesn't.
- Choose the LOWEST-INTENSITY component that works; one primary action per section.
- Cover every state (default/hover/focus/disabled + filled/error/loading/empty as relevant).
- IMPORT existing components; never re-implement. Bindings via Code Connect.
- Honor this project's DESIGN.md tokens. If none exists and UI work is starting,
  run the gap-detection protocol (Framework §12a) and self-prompt to author one.
- Meet the accessibility laws (Framework §8a): visible labels, focus management,
  correct ARIA roles, keyboard patterns, no color-alone, WCAG AA.
- Query the `ux-components` MCP for per-component specifics on demand; load this
  framework for the why; follow the ux-component-library skill for procedure.
```

---

## 15. Resource canon (annotated)

**The synthesis sources** — what each uniquely contributes.

- **UX Components dataset / `ux-components` MCP** (ux-components.com) — the 62-component × 68-system canon; intent, states, anatomy, 1,900+ name mappings. The live data layer of this system.
- **EightShapes / Nathan Curtis** (medium.com/eightshapes-llc, @nathanacurtis) — the **8-section component spec** (Anatomy · Properties · Layout & Spacing · Behavior · Accessibility · Motion · Component Tokens · Version History) and spec-vs-guidelines split; the **"as data"** series (*Components / Examples as Data*); **code-only props in Figma** (the hidden-layer mechanism); **the canonical state model** (*The Sorry State of States*); **purposeful-vs-aesthetic naming**; the **reimagined token taxonomy** (the Namespace→Object→Base→Modifier grammar); and **many-core-libraries** governance.
- **W3C Design Tokens (DTCG)** (designtokens.org) — the token JSON contract: `$value`/`$type`, `{group.token}` aliasing, composite types. The substrate beneath tokens, `DESIGN.md`, and Figma variables.
- **Brad Frost — Atomic Design** (atomicdesign.bradfrost.com) — atoms→molecules→organisms→templates→pages; the reuse gradient (components / recipes / snowflakes).
- **The Component Gallery** (component.gallery) — descriptive cross-system synonym dictionary ("also known as"); ~60 types, 90+ systems.
- **Open UI** (open-ui.org) — prescriptive name standardization; the research schema (Name · Concepts · Anatomy · States) and the convergence matrix.
- **Storybook / CSF** (storybook.js.org) — single-source living docs: args/argTypes as the props/API table; one story per state.
- **Material Design 3** (m3.material.io) — semantic color roles, tonal elevation, state-layer opacities, motion duration/easing tokens. The rationale for theme-adaptive visual decisions.
- **IBM Carbon** (carbondesignsystem.com) — the 2x grid + 8px mini-unit, productive-vs-expressive motion, data-density philosophy, governed patterns.
- **Apple HIG** (developer.apple.com/design/human-interface-guidelines) — Clarity/Deference/Depth; "which control and why"; 44pt target; platform adaptation.
- **WAI-ARIA APG** (w3.org/WAI/ARIA/apg) — the normative keyboard/role/focus patterns for dialog, menu, combobox, tabs, disclosure. The accessibility contract.
- **Refactoring UI** (refactoringui.com) — hierarchy via weight/color, the spacing scale, HSL color, paired shadows for depth.
- **Laws of UX** (lawsofux.com) — Fitts, Hick, Jakob, Miller, the **Doherty Threshold (~400ms)** — cognitive science tied to component thresholds.
- **Polaris content** (polaris.shopify.com) & **Mailchimp** (styleguide.mailchimp.com) — microcopy mechanics; voice-vs-tone.
- **Diana Wolosin — *Intent-Driven Context for AI Design Systems*** (designsystemscollective.com) — "Context is not documentation. Context is intent"; the four intent types → delivery mechanisms. The organizing idea of this framework.
- **Google `design.md`** (github.com/google-labs-code/design.md) — the portable visual-identity format + linter; the "prose over tokens / specific reference" philosophy.
- **Atlassian — *DESIGN.md in practice*** (atlassian.com/blog/ai-at-work) — the field test: where `DESIGN.md` wins (portability/theming) and where MCP+skills win (production); the three limitations this system is engineered around.
- **Figma MCP / Code Connect** (figma.com/blog, developers.figma.com) — design↔code binding; semantic naming → better AI code accuracy.
- **Into Design Systems — *Agentic Design Systems*** (intodesignsystems.com) — the three-layer architecture (always-on foundations + on-demand MCP + `AGENTS.md`); JSON-over-prose benchmarks.
- **AI-ready & agentic field guides** — Nick Babich / UX Planet (*DESIGN.md Best Practices*, *Creating an AI-Ready Design System Checklist*, *A/B Testing with Claude Code*), Design Systems Collective (*Using AI to Write DS Docs That Don't Suck*), Disco Lu (*Building Agentic Design Systems*) — the practical checklists, the AI doc-generation workflow, and the AI-as-user evaluation loop.
- **Google A2UI** (github.com/a2ui-project/a2ui) — the agent-to-UI protocol (swappable catalog + streaming JSON, on A2A/MCP); the runtime layer this system supplies components and tokens to (§11a).

---

## Appendix A — the 62-component quick reference

(intent one-liner per component; full detail in the MCP / [[ux-component-library]] inventory)

**Action** — Button (user-initiated action) · Toggle (stateful button, `aria-pressed`) · Toggle Group (connected single/multi toggles) · Toolbar (contextual action bar, roving tabindex).
**Form** — Input · Textarea · Label (the a11y layer) · Checkbox (deferred, multi) · Radio Group (2–5 exclusive) · Select (5–15) · Combobox (>15/filtered) · Switch (instant binary) · Slider · Rating · File Upload · Search · Number Input · Date Picker · Time Picker · Calendar · Color Picker · Form (container/validation).
**Navigation** — Link (navigates) · Breadcrumb · Tabs (parallel views) · Pagination · Dropdown Menu (action menu) · Context Menu (right-click) · Menubar (desktop File/Edit) · Navigation Menu (primary nav) · Stepper (sequential steps).
**Feedback** — Alert (persistent inline) · Toast (ephemeral) · Banner (page-wide) · Progress (determinate) · Spinner (indeterminate) · Skeleton (initial load) · Empty State · Meter (static gauge).
**Data Display** — Avatar · Badge (numeric/status) · Tag (textual) · Chip (interactive token) · List (one column) · Table (multi-column) · Data Table (sort/filter/paginate) · Tree View (hierarchy) · Timeline (chronology).
**Layout** — Card (one subject) · Separator (divider) · Scroll Area (custom scrollbar).
**Overlay** — Tooltip · Hover Card · Popover · Dialog (modal) · Alert Dialog (irreversible) · Sheet (edge panel).
**Disclosure** — Accordion (stacked sections) · Collapsible (single section).
**Content** — Carousel (cycling media) · Image · Icon.

---

## Appendix B — the blank schema + JSON contract

**Fill-in template** (the 18 facets, §5):
```
Identity · Intent · Context · Use · Avoid · Semantics · Anatomy · States · Variants ·
Behavior · Content · Visual(§8 dims) · Tokens · Relationships · Responsive/Platform ·
A11y · Definition-of-Done · Governance
```
**Machine record:** the `component intent record` JSON in §11 is the canonical contract — schema-validated, served on demand by the MCP, bound to a code symbol via Code Connect.

---

## Appendix C — canonical ↔ alias quick map (the false friends)

| If you hear… | It might mean… | Confirm by behavior |
|---|---|---|
| "Toggle" | Toggle *or* Switch | pressed button vs. pill-on-track |
| "Select" | Select *or* Combobox | fixed list vs. type-to-filter |
| "Tag" | Tag *or* Badge *or* Chip | textual / numeric-status / interactive |
| "Tooltip" | Tooltip *or* Popover | plain text vs. interactive content |
| "Banner" | Banner *or* Alert | page-wide vs. inline |
| "Menu" | Dropdown / Context / Navigation | action menu vs. right-click vs. wayfinding |
| "Drawer" | Sheet | edge-anchored overlay |
| "Modal" | Dialog *or* Alert Dialog | task vs. irreversible decision |
| "Snackbar"/"Flag" | Toast | ephemeral auto-dismiss |
| "Segmented Control" | Toggle Group | connected single/multi toggles |

---

## Relationship to the rest of the system

- **Above:** [[01-aesthetic-lens]] (why it feels right) and [[02-ui-ux-operational-framework]] (how to decide systematically) sit over this; this framework is the *component-and-pattern* specialization they route into.
- **Beside:** [[05-last-mile-craft-framework]] (the finishing discipline that enforces the state matrix and token usage) and [[06-qa-operating-model]] (the target-user QA bar — no curated subsets).
- **Below (delivery):** the [[ux-component-library]] skill (procedure), the `ux-components` MCP (per-component data), `DESIGN.md` (visual identity), and `AGENTS.md` + lint (enforcement). This framework is the hub they all point back to.
- **Companion references** (in the [[ux-component-library]] skill): `component-authoring.md` (components/props/states/examples *as data*), `tokens-and-naming.md` (the taxonomy grammar + purposeful naming), `ai-ready-design-systems.md` (AI-ready checklist · DESIGN.md authoring + gap-detection · A2UI). The reusable `AGENTS.md` binding lives at `02-shared-references/ds-agents-binding.md`; the worked `DESIGN.md` at `c8-plm/DESIGN.md`.
