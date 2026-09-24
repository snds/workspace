---
title: Design token architecture — Subatomic canon absorbed
tags: [design-systems, design-tokens, brad-frost, ian-frost, subatomic, theming, naming, governance, figma-variables, style-dictionary]
created: 2026-09-23
updated: 2026-09-23
status: validated
confidence: high
sources:
  - "Brad Frost & Ian Frost — Subatomic: The Complete Guide To Design Tokens (courses.bradfrost.com, captured 2026-09-23; 360 lessons, ~13.6 h)"
  - "07-projects/23-subatomic-design-tokens-course/notes/ (chapter notes) + synthesis/running.md"
related_skills: [token-architecture, ds-advisor, fe-design-tokens, design-engineer, design-system-ops, ux-component-library, figma-variable-creation]
related_projects: [23-subatomic-design-tokens-course]
relations:
  builds-on: ["[[ai-and-design-systems]]", "[[cross-surface-token-parity]]", "[[nathan-curtis-ds-ops-substack]]"]
  relates-to: ["[[figma-tailwind-token-pipeline]]", "[[shadcn-lint-token-tiers]]", "[[figma-component-token-axes]]", "[[llm-safe-design-system-expressiveness]]"]
---

# Design token architecture — Subatomic canon absorbed

## For future agent

- **TL;DR:** A token system is **three tiers** (definitions → semantic jobs → rare component overrides)
  whose tiers 2–3 are a **contract/API** that every root theme must implement identically (a child theme
  implements it through parent + override). Build it
  **MVP-first against a pilot**, name it with a **per-tier algorithm** co-owned by a design + a dev
  **token czar**, publish **tier 2/3 only** by default, adopt it at three levels (reference → tokens →
  components), and govern it with SemVer lockstep releases. Full design↔code automation does not exist;
  parity is a conversation plus a checker. **L3 detector: `python3 09-tools/token-audit.py`.**
  **Procedure: [[token-architecture]] skill.**
- **Key claims:** see "The canon" below; each row cites the course chapter note.
- **As of:** 2026-09 · **Status:** current (all 8 chapters + summary; course recorded 2024–2025 with a
  Fall-2025 Figma Extended Collections update)
- **Audience:** `for: agent` + Sean

---

## Already in the workspace (do not duplicate)

| Claim | Where it already lives | What Subatomic adds |
|---|---|---|
| Three tiers (global/semantic/component) | [[09-component-and-pattern-framework]] §3; `ux-component-library/references/tokens-and-naming.md` | Tier 3 as an *earned privilege*; tier = collection = directory; themes = modes over identical tier-2/3 names; core + vanilla themes |
| Naming grammar (Curtis) | `tokens-and-naming.md` §2 | A **per-tier** algorithm: tier 1 loose/literal, tier 2–3 strict; `disabled` placement; code-only prefix + tier id |
| Components consume semantic only | [[shadcn-lint-token-tiers]], [[figma-tailwind-token-pipeline]] | Exceptions: tier-1 **spacing** (on the grid) and **z-index** (the ramp) may be consumed directly; typography only via composites |
| Parity statuses MATCH/ALIGNED/DEVIATE/FIGMA-ONLY | [[cross-surface-token-parity]] | The enumerated **sanctioned divergences** (all ALIGNED or code-only-by-design) |
| Frost canon on AI × DS | [[ai-and-design-systems]], [[18-design-systems-ai-operating-model]] | Token-specific ops: czars, pilots, SemVer lockstep, governance workflow |

## Where Subatomic and Curtis disagree (pick per system — do not pretend it's settled)

| Question | Nathan Curtis (`tokens-and-naming.md`) | Frosts (Subatomic) | Workspace default |
|---|---|---|---|
| Where do component tokens come from? | Start **inside** a component; promote after reuse | Tier 2 does the heavy lifting; a tier-3 token must **earn** its place (heavily-variable components, component categories, special cases like focus ring) | **Multi-theme systems → Frost.** A component-local value becomes a *published* tier-3 token only if it fits one of Frost's three cases (most often: it varies by theme). Single-product systems may use Curtis's local-first promotion for *semantic* roles. |
| Literal vs purposeful names | Purposeful by default; never mix in one enum | Literal is **fine at tier 1** (`helvetica`, `64`, `pink-500`); purposeful from tier 2 up | Compatible — literal tier 1, purposeful tiers 2–3. Mixed enums stay banned. |
| Theme vs mode | Orthogonal axes in the name | **One flat theme list.** Knockout/inverted = tier-2 roles inside a theme; user/OS dark mode = a **child theme of one brand** (`dark-chocolate` inherits `chocolate`, overrides colour + shadow only; code loads parent then a small override, switched by root class or `prefers-color-scheme`; Figma = a sibling mode, often a full copy). Extended Collections (Enterprise) mentioned, not demonstrated. | **Not a contradiction — Frost just doesn't practise the orthogonal model.** Model brand × mode as orthogonal; *implement* dark as a per-brand child theme whose overrides are restricted to colour + shadow (TA022) and that only overrides existing parent names (TA021). |
| Size abbreviations | Deliberate choice (readability vs brevity) | Spell words out, **except** t-shirt sizes (`sm`/`lg`) | Abbreviated t-shirt sizes OK; one vocabulary per system (TA008). |

---

## The canon (chapter by chapter)

### Why tokens (Ch1 → [[00-01-intro-and-core-concepts]])

- Tokens = design properties stored as variables to make UI themeable; the **subatomic** layer of
  Atomic Design; implementation-agnostic; the engine of theming.
- Justified by **multi-all-the-things** orgs (products, brands, sub-brands, rebrands, white-label,
  product families, colour modes, frameworks, platforms). Size the architecture to the axes the org
  actually has.
- Economics: without tokens, a brand change scales multiplicatively per touchpoint; with token +
  component systems it is a fixed cost plus small marginal cost per variant. Reuse the *curve*, not
  the illustrative dollar figures.
- **New separation of concerns:** component system = structure + behaviour; token system = aesthetics.
  Tokens can be adopted **without** the component library (recipes, native, CMS, snowflakes).

### Architecture (Ch2 → [[02-foundations-architecture]])

- **Tier 1 definitions** (raw values, the pantry) → **Tier 2 semantic** (aliases that give values jobs;
  most of the system) → **Tier 3 component-specific** (rare; may alias tier 2 *or* tier 1).
- **Theme** = the three tiers working together; **token system** = the set of themes; one theme flows
  through the component system at a time. Build three tiers even for one brand.
- Colour tier 2 has three property buckets — **background, content, border** — split content into
  text/icon only if needed. Typography, shadow, animation are **composites**. Spacing tier 1 is often
  all you need. **Start simple; add complexity only when warranted** (the course's refrain).

### Naming (Ch3 → [[03-naming-conventions]])

- Naming matters because tokens are **the API for a design language** — contract, measurement hook
  (global prefix), UX for consumers, maintainability, and the substrate for automation/AI.
- Principles: clarity over cleverness · legibility over succinctness · consistency · existing org
  conventions · convey hierarchy · pragmatism over pedantry · environment-agnostic · cross-disciplinary.
  **Structure matters more than the exact words.**
- Architecture + nomenclature **must** be co-created by design and dev leads (the only "must" in the
  course); designers then own value mapping.
- Sanctioned design↔code divergences: code-only **global prefix** and **tier identifier**; Figma's
  mandatory named `default`; **viewport ≠ breakpoint**; animation and z-index live in code; px vs
  rem; unitless line-height.
- Algorithm (template, adapt it): tier 2 colour =
  `[prefix]-[theme]-color-{background|content|border}-{intention}-{variant}-{state}` with `disabled` as
  an intention; tier 3 = `[prefix]-[theme|component]-{component|category|case}-{variant}-{property}-{state}`
  with `disabled` as a state; tier-2 type = `typography-{role}-{t-shirt}-{screen?}-{property}` →
  composite. Decide it in a small working group of leads; present to codify, not to reopen; document it
  in the path of makers.

### Building (Ch4 → [[04-building-a-token-system]])

- Mirror structure exactly: Figma **collections = tiers** (later: per-theme tier-1 collections + tier
  2/3 **modes** per theme + a **core** collection); code **directories = tiers**; a Style Dictionary
  name transform adds the tier id to tiers 2–3 only.
- **Scope** Figma variables before publishing: tier 1 unscoped; tier-2 colour scoped by property.
- Code: **rem** for font size, relative units generally, **unitless** line-height; composites bundled
  (mixins/classes, one `box-shadow` value) — **no stray `font-size`/`font-weight` in components**.
- Responsive typography is the hardest part: Figma needs a viewport collection + a design-only
  viewport-typography collection; code uses media queries with more breakpoints than Figma has viewports.
- New themes = **remapping**, not new architecture. Create **core** tokens (neutrals, utility, transparent,
  data-viz, scale, spacing, motion, z-index — org-dependent) as soon as theme 2 starts. Keep an internal
  **vanilla** theme as the architecture's x-ray. Architecture should be stable by theme 2–4.
- Sync is a **spectrum** (manual → plugin export → Tokens Studio/repo → API/SaaS); **full automation
  doesn't exist**. Two **token czars** (design + code) gate every change.

### Publishing (Ch5 → [[05-publishing]])

- A token system is a **library** ("a product serving products") — change it carefully; its primary
  users are designers and developers, so optimize designer/developer experience.
- **Don't publish tier 1 by default** (integrity over flexibility; easier to add later than retract).
- Pre-publish checklist: mappings verified in a playground/kitchen-sink, design↔code match, variables
  scoped, internal items hidden, accessible in context, clean build, docs current.
- Tokens and components are **separate libraries**. Figma: untick the default publish set and add back
  deliberately. Code: ship **built output only**, tag + GitHub release per version; start registry/DevOps
  setup early.

### Adopting (Ch6 → [[06-adopting]])

- Token adoption is "design system adoption light." Three integration levels — **reference → token
  library → component library** — form a roadmap, not a yes/no; reference-only (CMS, email) is legitimate.
- Nobody cares about tokens: the DS team teaches and pairs. Swap hard-coded values with **zero visual
  change** (verify with visual regression), then show the theme switch.
- Knockout backgrounds pair with knockout content; interactive states use browser states; one JSON
  source feeds identical platform outputs; native apps swap theme files; recipes and smart components
  obey the same no-literal rule; palette utility classes (`.color-blue`) defeat theming.

### Maintaining & evolving (Ch7 → [[07-maintaining-evolving]])

- Phases: **0.x MVP proven in a production pilot** → **1.0 after a second pilot** (then migrate pilot 1)
  → **extend + shift makers into service** (the steady state for most orgs) → optional self-service themes.
- Pilot selection: timing (committed, not started), token/component yield, scope, feasibility, enthusiasm.
- **SemVer**: add = minor, rename/remove = major, patches rare; 1.0 = stable, not complete. **Tokens and
  components release in lockstep** (same version). `main` = latest stable; branch for work (Figma
  branching or file duplication).
- Governance workflow: use → talk → educate *or* triage (bug = drop everything; new/modified token →
  core vs recipe layer; visual discrepancy → Figma-vs-code or justified product-level) → build → test
  (visual regression across themes) → validate with requester → document → release → adopt. Most
  requests end at "talk + fix the docs."

### Advanced (Ch8 → [[08-advanced]])

- **"Advanced" = situational, not harder** — each case touches a small subset of token properties.
- **Dark mode**: knockout is tier-2 roles; user/OS dark is a per-brand child theme overriding **colour +
  shadow only**, validated in pilot screens and the playground. Parent changes ripple to every child —
  regression-test all descendants.
- **Sub-brands / campaigns**: partial overrides of a parent theme, **cosmetic only** (colour, font
  family, radius). A child that fights its parent should become a standalone theme. Campaign themes
  can be scoped to a page region by class; recurring ones archived, not deleted.
- **White-label / CMS**: after 1.0; auxiliary users get a small **allowlisted** set of keys (mostly
  colour) under friendly names mapped to internal tokens; start from vanilla; Figma barely involved.
- **i18n**: colour meaning and typography (scripts, writing modes, density) vary by locale; use CSS
  logical properties.
- **Rebrands**: strategy scales with scope; wire tokens with legacy fallbacks (`var(--token, legacy)`),
  ship dark, flip at launch, then retire fallbacks as tracked debt (Caterpillar: tokens wired into Sass
  variable definitions).
- **Product families**: one system across marketing and app; density themes possible but unseen by the
  authors in client work.
- **AI**: useful as an assistant, weak as an architect — screenshot→JSON lost aliasing; AI dark mode took
  several tries. Their principles: respect, fit the org, security/privacy, humans own input *and* output,
  predictability, enhance not replace. AI output passes the same gates as human work (→ [[ai-and-design-systems]]
  steel curtain).

---

## Mechanical harness (what any agent can run)

`09-tools/token-audit.py` — vendor-neutral; DTCG or Style Dictionary JSON; files or directories. Tier comes
from the path (a `tier-1|2|3` directory; `core/` → 1 — mirror the Figma collection structure in code
directories), else `--config` `tier_prefixes` (dotted token-name prefixes, for single-file exports), else
inferred.

| Rule | Checks | Source |
|---|---|---|
| TA001–TA005 | Aliases resolve, no cycles, tier 1 raw, tier 2 aliases, no upward refs (tier 3 → tier 1 allowed unless configured) | Ch2 |
| TA006 | Tier-3 share budget (default 25%) | Ch2 |
| TA007–TA009, TA011 | Legible names, one size vocabulary, colour property buckets, one casing | Ch3 |
| TA012 | `$type` present (opt-in) | DTCG |
| TA013 | Every **root** theme exposes the same tier-2/3 API (skinny child themes are checked by TA021–022 instead) | Ch4/Ch8 |
| TA014 | Figma↔code name parity after sanctioned divergences (FIGMA-ONLY / CODE-ONLY gaps) | Ch3/Ch4 + [[cross-surface-token-parity]] |
| TA015–TA018, TA020 | Component CSS/SCSS: no colour literals (hex, functional, named), no dimension/motion/z-index literals, no tier-1 (except spacing and z-index), typography via composites, knockout background ⇒ knockout content in the same component stylesheet | Ch4/Ch6 |
| TA019 | All platform outputs expose the same token set | Ch6 |
| TA021–TA022 | Child theme overrides only existing parent names, only allowed categories — dark: colour + shadow; sub-brand and campaign: colour, font-family, radius (unchanged re-declarations ignored) | Ch8 |
| TA023 | Tier-2 content-on-background pairs ≥ 4.5:1 in every theme; translucent text composited over its background (error — a11y is not deferrable) | Ch2/Ch8 + [[a11y-visual]] |
| TA024 | A contrast pair that exists but cannot be evaluated (unsupported colour value, translucent background) — warning, blocking under `--strict` | Ch8 |

**Calibrated on the course's own demo repo** (4 themes; re-run 2026-09-24 after an adversarial review fixed
31 confirmed defects): tiers/aliases/naming clean; identical root-theme API; identical build outputs;
genuine findings only — `content-subtle` on `background-default` at 4.07:1 in three light themes, one
font-family override in `dark-chocolate`, and 30 component-CSS warnings (hard-coded greys and named
colours in the checkout page and placeholder styles, 9 local z-index integers, literal animation/transition
timings, one decorative knockout wave with no text).
Details: `07-projects/23-subatomic-design-tokens-course/synthesis/running.md`.

Product-repo CI checks the course implies but that live outside this tool (by design — see the
independence contract in [[shadcn-lint-token-tiers]]): package ships `dist` only; SemVer bump matches
the token diff; tokens/components versions equal; changelog entry per release; CODEOWNERS = both czars;
visual regression across every theme and every descendant theme; contrast checks in the playground;
`prefers-color-scheme` block and per-theme root classes in CSS output; white-label key allowlist +
translation map; rebrand fallback-debt count; CSS logical properties (stylelint); AI tooling on a
sanctioned-endpoint allowlist.

## Triggers

`subatomic`, `three-tier tokens`, `token tiers`, `tier 3 tokens`, `token naming algorithm`, `vanilla
theme`, `core tokens`, `token czar`, `token governance`, `publish tier 1 tokens`, `token adoption`,
`token-audit`
