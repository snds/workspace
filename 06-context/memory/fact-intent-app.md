---
type: fact
description: Intent.app + intentd on Personal MBP (Voyager-2.local) as of 2026-09-04
created: 2026-09-04
confidence: high
---

## For future agent
- **TL;DR:** Personal MBP has Intent.app 2.129.1 running with bundled intentd 0.9.12 over a local Unix socket. Drive it with `python3 09-tools/intent-run.py daemon` or `/Applications/Intent.app/Contents/Resources/intentd/intentd`. Do not copy `~/intent/.secrets.json` or `server.auth.token` into the vault.
- **As of:** 2026-09 · **Status:** current on Voyager-2.local only

## Facts
- App: `/Applications/Intent.app` (Electron `intent-cloudlands` user-data dir).
- Daemon: `intentd serve` (pid beside the app); socket `~/Library/Application Support/intentd/intentd.sock`; WSS 5181 off by default (loopback only if enabled).
- Provider doctor saw: Claude Code via `npx @agentclientprotocol/claude-agent-acp`. Auggie / Codex / OpenCode not on PATH.
- `git.autoCommit` set **false** 2026-09-04 (vendor default was true). Matches workspace / employer no-auto-commit doctrine. Re-check if a future Intent update resets it.
- Workspaces list was empty at first probe. Adding a repo is a GUI onboarding step, not something the vault stores.

## Vocabulary (do not mix)

| Phrase | Means |
|---|---|
| **Brain / vault / this checkout** | `~/Projects/Workspace` (`snds/workspace`). Skills, frameworks, living-spec *protocol*. Not a product codebase. |
| **Product repo** | A real git repo under the machine `Projects/` dir (Legion, ShadeGraph, LCARS, centric-ui, …). Code agents write here. |
| **Intent task** | What Intent.app labels a "workspace": one isolated git worktree for one job. |

Attach **one product repo per Intent task**, the repo the agents will change. Do not bulk-add every project. Attach this vault only when the job is changing the brain itself. Employer (`c8` / Centric) repos stay off Intent until Sean names a PR-only run.

## Do not
- Enable `server.wsApi` / `--insecure` without Sean asking (opens a TCP JSON-RPC surface).
- Point Intent at an employer checkout without the `centric-engineering` profile (no auto-commit, no self-merge).
- Treat "add a workspace" as "index the whole Projects folder."
- Expect Intent agents to load the vault skill graph. File tools and `host.exec` cwd are contained to the attached product tree (`Access denied: path outside workspace`). Global Instructions should say that. Intent notes that say "read ~/Projects/Workspace/03-skills" will fail and invite hallucinated skills. Do not paste skill bodies into Intent notes (stale copies; employer wall). Product law lives in that repo's `AGENTS.md` / `.intent/guidelines.md`. Vault skills stay on Cursor/Claude in the vault checkout.
