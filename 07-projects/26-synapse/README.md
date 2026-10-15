---
title: Synapse
aliases: [Switchyard]
type: project
status: Active
triggers: [synapse, switchyard, workspace app, workspace generator gui, credential router, multi-account gh, gh auth switch, vaultwarden migration]
frameworks: [engineering-operating-model, security-operating-model, qa-operating-model, ui-ux-operational, workspace-contribution, domain-rigor-stack]
related_projects: [18-bootstrap-generator, 19-workspace-brain, 25-fontface]
---

# Synapse (26-synapse)

_Codename. It was "Switchyard" until 2026-10-14 (decision D37). The name is tracked as a fact, so a rename for branding or legal reasons is mechanical (D43)._

A desktop app and tray service for Mac and Windows that makes an AI workspace visible and manageable.

- **Plain files.** It reads and writes the same files agents and Obsidian use.
- **No agent needed.** It runs its checks on its own. A connected agent adds judgment.
- **Create and import.** It builds new workspaces and brings in existing ones, with measured results.
- **Personas.** It keeps each persona's accounts and tools apart.

Sean's workspace is the north star.

- **Status:** Stage 0 (model and map), started 2026-10-14.
- **Context profile:** `personal-solo`. Declared by Sean's `profile_resolve.py scan` on 2026-10-14.
- **Code repo:** `~/Projects/synapse`, remote `snds/synapse` (private). First commit `915b1c2`.
- **This folder:** baton and pointers only. The plan and all design docs live in the repo, the same as Fontface.
- **Baton:** [[07-projects/26-synapse/SESSION-STATE|SESSION-STATE]].

## Where things are (in the repo)

| Path | What |
|---|---|
| `docs/plan/00-big-picture.md` | Start here. Then model, architecture, app, create and import, measurement, security, roadmap, commercial path. |
| `docs/plan/decisions.md` | Decision log (D1–D62) |
| `docs/model/model-v1.md` | Workspace model v1 (draft): the contract, with JSON Schemas in `schemas/v1/` |
| `docs/plan/access/` | Personas & access module: logins, devices, Vaultwarden |
| `docs/stage-0/STAGE-0.md` | Stage 0 tracker |
| `scripts/build-plan-html.py` | Builds the readable page from `docs/plan/` |

**Readable copy:** https://claude.ai/artifact/VoPXvWfgPkc8ArsmtmESHt. It is built by `scripts/build-plan-html.py` into `05-artifacts/active/synapse-plan_v2.12_2026-10-15.html`. Artifacts aren't git-tracked. Edit the markdown in the repo, never the HTML.

**Provenance:** the plan was written in this folder (`plan/`, `tools/`) and moved to the repo on 2026-10-14. The last vault copy is at workspace commit `4e2b6cf`. The one-page origin proposal is at https://claude.ai/artifact/24mgDkXvtmu12rCcHJM5Be.

**T1 snapshot** (local only, never pushed): `~/Projects/synapse-sandbox/t1-workspace@4e2b6cf/`.

## Walls

- No employer names, org names or tokens in the repo or these docs. Use placeholders only.
- The T1 snapshot of Sean's workspace stays on his Mac.
- Employer identities and employer-persona workspaces live on the Work MBP only.
