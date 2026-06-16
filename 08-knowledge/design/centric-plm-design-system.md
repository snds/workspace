---
tags: [design-system, centric, plm, tokens, components, data-tables, ark-ui]
created: 2026-04-28
updated: 2026-04-28
status: stable
confidence: high
sources: [project-context 2026-04-28, session-state 02-centricPLM, role-and-context]
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

## What Loads When Working on This Project

- Strategic/governance work → `ds-advisor`
- Component authoring and code-level → `design-engineer`
- Dojo/dgrid legacy → `fw-dojo`
- TanStack Table implementation → `fe-data-visualization`
- Framework 02 (UX Operational) + Framework 05 (Last-Mile Craft) for component spec work
