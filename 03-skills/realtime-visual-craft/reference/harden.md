# Harden — pre-mortem and done-boundary

Two modes, same skill: **pre** (before build) and **done** (before "ready").

## Mode A — Pre (before craft)

Load [[failure-mode-premortem]] + Visual Failure-Mode Ledger + framework #11.

1. Name each new technique + pipeline stage (e.g. "raymarched atmosphere → ACES → 8-bit").
2. Pull ledger rows; write missing entries before proceeding.
3. Oppositional pass: which classic failures does this plan walk into?
4. Derive / refresh acceptance cues in `NORTHSTAR.md` from refs + ledger detection methods.
5. Adjust the plan (precision, dither, sample counts, pass order) **before** coding.

Do not start `craft` without a named pre-mortem output.

## Mode B — Done (triple gate)

All three required:

| Gate | Proof |
|---|---|
| **A Still** | Native captures; 1:1 grid tiles assessed; cues met/not-met |
| **B Motion** | Official paths recorded; frame-by-frame review; stress frames dense-sampled |
| **C Budget** | Measured worst-frame / pass ms at poses **and** paths |

Also:

- State pixel dimensions judged
- No verdict from thumbnail / fit-to-window / lossy preview
- Unmet cues listed as next-pass scope (honest partial > fake complete)
- Camera/interaction in the claim → motion gate cannot be skipped

## Verification (say out loud)

1. Pre-mortem named (or N/A with reason for pure non-visual change)
2. Triple gate artifacts cited
3. Unmet items surfaced

No artifacts → the claim of "ready" is unverified.

## Next

Pre → `craft`. Done fail → targeted `craft` / `optimize`. Done pass → optional `polish`.
