---
type: fact
description: "Per-machine install state of the 00-bootstrap machine layer (v2 hooks + doctor). Fleet: Personal MBP, Work MBP and the Windows desktop `Enterprise` (back in use 2026-10-14; not yet installed)."
created: 2026-07-09
updated: 2026-10-14
confidence: high
---

# Machine-layer install state (bootstrap v2)

The v2 machine layer (`00-bootstrap/dist/` shims + `doctor/workspace-doctor.sh`, built 2026-07-08
at `066edac`) must be installed **per machine**. State as known:

| Machine | Installed | Date | Notes |
|---|---|---|---|
| Personal MacBook Pro (`Voyager-2.local`) | ✅ yes | 2026-07-09 | Fix session FX-1. Doctor run clean; Drive-era hooks retired; beacon CLAUDE.md; launchd loaded. Parent-dir acceptance test GREEN. |
| Work MacBook Pro (main, `CS-K746DRWXY1`) | 🟡 mostly | 2026-10-14 | `--install-pin` (`1108a00`), `--install-git-hooks` and `--install-claude-overlay` (v6) run by Sean, plus one plain doctor run; the session-start hook and `~/.claude/CLAUDE.md` are healed (verified with `--check`). Still open: `--install-launchd` (the doctor timer is not loaded), and the Codex / `~/Projects` / home beacon drift the doctor names. Per-device detail is held (F-14). |
| ~~Work MacBook Pro (loaner, `CS-KQ23N94M0W`)~~ | **RETIRED** | 2026-09-23 | **No longer in use (Sean, 2026-09-23).** Removed from `devices.json`; the Work MBP (main) is the only work machine. |
| Windows Desktop (`Enterprise`) | ⬜ not installed | 2026-10-14 | **Back in active use: Sean's personal desktop (Sean, 2026-10-14).** This reverses the 2026-09-15 retirement ("being sold — out of the fleet"). It needs the Windows install route (the shims are bash; `devices.json` gives home `/c/Users/SNDS`), so harness-map Rec 13's Windows half is open again. Its Work-MBP half stays done (Cursor's prompt hook is registered; detail held, F-14; verified 2026-09-15). |

Install is explicit and pinned (H24, wave 0). In a plain terminal on that machine run
`workspace-doctor.sh --install-pin`, then `--install-shims=<surface>`, `--install-claude-overlay`,
`--install-plugin` and `--install-launchd` as needed. Since D-W1-4 (2026-09-25) `--install-claude-overlay`
installs the Claude-only env-file channel; once a new Claude shell's probe records `WS_OVERLAY_CHANNEL`,
`--install-claude-overlay-retire-env` removes the older copy from `~/.claude/settings.json` env. The unattended doctor only heals the
Claude-only injectors and reports everything else. Since D-W1-6 (H20, walls F-11) that heal copies
only from the pinned lib (never the checkout; nothing pinned = report only), and session start and
launchd run the pinned doctor through `~/.config/snds-workspace/bin/ws-doctor`, which the pin installs.
Per machine the residual closes after `--install-pin` (adopts the heal sources, the doctor and
`bin/ws-doctor`), one plain `workspace-doctor.sh` run (heals the hooks from the new pin) and
`--install-launchd` (the job then runs `bin/ws-doctor`). Every later change to a heal script, the
user CLAUDE.md or the doctor reaches the machine only through a re-pin; the doctor reports
"vault differs from pin" until then.
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
