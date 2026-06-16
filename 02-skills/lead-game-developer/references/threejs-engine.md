# Three.js Fundamentals & Web Game Architecture for Legion

Deep dive into Three.js: the 3D graphics engine powering Legion on the web. Rendering, asset loading, performance, and how to build a game runtime.

## Three.js Core Concepts

Three.js abstracts WebGL into a simple 3D API. Every game needs these pieces:

### Scene, Camera, Renderer

```typescript
// The scene holds all 3D objects (like a container or world)
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x000000);

// The camera defines what we see (like a film camera)
const camera = new THREE.PerspectiveCamera(
  75,                                   // field of view (degrees)
  window.innerWidth / window.innerHeight, // aspect ratio
  0.1,                                  // near clipping plane
  100000                                // far clipping plane (far enough for a galaxy)
);
camera.position.set(0, 500, 500);

// The renderer draws the scene using WebGL or WebGPU
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(window.devicePixelRatio);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFShadowShadowMap;
document.body.appendChild(renderer.domElement);

// The game loop
function animate() {
  requestAnimationFrame(animate);

  // Update logic here
  scene.traverse((obj) => {
    if (obj instanceof Entity) obj.update();
  });

  // Render
  renderer.render(scene, camera);
}

animate();
```

### Geometry, Material, Mesh

A **Mesh** is a visual object in the scene. It combines a Geometry (shape) and a Material (appearance).

```typescript
// Geometry: defines the shape (vertices, faces)
const geometry = new THREE.BoxGeometry(100, 100, 100);

// Material: defines how it looks (color, texture, shininess, etc.)
const material = new THREE.MeshStandardMaterial({
  color: 0x888888,
  metalness: 0.5,
  roughness: 0.5
});

// Mesh: the combination, placed in the world
const mesh = new THREE.Mesh(geometry, material);
mesh.position.set(100, 0, 200);
mesh.castShadow = true;
mesh.receiveShadow = true;
scene.add(mesh);
```

### The Scene Graph (Like DOM Hierarchy)

Objects can have children, forming a tree. This is familiar to Sean as a designer:

```typescript
// Factory building with child components
const factory = new THREE.Group(); // Container
factory.position.set(1000, 0, 2000);

const base = new THREE.Mesh(baseGeometry, baseMaterial);
const chimney = new THREE.Mesh(chimneyGeometry, chimneyMaterial);
const light = new THREE.PointLight(0xffff00, 1, 500);

factory.add(base);     // base is now a child of factory
factory.add(chimney);  // move factory, chimney moves with it
factory.add(light);    // light follows factory

scene.add(factory);

// Rotate the factory - all children rotate too
factory.rotation.y = Math.PI / 4;
```

## Loading 3D Assets

Games need 3D models. Load them with GLTFLoader:

```typescript
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js";

class AssetManager {
  private loader = new GLTFLoader();
  private cache = new Map<string, THREE.Group>();

  async loadModel(url: string): Promise<THREE.Group> {
    // Return cached model if available
    if (this.cache.has(url)) {
      return this.cache.get(url)!.clone();
    }

    return new Promise((resolve, reject) => {
      this.loader.load(
        url,
        (gltf) => {
          const model = gltf.scene;

          // Setup animations if any
          if (gltf.animations.length > 0) {
            const mixer = new THREE.AnimationMixer(model);
            gltf.animations.forEach((clip) => {
              mixer.clipAction(clip).play();
            });
          }

          // Cache and return
          this.cache.set(url, model);
          resolve(model.clone());
        },
        (progress) => {
          console.log(`Loading: ${(progress.loaded / progress.total) * 100}%`);
        },
        (error) => {
          console.error("Failed to load model:", error);
          reject(error);
        }
      );
    });
  }
}

// Usage
const assetManager = new AssetManager();
const factoryModel = await assetManager.loadModel("/assets/models/factory.glb");
scene.add(factoryModel);
```

### Texture Loading

```typescript
import { TextureLoader } from "three";

class TextureManager {
  private loader = new TextureLoader();
  private cache = new Map<string, THREE.Texture>();

  loadTexture(url: string): THREE.Texture {
    if (this.cache.has(url)) {
      return this.cache.get(url)!;
    }

    const texture = this.loader.load(url);
    texture.magFilter = THREE.LinearFilter;
    texture.minFilter = THREE.LinearMipmapLinearFilter;

    this.cache.set(url, texture);
    return texture;
  }
}

// Usage
const texManager = new TextureManager();
const factoryTexture = texManager.loadTexture("/assets/textures/factory.png");

const material = new THREE.MeshStandardMaterial({
  map: factoryTexture
});
```

## Lighting & Shadows

A dark scene is boring. Light it up:

```typescript
// Ambient light: general illumination (no shadows)
const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
scene.add(ambientLight);

// Directional light: sun-like (can cast shadows)
const sunLight = new THREE.DirectionalLight(0xffffff, 0.8);
sunLight.position.set(1000, 2000, 500);
sunLight.castShadow = true;

// Setup shadow camera (what the light "sees")
sunLight.shadow.camera.left = -5000;
sunLight.shadow.camera.right = 5000;
sunLight.shadow.camera.top = 5000;
sunLight.shadow.camera.bottom = -5000;
sunLight.shadow.camera.near = 0.1;
sunLight.shadow.camera.far = 10000;
sunLight.shadow.mapSize.width = 2048;
sunLight.shadow.mapSize.height = 2048;

scene.add(sunLight);

// Point light: like a light bulb (expensive, use sparingly)
const factoryLight = new THREE.PointLight(0xffff00, 1, 500);
factoryLight.position.set(500, 100, 500);
factoryLight.castShadow = true;
scene.add(factoryLight);
```

## Three.js Ecosystem: Postprocessing, Physics, Animation

### Postprocessing Effects

Make the game visually appealing:

```typescript
import { EffectComposer } from "three/examples/jsm/postprocessing/EffectComposer.js";
import { RenderPass } from "three/examples/jsm/postprocessing/RenderPass.js";
import { UnrealBloomPass } from "three/examples/jsm/postprocessing/UnrealBloomPass.js";

const composer = new EffectComposer(renderer);
const renderPass = new RenderPass(scene, camera);
composer.addPass(renderPass);

// Bloom effect (glowing objects)
const bloomPass = new UnrealBloomPass(
  new THREE.Vector2(window.innerWidth, window.innerHeight),
  1.5,  // strength
  0.4,  // radius
  0.85  // threshold
);
composer.addPass(bloomPass);

// Render with postprocessing
function animate() {
  requestAnimationFrame(animate);
  composer.render(); // Instead of renderer.render()
}
```

### Physics with Cannon-es

For realistic movement:

```typescript
import * as CANNON from "cannon-es";

const world = new CANNON.World();
world.gravity.set(0, -9.82, 0);

// Physics body for a building
const buildingShape = new CANNON.Box(new CANNON.Vec3(50, 50, 50));
const buildingBody = new CANNON.Body({ mass: 0 }); // Static
buildingBody.addShape(buildingShape);
buildingBody.position.set(500, 0, 500);
world.addBody(buildingBody);

// Mesh linked to physics body
const buildingMesh = new THREE.Mesh(geometry, material);
buildingMesh.position.copy(buildingBody.position as any);
scene.add(buildingMesh);

// Update loop
function animate() {
  requestAnimationFrame(animate);

  world.step(1 / 60);

  // Sync mesh position with physics body
  buildingMesh.position.copy(buildingBody.position as any);
  buildingMesh.quaternion.copy(buildingBody.quaternion as any);

  renderer.render(scene, camera);
}
```

### Animation with Mixer

```typescript
class AnimationController {
  private mixer: THREE.AnimationMixer;
  private actions: Map<string, THREE.AnimationAction> = new Map();

  constructor(model: THREE.Group, animations: THREE.AnimationClip[]) {
    this.mixer = new THREE.AnimationMixer(model);

    animations.forEach((clip) => {
      const action = this.mixer.clipAction(clip);
      this.actions.set(clip.name, action);
    });
  }

  play(animationName: string, loop: boolean = true): void {
    const action = this.actions.get(animationName);
    if (action) {
      action.loop = loop ? THREE.LoopRepeat : THREE.LoopOnce;
      action.reset();
      action.play();
    }
  }

  stop(animationName: string): void {
    const action = this.actions.get(animationName);
    if (action) action.stop();
  }

  update(deltaTime: number): void {
    this.mixer.update(deltaTime);
  }
}
```

## Vite + Three.js Project Setup

### package.json

```json
{
  "name": "legion-game",
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "three": "^r128",
    "cannon-es": "^0.20.0",
    "typescript": "^5.0.0"
  },
  "devDependencies": {
    "@types/three": "^r128",
    "vite": "^4.0.0"
  }
}
```

### vite.config.ts

```typescript
import { defineConfig } from "vite";

export default defineConfig({
  server: {
    port: 3000
  },
  build: {
    target: "esnext",
    minify: "terser"
  },
  optimize: {
    esbuildOptions: {
      target: "esnext"
    }
  }
});
```

### tsconfig.json

```json
{
  "compilerOptions": {
    "target": "ESNext",
    "module": "ESNext",
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "jsx": "react-jsx",
    "declaration": true,
    "outDir": "./dist",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true
  },
  "include": ["src"],
  "exclude": ["node_modules"]
}
```

## WebGPU vs. WebGL: The Path Forward

WebGPU is the next-gen graphics API, but WebGL is mature and portable.

```typescript
// Detect capability and fallback gracefully
class RendererManager {
  createRenderer(): THREE.Renderer {
    // Try WebGPU (if available in the browser)
    if (navigator.gpu) {
      console.log("Using WebGPU");
      const canvas = document.createElement("canvas");
      return new THREE.WebGPURenderer({ canvas });
    }

    // Fallback to WebGL
    console.log("Using WebGL");
    return new THREE.WebGLRenderer({
      antialias: true,
      powerPreference: "high-performance"
    });
  }
}
```

## Handling Browser Resize

Games must respond to window resizing:

```typescript
function setupResizeHandler(camera: THREE.Camera, renderer: THREE.Renderer) {
  window.addEventListener("resize", () => {
    const width = window.innerWidth;
    const height = window.innerHeight;

    if (camera instanceof THREE.PerspectiveCamera) {
      camera.aspect = width / height;
      camera.updateProjectionMatrix();
    }

    renderer.setSize(width, height);
  });
}
```

## Performance Profiling

Use Chrome DevTools to profile:

```typescript
// Stats.js for real-time FPS monitoring
import Stats from "three/examples/jsm/libs/stats.module.js";

const stats = new Stats();
document.body.appendChild(stats.dom);

function animate() {
  stats.begin();

  // Game logic here

  stats.end();
  requestAnimationFrame(animate);
}
```

### Key Metrics

- **FPS**: Target 60 on desktop, 30 on mobile
- **Frame time**: < 16.7ms for 60 FPS
- **GPU Memory**: < 512MB for web (browsers have limits)
- **Texture memory**: Compress textures, use atlases
- **Draw calls**: Batch with InstancedMesh, minimize materials

### Chrome DevTools Profiling

1. Open DevTools → Performance tab
2. Click Record, play for 10 seconds
3. Click Stop
4. Analyze the flame graph for bottlenecks

Look for:
- Long `render()` calls (GPU-bound)
- Long JavaScript execution (CPU-bound)
- Memory spikes (memory leak)

## Cleanup & Disposal

Prevent memory leaks by disposing of resources:

```typescript
class GameScene {
  private geometries: THREE.Geometry[] = [];
  private materials: THREE.Material[] = [];
  private textures: THREE.Texture[] = [];

  cleanup(): void {
    // Dispose geometries
    this.geometries.forEach((g) => g.dispose());

    // Dispose materials
    this.materials.forEach((m) => m.dispose());

    // Dispose textures
    this.textures.forEach((t) => t.dispose());

    // Remove from scene
    this.scene.children.forEach((child) => {
      if (child instanceof THREE.Mesh) {
        this.scene.remove(child);
      }
    });
  }
}
```

---

**Three.js is powerful but requires understanding rendering, memory, and performance. Master the core (Scene, Camera, Renderer), then layer in advanced features (postprocessing, physics, shaders) as needed.**
