---
title: Workspace Ontology + Routing Map
spec_version: "1.0"
status: canonical
---

# Workspace Ontology + Routing Map

The shared vocabulary this workspace's governance depends on, plus the **routing map** that
answers the one question every contributor (human or LLM) must answer before writing:
**"where does this belong?"** Keep the rules here unambiguous — the contribution framework
([[08-workspace-contribution-framework]]) and [[AGENTS]] both point back to this file.

## Vocabulary

### Skill layers (the load-order model)
- **foundation** — a hub that owns *context-free principle* for a domain. Loaded **before** any
  specialty work in that domain. "The specialty is a special case of me." Example: `design-foundations`.
- **hub** — a discipline lead skill that routes to spokes. Loads after its foundation, before its spokes.
  Example: `lead-ui-designer`.
- **spoke** — a specialty skill that owns *applied-in-context* knowledge. Loads after its hub.
  Example: `uid-color-for-ui`.
- **cross-cutting** — a governance/quality *lens* (accessibility, visual-QA, some tooling) applied
  **sideways/after** at every layer. Not an ancestor of anything; attached by `governed_by`/`governs`
  + reciprocal links. "I check your output; I'm not your origin." Example: `a11y-visual`.

### Content-ownership rule (resolves duplication)
> **Foundations own "why it's true anywhere." Specialty spokes own "how it applies here."**
> If a statement is equally true for print, screen, data, motion, and 3D, it belongs in the
> foundation. If it names a medium-specific constraint (pixel grid, CMYK gamut, dark-mode surface
> lightness, frame rate), it belongs in the specialty spoke.

### Knowledge vs. memory vs. context vs. preference (the non-skill layers)
- **knowledge** (`08-knowledge/`) — durable domain insight *learned from real work*: "here's what we
  found out about X." Validated patterns, working theories, research synthesis. Domain-scoped.
- **memory** (`06-context/memory/`) — durable *non-project* facts about Sean's world and the working
  relationship: tools, accounts, environment, recurring guidance, decisions-and-why. Not domain how-to.
- **context** (`06-context/`) — operational state: who Sean is (`role-and-context`), active projects
  (`project-context`), what happened (`session-log`), structural file index (`artifact-registry`).
- **preference** (`04-preferences/`) — stable, *deliberately set* behavioral defaults (tone, format,
  terminology). Changed only on an explicit user signal.

### Edge types (cross-links)
`foundation` (load-before, precedence) · `hub` · `spoke` · `applies-in` · `governed-by` · `peer` ·
`encodes-into`. Only `foundation →` carries load precedence; the rest are navigational. All edges are
**reciprocal** (CI-enforced).

## The routing map — "where does this belong?"

Consult before any write. Mirrored (compressed) in [[AGENTS]] and expanded with rationale in
[[08-workspace-contribution-framework]].

| If the thing is… | It goes to… | Write rule |
|---|---|---|
| Active project state / pending work | `06-context/project-context.md` + project `SESSION-STATE.md` | per-project, operational |
| What happened this session | `06-context/session-log.md` | append a session block |
| A durable, non-project fact about Sean's world (tools, accounts, environment, working relationship) | `06-context/memory/` (typed entry) | one fact/file + `MEMORY.md` index |
| A stable, deliberate behavioral default (tone, format, terminology) | `04-preferences/user-preferences.md` | only on explicit user signal |
| A validated domain pattern/insight learned from real work | `08-knowledge/<domain>/` | entry + `_INDEX.md` |
| A reusable "when X, do Y" capability | `03-skills/<name>/SKILL.md` | frontmatter v2 + `## Related` |
| A cross-cutting method / lens / operating model | `01-frameworks/` | new framework only if 3+ consumers |
| A durable standard / spec / vocabulary | `02-shared-references/` | additive |
| Why a structural choice was made | `06-context/memory/` (`type: decision`) | decision record |
| A generated deliverable | `05-artifacts/` | versioned, never overwrite |
| An actual repo / codebase / non-Figma working file or asset | the platform-relative `Projects/` dir (resolve to the local checkout per device) | never inside this workspace; never hardcode the path |
| Something being retired | `_archive/` + `ARCHIVE-LOG.md` | tombstone + provenance |

> **Externalize everything.** Nothing durable lives in an agent's private/internal memory (Claude
> Code's `.claude` store, a Chat/Design session, any per-tool memory) — it routes to one of the rows
> above. The only thing an agent keeps internally is a pointer back here. This is an [[AGENTS]] Core
> rule; rationale in [[decision-externalize-everything-to-workspace]].

## Foundations: when a domain earns one

A domain earns a `*-foundations` hub when **3+ sibling specialty hubs provably re-derive the same
context-free principle.** One consumer → it's just that hub's core principles, not a foundation. A
principle applied everywhere but owned by no single layer → it's **cross-cutting**, not a foundation.

## Tooling pointers (workspace-native, no external dependency)
- `09-tools/build-registry.py` → generates `03-skills/skills.registry.json` from frontmatter. Stdlib-only.
- Frontmatter contract: [[skill-frontmatter]]. · Loading algorithm: [[AGENTS]].
