# Legion Factory Interior Material Language & Master Material Setup

**A comprehensive art direction consultation for modular, prefab factory structures on planetary surfaces**

---

## Executive Summary

Legion's factory interiors must feel **engineered and prefabricated**, not organic. These are structures that Bob clones assemble on alien worlds—modular, functional, built with industrial intent. The visual language prioritizes:

- **Readable scale**: Assembly lines, machinery, catwalks visible at distance.
- **Material authenticity**: Real metals, composites, and concrete—not fantasy shine.
- **Modular visibility**: Seams, bolted connections, panel divisions emphasize assembly.
- **Functional lighting**: Overhead industrial rigs, machinery glow, operational accents.
- **Durability narrative**: Weathering shows age, but structures remain operational.

This approach ensures player readability, respects Legion's NASA-industrial hard sci-fi identity, and provides a solid foundation for UE5 master material implementation.

---

## I. Material Language for Factory Interiors

### A. Surface Finishes & What They Feel Like

Factory surfaces fall into three primary categories:

#### **1. Structural Steel (Load-Bearing, Support Frames)**

**The Feel**: Industrial backbone. Honest engineering. Heavy, immovable, functional.

**Visual Characteristics**:
- **Albedo**: Mid-gray (RGB ~0.48–0.52). Slightly warm tone (steel ~0.50, 0.48, 0.45) to avoid cold plasticity.
- **Roughness**: Brushed finish ≈ 0.35–0.45. Not mirror-polished; shows directional grain from manufacturing.
- **Metallic**: 1.0 (pure metal).
- **Normal Detail**: Macro = directional brush marks (parallel lines every 0.5–1m). Micro = fine tool marks and micro-scratches.
- **Weathering**: Edges and exposed corners show oxidation: roughness increases to 0.6–0.7, color desaturates toward brown (RGB ~0.50, 0.45, 0.40).

**Where It Appears**:
- Main support beams (I-beams, H-beams).
- Floor grating frames.
- Catwalk railings.
- Machinery housings (structural backbone, not fine details).

**Why This Works**: Brushed steel reads as "built by humans, worn by use" without looking rusty or derelict. It's the foundational material players trust to hold them up.

---

#### **2. Composite Panel Walls (Modular Enclosure)**

**The Feel**: Durable, lightweight, prefabricated. Industrial grace—functional elegance without unnecessary decoration.

**Visual Characteristics**:
- **Albedo**: Dark gray (RGB ~0.22–0.28). Slightly cooler than steel, emphasizing non-metallic character.
- **Roughness**: Matte finish ≈ 0.50–0.60. Slightly gloss on top of weave reduces it to 0.40–0.50.
- **Metallic**: 0.0 (non-metal). Critical—composites are not metals.
- **Normal Detail**:
  - Macro = carbon weave pattern (regular diagonal grid, visible every 1–1.5m at typical gameplay distance).
  - Micro = fine micro-scratches and handling wear (0.1–0.2m scale detail).
- **Weathering**: Seam lines and panel edges show discoloration (slight RGB desaturation, roughness +0.1). Older factory sections show patina accumulation.

**Where It Appears**:
- Walls of factory modules.
- Interior ceiling panels (non-critical structural).
- Maintenance compartments.
- Ducting covers.

**Why This Works**: Carbon-weave composite reads as "space-grade material, engineered for weight savings." The visible weave confirms material authenticity. The dark color minimizes visual clutter in busy factory scenes.

---

#### **3. Anodized Aluminum Accent Panels (Functional Trim, Visual Breaks)**

**The Feel**: Clean, precise engineering. Where form meets function—detailing that's also structural.

**Visual Characteristics**:
- **Albedo**: Light gray (RGB ~0.55–0.65). Slightly cooler tone (aluminum ~0.58, 0.57, 0.55).
- **Roughness**: Polished-to-brushed ≈ 0.15–0.30. Slightly reflective, but not mirror-like.
- **Metallic**: 1.0 (pure metal, anodized aluminum).
- **Normal Detail**: Subtle grain (optional anisotropy for visual realism, but adds shader cost).
- **Weathering**: Minimal. Anodized surfaces resist corrosion. Worn edges show slightly higher roughness (0.35–0.45), color desaturation minimal.

**Where It Appears**:
- Panel trim and frame edges.
- Handrails and ladder rungs.
- Control panel bezels.
- Door frames.
- Accent stripes or functional dividing lines.

**Why This Works**: Aluminum is the "readable" metal—players instantly recognize it as a precision-finished material. It breaks up the visual monotony of dark composite walls and creates visual hierarchy without flashiness.

---

#### **4. Concrete Flooring (Regolith-Aggregate Base)**

**The Feel**: Durable, established, weathered by foot traffic. The ground beneath factories feels ancient—compacted regolith, impact-polished in high-traffic zones.

**Visual Characteristics**:
- **Albedo**: Neutral gray with slight warmth (RGB ~0.40–0.48). Particle aggregate visible in normal detail.
- **Roughness**: High ≈ 0.75–0.85. Powdery, diffuse. High-traffic zones (assembly line crossings) show polish: roughness drops to 0.60–0.70.
- **Metallic**: 0.0 (non-metal).
- **Normal Detail**:
  - Macro = aggregate grain (Voronoi noise at 1–2cm scale, giving pebble-like texture).
  - Micro = micro-grain from fine particle impact.
- **Weathering**: Traffic wear shown via localized roughness reduction and subtle color darkening. Oil stains: very slight warm desaturation (RGB +0.02 red, -0.01 green/blue).

**Where It Appears**:
- Factory floor.
- Foundation/foundation slabs.
- High-traffic corridor crossings.

**Why This Works**: Concrete flooring anchors the factory to its planetary setting. It feels solid, timeworn, and operational. The visible grain confirms it's a real material, not a generic surface.

---

#### **5. Steel Grating & Perforated Metal (Catwalks, Machine Guards)**

**The Feel**: Open-plan, modular, protective without obstruction. You can see through it—visual honesty.

**Visual Characteristics**:
- **Albedo**: Mid-gray matching structural steel (RGB ~0.48–0.52).
- **Roughness**: Brushed ≈ 0.40–0.50.
- **Metallic**: 1.0 (pure metal).
- **Normal Detail**: The geometry handles the grating pattern (not fully from normal map). Normal provides micro-grain/wear.
- **Weathering**: Rust at contact points (where grating meets support beams). Use decals or procedural rust patches.

**Where It Appears**:
- Catwalk flooring.
- Machine guards and protective screens.
- Ventilation louvers.

**Why This Works**: Grating conveys "access"—players can see down, through, and beyond. It's the workhorse metal of industrial spaces.

---

### B. Metal Finishes: Detailed Specification

| Metal Type | Albedo (RGB) | Roughness (Base) | Roughness (Worn) | Metallic | Normal | Usage |
|---|---|---|---|---|---|---|
| **Structural Steel** | 0.50, 0.48, 0.45 | 0.35–0.45 | 0.60–0.75 | 1.0 | Directional brush, micro-scratches | Beams, frames, support |
| **Anodized Aluminum** | 0.58, 0.57, 0.55 | 0.15–0.30 | 0.35–0.45 | 1.0 | Subtle grain (optional anisotropy) | Trim, accents, handrails |
| **Stainless Steel** | 0.55, 0.54, 0.52 | 0.10–0.25 | 0.40–0.55 | 1.0 | Mirror-polished to brushed | High-corrosion zones (cooling radiators) |
| **Weathered/Oxidized Steel** | 0.45, 0.40, 0.35 | 0.70–0.85 | 1.0 | 0.7–0.8 (edges) | Rust texture, corrosion pits | Aged structural elements, worn machinery |

---

### C. Non-Metal Surfaces

#### **Rubber & Polymer Handles, Gaskets**

**Albedo**: Deep gray-black (RGB ~0.12–0.18).
**Roughness**: Matte ≈ 0.80–0.95.
**Metallic**: 0.0.
**Normal**: Slight grain from manufacturing.
**Location**: Grip surfaces, door seals, vibration dampers.

#### **Glass (Windows, Viewports, Display Panels)**

**Albedo**: Tinted pale blue or amber (aerospace tint).
**Roughness**: Crystal-clear ≈ 0.02–0.05.
**Metallic**: 0.0 (dielectric).
**IOR**: 1.5 (realistic refraction, UE5 Fresnel node).
**Emissive** (optional): Slight glow if displaying operational data.
**Location**: Observation windows, machinery view ports, control panel displays.

---

## II. Lighting Strategy for Factory Spaces

Factory interiors require **functional, high-contrast lighting** that reads at distance and reinforces the industrial mood.

### A. Overhead Industrial Rigs (Primary Lighting)

**The Mood**: Harsh, efficient, business-like.

**Technical Setup**:
- **Color Temperature**: Neutral to cool white (5000–5500K). Slightly blue cast to emphasize alien world context.
- **Intensity**: High contrast. Key light 2.0–3.0 lux (bright), shadows 0.1–0.3 lux (deep).
- **Direction**: Directional light from ceiling fixtures, angled slightly to create readable form shadows on machinery.
- **Shadow Type**: Dynamic shadows on machinery (moving robot arms, conveyor elements). Baked shadows on static architecture for performance.

**Lumen Consideration**:
- Keep emissive ceiling rigs subtle (Emissive ~0.6–0.8, not maxed). Avoid harsh bloom beyond fixture bounds.
- Let Lumen GI bounce cool light into shadows—creates visual depth.

**Implementation in UE5**:
```
Light Properties:
  Type: Directional
  Intensity: 2.5
  Color: RGB(245, 245, 255) [5500K, slight blue]
  Attenuation Radius: 10,000 (large factory space)
  Source Angle: 5–10 degrees (slight softness, not razor-sharp shadows)
  Cast Dynamic Shadows: TRUE on machinery
  Cast Static Shadows: TRUE on walls/ceiling
```

### B. Machinery Operational Glow (Accent Lighting)

**The Mood**: "This thing is working."

**Technical Setup**:
- **Color**: Functional accent colors per system:
  - Power systems: Amber/yellow-green (RGB 0.9, 0.8, 0.2).
  - Cooling loops: Cool cyan (RGB 0.1, 0.8, 0.9).
  - Fabrication lasers: Bright red (RGB 1.0, 0.1, 0.2) with slight flicker for dynamism.
- **Intensity**: Moderate. 0.5–1.5 lux local glow. Emissive material on machinery face ≈ 2.0–4.0 base intensity.
- **Type**: Point lights clustered near machinery, or emissive materials on machinery bodies + Lumen GI bounce.

**Lumen Consideration**:
- Emissive machinery is Lumen-lit. Warm accent colors bounce warm light; cool colors bounce cool light—visual feedback on system status.

### C. Corridor & Catwalk Navigation Lighting

**The Mood**: "Follow the light. Safe passage."

**Technical Setup**:
- **Linear Strip Lights**: Ceiling or wall-edge-mounted, continuous lines.
- **Color**: Neutral white (4500K), slightly cool.
- **Intensity**: 0.5–1.0 lux (navigational, not overwhelming).
- **Directionality**: Emissive channel on corridor ceiling/wall trim (RGB 0.7, 0.7, 0.7, Emissive 1.0–2.0). Creates visual directional cues.

### D. Emergency/Alert States (Narrative Overlay)

**The Mood**: "Something is wrong. Pay attention."

**Technical Setup**:
- **Red Wash**: Post-process filter or localized red-tinted lights (RGB 1.0, 0.2, 0.2).
- **Flicker**: Pulsing emissive on emergency lights. Use Panner node on emissive to create temporal variation.
- **Application**: Triggered by game state (reactor failure, hull breach, system malfunction). Not permanent factory aesthetic.

---

## III. Master Materials in UE5: Architecture & Implementation

This section provides a **modular master material system** that lets artists instantiate variations without recompiling shaders.

### A. Core Philosophy: One Master, Many Instances

Instead of creating individual materials for each surface, we build **4 core master materials** and spawn 8–12 instances per master.

```
Masters (Base):
├─ M_Steel_Master
├─ M_Composite_Master
├─ M_Aluminum_Master
└─ M_Concrete_Master

Instances (Variation):
├─ M_Steel_Polished
├─ M_Steel_Brushed
├─ M_Steel_Weathered
├─ M_Steel_Heavy_Rust
├─ M_Composite_NewPanel
├─ M_Composite_Aged
├─ M_Composite_Worn_Seam
└─ ... (etc., per master)
```

**Benefit**: Change base shader logic once (e.g., improve normal blending) → all instances update automatically.

---

### B. Master Material Structure: M_Steel_Master

**Inputs (Scalar Parameters)**:
- `MetallicValue` (default 1.0) — pure metal for structural steel.
- `RoughnessBase` (default 0.40) — brushed finish baseline.
- `WearAmount` (default 0.3) — procedural weathering intensity (0–1).
- `DetailStrength` (default 0.5) — fine grain visibility.

**Inputs (Vector Parameters)**:
- `BaseColor_Tint` (default RGB 0.50, 0.48, 0.45) — steel tone adjustments.
- `RustColor` (default RGB 0.55, 0.40, 0.30) — oxidation tone (warm brown).
- `WeatheringColor` (default RGB 0.48, 0.45, 0.40) — desaturation tone.

**Texture Slots**:
- `T_Steel_Albedo` (2K, sRGB=TRUE) — base steel color, neutral lighting.
- `T_Steel_Normal_Macro` (2K, sRGB=FALSE) — directional brush marks, large-scale detail.
- `T_Steel_Normal_Micro` (1K, sRGB=FALSE) — micro-scratches, fine grain (will be scaled ×4–8).
- `T_Steel_Roughness` (1K, sRGB=FALSE, grayscale) — roughness variation map.
- `T_Weathering_Noise` (1K, sRGB=FALSE) — Voronoi/Perlin for rust distribution (procedural OR baked).

**Shader Graph Structure**:

```
[T_Steel_Albedo]
  → [Desaturate: 0.3]
  → [Multiply with BaseColor_Tint]
  → [Lerp toward RustColor, using WearAmount × WeatheringNoise]
  → [Output: Base Color]

[T_Steel_Normal_Macro]
  → [Normalize]
  → [Blend with T_Steel_Normal_Micro scaled ×6 using DetailStrength]
  → [Output: Normal]

[T_Steel_Roughness]
  → [Multiply with RoughnessBase]
  → [Add (WearAmount × WeatheringNoise × 0.3)]
  → [Add edge wear (Fresnel-based roughness increase)]
  → [Clamp 0–1]
  → [Output: Roughness]

[Metallic]:
  → [Output: MetallicValue (1.0)]

[AO (Baked)]:
  → [Multiply with Base Color darkening]
```

**Key Nodes**:
- **Normalize**: Applied after normal blending to preserve detail.
- **Lerp**: Smoothly blend between steel and rust as WearAmount increases.
- **Fresnel**: Detect surface edges (camera-facing). Increase roughness at edges (Fresnel output × 0.2 + base).
- **Voronoi/Perlin (Procedural)**: Generate WeatheringNoise at 2m scale for non-repeating rust distribution.

---

### C. Master Material Structure: M_Composite_Master

**Inputs (Scalar Parameters)**:
- `MetallicValue` (default 0.0) — non-metal.
- `RoughnessBase` (default 0.50) — matte weave finish.
- `WeaveScale` (default 1.0) — adjust visible weave pattern size.
- `WearAmount` (default 0.2) — seam/edge weathering.
- `DetailStrength` (default 0.6) — micro-scratch visibility.

**Inputs (Vector Parameters)**:
- `BaseColor_Tint` (default RGB 0.24, 0.24, 0.26) — carbon gray.
- `SeamColor` (default RGB 0.18, 0.18, 0.20) — darkened color at seams.

**Texture Slots**:
- `T_Composite_Albedo` (2K, sRGB=TRUE) — neutral gray weave base.
- `T_Composite_Normal_Weave` (2K, sRGB=FALSE) — regular diagonal weave pattern (critical for material authenticity).
- `T_Composite_Normal_Micro` (1K, sRGB=FALSE) — micro-scratches, handling wear (scaled ×4).
- `T_Composite_Roughness` (1K, sRGB=FALSE) — slight gloss variation in weave.
- `T_Seam_Mask` (1K, sRGB=FALSE) — grayscale mask indicating seam locations (for edge darkening).

**Shader Graph Structure**:

```
[T_Composite_Albedo]
  → [Multiply with BaseColor_Tint]
  → [Lerp toward SeamColor using T_Seam_Mask × WearAmount]
  → [Output: Base Color]

[T_Composite_Normal_Weave scaled by WeaveScale]
  → [Normalize]
  → [Blend with T_Composite_Normal_Micro × DetailStrength]
  → [Output: Normal]

[T_Composite_Roughness]
  → [Multiply with RoughnessBase]
  → [Clamp 0–1]
  → [Output: Roughness]

[Metallic]:
  → [Output: 0.0]

[AO (Baked)]:
  → [Multiply with Base Color]
```

**Key Pattern**:
- Weave detail is **macro-critical**. Composite without visible weave reads as plastic, not engineering material.
- Seam mask darkening reinforces the "assembled from panels" aesthetic without complex geometry.

---

### D. Master Material Structure: M_Aluminum_Master

**Inputs (Scalar Parameters)**:
- `MetallicValue` (default 1.0) — pure metal.
- `RoughnessBase` (default 0.20) — polished-to-brushed.
- `AnisotropyStrength` (optional, default 0.0) — directional grain intensity (adds shader cost).

**Inputs (Vector Parameters)**:
- `BaseColor_Tint` (default RGB 0.58, 0.57, 0.55) — aluminum tone.

**Texture Slots**:
- `T_Aluminum_Normal` (1K, sRGB=FALSE) — subtle directional grain OR simple micro-detail.

**Shader Graph Structure**:

```
[Base Color]:
  → [Output: BaseColor_Tint (minimal texture variation)]

[T_Aluminum_Normal]:
  → [Normalize]
  → [Output: Normal]

[Roughness]:
  → [Output: RoughnessBase (simple scalar, not map-driven)]

[Metallic]:
  → [Output: 1.0]
```

**Simplicity Intentional**: Aluminum is accent trim—doesn't need complex weathering. Keeps shader simple, performance-friendly.

---

### E. Master Material Structure: M_Concrete_Master

**Inputs (Scalar Parameters)**:
- `MetallicValue` (default 0.0) — non-metal.
- `RoughnessBase` (default 0.80) — powdery aggregate.
- `AggregateScale` (default 1.0) — pebble grain size multiplier.
- `TrafficWearAmount` (default 0.3) — foot-traffic polish (roughness reduction in high-use areas).
- `DetailStrength` (default 0.7) — fine particle detail.

**Inputs (Vector Parameters)**:
- `BaseColor_Tint` (default RGB 0.44, 0.44, 0.42) — neutral concrete gray.
- `OilStainColor` (default RGB 0.43, 0.40, 0.38) — slight warm desaturation for worn zones.

**Texture Slots**:
- `T_Concrete_Albedo` (2K, sRGB=TRUE) — subtle color variation, aggregate visible.
- `T_Concrete_Normal_Aggregate` (2K, sRGB=FALSE) — Voronoi-based 1–2cm pebble grain.
- `T_Concrete_Normal_Micro` (1K, sRGB=FALSE) — fine particle impact texture.
- `T_Concrete_Roughness` (1K, sRGB=FALSE) — aggregate variation.
- `T_TrafficWear_Mask` (1K, sRGB=FALSE) — grayscale indicating high-traffic pathways.

**Shader Graph Structure**:

```
[T_Concrete_Albedo]
  → [Multiply with BaseColor_Tint]
  → [Lerp toward OilStainColor using T_TrafficWear_Mask × TrafficWearAmount]
  → [Output: Base Color]

[T_Concrete_Normal_Aggregate scaled by AggregateScale]
  → [Normalize]
  → [Blend with T_Concrete_Normal_Micro × DetailStrength]
  → [Output: Normal]

[T_Concrete_Roughness]
  → [Multiply with RoughnessBase]
  → [Subtract (T_TrafficWear_Mask × TrafficWearAmount × 0.15)]
  → [Clamp 0.60–1.0]
  → [Output: Roughness]

[Metallic]:
  → [Output: 0.0]

[AO (Baked)]:
  → [Multiply with diffuse]
```

**Key Pattern**:
- Traffic wear is driven by a **placement-specific mask** (hand-painted or procedurally baked per factory region).
- Roughness reduction in worn zones (travel pathways, assembly line crossings) conveys heavy use without geometric alteration.

---

## IV. Creating Instances: Practical Workflow

### A. Instance: M_Steel_Brushed (Factory Frame)

**Parent**: M_Steel_Master

**Parameter Overrides**:
- `RoughnessBase` = 0.40 (slightly more reflective than weathered).
- `WearAmount` = 0.15 (minimal weathering).
- `BaseColor_Tint` = (0.50, 0.48, 0.45) [no change—classic steel].

**Use**: Main structural beams, catwalk frames, unworn machinery housings.

---

### B. Instance: M_Steel_Weathered (Aged Factory Section)

**Parent**: M_Steel_Master

**Parameter Overrides**:
- `RoughnessBase` = 0.45.
- `WearAmount` = 0.60 (significant oxidation).
- `BaseColor_Tint` = (0.48, 0.44, 0.40) [slight desaturation toward brown].

**Use**: Factory sections that have operated for years. Edges of machinery, exposed to elements.

---

### C. Instance: M_Composite_New (Fresh Module)

**Parent**: M_Composite_Master

**Parameter Overrides**:
- `RoughnessBase` = 0.48.
- `WearAmount` = 0.05 (fresh panel, minimal wear).
- `WeaveScale` = 1.0.
- `BaseColor_Tint` = (0.26, 0.26, 0.28) [slightly lighter—factory-fresh composite].

**Use**: Recently added factory modules. Expansion areas. Visual contrast with older factory core.

---

### D. Instance: M_Concrete_Factory_Floor (Assembly Line)

**Parent**: M_Concrete_Master

**Parameter Overrides**:
- `RoughnessBase` = 0.78.
- `TrafficWearAmount` = 0.50 (heavy foot traffic).
- `BaseColor_Tint` = (0.42, 0.42, 0.40).
- **T_TrafficWear_Mask**: Hand-painted mask showing high-traffic crossing routes, conveyor-adjacent paths.

**Use**: Factory floor beneath assembly lines, between machinery, major thoroughfares.

---

## V. Performance & Optimization

### A. Nanite Considerations

Large factory walls and flooring may use **Nanite geometry**. Keep master materials simple on Nanite:

- **Texture Sample Count**: 2–3 (Albedo + Normal + optional Roughness). Avoid >4 samples on warehouse-scale Nanite.
- **Math Nodes**: Minimize Normalize calls. One per normal blend, not per layer.
- **Vertex Color Variation**: Use Nanite vertex colors (RGB = wear tint, A = detail scale) to vary instances without texture samples.

**Example**:
```
Albedo = Lerp(BaseColor, WornColor, VertexColor.R)
Roughness = Lerp(RoughnessBase, RoughnessWorn, VertexColor.R)
```

This adds variation to a single Nanite mesh using stored per-vertex data. No additional texture memory.

### B. Texture Memory & Compression

- **Albedo**: sRGB, DXT1 (no alpha). ~1.3 MB for 2K.
- **Normal**: Linear, BC5 (preserves detail). ~1.3 MB for 2K.
- **Roughness/AO**: Linear, grayscale, BC4. ~0.5 MB for 1K.

**Total per master**: ~3–4 MB. **4 masters = ~12–16 MB**—negligible modern budgets.

### C. Instance Overhead

Instances have minimal overhead (parameter values only, no new texture memory). Creating 50 instances from 4 masters is free relative to creating 50 unique materials.

---

## VI. Decal System for Variation & Wear

Decals are **cheap detail** applied on top of master materials. Use them for:

- Wear patterns (edge fadeouts, seam darkening).
- Logos and faction markings.
- Graffiti, burn marks, stains.
- Rust patches (edges, corners, contact points).
- Hazard tape (yellow/black stripes at doors).

**Decal Material Pattern**:

```
Decal Master Material:
  [Decal Texture (sRGB Albedo + Normal)]
  → [Multiply by Decal Mask (grayscale falloff)]
  → [Blend with Base Material using Decal Blend Mode]
```

**Example Rust Decal**:
- Albedo: Rust-orange gradient (RGB 0.60, 0.35, 0.20).
- Normal: Corrosion pits and edges.
- Mask: Soft radial falloff (center full opacity, edges transparent).
- Placement: Corner edges of structural steel beams, machinery seams.

Decals keep base materials unchanged while adding visual storytelling and wear character.

---

## VII. Lighting Material Handoff: Emissive Guidance

### A. Emissive Machinery

**Pattern**: Machinery operational lights emit color that Lumen respects.

```
Power System: Emissive color (0.8, 0.6, 0.1) [warm amber], intensity 2.0–3.0
Cooling Loop: Emissive color (0.1, 0.9, 0.9) [cool cyan], intensity 1.5–2.0
Fabrication Laser: Emissive color (1.0, 0.1, 0.2) [red], intensity 3.0–4.0 (red is dim relative to other channels)
```

**Note**: Emissive intensity >1.0 is valid for bright surfaces. Cap at 5.0 to avoid harsh bloom.

### B. Emissive in Master Materials

Add an optional **EmissiveColor** and **EmissiveIntensity** parameter to each master:

```
M_Steel_Master additions:
  Scalar: EmissiveIntensity (default 0.0)
  Vector: EmissiveColor (default RGB 0, 0, 0)

Graph:
  [If EmissiveIntensity > 0]
    → [Emissive = EmissiveColor × EmissiveIntensity]
  [Else]
    → [Emissive = Black (0)]
```

This allows instances to glow without duplicating masters. Use for accent panels that light machinery.

---

## VIII. Art Brief Summary: Deliverables to Environment Artist

### Steel Structural Elements

**Material**: M_Steel_Brushed (or _Weathered for aged sections)
**Tiling**: 2m seams visible, 0.5m brushing grain visible
**Placement**: Load-bearing beams, supports, main catwalk frames
**Visual Intent**: Industrial backbone—worn but operational

### Composite Walls

**Material**: M_Composite_NewPanel (fresh modules) or M_Composite_Aged (core sections)
**Tiling**: 1m weave visible, 0.2m micro-scratches
**Placement**: Interior walls, ceiling panels, modular enclosure
**Visual Intent**: Lightweight engineering—shows assembly history via seam variation

### Aluminum Trim

**Material**: M_Aluminum_Master
**Tiling**: 0.5m accent stripes, subtle grain
**Placement**: Frame edges, handrails, panel bezels, door frames
**Visual Intent**: Precision finishing—breaks up monotone composite

### Concrete Floor

**Material**: M_Concrete_Factory_Floor (with traffic wear mask)
**Tiling**: 1–2m pebble grain, 0.3m micro-grain
**Placement**: Factory floor, assembly line base, foundation slabs
**Visual Intent**: Compacted regolith—foot traffic polish shows heavy use

### Lighting Scheme

**Overhead Rigs**: Directional light 5500K, high contrast, dynamic shadows on machinery
**Machinery Accent**: Point lights + emissive materials (amber for power, cyan for cooling, red for fabrication)
**Navigation**: Wall-edge strip lights, neutral white 4500K, 0.5–1.0 lux
**Emergency**: Pulsing red overlay, reserved for alert states

---

## IX. Troubleshooting & Common Adjustments

### "Factory Feels Too Dark"

- Increase overhead light intensity 2.5 → 3.0–3.5.
- Add secondary fill light (softer directional) at 30% intensity for shadow detail.
- Check emissive machinery—if it's too dim, boost EmissiveIntensity.

### "Composite Walls Look Flat/Plastic"

- Verify T_Composite_Normal_Weave is loaded and normalized.
- Increase DetailStrength parameter 0.6 → 0.8 to show micro-scratches.
- Add slight color variation: desaturate albedo by 5–10% to add visual depth.

### "Steel Feels Too Shiny"

- Reduce RoughnessBase 0.40 → 0.45–0.50 for more matte finish.
- Verify MetallicValue = 1.0 (not accidentally 0.5).

### "Weathering Looks Blotchy"

- Check WeatheringNoise scale. If Voronoi is too coarse (scale >5m), reduce to 2–3m.
- Verify WearAmount parameter is reasonable (0.2–0.6 for most cases).
- Ensure WeatheringColor (desaturation target) is neutral gray (RGB ~0.45, 0.42, 0.40), not saturated.

### "Concrete Floor Seems Patchy"

- Verify T_TrafficWear_Mask is smoothly gradated (not hard edges).
- Ensure mask is baked per factory region (masks don't tile—they're placement-specific).
- If wear is too strong, reduce TrafficWearAmount 0.50 → 0.30–0.40.

---

## X. Summary: The Factory Material Language

Legion's factory interiors tell a **story of engineering pragmatism**:

| Element | Material | Feel | Gameplay Signal |
|---|---|---|---|
| **Structure** | Brushed steel | Honest, worn-in, trustworthy | "This holds me up." |
| **Enclosure** | Carbon composite | Lightweight, precision-engineered | "This was assembled, not built." |
| **Accents** | Anodized aluminum | Clean, professional, functional | "This is important detail." |
| **Ground** | Concrete regolith | Solid, ancient, compacted | "This is established." |
| **Lighting** | Cool overhead rigs + warm machinery glow | Functional efficiency + operational status | "I know what's running. I know where to go." |

The material language respects **hard sci-fi authenticity**: real metals, visible assembly, functional wear. The master material system scales these principles across dozens of instances without shader overhead. Decals and procedural weathering add character without geometric complexity.

---

## Next Steps

1. **Import base textures** (Steel, Composite, Concrete) into UE5 with correct sRGB/Linear settings.
2. **Build the 4 masters** (M_Steel, M_Composite, M_Aluminum, M_Concrete) following the shader graph structures provided.
3. **Create 2–3 instances per master** for variation (new, aged, weathered).
4. **Set up lighting rigs** in test factory level using Directional + Point lights per specifications.
5. **Validate with placeholder geometry** (simple boxes, walls, floor) before hero asset creation.
6. **Iterate on parameters** per factory region—older core sections use _Weathered instances; expansion areas use _New.

This approach balances **visual fidelity, technical performance, and scalability** for Legion's modular factory aesthetic.
