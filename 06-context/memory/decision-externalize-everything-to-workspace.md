---
type: decision
description: All durable content lives in the workspace (or the platform Projects dir) — never in an agent's private memory
created: 2026-06-30
confidence: high
---

**Directive (standing, set by Sean 2026-06-30).** Nothing durable lives inside any single agent's
private/internal memory. Every learning, insight, workflow, decision, project context, and asset
routes to the **workspace** (this git checkout) at its correct layer, or — for actual code/working
files — to the platform-relative `Projects` directory. The only thing an agent keeps internally is a
*pointer* back to the workspace.

**Why.** The workspace is portable, git-native, and surface/device/LLM-agnostic ([[decision-portable-workspace-refactor]]).
Anything stored in a vendor- or surface-specific memory (Claude Code's `.claude/.../memory`, a Chat
profile, a Design session) is invisible to every other surface and agent, can't be versioned or
reviewed, and silently drifts from the shared source of truth. Externalizing everything is what makes
"near-identical results across Claude Code, Claude Chat, Claude Design, Cursor, Perplexity, and any
future agent" actually hold. Private memory is also where the high-signal, hard-won detail was getting
stranded — exactly the content that most needs to be shared and durable.

**Routing (the layers — see [[workspace-ontology]] for the full map):**
- Durable, non-project fact about Sean's world / a structural decision → `06-context/memory/`.
- Active project state / pending work → `06-context/project-context.md` + the project's
  `07-projects/NN-*/SESSION-STATE.md`. Project-specific insights/guidance that aren't code → the
  project folder under `07-projects/` (the project content is git-local, not committed).
- A validated domain pattern/insight learned from real work → `08-knowledge/<domain>/`.
- A reusable "when X, do Y" capability → `03-skills/<name>/SKILL.md`.
- A cross-cutting method / lens / operating model → `01-frameworks/` (extend an existing one; a new
  framework only if 3+ consumers).
- A durable standard / spec / vocabulary → `02-shared-references/`. A deliberate behavioral default →
  `04-preferences/user-preferences.md`.
- **Actual repos, codebases, or non-Figma working files/assets** → the platform- and surface-relative
  `Projects` directory (e.g. `/Users/sean.sands/Projects` on this Mac; the absolute path varies by
  device and user profile — resolve to the local checkout, never hardcode). Never store these inside
  the portable workspace, and never inside an agent's private memory. See [[fact-workspace-repos]].

**Cross-surface persistence (so this rule reaches every agent).** The directive is encoded as a Core
rule in [[AGENTS]] — the universal contract that Claude Code, Claude Chat, Claude Design, Cursor,
Perplexity, and any future agent inherit (the per-tool adapters `CLAUDE.md`/`CURSOR.md`/`PERPLEXITY.md`
are thin layers over it). It also appears in the workspace-ontology routing map. The one
Claude-Code-internal memory that remains is a single pointer file that says exactly this and sends the
agent here.

**Alternatives rejected.** (1) Keep rich content in Claude Code's local memory with the workspace as a
mirror — couples the high-value content to one surface, the opposite of portable-first. (2) Encode the
rule only in workspace memory, not AGENTS.md — then non-Claude-Code surfaces and future agents never
inherit it as a contract obligation.

**Migration that established this (2026-06-30).** The 19 entries in Claude Code's local memory (17 at
the start + 2 visual-QA entries a concurrent session added mid-migration) were relocated: Figma
authoring conventions + transliteration + linked-library rule + clip-content cropping →
[[figma-ds-surface-authoring]]; figma-cli connect/branch/authoring → [[figma-cli-authoring]]; MS-icon
/ section-coords / headless-MCP gotchas → `figma-plugin-patterns`; Radix step→use-class rules →
`radix-derived-color-system`; high-res visual review + recursive-before-presenting QA discipline →
framework #05 (§3a); scope-of-effect placement → framework #02; side-chat handback → `04-preferences`;
the two Centric efforts → `07-projects/02-centricPLM/context/`; the framework-system build →
[[decision-component-pattern-framework-system]]; the "Drive is dead" fact was already covered by
[[decision-portable-workspace-refactor]] + [[fact-workspace-repos]] and retired. Local memory was then
reduced to the single pointer rule `externalize-to-workspace` (which lives in the Claude-Code `.claude`
store, not in this vault).
