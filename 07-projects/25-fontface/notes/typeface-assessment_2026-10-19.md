---
title: Fontface — assessment of the Typeface analysis, and the ideas it leads to
type: note
project: 25-fontface
created: 2026-10-19
status: recommendation, questions for Sean (section 5)
source: read-only assessment workflow (5 assessors + synthesis) in the Fontface Claude Code session, against Fontface main @ 2553fad and [[07-projects/25-fontface/notes/typeface-app-analysis_2026-10-19]]. Measurements came from a read-only copy of Sean's library database (since deleted) and live Google Fonts metadata.
---

**Short answer:** the note's top suggestion, system auto-activation, is real but covers fewer apps than the note says, so it should start with a one-day test. The better bets are measured font filters, a shared name matcher, and tools for Figma and design tokens. Typeface looks weakest in those areas, and they are where Sean works every day.

Five assessors covered the note: auto-activation, importers, measured data, formats and Google Fonts, and product. This is the merged plan. Nothing in Fontface was changed. Typeface was not run.

## 1. Biggest insights

1. **The system route for auto-activation is a single Apple call, and it is fragile.**
   - Auto-activation means turning a font on by itself when an app asks for one that isn't on.
   - The call is `CTFontManagerCreateFontRequestRunLoopSource`. Apple deprecated it in macOS 11. It still works on this Mac's macOS 27.0.1.
   - Fontface isn't sandboxed, so it doesn't need Typeface's helper app.
   - It reaches fewer apps than the note claims:
     - Typeface's help suggests App Store apps don't ask on macOS 27 (Word, PowerPoint, TextEdit, Pages, the App Store Affinity apps). Unconfirmed.
     - InDesign has ignored this route since 2008.
     - Figma probably never asks.
2. **Typeface probably doesn't reach Figma either.** Its help says Font Switch doesn't work in web apps, and Figma isn't on its list of 26 known apps. The Figma and design-system workflow is open for Fontface.
3. **The note is wrong about classification.** Typeface's "Style" classes come from numbers the font maker typed in (PANOSE, IBM family class), not from measuring shapes.
   - Sean's imported Style tags match the declared class 99.8% of the time, and Google's categories 97.9%.
   - Most of his fonts declare nothing: 58% have no PANOSE code, 96% no IBM family class. Copying Typeface would leave about 5,300 styles with no class.
   - Measuring shapes works: a quick prototype agreed with his Sans/Serif tags on 96% of 3,711 styles, by testing for serifs on I, H and n.
4. **The numbers stored in fonts are often wrong.** 5,665 of 12,257 faces say weight 400; 344 faces named condensed say normal width; the monospace flag finds 406 faces where measuring finds 602 (it misses Roboto Mono, Monaco, Courier…). Measuring fixes these.
5. **Duplicates: name matching finds too many, file matching almost none.** 1,032 styles share a PostScript name; only 2 are byte-identical; 156 are truly the same design; 159 groups are Sean's own "other-versions" folders, kept on purpose. The "same file hash" half of the Phase 3 row would find almost nothing.
6. **The scanner hides files without saying so.** It only reads .ttf, .otf, .ttc and .otc. Old Mac suitcases and LWFN files often have no extension, so they're invisible. Typeface's own help warns that opening resource-fork font files can crash recent macOS.
7. **Google Fonts in numbers (measured 2026-10-19).** About 1,918 families, 2.25 GB in all; "language" families are 1.48 GB of that (Chinese, Japanese, Korean alone 1.37 GB). Only 3 of ~589 variable families have static files, so "prefer static" needs the user's own Google API key. Typeface uses its own mirror; Fontface shouldn't (Google's terms).
8. **Importers.** FontBase collections are an editable JSON file (easy). FontExplorer X is a dead product; a 2017 source says its database is SQLite. The Suitcase/Connect vault clashes with Fontface's rule against parsing another manager's vault (`docs/INTEGRATIONS.md:367`, `:427`). FontBase can't export its tags.

**Corrections to the analysis note:**
- **Pricing:** Typeface is not a subscription. Pro is a one-time $44.99 purchase.
- **Tracking:** "No tracking found" conflicts with its App Store privacy label, which lists a user ID and usage data linked to the user.
- **Auto-activated fonts:** for most apps they go to the asking app only, not "until logout" for all apps.
- **Connect vault path:** `~/Library/Extensis/Connect Fonts/`.
- **`FontCaseExtractor`** may be a seventh import source (Fontcase is another font manager), not a format reader. Unproven.
- **`.typeface-license`** is Typeface's own product licence, not a font licence.
- **The `xRatio` rule** can't be read as a "large x-height" class under either interpretation.

## 2. Ranked features

Effort: S = under a day, M = a few days, L = a week or more.

**A. Quick wins (S, high value)**
1. **"Listen and log" test build for auto-activation.** Proves which apps ask for missing fonts and what a request holds, changing nothing for them. Decides bet B6. Phase 4, dev-only.
2. **One shared name matcher, plus "Turn on fonts from a pasted list".** Paste PostScript names, full names or "Family Style" lines; see matches; turn on or tag. Needs a full-name lookup in `LibraryIndex` (`tags/mod.rs`). The base for the Figma plugin, tokens files, "fonts in this file", auto-activation and importers. Phase 4.
3. **Figma plugin v0, private.** Lists a file's fonts and flags missing ones; copy the list into Fontface. Depends on #2. Phase 4 (new row).
4. **Report skipped files in the scan summary.** Counts of Type 1, WOFF, .dfont, EOT and extensionless old Mac files per folder (type codes from file attributes, without opening the fork). Decides the format work. Phase 1.5.
5. **Copy as CSS, plus optical size following text size.** Clean CSS for the current axes and features, with a fallback, using `font-weight` etc. where possible. Phase 3.
6. **Glyph-name search, and Copy glyph as SVG.** Search Material Symbols by icon name; paste glyphs into Figma as vectors. Phase 3.
7. **Add a source's folders from the import preview.** The Typeface backup's folders get added with one tick each. Phase 4.
8. **Local log file and "Copy diagnostics".** Problems in the running app can be traced afterwards. Phase 1.

**B. Next big bets (M or L, high value)**
1. **Measured metrics and kind filters.** Serif, Sans, Mono…, plus weight, width and x-height measured from the shapes; a filter popover, Table columns and an Info row saying where each answer came from. ~6,650 styles have no Style tag today. New side table like the preview table. Phase 2. (M)
2. **Full library backup and restore.** Family choices, folders, on/off intent and settings, not only tags. Phase 4. (M)
3. **Local control channel and a `fontface` command-line tool.** `fontface on --tag Clients/Acme`, `fontface need tokens.json`; unlocks Shortcuts, Raycast, Adobe scripts and Claude. Local socket only, never TCP. Phase 4 (new row). (M)
4. **Type-scale and pairing studio, with token export.** Base size and ratio, preview at the system's sizes, named presets; export as CSS variables or DTCG typography tokens. Shares the CSS writer. Phase 3 (new row). (M)
5. **Project font sets from a tokens file, plus a menu bar toggle.** A tokens file becomes a "Projects/…" tag switched on with one click. Phase 4. (M)
6. **System auto-activation, MVP.** Gives the font to the asking app, with a deny list for web-page processes; never hands over a Google Drive placeholder (queue the download instead). Value medium today; high only if test A1 shows Sean's main apps ask. Phase 4. (M + M testing)
7. **"Fonts in this file".** Drop an .indd/IDML, PDF, Sketch or Office file; see what you have and what's missing; turn on or tag. Works with sandboxed apps and on Windows. Phase 4. (M)
8. **List Type 1 fonts, and show which have a modern copy.** Sean's ~1,100 Type 1 files become a "keep or rebuy" list. Phase 1.5. (M)
9. **Google sizes, a language-fonts switch, then category downloads.** Sizes and a free-space check; "Include language fonts (+1.5 GB)"; "Download all shown" without turning on. (S–M, S, M)

**C. Later or optional**
- Figma live bridge (local connection with a pairing token). M–L.
- Duplicates view with a strictness choice and "on purpose" marks. M (the Phase 3 🟡 row).
- "For all apps until logout" auto-activation mode with "Clear auto-activated" and a request history. S–M.
- Importers: FontBase collections (S, once there's a sample); FontExplorer X database (M, needs a rule decision); moved-path re-mapping (S–M); tags from folder names (S–M).
- Formats: WOFF/WOFF2 listing with the `wuff` decoder (M, with licence warnings); .dfont (S–M).
- Character tools: Unicode names, HTML entities and scripts (M); language alphabets (L).
- Smaller: notes and licence files on Info (S–M); print/PDF specimen spike (S–M); `fontface://` links (S); an MCP server for Claude once the CLI exists (S); opening backup files by double-click (S).
- Typeface custom families import (S–M; check Sean's backups first). Missing-character fallback font (Adobe NotDef, S). Variable/static preference (M, needs an API key). AppleScript commands (M). Adobe and Quark script route (L). Background listener while Fontface is closed (L). Colour-palette picker (low value: 21 colour faces).

**D. Skip, and why**
- Native Font Switch in Adobe and Office: L, with upkeep per app version; Sean works mostly in Figma.
- Mac App Store build: the sandbox breaks auto-activation; App Review may reject the helper.
- Trial, Pro tier or Setapp: breaks the "no paywall" promise.
- Telemetry, Sentry, intro tour, review prompts, expiring betas: against the no-tracking stance.
- App Intents: needs a Swift build step Tauri doesn't run; the CLI covers Shortcuts.
- A Google mirror: breaks Google's terms.
- Reading FontBase's IndexedDB for tags: L and fragile.
- Parsing the Suitcase/Connect vault: forbidden by the current rule; unknown format.
- Opening resource forks during scans: not until tested on a spare Mac.
- Adobe Blank as a loading placeholder: Fontface already hides text until its font loads.

## 3. Where Fontface stands

**Ahead:** on/off never behind a paywall; no account, nothing collected, a published list of hosts; per-family Google Get/Update/Remove with no mirror; imports Typeface backups, Finder tags and Font Book collections; family groups; not sandboxed (simpler auto-activation); measured classes and Figma/token workflows would be clear leaps.

**Behind, in ways users notice:** no auto-activation; no kind/weight/width/mono filters; WOFF, .dfont, Type 1 and suitcase files invisible; no imports from FontExplorer X, Suitcase, RightFont or FontBase; no CSS copy, duplicates tool, notes, print or layout presets; no full library backup; no scripting or links into the app; no Google size estimates or bulk download.

## 4. Risks, unknowns and cheap ways to prove them

- **Auto-activation on macOS 27:** which apps ask; what a request holds; how long the asker waits; who owns the returned list's memory; which listener wins with two managers running. Proof: test A1 (look the call up at run time so Fontface still launches if Apple removes it; return nothing). Try TextEdit, Pages, Word, Affinity (App Store and direct), Figma, Sketch; then macOS 14, 15 and 26 in VMs, and with another manager's listener running.
- **Disabled-but-registered fonts:** whether macOS auto-activates them is untested (one S experiment, low priority).
- **Drive placeholders:** could stall an asking app. Rule: never hand one over; queue the download.
- **Resource-fork crash:** test only on a spare Mac.
- **Type 1:** Fontface's test says macOS 27 refuses it; Typeface's help says it works on Ventura and Sonoma. Retest with an intact LWFN + suitcase pair and a .pfb/.pfm pair.
- **Drive attributes:** check a few extensionless files with `xattr -l` (read-only) for old type codes.
- **Measuring limits:** script and decorative fonts can't be measured reliably; Didot and flared faces are edge cases. Use the Style tags as a private test set.
- **`wuff` decoder** is at 0.2: fuzz before trusting.
- **Bulk downloads:** GitHub's rate limits aren't published.
- **Local connections:** CLI over a local socket only; the Figma bridge needs a pairing token.
- **Import formats:** unknown until there are sample files.

**Public repo:** binary-derived detail stays in the workspace: the 26-app list, the Calibri skip, the rule thresholds, and the finding that Typeface's tags follow declared data.

## 5. Questions for Sean

1. **Which apps must get fonts by themselves?** Figma only, or also InDesign, Illustrator, Office or Affinity on the personal Mac? Decides whether the Figma bridge or auto-activation comes first.
2. **May Fontface read another manager's own sorting data** (set names and membership, read-only, never the font files)? Including the Suitcase/Connect vault? Yes means narrowing `docs/INTEGRATIONS.md:367` and `:427`.
3. **Personal sample files?** A FontBase `.fontbase/` JSON, a FontExplorer X `.fexdb` (with `-wal`/`-shm`), or a RightFont library. No employer data.
4. **How should measured kinds appear?** Filters only, or also Built-in tags? Typeface's six words (Sans, Serif, Script, Ornamental, Symbolic, Monospaced), plus Slab?
5. **A spare Mac or VM for risky tests?** Resource forks, Type 1, auto-activation on older macOS.
