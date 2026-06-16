---
name: 3d-modeling-fundamentals
description: >
  Polygon modeling, topology, and subdivision surfaces at a staff/principal level.
  Use this skill whenever the conversation touches: mesh construction, vertices/edges/
  faces, quads vs. tris vs. n-gons, edge flow, supporting loops, poles, subdivision
  surface modeling, cage-level modeling, hard surface modeling, organic modeling,
  sculpting workflow, retopology, NURBS, parametric modeling, Blender Geometry Nodes,
  CAD imports, high-poly to low-poly workflow, bevel/chamfer, boolean operations,
  ZBrush DynaMesh/ZRemesher, manual retopology, polygon budget by asset tier, or any
  question about how to build a mesh and why. This skill covers modeling craft and
  topology decisions — not materials (3d-materials-shading), rigging (3d-rigging-
  animation), or pipeline/export (3d-asset-pipeline).
hub: lead-3d-designer
aliases: [3d-modeling-fundamentals]
tier: spoke
domain: design
prerequisites: [lead-3d-designer]
spec_version: "2.0"
---

# 3D Modeling Fundamentals

Specialist lens for polygon modeling, topology, and mesh construction craft. Part of
the `lead-3d-designer` skill network.

---

## Domain Boundary

This skill owns **mesh construction decisions** — how to build a model, how topology
should flow, and why those choices affect downstream quality.

- **Materials, textures, PBR** → `3d-materials-shading`
- **Lighting and rendering** → `3d-lighting-rendering`
- **Rigging, animation** → `3d-rigging-animation`
- **Export, baking, engine import** → `3d-asset-pipeline`
- **Game environment layout** → `3d-spatial-design-for-games`

---

## The Mesh as a Data Structure

Every polygon mesh is a collection of:

- **Vertices**: Points in 3D space — the fundamental unit. Position, plus optional
  per-vertex data (normals, color, UVs on some formats).
- **Edges**: Connections between two vertices. Define form and control subdivision
  behavior.
- **Faces**: Surfaces enclosed by edges. Quads (4 vertices), tris (3), or n-gons (4+).

The mesh is what the artist authors. Everything downstream — UV unwrapping, baking,
rigging, rendering — operates on this structure.

---

## Polygon Types: Quads, Tris, N-gons

### Quads (4-sided polygons) — the production standard

Quads dominate production modeling for three reasons:

1. **Subdivision compatibility**: Subdivision surface algorithms (Catmull-Clark) work
   by splitting each quad into four quads. The result is mathematically predictable.
   A tri or n-gon inside a subdivided mesh creates pinching or uneven surfaces.

2. **UV unwrapping**: Quads unfold cleanly. The UV algorithm can follow the quad grid
   to produce minimal distortion. Tris inside UV islands create unpredictable stretching.

3. **Deformation predictability**: When a mesh is skinned and deformed (rigging), quads
   deform along their edge loops. Tris break the loop logic and produce artifact twisting
   at joints.

**The rule**: Model in quads. Convert to tris at the pipeline stage (game engine export)
— not during modeling.

### Tris (3-sided polygons) — acceptable in specific contexts

Acceptable when:
- The final mesh is a game-ready, non-subdivided mesh that will not deform
- Hidden areas where topology quality doesn't affect the visible surface or UVs
- Engine-facing geometry (the game engine renders tris natively; all quads are split to
  tris at runtime — so a game mesh with intentional tris is not a problem)
- Terminating an edge loop (poles and loop terminations sometimes require a tri)

Not acceptable when:
- The mesh will be subdivided — tris produce surface artifacts
- The mesh will deform (skinned character) — tris break joint deformation

### N-gons (5+ sided polygons) — treat as errors in production meshes

N-gons are non-planar by default (a 5-vertex face can't be flat in 3D space). This
produces:

- **Subdivision artifacts**: The algorithm can't cleanly subdivide a non-planar face —
  results in pinching, puckering, or unexpected crease behavior
- **Shading errors**: Flat shading and normal calculations on n-gons depend on which
  triangulation the software chooses — this can differ between DCC tools and engine
- **Boolean artifacts**: Boolean operations frequently produce n-gons at intersection
  edges — always clean up after booleans

**The exception**: N-gons are tolerable on flat, non-deforming, non-subdivided surfaces
(a wall panel that will never subdivide or bend). In practice, still clean them up.

---

## Topology Principles

### Edge Flow

Good topology follows the form of the underlying object. Think of edge loops as lines
drawn on the surface that describe its shape:

- **Organic forms**: Edge loops should follow muscle structure, joint planes, and
  natural body contours. A character's face has loops around the eyes, mouth, and jaw —
  mirroring how facial muscles fire and how the face deforms during animation.
- **Hard surface forms**: Edge loops should follow panel divisions, mechanical
  breaklines, and the silhouette-defining edges of the object.

Poor edge flow: loops that cross the form arbitrarily, terminate at unexpected poles,
or run perpendicular to the surface's natural deformation direction.

### Supporting Loops (Subdivision Control)

A subdivision surface algorithm takes the cage mesh and smooths it. Without control,
every edge becomes soft. Supporting loops let you control sharpness:

- A single supporting loop placed close to a crease edge will hold that edge tight
  through subdivision — the closer the loop, the sharper the crease.
- Two supporting loops (one on each side of the crease edge) create a symmetric,
  even crease.
- Too many supporting loops crowd the mesh and make it hard to edit. Use the minimum
  number of loops needed to achieve the desired surface.

**Mental model**: You are not modeling the final smooth surface. You are modeling the
cage that controls the smooth surface. Every decision at cage level has a magnified
consequence at subdivision level.

### Poles

A pole is a vertex where an unusual number of edges meet. Standard quads have 4-poles
(4 edges per vertex). Non-standard poles:

| Pole Type | Edge Count | Use |
|-----------|-----------|-----|
| 3-pole (triangle star) | 3 edges | Terminating a loop — mandatory at shape endpoints like fingertips, arrow tips |
| 4-pole (standard) | 4 edges | Default; everything should be 4-pole unless there's a reason |
| 5-pole (star) | 5 edges | Adding edge density (e.g., transition from low-density torso to high-density face). Creates slight subdivision tension — manageable if placed on flat or low-curvature surfaces |

**Where to put poles**: Flat, low-curvature areas where subdivision tension from the
pole is least visible. Never on a crease, never at a joint, never at the center of a
high-curvature surface.

---

## Hard Surface Modeling

Hard surface modeling produces mechanical, industrial, or architectural forms with
crisp edges and precise geometry.

### Bevel / Chamfer for Edge Control

In subdivision surface hard surface work, raw 90° edges subdivide into perfectly
round corners — too soft for mechanical geometry. The bevel/chamfer workflow:

1. Model with sharp 90° edges
2. Add a bevel to the crease edges (2–3 segments in Blender, scaled tight to the edge)
3. The bevel provides supporting geometry that holds the edge through subdivision

**Bevel settings**: 2-segment bevel with Profile = 1.0 gives a sharp crease; Profile
= 0.5 gives a slight roundover. Adjust for the desired sharpness.

**Alternative**: Crease values (Blender's mean crease) — set without adding geometry.
Faster but less flexible and not always compatible with all subdivision algorithms.

### Boolean Operations and Cleanup

Booleans (union, difference, intersection) allow rapid hard surface construction but
always require cleanup:

1. **Run the boolean**
2. **Inspect the result**: Booleans produce n-gons, non-manifold edges, and
   degenerate faces at intersection points
3. **Clean the intersection**: Dissolve the n-gons, reconnect with clean quad topology
4. **Add bevel support loops** at the new intersection edge
5. **Check in subdivision**: Apply subdivision to verify the result. Problems hide in
   cage view.

**Boolean workflow tools**: Blender (Boolean modifier), Maya (Boolean union/difference/
intersection). Both require the same manual cleanup pass.

### Panel Line Design

Panel lines (gaps, seams, and breaks between mechanical panels) are fundamental to
hard surface design hierarchy:

- **Primary panel lines**: The largest structural divisions — hull plates, major body
  panels. Wide gaps (~1–2mm at real scale), deep cuts.
- **Secondary panel lines**: Sub-panel detail within primary panels. Narrower, shallower.
- **Tertiary detail**: Bolts, rivets, micro-surface detail. Often added as a normal map
  bake from a high-poly mesh rather than modeled as geometry.

The panel hierarchy communicates scale. Consistent line width at each tier reads as
intentional design, not arbitrary surface noise.

---

## Organic Modeling and Sculpting

### Sculpting Workflow

For organic characters, creatures, and biomorphic forms, the sculpting workflow
is more efficient than polygon modeling from scratch:

1. **Blockout**: Start with a low-poly basemesh (either modeled or from a library).
   Establish major forms and proportions. In Blender: Sculpt Mode, use Grab and
   Elastic Deform to push mass around.

2. **DynaMesh / Remesh** (ZBrush / Blender Remesh): Dynamically re-triangulate the
   mesh to accommodate detail at any area. Use when the mesh needs more geometry
   to hold new detail. ZBrush: DynaMesh with resolution scaled to current zoom.
   Blender: Voxel Remesh (fast) or Quad Remesh (cleaner topology).

3. **Detailing**: Add surface detail with smaller brushes — pores, wrinkles, scales,
   fabric texture. This layer is high-poly only — detail goes into the normal map bake,
   not the game mesh.

4. **ZRemesher / Retopology**: Convert the sculptural high-poly into a clean low-poly
   with proper edge flow (see Retopology section below).

### Key Sculpting Brushes by Task

| Brush | Blender Name | ZBrush Name | Use |
|-------|-------------|-------------|-----|
| Volume manipulation | Grab | Move | Repositioning major forms |
| Volume build-up | Draw | Standard | Adding mass |
| Surface smoothing | Smooth | Smooth | Blending transitions |
| Crease definition | Crease | Dam Standard | Panel lines, wrinkles, fabric seams |
| Clay buildup | Clay Strips | Clay Buildup | Additive organic forms |
| Flatten | Flatten | Flatten | Mechanical flat surfaces in organic context |

---

## Retopology for Game Assets

Retopology is the process of rebuilding a clean low-poly mesh over a high-poly sculpt.
The low-poly carries the silhouette and animation; the high-poly's detail lives in the
normal map.

### Target Polygon Budgets

| Asset Tier | Triangle Budget | Context |
|------------|----------------|---------|
| Hero character (player / key NPC) | 20k–80k tris | Full LOD chain from this point |
| Supporting NPC | 8k–25k tris | Reduced facial/hand detail |
| Enemy unit (many on screen) | 3k–10k tris | Frequently instanced |
| Hero prop (weapon, held object) | 2k–10k tris | Player scrutinizes closely |
| Environment hero prop | 1k–5k tris | Key focal object |
| Environment fill prop | 200–1k tris | Repeated, background |
| Background prop | 50–300 tris | May use billboard at LOD2 |

### Retopology Standards

- **Quad-dominant**: No tris except at termination poles
- **Edge flow follows form**: Face loops around eyes, mouth, joints; edge loops follow
  mechanical panel lines on hard surface
- **Consistent polygon density**: More polygons where the surface curves or deforms;
  fewer on flat planes
- **Seam placement**: UV seams should sit at natural breaks — hairline, underarm, back
  of leg — where they are hidden in typical view

### Tools

- **Blender + RetopoFlow** (addon): Surface snapping, loop creation, poly fill. The
  fastest manual retopology workflow in Blender.
- **ZBrush ZRemesher**: Automatic retopology with guide curves to direct edge flow.
  Good for organic forms; requires cleanup for rigging-ready results.
- **Maya Quad Draw**: Freehand polygon creation with surface snapping. Industry-standard
  for character retopology.
- **Instant Meshes** (free): Fully automatic. Fast blockout, rarely production-ready
  without cleanup.

### Normal Map as the Bridge

The normal map captures the high-poly detail and applies it to the low-poly mesh at
render time. The baking workflow:

1. Position the high-poly and low-poly precisely on top of each other
2. Cast rays from the low-poly surface outward; the ray hits the high-poly and records
   the surface normal difference
3. Store the per-pixel normal difference in an RGB texture (DirectX or OpenGL format)
4. At render time, the shader uses this texture to simulate high-poly surface lighting
   on the low-poly mesh

The normal map cannot fix poor silhouette or missing mass from the low-poly — it only
adds surface detail within the existing silhouette. A good retopology preserves the
high-poly's silhouette with minimum geometry.

---

## NURBS and Parametric/CAD Modeling

### Parametric vs. Polygonal

**Polygonal**: Manual, artist-directed. Good for organic forms, stylized assets, fast
blockout. The artist places every vertex.

**Parametric / NURBS**: Definition-driven. Good for precision engineering, curves
defined mathematically. Resizable without quality loss. Native to CAD tools (Fusion 360,
Rhino, CATIA).

### Blender Geometry Nodes

Blender's Geometry Nodes system is a parametric node graph for procedural modeling:

- Define rules (distribute instances along a curve, create modular grid arrays, generate
  panel detail from parameters) instead of placing geometry manually
- Non-destructive: change the input parameters and the geometry updates
- Good for: modular structures, repeating mechanical detail, generative environment
  assets, parametric prop variants

Geometry Nodes is the recommended approach for Legion's probe/station modules — define
the module once, drive variants via parameters.

### CAD Imports: STEP/IGES to Polygon

CAD data (STEP, IGES, OBJ from CAD) must be converted to polygons for game engines.
Issues to watch:

- **Tessellation artifacts**: CAD surfaces are mathematically smooth; tessellation
  approximates them with polygons. Tessellation resolution controls the faceting.
  Set too low → faceted surfaces; too high → excessive polygon count.
- **N-gon explosion**: CAD conversion frequently produces n-gons. Run a cleanup pass
  (Tris to Quads, then manual cleanup for problem areas).
- **Non-manifold edges**: CAD tools allow surfaces that share no edge connection.
  Polygon meshes require manifold geometry for baking and physics.

**Workflow**: Import CAD → adjust tessellation quality → merge by distance (weld
coincident vertices) → tris to quads → cleanup n-gons → retopologize hero surfaces if
needed.

---

## Modeling Tool Reference

### Blender
- **Loop Cut (Ctrl+R)**: Insert an edge loop; scroll to add multiple
- **Bevel (Ctrl+B)**: Bevel an edge; V to bevel vertices; scroll for segments
- **Inset (I)**: Inset a face; applies to selection
- **Knife (K)**: Freehand cut across faces; C for angle-constrained
- **Shrinkwrap Modifier**: Project geometry onto another mesh — core retopology tool
- **Mirror Modifier**: Symmetric modeling; apply and merge at seam for final mesh
- **Subdivision Surface Modifier**: Apply Catmull-Clark subdivision; level 2 for
  preview, level 3–4 for bake/render

### Maya
- **Quad Draw**: Freehand retopology surface snapping tool
- **Multi-Cut**: Insert edge loops, cuts, and connection cuts
- **Boolean (Mesh > Booleans)**: Union, difference, intersection — always followed
  by cleanup

### ZBrush
- **DynaMesh**: Dynamic remesh for sculpt-phase work; resolution scales to zoom
- **ZRemesher**: Automatic retopology with guide curve support
- **Sculptris Pro**: Dynamic subdivision while sculpting (similar to DynaMesh but
  more adaptive)
- **Masking**: Isolate areas for localized operations; mask + extract for new
  sub-meshes
- **Layers**: Non-destructive sculpt layers (useful for blend shape targets)

---

## Quality Checklist

Before considering a model ready for materials or pipeline:

- [ ] Quad-dominant topology (tris only at intentional termination poles)
- [ ] No n-gons (check: Face > Select All by Trait > Non Quads > n-gons)
- [ ] No non-manifold geometry (Mesh Analysis > Non Manifold)
- [ ] No zero-area faces (degenerate polygons)
- [ ] No isolated vertices
- [ ] Edge flow follows form — verify by adding a subdivision modifier and evaluating
- [ ] Supporting loops in place on crease edges (subdivided result holds the right shape)
- [ ] Poles placed on flat/low-curvature areas only
- [ ] All transforms applied (scale = 1,1,1; rotation = 0,0,0; location as needed)
- [ ] Object naming follows project convention
- [ ] Within polygon budget for asset tier
- [ ] Silhouette reads correctly from primary view distances
