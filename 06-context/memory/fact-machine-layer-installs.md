---
type: fact
description: Per-machine install state of the 00-bootstrap machine layer (v2 hooks + doctor). Fleet is macOS-only since 2026-09-15 — the Windows desktop is retired.
created: 2026-07-09
confidence: high
---

# Machine-layer install state (bootstrap v2)

The v2 machine layer (`00-bootstrap/dist/` shims + `doctor/workspace-doctor.sh`, built 2026-07-08
at `066edac`) must be installed **per machine**. State as known:

| Machine | Installed | Date | Notes |
|---|---|---|---|
| Personal MacBook Pro (`Voyager-2.local`) | ✅ yes | 2026-07-09 | Fix session FX-1. Doctor run clean; Drive-era hooks retired; beacon CLAUDE.md; launchd loaded. Parent-dir acceptance test GREEN. |
| Work MacBook Pro (main, `CS-K746DRWXY1`) | 🟡 partial | 2026-09-09 | Cursor layer: `~/.cursor/hooks.json` now includes `beforeSubmitPrompt` → `cursor-prompt-route.sh` (Layer-0 via `prompt_route.py`; 2026-09-09). Prior: sessionStart/reassert/sessionend/subagent-stop from 2026-07-30. `~/.claude/workspace-brain-path` → `/Users/sean.sands/Projects/Workspace`. User Rules BEACON pasted 2026-07-30. Full `workspace-doctor.sh` + Claude SessionStart/reassert/audit + launchd still need a dedicated doctor run + `--ack-chat` (carry-over from ^pc-03). **2026-09-22:** (1) Claude identity overlay v4 is installed in `~/.claude/settings.json`: snds via includeIf on snds/* remotes, HTTPS transport through the Claude gh helper, employer remotes blocked. (2) Claude-only gh config lives in `~/.config/snds-workspace/gh-claude`, naming snds; the default `~/.config/gh` active account is Centric. (3) The Codex import hooks from 2026-07-31 (`~/.codex/hooks.json` + `hooks/`, and the workspace `.codex/`) are retired to `~/.config/snds-workspace/archive/codex-import-2026-07-31/`, with a README. (4) The Cursor route-injection hook is ineffective (0 of 232 injections reached a transcript); fix is in harness plan v1.1 N2. |
| Work MacBook Pro (loaner, `CS-KQ23N94M0W`) | ❌ no | — | Pending; machine may be returned. |
| ~~Windows Desktop (`Enterprise`)~~ | **RETIRED** | 2026-09-15 | **Machine is being sold (Sean, 2026-09-15) — out of the fleet.** No Windows install route is needed and none should be built. The fleet is macOS-only: Personal MBP + Work MBP (+ loaner, if kept). This closes harness-map Rec 13's Windows half; its Work-MBP half is done (`~/.cursor/hooks.json` carries `beforeSubmitPrompt`, verified 2026-09-15). |

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
