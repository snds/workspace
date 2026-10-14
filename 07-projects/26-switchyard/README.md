---
title: Switchyard
type: project
status: Planning
triggers: [switchyard, credential router, multi-account gh, gh auth switch, vaultwarden migration]
frameworks: [engineering-operating-model, security-operating-model, qa-operating-model, ui-ux-operational]
related_projects: [18-bootstrap-generator, 25-fontface]
---

# Switchyard (26-switchyard)

A background app for Mac and Windows that gives every tool the right login for the project it's working in. It routes git, `gh`, SSH, other CLIs and agent MCP access to the right account from rules, holds secrets in each device's secure storage, and shows problems in the menu bar or system tray. It is personal for now and built to product-grade security.

- **Status:** Planning. The plan set is drafted. Nothing is built.
- **Context profile:** `personal-solo`.
- **Code repo:** none yet. Phase 0 creates `~/Projects/switchyard` with the remote `snds/switchyard`, then moves `plan/` into the repo's `docs/`. This folder then keeps the baton and pointers, the Fontface pattern.
- **Baton:** [[07-projects/26-switchyard/SESSION-STATE|SESSION-STATE]].

## Plan

1. [Overview](plan/00-overview.md): problem, goals, decisions from Sean's answers, assumptions, alternatives, glossary
2. [Systems](plan/01-systems.md): the six parts, data, protocol, technology choices, repo layout
3. [Integrations and dependencies](plan/02-integrations.md): providers, tools, agent surfaces, OS and infrastructure, risk register
4. [How it works](plan/03-how-it-works.md): policy, request flows, sign-in, health checks, the app, device lifecycle
5. [Security](plan/04-security.md): threat model, controls, residual risks, red-team scenarios
6. [Vaultwarden](plan/05-vaultwarden.md): parity with 1Password, Unraid deployment, migration
7. [Implementation plan](plan/06-implementation-plan.md): phases 0–5, Vaultwarden track, exit criteria, first steps
8. [Commercial path](plan/07-commercial-path.md): what changes if it becomes a product, including the GUI workspace generator
9. [Decision log](plan/decisions.md)

Readable copy: https://claude.ai/artifact/VoPXvWfgPkc8ArsmtmESHt, built from `plan/` by `tools/build-plan-html.py` into `05-artifacts/active/switchyard-plan_v1.0_2026-10-14.html` (artifacts are not git-tracked). Edit the markdown, never the HTML.

Origin: the one-page proposal, https://claude.ai/artifact/24mgDkXvtmu12rCcHJM5Be (local copy `05-artifacts/active/switchyard-proposal_v1.0_2026-10-14.html`). Its decisions section is answered by this plan.

## Open questions for Sean

- Is the Windows PC personal-only?
- Does "account thresholds" mean per-account limits: devices, tools, scopes, token lifetime, presence interval, alert levels?
- Does employer IT policy allow a personal tool to hold employer credentials on the Work MBP? This must be answered before Phase 2 runs there.

## Walls

- No employer names, org names or tokens in these docs. Placeholders only.
- Employer identities live on the Work MBP only.
