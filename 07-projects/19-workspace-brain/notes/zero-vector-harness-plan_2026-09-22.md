---
title: Zero-Vector-informed additive harness plan
date: 2026-09-22
status: proposed
related: [[zero-vector-design-methodology]]
---

# Zero-Vector-informed additive harness plan (2026-09-22)

Standing home: this project.
- Synthesis of the methodology: `08-knowledge/cross-domain/zero-vector-design-methodology.md`.
- Implementation-grade detail for every component (read by section, never whole):
  `reports/zero-vector-harness-detail_v1.0_2026-09-22.md`.

## Bottom line

- **Zero-Vector's value is its patterns, not its tools.** Keep these five: declared project
  intent, a lint that checks the spec against disk, findings that stay open until closed with
  evidence, self-contained work packets, and owned write-sets. ZV's tooling runs all of these as
  prompts. Its own site repo shows the result: good remediation was produced and mostly carried
  out, but it was never closed, and stale maps still point agents the wrong way.
- **This workspace repeats that failure at two boundaries.**
  - *Project level:* projects don't declare intent, and audits never close.
  - *Surface boundaries:* Cursor commits skip the heal that only Claude runs. HEAD was red on
    registry drift until healed in `6cac460`. Also, `llms.txt`, the always-applied `brain.mdc`,
    and six Cursor agent files all teach reads that the contract bans.
- **The plan is 15 components in 4 waves**, and every one extends a home that already exists. It
  adds nothing to always-loaded context. Everything runs report-only before anything blocks, and
  the employer wall becomes mechanical for agent git actions.

## What changes for the long-term build process

| Today | After |
|---|---|
| A project's problem, audience, knowns and unknowns live in ad hoc prose (or nowhere) | A bounded `## Project intent` block in the README (vault projects) or a root `PROJECT.md` (external personal repos). It holds knowns and unknowns with #04 labels and decision rules written before any evidence, plus an explicit out-of-scope list and a Later list |
| Specs are trusted as written; approval is any string starting with "approved" | `intent-run lint` checks spec vs. disk and scales severity by `lifecycle:`. Approval is TTY-only and pinned to a content hash. Verify leaves append-only records in mission-fit's PASS/FAIL/UNKNOWN terms |
| Audits end as reports, and their status contradicts the memory decisions | Audits become remediation specs: a findings register (F-IDs, OPEN/RESOLVED/DEFERRED, `closed_by`), self-contained packets, a preserve list with expiry, and a mission-fit verdict. Snapshot reports are never edited |
| Parallel agents are separated only by worktrees | Tasks declare `writes`/`forbids` globs. `gate` rejects overlapping writers in the same wave, and `scope` checks each diff against its declared globs |
| Validators run only when someone remembers, and SessionEnd pushes unchecked | Gates run at boundaries every surface passes through (SessionEnd plus git hooks you install), and the diff decides which ones run. Failures are split into charged (this diff caused it) and ambient (it was already there). Reporting only until the data justifies blocking |
| Machine entry points drift from the contract | One `ENTRY_POINTS` list. A parity check fails any read order that names a banned-ingest file |
| The employer wall is text injected into context | One declared resolver on two axes (owner and credential), plus a user-global guard on agent `git`/`gh` actions |

## Waves

The **first breaker** is wiring any gate before wave 0 greens HEAD and makes the heal safe under
scoped commits. If that order is inverted, every gate fires on inherited debt, the telemetry that
must justify blocking is poisoned, and bypassing gates becomes a habit.

### Wave 0: a green baseline and proven tools (H1, H3, H2)

- **H1: regeneration baseline.** Make `nightly.py` the single regeneration sequencer, with
  per-step timeouts, a `--budget` deadline, and the fixpoint order build-registry → build-related
  → build-registry → build-trigger-routes. The SessionEnd hook calls it inside a 52 s deadline
  with a 12 s push reserve. The heal is skipped when a dirty `SKILL.md` belongs to another
  session, or to Cursor, which writes no touch-list. Its one-off census report covers
  git-tracked files only.
  - *Detector:* `nightly.py --self-test`, plus `TestScopedCommit` extensions.
  - *HEAD heal already done:* `6cac460`.
- **H3: harden intent-run before extending it.** Quote-aware frontmatter parsing, so
  `approved via PR #12` survives. Escaped table pipes. Measures run with `shell=False`, and an
  allowlist applies in CI and hooks, so a `; <cmd>` chain cannot run. A no-git-write invariant, a
  `--self-test`, and CI path filters.
- **H2: declared profile resolver.** `09-tools/profile_resolve.py` reads the declared table
  `delivery-playbooks/context-remotes.json` and returns two axes: owner profile and credential
  scope. It classifies against the declared table, and the code holds no employer org names.
  Contradictions come back as `conflict`, naming both sides. `beacon-enroll.sh` and the doctor
  call it, keeping their case arms only as a fallback when python3 is absent.
  - *Needs your sign-off:* the playbook step-3 edit.

### Wave 1: honest intent and honest entry points (H6, H15, H4, H5, H7)

- **H6: entry-point parity.**
  - One `ENTRY_POINTS` list in `workspace-harness.py`; the other two adapter lists derive from it.
  - A read-order check covering llms.txt, `brain.mdc`, CURSOR.md, CLAUDE.md:81, `.cursor/agents/*`
    and the ontology row. It lands in the same commit as the fixes for all 13+ current defects.
  - Prices `cursor_floor`, `hook_injection` and `trigger-routes.json`. Net token effect is
    negative.
- **H15: employer-wall guard.** A user-global `PreToolUse(Bash)` hook runs only on commands
  containing `git ` or `gh `, and calls `profile_resolve.py guard`. It runs 14 days in ask mode,
  then denies default-branch commits, pushes and self-merges in employer repos. Branch → PR flows
  stay allowed.
  - *Needs your approval* for the user-global fragment.
- **H4: project-intent block.** The `## Project intent` block has three sections:
  1. Problem & audience.
  2. Knowns & unknowns: claim | #04 label | tier | evidence | decision rule.
  3. Out of scope & Later (≤ 15 items).

  Details:
  - Capped at 40 lines; any field may be a pointer or `n/a (reason)`.
  - README frontmatter gains `lifecycle: discover|define|build|operate` (deliberately not
    "stage", which #17 already uses).
  - `intent-run init --frame` writes the block, and `/new-project` calls it.
  - Employer or unknown profiles get only an engineer-voiced `--neutral` variant, checked by a
    new opt-in `check-secrets --class workspace-leak`.
- **H5: intent-run lint / approve / next / verify --record.**
  - Lint compares spec vs. disk ("update one of them") and severity scales with `lifecycle`.
    Profiles must agree per repo.
  - Approval is TTY-only and hash-pinned: `gate` blocks silent edits to outcome, northstar or
    decision rules made after approval.
  - Verify records land in tracked `*.verify.jsonl` (personal-solo) or under the git dir
    (anything else).
  - In the same commit: `lint --all` joins CI, and this project's done-but-open
    `docs/INTENT.md` is closed.
- **H7: routes through the one matcher.** Multiword keys for knowns/unknowns, project brief,
  definition of done, "onboard this repo", and codebase/repo audit (→ eng + #14; still also #06).
  Remediation and closure keys land with H8. Target checks resolve anchors and subcommands, so a
  route can't land before its target. The dead dispatcher `TRIGGER_WORDS` and `KNOWLEDGE_HINTS`
  dicts are removed.

### Wave 2: close the loops (H8, H9, H10, H11). Report-only.

- **H8: remediation spec.** `kind: remediation` has these parts:
  - a read-only recon card (ported from `wsx adopt`, carries `source_sha`, stdout only for
    employer or unknown remotes);
  - `## Findings`, a findings register (not a "ledger"; that word is taken): F-IDs,
    Critical/High/Medium/Low, OPEN/RESOLVED/DEFERRED, `closed_by`, `revisit`;
  - `## Preserve`: glob | why | until;
  - `### T<n>` packets with non-goals, verification, rollback via worktree, bail points and
    previous attempts.

  How it behaves:
  - `verdict` returns Fit / Fit with gaps / Unfit / Blocked.
  - A loop-breaker refuses to re-dispatch after 3 FAIL records, and never reverts.
  - Dogfood: this project's A1–A10, R1–R3, R1–R16 and load-miss 1–15 are imported. A8 becomes
    RESOLVED, and the reports get registered in `artifact-registry`.
- **H9: write-set scope.** Task-graph `writes`/`forbids` globs, a committed contract before any
  fan-out, and a read-only verifier. `scope TASK` fails any file outside the task's globs, any
  forbidden file, lockfiles and manifests nobody owns, and preserve paths. The restore point is
  the worktree: no checkpoint commits, no stash, no reset.
- **H10: diff-computed gates.** `close-out-dispatch --from-diff` maps changed paths to
  QUALITY_CHAIN steps. A failure is charged if this diff caused it, including links broken by a
  delete or rename. `last-gate.json` keeps a bounded ring of recent runs. `--telemetry` counts
  catches and false positives for harness-map's Probation step; you decide every disposition.
  `ws-audit` gains one `COMPLY` line: injected close-out vs. whether it actually ran, and injected
  `SKILL.md` paths vs. which were actually Read. This is the Labrador-style context receipt.
- **H11: closure triggers.** The SessionEnd gate runs through `nightly --phases verify`, and the
  commit subject gets a `[gate: …]` suffix. `post-commit` and `pre-push` git hooks are installed
  only by your explicit `workspace-doctor.sh --install-git-hooks`, with a matching uninstall. Kill
  switch: `WS_PUSH_GATE=off`. A bypass requires a reason. The card gains at most one line:
  specs that need closure, and the last red gate.

### Wave 3: opt-in blocking plus breadth where it's needed (H12, H13, H14)

- **Blocking** is a per-machine opt-in (`--install-git-hooks --blocking`) for charged regressions
  only. It requires at most 1 false positive in 20 runs first.
- **H12: research records and project ADRs** (only when a tracked personal project keeps
  records). `vault-health --research` checks them over tracked files:
  - prefixed IDs and typed relations;
  - #04 labels only;
  - decision rules registered before the evidence;
  - personas only with evidence edges;
  - `^P\d+$` participant IDs;
  - an opt-in `check-secrets --class pii`.

  Project ADRs are Nygard-shaped, and supersession is written in both ADRs' bodies.
- **H13: `structure-conform.py`** (demand-triggered). It checks only the layers and import rules
  a project declared, in a fenced JSON block, using stdlib parsing. It becomes the eng hub's L3
  detector. ShadeGraph is the likely first consumer.
- **H14: rule-of-three instance log.** `06-context/rule-of-three.jsonl` plus a growth check: new
  hubs need 3 resolvable instances or a command-surface detector row, and new frameworks need 3
  consumers. self-improve asks "what would have helped at the start?"

## Not adopted (key refusals)

- **The ideology.** "One auteur, zero handoff" does not override the employer wall, and design
  systems are not "translation overhead". Handoffs also carry distributed scepticism, and
  independent measurement stays primary.
- **Auto-committing audits, checkpoint commits, forced reverts, and reflect-and-retry.** These
  break the walls and the Do-not-build list.
- **A standing named crew, per-role instruction files, a separate ledger tool, a separate
  project-drift tool, per-skill reads/writes frontmatter on all 301 skills, and a vault-wide
  artifact-lifecycle registry.** They would be parallel stores or would fail rule-of-three. The
  useful parts are folded in: globs on task rows, one parser, `source_sha` on recon.
- **A learning ladder (skills-as-levels, comprehension probes, coach mode).** The probes are
  self-report, not independent measurement. Only the session-end gap question survives.
- **A handoff-count KPI** (it encodes the ideology), **instruction-file rationale lint**
  (noisy), **a general fact registry** (drifts toward an LLM judge), and **a one-page operating
  model** (it duplicates AGENTS/CRITICAL_FACTS and eats contract headroom).
- **Any ZV text, schema or template**, because there is no upstream LICENSE. A one-shot n-gram
  overlap check runs before any template lands.

## Decisions needed from you (these block wave 0–1)

1. **Wave 0 go-ahead.** Approve H1 (the dispatcher and `nightly.py` changes) and H3. Both are
   harness mutations, so they need your approval under mission-fit.
2. **Playbook sign-off (H2).** Step 3 reads remotes via the declared `context-remotes.json` on
   two axes, and adds the `centricsoftware` Bitbucket org. Also fix row 48 ("Git identity:
   personal snds"). It contradicts `feedback-credential-scoping.md`, which requires the Centric
   identity for workspace commits on this laptop. The code is right; the doc is stale.
3. **Project-intent home (H4).** A README block for vault projects and `PROJECT.md` for external
   personal repos. Are `lifecycle` values discover/define/build/operate right?
4. **H15 wall guard.** Add it to the user-global fragment? It starts in ask mode for 14 days,
   then denies.
5. **Approval authenticity.** Is a TTY-only `approve` plus an intent hash enough, or do you want
   out-of-band approval (a PR review or signed tag) before implementors start?
6. **Beacon behaviour.** snds-owned repos reached through the `github-work` alias are currently
   refused, because the credential scope is work. Keep that, or allow them when the owner is
   personal?
7. **IP boundary.** The playbook says "no employer material, ever", but the vault deliberately
   tracks Centric context. Declare that as a sanctioned exception?

Later decisions: the `hook_injection` budget, blocking opt-in per machine, research-L3 naming,
the mapping between the DDR vocabulary and #04, grandfathering the rule-of-three baseline, and
the state of the 16-CDS plan. All are listed in the detail report.

## Defects found and verified along the way

All 18 candidates were confirmed by an independent read, plus one new one (X1). The
load-bearing claims were re-run by hand.

| ID | Defect | Sev | Status |
|---|---|---|---|
| X1 | Registry drift at HEAD; routing stamp stale | med | **Healed `6cac460`** |
| D7 | `llms.txt` "Start here" links `skills.registry.json` (~62k tok) and `trigger-routes.md` | high | H6 |
| D1–D2 | SessionEnd heal runs build-registry only, and no timeout; fixpoint order undocumented | med | H1 |
| D3 | Dead forked matcher code in `dispatcher.py`; one-matcher guard scans only the first 3000 chars | med | H7 |
| D4–D5 | CI path filters miss hooks/bootstrap/intent-run; `build-trigger-routes --check` not in CI | med | H3/H6/H10 |
| D6 | `intent-run` approval is self-attestable | med | H3/H5 |
| D8 | SessionStart timeout 30 s vs ~98 s of allowed serial subprocess time | med | H1 (extend to SessionStart) |
| D9 | Card warns on a missing routing stamp, not a stale one | low | small fix |
| D10 | `/new-project` and templates say to edit dispatcher `TRIGGER_WORDS` | med | H4/H6 |
| D11 | `beacon-enroll` refuses snds repos via `github-work` (documented fail-safe) | low | decision 6 |
| D12 | 6 of 12 SESSION-STATE files lack a Context profile line (4 are employer projects) | med | small fix + H5 |
| D13 | `github-guardrails` keeps dismissals in agent-local memory | low | self-improve |
| D14 | `HOSTNAME_MAP` duplicated ×3 with divergent labels; retired Windows host | low | self-improve |
| D15–D16 | `skill-placement` skips #13; hub-prerequisite rule not enforced | med | self-improve |
| D17 | `/optimize` exists only under `.claude/skills` (not portable) | med | separate task |
| D18 | "Seventeen frameworks" and a 01–05-only README template | low | self-improve |
| X2 | The UserPromptSubmit router also fires on background task-notification turns. It injected about 20 unrelated routes twice this session (e.g. `figma`, `centric`, `exposure`). Separately, "zero **vector**" false-routes to `sci-linear-algebra` | med | H7 (skip non-user turns; forbid case) |

## Do not build (inherited plus new)

The same list as `error-correction-research_2026-08-26.md`: no parallel agent framework or second
substance store, no default reflect-and-retry, no LLM-as-judge KPIs, no new framework or skill
without rule-of-three evidence, no unattended runners. This plan adds four items:
- no hooks in employer repos;
- no tracked blocking flag;
- no doctor-set `core.hooksPath`;
- no gate that charges ambient debt.

## Method

- **Source read, 2026-09-22.** One browser tab, read serially with 4–8 s pauses, about 20 page
  loads across zerovector.design, open.zerovector.design, herelabrador.ai and Substack.
  `robots.txt` allows everything and points LLMs to `llms.txt`. There was no CAPTCHA, bot wall or
  AI block. The three GitHub repos were read without authentication, because `gh` is logged into
  the work account, and none of their scripts were run.
- **First multi-agent workflow (8 agents).** Deep-read the local capture and mapped this
  workspace's runtime, method and project layers.
- **Second multi-agent workflow (12 agents).**
  - Designed three competing plans.
  - Three lens judges ranked them: minimal 24, closure 21, builder 19.
  - A synthesis merged the best, then three adversarial refuters attacked it.
  - A revision applied 58 objections, partially applied 2 and rejected 2.
  - An independent verifier checked the defects.
- **This session's outputs.**
  - The knowledge note.
  - This plan, and the detail report.
  - The X1 heal. No harness code was changed.
