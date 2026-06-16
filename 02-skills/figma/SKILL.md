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
  implementation (use /motion). Load the relevant figma-* skill (e.g. figma-use) before
  calling the matching MCP tool.
user-invocable: true
argument-hint: "[generate|spec|audit|migrate|tokens] [target: code|figma|component|tokens.json|selection] [--kind component|library|design|diagram|variables] [--out <path>] [--dry]"
license: Apache-2.0
metadata:
  hub: true
  family: figma
  poc: false
  version: 0.1.0
---

# /figma — Figma Authoring & Code-Connect Hub

The canvas-authoring hub. Where `/qa` *judges* a build and `/ds` *decides* the system,
`/figma` *makes* in Figma — components, variants, variables, styles, libraries, diagrams,
and the Code Connect bridge between design and code. It is a **wrapper**: it owns trigger
vocabulary, verb dispatch, and target parsing, then delegates depth to the figma-* skill
family and the Figma MCP server. It never duplicates a base's knowledge.

> **Mandatory pre-step.** The figma-* skills gate the MCP tools. Load the matching skill
> *before* calling its tool: `figma-use` before `use_figma`; `figma-generate-diagram`
> before `generate_diagram`; `figma-generate-library` for library builds;
> `figma-code-connect` for Code Connect. This hub routes; the skills hold the protocol.

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

1. **Parse** verb/target/modifiers; default `generate`, auto-`--kind`.
2. **Load the gating figma-* skill** for the resolved intent (mandatory) — then its MCP tools become callable.
3. **`--dry`?** Report the skill + MCP plan and stop.
4. **Acquire** the target (code scan / MCP read of the Figma node / token-file parse).
5. **Run** the base procedure. Apply variables/styles — never raw values (token-first).
6. **Emit** the report (authored artifacts or audit findings).
7. **Hand off**: `spec` → design-engineer; system-token decisions → `/ds`.

## POC scope note

Sibling to `/qa`, cloned from the same wrapper shape per `invokable-operations-spec_v0.2`.
Thin by design: the figma-* skills + Figma MCP hold the depth.
