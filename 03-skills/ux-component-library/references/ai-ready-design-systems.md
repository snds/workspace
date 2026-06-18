# AI-Ready & Agentic Design Systems — checklist, DESIGN.md, doc-gen, A2UI

> How to make the system legible to AI agents and design tools. Distilled from the AI-ready/agentic-DS canon (UX Planet, Design Systems Collective, Disco Lu, Into Design Systems), Google's `design.md`, Atlassian's field test, and the A2UI project. Companion to framework **§11 (the AI-legible layer)** and **§12 (the DESIGN.md protocol)**.

---

## 1. The AI-ready design-system checklist (4 pillars)

1. **Single source of truth — code-first.** AI tools comprehend code far better than Figma files. If you keep multiple sources, *align them* — **misalignment is the #1 cause of inconsistent AI output.** (Exemplar: IBM Carbon.)
2. **Well-structured documentation — one file, one job, explicit relationships.** The tiering rule: **Foundations describe intent · Tokens describe vocabulary · Specs describe contracts · Governance describes process.** Machine-readable formats (JSON/YAML/Markdown) let tools generate, sync, and validate. *"More stateful documentation means more predictable AI output — noticeably, not marginally."*
3. **Coded components / design-to-code parity.** What exists in the design tool matches what ships. "Developers implement components, not interpretations."
4. **Documentation & governance.** Usage guidelines, naming conventions, extension rules, and a defined component-request process.

Run this as a scorecard when auditing a system's AI-readiness; report gaps per pillar.

## 2. The 3-tier agent context architecture

Mirror of framework §1's delivery system, stated as an implementation:

1. **Always-on rules** for foundations (spacing, color, typography) — loaded every session (small, never truncated).
2. **MCP on-demand** for component retrieval — pulled only when needed (depth without bloat).
3. **`AGENTS.md` orchestration** — combines governance + routing + trust levels; points at the MCP, declares the always-on foundation rules.

**JSON over prose.** MCP is deterministic; structured data mitigates LLM randomness. Indeed benchmarked JSON at **higher accuracy with ~80% fewer tokens** vs Markdown; semantic token names measurably improve code accuracy. Proof points: Indeed parsed 77 components → JSON → 4,300 AI prototypes in 4 months; NY State fed a 5-page PDF to Claude Code → working state-styled web-component form in 13 minutes (Figma parity via Code Connect).

**Per-component packaging:** ship each component as `Component.tsx` + `Component.meta.json` (the metadata) + `Component.tokens.css` (token defs) + stories + tests that enforce token consumption. The `meta.json` is the framework §11 *component intent record* (identity / purpose / props / variants / sizes / states / usage / commonPatterns / **antiPatterns** / tokens / codeBinding).

**Token naming for agents = "reasonable English":** good `emphasis`, `subtle`, `color.action.primary`; poor `color-1`, bare `primary` with no description. Every token carries a `$description` of intent.

## 3. DESIGN.md authoring guide

`DESIGN.md` (Google) = a portable visual-identity snapshot for agents: YAML token frontmatter + Markdown rationale. Canonical section order (omit any, never reorder): **Overview → Colors → Typography → Layout → Elevation & Depth → Shapes → Components → Do's and Don'ts.** Token groups: `colors`, `typography`, `rounded`, `spacing`, `components` (+ any custom key e.g. `motion`). References: `{path.to.token}`. Lint: `npx @google/design.md lint DESIGN.md`.

**Best practices (the do's/don'ts):**
- **Specific values, not vague descriptions** — `"#2D76D4"`, not "a blue that feels trustworthy."
- **Semantic names alongside hex** — give each color a role + usage rationale so agents know what it's *for* and can validate against WCAG.
- **Negative constraints are first-class** — Do's/Don'ts prevent "technically reasonable but wrong" output. A *specific reference* ("a dense enterprise data console") carries its constraints for free; a long rambling don't-list signals the reference was too vague.
- **Formatting *is* structure** — headers + bullets parse more reliably than dense prose. The structure matters, not just the content.
- **Version-control it** — treat with the same rigor/commit discipline as code; review periodically.
- **Start simple** — begin with ~3 sections, expand as the product grows.
- **Prose over tokens is the focus** — "the quality of a generated design is determined less by the precision of its values than by how clearly the intent is described."

**Annotated template** (copy, fill, lint):
```markdown
---
version: alpha
name: <System Name>                 # required — a SPECIFIC reference, not adjectives
description: <one line>
colors:                             # primitives + a few semantic roles; specific values
  primary: "#______"                #   role + rationale belongs in the prose below
  surface: "#______"
  on-surface: "#______"
  error: "#______"
typography:                         # 9–15 levels; bundle size/weight/line-height
  headline-lg: { fontFamily: ___, fontSize: __px, fontWeight: 600, lineHeight: 1.2 }
  body-md:     { fontFamily: ___, fontSize: 16px, fontWeight: 400, lineHeight: 1.5 }
rounded:   { none: 0, sm: 4px, md: 8px, full: 100px }
spacing:   { xs: 4px, sm: 8px, md: 16px, lg: 32px }
components:                          # optional — component-level token decisions
  button-primary: { backgroundColor: "{colors.primary}", rounded: "{rounded.md}", padding: 12px }
---

## Overview
<Brand personality, audience, the emotional response. A SPECIFIC reference point.>

## Colors
<Each color: semantic role + where it's used + where it must NOT be used.>

## Typography
<Families, the voice each conveys, casing rules.>

## Layout
<Grid model, spacing rhythm, density.>

## Elevation & Depth
<Shadow vs tonal; how hierarchy is conveyed.>

## Shapes
<Radius language, iconography shape.>

## Components
<Per-component token notes; defer usage/anatomy/states to the framework + MCP.>

## Do's and Don'ts
- **Do** ...
- **Don't** ...
```

**Keep it lean.** DESIGN.md carries *visual identity only*; it must **defer component usage/anatomy/states to the framework + MCP** (this is the fix for Atlassian's "agents re-implement components" failure). Don't try to compress 50+ components into it.

### 3a. Gap-detection & self-prompting (framework §12a, operationalized)

On entering UI/build work for a project:
1. **Detect** a DESIGN.md or equivalent token+rationale source (theme file, token package, brand doc). Token source but no rationale = PARTIAL.
2. **Judge warrant:** YES when UI will be generated AND (distinct brand to honor OR multi-agent/tool/session portability matters OR output is drifting to generic "slop"). NO for throwaway/back-end work or when identity is already always-on in context.
3. **Act:** exists→load & bind · partial→offer to enrich · **absent & warranted→self-prompt** (don't silently generate unbranded UI) · absent & not-warranted→note in one line & proceed.

Self-prompt (verbatim): *"This project has no DESIGN.md to anchor its visual identity — UI generated now risks generic output and cross-session drift. I can author one from `<detected source>`: tokens (color/type/spacing/radius/elevation/motion) + brand prose + Do's/Don'ts. Generate it now so subsequent work stays on-brand?"* On approval: extract REAL tokens (never invent), write prose against a specific reference, lint, place at project root.

## 4. AI-written component documentation (drafts, you verify)

Set the reusable context **once**, then feed components:

> *"Help me create design-system documentation pages. Audience: designers, developers, content designers — new hires to seasoned pros. Tone: professional yet casual, plain language, concise bulleted lists over paragraphs. Add image-placement indicators for visual comparisons."*

**Per-component input:** `Component Name · Variants · Use-Case (one sentence)`.

**Required output hierarchy:** `H2 Overview` (1–3 sentences) · `H2 Usage` → `H3 When to Use` / `H3 When Not to Use` (with alternatives) · `H2 Variants` · `H2 Behaviors` · `H2 Accessibility` · `H2 Content Guidelines` (char limits, tone) · `H2 TL;DR`.

**Guardrails:** AI is stronger on universal components (button/card/accordion) than on proprietary variants — review those harder. Keep one running chat to preserve system context. Edit outputs directly or prompt targeted revisions; don't regenerate wholesale. **Always end on a human-verify gate** — confirm char limits and prop details the model invents. (Why docs usually fail: low priority, stale, knowledge trapped in heads — so the system stops being a shared language.)

## 5. AI-as-user evaluation (A/B testing with Claude Code)

Generate two variants from the *same* DESIGN.md/token contract (so they differ only on the dimension under test), then have the agent role-play a defined persona against each.

**Reusable input contract:** `target-user persona · user goal · business goal · the single screen under test · one measurable goal`. Output: predicted winner + friction list + rationale. **Mandatory caveat:** directional signal only — *not* a replacement for real-user testing.

## 6. A2UI integration — the agent-to-UI runtime layer

**What A2UI is.** Google's open (Apache-2.0) protocol that lets agents "speak UI": the agent streams a declarative JSON description of UI *intent*, and a client renderer maps it to its own pre-approved component library. It is the **payload** layer that rides on **A2A** (agent-to-agent transport) and is also servable over **MCP**. Used by Google Opal, Gemini Enterprise, and the Flutter GenUI SDK. Stage: early preview (production v0.9.1; v1.0 RC — "expect changes").

**Core model.**
- A **surface** (`surfaceId`, bound to one `catalogId`) = the unit of UI. UI is a **flat adjacency-list of components** linked by `id` (one must be `id: "root"`), rebuilt into a tree at render time → enables progressive streaming.
- Components live in a swappable **Catalog**, not the protocol. The Basic Catalog defines 18: `Text, Image, Icon, Video, AudioPlayer, Row, Column, List, Card, Tabs, Modal, Divider, Button, CheckBox, TextField, DateTimeInput, ChoicePicker, Slider`.
- **Layout:** flexbox-style (`Row/Column/List` + `justify`/`align`/`weight`); no pixels, no absolute positioning.
- **Styling: renderer-controlled — there is no token system in the protocol.** Agents pass only semantic hints (`Text.variant: caption|body`, `Button.variant: default|primary|borderless`). v1.0 deliberately *removed* hardcoded brand colors; web renderers theme via CSS variables. **→ DESIGN.md is the correct and only home for A2UI's visual layer.**
- **Data binding:** `DynamicString/Number/Boolean` are `oneOf` literal | `{path: <JSON-Pointer>}` | function call; the client data model is the single source of truth.
- **Actions/intent:** interactive components carry an `Action` (`event` to server, or local `functionCall`); the agent declares *semantic intent*, never pixels or executable UI code.

```jsonc
// A2UI surface fragment (basic catalog)
{ "version": "v1.0", "updateComponents": { "surfaceId": "s1", "components": [
  { "id": "root", "component": "Column", "children": ["title","cta"], "align": "center" },
  { "id": "title", "component": "Text", "text": "Click below", "variant": "body" },
  { "id": "cta", "component": "Button", "child": "lbl", "variant": "primary",
    "action": { "event": { "name": "clicked", "context": {} } } },
  { "id": "lbl", "component": "Text", "text": "Click Me" } ] } }
```

**The five integration seams** (A2UI deliberately leaves unspecified exactly what this system supplies):

| # | Seam | How |
|---|---|---|
| 1 | **Catalog ⟵ canonical taxonomy** | Emit a production A2UI catalog as a *projection* of the framework's 62-component taxonomy — restricting agents to the system's components. `ChoicePicker` covers radio/checkbox-group/select; many canonical components (combobox, popover, breadcrumb, toast…) have **no basic-catalog equivalent** → add as custom catalog components, and `log`/note the coverage gap. |
| 2 | **`ux-components` MCP as catalog source + runtime** | The MCP's per-component metadata (intent/states/anatomy/a11y) authors each catalog entry's schema + Markdown `instructions`, and is served at generation time so the agent picks the right component. a11y → `accessibility.{label,description}`; states → `variant` enums + `checks`. |
| 3 | **DESIGN.md tokens → renderer theme** | Since styling is renderer-side, export DESIGN.md tokens as the CSS-variable defaults the catalog's renderer injects; brand identity via `surfaceProperties` (`iconUrl`, `agentDisplayName`). Clean separation: agent emits intent, DESIGN.md styles it. |
| 4 | **Skill = prompt→generate→validate loop** | The skill owns catalog selection, generation guidance, and schema validation (A2UI ships a validator + conformance suite). |
| 5 | **Naming-map value-add** | The 1,900+ cross-system mappings translate a designer's component name → the correct A2UI catalog `component` key, and reconcile vocabularies when authoring a custom catalog. |

**Net:** A2UI owns the *wire format + streaming/data-binding/security*; this system owns the *components, semantics, and tokens* A2UI omits. Complementary layers. **Caveats:** spec unstable (3 concurrent families); only `accessibility.label/description` (no roles/states/anatomy taxonomy — the MCP fills this); no DTCG/Code-Connect/`design.md` references in-repo; catalog authoring is on you.

## 7. Relationships
- **Up:** framework [[09-component-and-pattern-framework]] §11 (AI-legible layer), §12 (DESIGN.md), §16 (A2UI).
- **Across:** `component-authoring.md` (the `meta.json` record), `tokens-and-naming.md` (DESIGN.md frontmatter = token export).
- **Out:** `AGENTS.md` binding (framework §14) — the always-on rules + MCP pointer + trust levels this architecture needs.
