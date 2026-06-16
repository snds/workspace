---
name: 3d-spatial-design-for-games
description: >
  Game environment design and spatial craft at a staff/principal level. Use
  this skill whenever the conversation touches: environmental storytelling,
  world building in 3D, modular kit design, modular environment, snap units,
  grid alignment, connector discipline, tileable environment, level art,
  level design, space station design, spaceship interior, corridor design,
  docking bay, engine room, command deck, reactor room, airlock, hull plating,
  human scale, proportion calibration, scale reference, LOD design philosophy,
  LOD0 LOD1 LOD2, billboard LOD, level of detail transition, spatial
  composition, environmental hierarchy, landmark navigation, cover placement,
  flow, pacing through space, skybox design, skybox cubemap, atmosphere design,
  volumetric fog, kitbashing, kitbash workflow, modular asset reuse, or any
  question about how to design a game environment, space station, spaceship
  interior, or outdoor level from a spatial and craft perspective.
hub: lead-3d-designer
aliases: [3d-spatial-design-for-games]
tier: spoke
domain: design
prerequisites: [lead-3d-designer]
spec_version: "2.0"
---

# 3D Spatial Design for Games

Specialist lens for game environment design, modular kit craft, and spatial
composition. Part of the `lead-3d-designer` skill network.

---

## Domain Boundary

This skill owns **spatial design decisions** — how to design and compose 3D
environments for games, with emphasis on modular workflows, human scale, and
environmental storytelling.

- **Modeling topology and mesh construction** → `3d-modeling-fundamentals`
- **Material authoring, trim sheets** → `3d-materials-shading`
- **Lighting design and mood** → `3d-lighting-rendering`
- **Game systems, level design intent (flow, objectives)** → `lead-game-designer`
- **Asset export, engine import** → `3d-asset-pipeline`
- **Faction aesthetics, art direction** → `lead-art-director` (Legion)

---

## Environmental Storytelling Principles

Environmental storytelling communicates narrative, history, and world logic through
the physical arrangement of objects and spaces — without cutscenes, dialogue, or
explanatory text. The player reads the room.

### The Lived-In Test

A space fails environmental storytelling if it looks like it was built for the player
to walk through. A space passes when it looks like it existed before the player arrived
and will continue after they leave.

Techniques:
- **Asymmetric wear**: Floors worn smooth along the most-walked path; corners and
  edges showing accumulation (dust, oxidation, boot scuffs)
- **Evidence of use**: Personal items out of place, work half-finished, equipment
  in mid-task state
- **Scale of purpose**: A large room with heavy lifting equipment and floor-marked
  loading zones reads as cargo handling before a sign is placed
- **Conflict evidence**: Scorch marks, dented panels, emergency lighting still active —
  something happened here
- **Hierarchy of care**: High-traffic / high-importance areas are well-maintained;
  forgotten corners are neglected

### Hierarchy Reads from Distance

Environmental hierarchy must work across three reading distances:

- **Silhouette (far)**: The overall form of the space. Is it tall and narrow (tension)?
  Wide and open (safety/exposition)? Curved (organic, unfamiliar)?
- **Mass (medium)**: Structural elements, large props, lighting zones — navigational
  landmarks readable at 30–50m
- **Detail (close)**: Surface texture, prop storytelling, decal narrative — readable
  at 2–5m

A space that only reads well up close fails the design. A player navigating by
landmark needs the medium-distance layer. Cinematic screenshots need all three.

---

## Modular Kit Design

Modular kit design is the systematic decomposition of an environment into
interchangeable, connectable pieces. It is the primary production workflow for
game environment art — especially for spaces like Legion's space stations and
ship interiors that have consistent structural logic.

### Grid System and Snap Units

Every modular kit is built on a grid. The grid determines:
- How pieces connect (they must align at connectors)
- How the designer assembles spaces (they snap to the grid)
- How LODs, collision, and lightmap UVs are structured (grid-aware)

**Choosing a grid unit**: Base the grid on human scale. A door is typically
2m wide × 2.2–2.4m tall. A corridor module should be a multiple of door width.
Standard convention: 2m grid (200cm base unit) for interior environments.

**Connector discipline**: Every module has defined connection points — typically
at face centers aligned to the grid. A connector point commits to:
- Exact position (must be at grid)
- Facing direction (normal vector out of the face)
- Size (must match connecting modules)
- Socket type (floor-to-floor, wall-to-wall, ceiling-to-floor, diagonal)

**Anti-pattern**: Modules that "mostly fit" — pieces that look right in one
orientation but don't snap cleanly. Breaks the system the first time a designer
tries to use them in combination.

### Modular Kit Categories for Interiors

A complete space station interior kit typically includes:

| Category | Pieces |
|----------|--------|
| Corridor straights | 1m, 2m, 4m lengths |
| Corridor turns | 90° and 45°, both wall-wall and floor-ceiling curve variants |
| T-junction / 4-way junction | Open intersections |
| Stairwell | Single-flight, landing pieces |
| Transition | Corridor-to-room threshold, widening/narrowing |
| Room walls | Flat panels 1×1m, 2×2m, 4×2m |
| Room floors | Flat tiles, grated floor tiles |
| Room ceilings | Flat, with conduit routing |
| Doorframes | Standard size, bulkhead / pressure door |
| Structural column | Vertical support |
| Conduit | Horizontal and vertical pipe/conduit runs |

**Trim sheet compatibility**: All kit pieces should UV to the same trim sheet.
This means every piece that uses a flat wall surface maps to the same horizontal
strip, and every floor piece maps to the same floor strip. Zero texture variation
budget — the trim sheet provides all variation.

### Kit Variant Strategy

A single kit piece with three material variants creates 3× the visual variety at
no additional mesh cost:
- **Clean**: Standard operational state
- **Damaged**: Dented, scored, breached
- **Emergency**: Warning-stripe markings, emergency lighting conduit

Variants are material swaps (or material layer toggles in engine), not separate meshes.
Design the kit piece once; author material variants in Substance Painter using material
ID layers.

---

## Human Scale and Proportion Calibration

Scale errors break spatial believability faster than almost any other artifact.
A corridor that is 80cm wide feels like a dollhouse; one that is 4m wide with
no reference objects reads as an empty warehouse.

### Scale Reference Objects

Always include scale reference objects in a scene while authoring:
- A 1.75m tall biped figure placed in key positions
- A standard door opening (2.0m × 2.2m)
- A seated workstation (desk height ~0.73m, monitor top ~1.4m from floor)

Place the biped in corners, doorways, and at key feature points. If it looks wrong,
something is wrong.

### Space Station Scale Reference (Legion)

For Legion's Von Neumann probe and station interiors:

| Space | Width | Height | Length |
|-------|-------|--------|--------|
| Maintenance corridor | 1.5–2.0m | 2.2m | Variable |
| Primary corridor | 2.5–3.0m | 2.5m | Variable |
| Airlock | 2.0m × 2.0m floor | 2.4m | 3–4m deep |
| Command deck (bridge) | 8–12m | 3.5m | 10–15m |
| Docking bay (small craft) | 12–20m | 8–12m | 15–25m |
| Reactor room | 10–15m | 12–20m | 10–15m |
| Fabrication/replication bay | 15–25m | 10–15m | 20–30m |

These are design targets, not hard constraints — but they must read as plausible
working spaces when a ~1.75m humanoid reference figure is placed inside them.

### Megastructure Scale Communication

At megastructure scale (Dyson shell, orbital ring, generation ship), human-scale
reference objects cannot be included literally. Communicate scale through:
- **Scale hierarchy**: Smaller structures (ships, platforms) that themselves dwarf
  human scale, nested against the megastructure
- **Forced perspective**: Camera framing that places small objects in the foreground
  against the incomprehensible background
- **Atmospheric perspective**: Even in space, depth cues through haze layers,
  star density falloff, and lighting color temperature shift with distance
- **Text and navigational graphics** embedded in the environment — scale labels,
  sector markers — which imply rather than show the human reference

---

## LOD Design Philosophy

Level of Detail (LOD) is a system that swaps a high-polygon mesh for progressively
lower-polygon versions as the object recedes from the camera. The design question is
not just "how many polygons" but "where do forms collapse, and does the object still
read at that distance?"

### When to Author LODs vs. Auto-Generate

**Author manually when**:
- The asset is a hero prop or architectural element with designed silhouette at multiple
  distances — auto-generation will collapse important read-at-distance forms
- The asset contains interior cutaways visible only at LOD0 — auto-generated LOD1
  may expose invisible interior geometry that was never modeled
- The asset is a modular piece used hundreds of times in the scene — every polygon saved
  at LOD1 multiplies across all instances

**Auto-generate when**:
- The asset is a background fill prop with no designed distant silhouette
- Time budget doesn't allow manual LOD (prototype stage)
- Asset is complex organic form where manual LOD is expensive and auto is acceptable

**LOD pipeline tools**: Blender LOD modifier (Decimate), Houdini's Labs LOD node,
Unreal Engine's Automatic LOD Generation (HLOD), Unity's LOD Group component.

### LOD Transition Visibility

LOD pops — the visible switch between LOD levels — are the main quality failure mode.
Reduce pop visibility:
- **Screen space threshold**: Switch at screen coverage percentage, not fixed distance.
  A large object should hold LOD0 further than a small one.
- **Dithered crossfade**: Engines support alpha-dithered blending between LOD levels
  (Unity: LOD Group cross-fade; Unreal: Dithered LOD Transition). Eliminates hard pop
  at the cost of transparency rendering cost for one frame.
- **Silhouette preservation**: At LOD1 and LOD2, any silhouette edge that's visible
  at the transition distance must survive. The transition is only acceptable if the
  eye does not track the pop.

### LOD Budgets by Asset Tier

| Asset | LOD0 | LOD1 | LOD2 | LOD3 / Billboard |
|-------|------|------|------|-----------------|
| Hero prop | Full | 50% | 25% | Not applicable |
| Environment prop (interactive) | Full | 30–40% | 15% | — |
| Environment prop (background) | Full | 25% | 10% | Billboard at distance |
| Large structure module | Full | 40% | 20% | Imposter at far distance |

---

## Legion-Specific Spatial Design

### Von Neumann Probe Interior Logic

The Bobiverse aesthetic establishes that Bob-built structures are functional-first.
Design principles:
- **No wasted volume**: Every corridor is as narrow as practical. Every room is
  sized to function, not to impress.
- **Utility hierarchy**: Frequently-accessed systems are closest to the center
  spine of the probe. Rarely-accessed maintenance is in the outer ring.
- **Visual language of engineering**: Exposed conduit and ducting is fine — it is
  practical and tells the reader "this was designed by an engineer, not an architect."
- **The exception is the Virtual Reality Space**: Bob's VR environment is intentionally
  beautiful, baroque, and spatially generous — a deliberate contrast to the functional
  exterior.

### Space Station and Spaceship Interior Design

Key design beats for Legion environments:

**Corridors** — the connective tissue of any space environment:
- T-junctions and 4-way intersections should have visual differentiation
  (a landmark: colored signage, a unique structure piece, a view port) to aid navigation
- Dead ends should be visually distinct (storage alcoves, maintenance terminations)
- Curvature communicates structure: curved corridors follow the hull line; straight
  corridors are deep-interior axial

**Command Deck / Bridge** — the player's primary operational space in Legion:
- Dominance of forward orientation — all major stations face or angle toward the
  main viewscreen
- Tiered floor plan if space allows — command chair elevated slightly for visibility
- Console density proportional to crew size: a Bob-piloted probe bridge is intimate
  and functional; a crewed multi-faction station is busy and complex

**Fabrication / Replication Bay** — central to the Von Neumann gameplay loop:
- Visual representation of the construction pipeline: raw feed → processing → assembly
  → output staging
- Scale communicates power: a large bay with visible work volume signals advanced capability
- Exposed mechanisms are desirable — they communicate function

### Kitbashing Workflow

Kitbashing starts with a library of parts (mechanical panels, greeble surfaces,
conduit sections, structural connectors) assembled in novel combinations to create
unique-looking hero assets without modeling from scratch.

**Workflow**:
1. Establish the primary silhouette shape (modeled clean)
2. Import kitbash library pieces to the scene
3. Boolean or surface-project the kitbash pieces onto the primary form
4. Select the most interesting combination; delete or hide rejected iterations
5. Weld and clean the final mesh; bake down to the clean low-poly

**Kitbash libraries**: KitBash3D, Sci-Fi Constructor (Blender Market), HardMesh
components. Or build a project-specific library from reused modular kit pieces.

---

## Cross-Links

| Skill | Relationship |
|-------|-------------|
| `3d-modeling-fundamentals` | Modular kit pieces need clean, connector-aligned topology; gridded edge loops at snap faces |
| `3d-materials-shading` | Trim sheet authoring and material ID workflow are the texture strategy for modular kits |
| `3d-lighting-rendering` | Spatial hierarchy must be readable under the target lighting; landmark placement is a lighting + spatial collaboration |
| `3d-asset-pipeline` | LOD generation, collision mesh generation, and engine import for modular pieces |
| `lead-game-designer` | Spatial flow, navigational intent, cover placement, and zone pacing are game design decisions that constrain spatial design |
| `anthropic-skills:lead-art-director` | Faction aesthetic and visual language decisions sit with art direction; spatial design executes that direction |

## Related
- hub → [[lead-3d-designer]]
