# Budget — measure the frame

Numbers close the third gate. FPS-counter vibes do not.

## Preconditions

`BUDGET.md` exists with planned allocation. Official poses/paths in `RENDER.md`. Load [[realtime-render-performance]].

## Steps

1. **Instrument.** Prefer harness JSON (`?perfcapture` or project equivalent), GPU timestamp queries where available, CPU timers as fallback. Record build/preset.
2. **Measure poses.** Worst-frame and/or per-pass ms at each P-ID. Judge **worst**, not average.
3. **Measure flythroughs.** Sample along F-IDs; capture spikes at LOD, origin shift, heavy views. A pose-only green with path spikes is a fail.
4. **Write results.** Update Measured columns in `BUDGET.md`. Attach artifact paths.
5. **Compare to envelope.** Over budget → name the pass and the release valve (DRS, cascade cut, GI rate…). Do not silently gut a northstar cue.
6. **Latency note.** If interaction feels laggy at "good FPS," flag input-to-photon separately (sample late, frames-in-flight).

## Report shape

```
## Budget: {target}
Floor: 60 FPS · real GPU budget: ~X ms
Poses: {table}
Paths: {worst ms, spike locations}
Over budget: {pass} → valve: …
Look impact of valve: …
```

## Fail immediately

- "We're fine, the counter says 60" with no worst-frame / path data
- Optimizing before a baseline measurement
- Cutting fidelity without updating `NORTHSTAR.md` / contract

## Next

Green budget + pending look → `match` / `audit`. Over budget → `optimize` with explicit look tradeoffs, then re-measure.
