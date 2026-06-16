# Environment Art — Art Direction & Three.js Implementation

## Space Environments

### Nebulae and Gas Clouds

**Art Direction**:
- Rendered as volumetric fog layers, not detailed geometry. Multiple transparency layers create depth.
- Color: Purples (Orion), blues/teals (emission nebula), deep crimsons (star-forming regions). Avoid saturated greens (too fantasy).
- Lighting interaction: Nebula glows faintly, illuminates nearby geometry subtly.
- Vast scale: Distant clouds fade, foreground clouds show structure.

**Three.js Implementation Sketch**:
```typescript
// Nebula background using fog + emissive planes
const nebulaMaterial = new THREE.MeshBasicMaterial({
  map: nebulaTex,
  emissive: 0x441166,
  emissiveMap: nebulaTex,
  emissiveIntensity: 0.4
});
const nebulaMesh = new THREE.Mesh(new THREE.PlaneGeometry(1000, 1000), nebulaMaterial);
scene.add(nebulaMesh);

// Volumetric effect with fog
scene.fog = new THREE.FogExp2(0x020612, 0.0008); // dark space, subtle fog

// Foreground nebula particles for detail
const nebulaParticles = new THREE.Points(particleGeometry, particleMaterial);
```

**Performance**: Single 2K volumetric texture, 2–3 particle emitters per nebula region max.

---

### Asteroid Fields

**Art Direction**:
- Mix of modular asteroids (4–8 unique variations) and scattered smaller rocks.
- Surface: Dark basalt grays (RGB ~0.25), occasional lighter silicates (RGB ~0.45). Crater and fracture normal maps essential.
- Lighting: Harsh, rim-lit. Space rocks catch deep shadows. Simulate solar direction with strong key light.
- Scale communication: Asteroid belt looks vast only if distant asteroids fade into fog. Close asteroids read scale; distant ones fade at ~500m.

**Three.js Implementation Sketch**:
```typescript
// Asteroid material: PBR with weathered basalt
const asteroidMaterial = new THREE.MeshStandardMaterial({
  color: 0x3d3d3d,
  metalness: 0.1,
  roughness: 0.85,
  normalMap: craterNormalMap,
  normalScale: new THREE.Vector2(1.5, 1.5)
});

// Directional light for harsh shadows
const sunLight = new THREE.DirectionalLight(0xffffff, 2.0);
sunLight.position.set(50, 30, 40);
sunLight.castShadow = true;
scene.add(sunLight);

// Fog to fade distant asteroids
scene.fog = new THREE.FogExp2(0x0a0e1a, 0.0005);

// Instanced rendering for large asteroid counts
const asteroids = new THREE.InstancedMesh(asteroidGeometry, asteroidMaterial, 10000);
// ... position each instance
```

---

### Orbital Stations

**Art Direction**:
- Modular design: radiator panels, docking collars, antenna arrays, solar panel wings.
- Silhouette priority: Players recognize station type (refinery vs research vs military) from shape alone.
- Materials: Anodized aluminum primary, carbon composite secondary, dark thermal radiators, reflective windows.
- Scale: Solar panel wing spans ~100m. Individual panels ~5m×10m. Docking clamps show engineering detail.

**Three.js Implementation Sketch**:
```typescript
// Station hull: brushed aluminum
const hullMaterial = new THREE.MeshStandardMaterial({
  color: 0x888888,
  metalness: 0.85,
  roughness: 0.4,
  normalMap: brushedAluminumNormal
});

// Radiator panels: matte black composites
const radiatorMaterial = new THREE.MeshStandardMaterial({
  color: 0x0a0a0a,
  metalness: 0.0,
  roughness: 0.95,
  emissive: 0x220000,
  emissiveIntensity: 0.1 // waste heat glow
});

// Windows with slight blue tint
const windowMaterial = new THREE.MeshPhysicalMaterial({
  color: 0xc0d8e8,
  transmission: 0.8,
  roughness: 0.05,
  ior: 1.5
});

// Assembled from modular pieces, each with appropriate material
```

---

### Ship Exteriors

**Art Direction**:
- Hull plating: large panels (2m×3m+) with visible seams and rivets. Seams don't need geometry—normal map detail sufficient.
- Wear pattern: Leading edge (nose cone, solar panel edges) shows micrometeorite scarring. Trailing edge clean.
- Thrusters: Glowing nozzles, visible heat distortion around exhaust.
- Windows: Slightly tinted, slightly reflective (10–20% reflectance). Show interior lights behind.

**Three.js Implementation Sketch**:
```typescript
// Hull panel with macro + micro detail
const hullMaterial = new THREE.MeshStandardMaterial({
  color: 0x505050,
  metalness: 0.9,
  roughness: 0.35,
  normalMap: hullNormalMap, // panel seams + micro-scratches
  aoMap: hullAOMap
});

// Thruster glow: emissive plane + particle effect
const thrusterGlow = new THREE.MeshBasicMaterial({
  color: 0xff6600,
  emissive: 0xff6600,
  emissiveIntensity: 2.0,
  toneMapped: false
});

// Particle system for thruster exhaust
const thrusterParticles = createThrusterVFX(thrusterPosition, direction);
```

---

## Planetary Surfaces

### Barren Rock Worlds

**Art Direction**:
- Terrain: Sculpted, cratered, angular. Avoid smooth rolling hills (unrealistic for small bodies).
- Material: Regolith (powdered rock aggregate). Normal map shows fine detail. Albedo ~0.4–0.5 (darker than sand).
- Color variation: Basalt-dominant (dark gray), minor iron oxide (rust red), occasional lighter mineral outcrops (tan, light gray).
- Lighting: No atmosphere = hard shadows. Horizon sharp and distant. Sky black (space).

**Three.js Implementation Sketch**:
```typescript
// Terrain shader with regolith detail
const terrainMaterial = new THREE.ShaderMaterial({
  uniforms: {
    baseColor: { value: new THREE.Color(0.45, 0.42, 0.40) },
    regolithNormal: { value: regolithTexture },
    craterNormal: { value: craterTexture }
  },
  vertexShader: terrainVS,
  fragmentShader: terrainFS,
  side: THREE.DoubleSide
});

// Hard shadows with directional light
const sunLight = new THREE.DirectionalLight(0xffffff, 2.5);
sunLight.position.set(1, 2, 1).normalize().multiplyScalar(50);
sunLight.castShadow = true;
sunLight.shadow.mapSize.set(2048, 2048);
scene.add(sunLight);

// Black sky, no atmospheric fog
scene.background = new THREE.Color(0x000000);
scene.fog = null;
```

---

### Atmospheric Worlds

**Art Direction**:
- Sky gradient: Close to surface (thin atmosphere), fade from blue/gray to starfield at top.
- Fog: Atmospheric haze at far distance (3–5km). Volumetric fog layer, slightly colored.
- Water: Reflective, captures sky. Foam at shorelines (particle spray, white froth).
- Vegetation (if habitable): Sparse, engineered. Avoid Earth-like jungle.

**Three.js Implementation Sketch**:
```typescript
// Atmosphere fog
scene.fog = new THREE.FogExp2(0x87ceeb, 0.0002); // light blue, thin

// Water shader with reflection/refraction
const waterMaterial = new THREE.ShaderMaterial({
  uniforms: {
    tDudv: { value: dudvMap },
    tNormal: { value: waterNormalMap },
    tReflection: { value: reflectionTexture }
  },
  vertexShader: waterVS,
  fragmentShader: waterFS
});

// Sky with gradient
const skyGeometry = new THREE.SphereGeometry(5000, 32, 32);
const skyMaterial = new THREE.ShaderMaterial({
  uniforms: {
    topColor: { value: new THREE.Color(0x001a4d) },
    bottomColor: { value: new THREE.Color(0x87ceeb) }
  },
  vertexShader: skyVS,
  fragmentShader: skyFS,
  side: THREE.BackSide
});
const sky = new THREE.Mesh(skyGeometry, skyMaterial);
scene.add(sky);
```

---

### Geological Features

**Art Direction**:
- Canyons: Strata visible in cliff walls. Layer materials (darker stone below, lighter above).
- Volcanoes: Dormant crater (dark rock rim), lava flows with glossy emissive glow.
- Ice formations: White/pale blue, translucent. Crevasses cast deep shadows.

**Three.js Implementation Sketch**:
```typescript
// Stratified canyon walls
const canyonMaterial = new THREE.ShaderMaterial({
  uniforms: {
    strataColors: { value: [darkStone, midStone, lightStone] },
    strataHeights: { value: [0, 0.3, 0.7] }
  },
  vertexShader: strataVS,
  fragmentShader: strataFS
});

// Lava with emissive glow
const lavaMaterial = new THREE.MeshStandardMaterial({
  color: 0x880000,
  metalness: 0.3,
  roughness: 0.7,
  emissive: 0xff4400,
  emissiveMap: lavaFlowMap,
  emissiveIntensity: 1.5
});

// Ice with translucency
const iceMaterial = new THREE.MeshPhysicalMaterial({
  color: 0xd4e5f7,
  transmission: 0.6,
  roughness: 0.1,
  thickness: 2.0,
  metalness: 0.0
});
```

---

## Interior Spaces

### Factory Floors

**Art Direction**:
- Volume: High ceilings (8–12m). Open sightlines. Machinery visible at distance.
- Layout: Orthogonal. Catwalks, scaffolding, modular workstations. Assembly lines visible and readable.
- Lighting: Overhead industrial rigs (tungsten-white, high-contrast shadows). Occasional machinery glow.
- Materials: Concrete flooring, steel support beams, corrugated metal walls.

**Three.js Implementation Sketch**:
```typescript
// Overhead industrial lighting
const mainLight = new THREE.DirectionalLight(0xfffacd, 1.8); // warm white
mainLight.position.set(0, 8, 5);
mainLight.castShadow = true;
mainLight.shadow.mapSize.set(2048, 2048);
mainLight.shadow.camera.left = -50;
mainLight.shadow.camera.right = 50;
mainLight.shadow.camera.top = 50;
mainLight.shadow.camera.bottom = -50;
scene.add(mainLight);

// Accent machinery glow
const machineryLight = new THREE.PointLight(0x00ff00, 0.6);
machineryLight.position.set(20, 4, 10);
machineryLight.range = 30;
scene.add(machineryLight);

// Concrete floor material
const floorMaterial = new THREE.MeshStandardMaterial({
  color: 0x6b6b6b,
  roughness: 0.85,
  metalness: 0.0,
  normalMap: concreteNormal,
  aoMap: concreteAO
});

// Steel beam material
const beamMaterial = new THREE.MeshStandardMaterial({
  color: 0x404040,
  roughness: 0.5,
  metalness: 0.8,
  normalMap: steelNormal
});
```

---

### Hab Modules

**Art Direction**:
- Atmosphere: Lived-in warmth. Warmer lighting (3000–3500K). Slightly dim (power-saving narrative).
- Layout: Modular sections—bunk area, common area, galley. Compact, efficient.
- Materials: Polymer wall panels (satin finish), rubber flooring, aluminum trim.
- Variation: Worn edges, scuffed walls (micro-details in normal map). Personality through posters, clutter.

**Three.js Implementation Sketch**:
```typescript
// Warm, soft lighting for comfort
const habLight = new THREE.DirectionalLight(0xffffcc, 1.2); // warm white
habLight.position.set(-2, 3, 3);
scene.add(habLight);

const habFillLight = new THREE.PointLight(0xffddaa, 0.5);
habFillLight.position.set(0, 2.5, -2);
scene.add(habFillLight);

// Polymer wall material (satin)
const wallMaterial = new THREE.MeshStandardMaterial({
  color: 0xe8e8e0,
  roughness: 0.4,
  metalness: 0.0,
  normalMap: polymerNormal
});

// Rubber flooring (grippy, worn)
const floorMaterial = new THREE.MeshStandardMaterial({
  color: 0x333333,
  roughness: 0.9,
  metalness: 0.0,
  normalMap: rubberWearNormal
});

// Warm color grading
const colorGradePass = new THREE.ColorGradingPass({
  warmth: 0.2,
  saturation: 0.95
});
```

---

### Command Centers

**Art Direction**:
- Focal point: Central display (holo-projection or screen wall). Ring of workstations around it.
- Lighting: Cool to neutral (4500K). Accent lighting from displays. High-contrast edges.
- Materials: Matte black panels (zero reflectance), brushed aluminum trim, dark composites.
- Readability: Terminals show active (glow), idle (dim), offline (dark).

**Three.js Implementation Sketch**:
```typescript
// Cool, neutral overhead lighting
const commandLight = new THREE.DirectionalLight(0xffffff, 1.5);
commandLight.position.set(0, 4, 0);
scene.add(commandLight);

// Display panel lighting (accent)
const displayLight = new THREE.PointLight(0x0088ff, 0.8);
displayLight.position.set(0, 2, 2);
displayLight.range = 15;
scene.add(displayLight);

// Matte black panel material
const panelMaterial = new THREE.MeshStandardMaterial({
  color: 0x0a0a0a,
  roughness: 1.0,
  metalness: 0.0,
  emissive: 0x001a3a
});

// Active terminal: bright glow
const activeTerminal = new THREE.MeshStandardMaterial({
  color: 0x00ff00,
  emissive: 0x00ff00,
  emissiveIntensity: 1.2
});

// Idle terminal: dim
const idleTerminal = new THREE.MeshStandardMaterial({
  color: 0x003300,
  emissive: 0x001100,
  emissiveIntensity: 0.2
});
```

---

### Corridors

**Art Direction**:
- Design: Narrower (2–3m width). Modular construction visible (wall seams every 2m). Cargo runs along base.
- Lighting: Linear strip lights (ceiling and/or edge glow). Directional, guide player motion.
- Materials: Composite walls (neutral, matte), stainless steel handrails, viewports at intervals.
- Variation: Hazard tape at door frames, worn floor plating at high-traffic zones.

**Three.js Implementation Sketch**:
```typescript
// Linear strip lighting (multiple point lights along corridor)
for (let i = 0; i < 10; i++) {
  const stripLight = new THREE.PointLight(0xffffff, 1.0);
  stripLight.position.set(0, 2.3, i * 5);
  stripLight.range = 8;
  scene.add(stripLight);
}

// Composite wall material
const corridorWallMaterial = new THREE.MeshStandardMaterial({
  color: 0x707070,
  roughness: 0.7,
  metalness: 0.0,
  normalMap: compositeNormal
});

// Handrail: brushed stainless
const handrailMaterial = new THREE.MeshStandardMaterial({
  color: 0xc0c0c0,
  roughness: 0.3,
  metalness: 0.95,
  normalMap: brushedMetalNormal
});

// Worn floor at high-traffic zones (procedural or decal)
const wornFloorDecal = new THREE.MeshStandardMaterial({
  color: 0x505050,
  roughness: 0.95,
  normalMap: wearNormal
});
```

---

## Architectural Language

**Modular Construction**: Every structure = assembly of repeating units. Seams matter. Visible panel edges, bolted connections, gap-line details (use decals or normal map bevels). Assembly order visible: newer sections look less weathered.

**Prefab Aesthetics**: Symmetry and regularity. Grids and arrays. Minimal custom-cut geometry. Repeat tiles where possible: 2m×2m wall sections, 1m risers, standard door frames.

**Functional Visibility**: Conduits, pipes, and cables semi-visible (use trim detail). Radiators and heat dissipation: Large fins, vaned surfaces. Structural support: Bracing visible, especially under load-bearing spans.

---

## Prop Design Philosophy

**Every Object Tells a Story**: A lever controls something specific. A control panel has readable buttons/switches. Tools scattered in workspace show wear patterns.

**Material Purpose**:
- Handles: higher roughness, slight color wear
- Wear points: exposed, darkened (corners of doors)
- Clean points: protected areas (interior edges, protected switches)

**Scale Hierarchy**:
- Large props (300+cm): Macro detail (seams, divisions), macro material variety
- Medium props (50–300cm): Seams + micro detail (normal map wear), 1–2 material types
- Small props (<50cm): Primarily normal map detail, single material

---

## Atmosphere and Mood

**Through Lighting**:
- Operational spaces: Hard key light, high contrast, cool color (4500–5500K). Conveys efficiency.
- Hab modules: Warm key light (3000–3500K), softer fill light. Conveys comfort.
- Emergency: Red wash. Conveys urgency.
- Discovery: Soft, cool backlighting (deep blue), cinematic rim light. Conveys wonder.

**Through Particles & Post-Processing**:
- Dust: Volumetric fog with particle spray in industrial spaces.
- Haze: Atmospheric fog at distance. Creates sense of scale, depth.
- Bloom: Subtle on bright surfaces. Avoid blooming beyond object bounds.
- Grading: Cold for alien worlds, neutral for stations, warm for hab spaces.

**Through Occlusion**:
- Distant mountains/structures fade into fog, not crisply rendered.
- Shadowed alcoves feel unlit, mysterious.
- Interior spaces feel enclosed (ceiling/walls visible).

---

## Scale Communication

**Making Vast Spaces Feel Vast**:
- Distance fog essential: Object becomes silhouette at ~2–5km.
- Repetition: Hundreds of distant rocks, repeated structures at horizon.
- Comparative props: Place human figures or small objects next to giant engineering.
- Low camera angle: Player positioned low amplifies height/scale.

**Making Small Spaces Feel Intimate**:
- Visible ceiling/walls close (≤10m). Enclosed feeling.
- Clutter and detail: More objects per m², higher material variety.
- Warm lighting, soft shadows. Coziness, safety.
