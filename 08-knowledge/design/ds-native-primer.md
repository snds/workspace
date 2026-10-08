---
tags: [design-systems, color, theming, tokens, primer, emphasis-engine]
created: 2026-10-08
updated: 2026-10-08
status: working
confidence: medium
sources: [emphasis-engine native example build 2026-10-08, github.com/snds/emphasis-engine docs/systems/primer.md, src/native/primer.tsx]
related_skills: [ds-advisor, design-engineer]
related_projects: [emphasis-engine]
relations:
  relates-to:
    - "[[ds-native-theming-survey]]"
---

# GitHub Primer — how its color works, learned by theming it

## For future agent
- **TL;DR:** Functional tokens follow `{property}Color-{role}-{emphasis}` (`bgColor-danger-muted`) with per-state component tokens, and `data-color-mode` is repeated on a div by BaseStyles. Info and brand share one role (`accent`). The header is a token island (`--header-*`).
- **Key claims:** see "How its color works" and "What the solved theme reached" below. Each was observed by rendering the real components and injecting a solved theme (stock vs. themed, light and dark, 390 and 1280 wide).
- **Centric takeaways:** section "Ideas for the Centric design system"; consolidated in [[centric-ds-ideas-from-ds-survey]].
- **As of:** 2026-10-08 (dated: package versions below) · **Status:** current
- **Audience:** `for: all`
- **Update 2026-10-08 (profile fixes):** Fixed: status text on muted tints keeps stock contrast (translucent-only stacks hang off the page). Still by design: info and brand share `accent`.

## At a glance

- Packages: `@primer/react` 38.40.1 and `@primer/primitives` 11.10.0 (both MIT). Icons from `@primer/octicons-react` (already a dependency of `@primer/react`).
- Page: `src/native/primer.tsx`, entry `native/primer.html`.
- Docs used:
  - https://primer.style/product/ui-patterns/forms/ (layout, validation)
  - https://primer.style/product/ui-patterns/saving/ (submit bottom-left, cancel to its right)
  - https://primer.style/product/components/button/ (one primary per group, avoid disabled)
  - https://primer.style/foundations/primitives/color (functional token names)
  - Component types in `node_modules/@primer/react/dist` for what this version exports.

## How its color works

- Three tiers. Base scales (`--base-color-*`) feed functional tokens, which feed component tokens.
- Functional tokens are named by role, then property, then variant: `--fgColor-muted`, `--bgColor-accent-emphasis`, `--borderColor-danger-muted`. Roles are `default`, `muted`, `accent`, `success`, `attention`, `severe`, `danger`, `done`, `sponsors`, `neutral`, `open`, `closed`. `emphasis` is the strong solid; `muted` is the soft, usually translucent tint.
- Component tokens sit on top: `--button-primary-bgColor-rest`, `--control-checked-bgColor-rest`, `--underlineNav-borderColor-active`, `--header-bgColor`.
- Everything is plain CSS from `@primer/primitives/dist/css/functional/themes/*.css`. The selectors are attributes: `[data-color-mode="light"][data-light-theme="light"]` and the dark twin. Each theme file also has a `prefers-color-scheme` `auto` branch.
- Mode switches by attribute. `ThemeProvider colorMode="day|night"` drives the React side. `BaseStyles` writes `data-color-mode`, `data-light-theme`, `data-dark-theme` again on its own div. So variables resolve on `<html>` and again on that div. The kit treats every `[data-color-mode]` element as a scope.
- States are separate tokens, not opacity or filters. Buttons have `-rest`, `-hover`, `-active`, `-disabled` for bg, fg and border. Controls have `--control-checked-bgColor-rest/-hover/-active/-disabled`. Focus is one token, `--focus-outline-color`.
- `muted` backgrounds are alpha colors (`rgb(... / 10%)`), so they tint whatever they sit on.
- Component CSS ships as CSS Modules (`prc-Button-...`) with a hex fallback in every `var()`. The fallbacks only matter if the primitives CSS is missing.

## Building the native page

- Shell: Primer `Header` (dark, the GitHub global bar) with a product link, nav links, a bell and the user's initials. Nav links hide at the narrow breakpoint with `Hidden when="narrow"` (experimental), like GitHub's own bar.
- Layout: `PageLayout containerWidth="xlarge"` with `Header`, `Content` and a `Pane position="end"`. The pane stacks under the content on phones. That's Primer's page pattern; there is no column grid. Spacing comes from `Stack gap` (`condensed`, `normal`, `spacious`) and `--base-size-*`.
- Header: `Breadcrumbs` above a `PageHeader` with `Title`, `Description`, `Actions` and `Navigation`. Page actions sit right of the title, invisible before default. Putting `Breadcrumbs` inside `PageHeader.Breadcrumbs` rendered them inline left of the title, so they sit above it.
- Tabs: `UnderlineNav` (TabNav is deprecated). It folds overflow items into a "More" menu on its own at 390px.
- Stats: `Card` (experimental) with a small muted label, a large `Heading` and a muted delta. `Card.Heading`/`Card.Description` gave the label more weight than the value, so I used plain content.
- Form: `FormControl` with `Label`, `Caption`, `Validation variant="error"`. The error field uses `validationStatus="error"`. Checkbox and radios are `FormControl`s with the control first. Radios sit in a `RadioGroup`. `ToggleSwitch` has no FormControl slot, so I followed Primer's pattern: a label and a caption beside it, linked with `aria-labelledby`/`aria-describedby`.
- Saving: primary "Save changes" bottom-left, default "Cancel" to its right. That's Primer's saving pattern (dialogs flip it).
- Action hierarchy: primary, default, invisible (Preview, with an icon), invisible (Cancel), danger, disabled primary. Primer has no outline or tertiary button, so tertiary is invisible. Primer advises `inactive` over `disabled`; the page shows `disabled` because the scene asks for it.
- Danger zone: a box with `--borderColor-danger-emphasis` holding a danger button, like GitHub repo settings. Composed from tokens. It's a GitHub product pattern, not a component.
- Status: `Banner` (critical, info, success, warning) with title and description, `layout="compact"`. `Flash` still exists but `Banner` is the current one. In the table, `Label` with success, accent, attention, danger. `StateLabel` is for issue and PR states, so it doesn't fit.
- Table: `DataTable` (experimental) in `Table.Container` with `Table.Title` and `Table.Subtitle`. DataTable wraps itself in a scrollable region, so the table scrolls inside itself at 390px. An outer `ScrollableRegion` broke the container's grid areas (the title and subtitle moved to the side), so don't wrap it.
- Text: `Text` with `--fgColor-default`, `--fgColor-muted`, `--fgColor-disabled`, and an inline `Link`.

## What the solved theme reached

Shots compared: `primer-{390,1280}-{light,dark}-{stock,themed}.png`, magenta brand.

- Reached: primary buttons (rest), checkbox, radio, toggle switch, links and breadcrumb links, the accent `Label` ("In production"), the info Banner icon, default-button tint, table header and `bgColor-muted` surfaces, borders, text. All of these read functional or component tokens on `<html>`/BaseStyles.
- Info is brand in Primer. `accent` is both the link color and the info role. With a magenta brand, "In production" and the info Banner turn magenta. That's correct for Primer, but status and brand can't be separated without a separate info role.
- The info and critical Banner backgrounds went almost gray. `--bgColor-accent-muted` and `--bgColor-danger-muted` solved to dark colors at 7% alpha (`rgb(53 3 60 / 7%)`, `rgb(65 3 4 / 7%)`). Stock uses a light hue at ~15–40% alpha. The solve keeps the contrast step but loses the tint. Worth checking in the engine's translucent path.
- Not reached:
  - The global `Header`: `--header-bgColor` and `--header-fgColor-*` aren't in the profile, so it stays stock charcoal in both modes.
  - The disabled primary button stays green (`--button-primary-bgColor-disabled` isn't solved). Next to a magenta primary, disabled reads as a different action.
  - The `UnderlineNav` active underline stays coral. It *is* solved, but the profile models it on the danger palette, so it lands close to stock. Primer's coral is a brand accent, not danger.
  - Success and attention Banners and Labels, and the danger-zone border, stay stock: those roles aren't in the profile. That's correct for status.
- No shadow DOM, portals or inline colors in what's shown. Every miss is a token the profile doesn't own.

## Accessibility notes

- Disabled primary button: white text on pale green (`#95d8a6`) is about 1.9:1. Intended for disabled, but it's why Primer says avoid disabling.
- `Header` link text is white at 70% on `#25292e`. Readable, but the active item has no indicator besides `aria-current`.
- The ToggleSwitch "On" text sits outside the switch and repeats the state; fine for screen readers, since the switch has `aria-pressed`.
- Validation messages pair an icon with red text, so the error doesn't rely on color.

## Ideas for the Centric design system

- Borrow the functional-token grammar: `{property}Color-{role}-{emphasis}` (`bgColor-danger-muted`, `fgColor-onEmphasis`). It's regular enough to generate and to lint, and `muted` vs `emphasis` maps cleanly onto soft vs solid in Radix scales.
- Borrow per-state component tokens (`-rest/-hover/-active/-disabled`). In a 3-tier model it gives one place to fix a state in Vue, React, Angular and React Native, with no `color-mix` or opacity math that native platforms render differently.
- Borrow translucent `muted` backgrounds. Status tints that work on any surface help dense tables with zebra rows, selected rows and sticky headers.
- Borrow `DataTable`'s built-in scroll region and `Table.Container` grid (title, actions, divider, subtitle, filter, table, footer). It's a good slot model for PLM list pages.
- Avoid making info and brand the same role (`accent`). When the brand changes per tenant or vertical, status meaning would move with it. Keep `info` separate.
- Avoid a header that sits outside the theme (`--header-*` is its own island). A themed product will look half-done. If the shell is meant to be fixed, say so in the tokens.
- Consider Primer's "danger zone" pattern for bulk delete and archive in record settings: one place, red border, confirmation.

## Open issues

- Profile gaps: `--header-bgColor`, `--header-fgColor-default/-logo`, `--button-primary-bgColor-disabled` (and fg/border disabled), success and attention roles.
- `--underlineNav-borderColor-active` is modeled on the danger palette. It should probably follow brand, or stay unsolved.
- Translucent `*-muted` solves come out near-black at 7% alpha in light mode. Check the translucent step.
- `PageHeader.Breadcrumbs` placement looked wrong in this version; worth a recheck on upgrade.
