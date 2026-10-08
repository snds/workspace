---
tags: [design-systems, color, theming, tokens, material, emphasis-engine]
created: 2026-10-08
updated: 2026-10-08
status: working
confidence: medium
sources: [emphasis-engine native example build 2026-10-08, github.com/snds/emphasis-engine docs/systems/material.md, src/native/material.tsx]
related_skills: [ds-advisor, design-engineer]
related_projects: [emphasis-engine]
relations:
  relates-to:
    - "[[ds-native-theming-survey]]"
---

# Material 3 (@material/web) — how its color works, learned by theming it

## For future agent
- **TL;DR:** Every component reads `--md-sys-color-*` roles through component tokens with a role fallback, and the variables pierce shadow DOM, so a role-level theme reaches nearly everything. @material/web ships no theme and no dark scheme, and has no card, table, alert, or top app bar. There is only one status role (error).
- **Key claims:** see "How its color works" and "What the solved theme reached" below. Each was observed by rendering the real components and injecting a solved theme (stock vs. themed, light and dark, 390 and 1280 wide).
- **Centric takeaways:** section "Ideas for the Centric design system"; consolidated in [[centric-ds-ideas-from-ds-survey]].
- **As of:** 2026-10-08 (dated: package versions below) · **Status:** current
- **Audience:** `for: all`

## At a glance

- Package: `@material/web` 2.5.0 (Apache-2.0). Lit web components, shadow DOM. Google has put it in maintenance mode, so no new components are coming.
- Page: `src/native/material.tsx`, entry `native/material.html`.
- Docs used:
  - https://material-web.dev/theming/color/ (fetched)
  - m3.material.io for color roles, layout (window size classes), cards, top app bar, and data tables. The site needs JavaScript and didn't render for WebFetch, so I checked specifics against the component token files shipped in the package: `node_modules/@material/web/tokens/versions/v0_192/_md-comp-{top-app-bar-small,outlined-card,filled-card,data-table,banner}.scss`.

## How its color works

- Three tiers. Reference palette tones (`md-ref-palette`: `primary40`, `neutral96`). System color roles (`--md-sys-color-primary`, `on-primary`, `primary-container`, `surface-container-high`, and so on). Component tokens (`--md-filled-button-container-color`) that default to a sys role.
- Each component reads `var(--md-filled-button-container-color, var(--md-sys-color-primary, #6750a4))`. The last fallback is the **light** baseline color, hard-coded in the component's shadow CSS.
- **No theme ships.** Nothing defines `--md-sys-color-*` on `:root`. Out of the box you get the light baseline from those fallbacks, and dark mode does nothing. The app has to supply both schemes (Theme Builder or material-color-utilities). Custom properties inherit through shadow roots, so a root variable reaches every component.
- Light/dark is whatever the app chooses. This page uses `.dark` on `<html>`, which matches the profile's selectors and the probe default.
- States are fixed-opacity layers of the on-color, drawn by `md-ripple` / `md-focus-ring`. Hover is 8%, focus and pressed are 10%. Disabled is on-surface at 12% (container) and 38% (label). There are no separate hover tokens. The solver has to pick tones that make those fixed layers visible.
- Status: M3 has exactly one status role, `error` (+ `on-error`, `error-container`, `on-error-container`). There's no success, warning or info role. Theme Builder's "custom colors" generate them, but they're not part of the baseline scheme or `@material/web`.

## Building the native page

- **Stock scheme.** Because the package ships no theme, the page builds one from the package's own token source. It imports `_md-ref-palette.scss` and `_md-sys-color.scss` (v0.192) with `?raw`, resolves each role to its palette tone, and writes light on `:root` and dark on `:root.dark`. No literal colors in the page, and stock dark now works. The kit's solved values go on top, as usual.
- **Type.** `md-typescale-styles` (adopted stylesheet) for every text style. `--md-ref-typeface-brand/plain` set to `Roboto, system-ui, sans-serif`. Roboto isn't bundled, so system-ui renders.
- **Layout.** Window size classes: 16dp margins in compact (<600), 24dp from medium up. Two panes from expanded (≥840). Spacing on the 4/8dp grid.
- **Components used**: outlined text fields (`supporting-text`, `error` + `error-text`), `md-outlined-select`, `md-switch` as the trailing control of an `md-list-item` (the M3 settings pattern), `md-checkbox` and `md-radio` in labels, `md-tabs` / `md-primary-tab`, `md-icon-button`, `md-divider`, and labs `md-outlined-card` / `md-filled-card` and `md-navigation-bar` / `md-navigation-tab`.
- **Buttons.** Emphasis order is filled, filled-tonal, outlined, text. Form actions sit at the trailing edge, text button (Cancel) then the filled button (Save). There's one filled button per container. M3 has no danger button, so danger is a filled button with its component tokens pointed at `error` / `on-error`, the documented way to restyle a component.
- **Composed from roles, because @material/web lacks them:**
  - **Top app bar**: follows `top-app-bar-small` tokens. 64px, `surface` container, `title-large` headline in `on-surface`, trailing icons in `on-surface-variant`.
  - **Status messages**: labs filled cards. Danger uses `error-container` / `on-error-container`. Success, info and warning use `surface-container-high` with an `on-surface-variant` icon. They differ only by icon and title, because M3 has no role for them. I didn't map them onto primary, secondary or tertiary, since those are brand.
  - **Data table**: a plain `<table>` following the `data-table` tokens. 4px corner, 1px `outline-variant` edge and row dividers, 56px header in `title-small` / `on-surface-variant`, 52px rows in `body-medium` / `on-surface`. It sits in its own horizontal scroll box.
  - **Table status**: icon plus label. M3 has no status chip or lozenge (chips are interactive, badges are counts). "Rejected" uses the `error` role. The others stay neutral.
  - **Link**: no component. An `<a>` in `primary`, underlined.
  - **Disabled text**: `on-surface` at 0.38 opacity, M3's disabled rule.
- **Left out or substituted:**
  - **Breadcrumb**: not in M3. Left out.
  - **Navigation**: M3 wants a rail or a standard drawer at medium and expanded widths. @material/web has neither as an inline component (the labs drawer is modal). The labs navigation bar sits at the bottom of the page at every width.
  - **Icons**: Material Symbols isn't bundled. Tabler SVGs go in `md-icon`. Note that `md-icon` fills slotted SVGs with `currentColor`, so stroke icons need `svg { fill: none }` from the light DOM.

## What the solved theme reached

Shots compared: `material-{390,1280}-{light,dark}-{stock,themed}.png`, magenta brand.

Almost everything. Every component resolves to `--md-sys-color-*`, the kit writes those on `<html>`, and custom properties cross shadow boundaries. Nothing is portaled at rest, and the hard-coded fallbacks only show when a role is unset.

- **Primary group**: filled buttons, the text and outlined button labels, the active tab label and indicator, switch track, checkbox and radio fills, the focused field outline, and the link all moved to the solved primary. In light mode the solver picked a deep plum, not the loud magenta. A light-on-dark label needs that tone for contrast. In dark mode it chose a light pink primary with dark labels, which is the M3 dark pattern.
- **Secondary group**: the tonal button and the navigation bar's active indicator went close to neutral gray. The profile derives secondary at 0.3× brand chroma, so it barely reads as tinted. Stock baseline secondary is visibly lavender.
- **Error group**: the danger button, the invalid field's outline and helper text, the danger card, and "Rejected" all followed the solved error. It's a darker, warmer red in light mode and a salmon in dark.
- **Surfaces and outlines**: page, card edges, the status cards (`surface-container-high`), the nav bar (`surface-container`) and dividers all picked up a faint brand cast.
- **Not reached**: roles the profile doesn't solve keep the baseline. Those are tertiary, `surface-variant`, `surface-dim`/`bright`, the `inverse-*` roles, the `*-fixed` roles, `shadow` and `scrim`. None of them is visible on this page. A snackbar (`inverse-surface`) or a tertiary FAB would show the stock purple next to the solved theme.

## Accessibility notes

- Stock baseline is solid. Role pairs are built for 4.5:1 and above. The weak spots are by design:
  - Disabled labels at 38% `on-surface` and disabled containers at 12% are around 2:1. That's expected, but the disabled filled button is hard to see at all in dark mode.
  - The 8% hover layer on `surface` is a very small step (not measured here, but barely visible in practice). Hover is close to invisible on outlined buttons and list items.
  - `outline-variant` dividers and card edges are faint by design. Don't use them for field borders (M3 uses `outline` for those, correctly).
- Tabs at 390px scroll inside `md-tabs`, and the last tab is cut off with no affordance. M3 calls for scrollable tabs with an edge fade, which @material/web doesn't draw.
- Without real Material Symbols, icon-only buttons depend entirely on `aria-label`. They have one here.

## Ideas for the Centric design system

- **Borrow container/on-container pairs.** Every fill ships with its text color (`error-container` + `on-error-container`). A component can't pair a fill with the wrong text. That's ideal for status cells in big tables and for cross-framework ports, because the pair is the API.
- **Borrow surface-container levels.** Five named tonal surfaces (lowest → highest) replace elevation shadows. Dense PLM screens (record detail with nested panels, bulk-edit drawers) need layering without shadows piling up. Named levels make "one step up from the parent" a token choice, not a guess.
- **Borrow component tokens with a role fallback.** `var(--md-filled-button-container-color, var(--md-sys-color-primary))` is exactly Centric's component → semantic tier, done in pure CSS. It survives shadow DOM, so it would work for Angular's emulated encapsulation and web components alike. Restyling danger this way took seven component-token overrides and no new CSS.
- **Avoid shipping no theme.** Components that fall back to hard-coded light colors silently work in light mode and silently break in dark. Ship a default scheme for both modes in the token package, and make the fallback obviously wrong (or absent) so a missing token shows up in review.
- **Avoid one status role.** M3's lone `error` role forces every product to invent success, warning and info off-system. Centric needs at least four status families, each with a full container/on-container set, as first-class semantic tokens.
- **Be careful with fixed-opacity states.** One 8%/10% rule is easy to port across Vue, React, React Native and Angular. But it gives near-invisible hover on light surfaces. If you adopt it, let the solver set the layer opacity per surface level, or use separate state tokens for dense tables, where hover is the main row affordance.
- Density: @material/web exposes density only per component (`--md-*-density`-style tokens on some components). There's no global density mode. Centric's density modes should stay a single top-level switch.

## Open issues

- The stock scheme is built at runtime by parsing the package's SCSS token source. That's fragile if the token file format changes. If more pages need it, a build-time JSON of the baseline roles belongs in the engine (the profile already has `BASELINE`). That would be a contract change. I didn't make it.
- Roboto and Material Symbols aren't loaded. The type scale and icons are the right shape but not the right faces.
- No rail or standard drawer at wider widths (not in @material/web).
- Secondary at 0.3× chroma reads as gray when themed. Worth checking against the M3 rule (secondary ≈ 1/3 of primary chroma, but with a floor) in the engine.
