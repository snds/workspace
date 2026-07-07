---
type: decision
description: Bootstrap v2 (2026-07-06) — the workspace handshake is guaranteed by deterministic harness layers, not model discretion; ritual token is frozen ABI.
created: 2026-07-06
confidence: high
---

The workspace bootstrap is enforced by **harness-executed layers**, never by hoping a model
notices a skill: **L1** user-scope `SessionStart` hook (any cwd; fires on startup/resume/compact,
emits root + branch@sha + standing rules + ritual instruction) · **L2** `UserPromptSubmit`
late-repair + every-15-prompts re-assert (compaction survival) · **L3** the WORKSPACE-BEACON in
`~/.claude/CLAUDE.md` (injected even if hooks die) · **L4** the same script via the snds plugin
(workspace-copy path, marker-deduped) · a `SessionEnd` **audit** that greps assistant-role
transcript messages only (OK/MISS/SKIP; injected text cannot fake OK) · a **launchd doctor**
(outside `~/.claude`, every 4h + login) that reinstalls drift and canary-detects "sessions ran
but audit silent." Source of truth: `00-bootstrap/dist/` + `00-bootstrap/doctor/`; fresh machine
= `00-bootstrap/bootstrap.sh` one-liner.

**Why:** the model-discretionary skill trigger reliably failed on compaction-resume and non-workspace
cwds (observed 2026-07-06: Figma real-components rule violated until Sean intervened — the exact
class of miss the workspace exists to prevent).

**Alternatives rejected:** skill-description triggers (model-discretionary — the failure mode
itself); cwd-scoped project hooks alone (never fire outside the checkout); `additionalDirectories`
grants (would weaken the employer-repo firewall); a single hook layer (single point of failure —
each layer's miss is caught by a layer in a different failure domain).

**Invariants:** the ritual line `[workspace: LOADED · <branch>@<sha> · <date> · via:<layer>]`
(+ `RULES-ONLY`, `UNREACHABLE`) is **frozen ABI** — never reword; the beacon text lives once in
`00-bootstrap/dist/BEACON.md` and is hash-nagged onto chat surfaces via `--ack-chat`; one-shot/
structured-output calls are exempt from the ritual (audit logs SKIP, not MISS).

Full red-teamed plan: `05-artifacts/active/workspace-bootstrap-durability-plan_v2.0_2026-07-06.md`
(local artifact). Related: [[decision-externalize-everything-to-workspace]] ·
[[decision-portable-workspace-refactor]].
