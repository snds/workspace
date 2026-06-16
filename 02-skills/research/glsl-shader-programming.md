# GLSL Shader Programming for WebGL and Three.js: Comprehensive Reference

## Table of Contents

1. [GLSL Fundamentals for Three.js](#glsl-fundamentals)
2. [Vertex Shader Techniques](#vertex-shader-techniques)
3. [Fragment Shader Techniques](#fragment-shader-techniques)
4. [Lighting in Custom Shaders](#lighting-in-custom-shaders)
5. [Advanced Shader Patterns](#advanced-shader-patterns)
6. [Performance Optimization](#performance-optimization)
7. [Noise Library Reference](#noise-library-reference)
8. [Shader Resources](#shader-resources)

---

## GLSL Fundamentals for Three.js {#glsl-fundamentals}

### Data Types

GLSL provides scalar and aggregate data types essential for shader programming:

#### Scalar Types
- `float` - 32-bit floating-point number
- `int` - 32-bit signed integer
- `bool` - Boolean value (true/false)

#### Vector Types
- `vec2` - 2D vector (x, y or s, t or u, v)
- `vec3` - 3D vector (x, y, z or r, g, b)
- `vec4` - 4D vector (x, y, z, w or r, g, b, a)
- `ivec2`, `ivec3`, `ivec4` - Integer vectors
- `bvec2`, `bvec3`, `bvec4` - Boolean vectors

#### Matrix Types
- `mat2` - 2x2 matrix
- `mat3` - 3x3 matrix
- `mat4` - 4x4 matrix

**Important Note on Matrix Layout:**
OpenGL/WebGL stores matrices in **column-major format**. This means `M[2]` refers to column 2 (not row 2), and `M[2][1]` is the element at column 2, row 1.

#### Sampler Types
- `sampler2D` - 2D texture sampler
- `samplerCube` - Cubemap sampler
- `sampler3D` - 3D texture sampler

### Variable Qualifiers

#### `uniform`
Values that remain constant for all vertices/fragments in a draw call. Used for matrices, lights, textures, time, etc.

```glsl
// Vertex Shader
uniform mat4 modelMatrix;
uniform mat4 viewMatrix;
uniform mat4 projectionMatrix;
uniform vec3 cameraPosition;
uniform float time;

// Fragment Shader
uniform sampler2D texture1;
uniform vec3 lightPosition;
uniform float intensity;
```

#### `attribute` (Vertex Shader)
Per-vertex data provided by the application. In modern GLSL (ES 3.0+), use `in` instead.

```glsl
// Legacy (ES 2.0)
attribute vec3 position;
attribute vec3 normal;
attribute vec2 uv;

// Modern (ES 3.0+)
in vec3 position;
in vec3 normal;
in vec2 uv;
```

#### `varying` (ES 2.0) / `in`/`out` (ES 3.0+)
Interpolated values passed from vertex to fragment shader.

```glsl
// Vertex Shader
varying vec3 vNormal;
varying vec2 vUv;
varying vec3 vPosition;

// Fragment Shader
varying vec3 vNormal;
varying vec2 vUv;
varying vec3 vPosition;
```

### Precision Qualifiers (Important for Mobile)

```glsl
// Default precision for fragment shaders (mobile)
precision highp float;

// Precision levels:
// highp - Full 32-bit precision (slower on mobile)
// mediump - 16-bit half precision (faster, but limited range)
// lowp - 8-bit precision (fastest, very limited)

// Use mediump for colors, position values in 0-1 range
mediump float colorValue;

// Use highp for positions, normals, angles
highp vec3 worldPosition;
highp float angle;
```

### Three.js Built-in Uniforms

Three.js automatically injects these uniforms into your shaders:

```glsl
uniform mat4 modelMatrix;
uniform mat4 modelViewMatrix;
uniform mat4 projectionMatrix;
uniform mat4 viewMatrix;
uniform mat3 normalMatrix;

uniform vec3 cameraPosition;
uniform float time;  // Requires THREE.ShaderMaterial.uniformsLib or manually added
```

### Three.js ShaderMaterial Setup

```javascript
const material = new THREE.ShaderMaterial({
  uniforms: {
    texture: { value: new THREE.TextureLoader().load('texture.jpg') },
    time: { value: 0 },
    color: { value: new THREE.Color(0xff0000) },
    intensity: { value: 1.0 },
    lightPosition: { value: new THREE.Vector3(0, 5, 0) }
  },
  vertexShader: `
    uniform mat4 modelMatrix;
    uniform mat4 projectionMatrix;
    uniform mat4 viewMatrix;

    varying vec3 vNormal;
    varying vec2 vUv;

    void main() {
      vNormal = normalize(normalMatrix * normal);
      vUv = uv;
      gl_Position = projectionMatrix * viewMatrix * modelMatrix * vec4(position, 1.0);
    }
  `,
  fragmentShader: `
    uniform sampler2D texture;

    varying vec3 vNormal;
    varying vec2 vUv;

    void main() {
      gl_FragColor = texture2D(texture, vUv);
    }
  `
});
```

### Accessing Three.js Lights in Custom Shaders

To receive lighting in custom shaders, enable lights and use UniformsLib:

```javascript
const material = new THREE.ShaderMaterial({
  lights: true,  // Enable light uniforms
  uniforms: THREE.UniformsUtils.merge([
    THREE.UniformsLib.lights,  // Includes all light data
    {
      // Your custom uniforms
    }
  ]),
  vertexShader: `
    #include <common>
    #include <lights_pars_begin>

    varying vec3 vNormal;

    void main() {
      vNormal = normalize(normalMatrix * normal);
      gl_Position = projectionMatrix * viewMatrix * modelMatrix * vec4(position, 1.0);
    }
  `,
  fragmentShader: `
    #include <common>
    #include <lights_pars_begin>

    varying vec3 vNormal;

    void main() {
      // Light information available through uniforms
      gl_FragColor = vec4(vNormal * 0.5 + 0.5, 1.0);
    }
  `
});
```

---

## Vertex Shader Techniques {#vertex-shader-techniques}

### Vertex Displacement - Wave Effect

Create a wave-like animation by displacing vertices along their normals:

```glsl
uniform float time;
uniform float amplitude;
uniform float frequency;
uniform float speed;

varying vec3 vNormal;
varying vec3 vPosition;

void main() {
  vec3 pos = position;

  // Displace along normal
  float displacement = sin(pos.y * frequency + time * speed) * amplitude;
  pos += normal * displacement;

  vPosition = vec3(modelMatrix * vec4(pos, 1.0));
  vNormal = normalize(normalMatrix * normal);

  gl_Position = projectionMatrix * viewMatrix * vec4(pos, 1.0);
}
```

### Vertex Displacement - Noise-Based Terrain

Use Perlin/Simplex noise for organic deformation:

```glsl
uniform sampler2D noiseTexture;
uniform float noiseScale;
uniform float noiseStrength;
uniform float time;

varying vec3 vNormal;
varying vec3 vWorldPos;

void main() {
  vec3 pos = position;

  // Sample noise texture
  float noise = texture2D(noiseTexture, position.xy * noiseScale + time * 0.1).r;

  // Displace vertex along normal
  pos += normal * (noise - 0.5) * 2.0 * noiseStrength;

  vWorldPos = vec3(modelMatrix * vec4(pos, 1.0));
  vNormal = normalize(normalMatrix * normal);

  gl_Position = projectionMatrix * viewMatrix * modelMatrix * vec4(pos, 1.0);
}
```

### Vertex Displacement - Morphing Between Shapes

Smoothly blend between two vertex positions:

```glsl
uniform float morphFactor;  // 0.0 to 1.0

attribute vec3 positionB;  // Alternative position

varying vec3 vNormal;

void main() {
  // Lerp between two positions
  vec3 pos = mix(position, positionB, morphFactor);

  // Could also lerp normals for smooth shading
  vec3 norm = mix(normal, normalB, morphFactor);

  vNormal = normalize(normalMatrix * norm);

  gl_Position = projectionMatrix * viewMatrix * modelMatrix * vec4(pos, 1.0);
}
```

### Instanced Rendering with Custom Attributes

For rendering many instances of the same mesh with different transforms:

```javascript
// JavaScript setup
const geometry = new THREE.BoxGeometry(1, 1, 1);
const positionArray = new Float32Array(instanceCount * 3);
const rotationArray = new Float32Array(instanceCount * 4);  // Quaternion
const scaleArray = new Float32Array(instanceCount);
const colorArray = new Float32Array(instanceCount * 3);

// Fill arrays with per-instance data
for (let i = 0; i < instanceCount; i++) {
  positionArray[i * 3] = Math.random() * 10 - 5;
  positionArray[i * 3 + 1] = Math.random() * 10 - 5;
  positionArray[i * 3 + 2] = Math.random() * 10 - 5;
  // ... fill rotation, scale, color
}

geometry.setAttribute('instancePosition',
  new THREE.InstancedBufferAttribute(positionArray, 3));
geometry.setAttribute('instanceRotation',
  new THREE.InstancedBufferAttribute(rotationArray, 4));
geometry.setAttribute('instanceScale',
  new THREE.InstancedBufferAttribute(scaleArray, 1));
geometry.setAttribute('instanceColor',
  new THREE.InstancedBufferAttribute(colorArray, 3));
```

```glsl
// Vertex shader
attribute vec3 instancePosition;
attribute vec4 instanceRotation;
attribute float instanceScale;
attribute vec3 instanceColor;

varying vec3 vColor;
varying vec3 vNormal;

// Quaternion rotation function
vec3 rotateByQuat(vec3 v, vec4 q) {
  return v + 2.0 * cross(q.xyz, cross(q.xyz, v) + q.w * v);
}

void main() {
  // Apply instance transformations
  vec3 pos = rotateByQuat(position, instanceRotation);
  pos *= instanceScale;
  pos += instancePosition;

  vec3 norm = rotateByQuat(normal, instanceRotation);

  vColor = instanceColor;
  vNormal = normalize(normalMatrix * norm);

  gl_Position = projectionMatrix * viewMatrix * modelMatrix * vec4(pos, 1.0);
}
```

### Screen-Space Calculations

Transform vertex positions to screen space for effects like billboards:

```glsl
varying vec3 vNormal;
varying vec2 vScreenPos;

void main() {
  vNormal = normalize(normalMatrix * normal);

  // Transform to screen space (0 to 1)
  vec4 screenPos = projectionMatrix * viewMatrix * modelMatrix * vec4(position, 1.0);
  vScreenPos = screenPos.xy / screenPos.w * 0.5 + 0.5;

  gl_Position = screenPos;
}
```

### Normal Recalculation After Displacement

When displacing vertices, normals may need recalculation:

```glsl
uniform float displacementScale;

varying vec3 vNormal;

void main() {
  vec3 pos = position;
  vec3 norm = normal;

  // Apply displacement
  float displacement = sin(pos.x) * cos(pos.y) * displacementScale;
  pos += norm * displacement;

  // Recalculate normal using neighbor samples
  float epsilon = 0.0001;
  float d1 = sin(pos.x + epsilon) * cos(pos.y) * displacementScale;
  float d2 = sin(pos.x) * cos(pos.y + epsilon) * displacementScale;

  vec3 tangent = normalize(vec3(epsilon, 0.0, d1 - displacement));
  vec3 bitangent = normalize(vec3(0.0, epsilon, d2 - displacement));
  vec3 newNormal = normalize(cross(tangent, bitangent));

  vNormal = normalize(normalMatrix * newNormal);

  gl_Position = projectionMatrix * viewMatrix * modelMatrix * vec4(pos, 1.0);
}
```

---

## Fragment Shader Techniques {#fragment-shader-techniques}

### Procedural Noise Implementation

#### Perlin 2D Noise

```glsl
float random(vec2 st) {
  return fract(sin(dot(st, vec2(12.9898, 78.233))) * 43758.5453123);
}

float perlin(vec2 st) {
  vec2 i = floor(st);
  vec2 f = fract(st);

  // Four corner values
  float a = random(i);
  float b = random(i + vec2(1.0, 0.0));
  float c = random(i + vec2(0.0, 1.0));
  float d = random(i + vec2(1.0, 1.0));

  // Smooth interpolation
  vec2 u = f * f * (3.0 - 2.0 * f);

  // Mix corner values
  float lowerMix = mix(a, b, u.x);
  float upperMix = mix(c, d, u.x);
  return mix(lowerMix, upperMix, u.y);
}
```

#### Simplex 2D Noise (Faster, Better Quality)

```glsl
float simplexNoise2D(vec2 v) {
  const vec4 C = vec4(0.211324865405187, 0.366025403784439,
                      -0.577350269189626, 0.024390243902439);

  vec2 i = floor(v + dot(v, C.yy));
  vec2 x0 = v - i + dot(i, C.xx);

  vec2 i1 = (x0.x > x0.y) ? vec2(1.0, 0.0) : vec2(0.0, 1.0);
  vec4 x12 = x0.xyxy + C.xxzz;
  x12.xy -= i1;

  i = mod289(i);
  vec3 p = permute(permute(i.y + vec3(0.0, i1.y, 1.0)) + i.x + vec3(0.0, i1.x, 1.0));

  vec3 m = max(0.5 - vec3(dot(x0, x0), dot(x12.xy, x12.xy),
                           dot(x12.zw, x12.zw)), 0.0);
  m = m * m;
  m = m * m;

  vec3 x = 2.0 * fract(p * C.www) - 1.0;
  vec3 h = abs(x) - 0.5;
  vec3 ox = floor(x + 0.5);
  vec3 sx = sign(x);
  vec3 sh = step(h, vec3(0.0));
  vec3 a0 = sx * vec3(sh.x, sh.y, sh.z) + vec3(1.0 - sh.x, 1.0 - sh.y, 1.0 - sh.z);

  vec3 p0 = vec3(x0.xy, h.x);
  vec3 p1 = vec3(x12.xy, h.y);
  vec3 p2 = vec3(x12.zw, h.z);

  vec3 g0 = vec3(p0.x, p0.y, p0.z);
  vec3 g1 = vec3(p1.x, p1.y, p1.z);
  vec3 g2 = vec3(p2.x, p2.y, p2.z);

  vec3 norm0 = tanh(g0 * g0);
  vec3 norm1 = tanh(g1 * g1);
  vec3 norm2 = tanh(g2 * g2);

  float n0 = dot(norm0, vec3(p0.x, p0.y, p0.z));
  float n1 = dot(norm1, vec3(p1.x, p1.y, p1.z));
  float n2 = dot(norm2, vec3(p2.x, p2.y, p2.z));

  vec3 fade_xyz = fade(vec3(x0.xy, h.x));
  vec3 n_xyz = mix(vec3(n0), vec3(n1), fade_xyz.z);
  n_xyz = mix(n_xyz, vec3(n2), fade_xyz.y);

  return 2.2 * mix(n_xyz.x, n_xyz.y, fade_xyz.x);
}

// Helper functions
vec3 mod289(vec3 x) { return x - floor(x * (1.0 / 289.0)) * 289.0; }
vec2 mod289(vec2 x) { return x - floor(x * (1.0 / 289.0)) * 289.0; }
vec3 permute(vec3 x) { return mod289(((x * 34.0) + 1.0) * x); }
vec3 fade(vec3 t) { return t * t * t * (t * (t * 6.0 - 15.0) + 10.0); }
```

#### Fractal Brownian Motion (fBm)

Combine multiple octaves of noise for more natural patterns:

```glsl
float fbm(vec2 st, int octaves) {
  float value = 0.0;
  float amplitude = 0.5;
  float frequency = 1.0;
  float maxValue = 0.0;

  for(int i = 0; i < octaves; i++) {
    value += amplitude * simplexNoise2D(st * frequency);
    maxValue += amplitude;
    amplitude *= 0.5;
    frequency *= 2.0;
  }

  return value / maxValue;
}
```

#### Worley/Voronoi Noise

```glsl
float worleyNoise(vec2 p) {
  vec2 n = floor(p);
  vec2 f = fract(p);

  float minDist = 8.0;

  for (int y = -1; y <= 1; y++) {
    for (int x = -1; x <= 1; x++) {
      vec2 neighbor = vec2(float(x), float(y));
      vec2 point = random2D(n + neighbor);

      vec2 diff = neighbor + point - f;
      float dist = length(diff);

      minDist = min(minDist, dist);
    }
  }

  return minDist;
}

vec2 random2D(vec2 st) {
  st = vec2(dot(st, vec2(127.1, 311.7)),
            dot(st, vec2(269.5, 183.3)));
  return -1.0 + 2.0 * fract(sin(st) * 43758.5453123);
}
```

### Procedural Textures

#### Wood Grain

```glsl
float woodGrain(vec3 pos, float scale) {
  float wood = fbm(pos.xz * scale, 4);
  float rings = sin(length(pos.xz) * 20.0 + wood * 5.0);
  return wood * 0.5 + rings * 0.5;
}

void main() {
  float wood = woodGrain(vPosition, 2.0);
  vec3 color = mix(vec3(0.4, 0.2, 0.1), vec3(0.8, 0.5, 0.2), wood);
  gl_FragColor = vec4(color, 1.0);
}
```

#### Marble Pattern

```glsl
float marble(vec3 pos) {
  float noise = fbm(pos.xy * 3.0, 5);
  float pattern = sin(pos.z * 5.0 + noise * 10.0);
  pattern = abs(pattern);
  return smoothstep(0.2, 0.8, pattern);
}

void main() {
  float m = marble(vPosition);
  vec3 color = mix(vec3(0.2), vec3(1.0), m);
  gl_FragColor = vec4(color, 1.0);
}
```

#### Rust/Corrosion Effect

```glsl
float rust(vec3 pos) {
  float base = fbm(pos.xy * 2.0, 4);
  float detail = fbm(pos.xy * 8.0, 3);
  float cracks = fract(sin(pos.x * 100.0) * sin(pos.z * 100.0) * 43758.5);

  float result = mix(base, detail, 0.5);
  result = mix(result, cracks, 0.3);

  return result;
}

void main() {
  float r = rust(vPosition);
  vec3 rustColor = vec3(0.8, 0.4, 0.2) * r + vec3(0.3, 0.1, 0.05);
  gl_FragColor = vec4(rustColor, 1.0);
}
```

#### Hex Grid Pattern

```glsl
float hexGrid(vec2 p) {
  const float sqrt3 = 1.732050808;
  const vec2 hex1 = vec2(1.0, sqrt3);
  const vec2 hex2 = vec2(2.0, 0.0);

  vec2 q = vec2(hex1.x * p.x + hex2.x * p.y,
                 hex1.y * p.x - hex2.x * p.y);
  q /= (hex1.x + hex2.x);

  vec2 pi = round(q);
  vec2 pf = fract(q);

  float d = dot(pf - 0.5, pf - 0.5);

  return step(0.3, d);
}

void main() {
  float hex = hexGrid(vUv * 10.0);
  vec3 color = mix(vec3(0.1), vec3(1.0), hex);
  gl_FragColor = vec4(color, 1.0);
}
```

### Color Manipulation

#### RGB to HSV Conversion

```glsl
vec3 rgb2hsv(vec3 c) {
  vec4 K = vec4(0.0, -1.0 / 3.0, 2.0 / 3.0, -1.0);
  vec4 p = mix(vec4(c.bg, K.wz), vec4(c.gb, K.xy), step(c.b, c.g));
  vec4 q = mix(vec4(p.xyw, c.r), vec4(c.r, p.yzx), step(p.x, c.r));

  float d = q.x - min(q.w, q.y);
  float e = 1.0e-10;

  return vec3(abs(q.z + (q.w - q.y) / (6.0 * d + e)),
              d / (q.x + e),
              q.x);
}

vec3 hsv2rgb(vec3 c) {
  vec4 K = vec4(1.0, 2.0 / 3.0, 1.0 / 3.0, 3.0);
  vec3 p = abs(fract(c.xxx + K.xyz) * 6.0 - K.www);
  return c.z * mix(K.xxx, clamp(p - K.xxx, 0.0, 1.0), c.y);
}
```

#### Palette Generation with Smooth Colors

```glsl
vec3 palette(float t, vec3 a, vec3 b, vec3 c, vec3 d) {
  return a + b * cos(6.28318 * (c * t + d));
}

void main() {
  vec3 col = palette(vUv.x,
                     vec3(0.5, 0.5, 0.5),
                     vec3(0.5, 0.5, 0.5),
                     vec3(1.0, 1.0, 1.0),
                     vec3(0.0, 0.33, 0.67));

  gl_FragColor = vec4(col, 1.0);
}
```

#### Gradient and Color Ramp

```glsl
vec3 colorRamp(float t) {
  if (t < 0.33) {
    return mix(vec3(0, 0, 1), vec3(0, 1, 1), t / 0.33);
  } else if (t < 0.66) {
    return mix(vec3(0, 1, 1), vec3(1, 0, 0), (t - 0.33) / 0.33);
  } else {
    return mix(vec3(1, 0, 0), vec3(1, 1, 0), (t - 0.66) / 0.34);
  }
}

void main() {
  float t = fbm(vUv, 4);
  vec3 color = colorRamp(t);
  gl_FragColor = vec4(color, 1.0);
}
```

### Edge Detection and Outline Effects

#### Sobel Edge Detection

```glsl
float sobel(sampler2D tex, vec2 uv, float resolution) {
  float step = 1.0 / resolution;

  // Sobel kernels
  float gx = -1.0 * texture2D(tex, uv + vec2(-step, step)).r +
             -2.0 * texture2D(tex, uv + vec2(-step, 0.0)).r +
             -1.0 * texture2D(tex, uv + vec2(-step, -step)).r +
              1.0 * texture2D(tex, uv + vec2(step, step)).r +
              2.0 * texture2D(tex, uv + vec2(step, 0.0)).r +
              1.0 * texture2D(tex, uv + vec2(step, -step)).r;

  float gy = 1.0 * texture2D(tex, uv + vec2(-step, step)).r +
             2.0 * texture2D(tex, uv + vec2(0.0, step)).r +
             1.0 * texture2D(tex, uv + vec2(step, step)).r +
             -1.0 * texture2D(tex, uv + vec2(-step, -step)).r +
             -2.0 * texture2D(tex, uv + vec2(0.0, -step)).r +
             -1.0 * texture2D(tex, uv + vec2(step, -step)).r;

  return sqrt(gx * gx + gy * gy);
}

void main() {
  float edge = sobel(tex, vUv, 512.0);
  gl_FragColor = vec4(vec3(edge), 1.0);
}
```

### Fresnel Effect for Rim Lighting

```glsl
varying vec3 vNormal;
varying vec3 vPosition;

uniform vec3 rimColor;
uniform float rimPower;
uniform float rimIntensity;

void main() {
  vec3 viewDir = normalize(cameraPosition - vPosition);
  vec3 normal = normalize(vNormal);

  // Fresnel calculation
  float fresnel = 1.0 - max(0.0, dot(normal, viewDir));
  fresnel = pow(fresnel, rimPower);

  vec3 rim = rimColor * fresnel * rimIntensity;

  vec3 baseColor = vec3(0.5);
  vec3 finalColor = baseColor + rim;

  gl_FragColor = vec4(finalColor, 1.0);
}
```

### Triplanar Mapping

Texture 3D objects without UV coordinates:

```glsl
varying vec3 vPosition;
varying vec3 vNormal;

uniform sampler2D textureX;
uniform sampler2D textureY;
uniform sampler2D textureZ;
uniform float scale;

void main() {
  vec3 position = vPosition * scale;
  vec3 normal = normalize(vNormal);
  normal = abs(normal);

  // Sample from three directions
  vec3 colX = texture2D(textureX, position.yz).rgb;
  vec3 colY = texture2D(textureY, position.xz).rgb;
  vec3 colZ = texture2D(textureZ, position.xy).rgb;

  // Normalize weights
  normal = normalize(normal);
  vec3 weights = normal / (normal.x + normal.y + normal.z);

  // Blend samples
  vec3 color = colX * weights.x + colY * weights.y + colZ * weights.z;

  gl_FragColor = vec4(color, 1.0);
}
```

---

## Lighting in Custom Shaders {#lighting-in-custom-shaders}

### Phong/Blinn-Phong Lighting Model

```glsl
varying vec3 vNormal;
varying vec3 vPosition;

uniform vec3 lightPosition;
uniform vec3 lightColor;
uniform vec3 ambientColor;
uniform float shininess;

void main() {
  vec3 normal = normalize(vNormal);
  vec3 viewDir = normalize(cameraPosition - vPosition);
  vec3 lightDir = normalize(lightPosition - vPosition);

  // Ambient
  vec3 ambient = ambientColor;

  // Diffuse
  float diff = max(0.0, dot(normal, lightDir));
  vec3 diffuse = diff * lightColor;

  // Specular (Blinn-Phong: use half vector)
  vec3 halfDir = normalize(lightDir + viewDir);
  float spec = pow(max(0.0, dot(normal, halfDir)), shininess);
  vec3 specular = spec * lightColor;

  vec3 color = (ambient + diffuse + specular) * vec3(0.8, 0.2, 0.1);

  gl_FragColor = vec4(color, 1.0);
}
```

### PBR Cook-Torrance Implementation

```glsl
const float PI = 3.14159265359;

varying vec3 vNormal;
varying vec3 vPosition;

uniform sampler2D albedoMap;
uniform sampler2D normalMap;
uniform sampler2D metallicMap;
uniform sampler2D roughnessMap;
uniform sampler2D aoMap;

uniform vec3 lightPositions[4];
uniform vec3 lightColors[4];

// Normal Distribution Function (Trowbridge-Reitz GGX)
float DistributionGGX(vec3 N, vec3 H, float roughness) {
  float a = roughness * roughness;
  float a2 = a * a;
  float NdotH = max(dot(N, H), 0.0);
  float NdotH2 = NdotH * NdotH;

  float nom = a2;
  float denom = (NdotH2 * (a2 - 1.0) + 1.0);
  denom = PI * denom * denom;

  return nom / denom;
}

// Geometry Function (Schlick-GGX)
float GeometrySchlickGGX(float NdotV, float roughness) {
  float r = (roughness + 1.0);
  float k = (r * r) / 8.0;

  float nom = NdotV;
  float denom = NdotV * (1.0 - k) + k;

  return nom / denom;
}

float GeometrySmith(vec3 N, vec3 V, vec3 L, float roughness) {
  float NdotV = max(dot(N, V), 0.0);
  float NdotL = max(dot(N, L), 0.0);
  float ggx2 = GeometrySchlickGGX(NdotV, roughness);
  float ggx1 = GeometrySchlickGGX(NdotL, roughness);

  return ggx1 * ggx2;
}

// Fresnel-Schlick Approximation
vec3 fresnelSchlick(float cosTheta, vec3 F0) {
  return F0 + (1.0 - F0) * pow(1.0 - cosTheta, 5.0);
}

void main() {
  // Fetch textures
  vec3 albedo = texture2D(albedoMap, vUv).rgb;
  float metallic = texture2D(metallicMap, vUv).r;
  float roughness = texture2D(roughnessMap, vUv).r;
  float ao = texture2D(aoMap, vUv).r;

  vec3 N = normalize(vNormal);
  vec3 V = normalize(cameraPosition - vPosition);

  // F0 varies with metallic
  vec3 F0 = vec3(0.04);
  F0 = mix(F0, albedo, metallic);

  vec3 Lo = vec3(0.0);

  // Directional lights
  for (int i = 0; i < 4; ++i) {
    vec3 L = normalize(lightPositions[i] - vPosition);
    vec3 H = normalize(V + L);

    float distance = length(lightPositions[i] - vPosition);
    float attenuation = 1.0 / (distance * distance);
    vec3 radiance = lightColors[i] * attenuation;

    // Cook-Torrance BRDF
    float NDF = DistributionGGX(N, H, roughness);
    float G = GeometrySmith(N, V, L, roughness);
    vec3 F = fresnelSchlick(max(dot(H, V), 0.0), F0);

    vec3 kD = vec3(1.0) - F;
    kD *= 1.0 - metallic;

    vec3 numerator = NDF * G * F;
    float denominator = 4.0 * max(dot(N, V), 0.0) * max(dot(N, L), 0.0);
    vec3 specular = numerator / max(denominator, 0.001);

    float NdotL = max(dot(N, L), 0.0);
    Lo += (kD * albedo / PI + specular) * radiance * NdotL;
  }

  vec3 ambient = vec3(0.03) * albedo * ao;
  vec3 color = ambient + Lo;

  // Tone mapping
  color = color / (color + vec3(1.0));
  color = pow(color, vec3(1.0 / 2.2));

  gl_FragColor = vec4(color, 1.0);
}
```

### Normal Mapping in Tangent Space

```glsl
varying vec3 vFragPos;
varying vec2 vUv;
varying mat3 vTBN;

uniform sampler2D normalMap;
uniform vec3 lightPos;

void main() {
  // Sample normal from normal map
  vec3 normal = texture2D(normalMap, vUv).rgb;

  // Convert from [0, 1] to [-1, 1]
  normal = normalize(normal * 2.0 - 1.0);

  // Transform to world space using TBN matrix
  normal = normalize(vTBN * normal);

  // Rest of lighting calculation uses perturbed normal
  vec3 lightDir = normalize(lightPos - vFragPos);
  float diff = max(dot(normal, lightDir), 0.0);

  vec3 color = vec3(0.5) * diff;
  gl_FragColor = vec4(color, 1.0);
}
```

**Vertex Shader for Normal Mapping:**

```glsl
attribute vec3 tangent;
attribute vec3 bitangent;

varying vec3 vFragPos;
varying vec2 vUv;
varying mat3 vTBN;

void main() {
  vFragPos = vec3(modelMatrix * vec4(position, 1.0));
  vUv = uv;

  // Transform tangent space vectors
  vec3 T = normalize(vec3(modelMatrix * vec4(tangent, 0.0)));
  vec3 B = normalize(vec3(modelMatrix * vec4(bitangent, 0.0)));
  vec3 N = normalize(vec3(modelMatrix * vec4(normal, 0.0)));

  // Gram-Schmidt orthogonalization
  T = normalize(T - dot(T, N) * N);
  B = cross(N, T);

  vTBN = mat3(T, B, N);

  gl_Position = projectionMatrix * viewMatrix * vec4(vFragPos, 1.0);
}
```

### Shadow Receiving in Custom Shaders

```glsl
#include <common>
#include <lights_pars_begin>
#include <shadowmap_pars_fragment>

varying vec3 vNormal;
varying vec3 vPosition;

void main() {
  vec3 normal = normalize(vNormal);
  vec3 viewDir = normalize(cameraPosition - vPosition);

  // Get shadow coordinate (provided by Three.js)
  vec4 shadowCoord = vShadowCoord[0];
  float shadow = 1.0;

  #if defined(USE_SHADOWMAP)
    // Sample shadow map
    shadow = getShadow(directionalLights[0].shadowMap, shadowCoord);
  #endif

  // Apply shadow to lighting
  vec3 color = vec3(0.5, 0.3, 0.2);
  color *= (0.3 + 0.7 * shadow);  // Shadow factor

  gl_FragColor = vec4(color, 1.0);
}
```

### Image-Based Lighting (IBL) Approximation

```glsl
varying vec3 vNormal;
varying vec3 vPosition;

uniform samplerCube irradianceMap;
uniform samplerCube prefilterMap;
uniform sampler2D brdfLUT;

void main() {
  vec3 normal = normalize(vNormal);
  vec3 viewDir = normalize(cameraPosition - vPosition);
  vec3 reflectDir = reflect(-viewDir, normal);

  // Diffuse IBL
  vec3 kD = vec3(1.0) - vec3(0.5);  // Metallic component
  vec3 diffuse = textureCube(irradianceMap, normal).rgb * kD;

  // Specular IBL
  vec3 prefilteredColor = textureCube(prefilterMap, reflectDir, log2(roughness * 4.0)).rgb;
  vec2 brdf = texture2D(brdfLUT, vec2(max(dot(normal, viewDir), 0.0), roughness)).rg;
  vec3 specular = prefilteredColor * (vec3(0.5) * brdf.x + brdf.y);

  vec3 color = diffuse + specular;
  gl_FragColor = vec4(color, 1.0);
}
```

---

## Advanced Shader Patterns {#advanced-shader-patterns}

### Raymarching Implementation

Basic raymarching with signed distance functions:

```glsl
uniform float maxSteps;
uniform float maxDistance;

float sceneSDF(vec3 p) {
  // Distance to sphere at origin with radius 1.0
  return length(p) - 1.0;
}

vec3 rayMarch(vec3 rayOrigin, vec3 rayDir) {
  float depth = 0.0;

  for (int i = 0; i < int(maxSteps); i++) {
    vec3 p = rayOrigin + rayDir * depth;
    float dist = sceneSDF(p);

    if (dist < 0.001) {
      return p;  // Hit
    }

    depth += dist;

    if (depth >= maxDistance) {
      break;  // Miss
    }
  }

  return rayOrigin + rayDir * maxDistance;
}

vec3 estimateNormal(vec3 p) {
  const float epsilon = 0.001;
  float d = sceneSDF(p);

  vec3 grad = vec3(
    sceneSDF(p + vec3(epsilon, 0, 0)) - d,
    sceneSDF(p + vec3(0, epsilon, 0)) - d,
    sceneSDF(p + vec3(0, 0, epsilon)) - d
  );

  return normalize(grad);
}

void main() {
  vec3 rayOrigin = cameraPosition;
  vec3 rayDir = normalize(vPosition - cameraPosition);

  vec3 hitPoint = rayMarch(rayOrigin, rayDir);
  vec3 normal = estimateNormal(hitPoint);

  // Simple diffuse shading
  vec3 lightDir = normalize(vec3(1, 1, 1));
  float diff = max(0.0, dot(normal, lightDir));

  vec3 color = vec3(0.5, 0.2, 0.1) * (0.3 + 0.7 * diff);
  gl_FragColor = vec4(color, 1.0);
}
```

### Volumetric Fog with Raymarching

```glsl
uniform float fogDensity;
uniform float fogStepSize;
uniform int fogSteps;

vec3 raymarchFog(vec3 rayOrigin, vec3 rayDir, float maxDist) {
  vec3 fog = vec3(0.0);
  float transmittance = 1.0;

  for (int step = 0; step < fogSteps; step++) {
    float dist = float(step) * fogStepSize;

    if (dist > maxDist) break;

    vec3 pos = rayOrigin + rayDir * dist;

    // Sample density at this position
    float density = fogDensity * exp(-length(pos) * 0.1);

    // Beer's Law: transmittance through fog
    float sampleTransmittance = exp(-density * fogStepSize);

    // Accumulate fog
    fog += transmittance * density * vec3(0.8, 0.8, 0.9);

    // Update transmittance
    transmittance *= sampleTransmittance;
  }

  return fog;
}

void main() {
  vec3 rayDir = normalize(vPosition - cameraPosition);
  vec3 fog = raymarchFog(cameraPosition, rayDir, 100.0);

  gl_FragColor = vec4(fog, 1.0);
}
```

### Screen-Space Reflections

```glsl
uniform sampler2D depthTexture;
uniform sampler2D normalTexture;
uniform mat4 projectionMatrix;

vec4 screenSpaceReflection(vec3 pos, vec3 normal, vec3 viewDir) {
  vec3 reflectDir = reflect(-viewDir, normal);

  // Project to screen space
  vec4 reflectPos = projectionMatrix * vec4(pos + reflectDir, 1.0);
  reflectPos.xy /= reflectPos.w;
  reflectPos.xy = reflectPos.xy * 0.5 + 0.5;

  vec3 rayPos = pos;
  vec3 rayDir = normalize(reflectDir);

  // March along reflection ray
  for (int i = 0; i < 32; i++) {
    rayPos += rayDir * 0.5;

    vec4 projRayPos = projectionMatrix * vec4(rayPos, 1.0);
    projRayPos.xy /= projRayPos.w;
    projRayPos.xy = projRayPos.xy * 0.5 + 0.5;

    float depth = texture2D(depthTexture, projRayPos.xy).r;

    if (projRayPos.z > depth) {
      // Hit detected
      return vec4(texture2D(normalTexture, projRayPos.xy).rgb, 1.0);
    }
  }

  return vec4(0.0);
}
```

### Parallax Mapping / Parallax Occlusion Mapping

```glsl
varying vec3 vTangentViewDir;
varying vec2 vUv;

uniform sampler2D heightMap;
uniform float heightScale;

vec2 parallaxMapping(vec2 uv, vec3 viewDir) {
  float height = texture2D(heightMap, uv).r;
  vec2 p = viewDir.xy / viewDir.z * (height * heightScale);
  return uv - p;
}

vec2 parallaxOcclusionMapping(vec2 uv, vec3 viewDir) {
  float heightScale = 0.1;
  float numLayers = 8.0;
  float layerHeight = 1.0 / numLayers;
  float currentLayerHeight = 0.0;
  vec2 shift = viewDir.xy / viewDir.z * heightScale;
  vec2 currentTextureCoords = uv;

  float heightFromTexture = texture2D(heightMap, currentTextureCoords).r;

  for (int i = 0; i < 8; i++) {
    currentLayerHeight += layerHeight;

    if (currentLayerHeight >= heightFromTexture) {
      break;
    }

    currentTextureCoords -= shift * layerHeight;
    heightFromTexture = texture2D(heightMap, currentTextureCoords).r;
  }

  return currentTextureCoords;
}

void main() {
  vec2 uv = parallaxOcclusionMapping(vUv, normalize(vTangentViewDir));

  vec3 color = texture2D(diffuseTexture, uv).rgb;
  gl_FragColor = vec4(color, 1.0);
}
```

### Subsurface Scattering Approximation

```glsl
varying vec3 vNormal;
varying vec3 vPosition;

uniform sampler2D thicknessMap;
uniform vec3 lightPos;

float subsurfaceScattering(vec3 pos, vec3 normal) {
  vec3 lightDir = normalize(lightPos - pos);

  // Check thickness (simulated with texture)
  float thickness = texture2D(thicknessMap, vUv).r;

  // Backlighting effect
  float backLight = max(0.0, dot(-normal, lightDir)) * thickness;

  // Gaussian falloff
  backLight = exp(backLight * 2.0 - 1.0) * 0.4;

  return backLight;
}

void main() {
  vec3 normal = normalize(vNormal);
  float sss = subsurfaceScattering(vPosition, normal);

  vec3 baseColor = vec3(1.0, 0.7, 0.5);  // Skin-like color
  vec3 scatteredLight = vec3(1.0, 0.2, 0.0) * sss;

  vec3 finalColor = baseColor + scatteredLight;
  gl_FragColor = vec4(finalColor, 1.0);
}
```

### Cel / Toon Shading

```glsl
varying vec3 vNormal;
varying vec3 vPosition;
varying vec3 vViewDir;

uniform vec3 lightPos;
uniform vec3 lightColor;

void main() {
  vec3 normal = normalize(vNormal);
  vec3 lightDir = normalize(lightPos - vPosition);
  vec3 viewDir = normalize(vViewDir);

  // Diffuse with threshold
  float diff = max(0.0, dot(normal, lightDir));
  diff = smoothstep(0.0, 0.01, diff - 0.5) + smoothstep(0.0, 0.01, diff - 0.0);

  // Specular highlight threshold
  vec3 halfDir = normalize(lightDir + viewDir);
  float spec = pow(max(0.0, dot(normal, halfDir)), 32.0);
  spec = step(0.5, spec);

  // Base color with cel shading
  vec3 baseColor = vec3(0.5, 0.2, 0.1);
  vec3 color = baseColor * (0.2 + diff * 0.8) + spec * vec3(1.0);

  gl_FragColor = vec4(color, 1.0);
}
```

### Hologram / Scan Line Effect

```glsl
varying vec2 vUv;
varying vec3 vPosition;

uniform float time;
uniform float scanLineIntensity;

void main() {
  // Scan lines
  float scanLines = sin(vUv.y * 100.0 + time * 5.0) * 0.5 + 0.5;
  scanLines = mix(1.0, scanLines, scanLineIntensity);

  // Horizontal distortion
  float distortion = sin(time * 2.0 + vPosition.y * 0.5) * 0.02;
  vec2 distortedUv = vUv + vec2(distortion, 0.0);

  // Flicker effect
  float flicker = sin(time * 10.0) * 0.2 + 0.8;

  vec3 color = vec3(0.0, 1.0, 0.5) * scanLines * flicker;
  gl_FragColor = vec4(color, 0.8);
}
```

### Dissolve / Disintegration Effect

```glsl
varying vec2 vUv;
varying vec3 vNormal;

uniform sampler2D dissolveTexture;
uniform float dissolveAmount;
uniform vec3 edgeColor;
uniform float edgeWidth;

void main() {
  float dissolve = texture2D(dissolveTexture, vUv).r;

  // Clip fragments
  if (dissolve < dissolveAmount) {
    discard;
  }

  // Edge detection
  float edge = smoothstep(
    dissolveAmount - edgeWidth,
    dissolveAmount,
    dissolve
  );

  vec3 baseColor = vec3(0.5, 0.2, 0.1);
  vec3 color = mix(baseColor, edgeColor, edge);

  gl_FragColor = vec4(color, 1.0);
}
```

### Force Field / Energy Shield Effect

```glsl
varying vec3 vNormal;
varying vec3 vPosition;
varying vec2 vUv;

uniform float time;
uniform vec3 shieldColor;
uniform float shieldIntensity;

void main() {
  // Ripple from center
  float ripple = sin(length(vPosition) * 5.0 - time * 3.0) * 0.5 + 0.5;

  // Fresnel effect
  vec3 viewDir = normalize(cameraPosition - vPosition);
  float fresnel = 1.0 - max(0.0, dot(normalize(vNormal), viewDir));
  fresnel = pow(fresnel, 2.0);

  // Combine effects
  float effect = mix(ripple, fresnel, 0.5) * shieldIntensity;

  vec3 color = shieldColor * effect;
  gl_FragColor = vec4(color, effect * 0.6);
}
```

### Heat Distortion / Refraction Effect

```glsl
varying vec2 vUv;
varying vec3 vPosition;

uniform sampler2D mainTexture;
uniform sampler2D distortionTexture;
uniform float time;
uniform float distortionAmount;

void main() {
  // Sample distortion map
  vec2 distortion = texture2D(distortionTexture, vUv + time * 0.1).rg;
  distortion = (distortion - 0.5) * 2.0;

  // Apply distortion to UV
  vec2 distortedUv = vUv + distortion * distortionAmount;

  // Sample refracted color
  vec3 color = texture2D(mainTexture, distortedUv).rgb;

  // Add heat glow
  vec3 heatGlow = vec3(1.0, 0.5, 0.0) * (sin(time * 2.0 + vPosition.y) * 0.5 + 0.5) * 0.3;

  gl_FragColor = vec4(color + heatGlow, 1.0);
}
```

---

## Performance Optimization {#performance-optimization}

### Branching Costs and Avoidance

**Problem:** Branching causes GPU pipeline stalls since parallel execution may diverge.

```glsl
// SLOW: Complex branching
if (value > 0.5) {
  result = expensiveFunction1();
} else if (value > 0.25) {
  result = expensiveFunction2();
} else {
  result = expensiveFunction3();
}

// FAST: Use smooth functions instead
result = mix(
  expensiveFunction3(),
  mix(expensiveFunction2(), expensiveFunction1(),
      smoothstep(0.5, 0.5 + epsilon, value)),
  smoothstep(0.25, 0.25 + epsilon, value)
);
```

**Best Practices:**
- Use `mix()`, `smoothstep()`, `clamp()`, `step()` instead of if-else
- These have no performance penalty on modern GPUs
- Unroll small loops at compile time
- Avoid dynamic loop bounds

### Texture Lookup Optimization

```glsl
// PROBLEM: Dependent texture reads
vec2 uv = vUv;
uv += texture2D(normalMap, uv).xy;  // Read-then-use
uv += texture2D(detailMap, uv).xy;

// SOLUTION: Cache results or use different approach
vec2 uv = vUv;
vec2 offset1 = texture2D(normalMap, uv).xy;
vec2 offset2 = texture2D(detailMap, vUv).xy;  // Use original UV
uv += offset1 + offset2;
```

**Texture Optimization Tips:**
- Minimize texture lookups (group into one sample when possible)
- Use integer coordinates for exact lookups
- Cache frequently accessed texture data
- Prefer `GL_NEAREST` filtering for pixel-perfect textures
- Use compressed texture formats (ASTC, ETC2, BC7)

### Precision Tradeoffs

```glsl
// For mobile ES 2.0 - set default precision
precision highp float;

// Use lowp for colors (0-1 range)
lowp vec3 color;

// Use mediump for normalized values
mediump float normalizedValue;

// Use highp only when needed
highp float worldPosition;
highp float angle;

// Example: Color operations can be mediump
mediump vec4 color = lowp vec4(1.0, 0.5, 0.2, 1.0) * lowp texture2D(tex, vUv);
```

**Precision Guidelines:**
- `highp`: Position, normals, angles, exponentials - needed for accuracy
- `mediump`: Colors, normalized values, direction vectors - sufficient precision
- `lowp`: Time loops, integer counters - fastest

### When to Precompute vs Compute in Shader

**Precompute in JavaScript:**
- Matrix transformations (use uniform matrices)
- Lighting constants
- Noise textures
- Environment maps
- Large lookup tables

```javascript
// Precompute and pass as uniform
const lightUniforms = {
  lightPos: new THREE.Vector3(5, 5, 5),
  lightColor: new THREE.Color(0xffffff)
};

// Store as texture instead of computing in shader
const noiseTexture = generateNoiseTexture(512, 512);
material.uniforms.noiseTexture.value = noiseTexture;
```

**Compute in Shader:**
- Per-pixel operations
- Fragment-dependent calculations
- Simple mathematical operations
- Procedural effects

### Shader Complexity Budget for 60fps

Target frame time: 16.67ms per frame

**Budget breakdown for typical scene:**
- Vertex shader: 30-50% of frame time
- Fragment shader: 40-60% of frame time
- GPU memory: 200-500MB total

**Shader complexity levels:**

```glsl
// LEVEL 1 (Simple): ~0.5ms on high-end GPU
void main() {
  gl_FragColor = texture2D(tex, vUv);
}

// LEVEL 2 (Moderate): ~2-3ms on high-end GPU
void main() {
  vec3 normal = normalize(vNormal);
  float diff = dot(normal, lightDir);
  gl_FragColor = vec4(vec3(diff), 1.0);
}

// LEVEL 3 (Complex): ~5-10ms on high-end GPU
// - Multiple texture lookups
// - Complex math (fbm, multiple noise samples)
// - Many branches or loops

// LEVEL 4 (Very Complex): 10-20ms+
// - Raymarching
// - Volumetric effects
// - Complex PBR
// - Screen-space calculations
```

**Optimization techniques:**
- Reduce texture lookups (atlas textures)
- Use lower resolution renders with upsampling
- Move calculations to vertex shader when possible
- Cache expensive calculations
- Use LOD (Level of Detail) systems

---

## Noise Library Reference {#noise-library-reference}

### Complete Simplex 2D Noise Implementation

For copy-paste directly into any shader:

```glsl
// Simplex 2D Noise
vec3 permute(vec3 x) { return mod((34.0 * x + 1.0) * x, 289.0); }

float simplexNoise2D(vec2 v)
{
  const vec4 C = vec4(0.211324865405187, 0.366025403784439,
                      -0.577350269189626, 0.024390243902439);
  vec2 i  = floor(v + dot(v, C.yy) );
  vec2 x0 = v -   i + dot(i, C.xx);
  vec2 i1;
  i1 = (x0.x > x0.y) ? vec2(1.0, 0.0) : vec2(0.0, 1.0);
  vec4 x12 = x0.xyxy + C.xxzz;
  x12.xy -= i1;
  i = mod(i, 289.0);
  vec3 p = permute( permute( i.y + vec3(0.0, i1.y, 1.0 ))
  + i.x + vec3(0.0, i1.x, 1.0 ));
  vec3 m = max(0.5 - vec3(dot(x0,x0), dot(x12.xy,x12.xy),
    dot(x12.zw,x12.zw)), 0.0);
  m = m*m ;
  m = m*m ;
  vec3 x = 2.0 * fract(p * C.www) - 1.0;
  vec3 h = abs(x) - 0.5;
  vec3 ox = floor(x + 0.5);
  vec3 sx = sign(x);
  vec3 sh = step(h, vec3(0.0));
  vec3 a0 = sx * vec2(sh.x, sh.y).xyx + sh.zyx;

  m *= inversesqrt( 2.0 * dot(a0,a0) );
  vec3 g;
  g.x  = a0.x  * x0.x  + a0.y  * x0.y;
  g.yz = a0.yz * x12.xz + a0.z  * x12.yw;
  return 130.0 * dot(m, g);
}
```

### Perlin 2D Noise Implementation

```glsl
float random(vec2 st) {
  return fract(sin(dot(st.xy, vec2(12.9898,78.233))) * 43758.5453123);
}

float perlin2D(vec2 st) {
  vec2 i = floor(st);
  vec2 f = fract(st);

  float a = random(i);
  float b = random(i + vec2(1.0, 0.0));
  float c = random(i + vec2(0.0, 1.0));
  float d = random(i + vec2(1.0, 1.0));

  // Smooth interpolation curve
  vec2 u = f * f * (3.0 - 2.0 * f);

  float lowerMix = mix(a, b, u.x);
  float upperMix = mix(c, d, u.x);
  return mix(lowerMix, upperMix, u.y);
}
```

### Simplex 3D Noise Implementation

```glsl
vec4 permute(vec4 x){return mod(((x*34.0)+1.0)*x, 289.0);}
vec4 taylorInvSqrt(vec4 r){return 1.79284291400159 - 0.85373472095314 * r;}

float snoise(vec3 v)
{
  const vec2  C = vec2(1.0/6.0, 1.0/3.0) ;
  const vec4  D = vec4(0.0, 0.5, 1.0, 2.0);
  vec3 i  = floor(v + dot(v, C.yyy) );
  vec3 x0 = v - i + dot(i, C.xxx) ;
  vec3 g = step(x0.yzx, x0.xyz);
  vec3 l = 1.0 - g;
  vec3 i1 = min( g.xyz, l.zxy );
  vec3 i2 = max( g.xyz, l.zxy );
  vec3 x1 = x0 - i1 + C.xxx;
  vec3 x2 = x0 - i2 + C.yyy;
  vec3 x3 = x0 - D.yyy;
  i = mod(i, 289.0 );
  vec4 p = permute( permute( permute(
             i.z + vec4(0.0, i1.z, i2.z, 1.0 ))
           + i.y + vec4(0.0, i1.y, i2.y, 1.0 ))
           + i.x + vec4(0.0, i1.x, i2.x, 1.0 ));
  float n_ = 0.142857142857;
  vec3  ns = n_ * D.wyz - D.xzx;
  vec4 j = p - 49.0 * floor(p * ns.z * ns.z);
  vec4 x_ = floor(j * ns.z);
  vec4 y_ = floor(j - 7.0 * x_ );
  vec4 x = x_ *ns.x + ns.yyyy;
  vec4 y = y_ *ns.x + ns.yyyy;
  vec4 h = 1.0 - abs(x) - abs(y);
  vec4 b0 = vec4( x.xy, y.xy );
  vec4 b1 = vec4( x.zw, y.zw );
  vec4 s0 = floor(b0)*2.0 + 1.0;
  vec4 s1 = floor(b1)*2.0 + 1.0;
  vec4 sh = -step(h, vec4(0.0));
  vec4 a0 = b0.xzyw + s0.xzyw*sh.xxyy ;
  vec4 a1 = b1.xzyw + s1.xzyw*sh.zzww ;
  vec3 p0 = vec3(a0.xy, h.x);
  vec3 p1 = vec3(a0.zw, h.y);
  vec3 p2 = vec3(a1.xy, h.z);
  vec3 p3 = vec3(a1.zw, h.w);
  vec4 norm = taylorInvSqrt(vec4(dot(p0,p0), dot(p1,p1), dot(p2, p2), dot(p3,p3)));
  p0 *= norm.x;
  p1 *= norm.y;
  p2 *= norm.z;
  p3 *= norm.w;
  vec4 m = max(0.6 - vec4(dot(x0, p0), dot(x1, p1), dot(x2, p2), dot(x3, p3)), 0.0);
  m = m * m;
  return 42.0 * dot( m*m, vec4( dot(p0,x0), dot(p1,x1), dot(p2,x2), dot(p3,x3) ) );
}
```

### Worley / Voronoi Noise

```glsl
vec2 random2D(vec2 p) {
  p = vec2(dot(p, vec2(127.1, 311.7)),
           dot(p, vec2(269.5, 183.3)));
  return -1.0 + 2.0 * fract(sin(p) * 43758.5453123);
}

float worley(vec2 p) {
  vec2 n = floor(p);
  vec2 f = fract(p);

  float minDist = 8.0;

  for(int j = -1; j <= 1; j++) {
    for(int i = -1; i <= 1; i++) {
      vec2 neighbor = vec2(float(i), float(j));
      vec2 point = random2D(n + neighbor);
      vec2 diff = neighbor + point - f;
      float dist = length(diff);
      minDist = min(minDist, dist);
    }
  }

  return minDist;
}
```

### Fractal Brownian Motion (fBm)

```glsl
float fbm(vec2 st, int octaves, float persistence, float lacunarity) {
  float value = 0.0;
  float amplitude = 1.0;
  float frequency = 1.0;
  float maxValue = 0.0;

  for(int i = 0; i < octaves; i++) {
    value += amplitude * simplexNoise2D(st * frequency);
    maxValue += amplitude;
    amplitude *= persistence;
    frequency *= lacunarity;
  }

  return value / maxValue;
}

// Typical usage
float pattern = fbm(vUv, 6, 0.5, 2.0);
```

### Domain Warping with Noise

```glsl
float domainWarp(vec2 st) {
  vec2 warp = vec2(simplexNoise2D(st), simplexNoise2D(st + 5.2));

  return simplexNoise2D(st + warp * 0.3);
}
```

### Ridge Noise (Good for Mountains)

```glsl
float ridge(float h, float offset) {
  h = offset - abs(h);
  return h * h;
}

float ridgeNoise(vec2 st, int octaves) {
  float value = 0.0;
  float amplitude = 1.0;
  float frequency = 1.0;
  float offset = 1.0;

  for(int i = 0; i < octaves; i++) {
    value += amplitude * ridge(simplexNoise2D(st * frequency), offset);
    amplitude *= 0.5;
    frequency *= 2.0;
  }

  return value;
}
```

---

## Shader Resources {#shader-resources}

### Key References and Documentation

**Official Documentation:**
- [Khronos GLSL Specification](https://www.khronos.org/opengl/wiki/OpenGL_Shading_Language)
- [OpenGL Wiki - Data Types](https://www.khronos.org/opengl/wiki/Data_Type_(GLSL))
- [Three.js Documentation](https://threejs.org/docs/)
- [Three.js Uniform Types](https://threejs.org/manual/en/uniform-types.html)

**Learning Resources:**
- [The Book of Shaders](https://thebookofshaders.com/) - Interactive shader tutorials by Patricio Gonzalez Vivo
- [LearnOpenGL](https://learnopengl.com/) - Comprehensive graphics programming guide
- [Aerotwist Shader Tutorials](https://aerotwist.com/tutorials/an-introduction-to-shaders-part-1/)
- [Ronja's Tutorials](https://www.ronja-tutorials.com/) - Individual shader technique tutorials
- [3D Game Shaders For Beginners](https://lettier.github.io/3d-game-shaders-for-beginners/)

**Noise Implementation References:**
- [Simplex/Perlin Noise - GitHub](https://gist.github.com/patriciogonzalezvivo/670c22f3966e662d2f83)
- [webgl-noise by Stefan Gustavson](https://github.com/stegu/webgl-noise)
- [Ashima Noise Library](https://github.com/ashima/webgl-noise)

**PBR and Advanced Techniques:**
- [LearnOpenGL PBR Theory](https://learnopengl.com/PBR/Theory)
- [Graphics Compendium - Cook-Torrance](https://graphicscompendium.com/gamedev/15-pbr)
- [Real-Time Subsurface Scattering Introduction](https://therealmjp.github.io/posts/sss-intro/)

**Interactive Playgrounds:**
- [ShaderToy](https://www.shadertoy.com/) - Online shader gallery and editor
- [GLSL Sandbox](http://glslsandbox.com/) - Browser-based GLSL sandbox
- [VertexShaderArt](https://www.vertexshaderart.com/) - Vertex shader art gallery

**Three.js Specific:**
- [Three.js ShaderMaterial Documentation](https://threejs.org/docs/pages/ShaderMaterial.html)
- [Three.js Shader Chunks](https://github.com/mrdoob/three.js/tree/dev/src/renderers/shaders/ShaderChunk)
- [DEV Community - Three.js Shaders](https://dev.to/maniflames/creating-a-custom-shader-in-threejs-3bhi)

**Books and Papers:**
- "Real-Time Rendering" by Akenine-Möller et al. - Industry standard reference
- "GPU Gems" series - Advanced GPU techniques
- "SIGGRAPH 2013 - Real Shading in Unreal Engine 4" - PBR foundation paper

### Tools and Utilities

**Shader Debugging:**
- Chrome DevTools - WebGL inspector
- RenderDoc - GPU frame debugging
- GLSL Sandbox - Inline shader testing
- Spector.js - WebGL debugging tool

**Optimization Tools:**
- GLSL Optimizer - Shader code optimization
- ANGLE - Shader compiler analysis
- GPUBench - Shader performance testing

**Asset Generation:**
- Substance Designer - Procedural texture generation
- Noisebrew - Procedural noise generator
- LYGIA - Shader library functions (https://lygia.xyz/)

---

## Conclusion

This reference covers the essential GLSL techniques for WebGL and Three.js shader development. Key takeaways:

1. **Master the fundamentals** - Understand data types, qualifiers, and how Three.js injects uniforms
2. **Optimize early** - Avoid branching, minimize texture lookups, use appropriate precision
3. **Leverage noise** - Procedural techniques unlock infinite variation without texture storage
4. **Study examples** - ShaderToy, Three.js examples, and academic papers provide implementation patterns
5. **Profile your shaders** - Use browser DevTools to identify bottlenecks
6. **Build a library** - Create reusable functions and store implementations for future projects

For production use, always test on target hardware, measure performance, and optimize based on real profiling data rather than assumptions.
