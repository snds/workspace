---
type: decision
description: First-wave automation (A1 loadset, A2/A3 dispatch, A6 secrets, A7 Layer 0 schema) is wired into Layer 0, close-out, AGENTS, adapters, and CI — not a pile of unused scripts.
created: 2026-09-11
confidence: high
relations:
  builds-on: ["[[decision-visual-qa-interrupt]]", "[[decision-self-improving-workspace]]", "[[decision-tool-native-adapters]]"]
  relates-to: ["[[process-rigor-gaps]]", "[[agent-load-miss-review]]"]
---

## For future agent
- **TL;DR:** Scripts that the next agent never runs are theater. Load set = `skill-loadset.py`. After produce = `close-out-dispatch.py --run`. Command-hub L3 coverage = `close-out-dispatch.py --check`. Layer 0 JSON = `validate-layer0-schema.py`. Secrets = `check-secrets.py`. Followthrough, adapters, bootstrap, CI, and close-out step 2 name those CLIs.
- **As of:** 2026-09 (corrected 2026-09-25, see the end) · **Status:** current

## Context — what forced a choice
Process-rigor and the automation review mapped jobs that should become scripts. Minting them without attach points would recreate the silent-hub problem: files exist, no load edge.

## Decision — what we chose
One L3 table in `close-out-dispatch.py` (not `governed_by` on all 47 hubs). Honest SKIP rows for MCP/device/aio. Wire the CLIs into `prompt_route.py` followthrough, AGENTS.md skill-loading, close-out step 2, thin adapters, `brain.mdc`, workspace-bootstrap, Layer 0 routes, write-quality CI, and nightly recipe (still opt-in, no cron).

## Rationale — why, and what we rejected
Pasting close-out into 47 hubs (R3). LLM-as-judge merge gate (R1). Requiring `governed_by` on every hub as the CI check. Enabling nightly cron (A4). Faking `cursor-externalize` in GitHub Actions (A10).

## Consequences — what this commits us to
New command hubs must get a `HUB_DETECTORS` row or `close-out-dispatch.py --check` fails. A8 (Figma bind probe) still waits for a produce that cannot refuse `Color/*`. Do not treat dispatch exit 0 as visual verified when SKIP lines remain.

## As-of correction — 2026-09-25
The A8 sentence above was true on 2026-09-11 and went stale: A8 landed 2026-09-15 (`figma-bind-probe.py`, report figma-bind-probe_v1.0), and A4, A5 and A9 landed the same day (automation-second-wave_v1.0). The current state of every recommendation from the 2026-09-11 reports lives in the findings register `07-projects/19-workspace-brain/docs/INTENT-remediation-2026-09.md`, not in this note or the reports' status lines.
