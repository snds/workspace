# Match — northstar delta

Prove Literal or Spirit match against **named** stills and video frames. Adjectives are not references.

## Preconditions

`NORTHSTAR.md` filled. Capture evidence at native res. Load [[reference-video-review]], [[native-visual-eval]], [[visual-qa-photoreal-rendering]].

## Steps

1. **Select refs.** Pick the S-/V-IDs that the claim cites. State match type per ref.
2. **Align views.** Match camera language as closely as the medium allows (FOV, lighting direction, time of day, subject scale). Note irreducible medium gaps.
3. **Still match.** Side-by-side native crops / 1:1 tiles. Score each acceptance cue: met / not-met. Use measurement tools when numeric deltas help; do not hide behind SSIM alone.
4. **Motion match.** Extract northstar key frames and capture frames at analogous moments. Compare temporal behavior (stability, energy under move), not just a paused pretty frame.
5. **Delta report.** For each not-met cue: what differs, likely cause class (light / material / post / temporal / budget cheat), suggested fix rung.
6. **Verdict.** `Matches contract` only if still **and** (when claimed) motion cues pass. Partial match lists remaining gaps as next-pass scope.

## Output shape

```
## Match: {target} vs {ref IDs}
Type: Literal | Spirit
Still: {cues met/not-met}
Motion: {cues met/not-met | n/a with reason}
Medium gaps (accepted): …
Blockers: …
```

## Reject

- Matching against a moodboard never written into `NORTHSTAR.md`
- Declaring Spirit match without stating which cues were allowed to diverge
- Single-frame match for a flythrough claim

## Next

Gaps → `craft` / `audit`. Full match + budget green → `harden` (done).
