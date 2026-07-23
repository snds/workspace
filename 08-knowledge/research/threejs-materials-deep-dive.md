# Three.js Materials System: Complete PBR Reference

**Version**: 2025 | **Target**: High-Fidelity Physically-Based Rendering

---

## Table of Contents

1. [MeshStandardMaterial Deep Dive](#meshstandardmaterial-deep-dive)
2. [MeshPhysicalMaterial Advanced Properties](#meshphysicalmaterial-advanced-properties)
3. [Texture Authoring Pipeline](#texture-authoring-pipeline)
4. [Environment Mapping & Lighting](#environment-mapping--lighting)
5. [Material Optimization](#material-optimization)
6. [Realistic Material Recipes](#realistic-material-recipes)
7. [Custom ShaderMaterial & RawShaderMaterial](#custom-shadermaterial--rawshadermaterial)

---

## MeshStandardMaterial Deep Dive

`MeshStandardMaterial` implements the Metallic-Roughness physically-based rendering (PBR) workflow. It's the foundation for photorealistic materials in Three.js.

### Core Properties

#### **Color & Albedo**

```javascript
const material = new THREE.MeshStandardMaterial({
  color: 0xffffff,        // Base color (default: white)
  map: colorTexture,      // Color/albedo map
  transparent: true,      // Enable transparency
  opacity: 1.0            // Alpha value [0.0-1.0]
});
```

- **`color`**: Base material color modulated with `map`
- **`map`**: Color/diffuse texture (RGB). May include alpha channel
  - Typically combined with `transparent` or `alphaTest`
  - Ideal resolution: 2K (2048×2048) for desktop, 1K for mobile
  - Format: sRGB color space required for accurate appearance

#### **Roughness (Microsurface Detail)**

```javascript
material.roughness = 0.5;        // Base roughness value [0.0-1.0]
material.roughnessMap = roughMap; // Per-texel roughness override
```

**Value Guide**:
- `0.0` = mirror-like, perfect specular reflection
- `0.3-0.5` = polished surfaces (glazed ceramic, wet surface)
- `0.5-0.7` = everyday materials (painted wood, plastic)
- `0.8-1.0` = fully diffuse, no specular (fabric, paper, concrete)

**Combined Behavior**: When both `roughness` and `roughnessMap` exist, they're **multiplied**. So `roughness: 0.5` + `roughnessMap` with value 0.8 = effective roughness of 0.4.

**Green Channel**: The green channel of `roughnessMap` contains the roughness data.

#### **Metalness (Conductor vs Dielectric)**

```javascript
material.metalness = 0.0;         // Base metalness [0.0-1.0]
material.metalnessMap = metalMap; // Per-texel metalness override
```

**Value Guide**:
- `0.0` = Pure dielectric (non-metal: wood, plastic, stone, skin)
- `0.5-0.8` = Corroded/rusty metal (mixed specular/diffuse)
- `1.0` = Pure conductor (clean metal: polished steel, aluminum, gold)

**Physical Accuracy**: In PBR, metalness is binary in real materials (either metal or not). Values between 0-1 simulate corrosion/wear on metals.

**Blue Channel**: The blue channel of `metalnessMap` contains the metalness data.

### Texture Maps in Detail

#### **normalMap - Surface Normal Details**

```javascript
material.normalMap = normalTexture;
material.normalScale = new THREE.Vector2(1.0, 1.0); // [0-1] typical
material.normalMapType = THREE.TangentSpaceNormalMap; // default
```

**What It Does**: Per-fragment normal modification affecting lighting calculations without changing actual geometry. Creates surface detail appearance.

**Normal Map Format**:
- RGB texture where R/G/B encode XYZ surface normals
- Tangent-space maps (default): Most common format
- Object-space maps: Less common, use `ObjectSpaceNormalMap`

**`normalScale` Property**:
- `Vector2` for independent X/Y intensity control
- Default: `(1,1)` = full effect
- Typical range: `[0, 1]`
- Use negative Y for left-handed convention maps: `new THREE.Vector2(1, -1)`

**Optimal Resolution**: Match color map resolution (2K desktop, 1K mobile).

#### **roughnessMap & metalnessMap**

Provide per-texel control over surface properties:

```javascript
// Packing optimization: Metal and Roughness often combined
// Into a single texture (green=roughness, blue=metalness)
const packedMetalRough = textureLoader.load('metal_rough.png');
material.roughnessMap = packedMetalRough;
material.metalnessMap = packedMetalRough;
```

**Channel Extraction**:
- **Roughness**: Uses green (G) channel
- **Metalness**: Uses blue (B) channel
- Can reuse same texture for both via shader sampling

#### **aoMap - Ambient Occlusion (Baked Shadows)**

```javascript
material.aoMap = aoTexture;        // Requires secondary UV set (uv2)
material.aoMapIntensity = 1.0;     // [0.0-1.0], default 1.0
```

**What It Does**: Darkens crevices/occluded areas where ambient light is blocked. Simulates baked shadow information.

**Critical Requirement**: Requires **second UV coordinate set** (geometry must have `uv2` attribute). This is different from primary UV for color maps.

**Red Channel**: The red (R) channel encodes AO data.

**Typical Intensity Values**:
- `0.0` = No AO effect (fully lit)
- `0.5` = 50% darkening in occluded areas
- `1.0` = Full AO effect

#### **emissiveMap & emissiveColor - Self-Illumination**

```javascript
material.emissive = new THREE.Color(0xff0000);     // Base emissive color
material.emissiveMap = glowTexture;                // Glow texture
material.emissiveIntensity = 1.0;                  // [0.0+] multiplier
```

**What It Does**: Adds unlit color/glow that doesn't cast light on other objects (fake emission).

**Color Behavior**:
- Emissive color is **added** to final pixel
- Doesn't affect shadows or GI (no real light emission)
- For visible glow, combine with post-processing (bloom)

#### **envMap - Environment Reflection**

```javascript
material.envMap = pmremTexture;        // Should be PMREM pre-processed
material.envMapIntensity = 1.0;        // [0.0-1.0], default 1.0
material.envMapRotation = new THREE.Euler(0, Math.PI/4, 0);
```

**Critical Detail**: For PBR, use **pre-filtered environment map** via `PMREMGenerator` (see Environment Mapping section).

**envMapIntensity**: Controls reflection strength:
- `0.0` = No reflections
- `0.5-1.0` = Typical for realistic materials
- `1.5+` = Overlit/bright reflections

#### **lightMap - Baked Lighting**

```javascript
material.lightMap = lightmapTexture;     // Requires secondary UV set (uv2)
material.lightMapIntensity = 1.0;        // [0.0-1.0] multiplier
```

**Requirements**:
- Requires second UV set (`uv2` attribute)
- Contains pre-baked lighting information
- Usually created in 3D DCC software or via external baking

#### **displacementMap - Vertex Deformation**

```javascript
material.displacementMap = heightMap;
material.displacementScale = 10.0;      // Strength [typically 5-50]
material.displacementBias = 0.0;        // Offset [typically -0.5 to 0.5]
```

**What It Does**: Modifies vertex positions based on texture values. Unlike normal mapping, displaced geometry is real (casts shadows, blocks rays).

**How It Works**:
- White pixels (1.0) = maximum displacement along surface normal
- Black pixels (0.0) = no displacement

**Performance Cost**: Highest of all maps due to vertex shader computation. Moderate impact on frame rate.

#### **bumpMap - Pseudo-Depth (Fallback)**

```javascript
material.bumpMap = bumpTexture;
material.bumpScale = 1.0;              // [typically 0-2]
```

**When to Use**: Only use if `normalMap` not available. Bumpmap is computed per-fragment as pseudo-normal from height data.

#### **alphaMap - Grayscale Transparency**

```javascript
material.alphaMap = alphaTexture;       // Grayscale texture
material.transparent = true;             // Enable blending
```

**Behavior**: Grayscale values control per-pixel opacity:
- Black (0.0) = fully transparent
- White (1.0) = fully opaque

### Complete MeshStandardMaterial Example

```javascript
const material = new THREE.MeshStandardMaterial({
  // Color
  color: 0xcccccc,
  map: colorMap,

  // Surface properties
  roughness: 0.6,
  roughnessMap: roughnessMap,
  metalness: 0.1,
  metalnessMap: metalnessMap,

  // Texture details
  normalMap: normalMap,
  normalScale: new THREE.Vector2(1.0, 1.0),

  // Lighting
  aoMap: aoMap,           // Requires uv2
  aoMapIntensity: 1.0,
  lightMap: lightMap,     // Requires uv2
  lightMapIntensity: 1.0,

  // Environment
  envMap: pmremEnvMap,
  envMapIntensity: 1.0,

  // Geometry deformation (expensive)
  displacementMap: displacementMap,
  displacementScale: 5.0,
  displacementBias: 0.0,

  // Advanced
  emissive: 0x000000,
  emissiveMap: emissiveMap,
  emissiveIntensity: 1.0,

  // Rendering
  transparent: true,
  opacity: 1.0,
  alphaMap: alphaMap
});
```

---

## MeshPhysicalMaterial Advanced Properties

Extends `MeshStandardMaterial` with advanced physically-correct properties for complex material types (coated surfaces, glass, anisotropic metals, iridescent materials).

### Clearcoat Layer (Multilayer Materials)

Simulates clear protective layers on top of base materials (automotive paint, glossy ceramics, varnished wood).

```javascript
const material = new THREE.MeshPhysicalMaterial({
  // Base layer (MeshStandard properties)
  color: 0xff0000,
  roughness: 0.8,
  metalness: 0.0,

  // Clear coat layer
  clearcoat: 1.0,                        // [0.0-1.0] intensity
  clearcoatRoughness: 0.1,               // [0.0-1.0] coat surface smoothness
  clearcoatMap: clearcoatMap,            // Red channel = clearcoat intensity
  clearcoatRoughnessMap: clearcoatRoughMap, // Green channel = roughness
  clearcoatNormalMap: clearcoatNormalMap,   // Independent coat normals
  clearcoatNormalScale: new THREE.Vector2(1.0, 1.0)
});
```

**When to Use**:
- Car paint (clearcoat over metallic base)
- Glossy plastic with imperfections
- Varnished wood
- Laminated surfaces

### Sheen (Cloth & Fabric)

Simulates fabric weave/textile appearance with characteristic directional highlights.

```javascript
const material = new THREE.MeshPhysicalMaterial({
  // Base properties
  color: 0x2a2a2a,
  roughness: 1.0,
  metalness: 0.0,

  // Sheen layer
  sheen: 0.8,                          // [0.0-1.0] intensity
  sheenColor: new THREE.Color(0xffffff), // Sheen tint color
  sheenColorMap: sheenColorMap,        // RGB channels
  sheenRoughness: 0.5,                 // [0.0-1.0] micro-roughness
  sheenRoughnessMap: sheenRoughMap     // Alpha channel
});
```

**Real-World Tuning**:
- Velvet: `sheen: 1.0, sheenRoughness: 0.8`
- Silk: `sheen: 0.9, sheenRoughness: 0.2`
- Cotton: `sheen: 0.4, sheenRoughness: 0.6`

### Transmission (Transparent & Translucent Materials)

Degree of light passing through material with refraction simulation (glass, plastic, wax).

```javascript
const material = new THREE.MeshPhysicalMaterial({
  // Base properties (opacity should be 1 when transmission is used)
  color: 0xffffff,
  opacity: 1.0,          // CRITICAL: Set to 1.0 for transmission
  roughness: 0.0,        // Usually smooth for clear materials
  metalness: 0.0,        // Non-metallic

  // Transmission (transparency with refraction)
  transmission: 1.0,                    // [0.0-1.0] optical transparency
  transmissionMap: transmissionMap,     // Red channel
  thickness: 10.0,                      // [0+] material thickness (critical!)
  thicknessMap: thicknessMap,          // Green channel
  ior: 1.5                             // Index of refraction [1.0-2.333]
});
```

**Critical Parameters**:

**`transmission`**:
- `0.0` = Opaque (no transmission)
- `0.5` = Semi-translucent (frosted glass effect)
- `1.0` = Fully transmissive (clear glass)

**`thickness`**: The magic parameter for realistic refraction effect.
- `0` = Infinitesimally thin (thin sheet of plastic wrap)
- `2-5` = Thin glass (window glass)
- `10-50` = Thick glass (bottle, lens)

**`ior` - Index of Refraction**:
- `1.0` = Vacuum (no refraction)
- `1.33` = Water
- `1.5` = Standard glass
- `1.6-1.8` = Dense glass/crystal
- `2.4` = Diamond

### Complete Glass Example

```javascript
const glassMaterial = new THREE.MeshPhysicalMaterial({
  color: 0xffffff,
  opacity: 1.0,
  metalness: 0.0,
  roughness: 0.0,           // Mirror-smooth

  transmission: 1.0,         // Fully transmissive
  thickness: 15.0,           // Simulate glass thickness
  ior: 1.5,                  // Standard glass

  envMap: pmremEnv,          // Essential for reflections
  envMapIntensity: 1.0
});
```

### Iridescence (Thin-Film Interference)

Simulates color-shifting seen in soap bubbles, oil slicks, insect wings.

```javascript
const material = new THREE.MeshPhysicalMaterial({
  color: 0xffffff,
  metalness: 0.0,
  roughness: 0.8,

  // Iridescence properties
  iridescence: 1.0,                    // [0.0-1.0] effect intensity
  iridescenceIOR: 1.3,                 // [1.0-2.333] thin film IOR
  iridescenceMap: iridMap,             // Red channel = intensity
  iridescenceThicknessRange: [100, 400], // Thickness range in nanometers
  iridescenceThicknessMap: thickMap    // Green channel = thickness variation
});
```

### Anisotropy (Brushed/Directional Metals)

Simulates directional surface detail (brushed metal, hair, carbon fiber weave).

```javascript
const material = new THREE.MeshPhysicalMaterial({
  color: 0x888888,
  metalness: 1.0,
  roughness: 0.3,

  // Anisotropy (directional)
  anisotropy: 1.0,                     // [0.0-1.0] strength
  anisotropyRotation: 0.0,             // Radians, counter-clockwise
  anisotropyMap: anisotropyMap         // RGB channels encode direction + strength
});
```

**Real-World Examples**:
- Brushed aluminum: `anisotropy: 0.8, anisotropyRotation: 0`
- Carbon fiber weave: `anisotropy: 1.0, anisotropyRotation: Math.PI/4`
- Hair/fur: `anisotropy: 0.9, anisotropyRotation: varies`

### Specular & Specular Color (Non-Metallic Customization)

Fine-grained control over non-metallic material specularity.

```javascript
const material = new THREE.MeshPhysicalMaterial({
  color: 0xff0000,
  metalness: 0.0,          // Must be non-metallic

  // Specular properties
  specularIntensity: 1.0,                    // [0.0-1.0] overall strength
  specularIntensityMap: specIntensityMap,   // Alpha channel
  specularColor: new THREE.Color(0xffffff), // Tint specular reflections
  specularColorMap: specColorMap            // RGB channels
});
```

---

## Texture Authoring Pipeline

### Texture Resolution Guidelines (2025)

| Target | Desktop | Mobile | Compression |
|--------|---------|--------|-------------|
| Hero/Close-up | 4K (4096×4096) | 2K (2048×2048) | KTX2/Basis |
| Mid-distance | 2K (2048×2048) | 1K (1024×1024) | KTX2/Basis |
| Background | 1K (1024×1024) | 512×512 | KTX2/Basis |
| Small Details | 512×512 | 256×256 | KTX2/Basis |

**Critical Rules**:
- All textures must be **power-of-two**: 512, 1024, 2048, 4096
- Downscale for mobile (half resolution minimum)
- Use texture compression (basis/KTX2) for web delivery

### Texture Compression: Basis & KTX2

**Why Compress**:
- PNG uncompressed in VRAM: 200KB file = 20MB+ GPU memory
- KTX2 with Basis: Same visual quality = 2MB VRAM
- ~10x memory reduction possible
- Mobile performance critical

**Basis Universal Format**:
- `.basis` or `.ktx2` file formats (ktx2 is standardized)
- Transcodes to GPU-native formats (ETC1, ASTC, BC1, etc.)
- Supports mipmap levels, cubemaps, texture arrays

**Three.js Implementation**:

```javascript
import { KTX2Loader } from 'three/examples/jsm/loaders/KTX2Loader.js';

const ktx2Loader = new KTX2Loader();
ktx2Loader.setTranscoderPath('path/to/basis_transcoder.wasm');

const texture = await ktx2Loader.loadAsync('texture.ktx2');
material.map = texture;
```

**Compression Strategy for PBR**:
- **Diffuse/Color maps**: ETC1S (better color, smaller size)
- **Normal maps**: UASTC (preserve detail)
- **Roughness/Metalness**: ETC1S (grayscale, small)

### Mipmapping Strategy

Mipmaps are pre-computed lower-resolution versions of textures for distant objects.

**Benefits**:
- Prevents aliasing on distant geometry
- Improves memory locality (performance)
- Automatic LOD system

**Three.js Setup**:

```javascript
const texture = textureLoader.load('texture.png');
texture.generateMipmaps = true;  // Usually true by default
texture.minFilter = THREE.LinearMipmapLinearFilter; // Trilinear
texture.magFilter = THREE.LinearFilter;

// For anisotropic filtering
renderer.capabilities.maxAnisotropy; // Check support
texture.anisotropy = renderer.capabilities.maxAnisotropy;
```

### Anisotropic Filtering

Improves texture quality on surfaces at oblique angles (walls, floors viewed from angle).

```javascript
// Enable anisotropic filtering
const maxAnisotropy = renderer.capabilities.maxAnisotropy;
material.map.anisotropy = maxAnisotropy;
material.normalMap.anisotropy = maxAnisotropy;
material.roughnessMap.anisotropy = maxAnisotropy;
```

### Texture Atlas Strategies

Combining multiple textures into a single texture atlas reduces GPU texture binding overhead.

**Modern Approach - Multiple UV Channels**:

Three.js r152+ supports 4 UV channels (uv, uv1, uv2, uv3):

```javascript
// Assign textures to different UV channels
material.map = colorTexture;
material.map.channel = 0;  // Uses primary UV

material.normalMap = normalTexture;
material.normalMap.channel = 1;  // Uses uv2

material.aoMap = aoTexture;
material.aoMap.channel = 2;  // Uses uv3

// Geometry must have corresponding attributes
geometry.setAttribute('uv2', uvAttribute2);
geometry.setAttribute('uv3', uvAttribute3);
```

**Benefits**:
- Single material with multiple UV maps
- No draw call overhead
- 5-10x more efficient than multiple materials

### Sourcing Textures

**Free PBR Texture Libraries**:

| Source | Quality | License | Best For |
|--------|---------|---------|----------|
| Poly Haven | Excellent | CC0 | All materials, professional quality |
| FreePBR | Good | CC0 | Metal, wood, stone, general materials |
| ambientCG | Excellent | CC0 | Production-ready, photogrammetry |
| CC0 Textures | Excellent | CC0 | Substance Painter compatible |
| Share Textures | Good | CC0 | Variety of material types |

**Professional Authoring**:
- **Substance Painter**: Industry standard, excellent normal map generation
  - Export as PBR MetalRough (not SpecGloss)
  - Supported texture maps: Albedo, Normal, Roughness, Metalness, AO, Displacement
- **Quixel Megascans**: Pre-made photogrammetry materials with Substance integration

---

## Environment Mapping & Lighting

### HDR Environment Maps (HDRI)

HDR (High Dynamic Range) Image-Based Lighting provides photorealistic lighting and reflections.

#### Proper HDRI Setup with PMREMGenerator

```javascript
import { RGBELoader } from 'three/examples/jsm/loaders/RGBELoader.js';
import { PMREMGenerator } from 'three/src/extras/PMREMGenerator.js';

const scene = new THREE.Scene();
const renderer = new THREE.WebGLRenderer();
const pmremGenerator = new PMREMGenerator(renderer);

// Load HDRI
const rgbeLoader = new RGBELoader();
rgbeLoader.load('environment.hdr', (texture) => {
  // Convert equirectangular to cubemap + pre-filter for PBR
  const envMap = pmremGenerator.fromEquirectangular(texture).texture;

  // Use for scene lighting
  scene.environment = envMap;        // Ambient lighting
  scene.background = envMap;         // Background

  // Use for material reflections
  material.envMap = envMap;
  material.envMapIntensity = 1.0;

  // Cleanup
  texture.dispose();
  pmremGenerator.dispose();
});
```

**Critical Steps**:
1. Load HDRI with `RGBELoader` (supports 32-bit radiance format)
2. **MUST** convert with `PMREMGenerator.fromEquirectangular()`
3. Set to both `scene.environment` and material `envMap`
4. Dispose of generator and original texture

### Environment Map Properties

```javascript
material.envMap = pmremTexture;
material.envMapIntensity = 1.0;           // [0.0-2.0+]
material.envMapRotation = new THREE.Euler(0, rotation, 0);
```

**`envMapIntensity`**:
- `0.0` = No environment reflections
- `0.5` = Subtle reflections (indoor lighting)
- `1.0` = Realistic reflections (typical)
- `1.5+` = Overlit/bright reflections

### HDRI Source Libraries

| Source | Format | Quality | Free |
|--------|--------|---------|------|
| Poly Haven HDRIs | .hdr, .exr | Excellent | Yes |
| ambientCG | .hdr, various | Excellent | Yes |
| Sketchfab Pro | Various | Good | Partial |

---

## Material Optimization

### Material Sharing vs. Cloning

**Rule**: Share materials when possible, clone only when necessary.

#### Sharing (Recommended)

```javascript
// Create once
const material = new THREE.MeshStandardMaterial({
  color: 0xcccccc,
  map: textureLoader.load('color.png')
});

// Reuse across many meshes
const mesh1 = new THREE.Mesh(geometry, material);
const mesh2 = new THREE.Mesh(geometry, material);
const mesh3 = new THREE.Mesh(geometry, material);
```

#### Cloning (When Necessary)

```javascript
// Clone when you need independent material properties
const material1 = baseMaterial.clone();
material1.color.set(0xff0000);

const material2 = baseMaterial.clone();
material2.opacity = 0.5;
```

**When to Clone**:
- Per-mesh color variations
- Skinning or morphing targets (required, can't share)
- Individual transparency/opacity control

### onBeforeCompile for Material Customization

Modify shader code before compilation without creating full custom ShaderMaterial.

```javascript
const material = new THREE.MeshStandardMaterial({
  color: 0xffffff,
  map: textureLoader.load('color.png')
});

// Add custom uniform and modify shader
material.onBeforeCompile = function(shader, renderer) {
  // Add custom uniform
  shader.uniforms.pulsePhase = { value: 0.0 };

  // Inject into vertex shader
  shader.vertexShader = shader.vertexShader.replace(
    '#include <common>',
    `
    #include <common>
    uniform float pulsePhase;
    `
  );

  // Modify fragment shader
  shader.fragmentShader = shader.fragmentShader.replace(
    'vec4 diffuseColor = vec4( diffuse, opacity );',
    `
    float pulse = sin(pulsePhase) * 0.5 + 0.5;
    vec4 diffuseColor = vec4( diffuse * pulse, opacity );
    `
  );
};

// Update uniform in animation loop
function animate() {
  material.uniforms.pulsePhase.value = Date.now() * 0.001;
  renderer.render(scene, camera);
}
```

### customProgramCacheKey() for Shader Caching

Tells Three.js when to recompile shaders.

```javascript
let customValue = 1;

material.onBeforeCompile = function(shader, renderer) {
  if (customValue === 1) {
    shader.defines.EFFECT_TYPE = 1;
  } else {
    shader.defines.EFFECT_TYPE = 2;
  }
};

// Tell Three.js to cache separately for each customValue
material.customProgramCacheKey = function() {
  return customValue.toString();
};
```

---

## Realistic Material Recipes

### Brushed Metal (Anisotropic)

```javascript
const brushedMetal = new THREE.MeshPhysicalMaterial({
  color: 0x888888,
  metalness: 1.0,
  roughness: 0.4,

  // Brushed effect
  anisotropy: 0.8,
  anisotropyRotation: 0,
  normalMap: brushedNormal,
  normalScale: new THREE.Vector2(0.5, 0.5),

  // Lighting
  envMap: pmremEnv,
  envMapIntensity: 1.2
});
```

### Polished Chrome

```javascript
const polishedChrome = new THREE.MeshPhysicalMaterial({
  color: 0xcccccc,
  metalness: 1.0,
  roughness: 0.05,         // Very smooth

  normalMap: microScratchNormal,
  normalScale: new THREE.Vector2(0.2, 0.2),

  envMap: pmremEnv,
  envMapIntensity: 1.5
});
```

### Matte Plastic

```javascript
const mattePlastic = new THREE.MeshStandardMaterial({
  color: 0xff6b6b,
  metalness: 0.0,
  roughness: 0.8,

  normalMap: plasticNormal,
  normalScale: new THREE.Vector2(0.5, 0.5),

  envMap: pmremEnv,
  envMapIntensity: 0.3
});
```

### Clear Glass

```javascript
const clearGlass = new THREE.MeshPhysicalMaterial({
  color: 0xffffff,
  opacity: 1.0,
  metalness: 0.0,
  roughness: 0.0,

  transmission: 1.0,
  thickness: 10.0,
  ior: 1.5,

  envMap: pmremEnv,
  envMapIntensity: 0.8
});
```

### Frosted Glass

```javascript
const frostedGlass = new THREE.MeshPhysicalMaterial({
  color: 0xffffff,
  opacity: 1.0,
  metalness: 0.0,

  transmission: 0.9,
  thickness: 6.0,
  roughness: 0.5,
  normalMap: frostNormal,
  normalScale: new THREE.Vector2(0.8, 0.8),

  ior: 1.5,
  envMapIntensity: 0.5
});
```

### Concrete

```javascript
const concrete = new THREE.MeshStandardMaterial({
  color: 0x808080,
  metalness: 0.0,
  roughness: 0.9,

  map: concreteColor,
  normalMap: concreteNormal,
  normalScale: new THREE.Vector2(1.0, 1.0),

  roughnessMap: concreteRoughness,
  aoMap: concreteAO,
  aoMapIntensity: 1.0,

  envMapIntensity: 0.2
});
```

### Fabric / Textile

```javascript
const fabric = new THREE.MeshPhysicalMaterial({
  color: 0x2a2a2a,
  metalness: 0.0,
  roughness: 0.95,

  map: fabricColor,
  normalMap: fabricWeaveNormal,
  normalScale: new THREE.Vector2(0.8, 0.8),

  sheen: 0.8,
  sheenColor: 0xffffff,
  sheenRoughness: 0.6,

  envMapIntensity: 0.1
});
```

### Carbon Fiber

```javascript
const carbonFiber = new THREE.MeshPhysicalMaterial({
  color: 0x1a1a1a,
  metalness: 0.4,
  roughness: 0.4,

  map: carbonColor,
  normalMap: carbonNormal,
  normalScale: new THREE.Vector2(1.0, 1.0),

  anisotropy: 1.0,
  anisotropyRotation: Math.PI / 4,

  clearcoat: 1.0,
  clearcoatRoughness: 0.15,

  envMapIntensity: 0.9
});
```

### Weathered/Rusted Metal

```javascript
const rustyMetal = new THREE.MeshPhysicalMaterial({
  color: 0x8b4513,
  metalness: 0.6,
  roughness: 0.8,

  map: rustColor,
  roughnessMap: rustRoughness,
  normalMap: rustNormal,
  normalScale: new THREE.Vector2(0.9, 0.9),

  aoMap: rustAO,
  aoMapIntensity: 1.0,

  emissive: 0x6b3410,
  emissiveIntensity: 0.1,

  envMapIntensity: 0.3
});
```

### Painted Surface

```javascript
const painted = new THREE.MeshPhysicalMaterial({
  color: 0xff0000,
  metalness: 0.0,
  roughness: 0.3,

  map: paintColor,
  normalMap: paintNormal,
  normalScale: new THREE.Vector2(0.5, 0.5),

  clearcoat: 1.0,
  clearcoatRoughness: 0.1,
  clearcoatNormalMap: clearcoatNormal,

  envMapIntensity: 1.0
});
```

### Anodized Aluminum

```javascript
const anodized = new THREE.MeshPhysicalMaterial({
  color: 0x333333,
  metalness: 0.8,
  roughness: 0.4,

  map: anodizedColor,
  normalMap: anodizedNormal,
  normalScale: new THREE.Vector2(0.6, 0.6),

  anisotropy: 0.5,
  anisotropyRotation: 0,

  clearcoat: 0.3,
  clearcoatRoughness: 0.2,

  envMapIntensity: 0.8
});
```

### LCD / Electronic Screens

```javascript
const lcdScreen = new THREE.MeshStandardMaterial({
  color: 0x000000,
  metalness: 0.0,
  roughness: 0.1,

  emissiveMap: screenContent,
  emissive: 0xffffff,
  emissiveIntensity: 1.5,

  envMap: pmremEnv,
  envMapIntensity: 0.4,

  normalMap: screenGlass,
  normalScale: new THREE.Vector2(0.2, 0.2)
});
```

---

## Custom ShaderMaterial & RawShaderMaterial

### ShaderMaterial: Automatic Uniforms & Attributes

ShaderMaterial automatically injects Three.js uniforms and attributes for common functionality.

```javascript
const material = new THREE.ShaderMaterial({
  uniforms: {
    time: { value: 0.0 },
    color: { value: new THREE.Color(0xffffff) }
  },
  vertexShader: `
    void main() {
      gl_Position = projectionMatrix * viewMatrix * modelMatrix * vec4(position, 1.0);
    }
  `,
  fragmentShader: `
    uniform vec3 color;
    void main() {
      gl_FragColor = vec4(color, 1.0);
    }
  `
});
```

### RawShaderMaterial: Complete Manual Control

RawShaderMaterial provides NO automatic uniforms/attributes. You define everything.

```javascript
const material = new THREE.RawShaderMaterial({
  uniforms: {
    uMatrix: { value: new THREE.Matrix4() },
    uModelViewMatrix: { value: new THREE.Matrix4() },
    uProjectionMatrix: { value: new THREE.Matrix4() },
    time: { value: 0.0 }
  },
  vertexShader: `
    precision highp float;

    uniform mat4 uMatrix;
    uniform mat4 uModelViewMatrix;
    uniform mat4 uProjectionMatrix;

    attribute vec3 position;

    void main() {
      gl_Position = uProjectionMatrix * uModelViewMatrix * vec4(position, 1.0);
    }
  `,
  fragmentShader: `
    precision highp float;

    void main() {
      gl_FragColor = vec4(1.0, 0.0, 0.0, 1.0);
    }
  `
});
```

### Uniforms: Passing Data to Shaders

Uniforms are constants across all vertices/fragments in a draw call but can change between frames.

```javascript
const material = new THREE.ShaderMaterial({
  uniforms: {
    uTime: { value: 0.0 },
    uColor: { value: new THREE.Color(0xff0000) },
    uPosition: { value: new THREE.Vector2(0.5, 0.5) },
    uTexture: { value: null }
  },

  vertexShader: `
    uniform float uTime;
    uniform vec2 uPosition;
    uniform sampler2D uTexture;
  `,

  fragmentShader: `
    uniform vec3 uColor;
    uniform float uTime;

    void main() {
      gl_FragColor = vec4(uColor, 1.0);
    }
  `
});

// Update uniforms each frame
function animate() {
  material.uniforms.uTime.value += 0.01;
  material.uniforms.uColor.value.setHSL(time * 0.5, 1, 0.5);
  renderer.render(scene, camera);
}
```

### Textures in Custom Shaders

```javascript
const material = new THREE.ShaderMaterial({
  uniforms: {
    uTexture: { value: textureLoader.load('image.png') },
    uNormalMap: { value: null }
  },

  vertexShader: `
    varying vec2 vUv;

    void main() {
      vUv = uv;
      gl_Position = projectionMatrix * viewMatrix * modelMatrix * vec4(position, 1.0);
    }
  `,

  fragmentShader: `
    uniform sampler2D uTexture;
    varying vec2 vUv;

    void main() {
      vec3 texColor = texture2D(uTexture, vUv).rgb;
      gl_FragColor = vec4(texColor, 1.0);
    }
  `
});
```

### Lighting in Custom Shaders

```javascript
const material = new THREE.ShaderMaterial({
  lights: true,

  uniforms: THREE.UniformsUtils.merge([
    THREE.UniformsLib['lights'],
    {
      uTexture: { value: textureLoader.load('color.png') }
    }
  ]),

  vertexShader: `
    varying vec3 vNormal;
    varying vec3 vPosition;

    void main() {
      vNormal = normalize(normalMatrix * normal);
      vPosition = vec3(modelViewMatrix * vec4(position, 1.0));
      gl_Position = projectionMatrix * vec4(vPosition, 1.0);
    }
  `,

  fragmentShader: `
    #include <common>
    #include <lights_pars_begin>

    varying vec3 vNormal;
    varying vec3 vPosition;
    uniform sampler2D uTexture;
    varying vec2 vUv;

    void main() {
      vec3 normal = normalize(vNormal);
      vec3 outgoing = vec3(0.0);
      for (int i = 0; i < NUM_DIR_LIGHTS; i++) {
        DirectionalLight light = directionalLights[i];
        vec3 lightDir = normalize(light.direction);
        float diffuse = max(dot(normal, lightDir), 0.0);
        outgoing += light.color * diffuse;
      }

      vec3 texColor = texture2D(uTexture, vUv).rgb;
      gl_FragColor = vec4(texColor * outgoing, 1.0);
    }
  `
});
```

---

## Best Practices Summary

### Material Setup
1. Always use environment maps with `PMREMGenerator` for PBR
2. Set `scene.environment` for global ambient lighting
3. Use `MeshPhysicalMaterial` for advanced effects
4. Share materials when possible, clone only when necessary

### Textures
1. Use power-of-two resolutions (512, 1024, 2K, 4K)
2. Compress to KTX2/Basis format for web (10x memory reduction)
3. Enable mipmapping and anisotropic filtering for quality
4. Use texture atlases with multiple UV channels for performance

### Performance
1. Pre-compile materials during load
2. Implement `customProgramCacheKey()` for dynamic `onBeforeCompile`
3. Minimize unique material variations
4. Profile shader compilation time in dev tools

### Quality
1. Match texture resolution to screen distance
2. Use proper normal map formats (tangent-space default)
3. Provide both color and roughness maps for PBR
4. Test materials with HDRI lighting for realism
5. Use reference photos for material tuning

---

## References

- [Three.js MeshStandardMaterial](https://threejs.org/docs/pages/MeshStandardMaterial.html)
- [Three.js MeshPhysicalMaterial](https://threejs.org/docs/pages/MeshPhysicalMaterial.html)
- [Three.js ShaderMaterial](https://threejs.org/docs/pages/ShaderMaterial.html)
- [Three.js Material Base Class](https://threejs.org/docs/pages/Material.html)
- [Poly Haven HDRI Library](https://polyhaven.com/hdris)
- [Three.js Official Examples - HDR Lighting](https://threejs.org/examples/webgl_materials_envmaps_hdr.html)
- [Basis Universal Compression](https://github.com/BinomialLLC/basis_universal)

**Document Version**: 2.0 | **Last Updated**: March 2025
