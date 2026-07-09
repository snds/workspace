---
name: variable-icon-font-architect
description: >
  Precision vector design, parametric variation, and interpolation-safe geometry.
  Spoke within `lead-type-designer` and sub-hub for a network of 10 specialist
  spokes covering icon design, vector construction, pipeline engineering, and
  applied mathematics. Use this skill whenever the conversation touches: variable
  font construction, icon font interpolation, point compatibility, master setup
  (Thin/Bold/Outlined/Filled), FILL/wght/GRAD/opsz axis mechanics, destructive
  conversion (Outline Stroke → Flatten Booleans → Path Cleanup), exploding glyphs,
  node parity debugging, skeleton-and-meat strategy, FontTools scripting,
  Glyphs/FontLab import prep, or any variable icon font pipeline work. Also
  trigger on "icon font", "variable axes", "interpolation", "node map",
  "path direction", "glyph construction", or any reference to building or
  debugging variable icon font masters.
hub: lead-type-designer
aliases: [variable-icon-font-architect]
triggers: [variable axis, variable axes]
spec_version: "2.0"
tier: hub
domain: design
---

# Variable Icon Font Architect

**Spoke within `lead-type-designer`** · **Sub-hub** for the icon font skill
network. Routes to 10 specialist spoke skills based on topic. This skill
provides the interpolation physics and axis
mechanics foundation; spokes provide domain-specific depth.

---

## Spoke Network — Load On-Demand

This hub routes to 10 specialist spoke skills. **Do not load all spokes
eagerly.** Load only the 1–2 spokes relevant to the current question.
The hub itself contains enough context to triage and route — spokes
provide the deep domain knowledge when needed.

### Spoke Manifest

| Skill | Domain | Trigger When |
|-------|--------|-------------|
| `lead-icon-artist` | Icon design language, visual semantics, optical correction, metaphor, keyline grids, naming taxonomy | Designing new icons, evaluating icon quality, specifying FILL/opsz behavior, visual weight audits |
| `lead-vector-designer` | Path construction craft, bezier mechanics, node placement, boolean hygiene, stroke-to-outline, SVG path data | Drawing icons in Figma, pen tool technique, node count issues, flatten/outline workflow |
| `lead-technical-digital-artist` | Font pipeline engineering, FontTools, coordinate transforms, GSUB/COLRv1, build automation, WOFF2 delivery | Building/debugging the font compilation pipeline, SVG→font conversion, designspace config |
| `math-bezier-spline-theory` | Parametric curve math, de Casteljau, curvature, inflection, offset curves, circle approximation, curve fitting | Node placement math, curve quality analysis, offset curve artifacts, node reduction algorithms |
| `math-computational-geometry` | Boolean operations, winding numbers, Minkowski sum, medial axis, topological validation, shape distance | Boolean cleanup issues, path direction debugging, stroke expansion math, weight derivation from skeleton |
| `math-optical-optimization` | Perceptual models (Weber-Fechner, Stevens), overshoot formulas, stroke weight compensation, APCA contrast, smoothness energy | Optical corrections, weight perception, counter legibility, visual center-of-mass, opsz simplification thresholds |
| `math-interpolation-designspace` | Multilinear interpolation, delta algebra, avar remapping, master placement optimization, compatibility, extrapolation | Variable font axis behavior, master budget decisions, interpolation artifacts, perceptual uniformity across axes |
| `opentype-layout-engineering` | GSUB/GPOS table construction, .fea syntax, liga vs calt behavior, rvrn, named lookups, shaping engine mechanics | Ligature substitution, feature code, why liga/calt fires or doesn't, .fea debugging, GSUB table structure |
| `fonttools-ufo-internals` | UFO package structure, defcon/ufoLib2 APIs, fontmake compilation pipeline, gvar delta computation, table inspection | Python build pipeline bugs, features.fea not written, GSUB missing after compile, gvar corruption, TTFont inspection |
| `font-qa-validation` | fontbakery check triage, OS/2 table, name table, STAT table, variable font requirements, pipeline validation errors | fontbakery failures, 442 validation errors, FAIL/WARN interpretation, font quality checklist before shipping |

### Spoke Loading Protocol

**Step 1**: Read the user's question and match against the Spoke Manifest
table above. Identify the 1–2 spokes (rarely 3) that are directly relevant.

Common routing patterns:

- **Designing a new icon**: `lead-icon-artist` (+ `lead-vector-designer` if construction details needed)
- **Debugging interpolation**: `math-interpolation-designspace`
- **Pipeline/compilation issues**: `lead-technical-digital-artist` + `fonttools-ufo-internals`
- **Optical correction**: `math-optical-optimization`
- **Path construction in Figma**: `lead-vector-designer`
- **Ligatures / GSUB not working**: `opentype-layout-engineering` + `fonttools-ufo-internals`
- **Font quality / fontbakery failures**: `font-qa-validation`
- **Full build review**: load spokes incrementally as each aspect is addressed

**Step 2**: Load the identified spoke(s) from the workspace checkout:
```
03-skills/[skill-name]/SKILL.md
```

**Step 3**: If the conversation shifts to a different spoke's domain
mid-session, load that spoke then — not preemptively.

**Never load all 7 spokes at once.** The full network is ~120k tokens.
A typical icon font question needs 1–2 spokes (10–30k tokens).

---

## This Skill Is Project-Agnostic

This hub and its spokes apply to **any** icon font or variable font work —
not just CentricSymbols. When triggered by icon/font/vector topics in any
project context (Omni, freelance, exploratory), load this network. Do not
route icon font topics to project-specific skills like `omni-project` or
`legion-project` unless the question is genuinely about that project's
non-font systems.

---

## Core Knowledge (Hub-Level)

### Interpolation Physics — Point Compatibility

Variable fonts interpolate between masters. Every master must have:

- **Identical node count** per glyph
- **Identical path direction** (CW/CCW) across masters
- **Identical start-point index** per contour
- **Identical path order** (contour sequence)

Violation causes **exploding glyphs**. Route to `math-interpolation-designspace`
for the formal algebra; route to `lead-vector-designer` for the Figma fix.

### The "Skeleton & Meat" Strategy

Centered strokes maintain a consistent **Skeleton** (node path) while **Meat**
(stroke weight) expands symmetrically. This preserves point compatibility
across weight masters. Route to `math-computational-geometry` for the medial
axis formalization.

### Axis Mechanics

| Axis | Range | Behavior | Spoke for Deep Dive |
|------|-------|----------|-------------------|
| FILL | 0–1 | Outlined → filled via counter collapse (no node add/remove) | `lead-icon-artist` (design), `math-interpolation-designspace` (math) |
| wght | 100–700 | Stroke weight variation, node parity critical | `lead-vector-designer` (construction), `math-optical-optimization` (perception) |
| GRAD | −25–200 | Weight change without advance width change | `math-interpolation-designspace` (constraint math) |
| opsz | 20–48 | Detail density for legibility at size | `lead-icon-artist` (simplification), `math-optical-optimization` (thresholds) |

### Project-Specific: CentricSymbols Rules

- Figma authors only default master (wght=400, FILL=0, opsz=24) + opsz=20 variant
- Weight extremes and opsz=40/48 are pipeline-derived
- Inside stroke on closed paths, center stroke on open paths
- Round join, butt cap
- PUA codepoints + GSUB ligatures in parallel
- COLRv1 via fonttools injection for per-path opacity
- Full font regeneration per build

---

## Workflows

### Node Map

Route to `lead-vector-designer` for construction details.
Route to `math-bezier-spline-theory` for the curve math.

### Destructive Conversion (Figma → Font-Ready SVG)

1. Outline Stroke → 2. Flatten Booleans → 3. Path Cleanup → 4. Node Parity Check → 5. Export

Route to `lead-vector-designer` for the Figma workflow.
Route to `math-computational-geometry` for boolean operation math.
Route to `lead-technical-digital-artist` for SVG optimization and pipeline ingestion.

### Troubleshooting Exploding Glyphs

Check: node count → path direction → start point → path order → outline conversion artifacts.

Route to `math-interpolation-designspace` for compatibility theory.
Route to `lead-vector-designer` for the practical fix.

### FontTools Integration

Route to `lead-technical-digital-artist` for all pipeline scripting.
Route to `math-bezier-spline-theory` for coordinate transform math.

---

## Visual QA Cross-Link

When this skill network produces visual output — completed icon sets, weight
master reviews, axis interpolation samples, or rendered font specimens — route
to `lead-visual-qa` for a final visual quality pass.

`lead-visual-qa` will apply the appropriate spoke automatically:
- **`visual-qa-graphic-design`**: Icon set coherence, metaphor clarity, visual
  weight consistency, blur test, optical size correctness
- **`visual-qa-ui-design`**: Icon-in-context evaluation — sizing relative to
  text, optical alignment, interactive state coverage

Trigger `lead-visual-qa` when:
- A new icon or icon set is declared complete
- A weight master (thin/bold) is ready for review
- FILL=0 and FILL=1 variants need cross-evaluation for visual consistency
- opsz=20 vs opsz=48 samples need review for optical compensation quality

---

## Design-Forward Operating Directive

This entire skill network operates with a design-first philosophy. Mathematical
rigor, technical correctness, and pipeline reliability are necessary but
insufficient — every output is ultimately evaluated by how the icon **looks**
at its rendered size. The eye is the final validator. Every spoke carries its
own design-forward directive; the hub enforces this as a network-wide principle.

---

## References

- CentricSymbols v0.3 spec (see project context / artifacts)
- Google Material Symbols methodology
- OpenType variable font spec (axes, GSUB, COLRv1)
- FontTools documentation

## Related
- hub → [[lead-type-designer]]
- spoke → [[math-bezier-spline-theory]] · [[math-computational-geometry]] · [[math-interpolation-designspace]] · [[math-optical-optimization]]
