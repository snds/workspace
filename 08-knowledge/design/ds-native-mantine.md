---
tags: [design-systems, color, theming, tokens, mantine, emphasis-engine]
created: 2026-10-08
updated: 2026-10-08
status: working
confidence: medium
sources: [emphasis-engine native example build 2026-10-08, github.com/snds/emphasis-engine docs/systems/mantine.md, src/native/mantine.tsx]
related_skills: [ds-advisor, design-engineer]
related_projects: [emphasis-engine]
relations:
  relates-to:
    - "[[ds-native-theming-survey]]"
---

# Mantine 9 — how its color works, learned by theming it

## For future agent
- **TL;DR:** Per-color variant tokens (`filled`, `filled-hover`, `light`, `light-hover`, `light-color`, `outline`, `outline-hover`) with explicit state values; there's no runtime mixing. `primaryShade` is set per scheme. The stock `dimmed` text sits at about 3.3:1.
- **Key claims:** see "How its color works" and "What the solved theme reached" below. Each was observed by rendering the real components and injecting a solved theme (stock vs. themed, light and dark, 390 and 1280 wide).
- **Centric takeaways:** section "Ideas for the Centric design system"; consolidated in [[centric-ds-ideas-from-ds-survey]].
- **As of:** 2026-10-08 (dated: package versions below) · **Status:** current
- **Audience:** `for: all`

## At a glance

- Packages: `@mantine/core` 9.7.1, `@mantine/hooks` 9.7.1. MIT. Icons: `@tabler/icons-react` (what Mantine's own docs use).
- Page: `src/native/mantine.tsx`. Probe harness: `src/probe/mantine-harness.tsx`.
- Docs used:
  - https://mantine.dev/core/app-shell/ (fetched: header, `mode="static"`, burger + navbar pattern)
  - https://mantine.dev/styles/css-variables/ (the profile's source)
  - https://mantine.dev/core/button/, /core/alert/, /core/table/, /core/badge/, /core/grid/, /core/breadcrumbs/
  - https://ui.mantine.dev/ StatsGrid (the stat-card pattern: uppercase dimmed label, big value, teal/red delta with an arrow)
  - `node_modules/@mantine/core/styles.css` for the per-scheme variable definitions.

## How its color works

- Ten-shade palettes per color (`blue.0` … `blue.9`), defined in the JS theme. `primaryColor` defaults to `blue`. `primaryShade` defaults to 6 in light and 8 in dark.
- Variant tokens per color, generated from the palette:
  - `--mantine-color-<c>-filled`, `-filled-hover`
  - `--mantine-color-<c>-light`, `-light-hover`, `-light-color`
  - `--mantine-color-<c>-outline`, `-outline-hover`
  - `--mantine-color-<c>-text`
  - `--mantine-primary-color-*` mirrors the primary color's set.
- Page tokens: `--mantine-color-body`, `-text`, `-dimmed`, `-placeholder`, `-anchor`, `-default`, `-default-hover`, `-default-border`, `-default-color`, `-disabled`, `-disabled-color`, `-disabled-border`, `-error`.
- Where they live: `MantineProvider` writes the variables from the JS theme into a `<style>` tag at runtime, under `:root[data-mantine-color-scheme="light"]` and `…="dark"`. `styles.css` carries the same defaults. No wrapper element, so no scopes.
- Light/dark: `data-mantine-color-scheme` on `<html>`. The page passes `forceColorScheme` to the provider, as the harness does.
- States are separate tokens, not math. Filled hover is the next shade down (`blue-7` in light). Light hover is `blue-2` in light. Outline hover is a 5% rgba tint. Disabled has its own trio (`--mantine-color-disabled`, `-disabled-color`, `-disabled-border`). No `color-mix` anywhere in `styles.css`.
- Dark mode is not a lighter mirror. `-light` in dark is a solid, deep shade (`rgba(12, 50, 86, 1)` for blue) with near-white text. Light alerts in dark look like muted filled alerts.
- `c="teal"` on `Text` resolves to `--mantine-color-teal-text`. So color props stay on tokens.

## Building the native page

- Shell: `AppShell` with `header` and a `navbar` that is collapsed on desktop and opens from a `Burger` on mobile. That's the docs' recommended mobile pattern. `mode="static"`: the frame sizes to content and the host page scrolls, so a fixed header would only pin to the top of a frame that never scrolls. Static keeps AppShell's structure without fixed offsets. One side effect from the docs: in static mode AppShell's layout variables move from `:root` to the AppShell root. They're layout, not color, so the kit doesn't care.
- Header nav: core has no header-nav component. ui.mantine.dev headers use CSS modules, which would be hand-rolled styling. The nearest native thing is `Button size="compact-sm"`: `subtle` + `gray` for items, `light` primary for the active one. The mobile navbar uses `NavLink`, which is native.
- Layout: `Container size="xl"`, `Stack gap="xl"`, `SimpleGrid cols={{ base: 1, sm: 3 }}` for stats, `Grid` with `Grid.Col span={{ base: 12, md: 7 }}` / `5` for the body. Mantine 9 renamed Grid's `gutter` to `gap`.
- Breadcrumbs: `Anchor` items, the current page as plain `Text`.
- Tabs: default variant. The list is flex-wrap, so at 390px "Danger zone" wraps to a second row. That's Mantine's behavior, and it causes no overflow.
- Stats: `Paper withBorder` per stat, StatsGrid style. The delta is `c="teal"` / `c="red"` / `c="dimmed"` with a Tabler arrow colored by `--mantine-color-<c>-text`.
- Form: `Card withBorder`. Inputs carry their own `label`, `description`, and `error` props. Mantine puts the description above the input by default. The page leaves that alone. `Select` is the combobox (closed, so nothing portals). `Switch` with `description`. `Radio.Group` with a label and stacked `Radio`s. Actions are `Group justify="flex-end"` with `default` Cancel first and the filled submit last, as in Mantine's form examples.
- Buttons: `filled` (primary), `light` (secondary, matches the probe), `outline` (tertiary), `subtle` (ghost), `color="red"` filled (danger), filled `disabled`. `default` appears as the form's Cancel. All five variants are on the page.
- Status: `Alert variant="light"` with `color` green, blue, yellow, red, each with a Tabler icon. Badges use the same colors in `light`. Mantine has no status prop, only colors by convention.
- Table: `Table.ScrollContainer minWidth={600}`, `striped highlightOnHover withTableBorder`. Units right-aligned.
- Text: `Text`, `Text c="dimmed"`, `Text c="var(--mantine-color-disabled-color)"`, `Anchor`.

## What the solved theme reached

The profile solves 24 variables: `body`, `text`, `dimmed`, `placeholder`, `anchor`, `white`, the `default` quartet, the blue filled/light/outline sets, `primary-color-filled`, red filled/light, and `gray-light`.

Reached:
- Everything primary. The filled buttons, the active tab, switch, checkbox, radio, the light Duplicate button and active header nav item, link, breadcrumb link, the info alert, and the "In production" badge all go magenta in both modes. Mantine's per-variant tokens are flat custom properties, so the overrides land directly.
- Red filled and light (danger button, danger alert, Rejected badge). Values resolve close to stock.
- `text`. Dark-mode text goes from Mantine's soft `#c9c9c9` to `#ffffff`, which makes the whole dark page crisper and higher contrast than stock.

Didn't reach, or reached wrong:
- Green, yellow, teal palettes. The success and warning alerts, their badges, and the stat deltas are unchanged. Correct, since they're status.
- `--mantine-color-placeholder` in dark resolves to `#ffffff`, the same as `--mantine-color-text`. The email field's placeholder reads like a typed value. Stock is `#696969`. Engine bug: the placeholder step runs `away` from `--mantine-color-white`, and in dark that lands at the text end.
- `--mantine-color-blue-outline` resolves to `#36003d` in light and `#fde6ff` in dark. The outline Preview button reads as near-black or near-white, not brand. Its hue is gone. Likely the step is chained off the 5%-alpha `outline-hover` and lands at an extreme.
- `--mantine-color-disabled-color` isn't solved. The disabled-text line and the disabled button stay stock.
- Avatar `color="initials"` picks a palette by hashing the name (red here). It's unthemed by design.

Status leaks into brand, as with Chakra: blue is Mantine's default `primaryColor` and the conventional info color. Themed, info turns brand. Picking `cyan` for info would dodge it, but it would no longer match the probe (`alert-info` is blue) or Mantine's docs.

## Accessibility notes

- `--mantine-color-dimmed` (`#868e96` on white) is about 3.3:1. Mantine uses it for descriptions and the page description. That fails AA for body text.
- `--mantine-color-placeholder` (`#adb5bd`) is about 2.1:1 on white.
- The yellow light alert title and the yellow badge (`yellow-9` orange on `yellow-1`) are about 2.6:1. The title looks washed out.
- Error state: red border, red input text, red message. It relies heavily on hue. The message text helps.
- Dark mode stock text `#c9c9c9` on `#242424` is fine (about 10:1), but the page is low-key gray overall.
- In the themed dark run, the placeholder matches the value color (see above). That's an accessibility problem the theme introduced, not stock.

## Ideas for the Centric design system

- Borrow: per-color variant tokens (`filled`, `filled-hover`, `light`, `light-hover`, `light-color`, `outline`, `outline-hover`, `text`). It's the cleanest component-tier naming in this set. Each variant answers "what does this color look like as X," with hover baked in as its own value. It maps straight onto our component tier, and it's trivial to emit for Vue, Angular, and React Native because it's a flat list.
- Borrow: explicit state tokens (hover is a step, disabled is its own trio). No `color-mix`, no opacity. Hover stays predictable over striped and selected table rows, which matters in a data-dense PLM grid.
- Borrow: dark-mode "light" variants as solid deep shades instead of alpha tints. Alpha tints over dark surfaces go muddy when stacked (a light badge in a selected dark row). Solid values compose better.
- Borrow: `primaryShade` per scheme (`{ light: 6, dark: 8 }`). One knob for "how deep is brand in each mode." Our emphasis solver could expose the same idea per role.
- Avoid: `dimmed` at 3.3:1 as the default secondary text. In dense record-detail views, secondary text is half the screen. It has to clear 4.5:1.
- Avoid: input descriptions above the field by default. In bulk-edit forms, helper text between label and input pushes the field off its label row and breaks scan lines. Mantine lets you reorder (`inputWrapperOrder`), but the default is the wrong way round for us.
- Note for density: Mantine's `size` prop plus `compact-*` button sizes are a good model for a density mode, but they're per component. A theme-level `defaultProps` override per density is how you'd globalize it.

## Open issues

- Engine/profile: `--mantine-color-placeholder` solves to text color in dark mode.
- Engine/profile: `--mantine-color-blue-outline` loses its hue (near-black in light, near-white in dark).
- Profile: blue is both primary and info, so info follows brand when themed.
- `--mantine-color-disabled-color` and `--mantine-color-disabled` aren't solved.
- The header nav uses Buttons as the nearest native. A product using Mantine for real would likely write a CSS-module header like ui.mantine.dev's.
