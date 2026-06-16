# Particle Systems and Atmospheric Effects

Production-ready implementations of particle systems and atmospheric effects for Three.js.

## Particle System Base Class

Foundation for all particle effects with pooling and lifecycle management.

```typescript
interface Particle {
  position: THREE.Vector3;
  velocity: THREE.Vector3;
  acceleration: THREE.Vector3;
  life: number;
  maxLife: number;
  size: number;
  color: THREE.Color;
}

export abstract class ParticleEffect {
  protected particles: Particle[] = [];
  protected geometry: THREE.BufferGeometry;
  protected material: THREE.Material;
  protected points: THREE.Points | THREE.Mesh;
  protected maxParticles: number;
  protected isActive: boolean = true;

  constructor(maxParticles: number) {
    this.maxParticles = maxParticles;
  }

  abstract update(dt: number): void;

  protected updateGeometryAttributes() {
    const posAttr = this.geometry.getAttribute('position');
    const colorAttr = this.geometry.getAttribute('color');
    const sizeAttr = this.geometry.getAttribute('size');

    const positions = posAttr.array as Float32Array;
    const colors = colorAttr?.array as Float32Array;
    const sizes = sizeAttr?.array as Float32Array;

    for (let i = 0; i < this.particles.length; i++) {
      const p = this.particles[i];
      positions[i * 3] = p.position.x;
      positions[i * 3 + 1] = p.position.y;
      positions[i * 3 + 2] = p.position.z;

      if (colors) {
        colors[i * 3] = p.color.r;
        colors[i * 3 + 1] = p.color.g;
        colors[i * 3 + 2] = p.color.b;
      }

      if (sizes) {
        sizes[i] = p.size * (p.life / p.maxLife);
      }
    }

    posAttr.needsUpdate = true;
    if (colorAttr) colorAttr.needsUpdate = true;
    if (sizeAttr) sizeAttr.needsUpdate = true;
  }

  addToScene(scene: THREE.Scene) {
    scene.add(this.points);
  }

  removeFromScene(scene: THREE.Scene) {
    scene.remove(this.points);
  }

  dispose() {
    this.geometry.dispose();
    if (this.material instanceof THREE.Material) {
      this.material.dispose();
    }
  }

  isAlive(): boolean {
    return this.particles.length > 0;
  }
}
```

---

## Thruster Exhaust Effect

Directional particle stream with momentum-based physics.

```typescript
export class ThrusterExhaust extends ParticleEffect {
  private direction: THREE.Vector3;
  private emissionRate: number;
  private emissionCounter: number = 0;

  constructor(
    position: THREE.Vector3,
    direction: THREE.Vector3,
    intensity: number = 1.0
  ) {
    super(Math.floor(1000 * intensity));
    this.direction = direction.normalize();
    this.emissionRate = 100 * intensity;

    // Setup geometry
    this.geometry = new THREE.BufferGeometry();
    const positions = new Float32Array(this.maxParticles * 3);
    const colors = new Float32Array(this.maxParticles * 3);
    const sizes = new Float32Array(this.maxParticles);

    this.geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    this.geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
    this.geometry.setAttribute('size', new THREE.BufferAttribute(sizes, 1));

    // Setup material
    this.material = new THREE.PointsMaterial({
      size: 0.5,
      transparent: true,
      opacity: 0.8,
      sizeAttenuation: true,
      vertexColors: true
    });

    this.points = new THREE.Points(this.geometry, this.material);
    this.points.position.copy(position);
  }

  update(dt: number) {
    // Emit new particles
    this.emissionCounter += this.emissionRate * dt;
    while (this.emissionCounter >= 1 && this.particles.length < this.maxParticles) {
      this.emitParticle();
      this.emissionCounter -= 1;
    }

    // Update existing particles
    for (let i = this.particles.length - 1; i >= 0; i--) {
      const p = this.particles[i];
      p.life -= dt;

      if (p.life <= 0) {
        this.particles.splice(i, 1);
        continue;
      }

      // Physics
      p.velocity.add(p.acceleration.clone().multiplyScalar(dt));
      p.position.add(p.velocity.clone().multiplyScalar(dt));

      // Drag
      p.velocity.multiplyScalar(0.95);

      // Fade color
      const alpha = p.life / p.maxLife;
      p.color.setScalar(Math.max(0.3, alpha));
      p.size *= 0.98;
    }

    this.updateGeometryAttributes();
  }

  private emitParticle() {
    const spread = 0.5;
    const speed = 5.0;

    const p: Particle = {
      position: new THREE.Vector3(
        (Math.random() - 0.5) * spread,
        (Math.random() - 0.5) * spread,
        (Math.random() - 0.5) * spread
      ),
      velocity: this.direction.clone().multiplyScalar(speed).addScaledVector(
        new THREE.Vector3(
          (Math.random() - 0.5) * 2,
          (Math.random() - 0.5) * 2,
          (Math.random() - 0.5) * 2
        ),
        0.5
      ),
      acceleration: new THREE.Vector3(0, 0, 0),
      life: 1.0,
      maxLife: 1.0,
      size: 0.3 + Math.random() * 0.2,
      color: new THREE.Color().setHSL(0.05 + Math.random() * 0.1, 0.8, 0.6)
    };

    this.particles.push(p);
  }
}
```

---

## Spark Shower Effect

Radial burst of bright sparks with gravity and friction.

```typescript
export class SparkShower extends ParticleEffect {
  private burstForce: number;

  constructor(position: THREE.Vector3, burstForce: number = 3.0) {
    super(300);
    this.burstForce = burstForce;

    this.geometry = new THREE.BufferGeometry();
    const positions = new Float32Array(this.maxParticles * 3);
    const colors = new Float32Array(this.maxParticles * 3);
    const sizes = new Float32Array(this.maxParticles);

    this.geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    this.geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
    this.geometry.setAttribute('size', new THREE.BufferAttribute(sizes, 1));

    this.material = new THREE.PointsMaterial({
      size: 0.4,
      sizeAttenuation: true,
      transparent: true,
      opacity: 1.0,
      vertexColors: true
    });

    this.points = new THREE.Points(this.geometry, this.material);
    this.points.position.copy(position);

    // Create burst of particles
    for (let i = 0; i < this.maxParticles; i++) {
      this.emitSpark();
    }
  }

  update(dt: number) {
    for (let i = this.particles.length - 1; i >= 0; i--) {
      const p = this.particles[i];
      p.life -= dt;

      if (p.life <= 0) {
        this.particles.splice(i, 1);
        continue;
      }

      // Gravity
      p.acceleration.y = -9.8;
      p.velocity.add(p.acceleration.clone().multiplyScalar(dt));

      // Friction
      p.velocity.multiplyScalar(0.96);

      // Position update
      p.position.add(p.velocity.clone().multiplyScalar(dt));

      // Fade and shrink
      const alpha = p.life / p.maxLife;
      p.color.multiplyScalar(alpha);
      p.size = Math.max(0.05, p.size * 0.99);
    }

    this.updateGeometryAttributes();
  }

  private emitSpark() {
    const phi = Math.random() * Math.PI * 2;
    const theta = Math.acos(Math.random() * 2 - 1);

    const p: Particle = {
      position: new THREE.Vector3(0, 0, 0),
      velocity: new THREE.Vector3(
        Math.sin(theta) * Math.cos(phi) * this.burstForce,
        Math.sin(theta) * Math.sin(phi) * this.burstForce,
        Math.cos(theta) * this.burstForce
      ),
      acceleration: new THREE.Vector3(0, 0, 0),
      life: 1.0 + Math.random() * 0.5,
      maxLife: 1.5,
      size: 0.2 + Math.random() * 0.1,
      color: new THREE.Color().setHSL(0.08 + Math.random() * 0.05, 1.0, 0.7)
    };

    this.particles.push(p);
  }
}
```

---

## Explosion with Shockwave

Dramatic explosion with expanding particle shell and shock effect.

```typescript
export class Explosion extends ParticleEffect {
  private shockwaveMesh: THREE.Mesh | null = null;
  private time: number = 0;
  private totalDuration: number = 3.0;

  constructor(position: THREE.Vector3, intensity: number = 1.0) {
    super(Math.floor(1000 * intensity));

    this.geometry = new THREE.BufferGeometry();
    const positions = new Float32Array(this.maxParticles * 3);
    const colors = new Float32Array(this.maxParticles * 3);
    const sizes = new Float32Array(this.maxParticles);

    this.geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    this.geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
    this.geometry.setAttribute('size', new THREE.BufferAttribute(sizes, 1));

    this.material = new THREE.PointsMaterial({
      size: 1.0,
      sizeAttenuation: true,
      transparent: true,
      vertexColors: true
    });

    this.points = new THREE.Points(this.geometry, this.material);
    this.points.position.copy(position);

    // Create shockwave mesh
    const shockGeom = new THREE.IcosahedronGeometry(1, 4);
    const shockMat = new THREE.MeshBasicMaterial({
      color: 0xffff00,
      transparent: true,
      opacity: 0.5,
      wireframe: false
    });
    this.shockwaveMesh = new THREE.Mesh(shockGeom, shockMat);
    this.shockwaveMesh.position.copy(position);

    // Emit explosion particles
    for (let i = 0; i < this.maxParticles; i++) {
      this.emitExplosionParticle();
    }
  }

  update(dt: number) {
    this.time += dt;

    // Update shockwave
    if (this.shockwaveMesh) {
      const expansionFactor = Math.min(this.time / 0.5, 1.0);
      this.shockwaveMesh.scale.setScalar(1.0 + expansionFactor * 5.0);

      const opacity = Math.max(0, 1.0 - this.time / 0.5);
      (this.shockwaveMesh.material as THREE.Material).opacity = opacity * 0.5;
    }

    // Update particles
    for (let i = this.particles.length - 1; i >= 0; i--) {
      const p = this.particles[i];
      p.life -= dt;

      if (p.life <= 0) {
        this.particles.splice(i, 1);
        continue;
      }

      // Drag and gravity
      p.velocity.multiplyScalar(0.97);
      p.velocity.y -= 0.1;

      p.position.add(p.velocity.clone().multiplyScalar(dt));

      // Fade
      const alpha = p.life / p.maxLife;
      p.color.multiplyScalar(alpha * 0.8);
      p.size *= 0.98;
    }

    this.updateGeometryAttributes();
  }

  private emitExplosionParticle() {
    const phi = Math.random() * Math.PI * 2;
    const theta = Math.acos(Math.random() * 2 - 1);
    const speed = 3.0 + Math.random() * 4.0;

    const p: Particle = {
      position: new THREE.Vector3(0, 0, 0),
      velocity: new THREE.Vector3(
        Math.sin(theta) * Math.cos(phi) * speed,
        Math.sin(theta) * Math.sin(phi) * speed,
        Math.cos(theta) * speed
      ),
      acceleration: new THREE.Vector3(0, 0, 0),
      life: 2.0 + Math.random(),
      maxLife: 3.0,
      size: 0.5 + Math.random() * 1.5,
      color: new THREE.Color().setHSL(0.05 + Math.random() * 0.1, 1.0, 0.7)
    };

    this.particles.push(p);
  }

  addToScene(scene: THREE.Scene) {
    super.addToScene(scene);
    if (this.shockwaveMesh) {
      scene.add(this.shockwaveMesh);
    }
  }

  removeFromScene(scene: THREE.Scene) {
    super.removeFromScene(scene);
    if (this.shockwaveMesh) {
      scene.remove(this.shockwaveMesh);
    }
  }

  isAlive(): boolean {
    return this.time < this.totalDuration && super.isAlive();
  }
}
```

---

## Energy Beam

Glowing directed beam with pulsing intensity.

```typescript
export class EnergyBeam {
  private mesh: THREE.Mesh;
  private light: THREE.PointLight;
  private startPos: THREE.Vector3;
  private endPos: THREE.Vector3;
  private time: number = 0;

  constructor(
    startPos: THREE.Vector3,
    endPos: THREE.Vector3,
    color: THREE.Color = new THREE.Color(0x00ffff),
    thickness: number = 0.3
  ) {
    this.startPos = startPos.clone();
    this.endPos = endPos.clone();

    const direction = this.endPos.clone().sub(this.startPos);
    const length = direction.length();

    // Create beam mesh
    const geometry = new THREE.CylinderGeometry(thickness, thickness, length, 8);
    const material = new THREE.MeshBasicMaterial({
      color: color,
      transparent: true,
      emissive: color,
      emissiveIntensity: 1.0
    });

    this.mesh = new THREE.Mesh(geometry, material);
    this.mesh.position.copy(startPos).add(direction.clone().normalize().multiplyScalar(length * 0.5));
    this.mesh.lookAt(endPos);

    // Create glow light
    this.light = new THREE.PointLight(color, 1.5, 50);
    this.light.position.lerpVectors(startPos, endPos, 0.5);
  }

  update(dt: number) {
    this.time += dt;
    const pulse = Math.sin(this.time * 4) * 0.2 + 0.8;
    this.mesh.material.emissiveIntensity = pulse;
    this.light.intensity = pulse;
  }

  getMesh(): THREE.Mesh {
    return this.mesh;
  }

  getLight(): THREE.PointLight {
    return this.light;
  }

  dispose() {
    this.mesh.geometry.dispose();
    (this.mesh.material as THREE.Material).dispose();
  }
}
```

---

## Floating Dust Motes

Gentle, light-affected particles that drift and twinkle.

```typescript
export class DustMotes extends ParticleEffect {
  private wind: THREE.Vector3 = new THREE.Vector3();
  private windTime: number = 0;

  constructor(position: THREE.Vector3, area: number = 10, count: number = 500) {
    super(count);

    this.geometry = new THREE.BufferGeometry();
    const positions = new Float32Array(this.maxParticles * 3);
    const colors = new Float32Array(this.maxParticles * 3);
    const sizes = new Float32Array(this.maxParticles);

    this.geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    this.geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
    this.geometry.setAttribute('size', new THREE.BufferAttribute(sizes, 1));

    this.material = new THREE.PointsMaterial({
      size: 0.15,
      sizeAttenuation: true,
      transparent: true,
      opacity: 0.6,
      vertexColors: true,
      fog: true
    });

    this.points = new THREE.Points(this.geometry, this.material);
    this.points.position.copy(position);

    // Create static dust particles
    for (let i = 0; i < this.maxParticles; i++) {
      const p: Particle = {
        position: new THREE.Vector3(
          (Math.random() - 0.5) * area,
          (Math.random() - 0.5) * area,
          (Math.random() - 0.5) * area
        ),
        velocity: new THREE.Vector3(
          (Math.random() - 0.5) * 0.1,
          (Math.random() - 0.5) * 0.1,
          (Math.random() - 0.5) * 0.1
        ),
        acceleration: new THREE.Vector3(0, 0.01, 0), // Slight drift up
        life: Infinity,
        maxLife: 1.0,
        size: 0.05 + Math.random() * 0.1,
        color: new THREE.Color(0xffffff).multiplyScalar(0.8 + Math.random() * 0.2)
      };

      this.particles.push(p);
    }
  }

  update(dt: number) {
    this.windTime += dt;

    // Smooth wind simulation
    this.wind.set(
      Math.sin(this.windTime * 0.5) * 0.5,
      0,
      Math.cos(this.windTime * 0.3) * 0.5
    );

    for (let i = 0; i < this.particles.length; i++) {
      const p = this.particles[i];

      // Apply wind
      p.velocity.add(this.wind.clone().multiplyScalar(dt * 0.1));

      // Drag
      p.velocity.multiplyScalar(0.98);

      // Move
      p.position.add(p.velocity.clone().multiplyScalar(dt));

      // Twinkling
      p.color.multiplyScalar(0.98 + Math.random() * 0.04);
    }

    this.updateGeometryAttributes();
  }
}
```

---

## Smoke and Steam

Rising, expanding cloud with dispersion.

```typescript
export class Smoke extends ParticleEffect {
  private basePosition: THREE.Vector3;
  private riseSpeed: number;
  private buoyancy: number;

  constructor(
    position: THREE.Vector3,
    riseSpeed: number = 2.0,
    count: number = 400
  ) {
    super(count);
    this.basePosition = position.clone();
    this.riseSpeed = riseSpeed;
    this.buoyancy = 0.5;

    this.geometry = new THREE.BufferGeometry();
    const positions = new Float32Array(this.maxParticles * 3);
    const colors = new Float32Array(this.maxParticles * 3);
    const sizes = new Float32Array(this.maxParticles);

    this.geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    this.geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
    this.geometry.setAttribute('size', new THREE.BufferAttribute(sizes, 1));

    this.material = new THREE.PointsMaterial({
      size: 1.0,
      sizeAttenuation: true,
      transparent: true,
      opacity: 0.5,
      vertexColors: true
    });

    this.points = new THREE.Points(this.geometry, this.material);
    this.points.position.copy(position);
  }

  emitSmoke(dt: number) {
    const emitCount = Math.floor(50 * dt);
    for (let i = 0; i < emitCount && this.particles.length < this.maxParticles; i++) {
      const p: Particle = {
        position: new THREE.Vector3(
          (Math.random() - 0.5) * 1.5,
          (Math.random() - 0.5) * 1.0,
          (Math.random() - 0.5) * 1.5
        ),
        velocity: new THREE.Vector3(
          (Math.random() - 0.5) * 0.5,
          this.riseSpeed + Math.random() * 0.5,
          (Math.random() - 0.5) * 0.5
        ),
        acceleration: new THREE.Vector3(0, 0, 0),
        life: 3.0,
        maxLife: 3.0,
        size: 0.3 + Math.random() * 0.2,
        color: new THREE.Color(0x666666).multiplyScalar(0.8)
      };

      this.particles.push(p);
    }
  }

  update(dt: number) {
    this.emitSmoke(dt);

    for (let i = this.particles.length - 1; i >= 0; i--) {
      const p = this.particles[i];
      p.life -= dt;

      if (p.life <= 0) {
        this.particles.splice(i, 1);
        continue;
      }

      // Buoyancy
      p.velocity.y += this.buoyancy * dt;

      // Horizontal dispersion
      p.velocity.x *= 0.98;
      p.velocity.z *= 0.98;

      p.position.add(p.velocity.clone().multiplyScalar(dt));

      // Fade and grow
      const alpha = p.life / p.maxLife;
      p.color.multiplyScalar(alpha);
      p.size += dt * 0.5;
    }

    this.updateGeometryAttributes();
  }
}
```

---

## Volumetric Fog (Raymarched)

Post-processing volumetric fog effect.

```typescript
export function createVolumetricFogPass(
  scene: THREE.Scene,
  camera: THREE.PerspectiveCamera
): ShaderPass {
  const fogShader = {
    uniforms: {
      tDiffuse: { value: null },
      fogColor: { value: new THREE.Color(0x8899cc) },
      fogDensity: { value: 0.005 },
      fogNear: { value: 0.1 },
      fogFar: { value: 100.0 }
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
      uniform vec3 fogColor;
      uniform float fogDensity;
      uniform float fogNear;
      uniform float fogFar;
      varying vec2 vUv;

      // Simple depth fog (use depth texture for better results)
      void main() {
        vec4 color = texture2D(tDiffuse, vUv);
        float depth = length(vUv - 0.5) * fogFar; // Simplified depth

        float fogFactor = exp(-fogDensity * fogDensity * depth * depth);
        fogFactor = clamp(fogFactor, 0.0, 1.0);

        vec3 final = mix(fogColor, color.rgb, fogFactor);
        gl_FragColor = vec4(final, color.a);
      }
    `
  };

  return new ShaderPass(fogShader);
}

// For depth-aware volumetric fog, capture depth in an earlier pass
export function createVolumetricFogWithDepth(
  scene: THREE.Scene,
  camera: THREE.PerspectiveCamera,
  depthTexture: THREE.Texture
): ShaderPass {
  const fogShader = {
    uniforms: {
      tDiffuse: { value: null },
      tDepth: { value: depthTexture },
      fogColor: { value: new THREE.Color(0x8899cc) },
      fogDensity: { value: 0.02 },
      cameraFar: { value: camera.far }
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

        float fogFactor = exp(-fogDensity * fogDensity * distance * distance);

        vec3 final = mix(fogColor, color.rgb, fogFactor);
        gl_FragColor = vec4(final, color.a);
      }
    `
  };

  return new ShaderPass(fogShader);
}
```

---

## God Rays / Volumetric Light Shafts

Light shafts from bright light source.

```typescript
export function createGodRaysPass(): ShaderPass {
  const godRaysShader = {
    uniforms: {
      tDiffuse: { value: null },
      lightPosition: { value: new THREE.Vector2(0.5, 0.5) },
      density: { value: 0.5 },
      decay: { value: 0.95 },
      weight: { value: 0.4 },
      samples: { value: 100.0 },
      exposure: { value: 0.6 }
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
      uniform vec2 lightPosition;
      uniform float density;
      uniform float decay;
      uniform float weight;
      uniform float samples;
      uniform float exposure;
      varying vec2 vUv;

      void main() {
        vec2 texCoord = vUv;
        vec2 deltaCoord = (lightPosition - texCoord);
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

        color *= exposure;
        gl_FragColor = vec4(color, 1.0);
      }
    `
  };

  return new ShaderPass(godRaysShader);
}
```

---

## Atmospheric Scattering (Sky)

Realistic sky with Rayleigh and Mie scattering.

```typescript
export function createAtmosphericSkyMaterial(
  sunPosition: THREE.Vector3
): THREE.ShaderMaterial {
  return new THREE.ShaderMaterial({
    uniforms: {
      sunPosition: { value: sunPosition.normalize() },
      turbidity: { value: 10.0 },
      rayleigh: { value: 2.0 },
      mieCoefficient: { value: 0.005 },
      mieDirectionalG: { value: 0.8 }
    },
    vertexShader: `
      varying vec3 vWorldPosition;

      void main() {
        vec4 worldPos = modelMatrix * vec4(position, 1.0);
        vWorldPosition = normalize(worldPos.xyz);
        gl_Position = projectionMatrix * viewMatrix * worldPos;
      }
    `,
    fragmentShader: `
      uniform vec3 sunPosition;
      uniform float turbidity;
      uniform float rayleigh;
      uniform float mieCoefficient;
      uniform float mieDirectionalG;
      varying vec3 vWorldPosition;

      const float pi = 3.14159265359;
      const float e = 2.71828182845904523536;

      float rayleighPhase(float cosTheta) {
        return (3.0 / (16.0 * pi)) * (1.0 + pow(cosTheta, 2.0));
      }

      float miePhase(float cosTheta) {
        float g = mieDirectionalG;
        float g2 = g * g;
        float cosTheta2 = cosTheta * cosTheta;

        return (3.0 / (8.0 * pi)) * ((1.0 - g2) * (1.0 + cosTheta2)) /
               (pow(1.0 + g2 - 2.0 * g * cosTheta, 1.5) * (2.0 + g2));
      }

      void main() {
        vec3 direction = normalize(vWorldPosition);
        float sunfade = clamp(1.0 - length(sunPosition - direction), 0.0, 1.0);

        float cosTheta = dot(direction, sunPosition);

        vec3 rayleighColor = vec3(
          pow(0.65, 2.0),
          pow(0.68, 2.0),
          pow(0.7, 2.0)
        ) * rayleigh;

        vec3 mieColor = vec3(1.0) * mieCoefficient;

        float rayleighScatter = rayleighPhase(cosTheta);
        float mieScatter = miePhase(cosTheta);

        vec3 scatter = (rayleighColor * rayleighScatter + mieColor * mieScatter) * (1.0 - turbidity * 0.01);

        vec3 sunColor = mix(vec3(1.0), vec3(1.0, 0.6, 0.2), sunfade * 0.5);
        scatter += sunColor * sunfade * mieScatter;

        gl_FragColor = vec4(scatter, 1.0);
      }
    `
  });
}
```

---

## Rain Effect

Falling rain particles with wind and splashing.

```typescript
export class Rain extends ParticleEffect {
  private area: THREE.Vector3;
  private windForce: THREE.Vector3 = new THREE.Vector3();

  constructor(position: THREE.Vector3, width: number = 100, height: number = 50, count: number = 3000) {
    super(count);
    this.area = new THREE.Vector3(width, height, width);

    this.geometry = new THREE.BufferGeometry();
    const positions = new Float32Array(this.maxParticles * 3);

    this.geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));

    this.material = new THREE.LineBasicMaterial({
      color: 0xccccff,
      transparent: true,
      opacity: 0.6
    });

    this.points = new THREE.Points(this.geometry, this.material);
    this.points.position.copy(position);

    // Create rain streaks
    for (let i = 0; i < this.maxParticles; i++) {
      const p: Particle = {
        position: new THREE.Vector3(
          (Math.random() - 0.5) * this.area.x,
          (Math.random() - 0.5) * this.area.y,
          (Math.random() - 0.5) * this.area.z
        ),
        velocity: new THREE.Vector3(0, -8.0 - Math.random() * 3.0, 0),
        acceleration: new THREE.Vector3(0, 0, 0),
        life: Infinity,
        maxLife: 1.0,
        size: 0.2,
        color: new THREE.Color(0xccccff)
      };

      this.particles.push(p);
    }
  }

  setWind(windVector: THREE.Vector3) {
    this.windForce.copy(windVector);
  }

  update(dt: number) {
    for (let i = 0; i < this.particles.length; i++) {
      const p = this.particles[i];

      // Wind force
      p.velocity.x += this.windForce.x * 0.01;
      p.velocity.z += this.windForce.z * 0.01;

      // Move
      p.position.add(p.velocity.clone().multiplyScalar(dt));

      // Respawn if below
      if (p.position.y < -(this.area.y / 2)) {
        p.position.y = this.area.y / 2;
        p.position.x = (Math.random() - 0.5) * this.area.x;
        p.position.z = (Math.random() - 0.5) * this.area.z;
      }

      // Wrap horizontally
      if (Math.abs(p.position.x) > this.area.x / 2) {
        p.position.x *= -1;
      }
      if (Math.abs(p.position.z) > this.area.z / 2) {
        p.position.z *= -1;
      }
    }

    this.updateGeometryAttributes();
  }
}
```

---

## Snow Effect

Gentle, drifting snow with wind and settling behavior.

```typescript
export class Snow extends ParticleEffect {
  private area: THREE.Vector3;
  private windTime: number = 0;

  constructor(position: THREE.Vector3, width: number = 100, height: number = 50, count: number = 2000) {
    super(count);
    this.area = new THREE.Vector3(width, height, width);

    this.geometry = new THREE.BufferGeometry();
    const positions = new Float32Array(this.maxParticles * 3);
    const sizes = new Float32Array(this.maxParticles);

    this.geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    this.geometry.setAttribute('size', new THREE.BufferAttribute(sizes, 1));

    this.material = new THREE.PointsMaterial({
      size: 0.3,
      sizeAttenuation: true,
      transparent: true,
      opacity: 0.8,
      color: 0xffffff
    });

    this.points = new THREE.Points(this.geometry, this.material);
    this.points.position.copy(position);

    for (let i = 0; i < this.maxParticles; i++) {
      const p: Particle = {
        position: new THREE.Vector3(
          (Math.random() - 0.5) * this.area.x,
          Math.random() * this.area.y,
          (Math.random() - 0.5) * this.area.z
        ),
        velocity: new THREE.Vector3(0, -0.5 - Math.random() * 0.5, 0),
        acceleration: new THREE.Vector3(0, 0, 0),
        life: Infinity,
        maxLife: 1.0,
        size: 0.2 + Math.random() * 0.2,
        color: new THREE.Color(0xffffff)
      };

      this.particles.push(p);
    }
  }

  update(dt: number) {
    this.windTime += dt;

    for (let i = 0; i < this.particles.length; i++) {
      const p = this.particles[i];

      // Wind effect
      const windX = Math.sin(this.windTime * 0.3) * 1.0;
      const windZ = Math.cos(this.windTime * 0.2) * 0.5;
      p.velocity.x += windX * dt * 0.01;
      p.velocity.z += windZ * dt * 0.01;

      // Gentle falling
      p.velocity.y -= 0.2 * dt;

      p.position.add(p.velocity.clone().multiplyScalar(dt));

      // Respawn
      if (p.position.y < -(this.area.y / 2)) {
        p.position.y = this.area.y / 2;
        p.position.x = (Math.random() - 0.5) * this.area.x;
        p.position.z = (Math.random() - 0.5) * this.area.z;
        p.velocity.set(0, -0.5 - Math.random() * 0.5, 0);
      }

      // Wrap horizontally
      if (Math.abs(p.position.x) > this.area.x / 2) {
        p.position.x *= -1;
      }
      if (Math.abs(p.position.z) > this.area.z / 2) {
        p.position.z *= -1;
      }
    }

    this.updateGeometryAttributes();
  }
}
```

---

## Nebula Background

Procedural nebula using simple particle clouds.

```typescript
export class NebulaBG extends ParticleEffect {
  constructor(position: THREE.Vector3, scale: number = 50) {
    super(2000);

    this.geometry = new THREE.BufferGeometry();
    const positions = new Float32Array(this.maxParticles * 3);
    const colors = new Float32Array(this.maxParticles * 3);
    const sizes = new Float32Array(this.maxParticles);

    this.geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    this.geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
    this.geometry.setAttribute('size', new THREE.BufferAttribute(sizes, 1));

    this.material = new THREE.PointsMaterial({
      size: 2.0,
      sizeAttenuation: false,
      transparent: true,
      opacity: 0.3,
      vertexColors: true
    });

    this.points = new THREE.Points(this.geometry, this.material);
    this.points.position.copy(position);

    // Create nebula clouds
    for (let i = 0; i < this.maxParticles; i++) {
      const p: Particle = {
        position: new THREE.Vector3(
          (Math.random() - 0.5) * scale,
          (Math.random() - 0.5) * scale,
          (Math.random() - 0.5) * scale
        ),
        velocity: new THREE.Vector3(0, 0, 0),
        acceleration: new THREE.Vector3(0, 0, 0),
        life: Infinity,
        maxLife: 1.0,
        size: 5.0 + Math.random() * 10.0,
        color: new THREE.Color().setHSL(
          0.6 + Math.random() * 0.3,
          0.5 + Math.random() * 0.5,
          0.3 + Math.random() * 0.3
        )
      };

      this.particles.push(p);
    }
  }

  update(dt: number) {
    // Static nebula background
    // Could add slow drift if desired
  }
}
```

---

## Starfield with Parallax

Background stars with depth-based parallax movement.

```typescript
export class ParallaxStarfield {
  private layers: THREE.Points[] = [];
  private parallaxSpeeds: number[] = [0.2, 0.5, 1.0];

  constructor(position: THREE.Vector3, scale: number = 200) {
    const layerCounts = [200, 400, 800];

    for (let layer = 0; layer < 3; layer++) {
      const geometry = new THREE.BufferGeometry();
      const positions = new Float32Array(layerCounts[layer] * 3);
      const colors = new Float32Array(layerCounts[layer] * 3);
      const sizes = new Float32Array(layerCounts[layer]);

      for (let i = 0; i < layerCounts[layer]; i++) {
        positions[i * 3] = (Math.random() - 0.5) * scale;
        positions[i * 3 + 1] = (Math.random() - 0.5) * scale;
        positions[i * 3 + 2] = (Math.random() - 0.5) * scale;

        const brightness = Math.random();
        colors[i * 3] = brightness;
        colors[i * 3 + 1] = brightness;
        colors[i * 3 + 2] = brightness;

        sizes[i] = (0.5 + Math.random()) * (layer + 1) * 0.3;
      }

      geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
      geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
      geometry.setAttribute('size', new THREE.BufferAttribute(sizes, 1));

      const material = new THREE.PointsMaterial({
        size: 1.0,
        vertexColors: true,
        transparent: true,
        opacity: 0.8 - layer * 0.1
      });

      const points = new THREE.Points(geometry, material);
      points.position.copy(position);
      this.layers.push(points);
    }
  }

  updateCameraPosition(cameraPos: THREE.Vector3) {
    for (let i = 0; i < this.layers.length; i++) {
      const layer = this.layers[i];
      const speed = this.parallaxSpeeds[i];
      layer.position.copy(cameraPos).multiplyScalar(speed);
    }
  }

  addToScene(scene: THREE.Scene) {
    for (const layer of this.layers) {
      scene.add(layer);
    }
  }

  removeFromScene(scene: THREE.Scene) {
    for (const layer of this.layers) {
      scene.remove(layer);
    }
  }
}
```
