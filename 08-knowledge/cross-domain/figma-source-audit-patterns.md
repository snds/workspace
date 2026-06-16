---
tags: [figma, shadcn, react, design-engineer, audit, components, variants]
created: 2026-05-08
updated: 2026-05-08
status: working
confidence: medium
sources: [09-figma-repo-sync-plugin sessions, full-file Figma audit 2026-05-08]
related_skills: [figma-source-audit, figma-modes-for-variants, design-engineer]
related_projects: [09-figma-repo-sync-plugin, centric-ui]
---

# Figma source-audit patterns

What we've learned reviewing a fully-generated centric-ui Figma library against shadcn source + canonical visual expectations. These are recurring observations across ~24 generated components — not Select-specific. The companion skill [`figma-source-audit`](../../03-skills/figma-source-audit/SKILL.md) packages the *methodology*; this entry holds the substance.

---

## Source-shape taxonomy (every shadcn component fits one of five)

When auditing a generated component, the first question is "which shape does the source take?" Five shapes recur across centric-ui and shadcn at large; each has different generation considerations.

| Shape | Recognise it by | Typical examples | What it should produce in Figma |
|---|---|---|---|
| **Pure alias** | `const X = Primitive.Y;` — no arrow body | `Dialog`, `Sheet`, `Sidebar`, `Tooltip` (the root re-exports) | No Component on its own. The compound parent assembly *is* the public face. |
| **Passthrough wrapper** | Arrow body, returns a primitive with no `cn()` | `Collapsible`, `CollapsibleTrigger`, `CollapsibleContent` | An empty styled frame; designers fill it via slot defaults / story content. |
| **Styled wrapper (single)** | Arrow body, has `cn()`, lives alone in its file | `Checkbox`, `Switch`, `Label`, `Skeleton`, `Separator`, `Input`, `Textarea`, `Badge` | One public Component with anatomy from the body + props as Figma component properties. |
| **CVA component** | Calls `cva(...)` for variant classes | `Button`, sometimes `Badge` | One public Component with variant axes as **modes** in component-scoped collections (per `figma-modes-for-variants`). |
| **Compound** | ≥ 2 PascalCase declarations with arrow bodies | `Select`, `Card`, `Dialog`, `Tabs`, `Popover`, `Sheet`, `Sidebar`, `Form`, `Table`, `AlertDialog`, `Avatar`, `Tooltip` | Multiple Components in a section: a public parent (assembled from the canonical story) + private `.Sub` wrappers + private `.Aux` for `*Indicator`-style patterns. |

Most "weirdness" we encounter in audits stems from misclassifying the shape. The new compound rule (≥ 2 components with arrow bodies, regardless of `cn()`) catches the passthrough-compound case (Collapsible). The body-presence test catches the alias filter (Dialog's root re-export is excluded so we don't generate `.Dialog` accidentally).

---

## The state-coverage taxonomy

Every interactive component has a *state surface* — the union of conditions that change its appearance. The audit should map each component to which states it needs and how each is best modeled.

| State family | Includes | Best Figma model | Notes |
|---|---|---|---|
| **Style axes** (color/density theme) | `Default`, `Hover`, `Focus`, `Active`, `Disabled`, `Error`, `Loading`, `Selected` | Either VARIANTS on a ComponentSet **or** modes on a `Component States` collection | When 2+ style axes combine multiplicatively (Type × State × Size), prefer `figma-modes-for-variants` to avoid variant explosion. |
| **Structural axes** | Density (compact/comfortable), Orientation (horizontal/vertical), `loading` swapping label for spinner | VARIANT on a ComponentSet | Modes can't change *structure*, only token values. |
| **Open / closed** | Popover, Dialog, Sheet, Sidebar collapsed/expanded | Either separate Components (`Select` vs `SelectMenu`) or a structural variant | Default to "closed" representation; surface "open" as a sibling Component or variant. |
| **Conditional content** (`{X && JSX}`) | `description?`, `action?`, optional icons | BOOLEAN component property bound to layer visibility | Designers toggle to show/hide. Pair with the property that drives the content (`description: TEXT` + `hasDescription: BOOLEAN`). |
| **Slot content** (`{children}`) | Trigger label, popover items, button label | Native `SlotNode` + `'SLOT'` component property | Pre-populate from canonical story for realistic empty-state. |
| **Indicator content** (`*Indicator` patterns) | Selected check, radio dot, valid/invalid icon | Promoted aux Component (`.SelectItemIndicator`) with hidden-by-default instance in parent | Designers toggle the instance's `visible` to inspect the active state. |

A component that touches more than one state family (most do) needs to choose one family as the *primary* axis and treat the others as nested concerns. Button is the canonical example: Type and Size are style axes (modes), Disabled is conditional (BOOLEAN), Loading is structural (variant or icon-swap), and the children slot covers the label. Trying to put all of them as VARIANTS produces 60+ cells.

---

## Recurring gaps observed in the 2026-05-08 audit

Across the 24 generated sections, the same gaps appear repeatedly. Listing them is more useful than enumerating per-component:

### Sizing

- **Default 100×100 placeholders.** Passthrough wrappers without `cn()` and without rich body content stay at Figma's default new-component size of 100×100. Auto-layout AUTO sizing should hug to ~0/content, but the resize never gets re-evaluated when no class-derived dimension is set. The generator currently calls `applyFrameStyling` *before* children are added; layout doesn't re-compute on appendChild for empty containers. Fix: explicitly call `node.resizeWithoutConstraints(1, 1)` after content is added, OR skip the styled frame entirely for content-less wrappers and let auto-layout absorb the contents.
- **Components hugging to icon-only width.** SelectTrigger / SelectItem before the slot-grow fix. Resolved earlier — see `figma-component-composition-from-react.md` for the fix.

### Variant coverage

- **CVA components show only their default state.** Button shows one Type/Size cell — designers can't see Primary vs Secondary vs Outline at a glance. Expected behavior of `figma-modes-for-variants`, but the *canvas* has no spec/preview frame demonstrating the modes. **Recommendation**: each CVA component's section should include a small "spec grid" frame that instances the component once per (Type × Size) cell so the visual range is browseable on the canvas. This is independent of the published Component — it's documentation.
- **No state variants anywhere.** Hover, Focus, Active, Disabled, Error, Loading — none of these exist on Button, Input, Switch, Checkbox, etc. Designers can't show "this Input is in error state" without manually overriding fills. **Recommendation**: introduce a per-component `Component States` collection with modes (`Default`, `Hover`, `Focus`, `Active`, `Disabled`, `Error`); bind interactive elements' fills/strokes to it. This is a Phase-4 feature (variants chunk).

### Composition

- **Passthrough compounds (Collapsible) lack visible content.** With no `cn()` and no story content matched to children slots, the components render as 100×100 grey boxes. **Recommendation**: pull `args:` from stories (currently we only read `render: () =>`) so single-prop components like `<Collapsible defaultOpen>` get default content from `args: { children: ... }` when available.
- **Story-multiple usages get duplicated.** Tabs's three "Overview" pills suggest the walker is including all `<TabsTrigger>` elements from the canonical story rather than picking one for each kind of slot. **Recommendation**: when building slot defaults, if the same sub-component appears N times in the story, aggregate into a *list-style* default (one instance + a "this slot accepts N items" hint) rather than placing N parallel instances.
- **Some compound parents lack public Component.** When the source's parent is itself a real arrow-body component (`const Dialog = ({ ...props }) => <DialogPrimitive.Root … />`), it gets generated as a sub (private `.Dialog`), and the parent assembly may collide. **Recommendation**: detect when `subComponents` includes a name matching `parentName` AND that component is content-less; treat it specially as the "parent skeleton" and use its body classes for the assembled parent rather than generating both.

### Properties

- **Conditional rendering not modeled.** EmptyState's `{description && <p>…</p>}` becomes a slot named after the whole expression. Same pattern visible across Input, Textarea, the `*Content` and `*Footer` of Dialog/Sheet — Input's properties include literal names like `errorSpanClassNameTextXsTextCdsRed500ErrorSpan4` (the entire `{description && <span className="text-xs text-cds-red-500">…</span>}` mashed into an identifier). Should become a TEXT property + BOOLEAN visibility on the description frame. **Recommendation**: walker enhancement to detect `{ident && jsx}` and emit `BOOLEAN` + visible-toggle. Phase-4 work.
- **`addComponentProperty` duplicates on every re-run.** `Figma.ComponentNode.addComponentProperty(name, kind, default)` does NOT throw on duplicate name — it silently appends a numeric suffix (`children`, `children2`, `children3`, …). Wrapping the call in `try/catch` therefore never catches; the registry grows on every generation. Audit toolkit Snippet B (component property definitions dump) makes this immediately visible:
  > `.CheckboxIndicator` had 6 SLOT properties named `children`/`children2`/`children3`/…; `.DialogContent`, `.SheetContent`, `.DialogFooter` each had 12 (4 BOOLEAN + 8 SLOT); `.Input` had 12 SLOTs with garbage conditional-rendering names; the four Select sub-components each had 10 SLOTs.
  **Required fix in `applySlotNode` and the BOOLEAN/TEXT prop loop in `generateStaticSubComponent`**: before calling `addComponentProperty`, check `node.componentPropertyDefinitions[propName]` (or any name beginning with `propName#`). Skip if present. Plus a one-time cleanup pass on existing components.
- **`children` slot duplication.** Sub-components and their compound parent both get `children` SLOT properties. When designers instance the parent and override `children`, the sub's `children` also seems to take over. Investigate whether nested SLOT properties create the right designer experience.

### Variables

The richest audit findings here came from `get_design_context` (which exposes
bindings as CSS-var references) and `use_figma` (which shows whether
variables are *aliased* to foundation variables or hold literal values).

- **CVA components ARE variable-bound** — `get_design_context` on Button shows
  `bg-[var(--background,#233e87)]`, `border-[var(--border,#d9d9e0)]`,
  `h-[var(--height,32px)]`, `text-[color:var(--foreground,white)]`, etc. The
  modes-as-variants pattern is functional. Variables are component-scoped
  (`Button — Types`, `Button — Sizes`) and shift correctly per mode.
- **Non-CVA styled wrappers have NO variable bindings.** `get_design_context`
  on Checkbox returns `border-[#d9d9e0]` — a literal color, not a `var(...)`
  reference. Same for Switch, Input, Label, etc. The single-styled-component
  dispatch path (and the static-sub path for compound members) bypasses
  variable creation entirely.
- **Component-scoped variables don't alias foundation variables.** Snippet E
  in the audit skill confirms: `Button — Types/background[default]` is a
  literal color (`#233e87`), not a `VARIABLE_ALIAS` to
  `Foundations / Colors/primary`. The foundation collections sit populated
  but unused. Editing `Foundations / Colors/primary` in dark mode would not
  cascade to Button.
- **Foundation values diverge from styleStub palette values.**
  `Foundations / Colors/primary` (Light) is `#171717` (near-black), but
  `Button — Types/background[default]` is `#233e87` (a centric blue). The
  same conceptual token has two different values living in two places.
  Wiring bindings without aligning values would change Button's appearance
  unexpectedly. **Recommendation**: in the wiring pass, treat the foundation
  values as authoritative; the component-scoped variables become aliases
  whose stored value is the alias, not a colour. Drop the styleStub
  fallback palette once foundation wiring is reliable.
- **`Component States` collections don't exist yet.** No per-component state
  collection has been generated; the variants chunk needs to create them and
  bind interactive elements.

### Indicators / hidden defaults

- **Working as intended.** Hidden indicators / scroll buttons render correctly per `figma-component-composition-from-react.md`. Designers can flip `visible` to inspect.

---

## Per-component recommendations (selected highlights)

Not exhaustive — these illustrate the application of the framework. The full per-component table belongs in a project artifact, not a knowledge entry.

| Component | Source shape | Current generated state | Highest-value next move |
|---|---|---|---|
| `Button` | CVA | Single-cell, default Primary/Default | Add spec frame showing all Type × Size cells. Add `Component States` collection (Default/Hover/Focus/Disabled). |
| `Checkbox` | Styled wrapper (single) + `*Indicator` aux | Empty 16×16 border + hidden CheckIndicator | Fill fix when active state is visible. State variants for Checked / Unchecked / Indeterminate / Disabled. |
| `Input` | Styled wrapper (single) | 124×156 placeholder | Real Input chrome (border, padding, placeholder text). State variants for all interactive states + Error. |
| `Switch` | Styled wrapper (single) | 100×100 placeholder | Track + thumb anatomy. State variants for Off / On / Disabled-Off / Disabled-On. |
| `Select` | Compound | Functioning, well-documented in companion entry | Add open-state representation as sibling Component or variant. |
| `Collapsible` | Passthrough compound | Empty placeholder boxes | Pull `args:` defaults from stories. State variant for Collapsed / Expanded. |
| `Dialog` / `Sheet` | Compound with alias parent | Subs generated, parent assembly partial | Resolve alias-parent collision; ensure public Dialog/Sheet with correct closed/open representation. |
| `Tabs` | Compound | Story-multiple duplicates | Collapse repeated TabsTrigger instances; pick one Tab as the canonical instance. |
| `Card` | Compound | Subs generated | Story-driven default content (Title + Description + Content + Footer should be visible). |
| `EmptyState` | Bespoke | (Pending generation fix per recent work) | TEXT props + BOOLEAN conditional visibility once dispatch path lands. |

---

## Recurring "skill-level" patterns to remember

These are the patterns the audit confirms, useful as durable advice:

1. **The shape determines the strategy.** Every audit starts by asking which of the five source shapes applies. Don't generalize across shapes.
2. **State coverage is a separate axis from anatomy.** Generation produces anatomy. State variants are a follow-on. Don't conflate "we generated SelectTrigger" with "we covered Hover/Focus/Disabled."
3. **The canonical story is the slot-default oracle.** Any time generation produces an empty slot, ask: did the canonical story show what should go there?
4. **Hidden-by-default for state-conditional content** (`*Indicator`, `*ScrollButton`, `*Arrow`) is correct. Designers use visibility toggle to inspect the active state.
5. **Foundation tokens are stable across extraction.** Component-scoped variables move with the component during break-apart; foundation variables stay put. The audit should distinguish.
6. **Multi-state components want a "spec grid" alongside the published Component.** The Component is the source of truth; the spec grid is the *reference visual* showing all states/variants without designers having to flip modes/variants. Ship both.
7. **Passthrough compounds need story-driven content** to be useful. Without it, they're 100×100 grey boxes. The story is the content.
8. **Sections by source path + horizontal layout** is the right organization at the file level. Inside a section: parent at top, subs/auxes in a grid below. Don't deviate per-component without strong reason.
9. **All multi-section Figma pages stack sections horizontally, never vertically.** Sections grow tall (component anatomies, icon grids, spec frames all pile up vertically inside a section). Stacking the *sections themselves* vertically too forces nested scrolling: scroll-down inside the section, then scroll-down again to find the next section, with no way to see what's coming. Horizontal layout puts sections side-by-side at `y = 0` so the canvas reads like a bookshelf — pan right to browse categories, scroll down inside a section to browse its contents. This applies to the Components page (per-source sections), the Icons page (per-category sections), and any future page with N comparable sections. Confirmed 2026-05-08 after the Material Symbols icon library was first generated vertically and proved unusable to skim.
10. **Figma stores ComponentNode property keys as `name#hash`, not `name`** — even on bare `COMPONENT` nodes (not just `COMPONENT_SET` variant properties). Every existence-check helper for component properties MUST match either the exact `name` OR any key starting with `name + "#"`. A `hasOwnProperty(defs, name)` check alone returns false when Figma has rewritten the key with a hash, and the surrounding addComponentProperty call then silently appends a numeric suffix on the *display* side. The audit on 2026-05-08 found CheckboxIndicator with 14 SLOTs, DialogContent with 28+, Input with 24 — all because the dedup helper missed the hash form.
11. **Generator fixes need a one-shot migration path for pre-fix artifacts.** The 2026-05-08 audit found three classes of stale data that landed before their respective fixes and were never cleaned up: (a) duplicate component properties from pre-dedup runs, (b) garbage-named slots from the pre-conditional-rendering JSX-encoded names (`error_____span_className__text_xs_text_cds_red_500…`), (c) private `.Dialog`/`.Sheet`/`.Sidebar` parents from the pre-alias-parent-collision compound detection. The new code prevents future occurrences but doesn't sweep what's already there. Every generator fix that changes WHAT gets created should ship with a paired CLEANUP pass that runs once at the start of the next generation and removes the obsolete artifacts.
12. **Foundation token coverage must match the source palette, not just shadcn defaults.** centric-ui adds `info`/`success`/`warning`/`danger`/`purple` on top of shadcn's standard set. The foundation scaffold only ships shadcn defaults, so per-mode CVA values for those extra tokens fall back to literal grey. The visible bug: Button spec grid renders info/success/warning cells as near-white pills. Audit any source palette before treating the foundation as authoritative; the foundation is the *upper bound* of color tokens, not just a baseline.
13. **CVA size axes can be structural, not just stylistic.** shadcn's Button uses `size: { default, sm, lg, icon, icon-sm, icon-lg }`. The `icon-*` values aren't just smaller paddings — they're a different *shape* (square, no label). Treating size as a pure token-shift axis (height/padding variables) renders icon variants with the regular label still visible, overflowing the box. Detect axis values whose names start with `icon` and either suppress the label in those modes via property reference, or split them out as a separate VARIANT axis.

---

## Track this

- [x] Confirm whether `args:`-driven story defaults should be added (would fix Collapsible). → P1.5 landed
- [x] "Alias-parent collision" handling. → P1.4 detector landed; **legacy artifact migration still needed** (2026-05-08 audit)
- [ ] **componentHasProperty must match `name#hash` form** — currently broken existence check (2026-05-08 audit; the visible cause of post-fix property pollution).
- [ ] Conditional-rendering legacy garbage-name cleanup pass — long underscore-laden property names from pre-P0.3 generations need an opt-in sweep.
- [ ] Foundation palette extension for centric extras (info/success/warning/danger/purple).
- [ ] CVA structural-axis support — icon-* sizes should hide the label.
- [ ] Text-fill propagation in `applyTextNode` — text colors don't theme yet because parent `textFillToken` isn't pushed into TextNode fills.
- [ ] Decide variant-vs-mode split for state coverage in Phase 4. (See related entry's "Open architectural problem" section.)
- [ ] Foundation variable binding — design the lookup path from styleStub token → foundation variable ID. → P1.1 landed for color/float; text-fill still pending
- [ ] Spec-grid generation as a first-class output of the plugin? → P2.2 landed (Badge + Button currently the only CVA components).
