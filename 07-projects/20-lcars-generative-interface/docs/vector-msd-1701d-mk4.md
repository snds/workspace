# Vector MSD reference — 1701-D Mk4 (Illustrator)

_Status: assessed on macOS without Illustrator · 2026-08-09 · Cursor · Composer · Personal MBP_  
_Authority: **vector grammar / construction reference only**. Not Matches Literal for S-SYS47-01 (Enterprise-E System47)._  
_Composite library (with SWFs / video loops): informs grammar — does not override active northstar IR/cues; Galaxy ≠ SYS47 match. See `docs/visual-replication-requirements.md`._

## Source

| Field | Value |
|---|---|
| Path | `/Users/snds/My Drive/Creative/Reference/Star Trek/1701_D_Mk4.ai` |
| Size | 5 789 149 bytes (~5.5 MB) |
| FS mtime | 2023-06-12 (Drive); PDF ModDate 2023-05-12 14:53 PDT |
| `file` | PDF document, version 1.6, 1 page |
| Creator | Adobe Illustrator **27.5** (Macintosh); PDF library 17.00 |
| MediaBox | **12336.8 × 4862.11** pts (~2.54∶1 wide MSD panel) |

PDF-compatible AI (`%PDF-1.6` head). Large-canvas AI24 (`%AI24_LargeCanvasScale`, `%AI5_ArtSize: 14400 14400`). Private AI payload present (`PieceInfo/Illustrator`, `%AI24_ZStandard_Data`).

## Extractability (no Illustrator)

| Probe | Result |
|---|---|
| `pdfinfo` / Poppler | Works. 1 page, unencrypted. |
| `pdftotext` | **Empty** — labels are outlined paths (or non-text), not extractable glyphs. |
| `pdftoppm` | Works. Preview at 14 dpi → **2399×946** PNG. |
| `qlmanage -t` | Sandbox-blocked this session; Poppler preview sufficient. |
| `mutool` / `gs` | Not installed (not required). |
| Named layers for content groups | **No.** OCG name is only `Layer 1`; `%AI5_NumLayers: 1`. No identity/spine/focal/callout/footer layer map without opening AI. |
| Embedded images | **0** `/Subtype/Image`, **0** `/DCTDecode`, **0** `/Im*` XObjects. (XMP holds a tiny thumbnail JPEG only.) |
| Vector structure | **551** Form XObjects (`/Fm0`…`/Fm550`); **34** Shading objects; main Flate content stream: ~27k `m`, ~96k `l`, ~82k `c`, 551 `Do`, thousands of `re`/`f`/`S`/`sh`. |

**Verdict:** Real path geometry (elbows, pills, ship cutaway, callout polylines), not a live-traced raster plate. Preview + path-op census are available on macOS today. Full native AI group tree / editable paths still want Illustrator (or an AI→SVG export Sean runs once).

## What the preview shows (grammar, not SYS47 Literal)

Galaxy-class lateral MSD: dual top elbows (class + ship ID), bottom-left “MASTER SYSTEMS DISPLAY” elbow, lavender/orange pill strips, dense vector cutaway with perimeter callout leaders, corner orthographic insets + radial diagnostic. Maps *conceptually* to content groups (identity / spine / focal MSD / callouts / support / footer aesthetic) but **composition and ship class differ** from S-SYS47-01.

## Use in the Literal program

**Do use for:**

- Shape grammar: constant-stroke elbows, pill aspect, callout leader orthography, dual opposing top frame.
- Construction IR vocabulary: frame vs focal vs callout vs support insets (same *roles* as content groups; different measured geometry).
- Contrast with Flash DefineShape MSD EXEs (`docs/runtime-exe-assessment.md`) — this file is native Illustrator paths at print-scale resolution.

**Do not use for:**

- Matches Literal / Δe / SSIM against S-SYS47-01.
- Drop-in recipe topology or Enterprise-E System47 chrome.

## Persisted vault artifacts

- Preview: `docs/construction/references/1701d-mk4/preview.png`
- README: `docs/construction/references/1701d-mk4/README.md`
- Full `.ai` **not** copied into vault (Drive remains source of truth; 5.5 MB + Google Drive sync).

## Blocked-on / optional next

- **Illustrator (or AI→SVG export by Sean):** named groups, editable elbows, font vs outlines, export of frame-only / ship-only layers.
- Not blocked for grammar study: Poppler preview + this note are enough to inform Construction IR shape primitives.
- Unrelated track: Flash SWF Ruffle/JPEXS still needs Sean approve (see runtime EXE assessment).
