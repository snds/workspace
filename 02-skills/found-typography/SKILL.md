---
name: found-typography
description: >
  Context-free principles of typography — letterform anatomy, classification
  logic, modular scales and ratios, the measure/leading relationship, and type
  as the primary carrier of hierarchy. True for a book, a screen, a title card,
  a chart label. The root beneath gd-typography, uid-type-for-screens, and the
  type-design spokes. Triggers: typography, type hierarchy, type scale, leading,
  measure, letterform, typeface classification, modular scale.
aliases: [found-typography]
triggers: [typography, type hierarchy, type scale, leading, measure, letterform, typeface classification, modular scale, baseline, x-height]
tier: foundation
hub: design-foundations
domain: design
surfaces: ["*"]
spec_version: "2.0"
---

# Foundations — Typography

Principles of setting type that hold in any medium. Rendering specifics (hinting, optical sizing on
screens, CMYK black for print) are downstream; this is the shared craft.

## Letterform anatomy
The parts that govern rhythm and recognition: **x-height** (drives apparent size and texture),
**cap/ascender/descender**, **counter** (interior space — readability), **stroke contrast** (thick/thin),
**axis**. Two faces at the same point size can look wildly different sizes because x-height differs — size
type by appearance, not by number.

## Classification logic
Categories encode history and voice: **serif** (humanist → transitional → didone, increasing contrast),
**sans** (grotesque, neo-grotesque, humanist, geometric), **slab**, **script**, **display**. Pick by the
*structural* relationship you want (contrast, warmth, neutrality), not by surface mood alone.

## Scale + ratio
Hierarchy needs discrete, related sizes — a **modular scale** (a ratio like 1.2, 1.25, 1.333, or the
golden 1.618 applied repeatedly) gives sizes that feel kin. Too many sizes = no hierarchy; ~3–5 steps is
usually enough. Steps must be *distinct enough to read as levels*.

## Measure + leading
The three are coupled: **measure** (line length, ~45–75 characters for sustained reading), **leading**
(line spacing — grows with measure and size), **size**. Long measure + tight leading loses the line return;
short measure + loose leading fragments. Set them together, never independently.

## Type *is* hierarchy
Before color or layout, type weight/size/case/spacing carries most of the priority signal. Most
hierarchy problems are typographic problems first — see [[found-hierarchy]].

## Related
- hub → [[design-foundations]]
- peer ↔ [[found-hierarchy]] · [[found-composition]]
