---
name: token-architecture
description: >
  Procedure for designing, naming, building, publishing, adopting, and governing a three-tier design
  token system (Brad Frost & Ian Frost "Subatomic" canon): tier 1 definitions → tier 2 semantic jobs →
  rare tier 3 component overrides; themes as modes over an identical tier-2/3 API; core + vanilla
  themes; per-tier naming algorithm; sanctioned Figma↔code divergences; publish tier 2/3 only; three
  adoption levels; token czars; SemVer lockstep with components; governance triage. Trigger on
  three-tier tokens, token tiers, tier 3 tokens, token naming algorithm, naming tokens, vanilla theme,
  core tokens, token czar, token governance, publishing tier 1 tokens, token adoption levels,
  multi-brand token architecture, adding a theme to a token system, or "subatomic". Measured by
  09-tools/token-audit.py. Strategy stays with ds-advisor; the Style Dictionary / Figma-sync pipeline
  with fe-design-tokens; drift/health ops with design-system-ops.
aliases: [token-architecture, subatomic, three-tier-tokens]
triggers: [subatomic, three-tier tokens, three tier tokens, token tiers, tier 3 tokens, tier-3 token, token naming algorithm, naming tokens, token naming convention, vanilla theme, core tokens, token czar, token czars, token governance, publish tier 1, token adoption, multi-brand tokens, new theme tokens, token-audit]
tier: spoke
domain: design
hub: ds-advisor
prerequisites: [ds-advisor]
related: [fe-design-tokens, design-system-ops, design-engineer, ux-component-library, figma-variable-creation, ai-design-systems]
governed_by: [qa, a11y-visual]
defers_to: [framework-09, framework-13, ds-advisor]
rigor_role: command-hub
surfaces: ["*"]
spec_version: "2.2"
---

# Token architecture — procedure

L2 command surface for the token layer of [[09-component-and-pattern-framework]] (§3 tiers). Doctrine
and provenance: [[design-token-architecture]] (Subatomic canon, Curtis disagreements, harness table).
Course notes: `07-projects/23-subatomic-design-tokens-course/notes/`. **L3:** `python3 09-tools/token-audit.py`.

## When to use

Designing a token architecture, adding a theme/brand/mode, naming tokens, deciding what to publish,
planning adoption, or setting up token governance — in Figma variables, code (Style Dictionary/DTCG),
or both.

## When NOT to use

- Style Dictionary transforms, Figma REST sync, CSS cascade/`@layer` mechanics → [[fe-design-tokens]]
- Drift detection, deprecation plans, health reports on an existing system → [[design-system-ops]]
- Binding variables on a Figma canvas → [[design-engineer]] + [[figma]] (mechanics)
- Component anatomy/props → [[ux-component-library]]
- Authoring *inside* a specific system (e.g. an employer DS): resolve in **that** system's tokens and
  naming; this procedure informs gap backlogs, it does not import Frost names into their system.

## Procedure

1. **Size the problem.** List the org's real multi-all-the-things axes (brands, sub-brands, modes,
   product families, platforms, frameworks, rebrand horizon). Architecture complexity follows those
   axes, not hypotheticals.
2. **MVP against a pilot.** One real production pilot (committed, not started; good token yield). Build
   one colour through all three tiers in Figma *and* code before expanding. Versions stay `0.x`.
3. **Structure = tier.** Figma collections per tier (per-theme tier-1 collections, tier-2/3 modes per
   theme, a `core` collection); code directories per tier. Configure `token-audit.py` `tier_prefixes`
   to the same structure so tier is never guessed.
4. **Name with an algorithm** (small group of design + dev leads; codify, document in the makers' path):
   tier 1 loose/literal and ramp-based; tier 2 `category → property/surface → intention → variant →
   state` (colour buckets background/content/border; `disabled` = intention); tier 3
   `component|category|case → variant → property → state` (`disabled` = state); code-only global prefix
   + tier id; one t-shirt vocabulary.
5. **Tier 3 must earn its place:** heavily-variable components (buttons), component categories (form
   controls), special cases (focus ring, highlighted row). Everything else resolves via tier 2.
6. **Composites for typography, shadow, motion;** consumers get one bundle (style / mixin / class /
   single `box-shadow`). Responsive type is absorbed by the system, not by consumers.
7. **Advanced axes are situational** (dark mode, sub-brands, campaigns, white-label, i18n, rebrand,
   AI): each is a child theme or a restricted override of a parent, never a new architecture. Dark =
   colour + shadow only; sub-brand = cosmetic only; white-label = allowlisted keys after 1.0.
8. **Second theme = remap + core.** Clone, remap aliases, extract `core` immediately, add an internal
   **vanilla** theme; expect architecture churn until theme 2–4, then stability.
9. **Publish tier 2/3 only** (tier 1 unscoped + hidden in Figma; not exported in the package unless a
   documented exception). Run the pre-publish checklist; ship built output only; tokens and components
   are separate libraries released in **SemVer lockstep**.
10. **Adopt by level:** reference → token library → component library. Swap hard-coded values with zero
   visual diff (visual regression), then demo the theme switch.
11. **Govern:** two token czars own design + code; triage every request (educate / bug / new-or-modified
    token at core-vs-recipe layer / visual discrepancy); add = minor, rename/remove = major.
12. **Measure** (below) before claiming the system is sound.

## Measurement (L3)

```bash
python3 09-tools/token-audit.py --self-test
python3 09-tools/token-audit.py --config token-audit.config.json tokens/**/*.json
python3 09-tools/token-audit.py --themes themes/*.json              # identical tier-2/3 API
python3 09-tools/token-audit.py --parity figma.json code.json --prefix ds
python3 09-tools/token-audit.py tokens.json --css src/components --prefix ds
python3 09-tools/token-audit.py --outputs dist/tokens.css dist/_tokens.scss dist/tokens.json
python3 09-tools/token-audit.py --parent brand/ --override brand-dark/ --kind dark   # colour + shadow only
python3 09-tools/token-audit.py core/ --themes brand-a/ brand-b/ --contrast           # WCAG per theme
```

Errors (TA001–005, TA013, TA021, TA023) block; warnings are review items. Product-repo CI owns: `dist`-only package,
SemVer-vs-diff, lockstep versions, changelog, CODEOWNERS = both czars, visual regression per theme,
contrast in the playground. Figma-side checks (tier-1 unscoped, tier-2 colour scopes) run via the Figma
MCP (`get_variable_defs`) — capability `figma-mcp`, degrade to a manual checklist if absent.

## Contrast example

**Bad —** a button variant needs a different colour in one brand, so the team adds
`button-primary-background`, `button-primary-background-hover`, … for *every* component and every
property "for flexibility." Tier 3 hits 60% of the system (TA006); themes drift (TA013); the next brand
takes weeks.

**Good —** buttons (heavily variable across brands) get tier-3 tokens aliasing tier 2; cards, inputs,
and text keep binding tier-2 `background-default`, `content-default`, `border-subtle`; a form-controls
category token covers input borders. A new brand is a remap of tier-1 + two modes.

**Why —** tier 2 is the contract; tier 3 multiplies maintenance per theme. Tokens exist for themeability,
so a component token is justified only by variation *across themes*.

## Defers to

[[09-component-and-pattern-framework]] (tier model, purposeful naming), [[13-domain-rigor-stack]],
[[ds-advisor]] (strategy, triage). Curtis vs Frost disagreements and the workspace default are recorded
in [[design-token-architecture]] — cite them rather than re-deciding.

## Related
- hub → [[ds-advisor]]
- governed-by → [[a11y-visual]] · [[qa]]
