# GLSL Noise Function Library

Complete, production-ready noise implementations. Copy any function directly into your shaders.

## Helper Functions (Required for all noise types)

```glsl
// Fast pseudo-random using sine
float random(vec2 st) {
  return fract(sin(dot(st, vec2(12.9898, 78.233))) * 43758.5453123);
}

// 2D random returning vec2
vec2 random2D(vec2 st) {
  st = vec2(dot(st, vec2(127.1, 311.7)),
            dot(st, vec2(269.5, 183.3)));
  return -1.0 + 2.0 * fract(sin(st) * 43758.5453123);
}

// 3D random
float random3D(vec3 st) {
  return fract(sin(dot(st, vec3(12.9898, 78.233, 45.164))) * 43758.5453123);
}

// Smoothstep interpolation (use for noise)
float smoothstep(float t) {
  return t * t * (3.0 - 2.0 * t);
}

// Mod and permutation for Simplex/Perlin
vec3 mod289(vec3 x) { return x - floor(x * (1.0 / 289.0)) * 289.0; }
vec2 mod289(vec2 x) { return x - floor(x * (1.0 / 289.0)) * 289.0; }
vec3 permute(vec3 x) { return mod289(((x * 34.0) + 1.0) * x); }
float permute(float x) { return mod289(((x * 34.0) + 1.0) * x); }

// Fade function for Perlin noise
vec3 fade(vec3 t) { return t * t * t * (t * (t * 6.0 - 15.0) + 10.0); }
```

---

## Perlin 2D Noise

Classic Perlin noise, good all-purpose noise:

```glsl
float perlin2D(vec2 st) {
  vec2 i = floor(st);
  vec2 f = fract(st);
  
  // Smooth interpolation curve
  vec2 u = f * f * (3.0 - 2.0 * f);
  
  // Sample corner values
  float a = random(i);
  float b = random(i + vec2(1.0, 0.0));
  float c = random(i + vec2(0.0, 1.0));
  float d = random(i + vec2(1.0, 1.0));
  
  // Interpolate
  float lowerMix = mix(a, b, u.x);
  float upperMix = mix(c, d, u.x);
  
  return mix(lowerMix, upperMix, u.y);
}
```

**Usage:**
```glsl
float noise = perlin2D(vUv * 5.0);  // Scale controls frequency
noise = noise * 0.5 + 0.5;  // Remap from -1..1 to 0..1
gl_FragColor = vec4(vec3(noise), 1.0);
```

---

## Perlin 3D Noise

3D variant for volumetric effects:

```glsl
float perlin3D(vec3 st) {
  vec3 i = floor(st);
  vec3 f = fract(st);
  
  vec3 u = f * f * (3.0 - 2.0 * f);
  
  // 8 corner values
  float a = random3D(i);
  float b = random3D(i + vec3(1.0, 0.0, 0.0));
  float c = random3D(i + vec3(0.0, 1.0, 0.0));
  float d = random3D(i + vec3(1.0, 1.0, 0.0));
  float e = random3D(i + vec3(0.0, 0.0, 1.0));
  float f = random3D(i + vec3(1.0, 0.0, 1.0));
  float g = random3D(i + vec3(0.0, 1.0, 1.0));
  float h = random3D(i + vec3(1.0, 1.0, 1.0));
  
  // Interpolate Z layer
  float ab = mix(a, b, u.x);
  float cd = mix(c, d, u.x);
  float ef = mix(e, f, u.x);
  float gh = mix(g, h, u.x);
  
  float abcd = mix(ab, cd, u.y);
  float efgh = mix(ef, gh, u.y);
  
  return mix(abcd, efgh, u.z);
}
```

---

## Simplex 2D Noise

Faster than Perlin, better gradient distribution:

```glsl
float simplex2D(vec2 v) {
  const vec4 C = vec4(0.211324865405187, 0.366025403784439,
                      -0.577350269189626, 0.024390243902439);
  
  vec2 i = floor(v + dot(v, C.yy));
  vec2 x0 = v - i + dot(i, C.xx);
  
  vec2 i1 = (x0.x > x0.y) ? vec2(1.0, 0.0) : vec2(0.0, 1.0);
  vec4 x12 = x0.xyxy + C.xxzz;
  x12.xy -= i1;
  
  i = mod289(i);
  vec3 p = permute(permute(i.y + vec3(0.0, i1.y, 1.0)) + 
                   i.x + vec3(0.0, i1.x, 1.0));
  
  vec3 m = max(0.5 - vec3(dot(x0, x0), dot(x12.xy, x12.xy),
                           dot(x12.zw, x12.zw)), 0.0);
  m = m * m;
  m = m * m;
  
  vec3 x = 2.0 * fract(p * C.www) - 1.0;
  vec3 h = abs(x) - 0.5;
  vec3 ox = floor(x + 0.5);
  vec3 sx = sign(x);
  vec3 sh = step(h, vec3(0.0));
  vec3 a0 = sx * vec3(sh.x, sh.y, sh.z) + 
            vec3(1.0 - sh.x, 1.0 - sh.y, 1.0 - sh.z);
  
  vec3 p0 = vec3(x0.xy, h.x);
  vec3 p1 = vec3(x12.xy, h.y);
  vec3 p2 = vec3(x12.zw, h.z);
  
  vec3 g0 = normalize(p0);
  vec3 g1 = normalize(p1);
  vec3 g2 = normalize(p2);
  
  float n0 = dot(g0, p0);
  float n1 = dot(g1, p1);
  float n2 = dot(g2, p2);
  
  vec3 fade_xyz = fade(vec3(x0.xy, h.x));
  vec3 n_xyz = mix(vec3(n0), vec3(n1), fade_xyz.z);
  n_xyz = mix(n_xyz, vec3(n2), fade_xyz.y);
  
  return 2.2 * mix(n_xyz.x, n_xyz.y, fade_xyz.x);
}
```

---

## Simplex 3D Noise

Fast 3D noise for volumetric effects:

```glsl
float simplex3D(vec3 v) {
  const vec2 C = vec2(1.0 / 6.0, 1.0 / 3.0);
  
  vec3 i = floor(v + dot(v, C.yyy));
  vec3 x0 = v - i + dot(i, C.xxx);
  
  vec3 g = step(x0.yzx, x0.xyz);
  vec3 l = 1.0 - g;
  vec3 i1 = min(g.xyz, l.zxy);
  vec3 i2 = max(g.xyz, l.zxy);
  
  vec3 x1 = x0 - i1 + C.xxx;
  vec3 x2 = x0 - i2 + C.yyy;
  vec3 x3 = x0 - 0.5;
  
  i = mod289(i);
  vec4 p = permute(permute(permute(i.z + vec4(0.0, i1.z, i2.z, 1.0))
            + i.y + vec4(0.0, i1.y, i2.y, 1.0))
            + i.x + vec4(0.0, i1.x, i2.x, 1.0));
  
  float n_ = 0.142857142857;
  vec3 ns = n_ * vec3(3.0, 2.0, 1.0) - vec3(2.0, 1.0, 0.0);
  vec4 j = p - 49.0 * floor(p * ns.z * ns.z);
  
  vec4 x_ = floor(j * ns.z);
  vec4 y_ = floor(j - 7.0 * x_);
  
  vec4 x = x_ * ns.x + ns.yyyy;
  vec4 y = y_ * ns.x + ns.yyyy;
  vec4 h = 1.0 - abs(x) - abs(y);
  
  vec4 b0 = vec4(x.xy, y.xy);
  vec4 b1 = vec4(x.zw, y.zw);
  
  vec4 s0 = floor(b0) * 2.0 + 1.0;
  vec4 s1 = floor(b1) * 2.0 + 1.0;
  vec4 sh = -step(h, vec4(0.0));
  
  vec4 a0 = b0.xzyw + s0.xzyw * sh.xxyy;
  vec4 a1 = b1.xzyw + s1.xzyw * sh.zzww;
  
  vec3 p0 = vec3(a0.xy, h.x);
  vec3 p1 = vec3(a0.zw, h.y);
  vec3 p2 = vec3(a1.xy, h.z);
  vec3 p3 = vec3(a1.zw, h.w);
  
  vec4 norm = inversesqrt(vec4(dot(p0, p0), dot(p1, p1), 
                               dot(p2, p2), dot(p3, p3)));
  p0 *= norm.x;
  p1 *= norm.y;
  p2 *= norm.z;
  p3 *= norm.w;
  
  vec4 m = max(0.6 - vec4(dot(x0, x0), dot(x1, x1), 
                          dot(x2, x2), dot(x3, x3)), 0.0);
  m = m * m;
  return 42.0 * dot(m * m, vec4(dot(p0, x0), dot(p1, x1),
                                 dot(p2, x2), dot(p3, x3)));
}
```

---

## Worley/Voronoi Noise

Cellular patterns, good for cracks, scales:

```glsl
float worleyNoise(vec2 p) {
  vec2 n = floor(p);
  vec2 f = fract(p);
  
  float minDist = 8.0;
  vec2 closestPoint = vec2(0.0);
  
  for (int y = -1; y <= 1; y++) {
    for (int x = -1; x <= 1; x++) {
      vec2 neighbor = vec2(float(x), float(y));
      vec2 point = random2D(n + neighbor);
      
      vec2 diff = neighbor + point - f;
      float dist = length(diff);
      
      if (dist < minDist) {
        minDist = dist;
        closestPoint = neighbor + point;
      }
    }
  }
  
  return minDist;
}
```

---

## Fractal Brownian Motion (fBm)

Layer multiple octaves for natural patterns:

```glsl
float fbm(vec2 st, int octaves) {
  float value = 0.0;
  float amplitude = 0.5;
  float frequency = 1.0;
  float maxValue = 0.0;
  
  for (int i = 0; i < octaves; i++) {
    value += amplitude * simplex2D(st * frequency);
    maxValue += amplitude;
    amplitude *= 0.5;
    frequency *= 2.0;
  }
  
  return value / maxValue;
}

float fbm3D(vec3 st, int octaves) {
  float value = 0.0;
  float amplitude = 0.5;
  float frequency = 1.0;
  float maxValue = 0.0;
  
  for (int i = 0; i < octaves; i++) {
    value += amplitude * simplex3D(st * frequency);
    maxValue += amplitude;
    amplitude *= 0.5;
    frequency *= 2.0;
  }
  
  return value / maxValue;
}
```

**Usage:**
```glsl
float noise = fbm(vUv, 5);  // 5 octaves for natural detail
```

---

## Ridge Noise

Inverted fBm for sharp peaks:

```glsl
float ridgeNoise(vec2 st, int octaves) {
  float value = 0.0;
  float amplitude = 0.5;
  float frequency = 1.0;
  float maxValue = 0.0;
  
  for (int i = 0; i < octaves; i++) {
    float n = simplex2D(st * frequency);
    n = abs(n);  // Invert valleys
    n = 1.0 - n;  // Ridge effect
    
    value += amplitude * n;
    maxValue += amplitude;
    amplitude *= 0.5;
    frequency *= 2.0;
  }
  
  return value / maxValue;
}
```

---

## Domain Warping

Distort coordinates for swirling effects:

```glsl
float domainWarp(vec2 p) {
  vec2 q = vec2(fbm(p + vec2(0.0, 0.0), 4),
                 fbm(p + vec2(5.2, 1.3), 4));
  
  vec2 r = vec2(fbm(p + 4.0 * q + vec2(1.7, 9.2), 4),
                 fbm(p + 4.0 * q + vec2(8.3, 2.8), 4));
  
  return fbm(p + 4.0 * r, 4);
}
```

---

## Turbulence

Chaotic, swirling patterns:

```glsl
float turbulence(vec2 p) {
  float value = 0.0;
  float amplitude = 1.0;
  float frequency = 1.0;
  
  for (int i = 0; i < 6; i++) {
    value += amplitude * abs(simplex2D(p * frequency));
    amplitude *= 0.5;
    frequency *= 2.0;
  }
  
  return value;
}
```

---

## Practical Usage Examples

### Clouds
```glsl
vec3 clouds(vec2 uv, float time) {
  float cloud = fbm(uv + time * 0.1, 5);
  cloud = smoothstep(0.3, 0.7, cloud);
  return vec3(cloud);
}
```

### Marble
```glsl
float marble(vec3 p) {
  float noise = fbm(p.xy * 3.0, 5);
  return sin(p.z * 5.0 + noise * 10.0);
}
```

### Rust/Weathering
```glsl
float rust(vec3 p) {
  float base = fbm(p.xy * 2.0, 4);
  float detail = fbm(p.xy * 8.0, 3);
  return mix(base, detail, 0.5);
}
```

### Wood Grain
```glsl
float wood(vec3 p) {
  float rings = sin(length(p.xz) * 20.0);
  float grain = fbm(p.xz * 3.0, 4);
  return rings * 0.5 + grain * 0.5;
}
```

### Terrain Height
```glsl
float terrain(vec2 uv) {
  return fbm(uv * 0.5, 6) * 0.5 + 
         fbm(uv * 2.0, 4) * 0.3 +
         fbm(uv * 8.0, 2) * 0.2;
}
```
