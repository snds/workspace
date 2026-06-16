---
name: workspace-bootstrap
description: >
  The session handshake — loads workspace context at the start of every session,
  on any device, surface, or model. Trigger immediately and silently whenever a
  conversation begins or the user says "let's get started", "resume", "continuing
  from", "pick up where we left off", "new session", "I'm back", "let's work on",
  or asks to load context. Run before any other skill. Also trigger on "reconcile
  sessions", "end of day sync", "merge sessions". Also trigger on "legion",
  "Legion", "my game", "game project" — load workspace context then the Legion
  skill set.
aliases: [workspace-bootstrap]
triggers: [bootstrap, resume, new session, load context, get started, reconcile sessions, legion]
tier: cross-cutting
domain: workspace
surfaces: ["*"]
spec_version: "2.0"
---

# Workspace Bootstrap

The session handshake. Loads workspace context at session start so any agent — Claude Code, Cursor,
Perplexity, a generic MCP client, or a human — orients identically. This skill is the **operational
how-to**; the **contract** it executes is [[AGENTS]] (universal) + framework 08's *portable session
protocol* ([[08-workspace-contribution-framework]]). It assumes only a git checkout and a filesystem —
**no Google Drive, no Desktop Commander, no vendor-specific mechanism.**

## Boot sequence (runs silently; one status line at the end)

1. **Resolve the workspace root** — the nearest ancestor directory containing `AGENTS.md`. That is the
   source of truth. (A tool adapter — a Claude `SessionStart` hook, a Cursor rule — may automate this,
   but the steps below work with zero tool support: just read files.)
2. **Read the contract + graph:** [[AGENTS]] → `03-skills/skills.registry.json`.
3. **Read context** via the filesystem (in order):
   - `06-context/role-and-context.md` — who Sean is
   - `06-context/project-context.md` — active projects + pending (authoritative)
   - `06-context/session-log.md` — recent entries, newest first
   - `06-context/memory/MEMORY.md` — durable non-project memory index
   - `04-preferences/user-preferences.md` — communication style
4. **Regenerate the registry if skills changed** since last run: `python3 09-tools/build-registry.py`
   (idempotent; no-op if nothing changed).
5. **Confirm** with the session-start ritual (the tool adapter defines the exact format; see
   [[CLAUDE]] / [[CURSOR]]). Then proceed into the user's request.

If a file is missing, proceed without it — note only genuinely unexpected gaps.

## Skill Loading Protocol (token-optimized)

**Load the minimum skill set for the current question.** Routing (matching the message to a skill) is
zero-cost — `description`/`triggers` are already available via the registry. Loading a `SKILL.md` costs
tokens, so never load speculatively.

1. **Route** — match the user's message to skills by `triggers` (fallback: `description`).
2. **Expand** — for each matched skill, take its `load_chains[name]` from the registry: the ordered
   ancestor list (**foundation → hub → spoke**). This is precomputed, so no graph traversal is needed.
3. **Load in order** — read those `SKILL.md` files foundation-first. A foundation loads *before* the
   specialty skill so principles are in hand before application.
4. **Suggest, don't load** — surface each skill's `related` as options; never auto-load them.
   Cross-cutting lenses (`governed_by`, e.g. `a11y-*`, `visual-qa-*`) load *after* output is produced.

**Do not** load all spokes of a hub, project-context skills unless the project is referenced, or
framework spokes for a framework not in use. A typical question needs 1–3 skills.

When the opening message is ambiguous ("let's get started"), finish boot, then ask what to work on.

## Project Context Triggers

When these keywords appear, load the project skill set (additive — layered on workspace context).

### Legion (game project)
**Triggers:** "legion", "Legion", "my game", "game project", "the game", "Bobiverse", "Bob clone",
"factory sim", "star system".

Load in order: `legion-project` (foundation context — always first), then the relevant hub by topic —
design → `lead-game-designer`; visual → `lead-art-director`; technical → `lead-game-developer`
(ambiguous → `lead-game-designer`). Specialty skills load by topic: materials/PBR → `threejs-materials-master`;
shaders/GLSL → `glsl-shader-architect`; post-processing/VFX → `threejs-vfx-atmosphere`; WebGPU/TSL →
`webgpu-advanced-rendering`.

## Session End

Triggered by "end of session", "wrap up", "done for today", or any closing signal. Follow framework 08's
*portable session protocol* — write via the filesystem, commit reviewable diffs:

1. Append a **Session Block** to `06-context/session-log.md` (newest-first).
2. Apply project status / pending changes to `06-context/project-context.md`.
3. Update the active project's `SESSION-STATE.md`.
4. If frontmatter changed, regenerate `03-skills/skills.registry.json`.
5. Record durable non-project facts in `06-context/memory/`; learned domain insight in `08-knowledge/`.
6. Commit + push.

**Session Block format** (portable unit of state; N blocks can be merged in a reconciliation session).
The `Agent`/`Surface`/`Machine` stamp is what keeps a multi-agent project one unified thread — see
[[AGENTS]] → "Multi-agent continuity & handoff".
```
--- SESSION BLOCK ---
Date: YYYY-MM-DD
Agent: <model/tool, e.g. Claude Opus / GPT / Perplexity / local>
Surface: <Claude Code | Cursor | Perplexity | web | ...>
Machine: <hostname-derived label>
Project(s): <names>
Artifacts: - <filename> — <one-line>
Decisions: - <decision, rationale>
Pending added: - <item>
Pending resolved: - <item>
Project status changes: - <project>: <old> → <new>
Next: - <specific next action>
--- END BLOCK ---
```
Omit empty sections. **Reconciliation** ("reconcile sessions", "end of day sync") merges multiple
Session Blocks into clean updates for `session-log.md` + `project-context.md`, flagging conflicts.

## Embedded snapshot (fallback when context files can't be read)

State once: `⚠ Running from embedded snapshot — context may be stale.` Then proceed.

**Preferences:** US English, Oxford comma · lead with the answer, no preamble · flag tradeoffs, explain
rationale · make uncertainty explicit · code comments only on non-obvious behavior · audience is a
UX/product designer · DS terms (tokens, variants, states, anatomy, slot, tier, alias, primitive) ·
3-tier token model (global → semantic → component) · avoid "This isn't X, it's Y".

**Role:** Principal Lead Product Designer — Design Systems, Centric Software (enterprise PLM: fashion,
food, general product). Specializes in component architecture, token systems, Figma plugin dev,
cross-framework strategy (Vue/React/React Native/Angular), audits, deprecation, design/dev handoff.
Users: high-density data-table and form-heavy interfaces. Account: hello@snds.design.

**Projects:** Data Table Documentation · Component Set Manager (Figma plugin) · this portable workspace
refactor · AI-Powered Design Assessment · **Legion** (hard-SF game; Three.js + WebGPU; trigger "legion").

**Artifacts:** `context_descriptor_vN.N_YYYY-MM-DD.ext` — never overwrite; increment version.

## Related
- peer ↔ [[skill-placement]]
