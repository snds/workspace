# SESSION-STATE — Unicron (+ DSA)

_Last updated: 2026-10-15 — 0.1.0 released; PRs #2 and #3 ready for Sean (checkpoint)_

---

## Current state (rewritten atomically — no stale fields)

### 🤝 Live handoff (the baton)

- **TL;DR (for future agent)**: Unicron is the shared design system for Mailbird, Synapse, and Lockdown. DSA (`snds/dsa`) is its analytics sibling: pattern-candidate detection, adoption metrics, ratchet. Both repos were created by Sean on 2026-10-15 and are being scaffolded.
- **Current focus**: both repos live. DSA `cc4cb05`: `@snds/dsa` 0.1.0, 44 tests, CLI `scan`/`patterns`/`ratchet`, JSON schemas, pattern catalog and family map as data. Unicron `5d16479`+: tokens (40 global, 30 semantic, 9 component), 28 primitives + Icon, playground, docs 01–05, DESIGN.md; `@snds/dsa` installed as a git dependency, first ratchet baseline committed, CI on a frozen lockfile with a hard ratchet.
- **Working set**: `~/Projects/dsa`, `~/Projects/unicron`. Contract used for the build: DSA config shape, suggestion record, tier heuristic (also in DSA's README and `schema/`).
- **Last action**: Shipped 0.5.0/0.3.0 (#17–#24, Version Packages #21). By Claude Fable 5.1 · Claude Code (cloud) · vm, 2026-10-17 18:25 UTC.
- **Federation (D17, Sean 2026-10-15):** contribution open, ownership not. Process written: `docs/06-contributing.md` (unicron `1b1234c`). Tooling in progress: publishable packages with a consumer smoke test, changesets, a release workflow (GitHub Release tarballs always; npm only when `NPM_TOKEN` exists), CODEOWNERS, PR and promotion templates, token lint in CI. Synapse logged D89 (replaces D87) and will move onto Unicron once it is ready. After the tooling lands: send Mailbird the "move off the submodule + promotion PRs" prompt and Synapse the "adopt unicron + dsa" prompt.
- **Identity crate started** (Lockdown D10–D16 green-lit): built by this session on `snds/Mailbird` branch `identity-crate` as `crates/identity` (`ecosystem-identity`), spec §10 steps 1–2, PR to follow; the Mailbird session was told not to duplicate it. Tracked on the Lockdown baton.
- **Next action**: Review Mailbird's 28 candidates and promote the clear ones into unicron (DialogHeader title+description and the icon-button recipe first); consider shipping built output or a publish step so consumers can use a plain dependency instead of a submodule; vendor `shadcn-material` now that it has `--alias-mode package`. Then: DSA Figma adapter (instance nesting → the same suggestion-record schema); Style Dictionary replacing `scripts/build.mjs`; the six security components from Lockdown's brief §5.7; a `shadcn-material` alias-mode flag so the generator can be vendored.
- **Open decisions**: npm publishing (scope `@snds`, `@unicron`); name trademark checks; whether Synapse's D87 ("each project grows its own") is formally reversed in the Synapse repo (Sean acted on D14 by creating unicron, so treat D14 as confirmed by action, but the Synapse log still says D87).
- **Blocked on**: nothing.
- **0.8.0 / tokens 0.6.0 released (#32 + Version Packages #33, 21:19 UTC):** SecretField `multiline` + `name`/`required`/`onBlur`, `secretStrengthFromScore`, `CommandItemAction` (⌘↵), `Command match="keywords"`, `Skeleton variant="row"` (`--c-skeleton-row-height`), Dialog size mapping documented. Known, documented not fixed: cmdk folds an `Icon`'s glyph name into an item's search text when no explicit `value` is given.
- **Contrast misses closed — tokens 0.7.0 / ui 0.8.1 (#34 + Version Packages #35, 21:59 UTC):** the two misses Lockdown measured. `--destructive` → new `red.700` (light) / `red.200` (dark): text on a selected row now Lc 76+ (was 74.1 / 74.5), label on its own tint 75 / 72. Light `--warning` → new `amber.450`: the fill reads Lc 31+ against page, sidebar and a selected row (was 27 on the sidebar), its label 62. `red.600`/`red.300` stay, unchanged. `contrast.mjs`: 119 gated recipes, all pass (adds destructive on selected rows, status fills as solids, red in the accent text table). Synapse is on it (`1c78164`, no app change). Mailbird and Lockdown: plain bump, no code change; destructive text and the light warning fill shift slightly in screenshots. Done by the Synapse session (Claude Opus 5.5 · Claude Code · Work MBP).
- **0.9.0 released (#36 + Version Packages #37, 22:15 UTC):** CodeDisplay gains SecretField's copy reference (`onCopy` → `{ hash }`, `clipboardHolds`, `onClipboardClear(ref)` → boolean); "Cleared" only after a real clear. Lockdown is on it.
- **0.10.0 → 0.12.0 (2026-10-18 00:42–01:28 UTC, from Synapse's UI review):** #38 shadcn's orientation variants (`data-horizontal`/`data-vertical` matched nothing: the line tab's marker, separators and scroll bars drew at zero size) and a hover preview on line tabs; #39 `SheetContent backdrop={false}` for a detail sheet beside a list (0.10.0). #41 `SheetContent size` (the dialog's sizes), the header clear of the close button, wrapping titles, a row footer from `sm` (0.11.0). #43 the rest of shadcn's state variants: cmdk's `data-selected="false"` had drawn every command item highlighted (0.11.1). #45 `CommandItemAction` is a span that takes no focus (axe `nested-interactive`, serious, on every item with an action) and `CommandDialog size` (0.12.0). Tokens unchanged at 0.7.0. Each with tests; CI green; Version Packages #40, #42, #44, #46.
- **In-flight / do-not-touch**: nothing. The four contrast waivers and the hairline question were closed by #27 (control borders now 3:1).
- **Agent thread**: Claude Fable 5.1/Claude Code cloud (2026-10-15): project created, both repos scaffolded; next = verify and wire.

### Environment
- **Context profile**: `personal-solo`
- **Machine**: cloud VM
- **Project root**: `07-projects/29-unicron/` (vault baton); code in `~/Projects/unicron` and `~/Projects/dsa`

### VCS state
- **Repos**: `snds/unicron` and `snds/dsa`, both `main`, both public

---

## Session history (append-only)

_Older entries are in [history/](history/), by month; the app's Projects timeline joins them with this file._

### 2026-10-15 — checkpoint (seeded)

**Focus this session**: scaffold the shared design system and its analytics sibling.
**Machine**: cloud VM
**Accomplishments**: project registered; both repos scaffolded (see repo commits).
**Decisions made**: D14 (shared system, Mailbird as base) confirmed by Sean's action; DSA is the home for all DS detection/analysis/analytics; employer systems may consume DSA later.
**Next resumption needs**: build verification results in each repo's README and CI.
