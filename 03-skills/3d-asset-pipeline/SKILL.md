---
name: 3d-asset-pipeline
description: >
  Export, optimization, and engine integration for 3D assets. Use this skill whenever
  the conversation touches: FBX, glTF, GLB, USDZ, OBJ, Alembic, file format choice,
  glTF schema, glTF extensions, KHR_draco_mesh_compression, Draco compression,
  gltf-validator, GLTFLoader, DRACOLoader, KTX2Loader, normal map baking, high-poly
  to low-poly baking, ray distance, bake cage, tangent space normal map, object space
  normal map, Marmoset baking, Substance Painter baking, xNormal, normal map seams,
  LOD generation, Decimate modifier, Simplygon, screen-space LOD, Unreal Nanite,
  texture export, power of two texture dimensions, BC1, BC3, BC5, BC7, DXT, ASTC,
  KTX2, Basis Universal, mipmap, engine import, Unreal Engine import settings, Unity
  import settings, skeletal mesh import, FBX unit mismatch, scale issue, flipped
  normals, asset validation, zero-scale transforms, UV overlaps, non-manifold geometry,
  degenerate faces, or any question about getting a 3D asset from a DCC tool into an
  engine correctly. This skill covers the handoff from 3D application to game engine —
  not material authoring (3d-materials-shading), shader code (glsl-shader-architect),
  or Three.js implementation (threejs-materials-master).
hub: lead-3d-designer
aliases: [3d-asset-pipeline]
tier: spoke
domain: design
prerequisites: [lead-3d-designer]
spec_version: "2.0"
---

# 3D Asset Pipeline

Specialist lens for the full pipeline from DCC tool to game engine or web renderer —
export, optimization, baking, and engine integration. Part of the `lead-3d-designer`
skill network.

---

## Domain Boundary

This skill owns **the path from DCC to engine** — file format decisions, baking
workflows, LOD generation, texture compression, and engine import validation.

- **Mesh construction, topology** → `3d-modeling-fundamentals`
- **Material authoring, PBR values** → `3d-materials-shading`
- **Lighting setup in engine** → `3d-lighting-rendering`
- **Rig export, animation bake** → `3d-rigging-animation`
- **GLSL shader code** → `glsl-shader-architect`
- **Three.js material implementation** → `threejs-materials-master`
- **LOD design philosophy** → `3d-spatial-design-for-games` (the design decisions);
  this skill covers the generation and technical pipeline

---

## File Formats

### FBX (Filmbox)

The most widely used interchange format for rigged characters and animation. Proprietary
Autodesk format (binary or ASCII); near-universal engine support (Unity, Unreal, Godot),
but not an open standard.

- **When to use**: Rigged characters, animation clips, skeletal mesh data — any asset that
  needs to carry animation or rig data to a game engine.
- **Limitations**: Binary (not human-readable); animation data can degrade across DCC→engine
  round-trips; FBX SDK version differences cause occasional import artifacts.

**FBX quirks to know**:

- **Scale units**: FBX carries a system-unit concept (cm/m/inches). Blender's scene unit is
  **meters**; Unreal imports assuming **centimeters** — so a 1.8 m character arrives at 180
  Unreal units (100× too large). Fix: enable "Apply Scalings → FBX All" on the UE import, or
  set the Blender FBX export scale to 0.01. Blender→Unity (meters): set FBX export scale to 1.0
  with "Apply Unit" on, or set 0.01 in Unity's import scale factor.
- **Apply transforms before export**: Non-unit scale or non-zero rotation in Blender can bake
  into the FBX unpredictably. Always Apply All Transforms (Ctrl+A → All Transforms) first.
- **Bone axes**: Blender uses Y-up along bone length; engines vary. The exporter applies a
  correction transform — verify in-engine that bones point the right way.
- **Smoothing groups**: FBX encodes hard/soft edges as smoothing groups. Select "Edge" (not
  "Face") in Blender's FBX smoothing option — "Face" loses split-normal data.
- **Materials**: FBX exports material *names*, not material data. The engine creates placeholder
  materials with the right names; you assign textures manually after import.

### glTF 2.0 / GLB

The open standard for real-time 3D on the web, increasingly adopted by game engines. JSON-based
schema maintained by the Khronos Group.

- **glTF**: separate files (`.gltf` JSON + `.bin` binary geometry + texture files).
- **GLB**: single binary container (all data packed) — preferred for delivery.
- **When to use**: Web delivery (Three.js, Babylon.js), AR/VR (WebXR, RealityKit), progressive
  loading pipelines, any context where an open standard matters. **Native to Three.js and React
  Three Fiber — the preferred format for Legion's web renderer.**
- **Engine support**: Unreal (native) and Unity (via importer) both import glTF, but it's less
  mature than FBX for animation — verify rig compatibility before committing to glTF for
  character import.
- **Extensions**: PBR materials, compression, transmission, clearcoat, specular, iridescence,
  anisotropy. Supports embedded textures (GLB) or separate (glTF + bin + textures).

**glTF PBR material mapping**:
- `baseColorTexture` → Albedo (sRGB)
- `metallicRoughnessTexture` → G = Roughness, B = Metalness (Linear)
- `normalTexture` → Normal map (OpenGL convention)
- `occlusionTexture` → AO (Linear)
- `emissiveTexture` → Emissive (sRGB)

**glTF export from Blender**: File → Export → glTF 2.0. Enable "Include Materials" (and
"Include Punctual Lights" if needed). The exporter respects Principled BSDF nodes — standard
node setups export correctly.

### glTF Schema Structure

```
Scene
  └── Nodes (transform hierarchy)
        └── Meshes (vertex data, indices)
              └── Materials (PBR metalness/roughness)
                    └── Textures → Images
  └── Skins (skeleton for skinned meshes)
  └── Animations (keyframe data)
  └── Cameras
```

**Key extensions**:

| Extension | Function |
|-----------|---------|
| `KHR_draco_mesh_compression` | Draco compression for vertex data — significant size reduction for web |
| `KHR_materials_unlit` | Unlit shading — no lighting calculation (UI elements, sky) |
| `KHR_materials_transmission` | Glass and transparent material support |
| `KHR_materials_emissive_strength` | HDR emissive values above 1.0 |
| `KHR_texture_basisu` | KTX2/Basis Universal compressed textures within glTF |
| `KHR_lights_punctual` | Point, spot, directional lights embedded in the file |

### gltf-transform

`gltf-transform` is a Node.js CLI and library for post-processing glTF/GLB files:

```bash
# Install
npm install -g @gltf-transform/cli

# Inspect a file
gltf-transform inspect model.glb

# Compress textures to KTX2 with UASTC (high quality) + ETC1S (size-focused)
gltf-transform uastc model.glb model-compressed.glb
gltf-transform etc1s model.glb model-small.glb

# Draco geometry compression
gltf-transform draco model.glb model-draco.glb

# Mesh quantization (reduces vertex data precision for smaller file size)
gltf-transform quantize model.glb model-quantized.glb

# All-in-one optimization
gltf-transform optimize model.glb model-final.glb
```

**For Legion's Three.js pipeline**: use `gltf-transform` as the final step — author in Blender
→ export GLB → run through `gltf-transform` for compression → import into the Three.js scene.
(Full optimization command reference in "glTF Optimization Reference" below.)

### USDZ

Apple's AR delivery format, based on Pixar's Universal Scene Description (USD).

- **When to use**: iOS AR (ARKit, Reality Composer, QuickLook), web AR on Safari, Apple-ecosystem
  integration.
- **Limitations**: limited material feature support vs. glTF; not suitable for complex rigged
  characters in real-time engines.
- **Export from Blender**: the bundled USD Exporter (3.x+), or export glTF → convert with
  `usd-from-gltf` (Khronos) or Reality Composer.
- USD (without the Z) is the emerging VFX/animation interchange format — DCC tools (Blender,
  Maya, Houdini) increasingly support USD import/export for pipeline interchange.

### OBJ

Legacy geometry-only format.

- ASCII text, universally supported, no animation, no embedded materials (separate `.mtl`
  file for material references, often breaks on import).
- **When to use**: quick geometry transfer when animation/materials don't matter; reference
  meshes for baking; CAD conversions.
- **Do not use** for any asset that needs to reach a game engine in production.

### Alembic (.abc)

Vertex-cache animation format.

- Stores per-frame vertex positions — no bones, no skinning. The mesh deforms by replaying
  raw vertex positions.
- **When to use**: simulation caches (cloth, fluid, destruction, crowd sim); VFX pipeline for
  baked simulations too complex for runtime skinning.
- Not suitable for looping game animations — file sizes are large (a full mesh of data per frame).

---

## glTF Deep Dive

### Draco Mesh Compression

Draco (Google) compresses mesh vertex data before storage; the decoder reconstructs vertices
at load time. Result: 50–90% reduction in mesh data size for web delivery.

**Setup in Three.js**:
```javascript
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { DRACOLoader } from 'three/examples/jsm/loaders/DRACOLoader.js';

const dracoLoader = new DRACOLoader();
dracoLoader.setDecoderPath('/draco/'); // path to decoder WASM files
const gltfLoader = new GLTFLoader();
gltfLoader.setDRACOLoader(dracoLoader);
```

**Export with Draco**: the Blender glTF exporter has a Draco option (Geometry section). Enable;
set quantization bits (position 14, normal 10, texcoord 12 — adjust for quality/size tradeoff).

### glTF Validation

Before delivering a glTF for production:

1. **gltf-validator** (CLI, Khronos): `npx gltf-validator model.glb` — reports schema errors,
   missing textures, invalid UV ranges.
2. **Khronos glTF Sample Viewer** (web): drag-and-drop; view in the reference PBR renderer.
3. **Three.js**: test in the actual runtime — issues that pass the validator can still cause
   runtime errors in specific Three.js versions.

### KTX2 / Basis Universal for Web

KTX2 is a GPU texture container; Basis Universal is a codec that encodes to KTX2 and transcodes
to the GPU's native format at runtime (BC1/BC3/BC7 desktop, ASTC mobile, ETC1/2 fallback).

**Why it matters for web**: browser WebGL/WebGPU can't decode JPEG/PNG at GPU level — the texture
occupies full uncompressed VRAM. KTX2 + Basis stays compressed on the GPU, dramatically reducing
VRAM usage.

**In Three.js**:
```javascript
import { KTX2Loader } from 'three/examples/jsm/loaders/KTX2Loader.js';
const ktx2Loader = new KTX2Loader();
ktx2Loader.setTranscoderPath('/basis/'); // path to basis_transcoder.js + .wasm
```

**Export to KTX2**: `toktx` (KTX-Software CLI), Basis Universal `basisu`, or `gltf-transform`
(see "Texture Export and Compression").

---

## Normal Map Baking

Normal baking is the most technically demanding step in the pipeline and the source of the most
common quality failures.

### High-to-Low Workflow

1. **Align meshes**: high-poly and low-poly in exactly the same position. The bake casts rays
   from the low-poly surface outward; the rays must hit the high-poly at a close, consistent
   distance.
2. **Set the cage / ray distance**: the cage is a slightly inflated low-poly that fully contains
   the high-poly; rays start from the cage, avoiding self-intersection. Far enough to reach the
   high-poly, not so far it crosses to adjacent surfaces.
3. **UV check**: the low-poly needs non-overlapping UVs in 0–1 space (or UDIM tiles for Substance
   Painter). Overlapping UVs make the bake data conflict.
4. **Bake**: the software casts rays from the low-poly, records where each hits the high-poly, and
   stores the surface-normal difference in RGB.
5. **Validate**: apply the map in the target renderer under multiple lighting angles; watch for
   seam lines (UV-island boundaries), skew at sharp angles, and missing high-poly detail.

### Baking Software Comparison

| Tool | Quality | Speed | Cage Control | Best For |
|------|---------|-------|-------------|---------|
| **Marmoset Toolbag** | Excellent | Fast (GPU) | Full, visual | Hero assets, complex characters — the industry reference |
| **Substance Painter** | Very good | Moderate | Per-mesh name match, limited cage | Game assets where texturing happens in Painter anyway |
| **Blender Cycles** | Good | Slow (complex scenes) | Cage object supported | Low-budget pipeline; no additional software cost |
| **xNormal** (free) | Good | Fast | Full | Legacy tool, still works well |

**Recommendation for Legion**: Marmoset Toolbag where bake quality matters (hero props,
characters, architectural hero pieces); Substance Painter bake for simpler assets (background
props, small objects) to keep the workflow in one tool.

### Common Baking Artifacts and Fixes

| Artifact | Cause | Fix |
|----------|-------|-----|
| Seam visible as hard edge | UV seam with no padding | Increase UV padding (8–16px at 2048); use "Match UVs" seam option in baker |
| Dark/light edge halo | Ray miss at mesh silhouette | Inflate cage or increase cage offset; check for gaps between high and low at that edge |
| Inverted normals (black patches) | High-poly faces normal-inward | Recalculate normals on high-poly (Blender: Mesh → Normals → Recalculate Outside) |
| Skewed/smeared detail | Low-poly UV islands rotated vs high-poly | Align UV islands to a primary axis; avoid 45° UV rotation on flat surfaces |
| Detail missing entirely | High-poly not covering low-poly there | Verify mesh alignment; bake in cage mode with sufficient offset |
| Color bleed from adjacent island | UV islands too close | Increase UV margin/padding between islands |

### Normal Map Format: DirectX vs. OpenGL

| Format | Green Channel | Common Engines |
|--------|--------------|---------------|
| DirectX (DX) | Y-down (green "up" reads inverted) | Unreal Engine, DirectX renderers, some Unity HDRP |
| OpenGL (GL) | Y-up (standard) | Unity default, Blender, glTF, Three.js / WebGL, Godot |

Wrong/mixed format = the map looks correct under light from one direction but inverted from the
perpendicular (depressions appear raised). Fix: invert the green channel, or set the target format
before baking (Substance Painter: Normal DirectX vs Normal OpenGL). **For Legion / Three.js: use
OpenGL** — consistent through the Blender → glTF → Three.js pipeline.

### Tangent Space vs. Object Space Normal Maps

**Tangent space** (standard for game assets):
- Normal vectors relative to the surface — mostly flat blue. Works with any mesh orientation.
- Supports UV mirroring (one map for both halves of a symmetric mesh).

**Object space**:
- Normal vectors in world/object coordinates — looks like a painted 3D surface. Full-quality
  detail regardless of UV direction, but does **not** work with mirrored UVs (each side needs
  its own UV space).
- Use case: sculpted organic surfaces where tangent-space quality is insufficient.

Use tangent space for game assets unless there's a specific reason not to.

### Normal Map Seam Management

UV seams create shading discontinuities if the map has a discontinuous edge at the seam. Prevention:
- **Edge split modifier** (Blender): split vertices at seams so each UV island has its own normal
  data. Required when the mesh has hard edges at UV seams.
- **Padding** (margin between UV islands): at least 8px at 2048. Bakers extend normal data into
  the padding to prevent seam lines at lower mip levels.
- **No mirrored UV islands in the bake**: mirrored UVs produce inverted normal lighting on the
  mirrored side. Use a unique UV for the bake (then pack), or configure the baker for mirrored UVs.

---

## LOD Generation

### Tools — When to Use Each

- **Blender Decimate Modifier** — fast, single-mesh, good for simple props:
  - *Collapse* mode: merges edges; fast, moderate quality; good for organic forms / background fill.
  - *Un-Subdivide* mode: reverses subdivision (subsurf meshes only) — clean quads, best quality
    for subdiv-modeled assets.
  - *Planar* mode: dissolves co-planar faces; excellent for hard-surface / architectural geometry.
  - Workflow: keep LOD0; apply Decimate at increasing ratios to make LOD1/LOD2; export each as
    `ASSETNAME_LOD0`, `ASSETNAME_LOD1`, … and check silhouette preservation.
- **Simplygon** — automatic mesh simplification at scale (AAA studios): input mesh + target
  triangle count → simplified mesh with preserved silhouette and UVs. The industry standard for
  automatic LOD in large studios.
- **Houdini Labs Tools** — node-based, batch-scriptable, production-grade: the LOD Generator node
  outputs multiple LOD levels with per-LOD polygon targets; author an HDA once, process whole batches.
- **Unreal Engine Auto LOD** — in-engine (Static Mesh Editor → LOD Settings → Auto LOD): no DCC
  round-trip; acceptable for background assets, check hero assets manually.
- **Unity LOD Group** — per-object component; Unity does *not* auto-generate — you bring in the
  pre-authored LOD meshes from the DCC.
- **Manual LOD** — hand-remodel where automatic simplification destroys key features: keep LOD0 as
  reference, model LOD1 (remove interior detail, simplify curves, merge small features), and keep the
  UV layout matching LOD0 so the same texture applies across levels.
- **Unreal Nanite** (UE5) — micropolygon virtualized geometry: streams and renders only the polygons
  visible at the current resolution, bypassing traditional LOD for eligible **static** meshes. Does
  NOT work with skeletal meshes, highly transparent materials, or deforming geometry.

### LOD Metric and Transitions

**Screen-space percentage** is the standard transition metric (not fixed distance): "switch when
the object occupies less than X% of screen height." Calibrate by scrubbing the camera until the
transition is invisible.

| Asset | LOD0→LOD1 | LOD1→LOD2 | LOD2→Billboard |
|-------|-----------|-----------|---------------|
| Hero character | 30% screen | 15% screen | — |
| Hero prop | 20% screen | 10% screen | — |
| Environment prop | 15% screen | 5% screen | 2% screen |
| Large structure | 40% screen | 20% screen | 5% screen |

These are starting points — tune against actual visual quality at the transition size.

---

## Texture Export and Compression

### Texture Dimension Rules

Always use power-of-two dimensions: 256, 512, 1024, 2048, 4096. Non-power-of-two textures either
force the GPU to upscale to the next power-of-two (wasting VRAM) or disable mipmapping (aliasing at
distance). Exception: UI textures in engines that disable mipmapping explicitly.

### Mipmap Generation

Mipmaps are pre-computed half-resolution chains (2048 → 1024 → … → 1×1); the GPU picks the level by
the surface's distance and angle. Without them, distant surfaces shimmer/sparkle (severe aliasing).
Non-optional for game textures. All engine importers generate them automatically; in Three.js,
`THREE.Texture` has `generateMipmaps: true` by default — leave it on for all tileable textures.

### Compression Format Reference

| Format | Channels | Use | Bit Rate |
|--------|---------|-----|---------|
| BC1 / DXT1 | 3 (RGB) or 4 (1-bit alpha) | Opaque albedo | 4 bpp |
| BC3 / DXT5 | 4 (RGBA) | Color with alpha | 8 bpp |
| BC4 | 1 (R) | Single-channel: roughness, metalness, height | 4 bpp |
| BC5 | 2 (RG) | Normal map XY | 8 bpp |
| BC7 | 3–4 (RGB/RGBA) | High-quality color + alpha | 8 bpp |
| ASTC 4×4 | Variable | Mobile (iOS, Android, Switch) | Variable |
| ASTC 6×6 | Variable | Mobile (more compression, lower quality) | Variable |
| ETC2 | 3–4 | Android fallback (when ASTC unavailable) | 4–8 bpp |
| KTX2 (Basis) | Variable | Web delivery (transcodes to GPU-native at runtime) | Variable |

**Per-map assignments**:
- **Albedo** (opaque): BC1 / ASTC 6×6 mobile
- **Albedo** (alpha): BC3 / ASTC 4×4 mobile
- **Normal map**: BC5 (best quality) — reconstructs Z in shader
- **ORM** (packed channels): BC7 (preserves subtle channel detail better than BC1)
- **Emissive**: BC7 (HDR-ish colors need the quality)
- **Roughness / Metalness** (separate): BC4

### Compression Pipelines

**toktx (KTX2 / Basis Universal)** — the Khronos reference encoder; one KTX2+BasisU file transcodes
to GPU-native on desktop, mobile, and web:
```bash
# Install via KTX-Software: https://github.com/KhronosGroup/KTX-Software/releases
toktx --uastc --genmipmap --assign_oetf srgb output.ktx2 input.png     # UASTC: high quality, larger
toktx --bcmp  --genmipmap output.ktx2 input.png                        # ETC1S: smaller, lower quality
toktx --uastc --assign_oetf linear normal_output.ktx2 normal_input.png # normal maps: linear
```
Or via `gltf-transform`:
```bash
gltf-transform uastc --quality 4 model.glb model-uastc.glb
gltf-transform etc1s --quality 128 model.glb model-etc1s.glb
```

**Compressonator (AMD, Windows GUI)** — BC1/BC3/BC4/BC5/BC7/ASTC compression for DDS texture sets,
batch atlas compression, and visual quality comparison. Normal-map workflow: source as 2-component
(RG) → output BC5 → import as BC5 with the "DirectX normal map" flag.

**Basis Universal / BasisU** — the tech underlying KTX2, two modes: **UASTC** (high quality, larger,
→ ASTC/BC7/RGBA16) for albedo and normal maps; **ETC1S** (small, lower quality, → ETC1/BC1) for
roughness/metalness/AO (less quality-sensitive).

---

## Engine Import

### Three.js / React Three Fiber (Legion primary)

Standard loading pattern:
```jsx
import { useGLTF } from '@react-three/drei'

function Ship({ url }) {
  const { scene, nodes, materials } = useGLTF(url)
  return <primitive object={scene} />
}

// Preload at app level
useGLTF.preload('/assets/ship.glb')
```

**Asset preparation checklist for Three.js**:
- GLB (single file, no loose textures)
- glTF PBR materials mapped from Principled BSDF in Blender
- Textures compressed with `gltf-transform` (UASTC or ETC1S + KTX2)
- Draco geometry compression for large meshes (>50k tris)
- Mesh quantization for web delivery (~40% smaller vertex data)
- Transform hierarchy clean — apply all transforms in Blender before export
- Texture resolution power-of-two (512, 1024, 2048, 4096)

**Runtime pipeline details** (imperative Three.js, Legion's stack):
- **GLTFLoader**: cache loader instances (don't create per load); after load, traverse to configure
  shadow casting per mesh and set up disposal cleanup to prevent VRAM leaks on unload.
- **Geometry instancing**: use `THREE.InstancedMesh` for any prop that repeats — all instances share
  one geometry + material, one draw call regardless of count. Essential for environment fill (crates,
  columns, modules).
- **Distance LOD** with `THREE.LOD`:
  ```javascript
  const lod = new THREE.LOD();
  lod.addLevel(highDetailMesh, 0);   // LOD0: 0–10 units
  lod.addLevel(medDetailMesh, 10);   // LOD1: 10–50 units
  lod.addLevel(lowDetailMesh, 50);   // LOD2: 50+ units
  scene.add(lod);
  ```
- **Texture caching**: one `THREE.TextureLoader` + a `Map` cache keyed by path; return the cached
  texture on repeat requests to prevent duplicate GPU uploads.
- **Progressive loading**: load LOD2 first (fast), swap to LOD0 on close approach or after a delay;
  combine with `THREE.LOD`. Draco on the glTF cuts initial download significantly.
- **Planetary-scale note**: `THREE.LOD`'s raw-distance switching is for props. Astronomical-scale
  hero bodies use angular-size LOD and the precision/temporal spine of [[game-scale-traversal]] /
  [[realtime-render-performance]] — not this component.

### Unreal Engine Import (FBX)

| Setting | Correct Value | Notes |
|---------|-------------|-------|
| Import Mesh | Yes | — |
| Skeletal Mesh | Yes (for characters) | Detect from FBX content |
| Import Normals | Import Normals and Tangents | Use DCC-calculated; don't let UE5 recalculate |
| Generate Lightmap UVs | Yes (for static meshes) | Required for Lumen/Lightmass baking |
| Apply Scalings | FBX All | Corrects Blender meter → UE5 centimeter mismatch |
| Import Animations | Yes | Only if the FBX contains animation clips |
| Combine Meshes | Off for modular kits; On for monolithic | — |
| Import Materials / Textures | On | Creates placeholder materials named from FBX; assign textures in the Material Editor |
| Import LODs | On if `_LOD1`/`_LOD2` meshes are in the FBX | — |

**The 100× scale problem**: Blender's scene unit is meters; Unreal imports as centimeters, so a
1.8 m character arrives at 180 units. Fix at export (Blender FBX Scale 0.01) or import (Apply
Scalings → FBX All).

### Unity Import

1. Drop the FBX into `Assets/Models/` — Unity auto-imports.
2. **Model tab**: Scale Factor 0.01 (Blender meters → Unity meters) or "Convert Units"; Mesh
   compression Off for hero / Low for background; Generate Lightmap UVs if not pre-authored;
   Normals: Import (DCC normals) or Calculate only if import produces artifacts.
3. **Rig tab** (characters): Animation Type Humanoid (retarget-compatible) or Generic (custom rigs);
   Avatar Definition Create From This Model (primary) / Copy From (shared).
4. **Animation tab**: Compression Optimal (or Keyframe Reduction for size); configure root motion
   (Root Transform Rotation/Position).
5. Extract materials ("Extract Materials") and assign textures manually.

### Common Import Artifacts

| Problem | Cause | Fix |
|---------|-------|-----|
| Character is 100× too large | FBX meter/cm unit mismatch | Apply scalings on import; or fix at export |
| Normals inverted (inside-out) | Normal direction flipped in export | In DCC: Flip Normals; or flip on import |
| Bones wrong orientation | Bone roll not set correctly | Fix bone rolls in DCC before export |
| Animation plays incorrectly | T-pose / bind-pose mismatch | Verify bind pose matches the engine avatar |
| Scale = 100 on root bone | FBX scale compensation on root | Apply all transforms in DCC before export |
| Textures not loading | Broken path references in FBX | Export textures alongside FBX; reimport with paths |

---

## Asset Validation Checklist

Run before finalizing an asset for delivery.

### Transforms & Geometry
- [ ] All transforms applied (Location/Rotation/Scale at default; scale = 1,1,1 in world space)
- [ ] Rotation deliberate (character facing +Y or +Z per engine convention)
- [ ] Origin at the intended pivot (base of feet, center of prop base)
- [ ] No zero-area/degenerate faces (produce NaN in GPU computations)
- [ ] No non-manifold edges (watertight — required for baking and physics)
- [ ] No isolated vertices; consistent outward face winding; no hidden internal geometry
- [ ] Polygon count within budget for the asset tier (see `lead-3d-designer` hub table)
- [ ] Custom/split normals correct — inspect in engine, not just the DCC

### UV Mapping
- [ ] UV channel 0 (texturing): non-overlapping in 0–1 space (or tiled within bounds)
- [ ] UV channel 1 (lightmap, if needed): non-overlapping, padded, full 0–1 coverage
- [ ] UV padding consistent with texture resolution (8–16px minimum at 2048)

### Textures
- [ ] All texture files power-of-two dimensions
- [ ] Albedo/emissive sRGB; normal/roughness/metalness/AO Linear
- [ ] Normal map format matches the target engine (DirectX vs. OpenGL)
- [ ] Texel density consistent across UV islands for the mesh's tier

### Naming & Pipeline
- [ ] File/object naming follows project convention; no stray parent empties or helpers in the export
- [ ] LOD meshes named consistently (`ASSETNAME_LOD0`, `_LOD1`, …) and transitions set
- [ ] Bone names follow the project/engine standard
- [ ] Texture files named and co-located with the mesh asset
- [ ] Collision mesh authored (convex hull for rigid props, custom for complex shapes)
- [ ] Imports correctly in the target engine at the correct scale, no console warnings/errors

---

## glTF Optimization Reference

`gltf-transform` optimization commands for the Legion web pipeline:

```bash
# Full optimization pipeline (textures + geometry)
gltf-transform optimize \
  --texture-compress uastc \
  --draco \
  model.glb model-optimized.glb

# Inspect sizes and contents before/after
gltf-transform inspect model.glb
gltf-transform inspect model-optimized.glb

# Strip unused materials and nodes
gltf-transform prune model.glb model-pruned.glb

# Flatten scene hierarchy (merges nodes where possible — faster rendering)
gltf-transform flatten model.glb model-flat.glb

# Merge separate meshes into one draw call where materials match
gltf-transform join model.glb model-joined.glb
```

**Optimization priority order for Legion**:
1. Texture compression (biggest file-size win — often 60–80%)
2. Draco compression (geometry — 40–60%)
3. Mesh quantization (additional ~10–20% on geometry data)
4. Join/flatten (draw-call reduction for performance)

---

## Blender → Web Automation & Volumetric Bakes (bpy)

The scriptable, batch side of the pipeline — and the **3D-texture / VDB bake path** the volumetric
renderers depend on. (Harvested from the `blender-web-pipeline` marketplace skill, which is the reference
implementation for bpy export automation; folded here rather than added as a duplicate spoke.)

- **bpy batch export.** Drive Blender headless (`blender --background --python export.py`) to export a
  directory of `.blend` files to GLB with consistent settings — Draco on, `+Y`-up, applied transforms,
  KTX2 textures — then pipe through `gltf-transform optimize`. Scriptable = reproducible; no per-asset
  hand-clicking. Author the export HDA/script once, run it in CI.
- **Density bake → 3D texture (the volumetric bridge).** [[vfx-volumetrics]] and
  [[atmospheric-scattering-and-clouds]] consume **baked 3D scalar fields**, not meshes: author a hero
  nebula / cloud shape in Blender, bake its density to **OpenVDB** or a **tiled 3D texture** (slice atlas),
  and load it in Three.js as a `Data3DTexture` for the raymarch's low-frequency shape (high-frequency detail
  stays procedural). This is the Blender-MCP path the [[legion-galaxy-playbook]] uses; automate the bake so
  a shape edit re-exports without manual steps.
- **Cloud noise bake.** The Perlin-Worley base + Worley detail volumes that
  [[atmospheric-scattering-and-clouds]] needs are best **baked offline to a 3D texture** (128³ base) and
  shipped compressed, not synthesized at runtime — bandwidth, not ALU, is the cloud bottleneck.
- **Capability:** requires the `blender-mcp` capability (degrades to hand-export if absent) — see
  [[skill-ecosystem-and-mcp-servers]].

---

## Cross-Links

| Skill | Relationship |
|-------|-------------|
| `3d-modeling-fundamentals` | Mesh must have applied transforms, correct normals, and clean topology before pipeline entry |
| `3d-materials-shading` | Texture map types, channel packing, and compression format decisions are authored at material stage; the pipeline executes them |
| `3d-rigging-animation` | Animation bake settings, FBX deform-bone-only export, and root-motion extraction are pipeline concerns |
| `3d-lighting-rendering` | Lightmap UV generation and bake quality settings live at the pipeline stage |
| `3d-spatial-design-for-games` | LOD *design* decisions (the philosophy); this skill covers LOD generation and pipeline execution |
| `glsl-shader-architect` | Custom shader code for engine materials (post-import) |
| `threejs-materials-master` | Three.js material class implementation details after glTF import |

## Related
- hub → [[lead-3d-designer]]
