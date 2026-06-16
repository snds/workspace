---
tags: [icon-font, variable-font, centricsymbols, figma, fonttools, design-system]
created: 2026-04-28
updated: 2026-04-28
status: stable
confidence: high
sources: [project-context 2026-04-28, session-state 14-variable-icon-font-generator]
related_skills: [variable-icon-font-architect]
related_projects: [14-variable-icon-font-generator]
---

# CentricSymbols Variable Icon Font — Accumulated Learnings

Architecture decisions, constraints, and hard-won details from building the CentricSymbols variable icon font pipeline. This is the working record of *why* things are the way they are — not a build guide (that's in the skill).

---

## What This Is

CentricSymbols is a variable icon font system for Centric's design system. It uses four variable axes to allow icons to shift weight, fill, grade, and optical size — similar to Google Material Symbols, but built from scratch for Centric's icon library.

**Current architecture version:** v0.3 pipeline spec  
**Delivery mechanism:** Hybrid Figma plugin + local FastAPI/PyInstaller server

---

## The Four Variable Axes

| Axis Tag | What It Controls | How It's Produced |
|----------|-----------------|-------------------|
| `wght` | Stroke weight (thin → bold) | Authored in Figma (default masters only); extremes derived algorithmically |
| `FILL` | Fill amount (outline → filled) | Authored; 0 = outline, 1 = filled |
| `GRAD` | Grade (subtle weight variation for context) | Derived algorithmically from `wght` masters |
| `opsz` | Optical size (icon tuned for small vs. large display) | Authored at standard optical sizes |

---

## Key Architectural Decisions

### Figma as Authoring Environment (Default Masters Only)
Figma handles authoring for the **default masters** only:
- `wght = 400` (Regular weight)
- `FILL = 0` (Outline)
- `opsz = 24` (Standard display size)

Weight extremes are **not drawn in Figma**. They're derived algorithmically via inner boundary offset. This is a significant constraint: designers author at one weight, the pipeline generates the weight variations. This means the algorithm must be trusted to produce correct interpolations — which requires the geometry to be interpolation-safe.

### Why Round Join Is Required
Variable font interpolation requires that path point topology is consistent between masters. Round joins produce clean, consistent geometry at variable weight extremes. Miter joins at sharp corners can cause unexpected geometry explosions during interpolation. **Round join is a hard constraint at the drawing level** — not a style choice.

### Stroke Rules
- **Closed paths:** Inside stroke
- **Open paths:** Center stroke

This keeps the stroke contained within the icon's visual bounding box on closed shapes, and centered (as expected) on open paths like lines and curves.

### COLRv1 for Per-Path Opacity
Some icons require per-path opacity variation — for example, a two-tone icon where one element is 40% opacity. COLRv1 font technology (injected via fonttools) enables this. This is not supported in older font formats.

### GRAD Axis: Derived, Not Authored
The GRAD axis is algorithmically derived from the `wght` masters. The specific derivation approach was an open decision as of the last CentricSymbols session — the decision on GRAD axis derivation approach is pending (captured in SESSION-STATE as a pending question).

---

## The Tool Pipeline

```
Figma (authoring) 
  → picosvg (SVG normalization)
  → fonttools + fontmake (variable font compilation)
  → defcon (UFO manipulation)
  → COLRv1 injection (fonttools)
  → Output: .ttf / .woff2 variable font
```

The Python environment uses `uv` for package management. Path confirmed at `/Users/sean.sands/.cache/uv/`.

---

## Delivery Architecture

The Figma plugin is one half of the system. The other half is a **local FastAPI server** packaged with PyInstaller. The server handles computationally intensive operations (font compilation, axis derivation) that can't run in the plugin sandbox. The plugin calls the server via localhost.

This is the v0.3 design. Earlier versions may have had different delivery patterns.

---

## What to Load When Resuming This Project

`variable-icon-font-architect` is the hub skill. It routes to 7 specialist spokes:
- Icon design (SVG authoring, conceptual design)
- Vector construction (path topology, interpolation-safe geometry)
- Pipeline engineering (fonttools, fontmake, build automation)
- 4 math spokes (geometry, interpolation, axis space, COLRv1 specifics)

The skill is also a spoke under `lead-type-designer` (it's a sub-hub — see the hub manifest).
