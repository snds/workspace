# Prove report — S-SYS47-01

- Build: `/Users/snds/Projects/Workspace/07-projects/20-lcars-generative-interface/docs/construction/captures/S-SYS47-01_build_v3.png`
- Cuespec: `/Users/snds/Projects/Workspace/07-projects/20-lcars-generative-interface/docs/construction/S-SYS47-01.cuespec.json`
- Capture: **unverified** (no capture manifest (*.capture.json) — provenance unknown)
- Generated: 2026-08-26T11:03:04 by vqa/1.0

## Verdict: **PARTIAL**

- Measured: **13/16 pass** · attested (not proof): 3 · errors: 0
- Measured coverage: 84% · score: 0.81 · mean margin: 0.4707
- 3 measured cue(s) failing

| # | Cue | Probe | Status | Value | Target | Margin |
|---|---|---|---|---|---|---|
| 1 | Canvas aspect 16:9 | `aspect` | PASS | 1.7778 | 1.7778 | 1.0 |
| 2 | Background pure black | `color_at` | PASS | hex=#000000, delta_e=0.0, at_px=[8, 540] | #000000 | 1.0 |
| 3 | Inter-element gutter 8px native | `gutter` | PASS | mode_px=3, gap_count=1907 | 4.0 | 0.3333 |
| 4 | Header bar interior fill | `color_at` | PASS | hex=#4985B9, delta_e=1.64, at_px=[700, 99] | #4881b5 | 0.7944 |
| 5 | Header elbow drop fill | `color_at` | PASS | hex=#4F96C7, delta_e=2.77, at_px=[850, 90] | #4c8fc1 | 0.654 |
| 6 | Header bar thickness at ML | `band_thickness` | PASS | px=59.0, runs_found=1 | 62.5 | 0.4167 |
| 7 | Left header elbow structure | `shape_class` | PASS | shape=complex, corner_radii={'tl': 42.0, 'tr': 0.0, 'bl': 25.1, 'br': 0.0}, open_quadrant=None | ['complex', 'elbow'] | 1.0 |
| 8 | Right header elbow present | `region_present` | PASS | fraction=0.3449, rect_px=[1056, 22, 480, 173] | present >= 0.21 | 0.1349 |
| 9 | Title string SYSTEM 47 | `attest` | ATTESTED |  |  |  |
| 10 | Registry peach text present | `region_present` | PASS | fraction=0.0115, rect_px=[960, 0, 960, 216] | present >= 0.004 | 0.0075 |
| 11 | Hero MSD occupies center band | `region_present` | PASS | fraction=0.4188, rect_px=[480, 162, 960, 594] | present >= 0.19 | 0.2288 |
| 12 | Hero MSD matches reference region | `ssim_region` | FAIL | 0.1951 | >=0.5 | -0.6098 |
| 13 | Callout column right of MSD | `count_regions` | PASS | 56 | [25, 110] | 1.0 |
| 14 | Mid pill cluster under schematic | `count_regions` | PASS | 39 | [15, 80] | 1.0 |
| 15 | Footer data band density | `count_regions` | FAIL | 20 | [40, 180] | 0.7183 |
| 16 | Silhouette chip bottom-right | `region_present` | FAIL | fraction=0.0, rect_px=[1498, 929, 384, 130] | present >= 0.15 | -0.15 |
| 17 | Accent orange coverage | `region_present` | PASS | fraction=0.003, rect_px=[0, 0, 1920, 1080] | present >= 0.0007 | 0.0023 |
| 18 | Chrome locked under motion | `attest` | ATTESTED |  |  |  |
| 19 | Programmatic emission via Scene IR | `attest` | ATTESTED |  |  |  |

## Notes

- **1 Canvas aspect 16:9**: canvas 1920x1080
- **9 Title string SYSTEM 47**: text identity needs OCR (optional dep); peach registry color is measured by cue 10
- **12 Hero MSD matches reference region**: asset S-SYS47-01.png resized to 960x594
- **18 Chrome locked under motion**: single-still prove; verify with `vqa motion` on a frame sequence
- **19 Programmatic emission via Scene IR**: code-level fact, not pixel-measurable

---

_A cue passes only if an instrumented probe measured it. Attested cues are
declarations, not proof, and never count toward a Matches verdict._
