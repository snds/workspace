---
tags: [design-systems, color, theming, tokens, carbon, emphasis-engine]
created: 2026-10-08
updated: 2026-10-08
status: working
confidence: medium
sources: [emphasis-engine native example build 2026-10-08, github.com/snds/emphasis-engine docs/systems/carbon.md, src/native/carbon.tsx]
related_skills: [ds-advisor, design-engineer]
related_projects: [emphasis-engine]
relations:
  relates-to:
    - "[[ds-native-theming-survey]]"
---

# IBM Carbon — how its color works, learned by theming it

## For future agent
- **TL;DR:** Role tokens (layer, field, border, text, interactive) set as full literal sets per theme zone class (`cds--white`, `cds--g100`). Contextual layer aliases step up per nesting level, and every state has its own token. Tags are hue-named (blue, green, red), not status-named, which mixes up info and brand when theming.
- **Key claims:** see "How its color works" and "What the solved theme reached" below. Each was observed by rendering the real components and injecting a solved theme (stock vs. themed, light and dark, 390 and 1280 wide).
- **Centric takeaways:** section "Ideas for the Centric design system"; consolidated in [[centric-ds-ideas-from-ds-survey]].
- **As of:** 2026-10-08 (dated: package versions below) · **Status:** current
- **Audience:** `for: all`

In this repo, Carbon's CSS prefix `cds--` and its `--cds-*` variables have nothing to
do with the "cds" page, which is Coinbase. They have nothing to do with the Centric
design system either.

## 1. At a glance

- Packages: `@carbon/react` 1.118.0 and `@carbon/styles` 1.117.0 (precompiled
  `css/styles.css`), plus `@carbon/icons-react`.
- License: Apache-2.0, per the `license` field of both packages.
- Docs: the page was already built from carbondesignsystem.com guidance: UI shell
  header, 2x grid, button set, inline notification, data table and tag. For this note
  I worked from the shipped `styles.css` and the shots. The relevant docs pages:
  - https://carbondesignsystem.com/elements/color/tokens/
  - https://carbondesignsystem.com/elements/themes/overview/
  - https://carbondesignsystem.com/components/button/usage/
  - https://carbondesignsystem.com/components/notification/usage/
  - https://carbondesignsystem.com/components/tag/usage/

## 2. How its color works

- **Three tiers.** Palette steps in `@carbon/colors` (`blue60`, `gray10`) feed
  role-named **theme tokens**. Examples: `background`, `layer-01..03`,
  `field-01..03`, `border-subtle-00..03`, `border-strong`, `border-interactive`,
  `text-primary/secondary/helper/placeholder/disabled/on-color`, `link-primary`,
  `focus`, `icon-*`, `support-error/success/warning/info`. A **component token** layer
  sits on top for the pieces that need their own values: `button-primary`,
  `button-secondary`, `button-tertiary`, `button-danger-primary`, `button-disabled`,
  `tag-background-<hue>` and `tag-color-<hue>`, `notification-background-<kind>`,
  `toggle-off`.
- **Zone classes are the themes.** `.cds--white`, `.cds--g10`, `.cds--g90` and
  `.cds--g100` each declare the full set of `--cds-*` variables as literals. Put one on
  `<html>` for the page theme, or on any element for a nested theme region. Light/dark
  is just which zone class is on `<html>` (white ↔ g100). No JS is involved.
- **Every use carries a fallback.** Component CSS is written as
  `var(--cds-border-interactive, #0f62fe)`. With no zone class you still get the white
  theme.
- **Layers are contextual aliases.** `.cds--tile` and most containers read
  `--cds-layer`, not `layer-01`. The `Layer` component's classes (`.cds--layer-one`,
  `.cds--layer-two`, …) remap it: `--cds-layer: var(--cds-layer-02, #fff)`. Nesting
  moves one step up the layer ladder, and hover, active and selected follow the same
  alias.
- **States are separate tokens.** Each button kind has `-hover` and `-active`, and
  layers and fields have `layer-hover-01` and `field-hover-01`. There's also
  `background-hover`, `background-active` and `button-disabled`. Carbon uses no
  opacity, color-mix or filters. Focus is a 2px `focus` outline with `focus-inset` on
  filled buttons.
- **Status.** The `support-*` tokens drive notification borders, icons and the toggle
  "on" track. Low-contrast notifications use `notification-background-<kind>`. Tags
  have hue types only (red, magenta, purple, blue, cyan, teal, green, gray, cool-gray,
  warm-gray, high-contrast, outline). Tags have no status semantics.

## 3. Building the native page

The page was already built. I checked it against the shots and made one fix.

- **UI shell.** `Header` with `HeaderName`, `HeaderNavigation`/`HeaderMenuItem`
  (Suppliers active) and `HeaderGlobalAction` icons. Below that, a 16-column `Grid`
  (4 columns on sm, 8 on md), productive type classes, and `Stack` for vertical rhythm.
- **Form.** In a `Tile`: `TextInput` (including the `invalid` state), `Select`, a
  `Toggle` with Off/On labels, `Checkbox` and a horizontal `RadioButtonGroup`.
- **Buttons.** A `ButtonSet` flush with the tile's bottom edge, secondary left and
  primary right. That's Carbon's container-edge button pattern. It stacks on small
  screens. The hierarchy row maps the scene like this:
  - primary → `primary`
  - secondary → `secondary` (dark gray)
  - tertiary → `tertiary` (the outline)
  - ghost → `ghost`
  - danger → `danger`
  - disabled → `disabled`
- **Status.** `InlineNotification lowContrast` for the alerts (success, info, warning,
  error). `DataTable` uses `Tag size="sm"` for status: green, blue, warm-gray and red.
  Carbon has no yellow or orange tag, so warning goes to warm-gray, which carries no
  warning meaning. Carbon's docs suggest status *indicators* (an icon plus text) for
  this use, not tags. A follow-up could switch to those.
- **Fix made.** The tab row sat flush against the stat tiles. I added a 2rem bottom
  margin to the heading column.
- **Missing.** Nothing major. Stats are composed from `Tile` and type classes, because
  Carbon has no stat component.

## 4. What the solved theme reached

The profile writes 42 `--cds-*` variables on `<html>`. `<html>` carries the zone class,
so the overrides win over it directly, and the kit added no redefinition rules: the
`ee-theme` style stayed empty. Measured on the themed light page:

Reached:
- **Brand.** Primary buttons, including the ButtonSet's Save (`button-primary`). The
  tertiary outline (`button-tertiary`). Links, the ghost button text and breadcrumb
  links (`link-primary`). The selected tab underline and the active shell-nav underline
  (`border-interactive`, measured `rgb(179,13,199)`). Focus.
- **Neutral steps.** Page background. Tiles and the table body (`--cds-layer`, which
  moved to a faint brand-tinted neutral, `rgb(250,240,250)`). Fields, borders and all
  text tokens. The secondary button.
- **Info and danger.** The info notification background (neutral step) and border
  (`support-info`, a solved darker blue). The error notification. The danger button.
- **Tags.** The **blue tag** ("In production") turned magenta. The profile solves
  `tag-background-blue` and `tag-color-blue` from the *brand* role. Carbon's primary is
  blue, so the profile reads blue tags as brand. On this page that maps an info status
  onto brand. Treat it as a profile issue, not a page issue.

Didn't reach:
- **The shell header background.** It stays white or g100. It reads `--cds-background`,
  which is solved, but the solved page color equals the stock one at this brand, so
  nothing visibly changed. Only the nav underline moved.
- **The table header row** (`--cds-layer-accent`, stock `#e0e0e0`) isn't in the
  profile. The gray header no longer matches the tinted body.
- **Tags other than blue and gray.** Green, warm-gray and red keep stock values, as do
  the success and warning notification backgrounds.
- **The toggle "on" track.** It uses `support-success`, which is solved but stays green
  by design, so it's correct that it didn't go brand. The checked checkbox fills with
  `icon-primary`, which is solved as near-black neutral.
- **Disabled buttons** (`button-disabled`, `text-on-color-disabled`) aren't in the
  profile.
- **Hover and active steps** (`layer-hover`, `field-hover`, `background-hover`) are
  only partly covered. Button hover and active are solved. Layer and field hovers fall
  back to stock grays.

Nested zones and layers:
- A `cds--g100` region inside a light page redefines every variable as a literal. The
  kit's `redefinitions()` pass sees that and forces the *root* (light) solved value onto
  the zone. The dark island would then render with light values. This page avoids
  nested zones for that reason. A real fix needs per-zone solving.
- `Layer` nesting has the opposite problem. `.cds--layer-two` remaps `--cds-layer` to
  `var(--cds-layer-02)`. That's a `var()` remap, which the kit deliberately leaves
  alone, and `layer-02` isn't solved, so a nested layer would fall back to stock gray.
  The profile only solves the contextual alias.

## 5. Accessibility notes (stock)

- Placeholder text (`text-placeholder`, 40% of gray-100) on `field-01` is about
  2.8:1. That's below 4.5:1, a known Carbon trade-off.
- Disabled text and disabled buttons are about 1.7:1. That's exempt from WCAG, but very
  faint.
- The toggle's "on" track is `support-success` green on white, about 3.2:1. It barely
  meets the 3:1 non-text minimum, and status green is reused for "on".
- Warning as a warm-gray tag carries no color meaning. It relies entirely on the label.
- At 390px, low-contrast inline notifications keep a max width and don't fill the
  column. That's cosmetic, not a contrast problem.

## 6. Ideas for the Centric design system

Borrow:
- **Contextual layer aliases** (`--cds-layer` remapped by `.layer-one/two/three`).
  Centric's record-detail pages nest panels inside drawers inside tables. A container
  that bumps one step up the neutral scale, without each component knowing its depth,
  is exactly the semantic tier doing its job. It would map onto Radix neutral steps
  1→2→3.
- **Zone classes for nested themes.** One class swaps the whole variable set for a
  region, like a dark header or an inverse toolbar in a light app. This works the same
  in Vue, React and Angular because it's only CSS. React Native would need an
  equivalent provider.
- **Explicit state tokens per surface** (`layer-hover-01`, `field-hover-01`,
  `button-primary-active`). Every state is a tunable, contrast-checkable token rather
  than an opacity guess. That fits a perceptual solver.
- **Fallback literals in every `var()`.** Components still render correctly when a
  consumer forgets the theme import. That's useful for Centric's embedded and
  partner-hosted surfaces.

Avoid:
- **Hue-named tags as the status mechanism.** "blue" means info to one team and brand
  to another, and Carbon has no yellow at all. Centric tags should take a status intent
  (`success | info | warning | danger | neutral`) mapped to semantic tokens, with hue
  tags kept separately for categorical data like collections and seasons.
- **Zone themes defined as full literal sets.** Every zone repeats ~300 literals. A
  theme engine (or a brand override) has to solve and write each zone separately.
  Defining zones as remaps onto a smaller set of semantic roots would make one solve
  cover them all.
- **Square, low-contrast placeholders in dense forms.** Fine for IBM, but Centric's
  bulk-edit grids put placeholders in many cells. Keep placeholder contrast at or above
  4.5:1.

## 7. Open issues

- **The profile maps `tag-*-blue` to brand.** On this page that turns an info tag
  magenta. Consider solving blue tags from the info role, or leaving them stock.
- **The profile omits `layer-accent`** (table header), the other tag hues, success and
  warning notification backgrounds, and `button-disabled`.
- **Nested zone classes are re-themed with root values**, and `Layer` nesting falls
  back to stock. Both need per-zone or per-layer solving.
- **The page reads `matchMedia` once**, so the stacked ButtonSet doesn't respond to a
  resize. That's fine in the frame, which loads at a fixed width.
- **Status could use Carbon's status indicator pattern** instead of tags.
