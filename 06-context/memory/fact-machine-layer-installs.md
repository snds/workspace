---
type: fact
description: Per-machine install state of the 00-bootstrap machine layer (v2 hooks + doctor)
created: 2026-07-09
confidence: high
---

# Machine-layer install state (bootstrap v2)

The v2 machine layer (`00-bootstrap/dist/` shims + `doctor/workspace-doctor.sh`, built 2026-07-08
at `066edac`) must be installed **per machine**. State as known:

| Machine | Installed | Date | Notes |
|---|---|---|---|
| Personal MacBook Pro (`Voyager-2.local`) | ✅ yes | 2026-07-09 | Fix session FX-1. Doctor run clean; Drive-era `resolve-skills-symlink.sh` + `workspace-bootstrap.sh` retired to `~/.claude/hooks/_retired/`; their `settings.json` registrations removed; `~/.claude/CLAUDE.md` → managed beacon (pre-beacon global-standards file backed up at `~/.claude/_retired/CLAUDE.pre-beacon-2026-07-09.md`); `workspace-brain-path` → `/Users/snds/Projects/Workspace`; launchd agent loaded. Live parent-dir acceptance test **deferred** — headless `claude -p` blocked by stale OAuth (401); offline handler executions all green. Next real session writes `OK/MISS` to `~/.claude/ws-state/audit.log` (canary). |
| Work MacBook Pro (main, `CS-K746DRWXY1`) | ❌ no | — | Runnable only there — pending item. |
| Work MacBook Pro (loaner, `CS-KQ23N94M0W`) | ❌ no | — | Pending; machine may be returned. |
| Windows Desktop (`Enterprise`) | ❌ no | — | Doctor is bash/launchd (macOS); Windows path needs its own install route + one verified post-migration session (validation report P1-13). |

Install = run `00-bootstrap/doctor/workspace-doctor.sh` on that machine, then retire any
Drive-era `~/.claude/hooks/*.sh` + their `settings.json` registrations, refresh
`~/.claude/workspace-brain-path`. Update this table when a machine's state changes.
