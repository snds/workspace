---
name: optimize
description: Workspace audit. Reviews CLAUDE.md, frameworks, MOCs, context files, skills for stale items, contradictions, drift, and consolidation opportunities. Runs a seven-surface system maintenance loop (skill graph, contract, knowledge, memory, routing, validators, handoff): deterministic probes first, then judgment. Distinct from per-task prove-gates. Outputs a prioritized punch list (P0/P1/P2) and applies fixes only with sign-off. Logs to 06-context/audit-log.md. Invoked as /optimize or triggered by "audit the brain" / "workflow audit" / "system error correction".
---

# /optimize — Brain audit

## When to invoke

- User explicitly runs `/optimize`
- User says "audit the brain", "workflow audit", "review the workspace foundations", "check for drift"
- The dispatcher's SessionStart notice flags stale audit (>14 days since last) AND user agrees to run one

## Why this exists

The brain accumulates entropy: pending items get done but stay listed; docs reference paths that move; skills overlap; MOCs link to deleted notes; conventions drift between CLAUDE.md and individual SKILL.md files. Without periodic review, the friction grows quietly until something breaks. This skill is the deliberate rebalancing pass: **system-level error correction** (drift of the vault), distinct from per-task generate-verify loops (#06 detector check, Literal prove-gate).

## Protocol

### Step 1 — Establish scope

Default scope is **full**: read all the foundation files listed below. If user specifies a narrower scope ("just frameworks", "just skills", "just project-context"), respect it.

**Full-scope reads (in this order):**

1. `CLAUDE.md` — primary context
2. `01-frameworks/00-README.md` + the numbered frameworks it lists (sixteen as of 2026-08; do not assume the old five-file core set)
3. `01-frameworks/team-practices-and-decisions.md`
4. `06-context/role-and-context.md`
5. `06-context/project-context.md` (full file)
6. `06-context/session-log.md` (head — first 200 lines is enough for recency)
7. `06-context/artifact-registry.md` (if exists)
8. `04-preferences/user-preferences.md`
9. All MOCs at workspace root: `_HOME.md`, `_PROJECTS.md`, `_SKILLS.md`, `_FRAMEWORKS.md`, `_CONTEXT.md`, `_CHEATSHEET.md`
10. `00-bootstrap/OBSIDIAN-SETUP.md`
11. `00-bootstrap/SURFACES.md`
12. `.claude/settings.json`
13. `.claude/hooks/dispatcher.py` (skim for hook-event coverage and helpers actually invoked)
14. List `.claude/skills/` and read each SKILL.md (small set, 5-10 files)
15. List `03-skills/` and sample the hub skills mentioned in CLAUDE.md (don't read all 60+)

### Step 1.5 — Honor audit-skip opt-outs

Before scanning, build a skip-list. Any markdown file whose YAML frontmatter contains `audit_skip: true` is exempt from ALL findings in this run — drift, contradictions, staleness, MOC-mention completeness, etc. The `audit_skip_reason` field (if present) explains why; surface it in the final report under a "Skipped (opt-out)" line so the audit is transparent about what wasn't checked.

Use `Grep` for `audit_skip: true` across the workspace and resolve the matched file paths. Examples of legitimate opt-out rationales: cross-context personal reference files, scratch notes Sean intentionally keeps loose, drafts in flux.

Do not invent your own opt-outs and do not skip files without the explicit frontmatter flag.

### Step 1.6 — Seven-surface maintenance loop (system ECC)

How the *brain* error-corrects itself. Distinct from per-task prove-gates. Run the
deterministic probes first (do not skip). Then Step 2 applies judgment on top of
the probe output.

This workspace's seven surfaces:

1. **Skill graph** — `python3 09-tools/validate-links.py` and `python3 09-tools/build-registry.py --check`
2. **Frameworks / contract** — judgment vs `AGENTS.md` and `01-frameworks/00-README.md` (drift, contradiction)
3. **Knowledge** — `python3 09-tools/validate-workspace.py` (index coverage) plus `python3 09-tools/vault-health.py`
4. **Context / memory** — pending items vs `session-log.md` head; `MEMORY.md` coverage (workspace validator already probes this)
5. **Triggers / routing** — `python3 09-tools/build-trigger-routes.py --check`. Under-fire on a real prompt must be visible (dispatcher routing-coverage note, or Cursor says Layer 0 missed). Silence is not "nothing matched."
6. **Validators** — `python3 09-tools/test-validators.py` plus the write-quality chain (`build-related` → `build-registry` → integrity → links → workspace)
7. **Handoff** — Active-project `SESSION-STATE.md` Live handoff `_Last updated` older than 30 days; uncompacted session fragments in `06-context/sessions/`

Probe failures are P0 until the detector is green or the finding is triaged. Do not
treat a green live-tree validator as proof the detector still has teeth; that is
what `test-validators.py` is for.

The opt-in cron cousin is `02-shared-references/nightly-maintenance-recipe.md`
(fold / heal / rebuild). `/optimize` stays human-in-the-loop judgment. Do not
auto-enable nightly from this skill.

### Step 2 — Run the checks

Look for the following classes of issue. Mark each finding with priority and concrete location.

**Drift (docs vs filesystem):**
- Paths referenced in docs that don't exist on disk
- Files in the filesystem that no docs mention (orphans)
- Skills in `03-skills/` not listed in `_SKILLS.md` or CLAUDE.md hub mentions
- Wikilinks in MOCs pointing to deleted notes
- Setup commands that reference moved/renamed files

**Contradictions:**
- Conflicting guidance between CLAUDE.md and a SKILL.md
- Two skills describing overlapping triggers (e.g., when does `ds-advisor` fire vs `design-engineer`?)
- Convention stated one way in one place, differently elsewhere
- Pending items in `project-context.md` that have actually been resolved per `session-log.md` or git history

**Stale items:**
- Pending items dated more than 60 days ago with no recent progress mention
- "Long-standing items" in project-context.md that should be evaluated for relevance or archived
- SESSION-STATE.md files that haven't been touched in >30 days for "active" projects
- Outdated dates in `_Last updated:` fields
- Project status descriptions that don't match recent reality (per session-log)

**Duplication / consolidation opportunities:**
- Same information stated in multiple files (could be canonical in one + linked from others)
- Multiple skills doing nearly the same thing
- Repeated boilerplate in SKILL.md files that could be a shared snippet

**Gaps:**
- Mentioned but unimplemented (e.g., "we will build X" — never built)
- Skills referenced from hubs but the SKILL.md doesn't exist
- Frameworks alluded to in docs but not actually present in `01-frameworks/`
- Surface-discovery gaps (a tool surface mentioned but no setup docs)

**Clutter:**
- `_archive` folders that should be cleared
- Loose `.md` files at `03-skills/` root that duplicate folder contents (Sean has flagged these before — see project-context.md "Clean up duplicate skill files")
- Drive-injected `desktop.ini` / `.DS_Store` files anywhere git tracks them

### Step 3 — Output the punch list

Render in this format:

```
## /optimize audit — {YYYY-MM-DD}, {machine}

**Scope:** {full | narrowed scope}
**Files reviewed:** {N}
**Findings:** {total} — P0: {n} · P1: {n} · P2: {n}

### P0 — workflow-breaking ({n})
1. **{file}:{line if applicable}** — {what's wrong, in one line}
   - Suggested fix: {specific edit}
2. ...

### P1 — friction ({n})
1. **{file}** — {issue}
   - Suggested fix: {edit}
2. ...

### P2 — polish ({n})
1. **{file}** — {issue}
   - Suggested fix: {edit}
2. ...

---

Want me to apply any of these now? Reply with the numbers (e.g., "P0 1,2 + P1 3") or "all P0" or "skip all".
```

### Step 4 — Apply approved fixes

Only apply fixes the user explicitly authorizes. Rules:

- **No deletions** without explicit per-fix confirmation. Move to `_archive/` instead.
- **Move-don't-rename** for files referenced from elsewhere — update references first, then move.
- For each fix: make the edit, verify the file is valid (e.g., JSON parses, markdown frontmatter intact), report what was done.
- If a fix has cascading implications (e.g., renaming a skill folder breaks 5 references), STOP and surface the cascade for user decision.

#### Step 4a — Stale-content review (mandatory before archiving)

Before moving any stale file to `_archive/`, you MUST do a content-comparison pass. Stale files often contain valuable context that hasn't been migrated to its successor. Skipping this step risks losing useful material that the live version doesn't carry.

For each candidate (a duplicate `.md`, a `_deprecated_*` directory, an older variant alongside its current canonical file, etc.):

1. **Read both files in full** — the stale candidate AND its presumed successor (the dir SKILL.md, the live framework file, whatever it's been replaced by).
2. **Diff for unique content** — identify sections, examples, rules, or reference material in the stale file that do NOT appear in the successor. Be specific: section headings, code examples, decision tables, named patterns.
3. **Check for contradictions** — if the stale file states something that conflicts with the successor, the successor wins (it's the live version). Note the contradiction in the audit log so we can verify the conflict was deliberate.
4. **Classify each candidate** as one of:
   - **Clean duplicate / strict subset** — successor is a superset; safe to archive without review.
   - **Stale-but-useful** — has unique content worth migrating. DO NOT archive yet. Leave in place. Write a `REVIEW-NEEDED.md` note (or extend an existing one in the same `_archive/<batch>/` folder) listing: file path, comparison target, unique sections, suggested action (migrate / confirm-superseded / defer).
   - **Stale and contradictory** — has content that conflicts with the successor. Flag explicitly in the review note; do not migrate without Sean confirming which version is correct.
5. **Surface flagged items in the final report** — list the stale-but-useful and stale-contradictory items by name so Sean knows exactly what's pending review.

This step is non-negotiable when archiving. The cost (two file reads + a diff) is small; the cost of silently losing migratable context across the brain is high.

### Step 5 — Log to audit-log.md

Append a new entry at the top of `06-context/audit-log.md` (newest first), under the "## Entries" heading, using the format defined in that file's preamble. Include:

- Date + machine
- Scope
- Findings counts (P0/P1/P2 totals)
- One-liner per finding (for searchability later)
- What was actually fixed in this run
- What was carried forward (un-fixed)

The dispatcher reads the date of the most recent entry to decide whether to surface a "stale audit" nudge in future SessionStart contexts. Threshold: 14 days.

### Step 6 — Final report

Output a one-line confirmation:

```
✓ Audit logged. {N} fixes applied · {M} carried forward · audit-log.md updated.
```

If carried-forward findings include things that ought to become real pending items in `project-context.md`, propose those additions explicitly and ask for sign-off before adding.

---

## What this skill does NOT do

- Doesn't refactor large structures unprompted (just flags them)
- Doesn't rename files (cascade risk too high without targeted user input)
- Doesn't archive without confirmation
- Doesn't second-guess deliberate stylistic choices in user-authored content
- Doesn't audit project-internal artifacts (`05-artifacts/`, `07-projects/<project>/<work-files>`) — those have their own per-project review cadence; this is meta-level only
- Doesn't replace per-task prove-gates (Literal prove, #06 detector check, Proofboard). Those fire inside producing work.
- Doesn't auto-enable the nightly recipe. That remains opt-in.

## Tone

Audit findings are observations, not judgments. Sean built this brain deliberately; drift is inevitable and natural, not a failure. Frame everything as "I noticed X — here's a possible cleanup" not "this is wrong."
