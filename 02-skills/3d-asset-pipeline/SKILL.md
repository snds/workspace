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

Specialist lens for export, optimization, and engine integration for 3D assets.
Part of the `lead-3d-designer` skill network.

---

## Domain Boundary

This skill owns **the handoff from DCC to engine** — file format decisions, baking
workflows, LOD generation, texture compression, and engine import settings.

- **Material authoring, PBR values** → `3d-materials-shading`
- **Shader code, GLSL** → `glsl-shader-architect`
- **Three.js material implementation** → `threejs-materials-master`
- **Mesh construction, topology** → `3d-modeling-fundamentals`
- **LOD design philosophy** → `3d-spatial-design-for-games` (the design decisions);
  this skill covers the generation and technical pipeline

---

## File Formats

### FBX (Filmbox)

The industry standard for rigged characters and animation.

- Proprietary Autodesk format (binary or ASCII). Nearly universal engine support.
- **When to use**: Rigged characters, animation clips, skeletal mesh data. Any asset
  that needs to carry animation or rig data to a game engine.
- **Limitations**: Binary format (not human-readable); animation data can degrade
  across DCC→engine round-trips; version differences between FBX SDK versions cause
  occasional import artifacts.
- **Critical setting**: FBX unit scale. Blender exports in meters; Unreal Engine
  imports in centimeters by default. A character that is 1.8m in Blender arrives at
  180 units in UE5 — 100× too large. Solution: enable "Apply Scalings" in the UE5
  importer, or scale the Blender export to 0.01 before export.

### glTF 2.0 / GLB

The open standard for real-time 3D assets. JSON-based schema, maintained by the
Khronos Group.

- **glTF**: Separate files (`.gltf` JSON + `.bin` binary geometry + texture files)
- **GLB**: Single binary container (all data packed, easier to transfer/serve)
- **When to use**: Web delivery (Three.js, Babylon.js), AR/VR (WebXR, RealityKit),
  any context where open standard matters; preferred for progressive loading pipelines.
- **Engine support**: Unreal and Unity both support glTF import (UE5 native; Unity
  via importer). Not as mature as FBX for animation pipelines — verify rig
  compatibility before committing to glTF for character import.

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

### USDZ

Apple's AR delivery format. Based on Pixar's Universal Scene Description (USD).

- **When to use**: iOS AR (ARKit, Reality Composer, QuickLook). Web AR on Safari.
- **Limitations**: Limited material feature support vs. glTF. Not suitable for
  complex rigged characters for real-time engines.
- USD (without the Z) is the VFX/animation interchange format of the future —
  DCC tools (Blender, Maya, Houdini) increasingly support USD import/export for
  pipeline interchange.

### OBJ

Legacy geometry-only format.

- ASCII text, universally supported, no animation, no materials embedded
  (separate `.mtl` file for material references, often breaks on import)
- **When to use**: Quick geometry transfer between tools when animation/materials
  don't matter. Export reference meshes for baking. Import CAD conversions.
- **Do not use** for any asset that needs to reach a game engine in production.

### Alembic (.abc)

Vertex cache animation format.

- Stores per-frame vertex positions — no bones, no skinning. The mesh deforms by
  replaying raw vertex positions.
- **When to use**: Simulation caches (cloth, fluid, destruction, crowd simulation).
  VFX pipeline for baked simulations that are too complex for runtime skinning.
- Not suitable for looping game animations — file sizes are large (one frame of
  full mesh data per frame).

---

## glTF Deep Dive

### Draco Mesh Compression

Draco (Google) compresses mesh vertex data before storage. The decoder reconstructs
vertices at load time. Result: 50–90% reduction in mesh data size for web delivery.

**Setup in Three.js**:
```javascript
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { DRACOLoader } from 'three/examples/jsm/loaders/DRACOLoader.js';

const dracoLoader = new DRACOLoader();
dracoLoader.setDecoderPath('/draco/'); // path to decoder WASM files
const gltfLoader = new GLTFLoader();
gltfLoader.setDRACOLoader(dracoLoader);
```

**Export with Draco**: Blender glTF exporter has a Draco option (Geometry section).
Enable; set quantization bits (position: 14, normal: 10, texcoord: 12 — adjust for
quality/size tradeoff).

### glTF Validation

Before delivering a glTF for production use:

1. **gltf-validator** (command line, Khronos Group): `npx gltf-validator model.glb`
   Reports schema errors, missing textures, invalid UV ranges.

2. **Khronos glTF Sample Viewer** (web): Drag and drop the file. View in the
   reference renderer with PBR shading.

3. **Three.js**: Test in the actual runtime environment — issues that pass the
   validator can still cause runtime errors in specific Three.js versions.

### KTX2 / Basis Universal for Web

KTX2 is a GPU texture container format. Basis Universal is a codec that encodes to
KTX2 and transcodes to the GPU's native format at runtime (BC1/BC3/BC7 on desktop,
ASTC on mobile, ETC1/2 as fallback).

**Why it matters for web**: Browser WebGL can't decode JPEG/PNG at GPU level — the
texture occupies full uncompressed memory. KTX2 with Basis stays compressed on GPU,
dramatically reducing VRAM usage.

**In Three.js**:
```javascript
import { KTX2Loader } from 'three/examples/jsm/loaders/KTX2Loader.js';
const ktx2Loader = new KTX2Loader();
ktx2Loader.setTranscoderPath('/basis/'); // path to basis_transcoder.js + .wasm
```

**Export to KTX2**: Use `toktx` (KTX-Software CLI) or Basis Universal `basisu` tool.

---

## Normal Map Baking

### The Baking Workflow

1. **Align high-poly and low-poly**: The high-poly should exactly overlay the
   low-poly. The baking ray is fired outward from the low-poly surface; it
   must hit the high-poly at a close, consistent distance.

2. **Set ray distance / cage**: The ray needs to travel far enough to reach the
   high-poly but not so far it crosses to adjacent surfaces. The cage inflates the
   low-poly slightly to define the ray boundary.

3. **Choose software**:
   - **Marmoset Toolbag**: Best-in-class baking. Visual skew correction, per-group
     cage control, explicit high/low mesh matching. The production standard for
     hero asset bakes.
   - **Substance Painter**: Good for assets being textured in Painter immediately.
     Bake once; use results directly in the project.
   - **Blender Cycles**: Requires manual setup (cage, ray distance, material
     nodes). Sufficient for personal/indie work.
   - **xNormal** (free): Legacy but still used; standalone baking tool.

4. **Output and verify**: Open the normal map in a viewer (Marmoset, Substance,
   or Sketchfab). Rotate lighting and look for:
   - Seam lines (UV island boundaries visible as shading breaks)
   - Skew artifacts at sharp angles
   - Missing detail (high-poly detail that didn't bake)

### DirectX vs. OpenGL Normal Maps

| Format | Green Channel | Used By |
|--------|-------------|---------|
| DirectX (DX) | Inverted (Y-down) | Unreal Engine, some Unity HDRP |
| OpenGL (GL) | Standard (Y-up) | Blender, Unity default, glTF, Three.js |

Wrong format = inverted surface detail (depressions appear raised, raised appears
depressed). The fix is simply to invert the green channel in any image editor.

Most baking software can export either format — set the target before baking.

### Tangent Space vs. Object Space Normal Maps

**Tangent space** (standard for game assets):
- Normal vectors relative to the surface. The map is mostly flat blue (most normals
  point outward, along the surface tangent).
- Works with any mesh orientation. The same map on a mirrored UV still works.
- Supports UV mirroring (one normal map for both halves of a symmetric mesh).

**Object space**:
- Normal vectors in world/object coordinates. The map looks like a painted 3D surface
  (reds, greens, blues in recognizable patches).
- Full-quality detail regardless of UV direction.
- Does NOT work with mirrored UVs (each side needs its own UV space).
- Use case: sculpted organic surfaces where tangent space quality is insufficient.

Use tangent space for game assets unless there's a specific reason not to.

### Normal Map Seam Management

UV seams create visible shading discontinuities if the normal map has a discontinuous
edge at the seam. Prevention:

- **Edge split modifier** (Blender): Split vertices at seams so each UV island has
  its own normal data. Required when the mesh has hard edges at UV seams.
- **Padding** (the margin between UV islands): Set to at least 8px at 2048 resolution.
  Bakers extend the normal data into the padding to prevent seam lines at lower mip
  levels.
- **No mirrored UV islands in the bake**: Mirrored UVs produce inverted normal
  lighting on the mirrored side. Either use a unique UV for the bake (then pack for
  texture), or ensure the baker is configured for mirrored UVs.

---

## LOD Generation

### Blender Decimate Modifier

- **Collapse mode**: Reduces polygon count by merging edges. Fast; moderate quality.
  Good for background fill props.
- **Un-Subdivide mode**: Reverses subdivision. Only works on subdivision surface
  meshes — produces clean quads. Best quality for subdiv-modeled assets.
- **Planar mode**: Removes faces whose normal deviation is below a threshold. Good
  for flat architectural elements with unnecessary internal loops.

**Workflow**: Keep the original mesh at LOD0. Apply Decimate as a modifier at
increasing strengths to generate LOD1, LOD2. Export each as a separate mesh named
`ASSETNAME_LOD0`, `ASSETNAME_LOD1`, etc.

### Simplygon

Automatic mesh simplification used at scale (AAA game studios). Takes a mesh and
a target triangle count; produces a simplified mesh with preserved silhouette and
UV data. The industry standard for automatic LOD in large studios.

### Manual LOD

Hand-remodeled LODs for assets where automatic simplification destroys important
features. Workflow:

1. Keep LOD0 as reference
2. Model LOD1 from scratch (or modify LOD0 in place) — remove interior detail,
   simplify curves, merge small features
3. Verify UV layout matches LOD0 so the same texture applies to all LOD levels

### LOD Metric and Transitions

**Screen-space percentage**: The standard engine LOD transition metric. A value
of 0.05 means "switch to this LOD when the object occupies less than 5% of the
screen height."

- LOD0 → LOD1: ~0.20–0.30 (transition at medium distance)
- LOD1 → LOD2: ~0.08–0.12
- LOD2 → LOD3 / billboard: ~0.02–0.05

Calibrate these by placing the object in the scene and scrubbing the camera distance
until the transition is invisible.

### Unreal Nanite

Nanite (UE5) uses micropolygon virtualized geometry — it streams and renders only
the polygons visible at the current camera resolution, bypassing traditional LOD
entirely for static meshes.

- Works with: static meshes with high polygon counts
- Does NOT work with: skeletal meshes (characters), highly transparent materials,
  deforming geometry (cloth, fluid)
- Replaces LOD pipeline for eligible static meshes — no need to hand-author LOD1/2/3

---

## Texture Export and Compression

### Texture Dimension Rules

Always use power-of-two dimensions: 256, 512, 1024, 2048, 4096.

Non-power-of-two textures either:
- Force the GPU to upscale to the next power-of-two (wasting VRAM)
- Disable mipmapping (causing aliasing artifacts at distance)

Exception: UI textures in some engines that disable mipmapping explicitly.

### Mipmap Generation

Mipmaps are pre-computed half-resolution versions of a texture (2048 → 1024 → 512
→ 256 → ... → 1×1). The GPU selects the appropriate mip level based on the surface's
distance and angle.

Without mipmaps: distant surfaces display full-resolution textures on tiny screen
coverage — severe aliasing (the surface shimmers and sparkles as the camera moves).
Mipmaps are non-optional for game textures.

All engine importers generate mipmaps automatically. In Three.js, `THREE.Texture`
has `generateMipmaps: true` by default — leave it on for all tileable textures.

### Compression Format Reference

| Format | Channels | Use | Bit Rate |
|--------|---------|-----|---------|
| BC1 / DXT1 | 3 (RGB) or 4 (with 1-bit alpha) | Opaque albedo | 4 bpp |
| BC3 / DXT5 | 4 (RGBA) | Color with alpha | 8 bpp |
| BC4 | 1 (R) | Single-channel: roughness, metalness, height | 4 bpp |
| BC5 | 2 (RG) | Normal map XY | 8 bpp |
| BC7 | 3–4 (RGB/RGBA) | High-quality color + alpha | 8 bpp |
| ASTC 4×4 | Variable | Mobile (iOS, Android, Nintendo Switch) | Variable |
| ASTC 6×6 | Variable | Mobile (more compression, lower quality) | Variable |
| ETC2 | 3–4 | Android fallback (when ASTC not available) | 4–8 bpp |
| KTX2 (Basis) | Variable | Web delivery (transcodes to GPU-native at runtime) | Variable |

**Per-map assignments**:
- **Albedo** (opaque): BC1 / ASTC 6×6 mobile
- **Albedo** (alpha): BC3 / ASTC 4×4 mobile
- **Normal map**: BC5 (best quality) — reconstructs Z in shader
- **ORM** (packed channels): BC7 (preserves subtle channel detail better than BC1)
- **Emissive**: BC7 (HDR-ish colors need the quality)
- **Roughness / Metalness** (separate): BC4

---

## Engine Import

### Unreal Engine Import Settings (FBX)

| Setting | Correct Value | Notes |
|---------|-------------|-------|
| Import Mesh | Yes | — |
| Skeletal Mesh | Yes (for characters) | Detect from FBX content |
| Import Normals | Import Normals and Tangents | Use DCC-calculated; do not let UE5 recalculate |
| Generate Lightmap UVs | Yes (for static meshes) | Required for Lumen or Lightmass baking |
| Apply Scalings | FBX All | Corrects Blender meter → UE5 centimeter mismatch |
| Import Animations | Yes | Only if FBX contains animation clips |
| Animation Length | Exported Time | Use the exact export range |

**The 100× scale problem**: Blender's default FBX export uses meters. Unreal Engine's
import assumes centimeters. A 1.8m character arrives as 180 Unreal units. Fix: in
Blender's FBX export, set Scale to 0.01; or in UE5 import settings, enable Apply
Scalings → FBX All.

### Unity Import Settings

**Model tab**:
- Scale Factor: 0.01 (for FBX from Blender at meter scale)
- Normals: Import (use DCC normals); Calculate only if import produces artifacts

**Rig tab** (for characters):
- Animation Type: Humanoid (for retarget-compatible characters); Generic (for custom rigs)
- Avatar Definition: Create From This Model (for the primary rig); Copy From (for shared avatars)

**Animation tab**:
- Compression: Optimal (Unity default); Keyframe Reduction for minor quality loss and
  significant size reduction
- Root Transform Rotation / Position: configure root motion here

### Common Import Artifacts

| Problem | Cause | Fix |
|---------|-------|-----|
| Character is 100× too large | FBX meter/cm unit mismatch | Apply scalings on import; or fix at export |
| Normals are inverted (inside-out) | Normal direction flipped in export | In DCC: Flip Normals; or flip on import setting |
| Bones have wrong orientation | Bone roll not set correctly | Fix bone rolls in DCC before export |
| Animation plays incorrectly | T-pose / bind pose mismatch | Verify bind pose matches engine avatar requirements |
| Scale = 100 on root bone | FBX scale compensation applied to root | Apply all transforms in DCC before export |
| Textures not loading | Path references broken in FBX | Export textures alongside FBX; reimport with texture paths |

---

## Asset Validation Checklist

### Transforms

- [ ] All scale transforms applied (scale = 1, 1, 1 in world space)
- [ ] Rotation applied or deliberate (character facing +Y or +Z per engine convention)
- [ ] Location: origin at intended pivot point (base of character feet, center of prop base)

### Geometry

- [ ] No zero-area faces (degenerate polygons)
- [ ] No non-manifold geometry (edges shared by 3+ faces)
- [ ] No isolated vertices (vertices not connected to any face)
- [ ] Consistent face winding (normals all pointing outward)
- [ ] No internal geometry (faces hidden inside the mesh)

### UV Mapping

- [ ] No UV overlaps in lightmap UV channel (UV channel 2 in Unreal, UV1 in Unity)
- [ ] UV islands within 0–1 space (or tiled within bounds for tiling textures)
- [ ] UV padding consistent with texture resolution (8–16px minimum at 2048)

### Naming and Hierarchy

- [ ] Object naming follows project convention
- [ ] No unnecessary parent empties or helper objects included in export
- [ ] LOD meshes named consistently (`ASSETNAME_LOD0`, `ASSETNAME_LOD1`, etc.)
- [ ] Bone names follow convention (project/engine standard)

### Textures

- [ ] All texture files power-of-two dimensions
- [ ] Normal map format matches target engine (DX vs. GL)
- [ ] Normal and data maps set to Linear (not sRGB) in engine import
- [ ] Albedo set to sRGB in engine import

---

## Three.js-Specific Pipeline

### GLTFLoader Optimization

Cache loader instances — do not create new ones per load. After loading, traverse
and configure shadow casting per mesh, and set up disposal cleanup to prevent VRAM
leaks when assets are unloaded.

### Geometry Instancing for Repeated Props

Use `THREE.InstancedMesh` for any prop that appears many times in the scene. All
instances share one geometry and one material, rendering in a single draw call
regardless of instance count. Essential for environment fill props (crates, columns,
structural modules).

### THREE.LOD for Distance-Based Switching

```javascript
const lod = new THREE.LOD();
lod.addLevel(highDetailMesh, 0);   // LOD0: 0–10 units
lod.addLevel(medDetailMesh, 10);   // LOD1: 10–50 units
lod.addLevel(lowDetailMesh, 50);   // LOD2: 50+ units
scene.add(lod);
```

### Texture Caching

Use a single `THREE.TextureLoader` instance with a `Map` cache. Call `loader.load(path)`
once per path; return the cached texture on subsequent requests. Prevents duplicate
texture uploads when multiple materials share the same texture.

### Progressive Loading

For large environments: load LOD2 first (fast), swap to LOD0 when the asset is within
close-view range or after a delay. Combine with THREE.LOD for the distance-based swap.
Draco compression on the glTF reduces initial download size significantly.

---

## Cross-Links

- `3d-materials-shading`: texture map types and compression settings are shared
  territory — this skill covers the pipeline; `3d-materials-shading` covers authoring
- `glsl-shader-architect`: custom shader code for engine materials (post-import)
- `threejs-materials-master`: Three.js material class implementation details
- `3d-spatial-design-for-games`: LOD design decisions (the philosophy); this skill
  covers LOD generation and pipeline execution
- `3d-modeling-fundamentals`: clean mesh requirements that make baking and export
  work correctly
  3D asset pipeline, export, baking, and engine import at a staff/principal
  level. Use this skill whenever the conversation touches: FBX export, FBX
  quirks, FBX scale, glTF, glTF 2.0, gltf-transform, GLB, GLTF binary, USDZ,
  USD, normal map baking, high-to-low baking, cage baking, bake offset, baking
  software, Marmoset Toolbag baker, Substance Painter baker, Blender Cycles
  bake, LOD generation, LOD tool, mesh decimation, collision mesh, convex hull,
  asset validation, polycount budget, UV overlap detection, smoothing groups,
  hard edges, split normals, custom normals, texture compression pipeline,
  toktx, KTX2, Basis Universal, compressonator, DXTex, texture compression
  workflow, Draco compression, mesh quantization, glTF optimization, glTF
  extensions, Three.js asset pipeline, React Three Fiber asset, R3F model,
  engine import workflow, asset naming convention, clean transforms, applied
  transforms, or any question about getting a 3D asset from a DCC tool into an
  engine or web renderer cleanly and correctly.
hub: lead-3d-designer
---

# 3D Asset Pipeline

Specialist lens for the full pipeline from DCC tool to game engine or web
renderer. Part of the `lead-3d-designer` skill network.

---

## Domain Boundary

This skill owns **the path from DCC to engine** — file formats, baking, LOD
generation, texture compression, and engine import validation.

- **Mesh construction, topology** → `3d-modeling-fundamentals`
- **Material authoring, PBR values** → `3d-materials-shading`
- **Lighting setup in engine** → `3d-lighting-rendering`
- **Rig export, animation bake** → `3d-rigging-animation`
- **GLSL shader code** → `glsl-shader-architect`
- **Three.js material implementation** → `threejs-materials-master`

---

## File Format Reference

### FBX

The most widely used interchange format for game assets. Works with all major engines
(Unity, Unreal, Godot). Not an open standard — owned by Autodesk.

**FBX quirks to know**:

- **Scale units**: FBX has a concept of system units (centimeters, meters, inches).
  Blender exports in centimeters by default; Unreal expects centimeters; Unity expects
  meters. A mesh exported at 1m in Blender may import at 100 units in Unreal unless
  the import scale factor is set to 1.0 (Unreal handles the cm-to-unit convention).
  Blender to Unity: set FBX export scale to 1.0 and "Apply Unit" on — or multiply
  all transforms by 0.01 in Unity's import settings.

- **Apply transforms before export**: If the mesh has non-unit scale or non-zero
  rotation in Blender, the FBX exporter may bake those in unpredictably. Always
  Apply All Transforms (Ctrl+A → All Transforms) before export.

- **Bone axes**: Blender uses Y-up along bone length; engines vary. The FBX exporter
  applies a correction transform — verify in the engine that bones point the right way.

- **Smoothing groups**: FBX encodes hard/soft edges as smoothing groups. Verify
  "Edge" is selected in Blender's FBX smoothing export option, not "Face" —
  "Face" loses split normal data.

- **Materials**: FBX exports material names, not actual material data. The engine
  will create placeholder materials with the correct names — you assign textures
  manually in the engine after import.

### glTF 2.0 / GLB

The open standard for 3D on the web, increasingly adopted by game engines.
`glTF` is the JSON + separate binary/texture version; `GLB` is the single-file
binary container. GLB is preferred for delivery.

**glTF strengths**:
- Open, well-specified, version-stable
- Native to Three.js and React Three Fiber — the preferred format for Legion's web renderer
- Extensions for PBR materials, compression, transmission, clearcoat, specular,
  iridescence, anisotropy
- Supports embedded textures (GLB) or separate textures (glTF + bin + textures)

**glTF PBR material mapping**:
- `baseColorTexture` → Albedo (sRGB)
- `metallicRoughnessTexture` → G=Roughness, B=Metalness (Linear)
- `normalTexture` → Normal map (OpenGL convention)
- `occlusionTexture` → AO (Linear)
- `emissiveTexture` → Emissive (sRGB)

**glTF export from Blender**: File → Export → glTF 2.0. Enable "Include Materials",
"Include Punctual Lights" if needed. The Blender glTF exporter respects Principled
BSDF nodes — set up materials with standard nodes and they export correctly.

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

**For Legion's Three.js pipeline**: Use `gltf-transform` as the final step in
the asset pipeline. Author in Blender → export GLB → run through `gltf-transform`
for compression → import into Three.js scene.

### USDZ

Apple's format for AR Quick Look on iOS. Based on Pixar's Universal Scene Description
(USD). Use when the deliverable is an AR experience or Apple ecosystem integration.

Export from Blender: third-party addon required (USD Exporter is bundled since 3.x).
Alternatively: export glTF → convert with `usd-from-gltf` (Khronos tool) or Reality
Composer.

---

## Normal Map Baking

Normal baking is the most technically demanding step in the asset pipeline and the
source of the most common quality failures.

### High-to-Low Workflow

1. **Align meshes**: The high-poly and low-poly must be in exactly the same position.
   The bake casts rays from the low-poly surface outward; the rays must hit the high-poly.
2. **Set the cage** (if using cage baking): The cage is a slightly inflated version of
   the low-poly that contains the high-poly fully. Ray baking uses the cage as the
   starting position for rays, avoiding self-intersection artifacts.
3. **UV check**: The low-poly must have non-overlapping UVs in the 0–1 space (or UDIM
   tiles for Substance Painter). Overlapping UVs cause bake data to conflict.
4. **Bake**: Software casts rays from the low-poly surface, records where each ray hits
   the high-poly, and stores the surface normal difference in RGB.
5. **Validate**: Apply the normal map in the target renderer and inspect under multiple
   lighting angles. Artifacts at bake seams, black/white bleeding, and incorrect
   edge softness are common failure modes.

### Baking Software Comparison

| Tool | Quality | Speed | Cage Control | Best For |
|------|---------|-------|-------------|---------|
| **Marmoset Toolbag** | Excellent | Fast (GPU) | Full, visual | Hero assets, complex characters — the industry reference |
| **Substance Painter** | Very good | Moderate | Per-mesh name match, limited cage | Game assets where texturing happens in Painter anyway |
| **Blender Cycles** | Good | Slow (complex scenes) | Cage object supported | Low-budget pipeline; no additional software cost |
| **xNormal** (free) | Good | Fast | Full | Legacy tool, still works well |

**Recommendation for Legion**: Marmoset Toolbag for any asset where bake quality
matters (hero props, characters, architectural hero pieces). Substance Painter bake
for simpler assets (background props, small objects) to keep the workflow in one tool.

### Common Baking Artifacts and Fixes

| Artifact | Cause | Fix |
|----------|-------|-----|
| Seam visible as hard edge | UV seam with no padding | Increase UV padding (8–16px at 2048); use "Match UVs" seam option in baker |
| Dark/light edge halo | Ray miss at mesh silhouette | Inflate cage or increase cage offset; check for gaps between high and low at that edge |
| Inverted normals (black patches) | Normal of high-poly faces inward | Recalculate normals on high-poly (Blender: Mesh → Normals → Recalculate Outside) |
| Skewed/smeared detail | Low-poly UV islands rotated relative to high-poly | Align UV islands to primary axis; avoid 45° UV rotation on flat surfaces |
| Detail missing entirely | High-poly not covering low-poly at that area | Verify mesh alignment; bake in cage mode with sufficient cage offset |
| Color bleed from adjacent UV island | UV islands too close | Increase UV margin/padding between islands |

### Normal Map Format: DirectX vs. OpenGL

| Format | Green Channel | Common Engines |
|--------|--------------|---------------|
| DirectX (DX) | Y-up (green = bright means "up") | Unreal Engine, DirectX renderers |
| OpenGL (GL) | Y-down (inverted green) | Unity, Blender, Three.js / WebGL, Godot |

Mixing formats causes the normal map to look correct under light from one direction
but inverted under light from the perpendicular direction. Verify format before delivery.
In Substance Painter export settings: choose Normal DirectX or Normal OpenGL.

**For Legion / Three.js**: OpenGL format. Blender's internal renderer also expects
OpenGL. Consistent through the Blender → glTF → Three.js pipeline.

---

## LOD Generation Tools and Thresholds

### When to Use Each Tool

**Blender Decimate Modifier** — fast, single-mesh, good for simple props:
- Collapse mode: reduces polygon count by collapsing edges; good for organic forms
- Planar mode: dissolves co-planar faces; excellent for hard surface geometry
- Best workflow: duplicate the LOD0 mesh, apply Decimate at the appropriate ratio,
  check for silhouette preservation, export

**Houdini Labs Tools** — node-based, batch-scriptable, production-grade:
- LOD Generator node: inputs the full-res mesh, outputs multiple LOD levels
  with per-LOD polygon targets
- Scriptable: author an HDA once, process entire asset batches

**Unreal Engine Auto LOD** — in-engine, integrated, good for architecture:
- Static Mesh Editor → LOD Settings → Auto LOD → set reduction targets
- Convenience: no round-trip through DCC, available after import
- Quality: acceptable for background assets; check hero assets manually

**Unity LOD Group** — per-object in-engine:
- Add LOD Group component; assign pre-authored meshes to each LOD level
- Unity does not auto-generate; you bring in the LOD meshes from DCC

### LOD Thresholds

Set LOD transitions based on screen percentage coverage (not fixed distance):

| Asset | LOD0→LOD1 | LOD1→LOD2 | LOD2→Billboard |
|-------|-----------|-----------|---------------|
| Hero character | 30% screen | 15% screen | — |
| Hero prop | 20% screen | 10% screen | — |
| Environment prop | 15% screen | 5% screen | 2% screen |
| Large structure | 40% screen | 20% screen | 5% screen |

These are starting points — tune based on actual visual quality at the transition
screen size.

---

## Texture Compression Pipelines

### toktx (KTX2 / Basis Universal)

`toktx` is the Khronos reference tool for encoding KTX2 containers with Basis
Universal compressed textures. KTX2+BasisU textures transcode to GPU-native formats
at runtime — a single compressed file works on desktop, mobile, and web.

```bash
# Install via KTX-Software
# https://github.com/KhronosGroup/KTX-Software/releases

# UASTC encoding (high quality, larger file)
toktx --uastc --genmipmap --assign_oetf srgb output.ktx2 input.png

# ETC1S encoding (smaller file, lower quality)
toktx --bcmp --genmipmap output.ktx2 input.png

# For normal maps: linear transfer function, no mipmaps (or controlled mip)
toktx --uastc --assign_oetf linear normal_output.ktx2 normal_input.png
```

**With gltf-transform**:
```bash
gltf-transform uastc --quality 4 model.glb model-uastc.glb
# or
gltf-transform etc1s --quality 128 model.glb model-etc1s.glb
```

### Compressonator (AMD) — Windows Desktop Tool

GUI tool for BC1/BC3/BC4/BC5/BC7/ASTC compression. Use for:
- DDS texture sets for engine-direct import
- Batch compression of texture atlases
- Visual quality comparison between compression formats

**Normal map workflow**: Set source as 2-component (RG) normal → output BC5 → import
as BC5 in engine with the "DirectX normal map" flag.

### Basis Universal / BasisU

The underlying compression technology in KTX2. Two modes:
- **UASTC**: High quality, larger file, transcodes to ASTC/BC7/RGBA16
- **ETC1S**: Small file, lower quality, transcodes to ETC1/BC1

Choose UASTC for albedo and normal maps (quality-sensitive). Choose ETC1S for
roughness/metalness/AO (less visually sensitive to quality loss).

---

## Engine Import Workflows

### Three.js / React Three Fiber (Legion Primary)

The standard asset loading pattern:

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
- GLB format (single file, no loose textures)
- glTF PBR materials mapped from Principled BSDF in Blender
- Textures compressed with `gltf-transform` (UASTC or ETC1S + KTX2)
- Draco geometry compression for large meshes (>50k tris)
- Mesh quantization applied for web delivery (reduces vertex data size ~40%)
- Transform hierarchy clean — apply all transforms in Blender before export
- Texture resolution power-of-two (512, 1024, 2048, 4096)

### Unity Import

1. Drop FBX into `Assets/Models/` folder — Unity auto-imports
2. In the model importer:
   - Set scale factor: Blender exports in centimeters; Unity expects meters → 0.01
     (or set "Convert Units" to handle this automatically)
   - Mesh compression: Off for hero assets, Low for background
   - Generate Lightmap UVs: On if not pre-authored in Blender
   - Normals: Import (if custom normals in FBX) or Calculate (if none)
3. Extract materials: "Extract Materials" button → assign textures manually
4. Rig: If animated, set Animation Type to Humanoid or Generic, configure Avatar

### Unreal Engine Import

1. Content Browser → Import → select FBX
2. Import options:
   - Scale: typically leave at default (UE handles cm to UE unit conversion)
   - Combine Meshes: Off for modular kits; On for single monolithic meshes
   - Import Materials: On (creates placeholder materials named from FBX)
   - Import Textures: On
3. Assign textures to the placeholder materials via the Material Editor
4. For LODs: if LOD meshes are in the FBX (named `_LOD1`, `_LOD2`), enable "Import LODs"

---

## Asset Validation

Run these checks before finalizing an asset for delivery:

### Mesh Validation

- [ ] All transforms applied (Location, Rotation, Scale = default values)
- [ ] No zero-area faces (degenerate polygons that produce NaN in GPU computations)
- [ ] No non-manifold edges (mesh is watertight — required for baking and physics)
- [ ] No isolated vertices
- [ ] Polygon count within budget for asset tier (see `lead-3d-designer` hub table)
- [ ] UV channel 0: texturing UVs, non-overlapping in 0–1 space
- [ ] UV channel 1 (if needed): lightmap UVs, non-overlapping, padded, full 0–1 coverage
- [ ] Custom normals (split normals) are correct — inspect in engine, not just DCC

### Texture Validation

- [ ] All texture resolutions power-of-two
- [ ] Albedo/emissive: sRGB color space; normal/roughness/metalness/AO: Linear
- [ ] Normal map format matches target engine (DirectX vs. OpenGL)
- [ ] No UV overlap in final bake (causes incorrect lighting in lightmaps)
- [ ] Texel density consistent across all UV islands for the mesh's tier

### Pipeline Validation

- [ ] File naming follows project convention
- [ ] All texture files are named and co-located with the mesh asset
- [ ] LOD chain present and transitions set
- [ ] Collision mesh authored (convex hull for rigid props, custom for complex shapes)
- [ ] Imported correctly in the target engine at the correct scale
- [ ] No import warnings or errors in engine console

---

## glTF Optimization Reference

Quick reference for `gltf-transform` optimization commands for the Legion web pipeline:

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
1. Texture compression (biggest file size wins — often 60–80% reduction)
2. Draco compression (geometry — 40–60% reduction)
3. Mesh quantization (additional ~10–20% on geometry data)
4. Join/flatten (draw call reduction for performance)

---

## Cross-Links

| Skill | Relationship |
|-------|-------------|
| `3d-modeling-fundamentals` | Mesh must have applied transforms, correct normals, and clean topology before pipeline entry |
| `3d-materials-shading` | Texture map types, channel packing, and compression format decisions are authored at material stage; pipeline executes them |
| `3d-rigging-animation` | Animation bake settings, FBX deform-bone-only export, and root motion extraction are pipeline concerns |
| `3d-lighting-rendering` | Lightmap UV generation and bake quality settings live at the pipeline stage |
| `anthropic-skills:threejs-materials-master` | Three.js material configuration after glTF import — loading GLBs, assigning textures, configuring tone mapping |
