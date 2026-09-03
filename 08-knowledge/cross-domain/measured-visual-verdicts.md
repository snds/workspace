---
tags: [cross-domain, visual, machine-vision, qa, verification, knowledge-vault]
created: 2026-08-26
updated: 2026-08-26
status: validated
confidence: high
sources: [visual-prove-engine build + calibration 2026-08-26, LCARS S-SYS47-01 re-prove, agentic-error-correction-foundations]
related_skills: [visual-prove-engine, visual-reference-replication, visual-qa-toolkit, lead-visual-qa, native-visual-eval]
related_projects: [20-lcars-generative-interface, 19-workspace-brain]
domain_agnostic: true
---

# For future agent

**TL;DR:** A visual verdict is only trustworthy if (1) every counted cue was measured by an
instrumented probe, never declared; (2) cue thresholds were derived from the reference, never
from the build; (3) the detectors themselves passed a planted-defect calibration with zero
misses and zero false fires; and (4) the improvement ledger reports newly failing cues even
when the aggregate score rose. All four were violated by the manual pipeline this replaced,
and each violation was caught on real project data the day the engine ran.

# Measured visual verdicts

Operational home: [[visual-prove-engine]] (`03-skills/visual-prove-engine/vqa.py`).
Diagnosis that motivated it: [[visual-reference-replication-findings]]. Verification
theory: [[agentic-error-correction-foundations]] (independent measurement is the
correction primitive; same-model narrative self-critique is not).

## Validated claims

1. **Self-attested cue matrices drift into fiction.** The LCARS S-SYS47-01 manual matrix
   claimed 15/16 pass. Under measurement (same cues, probes instead of prose): 13/16,
   and one claimed pass was flatly false. The silhouette chip row said "pass (in footer
   plate)"; the engine measured 0.0 foreground fraction in the zone and the native crop
   is pure black. Nobody lied; a plate mount changed and no instrument ever re-looked.

2. **Thresholds must come from scouting the reference with the same probes that will
   judge the build.** The manual matrix demanded MSD SSIM >= 0.85 against the asset
   plate, but the reference itself only scores 0.338 in that rect formulation (framing
   and letterbox differences). An unattainable threshold gets waived in prose ("pass*,
   toolkit not run"), which is how attestation creep starts. Scout first, then set the
   contract relative to measured reality, and record the derivation in the cuespec
   `_provenance` field.

3. **Detector reliability is a measured property, not a design intention.** The
   calibration suite (planted defects + known-good + noise-only variants, all 32 cases
   must resolve correctly) caught four real engine bugs before any real image was judged:
   a banding scorer that flagged normal 8-bit quantization in shallow gradients, a gutter
   probe that read anti-aliased edge blur as content, phantom jerk from centroid jitter at
   an animation's settle tail (change masks decay into slivers; gate trajectory points on
   area relative to peak, default 10 percent), and global SSIM/delta-E being too weak to
   see small local defects over full-canvas AA noise (compare region-local, not global).

4. **Aggregate improvement hides local regressions unless the ledger is cue-granular.**
   v2 to v3 improved 0.50 to 0.81 with 7 cues newly passing, but 2 cues that v2
   satisfied newly fail in v3. `movement: improved` with a `newly_failing` flag is the
   honest shape; a bare score delta would have buried it.

5. **Rank agreement is a cheap external validity check.** The engine's closeness ranking
   (mean of SSIM and inverted delta-E after phase-correlation registration) independently
   agreed with the human judgment that v3 beats v2. When measured ranking and human
   ranking disagree, investigate before trusting either.

6. **Provenance is part of the verdict.** A capture without a manifest (viewport, DPR,
   freeze state) reports `unverified` even when all cues pass, because an unpinned
   capture can pass by accident (wrong DPR smooths a defect) or fail by accident
   (font fallback shifts a scanline).

## Anti-patterns this entry exists to stop

- Writing per-project prove scripts whose cues contain `pass: True` literals.
- Setting a metric threshold from what the current build achieves.
- Claiming detector coverage ("the engine checks banding") without a planted-defect case
  proving the check fires, and a clean case proving it stays quiet.
- Reporting a single improvement score without per-cue movement.
- Treating a VLM's description of a screenshot as measurement (it is testimony;
  see [[component-contracts-and-schemas]] on testimony vs contract).
- Claiming a docs or catalog prove that only passed with extra rails on (chunks, lint, MCP). Isolation is [[agent-output-rails]].
- Claiming a docs or catalog prove that only passed with extra rails on (chunks, lint, MCP). Isolation is [[agent-output-rails]].

## Related
- [[visual-failure-mode-ledger]] carries the technique-keyed failure rows the perceive
  detectors implement (banding, blowout, illegal shapes C-08/C-09).
- [[silent-degradation-in-fenced-layers]] is the same lesson for non-visual pipelines:
  a fence that degrades silently erases the difference between healthy-empty and broken.
- [[agent-output-rails]] is the same lesson for agent rails: assistance can hide that the docs failed.
