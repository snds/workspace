---
title: Feedback — ALIGNED vs DEVIATE for cross-surface tokens
created: 2026-08-05
---

# Feedback — ALIGNED status for cross-surface tokens

When comparing Figma ↔ code (or similar surfaces):

1. Compare **resolved values and reference pipelines** (alias / `var()` chains). Prefer
   structural agreement of refs when designer/engineering experience allows.
2. If **intent and visual outcome match** but the technical form cannot (e.g. Figma
   `radius/full` = 9999px vs Tailwind `rounded-full`), status is **ALIGNED**, not
   DEVIATE / MATCH. Never say “no parity” when intent is shared.
3. Prefer true technical MATCH when possible; lean ALIGNED when the surface constraint
   is the only gap.

Canonical note: `08-knowledge/design/cross-surface-token-parity.md`.
