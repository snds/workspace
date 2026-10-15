# SESSION-STATE — Unicron (+ DSA)

_Last updated: 2026-10-15 — Sean's steps 1, 3, 4 done; Version Packages merged (checkpoint)_

---

## Current state (rewritten atomically — no stale fields)

### 🤝 Live handoff (the baton)

- **TL;DR (for future agent)**: Unicron is the shared design system for Mailbird, Synapse, and Lockdown. DSA (`snds/dsa`) is its analytics sibling: pattern-candidate detection, adoption metrics, ratchet. Both repos were created by Sean on 2026-10-15 and are being scaffolded.
- **Current focus**: both repos live. DSA `cc4cb05`: `@snds/dsa` 0.1.0, 44 tests, CLI `scan`/`patterns`/`ratchet`, JSON schemas, pattern catalog and family map as data. Unicron `5d16479`+: tokens (40 global, 30 semantic, 9 component), 28 primitives + Icon, playground, docs 01–05, DESIGN.md; `@snds/dsa` installed as a git dependency, first ratchet baseline committed, CI on a frozen lockfile with a hard ratchet.
- **Working set**: `~/Projects/dsa`, `~/Projects/unicron`. Contract used for the build: DSA config shape, suggestion record, tier heuristic (also in DSA's README and `schema/`).
- **Mailbird consumption (reported by the Mailbird session, 2026-10-15):** `snds/Mailbird` PR #42 (branch `unicron`, ADR-0047). unicron is a **git submodule** at `vendor/unicron` pinned to main `5a8cf8e`, its packages in the pnpm workspace as `workspace:*` (a `github:` dep failed: packages don't commit build output, and `@unicron/ui → @unicron/tokens` is `workspace:*`). Mailbird's `src/components/ui/*`, `icon.tsx`, `styles/tokens.css` are gone; app roles live in `src/styles/app-extension.css`. One drifted primitive (AdaptiveSheetContent `wide`) went upstream as unicron#1, merged. Proof: 133/133 tokens match light and dark; 15/16 screenshots pixel-identical, the 16th sub-threshold anti-aliasing; 38 browser suites pass. **dsa** pinned to `cc4cb05` (git+https; the sandbox proxy blocks codeload tarballs; lockfile had to be forced to HTTPS). Baseline: 274 className overrides, 2 style, 0 spreads, 2 Button look-alikes. **First real `dsa patterns`: 431 compositions, 28 candidates.** Strongest: icon Button (Fab), DropdownMenuItem with icon, DialogHeader title+description (19× across 18 files), Tooltip-wrapped icon button, NativeSelect, ActionDialog footer. `shadcn-material --alias-mode package` output equals unicron's button.tsx and dialog.tsx byte for byte. Mailbird's next: a DSA cleanup pass with promotion proposals to unicron.
- **Last action**: Wired dsa into unicron (`onlyBuiltDependencies`, lockfile, baseline, CI). First scan: 29 DS components used, 13 className overrides, 0 spread/look-alikes; no pattern candidates yet because the playground is a single host. By Claude Fable 5.1 · Claude Code (cloud) · vm.
- **Federation (D17, Sean 2026-10-15):** contribution open, ownership not. Process written: `docs/06-contributing.md` (unicron `1b1234c`). Tooling in progress: publishable packages with a consumer smoke test, changesets, a release workflow (GitHub Release tarballs always; npm only when `NPM_TOKEN` exists), CODEOWNERS, PR and promotion templates, token lint in CI. Synapse logged D89 (replaces D87) and will move onto Unicron once it is ready. After the tooling lands: send Mailbird the "move off the submodule + promotion PRs" prompt and Synapse the "adopt unicron + dsa" prompt.
- **Federation tooling landed** (unicron `4d46001`): publishable `@unicron/tokens` + `@unicron/ui` (external consumer smoke test builds), changesets, `release.yml` (GitHub Release tarballs always; npm only with `NPM_TOKEN` or `NPM_TRUSTED_PUBLISHING`), CODEOWNERS, PR + promotion templates, `Promoted from:` convention, token lint (two literal violations fixed), CI runs `lint:tokens` and a pack dry-run. First Release run failed only on the repo setting "Actions may create PRs" (Sean's step). **Mailbird opened unicron PR #2** (IconButton, pill/ghost variants, Icon tone, DialogTitle back button, fullscreen sheet; one design call open: solid vs frosted menus). Prompts sent 2026-10-15: Mailbird (changeset + template on #2, move off the submodule after 0.1.0, vendor `shadcn-material`, keep the loop running) and Synapse (adopt after 0.1.0, app-extension layer, dsa wiring, persona-wall pattern upstream, D90+).
- **Sean's answers (2026-10-15):** (1) Actions-may-create-PRs: done. (2) Branch protection: Sean will set it. (3) Version Packages PR #4 merged by this session on Sean's "go ahead" (squash `41cd41e`); release run then tags `@unicron/tokens@0.1.0` and `@unicron/ui@0.1.0` and attaches tarballs. (4) **Menus stay frosted glass by default** (posted on PR #2; a `solid` option only if a second consumer repeats the override). (5) npm: later. Also open: PR #3 from Mailbird vendors `shadcn-material` into `tools/`; PR #2 still needs a changeset and the template sections. Both wait for Sean's code-owner review.
- **Identity crate started** (Lockdown D10–D16 green-lit): built by this session on `snds/Mailbird` branch `identity-crate` as `crates/identity` (`ecosystem-identity`), spec §10 steps 1–2, PR to follow; the Mailbird session was told not to duplicate it. Tracked on the Lockdown baton.
- **Next action**: Review Mailbird's 28 candidates and promote the clear ones into unicron (DialogHeader title+description and the icon-button recipe first); consider shipping built output or a publish step so consumers can use a plain dependency instead of a submodule; vendor `shadcn-material` now that it has `--alias-mode package`. Then: DSA Figma adapter (instance nesting → the same suggestion-record schema); Style Dictionary replacing `scripts/build.mjs`; the six security components from Lockdown's brief §5.7; a `shadcn-material` alias-mode flag so the generator can be vendored.
- **Open decisions**: npm publishing (scope `@snds`, `@unicron`); name trademark checks; whether Synapse's D87 ("each project grows its own") is formally reversed in the Synapse repo (Sean acted on D14 by creating unicron, so treat D14 as confirmed by action, but the Synapse log still says D87).
- **Blocked on**: nothing.
- **In-flight / do-not-touch**: nothing.
- **Agent thread**: Claude Fable 5.1/Claude Code cloud (2026-10-15): project created, both repos scaffolded; next = verify and wire.

### Environment
- **Context profile**: `personal-solo`
- **Machine**: cloud VM
- **Project root**: `07-projects/29-unicron/` (vault baton); code in `~/Projects/unicron` and `~/Projects/dsa`

### VCS state
- **Repos**: `snds/unicron` and `snds/dsa`, both `main`, both public

---

## Session history (append-only)

### 2026-10-15 — checkpoint (seeded)

**Focus this session**: scaffold the shared design system and its analytics sibling.
**Machine**: cloud VM
**Accomplishments**: project registered; both repos scaffolded (see repo commits).
**Decisions made**: D14 (shared system, Mailbird as base) confirmed by Sean's action; DSA is the home for all DS detection/analysis/analytics; employer systems may consume DSA later.
**Next resumption needs**: build verification results in each repo's README and CI.
