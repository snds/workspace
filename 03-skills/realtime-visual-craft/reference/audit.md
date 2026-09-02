# Audit — technical photoreal quality

Instrument the image for energy, materials, lighting, post, and motion tells. Distinct from aesthetic critique.

## Preconditions

Native evidence in hand. Load [[visual-qa-photoreal-rendering]] + [[failure-mode-premortem]] ledger detection methods. #10 enforced.

## Checklist (still — native / 1:1 tiles)

| Area | Look for | Fail tells |
|---|---|---|
| Energy | Plausible luminance; conserved-ish response | Blowouts, crushed blacks, fill-light soup |
| Grazing Fresnel | Specular rise at glancing angles | Plastic dead rim or mirror everywhere |
| GI / ambient | Contact + bounce read | Flat ambient, HDRI-only marketing light |
| Shadows | Contact, cascade continuity, softness vs size | Acne, peter-panning, cascade seams |
| Tonemap / exposure | Curve shape; highlight roll-off | Posterization, hue shifts, middle-gray drift |
| Post | Bloom threshold/order; vignette; grain | Tonemap-before-bloom rings; crawl under motion |
| Materials | Albedo vs specular split; roughness response | Colored metal wrong; specular in albedo |

## Checklist (motion — frame-by-frame)

- TAA/TAAU ghosting on MV-less content
- Dither / noise crawl
- Volumetric banding under camera move
- Shadow cascade swimming
- LOD popping / morph seams
- Disocclusion shimmer at horizons
- Origin-shift history corruption

## Steps

1. Select official poses + stress frames from flythroughs.
2. Grid-assess stills; dense-sample motion stresses.
3. Mark each row **met / not-met / n/a** with artifact citation.
4. Map not-met rows to next craft actions (not vague "improve lighting").

## Fail immediately

- Audit closed on one hero still while motion features shipped
- "No banding" claimed from a downsampled screenshot

## Next

Not-met blockers → `craft` / `harden`. Clean audit → `match` + `budget` to close triple gate.
