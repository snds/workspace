---
type: decision
description: Where a gate needs a tool only the agent can reach, split it — the agent captures, a CLI judges; the capture stays a labelled SKIP and never gets faked into a green tick.
created: 2026-09-15
confidence: high
relations:
  builds-on: ["[[decision-reachability-is-a-detector]]", "[[decision-visual-qa-interrupt]]"]
  relates-to: ["[[figma-ds-surface-authoring]]", "[[agentic-error-correction-foundations]]", "[[measured-visual-verdicts]]"]
---

## For future agent
- **TL;DR:** Figma construction is now checked, not trusted.
  `python3 09-tools/figma-bind-probe.py --emit-template` prints the MCP calls;
  `--capture <scratchpad>/cap.json` refuses `Color/*` primitives, raw values (zeros are not
  exempt), and rects-instead-of-instances, and warns on density-unaware control tokens.
  **Exit 2 = nothing verified = NOT a pass.** Captures are employer content — scratchpad only,
  never committed. Same shape applies to any MCP-gated check.
- **As of:** 2026-09 · **Status:** current

## Context — what forced a choice
A8 sat open through two passes because the gate needs MCP inspection and MCP belongs to the
agent, not to a script. The tempting resolutions were both bad: leave it a prose instruction
(which is what "refuse Color/*" already was, and it was not being enforced), or pretend a
script could capture (a lie that would produce green ticks over unverified work).

## Decision — what we chose
Split the gate at the tool boundary. The agent captures via MCP into its scratchpad; a
deterministic CLI judges the capture against rules taken verbatim from doctrine. In
`close-out-dispatch` the capture step stays a labelled SKIP and the assess step is a real
CLI, so the plan tells the truth about which half was machine-verified. Nothing-to-verify is
its own exit code (2), never 0, because "no findings" and "no evidence" are different claims.

## Rationale — why, and what we rejected
Rejected: a model grading its own Figma output (same-model critique is not a detector);
faking the capture step in a script; failing R4 density (general surface radius may correctly
use the Radii ladder, so failing it would make the probe wrong on correct work — warn
instead); committing a real capture as a fixture (employer content in a personal repo).

## Consequences — what this commits us to
New MCP-gated checks follow this shape rather than becoming prose. The `figma` hub's step 7
names the probe, and `test_figma_splits_capture_from_assess` asserts BOTH halves so neither
regresses. Still open and deliberately recorded as such: the probe has never been fed real
MCP output — the capture contract comes from documented tool shapes, not observed ones, and
one live node URL closes that.
