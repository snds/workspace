---
tags: [design-systems, color, theming, tokens, atlassian, emphasis-engine]
created: 2026-10-08
updated: 2026-10-08
status: working
confidence: medium
sources: [emphasis-engine native example build 2026-10-08, github.com/snds/emphasis-engine docs/systems/atlassian.md, src/native/atlassian.tsx]
related_skills: [ds-advisor, design-engineer]
related_projects: [emphasis-engine]
relations:
  relates-to:
    - "[[ds-native-theming-survey]]"
---

# Atlassian Design System — how its color works, learned by theming it

## For future agent
- **TL;DR:** Dotted design tokens (`color.background.brand.bold.hovered`) map 1:1 to `--ds-*` variables and a typed `token()` helper; emphasis and state live in the name. The library ships as many small packages; only a few were installed here, so several pieces were composed from primitives. The licenses are Apache-2.0.
- **Key claims:** see "How its color works" and "What the solved theme reached" below. Each was observed by rendering the real components and injecting a solved theme (stock vs. themed, light and dark, 390 and 1280 wide).
- **Centric takeaways:** section "Ideas for the Centric design system"; consolidated in [[centric-ds-ideas-from-ds-survey]].
- **As of:** 2026-10-08 (dated: package versions below) · **Status:** current
- **Audience:** `for: all`
- **Update 2026-10-08 (profile fixes):** Fixed: dark `--ds-border` keeps its 11% white; primary buttons take the brand (`background.brand.bold` is the solid); danger and info keep their hues.

## At a glance

- Packages used (from node_modules): `@atlaskit/tokens` 20.4.0, `@atlaskit/primitives` 22.5.4, `@atlaskit/button` 25.4.7, `@atlaskit/textfield` 10.2.6, `@atlaskit/toggle` 17.3.4, `@atlaskit/checkbox` 19.3.0, `@atlaskit/icon` 38.0.2.
- `primitives` and `icon` come in as dependencies. The app's package.json lists only button, checkbox, textfield, toggle and tokens.
- License: every installed `@atlaskit/*` package says `Apache-2.0` in package.json. All have an Apache 2.0 LICENSE file except `platform-feature-flags` and `top-layer`, which ship no LICENSE file but declare Apache-2.0. I found no "Atlassian Design Guidelines" or other non-Apache license text. That includes `@atlaskit/icon`, whose older versions caused worry.
- License caveats worth knowing:
  - Apache 2.0 grants no trademark rights (section 6). The Atlassian name, logos and look are still Atlassian's.
  - The fonts named in the typography tokens are not shipped here: "Atlassian Sans", "Atlassian Mono", "Charlie Display/Text". Pages fall back to system fonts.
  - Transitive deps: `@atlaskit/feature-gate-js-client` pulls in Statsig's SDK (`@statsig/js-client` 3.30.2, ISC). `@compiled/react` is Apache-2.0 and `@emotion/react` is MIT.
- Not installed, and not added: tabs, breadcrumbs, heading, select, radio, form, section-message, lozenge, dynamic-table, avatar, page-header, banner, navigation.
- Docs used:
  - https://atlassian.design/components/button/usage
  - https://atlassian.design/components/lozenge/usage
  - https://atlassian.design/components/section-message/usage
  - Token roles and primitives props were read from the installed packages' type definitions.

## How its color works

- Tokens are dotted names (`color.background.brand.bold`, `color.text.subtle`, `elevation.surface.raised`). The CSS variable is the name with dots → dashes, prefixed `--ds-` (`--ds-background-brand-bold`). `token("color.text")` returns `var(--ds-text, <fallback>)`.
- Naming encodes role, emphasis and state: `color.background.danger` (subtle) → `.danger.bold` → `.danger.bold.hovered` / `.pressed`. Text, icon and border have parallel families.
- `setGlobalTheme({ colorMode })` sets `data-color-mode` and `data-theme` on `<html>` and injects one `<style>` per theme (light, dark, spacing, typography, shape). Variables live on `:root` under those attribute selectors. No provider div.
- Components compile to static CSS (Compiled, or Emotion for primitives) with `var(--ds-…, #fallback)`. So every component color is reachable through root variables.
- States are separate tokens: `.hovered`, `.pressed`, `color.background.selected`, `color.text.disabled`, `color.background.disabled`. No opacity or color-mix.
- Elevation is its own family: `elevation.surface`, `.surface.raised`, `.surface.overlay`, each paired with `elevation.shadow.*`.
- Inverse text is automatic: `Text` inside a `Box` with a bold background switches to `color.text.inverse`.

## Building the native page

- Layout: primitives only (`Box`, `Stack`, `Inline`, `Pressable`, `Anchor`, `Text`) on the 8px space scale (`space.100` = 8px). Responsive columns use `xcss` with `media.above.sm` / `media.above.md` (48rem, 64rem).
- Buttons: one primary per area. The button usage page says single-page forms left-align their buttons with the primary furthest toward the alignment, so the primary sits first. The actions row uses primary, default, default, subtle, danger, and a disabled primary. ADS has no outline appearance, so tertiary is `default`.
- ADS says avoid disabled buttons, especially in forms. The disabled one is only there because the scene asks for it.
- Status: semantic token families. success → success, info → information, warning → warning, danger → danger. These match the lozenge semantics (success, inprogress, moved, removed) and the section message appearances.
- Composed from primitives + tokens, because the package isn't installed:
  - App header: product name, subtle `Button`s with `isSelected`, `IconButton`s. Below 48rem the nav hides behind a menu `IconButton`.
  - Breadcrumbs: `Inline` with `separator="/"`, `Anchor` in `color.link`.
  - Headings: plain `h1`/`h2` with `font: token("font.heading.large")`.
  - Tabs: `Pressable role="tab"` with `color.text.selected` and a `color.border.selected` underline.
  - Select: a native `<select>` in `color.background.input` / `color.border.input`.
  - Radio: native radios with `accent-color: color.background.selected.bold`.
  - Field labels, helper and error: `<label>` in `font.body.small` semibold `color.text.subtle`, helper in `color.text.subtlest`, error in `color.text.danger` with the status-error icon.
  - Section messages: `Box` in `color.background.<status>` with the status icon in `color.icon.<status>`, title, body.
  - Lozenges: `Box` in `color.background.<status>` + `Text` bold in `color.text.<status>`.
  - Table: plain `<table>` with dynamic-table's head treatment (subtle bold labels, 2px `color.border`).
- These compositions use the tokens the real components use, but they are not the components. Spacing and radii approximate them.
- `@atlaskit/icon` glyphs ship as CommonJS only. Vite can hand back `{ default: Icon }` instead of the component, so the page unwraps it.

## What the solved theme reached

Compared stock and magenta-themed shots, light and dark.

- Reached: links (breadcrumb, PO numbers, text link), checkbox fill and the radio accent (`--ds-background-selected-bold`), surfaces, text, input backgrounds and borders, focus ring.
- Did not reach:
  - **Primary buttons stayed Atlassian blue.** Button reads `--ds-background-brand-bold` (+hovered/pressed). That token is not in `profiles/generated/atlassian.json`. This is the biggest gap.
  - Selected nav button, selected tab text and underline stayed blue. They use `--ds-background-selected`, `--ds-text-selected` and `--ds-border-selected`, which are not in the profile.
  - Success and warning lozenges and section messages kept stock colors. `--ds-background-success`, `--ds-background-warning`, `--ds-text-success` and `--ds-text-warning` are not in the profile.
  - Toggle stays green. It uses `background.success.bold`, which is in the profile, so the solved value is still a green.
- Reached, but wrongly:
  - `--ds-background-danger` and `--ds-background-information` both solve to the same brand-tinted neutral (#f7edf7 light, #312a31 / #2f2930 dark). The danger and info section messages lose their red and blue and turn pink-gray. Status is being mapped onto brand.
  - The likely cause: the probe harness builds its "alert" and "badge" by hand from those tokens, and the profile treated them as surfaces.
  - Dark `--ds-border` solves to `rgb(255 252 255 / 0%)`, fully transparent. Default buttons lose their outline, and the tab track and table row dividers disappear in dark themed.
- No portals or shadow DOM involved. Everything themes from `<html>`, so there are no scopes.

## Accessibility notes

- Disabled text (`color.text.disabled`) is very faint in both modes. Fine by WCAG for disabled, but hard to see.
- Lozenge text in light mode (for example green on pale lime) is small bold text. It reads, but it's the tightest contrast on the page.
- Stock is otherwise strong: the error field has a 2px red border plus an icon and text, not color alone.
- Themed dark: transparent borders make default buttons look like subtle buttons, so the button hierarchy collapses. That one is a theming bug, not a stock-theme problem.

## Ideas for the Centric design system

- Borrow: dotted token names that map 1:1 to CSS variables and to a typed `token()` helper with fallbacks. One name works in Vue, Angular, React and React Native, and typos fail at compile time (`token("border.radius")` was a type error here).
- Borrow: emphasis in the name (`subtle` → `bold` → `bolder`) plus state suffixes (`.hovered`, `.pressed`). This is the semantic tier spelled out, and it lines up well with an emphasis-driven solver.
- Borrow: the `elevation.surface.*` + `elevation.shadow.*` pairing. A dense PLM screen stacks table, side panel, popover and modal. Paired surface and shadow tokens keep those layers consistent in dark mode.
- Borrow: automatic inverse text inside bold backgrounds (the surface context in primitives). It removes a whole class of "white text on light chip" bugs in status-heavy tables.
- Borrow: primitives with a constrained `xcss` that only accepts tokens. It enforces the token model at the type level.
- Avoid: splitting the system into dozens of packages with deep CommonJS-only entry points (icons). A cross-framework system should ship ESM with explicit `exports`.
- Avoid: feature-flag clients (Statsig) as runtime deps of a component library. That doesn't belong in an enterprise customer's bundle.

## Open issues

- Profile fixes needed (not done; the brief forbids editing profiles):
  - Add `--ds-background-brand-bold` (+hovered/pressed) and the `selected` family (`background.selected`, `text.selected`, `border.selected`).
  - Add the success and warning background and text tokens.
  - Stop mapping `background.danger` / `background.information` to a brand-tinted neutral.
  - Floor dark `--ds-border` alpha above 0.
- The probe harness should use real status tokens in the way components do. It may be what taught the profile the wrong roles.
- Installing tabs, breadcrumbs, select, radio, section-message, lozenge, dynamic-table, heading and avatar would replace most compositions with the real components.
- `@atlaskit/primitives` and `@atlaskit/icon` should be declared in package.json if the page keeps them.
