---
tags: [design-system, boilerplate, tokens, radix, documentation, dogfooding, portfolio]
created: 2026-07-09
updated: 2026-07-09
status: stable
confidence: high
sources: [machine-local ~/.claude/CLAUDE.md (pre-beacon, migrated FX-15), nexus repo]
related_skills: [ds-advisor, design-engineer]
related_projects: [15-DavinciRemake]
---

# Davinci DS boilerplate — portfolio demo rebuilds (nexus reference)

_Migrated 2026-07-09 from the machine-local `~/.claude/CLAUDE.md` (FX-15). These were standing
"always use" standards for portfolio/demo rebuild work; reference implementation:
`github.com/snds/nexus`._

## 1. The boilerplate (ALWAYS use for portfolio demo rebuilds)

A pnpm + turbo monorepo, four surfaces sharing ONE DS:

1. **Custom demo app** tailored to the target project (`apps/web`).
2. **shadcn/Radix design system**: L0 tokens (`packages/tokens`) + shadcn var bridge
   (`--background → --nx-bg`); L1 pristine shadcn/Radix base in `components/ui` (Button, Tooltip,
   Dialog, DropdownMenu, Popover…); L3 product wrappers in `components/nexus` composing L1 + tokens.
3. **Docusaurus site** = EXCLUSIVELY design-system documentation (never project/process docs).
4. **Storybook** covering ALL base + tokens (Foundations) + product primitives, with `addon-a11y`.

Deploy all to GitHub Pages via Actions: guides at root, Storybook at `/storybook`, demo at `/app`.

## 2. Dogfooding (non-negotiable definition)

NOT "show accurate values" or "recolor the theme." The demo, docs site, AND Storybook must
**literally USE the DS for their own chrome and interactions** — nav, buttons, cards, surfaces,
menus, tooltips, focus/keyboard, type, spacing, radii are the DS's tokens + components. If a
surface looks like the framework default, it is NOT dogfooded. Swizzle framework chrome to DS
components; bind every framework variable to DS tokens.

## 3. Token architecture (3 tiers + Radix Colors — mandatory)

_Cross-link: [[radix-derived-color-system]] owns the general color-foundation architecture; this
section is the nexus-specific operating contract._

- **L0 primitives = real Radix Colors scales** (`@radix-ui/colors`), NOT hand-rolled HSL ramps and
  NOT Tailwind palette colors. Pick a cool gray (Slate) + an accent; map `--nx-neutral-*`/
  `--nx-accent-*` to them. Plus the full **type scale** (`--nx-text-*`, `--nx-weight-*`,
  `--nx-leading-*`, `--nx-tracking-*`) and entity/severity palettes.
- **Primitives are SINGLE-MODE constants.** Expose BOTH light and dark values side-by-side
  (`--nx-neutral-light-1..12` AND `--nx-neutral-dark-1..12`); never re-define a primitive per
  theme. **Modes live ONLY at L1 semantics** — `:root` points semantics at the dark primitives,
  `:root.light` re-points the same semantics at the light primitives.
- **The Radix 12-step CONTRACT is law — never cross a step's context:**
  `1–2` app/bg · `3–5` component states (normal/hover/active) · `6–8` borders (**8 = focus ring**)
  · `9–10` solid fills (9 solid, 10 hover) · `11` low-contrast text (AA) · `12` high-contrast text.
  **Text comes ONLY from 11/12. Solids ONLY from 9/10. Borders from 6–8.** A text token pointing at
  step 9/10 is the classic bug (it looks fine in dark, fails AA in light — Slate-9 on white ≈ 3.8).
- **Accent-as-fill ≠ accent-as-text.** Ship two tokens: `--nx-accent` (step 9, solid bg) and
  `--nx-accent-text` (step 11, links/icons/inline). Using step 9 as text fails contrast.
- **Solid + white text rarely hits WCAG AA 4.5** — Radix step-9 targets APCA/3:1, not WCAG-small.
  Verify by measurement: white on Blue-9 ≈ 3.3 (fail), on **Indigo/Iris-9 ≈ 5.2 (pass)**. If the
  brand solid can't carry white at AA, switch the *solid* to a deeper scale (Indigo) or use the
  Radix "soft" recipe (step-3 bg + step-11 text). Reds at 9 can't carry white at AA (~3.9) — that's
  a documented APCA/large exception, not a free pass.
- **Consumption = `var(--token)`**, never `hsl(var())`. Radix values are hex; opacity comes from
  **Tailwind opacity utilities** or `color-mix(in srgb, var(--x) N%, transparent)` — never inline
  hsl alpha, never Radix alpha scales. For Tailwind `/opacity` to work on hex CSS-var colors,
  define config colors as `rgb(from var(--x) r g b / <alpha-value>)` (relative-color syntax).
- **Type is mandatory** — `font-family` alone is not a type system. Ship a `Text` component as the
  semantic type layer (variants composed from type primitives).
- **Guard it in CI:** a contrast unit test that resolves every semantic text/solid pairing through
  its var() chain and asserts AA in BOTH themes; an ESLint ban on raw Tailwind palette classes
  (`bg-blue-500`…) in DS source; a token-lint that no `fg/text` alias points at steps 1–10 and no
  `bg/solid` alias at 11–12. "The rule is in the bundle" ≠ "it passes" — assert the computed ratio.

## 4. A design system must document EVERYTHING — canonical docs IA

Mature systems (Carbon, Atlassian, Polaris, Material, Spectrum) converge on this. Cover ALL of it:

1. **Get started / Overview** — what it is, principles, designer AND developer paths, install,
   versioning, contributing, support.
2. **Foundations** — principles, **accessibility (first-class)**, color, typography, spacing &
   layout/grid, elevation/surface, iconography, motion, shape/radius, **content & voice**, i18n.
3. **Tokens** — model (global→semantic→component), **full primitive ramps + type scale**, semantic
   aliases, theming/modes. Document ALL tokens.
4. **Components** — ONE page per component (never a single gallery), fixed template: header +
   **status badge** (stable/beta/deprecated) + Storybook/Figma/source links, live preview, usage
   (when/when-not), anatomy, variants, states, sizing, behavior/keyboard, content guidelines,
   **accessibility**, **API/props table**, code examples, related, changelog.
5. **Patterns** — composed solutions (forms, empty/error/loading, layouts, navigation, data).
6. **Content guidelines** — voice & tone, grammar, terminology, inclusive language.
7. **Resources / Contributing / Changelog** — Figma kit, packages, contribution, releases.

Cross-cutting: dual audience, per-component maturity labels, versioning + changelog, search, live
examples, accessibility per component.

**Tooling split:** Docusaurus owns IA + prose + foundations/tokens/patterns/content + per-component
prose (embeds the live example, deep-links Storybook). Storybook owns the interactive workbench —
every variant/state, `argTypes` controls, `tags:['autodocs']` prop tables, addon-a11y. Don't
duplicate APIs; Docusaurus links to Storybook autodocs. Full standard lives at
`docs/ds-documentation-standard_v1.0_2026-06-07.md` in the nexus repo.

## Related

- [[radix-derived-color-system]] — the general color-foundation architecture
- [[nexus-monorepo-playbook]] — the technical gotchas (pnpm/Docusaurus/Storybook/Pages)
- `01-frameworks/10-perception-integrity.md` — native-resolution visual assessment (framework #10)
