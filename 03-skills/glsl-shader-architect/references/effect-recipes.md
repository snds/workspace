# Shader Effect Recipes for Three.js

Complete, production-ready effect implementations. Each is a function that returns a configured ShaderMaterial ready to use.

---

## 1. Dissolve / Disintegration Effect

Gradually disintegrate objects with noise-based erosion:

```typescript
function createDissolveShader(dissolveAmount: number = 0.0): THREE.ShaderMaterial {
  return new THREE.ShaderMaterial({
    uniforms: {
      dissolveAmount: { value: dissolveAmount },
      dissolveTex: { value: new THREE.TextureLoader().load('noise.jpg') },
      color: { value: new THREE.Color(0xffffff) },
      emissive: { value: new THREE.Color(0xff6600) },
    },
    transparent: true,
    vertexShader: `
      varying vec2 vUv;
      varying vec3 vPosition;
      
      void main() {
        vUv = uv;
        vPosition = position;
        gl_Position = projectionMatrix * viewMatrix * modelMatrix * vec4(position, 1.0);
      }
    `,
    fragmentShader: `
      uniform float dissolveAmount;
      uniform sampler2D dissolveTex;
      uniform vec3 color;
      uniform vec3 emissive;
      
      varying vec2 vUv;
      varying vec3 vPosition;
      
      void main() {
        // Sample noise texture
        vec4 dissolveSample = texture2D(dissolveTex, vUv);
        float noise = dissolveSample.r;
        
        // Threshold based on dissolveAmount
        float threshold = noise - dissolveAmount;
        
        // Discard fragments below threshold
        if (threshold < 0.0) discard;
        
        // Soft edge glow
        float edge = smoothstep(-0.1, 0.1, threshold);
        
        // Mix base color with emissive glow at edges
        vec3 finalColor = mix(emissive, color, edge);
        float alpha = edge;
        
        gl_FragColor = vec4(finalColor, alpha);
      }
    `,
  });
}
```

**Usage:**
```typescript
const shader = createDissolveShader();
// Animate: shader.uniforms.dissolveAmount.value += 0.01;
```

---

## 2. Hologram / Scan Line Effect

Classic sci-fi hologram with animated scan lines:

```typescript
function createHologramShader(scanIntensity: number = 0.5): THREE.ShaderMaterial {
  return new THREE.ShaderMaterial({
    uniforms: {
      time: { value: 0 },
      scanIntensity: { value: scanIntensity },
      glitchAmount: { value: 0.0 },
      baseColor: { value: new THREE.Color(0x00ff88) },
    },
    transparent: true,
    vertexShader: `
      varying vec2 vUv;
      varying vec3 vNormal;
      
      void main() {
        vUv = uv;
        vNormal = normalize(normalMatrix * normal);
        gl_Position = projectionMatrix * viewMatrix * modelMatrix * vec4(position, 1.0);
      }
    `,
    fragmentShader: `
      uniform float time;
      uniform float scanIntensity;
      uniform float glitchAmount;
      uniform vec3 baseColor;
      
      varying vec2 vUv;
      varying vec3 vNormal;
      
      // Pseudo-random
      float hash(float n) {
        return fract(sin(n) * 43758.5453);
      }
      
      void main() {
        vec2 uv = vUv;
        
        // Scan lines
        float scanLine = sin(uv.y * 200.0 - time * 5.0) * 0.5 + 0.5;
        scanLine = mix(1.0, scanLine, scanIntensity);
        
        // Glitch effect
        float glitch = hash(time) * glitchAmount;
        uv.x += (hash(uv.y + time) - 0.5) * glitch;
        
        // Fresnel rim
        vec3 viewDir = normalize(vec3(0.0, 0.0, 1.0));
        float fresnel = 1.0 - abs(dot(vNormal, viewDir));
        fresnel = pow(fresnel, 2.0);
        
        // Combine effects
        vec3 color = baseColor * scanLine;
        float alpha = fresnel * 0.8 + scanLine * 0.2;
        
        gl_FragColor = vec4(color, alpha);
      }
    `,
  });
}
```

---

## 3. Force Field / Energy Shield

Animated shield with refraction and glow:

```typescript
function createForceFieldShader(): THREE.ShaderMaterial {
  return new THREE.ShaderMaterial({
    uniforms: {
      time: { value: 0 },
      shieldColor: { value: new THREE.Color(0x0099ff) },
      intensity: { value: 0.8 },
    },
    transparent: true,
    side: THREE.DoubleSide,
    blending: THREE.AdditiveBlending,
    vertexShader: `
      varying vec3 vNormal;
      varying vec3 vPosition;
      
      void main() {
        vNormal = normalize(normalMatrix * normal);
        vPosition = position;
        gl_Position = projectionMatrix * viewMatrix * modelMatrix * vec4(position, 1.0);
      }
    `,
    fragmentShader: `
      uniform float time;
      uniform vec3 shieldColor;
      uniform float intensity;
      
      varying vec3 vNormal;
      varying vec3 vPosition;
      
      // Simple noise
      float noise(vec3 p) {
        return fract(sin(dot(p, vec3(12.9, 78.2, 45.1))) * 43758.5) * 2.0 - 1.0;
      }
      
      void main() {
        // Animated waves on surface
        float wave1 = sin(vPosition.y * 5.0 + time) * 0.5 + 0.5;
        float wave2 = cos(vPosition.z * 3.0 - time * 1.5) * 0.5 + 0.5;
        float waves = wave1 * wave2;
        
        // Fresnel effect
        vec3 viewDir = normalize(vec3(0.0, 0.0, 1.0));
        float fresnel = 1.0 - abs(dot(vNormal, viewDir));
        fresnel = pow(fresnel, 1.5);
        
        // Combine waves and fresnel
        float alpha = (fresnel + waves * 0.3) * intensity;
        vec3 color = shieldColor * (1.0 + waves);
        
        gl_FragColor = vec4(color, alpha);
      }
    `,
  });
}
```

---

## 4. Heat Distortion / Refraction

Wavy heat shimmer effect:

```typescript
function createHeatDistortionShader(): THREE.ShaderMaterial {
  return new THREE.ShaderMaterial({
    uniforms: {
      time: { value: 0 },
      distortionStrength: { value: 0.02 },
      heatColor: { value: new THREE.Color(0xff3300) },
    },
    vertexShader: `
      varying vec2 vUv;
      varying vec3 vPosition;
      
      void main() {
        vUv = uv;
        vPosition = position;
        gl_Position = projectionMatrix * viewMatrix * modelMatrix * vec4(position, 1.0);
      }
    `,
    fragmentShader: `
      uniform float time;
      uniform float distortionStrength;
      uniform vec3 heatColor;
      
      varying vec2 vUv;
      varying vec3 vPosition;
      
      // Simple wave distortion
      float wave(vec2 uv) {
        return sin(uv.x * 10.0 + time * 3.0) * 
               cos(uv.y * 10.0 - time * 2.0);
      }
      
      void main() {
        // Create distortion
        vec2 distortion = vec2(
          wave(vUv + time * 0.1) * distortionStrength,
          wave(vUv + time * 0.15 + 10.0) * distortionStrength
        );
        
        vec2 distortedUv = vUv + distortion;
        
        // Heat intensity based on distance
        float heatIntensity = length(vPosition) * 0.5;
        heatIntensity = mod(heatIntensity + time, 1.0);
        
        // Wavy intensity
        float intensity = sin(vPosition.y * 20.0 + time * 5.0) * 0.5 + 0.5;
        
        vec3 color = mix(vec3(1.0), heatColor, intensity);
        
        gl_FragColor = vec4(color, 0.6);
      }
    `,
  });
}
```

---

## 5. Fresnel Rim Glow

Bright glow at silhouette edges:

```typescript
function createFresnelRimShader(rimColor: THREE.Color = new THREE.Color(0xff00ff)): THREE.ShaderMaterial {
  return new THREE.ShaderMaterial({
    uniforms: {
      rimColor: { value: rimColor },
      rimPower: { value: 2.0 },
      rimIntensity: { value: 1.0 },
      baseColor: { value: new THREE.Color(0x444444) },
    },
    vertexShader: `
      varying vec3 vNormal;
      varying vec3 vPosition;
      
      void main() {
        vNormal = normalize(normalMatrix * normal);
        vPosition = vec3(modelMatrix * vec4(position, 1.0));
        gl_Position = projectionMatrix * viewMatrix * modelMatrix * vec4(position, 1.0);
      }
    `,
    fragmentShader: `
      uniform vec3 rimColor;
      uniform float rimPower;
      uniform float rimIntensity;
      uniform vec3 baseColor;
      
      uniform vec3 cameraPosition;
      
      varying vec3 vNormal;
      varying vec3 vPosition;
      
      void main() {
        vec3 viewDir = normalize(cameraPosition - vPosition);
        vec3 normal = normalize(vNormal);
        
        // Fresnel: bright at grazing angles
        float fresnel = 1.0 - max(0.0, dot(normal, viewDir));
        fresnel = pow(fresnel, rimPower);
        
        vec3 rim = rimColor * fresnel * rimIntensity;
        vec3 color = baseColor + rim;
        
        gl_FragColor = vec4(color, 1.0);
      }
    `,
  });
}
```

---

## 6. Procedural Rust / Weathering

Organic rust and corrosion patterns:

```typescript
function createRustShader(): THREE.ShaderMaterial {
  return new THREE.ShaderMaterial({
    uniforms: {
      rustAmount: { value: 0.5 },
      scale: { value: 1.0 },
    },
    vertexShader: `
      varying vec3 vPosition;
      varying vec2 vUv;
      
      void main() {
        vPosition = position;
        vUv = uv;
        gl_Position = projectionMatrix * viewMatrix * modelMatrix * vec4(position, 1.0);
      }
    `,
    fragmentShader: `
      uniform float rustAmount;
      uniform float scale;
      
      varying vec3 vPosition;
      varying vec2 vUv;
      
      // Simple noise
      float noise(vec3 p) {
        return fract(sin(dot(p, vec3(12.9, 78.2, 45.1))) * 43758.5);
      }
      
      // fBm approximation
      float fbm(vec3 p) {
        float value = 0.0;
        value += noise(p) * 0.5;
        value += noise(p * 2.0) * 0.25;
        value += noise(p * 4.0) * 0.125;
        return value;
      }
      
      void main() {
        vec3 pos = vPosition * scale;
        
        // Multiple noise layers
        float base = fbm(pos);
        float detail = fbm(pos * 8.0);
        float cracks = abs(sin(pos.x * 100.0) * sin(pos.z * 100.0));
        
        // Combine for rust effect
        float rust = mix(base, detail, 0.5);
        rust = mix(rust, cracks, 0.2);
        
        // Color gradient
        vec3 rustColor = vec3(0.8, 0.4, 0.2) * (rust + rustAmount) +
                         vec3(0.3, 0.1, 0.05);
        
        gl_FragColor = vec4(rustColor, 1.0);
      }
    `,
  });
}
```

---

## 7. Procedural Hex Grid

Animated hexagonal grid pattern:

```typescript
function createHexGridShader(): THREE.ShaderMaterial {
  return new THREE.ShaderMaterial({
    uniforms: {
      gridColor: { value: new THREE.Color(0x00ff00) },
      gridLineWidth: { value: 0.02 },
      time: { value: 0 },
    },
    vertexShader: `
      varying vec2 vUv;
      
      void main() {
        vUv = uv;
        gl_Position = projectionMatrix * viewMatrix * modelMatrix * vec4(position, 1.0);
      }
    `,
    fragmentShader: `
      uniform vec3 gridColor;
      uniform float gridLineWidth;
      uniform float time;
      
      varying vec2 vUv;
      
      float hexGrid(vec2 p) {
        const float sqrt3 = 1.732050808;
        const vec2 hex1 = vec2(1.0, sqrt3);
        const vec2 hex2 = vec2(2.0, 0.0);
        
        vec2 q = vec2(hex1.x * p.x + hex2.x * p.y,
                      hex1.y * p.x - hex2.x * p.y);
        q /= (hex1.x + hex2.x);
        
        vec2 pi = round(q);
        vec2 pf = fract(q);
        
        float d = length(pf - 0.5);
        return step(0.3 + gridLineWidth, d);
      }
      
      void main() {
        vec2 uv = vUv * 10.0;
        
        // Animated pulse
        float pulse = sin(time) * 0.5 + 0.5;
        
        float hex = hexGrid(uv);
        vec3 color = mix(gridColor, vec3(0.0), hex);
        color *= pulse;
        
        gl_FragColor = vec4(color, 1.0);
      }
    `,
  });
}
```

---

## 8. Parallax Mapping

Fake depth with height-based offset:

```typescript
function createParallaxShader(heightMap: THREE.Texture): THREE.ShaderMaterial {
  return new THREE.ShaderMaterial({
    uniforms: {
      heightMap: { value: heightMap },
      heightScale: { value: 0.1 },
      baseColor: { value: new THREE.Color(0xcccccc) },
    },
    vertexShader: `
      varying vec2 vUv;
      varying vec3 vViewDir;
      varying mat3 vTBN;
      
      void main() {
        vUv = uv;
        vViewDir = vec3(0.0, 0.0, 1.0);  // View direction (simplified)
        
        // Simplified TBN
        vec3 T = normalize(vec3(1.0, 0.0, 0.0));
        vec3 B = normalize(vec3(0.0, 1.0, 0.0));
        vec3 N = normalize(vec3(0.0, 0.0, 1.0));
        vTBN = mat3(T, B, N);
        
        gl_Position = projectionMatrix * viewMatrix * modelMatrix * vec4(position, 1.0);
      }
    `,
    fragmentShader: `
      uniform sampler2D heightMap;
      uniform float heightScale;
      uniform vec3 baseColor;
      
      varying vec2 vUv;
      varying vec3 vViewDir;
      varying mat3 vTBN;
      
      void main() {
        vec3 viewDir = normalize(vTBN * vViewDir);
        
        // Sample height
        float height = texture2D(heightMap, vUv).r;
        
        // Parallax offset
        vec2 offset = viewDir.xy * (height - 0.5) * heightScale;
        vec2 parallaxUv = vUv + offset;
        
        // Sample with parallax
        height = texture2D(heightMap, parallaxUv).r;
        
        // Add shadow based on height
        vec3 color = baseColor * (0.5 + height * 0.5);
        
        gl_FragColor = vec4(color, 1.0);
      }
    `,
  });
}
```

---

## 9. Triplanar Mapping

Texture 3D objects without UVs:

```typescript
function createTriplanarShader(textureX: THREE.Texture, textureY: THREE.Texture, textureZ: THREE.Texture): THREE.ShaderMaterial {
  return new THREE.ShaderMaterial({
    uniforms: {
      textureX: { value: textureX },
      textureY: { value: textureY },
      textureZ: { value: textureZ },
      scale: { value: 1.0 },
    },
    vertexShader: `
      varying vec3 vPosition;
      varying vec3 vNormal;
      
      void main() {
        vPosition = position;
        vNormal = normalize(normalMatrix * normal);
        gl_Position = projectionMatrix * viewMatrix * modelMatrix * vec4(position, 1.0);
      }
    `,
    fragmentShader: `
      uniform sampler2D textureX;
      uniform sampler2D textureY;
      uniform sampler2D textureZ;
      uniform float scale;
      
      varying vec3 vPosition;
      varying vec3 vNormal;
      
      void main() {
        vec3 pos = vPosition * scale;
        vec3 normal = normalize(vNormal);
        normal = abs(normal);
        
        // Sample from three directions
        vec3 colX = texture2D(textureX, pos.yz).rgb;
        vec3 colY = texture2D(textureY, pos.xz).rgb;
        vec3 colZ = texture2D(textureZ, pos.xy).rgb;
        
        // Blend by normal
        vec3 weights = normal / (normal.x + normal.y + normal.z);
        vec3 color = colX * weights.x + colY * weights.y + colZ * weights.z;
        
        gl_FragColor = vec4(color, 1.0);
      }
    `,
  });
}
```

---

## 10. Toon / Cel Shading

Stylized cartoon appearance:

```typescript
function createToonShader(outlineColor: THREE.Color = new THREE.Color(0x000000)): THREE.ShaderMaterial {
  return new THREE.ShaderMaterial({
    uniforms: {
      lightPos: { value: new THREE.Vector3(5, 5, 5) },
      outlineColor: { value: outlineColor },
      outlineWidth: { value: 0.002 },
    },
    vertexShader: `
      varying vec3 vNormal;
      varying vec3 vPosition;
      
      void main() {
        vNormal = normalize(normalMatrix * normal);
        vPosition = vec3(modelMatrix * vec4(position, 1.0));
        gl_Position = projectionMatrix * viewMatrix * modelMatrix * vec4(position, 1.0);
      }
    `,
    fragmentShader: `
      uniform vec3 lightPos;
      uniform vec3 outlineColor;
      uniform float outlineWidth;
      
      uniform vec3 cameraPosition;
      
      varying vec3 vNormal;
      varying vec3 vPosition;
      
      void main() {
        vec3 normal = normalize(vNormal);
        vec3 lightDir = normalize(lightPos - vPosition);
        
        float diffuse = dot(normal, lightDir);
        
        // Quantize to steps (cartoon effect)
        if (diffuse > 0.8) diffuse = 1.0;
        else if (diffuse > 0.4) diffuse = 0.6;
        else if (diffuse > 0.0) diffuse = 0.3;
        else diffuse = 0.1;
        
        // Outline based on viewing angle
        vec3 viewDir = normalize(cameraPosition - vPosition);
        float edge = 1.0 - abs(dot(normal, viewDir));
        float outline = step(1.0 - outlineWidth, edge);
        
        vec3 color = vec3(0.7, 0.5, 0.3) * diffuse;
        color = mix(color, outlineColor, outline);
        
        gl_FragColor = vec4(color, 1.0);
      }
    `,
  });
}
```

---

## 11. Outline / Edge Detection

Silhouette outline effect:

```typescript
function createOutlineShader(): THREE.ShaderMaterial {
  return new THREE.ShaderMaterial({
    uniforms: {
      outlineColor: { value: new THREE.Color(0x000000) },
      outlineThickness: { value: 0.01 },
    },
    side: THREE.BackSide,
    vertexShader: `
      uniform float outlineThickness;
      
      void main() {
        vec4 clipPos = projectionMatrix * viewMatrix * modelMatrix * vec4(position, 1.0);
        vec3 clipNorm = normalize(normalMatrix * normal);
        clipNorm = normalize(clipNorm);
        
        vec2 offset = normalize(clipNorm.xy) * outlineThickness;
        clipPos.xy += offset * clipPos.w;
        
        gl_Position = clipPos;
      }
    `,
    fragmentShader: `
      uniform vec3 outlineColor;
      
      void main() {
        gl_FragColor = vec4(outlineColor, 1.0);
      }
    `,
  });
}
```

---

## 12. Animated Energy Beam

Pulsing cylindrical beam effect:

```typescript
function createEnergyBeamShader(): THREE.ShaderMaterial {
  return new THREE.ShaderMaterial({
    uniforms: {
      time: { value: 0 },
      beamColor: { value: new THREE.Color(0x00ffff) },
      intensity: { value: 1.0 },
    },
    transparent: true,
    blending: THREE.AdditiveBlending,
    vertexShader: `
      varying vec3 vPosition;
      varying vec2 vUv;
      
      void main() {
        vPosition = position;
        vUv = uv;
        gl_Position = projectionMatrix * viewMatrix * modelMatrix * vec4(position, 1.0);
      }
    `,
    fragmentShader: `
      uniform float time;
      uniform vec3 beamColor;
      uniform float intensity;
      
      varying vec3 vPosition;
      varying vec2 vUv;
      
      void main() {
        // Distance from center (U direction)
        float dist = length(vUv - 0.5);
        
        // Beam width
        float beam = 1.0 - smoothstep(0.0, 0.3, dist);
        
        // Pulsing core
        float pulse = sin(vPosition.z * 10.0 - time * 5.0) * 0.5 + 0.5;
        
        // Animated streaks along beam
        float streak = sin(vUv.y * 20.0 + time * 3.0) * 0.5 + 0.5;
        
        float alpha = beam * (pulse * 0.5 + streak * 0.5) * intensity;
        
        gl_FragColor = vec4(beamColor, alpha);
      }
    `,
  });
}
```

---

## 13. Warp / Hyperspace Tunnel

Hyperdrive-style warping effect:

```typescript
function createWarpTunnelShader(): THREE.ShaderMaterial {
  return new THREE.ShaderMaterial({
    uniforms: {
      time: { value: 0 },
      warpColor: { value: new THREE.Color(0xff00ff) },
      warpAmount: { value: 1.0 },
    },
    vertexShader: `
      varying vec2 vUv;
      
      void main() {
        vUv = uv;
        gl_Position = projectionMatrix * viewMatrix * modelMatrix * vec4(position, 1.0);
      }
    `,
    fragmentShader: `
      uniform float time;
      uniform vec3 warpColor;
      uniform float warpAmount;
      
      varying vec2 vUv;
      
      void main() {
        vec2 center = vec2(0.5);
        vec2 pos = vUv - center;
        
        // Radial warp
        float angle = atan(pos.y, pos.x);
        float radius = length(pos);
        
        // Tunnel effect
        float tunnel = sin(radius * 20.0 - time * 5.0) * 0.5 + 0.5;
        
        // Spiraling stripes
        float spiral = sin(angle * 5.0 + radius * 30.0 - time * 3.0) * 0.5 + 0.5;
        
        // Combine for warp effect
        float intensity = tunnel * spiral * warpAmount;
        
        // Fade at edges
        float fade = 1.0 - smoothstep(0.0, 0.5, radius);
        
        vec3 color = warpColor * intensity;
        
        gl_FragColor = vec4(color, fade * intensity);
      }
    `,
  });
}
```

Each recipe is a standalone function returning a ready-to-use ShaderMaterial. Customize by modifying the uniform values in the ShaderMaterial constructor before using.
