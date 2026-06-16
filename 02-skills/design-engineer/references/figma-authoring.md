# Figma Authoring Reference

Comprehensive reference for creating and maintaining styles, variables, components,
component sets, and slots in Figma. Load this spoke when building or refactoring
any Figma library asset.

---

## Table of Contents

1. Styles — creation, nesting, variable binding
2. Variables — structure, collections, modes, scoping
3. Components — anatomy, properties, naming
4. Component Sets — variant structure, property mapping
5. Slots — when to use, creation, constraints, migration
6. Patterns — composition strategies, preferred instances, documentation
7. Optimization & File Health — performance, layer hygiene, library architecture, Code Connect

---

## 1. Styles

Styles are reusable visual properties applied to layers. They define the "look"
independently of the "structure" (which is the component's job).

### Style types

| Type | Controls | Variable-bindable? |
|---|---|---|
| Color (fill/stroke) | Solid, gradient, image | Yes — bind to color variables |
| Text | Font family, size, weight, line height, letter spacing, paragraph spacing | Yes — each property independently |
| Effect | Drop shadow, inner shadow, layer blur, background blur | Yes — per sub-property (color, offset, blur, spread) |
| Layout grid | Columns, rows, grid | Yes — count, gutter, margin, offset |

### Creating styles with nested variables

The power move: every style should reference variables, not raw values.

**Workflow:**
1. Create variables first (see section 2). Establish the full token tiers
   before touching styles.
2. Create the style (e.g., a text style for "Body / Default").
3. Bind each style property to its corresponding variable:
   - Select a layer with the style applied.
   - In the right panel, click the variable icon (⬡) next to each property.
   - Select the appropriate semantic-tier variable.
4. The style now inherits from the variable. When the variable changes (e.g.,
   switching to dark mode), the style updates automatically.

**Common mistakes:**
- Binding styles to global-tier variables instead of semantic-tier. This works
  but bypasses the abstraction layer — mode switching won't map correctly.
- Creating styles without variable bindings. Every token-controlled property in
  a style should be bound. If a variable doesn't exist yet, create one.
- Duplicating what variables already handle. If a color variable with modes
  exists, you may not need a separate style — bind the variable directly to
  the layer or component property.

### When styles vs. variables

| Use case | Use styles | Use variables |
|---|---|---|
| Typography presets (Body/Default, Heading/H1) | ✓ Text styles bundle multiple properties into one reusable unit | Variables alone can't bundle font+size+weight+line-height |
| Color application | Only if you need gradients or image fills | ✓ For solid colors, variables are more flexible (modes, scoping) |
| Effects (shadows, blurs) | ✓ Bundles multiple sub-properties | Bind the sub-properties to variables inside the style |
| Spacing, sizing, corner radius | Styles don't apply to these | ✓ Variables are the only option |

**Rule of thumb:** Use styles for multi-property bundles (text, effects). Use
variables for single-property tokens (color, spacing, sizing, radius). When a
style exists, bind its internal properties to variables.

---

## 2. Variables

Variables are the token layer in Figma. They map directly to design tokens in
code (CSS custom properties, theme objects).

### Collection structure

Organize collections to mirror the 3-tier token model:

```
📁 Primitives (global tier)
  color.blue.50 ... color.blue.900
  color.neutral.0 ... color.neutral.1000
  spacing.0, spacing.2, spacing.4 ... spacing.64
  radius.none, radius.sm, radius.md, radius.lg, radius.full
  font.size.xs ... font.size.4xl

📁 Semantic (alias tier)
  Modes: Light, Dark (, [Brand A], [Brand B])
  color.background.primary → {Primitives/color.neutral.0} (Light) / {Primitives/color.neutral.900} (Dark)
  color.text.primary → {Primitives/color.neutral.900} (Light) / {Primitives/color.neutral.50} (Dark)
  color.action.primary → {Primitives/color.blue.600} (Light) / {Primitives/color.blue.400} (Dark)
  spacing.inline.sm → {Primitives/spacing.8}
  spacing.inline.md → {Primitives/spacing.16}

📁 Component (scoped tier — optional, for complex components)
  Modes: Default, Compact, Comfortable
  button.padding.x → {Semantic/spacing.inline.md} (Default) / {Semantic/spacing.inline.sm} (Compact)
  button.color.bg → {Semantic/color.action.primary}
  button.color.text → {Semantic/color.text.on-action}
```

### Variable types

| Type | Use for | Figma binding targets |
|---|---|---|
| Color | Any color value | Fill, stroke, effect colors |
| Number | Spacing, sizing, radius, opacity, font size, line height | Padding, gap, width, height, corner radius, min/max, opacity |
| String | Font family, font weight (as mapped values) | Text properties |
| Boolean | Feature flags, show/hide states | Layer visibility, component property defaults |

### Scoping

Scope variables to control where they appear in the variable picker. This
prevents designers from accidentally binding a background color to a text
property.

**Scoping recommendations:**
- `color.background.*` → scoped to "Fill color"
- `color.text.*` → scoped to "Text fill" (and "Fill color" for icon components)
- `color.border.*` → scoped to "Stroke color"
- `spacing.*` → scoped to "Gap", "Padding"
- `radius.*` → scoped to "Corner radius"
- `sizing.*` → scoped to "Width", "Height"

### Modes

Modes enable a single variable to resolve to different values based on context
(theme, brand, density, viewport).

**Mode strategy:**
- Keep mode count low. Every mode multiplies the number of values to maintain.
- Semantic collection modes handle theme switching (Light/Dark, Brand A/B).
- Component collection modes handle density (Default/Compact/Comfortable).
- Primitives collection should have zero modes — primitives are constants.

**Applying modes:**
- Set modes on frames, not on individual layers. A section frame with
  `mode: Dark` cascades to all children.
- Nested mode overrides are supported: a Light page can contain a Dark
  sidebar, which can contain a Light tooltip.

### Using modes for interactive states

Modes are not just for themes and density — they are the preferred mechanism
for expressing interactive states (hover, focus, active, disabled, error)
without creating variant permutations.

**Collection setup for state modes:**

```
📁 Component States (or per-component: "Button States")
  Modes: Default, Hover, Active, Focus, Disabled, Error

  Variables:
  state.background     → semantic/color.action.primary (Default)
                       → semantic/color.action.primary-hover (Hover)
                       → semantic/color.action.primary-active (Active)
                       → semantic/color.action.primary (Focus)
                       → semantic/color.action.disabled (Disabled)

  state.border.color   → semantic/color.border.default (Default)
                       → semantic/color.border.default (Hover)
                       → semantic/color.border.default (Active)
                       → semantic/color.border.focus (Focus)
                       → semantic/color.border.disabled (Disabled)

  state.text.opacity   → 1 (Default, Hover, Active, Focus)
                       → 0.4 (Disabled)
```

**Binding to the component:**
1. In the main component, bind visual properties (fill, stroke, opacity)
   to the state variables instead of directly to semantic tokens.
2. The state variable collection sits between the component and the
   semantic tier — it's an intermediary that resolves differently per mode.
3. The component structure stays identical across all states. No duplicated
   layers, no hidden elements toggled per variant.

**Setting the default mode explicitly:**

Do NOT leave mode assignment on "Auto." Always manually set the Default mode
on:
- The main component and its component set
- Published instances in library documentation pages
- Example frames in usage documentation

Why this matters for discoverability: When a designer inspects a component
instance and sees the mode set to "Default," they're prompted to check what
other modes exist. "Auto" is invisible — there's nothing to click, nothing
to discover. An explicitly named mode is a signpost: "There are named
alternatives here. Look at them."

In the right panel, the mode dropdown becomes a state selector. A designer
can switch a Button instance from "Default" to "Hover" to see the hover
appearance — without hunting through a variant list or detaching.

**Prototyping with state modes:**
- Use Figma's prototype interactions to switch modes on triggers:
  `On hover → Change to: Hover mode`
  `On press → Change to: Active mode`
  `While focused → Change to: Focus mode`
- This maps directly to CSS pseudo-classes (`:hover`, `:active`, `:focus`,
  `:disabled`), making the design-to-code translation clean.

**When modes can't express the state:**
If the state involves a structural change — adding a spinner for loading,
inserting an error icon, replacing content with a skeleton — that state needs
a variant or a boolean property to toggle the structural difference. Modes
only change resolved values, not layer structure. See the hub SKILL.md for
the decision boundary.

---

## 3. Components

### Anatomy checklist

Before publishing any component, verify:

- [ ] **Auto layout** applied at every level. No fixed positioning for content
      that should reflow.
- [ ] **Constraints** set correctly on non-auto-layout children (if any).
- [ ] **All token-controlled values** bound to variables (color, spacing, radius,
      sizing, typography properties).
- [ ] **Layer names** are semantic, not default ("Leading icon", not "Frame 12").
- [ ] **No hidden layers** used as show/hide workarounds — use boolean properties
      or slots instead. Hidden layers still cost memory.
- [ ] **Vectors flattened** where possible. Imported SVGs should be flattened
      (⌘E) to reduce node count.
- [ ] **Images sized appropriately.** No full-resolution photos embedded at
      thumbnail display size. Use Downsize plugin or resize before import.
- [ ] **Component description** filled in with purpose, usage guidance, and
      key variants — written for both humans and AI agents (MCP/Code Connect).
- [ ] **Property descriptions** filled in for every component property.
- [ ] **Preferred instances** set on any instance swap property or slot.
- [ ] **Code syntax** set on bound variables (CSS custom property name or
      theme path visible in Dev Mode).
- [ ] **Nesting depth** ≤ 3 levels. If deeper, evaluate whether intermediate
      components are reused — if not, flatten.

### Component properties

Use properties to expose configuration without adding variants:

| Property type | Use when | Maps to in code |
|---|---|---|
| Boolean | Show/hide a fixed element | `showIcon?: boolean` |
| Text | Expose a text layer for editing | `label: string` |
| Instance swap | Replace one instance with another of the same type | `icon: ReactNode` / named prop |
| Slot | Allow free-form content insertion (see section 5) | `children: ReactNode` / named slot prop |

**Priority order when adding flexibility:**
1. Component property (boolean, text, instance swap) — lightweight, no variant bloat
2. Slot — when content type/count is unpredictable
3. Variant — when the component's *structure* actually changes

### Naming conventions

**Components:** `PascalCase` — `Button`, `DataTableRow`, `NavigationItem`

**Variants:** `Property=Value` pairs, separated by comma-space in the
component name within the set. Only structural axes appear here — states
are expressed through variable modes, not variant names:
```
Size=Small, Emphasis=Primary
Size=Small, Emphasis=Secondary
Size=Medium, Emphasis=Primary
Size=Medium, Emphasis=Secondary
Size=Large, Emphasis=Tertiary
```

**Properties:**
- Boolean: question form — `Has icon?`, `Show helper text?`
- Text: describe the content — `Label`, `Helper text`, `Placeholder`
- Instance swap: describe what's being swapped — `Leading icon`, `Avatar`
- Slot: describe the region — `Content`, `Actions`, `Header`

---

## 4. Component Sets

A component set groups variants of the same component. In Figma, this is the
purple-dashed-border container created by `combineAsVariants()` in plugins or
by combining components manually.

### Variant matrix

Plan the matrix before building. Map every axis — but separate structural
axes (variants) from visual-state axes (modes):

```
Button variant matrix:
  Structural axes (variants):
    Size:     Small | Medium | Large
    Emphasis: Primary | Secondary | Tertiary | Ghost

  State axes (variable modes — NOT variants):
    State:    Default | Hover | Active | Focus | Disabled

  Boolean properties (NOT variant axes):
    Has icon: true | false
```

With this approach:
- Variant count = 3 × 4 = 12 (Size × Emphasis only)
- States are expressed through a dedicated variable collection with modes
- `Has icon` is a boolean property

Compare this to the naive approach of putting everything on variant axes:
3 × 4 × 5 × 2 = 120 variants. The modes-first approach reduces this by 90%.

**Reduction strategies (priority order):**
1. **Move interactive states to variable modes.** This is the highest-impact
   reduction. States like hover, focus, active, and disabled change visual
   properties (color, opacity, border) but not component structure. Variable
   modes express this naturally. See section 2, "Using modes for interactive
   states," for the full setup.
2. **Move boolean toggles to component properties.** `Has icon` as a boolean
   property eliminates a 2× multiplier from the variant matrix.
3. **Move content variation to slots.** Instead of creating variants for
   "card with image," "card with text only," "card with video" — use a
   content slot.
4. **Reserve variants for structural differences only.** Size changes that
   alter padding, icon sizing, and internal spacing. Emphasis levels that
   change the overall visual weight. Orientation changes (horizontal vs.
   vertical). These genuinely change the component's structure.

### Structure rules

- All variants share the same base anatomy. If a variant requires fundamentally
  different structure (not just show/hide), it may be a separate component.
- Keep auto layout settings consistent across variants at the same size tier.
- Shared elements should be in the same layer position across all variants to
  support smooth prototyping transitions.
- Description on the component set should document the full variant matrix and
  usage guidance.

---

## 5. Slots

Slots are native Figma component properties (open beta, March 2026) that define
flexible regions inside components where designers can freely add, remove, and
rearrange content in instances — without detaching.

### When to use slots

| Signal | Use a slot |
|---|---|
| Designers frequently detach this component to add content | ✓ |
| The component has repeating elements (list items, tabs, menu options) | ✓ |
| Content type varies per instance (text, image, icon, nested component) | ✓ |
| The component needs a flexible "body" or "content area" | ✓ |
| You're hiding/unhiding layers to simulate content flexibility | ✓ Migrate to slot |
| You have excessive variants to cover content permutations | ✓ Slot replaces many |

### When NOT to use slots

| Signal | Use instead |
|---|---|
| One-to-one instance replacement (icon swap, avatar swap) | Instance swap property |
| Binary show/hide of a fixed element | Boolean property |
| The component's structure changes (not just content) | Variant |
| Content is always the same type, just different values | Text property |

### Creating slots

**Convert an existing frame to a slot:**
1. Select a frame inside a main component.
2. Right-click → "Convert to slot" (or ⌘⇧S / ⌃⇧S).
3. Name the slot descriptively: "Content", "Actions", "List items".
4. Add a description explaining what should go in the slot.
5. Set preferred instances to guide designers toward approved content.

**Wrap non-frame layers in a slot:**
1. Select one or more layers (text, groups, instances) inside a main component.
2. Right-click → "Wrap in new slot".
3. A new slot frame is created containing your selection.

**Create from the properties panel:**
1. Select a main component.
2. In the Properties section of the right panel, click ⊕.
3. Select "Slot".
4. A new empty slot frame is added to the component.

### Slot configuration

- **Preferred instances**: Restrict what can be placed in the slot. Use this to
  enforce design system compliance — e.g., a "Actions" slot that prefers only
  Button and IconButton components.
- **Default content**: Slots can ship empty or pre-populated. Pre-populated
  slots show designers the intended usage; empty slots signal "fill this in."
- **Cross-variant slots**: Apply a slot property across variants using multi-edit.
  Select the same frame in multiple variants → create slot property once →
  it applies to all.

### Slot design patterns

**Repeating content (lists, tabs, menus):**
- Create the slot with one default item inside.
- Designer duplicates the item within the slot to add more.
- Use auto layout on the slot frame so items reflow automatically.
- Set preferred instances to the specific list item / tab / menu item component.

**Flexible body (cards, modals, dialogs):**
- Create a slot for the body region.
- Leave it empty or add a placeholder text layer.
- Don't restrict preferred instances too tightly — body content is varied
  by nature. Consider allowing text, images, and a curated set of components.

**Action bars (toolbars, card footers, modal footers):**
- Create a slot with 1-2 default button instances.
- Set preferred instances to the button component variants.
- Use auto layout with gap for consistent spacing between actions.

### Migrating to slots

Common pre-slot workarounds and their migration path:

| Old pattern | Migration |
|---|---|
| Hidden layers (unhide to use) | Remove hidden layers, convert parent frame to slot, add the layers as default slot content |
| Instance swap property on a wrapper | If the swapped content varies in type or count, convert to slot. If it's always 1:1 same-type replacement, keep as instance swap. |
| "Detach and customize" culture | Identify the detach point, convert that region to a slot, re-publish. Announce the change. |
| Excessive variants for content combos | Remove content-driven variants, replace with slot + fewer structural variants |

---

## 6. Patterns — Composition Strategies

### Component composition hierarchy

Build from the bottom up:

```
Primitives (tokens, icons, typography presets)
  ↓
Atoms (Button, Badge, Avatar, Input, Checkbox)
  ↓
Molecules (InputGroup, CardHeader, ListItem, Breadcrumb)
  ↓
Organisms (DataTable, Modal, NavigationBar, FormSection)
  ↓
Templates (PageLayout, DashboardGrid, SettingsView)
```

Each level consumes the level below via instances, slots, and instance swap
properties. No level reaches down more than one tier — an Organism should not
directly reference a Primitive token; it should reference the Atom that
consumes that token.

### Documentation in Figma

Every published component should have:

1. **Component set description**: What it is, when to use it, when *not* to use it.
2. **Property descriptions**: What each property controls and valid values.
3. **Preferred instances**: On instance swap properties and slots — guide
   designers toward the right child components.
4. **Usage page** (for complex components): A dedicated Figma page showing
   the component in context, with annotations explaining anatomy, spacing
   logic, responsive behavior, and accessibility requirements.
5. **Code Connect** (if available): Link to the corresponding code component
   so developers see the implementation alongside the design.

### Versioning and publishing

- Publish changes with meaningful descriptions. "Updated button padding" is
  better than "Updates."
- Use the library update notification to communicate breaking changes.
- When migrating to slots or restructuring variants, publish incrementally:
  add the new pattern first, deprecate the old one in a subsequent release,
  then remove it after consumers have migrated.
- Never delete a published component without a migration path.

---

## 7. Optimization & File Health

Figma runs in a browser with a ~2GB WASM memory ceiling per tab. Large design
systems hit this ceiling fast if not architected carefully. These practices keep
libraries performant without sacrificing flexibility.

### Layer hygiene

**Hidden layers cost memory.** Every hidden layer inside a component is loaded
into memory when any instance of that component exists in a file. The old
workaround of hiding layers to simulate flexibility (hiding an icon, hiding a
description row) should be replaced with component properties (booleans to
toggle visibility) or slots. If hidden layers remain, they should be actively
cleaned up — don't leave stale structural layers from previous iterations.

**Name every layer semantically.** "Frame 847" and "Rectangle 12" are the
most common signs of design debt. Semantic names ("Leading icon," "Content
area," "Divider") serve three purposes: they make the layers panel navigable,
they improve the output of Figma's MCP server and Code Connect (AI agents
interpret semantic names meaningfully), and they make component override
behavior predictable (Figma matches overrides by layer name during variant
swaps).

**Flatten complex vectors.** Imported SVGs or boolean-operated shapes can
contain dozens of unnecessary vector points and groups. Flatten to a single
vector where possible — fewer nodes = less memory. Use the Figma "Flatten"
command (⌘E / Ctrl+E) on finalized vector artwork.

**Remove detached instances.** Detached instances are dead weight — they
retain all the memory cost of an instance but receive no library updates.
Audit periodically and either re-attach or convert to frames.

### Image optimization

**Images are the biggest memory consumer.** A 4000×3000px photo placed at
200×150px in a frame still stores the full-resolution image in memory. Either
resize before importing, or use the Downsize plugin to compress images to
their displayed size. For placeholder images in components, use solid fills
or low-res placeholders — never embed full-resolution photos in library
components.

**Prefer vector fills over raster.** Where possible, use Figma's built-in
shape and gradient tools instead of imported images for backgrounds, patterns,
and decorative elements.

### Component architecture for performance

**Prefer properties over variants for non-structural changes.** Every variant
is a full layer tree in memory. A component set with 120 variants loads 120
layer trees. Converting boolean toggles and state changes to properties and
variable modes (as described in section 2 and section 4) dramatically reduces
the variant count without losing flexibility.

**Prefer preferred values on instance swap properties.** When you set preferred
values, Figma pre-loads only the preferred set — not the entire library — for
the swap dropdown. This reduces memory pressure in consumer files and
improves the designer's experience (shorter, curated swap lists instead of
an overwhelming full-library dump).

**Keep component nesting shallow.** Deeply nested instances (5+ levels) create
cascading update costs — a change to a deeply nested primitive ripples through
every parent. Two to three nesting levels is the practical ceiling for
performant components. If deeper nesting is structurally necessary, consider
whether the intermediate components are actually reused elsewhere. If not,
flatten them.

**Split large component sets.** If a single component set exceeds ~50 variants,
evaluate whether it should be decomposed into smaller, focused component sets.
A "Button" with 120 variants might better be three components: Button, IconButton,
and ButtonGroup — each with a manageable variant matrix.

### Library file architecture

**Split libraries by concern.** A monolithic library file containing tokens,
primitives, molecules, and organisms will hit memory limits and become slow
to publish. Recommended split:

```
📁 Tokens & Foundations (file 1)
   Variables, color styles, text styles, effect styles, grid styles.
   Published as a library. Other libraries depend on this.

📁 Primitives (file 2)
   Button, Icon, Badge, Input, Checkbox, etc.
   Publishes as a library. Depends on Tokens.

📁 Patterns / Organisms (file 3)
   DataTable, Modal, Navigation, FormSection, etc.
   Publishes as a library. Depends on Primitives + Tokens.

📁 Templates & Layouts (file 4, optional)
   Page-level compositions. May or may not be published.
```

This mirrors the composition hierarchy and means a change to a token doesn't
require opening (and loading into memory) the organism file.

**Use branches for library edits.** When making changes to a published library,
work on a branch rather than main. This avoids accumulating session history
(which bloats memory) and provides a clean merge/review point. Keep branches
short-lived — merge within a day or two. Large branch diffs can spike memory
during merge.

### Code Connect & MCP readiness

**Enrich component descriptions for AI consumption.** Figma's MCP server
exposes component descriptions to AI coding agents (Cursor, Copilot, Claude
Code). Treat component descriptions as machine-readable documentation: include
the component's purpose, when to use it, when NOT to use it, and key props
or variants. Descriptions that say "Button component" are wasted; descriptions
that say "Primary action trigger. Use for form submission, CTA, and navigation
actions. Use IconButton for icon-only actions. Variants: Size (sm/md/lg),
Emphasis (primary/secondary/tertiary/ghost)" give AI agents enough context
to use the component correctly.

**Set code syntax on variables.** Variables support a "code syntax" field
visible in Dev Mode. Populate this with the corresponding CSS custom property
name, React theme path, or platform-specific token reference. This bridges
the gap between Figma's variable name and the code implementation —
developers see `var(--color-action-primary)` in the inspect panel instead of
guessing. The SDS repo includes scripts to bulk-update code syntax values
via the Figma Variables REST API.

**Connect components to code via Code Connect.** Code Connect (UI or CLI)
maps Figma components to actual code components in your repository. When
connected, Dev Mode shows your real component code instead of auto-generated
CSS. This also feeds into the MCP server — AI agents get both the design
context and the code implementation, significantly improving code generation
accuracy. Use Code Connect UI for quick visual linking (works in-Figma, no
CLI needed) and Code Connect CLI for precise property mapping with dynamic
code examples.

**Mark components as "ready for dev."** Figma's dev readiness status is a
signal to both human developers and AI agents. Components marked as ready
appear in Code Connect and MCP server responses with higher confidence.
Components still in draft are excluded or flagged — preventing premature
implementation of work-in-progress components.

### Check Designs linter

Figma's Check Designs feature (released at Schema 2025) automatically
identifies hardcoded values and suggests the correct variable replacements.
Use it as a pre-publish quality gate:

- Run Check Designs before every library publish.
- It catches: hardcoded colors that should be variables, raw spacing values
  that should use spacing tokens, text properties that don't reference text
  styles.
- Review suggestions and apply — this is the fastest path to closing the
  gap between "tokens exist" and "tokens are actually used everywhere."
- For consumer files (not just libraries): run Check Designs after major
  design work to ensure instances haven't been overridden with hardcoded
  values.

### Prototype performance

**Avoid Smart Animate on complex components.** Smart Animate calculates
interpolation between every differing property across two frames. On complex
components with many layers, this is expensive. Use explicit variant transitions
or mode switching instead — they swap instantly without interpolation cost.

**Keep prototype flows focused.** A single prototype with 40+ connected frames
loads all frames into memory. Split distinct user flows into separate pages
with separate prototype starting points.

---

## Quick Reference — Decision Matrix

```
I need to...                              → Use
─────────────────────────────────────────────────────
Apply a color that switches in dark mode  → Color variable (semantic tier)
Bundle font+size+weight+line-height       → Text style (with variable bindings)
Let designers swap an icon                → Instance swap property
Let designers add N items to a list       → Slot (with preferred instances)
Show/hide a helper text line              → Boolean property
Change the component's visual weight      → Variant (Size or Emphasis axis)
Apply consistent spacing                  → Number variable (spacing tier)
Expose editable label text                → Text property
Define a flexible card body               → Slot (empty or with placeholder)
Apply a shadow that adapts to theme       → Effect style (with variable bindings)
Show hover/focus/disabled appearance      → Variable mode (state collection, explicit Default)
Express a structural state change         → Variant (e.g., loading state with spinner)
Let designers preview all states          → Doc-only component set (separate from production)
Reduce memory from hidden show/hide layers→ Boolean property (replaces hidden layers)
Curate the instance swap dropdown         → Preferred values on the swap property
Catch hardcoded values before publish     → Check Designs linter
Bridge Figma components to code           → Code Connect (UI for quick setup, CLI for precision)
Help AI agents use components correctly   → Rich component descriptions + Code Connect + MCP
```
