---
tags: [design-systems, color, theming, tokens, bootstrap, emphasis-engine]
created: 2026-10-08
updated: 2026-10-08
status: working
confidence: medium
sources: [emphasis-engine native example build 2026-10-08, github.com/snds/emphasis-engine docs/systems/bootstrap.md, src/native/bootstrap.tsx]
related_skills: [ds-advisor, design-engineer]
related_projects: [emphasis-engine]
relations:
  relates-to:
    - "[[ds-native-theming-survey]]"
---

# Bootstrap 5 — how its color works, learned by theming it

## For future agent
- **TL;DR:** Root `--bs-*` variables for page, text, and status triplets (`-text-emphasis`, `-bg-subtle`, `-border-subtle`). Each component class carries its own variables (`--bs-btn-bg` on `.btn-primary`), and many of them hold literal hex values baked at build time: checked states, focus rings, links, and badges. So a runtime theme stops at the button. `data-bs-theme` on any element is the mode boundary.
- **Key claims:** see "How its color works" and "What the solved theme reached" below. Each was observed by rendering the real components and injecting a solved theme (stock vs. themed, light and dark, 390 and 1280 wide).
- **Centric takeaways:** section "Ideas for the Centric design system"; consolidated in [[centric-ds-ideas-from-ds-survey]].
- **As of:** 2026-10-08 (dated: package versions below) · **Status:** current
- **Audience:** `for: all`
- **Update 2026-10-08 (profile fixes):** Fixed: outline and link buttons stay outlined (the base `.btn` value is now read as transparent); warning text and the success border match stock; `alert-info` and the `-rgb` channel variables (links, badges, tables) are themed. Still stock: the checked checkbox fill and focus rings (build-time literals).

## At a glance

- Package: `bootstrap` 5.3.8 (CSS only, `bootstrap/dist/css/bootstrap.min.css`). MIT license.
- No JS bundle on the page. Nothing in the scene needs it for static display. The navbar collapse simply stays collapsed below `lg`.
- Docs patterns followed (getbootstrap.com/docs/5.3):
  - Layout: `/layout/grid/`, `/layout/gutters/`
  - Components: `/components/navbar/`, `/components/breadcrumb/`, `/components/navs-tabs/`, `/components/card/`, `/components/buttons/`, `/components/alerts/`, `/components/badge/`, `/components/modal/` (footer button order)
  - Forms: `/forms/overview/`, `/forms/form-control/`, `/forms/select/`, `/forms/checks-radios/`, `/forms/validation/` (server-side section)
  - Content and theming: `/content/tables/`, `/helpers/color-background/`, `/utilities/colors/`, `/customize/color-modes/`, `/customize/css-variables/`
  - I worked from these patterns and from the installed CSS. I did not re-fetch the pages this session.

## How its color works

- Two tiers of CSS variables, both compiled from Sass.
  - Root tier on `:root, [data-bs-theme=light]` and `[data-bs-theme=dark]`: `--bs-body-bg`, `--bs-body-color`, `--bs-secondary-color`, `--bs-tertiary-color`, `--bs-border-color`, `--bs-link-color`, the theme colors `--bs-primary` and friends, their `-rgb` triplets, and per-status `-text-emphasis`, `-bg-subtle`, `-border-subtle`.
  - Component tier on each component class: `.btn-primary` sets `--bs-btn-bg`, `--bs-btn-hover-bg`, `--bs-btn-active-bg`, `--bs-btn-disabled-bg` and the matching color and border variables. `.alert-success` points `--bs-alert-*` at the root status tokens. `.nav-tabs`, `.card`, `.navbar` and `.table` work the same way.
- Light and dark switch with `data-bs-theme` on `<html>`. Any element can carry it, so a dark navbar inside a light page is one attribute.
- State colors are separate tokens, and Sass picks the values at build time. Hover is `shade-color($primary, 15%)`, active is 20%. Each one ships as a literal hex in its own variable. There's no `color-mix` anywhere in the CSS. Disabled buttons use `--bs-btn-disabled-*` (the base colors again) plus `opacity: .65`.
- A lot of color never becomes a variable. These ship as literal hex from Sass: `.form-check-input:checked` (`#0d6efd`), the switch knob SVG, the focus ring on inputs (`#86b7fe` border, `rgba(13,110,253,.25)` shadow), and the `.is-invalid` icon SVG. Button variables are literals too. `.btn-primary` writes `--bs-btn-bg: #0d6efd` instead of `var(--bs-primary)`.
- `text-bg-*` badges compute their background from `RGBA(var(--bs-success-rgb), var(--bs-bg-opacity))`. Their text color is a literal `#fff` or `#000`, chosen at build time with `!important`.

## Building the native page

- Navbar: `navbar navbar-expand-lg bg-body-tertiary` in a `.container`, brand, toggler, `navbar-nav` with `active` + `aria-current="page"`, and the user name as `navbar-text`. Bootstrap has no avatar component.
- Body: `.container` with `row`/`col` and gutter classes (`g-3`, `g-4`). Stats use `row-cols-1 row-cols-md-3`. The form and side column split `col-lg-7` / `col-lg-5` and stack below `lg`.
- Bootstrap has no stat component. Stats are cards (`card-subtitle text-body-secondary`, a large `card-title`, `card-text small`), its nearest native equivalent.
- The form follows the stacked docs layout: `mb-3` groups, `form-label`, `form-control`, `form-text` with `aria-describedby`. The error uses server-side validation, `is-invalid` + `invalid-feedback`, which shows without `.was-validated`. The switch is `form-check form-switch` with `role="switch"`. The radio group is a `fieldset` with `legend.col-form-label`.
- Form actions sit in `card-footer`, right-aligned, dismissive first and primary last, the modal-footer convention. Cancel is `btn-link`.
- Action hierarchy: `btn-primary`, `btn-secondary`, `btn-outline-primary`, `btn-link` (Bootstrap's ghost), `btn-danger`, and `btn-primary` with `disabled`.
- Alerts: `alert-success`, `alert-info`, `alert-warning`, `alert-danger`, each with `alert-heading`. Info is `alert-info`, not `alert-primary`, so status isn't mapped onto brand. No icons, because Bootstrap Icons is a separate package.
- Table: `table-responsive` > `table table-hover align-middle text-nowrap` with a `caption` and `th scope="row"` for the PO. Status uses `badge text-bg-{success,warning,info,danger}`. `text-nowrap` keeps cells on one line at 390px, and the table scrolls inside its wrapper.
- Text emphasis: body, `text-body-secondary`, `text-body-tertiary` (closest to "disabled text"), and a plain `<a>`.

## What the solved theme reached

The profile solves 63 variables: 9 at the root (`--bs-body-bg`, `--bs-body-color`, `--bs-border-color`, `--bs-secondary-bg`, `--bs-secondary-color`, `--bs-success-border-subtle`, `--bs-warning-text-emphasis`) and the rest scoped to `.btn*`, `.card`, `.nav`, `.nav-tabs`, `.alert-danger`, `.alert-primary` and `.form-check-input`.

Reached:
- Page and card backgrounds, body text, borders, card borders and the transparent card header.
- `btn-primary`, `btn-secondary` (warm gray), `btn-danger`, and all their hover and active states.
- Tab link color (`--bs-nav-link-color@.nav`), the active tab, and the tab border.
- `alert-danger` background, border and text.

Broken by the theme (profile bugs, not page bugs):
- `--bs-btn-bg@.btn` and `--bs-btn-border-color@.btn` are solved to brand. The kit writes them as `.btn{--bs-btn-bg:… !important}`. `btn-outline-primary` and `btn-link` don't set their own `--bs-btn-bg`, because they inherit the transparent base from `.btn`. So they turn into solid magenta blocks with magenta text. In light mode the label is invisible ("Preview" and both "Cancel" buttons). The probe saw `.btn` as the declaring selector, but the base value is the transparent fallback for the outline and link variants and should not be themed. Fix: drop the `@.btn` entries, or solve them to `transparent`.
- `--bs-warning-text-emphasis` is solved to `#ffffff` in light mode. Warning alert text becomes white on pale yellow (1.1:1). Stock is a dark brown, `#664d03`.
- `--bs-success-border-subtle` is solved to `#effff2` in light mode. That's nearly white, so the success alert border disappears (1.04:1 against white).

Not reached:
- Links: `--bs-link-color` and `--bs-link-hover-color` aren't in the profile. The breadcrumb link and "View supplier scorecard" stay Bootstrap blue.
- Checkbox, radio and switch checked fill, and input focus rings. These are Sass literals, not variables, so no root override can reach them.
- Disabled primary button: `--bs-btn-disabled-bg` isn't solved, so "Publish" stays pale blue next to a magenta primary.
- `alert-success`, `alert-info`, `alert-warning` backgrounds: their `-bg-subtle` root tokens aren't solved. The profile solves `alert-primary`, which the harness used as "info", but this page uses `alert-info`.
- Badges: `--bs-*-rgb` triplets aren't solved, and the badge text color is a literal.
- Navbar: `bg-body-tertiary` and `--bs-navbar-color` aren't solved. It stays neutral gray in both modes, so it reads slightly cool against the warm solved page.

## Accessibility notes

- Stock `btn-primary` is white on `#0d6efd`, exactly 4.50:1. One step lighter would fail.
- `text-body-tertiary` sits around 50% alpha. Fine for a deliberately disabled look, but not for content.
- Disabled buttons drop to 65% opacity and keep their hue. A disabled primary still reads as "primary" at a glance.
- Hover and active colors only darken (`shade-color`). In dark mode the hover on a mid-blue primary gets darker against a dark page, so it loses contrast instead of gaining it.
- `.is-invalid` adds a red border and a red icon. The text message carries the meaning, so it passes for color-alone, as long as `invalid-feedback` is present.

## Ideas for the Centric design system

Borrow:
- The component-scoped variable contract (`--bs-btn-bg` on `.btn-primary`, read by `.btn`). It's the same shape as a component token tier. One base rule reads variables, and each variant only rewrites variables. That keeps variants cheap across Vue, React and Angular, because the CSS is the contract.
- `data-bs-theme` on any element as a mode boundary. Useful for dark table headers, record-detail side panels, or a dark global nav inside a light app, with no JS.
- Status triplets per status: `-text-emphasis`, `-bg-subtle`, `-border-subtle`. That's exactly the three roles a data-dense table needs for a status cell, a row highlight and a callout. Name them that plainly.
- Server-side validation classes that work without a JS form state (`is-invalid` alone shows the message). Good for bulk-edit grids, where the server returns the errors.

Avoid:
- Variables that bake literals instead of pointing at the semantic tier (`--bs-btn-bg: #0d6efd` instead of `var(--bs-primary)`). Retheming then means rewriting every component variable. Component tokens should alias semantic tokens.
- State colors computed at build time by a preprocessor function. Runtime theming can't follow, and dark mode gets darker hovers. Prefer explicit state tokens per mode, or `color-mix` against the surface.
- Checked-state and focus-ring colors left as literals. Every interactive state color should be a token, or the brand stops at the button.
- A base-class variable that doubles as the "transparent" default for some variants. It invites exactly the override collision described above. Give outline and ghost variants their own explicit `transparent`.

## Open issues

- Profile: remove or fix `--bs-btn-bg@.btn` and `--bs-btn-border-color@.btn`. Either solve them to transparent or drop them. They break the outline and link buttons.
- Profile: the `--bs-warning-text-emphasis` and `--bs-success-border-subtle` light values look like the wrong step or direction. Check the `path` for both.
- Profile: consider adding `--bs-link-color`/`--bs-link-hover-color`, `--bs-btn-disabled-*@.btn-primary`, and the `-bg-subtle`/`-text-emphasis` set for all four statuses (`--bs-info-*`, not `alert-primary`).
- Checked form controls and focus rings can't be themed through variables in stock Bootstrap. Reaching them would need a Sass rebuild or component-selector overrides.
