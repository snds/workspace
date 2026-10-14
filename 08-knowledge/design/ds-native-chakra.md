---
tags: [design-systems, color, theming, tokens, chakra, emphasis-engine]
created: 2026-10-08
updated: 2026-10-08
status: working
confidence: medium
sources: [emphasis-engine native example build 2026-10-08, github.com/snds/emphasis-engine docs/systems/chakra.md, src/native/chakra.tsx]
related_skills: [ds-advisor, design-engineer]
related_projects: [emphasis-engine]
relations:
  relates-to:
    - "[[ds-native-theming-survey]]"
---

# Chakra UI 3 — how its color works, learned by theming it

## For future agent
- **TL;DR:** Every palette has the same slot set (`solid`, `contrast`, `fg`, `subtle`, `muted`, `emphasized`, `border`, `focusRing`). `colorPalette` is an inherited context variable that re-hues every recipe inside a container. Hover is `color-mix()`, and disabled is opacity only.
- **Key claims:** see "How its color works" and "What the solved theme reached" below. Each was observed by rendering the real components and injecting a solved theme (stock vs. themed, light and dark, 390 and 1280 wide).
- **Centric takeaways:** section "Ideas for the Centric design system"; consolidated in [[centric-ds-ideas-from-ds-survey]].
- **As of:** 2026-10-08 (dated: package versions below) · **Status:** current
- **Audience:** `for: all`
- **Update 2026-10-08 (profile fixes):** Changed: blue is info now, so the profile has no brand palette. Chakra's default palette is gray; a page has to set `colorPalette` before the brand pick drives anything.

## At a glance

- Package: `@chakra-ui/react` 3.37.0 (with `@emotion/react` 11.14). MIT.
- Page: `src/native/chakra.tsx`. Probe harness: `src/probe/chakra-harness.tsx`.
- Docs used:
  - https://chakra-ui.com/docs/components/stat (fetched: part names, up/down indicators)
  - https://chakra-ui.com/docs/theming/semantic-tokens (the profile's source)
  - https://chakra-ui.com/docs/components/button, /field, /alert, /table, /breadcrumb, /tabs, /card
  - The shipped recipes in `node_modules/@chakra-ui/react/dist/esm/theme/` were the final word on what each variant paints. Reading them was faster than the docs and more honest.

## How its color works

- Two tiers. Raw palettes (`gray.50` … `gray.950`, `blue.*`, `red.*`, and so on) sit under semantic tokens.
- Semantic tokens come in two families:
  - Page-level: `bg`, `bg.subtle`, `bg.muted`, `bg.emphasized`, `bg.panel`, `fg`, `fg.muted`, `fg.subtle`, `border`, `border.emphasized`, plus status tokens like `fg.success` and `fg.error`.
  - Per palette: `<palette>.solid`, `.contrast`, `.fg`, `.subtle`, `.muted`, `.emphasized`, `.border`, `.focusRing`. Every palette has the same seven slots.
- `colorPalette` is the trick. Recipes never name a hue. They paint `colorPalette.solid`, `colorPalette.fg`, and so on. Setting `colorPalette="red"` on an element writes `--chakra-colors-color-palette-*` on that element as `var(--chakra-colors-red-*)`. Children inherit.
- The global CSS sets `html { colorPalette: gray }`. So the default "primary" button is near-black in light and white in dark. Chakra's out-of-box brand is neutral.
- Variables: `ChakraProvider` turns the JS system object (`defaultSystem`) into CSS custom properties through Emotion at runtime. They land on `:root` for light and on `.dark` for dark. The provider renders no wrapper element, so there are no scopes.
- Light/dark: the `.dark` class on `<html>` (Chakra recommends `next-themes` to manage it; the page toggles the class directly, like the harness).
- States:
  - Hover on solid is `colorPalette.solid/90`, which compiles to `color-mix(in srgb, … 90%, transparent)`. No separate hover token.
  - Hover on subtle/surface steps to the next slot (`subtle` → `muted`). Outline and ghost hover to `subtle`.
  - Disabled is the `disabled` layer style: `opacity: 0.5`. No disabled color tokens.
  - Focus is `colorPalette.focusRing` as an outline.

## Building the native page

- Layout: `Container maxW="7xl"`, `Stack` for vertical rhythm, `SimpleGrid` for stats, `Grid` with `minmax(0, …)` tracks for the two-column body. Everything is style props on primitives, which is the Chakra way.
- Header: Chakra has no app-header or nav component. Its templates build one from `Flex`/`HStack` with plain `Link`s, so the page does that. Active item is `fg` and semibold, the rest `fg.muted`. The nav hides below `md` (`hideBelow`). There's no Chakra burger or drawer nav to fall back to without building one, so the phone layout has no main nav. Called out under open issues.
- Breadcrumb: `Breadcrumb.Root/List/Item/Link/Separator/CurrentLink`.
- Tabs: `variant="line"`. The list gets `overflowX="auto"` so four tabs scroll inside themselves at 390px.
- Stats: `Card.Root size="sm"` around `Stat.Root` with `Stat.UpIndicator` / `Stat.DownIndicator`. The third stat has no direction, so no indicator.
- Form: a `Card` with `Card.Header`/`Body`/`Footer`. Each control sits in `Field.Root` with `Field.Label`, `Field.HelperText`, and `Field.ErrorText`. `invalid` goes on `Field.Root`. Region uses `NativeSelect` rather than the portal-based `Select`; it needs no collection and nothing portals. Radio group is wrapped in `Fieldset` with a legend.
- Buttons: Chakra's card form examples end-align actions in the footer with the primary last. The action row steps down: `solid`, `subtle`, `outline`, `ghost`, then `solid` + `colorPalette="red"` for danger, then disabled `solid`. Secondary uses `subtle` because that's what the probe measured as button-secondary. `surface` (subtle fill plus an inset ring) is a sibling of `subtle`. The scene has no seventh action, so `surface` is left out.
- Status: `Alert.Root status=…` (success, info, warning, error) with the default `subtle` variant. Table badges use the matching palettes: green, blue, orange, red. Orange, not yellow, because that's the palette Chakra's own warning alert uses.
- Table: `Table.ScrollArea` with a border, `Table.Root size="sm" interactive`, units right-aligned.
- Text: `Text` with `fg`, `fg.muted`, `fg.subtle`. `Link variant="underline" colorPalette="blue"`, matching the harness.
- Icons: Chakra docs use `react-icons`, which isn't installed. The bell is from `@tabler/icons-react` inside a native `IconButton`. Alert and stat icons are Chakra's own.

## What the solved theme reached

The profile solves 22 variables: page tokens (`bg`, `bg.panel`, `bg.emphasized`, `fg`, `fg.muted`, `border`, `border.emphasized`), the default `color-palette-*` slots (neutral), `blue.subtle/fg/focusRing` (brand), and `red.subtle/fg/focusRing/solid` (danger).

Reached:
- Page surfaces and text. `bg` and `fg` pick up a faint brand tint (dark bg `#09090b` → `#0b080b`). Visible mostly in dark mode.
- Every component that uses the default palette: the primary/solid buttons, checkbox, switch, radio, the active tab indicator. They stay near-black / near-white, now tinted. Expected: the default palette is neutral, and the profile treats it that way.
- Anything on the blue palette's `subtle` and `fg` slots. The link, the info alert, and the "In production" badge turn magenta.
- Danger: `red.solid` and `red.fg`. They resolve close to stock, so the change is hard to see.

Didn't reach:
- `blue.solid`, `blue.muted`, `blue.emphasized`, `blue.border`, `blue.contrast`. They aren't in the profile. A `solid` button with `colorPalette="blue"` would stay stock blue `#2563eb`. Nothing on the page uses that, but a product that brands with `colorPalette="blue"` would see half its brand move and half stay.
- Green and orange palettes, and the semantic status tokens (`fg.success`, `fg.error`). The stat trend arrows, success and warning alerts, and those badges are untouched. Correct: they're status, not brand.
- `fg.subtle` isn't solved. The disabled-text line stays stock.
- Anything that sets `colorPalette` explicitly redefines `--chakra-colors-color-palette-*` on its own element as a `var()` remap. The kit rightly leaves remaps alone, so those elements follow the named palette, not the root override.

Status leaks into brand: Chakra's info status is the blue palette, and the profile uses blue as the brand palette. Themed, the info alert and the info badge go magenta. That's the profile choosing blue as brand, not the page. Flagged below.

## Accessibility notes

- `fg.subtle` (`#a1a1aa` on white) is about 2.6:1. Fine for disabled text, which is all the page uses it for. It's a trap if someone uses it for helper copy.
- Placeholder is `fg.muted/80`. Close to the 4.5:1 line on white. Readable, but only just.
- Disabled is plain 50% opacity. The disabled solid button reads as a mid-gray button, not clearly unavailable, and its contrast depends on whatever sits behind it.
- Field error text is small red text. The red border helps, and Chakra wires `aria-invalid` through `Field.Root`.
- The phone layout has no main nav (see Building).

## Ideas for the Centric design system

- Borrow: one fixed slot set per palette (`solid`, `contrast`, `fg`, `subtle`, `muted`, `emphasized`, `border`, `focusRing`). Every hue answers the same seven questions. A component recipe then names slots, never hues. That maps well onto our semantic → component tiers and onto Radix-style 12-step scales: each slot is a pointer to a step.
- Borrow: `colorPalette` as an inherited context variable. One attribute on a container re-hues every recipe inside it. For a PLM product, that's a clean way to do status-colored row groups, a "danger zone" panel, or per-vertical accents (fashion, food, engineering) without per-component props. It's plain CSS custom-property inheritance, so it ports to Vue, Angular, and React Native style objects the same way.
- Borrow with care: hover as `color-mix(solid, transparent 10%)`. Zero extra tokens. But the hover color then depends on the surface behind it. In dense tables with zebra or selected rows, that drifts. We'd want a solved hover step instead.
- Avoid: neutral default palette as "primary". A near-black primary button carries no brand and looks like a heading in dense UIs. We should keep brand and neutral as separate, explicit palettes.
- Avoid: disabled as opacity only. In data-dense screens, disabled controls over striped or selected rows go muddy. A disabled-fg/disabled-bg token pair is more predictable.
- Note for density modes: Chakra's `size` prop on Table/Card/Stat (`sm`/`md`/`lg`) is per component, not a global density. A density context like `colorPalette` (an inherited variable) would scale better.

## Open issues

- Profile: blue is both Chakra's info status palette and the profile's brand palette. Themed, info turns brand. A truer mapping would solve brand into a dedicated palette (or the default `color-palette-*`) and leave blue for info. Needs an engine/profile decision, not a page change.
- Profile: only three of blue's eight slots are solved. A blue `solid` button would stay stock blue.
- `fg.subtle` isn't solved, so the disabled-text tier doesn't move with the theme.
- No phone navigation. Chakra has a `Drawer` and `Menu`, but a nav menu built from them is a hand assembly, not a native pattern. Left out.
