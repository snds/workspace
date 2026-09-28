---
type: decision
description: use_figma skillNames is logging only; an existing-file wrap is not a construction exemption; the bind-probe capture is mandatory per component.
created: 2026-09-28
confidence: high
relations:
  builds-on: ["[[decision-capture-and-assess-split]]"]
  relates-to: ["[[figma]]", "[[figma-ds-surface-authoring]]"]
---

## For future agent
- **TL;DR:** `skillNames` on `use_figma` does not load or enforce skills. A wrap, recipe, instance, or edit in an existing file is not an exemption from binding. After each component, `figma-bind-probe.py --capture` must run; exit 2 is not done, and `--self-test` does not prove the node.
- **As of:** 2026-09 · **Status:** current

## Context — what forced a choice
Workspace doctrine already required [[figma]] + [[design-engineer]] before vendor plugin skills, semantic binds instead of `Color/*`, and `09-tools/figma-bind-probe.py`. That still failed on a real canvas write. Cursor's skill list did not auto-load the hub. `skillNames` was treated as if it executed skills. Agents treated "existing file / wrap / not greenfield" as a waiver. Numeric Plugin API padding, including zeros, was treated as done. The per-component probe was skipped, and a green close-out (`--self-test` plus a labelled capture skip) was treated as a pass.

## Decision — what we chose
Construction gates 0–6 live in `03-skills/figma/SKILL.md` and are the default path in `03-skills/figma-component-generation/SKILL.md`. Cursor loads `.cursor/rules/figma-construction.mdc` (`alwaysApply`) so a Figma write starts by reading the hub. Examples that assigned `paddingLeft` as a number now call `setBoundVariable`. The mint-vs-edit table for gates stays in the figma hub. It does not become a new framework.

## Rationale — why, and what we rejected
Rejected: another paragraph of the same hard-gate copied into every spoke; a new framework for a Figma-only skip; treating `skillNames` as enforcement; raising the user-rules beacon (it is a thin paste with a byte pin, and standing law does not belong there); hand-editing `~/.cursor`.

## Consequences — what this commits us to
A Figma write that cannot load the hub, cannot see the token collections, or cannot capture for the probe stops and reports the blocker. Negative overlap may stay literal only with an `allow` reason. Phase 0–2 of a from-scratch library pipeline is not required when tokens already exist; Gates 2 and 5 still are. A third domain that skips a prose gate the same way is what would promote this into [[13-domain-rigor-stack]].
