---
tags: [engineering, design-tokens, lint, shadcn, tailwind, agents]
created: 2026-09-15
updated: 2026-09-15
status: working
confidence: high
sources:
  - "https://github.com/shadcn-ui/lint (README, SETUP.md, docs/how-it-works.md, docs/rules/no-raw-colors.md, docs/design-systems.md, 2026-09-15)"
  - "session 2026-09-15 — independent ds-lint service"
related_skills: [design-engineer, ds-advisor, design-system-ops]
related_projects: [19-workspace-brain]
relations:
  builds-on:
    - "[[llm-safe-design-system-expressiveness]]"
    - "[[figma-tailwind-token-pipeline]]"
    - "[[radix-derived-color-system]]"
    - "[[agent-output-rails]]"
  relates-to:
    - "[[ds-ops-governance-notes]]"
    - "[[decision-shadcn-lint-independent-service]]"
    - "[[decision-lint-narrow-or-not-at-all]]"
---

# @shadcn/lint against our token tiers

## For future agent
- **TL;DR:** `@shadcn/lint` is the product-repo agent linter for shadcn-bound Tailwind apps. It is a **sibling** of vault integrity and of `09-tools/eslint-off-system/`, not a merge. Stock `no-raw-colors` **false-greens** `bg-cds-blue-500` because CDS declares `--color-cds-*` in `@theme inline`. Overlay `ds-lint/no-tier-leakage` is required in the same config (`eslint.ds.config.mjs`). Theme reset is a later product-CSS PR (overlay-first).
- **Key claims:**
  - *Timeless:* lint that makes off-system values inexpressible lives in the **product repo**. The vault owns the policy, the overlay spec, and the law.
  - *Timeless:* authoring vocabulary is the **semantic tier** (`bg-primary`, `text-muted-foreground`). Primitives and shade aliases are CSS mapping, not TSX classes.
  - *Dated 2026-09:* `@shadcn/lint` 0.1.x reads `--color-*` from `@theme` (+ imports). Tailwind's default palette is raw. `deny` cannot make a declared `@theme` token a raw color. Proven on cds `semantic.css`: `--color-cds-blue-500` is in `@theme inline`.
  - *Pointer:* canonical entry is `09-tools/shadcn-lint/eslint.ds.config.mjs`. Overlay-first; do not follow upstream SETUP "no new rules." Decision: [[decision-shadcn-lint-independent-service]].
- **As of:** 2026-09 · **Status:** current (cds + proto `lint:ds` on `main`; cui [#398](https://github.com/cpes-software/centric-ui/pull/398) awaiting review)
- **Audience:** `for: agent`

---

## Why stock @shadcn/lint is not enough here

The upstream plugin is built for Tailwind v4 design systems. It is the right engine: it reads components, variants, and the theme, and the errors tell an agent what to use instead. Six rules:

| Rule | Catches |
|---|---|
| `no-restyle` | Appearance classes on design-system components (allow `layout`) |
| `no-raw-colors` | Palette colors, undeclared tokens, raw SVG paints |
| `no-arbitrary-values` | `p-[13px]`, `bg-[#…]` |
| `no-inline-styles` | Inline `style` / `<style>` |
| `no-unknown-classes` | Classes the project's Tailwind cannot generate |
| `require-static-classes` | `` `bg-${color}` `` on components |

`no-raw-colors` treats **declared `@theme --color-*` names as legal**. Tailwind's built-in palette (`bg-pink-500`) is illegal unless you re-declared it.

Our stack does something stock shadcn does not:

1. **Radix primitives** `--color-{hue}-{1..12}` (and `A{n}`) — role scale, semantic layer maps by step ([[radix-derived-color-system]]).
2. **Shade aliases** `--color-{hue}-{50..950}` — nearest-OKLCh-L onto those steps so `bg-green-500` still *compiles* ([[figma-tailwind-token-pipeline]]).
3. **Semantics** `--sem-*` / shadcn `--color-primary`, `--color-background`, … — the only authoring tier.
4. Unlayered `:root` overrides `@layer theme` so palette **values** swap without regenerating utilities.

If (1) and (2) are in `@theme` so the utilities exist, stock `no-raw-colors` allows `bg-blue-9` and `bg-blue-500` in product TSX. **Live today, a third leak:** CDS `semantic.css` `@theme inline` declares `--color-cds-blue-500` (and the cds-* ramp) as back-compat aliases. Those *are* declared theme tokens. `bg-cds-blue-500` passes `no-raw-colors`. That is **tier leakage** ([[ds-ops-governance-notes]]), the same defect as binding a Figma component to `Color/*`.

`allow` / `deny` on `no-raw-colors` do not fix it: *"`deny: [\"bg-primary\"]` does not make a declared token a raw color."*

## The two customizations

### 1. Overlay rule (always)

`09-tools/shadcn-lint/no-tier-leakage.js` (spec `tier-leakage.json`, probe `probe.py`) flags:

- Radix steps: `bg-blue-9`, `text-zinc-11`, `bg-blueA-5`
- Shade aliases: `bg-blue-500`, `md:bg-zinc-100/50`
- Raw palette: `bg-white`, `text-black`
- **CDS compat (the live false-green):** `bg-cds-blue-500`, `text-cds-red-500`, `bg-cds-gray-1000`

It allows semantic utilities: `bg-primary`, `text-muted-foreground`, `bg-card`, `ring-ring`, `bg-selected`.

Run it **beside** `@shadcn/lint`, never inside vault CI.

### 2. Theme surgery (when the product can take it)

```css
@theme {
  --color-*: initial;
  /* re-declare semantic --color-* only */
}
:root {
  /* primitives as values, no utilities */
}
```

Then `no-unknown-classes` also refuses `bg-blue-9`. Shade aliases can remain as **variables** for `--color-primary: var(--color-blue-10)` without remaining as **classes**. That matches the LLM-safe law: off-system values are inexpressible, not discouraged. The compat layer was so existing CSS and the semantic map keep working — not so agents keep writing `bg-green-500`.

Do not apply the reset in this vault. The product theme is the SSOT.

## Independence contract

| Service | Scope |
|---|---|
| Vault validators / `workspace-harness.py` | Markdown graph, skills, links. No Tailwind. |
| `09-tools/eslint-off-system/` | Hex / arbitrary class strings. LCARS constitution table. No theme discovery. |
| `09-tools/shadcn-lint/` + `@shadcn/lint` | shadcn-bound product TSX. Theme-aware. Agent messages. |

A product may run `lint` (framework) and `lint:ds` (this service) as two scripts. Folding `lint:ds` into vault close-out as a required CLI would make every markdown session depend on Node + a product theme. Close-out's `eng` / `ai-design-systems` rows already SKIP to product CI — that skip now names `npm run lint:ds`.

## Adoption order (product repo)

Overlay-first. Upstream SETUP "no new rules" is the skip path that leaves `bg-cds-blue-500` green.

1. Copy `09-tools/shadcn-lint/` and point `lint:ds` at `eslint.ds.config.mjs` (both plugins; overlay at `error`).
2. Set `settings.shadcn.ui` for that app. Keep `no-raw-colors` and the overlay on inside `components/ui`.
3. `no-restyle` may start at `warn` + `--max-warnings` if the tree is dirty; do not warn-only the overlay.
4. Theme reset (`@theme { --color-*: initial }`, semantics only) is a **later** product-CSS PR — it would also retire `bg-cds-*` utilities still used in Storybook/docs.
5. Per-component `contracts` for CardTitle typography, CardContent spacing, Button `w-full`, etc. — in the product config.

Employer repos: copy the folder, open a PR, do not symlink the workspace. Oxlint-only is not a complete gate.

## Triggers

`shadcn lint`, `lint:ds`, `@shadcn/lint`, `no-restyle`, `no-raw-colors`, `no-tier-leakage`, `ds-lint`
