---
tags: [design-system, centric, plm, tokens, components, data-tables, ark-ui]
created: 2026-04-28
updated: 2026-07-31
status: stable
confidence: high
sources: [project-context 2026-04-28, session-state 02-centricPLM, role-and-context, session 2026-07-31-work-figma-density]
related_skills: [ds-advisor, design-engineer, fe-component-architecture, fw-dojo]
related_projects: [02-centricPLM]
---

# Centric PLM Design System — Accumulated Learnings

What we know about the Centric PLM design system from actual work: the scale, the constraints, the decisions made, and the strategic direction. Not a how-to — a working record of what's true.

---

## The Scale of the Problem

- **90 unique data tables** across **94 pages** of the PLM application (Phase 2 audit)
- **Primary interface paradigm:** Data tables, grids, forms, and dashboards — high-density data workflows dominate
- **User population:** Fashion designers, product designers, food scientists, merchandisers, executives, supply chain teams — wildly different mental models and task types, but all power users
- **Verticals served:** Fashion & apparel (primary), Food & beverage, General product (electronics, consumer goods)
- **Multi-framework reality:** Vue (primary production framework), React, React Native, Angular all in the codebase — single DS must serve all four

---

## The Legacy Technology Problem

The frontend is a dual-era codebase:
- **Legacy:** Dojo Toolkit SPA (dgrid for data tables, Dijit widgets, AMD module loading)
- **Modern:** React + TypeScript + MobX

The data table work specifically involves migrating away from Dojo's `dgrid` toward TanStack Table. These are architecturally different paradigms — dgrid is widget-based and imperative; TanStack Table is headless and composable. This isn't a component swap; it's a mental model shift.

**What this means for DS work:** Component specs written for the modern stack can't assume Dojo compatibility. The migration path is the DS's job to illuminate — components need to be specced at a behavior level (what it does) before they're tied to a framework.

---

## Strategic Decision: Ark UI as Headless Foundation

**Decision:** Recommend Ark UI as the headless component library foundation for cross-framework parity.

**Rationale:**
- Supports Vue, React, and Solid (React Native handled separately)
- Headless = no styling opinions, full DS token control
- ARIA patterns are built-in and WAI-ARIA compliant
- Reduces the maintenance burden of maintaining separate ARIA implementations per framework

**Status as of last session:** Recommended, not yet formally adopted. The recommendation is in the project context but hasn't been acted on in a live session.

---

## Token Architecture

**Three-tier token system:**
1. **Global tokens** — raw values (hex colors, pixel values, font names)
2. **Semantic tokens** — named by intent (surface.default, text.primary, border.subtle)
3. **Component tokens** — scoped to specific components (button.label.color.default)

**Pipeline:** Figma Variables → Style Dictionary (or equivalent) → framework-specific outputs

**Active challenge:** Token migration between Figma DS versions. When the DS version updates, mappings between old and new token names must be maintained. This has been a manual process and is a known pain point.

---

## Data Table Documentation Work

- **Current state:** Cell design documentation is the active work thread. Text cells and numeric cells are first.
- **Design scope:** Interactive states, inline editing, component specs for the data table cell anatomy
- **Technical reference:** TanStack Table is the modern target, dgrid/Dojo is the legacy context
- **The canonical reference:** `http://design-dev.centricsoftware.com` (Storybook — internal, DNS-gated). Not accessible outside Centric network.

**Key insight from the audit:** The sheer volume (90+ tables) means cell-level consistency is the highest-leverage DS investment. A well-specified cell type can propagate across all 90 tables. A poorly specified one multiplies the inconsistency at scale.

---

## Cross-Framework DS Strategy

**The core challenge:** One design system, four framework implementations that must stay in parity.

**Current approach:** Vue is primary. React and Angular are adapters. React Native is handled separately.

**What "parity" means in practice:**
- Same token values across all frameworks (Style Dictionary handles this)
- Same component API surface (same prop names, variant names, state names)
- Same behavior (interaction patterns, ARIA semantics, keyboard navigation)
- NOT necessarily the same implementation — the internals can be framework-idiomatic

---

## Active Figma Files

| Purpose | File Key |
|---------|---------|
| Core Design System | `sgsaBIZBVNjuoBDTwqZlhd` |
| Components | `pyYokK7ajFtPgeQAKfjIZd` |
| Research FigJam | `RWJnQG5MLStvN7JfEllnWZ` |
| Visual Research Board | `PuCufvvSxifLafOxHwQeMp` |

**Organization plan key:** `organization::849699634926501221`

---

## Density as a Semantic Variable-Mode System (Figma library, 2026-07-31)

Learned building the `Centric SaaS PLM - Design System` Figma library (file `o6o1ZuGHxDow2vHLuYXT6X` —
a distinct, newer library from the files listed above). This is the reusable pattern, not a one-off.

**Density belongs in the semantic layer as its own mode-set collection — not baked per component.**
- `Foundations / Semantics / Density` with modes **Normal (default) / Compact / Spacious**. Tokens:
  `control-height/*`, `padding-x/*`, `padding-y/*`, `gap/*`, `control-radius/*`, `container/*`,
  `icon-size/*` (xs/sm/md/lg — Material Symbol **fontSize** is the real lever; see
  `density-vertical-rhythm-audit.md`), `avatar-size/*` (sm/md/lg diameter; `Avatar / Size`.`size`
  aliases these so Size × Density compose). Per-instance icon size uses collection **`Icon / Size`**
  (modes default/xs/sm/lg/control) — masters bind `fontSize` → `size`; instances set an explicit mode.
  Nested swappable icons on parents must use **`INSTANCE_SWAP` props** (not bare nested swaps) —
  otherwise `resetOverrides` wipes icon identity. Icon-only controls: Button + `Button / Layout` =
  `icon-only` (not a separate Icon Button component).
- Each density token **aliases an existing Spacing/Radii semantic variable per mode** (never a raw
  number). Pin **Normal to the current values** so the refactor is value-identical — zero visual drift
  is what makes it safe to apply to a near-publish library.
- **Two composable axes.** A component's own `Size` variant (xs/sm/md/lg) and the ambient Density mode
  are independent. Re-point the component `Size` collections (Button/Select height+radius) *at* the
  density tokens so Size and Density multiply instead of fighting.

**Applying it without breaking instances:**
- Rebind structural props (heights, radii, vertical padding, gaps, container insets) to density tokens
  on **non-instance nodes only** (walk up the parent chain; skip anything inside an `INSTANCE`) — masters
  change, instances inherit. Match by *resolved px* → density token so Normal stays put.
- Breathe **container insets (16/24) on all sides**, but keep **control horizontal padding (8/10/12) fixed** —
  fluid horizontal control padding reads as sloppy; vertical rhythm + container breathing carries density.
- Keep Density and Colors on **Auto** for component masters, subcomponents, and nested instances.
  Set the collection defaults to **Normal** and **Light** for uncontextualized library previews; set an
  explicit context mode only on an app/chrome, page, feature, or audit shell. Nested components must
  inherit that shell so one Compact/Dark decision propagates through the whole composition. Use
  `clearExplicitVariableModeForCollection` to remove accidental context pins. Component-scoped axes
  (Size, Variant, State, Calendar position) remain explicit where the component API requires them.

**Collection hygiene that generalized:**
- An **alias-only intermediate collection is dead weight.** A "Typography Roles" layer whose every
  variable was a 1:1 alias into semantic Typography added a hop and bought nothing — text styles were
  bound to Roles, Roles pointed at semantics. Fix: rebind each style field *directly* to the semantic
  token the role aliased, verify no other node references the layer, then delete it. (21 styles ×
  6 fields = 126 rebinds; collection removed clean.)
- **Naming:** normalize collection names to spaced `Component / Axis` (` — ` → ` / `), singular axis
  words (`Sizes` → `Size`). Renaming collections/variables is **id-safe** (bindings are by id).
- **Semantic scale names use slash groups** (done 2026-07-31, before any Style Dictionary export):
  `font-size/4xl`, `space/4`, `radius/md`, `border-width/1` — Figma folders by type; Style Dictionary
  can map `/` → nested JSON (`fontSize.4xl`) or CSS vars (`--font-size-4xl`) without a rename pass.
  Same pattern already used by Density (`control-height/md`).
- **Semantic colors** (2026-07-31): category folders for intent —
  `surface/*`, `action/*`, `status/*`, `chrome/*`, `sidebar/*` (54 tokens). Examples:
  `action/primary/foreground`, `status/destructive/soft/foreground`, `chrome/border/subtle`.
  Style Dictionary should strip the category prefix for shadcn CSS parity
  (`action/primary` → `--primary`) or emit nested CSS vars — pick one mapping rule and stick to it.
- **CDS bridge removed** (same session): 42 `cds/{hue}/{step}` tokens deleted from Figma after
  cataloging Light/Dark → Radix maps. Zero Figma consumers. Catalog for the centric-ui migration:
  [[cds-to-radix-color-map]]. Do not recreate CDS steps in Figma; migrate code to intent tokens.
- **Instance vs context token method** (same session): [[figma-component-token-axes]] —
  Density/Color = shell context; Size/Variant = instance; compose via aliases. Pilot:
  `control-font-size/*` + `Sidebar / Surface`.

## What Loads When Working on This Project

- Strategic/governance work → `ds-advisor`
- Component authoring and code-level → `design-engineer`
- Dojo/dgrid legacy → `fw-dojo`
- TanStack Table implementation → `fe-data-visualization`
- Framework 02 (UX Operational) + Framework 05 (Last-Mile Craft) for component spec work
- **Component *contracts*** (a table/component being replaced, or two implementations disagreeing) →
  [[component-contracts-and-schemas]] (the seven gates + the investment gate) +
  [[component-contract-schema]] (the portable model) + framework #09 §5a. A replacement is the
  cheapest moment to buy a contract, because the contract *is* the definition of "equivalent."
