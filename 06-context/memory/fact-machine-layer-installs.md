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
| Personal MacBook Pro (`Voyager-2.local`) | ✅ yes | 2026-07-09 | Fix session FX-1. Doctor run clean; Drive-era hooks retired; beacon CLAUDE.md; launchd loaded. Parent-dir acceptance test GREEN. |
| Work MacBook Pro (main, `CS-K746DRWXY1`) | 🟡 partial | 2026-07-30 | Cursor layer present: `~/.cursor/hooks.json` + `cursor-sessionstart/reassert/sessionend/subagent-stop` shims installed from dist (2026-07-30 Cursor multi-agent pass). `~/.claude/workspace-brain-path` → `/Users/sean.sands/Projects/Workspace`. User Rules BEACON pasted 2026-07-30. Full `workspace-doctor.sh` + Claude SessionStart/reassert/audit + launchd still need a dedicated doctor run + `--ack-chat` (carry-over from ^pc-03). |
| Work MacBook Pro (loaner, `CS-KQ23N94M0W`) | ❌ no | — | Pending; machine may be returned. |
| Windows Desktop (`Enterprise`) | ❌ no | — | Doctor is bash/launchd (macOS); Windows path needs its own install route + one verified post-migration session. |

Install = run `00-bootstrap/doctor/workspace-doctor.sh` on that machine, then retire any
Drive-era `~/.claude/hooks/*.sh` + their `settings.json` registrations, refresh
`~/.claude/workspace-brain-path`. Update this table when a machine's state changes.

## Per-OS brain location (FX-14)

The authoritative pointer on every machine is `~/.claude/workspace-brain-path` (one line,
absolute path; doctor self-heals it on every run). Shims resolve brain-path first, then the
candidate list, testing for `AGENTS.md`:

| OS | Expected checkout |
|---|---|
| macOS (all Macs) | `~/Projects/Workspace` (case-insensitive APFS also accepts `workspace`) |
| Windows (`Enterprise`) | not yet installed post-migration — location TBD at install time (record here); shims are bash and need the Windows install route first |
