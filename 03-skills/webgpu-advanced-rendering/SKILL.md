---
name: webgpu-advanced-rendering
description: >
  Expert WebGPU rendering and Three.js TSL specialist. Trigger on: WebGPU, WebGPURenderer, 
  TSL, Three Shading Language, node material, compute shader, GPU particles, GPU culling, 
  clustered lighting, WGSL, advanced rendering, performance optimization, thousands of 
  objects, instancing, indirect draw, bindless textures, or any question about 
  high-performance 3D rendering on the web. Generates production-ready WebGPU-optimized 
  Three.js code and complex TSL node materials for cutting-edge visual effects.
aliases: [webgpu-advanced-rendering]
spec_version: "2.0"
tier: spoke
domain: game
hub: lead-game-developer
prerequisites: [lead-game-developer, science-foundations, imaging-foundations]
---

# WebGPU Advanced Rendering & Three.js TSL

## Core Identity

You are a **WebGPU and advanced rendering specialist**. You help developers:
- Migrate Three.js projects from WebGL to WebGPU
- Write high-performance TSL (Three Shading Language) materials
- Build GPU compute shaders for particles, physics, and culling
- Scale rendering to thousands of objects at 60fps
- Master modern GPU-driven rendering patterns

This skill covers **production-ready techniques** as of r171+ (March 2026).

---

## WebGPURenderer Setup Pattern

Every WebGPU project needs async initialization and graceful fallback:

```typescript
import * as THREE from 'three/webgpu';

async function initRenderer() {
  const renderer = new THREE.WebGPURenderer({ antialias: true });
  renderer.setPixelRatio(window.devicePixelRatio);
  renderer.setSize(window.innerWidth, window.innerHeight);
  
  // CRITICAL: Must await before rendering
  await renderer.init();
  
  document.body.appendChild(renderer.domElement);
  return renderer;
}

// Fallback detection
if (!navigator.gpu) {
  console.log('WebGPU not supported, would load WebGL fallback');
}
```

**Key points:**
- `await renderer.init()` is mandatory—requests GPU adapter/device
- Async initialization is the biggest API difference vs WebGLRenderer
- Use `forceWebGL: true` option for testing fallback behavior

---

## TSL Quick Reference

### Node Imports
```typescript
import { tsl as TSL } from 'three/webgpu';
const {
  // Core
  vec3, vec4, float, int, Var, Const, Fn,
  // Vertex data
  positionLocal, normalLocal, uv,
  positionWorld, normalWorld,
  // Camera/Screen
  cameraPosition, screenUV, time,
  // Math
  sin, cos, clamp, mix, length, normalize, cross,
  // Sampling
  texture, cubeTexture,
  // Control
  If, Switch, Loop,
} = TSL;
```

### Creating a Basic TSL Material
```typescript
const material = new THREE.MeshStandardNodeMaterial();

// Animated color from time
material.colorNode = vec3(
  sin(time.mul(0.001)).mul(0.5).add(0.5),
  0.3,
  1.0
);

// Procedural normal
const wave = sin(positionWorld.x.add(time.mul(0.002)));
material.normalNode = normalWorld.add(vec3(wave, 0, 0)).normalize();

// Roughness mapped by altitude
material.roughnessNode = positionWorld.y.div(10).clamp(0, 1);
```

---

## TSL vs ShaderMaterial: Decision Framework

| Scenario | Use TSL | Use ShaderMaterial |
|----------|---------|-------------------|
| New WebGPU project | ✅ Yes | ❌ Not supported |
| Complex node graphs | ✅ Yes | Not needed |
| WebGL + WebGPU target | ✅ Yes | Write 2× code |
| Simple color tweak | ✅ Yes | Possible but verbose |
| Custom vertex displacement | ✅ Yes | Possible but verbose |
| Legacy GLSL code | ❌ Migrate to TSL | Keep as-is for WebGL |

**Rule:** Always use TSL on WebGPURenderer. It compiles to both GLSL (WebGL fallback) and WGSL (WebGPU) automatically.

---

## Compute Shaders: Concept & Why They Matter

### What They Are
Compute shaders are **GPU programs that run arbitrary parallel code**, not just rendering. Each GPU thread runs independently.

**Performance reality:**
- CPU particle update: ~10k particles at 60fps
- GPU compute shader: 1 million particles at 60fps (<1ms overhead)

### Why Games Use Them
1. **Particles & Physics:** 1M+ particles with velocity/acceleration updates
2. **GPU Culling:** Frustum/occlusion culling on GPU (no CPU roundtrip)
3. **LOD Selection:** Choose detail level based on distance (computed in parallel)
4. **Spatial Hashing:** Build spatial grids for collision detection
5. **Clustered Lighting:** Sort lights by screen space for deferred rendering

### Basic Pattern in Three.js
```typescript
import { tsl as TSL } from 'three/webgpu';

// Create storage buffer
const particlesData = new Float32Array(1000 * 6); // pos.xyz + vel.xyz
const particlesBuffer = TSL.storageBuffer(particlesData);

// Define compute shader
const updateShader = TSL.Fn(
  [TSL.uint],
  (idx) => {
    const pos = particlesBuffer.load(idx).xyz;
    const vel = particlesBuffer.load(idx).zw;
    // Update logic...
    particlesBuffer.store(idx, newData);
  }
);

// Dispatch (runs in parallel)
renderer.compute(updateShader, 1000 / 64); // 1000 particles, 64 per workgroup
```

---

## Performance Scaling Strategies

### 1. Instancing (10–1000 objects)
```typescript
const geometry = new THREE.BoxGeometry();
const material = new THREE.MeshStandardNodeMaterial();
const count = 500;

const mesh = new THREE.InstancedMesh(geometry, material, count);

// Per-instance data
for (let i = 0; i < count; i++) {
  mesh.setMatrixAt(i, new THREE.Matrix4().setPosition(x, y, z));
}
mesh.instanceMatrix.needsUpdate = true;
```

**When to use:** 500–5000 identical objects. Still CPU-bounded at high counts.

### 2. GPU Instancing + Compute (1000–10,000 objects)
Compute shader updates matrices in storage buffer; GPU-driven rendering reads them.

**When to use:** 5k–50k objects with dynamic behavior.

### 3. Indirect Draw Calls (10,000+ objects)
Commands are generated on GPU; CPU never touches per-object state.

**When to use:** 50k+ objects, extreme scale.

### 4. LOD (Level of Detail)
High poly → medium poly → low poly → billboard, based on distance.

**When to use:** Massive scenes with mixed complexity.

---

## When to Optimize

**Measure first:**
- Profile with DevTools: Timeline tab, GPU metrics
- Identify bottleneck: CPU? GPU? Memory bandwidth?
- WebGPU is not universally faster—benefits are scenario-dependent

**WebGPU wins:**
- 100+ draw calls
- Compute-heavy workloads (particles, physics, culling)
- Complex post-processing chains

**WebGL still competitive:**
- Few objects (<50)
- Static geometry
- Low-compute scenarios

---

## References

For detailed techniques and code examples, see:
- **TSL Materials & Patterns:** `references/tsl-materials.md`
  - Animated procedural textures
  - Glass/transmission effects
  - Custom TSL functions
  - Complete code examples

- **GPU Compute & Performance:** `references/gpu-compute-performance.md`
  - Particle systems (1M+)
  - Frustum culling on GPU
  - Clustered lighting setup
  - Scaling checklist (10,000 objects at 60fps)
  - Performance profiling workflow

---

## Browser Support (2026)

| Browser | Support | Version |
|---------|---------|---------|
| Chrome/Edge | ✅ Shipped | 113+ |
| Firefox | ✅ Shipped | 141+ (Windows), 145+ (macOS) |
| Safari | ✅ Shipped | 18+ |
| **Coverage** | **~95%** | Remaining 5% get WebGL fallback |

**Deployment:** Ship WebGPU code with WebGL 2 fallback for legacy browsers. Use feature detection:
```typescript
if (navigator.gpu) {
  // WebGPU path
} else {
  // WebGL 2 fallback
}
```

---

## Quick Troubleshooting

| Issue | Solution |
|-------|----------|
| "Renderer not initialized" | Call `await renderer.init()` before rendering |
| ShaderMaterial doesn't work | Migrate to TSL + Node Materials |
| Compute shader not running | Check workgroup size ≤ 256 threads |
| Low FPS with many objects | Profile CPU vs GPU; consider LOD or culling |
| Texture not appearing | Use `texture(textureResource, uvCoords)` not direct sampling |

## Related
- foundation → [[imaging-foundations]] · [[science-foundations]]
- hub → [[lead-game-developer]]
- peer ↔ [[realtime-render-performance]]
