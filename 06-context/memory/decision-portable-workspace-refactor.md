---
type: decision
description: Why the workspace was refactored to be portable, git-native, and LLM-agnostic
created: 2026-06-16
confidence: high
---

The workspace was refactored from a Google-Drive + Desktop-Commander + Claude-specific system into a
portable, surface/device/LLM-agnostic one where **the git checkout is the source of truth** and any
capable agent follows one declarative loading + contribution structure via [[AGENTS]] and the generated
[[skills.registry.json]].

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
