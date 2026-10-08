---
tags: [design-systems, color, theming, tokens, daisyui, emphasis-engine]
created: 2026-10-08
updated: 2026-10-08
status: working
confidence: medium
sources: [emphasis-engine native example build 2026-10-08, github.com/snds/emphasis-engine docs/systems/daisyui.md, src/native/daisyui.tsx]
related_skills: [ds-advisor, design-engineer]
related_projects: [emphasis-engine]
relations:
  relates-to:
    - "[[ds-native-theming-survey]]"
---

# daisyUI 5 — how its color works, learned by theming it

## For future agent
- **TL;DR:** A flat set of role tokens, each paired with its on-color (`primary` / `primary-content`). All state colors are `color-mix()` of the role at runtime, so a theme that sets the base roles carries through hover and soft variants. Mode is `data-theme`. There is no component token tier.
- **Key claims:** see "How its color works" and "What the solved theme reached" below. Each was observed by rendering the real components and injecting a solved theme (stock vs. themed, light and dark, 390 and 1280 wide).
- **Centric takeaways:** section "Ideas for the Centric design system"; consolidated in [[centric-ds-ideas-from-ds-survey]].
- **As of:** 2026-10-08 (dated: package versions below) · **Status:** current
- **Audience:** `for: all`
- **Update 2026-10-08 (profile fixes):** Fixed: `--color-primary` is the brand solid again (pairs are grouped by property). `--color-secondary` follows the brand, since the engine has one brand color; before, it fell to the danger hue.

## At a glance

- Package: `daisyui` 5.7.47, a plugin for `tailwindcss` 4.3.3. MIT license.
- The probe loads the prebuilt `daisyui/daisyui.css`, which has component classes only. The native page compiles daisyUI as a Tailwind plugin instead (`src/native/daisyui.css`: `@import "tailwindcss" source(none)`, `@source "./daisyui.tsx"`, `@plugin "daisyui" { themes: light --default, dark; }`), so layout can use Tailwind utilities the way daisyUI's docs do. The repo's Vite config already runs `@tailwindcss/vite`. `source(none)` keeps scanning to this one page. `--prefersdark` is off, so only `data-theme` switches mode, same as the probe.
- Docs patterns followed (daisyui.com, v5):
  - Theming and setup: `/docs/themes/`, `/docs/install/`, `/docs/colors/`
  - Navigation: `/components/navbar/` (responsive dropdown + `menu-horizontal`), `/components/menu/`, `/components/breadcrumbs/`, `/components/tab/`
  - Content: `/components/stat/`, `/components/card/`, `/components/avatar/` (`avatar-placeholder`)
  - Forms: `/components/fieldset/`, `/components/label/`, `/components/input/`, `/components/select/`, `/components/toggle/`, `/components/checkbox/`, `/components/radio/`, `/components/validator/`
  - Actions and status: `/components/button/`, `/components/alert/`, `/components/table/`, `/components/badge/`, `/components/link/`
  - I worked from these patterns and from the installed component CSS (v5 class names were checked in `node_modules/daisyui/components/*.css`). I did not re-fetch the pages this session.

## How its color works

- One flat tier of about 20 theme variables, set on `:root, [data-theme=light]` and `[data-theme=dark]`:
  - Surfaces: `--color-base-100/200/300`, with text color `--color-base-content`.
  - Roles: `--color-primary`, `secondary`, `accent`, `neutral`.
  - Statuses: `--color-info`, `success`, `warning`, `error`.
  - Every role and status has a paired `-content` color for text on top.
  - Plus non-color knobs: `--radius-*`, `--size-*`, `--border`, `--depth`, `--noise`.
- Tailwind exposes the same names as utilities (`bg-primary`, `text-base-content/70`). Opacity modifiers compile to `color-mix(in oklab, var(--color-base-content) 70%, transparent)`, so they follow the theme.
- Components keep private variables that point at the theme. `.btn-primary` sets `--btn-color: var(--color-primary)` and `--btn-fg: var(--color-primary-content)`. `.alert-success` sets `--alert-color: var(--color-success)`. The base `.btn` / `.alert` rules read those.
- Mode is `data-theme` on `<html>` (or on any element, for a nested theme). Values are OKLCH in the stock themes.
- States come from `color-mix` at runtime:
  - Hover: `color-mix(in oklab, var(--btn-bg), #000 7%)`.
  - Depth shadow: `color-mix(... var(--btn-bg) calc(var(--depth) * 30%), #0000)`.
  - Soft and outline variants: `color-mix` of the role color into `base-100`.
  - Disabled: `color-mix(in oklch, var(--color-base-content) 20%, #0000)` text on a 10% `base-content` fill. It's neutral regardless of variant.
- Nothing important is a literal. There's no JS theme object, no shadow DOM, and no portals.

## Building the native page

- Navbar: daisyUI's responsive pattern. `navbar-start` has a `dropdown lg:hidden` hamburger and the brand as `btn btn-ghost text-xl`. `navbar-center` has `menu menu-horizontal` with `menu-active` on Suppliers. `navbar-end` has an `avatar avatar-placeholder` with initials.
- Layout: Tailwind utilities, since daisyUI has no grid of its own. `max-w-6xl` centered, `space-y-6`, `grid lg:grid-cols-12`, with the form on 7 columns and the side column on 5.
- Tabs: `tabs tabs-border` with `tab-active`. They scroll inside themselves at 390px.
- Stats: `stats stats-vertical md:stats-horizontal` with `stat-title`, `stat-value`, `stat-desc`. The component exists natively, so no substitute was needed.
- Form: v5 `fieldset` + `fieldset-legend` per field, with `p.label` for helper text.
  - Toggle, checkbox and radios are `label.label` wrapping the input, the v5 pattern.
  - The error field uses `input validator` with `aria-invalid="true"` and a `validator-hint`. `validator` reacts to `:user-invalid` or `aria-invalid`, so the error shows without interaction.
  - Actions go in `card-actions justify-end`, `btn-ghost` Cancel then `btn-primary` Save.
- Action hierarchy: `btn-primary`, `btn-secondary`, `btn-outline btn-primary`, `btn-ghost`, `btn-error`, and `btn-primary btn-disabled` with `aria-disabled` and `tabIndex=-1`, per the docs.
- Alerts: `alert-success/info/warning/error` (solid default style), each with the Heroicons outline SVG the docs use (`stroke="currentColor"`) and a title + body block.
- Table: inside a `card card-border`, `overflow-x-auto` > `table whitespace-nowrap`, with `badge badge-sm badge-{success,warning,info,error}`.
- Text: `text-base-content`, `/70`, `/40`, and `link link-primary`.
- Nothing was missing. Tailwind utilities handle layout and spacing, which is how daisyUI is meant to be used.

## What the solved theme reached

The profile solves 11 root variables: `base-100`, `base-200`, `base-content`, `primary(-content)`, `secondary(-content)`, `info(-content)`, `error(-content)`. They're all root variables, and every component reads them through `var()`, so the reach is total for those names.

Reached:
- Page background and text. The dark base picks up the brand's warm tint.
- Primary button, outline button, toggle, checkbox, radio, link, and the card actions' primary.
- Error: the validator border and hint, `btn-error`, `alert-error`, and the Rejected badge.
- Info: the alert and the "In production" badge.
- Hover, depth and soft shades follow automatically, because they're `color-mix` of the solved base.

Not reached, by design of the profile:
- `success`, `warning`, `accent`, `neutral` and `base-300` keep their stock values.
  - Success and warning alerts and badges look exactly like stock.
  - The navbar's active menu item and the avatar use `neutral`, so they stay near-black in light mode.
  - Card and stats borders (`base-300` / `card-border`) keep the stock gray, slightly cool against the warm solved base in dark mode.

Worth a look:
- `--color-secondary` is solved to a red (`#f5453f` light, `#f64740` dark). That's almost the same as `--color-error` (`#ff695e`). "Duplicate" (secondary) and "Delete workspace" (error) now look like the same action. Stock secondary is a pink (hue 354) that's distinct from error (hue 13). The solver seems to rotate the brand hue onto red.
- `--color-secondary-content` (`#f1e7f1`) on that secondary is 3.0:1, below 4.5 for button text. `--color-primary-content` on magenta is 4.1:1 in light mode, just under AA for the 14px semibold labels.

## Accessibility notes

- Stock light theme:
  - Secondary is `oklch(65% .241 354)` with a near-white `-content`, which is low contrast for button text (about 3:1).
  - The success alert's dark-green text on bright green and the warning alert's brown text on amber are fine.
  - Error is `oklch(71% .194 13)` with a dark `-content`, also fine.
- Helper text (`.label`, `.fieldset-label`) is `base-content` at 60% via `color-mix`. It passes on white but sits close to the line on `base-200`.
- `text-base-content/40` for disabled text is well under 4.5:1, which is acceptable only because it's meant to read as disabled.
- `btn-disabled` drops all variant color, so a disabled primary is indistinguishable from a disabled secondary. That's clear as "unavailable", but the role is lost.
- Solid alerts use the full status color as the background. The fill is loud, and stacking four of them competes with the page's primary action. `alert-soft` is the calmer native option.

## Ideas for the Centric design system

Borrow:
- The role + `-content` pairing: every fill token ships with its on-color. It's the simplest contract that guarantees a text color for every surface. It also maps directly onto an APCA solve, where each `-content` is solved against its own fill.
- State colors as `color-mix` of the role token at runtime (hover = role + 7% black, soft = role mixed into base-100). Themes then only define base roles, and every state follows, including dark mode and density variants. This would shrink the semantic tier a lot across Vue, React, React Native (with a JS mix helper) and Angular.
- Opacity modifiers on text tokens (`text-base-content/70`) for secondary and disabled text. They're one token with derived emphasis levels. That fits a luminance-based emphasis system better than separate gray tokens.
- `--depth` and `--noise` as theme-level scalars. A single density or "flatness" knob that every component reads is a clean model for Centric's density modes. Do the same for `--size-field` and `--size-selector`.
- `aria-invalid` as a styling hook (the `validator` class). Accessibility state and visual state come from one attribute, which is ideal for bulk-edit grids.

Avoid:
- A flat token tier with no component layer. It's fine for daisyUI's scope, but Centric needs a component tier for tables (row hover, selected row, sticky header) that `base-200/300` can't express without overloading surfaces.
- Disabled styles that ignore the variant. In dense toolbars, users still need to tell which disabled control is the primary.
- Solid full-saturation status fills as the default alert. In data-dense screens, soft or outline status treatments carry status without shouting.

## Open issues

- Profile: `--color-secondary` lands on red, colliding with `--color-error`. Consider constraining the secondary hue away from status hues, or solving it as a neutral or tinted role.
- Profile: `-content` contrast for primary (4.1:1) and secondary (3.0:1) with the magenta test brand is below AA. Check the target for `-content` paths.
- Profile: consider solving `success`, `warning`, `neutral` and `base-300` so success and warning alerts, the active nav item, the avatar and borders follow the theme.
- The page compiles daisyUI through Tailwind. The probe uses the prebuilt CSS. Variable names and selectors are the same (`:root, [data-theme=…]`), so the solved values apply identically, but layer order differs slightly from the probe build.
