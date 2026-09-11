---
type: decision
description: Cursor beforeSubmitPrompt + shared prompt_route.py so employer-repo sessions load workspace skill doctrine
created: 2026-09-09
confidence: high
relations:
  builds-on:
    - "[[decision-bootstrap-v2-guarantee]]"
    - "[[decision-externalize-everything-to-workspace]]"
---

## For future agent
- **TL;DR:** Cursor in an employer repo does not attach `brain.mdc`; Layer-0 skill routes must be injected on `beforeSubmitPrompt` from the brain checkout (brain-path), not from CWD.
- **As of:** 2026-09 · **Status:** current

## Context — what forced a choice
A Figma component-generate session in `cpes-software/cds` skipped workspace skills that already required semantic + theme/mode-aware token bindings. Claude Code injects `trigger-routes.json` on `UserPromptSubmit`. Cursor only ran routing-adjacent hooks at `sessionStart` / `preCompact`, so vendor `figma-use` / `figma-generate-library` won.

## Decision — what we chose
Share Layer-0 matching in `09-tools/prompt_route.py`. Cursor user-global `beforeSubmitPrompt` and Claude `handle_user_prompt` both resolve the portable workspace via `~/.claude/workspace-brain-path` (then Workspace/workspace candidates). Do not bloat `brain.mdc` or User Rules with the token gate — inject on the prompt that needs it.

## Rationale — why this, not the alternatives
Always-on files are a token tax (#1 priority). A prompt-scoped hook fires the gate when `figma` / `component` / `variant` match and stays silent otherwise. Duplicating the matcher in a Cursor-only script would drift from Claude.

## Consequences — what this commits us to
Doctor must keep `00-bootstrap/dist/cursor-prompt-route.sh` + `cursor-hooks.json` in sync with `~/.cursor/hooks.json`. After skill-frontmatter edits, regenerate the registry (and rebuild snds-local so the `figma` hub is mirrored). Restart Cursor once after hook install.
