# SESSION-STATE — Workspace Brain

_Last updated: 2026-10-14 — install round done; two mechanization branches await Sean's merge_

---

## Current state (rewritten atomically — no stale fields)

### 🤝 Live handoff (the baton — any agent reads this FIRST, updates it on every handoff)

- **Working set**: this workspace checkout on `main`, plus the two locked worktrees above.
- **Last action (2026-10-14)**: /session-end after the bare-word trigger review (`0e02416`) — Claude Opus 5.5 · Claude Code · Work MacBook Pro.
- **Unattended runner — decided 2026-09-15: not building it.** Not a pending task. The safety gate
  (`check-unattended-runner-gate.py`) stays and is silent when idle. See [[decision-no-unattended-runner]].
- **Next action (Sean)**: (1) review and merge both branches (rebase `worktree-b-fixes-b1-b10` first; ^pc-51), then re-pin with `workspace-doctor.sh --install-pin` and one plain `workspace-doctor.sh` run; (2) one real Centric push from Claude, which closes ^pc-50 and ^pc-09; (3) decide DSDS 0.20 → 0.22 (^pc-54); (4) Enterprise machine layer (^pc-53).
- **Open decisions**: the next wave from the mechanization review (M1–M25) once these branches land; the W1-window review and the per-Mac blocking opt-ins (Zero-Vector OPT-IN).
- **Blocked on**: Sean's review and merge of the two branches.
- **In-flight / do-not-touch**: branches `worktree-b-fixes-b1-b10` and `claude/kind-diffie-41820e` and their locked worktrees — do not delete, force-push, merge or hand-copy their fixes onto `main` without Sean. The stale `.dirty`/`.touched` markers in `06-context/sessions/` and the blank-line run in `session-log.md` are fixed on the b-fixes branch; leave them until it merges. Do **not** `git add` the c8 lane config. **Do not delete anchored `^pc-NN` stubs** from `project-context.md`. Do not auto-commit or merge employer repos.
- **Agent thread**: `… → Claude Opus 5.5 / Claude Code / Work MBP (2026-09-24): ZV wave 0 closed, wave 1 started → Claude Opus 5.5 / Claude Code / Work MBP (2026-10-13): mechanization review, B-fixes and M25 branches → Claude Opus 5.5 / Claude Code / Work MacBook Pro (2026-10-14): doctor + routing fixes, /optimize audit + all fixes, trigger review, session end`.

### Environment
- **Context profile**: `personal-solo` for the workspace itself. The engine's `c8` lane declares `centric-engineering` and is **movement-only** — pointers, status, receipts; never substance.
- **Machine**: Work MacBook Pro (`CS-K746DRWXY1`) this session; Personal MBP remains the other primary.
- **OS context**: macOS (Darwin 27.0.0)
- **Workspace root**: resolve via nearest `AGENTS.md` (this checkout)
- **Project root**: `07-projects/19-workspace-brain`

### VCS state
- **Branch**: `main` plus this session-end commit
- **Uncommitted at baton write**: session fragment + this SESSION-STATE rewrite (folded into session-log at end)
- **Test state at last check (2026-09-02):** `vqa doctor` core ok; FLIP/DreamSim/OCR/gltf-validator/VGGT degraded honestly. `vqa calibrate` **48/48** (`vqa/1.1`). LCARS `S-SYS47-01` v4 `vqa prove` 16/16 measured. Doctor personal lane `ok` on this Cursor.

### Open work and paused threads
- **Currently in progress**: error-correction items 1–5 landed; watch for skip-after-close.
- **Paused (unchanged)**: Open Agent Engine ritual integration still wants an ordinary-session proof; dense Layer-2 retrieval stays deferred ([[decision-defer-dense-vault-retrieval]]).
- **The engine passed its first real verification (2026-09-15).** A label-filtered `list_issues` on the personal lane returned 30 issues; all **23** anchor→issue mappings in `open-engine/personal.md` resolve — **zero orphaned pointers**. The other 7 are engine infra (`SEA-5`/`6`/`7`/`8`) plus three created after the migration. Remaining untested: whether `/session-end` files residue pointer-shaped rather than pasting prose.
- **The migration is DONE — this entry was stale (corrected 2026-09-15).** It happened 2026-07-30 (43 anchored items, 38 with issues across both lanes; personal lane 23, c8 15 machine-local) and the substance graduated to `project-context-detail.md` 2026-08-07. `project-context.md` is now **93 lines / 12.4 KB**, already pointer-shaped, and costs **560 tokens** at session start (head-30) — not the ~61 KB this entry implied. The five unmigrated items are refusals on purpose, not backlog: three are `c8` with no valid pointer, two are lane-ambiguous, and guessing a lane on a movement-only boundary is the one thing the skill forbids. The 21.6k session-start footprint was fixed separately by C2 (`artifact-find.py`), not by this.
- **Remaining `PENDING` fields**: none. Both lane configs fully provisioned.
- **Pending questions**: none.
- **Blocked on**: nothing for the error-correction P-items. Open Engine itself is unblocked.
- **Sean-side follow-ups** (not blocking): disable Linear auto-close-stale-issues on both workspaces; optionally build the lane-scoped scheduled runner.
- **Queued from the site review** (separate from Open Engine): trim the ~21.6k-token session-start footprint (`project-context.md` line 19 alone is ~1,490 tokens inside a head-60 read). Negative fixtures and `/optimize` seven-surface loop landed 2026-08-26.
- **What's needed to resume**: error-correction → read `notes/error-correction-research_2026-08-26.md` + the knowledge entry. Engine → `03-skills/open-agent-engine/SKILL.md` Preflight, then `06-context/open-engine/README.md`. Run `python3 00-bootstrap/doctor/linear-lanes.py` for live lane state.

---

## Session history (append-only)

_Older entries are in [history/README.md](history/README.md), the long-term tier, by month; the app's Projects timeline joins them with this file._

### 2026-10-14 — install round done; B-fixes + M25 branches await merge (baton rewrite)

**Agent**: Claude Opus 5.5 · Claude Code · Work MacBook Pro

The Live handoff had been stale since 2026-09-24. Its contents, moved here so nothing is lost:

- **Employer thread (2026-09-18 → 2026-09-21; employer detail stays in employer surfaces):** the focus was an employer design-system PR (CI green) waiting on Sean's review, with that employer checkout as the working set; a companion employer host PR got a peer-dependency correction on 2026-09-21. Standing cautions from it: do not agent-merge, do not bump a host pin, do not re-add widget libraries to a host to silence an unmet peer, do not commit an untracked canvases folder in the employer checkout. Two other employer PRs were last noted 2026-09-18 as human-merge. The 2026-09-21 entries below carry the detail.
- **Mechanization review (2026-10-13), as written then:** "Sean picks the first wave from the mechanization review — `reports/mechanization-review_v1.0_2026-10-13.md` (M1–M25, bugs B1–B10; suggested start: B1–B10, then M25 write-cost lane). Nothing applied yet." By 2026-10-14 the two branches in the Live handoff held the applied fixes (B1–B11 and M25), unmerged.
- **Other open decisions then:** a theme reset stays a later product-CSS PR; restyle/arbitrary/inline shadcn rules stay off until a later wave.
- **ZV blockers as of 2026-09-23:** nothing blocked the agent steps. Sean decided the last three items on 2026-09-23: the loaner is retired from `devices.json` (D9), probe records are public evidence under F-14 exception 1, and no per-use approval on the employer credential (H17-R10). CI was green on `e360aa3`.
- **Previous agent thread:** `… → Cursor Grok 4.7 / Cursor / Work MBP (2026-09-21): employer PR CI green → Cursor Grok 4.7 / Cursor / Work MBP (2026-09-21): employer host PR peer replies → Cursor Grok 4.7 / Cursor / Work MBP (2026-09-21): employer host PR drops widget deps → Claude Opus 5.5 / Claude Code / Work MBP (2026-09-22): Zero-Vector research + harness plan + X1 heal → Claude Opus 5.5 / Claude Code / Work MBP (2026-09-23): wave 0 A+B, fix round, harness environment notes → Claude Opus 5.5 / Claude Code / Work MBP (2026-09-23): D5, decisions recorded, worktrees removed → Claude Opus 5.5 / Claude Code / Work MBP (2026-09-23): F-14 and D6 applied, uncommitted`.
- **Zero-Vector thread as it stood (verbatim):**

- **Parallel thread (2026-09-22): Zero-Vector harness plan v1.1, WAVE 0 APPROVED (LLM-inclusive caveat).**
  - Plan: `notes/zero-vector-harness-plan_2026-09-22.md` (v1.1 summary). Full v1.1 detail and surface research are held locally at `.claude/state/held/` (Work MBP; not committed while the vault is public, ^pc-47).
  - Decisions are recorded in [[decision-llm-inclusive-harness]], [[decision-project-intent-in-repo]] and [[feedback-credential-scoping]].
  - **Wave 0 status (2026-09-23): published.** Waves A and B reached `main` at `ec77eda`. Sean then fast-forwarded `main` to the verified fix round (head `7fefad5`) and pushed it. That round holds 23 fixes, including the walls F-01/F-02 blockers, plus the harness environment notes.
  - **Verification at `bd8274d`:** harness 35/36 gates with the real git; the 36th (profile_resolve) is 340/340 outside the sandbox. Under Claude Code's Bash sandbox, 3 gates go red for environmental reasons (xcrun cache, `ps` denied); the harness now prints an environment note naming them.
  - **Done after publish (2026-09-23):** D5 landed in `6d30676` (exact, case-insensitive domain match; 351/351 resolver checks outside the sandbox; three reviewers found no defects). Decisions recorded here, in ^pc-45, the plan note, `surfaces.json` and the held spec. The ten merged intent worktrees were removed; their branches stay. The T10/T11 findings register is saved in held (`wave0-verification/`).
  - **F-14 and D6 landed (2026-09-23).** Gap detail follows repo visibility ([[decision-public-residual-detail]]). The public identity row states ten gaps at class level (H17-R1 to H17-R10) plus WALL-C1; the recipes and machine posture are in held (`h17-residual-register_2026-09-23.md`, `machine-posture_2026-09-23.md`). Four review rounds found new bypass shapes each time, so H17-R10 is an umbrella: the local layers are seatbelts against ordinary pushes, and the barriers are server-side protection and review. The classifier now labels single overlay-entry overrides, the `+=` form, `--no-verify` abbreviations and include/alias keys; the doctor's check mode audits URL rewrites (report-only). CI fix for the two red gates is in `6c5a909`.
  - **Wave 0: all gates closed (2026-09-24).** G5c passed: vetted prune apply from Claude Code, 3 action receipts ok, credential classes none (local) and https:github.com+gh:default-account (remote). Personal MBP: no Claude overlay until wave 1 (D4). The installer refuses on git without config hooks and on Claude settings env seen in another host's shell. Watch: re-probe Codex on the Work MBP after Codex updates.
  - **Rollout checklist (live until 2026-10-14; superseded by the vault copy `notes/zero-vector-rollout-checklist.md` — do not update the artifact):** https://claude.ai/artifact/MsCW4SkVxNvFNncAH6v4jz — every Zero-Vector step by wave with status, owner, device and evidence. Steps live in the artifact's db (`steps`, `waves`, `meta/status`); any agent that completes a step updates its doc with ArtifactData (status, ref, done_on) and bumps `meta/status.updated`.
  - **Wave 1 (started 2026-09-24):** spec held at `.claude/state/held/INTENT-wave1-2026-09.md`. Done: W1-a ^pc-47 email scrub (`a32d08a`); W1-b seven wave 0 follow-ups plus a review fix (`68b9835`; **Work MBP re-pin needed**); W1-c H6 measurement. **H6 (W1-1) done at `94b4b34`**: AGENTS.md cuts, beacons from beacons.json, Windsurf rule, route digest, harness floors. H6 installs done on both Macs. **H18 (git lanes), H15 (wall guard) and H7 (routing) merged** at `461c933` (+ P33 policy rule); harness 38/38. Next: Sean's combined install round on both Macs (checklist W1-2h), then live probes (W1-3h). Everything else waits on Sean's decisions D-W1-1..6 (listed in the spec and the plan note).
  - **Human steps later (words only until ready):** pin install, per-surface probes (Claude Code, Cursor, Codex, VS Code), Personal MBP identity checks, v5 overlay install, one vetted prune with the sandbox off. The Cursor card on this Mac needs the Cursor shim reinstalled to get `--family cursor`; the G3b `--install-shims` run does that (L-12).
  - **Sean's decisions (2026-09-23):** walls F-11: the heal path gets pinned in wave 1, and until then it is a declared residual. Tests F-07: the floor keeps blocking the vetted employer prune when `ps` is denied; that one command runs with the sandbox off. D5: the employer email domain is `centricsoftware.com`; Sean will say if the employer changes. D7: the three H25 items move to wave 1 with H23, H4 and H15. Walls F-14: gap detail follows the repo's visibility; in this public vault a gap is written at class level with a stable ID, and the recipe and machine posture stay held ([[decision-public-residual-detail]]). D6: approved; `00-context-profiles.md` says "cited by the agent". The work email address in three tracked files is handled with wave 1 (H25 scrub, ^pc-47).
  - **Claude may work in employer repos (2026-10-06)** under `centric-engineering` on the Work MBP, like Cursor and Codex ([[decision-claude-employer-surface]]). Each machine needs `workspace-doctor.sh --install-claude-overlay` re-run by a human before the old transport block is gone. _Until then the rule was: Claude sessions must not open employer repos._

### 2026-09-21 — cui #413 drop widget deps

**Focus this session**: Take Alex's encapsulation note on centric-ui #413 and correct the host.
**Machine**: Work MacBook Pro (`CS-K746DRWXY1`) · Cursor Grok 4.7 · Cursor
**Stopped because**: correction pushed and replied; session still open.

**Accomplishments**:
- Removed `input-otp` and `react-day-picker` in `022c468`; replied on both threads
- Encoded the boundary in the workspace (foundations, #14, #18, ds-advisor, fe-component-architecture, knowledge)

**Next**: Sean reviews cds #50. CDS-side peer hide is not started. Do not bump `cds.pin`.

### 2026-09-21 — cui #413 peer replies

**Focus this session**: Answer Alex on centric-ui #413 about `input-otp` and `react-day-picker`.
**Machine**: Work MacBook Pro (`CS-K746DRWXY1`) · Cursor Grok 4.7 · Cursor
**Stopped because**: Sean asked to end session.

**Accomplishments**:
- Replies posted on [#413](https://github.com/cpes-software/centric-ui/pull/413) discussion threads

**Next**: Sean reviews cds #50. Do not agent-merge.

### 2026-09-21 — cds #50 CodeQL green

**Focus this session**: Clear the remaining CodeQL failure on cds #50.
**Machine**: Work MacBook Pro (`CS-K746DRWXY1`) · Cursor Grok 4.7 · Cursor
**Stopped because**: Sean asked to end session.

**Accomplishments**:
- Linear CSS scans pushed as `a346322` on `feat/instance-0-thin-child-lockstep`
- CodeQL and CI green on [#50](https://github.com/cpes-software/cds/pull/50)

**Next**: Sean reviews #50. Do not agent-merge.

### 2026-09-18 — CDS ShadCN federalization instance 0 (local)

**Focus this session**: Federalize CDS on bumpable ShadCN; keep local; resume in CDS-rooted chat.
**Machine**: Work MacBook Pro (`CS-K746DRWXY1`) · Cursor Grok 4.6 · Cursor
**Stopped because**: Sean asked to end session.

**Accomplishments**:
- Local wrap merge on cds `feat/shadcn-federalization` @ `5b21ec9` (10 ahead of origin)
- Stock L0 + extras + ShadCN stories: Button, Input, Badge
- Remaining modules thin-wrapped (CDS-as-L0, not stock yet)
- Resumption prompt for a CDS-folder chat

**Next**: Open Cursor on `/Users/sean.sands/Projects/cpes-software/cds`. Restore stock per remaining module. No push until review.

