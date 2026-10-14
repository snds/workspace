---
type: decision
description: Why Sean's Google Drive (hello@snds.design) uses a numbered NN-Name top level ordered by irreplaceability, and how the Oct 2026 dedup/reorg was run
created: 2026-10-13
confidence: high
---

Sean's **My Drive** uses a numbered top level, `NN-Name`, ordered by how hard each folder would be to replace. Lowest number is most important. The scheme was adopted and executed 2026-10-12 → 13.

| # | Folder | Holds |
|---|---|---|
| 01 | `01-Documents` | 9 numbered categories: Medical, Financial, Housing, Career, Family, Vehicles-Legal, Personal, Google-Docs, Scans |
| 02 | `02-Security` | Recovery codes and keys |
| 03 | `03-Photos` | Personal photos |
| 04 | `04-Creative` | SNDS-Design, Work, Personal, Resources, Fonts, Reference, Tutorials, Enterprise-Build, To-Audit |
| 05 | `05-Projects` | `lattice`, `old-legion` |
| 06 | `06-Homelab` | Homelab material |
| 07 | `07-Images` | Wallpapers, memes, profile photos, inspiration |
| 08 | `08-Videos` | Videos, plus `Torrents` |
| 09 | `09-Audio` | Album folders live under `Music/` |
| 10 | `10-Gaming` | Gaming files |
| 11 | `11-Tech` | Apps, PC-Utilities, Hardware-Drivers, PC-Parts |
| 12 | `12-Adult` | Last, so it sorts out of the way |
| 99 | `99-Review` | `Duplicates/` and `Empty-or-Junk/`, each mirroring the original path |

**Rules Sean set**
- `NN-Name` format: two digits, a hyphen, a Title-Case name.
- **`00` is reserved for Sean at every level.** Agents never create a `00-` folder. Existing ones are renumbered only with his OK.
- Numbers are **sequential**. With about 12 folders, gaps buy nothing, and a Drive rename keeps IDs and links.
- Subfolders are numbered only where there are 5 or more siblings **and** their order means something. That excludes album, game and year folders.
- **Non-destructive only.** Never delete, trash or overwrite. Use true server-side moves so IDs, share links and history survive.
- Duplicates are *staged* in `99-Review`; Sean decides later whether to delete them.

**Why**
- The March 2026 pass promoted folders without an order, so new import dumps (`From iCloud Drive`, `parts`, `lattice`, `old-legion`) kept appearing at the root.
- A ranked, numbered top level makes the most important material easiest to find, and gives every new item an obvious home.

**Alternatives rejected**
- **Gapped numbering** (10, 20, 30): it reads worse, and inserting a folder is cheap anyway.
- **Merging `Images` into `Creative/Reference`:** flagged as an overlap, not merged.
- **Flattening deep trees:** the depth is almost entirely *inside* asset packs and work archives, and flattening would break them.
- **Splitting InDesign packages** (`Links`, `Document fonts`), flipbook exports and LCARS kits to dedupe them: those copies are deliberate.

**Outcome (verified 2026-10-13)**
- 22,527 logged moves, plus 5 interrupted moves completed afterwards. Every one has the same file ID at its new path, and **0 file IDs are missing**.
- `99-Review` holds 90.5 GB that can be reclaimed if Sean empties it: 90.4 GB of duplicates and 70 MB of junk and empty folders.
- File count and bytes differ from Phase 1 **only** because of a parallel font-repair session in `04-Creative/05-Fonts`:
  - 465 new files: fonts, plus `00-Licensing`.
  - 2,452 font files rewritten.
  - See `font-fix-log.csv` and the font-library memory in the files-reorg project.
- **LCARS** was consolidated to `04-Creative/06-Reference/Star Trek/LCARS`.
- The second **12th Fleet** tree sits whole under `04-Creative/03-Personal/12th Fleet/From-Reference-Star-Trek`, to be reconciled by hand later.

**Open items (Sean's call)**
- Possibly empty `99-Review`.
- Sort the ~450 loose files at the top of `01-Documents`.
- 28 leftovers in `From iCloud Drive`, and the now-empty `Outlook` folder.
- 879 version series and 231 zip-plus-extracted pairs (69 GB), none staged.
- Public "anyone with link" shares on medical, resume and family-finance files.
- `claude-haiku-api-key.txt`, now in `02-Security`: rotate the key.
- `05-Fonts/00-Licensing` uses Sean's reserved `00` number. It was named by the font session.

**Lessons for the next run**
- Key every move by content (`step|orig_path|dst`), never by a row number that restarts when the plan is regenerated.
- Stage parent folders before their children.
- Never run two agents that move files in the same Drive at once.
- Run rclone from bash, not PowerShell; PowerShell redirection re-encodes non-ASCII names.

**Artifacts** (the platform `Projects` dir, not this vault): `Projects/files-reorg/`
- `drive-reorg-plan.md` / `.html`: the approved plan.
- `drive-moves.csv`: the undo manifest.
- `drive-moves-results.csv`.
- `tools/` (`execute.py`, `rollback.py`, `verify.py`, `generate_plan.py`, …).
- `phase1/` and `phase5/` inventories.
- `phase2/visual/visual-review.md`.
- `RESUME.md`.

Related: [[decision-portable-workspace-refactor]] · [[fact-workspace-repos]]
