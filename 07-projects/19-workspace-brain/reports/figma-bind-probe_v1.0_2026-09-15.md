---
title: A8 — the Figma construction gate becomes a detector; capture and assess split honestly
version: "1.0"
date: 2026-09-15
surface: Claude Opus 5 + Claude Code (Mac desktop app)
sha: 71f8d7a
status: applied — probe minted, wired, fixture-validated; LIVE MCP validation still outstanding
companion: automation-second-wave_v1.0_2026-09-15.md
---

# Figma bind probe v1.0 — 2026-09-15

**Evidence-grade legend:** `VERIFIED` · `INFERRED` — re-runnable via
`09-tools/figma-bind-probe.py --self-test` and the two fixtures. The one thing NOT verified
is stated in §6 rather than buried.

A8 was the last open row from the 2026-09-11 automation review, deferred twice on the
grounds that it needed a real Figma produce. Sean asked for it directly, so it is built.

---

## 1. What A8 actually is

The `figma` hub's step 7 reads: *capture (MCP inspect + native-zoom screenshot) → assess
(refuse `Color/*`; instances not rects; variant matrix) → correct and re-prove. Missing
detector → mint it.* The review classified A8 as a **capability mint**, not a "turn into
check", and that classification is the whole design problem: **capture needs MCP, which only
the agent has; assess needs rules, which a script does better than a model grading its own
work.**

So the gate splits:

```
agent → get_variable_defs / get_metadata → capture.json → figma-bind-probe.py → verdict
```

`--emit-template` prints the exact MCP calls and the capture skeleton, so the agent half is
mechanical rather than remembered. Pretending the capture half could be scripted would have
been the easy lie here; `close-out-dispatch` keeps it labelled `SKIP` and now names a real
CLI for the half that can be.

## 2. Rules, all from doctrine

| Rule | Grade | Source |
|---|---|---|
| **R1** node binds a `Color/*` primitive directly | FAIL | `figma` hub hard gate |
| **R2** raw unbound value — *zeros are not exempt* (pad/gap 0 → `space-0`, radius 0 → `radius-none`, stroke 0 → `border-width-0`, transparent → the `transparent` token) | FAIL | [[figma-ds-surface-authoring]] rule 13 |
| **R3** painted RECTANGLE/ELLIPSE where an instance belongs | FAIL | hub step 7 |
| **R4** density-unaware ladder on a control | WARN | standing rule, Sean 2026-08-06 |
| **R0** an `allow` entry with no written reason | FAIL | rule 13: exceptions are *noted*, not silently left |

R4 is a warning on purpose: general surface radius (cards, dialogs) may legitimately use the
Radii ladder, so failing it would make the probe wrong on correct work. Same discipline as
the hub-prose spokes and the collision ceiling.

**An empty capture exits 2, never 0.** "Nothing to verify" is the failure mode that makes a
prove-gate worthless, so it is a distinct, loud exit code rather than a green tick.

## 3. Preflight defect found on the way

`capability-registry.md` detected Figma with `mcp__*figma*__*`. Claude Code mounts this
server under a **UUID** (`mcp__<uuid>__use_figma`), so the pattern reported the capability
**absent while it was live and authenticated** — meaning every `requires: [figma-mcp]` skill
would have silently taken the degraded path. Pattern corrected to `mcp__*figma*`, with the
reason recorded inline.

Found only because A8 forced an actual preflight instead of a documented one.

## 4. The employer wall

`whoami` returns `sean.sands@centricsoftware.com`, Centric Software org. Running the probe
against Centric files is fine — it is read-only, on Sean's own work account — but **captures
are employer content and must never be committed to this personal workspace**. Both fixtures
are therefore synthetic and say so in a `_note` field, and the skill, the CLI help and the
close-out SKIP text all say "write captures to your scratchpad."

## 5. Wiring

`close-out-dispatch` figma row (two bare SKIPs → SKIP for capture + **CLI** for assess), the
harness quality lane (22 gates), CI (self-test plus both fixtures, asserting the violation
fixture *fails*), `figma` hub step 7, five Layer-0 routes, and a rewritten negative fixture.
The old `test_figma_is_honest_skip` asserted the pre-A8 world; it is now
`test_figma_splits_capture_from_assess` and asserts **both** halves, so neither can quietly
regress — a scripted "capture" would be a lie, and a skipped assess is the gap A8 closed.

## 6. What is NOT verified — the live capture

**The probe has never been fed real MCP output.** The capture contract is derived from the
documented shapes of `get_variable_defs` (a name→value map, certain) and `get_metadata`
(XML of layer types/names, documented), not from observed responses. Parsing is deliberately
tolerant and `metadata_xml` degrades to "nothing verified" rather than to a false pass, but
tolerance is not evidence.

This is precisely the "plausible substitute" `mission-fit` warns about, so it is recorded as
an open gap rather than rounded up to done. Closing it needs one Figma node URL and one run —
after which the capture contract either holds or gets corrected against reality.

Until then the honest status is: **rules correct against doctrine, refusals exercised against
planted defects, input contract unproven against the live tool.**

## 7. State

22 harness gates green · connections 8/8 · token budgets met · 43/43 negative fixtures ·
48/48 matcher cases · 14/14 trajectories · ruff clean.
