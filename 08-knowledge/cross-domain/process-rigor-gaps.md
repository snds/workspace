---
tags: [workspace, rigor, close-out, qa, figma, engineering, token-frugality]
created: 2026-09-11
updated: 2026-09-24
status: working
confidence: high
sources: [01-frameworks/13-domain-rigor-stack.md, 03-skills/skills.registry.json, 02-shared-references/delivery-playbooks/05-validation-harness.md, 03-skills/plan-ahead/SKILL.md]
related_skills: [harness-map, plan-ahead, qa, figma, eng, mission-fit, failure-mode-premortem, close-out, self-improve]
related_projects: [19-workspace-brain]
relations:
  builds-on: ["[[agent-load-miss-review]]", "[[nate-jones-harness-enrichments]]"]
  relates-to: ["[[workspace-infrastructure]]", "[[self-improving-workspace]]"]
---

# Process rigor gaps — whole workspace

## For future agent

- **TL;DR:** The missing rigor is not more essays. Doctrine without a load edge does not attach. First-wave attach (2026-09-11): `skill-loadset.py` computes the load set; `close-out-dispatch.py --run` is the named L3 after produce; `--check` covers command hubs; Layer 0 JSON and secret scan refuse in CI. Do not paste a 40-line close-out into every SKILL.md. Human review of visual/LLM work is **not** a standing stop: if a detector is missing, mint it and push; page Sean only when the agent cannot be critical of its own work or that mint still cannot make QA usable.
- **As of:** 2026-09-11 · **Status:** recs **R1–R16** applied with load-miss 1–15; close-out interrupt policy (page Sean iff self-critique or QA rigor fails) landed the same day. Report: `07-projects/19-workspace-brain/reports/process-rigor-gaps_v1.0_2026-09-11.md`.
- **Sean's examples are instances, not the map:** coded order-of-operations, Figma construction, hub self-test + human visual QA. The same failure (doctrine without a load edge) hits analysis, a11y, motion, type, security-as-sideways, context-profile, Proofboard, and #07 reviewability.

## Target user and bar

**User.** Sean as designer-of-designers, plus any cold agent he will cross-check.

**Bar.** An agent finishes a hub's work only when: (1) it followed an order of operations that names the first later-breaker, (2) domain L3 actually ran or was honestly skipped, (3) it did not use verified/done language without a named detector, (4) it **captured, assessed, and corrected** with named CV / visual-code QA — minting a missing detector and pushing it here rather than paging Sean — and interrupts **only** if it cannot be critical of its own work or that mint still cannot hit the accuracy/perf bar. Leave-the-building (publish / employer merge / spend) stays human.

## The pattern (all clusters)

#13 already requires L1–L5. Instantiation on disk:

| Cluster | L1 exists | L2 findable | L3 runs | Close-out + human stop |
|---|---|---|---|---|
| UI/UX / DS | #02 #09 #18 | `ds-advisor` yes; `/ds` `/qa` **silent** | inspection scorecards rarely attached | No |
| Figma | #09 + authoring knowledge | Hub on GitHub has **no `triggers:` key**; prose still says load vendor `figma-use` first | No bind/instance machine check | Protocol steps 1–7 have no VQA stop |
| Engineering | #14 | `/eng` has triggers; `lead-frontend/backend/devops` **silent** | CI exists in repos, not invoked by the hub | Proofboard is a playbook, not a ship verb |
| Integration | #07 | No Layer-0 key for PR/merge/rebase | Author-owns-drift is prose | No |
| QA / visual | #06 #10 | **`qa` and `lead-visual-qa` silent** | toolkit + prove-engine exist | Human stop is one bullet in #06, not a hub step |
| Motion / Type / Graphic | #02 | `/motion` `/type` `/redesign` **silent** | `/qa --lens` never loads | No |
| Accessibility | #02 + toolkit | `lead-accessibility-architect` **silent** | `a11y-audit-toolkit` exists | Not sideways on Figma/code output |
| Security | #16 | `lead-security-architect` **has triggers** | scanners via `requires` | Only 3 spokes `governed_by` sec |
| Analysis / PM | #15 | both leads **silent** | experiment-validity knowledge, not a runner | Proofboard mentioned, not loaded |
| Photoreal / game | #12 | `realtime-visual-craft` **has triggers** — best instantiated | render-qa + #11 | Closest to the bar; still not a template copied elsewhere |
| Intent | #17 | `intent-coordination` + `intent-run.py` | gate/ready/verify | Not used for ordinary single-agent delivery |
| Workspace | #08 | validators + harness-map | integrity/links/workspace | Not a close-out of *product* work |
| Career / Adobe / Vision / Science | thin / none | mixed | checklists | Honest INCOMPLETE per #13 — do not fake L3 |
| Context / intent | `00-context-profiles.md`, #06, #15, #16 | Phrase `context profile` only; `audit`/`review` loads #06 file not `/qa` | CREATE never attaches JUDGE | Profile, target user, decision owner, and `done` are optional manners |

## Connective protocols (one home each)

1. **Close-out** — after produce: self-test → named detector → #06 honesty → capture/assess/correct. Missing detector → **capability mint** (smallest skill/tool, calibrate, independent workspace push). **Interrupt Sean iff** self-critique is failing or mint still cannot hit the accuracy/perf bar.
2. **Plan-ahead (general)** — not only cds/proto. Fetch, CI-contract vs local overlay, merge-conflict files, generated artifacts, first later-breaker. #07 stacking is the PR-shaped instance.
3. **Figma prove-gate** — instances not rects; semantic+mode binds not `Color/*`; variant matrix; native-zoom capture; correct and re-prove. Mint a missing inspect/cuespec before paging.
4. **Graph attach** — `governed_by` on producer hubs; real `triggers` on command wrappers; `governs` populated on `qa` / a11y / visual-qa.
5. **Self-improve** — per-session correct / heal / improve for the whole vault, not only QA detectors. Transfer processes across hubs (adapt, don't clone toolkits). Wire corollary edges. Push independently. Home: [[self-improve]]. Map: [[self-improving-workspace]].
6. **New detector ≠ reviewed detector** (2026-09-24) — the session-end auto-commit lands work on `main` without review, and the local validator chain omits ruff (CI-only by `ruff.toml` design). Before pushing a new/changed `09-tools/*.py`: `UV_CACHE_DIR=$TMPDIR/uv-cache UV_TOOL_DIR=$TMPDIR/uv-tools uvx ruff check <file>` (the temp dirs are needed under the sandbox). For a new L3 detector, run an adversarial review (finders → refuters → fix → re-verify) and calibrate on real data: `token-audit.py` shipped an F541 only CI caught, then 31 confirmed defects + 7 fix-introduced regressions surfaced ([[design-token-architecture]]).

Load-miss map: [[agent-load-miss-review]]. Proofboard: [[05-validation-harness]].
