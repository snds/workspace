---
description: Comprehensive design system health sweep
allowed-tools: Read, Write, Grep, Glob, Bash(find:*), Bash(wc:*), Bash(sort:*)
---

Run the full system diagnostic — a comprehensive health sweep that chains the five core audit skills into a unified diagnostic report, then theme-audit and docs-coverage when those surfaces exist.

Load the agent instructions from 03-skills/design-system-ops/skills/full-system-diagnostic-agent.md and follow the complete workflow.

Before starting, read the reference material for each chained skill from their respective 03-skills/design-system-ops/skills/*/references/ directories.

The diagnostic runs in this order:
1. Token audit — token architecture, naming, structural debt
2. Component audit — inventory, usage, duplication, coverage gaps
3. Naming audit — convention consistency, ambiguity, intent clarity
4. Drift detection — where teams diverge and why
5. System health — scored assessment across 7 dimensions
6. Theme audit — when the system has light/dark or brand modes (skip and name the skip if it does not)
7. Docs coverage — when Storybook, MDX, or a docs site exists (skip and name the skip if it does not)

After the core five, fold any theme/docs findings into the synthesis. Use the synthesis decision tree (Phase 3) to identify cross-skill patterns: concentrated debt, documentation gaps, governance gaps, structural gaps, AI-readiness gaps, platform maturity gaps, or dependency cascades.

Produce a unified diagnostic report with: executive summary, per-skill findings table, cross-skill patterns, and a ranked action list ordered by impact.

If the user provides context about their system: $ARGUMENTS
