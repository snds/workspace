---
type: decision
description: Ship thin native-filename adapters so Codex/Gemini/Copilot/Warp/Aider/Windsurf/web LLMs have a first-file path into AGENTS.md, without forking the contract.
created: 2026-09-11
confidence: high
relations:
  builds-on: ["[[decision-portable-workspace-refactor]]", "[[decision-cursor-prompt-route-hook]]"]
  relates-to: ["[[tool-adapter-discovery]]", "[[agent-load-miss-review]]"]
---

## For future agent
- **TL;DR:** Other LLMs will not reliably find the vault unless a file *they already look for* points at `AGENTS.md`. Add those pointers. Never symlink the full contract. Never add `.cursorrules` / `.windsurfrules` / `.clinerules`. Web surfaces still need a paste pack. This is not compliance.
- **As of:** 2026-09 · **Status:** current

## Context — what forced a choice
Cursor/Claude hooks inject Layer 0 on this Work MBP. Codex, Gemini CLI, VS Code Copilot Chat, Warp, Aider, Windsurf, and web ChatGPT/Grok do not run those hooks. Several of them auto-load a vendor filename and will never open `AGENTS.md` unless that filename exists. The root `README.md` also leads with the bootstrap-generator pitch, which is the wrong first page for an agent.

## Decision — what we chose
Keep `AGENTS.md` as the only contract. Add thin native-filename adapters plus Gemini/Aider config that names `AGENTS.md`. Put an agent stop-here on `README.md`. Ship `00-bootstrap/adapters/web-session.md` for paste-only surfaces. Validate that adapters mention `AGENTS.md` + `close-out` and stay short.

## Rationale — why, and what we rejected
A fat `GEMINI.md` that copies AGENTS.md would drift and, on tools that concatenate instruction files, double the token tax. Symlinks of AGENTS.md onto `GEMINI.md` have the same concatenate problem. Configuring Gemini to read AGENTS.md *and* keeping a short `GEMINI.md` covers both "settings honored" and "default filename only."

## Consequences — what this commits us to
New tools get a stub from the template + gitignore allowlist + validator row. Do not grow CLAUDE.md/CURSOR.md ritual into every stub. Windows/web still need BEACON paste. Doctor-managed `BEACON.md` stays the user-rules path; do not hand-edit it.
