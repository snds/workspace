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

Agent-specific files are adapters over the same workspace.

Examples:

- `CLAUDE.md` — Claude-specific adapter
- `PERPLEXITY.md` — Perplexity-specific adapter
- future adapters may exist for other agent ecosystems

Adapters should:

- reference the universal contract
- define agent-specific capabilities or limitations
- avoid forking the underlying workspace model unless absolutely necessary

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
