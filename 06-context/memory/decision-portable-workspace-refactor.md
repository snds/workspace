---
type: decision
description: Why the workspace was refactored to be portable, git-native, and LLM-agnostic
created: 2026-06-16
confidence: high
---

The workspace was refactored from a Google-Drive + Desktop-Commander + Claude-specific system into a
portable, surface/device/LLM-agnostic one where **the git checkout is the source of truth** and any
capable agent follows one declarative loading + contribution structure via [[AGENTS]] and the generated
`03-skills/skills.registry.json`.

**Why:** the prior design coupled everything to Google Drive (as the sync/source-of-truth filesystem),
Desktop Commander (the read/write MCP), and Claude-only mechanisms (`.claude/hooks`, slash commands).
That blocked reuse by any other tool or model and made "near-identical results across LLMs" impossible.
Skill loading order was implicit (the model guessed) and cross-links were sparse prose.

**Alternatives rejected:** (1) keeping Drive as source of truth with read-only fallbacks — still couples
the core; (2) building on the `wsx` bootstrap generator — kept as a *separate* effort, not a dependency,
so the workspace stands alone; (3) physically nesting `03-skills/` by domain — would break 200+ hardcoded
`SKILL.md` loader paths, so the flat-with-prefixes layout was kept and the tree imposed via frontmatter +
registry + MOCs.

This copy lives at `github.com/snds/workspace`, isolated from the Drive original's
`claude-workspace-system` repo (the shared local gitdir was never touched). See [[fact-workspace-repos]].

**Outcome (2026-06-16):** delivered as a 16-PR foundation-first stack (#1 standards → … → #16 Legion
galaxy playbook), then **consolidated onto `main` by fast-forward** (linear history; all 19 commits).
#1 auto-merged; #2–#16 closed as merged-by-fast-forward and the 16 `refactor/*` branches deleted
(commits preserved on `main`) — no zombie PRs/branches, per the open-writes "no zombies" gate. `main`
is the single source of truth: 233 skills, 540 markdown files, all five validators green. Day-to-day
contributions now follow [[08-workspace-contribution-framework]] + [[AGENTS]] write-quality gates.
