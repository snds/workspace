---
name: lead-technical-digital-artist
description: >
  Vector asset pipeline engineering, font compilation, and build automation.
  Use this skill whenever the conversation touches: FontTools Python scripting,
  font table construction (GSUB, GPOS, GDEF, cmap, COLRv1, CPAL), SVG-to-glyph
  coordinate transforms (Y-axis flip, UPM scaling), font compilation workflows,
  batch SVG processing, glyph metrics (advance width, sidebearings, ascender,
  descender), OpenType feature authoring, variable font master registration,
  designspace configuration, build automation for fonts, CI/CD for font pipelines,
  SVG optimization (SVGO, path simplification), format conversion (SVG ↔ UFO ↔
  TTF/OTF/WOFF2), PyInstaller packaging for font tools, or any question about
  *how to process vectors into compiled deliverables*. This skill covers the
  engineering pipeline — not path construction craft (lead-vector-designer) or
  icon design decisions (lead-icon-artist).
aliases: [lead-technical-digital-artist]
tier: hub
domain: design
spec_version: "2.0"
---

# Lead Technical Digital Artist

Specialist lens for font pipeline engineering, automation, and tooling. Part of
the precision vector & parametric design skill network.

---

## Domain Boundary

This skill owns **pipeline engineering** — transforming authored SVGs into
compiled, shippable font files through automated tooling.

- **How to draw paths** → `lead-vector-designer`
- **What to draw & why** → `lead-icon-artist`
- **Interpolation theory & axis design** → `variable-icon-font-architect` (hub)

---

## Core Competencies

### Coordinate System Transforms

The most common source of "upside-down glyph" bugs.

#### SVG vs. Font Coordinate Systems

| Property | SVG | Font (OpenType) |
|----------|-----|-----------------|
| Y-axis | Down is positive | Up is positive |
| Origin | Top-left | Baseline-left |
| Units | Arbitrary (viewBox) | UPM (units per em) |

#### Transform Pipeline

```
SVG viewBox coordinates
  → Scale to UPM (typically 1000 or 2048)
  → Flip Y-axis: y_font = UPM - y_svg (for baseline-aligned)
  → Translate to position on baseline
  → Output as font glyph coordinates
```

#### Project-Specific: CentricSymbols Coordinate Transform

- Source SVGs authored on 24×24 grid in Figma
- Target UPM: match Material Symbols convention (typically 2048)
- Scale factor: `2048 / 24 ≈ 85.33` per unit
- Y-flip applied after scaling
- Glyph centered in advance width with equal sidebearings

### FontTools Scripting

FontTools is the primary Python library for font manipulation in the
CentricSymbols pipeline.

#### Key Modules

| Module | Purpose |
|--------|---------|
| `fontTools.ttLib.TTFont` | Core font object — read/write/modify |
| `fontTools.pens` | Drawing API for constructing glyphs programmatically |
| `fontTools.designspaceLib` | Variable font master/axis configuration |
| `fontTools.feaLib` | OpenType feature (GSUB/GPOS) compilation |
| `fontTools.colorLib` | COLRv1/CPAL color font construction |
| `fontTools.subset` | Font subsetting |
| `fontTools.merge` | Font merging |
| `fontTools.svgLib.path` | SVG path data → pen commands |

#### Glyph Construction Pattern

```python
from fontTools.ttLib import TTFont
from fontTools.pens.t2Pen import T2Pen
from fontTools.svgLib.path import parse_path

font = TTFont()
# ... setup tables ...

glyph_name = "icon_name"
pen = font.getGlyphSet().getPen(glyph_name)

# Draw from SVG path data (after coordinate transform)
svg_path = "M100,200 L300,200 L300,400 Z"
path = parse_path(svg_path)
path.draw(pen)
```

#### Common Operations

- **Adding glyphs**: Create `glyf`/`CFF` entries + `cmap` mappings + `hmtx` metrics
- **GSUB ligatures**: Map character sequences ("settings" → icon codepoint)
- **Variable axes**: Register in `fvar`, define masters in designspace
- **COLRv1 injection**: Add `COLR`/`CPAL` tables for per-path color/opacity

### OpenType Table Construction

#### Essential Tables for Icon Fonts

| Table | Purpose | CentricSymbols Usage |
|-------|---------|---------------------|
| `cmap` | Character → glyph mapping | PUA codepoints (U+E000–U+F8FF) |
| `GSUB` | Glyph substitution | Ligature sequences for icon names |
| `glyf`/`CFF2` | Glyph outlines | Actual icon paths |
| `hmtx` | Horizontal metrics | Advance width + LSB |
| `fvar` | Variable font axes | wght, FILL, GRAD, opsz |
| `gvar`/`CFF2` | Glyph variations | Per-master deltas |
| `COLR` | Color glyph layers | Per-path opacity (COLRv1) |
| `CPAL` | Color palettes | Palette entries for COLR |
| `name` | Naming | Font family, version, copyright |
| `OS/2` | OS metrics | Weight class, width, vendor ID |
| `head` | Header | UPM, flags, dates |

#### GSUB Ligature Setup

```python
# Ligature: s-e-t-t-i-n-g-s → icon_settings glyph
feature_code = """
feature liga {
    sub s e t t i n g s by icon_settings;
} liga;
"""
```

Each icon gets a ligature rule mapping its name (as a character sequence) to
its PUA-mapped glyph. This enables `<span>settings</span>` rendering in browsers.

### COLRv1 Architecture

For icons requiring per-path opacity (not simple monochrome):

#### Structure

```
COLR table
  └── Base glyph record (icon_name)
      └── Paint tree
          ├── PaintColrLayers
          │   ├── Layer 0: PaintGlyph(path_A) + PaintSolid(color, alpha=1.0)
          │   ├── Layer 1: PaintGlyph(path_B) + PaintSolid(color, alpha=0.5)
          │   └── Layer 2: PaintGlyph(path_C) + PaintSolid(color, alpha=0.2)
          └── ...

CPAL table
  └── Palette 0
      └── Color entries (foreground color with varying alpha)
```

#### Implementation via FontTools

```python
from fontTools.colorLib.builder import buildCOLR, buildCPAL

# Define layers with opacity
layers = {
    "icon_name": [
        ("path_a_glyph", 0),   # palette index 0, full opacity
        ("path_b_glyph", 1),   # palette index 1, 50% opacity
    ]
}

colr = buildCOLR(layers)
cpal = buildCPAL([[(0, 0, 0, 255), (0, 0, 0, 128)]])

font["COLR"] = colr
font["CPAL"] = cpal
```

### Variable Font Master Registration

#### Designspace Configuration

```python
from fontTools.designspaceLib import (
    DesignSpaceDocument, AxisDescriptor, SourceDescriptor
)

doc = DesignSpaceDocument()

# Weight axis
wght = AxisDescriptor()
wght.tag = "wght"
wght.name = "Weight"
wght.minimum = 100
wght.default = 400
wght.maximum = 700
doc.addAxis(wght)

# FILL axis
fill = AxisDescriptor()
fill.tag = "FILL"
fill.name = "Fill"
fill.minimum = 0
fill.default = 0
fill.maximum = 1
doc.addAxis(fill)

# Add sources (masters)
default_source = SourceDescriptor()
default_source.filename = "masters/Regular.ufo"
default_source.location = {"wght": 400, "FILL": 0}
doc.addSource(default_source)
```

### Build Pipeline Architecture

#### Project-Specific: CentricSymbols Build Flow

```
Figma (authored masters)
  → Export SVGs (Figma plugin or manual)
  → SVG validation (node count, path direction checks)
  → Coordinate transform (24×24 → UPM, Y-flip)
  → Glyph construction (FontTools pens)
  → Table assembly (cmap, GSUB, hmtx, name, etc.)
  → Variable axis registration (fvar, gvar/CFF2)
  → COLRv1 injection (for multi-opacity icons)
  → Font compilation (TTFont.save())
  → Format conversion (TTF → WOFF2)
  → Validation (fontbakery, OpenType sanitizer)
```

#### Full Regeneration Model

CentricSymbols uses full font regeneration per build — no incremental patching.
This simplifies the pipeline (no diff/merge logic) at the cost of build time.
Acceptable for the current icon count.

### SVG Optimization

#### Pre-Pipeline Cleanup

Before SVGs enter the font build:

1. **Remove metadata**: editor artifacts, Figma-specific attributes
2. **Simplify paths**: remove redundant nodes (but preserve node count parity!)
3. **Normalize coordinates**: integer values on the authoring grid
4. **Validate structure**: single `<svg>` root, no `<use>`, no `<defs>` references
5. **Flatten transforms**: apply all `transform` attributes to path coordinates

#### SVGO Configuration (Cautious)

Icon font SVGs need a conservative SVGO config — aggressive optimization can
alter node counts or merge paths:

```yaml
# Safe plugins only
plugins:
  - removeDoctype
  - removeXMLProcInst
  - removeComments
  - removeMetadata
  - removeEditorsNSData
  - removeEmptyAttrs
  - removeEmptyContainers
  # DO NOT enable:
  # - mergePaths (breaks node parity)
  # - convertShapeToPath (may change node count)
  # - removeHiddenElems (may remove FILL=0 collapsed paths)
```

### Delivery Packaging

#### Project-Specific: CentricSymbols Delivery

CentricSymbols delivery uses:

- **Figma plugin**: icon browser, insertion, component generation
- **Local Python/FastAPI server**: font file serving, on-demand builds
- **PyInstaller**: packages the server as a standalone executable for
  non-developer users (no Python install required)

#### Font Format Output

| Format | Use Case |
|--------|----------|
| OTF (CFF2) | Desktop applications, design tools |
| TTF | Legacy compatibility |
| WOFF2 | Web delivery (smallest file size) |
| Variable TTF/OTF | Single file with all axis instances |

---

## Quality Gates

Before any font build ships:

- [ ] All glyphs render correctly at default axis values
- [ ] Variable axes interpolate without artifacts across full range
- [ ] GSUB ligatures resolve for all registered icon names
- [ ] COLRv1 layers render correct opacity in supporting browsers
- [ ] PUA codepoints are unique and within reserved range
- [ ] WOFF2 compression applied for web delivery
- [ ] fontbakery checks pass (or known exceptions documented)
- [ ] Metrics (advance width, sidebearings) consistent across all glyphs


---

## Design-Forward Operating Directive

Pipeline engineering is invisible to the end user — but its quality is not.
Every coordinate transform, table construction, and build decision either
preserves or degrades the designer's visual intent. This skill's measure of
success is not "does the font compile" but "does the compiled output look
exactly as designed."

### Principles

1. **Fidelity is the pipeline's primary metric.** A build that compiles
   without errors but introduces sub-pixel drift, quantization artifacts, or
   interpolation noise has failed. Validate visual fidelity at every pipeline
   stage — not just structural correctness.

2. **Coordinate transforms are design-critical.** The Y-axis flip, UPM
   scaling, and grid quantization are not mere format conversions — they can
   introduce rounding errors that compound across glyphs. Route to
   `math-bezier-spline-theory` for precision analysis and
   `math-optical-optimization` to understand when rounding errors cross the
   perceptual threshold.

3. **Build automation serves design iteration.** The full-regeneration model
   exists so designers can iterate quickly. Pipeline speed and reliability
   directly affect design quality by enabling more review cycles. Optimize
   build times without sacrificing fidelity.

4. **COLRv1 is a design tool, not just a format feature.** Per-path opacity
   enables visual depth, hierarchy, and emphasis within a single icon.
   Implement COLRv1 injection with the same care as glyph construction —
   opacity values should be design-specified, not arbitrary.

5. **Validate against the full axis range.** A font that renders correctly at
   the default instance but breaks at axis extremes or unusual combinations
   has a pipeline bug. Route to `math-interpolation-designspace` to identify
   interpolation edge cases, then build validation checks for them. Test at
   the corners and center of the designspace, not just the default.

6. **Surface visual issues, don't silently absorb them.** If the pipeline
   detects a glyph with unexpected node counts, path direction mismatches,
   or out-of-tolerance Hausdorff distance from the source SVG, flag it
   visually (render a comparison) rather than just logging a warning.
   Designers respond to visual evidence, not log files.
