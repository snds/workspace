# AGENTS.md — Universal Agent Context

_Status: **canonical** universal cross-agent contract for this workspace._
_spec_version: 1.0 · Owner: Sean Sands_
_This is the authoritative contract. Tool-specific files (`CLAUDE.md`, `CURSOR.md`, `PERPLEXITY.md`)
are thin adapters over it, not peers to it. Machine entry point: [llms.txt](llms.txt)._

---

## Purpose

This file defines the universal operating contract for any agent or LLM entering this workspace.

Its job is to help any capable system understand:

- what this workspace is
- what to read first
- where context lives
- how skills are discovered
- how project-local instructions interact with workspace-level rules
- how to write safely without breaking existing Claude support

Tool-specific adapters such as `CLAUDE.md` and `PERPLEXITY.md` should be treated as implementation layers on top of this contract, not replacements for it.

---

## Workspace identity

This workspace is a long-lived personal AI operating environment for Sean Sands.

It is designed to work across:

- multiple models and agent runtimes
- multiple devices and operating systems
- markdown-first knowledge management through Obsidian
- versioned, resilient change management through Git and related repositories

The workspace is both a knowledge base and an execution environment.

---

## Core rules

- **Portable-first.** No mechanism here may depend on a single vendor, device, surface, or cloud
  drive. The git checkout is the source of truth; the plain filesystem is the I/O layer. Any capable
  agent must be able to work here by reading this contract — nothing else required.
- **Adapters, not forks.** Tool-specific files (`CLAUDE.md`, `CURSOR.md`, `PERPLEXITY.md`) describe
  only how that tool executes this contract. They never hold logic the contract lacks, and no tool is
  privileged over another.
- Prefer additive changes over destructive ones; when retiring something, archive it with provenance
  (see [Mutation policy](#mutation-policy)).
- Use canonical files already in the workspace before inventing new sources of truth.
- Keep human-readable markdown and machine-readable manifests aligned. Frontmatter is the source of
  truth for the skill graph; `02-skills/skills.registry.json` is generated from it, never hand-edited.
- Favor idempotent updates, deterministic naming, and reviewable diffs.
- Before writing anything, consult the routing map in [workspace-ontology.md](01-shared-references/workspace-ontology.md).

---

## Bootstrap on a checkout

The workspace is a plain git checkout. Resolve the workspace root deterministically:

> **Workspace root = the nearest ancestor directory that contains `AGENTS.md`.**

No cloud-drive path probing, no mount detection, no sync layer. Read and write ordinary files at
that root; git is the source of truth and the sync mechanism. (Tool adapters may add ergonomics — a
Claude hook, a Cursor rule — but the contract above is sufficient with zero tool support.)

## Canonical read order

When entering the workspace without prior context, read in this order:

1. [llms.txt](llms.txt) — machine entry point
2. `AGENTS.md` (this file)
3. `02-skills/skills.registry.json` — the skill graph (for routing + load order)
4. [workspace-ontology.md](01-shared-references/workspace-ontology.md) — vocabulary + routing map
5. Root helper files such as `_HOME.md`, `_CONTEXT.md`, `_FRAMEWORKS.md`, `_SKILLS.md`
6. `06-context/` — durable context + memory (`memory/MEMORY.md` index)
7. Shared references in `01-shared-references/` and preferences in `03-preferences/` when relevant
8. Project-local context files for the active project; skill files when performing specialized work

If a task is clearly project-scoped, move to the nearest project root and read local context immediately after these workspace files.

---

## Folder semantics

- `00-bootstrap/` — bootstrap docs, setup, adapters, environment logic
- `00-frameworks/` — reusable frameworks, methods, and operating models (incl. the contribution framework that governs edits to this workspace)
- `01-shared-references/` — durable standards: ontology + routing map, frontmatter spec, reasoning/artifact standards
- `02-skills/` — reusable capabilities; `skills.registry.json` is the generated skill graph (source of truth = each `SKILL.md` frontmatter)
- `03-preferences/` — stable, deliberately set behavioral defaults
- `04-artifacts/` — generated outputs, active artifacts
- `05-version-registers/` — registers, logs, version tracking
- `06-context/` — durable operational context; `06-context/memory/` is the typed, non-project memory layer
- `07-projects/` — project workspaces with local instructions and deliverables
- `08-knowledge/` — long-lived domain insight learned from real work
- `09-tools/` — scripts, generators, validators, automation
- `_archive/` — retired files, each with provenance in `ARCHIVE-LOG.md`

Root helper files (`_HOME.md`, `_SKILLS.md`, …) and per-domain MOCs are Obsidian navigation shortcuts, not replacements for the canonical registry/manifests.

---

## Context precedence

When multiple context files exist, apply this order of precedence:

1. Explicit user instruction in the current session
2. Active project-local context files
3. Workspace bootstrap and manifest files
4. Shared references and frameworks
5. Historical artifacts and archived materials

Project-local overrides should be interpreted narrowly and should not silently rewrite workspace-global policy.

---

## Skills discovery contract

Skills are discoverable by both humans and machines through one generated graph:

1. `02-skills/skills.registry.json` — the machine graph (tiers, prerequisites, related, triggers,
   precomputed `load_chains`). Generated from frontmatter by `09-tools/build-registry.py`.
2. Each `02-skills/<name>/SKILL.md` — the skill itself; its frontmatter is the source of truth.
   Spec: [skill-frontmatter.md](01-shared-references/skill-frontmatter.md).
3. `_SKILLS.md` and per-domain MOCs — human navigation.

Each skill's frontmatter exposes: `name`, `description` (routing prose), `triggers`, `tier`
(`foundation`/`hub`/`spoke`/`cross-cutting`), `hub`, `prerequisites`, `related`, `governed_by`,
`surfaces`. When improving skills, extend frontmatter — never duplicate a skill per agent.

## Skill loading precedence

Foundations load before hubs load before spokes. This is **computed from the graph**, not guessed.
Any agent — with or without tool hooks — runs the same algorithm:

```
load_set(message, registry):
  matched   = skills whose `triggers` match the message   (fallback: match `description`)
  required  = for each matched skill, the union of its load_chains[name]   # ancestors + self, ordered
  ordered   = merge the chains, preserving order; dedupe; foundations first
  suggestions = union of `related` for required skills, minus required     # surfaced, never auto-loaded
  return ordered, suggestions
```

`load_chains[name]` is precomputed in the registry (foundation → hub → spoke), so even a weak or
offline agent needs no graph traversal — it looks up the chain and reads those `SKILL.md` files in
order. Only `prerequisites` and the implicit spoke→`hub` edge are hard (load-before). `related` and
`governed_by` are navigational/lenses, never auto-loaded.

Worked example — "dark-mode palette for this dashboard" →
`design-foundations` → `lead-ui-designer` → `uid-color-for-ui` (suggests `ds-advisor`, `uid-surface-depth`).

---

## Project contract

Each project under `07-projects/` should be interpretable by any agent.

Preferred local discovery order:

1. `README.md`
2. project-level agent adapter files such as `CLAUDE.md`
3. local config or context files such as `.visual-qa-context.yaml`
4. supporting specs, plans, or notes

For future normalization, each project should eventually expose a universal local context file such as `PROJECT.md`, `AGENT-CONTEXT.md`, or a manifest-backed equivalent.

---

## Mutation policy

All agents default to safe, reviewable mutation. **Where a piece of information belongs, and how to
add it, is governed by the routing map** ([workspace-ontology.md](01-shared-references/workspace-ontology.md))
and the full per-layer rules in [00-frameworks/08-workspace-contribution-framework.md](00-frameworks/08-workspace-contribution-framework.md).
Read those before writing.

Preferred actions:

- add or extend skills via frontmatter (then regenerate the registry); add cross-links reciprocally
- add adapter files; add validation/generation tools; update canonical docs in reviewable diffs
- record durable non-project facts in `06-context/memory/`; record learned domain insight in `08-knowledge/`

Avoid by default:

- renaming a `SKILL.md` file/dir or a stable root file (breaks loader paths + Obsidian links — add `aliases` instead)
- moving folders with active references without re-pointing them
- **deleting** anything — archive to `_archive/` with an `ARCHIVE-LOG.md` entry + tombstone instead
- introducing hidden state that bypasses git or human review
- hand-editing generated files (`skills.registry.json`)

---

## Git and Obsidian resilience

This workspace should remain durable under long-term use.

Agents should preserve:

- markdown readability in Obsidian
- stable paths and names for links and automation
- small, auditable diffs where possible
- replayable or idempotent setup logic
- explicit manifests over undocumented assumptions

When adding structure, prefer formats that are friendly to both markdown readers and automation.

---

## Adapter model

Agent-specific files are thin adapters over this one contract — **not** separate contracts.

- `CLAUDE.md` — Claude Code / Desktop · `CURSOR.md` — Cursor · `PERPLEXITY.md` — Perplexity ·
  any future agent ecosystem (GPT-based tools, Gemini, local models, a human).
- **A new agent needs no adapter to participate at full fidelity** — executing this contract is
  sufficient. An adapter only documents that tool's ergonomics (hooks, rule files, slash commands)
  and capability limits. Onboard a new one from `00-bootstrap/adapters/_ADAPTER-TEMPLATE.md`.

Adapters must: reference this contract; describe only tool-specific execution; never fork the workspace
model or hold state the contract lacks. No tool is privileged over another.

---

## Multi-agent continuity & handoff

**The guarantee: one workspace = one contract = one continuous, shared state.** A project, conversation,
or session is a **single unified thread** no matter how many agents, models, surfaces, or devices touch
it. Mid-project handoff between *any* agents — Claude → Cursor → Perplexity → a local model → a human and
back — must feel seamless, never like separate contracts or restarted context. This is the hardest part of
multi-agent work, so it is a first-class contract obligation, not an afterthought.

### Single shared state (no private contexts)
Every agent reads from and writes to the **same** state. An agent must never keep a private/parallel
context store; it updates the shared one so the next agent inherits an unbroken thread.

| State | Holds | Cadence |
|---|---|---|
| Active project `SESSION-STATE.md` (its **Live handoff** block) | "pick up exactly here": current focus, working set, last action, next action, open decisions, blocked-on, in-flight/do-not-touch | updated **continuously** + at every handoff |
| `06-context/session-log.md` | chronological history, newest-first, each block attributed | appended at handoff / session end |
| `06-context/memory/` | durable, non-project facts + decisions | when a durable fact emerges |

### Handoff protocol (tool-neutral — every agent follows this)
1. **On entry** — read this contract, then the active project's `SESSION-STATE.md` **Live handoff** block
   and the head of `session-log.md`. You now hold the same context the previous agent had. Do **not** infer
   state from scratch or assume a fresh project.
2. **While working** — keep the Live handoff block current as the situation changes (focus, working set,
   decisions). It is the baton, not a journal.
3. **On handoff / pause / end** — rewrite the Live handoff block (atomically, no stale fields) and append a
   session-log entry. Leave the next agent a clean "next action."
4. **Concurrent edits** — if two agents touched the same project in parallel, run the reconcile protocol
   (`/reconcile` or the merge steps in the bootstrap skill) to merge into one thread; flag genuine conflicts.

### Agent self-identification
Every session-log entry and Live handoff update stamps **Agent · Surface · Machine** (e.g.
`Claude Opus / Claude Code / Personal MBP`, `GPT / Cursor / Work MBP`, `Perplexity / web`). Attribution is
what lets one continuous thread show *who did what* without fragmenting into per-agent contexts.

### What makes it unified (not N contracts)
- One contract (this file) every agent obeys → identical rules, identical loading precedence.
- One generated skill graph (`02-skills/skills.registry.json`) → identical skill set + order for the same request.
- One live state (above) → the baton passes intact.
- One routing map (`01-shared-references/workspace-ontology.md`) → everyone writes to the same place.

Full per-layer protocol: `00-frameworks/08-workspace-contribution-framework.md` → "Portable session protocol".

---

## Desired end state

A successful universal agent system should allow any capable model to:

- enter the workspace and orient quickly
- find the correct bootstrap path
- discover relevant skills
- identify active project context
- understand safe write locations and mutation rules
- improve the workspace without breaking existing integrations

No single tool is privileged: Claude, Cursor, Perplexity, a generic MCP client, and a human reading
the files all follow this same contract and should reach near-identical results.
