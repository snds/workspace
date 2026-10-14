---
tags: [design-systems, centric, tokens, color, theming, ideas, emphasis-engine]
created: 2026-10-08
updated: 2026-10-08
status: working
confidence: medium
sources: [emphasis-engine native examples 2026-10-08, "[[ds-native-theming-survey]]"]
related_skills: [ds-advisor, design-engineer]
related_projects: [emphasis-engine]
relations:
  relates-to:
    - "[[ds-native-theming-survey]]"
    - "[[centric-plm-design-system]]"
    - "[[radix-derived-color-system]]"
    - "[[design-token-architecture]]"
    - "[[interaction-state-semantics]]"
---

# Ideas for the Centric design system, from theming 13 other systems

## For future agent
- **TL;DR:** Ten ideas, ranked by how much they'd help a data-dense, cross-framework PLM system. The top three:
  - make status a first-class token family that never aliases brand;
  - make every component token a `var()` reference to the semantic tier, never a literal;
  - solve state colors as tokens per surface, rather than using opacity or JS math.
- **Key claims:** each idea names the system it comes from and the mechanism behind it. Evidence is in the `ds-native-<id>` entries.
- **As of:** 2026-10-08 · **Status:** current
- **Audience:** `for: all`
- **Boundary:** these are ideas, learned from public systems in a personal project. Applying them to Centric work happens on Centric surfaces under the `centric-design` / `centric-engineering` profiles. Nothing here is employer code.

Centric context these were judged against:
- enterprise PLM (fashion, food, product engineering);
- big tables, record detail, bulk edit;
- Vue, React, React Native, and Angular;
- 3-tier tokens (global → semantic → component);
- Radix-derived scales on a shadcn base;
- density modes.

## 1. Status is its own family, never brand
- **What:** every status intent (`success`, `info`, `warning`, `danger`, `neutral`) gets a full triplet: wash background, solid, and text/foreground. Map them to Radix steps 3, 9, and 11. Tags take a status intent. Hue-named tags (blue, green) are a separate set, for categorical data like seasons and collections.
- **From:** Bootstrap's `-bg-subtle` / `-border-subtle` / `-text-emphasis`. Coinbase CDS's `bgNegativeWash` / `bgNegative` / `fgNegative`. Primer's `muted` / `emphasis`.
- **Why:** five of 13 systems leak info into brand. When a tenant or vertical changes its brand, "in production" stops looking like info. "Approved" and "shipped" are the most common statuses in PLM, so success can't be an afterthought. Coinbase CDS has no success banner, and Material has no status roles besides error.

## 2. Component tokens are always references
- **What:** the component tier is `var(--semantic, fallback)`, never a literal. Add a lint rule: a component token may not resolve to a global hue step.
- **From (borrow):** Material's `var(--md-filled-button-container-color, var(--md-sys-color-primary))`. Restyling its danger button took seven token overrides and no new CSS.
- **From (avoid):** Bootstrap's `--bs-btn-bg: #0d6efd`, Ant Design's literal component tokens, and Radix's hidden `--accent-track` → `--blue-9` chain.
- **Why:** a tenant theme, a vertical accent, or a token hot-swap then reaches every component. It's also the cheapest way to keep four framework bindings in sync, because the CSS is the contract.

## 3. Solved state tokens, per surface
- **What:** hover, pressed, selected, and disabled are their own tokens, solved for contrast against the surface they sit on. Use a fixed name grammar such as `-rest` / `-hover` / `-active` / `-disabled`.
- **From (borrow):** Fluent's Rest/Hover/Pressed/Selected/Disabled, Primer's per-state component tokens, Carbon's `layer-hover-01`, and Mantine's `filled-hover` / `light-hover`.
- **From (avoid):** opacity-only states (shadcn `/90`, Chakra's disabled), and JS-computed states (Coinbase CDS, Ant Design).
- **Why:** dense tables put controls on zebra, selected, and sticky-header rows. Opacity and `color-mix()` change contrast row by row, and JS-computed states break CSS theming. Named values also port to React Native, which has no `color-mix()`.
- **Fallback:** `color-mix()` is fine for decorative hovers (daisyUI, Chakra) where contrast isn't at stake.

## 4. Every fill ships with its on-color
- **What:** a fill token and its text color are one pair (`primary` + `primary-content`, `error-container` + `on-error-container`).
- **From:** daisyUI, Material, shadcn (`-foreground`).
- **Why:** a component can't pair a fill with the wrong text, and a contrast solver can solve each pair directly.

## 5. Subtree theming by one attribute
- **What:** one attribute re-scopes a palette or mode for everything inside it. Use it for a dark global nav, a dark record side panel, per-vertical accents, and a "danger zone" panel.
- **From:** Radix `data-accent-color`, Chakra `colorPalette` (an inherited variable), Bootstrap `data-bs-theme` on any element, Carbon zone classes, Fluent's nested provider.
- **Caution:** define zones as remaps onto a few semantic roots, not as full literal sets (Carbon repeats ~300 literals per zone). Then one solve covers every zone. Pure CSS works in Vue, React, and Angular. React Native needs an equivalent context.

## 6. Named layers for nesting
- **What:** "one step up from my parent" is a token, not a guess.
- **From:** Carbon's contextual layer aliases (`--cds-layer` re-pointed per nesting level), Material's five `surface-container` levels, and Atlassian's paired `elevation.surface.*` + `elevation.shadow.*`.
- **Why:** PLM record detail nests panels inside drawers inside tables. These map onto Radix neutral steps 1 → 2 → 3.

## 7. Density as a theme, not a prop
- **What:** density is one top-level switch that transforms space and control sizes. It's not a `size` prop on every component.
- **From:** Coinbase CDS's `coinbaseDenseTheme`, Radix's `scaling`, daisyUI's `--size-field` / `--size-selector`, and Ant Design's `compactAlgorithm` (density as a transform on the same seeds).
- **Avoid:** density that only exists per component (Chakra and Mantine `size`, @material/web).

## 8. A name grammar you can generate and lint
- **What:** pick one of these and enforce it with types:
  - Primer's `{property}Color-{role}-{emphasis}` (`bgColor-danger-muted`);
  - Atlassian's dotted names with a typed `token()` helper (typos fail at compile time);
  - Chakra's fixed slot set per palette (`solid`, `contrast`, `fg`, `subtle`, `muted`, `emphasized`, `border`, `focusRing`).
- **Why:** emphasis and state live in the name, which lines up with an emphasis-driven solver. A fixed slot set means component recipes name slots, never hues.

## 9. Portable component maps
- **What:** each component's variant → semantic-token map is plain data, shared by every framework binding.
- **From:** Coinbase CDS's `tokens/button.js`, which is shared by web and React Native.
- **Avoid:**
  - deep CommonJS-only entry points (Atlassian's icons broke Vite interop);
  - runtime dependencies that don't belong in a component library (Atlassian pulls in a feature-flag SDK).
  - Ship ESM with explicit `exports`.

## 10. Forms and tables patterns for bulk edit
- **Forms:**
  - One field wrapper owns label, hint, and validation (Fluent's `Field`; Ant Design's `Form.Item` with `validateStatus` / `help` / `extra`).
  - Style validity from `aria-invalid` (daisyUI's `validator`), so accessibility state and visual state come from one attribute.
  - Validation classes that work without client form state (Bootstrap's `is-invalid`) suit server-returned bulk-edit errors.
  - Put helper text below the field: Mantine's default above-the-field placement breaks scan lines in dense forms.
- **Tables:**
  - Wide tables scroll in their own container (Primer's `DataTable`; Ant Design's `scroll={{ x: "max-content" }}`).
  - Primer's `Table.Container` slots (title, actions, filter, table, footer) are a good model for list pages.

## Accessibility floors to set in the semantic tier
- Secondary text and placeholders at least 4.5:1. Mantine's `dimmed` is 3.3:1, and secondary text is half of a record-detail screen.
- Control edges at least 3:1. shadcn's field border is about 1.3:1.
- Disabled must keep its variant readable, and must not be opacity alone.
- Ship both modes in the token package, and make a missing token obvious. @material/web silently falls back to light-mode literals.
