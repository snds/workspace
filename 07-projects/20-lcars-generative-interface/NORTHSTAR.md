---
title: LCARS Generative Interface — Visual Northstars
status: active
date: 2026-08-09
tags: [lcars, northstar, literal, okudagram]
project: "[[20-lcars-generative-interface]]"
fidelity_contract: Literal
---

# NORTHSTAR — LCARS Generative Interface

**Program thesis:** LCARS Literal fidelity is the hard proof that a systemic stack (concept + context + intent + aesthetic → Construction IR → Scene IR → renderer → prove) can scale to other surfaces and aesthetics. See `docs/program-thesis.md`.

**Fidelity contract: Literal** for named recreation work. Spirit / "inspired by" / "reads as LCARS" is not acceptance. See `docs/visual-replication-requirements.md` and skill `visual-reference-replication`.

Reference library (local, not in git):

`/Users/snds/My Drive/Creative/Reference/Star Trek/LCARS`

App notes: `~/Projects/lcars-generative-interface/docs/REFERENCES.md`

### Composite reference library

EXEs→SWFs, `1701_D_Mk4.ai`, video loops, and sibling stills inform grammar, motion, density, and topology **in composite**. They do **not** override this table or S-SYS47-01 Construction IR / cue matrix. **S-SYS47-01 stays Literal authority** until Sean renames the northstar. Galaxy AI ≠ Enterprise-E SYS47 match (see `docs/visual-replication-requirements.md`).

## Active recreation target (current pass)

| ID | Source | Kind | Contract | Status |
|---|---|---|---|---|
| **S-SYS47-01** | `LCARS-videos/003 - System47： Enterprise-E Schematics…mkv` — still @ t=30s → `docs/construction/captures/S-SYS47-01.png` | Screensaver / complex screen | Literal | **Partial** — IR measured; live `sys47.literal` surface; see cue matrix |
| **S-SOV-MSD-01** | Sean Desktop `sovereign_msd.mp4` — frames in `docs/construction/captures/sovereign-msd/` | MSD / dual opposing spines (T2) | Literal (topology study) | **Queued** — alternate T2 reference for opposition conjunction |
| **S-TITAN-01** | `LCARS-videos/001 - Titan.DS…mkv` — clean top-down EPS frame | Screensaver | Literal | Backup / second pass |
| **S-WALL-01** | `Desktop/Star Trek MBP Wallpaper V2.png` | Still | Literal (anatomy study) | Anatomy reference for spine/elbow/gutter grammar |

**Primary done criterion for the LCARS proof (ladder step 1–2):** S-SYS47-01 recreated in the live app such that a stranger overlaying ref and build sees the same frame graph, segment inventory, type specimens, and schematic crop — cue matrix all pass — and the result is expressed through Scene IR / catalog primitives, not one-off CSS.

**Program done (later):** generative recomposition under that grammar, then a second non-LCARS system pack using the same pipeline (`docs/program-thesis.md`).

## Cue matrix stub (S-SYS47-01) — fill after measurement

Falsifiable must-pass list (numbers TBD from pixel probes; do not invent):

1. Canvas aspect and black field match extracted still
2. Dual vertical spine widths / canvas width within ±2%
3. Header elbow / gold band geometry within ±2px at study scale
4. Inter-segment gutter constant (state measured px; ±1px)
5. Side-profile Enterprise-E schematic IoU / SSIM vs traced asset ≥ agreed threshold
6. Bottom data grid + clock region present with measured row rhythm
7. Mini ship silhouette chip present at measured bbox
8. Status type (`SYSTEM STATUS: READY` or exact on-frame string) size/case/tracking within cue budget
9. Three sampled fills (header, spine mid, accent) Δe ≤ 3 vs still probes
10. Motion (if proving video): chrome locked; only allowed instrument cues move

IR path (to author): `docs/construction/S-SYS47-01.ir.json`  
Cue matrix sibling: `docs/construction/S-SYS47-01.cues.md`

## Explicit non-northstars for Literal claims

- Generic "LCARS-ish" CSS grid shells in the app without a row above
- Hand-authored SVG schematics not traced from a `sourceCrop`
- Token sheets that have not been Δe-checked against the active S-ID

## ADR rule

Any deliberate departure from a measured northstar sample (a11y plate, density for generative IR, APCA) requires a short ADR under `docs/adr/` naming the cue sacrificed and why. Silent constraint-driven aesthetic collapse is a Fail (ledger **C-06**).
