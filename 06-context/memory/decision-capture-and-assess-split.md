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
  **Exit 2 = nothing verified = NOT a pass.** Captures go to the scratchpad because they are
  transient and file-specific, NOT because of wall 3 (that wall is one-directional: nothing
  personal into employer repos; employer design data lives here by design). Same split shape
  applies to any MCP-gated check.
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
regresses.

**Validated on three live nodes, which corrected the contract three times and then proved its premise.**
`get_metadata` carries no paint data and types are element tags, so R3 must judge a raw shape
by tree position (top-level = chrome; inside an instance = that component's internals).
`get_variable_defs` returns a MIXED map — token paths, `var(--x)` refs, and bare property
names that are the resolved literals of UNBOUND properties. That third kind is the R2 signal
and it is visible nowhere else; without the fix the probe would have returned a false pass on
a component carrying eight unbound properties.

Third: a second node, probed specifically to test for over-fire, found one. R2 must key on
**Figma/CSS PROPERTY NAMES (a closed, stable set)**, never on token shape — "no slash"
flagged doctrine's `space-0`; "no separator" flagged a real single-word semantic token,
`foreground`. Two lessons that generalise: a detector built only against fixtures of your own
design tests your imagination, not the tool — and when writing a discriminator, enumerate the
closed set, never the open one.

Fourth, the premise itself is now demonstrated: a 15px focus-ring radius appears in one node
as the bare property `radiusRing` (no token in its map) and in another as the bound token
`focus-ring-radius/md` (no bare key). Bare where unbound, token where bound. That is why a
bare key can be trusted to mean unbound, and it is what settled the raw variable-font weight
axis as a TRUE positive — two of the three nodes carry `wght` values that no token in their
own map could be echoing.
