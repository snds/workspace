---
name: qa
description: >-
  Visual, structural, and functional QA hub for UI, design-system, and frontend
  work. Use when the user wants to review, audit, critique, triage, or inventory an
  interface — a screenshot, a Storybook story, a live page or dev server, a Figma
  export, a component, or a working-tree diff. Covers visual craft (alignment,
  spacing, contrast, color drift, typography, grid, icon/state consistency),
  accessibility (WCAG), usability/heuristics, UX flows, and graphic-design quality.
  Trigger on "qa this", "audit this screen", "review this UI", "critique this
  component", "check the contrast/spacing", "is this accessible", "compare design vs
  build", "what's wrong with this page", or any request to evaluate an interface
  against a standard. Also the explicit entry point for the `/qa` operation grammar
  (`/qa <verb> <target> [--modifiers]`). This is the canonical owner of UI-evaluation
  routing: when the request is to *judge or measure an existing interface*, prefer
  this hub over design-engineer (which OWNS authoring/implementation), ds-advisor
  (which OWNS system strategy/decisions), or impeccable (which OWNS generative
  redesign + live in-browser variant iteration). Not for building components, writing
  tokens, Figma authoring, or backend work.
user-invocable: true
argument-hint: "[audit|critique|triage|inventory|spec] [target: screenshot|story|url|figma|component|diff|selection] [--lens ui|ux|a11y|usability|graphic|game] [--level a|aa|aaa] [--theme light|dark] [--live] [--out <path>]"
license: Apache-2.0
metadata:
  hub: true
  family: design-quality
  poc: true
  version: 0.1.0
aliases: [qa]
spec_version: "2.0"
tier: hub
domain: quality
prerequisites: [design-foundations]
---

# /qa — Visual & Functional QA Hub

The QA operation hub. Turns "look at this and tell me what's wrong" into a precise,
routed, repeatable operation. This is a **wrapper** (three-way-contract *wrapper*
layer): it owns trigger vocabulary, verb dispatch, target parsing, and the shared
report format — then delegates the actual evaluation to **base** skills that hold the
depth. It never duplicates a spoke's knowledge.

## Operation grammar

```
/qa <verb> <target> [--modifiers]
```

- **verb** — one of the canonical Inspect-family verbs (below). Omitted → `audit`.
- **target** — what to evaluate (below). Omitted → ask once; if an image is attached
  to the session, use it.
- **modifiers** — stable flags (below).

Conversational invocation works too: "qa this screenshot for accessibility" resolves
to `/qa audit <screenshot> --lens a11y`. The grammar is the precise form; organic
phrasing is mapped to it.

### Verbs (Inspect family — hub-invariant meaning)

| Verb | Meaning | Default base route |
|---|---|---|
| `audit` | Evaluate against an explicit, measurable standard → scored, structured report | `visual-qa-toolkit` (instrumented) + the lens spoke |
| `critique` | Subjective quality judgment against heuristics/taste | the lens spoke + `lead-visual-qa` |
| `triage` | Rank existing findings by severity × effort → phased plan | `lead-visual-qa` |
| `inventory` | Enumerate instances across a set (no judgment) — e.g. every icon, every component state | `visual-qa-toolkit` (`icon_consistency`, `state_comparison`) |
| `spec` | Convert findings into a fix/handoff spec | hand off to `design-engineer` (authoring owner) |

> `audit` is *measured* (deterministic scripts where possible); `critique` is *judged*
> (expert heuristics). When the user says "review," infer: pixel/standard claim →
> `audit`; "does this feel right / is this good" → `critique`. When unsure, ask once.

### Targets

| Target | How it's read |
|---|---|
| `screenshot` / image path | Session upload or provided path → `visual-qa-toolkit` |
| `story` (Storybook id or URL) | Render/screenshot the story, then audit; supports `--theme` for light/dark |
| `url` | Live page; with `--live` use the impeccable extension/live bridge (see below) |
| `figma` (figma.com link) | Pull export via Figma MCP, then audit; enables design-vs-build `visual_diff` |
| `component` (name/path) | Locate stories/states; audit rendered output |
| `diff` | Working-tree changes (current repo) — audit only what changed |
| `selection` | Current Figma/editor selection |
| `page` | The currently open preview/dev-server page |

### Modifiers

- `--lens ui|ux|a11y|usability|graphic|game` — which discipline spoke leads. **Auto-detected** from the target/intent when omitted (e.g. "contrast"/"screen reader" → `a11y`; "flow"/"onboarding" → `ux`). Multiple allowed.
- `--level a|aa|aaa` — WCAG conformance target for `a11y` (default `aa`).
- `--theme light|dark` — which theme to evaluate; for stories, audit both if omitted and the project ships both.
- `--live` — use the impeccable browser bridge for live-page work (see "Live mode").
- `--out <path>` — where to write the report + annotated images (default: project `qa-out/` or session output).
- `--dry` — plan the audit (what would run, which spokes) without executing.

## Lens → base-skill routing

The hub selects the lead **base** skill by lens; the instrumented toolkit augments any
lens that needs measurement.

| Lens | Lead base skill | Adds |
|---|---|---|
| `ui` | `visual-qa-ui-design` | `visual-qa-toolkit` (alignment, spacing, typography, grid) |
| `ux` | `visual-qa-ux-design` | `visual-qa-usability` for heuristics |
| `a11y` | `visual-qa-accessibility` | `visual-qa-toolkit` (contrast, color-vision) |
| `usability` | `visual-qa-usability` | — |
| `graphic` | `visual-qa-graphic-design` | `visual-qa-toolkit` (color Δe, palette drift) |
| `game` | `visual-qa-game-design` | for Legion / game UI |
| *(strategy/prioritization across findings)* | `lead-visual-qa` | always available for `triage` |

Instrumented measurement (contrast, SSIM, Δe, alignment, icon/state consistency) is
**always** routed through `visual-qa-toolkit` rather than eyeballed — that is the
toolkit's whole reason to exist. Read its protocol for input handling (it asks for
paths; it never hunts the filesystem).

## Disambiguation — who owns what (the precision contract)

`/qa` is the canonical owner of **evaluating an existing interface**. Neighboring
skills own adjacent concerns; defer to them when the request crosses the line:

- **Building / changing UI code, variants, props, tokens** → `design-engineer`
  (authoring owner). `/qa spec` produces the fix list; design-engineer applies it.
- **Design-system strategy, anatomy, governance, "should we…" decisions** → `ds-advisor`.
- **Generative redesign / making it bolder / live in-browser variant generation** →
  `impeccable` (owns the `live` creative loop; see below). `/qa` *judges*; impeccable
  *creates*.
- **Figma authoring / canvas generation** → `figma-canvas-designer` / `figma-plugin-dev`.

When a request is ambiguous ("make this better"), name the fork once: *measure/judge*
(stay in `/qa`) vs *change it* (route to design-engineer or impeccable).

## Live mode (`--live`) — impeccable bridge, preserved & extensible

For live-page or running-dev-server work, `/qa … --live` uses impeccable's browser
integration rather than a static screenshot. Two surfaces:

1. **Passive detection** — the impeccable Chrome **DevTools extension** detects common
   UI anti-patterns on any page. `/qa audit page --live` consumes those findings as one
   input to the audit, alongside the toolkit's measurements.
2. **Active iteration** — impeccable's **`live` mode** (local helper server + `/poll`
   SSE; `live.mjs` / `live-poll.mjs`) lets the user pick elements in-browser and get
   generated variants. This is impeccable's owned creative loop — for *generating*
   fixes, `/qa` hands off to it (`impeccable live` / `/qa polish … --live` → impeccable),
   keeping the judge/create boundary clean.

> **Preserve:** do not bypass or reimplement impeccable's live helper protocol. The hub
> *routes to* it. **Expansion seam (future):** additional workspace spokes
> (`visual-qa-accessibility`, `uid-visual-critique`, token-audit) can subscribe to the
> same `/poll` event stream so a selected element can be evaluated by the right spoke —
> the hub multiplexes spokes onto impeccable's bridge (base), via a thin wrapper. See
> `skill-ecosystem-stocktake_v0.3` Finding 3.

Claude Code policy for live polling: run the poll as a **background task** (long
timeout); the harness notifies on completion. Never block the shell.

## Shared report format (cross-hub convention)

Every `/qa` run returns the same shape so results are comparable and feed `triage`:

```
## QA Report — <target> · <verb> · lens:<lens> [· level:<aa>] [· theme:<…>]
Standard: <what was measured/judged against>
Method:   <toolkit checks run | heuristics applied | live findings>

### Findings  (severity: blocker | major | minor | nit)
- [severity] <finding> — <evidence: measured value / annotated image / heuristic>
  Fix: <one line>  ·  Owner: <qa|design-engineer|ds-advisor>

### Summary
<count by severity>  ·  Score: <if audit>  ·  Annotated: <paths if any>

### Next
<for triage: phased plan; otherwise: recommended follow-up verb/target>
```

`--out` writes the full report + annotated images to disk; the chat gets the synthesis.

## Execution protocol

1. **Parse** verb / target / modifiers. Fill defaults (`audit`, auto-lens). If target
   is missing and nothing is attached, ask once — don't hunt the filesystem.
2. **`--dry`?** Report the plan (spokes + toolkit checks that would run) and stop.
3. **Route**: pick lead spoke by lens; attach `visual-qa-toolkit` for any measured
   dimension; `lead-visual-qa` for `triage`.
4. **Acquire the target**: screenshot upload / render story / Figma export / live
   bridge as appropriate.
5. **Run** the spoke procedure + toolkit checks. Prefer measured over eyeballed.
6. **Emit** the shared report format. Write to `--out` if given.
7. **Hand off** if the verb implies change (`spec` → design-engineer) or generative
   work (`--live` polish → impeccable).

## POC scope note

v0.1.0 is the proof-of-concept hub for the operation grammar (Phase 3 of the
skill-ecosystem effort). It validates the pattern against the pending **Davinci
Storybook QA audit**. Once proven, the same wrapper shape generates the sibling hubs
(`/ds`, `/figma`, `/motion`, `/type`, `/redesign`) per
`invokable-operations-spec_v0.1`. Keep this hub thin: depth lives in the spokes.

## Related
- foundation → [[design-foundations]]
