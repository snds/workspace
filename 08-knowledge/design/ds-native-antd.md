---
tags: [design-systems, color, theming, tokens, antd, emphasis-engine]
created: 2026-10-08
updated: 2026-10-08
status: working
confidence: medium
sources: [emphasis-engine native example build 2026-10-08, github.com/snds/emphasis-engine docs/systems/antd.md, src/native/antd.tsx]
related_skills: [ds-advisor, design-engineer]
related_projects: [emphasis-engine]
relations:
  relates-to:
    - "[[ds-native-theming-survey]]"
---

# Ant Design 6 — how its color works, learned by theming it

## For future agent
- **TL;DR:** A seed → algorithm → map → component token pipeline, run in JS. In cssVar mode the global tokens become variables, but many component tokens (Tabs ink bar, Radio, Menu, Header) are written as resolved literals. A runtime theme reaches the global layer and misses those components.
- **Key claims:** see "How its color works" and "What the solved theme reached" below. Each was observed by rendering the real components and injecting a solved theme (stock vs. themed, light and dark, 390 and 1280 wide).
- **Centric takeaways:** section "Ideas for the Centric design system"; consolidated in [[centric-ds-ideas-from-ds-survey]].
- **As of:** 2026-10-08 (dated: package versions below) · **Status:** current
- **Audience:** `for: all`
- **Update 2026-10-08 (profile fixes):** Fixed: the native page feeds the solved values into `ConfigProvider` tokens, so the Tabs ink bar, a checked Radio, and the selected Menu item follow the brand. Info background is info, not brand-tinted neutral.

## At a glance

- Package: `antd` 6.6.5 (MIT). CSS-in-JS via `@ant-design/cssinjs`.
- Page: `src/native/antd.tsx`, entry `native/antd.html`.
- Docs used:
  - https://ant.design/docs/spec/buttons (one primary per group, order of importance left to right)
  - https://ant.design/docs/react/customize-theme (seed, map and component tokens; algorithms; `cssVar`)
  - https://ant.design/components/layout (top-nav layout: dark Header, horizontal Menu, Breadcrumb, Content)
  - https://ant.design/components/form (vertical layout, `validateStatus`, `help`, `extra`)

## How its color works

- Three tiers, all in JS. Seed tokens (`colorPrimary`, `colorInfo`, `colorBgBase`) go through an algorithm (`defaultAlgorithm`, `darkAlgorithm`, `compactAlgorithm`) to make map tokens (`colorPrimaryHover`, `colorPrimaryBg`, `colorFillSecondary`). Alias tokens sit on those. Then each component computes its own component tokens.
- With `cssVar` on, tokens become custom properties. Global ones (`--ant-color-primary`, `--ant-color-bg-layout`) are written on the cssVar key class, here `.probe`. Every component root also carries that class, so each Tag, Alert and Table is its own scope.
- Component tokens are written as **literals** on rules like `.probe.ant-tabs-css-var { --ant-tabs-ink-bar-color: #1677ff }`, `.probe.ant-menu-css-var { --ant-menu-dark-item-selected-bg: #1677ff }`, `.probe.ant-layout { --ant-layout-header-bg: #001529 }`. They're computed in JS from the seed, not `var()` references. Overriding `--ant-color-primary` doesn't reach them.
- Light and dark aren't a class or attribute. They're a different algorithm on `ConfigProvider`, which regenerates every token and rewrites the CSS.
- Hover, active and border variants are separate map tokens the algorithm derives from the seed (`colorPrimaryHover`, `colorPrimaryActive`, `colorPrimaryBorder`), mostly by stepping a generated 10-step palette. Disabled uses neutral alpha tokens (`colorBgContainerDisabled`, `colorTextDisabled`). Focus is an outline in `colorPrimaryBorder`.
- Preset Tag colors map onto the status tokens: `success` reads `--ant-color-success*`, `processing` reads `--ant-color-info*`, `error` reads `--ant-color-error*`.

## Building the native page

- `ConfigProvider` exactly as the probe: algorithm by mode, `cssVar: { key: "probe" }`, `hashed: false`, `className="probe"` on the root `Layout`. Imported `antd/dist/reset.css` (Ant's own reset) to drop the UA body margin.
- Layout follows the ant.design top-nav example: `Layout` > dark `Header` with the product name and a `Menu theme="dark" mode="horizontal"`, then `Content` with a `Breadcrumb`, then `Footer`. Content padding is 48px from `md`, 16px below, via `Grid.useBreakpoint`.
- Grid: `Row`/`Col` on the 24-column grid with `gutter`. Stats are `xs=24 sm=8`. Form `lg=14`, side column `lg=10`. `Flex vertical` handles vertical rhythm.
- Title is `Typography.Title level={2}` with a secondary `Paragraph`. `Tabs` with items below.
- Stats: `Statistic` in borderless `Card`s, with a secondary `Text` delta.
- Form: `Form layout="vertical"` with `initialValues`. Helper text in `extra`, the error field in `validateStatus="error"` with `help`. `Switch` and `Checkbox` use `valuePropName="checked"`. `Radio.Group` with `options`.
- Buttons: Ant puts actions in order of importance, left to right. The form's submit sits under the fields, left-aligned: primary "Save changes", then default "Cancel" in a `Space`.
- Action hierarchy: primary, default, dashed (tertiary), text (ghost), link, primary danger, disabled primary. Ant reserves dashed for "add content", so using it for Preview is a stretch; it's the closest third tier. The link button reuses the scene's link label.
- Status: `Alert` with `showIcon`, `title` and `description` (`message` is deprecated in v6). Table is `Table` with `pagination={false}` and `scroll={{ x: "max-content" }}`, inside a `Card`. Status is a preset `Tag` color.
- Nothing missing. The horizontal `Menu` folds into an ellipsis at 390px on its own; the selected item can end up hidden in it.

## What the solved theme reached

Shots compared: `antd-{390,1280}-{light,dark}-{stock,themed}.png`, magenta brand.

- Reached: primary buttons, the checkbox, the switch, links (`Typography.Link`, link button, breadcrumb hover), the text button, info and error Alert backgrounds and borders, `processing` and `error` Tags (computed: tag info text `rgb(0 129 204)`, bg `rgb(247 238 248)`), page and container backgrounds, borders, text. These read global `--ant-color-*` variables.
- Not reached, because they're literal component tokens computed in JS:
  - `Tabs` ink bar and active tab text stay `#1677ff` (`--ant-tabs-ink-bar-color`, `--ant-tabs-item-selected-color`).
  - Checked `Radio` stays blue (`--ant-radio-radio-bg-color`). The checkbox next to it turns magenta, so the two controls disagree.
  - The selected dark `Menu` item stays `#1677ff` (`--ant-menu-dark-item-selected-bg`).
  - `Layout.Header` stays `#001529` (`--ant-layout-header-bg`) in both modes.
- Not reached, because the profile doesn't solve them: success and warning Alerts and Tags (correct for status), and the `Avatar` background.
- Info Alert and info Tag backgrounds go pink, not blue. The profile steps `--ant-color-info-bg` from the neutral palette, and the neutral palette is brand-tinted. The info icon stays blue. Fine as a brand-tinted neutral, but the info surface stops reading as info.
- The kit's literal-redefinition pass doesn't help here. It only covers root variables redefined under component selectors. Ant's component tokens are separate names, so the solved root values never feed them.

## Accessibility notes

- Preset Tag text on its tint is low contrast in light mode: warning `#faad14` on `#fffbe6` is about 1.9:1, success `#52c41a` on `#f6ffed` about 2.4:1.
- Placeholder text (`colorTextPlaceholder`, 25% black) is about 1.9:1 on white. Disabled text is the same alpha.
- The error message sits in the field's margin, so the next label ("Region") moves up against it. The space between fields gets smaller when there's an error.
- Secondary text (`colorTextSecondary`, 45% black) is about 4.6:1 on white: just passes.

## Ideas for the Centric design system

- Borrow the seed → algorithm → map token pipeline for density. Ant's `compactAlgorithm` makes a compact mode from the same seeds. Centric's density modes could be a transform on the semantic tier rather than a parallel token set.
- Borrow component-root scoping (every component carries the cssVar class). A nested theme (a dark side panel, a per-vertical accent) can be applied to one subtree without a provider for each.
- Avoid component tokens as computed literals. Ant's Tabs, Radio, Menu and Header ignore a runtime brand change because their tokens are resolved in JS. In a 3-tier model the component tier should be `var()` references to semantic tokens, so a tenant theme or a token hot-swap reaches every component. This one decision is the biggest difference between Ant and Primer here.
- Avoid deriving `info-bg` from the neutral scale. Status tints should come from the status hue, or info turns into brand when the neutrals are brand-tinted.
- Borrow `Form.Item`'s `validateStatus` + `help` + `extra` slots. One API covers error, warning, success and validating, with helper text kept apart from the error. It maps well to bulk-edit forms where many fields can be in different states.
- Borrow `Table` `scroll={{ x: "max-content" }}`. Wide tables scroll in their own container at any width.

## Open issues

- To make Ant fully themeable at runtime, the profile would need the component tokens too (`--ant-tabs-ink-bar-color`, `--ant-tabs-item-selected-color`, `--ant-radio-radio-bg-color`, `--ant-menu-dark-item-selected-bg`, `--ant-layout-header-bg`). They're written on `.probe.ant-*-css-var` and need scoped entries, not root ones.
- `--ant-color-info-bg` steps from neutral; probably should step from the info palette.
- The `link` button repeats the scene's link label. If the scene ever adds a link-style action, use that.
