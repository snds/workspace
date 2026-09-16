---
tags: [design-system, figma, tokens, density, component-tokens, modes]
created: 2026-07-31
updated: 2026-09-16
status: stable
confidence: high
sources: [session 2026-07-31-work-figma-density, Figma o6o1ZuGHxDow2vHLuYXT6X]
related_skills: [ds-advisor, design-engineer, figma-ds-surface-authoring]
related_projects: [centric-ui]
---

# Figma DS — instance vs context component tokens

Authoring method for the Centric SaaS PLM Figma library so designers are not asked to
stack Density + Size + Variant + theme modes on every instance.

## Rule of thumb

> **If flipping it should change a whole view, it is context.  
> If flipping it should change one control, it is instance.**

| Kind | Examples | Who sets it | Mechanism |
|------|----------|-------------|-----------|
| **Context** | Density (Compact/Normal/Spacious), Color (Light/Dark) | App shell / page / feature frame | Collection mode on an **ancestor**; children inherit |
| **Instance** | Size, Variant, Position, State | Each component instance | Component **variant property** (preferred) + optional component-scoped variable collection |

## Layers (alias down, never sideways)

```
Context modes     →  set once on shell (Density, Colors)
Instance axes     →  component properties (+ component var collection when values differ by mode)
Component vars    →  alias semantics (including density tokens)
Semantics         →  alias primitives
Primitives        →  raw scales (always present; unused steps are capacity)
```

**Compose in the alias graph, not in the designer’s mode picker.**  
Example: `Button / Size` `height` aliases `control-height/*` (Density). Choosing Size=sm
already picks a density-aware height — the designer does **not** also set Density on the Button.

Same pattern for type: text styles bind to **`type-size/*` + `type-leading/*` + `type-paragraph/*`**
(Density). Size-varying controls (Button/Avatar) bind `fontSize`/`lineHeight` to Size-collection
vars that alias those same density rungs — Size picks the rung, Density scales it. UI text styles
used in product chrome breathe with shell Density automatically.

## What not to do

- **Do not** invent composite modes like `compact-sm` / `spacious-lg`. Mode count explodes;
  global “make this table compact” breaks; code keeps `data-density` and `size` separate anyway.
- **Do not** pin Density or Color on component roots. Leave context collections on **Auto** so
  app/chrome, page, feature, and audit shells can control the whole composition. Collection defaults
  (Normal / Light) provide the standalone library baseline. Keep only true component axes such as
  Size, Variant, State, and Position explicit on component roots or instances.
- **Do not** leave domain semantics (`sidebar/*`) only as loose Variables-panel tokens.
  Expose them through a **component collection** (`Sidebar / Surface`, `Sidebar / Menu Button`)
  so the instance API is the component, not raw semantics.

## Component collection recipe

1. Name: `Component / Axis` (e.g. `Button / Size`, `Calendar / Radii`, `Toggle Group / Item`, `Sidebar / Surface`).
2. Modes = the **instance** axis only (or a single `Value` mode when the shell has one appearance).
3. Variable names = short property paths (`height`, `fontSize`, `Day/top-left`, `Item/top-left`, `background`).
4. Every mode value **aliases** a semantic or density token — no raw numbers when a scale exists.
5. Bind component masters to the component vars (not past them to semantics), so the Size/State
   mode pin actually drives the node.
6. **WEB syntax on a Color collection is the semantic CSS variable**, not a new `--component-*`
   custom property. Code stays on Tailwind semantic utilities (`bg-primary-soft`). MATCH is
   “same `--sem-*` published on both surfaces.”
7. Rebinding a main component does **not** clear nested-instance paint overrides. Walk those
   instances too, or they stay pinned to `Color/*` primitives.

Subcomponent folders inside a collection are fine when one chrome owns several parts
(`Calendar / Radii` → `Day/*`; later `Header/*`).

## Capacity vs orphans

| Keep as capacity (“there when needed”) | Actionable |
|------------------------------------------|------------|
| Full primitive scales | Component vars that exist but nothing binds |
| Unused semantic scale steps (`space/96`, `radius/4xl`) | Semantics that should be behind a component API but aren’t |
| Density tokens not yet applied to a surface | |

Density tokens and large spacing steps are **capacity**, same philosophy as primitives.

## Worked example — Sidebar (pilot)

| Semantic | Component token | Bound on |
|----------|-----------------|----------|
| `sidebar` | `Sidebar / Surface` `background` | `Sidebar` fill |
| `sidebar/border` | `Sidebar / Surface` `border` | `Sidebar` stroke |
| `sidebar/foreground` | (via Menu Button + labels) | menu / group text |
| `sidebar/accent` (+ `/foreground`) | `Sidebar / Menu Button` | Hover |
| `sidebar/selected` (+ `/foreground`) | `Sidebar / Menu Button` | Selected |
| `sidebar/primary` (+ `/foreground`) | `Sidebar / Surface` `primary` | capacity / future CTA |
| `sidebar/ring` | `Sidebar / Surface` `ring` | Menu Button Focus ring |

Designers interact with **Sidebar** and **Menu Button** state — not Density + sidebar semantics
as separate mode chores.

## Worked example — control type × density

| Size mode | Component var | Density token (Normal) | Compact / Spacious |
|-----------|---------------|------------------------|--------------------|
| Button xs | `fontSize` | `control-font-size/xs` → 12 | 12 / 14 |
| Button default | `fontSize` | `control-font-size/md` → 14 | 12 / 16 |
| Avatar sm/md/lg | `fontSize` | xs / md / lg rungs | step ±1 on the type scale |

Text nodes bind to **`Button / Size` `fontSize`** (etc.), not straight to `font-size/sm`,
so Size mode and Density mode both participate.

**Gotcha (verified 2026-09-16 on Button):** a Text Style that binds `fontSize` dual-binds
alongside `Button / Size`.`fontSize`, then *wins*. Clearing the style drops the Size bind
and leaves the style’s `type-size/*` token — xs/sm/lg no longer scale. Do not apply
`textStyleId` on a node whose type size is a component Size mode. Bind family / weight /
leading / letter-spacing individually; let the Size var own `fontSize`. Physical Size
*variants* (a Compact component vs a Field component) may each have a matching style.
Doctrine: [[figma-ds-surface-authoring]] rule 21.

## Checklist for a new component axis

- [ ] Is this context or instance?
- [ ] If instance: variant property first; variable collection only if values must mode-resolve
- [ ] Alias into semantics/density — no parallel raw ladders
- [ ] Bind masters to component vars; leave Density/Colors Auto; set context on the shell
- [ ] Document any semantic tokens held as capacity until a surface exists

## Related

- [[centric-plm-design-system]] — density system + semantic naming
- [[figma-ds-surface-authoring]] — surface/overlay construction rules
- [[figma-variable-state-representation]] — modes as a vertical slice; CVA→Figma
- [[cds-to-radix-color-map]] — retired CDS bridge (code migration only)
