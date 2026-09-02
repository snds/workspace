# Three.js Post-Processing, Particle Systems, and Visual Effects

Comprehensive guide to advanced rendering techniques in Three.js for creating professional visual effects, post-processing pipelines, and particle systems.

---

## 1. EffectComposer Pipeline

### Overview

EffectComposer is the core post-processing infrastructure in Three.js that manages a pipeline of rendering passes. It uses a dual render-target system (often called rtA and rtB) that alternates between them as data flows through each pass.

### How the Pipeline Works

1. **Initial Render**: The scene is rendered to rtA via RenderPass
2. **Pass Chain**: Each subsequent pass reads from its input render target and writes to an output target
3. **Alternation**: Results alternate between rtA and rtB as they flow through the pipeline
4. **Final Output**: The last pass writes to the canvas when `renderToScreen` is set to true

### Basic Setup Pattern

```javascript
import { EffectComposer } from 'three/examples/jsm/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/examples/jsm/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/examples/jsm/postprocessing/UnrealBloomPass.js';

// Create composer
const composer = new EffectComposer(renderer);

// Add render pass (always first)
const renderPass = new RenderPass(scene, camera);
composer.addPass(renderPass);

// Add effect passes
const bloomPass = new UnrealBloomPass(
  new THREE.Vector2(window.innerWidth, window.innerHeight),
  1.5, // strength
  0.4, // radius
  0.85 // threshold
);
composer.addPass(bloomPass);

// Final pass must render to screen
bloomPass.renderToScreen = true;

// In animation loop
composer.render();
```

### Pass Ordering Guidelines

1. **RenderPass first**: Clears buffers and renders the scene
2. **Depth/Normal passes**: If needed (SSAOPass requires depth and normals)
3. **Effect passes**: Color grading, bloom, depth of field, etc.
4. **Anti-aliasing**: Place SMAA/FXAA near the end but before tone mapping
5. **Tone mapping**: Apply color grading and tone mapping before final output
6. **Final pass**: Set `renderToScreen = true` only on the last pass

### Performance Implications

- **Render target cost**: Each pass allocates VRAM for input/output textures. Large resolutions compound this.
- **GPU bandwidth**: Switching between targets has overhead; minimize passes when possible
- **Shader complexity**: Complex fragment shaders multiply processing per pixel
- **Read-modify-write pattern**: Each pass reads the previous target and writes a new one, creating latency

### Built-in Three.js vs pmndrs/postprocessing

**Three.js Built-in EffectComposer**:
- Traditional pass-by-pass architecture
- Each pass is independent, making code clear but inefficient
- Many passes redundantly calculate depth, normals, or render operations
- Better for simple pipelines (1-3 passes)

**pmndrs/postprocessing Library**:
- Uses EffectPass that automatically merges effect shaders
- Minimizes render operations by combining multiple effects
- Uses single fullscreen triangle instead of quad (modern GPU optimization)
- Can combine 10+ effects without performance penalty of traditional chaining
- Recommended for complex visual pipelines

**Why pmndrs is More Performant**:
1. **Effect Merging**: Shader code combining multiple effects into single render pass
2. **Shared Resources**: Reuses depth/normal buffers across multiple effects
3. **Fewer Render Targets**: Reduces VRAM allocation and bandwidth
4. **GPU-Optimized Rendering**: Single-triangle fullscreen rendering eliminates diagonal fragment overhead

---

## 2. Key Post-Processing Passes

### UnrealBloomPass / BloomEffect

**Purpose**: Creates a glow effect around bright areas by blurring and compositing them additively.

**How It Works**:
1. Creates a mip-map chain of bloom textures at different resolutions
2. Blurs them with different radii (larger blurs on higher mips)
3. Composites them back onto the scene additively
4. Provides both quality and performance through multi-scale approach

**Configuration for Good Results**:

```javascript
const bloomPass = new UnrealBloomPass(
  resolution,
  strength,    // 0.5-2.0 (1.5 default)
  radius,      // 0.1-1.0 (0.4 default)
  threshold    // 0.5-1.0 (0.85 default)
);

// Selective bloom: Adjust threshold to include only bright materials
bloomPass.threshold = 0.9; // Only brightest pixels bloom
bloomPass.strength = 1.5;  // How intense the glow
bloomPass.radius = 0.4;    // Spread of the glow
```

**Avoiding Wash-Out**:
- Keep threshold HIGH (0.8-0.9) to prevent everything from blooming
- Limit strength to 1.0-1.5 range
- Use selective bloom by setting object.layers or renderToScreen = false during bloom rendering
- Combine with tone mapping for better results
- Reduce strength if using multiple bright materials

**pmndrs Version** (BloomEffect):
```javascript
import { BloomEffect } from 'postprocessing';

const bloom = new BloomEffect({
  intensity: 1.0,
  blurPass: null, // Optional separate blur pass
  kernelSize: KernelSize.LARGE,
  luminanceThreshold: 0.9,
  luminanceSmoothing: 0.025,
  mipmapBlur: true,
  opacity: 1.0
});
```

### SSAOPass / SSAOEffect

**Purpose**: Screen-space ambient occlusion adds depth and realism by darkening crevices.

**Setup**:
```javascript
import { SSAOPass } from 'three/examples/jsm/postprocessing/SSAOPass.js';

const ssaoPass = new SSAOPass(scene, camera, window.innerWidth, window.innerHeight);
ssaoPass.kernelRadius = 16;
ssaoPass.minDistance = 0.005;
ssaoPass.maxDistance = 0.1;
ssaoPass.aoRadius = 2.0; // World-space radius
ssaoPass.intensity = 1.0;
composer.addPass(ssaoPass);
```

**Key Parameters**:
- **aoRadius**: Size of ambient occlusion in world units (most important)
- **intensity**: Darkness strength (0.5-2.0)
- **kernelRadius**: Quality/blur radius (higher = better quality, slower)
- **minDistance/maxDistance**: Depth test range

**High-Quality Approach**:
Use TWO SSAO passes with different settings for both rough AO and fine details:

```javascript
// First pass: Broad AO
const ssao1 = new SSAOPass(scene, camera, w, h);
ssao1.aoRadius = 5.0;
ssao1.intensity = 0.4;
composer.addPass(ssao1);

// Second pass: Fine details
const ssao2 = new SSAOPass(scene, camera, w, h);
ssao2.aoRadius = 1.0;
ssao2.intensity = 0.3;
composer.addPass(ssao2);
```

**pmndrs Version** (SSAOEffect):
```javascript
import { SSAOEffect } from 'postprocessing';

const ssao = new SSAOEffect(camera, depthTexture, {
  radius: 20,
  intensity: 1.5,
  bias: 0.5,
  luminanceInfluence: 0.7,
  scale: 1.0,
  fade: 1.0,
  samples: 16
});
```

### SMAAPass / SMAAEffect

**Purpose**: Subpixel Morphological Antialiasing for smooth edges.

**Setup**:
```javascript
import { SMAAPass } from 'three/examples/jsm/postprocessing/SMAAPass.js';

const smaaPass = new SMAAPass(window.innerWidth, window.innerHeight);
composer.addPass(smaaPass);
smaaPass.renderToScreen = true;
```

**Important**: Must run in linear color space; execute before OutputPass.

**Comparison with FXAA**:
- SMAA: Better quality, uses lookup tables for edge detection, slightly slower
- FXAA: Faster, but less accurate edge detection
- MSAA: Hardware sampling, stable but artifacts with depth-based effects

**pmndrs Version**:
```javascript
import { SMAAEffect } from 'postprocessing';

const smaa = new SMAAEffect({
  preset: SMAAPreset.MEDIUM // LOW, MEDIUM, HIGH, ULTRA
});
```

### BokehPass / DepthOfFieldEffect

**Purpose**: Creates depth of field with bokeh blur based on focus distance.

**Setup**:
```javascript
import { BokehPass } from 'three/examples/jsm/postprocessing/BokehPass.js';

const bokehPass = new BokehPass(scene, camera, {
  focus: 500,      // Distance in world units
  aperture: 5,     // Blur amount (0.1-100)
  maxblur: 0.01    // Max blur radius
});
composer.addPass(bokehPass);

// Animate focus
bokehPass.uniforms.focus.value = newDistance;
```

**Parameters**:
- **focus**: Distance from camera where objects are sharp
- **aperture**: Controls blur strength (higher = more blur)
- **maxblur**: Maximum blur radius to prevent excessive blur

**Performance Note**: BokehPass renders depth, so ensure depth buffer is enabled.

**pmndrs Version** (DepthOfFieldEffect):
```javascript
import { DepthOfFieldEffect } from 'postprocessing';

const dof = new DepthOfFieldEffect(camera, {
  focusDistance: 0.0,
  focusRange: 1.0,
  bokehScale: 1.0,
  height: 480
});
```

### FilmPass

**Purpose**: Adds film grain and scanlines for vintage or CRT effects.

**Setup**:
```javascript
import { FilmPass } from 'three/examples/jsm/postprocessing/FilmPass.js';

const filmPass = new FilmPass(
  0.35,    // Noise intensity
  0.025,   // Scanline intensity
  648,     // Scanline count
  false    // Grayscale
);
composer.addPass(filmPass);
```

**Runtime Configuration**:
```javascript
filmPass.uniforms.nIntensity.value = 0.5;  // Noise
filmPass.uniforms.sIntensity.value = 0.1;  // Scanlines
filmPass.uniforms.sCount.value = 648;      // Scanline resolution
filmPass.uniforms.grayscale.value = false; // Color or B&W
```

### ColorCorrectionShader / ToneMappingEffect

**Purpose**: Adjusts color, saturation, contrast for mood and visual style.

**Tone Mapping Types**:
1. **NoToneMapping**: Linear output (default)
2. **LinearToneMapping**: Simple linear mapping
3. **ReinhardToneMapping**: Photographic curve, natural but can look washed
4. **CineonToneMapping**: Film-like curve
5. **ACESFilmicToneMapping**: Industry standard (ACES color space), cinematic

**Setup**:
```javascript
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.0; // 0-10 range

// Or use custom color grading pass
import { ShaderPass } from 'three/examples/jsm/postprocessing/ShaderPass.js';

const colorPass = new ShaderPass(ColorCorrectionShader);
colorPass.uniforms['powRGB'].value = new THREE.Vector3(2.2, 2.2, 2.2); // Gamma
colorPass.uniforms['mulRGB'].value = new THREE.Vector3(1.0, 1.0, 1.0); // Brightness
composer.addPass(colorPass);
```

**Choosing Tone Mapping**:
- **LinearToneMapping**: Game-like, maximizes dynamic range
- **ReinhardToneMapping**: Natural, photographic
- **CineonToneMapping**: Filmic, cinematic
- **ACESFilmicToneMapping**: Industry standard, best for HDR content

### GlitchPass

**Purpose**: Creates digital glitch effects for sci-fi HUD, malfunction themes.

**Setup**:
```javascript
import { GlitchPass } from 'three/examples/jsm/postprocessing/GlitchPass.js';

const glitchPass = new GlitchPass(512); // Texture size
glitchPass.goWild = false; // Continuous glitch or trigger-based
composer.addPass(glitchPass);

// Trigger glitch on demand
glitchPass.goWild = true;
setTimeout(() => { glitchPass.goWild = false; }, 200);
```

**Applications**:
- Cyberpunk HUD effects
- Digital malfunction sequences
- Data corruption visualization
- Alarm state feedback
- Damaged device displays

### OutlinePass

**Purpose**: Highlights selected objects with colored outlines.

**Setup**:
```javascript
import { OutlinePass } from 'three/examples/jsm/postprocessing/OutlinePass.js';

const outlinePass = new OutlinePass(
  new THREE.Vector2(window.innerWidth, window.innerHeight),
  scene,
  camera
);

outlinePass.edgeStrength = 3.0;
outlinePass.edgeGlow = 0.0;
outlinePass.edgeThickness = 1.0;
outlinePass.visibleEdgeColor.set('#ffffff');
outlinePass.hiddenEdgeColor.set('#190a05');
outlinePass.selectedObjects = [object1, object2];

composer.addPass(outlinePass);
```

**Configuration**:
```javascript
outlinePass.edgeStrength = 3;        // Outline boldness
outlinePass.edgeGlow = 1;            // Glow intensity
outlinePass.edgeThickness = 2;       // Pixel width
outlinePass.pulsePeriod = 0;         // Animation speed
outlinePass.usePatternTexture = false; // Pattern fill
```

**Dynamic Selection**:
```javascript
// Update selected objects at runtime
function selectObject(obj) {
  outlinePass.selectedObjects = [obj];
}

// Multi-select
function multiSelect(objects) {
  outlinePass.selectedObjects = [...objects];
}
```

### GTAOPass

**Purpose**: Ground Truth Ambient Occlusion provides high-quality depth-based shading.

**Setup**:
```javascript
// GTAOPass requires WebGL2
const gtaoPass = new GTAOPass(scene, camera, window.innerWidth, window.innerHeight);
gtaoPass.radius = 2;
gtaoPass.intensity = 1;
gtaoPass.bias = 0.5;
gtaoPass.samples = 16;
composer.addPass(gtaoPass);
```

**Configuration**:
```javascript
gtaoPass.radius = 2.0;          // World-space sample radius
gtaoPass.intensity = 1.0;       // AO darkness
gtaoPass.bias = 0.5;            // Reduces self-shadowing artifacts
gtaoPass.samples = 16;          // Quality/performance tradeoff
gtaoPass.denoise = true;        // Apply spatial blur
```

**Quality vs Performance**:
- Samples 16: Fast, visible banding
- Samples 32: Balanced
- Samples 64+: High quality, slower

### Custom Pass Creation

**Using ShaderPass**:
```javascript
const customShader = {
  uniforms: {
    tDiffuse: { value: null },
    intensity: { value: 1.0 }
  },
  vertexShader: `
    varying vec2 vUv;
    void main() {
      vUv = uv;
      gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    }
  `,
  fragmentShader: `
    uniform sampler2D tDiffuse;
    uniform float intensity;
    varying vec2 vUv;

    void main() {
      vec4 color = texture2D(tDiffuse, vUv);
      gl_FragColor = vec4(vec3(1.0) - color.rgb, 1.0) * intensity;
    }
  `
};

const customPass = new ShaderPass(customShader);
customPass.uniforms.intensity.value = 0.5;
composer.addPass(customPass);
```

**Extending Pass Class**:
```javascript
import { Pass } from 'three/examples/jsm/postprocessing/Pass.js';

class CustomPass extends Pass {
  constructor(scene, camera) {
    super();
    this.scene = scene;
    this.camera = camera;
    this.material = new THREE.ShaderMaterial({
      uniforms: { tDiffuse: { value: null } },
      vertexShader: '...',
      fragmentShader: '...'
    });
    this.quad = new THREE.Mesh(new THREE.PlaneGeometry(2, 2), this.material);
    this.scene2d = new THREE.Scene();
    this.scene2d.add(this.quad);
  }

  render(renderer, writeBuffer, readBuffer) {
    this.material.uniforms.tDiffuse.value = readBuffer.texture;
    renderer.setRenderTarget(this.renderToScreen ? null : writeBuffer);
    renderer.render(this.scene2d, this.camera);
  }

  setSize(width, height) {
    // Handle resizing
  }

  dispose() {
    this.material.dispose();
    this.quad.geometry.dispose();
  }
}
```

---

## 3. Tone Mapping

### What is Tone Mapping?

Tone mapping is the process of converting HDR (High Dynamic Range) color values to LDR (Low Dynamic Range) displayable values while preserving visual detail and color accuracy. It simulates how cameras and human eyes adapt to different lighting conditions.

### Why It Matters for HDR

Without tone mapping:
- Bright areas are clipped to white
- Details in highlights are lost
- Physically correct lighting looks flat on SDR displays
- No compensation for display limitations

With tone mapping:
- Preserves detail across full dynamic range
- Creates more realistic/cinematic results
- Adapts bright lighting to display capabilities
- Improves overall image quality

### Available Algorithms

**1. NoToneMapping (THREE.NoToneMapping)**
```javascript
renderer.toneMapping = THREE.NoToneMapping;
// Linear output, no adjustment
// Use for stylized/non-photorealistic renders
```

**2. LinearToneMapping (THREE.LinearToneMapping)**
```javascript
renderer.toneMapping = THREE.LinearToneMapping;
// Simple linear scaling with exposure
// Fast, good for game-like aesthetics
renderer.toneMappingExposure = 1.5;
```

**3. ReinhardToneMapping (THREE.ReinhardToneMapping)**
```javascript
renderer.toneMapping = THREE.ReinhardToneMapping;
// Photographic curve: gives impression of washed-out colors
// Actually achieves high realism despite appearance
// Natural, camera-like response
renderer.toneMappingExposure = 2.0;
```

**4. CineonToneMapping (THREE.CineonToneMapping)**
```javascript
renderer.toneMapping = THREE.CineonToneMapping;
// Film-inspired curve
// More contrast than Reinhard
// Cinematic appearance
renderer.toneMappingExposure = 1.0;
```

**5. ACESFilmicToneMapping (THREE.ACESFilmicToneMapping)**
```javascript
renderer.toneMapping = THREE.ACESFilmicToneMapping;
// Academy Color Encoding System (ACES)
// Industry standard for film/VFX
// Best for HDR environments and professional work
renderer.toneMappingExposure = 1.0;

// Note: Can cause low-contrast textures if not configured properly
// Use with proper environment maps for best results
```

### Choosing the Right Tone Mapping

| Type | Best For | Characteristics |
|------|----------|-----------------|
| Linear | Games, stylized | Fast, maximizes range, less natural |
| Reinhard | Photography, realism | Natural, photographic, washed appearance |
| Cineon | Cinematics, video | Filmic, high contrast, dramatic |
| ACES Filmic | Professional, HDR | Industry standard, color-accurate, cinematic |

### Implementation Pattern

```javascript
// Setup
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.0;

// Runtime adjustment
function setExposure(value) {
  renderer.toneMappingExposure = Math.pow(2, value); // -10 to +10
}

// A/B comparison UI
const tonemappings = [
  THREE.NoToneMapping,
  THREE.LinearToneMapping,
  THREE.ReinhardToneMapping,
  THREE.CineonToneMapping,
  THREE.ACESFilmicToneMapping
];

function switchToneMapping(index) {
  renderer.toneMapping = tonemappings[index];
}
```

---

## 4. Color Grading

### LUT-Based Color Grading

Color grading via 3D Lookup Tables (LUTs) applies professional color transforms to create mood and visual style.

### How LUTs Work

A 3D LUT samples color gradations across RGB space (typically 32x32x32 or 64x64x64 resolution):
1. Input color (R, G, B) samples into the 3D texture
2. Output color retrieved from LUT texture
3. Result blended back to scene

### Creating/Using LUTs

**Using Pre-Made LUTs**:
```javascript
const textureLoader = new THREE.TextureLoader();
const lutTexture = await textureLoader.loadAsync('lut.png');

// LUT applied via custom shader or postprocessing library
const lutPass = new LUTPass(lutTexture);
composer.addPass(lutPass);
```

**Implementing LUT Shader**:
```javascript
const lutShader = {
  uniforms: {
    tDiffuse: { value: null },
    tLUT: { value: lutTexture },
    intensity: { value: 1.0 }
  },
  fragmentShader: `
    uniform sampler2D tDiffuse;
    uniform sampler2D tLUT;
    uniform float intensity;
    varying vec2 vUv;

    // Sample 3D LUT from 2D texture
    vec3 sampleLUT(vec3 color) {
      float texelSize = 1.0 / 32.0; // For 32x32x32 LUT
      float blueIndex = color.b * 31.0;

      float x = color.r + (mod(blueIndex, 8.0) * 32.0);
      float y = color.g + (floor(blueIndex / 8.0) * 32.0);

      return texture2D(tLUT, vec2(x, y) * texelSize).rgb;
    }

    void main() {
      vec3 color = texture2D(tDiffuse, vUv).rgb;
      vec3 graded = sampleLUT(color);
      gl_FragColor = vec4(mix(color, graded, intensity), 1.0);
    }
  `
};
```

### Mood Creation Patterns

**Cold Industrial**:
```javascript
// Desaturate greens/reds, boost blues/cyans
// Reduce overall brightness
// Increase contrast
const industrialLUT = {
  colorOffset: new THREE.Vector3(-0.1, 0.0, 0.2),
  saturation: 0.7,
  brightness: 0.9,
  contrast: 1.2
};
```

**Warm Habitat**:
```javascript
// Boost reds/oranges/yellows
// Increase saturation
// Warm highlights
const habitatLUT = {
  colorOffset: new THREE.Vector3(0.15, 0.1, -0.1),
  saturation: 1.1,
  brightness: 1.05,
  contrast: 0.95
};
```

**Emergency Alert**:
```javascript
// Desaturate to emphasize danger
// Boost reds strongly
// High contrast
// Slight vignette
const emergencyLUT = {
  colorOffset: new THREE.Vector3(0.3, -0.2, -0.2),
  saturation: 0.6,
  brightness: 1.1,
  contrast: 1.3
};
```

**Alien Discovery**:
```javascript
// Shift to unnatural colors
// Boost magentas/cyans
// High saturation
// Ethereal appearance
const alienLUT = {
  colorOffset: new THREE.Vector3(-0.1, 0.2, 0.3),
  saturation: 1.3,
  brightness: 1.0,
  contrast: 1.1
};
```

### Implementation

```javascript
import { ShaderPass } from 'three/examples/jsm/postprocessing/ShaderPass.js';

class ColorGradingPass extends ShaderPass {
  constructor(lutTexture) {
    const shader = {
      uniforms: {
        tDiffuse: { value: null },
        tLUT: { value: lutTexture },
        saturation: { value: 1.0 },
        brightness: { value: 1.0 },
        contrast: { value: 1.0 }
      },
      vertexShader: `
        varying vec2 vUv;
        void main() {
          vUv = uv;
          gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
        }
      `,
      fragmentShader: `
        uniform sampler2D tDiffuse;
        uniform sampler2D tLUT;
        uniform float saturation;
        uniform float brightness;
        uniform float contrast;
        varying vec2 vUv;

        vec3 adjustSaturation(vec3 color, float sat) {
          vec3 gray = vec3(dot(color, vec3(0.299, 0.587, 0.114)));
          return mix(gray, color, sat);
        }

        void main() {
          vec3 color = texture2D(tDiffuse, vUv).rgb;

          // Apply LUT
          float lut_size = 32.0;
          float cell = color.b * (lut_size - 1.0);
          float cell_offset = fract(cell);
          float cell_index = floor(cell);

          vec2 uv = vec2(color.r, color.g);
          uv.x = (uv.x + cell_index) / lut_size;

          color = mix(
            texture2D(tLUT, uv).rgb,
            texture2D(tLUT, uv + vec2(1.0/lut_size, 0.0)).rgb,
            cell_offset
          );

          // Apply adjustments
          color = adjustSaturation(color, saturation);
          color = color * brightness;
          color = mix(vec3(0.5), color, contrast);

          gl_FragColor = vec4(color, 1.0);
        }
      `
    };

    super(shader);
  }

  setMood(mood) {
    switch(mood) {
      case 'industrial':
        this.uniforms.saturation.value = 0.7;
        this.uniforms.brightness.value = 0.9;
        this.uniforms.contrast.value = 1.2;
        break;
      case 'habitat':
        this.uniforms.saturation.value = 1.1;
        this.uniforms.brightness.value = 1.05;
        this.uniforms.contrast.value = 0.95;
        break;
      case 'emergency':
        this.uniforms.saturation.value = 0.6;
        this.uniforms.brightness.value = 1.1;
        this.uniforms.contrast.value = 1.3;
        break;
      case 'alien':
        this.uniforms.saturation.value = 1.3;
        this.uniforms.brightness.value = 1.0;
        this.uniforms.contrast.value = 1.1;
        break;
    }
  }
}
```

---

## 5. Particle Systems and VFX

### THREE.Points - Basic Particles

Simplest approach: geometry + PointsMaterial + Points object.

```javascript
// Create particles
const count = 1000;
const geometry = new THREE.BufferGeometry();

// Positions
const positions = new Float32Array(count * 3);
for (let i = 0; i < count * 3; i += 3) {
  positions[i] = (Math.random() - 0.5) * 100;
  positions[i + 1] = (Math.random() - 0.5) * 100;
  positions[i + 2] = (Math.random() - 0.5) * 100;
}
geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));

// Material
const material = new THREE.PointsMaterial({
  size: 1.0,
  color: 0xffffff,
  sizeAttenuation: true,
  map: particleTexture,
  transparent: true,
  fog: true
});

const points = new THREE.Points(geometry, material);
scene.add(points);

// Animation in shader
const positionAttribute = geometry.getAttribute('position');
function animateParticles() {
  const positions = positionAttribute.array;
  for (let i = 0; i < count * 3; i += 3) {
    positions[i] += (Math.random() - 0.5) * 0.2; // Brownian motion
    positions[i + 1] -= 0.1; // Fall
    positions[i + 2] += (Math.random() - 0.5) * 0.2;
  }
  positionAttribute.needsUpdate = true;
}
```

**Advantages**: Simple, one draw call, efficient for large counts

**Disadvantages**: Limited visual complexity, all particles identical size/shape in world space

### InstancedMesh - Complex Particles

Use for particles with individual transforms (position, rotation, scale).

```javascript
const count = 10000;
const geometry = new THREE.BoxGeometry(1, 1, 1);
const material = new THREE.MeshPhongMaterial({ color: 0xffffff });

const instancedMesh = new THREE.InstancedMesh(geometry, material, count);

// Dummy object for transform calculations
const dummy = new THREE.Object3D();

// Set instance transforms
for (let i = 0; i < count; i++) {
  dummy.position.set(
    (Math.random() - 0.5) * 100,
    (Math.random() - 0.5) * 100,
    (Math.random() - 0.5) * 100
  );
  dummy.rotation.set(
    Math.random() * Math.PI * 2,
    Math.random() * Math.PI * 2,
    Math.random() * Math.PI * 2
  );
  dummy.scale.set(0.5, 0.5, 0.5);
  dummy.updateMatrix();

  instancedMesh.setMatrixAt(i, dummy.matrix);
}
instancedMesh.instanceMatrix.needsUpdate = true;

scene.add(instancedMesh);

// Animate
function updateInstances() {
  for (let i = 0; i < count; i++) {
    instancedMesh.getMatrixAt(i, dummy.matrix);
    dummy.position.y -= 0.1;
    dummy.updateMatrix();
    instancedMesh.setMatrixAt(i, dummy.matrix);
  }
  instancedMesh.instanceMatrix.needsUpdate = true;
}
```

**Advantages**: One draw call for thousands of unique objects, supports individual transforms/materials

**Disadvantages**: Slower per-frame updates if frequently modified, memory overhead

### GPU-Driven Particles with Compute Shaders (WebGPU)

Most performant for large particle counts (100k+).

```glsl
// Compute shader for particle physics
struct Particle {
  position: vec3f,
  velocity: vec3f,
  life: f32,
};

@group(0) @binding(0) var<storage, read_write> particles: array<Particle>;

@compute @workgroup_size(64)
fn main(@builtin(global_invocation_id) global_id: vec3u) {
  let idx = global_id.x;
  if (idx >= arrayLength(&particles)) { return; }

  var p = particles[idx];

  // Physics
  p.velocity.y -= 0.01; // Gravity
  p.position += p.velocity;
  p.life -= 0.016; // Time

  // Reset if dead
  if (p.life < 0.0) {
    p.position = vec3f(0.0);
    p.velocity = vec3f(0.0);
    p.life = 1.0;
  }

  particles[idx] = p;
}
```

**Advantages**: Thousands of particles with full physics, minimal CPU overhead, sub-millisecond updates

**Disadvantages**: Requires WebGPU, complex shader programming, less browser support currently

### Third-Party Libraries

**three-nebula**: Professional particle engine with visual editor
```javascript
import { Engine } from 'three-nebula';

const engine = new Engine();
engine.addRenderer(renderer);

// Load from JSON or visual editor
const particleSystem = engine.createFromJSON(jsonConfig);
scene.add(particleSystem);

engine.update();
```

**three.quarks**: High-performance VFX with CPU + GPU optimization
```javascript
import { System, BatchedRenderer } from 'three.quarks';

const system = new System({
  duration: 5,
  looping: true,
  startLife: { constant: 3 },
  emissionRate: { constant: 100 }
});

const renderer = new BatchedRenderer();
scene.add(renderer);
renderer.addSystem(system);
```

### Common VFX Effects

#### Thruster Exhaust

```javascript
class ThrusterExhaust {
  constructor(position) {
    const count = 500;
    const geometry = new THREE.BufferGeometry();

    // Emit particles backward
    const positions = new Float32Array(count * 3);
    const velocities = new Float32Array(count * 3);

    for (let i = 0; i < count * 3; i += 3) {
      positions[i] = (Math.random() - 0.5) * 2;
      positions[i + 1] = (Math.random() - 0.5) * 2;
      positions[i + 2] = 0;

      velocities[i] = (Math.random() - 0.5) * 0.5;
      velocities[i + 1] = (Math.random() - 0.5) * 0.5;
      velocities[i + 2] = -Math.random() * 3; // Backward
    }

    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geometry.setAttribute('velocity', new THREE.BufferAttribute(velocities, 3));

    this.material = new THREE.PointsMaterial({
      size: 0.5,
      color: 0xff8800,
      transparent: true,
      map: gradientTexture
    });

    this.points = new THREE.Points(geometry, this.material);
    this.points.position.copy(position);
  }

  update() {
    const posAttr = this.points.geometry.getAttribute('position');
    const velAttr = this.points.geometry.getAttribute('velocity');
    const positions = posAttr.array;
    const velocities = velAttr.array;

    for (let i = 0; i < positions.length; i += 3) {
      positions[i] += velocities[i];
      positions[i + 1] += velocities[i + 1];
      positions[i + 2] += velocities[i + 2];

      // Gravity
      velocities[i + 1] -= 0.05;

      // Fade and shrink
      positions[i + 1] *= 0.98;
    }
    posAttr.needsUpdate = true;
  }
}
```

#### Sparks Effect

```javascript
class SparksEffect {
  constructor(position, count = 200) {
    const geometry = new THREE.BufferGeometry();
    const positions = new Float32Array(count * 3);
    const velocities = new Float32Array(count * 3);
    const lifetimes = new Float32Array(count);

    for (let i = 0; i < count; i++) {
      const angle = Math.random() * Math.PI * 2;
      const speed = 1 + Math.random() * 2;

      positions[i * 3] = position.x;
      positions[i * 3 + 1] = position.y;
      positions[i * 3 + 2] = position.z;

      velocities[i * 3] = Math.cos(angle) * speed;
      velocities[i * 3 + 1] = Math.sin(angle) * speed;
      velocities[i * 3 + 2] = (Math.random() - 0.5) * speed;

      lifetimes[i] = Math.random();
    }

    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geometry.setAttribute('velocity', new THREE.BufferAttribute(velocities, 3));
    geometry.setAttribute('lifetime', new THREE.BufferAttribute(lifetimes, 1));

    this.material = new THREE.PointsMaterial({
      size: 0.3,
      color: 0xffaa00,
      transparent: true,
      emissive: 0xffaa00,
      emissiveIntensity: 0.5
    });

    this.points = new THREE.Points(geometry, this.material);
    this.age = 0;
  }

  update(dt) {
    this.age += dt;
    const posAttr = this.points.geometry.getAttribute('position');
    const positions = posAttr.array;
    const velocities = this.points.geometry.getAttribute('velocity').array;

    for (let i = 0; i < positions.length; i += 3) {
      positions[i] += velocities[i];
      positions[i + 1] += velocities[i + 1];
      positions[i + 2] += velocities[i + 2];

      velocities[i] *= 0.98;
      velocities[i + 1] -= 0.1; // Gravity
      velocities[i + 2] *= 0.98;
    }
    posAttr.needsUpdate = true;

    return this.age > 2.0; // Dead when older than 2 seconds
  }
}
```

#### Explosion Effect

```javascript
class ExplosionEffect {
  constructor(position, intensity = 1.0) {
    const count = Math.floor(500 * intensity);
    const geometry = new THREE.BufferGeometry();

    const positions = new Float32Array(count * 3);
    const velocities = new Float32Array(count * 3);
    const sizes = new Float32Array(count);

    for (let i = 0; i < count; i++) {
      // Spherical distribution
      const phi = Math.random() * Math.PI * 2;
      const theta = Math.acos(Math.random() * 2 - 1);
      const speed = 2 + Math.random() * 4;

      positions[i * 3] = position.x;
      positions[i * 3 + 1] = position.y;
      positions[i * 3 + 2] = position.z;

      velocities[i * 3] = Math.sin(theta) * Math.cos(phi) * speed;
      velocities[i * 3 + 1] = Math.sin(theta) * Math.sin(phi) * speed;
      velocities[i * 3 + 2] = Math.cos(theta) * speed;

      sizes[i] = 1 + Math.random() * 2;
    }

    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geometry.setAttribute('velocity', new THREE.BufferAttribute(velocities, 3));
    geometry.setAttribute('size', new THREE.BufferAttribute(sizes, 1));

    this.material = new THREE.PointsMaterial({
      size: 2,
      color: 0xffff00,
      transparent: true,
      emissive: 0xff6600,
      map: explosionTexture
    });

    this.points = new THREE.Points(geometry, this.material);
    this.age = 0;
  }

  update(dt) {
    this.age += dt;
    const alpha = Math.max(0, 1 - this.age / 2);

    this.material.opacity = alpha;

    const posAttr = this.points.geometry.getAttribute('position');
    const positions = posAttr.array;
    const velocities = this.points.geometry.getAttribute('velocity').array;

    for (let i = 0; i < positions.length; i += 3) {
      positions[i] += velocities[i];
      positions[i + 1] += velocities[i + 1];
      positions[i + 2] += velocities[i + 2];

      velocities[i] *= 0.96;
      velocities[i + 1] *= 0.96;
      velocities[i + 2] *= 0.96;
    }
    posAttr.needsUpdate = true;

    return this.age > 2.0;
  }
}
```

#### Energy Beam / Laser

```javascript
class EnergyBeam {
  constructor(startPos, endPos, color = 0x00ffff) {
    // Cylinder along beam direction
    const direction = new THREE.Vector3().subVectors(endPos, startPos);
    const length = direction.length();

    const geometry = new THREE.CylinderGeometry(0.2, 0.2, length, 8);

    const material = new THREE.MeshBasicMaterial({
      color: color,
      transparent: true,
      emissive: color,
      emissiveIntensity: 1.0
    });

    this.mesh = new THREE.Mesh(geometry, material);
    this.mesh.position.copy(startPos);
    this.mesh.position.addScaledVector(direction.normalize(), length * 0.5);
    this.mesh.lookAt(endPos);

    // Glow effect with point light
    this.light = new THREE.PointLight(color, 1, 50);
    this.light.position.lerpVectors(startPos, endPos, 0.5);

    this.pulse = 0;
  }

  update(dt) {
    this.pulse = (this.pulse + dt * 3) % 1.0;
    this.mesh.material.emissiveIntensity = 0.8 + Math.sin(this.pulse * Math.PI) * 0.2;
    this.light.intensity = 0.8 + Math.cos(this.pulse * Math.PI * 2) * 0.3;
  }
}
```

#### Smoke / Fog Cloud

```javascript
class SmokePuff {
  constructor(position) {
    const count = 300;
    const geometry = new THREE.BufferGeometry();

    const positions = new Float32Array(count * 3);
    const velocities = new Float32Array(count * 3);
    const ages = new Float32Array(count);

    for (let i = 0; i < count; i++) {
      positions[i * 3] = position.x + (Math.random() - 0.5) * 2;
      positions[i * 3 + 1] = position.y + (Math.random() - 0.5) * 2;
      positions[i * 3 + 2] = position.z + (Math.random() - 0.5) * 2;

      const angle = Math.random() * Math.PI * 2;
      const speed = Math.random() * 0.2;
      velocities[i * 3] = Math.cos(angle) * speed;
      velocities[i * 3 + 1] = 0.5 + Math.random() * 0.5; // Rise
      velocities[i * 3 + 2] = Math.sin(angle) * speed;

      ages[i] = Math.random();
    }

    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geometry.setAttribute('velocity', new THREE.BufferAttribute(velocities, 3));
    geometry.setAttribute('age', new THREE.BufferAttribute(ages, 1));

    this.material = new THREE.PointsMaterial({
      size: 2,
      color: 0xcccccc,
      transparent: true,
      opacity: 0.5,
      map: smokeTexture
    });

    this.points = new THREE.Points(geometry, this.material);
  }

  update() {
    const posAttr = this.points.geometry.getAttribute('position');
    const positions = posAttr.array;
    const velocities = this.points.geometry.getAttribute('velocity').array;

    for (let i = 0; i < positions.length; i += 3) {
      positions[i] += velocities[i];
      positions[i + 1] += velocities[i + 1];
      positions[i + 2] += velocities[i + 2];

      // Diffusion - slow horizontal spread
      velocities[i] *= 0.99;
      velocities[i + 2] *= 0.99;
    }
    posAttr.needsUpdate = true;
  }
}
```

#### Snow / Rain

```javascript
class SnowParticles {
  constructor(area = 200, count = 5000) {
    const geometry = new THREE.BufferGeometry();
    const positions = new Float32Array(count * 3);
    const velocities = new Float32Array(count * 3);
    const sways = new Float32Array(count);

    for (let i = 0; i < count; i++) {
      positions[i * 3] = (Math.random() - 0.5) * area;
      positions[i * 3 + 1] = (Math.random() - 0.5) * area;
      positions[i * 3 + 2] = (Math.random() - 0.5) * area;

      velocities[i * 3] = 0;
      velocities[i * 3 + 1] = -(0.5 + Math.random() * 1.0); // Fall speed
      velocities[i * 3 + 2] = 0;

      sways[i] = Math.random() * Math.PI * 2;
    }

    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geometry.setAttribute('velocity', new THREE.BufferAttribute(velocities, 3));
    geometry.setAttribute('sway', new THREE.BufferAttribute(sways, 1));

    this.material = new THREE.PointsMaterial({
      size: 0.5,
      color: 0xffffff,
      transparent: true,
      map: snowflakeTexture,
      sizeAttenuation: true,
      fog: true
    });

    this.points = new THREE.Points(geometry, this.material);
    this.area = area;
    this.time = 0;
  }

  update(dt) {
    this.time += dt;
    const posAttr = this.points.geometry.getAttribute('position');
    const positions = posAttr.array;
    const velocities = this.points.geometry.getAttribute('velocity').array;
    const sways = this.points.geometry.getAttribute('sway').array;

    for (let i = 0; i < positions.length; i += 3) {
      // Fall
      positions[i + 1] += velocities[i + 1];

      // Sway - wind
      const swayPhase = sways[i / 3] + this.time;
      positions[i] += Math.sin(swayPhase) * 0.02;

      // Respawn at top
      if (positions[i + 1] < -(this.area / 2)) {
        positions[i + 1] = this.area / 2;
        positions[i] = (Math.random() - 0.5) * this.area;
        positions[i + 2] = (Math.random() - 0.5) * this.area;
      }
    }
    posAttr.needsUpdate = true;
  }
}
```

---

## 6. Fog and Atmosphere

### THREE.Fog and THREE.FogExp2

**Linear Fog**:
```javascript
const fog = new THREE.Fog(0x000000, 100, 1000);
scene.fog = fog;

// fog.color: Color
// fog.near: Distance where fog starts
// fog.far: Distance where fog is complete
```

**Exponential Fog** (grows exponentially):
```javascript
const fog = new THREE.FogExp2(0x000000, 0.0002);
scene.fog = fog;

// fog.color: Color
// fog.density: How quickly fog increases (0-1 typical range)
// Denser = more fog closer
```

**Runtime Changes**:
```javascript
scene.fog.color.set(0xff0000); // Change color
scene.fog.near = 50;           // For linear fog
scene.fog.far = 500;
```

### Volumetric Fog with Raymarching

Fog effect that fills space realistically (post-processing).

```javascript
const volumetricFogShader = {
  uniforms: {
    tDiffuse: { value: null },
    tDepth: { value: null },
    cameraFar: { value: 1000 },
    fogColor: { value: new THREE.Color(0x888888) },
    fogDensity: { value: 0.01 }
  },
  vertexShader: `
    varying vec2 vUv;
    void main() {
      vUv = uv;
      gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    }
  `,
  fragmentShader: `
    uniform sampler2D tDiffuse;
    uniform sampler2D tDepth;
    uniform vec3 fogColor;
    uniform float fogDensity;
    uniform float cameraFar;
    varying vec2 vUv;

    void main() {
      vec4 color = texture2D(tDiffuse, vUv);
      float depth = texture2D(tDepth, vUv).r;
      float distance = depth * cameraFar;

      // Exponential fog
      float fogFactor = exp(-fogDensity * fogDensity * distance * distance);

      gl_FragColor = vec4(mix(fogColor, color.rgb, fogFactor), color.a);
    }
  `
};

const volumetricPass = new ShaderPass(volumetricFogShader);
composer.addPass(volumetricPass);
```

### Atmospheric Scattering (Sky Simulation)

Simulates Rayleigh and Mie scattering for realistic sky.

```javascript
const skyShader = {
  uniforms: {
    sunPosition: { value: new THREE.Vector3(0, 1, 0).normalize() },
    turbidity: { value: 10 },      // 0=clear, 20=hazy
    rayleigh: { value: 2.0 },       // Blue scattering
    mieCoefficient: { value: 0.005 },
    mieDirectionalG: { value: 0.8 }
  },
  vertexShader: `
    varying vec3 vWorldPosition;
    void main() {
      vec4 worldPos = modelMatrix * vec4(position, 1.0);
      vWorldPosition = worldPos.xyz;
      gl_Position = projectionMatrix * viewMatrix * worldPos;
    }
  `,
  fragmentShader: `
    uniform vec3 sunPosition;
    uniform float turbidity;
    uniform float rayleigh;
    uniform float mieCoefficient;
    varying vec3 vWorldPosition;

    const vec3 up = vec3(0.0, 1.0, 0.0);
    const float e = 2.71828182845904523536;

    // Rayleigh scattering
    vec3 rayleighScatter(float distance, vec3 direction) {
      float cosAngle = dot(direction, sunPosition);
      float rPhase = 0.75 * (1.0 + cosAngle * cosAngle);

      vec3 wavelength = vec3(680e-9, 550e-9, 450e-9);
      vec3 mieCoeff = vec3(0.434, 0.434, 0.434) * (turbidity * 0.01);

      return rPhase * pow(e, -(rayleigh / wavelength));
    }

    void main() {
      vec3 direction = normalize(vWorldPosition);
      vec3 scatter = rayleighScatter(1.0, direction);
      gl_FragColor = vec4(scatter, 1.0);
    }
  `
};
```

### God Rays / Volumetric Light Shafts

Post-processing effect that creates light shafts from a light source.

```javascript
const godRaysShader = {
  uniforms: {
    tDiffuse: { value: null },
    lightPosition: { value: new THREE.Vector2(0.5, 0.5) }, // Screen space
    density: { value: 0.5 },
    decay: { value: 0.95 },
    weight: { value: 0.4 },
    samples: { value: 100.0 },
    exposure: { value: 0.6 }
  },
  fragmentShader: `
    uniform sampler2D tDiffuse;
    uniform vec2 lightPosition;
    uniform float density;
    uniform float decay;
    uniform float weight;
    uniform float samples;
    uniform float exposure;
    varying vec2 vUv;

    void main() {
      vec2 texCoord = vUv;
      vec2 deltaCoord = normalize(lightPosition - texCoord);
      deltaCoord *= 1.0 / samples * density;

      float illuminationDecay = 1.0;
      vec3 color = texture2D(tDiffuse, texCoord).rgb;

      for (float i = 0.0; i < samples; i += 1.0) {
        texCoord -= deltaCoord;
        vec3 sample = texture2D(tDiffuse, texCoord).rgb;

        sample *= illuminationDecay * weight;
        color += sample;

        illuminationDecay *= decay;
      }

      gl_FragColor = vec4(color * exposure, 1.0);
    }
  `
};
```

### Dust Motes and Floating Particles

Interior atmosphere effect using Points with slow animation.

```javascript
class DustMotes {
  constructor(count = 1000) {
    const geometry = new THREE.BufferGeometry();
    const positions = new Float32Array(count * 3);
    const scales = new Float32Array(count);

    for (let i = 0; i < count; i++) {
      positions[i * 3] = (Math.random() - 0.5) * 100;
      positions[i * 3 + 1] = (Math.random() - 0.5) * 100;
      positions[i * 3 + 2] = (Math.random() - 0.5) * 100;

      scales[i] = Math.random() * 0.5 + 0.1;
    }

    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geometry.setAttribute('scale', new THREE.BufferAttribute(scales, 1));

    this.material = new THREE.PointsMaterial({
      size: 0.1,
      color: 0xffffff,
      transparent: true,
      opacity: 0.3,
      map: dustTexture
    });

    this.points = new THREE.Points(geometry, this.material);
    this.time = 0;
    this.positions = positions;
  }

  update(dt) {
    this.time += dt * 0.1;
    const posAttr = this.points.geometry.getAttribute('position');
    const positions = posAttr.array;

    for (let i = 0; i < positions.length; i += 3) {
      // Slow Brownian motion
      positions[i] += Math.sin(this.time + i) * 0.01;
      positions[i + 1] += Math.cos(this.time + i * 0.7) * 0.005;
      positions[i + 2] += Math.sin(this.time * 0.7 + i) * 0.01;
    }
    posAttr.needsUpdate = true;
  }
}
```

---

## 7. Shadows

### Shadow Map Types

**BasicShadowMap (THREE.BasicShadowMap)**
- Hardest shadows, fastest
- No filtering, aliasing visible
```javascript
renderer.shadowMap.type = THREE.BasicShadowMap;
```

**PCF (Percentage Closer Filtering) (THREE.PCFShadowMap)**
- Standard soft shadows
- 3x3 kernel samples
- Balance of quality and performance
```javascript
renderer.shadowMap.type = THREE.PCFShadowMap;
```

**PCFSoft (THREE.PCFSoftShadowMap)**
- Better soft shadows than PCF
- Higher quality filtering
- Slightly slower
```javascript
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
```

**VSM (THREE.VSMShadowMap)**
- Variance-based soft shadows
- Advanced filtering
- Can suffer from light bleeding
```javascript
renderer.shadowMap.type = THREE.VSMShadowMap;
```

### Shadow Map Resolution and Bias Tuning

```javascript
// Setup
const light = new THREE.DirectionalLight(0xffffff, 1);
light.castShadow = true;

// Resolution (power of 2)
light.shadow.mapSize.width = 2048;
light.shadow.mapSize.height = 2048;

// Camera frustum
light.shadow.camera.left = -100;
light.shadow.camera.right = 100;
light.shadow.camera.top = 100;
light.shadow.camera.bottom = -100;
light.shadow.camera.near = 0.5;
light.shadow.camera.far = 500;

// Bias - prevents shadow acne and peter-panning
light.shadow.bias = -0.0001;     // Adjust for acne
light.shadow.normalBias = 0.02;  // Adjust for peter-panning

// Blur
light.shadow.blurSamples = 8;    // For soft shadows

// Objects
mesh.castShadow = true;
mesh.receiveShadow = true;

renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
```

### Cascaded Shadow Maps (CSM)

For large scenes with distant objects, use multiple shadow maps at different scales.

```javascript
import { CSM } from 'three/examples/jsm/csm/CSM.js';

const csm = new CSM({
  maxFar: 3000,
  cascades: 4,
  lightIntensity: 1,
  shadowMapSize: 2048,
  lightNear: 0.5,
  lightFar: 3000,
  lightMargin: 200,
  mode: 'practical' // 'uniform', 'logarithmic', 'practical'
});

csm.getLight().position.set(0, 50, 50);
scene.add(csm.getLight());

// Add meshes to receive CSM shadows
for (let mesh of meshes) {
  csm.setupMaterial(mesh.material);
  mesh.castShadow = true;
  mesh.receiveShadow = true;
}

// In render loop
csm.update(camera);
renderer.render(scene, camera);
```

**CSM Benefits**:
- High-resolution shadows near camera
- Lower resolution for distant objects
- Efficient for large-scale terrains and worlds
- Reduces aliasing and shadow banding

### Contact Shadows

"Fake" soft shadows that don't require shadow maps - raymarched screen-space solution.

```javascript
// Raymarched contact shadow
const contactShadowShader = {
  uniforms: {
    tDiffuse: { value: null },
    tDepth: { value: null },
    lightPos: { value: new THREE.Vector3(5, 10, 5) },
    bias: { value: 0.01 },
    intensity: { value: 1.0 }
  },
  fragmentShader: `
    uniform sampler2D tDiffuse;
    uniform sampler2D tDepth;
    uniform vec3 lightPos;
    uniform float bias;
    uniform float intensity;
    varying vec2 vUv;

    // Simple contact shadow
    void main() {
      float depth = texture2D(tDepth, vUv).r;

      // Raymarch from surface toward light
      float shadow = 0.0;
      for (int i = 0; i < 10; i++) {
        float sample = texture2D(tDepth, vUv + vec2(float(i)) * 0.01).r;
        if (sample > depth + bias) {
          shadow += 0.1;
        }
      }

      vec4 color = texture2D(tDiffuse, vUv);
      color.rgb *= 1.0 - shadow * intensity;
      gl_FragColor = color;
    }
  `
};
```

### Baked Shadows vs Real-Time

**Real-Time Shadows**:
- Advantages: Dynamic, objects can move, lighting changes
- Disadvantages: Performance cost, limited resolution, aliasing
- Best for: Animated objects, moving lights, interactive scenes

**Baked Shadows**:
- Advantages: High quality, free at runtime, no aliasing
- Disadvantages: Static, must bake when scene changes, large texture memory
- Best for: Static environments, background elements, optimization

**Hybrid Approach**:
```javascript
// Bake static geometry shadows
const staticMaterial = new THREE.MeshStandardMaterial({
  map: colorTexture,
  aoMap: bakedShadowTexture, // Use AO for baked shadows
  aoMapIntensity: 1.0
});

// Real-time shadows for dynamic objects
const dynamicMesh = new THREE.Mesh(geometry, new THREE.MeshStandardMaterial());
dynamicMesh.castShadow = true;
dynamicMesh.receiveShadow = true;
```

---

## 8. Advanced Rendering Techniques

### Deferred Rendering

Renders geometry properties (position, normal, albedo, roughness) to multiple targets first, then lights operate on those buffers.

```javascript
import { WebGLMultipleRenderTargets } from 'three';

const gBuffer = new WebGLMultipleRenderTargets(
  window.innerWidth,
  window.innerHeight,
  4 // Number of targets
);

gBuffer.texture[0].internalFormat = 'RGBA';    // Position
gBuffer.texture[1].internalFormat = 'RGBA';    // Normal
gBuffer.texture[2].internalFormat = 'RGBA';    // Albedo
gBuffer.texture[3].internalFormat = 'RGBA';    // Roughness/Metallic

// G-Buffer material
const gBufferMaterial = new THREE.RawShaderMaterial({
  vertexShader: `
    varying vec3 vPosition;
    varying vec3 vNormal;
    varying vec2 vUv;
    void main() {
      vPosition = position;
      vNormal = normal;
      vUv = uv;
      gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    }
  `,
  fragmentShader: `
    varying vec3 vPosition;
    varying vec3 vNormal;
    varying vec2 vUv;

    layout(location = 0) out vec4 outPosition;
    layout(location = 1) out vec4 outNormal;
    layout(location = 2) out vec4 outAlbedo;
    layout(location = 3) out vec4 outRoughnessMetallic;

    void main() {
      outPosition = vec4(vPosition, 1.0);
      outNormal = vec4(normalize(vNormal), 1.0);
      outAlbedo = vec4(0.8, 0.8, 0.8, 1.0); // Base color
      outRoughnessMetallic = vec4(0.5, 0.0, 0.0, 1.0);
    }
  `
});

// Deferred lighting pass
const lightingPass = new ShaderPass(deferredLightingShader);
lightingPass.uniforms.gPosition.value = gBuffer.texture[0];
lightingPass.uniforms.gNormal.value = gBuffer.texture[1];
lightingPass.uniforms.gAlbedo.value = gBuffer.texture[2];
lightingPass.uniforms.gRoughnessMetallic.value = gBuffer.texture[3];
```

**Advantages**: Supports many lights efficiently

**Disadvantages**: Higher bandwidth, MSAA not compatible, expensive to implement

### Screen-Space Reflections (SSR)

Reflections computed from screen-space depth/normal information.

```javascript
const ssrShader = {
  uniforms: {
    tDiffuse: { value: null },
    tDepth: { value: null },
    tNormal: { value: null },
    tRoughness: { value: null },
    cameraProjectionMatrix: { value: camera.projectionMatrix }
  },
  fragmentShader: `
    uniform sampler2D tDiffuse;
    uniform sampler2D tDepth;
    uniform sampler2D tNormal;
    uniform sampler2D tRoughness;
    varying vec2 vUv;

    vec4 rayMarch(vec3 position, vec3 direction, sampler2D tDepth) {
      vec3 march = position + direction;

      for (int i = 0; i < 64; i++) {
        float depth = texture2D(tDepth, march.xy).r;
        if (march.z > depth) {
          return vec4(march.xy, depth, 1.0);
        }
        march += direction * 0.1;
      }
      return vec4(0.0);
    }

    void main() {
      vec3 normal = texture2D(tNormal, vUv).rgb;
      vec3 reflected = reflect(vec3(0, 0, 1), normal);

      vec4 hitPos = rayMarch(vec3(vUv, 0.0), reflected, tDepth);

      if (hitPos.w > 0.0) {
        gl_FragColor = texture2D(tDiffuse, hitPos.xy);
      } else {
        gl_FragColor = vec4(0.0);
      }
    }
  `
};
```

**Advantages**: Fast reflection approximation, no geometry needed

**Disadvantages**: Screen-space only, artifacts at edges, fallback needed for off-screen reflections

### Decal Systems

Apply decals (bullet holes, damage, graffiti) to surfaces using projected geometry.

```javascript
class DecalSystem {
  constructor(scene) {
    this.scene = scene;
    this.decals = [];
  }

  addDecal(position, normal, size, texture) {
    // Create decal mesh
    const geometry = new THREE.BoxGeometry(size, size, size);

    // Decal material - transparent with texture
    const material = new THREE.MeshBasicMaterial({
      map: texture,
      transparent: true,
      depthTest: false,
      depthWrite: false,
      polygonOffset: true,
      polygonOffsetFactor: -2
    });

    const decal = new THREE.Mesh(geometry, material);
    decal.position.copy(position);

    // Orient to surface normal
    const quaternion = new THREE.Quaternion();
    quaternion.setFromUnitVectors(new THREE.Vector3(0, 0, 1), normal);
    decal.quaternion.copy(quaternion);

    this.scene.add(decal);
    this.decals.push(decal);

    // Auto-remove after timeout
    setTimeout(() => {
      this.scene.remove(decal);
      this.decals.splice(this.decals.indexOf(decal), 1);
    }, 10000);
  }
}

// Usage
const decalSystem = new DecalSystem(scene);
const hitPoint = raycast.intersectObjects(scene)[0].point;
const normal = raycast.intersectObjects(scene)[0].face.normal;
decalSystem.addDecal(hitPoint, normal, 0.5, bulletHoleTexture);
```

### Level of Detail (LOD) System

Render different mesh complexity based on distance.

```javascript
class LODManager {
  constructor() {
    this.lods = [];
  }

  addLODObject(camera, lowRes, medRes, highRes, dist1, dist2) {
    const lod = new THREE.LOD();

    lod.addLevel(highRes, 0);       // Full detail at 0-dist1
    lod.addLevel(medRes, dist1);    // Medium detail at dist1-dist2
    lod.addLevel(lowRes, dist2);    // Low detail beyond dist2

    lod.position.copy(lowRes.position);

    this.lods.push(lod);
    return lod;
  }

  update(camera) {
    for (let lod of this.lods) {
      lod.update(camera);
    }
  }
}

// Usage
const lodManager = new LODManager();

const highDetail = createHighPolyMesh();
const medDetail = createMediumPolyMesh();
const lowDetail = createLowPolyMesh();

const lod = lodManager.addLODObject(camera, lowDetail, medDetail, highDetail, 50, 200);
scene.add(lod);

// In animation loop
lodManager.update(camera);
```

### Impostor / Billboard Rendering

Replace distant 3D geometry with textured billboards.

```javascript
class ImpostorRenderer {
  constructor(size = 10, resolution = 512) {
    this.size = size;
    this.resolution = resolution;
    this.impostors = [];
  }

  createImpostor(geometry, material, position) {
    // Render geometry to impostor texture
    const canvas = new THREE.OffscreenCanvas(this.resolution, this.resolution);
    const ctx = canvas.getContext('2d');

    // Create impostor sprite
    const impostorMaterial = new THREE.SpriteMaterial({
      map: new THREE.CanvasTexture(canvas),
      sizeAttenuation: true
    });

    const impostor = new THREE.Sprite(impostorMaterial);
    impostor.position.copy(position);
    impostor.scale.set(this.size, this.size, 1);

    this.impostors.push(impostor);
    return impostor;
  }
}

// Usage
const impostorRenderer = new ImpostorRenderer();
const impostor = impostorRenderer.createImpostor(geometry, material, position);
scene.add(impostor);
```

### Instanced Rendering for 1000+ Objects

Optimal pattern for rendering many copies of the same mesh.

```javascript
class InstancedObjectPool {
  constructor(geometry, material, count) {
    this.instancedMesh = new THREE.InstancedMesh(geometry, material, count);
    this.count = count;
    this.dummy = new THREE.Object3D();
    this.activeInstances = 0;
  }

  addInstance(position, rotation = null, scale = 1) {
    if (this.activeInstances >= this.count) {
      console.warn('Instance pool full');
      return -1;
    }

    this.dummy.position.copy(position);
    if (rotation) this.dummy.quaternion.copy(rotation);
    this.dummy.scale.setScalar(scale);
    this.dummy.updateMatrix();

    this.instancedMesh.setMatrixAt(this.activeInstances, this.dummy.matrix);
    this.instancedMesh.instanceMatrix.needsUpdate = true;

    return this.activeInstances++;
  }

  updateInstance(index, position, rotation = null) {
    this.dummy.position.copy(position);
    if (rotation) this.dummy.quaternion.copy(rotation);
    this.dummy.updateMatrix();

    this.instancedMesh.setMatrixAt(index, this.dummy.matrix);
    this.instancedMesh.instanceMatrix.needsUpdate = true;
  }

  getInstancedMesh() {
    return this.instancedMesh;
  }
}

// Usage
const pool = new InstancedObjectPool(treeGeometry, treeMaterial, 10000);

for (let i = 0; i < 10000; i++) {
  const x = (Math.random() - 0.5) * 1000;
  const z = (Math.random() - 0.5) * 1000;
  pool.addInstance(new THREE.Vector3(x, 0, z));
}

scene.add(pool.getInstancedMesh());
```

---

## Performance Optimization Checklist

- Use pmndrs/postprocessing for complex effect chains
- Set `renderer.shadowMap.type = THREE.PCFSoftShadowMap` (balanced quality)
- Limit shadow map resolution to actual needs (1024-2048 typical)
- Use InstancedMesh for 100+ identical objects
- Implement LOD for distant objects
- Use baked shadows for static geometry
- Disable unused buffers: `renderer.outputColorSpace = THREE.SRGBColorSpace`
- Profile with DevTools: check draw calls and GPU time
- Consider using WebGPU compute shaders for particle physics
- Use canvas-generated textures only once, cache results

---

## References and Further Reading

- [Three.js Post-Processing Documentation](https://threejs.org/manual/en/post-processing.html)
- [pmndrs/postprocessing GitHub](https://github.com/pmndrs/postprocessing)
- [Three.js Shadows Tutorial](https://threejs-journey.com/lessons/shadows)
- [Three-Nebula Particle Engine](https://three-nebula.org/)
- [Three.Quarks VFX Library](https://quarks.art/)
- [Three.js Examples Collection](https://threejs.org/examples/)
