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
- **`scope-audit`.** Checks each integration merge (or a `--task ID --rev A..B` range) against the
  task's `writes` plus the integrator's, the spec's `**HELD:**` set, JSON selectors, and unreverted
  `session: auto-commit` commits. Exit 0 clean, 1 violation, 3 nothing to audit.

## Filename and placement

| Work lives in… | Spec lives in… |
|---|---|
| `07-projects/<id>/` | that folder, usually `docs/INTENT.md` |
| An external git repo | that repo (never copy employer substance into this vault) |
| Workspace-brain itself | `07-projects/19-workspace-brain/docs/` |

Live handoff **points at** the spec; it does not duplicate it.

## Related

- L1: [[17-intent-coordination-operating-model]]
- L2: [[intent-coordination]]
- Verifier: [[mission-fit]] · [[06-qa-operating-model]]
- Movement: [[open-agent-engine]]
