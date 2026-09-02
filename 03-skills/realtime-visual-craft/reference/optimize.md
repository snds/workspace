# Optimize — cut cost, keep the contract

Performance work that silently drops northstar cues is a regression, not a win.

## Preconditions

Baseline `budget` numbers exist. Fidelity contract + northstar cues known. Load [[realtime-render-performance]].

## Steps

1. **Name the hotspot.** Which pass / view / path spike? Cite measurement artifact.
2. **Pick a release valve** from `BUDGET.md` order (DRS → shadows → GI rate → volumetrics → post…). State the **look impact** before changing code.
3. **Preserve contract cues.** If a valve would break a Literal/Spirit cue, escalate: change the cue with user approval, or pick a different valve, or raise the hardware floor.
4. **Implement one valve.** Re-measure poses **and** flythroughs.
5. **Re-prove look.** Native still grid + motion spot-check on the affected views. Run a light `audit` on known failure tells for that valve (e.g. DRS → aliasing; shadow cut → acne/seams; GI rate → temporal pump).
6. **Update docs.** Measured ms, valve chosen, any accepted look delta in `BUDGET.md` / `NORTHSTAR.md`.

## Rules

- 60 FPS floor remains; optimize to defend worst frame
- Uncapped default stays; optional user cap is not a substitute for fixing the hotspot
- No fragment log-depth "optimization" that kills early-Z as a casual default
- Optimize after fidelity holds when possible; if blocked on ship, keep look deltas explicit

## Output shape

```
## Optimize: {hotspot}
Before → after (worst ms): …
Valve: … · look impact: …
Still re-check: …
Motion re-check: …
Contract status: held / cue waived ({id})
```

## Next

Still over budget → next valve. Green → `harden` (done) re-affirm or `polish`.
