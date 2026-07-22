# Perception Integrity

*A top-level operating document that sits alongside the Aesthetic Lens, UI/UX Operational Framework, Collaboration and Critique Framework, Research and Evidence Framework, Last-Mile Craft Framework, QA Operating Model, Integration & Review Framework, Workspace Contribution Framework, and Component & Pattern Framework. Where Last-Mile Craft (#05) holds the **finishing** discipline and the QA Operating Model (#06) frames the **target**, this framework governs the layer beneath both: whether the pixels I am judging are real. It is cross-cutting beyond design — it governs ALL visual evaluation: design QA, game and 3D renders, shader and dither artifacts, reference art, photography, data-viz, OCR-able text, anything visual.*

---

## The core conviction

**A visual judgment is only as truthful as the pixels it runs on. Never judge fine visual detail from a downsampled image. Capture at native resolution — zoom the subject so the artifact fills the frame, or read the frame back in 1:1 native chunks — and state the pixel dimensions you judged at before claiming anything is fixed, gone, matching, or clean. A thumbnail is a locator, never a verdict.**

This is not a finishing check among others. It is the *precondition* to every visual check — to baseline perception, to augmented (instrumented) perception, to human review, to reference comparison. A measurement run on scaled pixels measures the scaling. A "looks fixed" claimed from a fit-to-window preview is unverified. The discipline elevated here used to live as a subsection of Last-Mile Craft; it earns first-class status because it applies wherever a render, frame, or image asset is being assessed — not only at the design-finishing layer.

---

## When this framework invokes

Default-active the instant a fine visual detail is in question, in **any** domain. Specifically:

- **A screenshot / preview / render tool hands back a scaled or fit-to-window frame** (the common ~800 px case) and I'm about to draw a conclusion from it.
- **Any "is the artifact gone?" call** — banding, posterization, grain, dither, noise, aliasing, jaggies, moiré.
- **Edge / stroke / radius / anti-aliasing fidelity**, sub-pixel and few-pixel alignment, spacing precision, small-text legibility, contrast at thin features, gradient smoothness, fine texture or feathering, compression artifacts.
- **Reference comparison** — claiming a produced artifact "matches" a source (shadcn docs, Storybook, brand spec, design source, concept art).
- **Game / 3D / shader work** — judging a volumetric, a post-process chain, a dither pass, a material, a VFX frame.
- **Static asset review at native scale** — reference art, photography, mockups, comps, diagrams, PDFs.

It steps aside only for *gross* questions a thumbnail answers honestly: where is the thing, is it on screen, which region do I inspect next, what's the overall layout. Those are locator questions. The moment the question becomes *finish*, this framework is back.

---

## Why it's non-negotiable — the failure mode

**Downscaling is a low-pass filter.** It erases exactly the high-frequency detail the judgment depends on, and it erases it *invisibly*: the scaled image looks clean **because the resample hid the defect**, not because the defect is gone. Conclusions drawn from it are unreliable and frequently *confidently wrong* — which is worse than uncertain, because confidence suppresses the second look.

The concrete tell this framework exists to prevent: a render artifact (the canonical case — banding in a volumetric run through a post-process composer) declared "fixed / gone" from a preview tool's ~800 px thumbnail. The downscale smoothed the stepped contours out of the thumbnail. At native resolution the banding was plainly still there — Sean saw it in a single glance. *Trusting the scaled tool output was the bug.* A shipped change is not a verified change; a good-looking thumbnail is not verification.

Two corollaries that catch the subtle re-failures:

- **Retina ≠ resolution-on-the-subject.** A high-DPR screenshot of a maximized window is still the *whole window* downscaled to fit the display. High DPR is not high effective resolution on the thing being judged — it's the originating failure in disguise.
- **Lossy capture read as render artifact.** A JPEG screenshot adds 8×8 DCT blocking and edge ringing that get mistaken for render banding or halos. Capture/save **PNG (lossless)** before judging banding or edges, or the codec gets flagged instead of the render.

---

## The method — by surface (the skill carries the mechanics)

The principle is here; the **operational method lives in the standalone [`native-visual-eval`](../03-skills/native-visual-eval/SKILL.md) skill** — load it on its own, it carries *no visual-QA-hub dependency*, so the discipline is always cheap to invoke for the volume of visual work we do. The skill holds the exact mechanics (the same-tick canvas/WebGL readback, the `preserveDrawingBuffer` timing, the chunk-and-Read loop, the composer-vs-renderer trap, the tile-sizing heuristics). What the framework holds is *which surface needs which move*:

- **Runtime canvas / WebGL preview** — either **zoom the subject** (dolly the camera / grow the element so the artifact fills the frame, then screenshot — and restore the view), or do a **native readback + 1:1 chunk** off the *app's actual final draw* (the composer's render, not a raw `renderer.render`, or the post-process defect is invisible).
- **DOM / web (non-canvas)** — raise DPR or zoom so the region renders larger, or capture full-page and crop native 1:1 tiles; read **computed values** for exact geometry/color rather than eyeballing.
- **Native desktop apps** — screenshot + region-zoom; confirm you captured the intended display at its physical resolution (a scaled-desktop capture is itself a downsample).
- **Static image assets** — never evaluate from a resized copy; crop the *original* into 1:1 native chunks. PDFs rasterize at ≥300 DPI; design-tool exports go out at the dimension the artifact needs (the screenshot API's `maxDimension` reaches 65536), never the default scale.
- **Video frames / playback stills** — the player is always fit-to-window (locator only); pause, seek, `drawImage` the **video element** at its *decoded* dimensions, then chunk-and-Read.

Capture native **first** with this skill; *then* hand off to augmented perception (`visual-qa-toolkit`) to measure and to `lead-visual-qa` to judge. Those outputs are only trustworthy because the pixels under them are real.

---

## The verification gate

Before any **"fixed / gone / matches / clean / looks right / ships"** claim about fine visual detail, three things must be true — say the first one out loud:

1. **State the pixel dimensions and scale judged at — a *number*, not a method name.** "native 1920×1080, read as 6 tiles at 1:1" or "subject zoomed to fill an 800 px frame (~10× effective)" passes; "I zoomed in" / "looks fixed" does not. If I can't state the number, I haven't verified.
2. **If it was a scaled view, I have NOT verified.** Capture native and re-judge before claiming anything.
3. **Then measure / judge.** Native capture (this framework) → measure with `visual-qa-toolkit` (SSIM, Δe, contrast, alignment) and/or judge with `lead-visual-qa`.

This gate is the operational teeth behind the global standard *"assess visuals at native resolution — always, for everything"* and the QA Operating Model's *"a 1024-px thumbnail is not a verification."* It is the same gate enumerated as the **Resolution check** in #06's pre-output gate — that check is this framework firing inside the QA report.

---

## Relationship to the other frameworks

- **#05 Last-Mile Craft (augmented perception).** Last-Mile's enforcement model distributes across four surfaces — Claude's reliable authoring, Claude's baseline + augmented perception, human perception, tooling. This framework is the **precondition to the two perception surfaces**: baseline perception and augmented perception (Pillow/NumPy/OpenCV/scikit-image measurement) are both only as truthful as the pixels they run on. #05 says *measure it*; #10 says *measure it on real pixels*. The §2.5 that used to carry this in #05 now points here; #05 stays complete to read.
- **#06 QA Operating Model (the gate).** #06's pre-output gate includes a **Resolution check** and a native-resolution precondition on its reference-comparison protocol. Those are this framework operating inside the QA report — #06 frames *which target* and *whose eyes*; #10 guarantees the evidence under the verdict is real. #06 fires before #05; #10 underwrites both.
- **#01 Aesthetic Lens / #09 Component & Pattern.** When the judgment is aesthetic or component-anatomy fidelity, the *call* belongs to #01/#09 — but the call is only valid on native pixels. #10 doesn't make the aesthetic judgment; it makes the aesthetic judgment *trustworthy*.
- **The global standard.** This codifies, at the workspace level, the user's core memory: *assess visuals at NATIVE resolution — always, for everything; crop into 1:1 native chunks; downsample only as a locator.* The framework is the principle, `native-visual-eval` is the method, and the verification gate is the habit that makes it stick.

---

## Operating habits

How this framework shows up in the work:

- **Native-resolution capture before any fine-detail call.** I capture native — zooming the subject so the artifact fills the frame, or reading the frame back in 1:1 native chunks — *before* judging, in every domain, not just design.
- **State the number.** I name the pixel dimensions and effective scale I judged at before I say fixed / gone / matches / clean. No number → not verified → I don't claim it.
- **Thumbnail as locator, never verdict.** I use a cheap downsample to find the region of interest, then return to native crops for the actual call. I never let the locator become the verdict.
- **Defect-review images are verdict tasks — 1:1 from the first look.** When handed screenshots or a feedback set that *marks or asks about* visual defects (a review, a bug report, annotated captures, a QA pass), that is a verdict task the instant I open it — not a locator task. I review at **native 1:1, at the original size and aspect ratio**, and **tile a too-large capture into a grid of native chunks** rather than downscale it to fit a viewer. Downscaling a defect-review image downscales the verdict; the resample is exactly what hides the reported artifact. A downsample is allowed only to decide *which tile to open*, never as the surface I judge on. (This closes the "locator" carve-out below: reviewing provided defect captures never qualifies as a locator question.)
- **PNG for banding/edge calls.** I capture/save lossless before judging high-frequency detail, so I flag the render and not the codec.
- **Read the app's real frame.** For post-processed canvases I read back the composite the app actually presents, not a pre-composite raw render.
- **Capture native first, then measure, then judge.** I sequence `native-visual-eval` → `visual-qa-toolkit` → `lead-visual-qa`, and I say which I'm doing.
- **Honest "not verified."** If I only had a scaled view and couldn't get native pixels (tainted canvas, no render handle, out of reach), I say so explicitly rather than launder a thumbnail glance into a verdict.

---

## Relationship to skills

This framework is the meta-layer; the execution lives in the skill network.

- **[`native-visual-eval`](../03-skills/native-visual-eval/SKILL.md)** — the tactical implementation of this entire framework: capture-and-chunk across canvas/WebGL, DOM, native desktop, static assets, and video; the same-tick readback mechanics; the verification gate restated for the operator. Standalone, no hub dependency. This is where the *how* lives.
- **`visual-qa-toolkit`** — augmented perception (measurement). Runs *after* native capture: SSIM, Δe, contrast, alignment, color-vision simulation, grid overlays. Trustworthy only on real pixels.
- **`lead-visual-qa`** — the judgment lens. Runs *after* native capture; pairs with #06's target-user framing.
- **`reference-video-review`** — frame-accurate extraction for video on disk (`ffmpeg -ss`), the no-browser path for surface E.

---

## What this framework is not

- **Not a design-only rule.** It governs game/3D, shaders, photography, print, data-viz, OCR-able text — anything visual. Scoping it to UI finishing was exactly the under-reach that motivated promoting it out of #05.
- **Not "always capture at maximum resolution for everything."** Locator questions (where, is-it-on-screen, gross layout) are fine on a thumbnail. The discipline is matching resolution to the *judgment*, and never letting a locator masquerade as a verdict.
- **Not a measurement framework.** It guarantees the pixels are real; #05's augmented perception and `visual-qa-toolkit` do the measuring. Native capture answers *is it there*; the toolkit answers *by how much*.
- **Not optional once a number can't be stated.** If I can't state the resolution I judged at, the claim isn't ready — that's the whole point.
