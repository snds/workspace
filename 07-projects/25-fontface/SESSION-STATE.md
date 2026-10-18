# SESSION-STATE — Fontface (25-fontface)

_Last updated: 2026-10-14 — renumbered 24 → 25; `main` = `826c574` public on `snds/fontface`; next is Sean's on-screen check of the build_

---

## Current state (rewritten atomically — no stale fields)

### 🤝 Live handoff (the baton — any agent reads this FIRST)

- **TL;DR (for future agent)**: Clean-room Mac font manager replacing Typeface (no subscription). Tauri 2 + React. Phase 1 is built, the scan fixes from the first user test landed, and everything since (views + Google Fonts, settings and title bar, tags, Purchases, preview profiles, Google icon fonts) is merged on `main` = `826c574`, public on GitHub (checked 2026-10-14: only `main`, in sync with origin). See [[07-projects/25-fontface/README|README]].
- **Published 2026-10-13: https://github.com/snds/fontface (PUBLIC), `main` = `c71009c`.**
  - **Created and pushed as `snds`**, after Sean switched Claude's gh config back to `snds`. It had `sean-sands-centric` active, against the credential-scoping rule.
  - **History was rewritten before publishing.** One test line named the employer's OneDrive folder. It's now a generic work/school OneDrive check that skips `/CloudStorage/OneDrive-*` except `OneDrive-Personal`.
  - **Old SHAs no longer exist.** Every commit SHA from the first commit on differs from the ones in older notes; for example, the old `4b4e625` is now `c71009c`. The local backups (tag and `refs/original`) were deleted after the push.
  - **Public-repo scan:** no secrets, no personal email, no `/Users/...` paths. It still mentions Sean's folder names (`04-Creative/05-Fonts`) as examples in docs and tests, plus Typeface's public bundle id.
  - **Don't** `gh auth logout` the Centric account from `gh-claude`: the keyring token may be shared with the device-default gh config.
- **Second rewrite, pushed 2026-10-13: `main` = `826c574` on GitHub.**
  - **What changed:** Sean's folder names were made generic in every commit (`Creative/Fonts` → `Design/Fonts`, `04-Creative/05-Fonts` → `Archive/Fonts`).
  - **How it went out:** force-pushed as `snds` with `--force-with-lease`. The local backups are deleted.
  - **Lesson 1:** Claude's `gh-claude/hosts.yml` had drifted from the dist master. `sean-sands-centric` was added and set active, and it flipped back about 15 minutes after a manual `gh auth switch`. Restoring the file with the installer fixed it, and the result matches dist. ~~Run it with `/bin/bash`: `workspace-doctor.sh` has no execute bit~~ — stale: the execute bit was fixed in `c59bbbe` (2026-10-14).
  - **Lesson 2:** something writes Centric into Claude's gh config, probably a session doing employer gh work without `env -u GH_CONFIG_DIR`. It's worth hardening the workspace against this.
- **`4b4e625` (pre-rewrite): icon fonts with plain letters (Material Symbols, Google Symbols) preview as icons. `PREVIEW_REV` = 3.**
- **`565444e` (2026-10-13): Google icon fonts added on top of `ccf6cd1`.**
  - **Sources:** Material Icons in five styles and Material Symbols Outlined, Rounded and Sharp (variable), all from google/material-design-icons. The table is in `src-tauri/src/services/google/icons.rs`. The license is Apache 2.0, saved as LICENSE.txt.
  - **Duplicate hidden:** the static "material-symbols" entry duplicates Outlined.
  - **Updates:** decided by each file's ETag (a version tag from the server), checked after the catalog lock with a 5 s budget. Unchanged files are reused through a "not modified" answer.
  - **Two Tone:** draws its colour palette correctly in dark mode.
  - **Checks:** 251 Rust tests and 35 UI tests pass.
  - **Open:** Material Symbols in the main library list draws its name in letters, not icons. Fixing that needs a library-wide preview rule plus a `PREVIEW_REV` bump.
  - **Housekeeping:** all worktrees and merged branches removed (2026-10-13). Only `main` remains.
- **Preview profiles:**
  - **Code:** `src-tauri/src/preview/` (`face_previews` side table, `PREVIEW_REV`=2, backfill at launch, on-demand reader lanes), plus `src/previewFit.ts`, `previewQueue.ts` and `components/PreviewText.tsx`/`CharacterGrid.tsx`.
  - **Design and evidence:** in the agent scratchpad only. The design is summarised in `docs/ARCHITECTURE.md`.
  - **Whole-library pass, 12,167 faces:** 11,338 name / 44 trim / 56 case / 10 sample19 / 222 script / 159 symbols / 238 expert / 100 partial.
- **Not yet checked on screen:** title bar, settings, tag groups, sync between two Macs, and previews. WKWebView canvas metrics are unverified too. Sean tries the build next.
- **Settings/title bar (2026-10-12)**:
  - **Title bar:** `tauri.macos.conf.json` uses an Overlay title bar with traffic lights at (20, 28). The 52px first row is a drag region, set up in `src/components/TitleBar.tsx`. Double-clicking it follows the macOS AppleActionOnDoubleClick setting through the `title_bar_double_click` command.
  - **App menu:** Fontface ▸ Settings… (⌘,) emits `open-settings`.
  - **Settings storage:** `src-tauri/src/settings.rs`, in the `app_settings` table. The settings screen lives in `src/settings/`.
  - **Activation modes:** "persistent" or "temporary". Temporary uses CoreText session scope, tracked in a `temporary_activations` table. Restore at launch is always, ask or never. There's also "turn off all".
  - **Other settings:**
    - Keep running when the window is closed (macOS hides the window; the Dock reopens it).
    - Open at login (a LaunchAgent in `login_item.rs`).
    - Daily tag backups in `<app data>/Backups`, with rotation (`backups.rs`). Restore can add or replace.
- **Review record:** a build of 3 agents, then a review (24 confirmed) → fixes → recheck. Then a merge review: 4 confirmed, being fixed now. 121 Rust tests pass. tsc is clean and the app builds. Nothing has been checked on screen yet, because the agent sandbox can't launch the app.
- **Typeface tags imported into the real library (2026-10-12)**:
  - **Backups used:** the May 2026 export (`05-Fonts/export-26-05-10-175600.typeface-backup`), then the Oct 1 backup.
  - **Result:** 30 tags and 10,452 tag links. 4,591 styles are tagged. 5,285 links wait for fonts not in the library; nearly all are Google Fonts that Typeface kept in its own hidden folder, so re-run the import after adding them via Google Fonts.
  - **Safety copy:** `~/Library/Application Support/design.snds.fontface/library.before-typeface-import.sqlite3`, the library from before the import, with no tags.
  - **Lesson 1:** macOS blocks Terminal from reading another app's container (`~/Library/Containers/com.criminalbird.typeface`, "Operation not permitted"). Copy the backup out first.
  - **Lesson 2:** the agent sandbox and the auto-mode classifier block agents from writing the real library DB. Sean runs that step himself (the `import_typeface_backups` ignored test with `FONTFACE_APPLY_TO` and `FONTFACE_REAL_LIBRARY=yes`).
  - **Not imported:** the Apr 2025 export has 7 tags the later backups dropped: Designer, Mainstays, Pixel, Global, Icons, Utility and Sci-Fi/Aliens. Whether to import them is Sean's call.
- **Working set**: `~/Projects/fontface`. Docs: `docs/ARCHITECTURE.md`, `docs/FEATURES.md`, `docs/TAGS.md`, `docs/INTEGRATIONS.md`.
- **Last action**: 2026-10-13 — Google icon fonts and icon-font previews (`826c574`) pushed to `snds/fontface` after the two history rewrites; worktrees and merged branches removed. Earlier (2026-10-12): `settings-and-titlebar` merged and the real Typeface import run with Sean. — by Claude Opus · Claude Code · Work MacBook Pro.
- **Purchases watcher (built 2026-10-12)**:
  - Watches `~/Downloads` and any added folders (FSEvents via `notify`). Each top-level zip, folder or font file is one "find".
  - Store detection from the download's source address (`kMDItemWhereFroms`; Windows `Zone.Identifier` planned), or the user picks.
  - License files kept. Web/app/ebook fonts left out. OTF wins over TTF only for the same faces. Trial words flagged. Envato Elements marked subscription-bound.
  - Imports go to `<app data>/Services/Purchases/<Store>/<Family>/` with a `.fontface-purchase.json` sidecar, then turn on in the library.
  - Move detection (dev:inode + stamp), per-folder watch failures with retry on window focus, nested watch folders refused.
  - Unreadable font files are listed on the find, never dropped silently.
  - Lesson: `std::fs::copy` keeps macOS's compression on system fonts, and reading a fresh copy can fail with ENOATTR ("Attribute not found"). Tests copy fixtures as plain bytes.
  - Still open: Replace offer (newer version of an imported download), 30-day trial reminder, "License transferred". Edge cases: an imported folder moved into a subfolder is offered again; loose files of one family land in separate folders; the worker drops its batch if its channel closes; `check_folders` has no single-flight guard.
- **Tags session**: `fontface-tags` (local_4c374988-a9ce-44c1-992d-9a0e73282097) builds tags imported from other font managers, exports in common formats, and folder/tag colors with defaults for cloud and OS locations. Worktree `.claude/worktrees/tags-and-colors-dda0ca`.
- **Review rounds (2026-10-12)**:
  - **Round 1:** 27 confirmed findings.
  - **Round 2:** 21 of those resolved. It also found 24 regressions, all fixed.
  - **Round 3:** 24 of 30 resolved, plus 9 new low/medium issues, all fixed. It found that scan writers starve each other, so they now take turns through a process-wide `SCAN_WRITER` mutex. Lock order is scan write turn, then activation lock, then the DB mutex.
- **Current state of the build:**
  - Grouping is library-wide. A face key is PostScript name + variable + slant, or the file when there's no PostScript name. Copies merge across family names, so "Abaddon" and "Abaddon™" are one face.
  - A family switch turns every face on. Collection-only faces pick a .ttc first.
  - On/off requests are serialized in the UI and marked busy per file path.
  - A font another app turns off mid-session is recorded as off.
  - Previews come from `local()` for installed fonts. Other fonts use a LIFO fetch of 6 that drops rows scrolled away; a cloud file returns 503 and a file over 96 MB returns 413. Collection reads are serialized.
  - 24 Rust tests pass. The real-library migration and the CoreText round trip are both verified.
- **Next action**: Sean tries the build on screen: title bar, settings, tags, tag groups, sync between two Macs, previews, Purchases (the merge-review fixes and the `settings-and-titlebar` merge are done, in `ccf6cd1`). Older items still open: (1) installed fonts disabled in Font Book still show as on; latent, since no font on this Mac is disabled. (2) Turning on every family would register 206 PostScript names twice, almost all a variable font plus its static Regular; macOS accepts this. (3) document.fonts eviction.
- **Open decisions**: (1) add `<repo>/PROJECT.md` and move the README intent block there; ~~(2) when to push to `snds/fontface`~~ — done 2026-10-13 (public).
- **Blocked on**: nothing.
- **In-flight / do-not-touch**: none. The worktrees `.claude/worktrees/tags-and-colors-dda0ca` and `tags-sidebar-ui-81297a` are merged and can be cleaned up.
- **Built 2026-10-12 (views + services)**:
  - Sidebar shows Library (All Fonts, Font Book with the OS folders nested), Services and Folders. An All/Active/Inactive filter sits in the toolbar.
  - Google Fonts works without an API key:
    - The Fontsource catalog is cached for a day, with a back-off after a failure.
    - Full font files come from the google/fonts repo (`METADATA.pb` on raw.githubusercontent.com), and the license file is required.
    - Downloads land in `<app data>/Services/Google Fonts` (folder kind `service`).
    - An install is prepare, then commit, with a backup and rollback. Each family has its own lock.
    - An update turns back on exactly the files that were on before.
  - Adobe Fonts is read-only (detect-only):
    - It lists only fonts Creative Cloud has turned on, read through the core-text descriptors and filtered by the `livetype` path.
    - Guards keep the scanner (including through symlinks), add_folder, previews, activation and reveal away from Creative Cloud's font store, and the database purges any such rows.
    - It hasn't been tested with Creative Cloud installed; CC isn't on this Mac.
  - Plan and research: `docs/INTEGRATIONS.md`.
  - The services review found 35 issues, all fixed. The recheck found 6 more and finished 3 partial fixes; all are fixed.
    - The Adobe purge now runs once at startup (`db::purge_adobe_rows`), never in `db::open`, because writing in `db::open` collided with running scans.
    - Catalog reads no longer wait behind a fetch (`try_lock`).
    - Renamed files count as replacements on update.
    - Install now reports accurate partial results.
    - A shared `ChoiceGroup` radio group works with arrow keys.
  - 32 Rust tests pass, plus the live Google test. The app bundle builds.
- **Next (from INTEGRATIONS.md)**:
  - Font Book: show deactivated fonts and collections.
  - Purchases watcher follow-ups: Replace offer, trial reminder, "License transferred".
  - Open fonts catalog: Fontsource, Noto, Nerd Fonts and open foundries.
  - "Managed by" badges for Monotype Fonts, Connect and Fontstand.
- **Agent thread**: Claude Opus/Claude Code (2026-10-12): chose stack, built Phase 1, ran user test, started scan fix.

### First user test (2026-10-12)

What Sean saw:
1. macOS system font folders were not detected automatically.
2. Adding his Google Drive fonts folder seemed to do nothing. Rescan did nothing. No loading state.

Root cause: the folder holds ~14.8k files (~12k `.otf`/`.ttf`, plus ~1.1k Type 1 `.pfb`/`.pfm`, `.woff`/`.woff2`, `.eot`). All are online-only Google Drive placeholders (dataless files). The scanner read them one at a time (one download at a time), saved only every 200 files, and showed no progress while listing files. Rescan started a second scan.

Sean's follow-up: the folder is set to "Available offline". Finder showed the Drive green check, plus macOS's download pie still in progress. By 10:00 all 15,511 files had downloaded.

Fixes landed (2026-10-12):
- **Scanner.**
  - Discovery runs with progress events.
  - 8 reader threads fail fast on online-only files (`setiopolicy_np` → EDEADLK). 3 detached download threads fetch those files.
  - Commits run on a timer, and the list updates live.
  - Cancel works, and duplicate scans are blocked; a second caller waits for the running scan's result.
  - A read that fails never deletes a font's rows. `skipped_files` stops repeat re-reads and repeat toasts.
  - Dead symlinks and hidden files no longer block cleanup.
  - Files are stored under canonical real paths. A file is skipped when a symlink resolves it into another library folder.
- **Folders.**
  - The macOS font folders are added automatically as `kind='system'`, shown as Installed and always on.
  - A user folder can't swallow them.
- **On/off state.**
  - The OS's view comes from `CTFontManagerCopyAvailableFontURLs`, canonicalized. CoreText returns paths with symlinks resolved, `/private` dropped, and NFD names.
  - Every result is checked against the OS. A session-scope unregister is the fallback when another app still has the font on.
  - A global activation lock serializes all changes.
  - Reconcile runs at launch, and only for files that were unreachable at that point.
- **Database.**
  - DB v3 uses AUTOINCREMENT, so ids are never reused.
  - Found during testing: bundled SQLite turns foreign keys ON by default, so the migration has to turn them off, or dropping `folders` deletes every font.
  - All commands run async, off the main thread.
- **UI.**
  - Previews are keyed by file version. Installed fonts preview through `local()`, with at most 6 loads at once.
  - Duplicate copies are grouped per PostScript name: turning a font on registers one copy, turning it off covers all copies.
  - The list refreshes when the window regains focus and keeps its scroll position.
  - Keyboard access and screen-reader announcements are handled.
- **Format probe (macOS 27.0.1).** CoreText can activate WOFF, WOFF2, OTC and `.dfont` (FOND). It can't activate any Type 1 font (.pfb/.pfm/LWFN) or .eot.

Deferred: installed fonts that are disabled in Font Book (they still show as on). document.fonts eviction. WOFF/WOFF2/.dfont metadata parsing.

### Environment
- **Context profile**: `personal-solo`. `resolve` confirms personal for `~/Projects/fontface` (remote `snds/fontface`). Lesson: an agent can't see a new `~/Projects` folder as personal until Sean runs `09-tools/profile_resolve.py scan` in a plain terminal, because agents read classification from the cache only.
- **Machine**: Work MacBook Pro (personal project).
- **Project root (code)**: `~/Projects/fontface`
- **Project root (baton)**: `07-projects/25-fontface/` (was `24-fontface` until 2026-10-14; see history)

### Active servers and processes
- **Dev server**: not running. **Build**: app bundle builds.
- **Tests**: Rust — 45 pass, 5 ignored. Ignored tests run on request: the CoreText round trip, `real_db_migrates_without_loss` (FONTFACE_DB_COPY), the live Google test and two live watcher tests (FSEvents doesn't work inside the agent sandbox). TypeScript typecheck is clean.

### VCS state
- **Code repo**: `~/Projects/fontface`, remote `snds/fontface` (not pushed yet). `main` = `04fd9db` (Phase 1, views, Google/Adobe). `purchases-watcher` = `5c8c728`. `claude/tags-and-colors-dda0ca` = tags session's branch.
- **Vault**: tracked in `snds/workspace`; committed at session-end.

---

## Session history (append-only)

_Older entries are in [history/](history/), by month; the app's Projects timeline joins them with this file._

### 2026-10-14 — renumbered 24 → 25; baton now git-tracked

**Why**: Mailbird reached GitHub first as `24-mailbird` (2026-10-13), and this folder had never been committed, so both projects held 24. Sean chose: Mailbird keeps 24, Fontface moves to 25. Same rule as 22 (whoever reaches GitHub first keeps the number).
**Also**: `.gitignore` had no allow-entry for this folder, so the baton existed only on the Work MBP. Sean approved tracking it like 21–24.
**By**: Claude Opus · Claude Code · Work MacBook Pro.

### 2026-10-12 — checkpoint

**Focus**: Decide the stack, build Phase 1, run the first user test, record the project.
**Machine**: Work MacBook Pro

**Decisions made**:
- Tauri 2; Mac first; Windows designed for, not built.
- shadcn/ui (Base UI, Tailwind v4), Material Symbols Rounded, IBM Plex Sans + Mono.
- CoreText persistent user-scope activation, per file; nothing copied into `~/Library/Fonts`.
- Clean-room: no Typeface code or binaries; parity against its public feature list only.

**Next resumption needs**: finish the scan fix list; retest on the Drive folder; settle the repo move + git.
