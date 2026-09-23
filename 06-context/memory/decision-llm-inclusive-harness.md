---
type: decision
description: Every workspace harness change is LLM- and device-inclusive by construction — one tool-neutral mechanism, thin per-surface shims, a declared coverage row per surface (min Claude Code, Claude Chat, Cursor, Codex), repos keyed by remote and resolved per device (Work + Personal MBP).
created: 2026-09-22
confidence: high
relations:
  builds-on: ["[[decision-portable-workspace-refactor]]", "[[decision-tool-native-adapters]]", "[[decision-one-matcher-per-workspace]]"]
  relates-to: ["[[zero-vector-design-methodology]]"]
---

## For future agent
- **TL;DR:** No harness mechanism may depend on one LLM or one vendor surface. The logic lives in the
  workspace (stdlib `09-tools/*.py`, declared data, git hooks, CI). Each surface gets a thin shim, and
  each component declares how it behaves per surface, including an honest "cannot enforce here".
  Minimum surfaces: **Claude Code, Claude Chat, Cursor, Codex**. Add others where feasible.
- **As of:** 2026-09 · **Status:** current

## Context — what forced a choice
Sean approved wave 0 of the Zero-Vector harness plan on 2026-09-22, on one condition: this work and
**any** later workspace harness work must scale beyond Claude. The workspace is LLM-independent /
LLM-inclusive as a first-class concept. The v1.0 plan leaned on Claude Code hooks: the SessionEnd heal
and gate, and a user-global Claude `PreToolUse` wall guard. The Zero-Vector tooling it drew on is
Claude Code-specific.

## Decision — what we chose
1. **One mechanism, many shims.** Behaviour is implemented once, in a surface-neutral place: a
   `09-tools` CLI, a declared JSON table, git hooks, or CI. Vendor hooks (Claude, Cursor, Codex, …)
   only call that one implementation, following the `prompt_route.py` pattern. They never re-implement
   it.
2. **Coverage is declared, not assumed.** Every harness component carries a per-surface row
   (enforced / advisory / not applicable), stating how enforcement happens there. When a surface
   cannot run it (e.g. Claude Chat has no local shell or hooks), the row says so and names the
   server-side backstop (CI, branch protection).
3. **Parity is tested.** Where two or more surfaces share a shim point, a fixture proves they give
   the same result, extending `evaluate-surface-trajectories.py`.
4. **Git and CI are the universal floor.** Every local agent and every human passes through git.
   Every API or cloud agent passes through the remote. So git hooks plus CI are the enforcement
   layer that no surface can skip. Vendor hooks are accelerators on top.
5. **Device-inclusive too (Sean, 2026-09-22).** Personal projects continue on the Personal MBP
   (`Voyager-2.local`, home `/Users/snds`). Its layout is similar to the Work MBP's
   (`CS-K746DRWXY1`, home `/Users/sean.sands`), but its folder names differ. No mechanism may
   hardcode a device path:
   - repos are identified by **remote slug**;
   - the local checkout is resolved per device under the platform `Projects` root;
   - devices come from one declared table (hostname → label, home, projects root), which replaces
     the three `HOSTNAME_MAP` copies;
   - the per-machine brain pointer gets a tool-neutral home, with `~/.claude/workspace-brain-path`
     kept as a compatibility alias.

   A repo that isn't checked out on this device is reported as "not on this device", never as an
   error.

   **Identity is keyed by (surface family, device).** Every **Claude** surface is personal-only on every
   device: it uses `snds` and does no employer work. Every other surface follows the device: on the
   Work MBP it is work/Centric unless Sean expressly overrides for a task, and on the Personal MBP it
   is personal (`snds`). Surface shims only apply the resolved row ([[feedback-credential-scoping]]).

## Rationale — why, and what we rejected
Rejected: Claude-first with other surfaces as "later". The contract already says no tool is
privileged, and a Claude-only gate is how HEAD went red (Cursor commits skip the Claude-only
SessionEnd heal). Rejected: per-surface forks of the logic, because they drift, as three hand-copied
adapter lists already have.

## Consequences — what this commits us to
- Plans and components state their surface matrix. A component with no row for Claude Chat, Cursor
  or Codex is incomplete.
- Enforcement that exists only in a vendor hook is labelled an accelerator, never the gate.
- Adding a surface means adding a shim, a coverage row and a parity case. It never means forking.
