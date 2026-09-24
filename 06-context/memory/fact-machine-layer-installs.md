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
| Work MacBook Pro (main, `CS-K746DRWXY1`) | 🟡 partial | 2026-09-22 | Per-device install detail is held (F-14). Still needed: ^pc-03, the wave-0 human steps in ^pc-45, and removing the retired Cursor scripts (the doctor names the step while any remain installed). |
| Work MacBook Pro (loaner, `CS-KQ23N94M0W`) | ❌ no | — | Pending; machine may be returned. |
| ~~Windows Desktop (`Enterprise`)~~ | **RETIRED** | 2026-09-15 | **Machine is being sold (Sean, 2026-09-15) — out of the fleet.** No Windows install route is needed and none should be built. The fleet is macOS-only: Personal MBP + Work MBP (+ loaner, if kept). This closes harness-map Rec 13's Windows half; its Work-MBP half is done (Cursor's prompt hook is registered; detail held, F-14; verified 2026-09-15). |

Install is explicit and pinned (H24, wave 0). In a plain terminal on that machine run
`workspace-doctor.sh --install-pin`, then `--install-shims=<surface>`, `--install-claude-overlay`,
`--install-plugin` and `--install-launchd` as needed. The unattended doctor only heals the
Claude-only injectors and reports everything else. Until wave 1 pins it, that heal copies the
injectors from the checkout, not the pinned lib, and its session-start and scheduled runs use the
checkout's doctor (a declared residual; Sean, 2026-09-23).
Update this table when a machine's state changes.

## Per-OS brain location (FX-14)

The authoritative pointer on every machine is `~/.claude/workspace-brain-path` (one line,
absolute path; doctor self-heals it, HEAL class). `~/.config/snds-workspace/root` is the
tool-neutral pointer written by `--install-pin`. Shims resolve brain-path first, then the
candidate list, testing for `AGENTS.md`:

| OS | Expected checkout |
|---|---|
| macOS (all Macs) | `~/Projects/Workspace` (case-insensitive APFS also accepts `workspace`) |
| Windows (`Enterprise`) | not yet installed post-migration — location TBD at install time (record here); shims are bash and need the Windows install route first |
