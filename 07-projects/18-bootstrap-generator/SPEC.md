---
status: draft
version: 0.2
date: 2026-06-13
tags: [bootstrap-generator, skills, workspace-system, spec, portability]
derived-from: "[[workspace-bootstrap]]"
---

# Portable, Model-Agnostic Workspace Bootstrap Generator — Spec v0.2

_2026-06-13 · derived from Sean's Claude Workspace (`02-skills/workspace-bootstrap`)_

**Goal:** let a friend run an interview and walk away with a personalized hub/spoke skill network + context system that works on any model and any surface.

---

## Resolved decisions (drive everything below)

1. **Skill + CLI, in tandem.** Skill = the brain (interview, judgment, generation). CLI (`wsx`) = the hands (deterministic file ops, emit, sync, verify). The skill calls the CLI for anything mechanical. The CLI is also the portability backstop for surfaces with no skill mechanism / weak models.
2. **Transport = git, with Obsidian as the human layer.** The generated workspace root is an Obsidian vault (`.obsidian/` shipped in the emit). Gitignore `.obsidian/workspace*.json` (per-machine UI state); commit shared vault config. `[[wikilinks]]` are the native cross-link idiom between context and skills.
3. **Second emit target = the MCP runtime** (not a second bespoke file adapter). One MCP server lights up Cursor + Codex + Windsurf + local frontends. Per-product file adapters (Cursor/AGENTS.md) come later as thin fallbacks.
4. **Context model = walled by default, opt-in blend.** Work/professional/personal live in separate context files with a `personal.private = true ⇒ never synced` flag; a one-word trigger pulls personal context in on demand. Default derived from the Movement 5 separation answer; wall it for anyone with a work machine.

---

## 1. The portable kernel

Kernel = markdown corpus + a manifest + a lifecycle protocol (all plain files). Vendor-specific bits (skill triggering, lifecycle automation, file I/O, sync) become thin, regenerable adapters around it.

## 2. The Interview (→ `profile.yaml`)

Six adaptive movements (M0–M5; folded into five friendly "parts" for the user-facing README); suggestive not prescriptive; ends with synthesize-and-confirm.

- **M0 — Surfaces & infra:** which tools/models, offline needs, machines, current sync, existing assets to import. → emit targets, transport, capability tier.
- **M1 — Work context:** role/domain, recurring deliverables, fixed constraints, standards, where time is lost. → work hubs/spokes + work project-context.
- **M2 — Professional craft:** deep expertise, active growth, north-star standards, craft done outside the employer. → the `lead-*` hubs.
- **M3 — Personal context (guide & suggest):** dream builds, hobbies, life admin (financial planning, taxes, health, language), creative pursuits, learning goals. → private personal context.
- **M4 — Operating preferences:** tone/verbosity, audience, code-vs-prose, banned anti-patterns, ask-vs-proceed posture. → user-preferences + offline snapshot.
- **M5 — Lifecycle & ambition:** session continuity, walled/blended separation, automation level, privacy/encryption. → lifecycle adapter + separation + gitignore/encryption policy.

## 3. Profile Manifest

`schema_version · identity · surfaces · models{tier,offline} · transport · contexts{work,professional,personal} · preferences · lifecycle · privacy · imports` — the seam interface the CLI consumes.

## 4. The Resolver

Per domain: search registries → strong match **PULL** (pin+namespace) · partial **PULL+PATCH** (patches in a sibling overlay; pulled skills read-only) · none **GENERATE** via skill-creator. Assign to a hub, register triggers, then mandatory overlap reconciliation (dedupe triggers, assign a canonical owner per concern). Registries = pluggable sources (skills.sh, anthropic-skills, claude-1337 & similar, community, user imports), each with fetch + license/trust notes.

## 5. The Emitter (the spine)

Canonical source-of-truth (git transport, Obsidian vault):

```
workspace/
  context/    profile · project-context · session-log · relational · artifact-registry
  skills/     hub/spoke markdown (canonical SKILL.md)
  frameworks/
  manifest.json    routing index
  adapters/   generated, surface-specific — never hand-edited
  .obsidian/  vault config (workspace*.json gitignored)
```

**Canonical skill format:** markdown + frontmatter (`name · description · triggers · domain · role · hub · source · surfaces`); `triggers`/`description` are the single source each adapter translates.

**Adapters:** Claude Code (`.claude/skills/`, `CLAUDE.md`, hooks) · MCP runtime · Cursor (`.cursor/rules` + `AGENTS.md`) · AGENTS.md (Codex/Copilot/Windsurf) · context pack (tool-less).

**Universal runtime:** one MCP server `workspace-mcp` exposing `context.load · skills.search · skills.load · session.start · session.end · reconcile`.

**Degradation ladder** (your tiering, generalized): MCP/native tools → CLI (`wsx`) → pasteable context pack.

**Capability tiering:** frontier = full on-demand network; small-local = pre-flattened pack of 8–15 highest-value skills.

## 6. The CLI/skill seam (defined in Phase 0, before building either side)

The boundary IS the architecture. Two manifests are the contract: `profile.yaml` and `manifest.json`. The skill produces/edits them; the CLI consumes them. Everything mechanical is a `wsx` subcommand the skill invokes, never does inline.

`wsx` command surface:

```
wsx init                 scaffold neutral workspace + Obsidian vault + git init
wsx profile <get|set>    validate/read/write profile.yaml
wsx resolve              fetch + pin pulled skills (mechanical half of Resolver)
wsx emit <target>        compile canonical → adapter (claude-code|mcp|cursor|agents-md|pack)
wsx lint                 validate skills + manifest, report trigger overlaps
wsx verify               dry-run load per target
wsx session <start|end|reconcile>   lifecycle file ops
wsx sync                 git pull/push (or chosen transport)
```

- **CLI owns:** filesystem, emit/compile, manifest hashing/sync, lint, verify, git, scaffold — deterministic, no model.
- **Skill owns:** interview, profile synthesis, match/rank/generate judgment, overlap-reconciliation decisions, narration.

## 7. Revised build order (dogfood-first)

- **Phase 0 — Kernel + seam.** Templatize context/frameworks/lifecycle into neutral templates w/ placeholders. Define the two manifest schemas and the `wsx` command surface (stubs). Ship the Obsidian-vault scaffold + gitignore rules + `git init` in `wsx init`. Bake in: git+Obsidian transport, walled-context file layout w/ `private` flags, skill-calls-CLI boundary.
- **Phase 1 — Interview → profile.** Skill runs M0–M5 → `wsx profile set` writes `profile.yaml`; synthesis/confirm gate.
- **Phase 2 — Resolver.** Skill judgment + `wsx resolve` for fetch/pin; overlap pass mandatory.
- **Phase 3 — Emitter.** `wsx emit claude-code` first (dogfood) → `wsx emit mcp` (universal runtime, decision #3) → then `cursor`/`agents-md`/`pack` as thin fallbacks.
- **Phase 4 — Verify + install docs.** `wsx lint` + `wsx verify` per target; per-surface/per-machine setup docs; walled/blend toggle documented.

## 8. Standing risks

Format churn → adapters thin, never hand-edited. Library trust → vet/pin/namespace, pulled read-only. Privacy → personal context local-only + gitignored, `private` ⇒ never synced, encryption offered. Model variance → capability tiering.

## 9. Ship-as (last open choice)

A `bootstrap-gen` skill in `02-skills/` and a standalone `wsx` CLI repo — the seam in §6 makes them one system, not two.
