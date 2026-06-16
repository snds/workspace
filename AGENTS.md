# AGENTS.md — Universal Agent Context

_Status: universal cross-agent contract for this workspace._
_This file is additive and may coexist with compiled or tool-specific agent files._
_Owner: Sean Sands_

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

- Prefer additive changes over destructive ones.
- Preserve backward compatibility with Claude unless the user explicitly requests a breaking refactor.
- Treat existing Claude-specific files and flows as active production dependencies.
- Use canonical files already in the workspace before inventing new sources of truth.
- Keep human-readable markdown and machine-readable manifests aligned.
- Favor idempotent updates, deterministic naming, and reviewable diffs.

---

## Canonical read order

When entering the workspace without prior context, read in this order:

1. `00-bootstrap/BOOTSTRAP.md`
2. `AGENTS.md`
3. `00-bootstrap/workspace-manifest.json`
4. Root helper files such as `_HOME.md`, `_CONTEXT.md`, `_FRAMEWORKS.md`, `_SKILLS.md`
5. Shared references in `01-shared-references/` when relevant
6. Preference files in `03-preferences/` when relevant
7. Project-local context files for the active project
8. Skill-specific files when performing specialized work

If a task is clearly project-scoped, move to the nearest project root and read local context immediately after the workspace bootstrap files.

---

## Folder semantics

- `00-bootstrap/` — bootstrap docs, manifests, setup, adapters, environment logic
- `00-frameworks/` — reusable frameworks, methods, and operating systems
- `01-shared-references/` — durable standards for reasoning, artifacts, and quality
- `02-skills/` — reusable capabilities, manifests, packaging, installers, compatibility metadata
- `03-preferences/` — user preferences and behavioral defaults
- `04-artifacts/` — generated outputs, active artifacts, archives
- `05-version-registers/` — registers, logs, version tracking
- `06-context/` — durable supporting context and memory-like references
- `07-projects/` — project workspaces with local instructions and deliverables
- `08-knowledge/` — long-lived notes and knowledge resources
- `08-tools/` — scripts, compilers, validators, automation

Root helper files serve as shortcuts and summaries, not replacements for canonical manifests.

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

Skills should be discoverable by both humans and machines.

Preferred discovery path:

1. `02-skills/skills-manifest.json`
2. `_SKILLS.md`
3. Skill folder metadata and `SKILL.md`
4. Supporting docs, scripts, and installers

A skill should ideally expose:

- identifier
- human name
- purpose
- invocation guidance
- inputs and outputs
- dependencies or setup requirements
- compatibility notes by agent or environment
- safe mutation scope, if relevant

When improving skills, extend metadata rather than duplicating entire skills for each agent.

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

All agents should default to safe, reviewable, additive mutation.

Preferred actions:

- add adapter files
- add manifest fields
- add compatibility notes
- add validation or reconciliation tools
- update canonical docs in backward-compatible ways

Avoid by default:

- deleting bootstrap files
- renaming stable root files
- moving folders with active references
- replacing Claude-specific files with universal ones
- introducing hidden state that bypasses Git or human review

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
- improve the workspace bootstrap system without breaking existing integrations

Claude compatibility must remain intact throughout that evolution.
