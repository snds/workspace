---
title: Chapter 2 — Foundations & Architecture
course: Subatomic — The Complete Guide To Design Tokens (Brad Frost & Ian Frost)
sections: ["Chapter 2: Foundations & Architecture"]
lessons: 28
status: noted
as-of: 2026-09-23
---

# Chapter 2 — Foundations & Architecture

Original notes (not a transcript). Raw transcripts: `<Projects>/subatomic-design-tokens-course/transcripts/02-*`.

## MVP first

Diagnostic move: run a site through a CSS-stats tool and look at the spread of "almost-brand" colors
(their T-Mobile example surfaces many near-identical pinks). Every org has close-but-not-quite brand
values; the MVP token system exists to collapse them to one source.

The MVP is built in three steps, identically in Figma Variables and CSS custom properties:

1. **Tier 1** — a variable holding the raw value (`pink`). Wire components to the library variable,
   not a local/custom value.
2. **Tier 2** — a variable that *aliases* tier 1 and names the job (`brand → pink`). Components move to
   `brand`. Now swapping brand to blue touches zero components.
3. **Tier 3** — a component variable (`button-background → blue`) so one component can deviate from
   the theme.

That is a complete token system. **Build up only as real needs demand** — design-system people drift
into speculative "what if one day" architecture; resist it.

## The three-tier architecture (the backbone)

| Tier | Also called | Job | Values |
|---|---|---|---|
| **1 — Definition** | primitive, core, global | The pantry: every available ingredient (ramps, scales). Not everything here gets used. | Raw values |
| **2 — Semantic** | alias, theme, role | Gives tier-1 ingredients **jobs** in a UI (`color-background-brand`). Does the heavy lifting. | Alias → tier 1 |
| **3 — Component-specific** | override, component, special-case | Narrow deviations for one component, a component category, or a special case. | Alias → tier 2 **or** tier 1 (either is fine) |

**Alias** = a variable whose value is a reference to another variable (`{color.green.starbucks}` in
Style Dictionary JSON; library alias in Figma).

### Tier 3 is a privilege, not a default

- Cautionary tale: orgs managing **4,000+ tokens** because every property of every variant of every
  component got its own token. Unwieldy; don't.
- House rule they teach teams: adding a tier-3 token should feel like it had to **earn** its place.
- Legitimate tier-3 cases:
  1. **Heavily variable components** — buttons (some themes use brand color, others neutral/black, others
     an A/B-tested color).
  2. **Component categories** — one `input-border` shared by text input, textarea, select.
  3. **Special cases** — focus ring (assistive, must be controllable), highlighted table row, chart/data
     specifics.
- Everything else should resolve through tier 2 (Polaris: form labels and input text simply inherit the
  default tier-2 content color).

## Themes and the token system

- **Theme** = the three tiers operating together to express one visual language.
- **Design token system** = the collection of themes (1, 2, 12, 300 — Pfizer has 300+ consumer brands;
  the Frosts built the architecture + first several themes).
- Precision: **one theme** at a time flows through the component system to produce a result (Verywell /
  Verywell Mind / Verywell Fit = three themes, one shared "vanilla" component set).
- Build three tiers **even for a single brand** — the redesign is coming, and the tiers absorb it.

## Category playbook

All categories fit the three tiers. **Color and typography carry disproportionate impact** — prioritize them.

### Color

- Four lenses for a UI color system: **brand, visual harmony, UX meaning, accessibility**.
- Brand books are rarely digital-ready; the DS team *interprets* them (Cat yellow used sparingly as accent
  + primary button). Vox Media: one system, many brands, color carries each brand's ethos.
- UX meaning: standard status semantics (info/success/warning/error) plus domain semantics (Nasdaq
  up/down; QuickBooks income/expense/liability/blocker).
- Accessibility: contrast (WCAG checkers, Figma Contrast plugin, DevTools) and color-vision deficiency
  (who-can-use-style simulation). Gray-on-light-gray is the canonical anti-pattern.
- **Tier 1**: ramps grouped (brand / neutral / utility / transparent) *or* flat rainbow ramps (Material
  style). Naming matters less here — but **reuse the org's existing names** ("Cat Yellow" stays "Cat Yellow").
- **Tier 2**: three buckets — **background, content, border** — each with `default` plus variants
  (`subtle`, `strong`, `brand`, `knockout`, status…). Content = text + icons. Split content into separate
  text/icon buckets **only if needed** (Polaris does; it costs maintenance).
- **Tier 3**: `button-[variant-]color-{background|content|border}`, `link-*`, form-control category tokens.

### Typography

- Same four lenses; font pairing and type scale are the big visual decisions. Which scale (modular,
  Fibonacci, t-shirt, even animal names) matters less than **having** one.
- Typography is a **composite token** (DTCG: made of named child values that travel together).
- **Tier 1**: separate ingredient sets — families, sizes (the ramp), line-heights, weights, letter-spacing,
  text-transform.
- **Tier 2**: role composites — `display`, `headline`, `title`, `body`, `label`, `meta` (a.k.a.
  eyebrow/overline), plus optional domain roles (chart/data) — each with size variants.
- **Tier 3**: rarer than for color (`typography-button`); composites allow **partial overrides**
  (change line-height, keep the rest).

### Spacing

- 8pt grid (4pt for finer steps). Tier 1 integers are often **all you need**, applied directly in components.
- Tier 2 only for real semantic constants (e.g. `section-break` spacing between major page regions).
- Tier 3 possible (`button-padding-x/y` per theme).

### Border

- Radius matters most, width sometimes, style almost never.
- Tier 1 on the grid (2/4/8/16/32 + `round`); tier 2 as one theme radius or t-shirt sizes
  (none/sm/md/lg); applied across inputs/cards/badges. Often one radius value suffices.

### Shadow

- Composite (color from transparent tier-1 colors + x/y/blur/spread). Values are judged by eye — they
  don't affect the box model. Tier 2 = one theme shadow or a small t-shirt set. Tier 3 rare.

### Animation

- Composite (duration + easing + animated property). Tier 2 names the motion (`fade-quick`, `slide`).
  Naming animations is hard; borrow vocab (Lightning: fade/grow/shrink/rise/lower; Carbon motion).

### Breakpoints & z-index

- Token-able but odd; deferred to Chapter 4 (handled differently).

## Chapter homework (reusable audit)

Map existing variables/styles onto the three tiers: what's missing, what should be added, and what is
excess — **especially at tier 3**.

## For Sean

- The audit questions are mechanizable: tier classification of every token, tier-3 ratio, alias depth,
  hardcoded values in components. → candidate harness (`token-tier-audit`).
- "Tier 3 may alias tier 1 directly" differs from stricter rules some systems enforce (tier 3 → tier 2
  only). Treat it as allowed-by-default but lintable per system.
- Background / content / border as the tier-2 color buckets is a clean default; the text/icon split is
  an opt-in with a stated cost.
