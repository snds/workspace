---
title: Chapter 3 — Naming Conventions
course: Subatomic — The Complete Guide To Design Tokens (Brad Frost & Ian Frost)
sections: ["Chapter 3 - Naming Conventions"]
lessons: 62
status: noted
as-of: 2026-09-23
---

# Chapter 3 — Naming Conventions

Original notes (not a transcript). Raw transcripts: `<Projects>/subatomic-design-tokens-course/transcripts/03-*`.
The authors call this chapter "worth the price of admission" — most token-team pain they've seen is naming.

## Why naming matters (seven reasons)

1. **Shared understanding** — the token set is the working lexicon of a visual language; names are how
   people stop talking past each other.
2. **Collaboration** — designers, developers, tools, and now AI align on the same words.
3. **Contract** — Figma variable definitions *and applications* must match code's. Names are the handshake.
4. **Infrastructure / API** — tokens are "the API for design language"; self-explanatory names are what
   make the API usable.
5. **Traceability & measurement** — a stable global namespace (e.g. a `ds-` prefix) lets code search
   measure adoption; Figma library analytics (Org/Enterprise plans) does the same on the design side.
6. **User experience** — consumers internalize a consistent language and stop breaking flow for docs.
7. **Maintainability & automation** — consistent names make find-replace, codemods, sync to Figma/docs/CMS,
   and AI tooling trivial instead of archaeological.

## Why naming is hard

- **Invented language** — arbitrary strings that carry contract-level weight (more onomatopoeia than TypeScript).
- **Subjectivity** — the same danger button is *destructive / danger / error / caution* across Lightning,
  Primer, Material, Mailchimp. "Meticulously debated variables" (T.J. Pitre, as quoted).
- **Only some of it matters** — part of naming demands rigor, part is preference; knowing which is the skill.
- **Rigor is new to designers** — Figma Variables only arrived (beta) in 2023; layer names never shipped
  to production before, token names do.
- **Consistency over time and people** — future-you forgets; teams play telephone.
- **Designer/developer divide** — waterfall handoff calcifies; developers become "just implementers."
- **Environments differ** — design tools ≠ runtimes (Figma needs explicit state variants; code doesn't;
  z-index, breakpoints, animation are awkward or impossible in static tools).

## Naming principles (adapt to your org)

Test principles with Jared Spool's lens: grounded in research? helps you say *no*? continuously tested?

| Principle | Meaning |
|---|---|
| **Clarity over cleverness** | `typography-display-large`, not a whimsical name (their real client had a horse-themed heading name). |
| **Legibility over succinctness** | Spell it out. No decoder ring — names travel to design tools, code, AI, CMS. |
| **Consistency is key** | Pick `lg` once, use it everywhere. |
| **Use existing conventions** | If the org says "Starbucks Green", the token says it too. |
| **Convey hierarchy** | Order like a taxonomy (kingdom → species), not like speech ("brand background color"). |
| **Pragmatism over pedantry** | Equivalent words are equivalent. Decide and move on. |
| **Environment-agnostic** | Respect platform idioms, but don't skew a cross-platform system toward one platform. |
| **Naming is cross-disciplinary** | See next section. |

Overriding claim: **a sound naming *structure* matters far more than the specific words.**

## Cross-disciplinary ownership (one of the few "musts")

- Designers and developers have to author the token **architecture, structure, and nomenclature** together.
  Thrown-over-the-fence systems fail — this is the only place the authors use "must."
- Developers have decades of naming discipline; they should act as guides.
- Division of labor after the structure is agreed: **designers own value assignment/mapping**
  (which brand color feeds which role); developers implement.

## Naming parity: critical but impossible

Design ↔ code parity is required, yet static tools and runtimes differ. Known, *acceptable* divergences:

| Divergence | Resolution |
|---|---|
| **Global namespace prefix** (`ds-`) | Code only — prevents collisions and enables measurement. Figma libraries don't need it. |
| **Viewport vs. breakpoint** | Figma artboard viewport sizes and code media-query breakpoints are different concepts — manage separately, don't sync. |
| **Animation** | Definable in Figma, not usable there — lives in code. |
| **z-index** | Code concern; awkward and unused in Figma. |
| **Unnamed defaults** | Code can have `typography-display` as the default with `-large`/`-small` modifiers; Figma requires every cell to be named → explicit `default` segments. |

These must be documented as sanctioned exceptions; everything else should match 1:1.

## Naming systems — mix per category

Ramps (`red-500`), steps (`gray-1…10`), scales (`spacing-8`), t-shirt (`sm/md/lg`), timing (`fast/slow`),
named values (`cat-yellow`), named properties (`fade`, `slide`), semantic-functional
(`primary/secondary`), variant (`lightest/darkest`), category (`headline`, `background`). **Different
categories legitimately use different systems** — brute-forcing one scheme everywhere is a mistake;
consistency applies *within* a category.

Synonyms abound (tokens = design variables = theme variables…; tier 1 = definitions/base/primitives;
tier 2 = semantic/theme/usage/applied; tier 3 = component/override/pattern/element). Pick one set, publish it.

## The naming algorithm

An algorithm = a finite, repeatable procedure. Published examples: Atlassian, REI Cedar, GitLab
Pajamas, GitHub Primer, Adobe Spectrum; Nathan Curtis's taxonomy article. The course ships a FigJam
template (see Links in manifest). Naming anatomy differs by tier:

- **Tier 1** — organized by *category* (color, typography, spacing, border, shadow, animation,
  viewport, z-index) plus a **core/shared bucket** of categories identical across all themes. Decisions
  are per-category (`brand/yellow/500` vs `yellow/500`).
- **Tier 2** — ordered segments:
  `[global-prefix (code only)]-[tier id: theme|semantic]-[category]-[property: background|content|border (mostly color)]-[variant: default|brand|subtle|status…]-[state]`
- **Tier 3** — ordered segments:
  `[global-prefix]-[tier id: theme|component (optional distinction)]-[component | component-category | special-case]-[variant]-[css/style property]-[state]`
  Any CSS property can be tokenized at tier 3 — which is exactly why tier 3 must stay rare.

### Process for establishing it

1. **Small decision group**: design + dev **leads with authority** only. Open invitations derail.
2. Duplicate the template; run **real-time working sessions** (several if needed) aimed at crisp decisions,
   not esoteric debate.
3. **Present to the wider org to communicate and codify**, not to reopen — fix only egregious issues.
4. **Document** on the DS reference site; **link it from Figma and code** so it sits in the path of
   creators and consumers.

## Global conventions (code only)

- **Global prefix** (`ds-` placeholder; real systems use `slds`, `mdc`, `usa`, `cds`…): the design-system or
  org name. Namespaces against collisions (another `brand-red` from elsewhere) and marks provenance.
  Not needed in Figma — the library UI already namespaces.
- **Tier identifier** (`theme` / `semantic`, optionally `component` for tier 3): dev-only signal that
  "these are the tokens you wire up"; distinguishes the consumable API from tier-1 ingredients.
- Then the **category**: color, typography, spacing, border, shadow, animation (+ breakpoint, z-index).

## Per-category naming — their house conventions (a guide, not gospel)

### Color

- **Tier 1 — loose, maintainer-facing.** `color-yellow-100` (flat) or `color-brand-yellow-100` (grouped:
  brand / neutral / utility / data-viz). Raw names, ramps, categories, or a third-party palette
  (Tailwind, Material, Open Props) are all valid; **ramps recommended** for scalable structure. Legibility
  for the people doing the mapping is the goal. If tier 1 is ever published to consumers, naming needs
  to be clearer still (publishing is a Ch5 decision).
- **Tier 2 — "don't screw this part up."** It is the contract. Anatomy:
  `[prefix]-[tier]-color-{property|surface}-{intention}-{variant}-{state}`
  - property/surface: `background` · `content` · `border` (optionally `text` + `icon` split)
  - intention (the job): `default`, `brand`, `disabled`, `utility`, `accent`, `transparent`, data-viz…
  - variant: `default`, `strong`, `subtle`, `error|success|warning|info`, `knockout|inverted`,
    `primary|secondary|tertiary`, numbered siblings (`accent-1..3`)
  - state: `hover`, `focus`, `active`, `pressed`
  - **`disabled` lives at the intention level in tier 2** (avoids duplicating every variant).
- **Tier 3** — `[prefix]-[tier]-{component|category|use-case}-{variant}-color-{property}-{state}`,
  e.g. `button-primary-color-background-hover`. Here **`disabled` is a state**.
- Takeaway: tier 1 can be loose; **tier 2 and tier 3 must be strict** because components bind to them.

### Typography

- **Tier 1** — grouped by CSS property: `typography-font-size-*`, `-font-family-*`, `-font-weight-*`,
  `-font-style-*`, `-line-height-*` (unitless OK), `-text-transform-*`, `-letter-spacing-*` (negative
  values need a word like `minus-2` because `-` is the separator). Values follow tech conventions
  (`bold`, `uppercase`). **Descriptive-literal names are fine here** (`helvetica`, `64`) — developers
  find them "too on the nose," but tier 1 is only a mapping source. **Don't publish tier-1 typography.**
- **Tier 2** — `[prefix]-theme-typography-{intention}-{variant}-{screen?}-{property}` then clustered as
  a composite (`typography-body-sm`) that designers use as a style and developers as a mixin.
  - intentions: `display`, `headline`, `title`, `body`, `label`, `meta(data)` (+ your own)
  - variants: t-shirt sizes — they prefer **abbreviated** (`sm`, `lg`, `xl`) over `extra-extra-large`;
    whichever form, use it consistently
  - optional screen segment (`mobile`/`tablet`/`desktop`) for responsive size/line-height on large type only
- **Tier 3** — `{component}-{variant}-{property}`; mostly a size tweak or `line-height: 1` to trim text
  box whitespace. Rare.

### Spacing

- Tier 1 `spacing-{n}` on the 4/8 grid (`spacing-4 = 4`). Looks redundant; it's a useful mapping
  convention. **Unlike color/typography, tier-1 spacing may be used directly by components.**
- Tier 2 named intentions (`theme-spacing-section-break`, vertical rhythm). Tier 3
  `{component}-{variant}-{padding|margin|gap…}`.

### Border

- Tier 1 radius (+ width, rarely style) values → tier 2 `theme-border-radius-{t-shirt}` → optional
  component radius.

### Shadow

- Composite. Often defined **only at tier 2** in practice (x/y/blur/spread/color clustered); tier-1
  shadow parts are technically possible but usually overkill.

### Animation

- Tier 1 durations + easings (not the animated property, which is applied in code) → tier 2 named
  effects. Component-level animation tokens: possible; they've never shipped one.

### Breakpoint & z-index

- `breakpoint-{t-shirt}` (device names possible, not recommended); rarely co-managed with designers.
- `z-index-{100..900}` ramp so values can be slotted in between. Inclusion in the token system is optional.

## Chapter homework

1. Review existing naming (tokens, code, docs): consistent? understood? what must change?
2. Name the design + dev **leads** who own nomenclature.
3. Codify the algorithm in the FigJam template.

## For Sean

- Mechanizable now (→ `09-tools/token-audit.py`): tier-2 colour bucket position, one size vocabulary,
  no cryptic abbreviations (t-shirt abbreviations are sanctioned), theme API identical across themes,
  Figma↔code parity after the five sanctioned divergences, no tier-1 in component CSS **except spacing and z-index**.
- `disabled` placement (intention in tier 2, state in tier 3) is a subtle rule worth encoding in any
  generator that emits token names.
- "Tier 1 names can be literal" is a useful counter to reviewers who push semantic names into primitives.
