# Carved Flash SWFs — MSD screensaver EXEs

_Status: durable extract · 2026-08-09 · static carve only_  
**Not** S-SYS47-01 Literal authority. Motion/grammar study aids for MSD-style panels only.

## Provenance

Source root (Sean Drive library):

`/Users/snds/My Drive/Creative/Reference/Star Trek/LCARS`

| Vault folder | Source EXE folder | Source EXE |
|---|---|---|
| `MSD_Sovereign_Class/` | `MSD_Sovereign Class` | `MSD_Sovereign Class.exe` |
| `MSD_Dauntless/` | `MSD Dauntless` | `MSD Dauntless.exe` |
| `MSD_Defiant/` | `MSD Defiant` | `MSD Defiant.exe` |
| `MSD_Defiant_Main_Bridge/` | `MSD Defiant Main Bridge` | `MSD Defiant Main Bridge.exe` |
| `MSD_Prometheus/` | `MSD Prometheus` | `MSD Prometheus.exe` |
| `lcars_USS_Enterprise_Galaxy_Class_MSD/` | `lcars_USS_Enterprise_Galaxy_Class_MSD` | `lcars_USS_Enterprise_Galaxy_Class_MSD.exe` |

Each EXE is an Inno Setup self-extracting archive wrapping a **Macromedia Flash SWF** + 2Flyer Screensaver Pro INI (not Delphi LCARS, not System47).

Assessment: [`../../runtime-exe-assessment.md`](../../runtime-exe-assessment.md)

## What’s in each folder

- `*.swf` — original CWS (zlib-compressed Flash)
- `*_FWS.swf` — decompressed FWS copy (handy for JPEXS / tag inspection)
- `2flyer.ini` — screensaver host config (chrome paths only; not LCARS IR)
- Optional tiny embedded JPEGs where carved (Sovereign, Dauntless)

`summary.json` — carve inventory (tag counts, frame rates, shape/morph flags).

PE stubs / UPX hosts / ICO were **not** persisted (low value once SWF is out).

## What these are for

Flash **DefineShape** / **DefineShape2–4** (+ morphs on Sovereign / Defiant Bridge) sources for vector + sprite-timeline study after Sean approves **Ruffle** and/or **JPEXS (ffdec)**.

Prefer **MSD_Sovereign_Class** first (richest morphs/sprites; pairs with `sovereign_msd.mp4`).

## Explicit non-authority

- Do **not** cite these SWFs as Matches Literal evidence for **S-SYS47-01**.
- System47 Literal path remains Construction IR + measured stills/MKV under `docs/construction/`.
