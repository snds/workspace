---
name: visual-qa-interior-design
description: >
  Interior design visual QA specialist. Use this skill for reviewing: interior
  renders and visualizations, spatial proportion and room scale, furniture
  selection and arrangement quality, material and finish accuracy (fabrics,
  stone, wood, metals, paint), PBR material correctness in interior renders,
  lighting simulation (natural light, artificial lighting layers, accent
  lighting), light color temperature accuracy and consistency, shadow quality
  in interior spaces, ceiling height and architectural detail accuracy,
  flooring pattern scale and direction, rug sizing and placement, art and
  object placement composition, style consistency (modern, traditional,
  transitional, etc.), FF&E (furniture, fixtures, equipment) scale and
  proportion relative to room, window treatment design, millwork and
  cabinetry detail quality, kitchen and bath fixture accuracy, spatial
  flow and traffic path legibility, color palette harmony in a three-
  dimensional context, and whether an interior render communicates the
  intended mood, function, and aesthetic accurately. Spoke of lead-visual-qa.
aliases: [visual-qa-interior-design]
tier: cross-cutting
domain: quality
hub: lead-visual-qa
spec_version: "2.0"
---

# Visual QA — Interior Design

Interior design quality assurance specialist. Evaluates visual output through
the lens of interior design craft: spatial proportion, material accuracy,
lighting simulation, furniture arrangement, style coherence, and the quality
of interior visualization. Spoke of `lead-visual-qa`.

---

## Domain Boundary

This skill owns the **interior environment evaluation lens**.

- **Building envelope, facade, site context** → `visual-qa-architecture`
- **Brand and graphic elements (signage, menus, labels)** → `visual-qa-graphic-design`
- **Interactive digital interfaces within the space** → `visual-qa-ui-design`
- **Game-engine interior environments** → `visual-qa-game-design` + this skill

Interior design and architecture overlap at the building envelope. Structural
elements (columns, beams, window openings) are architectural; how those elements
are treated, finished, and furnished is interior. Apply both lenses when the
artifact involves both exterior structure and interior condition.

---

## Spatial Proportion QA

### Human Scale Verification

Every interior render must be anchored to human scale.

- **Ceiling height**: Residential standard 2.4–2.7m; premium residential 3.0–3.5m;
  commercial/hospitality 3.5–5.0m+. Identify and flag ceilings that read too low
  or impossibly high for the stated context.
- **Door height**: 2.1m standard residential; 2.4m premium; 3.0m+ in monumental
  or hospitality contexts.
- **Furniture scale**: A sofa seat height is ~430–480mm; dining table height ~750mm;
  kitchen counter height ~900mm; bar height ~1050–1100mm. Furniture that doesn't
  match these modules reads as incorrectly scaled.
- **Human figures**: Where present, entourage figures should be 1.7–1.8m standing.
  Check figures against doors, counters, and furniture for consistent scale.

### Room Proportion

- Does the room's proportional width-to-length-to-height relationship read as
  livable and plausible for the stated function?
- Is there spatial breathing room — do furniture arrangements allow plausible
  traffic paths (minimum 900mm clear path in residential; 1200mm in commercial)?
- Do ceiling details (coffered ceilings, beams, crown mouldings) scale
  proportionally to the room volume?

---

## Material and Finish QA

### Surface Material Accuracy

| Material | Expected Visual Properties | Common Failures |
|----------|---------------------------|----------------|
| **Hardwood flooring** | Grain direction consistent along plank length; knots/variation appropriate to species; finish sheen matching stated finish (matte/satin/gloss) | Grain running across planks; all planks identical; tiling repeat visible |
| **Stone (marble, granite)** | Veining scale relative to slab size; bookmatching on featured walls; honed vs. polished finish distinction | Veining too small (tile scale on full wall panels); no matching at joints |
| **Painted wall** | Slight sheen variation near light sources; no tiling artifacts; color consistent with stated paint and finish | Flat matte with no material response to light |
| **Fabric (upholstery)** | Texture visible at seam transitions; cushion compression under load; wrinkle and fold plausibility | Fabric appears stretched over a hard form; no texture; impossibly perfect |
| **Carpet** | Pile direction consistent; compression in traffic paths; correct color response under different light angles | Flat, textureless surface; no response to directional light |
| **Metal fixtures (brushed)** | Directional grain in consistent direction; specular highlight elongated along grain; no mirror-finish | Omnidirectional reflection — reads as polished, not brushed |
| **Glass (backsplash, shelves)** | Semi-transparent with slight tint; edge glow; backing color influence | Fully transparent (no glass feel) or opaque |

### Texture Scale

Every texture must be calibrated to real-world material dimensions:
- Hardwood plank width: 75–150mm typical; wide plank 150–250mm
- Tile module: 100×100mm to 600×600mm — tiles must not appear to be the wrong
  size for the stated material
- Wallpaper patterns: repeat size must be plausible for standard roll dimensions
- Stone slab tiles: 600×600mm, 600×1200mm, 1200×2400mm are the common range

**Tiling artifact check**: At normal viewing distance, no texture repetition
should be visible as a geometric grid.

---

## Lighting Simulation QA

### Natural Light

Natural light in an interior render should read as physically consistent:

- **Sky condition match**: The quality of light entering windows (hard/directional
  vs. soft/diffuse) must match the sky visible through those windows
- **Light penetration depth**: Direct sunlight penetrates a room proportionally to
  the sun altitude and window dimensions. A low morning sun creates a bright rectangle
  on the floor at an angle; overhead sun creates a pool directly below the window.
- **Color temperature gradient**: Natural light is cooler near the window, warming
  toward the interior as it mixes with artificial light (if present)
- **Exposure on window area**: Correctly rendered windows should show a blown-out or
  near-blown-out exterior through glass — interior-calibrated exposure makes exteriors
  lose all detail, which is correct

### Artificial Lighting Layers

A high-quality interior lighting design uses multiple layers:

| Layer | Description | Visual Indicator |
|-------|-------------|-----------------|
| **Ambient** | Overall base light level | Even, low-intensity illumination throughout |
| **Task** | Functional light at activity areas | Kitchen pendants over island; desk lamp; under-cabinet |
| **Accent** | Highlighting architectural features or objects | Cove lighting, art spotlights, toe-kick lighting |
| **Decorative** | Fixtures as objects of beauty (chandeliers, sconces) | Fixture itself is visible; light contribution may be minimal |

Evaluate: Is each layer present at appropriate intensity? Renders with only
ambient lighting flatten the space and remove depth.

### Light Color Temperature

Residential spaces typically mix warm (2700–3000K) and neutral (3000–3500K) sources.
Evaluate:

- **Consistency**: Are all artificial sources in a zone the same color temperature,
  or do some read warmer/cooler without reason?
- **Day/night transition**: In renders showing an interior with exterior view, does
  the balance between warm interior and cool exterior read correctly for the stated
  time of day?
- **Accent light color accuracy**: Colored accents (blue under-cabinet, warm cove)
  must mix plausibly with surrounding surfaces

---

## Furniture and FF&E Arrangement

### Arrangement Principles

Interior furniture arrangements are evaluated on function, circulation, and composition.

**Functional zoning**: Furniture should define activity zones visually:
- Seating grouped to face a focal point (fireplace, view, TV) — not scattered
- Dining area clearly separate from living area even in open-plan spaces
- Work areas isolated from rest/relaxation areas

**Traffic paths**: Are there clear paths from entry to key destinations without
requiring furniture to be moved or circled awkwardly? Minimum 900mm clear path.

**Focal point hierarchy**: Every room should have one dominant focal point and
supporting secondary elements. Flag rooms where:
- Multiple competing focal points exist at equal visual weight
- The strongest visual element is not the intended focal point

### Rug Sizing

Rug sizing is one of the most common interior design errors in renders:
- **Living room**: All major seating legs on the rug, or front legs of all seating
  on the rug — rug should not be small enough that all furniture floats off it
- **Dining room**: Rug should extend 600mm beyond the table on all sides to
  accommodate pulled-out chairs
- **Bedroom**: Rug should extend 450–600mm beyond the bed sides and foot;
  a rug that only reaches under half the bed is undersized

### Art and Object Placement

- **Art hanging height**: Center of art at approximately eye level (~145–160cm
  from floor), not from the top of the frame
- **Art scale to wall**: Art that is too small for the wall it occupies reads as
  incorrect placement; art should fill 2/3–3/4 of the wall width for a solo piece
- **Object grouping (vignettes)**: Objects grouped in a display should vary in
  height and visual weight; odd numbers of objects (3, 5) typically group more
  naturally than even numbers

---

## Style and Mood Coherence

### Style Consistency

Interior design styles have defining characteristics that must be consistent across all
elements in the space:

| Style | Key Visual Markers | Failure Mode |
|-------|-------------------|--------------|
| **Contemporary** | Clean lines, neutral palette, mixed metals, minimal ornament | Mixed period pieces that don't have contemporary reinterpretation |
| **Traditional** | Symmetry, warm tones, carved details, rich fabrics, one metal finish | Modern elements with no transitional bridging |
| **Scandinavian** | Light wood, white/grey palette, natural materials, minimal accessories | Busy pattern mixing; warm/dark tones |
| **Industrial** | Raw materials (concrete, brick, steel), utilitarian fixtures, dark palette | Polished finishes where raw materials are expected |
| **Biophilic** | Natural materials, plant life, organic forms, natural light emphasis | Artificial-looking plants; heavy use of synthetic materials |

### Mood Accuracy

Does the render's color temperature, material selection, furniture choice, and
lighting create the mood specified in the brief?

- **Cozy/warm**: Soft textures, warm lighting, warm wood tones, layered fabrics
- **Minimal/serene**: High contrast of surfaces, clean shadows, neutral palette,
  carefully curated object count
- **Energetic/vibrant**: Color saturation, contrasting patterns, bright task lighting
- **Sophisticated/formal**: Symmetry, rich materials, precise shadow, restrained palette

If a render is described as "warm and inviting" but reads as cool and sterile —
or vice versa — flag the delta between stated mood and achieved mood.

---

## QA Checklist — Interior Design

**Scale and Proportion:**
- [ ] Ceiling height reads correctly for the stated building type
- [ ] Furniture heights match real-world FF&E dimensions (seat 430–480mm, counter 900mm)
- [ ] Traffic paths are visibly clear (≥ 900mm residential, ≥ 1200mm commercial)
- [ ] Human figures (if present) are correctly scaled to architectural elements

**Materials:**
- [ ] Wood grain runs in the correct direction along planks
- [ ] Stone veining scale is appropriate for slab/tile size
- [ ] All textures are calibrated to real-world material dimensions
- [ ] No visible tiling repetition at normal viewing distance
- [ ] Material finish (matte/satin/gloss) is visually distinguishable and correct

**Lighting:**
- [ ] Natural light direction and quality match the sky visible through windows
- [ ] Artificial lighting uses at least ambient + task layers
- [ ] Color temperatures are consistent within zones
- [ ] Interior has depth through contrast between lit and shadowed areas

**Furniture and Arrangement:**
- [ ] Seating grouped to address a clear focal point
- [ ] Rug is correctly sized (furniture legs on rug; dining rug extends beyond chairs)
- [ ] Art hung at eye level and scaled appropriately to the wall
- [ ] Room has one dominant focal point

**Style and Mood:**
- [ ] All furniture, materials, and objects belong to the same style family (or bridged deliberately)
- [ ] The render's mood (light quality, palette, texture) matches the stated brief
- [ ] No rogue elements that break the style coherence without justification
