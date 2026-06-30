---
tags: [figma-plugin, engineering, design-tools]
created: 2026-05-11
updated: 2026-05-13
status: stable
confidence: high
sources: [figma-repo-sync-plugin Bundles 5–11 + 10A.2 Phases 1–3b, sessions 2026-05-11..05-13]
related_skills: [figma-plugin-dev, figma-modes-for-variants]
related_projects: [04-claude-figma-plugin]
---

# Figma Plugin Patterns (Hard-Won)

Durable patterns extracted from the figma-repo-sync-plugin work. Each one fixed
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

## 6. Name unification must respect semantic purpose, not just textual similarity

**Problem:** Two pipelines in the figma-repo-sync-plugin were writing to similar-
named Variable Collections — `foundations.ts` to `Foundations / Colors` (Light/Dark
modes, semantic colors like `background`/`foreground`) and `variableSync.ts` Pass 1
to `Foundations/Color` (single `Value` mode, palette primitives like `cds-blue-500`).
The cosmetic-only name difference made it look like the duplication was a naming
inconsistency. Bundle 7 "fixed" it by unifying both to `Foundations / Colors`.

**What broke:** The two pipelines had different *mode-structure* expectations.
Whichever ran second added its mode to the existing collection — yielding a
3-mode collection (`Value` + `Light` + `Dark`) with `Value` mostly white
because that mode's variables were only populated by Pass 1 of variableSync,
and `Light/Dark` only by foundations.ts seeds. Designers saw an obviously
wrong column of FFFFFF in the panel.

**Lesson:** Before unifying any two artifacts that share a name prefix, check
whether they're the **same concept** or **different concepts that happen to
share a noun**. Use a quick checklist:

1. **Mode/dimension structure** — do both producers expect the same number and
   names of modes/columns/axes?
2. **Content kind** — palette primitives vs semantic aliases vs typography vs
   spacing are all "foundation" tokens but live at different abstraction layers
3. **Lifecycle** — does one producer create the artifact unconditionally
   (scaffolding) while the other writes only on demand (sync)? Mismatched
   lifecycles imply different conceptual roles
4. **Variable names inside** — if the variable names DON'T overlap between the
   two collections (e.g., `cds-blue-500` vs `background`), that's a strong
   signal they're different concepts that just share a category label

**Fix (Bundle 7.1):** Split back into two collections by semantic purpose —
`Foundations / Palette` (single mode, palette primitives, from variableSync
Pass 1) and `Foundations / Colors` (Light+Dark, semantic colors, from
foundations.ts seeds + variableSync Pass 3). Within each, the producers can
now safely merge because they agree on the structure. Migration sweep
detects the spurious-mode artifact and either drops the mode (when no data
loss) or warns for clear+regenerate.

This generalizes to any name-unification work: don't conflate **same noun**
with **same concept**.

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

## 6. Variant cascade — body-default for foreground only, transparent for the rest

**Problem:** When a CVA variant has no `bg-*` / `border-*` class, what should
its variable mode value be?

- Falling back to the DEFAULT variant's value: wrong for `outline` / `ghost` /
  `link` — they end up with the default's blue background.
- Falling back to a body-default token (`background` foundation): better, but
  still wrong — `ghost` should be transparent, not opaque white.
- Falling back to ALPHA-ZERO: correct. A variant with no `bg-*` class is
  CSS-semantically transparent.

**Rule:** For each color slot in a CVA variant:

```
1. variant's own class
2. base classes
3. ONLY for foreground slot → body-default ("foreground" foundation token)
4. otherwise → alpha-0 (transparent)
```

The foreground slot is special because CSS body-inheritance applies (text
inherits a body-level color). Background, border, ring, outline don't —
their CSS default IS transparent.

**Token-name sentinels for transparency:** `transparent` and `none` always
resolve to alpha-0 paints, regardless of cascade level. `border-transparent`
parses as token "transparent" — without a sentinel rule, it'd fall through
to a fallback color lookup and render as gray.

## 7. Repeated-ref dedup — pair-vs-loop heuristic

**Problem:** When the story fixture produces three `<TabsTrigger>` instances
in a row, the plugin's anatomy walker emits three subcomponent-refs. Placing
all three in the same slot makes Figma show three identical labels (instances
inherit master defaults, so per-trigger text doesn't transfer). Pre-fix the
dedup pass aggressively collapsed ANY repeated same-named refs.

**Naive dedup over-eagerness:** A `<DialogFooter>` legitimately containing
TWO `<Button>` refs (Cancel + Continue) gets collapsed to one button.

**Right heuristic:**

- **Run of 1-2 same-named refs:** keep all. This is deliberate composition.
- **Run of 3+ same-named refs:** collapse to the first only. This is
  loop-generated boilerplate (Tabs, Menubar items, etc.) where the variation
  is in the props/text, not the count.

The fix lets a Dialog show its Cancel + Continue, and a Tabs show its 3
triggers — instead of either being collapsed to a useless single instance.

## 8. Text Styles vs inline text properties — the asset-panel test

**Problem:** Setting `fontSize` / `lineHeight` directly on every TextNode
gives the right rendering but produces ZERO named styles in the asset panel.
Designers see "Body text 14px" rendered correctly but can't pick "Body/Default"
from a typography dropdown — there is no dropdown.

**Fix:** Generate Figma TextStyles (`figma.createTextStyle()`) for every
canonical typography role (Heading/H1–H6, Body/Default–Small–Large, Caption,
Label, Code). Apply via `textNode.textStyleId = style.id`. Designers get
both: correct rendering AND a discoverable typography library.

**Inference rule:** Combine source `text-{size}` + `font-{weight}` to pick
a named style. `text-base font-medium` → `Heading/H5`. `text-sm` (no weight)
→ `Body/Default`. Bind style fontSize to the matching `font-size-{token}`
variable so theme-scale changes cascade.

**Limitation:** Figma TextStyle accepts variable binding on `fontSize`,
`lineHeight`, `letterSpacing` — but NOT on `fontName`. Font family + weight
combo is set literally. Designers can manually swap fonts later if needed.

## 9. Fallback chains must not short-circuit on intermediate failures

**Problem:** A source-resolution function (story → shadcn-docs → category-fixture)
returned early on the FIRST stage's failure modes — both `404 on story file` and
`story parsed empty` — so Form / Sidebar / NativeDialog / Sheet hit the
"no story tree" branch in the downstream generator and emitted as empty
minimal shells. The fixture fallback would have rendered perfectly, but the
function never reached the fixture-fallback line.

**Wrong instinct:** "If the first lookup fails, return null so callers know
it's unresolved." This leaks the failure mode upward instead of trying the
next strategy.

**Right pattern:** A fallback chain is a single decision tree. Intermediate
failures populate a diagnostic field but the function MUST continue to the
next stage. Only return null when ALL stages exhausted.

```typescript
// WRONG — early return swallows the fallback chain
} catch (e) {
  return { tree: null, diag: `fetch failed: ${e}` };
}

// RIGHT — track the failure for diagnostics, continue the chain
} catch (e) {
  storyAccessDiag = `fetch failed: ${e}`;
  storyContent = "";  // empty parse → empty bestRender → fixture fallback runs
}
```

The original diagnostic survives by prefixing onto the chosen-source diag:
`"story fetch failed: ... 404; category fixture picked for Form (richness=67)"`.
Traceability preserved, behavior corrected.

**General lesson:** When designing a multi-stage resolution function,
**every stage must be able to fail silently for the next stage to run.**
The function's contract should be "return the best available" rather than
"return what the first non-null stage produces."

## 10. Single-component primitives need slot-default wiring from synthetic fixture children

**Problem:** Components like EmptyState are a SINGLE function component (no
sibling exports) whose source uses slot expressions: `<p>{title}</p>`,
`{description && <p>{description}</p>}`, `{action && <div>{action}</div>}`.
The category fixture, designed for compound components, synthesises children
named `EmptyStateTitle` / `EmptyStateDescription` / `EmptyStateAction` even
though those exports don't exist. The synthetic children passed through
`walkChildrenAnatomy` as unknown-component frame placeholders and never
reached the source's slot expressions — the master shipped with empty
slots.

**Right convention:** Map fixture children whose tagName matches
`${parentName}${Suffix}` to slot defaults keyed by lowercased suffix:

```
<EmptyState>                       Source has:
  <EmptyStateTitle>X</X>     →     <p>{title}</p>           slotDefaults.title = [X]
  <EmptyStateDescription>Y  →     <p>{description}</p>     slotDefaults.description = [Y]
  <EmptyStateAction>Z       →     <div>{action}</div>      slotDefaults.action = [Z]
</EmptyState>
```

The walker already realizes `slotDefaults[expression]` inside `kind: "slot"`
anatomy nodes for compound subcomponents — this pattern wires the same
mechanism into the single-component dispatch path. Generalizes to any
primitive whose source has prop-driven slot expressions and whose fixture
follows the compound-child naming convention.

## 11. Tailwind class-based layout inference is a leaky abstraction

**Problem:** `inferLayoutMode("inline-flex group-data-vertical/tabs:flex-col")`
returned VERTICAL — the regex matched `flex-col` in a conditional class that
only applies when the data attribute is set. TabsList rendered with VERTICAL
auto-layout, stacking its 3 triggers instead of placing them in a row.

**Three independent failure modes on the same axis:**

1. **Data-attribute and pseudo-state conditional classes** (`group-data-[…]:`,
   `hover:`, `dark:`, `data-[…]:`, `disabled:`, `aria-disabled:`) shouldn't
   contribute to default-state layout — they only apply under their
   condition. Filter them out before regex matching, but KEEP responsive
   prefixes (`sm:`/`md:`/`lg:`/`xl:`/`2xl:`) because desktop-targeted Figma
   should pick up the desktop override.

2. **HTML elements with implicit flow direction** — `<tr>` has horizontal
   cell layout regardless of CSS. No Tailwind class on a `<tr>` expresses
   this. Pass the source root tagName as a tag-hint and resolve to
   HORIZONTAL for known cases when no flex class wins.

3. **CVA call expressions in `cn()` can't be statically unwrapped.**
   `cn(tabsListVariants({variant}), className)` — the first arg is a call,
   not a string literal, so the extractor returns `""`. Even with the
   conditional-class filter, there's nothing to anchor HORIZONTAL on.
   Fallback: per-component-name override set for known cases (TabsList,
   AvatarGroup). A deeper fix would extend the extractor to recognize
   `cn(cvaName(...), …)` patterns and pull the cva base, but the override
   list is small and self-documenting.

**Resolution order:** class-derived flex direction → HTML tag hint →
component-name override → block-flow default (VERTICAL). Class always wins
so explicit `flex-col` on a `<tr>` still goes VERTICAL — defends against
future weirdness.

**General lesson:** Class-based inference works for the common case but
needs explicit escape hatches when the class is conditional, the class is
inferred indirectly (cva calls), or the underlying element semantics
override CSS.

## 12. Figma masters should show the canonical example, not the React default state

**Problem:** Source has `{description && <p>{description}</p>}` — React
semantics: hide unless `description` is truthy. The plugin emitted these as
hidden Figma frames with a BOOLEAN component property defaulting to FALSE.
Result: when the canonical example (fixture/story) populated the inner
slot with content, designers still saw an empty master because the
description frame stayed hidden.

**Right call:** Figma masters represent the canonical example, not the
"unset" runtime state. When the inner slot has a story-driven default,
the enclosing conditional should default to VISIBLE, AND the BOOLEAN
property should default to TRUE. Designers can still toggle the property
off if they want the bare state.

Implementation: walk the conditional's inner anatomy recursively, looking
for a slot whose expression has a non-empty `slotDefaults` entry. If found,
visible=true. Otherwise, current "hidden by default" semantics persist.

**General lesson:** A Figma component master is a sticker-sheet
representation of the COMPLETE composition, not a minimal scaffold. The
React semantic ("falsy → no render") and the Figma semantic ("show the
canonical example") diverge by default; the plugin needs to bridge them
explicitly when canonical content is available.

## 13. Master-assembly dedup vs slot-defaults dedup are different layers

**Problem:** Bundle 10B's "pairs stay, 3+ collapse" dedup heuristic ran at
the slot-defaults computation (TabsList's slot for its 3 TabsTriggers got
collapsed to 1) but NOT at the master-assembly layer (Tabs's 3 TabsContent
siblings landed as 3 stacked instances). The Tabs master ended up with the
opposite of the intended shape: 1 trigger inside TabsList + 3 stacked
TabsContent panels at the Tabs root.

**Two dimensions:**

| Layer | Problem | Fix |
|---|---|---|
| **Slot defaults** | `<TabsList>` populated with 3 TabsTriggers via slot-default → collapsed to 1 (loses identity) | Exempt "list container" subcomponents (TabsList, TableRow, SelectGroup, AvatarGroup, etc.) from dedup — the count IS the identity |
| **Master assembly** | `<Tabs>` direct children include 3 TabsContent siblings → all 3 instantiated, each showing the same content | Apply dedup at the assembly loop too; special-case `Tabs` so non-list categories aren't affected |

**General lesson:** When a heuristic exists at one layer, check whether
the same logic should apply at adjacent layers. Code paths that look
different mechanically (slot fill vs. parent assembly) often share the
same correctness invariants ("3+ same-name siblings is a loop-fixture
artifact" applies in both places).

## 14. Diagnostic logs unblock multi-mechanism debugging

**Problem:** An audit found 11 ❌ components. Initial assumption: one
mechanism. Reality: 4+ distinct mechanisms, each affecting a different
subset, indistinguishable from final visual output alone.

**Right move:** Ship a logging-only build BEFORE attempting fixes. Four
log lines per compound parent at fixed code-path checkpoints (source
resolution, minimal-shell entry, assembly entry, assembly summary) made
the failure modes name themselves in the dev console:

```
[Bundle 10A.2 diag] fetchStoryTree Form: story fetch failed: ...404
[Bundle 10A.2 diag] minimal-shell Form: no story tree
[Bundle 10A.2 diag] fetchStoryTree Tabs: story picked: ... (richness=75)
[Bundle 10A.2 diag] assembly Tabs: root=<Tabs> children=4
[Bundle 10A.2 diag] assembly-summary Tabs: assemblyChildren=4, placed=4
```

Comparing diags across components: Form/Sidebar/NativeDialog/Sheet all
hit `minimal-shell` for different stage-failure reasons (404 vs parse-
empty). Input/Textarea showed `fixture picked` but no assembly lines —
different code path entirely. The logs let the fix split into Phase 1
(fallback chain), Phase 2 (placeholder rendering), Phase 3 (other paths)
landing as discrete, verifiable shippable commits.

**General lesson:** When debugging a class of bug across N components,
the FIRST commit should be diagnostic logging, not a fix. The visual
output is the wrong abstraction for differentiating failure modes —
the code-path checkpoints are. Cost: ~30 lines of `console.warn`.
Benefit: reframes the work from "fix N things at once" to "fix the
right thing for each."

---

## Migrated Figma-API gotchas (from local memory, 2026-06-30)

### 15. Material Symbols icon instances enforce a min/max width — `resize()` reverts

Generated Material Symbols icon instances enforce a min/max width that locks them at their
native ~20px size. Calling `instance.resize(8,8)` **silently reverts** to 20px, and setting the
inner glyph's `fontSize` alone leaves the fixed 20px frame around an 8px glyph.

**To resize an MS icon instance** (e.g. to an 8px `size-2` badge glyph):
1. Clear the constraints: `for (const p of ["minWidth","maxWidth","minHeight","maxHeight"]) inst[p] = null;`
2. `inst.rescale(target / inst.width)` — `rescale()` scales the **frame and glyph together**
   (unlike `resize()`), so 8px target = `rescale(8/20)` = `rescale(0.4)`.
3. Recolor the glyph and recenter (`inst.x = (parent.width - inst.width)/2`).

Also: the MS icon glyph is itself a **TEXT node** (the ligature), so
`instance.findOne(n=>n.type==="TEXT")` returns the **glyph**, not a sibling label — use top-level
`instance.children.find(c=>c.type==="TEXT")` when you mean a label next to an icon.

### 16. SectionNode children use PARENT-RELATIVE coordinates (frame-like), not page-absolute

A Figma **SectionNode's children use coordinates relative to the section's own origin**, NOT
page-absolute — even though sections visually look like loose canvas containers. Matters when
nesting sections (grouping per-component sections into category supersets):

- Setting a nested child's `y` to an **absolute page value double-offsets it** (`category.y +
  child.y`). A child meant to sit at page-y 5355 inside a category at y5259 must have `child.y = 96`
  (relative), not `5355`.
- Symptom: the FIRST/top category (at y0) looks correct while every later one is pushed
  progressively further down — because only the y0 parent makes relative == absolute.
- Diagnose: compare `node.x/.y` (relative to parent) against `node.absoluteBoundingBox` (page
  coords). If they differ by the parent's offset, you're in relative-coord land.

### 17. The official `use_figma` MCP runs in a detached/headless session

The official Figma MCP `use_figma` executes in a **detached/headless Figma session**, NOT the
user's live desktop editor. Evidence (centric-ui file):
- `figma.currentUser` throws "not a supported API".
- `figma.currentPage` always resets to the file's FIRST page at the start of each call — it never
  reflects the page the user is viewing or their manual selection.
- `setCurrentPageAsync` + `currentPage.selection = [...]` + `scrollAndZoomIntoView` all succeed and
  read back correctly, but NONE of it appears in the user's editor.
- `listAvailableFontsAsync()` may return nothing for fonts the file uses (Material Symbols came back
  empty), so `loadFontAsync` for those can't be relied on.

**Consequence:** any task of the form "select these nodes in my editor so I can act on them" CANNOT
be done via `use_figma` — the selection lives in a session the user can't see. Deliver a tiny **dev
plugin the user imports** (Plugins → Development → Import plugin from manifest) instead; it runs in
their real session so selection/viewport stick. (A working example: `Projects/select-filled-icons/`
— manifest.json + code.js.) **Also:** the Plugin API has NO variable-font axis setter — only
`setRangeFontName`/`setRangeFontSize`/`setRangeFontWeight`. Material Symbols' FILL/wght/GRAD/opsz are
variable AXES → can't be set programmatically; the user must drag the axis in the Type panel.

Related: [[figma-cli-authoring]] · [[figma-ds-surface-authoring]] · [[figma-variable-state-representation]].
