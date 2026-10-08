---
tags: [design-systems, color, theming, tokens, cds, emphasis-engine]
created: 2026-10-08
updated: 2026-10-08
status: working
confidence: medium
sources: [emphasis-engine native example build 2026-10-08, github.com/snds/emphasis-engine docs/systems/cds.md, src/native/cds.tsx]
related_skills: [ds-advisor, design-engineer]
related_projects: [emphasis-engine]
relations:
  relates-to:
    - "[[ds-native-theming-survey]]"
---

# Coinbase Design System (CDS) — how its color works, learned by theming it

## For future agent
- **TL;DR:** ThemeProvider writes semantic color variables inline on its own div. Variant maps are plain data shared by web and React Native. Hover, pressed, and disabled are blended in JS and written as literals, so a CSS-variable theme never reaches them. Info is brand, and there is no success banner. A dense theme ships next to the default. In this repo, "cds" means Coinbase, not Centric.
- **Key claims:** see "How its color works" and "What the solved theme reached" below. Each was observed by rendering the real components and injecting a solved theme (stock vs. themed, light and dark, 390 and 1280 wide).
- **Centric takeaways:** section "Ideas for the Centric design system"; consolidated in [[centric-ds-ideas-from-ds-survey]].
- **As of:** 2026-10-08 (dated: package versions below) · **Status:** current
- **Audience:** `for: all`

In this repo, "cds" means Coinbase's design system. It is not the Centric design
system. Section 6 is the only place Centric comes up.

## 1. At a glance

- Package: `@coinbase/cds-web` 9.29.0, with `@coinbase/cds-common` 9.29.0 and
  `@coinbase/cds-icons` 5.x (icon font). React peer range is `^18 || ~19.1.2`.
  The repo runs React 19.3.0. Nothing broke, but it's outside the declared range.
- License: Apache-2.0, per the LICENSE file in github.com/coinbase/cds (checked
  2026-10-08). The npm packages themselves carry no `license` field and no LICENSE
  file, so the repo is the only place it's stated.
- Docs used:
  - https://cds.coinbase.com/getting-started/theming/
  - https://cds.coinbase.com/components/feedback/Banner/
  - https://cds.coinbase.com/components/inputs/Button/
- Also read from the package source: `cds-common/tokens/{button,banner,tags,interactable}.js`,
  `cds-web/system/Interactable.js`, `cds-web/layout/Grid.js`.

## 2. How its color works

- **Two tiers.** A *spectrum* of raw hue steps (`blue0`…`blue100`, `gray0`…) and a
  *semantic color* layer (`fg`, `fgMuted`, `fgPrimary`, `bg`, `bgAlternate`,
  `bgPrimary`, `bgPrimaryWash`, `bgSecondary`, `bgTertiary`, `bgLine`, `bgNegative`,
  `bgNegativeWash`, `bgWarningWash`, `bgPositive`, the `accentSubtle*`/`accentBold*`
  set, and so on). Names are camelCase. They read as role plus emphasis: `bgX` for the
  solid, `bgXWash` for the tint, `fgX` for text in that hue.
- **Component maps.** The components don't own any color tokens. Each one maps its
  variants onto semantic names in a plain JS table in `cds-common/tokens/*`. Two
  examples: button primary is `{ color: fgInverse, background: bgPrimary }`, and banner
  warning is `{ background: bgWarningWash, iconColor: fgWarning, borderColor: bgWarning }`.
  Tags are the exception. They map straight to spectrum steps (`green0`/`green60`,
  `yellow0`/`yellow70`).
- **Where variables live.** `ThemeProvider` writes every value inline on its own
  root `<div>` (class `cds-default light|dark`). That covers `--color-*` for semantics,
  `--blue10`-style for spectrum, and `--light-*`, `--dark-*` and `--lightColor-*` for
  both schemes. Nothing goes on `:root`. The component CSS (Linaria, inside
  `@layer cds`) reads `var(--color-bgPrimary)`.
- **Light/dark.** It's a prop: `activeColorScheme="light" | "dark"`. The provider
  rewrites the inline variables and swaps the class. Spectrum inverts with the scheme
  (`gray0` is white in light and black in dark), so tags flip without separate dark
  tokens.
- **Values are raw strings.** Theme colors have to be literal `rgb()` strings, not
  `var()` or functions. The docs say so explicitly.
- **States are computed in JS.** `Interactable` (under every Button, IconButton, cell
  and select option) reads `theme.color[background]` from the **JS theme object**. It
  blends that value with d3-color at fixed opacities (hover 0.88, pressed 0.82,
  disabled 0.75; buttons use the accessible 0.5) and writes the results inline on each
  element as literal colors: `--inter-hover-bg: rgb(0,72,224)`, `--inter-press-bg`,
  `--inter-disable-bg`. Only the rest color stays a variable
  (`--inter-bg: var(--color-bgPrimary)`).
- **Disabled.** Opacity on the element, over the precomputed `--inter-disable-bg`.
  `Text` takes `disabled` and dims by opacity. There is no `fgDisabled` token.
- **Focus.** A ring in `bgLinePrimary` (brand).

## 3. Building the native page

- **Layout.** Everything is built from `Box`, `VStack` and `HStack` with theme spacing
  units (`gap={2}` = 16px on the 8px base). The two-column area and the stats row are
  `Box display="grid"` with a responsive `gridTemplateColumns`
  (`{ base, tablet, phone }`). CDS style props take responsive objects keyed to its
  breakpoints: phone < 768, tablet 768–1279, desktop ≥ 1280.
  - `Grid columnMin` is a trap. It concatenates the value into `minmax(${columnMin}, …)`,
    so `columnMin={200}` produces invalid CSS and silently gives one column. Pass
    `"200px"`.
  - `Box` defaults to `display: flex`. A flex `main` lets a wide child, like a tab row
    or a table, push the page wider than the viewport. I set `display="block"` on main.
- **Type.** `TextTitle1` (page title), `SectionHeader` (section titles and
  descriptions), `TextHeadline`, `TextBody`, `TextLabel1`/`TextLabel2`. Color comes
  only through palette props (`color="fgMuted"`, `background="bgAlternate"`).
  `SectionHeader` defaults to `paddingX={4} paddingY={2}`. Zero them when it sits
  inside a padded container.
- **Header.** `NavigationBar`, with the product name at the start and `NavLink`s in
  the middle (hidden on phones with responsive `display`). The end slot holds a
  transparent `IconButton` bell and an `Avatar`.
- **Tabs.** `Tabs` (the new API). `TabNavigation` is deprecated, slated for removal in
  v10. Tabs ship with no gap between labels, so pass `gap={3}`.
- **Form.** `TextInput` with `label` and `helperText`. The error field is
  `variant="negative"`, and its helperText becomes the error message with an icon.
  `Select` comes from `@coinbase/cds-web/alpha/select`, because the old `Select` is
  deprecated. The rest are `Switch`, `Checkbox`, and a `RadioGroup` taking an options
  record.
- **Button order.** CDS says one primary per screen. Its form and dialog examples
  right-align a **transparent secondary Cancel** beside the primary, so the form footer
  is `HStack justifyContent="flex-end"` with Cancel then Save. The hierarchy row maps
  the scene like this:
  - primary → `primary`
  - secondary → `secondary`
  - tertiary → `tertiary` (a darker gray fill, not an outline)
  - ghost → `secondary transparent`
  - danger → `negative`
  - disabled → `primary disabled`
- **Status.** Tags for table status (`colorScheme` green/blue/yellow/red at
  `emphasis="low"`). Alerts are `Banner` with `styleVariant="inline"`, which is the
  documented choice for section-level errors. `showDismiss={false}`.
- **Stats.** `ContentCard`. The old `Card` is deprecated. ContentCard defaults to a
  fixed `minWidth` and `maxWidth`, which made the cards overlap in a grid, so I reset
  them to `0` and `none`.
- **Table.** `Table variant="ruled"` with `TableHeader`/`TableBody`/`TableRow`/`TableCell`
  (`title` cells), inside a bordered `Box overflow="auto"` so it scrolls sideways on
  phones.

Missing or substituted:
- **Breadcrumb**: CDS has none. I composed it from `Link font="label2"` and a
  `TextLabel2 color="fgMuted"` slash, with `aria-current` on the last crumb.
- **Success banner**: Banner has `informational | warning | error | promotional` and
  nothing positive. Success uses `informational` with
  `startIcon="circleCheckmark" startIconColor="fgPositive"`, both documented props.
  `promotional` is brand-tinted, so I didn't use it for status.
- **Outline button**: none. Tertiary is a filled gray.
- **Breakpoint-driven nav**: CDS's desktop app pattern is a `Sidebar`. I used the top
  `NavigationBar` because it works at both widths without a drawer.

## 4. What the solved theme reached

The profile sets 14 semantic variables: `bg`, `bgAlternate`, `bgPrimary`,
`bgSecondary`, `bgTertiary`, `bgLine`, `bgLineHeavy`, `bgNegative`, `bgNegativeWash`,
`fg`, `fgMuted`, `fgInverse`, `fgPrimary`, `fgNegative`. With the provider div listed
as a scope, every component that reads one of those at rest picked up the solved value.

Reached:
- **Primary**: buttons, the switch track, the checked checkbox, the radio dot, the
  active tab label and indicator, links and the breadcrumb link.
- **Neutral steps**: the stat cards (`bgAlternate`), secondary and tertiary buttons,
  page background, borders and text.
- **Banners**: the informational banner's icon and border turned brand magenta. CDS's
  own map points informational at `fgPrimary`/`bgPrimary`, so in this system info
  *is* brand.
- **Danger**: the danger button and the negative input.

Didn't reach:
- **Hover, pressed and disabled on every interactive element.** These are literal
  colors computed in JS from the stock theme object. Measured on the themed page, the
  magenta primary button still hovers to `rgb(0,72,224)` (stock blue), and the
  disabled "Publish" button renders `rgb(20,96,255)` at 50% opacity. A CSS-variable
  override can't reach them. The fix is to pass the solved colors into the
  `ThemeProvider` theme object (`lightColor`/`darkColor`) so the blends are computed
  from them.
- **Tags.** These read spectrum variables (`--green0`, `--yellow70`), which aren't in
  the profile. "In production" stays blue.
- **Warning banner.** `bgWarningWash`, `fgWarning` and `bgWarning` aren't in the
  profile.
- **Positive.** `fgPositive` (the success icon) isn't in the profile.
- **Avatar fallback.** Spectrum blue, by `colorScheme`.
- **Things outside the scope div.** Inline values sit on the provider div, so any
  portal without its own `isolated` ThemeProvider would miss them, including the
  alpha Select dropdown. Not shown in the shots because the dropdown is closed.

## 5. Accessibility notes (stock)

- Disabled primary: white text over 50%-opacity blue is roughly 2.2:1. That's
  intentional for disabled and exempt from WCAG, but the label is hard to read.
- Disabled text is `fgMuted` at reduced opacity, about 2.2:1 on white. Fine for
  disabled, but there's no separate token to tune it.
- `fgMuted` on `bg` is about 6.3:1. On `bgAlternate` (the stat cards) it is lower, about
  5.5:1, which still passes AA.
- The transparent ghost button has no visible boundary at rest, only text. Pairing it
  with a primary is fine. On its own it reads as plain text.
- Low-emphasis tags (`green60` on `green0`) pass easily in light mode. In dark mode the
  spectrum inversion keeps them readable.

## 6. Ideas for the Centric design system

Borrow:
- **Component variant maps as data.** `tokens/button.js` maps each variant to semantic
  names in a plain object, shared by web and React Native. Centric ships Vue, React,
  React Native and Angular. One framework-free map per component (variant →
  semantic tokens) would be the component tier of the 3-tier model in a portable form,
  and every framework binding could read it.
- **Wash/solid/fg triplets per intent** (`bgNegative`, `bgNegativeWash`, `fgNegative`).
  That's the exact set a status banner, a tag and an inline error need. It maps cleanly
  onto Radix steps 3/9/11 for Centric's status scales.
- **Responsive style props keyed to named breakpoints** (`{ base, phone, tablet }`).
  Dense PLM layouts change shape at breakpoints. Expressing that in props instead of
  per-component media queries keeps layouts declarative across frameworks.
- **A first-class dense theme.** CDS ships `coinbaseDenseTheme` next to the default:
  the same tokens with smaller space and control sizes. That's density as a theme swap,
  not a per-component prop, which suits Centric's density modes.

Avoid:
- **JS-computed interaction states.** Blending hover and pressed from the JS theme
  object and writing literal colors inline means any CSS-variable theming (a customer
  brand, a vertical theme) breaks every hover state. Centric should compute state
  colors in CSS (separate step tokens from the Radix scale, or `color-mix()` over the
  variable) so one variable change carries through.
- **Theme variables only on a provider div.** It works, but portals need their own
  isolated provider, and tooling can't find the values on `:root`. Centric's tables,
  menus and bulk-edit popovers are portal-heavy. Root-level variables with a
  class-scoped override are simpler.
- **No success banner, and info = brand.** In a PLM app, "approved" and "shipped" are
  the most common statuses. Status intents should be complete (success, info, warning,
  danger, neutral) and never alias brand.
- **Tags on raw spectrum steps.** Theming and status meaning get lost. Route tags
  through semantic status tokens.

## 7. Open issues

- **Contract issue in `kit.tsx`.** `restore()` writes back the inline values it saved
  before applying. CDS's provider rewrites those same inline variables on a mode
  switch, so going from themed light to stock dark restored *light* values over the
  provider's fresh dark ones. The result was a half-light dark page. I worked around it
  in the page by keying `ThemeProvider` on mode, so each switch gets a new div. That
  resets form state on a mode switch. The real fix belongs in the kit: on restore, skip
  any property whose current inline value isn't the one the kit set. (Fixed in the
  kit on 2026-10-08; the mode-keyed provider workaround was removed.)
- **The profile misses intents.** It covers no warning, positive or spectrum
  variables, so tags, the warning banner and success icons never theme. Its dark
  selector is listed as `.dark`, but the provider uses inline values on
  `.cds-default.dark`.
- **The solved theme should also feed the JS theme object**, so hover, pressed and
  disabled follow. That would need a contract hook, for example
  `render(mode, values)`.
- **The alpha Select dropdown was not checked open.** It portals.
