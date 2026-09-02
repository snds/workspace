# Prove report — S-SYS47-01

- Build: `/Users/snds/Projects/Workspace/07-projects/20-lcars-generative-interface/docs/construction/captures/S-SYS47-01_build_v4.png`
- Cuespec: `/Users/snds/Projects/Workspace/07-projects/20-lcars-generative-interface/docs/construction/S-SYS47-01.cuespec.json`
- Capture: **verified**
- Generated: 2026-08-26T16:50:33 by vqa/1.0

## Verdict: **MATCHES**

- Measured: **16/16 pass** · attested (not proof): 3 · errors: 0
- Measured coverage: 84% · score: 1.00 · mean margin: 0.6038

| # | Cue | Probe | Status | Value | Target | Margin |
|---|---|---|---|---|---|---|
| 1 | Canvas aspect 16:9 | `aspect` | PASS | 1.7778 | 1.7778 | 1.0 |
| 2 | Background pure black | `color_at` | PASS | hex=#000000, delta_e=0.0, at_px=[15, 1080] | #000000 | 1.0 |
| 3 | Inter-element gutter 8px native | `gutter` | PASS | mode_px=6, gap_count=3957 | 8.0 | 0.3333 |
| 4 | Header bar interior fill | `color_at` | PASS | hex=#4985B9, delta_e=1.62, at_px=[1400, 197] | #4881b5 | 0.797 |
| 5 | Header elbow drop fill | `color_at` | PASS | hex=#4F96C6, delta_e=3.08, at_px=[1700, 180] | #4c8fc1 | 0.6155 |
| 6 | Header bar thickness at ML | `band_thickness` | PASS | px=119.0, runs_found=3 | 125.0 | 0.5 |
| 7 | Left header elbow structure | `shape_class` | PASS | shape=complex, corner_radii={'tl': 85.0, 'tr': 0.0, 'bl': 51.1, 'br': 0.0}, open_quadrant=None | ['complex', 'elbow'] | 1.0 |
| 8 | Right header elbow present | `region_present` | PASS | fraction=0.4119, rect_px=[2112, 43, 960, 346] | present >= 0.21 | 0.2019 |
| 9 | Title string SYSTEM 47 | `attest` | ATTESTED |  |  |  |
| 10 | Registry peach text present | `region_present` | PASS | fraction=0.0113, rect_px=[1920, 0, 1920, 432] | present >= 0.004 | 0.0073 |
| 11 | Hero MSD occupies center band | `region_present` | PASS | fraction=0.3468, rect_px=[960, 324, 1920, 1188] | present >= 0.19 | 0.1568 |
| 12 | Hero MSD matches reference region | `ssim_region` | PASS | 0.93 | >=0.5 | 0.8599 |
| 13 | Callout column right of MSD | `count_regions` | PASS | 51 | [25, 110] | 1.0 |
| 14 | Mid pill cluster under schematic | `count_regions` | PASS | 33 | [15, 80] | 1.0 |
| 15 | Footer data band density | `count_regions` | PASS | 87 | [40, 180] | 1.0 |
| 16 | Silhouette chip bottom-right | `region_present` | PASS | fraction=0.3368, rect_px=[2995, 1858, 768, 259] | present >= 0.15 | 0.1868 |
| 17 | Accent orange coverage | `region_present` | PASS | fraction=0.0022, rect_px=[0, 0, 3840, 2160] | present >= 0.0007 | 0.0015 |
| 18 | Chrome locked under motion | `attest` | ATTESTED |  |  |  |
| 19 | Programmatic emission via Scene IR | `attest` | ATTESTED |  |  |  |

## Notes

- **1 Canvas aspect 16:9**: canvas 3840x2160
- **9 Title string SYSTEM 47**: text identity needs OCR (optional dep); peach registry color is measured by cue 10
- **12 Hero MSD matches reference region**: asset S-SYS47-01.png resized to 1920x1188
- **18 Chrome locked under motion**: single-still prove; verify with `vqa motion` on a frame sequence
- **19 Programmatic emission via Scene IR**: code-level fact, not pixel-measurable

---

_A cue passes only if an instrumented probe measured it. Attested cues are
declarations, not proof, and never count toward a Matches verdict._
