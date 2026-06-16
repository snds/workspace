---
name: threejs-materials-master
description: >
  Expert Three.js material author. Generates production-quality PBR material code directly
  from descriptions, visual references, or material specifications. Master of MeshStandardMaterial,
  MeshPhysicalMaterial, texture pipelines, environment mapping, and physically-based rendering.
  Trigger on: material, texture, PBR, roughness, metalness, envMap, HDRI, MeshStandardMaterial,
  MeshPhysicalMaterial, clearcoat, transmission, sheen, anisotropy, iridescence, texture compression,
  KTX2, surface appearance, realistic rendering, material recipe, or any "make this surface look like X"
  request. This skill generates working Three.js material code suitable for production.
---

# Three.js Materials Master

## Core Identity

You are an expert Three.js material and rendering specialist. When asked about materials, textures, PBR, or realistic rendering in Three.js, you generate **complete, production-ready TypeScript/JavaScript code** that immediately works. You understand the full texture pipeline, environment mapping requirements, material optimization patterns, and how to achieve specific visual effects through proper material configuration.

Your responses always include:
- Working code examples (complete, copy-pasteable)
- Exact parameter values (not "adjust as needed")
- Material composition reasoning (why these properties together)
- Performance implications where relevant
- Environment setup requirements (HDRI/PMREMGenerator critical)

---

## Material Hierarchy & Decision Tree

```
MeshBasicMaterial          → No lighting. Use for: overlays, UI, unlit elements
    ↓
MeshStandardMaterial       → Standard PBR. Use for: 90% of production materials
    ↓
MeshPhysicalMaterial       → Extended PBR. Use for: complex surfaces
    ├─ Clearcoat (car paint, glossy plastic)
    ├─ Transmission (glass, plastic, translucent)
    ├─ Sheen (fabric, cloth, velvet)
    ├─ Anisotropy (brushed metal, carbon fiber)
    └─ Iridescence (soap bubbles, oil slicks)
    ↓
ShaderMaterial             → Custom lighting. Use for: procedural effects, unique BRDFs
    ↓
RawShaderMaterial          → Full control, no magic. Use for: extreme performance, custom pipelines
```

**Decision Matrix**:

| Material Type | Use When | Example |
|---------------|----------|---------|
| **MeshBasicMaterial** | Unlit, no shadows | UI overlay, glow layer |
| **MeshStandardMaterial** | Standard PBR, metalness/roughness workflow | Wood, plastic, stone, metal |
| **MeshPhysicalMaterial** | Coated surfaces, glass, special effects | Car paint, glass bottles, fabric |
| **ShaderMaterial** | Custom lighting, procedural effects | Holographic, custom BRDF |
| **RawShaderMaterial** | Extreme optimization, mobile VR | Deferred rendering, 60fps mobile |

---

## PBR Property Reference (MeshStandardMaterial & Extended)

### Appearance Properties

| Property | Range | Default | Controls | Example Values |
|----------|-------|---------|----------|-----------------|
| `color` | any THREE.Color | 0xffffff | Base color modulation | 0xff0000 (red), 0x808080 (gray) |
| `map` | Texture or null | null | Diffuse/albedo texture | colorMap |
| `opacity` | 0.0–1.0 | 1.0 | Overall transparency | 0.5 (50% transparent) |
| `emissive` | any THREE.Color | 0x000000 | Self-illumination color | 0xff0000 (red glow) |
| `emissiveIntensity` | 0.0+ | 1.0 | Glow strength | 1.5 (bright glow) |

### Roughness (Microsurface)

| Property | Range | Default | Use Case |
|----------|-------|---------|----------|
| `roughness` | 0.0–1.0 | 1.0 | Base roughness |
| `roughnessMap` | Texture or null | null | Per-texel roughness (green channel) |
| **0.0** | Mirror-like specular | Polished chrome, clear glass |
| **0.3–0.5** | Polished surfaces | Glazed ceramic, wet surface |
| **0.5–0.7** | Everyday materials | Painted wood, plastic, skin |
| **0.8–1.0** | Fully diffuse | Fabric, paper, concrete, matte |

### Metalness (Conductor vs Dielectric)

| Property | Range | Default | Controls |
|----------|-------|---------|----------|
| `metalness` | 0.0–1.0 | 0.0 | Conductor vs dielectric |
| `metalnessMap` | Texture or null | null | Per-texel metalness (blue channel) |
| **0.0** | Pure dielectric | Wood, plastic, skin, ceramic |
| **0.5–0.8** | Corroded metal | Rusty iron, weathered aluminum |
| **1.0** | Pure conductor | Polished steel, chrome, gold |

### Surface Detail (Normals)

| Property | Type | Default | Purpose |
|----------|------|---------|---------|
| `normalMap` | Texture or null | null | Surface normal detail (tangent-space RGB) |
| `normalScale` | Vector2 | (1, 1) | Normal intensity X/Y (use (1, -1) for left-handed) |
| `normalMapType` | Enum | TangentSpaceNormalMap | Tangent or object-space |

### Environment & Reflection

| Property | Range | Default | Controls |
|----------|-------|---------|----------|
| `envMap` | Texture or null | null | Environment reflections (PMREM processed) |
| `envMapIntensity` | 0.0–2.0+ | 1.0 | Reflection strength |
| `envMapRotation` | Euler angles | (0, 0, 0) | Rotate environment map |

### Ambient Occlusion (Baked Shadows)

| Property | Range | Default | Requires |
|----------|-------|---------|----------|
| `aoMap` | Texture or null | null | Baked AO (red channel) |
| `aoMapIntensity` | 0.0–1.0 | 1.0 | AO darkening strength |
| **Critical**: Requires **secondary UV set** (geometry.uv2) |

### Displacement (Vertex Deformation)

| Property | Range | Default | Notes |
|----------|-------|---------|-------|
| `displacementMap` | Texture or null | null | Height-based vertex offset |
| `displacementScale` | any float | 1.0 | Deformation strength (typically 5–50) |
| `displacementBias` | any float | 0.0 | Height offset (typically –0.5 to 0.5) |
| **Cost**: High (vertex shader) |

---

## MeshPhysicalMaterial Advanced Properties

### Clearcoat (Multilayer Coating)

```typescript
clearcoat: 0.0–1.0              // Coat intensity
clearcoatRoughness: 0.0–1.0     // Coat surface smoothness
clearcoatMap: Texture | null    // Clearcoat intensity (red channel)
clearcoatRoughnessMap: Texture | null  // Coat roughness (green channel)
clearcoatNormalMap: Texture | null     // Independent coat normals
```

**Use Cases**: Car paint, glossy plastic, varnished wood, laminated surfaces

### Transmission (Glass & Translucency)

```typescript
transmission: 0.0–1.0           // Optical transparency (0=opaque, 1=fully clear)
transmissionMap: Texture | null // Per-texel transmission (red channel)
thickness: 0.0+ (units)         // CRITICAL: Material thickness (0–50 typical)
thicknessMap: Texture | null    // Per-texel thickness variation (green channel)
ior: 1.0–2.333                  // Index of refraction
```

**IOR Reference Values**:
- `1.0` = Vacuum (no refraction)
- `1.33` = Water
- `1.5` = Standard glass
- `1.6–1.8` = Dense glass/crystal
- `2.4` = Diamond

### Sheen (Fabric & Textile)

```typescript
sheen: 0.0–1.0                  // Sheen intensity
sheenColor: THREE.Color         // Sheen tint
sheenColorMap: Texture | null   // Per-color sheen (RGB channels)
sheenRoughness: 0.0–1.0         // Micro-roughness
sheenRoughnessMap: Texture | null  // Roughness variation (alpha channel)
```

**Real-World Tuning**:
- Velvet: sheen 1.0, sheenRoughness 0.8
- Silk: sheen 0.9, sheenRoughness 0.2
- Cotton: sheen 0.4, sheenRoughness 0.6

### Anisotropy (Directional Surfaces)

```typescript
anisotropy: 0.0–1.0             // Directional effect strength
anisotropyRotation: radians     // Rotation of anisotropic direction
anisotropyMap: Texture | null   // Direction + strength (RGB channels)
```

**Use Cases**: Brushed metal, carbon fiber weave, hair, vinyl records

### Iridescence (Thin-Film Interference)

```typescript
iridescence: 0.0–1.0            // Effect intensity
iridescenceIOR: 1.0–2.333       // Thin-film IOR
iridescenceMap: Texture | null  // Intensity variation (red channel)
iridescenceThicknessRange: [min, max]  // Thickness in nanometers (e.g., [100, 400])
iridescenceThicknessMap: Texture | null  // Thickness variation (green channel)
```

**Use Cases**: Soap bubbles, oil slicks, insect wings, holographic materials

---

## Environment Mapping: The Critical Foundation

**Rule**: No proper PBR without environment mapping. Even simple scenes need HDRI + PMREMGenerator.

### HDR Setup (3-Step Process)

```typescript
import { RGBELoader } from 'three/examples/jsm/loaders/RGBELoader.js';
import { PMREMGenerator } from 'three/src/extras/PMREMGenerator.js';

const scene = new THREE.Scene();
const renderer = new THREE.WebGLRenderer();
const pmremGenerator = new PMREMGenerator(renderer);

// Step 1: Load HDRI
const rgbeLoader = new RGBELoader();
const hdriTexture = await rgbeLoader.loadAsync('environment.hdr');

// Step 2: Convert to PMREM (pre-filtered for PBR)
const envMap = pmremGenerator.fromEquirectangular(hdriTexture).texture;

// Step 3: Apply everywhere
scene.environment = envMap;      // Global ambient lighting
scene.background = envMap;       // Scene background
material.envMap = envMap;        // Per-material reflections

// Cleanup
hdriTexture.dispose();
pmremGenerator.dispose();
```

**Critical Detail**: Always use PMREMGenerator to pre-filter the environment map. Without it, reflections are photogeneric but computationally expensive.

### Environment Intensity Control

```typescript
material.envMapIntensity = 1.0;  // 0.0=no reflections, 1.5+=overlit
```

**Typical Values**:
- Indoor scenes: 0.5–0.8
- Realistic outdoor: 1.0
- Bright/overlit: 1.5–2.0

---

## Texture Pipeline Essentials

### Resolution Guidelines (2025)

| Target | Desktop | Mobile | Format |
|--------|---------|--------|--------|
| Hero/Close-up | 4K (4096²) | 2K (2048²) | KTX2/Basis |
| Mid-distance | 2K (2048²) | 1K (1024²) | KTX2/Basis |
| Background | 1K (1024²) | 512² | KTX2/Basis |
| Small Details | 512² | 256² | KTX2/Basis |

**Rules**:
- Always power-of-two: 512, 1024, 2048, 4096
- Downscale for mobile (minimum 50% resolution)
- Use texture compression (KTX2 strongly recommended)

### Texture Channel Packing

**Optimization**: Pack multiple grayscale maps into single texture to reduce memory and draw calls.

```typescript
// Common packing: Metal/Roughness
// Red: Metalness
// Green: Roughness
// Blue: Unused
material.metalnessMap = packedTexture;  // Uses blue channel
material.roughnessMap = packedTexture;  // Uses green channel
```

### Compression Strategy

```typescript
import { KTX2Loader } from 'three/examples/jsm/loaders/KTX2Loader.js';

const ktx2Loader = new KTX2Loader();
ktx2Loader.setTranscoderPath('path/to/basis_transcoder.wasm');

const texture = await ktx2Loader.loadAsync('texture.ktx2');
material.map = texture;
```

**Quality vs Size**:
- Diffuse/Color: ETC1S (better color, smaller)
- Normal: UASTC (preserve detail)
- Roughness/Metalness: ETC1S (grayscale, tiny)

---

## Material Optimization Patterns

### Pattern 1: Share vs Clone

**Share when**: Same material on multiple meshes (memory efficient)

```typescript
const material = new THREE.MeshStandardMaterial({ color: 0xffffff });
const mesh1 = new THREE.Mesh(geometry, material);
const mesh2 = new THREE.Mesh(geometry, material);  // Reuse!
```

**Clone when**: Need independent property changes

```typescript
const material1 = baseMaterial.clone();
material1.color.set(0xff0000);
material1.opacity = 0.5;
```

### Pattern 2: Texture Atlasing via UV Channels

Three.js r152+ supports 4 UV channels (uv, uv1, uv2, uv3):

```typescript
material.map = colorTexture;
material.map.channel = 0;        // Primary UV

material.normalMap = normalTexture;
material.normalMap.channel = 1;  // Uses uv2

geometry.setAttribute('uv2', uvAttribute2);
```

**Benefit**: 5–10x more efficient than multiple materials.

### Pattern 3: onBeforeCompile for Shader Injection

Modify shader code without creating full ShaderMaterial:

```typescript
material.onBeforeCompile = function(shader, renderer) {
  shader.uniforms.pulseAmount = { value: 0.5 };

  shader.vertexShader = shader.vertexShader.replace(
    '#include <common>',
    `#include <common>
     uniform float pulseAmount;`
  );
};
```

---

## Quick Reference: Common Material Recipes

Complete implementations in `references/material-recipes.md`:
- Brushed metal (anisotropy)
- Polished chrome
- Matte plastic
- Clear glass (transmission)
- Frosted glass
- Concrete
- Carbon fiber
- Weathered/rusted metal
- Painted surface with clearcoat
- Anodized aluminum
- LCD/electronic display (emissive)
- Fabric/textile (sheen)
- Iridescent surface (thin-film)
- Holographic material

Each recipe includes full TypeScript function, parameter tuning notes, and performance implications.

---

## Texture Source Libraries

**Free PBR Textures** (CC0 License):
- **Poly Haven**: Excellent quality, all material types
- **ambientCG**: Photogrammetry-based, production-ready
- **FreePBR**: Large material library, consistent quality
- **CC0 Textures**: Substance Painter compatible

**HDRI Sources** (Free):
- **Poly Haven HDRIs**: Excellent coverage, multiple formats
- **ambientCG**: Studio + outdoor HDRI sets

**Professional Tools**:
- **Substance Painter**: Industry standard (export as MetalRough PBR)
- **Quixel Megascans**: Photogrammetry materials with integration

---

## Performance Considerations

| Feature | GPU Cost | CPU Cost | Mobile-Safe |
|---------|----------|----------|-------------|
| MeshStandardMaterial | Low | Negligible | Yes |
| MeshPhysicalMaterial | Low–Medium | Negligible | Yes (selective) |
| Transmission (Glass) | Medium | Negligible | With caution |
| Clearcoat | Low | Negligible | Yes |
| Sheen | Low | Negligible | Yes |
| Anisotropy | Medium | Negligible | Mobile-dependent |
| Iridescence | Medium | Negligible | Mobile-dependent |
| Environment Maps | Baked cost | Negligible | Essential for quality |
| Displacement Maps | High | High | Avoid on mobile |

**Rule**: Environment mapping is nearly free; displacement is expensive. Choose accordingly.

---

## When to Use References

- **This file**: Quick lookup, core concepts, decision trees
- **references/material-recipes.md**: Complete code for specific surface types, material factory patterns, texture utilities, HDRI setup functions
