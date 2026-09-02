---
title: Component Contract Schema (portable model v0.2)
tags: [reference, design-systems, components, contracts, schema, specs, governance]
created: 2026-07-28
updated: 2026-07-28
links:
  - "[[09-component-and-pattern-framework]]"
  - "[[component-contracts-and-schemas]]"
  - "[[ds-agents-binding]]"
---

# Component Contract Schema — portable model v0.2

`schema_version: 0.2.0` · status: **draft, unimplemented** — the model, the verification levels, and
the governance protocol. No tooling exists yet; adopt incrementally per §9.

The **why** lives in [[component-contracts-and-schemas]] (definitions, the seven gates, the wider
field) and [[09-component-and-pattern-framework]] §5a. This file is the **what**: the shape a contract
is written in, platform-neutral, so that any implementation — React, Vue, iOS, Android, Web Components,
**and Figma** — can sign it.

> This model deliberately does **not** replace the 18-facet documentation schema
> ([[09-component-and-pattern-framework]] §5). It is the **typed subset that arbitrates.** Facets that
> stay prose stay prose — they inform. Facets promoted here are the ones a machine must decide.

**v0.2 changelog.** Absorbed from the reference implementations surveyed 2026-07-28 (EightShapes
**Specs** schema + its 60-ADR corpus, Southleft **DS Contracts**, PJ Onori's **DSDS**): the
constitution (§0), the **variant-delta layering model + resolution algorithm** (§2.5),
**state classification — browser-driven vs consumer-controlled** (§2.4), `invalidPropConfigurations`
(§2.5), the `$binding`/`$ref`/`$extensions` conventions (§2.10), collapsed-or-expanded values and the
constraint→edge mapping (§3), the **opt-in-inference-with-declared-false-positives** rule (§4), the
three-way differ (§5), and the explicit **contract boundary** (§8).

---

## 0. The constitution — three rules the model itself obeys

Borrowed wholesale from the Specs schema's own constitution, because all three earn their place:

| # | Rule | Why it matters |
|---|---|---|
| **I** | **Type–schema symmetry.** Every change to the type definition has a corresponding change to the validation schema, in the same commit. No drift, ever. | Drift between the type and its validator is how a "verifiable" contract silently stops verifying. Three ADRs in the reference corpus exist purely to fix this class of bug. |
| **II** | **No runtime logic in the model.** The schema holds **pure data shapes**. Merge semantics, inference heuristics and transforms are *described* here and *implemented* elsewhere. | Keeps the contract readable by every party. The moment behavior lives in the model, only one runtime can implement it. |
| **III** | **Minimal, stable, intentional API.** Adding an optional field is MINOR. Removing or renaming a field is MAJOR and needs an ADR. | Consumers pin the model. Churn in the model is more expensive than churn in the content. |

---

## 1. The two versioned things

Every contract carries both, and consumers pin both:

```yaml
schema_version: 0.1.0   # the MODEL — what a contract can say. Semver. Changed only via ADR (§6).
spec_version:   3.2.1   # the CONTENT — what this contract does say. Semver per component or library.
```

| Change | Bumps | Consumer impact |
|---|---|---|
| New optional field in the model | schema **minor** | none until used |
| Field re-typed / removed / semantics changed | schema **major** | must migrate; opt-in window |
| New component, new prop, new variant | spec **minor** | additive |
| Prop removed, enum value dropped, default changed | spec **major** | breaking for implementers |
| Style value changed (`backgroundColor`, spacing…) | spec **patch** | regenerate, no code change |

---

## 2. The model

### 2.1 Top level

```yaml
component:
  id: string                # stable, kebab-case, never renamed (aliases carry old names)
  name: string              # display name
  aliases: [string]         # cross-system + team vocabulary (canon resolution — §9 of the framework)
  category: enum            # action | form | navigation | feedback | data-display | layout |
                            # overlay | disclosure | content
  status: enum              # draft | alpha | stable | deprecated
  intent: string            # ≤144 chars, verb-led, non-normative prose
  api: {...}                # §2.2 — props
  anatomy: {...}            # §2.3 — elements
  states: {...}             # §2.4 — the four separated concerns
  stateClassification: {...}#      — browser-driven vs consumer-controlled (§2.4)
  default: {...}            # §2.5 — the COMPLETE baseline every variant layers onto
  variants: [...]           # §2.5 — configuration → element deltas
  invalidPropConfigurations: [...]  # §2.5 — combinations that must NOT exist
  behavior: {...}           # §2.6 — keyboard, focus, timing
  a11y: {...}               # §2.7
  examples: [...]           # §2.8 — composition, captured separately from variants
  governance: {...}         # §2.9 — owner, code binding, changelog ref
  $extensions: {...}        # §2.10 — the sanctioned platform-metadata escape hatch (DTCG)
  notes: [string]           # EXPLICITLY NON-NORMATIVE. Deleting any note must not change the contract.
```

**Two escape hatches, and the difference matters.** `$extensions` (§2.10) is the **structured** one —
platform-specific metadata, reverse-domain keyed, still typed and still validated. `notes` is the
**unstructured** one and it is load-bearing that it stays empty of decisions: anything in `notes` that
fails the deletion test (delete it — does the contract change?) is misfiled and must be promoted into a
typed field or cut. A contract with a fat `notes` array is a description with extra steps.

### 2.2 `api` — props, typed and closed

```yaml
api:
  size:
    type: enum
    values: [small, medium, large]
    default: medium
    surfaces: [design, code]        # design | code | both — code-only props (handlers, ids, aria) never leak to Figma
  loading:
    type: boolean
    default: false
    surfaces: [code]
  rowHeight:
    type: number
    unit: px                        # unit is DECLARED, never inferred from the value
    default: 40
  onSelect:
    type: handler
    signature: "(ids: string[]) => void"
    surfaces: [code]
```

Legal `type` values: `enum` · `boolean` · `number` · `string` · `token` · `node` (slot/content) ·
`component` (an instance of another contract, by `id`) · `handler` · `array<T>` · `object<Shape>`.

**Rules.**
- No untyped values. A bare string is a type declaration, not a default place to put things.
- Enums are **closed** — `values` is exhaustive; an unlisted value is invalid, not "custom."
- `unit` is declared for every numeric. Never `"16px"` as a string.
- **No platform-native prop types.** `INSTANCE_SWAP` → `component`; Figma `TEXT` props whose values are
  numeric → `number`, re-typed at the transform, not at read time.
- `surfaces` makes design/code divergence explicit rather than a surprise at handoff.

### 2.3 `anatomy` — elements, typed by what they can carry

```yaml
anatomy:
  root:     { kind: container, children: [leadingIcon, label, trailingIcon, spinner] }
  label:    { kind: text }
  leadingIcon:  { kind: glyph, optional: true }
  trailingIcon: { kind: glyph, optional: true }
  spinner:  { kind: component, ref: spinner, optional: true }
```

`kind`: `container` · `text` · `glyph` · `image` · `component`.
**The typing does real work:** a `text` element may not take `backgroundColor`; a `container` may not
take a glyph name; a `glyph` must resolve to a name the icon library actually ships (verification
level 2, §5).

### 2.4 `states` — four separated concerns, and each one *classified*

```yaml
states:
  interaction: [rest, hover, active, focus]      # enum — exactly one at a time
  configuration: [disabled, readonly, loading]   # BOOLEANS — independently combinable
  validation: [none, error, warning, success]    # enum
  selection: [none, selected, indeterminate]     # enum
```

Collapsing these into one enum is the field's most common Gate-1/Gate-2 failure: it cannot express
`readonly + focus` or `hover + error`, and it forces synonyms (`default` / `enabled` / `resting`) to
multiply. Normalize synonyms to `rest`. See [[09-component-and-pattern-framework]] §8d.

#### State classification — browser-driven vs consumer-controlled

**The separation above is necessary but not sufficient.** Each state must also declare *who causes it*,
because that decides whether it appears in the component's API at all. This is the single most
practically valuable idea absorbed from the Specs schema (its ADR-055), and it resolves a confusion our
own state model left open.

```yaml
state_classification:
  hover:      { driver: browser,  selector: ":hover",                          inApi: false }
  active:     { driver: browser,  selector: ":active",                         inApi: false }
  focus:      { driver: browser,  selector: ":focus-visible",                  inApi: false }
  disabled:   { driver: consumer, selector: ':disabled, [aria-disabled="true"]', inApi: true }
  readonly:   { driver: consumer, selector: "[readonly]",                      inApi: true }
  checked:    { driver: consumer, selector: ':checked, [aria-checked="true"]', inApi: true }
  expanded:   { driver: consumer, selector: '[aria-expanded="true"]',          inApi: true }
  pressed:    { driver: consumer, selector: '[aria-pressed="true"]',           inApi: true }
  selected:   { driver: consumer, selector: '[aria-selected="true"]',          inApi: true }
  invalid:    { driver: consumer, selector: '[aria-invalid="true"]',           inApi: true }
```

- **Browser-driven** states happen through user interaction. The application never sets them, so they
  are **omitted from the props interface** and rendered as pseudo-class selectors.
- **Consumer-controlled** states are set explicitly. They **belong in the props interface** and map to
  an ARIA attribute or native attribute selector.
- Anything unclassified falls back to a `data-*` attribute — a visible, greppable "undecided" marker
  rather than a silent guess.

**One classification drives two outputs** (the styling selector and the API surface), which is exactly
Gate 2: state each decision once. It also kills the most common component-API bug in design systems —
shipping a `hover` prop.

### 2.5 `variants` — deltas over a default, resolved by specificity

A component with 3 boolean props has 8 configurations; fully expanding them across ~15 elements × ~40
properties is ~4,800 entries for a component with maybe a dozen real decisions. The **layering model**
(from Specs) records only what changes and cuts output by 95%+ while remaining lossless.

```yaml
default:                                # COMPLETE baseline — every element, every property
  elements:
    root:
      backgroundColor: "{color.action.primary}"
      cornerRadius: "{radius.md}"
      padding: 12                       # collapsed scalar — uniform
    label:
      color: "{color.on.action.primary}"
      typography: "{type.body.md}"

variants:                               # DELTAS only
  - configuration: { disabled: true }
    elements:
      root: { opacity: 0.36 }

  - configuration: { size: small }
    elements:
      root:   { padding: { top: 4, end: 8, bottom: 4, start: 8 } }   # expanded — sides differ
      label:  { typography: "{type.body.sm}" }

  - configuration: { variant: primary, interaction: hover }
    elements:
      root: { backgroundColor: "{color.action.primary.hover}" }

invalidPropConfigurations:              # combinations that must NOT exist
  - { variant: ghost, elevation: raised }
  - { loading: true, disabled: true }
```

**Resolution algorithm** (deterministic — same config in, same styles out):

1. Start from `default` (the complete baseline).
2. Select every variant whose `configuration` is a **subset** of the target configuration, with exact
   value matches.
3. Apply them in **specificity order** — fewer configuration keys before more.
4. Later layers override earlier ones by **property-level replacement**, *not* deep merge.

**Property-level replacement is a rule, not an accident.** If `default` has `padding: 12` and a variant
declares `padding: { top: 4, … }`, the entire prior value is discarded — no field-by-field merge. Same
for color (a token reference is replaced wholesale by an override), typography, and effects. Deep-merge
semantics are where "why is this component 2px off" bugs live.

**Rules.**
- A variant is a **condition → delta** pair, never a row in a cross-product. One decision, one place.
  (The anti-pattern: 96 Figma variants each re-stating the same disabled opacity — ~500 layers for one
  intent.)
- **`invalidPropConfigurations` is required, not optional.** A contract that can only say what is legal
  and never what is illegal cannot reject a real class of malformed spec. Most systems omit this and
  discover the illegal combinations in QA.
- Style values are **token references** (`{group.token}`, DTCG) or typed literals with declared units.
  Raw hex in a variant is a Gate-2 failure waiting to drift.
- Sides are `start` / `end`, never `left` / `right` — RTL and cross-platform both depend on it.
- Positioning is expressed as **edges + offsets**, not any tool's `constraints` model (§3).
- Output mode is declared: `LAYERED` (deltas, the default) or `FULL` (every variant fully resolved) —
  consumers that can't implement the merge get `FULL` without changing the source of truth.

### 2.6 `behavior`

```yaml
behavior:
  keyboard:
    - { keys: [Enter, Space], action: activate }
    - { keys: [Escape], action: dismiss, when: { overlay: true } }
  focus:
    model: roving-tabindex        # roving-tabindex | aria-activedescendant | natural | trap
    returnsTo: trigger            # for modal surfaces
  timing:
    openDelayMs: 0
    autoDismissMs: null
```

### 2.7 `a11y`

```yaml
a11y:
  role: button
  requiredNames: [{ when: { iconOnly: true }, via: aria-label }]
  minTargetPx: 44
  contrast: { focusRing: 3.0, text: 4.5 }     # numeric floors, machine-checkable
  liveRegion: null
```

### 2.8 `examples` — composition, captured distinctly from variants

```yaml
examples:
  - id: with-leading-icon
    props: { size: medium }
    slots: { leadingIcon: "icon:plus", label: "Add material" }
  - id: loading
    props: { loading: true }
```

Variants describe *how it varies*. Examples describe *how it is composed*. Conflating them is what
produces variant explosions.

**Demo content is not a default.** `default` is the value the component takes when the consumer says
nothing. `examples` is illustrative content for docs, Figma and stories. Putting `"Add material"` in
`default` means every consumer inherits a label they never asked for — the reason every generated
TabsTrigger in a library ends up saying "List view." Keep `default` optional and `examples` separate.

**Two kinds of example, and only one belongs inside.** *Composition* examples (which slots hold what,
which instances nest) are structured and verifiable — they belong here. *Usage/guidance* examples
("what makes a good pricing card") are judgment and prose — they sit **alongside** the contract, in the
documentation layer, never inside it (§8).

### 2.9 `governance`

```yaml
governance:
  owner: design-system
  codeBinding: { import: "@ds/button", symbol: Button }
  figmaBinding: { fileKey: "…", componentKey: "…" }     # a signatory, not the source
  adrs: [ADR-0007-sides, ADR-0012-numbers]
  changelog: ./CHANGELOG.md
```

### 2.10 Reserved-key conventions

Four reserved keys, each with exactly one job. Collisions between them are a known failure mode — the
reference schema burned an ADR renaming its binding key after it collided with JSON Schema's `$ref`.

| Key | Means | Example |
|---|---|---|
| `$ref` | **JSON Pointer** to another node in this document. Structural reference only. | `instanceOf: { $ref: "#/subcomponents/icon" }` |
| `$binding` | **Bind a value to a prop.** Deliberately *not* `$ref`, to avoid the JSON-Schema collision. | `content: { $binding: "#/api/label" }` |
| `$token` | A DTCG token reference with its `$type`. | `{ $token: "color.action.primary", $type: "color" }` |
| `$extensions` | **DTCG-standard platform metadata**, reverse-domain keyed. The *only* sanctioned place for platform-specific data. | `$extensions: { "com.figma.plugin": { nodeId: "1:23" } }` |

**`Conditional` — declarative logic without runtime logic.** Visibility and similar derived values are
expressed as data, satisfying Constitution II:

```yaml
elements:
  spinner:
    visible: { if: { $binding: "#/api/loading" }, then: true, else: false }
  trailingIcon:
    visible: { if: { $binding: "#/api/trailingIcon" }, condition: "notNull", then: true, else: false }
```

This is what keeps "the spinner shows when loading" *verifiable* instead of a sentence someone has to
read.

---

## 3. Platform-neutrality conventions (Gate 3, made concrete)

| Never | Always | Why |
|---|---|---|
| `left` / `right` | `start` / `end` | RTL; iOS/Android/CSS logical properties |
| Figma `constraints` | edges + offsets | `constraints` is an approximation of three other models |
| `INSTANCE_SWAP` | `type: component, ref: <id>` | tool-native types can't be implemented off-platform |
| `"16px"` (string) | `{ type: number, unit: px }` | strings can't be validated or converted |
| raw hex in a variant | `{token.reference}` | one theme-control point |
| CSS-only shorthands | explicit per-side / per-axis fields | shorthand parsing differs per platform |
| implied state in a name | the `states` model (§2.4) | `button-primary-hover` is unverifiable |

**Accept bias by name, reject bias by model.** Calling the block `variants` is a naming inheritance and
is fine; encoding a tool's *data model* is not. Cull leaks over time rather than stalling on purity.

### 3.1 Collapsed-or-expanded values

Normalization applies at the *value* level too, not just the decision level:

```yaml
padding: 12                                          # collapsed — all sides uniform
padding: { top: 4, end: 8, bottom: 4, start: 8 }     # expanded — only when they differ
cornerRadius: 8                                      # collapsed
cornerRadius: { topStart: 8, topEnd: 8, bottomEnd: 0, bottomStart: 0 }   # expanded
```

Emitting four properties when one value would do is the same redundancy failure as a 96-variant
disabled opacity, one level down. It also gives consumers a cheap uniformity check (`typeof padding ===
"number"`) instead of comparing four fields.

### 3.2 Why `start`/`end` and not `leading`/`trailing`

Worth recording, because the question recurs and there are three candidates, not two:

| Model | Used by | Why not chosen |
|---|---|---|
| `left` / `right` | Figma API, CSS physical properties | Assumes LTR. Every RTL-aware consumer must flip them itself — which is the consumer doing the contract's job. CSS itself is moving to logical properties. |
| `leading` / `trailing` | SwiftUI / UIKit | Typographic terms borrowed from *text* direction; confusing when applied to padding or stroke weight, which are layout, not text. |
| **`start` / `end`** ✅ | CSS logical properties, Android/Compose | Direction-agnostic, already standard on two of three target platforms, reads correctly for non-text properties. |

### 3.3 Neutralizing anchored positioning

Tool `constraints` models must be transformed into named edges. The mapping is mechanical, so specify
it rather than leaving each consumer to re-derive it:

| Source constraint | Horizontal → | Vertical → | Dimension |
|---|---|---|---|
| `MIN` | `start` (px from inline-start) | `top` (px from block-start) | preserved |
| `MAX` | `end` (px from inline-end) | `bottom` (px from block-end) | preserved |
| `CENTER` | `centerHorizontalOffset` | `centerVerticalOffset` | preserved |
| `STRETCH` | `start` **+** `end` | `top` **+** `bottom` | `width`/`height` → `null` |
| `SCALE` | `start` as a percentage string (`"25%"`) | `top` as a percentage string | `width`/`height` → `null` |

The failure this prevents: a consumer receiving `x: 24` has no way to know whether that means 24px from
the left edge, 24px from the right edge, or centered with a 24px offset. Raw coordinates are testimony;
named edges are contract.

---

## 4. The transform boundary — testimony → contract

```
  Figma file / legacy code / prototype
            │  extract  (deterministic, no LLM)
            ▼
       RAW EXTRACT           ← testimony. Never published as the contract.
            │  transform (configured, mechanical, versioned rules)
            ▼
     CONTRACT (this schema)  ← validated at levels 1–2 (§5)
            │  generate (deterministic)
            ▼
  CSS · TS types · stories · scaffolds · docs · Figma library
```

Three rules on this boundary:

1. **No LLM between extract and contract.** Inference here is invisible and hardens. Configured
   transforms only — naming conventions, re-typing heuristics, side mapping — each with an ADR.
2. **Downstream consumers read the contract, not a prose rendering of it.** If an agent smooths the
   contract into markdown and the next consumer reads *that*, verification stopped at the boundary.
3. **AI at authoring time; determinism at run time.** A model is excellent at the one-time judgment
   work of *writing* a contract from a messy legacy source. It is the wrong tool for the recurring work
   of *enforcing* one. Or, as TJ Pitre puts it: **"Authority belongs to whatever layer can refuse
   deterministically, not whatever layer instructs loudest. A model can be talked around. A schema
   can't."**

### 4.1 Heuristics are allowed — undeclared heuristics are not

Some transforms genuinely cannot be exact. Re-typing a numeric-looking string prop to a number is the
canonical case: the source tool has no number type, so `"24"` and `"Submit"` arrive identically typed.
The rule that keeps this inside Gate 5 is **declare the guard and declare its false positives**:

```yaml
inference:
  inferNumberProps:
    enabled: false                       # OPT-IN. Never on by default.
    guard: >
      Not "" or "-"; no leading zero before another digit ("007", "0800", "01" rejected;
      "0", "0.5", "-0.5" allowed); Number(v) is finite.
    knownFalsePositives:
      - '"90210" — a postal code, inferred as a number'
      - '"1.0"  — a version string, inferred as a number'
```

Three properties make this legitimate rather than hand-waving: it is **opt-in**, the guard is
**written down and testable**, and the cases it gets wrong are **named in advance**. A heuristic that
declares where it fails is configured inference; one that doesn't is hoped-for inference.

---

## 5. Verification levels

| Level | Question | Mechanism | Gate |
|---|---|---|---|
| **L1 — structural** | Is this a validly structured spec? | JSON Schema validation of the model | 1, 4 |
| **L2 — referential** | Does everything it names exist? | tokens resolve · glyphs ship · `component` refs resolve · `codeBinding` symbol exists | 4 |
| **L3 — determinism** | Is generation stable? | generate twice → **empty diff** | 5 |
| **L4 — conformance** | Is it precisely implemented? | per-implementation conformance tests derived from the contract (state matrix, a11y floors, token bindings) | 4 |
| **L5 — coverage** | Is anything undecided? | every element × every state combination resolves to a value or an explicit inherit; `invalidPropConfigurations` populated | 1, 2 |
| **L6 — three-way agreement** | Do contract, design library and code still agree? | a **differ** that compares all three and reports exact mismatches, run in CI | 2, 6 |

L1–L3 are cheap and should gate every commit. L4 is per-implementation and is what makes the contract
*arbitrate*. L5 is the audit pass. **L6 is the one that keeps the contract true over time** and is the
practice Southleft's DS Contracts is built around: never let the design library and the code update
each other directly — changes land in the contract, get reviewed like code, then both regenerate, and
the differ proves they still match. It is a compiler, not a generative model.

**The evidence that this pays.** Southleft's published A/B test: an ungoverned agent building UI scored
**69/100 with 90 violations**; the *same model* held to the contract as a strict rulebook scored
**100/100**, and reported gaps instead of fabricating values. Deterministic extraction is likewise
cited at ~1 second and zero tokens per component versus 5–10 minutes and ~100k tokens for an agentic
pass. Treat both as directional, not universal — but the direction is not in dispute.

---

## 6. Evolution protocol (ADRs)

Any change to the **model** requires an ADR. Changes to **content** do not.

```markdown
# ADR-00NN — <decision>
Status: proposed | accepted | superseded by ADR-00MM
Date: YYYY-MM-DD
schema_version: 0.1.0 → 0.2.0

## Context      — what forced the question
## Decision     — the change to the model, precisely
## Surface      — every part of the schema this touches (api · anatomy · states · variants ·
                  examples · storage · generators · downstream consumers)
## Alternatives — what was rejected and why
## Migration    — what breaks, what auto-migrates, the opt-in window
## Verification — which of L1–L5 changes
```

**Publish the diff, not the narrative.** Consumers must be able to see exactly what changed and opt in
when their own tooling is ready. Downstream pushback that delays a generation pass by a week is a
**success signal** — it means coordination replaced interpretation.

---

## 7. Two adoption directions — extract, or generate

Both the surveyed implementations agree Figma is not the source. They disagree about which way the
arrow points, and the answer is *situational*, not doctrinal:

| Direction | Shape | When it fits | Cost |
|---|---|---|---|
| **Extract → transform** (Curtis / Specs) | The library already exists in Figma. Read it, neutralize it, publish the contract. | Brownfield. A mature design file that is ahead of code. | Ongoing transform maintenance; testimony risk if the transform is skipped |
| **Generate ← contract** (Vallaure / DS Contracts) | The contract is authored first; a plugin *builds* the Figma variants and the code from it. | Greenfield, or a library being rebuilt anyway. | Higher up-front; designers give up hand-building variants |

They converge in practice: extract once to bootstrap the contract, then flip to generate so the
contract stays upstream of both. **Our `figma-repo-sync-plugin` already runs the generate direction
(code → Figma); adding the contract makes it code → *contract* → Figma, which is the shape both sources
are pointing at.**

---

## 8. The contract boundary — what a contract must NOT absorb

A contract that tries to hold everything becomes unverifiable and rots (Gate 6). Both reference
implementations draw the same line, and it is sharper than it first looks:

| Stays **in** the contract | Stays **out** |
|---|---|
| The **required outcome**: "focus returns to the trigger on close" | The **technique**: how you implement the focus trap |
| Keyboard **map**: which keys do what | Interaction **craft**: drag physics, typeahead tuning, easing curves |
| Token **bindings** and computed values | CSS craftsmanship, the cascade strategy |
| **Composition** examples (which slots hold what) | **Usage** examples ("what makes a good pricing card") |
| a11y **floors** (contrast ratios, target size, roles) | The a11y *implementation* review |
| When a configuration is **invalid** | When a component is the **wrong choice** — that is §6 of the framework, and it is judgment |

**The load-bearing distinction: outcome vs technique.** "Focus returns to the trigger" is testable, so
it is contract. "Use a focus-trap library with `inert`" is craft, so it is code. Getting this wrong in
either direction is expensive — pull craft in and the contract can't be kept true; push outcomes out
and the contract can't arbitrate the thing implementations most often get wrong.

**Corollary:** the contract does not replace [[09-component-and-pattern-framework]] §4/§6/§7 — the
taxonomy, the *which component* trees, and composition guidance are judgment layers that sit above it.
A contract tells you what *our* Dialog is. It never tells you that you wanted a Sheet.

---

## 9. Adoption path (don't build this all at once)

| Step | Do | Cost | Unlocks |
|---|---|---|---|
| 0 | Run the **investment gate** ([[component-contracts-and-schemas]] §3). Below it → stay on markdown, stop here. | minutes | not wasting months |
| 1 | Pick **one** component under real change pressure (a migration is ideal). Author its contract by hand against §2. | hours | the model meets reality |
| 2 | Write the **JSON Schema** for §2 and validate that one file (L1). | hours | malformed becomes impossible |
| 3 | Add **L2 referential** checks against the real token file + icon set + code exports. | hours | the contract stops naming things that don't exist |
| 4 | Generate **one** artifact deterministically (TS types, or the story matrix). Prove L3 with `generate && generate && diff`. | days | evidence the contract is good |
| 5 | Add the **extract → transform** stage for the tool that currently supplies testimony (§7). | days | Figma becomes a signatory, not the source |
| 6 | Add the **three-way differ in CI** (L6) — contract vs design vs code. | days | the contract stays true without vigilance |
| 7 | Version the schema, start the **ADR log**, publish diffs. | ongoing | L4 maturity |

**Stop at the rung that pays.** Steps 0–3 alone convert a description into a verifiable spec and are
worth doing for a single high-churn component.

**A capacity warning worth taking seriously.** Vallaure's observation on who can actually run this:
solo and very small teams don't need a contract (no handoff to arbitrate); **mid-size orgs (~20–200)
have the highest need and the lowest capacity to build the tooling**; enterprises fit because they can
staff it. *"Both need it, the middle and the top. Only one can run it."* If you are in the middle, bias
hard toward steps 0–3 on one component and toward adopting an existing format over authoring tooling.
The field is roughly where tokens were before Style Dictionary and Tokens Studio made them tractable.

---

## Appendix — the format landscape (as of 2026-07)

These solve **different layers** and are complements, not competitors. Knowing which layer a format
occupies prevents adopting the wrong one:

| Format | Layer | Models | Maturity |
|---|---|---|---|
| **DTCG** (designtokens.org) | values | tokens — `$value`/`$type`/aliasing/`$extensions` | stable spec (v2025.10); broad tool adoption |
| **Specs** (EightShapes / Curtis) | **component decisions** — the contract layer | anatomy · props · default + variant deltas · styles · subcomponents · examples | ~60 ADRs, versioned schema, CLI |
| **DS Contracts** (Southleft) | **component decisions** + reconciliation | contract as the neutral third artifact; three-way differ; generates Figma *and* code | 51 contracts, 282 tokens, published A/B evidence |
| **DSDS** (PJ Onori) | **documentation** — docs as data | 6 entity types (components, tokens, themes, foundations, patterns, guides) × 17 typed `kind` blocks (anatomy, api, states, variants, interactions, accessibility, content, guidelines, motion, principles, use-cases…) | draft v0.15.2 (2026-07) |

**The mapping onto our own system is clean and worth stating:** DSDS is the machine-readable form of
[[09-component-and-pattern-framework]]'s **facets 1–17** (documentation); Specs / DS Contracts are the
machine-readable form of **facet 18** (the arbitration record). This file models the latter. If we ever
want the former as data rather than prose, DSDS is the format to adopt rather than invent.

**Convergence is the goal, not our own format.** Tokens took ~a decade to reach a stable spec; JSON
Schema took two. The right posture is to model against these, keep our shape close enough to migrate,
and adopt whichever converges — not to defend a bespoke schema.

---

## Related

- [[component-contracts-and-schemas]] — definitions, the seven gates, the investment gate, the ladder,
  the wider field and its reconciliations
- [[09-component-and-pattern-framework]] — §5a the contract layer · §5 the 18 facets · §11 the AI-legible
  record · §12 `DESIGN.md`
- [[ds-agents-binding]] — the `AGENTS.md` enforcement block that points agents here
- [[artifact-standards]] · [[epistemic-standards]] — workspace-wide output and evidence bars
- [[figma-tailwind-token-pipeline]] · [[radix-derived-color-system]] — DTCG/token-layer precedent
- [[figma-variable-state-representation]] — our own prior state-modeling work, which §2.4's
  classification layer extends
