---
name: realtime-visual-craft
description: >
  Impeccable-style command router for realtime photoreal craft — the operational surface of
  framework #12. Use when shaping, building, critiquing, auditing, matching, budgeting,
  hardening, polishing, or optimizing realtime 3D / game / shader / lighting / material / post /
  LOD / scale-traversal work against movie-level northstar references. Commands: init, shape,
  craft, flythrough/interact, critique, audit, match, budget, harden, polish, optimize.
  Forced setup: if RENDER.md / BUDGET.md / NORTHSTAR.md are missing, run init first. Enforces
  the triple done-gate (native still grid + motion video frame-by-frame + measured frame budget)
  and bans low-res / still-only verdicts. Load with frameworks #12 and #10. Triggers: photoreal,
  realtime craft, flythrough, northstar match, render contract, frame budget QA, cinematic look.
aliases: [realtime-visual-craft, rvc]
triggers: [photoreal, photorealism, realtime craft, realtime visual, flythrough, fly-through, northstar, render contract, RENDER.md, BUDGET.md, NORTHSTAR.md, cinematic look, movie-level, match the reference, frame budget qa, still grid, motion fidelity, interactive capture, craft photoreal, harden render, polish render]
tier: hub
domain: game
related: [imaging-foundations, realtime-render-performance, native-visual-eval, interactive-capture-eval, reference-video-review, visual-qa-photoreal-rendering, rendering-guild, failure-mode-premortem, lead-visual-qa, lead-game-developer, dynamic-gi-production, shadow-quality-craft, virtual-texturing-ops, bake-orchestration, gpu-capture-tooling, adapter-webgpu-three, adapter-unreal, adapter-unity-hdrp]
surfaces: ["*"]
spec_version: "2.0"
---

# Realtime Visual Craft

Command router for **movie-level realtime photoreal** work. This is the operational surface of
framework [#12 Realtime Photoreal Operational Framework](../../01-frameworks/12-realtime-photoreal-operational-framework.md).
Every command below assumes the fidelity contract is written, the northstar set is named, and the
**triple done-gate** closes the work:

1. **Still fidelity** — native-resolution captures; grid into 1:1 tiles when the subject exceeds one
   truthful view ([#10](../../01-frameworks/10-perception-integrity.md) / [[native-visual-eval]]).
2. **Motion / interaction fidelity** — recorded paths covering move, look, roll, zoom/scale; review
   video **frame-by-frame** ([[interactive-capture-eval]] / [[reference-video-review]]).
3. **Frame budget** — measured worst-frame / pass ms at official poses **and** along official
   flythroughs ([[realtime-render-performance]]).

A single screenshot is not proof. Low-res / fit-to-window imagery is a **locator only**, never a verdict.

---

## Forced setup

Before any command other than `init`:

1. Locate `RENDER.md`, `BUDGET.md`, and `NORTHSTAR.md` (project root, `docs/`, or `.agents/context/`).
2. **If any are missing → stop and run `init`.** Finish init, then resume the original command.
3. Load framework [#12](../../01-frameworks/12-realtime-photoreal-operational-framework.md) and
   [#10](../../01-frameworks/10-perception-integrity.md). For technique proposals also load #11 /
   [[failure-mode-premortem]].
4. If the user invoked a sub-command, **read `reference/<command>.md` next**. Non-optional.

Templates live in [`templates/`](templates/). Command flows live in [`reference/`](reference/).

---

## Absolute bans

Match-and-refuse. If you are about to do any of these, stop and rewrite the plan:

- **Still-only QA** for camera, LOD, temporal, dither, cascade, or scale-traversal features
- **Verdicts from downsampled / fit-to-window / JPEG-lossy** captures ("looks fixed" from a thumbnail)
- **Closing "done" on a single frame** when the claim involves camera motion or interaction
- **Marketing HDRI-only lighting** claimed as photoreal without contact shadows / energy / materials
- **Fragment `logarithmicDepthBuffer`** (or equivalent early-Z killers) as a default
- **Fill lights that break energy conservation** to "brighten" a scene
- **Post-order mistakes** (tonemap before bloom; judging pre-composer buffers as final look)
- **Self-imposed low frame caps** that leave FPS/latency on the table without a player-facing setting
- **Vague northstars** ("cinematic", "AAA", "photoreal") without named stills/videos/game refs
- **Add-then-hope budget** — adding a look pass without a `BUDGET.md` line and measured cost

---

## Commands

| Command | Category | Description | Reference |
|---|---|---|---|
| `init` | Setup | Create RENDER.md / BUDGET.md / NORTHSTAR.md from templates | [reference/init.md](reference/init.md) |
| `shape` | Plan | Fidelity contract, northstar set, technique ladder, budget envelope, official poses + paths | [reference/shape.md](reference/shape.md) |
| `craft` | Build | Shape → harden (pre) → implement against the contract | [reference/craft.md](reference/craft.md) |
| `flythrough` / `interact` | Capture | Record official camera / interaction paths at native/lossless | [reference/flythrough.md](reference/flythrough.md) |
| `critique` | Evaluate | Aesthetic + photoreal judgment against northstar (still + motion) | [reference/critique.md](reference/critique.md) |
| `audit` | Evaluate | Technical quality: energy, Fresnel, GI, shadows, tonemap, post, motion tells | [reference/audit.md](reference/audit.md) |
| `match` | Evaluate | Literal/Spirit delta vs named northstar stills and video frames | [reference/match.md](reference/match.md) |
| `budget` | Measure | Pass costs + worst-frame along poses and flythroughs | [reference/budget.md](reference/budget.md) |
| `harden` | Gate | Pre-mortem (#11) before build; acceptance prove at done-boundary | [reference/harden.md](reference/harden.md) |
| `polish` | Refine | Last-mile finish after fidelity holds | [reference/polish.md](reference/polish.md) |
| `optimize` | Refine | Cut cost without silently dropping look; re-prove triple gate | [reference/optimize.md](reference/optimize.md) |

### Routing rules

1. **No argument** — recommend the 2–3 highest-value next commands from project state (missing contracts → `init`; no northstar → `shape`; no motion evidence → `flythrough`; fidelity claim without numbers → `budget` + `match`). Never auto-run; confirm with the user.
2. **First word matches a command** — load its reference and follow it. Everything after the name is the target.
3. **Intent maps clearly** ("does this match Interstellar?" → `match`; "we're dropping frames on approach" → `budget`) — load that reference.
4. **`craft` always runs setup first**; if setup blocks on `init`, finish init, then resume into `shape` before code.

---

## Operating sequence (default)

1. `init` → contracts exist  
2. `shape` → contract + northstar + technique + budget + poses/paths locked  
3. `harden` (pre) → failure-mode premortem  
4. `craft` → implement  
5. `flythrough` / `interact` → motion evidence  
6. `budget` → measured ms  
7. `match` / `audit` / `critique` → still grid + motion frames + northstar  
8. `harden` (done) → prove acceptance at native res in motion  
9. `polish` / `optimize` → only after fidelity holds  

---

## Pairing

| Need | Skill |
|---|---|
| Capture native / 1:1 tiles | [[native-visual-eval]] |
| Record → extract → grid-assess | [[interactive-capture-eval]] |
| Decompose reference / capture video | [[reference-video-review]] |
| Photoreal judgment lens | [[visual-qa-photoreal-rendering]] |
| Multi-agent deliberation | [[rendering-guild]] |
| Frame / latency doctrine | [[realtime-render-performance]] |
| Technique failure modes | [[failure-mode-premortem]] |
| Light transport craft | [[imaging-foundations]] |

---

## Related
- spoke → [[adapter-unity-hdrp]] · [[adapter-unreal]] · [[adapter-webgpu-three]] · [[bake-orchestration]] · [[dynamic-gi-production]] · [[gpu-capture-tooling]] · [[render-qa-toolkit]] · [[shadow-quality-craft]] · [[virtual-texturing-ops]]
- peer ↔ [[lead-visual-qa]] · [[interactive-capture-eval]] · [[render-qa-toolkit]] · [[native-visual-eval]] · [[reference-video-review]] · [[visual-qa-photoreal-rendering]] · [[rendering-guild]] · [[failure-mode-premortem]] · [[realtime-render-performance]] · [[imaging-foundations]] · [[lead-game-developer]] · [[legion-project]] · [[lead-3d-designer]]
