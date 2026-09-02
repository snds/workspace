# Shape — lock the fidelity plan

Plan before code. Vague "make it photoreal" dies here.

## Preconditions

Contracts exist (`init`). Load framework #12 + #10. Read current `RENDER.md` / `BUDGET.md` / `NORTHSTAR.md`.

## Steps

1. **Fidelity contract.** Check Literal / Spirit / Standard / Intent in `RENDER.md`. Default bar: movie-level northstar-gated. Write the one-sentence contract.
2. **Northstar set.** Fill `NORTHSTAR.md` with concrete stills, videos (timestamps), and game/engine ceilings. Reject adjective-only refs. Add anti-references.
3. **Technique ladder.** Pick the cheapest rung that can satisfy the contract. State the cheat and what higher rungs buy. Note tonemap / bloom / TAA order.
4. **Budget envelope.** Allocate planned ms per pass in `BUDGET.md` before any new look work. Reserve headroom. Name release valves.
5. **Official poses + paths.** Define ≥3 still poses and ≥1 flythrough covering move, look, roll, zoom/scale, plus project stresses (LOD, origin shift, approach). Write IDs into `RENDER.md`.
6. **Acceptance cues.** Translate northstar into falsifiable plain-English still + motion cues in `NORTHSTAR.md`.
7. **Present and stop.** Show the shape brief (contract, refs, ladder, budget, poses/paths, cues). Wait for confirm / override before `craft`.

## Shape brief (output)

```
## Shape: {target}
- Contract: …
- Northstars: S.. / V.. / G..
- Ladder rung: … (cheat: …)
- Budget envelope: … ms total planned @ floor
- Poses: P.. · Paths: F..
- Still cues: …
- Motion cues: …
Confirm, override, or course-correct.
```

## Reject at shape time

- No named northstar assets
- Budget TBD / "we'll see"
- Motion-sensitive feature with zero flythrough path
- Early-Z-killing depth defaults proposed without justification

## Next

Confirmed → `harden` (pre) then `craft`. Unconfirmed → revise; do not code.
