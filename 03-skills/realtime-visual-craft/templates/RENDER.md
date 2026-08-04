# RENDER.md — Realtime Photoreal Contract

> Project render spine. Fill before choosing techniques. Owned by `realtime-visual-craft`.
> Companion files: `BUDGET.md` (costs) · `NORTHSTAR.md` (references).

---

## Project

- **Name:**
- **Engine / adapter:** (e.g. WebGPU/three · Unreal · Unity HDRP)
- **Target platforms:** (desktop integrated GPU floor · discrete · mobile if any)
- **Owner / last updated:**

---

## Fidelity contract

Stack one or more (see Lead Visual QA / framework #12):

| Contract | Active? | Meaning for this project |
|---|---|---|
| **Literal** | ☐ | Match named northstar stills/frames within medium limits |
| **Spirit** | ☐ | Capture energy, materials, camera language of northstar without copying |
| **Standard** | ☐ | Industry-correct PBR / tonemap / exposure |
| **Intent** | ☐ | Serve stated gameplay/look goal |

**Default bar:** movie-level / northstar-gated (Literal or Spirit against named film / cinematic / AAA refs).

**One-sentence contract:**
> …

---

## Technique ladder (name the cheat)

Chosen rung and what higher rungs would buy:

| Rung | In plan? | Cheat / approximation | Buys |
|---|---|---|---|
| 1. Direct lighting + correct materials | ☐ | | |
| 2. Ambient occlusion (contact) | ☐ | | |
| 3. IBL / HDRI | ☐ | | |
| 4. Probes / irradiance / lightmaps | ☐ | | |
| 5. SSGI / DDGI / probe-grid GI | ☐ | | |
| 6. ReSTIR / HW RT / path tracing | ☐ | | |

**Pipeline notes** (tonemap order, bloom, TAA/TAAU, exposure model):

-

---

## Official poses (still gate)

Named camera poses for native still capture. Each must be reproducible.

| Pose ID | Description | What it proves | Capture path |
|---|---|---|---|
| P01 | | | |
| P02 | | | |
| P03 | | | |

---

## Official paths (motion gate)

Named flythrough / interaction paths. Cover move, look, roll, zoom/scale, and project stresses (LOD, origin shift, approach).

| Path ID | Description | Stresses | Capture path |
|---|---|---|---|
| F01 | | | |
| F02 | | | |

---

## Absolute bans (project-local additions)

In addition to framework #12 bans:

-

---

## Done-gate checklist

- [ ] Native still grid assessed 1:1 against northstar (tile dims stated)
- [ ] Motion video reviewed frame-by-frame (paths + key stress frames named)
- [ ] Frame budget measured at poses **and** along flythroughs (JSON / harness, not vibes)
- [ ] No verdict sourced from thumbnail / fit-to-window / lossy preview
