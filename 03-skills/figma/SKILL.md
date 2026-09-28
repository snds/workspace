---
name: figma
description: >-
  Figma authoring & code-connect hub — generate designs/components/variables on the
  Figma canvas, sync code↔design, and map Code Connect. Use when the user wants to
  create or edit something *in Figma*: build a component set, generate a library or
  screen from code/intent, author variables/modes/styles, wire Code Connect, or produce
  a diagram. Trigger on "build this in Figma", "generate a Figma library", "create the
  component set", "author the variables", "push this design to Figma", "code connect
  mapping", "make a FigJam diagram", or any canvas-authoring request. Also the explicit
  entry point for the `/figma` operation grammar (`/figma <verb> <target> [--modifiers]`).
  Canonical owner of Figma authoring + code-connect routing; delegates to the figma-*
  skills, figma-canvas-designer, and figma-plugin-dev, and uses the Figma MCP server.
  Not for judging a rendered UI (use /qa), system token decisions (use /ds), or motion
  implementation (use /motion). Load this hub + design-engineer BEFORE vendor plugin
  skills (figma-use, figma-generate-library); those are mechanics only.
user-invocable: true
argument-hint: "[generate|spec|audit|migrate|tokens] [target: code|figma|component|tokens.json|selection] [--kind component|library|design|diagram|variables] [--out <path>] [--dry]"
license: Apache-2.0
metadata:
  hub: true
  family: figma
  poc: false
  version: 0.1.0
aliases: [figma]
triggers: [figma, in figma, build in figma, component set, library file, generate a library, code connect, author the variables, stickersheet]
defers_to: [design-engineer]
governed_by: [qa, a11y-visual]
rigor_role: command-hub
spec_version: "2.2"
tier: hub
domain: design
prerequisites: [design-foundations]
related: [design-engineer, close-out]

---

# /figma — Figma Authoring & Code-Connect Hub

The canvas-authoring hub. Where `/qa` *judges* a build and `/ds` *decides* the system,
`/figma` *makes* in Figma — components, variants, variables, styles, libraries, diagrams,
and the Code Connect bridge between design and code. It is a **wrapper**: it owns trigger
vocabulary, verb dispatch, and target parsing, then delegates depth to the figma-* skill
family and the Figma MCP server. It never duplicates a base's knowledge.

Rigor obligations come from [#13 Domain Rigor Stack](../../01-frameworks/13-domain-rigor-stack.md):
this hub is the figma cluster's L2 command surface, the figma-* spokes and the MCP are the depth
(L3/L4), and **doctrine precedence holds** — workspace frameworks and skills outrank the installed
Figma plugin skills, which supply mechanics only. Component and token *decisions* stay governed by
[#09 Component & Pattern](../../01-frameworks/09-component-and-pattern-framework.md) and `/ds`; an
`audit` claim here needs a measurement path (variable/style/component inspection), not an
impression.

> **Mandatory pre-step.** Load **this hub + [[design-engineer]] before vendor plugin
> skills** (`figma-use`, `figma-generate-library`, `figma-generate-design`,
> `figma-generate-diagram`). Plugin skills supply MCP mechanics only; workspace
> doctrine wins. Then load the matching figma-* protocol skill before its tool.
> **Hard gate:** bind fill/stroke/text/spacing/radius to the target system's
> semantic + theme/mode tokens — never `Color/*` primitives on components/sets/variants.

## Operation grammar

```
/figma <verb> <target> [--modifiers]
```

- **verb** — a canonical Produce/Inspect/Transform verb (below). Omitted → `generate`.
- **target** — code, a Figma link, a component name, a token file, or `selection`.
- **modifiers** — stable flags (below).

Conversational invocation maps in: "generate a Figma library from our components" →
`/figma generate code --kind library`.

### Verbs (hub subset)

| Verb | Meaning here | Default base route |
|---|---|---|
| `generate` | Scaffold canvas artifacts: component sets, variables/modes, styles, a library, a screen, or a FigJam diagram | `figma-canvas-designer` / `figma-component-generation` / `figma-generate-library` / `figma-generate-design` / `figma-generate-diagram` |
| `spec` | Emit a build spec / handoff (anatomy → variant matrix → variable bindings) before authoring | `design-engineer` + `figma-component-generation` |
| `audit` | Evaluate an existing Figma source (variable structure, style binding, component health) | `figma-source-audit` / `figma-variable-creation` rules |
| `migrate` | Convert/repair: styles→variables, restructure collections, modes-for-variants | `figma-modes-for-variants` / `figma-style-binding` |
| `tokens` | Author or sync Figma variables ↔ design tokens (DTCG round-trip) | `figma-variable-creation` + `fe-design-tokens` |

### Targets

| Target | How it's read |
|---|---|
| `code` (path / component) | Source to translate into Figma (design-from-code) |
| `figma` (figma.com link) | Existing file/node — read via MCP (`get_design_context`, `get_metadata`, `get_variable_defs`) |
| `component` (name) | A named component to author or map |
| token file | DTCG/Style-Dictionary tokens to push as variables |
| `selection` | Current Figma selection |

### Modifiers

- `--kind component|library|design|diagram|variables` — what to author (routes to the right figma-* generator). Auto-detected from the target/intent when omitted.
- `--out <path>` — where to write specs/exports/Code-Connect maps.
- `--dry` — report the plan (which figma-* skill + MCP tools would run) without executing.

## Routing

| Intent | Lead base skill | MCP tools |
|---|---|---|
| Build/edit canvas content | `figma-canvas-designer` → `figma-use` | `use_figma`, `create_new_file` |
| Component sets / variants | `figma-component-generation` | `use_figma` |
| Full design system in Figma | `figma-generate-library` (+ ds-generation-pipeline) | `use_figma`, `create_design_system_rules` |
| Page/screen from app layout | `figma-generate-design` | `use_figma`, `get_design_context` |
| Variables / modes / styles | `figma-variable-creation`, `figma-modes-for-variants`, `figma-style-binding` | `get_variable_defs`, `use_figma` |
| Code Connect | `figma-code-connect` | `get_code_connect_map`, `add_code_connect_map`, `send_code_connect_mappings` |
| FigJam diagram | `figma-generate-diagram` | `generate_diagram`, `get_figjam` |
| Troubleshooting / API routing | `figma-error-troubleshooting`, `figma-api-router`, `figma-mcp-tool-usage` | — |

## Disambiguation — who owns what

`/figma` is the canonical owner of **Figma canvas authoring + Code Connect**. Defer when:

- **Judging a rendered UI** (the build, a screenshot, a story) → `/qa`.
- **System token/anatomy *decisions*** (what the token *should* be) → `/ds`. `/figma tokens` *binds* the decided tokens into variables; it doesn't decide them.
- **Component *code* authoring** → `design-engineer`.
- **Motion implementation** → `/motion`.

Design-vs-build comparison (Figma export vs rendered build) is a *judging* task — that's
`/qa audit <component> --against figma`, not `/figma`.

## Shared report format

For `audit`/`migrate`, return the cross-hub shape (findings · severity · fix · owner ·
summary · next). For `generate`, return: what was authored (named layers/components/
variables), where, and the verification (variant matrix complete, variables bound, modes
resolve).

## Execution protocol

These gates are the default path for every generate or edit of a component, set, variant, or nested `_Part`. They are not a later audit.

**Not an exemption:** an existing file, a recipe, a wrap, an instance of an existing primitive, a "small" component, or a one-shot append. `skillNames` on `use_figma` is telemetry. It does not load skills and it does not satisfy Gate 0.

**Not required:** Phase 0–2 of vendor `figma-generate-library` when the file already has tokens. Gates 2 and 5 still apply.

### Gate 0 — Doctrine load

No `use_figma` write until this hub and [[design-engineer]] are loaded in this turn. Vendor skills (`figma-use`, `figma-generate-library`, `figma-generate-design`) cannot be the first Figma skill.

### Gate 1 — Tokens exist

Inspect Foundations / Semantics / Density, or the target system's equivalent, before binding. A missing semantic or density token is created as an alias in that system, then bound. Never bind `Color/*` primitives on a component.

### Gate 2 — Bind before ship

Every auto-layout node inside a `COMPONENT` or `COMPONENT_SET` binds padding, gap, radius, fill, stroke, and type size. `paddingLeft` / `paddingRight` / `paddingTop` / `paddingBottom`, `itemSpacing`, radius, and height stay numeric only when no token exists — and a zero is not exempt when one does. Prefer a variable handle (`setBoundVariable`, or `$fig` when that channel accepts one) over `figma.create*` plus a numeric auto-layout assignment.

**Axis (choose one per edge):**

| Intent | `layoutSizing` | Size source |
|---|---|---|
| Compose to content | `HUG` | padding + children. Density remaps pad, type, icon, and gap. No height token on the parent. |
| Align to the control grid | `FIXED` | bound to `control-height/*` or Component / Size.height. Padding is inset inside that slot. |
| Fill the parent | `FILL` | the parent owns the slot (viewport, plot, editor canvas). |

Hugging does not turn density off. A raw unlocked pixel on that axis does. Never a FIXED height with no variable. Never hug a slot control and expect padding plus type size to equal `control-height` — those are different rungs.

**Density is the whole ladder**, not padding alone: padding, gap, control-height, type-size, icon-size, radius, container padding. File Density modes and a component Size axis stay separate. Do not collapse them into one mode, and do not drop control-height to look more tokenized.

**Type.** If the component binds `type-size/*`, `control-font-size/*`, or Component / Size.fontSize, leave `textStyleId` empty. A library Text Style applies only when no sizing or density type axis exists.

**Negative overlap.** `itemSpacing` below 0 (avatar stack, trailing cluster) may stay a literal. Say why on the node description. Do not invent a negative space token.

**Modes.** Style axes are component-scoped variable collections, one mode per value. The collection cap is 20. Before `addMode`, count. At the cap, remap a redundant alias or add a named recipe instance. Do not drop a host-facing value. A physical `VARIANT` is only for true structure. `BOOLEAN` for part presence. Nested chrome is an instance of a library atom, not a drawn duplicate.

### Gate 3 — Catalog placement

Owning `SECTION`, no AABB overlap, Title Case with spaces. `$fig.section()` at `(0,0)` with the default 496² is a defect. Measure sibling boxes, grow the parent category, and restack page-level category sections with the library gap (typically 80). The six category names are Primitives, Inputs, Layout, Navigation, Overlays, and Feedback.

### Gate 4 — From code

Read the implementation, variant map, stories, and docs before drawing. Skim hosts only to see which variant strings and tokens they pass. Classify the source: pure alias, passthrough, styled wrapper, variant map, compound, or recipe on a parent. If the anatomy is a public primitive plus props or slots, instance that primitive. A new `COMPONENT` is only for structure an instance cannot carry. Bind what the code remaps (padding and gap tokens, slot height, hug, fill, radius, type size, semantic color). Code-only behavior (hover-within, peer, keyboard, draft-until-done) gets a legal stand-in and a one-line description, not fake chrome. The stand-in catalog is [[figma-source-audit-patterns]]. Construction steps: [[figma-component-generation]].

### Gate 5 — Prove

After **each** component, not after the batch:

1. `python3 09-tools/figma-bind-probe.py --emit-template`
2. Write that node's `get_variable_defs` and `get_metadata`, per-node bindings, and a `layout` object (`sizingVertical`, `paddingTop`, `paddingBottom`, `heightBound`). Add `sections` when placing a catalog, and `collections` with mode counts when you touch a variable collection.
3. `python3 09-tools/figma-bind-probe.py --capture <scratchpad>/cap.json`

The probe refuses `Color/*`, raw spacing, radius, and height (zeros included), rects-instead-of-instances, a FIXED axis with padding and no height token, a hug that also locks height, overlapping sections, the 496² default section, and a collection over 20 modes. **Exit 2 means nothing was verified, which is not done.** Screenshot the node. `figma-bind-probe.py --self-test` proves the script, not the node. [[close-out]] exit 0 does not replace the capture. Pixels still go through `vqa prove` when a cuespec exists.

### Gate 6 — No silent skip

If a gate cannot run (MCP down, probe missing, token collection absent), stop and report the blocker. Do not ship unbound chrome.

### Order

1. **Parse** verb/target/modifiers; default `generate`, auto-`--kind`.
2. **Gate 0.** Then the matching figma-* spoke. Vendor skills after that.
3. **`--dry`?** Report the skill + MCP plan and stop.
4. **Gate 1.** Acquire the target (code, MCP read, or token file) and the collections.
5. **Gates 2–4.** Choose hug, slot, or fill. Bind. Count modes before adding one.
6. **Gate 5** on that component before starting the next. **Gate 6** if a step cannot run.
7. **Emit** named layers, where they sit, the probe exit code, and the screenshot.
8. **Hand off:** `spec` → design-engineer; system-token decisions → `/ds`. After produce, load `governed_by` lenses (`qa`, `a11y-visual`). Missing detector → mint it and push here. **Do not page Sean** unless self-critique is failing or that mint still cannot hit the bar.

## When to mint a gate vs edit one

Figma-only. Do not add a framework for this cluster. Promote the "knowledge vs enforcement" row to [[13-domain-rigor-stack]] only after a third domain hits the same skip.

| Change | Where | When |
|---|---|---|
| New reusable "when X, refuse / prove Y" | This hub's prove-gate, or [[figma-component-generation]] | The failure happened twice, or one failure is structural (agents will repeat it) |
| New instrumented check | `09-tools/` detector + Gate 5 | Prose already exists and agents skip it (hug/slot, section overlap, and the 20-mode cap are this pattern) |
| Workaround catalog | [[figma-source-audit-patterns]] | After a real code-to-canvas pass |
| Cross-domain "knowledge vs enforcement" | [[13-domain-rigor-stack]] | Only if 3+ domains need it |
| One-off fact about tools or MCP | `06-context/memory/` `type: decision` | Example: `skillNames` is logging |
| Validated construction pattern | `08-knowledge/design/` | After a real pass with evidence |
| Behavioral default | `04-preferences/` | Only on Sean's explicit signal |
| Plugin vendor text | Do not fork it | Wrap here; the vendor skill is mechanics |

Mint a gate only when all three are true: an existing gate cannot name the failure, you can state the detector (script, inspect query, or hard stop), and you know the owner skill that loads before the write.

Edit a gate when the rule is right and agents skip it (add a detector or a load-order hook, not a second paragraph), when an example contradicts the rule (fix the example), or when a real exception exists (name it in the owner skill; default stays fail-closed).

Never duplicate this hub's gates into five spokes, put employer library specifics in the vault, or treat a green `--self-test` as a pass on the node just written.

## POC scope note

Sibling to `/qa`, cloned from the same wrapper shape per `invokable-operations-spec_v0.2`.
Thin by design: the figma-* skills + Figma MCP hold the depth.

## Related
- foundation → [[design-foundations]]
- spoke → [[figma-api-router]] · [[figma-canvas-designer]] · [[figma-code-connect]] · [[figma-component-generation]] · [[figma-design-specs]] · [[figma-design-to-code]] · [[figma-diagramming]] · [[figma-ds-generation-pipeline]] · [[figma-error-troubleshooting]] · [[figma-mcp-tool-usage]] · [[figma-modes-for-variants]] · [[figma-plugin]] · [[figma-plugin-dev]] · [[figma-source-audit]] · [[figma-style-binding]] · [[figma-variable-creation]]
- governed-by → [[a11y-visual]] · [[qa]]
- peer ↔ [[design-system-ops]] · [[close-out]]
