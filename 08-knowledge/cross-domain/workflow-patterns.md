---
tags: [workflow, process, patterns, audit, session-management]
created: 2026-04-28
updated: 2026-04-28
status: stable
confidence: high
sources: [session-log 2026-04-27, audit-log 2026-04-27]
related_skills: [workspace-bootstrap]
related_projects: [00-obsidian]
---

# Workflow Patterns — What We've Learned Works

Cross-domain patterns for how to manage work across sessions, machines, and projects. These are the operating habits that emerged from real experience, not from theoretical planning.

---

## Stale-Content Review Before Archiving

**The rule:** Before archiving any file as a duplicate, read both the candidate and the target side-by-side. Explicitly check for content that exists in the candidate but NOT in the target. Only archive if it's a strict subset.

**Why:** The first `/optimize` run found two files (`figma-ds-generation-pipeline.md` and `figma-style-binding.md`) that looked like duplicates but contained unique content (Radix scale binding maps, Effect Style binding details) that wasn't in the live SKILL.md. If archived without review, that content would have been silently lost.

**The process:**
1. Read both files
2. Diff for unique sections
3. Classify: clean-duplicate / stale-but-useful / stale-contradictory
4. If stale-but-useful: migrate the unique content first, then archive
5. Write a REVIEW-NEEDED.md note if anything needs Sean's attention before archiving

---

## Pending Items — Three-Bucket Structure

**Active** (next actions — things with a clear next step that can be done in the next session):
- Specific, actionable, with a clear first move

**Deferred** (resurface on context match — things that matter but have no near-term trigger):
- Not urgent, not blocked — just waiting for the right moment
- Resurface when a related project becomes active

**Recently resolved** (prune at next /optimize — completed items held for short-term reference):
- Crossed off with a date and summary
- Cleaned out at the next audit cycle

**Why this structure:** The prior structure (5 buckets, chronological) made it hard to triage at session start. The three-bucket model answers one question immediately: "what can I actually do today?"

---

## audit_skip Mechanism

Some files should be invisible to the `/optimize` audit — personal reference sheets, scratch notes, drafts in progress. Add this to the YAML frontmatter:

```yaml
audit_skip: true
audit_skip_reason: "cross-context personal reference — audit would misread as stale"
```

The optimize skill reads this flag and excludes the file from analysis. First user: `_CHEATSHEET.md`.

---

## Skill File Discovery Pattern

When there are two files for the same skill — one at `02-skills/skill-name.md` (loose) and one at `02-skills/skill-name/SKILL.md` (canonical) — the directory version is always authoritative. The loose file is a legacy artifact from an earlier era of the skill system.

The skills-manifest.json always points to the directory SKILL.md. The manifest is the single source of truth for the canonical location of every skill.

---

## Session End Protocol Habit

The `/session-end` skill is the canonical close-out. What matters most for continuity:
1. **Write the session block** to `06-context/session-log.md` — newest first
2. **Update project-context.md** — mark resolved items, add new pending items
3. **Update the relevant SESSION-STATE.md** if project state changed
4. **Commit and push** — everything on `main` via `git add -A` (the dispatcher handles this)

**Don't skip the commit even for small sessions.** Drive sync is the file layer, but git is the version layer. A session that only moves files still needs a commit so the history is coherent.

---

## Trigger-Word Context Loading

The `UserPromptSubmit` hook loads context automatically when certain words appear in prompts. Known triggers:

| Trigger words | What loads |
|--------------|-----------|
| `legion`, `the game`, `bobiverse` | `legion-project` skill + relevant sub-hub |
| `centric`, `PLM`, `data table` | Centric DS context, Ark UI notes |
| `icon font`, `centricsymbols`, `variable axis` | `variable-icon-font-architect` skill |
| `figma plugin`, `plugin dev` | `figma-plugin-dev` skill |
| `omni` | `omni-project` skill |

This is defined in the dispatcher's `handle_user_prompt_submit()`. Adding new triggers requires editing the dispatcher directly.

---

## Cross-Machine Work Reconciliation

When two sessions happen on different machines the same day (e.g., morning on Windows, afternoon on Mac), both sessions write their own blocks to the session log independently. `/reconcile` merges them into a single coherent entry in chronological order.

**The pattern that works:** End each session with its own block written. Don't try to write a combined block retrospectively — that loses the per-machine context. The reconcile skill does the merge.
