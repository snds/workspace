# Three.js Material Recipes: Complete Production Code

Comprehensive TypeScript implementations for realistic material types. Every recipe is production-ready and includes performance notes.

---

## Material Recipes

### 1. Brushed Metal (Anisotropic)

Used for brushed aluminum, steel, stainless steel with directional surface detail.

```typescript
import * as THREE from 'three';
import { TextureLoader } from 'three';

function createBrushedMetalMaterial(
  texturePath: string,
  direction: 'horizontal' | 'vertical' = 'horizontal'
): THREE.MeshPhysicalMaterial {
  const textureLoader = new TextureLoader();
  const brushedNormalMap = textureLoader.load(`${texturePath}/brushed_normal.jpg`);

  const anisotropyRotation = direction === 'vertical' ? Math.PI / 2 : 0;

  const material = new THREE.MeshPhysicalMaterial({
    // Base properties
    color: 0x888888,              // Neutral gray for metal
    metalness: 1.0,               // Pure conductor
    roughness: 0.4,               // Slightly rough for brushed effect

    // Normal detail for brush marks
    normalMap: brushedNormalMap,
    normalScale: new THREE.Vector2(0.5, 0.5),  // Subtle normal effect

    // Anisotropic brushing
    anisotropy: 0.8,              // Strong directional effect
    anisotropyRotation: anisotropyRotation,

    // Environment reflection
    envMapIntensity: 1.2,         // Slightly bright reflections

    // Rendering
    side: THREE.FrontSide,
  });

  return material;
}

// Usage
const hdri = null; // Assume pre-loaded HDRI
const brushedMetal = createBrushedMetalMaterial('/textures/metal');
brushedMetal.envMap = hdri;
```

**Performance Note**: Low GPU cost. Anisotropy adds minimal overhead. Safe for mobile.

**Tuning**:
- For more visible brushing: increase `normalScale` to `(0.8, 0.8)`
- For less metallic: reduce `metalness` to `0.8` and increase `roughness` to `0.6`

---

### 2. Polished Chrome

Mirror-like reflective surface with minimal roughness.

```typescript
function createPolishedChromeMaterial(envMap: THREE.Texture): THREE.MeshPhysicalMaterial {
  const textureLoader = new TextureLoader();

  // Very subtle micro-scratch normal map
  const microScratchNormal = textureLoader.load('micro_scratch_normal.jpg');

  const material = new THREE.MeshPhysicalMaterial({
    // Color
    color: 0xcccccc,              // Light gray for polish

    // Metallic properties
    metalness: 1.0,               // Pure metal
    roughness: 0.05,              // Nearly mirror-like

    // Barely visible micro-detail
    normalMap: microScratchNormal,
    normalScale: new THREE.Vector2(0.2, 0.2),  // Very subtle

    // Strong environment reflection
    envMap: envMap,
    envMapIntensity: 1.5,         // Bright, polished reflections

    side: THREE.FrontSide,
  });

  return material;
}

// Usage
const chrome = createPolishedChromeMaterial(pmremEnvMap);
```

**Performance Note**: Extremely low cost. Just standard PBR with low roughness.

**Tuning**:
- For mirror effect: reduce `roughness` to `0.0`
- For more visibility of microdetail: increase `normalScale` to `(0.5, 0.5)`

---

### 3. Matte Plastic

Everyday plastic material without shine. Common in consumer products.

```typescript
function createMattePlasticMaterial(
  baseColor: number = 0xff6b6b,
  texturePath?: string
): THREE.MeshStandardMaterial {
  const textureLoader = new TextureLoader();

  const material = new THREE.MeshStandardMaterial({
    // Color
    color: baseColor,
    map: texturePath ? textureLoader.load(`${texturePath}/color.jpg`) : undefined,

    // Matte finish properties
    metalness: 0.0,               // Non-metallic
    roughness: 0.8,               // Dull surface

    // Subtle surface detail
    normalMap: texturePath ? textureLoader.load(`${texturePath}/normal.jpg`) : undefined,
    normalScale: new THREE.Vector2(0.5, 0.5),

    // Minimal reflection
    envMapIntensity: 0.3,         // Barely visible reflections

    side: THREE.FrontSide,
  });

  return material;
}

// Usage
const plasticRed = createMattePlasticMaterial(0xff6b6b, '/textures/plastic');
```

**Performance Note**: Low cost. No special features, pure standard material.

**Tuning**:
- For shinier plastic: reduce `roughness` to `0.5`
- For duller plastic: increase `roughness` to `0.95`

---

### 4. Clear Glass

Transparent optical material with refraction. Requires scene.environment to be set.

```typescript
function createClearGlassMaterial(
  envMap: THREE.Texture,
  tint: number = 0xffffff,
  thickness: number = 10.0
): THREE.MeshPhysicalMaterial {
  const material = new THREE.MeshPhysicalMaterial({
    // Color (light tint)
    color: tint,
    opacity: 1.0,                 // CRITICAL: Must be 1.0 for transmission

    // Non-metallic, smooth
    metalness: 0.0,
    roughness: 0.0,               // Mirror-smooth for clear glass

    // Transmission (optical glass)
    transmission: 1.0,            // Fully transparent
    thickness: thickness,          // Glass thickness in units
    ior: 1.5,                      // Standard glass IOR

    // Reflection
    envMap: envMap,
    envMapIntensity: 0.8,

    // Rendering
    side: THREE.DoubleSide,        // Glass visible from both sides
    depthWrite: true,
  });

  return material;
}

// Usage with different thicknesses
const thinGlass = createClearGlassMaterial(pmremEnv, 0xffffff, 2.0);    // Window pane
const thickGlass = createClearGlassMaterial(pmremEnv, 0xe6f2ff, 25.0);  // Lens/bottle
```

**Performance Note**: Medium GPU cost for transmission. Requires scene.environment. Avoid thick transmission + high roughness on mobile.

**Critical**: `opacity: 1.0` is mandatory for transmission to work. Do NOT use opacity for transparency with transmission.

**Tuning**:
- Cloudier glass: Add roughness `0.3–0.5`
- Colored glass: Change `color` to tinted value (e.g., `0x00ff00` for green)
- Thicker appearance: Increase `thickness` (more refraction bending)

---

### 5. Frosted Glass

Translucent glass with diffusion. Appears opaque but light passes through.

```typescript
function createFrostedGlassMaterial(
  envMap: THREE.Texture,
  roughness: number = 0.5
): THREE.MeshPhysicalMaterial {
  const textureLoader = new TextureLoader();
  const frostNormal = textureLoader.load('frost_normal.jpg');

  const material = new THREE.MeshPhysicalMaterial({
    // Color
    color: 0xffffff,
    opacity: 1.0,

    // Smooth base but frosted surface
    metalness: 0.0,
    roughness: roughness,         // Controllable frosting

    // Transmission with diffusion
    transmission: 0.9,            // High transparency
    thickness: 6.0,               // Thin frosted layer
    ior: 1.5,

    // Frost surface pattern
    normalMap: frostNormal,
    normalScale: new THREE.Vector2(0.8, 0.8),

    // Reflection
    envMap: envMap,
    envMapIntensity: 0.5,

    side: THREE.DoubleSide,
  });

  return material;
}

// Usage
const frosted = createFrostedGlassMaterial(pmremEnv, 0.5);
```

**Performance Note**: Medium cost, similar to clear glass. The normal map adds minimal overhead.

**Tuning**:
- More opaque/frosted: Increase `roughness` to `0.7–0.8` and reduce `transmission` to `0.7`
- More transparent: Reduce `roughness` to `0.2` and increase `transmission` to `1.0`

---

### 6. Concrete

Rough, porous surface with ambient occlusion. Typical for architectural/industrial materials.

```typescript
function createConcreteMaterial(texturePath: string): THREE.MeshStandardMaterial {
  const textureLoader = new TextureLoader();

  const colorMap = textureLoader.load(`${texturePath}/color.jpg`);
  const normalMap = textureLoader.load(`${texturePath}/normal.jpg`);
  const roughnessMap = textureLoader.load(`${texturePath}/roughness.jpg`);
  const aoMap = textureLoader.load(`${texturePath}/ao.jpg`);

  // Configure color map for sRGB
  colorMap.colorSpace = THREE.SRGBColorSpace;

  const material = new THREE.MeshStandardMaterial({
    // Texture maps
    map: colorMap,
    normalMap: normalMap,
    normalScale: new THREE.Vector2(1.0, 1.0),

    // Surface properties
    metalness: 0.0,               // Non-metallic
    roughnessMap: roughnessMap,
    roughness: 0.9,               // Very rough

    // Baked ambient occlusion
    aoMap: aoMap,
    aoMapIntensity: 1.0,

    // Minimal reflection
    envMapIntensity: 0.2,

    side: THREE.FrontSide,
  });

  return material;
}

// Usage
const concrete = createConcreteMaterial('/textures/concrete');
concrete.envMap = pmremEnv;
```

**Performance Note**: Low–medium cost. AO map requires uv2 coordinate set on geometry.

**Setup Requirement**: Geometry must have uv2 attribute:
```typescript
geometry.setAttribute('uv2', new THREE.BufferAttribute(
  geometry.attributes.uv.array,
  2
));
```

**Tuning**:
- For weathered look: Tint color slightly `0x707070`
- For lighter concrete: Use lighter base color `0xb0b0b0`

---

### 7. Carbon Fiber

Woven composite with directional pattern and protective clearcoat.

```typescript
function createCarbonFiberMaterial(
  envMap: THREE.Texture,
  texturePath: string
): THREE.MeshPhysicalMaterial {
  const textureLoader = new TextureLoader();

  const colorMap = textureLoader.load(`${texturePath}/carbon_color.jpg`);
  const normalMap = textureLoader.load(`${texturePath}/carbon_normal.jpg`);

  const material = new THREE.MeshPhysicalMaterial({
    // Texture
    map: colorMap,
    normalMap: normalMap,
    normalScale: new THREE.Vector2(1.0, 1.0),

    // Base material (dark composite)
    color: 0x1a1a1a,
    metalness: 0.4,               // Partially metallic (resin + fiber)
    roughness: 0.4,

    // Directional weave pattern (anisotropic)
    anisotropy: 1.0,
    anisotropyRotation: Math.PI / 4,  // 45-degree weave pattern

    // Clear protective coat (gloss finish)
    clearcoat: 1.0,
    clearcoatRoughness: 0.15,

    // Reflection
    envMap: envMap,
    envMapIntensity: 0.9,

    side: THREE.FrontSide,
  });

  return material;
}

// Usage
const carbonFiber = createCarbonFiberMaterial(pmremEnv, '/textures/carbon');
```

**Performance Note**: Medium cost due to anisotropy. Slightly higher GPU load than standard PBR.

**Tuning**:
- Glossier carbon: Reduce `clearcoatRoughness` to `0.05`
- Matte carbon: Increase `clearcoatRoughness` to `0.3`
- Different weave angle: Adjust `anisotropyRotation` (in radians)

---

### 8. Weathered/Rusted Metal

Oxidized metal with rust coloration and rough surface.

```typescript
function createRustedMetalMaterial(
  texturePath: string,
  envMap: THREE.Texture
): THREE.MeshPhysicalMaterial {
  const textureLoader = new TextureLoader();

  const colorMap = textureLoader.load(`${texturePath}/rust_color.jpg`);
  const roughnessMap = textureLoader.load(`${texturePath}/rust_roughness.jpg`);
  const normalMap = textureLoader.load(`${texturePath}/rust_normal.jpg`);
  const aoMap = textureLoader.load(`${texturePath}/rust_ao.jpg`);

  const material = new THREE.MeshPhysicalMaterial({
    // Rust coloration
    color: 0x8b4513,              // Brown rust color
    map: colorMap,

    // Surface detail
    normalMap: normalMap,
    normalScale: new THREE.Vector2(0.9, 0.9),

    // Oxidized properties
    metalness: 0.6,               // Partially corroded (mixed metal/oxide)
    roughnessMap: roughnessMap,
    roughness: 0.8,               // Rough oxidized surface

    // Depth in crevices
    aoMap: aoMap,
    aoMapIntensity: 1.0,

    // Slight glow (oxidation layer)
    emissive: 0x6b3410,
    emissiveIntensity: 0.1,

    // Minimal reflection
    envMap: envMap,
    envMapIntensity: 0.3,

    side: THREE.FrontSide,
  });

  return material;
}

// Usage
const rustyPipe = createRustedMetalMaterial('/textures/rust', pmremEnv);
```

**Performance Note**: Low–medium cost. Requires uv2 for AO map.

**Tuning**:
- More corroded: Increase `metalness` to `0.8` and `roughness` to `0.95`
- More metallic base: Reduce `metalness` to `0.4` and `roughness` to `0.5`
- Heavier glow: Increase `emissiveIntensity` to `0.2`

---

### 9. Painted Surface with Clearcoat

Multi-layer paint with protective clear coat (automotive quality).

```typescript
function createPaintedSurfaceMaterial(
  baseColor: number = 0xff0000,
  texturePath?: string,
  envMap?: THREE.Texture,
  glossy: boolean = true
): THREE.MeshPhysicalMaterial {
  const textureLoader = new TextureLoader();

  let colorMap: THREE.Texture | undefined;
  let normalMap: THREE.Texture | undefined;

  if (texturePath) {
    colorMap = textureLoader.load(`${texturePath}/paint_color.jpg`);
    normalMap = textureLoader.load(`${texturePath}/paint_normal.jpg`);
  }

  const material = new THREE.MeshPhysicalMaterial({
    // Base paint color
    color: baseColor,
    map: colorMap,

    // Paint layer surface
    roughness: glossy ? 0.3 : 0.6,
    metalness: 0.0,

    normalMap: normalMap,
    normalScale: new THREE.Vector2(0.5, 0.5),

    // Clear coat protection
    clearcoat: 1.0,
    clearcoatRoughness: glossy ? 0.1 : 0.2,

    // Reflection
    envMap: envMap,
    envMapIntensity: 1.0,

    side: THREE.FrontSide,
  });

  return material;
}

// Usage
const carPaint = createPaintedSurfaceMaterial(0xff0000, '/textures/paint', pmremEnv, true);
const mattePaint = createPaintedSurfaceMaterial(0x000000, '/textures/matte', pmremEnv, false);
```

**Performance Note**: Low cost. Clearcoat adds minimal overhead.

**Tuning**:
- High gloss (automotive): `glossy: true`, `clearcoatRoughness: 0.05`
- Satin finish: `glossy: false`, `clearcoatRoughness: 0.15`
- Metallic paint: Add `metalness: 0.5` to base layer

---

### 10. Anodized Aluminum

Colored anodized aluminum with brushed/directional finish.

```typescript
function createAnodizedAluminumMaterial(
  anodizeColor: number = 0x333333,
  envMap: THREE.Texture,
  texturePath: string
): THREE.MeshPhysicalMaterial {
  const textureLoader = new TextureLoader();
  const normalMap = textureLoader.load(`${texturePath}/anodized_normal.jpg`);

  const material = new THREE.MeshPhysicalMaterial({
    // Anodized color
    color: anodizeColor,

    // Subtle brushing
    normalMap: normalMap,
    normalScale: new THREE.Vector2(0.6, 0.6),

    // Metal base with anodize coating
    metalness: 0.8,               // Partially metallic through oxide
    roughness: 0.4,

    // Directional anisotropy
    anisotropy: 0.5,
    anisotropyRotation: 0,        // Horizontal brushing

    // Protective oxide layer
    clearcoat: 0.3,
    clearcoatRoughness: 0.2,

    // Reflection
    envMap: envMap,
    envMapIntensity: 0.8,

    side: THREE.FrontSide,
  });

  return material;
}

// Usage
const blackAnodized = createAnodizedAluminumMaterial(0x1a1a1a, pmremEnv, '/textures/aluminum');
const goldAnodized = createAnodizedAluminumMaterial(0xc9a961, pmremEnv, '/textures/aluminum');
const redAnodized = createAnodizedAluminumMaterial(0xff4444, pmremEnv, '/textures/aluminum');
```

**Performance Note**: Low–medium cost. Anisotropy adds minimal overhead.

**Tuning**:
- More metallic: Increase `metalness` to `0.95` and reduce `roughness` to `0.2`
- More matte: Reduce `metalness` to `0.5` and increase `roughness` to `0.6`

---

### 11. LCD/Electronic Display Screen

Self-illuminating screen with gloss front layer.

```typescript
function createLCDScreenMaterial(
  screenContentTexture: THREE.Texture,
  envMap: THREE.Texture,
  brightness: number = 1.5
): THREE.MeshStandardMaterial {
  const material = new THREE.MeshStandardMaterial({
    // Dark background
    color: 0x000000,

    // Gloss screen finish
    metalness: 0.0,
    roughness: 0.1,               // Smooth glass-like surface

    // Screen content (emissive)
    emissiveMap: screenContentTexture,
    emissive: 0xffffff,
    emissiveIntensity: brightness,

    // Reflection (glossy screen)
    envMap: envMap,
    envMapIntensity: 0.4,

    side: THREE.FrontSide,
  });

  return material;
}

// Usage
const phone = createLCDScreenMaterial(
  screenTexture,
  pmremEnv,
  1.5  // Bright display
);

const dimScreen = createLCDScreenMaterial(
  screenTexture,
  pmremEnv,
  0.8  // Dimmer (battery saver mode)
);
```

**Performance Note**: Low cost. Emissive rendering is efficient. No texture filtering overhead.

**Screen Content Texture**: Should be pre-rendered at target resolution (usually 1024x2048 for phones).

**Tuning**:
- Brighter/darker display: Adjust `emissiveIntensity`
- Reflections visible: Increase `envMapIntensity` to `0.6`
- Add screen glare: Increase `roughness` to `0.2`

---

### 12. Fabric/Textile (Sheen)

Cloth material with directional sheen highlight. Realistic for velvet, silk, cotton.

```typescript
function createFabricMaterial(
  baseColor: number = 0x2a2a2a,
  fabricType: 'velvet' | 'silk' | 'cotton' = 'cotton',
  texturePath?: string,
  envMap?: THREE.Texture
): THREE.MeshPhysicalMaterial {
  const textureLoader = new TextureLoader();

  // Fabric type presets
  const presets = {
    velvet: { sheen: 1.0, sheenRoughness: 0.8 },
    silk: { sheen: 0.9, sheenRoughness: 0.2 },
    cotton: { sheen: 0.4, sheenRoughness: 0.6 },
  };

  const preset = presets[fabricType];

  const material = new THREE.MeshPhysicalMaterial({
    // Fabric color
    color: baseColor,
    map: texturePath ? textureLoader.load(`${texturePath}/fabric_color.jpg`) : undefined,

    // Non-metallic, rough
    metalness: 0.0,
    roughness: 0.95,

    // Weave pattern
    normalMap: texturePath ? textureLoader.load(`${texturePath}/fabric_weave.jpg`) : undefined,
    normalScale: new THREE.Vector2(0.8, 0.8),

    // Fabric sheen (characteristic highlight)
    sheen: preset.sheen,
    sheenColor: new THREE.Color(0xffffff),
    sheenRoughness: preset.sheenRoughness,

    // Minimal reflection
    envMap: envMap,
    envMapIntensity: 0.1,

    side: THREE.FrontSide,
  });

  return material;
}

// Usage
const velvet = createFabricMaterial(0xff0000, 'velvet', '/textures/fabric', pmremEnv);
const silkScarf = createFabricMaterial(0xffd700, 'silk', '/textures/silk', pmremEnv);
const cottonShirt = createFabricMaterial(0xffffff, 'cotton', undefined, pmremEnv);
```

**Performance Note**: Low cost. Sheen is efficient. Normal map adds minimal overhead.

**Tuning**:
- Glossier fabric: Reduce `sheenRoughness`
- Duller fabric: Increase `roughness` and reduce `sheen`

---

### 13. Iridescent Surface (Thin-Film)

Color-shifting material like soap bubbles, oil slicks, holographic surfaces.

```typescript
function createIridescentMaterial(
  baseColor: number = 0xffffff,
  intensity: number = 1.0,
  envMap: THREE.Texture
): THREE.MeshPhysicalMaterial {
  const material = new THREE.MeshPhysicalMaterial({
    // Base color
    color: baseColor,

    // Non-metallic but reflective
    metalness: 0.0,
    roughness: 0.8,

    // Iridescence (thin-film interference)
    iridescence: intensity,
    iridescenceIOR: 1.3,           // Thin film IOR (soap bubble ~1.3)
    iridescenceThicknessRange: [100, 400],  // Nanometers

    // Strong environment reflection
    envMap: envMap,
    envMapIntensity: 1.0,

    side: THREE.FrontSide,
  });

  return material;
}

// Usage
const soapBubble = createIridescentMaterial(0xffffff, 1.0, pmremEnv);
const oilSlick = createIridescentMaterial(0x000000, 0.8, pmremEnv);
```

**Performance Note**: Medium cost. Iridescence calculation adds GPU overhead. Monitor on mobile.

**Tuning**:
- More pronounced color shift: Increase `iridescence` to `1.0` and widen `iridescenceThicknessRange` to `[50, 500]`
- Subtle effect: Reduce `iridescence` to `0.5`

---

### 14. Holographic Material

High-tech iridescent surface with multiple color layers and high specularity.

```typescript
function createHolographicMaterial(
  envMap: THREE.Texture
): THREE.MeshPhysicalMaterial {
  const material = new THREE.MeshPhysicalMaterial({
    // Bright base
    color: 0xccccff,

    // Highly reflective
    metalness: 0.5,
    roughness: 0.2,

    // Strong iridescence with multiple colors
    iridescence: 1.0,
    iridescenceIOR: 2.0,          // Higher IOR for more color shift
    iridescenceThicknessRange: [200, 800],  // Wider range for varied colors

    // Strong environment reflection
    envMap: envMap,
    envMapIntensity: 1.5,

    // Slight emission for glow
    emissive: 0x00ffff,
    emissiveIntensity: 0.2,

    side: THREE.FrontSide,
  });

  return material;
}

// Usage
const hologram = createHolographicMaterial(pmremEnv);
```

**Performance Note**: Higher GPU cost due to iridescence + emission. Test on target hardware.

**Tuning**:
- More colorful: Increase `iridescenceThicknessRange` to `[100, 1000]`
- More subtle: Reduce `iridescence` to `0.6` and `envMapIntensity` to `1.0`
- More glow: Increase `emissiveIntensity` to `0.4`

---

## Advanced Patterns

### Material Factory

Reusable pattern for creating families of similar materials with consistent properties.

```typescript
interface MaterialConfig {
  baseColor: number;
  metalness: number;
  roughness: number;
  hasNormal: boolean;
  hasAO: boolean;
  hasEmissive: boolean;
}

class MaterialFactory {
  private textureLoader: THREE.TextureLoader;
  private envMap: THREE.Texture | null = null;
  private textureCache: Map<string, THREE.Texture> = new Map();

  constructor() {
    this.textureLoader = new THREE.TextureLoader();
  }

  setEnvironmentMap(envMap: THREE.Texture): void {
    this.envMap = envMap;
  }

  private loadTexture(path: string): THREE.Texture {
    if (this.textureCache.has(path)) {
      return this.textureCache.get(path)!;
    }
    const texture = this.textureLoader.load(path);
    this.textureCache.set(path, texture);
    return texture;
  }

  createMaterial(
    config: MaterialConfig,
    textureBasePath?: string
  ): THREE.MeshStandardMaterial | THREE.MeshPhysicalMaterial {
    const material = new THREE.MeshStandardMaterial({
      color: config.baseColor,
      metalness: config.metalness,
      roughness: config.roughness,
      envMap: this.envMap ?? undefined,
      envMapIntensity: 1.0,
    });

    if (textureBasePath) {
      if (config.hasNormal) {
        material.normalMap = this.loadTexture(`${textureBasePath}/normal.jpg`);
        material.normalScale.set(1.0, 1.0);
      }

      if (config.hasAO) {
        material.aoMap = this.loadTexture(`${textureBasePath}/ao.jpg`);
        material.aoMapIntensity = 1.0;
      }

      if (config.hasEmissive) {
        material.emissiveMap = this.loadTexture(`${textureBasePath}/emissive.jpg`);
        material.emissive = new THREE.Color(0xffffff);
        material.emissiveIntensity = 0.5;
      }
    }

    return material;
  }

  clearCache(): void {
    this.textureCache.forEach(texture => texture.dispose());
    this.textureCache.clear();
  }
}

// Usage
const factory = new MaterialFactory();
factory.setEnvironmentMap(pmremEnv);

const metalConfig: MaterialConfig = {
  baseColor: 0x888888,
  metalness: 1.0,
  roughness: 0.3,
  hasNormal: true,
  hasAO: false,
  hasEmissive: false,
};

const metal1 = factory.createMaterial(metalConfig, '/textures/metal1');
const metal2 = factory.createMaterial(metalConfig, '/textures/metal2');
```

---

### Texture Loader Utility with Caching

Production-ready texture loading with error handling and memory management.

```typescript
interface TextureLoaderOptions {
  sRGB?: boolean;
  generateMipmaps?: boolean;
  anisotropy?: number;
}

class CachedTextureLoader {
  private loader: THREE.TextureLoader;
  private cache: Map<string, THREE.Texture> = new Map();
  private maxAnisotropy: number = 16;

  constructor(maxAnisotropy: number = 16) {
    this.loader = new THREE.TextureLoader();
    this.maxAnisotropy = maxAnisotropy;
  }

  async load(
    path: string,
    options: TextureLoaderOptions = {}
  ): Promise<THREE.Texture> {
    const cacheKey = `${path}:${JSON.stringify(options)}`;

    if (this.cache.has(cacheKey)) {
      return this.cache.get(cacheKey)!;
    }

    return new Promise((resolve, reject) => {
      this.loader.load(
        path,
        (texture) => {
          if (options.sRGB !== false) {
            texture.colorSpace = THREE.SRGBColorSpace;
          }

          if (options.generateMipmaps !== false) {
            texture.generateMipmaps = true;
            texture.minFilter = THREE.LinearMipmapLinearFilter;
            texture.magFilter = THREE.LinearFilter;
          }

          if (options.anisotropy ?? true) {
            texture.anisotropy = this.maxAnisotropy;
          }

          this.cache.set(cacheKey, texture);
          resolve(texture);
        },
        undefined,
        reject
      );
    });
  }

  dispose(): void {
    this.cache.forEach(texture => texture.dispose());
    this.cache.clear();
  }
}

// Usage
const textureLoader = new CachedTextureLoader(16);

const colorMap = await textureLoader.load('/textures/color.jpg', { sRGB: true });
const normalMap = await textureLoader.load('/textures/normal.jpg', { sRGB: false });
```

---

### HDRI Environment Setup Function

Complete HDRI initialization with memory cleanup.

```typescript
async function setupHDRIEnvironment(
  hdriPath: string,
  scene: THREE.Scene,
  renderer: THREE.WebGLRenderer
): Promise<THREE.Texture> {
  const rgbeLoader = new RGBELoader();
  const pmremGenerator = new PMREMGenerator(renderer);

  try {
    // Load HDRI
    const hdriTexture = await new Promise<THREE.Texture>((resolve, reject) => {
      rgbeLoader.load(hdriPath, resolve, undefined, reject);
    });

    // Convert to PMREM
    const envMap = pmremGenerator.fromEquirectangular(hdriTexture).texture;

    // Apply to scene
    scene.environment = envMap;
    scene.background = envMap;

    // Cleanup
    hdriTexture.dispose();
    pmremGenerator.dispose();

    return envMap;
  } catch (error) {
    console.error(`Failed to load HDRI: ${hdriPath}`, error);
    throw error;
  }
}

// Usage
const envMap = await setupHDRIEnvironment(
  '/environments/studio.hdr',
  scene,
  renderer
);

// Apply to materials
material.envMap = envMap;
material.envMapIntensity = 1.0;
```

---

## Performance Optimization Notes

### Mobile Optimization Checklist

```typescript
// For mobile devices, use simplified material configs

function createMobileFriendlyMaterial(baseColor: number): THREE.MeshStandardMaterial {
  return new THREE.MeshStandardMaterial({
    // Reduced complexity
    color: baseColor,
    metalness: 0.0,
    roughness: 0.7,

    // No displacement
    // No second UV set (aoMap)

    // Minimal texturing
    // Use compressed textures (KTX2)

    // Light environment
    envMapIntensity: 0.5,
  });
}
```

### GPU Memory Usage

| Material Type | VRAM (per instance) | Notes |
|---------------|-------------------|-------|
| MeshStandardMaterial | ~100KB–1MB | Depends on texture count |
| MeshPhysicalMaterial | ~150KB–2MB | Clearcoat/transmission adds overhead |
| Textures (uncompressed) | 200KB (1K²) per texture | PNG ~200KB → 20MB+ in VRAM |
| Textures (KTX2) | 2–5MB per texture | 10x compression typical |

**Rule**: Compress all textures to KTX2 for web delivery. Uncompressed PNG kills memory.

---

## Recommended Texture Resolution by Use Case

| Use Case | Resolution | Compression | Rationale |
|----------|-----------|-------------|-----------|
| Hero shots | 4K (4096²) | KTX2/UASTC | Close inspection, print quality |
| General scenes | 2K (2048²) | KTX2/ETC1S | Best quality/performance balance |
| Mobile only | 1K (1024²) | KTX2/ETC1S | Mobile memory + GPU constraints |
| Distant objects | 512² or less | KTX2/Basis | No visible detail at distance |

