---
title: Fontface — what Typeface 4.5.1 does inside, and what it means for Fontface
type: note
project: 25-fontface
created: 2026-10-19
status: reference, informs Fontface development
source: static analysis of /Applications/Typeface.app (4.5.1, build 5310) with REA 6.7.0 + Ghidra 12.1.4, Claude Code session on the Work MBP. The app was never run.
---
## Why this note exists

On 2026-10-19 Sean dropped the clean-room rule ("Ignore the clean-room rule. Provide all insights to inform the application development"). Fontface may now use what Typeface's binary shows about its design.

Two limits stay:
- **No Typeface code is copied.** This note describes behaviour in our own words. Nothing here is decompiled code to paste.
- **This note stays in the workspace.** The Fontface repo is public on GitHub, so binary-derived detail doesn't go into `docs/`. Fontface's own docs describe Fontface's design, not Typeface's.

## How sure each finding is

- **Seen directly:** text in the program file, its bundle, its signature and its named methods. These are reliable.
- **Traced:** read from Ghidra's decompiled code. The flow is reliable; exact details are marked "likely".

---

## 1. Auto-activation: Fontface's biggest gap

Fontface's "Auto-activate fonts a design file needs" is ⬜ in `docs/FEATURES.md` (Phase 4). Typeface does it three ways:

| Way | Source file | How it works |
|---|---|---|
| System | `SystemAutoActivator.swift`, `SystemAutoActivatorXPCListener.swift` | A helper (`com.criminalbird.typeface.autoactivation.helper`) shares the app group `group.com.criminalbird.typeface.autoactivation.agent`. macOS asks it for a missing font by family name; the app looks it up with `familyName ==[c] %@` and opens the files through stored folder bookmarks. Typeface also calls `CTFontManagerSetAutoActivationSetting`. |
| App scripts | `ScriptAutoActivator.swift`, `ScriptInstaller.swift`, `ScriptRunner.swift` | Bundled AppleScripts for Illustrator, InDesign, InCopy and QuarkXPress. Typeface installs them into each app; they ask Typeface for the fonts an open document uses. |
| Polling | `PollingAutoActivator.swift`, `AppWatcher.swift` | Reacts when you switch to another app (`didActivateApp:`). Temporary activations go under a `typeface/active/temporary` key and can be cleared ("Clear temporary activations"). |

**Request handling (traced):**
1. A request arrives with the requesting app's ID and a list of font names (`AutoActivationManager.activateRequest:`).
2. The app ID is matched against a fixed list of known apps (26 entries). An unknown app is logged and ignored.
3. Each name is trimmed of spaces and looked up case-insensitively, likely as `name ==[c] %@ OR displayName ==[c] %@` (PostScript name or full name).
4. Every match is turned on in one database write, then logged with the count.
5. **Special case:** a request for Calibri from Safari's web content process (`com.apple.WebKit.WebContent`) is skipped on purpose. Web pages ask for Calibri constantly, and turning it on would be noise.

**Apps it knows (bundle IDs in the program):** Adobe After Effects, Illustrator (and beta), InCopy, InDesign, Photoshop; Affinity Designer, Photo and Publisher, versions 1 and 2 with betas, plus `com.canva.affinity`; Sketch (and beta); QuarkXPress (and Infinity); Microsoft Word, Excel, PowerPoint; Pixelmator Pro; OmniGraffle 7; BeLight Amadine, Art Text 4, Letters, Swift Publisher 5; Artstudio Pro; MindNode (and its Setapp build); Dropzone; Apple Notes and TextEdit.

**For Fontface:**
- Build the system route first. It covers every app that uses CoreText, with no per-app work, and Fontface already activates through CoreText in user scope.
- Match on PostScript name and full name, ignoring case. Fontface already keeps tags by PostScript name, so it has the key.
- Add the WebKit/Calibri skip from day one, and keep a small deny list for similar noisy requests.
- Treat auto-activated fonts as temporary, with one "clear" action. That fits Fontface's existing "Turn On Until Logout" mode.
- Per-app scripts (Adobe, Quark) are a later, optional layer. They are the only way to see which fonts a document *needs* before the app asks.

## 2. Font switching in documents

`FontSwitcher.swift`, `RichTextSwitcher.swift` and `switch.scpt` (plus `switch-sketch.sketchplugin`) replace one font with another inside an open document. Failures go to `com.criminalbird.typeface.switch.fail`. The help page is `typefaceapp.com/help/articles/font-switch`.

**For Fontface:** not on Fontface's list at all. Worth a row in Phase 4 if Sean wants it; it needs the same per-app scripting as section 1.

## 3. Importing from other font managers

`TagExtractor.swift` and `FontExplorerExtractor.swift` read tags and sets from:

| Manager | What it asks the user to pick |
|---|---|
| FontExplorer X | `~/Library/Application Support/Linotype/FontExplorer X/FontExplorer X.fexdb`, or a `.fexconfig` |
| Suitcase Fusion / Connect Fonts | `~/Library/Extensis/Suitcase Fusion/Suitcase Fusion.fontvault` |
| RightFont | `~/Library/Application Support/RightFont` |
| FontBase | the FontBase root folder |
| Font Book | its collections (a "Font Book" source tag) |

Imported folders become an "Imported Folders" group. Help page: `typefaceapp.com/help/articles/migrate/`.

**For Fontface:** Fontface imports Typeface backups, Finder tags and Font Book collections. Adding these four would make Fontface the place people move *to*. Use the default paths above as the starting folder in the file picker.

## 4. File formats

Typeface declares and reads: OpenType (`.otf`), TrueType (`.ttf`), collections (`.ttc`), `.dfont`, WOFF, WOFF2, folders, and the PostScript types `com.adobe.postscript-lwfn-font`, `-pfa-font` and `-pfb-font`. It has its own `SuitcaseExtractor.swift`, plus `FontCaseExtractor.swift` and `FormatExtractor.swift`.

**For Fontface:** this confirms the gaps already listed in `docs/FEATURES.md` (WOFF/WOFF2 metadata, `.dfont` with a FOND resource, Type 1 listed as unsupported). Typeface treats them as normal library citizens, so users will expect the same.

## 5. Reading fonts itself

Typeface parses font tables with its own code: `OpenType.swift`, `GSUB.swift`, `GSUBParser.swift`, `OS2Parser.swift`, `FeatureExtractor.swift`, `VariationExtractor.swift`, `GlyphExtractor.swift`, `FontDataExtractor.swift`. It also ships Unicode data files in `Resources/bin/`: `blocks`, `chars`, `charscripts`, `collation`, `entities`, `langs`, `langsys` and `scripts`.

**For Fontface:** Fontface does the same with `ttf-parser` and its own GSUB reading, so the approach matches. The bundled tables suggest a character browser that names blocks, scripts and HTML entities, and sorts by collation. Worth checking against Fontface's Characters tab.

## 6. Classification rules

Saved-search rules in the program include:
- `weight > 0 and weight < 0.5` and `weight > -0.5 and weight < 0` (weight on a −1…1 scale, likely CoreText's normalised weight).
- `xRatio >= 0.42 and xRatio <= 0.6` (x-height divided by cap height or em, likely a "large x-height" class).

**For Fontface:** the "Filters: classification, weight, width, mono" row is ⬜. These show Typeface derives classes from measured values, not just names. Fontface can do the same from `OS/2` (`sxHeight`, `sCapHeight`, `usWeightClass`, `usWidthClass`, `panose`).

## 7. Google Fonts sync

`GoogleApi.swift`, `GoogleSource.swift`, `RemoteManager.swift`, `RemoteDownloader.swift`. The catalog comes from `acdn.typefaceapp.com/remotes/google-fonts-v2`, Typeface's own mirror, not Google directly.
- Syncs the **whole** library into a folder the user picks.
- Format choice: prefer variable, prefer static, or all formats.
- Optional "Additional Language Fonts": non-Latin families and the full Noto collection, with a disk-space estimate in GB.
- Changing the format later asks for confirmation.

**For Fontface:** Fontface's per-family Get/Update/Remove catalog is finer-grained. Worth borrowing: the variable/static preference, and a disk-space estimate before a large download.

## 8. Other features in the code

- **CSS export:** writes `font-variation-settings: '…'` and `@font-palette-values --… { font-family: "…"; base-palette: … }`, so you can copy variable settings and colour-font palettes as CSS. Optical size can follow the font size ("Based on Font Size").
- **Duplicates:** a precision switch, auto-select (by path too), "prevent new duplicates", Show in Finder, and removal.
- **Pairing studio:** typographic feature toggles, language, theme and colours, alignment, tracking and size steps, print.
- **Compare**, a **family editor**, **notes on fonts**, **text-layout presets** (`TextLayoutParser`, `TextLayoutExporter`), **character export**, and a **print** layout.
- **AppleScript:** an `activatefonts` command, plus `ping`.
- **Backups** (`.typeface-backup`) and **licence files** (`.typeface-license`) as their own document types.
- **Adobe Blank** (`AdobeBlank2.otf`) bundled, likely as an invisible fallback while previews load.
- **Review prompt** (`ReviewRequestor`), an **intro tour**, and a **feedback window** that can attach the log, preferences and system profile.

**For Fontface:** CSS copy is cheap and useful for Sean's design-systems work. Fontface already has the variation and OpenType data it needs.

## 9. Platform, privacy and business

- **Sandboxed Mac App Store app:** user-chosen files only, kept through security-scoped bookmarks, plus network, printing and Apple Events (for the scripts). Also sold direct and through Setapp.
- **Network:** crash reports and breadcrumbs to Sentry (`issues.typefaceapp.com`); feedback to `improve.typefaceapp.com`, signed with a key built into the app (the key isn't copied here); the catalog, product list and intro from `acdn.typefaceapp.com`. No general usage tracking was found.
- **Licensing:** Mac App Store receipts, Setapp, and AquaticPrime-signed licence files for the direct build. A 15-day trial, then a free mode where some actions need Pro (`isProRequired`). Beta builds stop working after a set date.
- **Storage:** Realm database, with migrators for fonts, tags, preferences and writable locations.

**For Fontface:** Fontface's "never turns fonts off without a subscription" promise holds against this model. Its no-tracking, local-first stance is already stronger. If Fontface ever goes to the Mac App Store, the sandbox and bookmark design is the template to plan for, since auto-activation then needs a separate helper.

---

## Suggested backlog rows for Fontface

1. **Auto-activation, system route:** CoreText requests, PostScript/full-name match, temporary activations with one clear action, WebKit/Calibri skip. (Phase 4)
2. **Import from FontExplorer X, Suitcase / Connect Fonts, RightFont and FontBase.** (Phase 4)
3. **Measured classification filters** (x-height ratio, weight, width) from `OS/2`. (Phase 2)
4. **Copy as CSS** for variation settings and colour palettes. (Phase 3)
5. **Duplicate precision and "prevent new duplicates".** (Phase 3)
6. **Google sync options:** variable/static preference and a disk-space estimate. (Google Fonts)
7. **Font switching in documents.** Optional, needs per-app scripting. (Phase 4)

## How to repeat this

REA and Ghidra are set up on the Work MBP (`~/.claude/settings.json` holds `GHIDRA_INSTALL_DIR`, `JAVA_HOME` and two 20-minute time limits). Ghidra needs one architecture, so first make a thin copy:

```bash
lipo /Applications/Typeface.app/Contents/MacOS/Typeface -thin arm64 -output "$TMPDIR/Typeface-arm64"
```

Opening it takes about 9 minutes. The Swift source paths (`strings -a` on the binary, then `grep '\.swift$'`) are the fastest map. Ghidra can't link Swift strings to code, so read strings near a source path for context.
