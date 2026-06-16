# GPU Compute & High-Performance Rendering Patterns

## Compute Shader Fundamentals in Three.js

### What are Compute Shaders?

Compute shaders are GPU programs that **run arbitrary parallel computations**, not just rendering. Each GPU thread executes independently on data:

```typescript
// CPU approach: update 1M particles in JavaScript
for (let i = 0; i < 1000000; i++) {
  particles[i].x += particles[i].vx * dt;
  particles[i].y += particles[i].vy * dt;
  particles[i].vy -= 9.81 * dt;  // gravity
}
// Result: ~50ms per frame (too slow)

// GPU compute approach: parallel on GPU
// 1M particles updated in <1ms
```

### Setup: Compute Shader in Three.js

```typescript
import { tsl as TSL } from 'three/webgpu';
import * as THREE from 'three/webgpu';

// 1. Create storage buffer (GPU memory)
const particleCount = 100000;
const particlesData = new Float32Array(particleCount * 6); // pos.xyz + vel.xyz

// Initialize with random positions
for (let i = 0; i < particleCount * 6; i += 6) {
  particlesData[i] = (Math.random() - 0.5) * 10;     // x
  particlesData[i + 1] = (Math.random() - 0.5) * 10; // y
  particlesData[i + 2] = (Math.random() - 0.5) * 10; // z
  particlesData[i + 3] = (Math.random() - 0.5);      // vx
  particlesData[i + 4] = (Math.random() - 0.5);      // vy
  particlesData[i + 5] = (Math.random() - 0.5);      // vz
}

// 2. Define compute shader (WGSL)
const computeShaderCode = `
  struct Particle {
    pos: vec3<f32>,
    vel: vec3<f32>,
  }
  
  @group(0) @binding(0) var<storage, read_write> particles: array<Particle>;
  
  @compute @workgroup_size(64)
  fn updateParticles(
    @builtin(global_invocation_id) global_id: vec3<u32>,
  ) {
    let idx = global_id.x;
    if (idx >= ${particleCount}u) { return; }
    
    let gravity = vec3<f32>(0.0, -9.81, 0.0);
    let dt = 0.016;  // 60 FPS
    
    // Update velocity
    particles[idx].vel += gravity * dt;
    
    // Update position
    particles[idx].pos += particles[idx].vel * dt;
    
    // Bounce on ground
    if (particles[idx].pos.y < -5.0) {
      particles[idx].pos.y = -5.0;
      particles[idx].vel.y *= -0.8;  // Damping
    }
  }
`;

// 3. Create compute pipeline
const computeModule = device.createShaderModule({
  code: computeShaderCode,
});

const computePipeline = device.createComputePipeline({
  layout: 'auto',
  compute: { module: computeModule, entryPoint: 'updateParticles' },
});

// 4. Create bind group (resource binding)
const particlesBuffer = device.createBuffer({
  size: particlesData.byteLength,
  usage: GPUBufferUsage.STORAGE | GPUBufferUsage.COPY_SRC,
  mappedAtCreation: true,
});
new Float32Array(particlesBuffer.getMappedRange()).set(particlesData);
particlesBuffer.unmap();

const bindGroup = device.createBindGroup({
  layout: computePipeline.getBindGroupLayout(0),
  entries: [
    { binding: 0, resource: { buffer: particlesBuffer } },
  ],
});

// 5. Dispatch compute shader (execute on GPU)
function dispatchCompute() {
  const workgroupCount = Math.ceil(particleCount / 64);
  
  const commandEncoder = device.createCommandEncoder();
  const computePass = commandEncoder.beginComputePass();
  
  computePass.setPipeline(computePipeline);
  computePass.setBindGroup(0, bindGroup);
  computePass.dispatchWorkgroups(workgroupCount);
  
  computePass.end();
  device.queue.submit([commandEncoder.finish()]);
}

// 6. Read back results (if needed)
async function readbackParticles() {
  const stagingBuffer = device.createBuffer({
    size: particlesData.byteLength,
    usage: GPUBufferUsage.COPY_DST | GPUBufferUsage.MAP_READ,
  });
  
  const commandEncoder = device.createCommandEncoder();
  commandEncoder.copyBufferToBuffer(
    particlesBuffer, 0,
    stagingBuffer, 0,
    particlesData.byteLength
  );
  device.queue.submit([commandEncoder.finish()]);
  
  await stagingBuffer.mapAsync(GPUMapMode.READ);
  const result = new Float32Array(stagingBuffer.getMappedRange()).slice();
  stagingBuffer.unmap();
  return result;
}
```

---

## GPU Particle System (1M+ Particles with Physics)

### Full Implementation

```typescript
import * as THREE from 'three/webgpu';

class GPUParticleSystem {
  constructor(renderer, particleCount = 1000000) {
    this.device = renderer.device;
    this.queue = this.device.queue;
    this.particleCount = particleCount;
    
    this.initBuffers();
    this.initShaders();
    this.initRenderMesh();
  }
  
  initBuffers() {
    // Particle data: position (12 bytes) + velocity (12 bytes) = 24 bytes each
    const totalBytes = this.particleCount * 24;
    
    this.particleBuffer = this.device.createBuffer({
      size: totalBytes,
      usage:
        GPUBufferUsage.STORAGE |
        GPUBufferUsage.COPY_SRC |
        GPUBufferUsage.COPY_DST,
      mappedAtCreation: true,
    });
    
    // Initialize random particles
    const data = new Float32Array(this.particleBuffer.getMappedRange());
    for (let i = 0; i < this.particleCount; i++) {
      const base = i * 6;
      // Position
      data[base] = (Math.random() - 0.5) * 20;
      data[base + 1] = Math.random() * 10;
      data[base + 2] = (Math.random() - 0.5) * 20;
      // Velocity
      data[base + 3] = (Math.random() - 0.5) * 5;
      data[base + 4] = (Math.random() - 0.5) * 5;
      data[base + 5] = (Math.random() - 0.5) * 5;
    }
    this.particleBuffer.unmap();
    
    // Indirect draw buffer (for indirect rendering)
    this.indirectBuffer = this.device.createBuffer({
      size: 16,  // 4 u32 values: vertexCount, instanceCount, firstVertex, firstInstance
      usage: GPUBufferUsage.STORAGE | GPUBufferUsage.INDIRECT,
      mappedAtCreation: true,
    });
    const indirect = new Uint32Array(this.indirectBuffer.getMappedRange());
    indirect[0] = 1;  // vertexCount (1 vertex per particle = point)
    indirect[1] = this.particleCount;
    indirect[2] = 0;
    indirect[3] = 0;
    this.indirectBuffer.unmap();
  }
  
  initShaders() {
    const computeCode = `
      struct Particle {
        pos: vec3<f32>,
        vel: vec3<f32>,
      }
      
      @group(0) @binding(0) var<storage, read_write> particles: array<Particle>;
      @group(0) @binding(1) var<uniform> params: ParticleParams;
      
      struct ParticleParams {
        gravity: f32,
        damping: f32,
        dt: f32,
        _pad: f32,
      }
      
      @compute @workgroup_size(256)
      fn updateParticles(
        @builtin(global_invocation_id) gid: vec3<u32>,
      ) {
        let idx = gid.x;
        if (idx >= ${this.particleCount}u) { return; }
        
        var p = particles[idx];
        
        // Apply forces
        p.vel.y -= params.gravity * params.dt;
        p.vel *= params.damping;
        
        // Update position
        p.pos += p.vel * params.dt;
        
        // Bounce on plane y = 0
        if (p.pos.y < 0.0) {
          p.pos.y = 0.0;
          p.vel.y *= -0.9;
        }
        
        // Clamp to bounds
        let bound = 30.0;
        if (abs(p.pos.x) > bound) { p.vel.x *= -0.8; }
        if (abs(p.pos.z) > bound) { p.vel.z *= -0.8; }
        
        particles[idx] = p;
      }
    `;
    
    const computeModule = this.device.createShaderModule({
      code: computeCode,
    });
    
    this.computePipeline = this.device.createComputePipeline({
      layout: 'auto',
      compute: { module: computeModule, entryPoint: 'updateParticles' },
    });
    
    // Uniform buffer for parameters
    this.paramsBuffer = this.device.createBuffer({
      size: 16,  // 4 floats
      usage: GPUBufferUsage.UNIFORM | GPUBufferUsage.COPY_DST,
    });
    
    this.computeBindGroup = this.device.createBindGroup({
      layout: this.computePipeline.getBindGroupLayout(0),
      entries: [
        { binding: 0, resource: { buffer: this.particleBuffer } },
        { binding: 1, resource: { buffer: this.paramsBuffer } },
      ],
    });
  }
  
  initRenderMesh() {
    // Create point geometry + material for rendering
    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute(
      'position',
      new THREE.BufferAttribute(new Float32Array(this.particleCount * 3), 3)
    );
    
    const material = new THREE.PointsMaterial({
      size: 0.1,
      color: 0x00ff00,
    });
    
    this.points = new THREE.Points(geometry, material);
  }
  
  update(deltaTime) {
    // Update parameters
    const params = new Float32Array([
      9.81,      // gravity
      0.99,      // damping
      deltaTime,
      0,
    ]);
    this.queue.writeBuffer(this.paramsBuffer, 0, params);
    
    // Dispatch compute
    const commandEncoder = this.device.createCommandEncoder();
    const computePass = commandEncoder.beginComputePass();
    
    computePass.setPipeline(this.computePipeline);
    computePass.setBindGroup(0, this.computeBindGroup);
    const workgroupCount = Math.ceil(this.particleCount / 256);
    computePass.dispatchWorkgroups(workgroupCount);
    
    computePass.end();
    this.queue.submit([commandEncoder.finish()]);
  }
  
  getMesh() {
    return this.points;
  }
}

// Usage
const particleSystem = new GPUParticleSystem(renderer, 1000000);
scene.add(particleSystem.getMesh());

function animate() {
  particleSystem.update(0.016);  // 60 FPS
  renderer.render(scene, camera);
}
renderer.setAnimationLoop(animate);
```

---

## GPU Frustum Culling for InstancedMesh

Cull invisible instances before rendering:

```typescript
class GPUFrustumCull {
  constructor(device, maxInstanceCount = 100000) {
    this.device = device;
    this.maxInstanceCount = maxInstanceCount;
    
    // Storage buffer: instance visibility (1 = visible, 0 = culled)
    this.visibilityBuffer = device.createBuffer({
      size: maxInstanceCount * 4,  // 1 u32 per instance
      usage: GPUBufferUsage.STORAGE | GPUBufferUsage.COPY_SRC,
      mappedAtCreation: true,
    });
    new Uint32Array(this.visibilityBuffer.getMappedRange()).fill(1);
    this.visibilityBuffer.unmap();
    
    // Indirect draw buffer (updated by compute)
    this.indirectBuffer = device.createBuffer({
      size: 16,
      usage: GPUBufferUsage.INDIRECT | GPUBufferUsage.STORAGE,
      mappedAtCreation: true,
    });
    const indirect = new Uint32Array(this.indirectBuffer.getMappedRange());
    indirect.set([1, 0, 0, 0]);  // Will be written by compute
    this.indirectBuffer.unmap();
    
    // Camera params
    this.cameraBuffer = device.createBuffer({
      size: 128,  // projection matrix + frustum planes
      usage: GPUBufferUsage.UNIFORM | GPUBufferUsage.COPY_DST,
    });
    
    this.initComputeShader();
  }
  
  initComputeShader() {
    const code = `
      struct AABB {
        minPos: vec3<f32>,
        maxPos: vec3<f32>,
      }
      
      struct CameraData {
        projMatrix: mat4x4<f32>,
      }
      
      @group(0) @binding(0) var<storage, read_write> visibility: array<atomic<u32>>;
      @group(0) @binding(1) var<storage, read> aabbs: array<AABB>;
      @group(0) @binding(2) var<uniform> camera: CameraData;
      @group(0) @binding(3) var<storage, read_write> indirect: array<u32, 4>;
      
      fn isInsideFrustum(aabb: AABB, proj: mat4x4<f32>) -> bool {
        // Simplified: test AABB corners against clip space
        let p0 = proj * vec4<f32>(aabb.minPos, 1.0);
        let p1 = proj * vec4<f32>(aabb.maxPos, 1.0);
        
        // Perspective divide and NDC test
        let ndc0 = p0.xyz / p0.w;
        let ndc1 = p1.xyz / p1.w;
        
        // In frustum if any part overlaps [-1, 1]³
        return max(ndc0, ndc1).x >= -1.0 && min(ndc0, ndc1).x <= 1.0
            && max(ndc0, ndc1).y >= -1.0 && min(ndc0, ndc1).y <= 1.0
            && max(ndc0, ndc1).z >= -1.0 && min(ndc0, ndc1).z <= 1.0;
      }
      
      @compute @workgroup_size(256)
      fn cullInstances(
        @builtin(global_invocation_id) gid: vec3<u32>,
      ) {
        let idx = gid.x;
        
        let visible = isInsideFrustum(aabbs[idx], camera.projMatrix);
        atomicStore(&visibility[idx], u32(visible));
        
        if (visible) {
          atomicAdd(&indirect[1], 1u);  // Increment instance count
        }
      }
    `;
    
    const module = this.device.createShaderModule({ code });
    this.pipeline = this.device.createComputePipeline({
      layout: 'auto',
      compute: { module, entryPoint: 'cullInstances' },
    });
  }
  
  updateCamera(projectionMatrix) {
    const data = new Float32Array(projectionMatrix.elements);
    this.device.queue.writeBuffer(this.cameraBuffer, 0, data);
  }
  
  cull(aabbBuffer, instanceCount) {
    this.bindGroup = this.device.createBindGroup({
      layout: this.pipeline.getBindGroupLayout(0),
      entries: [
        { binding: 0, resource: { buffer: this.visibilityBuffer } },
        { binding: 1, resource: { buffer: aabbBuffer } },
        { binding: 2, resource: { buffer: this.cameraBuffer } },
        { binding: 3, resource: { buffer: this.indirectBuffer } },
      ],
    });
    
    const encoder = this.device.createCommandEncoder();
    const pass = encoder.beginComputePass();
    
    pass.setPipeline(this.pipeline);
    pass.setBindGroup(0, this.bindGroup);
    pass.dispatchWorkgroups(Math.ceil(instanceCount / 256));
    
    pass.end();
    this.device.queue.submit([encoder.finish()]);
  }
}
```

---

## Spatial Hashing on GPU

Build spatial grid for collision detection:

```typescript
// Compute shader: spatial hashing
const spatialHashCode = `
  struct Particle {
    pos: vec3<f32>,
    vel: vec3<f32>,
  }
  
  @group(0) @binding(0) var<storage, read> particles: array<Particle>;
  @group(0) @binding(1) var<storage, read_write> grid: array<atomic<u32>>;
  @group(0) @binding(2) var<uniform> params: GridParams;
  
  struct GridParams {
    gridSize: u32,      // Number of cells per axis
    cellSize: f32,      // World space size of one cell
  }
  
  fn spatialHash(pos: vec3<f32>, gridSize: u32, cellSize: f32) -> u32 {
    let gridCoord = vec3<u32>(floor(pos / cellSize)) % vec3<u32>(gridSize);
    return gridCoord.x + gridCoord.y * gridSize + gridCoord.z * gridSize * gridSize;
  }
  
  @compute @workgroup_size(256)
  fn buildGrid(
    @builtin(global_invocation_id) gid: vec3<u32>,
  ) {
    let idx = gid.x;
    let p = particles[idx];
    let cellIdx = spatialHash(p.pos, params.gridSize, params.cellSize);
    
    // Increment count for this cell
    atomicAdd(&grid[cellIdx], 1u);
  }
`;
```

---

## LOD Selection on GPU

Select geometry detail level based on distance:

```typescript
// Compute shader: LOD assignment
const lodCode = `
  struct Instance {
    position: vec3<f32>,
    scale: f32,
    lod: u32,
    _pad: vec3<u32>,
  }
  
  @group(0) @binding(0) var<storage, read_write> instances: array<Instance>;
  @group(0) @binding(1) var<uniform> camera: CameraData;
  
  @compute @workgroup_size(256)
  fn assignLOD(
    @builtin(global_invocation_id) gid: vec3<u32>,
  ) {
    let idx = gid.x;
    let inst = instances[idx];
    
    let distToCamera = distance(inst.position, camera.position);
    
    // Choose LOD based on distance
    if (distToCamera < 10.0) {
      instances[idx].lod = 0u;  // High detail
    } else if (distToCamera < 50.0) {
      instances[idx].lod = 1u;  // Medium detail
    } else if (distToCamera < 200.0) {
      instances[idx].lod = 2u;  // Low detail
    } else {
      instances[idx].lod = 3u;  // Billboard
    }
  }
`;
```

---

## Clustered Lighting Setup (100+ Lights)

Organize lights in screen-space clusters for deferred rendering:

```typescript
class ClusteredLighting {
  constructor(renderer, tileSize = 16) {
    this.tileSize = tileSize;
    this.screenWidth = renderer.width;
    this.screenHeight = renderer.height;
    
    this.tilesX = Math.ceil(this.screenWidth / tileSize);
    this.tilesY = Math.ceil(this.screenHeight / tileSize);
    this.tileCount = this.tilesX * this.tilesY;
    
    this.initBuffers();
  }
  
  initBuffers() {
    // Light list: max lights per tile
    const maxLightsPerTile = 64;
    this.lightIndexBuffer = this.device.createBuffer({
      size: this.tileCount * maxLightsPerTile * 4,
      usage: GPUBufferUsage.STORAGE,
    });
    
    // Light count per tile
    this.lightCountBuffer = this.device.createBuffer({
      size: this.tileCount * 4,
      usage: GPUBufferUsage.STORAGE | GPUBufferUsage.COPY_DST,
    });
  }
  
  assignLightsToTiles(lightDataBuffer, lightCount) {
    // Compute shader: assign lights to tiles
    const code = `
      @compute @workgroup_size(16, 16)
      fn clusterLights(
        @builtin(global_invocation_id) gid: vec3<u32>,
      ) {
        let tileCoord = gid.xy;
        let tileIdx = tileCoord.x + tileCoord.y * ${this.tilesX}u;
        
        // For each light, check if it overlaps this tile
        var lightCount = 0u;
        for (var i = 0u; i < ${lightCount}u; i++) {
          let light = lights[i];
          
          // Sphere-to-tile AABB test
          let tileMin = vec2<f32>(tileCoord) * ${this.tileSize}.0;
          let tileMax = tileMin + vec2<f32>(${this.tileSize}.0);
          
          let closest = clamp(light.position.xy, tileMin, tileMax);
          let dist = distance(light.position.xy, closest);
          
          if (dist <= light.radius) {
            lightIndices[tileIdx * 64u + lightCount] = i;
            lightCount++;
            if (lightCount >= 64u) { break; }
          }
        }
        
        lightCounts[tileIdx] = lightCount;
      }
    `;
  }
}
```

---

## Indirect Draw Calls Pattern

GPU generates draw commands without CPU involvement:

```typescript
// Compute shader: generate draw commands
const indirectDrawCode = `
  struct DrawCommand {
    vertexCount: u32,
    instanceCount: u32,
    firstVertex: u32,
    firstInstance: u32,
  }
  
  @group(0) @binding(0) var<storage, read_write> commands: array<DrawCommand>;
  @group(0) @binding(1) var<storage, read> visibility: array<u32>;
  
  @compute @workgroup_size(64)
  fn buildDrawCommands(
    @builtin(global_invocation_id) gid: vec3<u32>,
  ) {
    let batchIdx = gid.x;
    var visibleCount = 0u;
    
    // Count visible instances in batch
    for (var i = 0u; i < 1000u; i++) {
      if (visibility[batchIdx * 1000u + i] != 0u) {
        visibleCount++;
      }
    }
    
    // Fill draw command (GPU-driven)
    commands[batchIdx].vertexCount = 36u;  // Cube vertices
    commands[batchIdx].instanceCount = visibleCount;
    commands[batchIdx].firstVertex = 0u;
    commands[batchIdx].firstInstance = batchIdx * 1000u;
  }
`;

// Rendering with indirect:
function renderIndirect(renderPass, indirectBuffer, drawCount) {
  renderPass.drawIndirect(indirectBuffer, 0);
}
```

---

## Object Pooling & Memory Management

Prevent GC pressure with large object counts:

```typescript
class ObjectPool {
  constructor(ObjectClass, initialSize = 1000) {
    this.ObjectClass = ObjectClass;
    this.available = [];
    this.inUse = new Set();
    
    // Pre-allocate pool
    for (let i = 0; i < initialSize; i++) {
      this.available.push(new ObjectClass());
    }
  }
  
  acquire() {
    let obj;
    if (this.available.length > 0) {
      obj = this.available.pop();
    } else {
      obj = new this.ObjectClass();
    }
    this.inUse.add(obj);
    return obj;
  }
  
  release(obj) {
    obj.reset?.();  // Call reset if available
    this.inUse.delete(obj);
    this.available.push(obj);
  }
  
  clear() {
    this.available = [];
    this.inUse.clear();
  }
}

// Usage
const particlePool = new ObjectPool(Particle, 100000);

function emitParticles(count) {
  for (let i = 0; i < count; i++) {
    const p = particlePool.acquire();
    p.init(Math.random() * 10, Math.random() * 10);
  }
}

function updateParticles() {
  for (const p of particlePool.inUse) {
    p.update(deltaTime);
    if (p.isDead) {
      particlePool.release(p);
    }
  }
}
```

---

## Performance Profiling Workflow

### What to Measure

1. **CPU Time:** Time spent on main thread
   - DevTools > Performance > Record frame
   - Look for JS execution peaks

2. **GPU Time:** Time spent in shaders
   - WebGPU has limited built-in timing (use GPU timestamps)
   - Frame time = CPU prep + GPU execution
   - If frame is 60fps but GPU alone is 50ms, GPU is bottleneck

3. **Memory:** GPU memory usage
   - DevTools > Memory tab (limited visibility)
   - Rule of thumb: 1M vertices = ~50MB

4. **Draw Call Count:** Fewer is better
   - Target: 1000 draw calls at 60fps on mid-range GPU
   - Use InstancedMesh or indirect draws for more

### Profiling Code

```typescript
class GPUProfiler {
  constructor(device) {
    this.device = device;
    this.querySet = device.createQuerySet({
      type: 'timestamp',
      count: 10,
    });
  }
  
  measureFrame(renderFn) {
    const start = performance.now();
    
    // Render
    renderFn();
    
    const end = performance.now();
    console.log(`Frame time: ${(end - start).toFixed(2)}ms`);
  }
}

// Usage
const profiler = new GPUProfiler(renderer.device);

function animate() {
  profiler.measureFrame(() => {
    renderer.render(scene, camera);
  });
}
```

---

## Scaling Checklist: Render 10,000 Objects at 60fps

### Step 1: Choose Rendering Strategy
- [ ] Verify WebGPU available (`navigator.gpu`)
- [ ] Use WebGPURenderer with async init
- [ ] Have WebGL 2 fallback ready

### Step 2: Geometry Optimization
- [ ] Use merged geometry if static
- [ ] Consider LOD (high/medium/low/billboard)
- [ ] Measure triangle count per object

### Step 3: Use Instancing or GPU-Driven Rendering
- [ ] InstancedMesh for 1000-5000 objects
- [ ] Compute shader + indirect draw for 5000+
- [ ] Keep matrix updates on GPU (not CPU)

### Step 4: Culling
- [ ] Frustum cull on GPU
- [ ] Occlude-away distant objects
- [ ] Use spatial hashing for proximity queries

### Step 5: Lighting
- [ ] Use clustered lighting (not per-light loop)
- [ ] Limit light count (8-16 per pixel)
- [ ] Defer light evaluation to fragment shader

### Step 6: Materials
- [ ] Use TSL node materials (single compilation)
- [ ] Minimize unique material count
- [ ] Cache compiled materials

### Step 7: Post-Processing
- [ ] Use node-based post FX (efficient)
- [ ] Reduce render target resolution if needed
- [ ] Bloom + FXAA = typical pipeline

### Step 8: Profile & Iterate
- [ ] Measure frame time breakdown (CPU vs GPU)
- [ ] Profile memory (should be <2GB for typical)
- [ ] Test on target hardware (not just dev machine)

---

## Browser Compatibility Detection & Fallback

```typescript
async function initGraphics() {
  // Check for WebGPU
  if (!navigator.gpu) {
    console.log('WebGPU not supported');
    return initWebGL();
  }
  
  try {
    const adapter = await navigator.gpu.requestAdapter({
      powerPreference: 'high-performance',
    });
    
    if (!adapter) {
      console.log('No suitable GPU adapter');
      return initWebGL();
    }
    
    const device = await adapter.requestDevice();
    const renderer = new THREE.WebGPURenderer();
    await renderer.init();
    
    return renderer;
  } catch (error) {
    console.error('WebGPU init failed:', error);
    return initWebGL();
  }
}

function initWebGL() {
  const renderer = new THREE.WebGLRenderer({ antialias: true });
  // WebGL 2 fallback—use ShaderMaterial instead of TSL
  return renderer;
}

// Usage
const renderer = await initGraphics();
```

### Feature Detection Pattern

```typescript
const hasWebGPU = !!navigator.gpu;
const hasSharedArrayBuffer = typeof SharedArrayBuffer !== 'undefined';
const hasComputeShaders = hasWebGPU;  // WebGPU only
const hasIndirectDraw = hasWebGPU;   // WebGPU only
const hasInstancing = hasWebGPU || hasWebGL2;

// Choose strategy based on capabilities
if (hasIndirectDraw) {
  // Use GPU-driven rendering (10k+ objects)
} else if (hasInstancing) {
  // Use InstancedMesh (1k-5k objects)
} else {
  // CPU-based batching
}
```

