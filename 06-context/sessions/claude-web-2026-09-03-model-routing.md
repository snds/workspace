---
SessionID: claude-web-2026-09-03-model-routing
Agent: Claude Sonnet 4.6
Surface: claude.ai (web)
Machine: Voyager-2.local
Date: 2026-09-03
Branch: main
Commit: 23788ee
---

## Summary

Local LLM setup and workspace model routing infrastructure session.

## What happened

- Debugged Ollama setup on M3 Max (36GB): EOF on model pulls traced to invalid
  tag names from third-party guides (not a connectivity or disk issue); resolved
  by using `ollama run gemma4` without explicit tag suffix
- Mapped open-source model recommendations to specific work contexts (DS work,
  code, reasoning, comms, Legion creative) across the local Ollama roster
- Created `02-shared-references/model-routing.md` — new canonical shared reference
  covering Ollama, Claude, Cursor, and Codex surfaces; native-first model roster
  per surface; work context → model map; effort tiers 1–4; speed signals
- Added 13 trigger phrases to `trigger-routes.json` for model selection vocabulary
  (which model, pick a model, best model for, model routing, ollama model, local
  model, cursor model, codex model, grok or claude, effort tier, etc.)
- Regenerated `trigger-routes.md` via `build-trigger-routes.py`
- Confirmed dispatcher.py loads trigger-routes.json dynamically — no hook changes needed
- Confirmed Cursor brain.mdc already reads trigger-routes.md at session start — no rule changes needed
- All validators green (validate-links, validate-capabilities, validate-workspace)
- Committed and pushed to github.com/snds/workspace main (23788ee)

## Pending

- No new pending items from this session
- GitHub MCP not surfaced in claude.ai session despite being installed; used git
  via Desktop Commander instead — consider verifying GitHub MCP connector state

## Notes

Filesystem MCP (read/write at /Users/snds/Projects) + Desktop Commander both
available this session — used both successfully. Web surface confirmed write-capable
via Desktop Commander when workspace is on local disk.
