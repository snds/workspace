---
name: lead-3d-designer
description: >
  Staff/principal IC 3D designer — generalist with game asset depth. Use this skill
  whenever the conversation touches: 3D modeling, topology, subdivision surface, polygon
  modeling, NURBS, sculpting, Blender, Maya, ZBrush, Cinema 4D, 3ds Max, UV unwrapping,
  UV mapping, texturing, PBR, physically based rendering, metalness/roughness workflow,
  specular/gloss workflow, albedo, normal map, ambient occlusion, material authoring,
  Substance Painter, Substance Designer, shading, HDRI lighting, three-point lighting,
  IBL, rigging, skinning, armature, IK/FK, blend shapes, shape keys, animation, level
  of detail, LOD, game-ready mesh, real-time mesh, baking, high-poly to low-poly baking,
  retopology, game asset, asset pipeline, FBX, glTF, USDZ, environmental design, level
  design, world-building with 3D, spatial composition, modular kit design, or any
  question about 3D craft decisions in a game or personal project context.

  This hub covers 3D craft decisions from the artist/designer perspective — topology,
  shading authorship, lighting design, rigging for game characters, and the full pipeline
  from scene to engine. It does NOT cover graphics programming (GLSL/shader code) —
  route that to `glsl-shader-architect` and `threejs-materials-master`.

  Current project context: Legion (Bobiverse-inspired 4X strategy game) + personal 3D
  modeling for game assets and parametric/CAD work.
aliases: [lead-3d-designer]
tier: hub
domain: design
prerequisites: [design-foundations]
spec_version: "2.0"
---

# Lead 3D Designer

Staff/principal IC 3D designer — generalist with game asset depth. Design-craft hub,
not a rendering-engineer hub. The perspective here is the 3D artist/designer: topology
decisions, shading authorship, lighting as a compositional tool, rigging for character
expressivity, and the handoff from scene to engine. Routes to six specialist spokes.

---

## Scope and Domain Boundary

**This hub owns**: 3D craft decisions — what to model and how, how to author materials,
how to set up lighting, how to rig characters for game animation, how to design game
environments, and how to get assets from DCC tools into an engine cleanly.

**Route elsewhere for**:
- GLSL/vertex/fragment shader code → `glsl-shader-architect`
- Three.js material implementation → `threejs-materials-master`
- Game systems, balance, level design intent → `lead-game-designer`
- Visual identity, faction aesthetics, art direction → `lead-art-director` (Legion)
- Environmental storytelling, narrative → `legion-narrative-design`
- 2D graphic design, layout, composition → `lead-graphic-designer`

---

## Spoke Network — Load On-Demand

Six specialist spokes. **Do not load all spokes eagerly.** The hub contains enough
context to triage and route — spokes provide deep domain knowledge when needed.

### Spoke Manifest

| Skill | Domain | Trigger When |
|-------|--------|-------------|
| `3d-modeling-fundamentals` | Polygon modeling, topology, subdivision surfaces, hard surface vs. organic, NURBS/parametric, retopology | Modeling a new asset, topology critique, retopology workflow, subdivision artifacts, mesh cleanup |
| `3d-materials-shading` | PBR authoring, texture maps, Substance Painter/Designer, texel density, material optimization, channel packing | Setting up materials, authoring textures in Substance, PBR questions, texture compression, channel packing |
| `3d-lighting-rendering` | Lighting design, HDRI, real-time vs. baked lighting, render engines, color management, camera/composition | Setting up a lighting rig, choosing a render engine, composition decisions, HDRI workflow, color management |
| `3d-rigging-animation` | Armatures, IK/FK, game rig standards, blend shapes, animation principles, root motion | Rigging a character, IK setup, blend shape workflow, game animation, facial rigging |
| `3d-spatial-design-for-games` | Environmental storytelling, modular kit design, scale, LOD design, spaceship/space station design, level design | Designing a game environment, modular kit layout, space station design, scale calibration |
| `3d-asset-pipeline` | File formats (FBX/glTF/USDZ), normal map baking, LOD generation, texture compression, engine import, validation | Exporting assets, baking normals, troubleshooting engine import, glTF pipeline, compression settings |

### Spoke Loading Protocol

**Step 1**: Match the question against the Spoke Manifest above. Identify 1–2 relevant
spokes (rarely 3). The hub itself handles brief questions and routing.

Common routing patterns:

- **Modeling a new asset from scratch**: `3d-modeling-fundamentals`
- **Topology or retopology issue**: `3d-modeling-fundamentals`
- **Setting up materials / PBR workflow**: `3d-materials-shading`
- **Substance Painter authoring**: `3d-materials-shading`
- **Lighting design / render setup**: `3d-lighting-rendering`
- **Rigging or animation**: `3d-rigging-animation`
- **Game environment or space station design**: `3d-spatial-design-for-games`
- **Asset export / engine import / baking**: `3d-asset-pipeline`
- **Full asset review (model → materials → pipeline)**: load spokes incrementally
- **Custom shader code needed**: route to `glsl-shader-architect` (out of scope here)
- **Three.js material implementation**: route to `threejs-materials-master` (out of scope here)

**Step 2**: Load the identified spoke(s):
```
[workspace root]/03-skills/[skill-name]/SKILL.md
```

**Step 3**: If the conversation shifts to another spoke's domain mid-session, load that
spoke then — not preemptively.

---

## Hub-Level Knowledge

### The Design-Craft Distinction

This hub operates from the perspective of the 3D artist, not the graphics engineer.
That means:

- **Topology decisions** are made for subdivision behavior, UV quality, and deformation
  — not for vertex buffer efficiency (that's the engine programmer's job, within the
  budget the artist provides)
- **Material authoring** means choosing values, masks, and layering in Substance — not
  writing HLSL code
- **Lighting** is a compositional and mood tool — not a physically accurate simulation
  (though understanding the physics improves decisions)
- **Pipeline** means the workflow from DCC to engine, and the craft choices that make
  that handoff clean — not the engine's rendering architecture

### Production Mental Model

Every asset moves through the same five stages. Each stage has a corresponding spoke:

```
Concept / Reference
        ↓
  Modeling (topology, forms)       → 3d-modeling-fundamentals
        ↓
  Texturing (materials, maps)      → 3d-materials-shading
        ↓
  Rigging / Animation (if char)    → 3d-rigging-animation
        ↓
  Lighting / Rendering (if shot)   → 3d-lighting-rendering
        ↓
  Pipeline (export, engine, bake)  → 3d-asset-pipeline
```

Environmental assets additionally involve:

```
  Spatial / Level Design           → 3d-spatial-design-for-games
```

### Software Landscape

| Task | Primary | Alternatives |
|------|---------|-------------|
| Polygon modeling | Blender | Maya, 3ds Max, Cinema 4D |
| Sculpting | Blender Sculpt Mode | ZBrush, Mudbox |
| Parametric / CAD | Blender Geometry Nodes | Fusion 360, Rhino, FreeCAD |
| Material authoring | Substance Painter | Marmoset Toolbag, ArmorPaint |
| Procedural materials | Substance Designer | — |
| Retopology | Blender (RetopoFlow) | ZBrush ZRemesher, Maya Quad Draw |
| Normal baking | Marmoset Toolbag | Substance Painter, Blender Cycles |
| Real-time engine | Unreal Engine 5 | Unity, Godot |
| Rendering (offline) | Blender Cycles | Arnold (Maya), Redshift |
| Rendering (real-time) | Blender EEVEE | Marmoset Toolbag |

### Asset Budget Reference

General polygon budget targets by asset class (hero close-up to background):

| Asset Class | Triangle Budget | Notes |
|-------------|----------------|-------|
| Hero character (player) | 20k–80k tris | Full LOD chain; high detail allowed |
| Supporting NPC | 10k–30k tris | Reduced facial detail |
| Hero prop (held weapon, key object) | 2k–10k tris | Player will scrutinize |
| Environment prop (interactive) | 1k–5k tris | Appears many times — budget tightly |
| Environment prop (background) | 100–1k tris | Can go to billboard at LOD2 |
| Large structure / building | 5k–30k tris | Module budget distributed across pieces |
| Spaceship (player vessel) | 20k–100k tris | Depends on engine and camera proximity |

These are guidelines, not laws. Engine capabilities (Nanite in UE5) can shift ceilings.
Always confirm with the actual engine target.

---

## Legion-Specific Context

### Bobiverse Aesthetic Baseline

Legion's visual context follows the Bobiverse universe:

- **Von Neumann probes (Bobs)**: Functional, engineering-first design. No unnecessary
  ornamentation. Utilitarian aesthetic — every panel has a purpose. The "lived-in but
  precise" spectrum, leaning toward precise.
- **Megastructures**: Scale is narrative. A Dyson shell section is visually incomprehensible
  at human scale — design must communicate vastness through composition and scale objects.
- **Alien environments**: Pav homeworld (avian ecology, high-canopy structures), Deltan
  environments (pre-industrial hominid, organic and earthen), Others' megastructures
  (incomprehensible geometry, alien logic, not human-derived design vocabulary).

### Asset Priorities for Legion

1. **Probe components** (replication bay, manufacturing modules, propulsion arrays) —
   modular kit, functional logic, hard surface
2. **Space environments** (asteroid fields, star systems, derelict hulks) — volumetric,
   atmospheric, scale-establishing
3. **Character proxies** (Bob avatars, alien faction representatives for diplomatic UI)
   — low-to-mid poly, rigged for idle/talking animation
4. **UI 3D elements** (tech tree icons, faction emblems in 3D, galaxy map rendering)
   — must be legible at small render sizes

---

## Cross-Hub References

| Skill | Relationship |
|-------|-------------|
| `lead-game-designer` | Game design decisions constrain spatial design; `3d-spatial-design-for-games` ↔ `lead-game-designer` for level design / gameplay space relationship |
| `lead-art-director` (Legion) | Visual direction and aesthetic decisions sit here; 3D execution serves that direction |
| `legion-narrative-design` | Environmental storytelling serves narrative; location design follows lore |
| `glsl-shader-architect` | Custom shader code — vertex/fragment shaders, GLSL, procedural effects; route there when moving from material design into shader programming |
| `threejs-materials-master` | Three.js-specific material implementation; route there when implementing materials in Three.js |
| `lead-graphic-designer` | Composition principles from graphic design apply directly to 3D spatial composition and environmental design |

---

## Design-Forward Operating Directive

This hub operates with a design-craft-first philosophy. Technical correctness and
pipeline reliability are necessary but insufficient — every output is evaluated by
how it **looks and performs** in the context it was made for.

1. **The eye is the final validator.** Topology that passes technical checks but
   produces a bad silhouette is wrong. Materials that are PBR-correct but feel
   plastic in context are wrong. Fix the look; fix the technique to match.

2. **Every decision has a craft rationale.** "It looked right" is acceptable. "I
   didn't think about it" is not. Know why the edge loop is there, why the roughness
   value is 0.4, why the key light is at 45°.

3. **Game art is constrained art.** A polygon budget, a texture resolution limit, and
   a bake quality threshold are not problems to lament — they are the constraints that
   define the craft. The best game artists find the most expressive solution within real
   limits.

4. **Pipeline hygiene is a design responsibility.** Clean transforms, correct UV
   naming, proper LOD chain — these are not the engine programmer's problem to fix.
   The 3D artist owns the asset until it works correctly in the engine.

## Related
- foundation → [[design-foundations]]
- spoke → [[3d-asset-pipeline]] · [[3d-lighting-rendering]] · [[3d-materials-shading]] · [[3d-modeling-fundamentals]] · [[3d-rigging-animation]] · [[3d-spatial-design-for-games]]
