---
tags: [workspace, harness, load-order, token-frugality, agent-miss]
created: 2026-09-11
updated: 2026-09-11
status: working
confidence: high
sources: [AGENTS.md, 03-skills/skills.registry.json, 02-shared-references/trigger-routes.json, 09-tools/prompt_route.py, 01-frameworks/00-README.md]
related_skills: [harness-map, workspace-bootstrap, plan-ahead, mission-fit]
related_projects: [19-workspace-brain]
relations:
  builds-on: ["[[nate-jones-harness-enrichments]]", "[[workspace-infrastructure]]", "[[knowledge-vault-design]]"]
  relates-to: ["[[multi-session-workspace-resilience]]"]
---

# Agent load-miss review — what a cold LLM never sees

## For future agent

- **TL;DR:** Important process is usually *in the vault*. The miss is **routing**: Layer 0 is a hook plus a hope. Recs **1–15** applied 2026-09-11 with process-rigor **R1–R16** (close-out attach). Produce-followthrough (2026-09-11): Cursor `beforeSubmitPrompt` + Claude `UserPromptSubmit` inject close-out/self-improve on produce language, and a visible miss on work verbs with zero Layer-0 hits. That closes the “didn’t find the skill” class **on hooked surfaces**. It does **not** force the model to obey, and it does not reach Perplexity / ChatGPT / Grok.com / Windows-without-hook. A cold agent that only follows always-on files still needs Layer 0; AGENTS read-order now says lookup `load_chains`, not ingest the registry.
- **As of:** 2026-09-11 · **Status:** recs 1–15 applied; produce-followthrough landed same day. Numbered dispositions live in [[harness-map_v2.0_2026-09-11]].
- **Key claims:** silent hubs (empty `triggers`) are invisible to `prompt_route.py`; description-fallback is documented in AGENTS and unimplemented; `component` burns the Figma generate stack; `prompt_route.py` is gitignore-allowlisted (clones can run it); Work MBP has `beforeSubmitPrompt`; Windows / loaner / web LLMs still miss the hook. Injection ≠ compliance.

## Target user and bar

**User.** Any cold LLM agent (Claude, GPT, Grok, Cursor, Perplexity) plus Sean checking their work on another model.

**Bar.** Important process is findable and followed at acceptable token cost. Missing a steel curtain or a dual-repo order-of-operations is a fail. Loading 2,400 lines because the prompt said "design system" is also a fail.

**Surface this run.** Workspace core + Cursor on Work MBP. GitHub-only and Perplexity are `INACCESSIBLE` for hooks.

## Four miss types

| Type | Meaning |
|---|---|
| **MISS** | Cold agent never sees it unless the user names the file or a Layer-0 phrase hits |
| **TOKEN TAX** | Always-on or always-instructed load that is fatter than the value |
| **DUPLICATE HOME** | Same law in 2+ files; the agent can pick the weaker copy |
| **INACCESSIBLE** | Exists on this machine or this surface only |

## Highest-leverage misses (ranked)

1. **Silent hubs.** 34/47 hubs have `triggers: []` (`qa`, `ds`, `motion`, `type`, `lead-ui-designer`, `lead-ux-designer`, `lead-frontend-engineer`, `ds-generation-pipeline`, …). Spec says hubs must have triggers. AGENTS says "fallback: match description." `prompt_route.py` does not. Grade: `VERIFIED`.
2. **AGENTS read order vs token diet.** Steps 3–5 ingest registry + `trigger-routes.md` + `_INDEX.md` (~70k tokens) if followed literally. Hooks load JSON + caps. Grade: `VERIFIED` (files) / `INFERRED` (whether a given model obeys).
3. **`design system` bomb.** Curated route loads #18 + #09 (717 lines) + `ds-advisor` (887) + `design-engineer`. `component` / `variant` / `mockup` alias the entire Figma generate stack — wrong process for an audit. Grade: `VERIFIED`.
4. **Layer 0 is not portable to every LLM.** `09-tools/prompt_route.py` is gitignore-allowlisted. Cursor `beforeSubmitPrompt` is installed on Work MBP (`CS-K746DRWXY1`) and injects produce-followthrough + visible miss. Windows / loaner pending per [[fact-machine-layer-installs]]. Perplexity / GPT.com / Grok.com get nothing automatic — paste [[tool-adapter-discovery]] `web-session.md` + BEACON. Gemini CLI / Copilot Chat / Warp / Aider / Windsurf now have thin native-filename pointers at `AGENTS.md`. Injection ≠ compliance. Grade: `VERIFIED`.
5. **#18 is routed, not contracted.** Frost DS×AI is in `trigger-routes.json` on Frost phrases. AGENTS doctrine list names #17 as **intent coordination**, not DS×AI. A hookless agent never opens #18. Grade: `VERIFIED`.
6. **Knowledge and memory dark matter.** `knowledge-hints.json` covers 12 unique files. `_INDEX` has ~71 entries. Memory has **zero** Layer-0 keys. Three memory files and four knowledge notes were untracked on this machine at review time. Grade: `VERIFIED`.
7. **Plugin `figma-use` beats workspace doctrine** unless Layer-0 fires. Workspace `figma` hub has no `defers_to`. Lone `"figma"` fails the 2-token gate. Grade: `VERIFIED` (structure) / `INFERRED` (runtime plugin order).
8. **Gitignore project allowlist.** Most `07-projects/` SESSION-STATE never reaches GitHub. Intentional. A GitHub-only agent has stubs, not Live handoff. Grade: `VERIFIED`.

## What actually works

- Curated keys for QA (`audit`/`review`), Frost phrases (`steel curtain`, `vibe coding`, `brad frost`), plan-ahead (`cds then proto`, `pages build`), and a11y FOUNDATION_ROUTE.
- Produce-followthrough: `build this in figma` / `implement this` / work-verb+hub-hit inject close-out then self-improve on hooked surfaces. `make the primary button blue` injects **Layer 0 missed**, not `{}`.
- Registry `load_chains` is the cheap graph — **if** the agent looks up a name instead of ingesting the file.
- Framework #18 exists beside #09; `ai-design-systems` is the procedure spoke. Do not duplicate the mortar/stool/steel-curtain envelope into a third L1.

## Numbering collision (this merge)

Origin claimed **#17** for Intent Coordination (2026-09-04) and **`07-projects/21-shadegraph`**. Local Frost work had used both numbers. After rebase: Intent stays #17; Frost DS×AI is **#18**; course notes are **`22-ai-design-systems-course`**. Fetch before claiming the next integer.

## Do not do next

Do not "fix the vault" in the same turn. Harness-map: map before clean. Approve numbered recs in the v2.0 report.

Full map: `07-projects/19-workspace-brain/reports/harness-map_v2.0_2026-09-11.md`.

Companion (process that exists but does not run): [[process-rigor-gaps]] · recs **R1–R16**. Load-miss recs **1–15** are not replaced.
