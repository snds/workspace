# Shader & Material Authoring for Three.js/WebGPU

This is the core technical resource for implementing Legion's visual language in Three.js. This directly addresses the generative capability: taking visual references and producing working material and shader code.

## Three.js Material Types

**When to Use Each**:

### MeshStandardMaterial
- **Use for**: Most Legion assets. PBR workflow with metalness/roughness maps.
- **Pros**: Works with all lights, respects environment maps, performant
- **Cons**: Limited customization
- **Example**: Hull panels, terrain, composite structures

```typescript
const material = new THREE.MeshStandardMaterial({
  color: 0x888888,
  metalness: 0.85,
  roughness: 0.4,
  normalMap: normalTexture,
  aoMap: aoTexture,
  side: THREE.FrontSide,
  envMap: environmentMap,
  envMapIntensity: 1.0
});
```

### MeshPhysicalMaterial
- **Use for**: Glass, translucent materials, advanced effects (anisotropy, iridescence, clearcoat)
- **Pros**: Physically-based glass rendering, clearcoat layer for dirty windows
- **Cons**: Slightly more expensive than Standard
- **Example**: Viewports, displays, polished surfaces with clearcoat wear

```typescript
const glasseMaterial = new THREE.MeshPhysicalMaterial({
  color: 0xc0d8e8,
  transmission: 0.8, // 1.0 = fully transparent
  thickness: 1.0,    // for refraction
  roughness: 0.05,
  ior: 1.5,          // realistic refraction
  clearcoat: 0.2,    // scratched surface layer
  clearcoatRoughness: 0.4
});
```

### ShaderMaterial (GLSL)
- **Use for**: Custom effects, procedural textures, vertex displacement, post-processing
- **Pros**: Maximum control, can implement any visual effect
- **Cons**: More code, shader compilation cost
- **Example**: Procedural wear, vertex deformation, custom lighting

```typescript
const material = new THREE.ShaderMaterial({
  uniforms: {
    baseColor: { value: new THREE.Color(0x888888) },
    time: { value: 0.0 },
    wearAmount: { value: 0.5 }
  },
  vertexShader: `
    varying vec3 vNormal;
    varying vec2 vUv;
    void main() {
      vNormal = normalize(normalMatrix * normal);
      vUv = uv;
      gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    }
  `,
  fragmentShader: `
    uniform vec3 baseColor;
    varying vec3 vNormal;
    varying vec2 vUv;
    void main() {
      vec3 normal = normalize(vNormal);
      vec3 light = normalize(vec3(1.0, 1.0, 1.0));
      float diffuse = max(0.0, dot(normal, light));
      gl_FragColor = vec4(baseColor * (0.2 + 0.8 * diffuse), 1.0);
    }
  `
});
```

### RawShaderMaterial
- **Use for**: Low-level control, WebGPU compatibility, minimal overhead
- **Pros**: No automatic uniforms from Three.js, pure shader
- **Cons**: Must define all uniforms and varyings manually
- **Example**: WebGPU-optimized materials

---

## PBR Texture Workflow

### Texture Map Requirements

For each material you author or receive:

1. **Albedo (Base Color)**: RGB color, sRGB color space
   - No light/shadow baked in
   - mid-gray for metals (0.5), darker for composites (0.2–0.35)
   - Load: `textureLoader.load('albedo.png')` and set `colorSpace = THREE.SRGBColorSpace`

2. **Normal Map**: XY = surface slope, Z = height, Linear color space
   - Encodes fine detail without geometry
   - Load: `textureLoader.load('normal.png')` and set `colorSpace = THREE.LinearSRGBColorSpace`
   - Apply scale: `material.normalScale.set(1.0, 1.0)`

3. **Roughness**: Grayscale, Linear color space
   - 0 = mirror smooth, 1 = matte diffuse
   - Load as Linear, multiply by scalar parameter for runtime control

4. **Metallic**: Grayscale, Linear color space
   - 0 = non-metal (plastic, stone, fabric)
   - 1 = pure metal (steel, aluminum)
   - Rarely in-between except worn edges (0.7–0.8)

5. **AO (Ambient Occlusion)**: Grayscale, Linear color space
   - Shadows in crevices
   - Multiplied into base color for darkening

### Loading and Configuring Textures

```typescript
const textureLoader = new THREE.TextureLoader();

// Albedo (sRGB)
const albedoMap = textureLoader.load('albedo.png');
albedoMap.colorSpace = THREE.SRGBColorSpace;
albedoMap.wrapS = albedoMap.wrapT = THREE.RepeatWrapping;
albedoMap.repeat.set(4, 4); // tiling

// Normal (Linear)
const normalMap = textureLoader.load('normal.png');
normalMap.colorSpace = THREE.LinearSRGBColorSpace;

// Roughness (Linear)
const roughnessMap = textureLoader.load('roughness.png');
roughnessMap.colorSpace = THREE.LinearSRGBColorSpace;

// Create material
const material = new THREE.MeshStandardMaterial({
  map: albedoMap,
  normalMap: normalMap,
  roughnessMap: roughnessMap,
  metalness: 0.9, // or metalMap for per-pixel metalness
  side: THREE.FrontSide
});
```

### Texture Size Guidelines

- Hero assets (focal point): 2K (2048×2048) albedo + normal
- Secondary/modular assets: 1K, tiling across multiple instances
- Very small props: 512×512 sufficient
- Atlasing: Combine 4–8 small materials on 2K atlas if memory-critical

---

## Custom GLSL Shader Patterns

### Procedural Wear & Weathering

Generate realistic wear without hand-painted textures:

```typescript
const wearShader = {
  uniforms: {
    baseColor: { value: new THREE.Color(0x505050) },
    rustColor: { value: new THREE.Color(0x8b4513) },
    baseRoughness: { value: 0.35 },
    wearAmount: { value: 0.5 },
    wearScale: { value: 2.0 }
  },
  vertexShader: `
    varying vec3 vPosition;
    varying vec3 vNormal;
    varying vec2 vUv;

    void main() {
      vPosition = position;
      vNormal = normalize(normalMatrix * normal);
      vUv = uv;
      gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    }
  `,
  fragmentShader: `
    uniform vec3 baseColor;
    uniform vec3 rustColor;
    uniform float baseRoughness;
    uniform float wearAmount;
    uniform float wearScale;

    varying vec3 vPosition;
    varying vec3 vNormal;
    varying vec2 vUv;

    // Voronoi noise for corrosion pattern
    float voronoi(vec3 x) {
      vec3 p = floor(x);
      vec3 f = fract(x);
      float res = 8.0;
      for(int j=-1; j<=1; j++)
        for(int k=-1; k<=1; k++)
          for(int l=-1; l<=1; l++) {
            vec3 b = vec3(j,k,l);
            vec3 r = vec3(b) - f + fract(sin(dot(p+b, vec3(1.,57.,113.)))*43758.5);
            float d = dot(r,r);
            res = min(res, d);
          }
      return sqrt(res);
    }

    void main() {
      vec3 normal = normalize(vNormal);

      // Wear pattern via Voronoi
      float wear = voronoi(vPosition * wearScale) * wearAmount;

      // Edges have more wear (Fresnel effect)
      float fresnel = pow(1.0 - abs(dot(normal, vec3(0., 0., 1.))), 2.0);
      float edgeWear = fresnel * wearAmount * 0.5;

      // Combine wear effects
      float totalWear = wear + edgeWear;

      // Lerp from base color to rust
      vec3 finalColor = mix(baseColor, rustColor, totalWear);

      // Roughness increases with wear
      float finalRoughness = mix(baseRoughness, 0.8, totalWear);

      gl_FragColor = vec4(finalColor, 1.0);
    }
  `
};

const wearMaterial = new THREE.ShaderMaterial(wearShader);
```

### Vertex Displacement

Create surface deformation effects (swaying cables, rippling surfaces):

```typescript
const displacementShader = {
  uniforms: {
    time: { value: 0.0 },
    displacement: { value: 0.1 },
    frequency: { value: 2.0 }
  },
  vertexShader: `
    uniform float time;
    uniform float displacement;
    uniform float frequency;

    void main() {
      vec3 newPos = position;

      // Sine wave deformation based on Y position
      newPos.x += sin(position.y * frequency + time) * displacement;
      newPos.z += cos(position.y * frequency + time) * displacement * 0.5;

      gl_Position = projectionMatrix * modelViewMatrix * vec4(newPos, 1.0);
    }
  `,
  fragmentShader: `
    void main() {
      gl_FragColor = vec4(0.8, 0.8, 0.8, 1.0);
    }
  `
};
```

### Brushed Metal with Directional Grain

Realistic anisotropic metal finish:

```typescript
const brushedMetalShader = `
  uniform sampler2D normalMap;
  uniform vec3 brushDirection;
  uniform float brushIntensity;

  varying vec3 vNormal;
  varying vec2 vUv;

  void main() {
    // Sample normal map
    vec3 normal = texture2D(normalMap, vUv).rgb * 2.0 - 1.0;

    // Apply brush direction (anisotropic effect)
    vec3 brushNormal = normalize(mix(normal, brushDirection, brushIntensity));

    // Light direction
    vec3 light = normalize(vec3(1., 1., 1.));

    // Anisotropic specular
    float specular = pow(max(0.0, dot(brushNormal, light)), 16.0);
    float diffuse = max(0.0, dot(vNormal, light));

    vec3 finalColor = vec3(0.6) * (diffuse + specular);
    gl_FragColor = vec4(finalColor, 1.0);
  }
`;
```

---

## Post-Processing with EffectComposer

### Bloom Effect

Enhance bright surfaces:

```typescript
import { EffectComposer } from 'three/examples/jsm/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/examples/jsm/postprocessing/RenderPass.js';
import { BloomPass } from 'three/examples/jsm/postprocessing/BloomPass.js';
import { FilmPass } from 'three/examples/jsm/postprocessing/FilmPass.js';

const composer = new EffectComposer(renderer);
composer.addPass(new RenderPass(scene, camera));

const bloom = new BloomPass(
  1.0,      // strength
  25,       // kernel size
  4,        // sigma
  256       // resolution
);
composer.addPass(bloom);

// In animation loop
composer.render();
```

### Tone Mapping & Color Grading

```typescript
// Tone mapping
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.0;

// Color grading via shader
const colorGradeShader = {
  uniforms: {
    tDiffuse: { value: null },
    warmth: { value: 0.0 }, // -1 to 1
    saturation: { value: 1.0 }
  },
  fragmentShader: `
    uniform sampler2D tDiffuse;
    uniform float warmth;
    uniform float saturation;
    varying vec2 vUv;

    void main() {
      vec4 color = texture2D(tDiffuse, vUv);

      // Warm/cool shift
      color.r += warmth * 0.1;
      color.b -= warmth * 0.1;

      // Saturation
      float gray = dot(color.rgb, vec3(0.299, 0.587, 0.114));
      color.rgb = mix(vec3(gray), color.rgb, saturation);

      gl_FragColor = color;
    }
  `
};
```

### SSAO (Screen-Space Ambient Occlusion)

```typescript
import { SSAOPass } from 'three/examples/jsm/postprocessing/SSAOPass.js';

const ssaoPass = new SSAOPass(scene, camera, window.innerWidth, window.innerHeight);
ssaoPass.kernelRadius = 16;
ssaoPass.minDistance = 0.005;
ssaoPass.maxDistance = 0.1;
composer.addPass(ssaoPass);
```

---

## WebGPU-Specific Material Considerations

**Shader Language**: WebGPU uses WGSL (not GLSL), but Three.js handles the conversion.

**Compatible Material Types**: MeshStandardMaterial and ShaderMaterial work with WebGPU.

**Texture Limits**: WebGPU has similar texture limits to WebGL, but consider:
- Fewer dynamic texture updates
- Mipmap chains for downsampling
- Compressed texture formats (ASTC, BC) where supported

**Performance**: WebGPU materials can be slightly more performant due to better pipeline efficiency, but shader optimization is still critical.

```typescript
// Test for WebGPU support
const isWebGPUSupported = navigator.gpu !== undefined;

// Material that works on both WebGL and WebGPU
const modernMaterial = new THREE.MeshPhysicalMaterial({
  color: 0x888888,
  metalness: 0.85,
  roughness: 0.4,
  normalMap: normalTexture,
  envMap: environmentMap
});

// ShaderMaterial is compatible (Three.js transpiles to WGSL if needed)
const shaderMat = new THREE.ShaderMaterial({
  // ... define vertexShader and fragmentShader as normal GLSL
  // Three.js handles transpilation
});
```

---

## Master Material Pattern: Reusable Material Factory

Create parameterized material factories for rapid iteration:

```typescript
class MaterialLibrary {
  private textureLoader = new THREE.TextureLoader();

  // Material factory function
  createMetal(options: {
    color?: number,
    metalness?: number,
    roughness?: number,
    normalScale?: number,
    wear?: number
  } = {}) {
    const {
      color = 0x888888,
      metalness = 0.85,
      roughness = 0.35,
      normalScale = 1.2,
      wear = 0.0
    } = options;

    const material = new THREE.MeshStandardMaterial({
      color: color,
      metalness: metalness,
      roughness: roughness + wear * 0.3, // wear increases roughness
      normalMap: this.brushedMetalNormal,
      normalScale: new THREE.Vector2(normalScale, normalScale),
      aoMap: this.metalAO
    });

    return material;
  }

  createComposite(options: {
    color?: number,
    weaveScale?: number,
    wear?: number
  } = {}) {
    const { color = 0x2a2a2a, weaveScale = 1.0, wear = 0.0 } = options;

    const material = new THREE.MeshStandardMaterial({
      color: color,
      metalness: 0.0,
      roughness: 0.5 + wear * 0.2,
      normalMap: this.compositeWeaveNormal,
      normalScale: new THREE.Vector2(weaveScale, weaveScale)
    });

    return material;
  }

  createGlass(options: {
    tint?: THREE.Color,
    transparency?: number,
    thickness?: number
  } = {}) {
    const {
      tint = new THREE.Color(0xc0d8e8),
      transparency = 0.8,
      thickness = 1.0
    } = options;

    const material = new THREE.MeshPhysicalMaterial({
      color: tint,
      transmission: transparency,
      thickness: thickness,
      roughness: 0.03,
      ior: 1.5,
      side: THREE.DoubleSide
    });

    return material;
  }

  createProcedural(baseColor: THREE.Color, wearAmount: number) {
    // Shader material with procedural wear
    return new THREE.ShaderMaterial({
      uniforms: {
        baseColor: { value: baseColor },
        wearAmount: { value: wearAmount }
      },
      // ... shader code
    });
  }
}

// Usage
const matLib = new MaterialLibrary();
const hullMaterial = matLib.createMetal({
  color: 0x888888,
  metalness: 0.9,
  wear: 0.3
});
const compositeMaterial = matLib.createComposite({
  weaveScale: 1.5,
  wear: 0.2
});
```

---

## Legion-Specific Material Library

### Brushed Aluminum Hull Panels

```typescript
const brushedAluminumMaterial = new THREE.MeshStandardMaterial({
  color: 0x888888,
  metalness: 0.95,
  roughness: 0.35,
  normalMap: brushedAluminumNormal, // Directional grain at ~2m scale
  aoMap: hullAO,
  envMapIntensity: 1.0,
  normalScale: new THREE.Vector2(1.2, 1.2)
});
```

### Carbon Composite Weave

```typescript
const carbonCompositeMaterial = new THREE.MeshStandardMaterial({
  color: 0x1a1a1c,
  metalness: 0.0,
  roughness: 0.55,
  normalMap: carbonWeaveNormal, // Regular grid pattern
  normalScale: new THREE.Vector2(1.5, 1.5),
  aoMap: compositeAO
});
```

### Military-Grade Glass with Clearcoat

```typescript
const viewportMaterial = new THREE.MeshPhysicalMaterial({
  color: 0xc0d8e8,
  transmission: 0.8,
  thickness: 1.5,
  roughness: 0.04,
  ior: 1.5,
  clearcoat: 0.15, // Scratched surface layer
  clearcoatRoughness: 0.5,
  side: THREE.DoubleSide
});
```

### Weathered Steel (Oxidized)

```typescript
const weatheredSteelMaterial = new THREE.MeshStandardMaterial({
  color: 0x403030,
  metalness: 0.7, // Losing metallic quality
  roughness: 0.75,
  normalMap: rustPatternNormal,
  aoMap: weatheredAO,
  envMapIntensity: 0.5
});
```

### Matte Black Control Panels

```typescript
const panelMaterial = new THREE.MeshStandardMaterial({
  color: 0x0a0a0a,
  metalness: 0.0,
  roughness: 0.95,
  emissive: 0x001a3a, // Slight glow
  emissiveIntensity: 0.1
});
```

### Concrete Regolith Terrain

```typescript
const regolithMaterial = new THREE.ShaderMaterial({
  uniforms: {
    baseColor: { value: new THREE.Color(0x6b6b6b) },
    detailScale: { value: 5.0 }
  },
  vertexShader: terrainVS,
  fragmentShader: `
    uniform vec3 baseColor;
    uniform float detailScale;
    varying vec3 vNormal;
    varying vec2 vUv;

    float noise(vec3 p) {
      // Perlin noise implementation
      // ... (standard 3D Perlin)
    }

    void main() {
      // Blend macro + micro detail
      float macroNoise = noise(vUv * 2.0);
      float microNoise = noise(vUv * detailScale);

      float roughness = mix(0.8, 0.9, microNoise);

      gl_FragColor = vec4(baseColor * (0.8 + 0.2 * macroNoise), 1.0);
    }
  `
});
```

---

## Writing Effective Material Briefs

When requesting material implementation from Claude or a technical artist, provide:

```
Material: [Name]
Visual Reference: [Photo URL or description]
Base Color: [RGB values or description]
Metalness: [0.0–1.0]
Roughness: [0.0–1.0, or range for variation]
Normal Map: [Macro detail + micro detail description]
Special Effects: [Procedural wear, emissive, anisotropy, etc.]
Tiling: [How large should pattern repeat?]
Performance Budget: [Max texture samples, WebGPU compatibility?]
```

**Example**:
```
Material: Ceres Station Hull Panel (brushed aluminum composite)
Visual Reference: Brushed aircraft aluminum + spaceworn edges
Base Color: RGB (0.55, 0.55, 0.53) — warm gray steel
Metalness: 0.95 (pure metal)
Roughness: 0.3–0.5 (directional brushing, higher at worn edges)
Normal Map: Macro = 2K brushed grain (directional, ~2m visible),
            Micro = random scratches (~0.1m scale)
Special Effects: Procedural edge wear using Fresnel,
                color desaturation toward rust brown at high-wear zones
Tiling: Grain visible every 2m, micro-scratches every 0.2m
Performance Budget: 3 texture samples max, WebGPU-compatible
Expected Code: MeshStandardMaterial with procedural wear shader
```

---

## Common Material Implementation Pitfalls

**Problem: Material Looks Too Shiny/Wet**
- *Cause*: Roughness too low, or metalness mistakenly set to 1.0 on non-metals
- *Fix*: Increase roughness to 0.5–0.7 for non-metal surfaces. Ensure metalness = 0.0 unless intentional metal.

**Problem: Normal Map Doesn't Show Detail**
- *Cause*: Normal texture too low-res, or normal not applied with proper scale
- *Fix*: Use 2K+ textures for hero assets. Increase normalScale (e.g., `normalScale: new THREE.Vector2(1.5, 1.5)`). Layer detail normals.

**Problem: Material Appears Flat/Plasticky**
- *Cause*: Missing AO, no micro-detail normal map, albedo too uniform
- *Fix*: Add AO map. Layer procedural detail normals. Introduce albedo variation via normal map influence.

**Problem: Seams Visible When Tiling**
- *Cause*: Texture edges don't match, or tiling visible at gameplay distance
- *Fix*: Use seamless textures (created in Substance Designer, etc.). Offset Texture Coordinate slightly to break pattern. Blend multiple tiles with different rotations.

**Problem: Emissive Doesn't Appear**
- *Cause*: Emissive intensity too low (<0.2), or material doesn't support emissive
- *Fix*: Increase emissive intensity to 1.0+. Ensure material type supports emissive (MeshStandardMaterial does). Check toneMappingPass isn't clamping.

**Problem: Material Performance Frame Drop**
- *Cause*: Too many texture samples (>6), expensive math operations, complex shader on WebGPU
- *Fix*: Consolidate textures (pack roughness + metalness in RGB channels). Reduce normalize operations. Simplify procedural noise. Test on target device.
