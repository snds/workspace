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

## Do not
- Enable `server.wsApi` / `--insecure` without Sean asking (opens a TCP JSON-RPC surface).
- Point Intent at an employer checkout without the `centric-engineering` profile (no auto-commit, no self-merge).
