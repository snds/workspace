---
type: decision
description: Human review of visual/LLM work is the exception — mint missing detectors and push; page Sean only if self-critique is failing or mint still cannot hit the accuracy/perf bar.
created: 2026-09-11
confidence: high
relations:
  builds-on: ["[[close-out]]"]
  relates-to: ["[[process-rigor-gaps]]"]
---

## For future agent
- **TL;DR:** After producing visual or code-adjacent work, run capture → assess → correct with named CV / visual-code QA. If a detector is missing or cannot hit the accuracy/perf bar, mint the smallest QA method/skill/tool, calibrate it, re-prove, and **push to this workspace independently**. Prompt Sean only if you cannot be critical of your own work or that mint still fails. Skill: `03-skills/close-out/SKILL.md`. Leave-the-building is still human. Never this path on employer repos.
- **As of:** 2026-09 · **Status:** current

## Context — what forced a choice
Close-out v2.2 made "stop for Sean" the default last step of every Figma generate and visual hub. Sean's actual bar: he should only be interrupted when the agent is failing at self-critique or cannot run a usable QA loop. A standing eyeball made him the detector.

## Decision — what we chose
Human visual review is optional **iff** computer vision and visual/code QA can capture, assess, **and** correct the in-scope defect classes. If they cannot because a detector is missing, **mint it** (extend L3 first; else smallest skill/tool + planted fixture) and push to this vault without waiting. Interrupt only for self-critique failure or a mint that still misses the accuracy/perf bar. VLM "looks good" is critique, not a detector. Operational home is close-out.

## Rationale — why, and what we rejected
Rejected "always stop" (turns Sean into unpaid L3). Rejected "never stop" (agents over-grade). Rejected "page Sean when a tool is missing" (he becomes the missing detector). The honesty bound stays: if you would over-grade, cannot refute, or the mint cannot calibrate — page him.

## Consequences — what this commits us to
Figma prove-gate still inspects binds/instances/variant matrix and native-zoom captures. Missing cuespec/inspect → mint, then re-prove. Library publish remains leave-the-building. A mint without a failing fixture, or a red CI, is not a pass. Employer repos are out of this push path.
