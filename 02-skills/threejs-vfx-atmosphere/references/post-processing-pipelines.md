# Post-Processing Pipelines for Three.js

Complete, production-ready post-processing configurations for various visual styles and moods.

## Cinematic Sci-Fi Pipeline

High-end cinematic look with bloom, ambient occlusion, film grain, and color grading.

```typescript
import { EffectComposer } from 'three/examples/jsm/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/examples/jsm/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/examples/jsm/postprocessing/UnrealBloomPass.js';
import { SSAOPass } from 'three/examples/jsm/postprocessing/SSAOPass.js';
import { FilmPass } from 'three/examples/jsm/postprocessing/FilmPass.js';
import { ShaderPass } from 'three/examples/jsm/postprocessing/ShaderPass.js';
import { SMAAPass } from 'three/examples/jsm/postprocessing/SMAAPass.js';

export function createCinematicSciFilePipeline(
  renderer: THREE.WebGLRenderer,
  scene: THREE.Scene,
  camera: THREE.PerspectiveCamera
): EffectComposer {
  const composer = new EffectComposer(renderer);
  const w = window.innerWidth;
  const h = window.innerHeight;

  // 1. Render scene
  const renderPass = new RenderPass(scene, camera);
  composer.addPass(renderPass);

  // 2. Ambient occlusion (screen-space)
  const ssaoPass = new SSAOPass(scene, camera, w, h);
  ssaoPass.kernelRadius = 16;
  ssaoPass.aoRadius = 2.5;
  ssaoPass.intensity = 1.2;
  ssaoPass.minDistance = 0.005;
  ssaoPass.maxDistance = 0.1;
  composer.addPass(ssaoPass);

  // 3. Bloom for bright emissive materials
  const bloomPass = new UnrealBloomPass(
    new THREE.Vector2(w, h),
    1.5,    // strength
    0.4,    // radius
    0.85    // threshold
  );
  composer.addPass(bloomPass);

  // 4. Film grain for cinematic texture
  const filmPass = new FilmPass(
    0.25,    // noise intensity
    0.03,    // scanline intensity
    648,     // scanline count
    false    // grayscale
  );
  composer.addPass(filmPass);

  // 5. Color grading + tone mapping
  const colorGradePass = new ShaderPass(createCinematicColorShader());
  colorGradePass.uniforms.saturation.value = 1.0;
  colorGradePass.uniforms.brightness.value = 1.05;
  colorGradePass.uniforms.contrast.value = 1.1;
  colorGradePass.uniforms.colorShift.value = new THREE.Vector3(0.05, 0.02, -0.02);
  composer.addPass(colorGradePass);

  // 6. Anti-aliasing
  const smaaPass = new SMAAPass(w, h);
  composer.addPass(smaaPass);

  smaaPass.renderToScreen = true;
  return composer;
}

function createCinematicColorShader() {
  return {
    uniforms: {
      tDiffuse: { value: null },
      saturation: { value: 1.0 },
      brightness: { value: 1.0 },
      contrast: { value: 1.0 },
      colorShift: { value: new THREE.Vector3(0, 0, 0) }
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
      uniform float saturation;
      uniform float brightness;
      uniform float contrast;
      uniform vec3 colorShift;
      varying vec2 vUv;

      void main() {
        vec4 texColor = texture2D(tDiffuse, vUv);
        vec3 color = texColor.rgb;

        // Saturation
        float gray = dot(color, vec3(0.299, 0.587, 0.114));
        color = mix(vec3(gray), color, saturation);

        // Color shift (warm cyan-red gradient)
        color += colorShift;

        // Brightness and contrast
        color *= brightness;
        color = mix(vec3(0.5), color, contrast);

        gl_FragColor = vec4(color, texColor.a);
      }
    `
  };
}
```

**Parameters to Tune**:
- SSAO `aoRadius`: 1.0-5.0 (larger = broader shadows)
- Bloom `strength`: 0.5-2.0 (1.5 default is safe)
- Bloom `threshold`: 0.75-0.95 (higher = less bloom, more selective)
- Film grain `nIntensity`: 0.1-0.5 (very subtle, use sparingly)

---

## Industrial Interior Pipeline

Emphasizes depth, spatial awareness, and muted industrial aesthetic.

```typescript
export function createIndustrialInteriorPipeline(
  renderer: THREE.WebGLRenderer,
  scene: THREE.Scene,
  camera: THREE.PerspectiveCamera
): EffectComposer {
  const composer = new EffectComposer(renderer);
  const w = window.innerWidth;
  const h = window.innerHeight;

  const renderPass = new RenderPass(scene, camera);
  composer.addPass(renderPass);

  // Heavy SSAO for industrial crevices and depth
  const ssao = new SSAOPass(scene, camera, w, h);
  ssao.kernelRadius = 24;      // High quality
  ssao.aoRadius = 3.0;         // Larger radius for broad shadows
  ssao.intensity = 1.8;        // Dark industrial look
  ssao.minDistance = 0.005;
  ssao.maxDistance = 0.15;
  composer.addPass(ssao);

  // Subtle bloom only on metallic highlights
  const bloom = new UnrealBloomPass(
    new THREE.Vector2(w, h),
    0.8,    // Lower strength for industrial
    0.3,    // Smaller radius
    0.95    // High threshold - only brightest metal
  );
  composer.addPass(bloom);

  // Desaturated, cool color grade
  const colorPass = new ShaderPass(createIndustrialColorShader());
  composer.addPass(colorPass);

  const smaa = new SMAAPass(w, h);
  composer.addPass(smaa);
  smaa.renderToScreen = true;

  return composer;
}

function createIndustrialColorShader() {
  return {
    uniforms: {
      tDiffuse: { value: null }
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
      varying vec2 vUv;

      void main() {
        vec4 color = texture2D(tDiffuse, vUv);

        // Desaturate (industrial gray aesthetic)
        float lum = dot(color.rgb, vec3(0.299, 0.587, 0.114));
        color.rgb = mix(vec3(lum), color.rgb, 0.6);

        // Cool blue-gray shift
        color.r *= 0.95;
        color.b *= 1.05;

        // Slightly reduce brightness (darker)
        color.rgb *= 0.95;

        gl_FragColor = color;
      }
    `
  };
}
```

**Key Parameters**:
- SSAO `intensity`: 1.5-2.0 (darker for industrial feel)
- Bloom `threshold`: 0.95 (very selective, only metal)
- Color shift: Boost blue, reduce red for cool tone

---

## Emergency/Alert Pipeline

Red warning aesthetic with high contrast and urgency signaling.

```typescript
export function createEmergencyAlertPipeline(
  renderer: THREE.WebGLRenderer,
  scene: THREE.Scene,
  camera: THREE.PerspectiveCamera
): EffectComposer {
  const composer = new EffectComposer(renderer);
  const w = window.innerWidth;
  const h = window.innerHeight;

  const renderPass = new RenderPass(scene, camera);
  composer.addPass(renderPass);

  // Moderate bloom on warning lights
  const bloom = new UnrealBloomPass(
    new THREE.Vector2(w, h),
    1.2,
    0.5,
    0.8
  );
  composer.addPass(bloom);

  // High-contrast red alert color grade
  const alertPass = new ShaderPass(createEmergencyColorShader());
  composer.addPass(alertPass);

  const smaa = new SMAAPass(w, h);
  composer.addPass(smaa);
  smaa.renderToScreen = true;

  return composer;
}

function createEmergencyColorShader() {
  return {
    uniforms: {
      tDiffuse: { value: null }
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
      varying vec2 vUv;

      void main() {
        vec4 color = texture2D(tDiffuse, vUv);

        // Boost red channel significantly
        color.r *= 1.3;
        color.g *= 0.7;
        color.b *= 0.7;

        // Reduce overall saturation but keep red
        float lum = dot(color.rgb, vec3(0.299, 0.587, 0.114));
        color.rgb = mix(vec3(lum * 0.8), color.rgb, 0.5);

        // High contrast
        color.rgb = mix(vec3(0.5), color.rgb, 1.3);

        // Slight vignette effect
        vec2 vignette = vUv - 0.5;
        float vig = 1.0 - length(vignette) * 1.2;
        color.rgb *= vig;

        gl_FragColor = color;
      }
    `
  };
}
```

**Configuration**:
- Use red emissive materials in scene for alerts
- Bloom will amplify them
- High contrast emphasizes danger
- Vignette draws focus inward

---

## Deep Space Pipeline

Subtle, ethereal look with minimal bloom on distant stars and clean colors.

```typescript
export function createDeepSpacePipeline(
  renderer: THREE.WebGLRenderer,
  scene: THREE.Scene,
  camera: THREE.PerspectiveCamera
): EffectComposer {
  const composer = new EffectComposer(renderer);
  const w = window.innerWidth;
  const h = window.innerHeight;

  const renderPass = new RenderPass(scene, camera);
  composer.addPass(renderPass);

  // Very subtle bloom only for stars
  const bloom = new UnrealBloomPass(
    new THREE.Vector2(w, h),
    0.4,    // Very subtle
    0.2,
    0.95    // Only brightest stars
  );
  composer.addPass(bloom);

  // Minimal film grain
  const film = new FilmPass(0.1, 0.01, 648, false);
  composer.addPass(film);

  // Clean, cool color grading
  const colorPass = new ShaderPass(createDeepSpaceColorShader());
  composer.addPass(colorPass);

  const smaa = new SMAAPass(w, h);
  composer.addPass(smaa);
  smaa.renderToScreen = true;

  return composer;
}

function createDeepSpaceColorShader() {
  return {
    uniforms: {
      tDiffuse: { value: null }
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
      varying vec2 vUv;

      void main() {
        vec4 color = texture2D(tDiffuse, vUv);

        // Slightly boost blues for space aesthetic
        color.b *= 1.1;
        color.r *= 0.95;

        // Very slight vignette
        vec2 vignette = vUv - 0.5;
        float vig = 1.0 - length(vignette) * 0.5;
        color.rgb *= vig;

        gl_FragColor = color;
      }
    `
  };
}
```

**Key Idea**: Restraint. Deep space should feel clean, stars should twinkle, black should be truly black.

---

## Discovery Pipeline

Warm, welcoming aesthetic for exploration and discovery moments.

```typescript
export function createDiscoveryPipeline(
  renderer: THREE.WebGLRenderer,
  scene: THREE.Scene,
  camera: THREE.PerspectiveCamera
): EffectComposer {
  const composer = new EffectComposer(renderer);
  const w = window.innerWidth;
  const h = window.innerHeight;

  const renderPass = new RenderPass(scene, camera);
  composer.addPass(renderPass);

  // Moderate SSAO for depth perception
  const ssao = new SSAOPass(scene, camera, w, h);
  ssao.kernelRadius = 16;
  ssao.aoRadius = 2.0;
  ssao.intensity = 0.8;
  composer.addPass(ssao);

  // Warm bloom
  const bloom = new UnrealBloomPass(
    new THREE.Vector2(w, h),
    1.3,
    0.4,
    0.8
  );
  composer.addPass(bloom);

  // Depth of field for cinematic focus
  const bokeh = new BokehPass(scene, camera, {
    focus: 1000,
    aperture: 2.5,
    maxblur: 0.01
  });
  composer.addPass(bokeh);

  // Warm color grading
  const colorPass = new ShaderPass(createDiscoveryColorShader());
  composer.addPass(colorPass);

  const smaa = new SMAAPass(w, h);
  composer.addPass(smaa);
  smaa.renderToScreen = true;

  return composer;
}

function createDiscoveryColorShader() {
  return {
    uniforms: {
      tDiffuse: { value: null }
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
      varying vec2 vUv;

      void main() {
        vec4 color = texture2D(tDiffuse, vUv);

        // Warm color shift
        color.r *= 1.1;
        color.g *= 1.05;
        color.b *= 0.95;

        // Slight saturation boost
        float lum = dot(color.rgb, vec3(0.299, 0.587, 0.114));
        color.rgb = mix(vec3(lum), color.rgb, 1.1);

        // Gentle contrast
        color.rgb = mix(vec3(0.5), color.rgb, 1.05);

        gl_FragColor = color;
      }
    `
  };
}
```

**Character**: Welcoming, inviting, emphasizes discovery. Warm tones, moderate contrast, good depth.

---

## Individual Pass Tuning Guide

### UnrealBloomPass Parameters

```typescript
// Strength: How bright the bloom is
// 0.5  = subtle, almost invisible
// 1.5  = moderate, professional
// 2.0+ = intense, dreamlike

// Radius: Spread of the bloom glow
// 0.1  = tight, local to bright pixels
// 0.4  = standard, 40 pixels
// 0.8+ = wide, strong blur

// Threshold: Determines which pixels bloom
// 0.5  = almost everything blooms
// 0.85 = bright materials only
// 0.95 = only extremely bright (stars, lights)

bloomPass.strength = 1.5;
bloomPass.radius = 0.4;
bloomPass.threshold = 0.85;
```

### SSAOPass Tuning

```typescript
// aoRadius: World-space size of occlusion
// 1.0  = tight, crevices only
// 2.5  = moderate, good balance
// 5.0+ = broad, cave-like depth

// intensity: Darkness multiplier
// 0.5  = subtle, naturalistic
// 1.0  = moderate
// 1.5+ = dramatic, heavy shadows

// kernelRadius: Sampling quality
// 8    = fast, visible banding
// 16   = balanced
// 32   = high quality, slower

ssao.aoRadius = 2.5;
ssao.intensity = 1.0;
ssao.kernelRadius = 16;
```

### FilmPass Tuning

```typescript
// nIntensity: Film grain noise
// 0.1  = subtle texture
// 0.3  = moderate grain
// 0.5+ = very grainy, vintage

// sIntensity: Scanline visibility
// 0.01 = barely visible
// 0.03 = subtle CRT effect
// 0.1+ = strong scanlines, retro

filmPass.uniforms.nIntensity.value = 0.25;
filmPass.uniforms.sIntensity.value = 0.025;
```

---

## Custom LUT-Based Color Grading Implementation

Advanced color grading using 3D lookup tables.

```typescript
export function createLUTColorGradingPass(
  lutTexture: THREE.Texture,
  mood: 'warm' | 'cold' | 'cinematic' | 'scifi'
): ShaderPass {
  const pass = new ShaderPass(createLUTShader());
  pass.uniforms.tLUT.value = lutTexture;

  switch (mood) {
    case 'warm':
      pass.uniforms.saturation.value = 1.15;
      pass.uniforms.brightness.value = 1.08;
      pass.uniforms.contrast.value = 1.0;
      break;
    case 'cold':
      pass.uniforms.saturation.value = 0.75;
      pass.uniforms.brightness.value = 0.95;
      pass.uniforms.contrast.value = 1.1;
      break;
    case 'cinematic':
      pass.uniforms.saturation.value = 1.0;
      pass.uniforms.brightness.value = 1.05;
      pass.uniforms.contrast.value = 1.15;
      break;
    case 'scifi':
      pass.uniforms.saturation.value = 1.2;
      pass.uniforms.brightness.value = 1.0;
      pass.uniforms.contrast.value = 1.2;
      break;
  }

  return pass;
}

function createLUTShader() {
  return {
    uniforms: {
      tDiffuse: { value: null },
      tLUT: { value: null },
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

      vec3 applyLUT(vec3 color) {
        float lutSize = 32.0;
        float cellIndex = color.b * (lutSize - 1.0);
        float cellOffset = fract(cellIndex);
        cellIndex = floor(cellIndex);

        vec2 uv = vec2(color.r, color.g);
        uv.x = (uv.x + cellIndex) / lutSize;

        vec3 cell0 = texture2D(tLUT, uv).rgb;
        vec3 cell1 = texture2D(tLUT, uv + vec2(1.0 / lutSize, 0.0)).rgb;

        return mix(cell0, cell1, cellOffset);
      }

      vec3 adjustSaturation(vec3 color, float sat) {
        float gray = dot(color, vec3(0.299, 0.587, 0.114));
        return mix(vec3(gray), color, sat);
      }

      void main() {
        vec4 texColor = texture2D(tDiffuse, vUv);
        vec3 color = texColor.rgb;

        // Apply LUT
        color = applyLUT(color);

        // Adjust properties
        color = adjustSaturation(color, saturation);
        color *= brightness;
        color = mix(vec3(0.5), color, contrast);

        gl_FragColor = vec4(color, texColor.a);
      }
    `
  };
}
```

---

## Pipeline Performance Optimization

### Resolution Scaling

```typescript
function createOptimizedComposer(
  renderer: THREE.WebGLRenderer,
  scene: THREE.Scene,
  camera: THREE.PerspectiveCamera,
  scale: number = 0.8 // 80% resolution
): EffectComposer {
  const w = window.innerWidth * scale;
  const h = window.innerHeight * scale;

  const composer = new EffectComposer(renderer, new THREE.WebGLRenderTarget(w, h));
  // Adds passes...
  return composer;
}
```

### Combining Passes

```typescript
// Instead of multiple SSAO passes, use one tuned pass:
const ssao = new SSAOPass(scene, camera, w, h);
ssao.aoRadius = 2.5;
ssao.intensity = 1.2;
ssao.kernelRadius = 16;
composer.addPass(ssao);

// Instead of separate bloom + color pass, merge shader logic:
// (This requires custom shader combining both effects)
```

### Conditional Passes

```typescript
function addPassIfNeeded(
  composer: EffectComposer,
  pass: Pass,
  enabled: boolean
) {
  if (enabled) {
    composer.addPass(pass);
  }
}

// Usage: Add SSAO only if quality mode
addPassIfNeeded(composer, ssaoPass, settings.quality === 'high');
```
