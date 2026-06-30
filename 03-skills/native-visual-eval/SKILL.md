---
name: native-visual-eval
description: >
  Capture-at-native-resolution discipline — the precondition to ALL visual evaluation. Use BEFORE
  judging any fine visual detail from a rendered preview, screenshot, canvas/WebGL frame, video still,
  render, mockup, or image asset, and ANY time a screenshot/preview tool hands back a downsampled or
  fit-to-window image. The core rule: never assess banding, posterization, grain, dither, aliasing,
  moiré, edge sharpness, stroke weight, corner radii, sub-pixel alignment, spacing precision, small-text
  legibility, contrast at thin features, fine texture/feathering, compression artifacts, or "is this
  artifact gone?" from a scaled-down image — resampling is a low-pass filter that erases exactly the
  high-frequency detail the judgment depends on, producing confidently wrong conclusions. This skill is
  the METHOD: treat any scaled output as a LOCATOR only, then get true native pixels — same-tick
  canvas/WebGL readback, zoom-the-subject-not-the-image, or capture the frame and read it back in 1:1
  native BLOCKS (chunk + Read each). Trigger on: "take a high-res screenshot," "native resolution,"
  "is the banding/aliasing/grain gone," "zoom in and check," "the screenshot looks low-res," reviewing
  renders/shaders/artifacts/dither, or any pixel-level finish check. Pairs with `visual-qa-toolkit`
  (measurement) and `lead-visual-qa` (judgment) — capture native FIRST, then measure/judge. Standalone:
  does NOT require loading the visual-QA hub.
aliases: [native-visual-eval]
triggers: [native resolution, high-res screenshot, downsample, downscaled, capture and chunk, 1:1 pixels, canvas readback, preservedrawingbuffer, banding, aliasing, grain, dither, moire, zoom in, full res, pixel-level, retina, screenshot looks low-res]
tier: cross-cutting
domain: quality
related: [visual-qa-toolkit, lead-visual-qa, reference-video-review]
surfaces: ["*"]
spec_version: "2.0"
---

# Native-Resolution Visual Evaluation

**The directive: never judge fine visual detail from a downsampled image. Capture at native
resolution; if the subject is larger than one truthful view, capture it in 1:1 native BLOCKS and read
each. Any scaled / fit-to-window / "thumbnail" output is a LOCATOR ONLY — never a verdict.**

This is the precondition to every other visual check. Measurement (`visual-qa-toolkit`) and judgment
(`lead-visual-qa`) are only as trustworthy as the pixels they run on. Load this skill on its own — it
carries no hub dependency.

---

## Why (the failure mode this prevents)

Downscaling is a **low-pass filter**. It destroys precisely the high-frequency detail that fine visual
judgments depend on — and it destroys it *invisibly*: the scaled image can look **clean because the
resample erased the defect**, not because the defect is gone. Conclusions drawn from it are unreliable
and frequently **confidently wrong**.

> **Cautionary tale (real).** A volumetric-render banding artifact was declared "fixed / gone" from a
> preview tool's ~800 px thumbnail. The downscale had smoothed the stepped contours out of the
> thumbnail. At native resolution the banding was plainly still there — the user saw it in one glance.
> The thumbnail was a locator masquerading as a verdict. *Trusting the scaled tool output was the bug.*

Detail that **only survives at native resolution**: banding / posterization / quantization contours ·
grain · dither · noise character · aliasing / jaggies / moiré · edge sharpness · stroke weight · corner
radii · sub-pixel & few-pixel alignment · spacing precision · small-text legibility · contrast at thin
strokes · fine texture / feathering / gradient smoothness · compression artifacts · and every "is the
artifact gone?" call.

---

## When native resolution is REQUIRED vs. when a thumbnail is fine

| Judgment | Resolution needed |
|---|---|
| Banding, grain, dither, aliasing, moiré, "is the artifact gone?" | **Native, always.** Chunk if needed. |
| Edge/stroke sharpness, corner radii, anti-aliasing fidelity | **Native.** |
| Sub-pixel / few-pixel alignment, spacing precision, small text | **Native** (then measure with `visual-qa-toolkit`). |
| Contrast at thin features, gradient smoothness, fine texture | **Native.** |
| "Where is the thing", gross layout, is-it-on-screen, which region to inspect | Thumbnail OK — **as a locator only.** |

Use a cheap downsample to **locate** the region of interest, then **return to native crops** for the
actual call. Never let the locator become the verdict.

---

## The method — by surface

### A. Runtime canvas / WebGL preview (the common case)

The preview-screenshot tool returns a scaled frame (often ~800 px wide). Two ways to get true pixels:

**A1 — Zoom the subject, not the image (fastest when you control the view).** Dolly the camera / grow
the element so the artifact fills the frame, *then* screenshot — the tool's fixed output budget is now
spent entirely on the region of interest, so 800 px covers just the artifact = high *effective*
resolution. **Save and restore the original view** so you don't disturb the user's setup.

**A2 — Native readback + 1:1 chunk (when you need the real frame).**

> **Read back the SAME draw call the app composites.** If the app post-processes (an `EffectComposer` —
> bloom / SMAA / tonemap / **dither**), call the app's *actual* final render (`composer.render()` / its
> render-loop function), **not** `renderer.render(scene, camera)`. Calling `renderer.render()` yourself
> overwrites the buffer with a **pre-composite** frame — so banding introduced by a dither/tonemap pass
> is invisible, and raw banding can be masked or altered by the post chain. This is most dangerous in
> exactly this skill's headline case (banding in a volumetric, which usually runs through a composer):
> A2 can return a confidently *wrong* verdict. If you can't reach a render handle at all, use **A1**.

The mechanism (why step 1 is single-tick but step 2 is free): with `preserveDrawingBuffer:false` the GL
drawing buffer is presented and then **cleared after the current task**. So **step 1 — repaint then
`drawImage` the canvas into a 2D canvas — must be one synchronous `preview_eval`**; render and read in
the same tick and the pixels are intact. Once they live in the 2D `__cap` canvas they **persist
indefinitely** (a 2D canvas is never auto-cleared), so **step 2's per-tile crops run on any later tick**.

```js
// 1) ONE synchronous eval: repaint, then snapshot the GL buffer into a persistent 2D canvas
const cv = renderer.domElement;                  // the renderer's OWN canvas — NOT a blind querySelector('canvas')
appRender();                                      // the app's FINAL draw: composer.render() if post-processed
const off = document.createElement('canvas');
off.width = cv.width; off.height = cv.height;     // cv.width/height = true backing-store pixels (already DPR-scaled);
off.getContext('2d').drawImage(cv, 0, 0);         //   never size off getBoundingClientRect()/CSS px → that re-downsamples
window.__cap = off;                               // 2D canvas: pixels persist across later evals
return { w: cv.width, h: cv.height };             // plan the chunk grid from the native dims
```

```js
// 2) Per tile (any later tick): crop a sub-rect at 1:1 native scale (NO resampling), return its PNG
const [x, y, w, h] = [TX, TY, TW, TH];
const t = document.createElement('canvas'); t.width = w; t.height = h;
t.getContext('2d').drawImage(window.__cap, x, y, w, h, 0, 0, w, h);  // src rect == dest rect → 1:1, true pixels
return t.toDataURL('image/png');                  // base64 → write to a file → Read it
```

Then: write each tile's base64 to a scratch `.png` and **Read** it (the Read tool renders true pixels).
Tile across the ROI; reconstruct the composite mentally. **Size tiles to the artifact, not a fixed
block** — PNG is lossless, so grain/dither/noise (the very things you're judging) barely compress, and a
busy ~400×300 tile can blow the eval return budget while a flat one is tiny. A quick brightness-bbox scan
on a downsample tells you which tiles contain the subject, so you only chunk what matters.

*Preconditions & hard failures:* A2 needs a **callable render handle** (or an on-demand render you can
trigger in the eval) — unreachable in many bundled apps, so fall back to **A1**. If the scene drew
**cross-origin textures without CORS**, the canvas is tainted and `toDataURL` throws `SecurityError` —
set `crossOrigin` on those assets, or use A1. (Split the tick and the read returns the *cleared* buffer
— transparent / the clear color, black once flattened — that's the tell.)

### B. DOM / web (non-canvas)

Raise device pixel ratio or browser zoom so the region renders larger, **or** capture full-page and
crop native 1:1 tiles. For exact geometry/color, read **computed values** (`getComputedStyle`,
`getBoundingClientRect`) and hand off to `visual-qa-toolkit` — don't eyeball measurements off a scaled
image.

### C. Native desktop apps

computer-use `screenshot` + the region `zoom` tool; crop to native. Never assess fine detail from the
fit-to-display capture. On **scaled or multi-monitor displays** the OS may hand back a *logically*-scaled
buffer (not physical pixels) or the wrong display — confirm you captured the intended display at its
physical resolution before region-zooming; a scaled-desktop capture is itself a downsample.

### D. Static image assets (reference art, renders, photos, mockups, comps, diagrams)

**Never evaluate from a resized copy.** Crop the *original* into 1:1 native chunks and inspect each;
downsample only for a cheap overview/locator, then return to native crops for any actual quality call.
Domain-independent — game/3D, DS/UI, photography, print, data-viz, OCR-able text, anything visual.

- **PDF** — rasterize at **≥300 DPI** before cropping; a default-DPI page render is a built-in downsample.
- **Figma / design-tool exports** — export at the dimension the artifact needs (raise scale / the
  screenshot API's `maxDimension` to what the finishing-tier check needs — it goes to 65536), never the
  default scale. (This is the method home for framework #06's "use what's needed" reference-zoom rule.)
- **Large assets** (e.g. 8000 px wide) — plan a tile grid from the native dims and use a downsample
  brightness-bbox prescan (per A2) to chunk only the tiles that contain the subject.

### E. Video frames / playback stills

The on-screen player is always fit-to-window — a player screenshot is a **locator only** — and a
`<video>` is not a `<canvas>`. Pause, seek to the target frame, then `drawImage` the **video element**
into a 2D canvas sized to its **decoded** dimensions (`videoWidth/videoHeight`, *not* `clientWidth`),
then chunk-and-Read per A2:

```js
v.pause(); v.currentTime = T;                     // seek; wait for the 'seeked' event before drawing
const c = document.createElement('canvas');
c.width = v.videoWidth; c.height = v.videoHeight;  // the true decoded frame, NOT the scaled display box
c.getContext('2d').drawImage(v, 0, 0);
window.__cap = c;                                  // then crop 1:1 tiles exactly as in A2 step 2
```

Video is where banding/blocking hides most (dark-gradient banding, 8×8 macroblocks, chroma subsampling).
For files on disk, `reference-video-review`'s `ffmpeg -ss <t> -vframes 1` extracts the frame at native
decode resolution without a browser.

---

## The verification gate (say it out loud)

Before any **"fixed / gone / matches / clean / looks right / ships"** claim about fine visual detail:

1. **State the pixel dimensions and scale you judged at** — a *number*, not a method name. "native
   1920×1080, read as 6 tiles at 1:1" or "subject zoomed to fill an 800px frame (~10× effective)" passes;
   "I zoomed in" / "looks fixed" does not. If you can't state the number, you haven't verified.
2. **If it was a scaled view, you have NOT verified.** Capture native and re-judge before claiming.
3. **Then measure / judge.** Capture native (this skill) → **measure** with `visual-qa-toolkit`
   (SSIM, Δe, contrast, alignment) and/or **judge** with `lead-visual-qa`. Native capture is what makes
   those outputs trustworthy.

This is the operational teeth behind the global standard *"assess visuals at native resolution —
always, for everything"* and the QA Operating Model's *"a 1024-px thumbnail is not a verification."*

---

## Anti-patterns

- **Thumbnail-as-verdict.** Declaring an artifact resolved from the tool's scaled output. The most
  common and most embarrassing failure — the resample hid the defect.
- **Retina ≠ resolution-on-the-subject.** A "Retina"/high-DPR screenshot of a maximized window is still
  the *whole window* downscaled to fit the display. High DPR is not high effective resolution on the
  thing you're judging — this is the originating ~800px failure in disguise. Zoom the subject, or chunk.
- **Lossy capture read as render artifact** (false positive). A JPEG screenshot adds 8×8 DCT blocking
  and edge ringing that get mistaken for render banding/halos. Capture/save **PNG (lossless)** before
  judging banding or edges, or you'll flag the codec, not the render.
- **"The rule is in the code, so it's fixed."** A shipped change is not a verified change. Look at
  native pixels.
- **Re-judging from a re-downsampled crop.** If you crop then let the tool scale the crop, you're back
  to a thumbnail. Crop at **1:1** (src rect == dest rect) and move the bytes to disk to Read.
- **Splitting the tick (step 1).** Repaint in one eval, `drawImage` into the 2D canvas in the next →
  you read the cleared buffer. The render→snapshot must be one synchronous call; *step 2* chunks freely.
- **Eyeballing measurements off any image.** Native capture answers "is it there"; `visual-qa-toolkit`
  answers "by how much."

---

## Related
- peer ↔ [[visual-qa-toolkit]] · [[lead-visual-qa]] · [[reference-video-review]]
