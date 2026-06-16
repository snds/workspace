---
name: figma-canvas-designer
description: >
  Generate, ideate, and modify UI screen designs directly on the Figma canvas
  using Figma MCP tools. Use this skill whenever the user mentions Figma in the
  context of creating, designing, wireframing, laying out, prototyping, or
  modifying screens, pages, views, or UI layouts. Also trigger when the user
  asks to "design something in Figma," "create a screen," "lay out a page,"
  "build a UI," "mock up," "wireframe," or any request that involves generating
  or editing visual design content on a Figma canvas — even if they just say
  "put this in Figma" or "show me what that looks like in Figma." If the user
  mentions Figma and the intent is visual design output (not plugin development
  or code generation), use this skill. Do NOT use for Figma plugin development
  (TypeScript, bundling, Plugin API code) — defer to figma-plugin-dev instead.
aliases: [figma-canvas-designer]
spec_version: "2.0"
tier: spoke
domain: design
hub: figma
prerequisites: [figma]
---

# Figma Canvas Designer

Generate and modify UI designs directly on the Figma canvas through a structured
ideation workflow. Outputs mid-fidelity screens using design system components
when available, falling back to custom frames/shapes when not.

---

## File Access: Getting the fileKey

Every Figma MCP tool requires a `fileKey`. Before any canvas work, make sure you
have one. In order of preference:

1. **User provided a Figma URL.** Extract the fileKey from the URL format
   `figma.com/design/:fileKey/:fileName?node-id=...`. The segment after
   `/design/` is the fileKey.
2. **User referenced a file by name but no URL.** Ask: "Can you share the Figma
   file URL so I can work on it directly?"

3. **User wants a fresh exploration.** Use `create_new_file` to spin up a new
   file. This requires a `planKey` — call `whoami` first to get it. If the user
   has multiple plans, ask which team/org to use.

Never assume a fileKey from a previous conversation. Always confirm you have one
before calling any Figma tool.

---

## Core Workflow: Structured Ideation

Every design request follows a **3-direction → pick → refine** cycle unless the
user explicitly asks to skip ideation and go direct.

**Skip-ideation heuristic:** If the user's request is fully specified — they've
listed the exact elements, stated the fidelity ("simple," "quick," "just X and
Y"), and there's no ambiguity about layout — skip Phase 2 and go directly to
Phase 3. Confirm briefly: "This is straightforward enough to build directly —
I'll check your DS for components and generate it." This also applies when the
user gives quick iteration feedback ("looks good, but change X") — go straight
to modification, not back through ideation.

### Phase 1: Understand the Brief

Before touching the canvas, establish:

1. **What screen/view** — name it (e.g., "Settings page," "Product detail view")
2. **Key content** — what data, controls, and actions need to appear3. **Constraints** — viewport size, platform (desktop/mobile/responsive), any
   layout requirements the user has stated
4. **Context** — where does this screen sit in the user's flow? What comes
   before/after?

If the user's request is vague ("design me a dashboard"), ask one focused
clarifying question. Don't interrogate — infer reasonable defaults and state
your assumptions so the user can correct.

### Phase 2: Present 3 Directions

Describe 3 distinct layout approaches **in conversation** before building
anything. Each direction should be a short paragraph covering:

- **Layout strategy** — how content is organized (e.g., sidebar + main panel,
  stacked cards, split view, tabbed sections)
- **Visual hierarchy** — what gets emphasis, what recedes
- **Tradeoff** — what this direction prioritizes vs. what it sacrifices

Example format:

> **Direction A — Dense data table with filters panel**
> Prioritizes information density and power-user efficiency. Left sidebar for
> persistent filters, main area is a full-width data table with inline editing.
> Tradeoff: less visually approachable for new users.
>
> **Direction B — Card-based overview with drill-down**
> Prioritizes scannability and progressive disclosure. Top-level shows summary
> cards; clicking into a card reveals detail. Tradeoff: requires more clicks to
> reach specific data.
>
> **Direction C — Split panel with contextual detail**
> Prioritizes comparison and context. Master list on the left, detail panel on
> the right updates based on selection. Tradeoff: constrained horizontal space
> on smaller viewports.

Ask the user to pick a direction (or combine elements from multiple).

### Phase 3: Build on Canvas

Once a direction is selected, generate the design in Figma using `use_figma`.
See [Tool Routing](#tool-routing) and [Canvas Generation Patterns](#canvas-generation-patterns)
for implementation details.

### Phase 4: Refine

After the initial build, take a screenshot with `get_screenshot` and share it.
Ask: "Here's where we're at — what should I adjust?" Then iterate using
`use_figma` to modify the existing canvas content.
---

## Tool Routing

### Primary tools and when to use them

| Tool | Use for |
|---|---|
| `search_design_system` | **Always call first** before generating. Search for relevant components (buttons, inputs, tables, cards, navbars) and variables (colors, spacing, typography tokens). |
| `use_figma` | All canvas creation and modification — creating frames, placing components, drawing shapes, setting text, applying auto-layout, binding variables. This is the primary workhorse. |
| `get_screenshot` | Visual check after generation or modification. Always screenshot the result and share with the user. |
| `get_metadata` | Inspect existing canvas structure when the user asks to modify something already on the page. Use node IDs from metadata to target edits. |
| `get_design_context` | Deep inspection of a specific node — get its code representation and screenshot. Use when the user points to a specific element to understand its current structure before modifying. |
| `get_variable_defs` | Inspect what variables are bound to existing nodes. Useful when modifying designs to preserve token bindings. |
| `create_new_file` | Only when the user explicitly asks for a new file, or when working in a fresh exploration that shouldn't touch existing work. Requires `whoami` first to get planKey. |
| `generate_diagram` | **Only if the user explicitly asks for a FigJam wireframe or flow diagram.** Default is always Figma canvas. |

### Routing rules

1. **DS check is non-blocking.** Always call `search_design_system` before
   generating, but if no relevant components are found, proceed with custom
   frames/shapes. Flag what was improvised: "No button component found in your
   DS — I used a rounded rectangle with your primary color token."

2. **Yield to figma-plugin-dev** when the request is about building a Figma
   plugin (TypeScript, manifest.json, Plugin API code, bundling). This skill
   handles *using* the Figma Plugin API via MCP to place designs — not
   *developing* plugins.

3. **Modification requests** (e.g., "move the sidebar to the right," "swap the
   table for cards," "resize the header") go through `get_metadata` first to
   understand the current structure, then `use_figma` to make changes.
---

## Design System Integration

### Search strategy

When the user's request implies specific UI elements, search for them before
building. Map common request language to DS search queries:

| User says | Search for |
|---|---|
| "form," "input fields" | `input`, `text field`, `form`, `select`, `checkbox` |
| "table," "data grid" | `table`, `data table`, `row`, `cell` |
| "navigation," "sidebar" | `nav`, `sidebar`, `menu`, `navigation` |
| "button," "action" | `button`, `icon button`, `CTA` |
| "card," "tile" | `card`, `tile`, `container` |
| "modal," "dialog" | `modal`, `dialog`, `overlay` |
| "timeline," "stepper," "progress" | `timeline`, `stepper`, `progress`, `step indicator` |
| "attributes," "key-value," "details" | `list`, `description list`, `property`, `key value` |
| "image," "gallery," "media" | `image`, `gallery`, `carousel`, `thumbnail`, `media` |
| "badge," "tag," "chip," "status" | `badge`, `tag`, `chip`, `status`, `indicator` |
| "tabs," "tab bar" | `tab`, `tabs`, `tab bar`, `segmented control` |
| "header," "top bar," "app bar" | `header`, `app bar`, `top bar`, `toolbar` |
| "avatar," "user," "profile" | `avatar`, `user`, `profile`, `icon` |
| "toast," "snackbar," "alert" | `toast`, `snackbar`, `alert`, `notification`, `banner` |

**Catch-all:** For any UI element not in the table above, search using the
user's exact terminology plus 1–2 common synonyms. The DS search is keyword-
based and forgiving — it's better to search and find nothing than to skip the
search and miss a component that exists.

Run multiple targeted searches rather than one broad query. Each search should
focus on one UI element type — the DS search returns better results with
specific terms.

### Using found components

When `search_design_system` returns components:

1. Note the component `key` from the results
2. In `use_figma`, import via `figma.importComponentByKeyAsync(key)`
3. Create an instance with `.createInstance()`
4. Position and resize the instance within your layout

### When components aren't found

Build with primitives and flag it:

- Use `figma.createFrame()` for containers
- Use `figma.createRectangle()` for shapes and placeholders
- Use `figma.createText()` for labels (load font first: `await figma.loadFontAsync({ family: "Inter", style: "Regular" })`)
- Apply auto-layout for structure: `frame.layoutMode = "VERTICAL"` or `"HORIZONTAL"`
- Use semantic colors from variable search results when available

Always tell the user what was improvised so they can decide whether to
componentize it later.
---

## Canvas Generation Patterns

### Frame setup

Every generated screen starts with a properly sized parent frame:

```javascript
const page = figma.currentPage;
const frame = figma.createFrame();
frame.name = "Screen Name";
frame.resize(1440, 900); // Desktop default — adjust per brief
frame.layoutMode = "VERTICAL";
frame.primaryAxisAlignItems = "MIN";
frame.counterAxisAlignItems = "MIN";
frame.paddingTop = 0;
frame.paddingBottom = 0;
frame.paddingLeft = 0;
frame.paddingRight = 0;
frame.itemSpacing = 0;
page.appendChild(frame);
```

Adjust dimensions based on platform:
- Desktop: 1440×900 or 1280×800
- Tablet: 768×1024
- Mobile: 375×812

### Auto-layout first

Build everything with auto-layout. Avoid absolute positioning unless the design
explicitly requires overlapping elements. Auto-layout produces designs that are
structurally coherent and easier to modify later.
### Font loading

Always load fonts before creating text nodes. Default to Inter if no DS font is
specified:

```javascript
await figma.loadFontAsync({ family: "Inter", style: "Regular" });
await figma.loadFontAsync({ family: "Inter", style: "Semi Bold" });
await figma.loadFontAsync({ family: "Inter", style: "Bold" });
```

### Color application

Prefer variables/tokens when available. When applying colors directly, use the
Figma `SolidPaint` format:

```javascript
node.fills = [{ type: "SOLID", color: { r: 0.2, g: 0.2, b: 0.2 } }];
```

Color values in Figma are 0–1 floats, not 0–255 integers.

### Naming conventions

Name every layer meaningfully. Use `/` separators for hierarchy:
- `Header/Logo`
- `Sidebar/NavItem/Label`
- `Content/Table/Row/Cell`

This makes the layers panel navigable and supports future componentization.
### Placeholder content

Use realistic, contextually appropriate content — not lorem ipsum. Field labels,
helper text, button copy, column headers, and sample data should reflect what the
actual UI would say. Examples:

- Button: "Save Changes" not "Button" or "Click Here"
- Input label: "Email address" with placeholder "you@company.com"
- Table headers: "Product Name," "Status," "Last Modified" — not "Column 1"
- Status badges: "In Review," "Approved," "Draft"

Realistic content helps the user evaluate whether the layout actually works for
their data.

### Common layout recipes

For multi-section screens, nest auto-layout frames to compose standard patterns:

**App shell (header + sidebar + content):**
```
Root (VERTICAL)
├── Header (HORIZONTAL, fill width, fixed height 64)
└── Body (HORIZONTAL, fill width, fill height)
    ├── Sidebar (VERTICAL, fixed width 240, fill height)
    └── Content (VERTICAL, fill width, fill height)
```
**Stacked page (header + scrollable sections):**
```
Root (VERTICAL)
├── Header (HORIZONTAL, fill width, fixed height 64)
├── Hero/Banner (VERTICAL, fill width, fixed height)
├── Section 1 (VERTICAL, fill width, hug height, padding 24)
├── Section 2 (VERTICAL, fill width, hug height, padding 24)
└── Footer (HORIZONTAL, fill width, fixed height)
```

**Split panel (master-detail):**
```
Root (HORIZONTAL)
├── List panel (VERTICAL, fixed width 360, fill height)
│   ├── Search bar
│   └── List items (VERTICAL, fill, itemSpacing 1)
└── Detail panel (VERTICAL, fill width, fill height, padding 24)
```

Use these as starting skeletons, then populate sections with content per the
user's brief.

---

## Modification Workflow

When the user asks to modify existing canvas content:

1. **Identify the target.** Use `get_metadata` with the page node ID to get the
   layer tree. If the user references a specific element by name or position,
   find its node ID in the metadata.
2. **Screenshot before.** Take a screenshot of the current state with
   `get_screenshot` so you and the user have a baseline. This enables before/after
   comparison and makes it easier to evaluate the change.

3. **Inspect before editing.** For complex modifications, use `get_design_context`
   on the target node to understand its current structure, auto-layout settings,
   and component bindings.

4. **Preserve what exists.** When modifying a frame, don't recreate it — edit
   properties in place. When rearranging children, use `parent.insertChild(index, node)`
   rather than removing and re-adding.

5. **Screenshot after.** Take a screenshot of the modified result and share it
   alongside the before screenshot for comparison.

6. **Rollback.** If a modification produces unexpected results (wrong node
   targeted, layout breaks), inform the user they can undo via Figma's history
   (Cmd+Z / Ctrl+Z). MCP operations appear in Figma's undo stack just like
   manual edits.

---

## Edge Cases

### Multiple screens
If the user asks for multiple related screens (e.g., "design the list view and
detail view"), generate each as a separate top-level frame on the same page,
positioned side by side with 100px spacing.

### Responsive variants
If the user asks for responsive versions, generate separate frames at each
breakpoint, named with the breakpoint suffix (e.g., "Settings/Desktop",
"Settings/Mobile").
### When the user provides a URL or reference
If the user shares a Figma URL, extract the fileKey and nodeId. Use
`get_design_context` to understand what's there, then proceed with the request
(modify, extend, or use as reference for a new design).

### Iteration shortcut
Iteration feedback ("looks good, but...") bypasses ideation entirely — see the
skip-ideation heuristic at the top of Core Workflow.

---

## Skill Routing — Icon & Variable Font Work in Figma

When the Figma canvas work involves **icon authoring for a font pipeline**
(not general UI icon placement), load `variable-icon-font-architect` and its
spoke network. This includes: drawing icons on a 24×24 grid with stroke rules,
preparing masters for interpolation, outline/flatten workflows for font export,
component set variants for opsz, or any CentricSymbols icon authoring.

The icon font network provides the deep domain knowledge for path construction
(`lead-vector-designer`), icon design language (`lead-icon-artist`), and the
mathematical foundations for optical correction and node placement.

## Related
- hub → [[figma]]
