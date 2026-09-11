---
title: Workspace automation review — scripts vs LLM judgment
version: "1.0"
date: 2026-09-11
surface: Cursor + workspace-core
sha: 8b1b12f
status: map-only — numbered recs A1–A10 mint, R1–R3 refuse; nothing applied
companion: harness-map_v2.0_2026-09-11.md
---

# Workspace automation review v1.0 — 2026-09-11

**Read-only map.** Do not mint until Sean approves numbers. Decision rule (written first):

> If adding script X means the next cold agent on another device can **refuse a false done** or **skip a 400-line skill**, mint X. If both branches are “the model tries harder,” do not mint.

Same-model critique is not a detector ([[agentic-error-correction-foundations]]). Nightly must not invent skills ([[nightly-maintenance-recipe]]). Photoreal/#12 is the attach template — copy the *done-gate*, not the GPU toolkit.

Canvas: `07-projects/19-workspace-brain/canvases/workspace-automation-review.canvas.tsx` (live compile is Cursor-local).

## 1. What already automates (keep)

| Job | Machinery |
|---|---|
| Skill graph | `build-related.py` → `build-registry.py` → `build-trigger-routes.py` |
| Write-quality | `validate-integrity.py` · `validate-links.py` · `validate-workspace.py` · `validate-capabilities.py` |
| Detector honesty | `test-validators.py` · `vqa calibrate` |
| Layer 0 | `prompt_route.py` · `evaluate-skill-routing.py` (43 fixtures) |
| Layer 1 | `vault-retrieve.py` |
| Visual prove | `vqa prove/capture/compare/motion` |
| Multi-agent | `intent-run.py` |
| Off-system CSS | `09-tools/eslint-off-system/` (product repos, not this vault) |
| Nightly (opt-in, **not enabled**) | fold → vault-health report → rebuild chain |

GitHub CI today: workspace-integrity, validator-fixtures, registry-drift, link-validator, capability-validator.

**Do not rebuild these as skills.**

## 2. Coverage that scripts should police

Live registry 2026-09-11: **299** skills, **47** hubs (all have triggers — rec 3 applied), **33/47 hubs** have empty `governed_by`, **130/185 spokes** silent triggers, `rigor_role` set on **35** skills, `requires` on **26**.

`governed_by` is still navigational: `prompt_route.py` does not load it after produce. Close-out injection (cd63d99) is the current attach. A script that **names the detector** is the next mechanical step.

## 3. Numbered recommendations

Approve by number. Nothing below has been applied.

| # | Disposition | Change | Risk if skipped | Rollback |
|---|---|---|---|---|
| **A1** | **Turn into check** | `09-tools/skill-loadset.py` — utterance → ordered `SKILL.md` paths (`load_chains`). | Agents ingest the 55k registry or guess. | Delete the script; AGENTS algorithm remains. |
| **A2** | **Turn into check** | Hub L3 coverage CI: command hubs must name a detector (`requires`, toolkit in chain, or `rigor_role: measurement`). | #13 “audit without L3 is critique” stays a checklist. | Revert the check; keep #13 prose. |
| **A3** | **Turn into check** | `close-out-dispatch.py` — hub/domain → one command (vqa / integrity / honest skip); non-zero exit. | Injected close-out is still hope the model opens the skill. | Delete; keep SKILL.md. |
| **A4** | **Turn into check** | `09-tools/nightly.sh` wrapping the existing recipe. **Do not enable cron** until you say so. | Agents re-read markdown instead of running one entrypoint. | Delete the wrapper. |
| **A5** | **Turn into check** | Ruff on `09-tools/` in CI only (not a vault runtime dep). | Automation layer can rot while it polices everything else. | Drop the workflow job. |
| **A6** | **Turn into check** | Secret scan (gitleaks or detect-secrets) on tracked files. | Personal vault leak is irreversible. | Drop the workflow. |
| **A7** | **Turn into check** | JSON Schema for `trigger-routes.json`, `knowledge-hints.json`, routing cases. | Malformed Layer 0 fail-opens to `{}`. | Drop schema job. |
| **A8** | **Capability mint** | Smallest Figma bind probe: semantic + mode tokens, instances not rects. MCP inspect; no GPU clone. | Construction doctrine stays unenforced. | Delete the probe. |
| **A9** | **Turn into check** | Analysis reports: `VERIFIED` requires named detector + decision-rule fields ([[experiment-validity-baseline]]). | PM/DS hubs ship narrative as evidence. | Drop the lint. |
| **A10** | **Keep** (session-end, not CI) | `cursor-externalize.py` already exists. GitHub cannot see `~/.cursor`. Do not fake it in GHA. | Canvases stay laptop-local if session-end is skipped. | n/a |
| **R1** | **Refuse** | No promptfoo / LLM-as-judge merge gate. | Flaky “quality” scores that cannot refuse. | n/a |
| **R2** | **Refuse** | No cloned `vqa` toolkit per hub. Replicate *intent* (type → fonttools; eng → tests; PM → pre-registration). | Token bomb + wrong construct. | n/a |
| **R3** | **Refuse** | No pasting close-out into 47 hubs or SessionStart `_INDEX` ingest. | Recreates the 70k read-order miss. | n/a |

Suggested first wave: **A1, A2, A3, A6, A7**. A8 on the next Figma produce that cannot refuse `Color/*`. A4 wrapper without enabling nightly. A5 after A1–A3 if the script layer is growing.

## 4. Synthesis + field practice (why these, not others)

- Frost / #18: steel curtain = CI, axe, evals — not LLM-as-judge.
- #13 Domain Rigor Stack: L3 is scripts/harnesses, not judgment prose.
- #06 + close-out: capture → assess → correct; mint missing detectors.
- Nate Jones: proof + diet; do not preload catalogs.
- 2026 agent harness writing: `init` / `test-all` / `review` as executable gates; the agent never self-certifies. Trajectory fixtures (`evaluate-skill-routing`) beat golden-prose evals. Extend that corpus; do not add promptfoo on the hot path.

## 5. Explicit non-goals this pass

Windows Layer 0 hook install (machine layer, not a vault script). ChatGPT/Grok paste pack (already `web-session.md`). Employer-repo CI (centric-engineering profile — no auto-push of these checks into `c8/*`).
