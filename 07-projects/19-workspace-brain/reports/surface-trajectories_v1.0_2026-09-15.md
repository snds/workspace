---
title: Per-surface routing trajectories — the Cursor complaint, reproduced and closed
version: "1.0"
date: 2026-09-15
surface: Claude Opus 5 + Claude Code (Mac desktop app)
sha: 7af2428
status: applied — 3 matchers collapsed to 1; 6/48 surface divergences → 0; 14 trajectory cases green
companion: workspace-harness_v1.0_2026-09-15.md
---

# Surface trajectories v1.0 — 2026-09-15

Phase 5 of the review prompt. The harness proved the graph is *traversable*; this proves
each surface *traverses* it. "Cursor didn't find the skill" turned out to be a measurable,
reproducible defect, not a model-quality impression.

---

## 1. The measurement

There were **three independent implementations** of Layer-0 matching:

| Implementation | Used by |
|---|---|
| `09-tools/prompt_route.py` | Cursor, via `cursor-prompt-route.py` |
| `.claude/hooks/dispatcher.py` → `handle_user_prompt` | Claude Code |
| `09-tools/evaluate-skill-routing.py` | the 48 fixtures — *a copy, with a "do not drift" comment* |

The fixtures tested the copy. Neither live surface was under test by anything. Running the
same 48 utterances through both real entry points: **6 divergences (12.5%)** — the same
vault and the same words delivering a different set of files depending on which tool Sean
happened to be in.

Both surfaces were wrong, in opposite directions:

- **Cursor had no Layer-1 lexical fallback.** On a thin-trigger prompt (`qa this screenshot`)
  Claude gap-filled from `vault-retrieve.py` and Cursor returned the bare hub. AGENTS.md
  documents that fallback as part of the contract, so Cursor was non-compliant, not merely
  different. This is the complaint, mechanically.
- **The Claude hook deduped by trigger instead of by target.** When one trigger produced both
  a curated route and a knowledge hint, Claude silently dropped the knowledge entry. On
  `audit this design system component`, Cursor delivered `ai-and-design-systems.md` and Claude
  did not.

## 2. The fix — one matcher, not two that agree

Patching each matcher would have re-created the drift on a slower clock.

1. **Layer 1 ported into `prompt_route.py`** (`lexical_fallback` + `apply_lexical_fallback`),
   so Cursor and every shell surface inherit the fallback the contract promises.
2. **`dispatcher.handle_user_prompt` now delegates** to `prompt_route.route_prompt()`. The
   forked tier machinery is gone.
3. **`evaluate-skill-routing.py` imports `term_matches`** instead of copying it. Three
   implementations → one.

Re-measured across the same 48 utterances: **0 divergences.**

One regression surfaced during the port and is worth keeping in view, because it is the
cost of unification: with Layer 1 shared, a *non-work* utterance with zero hits started
emitting a bare "routing skip" note on both surfaces at once. Suppressed by a general rule —
a payload consisting only of parenthetical status notes is noise — which preserves the
visible miss for work verbs, where `followthrough_lines` contributes a real line. Before the
unification that bug would have hit one surface and gone unnoticed; now it hits both and two
fixtures catch it. That is the trade, and it is the right one.

## 3. `09-tools/evaluate-surface-trajectories.py`

Runs the command each surface really invokes, and asserts what lands in context.

| Surface | Entry point | Kind |
|---|---|---|
| `claude-code` | `.claude/hooks/dispatcher.py user-prompt` (stdin JSON, `CLAUDE_PROJECT_DIR`) | hook |
| `cursor` | `09-tools/cursor-prompt-route.py` (`beforeSubmitPrompt`) | hook |
| `shell-agent` | `09-tools/skill-loadset.py --json` | CLI — Gemini CLI, Warp, Aider, generic MCP |
| `hookless` | none — web ChatGPT / Grok / Perplexity | adapter file asserted statically |

Per case: `expect_paths`, `forbid_paths`, `expect_header`, `expect_empty`, and **`parity`** —
the two hook surfaces must deliver an identical path set, since they now run one matcher and
any divergence means the unification regressed.

Two guards the fixtures alone cannot give:

- **One-matcher structural guard.** `handle_user_prompt` must name `prompt_route` and must not
  re-declare `TIER_CAPS[` or `_registry_trigger_hits(`. Fixtures catch drift for utterances in
  the corpus; this catches the *shape* that caused it, for every utterance.
- **Hookless adapter check.** A surface with no hook gets only what its adapter file says, so
  every adapter must name `AGENTS.md`. Nothing executable can help there.

`--self-test` plants a divergence between two stub surfaces and asserts parity fails on it —
the parity check is the centerpiece, so it does not get to be assumed.
`--utterance "…"` prints what every surface delivers for one prompt, with a parity verdict.

**14 cases** covering: hub-before-vendor (figma), foundation-first chain, the lexical
fallback, knowledge-hint survival, produce → close-out, order-of-operations, a visible miss,
greeting silence, chatter silence, stopword over-fire safety, vault-edit routing, and two
shell-agent trajectories.

## 4. Attach points

CI (`--self-test` then `--check`), the `workspace-harness` quality lane (now 17 gates), the
AGENTS.md enforcement chain, the `self-improve` close-out row, and five Layer-0 routes
(`surface parity`, `cursor missed`, `what does cursor see`, …).

## 5. What this does and does not prove

It proves that for these 14 utterances every surface receives the same context, and that the
architecture which allowed divergence is gone. It does **not** prove a model *reads* what it
receives — injection is not compliance, as AGENTS.md already says. Closing that gap needs
outcome evidence from real sessions, not a static fixture, and nothing here attempts it.

Coverage is 14 trajectory cases against 48 matcher cases. The matcher corpus is the breadth;
trajectories are the delivery proof. Grow trajectories when a surface is added or a delivery
bug is found — not by mirroring every matcher case, which would pay the subprocess cost for
no new information.
