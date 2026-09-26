---
title: Living intent spec
spec_version: "1.0"
status: canonical
---

# Living intent spec

The coordination artifact for [[17-intent-coordination-operating-model]]. Copy
[00-bootstrap/templates/intent-spec.md](../00-bootstrap/templates/intent-spec.md) into the
**owning** project or repo (`docs/INTENT.md` or `docs/INTENT-<wave>.md`). Do not put the body
in a Linear issue ([[open-agent-engine]] stays pointer-shaped).

The spec is **living**: agents update checklist status, wave notes, and the changelog when
reality changes. Designed intent (outcome + northstar) changes only with Sean's approval.

## Required sections

1. **Outcome** — what should exist, and where (no use of *done* / *complete* as the definition).
2. **Context profile** + **lane** (if movement is tracked).
3. **Northstar** — Figma, `NORTHSTAR.md`, contract, or quoted user intent. Pointers, not a paste of the whole file.
4. **Fidelity / acceptance checklist** — checkable items; name the measurement (`vqa prove`, test command, validator, review).
5. **Task graph** — id, role (`coordinator` / `implementor` / `verifier`), `depends_on`, isolation, specialist skill.
6. **Waves** — what may run in parallel; what is held.
7. **Evidence** — per task, what the verifier will read. Author chat is never sufficient for consequential work.
8. **Open decisions / blocked-on**
9. **Changelog** — date, who, what changed in the plan.

## Grammar (read by `09-tools/intent-run.py`)

- **Frontmatter.** `#` starts a comment only after whitespace and outside quotes; quote the whole
  value to keep a `#`. Stripped comments are recorded.
- **Approval.** `approved YYYY-MM-DD by <name>[ <note without #>]`, `approved via PR <n>`, or
  `waived (<reason>)`. The gate opens on any value starting `approved` or `waived`; an approval
  that lost `#<n>` to a comment is a lint ERROR.
- **Checklist.** `- [ ] <label> -- measure: <command>`. A measure ends at the next ` -- <key>:`
  (for example `-- signal:`). A `human:` measure never executes; `verify` reports it as HUMAN, or
  HUMAN-ATTESTED when ticked, and never as PASS.
- **Tables.** Write `\|` for a literal pipe inside a cell.
- **Task graph `writes`.** Comma-separated at bracket depth 0: paths and globs (`*`, `**`,
  `{a,b}`), `path.json[key.path, …]` selectors (`*` matches every list element by `id`, or every
  key), `@Tn` for another task's writes, or `none`.
- **`verify --run [--root DIR]`.** Measures run through `shlex` with `shell=False`. The cwd is DIR,
  else the process cwd's git toplevel when the spec is outside it or ignored by it, else the spec's
  own toplevel. In an automated context (CI, any agent, no TTY) only `python3 <git-tracked
  09-tools/*.py>` without shell metacharacters runs; anything else is NOT_EXPOSED. Exit 1 on FAIL
  or SKIP, 2 on NOT_EXPOSED only, else 0.
- **Project intent (`<repo>/PROJECT.md`, H4).** Frontmatter: `lifecycle:` discover | define | build |
  operate; `profile:` in personal repos only and tighten-only (the context table is authoritative);
  optional `inherits: <owner>/<repo>[#path][@ref]` and `inherits_context: <slug>#AGENTS.md[, vault:<id>]`;
  optional `approval:` (grammar above). Body `## Project intent`, ≤40 lines: `### Problem & audience`,
  `### Knowns & unknowns` (table `claim | label | tier | evidence | decision rule`; labels known,
  inferred, assumed, unknown, conflicted; tiers T1–T5; the rule is written before the evidence),
  `### Out of scope & later`. `n/a (reason)` and `[HUMAN: …]` markers are allowed; markers and missing
  rules WARN at discover and ERROR from define on. The repo's `AGENTS.md` (and `AGENTS.override.md`)
  carries `Project intent: PROJECT.md`. Vault-only projects use the same block in their README. Frame
  with `init --frame --repo DIR`; employer repos get the `--neutral` render by PR only.
- **`lint` / `approve` / `next` / `verify --record` (H5).** Inheritance stays within one owner class
  (checked from the table before any read). An approval whose introducing commit (`git log -S`)
  carries an agent trailer is BLOCKED; with no trailer lane it WARNs "provenance unknown". Employer
  intent and specs accept only `approved via PR <n>`. Records: `<spec>.verify.jsonl` (workspace,
  `merge=union`); employer records hold counts, ids and hashes under
  `~/.config/snds-workspace/state/telemetry/<slug>/`, never in the repo.
- **Remediation specs (H8, `kind: remediation`).** Template:
  [intent-remediation.md](../00-bootstrap/templates/intent-remediation.md). `## Recon` holds the
  `<!-- intent:recon:start -->` block that `init --recon --repo DIR [--spec PATH]` regenerates (read-only;
  content-read policy first, so a Claude chain on a non-personal repo is routed; employer recon goes to
  stdout; the card stores a count of secret-shaped names, never the names). `## Findings` is the findings
  register: `id | sev | status | origin | observed | expected | evidence | closure | closed_by | revisit`
  (+ optional `risk` low|medium|high). Ids `F-NNN`, never reused; sev Critical|High|Medium|Low (a11y
  blocker|major|minor|nit map 1:1); status OPEN|RESOLVED|DEFERRED; origin `<report-slug>#<ID>`, `recon` or
  `external`; closure is a `C-NNN` into `### Closures` (`- C-001: measure: <cmd>` or `judgment: <who>`),
  never a command in a cell. RESOLVED needs closure + closed_by; DEFERRED needs closed_by (the reason) +
  revisit (a date or `on: <trigger>`). `## Preserve` is `glob | why | until`. `## Packets` holds one
  `### T<n> — title` per implementor with `- outcome/context/findings/acceptance/last verified state/
  non-goals/verification/rollback/bail point/previous attempts:` fields. Lint refuses `status: closed`
  with an OPEN row, an implementor without a packet, a preserve row without `until`, an unresolved
  `blocked_by:`, and (`--since REF`) a finding that vanished; `--run-closures` marks a failing RESOLVED
  closure REGRESSED. `packet --format prompt T<n>|F-NNN` prints a self-contained brief for any agent;
  `verdict [--branch B | --range A..B] [--run]` is the mission-fit verdict (Fit / Fit with gaps exit 0,
  Unfit 1, Blocked 2: a High or Critical closure that did not run is Blocked, never a plausible Fit);
  `gate` refuses while a `blocked_by` upstream is Unfit or Blocked; `ready` / `worktree add` hold a task
  with 3 FAIL verify records since its newest Previous attempts entry. Dated reports are never edited:
  `validate-evidence-grades.py --status` flags one whose status claims closure that no register row cites.
- **Write scope (H9, kernel `09-tools/intent_scope.py`).** `writes` and `forbids` share the `writes`
  grammar; a literal path covers what is under it; a token with whitespace is prose (a prose `writes`
  cell is not machine-checkable; prose `forbids` contribute their backticked paths). Optional `enforce`
  column (`true`) and frontmatter `generated:` (globs allowed anywhere) and `contract:` (paths).
  `lint` / `gate` ERROR on two implementors of one wave (a `wave` cell, else dependency depth; neither
  depends on the other; not verified) whose writes intersect, and on a verifier that declares writes.
  `ready` releases a second parallel implementor only when every `contract:` path is committed at HEAD.
  `scope --branch B [--base REF] | --range A..B` (read-only; task from `--task`, an `intent/<ID>` branch
  or the active task) reports forbidden, H8 Preserve, the sensitive denylist (lockfiles, manifests,
  `.github/workflows/**`, `.env*`, `*.pem`) unless a writes entry owns it explicitly, and paths outside
  writes: exit 0 clean, 1 findings, 3 nothing changed, 4 refused. `status` shows `scope=pass|fail|
  unchecked` per recorded branch. The active task (`worktree add` or `scope --set`) is
  `.workspace/state/active-task` in the workspace and `~/.config/snds-workspace/state/telemetry/<slug>/
  active-task` elsewhere (never inside the repo). `scope --check-path PATH` is the pre-write accelerator:
  it fails open, stays under 50 ms, and exits 1 only when the task says `enforce: true`; the hook step
  is report-only on every host (stderr + `scope.jsonl` beside the pointer).
- **`scope-audit`.** Checks each integration merge (or a `--task ID --rev A..B` range) against the
  task's `writes` plus the integrator's, the spec's `**HELD:**` set, JSON selectors, and unreverted
  `session: auto-commit` commits. Exit 0 clean, 1 violation, 3 nothing to audit.

## Filename and placement

| Work lives in… | Spec lives in… |
|---|---|
| `07-projects/<id>/` | that folder, usually `docs/INTENT.md` |
| An external git repo | that repo (never copy employer substance into this vault) |
| Workspace-brain itself | `07-projects/19-workspace-brain/docs/` (remediation: `INTENT-remediation-<yyyy-mm>.md`) |
| An employer repo's remediation | stdout by default; a neutral render lands only by branch → PR from a non-Claude surface |

Live handoff **points at** the spec; it does not duplicate it.

## Related

- L1: [[17-intent-coordination-operating-model]]
- L2: [[intent-coordination]]
- Verifier: [[mission-fit]] · [[06-qa-operating-model]]
- Movement: [[open-agent-engine]]
