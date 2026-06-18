# Component Authoring — components, props, states & examples *as data*

> The procedural layer for **authoring and documenting** a component in Figma + code + spec. Distilled from Nathan Curtis / EightShapes (*Components as Data*, *Component Examples as Data*, *Code-only Props in Figma*, *The Sorry State of States*, *Component Specifications*). Companion to framework **§5 (the Universal Component Schema)** — that file is *what facets a component has*; this is *how to build and document them*.

---

## 1. The "as data" principle

Define a component **once** as structured, platform-agnostic data (YAML/JSON) — then Figma, code, and AI all generate from that single source rather than maintaining parallel artifacts. A component record has four backbone keys, plus examples:

```yaml
Button:
  anatomy:   # the named parts (hierarchical)
  props:     # the configurable API (3 buckets — see §3)
  default:   # default styling per element (token refs or raw values)
  variants:  # conditional style overrides keyed on prop configurations
  examples:  # composition, NOT variants (see §5)
```

Scale reality (Curtis): a simple component ≈ 20–50 lines of data; complex (Alert, TextInput) ≈ 500+; a team's `core.yaml` of 30–50 components runs into tens of thousands of lines.

## 2. Anatomy as data

Each element carries a `type` (`container | slot | text`), nests hierarchically, and names **nested-component dependencies** (a Button inside an Input):

```yaml
anatomy:
  root:          { type: container }
  content:       { type: container }
  leadingVisual: { type: slot, oneOf: [icon, avatar, image], nullable: true }
  label:         { type: text }
```

## 3. Props as data — the three buckets

Tag every prop by **where it lives**. This is the bridge between Figma and code (and the fix for "the Figma component and the code component disagree").

| Bucket | Exists in | Examples |
|---|---|---|
| **Figma-only** | design only | decorative-layer toggles, instance-swap scaffolding |
| **Shared** | both | `variant`, `size`, `disabled`, text content, instance swaps |
| **Code-only** | code/spec only, hidden from designers | a11y, semantics, constraints, behavior |

**Code-only prop catalog** (Curtis's set, + the handler/id set you should add):
`accessibilityLabel` (→ `aria-label`/`<label>`), `as` (semantic tag: `button|a|h1…h4`), `level`, `src`, `altText`, `minLength`/`maxLength`, `minRows`/`maxRows`, `items anyOf` / `minItems` / `maxItems`, `validation` — **plus** `onClick`/`onChange` handlers, `id`, `htmlFor`, `name`, `type`, `autoComplete`.

**How to carry code-only props *inside* a Figma component** (so one Figma asset emits a complete spec):
1. Add a layer literally named **`Code only props`** as a child of the component's **root** layer.
2. Geometry: position **(0,0)**, width & height **0.01**, **clip contents on** → effectively invisible.
3. Inside it, place text / nested-instance layers **bound to real component props**.
4. **Selectively hide** the irrelevant bound props from the designer's Properties panel.
5. A handoff plugin reads these as **metadata, not layout** — emitting them into the spec and discarding the Figma scaffolding.

## 4. States as data — escaping "the sorry state of states"

"States" is an overloaded grab-bag; design tools model it as one enum, code models it as many booleans, and they break on handoff. **The fix is to separate the concerns into distinct properties** instead of one mega-enum:

| Concern | Shape | Values |
|---|---|---|
| **Interaction** | enum `state` | `rest \| hover \| active \| focus` |
| **Configuration** | booleans | `disabled`, `readonly` (never members of the state enum) |
| **Validation** | enum `validation` | `none \| error \| success` (Primer precedent: `validationStatus`) |
| **Selection** | enum/booleans | `selected`, `indeterminate` |

Rules:
- **Normalize synonyms on import:** `resting / initial / default / enabled` → `rest`; `hovered` → `hover`; `focused` → `focus`.
- **Support valid cross-concern combinations** a single enum can't express: `readonly + focus`, `hover + error`. Author Figma variant props as orthogonal axes so these compose.
- Don't over-model — "completeness loses steam before perfection." Cover the matrix that matters (framework §5 law: default/hover/focus/disabled + filled/error/loading/empty as relevant), not every theoretical combination.

The full per-component state set is the **build/QA gate** — run it through [[06-qa-operating-model]].

## 5. Examples as data — composition, not variants

Variants capture only what's *built into* a component; real usage is **composition**, which is wider. So examples are their own data output, **not more variants**.

- **Source:** harvest Figma instances discovered by layer-name pattern or by `parent` — convention: a frame/section literally named **`Examples`**.
- **Emit two collections:** `instanceExamples` (ready-made component instances) and `slotContentExamples` (what's composed into each slot).
- **Intent-bearing placeholders:** prefer context-scoped fills (`{Vacation package title}`) over bare generics (`{Title}`) — tight enough to swap, meaningful enough to guide.
- **Guidance metadata** layered onto examples: `do/don't`, and a `must / should / could / avoid / never` priority.

```yaml
examples:
  instanceExamples:
    - id: alert-with-action
      component: Alert
      props: { variant: warning, dismissible: true }
      slots:
        title: "{Payment overdue}"
        description: "{Update billing to avoid interruption}"
        actions: [Button#review, Button#dismiss]
      guidance: { do: "lead with the consequence", dont: "stack more than one" }
```

## 6. The component specification (Curtis's 8 sections)

A **spec** documents *how to make* a component (builder-facing); **guidelines** document *how to use* it (consumer-facing). Ship specs first; save guidelines for nearer release. Sections, in order:

1. **Anatomy** — parts, visual attributes per part, nested-component dependencies
2. **Properties** — each prop: default vs alternatives, light/dark, token application; non-visual (code/a11y/content) props in a **table**
3. **Layout & Spacing** — padding/margin/item-spacing, direction/alignment, wrapping & overflow, responsiveness, sizing, touch targets
4. **Behavior & Animation** — events (click/mousedown/drag) and the state changes they trigger
5. **Motion** — timing, easing
6. **Accessibility** — auditable: screen reading, focus order, announced order, alt text; element-by-element role annotations
7. **Component Tokens** — table mapping each component token → **description · alias · Figma style name · default value**
8. **Version History** — changes across cycles/releases

(Foundation & component entries are ordered **alphabetically**.)

## 7. The single component record (worked — combines §1–6)

```yaml
Button:
  anatomy: { root: {type: container}, label: {type: text}, leadingVisual: {type: slot, oneOf: [icon], nullable: true} }
  props:
    variant:    { type: enum, enum: [primary, secondary, ghost, destructive], surface: shared }
    size:       { type: enum, enum: [sm, md, lg], default: md, surface: shared }
    disabled:   { type: boolean, default: false, surface: shared }      # boolean, NOT in state enum
    state:      { type: enum, enum: [rest, hover, active, focus], default: rest, surface: shared }
    validation: { type: enum, enum: [none, error, success], default: none, surface: shared }
    accessibilityLabel: { type: string, surface: code-only }            # → aria-label (icon-only)
    as:         { type: enum, enum: [button, a], surface: code-only }
    onClick:    { type: handler, surface: code-only }
  default:  { elements: { root: { styles: { backgroundColor: "{color.action.primary}", rounded: "{rounded.md}" } } } }
  variants:
    - configuration: { state: hover }
      elements: { root: { styles: { backgroundColor: "{color.action.primary-hover}" } } }
  examples:
    instanceExamples: [ {id: save, props: {variant: primary}, slots: {label: "{Save changes}"}} ]
```

## 8. Three rules to bake into Figma authoring

1. **State modeling:** author `state` as an interactive-only variant prop (`rest/hover/active/focus`); model `disabled`, `readonly`, `validation`, `selected` as *separate* props; normalize synonyms.
2. **Code-only props:** generate the hidden `Code only props` layer (child of root, (0,0), 0.01×0.01, clip-contents), bind code-only props inside it, hide them from the panel, emit as spec metadata.
3. **Examples:** harvest from a section named `Examples`; emit `instanceExamples` + `slotContentExamples` with intent-bearing placeholders — kept distinct from the variant grid.

## 9. Relationships
- **Up:** framework [[09-component-and-pattern-framework]] §5 (facets), §8 (state laws).
- **Across:** `tokens-and-naming.md` (the token refs used in `default`/`variants`); `ai-ready-design-systems.md` (emitting the record as `*.meta.json` for the MCP/agents).
- **Code binding:** the `surface: code-only` props + the import symbol are what Code Connect carries so agents *import* rather than re-implement.
