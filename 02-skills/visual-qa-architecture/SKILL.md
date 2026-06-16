---
name: visual-qa-architecture
description: >
  Architectural design visual QA specialist. Use this skill for reviewing:
  architectural renders and visualizations (exterior and interior structural),
  building proportions and massing, facade composition and rhythm, material
  accuracy and PBR correctness in renders, structural plausibility, site
  context integration, landscape and hardscape rendering quality, lighting
  simulation accuracy (natural and artificial), time-of-day render quality,
  shadow accuracy and cast behavior, human scale elements (people, vehicles,
  furniture), entourage quality (trees, landscaping, signage), aerial and
  bird's-eye renders, section and elevation drawing quality, axonometric and
  isometric architectural illustration, construction document clarity,
  architectural diagram legibility, form and geometry accuracy, window
  and glazing material quality, contextual fit of buildings in existing
  streetscapes or environments. Spoke of lead-visual-qa.
aliases: [visual-qa-architecture]
tier: cross-cutting
domain: quality
hub: lead-visual-qa
spec_version: "2.0"
---

# Visual QA — Architecture

Architectural design quality assurance specialist. Evaluates visual output
through the lens of architectural craft: building proportion, material
accuracy, structural logic, lighting fidelity, site context, and the quality
of architectural communication. Spoke of `lead-visual-qa`.

---

## Domain Boundary

This skill owns the **architectural visualization evaluation lens**.

- **Interior finish, furnishing, spatial arrangement** → `visual-qa-interior-design`
- **Game-level environment art** → `visual-qa-game-design`
- **Brand, signage, wayfinding** → `visual-qa-graphic-design`
- **Accessibility in built environments** → apply `visual-qa-accessibility` for
  visual communication; consult ADA/WCAG standards for built-environment compliance

Architecture and interior design overlap at the threshold of a building.
Exterior massing, structural envelope, and site context are architectural.
The moment the lens is inside the building evaluating a room, apply
`visual-qa-interior-design` in parallel.

---

## Proportion and Massing QA

### Human Scale

Architectural proportion is meaningless without a human scale reference.
Evaluate every render for correct scale referencing:

- **People**: Are entourage figures correctly scaled? A standing adult is ~1.75–1.8m.
  Check figures against door heights (~2.1m), floor-to-floor heights (~3.0–4.5m),
  and vehicle dimensions.
- **Vehicles**: Standard passenger car ~4.5m long, ~1.5m tall. Larger vehicles should
  not dwarf the building unless the building is intentionally monumental.
- **Doors and windows**: Standard door height is 2.1m. Residential windows 1.0–1.5m
  tall. Commercial storefronts 2.5–4.0m. Flag anything that doesn't follow a
  plausible module.

### Facade Rhythm and Proportion

- **Bay rhythm**: Does the facade have a consistent structural rhythm (column-to-column
  spacing, window-to-window spacing) that reflects structural logic?
- **Floor height legibility**: Are floor lines readable on the facade? Horizontal
  banding and shadow lines between floors give scale to large buildings.
- **Vertical proportion**: Does the building's overall height-to-width ratio feel
  intentional and structurally plausible?
- **Golden ratio / modular coordination**: Is there an evident proportional system?
  Buildings designed without a proportional logic often feel "random" even when
  technically constructible.

---

## Material and Texture QA

### PBR Correctness in Renders

| Material | Expected Visual Properties | Common Failures |
|----------|---------------------------|----------------|
| **Concrete (raw)** | Matte, slight variation, formwork texture, minor color range | Overly smooth and uniform — reads as cheap render preset |
| **Glass (clear)** | Reflective at low angles, semi-transparent at ~90°, tinted blue-green at edge | Fully black or fully transparent — no physical glass behavior |
| **Glass (structural)** | Reflection dominant, sky colors, slight tint, frame shadows | Mirror-perfect with no distortion — reads as painted metal |
| **Steel (painted)** | Semi-gloss, slight specular, consistent sheen | High-gloss plastic look; or flat matte that reads as cardboard |
| **Brick** | Matte, variation in color and mortar, grout lines consistent in scale | All bricks identical (tiled texture); mortar too light or too dark |
| **Stone (cut)** | Joint lines at module, slight variation per stone, edge sharpness | Overly uniform; or texture doesn't match scale of joints |
| **Timber / wood siding** | Wood grain direction consistent; weathering appropriate to age | Grain direction changes mid-panel; unnaturally even color |
| **Metal panel** | Flat or micro-brushed, joint lines, slight specular variation | No joint lines — looks like solid painted surface |

### Material Scale

- Texture maps must be scaled to match real-world material size
- Brick should have ~65mm courses; floor tiles should match the specified module;
  stone cladding should reflect realistic slab sizes (~600–1200mm)
- **Tiling artifacts**: Is a repeating texture visible as a repeating tile grid?
  Flag any 2×2 or 4×4 repeat that is visible at render scale.

### Weathering and Age Appropriateness

- Does the material finish match the building's stated context and age?
- A new contemporary building: pristine finishes, clean edges
- A historical building or adaptive reuse: weathering, patina, aging appropriate
  to the material and climate
- Mismatch between a "worn" material and otherwise perfect geometry reads as
  a texture application error, not intentional aging

---

## Lighting QA

### Sun and Shadow Accuracy

- **Shadow direction consistency**: All shadows in a scene must originate from the
  same sun angle. Mixed shadow directions in a single render are a critical failure.
- **Shadow softness**: Direct sunlight at midday produces hard shadows; early/late
  sun and overcast conditions produce soft shadows. The softness must match the
  sky condition.
- **Ambient occlusion**: Contact shadows and crevice darkening should be present
  and physically plausible. Missing ambient occlusion makes renders look "floating."
- **Sun altitude legibility**: The render's stated time of day should be readable
  from shadow length, sky color, and highlight intensity. A "golden hour" render
  must have warm side lighting, long shadows, and a warm-to-cool gradient in the sky.

### Artificial Lighting

- Do interior light sources (visible through glazing in nighttime renders) produce
  correct light spill onto exterior surfaces?
- Are accent lights (uplighting on trees, facade wash lighting) producing the
  correct beam spread and falloff?
- At night, is there a plausible ambient contribution from surrounding context
  (street lights, neighboring buildings, sky glow), or is the scene unnaturally dark
  outside lit areas?

### Sky and HDR Quality

- Does the sky match the intended render time and weather?
- Is the sky resolution appropriate — no visible pixels or HDRI seams?
- Does the sky's light color match the light on the building? (An overcast sky
  should not produce hard directional shadows on the building)

---

## Structural Plausibility

### Gravity and Support Logic

Renders must depict architecturally plausible structures — elements must be
visibly supported or have a clear structural logic for their spanning.

- **Cantilevered elements**: Long cantilevered floors, roofs, or balconies should
  have visible structural support members (steel beams, post tension, back-span)
- **Column and beam expression**: Where structure is visible, its size should be
  proportional to the span (thin columns cannot support a wide, heavy roof)
- **Floating elements**: Any mass that appears to hover or float requires a visible
  support strategy — glass fins, tension cables, concealed post — or reads as
  an error

### Constructibility Red Flags

- Angles that would require non-standard construction methods without visible
  acknowledgment
- Material transitions that would be impossible to waterproof (open horizontal
  joints in walls, upturned roof perimeters without flashing)
- Window openings without visible frames or structural headers over wide spans

---

## Site Context and Integration

### Site Fit

- Does the building's scale, massing, and character relate to the surrounding context?
- Is the streetscape accurately represented (adjacent buildings, sidewalk width,
  street furniture scale)?
- Is the topography correct — does the building meet the ground in a way that
  reflects the site's slope?

### Landscape and Hardscape Quality

- Are tree species and sizes appropriate to climate and stated maturity level?
- Is ground cover (lawn, paving, gravel) correctly textured and scaled?
- Do planted areas have shadow and ambient occlusion that grounds them in the scene?
- Is hardscape (pavement, steps, curbs) at correct scale and with correct material reads?

### Entourage Integration

Entourage (people, vehicles, trees, signage) must:
- Cast correct shadows at the correct angle
- Have correct scale relative to each other and the building
- Be placed in contextually appropriate positions (people on sidewalks, not
  floating in space; cars in parking areas at correct spacing)

---

## Communication Quality (Drawings and Diagrams)

### Elevation and Section Drawing Quality

- Are line weights differentiated correctly? (Cut elements heavier; visible elements
  medium; background elements lighter)
- Is the scale bar present and legible?
- Are material patterns applied consistently with drafting conventions?
- Do section cuts show the correct interior condition (floor construction, wall
  build-up, ceiling depth)?

### Architectural Diagram Legibility

- Is the diagram's message immediately legible without reading labels?
- Are arrows and flow indicators clearly directional (arrowheads, not bidirectional)?
- Is color used with a consistent legend (program areas, circulation, structure)?
- Is the diagram appropriately abstract — not confused with a floor plan or render?

---

## QA Checklist — Architecture

**Proportion and Scale:**
- [ ] Human-scale elements (people, doors, vehicles) are correctly sized
- [ ] Facade rhythm reflects a structural logic
- [ ] Floor heights are readable on the facade
- [ ] Overall massing proportions are plausible

**Materials:**
- [ ] All materials have correct PBR properties (reflectivity, roughness)
- [ ] Texture scale matches real-world material dimensions
- [ ] No visible tiling artifacts at render scale
- [ ] Material finish matches building age and context

**Lighting:**
- [ ] All shadows originate from the same sun angle
- [ ] Shadow softness matches stated sky condition
- [ ] Sky color, shadow angle, and highlight intensity match the stated time of day
- [ ] Ambient occlusion is present in contact areas

**Structure:**
- [ ] All cantilevered and spanning elements have visible support logic
- [ ] Column sizes are proportional to their spans
- [ ] No floating masses without a visible structural strategy

**Site Context:**
- [ ] Adjacent buildings and streetscape are correctly scaled
- [ ] Trees and landscape are climatically appropriate and correctly scaled
- [ ] Entourage casts correct shadows at the correct angle
- [ ] Ground plane meets building in a topographically plausible way

**Drawings:**
- [ ] Line weights are differentiated by cut, visible, and background
- [ ] Scale bar present and legible
- [ ] Diagrams communicate their message without requiring label reading
