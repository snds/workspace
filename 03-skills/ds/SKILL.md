---
name: ds
description: >-
  Design-system operations hub — decisions, token architecture, component anatomy,
  governance, and design/dev handoff. Use when the user wants to evaluate or evolve a
  *system* (not a single screen): audit token coverage, decide variant/anatomy
  questions, plan a migration or deprecation, draft a DDR, or turn findings into a
  handoff spec. Trigger on "audit our tokens", "is this token architecture sound",
  "should this be a variant or a prop", "plan the deprecation", "design-system health",
  "token coverage", "write the DDR", "system governance", or any system-level design
  decision. Also the explicit entry point for the `/ds` operation grammar
  (`/ds <verb> <target> [--modifiers]`). Canonical owner of design-SYSTEM strategy +
  token routing: it delegates decisions to ds-advisor and authoring to design-engineer.
  Not for judging a rendered interface (use /qa), Figma canvas authoring (use /figma),
  building one component's code (that's design-engineer directly), or backend work.
user-invocable: true
argument-hint: "[audit|triage|tokens|spec|generate|document] [target: packages/ui|tokens.json|component|diff|figma] [--lens tokens|anatomy|governance|a11y] [--level a|aa|aaa] [--out <path>] [--dry]"
license: Apache-2.0
metadata:
  hub: true
  family: design-system
  poc: false
  version: 0.1.0
aliases: [ds]
spec_version: "2.0"
tier: hub
domain: design
prerequisites: [design-foundations]
---

# /ds — Design-System Operations Hub

The system-altitude hub. Where `/qa` judges a rendered surface and `design-engineer`
authors a component, `/ds` operates on the **system**: tokens, anatomy, governance,
and the decisions that bind them. It is a **wrapper** (three-way-contract wrapper layer):
it owns trigger vocabulary, verb dispatch, and target parsing, then delegates the depth
to the base skills — `ds-advisor` (strategy/decisions/DDRs), `design-engineer`
(authoring), `fe-design-tokens` (token engineering), `ux-design-systems` (consumption
patterns). It never duplicates a base's knowledge.

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
| `audit` | Evaluate the system against an explicit standard → scored report (token coverage, anatomy completeness, governance gaps) | `ds-advisor` triage lens + `fe-design-tokens` |
| `triage` | Rank findings by severity × effort → phased plan with DDR stubs | `ds-advisor` |
| `tokens` | Token-layer work: define, map (global→semantic→component), audit usage, fix tier violations | `fe-design-tokens` |
| `spec` | Convert findings/decisions into a fix or handoff spec | hand off to `design-engineer` (authoring owner) |
| `generate` | Scaffold a system artifact (token set, component skeleton, DDR, governance doc) | `design-engineer` / `ds-advisor` |
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
| `tokens` | `fe-design-tokens` | DTCG validation, tier mapping, Style-Dictionary config |
| `anatomy` | `design-engineer` | variant matrix, state contract, slot/prop decisions |
| `governance` | `ds-advisor` | ownership model, contribution/deprecation policy, DDR |
| `a11y` | `ds-advisor` + `visual-qa-accessibility` | system-level WCAG conformance posture |

Token-architecture decisions (tier collapse, semantic-vs-component, alias hygiene) are a
*decision* → `ds-advisor` authors the DDR; `fe-design-tokens` implements; `design-engineer`
applies in components. This hub sequences that handoff.

## Disambiguation — who owns what (the precision contract)

`/ds` is the canonical owner of **design-system strategy + token routing**. Defer when a
request crosses the line:

- **Judging/measuring a rendered interface** (contrast, spacing, "what's wrong with this screen") → `/qa`.
- **Building or changing component code/variants/props** → `design-engineer` (authoring owner). `/ds spec` produces the fix list; design-engineer applies it.
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
  Fix: <one line>  ·  Owner: <ds|design-engineer|ds-advisor>

### Summary
<count by severity>  ·  Score: <if audit>  ·  DDRs drafted: <ids if any>

### Next
<phased plan for triage; otherwise recommended follow-up verb/target>
```

## Execution protocol

1. **Parse** verb/target/modifiers. Fill defaults (`audit`, auto-lens). Ask once only if the target is missing and nothing is attached.
2. **`--dry`?** Report the plan (bases + checks) and stop.
3. **Route**: pick the lead base by lens; attach `fe-design-tokens` for any token measurement; `ds-advisor` for decisions/DDRs.
4. **Acquire** the target (source scan / token-file parse / Figma export / diff).
5. **Run** the base procedure + measured checks. Prefer measured (coverage %, tier-violation counts) over eyeballed.
6. **Emit** the shared report. Write to `--out` if given.
7. **Hand off** when the verb implies change (`spec`/`generate` → design-engineer) or a governance decision (`document` → ds-advisor DDR).

## POC scope note

Sibling to the proven `/qa` hub, cloned from the same wrapper shape per
`invokable-operations-spec_v0.2`. Keep this hub thin: depth lives in `ds-advisor`,
`design-engineer`, and `fe-design-tokens`.

## Related
- foundation → [[design-foundations]]
