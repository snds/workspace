# Component Patterns Reference

> **Status:** Stub — expand with patterns from Centric PLM audits and
> cross-framework component work.

## Contents

### Component Anatomy Template

For each component, document:

```
[Component Name]
├── Structure (layers, nesting, auto layout direction)
├── Properties (boolean, text, instance swap, slot — with defaults)
├── Variants (axes and values)
├── States (default, hover, active, focus, disabled, error, loading)
├── Token bindings (which variables control which visual properties)
├── Accessibility (ARIA role, keyboard behavior, focus order)
├── Responsive behavior (min/max width, truncation, wrapping)
└── Code mapping (React prop names, CSS class structure)
```

### State Contract

Every interactive component must define its state contract:

| State | Visual change | Trigger | ARIA |
|---|---|---|---|
| Default | Base appearance | — | — |
| Hover | Subtle background shift | Mouse enter | — |
| Active/Pressed | Darkened, slightly scaled | Mouse down | aria-pressed (if toggle) |
| Focus | Focus ring (2px, offset 2px, action color) | Tab / programmatic | — |
| Disabled | Reduced opacity (0.4), no pointer events | disabled prop | aria-disabled="true" |
| Error | Error border color, error text | Validation failure | aria-invalid="true" |
| Loading | Skeleton or spinner replacement | Async operation | aria-busy="true" |

### Variant Matrix Planning

Before building, enumerate the full matrix:

```
[Component] variant matrix:
  [Axis 1]: Value A | Value B | Value C
  [Axis 2]: Value X | Value Y
  ...
  Total: [product of all axes]
  Reduction strategy: [which axes become properties instead]
```

### Cross-Framework API Alignment

When a component exists in multiple frameworks (Vue, React, React Native,
Angular), align the public API:

- Same prop names across frameworks where possible.
- Same variant values (size names, emphasis levels).
- Same slot/children composition model.
- Framework-specific patterns (v-model in Vue, controlled/uncontrolled in
  React) are acceptable divergences — document them.

### Accessibility Patterns

Reference: WAI-ARIA Authoring Practices Guide (APG)
https://www.w3.org/WAI/ARIA/apg/

Common component patterns with keyboard expectations:
- Button: Enter/Space activates
- Checkbox: Space toggles
- Radio group: Arrow keys navigate, Space selects
- Tabs: Arrow keys navigate, Enter/Space activates
- Menu: Arrow keys navigate, Enter activates, Escape closes
- Dialog/Modal: Tab traps focus, Escape closes
- Combobox: Arrow keys navigate list, Enter selects, Escape closes
- Data table: Arrow keys navigate cells (when keyboard nav is enabled)

### Composition Patterns

**Compound component:** Parent provides context, children consume it.
```
<Select>
  <SelectTrigger />
  <SelectContent>
    <SelectItem value="a">Option A</SelectItem>
    <SelectItem value="b">Option B</SelectItem>
  </SelectContent>
</Select>
```
Figma equivalent: Parent component with slots for trigger and content.

**Render prop / slot pattern:** Parent defines structure, consumer provides
content via function or named slot.
```
<DataTable
  columns={columns}
  data={data}
  renderCell={(cell) => <CustomCell {...cell} />}
/>
```
Figma equivalent: Slot with preferred instances.
