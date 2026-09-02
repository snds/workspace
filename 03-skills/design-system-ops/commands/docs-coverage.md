---
description: Audit whether docs and Storybook keep pace with the code SSOT
allowed-tools: Read, Grep, Glob, Bash(find:*), Bash(wc:*), Bash(sort:*), Bash(head:*)
---

Run the docs-coverage skill against the user's component library and documentation surface.

Load the docs-coverage skill from 03-skills/design-system-ops/skills/docs-coverage/SKILL.md and follow its complete workflow.

If the user provided a file or directory path as an argument, use that as the docs/code root: $ARGUMENTS

If no argument was provided, begin with discovery — code components as SSOT, then Storybook/MDX/docs pages, then git staleness. Score join-confidence tiers A/B/C as the skill specifies.

Before starting the audit, read 03-skills/design-system-ops/knowledge-notes/documentation-coverage.md. Durable workspace doctrine still wins: [[ds-ops-governance-notes]].

Produce the full coverage report including: undocumented components, stale docs, join-confidence, and a prioritised remediation list.
