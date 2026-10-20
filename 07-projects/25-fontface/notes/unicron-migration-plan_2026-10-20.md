---
title: Fontface → Unicron: what moves, how to migrate, and one transparency system
type: note
project: 25-fontface
created: 2026-10-20
status: plan, decisions D1–D12 open for Sean
source: read-only research workflow wf_2466c56a-c4f (four readers, a planner, a completeness critic and a revision) in the Fontface Claude Code session. Nothing in any repo was changed.
---

# Fontface → Unicron: what moves, how to migrate, and one transparency system

_Read-only research, 2026-10-20. Nothing in any repo was changed._

**Path key** (used in every citation)
- `FF/` is the Fontface snapshot at `/tmp/claude-502/fontface-snapshot-a7fa3f3/`, commit `a7fa3f3`. That commit is on branch `tooltip-trim`. It is not in `main` yet.
- `FFLIVE/` is `/Users/sean.sands/Projects/fontface/`.
  - It is on branch `tooltip-trim` at `6350609`, "Sources: brand-free monograms for Google and Adobe; 'System Fonts' everywhere".
  - The working tree is clean (`git status`, 2026-10-20).
  - Local `main` is at `a833670`. GitHub's `origin/main` is at `826c574`.
- `UC/` is `/Users/sean.sands/Projects/unicron/`. The local clone is on branch `icon-webkit-anchor` at `9fd04e2`.
- `SY/` is `/Users/sean.sands/Projects/synapse/app/`.
- `WS/` is `/Users/sean.sands/Projects/workspace/07-projects/25-fontface/`. Its line numbers are as of 2026-10-20, and the file is still being edited.
- `gh:lockdown/` and `gh:Mailbird/` are the public GitHub repos `snds/lockdown` and `snds/Mailbird`, branch `main`. Neither is on this Mac.
- `CARGO/` is `/Users/sean.sands/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/`, the local copy of Tauri's source.

**Public-text rule.** This plan is for Sean, so it cites private paths. Some parts of it will become public text:
- §3.5 to §3.8 go into `UC/docs/04-patterns.md`, `07-content.md`, `08-accessibility.md` and `09-icons.md`.
- §5 goes into `UC/docs/specs/translucent-window.md`.

Before any of that goes public:
- remove `SY/…` paths, because Synapse is private;
- remove `WS/…`, `/Users/sean.sands/…` and `/private/tmp/…` paths;
- paraphrase workspace rules instead of linking to them.

Fontface's public-repo scan already rejects `/Users/...` paths (`WS/SESSION-STATE.md:235`).

---

## 1. Summary

- **Recommendation:** move Fontface onto Unicron in six phases, numbered 0 to 5:
  - make the decisions, audit Fontface's unpushed work, then push it;
  - send the generic pieces up to Unicron in three batched releases (R1, R2 and R3);
  - switch Fontface over one layer at a time: tokens, then primitives, then shared components;
  - clean up.
- **Unicron is public on GitHub today, not private.** The GitHub API (2026-10-20, without logging in) reports `snds/unicron` as public under Apache-2.0, and `UC/README.md:4` agrees.
  - Lockdown and Mailbird are public too. Only Synapse is private.
  - You may have been thinking of Synapse. Its CI notes the extra cost of a private repo (`/Users/sean.sands/Projects/synapse/.github/workflows/ci.yml:1-2`).
  - **Please tell me what "private" means to you.**
    - If you want control, keep Unicron public and add a "personal project, not accepting outside PRs" notice (option A2).
    - If you want secrecy, publish to npm first (option B). Even then, little stays hidden.
- **The monograms (option B) are built.** Fontface commit `6350609` added a `Monogram` component: "G" and "A" in a rounded square, drawn in IBM Plex Sans (`FFLIVE/src/components/Monogram.tsx`).
  - The same commit renamed the system source "System Fonts", with a computer icon for each OS (`FFLIVE/src/library.ts:191-198`).
  - It also deleted `BrandIcon` and `docs/THIRD-PARTY.md`.
  - Monogram is the first new component to go up to Unicron (PR 1g, in R1). §3.8 has the spec.
- **109 items move, in 9 groups (§3).** The transparency system comes on top of that (§5).
- **Transparency becomes one Unicron system.** It has these parts:
  - one setting: Off, Sidebar or Whole window;
  - one decision table that every platform shares, with a reason code for each time the window is forced solid;
  - one CSS contract: `data-translucent` on `<html>`, `data-surface` on each area, a new `pane` colour role, and tokens for the frosted menus and the dimmed backdrop behind dialogs;
  - one small adapter per destination;
  - one platform-notes table, covering Tauri, Electron, the web, SwiftUI and AppKit, WinUI, Compose and Figma, so the system holds wherever an app ends up.

  All your desktop apps ship on Tauri 2, so the shared Rust plugin comes first.
- **The biggest decisions:**
  - D1: Unicron public or private.
  - D2: Fontface's licence.
  - D3: one font for every app, or one per app.
  - D4: which contrast rule glass must pass. Under Unicron's APCA rule (APCA is a newer contrast measure), the light sidebar has to be about 88% solid, unless the real desktop behind it turns out lighter than today's guess.
- **The other apps follow in this order:** Synapse, then Lockdown, then Mailbird.

---

## 2. Decisions to make first

### When each decision is needed

| Gate | Decide first | Why |
|---|---|---|
| Before pushing Fontface (Phase 0) | D2 | A public repo should have its licence before more code goes up. |
| Before Unicron release R1 | D1, D3, D7, D9, D11 | They shape PRs 1c, 1d, 1e and 1g, and how apps install Unicron. |
| Before Fontface Phase 2 | D6 | It sets Fontface's new greys. |
| Before release R2 | D8 | It shapes PR 1h. |
| Before release R3 | D4, D5, D10, D12 | They shape PRs 1k, 1l and 1m. |

### D1. How Fontface gets Unicron (public or private)

**What I found:**
- The GitHub API (2026-10-20, without logging in) reports:
  - `snds/unicron`, `snds/lockdown`, `snds/Mailbird` and `snds/dsa`: public, Apache-2.0.
  - `snds/fontface`: public, with no licence.
  - `snds/synapse`: not found, so it is private.
- The workspace notes also say Unicron is public (`/Users/sean.sands/Projects/workspace/07-projects/29-unicron/SESSION-STATE.md:37`).
- Neither package is on npm. Apps install the GitHub Release tarballs (the packaged `.tgz` files attached to each release) by URL:
  - `UC/.github/workflows/release.yml`
  - `SY/package.json:29-30`
  - `gh:lockdown/apps/desktop/package.json:30-31`
  - `gh:Mailbird/apps/web/package.json:32-33`
- **So a private Unicron would break three public builds: Fontface, Lockdown and Mailbird.**

| Option | Can anyone build Fontface without logging in? | Effect on the other apps | Verdict |
|---|---|---|---|
| A. Keep Unicron public and install the release tarballs | Yes | None. It is what they do now. | **Recommended now** |
| A2. Like A, plus a "personal project, not accepting outside PRs" notice in the README and a CONTRIBUTING file | Yes | None | **Recommended** if "private" means control rather than secrecy |
| A3. Stay public and also publish to public npm | Yes | An optional switch. It removes the hand-edited URLs and the drift bug (§6). | **Recommended next** |
| B. Make the repo private and publish the packages to public npm | Yes | All four apps must move to npm versions *before* the repo goes private, and npm provenance in `UC/.github/workflows/release.yml` must be turned off. **It also has three costs.** (1) The npm tarballs ship readable JS and the full DTCG token source (`UC/packages/tokens/package.json` `files`: `dist`, `tokens`, `examples`), so little is hidden. (2) Every `Promoted from:` and PR link in public Lockdown and Mailbird starts returning 404. (3) Actions minutes cost more on a private repo. Synapse ran out of its free minutes in four days (`/Users/sean.sands/Projects/synapse/.github/workflows/ci.yml:1-7`), and the macOS and Windows runners in §5.11 make that worse. crates.io also publishes the Rust plugin's source. | The only workable private route, and it hides little |
| C. GitHub Packages registry | No. It needs a token even to install. | Every app needs `.npmrc` and a token, and a rename to `@snds/*`. | Reject |
| D. Copy the tarballs into Fontface (vendoring) | Yes | None | Fallback only. It hides nothing. |
| E. Git submodule | Only while Unicron is public | None | Reject. `UC/docs/06-contributing.md` calls it the "week-one exception". |

- **Recommendation:** A now, plus A2 if you want control. Then A3.
- **If it must be private,** do it in this order:
  1. Settle the npm scope (`/Users/sean.sands/Projects/workspace/07-projects/29-unicron/SESSION-STATE.md:18`).
  2. Publish to npm.
  3. Move all four apps to npm versions.
  4. Turn off provenance.
  5. Make the repo private.
- **The Rust transparency plugin (§5.6) follows the same choice.** A Cargo git dependency works only while the repo is public. If Unicron goes private, publish the plugin to crates.io.
- **A rule for every promotion PR:** "No employer names, tokens, paths, data, or code in either repo" (`/Users/sean.sands/Projects/workspace/07-projects/29-unicron/README.md:33`). No employer project folders were read or cited for this plan.
- **Start version:** `@unicron/ui` 0.13.1 and `@unicron/tokens` 0.7.0.
  - 0.13.1 is the first version whose icons show in WebKit, which draws Fontface's Mac window (`UC/.changeset/icon-webkit-anchor.md`).
  - Fontface uses npm (`FF/package-lock.json`). List both tarball URLs and add **no** `overrides` entry. Then a version mismatch stops the install, instead of quietly installing the wrong tokens (§6).

### D2. Fontface's licence

- **The gap.** Fontface is public but has no licence.
  - The GitHub API reports `license: null`.
  - There is no LICENSE file at the root of `FFLIVE/` (checked with `ls`, 2026-10-20).
  - Without a licence, people may read the code but may not legally reuse it or build on it.
- **Options:** Apache-2.0 (the same as Unicron, Lockdown, Mailbird and dsa), MIT, or no licence.
- **Recommendation:** Apache-2.0.
  - Commit `6350609` deleted `docs/THIRD-PARTY.md` along with the brand artwork, so the Simple Icons and Tabler credits are already gone.
  - Create a new third-party notice holding Unicron's NOTICE (`UC/NOTICE`) and shadcn/ui's MIT notice, because the built app ships Unicron code.

### D3. One font for all apps, or one per app

**The facts:**
- Unicron always loads Inter (`UC/packages/ui/src/styles/index.css:8`; `UC/packages/tokens/tokens/global.json` `font.sans`).
- Installing `@unicron/ui` also installs `@fontsource-variable/inter`, `next-themes` and `cmdk`. All three are hard dependencies (`UC/packages/ui/package.json` `dependencies`).
- Synapse gave up IBM Plex when it moved to Unicron (`/Users/sean.sands/Projects/synapse/docs/plan/decisions.md:104`, D90).
- Fontface uses IBM Plex Sans and Mono (`FF/src/index.css:4-8,14-16`).
- Monogram is drawn in IBM Plex Sans (`FFLIVE/src/components/Monogram.tsx`).

**Options:**
- (a) Fontface moves to Inter.
- (b) The font becomes an app token. Unicron adds a stylesheet without fonts and documents three app overrides: `--font-sans`, `--font-mono` and a new `--font-mark`.

**Recommendation: (b).**
- It is one small Unicron PR (1e).
- It keeps Fontface's identity.
- It is still the same decision in every app: each app sets its font through a token.
- **`styles/core` drops only the Inter *import*.** The Inter package stays installed until 1.0, but Vite bundles only what is imported, so Fontface never ships Inter. At 1.0, make Inter an optional peer dependency (a package the app installs only if it wants it).

### D4 to D12. The other decisions

| # | Decision | Options | Recommendation | Blocks |
|---|---|---|---|---|
| D4 | Contrast rule for glass | Unicron's APCA floors (Lc 75 for reading text; Lc is APCA's contrast score), or Fontface's WCAG AA (4.5:1 and 7:1) | Measure the real macOS and Windows materials first, then use APCA, Unicron's one rule. Keep the selected row solid in light mode. | PR 1k (R3) |
| D5 | Menus over a see-through window | Solid, as in Fontface (`FF/src/index.css:135`), or frosted, as Unicron decided (`UC/docs/03-components.md:91`) | Keep them frosted, with measured recipes (§5.10). They turn solid under reduced transparency, more contrast or forced colours. They turn solid under `data-translucent` too, but only if a recipe fails. | PR 1k (R3) |
| D6 | Neutral colours | Keep Fontface's grey (hue 0, faint text at 4.7:1), or take Unicron's (hue 260, stronger faint text) (`UC/packages/tokens/tokens/semantic.json`) | Take Unicron's, and accept the slightly cooler look. | Phase 2 |
| D7 | Tooltip rule in Unicron | Adopt Fontface's 2026-10-20 rule everywhere, or keep `IconButton`'s `tooltip` prop for longer text (`UC/packages/ui/src/components/icon-button.tsx:19-20`) | Adopt it everywhere and deprecate long `tooltip` text. An explain (i) button that opens a Popover (RiskTierBadge `explain`) is "directly scoped", so it stays. | PR 1c (R1) |
| D8 | How shortcuts show in tooltips | Menu-style glyphs (`FF/src/tips.ts`) or a `Kbd` chip (Unicron's IconButton) | `Kbd` in tooltips and plain glyphs in menus, both from one shortcut helper (C4). | PR 1h (R2) |
| D9 | The "on" green | An app role (Fontface `--active`; Synapse `--success-*` in `SY/src/app-extension.css`), or a core `success` role | A core `success` role, since two apps already want it. | PR 1d (R1) |
| D10 | Label colours | Fontface's 12 named hues (`FF/src/tags/colors.css:1-40`), or Unicron's 10 hue angles (`UC/packages/tokens/tokens/global.json` `hue`) | A core `label.*` set built from Fontface's 12. Fontface keeps its names as stored keys. | PR 1m (R3 or later) |
| D11 | Name of the monogram component | `Monogram` (what Fontface shipped: `FFLIVE/src/components/Monogram.tsx`) or `Mark` (the name in your 2026-10-20 decision, `WS/SESSION-STATE.md`) | **`Monogram`.** "Mark" clashes twice. Unicron already exports `CrownJewelMark` (`UC/packages/ui/src/components/security/crown-jewel.tsx:83`). Mailbird had a local `Mark` tooltip wrapper, which `IconButton` replaced (`UC/docs/04-patterns.md:55`); delete it when Mailbird upgrades. "Monogram" also says what the thing is. | PR 1g (R1) |
| D12 | Where the Rust transparency plugin lives | The Unicron repo, a separate repo, or each app | The Unicron repo (for example `native/tauri-plugin-translucent/`), with the same licence and its own release tags (§5.6). | PR 1l (R3) |

---

## 3. The change list

**Effort:**
- S: one small PR.
- M: one PR with new tests and docs.
- L: several PRs, or work on more than one OS.

**Status:**
- **new:** Unicron does not have it.
- **differs:** Unicron has something different.
- **already there:** Fontface just switches to Unicron's version.

The "PR" column refers to the Phase 1 PRs in §4.

### 3.1 Tokens (`UC/packages/tokens/tokens/*.json`)

| Item | What it is | Fontface source | Unicron destination | Status | Effort | PR | Notes |
|---|---|---|---|---|---|---|---|
| T1 Neutral and semantic colours | Fontface replaces its stock shadcn grey with Unicron's | `FF/src/index.css:59-128` | `semantic.json`, `global.json` | already there | S | — | D6. The glass tints (§5) and the preview checks must be solved again. |
| T2 Radius scale | Same base (0.625rem) and same multipliers | `FF/src/index.css:50-56,83` | `semantic.json` `$extensions["unicron.theme"].radius` | already there | — | — | — |
| T3 `pane` role | The content surface. It equals the background, and it is the only content surface allowed to go see-through. | `FF/src/index.css:142,172-178` | `semantic.json`; the CORE list in `UC/packages/tokens/scripts/check.mjs:14`; the theme map | new | S | 1d | §5.3 |
| T4 `translucent.*` group | Glass tints, the selected row, glass text steps, `window-background`, worst-case backdrops | `FF/src/index.css:130-190` | `component.json` | new | M | 1k | §5.3. The values are solved again, not copied. |
| T5 `success` role | The "on" green | `FF/src/index.css` `--active`; `FF/src/components/ActivationSwitch.tsx:109`; `FF/src/components/fontPage/InfoTab.tsx:212` | `semantic.json` `success` and `success-foreground`, plus contrast recipes | new | S | 1d | D9 |
| T6 Small and odd text steps | `text-[11px]` is used 32 times in Fontface and 33 times in Synapse. `text-[10px]` and `text-[13px]` are each used twice in Fontface (grep of `FF/src`). | `FF/src/**` | A theme step, for example `text-2xs`. Fold the 10px and 13px uses into existing steps. | new | S | 1d | Needs its own APCA floor, because small text needs more contrast. |
| T7 App font | Fontface uses Plex. Unicron forces Inter. | `FF/src/index.css:4-8,14-16`; `UC/packages/ui/src/styles/index.css:8` | `font.mark` token; `@unicron/ui/styles/core` with no fonts; documented `--font-sans`, `--font-mono`, `--font-mark` | differs | S | 1d, 1e | D3 |
| T8 Label colours | 12 named hues, each 3:1 against background, sidebar and accent; tints of 16% and 22% | `FF/src/tags/colors.css:1-40`; `FF/src-tauri/src/tags/colors.rs` | A new `label.*` group built on `global.json` `hue` | differs (only 10 hue angles exist) | M | 1m | D10. Pairs with C13. Needs glass recipes (§5.10). |
| T9 Icon axes | Fontface sets `fontVariationSettings` inline | `FF/src/components/ui/icon.tsx` | `component.json` `icon` (`--c-icon-*`) | already there | — | — | Comes with the Icon swap (P12). |
| T10 Motion | Fontface uses tw-animate defaults | — | `--g-duration-fast`, `--g-duration-base`, `--g-ease-standard` | already there | — | — | Fontface lacks reduced-motion handling (A11). |
| T11 Native colour export | Rust code and tests copy colours by hand | `FF/src-tauri/src/window.rs:509-515`; `FF/src/previewStyle.ts:143-146`; `FF/src-tauri/src/translucency.rs:406-410`; `FF/src-tauri/src/settings_tests.rs:1052-1061` | `UC/packages/tokens/scripts/build.mjs` writes a resolved sRGB hex value per mode into `dist/tokens.json` | new | M | 1d | Today `dist/tokens.json` holds references, not colours. For example, `--background` is `var(--g-neutral-0)`, and `var(--g-neutral-950)` in dark (`/Users/sean.sands/Projects/synapse/app/node_modules/@unicron/tokens/dist/tokens.json:361-366`; written at `UC/packages/tokens/scripts/build.mjs:148-150`). Unicron's dark background is `#090a0d`, not Fontface's `#0A0A0A`. |
| T12 Desktop sizes | 52px title row, 28px footer rail, 240px sidebar, 64px of space under lists | `FF/src/components/TitleBar.tsx`; `FF/src/components/FooterRail.tsx` (`FOOTER_RAIL_HEIGHT`); `FF/src/App.tsx:1720`; `PREVIEW_BAR_SPACE` | `component.json` `desktop.*` | new | S | 1j | Synapse shares the 52px row (`SY/src/components/TitleBar.tsx`). |
| T13 Chart colours | `--chart-1` to `--chart-5`, never used | `FF/src/index.css` | — | — | S | — | Delete them in Fontface. |
| T14 Layer order | Named stacking levels (z-index) for toast, tooltip, popover and dialog | `FF/src/components/ui/tooltip.tsx:71` hard-codes `z-[1000000000]` | `component.json` `layer.*` | new | S | 1d | Unicron has none. P1 needs it. |

### 3.2 Changes to existing Unicron components (`UC/packages/ui/src/components/`)

| Item | What it is | Fontface source | Unicron destination | Status | Effort | PR | Notes |
|---|---|---|---|---|---|---|---|
| P1 Tooltip fixes | Esc closes the tooltip and still reaches the page. Fixed positioning. Sits above toasts. | `FF/src/components/ui/tooltip.tsx:27-38,68,71`; `FF/src/tips.ts:160-212` | `ui/tooltip.tsx` | differs | S | 1a | Uses T14 rather than a hard-coded z-index. |
| P2 Tooltip timing | 500ms delay, a 400ms window where the next tooltip opens at once, 800ms in list rows | `FF/src/components/Tip.tsx:73-80` | `ui/tooltip.tsx` and `TooltipProvider` defaults | differs | S | 1a | Unicron's provider says delay 0, but no app mounts it, so Base UI's 600ms applies (`SY/node_modules/@base-ui/react/tooltip/utils/constants.d.ts`). |
| P3 IconButton `tooltip` prop | Offers "longer text", which the new rule forbids | `FFLIVE/src/components/Tip.tsx` (header); `WS/SESSION-STATE.md` (2026-10-20 tooltip decision) | `icon-button.tsx:19-20` | differs | S | 1c | D7. Keep the label and the shortcut. Deprecate sentences. |
| P4 Switch | `focusableWhenDisabled`: stays in the Tab order and uses `aria-disabled` | `FF/src/components/ui/switch.tsx:5-26` | `ui/switch.tsx` | new prop | S | 1c | — |
| P5 Tabs | The panel shows an inset focus ring, because it is a Tab stop | `FF/src/components/ui/tabs.tsx:41-53` | `ui/tabs.tsx:83-91` | differs | S | 1a | Accessibility patch |
| P6 Chip | A colour dot and tint; a dashed "partial" state; a "+n" overflow chip | `FF/src/tags/TagChips.tsx` | `chip.tsx` (`color`, `partial`) | differs | S | 1i | Replace the native `title` at lines 22, 57 and 79. |
| P7 Item | A 28px nav-row size with a count slot. Also fixes `default` and `sm` being identical. | `FF/src/components/Sidebar.tsx:63-185`; `FF/src/sidebar.ts:69-94` | `ui/item.tsx:57-58` | differs | S | 1i | — |
| P8 Empty | A quiet variant (one muted line) and large media (40px icons at weight 300) | `FF/src/App.tsx:2086-2175`; `FF/src/components/AdobeFontsPanel.tsx:188-196` | `ui/empty.tsx` | differs | S | 1i | — |
| P9 DropdownMenu | Solid in Fontface, frosted in Unicron (`bg-popover/70` with `backdrop-blur-2xl`) | `FF/src/components/ui/dropdown-menu.tsx`; `FF/src/index.css:135` | `ui/dropdown-menu.tsx:47,141` | differs | S | 1k | D5. Move the hard-coded glass into tokens (§5.3) and add measured recipes. |
| P10 Toaster | Fontface passes the theme as a prop and doesn't use next-themes | `FF/src/components/ui/sonner.tsx` | `ui/sonner.tsx` | differs | S | 1a | Make the next-themes import optional; the theme prop already wins. `next-themes` is still a hard dependency (`UC/packages/ui/package.json`), so it gets installed anyway until 1.0. **Visible differences to accept:** the error icon is `dangerous` (`ui/sonner.tsx:28`) and toasts are `rounded-2xl` (`:44`). |
| P11 Kbd | Show shortcuts through one shared helper | `FF/src/tips.ts:1-155` | `ui/kbd.tsx` | differs | S | 1h | D8, C4 |
| P12 Icon | Fontface draws a `<span>` with `size`, `filled`, `weight`. Unicron draws an SVG with `fill`, `weight`, `grade`, `opticalSize`, `label`, `tone`. | `FF/src/components/ui/icon.tsx` (199 uses) | `icon.tsx` | already there | M (a codemod: a script that rewrites Fontface's code) | — | Needs 0.13.1 or later for the WebKit fix. |
| P13 Dialog | Fontface puts a drag strip inside. Unicron uses `beforeContent` and `--c-dialog-titlebar-inset`. | `FF/src/components/ui/dialog.tsx:53,61` | `ui/dialog.tsx`; `UC/docs/05-consuming.md` §9 | already there | S | — | — |
| P14 Button | Unicron's Button does everything Fontface's does, and more | `FF/src/components/ui/button.tsx` | `ui/button.tsx` | already there | S | — | Review at least 29 `<Button … className=` overrides in Fontface. |
| P15 Badge, Input, Checkbox, ScrollArea, Separator | Stock in both | `FF/src/components/ui/*` | `ui/*` | already there | S | — | **Visible difference to accept:** the Checkbox tick size. Unicron sizes an SVG tick at 3.5 (`ui/checkbox.tsx:22`). Fontface's `[&>svg]` rule doesn't match its `<span>` icon (`FF/src/components/ui/checkbox.tsx:19`). |
| P16 Command action `title` | `CommandItemAction` puts a native `title` on its button. That breaks W4. | — | `ui/command.tsx:317` | differs | S | 1a | Use Tooltip, or rely on the visible shortcut. |
| P17 The `data-selected` trap (added 2026-10-20) | Unicron's `data-selected` variant matches only `[data-selected="true"]` (`ui/styles/index.css:48`, tested in `orientation.test.tsx:28`). That suits cmdk (`ui/command.tsx:235`). But Base UI's Select and Combobox items write `data-selected=""`, so `data-selected:` never matches them. | Fontface's Characters tab tick boxes never filled until `5b46e35` (`FF/src/components/fontPage/BlockSelect.tsx`) | `UC/docs/` (component guidelines), and a DS lint rule | new rule | S | 1a | For Base UI items, write `data-[selected]:` (any value). Keep the variant as it is, because cmdk needs it. |

### 3.3 New primitives

Generate each one with `UC/tools/shadcn-material`, then add Fontface's deliberate changes as variants or props. All of these go in PR 1f.

| Item | What it is | Fontface source | Unicron destination | Status | Effort | Notes |
|---|---|---|---|---|---|---|
| N1 Popover | Used in 4 Fontface files | `FF/src/components/ui/popover.tsx` | `ui/popover.tsx` | new | S | On Unicron's candidate list (`UC/docs/03-components.md:57-60`). Always solid (§5.4). |
| N2 Select | Used in 6 files. Uses the `unfold_more` icon, `alignItemWithTrigger={false}`, and an `sm` size. | `FF/src/components/ui/select.tsx` | `ui/select.tsx` | new | M | Candidate list. Its popup counts as a menu (§5.4). |
| N3 ContextMenu | Used in 13 files. Includes the Shift-F10 and Menu-key opener. | `FF/src/components/ui/context-menu.tsx`; `FF/src/tags/menus.tsx:71-88` | `ui/context-menu.tsx` | new | M | Not on the candidate list. A menu (§5.4). |
| N4 AlertDialog | Used in 6 files. Includes a drag strip. | `FF/src/components/ui/alert-dialog.tsx:51` | `ui/alert-dialog.tsx` with `beforeContent` and the title-bar inset | new | S | Candidate list |
| N5 Slider | Used in 4 files. The description sits on the thumbs; `thumbAlignment="edge"`. | `FF/src/components/ui/slider.tsx:12,46` | `ui/slider.tsx` | new | S | Candidate list |
| N6 Combobox (autocomplete) | Popup on the top side, at most 20rem, hidden when empty | `FF/src/components/ui/autocomplete.tsx` | `ui/combobox.tsx` | new | M | Candidate list. Its popup counts as a menu (§5.4). |
| N7 Toolbar | Base UI Toolbar: one Tab stop, and arrow keys move between items | `FF/src/components/PreviewBar.tsx` | `ui/toolbar.tsx` | new | S | The base for C5 |

### 3.4 New components (Fontface designs to promote)

| Item | What it is | Fontface source | Unicron destination | Status | Effort | PR | Notes |
|---|---|---|---|---|---|---|---|
| C1 Monogram | A brand-free identifier: 1 or 2 letters in a rounded square | `FFLIVE/src/components/Monogram.tsx` (`6350609`), which replaced `FF/src/components/BrandIcon.tsx` | `components/monogram.tsx` | new | S (already built) | 1g | Spec in §3.8. D11. |
| C2 RadioGroup | Radio behaviour with one Tab stop and arrow, Home and End keys. Three looks: segments, chips and cards. Labels keep a fixed width. Skips choices that aren't available. | `FF/src/components/ChoiceGroup.tsx` (11 uses); `FF/src/components/ViewOptions.tsx` (`LayoutSwitch`) | `ui/radio-group.tsx` | new | M | 1h | On the candidate list |
| C3 Tooltip wrapper and CutShort | A tooltip around any control. One shared tooltip per virtual list. Cut-off text shows in full only while it is cut. | `FFLIVE/src/components/Tip.tsx` (`Tip`, `TipHost`, `createTipHandle`, `CutShort`) | `components/tip.tsx` | new | M | 1h | Replaces native `title` (W4) |
| C4 Shortcut helper | Write a shortcut once and get its visible label, its spoken text and `aria-keyshortcuts`. Matches the typed letter, so it works on Dvorak. `keyHandled()`. | `FF/src/tips.ts:1-155`; `FF/src/fontActions.ts:307-309` | `lib/shortcut.ts`, used by Kbd, IconButton and menus | differs (only `command.tsx:254-266` exists) | M | 1h | D8. Ships with `platformWords` (W10). |
| C5 FloatingToolbar | A pill at the bottom of a list. Its panels open from separate popover handles. A button's tooltip hides while its panel is open. It scrolls sideways when the window is narrow. | `FF/src/components/PreviewBar.tsx` (sideways scroll: `:125`) | `components/floating-toolbar.tsx` | new | M | 1m | The bar's contents stay in Fontface. |
| C6 StatusBar and ListFrame | A 28px status line. A frame that holds the list, the bar and the rail, with the bar after the list in Tab order. | `FF/src/components/FooterRail.tsx` | `components/status-bar.tsx` | new | S | 1m | Counts as chrome on glass (§5.4). |
| C7 Desktop module | TitleBar, `useTitleBar`, `dragRegion`, `NO_DRAG`, `DialogDragStrip`, the title-bar double-click (Rust), base CSS so the window never scrolls, a scroll guard, the first-paint theme script, and the theme hook | `FF/src/components/TitleBar.tsx`; `FF/src-tauri/src/window.rs:461-555`; `FF/src/index.css:204-215`; `FF/src/main.tsx:17-22`; `FF/index.html`; `FF/src/settings/theme.ts` | `@unicron/ui/desktop`, `desktop.css`, and a Rust crate (shared with §5) | differs (only `beforeContent` and a docs recipe exist: `UC/docs/05-consuming.md:165-205`) | L | 1j | Synapse copied it. Its `SY/src/components/TitleBar.tsx` says it "moves into Unicron". |
| C8 PageHeader and BackButton | A 52px row: an icon or Back, then the heading (focused when the page opens), then actions. Back is ⌘[ on Mac and Alt+Left on Windows. | `FF/src/components/TitleBar.tsx:150-176`; `FF/src/components/fontPage/PageHeader.tsx:17-34` | `components/page-header.tsx` | new | S | 1j | — |
| C9 Settings parts | SettingsGroup; SettingsRow (label plus one plain line, control on the right); NumberField (saves on blur or Return, Esc undoes); a text field that saves itself after 500ms; ConfirmButton | `FF/src/settings/parts.tsx` | `components/settings.tsx`, `ui/number-field.tsx` | differs (`Field*` and `Item` exist) | M | 1m | Mailbird's settings rows already use `Item` (`UC/docs/04-patterns.md:61`). |
| C10 Selection model | Finder-style selection, keyed by row, so it survives a layout change | `FF/src/selection.ts`; `FF/src/components/library/useSelection.ts` | `lib/selection.ts` plus a hook | new | L | 1m | Ship the pure model first. |
| C11 focusReturn | Gives focus back after a dialog opened from code | `FF/src/focusReturn.ts` | `lib/focus-return.ts` | new | S | 1h | Fills a Base UI gap |
| C12 undoToast | A success toast with Undo for 10 seconds, then "Undone: …" | `FF/src/families/feedback.ts`; `FF/src/tags/drag.tsx:121` | `lib/toast.ts` | new | S | 1h | — |
| C13 Swatch picker | A radio grid. Arrows move by 1 or by 6. Swatches are named, and the default is marked. | `FF/src/tags/ColorSwatches.tsx` | `components/swatch-picker.tsx` | new | S | 1m | Pairs with T8 |
| C14 Menu model | One list of items, shown as a dropdown or as a right-click menu | `FF/src/components/Tip.tsx` (`Kit`, at the end of the file); `FF/src/components/SectionDivider.tsx` (`MenuLines`) | `lib/menu-model.ts` | new | S | 1h | — |
| C15 SectionDivider | A hairline with a centred icon button. It can collapse its section or open a menu. Dragging over a collapsed section opens it after 700ms. | `FF/src/components/SectionDivider.tsx` (drag-hover: `:68`) | Docs now; a component once a second app needs it | new | M | 1m | Separate it from `FF/src/sidebar.ts` first. |
| C16 copyText | Copies to the clipboard, with a fallback | `FF/src/lib/clipboard.ts` | `lib/clipboard.ts` | new | S | 1h | — |
| C17 Transparency runtime, CSS and Tauri plugin | See §5 | §5 | §5 | new | L | 1k, 1l | — |

### 3.5 Patterns and guidelines (docs)

These go into `UC/docs/04-patterns.md` unless noted, in PR 1o.

| Item | What it is | Fontface source | Unicron destination | Status | Effort | Notes |
|---|---|---|---|---|---|---|
| G1 Tooltip rule | Only controls without visible words get a tooltip, and it holds just their name | `FFLIVE/src/components/Tip.tsx` (header); `WS/SESSION-STATE.md` (2026-10-20) | `UC/docs/03-components.md` (Tooltip, IconButton) and 04 | new | S | D7 |
| G2 Sidebar navigation | Rows are 28px with an 18px muted outline icon, and the whole row is the target; `aria-current`. Library always shows counts; other rows show them on hover, focus or selection. A hidden count stays `invisible`, so nothing moves, and screen readers always hear it. Hover actions take the count's place. Use `:focus-visible`, not `:focus-within`. | `FF/src/components/Sidebar.tsx:63-185`; `FF/src/sidebar.ts:69-94`; `FF/docs/ARCHITECTURE.md:682` | 04 | new | S | — |
| G3 Dividers instead of headings | Icon dividers start sections. A "+" add menu sits at the bottom. Right-click and Shift-F10 open the section's menu. Dragging over a collapsed section opens it after 700ms. | `FF/src/components/SectionDivider.tsx` (`:68`); `FF/src/components/Sidebar.tsx:175-195` | 04 | new | S | An exception to "whitespace first" (`UC/DESIGN.md:77-78`) |
| G4 No settings gear | Settings opens from the app menu (⌘, or Ctrl+,) | `FF/docs/ARCHITECTURE.md:675` | 04 | new | S | — |
| G5 App-wide view settings | Layout, grouping, sort, columns, preview, filters and search are shared across sections. Only filters that belong to one section are kept per section. | `WS/SESSION-STATE.md` (2026-10-20) | 04 | new | S | — |
| G6 Page stack and Back | Pages open over a list that stays loaded but can't be used. Back works by button, ⌘[, Alt+Left, the mouse back button, or Esc. A sidebar click closes all pages. | `FF/src/nav.ts`; `FF/src/useNav.ts` | 04 | new | S | — |
| G7 Keyboard model for collections | Lists are listbox, grid or treegrid widgets, with `aria-activedescendant`. Only the active row's controls are in the Tab order. Selection keys work like Finder. Right-click only selects. In table headers, Return sorts and Shift+Left/Right resizes. | `FF/src/components/FontList.tsx`; `FF/src/components/library/FontTiles.tsx`; `FF/src/components/library/FontTable.tsx`; `FF/docs/ARCHITECTURE.md:689` | 04 | new | M | Pairs with C10 |
| G8 Selection bar | "N selected · M styles", the actions, and Clear (Esc), in a `role=region` | `FF/src/components/library/LibraryPane.tsx:522-560` | 04 | new | S | — |
| G9 Undo before confirm | An action you can reverse gets a toast with Undo for 10 seconds. One you can't reverse gets an AlertDialog. | `FF/src/families/feedback.ts`; `FF/src/components/RemoveFontsDialog.tsx` | 04 (Confirmation, `:37`) | differs | S | — |
| G10 Empty states | Full: icon, title, one sentence, one action. Quiet: one line, for filtered views. | `FF/src/App.tsx:2086-2175` | 04 | differs | S | Pairs with P8 |
| G11 Settings screen | Settings open inside the window, and the sidebar becomes the section list. Search covers labels and descriptions. Esc order: clear the search first, leave a field next, then close. | `FF/src/settings/SettingsView.tsx`; `FF/src/settings/SettingsNav.tsx` | 04 | new | S | — |
| G12 Read-only state | Show a lock and the reason, not a greyed-out control | `FF/src/components/ActivationSwitch.tsx` (`LockBadge`) | 04 | new | S | — |
| G13 Single choice vs several | One choice uses a radio group. Several choices use pressed pills. | `FF/src/components/ChoiceGroup.tsx`; `UC/docs/03-components.md:74` | 04 | differs | S | — |
| G14 Desktop shell | The window never scrolls. Text can't be selected except where marked `.selectable`. The 52px first row is the title bar. The native menu mirrors app commands without firing twice. | `FF/src/index.css:204-215`; `FF/src-tauri/src/window.rs:57-460`; `FF/docs/ARCHITECTURE.md:672` | new `UC/docs/specs/desktop-shell.md` | new | M | Pairs with C7 |
| G15 Floating bar and list frame | Lists keep 64px of space under the last row. Toasts sit above the bar and the rail. | `FF/src/components/PreviewBar.tsx`; `FF/src/App.tsx:146-148` | 04 | new | S | — |
| G16 One menu model, two menus | The same items appear in the dropdown and the right-click menu | `FF/src/components/Tip.tsx` (`Kit`) | 04 | new | S | Pairs with C14 |
| G17 Privacy notice where a feature is turned on | Google previews come with a note saying what Google sees. Downloads access is asked for only when Purchases watching is turned on. | `WS/SESSION-STATE.md` (decisions of 2026-10-18; Purchases opt-in, `:167`) | `UC/docs/07-content.md` | new | S | — |
| G18 Toolbar row | The 52px top row is also the drag area. Below 800px, a container query folds the layout switch into View options. | `FF/src/components/Toolbar.tsx:69-96` | 04, plus `desktop-shell.md` | new | S | Pairs with C7 |

### 3.6 Content and copy rules

These go into a new `UC/docs/07-content.md`, in PR 1o. Unicron has no content doc, and its security specs note that a localization hook is still missing (`UC/docs/specs/security/README.md:29`).

| Item | What it is | Fontface source | Unicron destination | Status | Effort | Notes |
|---|---|---|---|---|---|---|
| W1 Voice | Answer first, short sentences, ordinary words | Sean's response-style rule (`/Users/sean.sands/Projects/workspace/04-preferences/user-preferences.md`, Response Style) | 07 | new | S | Paraphrase it in 07. Don't link the workspace file. |
| W2 Tooltip words | The control's name in a few words, sentence case, no full stop. The shortcut is shown separately. | `FFLIVE/src/components/Tip.tsx` (header) | 07 | new | S | — |
| W3 Why a control is greyed out | Say it in visible text near the control, not in a tooltip. The control stays focusable. | `FFLIVE/src/translucency.ts:27-52` | 07 | new | S | — |
| W4 No browser `title` | Use Tip or CutShort instead | The rule is in the Tip header. Breaches: `FF/src/tags/TagChips.tsx:22,57,79`; `FF/src/components/library/FontTiles.tsx:253`; `FF/src/components/library/FontTable.tsx:561,586,599,606`; and in Unicron, `UC/packages/ui/src/components/ui/command.tsx:317` (P16) | 07 | new | S | — |
| W5 Names and logos | (1) No logos. (2) Generic words for the operating system ("System Fonts"). (3) No competitor names (`WS/SESSION-STATE.md:71`). (4) Third-party service names, such as "Google Fonts", only where people need them to recognise the source. | `FFLIVE/src/library.ts:191-198`; `FFLIVE/src/components/Monogram.tsx` | 07 | new | S | One flag: "Mailbird" is a working name (`/Users/sean.sands/Projects/workspace/07-projects/24-mailbird/README.md:2`) and also the name of a real email client. This rule applies to it too. |
| W6 Counts | Every digit, en-US grouping, correct singulars, tabular figures. For example "2,514 families · 11,047 styles". | `FF/src/footerCounts.ts` | 07 | new | S | — |
| W7 Capitals | Title Case for menu items and buttons, with "…" when more input follows. Sentence case for descriptions. | `FF/src/components/Sidebar.tsx` | 07 | new | S | Check Unicron's own strings against it. |
| W8 Confirmations | The title is the question. The action repeats the verb. Say what is kept. | `FF/src/components/RemoveFontsDialog.tsx`; `FF/src/settings/parts.tsx` (ConfirmButton) | 07 | differs | S | — |
| W9 Errors | Start with "Couldn't …" and give the cause as the description | `FF/src/families/feedback.ts` | 07 | new | S | — |
| W10 Platform words | Finder or Explorer, macOS or Windows, ⌘ or Ctrl, all from one place | `FF/src/components/Sidebar.tsx` (`FILE_BROWSER`); `FF/src/places.ts:31`; `FF/src/tips.ts` | 07 for the rule. The `platformWords` helper ships next to C4 in PR 1h. | new | S | — |
| W11 Settings rows | A label plus one plain line | `FF/src/settings/parts.tsx:25` | 07 | new | S | — |
| W12 Empty states | Say why the view is empty, and give the one next step | `FF/src/App.tsx:2086-2175` | 07 | new | S | — |

### 3.7 Accessibility rules

These go into a new `UC/docs/08-accessibility.md`, in PR 1o. A11 is code and goes in PR 1h.

| Item | What it is | Fontface source | Unicron destination | Status | Effort | Notes |
|---|---|---|---|---|---|---|
| A1 Icon-only names | `aria-label` uses the same words as the tooltip | `FFLIVE/src/components/Tip.tsx`; `UC/packages/ui/src/components/icon-button.tsx` | 08 | already there | S | — |
| A2 Focus and Esc | Keyboard focus opens tooltips the way hover does. One Esc closes the tooltip and also does its normal job. | `FF/src/tips.ts:160-212` | 08, plus P1 | differs | S | — |
| A3 Colour is never the only signal | State marks have text. Tags are 3:1. Partial tags are dashed. | `FF/src/components/ActivationSwitch.tsx`; `FF/src/tags/colors.css:1-10`; `FF/src/tags/TagChips.tsx` | 08 | differs | S | — |
| A4 Contrast is tested | Fontface's WCAG tests move to Unicron's APCA-first gate | `FF/src/translucency.test.ts`; `FF/src/previewStyle.test.ts`; `UC/packages/tokens/scripts/contrast.mjs` | 08 | already there in Unicron | M | — |
| A5 Controls stay focusable when greyed out or busy | A greyed-out control that explains itself stays focusable. A busy control keeps focus and sets `aria-busy`. | `FF/src/components/ui/switch.tsx`; `FF/src/components/ActivationSwitch.tsx:98`; `FF/src/tags/ImportDialog.tsx:357` | 08, plus P4 | new | S | — |
| A6 Scrollable panels | They are focusable and show a ring | `FF/src/components/ui/tabs.tsx:41-53` | 08, plus P5 | new | S | — |
| A7 Slider descriptions | The description sits on the thumbs | `FF/src/components/ui/slider.tsx:12,46` | 08, plus N5 | new | S | — |
| A8 Virtual lists | `aria-activedescendant`, focus recovery (`keepFocus`), sr-only row text, live updates at most every 15 seconds | `FF/src/App.tsx:141-142` (`ANNOUNCE_MS`) | 08, plus C10 | new | S | — |
| A9 Reduced transparency, more contrast and forced colours make the window solid | — | §5.8 | 08 | new | S | — |
| A10 Labels keep a fixed width | Nothing shifts when a choice changes | `FF/src/components/ChoiceGroup.tsx`; `FF/src/sidebar.ts` (`countClass`) | 08, plus C2 | new | S | — |
| A11 Reduced motion and forced colours | Fontface handles neither (a grep of `FF/src` found nothing). Unicron has `useReducedMotion` and `useHighContrast`, but only inside the security code. | `UC/packages/ui/src/components/security/copy-countdown.ts:52-54` | Export both hooks from a general path (PR 1h) | differs | S | Fontface must adopt both. |
| A12 Warning for user-chosen colours | When a user picks text and paper colours under 3:1, show a visible warning | `FF/docs/ARCHITECTURE.md:688` | 08 | new | S | The rule moves. Fontface's preview code stays (§3.11). |

### 3.8 Icon rules

These go into a new `UC/docs/09-icons.md`, plus the iconography part of `UC/DESIGN.md`, in PR 1o. I7 and I8 are code.

| Item | What it is | Fontface source | Unicron destination | Status | Effort | Notes |
|---|---|---|---|---|---|---|
| I1 One icon set | Material Symbols Rounded only. Carbon was considered and turned down. | `WS/SESSION-STATE.md` (2026-10-20) | `UC/DESIGN.md:35-39`, 09 | already there | S | — |
| I2 Fill shows state | Outline at rest. Filled when selected, on or pressed. Animate the `FILL` axis. | `FF/src/settings/SettingsNav.tsx:66`; `FF/src/components/Toolbar.tsx:92`; `FF/src/components/ViewOptions.tsx:93`; `FF/src/components/fontPage/InfoTab.tsx:213` | 09 (`UC/DESIGN.md:94-96` mentions it, but not as a usage rule) | differs | S | — |
| I3 Size steps | One list: 14 (dense text), 16 (controls), 18 (nav rows), 20 (Unicron's default), 40 at weight 300 (empty states) | `FF/src/App.tsx:2125,2157`; `FF/src/components/GoogleFontsPanel.tsx:841` | 09; size classes | new | S | Unicron fixes optical size 20 and weight 400 everywhere (`UC/packages/tokens/tokens/component.json` `icon`). Monogram uses the same list. |
| I4 Tone | Muted for navigation and decoration. Colour only when the icon carries data, such as a tag's colour. | `FF/src/tags/TagsSection.tsx:172`; `UC/docs/03-components.md:76` | 09 | differs | S | — |
| I5 Icon-only buttons | Always use IconButton | `UC/packages/ui/src/components/icon-button.tsx` | 09 | already there | S | — |
| I6 When there is no fitting icon | 1) Pick the nearest metaphor, and record it in one shared icon map. 2) For a company, product, account or source, use Monogram: never a logo, and never a second icon library. 3) For a device or OS, use a plain Material Symbol (`desktop_mac`, `desktop_windows`, `computer`). 4) For a true gap, draw a custom glyph on the Material Symbols Rounded grid, and add it to Unicron with a provenance line, never inside one app. | `FF/src/components/BrandIcon.tsx` (deleted in `6350609`); `FFLIVE/src/library.ts:194-198` | 09 | new | S | — |
| I7 Font subsetting | Ship only the glyphs the apps use. Unicron loads the whole `material-symbols/rounded.css` (`UC/packages/ui/src/styles/index.css:9`). `UC/tools/shadcn-material` writes a `.material-symbols.json` starting list. | Fontface uses at least 59 distinct icon names (grep of `FF/src`) | Build step (PR 1n), plus 09 | new | M | — |
| I8 Monogram | The spec below | `FFLIVE/src/components/Monogram.tsx` | `components/monogram.tsx` (PR 1g) | new | S | Same as C1 |

**Monogram spec** (a draft for the Unicron PR. Fontface's version already follows most of it.)
- **Purpose:** to name a company, product, account or source without using its logo.
- **Why not Avatar:** Unicron's Avatar (`UC/packages/ui/src/components/ui/avatar.tsx`) is round, shows an image first, and is meant for people. A source is not a person, and it sits in rows next to square-grid icons. That is the "compose before you create" check (`UC/docs/01-principles.md:29-41`).
- **Anatomy:**
  - It is drawn on the 24-unit Material Symbols grid, so it scales with `size` and lines up with the icons next to it.
  - The square is 16 × 16 units with 3.5-unit corners and a 2-unit stroke, the same stroke as the outlined icons.
  - It uses `currentColor`, with no brand colours.
  - The letter is 11 units tall, weight 600, and its capitals are centred using the font's cap height (`FFLIVE/src/components/Monogram.tsx`).
  - It is filled only when selected (I2). Then the square is solid and the letter is cut out in the surface colour.
- **Content:** letters only.
  - Use 1 letter, taken from the start of the visible name: "G" for Google Fonts, "A" for Adobe Fonts.
  - Use 2 letters only to tell apart two sources that share a first letter.
  - It has no icon content. A device or OS uses a plain Material Symbol: `desktop_mac` on a Mac, `desktop_windows` on Windows, and `computer` on Linux and elsewhere (`FFLIVE/src/library.ts:194-198`).
- **Font:** the `--font-mark` token, which defaults to `var(--font-sans)`. Fontface sets it to IBM Plex Sans (D3). Fontface's code reads `var(--font-sans)` directly today.
- **Sizes:** the I3 list (14, 16, 18, 20, 40).
- **Props:**
  - `letters: string` (1 or 2 characters);
  - `size?`;
  - `fill?: boolean`;
  - `tone?: "default" | "muted"`;
  - `label?: string`. This gives it `role="img"` and an `aria-label`. Leave it out when the visible name sits next to the Monogram. It then gets `aria-hidden="true"` and `focusable="false"`, as Fontface does today.
- **Build it in Fontface with Unicron's prop names now.** Rename `letter` to `letters` and add `fill` (not `filled`). Then the Phase 4 swap is only an import change.
- **Contrast:**
  - The outline must reach 3:1 against the sidebar, on solid and on glass, in both modes. That is Unicron's control-border floor.
  - The filled state needs a letter-on-fill recipe at Lc 60, in both modes, on solid and on glass.
- **Tests:**
  - letters are centred at every size;
  - it renders in WebKit;
  - an axe check passes;
  - the contrast recipes above pass in `UC/packages/tokens/scripts/contrast.mjs`.
- **Uses outside Fontface:**
  - mail accounts in Mailbird;
  - issuer fallbacks in Lockdown's `CodeDisplay` `media` slot.
- **Already fixed:** `FF/src/library.ts:192-193` used to label every non-Windows OS "macOS Fonts", Linux included. "System Fonts" fixed that in `6350609`.

### 3.9 Transparency

See §5.

### 3.10 Unicron consumption and housekeeping

| Item | What it is | Unicron destination | Status | Effort | PR | Notes |
|---|---|---|---|---|---|---|
| H1 npm setup and drift check | A paragraph on installing with npm (no `overrides`), plus `scripts/check-unicron.mjs` in each app | `UC/docs/05-consuming.md` §1 | new | S | 1o | The script is in §6. It also checks the plugin version (§5.6). |
| H2 Ship NOTICE | Add `NOTICE` to `files` in both packages. Today ui ships only `dist`, `README.md` and `LICENSE`. | `UC/packages/ui/package.json`, `UC/packages/tokens/package.json` | new | S | 1b | Apache-2.0 asks for it. A ui and tokens patch. |
| H3 Source maps | They point at `src/` files that aren't shipped | `UC/packages/ui` build | new | S | 1b | Fix them or drop them. A ui patch. |
| H4 Stale docs | The security parts are called "not built yet"; the rule about `--g-*` imports no longer matches the code; the DESIGN.md values are out of date | `UC/docs/01-principles.md:43-57`; `UC/docs/03-components.md:133-134,142`; `UC/DESIGN.md` front matter | differs | S | 1o | — |
| H5 Version policy | Batched releases. A support window of "the latest two minors, or 30 days, whichever is longer". Version 1.0 once Fontface is on Unicron. | `UC/docs/06-contributing.md` (Releasing) | new | S | 1o | — |

### 3.11 What stays in Fontface, and why

Unicron's core turns down anything named after one app's domain (`UC/docs/06-contributing.md`, "What core will decline"). So these stay in Fontface:

- **Font views and logic:**
  - the contents of FontList and ViewOptions;
  - FacePreview, PreviewText, PreviewStyle and CharacterGrid;
  - PreviewOptions (`ColorChoice`, `ContrastNote`);
  - the Compare, Pair and Family groups pages.
- **Sources and tags:** the Google, Adobe and Purchases panels; TagPicker; tag storage; the sync UI; the menu bar app (`tray.rs`).
- **Font activation:** `ActivationSwitch`, `StateControl`, `LockBadge` and `StateMark`. Their general rules go to the docs (G12, A3, A5).
- **Table and tile maths:** `FF/src/components/library/columns.ts` and `tileGrid.ts`.
- **App settings plumbing:**
  - what the native menu contains (`FF/src-tauri/src/window.rs:57-460`);
  - where the translucency setting is stored (`FF/src-tauri/src/settings.rs`);
  - which areas count as "pane".
- **The preview contrast warning code** (`FF/docs/ARCHITECTURE.md:688`). The rule moves as A12.
- **Tag colour names,** which are stored data keys.
- **Anything learned from analysing Typeface.** That detail never goes into a public repo (`WS/SESSION-STATE.md:13,110`). Unicron and Fontface are both public.

---

## 4. Migration plan for Fontface

### Phase 0: Prerequisites

**Entry:** this document.

**Work:**
1. **Decide the gate decisions** (§2, "When each decision is needed"):
   - D2 before pushing;
   - D1, D3, D7, D9 and D11 before R1;
   - D6 before Phase 2.
2. **Merge the tooltip trim and the monograms.** Merge `tooltip-trim` through `6350609` into Fontface `main` (`a833670`). The branch also holds the snapshot commit `a7fa3f3`.
3. **Audit before pushing.** GitHub's `origin/main` is still at `826c574`. Going from there to `6350609` is 78 unpushed commits and 222 changed files (`git rev-list --count` and `git diff --stat`, 2026-10-20).
   - Your rule is that detail taken from the Typeface binary stays in the workspace and out of the public repo (`WS/SESSION-STATE.md:13,110`).
   - The range includes the auto-activation listener (`4166da2`). It answers a gap listed in `WS/notes/typeface-app-analysis_2026-10-19.md` §1.
   - `FFLIVE/docs/FEATURES.md:4` still says "No Typeface code or binaries are used". Decide whether that wording still fits now that the clean-room rule has been dropped.
   - **Gate:** you review the `826c574..6350609` diff against the Typeface notes, and settle the FEATURES.md wording, before anything is pushed.
4. **Add a LICENSE (D2), a third-party notice, and CI to Fontface.** `FFLIVE/` has no `.github/`, so there is no CI today. The CI should run, in order:
   - `npm ci`
   - `npm run typecheck`
   - `npm run test:ui`
   - `npm run build`
   - `cargo test` (in `src-tauri`)
   - later: `check-unicron`, the generated-colours freshness check (Phase 2), and `dsa ratchet`

   The scripts are in `FFLIVE/package.json`.
5. **Push Fontface `main`.** Do this before the first Unicron PR. Each Unicron promotion cites a Fontface commit, so that commit must be visible on GitHub.
6. **Measure before anything moves.** Add dsa (Sean's design-system analytics tool) with the same git pin as Synapse's `SY/package.json` devDependencies. Add a `dsa.config.json` with `localAliases: ["@/components/ui"]`. Write a baseline.
7. **Update the local Unicron clone.** It is on `icon-webkit-anchor` at `9fd04e2`, and GitHub already has 0.13.1.
8. **Monogram is done** (`6350609`). Rename its prop to `letters` and add `fill` (§3.8).
9. **Take baseline screenshots** of these screens, in light and dark, and with each translucency choice (Off, Sidebar, Whole window):
   - Library as Tiles, Rows and Table;
   - a font page;
   - Settings;
   - a dialog;
   - a menu.
10. **Measure the macOS backdrops now,** with today's Fontface build, following the method in §5.10. Windows and Linux follow in Phase 1.
11. **Keep the working files.** Done 2026-10-20: the glass measurement scripts are in [glass-contrast-scripts_2026-10-20.md](glass-contrast-scripts_2026-10-20.md), and this plan is saved here.

**Exit:**
- the decisions are written to `WS/SESSION-STATE.md`;
- the audit is done, and Fontface `main` is pushed with a LICENSE;
- Fontface CI passes;
- the dsa baseline is committed;
- the macOS backdrop numbers are recorded.

**Risk:** low.

### Phase 1: Send pieces up to Unicron

How each PR works:
- Each row is one Unicron PR on a feature branch, with a changeset (Unicron's release-note file). It merges on your OK.
- Each promoted file gets a provenance line: `// Promoted from: fontface · <commit> · DSA <id | none>` (`UC/docs/06-contributing.md:28-58`). The commit must be on GitHub (Phase 0, step 5).
- Every PR follows the employer-content rule (D1).

| PR | Contents | Decisions | Changeset | Release |
|---|---|---|---|---|
| 1a | Fixes: Tooltip and Tabs (P1, P2, P5); next-themes made optional in Toaster (P10); the Command action's `title` (P16) | — | ui patch | R1 |
| 1b | Packaging: NOTICE in `files` (H2); source maps (H3) | — | ui patch + tokens patch | R1 |
| 1c | Switch `focusableWhenDisabled` (P4); long `tooltip` text deprecated (P3) | D7 | ui minor | R1 |
| 1d | Tokens: `pane` (T3), `success` (T5), the small text step and its floor (T6), `font.mark` (T7), sRGB colour export (T11), layer order (T14) | D9 | tokens minor (ui follows) | R1 |
| 1e | Stylesheet without fonts, `@unicron/ui/styles/core` (T7) | D3 | ui minor | R1 |
| 1f | Missing primitives N1–N7 | — | ui minor | R1 |
| 1g | Monogram (C1, I8). It comes after 1d, because it needs `--font-mark`. | D11 | ui minor | R1 |
| 1h | Tooltip wrapper and CutShort, the shortcut helper with `platformWords`, RadioGroup, small helpers, and the motion and contrast hooks (C2–C4, C11, C12, C14, C16, P11, W10, A11) | D8 | ui minor | R2 |
| 1i | Chip, Item and Empty changes (P6–P8) | — | ui minor | R2 |
| 1j | Desktop module and PageHeader (C7, C8, T12, G18), plus the Rust title-bar helper | — | ui minor | R2 |
| 1k | Transparency step 1: tokens, CSS, overlay tokens, contrast recipes including menus (T4, P9), and the spec docs (§5.13). It comes after measuring. | D4, D5 | tokens minor + ui minor | R3 |
| 1l | Transparency step 2: the runtime, the adapters, the Rust plugin and its first crate tag | D12 | ui minor + crate tag | R3 |
| 1m | Bigger components and label colours (C5, C6, C9, C10, C13, C15, T8) | D10 | tokens minor + ui minor | R3 or later |
| 1n | Icon subsetting (I7) | — | ui minor | R3 or later |
| 1o | Docs only (G1–G18, W1–W12, A1–A10, A12, I1–I6, H1, H4, H5) | — | none | any time |

**Releases.** Merge the "Version Packages" PR only at R1, R2 and R3, not after every PR. The other apps then take three bumps instead of fifteen.

**Measuring for 1k.** 1k needs measured backdrops for every OS it ships on. Fontface has never been built for Windows or Linux (`FF/docs/FEATURES.md:221`). There are two ways forward:
- **Preferred:** during Phase 1, build today's Fontface for Windows and Linux and measure Mica and the plain look there. Sean has a Windows PC for this (`/Users/sean.sands/Projects/synapse/.github/workflows/ci.yml:3-4`).
- **Fallback:** ship 1k with macOS values only. Mark the Windows and Linux values "provisional", and make Off their default.

**Entry:** Phase 0 is done, including the push.

**Exit, for each release:**
- Unicron CI passes. It runs typecheck, oxlint, `lint:tokens`, the contrast gate, Vitest, `ds:ratchet` and a pack dry run (`UC/.github/workflows/ci.yml`).
- Each new part shows in `UC/apps/playground` in light and dark.
- A GitHub Release exists with the tarballs attached.
- For R3, the plugin's crate tag exists too.

**Risks:**
- **Churn for the other apps.** `@unicron/ui` went from 0.1.0 to 0.13.1 in 5 days (`UC/packages/ui/CHANGELOG.md`). Batching the releases limits this.
- **Regenerated primitives may differ from Fontface's hand edits.** Bring each edit across as a variant or a prop. Don't copy the file.

**Verify:**
- Unicron CI;
- playground screenshots;
- for 1k, the measurement screenshots (§5.10).

### Phase 2: Fontface takes Unicron's tokens and stylesheet

**Entry:** R1 is released. This phase needs T11 (the resolved colour export) and `styles/core`. D1, D3 and D6 are decided.

**Work:**
1. **Add Unicron as a dependency.**
   - Add both tarball URLs to `package.json`, with no `overrides`.
   - Commit `package-lock.json`.
   - Add `scripts/check-unicron.mjs` (§6).
   - Expect `next-themes`, `cmdk` and the Inter package to come with it, because they are hard dependencies (`UC/packages/ui/package.json`). `styles/core` keeps Inter out of the bundle (D3).
2. **Switch `src/index.css` to Unicron's styles.**
   - Import `@unicron/ui/styles/core`.
   - Remove the imports Unicron already brings: `shadcn/tailwind.css`, Tailwind, tw-animate and Material Symbols (`UC/packages/ui/src/styles/index.css:6-10`).
   - Delete the shadcn colour block (`FF/src/index.css:59-128`) and the `--chart-*` tokens.
3. **Create `src/app-extension.css`** with:
   - the Plex fonts (`--font-sans`, `--font-mono`, `--font-mark`);
   - `--active` pointed at `success`;
   - the tag palette, until 1m ships;
   - Fontface's translucency block, retuned to the new colours, until 1k ships.
4. **Read colours from `@unicron/tokens/dist/tokens.json` instead of copying them.**
   - **TypeScript** reads the file directly. Update:
     - `FF/src/translucency.test.ts`. Its `gray()` parser expects `oklch(L 0 0)`, and Unicron's greys are not neutral grey.
     - `FF/src/previewStyle.ts:143-146`
     - `FF/src/previewStyle.test.ts:125`
   - **Rust** gets a generated file. A script writes `src-tauri/src/theme_colors.rs` from `tokens.json`, and the file is committed. CI checks that it is fresh. That way `cargo test` never needs `node_modules`.
     - The other option is a `build.rs` that reads `node_modules`. Then `npm ci` must always run before `cargo test`.
     - Update `FF/src-tauri/src/window.rs:509-515`, `FF/src-tauri/src/translucency.rs:406-410` and `FF/src-tauri/src/settings_tests.rs:1052-1061`.
5. **Remove `shadcn` from the dependencies.**

**Exit:**
- typecheck, `test:ui`, build and `cargo test` all pass;
- the contrast tests pass with the new colours;
- you approve the look, compared with the Phase 0 screenshots.

**Risks:**
- **The look changes:** a cooler grey and stronger faint text.
- **Glass tints may fail.** They were tuned for the old grey. Retune them, or default the setting to Off until 1k ships (see "Rollback" for how).
- **The window colour in Rust must match the new background.** Dark is `#090a0d`, not `#0A0A0A`. If they differ, the wrong colour flashes at launch.

**Verify:**
- light and dark;
- Off, Sidebar and Whole window on macOS;
- no wrong-colour flash at launch (the inline script at `FFLIVE/index.html:14`).

### Phase 3: Swap the primitives

**Entry:** R1 is released, because this phase needs N1–N7 and P1–P5.

**Work, lowest risk first:**
1. **Simple parts.** Switch Badge, Input, Checkbox, ScrollArea, Separator and Button to `@unicron/ui`.
   - Review the ~29 Button `className` overrides, and turn the repeated ones into Unicron variants.
   - Accept the Checkbox tick size and the toast differences (P10, P15).
2. **Icons.** Run the Icon codemod over all 199 uses:
   - `size={n}` becomes a size class;
   - `filled` becomes `fill`;
   - muted and destructive classes become `tone`.

   Then check that every icon shows in WKWebView, the Mac web view.
3. **Overlays:**
   - Dialog. Pass the drag strip through `beforeContent`, and use `html[data-own-title-bar]` with `--c-dialog-titlebar-inset` (`UC/docs/05-consuming.md` §9).
   - AlertDialog, Popover, DropdownMenu, ContextMenu and Tooltip.
   - Toaster, with the theme passed as a prop.
4. **Form controls:** Switch, Select, Slider, Tabs and Combobox.
5. **Adopt the Unicron parts Fontface doesn't use yet.** A grep of `FF/src` finds 25 raw `<button>` elements and 72 `<Icon … className=` uses. Track both in dsa.
   - icon-only `Button` plus `Tip` → `IconButton` (`UC/packages/ui/src/components/icon-button.tsx`);
   - the preview-bar and Variable toggles → `Toggle` and `ToggleGroup` (`UC/packages/ui/src/components/ui/toggle.tsx`, `toggle-group.tsx`). Today they use `aria-pressed` in `FF/src/components/Toolbar.tsx`, `CharacterGrid.tsx` and `fontPage/SpecimenTab.tsx`;
   - the search field → `InputGroup` (`ui/input-group.tsx`);
   - settings rows → `Field*` (`ui/field.tsx`);
   - busy states → `Spinner` (`ui/spinner.tsx`);
   - loading rows → `Skeleton` (`ui/skeleton.tsx`);
   - FontPicker's list (`FF/src/components/FontPicker.tsx`) → `Command` (`ui/command.tsx`).
6. **Keep the old `src/components/ui/*` files** until Phase 5. Just stop importing them.

**Exit:**
- Nothing imports from `@/components/ui/*` any more, except parts still waiting upstream. Those are generated with `--alias-mode app` (`UC/docs/05-consuming.md` §6).
- dsa shows the local count falling, and the raw `<button>` count falling.

**Risks:**
- icons not showing in WebKit;
- Esc and focus behaviour in overlays;
- frosted menus (D5).

**Verify:**
- typecheck, tests and build;
- a keyboard pass: Tab order, Esc order, Shift-F10, arrow keys in menus;
- VoiceOver spot checks on the sidebar, a dialog, a menu and the tag picker;
- screenshots in light, dark and translucent.

### Phase 4: Shared components, patterns and transparency

**Entry:** R2 for the components. R3 for transparency.

**Work, one component per commit:**
1. Switch to Unicron's `Monogram`, and delete `FFLIVE/src/components/Monogram.tsx`.
2. Replace `Tip`, `TipHost` and `CutShort` with Unicron's tooltip wrapper. Replace the shortcut code in `FF/src/tips.ts` with the shared helper and `platformWords`. Remove the native `title` uses (W4).
3. Replace `ChoiceGroup` with RadioGroup, including in `LayoutSwitch`.
4. Replace `TitleBar.tsx`, the theme start-up code and the desktop base CSS with the desktop module. Add PageHeader.
5. Move the sidebar rows to `Item` with the 28px nav size (P7).
6. Switch these as they ship: settings parts, `focusReturn`, `undoToast`, `copyText`, Chip (for tags), Empty and the swatch picker.
7. Adopt `useReducedMotion` and `useHighContrast` (A11).
8. Transparency: follow the Fontface steps in §5.12.

**Exit:**
- No Fontface component duplicates a Unicron one.
- The dsa ratchet has gone down.
- The tests have moved with the code.

**Risk:** heavily used parts (tooltips, sidebar rows, lists) may break in small ways.

**Verify:**
- everything in Phase 3;
- the §5.10 checks on macOS;
- the first Windows and Linux builds with translucency, in the CI build matrix (§5.11).

### Phase 5: Cleanup

**Work:**
- Delete the local `src/components/ui/*` copies and every replaced component.
- Update `FF/docs/ARCHITECTURE.md`: the front-end part (`:669-675`) and the translucency part (`:568-578`).
- Write a new dsa baseline at the new low.
- Add entries to Unicron's promotion log (`UC/docs/04-patterns.md:51-75`) and to the workspace notes.

**Exit:**
- CI passes;
- there is no `shadcn` dependency;
- `ARCHITECTURE.md` describes Unicron.

### Rollback

- **Each phase is a feature branch** that merges on your OK. To roll back, revert the merge.
- **Unicron is pinned by exact URL, and the lockfile records each file's hash.** Going back a version means changing two URLs and running `npm install`.
- **The old primitives stay on disk until Phase 5,** so any single swap can be undone.
- **Transparency's kill switch must be a settings migration.**
  - Changing `TRANSLUCENCY_BY_DEFAULT` (`FFLIVE/src/translucency.ts:22`; `FF/src-tauri/src/settings.rs:347`) only affects new installs. The default applies only when no settings are stored yet (`FFLIVE/src-tauri/src/settings.rs:312-316`). Anyone whose settings already say `window` keeps it.
  - To turn it off for everyone, add a migration that writes `off`. There is a precedent: Purchases watching was "reset to off for everyone" (`WS/SESSION-STATE.md:167`).
  - After Phase 4, the same migration lives in each app, and `translucencyDefault` in Unicron covers new installs.
- **Never delete or re-upload a Unicron release tarball,** because apps pin those URLs. Fix problems with a new patch release instead.
  - `UC/.github/workflows/release.yml` uploads with `--clobber`, which can overwrite a file.
  - Turning on GitHub's immutable releases would prevent that.

### How Lockdown, Mailbird and Synapse pick up the new pieces

**Each app makes one "bump Unicron" commit per release,** as Synapse already does (Synapse commit `47bd589`):
1. Read the changelog.
2. Edit the URLs (and the plugin tag, from R3 on).
3. Install.
4. Run the drift check, typecheck, build and `ds:ratchet`.
5. Look at the screens in light and dark.
6. Commit.

**Synapse goes first.** It is on 0.13.1 and uses npm.
- Drop its `overrides` entry (`SY/package.json:52-54`).
- Use the desktop module instead of its own `SY/src/components/TitleBar.tsx`.
- Take the tooltip fixes.
- Then add transparency (§5.12).

**Lockdown comes next.** Fix its tokens drift first.
- Three files pin tokens 0.6.0, while ui 0.12.0 asks for 0.7.0:
  - `gh:lockdown/apps/desktop/pnpm-workspace.yaml:11`
  - `gh:lockdown/apps/web/pnpm-workspace.yaml:8`
  - `gh:lockdown/extension/pnpm-workspace.yaml:11`
- Then bump.

**Mailbird goes last.**
- It is on 0.9.0 (`gh:Mailbird/apps/web/package.json:33`). That is outside the support window, which covers 0.12 and 0.13.
- Bump in steps, reading each changelog.
- Delete its old local `Mark` if it is still there.

**Unicron process changes that make this manageable** (H5):
- batched releases;
- a support window of "the latest two minors, or 30 days";
- version 1.0 after Fontface lands;
- one table of which app is on which version (ui, tokens and plugin), kept in `/Users/sean.sands/Projects/workspace/07-projects/29-unicron/`.

---

## 5. One transparency system for every app

### 5.1 Goals

- **One of each:** one setting, one decision table, one CSS contract and one set of tokens, for every app.
- **Each destination answers only three questions:**
  1. What can this OS show?
  2. Does the OS ask for less transparency or more contrast?
  3. Can the window change while it is open?
- **Text keeps Unicron's contrast floors over the worst-case backdrop.**
- **When in doubt, the window is solid.** Solid is always safe.
- **Fontface's stored values and attribute names stay the same,** so it moves over with no data changes.

### 5.2 Words used here

- **Setting:** `off`, `sidebar` or `window`. These are the stored values, unchanged from `FF/src-tauri/src/settings.rs:36-47`.
- **Look:**
  - `blur`: the OS draws a blurred material behind the window.
  - `plain`: see-through with nothing blurred. This is Linux.
- **Surface:**
  - `chrome`: sidebars, rails, tab bars, list panes and status bars.
  - `content`: the main view.
- **Material:** what the OS draws behind the window. Examples are the macOS Sidebar material and Windows 11 Mica.
- **Backdrop:** the worst-case colour behind a surface, used in the contrast test.
- **Reason:** why the window is solid when the setting asks for glass (§5.5).

### 5.3 Tokens (`@unicron/tokens`)

**Tier 2: the role.** Add `pane` to `UC/packages/tokens/tokens/semantic.json`.
- Its value is `{background}` in both modes.
- What it means: "the content area that sits directly on the window. It is the only content surface that may go faintly see-through. `bg-background` always stays solid."
- Add it to the CORE list in `UC/packages/tokens/scripts/check.mjs:14`, and add `--color-pane` to the theme map.
- Mailbird's names `--surface-canvas` and `--surface-chrome` are banned from the core (`check.mjs:22`). `pane` is also Fontface's existing name.

**Tier 3: the `translucent` group.** Add it to `component.json`. In CSS it becomes `--c-translucent-*`. Dark values use the same `$extensions["unicron.modes"].dark` mechanism as `icon.grad`.

These values are starting points from §5.10. Solve them again after measuring the real materials.

| Token | Light | Dark | Notes |
|---|---|---|---|
| `blur-chrome` | `color-mix(in oklab, {neutral.50} 88%, transparent)` | `… {neutral.900} 60%` | Fontface ships 45% and 60% (`FF/src/index.css:141-160`) |
| `plain-chrome` | `… {neutral.50} 96%` | `… {neutral.900} 90%` | Light is nearly solid (§5.14, question 2) |
| `blur-content` | `… {neutral.0} 92%` | `… {neutral.950} 92%` | Passes as shipped |
| `plain-content` | `… {neutral.0} 97%` | `… {neutral.950} 96%` | Passes |
| `selected` | `{neutral.100}` (solid) | `color-mix(in oklab, {neutral.25} 7%, transparent)` | A 7% tint never reaches Lc 75 in light mode |
| `chrome-muted-foreground` | the weakest tier-1 step that passes | same | Needed only if the opacity drops below what plain muted text needs |
| `content-muted-foreground` | `{neutral.600}` | `{neutral.200}` | Today's muted values already pass |
| `window-background` | `{neutral.0}` | `{neutral.950}` | Exported as sRGB hex for the Rust, Swift and Electron shells (T11) |

**Tier 3: the `overlay` group** (new). It holds the glass inside the page, so it can be turned off.

| Token | Value today | Where it is hard-coded now |
|---|---|---|
| `overlay.menu` | `color-mix(in oklab, {popover} 70%, transparent)`, with `backdrop-blur-2xl` | `UC/packages/ui/src/components/ui/dropdown-menu.tsx:47,141` (`bg-popover/70`) |
| `overlay.scrim` | `{black} 10%`, with `backdrop-blur-xs` | `UC/packages/ui/src/components/ui/dialog.tsx:37`; `sheet.tsx:35` (`bg-black/10`) |

Today Unicron's frosted menus ignore `prefers-reduced-transparency`, even with no window glass. With these tokens, the CSS in §5.4 can make them solid.

**Rules:**
- **The worst-case backdrops live in the group's `$extensions["unicron.backdrops"]`:**
  - blur: one measured value per OS material and mode;
  - plain: black under light mode, white under dark mode.
- **A glass token never points at the role it replaces.**
  - Glass tokens point at tier 1. Otherwise `--sidebar` would refer to itself, and CSS treats that loop as invalid.
  - An app that re-points `--sidebar` must also set the matching glass token.
- **The tokens pass Unicron's lint as written.** `color-mix(…, transparent)` over tier-1 references is allowed (`UC/packages/tokens/scripts/lint.mjs`).
- **"Look" is a token group, not a mode.** The builder knows only the `dark` mode (`UC/packages/tokens/scripts/build.mjs:31`).

### 5.4 CSS contract (new `UC/packages/ui/src/styles/translucent.css`)

`styles/index.css` and `styles/core` both import this file.

**Root attributes.** Only the runtime sets these. They keep Fontface's names.
- `data-translucent="blur" | "plain"` is present only while the window is see-through.
- `data-translucent-window` is present for Whole window.
- `data-reduce-transparency` is present whenever the OS asks for less transparency or more contrast, even if the window is solid. It covers OS signals the web view can't see.

**Surface tags.** The app sets these on the root element of each area.
- `data-surface="chrome"` goes on sidebars, rails, tab bars, list panes and status bars. They use `bg-sidebar`, or an app role pointed at `--sidebar`.
- `data-surface="content"` goes on the main view, which uses `bg-pane`.

```css
/* Leave these rules unlayered, so they beat the base layer's solid body (UC/packages/ui/src/styles/index.css:102-104). */
:root[data-translucent] body { background-color: transparent; }
:root[data-translucent="blur"]  { --sidebar: var(--c-translucent-blur-chrome);  --sidebar-accent: var(--c-translucent-selected); }
:root[data-translucent="plain"] { --sidebar: var(--c-translucent-plain-chrome); --sidebar-accent: var(--c-translucent-selected); }
:root[data-translucent="blur"][data-translucent-window]  { --pane: var(--c-translucent-blur-content); }
:root[data-translucent="plain"][data-translucent-window] { --pane: var(--c-translucent-plain-content); }
:root[data-translucent] [data-surface="chrome"] { --muted-foreground: var(--c-translucent-chrome-muted-foreground); }
:root[data-translucent][data-translucent-window] [data-surface="content"] { --muted-foreground: var(--c-translucent-content-muted-foreground); }
@media (forced-colors: active) { :root[data-translucent] body { background-color: Canvas; } }

/* In-page glass turns solid when anyone asks for less transparency or more contrast. */
:root[data-reduce-transparency] { --c-overlay-menu: var(--popover); --c-overlay-scrim-blur: 0px; }
@media (prefers-reduced-transparency: reduce), (prefers-contrast: more), (forced-colors: active) {
  :root { --c-overlay-menu: var(--popover); --c-overlay-scrim-blur: 0px; }
}
```

A browser that doesn't know a media query treats it as not matching. So in that browser, menus stay frosted unless the runtime sets `data-reduce-transparency`.

**This fixes two Fontface problems:**
- **Fontface matches the tags `aside` and `main`** (`FF/src/index.css:184-190`). In Synapse, that rule would miss the real sidebar, which is a `<nav>` (`SY/src/components/Rail.tsx:85`). It would hit solid detail panels instead (`SY/src/components/LibraryView.tsx:110`, `SY/src/components/SkillPage.tsx:111`).
- **Windows High Contrast leaves the body clear today.** In forced-colours mode the browser keeps transparent backgrounds transparent, so the desktop would show behind high-contrast text.

**Every overlay, classified:**

| Surface | Class | On glass |
|---|---|---|
| DropdownMenu, ContextMenu (N3), the Select popup (N2), the Combobox popup (N6) | menu | Frosted (D5), using `overlay.menu` and a measured recipe. Solid under reduced transparency, more contrast or forced colours. |
| Popover (N1), Tooltip, Toast, Dialog, AlertDialog, Sheet, Command palette | solid | Always solid |
| Dialog and Sheet scrim | scrim | Uses `overlay.scrim`. Add a recipe over glass. It is reported, not gated, because no text is read through it. |
| Floating toolbar (C5) and its panels | solid pill over content (`bg-popover`, `FF/src/components/PreviewBar.tsx:125`) | Its border needs 3:1 against glass content |
| Status bar (C6) | chrome | Tag it `data-surface="chrome"`. It uses the chrome recipes. |

**What may be see-through:**
- the page body;
- chrome;
- content, under Whole window only;
- menus, measured over the glass (D5).

**What always stays solid:**
- dialogs, sheets and popovers;
- cards, inputs, toasts and tooltips;
- sticky table headers and pinned columns (`FF/src/components/library/FontTable.tsx:297`);
- the dialog drag strip;
- every security surface: CrownJewel, SecretField reveal, LargeTypeView and ApprovalSheet;
- **any surface whose colours come from users or third parties.** Examples: Mailbird's HTML email bodies, Fontface previews with a custom paper colour, and Lockdown's secrets.

**Rules for apps:**
- The main view uses `bg-pane`, never `bg-background`. dsa can count this.
- **Mailbird must flip its chrome alias.** Unicron's example extension, which follows Mailbird's naming, sets `--sidebar: var(--surface-chrome)` (`UC/packages/tokens/examples/app-extension.css:20-21,36`). With that, the glass never reaches `bg-surface-chrome`. Point `--surface-chrome` at `--sidebar` and `--surface-canvas` at `--pane` instead.

### 5.5 Runtime: `@unicron/ui/translucent`

This is ported from `FF/src/settings/translucent.ts` and `FFLIVE/src/translucency.ts`.

**There is no React provider.** The store is one module, read with `useSyncExternalStore`, so pages without React can use it too.

```ts
export type TranslucencySetting = "off" | "sidebar" | "window"
export type TranslucentLook = "blur" | "plain"
export type Platform = "mac" | "windows" | "linux" | "web" | "ios" | "android"
export type SolidReason =
  | "unsupported"             // this OS or version can't do it
  | "os-reduce-transparency"  // Reduce transparency is on (OS or web view)
  | "os-increase-contrast"    // Increase contrast is on (OS or web view)
  | "forced-colors"           // Windows High Contrast or another forced-colours mode
  | "next-launch"             // chosen, but the window was made solid; shows after a relaunch

export interface TranslucencyState {
  look: TranslucentLook | null // null = solid
  window: boolean              // Whole window: content is see-through too
  reason: SolidReason | null   // why it is solid or greyed out; null when nothing stops it
}
export interface SystemReport {   // what the native side reports (Rust, Electron, Swift)
  version: 1                      // contract version of the command and event JSON
  look: TranslucentLook | null
  reduceTransparency: boolean
  increaseContrast: boolean
  windowReady: boolean
}

export interface TranslucencyAdapter {
  platform: Platform
  get(): Promise<SystemReport>
  subscribe(onChange: (r: SystemReport) => void): () => void
}

export function initTranslucency(o: { adapter: TranslucencyAdapter; storageKey: string; root?: HTMLElement }): () => void
export function getTranslucency(): TranslucencyState
export function subscribeTranslucency(cb: () => void): () => void
export function useTranslucency(): TranslucencyState
export function decide(setting: TranslucencySetting, system: SystemReport, webview: { reduceTransparency: boolean; moreContrast: boolean; forcedColors: boolean }): TranslucencyState // the Rust decide() covers the first two arguments

// Settings row: the copy, with blanks for app words
export interface TranslucencyWords { app: string; content: string; chrome?: string } // e.g. { app: "Fontface", content: "Font lists and pages" }
export function translucencyDefault(platform: Platform, windowsBuild?: number): TranslucencySetting
export function translucencyShown(setting: TranslucencySetting, s: TranslucencyState): TranslucencySetting
export function translucencyDisabledReason(platform: Platform, s: TranslucencyState): string | false // names the right OS setting and its path, from s.reason
export function translucencyDescription(platform: Platform, s: TranslucencyState, w: TranslucencyWords): string
export function translucencyOptions(w?: Pick<TranslucencyWords, "chrome">): readonly { value: TranslucencySetting; label: string }[]

// Adapters, each on its own subpath so web apps don't pull in Tauri
export function tauriAdapter(o?: { command?: string; event?: string }): TranslucencyAdapter // @unicron/ui/translucent/tauri
export function electronAdapter(bridge: { get(): Promise<SystemReport>; onChange(cb: (r: SystemReport) => void): () => void }): TranslucencyAdapter
export function webAdapter(o?: { pageBackdrop?: boolean }): TranslucencyAdapter
```

**What `initTranslucency` does:**
1. It checks the adapter's `version`. If the major version doesn't match, it stays solid and logs why.
2. It merges the adapter's report with what the web view reports:
   - `prefers-reduced-transparency: reduce`, trusted only when `matchMedia(q).media !== "not all"`. WebKit reads an unknown query back as "not all" (`WS/notes/window-translucency-learnings_2026-10-20.md`).
   - `prefers-contrast: more`.
   - `forced-colors: active`.
3. It sets or removes the root attributes, including `data-reduce-transparency`.
4. It writes the first-paint cache. The values are `blur`, `blur+window`, `plain` and `plain+window`, as Fontface uses today (`FF/src/settings/translucent.ts`).
5. It tells the hook.

**First paint** (the script that runs before the page draws):
- **It must check the media queries before applying the cached attributes.** It tests `forced-colors`, `prefers-contrast: more` and `prefers-reduced-transparency` (with the "not all" guard). Otherwise the window flashes see-through at launch for someone who asked for less transparency.
- **How it gets into the page.** Fontface's CSP has no `script-src`, so `default-src 'self'` applies (`FFLIVE/src-tauri/tauri.conf.json:25`). Fontface's inline script works today (`FFLIVE/index.html:14`) only because it is in the built HTML, where Tauri can hash it into the CSP. A function that returns script text at runtime can't be used.
  - **Recommended:** ship a static `first-paint.js` and load it with `<script src="/first-paint.js" data-theme-key="…" data-translucent-key="…">` in `<head>`. `'self'` allows it. It blocks drawing until it runs, and it reads its keys from `document.currentScript.dataset`. The desktop module's theme script shares it.
  - **Alternative:** a Vite plugin that writes the script into `index.html` at build time, so Tauri hashes it.
  - Check each app's CSP when it adopts this.

**Each app keeps its own settings storage.** Fontface keeps SQLite (`FF/src-tauri/src/settings.rs`).

**The setting belongs to one device and never syncs.** That generalises Fontface's rule that settings belong to one computer (`FFLIVE/docs/SYNC.md:25`). It matters for Lockdown and Mailbird, which sync data across devices.

### 5.6 Adapters, one per destination

**Tauri 2 (Fontface, Synapse, Lockdown desktop, Mailbird desktop)**

- **Rust plugin.** Make one plugin crate out of `FF/src-tauri/src/translucency.rs` and `FF/src-tauri/src/window.rs:507-556`.

  ```rust
  pub fn init<R: Runtime>(cfg: Config) -> TauriPlugin<R>      // command plugin:translucent|get; event "translucency-changed"; JSON carries version: 1
  pub struct Config { pub window_label: String /* Fontface hard-codes "main" */, pub background: Rgb2 /* light, dark from tokens.json */ }
  pub fn decide(setting: Setting, system: System) -> State     // same as FF translucency.rs:85-96, plus reason codes
  pub fn effect(os: Os, look: Option<Look>, theme: Theme) -> Option<Effect>
  pub fn has_mica(windows_build: u32) -> bool                  // build >= 22000
  pub fn create_main_window(app: &tauri::App, label: &str, setting: Setting) -> tauri::Result<()>
  pub fn apply<R: Runtime>(app: &AppHandle<R>, setting: Setting, theme: Theme)
  pub fn refresh<R: Runtime>(app: &AppHandle<R>)
  pub fn paint_background<R: Runtime>(app: &AppHandle<R>, theme: Theme)
  ```

- **Tauri calls it uses** (as Fontface does today):
  - `Window::set_effects(EffectsBuilder::new().effect(e).state(EffectState::FollowsWindowActiveState).build())` (`FF/src-tauri/src/translucency.rs:182-183`);
  - `WebviewWindowBuilder::from_config(..).transparent(see_through)` (`:219`);
  - `Window::set_background_color(Some(Color(r, g, b, a)))`, with alpha 0 while see-through (`FF/src-tauri/src/window.rs:546-556`).
- **Materials:**
  - **macOS:** `Effect::Sidebar`. Liquid Glass (`Effect::LiquidGlassRegular` and `LiquidGlassClear`, macOS 26 and later) exists in the Tauri version Fontface already uses (`CARGO/tauri-utils-2.10.1/src/lib.rs:119-121`; Fontface's lock has `tauri` 2.12.3 and `tauri-utils` 2.10.1, `FFLIVE/src-tauri/Cargo.lock`). Whether to use it is §5.14, question 3.
  - **Windows 11:** `Effect::Mica`, `MicaLight` or `MicaDark`.
  - **Windows 10:** nothing. Acrylic lags while the window moves (`FF/src-tauri/src/translucency.rs:15-19`).
  - **Linux:** no effect. Plain only, and Off by default.
  - **iOS and Android (Tauri mobile):** the plugin compiles to a no-op, and the adapter reports `unsupported`. Mailbird's mobile shell is still a spike, with Capacitor as the fallback (`/Users/sean.sands/Projects/workspace/07-projects/24-mailbird/README.md:28`).
- **Accessibility signals, per OS:**
  - **macOS:** `NSWorkspace.accessibilityDisplayShouldReduceTransparency` and `accessibilityDisplayShouldIncreaseContrast`, plus `NSWorkspaceAccessibilityDisplayOptionsDidChangeNotification` for live changes.
  - **Windows:** the `HKCU\…\Themes\Personalize\EnableTransparency` registry value, plus the real Windows build number from `RtlGetVersion`, re-checked each time the window comes to the front (`FF/src-tauri/src/translucency.rs:232-336`; `FF/src-tauri/src/lib.rs:433-437`). High Contrast reaches the web view as `forced-colors`.
  - **Linux:** the OS gives no reduce-transparency signal. That is one more reason to default to Off. The web view's media queries still apply.
  - The `unsafe` code lives inside the plugin. Apps whose lints forbid `unsafe`, like Synapse (`SY/src/components/TitleBar.tsx:18`), need none of their own.
- **App config:**
  - **macOS:** `"transparent": true` in `tauri.macos.conf.json`, as in `FF/src-tauri/tauri.macos.conf.json`.
  - **Windows and Linux:** `"create": false` (`FF/src-tauri/tauri.windows.conf.json`), and `create_main_window` runs in setup. Turning it on later waits for the next launch.
  - **Permissions:** add the plugin's permission to `src-tauri/capabilities/default.json`.
- **Fix the Windows mode mismatch.** Tauri's plain `Mica` "matches the system dark preference" (`CARGO/tauri-utils-2.10.2/src/lib.rs:122`). So with Appearance set to Dark on a light Windows, a dark tint sits on light Mica. Either pick `MicaLight` or `MicaDark` from the app's Appearance, or use the plain tints whenever Appearance and the OS disagree.
- **Versions and releases:**
  - Changesets versions only the npm packages (`UC/.github/workflows/release.yml`). Add a crate release step with its own tags, for example `tauri-plugin-translucent-v0.1.0`, so apps can pin `git = "…", tag = "…"`.
  - The command and event JSON carry `version` (§5.5).
  - `check-unicron.mjs` also compares the plugin version in `src-tauri/Cargo.lock` with the range `@unicron/ui` expects. Put that range in a field of `@unicron/ui/package.json`. This stops ui 0.15 running against plugin 0.14.
  - Pin the plugin to `tauri = ">=2.12.1, <3"`. From 2.12.1, macOS allows a see-through window without private APIs (`WS/notes/window-translucency-learnings_2026-10-20.md:11`). Fontface and Synapse both ask only for `tauri = "2"` (`FFLIVE/src-tauri/Cargo.toml:17`; `/Users/sean.sands/Projects/synapse/app/src-tauri/Cargo.toml:17`).
  - **The plugin must not turn on `macos-private-api`.** Cargo merges features across crates, so every app would get it. It does nothing from 2.12.1 on (same note, `:11`). Fontface sets it itself (`FFLIVE/src-tauri/Cargo.toml:17`) and can drop it.
- **TS side:** `tauriAdapter()`, about 20 lines of `invoke` plus `listen`.

**Electron (no app uses it today)**
- **macOS:**
  - `new BrowserWindow({ vibrancy: "sidebar", visualEffectState: "followWindow", backgroundColor: "#00000000" })`;
  - `win.setVibrancy(type | null)` switches it while the window is open.
- **Windows 11:**
  - `backgroundMaterial: "mica"` and `win.setBackgroundMaterial("mica" | "none")`;
  - don't use `transparent` on Windows.
- **Signals:** `nativeTheme.prefersReducedTransparency`, `nativeTheme.shouldUseHighContrastColors` and `nativeTheme.inForcedColorsMode`. Read them again on `nativeTheme.on("updated")`.
- **Bridge:** a preload `contextBridge` exposes `{ get, onChange }`. Both OSes switch while the window is open, so `windowReady` is always true.

**Plain web (Lockdown's vault, Mailbird's web app and PWA, Unicron's playground)**
- **A page can't see the desktop.**
  - By default, `reason` is `unsupported` and the setting is hidden.
  - Optional "page backdrop" mode: the app paints its own backdrop, and chrome uses `supports-backdrop-filter:backdrop-blur-*` with the blur tints. The worst case is then known exactly.
- **`prefers-reduced-transparency` works only in Chromium-based browsers,** not in Safari or Firefox. So the in-app setting is the real switch.

**Native (planned builds only)**
- **macOS (SwiftUI or AppKit):**
  - `NavigationSplitView` sidebars get the sidebar material for free.
  - Custom views use `NSVisualEffectView` with `.material = .sidebar`, `.blendingMode = .behindWindow` and `.state = .followsWindowActiveState`.
  - Read `@Environment(\.accessibilityReduceTransparency)`, `@Environment(\.colorSchemeContrast)` and `NSWorkspace.accessibilityDisplayShouldIncreaseContrast`.
  - Tints come from `dist/tokens.json` through code generation.
- **WinUI 3:** `Window.SystemBackdrop = new MicaBackdrop()`. Read `UISettings.AdvancedEffectsEnabled` and its `AdvancedEffectsEnabledChanged` event, plus `AccessibilitySettings.HighContrast` and its `HighContrastChanged` event.
- **iOS and Android (SwiftUI, Compose):** no window setting. Use the system's own chrome only.

### 5.7 Platform notes (the core table of the spec)

This table is the answer to "regardless of the final coded destination". It goes into `UC/docs/specs/translucent-window.md`, laid out like `UC/docs/specs/security/risk-tier-badge.md:91-97`.

| Platform | Native material | Switches while open? | Reduce and contrast signals | Spec still requires |
|---|---|---|---|---|
| Tauri, macOS | `Effect::Sidebar` through the plugin; `transparent: true` | Yes | NSWorkspace reduce transparency and increase contrast, with the change notification; web view media queries | The same setting, stored values, decision table, tokens, overlay classes and solid list |
| Tauri, Windows 11 | `MicaLight` or `MicaDark`, matched to Appearance | No. The window is made at launch, so the reason is `next-launch`. | `EnableTransparency`; build 22000 or later; web view `forced-colors` | Same |
| Tauri, Windows 10 | None | — | — | Shown greyed out, with reason `unsupported` |
| Tauri, Linux | None; plain see-through | No | None from the OS; web view media queries only | Off by default; plain tints |
| Tauri, iOS and Android | None | — | — | The plugin is a no-op; the setting is hidden |
| Electron, macOS | `vibrancy: "sidebar"` | Yes (`setVibrancy`) | `prefersReducedTransparency`, `shouldUseHighContrastColors`, `inForcedColorsMode` | Same |
| Electron, Windows 11 | `backgroundMaterial: "mica"` | Yes (`setBackgroundMaterial`) | Same as Electron on macOS | Same |
| Web and PWA | None; a page can't see the desktop | — | `prefers-reduced-transparency` (Chromium only), `prefers-contrast`, `forced-colors` | Hidden, or page-backdrop mode |
| SwiftUI or AppKit, macOS | `NSVisualEffectView`, `.sidebar`, `.behindWindow` | Yes | `accessibilityReduceTransparency`, `colorSchemeContrast`, `accessibilityDisplayShouldIncreaseContrast` | Tints from `tokens.json` |
| WinUI 3 | `MicaBackdrop` | Yes | `AdvancedEffectsEnabled`, `AccessibilitySettings.HighContrast` | Same |
| SwiftUI on iOS, Compose on Android | System chrome only | — | — | No setting |
| Figma | `window-material` variable collection, with modes `solid`, `blur` and `plain` | — | — | A backdrop sample frame |

**Figma.** Add a `window-material` variable collection with three modes: `solid`, `blur` and `plain`.
- Its variables (`sidebar`, `sidebar-accent`, `pane`, `muted-foreground` per surface) alias the `semantic` collection, in the same way the existing collections mirror the token tiers (`UC/docs/02-tokens.md:113-126`).
- Add a backdrop sample frame. It shows the worst-case backdrops (black, white and the measured colours), with real library components placed over them: sidebar rows, a Monogram, a menu and a toast. Following your Figma rule, use real library components, not hand-drawn shapes.
- Figma can't show the real desktop material. The frame is a contrast check, not a picture of the real thing.

### 5.8 The decision table (the same everywhere)

Rust (`FF/src-tauri/src/translucency.rs:85-96`) and TypeScript share this logic. Rust handles the OS inputs. Only TypeScript adds the web-view inputs.

```
reason =
  system.look == null                                   → "unsupported"
  system.reduceTransparency || webview.reduceTransparency → "os-reduce-transparency"
  system.increaseContrast  || webview.moreContrast        → "os-increase-contrast"
  webview.forcedColors                                   → "forced-colors"         (TS only)
  setting != off && !system.windowReady                  → "next-launch"
  otherwise                                              → null
look   = (setting != off && reason == null) ? system.look : null
window = look != null && setting == window
```

**Order of precedence:**
1. Unsupported: solid, greyed out.
2. The OS asks for less transparency: solid, greyed out, and the text names the setting and where to change it.
3. The OS asks for more contrast: the same, naming the contrast setting.
4. Forced colours: solid.
5. The window was made solid: the text says "Open {app} again to see it."
6. Otherwise: the chosen look.

**Defaults:**
- Whole window on macOS and on Windows 11, for new installs.
- Unsupported on Windows 10.
- Off on Linux.
- Hidden on the web (unless page-backdrop mode is on) and on mobile.
- **Existing users of Synapse, Lockdown and Mailbird get Off when they upgrade.** A settings migration writes `off` for them, because a see-through window would be a visual change they didn't choose. New installs get the platform default.

### 5.9 Accessibility

- **Reduced transparency, more contrast and forced colours each make the window solid.** They also make the frosted menus and the dialog scrim solid (§5.4).
  - Today Fontface relies on the CSS query `prefers-contrast: more`.
  - The plugin should also read `accessibilityDisplayShouldIncreaseContrast` on macOS, which is more reliable.
- **While the setting is greyed out, the control shows "Off",** but the saved choice is kept (`translucencyShown`).
- **No tooltips on the options or the reason.** The reason is visible text in the row's description, chosen by the reason code. The tooltip trim already does this (`FFLIVE/src/translucency.ts:27-52`).
- **Switching fades over 120–200ms,** using Unicron's motion tokens. Under reduced motion it switches instantly.
- **Security surfaces, and colours the app doesn't control, never go see-through** (§5.4).

### 5.10 Settings model and copy

- **One row:**
  - the label "Translucent window";
  - a RadioGroup (C2) with the choices Off, Sidebar and Whole window;
  - the stored values `off`, `sidebar` and `window`.
- **Apps may rename "Sidebar".** For example, Mailbird could call it "Side panels" through `translucencyOptions({ chrome })`.
- **The description says three things:** what the setting does, why it is greyed out (when it is), and "Open {app} again to see it" (when that applies).
- **The template is Fontface's copy** (`FFLIVE/src/translucency.ts:27-52`).
  - The OS words and settings paths move as they are. For example: "Reduce transparency is on in System Settings › Accessibility › Display".
  - "Fontface" and "Font lists and pages" become blanks that each app fills in.
- **The setting is stored per device and never synced** (§5.5).

### 5.11 Contrast rule and tests

**The rule** (to write into `UC/docs/02-tokens.md`):
1. **For each look, mode and surface, the tint's opacity is the lowest value, in 1% steps, at which every recipe on that surface passes its floor.**
   - Each surface is composited over the worst-case backdrop for that look and mode.
   - Unicron's floors (`UC/packages/tokens/scripts/contrast.mjs:36-60`) are:
     - reading text: Lc 75;
     - labels on a fill: Lc 60;
     - control borders: 3:1;
     - the focus ring: 3:1 as drawn. Primitives draw it at 50% (`outline-ring/50`, `UC/packages/ui/src/styles/index.css:100`; `semantic.json` `ring`).
2. **If no opacity up to 97% works,** that surface gets a glass text step: the weakest tier-1 step that passes.
3. **If even that fails,** the look is not offered in that mode.
4. **Text never sits on two see-through layers.** The one exception is the frosted menu, which has its own recipe.
5. **How to measure the backdrop:**
   - Draw the real material over a pure black desktop (for light mode) and a pure white desktop (for dark mode).
   - Do it on real hardware, with the window both active and inactive.
   - Take the darkest pixel (light mode) or the lightest pixel (dark mode).

**What the frosted menu sits on.** In a web view, `backdrop-filter` blurs only page content, never the desktop. So the menu's recipe is a stack of three layers:
1. the 70% menu;
2. on top of the chrome or content tint;
3. on top of the worst-case backdrop.

WebKitGTK, the Linux web view, may not support `backdrop-filter` at all. The menu would then be unblurred, so the recipe must pass without blur (not checked, §6).

**Starting numbers.** These were measured with `apca-w3` 0.1.9, blending in gamma sRGB the way browsers do. The scripts are in the session scratch folder named in Phase 0, step 11. Move them into PR 1k as glass recipes in `contrast.mjs`, and into `WS/notes/`.
- **Fontface's shipped tints pass WCAG AA, but every faint-text case fails Lc 75.**
  - Faint text reads Lc 50.6–71.3.
  - In light mode with blur, even main sidebar text reads only Lc 72.4.
- **With Unicron's colours, these are the lowest opacities that pass:**

| | Chrome | Content |
|---|---|---|
| light, blur (backdrop `#999`) | 0.88 | 0.80 |
| light, plain (black) | 0.96 | 0.92 |
| dark, blur (`#737373`) | 0.43 (0.56 with a 7% selected row) | 0.39 |
| dark, plain (white) | 0.77 (0.82 with a selected row) | 0.74 |

- **The backdrop guess drives the answer.** For light chrome:
  - `#999` needs 0.88;
  - `#ccc` needs 0.74;
  - `#e0e0e0` needs 0.50.

  So measuring the real material could win back a lot of see-through.
- **A frosted `bg-popover/70` menu over the light chrome passes,** at Lc 76.2 for muted text. But Unicron never tests that menu over anything. Over content of the opposite brightness, its muted text drops to about Lc 43. That gap exists even without window glass.

**Recipes to add:**
- chrome text and muted text;
- selected rows;
- **hover rows.** They are `hover:bg-sidebar-accent/60`, a second see-through layer on top of the glass tint (`FFLIVE/src/components/Sidebar.tsx:66`; `FF/src/settings/SettingsNav.tsx:24`);
- the focus ring at 50%, and control borders, including the dark `--input`, which is white at 35% (`UC/packages/tokens/tokens/semantic.json:31`);
- content text and muted text;
- `success`, destructive and warning text on glass content;
- tag label colours (T8). They are 3:1 against a sidebar that turns see-through;
- the Monogram outline (3:1) and the filled Monogram's letter (Lc 60);
- the frosted menu over chrome and over content, using the three-layer stack above;
- the dialog and sheet scrim over glass (reported, not gated);
- the floating toolbar's border over glass content, and the status bar as chrome.

**Tests:**
1. **Unicron's contrast gate** (`UC/packages/tokens/scripts/contrast.mjs`).
   - Add a `backdrop(look, mode)` bottom layer and the recipes above.
   - `flatten()` (`:341-353`) puts a see-through layer on `--background`. Glass recipes must start from the backdrop instead.
2. **One shared fixture, `translucency-cases.json`,** run by both the plugin's `cargo test` and `node --test`.
   - It covers both layers: the OS inputs that Rust decides on, and the web-view inputs that only TypeScript merges.
   - Fontface's 7 Rust tests are the first cases (`FFLIVE/src-tauri/src/translucency.rs:343-405`).
3. **Attribute tests:**
   - The state and the media queries produce the right root attributes, including `data-reduce-transparency`.
   - `first-paint.js` and the store agree on keys and values.
   - **First paint against the backend:** the cache says see-through, but the adapter says reduced. The window must end up solid, with no see-through frame first.
4. **CSS contract test, in a real browser.** Add a Playwright WebKit test that reads the resolved `--sidebar`, `--pane` and `--c-overlay-menu` values. It checks that:
   - each look has a chrome rule and a content rule;
   - the body is clear only under the attribute;
   - the forced-colours rule exists;
   - no glass token resolves through the role it replaces.

   jsdom can't resolve `color-mix` or catch a variable that refers to itself. Unicron already marks colour checks "for Playwright" and lists a browser suite as an open item (`UC/docs/specs/security/README.md:50,58`). This replaces Fontface's Rust test that reads `index.css` (`FFLIVE/src-tauri/src/translucency.rs:405`).
5. **OS build matrix.** Add CI jobs that run `cargo check` and `cargo test` on macOS, Windows and Ubuntu, for both the plugin and Fontface. Fontface's Windows and Linux code has never compiled (`FF/docs/FEATURES.md:221`). On a public repo these runners are free. A private repo would pay for them (D1).
6. **App checks:**
   - dsa checks for `bg-pane` on the main view and `data-surface` on chrome.
   - Synapse's axe and APCA run with `data-translucent` set, over a synthetic backdrop.
7. **Screenshots.**
   - Automate diffs of the Phase 0 baseline screens.
   - Also check by hand on each OS: active and inactive, light and dark. These screenshots also give the measured backdrops. Fontface hasn't done this yet (`FF/docs/FEATURES.md:221`).

### 5.12 How each app adopts it

| App | Where it ships (as found) | Steps |
|---|---|---|
| **Fontface** | Tauri 2. Built for macOS. The Windows and Linux code is written but has never been built (`FF/docs/FEATURES.md:221`). | 1. Import Unicron's styles and delete `FF/src/index.css:130-190`. 2. Add `data-surface` to `FF/src/components/Sidebar.tsx:387`, `FF/src/settings/SettingsNav.tsx:45`, `FF/src/App.tsx:1749,1899` and `FF/src/settings/SettingsView.tsx:96`. 3. Use the shared runtime and plugin, and remove `FF/src-tauri/src/translucency.rs`. The command moves from `translucency_get` to `plugin:translucent|get` (`FFLIVE/src/api.ts:828-829`; `FFLIVE/src-tauri/src/lib.rs:361`). The event keeps the name `translucency-changed` (`FFLIVE/src/settings/translucent.ts:53`). 4. Use RadioGroup for the setting. 5. Replace the inline first-paint script with `first-paint.js`. 6. Check live on macOS, then do the first Windows and Linux builds in the CI matrix. |
| **Synapse** | Tauri 2 on macOS (overlay title bar, `SY/src-tauri/tauri.macos.conf.json`) and Windows. No transparency today (`SY/src-tauri/tauri.conf.json`). | 1. Add the plugin and its permission (`SY/src-tauri/capabilities/default.json`). 2. Set `transparent: true` in `tauri.macos.conf.json`. 3. Add a new `tauri.windows.conf.json` with `create: false`. 4. Put `data-surface="chrome"` on `SY/src/components/Rail.tsx:85`. 5. Give the main view `bg-pane` and `data-surface="content"`. 6. Leave the `<aside>` panels solid. 7. Existing users start at Off (§5.8). It already sets a root attribute (`SY/src/components/Shell.tsx:88-90`), so the pattern fits. |
| **Lockdown** | Tauri 2.12.3 desktop on macOS, Windows and Linux (`gh:lockdown/apps/desktop/src-tauri/Cargo.toml:56`), plus a web vault and a browser extension. No transparency today (`gh:lockdown/apps/desktop/src-tauri/tauri.conf.json`). | 1. Fix the tokens drift. 2. Desktop: the same steps as Synapse. 3. The security surfaces and the secrets stay solid. 4. Web vault: `webAdapter()`, with the setting hidden. 5. Extension: hidden. 6. Decide its default (§5.14, question 5). 7. Keep the setting per device, even though the vault syncs. |
| **Mailbird** | Web app and PWA (`apps/web`), plus a Tauri 2 desktop shell with the native title bar (`apps/web/src-tauri`). Mobile is a spike (`/Users/sean.sands/Projects/workspace/07-projects/24-mailbird/README.md:28`). No transparency today. | 1. Bump into the support window. 2. Flip the chrome alias: point `--surface-chrome` at `--sidebar` and `--surface-canvas` at `--pane` (§5.4). 3. Tag the nav rail, the tab bar and the list pane as `chrome`. 4. Keep HTML email bodies solid. 5. Relabel the choice "Side panels". 6. Web, PWA and mobile: hidden. 7. On macOS, adopt the overlay title bar from the desktop module first, so the glass reaches the top edge. 8. Keep the setting per device. |

### 5.13 Where the spec lives

- **`UC/docs/specs/translucent-window.md`:** the full spec. It holds §5.1 to §5.11, with the platform-notes table (§5.7) as its core. Scrub it with the public-text rule first.
- **A "Translucent window" section in `UC/docs/05-consuming.md`:** how an app adopts it, in the order of the Synapse row in §5.12.
- Both ship in PR 1k.

### 5.14 Open questions

1. **Which contrast rule applies to glass (D4)?** My advice is to measure first, then use APCA.
2. **Linux plain look in light mode** needs about 96% opacity. Offer it in dark mode only, or not at all?
3. **macOS material.** Keep `Sidebar`, or adopt Liquid Glass on macOS 26 with `Sidebar` as the fallback? The Tauri version Fontface uses already has it (§5.6), so this is a design choice, not a question of what is possible.
4. **Web.** Hide the setting, or offer the page-backdrop mode?
5. **Lockdown's default.** A password manager may prefer Off by default, even on macOS.
6. **Windows.** Replace the registry read with the live `UISettings.AdvancedEffectsEnabled` event?

---

## 6. Risks and unknowns

**Visibility and access**
- **Unicron's visibility.** You said Unicron is private. GitHub says it is public, and so are Lockdown and Mailbird (GitHub API, 2026-10-20). Synapse is the private one. Making Unicron private without npm (D1) breaks three public builds, and even with npm it hides little.

**Publishing Fontface**
- **78 unpushed commits** (`826c574..6350609`, 222 files). They need your review against the Typeface rule before the push (Phase 0, step 3). The Unicron provenance lines depend on that push.

**Version drift**
- **Lockdown's tokens drift.** Its pnpm overrides pin tokens 0.6.0, while ui 0.12.0 asks for 0.7.0. So it misses the 0.7.0 contrast fixes (`gh:lockdown/apps/{desktop,web}/pnpm-workspace.yaml`, `gh:lockdown/extension/pnpm-workspace.yaml`).
- **npm apps should drop the override.** One reader tested npm 11.13.0 in a scratch folder:
  - With no override, a mismatch fails the install. That is safe.
  - With the override, npm silently installs the wrong tokens.

  pnpm apps still need the override, plus this check after install:
  ```js
  // scripts/check-unicron.mjs: fail when the installed tokens differ from what @unicron/ui pins
  import { createRequire } from "node:module"
  const req = createRequire(import.meta.url)
  const ui = req("@unicron/ui/package.json")
  const tokens = createRequire(req.resolve("@unicron/ui/package.json"))("@unicron/tokens/package.json")
  const want = ui.dependencies["@unicron/tokens"]
  if (tokens.version !== want) { console.error(`@unicron/ui ${ui.version} wants tokens ${want}, got ${tokens.version}`); process.exit(1) }
  // From R3: also read src-tauri/Cargo.lock and compare tauri-plugin-translucent with the range @unicron/ui declares (§5.6).
  ```
- **Plugin drift.** If the crate tag and `@unicron/ui` don't match, the contract version and the check above catch it (§5.6).
- **Mailbird is outside the support window.** It is on 0.9.0 (`gh:Mailbird/apps/web/package.json:33`).
- **Release pace.** 13 minor releases in 5 days (`UC/packages/ui/CHANGELOG.md`). Without batching, every app falls behind within a day.

**Out-of-date clones**
- **The local Unicron clone is behind GitHub.** It is on `icon-webkit-anchor` at `9fd04e2`, and its last tag is 0.13.0.

**Fontface gaps**
- **No CI and no licence** (`FFLIVE/` has no `.github/` and no LICENSE).

**Look and rendering**
- **The look changes:** Unicron's cooler grey (D6), Inter vs Plex (D3), the toast icon and corners, and the Checkbox tick (P10, P15).
- **Icons in WebKit.** They need ui 0.13.1 or later. Check them in Fontface's WKWebView.
- **Hand-copied colours.** Six Fontface files copy colours or parse `index.css` (Phase 2, step 4). They break silently if they aren't moved to the generated values. That move needs T11, which ships in R1.

**Transparency**
- **The worst-case backdrops are guesses** (`#999` and `#737373`). Under APCA they decide how see-through the glass can be. Nobody has seen the tints live yet (`WS/notes/window-translucency-learnings_2026-10-20.md`, last line).
- **Windows and Linux translucency have never been built,** and that blocks the measurements for 1k (Phase 1).
- **Mica can show the wrong mode.** Fontface's code is untested on Windows (`FF/src-tauri/src/translucency.rs:27`), and plain `Mica` follows the OS, not the app (§5.6).
- **Windows High Contrast isn't handled today.** §5.4 fixes this.
- **The first-paint script can flash glass** for people who asked for less transparency. §5.5 fixes this.
- **The kill switch only works as a migration** (see "Rollback").

**Naming and constraints**
- **The name clash** with Mailbird's old `Mark` and Unicron's `CrownJewelMark` (D11).
- **"Mailbird" is a working name** that matches a real email client (W5).
- **Typeface analysis detail** must never enter Unicron or Fontface, because both are public (`WS/SESSION-STATE.md:13,110`).
- **Employer content** must never enter either repo (`/Users/sean.sands/Projects/workspace/07-projects/29-unicron/README.md:33`).

**Not checked**
- Who owns the npm `unicron` scope.
- Whether GitHub Packages needs a token for public installs.
- Whether npm provenance needs a public repo.
- Whether Electron's `nativeTheme` "updated" event fires when reduced transparency changes.
- Whether WebKitGTK supports `backdrop-filter`.
- That Tauri hashes inline scripts into the CSP. This is inferred from Fontface's inline script working under `default-src 'self'`.
- Synapse's, Lockdown's and Mailbird's CSPs.
- Lockdown's and Mailbird's code, which was read only from GitHub `main`, not from a local checkout.

---

## 7. Sources for the platform claims

**Checked in local source:**
- Tauri window effects: `CARGO/tauri-utils-2.10.2/src/lib.rs:112-123`. This covers `LiquidGlassRegular` and `LiquidGlassClear` for macOS 26.0 and later, and plain `Mica` matching "the system dark preference". The same Liquid Glass variants are at `CARGO/tauri-utils-2.10.1/src/lib.rs:119-121`.
- Tauri's Liquid Glass handling: `CARGO/tauri-2.12.4/src/vibrancy/macos.rs:28`.
- `macos-private-api` doing nothing from Tauri 2.12.1, and WebKit reading unknown media queries as "not all": `WS/notes/window-translucency-learnings_2026-10-20.md:11` and the same note.
- Fontface's Tauri version: `FFLIVE/src-tauri/Cargo.lock` (`tauri` 2.12.3, `tauri-utils` 2.10.1).

**Official docs to cite in the public spec** (not opened in this pass):
- Tauri `Effect`: https://docs.rs/tauri/latest/tauri/window/enum.Effect.html
- Electron BrowserWindow (`vibrancy`, `visualEffectState`, `backgroundMaterial`, `setVibrancy`, `setBackgroundMaterial`): https://www.electronjs.org/docs/latest/api/browser-window
- Electron nativeTheme (`prefersReducedTransparency`, `shouldUseHighContrastColors`, `inForcedColorsMode`, `updated`): https://www.electronjs.org/docs/latest/api/native-theme
- CSS Color Adjustment Level 1, forced colours mode: https://www.w3.org/TR/css-color-adjust-1/#forced
- `prefers-reduced-transparency`: https://www.w3.org/TR/mediaqueries-5/#prefers-reduced-transparency and https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-reduced-transparency
- AppKit `NSVisualEffectView`: https://developer.apple.com/documentation/appkit/nsvisualeffectview
- `accessibilityDisplayShouldReduceTransparency`: https://developer.apple.com/documentation/appkit/nsworkspace/accessibilitydisplayshouldreducetransparency
- Windows Mica: https://learn.microsoft.com/en-us/windows/apps/design/style/mica
- `UISettings.AdvancedEffectsEnabled`: https://learn.microsoft.com/en-us/uwp/api/windows.ui.viewmanagement.uisettings.advancedeffectsenabled
- APCA (`apca-w3`): https://github.com/Myndex/apca-w3





