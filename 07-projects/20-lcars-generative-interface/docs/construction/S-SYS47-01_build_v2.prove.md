# Prove report — S-SYS47-01

- Build: `/Users/snds/Projects/Workspace/07-projects/20-lcars-generative-interface/docs/construction/captures/S-SYS47-01_build_v2.png`
- Cuespec: `/Users/snds/Projects/Workspace/07-projects/20-lcars-generative-interface/docs/construction/S-SYS47-01.cuespec.json`
- Capture: **unverified** (no capture manifest (*.capture.json) — provenance unknown)
- Generated: 2026-08-26T11:03:54 by vqa/1.0

## Verdict: **PARTIAL**

- Measured: **8/16 pass** · attested (not proof): 3 · errors: 0
- Measured coverage: 84% · score: 0.50 · mean margin: -5.8177
- 8 measured cue(s) failing

| # | Cue | Probe | Status | Value | Target | Margin |
|---|---|---|---|---|---|---|
| 1 | Canvas aspect 16:9 | `aspect` | FAIL | 0.9953 | 1.7778 | -87.0317 |
| 2 | Background pure black | `color_at` | PASS | hex=#000000, delta_e=0.0, at_px=[8, 1058] | #000000 | 1.0 |
| 3 | Inter-element gutter 8px native | `gutter` | FAIL | mode_px=2, gap_count=2134 | 7.8 | -0.9861 |
| 4 | Header bar interior fill | `color_at` | FAIL | hex=#000000, delta_e=61.91, at_px=[768, 193] | #4881b5 | -6.7391 |
| 5 | Header elbow drop fill | `color_at` | PASS | hex=#5D8EBD, delta_e=4.04, at_px=[932, 176] | #4c8fc1 | 0.4944 |
| 6 | Header bar thickness at ML | `band_thickness` | FAIL | px=152.0, runs_found=1 | 122.5 | -1.5134 |
| 7 | Left header elbow structure | `shape_class` | FAIL | shape=bar, corner_radii={'tl': 0.0, 'tr': 0.0, 'bl': 0.0, 'br': 0.0}, open_quadrant=None | ['complex', 'elbow'] | -1.0 |
| 8 | Right header elbow present | `region_present` | PASS | fraction=0.408, rect_px=[1158, 42, 526, 339] | present >= 0.21 | 0.198 |
| 9 | Title string SYSTEM 47 | `attest` | ATTESTED |  |  |  |
| 10 | Registry peach text present | `region_present` | PASS | fraction=0.006, rect_px=[1053, 0, 1053, 423] | present >= 0.004 | 0.002 |
| 11 | Hero MSD occupies center band | `region_present` | PASS | fraction=0.3206, rect_px=[526, 317, 1053, 1164] | present >= 0.19 | 0.1306 |
| 12 | Hero MSD matches reference region | `ssim_region` | FAIL | 0.3169 | >=0.5 | -0.3661 |
| 13 | Callout column right of MSD | `count_regions` | PASS | 79 | [25, 110] | 1.0 |
| 14 | Mid pill cluster under schematic | `count_regions` | FAIL | 2 | [15, 80] | 0.6119 |
| 15 | Footer data band density | `count_regions` | PASS | 44 | [40, 180] | 1.0 |
| 16 | Silhouette chip bottom-right | `region_present` | PASS | fraction=0.2668, rect_px=[1643, 1820, 421, 254] | present >= 0.15 | 0.1168 |
| 17 | Accent orange coverage | `region_present` | FAIL | fraction=0.0, rect_px=[0, 0, 2106, 2116] | present >= 0.0007 | -0.0007 |
| 18 | Chrome locked under motion | `attest` | ATTESTED |  |  |  |
| 19 | Programmatic emission via Scene IR | `attest` | ATTESTED |  |  |  |

## Notes

- **1 Canvas aspect 16:9**: canvas 2106x2116
- **9 Title string SYSTEM 47**: text identity needs OCR (optional dep); peach registry color is measured by cue 10
- **12 Hero MSD matches reference region**: asset S-SYS47-01.png resized to 1053x1164
- **18 Chrome locked under motion**: single-still prove; verify with `vqa motion` on a frame sequence
- **19 Programmatic emission via Scene IR**: code-level fact, not pixel-measurable

---

_A cue passes only if an instrumented probe measured it. Attested cues are
declarations, not proof, and never count toward a Matches verdict._
