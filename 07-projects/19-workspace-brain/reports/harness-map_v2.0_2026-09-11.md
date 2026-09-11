---
title: Harness map — agent load-miss (workspace core + Cursor)
version: 2.0
date: 2026-09-11
surface: Cursor + workspace-core
branch: main
sha: 1f87419
agent: Cursor Grok 4.6
status: map-only — no clean applied
supersedes: harness-map_v1.0_2026-08-07.md
---

# Harness map v2.0 — 2026-09-11

Hub-gated adversarial review: would a cold LLM miss important process, or pay too much to find it?

## 1. Boundary + evidence grades

| Field | Value |
|---|---|
| Workspace root | nearest `AGENTS.md` → `~/Projects/workspace` |
| Branch @ sha | `main` @ `1f87419` (pushed) |
| Surface edition | **Workspace core** + **Cursor** |
| Model | Cursor Grok 4.6 |
| Machine | Work MBP (`CS-K746DRWXY1`) |
| Date | 2026-09-11 |
| Prior map | v1.0 2026-08-07 — several recs applied; this run is a new miss-audit after Frost #18 + 44-commit rebase |

**Evidence-grade legend:** `VERIFIED` · `USER_REPORTED` · `INFERRED` · `INACCESSIBLE` · `NOT_EXPOSED` · `NOT_APPLICABLE`

**This run is read-only.** No always-on edits, no trigger rewrites, no archive. Recs below wait for numbered approval.

**Target user.** Any cold agent (Claude, GPT, Grok, Cursor, Perplexity) + Sean cross-checking on other models.

**Bar.** Process findable and followed at acceptable token cost.

## 2. System map

### Always-on / early load

| Control | Path | Size (approx) | Grade |
|---|---|---|---|
| Universal contract | `AGENTS.md` | ~6.4k tok; read order 1–5 ≈ **78k** if obeyed | `VERIFIED` |
| Claude adapter | `CLAUDE.md` | ~2k tok; forks load list (`CRITICAL_FACTS`) | `VERIFIED` |
| Cursor brain | `.cursor/rules/brain.mdc` `alwaysApply: true` | ~0.9k tok; Brain-first folder only | `VERIFIED` |
| Write gates | `.cursor/rules/01-agent-controller.mdc` | ~0.2k tok | `VERIFIED` |
| Cursor adapter | `CURSOR.md` | docs only, not auto | `VERIFIED` |
| Perplexity adapter | `PERPLEXITY.md` | **forks the contract** (no routes, no #18, session-log append) | `VERIFIED` |
| `llms.txt` | machine entry | names `.md` routes not JSON | `VERIFIED` |
| Hot facts | `06-context/CRITICAL_FACTS.md` | still says **seventeen** frameworks; #17 = intent | `VERIFIED` |
| Cursor prompt-route hook | user-global `beforeSubmitPrompt` | **not** in project `.cursor/hooks.json`; Work MBP pending | `VERIFIED` / `USER_REPORTED` |
| Vendor system prompt | Cursor / Claude product | — | `NOT_EXPOSED` |

This chat's workspace root is `~/Projects` → **mdc rules do not attach.** Fallback: user beacon + User Rules.

### Routed load

| Control | Observation | Grade |
|---|---|---|
| Skill registry | **297** skills after rebase (43 cross-cutting · 22 foundation · 47 hub · 185 spoke) | `VERIFIED` |
| Curated JSON | `trigger-routes.json` — 245 keys after merge; cap **8** unique | `VERIFIED` |
| Knowledge hints | 12 unique files; cap **4** | `VERIFIED` |
| Registry triggers | cap **6**; empty `triggers: []` = invisible | `VERIFIED` |
| Index triggers | `_INDEX.md` cap **4**; Cursor Layer-0 does not load the index file | `VERIFIED` |
| Description fallback | AGENTS claims it; `prompt_route.py` does **not** implement it | `VERIFIED` |
| 2-token gate | prompts with <2 tokens of length ≥4 skip Layer 0 entirely | `VERIFIED` |
| Framework #18 | Frost DS×AI — curated Frost phrases only; **not** in AGENTS doctrine list | `VERIFIED` |
| Framework #17 | Intent coordination — in AGENTS; living-spec / `intent-run.py` | `VERIFIED` |
| Memory | 0 Layer-0 keys | `VERIFIED` |

### Enforcement

Validators + `build-related` → `build-registry` → `build-trigger-routes` remain the write-quality chain. Integrity currently fails on origin's dangling `_PROJECTS.md` → `01-mediaservices/SESSION-STATE` (`VERIFIED`; pre-existing on origin).

`09-tools/prompt_route.py` is the Layer-0 matcher and is **gitignored** (not in the 09-tools allowlist). Remote clone cannot run or read it. `VERIFIED`.

### Authority + done

- Workspace = `personal-solo` (this merge was a direct push after rebase).
- Employer repos = `centric-engineering` (no self-merge).
- Figma vendor plugins = mechanics only; workspace `figma` + `design-engineer` own doctrine — **unenforced** unless Layer-0 fires.

### Receipts

Live handoff: `07-projects/19-workspace-brain/SESSION-STATE.md`. Run map of "what the model actually loaded" is `NOT_EXPOSED` on Cursor.

## 3. Protect vs drag

**Protects.** Portable AGENTS contract; context-profile fail-safe; write-quality validators; curated QA / Frost / plan-ahead / a11y keys; #18 as a real L1 instead of stuffing Frost into `ds-advisor`; gitignore allowlist that keeps employer substance out of GitHub.

**Drag.** Read-order that contradicts token frugality. Silent hubs. `component` = Figma generate. Three copies of contracts (#09 §5a / knowledge / portable schema). `ds-advisor` restates #18 so a skill-first agent can skip the framework. PERPLEXITY.md is still a fork. Stale "seventeen" in CRITICAL_FACTS / `_HOME` anatomy vs eighteen files.

## 4. Numbered recommendations

Approve by number. Nothing below has been applied.

| # | Disposition | Owner | Change | Risk if skipped | Rollback |
|---|---|---|---|---|---|
| **1** | **Load later** | `AGENTS.md` read order | Step 3 = *lookup* `load_chains[name]`, do not ingest the registry. Step 4 = `trigger-routes.json` (or "head"), not the generated `.md`. Step 5 = match `Triggers:` from `_INDEX` without swallowing 8k tok. | Every obedient cold agent burns ~70k before work. | Revert the three sentences. |
| **2** | **Turn into check** | `.gitignore` + `09-tools/` | Allowlist `prompt_route.py`, `cursor-prompt-route.py`, and the Cursor prompt-route shim so GitHub clones have Layer 0. | Remote / other-machine agents have no matcher. | Remove the allowlist lines. |
| **3** | **Turn into check** | hub `SKILL.md` frontmatter | Add real `triggers` to `/qa`, `/ds`, `/motion`, `/type`, `lead-ui-designer`, `lead-ux-designer`, `lead-frontend-engineer`, `lead-visual-qa`, `ds-generation-pipeline` — **or** delete AGENTS' "fallback: match description" sentence. | "qa this screen" never loads `/qa`; "generate a design system" never hits the Frost ban. | Revert frontmatter. |
| **4** | **One home** | `trigger-routes.json` | Stop aliasing `component` / `variant` / `mockup` / `wireframe` to `$FIGMA_GENERATE_ROUTE`. Keep that template on `in figma` / `component set` / `library file`. | Audits pull the generate stack; cap-8 drops #18. | Restore aliases. |
| **5** | **Load later** | `trigger-routes.json` `design system` | Default pair = `#18` + `ds-advisor`. Load #09 only on component-schema / Atomic Design / `DESIGN.md` keys. | Two words cost ~2,300 lines. | Restore bundled #09. |
| **6** | **Keep** (one phrase) | `AGENTS.md` doctrine list | Add **#18 DS×AI** next to existing #17 intent. Do not paste Frost models into the contract. | Hookless agents never hear that Frost is L1. | Delete the phrase. |
| **7** | **One home** | `CRITICAL_FACTS.md`, `_HOME.md` anatomy, `.claude/skills/framework-check` | "seventeen" → **eighteen**; keep #17 = intent, #18 = Frost. | Stale count trains agents to stop at 17. | Revert strings. |
| **8** | **Load later** | `knowledge-hints.json` | Hint the high-value INDEX-only doctrine: `component-contracts-and-schemas`, `enterprise-saas-design-patterns`, `contracts-first-delivery`, `accessibility-beyond-wcag-baseline`, `threat-model-before-controls`, `visual-failure-mode-ledger`. Cap stays 4 — pick fewer, better. | Doctrine stays dark unless `_INDEX` is ingested. | Remove keys. |
| **9** | **Turn into check** | `03-skills/figma/SKILL.md` | `defers_to: [design-engineer]` (and document plugin `figma-use` as L5 mechanics). | Vendor skill wins on Cursor. | Remove frontmatter. |
| **10** | **One home** | `PERPLEXITY.md` | Make it a thin adapter: same read order as AGENTS, no session-log-append fork, no "Claude is privileged." | Perplexity runs a different workspace. | Restore current adapter. |
| **11** | **Keep** | untracked knowledge/memory | When committing prompt-route / charting / opacity WIP, add `_INDEX` + `MEMORY.md` lines in the **same** commit. Do not hint files GitHub cannot fetch. | Layer-0 404s on other machines. | n/a |
| **12** | **Probation** | `ds-advisor` principle 5 vs #09 contracts | "Figma is the knowledge center" vs "Figma is a signatory." Reconcile in `ds-advisor` with a pointer to contracts — do not grow another essay. | Skill-first agents ship the weaker rule. | Revert the sentence. |
| **13** | **Turn into check** | `00-bootstrap` / doctor | Install Cursor `beforeSubmitPrompt` on Work MBP (this machine) + Windows. Memory already says pending. | This surface is beacon-only for employer-repo chats. | Uninstall hook. |
| **14** | **Keep** (process) | contribution / plan-ahead | **Fetch before claiming the next integer.** This merge moved Frost #17→#18 and course 21→22 because origin already used both. | Duplicate numbers, broken wikilinks. | n/a |
| **15** | **Probation** | Claude SessionStart `_INDEX` head-60 | ~5k tok of Design blurbs every Claude boot. Trim or stop injecting. | Recurring Claude-only tax AGENTS does not mention. | Restore head-60. |

Invalid: "delete `ds-advisor` because it is long." Length is not a disposition. Split load, don't punish the hub.

## 5. Explicit gaps

| Item | Grade |
|---|---|
| Cursor vendor system prompt / skill-catalog truncation | `NOT_EXPOSED` |
| Whether this chat's model ingested AGENTS natively | `INFERRED` (root is `~/Projects`) |
| Perplexity / GPT.com / Grok.com / Claude iOS file access | `INACCESSIBLE` |
| Gitignored `07-projects/` Live handoffs (Centric, Legion, CDS audit, …) | `INACCESSIBLE` on GitHub |
| `05-artifacts/` | `INACCESSIBLE` remotely (local-only by design) |
| Nested `design-system-ops/skills/*/SKILL.md` (36 files, not in registry) | `VERIFIED` glob trap |
| `_PROJECTS.md` → missing `01-mediaservices/SESSION-STATE` | `VERIFIED` origin pre-existing integrity fail |

## 6. Suggested verification after any approved change

1. `python3 09-tools/build-related.py && python3 09-tools/build-registry.py && python3 09-tools/build-trigger-routes.py`
2. Validators: integrity → links → workspace → capabilities
3. `python3 09-tools/evaluate-skill-routing.py` if rec **3** or **4** or **5** lands
4. Cold-prompt fixtures: `"audit this design system component"`, `"dark mode palette for this dashboard"`, `"generate a design system"`, `"qa this screenshot"` — record what Layer 0 emits
5. Optional: [[mission-fit]] on one real DS task after the route change

Companion knowledge: [[agent-load-miss-review]].
