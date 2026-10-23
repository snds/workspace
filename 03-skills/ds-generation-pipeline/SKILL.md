---
name: ds-generation-pipeline
description: >
  Generating a design system's artifacts for a target stack, and the order of operations
  that keeps a generation run sound. Coordinates the framework spokes (fw-*) to produce
  tokens, component scaffolds, theme configuration, documentation structure and build
  config, and holds the generation manifest: the dependency graph, phase gates and
  validation checkpoints (variables → styles → utilities → components → documentation).
  Use when the user wants to generate a design system, scaffold DS artifacts for a stack
  (e.g. shadcn + Tailwind + Radix), produce framework-specific token files, create
  component shells with token binding, plan a multi-phase generation run, or produce
  cross-framework DS output. Figma-side generation mechanics → figma-ds-generation-pipeline.
pinned_date: "2026-03-26"
aliases: [ds-generation-pipeline, gen-manifest]
triggers: [generate a design system, scaffold ds artifacts, ds generation pipeline, gen manifest, generation manifest, design system for shadcn, scaffold ds components, set up tokens for, generation run, create ds from scratch]
governed_by: [qa]
related: [close-out, figma-ds-generation-pipeline, token-architecture]
spec_version: "2.0"
tier: spoke
domain: design
hub: ds
prerequisites: [ds]
---

# DS Generation Pipeline — Orchestrator Skill

## Purpose

This skill coordinates framework-specific spoke skills to generate complete design
system artifacts. It is the **generation** counterpart to `design-engineer` (which
is the **advisory/review** counterpart). Think of it as the assembly line; design-engineer
is the engineering review board.

> **Frost ban — do not generate a design system from scratch when one exists.**
> That is the same failure as adopting Material wholesale ([[18-design-systems-ai-operating-model]]).
> **Inspect, then extend.** If a published library / token graph / component package
> is in session or project context, this pipeline scaffolds *against it*. True
> greenfield (no system, no product yet) is rare — ask once, then proceed. Mortar,
> not a parallel universe. AI-ready generation still uses the three-tier token model
> and maps to existing components before minting new ones ([[ai-design-systems]]).

---

## Orchestration Flow

### Phase 0: Stack Selection

Determine the target framework combination. Common stacks:

| Stack | Primitives | Styling | Components | Docs |
|---|---|---|---|---|
| **shadcn stack** | Radix UI / Base UI | Tailwind CSS | shadcn/ui | Storybook |
| **Spectrum stack** | React Aria | CSS Modules / VE | Custom | Storybook |
| **Carbon stack** | Carbon React | Carbon Sass | Carbon | Carbon Storybook |
| **Lightning stack** | LWC | SLDS tokens | SLDS blueprints | SLDS docs |
| **Bootstrap stack** | Bootstrap JS | Bootstrap Sass | Bootstrap | — |
| **Web Components stack** | Lit | CSS variables | Custom elements | Storybook |
| **Multi-framework** | Web Components | CSS variables | Lit + wrappers | Storybook |
| **Vue stack** | Headless UI / Radix Vue | Tailwind CSS | Custom | Storybook |
| **Angular stack** | CDK | CSS variables | Custom | Storybook |
| **Svelte stack** | Melt UI / Bits UI | Tailwind CSS | Custom | Storybook |

### Phase 1: Version Check (all relevant spokes)

Before generating any artifacts, load and version-check every spoke skill in the
target stack. Each spoke has a `pinned_version` and `changelog_url` in its frontmatter.

```
For each spoke skill in the stack:
  1. Read the spoke's SKILL.md
  2. Execute its Version Check procedure
  3. Collect { name, pinned_version, latest_version, is_stale, breaking_changes }
  4. Report summary to user before proceeding
```

If any spoke is significantly stale (major version behind), warn the user and offer
to do a deep research pass on the breaking changes before generating.

### Phase 2: Token Generation

Generate design tokens in the target format. Token tiers follow the 3-tier model:

```
Tier 1: Primitives (raw values)
  ├── Colors (from fw-radix-colors or custom)
  ├── Spacing scale
  ├── Typography scale
  ├── Border radii
  ├── Shadows
  └── Motion (duration, easing)

Tier 2: Semantic (purpose-driven aliases)
  ├── Surface / background tokens
  ├── Interactive state tokens
  ├── Border tokens
  ├── Text tokens
  ├── Status tokens (success, warning, error, info)
  └── Focus / ring tokens

Tier 3: Component (scoped overrides — generated per component)
  └── Only when component-specific tokens diverge from semantics
```

#### Output format by stack

| Stack | Token format |
|---|---|
| **shadcn/Tailwind** | CSS custom properties in `@theme` block |
| **Carbon** | Sass variables + CSS custom properties |
| **Lightning** | SLDS token JSON + CSS custom properties |
| **Bootstrap** | Sass variables + CSS custom properties |
| **Vanilla Extract** | TypeScript theme contract |
| **Web Components** | CSS custom properties on `:root` |
| **DTCG export** | tokens.json (W3C DTCG format) |

### Phase 3: Component Scaffolding

Generate component shells with:
- Proper token binding (no hardcoded values)
- Variant structure matching the DS component taxonomy
- Accessibility attributes (from the headless layer)
- TypeScript types for props
- Basic story file for Storybook

Component classification follows the `design-engineer` taxonomy:

```
Primitive → Composite → Pattern → Template
```

### Phase 4: Theme Configuration

Generate the theme entry point for the target stack:

| Stack | Output |
|---|---|
| **shadcn** | `globals.css` with `:root` and `.dark` token blocks |
| **Tailwind** | CSS file with `@import "tailwindcss"` and `@theme` block |
| **Vanilla Extract** | `theme.css.ts` with `createThemeContract` + implementations |
| **Carbon** | Sass theme file with Carbon theme imports |
| **Bootstrap** | Sass variables file imported before Bootstrap |
| **Web Components** | Global CSS file with `:root` tokens |

### Phase 5: Documentation Structure

Generate documentation scaffolding:
- Component docs (anatomy, variants, states, usage guidelines)
- Token reference (all tiers with examples)
- Storybook configuration (if applicable)
- Getting started guide

### Phase 6: Validation

Run a validation pass:
- All token references resolve (no undefined variables)
- All components consume only semantic or component-tier tokens
- No hardcoded color/spacing/typography values
- Accessibility baseline (ARIA attributes, keyboard patterns)
- Dark mode rendering (if applicable)

---

## Spoke Skills (load on demand)

### Priority tier (load first, check for updates)

| Skill | Covers |
|---|---|
| `fw-shadcn` | shadcn/ui CLI, registry, theming, component customization |
| `fw-tailwind-css` | Tailwind v4 @theme, CSS-first config, utilities, dark mode |
| `fw-radix-colors` | 12-step color scales, dark mode pairing, custom generation |

### Framework layer

| Skill | Covers |
|---|---|
| `fw-radix-primitives` | Headless Radix components (Dialog, Popover, Tabs, etc.) |
| `fw-react-aria` | Adobe's accessibility-first hooks |
| `fw-vue` | Vue 3 Composition API patterns for DS components |
| `fw-angular` | Angular standalone components, signals for DS |
| `fw-svelte` | Svelte 5 runes and snippets for DS components |
| `fw-web-components` | Lit, Shadow DOM, custom elements |

### Styling layer

| Skill | Covers |
|---|---|
| `fw-css-modules` | CSS Modules + Vanilla Extract for zero-runtime CSS |

### Reference systems

| Skill | Covers |
|---|---|
| `fw-carbon` | IBM Carbon patterns, tokens, 2× grid |
| `fw-lightning` | Salesforce SLDS patterns, tokens, agentic UI |
| `fw-bootstrap` | Bootstrap Sass, utility API, grid |

### Documentation layer

| Skill | Covers |
|---|---|
| `fw-storybook` | Storybook CSF stories, addons, testing |

---

## Cross-Framework Generation

When generating for multiple frameworks simultaneously:

1. Generate tokens once (DTCG format as canonical source)
2. Transform tokens per target: `DTCG → Tailwind @theme`, `DTCG → Sass`, `DTCG → CSS`
3. Generate component shells per framework using parity mappings from each fw-* skill
4. Ensure behavioral contracts (keyboard nav, focus, ARIA) are identical across frameworks
5. Generate Storybook stories for each framework variant

---

## Figma Integration

When generating alongside Figma:
- Load `figma-ds-generation-pipeline` for the Figma-specific phases
  (Variable Collections → Styles → Canvas Components)
- Token names must align 1:1 between code and Figma variables
- Component property names map to React/Vue/Angular props

## Order of operations — the generation manifest

_Merged word for word from the former `gen-manifest` skill on 2026-10-22 (one generation spoke under `ds`; the original is archived in `_archive/2026-10-22-design-rearchitecture/gen-manifest.md`)._


Orchestrates the full design system generation pipeline. Every generation run
follows this manifest — no phase begins until its prerequisites are validated.

---

### Why This Exists

AI agents generating design system content fail predictably when they:
1. Create content that references prerequisites that don't exist yet
2. Miss opportunities to create reusable components before composing with them
3. Bind tokens/variables incorrectly because they lack inventory of what's available
4. Treat generation as a single pass instead of a phased, validated pipeline

This manifest encodes the dependency graph so the agent executes in the right
order and validates between phases.
---

### Dependency Graph

```
Phase 1: VARIABLES          (no dependencies)
  ↓
Phase 2: STYLES             (depends on: Phase 1 variables)
  ↓
Phase 3: UTILITIES          (depends on: Phase 1 variables, Phase 2 styles)
  ↓
Phase 4: COMPONENTS         (depends on: Phases 1–3)
  ↓
Phase 5: DOCUMENTATION      (depends on: Phases 1–4)
```

Each phase produces a **manifest inventory** — a structured record of every
asset created. Downstream phases consume this inventory to bind, reference,
and compose correctly.

---

### Phase Definitions

#### Phase 1 — Variables (`gen-variables`)

**Produces:** Variable collections, individual variables with values per mode.
**Inventory output:** List of all variables by collection, with name, type,
values per mode, and scoping metadata.

#### Phase 2 — Styles (`gen-styles`)

**Consumes:** Phase 1 variable inventory.
**Produces:** Composite styles (text, color, effect, grid) bound to variables.
**Inventory output:** List of all styles by type, with name, bound variables,
and composite property map.

#### Phase 3 — Utilities (`gen-utilities`)

**Consumes:** Phase 1 + 2 inventories.
**Produces:** Reusable supporting components — swatches, spacer elements,
icon containers, token visualization components, and any element that will
be instanced inside Phase 4 components.
**Inventory output:** List of all utility components with name, purpose,
accepted properties, and dependency references.

#### Phase 4 — Components (`gen-components`)

**Consumes:** Phase 1 + 2 + 3 inventories.
**Produces:** Design system components — primitives, composites, patterns.
**Inventory output:** List of all components with name, variant matrix,
properties, slot definitions, and utility/variable/style dependencies.

#### Phase 5 — Documentation (`gen-documentation`)

**Consumes:** Phase 1–4 inventories.
**Produces:** Token tables, usage examples, component anatomy pages,
swatch visualizations, getting-started guides.
**Inventory output:** List of all documentation pages with name and content type.

---

### Phase Gate Protocol

Before starting any phase N, run these checks:

#### Pre-flight checklist

1. **Inventory exists.** All prerequisite phase inventories are available
   and non-empty. If a prerequisite inventory is missing, stop and run
   that phase first.

2. **References resolve.** Spot-check that 3–5 items from the prerequisite
   inventory actually exist in the target environment (e.g., verify that
   named variables from Phase 1 are findable before Phase 2 tries to bind
   them).

3. **Scope is defined.** The generation scope for this phase is explicit:
   what collections, categories, or components are being generated in
   this run? Unbounded "generate everything" runs fail. Scope it.

#### Post-phase validation

After completing any phase, before proceeding to the next:

1. **Count check.** Expected item count matches actual created count.
   If there's a delta, investigate before continuing.

2. **Binding check.** For phases that bind to prerequisites (2, 3, 4):
   verify that bindings resolve. A style bound to a nonexistent variable
   is a silent failure that cascades downstream.

3. **Naming check.** All created assets follow the naming convention
   defined in the phase skill. No auto-generated names ("Frame 847",
   "Variable 12").

4. **Inventory update.** The phase inventory is written and available
   for downstream consumption.

---

### Manifest Inventory Format

Each phase produces an inventory in this structure. The format is
tool-agnostic — the adapter layer (see `references/figma-adapter.md`)
maps it to tool-specific identifiers.

```
## Phase [N] Inventory — [Phase Name]
Generated: [YYYY-MM-DD]
Scope: [what was generated in this run]
Count: [total items created]

### [Category]

| Name | Type | Dependencies | Notes |
|---|---|---|---|
| color.blue.500 | color | — | Primitive, no mode variants |
| color.background.primary | color | color.neutral.0 (Light), color.neutral.900 (Dark) | Semantic, 2 modes |
```

---

### Generation Scoping

Never run an unbounded generation. Every run targets a specific scope:

#### Scope levels

| Level | Example | When to use |
|---|---|---|
| **Full system** | "Generate the complete color token system" | Initial creation only |
| **Category** | "Generate all spacing variables" | Adding a new token category |
| **Component** | "Generate the Button component" | Adding a single component |
| **Incremental** | "Add 'Compact' mode to the spacing collection" | Extending existing content |

#### Scope declaration

Before starting generation, state the scope explicitly:
```
Scope: [level] — [specific target]
Phases required: [which phases this scope touches]
Prerequisites already met: [yes/no — which inventories exist]
```

---

### Error Recovery

When a phase fails mid-execution:

1. **Record what was created.** Partial inventory is better than none.
   Downstream phases need to know what exists even if the phase didn't
   complete.

2. **Do not retry the full phase.** Identify what failed, fix it, and
   continue from the failure point. Re-running an entire phase risks
   duplicating already-created assets.

3. **Roll back only if necessary.** If the partial output is structurally
   unsound (e.g., half a variable collection that will confuse mode
   resolution), remove the partial output and re-run. Otherwise, complete
   the phase incrementally.

---

### Tool Adapter

This manifest is tool-agnostic. The operations described in each phase
skill use generic terms (create variable, bind variable, create style,
create component). The adapter layer translates these to tool-specific
API calls.

**Active adapter:** `references/figma-adapter.md` — Figma MCP / Plugin API

When the target design tool changes, swap the adapter reference. Phase
skills remain unchanged — only the adapter is tool-specific.

Load the adapter when executing any phase. The adapter defines:
- How each generic operation maps to tool-specific API calls
- Tool-specific constraints and workarounds
- Tool-specific validation methods

---

### Reference Spokes

| Spoke | When to load |
|---|---|
| `references/figma-adapter.md` | When executing any generation phase against Figma. Maps generic operations to Figma MCP/Plugin API calls. |
| `gen-variables` skill | Phase 1 execution — variable/token generation |
| `gen-styles` skill | Phase 2 execution — style generation with variable bindings |
| `gen-utilities` skill | Phase 3 execution — utility component generation |
| `gen-components` skill | Phase 4 execution — design system component generation |
| `gen-documentation` skill | Phase 5 execution — documentation generation |

---

### Interaction with Other Skills

- **`design-engineer`** — Hub skill. The gen-manifest and all gen-* phase
  skills are spokes under design-engineer. Load design-engineer's references
  (especially `figma-authoring.md` and `token-architecture.md`) alongside
  the relevant phase skill.
- **`ds-advisor`** — Governs the *what* and *why* of design system decisions.
  Gen-manifest governs the *how* and *when* of generation execution. When
  making design decisions during generation (e.g., which token tiers to
  create, which component variants to include), defer to ds-advisor.
- **`figma-canvas-designer`** — Handles freeform Figma canvas work (screens,
  layouts, wireframes). Gen-* skills handle structured DS asset generation.
  Don't cross the streams — if the task is "design a settings page," use
  figma-canvas-designer. If the task is "generate the Button component for
  the design system," use gen-manifest + gen-components.

## Related
- hub → [[ds]]
- governed-by → [[qa]]
- peer ↔ [[ai-design-systems]]
