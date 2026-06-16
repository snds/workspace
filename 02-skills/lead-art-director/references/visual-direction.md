# Visual Direction & Style Guide

## Legion's Visual DNA

Legion draws visual language from four core reference films. Here's what to extract from each:

**The Martian (Ridley Scott, 2015)**
- NASA pragmatism: form follows function. Solar panels are unglamorous but beautiful in their honesty.
- Dust storms and atmospheric haze—volumetric fog as mood-maker, not obstacle.
- Hab module warmth: interior spaces feel lived-in, jury-rigged, survivor mentality.
- *Take*: Functional simplicity, warm interiors, documentary realism in engineering.

**Project Hail Mary (Andy Weir aesthetic)**
- Extreme isolation made beautiful. Loneliness in wide shots.
- Practical problem-solving design: "if it's stupid but it works, it works."
- Material honesty: duct tape, 3D-printed parts, visible repair history.
- *Take*: Visible wear, improvisation, the romance of surviving alone in space.

**The Expanse (TV series, Alcon Entertainment)**
- Lived-in industrial design. Ships are workspaces, not showrooms.
- Faction visual identity through logos and panel colors, not material differences.
- Realistic mass/weight—structures sag, bend, show stress.
- Strong lighting: contrast between lit and shadowed areas creates mood.
- *Take*: Visual factions, industrial wear, dramatic lighting, weight and mass feel real.

**Oblivion (Joseph Kosinski, 2013)**
- Clean architecture, white and silver palette, geometric forms.
- Glow and light as primary visual storytelling (bioluminescence on structures).
- Futuristic but still grounded (not impossible physics).
- Minimalist interior design: clutter-free, purpose-built spaces.
- *Take*: White/silver palette baseline, architectural minimalism, light as narrative.

## Color Strategy

**Dominant Palette**:
- Titanium Gray (RGB 0.45, 0.45, 0.45): Hull plating, primary structure
- Deep Carbon (RGB 0.15, 0.15, 0.15): Shadows, interior walls, void contrast
- Anodized Silver (RGB 0.75, 0.75, 0.75): Trim, highlight, wear-resistant surfaces
- Concrete Beige (RGB 0.55, 0.50, 0.45): Terrain aggregate, regolith, industrial flooring

**Accent Palette** (Functional, Not Decorative):
- Warning Red (RGB 0.8, 0.1, 0.1): Emergency systems, alert status, danger zones
- System Green (RGB 0.1, 0.7, 0.2): Operational, power active, safe status
- Operational Blue (RGB 0.1, 0.5, 0.8): Information, diagnostics, active systems
- Alert Amber (RGB 0.9, 0.7, 0.0): Caution, degraded systems, maintenance needed

**Faction Color Differentiation**:
- Colonial Authority: Blue trim, official logos, bureaucratic precision
- Free Collective: Red/Orange accents, worn aesthetics, DIY visible repairs
- Synthetic Ascendant: Cyan/white cold palette, geometric logos, sterile precision
- Terrestrial Union: Green/brown earth tones, organic integration, heritage signage

*Rule*: Never saturate accent colors. Accents should read immediately but not oversaturate. RGB values above 0.8 should be rare.

## Typography

**Display Font** (HUD titles, menu headers): Eurostile or equivalent geometric sans-serif. Clean, futuristic, technical. All caps preferred. Tracking: +2%.

**Body Font** (UI text, data readouts): Monospaced OCR-A or Source Code Pro. Readability at 12px minimum. Kerning auto, no customization.

**Terminal/Display Font** (In-world screens, holograms): Monospaced, monochrome green or amber on dark background. Evokes 1980s CRT terminals but rendered at 4K. Use SF Mono or Courier Prime.

**Readability Hierarchy**:
1. Size: Title > Section > Body (2:1.5:1 ratio minimum)
2. Color: Full saturation for headers, slightly desaturated for body (95% alpha)
3. Weight: Bold titles, Regular body (no light weights—hard to read in dark spaces)

## Iconography

**Style Basis**: Engineering line drawings, technical blueprints, ISO symbols.

**Grid**: 24×24 baseline (2px line weight), scales to 32×32 at 2.5px for HUD.

**Metaphor**: Icons represent *function*, not ornament. A power icon is literally a power symbol (⊕). A drill is a stylized drill bit, not a cartoon.

**Construction**:
- Stroke-based, minimal fill
- 45° diagonals, 90° angles only (no curves unless functional—thruster glow is curved)
- 1px inside stroke to maintain shape integrity at small sizes

**Color**: Monochrome by default (accent color = function status). Context-specific fill only for status (green = active, red = offline).

## Mood Board Methodology

**Building a Mood Board**:

1. **Reference Collection**: Gather 20–30 images from architecture, industrial design, film stills. Save as 1:1 crops, 512px minimum.
2. **Dominant Mood**: What emotional note? Industrial calm, urgent survival, isolated beauty, discovery wonder?
3. **Palette Extraction**: Use eyedropper on 5–7 images, average to dominant + accent.
4. **Material Callout**: Annotate 3–4 key materials (metal type, surface finish, wear pattern).
5. **Lighting Diagram**: Sketch key light angle, key intensity (0–1 scale), fill light, backlight.
6. **Typography Sample**: Render 2–3 lines of game text in chosen fonts at game-scale sizes.

**Using a Mood Board**:
- Reference during material authoring (shows desired surface roughness, weathering)
- Share with programmers (lighting intensity targets, particle density)
- Use as approval gate (stakeholder sign-off before asset creation)

## Three.js Material Parameters from Visual References

When working from mood boards or visual references, translate directly to Three.js material parameters:

**NASA-Industrial Brushed Metal** (e.g., Ceres station hull panels):
- Reference: Photos of brushed aluminum aircraft skins, SpaceX Raptor nozzles
- Metalness: 0.95 (nearly pure metal)
- Roughness: 0.3–0.5 (directional brush marks visible)
- Normal map: Directional grain at ~2m scale, fine scratches at ~0.1m scale
- Example code: `material.metalness = 0.95; material.roughness = 0.4; material.normalScale.set(1.2, 1.2);`

**Carbon Composite Weave** (body panels, structural):
- Reference: Carbon fiber fabric, woven composites
- Metalness: 0.0 (pure non-metal)
- Roughness: 0.5–0.65 (weave texture visible, slight gloss)
- Normal map: Regular grid pattern (weave), ~1m visible repeat
- Example: `material.metalness = 0.0; material.roughness = 0.55; normalMap = weaveTexture;`

**Military-Grade Glass** (viewports, displays):
- Reference: Aerospace windscreens, tinted viewports
- Use MeshPhysicalMaterial for better glass rendering
- Roughness: 0.02–0.05 (nearly crystal clear)
- IOR: 1.5 (realistic refraction)
- Transmission: 1.0 (fully transparent)
- Thickness: Set on material for refraction thickness
- Example: `material.transmission = 1.0; material.roughness = 0.03; material.ior = 1.5;`

**Weathered/Corroded Metal** (aged equipment, worn panels):
- Reference: Rusty steel, oxidized aluminum, salt-spray corrosion
- Metalness: 0.7–0.8 (losing metallic quality due to oxidation)
- Roughness: 0.65–0.85 (highly scattered light)
- Albedo: Desaturated toward rust/brown tones on edges
- Normal map: Irregular corrosion texture, high-frequency detail
- Example: `material.metalness = 0.75; material.roughness = 0.75; albedoTint = lerpColor(gray, rustBrown, wearAmount);`

## Visual Consistency Checklist

Before art closure on any asset or space:

- [ ] **Material Consistency**: Metals use metalness ≥ 0.8, composites show fiber (normal map visible), glass is translucent (transmission 1.0)
- [ ] **Weathering**: High-touch surfaces show wear (roughness higher, color desaturated). Low-touch surfaces stay clean.
- [ ] **Faction Identity**: Logos, panel colors, or trim visible if asset is faction-specific
- [ ] **Lighting Readability**: Asset is readable in gameplay lighting. Test in target scene.
- [ ] **Scale Cues**: Proportions read correct size. Include reference prop (1m cube, human figure) if needed.
- [ ] **Normal Map Quality**: Surfaces don't look flat (normal != baked AO). Fine detail visible at gameplay distance.
- [ ] **Emissive Balance**: Screens/lights glow without blooming bleeding into surroundings. Test bloom at 1.0x target intensity.
- [ ] **Color Grading Stability**: Asset color stable under cool (3500K) and warm (5000K) color grades.
- [ ] **Modular Fit**: If tiling, seams invisible. If modular piece, UV mapping matches adjacent panels.
- [ ] **Performance**: Texture memory budget met (check WebGL texture limits).
