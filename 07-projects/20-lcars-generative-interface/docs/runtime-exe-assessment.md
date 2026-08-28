# Runtime EXE assessment — LCARS reference library

_Status: investigation complete (static only) · 2026-08-09 · Cursor · Composer · Personal MBP_  
_Does **not** claim Matches Literal. Separate from S-SYS47-01 northstar work._

## Where they live

Root: `/Users/snds/My Drive/Creative/Reference/Star Trek/LCARS`

Six sibling folders, each a single Windows `.exe` (no companion DLL/dat/readme):

| Folder | EXE | Size | Date |
|---|---|---:|---|
| `MSD_Sovereign Class` | `MSD_Sovereign Class.exe` | 708 KB | 2008-08-11 |
| `MSD Dauntless` | `MSD Dauntless.exe` | 640 KB | 2008-08-11 |
| `MSD Defiant` | `MSD Defiant.exe` | 659 KB | 2008-08-11 |
| `MSD Defiant Main Bridge` | `MSD Defiant Main Bridge.exe` | 662 KB | 2008-08-11 |
| `MSD Prometheus` | `MSD Prometheus.exe` | 643 KB | 2008-08-11 |
| `lcars_USS_Enterprise_Galaxy_Class_MSD` | `lcars_USS_Enterprise_Galaxy_Class_MSD.exe` | 627 KB | 2010-10-18 |

**Not found as EXEs in this library:** System47 installer/screensaver binaries. System47 appears only as captured loops under `LCARS-videos/` (and Desktop playlist downloads). Desktop also has `sovereign_msd.mp4` (likely a screen capture of the Sovereign Flash MSD).

## What they actually are

`file` reports **PE32 GUI · Inno Setup self-extracting archive** (Inno Setup Data **2.0.11**).

Payload (identical wrapper across all six; only the embedded SWF differs):

1. Inno stub PE (~63 KB)
2. UPX-packed PE (~335 KB) — shared screensaver host
3. **Macromedia Flash SWF** (CWS zlib, Flash 8; Galaxy is Flash 10 / Adobe Flash CS4)
4. INI config for **2Flyer Screensaver Pro** (`SplashImage=...\2Flyer\Screensaver Pro\...`, `PicturePath=F:\My web flashes\LCARS MSD …`)
5. Shared 32×32 ICO

So: fan-made **Flash MSD panels** packaged as Windows screensavers via a commercial Flash screensaver builder — **not** Delphi LCARS runtimes, **not** System47, **not** DirectX apps.

## Decompile / extract?

| Layer | Verdict | Method |
|---|---|---|
| Outer EXE | **Yes (unpack)** | Inno Setup archive; `innoextract` preferred. Without it, carve `zlb\x1a` zlib streams (verified). |
| UPX host PE | **Partial** | UPX-packed; `upx -d` would expose host strings. Low value once SWF is out. |
| SWF content | **Yes (decompile/export)** | JPEXS Free Flash Decompiler (`ffdec`) → shapes, sprites, morphs, fonts, timeline. Not native C decompile. |
| ActionScript | **Mostly N/A** | No `DoABC` (AS3). Sparse `DoAction` on a few sprites. Motion is timeline/sprite driven. |

Static extract was performed to `/tmp/lcars-msd-extract/` (ephemeral) and **persisted** to `docs/construction/runtime-swf/` (SWF + FWS + INI + `summary.json`; PE stubs omitted). Re-carve from Drive EXEs anytime if needed.

## Vectors / assets / animation structure

**Vectors: yes.** All six SWFs contain `DefineShape` / `DefineShape2` / `DefineShape3` / `DefineShape4`. Morph shapes present on Sovereign (3) and Defiant Main Bridge (2).

**Rasters: sparse.** Sovereign: two tiny JPEGs (10×34, 8×20). Dauntless: one 300×300 JPEG. Others: no embedded JPEG tags found. Layout is overwhelmingly vector + text/fonts (`DefineFont3`, lots of `DefineText` / `DefineEditText`).

**Layout/config:** only the 2Flyer INI (screensaver chrome, not LCARS IR). No XML/JSON layout IR.

**Animation model:** main timeline is **1 frame** @ ~10–12 fps. Motion lives in nested **DefineSprite** timelines (examples: Sovereign sprites up to 96 frames; Defiant to 176; Prometheus to 165). Galaxy Class SWF has **no** multi-frame sprites (effectively static/near-static). Stage sizes (px): Sovereign 1450×420; Galaxy 2260×730; Defiant Bridge 1274×258; etc.

**Fonts:** embedded Flash fonts including string hit `LCARS Title Font`. Export via JPEXS possible; licensing for reuse still a separate question.

## Playback on macOS (honest)

| Option | Works without Windows? | Notes |
|---|---|---|
| **Ruffle** on extracted `.swf` | **Best path** | Open/play SWF natively in browser or desktop build. Not installed here yet. |
| **JPEXS / ffdec** | Yes (needs Java) | Preview + export SVG/PNG/sprites. Java present; ffdec not installed. |
| Existing **video captures** | Yes | `sovereign_msd.mp4`, System47 MKVs — already usable for motion guidance; no EXE run. |
| Wine / CrossOver running the EXE | Partial | Possible later; unnecessary once SWF is carved. Wine not installed. |
| QEMU/full Windows VM | Works, heavy | Only if you want original 2Flyer fullscreen host behavior. |
| DOSBox | No | Irrelevant (Win32 PE). |
| Run unknown EXE on host | **Do not** | Prefer static extract. |

**Risk:** Fan reference tooling Sean already holds; wrapper is known-class (old Inno + 2Flyer + Flash). Risk for **static carve** is low. Risk for **blind execution** is higher than needed — skip.

## Relation to Literal / S-SYS47-01

These EXEs are **useful motion/grammar references for MSD-style panels**, especially Sovereign. They are **not** the System47 northstar and must not be cited as Matches Literal evidence for S-SYS47-01.

System47 animation guidance remains: measured construction IR + MKV/mp4 captures already in the vault/app northstar pipeline.

### Composite reference library

SWFs sit with AI vectors, video loops, and other Drive assets as one **composite** library: inform shape grammar, motion cadence, density, and content-group topology. They do **not** replace Construction IR or silently change Literal acceptance cues. **S-SYS47-01 remains Literal authority** unless Sean renames the northstar. Full rule: `docs/visual-replication-requirements.md` → Composite reference library.

## Sibling vector reference (Illustrator, not Flash)

Separate from these EXEs: Sean’s Drive file `1701_D_Mk4.ai` (Galaxy-class 1701-D MSD, Illustrator 27.5 PDF-compatible). Assessed 2026-08-09 — **true path vectors** (551 Form XObjects, 0 image XObjects); preview at `docs/construction/references/1701d-mk4/`. Full write-up: [`docs/vector-msd-1701d-mk4.md`](vector-msd-1701d-mk4.md). Same rule: grammar only, not S-SYS47-01 Literal.

## Recommended next step (needs Sean approve)

1. ~~Persist carved SWFs~~ — done: `docs/construction/runtime-swf/` (~912 KB; see README there).
2. **Needs Sean approve:** install **Ruffle** + **JPEXS ffdec**; open `MSD_Sovereign_Class` SWF; export vector shapes / sprite strips for animation-timing study.
3. Keep using `sovereign_msd.mp4` + System47 MKVs for playback-as-guidance until Ruffle is set up.
4. Optional: `brew install innoextract upx` once Homebrew Cellar perms are fixed (sandbox/403 blocked install this session).
5. Parallel track: continue S-SYS47-01 native prove (cue matrix) — SWFs are not Literal authority for that screen.

## Extract recipe (macOS, no install)

```bash
# Carve zlib streams after Inno zlb\x1a markers; keep the CWS/FWS SWF.
# See session scratch under /tmp/lcars-msd-extract/ for a prior run.
python3 - <<'PY'
# (same carve used 2026-08-09: find b"zlb\\x1a", zlib.decompress, classify CWS/MZ/INI/ICO)
PY
```

Prefer `innoextract <file.exe>` when available.
