# SESSION-STATE — Fontface (25-fontface)

_Last updated: 2026-10-20 — `main` = `5b46e35` pushed to GitHub (Sean's OK); first CI run; Unicron notice PR snds/unicron#52 open_

## Current state (rewritten atomically — no stale fields)

### 🤝 Live handoff (the baton — any agent reads this FIRST)

- **TL;DR (for future agent)**: Mac font manager replacing Typeface (no subscription). Tauri 2 + React 19, shadcn/ui `base-nova` on Base UI, Tailwind v4, Material Symbols Rounded, IBM Plex. Public repo https://github.com/snds/fontface: `main` = `5b46e35`, pushed 2026-10-20 as `snds` with Sean's OK, in sync with origin. It's Apache-2.0 with CI on macOS. Fontface is moving onto Unicron, Sean's shared design system. See [[07-projects/25-fontface/README|README]].
- **What `main` holds since `a833670`** (details in today's session-history entry): the tooltip trim and monograms (`tooltip-trim`), licence, NOTICE and CI (`phase0`), the pre-push audit's 3 fixes, and the Characters tab's multi-block picker (`claude/char-blocks`) with the 3 fixes its review confirmed. tsc, 440 UI tests and 404 Rust tests pass, and the app is built from `5b46e35`.
- **First CI run:** https://github.com/snds/fontface/actions/runs/39489328758. Typecheck, UI tests and build passed on GitHub; `cargo test` was still running when this was written.
- **Unicron notice PR:** https://github.com/snds/unicron/pull/52 (branch `docs/personal-project-notice`, `d280439`, D1 option A2). A README notice, a new `CONTRIBUTING.md`, and a note in `docs/06-contributing.md`. Docs only, so no changeset. It merges only on Sean's OK. Made in a fresh clone under the session scratchpad, because the local `~/Projects/unicron` checkout is on branch `ui-text-roles`.
- **Local branches, all merged into `main` and kept; cleanup waits for Sean's OK:** `integrate`, `phase0`, `tooltip-trim`, `claude/char-blocks` (worktree `.claude/worktrees/char-blocks`, side session `local_b09f8202`), `claude/tray`, `claude/purchases-optin`, `claude/translucency`, `dc-sidebar`, `dc-toolbar`, `dc-google-rows`, `declutter`, `google-previews`, `library-redesign`.
- **Next action:**
  1. Read the first CI run's result, and fix it if `cargo test` fails on GitHub's runner.
  2. Sean tries the build: the Characters tab picker, tooltips, monograms, System Fonts.
  3. The rest of Phase 0: a dsa baseline, baseline screenshots, and the macOS backdrop measurement.
  4. With Sean's OK, clean up the merged branches and the char-blocks worktree, and archive the finished side sessions.
- **Plan:** [[07-projects/25-fontface/notes/unicron-migration-plan_2026-10-20|Unicron migration plan]]: 109 items in 9 groups, phases 0–5, Unicron releases R1–R3, and the unified transparency spec. Glass contrast scripts: [[07-projects/25-fontface/notes/glass-contrast-scripts_2026-10-20]].
  - **Decided (Sean, 2026-10-20):** D1 keep Unicron public with a "personal project" notice; D2 Fontface is Apache-2.0; D3 each app sets its font through a token, so Fontface keeps Plex; D6 Fontface takes Unicron's cooler greys.
  - **Open:** D4, D5 and D7–D12, each gated to a phase in the plan.
- **Rules in force (details in [history/2026-10.md](history/2026-10.md)):**
  - Typeface's binary may inform Fontface. No Typeface code is copied, and binary-derived detail stays in the workspace, never in the public repo or Unicron.
  - No competitor names in app text. Source icons are brand-free monograms: no Google, Adobe, Apple or Windows logos.
  - Tooltips only label controls that have no visible label: the label, plus a shortcut if there is one. No sentences.
  - View and preview settings are app-wide, search included. Only section-specific controls stay per section.
  - Importers may read other font managers' sorting data, read-only, never their font files.
- **Not yet checked in the running app:** most work since the library redesign. Agents can't launch it; Sean opens `src-tauri/target/release/bundle/macos/Fontface.app`.
- **Backlog, not started:**
  - Measured kinds (Sans, Serif, Script, Mono, Slab…) as filters and as read-only Built-in tags.
  - Importers for FontBase, FontExplorer X and Suitcase/Connect; narrow `docs/INTEGRATIONS.md` (~:367, ~:427) to match.
  - The auto-activation MVP, after real results from the listen-and-log test (`docs/AUTO-ACTIVATION-TEST.md`).
  - Menu bar app: a single-instance guard for Windows.
  - Vendor accounts: ON HOLD ([[07-projects/25-fontface/notes/vendor-accounts-design_2026-10-18]]).
  - Purchases follow-ups: Replace offer, 30-day trial reminder, "License transferred".
- **Open decisions**: Unicron D4, D5, D7–D12; whether to import the 7 tags only the Apr 2025 Typeface export has.
- **Blocked on**: Sean's OK to merge and to push.
- **In-flight / do-not-touch**: `.claude/worktrees/char-blocks` (side session `local_b09f8202`).
- **Lessons that still bite:**
  - Every `Fontface.app` copy shares the bundle id `design.snds.fontface`. Spotlight or the Dock can open an old copy left in a worktree, so remove merged worktrees.
  - Claude's gh config has drifted to the Centric account before. Push to `snds/*` only as `snds`, and don't `gh auth logout` the Centric account.
  - Agents never write Sean's real library DB; Sean runs that step. Agents never read Adobe Creative Cloud's font files.
- **Last action**: 2026-10-20 — Unicron plan saved; Phase 0 groundwork committed on `phase0`; glass scripts saved; this baton moved its history to [history/2026-10.md](history/2026-10.md). — by Claude Opus · Claude Code · Work MacBook Pro.

### Environment
- **Context profile**: `personal-solo`. `resolve` confirms personal for `~/Projects/fontface` (remote `snds/fontface`).
- **Machine**: Work MacBook Pro (personal project).
- **Project root (code)**: `~/Projects/fontface`. Docs: `docs/ARCHITECTURE.md`, `docs/FEATURES.md`, `docs/TAGS.md`, `docs/INTEGRATIONS.md`.
- **Project root (baton)**: `07-projects/25-fontface/`.
- **Checks**: `npx tsc --noEmit`; `npm run test:ui`; `cargo test` in `src-tauri` (agents use `CARGO_HOME=/tmp/claude-502/cargo-home` with `--offline`); `npx tauri build --bundles app`.

### Active servers and processes
- **Dev server**: not running. **Build**: the app bundle builds.
- **Tests**: 424 UI tests and 404 Rust tests pass on `tooltip-trim`. Ignored tests run on request: the CoreText round trip, the real-DB migration, the live Google test and the live watcher tests.

### VCS state
- **Code repo**: `~/Projects/fontface`, remote `snds/fontface` (public). GitHub `main` = `826c574`; local `main` = `a833670`; branches as listed in the Live handoff.
- **Vault**: tracked in `snds/workspace`; committed at session-end.

---

## Session history (append-only)

_Older entries are in [history/README.md](history/README.md), the long-term tier, by month; the app's Projects timeline joins them with this file._

### 2026-10-20 — merged and pushed: tooltip trim, licence and CI, Characters tab picker

**Sean's OK** (2026-10-20, answering "Which of these should I do now?"): "Merge into main, Push main to GitHub, Unicron notice PR".
**Merged:** local `main` fast-forwarded `a833670` → `5b46e35` with `git update-ref` (via `integrate`):
- `tooltip-trim` `6350609`: `a7fa3f3` Tags always open, the (i) gone, 18px centred divider icons, built-in tags in the tag picker only when on, with a lock; `0db1386` and `7b77a40` the tooltip trim (204 `<Tip>` wrappers → 66, label only; `TipItem`, `disabledReason` and descriptions gone; `CutShort`); `6350609` the `Monogram` source icons and "System Fonts".
- `phase0` `729e568`: Apache-2.0 `LICENSE`, `NOTICE`, `.github/workflows/ci.yml` (macOS: npm ci, typecheck, test:ui, build, cargo test --locked), licence fields, README Licence section.
- `5100ad1`, the pre-push audit's fixes (workflow `wf_4c1b7c01-019`, read-only over `826c574..phase0`: no binary-derived detail, competitor names in app text, `/Users/...` paths, employer content or secrets): `docs/FEATURES.md:4` reads "Fontface contains no code, binaries or other files from Typeface"; ", as Typeface does" removed from `docs/FEATURES.md:131`; shadcn/ui's MIT text in `LICENSES/shadcn-ui.txt`, linked from `NOTICE`.
- `ff405e5` merges `claude/char-blocks` `17b3c0d` (side session `local_b09f8202`): the Characters tab picks any number of Unicode blocks, shown as collapsible groups. The one conflict, in `src/components/CharacterGrid.tsx`, kept the branch's grouped grid and reapplied the tooltip trim ("Copy U+00DF · germandbls"); `BlockSelect`'s Clear tooltip lost the `describe` prop the trimmed `Tip` no longer has.
- `5b46e35`, the 3 fixes its review confirmed (workflow `wf_790e38a6-6a1`, 3 lenses, 2 skeptics per finding; 5 other findings refuted): tick boxes in the block list now fill (`group-data-[selected]/item:`, because shadcn's `data-selected` variant matches only `"true"` and Base UI writes `""`; plan item P17); the trigger's hover colours apply only while enabled (dark mode's hover won over the disabled reset); every group's `CellTip` shares one last-close time (`cellTipClosedAt`), so the next group's tooltip opens at once.
**Checks:** tsc, 440 UI tests, 404 Rust tests, `npm run build`, and the app bundle.
**Pushed:** `git push origin main` (`826c574..5b46e35`, 83 commits). `gh_route.py which` confirmed `github.com/snds -> snds` first, and a `--dry-run` push passed.
**Lessons:**
- Inside the agent sandbox, `gh auth status` reports "The token in keyring is invalid" and `gh` API calls fail with "x509: OSStatus -26276". The sandbox blocks the keychain and certificate checks, and the token is fine. Git over HTTPS works in the sandbox through `git-credential-ws` (pass `allowed_domains` github.com). Public API reads work with plain `curl`. `gh pr create` needs the sandbox off, run through `gh_route.py gh …`.
- The workspace wall guard denied a compound command that began `cd "$D" && … git commit` (rule P31, employer default branch): it couldn't resolve the folder from a shell variable. The same commit, run as `git -C <absolute path> commit` on the feature branch, was allowed.
**By**: Claude Opus · Claude Code · Work MacBook Pro.

### 2026-10-20 — baton housekeeping

**What**: this file was 44 KB, over the 12 KB limit (D98). Every dated entry and the 2026-10-13 Live handoff moved word for word to [history/2026-10.md](history/2026-10.md), and the Live handoff was rewritten for today.
**By**: Claude Opus · Claude Code · Work MacBook Pro.
