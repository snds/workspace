---
type: feedback
description: Every PR whose change is visual commits its A/B before/after/heatmap evidence into the PR and embeds it — review happens in the PR, not by pulling the branch
created: 2026-07-21
confidence: high
---

**Any PR whose change is visual — tokens, primitives, spacing, layout, colour, a component's
rendered output — ships its A/B visual evidence _inside the PR_.** Not a metrics line, not a
description: the actual **before / after / change-heatmap** for the affected screens, plus an
overview board embedded in the PR body, with the per-screen full-resolution comparisons committed
so they render in the diff. The reviewer sees what changed and judges intended-vs-unintended
without pulling the branch or running anything.

**Why:** This is the [[05-validation-harness]] Proofboard principle — _show-me evidence_ — applied
to visual work. "SSIM 0.997" is not a review; a designer or reviewer needs to **see** the
comparison. Committing the evidence makes the PR self-contained and the visual judgment
reproducible by anyone with repo access. It extends framework [[06-qa-operating-model]]'s show-me
gate to the visual layer, and the captures themselves follow [[10-perception-integrity]] (judge at
native resolution, never downsampled). Sean made this a standing rule after seeing a token-migration
PR that carried only a metrics table.

**How to apply:**
- Build a deterministic A/B harness once (freeze non-determinism — pinned clock, no random/relative
  time; native-resolution capture). The `visual-qa-toolkit` / `native-visual-eval` stack covers the
  diff side (SSIM · %pixels-changed · ΔE · `before|after|heatmap` triptych).
- Capture **before** (the baseline git ref) and **after** (the change); diff every screen.
- Commit a curated set — an overview **board** + the representative per-screen triptychs — to a
  **tracked evidence path** in the repo (e.g. `qa/evidence/<phase>/`; gitignore the rest of the
  capture output). **Embed the board in the PR body**; keep the metrics table beside it.
- Triage every flagged change **Intended / Unintended / Ambiguous**; unintended blocks the PR.
- Practical constraint: the `gh` CLI can't upload to GitHub's markdown-image CDN, so **committing**
  the evidence (not web drag-drop) is the reliable automated path. Keep it curated — baselines stay
  *reproduced from a ref via the capture script*, never stored; only the review evidence is committed.

**Applies across surfaces and profiles** (personal + employer). On employer repos it rides the
normal branch → PR → review flow; the evidence just makes the visual review real. Do not let a
visual PR go up "evidence-later."
