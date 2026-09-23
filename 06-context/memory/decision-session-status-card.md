---
type: decision
description: Every surface emits the same session-start card (notices + all projects + pending) via session-status.py — not a Claude-only ritual.
created: 2026-09-11
confidence: high
relations:
  builds-on: ["[[decision-bootstrap-v2-guarantee]]", "[[decision-tool-native-adapters]]", "[[decision-workspace-automation-first-wave]]"]
  relates-to: ["[[workflow-patterns]]", "[[tool-adapter-discovery]]"]
---

## For future agent
- **TL;DR:** Claude Code already showed notices + last session + pending + every `SESSION-STATE` project. Cursor and other LLMs were shrinking to an ABI one-liner. The card is now `09-tools/session-status.py`. Hooks inject it; AGENTS.md requires it on the first reply of a **new** session. Continuations skip it.
- **As of:** 2026-09 · **Status:** current

## Context — what forced a choice
Sean pointed at Claude's boot card (MISS notices, 13 active projects, pending count) and asked for that reminder on every LLM. Cursor's user `sessionStart` hook only injected `[workspace: LOADED · sha]`. `brain.mdc` had shrunk Active projects to one line. Parent `~/Projects` as root often meant `brain.mdc` never attached.

## Decision — what we chose
One stdlib CLI owns the shape. Claude dispatcher shells out to it (Claude-only extras still prepend). Cursor `cursor-sessionstart.sh` injects stdout. Thin adapters name the CLI. Layer 0 routes `session status` / `what's on the agenda` to it.

## Rationale — why, and what we rejected
Re-implementing the card in each adapter (drift). Teaching models to invent a shorter summary. Ingesting `project-context-detail.md` at boot (token bomb). Requiring every surface to parse `session-log.md` by hand.

## Consequences — what this commits us to
`workspace-doctor.sh --install-shims=cursor` (human-run) installs `00-bootstrap/dist/cursor-sessionstart.sh` as `~/.claude/hooks/cursor-sessionstart.sh`; the doctor only reports drift. Do not shrink Active projects. Do not dump the card on a continuation. `session-status.py --check` is in the write-quality chain.
