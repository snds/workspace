# VFX & Lighting Design for Three.js

## Three.js Light Types & Configuration

### Directional Light (Sun/Starlight)

Use for global illumination, simulating the sun or distant star:

```typescript
const sunLight = new THREE.DirectionalLight(0xffffff, 2.0);
sunLight.position.set(50, 30, 40); // Far away, establishes direction
sunLight.castShadow = true;

// Configure shadow map
sunLight.shadow.mapSize.width = 2048;
sunLight.shadow.mapSize.height = 2048;
sunLight.shadow.camera.left = -100;
sunLight.shadow.camera.right = 100;
sunLight.shadow.camera.top = 100;
sunLight.shadow.camera.bottom = -100;
sunLight.shadow.camera.near = 0.5;
sunLight.shadow.camera.far = 500;

// Shadow bias (prevents peter-panning)
sunLight.shadow.bias = -0.0001;
sunLight.shadow.normalBias = 0.02;

scene.add(sunLight);
```

**Parameters**:
- **Intensity**: 1.5–3.0 typical for daylit scenes, 0.3–0.5 for moonlit
- **Color**: 0xffffff (white sun), 0xffffcc (warm sunset), 0x8899ff (cool alien star)
- **Position**: Set far from scene center (e.g., multiply direction by 100)
- **Shadow**: Essential for drama. Adds 1–2ms per frame cost.

---

### Point Light (Localized Glow)

Use for screens, torches, nozzles, local environment lighting:

```typescript
const screenGlow = new THREE.PointLight(0x00ff00, 1.0);
screenGlow.position.set(0, 2, 0);
screenGlow.range = 15; // Attenuation distance
screenGlow.castShadow = true;
scene.add(screenGlow);

// Thruster glow (dynamic, colored)
const thrusterLight = new THREE.PointLight(0xff6600, 0.8);
thrusterLight.position.set(0, 0, -5);
thrusterLight.range = 25;
thrusterLight.decay = 2.0; // Realistic falloff
scene.add(thrusterLight);
```

**Parameters**:
- **Intensity**: 0.3–2.0 (lower = accent light, higher = primary light)
- **Range**: Distance at which light falloff reaches near-zero. ~10–30m typical for interiors.
- **Decay**: 1.0 = linear, 2.0 = realistic quadratic. Use 2.0 for naturalism.
- **castShadow**: Optional. True adds cost, creates dramatic shadows.

---

### Spotlight (Focused Beam)

Use for work rigs, security lights, dramatic accent:

```typescript
const workLight = new THREE.SpotLight(0xffffff, 1.5);
workLight.position.set(10, 8, 5);
workLight.target.position.set(0, 0, 0);
workLight.angle = Math.PI / 6; // ~30° cone
workLight.penumbra = 0.3; // Soft edge falloff
workLight.decay = 2.0;
workLight.distance = 50;
workLight.castShadow = true;
scene.add(workLight);
scene.add(workLight.target);
```

**Parameters**:
- **Angle**: Controls beam width. π/6 ≈ 30° (narrow spotlight), π/4 ≈ 45° (medium), π/3 ≈ 60° (wide flood)
- **Penumbra**: 0.0 = hard edge, 1.0 = very soft. 0.2–0.5 looks natural.
- **Distance**: Maximum range (like range on PointLight)
- **Target**: What the light points at (can be a separate object)

---

### Ambient Light (Global Fill)

Use sparingly—mainly for preventing pitch-black shadows:

```typescript
const ambientLight = new THREE.AmbientLight(0xffffff, 0.3);
scene.add(ambientLight);
```

**Note**: Minimize use. Strong ambient light flattens the scene. Prefer direct lights + shadow maps.

---

## Lighting for Mood

### Operational Industrial

Harsh, efficient, conveying functionality:

```typescript
const operationalSetup = () => {
  // Primary: hard key light, cool white
  const keyLight = new THREE.DirectionalLight(0xffffff, 2.2);
  keyLight.position.set(1, 2, 1).normalize().multiplyScalar(50);
  keyLight.castShadow = true;
  keyLight.shadow.mapSize.set(2048, 2048);
  scene.add(keyLight);

  // Minimal fill: ~20% of key
  const fillLight = new THREE.DirectionalLight(0xaabbff, 0.4);
  fillLight.position.set(-1, 1, -1).normalize().multiplyScalar(50);
  scene.add(fillLight);

  // Color grade: cool, slightly blue
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.0;
};
```

**Result**: High contrast, cold color, clinical feel. Players read urgency and efficiency.

---

### Hab Module (Comfort & Warmth)

Softer, warmer, conveying safety:

```typescript
const habModuleSetup = () => {
  // Warm key light (lower color temperature)
  const keyLight = new THREE.DirectionalLight(0xffddaa, 1.4);
  keyLight.position.set(-1, 3, 2).normalize().multiplyScalar(50);
  keyLight.castShadow = true;
  scene.add(keyLight);

  // Softer fill: ~50% of key
  const fillLight = new THREE.DirectionalLight(0xffccaa, 0.7);
  fillLight.position.set(1, 2, -2).normalize().multiplyScalar(50);
  scene.add(fillLight);

  // Subtle rim: warm glow from behind
  const rimLight = new THREE.DirectionalLight(0xff9966, 0.3);
  rimLight.position.set(0, 1, -3).normalize().multiplyScalar(50);
  scene.add(rimLight);

  // Slightly warm color tone
  renderer.toneMappingExposure = 0.9; // slightly dim, cozy
};
```

**Result**: Inviting, safe, comfortable. Players feel at home.

---

### Emergency/Alert

Red, flickering, conveying danger:

```typescript
const emergencySetup = () => {
  // Red-shifted directional or volumetric effect
  const emergencyLight = new THREE.DirectionalLight(0xff4444, 1.8);
  emergencyLight.position.set(0, 2, 0).normalize().multiplyScalar(50);
  scene.add(emergencyLight);

  // Flickering via pulsing intensity (use in animation loop)
  let flickerTime = 0.0;
  const updateEmergencyFlicker = (deltaTime: number) => {
    flickerTime += deltaTime;
    emergencyLight.intensity = 1.5 + 0.3 * Math.sin(flickerTime * 8.0); // ~8 Hz flicker
  };

  // Red tint via material emissive on emergency geometry
  const emergencyPanel = new THREE.MeshStandardMaterial({
    emissive: 0xff0000,
    emissiveIntensity: 0.5
  });
};
```

**Result**: Tension, urgency, danger. Flickering adds stress.

---

### Discovery/Wonder

Cinematic, cool backlighting, awe:

```typescript
const discoverySetup = () => {
  // Backlighting: cool blue rim light (deep space)
  const backLight = new THREE.DirectionalLight(0x0033ff, 1.5);
  backLight.position.set(0, 2, -3).normalize().multiplyScalar(50);
  scene.add(backLight);

  // Minimal key light (silhouette effect)
  const keyLight = new THREE.DirectionalLight(0x4488ff, 0.3);
  keyLight.position.set(1, 0.5, 1).normalize().multiplyScalar(50);
  scene.add(keyLight);

  // Volumetric fog for drama
  scene.fog = new THREE.FogExp2(0x0a1a3a, 0.003);

  // Particles catch light (nebula haze)
  const particleLight = new THREE.PointLight(0x00ffff, 0.5);
  particleLight.position.set(0, 0, 5);
  particleLight.range = 40;
  scene.add(particleLight);

  // Cool color tone
  renderer.toneMappingExposure = 1.1; // slightly bright, cinematic
};
```

**Result**: Cinematic, mysterious, wonder. Players sense discovery.

---

## Particle Systems in Three.js

### Basic Points Particle System

Use THREE.Points for large particle counts (performant):

```typescript
class ThrusterVFX {
  private particles: THREE.Points;
  private geometry: THREE.BufferGeometry;
  private positions: Float32Array;
  private velocities: Float32Array;

  constructor(nozzlePos: THREE.Vector3, thrustDirection: THREE.Vector3) {
    const particleCount = 1000;
    this.geometry = new THREE.BufferGeometry();

    // Position buffer
    this.positions = new Float32Array(particleCount * 3);
    for (let i = 0; i < particleCount * 3; i += 3) {
      this.positions[i] = nozzlePos.x;
      this.positions[i + 1] = nozzlePos.y;
      this.positions[i + 2] = nozzlePos.z;
    }
    this.geometry.setAttribute('position', new THREE.BufferAttribute(this.positions, 3));

    // Velocity buffer for movement
    this.velocities = new Float32Array(particleCount * 3);
    for (let i = 0; i < particleCount * 3; i += 3) {
      const speed = 10 + Math.random() * 5;
      this.velocities[i] = thrustDirection.x * speed + (Math.random() - 0.5) * 2;
      this.velocities[i + 1] = thrustDirection.y * speed + (Math.random() - 0.5) * 2;
      this.velocities[i + 2] = thrustDirection.z * speed + (Math.random() - 0.5) * 2;
    }

    // Material
    const material = new THREE.PointsMaterial({
      color: 0xff6600,
      size: 0.3,
      sizeAttenuation: true,
      transparent: true,
      opacity: 0.6,
      emissive: 0xff6600,
      emissiveIntensity: 1.0
    });

    this.particles = new THREE.Points(this.geometry, material);
  }

  update(deltaTime: number) {
    const positions = this.geometry.getAttribute('position').array as Float32Array;
    const velocities = this.velocities;
    const gravity = -9.8;

    for (let i = 0; i < positions.length; i += 3) {
      // Apply velocity
      positions[i] += velocities[i] * deltaTime;
      positions[i + 1] += velocities[i + 1] * deltaTime;
      positions[i + 2] += velocities[i + 2] * deltaTime;

      // Apply gravity
      velocities[i + 1] += gravity * deltaTime;

      // Remove particles that are too far
      const dist = Math.sqrt(positions[i] * positions[i] + positions[i + 1] * positions[i + 1] + positions[i + 2] * positions[i + 2]);
      if (dist > 50) {
        positions[i] = positions[i + 1] = positions[i + 2] = -9999; // Off-screen
      }
    }

    this.geometry.getAttribute('position').needsUpdate = true;
  }

  getMesh() {
    return this.particles;
  }
}

// Usage
const thrusters = new ThrusterVFX(new THREE.Vector3(0, 0, 0), new THREE.Vector3(0, 0, -1));
scene.add(thrusters.getMesh());
```

---

### Sparks (Welding, Impact)

Quick, directional particles:

```typescript
class SparkEffect {
  private particles: THREE.Points;

  constructor(position: THREE.Vector3, direction: THREE.Vector3) {
    const particleCount = 50;
    const geometry = new THREE.BufferGeometry();

    const positions = new Float32Array(particleCount * 3);
    const colors = new Float32Array(particleCount * 3);

    for (let i = 0; i < particleCount; i++) {
      const angle = Math.random() * Math.PI * 2;
      const speed = 5 + Math.random() * 15;
      const spread = Math.PI * 0.3; // 60° cone

      positions[i * 3] = position.x;
      positions[i * 3 + 1] = position.y;
      positions[i * 3 + 2] = position.z;

      // Warm orange to white color
      const warm = 0.8 + Math.random() * 0.2;
      colors[i * 3] = 1.0;
      colors[i * 3 + 1] = warm * 0.5;
      colors[i * 3 + 2] = 0.0;
    }

    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));

    const material = new THREE.PointsMaterial({
      size: 0.2,
      sizeAttenuation: true,
      transparent: true,
      opacity: 0.8,
      vertexColors: true
    });

    this.particles = new THREE.Points(geometry, material);
  }

  getMesh() {
    return this.particles;
  }
}
```

---

### Dust & Atmosphere

Large, slow particles for volumetric effect:

```typescript
class DustCloud {
  private particles: THREE.Points;

  constructor(position: THREE.Vector3) {
    const particleCount = 500;
    const geometry = new THREE.BufferGeometry();

    const positions = new Float32Array(particleCount * 3);
    for (let i = 0; i < particleCount; i++) {
      positions[i * 3] = position.x + (Math.random() - 0.5) * 50;
      positions[i * 3 + 1] = position.y + (Math.random() - 0.5) * 30;
      positions[i * 3 + 2] = position.z + (Math.random() - 0.5) * 50;
    }

    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));

    const material = new THREE.PointsMaterial({
      color: 0xaa9966,
      size: 2.0,
      sizeAttenuation: true,
      transparent: true,
      opacity: 0.08,
      fog: true
    });

    this.particles = new THREE.Points(geometry, material);
  }

  getMesh() {
    return this.particles;
  }
}
```

---

### Nebula/Cosmic Haze

Volumetric effect using emissive planes:

```typescript
const createNebula = () => {
  const geometry = new THREE.PlaneGeometry(200, 200);

  const material = new THREE.ShaderMaterial({
    uniforms: {
      time: { value: 0.0 },
      color1: { value: new THREE.Color(0x441166) },
      color2: { value: new THREE.Color(0x1144aa) }
    },
    transparent: true,
    fog: false,
    vertexShader: `
      varying vec2 vUv;
      void main() {
        vUv = uv;
        gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
      }
    `,
    fragmentShader: `
      uniform float time;
      uniform vec3 color1;
      uniform vec3 color2;
      varying vec2 vUv;

      float noise(vec3 p) {
        // Perlin noise or texture-based
        return sin(p.x * 10.0 + time) * cos(p.y * 10.0) * 0.5 + 0.5;
      }

      void main() {
        float n = noise(vec3(vUv, time * 0.1));
        vec3 color = mix(color1, color2, n);
        gl_FragColor = vec4(color, 0.3);
      }
    `
  });

  const nebula = new THREE.Mesh(geometry, material);
  nebula.position.z = -100;
  return nebula;
};
```

---

## Post-Processing Effects

### Bloom (Glow on Bright Surfaces)

```typescript
import { UnrealBloomPass } from 'three/examples/jsm/postprocessing/UnrealBloomPass.js';

const unrealBloomPass = new UnrealBloomPass(
  new THREE.Vector2(window.innerWidth, window.innerHeight),
  1.5,  // strength
  0.4,  // radius
  0.85  // threshold
);

composer.addPass(unrealBloomPass);
```

**Parameters**:
- **Strength**: 0.5–2.0 (intensity of bloom)
- **Radius**: 0.3–1.0 (spread/blur of glow)
- **Threshold**: 0.7–1.2 (what brightness triggers bloom)

---

### Tone Mapping & Exposure

```typescript
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.0;

// Dynamic exposure (fades as player adapts)
let exposureBias = 0.0;
const updateExposure = (deltaTime: number) => {
  const targetExposure = player.inDarkSpace ? -0.5 : 0.0;
  exposureBias = THREE.MathUtils.lerp(exposureBias, targetExposure, deltaTime * 0.5);
  renderer.toneMappingExposure = 1.0 + exposureBias;
};
```

---

### Color Grading

```typescript
const colorGradePass = new THREE.ShaderPass({
  uniforms: {
    tDiffuse: { value: null },
    warmth: { value: 0.0 },
    saturation: { value: 1.0 }
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
});

// Usage
colorGradePass.uniforms.warmth.value = isHabModule ? 0.2 : -0.1;
colorGradePass.uniforms.saturation.value = isEmergency ? 0.6 : 1.0;
composer.addPass(colorGradePass);
```

---

### Fog (Atmospheric)

```typescript
// Exponential fog (realistic for outdoor/space scenes)
scene.fog = new THREE.FogExp2(0x87ceeb, 0.0002);

// Linear fog (useful for interior spaces)
scene.fog = new THREE.Fog(0x505050, 10, 1000);

// Update fog dynamically
scene.fog.color.setHex(isAlert ? 0x440000 : 0x505050);
```

---

### Film Grain & Vignette

```typescript
import { FilmPass } from 'three/examples/jsm/postprocessing/FilmPass.js';

const filmPass = new FilmPass(
  0.35,   // noise intensity
  0.0025, // scan line intensity
  648,    // scan line count
  false   // greyscale
);

composer.addPass(filmPass);
```

---

## Performance Budgeting

**Frame Time Targets**:
- 60fps (16.67ms per frame): VFX budget ~2–3ms
- 30fps (33.33ms per frame): VFX budget ~5ms

**Optimization Strategies**:

1. **Particle Count**: Reduce spawn rate when off-screen. Clamp max particles.
   ```typescript
   const maxParticles = 5000;
   const activeParticles = Math.min(currentParticles, maxParticles);
   ```

2. **Shadows**: Directional light shadows are expensive. Use selectively.
   ```typescript
   sunLight.castShadow = !isPerformanceConstrained;
   ```

3. **Volumetric Fog**: Use simple fog, not fine-detailed volumetric textures.
   ```typescript
   scene.fog = new THREE.FogExp2(skyColor, 0.0003); // Simpler than volumetric shader
   ```

4. **Post-Processing**: Bloom and other passes add cost. Test impact.
   ```typescript
   const enableBloom = !isLowEndDevice;
   if (enableBloom) composer.addPass(bloomPass);
   ```

5. **GPU Particles**: Use THREE.Points instead of custom ShaderMaterial where possible (faster).

---

## Lighting Mood Configuration Table

| Mood | Key Light Color | Key Intensity | Fill Intensity | Fill Color | Result |
|------|-----------------|---------------|----------------|------------|--------|
| Operational | 0xffffff (white) | 2.0–2.5 | 0.2–0.3 | 0xaabbff (cool) | Harsh, efficient |
| Hab Comfort | 0xffddaa (warm) | 1.2–1.5 | 0.5–0.7 | 0xffccaa (warm) | Inviting, safe |
| Emergency | 0xff4444 (red) | 1.5–2.0 + flicker | 0.1 | 0x330000 | Tense, urgent |
| Discovery | 0x4488ff (cool) | 0.2–0.4 | 0.5 | 0x0033ff (deep blue) | Cinematic, wonder |
