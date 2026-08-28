---
name: play-prove
description: >
  Headless simulation and balance prove (altitude G). Use when the question is
  whether a game or interactive system plays fairly and diversely — win-rate,
  no dominant strategy, score moments, input-to-photon is a sibling motion
  check — not whether a screenshot matches. Trigger on: play-prove, headless
  playtest, win-rate gate, dominant strategy, balance simulation, AutoSim,
  MCTS playtest, simulation prove. Do NOT use for pixel/Literal UI (visual-prove-engine),
  render beauty, or VLM "does this look fun" judgments. A screenshot cannot
  prove feel.
aliases: [play-prove]
triggers: [play-prove, headless playtest, win-rate, dominant strategy, balance simulation, autosim, mcts playtest, simulation prove, playtest agent]
tier: spoke
domain: game
hub: lead-game-designer
related: [visual-prove-engine, visual-qa-motion, realtime-render-performance]
governed_by: []
rigor_role: measurement
surfaces: ["*"]
spec_version: "2.2"
---

# Play Prove

Altitude G of the [[perception-critique-stack]]: did the system play, and did
it play fairly? This is a sibling of [[visual-prove-engine]], not a `vqa`
subcommand. Cameras, SSIM, and VLMs pollute balance numbers.

## Contract

1. Author a `play-prove/1` spec with an **adapter command** that already ran
   the simulation (math model preferred when physics/render would dominate).
2. `python3 03-skills/play-prove/playprove.py prove SPEC.json` asserts
   `win_rate`, `avg`/`stddev`, and `no_dominant_strategy` against adapter JSON.
3. Adapter failure is an **error**, never a pass.
4. Pixel `vqa prove` / `vqa interact` remain the visual gates. This CLI does
   not look at frames.

## Done-gate

- Adapter emitted the named metrics.
- Every assertion in the spec passed.
- Strategy share max ≤ `max_share` when `no_dominant_strategy` is present.
- Report names altitude G so it cannot be mistaken for a Literal matches.

## Refuse / degrade

- Do not accept a VLM playtest transcript as this contract.
- Do not accept a screenshot prove as feel.
- Do not invent win-rate from one human session.
- If the adapter cannot run, stop and say so.

## Related
- hub → [[lead-game-designer]]
- peer ↔ [[visual-prove-engine]]
