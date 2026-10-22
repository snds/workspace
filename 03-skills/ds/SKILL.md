---
name: ds
description: >-
  The design-system hub: the one entry for any design-system ask, and the `/ds` operation
  grammar (`/ds <verb> <target> [--modifiers]`). Use when the work is about a *system*, not
  a single screen: token architecture and naming, component specs (anatomy, variants,
  states, props), governance and deprecation, audits and health, generation for a stack,
  AI-ready design systems, docs voice, DDRs and strategy. It routes each ask to the one
  spoke that owns it (table below) and holds the area's standards. Trigger on "design
  system", "is this token architecture sound", "should this be a variant or a prop",
  "plan the deprecation", "design-system health", "write the DDR", or any system-level
  design decision. Not for judging a rendered interface (/qa), Figma canvas authoring
  (/figma), or code-side component questions (design-engineer, a lens).
user-invocable: true
argument-hint: "[audit|triage|tokens|spec|generate|document] [target: packages/ui|tokens.json|component|diff|figma] [--lens tokens|anatomy|governance|a11y] [--level a|aa|aaa] [--out <path>] [--dry]"
license: Apache-2.0
metadata:
  hub: true
  family: design-system
  poc: false
  version: 0.2.0
aliases: [ds, design-system-hub]
area: design-system
triggers: [ds hub, design system, design systems, design system decision, token decision, write the ddr, token architecture, design token, design tokens, semantic token, semantic tokens, design-system health, our design system, system governance]
related: [close-out, ux-component-library, infod-design-system-patterns, figma, design-engineer]
governed_by: [qa]
rigor_role: command-hub
spec_version: "2.2"
tier: hub
domain: design
prerequisites: [design-foundations]
---

# /ds — Design-System Hub

The hub for the `design-system` area (one of six hubs until 2026-10-22; now the only one).
Where `/qa` judges a rendered surface, `/ds` operates on the **system**: tokens, anatomy,
governance, and the decisions that bind them. It owns the area's trigger vocabulary, verb
dispatch and target parsing, and routes each ask to the **one spoke that owns it**. It never
duplicates a spoke's knowledge.

**Prefix rule.** `ds-` always means design system in this workspace. Data science uses
`dsci-` (renamed 2026-10-22); any future "DS"-like collision follows that template:
[[decision-skill-prefixes]].

## Spokes — one home per subspecialty

Load the one spoke the ask names; the load chain brings this hub and `design-foundations`
first.

| Subspecialty | Spoke | Typical asks |
|---|---|---|
| Strategy, triage, DDRs, stakeholders | `ds-advisor` | "too much to fix", "write the DDR", DS roadmap, PLM pattern triage |
| Component spec: anatomy, slots, variants, states, props, behaviour | `ds-component-spec` | "what states does this need", "variant or a prop", "what else moves", system fit |
| Token tiers, naming, governance, multi-brand | `token-architecture` | "name these semantic tokens", "is this token architecture sound" |
| Ops over the vendored pack: audits, drift, deprecation, health | `design-system-ops` | "audit my tokens", "plan the deprecation", "design system health" |
| Generation for a stack, and its order of operations | `ds-generation-pipeline` | "generate a design system for shadcn and Tailwind", a generation run |
| AI-ready design systems (framework #18) | `ai-design-systems` | "make our design system AI-ready", agents as users, steel curtain |
| Docs and changelog voice | `canonical-docs-voice` | component docs page, changelog note |
| Upstream source watch | `ds-source-watch` | "what changed upstream" in a reference system |
| Employer Storybook / UI workflow | `centric-ui-storybook`, `centric-ui-workflow` | (employer context only; see each spoke) |

**Linked, not owned here:** choosing which existing component fits a screen →
`ux-component-library` (UX); charts inside a design system → `infod-design-system-patterns`
(information design); Figma authoring and variables → `figma`; token engineering in code →
`fe-design-tokens`. **Lens:** `design-engineer` judges spec, generation and Storybook output
at the design × code seam after it is produced.

## Operation grammar

```
/ds <verb> <target> [--modifiers]
```

- **verb** — a canonical Produce/Inspect verb (below). Omitted → `audit`.
- **target** — what to operate on (below).
- **modifiers** — stable flags (below).

Conversational invocation works too: "audit our token architecture" resolves to
`/ds audit tokens --lens tokens`. The grammar is the precise form; organic phrasing maps to it.

### Verbs (hub subset — meaning invariant across hubs, standard differs)

| Verb | Meaning here | Default base route |
|---|---|---|
| `audit` | Evaluate the system against an explicit standard → scored report (token coverage, anatomy completeness, governance gaps) | `design-system-ops` + `fe-design-tokens` |
| `triage` | Rank findings by severity × effort → phased plan with DDR stubs | `ds-advisor` |
| `tokens` | Token-layer work: define, map (global→semantic→component), audit usage, fix tier violations | `token-architecture` (+ `fe-design-tokens` in code) |
| `spec` | Convert findings/decisions into a component or handoff spec | `ds-component-spec` (lens: `design-engineer`) |
| `generate` | Scaffold a system artifact (token set, component skeleton, DDR, governance doc) | `ds-generation-pipeline` / `ds-advisor` (DDR) |
| `document` | Author the system docs/decision record (DDR, usage guidance, migration guide) | `ds-advisor` (DDR) / `feynman`-style docs |

> `audit` is *measured* (token coverage %, tier-violation counts, anatomy/state matrices);
> `triage` is *prioritized*; `tokens` is the token-layer specialist path.

### Targets

| Target | How it's read |
|---|---|
| path (`packages/ui`, `src/`) | Source tree — scan components/styles for token usage + anatomy |
| token file (`tokens.json`, DTCG/Style-Dictionary) | Token definitions — audit tiers, naming, coverage |
| `component` (name/path) | Single component's anatomy/state/variant contract |
| `diff` | Working-tree changes — audit only what changed |
| `figma` (figma.com link) | Variable collections / library — audit via Figma MCP, design-vs-build token parity |
| `system` | The whole design system (holistic health) |

### Modifiers

- `--lens tokens|anatomy|governance|a11y` — which dimension leads. Auto-detected from the target/intent when omitted (a token file → `tokens`; "should this be a variant" → `anatomy`).
- `--level a|aa|aaa` — WCAG target when the lens is `a11y` (default `aa`).
- `--out <path>` — where to write the report + DDR drafts (default project `ds-out/` or session output).
- `--dry` — plan the operation (bases + checks that would run) without executing.

## Lens → base-skill routing

| Lens | Lead base | Adds |
|---|---|---|
| `tokens` | `token-architecture` | tier mapping, naming, alias hygiene; `fe-design-tokens` for DTCG / Style-Dictionary |
| `anatomy` | `ds-component-spec` | variant matrix, state contract, slot/prop decisions |
| `governance` | `design-system-ops` | ownership model, contribution/deprecation policy; `ds-advisor` for the DDR |
| `a11y` | `lead-accessibility-architect` + `visual-qa-accessibility` | system-level WCAG conformance posture |

Token-architecture decisions (tier collapse, semantic-vs-component, alias hygiene) are a
*decision* → `token-architecture` decides, `ds-advisor` records the DDR, `fe-design-tokens`
implements, and `design-engineer` checks the result in components. This hub sequences that
handoff.

## Disambiguation — who owns what (the precision contract)

`/ds` is the canonical owner of **design-system strategy + token routing**. Defer when a
request crosses the line:

- **Judging/measuring a rendered interface** (contrast, spacing, "what's wrong with this screen") → `/qa`.
- **Building or changing component code** → `design-engineer` (lens; code-side questions). `/ds spec` (`ds-component-spec`) produces the spec; the code follows it.
- **Figma canvas authoring / variable creation** → `/figma`.
- **Generative redesign / making it bolder / live in-browser iteration** → `/redesign` / `impeccable`.

When ambiguous ("improve our system"), name the fork once: *decide/measure* (stay in `/ds`)
vs *change it* (route to design-engineer) vs *judge the surface* (`/qa`).

## Shared report format (cross-hub convention)

Every `/ds` run returns the cross-hub shape so results are comparable and feed `triage`:

```
## DS Report — <target> · <verb> · lens:<lens> [· level:<aa>]
Standard: <what was measured/decided against>
Method:   <token coverage scan | tier validation | anatomy matrix | governance checklist>

### Findings  (severity: blocker | major | minor | nit)
- [severity] <finding> — <evidence: measured value / tier violation / missing state>
  Fix: <one line>  ·  Owner: <the owning spoke>

### Summary
<count by severity>  ·  Score: <if audit>  ·  DDRs drafted: <ids if any>

### Next
<phased plan for triage; otherwise recommended follow-up verb/target>
```

## Execution protocol

1. **Parse** verb/target/modifiers. Fill defaults (`audit`, auto-lens). Ask once only if the target is missing and nothing is attached.
2. **`--dry`?** Report the plan (bases + checks) and stop.
3. **Route**: pick the owning spoke from the table above (by lens when given); attach `fe-design-tokens` for any token measurement; `ds-advisor` for decisions/DDRs.
4. **Acquire** the target (source scan / token-file parse / Figma export / diff).
5. **Run** the base procedure + measured checks. Prefer measured (coverage %, tier-violation counts) over eyeballed.
6. **Emit** the shared report. Write to `--out` if given.
7. **Hand off** when the verb implies change (`spec` → `ds-component-spec`, `generate` → `ds-generation-pipeline`) or a governance decision (`document` → `ds-advisor` DDR).
8. **Close-out** — invoke [[close-out]].

## Scope note

Sibling to the `/qa` hub, cloned from the same wrapper shape per
`invokable-operations-spec_v0.2`. Keep this hub thin (about 1,500 words): depth lives in
the spokes above. Rearchitecture record:
[design-skill-architecture](../../07-projects/19-workspace-brain/reports/design-skill-architecture_v1.0_2026-10-22.md).

## Related
- foundation → [[design-foundations]]
- spoke → [[ai-design-systems]] · [[canonical-docs-voice]] · [[centric-ui-storybook]] · [[centric-ui-workflow]] · [[design-system-ops]] · [[ds-advisor]] · [[ds-component-spec]] · [[ds-generation-pipeline]] · [[ds-source-watch]] · [[token-architecture]]
- governed-by → [[qa]]
