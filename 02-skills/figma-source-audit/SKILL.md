---
name: figma-source-audit
description: >
  Audit a Figma component (or set of generated components in a Figma library file)
  against its canonical source — typically a shadcn/Tailwind/CVA repo — to grade
  visual fidelity, state coverage, anatomy correctness, slot/property mapping,
  and variable binding. Produces gap analysis + ranked recommendations covering
  variants, modes-as-variants, component-specific variables, properties, states,
  and composition. Use this skill whenever reviewing the output of the figma-
  repo-sync-plugin (or any source-driven Figma generator), assessing whether a
  hand-built Figma library matches its code spec, or planning the next iteration
  of a generated design system. Trigger words: "audit Figma file", "audit
  components", "review Figma against source", "grade Figma library", "Figma
  visual QA", "Figma generation review", "design-engineer audit", "spec gap",
  "state coverage", "variant audit", "shadcn parity in Figma".
aliases: [figma-source-audit]
spec_version: "2.0"
---

# Figma source-audit — methodology

The job: take a Figma file's components and grade them against their source-of-truth
React/CSS code (and the canonical visual reference). Output: a gap analysis with
ranked recommendations, organized so the next chunk of work is obvious.

This skill is the *methodology*. The accumulated *findings* from past audits live
in the companion knowledge entry
[`figma-source-audit-patterns.md`](../../08-knowledge/cross-domain/figma-source-audit-patterns.md);
read it before starting an audit so you don't re-discover the standard gap set.

This skill operates **above** the dual-lens defaults from
[`design-engineer`](../../00-frameworks/00-README.md). Both lenses apply throughout —
Designer ("does it serve the user?") + Developer ("is the API minimal and
predictable?") — but with a primary focus on fidelity and parity with source.

---

## When to use this skill

- After a generation run of the figma-repo-sync-plugin, to grade the output.
- When reviewing a hand-built Figma library that's supposed to match a code spec.
- When planning a "next chunk" for the plugin and you need to know which components
  are most under-served.
- When a designer says "this Figma component doesn't feel right" and you need a
  framework for the conversation.

Do NOT use for:
- Brand-new Figma design (no source spec exists yet) — that's
  [`figma-canvas-designer`](../figma-canvas-designer/SKILL.md) territory.
- Plugin-internal generator bugs — those go to
  [`figma-plugin-dev`](../figma-plugin-dev/SKILL.md).
- Pure design critique unattached to code — use
  [`ds-advisor`](../ds-advisor/SKILL.md) instead.

---

## The five-phase audit loop

Every audit moves through these phases in order. Skipping phases produces
recommendations that don't survive scrutiny.

### Phase 1 — Source ingestion (per component)

For each component:
- Read its `.tsx` source file end-to-end. No skimming.
- Read its `.stories.tsx` (or equivalent) — note every story render AND args set.
- Identify which of the **five source shapes** applies: pure alias, passthrough
  wrapper, styled wrapper (single), CVA component, or compound. (See
  `figma-source-audit-patterns.md` for the table.)
- Note the primitive base library (Base UI, Radix, plain HTML).
- List exports. List props. Note conditional rendering patterns
  (`{X && JSX}`), render-prop patterns (`<X render={<Y/>}>...</X>`), and slot
  patterns (`{children}`).

### Phase 2 — Visual reference (per component)

Pull the canonical visual reference. Sources in priority order:
1. The component's own storybook (run locally if possible).
2. shadcn-ui docs page for the component (if shadcn-derived).
3. A live production site using the same component (Vercel sites with shadcn
   are good; Tailwind UI examples).

Note from the reference:
- Which **states** are shown (Default, Hover, Focus, Active, Disabled, Error,
  Loading, Selected — record which ones the canonical examples expose).
- Which **variant axes** are shown (Type, Size, Density, Orientation, etc.).
- The **canonical composition** when the component is compound — what wraps
  what.
- Visual properties that aren't variant axes (border-radius, shadow elevations,
  typography sizes).

### Phase 3 — Figma generated state (per component)

**Required tool usage** — the audit must collect data from at least four
distinct MCP tools per component. Screenshots alone are insufficient and
produce surface-only findings. Combine the tools below; treat any Phase-3
section that's screenshot-only as incomplete.

| MCP tool | What it tells you the screenshot can't | When to use |
|---|---|---|
| **`get_metadata`** | Section + symbol structure, dimensions, naming, hierarchy. Fast overview of the whole compound or page. | First call per audit. Always. |
| **`get_screenshot`** | The pixels. Final visual sanity check. Bounds, overflow, clipping, glaring layout breaks. | Once you know which nodes are interesting from `get_metadata`. |
| **`get_design_context`** | The component as React+Tailwind code, **including CSS-var references for every bound variable** (`bg-[var(--background,#fff)]`). Reveals which fields ARE bound and the fallback color. The single fastest way to confirm "is this variable-bound or hard-coded?" | Always, for every component you're auditing for variable bindings. |
| **`get_variable_defs`** | A flat object of `{varName: resolvedValue}` for every variable visible on the node. Confirms what Figma sees the node resolving to. | When you need to know the *resolved* value (e.g. "what color does Button's background actually paint?"). |
| **`use_figma`** | Arbitrary Plugin API queries. The deepest inspection tool — bound-variable maps, plugin data, collection contents, mode lists, variable values per mode, component property definitions. | When the other tools don't expose what you need. See the snippets below. |

**Minimum data to collect per component:**
- Component name (public vs `.private` — does it match expected?)
- Section name + position (from `get_metadata`)
- Outer auto-layout: direction, sizing modes, alignment, padding (from `use_figma`)
- Inner anatomy: present? sized? styled? (from `get_metadata` + screenshot)
- **Component property definitions**: BOOLEAN/TEXT/INSTANCE_SWAP/SLOT/VARIANT. Names. Defaults. (from `use_figma`)
- **Variable bindings on every binding-capable field**: fills, strokes, height, padding\*, itemSpacing, cornerRadius, fontSize, fontWeight, fontFamily, etc. Note WHICH variable (foundation vs. component-scoped) and the resolved value per relevant mode. (from `use_figma` or `get_design_context`)
- Hidden-by-default elements (indicators, scroll buttons): present and hidden? (from `use_figma`)
- Plugin data: `centric-source-path`, `centric-component-name`, `centric-dependency-refs`, etc. — confirms generator metadata is intact.

For compound files: collect for parent + each sub + each auxiliary.

#### `use_figma` snippets — the standard audit toolkit

Reuse and adapt these. They're written to return strings so the result
shows up directly in the tool response.

**A. Auto-layout + bindings dump for one node.** First-line check for any
audit. Shows direction, sizing, padding, gap, fills/strokes, and every
bound variable.

```javascript
const node = figma.getNodeById("19:1213");
const out = [];
const get = (k) => (k in node ? String(node[k]) : "-");
out.push(node.type + ' "' + node.name + '" ' + Math.round(node.width) + "x" + Math.round(node.height));
out.push("  layoutMode=" + get("layoutMode") + " ps=" + get("primaryAxisSizingMode") + " cs=" + get("counterAxisSizingMode"));
out.push("  padding=" + get("paddingLeft") + "/" + get("paddingTop") + "/" + get("paddingRight") + "/" + get("paddingBottom") + " gap=" + get("itemSpacing"));
const bv = node.boundVariables || {};
for (const f of Object.keys(bv)) {
  const v = bv[f];
  const list = Array.isArray(v) ? v : [v];
  for (const item of list) {
    const variable = figma.variables.getVariableById(item.id);
    out.push("  " + f + " → " + (variable ? variable.name : "(missing)"));
  }
}
return out.join("\n");
```

**B. Component property definitions dump.** Reveals exactly which props
the Component exposes — names, kinds, defaults — without designers having
to open the properties panel. Pair with the source's prop list to find
gaps.

```javascript
const node = figma.getNodeById("19:1213");
if (node.type !== "COMPONENT" && node.type !== "COMPONENT_SET") return "not a Component";
const defs = node.componentPropertyDefinitions || {};
const out = [];
for (const name of Object.keys(defs)) {
  const d = defs[name];
  out.push(name + " [" + d.type + "]" + (d.defaultValue !== undefined ? " default=" + JSON.stringify(d.defaultValue) : ""));
}
return out.join("\n") || "(no component properties)";
```

**C. Variable collection inventory.** Every collection, its modes, and how
many variables it contains. The one-shot "is the foundation scaffold
populated?" check.

```javascript
const out = [];
for (const c of figma.variables.getLocalVariableCollections()) {
  out.push("'" + c.name + "' — " + c.variableIds.length + " vars, modes: [" + c.modes.map((m) => m.name).join(", ") + "]");
}
return out.join("\n");
```

**D. Per-mode value dump for one collection.** Use to sanity-check that
modes actually carry distinct values (a common bug is all modes resolving
to the same value because mode IDs got mixed up).

```javascript
const colName = "Button — Types";
const c = figma.variables.getLocalVariableCollections().find((c) => c.name === colName);
if (!c) return "no collection " + colName;
const modes = c.modes;
const out = ["columns: " + modes.map((m) => m.name).join(" | ")];
for (const id of c.variableIds) {
  const v = figma.variables.getVariableById(id);
  if (!v) continue;
  const row = [v.name];
  for (const m of modes) row.push(JSON.stringify(v.valuesByMode[m.modeId]));
  out.push(row.join(" | "));
}
return out.join("\n");
```

**E. Foundation-binding cross-check.** For each component-scoped variable,
check whether its value is a literal color/number OR a *variable alias*
to a foundation variable. The presence of aliases tells you the foundation
wiring is in place.

```javascript
const collectionsToCheck = ["Button — Types", "Button — Sizes"];
const out = [];
for (const colName of collectionsToCheck) {
  const c = figma.variables.getLocalVariableCollections().find((c) => c.name === colName);
  if (!c) { out.push("no " + colName); continue; }
  for (const id of c.variableIds) {
    const v = figma.variables.getVariableById(id);
    if (!v) continue;
    for (const m of c.modes) {
      const val = v.valuesByMode[m.modeId];
      const isAlias = val && typeof val === "object" && "type" in val && val.type === "VARIABLE_ALIAS";
      if (isAlias) {
        const target = figma.variables.getVariableById(val.id);
        out.push(c.name + "/" + v.name + "[" + m.name + "] → ALIAS " + (target ? target.name : "(missing)"));
      } else {
        out.push(c.name + "/" + v.name + "[" + m.name + "] → literal " + JSON.stringify(val));
      }
    }
  }
}
return out.join("\n");
```

**F. Plugin data dump.** Confirms the generator's metadata for the
break-apart workflow (`centric-owned-variable-ids`, `centric-dependency-refs`, etc.).

```javascript
const node = figma.getNodeById("19:1213");
const keys = [
  "centric-generated-by",
  "centric-source-path",
  "centric-component-name",
  "centric-binding-name",
  "centric-owned-collection-ids",
  "centric-owned-variable-ids",
  "centric-dependency-refs",
  "centric-foundation-bindings"
];
return keys.map((k) => k + " = " + (node.getPluginData(k) || "(empty)")).join("\n");
```

When in doubt, prefer `use_figma` over a screenshot. The screenshot tells
you what *looks* wrong; `use_figma` tells you *why*.

### Phase 4 — Gap analysis (per component)

Compare what you've gathered. Categorize gaps into one of seven buckets — pick
the **single best fit** for each gap; don't double-classify:

1. **Anatomy missing** — structural elements the source declares but Figma doesn't show.
2. **Sizing wrong** — components at default 100×100, slots collapsed, frames over/undersized.
3. **Styling missing** — fills/borders/radii not applied; text color/size off; foundations not bound.
4. **States missing** — no Hover/Focus/Active/Disabled/Error/Loading; designers can't show the active state.
5. **Variants missing** — source has axes (CVA, `data-[size=*]`, etc.) that aren't surfaced as Figma variants/modes.
6. **Slots wrong** — missing slot, slot in wrong place, slot has no default content where the story shows one.
7. **Composition wrong** — the assembled layout doesn't match the canonical story tree.

Plus a meta-bucket for **Properties missing** (props that exist in source but
aren't surfaced as Figma component properties — TEXT, BOOLEAN, INSTANCE_SWAP).

Severity per gap: **critical** (designers can't recognize / use the component),
**high** (significantly limits usefulness), **medium** (visible but workable),
**low** (cosmetic).

### Phase 5 — Recommendations + synthesis

For each gap, recommend an approach. Use the **state-coverage taxonomy** from
the patterns entry to decide between VARIANT, MODES, SLOT, BOOLEAN, INSTANCE_SWAP.

Then **synthesize across components**: which gaps recur? A pattern that affects
10 components is one recommendation, not 10. The output of synthesis is a small
ranked list of "next chunks" — not a per-component punch list. Per-component
detail goes in an appendix, not the lead.

---

## Output format

The deliverable from an audit:

### 1. Lead with synthesis (top of the output)

Something like:

> Audited 24 generated sections in centric-ui Figma library against shadcn
> source. The four most impactful gaps:
>
> 1. **Foundation variables not bound** (affects all 24) — generated components
>    use stub palette colours instead of `Foundations / Colors` variables. Wire
>    the styleStub token resolver to look up + bind. Highest-priority.
> 2. **State coverage missing** (affects all interactive components, ~12) — no
>    Hover/Focus/Disabled variants. Phase-4 work; plan modes vs. native variants
>    decision before starting.
> 3. **Spec grids missing for CVA components** (affects ~5 — Button, Badge, …)
>    — designers can't see all Type × Size cells without flipping modes. Add a
>    grid frame per CVA component as documentation.
> 4. **Passthrough compounds lack content** (affects ~3 — Collapsible, Form,
>    NativeDialog) — story-args defaults aren't being read. Walker enhancement.

Each item: the gap, scope (count of affected components), recommended approach,
estimated next-chunk effort.

### 2. Per-component appendix (below the synthesis)

A table or short paragraph per component covering: shape, current state, top
recommendation. Use the highlights table from
`figma-source-audit-patterns.md` as the format reference.

### 3. Codify new findings

If the audit surfaces a *new* recurring pattern (not already in the patterns
entry), append it. The patterns entry is the durable record; each audit refines it.

---

## Craft-level visual checklist (REQUIRED per public component)

Codified 2026-05-09 after the audit reframe. Structural recognition is not
enough — every public component must pass these CRAFT dimensions, and every
audit must explicitly check them. Use Vision + `use_figma` together:
Vision detects "this doesn't look right"; `use_figma` tells you *why* and
gives the layout-mode / sizing / alignment / instance-reference data you
need to recommend a fix.

For each public parent component, run the seven checks below. Skipping
any check produces audits that miss craft-level gaps and call broken
components "Tier 2 — Recognisable" when they're actually unusable.

### 1. Fill / hug semantics (the most overlooked dimension)

The single most common gap. Every child of every auto-layout parent
should have its `layoutAlign` + `layoutGrow` set with intent:

- **Header / Body / Footer inside a Dialog or Card**: usually
  `layoutAlign: STRETCH` on the cross-axis (fills parent width).
- **Description text inside a Header**: usually `textAutoResize: HEIGHT`
  (wraps text on parent width) — never `WIDTH_AND_HEIGHT` (single-line,
  overflows).
- **Avatar Image / Fallback inside Avatar**: `layoutAlign: STRETCH` +
  `layoutGrow: 1` (fills both axes of the parent box).
- **Trigger / Close affordances inside a popover surface**: typically
  intrinsic-sized (don't stretch).

**`use_figma` snippet (run for every child of every parent under audit):**

```javascript
const node = figma.getNodeById("..."); // a child instance
out.push(`${node.name} ${node.width}x${node.height}`);
out.push(`  layoutAlign=${node.layoutAlign} layoutGrow=${node.layoutGrow}`);
const p = node.parent;
if (p && "layoutMode" in p) {
  out.push(`  parent layoutMode=${p.layoutMode} primary=${p.primaryAxisSizingMode} counter=${p.counterAxisSizingMode}`);
}
```

**Red flag pattern**: child width > parent content area (parent width
minus parent padding). E.g., AlertDialog 480×280, padding 24, content
area 432. Header instance 689×82 → overflow. The Header's master
auto-sized to its longest child (a non-wrapping Description), and the
instance has `layoutAlign: INHERIT` (not STRETCH). Fix at instance-
placement time.

### 2. Spacing distribution

Padding vs. gap are different concerns. Padding is *inside the
container*; gap is *between siblings*. Distribute deliberately:

- **Parent dialog**: padding = the visual breathing room around all
  content (e.g., 24px). Gap = between Header/Body/Footer (e.g., 16-24px).
- **Footer master**: usually padding=0 (parent's padding handles it) +
  gap=8 between buttons. NOT padding=16 in addition to parent's 24.
- **Card footer**: shadcn's `<CardFooter className="flex items-center
  px-6 pt-6">` — padding-top only (gap above), no horizontal padding of
  its own (parent handles px-6). The plugin shouldn't double up.

**`use_figma` snippet**: dump padding+gap for every public component and
its first-level sub-instances. Look for `padding > 0` on a child whose
parent already has the same padding. That's the double-padding smell.

### 3. Reference components vs. raw frames

shadcn compound files routinely use `<Button variant="outline">` inside
their footers (AlertDialogCancel applies `buttonVariants({ variant:
"outline" })`; Card examples literally do `<CardFooter><Button>...
</Button></CardFooter>`). The generated Figma should instance the
`Button` Component master, NOT render a raw FRAME with a TEXT child.

**`use_figma` snippet:**

```javascript
for (const c of footerMaster.children) {
  const isInstance = c.type === "INSTANCE";
  let ref = "(NOT an instance — raw frame)";
  if (isInstance) {
    try { ref = `→ "${c.mainComponent.name}"`; } catch {}
  }
  out.push(`  ${c.type} "${c.name}" — ${ref}`);
}
```

**Red flag pattern**: `FRAME "Button"` (raw, sized to text content) where
shadcn's source uses `<Button>` JSX OR applies `buttonVariants(...)` via
cn(). Fix in the generator: when a component's source applies a known
CVA's classes (like `buttonVariants(...)`), treat it as an instance of
that CVA's Component instead of a styled wrapper.

### 4. Theme-color binding for text (contrast)

Text fills must alias to the foundation when the source uses a foundation
token. Literal fills produce contrast bugs when modes flip OR when the
fallback grey clashes with the surrounding fill.

**`use_figma` snippet:**

```javascript
const text = node.findOne(n => n.type === "TEXT");
const bf = text.boundVariables?.fills;
if (bf && bf.length) {
  const v = figma.variables.getVariableById(bf[0].id);
  out.push(`  text fill → ALIAS ${v.name}`);
  // Dump per-mode values so you can see same-color-on-same-color bugs
} else {
  out.push(`  text fill: literal ${JSON.stringify(text.fills?.[0]?.color)}`);
}
```

**Red flag pattern**: text fill literal AND background fill literal in
the SAME color family (both grey, both white, both dark). That's
invisible text in some mode.

### 5. Alignment intent

Counter/primary alignment must match shadcn convention:

- **Footer action buttons**: `primaryAxisAlignItems: MAX` on a HORIZONTAL
  footer (right-aligned). VERTICAL footer with MAX is bottom-aligned —
  rarely what shadcn intends; usually the footer should have been
  generated HORIZONTAL but `flex-col-reverse sm:flex-row` collapsed to
  VERTICAL because the responsive prefix got filtered.
- **Header content**: usually `counterAxisAlignItems: MIN` (left) — but
  check if `text-center` in source intends `CENTER`.
- **Avatar fallback text**: `CENTER` on both axes (centered initials).

**Red flag pattern**: VERTICAL footer (was probably `flex-col-reverse
sm:flex-row`); CENTER-aligned Header content (was probably unintended
inheritance from a Media icon).

### 6. Surface treatment (fills / borders / shadows)

Every parent that ISN'T a flow-only container needs visible chrome:

- Popover-family (Dialog/Sheet/Popover/Dropdown/Tooltip): popover fill,
  hairline border (popover/dropdown), shadow per strength tier.
- Container categories (Card/Sidebar/Skeleton): container fill, optional
  border, optional shadow. Card uses card+border+light-shadow; Sidebar
  uses card+border+no-shadow; Skeleton uses muted+no-border+no-shadow.
- Atomic primitives (Input/Switch/Checkbox/etc.): source-driven (cn())
  classes drive the chrome.

**`use_figma` snippet:**

```javascript
out.push(`fills=${node.fills?.length} (bound: ${node.fills?.[0]?.boundVariables?.color ? "yes" : "no"})`);
out.push(`strokes=${node.strokes?.length} (weight=${node.strokeWeight})`);
out.push(`effects=${node.effects?.length} (${node.effects?.[0]?.type})`);
```

**Red flag pattern**: parent has `cornerRadius` but `fills=[]` (invisible
on dark canvas) — the surface treatment was skipped or partially
applied.

### 7. Anatomy completeness

Are all the visual affordances present? shadcn's Switch has a thumb;
Slider has a track + range + thumb; Tabs has an active indicator;
Checkbox has a check glyph. If the generated component is missing one,
the absence is a visible debris signal.

**`use_figma` snippet:**

```javascript
out.push(`${node.name}: children=${node.children.map(c => `<${c.type} "${c.name}">`).join(", ") || "(none)"}`);
```

**Red flag pattern**: an interactive component with `children=(none)`
where the source has Radix primitives like `<SwitchPrimitive.Thumb />`.
The walker dropped the primitive; fix is hardcoded Radix-primitive
materialization.

---

## Anti-patterns

- **Auditing one component in isolation.** Always look at the full file or at
  least the full pattern family (all CVA components together; all compound
  popovers together). The synthesis is more valuable than per-component depth.
- **Recommending VARIANTS for everything stateful.** State explosion is a real
  failure mode. Use modes-as-variants for token-shift state changes; reserve
  VARIANTS for structural changes.
- **Demanding pixel-perfect parity with the canonical visual.** Generation
  produces approximate visual fidelity; designers refine in Figma. Audit for
  *recognisability* and *state coverage*, not exact pixel match.
- **Treating "we generated it" as success.** Generation is the floor. The
  audit is about the gap above the floor.
- **Calling a component "Tier 2 — Recognisable" without running the craft
  checklist.** A component can be visually identifiable as the right
  primitive AND still be unusable — overflowing text, gap-zero footers,
  invisible status text, raw-frame buttons. Recognition is necessary but
  insufficient. Run all seven checks before assigning a tier.

---

## Reference spokes

Load when relevant to the audit:

| Spoke | When to load |
|---|---|
| [`figma-source-audit-patterns.md`](../../08-knowledge/cross-domain/figma-source-audit-patterns.md) | Always — the recurring gaps + per-component recommendations live here. Read before starting any audit. |
| [`figma-component-composition-from-react.md`](../../08-knowledge/cross-domain/figma-component-composition-from-react.md) | When auditing the composition layer specifically (anatomy walker, render-prop, slot defaults). |
| [`figma-modes-for-variants/SKILL.md`](../figma-modes-for-variants/SKILL.md) | When auditing CVA components. Use this skill's decision rules for variant vs. mode. |
| [`design-engineer`](../../00-frameworks/00-README.md) | The dual-lens defaults — both Designer and Developer perspectives apply throughout. |
| [`figma-mcp-tool-usage/SKILL.md`](../figma-mcp-tool-usage/SKILL.md) | When you need the right MCP commands to inspect the file. |
| [`ds-advisor/SKILL.md`](../ds-advisor/SKILL.md) | For the strategic "what does this DS need?" question if the audit reveals system-level gaps. |

---

## What this skill replaces / complements

- **Replaces** the ad-hoc per-session audits we'd otherwise re-derive each time.
- **Complements** `figma-modes-for-variants` (which decides *how* to model
  variants) by deciding *whether and what* to model.
- **Complements** `design-engineer` (which is the always-on dual lens) by
  providing a focused review framework for source-driven generated libraries.
- **Does not** cover plugin generator bugs or implementation work — those
  follow from the audit's recommendations but live in different sessions.
