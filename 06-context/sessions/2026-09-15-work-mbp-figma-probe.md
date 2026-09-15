### 2026-09-15 — A8: the Figma construction gate becomes a detector

SessionID: 2026-09-15-work-mbp-figma-probe
--- SESSION BLOCK ---
Date: 2026-09-15
Machine: Work MacBook Pro (main, going forward)
Surface: Claude Code (Mac desktop app)
Agent: Claude Opus 5
Project(s): 19-workspace-brain

Summary: A8, the last open row from the 2026-09-11 automation review. It was classified a
capability mint rather than a check because capture needs MCP, which only the agent has.
Resolved by splitting the gate at the tool boundary: the agent captures via
get_variable_defs/get_metadata into its scratchpad, and `09-tools/figma-bind-probe.py`
judges the capture deterministically. `--emit-template` prints the exact MCP calls so the
agent half is mechanical.

Rules taken verbatim from the figma hub hard gate and figma-ds-surface-authoring: R1 a bound
`Color/*` primitive (FAIL), R2 raw unbound value with zeros explicitly not exempt (FAIL), R3
painted rect where an instance belongs (FAIL), R4 density-unaware ladder on a control (WARN,
because general surface radius may correctly use the Radii ladder), R0 an allow entry with no
written reason (FAIL — doctrine says exceptions are noted, not silently left). An empty
capture exits 2, never 0: "no findings" and "no evidence" are different claims.

Preflight defect found on the way: capability-registry detected Figma with `mcp__*figma*__*`,
but Claude Code mounts the server under a UUID (`mcp__<uuid>__use_figma`), so the capability
read as ABSENT while live and authenticated — every `requires: [figma-mcp]` skill would have
silently degraded. Pattern fixed to `mcp__*figma*` with the reason recorded inline. Found only
because A8 forced a real preflight instead of a documented one.

Employer wall: `whoami` is sean.sands@centricsoftware.com (Centric org). Running the probe is
fine (read-only, Sean's own work account) but captures are employer content — both fixtures
are synthetic and say so, and the skill, CLI help and close-out SKIP text all say scratchpad.

Wired: close-out figma row goes from two bare SKIPs to SKIP-for-capture plus a real CLI for
assess; harness quality lane (22 gates); CI runs the self-test and both fixtures, asserting
the violation fixture FAILS; figma hub step 7; five Layer-0 routes. The old
`test_figma_is_honest_skip` encoded the pre-A8 world and is now
`test_figma_splits_capture_from_assess`, asserting both halves.

OPEN AND STATED: the probe has never been fed real MCP output. The capture contract comes
from documented tool shapes, not observed ones. One Figma node URL and one run closes it.
Recorded as a gap rather than rounded up to done.

22 harness gates green, 43/43 negative fixtures, 48/48 matcher cases, 14/14 trajectories,
ruff clean.

Report: `07-projects/19-workspace-brain/reports/figma-bind-probe_v1.0_2026-09-15.md`
Decision: `[[decision-capture-and-assess-split]]`
--- END BLOCK ---
