---
name: figma-modes-for-variants
description: >
  Collapse combinatorial Figma component variants into a smaller variant matrix by
  routing color/style axes through Figma variable modes instead of component variant
  properties. Use this skill whenever generating Figma component sets from a CVA-like
  source (shadcn, class-variance-authority, tailwind-variants), when designing a new
  Figma component library, or when an existing component set has hundreds of variants
  driven by visual style. Trigger words: "modes for variants", "variable modes",
  "component-scoped collection", "collapse variants", "variant explosion", "mode-driven
  component", "shadcn variant in Figma".
aliases: [figma-modes-for-variants]
spec_version: "2.0"
---

# Modes for Variants — Collapsing Component Sets via Variable Modes

## When to use this skill

When you have a multi-axis component (e.g. shadcn Button with `variant` × `size`) and
some of those axes are **purely visual style** (background, foreground, border colors).
Modeling every such axis as a Figma component variant produces an N × M matrix that
grows multiplicatively. The same outcome is reachable with a smaller matrix and fewer
artifacts to maintain.

This skill operates above [figma-variable-creation](../figma-variable-creation/SKILL.md)
(primitives for collections + modes + variables) and
[figma-style-binding](../figma-style-binding/SKILL.md) (the immutability + binding
mechanics for paints). Read those for the call-level details; this skill covers the
*decision* of when and how to apply them.

---

## The pattern in one sentence

**Each CVA axis → its own component-scoped variable collection with one mode per
value. The component is a single Figma component (no variant property) bound
across all collections. One component per Figma file.**

> **Architectural update 2026-05-07**: this skill originally described a hybrid
> in which color-driven axes became modes and structure-driven axes stayed as
> Figma component variants. The current canonical pattern is uniformly
> mode-driven: every axis becomes its own collection. Color axes hold COLOR
> variables; structure axes hold FLOAT variables (height, padding, gap, radius,
> font size). The hybrid description is preserved below for historical context
> and for cases where a structure axis genuinely cannot be expressed as variable
> values (e.g., axes that toggle between fundamentally different shapes).

---

## Why this matters

A shadcn Button with 10 `variant` values × 8 `size` values produces 80 component
variants if you naively mirror the CVA matrix into Figma. That's:

- **80 components to render**, every time you regenerate.
- **80 places** to fix a single token reference if it changes.
- **80 thumbnails** in the Assets panel.
- A **slow** instance picker.

The 10 `variant` values are pure color permutations of the same shape — `bg-primary`
becomes `bg-secondary` becomes `bg-destructive`. The shape itself doesn't change.
Figma's variable modes are designed for exactly this: same node, different resolved
values, switched at the instance via Appearance → Apply variable mode.

After applying this skill: **8 component variants + 1 collection with 10 modes**.
10× fewer components, identical end-user expressiveness.

---

## Axis classification — when to use which

For each variant axis, count the kinds of classes its values produce. The decision
follows from where the visual change lands:

| Axis class composition | Conclusion | Treatment in Figma |
|---|---|---|
| Mostly color (`bg-*`, `text-{token}`, `border-*`, `ring-*`, `outline-*`) | Style axis | Variable mode on component-scoped collection |
| Mostly geometry (`h-*`, `w-*`, `size-*`, `p*-*`, `gap-*`, `rounded-*`, `text-{size}`) | Structure axis | Figma component variant property |
| Mixed | See below | Default to component variant; surface the mixed signal |

**Heuristic threshold**: if ≥ 70% of the unique non-base classes across an axis's
values are color-bindable, treat it as a style axis. Below that, keep it as a
component variant. The 70% line is conservative — false positives on style-axis
detection produce unbindable variables; false negatives just keep the matrix larger.

**Mixed axes** (e.g. shadcn's `link` variant adds `underline-offset-4 hover:underline`
on top of color classes): keep them as a component variant in v1. Modes only express
variable values, not structural overrides like text decoration. A future iteration
could detect and warn on the mixed signal explicitly.

---

## Architecture (canonical, multi-collection)

Each CVA axis becomes its own collection, named after the axis category in
plural (`Types`, `Sizes`, `Intents`, …). The component name is **not** in the
collection name — under the file-per-component convention (one component per
Figma file), it would be redundant. The component is **a single Figma component**,
no variant property — every visual difference is mode-driven across one or more
collections.

```
File: button.fig    (one component per file)
└── Page "Component"
    └── Component "Button"
        ├── owns (via plugin data) → VariableCollection "Types"
        │                              ├── modes: default, outline, secondary,
        │                              │          ghost, destructive, link,
        │                              │          danger, info, success, warning
        │                              └── variables (COLOR):
        │                                  ├── background  (10 mode values)
        │                                  ├── foreground  (10 mode values)
        │                                  └── border      (10 mode values)
        │
        ├── owns (via plugin data) → VariableCollection "Sizes"
        │                              ├── modes: default, xs, sm, lg, icon,
        │                              │          icon-xs, icon-sm, icon-lg
        │                              └── variables (FLOAT):
        │                                  ├── height        (8 mode values)
        │                                  ├── paddingX      (8 mode values)
        │                                  ├── paddingY      (8 mode values)
        │                                  ├── itemSpacing   (8 mode values)
        │                                  ├── cornerRadius  (8 mode values)
        │                                  └── fontSize      (8 mode values)
        │
        └── bindings:
            • fills              ← Types: background
            • strokes            ← Types: border
            • text fills         ← Types: foreground
            • height             ← Sizes: height
            • paddingLeft/Right  ← Sizes: paddingX
            • paddingTop/Bottom  ← Sizes: paddingY
            • itemSpacing        ← Sizes: itemSpacing
            • all 4 corners      ← Sizes: cornerRadius
            • text fontSize      ← Sizes: fontSize
```

**End-user workflow**: place a `Button` instance. **Appearance → Apply variable
mode → Types** to switch the visual style; **Appearance → Apply variable
mode → Sizes** to switch the size. The two collections compose
independently.

### Pretty-name table

CVA axis names are programmer-friendly; collections want design-system-friendly
names. A small alias table covers the common cases (pluralized — each collection
holds the *category* of values); everything else falls through to capitalize.

| CVA axis name | Collection name |
|---|---|
| `variant`  | `Types`     |
| `size`     | `Sizes`     |
| `intent`   | `Intents`   |
| `tone`     | `Tones`     |
| `state`    | `States`    |
| (other)    | Capitalize  |

### Mode ordering: physical scale, not declaration order

CVA value names are preserved verbatim — `default`, `xs`, `sm`, `lg`, `icon`,
etc. flow through unchanged. But the order in which modes appear in Figma's
mode list is **sorted by physical scale**, not by CVA declaration order.

Why: shadcn's convention universally uses `default` to mean "the standard
size" — and that size is medium across every shadcn-ui component. Listing the
modes in declaration order ([default, xs, sm, lg, …]) hides that semantic.
Sorting by extracted height ([xs, sm, default, lg]) puts each mode where it
belongs in the scale, so the user can see at a glance that `default` sits
between `sm` and `lg`.

The sort signal is the `height` slot extracted by structureSlots. Tiebreaker
is declaration order. Axes without any height signal (e.g., a color-only
variant axis) keep declaration order entirely.

Worked example for shadcn Button's size axis:

| CVA declaration order | Sorted by physical scale |
|---|---|
| default, xs, sm, lg, icon, icon-xs, icon-sm, icon-lg | xs, icon-xs, sm, icon-sm, default, icon, lg, icon-lg |

The component is still pinned to `default` via `setExplicitVariableModeForCollection`,
so instances inherit that explicitly. Mode position in the list only affects
the dropdown display order; the auto-fallback never fires for our generated
component.

### File-per-component convention

Each component lives in its own Figma file. Reasons:

- Variable collections are file-local — keeping `Types` and
  `Card - Type` in separate files prevents cross-component name collisions.
- Library publishing is component-by-component. Consumers import the Button
  library and bring its collections in scope without inheriting `Card - Size`.
- File-level dependency graph is clean: each component file depends on a shared
  primitives library (when token-side lands) but not on sibling components.

The plugin places the generated component on a dedicated `Component` page
(created if missing) so the file's other pages stay free for documentation,
specs, exemplar usage, etc.

---

## Plugin API call sequence (multi-collection)

For each CVA axis, run the sequence below. The component is created once and
bound across all the resulting collections.

The exact API surface (verified against `@figma/plugin-typings`):

### 1. Create the component-scoped collection

```ts
const collection = figma.variables.createVariableCollection(componentName);
// Collections always start with one default mode named "Mode 1".
collection.renameMode(collection.modes[0].modeId, styleAxisValueNames[0]);

const modeIdByValue: Record<string, string> = {
  [styleAxisValueNames[0]]: collection.modes[0].modeId,
};
for (const value of styleAxisValueNames.slice(1)) {
  // addMode throws if the file's pricing tier is exceeded — see "Plan limits" below.
  modeIdByValue[value] = collection.addMode(value);
}
```

### 2. Create one COLOR variable per slot

```ts
type Slot = "background" | "foreground" | "border" | "ring" | "outline";

const variableBySlot: Record<Slot, Variable> = {} as any;
for (const slot of slotsUsedAcrossAllValues) {
  variableBySlot[slot] = figma.variables.createVariable(slot, collection, "COLOR");
}
```

### 3. Set per-mode values

```ts
for (const value of styleAxisValueNames) {
  const slotsForValue = parseSlotsFromClasses(classesByValue[value]);
  for (const slot of Object.keys(slotsForValue)) {
    const rgb = resolveTokenToRgb(slotsForValue[slot]);  // your token lookup
    variableBySlot[slot].setValueForMode(modeIdByValue[value], rgb);
  }
}
```

### 4. Bind variables on the (single) generated component

For COLOR variables (Paint-bound):

```ts
const boundPaint = figma.variables.setBoundVariableForPaint(
  { type: "SOLID", color: { r: 0, g: 0, b: 0 } }, // base color is overridden
  "color",
  variableBySlot.background,
);
component.fills = [boundPaint];

// Text node fills work the same way:
const boundTextPaint = figma.variables.setBoundVariableForPaint(
  { type: "SOLID", color: { r: 0, g: 0, b: 0 } },
  "color",
  variableBySlot.foreground,
);
textNode.fills = [boundTextPaint];
```

For FLOAT variables (geometry), use `setBoundVariable` directly on the field:

```ts
component.setBoundVariable("height", floatVarBySlot.height);
component.setBoundVariable("paddingLeft", floatVarBySlot.paddingX);
component.setBoundVariable("paddingRight", floatVarBySlot.paddingX);
component.setBoundVariable("paddingTop", floatVarBySlot.paddingY);
component.setBoundVariable("paddingBottom", floatVarBySlot.paddingY);
component.setBoundVariable("itemSpacing", floatVarBySlot.itemSpacing);
component.setBoundVariable("topLeftRadius", floatVarBySlot.cornerRadius);
component.setBoundVariable("topRightRadius", floatVarBySlot.cornerRadius);
component.setBoundVariable("bottomLeftRadius", floatVarBySlot.cornerRadius);
component.setBoundVariable("bottomRightRadius", floatVarBySlot.cornerRadius);
textNode.setBoundVariable("fontSize", floatVarBySlot.fontSize);
```

**Crucial**: `setBoundVariableForPaint` returns a NEW Paint. The original is not
mutated (paints/fills are `ReadonlyArray` — see [figma-style-binding](../figma-style-binding/SKILL.md)).

**Width is intentionally not bound in v1**. We keep `primaryAxisSizingMode = AUTO`
so width hugs content. Per-mode width overrides require toggling the sizing mode,
which Figma can't express via variable modes. For axes that include
fundamentally different shapes (e.g. icon-only vs text-with-icon variants), this
is a known v1 limitation — accept the imperfection or split into separate
components.

### 5. Pin each collection's default mode on the component

```ts
for (const ac of axisCollections) {
  const defaultModeId = ac.modeIdByValue[ac.defaultValueName];
  component.setExplicitVariableModeForCollection(ac.collection, defaultModeId);
}
```

This sets the component's preview to the default value for every axis. Instances
inherit Auto mode (the collection's first mode) until the user explicitly switches.

### 6. Persist ownership for idempotent re-runs

```ts
component.setPluginData("centric-source-path", sourcePath);
component.setPluginData(
  "centric-owned-collection-ids",
  JSON.stringify(axisCollections.map((ac) => ac.collection.id)),
);
```

On regeneration, look up the component by source-path plugin data, parse the
owned-collection-ids array, delete each prior collection by ID, then delete the
prior component. Skipping this step accumulates orphaned collections on every run.

---

## Plan limits — fail gracefully

`collection.addMode()` throws if the file's pricing tier is exceeded:

| Plan        | Modes per collection |
|-------------|----------------------|
| Starter     | 1 (no extra modes)   |
| Professional| 4                    |
| Organization| 4                    |
| Enterprise  | 40                   |

When `addMode` throws:

1. **Check before**: `if (collection.modes.length >= maxAllowed)` — but the limit
   isn't programmatically queryable. Use a try/catch and surface a clear error.
2. **Fall back gracefully**: catch the throw, log how many modes succeeded, and
   convert the remaining style-axis values to ordinary component variants for that
   run. Surface the partial degradation in the result payload so the user knows.

```ts
const succeededValues: string[] = [styleAxisValueNames[0]];
for (const value of styleAxisValueNames.slice(1)) {
  try {
    modeIdByValue[value] = collection.addMode(value);
    succeededValues.push(value);
  } catch {
    break; // remaining values fall back to component variants
  }
}
const fallbackValues = styleAxisValueNames.filter((v) => !succeededValues.includes(v));
```

---

## What modes can't do (for v1 of this pattern)

- **State-based color overrides** (`hover:bg-muted`, `active:translate-y-px`,
  `focus-visible:ring-3`) don't translate. Figma component states are a separate
  concept; modes only resolve a single value per (variable × mode). v1: strip state
  prefixes before extracting slots; surface them as `unhandledStateClasses` for
  visibility, defer real handling to a later iteration.
- **Compound variants in CVA** (`{ variant: "primary", size: "lg", class: "shadow-lg" }`)
  cross axis boundaries. If the style axis becomes a mode, the compound's `class`
  payload can't reference the structure axis cell selectively. v1: apply compound
  classes to all variants when their style-axis predicate matches; flag if a compound
  predicates on a structure axis.
- **Non-color style axis classes** (the `link` example with `underline-offset-4`)
  can't be expressed as variables. v1: keep mixed axes as component variants.

---

## Cross-references

- [figma-variable-creation](../figma-variable-creation/SKILL.md) — primitives:
  `createVariableCollection`, `addMode`, `createVariable`, `setValueForMode`, plan
  limits table.
- [figma-style-binding](../figma-style-binding/SKILL.md) — immutability rules for
  fills/strokes/effects, `setBoundVariableForPaint` mechanics, common errors.
- [figma-component-generation](../figma-component-generation/SKILL.md) — variant
  property naming format (`Property=Value, Property=Value`), `combineAsVariants`,
  auto-layout configuration.
- [figma-plugin-dev](../figma-plugin-dev/SKILL.md) — general plugin practices,
  async page loading, error recovery.

---

## Field log

Add a dated entry whenever this pattern is applied to a real codebase. Keep entries
short — facts, not narrative.

### 2026-05-07 — `centric-ui` Button (figma-repo-sync-plugin)

- **CVA shape**: `variant` (10 values) × `size` (8 values).
- **Classification**: `variant` → STYLE_AXIS (~100% color classes), `size` →
  STRUCTURE_AXIS (geometry only).
- **Iteration 1 (single-collection, hybrid)**: 8 size-variant components +
  1 `Button` collection with 10 type modes. Worked but didn't satisfy the
  "modes should drive size too" intent.
- **Iteration 2 (multi-collection, canonical)**: single `Button` component +
  2 collections — `Types` (10 modes, COLOR vars: background, foreground,
  border) and `Sizes` (8 modes, FLOAT vars: height, paddingX, paddingY,
  itemSpacing, cornerRadius, fontSize). No Figma component variants. Component
  placed on a dedicated `Component` page; one component per file.
- **Plan**: cpes-software is on Enterprise; full mode counts succeeded.
- **Known v1 limitations on this component**:
  - `link` type adds `underline-offset-4 hover:underline` — the `underline`
    can't be expressed as a variable; deferred.
  - icon-* sizes (`icon`, `icon-xs`, `icon-sm`, `icon-lg`) want both width AND
    height fixed; v1 only binds height. Width stays AUTO so icon variants
    render with whatever inner-content width emerges. Acceptable visual
    imperfection until v1.1 introduces conditional sizing.
  - State-prefixed classes (`hover:bg-*`, `aria-expanded:*`, `dark:*`) stripped
    and recorded under `unhandledStateClasses`.
