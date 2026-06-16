---
name: 3d-lighting-rendering
description: >
  Lighting design and rendering from the 3D artist/designer perspective. Use this skill
  whenever the conversation touches: lighting design, three-point lighting, one-point
  lighting, key light, fill light, rim light, back light, directional light, point light,
  spot light, area light, HDRI lighting, image-based lighting, IBL, HDRI workflow, real-
  time lighting, baked lighting, lightmaps, light probes, Lumen, SSAO, SSR, Blender Cycles,
  Blender EEVEE, Arnold, Redshift, Marmoset Toolbag, Unreal Engine rendering, camera
  composition, depth of field, focal length, rule of thirds, linear workflow, ACES, sRGB,
  filmic tone mapping, OpenColorIO, or any question about how to light a scene or set up
  a render. This skill covers lighting design and render decisions — not shader code
  (glsl-shader-architect), material authoring (3d-materials-shading), or engine technical
  setup.
hub: lead-3d-designer
aliases: [3d-lighting-rendering]
tier: spoke
domain: design
prerequisites: [lead-3d-designer, imaging-foundations]
spec_version: "2.0"
---

# 3D Lighting and Rendering

Specialist lens for lighting design and rendering decisions. Part of the
`lead-3d-designer` skill network.

---

## Domain Boundary

This skill owns **lighting design and rendering decisions** — how to light a scene,
which render engine to choose, and how to compose and frame a shot.

- **Material authoring, PBR values** → `3d-materials-shading`
- **Shader code, procedural effects** → `glsl-shader-architect`
- **Real-time engine architecture** → engineering/lead-game-developer territory
- **Mesh construction** → `3d-modeling-fundamentals`
- **Game environment layout** → `3d-spatial-design-for-games`

---

## Lighting as a Design Tool

Lighting is not a technical afterthought — it is one of the three fundamental
authorship decisions in 3D work (alongside form and material). Lighting:

- **Reveals form**: The interplay of light and shadow makes 3D shapes readable. A
  sphere is a circle without lighting.
- **Establishes mood**: Color temperature (warm vs. cool), intensity (bright vs.
  dim), and direction (from above vs. below) carry emotional weight.
- **Directs attention**: A bright key light draws the eye. A dark area recedes.
- **Sets time and place**: Noon sun (overhead, high color temperature) reads
  differently from golden hour (low angle, warm, long shadows).

The lighting designer's job is to make these decisions intentionally — not to "add
light until the scene is bright enough."

---

## Classical Lighting Setups

### Three-Point Lighting

The foundational controlled-environment setup. Three lights, three distinct roles:

**Key Light** (primary)
- The dominant light source. Defines the main direction of illumination.
- Typical placement: 30–45° to the side of the camera, elevated 30–45° above
  the subject.
- Sets the exposure baseline for the scene.
- Hard vs. soft edge: hard key (small source, directional sun) for drama and
  crisp shadows; soft key (large area light, overcast sky) for flattering, subtle shadow.

**Fill Light** (secondary)
- Softens the shadow side created by the key. Not the opposite of the key — the
  shadow side still reads as shadow.
- Intensity: 25–50% of key intensity (fill ratio 2:1 to 4:1). Higher fill = flatter
  look. Lower fill = more dramatic.
- Placement: opposite side from key, low angle or from camera direction.
- Usually a soft/diffuse light. Rarely casts sharp shadows.

**Rim / Back Light**
- Placed behind the subject, opposite the camera, slightly to one side.
- Creates a halo of light along the subject's silhouette — separates the subject
  from the background.
- Intensity: 10–25% of key (enough to read, not enough to dominate).
- Critical for preventing subjects from merging with dark backgrounds.

### One-Point Lighting

Single source. High contrast. Dramatic, noir, cinematic.
- Classic use: a single window light, a fire, a lamp.
- The fill is the environment itself (GI or ambient). No explicit fill light.
- Shadow density and direction carry the entire mood.

### Two-Point Lighting

Key + rim only. No fill. Clean backgrounds, product shots, technical presentation.
- The subject is separated from background (rim) and lit clearly (key), without the
  softening of a fill light.
- Used when you want the shadow side to stay dark and the background to stay clean.

---

## Light Types

### Directional Light (Sun)

- Infinitely far away — parallel rays, consistent shadow direction across the scene.
- Represents the sun, moon, or any large, distant light source.
- Cast hard shadows at 0° softness; soft shadows with angular diameter set > 0.
- The direction is set by the light's rotation, not its position.

**Game engine use**: One per scene, maximum. The dominant outdoor light. Combined
with sky dome for ambient.

### Point Light (Omni)

- Emits light in all directions from a single position. Spherical falloff.
- Physical falloff: intensity ∝ 1/distance² (inverse square law).
- Radius/sphere setting: defines the physical size of the source (affects shadow
  softness) and often the maximum influence range.
- Use: interior practical lights (lamps, candles, screens), emergency lighting.

### Spot Light

- Point source constrained to a cone. Inner angle (umbra) and outer angle (penumbra).
- Inner-to-outer gap creates the soft edge. Large gap = gradual falloff; small gap =
  sharp-edged beam.
- Use: focused practical lights (flashlights, engine jets, stage lighting), hero
  highlights on key objects.

### Area Light

- Emissive planar surface. Physically accurate soft shadows (shadow softness scales
  with source size and distance).
- Blender Cycles: true area light. EEVEE: approximation using LTC (Linearly
  Transformed Cosines — good approximation, not physically exact).
- Real-time engines approximate area lights — at significant performance cost.
- Use: windows, monitors, soft box studio lighting, architectural overheads.

### HDRI / IBL (Image-Based Lighting)

The dominant workflow for product visualization, character renders, and any work
where environmental lighting matters.

- A 360° panoramic HDR image captures real-world light from all directions, including
  color, intensity, and highlights.
- Applied to an environment sphere, it provides both the ambient light and reflections
  for every surface in the scene simultaneously.
- Result: materials that look like they're really in the environment because they are
  reflecting that environment.

---

## HDRI Workflow

### Selecting an HDRI

Key properties to evaluate:
- **Dynamic range**: A good HDRI captures from deep shadow to bright sun highlight —
  10–14 stops. Low-range HDRIs produce flat, uninspiring lighting.
- **Dominant light direction**: Where is the brightest point? This acts as the sun.
  Orient the HDRI so this aligns with your intended key direction.
- **Color temperature**: Warm (golden hour, studio), neutral (overcast, shade), or
  cool (dusk, night). Match the mood of the scene.
- **Resolution**: 4K–8K HDRIs give sharp, artifact-free reflections. 1K is too
  low for reflective surfaces (blocky reflections visible).

Free sources: Poly Haven (CC0, high quality). Sketchfab HDRIs.

### HDRI Rotation

The HDRI is rotated around the vertical (Y/Z) axis to change the direction of the
dominant light. Workflow:
1. Add the HDRI to the environment
2. Use rotation to point the bright spot at your subject from the desired direction
3. Add a directional light (sun) aligned to that bright spot for sharper, controllable
   shadows — the HDRI provides ambient and reflection; the directional provides the
   defined key shadow

### HDRI as Sole Light Source

Without a supplementary light, the HDRI provides: ambient light, indirect bounced
light, and reflections. Results are naturalistic but may lack the directional control
needed for intentional composition. Often sufficient for environment renders; often
supplemented with a directional for hero shots.

---

## Real-Time Lighting

### Baked vs. Dynamic

| Approach | Performance | Flexibility | Visual Quality |
|----------|------------|-------------|---------------|
| **Baked Lightmaps** | Excellent — zero runtime cost | None — lights can't move | High — full GI, no approximation |
| **Dynamic (real-time)** | Costly — computed every frame | Full — lights move freely | Lower without GI; depends on tech |
| **Hybrid** | Good — static baked + dynamic for characters | Moderate | Good |

**Baked lightmaps**: Unity Lightmapper, Unreal Lightmass. Requires a second UV
channel (Lightmap UVs) with no overlapping islands. Bake times scale with scene
complexity and quality settings. Best for static architecture and environments.

**Dynamic**: Every frame, the engine computes light → surface interaction.
Performance-limited. Without GI, looks flat. With GI (Lumen), approximated.

### Lumen (Unreal Engine 5)

Lumen is UE5's fully dynamic global illumination system. It uses:
- **Ray tracing** (hardware or software)
- **Signed Distance Field** surface representations
- **Screen-space probes** for irradiance

Result: indirect lighting that updates in real time as lights move. Comparable to
baked quality for many scenes. Cost: GPU-intensive. Not viable for mobile.

### Light Probes (Unity)

Probes placed throughout the scene sample the baked irradiance. Dynamic objects
(characters, vehicles) interpolate between nearby probes to receive correct indirect
lighting without bake cost.

- **Light Probes**: Low resolution, sampled per object. Fast. Use for moving objects.
- **Reflection Probes**: Local reflections capture. Higher resolution. Use for
  reflective surfaces in specific areas (a metal floor, a pool of water).

### SSAO and SSR

**Screen-Space Ambient Occlusion (SSAO)**: Approximates contact shadow in crevices
and corners from depth buffer data. Only works for surfaces visible on screen
(camera-space effect). Fast and nearly universal in real-time engines.

**Screen-Space Reflections (SSR)**: Approximates reflections by tracing through the
depth buffer backward. Fails for off-screen objects (reflections disappear as objects
leave the frame). Use with Reflection Probes as fallback.

---

## Render Engines

### Blender Cycles

- Unbiased path tracer. Physically accurate. CPU and GPU (CUDA, Metal, OpenCL).
- Path tracing: follows light paths until they decay. Requires many samples for
  noise-free results. Each sample reduces noise by `1/√samples`.
- Use for: character renders, product visualization, animation frames, any output
  where physical accuracy matters and time is available.
- Denoiser (OptiX, Open Image Denoise): enables low-sample rendering with acceptable
  noise for fast iteration.

### Blender EEVEE

- Rasterization-based with ray-tracing approximations (EEVEE Next in Blender 4.x).
- Near-instant renders. Interactive viewport lighting.
- Approximations: screen-space effects, probe-based GI, LTC area lights.
- Use for: previz, layout review, stylized work, real-time game feel preview, any
  output where speed > physical accuracy.
- EEVEE Next adds ray-traced shadows and reflections — narrows the quality gap
  significantly.

### Arnold (Maya)

- Production Monte Carlo path tracer. The industry standard for film and TV VFX.
- CPU-primary (GPU option exists). Integrates with Maya.
- Strong volume rendering (clouds, smoke, fire).
- Use when the deliverable is film/TV VFX or when the studio pipeline requires it.

### Redshift

- GPU-accelerated path tracer (Maxon/Chaos). Very fast compared to CPU renderers.
- Works with Maya, Cinema 4D, Blender, Houdini.
- Production-quality output at significantly faster render times than CPU Arnold.
- Use for: studio production work that needs fast turnaround with high quality.

### Marmoset Toolbag

- Real-time PBR renderer designed for asset presentation.
- The industry standard for game asset screenshots, portfolio renders, and texture
  baker.
- Set up a scene in minutes; render quality immediately.
- Also the best standalone baking tool (high-poly → low-poly normal bakes).
- Use for: game asset presentation, quick portfolio renders, normal map baking.

---

## Composition and Camera

### Compositional Principles in 3D

**Rule of thirds**: Divide the frame into a 3×3 grid. Place the subject at one of
the four intersection points. Avoid dead-center unless the composition is deliberately
formal or symmetrical.

**Leading lines**: Lines in the scene (corridors, road edges, architecture) that lead
the eye toward the subject. In 3D level design, leading lines guide the player toward
their objective.

**Depth / Scale contrast**: Foreground, midground, background layers create
spatial depth. A small object in the foreground next to a large background structure
establishes scale. Crucial for megastructure shots in Legion.

**Framing**: Use architectural elements, environment geometry, or volumetric effects
to frame the subject (a doorframe, a canyon, fog depth). Natural framing gives the
eye a structure to follow.

### Depth of Field

DoF as a compositional tool (not just a photographic simulation):
- **Focal length**: Longer focal lengths (85mm+) compress background relative to
  subject (subjects pop from background). Short focal lengths (24mm) exaggerate
  foreground depth.
- **f-stop**: Lower f-stop = wider aperture = shallower DoF (more background blur).
  Higher f-stop = sharper everything.
- **Focus distance**: Where the plane of sharpness sits. Keep the most important
  element in sharp focus.

DoF draws attention by blurring everything except the focus subject. Use to reduce
visual noise in busy environments and guide the viewer's eye.

### Camera Types

- **Perspective**: Standard — objects appear smaller with distance. Natural,
  photorealistic.
- **Orthographic**: No perspective foreshortening. Used for technical renders,
  UI element icons, isometric game art.
- **Anamorphic**: Wider aspect ratio (2.35:1+), characteristic lens flare streaks.
  The cinematic feel. Use for cutscenes and key art.

---

## Color Management

### The Linear Workflow

3D rendering works in **linear light** (scene-referred). Raw renderer output is
linear — a value of 0.5 is exactly half as bright as 1.0, as real light behaves.

Display devices use **gamma-corrected / display-referred** space (sRGB). A gamma
curve is applied at the end to convert linear → display.

**Why this matters**: If textures are authored in sRGB and imported without correction
into a linear renderer, they'll look too bright (gamma baked in twice). PBR relies on
correct linear inputs. This is why:
- Albedo maps: import as sRGB (engine applies gamma correction on import)
- Normal/roughness/metalness/AO: import as Linear (no gamma correction — these
  are data, not display color)

### ACES (Academy Color Encoding System)

The film industry standard tone mapping and color space system.

- Scene-referred: encodes light as physical values, not display values
- Tone mapping transforms HDR scene values to displayable range with film-like
  rolloff in highlights (not a hard clip)
- Result: highlights compress rather than clip, giving a more photographic look

ACES in Blender: use the Filmic or ACES transform (via OpenColorIO config).
ACES in Unreal Engine: built-in tone mapper setting.

### Blender Filmic

Blender's built-in tone mapping alternative to raw sRGB display.
- Soft highlight rolloff (similar film-like behavior to ACES)
- Available in Render Properties → Color Management → View Transform

The default Blender view transform is not Filmic — switch to it immediately for
production work.

### OpenColorIO (OCIO)

The open standard for color space management in VFX and film pipelines.
Allows all applications in a pipeline (Blender, Nuke, Photoshop with plug-in,
DaVinci Resolve) to use the same color space definitions — no color shifts between
applications. When working on a multi-app pipeline, confirm OCIO config version.

---

## Quality Checklist

Before delivering a lighting/rendering setup:

- [ ] Scene-referred linear workflow is active (correct sRGB vs. linear import per
      map type)
- [ ] Tone mapping applied (Filmic, ACES, or equivalent — not flat sRGB)
- [ ] Three-point (or intentional single/two-point) setup in place with deliberate
      fill ratio
- [ ] Rim/back light separates subject from background
- [ ] HDRI rotation aligns dominant light with intended key direction
- [ ] Camera focal length chosen for intended composition effect
- [ ] DoF set with focus on the primary subject
- [ ] Composition uses rule of thirds or has a deliberate reason to violate it
- [ ] Render samples sufficient for noise-free output (or denoiser applied)
- [ ] No color clipping in highlights (verify with false-color or histogram)
- [ ] All lights have physically plausible intensity and color temperature
- [ ] Real-time: shadow and reflection probe placement covers all hero surfaces

## Related
- foundation → [[imaging-foundations]]
- hub → [[lead-3d-designer]]
