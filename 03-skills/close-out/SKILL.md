---
name: close-out
description: >
  After any hub produces, run the four-step done-gate: self-test, self-validate
  (named detector or honest skip), self-confirm (#06 honesty), then stop for
  human visual QA or a Proofboard. Use when the user says "close-out",
  "self-police", "prove-gate", "human visual qa", "named detector", or when a
  command hub (/qa /figma /ds /eng /motion /type /redesign) finishes producing.
  Do not paste this body into other skills — hubs invoke it. Photoreal/#12 is
  the attach template; do not cargo-cult GPU scripts into other domains.
aliases: [close-out]
triggers: [close-out, self-police, prove-gate, human visual qa, named detector]
tier: cross-cutting
domain: workspace
related: [qa, plan-ahead, mission-fit, eng, figma, failure-mode-premortem]
surfaces: ["*"]
spec_version: "2.2"
---

# Close-out — self-police, then stop for Sean

One home for "looks good." Command hubs **invoke** this; they do not copy it.

Doctrine homes (pointer, not restatement): [[06-qa-operating-model]] honesty ·
[[mission-fit]] false `done` · [[05-validation-harness|Proofboard]] ·
[[14-engineering-operating-model]] verify · [[11-anticipatory-failure-analysis]] ·
[[plan-ahead]] sequence.

## When to use

After `/qa` `/ds` `/figma` `/eng` `/motion` `/type` `/redesign` (or any hub that
produced an artifact). After analysis/PM claims. Not for a question with no write.

## The four steps

1. **Self-test** — run the domain L3 you already have (toolkit, CI, bind inspect,
   contrast). If the hub never captured evidence, say so; `visual-qa-toolkit`
   will not hunt screenshots.
2. **Self-validate** — name the detector (`vqa prove`, axe/contrast, Pages
   `cds-exports-check`, variable bind inspect, `validate-integrity`). Honest skip
   beats a fake pass.
3. **Self-confirm** — #06: no `verified`/`done` language without that detector.
   Resolve the [context profile](../../02-shared-references/delivery-playbooks/00-context-profiles.md)
   if a repo or product file was touched.
4. **Human stop** — visual work: native-zoom screenshot, Sean looks. Code-heavy
   work: name or build the Proofboard. The agent is never the sole witness.

## Figma prove-gate (when `/figma` or design-engineer produced canvas)

Binary (MCP/inspect): fills/strokes bound to semantic + mode tokens — refuse
`Color/*` on components; controls are library or `local/…` instances, not
rectangles; variant matrix complete. Then native-zoom screenshot and **stop**.

## When NOT to use

- Photoreal/#12 already has a named done-gate — do not clone GPU toolkits here.
- Intent #17 / `intent-run.py` stays N-agent. This skill is the single-agent case.
- Cargo-cult SSIM onto a threat model or a career checklist.

## Related
- peer ↔ [[qa]] · [[plan-ahead]] · [[mission-fit]] · [[eng]] · [[figma]]
