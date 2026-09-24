---
title: Running synthesis
project: 23-subatomic-design-tokens-course
as-of: 2026-09-23
status: graduated
---

# Running synthesis — Subatomic: The Complete Guide To Design Tokens

Original synthesis, not a transcript. Chapter depth lives in `notes/`; graduated doctrine lives in
[[design-token-architecture]] (knowledge) and [[token-architecture]] (procedure skill); the L3 detector
is `09-tools/token-audit.py`.

## For future agent

All 11 sections captured (360 videos, 358 course transcripts + Wistia captions for gaps, slides, 7 demo
repos) into `<Projects>/subatomic-design-tokens-course/`. Notes for every chapter are in `notes/`.
Surviving claims graduated 2026-09-23. Re-open only if the authors publish an update lesson (they
added a Fall-2025 Figma Extended Collections note — check the course for newer HTML items).

## Thesis

A design token system is **themeability infrastructure with an API**. Tier 1 is the pantry, tier 2 is
the contract every theme implements identically, tier 3 is a rare, earned exception. Everything else
in the course — naming algorithms, parity divergences, publishing only tiers 2–3, adoption levels,
czars, SemVer lockstep, governance triage — exists to keep that contract **legible, stable, and
shared by designers and developers**. Tools help at the edges; the course's single insistence is
cross-disciplinary collaboration.

## What was new to the workspace (vs. Curtis-based doctrine already in #09)

1. **Tier 3 must be earned** (heavily-variable components, component categories, special cases) — contradicts Curtis's local-first promotion;
   recorded as a disagreement with a context-dependent default.
2. **Structure = tier** (Figma collections, code directories) → mechanical tier resolution.
3. **Sanctioned Figma↔code divergences** enumerated (prefix, tier id, named `default`, viewport ≠
   breakpoint, code-only motion/z-index, px→rem, unitless line-height) — all ALIGNED in
   [[cross-surface-token-parity]] terms.
4. **Core + vanilla themes**; architecture stable by theme 2–4.
5. **Publish tiers 2–3 only**; tokens and components released in **SemVer lockstep**.
6. **Adoption levels** reference → tokens → components; tier-1 spacing and z-index are directly consumable.
7. **Token czars** + a governance triage tree; most requests end at "talk + docs."

## Harness calibration (2026-09-23, course demo repo `subatomic-design-tokens-course-main`)

| Run | Result |
|---|---|
| `token-audit.py core/ <theme>/ --prefix ds` × 4 themes | 0 errors, 0 warnings; tier 3 ≈ 11% (42/≈390) |
| `--themes strawberry chocolate vanilla dark-chocolate` | identical tier-2/3 API (315–337 tokens per theme dir). dark-chocolate passes only because the demo ships it as a full tier-1/2/3 copy; Ch8's skinny code override belongs under `--parent/--override`, not `--themes` |
| `--outputs build/json/tokens.json build/css/tokens.css` | identical token sets |
| `core/ --themes … --contrast` | **3 genuine WCAG failures**: `content-subtle` (#7A7E87) on `background-default` (#fff) = 4.07:1 in strawberry, chocolate, vanilla; dark-chocolate passes |
| `--parent chocolate --override dark-chocolate --kind dark` | 1 genuine drift: dark theme changes `typography.title-lg-mobile.font-family` (dark should touch colour + shadow only) |
| `--css subatomic-components/src` | 2026-09-23: 15 warnings. **2026-09-24 re-run after the review fixes: 30**, all genuine or explainable — 16 TA020 (9 local z-index integers, 2 literal animations, padding/radius/transition literals), 11 TA015 (hex greys on the checkout page, named `darkblue`/`lightblue` in the `fpo` placeholder, rgba gradient stops), 2 TA017, 1 TA018 (the hero's decorative knockout wave — no text on it, a human-confirmable warning). Authors call the demo "not production-ready" |

**2026-09-24 adversarial review** (workflow: 4 reviewers + 31 refuters): 31 findings, all confirmed and fixed
— parity exempted by meaning segment (z-index was never exempt; `media-*`/`layer-*` components were
silently dropped), declarations without `;`, Style Dictionary `{a.value}` refs, ancestor `build/`/`core/`
directories, bad input exiting 1 instead of 2, alpha-blind contrast, DTCG colour objects/hsl, named
colours, negative/animation/z-index literals, Sass `//` comments and `$vars`, campaign allowlist, doc
drift. One review recommendation was superseded by data: per-rule knockout checking misfired on 5 correct
demo stylesheets, so TA018 is judged per component stylesheet (the course's "same component").

Calibration fixes made from real data: z-index joins spacing as directly consumable tier 1; `.storybook`/docs
specimen CSS skipped; zero values exempt; tier from `tier-N` directories; knockout content pairs with
knockout background only (brand backgrounds are pale tints — an invented `content-knockout`/`background-brand`
pair produced false failures and was removed); override check ignores unchanged re-declarations
(full-copy child themes) and finds the category anywhere in tier-3 names.

## Open questions

- ~~Theme vs mode for dark mode~~ — resolved (Ch8): one flat theme list in practice, dark = per-brand
  child theme (colour + shadow only). Workspace default in [[design-token-architecture]]: model
  orthogonally, implement as restricted child themes.
- Ch8 lesson 8.13 promises an i18n Q&A recording; the course ships a different community demo in its
  place (item 336). Not a capture error.
- Value-level Figma↔code parity (TA014 checks names only). Needs a normalised value comparison
  (px↔rem at 16px, unitless line-height, alias resolution per mode) — backlog, not built.
- Figma-side checks (tier-1 unscoped, tier-2 colour scopes, publish set) need an MCP-driven probe akin to
  `figma-bind-probe.py` — backlog.
