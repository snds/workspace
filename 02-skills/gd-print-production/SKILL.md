---
name: gd-print-production
description: >
  The physical constraints and craft of print — where design meets
  manufacturing. Use this skill whenever the conversation touches: offset
  lithography, digital printing, screen printing, letterpress, flexography,
  gravure, CMYK separations, spot colors, Pantone, duotones, bleed, safe
  zone, crop marks, registration marks, color profiles, ICC profiles, Fogra39,
  ISO Coated v2, SWOP, paper stock, gsm, coated vs. uncoated paper, paper
  grain direction, binding methods (saddle stitch, perfect bind, case bind),
  PDF/X-1a, PDF/X-4, font embedding, prepress, contract proofs, print proofing,
  or any question about preparing files for physical output.
aliases: [gd-print-production]
tier: spoke
domain: design
hub: lead-graphic-designer
prerequisites: [lead-graphic-designer]
spec_version: "2.0"
---

# GD — Print Production

Specialist lens for printing processes, prepress requirements, and physical
production craft. Part of the Lead Graphic Designer skill network.

---

## Domain Boundary

This skill owns **print production knowledge** — everything from understanding
how a printing process works to preparing files that survive the press.

- **Color theory and color model fundamentals** → `gd-color-theory`
- **Brand color specification across print and digital** → `gd-brand-identity`
- **Typography for print** → `gd-typography`
- **Grid and layout for print** → `gd-grid-and-layout`

---

## Printing Processes

Understanding the printing process is not optional for a graphic designer
producing for print. Each process has specific capabilities and constraints
that must be addressed in the design and file preparation phase — not
discovered at the press.

### Offset Lithography

**Mechanism:** Ink is transferred from a metal plate to a rubber blanket,
then from the blanket to paper. The process separates CMYK (and optional spot)
colors onto separate plates. The term "offset" refers to the blanket
intermediary — ink never transfers directly from plate to paper.

**Specifications:**
- Color mode: CMYK + optional Pantone spot colors
- Resolution: 300 dpi at final size (for raster elements)
- Line screen (LPI): 150–175 LPI for coated stock, 100–133 LPI for uncoated
- Dot gain: 10–15% coated, 20–30% uncoated — compensated by ICC profiles

**When to use:** High volume (1,000+ copies), high quality, consistent color.
Magazines, books, packaging, annual reports, corporate stationery.

**Strengths:** Best color consistency run-to-run; capable of Pantone spot color;
most economical at high volume.

**Limitations:** Expensive setup (plates, make-ready); not economical below
~500 copies; no variable data; requires longer production lead times.

### Digital Printing

**Mechanism:** Electrostatic/inkjet process, no plates. Each copy can differ
(variable data printing). Color is CMYK only (no true Pantone spot).

**Specifications:**
- Color mode: CMYK (some presses simulate spot with extended gamut)
- Resolution: typically 600–1200 dpi equivalent
- Dot gain: lower and more predictable than offset

**When to use:** Short runs (1–500 copies), proofing, personalization, fast
turnaround, test prints, on-demand printing.

**Limitations:** Color consistency across large runs is inferior to offset;
no true Pantone; some paper limitations (not all stocks work with digital);
higher per-unit cost at large volumes.

### Screen Printing

**Mechanism:** Ink is pushed through a mesh screen (one screen per color)
onto the substrate. Used for textiles, signage, and specialty applications.

**Specifications:**
- Each color requires a separate screen; color count directly affects cost
- Colors must be opaque (or carefully sequenced) on dark substrates
- Halftones are possible but limited; prefer flat color separation for screen

**When to use:** Apparel, merchandise, signage, specialty paper. Any application
where durability and tactile ink deposit are required.

**Limitations:** Registration across multiple colors has tolerances; fine type
and detail are problematic; not suitable for photographic reproduction at small scale.

### Letterpress

**Mechanism:** Relief printing — raised type or image is inked and pressed
into the substrate. The historical printing method; now used for its tactile,
handcrafted qualities.

**Specifications:**
- Best for single or two colors; multi-color requires careful registration
- Works with photopolymer plates (for halftones and logos) or actual metal type
- Impression depth (the "debossed" feel) requires appropriate paper weight (300gsm+)

**When to use:** High-end stationery, invitations, packaging details, artisanal
publications where tactile quality is the message.

### Flexography

**Mechanism:** Relief printing using flexible rubber/polymer plates, applied
inline in a roll-to-roll process. Standard process for packaging.

**Specifications:**
- Minimum line weight: 0.5–0.75pt (thinner lines close up)
- Minimum type size: 6–7pt (smaller fills in or drops out)
- Ink trapping (slightly overprinting adjacent colors) prevents gaps
- Kiss-cut die lines for labels; full cut for cartons

**When to use:** Labels, flexible packaging (bags, wrappers), corrugated
packaging, folding cartons. Essential to know if designing packaging.

### Gravure (Rotogravure)

**Mechanism:** Intaglio process — image is etched into a cylinder; ink fills
the recesses; excess is wiped by a doctor blade; paper picks up the ink under
pressure.

**When to use:** Ultra-high volume (millions of copies): magazines, catalogs,
packaging, currency, stamps. Not relevant for most graphic design practice
unless working in high-volume publication or packaging.

---

## Color Modes and Separations

### CMYK Process Color

All press-ready files for full-color offset or digital printing must be in
CMYK with an embedded or assigned ICC profile.

**Rich black vs. true black:**
- True black: 0C 0M 0Y 100K — single-plate black; use for type and fine lines
- Rich black: 60C 40M 40Y 100K (or similar builds) — deep, saturated black
  for large fills; NEVER use for type (registration tolerances cause blur)
- Solid knockout black: areas where black text appears over a color background
  should be set to overprint the black plate only — not knock out the background

### Spot Colors (Pantone)

Each Pantone spot color requires a dedicated ink plate. Budget implications:
- 2-color job (black + 1 spot): cheaper setup than 4-color process
- 4-color process + 1 spot: significantly more expensive than process alone

**When spot color is worth the cost:**
- When the brand color cannot be accurately reproduced in CMYK (most saturated
  Pantone colors — especially blues, greens, oranges)
- When a metallic, fluorescent, or specialty ink is required
- When absolute color consistency across a run or across printers is critical

### Duotones, Tritones, Quadtones

Duotone: a black-and-white image converted to two plates — typically black plus
a brand color. Creates a rich, distinctive treatment. Set up in Photoshop (Image
Mode → Duotone) with custom curves for each plate.

**File requirement:** duotone images must be placed in the layout as-is (as
Photoshop .eps or .pdf), not flattened to CMYK — flattening destroys the
duotone relationship.

### Special Finishes

Finishes applied after printing (post-press):
- **Spot UV varnish**: high-gloss varnish applied to specific areas; requires
  a separate die/plate; specified as a fifth color channel in the press file
- **Foil stamping**: metallic or holographic foil applied by heat and pressure;
  separate plate; only works on smooth, even surfaces
- **Emboss / deboss**: paper pressed into a die to create a raised/recessed
  area; works with or without foil; requires a separate die specification
- **Matte/gloss laminate**: applied to the entire sheet; changes the surface
  texture and protects the print

---

## Prepress Requirements

### Bleed
Bleed extends artwork beyond the trim edge so that when the press sheet is
trimmed, ink runs to the exact edge with no white showing.

**Standard bleed:** 3mm (metric) / 0.125 inch (imperial) on all sides.
Some printers require 5mm for certain processes.

**When to apply:** Any element that bleeds off the page — backgrounds, full-bleed
images, colored panels that extend to the edge. Elements that end before the
edge do not need bleed.

### Safe Zone
The safe zone (live area) is the margin within which all critical content
must appear — type, logos, key visual elements. Paper shift at the press
and trimming tolerances mean elements close to the edge can be cut off.

**Standard safe zone:** 3mm inset from the trim edge (6mm from the bleed edge).
Some printers require 5mm safe zone.

### Crop Marks and Registration Marks
- **Crop marks** (trim marks): indicate where the sheet will be cut; placed
  outside the bleed area
- **Registration marks**: cross-hair marks used to align plates; placed outside
  the crop marks
- **Color bar**: a strip of ink swatches used for press calibration

Most design applications (InDesign, Illustrator) add these automatically on
PDF export. Do not draw them manually.

### Color Profiles and Intent

Every press-ready PDF should have a color profile either embedded or specified:

| Profile | Use Case |
|---------|----------|
| ISO Coated v2 / Fogra39 | European offset printing on coated stock (standard) |
| ISO Uncoated / Fogra47 | European offset on uncoated stock |
| SWOP v2 | North American publication printing |
| GRACoL 2013 | North American commercial printing on coated stock |
| Japan Color 2011 | Japanese printing standards |

**Rendering intent** for color conversion:
- Perceptual: adjusts the entire gamut to fit the destination; best for photographic images
- Relative Colorimetric: clips out-of-gamut colors to the nearest in-gamut value;
  best for logos and spot color builds; preserves whites

---

## Paper and Substrate

### Specifying Paper

**GSM (grams per square meter)**: the universal paper weight standard.

| Weight | Type | Typical Use |
|--------|------|-------------|
| 60–90 gsm | Lightweight text stock | Newsprint, offsets, novel paper |
| 90–120 gsm | Standard text stock | Letter paper, book interiors |
| 130–170 gsm | Heavy text / light cover | Magazine pages, letterhead |
| 200–250 gsm | Cover stock | Brochure covers, postcards |
| 300–400 gsm | Heavy cover | Business cards, packaging |
| 400+ gsm | Board | Folding cartons, rigid packaging |

**Surface treatments:**
- **Coated gloss**: highest color fidelity, brightest colors, sharp edges;
  fingerprints show; reads as corporate/commercial
- **Coated silk/satin**: high quality, slight sheen, more tactile than gloss;
  balanced aesthetic
- **Coated matte**: flat surface, good color fidelity, more upscale/understated;
  slightly less sharp than gloss at fine detail
- **Uncoated**: ink absorbs into fibers; colors shift (see `gd-color-theory`);
  more tactile; warmer, more personal feel; premium when combined with letterpress
  or heavy weight

**Paper grain direction:** Paper has a machine direction (grain). Folded parallel
to grain folds cleanly; folded against grain cracks or resists. Books must be
bound with grain parallel to the spine. Confirm with the printer.

**Opacity**: Important for double-sided printing. Too-thin paper will show
the reverse side through (show-through). Specify minimum opacity (80%+) for
two-sided work.

---

## Binding Methods

| Method | Description | Best For |
|--------|-------------|----------|
| **Saddle stitch** | Staples through the fold of nested signatures | Magazines, catalogs, brochures (up to ~64 pages) |
| **Perfect bind** | Pages and covers glued at a flat spine | Trade paperbacks, magazines over 64 pages, catalogs |
| **Case bind (hardcover)** | Text block sewn and glued into a rigid board cover | Books, corporate reports, premium publications |
| **Ring bind (loose-leaf)** | Pages hole-punched and bound with rings | Manuals, workbooks, anything that needs to open flat |
| **Swiss binding** | Exposed-spine binding; visible sewing thread; opens completely flat | Premium publications, art books, portfolios |
| **Japanese stab binding** | Thread sewn through the entire stack; opens with resistance | Art books, limited editions; cannot open flat fully |

**Structural implications:**
- Saddle stitch requires page count in multiples of 4 (a "signature")
- Perfect bind requires minimum page count (~48–64 pages for structural integrity)
- Case bind is significantly more expensive; use when the physical object is
  part of the brand statement

---

## File Delivery Standards

### PDF/X Standards

PDF/X is an ISO standard for print-production PDF that eliminates features
which cause press failures:

**PDF/X-1a:**
- CMYK and spot colors only (no RGB, no device-independent color)
- All fonts embedded
- No live transparency (all transparency must be flattened)
- ICC profile embedded or output intent specified
- No JavaScript, forms, multimedia

Use PDF/X-1a for: offset printing, any workflow that cannot handle live transparency,
any workflow where you need maximum compatibility with older RIP systems.

**PDF/X-4:**
- Allows live transparency (RIP flattens at output)
- Allows CMYK, spot color, and ICC-tagged RGB/Lab (RIP converts)
- All fonts embedded
- ICC output intent specified

Use PDF/X-4 for: modern workflows, files using effects that would degrade if
pre-flattened, files with complex transparency.

### Font Embedding

All fonts must be embedded in the press file. Failure to embed results in font
substitution (the most common reason for press rejections).

- Always embed fonts when exporting PDF, not just subsetting
- Check PDF properties after export: confirm "All Fonts Embedded"
- Convert fonts to outlines as a fallback only — this prevents later editing
  and loses hinting, which affects rendering quality

### Image Resolution Requirements

- **CMYK photographs**: 300 dpi at 100% final print size (minimum 250 dpi)
- **Lineart/bitmaps**: 1200 dpi (600 dpi minimum)
- **Vector artwork**: resolution-independent — always use vector for logos and linework
- **Scaling images in layout**: images should never be scaled above 100%
  in the layout — scale them in Photoshop first; scaling up in InDesign reduces
  the effective resolution

---

## Print Proofing

Three levels of proof validate different aspects of the work:

### Digital Proof (Contract Proof)
A colorimetrically accurate inkjet print using the production ICC profile.
This is the legal standard for color approval before press.

**What it validates:** color accuracy against the ICC profile; content completeness;
layout correctness; bleed and crop marks.

**What it doesn't validate:** actual press color (small deviations occur due
to ink, paper, and press variables); special finishes (foil, emboss, spot UV).

### Press Proof
A short run on the actual production press with actual inks and paper.

**When to use:** Brand-critical jobs with strict color requirements; jobs with
special inks (metallics, neons, Pantone spot); first-time production on a new
press or stock.

**Cost:** Expensive — press setup time plus material costs. Reserved for
high-value jobs.

### Soft Proof (Monitor Proof)
On-screen preview using a calibrated monitor with the ICC profile applied
as a soft proof simulation.

**Requirements for accuracy:** calibrated monitor (hardware colorimeter required;
screen calibration targets should be 6500K D65, gamma 2.2 or sRGB); room
ambient lighting controlled; proof comparison against a reference print.

**What it validates:** layout, content, approximate color.

**Not a substitute for a contract proof** for color-critical work.

---

## Anti-Patterns

- **RGB files for offset printing.** Convert to CMYK with the correct ICC
  profile before delivering to press. After-the-fact conversion produces
  unpredictable color shifts.
- **No bleed on bleed-to-edge elements.** The single most common prepress error.
  If ink goes to the edge, it needs 3mm bleed.
- **Rich black on type.** Multi-plate blacks on text causes registration blur.
  Use 100K only for all type, hairlines, and fine detail.
- **Low-resolution images.** Placing 72 dpi screen-captured images in a print
  layout will produce visible pixelation. Source 300 dpi images.
- **Unembedded fonts.** The most common reason for PDF rejection. Always
  verify font embedding after export.
- **Coated ICC profile on uncoated stock.** The color will be darker and
  muddier than the proof. Match the ICC profile to the actual stock.
- **PDF/X-1a with live transparency.** Transparency will be stripped or
  cause errors. Either flatten before export or use PDF/X-4.
- **Designing grain direction without specifying it.** A folding carton
  or book designed against grain will crack or resist at the fold.

---

## Cross-Links

- **`gd-color-theory`**: color model understanding (CMYK vs. RGB), Pantone
  color behavior, dot gain, simultaneous contrast — all from this spoke
- **`gd-brand-identity`**: brand color specification across print and digital;
  the Pantone/CMYK/RGB requirement in brand standards is a print production
  requirement
- **`gd-typography`**: type for print: minimum sizes for each process,
  counterspace requirements, rich black rules for text
- **`gd-grid-and-layout`**: bleed zones and safe zones integrate with grid
  setup; margins must account for print tolerances

---

## References

- Tony Johnson: ICC Profile specifications (International Color Consortium)
- ISO 12647-2: Offset lithographic printing — process control
- ISO 15930: PDF/X standards (all parts)
- Fogra Research Institute: ICC profile documentation
- PrintWiki: open resource for printing technology terminology
- Frank Romano: *Delmar's Dictionary of Digital Printing and Publishing* (2004)
