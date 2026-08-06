---
title: Figma shadow modes (CDS drop)
status: living
updated: 2026-08-05
figma_file: o6o1ZuGHxDow2vHLuYXT6X
related: [token-spec-page, density-radius-xxs-alignment, cross-surface-token-parity]
---

# Figma shadow modes — single style, elevation modes

Code SSOT: centric-ui `app/app.css` `--shadow-cds-drop-{1,2,3}` (light + dark opacities).

## Structure

| Layer | Collection | Modes | Variables |
|---|---|---|---|
| Elevation geometry + color pick | `Foundations / Semantics / Shadows` | **Drop 1 / Drop 2 / Drop 3** | `shadow/offset-x`, `offset-y`, `blur`, `spread`, `color` |
| Theme opacity | `Foundations / Semantics / Colors` | **Light / Dark** | `shadow/drop-1`, `drop-2`, `drop-3` → alias `Color/Overlay/Black/{15,10,15}` light / `{40,30,40}` dark |

**Effect style:** one style `shadow/cds-drop`. All DROP_SHADOW fields (`offsetX/Y`, `radius`, `spread`, `color`) bind to the Shadows collection vars via `setBoundVariableForEffect`. Switching the Shadows mode on a frame changes elevation; Colors Light/Dark flips opacity through the `shadow/color` → `shadow/drop-*` alias chain.

## Values (Drop 1 / 2 / 3)

| | offset | blur | spread | light α | dark α |
|---|---|---|---|---|---|
| Drop 1 | 0, 1 | 3 | 0 | 15% | 40% |
| Drop 2 | 0, 2 | 4 | 0 | 10% | 30% |
| Drop 3 | 0, 3 | 6 | 0 | 15% | 40% |

## API note

A **single** mode-driven effect style **works**. Figma has no composite “shadow” variable type, but binding each effect field to FLOAT/COLOR variables is enough: one style + collection modes replaces three separate styles. Separate `shadow/cds-drop-1|2|3` styles are unnecessary unless a consumer cannot set variable modes.
