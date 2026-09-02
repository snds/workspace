# Realtime Photoreal Operational Framework

*A companion to the Aesthetic Lens and the imaging foundations. Where the lens answers "why does this feel right?" and imaging answers "what is light transport?", this framework answers "how do we systematically choose techniques, allocate frame budget, and prove movie-level fidelity under real camera interaction before calling realtime work done?" It sits above project skills. Legion is a test platform, not the owner of this doctrine.*

---

## The core conviction

**Photorealism is a budgeted approximation of light transport, judged in motion as much as in stills. Every technique choice must name what it cheats on, what frame time it buys, and how fidelity is verified against movie-level northstar references under real camera interaction before "done."**

Vague "make it photoreal" is not a contract. A single screenshot is not proof. Low-resolution or fit-to-window imagery makes work look better than it is and is banned as a verdict source.

---

## When this framework invokes

Default-active for any realtime 3D / game / shader / lighting / material / post / LOD / scale-traversal work, and any claim that a scene "matches" film, cinematic, or AAA/northstar game reference.

Load at minimum with [#10 Perception Integrity](10-perception-integrity.md) and [#11 Anticipatory Failure Analysis](11-anticipatory-failure-analysis.md). Pair with [#01 Aesthetic Lens](01-aesthetic-lens.md) and [#05 Last-Mile Craft](05-last-mile-craft-framework.md) for look judgment.

Operational surface: skill `realtime-visual-craft`. Measurement: `render-qa-toolkit` + `interactive-capture-eval` + `native-visual-eval`. Judgment: `lead-visual-qa` → `visual-qa-photoreal-rendering` + `rendering-guild`.

---

## 1. Fidelity contract (before technique selection)

Reuse Lead Visual QA contract types — require one (or a stack) before choosing techniques:

| Contract | Meaning for realtime photoreal |
|---|---|
| **Literal** | Match named northstar stills/frames within medium limits |
| **Spirit** | Capture the energy, materials, and camera language of the northstar without copying |
| **Standard** | Industry-correct PBR/tonemap/exposure without a specific hero ref |
| **Intent** | Serve a stated gameplay/look goal (e.g. NASA-industrial readability at distance) |

Default bar for this workspace's game/3D work: **movie-level / northstar-gated** (Literal or Spirit against named film stills, cinematic trailers, SpaceEngine-class or AAA game footage). Write the contract into `RENDER.md` / `NORTHSTAR.md`.

---

## 2. Northstar set (required)

Every project names concrete references in `NORTHSTAR.md` (or a dedicated section of `RENDER.md`):

- Reference **stills** (paths or URLs) with what each proves
- Reference **videos** with clip timestamps / key frames
- **Northstar game / engine examples** (what ceiling they represent)
- What "match" means (Literal vs Spirit) per reference

Vague adjectives ("cinematic", "AAA", "photoreal") without named assets are rejected at `shape` time.

---

## 3. Technique ladder (name the cheat)

Choose the cheapest rung that satisfies the fidelity contract; state what higher rungs would buy:

1. Direct lighting + correct materials  
2. Ambient occlusion (contact)  
3. IBL / HDRI (largest real-time photoreal win)  
4. Probes / irradiance volumes / lightmaps (static or semi-static GI)  
5. SSGI / DDGI / probe-grid dynamic GI  
6. ReSTIR-class / hardware RT / path tracing (hero stills or cinematic moments)

Engine adapters (`adapter-webgpu-three`, `adapter-unreal`, `adapter-unity-hdrp`) translate ceilings and APIs. Principles stay here and in `imaging-foundations`.

---

## 4. Budget-first allocation

From `realtime-render-performance`:

- **60 FPS is the floor**, not the goal. Design for worst frame, not average.  
- Uncapped by default; optional user frame cap in settings.  
- Input-to-photon latency is co-equal with frame rate.  
- Real in-browser GPU budget ≈ 14–15 ms at 60 Hz after compositor overhead.

Allocate pass costs in `BUDGET.md` before adding look. Never "add then hope."

---

## 5. Triple done-gate (all three required)

### A — Still fidelity
Native-resolution captures. If the subject exceeds one truthful view, **chunk into a 1:1 grid and assess tile-by-tile** (#10 / `native-visual-eval`). Match against northstar stills + Visual Failure-Mode Ledger detection methods.

### B — Motion / interaction fidelity
Recorded camera paths covering **move, look, orientation/roll, zoom/scale traversal**, and project-specific stresses (LOD swaps, floating-origin shifts, approach-to-surface). Review video **frame-by-frame**, with dense sampling at temporal stress points. Still-only approval is an **automatic fail** for motion-sensitive work (TAA, volumetrics, dither, cascades, LOD, scale traversal).

### C — Frame budget
Measured worst-frame and/or pass ms at official poses **and along official flythroughs**. Numbers from harness JSON (`?perfcapture` or equivalent), not FPS counter vibes.

A report that only cites a single screenshot is **incomplete**.

---

## 6. Evidence hierarchy (absolute)

Highest trust → lowest:

1. Interactive recording + native grid chunks of extracted frames  
2. Native full-frame still (lossless PNG)  
3. Subject-zoomed still (artifact fills frame at tool output size)  
4. Thumbnail / fit-to-window / low-res preview — **locator only**

Low-res imagery will make you think something looks better than it actually is. Claiming "fixed / gone / matches / ships" from a locator is a ban.

---

## 7. Absolute bans (realtime AI / marketing slop)

- Still-only QA for camera, LOD, temporal, or scale features  
- Verdicts from downsampled / fit-to-window / JPEG-lossy captures  
- Marketing HDRI-only lighting claimed as photoreal  
- Fragment `logarithmicDepthBuffer` (or equivalent early-Z killers) as a default  
- Fill lights that break energy conservation to "brighten" a scene  
- Post-order mistakes (e.g. tonemap before bloom; judging pre-composer buffers as final)  
- Plugin marketing-3D cookbook defaults that contradict Workspace doctrine when the render spine is loaded  
- Self-imposed low frame caps that leave FPS/latency on the table without a player-facing setting  

---

## 8. Operating sequence

1. **`init`** — ensure `RENDER.md`, `BUDGET.md`, `NORTHSTAR.md` exist  
2. **`shape`** — fidelity contract, northstar set, technique plan, budget envelope, official poses + flythrough paths  
3. **`harden` (pre)** — failure-mode premortem (#11) against the ledger  
4. **`craft`** — implement; load imaging + performance + adapter skills as needed  
5. **`flythrough` / `interact`** — capture motion evidence  
6. **`budget`** — measure poses + paths  
7. **`match` / `audit` / `critique`** — still grid + motion frames + northstar  
8. **`harden` (done)** — prove acceptance criteria at native res in motion  
9. **`polish` / `optimize`** — only after fidelity holds; optimize must not silently drop look  

---

## Relationship to other frameworks

| Framework | Role relative to #12 |
|---|---|
| #01 Aesthetic Lens | Why the look feels authored |
| #05 Last-Mile Craft | Finishing discipline; augmented perception |
| #06 QA Operating Model | Target-user / honesty gate around reports |
| #10 Perception Integrity | Native pixels precondition for every visual claim |
| #11 Anticipatory Failure Analysis | Technique failure modes before build and at done-boundary |
| imaging-foundations | Physics/craft of forming the image |
| game-foundations | Performance is game feel |

---

## Skills that carry the mechanics

- `realtime-visual-craft` — command router  
- `render-qa-toolkit` — deterministic measurement  
- `interactive-capture-eval` — record → extract → grid-assess  
- `native-visual-eval` — 1:1 capture method  
- `reference-video-review` — reference and capture video decomposition  
- `visual-qa-photoreal-rendering` — photoreal judgment lens  
- `rendering-guild` — multi-lens deliberation  
- `realtime-render-performance` — frame/latency doctrine  
- Engine adapters — API/ceiling translation  

---

## Operating habits

- Name the fidelity contract and northstar assets before naming a shader.  
- Budget the frame before adding a pass.  
- Capture motion for anything temporal.  
- Grid-assess native stills; never trust a thumbnail.  
- Close with numbers: tile dimensions judged, frames reviewed, ms measured.  
