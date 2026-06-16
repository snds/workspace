---
name: omni-project
description: >
  Persistent project context for the Omni design-to-production platform. Load this
  skill whenever working on any aspect of Omni — the canvas editor, computational
  design system, headless component library, IDE/CLI, visual logic builder, IR data
  model, token architecture, or any planning/UX/engineering work related to the Omni
  ecosystem. Also trigger when the user mentions "Omni", "seed product", "canvas
  editor", "visual logic builder", "headless components", "intermediate representation",
  or discusses building a design tool, framework-agnostic component system, or
  computational design system. This skill ensures every decision considers the full
  ecosystem intent — it should load alongside workspace-bootstrap at session start
  for any Omni-related work.
aliases: [omni-project]
spec_version: "2.0"
---

# Omni Project Context

This skill is the single source of truth for the Omni platform vision, architectural
decisions, and module boundaries. It exists so that no session ever loses sight of the
long-tail intent: Omni is an ecosystem of interconnected surfaces, not a single tool.

Every engineering and design decision made in any session should be evaluated against
the ecosystem context captured here. If a decision serves the immediate module but
undermines the broader platform, flag it.

---

## The Vision

Omni is a design-to-production platform. Sean's own words:
> 1. By which to begin a brand new interactive digital experience regardless of the
>    type of experience
> 2. That gets implementation of the front-end out of the way of creating the experience
> 3. Which offers an accelerated path to getting any project off the ground
> 4. Lets developers/engineers focus on the broader systemic issues
> 5. Offers designers a way to have a steady and reliable set of defaults

The platform is **agentic-system agnostic** — Omni is the substrate, agents bring
intelligence. Claude is the current testing method, not a hard dependency. Each module
could be sold as an independent product/service.

---

## The Five Surfaces

Omni comprises five core surfaces. Each is a product-grade module that also participates
in the broader ecosystem through the shared Intermediate Representation (IR).

### 1. Headless Component Library
- Framework-agnostic, accessible-by-default primitives
- Surface/context-aware (the component knows where it lives)
- Output targets: Vue, React, React Native, Angular, Web Components
- The foundational layer — all other surfaces consume or reference these components

### 2. Computational Design System
- Algorithmically generated tokens (color, typography, spacing, motion, elevation)
- OKLCH color space with perceptual math, gamut clamping, APCA contrast
- Three-tier token architecture: global → semantic → component
- Surface context model: 7 surface types, emphasis modes, nesting/inheritance
- This is the "brain" — the system that makes design decisions computationally
### 3. IDE + CLI
- Developer-facing authoring environment
- Direct manipulation of the IR, components, and token system
- Code-first workflow that complements the canvas tool
- Extension/plugin architecture for custom workflows

### 4. Canvas Editor (SEED PRODUCT)
- Visual editor for designing interactive experiences
- Closer to Webflow than Figma — this is NOT a drawing tool
- Supports: flows, states, breakpoint views, platform-specific views
- Designer-first experience, but engineers can use it too
- Outputs production-ready code through the IR → framework pipeline

### 5. Visual Logic Builder
- Node-based interaction and logic authoring
- Single module, two persona treatments:
  - **Designers**: simplified, visual-first, focused on interactions and states
  - **Engineers**: full access, scripting hooks, system-level logic
- Bridges the gap between "what it looks like" and "how it behaves"

---

## Architectural Pillars

### Intermediate Representation (IR)
The IR is the central data model that all five surfaces read and write. It is the
single source of truth for any Omni project. Key requirements:

- Framework-agnostic (similar to Mitosis/Radix approach)
- Serializable, diffable, version-controllable