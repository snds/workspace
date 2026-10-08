---
tags: [design-systems, color, theming, tokens, fluent, emphasis-engine]
created: 2026-10-08
updated: 2026-10-08
status: working
confidence: medium
sources: [emphasis-engine native example build 2026-10-08, github.com/snds/emphasis-engine docs/systems/fluent.md, src/native/fluent.tsx]
related_skills: [ds-advisor, design-engineer]
related_projects: [emphasis-engine]
relations:
  relates-to:
    - "[[ds-native-theming-survey]]"
---

# Fluent 2 — how its color works, learned by theming it

## For future agent
- **TL;DR:** FluentProvider writes alias tokens (`colorNeutral*`, `colorBrand*`, `colorStatus*`) on its own div. Each role has separate Rest/Hover/Pressed/Selected/Disabled tokens and a compound-brand family for brand-on-neutral marks. Badge and Field errors read palette tokens directly, so a theme can't reach them. There is no danger button.
- **Key claims:** see "How its color works" and "What the solved theme reached" below. Each was observed by rendering the real components and injecting a solved theme (stock vs. themed, light and dark, 390 and 1280 wide).
- **Centric takeaways:** section "Ideas for the Centric design system"; consolidated in [[centric-ds-ideas-from-ds-survey]].
- **As of:** 2026-10-08 (dated: package versions below) · **Status:** current
- **Audience:** `for: all`
- **Update 2026-10-08 (profile fixes):** Profiled from the full native page: compound brand (radio dot, checkbox) and the success and warning tokens are solved.

## At a glance

- Package: `@fluentui/react-components` 9.74.9. Icons: `@fluentui/react-icons` 2.0.343. Styling engine: `@griffel/react` 1.7.8.
- License: MIT for all three. Icons are MIT too, and come in as a dependency of react-components. The app's package.json does not list `@fluentui/react-icons`, so the page imports a transitive dependency.
- Docs used:
  - https://fluent2.microsoft.design/components/web/react/core/button/usage
  - Component props and token usage were read from the installed packages (types and style files).

## How its color works

- Two tiers. Brand ramp and palette ramps (`colorPaletteRedForeground1`, `colorPaletteGreenBackground2`) sit under alias tokens (`colorNeutralForeground1`, `colorBrandBackground`, `colorCompoundBrandStroke`, `colorStatusDangerBackground1`).
- Tokens are camelCase CSS variables (`--colorNeutralBackground1`). `FluentProvider` writes them in a generated class on its own root div, not on `:root`. Nested providers can re-theme a subtree.
- Components read them through the `tokens` object (`tokens.colorNeutralForeground2` resolves to `var(--colorNeutralForeground2)`), compiled into atomic classes by Griffel.
- Light and dark are two JS theme objects (`webLightTheme`, `webDarkTheme`) handed to the provider. No class or attribute on `<html>`.
- States are separate tokens, not math: `colorBrandBackgroundHover`, `...Pressed`, `...Selected`, `colorNeutralForegroundDisabled`, `colorNeutralBackgroundDisabled`. No opacity or color-mix.
- "Compound brand" tokens are a separate family for brand color drawn on top of neutrals: checkbox fill, radio dot, tab underline, switch track. They differ from `colorBrandBackground` in dark mode (a lighter brand step).

## Building the native page

- Layout: a 48px app bar, then a centered column with Fluent's 4px spacing ramp (`spacingVerticalXXL`, `spacingHorizontalL`). Cards sit on `colorNeutralBackground2`, which is how Fluent separates surfaces.
- Type ramp components: `Title1` for the page, `Subtitle1` for card titles, `Title2` for stat values, `Body1` and `Caption1` for text. Rendered as `h1`/`h2`, they keep browser margins; reset to 0.
- Forms: `Field` carries label, hint and `validationState="error"` + `validationMessage`. Switch hint goes on the wrapping Field.
- Buttons: one primary per area, placed first (left in LTR), per the button usage page. Actions row uses primary, secondary, outline, subtle, then a disabled primary.
- Destructive action: Fluent has no danger appearance. The guidance is a neutral button that opens a confirmation dialog whose buttons answer the question ("Delete" / "Cancel"). "Delete workspace" is a secondary button with a delete icon.
- Status: `MessageBar` intents success, info, warning, error. Table status uses `Badge appearance="tint"` with success, informative, warning, danger. Fluent's `informative` badge and `info` message bar are neutral gray, not blue. That is Fluent's convention, not a mistake.
- Substitutions: Fluent has no app-header component. The bar is tokens + `TabList size="small"` for nav + subtle icon `Button` + `Avatar`. `Nav`/`NavDrawer` exist but are vertical side nav. No stat component: Cards with type ramp text.
- Table: `Table` (not DataGrid). It scrolls inside its own container under 560px.

## What the solved theme reached

Compared stock and magenta-themed shots, light and dark.

- Reached: primary buttons, link, tab and nav underline, switch track, checkbox fill, focus ring, neutral surfaces (canvas and cards picked up a faint magenta tint), neutral text, strokes. Dark mode followed too.
- The info MessageBar went pink. It is built on neutral tokens (`colorNeutralBackground3`), and the solved neutrals are tinted with the brand. So "info" picks up the brand hue by design in Fluent.
- Did not reach:
  - Radio dot and checked ring stayed Fluent blue. Radio draws them with `colorCompoundBrandForeground1` (+Hover, Pressed). That token is missing from `profiles/generated/fluent.json`. The profile has `colorCompoundBrandStroke` and `...Background` but not `...Foreground1`.
  - Badges kept stock colors. Tint badges use palette tokens (`colorPaletteGreenBackground1`, `colorPaletteRedForeground2`, ...). The profile has none of them.
  - Success and warning MessageBars kept stock colors. Only the danger status tokens are in the profile (`colorStatusDanger*`). The error bar moved a little (#fdf3f1 solved).
  - Field error text and border use `colorPaletteRedForeground1`/`colorPaletteRedBorder2`, not status tokens, so they stayed stock.
  - Disabled button and disabled text use `colorNeutralForegroundDisabled` / `colorNeutralBackgroundDisabled`. Not in the profile, so they stayed stock gray.
- No portals or shadow DOM were involved. Everything here renders inside the provider div, which the kit scopes.

## Accessibility notes

- Disabled text (`colorNeutralForegroundDisabled`, #bdbdbd on white) is about 1.9:1. Fine for disabled by WCAG, but the "Disabled text sits back" line almost vanishes.
- Caption1 helper text in `colorNeutralForeground2` on white passes easily. Fine.
- The neutral info MessageBar relies on its icon to read as info. Color alone doesn't separate it from a plain panel.
- Warning badge text (dark yellow on pale yellow) is the weakest of the four in light mode but still readable.

## Ideas for the Centric design system

- Borrow: separate state tokens per role (`Rest`/`Hover`/`Pressed`/`Selected`/`Disabled`). This is the third tier done well. It ports cleanly to Vue, Angular and React Native because it's just named values, no runtime color math.
- Borrow: the compound-brand family. Brand-on-neutral marks (checkbox, radio, tab underline) get their own token so dark mode can lighten them without touching filled buttons. Centric's dense tables are full of checkboxes, so this matters.
- Borrow: a provider that writes tokens on a subtree. It's how you'd theme a single panel (for example a supplier portal embed) or a density mode without touching `:root`.
- Borrow: `Field` as the one wrapper that owns label, hint and validation. One API for every input type keeps bulk-edit forms consistent.
- Avoid: palette tokens used directly by components (Badge, Field error). They skip the semantic tier, so a theme can't reach them. In Centric's model every component color should go through a semantic token.
- Avoid: no danger button. Enterprise PLM has lots of destructive bulk actions (delete styles, reject samples). A real destructive appearance is clearer than relying on a confirm dialog alone.

## Open issues

- Profile gaps to fix upstream: `colorCompoundBrandForeground1` (+Hover/Pressed), success and warning status tokens, `colorNeutralForegroundDisabled` / `colorNeutralBackgroundDisabled`. Palette tokens are a judgment call.
- `@fluentui/react-icons` should be declared in package.json if the page keeps it.
- The 390px header scrolls its nav sideways. A real product would collapse it into a hamburger + `NavDrawer`.
