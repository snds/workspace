---
title: Workspace Brain
type: project
status: Active
triggers: [workspace brain, workspace fix, workspace validation, error correction, verification loop]
frameworks: [qa-operating-model, integration-and-review, workspace-contribution]
created: 2026-07-09
lifecycle: define
---

# 19-workspace-brain

**Standing home for sessions whose subject is the workspace itself** — validation harnesses,
fix sessions, migrations, hook/bootstrap infrastructure, audits of the brain.

Established per the workspace-work project-home rule in
[[08-workspace-contribution-framework]] (added 2026-07-09, FX-13): workspace-subject sessions
either use this project's `SESSION-STATE.md` + Live handoff, or explicitly declare
"no project home — session-log only".

- Registered in [[project-context]] under Active Projects.
- Origin: the 2026-07-09 validation session (`workspace_validation-report_v1.0_2026-07-09.md`,
  finding P2-16) and the same-day fix session (FX-1..FX-14).
- Notes live in `notes/`; operational state in `SESSION-STATE.md`.
- Cursor canvas copies (git-tracked): `canvases/` — live compile path stays in `~/.cursor/projects/…`; `python3 09-tools/cursor-externalize.py` copies into git and mirrors back into this checkout's live folder. Employer canvases go to that repo's `canvases/`, never this vault.
- 2026-08-26 research thread: [[agentic-error-correction-foundations]] + `notes/error-correction-research_2026-08-26.md`. Mechanical close (items 1–5) landed the same day.

## Project intent

### Problem & audience

Sessions whose subject is the workspace itself (validation harnesses, fixes, migrations, hook and
bootstrap infrastructure, audits of the brain) need one standing home. The audience is Sean and every
agent surface that works in the workspace.

### Knowns & unknowns

| claim | label | tier | evidence | decision rule |
|---|---|---|---|---|
| Workspace-subject sessions need one project home, or an explicit "no project home" | known | T1 | the FX-13 rule in [[08-workspace-contribution-framework]] | — |
| The harness plan lands in waves against a held living spec | known | T1 | Live handoff: wave 0 gates closed 2026-09-24; wave 1 under way | — |
| Every agent surface gets the same walls | assumed | T4 | surfaces.json: several shared cells are still advisory or unverified | if the parity gate lists a shared gap on a minimum surface, fix it or record a waiver with a wave |
| Local seatbelts stop ordinary leaks; server-side review is the real barrier | inferred | T3 | four review rounds kept finding new bypass shapes (H17-R10) | if a new bypass class appears, add a class-level row to the public register, never the recipe |

### Out of scope & later

Employer repo work runs in Cursor or Codex, never from this project. Later: the rest of wave 1 and
the human install steps named in the Live handoff.
