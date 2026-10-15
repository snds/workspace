---
type: decision
description: Every design system Sean builds runs a mechanical pass that finds recurring component compositions and suggests them as pattern candidates; the detector is a reusable library, not prose
created: 2026-10-15
confidence: high
relations:
  builds-on: ["[[decision-component-pattern-framework-system]]", "[[decision-pattern-uniqueness]]"]
  relates-to: ["[[decision-frost-ds-ai-operating-model]]"]
---

## For future agent

- **TL;DR:** A design system must be able to *notice its own patterns*. A detector scans how components are actually combined (in code and in Figma), finds compositions that repeat, and proposes them as candidates. People decide; the detector only suggests. The same detector is reused by the design-system analytics tool. **As of:** 2026-10-15 · standing rule.

## The rule

1. **Every design system Sean builds or adopts ships with pattern-candidate detection.** This applies to the shared Mailbird / Synapse / Lockdown system and to employer systems (the rule crosses the wall; the data never does).
2. **What counts as a candidate.** A composition of two or more components in the same arrangement (parent, children, order, the props that shape them) that appears **three or more times** across **two or more hosts** (screens, routes, Figma pages). Three is the workspace's rule of three; one or two occurrences stay host-local.
3. **Judge with [[decision-pattern-uniqueness]].** Different user job and different anatomy → **pattern**. Shares a parent component → **variant or usage** of that parent. One-off → **snowflake**, left alone.
4. **Output is a suggestion record, never an auto-created component.** Fields: candidate name by intent, anatomy (the slot tree), occurrences with file or node references, hosts, proposed tier (pattern · compound component · variant · snowflake), confidence, and the nearest existing pattern if one is close.
5. **The detector is a library with one output schema**, so the design-system analytics tool, the `component-audit` and `drift-detection` skills, and a Figma plugin can all call it. Prose skills describe how to read its output; they do not re-implement it.
6. **Inputs.** Code: the component import graph and JSX/template composition. Figma: instance nesting read through the Figma MCP or a plugin. Both feed the same schema.
7. **Review cadence.** Candidates surface in the drift report. A candidate ignored three times is parked, not re-raised.

## Why

Pattern documentation is the most under-done part of every design system. Patterns form by convention and are discovered late, usually after three teams have built the same thing three ways. A mechanical pass turns that into an early, cheap signal. Making the detector a library rather than a skill keeps one source of truth for "what is a candidate" across the analytics tool, the audits, and Figma.

## Where it lives

- Rule: this note. Hub: [[01-frameworks/09-component-and-pattern-framework|framework 09]] §7a.
- First implementation target: the shared Mailbird / Synapse / Lockdown design system (Lockdown D14), then the design-system analytics tool reuses it.
- Reference implementation: `snds/dsa` (`@snds/dsa`, TypeScript, ts-morph for the code graph; Figma adapter planned). Decided 2026-10-15. Vault project: [[07-projects/29-unicron/README|29-unicron]].
