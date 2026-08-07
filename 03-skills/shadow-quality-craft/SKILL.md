---
name: shadow-quality-craft
description: >
  Production shadow recipes — cascaded shadow maps (CSM), PCSS / contact-hardening, VSM, ray-traced
  shadows; bias and light leakage; cascade swimming under camera move. Use when shadows swim,
  peter-pan, acne, or soft-contact looks wrong in motion. Triggers: CSM, cascaded shadows, PCSS,
  contact hardening, VSM, shadow bias, shadow acne, peter panning, cascade swimming, RT shadows.
aliases: [shadow-quality-craft]
triggers: [csm, cascaded shadow, cascade shadow, pcss, contact hardening, vsm, variance shadow, shadow bias, shadow acne, peter panning, cascade swimming, rt shadows, ray traced shadows, soft shadows, shadow map]
tier: spoke
hub: realtime-visual-craft
domain: imaging
related: [img-photoreal-rendering, interactive-capture-eval, dynamic-gi-production, realtime-render-performance, adapter-webgpu-three]
surfaces: ["*"]
spec_version: "2.0"
---

# Shadow Quality Craft

Owns **realtime shadow technique choice, bias craft, and motion failure modes**. Theory context:
[[img-photoreal-rendering]]. Motion proof: [[interactive-capture-eval]] (still-only approval is an
automatic fail for cascades / contact-hardening).

## Technique choice

| Need | Technique | Cost / cheat |
|---|---|---|
| Large outdoor / planet approach | CSM (2–4 cascades) | Cascade seams; swimming; resolution per split |
| Soft contact under local lights | PCSS / contact-hardening | Extra blocker search; noise without TAA |
| Soft blob without RT | VSM / EVSM | Light bleed; needs blur + clamp |
| Perfect contact / thin geo | RT shadows (hw or compute) | Budget; denoiser; rare on WebGPU ship path |
| Static indoor hero | Baked shadows / lightmap AO | No dynamic casters |

**Default shipping path (web):** directional CSM + PCF or lightweight contact-hardening on key light
only; bake contact AO for static. Escalation: VSM for stylized soft; RT only if measured.

## CSM recipe checklist

- [ ] Split scheme documented (practical / logarithmic / PSSM) and locked in `RENDER.md`.
- [ ] Cascade resolution fits texel density at near cascade (not "4K atlas, empty far").
- [ ] Stabilization: snap shadow camera to texel grid in light space (kills shimmer under slow pan).
- [ ] Fade / blend between cascades; hard hard-cuts read as swimming even when stable.
- [ ] Receiver bias scale per cascade (near needs less slope-scale than far).
- [ ] Casters: frustum cull on **shadow** camera; LOD select on **main** camera (mismatch = pop).
- [ ] Max cascades in budget: prefer 3 good over 4 starving.

## Bias, acne, peter-panning

| Artifact | Cause | Fix order |
|---|---|---|
| Shadow acne (self-shadow mottling) | Depth precision / coplanar | Depth bias + slope-scale; normal offset; reverse-Z |
| Peter-panning (shadow detaches) | Bias too high | Reduce constant bias; prefer slope-scale; normal offset carefully |
| Light leak at thin walls | Dual-face / insufficient depth | Two-sided shadow casters; tighter near plane; RT if critical |
| Receiver acne on slopes | Constant bias only | Slope-scale bias; receiver plane bias |

**Rule:** fix acne with slope-scale and reverse-Z before cranking constant bias. Constant bias is a
last resort and is the usual cause of peter-panning.

## PCSS / contact-hardening

1. Find average blocker depth in shadow map (search radius ∝ light size).
2. Penumbra width ∝ `(receiverDepth - blockerDepth) * lightSize / blockerDepth`.
3. Filter with variable kernel (PCF or Poisson); blue-noise rotate per frame.
4. Clamp max penumbra so sky-sized sun does not melt the whole cascade.

Checklist:
- [ ] Light angular size authored (sun ≠ studio softbox).
- [ ] Search radius scales with cascade texel size.
- [ ] Motion: no strobing kernel — temporal rotate + TAA or freeze kernel under pause.
- [ ] Judge under camera move, not a parked still.

## VSM notes

Variance shadow maps store depth moments; soft edges via Chebyshev. **Failure:** light bleed through
occluders. Mitigate with EVSM / bleed reduction / tight depth range. Prefer PCSS for "physical soft"
and VSM for stylized or particle-friendly softness when bleed is acceptable.

## Cascade swimming under camera move

Swimming = cascade bounds or shadow-camera origin updating continuously so shadow texels crawl.

Mitigations (apply in order):
1. **Texel snap** shadow-camera to light-space texel grid.
2. **Stable splits** from camera-forward sphere / fixed radii, not raw frustum corners every frame.
3. **Cascade blend** band so the pop is a crossfade.
4. **Reduce near cascade FOV sensitivity** (overly tight near cascade amplifies crawl).
5. Prove with a slow orbit + strafe flythrough; frame-by-frame at cascade boundaries.

## RT shadows (honest)

Use when: thin geometry, alpha-tested foliage contact, or northstar demands hard contact. WebGPU:
treat as experimental; do not block ship on hardware RT. Unreal Virtual Shadow Maps / RT shadows are
northstar references ([[adapter-unreal]]), not web defaults.

## Failure modes (quick)

- **Swim on pan** → missing texel snap / unstable splits.
- **Seam ring on ground** → cascade blend width 0 or resolution cliff.
- **Acne on terrain slopes** → constant bias only; add slope-scale.
- **Characters float above shadow** → bias / normal offset too aggressive.
- **Foliage speckles** → need deeper bias or contact AO bake, not more PCF.
- **Still looks fine, move looks bad** → you skipped motion QA.

## Adapter notes

- **Three/WebGPU:** `DirectionalLightShadow` + cascade helpers; custom PCSS in TSL/WGSL; watch
  shadow map size vs atlas. No fragment logarithmic depth as default ([[adapter-webgpu-three]]).
- **Unreal:** Virtual Shadow Maps + contact shadows as ceiling reference.
- **Unity HDRP:** cascade + contact shadows via Volume; bias on light component.

## Related
- hub → [[realtime-visual-craft]]
- peer ↔ [[dynamic-gi-production]] · [[adapter-webgpu-three]] · [[adapter-unreal]] · [[gpu-capture-tooling]]
