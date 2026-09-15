---
title: A8 — the Figma construction gate becomes a detector; capture and assess split honestly
version: "1.0"
date: 2026-09-15
surface: Claude Opus 5 + Claude Code (Mac desktop app)
sha: 71f8d7a
status: applied — validated on three live nodes; R2's premise demonstrated, not assumed
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

## 4. Where captures live — and a rule I got wrong first

Captures belong in the scratchpad: they are large, one-off and file-specific, while a fixture
should be small, stable and legible. The shipped fixtures are synthetic for that reason.

I initially justified this as **wall 3** — "captures are employer content, never commit them
here". That is wrong, and worth recording because a wrong rule written into a skill gets
followed later. Wall 3 is one-directional: *employer repos never receive personal-workspace
content, and workspace content is never pasted into employer surfaces.* It says nothing about
employer design data living in this vault, which demonstrably does — the CDS file key, token
names and hex values are already tracked across `07-projects/02-centricPLM`,
`09-figma-repo-sync-plugin`, `project-context-detail.md` and the session-log archive, by
design. Corrected in the probe docstring, its `--emit-template` help, the `figma` hub step 7,
and the close-out SKIP text.

## 5. Wiring

`close-out-dispatch` figma row (two bare SKIPs → SKIP for capture + **CLI** for assess), the
harness quality lane (22 gates), CI (self-test plus both fixtures, asserting the violation
fixture *fails*), `figma` hub step 7, five Layer-0 routes, and a rewritten negative fixture.
The old `test_figma_is_honest_skip` asserted the pre-A8 world; it is now
`test_figma_splits_capture_from_assess` and asserts **both** halves, so neither can quietly
regress — a scripted "capture" would be a lie, and a skipped assess is the gap A8 closed.

## 6. Live validation — and the two things it corrected

The probe was fed a real component set from an employer design-system file (read-only;
the capture lives in a scratchpad and is deliberately not in this repo). It ran end to end,
and it corrected the capture contract in two places that fixtures could never have caught:

**`get_metadata` has no paint data, and types are element TAGS.** Real output is
`<frame …><symbol …/></frame>` — `id`, `name`, `x`, `y`, `width`, `height`, and nothing
else. The first version keyed off a `type="RECTANGLE" fill="#fff"` attribute shape that
Figma never emits, so its R3-from-metadata path **could not fire on real output at all** —
and a self-test asserted it worked, using that invented shape. R3 now judges a raw shape by
its position in the tree: top-level chrome fails; the same shape inside an instance is that
component's own internals (icon vectors are legitimate) and is left alone.

**`get_variable_defs` carries the R2 signal, and the probe was not reading it.** The map is
*mixed*, three kinds of key:

| Key shape | Meaning |
|---|---|
| `<family>/<name>` (a slash or hyphen path) | bound Figma variable |
| `var(--icon-size)` | bound CSS variable reference |
| `fontSize`, `gap`, `height`, `radius` | **the resolved literal of an UNBOUND property** |

The third kind is exactly what R2 exists to refuse, and it is visible nowhere else. Before
this correction the probe would have reported *"R1 and R3 verified, 0 violations"* on a
component carrying eight unbound properties — **a false pass**, which is the single worst
outcome for a prove-gate.

One further fragility surfaced while fixing it: the first discriminator was "a token has a
`/`", which would have flagged doctrine's own hyphenated spellings (`space-0`,
`radius-none`, `border-width-0`) as violations. The rule is now "a token has a separator";
bare and camelCase property names are the unbound ones. A self-test pins both directions.

**Residual uncertainty, stated:** if Figma reports a bare key for a property bound to a
*style* rather than a variable, R2 would over-fire there. Nothing in the observed output
suggests it does, and the reasoned `allow` list is the escape hatch — but this is inference
from one file, not a proof.

## 6a. Two nodes, and the false positive that rebuilt R2

**Node 1 — a component set (30 variables).** R1 clean: no `Color/*` anywhere, so the hard
gate does not over-fire on real production work. R3 clean: every child a variant symbol.
R2: **eight unbound properties** — height, padding, gap, radius, focus-ring radius, font
size, line height, weight. Exactly the families the Density standing rule names, on a
control, while tokens for them exist in the same file.

**Node 2 — a composed overlay (38 variables), probed specifically to test for over-fire.**
It found one, immediately. The separator-based discriminator flagged `foreground` — a **real
single-word semantic token**, sitting among `surface/popover` and `chrome/border/subtle`,
with a `var(--sem-muted-foreground)` CSS twin. Flagging it would have told a designer to
"bind" something already bound.

The rule was backwards. Three attempts:

| Discriminator | Fails on |
|---|---|
| "a token has a `/`" | doctrine's own `space-0`, `radius-none`, `border-width-0` |
| "a token has a separator" | a real single-word token, `foreground` |
| **"the key names a Figma/CSS property"** | — holds on both nodes |

Token names are unbounded and system-specific; **property names are a closed, stable set**.
Keying on the open set was the error. The tell was in the live data all along: node 1 was
full of bound fills and produced **no colour-valued bare key** — every bare key was a
property name.

After the rebuild: node 2 reports **1** hit (down from 2), node 1 still reports **8**
(unchanged). Precision improved without weakening detection, which is the only version of
that trade worth taking.

**The one remaining hit, settled by a third node.** A raw variable-font weight axis (`wght`)
appeared on every node while named weight tokens existed in the file. The open question was
whether Figma merely echoes a resolved axis for bound text — which would make it a false
positive. It does not, and a natural experiment across the three nodes proves it.

*The direct evidence.* A 15px focus-ring radius appears in node 1 as the **bare property**
`radiusRing: 15` with no focus-ring token anywhere in its map, and in node 3 as the **token**
`focus-ring-radius/md: 15` with no bare key. One concept, one value, two nodes — bare where
unbound, token where bound. If bare keys were echoes of bound properties, node 3 would show
both. It shows one. **R2's premise is demonstrated rather than assumed.**

*Applied to `wght`:*

| Node | `wght` | weight tokens in that node's map | could it be an echo? |
|---|---|---|---|
| 1 | 400 | `font-weight/medium: 500` | **no** — no 400 token to echo |
| 2 | 461 | `medium: 500`, `semibold: 600` | **no** — no 461 token to echo |
| 3 | 400 | `medium: 500`, `semibold: 600`, `normal: 400` | coincidence |

Nodes 1 and 2 decide it: `wght` carries values no token in their own map could be echoing, so
it is an independently-set raw axis. Node 3's agreement with `font-weight/normal` is just 400
being Regular. The likely cause is worth naming — the `ligature/*` entries show this file uses
variable **icon** fonts, which carry their own `wght` axis; `var(--icon-size)` is bound and the
icon weight axis is not, which also explains node 2's otherwise odd `461`.

*Also confirmed on node 3:* the rebuilt property-name discriminator holds — `foreground`
passes, and the Figma-only construction tokens (`Day/top-left` and siblings, sanctioned by
doctrine rule 0) pass as tokens. And the probe correctly reported `verified: R1, R2` only,
because no metadata was supplied: it declined to claim R3 rather than implying a clean tree.

R3 also gained live vocabulary: real trees use `symbol` / `instance` / `slot` / `frame` /
`text`, and a `slot` inside an instance must not reset instance context or every icon vector
inside a composed overlay would be flagged. Pinned by self-test.

## 7. State

22 harness gates green · connections 8/8 · token budgets met · 43/43 negative fixtures ·
48/48 matcher cases · 14/14 trajectories · ruff clean.
