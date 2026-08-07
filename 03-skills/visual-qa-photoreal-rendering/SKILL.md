---
name: visual-qa-photoreal-rendering
description: >
  Photoreal rendering evaluation lens — spoke of lead-visual-qa. Use when judging realtime or offline
  rendered frames for movie-level / northstar photoreal quality: energy conservation read, grazing
  Fresnel, GI/ambient plausibility, shadow contact and cascades, tonemap/exposure, post-process
  artifacts, and motion tells (TAA ghosting, dither crawl, volumetric banding, LOD pop). Explicit:
  do not close on a single frame when camera or interaction is part of the claim — require motion
  evidence per interactive-capture-eval. Distinct from visual-qa-game-design (gameplay readability /
  HUD / silhouette). Triggers: photoreal QA, lighting review, material review, Fresnel, tonemap
  artifacts, shadow acne, GI flatness, bloom rings, cinematic match.
aliases: [visual-qa-photoreal-rendering, photoreal-qa]
triggers: [photoreal qa, photoreal review, lighting review, material review, fresnel, grazing angle, energy conservation, gi quality, shadow cascade, tonemap, bloom artifact, post artifact, motion tell, taa ghosting, dither crawl, volumetric banding, cinematic lighting]
tier: spoke
hub: lead-visual-qa
domain: quality
prerequisites: [native-visual-eval]
related: [visual-qa-game-design, interactive-capture-eval, reference-video-review, realtime-visual-craft, rendering-guild, failure-mode-premortem, imaging-foundations, realtime-render-performance]
surfaces: ["*"]
spec_version: "2.0"
---

# Visual QA — Photoreal Rendering

Spoke of [[lead-visual-qa]]. Evaluates whether a rendered image (and its motion) reads as
**budgeted light transport** at the project's fidelity contract — usually movie-level / northstar-gated
per framework [#12](../../01-frameworks/12-realtime-photoreal-operational-framework.md).

This is **not** [[visual-qa-game-design]]. Game-design QA asks "can the player read threats and
objectives?" Photoreal QA asks "does the light, material, and temporal behavior hold against the
northstar and against physical craft tells?"

---

## Domain boundary

| Own | Hand off |
|---|---|
| Energy, materials, Fresnel, GI, shadows, tonemap, post, motion render tells | Gameplay readability / HUD / silhouette → [[visual-qa-game-design]] |
| Northstar still + motion match for look | Native capture method → [[native-visual-eval]] |
| Photoreal judgment | Multi-agent deadlock → [[rendering-guild]] |
| Craft / physics of forming the image | [[imaging-foundations]] |

Stack lenses when needed (e.g. readable night-side HUD **and** plausible night lighting).

---

## Preconditions (non-negotiable)

1. **Fidelity contract stated** — Literal / Spirit / Standard / Intent ([[lead-visual-qa]]).
2. **Native pixels** — #10 / [[native-visual-eval]]. Low-res previews are locators only.
3. **Motion when claimed** — if camera or interaction is in the claim, require
   [[interactive-capture-eval]] evidence. **Do not close on a single frame.**

---

## Evaluation lenses

### Energy

- Highlight roll-off vs crushed/clipped blowouts
- Shadow floor still carries form (not crushed to void unless intentional)
- No "brighten the scene" fill lights that destroy contrast hierarchy
- Exposure continuity across a path (no pump/flash frames)

### Grazing Fresnel

- Specular response rises at glancing angles on dielectrics
- Metals hold tinted specular without albedo cheat
- Fail: plastic dead rims, mirror-ball everything, Fresnel missing on wet/water/eyes

### GI / ambient

- Contact occlusion readable at object meetings
- Bounce / irradiance plausible for the time of day and sky
- Fail: marketing HDRI-only (shiny on gray void), flat ambient gray, screen-space GI swimming as "lighting"

### Shadows

- Contact tightness vs light size
- Cascade continuity under motion
- Fail: shadow acne, peter-panning, seam lines, swimming cascades, contact gaps

### Tonemap / exposure

- Middle-gray placement; highlight compression shape
- Hue shifts and posterization under gradients (sky, atmospheres, skin)
- Fail: judging linear/pre-tonemap buffers as final; ACES/other mis-applied twice

### Post artifacts

- Bloom threshold and **order** (bloom before tonemap in HDR; never evaluate swapped order as final)
- Halos, black rings, vignette crushing corners
- Grain/dither that is stable in stills but crawls under move

### Motion tells (required when camera/interaction in claim)

- TAA/TAAU ghosting on procedural / MV-less content
- Dither crawl; noise that sticks to screen vs world
- Volumetric banding under camera motion
- LOD pop / morph seams
- Disocclusion shimmer
- Origin-shift history corruption

---

## Single-frame rule

```
IF claim includes camera OR interaction OR temporal technique:
  REQUIRE path recording + frame-by-frame review
  FORBID done-verdict from one hero still
ELSE:
  native still grid may suffice for static look claims
```

---

## Output shape

```
## Photoreal QA: {target}
Contract: …
Evidence: still {native dims/tiles} · motion {paths / n/a}
Energy: … | Fresnel: … | GI: … | Shadows: …
Tonemap/post: … | Motion tells: …
Blockers: …
Verdict: pass | pass-with-polish | fail
```

---

## Related
- hub → [[lead-visual-qa]]
- peer ↔ [[visual-qa-game-design]] · [[interactive-capture-eval]] · [[reference-video-review]] · [[realtime-visual-craft]] · [[rendering-guild]] · [[failure-mode-premortem]] · [[imaging-foundations]] · [[realtime-render-performance]] · [[render-qa-toolkit]] · [[native-visual-eval]] · [[lead-3d-designer]]
