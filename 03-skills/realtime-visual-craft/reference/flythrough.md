# Flythrough / Interact — motion evidence

Record the official camera and interaction paths. Still-only approval is an automatic fail for motion-sensitive work.

## Preconditions

Paths defined in `RENDER.md`. Load [[interactive-capture-eval]] + [[native-visual-eval]] + framework #10.

## Steps

1. **Name the paths.** Use F-IDs from `RENDER.md`. Cover at minimum: move, look, orientation/roll, zoom/scale. Add project stresses: LOD swaps, floating-origin shifts, approach-to-surface, cascade boundaries.
2. **Record at native / lossless.** Prefer project harness / lossless PNG sequence / high-bitrate capture. No compressed preview as the archive of record.
3. **Log metadata.** Resolution, refresh, path ID, duration, build SHA / preset, whether TAA history was warm.
4. **Extract frames.** Use ffmpeg (or harness) at a base rate; **dense-sample** temporal stress windows (LOD pop, origin recenter, fast pan, disocclusion).
5. **Grid-assess key frames.** For frames under judgment, chunk to 1:1 tiles and Read each ([[native-visual-eval]]). Thumbnails locate; they do not verdict.
6. **Judge motion first.** Stability, crawl, shimmer, ghosting, popping, exposure pump — before still beauty.
7. **Store artifacts.** Paths into `NORTHSTAR.md` evidence log or project capture folder. Link from the QA note.

## Path coverage checklist

- [ ] Translate / orbit / strafe
- [ ] Look / pitch-yaw
- [ ] Roll / orientation change (if supported)
- [ ] Zoom or scale traversal (near↔far)
- [ ] LOD / chunk / cascade stress
- [ ] Origin-shift or large teleport (if applicable)

## Fail immediately

- "Looks fine in the live window" with no recording
- Reviewing only the mid-journey hero frame
- Motion claim closed from a GIF/thumbnail

## Next

`budget` (measure along the same paths) → `match` / `audit` / `critique` on extracted frames.
