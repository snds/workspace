# TSL (Three Shading Language) Materials & Patterns

## TSL Fundamentals

### Nodes: The Building Blocks

Everything in TSL is a **node**—composable shader building blocks that connect together:

```typescript
import { tsl as TSL } from 'three/webgpu';
const { vec3, texture, uv, sin, time } = TSL;

// Node: uniform value (same for all pixels)
const baseColor = vec3(1, 0, 0);

// Node: texture sample (read from texture at UV)
const colorMap = texture(someTexture, uv());

// Node: computed value (math operation)
const animatedColor = baseColor.mul(sin(time));

// Connect nodes into a material
const material = new THREE.MeshStandardNodeMaterial();
material.colorNode = animatedColor;
```

Nodes are **lazy-evaluated graphs**. They don't execute until rendered. The compiler optimizes them automatically.

### Connecting Nodes

Nodes support **fluent chaining** via math operations:

```typescript
const wave = sin(time.mul(0.001))        // sin(time * 0.001)
  .mul(0.5)                              // * 0.5
  .add(0.5)                              // + 0.5
  .clamp(0, 1);                          // clamp to [0, 1]
```

### Node Types

| Category | Examples |
|----------|----------|
| **Vertex Data** | `positionLocal`, `normalLocal`, `uv`, `uv0`, `uv1` |
| **World Space** | `positionWorld`, `normalWorld`, `tangentWorld` |
| **Screen Data** | `screenUV`, `screenSize`, `viewportUV` |
| **Camera** | `cameraPosition`, `cameraViewMatrix`, `cameraNear`, `cameraFar` |
| **Material** | `diffuseColor`, `metalness`, `roughness`, `emissive`, `opacity` |
| **Time** | `time` (seconds since start) |
| **Math** | `sin`, `cos`, `tan`, `sqrt`, `pow`, `clamp`, `mix`, `step`, `smoothstep` |
| **Vectors** | `normalize`, `length`, `distance`, `cross`, `dot`, `reflect` |
| **Sampling** | `texture`, `cubeTexture`, `textureProj`, `textureLod` |
| **Control** | `If`, `Switch`, `Loop`, `Var`, `Const` |

---

## Converting GLSL Patterns to TSL

### Pattern 1: Time-Based Animation

**GLSL:**
```glsl
uniform float uTime;
uniform sampler2D uTexture;
varying vec2 vUv;

void main() {
  float wave = sin(vUv.x * 10.0 + uTime);
  gl_FragColor = texture2D(uTexture, vUv + wave * 0.01);
}
```

**TSL:**
```typescript
import { tsl as TSL } from 'three/webgpu';
const { texture, uv, sin, time } = TSL;

const material = new THREE.MeshStandardNodeMaterial();
const wave = sin(uv().x.mul(10).add(time));
material.colorNode = texture(myTexture, uv().add(wave.mul(0.01)));
```

### Pattern 2: Normal Mapping

**GLSL:**
```glsl
uniform sampler2D normalMap;
varying vec3 vNormal;
varying vec2 vUv;

void main() {
  vec3 normal = texture2D(normalMap, vUv).rgb * 2.0 - 1.0;
  normal = normalize(normal);
  gl_FragColor = vec4(normal, 1.0);
}
```

**TSL:**
```typescript
import { tsl as TSL } from 'three/webgpu';
const { texture, uv, normalLocal } = TSL;

const material = new THREE.MeshStandardNodeMaterial();
const normalMap = texture(myNormalTexture, uv())
  .mul(2)
  .sub(1)
  .normalize();
material.normalNode = normalMap;
```

### Pattern 3: Parallax Mapping

**GLSL:**
```glsl
uniform sampler2D heightMap;
uniform float heightScale;
varying vec3 vViewDir;
varying vec2 vUv;

void main() {
  float height = texture2D(heightMap, vUv).r;
  vec2 uvOffset = vViewDir.xy * height * heightScale;
  gl_FragColor = texture2D(diffuseMap, vUv + uvOffset);
}
```

**TSL:**
```typescript
import { tsl as TSL } from 'three/webgpu';
const { texture, uv, vec2 } = TSL;

const material = new THREE.MeshStandardNodeMaterial();
const height = texture(heightMap, uv()).r;
const uvOffset = vec2(height.mul(heightScale));
material.colorNode = texture(diffuseMap, uv().add(uvOffset));
```

---

## TSL Material Examples

### Example 1: Animated Procedural Material (Noise-Based)

```typescript
import { tsl as TSL } from 'three/webgpu';
import * as THREE from 'three/webgpu';

const {
  vec3, vec4, float, sin, cos, time,
  positionWorld, normalWorld, uv, hash,
  clamp, mix, smoothstep
} = TSL;

// Simplex-like noise approximation (3D perlin-style)
function turbulence(pos, scale = 1.0) {
  const p = pos.mul(scale);
  const x = sin(p.x.mul(12.9898)).mul(43758.5453);
  const y = sin(p.y.mul(78.233)).mul(43758.5453);
  const z = sin(p.z.mul(45.164)).mul(43758.5453);
  return sin(x.add(y).add(z)).add(1).mul(0.5);
}

function animatedNoise() {
  const pos = positionWorld;
  const t = time.mul(0.5);
  
  // Layer noise at multiple scales
  const noise1 = turbulence(pos, 2.0);
  const noise2 = turbulence(pos.add(vec3(t, 0, t)), 4.0).mul(0.5);
  const noise3 = turbulence(pos.add(vec3(0, t, 0)), 8.0).mul(0.25);
  
  const combined = noise1.add(noise2).add(noise3);
  return combined.clamp(0, 1);
}

const material = new THREE.MeshStandardNodeMaterial();

// Color based on animated noise
const noiseFactor = animatedNoise();
material.colorNode = vec3(
  noiseFactor.mul(0.8),
  noiseFactor.mul(0.5).add(0.3),
  noiseFactor.mul(1.2).clamp(0, 1)
);

// Roughness varies with noise too
material.roughnessNode = noiseFactor.mix(0.2, 0.8);

// Normal displacement
const displacement = noiseFactor.mul(0.1);
material.normalNode = normalWorld
  .add(vec3(displacement, displacement.mul(0.5), displacement))
  .normalize();
```

**What it does:**
- Creates 3D turbulent noise layered at multiple frequencies
- Animates the noise over time for organic motion
- Maps noise to color, roughness, and normal displacement
- Result: liquid metal-like flowing surface

---

### Example 2: Glass/Transmission Material in TSL

```typescript
import { tsl as TSL } from 'three/webgpu';
import * as THREE from 'three/webgpu';

const {
  vec3, float, sin, time,
  positionWorld, normalWorld, cameraPosition,
  texture, uv, refract, normalize, length,
  mix, smoothstep, clamp
} = TSL;

const material = new THREE.MeshPhysicalNodeMaterial();

// Chromatic aberration (refracts different wavelengths differently)
function chromaticRefraction(normal, viewDir, ior = 1.5) {
  const refractR = refract(viewDir, normal, ior + 0.02);
  const refractG = refract(viewDir, normal, ior);
  const refractB = refract(viewDir, normal, ior - 0.02);
  
  // In real scenario, would sample environment map at offset coordinates
  return vec3(
    refractR.x.mul(0.3),
    refractG.y.mul(0.3),
    refractB.z.mul(0.3)
  );
}

material.transmissionNode = float(0.9); // Highly transparent

// Slight chromatic aberration
const normal = normalWorld;
const viewDir = normalize(cameraPosition.sub(positionWorld));
const aberration = chromaticRefraction(normal, viewDir);

material.colorNode = vec3(
  0.9,
  0.95,
  1.0
).add(aberration.mul(0.1));

// Glass-like roughness (mostly smooth, slight micro-roughness)
material.roughnessNode = float(0.02);

// High IOR for realistic glass
material.iorNode = float(1.5);

// Slight blue tint for glass
material.emissiveNode = vec3(0.02, 0.02, 0.04);
```

**What it does:**
- Creates physically-based transparent glass
- Simulates chromatic aberration (color fringing at edges)
- Realistic glass IOR and roughness values
- Result: convincing glass or ice material

---

### Example 3: Procedural Metal with Weathering

```typescript
import { tsl as TSL } from 'three/webgpu';
import * as THREE from 'three/webgpu';

const {
  vec3, vec4, float, sin, cos, time,
  positionWorld, normalWorld, screenUV,
  texture, uv, clamp, mix, smoothstep,
  cross, normalize, dot
} = TSL;

// Hash-based pseudo-random function
function pseudoRandom(seed) {
  const x = sin(seed.mul(12.9898)).mul(43758.5453);
  return x.sub(x.floor());
}

// Weathering pattern based on position
function weatheringMap() {
  const pos = positionWorld.mul(5.0);
  
  // Horizontal streaks (water damage)
  const streaks = sin(pos.y.mul(20.0)).mul(0.5).add(0.5);
  
  // Random spots (rust)
  const spots = pseudoRandom(pos.xyz).smoothstep(0.5, 0.7);
  
  // Vertical cracks
  const cracks = pseudoRandom(pos.xz.mul(3.0)).smoothstep(0.4, 0.6);
  
  return streaks.mul(0.4).add(spots.mul(0.3)).add(cracks.mul(0.3));
}

const material = new THREE.MeshStandardNodeMaterial();

// Base metal: brushed steel
const baseColor = vec3(0.7, 0.7, 0.75);

// Weathering oxidizes the surface to rusty orange
const weathering = weatheringMap();
const weatheredColor = baseColor.mix(
  vec3(0.8, 0.4, 0.1), // Rust orange
  weathering.mul(0.5)
);

material.colorNode = weatheredColor;

// Weathered areas are rougher
material.roughnessNode = float(0.3).mix(0.7, weathering.mul(0.6));

// Metalness slightly reduced by oxidation
material.metalnessNode = float(0.9).mix(0.7, weathering.mul(0.4));

// Add subtle normal variation from weathering
const normalDisplacement = weathering.mul(0.02);
material.normalNode = normalWorld
  .add(vec3(normalDisplacement, normalDisplacement, normalDisplacement))
  .normalize();
```

**What it does:**
- Creates brushed steel base color
- Adds procedural weathering patterns (streaks, rust spots, cracks)
- Changes material properties (roughness/metalness) based on weathering
- Result: realistic aged metal surface

---

### Example 4: Energy/Holographic Effect

```typescript
import { tsl as TSL } from 'three/webgpu';
import * as THREE from 'three/webgpu';

const {
  vec3, vec4, float, sin, cos, time,
  positionWorld, normalWorld, screenUV, cameraPosition,
  uv, clamp, mix, dot, length, normalize,
  smoothstep, PI, TWO_PI
} = TSL;

const material = new THREE.MeshStandardNodeMaterial();

// Holographic scanlines
const scanlines = sin(screenUV.y.mul(200)).mul(0.3).add(0.7);

// Emission pulse from center
const distFromCenter = length(positionWorld.xz);
const pulse = sin(time.mul(3).sub(distFromCenter.mul(5))).mul(0.5).add(0.5);

// Rainbow gradient (hue shift)
const hue = atan(positionWorld.x, positionWorld.z).div(PI).add(time.mul(0.2));
const rainbowPhase = hue.mul(3);

// Shimmer effect based on view angle
const viewDir = normalize(cameraPosition.sub(positionWorld));
const rim = float(1).sub(dot(normalWorld, viewDir));
const shimmer = smoothstep(0.3, 0.8, rim);

// Combine effects
const emissiveBase = vec3(0, 0.8, 1); // Cyan
const emission = emissiveBase
  .mul(pulse.mul(2))
  .mul(scanlines)
  .mul(mix(1, shimmer, 0.5));

material.colorNode = vec3(0, 0.1, 0.15);
material.emissiveNode = emission;
material.roughnessNode = float(0.5);
material.metalness = float(0.6);

// Pulsing transparency
material.opacityNode = pulse.mul(0.3).add(0.7);
```

**What it does:**
- Creates cyan holographic glow with scanlines
- Pulsing emission that varies with distance
- Rainbow shimmer based on view angle
- Result: sci-fi energy shield or hologram

---

### Example 5: Terrain Material with Height-Based Blending

```typescript
import { tsl as TSL } from 'three/webgpu';
import * as THREE from 'three/webgpu';

const {
  vec3, vec4, float, sin, cos,
  positionWorld, normalWorld, uv,
  texture, clamp, mix, smoothstep,
  cross, normalize, dot
} = TSL;

// Three texture layers: grass, rock, snow
const grassTexture = new THREE.Texture(); // Green
const rockTexture = new THREE.Texture();   // Gray
const snowTexture = new THREE.Texture();   // White

function terrainMaterial() {
  // Height ranges
  const height = positionWorld.y;
  const grassHeight = float(0);
  const rockHeight = float(5);
  const snowHeight = float(10);
  
  // Blending based on height with smooth transitions
  const grassBlend = smoothstep(grassHeight.add(2), grassHeight, height);
  const rockBlend = smoothstep(rockHeight, grassHeight, height)
    .mul(smoothstep(snowHeight, rockHeight, height));
  const snowBlend = smoothstep(snowHeight.sub(2), snowHeight, height);
  
  // Sample all three textures
  const grassColor = texture(grassTexture, uv().mul(3)); // Tiled 3x
  const rockColor = texture(rockTexture, uv().mul(2));   // Tiled 2x
  const snowColor = texture(snowTexture, uv().mul(1));   // Not tiled
  
  // Blend colors
  const color = grassColor
    .mul(grassBlend)
    .add(rockColor.mul(rockBlend))
    .add(snowColor.mul(snowBlend));
  
  // Adjust roughness by elevation
  const roughness = float(0.7)
    .mix(0.4, rockBlend)      // Rock is smoother
    .mix(0.3, snowBlend);     // Snow is smoothest
  
  // Slope affects material choice (steep = more rock)
  const slope = float(1).sub(dot(normalWorld, vec3(0, 1, 0)));
  const finalRoughness = roughness.mix(0.8, slope.mul(0.5));
  
  const material = new THREE.MeshStandardNodeMaterial();
  material.colorNode = color;
  material.roughnessNode = finalRoughness;
  material.metalnessNode = float(0);
  
  return material;
}
```

**What it does:**
- Blends three textures (grass, rock, snow) based on height
- Smoothly transitions between materials
- Adjusts roughness for realistic surfaces
- Accounts for slope in material distribution
- Result: natural terrain with height-based detail

---

## Custom TSL Functions

You can create reusable functions with `Fn`:

```typescript
import { tsl as TSL } from 'three/webgpu';
const { Fn, vec3, vec2, sin, cos, PI } = TSL;

// Function signature: types → logic → returns
const cartesianToPolar = Fn(
  [ vec2 ],  // Input: 2D position
  (pos) => {
    const r = pos.length();
    const theta = atan(pos.y, pos.x);
    return vec2(r, theta);
  }
  // Returns: vec2 (radius, angle)
);

// Function with multiple parameters
const mix3 = Fn(
  [ vec3, vec3, vec3, float ],  // v1, v2, v3, blend (0-1-2)
  (v1, v2, v3, t) => {
    return v1
      .mix(v2, clamp(t, 0, 1))              // t in [0,1] → blend v1-v2
      .mix(v3, clamp(t.sub(1), 0, 1));     // t in [1,2] → blend v2-v3
  }
);

// Function with side effects
const waveDeformation = Fn(
  [ vec3, float, float ],  // position, time, scale
  (pos, time, scale) => {
    const wave1 = sin(pos.x.add(time).mul(scale));
    const wave2 = cos(pos.z.add(time).mul(scale.mul(0.7)));
    return pos.add(vec3(wave1, 0, wave2).mul(0.1));
  }
);

// Usage in materials
const material = new THREE.MeshStandardNodeMaterial();
material.positionNode = waveDeformation(positionLocal, time, 3.0);
const polar = cartesianToPolar(uv());
```

---

## TSL vs ShaderMaterial: Side-by-Side Comparison

### Same Effect: Animated Stripes

**ShaderMaterial (GLSL):**
```typescript
const material = new THREE.ShaderMaterial({
  uniforms: {
    uTime: { value: 0 },
    uScale: { value: 5 },
  },
  vertexShader: `
    varying vec3 vPosition;
    void main() {
      vPosition = position;
      gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    }
  `,
  fragmentShader: `
    uniform float uTime;
    uniform float uScale;
    varying vec3 vPosition;
    void main() {
      float stripe = sin(vPosition.x * uScale + uTime);
      stripe = stripe * 0.5 + 0.5;  // Remap to [0, 1]
      gl_FragColor = vec4(stripe, stripe * 0.5, 1.0, 1.0);
    }
  `,
});

// Update uniform each frame
material.uniforms.uTime.value += 0.016;
```

**TSL (Node Material):**
```typescript
const material = new THREE.MeshStandardNodeMaterial();
const { positionLocal, sin, time } = TSL;

material.colorNode = (function() {
  const stripe = sin(
    positionLocal.x.mul(5).add(time)
  ).mul(0.5).add(0.5);
  
  return vec3(stripe, stripe.mul(0.5), 1);
})();

// No manual uniform updates—TSL handles it
```

**Advantages of TSL:**
- ✅ No manual uniform tracking
- ✅ Automatic type checking
- ✅ Compiles to both GLSL (WebGL) and WGSL (WebGPU)
- ✅ Reusable nodes across multiple materials
- ✅ Built-in optimizations

---

## Performance Characteristics of TSL

### Node Graph Compilation

TSL compiles node graphs into optimized shaders. Complex graphs may add compilation overhead:

```typescript
// ✅ EFFICIENT: One material, shared nodes
const baseColor = vec3(1, 0, 0);
const metalMaterial = new THREE.MeshStandardNodeMaterial();
metalMaterial.colorNode = baseColor;

const glassMaterial = new THREE.MeshPhysicalNodeMaterial();
glassMaterial.colorNode = baseColor;  // Reuses same node


// ❌ INEFFICIENT: Many unique node combinations
for (let i = 0; i < 1000; i++) {
  const mat = new THREE.MeshStandardNodeMaterial();
  mat.colorNode = vec3(Math.random(), Math.random(), Math.random());
  // Creates 1000 unique node graphs → slow compilation
}
```

### Optimization Tips

1. **Reuse nodes:** Cache expensive computations
   ```typescript
   const noise = turbulence(positionWorld);
   material.colorNode = noise;
   material.roughnessNode = noise.mul(0.5).add(0.25);
   ```

2. **Avoid deep nesting:** Each operation adds complexity
   ```typescript
   // ❌ Deep: sin(sin(sin(x)))
   const val = sin(sin(sin(x)));
   
   // ✅ Flat: store intermediate
   const v1 = sin(x);
   const v2 = sin(v1);
   const val = sin(v2);
   ```

3. **Use Const for static values:**
   ```typescript
   const { Const } = TSL;
   const PI = Const(3.14159);  // Optimized away
   ```

4. **Measure with DevTools:** Profile shader compilation time in Performance tab

---

## Common Node Operations Reference

| Operation | TSL Code | Notes |
|-----------|----------|-------|
| Add | `a.add(b)` | Component-wise |
| Multiply | `a.mul(b)` | Component-wise |
| Mix (lerp) | `a.mix(b, t)` | Linear interpolation |
| Clamp | `x.clamp(0, 1)` | Clamp to range |
| Normalize | `v.normalize()` | Unit vector |
| Length | `v.length()` | Magnitude |
| Dot product | `dot(a, b)` | Scalar result |
| Cross product | `cross(a, b)` | vec3 only |
| Smoothstep | `x.smoothstep(a, b)` | Smooth transition |
| If/Else | `If(cond, trueVal, falseVal)` | Conditional |
| Texture sample | `texture(tex, uv)` | Fetch texel |

