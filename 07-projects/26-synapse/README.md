---
title: Synapse
aliases: [Switchyard]
type: project
status: Planning
triggers: [synapse, switchyard, workspace app, workspace generator gui, credential router, multi-account gh, gh auth switch, vaultwarden migration]
frameworks: [engineering-operating-model, security-operating-model, qa-operating-model, ui-ux-operational, workspace-contribution, domain-rigor-stack]
related_projects: [18-bootstrap-generator, 19-workspace-brain, 25-fontface]
---

# Synapse (26-synapse)

_Codename. It was "Switchyard" until 2026-10-14 (decision D37). Every place the name appears will be tracked in a name ledger built in Stage 0, so a rename for branding or legal reasons is mechanical._

A desktop app and tray service for Mac and Windows that makes an AI workspace visible and manageable.

- It reads and writes the same plain files agents and Obsidian use.
- It runs its checks without an agent, and a connected agent adds judgment.
- It creates and imports workspaces, with measured results.
- It keeps each persona's accounts and tools apart.

Sean's workspace is the north star. "Synapse" is a working name.

- **Status:** Planning. The plan set is at v2.0, after the 2026-10-14 reframe. Nothing is built.
- **Context profile:** `personal-solo`.
- **Code repo:** none yet. Stage 0 creates `~/Projects/synapse` (remote `snds/synapse`) and moves `plan/` into its `docs/`. This folder then keeps the baton and pointers, as with Fontface.
- **Baton:** [[07-projects/26-synapse/SESSION-STATE|SESSION-STATE]].

## Plan

1. [Big picture](plan/00-big-picture.md): what changed, the product on one page, principles, modules, north star, domains
2. [Workspace model](plan/01-workspace-model.md): node types, edges, domains and areas, file contract, conformance
3. [Architecture](plan/02-architecture.md): engine, tray service, access process, app, CLI, agent jobs, plugins, technology
4. [App experience](plan/03-app-experience.md): tray, screens, key journeys
5. [Create and import](plan/04-generator-and-importer.md): generator, importer, agentic scanner, how this workspace maps, where `wsx` pieces go
6. [Measurement](plan/05-measurement.md): 13 metrics, corpus T1–T4, gates
7. [Security](plan/06-security.md): app-wide risks, process separation, tests
8. [Roadmap](plan/07-roadmap.md): Stages 0–7, tracks, first steps
9. [Commercial path](plan/08-commercial-path.md)
10. [Decision log](plan/decisions.md)
11. Personas & access module: [plan/access/](plan/access/00-overview.md). This was the original credential plan: systems, integrations, flows, security, Vaultwarden, phases.

**Readable copy:** https://claude.ai/artifact/VoPXvWfgPkc8ArsmtmESHt. It is built from `plan/` by `tools/build-plan-html.py` into `05-artifacts/active/synapse-plan_v2.1_2026-10-14.html`. Artifacts aren't git-tracked. Edit the markdown, never the HTML.

**Origin:** the one-page proposal, https://claude.ai/artifact/24mgDkXvtmu12rCcHJM5Be.

## Open decisions (see the big picture)

- The name.
- Frontmatter placement for workspace fields, against the Agent Skills spec.
- Generator engine: Rust core with `wsx` as the oracle, the recommended option.
- Plugin runtime: MCP-server plugins with sandboxed UI, the recommended option.
- The domain and area map, set after the first scan.

## Walls

- No employer names, org names or tokens in these docs. Use placeholders only.
- The snapshot of Sean's workspace used for testing stays on his Mac.
- Employer identities and employer-persona workspaces live on the Work MBP only.
