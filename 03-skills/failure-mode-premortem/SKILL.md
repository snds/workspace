---
name: failure-mode-premortem
description: >
  Anticipatory failure analysis — the input-time discipline that finds visual bugs BEFORE they ship,
  not after Sean spots them. Use BEFORE proposing or implementing any technique with a visible failure
  surface (shader, post-process chain, volumetric, dither, material, tonemapper, bloom, procedural
  generator, particle system, motion curve, layout, color treatment) and AGAIN at the done-boundary
  before claiming "complete / ready for review / matches the reference." The core sequence: name the
  technique → consult the Visual Failure-Mode Ledger for its classic failure modes (write the entry if
  none exists) → argue AGAINST your own plan (oppositional / red-team pass, pros and cons of the
  scenarios others have hit) → derive plain-English visual acceptance criteria from the reference/article
  figures using machine vision → build → prove the result against those criteria at native resolution.
  This is the METHOD behind framework #11 Anticipatory Failure Analysis. It converts reactive "that's a
  classic symptom" (said after the artifact appears) into proactive detection (caught before the code is
  written). Trigger on: "before we build this," "what could go wrong," "will this have banding/artifacts,"
  a linked reference article or concept plate, "is this ready for review," reviewing a rendering approach,
  or any moment about to reach for a visual technique. Pairs with `native-visual-eval` (native capture),
  `visual-qa-toolkit` (measurement), and `lead-visual-qa` (judgment). Standalone: does NOT require the
  visual-QA hub.
aliases: [failure-mode-premortem, visual-pre-mortem, anticipatory-failure-analysis, render-premortem]
triggers: [pre-mortem, premortem, failure mode, what could go wrong, before we build, red team, oppositional, classic symptom, common issue, avoidable, will this band, acceptance criteria, reference comparison, ready for review, pitfall ledger, anticipate bugs, find the bug first]
tier: cross-cutting
domain: quality
related: [native-visual-eval, visual-qa-toolkit, lead-visual-qa, reference-video-review]
surfaces: ["*"]
spec_version: "1.0"
---

# Failure-Mode Pre-Mortem

**The directive: before reaching for any technique with a visible failure surface, name it, look up how it
classically fails, argue against your own plan, and derive from the reference what "correct" looks like —
*then* build, and prove the result against those criteria at native resolution before calling it done.
Find the bug before Sean does.**

This is the method behind framework [#11 Anticipatory Failure Analysis](../../01-frameworks/11-anticipatory-failure-analysis.md).
Load it on its own — it carries no hub dependency. Its memory is the
[Visual Failure-Mode Ledger](../../08-knowledge/cross-domain/visual-failure-mode-ledger.md).

---

## Why (the failure mode this prevents)

The knowledge that "volumetrics band under a tonemapper" or "dither crawls under camera motion" lives in
latent memory that is retrieved **by symptom** — you show me the banding, I recall the cause. That is why
it always surfaces *after* the artifact is visible, as a post-hoc "classic symptom." The pre-mortem forces
the same knowledge to be retrieved **by technique-name at planning time**, and externalizes it into a
ledger so retrieval doesn't depend on recall at all. A failure anticipated is a bug that never ships.

---

## The sequence

### 1 · Name the technique
Say it out loud, specifically, including the pipeline it sits in — the pipeline is where most visual
failures actually live. "Raymarched volumetric glow, composited through an ACES tonemapper at 8-bit
output" — not "add a glow."

### 2 · Consult the ledger
Open the [Visual Failure-Mode Ledger](../../08-knowledge/cross-domain/visual-failure-mode-ledger.md) and
pull every row whose technique or pipeline stage matches. Each row gives you: symptom · visible tell ·
root cause · prevention · **how to detect it in a frame** · reference.

**If there is no matching row:** research the technique's failure modes now (article + prior art, per
framework #04 Research & Evidence), and **write the entry before proceeding**. This is how the ledger
grows. Cite the source and name the confidence tier.

### 3 · Oppositional pass — argue against your own plan
Red-team the approach before writing it:
- Which ledger failure modes does my *current* plan walk straight into?
- What will Sean see at native resolution that looks wrong — banding, rings, crawl, energy loss,
  posterization, aliasing, haloing, seams, colour shift?
- What are the pros and cons of the scenarios others have hit with this technique? (Not the happy path.)

Then **troubleshoot the plan to dodge them** — change the render target precision, add blue-noise dither
before quantize, increase march steps, jitter the sample origin, move the operation before/after tonemap,
whatever the ledger's *prevention* column prescribes. This is the "meet the expected outcome" step: the
build starts already hardened against its known failures.

### 4 · Derive acceptance criteria from the reference (machine vision)
If a reference, article, concept plate, docs page, or prior art is in play, its **figures are ground
truth**:
- Fetch it (`WebFetch` the article; or native-resolution browser capture of the figure region; or read a
  local plate). Extract the reference image(s).
- Read them at native resolution (per `native-visual-eval` — a downsampled figure hides the very detail
  you're contracting on).
- Translate what you see into a **short list of plain-English, falsifiable criteria** — what *correct*
  looks like:
  - "Glow falloff is a smooth radial ramp — no concentric steps."
  - "Emissive bloom has a soft threshold — no hard ring at the emitter edge."
  - "Planet terminator is a smooth day→night gradient — no stair-stepping."
- If **no** reference exists, say so explicitly and derive criteria from the ledger's *visible tell* /
  *how-to-detect* columns instead — never substitute unstated personal taste for a missing reference.

### 5 · Build
Implement the hardened plan from step 3, targeting the criteria from step 4.

### 6 · Prove it at the done-boundary
Before "complete / ready for review":
- Capture the produced result at **native resolution** (`native-visual-eval` — state the pixel dimensions).
- Compare against each derived criterion **and** each matching ledger detection method. Use
  `visual-qa-toolkit` for SSIM / ΔE / edge maps where a numeric comparison against the reference helps.
- Mark each criterion **met / not-met**. Any not-met item is surfaced as next-pass scope, never buried.
- The criteria list + before/after native crops **are the Proofboard** — Sean verifies the visual against
  the reference without reading the shader.

---

## The verification gate (say #1 out loud)

1. **Pre-mortem run + output named** — technique, ledger row(s) consulted or written, criteria derived.
2. **Acceptance check stated at native resolution** — pixel dimensions judged at, each criterion met/not-met.
3. **Unmet criteria surfaced as next-pass scope** — honest partial beats generous "looks good."

No pre-mortem output to state → the claim of "ready" isn't verified.

---

## Feeding the ledger (the self-improving loop)

- **Sean caught a visual bug you missed?** Write a ledger row for it at session-end — that exact "classic
  symptom" is now proactive for next time.
- **Researched a new technique in step 2?** Its entry is a side effect of the pre-mortem — commit it.
- The ledger accretes from ordinary work; no separate documentation pass required.

---

## Pairing

Capture native first (`native-visual-eval`) → measure (`visual-qa-toolkit`) → judge (`lead-visual-qa`),
framed by the target user (#06). This skill is what runs *before* all of them (steps 1–4) and what closes
the loop *after* them (step 6). It is the operational teeth of framework #11.
