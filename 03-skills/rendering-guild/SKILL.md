---
name: rendering-guild
description: >
  Multi-agent rendering deliberation guild (arch-guild pattern) for realtime photoreal decisions.
  Convene when choosing technique rungs, resolving look-vs-budget conflicts, reviewing lighting /
  material / shadow / shader / camera-motion proposals, or closing a harden-done gate. Agents:
  Light TD, Material TD, Shadow TD, Perf Engineer, Shader Architect, Camera/Motion TD, Art Director,
  Validator. Verdicts APPROVE / CONCERN / OBJECTION / BLOCK. Modes: Methodology (inline), Quick,
  Focus, Full. Validator always closes with measurable still + motion + budget criteria. Triggers:
  rendering guild, convene guild, light review board, look vs budget, photoreal deliberation.
aliases: [rendering-guild]
triggers: [rendering guild, convene guild, render guild, light td, material td, shadow td, look vs budget, photoreal deliberation, guild review render, validator criteria]
tier: cross-cutting
domain: game
related: [realtime-visual-craft, visual-qa-photoreal-rendering, realtime-render-performance, imaging-foundations, failure-mode-premortem, interactive-capture-eval, native-visual-eval, lead-visual-qa]
surfaces: ["*"]
spec_version: "2.0"
---

# Rendering Guild

System-level **photoreal rendering** deliberation using the arch-guild pattern. Orthogonal agents
pressure a proposal before it ships. Framework [#12](../../01-frameworks/12-realtime-photoreal-operational-framework.md)
is the doctrine; this skill is the multi-lens review ritual.

Load with [[realtime-visual-craft]] contracts (`RENDER.md` / `BUDGET.md` / `NORTHSTAR.md`) when they exist.

---

## The Guild

### Standing agents (every Quick / Full review)

| Agent | Core question |
|---|---|
| **Light TD** | Is the lighting energy story coherent (key/fill/bounce/sky) without conservation cheats? |
| **Material TD** | Do albedo/spec/roughness responses read under the contract (Fresnel, metals, dielectrics)? |
| **Shadow TD** | Contact, cascades, acne, peter-pan, motion swimming — what fails? |
| **Perf Engineer** | What does this cost in worst-frame ms? Does it defend the 60 FPS floor and latency? |
| **Shader Architect** | Is the technique the right rung? Pass order, precision, early-Z, TAA coupling sound? |
| **Camera / Motion TD** | What breaks under move/look/roll/zoom/LOD/origin? Still-only proof rejected? |
| **Art Director** | Does it match the northstar contract (Literal/Spirit/Intent) aesthetically? |
| **Validator** | How do we **measure** still + motion + budget success? (always last) |

### Focus domains (Focus mode)

| Domain | Agents |
|---|---|
| `lighting` | Light TD, Material TD, Art Director, Validator |
| `shadows` | Shadow TD, Light TD, Perf Engineer, Validator |
| `materials` | Material TD, Shader Architect, Art Director, Validator |
| `performance` | Perf Engineer, Shader Architect, Light TD, Validator |
| `motion` | Camera/Motion TD, Shader Architect, Perf Engineer, Validator |
| `match` | Art Director, Light TD, Camera/Motion TD, Validator |

---

## Guild modes

| Mode | Agents | Trigger |
|---|---|---|
| **Methodology** | None summoned (reason inline with guild questions) | Skill loads; default |
| **Quick** | All standing agents | "quick rendering guild" / "quick guild review" |
| **Focus** | 3–4 from a focus domain (+ Validator always) | "focus guild on lighting\|shadows\|…" |
| **Full** | All standing agents, deeper rationales + ledger pass | "convene full rendering guild" |

Validator is **mandatory** in Quick, Focus, and Full.

---

## Review process

1. Present the proposal (technique, contract citation, budget line, northstar IDs).
2. Agents evaluate from orthogonal seats; surface dissent explicitly.
3. Map findings to framework #12 bans and the Visual Failure-Mode Ledger where relevant.
4. Consensus label: APPROVED / CONCERNS / BLOCKED.
5. **Validator closes** with measurable still + motion + budget criteria (mandatory).

---

## Verdicts

Each agent produces one of:

- **APPROVE** — no concerns from this seat
- **CONCERN** — minor issues; acceptable short-term with named follow-up
- **OBJECTION** — significant issues; must address before ship
- **BLOCK** — fundamental conflict with contract, physics craft, or frame floor

---

## Output format

```
## Rendering Guild: {Topic}

### Agents
- Light TD: {VERDICT} — {rationale}
- Material TD: {VERDICT} — {rationale}
- Shadow TD: {VERDICT} — {rationale}
- Perf Engineer: {VERDICT} — {rationale}
- Shader Architect: {VERDICT} — {rationale}
- Camera/Motion TD: {VERDICT} — {rationale}
- Art Director: {VERDICT} — {rationale}

### Consensus
{APPROVED | BLOCKED by X, Y | CONCERNS from Z}

### Blocking Concerns (if any)
1. {Agent}: {concern}

### Recommendation
{Action to take — rung change, valve, capture path, doc update}

### Validation Criteria (Validator) — mandatory
Still:
- {Native pose/tile criterion — dims + cue}
Motion:
- {Path ID + frame-by-frame cue; or explicit N/A only if camera/interaction not in claim}
Budget:
- {Worst-frame / pass ms at pose + path; harness artifact}
Ban check:
- No low-res verdicts · no still-only close if motion in claim
```

---

## Absolute guild rules

- Art Director may not APPROVE on taste alone without northstar IDs (or an explicit Standard/Intent contract).
- Perf Engineer BLOCKS self-imposed low frame caps that leave FPS/latency on the table without a user setting.
- Camera/Motion TD BLOCKS still-only proof for temporal / LOD / scale features.
- Validator never closes with vibes-only criteria — each criterion must be falsifiable from an artifact.

---

## Pairing

- Ops router → [[realtime-visual-craft]]
- Judgment lens → [[visual-qa-photoreal-rendering]]
- Capture → [[interactive-capture-eval]] · [[native-visual-eval]]
- Cost doctrine → [[realtime-render-performance]]
- Pre-mortem → [[failure-mode-premortem]]

## Related
- peer ↔ [[lead-visual-qa]] · [[realtime-visual-craft]] · [[visual-qa-photoreal-rendering]] · [[realtime-render-performance]] · [[imaging-foundations]] · [[failure-mode-premortem]] · [[interactive-capture-eval]] · [[native-visual-eval]] · [[lead-game-developer]] · [[render-qa-toolkit]]
