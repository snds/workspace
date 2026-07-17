---
tags: [cross-domain, failure-modes, visual, rendering, shaders, qa, pre-mortem, knowledge-vault]
created: 2026-07-14
updated: 2026-07-14
status: working
confidence: high
sources: [framework 11-anticipatory-failure-analysis, framework 10-perception-integrity, skill failure-mode-premortem]
related_skills: [failure-mode-premortem, native-visual-eval, visual-qa-toolkit, lead-visual-qa, threejs-materials-master, glsl-shader-architect, threejs-vfx-atmosphere]
related_projects: [13-legion]
domain_agnostic: true
---

# Visual Failure-Mode Ledger

**The externalized memory behind framework [#11 Anticipatory Failure Analysis](../../01-frameworks/11-anticipatory-failure-analysis.md) and the [`failure-mode-premortem`](../../03-skills/failure-mode-premortem/SKILL.md) skill.** Technique-keyed rows of *how a visual technique classically fails and how to catch it in a frame* — so the "classic symptom" is retrieved **by technique-name at planning time**, not recalled by symptom after the artifact ships.

This is **domain-agnostic by design.** Rows are keyed by *technique / pipeline stage*, never by project. Legion is the test-bed that seeded the first entries; the ledger governs any visual work in any project. Consult it in **step 2** of the pre-mortem; add to it via the **self-improving loop** (bottom).

Each row: **Symptom** (what's wrong) · **Visible tell** (how it looks at native res) · **Root cause** · **Prevention** (do this at build time) · **Detect** (how to spot it in a produced frame) · **Ref/tier** (source + confidence per #04).

---

## A · Rendering pipeline & post-processing

| ID | Technique / stage | Symptom | Visible tell (native res) | Root cause | Prevention | Detect | Ref/tier |
|----|----|----|----|----|----|----|----|
| **A-01** | Volumetric / glow / gradient through a tonemapper, 8-bit output | Banding | Concentric stepped isolines in the falloff; worst on dim, low-contrast gradients | 8-bit quantization applied *after* tonemap; too few raymarch steps | Blue-noise/ordered dither *before* quantize; float (RGBA16F) render targets through the chain; jitter step origin; more steps in dim regions | Native crop of the falloff — look for stepped contours, not a smooth ramp. `native-visual-eval` mandatory; the defect vanishes in a thumbnail | Legion volumetric-banding case (#10); industry-supported |
| **A-02** | Screen-space dither / blue-noise applied in screen space | Pattern "crawl" / shimmer under camera motion | Static-looking grain that swims or boils as the camera moves | Dither pattern fixed to screen pixels, not to the surface/world | Anchor noise to world/UV space, or animate the noise with a temporally stable sequence (e.g. per-frame golden-ratio offset + TAA) | Judge **in motion**, not on a still — a static frame looks fine. Record and step frames | Industry-supported |
| **A-03** | Bloom / emissive threshold | Hard ring / abrupt halo at emitter edge | A crisp bright ring outlining the emissive shape instead of a soft falloff | Hard threshold cutoff; single-pass blur; bloom applied to clipped (already-white) values | Soft knee on the threshold; multi-scale (mip pyramid) blur; bloom in HDR *before* tonemap/clip | Native crop across the emitter edge — soft gradient (correct) vs. stepped ring (wrong) | Industry-supported |
| **A-04** | Additive blending (particles, energy FX) | Blowout to flat white where sprites overlap | Detail-less white blobs in dense/overlapping regions | Unbounded additive accumulation clips at 1.0 | HDR target + tonemap; cap per-particle contribution; consider energy-conserving blend | Native crop of the densest overlap — is there structure, or a clipped white mass? Check the histogram for a spike at max | Industry-supported |
| **A-05** | Post-process read as render artifact | Wrong layer blamed for the defect | 8×8 blocky artifacts or edge ringing that look like render banding/halos | JPEG/lossy *capture* of the frame, not a render defect at all | Capture/save **PNG (lossless)** before judging banding or edges (per #10) | If the "banding" is on an 8×8 grid, it's the codec — recapture lossless | #10 corollary; high |
| **A-06** | "Draw-first" backdrop (skybox stars/points) with `transparent: true` + `depthTest: false` (three.js & similar sorted renderers) | Background stars/backdrop shine *through* every opaque foreground body | Sharp star points visible ON a planet/sun disc, worst against dark surface regions; screen-fixed while the body rotates under them (they survive a temporal median across frames) | `transparent: true` schedules the material in the **transparent pass, after ALL opaque geometry** — `renderOrder` only sorts *within* a pass, so "drawn first" is silently defeated and `depthTest: false` lets it composite over everything | For a backdrop meant to be overdrawn: `transparent: false` (blend mode is honoured per-material regardless of the flag in three.js) so it renders in the opaque pass where a negative renderOrder truly runs first | Put an opaque body in front of the backdrop and inspect its dark limb at native res; verify at runtime which pass the material is in (`material.transparent`), not just its renderOrder | Legion star-field case, 2026-07-16 (long-standing; frame-extracted video repro); evidenced |

## B · Color, light & material

| ID | Technique / stage | Symptom | Visible tell (native res) | Root cause | Prevention | Detect | Ref/tier |
|----|----|----|----|----|----|----|----|
| **B-01** | sRGB / linear color management | Washed-out or muddy-dark result; lighting looks flat | Colors too pale (double-gamma) or midtones crushed (missing decode) | Mixing sRGB and linear values; textures not decoded; output not encoded | Decode albedo/emissive textures to linear on read; work in linear; encode to sRGB at output only | Compare a known mid-grey against the reference; check that 50% grey reads as 50% perceptually | Industry-supported |
| **B-02** | PBR at grazing angles | Surface goes flat/dark or unnaturally bright at glancing view | Missing rim energy, or a too-hot Fresnel edge | No multi-scatter / energy compensation; wrong Fresnel; roughness mis-authored | Use energy-conserving BRDF (multi-scatter GGX); verify Fresnel term; sanity-check roughness range | Rotate to a grazing angle and compare edge behavior to the material reference | Industry-supported |
| **B-03** | Normal maps / tangent space | Lighting seams or inverted bumps | Visible seam at UV boundaries; bumps that light "backwards" | Mirrored-UV handedness; green-channel convention (OpenGL vs DirectX) flipped | Match the engine's normal-map convention; handle mirrored-UV tangent sign; check seams at authoring | Light from a known direction — do bumps rise toward the light? Inspect UV seams native-res | Industry-supported |

## C · 2D / UI / design surfaces

| ID | Technique / stage | Symptom | Visible tell (native res) | Root cause | Prevention | Detect | Ref/tier |
|----|----|----|----|----|----|----|----|
| **C-01** | Foreground text/icon on full-bleed image or gradient | Illegible in the worst region | Text disappears over a light or busy patch of the image | Contrast verified against an average, not the worst-case local background | Verify APCA (preferred) / WCAG AA against the *worst* local region; add scrim/plate if needed | Sample the foreground vs its local background at the hardest point; run APCA — don't eyeball | Framework #06 a11y check; evidenced |
| **C-02** | Status/meaning carried by color | CVD users lose the signal | Two states distinguishable only by hue (red/green) | Meaning rides on color alone | Add a non-color channel (icon, label, shape); simulate CVD | Run a deuteranopia/protanopia sim (`visual-qa-toolkit`); is the state still readable? | #06 a11y check; evidenced |

## P · Procedural generation (terrain / planets / worlds)

| ID | Technique / stage | Symptom | Visible tell (native res) | Root cause | Prevention | Detect | Ref/tier |
|----|----|----|----|----|----|----|----|
| **P-01** | Continents as radial spherical caps / distance-field-from-seed (thresholded) | Circular "glob" landmasses; peanut shapes where two meet | Continents have a visible common center; smooth oval coastlines; no bays/peninsulas/islands | Land = a purely *radial* function of angular distance from a seed point → an iso-contour of a smooth field is a circle. Coastline dimension ≈1.0 | Define land by thresholding a **fractal** field: multi-octave fBm (warped), with cap seeds as a low-frequency *bias* only — never the coastline itself. Coastline = iso-contour of fBm → fractal dimension ≈1.2–1.3 | Trace the coastline — is it a wavy circle (wrong) or self-similar bays/peninsulas at multiple scales (right)? Look for a shared center across continents | Legion planet-lab `plates.ts` `macroHeight`; Mandelbrot/Richardson coastline dimension; evidenced |
| **P-02** | Domain warp applied to a fundamentally circular primitive | Coasts wobble but stay round; warp slider "does nothing useful" | Gently wavy circles, not fractal coasts, at any warp setting | Warp perturbs the *lookup direction* of a smooth radial cap; at feature-scale the wiggle is small vs the cap radius, so topology stays circular | Warp must act on a field that already has mid-frequency structure (P-01 fix), and at amplitude comparable to the feature size; multi-octave warp; raise the warp ceiling | Sweep the warp slider to max — if coasts stay closed ovals, the primitive (not the warp) is the problem | Legion `glsl.ts` `terrainHeight`; industry-supported |
| **P-03** | Fractal detail added as height relief *after* a dominant smooth macro | Coastline won't fractalize even with detail cranked | Fine bumps on land, but the land/sea line is still smooth | Detail amplitude (relief) is small vs the macro ramp at the sea-level crossing, and it's added to *height* rather than perturbing the land/sea *threshold* | Perturb the land/sea threshold with mid-freq fBm at amplitude comparable to the macro edge slope (≈0.2–0.3), so the sea-level contour itself meanders | Threshold a mid-freq noise into the mask and check the coast breaks into islands; compare detail amp vs macro slope at the waterline | Legion `terrainHeight` relief term; industry-supported |
| **P-04** | Tectonic ranges from raw Voronoi boundaries with constant along-edge uplift | Faceted / geometric mountain ranges; straight ridge "seams" | Ranges run as uniform straight walls along cell edges; uniform height along a segment | Boundary = nearest-vs-2nd-nearest seed (a Voronoi edge → great-circle arc); uplift & convergence are constant per plate-pair → uniform straight ridge | Warp the plate-distance field (independent seed) so boundaries meander; modulate uplift **along** the boundary with ridged noise so ranges vary in height and break into peaks | Look along a range — uniform straight wall (wrong) vs meandering, height-varying chain (right) | Legion `plateMacro` range term; industry-supported |
| **P-05** | Value noise used as a **domain-warp vector field** | Lattice-aligned creases; a "faceted"/polygonal cellular pattern returns after warping | Straight/axis-aligned crease lines across a surface that a warp was supposed to dissolve — worst on large, low-frequency warps | Value noise (integer-lattice + smoothstep interp) has axis-aligned gradients; as a *vector* warp it pushes features along lattice directions, so warped boundaries re-straighten and grid artifacts appear | Use gradient/simplex noise for warp **fields** (isotropic). Value noise is fine for a *scalar* threshold nudge (e.g. a coastline) but not for a directional warp. For CPU↔GPU parity, port the *simplex* noise to the CPU rather than substituting value noise on one side | Sweep warp to max — if straight cellular creases persist, the warp noise itself is anisotropic (not a strength problem) | Legion parity attempt, 2026-07-14 (caught + reverted pre-merge); **recurred 2026-07-16** as bake-detail value noise → lattice BLOCKS in baked bathymetry ("needn't match, only has to read organic" is the trap rationale); evidenced ×2 |
| **P-06** | Animated advection via **time-accumulating differential rotation** (zonal shear ∝ t) | Texture winds into smeared horizontal ribbons over minutes; looks fine in the first seconds | Cloud/flow pattern stretched into long thin latitude-parallel streaks; all patchy structure gone; worsens monotonically with time | Latitude-differential rotation angle grows without bound (`angle = shear(lat) · t`), so pattern shear accumulates forever — any static-frame check or short preview passes while long-run state degrades toward pure ribbons | Make the differential term a **bounded oscillation** (`A·shear(lat)·sin(ωt)`) riding on a uniform drift, and carry temporal evolution via a time-morphing noise warp instead; size `A` so the **max-shear frame** still reads correctly | Torture test: jump the time uniform far ahead (+400 s and to the sin-phase max) and re-judge at native res — never accept an animated field from its t≈0 frame | Legion cloud deck, 2026-07-16 (caught by motion torture test pre-merge; amplitude re-tuned after max-shear frame still marbled); evidenced |
| **P-07** | Per-tile/per-face processing (erosion, blur, sim) with a hard **untouched edge margin** for cross-tile continuity | Straight seam lines parallel to tile/face edges; meet in "V"/corner junctions; worsen as the process gets stronger | Crisp straight steps a fixed distance INSIDE each tile boundary (not at the boundary itself); the boundary line is fine — the step is where margin meets processed interior | The margin holds boundary texels at the continuous source so edges match — but that leaves a discontinuity between the untouched band and the heavily-processed interior; the stronger the process, the taller the step | **Feather, never gate**: ramp the process delta in smoothly over a band from the boundary (`v = pre + (post−pre)·smoothstep(dEdge/B)`); both sides then meet the continuous source with C0 continuity | Crank the per-tile process to maximum and inspect along/near tile boundaries at native res — hard margins hide at low strength and step at high | Legion bake erosion EDGE_MARGIN, 2026-07-16 (field report from deployed build; fixed with featherEdges); evidenced |

## Z · Meta (cross-cutting)

| ID | Technique / stage | Symptom | Visible tell | Root cause | Prevention | Detect | Ref/tier |
|----|----|----|----|----|----|----|----|
| **Z-01** | Judging any fine detail from a preview/screenshot tool | False "fixed / clean" | Thumbnail looks clean; native crop shows the defect still there | Downsampling is a low-pass filter that hides high-frequency defects | Never claim fixed/gone/matches from a scaled view — capture native first (#10) | State the pixel dimensions judged at; a number, not "I zoomed in" | Framework #10; evidenced |

---

## How to add an entry

Triggered in pre-mortem **step 2** (researching a technique with no row) or by the **self-improving loop** (Sean caught a bug I missed):

1. Pick the category (add a new letter section if genuinely new).
2. Assign the next ID in that section.
3. Fill all seven columns — the **Detect** column is the most valuable; it's what makes the row fire at the done-boundary.
4. Cite the source and name the confidence tier (per framework #04: evidenced / industry-supported / single-high-value / expert-judgment / preference).
5. Keep it **technique-keyed, not project-keyed** — write it so it applies wherever the technique is used.

## The self-improving loop

- **A visual bug slipped past me and Sean caught it → write the row now.** That exact classic symptom becomes proactive for next time. Capture at session-end.
- **A pre-mortem researched a new technique → its row is a side effect.** Commit it with the work.
- The second occurrence of any failure here is caught by the row the first one wrote. That is the whole point.
