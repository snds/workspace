---
description: Audit theme coverage, mode propagation, and DTCG resolve
allowed-tools: Read, Grep, Glob, Bash(find:*), Bash(wc:*), Bash(sort:*), Bash(head:*)
---

Run the theme-audit skill against the user's design system themes.

Load the theme-audit skill from 03-skills/design-system-ops/skills/theme-audit/SKILL.md and follow its complete workflow.

If the user provided a file or directory path as an argument, use that as the token/theme source: $ARGUMENTS

If no argument was provided, begin with discovery — search the codebase for theme files, dark/light (or brand) mode maps, DTCG `$extensions`, CSS `light-dark()`, and component-tier tokens that should resolve per mode.

Before starting the audit, read the reference material specified in the skill's frontmatter from 03-skills/design-system-ops/skills/theme-audit/references/ when those files exist.

Produce the full audit report including: theme coverage, component-tier propagation, resolver findings, and a prioritised remediation list.
