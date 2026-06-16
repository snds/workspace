---
name: gen-manifest
description: >
  Orchestration manifest for design system generation. Defines the dependency
  graph, phase gates, and validation checkpoints for generating a complete
  design system — tokens through documentation. Use this skill whenever
  generating design system content that spans multiple phases (variables,
  styles, components, documentation) or when planning a generation run.
  This is the "order of operations" skill — it prevents the agent from
  generating content that depends on prerequisites that don't exist yet.
  Trigger on: "generate design system", "generation pipeline", "run
  generation", "create DS from scratch", or any multi-phase DS creation task.
  Always load this skill before any individual gen-* phase skill.
aliases: [gen-manifest]
spec_version: "2.0"
---

# Generation Manifest

Orchestrates the full design system generation pipeline. Every generation run
follows this manifest — no phase begins until its prerequisites are validated.

---

## Why This Exists

AI agents generating design system content fail predictably when they:
1. Create content that references prerequisites that don't exist yet
2. Miss opportunities to create reusable components before composing with them
3. Bind tokens/variables incorrectly because they lack inventory of what's available
4. Treat generation as a single pass instead of a phased, validated pipeline

This manifest encodes the dependency graph so the agent executes in the right
order and validates between phases.
---

## Dependency Graph

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

## Phase Definitions

### Phase 1 — Variables (`gen-variables`)

**Produces:** Variable collections, individual variables with values per mode.
**Inventory output:** List of all variables by collection, with name, type,
values per mode, and scoping metadata.

### Phase 2 — Styles (`gen-styles`)

**Consumes:** Phase 1 variable inventory.
**Produces:** Composite styles (text, color, effect, grid) bound to variables.
**Inventory output:** List of all styles by type, with name, bound variables,
and composite property map.

### Phase 3 — Utilities (`gen-utilities`)

**Consumes:** Phase 1 + 2 inventories.
**Produces:** Reusable supporting components — swatches, spacer elements,
icon containers, token visualization components, and any element that will
be instanced inside Phase 4 components.
**Inventory output:** List of all utility components with name, purpose,
accepted properties, and dependency references.

### Phase 4 — Components (`gen-components`)

**Consumes:** Phase 1 + 2 + 3 inventories.
**Produces:** Design system components — primitives, composites, patterns.
**Inventory output:** List of all components with name, variant matrix,
properties, slot definitions, and utility/variable/style dependencies.

### Phase 5 — Documentation (`gen-documentation`)

**Consumes:** Phase 1–4 inventories.
**Produces:** Token tables, usage examples, component anatomy pages,
swatch visualizations, getting-started guides.
**Inventory output:** List of all documentation pages with name and content type.

---

## Phase Gate Protocol

Before starting any phase N, run these checks:

### Pre-flight checklist

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

### Post-phase validation

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

## Manifest Inventory Format

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

## Generation Scoping

Never run an unbounded generation. Every run targets a specific scope:

### Scope levels

| Level | Example | When to use |
|---|---|---|
| **Full system** | "Generate the complete color token system" | Initial creation only |
| **Category** | "Generate all spacing variables" | Adding a new token category |
| **Component** | "Generate the Button component" | Adding a single component |
| **Incremental** | "Add 'Compact' mode to the spacing collection" | Extending existing content |

### Scope declaration

Before starting generation, state the scope explicitly:
```
Scope: [level] — [specific target]
Phases required: [which phases this scope touches]
Prerequisites already met: [yes/no — which inventories exist]
```

---

## Error Recovery

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

## Tool Adapter

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

## Reference Spokes

| Spoke | When to load |
|---|---|
| `references/figma-adapter.md` | When executing any generation phase against Figma. Maps generic operations to Figma MCP/Plugin API calls. |
| `gen-variables` skill | Phase 1 execution — variable/token generation |
| `gen-styles` skill | Phase 2 execution — style generation with variable bindings |
| `gen-utilities` skill | Phase 3 execution — utility component generation |
| `gen-components` skill | Phase 4 execution — design system component generation |
| `gen-documentation` skill | Phase 5 execution — documentation generation |

---

## Interaction with Other Skills

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
