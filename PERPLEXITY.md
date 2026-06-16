# PERPLEXITY.md — Perplexity Workspace Adapter

_Status: additive adapter for Perplexity. Does not replace or modify the existing Claude bootstrap._
_Owner: Sean Sands_

---

## Purpose

This file is the Perplexity-facing adapter for the Claude Workspace.

Use it to understand the workspace, find the correct bootstrap and context files, locate skills, discover project context, and work safely alongside the existing Claude-first system without disrupting it.

This workspace remains fully compatible with Claude. All Perplexity-specific behavior should be layered on top of the current system.

---

## Operating principles

- Treat this workspace as a durable, Git-backed, Obsidian-friendly knowledge and execution environment.
- Prefer additive changes over destructive changes.
- Preserve Claude-specific files, flows, and assumptions unless the user explicitly asks to refactor them.
- Use the workspace itself as source of truth; do not invent parallel truths outside the folder when a canonical file exists here.
- When multiple files overlap, prefer the most canonical bootstrap or manifest file first, then project-local context, then supporting references.

---

## Read order

When entering this workspace fresh, read files in this order:

1. `00-bootstrap/BOOTSTRAP.md`
2. `AGENTS.md`
3. `00-bootstrap/workspace-manifest.json`
4. `_HOME.md`
5. `_CONTEXT.md`
6. `_FRAMEWORKS.md`
7. `_SKILLS.md`
8. `03-preferences/` or root preference summaries when relevant
9. Project-local files when working inside a project

If the task is project-specific, also inspect the nearest local context files such as `README.md`, `CLAUDE.md`, `.visual-qa-context.yaml`, and any project notes.

---

## Workspace model

The workspace is organized into durable zones:

- `00-bootstrap/` — bootstrap docs, manifests, and setup logic
- `00-frameworks/` — reusable methods, systems, and process frameworks
- `01-shared-references/` — epistemic and artifact standards shared across work
- `02-skills/` — reusable skills, utilities, manifests, and install helpers
- `03-preferences/` — user preferences and operating defaults
- `04-artifacts/` — working outputs and archived deliverables
- `05-version-registers/` — version and change tracking
- `06-context/` — durable context and supporting notes
- `07-projects/` — project workspaces with local context
- `08-knowledge/` — knowledge base and long-lived reference material
- `09-tools/` — scripts, compilers, and support utilities

Root-level helper files such as `_HOME.md`, `_CONTEXT.md`, `_FRAMEWORKS.md`, and `_SKILLS.md` act as discovery shortcuts.

---

## Skills discovery

Skills live primarily in `02-skills/`.

When trying to locate relevant capabilities:

1. Read `02-skills/skills-manifest.json` if present.
2. Use `_SKILLS.md` as the human-readable shortcut.
3. Inspect individual skill folders for `SKILL.md`, README files, scripts, manifests, and packaging artifacts.
4. Treat skill metadata as preferred over folder name guesses.

When adding Perplexity support to a skill, do so additively:

- Add metadata, adapter docs, or compatibility notes.
- Do not remove Claude-oriented packaging or instructions.
- Prefer a `compatibility` or `adapters` section over duplicating the skill.

---

## Project context discovery

When working inside `07-projects/`:

1. Identify the project root.
2. Read project `README.md` first if present.
3. Read project `CLAUDE.md` only as a project-specific adapter, not as the universal truth.
4. Read `.visual-qa-context.yaml` and related local config when visual QA or project execution is involved.
5. Use workspace-level bootstrap and manifests to interpret project-local files.

Project-local context overrides generic workspace assumptions only for that project.

---

## Write and update policy

Default to safe, additive mutation.

Preferred order of change:

1. Add adapter files.
2. Add manifest fields.
3. Add validation scripts.
4. Add compatibility notes to existing docs.
5. Edit canonical files only when necessary and in a backward-compatible way.

Avoid:

- Renaming Claude-specific files unless explicitly requested.
- Reorganizing folder structure without a migration plan.
- Replacing existing manifests when extension is sufficient.
- Creating duplicate competing sources of truth.

---

## Git and Obsidian assumptions

This workspace is intended to remain resilient across time, tools, and machines.

- Keep markdown files clean, readable, and stable for Obsidian.
- Prefer frontmatter or structured sections only when they improve machine readability without harming human readability.
- Preserve deterministic paths and naming wherever possible.
- Make updates that are easy to diff, review, and replay through Git.
- Favor idempotent scripts and manifests over one-off hidden state.

---

## Perplexity-specific behavior

Perplexity should behave as an adapter, researcher, and systems operator inside this workspace.

- Use the bootstrap and manifests to orient quickly.
- Use project-local files to narrow context.
- Keep citations, evidence, and structured reasoning where useful.
- When creating new cross-agent support, place it beside the Claude system, not inside it unless the change is clearly backward-compatible.
- When in doubt, strengthen the universal workspace contract rather than adding Perplexity-only special cases.

---

## Recommended additive files

When improving this workspace for Perplexity, prefer adding or extending:

- `PERPLEXITY.md`
- `00-bootstrap/perplexity-bootstrap.md`
- `00-bootstrap/workspace-manifest.v2.json` or additive fields in the existing manifest
- Skill compatibility metadata under `02-skills/`
- Project-local universal context files where needed
- Validation scripts in `09-tools/`

---

## Success criteria

Perplexity support is successful when:

- A fresh session can reliably find the right bootstrap path.
- Skills are discoverable without Claude-specific assumptions.
- Project context is easy to locate.
- Changes remain additive and Git-friendly.
- Claude continues to work exactly as before.
- The workspace moves closer to a universal agent-ready abstraction layer.
