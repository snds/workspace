---
title: "Zero-Vector-informed harness — component specifications"
version: "1.0"
date: 2026-09-22
status: proposed
companion: "07-projects/19-workspace-brain/notes/zero-vector-harness-plan_2026-09-22.md"
sources:
  - "08-knowledge/cross-domain/zero-vector-design-methodology.md"
  - "Multi-agent judge panel + adversarial verification, 2026-09-22 (Claude Opus 5.5 / Claude Code / Work MBP)"
---

# Zero-Vector-informed harness — component specifications (v1.0)

Read the plan note first: [zero-vector-harness-plan](../notes/zero-vector-harness-plan_2026-09-22.md). This
report is the implementation-grade detail behind it: each component with its home, mechanics, detector and
fixtures, token impact, and behaviour per context profile. Snapshot: never edited in place. A revision
ships as v1.1.

**Provenance.** Three independent plans (minimal-additive, closure-first, builder-lifecycle) were scored by
three lens judges (contract, leverage, feasibility). The top plan (minimal-additive, 24/30) was synthesized
with grafts from the others, then attacked by three refuters (duplication/homes, contract/walls, facts). The
reviser applied 58 objections, partially applied 2 and rejected 2 (both logged below). Line numbers cite
HEAD `22934df`–`6cac460` and will drift. Re-verify before implementing. `zv-scratch/` refers to the
session-local capture of the Zero-Vector corpus. It was deliberately **not** vendored, because the upstream
repos have no LICENSE.

## Evidence-grade legend

Component text reuses the existing vocabulary and invents no new one. Check status is PASS / FAIL / UNKNOWN
(`03-skills/mission-fit/SKILL.md`). Evidence grades are VERIFIED (a named detector ran), USER_REPORTED (a
human signed it), INFERRED (derived, not measured) and NOT_EXPOSED (not measurable here), per the evidence-grade
legend enforced by `09-tools/validate-evidence-grades.py`. Every component names the detector that can fail it.

## Components

### H1 — Wave-0 baseline: heal HEAD, make nightly.py the single regeneration sequencer (timeouts, budget, fixpoint order), make the SessionEnd heal safe under scoped commits, census inherited debt

- **Wave / effort / layer / enforcement:** 0 · M · hook · deterministic
- **Home (extend):** 09-tools/nightly.py + .claude/hooks/dispatcher.py (handle_session_end, git helper line 169) + order lines in AGENTS.md:461, nightly.py docstring, workspace-harness.py QUALITY_CHAIN comment + 07-projects/19-workspace-brain/reports/ (census)
- **Depends on:** —
- **ZV sources:** zv-live-07 (done but not closed), 22 (never gate on a red baseline), BRIEF anti-pattern: manual-only closure, B-C0

**Why this home.** nightly.py already owns fold → rebuild → verify → commit-only-if-green, so the dispatcher should call it rather than keep a second generator list. reports/ is the tracked landing zone for workspace self-audits (reports/README.md).

**Problem.**

HEAD is red on registry drift only.
- HEAD 22934df: `python3 09-tools/build-registry.py --check` returns rc=1 (re-run 2026-09-22).
- The stale hashes are ds-advisor, eng-foundations, fe-component-architecture and plan-ahead, touched by the Cursor co-authored commits 41737cd and 8fcb70e.
- `build-related.py --check` returns rc=0.
- The validate-integrity red is not on HEAD. It comes from the uncommitted in-flight `[[zero-vector-design-methodology]]` line in 08-knowledge/_INDEX.md (`git diff` shows +1).

The regeneration sequence already exists in 09-tools/nightly.py (PHASES line 55; SAFE_COMMIT_PATHS line 64; refuses to commit on a red tree, line 141). But run_step (line 74) has no timeout, and the dispatcher re-lists only build-registry, with no timeout, in handle_session_end (.claude/hooks/dispatcher.py:1661-1673).

The order is taught inconsistently. build-related.py's docstring says 'Reads 03-skills/skills.registry.json (run build-registry.py first)'. AGENTS.md:461, the nightly docstring and the workspace-harness QUALITY_CHAIN comment (lines 68-70) teach related → registry. Inference: when a frontmatter edge changes, only registry → related → registry converges.

The scoped commit stages only this session's touched paths plus _SCOPE_ALWAYS (dispatcher.py:1527). So generator rewrites in untouched SKILL.md files would ship a registry that hashes content never staged, or the heal would write into another session's claimed file.

**Mechanics.**

(1) nightly.py changes:
- run_step gets a per-step timeout (default 15 s) and a `--budget S` deadline.
- `--phases fold,rebuild,verify` selects phases.
- rebuild becomes build-registry → build-related → build-registry → build-trigger-routes. The second registry pass is skipped when build-related changed nothing.
- verify gains `--from-diff (--staged | --range R)`, which runs `close-out-dispatch.py --from-diff … --json` (H10) as its one step. Without that flag, verify stays workspace-harness.
- A timeout reports SKIPPED, never green. commit_mechanical still refuses a red tree.

(2) Same commit: the nightly docstring and PHASES, the QUALITY_CHAIN comment and the AGENTS.md write-quality sentence all state the fixpoint order, at about the same length.

(3) Dispatcher changes:
- handle_session_end replaces its inline build-registry call with `python3 09-tools/nightly.py --phases rebuild --budget <remaining> --json`.
- It runs under a deadline scheduler: t0+52 s, with 12 s always reserved for one push. git() gains an optional timeout, used for push and pull.
- Heal safety pre-check, before any generator runs: if any dirty 03-skills/** path is outside this session's touch-list, or appears in _other_session_claims() (dispatcher.py:1531), the heal is skipped and H11 marks the gate red. That covers Cursor edits, which write no touch-list.
- Otherwise, snapshot `git status --porcelain -z` before and after the run and stage exactly the paths the generators touched.
- If nightly.py is missing or its output is unparseable, fall back to today's build-registry-only heal (fail-open).

(4) The wave-0 heal is one deliberate personal-solo commit: `nightly.py --phases rebuild`, then `git commit -- <generator-touched paths>`. It must not include the in-flight ZV note, its _INDEX.md line, or 08-knowledge/design/ds-parent-owns-shared-defects.md, which belongs to another session. Those, plus the missing link target, belong to the ZV research session's own close-out.

(5) Census: reports/closure-census_v1.0_<date>.md, counts only, computed from `git ls-files` so every machine and CI agree:
- 3 status contradictions;
- at least 13 entry-point parity defects;
- 2 lifecycle probes with no route, 3 with only a generic one;
- 1 spec that is done but not closed;
- 10 tracked versioned reports, 4 of them indexed.
Each later check sets its ratchet ceiling from its own --report in the commit that lands it. Ceilings only go down (precedent: 09-tools/shadcn-lint/baseline.json).

**Detector and fixtures.**

New `nightly.py --self-test` on a fake tools directory checks: fixpoint order; the second registry pass skipped when related changed nothing; a timeout reported as SKIPPED; the budget deadline respected; no commit on red. It is added to QUALITY_CHAIN and the validator-fixtures path filter.

TestScopedCommit (09-tools/test-validators.py:454) is extended:
(a) An edge edit in a SKILL.md followed by the heal: the COMMITTED tree (`git archive HEAD` into a temp directory) passes build-registry --check and build-related --check.
(b) Another session's touch file claims a reciprocal SKILL.md: the heal is skipped and none of its files are staged.
(c) A dirty SKILL.md with no touch-list (the Cursor case): the heal is skipped.
(d) A generator stub sleeps past its cap: it reports SKIPPED, the handler returns 0, and push is attempted only if the reserve remains.
(e) A hanging push stub is killed at 12 s and the commit is kept.

Live exit: build-registry --check exits 0 at HEAD.

**Token impact.**

The AGENTS.md sentence is reworded (about ±10 tokens). contract_floor is measured before and after with `workspace-harness.py --tokens` and must stay ≤ 10,384. The census report is read on demand only.

**Profile behaviour.**

Applies to the personal-solo workspace checkout only (CLAUDE_PROJECT_DIR) and never touches employer repos. The census counts only git-tracked paths, so untracked employer folders on the Work MBP never change the numbers.

### H2 — Declared profile resolver with two axes (owner profile and credential scope), plus migration of the repo classifiers

- **Wave / effort / layer / enforcement:** 0 · M · tool · deterministic
- **Home (new):** 09-tools/profile_resolve.py (+ `!09-tools/profile_resolve.py` whitelist line in .gitignore; `git check-ignore` confirms it is ignored today) reading a new declared table 02-shared-references/delivery-playbooks/context-remotes.json (tracked via `!02-shared-references/**`) + extend 00-context-profiles.md step 3 (Sean sign-off) + extend beacon-enroll.sh and workspace-doctor.sh
- **Depends on:** —
- **ZV sources:** 23 (profile-aware part only), Ideology caution: zero handoff vs employer walls, OV-02, ZV-OTH-01, C-C0

**Why this home.** No shared resolver exists in 09-tools. The declared-data design follows wsx gitscope's remote → scope → identity map (07-projects/18-bootstrap-generator/generator/wsxlib/gitscope.py, context/remotes.json) and dest.py's 'walls by scope, not employer org names'. 09-tools does not import wsxlib, because wsx is a separately distributed package (generator/pyproject.toml). The table sits beside the playbook whose 'Changing this file' rule already requires Sean's sign-off.

**Problem.**

Constraint 6 needs one mechanical wall answer for every new write path.

The repo classifiers are forked, with hardcoded markers:
- 00-bootstrap/beacon-enroll.sh classify(), lines 38-46;
- the inline skips in 00-bootstrap/doctor/workspace-doctor.sh:132,137.

The github-work → employer result is a documented fail-safe, not a bug:
- beacon-enroll.sh:14 and its refusal at :109, '(standing rule)';
- github-work is the workspace credential on the Work MBP by design (06-context/memory/feedback-credential-scoping.md:35-38);
- wsx gitscope.py resolve_scope also treats github-work as work.

02-shared-references/delivery-playbooks/00-context-profiles.md defines three profiles plus a `visibility: public` flag. Its step-2 declaration is a SESSION-STATE line OR a project-context.md entry. Its step-3 remote rule is host-specific (`github.com/snds/*`).

The real employer remotes on this Mac use an owner spelling that no current marker matched, so an employer checkout resolved unknown: fail-safe, but unlabelled. The per-device detail is held (F-14).

**Mechanics.**

resolve(path, declared=None, explicit=None) returns {owner_profile, credential_scope, visibility, source, reason, qualified}.

The resolution order is the playbook's, verbatim:
1. Sean's explicit word.
2. The project declaration: the first backticked token of the SESSION-STATE 'Context profile' line, or the project-context.md entry. Lines with EXCEPT/lane qualifiers set `qualified`.
3. The remote, looked up by host + owner in the table. The code holds no org literals.
4. unknown.

If reality contradicts a declaration, the result is `conflict`, naming both sides (the playbook's 'stop and surface it'). It does not silently pick the most restrictive.

Profiles are personal-solo | centric-engineering | centric-design | unknown, plus the visibility: public flag. Callers that must act without asking use a restrictiveness lattice in which unknown/conflict = the union of all restrictions: no commit, no push, stdout only, confidential. credential_scope comes from the host alias and is a separate axis (github-work → work).

write_allowed(res, branch, action):
- personal-solo: True;
- centric-engineering: commit or push only off the default branch, never merge;
- centric-design: no repo writes;
- unknown or conflict: False.
Sean-declared `grants` rows in the table (for example 12-MCS's saas-plm-analysis PR+commit+merge grant) are treated as rank-1 input.

CLI: `profile_resolve.py <path> [--json] [--for beacon] [--table P] [--self-test]`, plus `guard` (H15). `--for beacon` reproduces today's behaviour: employer when credential_scope=work or the owner is Centric. That fail-safe stays until Sean changes the playbook.

Migration, in the same wave:
- beacon-enroll.sh classify() and the doctor skips call the CLI, keeping their case statements only as the fallback when python3 is absent.
- artifact-ingest.py:37 keeps its path tuple under a parity assertion (⊆ the table's path markers).
- cursor-externalize.py (a destination map for Cursor slugs) and prune-our-branches.py (a repo list, not a classifier) are allowlisted with reasons.

A proposed playbook diff lands only with Sean's sign-off: step 3 becomes 'owner per context-remotes.json (the host alias is the credential, not the owner)', and centricsoftware is added.

**Detector and fixtures.**

TestProfileResolve uses a synthetic `--table` fixture with synthetic owners (example-personal, example-employer), so no real employer repo names go into tracked fixtures. Cases:
- git@github-work:example-personal/x.git → owner personal-solo, credential work, and `--for beacon` → employer (today's behaviour).
- git@bitbucket.org:example-employer/app.git → centric-engineering.
- No remote → unknown.
- Declared personal-solo with an employer remote → conflict, naming both sides.
- A qualified SESSION-STATE line (synthetic copy of the 12-MCS shape) → its token plus qualified.
- A grant row → write_allowed(merge) is True for that repo only.
- centric-design → no writes.
- visibility: public → propagated.

Fork detector: scans classify-shaped code (functions named classify / is_employer* / refuse_path, and shell `case` arms matching remotes) in 09-tools/*.py and 00-bootstrap/**/*.sh. Employer marker literals outside profile_resolve.py and the declared fallbacks/allowlist fail it. Docstrings and test fixtures are exempt.

wsx gitscope is declared an intentionally separate distributable, with a parity fixture: the same synthetic remotes must give the same credential_scope.

Wiring: QUALITY_CHAIN (--self-test); validator-fixtures and workspace-integrity path filters (profile_resolve.py, context-remotes.json, beacon-enroll.sh).

**Token impact.**

0 always-loaded. The table is never auto-loaded. 00-context-profiles.md grows by about 2 lines; it is already priced under REQUEST_EXTRAS.

**Profile behaviour.**

The resolver never writes; it is the wall. Beacon enrollment does not change until Sean decides (open decision). Edits to context-remotes.json fall in the SENSITIVE diff class (H10), so every loosening shows up in gate output and the commit suffix.

### H3 — Harden intent-run before extending it: quote-aware parser, '#'-free approval grammar, escaped table pipes, shell=False measures with an allowlist in automated contexts, a no-git-write self-test, CI wiring

- **Wave / effort / layer / enforcement:** 0 · S · tool · deterministic
- **Home (extend):** 09-tools/intent-run.py + .github/workflows/{validator-fixtures,workspace-integrity}.yml (path filters: intent-run.py only) + 09-tools/workspace-harness.py QUALITY_CHAIN + 09-tools/close-out-dispatch.py HUB_DETECTORS + 09-tools/test-validators.py TestIntentRun (line 259)
- **Depends on:** —
- **ZV sources:** 5 (closure must be CI/hook-triggered), zv-live-07, zv-inv-verify, BRIEF anti-pattern: audit skills that auto-commit, C-C1

**Why this home.** intent-run already owns the spec parser. The tool has to be fixed and proven before any new grammar lands on it.

**Problem.**

Verified in 09-tools/intent-run.py (588 lines):
- _split_frontmatter (line 66) runs `val.split("#",1)[0]`, which truncates 'approved via PR #12'. A whitespace-only rule would still truncate it.
- MEASURE_RE `(.+)$` (line 44) passes any suffix into the shell.
- cmd_verify runs `subprocess.run(c["measure"], shell=True)` at line 426, so a prefix allowlist can be bypassed with `; …`.
- _parse_table (lines 72-89) has no `\|` escape.
- There is no --self-test, and cmd_doctor always returns 0.
- intent-run.py is in neither workflow's path filter.
- HUB_DETECTORS['intent-coordination'] is only `intent-run doctor` (close-out-dispatch.py:135).

**Mechanics.**

(1) Frontmatter parsing:
- An inline `#` starts a comment only after whitespace and outside quotes (YAML-style). Template comments still strip.
- The approval grammar has no '#': `approved YYYY-MM-DD by <name>` | `approved via PR 12` | `waived (<reason>)`.
- Cross-references use `<slug>#F-003` with no whitespace, so they survive.
- The parser records what it stripped. lint ERRORs when the approval value lost a `#\d+` comment ('write PR 12 or quote it').

(2) `_parse_table` accepts `\|` escapes. Commands and regexes never live in table cells: closures go to an ID-keyed list (H8) and structure rules to fenced JSON (H13).

(3) MEASURE_RE stops at the next ` -- <key>:` delimiter.

(4) Measures always run through shlex.split with shell=False, and cwd is pinned to the governed checkout (the workspace root for vault specs). In automated contexts (CI or WS_HOOK set):
- argv[0] must be python3 or sys.executable;
- argv[1] must be a `git ls-files`-tracked 09-tools/*.py;
- the raw string must contain none of ; & | ` $ < >;
- otherwise the result is NOT_EXPOSED with exit 2.
Manual runs print each argv before executing.

(5) `--self-test` covers the parser cases plus an AST invariant: no subprocess call in intent-run.py passes commit, push, merge, reset, stash or rebase to git.

(6) Wiring:
- Workflow path filters gain 09-tools/intent-run.py only; workspace-integrity's `**/*.md` already covers the template and INTENT*.md.
- QUALITY_CHAIN gains ('intent-run.py', ['--self-test']).
- HUB_DETECTORS['intent-coordination'] becomes (_cli intent-run --self-test, _skip 'doctor is environment info, not a detector').
- `lint --all` joins in H5.

(7) The three hand-rolled frontmatter parsers (build-registry.py:73, intent-run.py:50, vault-health.py) are recorded as H14 instance rows, so extracting a shared helper happens on evidence, not here.

**Detector and fixtures.**

TestIntentRun planted cases:
- `approval: approved via PR 12` round-trips.
- A quoted `"approved via PR #12"` round-trips.
- An unquoted `approval: approved via PR #12` → lint ERROR.
- `blocked_by: remediation-2026-09#F-003` round-trips.
- `profile: personal-solo # c` → personal-solo.
- A cell `(foo\|bar)` parses as one cell.
- `- [ ] x -- measure: python3 a.py -- signal: y` → measure 'python3 a.py'.
- A copied source containing `subprocess.run(['git','commit'])` → --self-test exits 1.
- Under CI=1, `python3 09-tools/x.py; touch <tmp>/pwned` does not run, the file is absent, exit 2.
- Under CI=1, an untracked 09-tools/evil.py → exit 2.
close-out-dispatch --check stays green. A commit touching intent-run.py triggers validator-fixtures CI.

**Token impact.**

0.

**Profile behaviour.**

The no-git-write invariant holds in every profile. shell=False applies everywhere, so a spec row authored in any repo cannot chain commands.

### H4 — Project-intent block in the project README (vault projects) or PROJECT.md (external personal repos), the home AGENTS.md's Project contract names; job specs point at it. Neutral engineer variant plus a workspace-leak scan class for employer repos

- **Wave / effort / layer / enforcement:** 1 · M · template · deterministic
- **Home (extend):** 00-bootstrap/templates/project-readme.md (block + `lifecycle:` frontmatter; line 19 repoint) + .claude/skills/new-project/SKILL.md (Step 3 calls init --frame; Step 6 line 82 repoint) + 02-shared-references/intent-spec.md (about 12-line 'Project intent block' grammar, `intent:` pointer, REQUIRED_SECTIONS reconciliation) + 02-shared-references/workspace-ontology.md (one routing row) + 09-tools/check-secrets.py (opt-in `workspace-leak` class) + new 06-context/memory/decision-project-intent-in-readme.md (indexed in MEMORY.md)
- **Depends on:** H2, H3
- **ZV sources:** 1, 10, 25, 34, zv-vector-md, OV-08, OV-09, OV-12, ZV-DOC-03, zv-live-01 (verbatim-defaults anti-pattern), zv-live-13, C-C2 (pointer-first, 40-line cap)

**Why this home.** The AGENTS Project contract is the declared per-project entry point (README first, PROJECT.md for external repos). Agents already read it first, and it is permanent. #17, the intent-coordination When-NOT list and the ontology's spec row stay true without edits. check-secrets is the existing content scanner that never echoes a match, so leak detection is a new pattern class there, not a third scanner.

**Problem.**

Gap (a): no project declares its problem, audience, knowns and unknowns. The existing fragments are ad hoc: 20-lcars SPEC.md and 21-shadegraph DESIGN-PLAN.md (ws-projects map Q1).

The living spec is the wrong home, per four sources:
- 01-frameworks/17-intent-coordination-operating-model.md:26: a spec file is required only for multi-agent work; single-agent work keeps its outcome in the Live handoff.
- 03-skills/intent-coordination/SKILL.md:48: 'skip a new spec file'.
- workspace-ontology.md:89: 'A living intent spec (multi-agent plan)'.
- Lifecycle: project intent is permanent, while job specs are meant to close.

AGENTS.md's Project contract already names the per-project home: README.md first, then 'a universal local context file such as PROJECT.md'.

The routing instructions are stale. .claude/skills/new-project/SKILL.md:82 and 00-bootstrap/templates/project-readme.md:19 tell agents to edit dispatcher TRIGGER_WORDS, which is now loaded from trigger-routes.json (dispatcher.py:101).

The standard (02-shared-references/intent-spec.md, 9 required sections) and the template (7 headings, with profile/lane as frontmatter and evidence as a Task-graph column) already disagree.

**Mechanics.**

A `## Project intent` block, capped at 40 lines, with three H3 sections:
- Problem & audience: a named role and its pain, with no personal data.
- Knowns & unknowns: a table with columns claim | label (#04 known/inferred/assumed/unknown/conflicted) | tier (#04) | evidence | decision rule. The decision rule is written before the evidence, in 08-knowledge/data-science/experiment-validity-baseline.md phrasing: 'if <X> we <A>; if <Y> we <B>'. The six pre-registration fields apply only when the claim is experiment-shaped, which validate-evidence-grades --strict already lints.
- Out of scope & later: the scope fence plus a Later list of at most 15 items, reviewed when the lifecycle changes.

Every field may instead be a pointer (`→ path#heading`) or `n/a (reason)`. `[HUMAN: …]` marks fields only Sean can fill. No default principles are injected.

README frontmatter gains `lifecycle: discover|define|build|operate`. It is orthogonal to `status:`, and it is not called 'stage', which #17 already uses.

For external personal repos, the same block goes in a root PROJECT.md and the vault README points at it.

Job specs gain an optional `intent: → <path>#project-intent` and `kind: coordination|remediation` (missing means coordination). Specs stay job-scoped and closable.

`intent-run.py init --frame [--path]` writes the block idempotently as a regenerated marker-delimited section, the pattern from wsx adopt (projects.py:136). /new-project Step 3 calls it. Step 6 and project-readme.md:19 are repointed to trigger-routes.json.

In the same commit as the one-home test, the standard reconciles its 9 'required sections' into three kinds: frontmatter keys (profile, lane, approval, northstar), headings, and Task-graph columns (evidence).

Employer and unknown profiles: `init --frame` refuses unless `--neutral` is passed. --neutral emits an engineer-voiced variant with no workspace skill names, no 09-tools measures, no [HUMAN:] marker and no hash, printed to stdout unless write_allowed permits a write.

check-secrets.py gains an opt-in class, `--class workspace-leak --stdin|--paths`. Its denylist:
- `[[`, `07-projects/`, `06-context/`, `03-skills/`, `01-frameworks/`, `09-tools/`;
- `snds/workspace`, `WORKSPACE-BEACON`, `personal-solo`;
- `intent-run`, `[HUMAN:`, `intent_hash:`;
- 'framework #NN'-shaped references;
- skill names read programmatically from the registry.
It reports only pattern name and line, never the text.

**Detector and fixtures.**

H5 enforces the block. Two one-home tests in TestIntentRun:
- The README template's block headings == intent-run PROJECT_INTENT_SECTIONS == the standard's list.
- The spec template's headings == REQUIRED_SECTIONS[kind] == the standard's reconciled list.

Fresh `init --frame` output FAILS `lint --project` from define onward, because of its HUMAN markers. A filled fixture passes.

check-secrets fixtures:
- Today's 00-bootstrap/templates/intent-spec.md FAILS `--class workspace-leak`, because its Task graph seeds intent-coordination and mission-fit.
- The --neutral variant passes.
- The default run is unchanged, since the class is opt-in.

**Token impact.**

0 always-loaded. The standard grows about 12 lines (about 150 tokens), paid only when routed. The README template is copied by init, not read by agents.

**Profile behaviour.**

- personal-solo: direct commits.
- centric-engineering: the neutral variant only. It lives in the employer repo, arrives via PR with human review, and is never copied into the vault.
- unknown: stdout only.
(RULES.txt: employer repos never receive personal-workspace content.)

### H5 — intent-run lint / approve / next / verify --record: lint scaled by lifecycle, declared-vs-disk drift, per-repo profile agreement, TTY-only approval hash, and verify records in the existing mission-fit + evidence-grade vocabulary

- **Wave / effort / layer / enforcement:** 1 · M · validator · deterministic
- **Home (extend):** 09-tools/intent-run.py (+ HUB_DETECTORS, QUALITY_CHAIN, a .gitattributes merge=union line for *.verify.jsonl, TestIntentRun, a note in 02-shared-references/intent-spec.md on the two sidecars, 03-skills/intent-coordination/SKILL.md body ≤6 lines)
- **Depends on:** H2, H3, H4
- **ZV sources:** 2, 8, 10, 11 (narrowed to hash + append-only Changelog), 13 (append-only class), 26, 27, 34, zv-inv-doctrine, zv-operator-bracket, zv-opt-validate, zv-live-02, zv-live-03, C-C3, C-C4

**Why this home.** One parser for one grammar. The verify vocabulary is mission-fit's, not a new one. A second spec reader would recreate ZV's two-dialect anti-pattern.

**Problem.**

Gap (b) plus trust defects verified in intent-run.py:
- approval_ok (lines 122-124) accepts any string starting with 'approved' or 'waived'.
- task_status trusts an explicit 'verified' as written.
- A dry verify returns 0.
- #17's spec-laundering ban (line 111) has no detector.

The workspace already has a verification vocabulary:
- 03-skills/mission-fit/SKILL.md:163 grades each check PASS / FAIL / UNKNOWN with VERIFIED / USER_REPORTED / INFERRED / NOT_EXPOSED.
- 09-tools/validate-evidence-grades.py enforces those grades.

Real profile declarations are qualified prose, not enum values: 07-projects/19-workspace-brain/SESSION-STATE.md:23 and 07-projects/12-MCS/SESSION-STATE.md:40.

**Mechanics.**

`lint [--spec P | --project P | --all] [--report] [--notice] [--since REF]`

Spec checks:
- REQUIRED_SECTIONS[kind].
- Enums: profile (including centric-design) and kind.
- The approval grammar (H3) and unfilled template tokens.
- A measure on every checklist item: WARN while the pointed-at project is at discover or unknown, ERROR from define on.
- Declared-vs-disk: northstar, contract, writes and preserve paths must exist in the governed checkout ('spec and disk disagree — update one of them').
- `→` pointers must resolve inside the same checkout; a cross-checkout pointer is a WARN ('unresolvable here').
- L-P1 profile agreement (see below).

Project-block checks:
- PROJECT_INTENT_SECTIONS by lifecycle.
- HUMAN markers: ERROR at build/operate, WARN before.
- Assumed and unknown rows need a decision rule from define on.
- The 40-line cap.

L-P1 is per repo:
- If the spec's git toplevel is not the workspace root, compare `profile:` with profile_resolve for that checkout.
- Inside the vault, compare with the first backticked token on the project's SESSION-STATE 'Context profile' line.
- A qualified line gives a WARN naming both sides. A declared grant is honoured. A conflict gives an ERROR naming both sides.

A spec with no `kind` is legacy and gets WARN only. `--report` counts legacy specs, HUMAN markers and cycle time (created → first PASS → closed), for information only. `--all` covers only `git ls-files` 07-projects/*/docs/INTENT*.md plus tracked READMEs that carry the block.

`approve --by NAME`:
- Refuses without a TTY, or when CI or WS_HOOK is set.
- Writes `approved YYYY-MM-DD by NAME`, `approved_via: cli` and `intent_hash:`. The hash is sha256 over Outcome, Northstar, the checklist labels and measures, and the pointed-at block's decision rules; checkbox state is excluded.
- lint WARNs 'self-approved' when the approval line lands in the spec's creating commit.

`gate` BLOCKS on HUMAN markers, or on a hash mismatch with no dated Changelog line naming the changed section. `status` prints a computed `next:`.

`verify` vocabulary:
- Status is PASS / FAIL / UNKNOWN (mission-fit).
- Grade is VERIFIED (an allowlisted measure ran in this invocation), USER_REPORTED (`-- signed: <date> by <who>` or `human:`) or NOT_EXPOSED (untrusted skip, or human input pending).
- A pending human item is UNKNOWN and exits 2. Exit 0 requires every item to PASS, with USER_REPORTED passes listed separately. There is no new ATTESTED word.

`verify --run --record` appends {ts, head_sha, intent_hash, item, measure, status, grade}. For personal-solo it writes the tracked, append-only `<spec-stem>.verify.jsonl` (merge=union). For any other profile it writes `$(git rev-parse --git-dir)/intent-verify/`, never the working tree. The standard documents both sidecars: the local gitignored `<stem>.state.json` (intent-run.py:176-190, .gitignore:154) and the tracked verify.jsonl.

ready and next treat a task as 'verified' only if a PASS record newer than the spec's last commit exists.

Same commit (the first breaker):
- `lint --all` joins HUB_DETECTORS['intent-coordination'] and QUALITY_CHAIN.
- 19-workspace-brain/docs/INTENT.md gets `kind: coordination` and is closed with a Changelog line. Its optional install-app wave becomes a Later item in that project's README block.

#13 walk for intent-coordination (command-hub):
- L1: #17 unchanged, and the spec stays job-scoped.
- L2: lint / approve / next / verify --record, re-walked when H8 and H9 add subcommands.
- L3: --self-test plus lint --all, with every subcommand fixture reachable through --self-test from the hub row.
- L4: unchanged, no new spoke.
- L5: the verifier role and defers_to unchanged.
The description and triggers are not broadened.

**Detector and fixtures.**

TestIntentRun planted cases:
(1) An item with no measure while the project is at build → 1.
(2) An assumed row with no decision rule at define → 1.
(3) A HUMAN marker at build → 1; at discover → WARN.
(4) Outcome edited after approve with no Changelog line → gate BLOCKED.
(5) A decision rule edited after approve → BLOCKED.
(6) An unchecked human: item → verify exits 2 with UNKNOWN/NOT_EXPOSED.
(7) A missing declared path → 1.
(8) `→ SPEC.md#Nope` in the same checkout → 1.
(9) A synthetic qualified SESSION-STATE line → WARN, not ERROR.
(10) A synthetic conflict → ERROR naming both sides.
(11) A vault-resident spec with profile centric-engineering and a matching SESSION-STATE → 0. Its remote is not compared, because the toplevel is the workspace root.
(12) A task marked 'verified' with no PASS record → ready treats it as running.
(13) Two --record runs append 2N lines.
(14) An employer-profile spec's records land under the git dir, and the working tree is unchanged.
(15) approve under CI=1 or with no TTY → refused.
(16) A legacy spec → 0 plus WARN.
Live: `lint --all` is green on the migrated tree.

**Token impact.**

0 always-loaded. The intent-coordination body grows by at most 6 lines, loaded only on trigger. The AGENTS 'Living spec (scale)' line is unchanged.

**Profile behaviour.**

Read-only except `approve`, which writes only the spec file and only where write_allowed permits (personal-solo). Employer specs accept only `approved via PR 12`. Their verify records never enter the employer working tree, so a `git add -A` cannot sweep them in. Stated residual: the hash proves no silent change after approval, not who approved; the TTY requirement makes agent self-approval hard, not impossible.

### H6 — Machine entry-point parity: one ENTRY_POINTS list that the three existing adapter lists derive from, fixes to every hit including CLAUDE.md:81 and .cursor/agents, hook-copy parity, and pricing for cursor_floor, hook_injection and trigger-routes.json

- **Wave / effort / layer / enforcement:** 1 · M · validator · deterministic
- **Home (extend):** 09-tools/workspace-harness.py (ENTRY_POINTS defined once; check_entry_points in the connections lane; cursor_floor + hook_injection; QUERIED_NOT_INGESTED += trigger-routes.json) + 09-tools/validate-workspace.py and 09-tools/evaluate-surface-trajectories.py derive their lists from ENTRY_POINTS + same-commit fixes to llms.txt, .cursor/rules/brain.mdc, CURSOR.md, CLAUDE.md:81, .cursor/agents/*.md, workspace-ontology.md:82, AGENTS.md step 4 (wording only), the TRIGGER_WORDS/KNOWLEDGE_HINTS doc sites + .cursor/hooks/cursor-sessionend.sh becomes a one-line exec of the dist copy
- **Depends on:** H1
- **ZV sources:** 19, zv-live-12, zv-live-03, zv-invest-md, OV-21, OV-23, ZV-ONB-01, B-C2

**Why this home.** workspace-harness already owns BANNED_INGEST, QUERIED_NOT_INGESTED, CONTRACT_FLOOR and ADAPTERS. The other two tools import from it (importlib, following artifact-ingest.load_secrets), so the plan consolidates three lists into one instead of adding a fourth.

**Problem.**

At least 13 read-order and restated-fact defects, verified 2026-09-22:
- llms.txt:12 and :14 link skills.registry.json and trigger-routes.md under 'Start here'.
- llms.txt:29 says 'append an attributed session-log entry'.
- .cursor/rules/brain.mdc:28-29 (alwaysApply) teaches the banned read order.
- brain.mdc:40 still lists `Enterprise`→Windows, which CLAUDE.md says is retired.
- CURSOR.md:23 routes through trigger-routes.md.
- CLAUDE.md:81 (auto-loaded) routes through 'trigger-routes.md + 03-skills/skills.registry.json'.
- workspace-ontology.md:82 says 'append a session block'.
- .cursor/agents/workspace-bootstrap.md:16 and :18, lead-ui-designer.md:18 and :20, ds-advisor.md:22 and lead-ux-designer.md:19 restate the banned order.

'Edit dispatcher TRIGGER_WORDS/KNOWLEDGE_HINTS' instructions persist at new-project SKILL.md:82, project-readme.md:19, delivery-playbooks/README.md:88, 08-knowledge/_README.md:96, :128, :130 and knowledge-vault-design.md:43.

Three adapter lists already exist:
- workspace-harness.py:491 ADAPTERS (6 files);
- validate-workspace.py:34-47 ADAPTER_MD (7 files plus a 40-line cap);
- evaluate-surface-trajectories.py:61-68 HOOKLESS_ADAPTERS with check_hookless_adapters (line 192).

Two tracked copies of cursor-sessionend.sh are byte-identical (`cmp`): .cursor/hooks/ is the one .cursor/hooks.json runs, and 00-bootstrap/dist/ is installed user-globally.

trigger-routes.json is 40,528 bytes (about 10k tokens). It is named in AGENTS.md read-order step 4 but is priced nowhere: not in BUDGETS, BANNED_INGEST or QUERIED_NOT_INGESTED.

**Mechanics.**

ENTRY_POINTS is a list of records {path, hook, adapter, line_cap} covering: llms.txt, AGENTS.md, CLAUDE.md, CURSOR.md, GEMINI.md, PERPLEXITY.md, WARP.md, CONVENTIONS.md, .github/copilot-instructions.md, .windsurf/rules/workspace.md, 00-bootstrap/adapters/web-session.md, 00-bootstrap/dist/{RULES.txt, BEACON.md, user-CLAUDE.md}, .cursor/rules/*.mdc and .cursor/agents/*.md.

line_cap is 40 only for today's ADAPTER_MD set (80 for web-session). It is not imported onto CURSOR.md, the .mdc files or the agent files. check_hookless_adapters iterates the records where hook=false.

Checks:
- P1, read order: flags a BANNED_INGEST or QUERIED_NOT_INGESTED path inside a read-order context (headings containing Start here / read order / Session start, numbered steps, `→` chains). Prohibition lines pass.
- P2: check_named_detectors runs over ENTRY_POINTS.
- P3, RESTATED_FACTS, observed drift only: the fragment rule vs 'append…session-log / session block'; the retired machine label `Enterprise`→Windows; 'edit dispatcher TRIGGER_WORDS / KNOWLEDGE_HINTS'.
- P4: every entry point is matched by at least one workflow path filter. Add llms.txt, .cursor/** and 00-bootstrap/dist/**.
- P5: tracked hook copies (.cursor/hooks/* vs 00-bootstrap/dist/*) are byte-identical unless the local copy is a one-line exec.
- P6, tokens: cursor_floor = AGENTS.md + the alwaysApply .mdc files, held under the existing 11,800 contract budget. hook_injection = the worst-case session-status card plus the SessionStart heads, under a new budget (open decision). QUERIED_NOT_INGESTED gains ('02-shared-references/trigger-routes.json', '09-tools/evaluate-skill-routing.py --utterance').

The same commit fixes every P1 and P3 hit. AGENTS.md step 4 becomes 'query with `python3 09-tools/evaluate-skill-routing.py --utterance "<text>"`; never ingest', at the same length.

**Detector and fixtures.**

--self-test on a fake root:
- An llms.txt Start-here that links skills.registry.json fails.
- A 'never ingest skills.registry.json' line passes.
- An .mdc read order naming trigger-routes.md fails.
- A .cursor/agents file with an AGENTS → registry → trigger-routes chain fails.
- A restated 'append … session-log' is counted.
- 'Enterprise→Windows' is counted.
- An entry point in no path filter fails.
- Divergent hook copies fail.
- An alwaysApply .mdc that pushes cursor_floor over budget fails.
- validate-workspace still caps GEMINI.md at 40 lines and does not cap CURSOR.md.
test-validators mirrors these as negative fixtures. The check fails on today's tree, so it lands in the same commit as the fixes.

**Token impact.**

Net negative: the llms.txt bullets shrink, and the always-applied brain.mdc gets shorter on every Cursor request. CURSOR.md is the worst adapter (1,538 tokens, `workspace-harness.py --tokens`) and sets contract_floor, so it is measured before and after; the target is ≤ 10,384. trigger-routes.json becomes priced, not paid.

**Profile behaviour.**

Workspace-only files, committed directly. BEACON.md is validated but its content is unchanged. The check never reads employer repos.

### H7 — Layer-0 routes through the one matcher: intent and onboarding keys in wave 1, remediation and closure keys shipped with H8; anchor- and subcommand-resolving target check; dead dispatcher dicts retired

- **Wave / effort / layer / enforcement:** 1 · S · shared-reference · injected-advisory
- **Home (extend):** 02-shared-references/trigger-routes.json (+ skill-routing-cases.jsonl expect_routes/forbid_routes, surface-trajectory-cases.jsonl, knowledge-hints.json; trigger-routes.md regenerated by 09-tools/build-trigger-routes.py) + 09-tools/workspace-harness.py check_layer0_targets + route-key overlap check + .claude/hooks/dispatcher.py (remove the dead dicts)
- **Depends on:** H4, H5, H6
- **ZV sources:** 1, 4, 5, 6, 9, zv-reading-order, OV-13, C-C5 (forbid cases)

**Why this home.** Constraint 3: there is one matcher (09-tools/prompt_route.py, decision-one-matcher-per-workspace), and the corpus already supports expect_routes and forbid_routes.

**Problem.**

On 2026-09-22, `python3 09-tools/skill-loadset.py` matched nothing for every probe. `evaluate-skill-routing.py --utterance` gave:
- 2 probes with no route;
- 'codebase audit and remediation plan' hitting only the generic `audit` → #06 route.

Other problems:
- 'adopt this repo' collides with the existing `wsx project adopt` (07-projects/18-bootstrap-generator/generator/wsxlib/projects.py:214).
- The engineering home (03-skills/eng/SKILL.md; #14:171 'audit requires measurement') was bypassed.
- check_layer0_targets (workspace-harness.py:186-206) checks that the file exists, but not anchors or subcommands.
- check_trigger_collisions (line 384) sees only skill frontmatter.
- dispatcher.py:101 TRIGGER_WORDS and :106 KNOWLEDGE_HINTS appear unreferenced (`git grep` finds only their definitions), leaving a second hint table beside knowledge-hints.json.

**Mechanics.**

Wave 1 keys (multiword only):
- 'knowns and unknowns', 'problem statement', 'project brief', 'product brief', 'definition of done', 'spec for a new build' and 'new build project' → 02-shared-references/intent-spec.md#project-intent-block, plus `intent-run.py init --frame` / `lint --project`.
- 'onboard this repo' and 'backfill the repo' → 00-context-profiles.md + intent-spec.md#project-intent-block. The hint reads 'resolve profile first (profile_resolve.py); employer or unknown = --neutral, stdout only'.
- 'codebase audit' and 'repo audit' → 03-skills/eng/SKILL.md + 01-frameworks/14-engineering-operating-model.md. The corpus asserts they ALSO hit the existing `audit` → #06 route (QA always-load).
- 'adopt this repo' is dropped.

Wave 2, landing with H8: 'remediation plan', 'findings register', 'close the audit' and 'done but not closed' → intent-spec.md#findings + `intent-run.py verdict`.

Wave 3, landing with H12: 'research record' and 'assumption log'.

Knowledge hint: 'zero vector' / 'investiture' → the ZV note, once the ZV session tracks it.

New keys go after the existing high-priority routes (per-tier caps, prompt_route.py:25-31). The intent-coordination description and triggers are not broadened.

Target checks:
- check_layer0_targets now resolves `path#anchor` against headings and `intent-run.py <subcommand>` against its argparse subcommands, so a route landing before its target fails.
- A new route-key overlap check (keys that are substrings of each other with different targets) reports against a ceiling.

The unreferenced dispatcher.py TRIGGER_WORDS and KNOWLEDGE_HINTS dicts are removed. git history is the provenance, and no file is removed.

**Detector and fixtures.**

`evaluate-skill-routing.py --check` requires an expect_routes case per key. forbid_routes cases:
- 'this is a known issue' → no knowns route.
- 'audit this' → only `audit`.
- 'Frame this card in Figma' → no intent route.
- 'adopt this repo' → no new route.
'codebase audit and remediation plan' → eng + #06 in wave 1, plus findings from wave 2.

`evaluate-surface-trajectories.py --check` needs at least 2 parity cases (claude-code, cursor).

Anchor fixtures: a route to intent-spec.md#nope fails check_layer0_targets, and a route naming `intent-run.py verdict` before H8 lands fails.

The overlap-check fixture is a planted substring collision. Dispatcher fixtures stay green after the dicts are removed. validate-layer0-schema --check and evaluate-skill-routing --lint also run.

**Token impact.**

Per prompt: +1–3 hint lines, only on a match. trigger-routes.json grows about 1 KB and is priced by H6. Removing the dicts shrinks dispatcher.py.

**Profile behaviour.**

prompt_route already resolves the brain from employer working directories and injects pointers only. The hint text states the wall. Nothing is written into employer repos.

### H8 — Remediation spec: read-only recon card (ported from wsx adopt), findings register with namespaced origins, packets, preserve list, mission-fit verdict; snapshots never edited; reports indexed in artifact-registry; the workspace's own findings as dogfood

- **Wave / effort / layer / enforcement:** 2 · L · tool · deterministic
- **Home (extend):** 09-tools/intent-run.py (init --recon, verdict, findings lint rules, next) + 02-shared-references/intent-spec.md and the template (optional kind: remediation sections) + 09-tools/validate-evidence-grades.py (--status lane, tracked-only) + 06-context/artifact-registry.md (register the reports) + 07-projects/19-workspace-brain/reports/README.md + 06-context/memory/decision-workspace-automation-first-wave.md (As-of correction)
- **Depends on:** H2, H3, H5
- **ZV sources:** 4, 5, 6, 7, 8, 13 (source_sha only), 21 (record-counted loop-breaker, no revert), 22, 24, 25, 26, zv-inv-preflight, zv-inv-repo-audit, zv-inv-remediate, zv-inv-verify, zv-live-04, zv-live-05, zv-live-06, zv-live-07, zv-live-08, OV-04, OV-15, ZV-QG-05, B-C1 rules L4-L8, C-C7, C-C9, C-C11

**Why this home.** A remediation plan is a job spec whose tasks are packets. Findings are current state in one file, and reports stay dated snapshots per artifact-standards §3 ('Never silently overwrite'). artifact-find is the report index. The recon ports wsx adopt's scan pattern (07-projects/18-bootstrap-generator/generator/wsxlib/projects.py:124-200) rather than importing a separately distributed package.

**Problem.**

Gaps (d) and (h), verified 2026-09-22.

The companion: chain already carries the report-to-report dispositions:
- workspace-automation-review_v1.0: 'A4/A5/A8/A9 deferred'.
- automation-second-wave_v1.0: A4/A5/A9 applied, A8 deferred.
- figma-bind-probe_v1.0: A8 applied.

But the current-state memory file 06-context/memory/decision-workspace-automation-first-wave.md:25 still says 'A8 … still waits'. process-rigor-gaps_v1.0 has 'applied … load-miss 1–15' in frontmatter and 'recs 1–15 still open' at line 25.

Report indexing is incomplete:
- `git ls-files` shows 10 versioned reports; reports/README.md lists 4.
- The README says the primary write path is 05-artifacts/active, which is wholly untracked.
- `python3 09-tools/artifact-find.py` returns no match for these reports.
- workspace-automation-review's R1–R3 (refusals) collide with process-rigor's R1–R16.

Elsewhere:
- 'Ledger' already means open-agent-engine's status ledger (SKILL.md:15) and #11's Visual Failure-Mode Ledger.
- ZV's verify step expected IDs its audit never minted (zv-inv-verify).

**Mechanics.**

(1) Recon, `init --recon DIR`
- Ports wsx adopt's read-only pattern: skip dirs, secret-name hints that are never opened, language counts, a regenerated marker block `<!-- intent:recon:start -->`.
- Adds only source_sha, tests/CI/lint presence and hazards. Hazards: files above the target repo's own p99 line count; a lockfile older than its manifest; 3 or more languages; monorepo markers. Thresholds come from the repo's own data, not ZV's list; the idea provenance is ZV invest.md:175.
- The persisted card stores only a COUNT of secret-shaped filenames. The names go to stdout only.
- Labels: manifest/config = known, extension counts = inferred, naming only = assumed.
- Employer and unknown remotes: stdout only.
- lint WARNs 're-recon' when source_sha is more than 50 commits behind on declared paths.

(2) `## Findings`, called a 'findings register', not a 'ledger'. Columns:
- id: F-NNN, never reused.
- sev: Critical/High/Medium/Low, the ds-advisor DDR scale. a11y_audit.py's blocker/major/minor/nit map onto it 1:1, as documented.
- status: OPEN/RESOLVED/DEFERRED.
- origin: namespaced `<report-slug>#<ID>`, recon, or external.
- observed, expected, evidence.
- closure: a C-ID pointing into an ID-keyed `### Closures` list (`- C-003: measure: python3 09-tools/x.py --check` or `judgment: <who>`), never a command inside a cell.
- closed_by: a sha, a verify record or a decision note.
- revisit: required for DEFERRED; a date or `on: <trigger>`.
`## Preserve` holds glob | why | until.

(3) Packets: one `### T<n>` per implementor. They reuse Open Engine's cold-agent fields and add Last verified state (sha), Non-goals, Verification, Rollback (a worktree or branch; never reset an employer default branch), Bail point and Previous attempts. `next` orders by severity within risk band.

(4) Lint rules:
- IDs are unique.
- RESOLVED needs closed_by. DEFERRED needs a reason and a revisit.
- `status: closed` is refused while any row is OPEN.
- An implementor without a packet is an ERROR.
- A Preserve entry without `until` is an ERROR; an expired one is a WARN.
- No silent drop: `--since REF` fails if an F-ID vanished.
- blocked_by refs must resolve.
- Loop-breaker: ready and worktree add refuse a task with 3 or more FAIL records in verify.jsonl since its newest Previous-attempts entry. No revert.

(5) `verdict` speaks mission-fit:
- Fit (no OPEN Critical/High, and packet measures PASS VERIFIED) → exit 0.
- Fit with gaps (only Medium/Low OPEN, or DEFERRED with a revisit, listed) → exit 0.
- Unfit (OPEN Critical/High, or REGRESSED) → exit 1.
- Blocked (a Critical/High closure is NOT_EXPOSED) → exit 2.
gate refuses a spec whose blocked_by upstream is Unfit or Blocked. CI's `lint --all --run-closures` re-runs allowlisted closures (H3 rules) on RESOLVED rows; a failure is REGRESSED.

(6) Legacy reports are never edited. `validate-evidence-grades.py --status` is report-only against a census ceiling and walks `git ls-files` report roots only. It flags a versioned report whose frontmatter status pairs a closure word with ID ranges while no tracked findings row cites it in `origin`. Resolution runs one way: register → report. A report whose own status must change gets a v1.1 per §3. There is no `ledger:` key and no §3 exception.

(7) Dogfood, in wave 2:
- Create 07-projects/19-workspace-brain/docs/INTENT-remediation-2026-09.md (kind: remediation). It imports A1–A10 and R1–R3 (origin workspace-automation-review#…), R1–R16 (process-rigor-gaps#…) and load-miss 1–15 (harness-map_v2.0_2026-09-11#…).
- A8 is RESOLVED, closed_by figma-bind-probe_v1.0.
- The memory decision gets an As-of correction.
- The reports are registered in 06-context/artifact-registry.md.
- The README's 'Current reports' table is replaced by `python3 09-tools/artifact-find.py --path 19-workspace-brain/reports`, and its 'primary write path' sentence is corrected.

(8) Clean-room check: before any new template or standard text lands, run a one-shot 8-token n-gram overlap check against the scratch ZV corpus (never vendored). The result goes in the H4 memory decision.

#13 re-walk of intent-coordination L2/L3: the new subcommands' fixtures are reachable through --self-test.

**Detector and fixtures.**

TestIntentRun planted cases, each exiting 1 unless noted:
- a duplicate F-ID;
- RESOLVED without closed_by;
- DEFERRED without a revisit;
- a closed spec with an OPEN row;
- an implementor without a packet;
- a Preserve entry without `until`;
- an F-ID dropped relative to `--since` (temp git repo);
- blocked_by pointing at an Unfit spec → gate BLOCKED;
- 3 FAIL records with no new Previous attempts → worktree add refuses;
- a RESOLVED row whose allowlisted closure now fails → REGRESSED;
- `workspace-automation-review#R2` and `process-rigor-gaps#R2` coexist → 0;
- a11y blocker maps to Critical.

Recon self-test on a temp repo containing package.json, tests/, a long file and a .env:
- the expected fields and source_sha are present;
- open() is never called on .env;
- the card holds a count, not names;
- the target tree is byte-identical after the run;
- an employer-shaped synthetic remote writes nothing.

validate-evidence-grades --self-test replays the real A8 shape: flagged with no citing row, passes with a citing RESOLVED row, and an untracked c8_* report is ignored.

**Token impact.**

0 always-loaded. The remediation sections are read only when that spec is opened. One findings register replaces reading 3 or more reports to learn their state (inference).

**Profile behaviour.**

- personal-solo: committed in the project's docs/.
- centric-engineering: recon to stdout only. Findings and packets live in the employer repo via PR (neutral variant, H4 leak scan) or in gitignored 05-artifacts/active/c8_*, never in tracked vault files.
verdict and gate never commit and never auto-close. Machine locality: the real personal repos needed for the wave-2 recon exit live on the Personal MBP.

### H9 — Write-set scope as task data: writes/forbids globs, disjoint-wave lint, read-only verifier, committed contract before fan-out, diff-vs-scope check

- **Wave / effort / layer / enforcement:** 2 · M · tool · deterministic
- **Home (extend):** 09-tools/intent-run.py (cmd_gate, cmd_ready, new `scope`) + 00-bootstrap/templates/intent-spec.md Task graph columns
- **Depends on:** H5, H8
- **ZV sources:** 14 (globs only, no standing crew), 15, 23 (diff-scope + sensitive denylist; no restore-point hook), OV-02, OV-06, ZV-ORCH-01, ZV-ORCH-05, ZV-ORCH-07, ZV-QG-03, zv-opt-crew

**Why this home.** The runner already records each task's worktree and branch (cmd_worktree_add; `<stem>.state.json`), so no new state store is needed.

**Problem.**

Gap (g). The template's Task graph (id, role, skill, isolation, depends_on, status, evidence) has no path scope. The .cursor/agents definitions carry load chains only. The dispatcher's touch-lists (dispatcher.py:1418-1575) scope commits by session, not by declared task. #17's two-writers ban is enforced only by worktree isolation.

**Mechanics.**

The Task graph gains `writes` and `forbids` glob columns ('-' for none), read with H3's escape-aware parser. Frontmatter gains `contract:` paths.

`gate`:
- Expands each wave's implementor globs against `git ls-files`. A tracked file matched by two same-wave implementors is an ERROR naming both globs.
- A verifier with any `writes` is an ERROR.

`ready` releases 2 or more parallel implementors only when every contract path exists and is committed at HEAD. Otherwise it releases only the first.

`scope TASK [--base REF]` runs in the task's recorded worktree. It diffs `git diff --name-only $(git merge-base <base> HEAD)` plus untracked files, and exits 1 on any path that is:
- outside `writes`;
- inside `forbids`;
- on the sensitive denylist, unless explicitly owned. The denylist imports check-secrets.py SKIP_NAMES (lockfiles) and adds package manifests, .github/workflows/**, .env* and *.pem;
- an H8 Preserve path.
`generated:` globs are allowed.

`status` shows scope pass/fail/unchecked, and a task cannot show verified while scope fails. The restore point is the worktree `worktree add` already creates: no checkpoint commits, no stash, no reset.

**Detector and fixtures.**

TestIntentScope on temp git repos:
- overlapping writes in the same wave → gate 1;
- a verifier with writes → 1;
- two parallel implementors with no committed contract → ready lists one;
- an out-of-glob file → scope 1;
- an unowned package-lock.json → 1, with the denylist constant shared with check-secrets;
- a Preserve path → 1;
- in-scope changes and generated globs → 0;
- a glob cell containing `\|` parses as one cell.

**Token impact.**

0.

**Profile behaviour.**

Read-only git only. In employer repos it runs locally against the PR branch as advisory evidence for the human reviewer. Any writes/forbids table that lives in an employer repo uses the H4 neutral variant, and merging stays human.

### H10 — Diff-computed gate selection that references QUALITY_CHAIN steps, charged-vs-ambient attribution seeded from session touch-lists, and compliance measured by extending ws-audit's transcript scan (close-out-dispatch)

- **Wave / effort / layer / enforcement:** 2 · M · validator · deterministic
- **Home (extend):** 09-tools/close-out-dispatch.py (DIFF_CLASSES beside HUB_DETECTORS; --from-diff/--staged/--range/--budget/--fast/--telemetry) + QUALITY_CHAIN in 09-tools/workspace-harness.py as the step source + 00-bootstrap/dist/workspace-audit.sh (COMPLY line) + 03-skills/harness-map/SKILL.md step 4
- **Depends on:** H1, H3, H6
- **ZV sources:** 16, 17, 24, 33 (closure/catch metrics only), ZV-QG-01, ZV-QG-04, ZV-QG-06, OV-15, zv-live-14, B-C4, B-C6

**Why this home.** close-out-dispatch is already the one place that decides which detectors prove a change, with honest exits (0/1/2). QUALITY_CHAIN is already the proven read-only invocation of every validator. ws-audit already owns transcript-based compliance measurement. One selector, one chain, one telemetry log.

**Problem.**

AGENTS.md says gates are 'Embedded, not commit-only', but nothing computes which validators a change needs. close-out-dispatch selects detectors from the prompt, not the diff.

The CI filters miss the NON-markdown files under 00-bootstrap/ and .claude/ (.py, .sh, .txt, .json, .mdc) plus llms.txt. workspace-integrity's `**/*.md` already covers the markdown.

Most tracked tools have no --self-test. build-registry.py, build-related.py and compact-sessions.py treat unknown flags as write mode (their main() reads sys.argv as a set), so an invented `--self-test` step would rewrite tracked files from inside a hook.

Whole-tree validators name the file that CONTAINS a dangling link, so a deleted or renamed note breaks only unchanged files.

Existing homes cover the rest:
- The dispatcher's touch-lists and _other_session_claims (dispatcher.py:1531-1574) already separate this session's paths from concurrent ones.
- ws-audit (00-bootstrap/dist/workspace-audit.sh) already scans transcripts into ~/.claude/ws-state/audit.log.
- harness-map's Probation/Retire (SKILL.md:157-158) has no catch data.

**Mechanics.**

(1) DIFF_CLASSES maps path globs to QUALITY_CHAIN step names. QUALITY_CHAIN is imported from workspace-harness via importlib, so every invocation is an already-proven flag set, and no flag is invented. Parametrised chain steps (e.g. `intent-run lint --spec <each>` for the chain's `lint --all`) are declared explicitly.

Classes:
- skills; layer0; tools (test-validators plus the tool's chain entry, if any); hooks (.claude/hooks/**, 00-bootstrap/**); specs; entry points (H6); reports; markdown (validate-integrity, validate-workspace, vault-health).
- projects (07-projects/** → markdown), so opting a new project into tracking never turns --check red.
- all paths → check-secrets.
- SENSITIVE (.github/workflows/**, .gitignore, .gitattributes, .claude/settings.json, context-remotes.json, 00-bootstrap/dist/settings-user-fragment.json) → flagged in output and in the commit suffix.

`--check` asserts:
- every class step exists in QUALITY_CHAIN (or is a declared parametrised step whose flags argparse accepts);
- every QUALITY_CHAIN step belongs to at least one class;
- every class glob is covered by at least one workflow path filter;
- every tracked path falls in a class.
Generating the workflow YAML from this is deferred.

`--fast` drops steps measured over 5 s. Re-measured 2026-09-22 with read-only runs: related 0.25 s, registry 0.15, trigger-routes 0.13, layer0 0.12, skill-routing 1.91, close-out 0.13, validate-integrity 0.89, validate-links 0.21, validate-workspace 0.11, vault-health 0.54, check-secrets 1.26, about 5.7 s in total.

(2) Attribution. A failure is CHARGED when any of these holds:
(a) A class-owned generator or consistency step fails for a matched class: build-registry, build-related, build-trigger-routes, validate-layer0-schema, intent-run lint --spec.
(b) A whole-tree error names a changed path. 'Changed' means this session's touch-list minus other sessions' claims when a touch-list exists, otherwise the diff.
(c) An error's link target (wikilink stem or path) matches a D or R entry in `git diff --name-status`.
Everything else is AMBIENT: printed, never red. CI may also run whole-tree validators on the merge-base and on head inside the runner, and charge only new errors. Each step has a timeout under --budget; a timeout is SKIPPED.

(3) Results are written atomically to the gitignored .claude/state/last-gate.json: {tree, range, steps[name, rc, secs, charged], held}, plus a bounded ring of the last 50 runs. There is no separate gate-log.jsonl. A red result prints a failure-report skeleton: expected, observed, repro, `git log -1 -- <charged>`.

(4) `--telemetry --since 30d` reads the ring plus `git log --grep '\[gate:'` (the H11 commit suffixes, which are portable across machines) and prints machine coverage.
- A catch = red, then green on the same detector after a diff touching the charged paths.
- An FP candidate = red cleared with no diff to those paths, or a bypass.
- Probation candidacy (harness-map step 4) needs corroboration from commit-suffix history or CI, not one machine's ring.
Sean decides every disposition; nothing auto-prunes.

(5) Compliance: ws-audit's existing single transcript pass emits one `COMPLY <sid> dispatch=a/b receipts=c/d` line into its existing audit.log:
- dispatch = the injected close-out followthrough vs an actual close-out-dispatch.py Bash call;
- receipts = injected SKILL.md paths vs Read tool_use calls (a Labrador-style context receipt, pages/11-labrador.md).
The line holds counts only, and has no ' MISS ' token, so doctor_misses (session-status.py:185) is unaffected. It covers Claude only; Cursor sessions report an honest SKIP. No hook logs followthroughs.

(6) There is no identity gate row: it would contradict feedback-credential-scoping.md.

#13 walks:
- close-out: L1 #06 + agentic-error-correction foundations; L2 steps + CLI flags; L3 --check / --from-diff / --telemetry self-tests; L4 and L5 unchanged.
- harness-map step 4: L2 step text; L3 close-out-dispatch --telemetry --self-test; others unchanged.

**Detector and fixtures.**

TestCloseOutDispatch (test-validators.py:368):
(a) Cursor-class replay: a temp tree with a SKILL.md edit and a stale registry exits 1, charged to skills via build-registry.
(b) A docs-only diff runs only markdown steps.
(c) Removing `.claude/hooks/**` from a fixture workflow → --check fails.
(d) A class naming `build-registry.py --self-test`, which is not in QUALITY_CHAIN → --check fails.
(e) A sleeping step → SKIPPED, exit 2.
(f) An untracked-file integrity error outside the diff → AMBIENT, exit 0.
(g) Deleting a note linked from an unchanged file → CHARGED.
(h) With a touch-list, errors on another session's claimed path → AMBIENT.
(i) A newly tracked 07-projects folder → classed, --check green.

`--telemetry --self-test` on a synthetic ring and a synthetic git log checks: a catch, an FP, and that a single-machine-only candidate is not listed for Probation.

ws-audit fixture transcript → `COMPLY dispatch=0/1 receipts=2/3`, and the doctor_misses count is unchanged.

QUALITY_CHAIN gains `close-out-dispatch.py --telemetry --self-test`.

**Token impact.**

0 always-loaded. Failure output appears only on red. last-gate.json is listed in QUERIED_NOT_INGESTED with --telemetry as its CLI.

**Profile behaviour.**

Runs on the workspace checkout only and is never installed as a gate in employer repos. ws-audit COMPLY lines carry counts only, no paths and no prompt text. There is no gh-based metric, because gh's shared default config holds the device's default account, which is the employer account on an employer-default device (`devices.json`).

### H11 — Closure triggers at session and git boundaries: SessionEnd gate through nightly.py's verify phase, git hooks installed only by Sean's explicit command, one conditional notice line. Report-only first; later a per-machine opt-in hold for charged regressions only

- **Wave / effort / layer / enforcement:** 2 · M · hook · deterministic
- **Home (extend):** .claude/hooks/dispatcher.py handle_session_end + 09-tools/nightly.py (verify phase, H1) + 09-tools/session-status.py _notices (line 241) + tracked 00-bootstrap/dist/git-hooks/{post-commit,pre-push} + explicit `--install-git-hooks` / `--uninstall-git-hooks` modes in 00-bootstrap/doctor/workspace-doctor.sh + 00-bootstrap/dist/cursor-sessionend.sh (.cursor/hooks copy becomes an exec of it) + .claude/skills/session-end/SKILL.md Step 6 + 03-skills/close-out/SKILL.md step 2 (one line)
- **Depends on:** H1, H2, H5, H8, H10
- **ZV sources:** zv-live-07 (closure triggered by something other than memory), 5, 16, 22, ZV-QG-05, ZV-MEM-01, ZV-AUD-01, A-H6 push-hold, B-C5, B-C7, C-C6

**Why this home.** Git hooks are the one boundary that Claude, Cursor and a human all pass through (portable-first). nightly.py already sequences verify-then-commit-if-green, so SessionEnd calls it instead of a second orchestration. session-status is the card every surface prints, and its existing unpushed line carries the hold state.

**Problem.**

Cursor commits never pass the Claude-only SessionEnd, and that is how HEAD went red. Supporting facts:
- Both tracked copies of cursor-sessionend.sh only nudge.
- No non-sample git hooks exist, and `git config core.hooksPath` returns rc=1.
- SessionEnd auto-commits and pushes without running validators (dispatcher.py:1611-1695).
- Nothing surfaces a spec that is done but not closed.

Channels that already exist:
- nightly.py already verifies, then refuses to commit on red.
- session-status already has an 'N unpushed commit(s)' line (:270-271) and a harness-map.stamp staleness notice (:259-263).

Constraints on the design:
- The doctor runs unattended: `--quick` on every SessionStart (workspace-sessionstart.sh:78) and a launchd run every 14,400 s. So it must not set persistent git config on its own.
- _push_with_retry runs `git pull --rebase` when it loses a race (dispatcher.py:1577-1608), which changes the tree.

**Mechanics.**

SessionEnd sequence, inside H1's deadline:
1. fold (existing);
2. heal (`nightly --phases rebuild`, with H1's staging rules);
3. stage;
4. gate: `nightly.py --phases verify --from-diff --staged --fast --budget ≤20 --json`. It runs only if at least 20 s remain after the 12 s push reserve; otherwise it is SKIPPED;
5. commit with the suffix `[gate: green|red:<detectors>|skipped]`;
6. push via _push_with_retry, with env WS_GATE_RESULT=<tree> and WS_PREPUSH_BUDGET=<remaining>.

Hold rule: a push is held only when this clone has opted in (`git config --local ws.pushgate block`, set only by the explicit installer) and the gate is CHARGED red. A hold skips the push and sets held=true in last-gate.json. Everything fails open on timeout, exception or rc 2. `WS_PUSH_GATE=off` is the kill switch. `WS_GATE_BYPASS='<reason>'` allows one push and is recorded in the last-gate ring; an empty reason is refused.

Git hooks (tracked stdlib Python):
- Installed ONLY by `workspace-doctor.sh --install-git-hooks [--blocking]`, which Sean runs. `--uninstall-git-hooks` unsets core.hooksPath and ws.pushgate. `--quick` and launchd only REPORT drift.
- They exit 0 as a no-op when python3 or the workspace root is missing, or when the repo toplevel is not the workspace.
- post-commit is a no-op during rebase, cherry-pick or am (.git/rebase-merge, .git/rebase-apply, CHERRY_PICK_HEAD, GIT_REFLOG_ACTION contains rebase). It dedupes via an O_EXCL lock keyed on HEAD^{tree}. If WS_GATE_RESULT is set, it records and exits. Otherwise it detaches `nightly.py --phases verify --range HEAD~1..HEAD --budget 8` and exits 0 at once.
- pre-push: if WS_GATE_RESULT is set (SessionEnd pushes, including the rebase-retry path), it trusts that result. Otherwise it runs `--from-diff --range @{u}..HEAD --budget min(30, WS_PREPUSH_BUDGET)`. It is report-only unless ws.pushgate=block, and then exits 1 only on CHARGED failures.

Notices: session-status gains at most ONE conditional line, with a 1.5 s budget, fail-open, printing 'skipped (budget)' rather than staying silent:
'Closure: N spec(s) need closure · last gate red: <detectors>'
It draws on `intent-run lint --all --notice` (vault-tracked only) and last-gate.json. The existing unpushed line is annotated '(held: gate red)' when held. There is no push-held.md and no 'detector review stale' line.

Cursor: .cursor/hooks/cursor-sessionend.sh becomes a one-line exec of the dist copy. The dist copy adds the gate line only when the payload's workspace root resolves to the workspace, never in employer cwds.

close-out step 2 gains: 'if this work resolves a finding, set closed_by; intent-run lint verifies'.

Typical SessionEnd budget: compaction ≤2 s (inference) + heal about 0.5 s + fast gate about 5.7 s + commit <1 s + push 2–5 s ≈ 10–14 s. The worst case is bounded by the 52 s deadline.

**Detector and fixtures.**

session-status --check with synthetic inputs:
- red → one line; clean → none.
- Held → the unpushed line is annotated.
- A budget overrun prints the skip line.
- The ABI line is unchanged.

Dispatcher fixtures (TestScopedCommit pattern):
- A gate timeout still commits and returns 0.
- With ws.pushgate=block, a charged red → push not called, held recorded.
- rc 2 → push called.
- WS_PUSH_GATE=off → push called.
- An empty bypass reason is refused.

Temp-repo git-hook fixtures:
- post-commit always exits 0.
- post-commit during a synthetic rebase state → no-op.
- Two post-commits on one tree → one gate run.
- pre-push with WS_GATE_RESULT → no gate run, including after a simulated pull --rebase.
- report-only red → exit 0 with a note.
- blocking on a charged regression → 1; a red in an untouched path → 0.
- Hooks with no python3 or no workspace root → exit 0.
- `--uninstall-git-hooks` restores the unset config.
- The doctor in `--quick` mode never sets core.hooksPath.
- Cursor replay: a SKILL.md commit without regeneration in a temp clone with hooks installed is reported.

cursor-sessionend fixture: an employer cwd payload → no gate line.

**Token impact.**

0 when clean. At most 1 card line (about 30 tokens), priced under H6's hook_injection. close-out grows about 25 tokens, only when it loads.

**Profile behaviour.**

Hooks apply only to the workspace clone, and only after Sean runs the installer. Opt-in for beacon-enrolled personal repos is an open decision. They are never installed in employer repos: the installer refuses via profile_resolve, and the hooks refuse non-workspace toplevels. Blocking only withholds a push; the commit is kept locally and never reverted.

### H12 — Research-record lint over tracked files and Nygard-style project ADRs (demand-triggered): decision-rule records, evidence-gated personas, PII as an opt-in check-secrets class

- **Wave / effort / layer / enforcement:** 3 · M · validator · deterministic
- **Home (extend):** 09-tools/vault-health.py (`--research [--root DIR]`, `--graph`) + 09-tools/check-secrets.py (opt-in `pii` class) + 02-shared-references/delivery-playbooks/06-research-and-design-artifacts.md ('Records' subsection) + new 00-bootstrap/templates/project-adr.md (Nygard shape) + pointers of 3 lines or fewer in 03-skills/pm-discovery-research/SKILL.md and 03-skills/ux-research-synthesis/SKILL.md + 01-frameworks/04-research-and-evidence-framework.md (pointer)
- **Depends on:** H4, H7
- **ZV sources:** 9, 10, 11 (provenance part), zv-research-schemas, ZV-PIPE-02, ZV-PIPE-03, zv-opt-research-loop, zv-opt-validate, zv-opt-synthesize, zv-opt-adr, zv-adr-template, C-C10

**Why this home.** vault-health already parses `relations:` and errors on dangling typed edges. check-secrets is the tracked-file content scanner. The research skills are the existing method homes. The ADR shape matches the only existing project ADR, so nothing needs migrating.

**Problem.**

Gap (e): 02-shared-references/domain-constitutions/dc-research.yaml has `measurement: []` and `command: []`. Its note near line 83 says this is on purpose: 'protocol + named tier, not a scanner'. vault-health.py:29 SCOPE excludes 07-projects.

Gap (f): the only project ADR is 07-projects/20-lcars-generative-interface/docs/adr/ADR-001-sys47-measured-fills.md. It is Nygard-style, with body Date/Status lines and no frontmatter. #14 asks for 'an ADR per structural decision' in the repo.

Personas: #04:31 bans INVENTED personas, and playbook 06:171 specifies research-grounded ones.

BRIEF constraint 10 (no identifiable participant data) has no detector.

**Mechanics.**

This ships only when at least one tracked personal project keeps records, at `<project>/docs/research/<proj>-<kind>-NNN-slug.md`.

Kinds:
- assumption, interview-finding, insight, jtbd, evidence.
- decision-rule: the signal plan, in experiment-validity-baseline phrasing, with `registered:`. The six pre-registration fields apply when it is experiment-shaped, via validate-evidence-grades --strict.
- persona: allowed only with at least one builds-on evidence edge and a #04 tier.

Fields:
- review_status: agent-draft | human-confirmed | retracted.
- claim/tier: #04 only.
- relations: the five verbs from the memory template.
- participants: must match ^P\d+$.

Scope: `--research` walks `git ls-files` only. `--root` must be given explicitly for a personal repo checkout. `--graph` refuses untracked paths. Output is relative paths and counts.

ERRORs:
- a bad prefix or a duplicate ID;
- a dangling relation;
- a label or tier outside #04;
- known + agent-draft with no evidence edge;
- confirming evidence dated before its decision-rule record's `registered:`;
- a persona with no evidence edge;
- a non-pseudonymous participant.
Refs to retracted records WARN, and `--cascade <id>` lists dependents.

PII: check-secrets gains an opt-in `pii` class (email/phone patterns, plus denylisted frontmatter keys email/phone/name/full_name/contact). It runs with --paths over records only, because legitimate addresses exist in memory files.

Project ADRs: Nygard-style (Date/Status/Context/Decision/Consequences). ADR-NNN is unique per project. Supersession is two-sided in the body: 'Superseded by ADR-NNN' ↔ 'Supersedes ADR-MMM'. It never uses `superseded_by:` frontmatter, which validate-integrity.py:15 treats as a live zombie. ADR-001 needs no migration.

ds-advisor's DDR is not linted (open decision on its Context-Quality ↔ #04 mapping).

#13 walk for the research domain:
- L1: #04 unchanged.
- L2: N/A, no command surface added.
- L3: this structural lane only. It is named research L3 only if Sean decides.
- L4: hub pointers.
- L5: N/A.
The 'research record' and 'assumption log' routes land here (H7).

**Detector and fixtures.**

TestResearchRecords, each failing unless noted:
- a dangling ref;
- a duplicate ID;
- participant 'Jane';
- known + agent-draft with no evidence edge;
- evidence dated before `registered`;
- a persona with no builds-on edge;
- a persona with an edge → PASS;
- ADR-002 'Supersedes ADR-001' while ADR-001 lacks 'Superseded by' → FAIL;
- an untracked record → ignored, and --graph refuses it;
- a retracted upstream → WARN, listed by --cascade.
check-secrets `--class pii --paths` on an `email:` key → 1, and the value is never echoed. vault-health gains --self-test; it is already in QUALITY_CHAIN and the CI filters.

**Token impact.**

0 always-loaded. Playbook 06 grows about 15 lines on route. The hub pointers are 3 lines or fewer each.

**Profile behaviour.**

Employer research (e.g. 10-centric-UX-research) stays on employer surfaces or in gitignored employer folders. The lane never walks untracked paths, so local results match CI.

### H13 — Declared-only structure conformance as the eng hub's L3 detector (demand-triggered)

- **Wave / effort / layer / enforcement:** 3 · M · tool · deterministic
- **Home (new):** 09-tools/structure-conform.py (+ .gitignore whitelist) + HUB_DETECTORS['eng'] row (--self-test) + a `### Structure` fenced JSON declaration inside the project-intent block (README/PROJECT.md, H4)
- **Depends on:** H4
- **ZV sources:** 3, zv-inv-architecture, OV-16, ZV-AUD-01, C-C14 (reshaped as a fenced JSON declaration)

**Why this home.** Structural conformance is the engineering hub's measurement, not coordination. Keeping it out of intent-run holds that runner to the spec lifecycle. Any spec can cite it through `measure:`.

**Problem.**

Gap (c): code repos have no structural conformance check.
- 09-tools/eslint-off-system and 09-tools/shadcn-lint own token and tier lint only.
- 03-skills/eng/SKILL.md owns 'review this architecture', and #14 (01-frameworks/14-engineering-operating-model.md:171) rules that 'audit requires measurement'.
- HUB_DETECTORS['eng'] (close-out-dispatch.py:102-107) is validate-integrity plus a product-ci SKIP, so eng has no L3 detector of its own.
- ZV's architecture check asked an LLM to walk every import.

**Mechanics.**

The declaration is a fenced ```json block {"layers":[{"name","glob","may_import":[…],"naming":"<regex>"}]}, so no regex sits in a table cell.

`structure-conform.py --decl <file> --repo DIR` extracts imports with stdlib code only: regex for JS/TS import / require / export-from (relative and alias), and ast for Python. It resolves importer and target to layers by glob.
- ERROR on an undeclared edge (file:line), a naming failure, or a missing declared layer directory.
- Undeclared categories are skipped.
- No declaration → exit 2.

Raw colour and token literals stay with shadcn-lint and eslint-off-system. Layer-bleed judgment stays with arch-guild.

It ships when at least one personal repo declares a Structure. ShadeGraph src/{model, compiler, nodes, preview, ui} is the likely first (inference), and its checkout is on the Personal MBP.

#13 walk (eng):
- L1: #14 unchanged.
- L2: the review verb.
- L3: --self-test added to HUB_DETECTORS['eng'] beside the product-ci SKIP.
- L4 and L5: unchanged (arch-guild multi-voice).

**Detector and fixtures.**

`structure-conform.py --self-test` on a temp repo:
- ui imports data while ui may_import only [domain] → 1;
- an undeclared category → 0;
- a naming violation → 1;
- a missing layer directory → 1;
- no declaration → 2;
- a naming regex `^(use|with)[A-Z]` parses intact.
It is added to QUALITY_CHAIN, the validator-fixtures filter and HUB_DETECTORS['eng'], and close-out-dispatch --check stays green.

**Token impact.**

0.

**Profile behaviour.**

Read-only on any checkout. For employer repos, the declaration must live in that repo in the neutral variant and arrive via PR. The output is local evidence for the human reviewer.

### H14 — Rule-of-three instance log in 06-context and a growth check that allows command-surface hubs and counts consumers for frameworks

- **Wave / effort / layer / enforcement:** 3 · S · validator · deterministic
- **Home (extend):** 09-tools/workspace-harness.py (connections lane: check_rule_of_three) + new 06-context/rule-of-three.jsonl (merge=union line in .gitattributes) + 09-tools/rule-of-three.baseline.json (+ whitelist) + 03-skills/self-improve/SKILL.md (Improve step)
- **Depends on:** H1
- **ZV sources:** 28, 18 (gap interview only), ZV-AUT-02, ZV-MEM-01, OV-05

**Why this home.** 06-context is the routing-map home for operational logs, and reports/ holds versioned audits. The baseline sits beside its owning tool, like 09-tools/shadcn-lint/baseline.json. workspace-harness is already self-improve's close-out detector.

**Problem.**

BRIEF constraint 1 exists only as prose:
- 03-skills/self-improve/SKILL.md:66 allows a hub, foundation or framework 'Only if a command surface is missing, or 3+ hubs re-derive the same principle'.
- AGENTS.md and the ontology require '3+ consumers' for a framework.
- 07-projects/19-workspace-brain/notes/error-correction-research_2026-08-26.md:23 and 08-knowledge/research/agentic-error-correction-foundations.md:289 restate it.
With no instance log, the rule can never fire on evidence.

Most 01-frameworks files have no frontmatter; 09-component-and-pattern-framework.md and 18-design-systems-ai-operating-model.md do. The check is therefore keyed by path.

session-log anchors move during compaction (AGENTS.md: the log 'is bounded by archival').

**Mechanics.**

Rows: {pattern, target, instance_ref, date, surface}. instance_ref must be a tracked path or a commit SHA, resolved with `git cat-file -e`; session-log anchors are not accepted. Only an explicit self-improve step appends rows, never a hook.

The baseline is generated once from current hubs, foundations and frameworks, and may only shrink relative to HEAD.

check_rule_of_three FAILs in two cases:
- A new hub or foundation (registry tier) that is not baselined, unless (a) at least 3 rows with distinct resolvable instance_refs target it, or (b) it is `rigor_role: command-hub` with a HUB_DETECTORS row (self-improve's command-surface branch).
- A new 01-frameworks/*.md with fewer than 3 inbound consumers (skills or frameworks linking it, counted by path).

self-improve changes:
(a) When a session restates a protocol that another workstream already restated, append a row instead of minting.
(b) Ask 'what would have helped at the start?' at session end, and route the answer to an existing Improve class, to a row, or to an explicit 'no vault gap'.

The first rows are seeded with the three hand-rolled frontmatter parsers (H3).

#13 walk for self-improve (command-hub):
- L1: #08.
- L2: the Improve steps.
- L3: check_rule_of_three through HUB_DETECTORS['self-improve'] = workspace-harness.
- L4 and L5: unchanged.

**Detector and fixtures.**

test-validators cases:
- a new hub with fewer than 3 rows → FAIL;
- 3 resolvable rows → PASS;
- a new command-hub with a HUB_DETECTORS row → PASS;
- a dangling SHA → FAIL;
- a session-log anchor → FAIL;
- a baseline that grew relative to HEAD → FAIL;
- a new framework with 2 consumers → FAIL, with 3 → PASS.

**Token impact.**

0 always-loaded. self-improve grows about 5 lines, only when loaded.

**Profile behaviour.**

Vault only (personal-solo). instance_refs are vault paths or SHAs and never carry employer substance.

### H15 — Employer-wall guard on agent git actions: a user-global PreToolUse check backed by the one resolver (new, from missing_from_plan)

- **Wave / effort / layer / enforcement:** 1 · S · hook · deterministic
- **Home (extend):** 00-bootstrap/dist/settings-user-fragment.json (PreToolUse matcher Bash) + new thin 00-bootstrap/dist/workspace-wallguard.sh (added to the doctor's existing repair_file list) + a `guard` subcommand in 09-tools/profile_resolve.py
- **Depends on:** H2
- **ZV sources:** 23 (profile-aware scope guard), Ideology caution: zero handoff vs employer walls, OV-02

**Why this home.** User-global hooks are the only layer that fires in employer cwds, and the doctor's fragment merge is the existing, sanctioned distribution channel for them. The decision logic stays in the one resolver, so no second classifier appears.

**Problem.**

The ws-projects map (Q5) calls the employer wall 'mostly advisory':
- The project .claude/settings.json PreToolUse matcher covers only `mcp__.*use_figma.*`.
- 00-bootstrap/dist/settings-user-fragment.json, the user-global layer and the only one that reaches employer-cwd sessions, has no PreToolUse entry at all.
Nothing mechanical stops an agent from committing, pushing or self-merging on an employer default branch. feedback-credential-scoping.md records a real identity leak into an employer repo. H2's write_allowed() would otherwise have no consumer where the risk is highest.

**Mechanics.**

A thin wrapper runs the guard only for commands in its scope (the matching rule is held, F-14); other commands get no decision.

guard parses the command and resolves the target repo, its profile and its default branch.

Decisions for centric-engineering:
- deny `git commit` on the default branch;
- deny a `git push` whose refspec targets the default branch, or any force-push to a shared branch;
- deny `git merge` into the default branch;
- deny `gh pr merge` (self-merge);
- allow branch commits and branch pushes, since branch → PR is the sanctioned path.
For other profiles:
- unknown or conflict → `ask` for push and merge;
- personal-solo → allow;
- declared grants are honoured.

The deny reason cites the profile: 'per centric-engineering: open a PR, not a merge'.

Fail-open: when the guard itself errors, it produces no decision and allows (declared residual, H17-R8 class; the triggers are held, F-14). The guard is a seatbelt; the doctrine and human PR review stay the wall.

Rollout: wave 1 ships with every deny downgraded to `ask` for 14 days. It flips to deny after zero false asks, by Sean's decision.

Cursor: wire the same CLI if Cursor's hook surface exposes a pre-shell event. That is inference: the events in the current cursor-hooks.json are sessionStart, beforeSubmitPrompt, preCompact, sessionEnd and subagentStop. If it does not, record the degrade in capability-registry.

**Detector and fixtures.**

TestWallGuard with a synthetic table and temp repos:
- employer `git commit -m x` on main → deny (ask during rollout);
- on a feature branch → allow;
- `git push origin HEAD:main` → deny;
- `git push -u origin feat` → allow;
- `gh pr merge 3` → deny;
- `git -C <employer> merge feat` while on main → deny;
- an unknown remote push → ask;
- personal → allow;
- a merge in a grant repo → allow;
- a malformed payload → no decision (declared fail-open, H17-R8 class);
- a command outside the guard's scope → no decision.
Runs through profile_resolve --self-test in QUALITY_CHAIN. The fragment and wrapper paths go into the path filters. An evaluate-surface-trajectories note records the Cursor degrade.

**Token impact.**

0. Nothing is injected into context; the deny reason appears only when the guard fires. Python starts only for commands in the guard's scope.

**Profile behaviour.**

Protective only: it never writes, and only denies or asks. It protects the centric-engineering walls in employer cwds. The fragment change lands only with Sean's approval, because the doctor then installs it on every machine.

## Sequencing

### Wave 0 — H1, H3, H2

A green HEAD, one regeneration sequencer, one wall resolver and a proven intent-run, all before any new gate or grammar. Order:
1. H1: nightly.py timeouts, budget and fixpoint, plus the order doctrine fix in the same commit.
2. H1: the wave-0 heal commit (`git commit -- <generator-touched paths>` only).
3. H1: dispatcher delegation and heal-staging safety.
4. H3: parser, shell=False measures, --self-test and CI wiring.
5. H2: resolver, declared table, migration of beacon-enroll and the doctor. The playbook diff is proposed to Sean.

**Exit gate.**

- build-registry.py --check exits 0 at HEAD, and the heal commit contains only generator outputs.
- nightly.py --self-test is green, and so are the TestScopedCommit extensions (committed-tree check, concurrent-claim skip, Cursor no-touch-list skip, timeouts).
- intent-run.py --self-test is green, including the '#' round-trip and `; touch pwned` fixtures, and a commit touching intent-run.py triggers validator-fixtures CI.
- TestProfileResolve is green, including the alias fixture asserting today's beacon behaviour, and the fork detector is clean.
- close-out-dispatch --check is green.
- The census is committed.
- contract_floor ≤ 10,384 after the AGENTS order sentence.
Sean's sign-off on the 00-context-profiles.md diff is requested but is not an exit condition.

### Wave 1 — H6, H15, H4, H5, H7

Make project intent a lintable declaration, make every machine entry point honest, and make the employer wall mechanical for agent git actions, with no growth in always-loaded text. Order:
1. H6: the check plus every fix (llms.txt, brain.mdc, CURSOR.md, CLAUDE.md:81, .cursor/agents, ontology, the TRIGGER_WORDS doc sites, AGENTS step 4 wording, hook-copy exec) in ONE commit.
2. H15 in ask mode, after Sean approves the fragment change.
3. H4: project block, neutral variant, workspace-leak class, standard/template reconciliation with the one-home tests.
4. H5: lint with the legacy WARN rule, disposition of 19-workspace-brain/docs/INTENT.md, and lint --all wiring, in ONE commit.
5. H7: intent and onboarding keys only, with anchor-resolving target checks, and the dead dispatcher dicts removed.
6. The write-quality chain in the fixpoint order.

**Exit gate.**

- `intent-run.py lint --all` is green, and every H5 planted fixture fails as intended.
- Entry-point defects go from at least 13 to 0 in the same commit as the check.
- contract_floor ≤ 10,384, measured before and after the CURSOR.md edit.
- cursor_floor and hook_injection are priced, trigger-routes.json is in QUERIED_NOT_INGESTED, and no existing BUDGETS key is raised.
- evaluate-skill-routing --check and evaluate-surface-trajectories --check are green with the new cases, including forbid cases and 'codebase audit' also hitting #06.
- check_layer0_targets resolves anchors and subcommands.
- TestWallGuard is green.
- The decision-project-intent-in-readme memory note is indexed, with the clean-room overlap result.
- close-out-dispatch --check is green.

### Wave 2 — H8, H9, H10, H11

Close the audit → remediate → verify loop and the write-scope loop with computed verdicts, then move validation to event boundaries that every surface shares (SessionEnd through nightly, explicitly installed git hooks), in report-only mode, measuring compliance through ws-audit. H7's remediation and closure routes land with H8.

**Exit gate.**

- The dogfood remediation spec is lint-clean with A8 RESOLVED, and the --status lane (tracked only) goes from 3 contradictions to 0.
- The reports are registered and artifact-find returns them.
- One personal project on the Personal MBP runs recon → findings → packets → verdict Fit, with scope passing on at least one worktree task.
- At least 20 gate runs are recorded across Claude SessionEnds and Cursor-path commits (last-gate ring plus commit suffixes), and the Cursor-path replay is flagged.
- SessionEnd gate p95 ≤ 20 s, post-commit < 1 s, and pre-push with WS_GATE_RESULT ≤ 1 s.
- Hooks exit 0 in 100% of report-only runs.
- FP candidates ≤ 1 per 20 runs.
- ws-audit COMPLY lines have been recorded for 14 days.
- hook_injection stays under its budget.

### Wave 3 — H12, H13, H14

Let Sean opt individual machines into blocking on charged regressions once wave-2 telemetry holds. Add breadth only where demand exists: research records and ADRs, structure conformance, and the rule-of-three growth check.

**Exit gate.**

- Blocking is enabled only by Sean's explicit `--install-git-hooks --blocking` on at least one machine.
- 30 days pass with no charged-red push reaching main, by commit suffix and CI.
- Every bypass carries a reason.
- The H14 baseline is committed and check_rule_of_three is green.
- H12 and H13 have each either shipped with a real consumer or are honestly recorded as not yet triggered.
- No BUDGETS are raised.
- New 09-tools files are limited to profile_resolve.py, structure-conform.py (if shipped) and named intent-run sibling modules if the ~900-line split fires.
- No new skill or framework exists.

## First breaker

The first breaker is wiring any gate before wave 0 heals HEAD and makes the SessionEnd heal safe under scoped commits. That covers `intent-run lint --all` in CI, QUALITY_CHAIN or HUB_DETECTORS, the SessionEnd gate, and the git hooks.

Why HEAD is red today:
- HEAD 22934df is red on registry drift only. `build-registry --check` returns rc=1, with stale hashes from the Cursor co-authored commits 41737cd and 8fcb70e. `build-related --check` returns rc=0.
- The validate-integrity red comes from the uncommitted in-flight ZV line in 08-knowledge/_INDEX.md. It belongs to that session's own close-out, not to the heal.

If the order were inverted:
- Every gate would fire on inherited debt.
- The wave-2 false-positive telemetry that must justify any blocking would be poisoned.
- Bypass would become a habit (decision-lint-narrow-or-not-at-all).
- Today's heal would keep committing a registry that hashes files the scoped commit never staged (dispatcher.py:1527).

Secondary ordering rules (a single commit, or a strict order):
(a) H3's quote-aware parser, '#'-free approval grammar and shell=False measures land before any '#'-bearing grammar and before any CI re-run of spec measures. Otherwise `approved via PR #12` silently truncates, and `; <cmd>` executes in CI.
(b) `lint --all` wiring lands in the same commit as the legacy WARN rule and the closing of 19-workspace-brain/docs/INTENT.md, which is all-checked while status is active.
(c) H6's check lands in the same commit as every entry-point fix, including CLAUDE.md:81 and the six .cursor/agents files. Otherwise it lands red.
(d) H7's remediation and closure routes land with H8, after check_layer0_targets resolves anchors and subcommands. Otherwise dead routes pass CI for a wave.
(e) H11's pre-push ships with the WS_GATE_RESULT passthrough and the rebase no-op. Otherwise the pull-rebase retry in _push_with_retry re-runs the gate inside the 12 s push cap and kills the push on exactly the multi-machine race path.

## Not adopted

- **Moving per-project intent into the living coordination spec (the previous H4)** — #17:26, the intent-coordination When-NOT list (SKILL.md:48) and ontology row :89 all scope the spec to multi-agent jobs. Project intent is permanent while specs close. The AGENTS Project contract already names README.md / PROJECT.md as the per-project home, so H4 uses that and specs point at it.
- **A `ledger:` frontmatter pointer on snapshot reports, plus an artifact-standards §3 exception** — This erodes 'Never silently overwrite' (artifact-standards.md:61-62) for no gain. Namespaced `origin` refs in the findings register resolve register → report one way; the existing `companion:` chain carries report-to-report dispositions; and a report whose own status needs correcting gets a v1.1 (H8).
- **Hardcoded employer org literals in resolver code, and an owner-only classifier that treats the github-work alias as personal** — The literals would recreate the fork problem. Owner-only loses the documented credential axis: github-work is the Work-MBP credential by design (feedback-credential-scoping.md:35-38), and beacon-enroll.sh:14 fails safe on it. H2 reads a declared table and returns two axes, and beacon behaviour is unchanged until Sean decides.
- **Importing wsxlib (gitscope, adopt scan) from 09-tools** — wsx is a separately distributed package (07-projects/18-bootstrap-generator/generator/pyproject.toml). H2 copies gitscope's declared-map design and H8 ports adopt's scan pattern, each with a parity fixture.
- **leak_scan and a PII denylist as new scanners in profile_resolve.py / vault-health.py** — check-secrets.py is the existing tracked-file content scanner that never echoes a match. Both become opt-in pattern classes there (workspace-leak in H4, pii in H12), not a third and fourth scanner.
- **New ATTESTED verify state and a GO/NO-GO verdict word** — mission-fit (SKILL.md:163) already defines PASS/FAIL/UNKNOWN with VERIFIED/USER_REPORTED/INFERRED/NOT_EXPOSED grades, plus the Fit / Fit with gaps / Unfit / Blocked verdicts. validate-evidence-grades.py enforces the grades. H5 and H8 reuse them.
- **A new validates/invalidates/ambiguous signal grammar** — 08-knowledge/data-science/experiment-validity-baseline.md already defines the pre-committed decision rule and the six pre-registration fields, linted by validate-evidence-grades.py --strict. H4 and H12 reuse that phrasing.
- **A per-machine gate-log.jsonl telemetry store with followthrough events appended by two hook entry points** — It would be a second telemetry store, and followthrough logic would be forked across dispatcher.handle_user_prompt and cursor-prompt-route.py (decision-one-matcher-per-workspace). Compliance comes from ws-audit's existing transcript scan; timings come from the last-gate.json ring; cross-machine history comes from commit-subject suffixes (H10).
- **A PostToolUse Read hook for context receipts** — It would add a hook call to every Read. The same receipt is derivable from the transcript ws-audit already parses at SessionEnd (H10).
- **An identity-vs-profile gate row, or changing repo-local git config** — It contradicts the standing decision in feedback-credential-scoping.md: Centric identity for workspace commits on the Work MBP, no identity flags. It would also hold every Work-MBP push once blocking is on. The playbook's 'Git identity' row goes to Sean as a documentation fix.
- **The doctor setting core.hooksPath automatically, and a tracked BLOCKING flag** — The doctor runs unattended (every SessionStart via --quick, and every 14,400 s via launchd), and a tracked flag would propagate to every clone on pull. Instead, hooks install only through an explicit `--install-git-hooks`, and blocking is per-clone `git config --local ws.pushgate block` (H11).
- **A push-held.md file, a 'detector review stale' notice, and up to 3 new notice lines** — The existing channels cover these: the unpushed line (session-status.py:270) is annotated '(held: gate red)' from last-gate.json, and the harness-map.stamp notice (:259-263) already covers review cadence. At most one conditional line is added (H11), given #17:28's no-session-tax rule.
- **Invented per-tool `--self-test` steps in the diff gate matrix** — build-registry, build-related and compact-sessions ignore unknown flags and write. DIFF_CLASSES may only reference QUALITY_CHAIN's proven invocations (H10).
- **B's separate finding-ledger.py tool, and in-place closures inside versioned v1.0 reports** — There is one parser (intent-run), and snapshots are never edited. The ledger rules survive as findings-register lint in the remediation spec (H8).
- **B's separate project-drift.py and a README `stage:` key (C8)** — The README is now the project-intent home (H4), but its lint belongs to intent-run's one parser, not a second tool, and 'stage' overloads #17's four stages. `lifecycle:` is used instead.
- **A `stage:` frontmatter key (both B and C)** — Name overload with 01-frameworks/17's 'Four ordered stages' (ZV had three 'Seven Principles'). The plan uses `lifecycle:`.
- **'Finding ledger' as the concept name, and an 'adopt this repo' route** — 'Ledger' already names open-agent-engine's status ledger (SKILL.md:15) and #11's Visual Failure-Mode Ledger. 'adopt' collides with `wsx project adopt` (projects.py:214). The plan uses 'findings register' / `## Findings` and 'onboard this repo'.
- **Structural conformance as an intent-run subcommand** — Code-structure measurement belongs to the eng hub's L3 (#14:171, HUB_DETECTORS['eng'] has only a SKIP). intent-run stays with the spec lifecycle; a standalone CLI is cited via `measure:` (H13).
- **A rule-of-three check requiring 3 instance rows for every new hub, foundation or framework, with its log in reports/ and session-log anchors as instances** — It contradicts self-improve:66's command-surface branch and the frameworks' '3+ consumers' rule. reports/ holds versioned audits, and anchors move during compaction. H14 exempts command hubs, counts consumers for frameworks, logs to 06-context, and accepts only tracked paths or SHAs.
- **Rejecting persona records outright** — #04:31 bans INVENTED personas, and playbook 06:171 specifies research-grounded ones. H12 allows personas only with builds-on evidence edges and a #04 tier.
- **A single memory-template shape for project ADRs (migrating ADR-001)** — The only project ADR is Nygard-style (ADR-001), and #14 asks for ADRs in the repo. H12 adopts that shape with two-sided body supersession, so nothing needs migrating.
- **C12 learning ladder (skills-as-levels, comprehension probes, coach mode) (BRIEF 31, 32)** — The probe answers can be read off the graded fields, so this is self-report (constraint 8), and nothing consumes levels. Only the end-of-session gap question is adopted (H14).
- **C13 wsx port and BRIEF 20 upgrade manifest** — This belongs in the 18-bootstrap-generator backlog: wsx upgrade.py already never clobbers hand edits. Revisit when the harness is distributed.
- **C9 `survey --write` into an employer repo on a non-default branch** — The most wall-exposed write path in any draft. Employer and unknown recon stays stdout-only (H8).
- **C7 separate docs/phases/<task>.md packet files and an archive tree** — A second current-state file would deviate from the mutation policy. Packets are `### T<n>` sections of the spec (H8).
- **C5 broadening intent-coordination triggers and description, or minting a build-lifecycle spoke** — That would stretch a command hub's identity without a #13 walk. Routing is done by trigger-routes.json keys (H7).
- **12 reads/writes/produces/consumes in skill frontmatter** — It touches the frontmatter of 301 skills and fails rule-of-three. Revisit after a second cross-skill artifact break.
- **13 vault-wide artifact lifecycle-class registry and freshness lane** — No consumer justifies a new index. Only part is adopted: sidecar roles are documented (H5), and recon carries source_sha (H8).
- **18 instruction-file lint (rationale per rule, review-by dates) and a comprehension probe** — Size is already gated by BUDGETS plus H6's floors. A per-rule rationale lint would be noisy (decision-lint-narrow-or-not-at-all), and a same-model probe is not independent measurement.
- **19 general fact registry for restated facts** — Detecting restated facts in general drifts toward an LLM judge. Only entry-point parity and a narrow observed-drift table are adopted (H6).
- **29 one-page operating model** — Duplicates AGENTS.md, CRITICAL_FACTS and the session-status card, and would compete for about 1.4k of contract_floor headroom.
- **30 external critique packet and scheduled dissent rhythm** — A scheduled rhythm needs a runner (decision-no-unattended-runner). Friction stays with the read-only verifier (H9), human items that are never VERIFIED (H5), mission-fit and arch-guild. Findings accept `origin: external`.
- **33 handoff-count north-star KPI** — It encodes ZV's zero-handoff ideology. Cycle time is reported for information only (H5).
- **4 full stamped MANIFEST inventory** — Snapshot inventories rot (zv-live-04). A recon card with source_sha and a staleness WARN is enough (H8).
- **3 LLM-judged categories inside the conformance gate** — Gates must be deterministic (constraint 8). Judgment stays with arch-guild (H13).
- **21 forced revert after N attempts, and default reflect-and-retry** — Destructive git operations violate the walls and the mutation policy, and reflect-and-retry is on the Do-not-build list. Only a refusal to re-dispatch, counted from verify records, is adopted (H8).
- **23 restore-point pre-hook and checkpoint commits** — Auto-commit is forbidden in centric-engineering, and concurrent sessions share an index. The worktree is the restore point (H9).
- **17 scheduled prune/promote cadence** — decision-no-unattended-runner. Telemetry is read when harness-map or self-improve runs, and Sean decides (H10).
- **14 standing named crew or per-role instruction files** — That would be a parallel agent framework (constraint 1). Roles stay rows with owned globs (H9).
- **11 interactive two-gate propose→diff→apply tool** — ZV's gates were conversational and could be skipped when non-interactive. Provenance stays deterministic: the approval hash, the Changelog and verify records (H5).
- **B's gh-cli 'escape' metric** — gh's shared default config holds the device's default account (see H10). Commit-subject gate suffixes give a portable metric instead (H11).
- **Markdown table cells for structure regexes or closure commands** — _parse_table splits on '|' (intent-run.py:72-89), so alternation regexes and piped commands would shift columns. The plan uses fenced JSON (H13) and an ID-keyed Closures list (H8).
- **A new closure skill or framework** — Prompt-only enforcement is the ZV anti-pattern, and constraint 1 requires 3+ consumers or rule-of-three evidence. The mechanisms fit existing homes.
- **ZV ideology (one auteur, zero handoff; design systems as overhead), auto-committing audits, a verify step that deletes REMEDIATION.md, verbatim default principles** — Each conflicts with the context-profile walls, Sean's DS practice, the mutation policy or the verbatim-defaults anti-pattern. The plan adopts ZV's mechanisms and rejects its ideology.
- **Vendoring ZV SKILL.md text, schemas or templates** — There is no upstream LICENSE (SOURCES.md), so the work must be clean-room. It is backed by a one-shot n-gram overlap check recorded in the H4 memory decision (H8 step 8).
- **Porting /optimize (Claude-only under .claude/skills) to a portable home, and a vault-side scan for employer-derived tracked content** — Real gaps, but outside this harness's scope. Both are raised as open decisions or self-improve items, not built here.
- **Generating CI workflow path lists from DIFF_CLASSES** — Deferred. H10's --check asserts coverage and step equivalence, which is enough until drift is observed.

## Risks

- **Gates fire on debt the diff did not cause: concurrent sessions, earlier Cursor commits, or links broken by a delete. The false holds train people to bypass.** — Attribution seeded from session touch-lists and claims, with class-owned generator checks charged to their class and D/R link targets charged (H10). Census ceilings that only go down (H1). Report-only through wave 2. Blocking is a per-machine opt-in for charged regressions only, after FP ≤ 1/20. Bypass requires a recorded reason.
- **The SessionEnd 60 s budget overruns: compaction, heal, gate, push and a nested pre-push hook.** — H1 deadline scheduler (52 s, 12 s push reserve). Per-step timeouts in nightly.py. The gate is SKIPPED under 20 s remaining. pre-push trusts WS_GATE_RESULT even after pull --rebase. post-commit is a no-op during rebase and deduped by tree. Measured fast set about 5.7 s, typical total about 10–14 s. Everything fails open with the commit kept.
- **SessionEnd now depends on nightly.py; a broken nightly would break the heal.** — If nightly.py is missing or its output is unparseable, the dispatcher falls back to today's build-registry-only heal. nightly --self-test is in QUALITY_CHAIN and the validator-fixtures filter.
- **intent-run.py becomes a kitchen sink (588 lines today).** — Conformance moved to structure-conform.py (H13), and recon is a port of a small pattern. Past about 900 lines, split into named, whitelisted sibling modules (e.g. intent_run_lint.py, intent_run_findings.py), each covered by `intent-run --self-test`. The wave-3 exit gate names them.
- **Approval and human fields stay self-attestable.** — `approve` is TTY-only and refuses under CI or WS_HOOK. It records approved_via. lint WARNs 'self-approved' when the approval lands in the creation commit. The intent_hash makes silent post-approval drift fail. Human items are USER_REPORTED, never VERIFIED. The residual is stated in the memory decision.
- **Employer-wall leak through recon, specs, packets, verify records, notices or telemetry.** — H2 resolver on two axes with a restrictiveness lattice. The neutral variant plus check-secrets workspace-leak class for anything placed in employer repos. Employer verify records under the git dir. Recon stdout-only for employer and unknown remotes. Notices and COMPLY lines carry counts only. The H15 guard denies default-branch commit, push and merge by agents. Hooks and the installer refuse non-workspace repos.
- **An agent edits context-remotes.json and loosens a wall.** — It is in the SENSITIVE diff class, so the change is flagged in gate output and the commit suffix. The playbook's 'only Sean's explicit sign-off' rule applies. profile_resolve --self-test fixtures pin the lattice semantics.
- **The H15 guard falsely denies a legitimate operation, or misses a command shape.** — 14 days in ask mode before deny. Fails open on its own errors (declared residual, H17-R8 class; triggers held). Branch-to-PR flows are explicitly allowed. Shapes are covered by TestWallGuard fixtures. PR review remains the wall.
- **Compliance measurement is Claude-only (transcripts), so Cursor gets no compliance data.** — Cursor reports an honest SKIP in COMPLY accounting. Cursor commits are still gated and measured through post-commit / pre-push and commit-subject suffixes.
- **Machine locality: the personal repos needed for wave-2 recon and H13 live only on the Personal MBP.** — Those exit criteria are stated as Personal-MBP runs. Work-MBP runs cover the vault dogfood.
- **Tools that walk 07-projects/ or 05-artifacts/ give different results per machine because of untracked employer folders.** — A global rule: every new walker uses `git ls-files` (H1 census, H5 --all, H8 --status, H12 --research), each with a fixture proving an untracked c8_* or employer file is ignored.
- **Template bloat and ceremony on small or exploratory builds.** — Severity scales with lifecycle. The block has a 40-line cap. Pointers and `n/a (reason)` are accepted. No default principles are injected. Single-agent short work still needs only plan-ahead and the Live handoff (#17:26).
- **New Layer-0 keys become hair triggers or collide.** — Multiword keys only. forbid_routes cases. A route-key overlap check (H7) in addition to the skill-trigger ceiling. evaluate-skill-routing --lint.
- **Legacy-spec and legacy-report exemptions become permanent loopholes.** — `lint --report` and `--status` count them against ceilings. At 0 the rule flips to ERROR by a deliberate diff (shadcn-lint baseline precedent).
- **Clean-room drift: new templates echo ZV text.** — A one-shot 8-token n-gram overlap check against the scratch corpus before landing, with the result and idea provenance recorded in the H4 memory decision.
- **Name overload recreates ZV's drift ('stage', 'ledger', 'adopt', 'frame').** — The plan uses `lifecycle:`, 'findings register', 'onboard' and plain headings, plus the one-home tests (template == constant == standard).

## Success metrics

| Metric | How measured | Baseline | Target |
|---|---|---|---|
| HEAD red on registry drift | build-registry --check at HEAD; commit-subject `[gate: …]` suffix in git log; CI | HEAD 22934df: build-registry --check rc=1 (4 stale hashes from 41737cd/8fcb70e); build-related --check rc=0; validate-integrity red only from the uncommitted in-flight _INDEX.md line (re-verified 2026-09-22) | Green at the wave-0 exit. After wave 3, 0 charged-red pushes reaching main per 30 days. |
| Report and decision status contradictions | intent-run.py lint --all (findings rules) + validate-evidence-grades.py --status (git ls-files only) | 3: the A8 memory decision vs figma-bind-probe; the process-rigor-gaps frontmatter vs its line 25; the workspace-automation-review frontmatter superseded only through the companion chain | 0, with snapshot reports unedited |
| Machine entry-point parity defects | workspace-harness.py --connections (check_entry_points) | At least 13: llms.txt 12/14/29; brain.mdc 28-29 and 40; CURSOR.md 23; CLAUDE.md 81; ontology 82; .cursor/agents (6 lines); plus the TRIGGER_WORDS/KNOWLEDGE_HINTS doc sites | 0 |
| Adapter-list definitions | Code review plus the H6 --self-test | 3 independent lists (workspace-harness ADAPTERS, validate-workspace ADAPTER_MD, evaluate-surface-trajectories HOOKLESS_ADAPTERS) | 1 ENTRY_POINTS definition, with the other two derived from it |
| Lifecycle routing | evaluate-skill-routing.py --check; evaluate-surface-trajectories.py --check | Of 5 probes, 2 hit no route, 3 hit only generic routes, and skill-loadset matched nothing for any of them (2026-09-22) | 5 of 5 hit their intended route (audit probes also hit #06), and every forbid case passes |
| Active personal projects with a lint-clean project-intent block | python3 09-tools/intent-run.py lint --all --report | 0 | 3 or more within 30 days of the wave-1 exit |
| Specs done but not closed | The single session-status closure line, backed by intent-run lint --all --notice | At least 1 (19-workspace-brain/docs/INTENT.md: all items checked, status active) | 0 older than 7 days |
| Always-loaded and injected tokens | python3 09-tools/workspace-harness.py --tokens | contract_floor 10,384/11,800; session_floor 15,440/17,000; cursor_floor, hook_injection and trigger-routes.json (about 10k tokens) unpriced | contract_floor ≤ 10,384 (expected to fall after H6); session_floor ≤ 15,440 plus at most about 30 tokens while the closure line fires; all three unpriced items priced; no existing BUDGETS key raised |
| Gate cost and fail-open integrity | The last-gate.json ring via close-out-dispatch.py --telemetry | No gate exists. The fast validator set is about 5.7 s (read-only runs, 2026-09-22). | SessionEnd gate p95 ≤ 20 s; post-commit < 1 s; pre-push with WS_GATE_RESULT ≤ 1 s and without it ≤ 30 s; hook exit 0 in 100% of report-only runs |
| Detector value and false positives | close-out-dispatch.py --telemetry --since 30d | No catch data | Every gated detector has runs, catches and FP counts with machine coverage; FP ≤ 1 per 20 runs before any blocking opt-in; Probation candidates corroborated by commit suffixes or CI |
| Injection-vs-execution compliance and context receipts | ws-audit COMPLY lines in ~/.claude/ws-state/audit.log | Never measured | Measured for every multi-prompt Claude session. A sustained dispatch ratio below 0.5, or receipts below 0.5, becomes a findings-register row. Cursor is an honest SKIP. |
| Wall classification and enforcement | TestProfileResolve, the fork detector, TestWallGuard, and the intent-run no-git-write invariant | Two repo classifiers with hardcoded markers, and no Centric Bitbucket owner in any list. No agent-side guard (PreToolUse covers only use_figma). | 1 resolver over a declared table plus python3-absent fallbacks. 100% of TestWallGuard deny cases denied, and 0 false asks or denies over 14 days of ask mode. 0 intent or recon writes into employer working trees. |
| Out-of-scope or preserve-path writes caught before merge | intent-run.py status scope column and scope exit codes | No detector | Every intent/<slug> branch passes scope before its task shows verified |
| New hubs, foundations or frameworks without rule-of-three, command-surface or 3+-consumer evidence | workspace-harness.py --connections (check_rule_of_three) | No check exists | 0 |
| Spec cycle time (created → first PASS record → closed), informational only | intent-run.py lint --all --report | Not measurable | Reported, never gated |

## Open decisions for Sean

1. Project intent home: a README `## Project intent` block for vault projects and a root PROJECT.md for external personal repos, following AGENTS.md's Project contract, with job specs pointing at it via `intent:`. Recommendation: yes. The rejected alternative (inside the coordination spec) would require amending #17:26, the intent-coordination When-NOT list, the ontology row and AGENTS.md.
2. Are the lifecycle values discover | define | build | operate right for README frontmatter, with WARN at discover and ERROR from define?
3. 00-context-profiles.md step 3 (needs your sign-off): approve reading remotes via the declared context-remotes.json table on two axes (owner vs credential), adding the centricsoftware Bitbucket org, and declaring grants such as 12-MCS's saas-plm-analysis PR+commit+merge grant in that table.
4. Beacon enrollment for snds-owned repos reached through the github-work alias: keep today's fail-safe refusal (credential scope = work), or allow enrollment when the owner is personal? The fixtures assert today's behaviour until you decide.
5. Git identity documentation contradiction: 00-context-profiles.md says 'Personal snds GitHub auth' for personal-solo, but feedback-credential-scoping.md requires the Centric identity for workspace commits on the Work MBP. Approve a doc fix adding a per-machine identity note. No git config change is proposed.
6. IP boundary contradiction: 00-context-profiles.md says personal-solo carries 'No employer material, ever', yet the workspace deliberately tracks Centric context (08-knowledge/engineering/centric-plm-codebase.md; 07-projects/12-MCS/SESSION-STATE.md; the shared-brain rationale in feedback-credential-scoping.md). Declare the sanctioned exception in the playbook, or ask for a vault-side check?
7. H15 wall guard: approve adding it to the user-global settings fragment, which the doctor then installs on every machine. It starts in ask mode for 14 days, then flips to deny for employer default-branch commit, push and self-merge.
8. Blocking after wave-2 telemetry: will you opt individual machines in with `workspace-doctor.sh --install-git-hooks --blocking` (charged regressions only; WS_PUSH_GATE=off kill switch; bypass needs a reason)? Also, should hooks extend to beacon-enrolled personal repos (ShadeGraph, LCARS)?
9. Approval authenticity: accept TTY-only `approve --by` plus intent_hash, where agent self-approval is hard but not impossible, or require an out-of-band approval (a PR review, a signed tag) before implementors start? For employer repos, is only `approved via PR 12` accepted?
10. Remediation dogfood: migrate A1–A10, R1–R3, R1–R16 and load-miss 1–15 into 07-projects/19-workspace-brain/docs/INTENT-remediation-2026-09.md now (recommended), or grandfather them under the --status ceiling?
11. Budgets: set hook_injection (proposed about 2,500 tokens, from the measured card plus headroom), and decide whether cursor_floor shares the 11,800 contract budget.
12. dc-research.yaml leaves measurement empty on purpose ('not a scanner'). May the H12 structural lane (IDs, refs, #04 labels, decision-rule dates, participant pseudonyms) be named research L3, or should it stay an unnamed hygiene lane?
13. ds-advisor's DDR Context-Quality vocabulary (Confirmed/Inferred/Undocumented/Conflicted) sits beside the #04 labels. Map it to #04 in ds-advisor, or leave it domain-specific?
14. Should every project whose spec or intent block is linted also require a 'Context profile' line in SESSION-STATE.md? 6 of 13 lack one, all untracked.
15. H13 structure-conform and H12 research records are demand-triggered. Confirm that neither ships until a real personal-repo consumer exists.
16. Grandfather all current hubs, foundations and frameworks in rule-of-three.baseline.json, so the H14 check applies only to new mints?
17. The 16-CDS Figma remediation plan (employer, untracked, draft since 2026-05-04): was it executed, abandoned or superseded? Any findings register for it stays in the employer repo or in gitignored c8_* paths.
18. The ZV knowledge note links to 07-projects/19-workspace-brain/notes/zero-vector-harness-plan_2026-09-22.md, which does not exist. Write that plan note or repoint the link as part of the ZV session's own close-out; the wave-0 heal commit deliberately excludes it.
19. /optimize is Claude-only (it lives under .claude/skills). Queue a separate self-improve task to give it a portable 03-skills home?

## Revision log (objections not fully applied)

- **partially-applied** — Skeptic, H3 upheld: optional shared frontmatter helper, since build-registry, intent-run and vault-health each hand-roll a parser → Extraction is deferred on purpose. The three parsers are seeded as H14 rule-of-three instance rows, so the helper is built on logged evidence rather than inside H3.
- **partially-applied** — Skeptic, H10 weakened: a third path→validator table; ignores touch-lists; a second telemetry store beside ws-audit → Applied: DIFF_CLASSES references QUALITY_CHAIN step names with a two-way --check; attribution is seeded from touch-lists and claims; compliance comes from ws-audit's transcript scan as a COMPLY line; gate-log.jsonl is dropped in favour of a last-gate.json ring. Not applied: generating the workflow YAML path lists, deferred because --check already asserts coverage.
- **rejected** — Missing: reverse-direction wall (employer-derived content tracked in the vault) → Tracking that content is currently sanctioned by the shared-brain rationale in feedback-credential-scoping.md, which contradicts the playbook's IP-boundary row. Building a scanner before Sean resolves that contradiction would encode a guess, so it is raised as an open decision.
- **rejected** — Missing: /optimize is Claude-only (portable-first gap) → It is a real gap but unrelated to the ZV closure harness. It is listed as an open decision for a separate self-improve task.

## Workspace defects verified during design (read-only, 2026-09-22)

Each claim was checked against the files by an independent verifier. The load-bearing ones (X1, D7) were also re-run by hand.

### D1 — confirmed · medium

The SessionEnd self-heal in .claude/hooks/dispatcher.py runs build-registry.py but not build-related.py first, which breaks the documented order.

**Evidence.** dispatcher.py:1658-1671 handle_session_end runs only 09-tools/build-registry.py, only when `git status -- 03-skills` shows a SKILL.md change, and with no timeout. It never runs build-related.py or build-trigger-routes.py. AGENTS.md:461 and :470-473 fix the order as build-related → build-registry → build-trigger-routes ('Order matters'); 01-frameworks/08-workspace-contribution-framework.md:55-66 says the same. Live corroboration: the self-heal exists only in the Claude hook, so other surfaces bypass it. HEAD is currently drifted: `build-registry.py --check` exits 1, with hash drift for ds-advisor, eng-foundations, fe-component-architecture and plan-ahead. Commits 41737cd (2026-09-21) and 8fcb70e (2026-09-22) edited those SKILL.md files without regenerating the registry. The same session-end path also commits and pushes without running any validator (dispatcher.py:1680-1689).

**Smallest fix.** In handle_session_end, replace the single builder call with the chain build-registry → build-related → build-registry → build-trigger-routes (see D2 for the fixpoint), each with a timeout that fits the 60s SessionEnd budget. For portability, put the same sequence in one 09-tools entrypoint, for example a `nightly.py rebuild` lane already ordered this way (nightly.py:57-59). Have close-out and self-improve call that entrypoint so Cursor-authored commits also regenerate.

### D2 — confirmed · medium

build-related.py builds Related blocks from the committed registry, so a registry→related→registry fixpoint is needed when frontmatter edges change.

**Evidence.** The docstring at build-related.py:13 says 'Reads `03-skills/skills.registry.json` (run build-registry.py first)'. REG is set at :27, and main() loads it at :119 (`reg = json.loads(REG.read_text())`), then derives every block from reg['skills'] edges (:34-60). One correction to the claim: it reads the ON-DISK registry file, not specifically the committed one. build-registry.py:158-159 and :185 store a sha256 of the whole SKILL.md, so the Related-block rewrite changes the hash. The coupling therefore runs both ways: registry edges feed Related, and Related bytes feed the registry hash. AGENTS.md:461/470 and framework 08:55-66 prescribe related → registry only. Framework 08:62-63 wrongly asserts 'The coupling is one-directional … so ordering alone closes it.' The docstring's 'run build-registry.py first' contradicts AGENTS.md. When an edge changes, following AGENTS.md produces Related blocks from the stale graph, and link-validator.yml:24 (`build-related.py --check`) then fails.

**Smallest fix.** Document and script the order build-registry → build-related → build-registry (or loop until build-related writes 0 files). Update AGENTS.md:461/470-473, framework 08:55-66 (delete the 'one-directional' sentence), the build-related.py:13 docstring, skill-placement Step 5, close-out:107, self-improve:43 and nightly.py:57-58 together, so there is one order everywhere.

### D3 — confirmed · medium

dispatcher.py contains dead forked matcher code, and the one-matcher guard in evaluate-surface-trajectories.py scans only the first ~3000 chars of handle_user_prompt.

**Evidence.** handle_user_prompt (dispatcher.py:1317-1345) only imports prompt_route and calls route_prompt. The following have no callers anywhere in the repo (grep over *.py): TRIGGER_WORDS (:84-101), the hard-coded KNOWLEDGE_HINTS dict (:106-128), _term_matches (:1112), _registry_trigger_hits (:1119), _knowledge_index_hits (:1150), TIER_CAPS (:1186), LEXICAL_FALLBACK_MIN (:1196), _hint_target_key/_HINT_TARGET_RE (:1203-1208), LexicalFallback/_lexical_fallback/_lexical_fallback_hits (:1227-1290) and _followthrough_lines (:1293). The session-start checks _check_audit_staleness (:449), _check_harness_map_staleness (:486) and _check_skill_routing_harness (:512) are also defined but never called. The guard at evaluate-surface-trajectories.py:168-189 takes `text[start:start + 3000]` from `def handle_user_prompt` (:180) and greps only for the literals '_registry_trigger_hits(' and 'TIER_CAPS[' (:185). The function is 1,195 chars today, so the window covers it (it ends at dispatcher line 1368). The real blind spots are twofold. First, the whole dead fork above the function is never scanned. Second, the guard is bypassed by indirection (a helper that calls the forked code) or by growth past 3000 chars. The self-test (:257) asserts only that the guard passes on the live file. There is no negative fixture proving it can fail.

**Smallest fix.** Remove the dead matcher block (lines 84-128 and 1112-1315 minus _refresh_vault_retrieve_index) and the three uncalled _check_* functions. Git history is the provenance, and one ARCHIVE-LOG line records it. Change check_one_matcher to scan the whole module, failing on any `def _registry_trigger_hits`, `def _knowledge_index_hits`, `TIER_CAPS =` or `KNOWLEDGE_HINTS = {`. Add a planted-fork negative fixture to its self_test and to test-validators.py.

### D4 — confirmed · medium

CI workflow path filters omit .claude/hooks/**, 00-bootstrap/**, 09-tools/intent-run.py, build-trigger-routes.py, compact-sessions.py and cursor-prompt-route.py.

**Evidence.** The paths blocks were read in all 5 workflows: capability-validator.yml:9-23, link-validator.yml:9-13, registry-drift.yml:9-13, validator-fixtures.yml:8-40 and workspace-integrity.yml:12-73. None lists .claude/**, 09-tools/intent-run.py, 09-tools/build-trigger-routes.py, 09-tools/compact-sessions.py or 09-tools/cursor-prompt-route.py. All four tools exist in 09-tools/. Nuance: workspace-integrity's `**/*.md` filter does catch 00-bootstrap/*.md, but not 00-bootstrap/beacon-enroll.sh, setup/setup.py, doctor/linear-lanes.py or the manifests. Concrete consequence: a PR that edits only .claude/hooks/dispatcher.py triggers no workflow, so the one-matcher guard (evaluate-surface-trajectories --check, workspace-integrity.yml:112) never runs on the file it guards. No workflow has a schedule or workflow_dispatch fallback. No CI step runs intent-run.py or compact-sessions.py at all.

**Smallest fix.** Add ".claude/hooks/**", "00-bootstrap/**", "09-tools/*.py" (or at least the four named tools) and ".cursor/rules/**" to workspace-integrity.yml push and pull_request paths. Optionally add a weekly `schedule:` so path gaps cannot hide drift indefinitely.

### D5 — confirmed · medium

No CI workflow runs build-trigger-routes.py --check.

**Evidence.** `grep run:` across .github/workflows/*.yml shows no build-trigger-routes step. The only chain that includes it is workspace-harness QUALITY_CHAIN (workspace-harness.py:74). CI invokes the harness only as `--connections --tokens` (workspace-integrity.yml:108), and the quality lane runs only with --quality or no flags (workspace-harness.py:837-840). So the chain entry never executes in CI. The tool's own docstring claims 'CI: fail on drift' (build-trigger-routes.py:11). No other validator references trigger-routes.md (grep over 09-tools/*.py: only build-trigger-routes, nightly and workspace-harness). Current state: `build-trigger-routes.py --check` prints 'trigger-routes.md OK', so there is no live drift today, only no gate. llms.txt:14 points non-Claude agents at this generated file, so silent drift misroutes them.

**Smallest fix.** Add a step `python3 09-tools/build-trigger-routes.py --check` to workspace-integrity.yml, next to validate-layer0-schema. Add 09-tools/build-trigger-routes.py and 02-shared-references/trigger-routes.md to its path filters.

### D6 — confirmed · medium

The 09-tools/intent-run.py approval gate accepts any frontmatter string starting with 'approved' or 'waived', so approval is self-attestable.

**Evidence.** intent-run.py:122-124 `approval_ok`: `a = (meta.get('approval') or '').strip().lower(); return a.startswith('approved') or a.startswith('waived')`. This gates cmd_gate (:330-349), task_status for T0/coordinator (:141) and implementors (:149), and the worktree exit code (:327). There is no check of approver identity, date, reason or commit authorship. The template 00-bootstrap/templates/intent-spec.md:8 documents `pending | approved YYYY-MM-DD by Sean | waived (reason)`, but the parser does not enforce that shape. A bare 'approved', 'approvedx' or 'waived' with no reason all pass. Any agent that can edit the spec frontmatter can unblock implementors, even though #17:91 names 'Starting implementors before spec approval' as a failure. The ws-method.json map records the same finding.

**Smallest fix.** Make approval_ok require the template grammar: regex `^approved \d{4}-\d{2}-\d{2} by \S+` or `^waived \(.+\)`. Have `gate` echo the approver and date. Add a negative fixture in test-validators.py for bare 'approved' and reasonless 'waived'. Optionally have `gate` report whether the commit that last changed the approval line carries an agent Co-Authored-By trailer. This is advisory only, so there is no identity system to build.

### D7 — confirmed · high

The llms.txt 'Start here' list includes skills.registry.json and/or trigger-routes.md, which AGENTS.md bans ingesting.

**Evidence.** The 'Start here (read in order)' list in llms.txt:9-17 includes item 2, `[skills.registry.json](03-skills/skills.registry.json)` (:12-13), and item 3, `[trigger-routes.md](02-shared-references/trigger-routes.md)` (:14-15). AGENTS.md:104 makes llms.txt read-order step #1, and AGENTS.md:107 says 'Do **not** ingest `03-skills/skills.registry.json` (~55k tokens)'. AGENTS.md:110-111 says 'Do not ingest the generated trigger-routes.md', and AGENTS.md:230 repeats the ban. Sizes: skills.registry.json is 246,554 bytes (~62k tokens by the bytes/4 convention) and trigger-routes.md is 62,929 bytes (~16k). llms.txt:25-26 also tells agents to match triggers themselves instead of pointing them at `skill-loadset.py` in the start list (it appears only under Generate/validate at :55). The contract_floor budget (workspace-harness.py:490) counts llms.txt bytes but does not follow its 'read in order' links, so the harness cannot see this ~78k-token trap. Hookless surfaces (Perplexity, ChatGPT, Gemini) follow llms.txt literally.

**Smallest fix.** Replace llms.txt:12-15 with `python3 09-tools/skill-loadset.py "<utterance>"` (query, never ingest) and `trigger-routes.json` (curated, small), each with an explicit 'do not ingest skills.registry.json / trigger-routes.md' note. Add a check (in validate-layer0-schema or workspace-harness connections) that fails when any ingest-banned file is linked from llms.txt's Start-here section. Add a negative fixture.

### D8 — confirmed · medium

The SessionStart hook timeout in .claude/settings.json is smaller than the sum of the serial subprocess timeouts the dispatcher allows.

**Evidence.** .claude/settings.json:11 sets SessionStart `timeout: 30`. On a startup source, handle_session_start (dispatcher.py:1086-1110) runs these serially. compact-sessions.py has timeout=20 (:731). vault-retrieve.py --rebuild has timeout=60 (:1221). Then build_session_start_context runs `claude --version` with timeout=5 (:407), linear-lanes.py with timeout=5 (:699) and session-status.py with timeout=8 (:867). That totals 98s of allowed subprocess time against a 30s kill. ensure_local_gitdir and _cleanup_stale_worktrees also make git() calls with no timeout at all (git helper :169-175). emit_context runs only once, at the end (:1104-1110). If the harness kills the hook at 30s, the entire injection (ritual card, log head, pending) is lost rather than degraded, so the hook is fail-closed on context despite the per-step try/except. Inference: typical runs likely finish well under 30s, because the rebuild is probably incremental. The overrun case is a cold or large index or a slow git on a Drive-backed checkout.

**Smallest fix.** Launch the vault-retrieve rebuild detached (subprocess.Popen with start_new_session=True, no wait), or move it after emit_context. Add a monotonic deadline (e.g. 22s) in handle_session_start that skips remaining optional steps (version check, linear lanes) once exceeded. Give git() a default timeout.

### D9 — confirmed · low

session-status.py warns only when the skill-routing stamp is MISSING, not when it is stale (graph hash changed).

**Evidence.** session-status.py:264-268: `if not ROUTING_STAMP.is_file(): out.append('Skill-routing harness stamp missing …')`. There is no hash or result comparison. The stamp (07-projects/19-workspace-brain/reports/skill-routing-harness.stamp) carries `hash: 2c6a9e6d10acbb7d` and `result: pass`. evaluate-skill-routing.py already implements `--stale` (:315, :332-342: exits 1 on hash mismatch or result != pass), and its docstring (:19) promises a check 'at session start, if the stamp is missing or the graph hash changed'. The dispatcher function that did this (_check_skill_routing_harness, dispatcher.py:512-553) is never called, so this is a regression from the port to session-status. Live evidence: `evaluate-skill-routing.py --stale` right now prints 'skill-routing harness stale (stamp 2c6a9e6d10acbb7d vs 16aa09a7f679a7de)' and exits 1, while the session card is silent. CI does run `evaluate-skill-routing.py --check` (workspace-integrity.yml:92), which limits the impact.

**Smallest fix.** In session-status._notices, replace the is_file check with an import of evaluate-skill-routing's read_stamp() and graph_hash(), or a subprocess `--stale` call with a ≤3s timeout. Emit 'routing stamp stale' on hash mismatch and 'routing corpus last failed' on result != pass. Extend `session-status.py --check` or add a fixture for the stale case.

### D10 — confirmed · medium

.claude/skills/new-project/SKILL.md tells the agent to edit a TRIGGER_WORDS dict in dispatcher.py, which is now derived from trigger-routes.json.

**Evidence.** new-project/SKILL.md:80-83 ('Step 6 — Register trigger words … add them to the `TRIGGER_WORDS` dict in `.claude/hooks/dispatcher.py`'). dispatcher.py:84-101 builds TRIGGER_WORDS from 02-shared-references/trigger-routes.json, and nothing reads it (see D3). Routing now lives only in 09-tools/prompt_route.py. The same stale instruction appears in 00-bootstrap/templates/project-readme.md:19 ('Edit .claude/hooks/dispatcher.py TRIGGER_WORDS'), in 08-knowledge/_README.md:128-130 (add to dispatcher `KNOWLEDGE_HINTS`, now a dead dict superseded by knowledge-hints.json) and in 02-shared-references/delivery-playbooks/README.md:88. An agent that follows any of these writes to dead code, and the route silently never fires on any surface.

**Smallest fix.** Repoint all four lines to 'add a row to 02-shared-references/trigger-routes.json (skills) or knowledge-hints.json (knowledge), run build-trigger-routes.py, and add a case to skill-routing-cases.jsonl / surface-trajectory-cases.jsonl'. Add a validate-integrity smell that flags 'TRIGGER_WORDS' or 'KNOWLEDGE_HINTS' in live (non-archive, non-log) markdown.

### D11 — confirmed · low

00-bootstrap/beacon-enroll.sh classify() would treat a personal snds/* repo cloned via the github-work SSH alias as employer.

**Evidence.** beacon-enroll.sh:38-46: the first arm, `*github.com[:/]snds/*`, requires the literal host 'github.com'. The next arm, `*github-work*|…`, then returns 'employer'. A personal remote cloned through the work SSH alias fails the personal arm and matches the employer arm. The workspace itself is exempt (sweep skips $WS at :87). For other repos, `--sweep --apply` permanently records them in beacon-repos.ignore.txt (:95-96), and single-repo mode refuses even with `--personal`, because the employer arm exits before FORCE is read (:109). The authoritative rule keys on OWNER, not host alias: 00-context-profiles.md:28-29 says '`github.com/snds/*` → personal. `cpes-software/*` … → Centric'. The error direction is fail-safe (over-restrictive), so no wall is breached. The cost is lost beacon coverage for personal repos on work machines.

**Smallest fix.** Change the personal arm to `*github.com[:/]snds/*|*github-work:snds/*|*github-work/snds/*)` (owner-keyed, and checked before the github-work employer arm), keeping `*c8*` and `cpes-software` as employer. Add a tiny shell self-test (or a test-validators.py case that sources classify) covering github-work:snds → personal and github-work:cpes-software → employer.

### D12 — confirmed · medium

Some 07-projects/*/SESSION-STATE.md files lack a Context profile line, including employer projects.

**Evidence.** 6 of the 12 SESSION-STATE.md files have no 'Context profile' line (grep -i). (1) 07-projects/02-centricPLM: employer. Line 12 says 'Do not auto-commit employer repos' but declares no profile. (2) 07-projects/09-figma-repo-sync-plugin: employer. Line 9 puts the code in ~/Projects/cpes-software/centric-ui. (3) 07-projects/10-centric-UX-research: employer. (4) 07-projects/13-legion: personal (inferred from beacon-repos.txt listing Legion). (5) 07-projects/14-variable-icon-font-generator: CentricSymbols, employer-adjacent (inferred). (6) 07-projects/16-CDS Figma-Code Audit: employer. Line 13 audits ~/projects/c8-plm/CDS. Present in 00, 12, 18, 19, 20, 21 and 22. Another 13 project dirs have no SESSION-STATE.md at all, including 05-C8-PLM, 11-lexical-react-native and '17-data table' (employer by name; inferred). The template carries the field (01-frameworks/_session-state-template.md:47), but no validator checks it: grep 'Context profile' over 09-tools/*.py finds only a README mention. The fallback to a git remote exists (00-context-profiles.md:28-29) but is itself ambiguous under the github-work alias (see D11).

**Smallest fix.** Add a `- **Context profile**:` line to the 6 files (centric-engineering or centric-design for 02/09/10/16, personal-solo for 13, and ask Sean about 14). Add a check to validate-integrity.py (or `session-status.py --check`) requiring every 07-projects/*/SESSION-STATE.md to declare one of the profile ids in 00-context-profiles.md. Add a negative fixture in test-validators.py.

### D13 — confirmed · low

03-skills/github-guardrails/SKILL.md keeps dismissal state in agent-local ~/.claude/.../memory, against externalize-everything.

**Evidence.** github-guardrails/SKILL.md:71-78 ('Dismissed state is stored at: ~/.claude/projects/-Users-sean-sands-projects-cpes-software/memory/github-guardrails.json', with the format `{dismissed:[…], last_reset}`), repeated at :490-497 ('Claude reads the state file before each guarded operation'). That path is Claude Code's private per-project memory on one machine. It is invisible to Cursor or other surfaces and to the other MBP, which violates AGENTS.md:48 ('Externalize everything; keep nothing durable in private memory … Claude Code's `.claude` memory') and portable-first. The skill is tier cross-cutting with triggers such as 'force push' and 'open a pull request', so it fires on every surface. On any surface but the one that recorded a dismissal, dismissals diverge: interrupts re-fire or are silently skipped.

**Smallest fix.** Move the dismissal list into the workspace at a file that is never auto-loaded, such as 04-preferences/github-guardrails-dismissals.json. Dismissal is an explicit user signal, which matches the 04-preferences routing rule in workspace-ontology.md:84. Update SKILL.md:71-78 and :490-497 to read and write it. No employer content is involved: the file holds only GUARD ids.

### D14 — confirmed · low

HOSTNAME_MAP is duplicated in dispatcher.py and session-status.py with divergent labels, and still lists a retired Windows host.

**Evidence.** dispatcher.py:69-75 and 09-tools/session-status.py:29-35 both define HOSTNAME_MAP, as does a third copy in 00-bootstrap/setup/setup.py:40-46. A fourth, prose copy is in .cursor/rules/brain.mdc:39-40, plus the CLAUDE.md:93-94 table that CRITICAL_FACTS.md:37 names as canonical. Divergence: CS-K746DRWXY1 maps to 'Work MacBook Pro (main, going forward)' in dispatcher and setup but 'Work MacBook Pro' in session-status. Every code copy still has `"Enterprise": "Windows Desktop"`, and brain.mdc:40 has '`Enterprise`→Windows', although CLAUDE.md:94 says 'Fleet is macOS-only; Windows retired 2026-09-15'. Session-log attribution (Agent · Surface · Machine) therefore depends on which surface wrote it. brain.mdc is alwaysApply, so the retired row is a recurring token cost.

**Smallest fix.** Make session-status.py's map the single code source and have dispatcher.py and setup.py import or read it, as dispatcher already shells out to session-status. Drop the Enterprise row everywhere, including brain.mdc:40, and pick one CS-K746DRWXY1 label. Optionally add a harness connection check that the CLAUDE.md table and the code map agree.

### D15 — confirmed · medium

03-skills/skill-placement/SKILL.md never references 01-frameworks/13-domain-rigor-stack.md.

**Evidence.** grep -i '13-domain|domain-rigor|domain rigor|#13|rigor' over the whole 49-line 03-skills/skill-placement/SKILL.md returns nothing. Its frontmatter has no governed_by or related edge, and its Related block is only 'peer ↔ [[workspace-bootstrap]]' (:48-49). It owns the triggers 'create a skill / generate skill / make a skill / new skill' (:10). Running prompt_route.route_prompt('create a skill for onboarding repos') and skill-loadset.py on the same utterance loads only 03-skills/skill-placement/SKILL.md, with no #13. AGENTS.md:188 says 'Native "create a skill" flows that skip this checklist are insufficient — follow #13's authoring algorithm', and 13-domain-rigor-stack.md:115 says the same. The only Layer-0 path into skill creation therefore skips the L1-L5 checklist.

**Smallest fix.** Add a step 0 to skill-placement: 'Hub, spoke, addendum or command surface → load 01-frameworks/13-domain-rigor-stack.md and complete its authoring checklist (L1-L5) before step 3'. Add a trigger-routes.json row mapping 'create a skill' to skill-placement plus #13. Add a skill-routing-cases.jsonl case that expects 01-frameworks/13-domain-rigor-stack.md for 'create a skill'.

### D16 — confirmed · medium

The #13 rule 'every hub declares prerequisites' is not machine-enforced by build-registry.py or validate-links.py.

**Evidence.** The rule is stated at 13-domain-rigor-stack.md:54 ('No orphan hubs. Every `tier: hub` declares `prerequisites` (usually a `*-foundations`)') and in the checklist at :89. build-registry.py validate() (:200-226) checks only dangling prerequisite, hub or governed_by references, a missing tier (warning) and hub or foundation without triggers (error). validate-links.py (:105-121) checks Related reciprocity and warns only on design/eng spokes without a foundation. workspace-harness check_hub_edges (:258-290) checks existence and chain order only. Live count from the registry: 9 of 47 tier:hub skills have empty prerequisites: google-fonts-scraper, google-fonts-web-scraping, job-search-strategist, material-symbols-project, omni-project, python-cross-platform-gui, realtime-visual-craft, svg-font-extraction and variable-icon-font-architect. Inference: some of these are project hubs where 'usually a foundation' may legitimately not apply, but no exemption mechanism exists either.

**Smallest fix.** In build-registry.py validate(), emit a warning, promotable to an error, for `tier == 'hub' and not prerequisites` unless the frontmatter carries an explicit exemption. Reuse an existing field, e.g. `prerequisites: []` plus a `rigor_exempt:` reason, rather than a new dialect. Add a negative fixture in test-validators.py. Triage the 9 current hubs.

### D17 — confirmed · medium

/optimize exists only under .claude/skills, with no portable 03-skills equivalent.

**Evidence.** The full protocol is .claude/skills/optimize/SKILL.md (220 lines), and 03-skills/optimize does not exist. By contrast, .claude/skills/harness-map (14 lines) and mission-fit (15 lines) are thin wrappers over 03-skills homes. The portable session card nonetheless tells every surface to 'Run `/optimize`' / 'Propose `/optimize` this session' (session-status.py:253, :257), and framework 08:81 says to run vault-health 'inside `/optimize`'. trigger-routes.json:114 routes 'maintenance loop' to the .claude path, so the file is readable but has no frontmatter triggers in the registry, no load chain and no close-out row. The gap is broader than the claim: framework-check, health, new-project, reconcile, session-end (367 lines) and today also exist only under .claude/skills with no 03-skills directory. Session-end is partly covered by the portable doctrine in framework 08 §'Portable session protocol' (:242).

**Smallest fix.** Create 03-skills/optimize/SKILL.md (frontmatter triggers such as 'audit the brain', 'workflow audit', 'maintenance loop') holding the protocol. Reduce .claude/skills/optimize/SKILL.md to the harness-map-style pointer, which keeps the file, so there is no rename. Repoint trigger-routes.json:114 and regenerate the registry and trigger routes. Queue the same treatment for health, framework-check and new-project.

### D18 — confirmed · low

01-frameworks/team-practices-and-decisions.md says 'seventeen frameworks' while 00-README.md lists eighteen, and 00-bootstrap/templates/project-readme.md lists only frameworks 01-05.

**Evidence.** team-practices-and-decisions.md:9 ('Unlike the seventeen frameworks') and :222 ('## Integration with the seventeen frameworks'). 01-frameworks/00-README.md:6, :8, :12 and :361 say 'eighteen', and the table at :16-33 lists #01-#18. project-readme.md:6 has frontmatter `frameworks: [aesthetic-lens, ui-ux-operational, collaboration-critique, research-evidence, last-mile-craft]`, and :22-27 lists only 01-05, omitting #06 QA, which CLAUDE.md marks 'always-load before audit/review'. The same template also carries the stale TRIGGER_WORDS instruction at :19 (D10). Broader drift: .claude/skills/framework-check/SKILL.md:3, :31 and :116 say 'eleven' operating frameworks.

**Smallest fix.** Replace hard-coded counts with a count-free phrase ('the frameworks in 00-README') in team-practices:9/:222 and framework-check:3/:31/:116. In project-readme.md, replace the 01-05 list with a pointer to 00-README plus #06. Optionally add a validate-integrity smell that fails when a spelled-out framework count disagrees with the number of NN-*.md files in 01-frameworks.

### X1 — confirmed · medium

(New, found while verifying D1/D9) The committed registry at HEAD is drifted, and the skill-routing stamp is stale.

**Evidence.** `python3 09-tools/build-registry.py --check` exits 1 ('skills.registry.json is out of date'), and the working tree has no SKILL.md changes (git status shows only 08-knowledge edits). A hash comparison shows drift in ds-advisor, eng-foundations, fe-component-architecture and plan-ahead, all edited by commits 41737cd (2026-09-21) and 8fcb70e (2026-09-22), neither of which touched skills.registry.json (last registry commit f6090f9, 2026-09-16). `evaluate-skill-routing.py --stale` exits 1 (stamp 2c6a9e6d10acbb7d vs current 16aa09a7f679a7de). Inference: these 'learn:' commits came from a non-Claude-hook path (session subjects cite Work MacBook Pro / Cursor), which has no registry self-heal. registry-drift.yml should have failed on push; the CI result was not checked because no network was used.

**Smallest fix.** Run build-registry → build-related → build-registry → build-trigger-routes → evaluate-skill-routing, which also rewrites the stamp. Commit. Then land the D1/D2 fix so the regeneration runs from a surface-neutral entrypoint that close-out and self-improve invoke, not only from the Claude SessionEnd hook.

X1 was healed in commit `6cac460`: the registry was regenerated in fixpoint order and the routing stamp refreshed (49/49).
