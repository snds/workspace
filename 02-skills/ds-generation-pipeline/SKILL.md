---
name: ds-generation-pipeline
description: >
  Orchestrator for generating complete design system artifacts targeting a specific
  framework stack. Coordinates framework-specific spoke skills to produce tokens,
  component scaffolds, theme configuration, documentation structure, and build
  pipeline config for any combination of supported frameworks. Use this skill
  whenever the user wants to generate a new design system, scaffold DS artifacts
  for a target stack (e.g., shadcn + Tailwind + Radix), produce framework-specific
  token files, create component shells with proper token binding, or set up the
  full DS toolchain for a project. Also trigger when the user says "generate a
  design system", "scaffold DS components", "set up tokens for [framework]", or
  asks for cross-framework DS output. This is the meta-skill that coordinates
  all fw-* spoke skills — load it when the task is generation, not advisory.
pinned_date: "2026-03-26"
---

# DS Generation Pipeline — Orchestrator Skill

## Purpose

This skill coordinates framework-specific spoke skills to generate complete design
system artifacts. It is the **generation** counterpart to `design-engineer` (which
is the **advisory/review** counterpart). Think of it as the assembly line; design-engineer
is the engineering review board.

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
