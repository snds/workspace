---
name: 3d-materials-shading
description: >
  PBR material authoring and shading design from the artist/designer perspective.
  Use this skill whenever the conversation touches: PBR, physically based rendering,
  metalness/roughness workflow, specular/gloss workflow, albedo, base color, normal map,
  roughness map, metalness map, ambient occlusion, emissive, opacity, height map,
  displacement, subsurface scattering, Substance Painter, Substance Designer, material
  authoring, smart materials, procedural materials, texel density, UV density, texture
  atlasing, trim sheets, channel packing, ORM map, texture compression, BC1, BC3, BC5,
  BC7, DXT, ASTC, KTX2, or any question about what a material is made of, how to author
  it, or how to optimize it. This skill covers material design and texture craft — not
  shader code (glsl-shader-architect), Three.js material classes (threejs-materials-master),
  or model topology (3d-modeling-fundamentals).
hub: lead-3d-designer
aliases: [3d-materials-shading]
tier: spoke
domain: design
prerequisites: [lead-3d-designer]
spec_version: "2.0"
---

# 3D Materials and Shading

Specialist lens for PBR material authoring and shading design. Part of the
`lead-3d-designer` skill network.

---

## Domain Boundary

This skill owns **material design decisions** — what maps to use, how to author them,
how to set PBR values, and how to optimize textures for delivery.

- **Shader code (GLSL/HLSL)** → `glsl-shader-architect`
- **Three.js material classes** → `threejs-materials-master`
- **Mesh construction, UV layouts** → `3d-modeling-fundamentals`
- **Lighting setup** → `3d-lighting-rendering`
- **Export, compression, engine import** → `3d-asset-pipeline`

---

## PBR Fundamentals

### What PBR Is

Physically based rendering (PBR) is a shading model that approximates real-world
light behavior. The key insight: light interacts with surfaces in physically
consistent ways — energy in equals energy out (energy conservation), and the way
light reflects depends on surface properties (roughness, metalness) that can be
parameterized.

PBR means materials look consistent across different lighting environments. A
PBR-correct metal looks like metal whether lit by an HDRI studio, outdoor noon
sun, or a candle — the same roughness and metalness values produce the right result
in all three contexts.

### The Two PBR Workflows

**Metalness/Roughness** — the standard for real-time / game engines:

| Map | What It Stores | Key Notes |
|-----|---------------|-----------|
| **Albedo / Base Color** | Surface color with NO lighting information | No baked AO, no hand-painted shadows. Pure color, pure albedo. sRGB space. |
| **Metalness** | Binary: 0.0 = dielectric, 1.0 = conductor | Real-world materials are one or the other. In-between values are for dirt, oxidation, and transition zones — not "slightly metallic" |
| **Roughness** | Microsurface — how scattered reflected light is | 0.0 = mirror; 1.0 = fully diffuse. Perceptually linear. Stored in linear space. |

**Specular/Gloss** — legacy, still common in older pipelines:

| Map | What It Stores |
|-----|---------------|
| **Diffuse** | Surface color (similar to Albedo) |
| **Specular** | Specular reflectance color — grayscale for metals, fixed values for dielectrics |
| **Glossiness** | Inverse of Roughness (1.0 = mirror, 0.0 = diffuse) |

Conversion: Roughness = 1 − Glossiness. Metalness workflow is preferred for new work.

### Energy Conservation

PBR enforces energy conservation: a surface cannot reflect more light than it
receives. A Roughness of 0.0 with Metalness of 1.0 = a perfect mirror. The shader
ensures reflected + diffuse ≤ incident light, automatically. The artist's job is
to set values that are plausible, not to calculate the math.

### PBR Value Reference

Common material values in metalness/roughness:

| Material | Albedo | Metalness | Roughness |
|----------|--------|-----------|-----------|
| Bare steel | 0.5–0.7 (gray) | 1.0 | 0.1–0.3 |
| Brushed aluminum | 0.75 (silver) | 1.0 | 0.4–0.6 |
| Oxidized copper | 0.15–0.35 (green) | 0.8 | 0.6–0.8 |
| Painted metal | Paint color | 0.0 | 0.3–0.6 (paint sheen) |
| Rough concrete | 0.3–0.5 (gray) | 0.0 | 0.85–0.95 |
| Polished marble | 0.6–0.8 (white) | 0.0 | 0.05–0.2 |
| Matte plastic | Plastic color | 0.0 | 0.7–0.9 |
| Glossy plastic | Plastic color | 0.0 | 0.1–0.3 |
| Fabric (matte) | Fabric color | 0.0 | 0.9–1.0 |
| Glass (opaque look) | 0.05–0.1 | 0.0 | 0.0–0.1 |
| Human skin | 0.3–0.6 (skin tone) | 0.0 | 0.4–0.65 |

---

## Texture Map Types

### Core Maps (All Real-Time Assets)

**Albedo / Base Color**
- RGB color. No lighting information whatsoever — no baked shadows, no AO, no
  specular glints painted by hand. PBR engines add lighting; the albedo provides
  only the surface color.
- sRGB color space (gamma-corrected for display). Import settings in engine must
  mark this as sRGB.
- Value range: Metal albedo can be 0.5–0.8. Dielectric albedo is rare below 0.04
  (very dark charcoal) or above 0.9 (fresh snow). Stay in plausible range.

**Normal Map**
- RGB encodes X/Y/Z surface normal deviation. Gives the illusion of high-poly detail
  on low-poly geometry.
- Two formats — **DirectX** (green channel inverted) vs. **OpenGL** (standard). Unreal
  Engine uses DirectX; Unity defaults to OpenGL; Substance Painter exports either.
  Mismatch causes the "inside-out" or "relief inverted" look. Check before delivery.
- Linear color space (not sRGB). Import settings in engine must mark as Normal or Linear.

**Roughness**
- Grayscale (single channel). 0.0 = mirror; 1.0 = fully diffuse.
- Linear color space.
- Common error: exporting from Substance with sRGB encoding causes roughness to be
  darker than intended, making materials look shinier than authored. Use linear export.

**Metalness**
- Grayscale (single channel). Binary in reality (0 or 1); in-between values for
  transitions (oxidation boundaries, dirt on metal).
- Linear color space.

**Ambient Occlusion (AO)**
- Grayscale. Encodes how much ambient light reaches each surface point. Pre-computed
  from the mesh geometry.
- Used as a multiplier on top of the albedo (multiply blend) or as a separate input
  to the material.
- Warning: AO is indirect lighting information. In strict PBR, baking AO into the
  albedo is incorrect (it prevents dynamic lighting from correctly illuminating the
  surface). Best practice: keep AO as a separate channel (part of the ORM pack), let
  the material blend it.

### Optional Maps

**Emissive**
- RGB color. Areas of the mesh that emit light independently of scene lighting. Used
  for screens, lights, glowing elements, engine trails.
- No upper bound — emissive values can exceed 1.0 for HDR bloom. Use with intent.

**Opacity / Alpha**
- Single channel. 0.0 = transparent; 1.0 = fully opaque.
- **Alpha Clip**: Pixels below a threshold are fully discarded (binary transparent).
  No sorting required. Use for foliage, chain-link fences, hard-edged holes.
  Performance-friendly.
- **Alpha Blend**: True transparency with sorting. Required for glass, water, VFX
  particles. Performance cost — transparent draw calls are sorted per frame. Use
  sparingly for large surfaces.

**Height / Displacement**
- Grayscale. 0.5 = flat; 0.0 = recessed; 1.0 = raised.
- Real-time use: Parallax Occlusion Mapping (POM) — simulates depth without geometry.
  Cost increases with surface complexity.
- Offline/bake use: actual mesh displacement at render time (Cycles, Arnold).

**Subsurface Scattering (SSS)**
- RGB or grayscale. Controls how much light passes through and scatters inside the
  surface. Critical for: skin, wax, translucent foliage, marble.
- Real-time approximation is an engine-specific shader feature. Not a universal PBR map.

---

## Substance Painter Workflow

### Project Setup

1. **Create a new project**: Import the mesh (FBX or OBJ). Set texture resolution
   (2048 or 4096 for hero assets). Set Document Resolution to match.
2. **UV padding**: Set padding to 16px at 2048, 32px at 4096. This prevents texture
   bleeding across UV islands at lower mip levels.
3. **Bake mesh maps** before painting. Painter's generators depend on baked data.

### Baking in Substance Painter

Bake these maps from the high-poly mesh:
- **Normal**: Surface normal deviation (the primary bake)
- **World Space Normal**: Used by position-based generators
- **AO**: Per-vertex ambient occlusion
- **Curvature**: Edge highlight/crevice data (used by most wear generators)
- **Position**: World-space position gradient (used by position generators for
  top/bottom/left/right variation)
- **Thickness**: How thin the mesh is at each point (SSS input)

**High-poly match**: Name the high-poly mesh with a `_high` suffix or use the
"by mesh name" matching option. Painter matches high-poly to low-poly by name — a
mismatch fails silently (bakes from the low-poly onto itself, producing a flat normal).

### Layer Stack Logic

Substance Painter uses a layer stack (like Photoshop, but 3D-aware):

- **Fill Layer**: Flat, uniform values across the entire mesh (base color, roughness,
  metalness). The foundation of any material.
- **Paint Layer**: Hand-painted strokes on the mesh surface. UV-space painting.
- **Smart Material**: A pre-configured layer stack saved as a preset. Applies a complex
  material setup (paint base + edge wear + dirt generator + scratches) in one step.

Stack order: Bottom layers are applied first; top layers override. A "dirt" layer sits
at the top (or behind transparency masking) to show through on top of the base material.

### Generator System

Generators are the power tool of Substance Painter — they create procedural masks
based on baked mesh data:

| Generator | Input | Use |
|-----------|-------|-----|
| **AO Generator** | AO map | Darken recessed areas (dirt accumulation in crevices) |
| **Curvature Generator** | Curvature map | Highlight edges (edge wear), darken corners |
| **Position Generator** | Position map | Vary by height (more dirt on bottom), by side (weathering direction) |
| **Dirt Generator** | AO + Curvature | Combined dirt simulation — the most-used generator |
| **Grunge Map** | — | Procedural noise overlaid as texture variation |

### Export Settings

Export presets per target engine:
- **Unreal Engine**: ORM pack (R=AO, G=Roughness, B=Metalness), Normal (DirectX)
- **Unity (HDRP)**: Mask Map (R=AO, G=Detail Mask, B=Metalness, A=Smoothness), Normal
  (OpenGL)
- **glTF / Three.js**: Separate maps per channel (or ORM pack); Normal (OpenGL)
- **Marmoset / Generic**: Full PBR set, OpenGL normals

Always verify the normal map format matches the target before delivery.

---

## Substance Designer

Substance Designer creates **tileable, procedural materials** using a node graph.
The output is a set of texture maps (not a mesh-specific paint).

### When to Use Designer vs. Painter

| Use Substance Painter | Use Substance Designer |
|----------------------|----------------------|
| Specific mesh with unique UV placement | Tileable, generic material (concrete, wood, fabric) |
| Hand-painted details, unique wear patterns | Procedural variation (drive parameters to get variants) |
| Hero asset texturing | Trim sheet and atlas material creation |
| Character and prop texturing | Environment material libraries |

### Key Node Types

- **Generators**: Noise, gradient, shape, pattern — create raw grayscale or color data
- **Filters**: Blur, warp, edge detect, histogram — transform existing data
- **Blends**: Combine two inputs (multiply, add, overlay, normal combine for normals)
- **Atomic nodes**: The fundamental primitives (uniform color, gradient, noise)

### Exposing Parameters

Parameters can be "exposed" to the material's interface — usable in engine as
material instance sliders. Expose: color tints, roughness bias, grunge intensity,
tile scale. This turns one material into a system that artists can customize in
engine without re-exporting.

---

## Texel Density

Texel density = how many pixels of texture cover one meter of surface. Consistent
texel density is a quality bar — objects that break the pattern look visually
inconsistent.

### Target Texel Density by Asset Type

| Asset Type | Target Texel Density |
|------------|---------------------|
| Hero character / hero prop (close view) | 1024 texels/meter |
| Mid-ground props and characters | 512 texels/meter |
| Background props | 256 texels/meter |
| Large architectural surfaces (floor, walls) | 512 texels/meter (tiled) |

### Texel Density Workflow

1. Use a UV checker texture (grid pattern, labeled squares) on the mesh
2. Check that the grid squares appear the same size across different UV islands
3. Scale UV islands up or down until texel density is consistent
4. For hero assets that share a texture sheet (atlas), all contributing meshes should
   match the atlas's texel density target

**Blender tool**: UV > Average Islands Scale (matches all islands to the same texel
density given their relative surface area).

---

## Material Optimization

### Texture Atlasing

Multiple assets sharing one texture sheet reduces draw calls. The engine renders all
objects using the same material in one draw call — switching textures costs performance.

**Atlas strategy**:
- Group assets that appear together in the scene (a furniture set, a weapon + holster)
- Pack their UV islands into a single texture atlas
- Balance island size by importance (hero prop gets more UV space than background fill)

### Trim Sheets

Trim sheets are single, tileable texture strips used for repeating architectural elements.
A 2048×2048 trim sheet might contain 8–12 horizontal strips:
- Stone wall top
- Stone wall middle
- Stone wall base
- Window sill
- Window frame top
- Metal grate panel
- etc.

Level geometry is UV-mapped to align with the appropriate trim strip. One material
handles the entire level's wall surfaces, dramatically reducing material count.

Trim sheets are the standard workflow for environment art in game development.

### Channel Packing (ORM Map)

Roughness, Metalness, and AO are all single-channel (grayscale) maps. They can be
packed into the three RGB channels of one texture, saving a texture slot:

**ORM Map** (Unreal Engine standard):
- **R channel**: Ambient Occlusion
- **G channel**: Roughness
- **B channel**: Metalness

This saves 2 texture samples per material — significant at scale.

Unity HDRP uses a different packing (Mask Map: R=AO, G=Detail, B=Metalness,
A=Smoothness/Glossiness).

### Texture Compression

| Format | Use | Bit Rate |
|--------|-----|---------|
| **BC1 / DXT1** | Opaque color (albedo without alpha) | 4 bpp |
| **BC3 / DXT5** | Color with alpha (opacity, particles) | 8 bpp |
| **BC4** | Single-channel grayscale (roughness, metalness when stored separately) | 4 bpp |
| **BC5** | Two-channel (normal map XY — Z is reconstructed in shader) | 8 bpp |
| **BC7** | High-quality color + optional alpha | 8 bpp |
| **ASTC** | Mobile (iOS, Android, consoles) — flexible block size | Variable |
| **KTX2 / Basis** | Web delivery — transcodes to GPU native at runtime | Variable |

Normal maps should always use BC5 (or BC3 if the engine doesn't support BC5 for normals).
BC5 stores X and Y; the shader reconstructs Z with `sqrt(1 - x² - y²)`, preserving
quality better than BC1/BC3's RGB storage.

---

## Cross-Links

- `glsl-shader-architect`: Custom shader code — vertex/fragment, GLSL, procedural
  effects; route there when moving from material design into shader programming
- `threejs-materials-master`: Three.js material implementation; route there when
  implementing materials in Three.js code
- `3d-asset-pipeline`: Texture export settings, compression pipeline, engine import

---

## Quality Checklist

Before delivering a material set:

- [ ] Albedo has no lighting information baked in (no hand-painted shadows, no AO)
- [ ] Normal map format matches target engine (DirectX vs. OpenGL)
- [ ] Normal and roughness maps exported in linear (not sRGB)
- [ ] No metalness values in the 0.1–0.9 range without a physical reason
- [ ] Roughness variation present — perfectly uniform roughness reads as plastic
- [ ] AO is a separate channel, not baked into albedo
- [ ] Texel density is consistent across all UV islands
- [ ] Texture resolution is power-of-two
- [ ] Channel packing applied (ORM or engine equivalent)
- [ ] Compression format set correctly per map type and platform target
- [ ] Material verified in the target engine (not just in Painter)
- [ ] No texture seams visible at normal viewing distance
