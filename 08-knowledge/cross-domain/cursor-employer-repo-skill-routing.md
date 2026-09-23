---
tags: [workspace, cursor, harness, skills, routing, figma, tokens]
created: 2026-09-09
updated: 2026-09-09
status: stable
confidence: high
sources: [cds Object Chip Figma generate session 2026-09-09]
related_skills: [figma, design-engineer, figma-component-generation, workspace-bootstrap]
related_projects: [19-workspace-brain]
---

# Cursor employer-repo skill routing

## For future agent

When Cursor is opened on an employer repo (`cpes-software/cds`, centric-ui, …) **Brain is not
folder 1**. `brain.mdc` does not attach. Vendor Figma plugin skills (`figma-use`,
`figma-generate-library`) still appear in the tool/skill list as **MANDATORY** and will win
unless Layer-0 workspace routes are **injected on the prompt**.

**Do not skip** `03-skills/figma/SKILL.md` + `03-skills/design-engineer/SKILL.md` +
`08-knowledge/design/figma-ds-surface-authoring.md` before generating components/sets/variants.
Hard gate: bind **semantic + theme/mode tokens** (Light/Dark, Density) — never `Color/*`
primitives. Missing token → create a semantic alias in the **target** system, then bind.

## What failed (2026-09-09)

The token rule already existed (design-engineer Token Enforcement, figma hub “never raw
values”, figma-ds-surface-authoring total tokenization). It did not fire because:

1. Curated `"figma"` route loaded canvas-designer + design-engineer for *real-library-components
   only* — not the figma hub, not FIGMA_GENERATE_ROUTE, not FOUNDATION_ROUTE.
2. Skill `triggers:` missed spoken phrasing (`build in figma`, `component set`, `library file`).
3. Claude `UserPromptSubmit` injects trigger-routes; Cursor only had `sessionStart` +
   `preCompact`. `cursor-reassert.sh` comments mentioned `beforeSubmitPrompt` but was never
   registered on that event. (Both scripts retired 2026-09-22 to `_archive/cursor-dark-shims-2026-09/`.)
4. snds-local plugin mirrored canvas-designer but **not** the `figma` hub, so employer-repo
   Cursor never saw “plugins = mechanics” in available skills.
5. Agents loaded Cursor plugin `figma-use` / `figma-generate-library` first because those
   skills say MANDATORY before every MCP call.
6. Wrapped YAML `triggers: [` lists were stored as a string; iterating a string matched
   every letter (`a` in “as a component set”) and stole registry slots. Parser now joins
   until `]`; `prompt_route` ignores non-list triggers and 1-character terms.

## What to load (the path)

Retired 2026-09-22 (the injection never reached the model; the H7 `ws route` steer replaces it,
and the scripts are in `_archive/cursor-dark-shims-2026-09/`). The path was: user-global
`~/.cursor/hooks.json` `beforeSubmitPrompt` →
`~/.claude/hooks/cursor-prompt-route.sh` → `09-tools/cursor-prompt-route.py` →
`09-tools/prompt_route.py` (resolves `~/.claude/workspace-brain-path`, then
`~/Projects/Workspace` / `workspace`). Matches `trigger-routes.json`,
`knowledge-hints.json`, `skills.registry.json`, `08-knowledge/_INDEX.md`.

Claude dispatcher `handle_user_prompt` uses the same `prompt_route.py` and the same brain
resolver, so employer-repo Claude sessions also get Layer 0 even when
`CLAUDE_PROJECT_DIR` is not the brain.

Vendor Figma plugins remain the MCP **mechanics**. Workspace skills own doctrine.
