---
name: close-out
description: >
  After any hub produces, run the QA loop: self-test, named detector (or honest
  skip), #06 honesty, then capture → assess → correct. If rigor is unusable
  because a detector is missing, mint the smallest QA method/skill/tool, calibrate
  it, re-prove, and push it to this workspace independently. Prompt Sean only if
  self-critique is failing or that mint still cannot hit the accuracy/perf bar.
  Use when the user says "close-out", "self-police", "prove-gate", "human visual
  qa", "named detector", "llm qa", "capability mint", or when a command hub
  finishes producing. Do not paste this body into other skills. Photoreal/#12 is
  the attach template; do not cargo-cult GPU scripts into other domains.
aliases: [close-out]
triggers: [close-out, self-police, prove-gate, human visual qa, named detector, llm qa, capability mint]
tier: cross-cutting
domain: workspace
related: [qa, plan-ahead, mission-fit, eng, figma, failure-mode-premortem, visual-prove-engine, vision-foundations, visual-qa-toolkit, native-visual-eval, self-improve]
surfaces: ["*"]
spec_version: "2.5"
---

# Close-out — run the QA loop; page Sean only when it cannot

One home for "looks good." Command hubs **invoke** this; they do not copy it.

Doctrine homes (pointer, not restatement): [[06-qa-operating-model]] honesty ·
[[mission-fit]] false `done` · [[05-validation-harness|Proofboard]] ·
[[14-engineering-operating-model]] verify · [[11-anticipatory-failure-analysis]] ·
[[plan-ahead]] sequence.

Sean is not the default last step. After produce, the agent must **capture,
assess, and correct** using computer vision and visual/code QA. If that loop
fails because **the detector does not exist** (or cannot hit the accuracy/perf
bar), mint the missing QA capability, re-run the loop, and push it here — do
not wait. Prompt him **only if** (a) you cannot be sufficiently critical of
your own work, or (b) the mint still cannot make the QA process usable.

Leave-the-building (external publish, employer merge, spend, delete) stays
[[mission-fit]] — this skill does not waive that. Never push this mint path
into employer (`c8/*`) repos.

## When to use

After `/qa` `/ds` `/figma` `/eng` `/motion` `/type` `/redesign` (or any hub that
produced an artifact). After analysis/PM claims. Not for a question with no write.

## The four steps

1. **Self-test** — run the domain L3 you already have (toolkit, CI, bind inspect,
   contrast). If the hub never captured evidence, say so; `visual-qa-toolkit`
   will not hunt screenshots.
2. **Self-validate** — run `python3 09-tools/close-out-dispatch.py --from-prompt "<user prompt>" --run`
   first. That CLI is the named-detector table (command-hub L3). Exit 0 is not
   verified for SKIP classes; exit 2 is honest skip only. Then name any extra
   detector the table could not run (`vqa prove`, axe/contrast, Pages
   `cds-exports-check`, MCP bind inspect). Honest skip beats a fake pass.
3. **Self-confirm** — #06: no `verified`/`done` language without that detector.
   Resolve the [context profile](../../02-shared-references/delivery-playbooks/00-context-profiles.md)
   if a repo or product file was touched.
4. **Interrupt test** — if rigor is unusable from a **capability gap**, run
   **Capability mint** first. Page Sean **only** when the test below still
   fails. Otherwise report the detector + the fix loop and do not wait.

## Interrupt test (page Sean iff)

Page him if **either** is still true **after** mint (when mint applies):

- **Self-critique failing** — you would over-grade; you cannot refute your own
  findings; the only check is same-model "looks good"; a VLM caption is being
  treated as a measured pass ([[vision-foundations]]: critique ≠ audit).
  **Do not mint a skill to launder this.**
- **QA rigor still unusable** — mint was skipped, refused, or ran and still
  cannot capture/assess/correct to the accuracy and performance bar.

All three legs are required for usable QA: **capture** (native pixels or MCP
node inspect) → **assess** (named, calibrated detector) → **correct** (fix,
recapture, reassess until pass or cannot-fix). A finding list without a fix is
not usable rigor.

Per-class, not all-or-nothing. Receipt: waived classes (detector + re-prove)
vs minted classes (new detector + SHA) vs interrupted classes (why mint missed).

Code-heavy work that cannot close the loop: name or build the Proofboard, then
mint or interrupt. Do not invent a visual pass from CI logs.

## Capability mint (unusable rigor → build the detector)

Fires only for a **missing or under-performing detector**, not for honesty
failure. Goal: accuracy **and** performance good enough that the LLM QA loop
is usable in this session.

1. **Name the gap** — defect class, which leg failed (capture / assess /
   correct), accuracy bar, perf budget (seconds, not a GPU farm).
2. **Extend first** — search existing L3 (`visual-qa-toolkit` check, `vqa.py`
   probe, MCP inspect in `/figma`, CI fixture, knowledge method). Do not add a
   hub. Do not clone photoreal/#12.
3. **Mint the smallest layer** per [[workspace-ontology]] +
   [[08-workspace-contribution-framework]]:
   - procedure → extend a skill or add `08-knowledge`
   - script → `09-tools/` + a **negative fixture** (`test-validators.py` and/or
     `vqa calibrate` planted defect)
   - reusable when-X-do-Y → spoke under an existing hub from
     `00-bootstrap/templates/skill.md` (frontmatter, real `triggers`,
     `governed_by` if it produces visuals)
4. **Calibrate** — planted defect must fire; clean fixture must not. A mint
   without a failing fixture is unusable rigor.
5. **Rebuild** — `build-related.py` → `build-registry.py` →
   `build-trigger-routes.py` → integrity / links / workspace / routing
   fixtures. Registry is generated; never hand-edit it.
6. **Re-prove** the original artifact with the new detector (capture → assess
   → correct).
7. **Push independently** if it now meets the bar — this workspace is
   `personal-solo`: commit + push here without waiting. Report detector name +
   SHA. Never `--no-verify`, never force-push, never employer repos.
8. **Then interrupt** only if the bar still misses. Include the gap, what was
   minted, and why.

Hair-trigger skills that steal routing, a detector whose only job is "looks
good", or a mint that fails CI are not a pass.

Non-detector vault gaps (missed route, transferable process, corollary edge,
research-worthy skillset) → invoke [[self-improve]]. Do not grow this file.

## Figma prove-gate (when `/figma` or design-engineer produced canvas)

Loop until pass or interrupt:

1. **Capture** — MCP inspect (fills/strokes/instances/variant matrix) **and** a
   native-zoom screenshot of the authored node (`get_screenshot` on the node,
   subject filling the frame — not the page thumbnail).
2. **Assess** — construction (binary): fills/strokes bound to semantic + mode
   tokens — refuse `Color/*` on components; controls are library or `local/…`
   instances, not rectangles; variant matrix complete. Pixels: `vqa prove` /
   toolkit when a reference or cuespec exists. Load `a11y-visual` (contrast/CVD).
   Screenshot-as-VLM-caption is critique, not a detector.
3. **Correct** — rebind, replace rects with instances, complete the matrix,
   nudge; recapture; reassess. Cannot-fix (missing token, MCP write rejected,
   DS gap) → interrupt with the finding, do not hide it.
4. **Mint or interrupt** — missing cuespec / inspect / pixel probe for a class
   → Capability mint, then re-prove. Page Sean only if mint cannot close that
   class, or self-critique is failing. Construction that passed MCP inspect
   after a fix does **not** page him. Publishing/sharing a library is
   leave-the-building, not this waiver.

## When NOT to use

- Photoreal/#12 already has a named done-gate — do not clone GPU toolkits here.
- Intent #17 / `intent-run.py` stays N-agent. This skill is the single-agent case.
- Cargo-cult SSIM onto a threat model or a career checklist.

## Related
- peer ↔ [[qa]] · [[plan-ahead]] · [[mission-fit]] · [[eng]] · [[figma]] · [[self-improve]]
