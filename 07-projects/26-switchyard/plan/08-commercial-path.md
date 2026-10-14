---
title: Switchyard — Commercial path
type: plan
project: 26-switchyard
status: draft
updated: 2026-10-14
---

# Commercial path

**TL;DR:** Build it for yourself first, with product-grade security. The GUI workspace generator is no longer a commercial add-on. Create and Import are core, built in Stage 3. If you decide to sell the app, Stage 7 adds:

- Switchyard's own app registrations with each provider
- a hosted hub that still can't read user data
- a starter library of generic skills and domains
- the business pieces around all of that

Stages 0–6 don't need to be redone. Nothing here starts until you make a go decision.

## What carries over unchanged

- **Files are the source of truth,** in standard formats, so a user can walk away with their workspace at any time.
- **Local-first:** secrets stay on each device, and the index stays local.
- **Zero-knowledge sync:** the server can't read anything.
- **The workspace model, the checks, the scorecards and the security testing.**

## What changes

| Area | For you now | As a product |
|---|---|---|
| Provider apps | A GitHub App you register yourself, `gh` import, pasted tokens | Switchyard registers a GitHub App, a Linear OAuth app and an Atlassian OAuth app. Each provider has its own review. |
| Hub | Self-hosted on Unraid | Hosted by us, end-to-end encrypted, plus a self-host option |
| Starting content | Your workspace | A starter library of generic domains, skills, frameworks and checks, built from your workspace's **patterns** with none of its personal or employer content |
| Onboarding | The Create and Import flows | The same flows, plus first-run guidance, sample workspaces and a guided first import |
| Agents | Your own agent accounts | Still the user's own agents and accounts. Switchyard doesn't resell model access at first. |
| Distribution | Signed builds from CI | Website, auto-update channels, Homebrew cask, winget |
| Plugins | Your own | A plugin directory with review and signing |
| Support | You | Docs, a redacted diagnostics bundle, issue intake |
| Security | Internal tests | External audit before launch, then a bug bounty, a security page and a disclosure policy |
| Legal | None | Privacy policy, terms, data-processing terms for teams, export rules for encryption software (to check) |
| Name | Switchyard (working name) | Trademark search first. A discontinued JBoss project was called SwitchYard. |

## Create and import, as a product feature

These are now core (see [Create and import](04-generator-and-importer.md)). For sale, they also need:

- **Sample profiles** for common users: a solo developer, a designer, a mixed work-and-personal user, a team lead.
- **Importers for common starting points:** a plain Obsidian vault, a Cursor rules repo, a Claude Code skills folder, a repo with only `AGENTS.md`.
- **Guided personas and limits ("thresholds"),** so a user can define work, personal or their own personas, how each is walled, and the limits on each account, without reading docs.
- **A public scorecard** for each release, from corpus T2–T4, so users can see how reliable Create and Import are.

## Business model options (not decided)

| Option | For | Against |
|---|---|---|
| Free local app, paid sync and team features | Easy to try. Revenue tied to multi-device value. | Solo users may never pay |
| One-time license with paid upgrades | Simple. People like it for local tools. | Uneven revenue |
| Open-source core, paid hosted hub and plugin directory | Source you can inspect builds trust in a tool that holds credentials and knowledge | Others can self-host for free |

Lean toward **open core** for a tool that holds both secrets and a person's working knowledge, but decide at the gate.

## Market check before committing

- **Who has the pain?** People who run AI agents across several apps and machines, keep a growing set of instructions and skills, and have more than one account or persona.
- **What they use now:**
  - Obsidian and its plugins
  - per-app rule and skill folders (Claude Code, Cursor, Codex)
  - `AGENTS.md`
  - 1Password for logins
  - their own scripts
- **What to validate:**
  - About 10 conversations with people who have the pain.
  - A landing page.
  - Your own numbers from Stages 0–6: issues caught, time saved, scorecards.

## Team features (only if asked for)

- **Shared models and templates from a company:** org-defined domains, walls and required checks.
- **A compliance view:** which devices and workspaces meet policy.

Keep these zero-knowledge, and stay out of device management.

## Go / no-go checklist

- [ ] Two or more months of daily personal use, with the measurement gates met
- [ ] Market conversations show real demand
- [ ] Name cleared
- [ ] External security audit budgeted
- [ ] Provider app reviews understood (GitHub, Linear, Atlassian)
- [ ] Starter library separated cleanly from your personal content
- [ ] Support time accepted
- [ ] Decision recorded in the [decision log](decisions.md)
