---
tags: [figma-plugin, engineering, design-tools]
created: 2026-05-11
updated: 2026-05-11
status: stable
confidence: high
sources: [figma-repo-sync-plugin Bundles 5–7, session 2026-05-11]
related_skills: [figma-plugin-dev, figma-modes-for-variants]
related_projects: [04-claude-figma-plugin]
---

# Figma Plugin Patterns (Hard-Won)

Five durable patterns extracted from the figma-repo-sync-plugin work. Each one fixed
a class of bug that surfaced when generating real components against real designer
expectations — not theoretical issues.

## 1. `layoutSizingHorizontal/Vertical = "FILL"` beats `layoutAlign = "STRETCH"`

**Problem:** `layoutAlign = "STRETCH"` on a child instance doesn't reliably stretch
the instance horizontally when the instance's master has `primaryAxisSizingMode =
"AUTO"`. Symptom: a `.CardFooter` instance with `STRETCH` rendered at 96px (its
master's hug-content width) inside a 432px Card, not the expected 384px content-area
width.

**Why:** For nested auto-layout where the child's primary-axis aligns with the
parent's cross-axis, the instance reads sizing from its master. `layoutAlign` is
a parent-flow hint; the master's intrinsic sizing wins in this configuration.

**Fix:** Set BOTH `layoutAlign = "STRETCH"` (legacy compatibility) AND
`layoutSizingHorizontal/Vertical = "FILL"` (modern API). `FILL` reliably overrides
the master's primaryAxisSizingMode for the placement.

```ts
inst.layoutAlign = "STRETCH";
if (parent.layoutMode === "VERTICAL") {
  inst.layoutSizingHorizontal = "FILL";  // parent's cross-axis = horizontal
} else {
  inst.layoutSizingVertical = "FILL";    // parent's cross-axis = vertical
}
```

## 2. Three-tier upsert for any persistent artifact

**Problem:** Plugin re-runs created duplicate Variable Collections (`Button — Sizes
×3`, `Badge — Types ×3`) because the existing-collection lookup relied on a single
signal — owned-IDs plugin data on the Component — and that signal got lost when the
Component was recreated, hand-edited, or the IDs pointed to deleted collections.

**Fix:** Always look up persistent artifacts via THREE tiers in this priority order:

1. **Fast path — Plugin-data IDs on the owner.** Most reliable when intact. Works
   across renames.
2. **Recovery — Walk all candidate artifacts; match by their OWN plugin-data tags
   (e.g., "this collection was made for component X, axis Y").** Survives the
   owner losing its index.
3. **Last resort — Display-name pattern match.** Catches the case where plugin
   data was lost on both sides. Pair with a reverse mapper for any
   pretty-name → source-name transformation (we needed `axisFromPretty()` to
   reverse the `prettyAxisName()` mapping).

This pattern applies to any artifact relationship (Component ↔ Collection, Master
↔ Sub-component, Library ↔ Asset). Sean's rule: *"upsert in place, never
remove-and-recreate."*

## 3. Tailwind `/N` opacity parsing — color-class prefix is essential

**Problem:** Naive stripping of `/N` suffix corrupts non-color fractional classes
(`w-1/2`, `h-3/4`, `max-w-1/12`) that share the same slash syntax but mean
"width is 1/2 of parent," not "alpha is 50%."

**Fix:** Only treat `/N` as opacity on color-class prefixes. Tailwind's color
prefixes that pair with `/N`:

```
bg- text- border- ring- outline- fill- stroke-
decoration- divide- placeholder- accent- caret- shadow-
```

For everything else, the `/N` is part of the value (fractional width, custom-property
notation, etc.) and must stay intact.

## 4. Variable binding survives opacity — multiply at paint, not at variable

**Problem:** `bg-muted/50` needs to render at 50% opacity over the parent surface
while still cascading dark-mode swaps through the muted variable.

**Wrong fix:** Bake opacity into the variable's mode value as `{r,g,b,a:0.5}`. The
foundation variable then carries an opinionated alpha that can't be reused for
non-opacity contexts.

**Right fix:** Capture opacity at the parse layer (`fillOpacity` on the StylePatch).
At paint application time, bind the SOLID paint to the foundation variable normally,
then set the paint's `.opacity` property to the captured factor. The variable
binding remains pure; the alpha lives on the paint instance.

```ts
// Bind to foundation (preserves cascade)
const bound = figma.variables.setBoundVariableForPaint(paint, "color", fgVar);
// Apply captured opacity on top
node.fills = [{...bound, opacity: 0.5}];
```

## 5. `figma.createFrame()` seeds 100×100 — kickstart AUTO sizing to 1×1

**Problem:** New frames created via `createFrame()` start at 100×100. Setting
`primaryAxisSizingMode = "AUTO"` + `counterAxisSizingMode = "AUTO"` on the empty
frame does NOT shrink it. When children are then appended, Figma's auto-layout
engine reflows but the 100×100 seed sticks — auto-resize sometimes doesn't
recompute on first child append.

**Symptom:** Icon slot frames inside Button instances rendered at 100×100 instead
of hugging the 24×24 icon glyph.

**Fix:** Call `resizeWithoutConstraints(1, 1)` immediately after setting AUTO
sizing modes and BEFORE appending children. The 1×1 seed lets the appended
children's intrinsic dimensions drive the final size.

```ts
const frame = figma.createFrame();
frame.layoutMode = "HORIZONTAL";
frame.primaryAxisSizingMode = "AUTO";
frame.counterAxisSizingMode = "AUTO";
frame.resizeWithoutConstraints(1, 1);  // Kickstart before children land
frame.appendChild(iconInstance);       // Now AUTO grows correctly to icon size
```

---

## Related anti-patterns

- **Don't filter on `node.visible` for layout calculations.** Hidden children DO
  contribute to auto-layout sizing in some Figma versions; rely on `layoutMode`
  + `STRETCH` instead.
- **Don't assume Component name uniqueness across files.** Same component name
  can exist in multiple source paths (private subs especially). Always pair name
  with sourcePath when keying lookups.
- **Don't use `setProperties` for CVA variant axes.** `setProperties` only works
  for BOOLEAN, INSTANCE_SWAP, and TEXT component properties. CVA variants are
  Variable Collection MODES — use `setExplicitVariableModeForCollection` on the
  instance with the collection resolved via owned-IDs.
