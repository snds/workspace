---
title: Switchyard — Commercial path
type: plan
project: 26-switchyard
status: draft
updated: 2026-10-14
---

# Commercial path

**TL;DR:** Build it for yourself first, with product-grade security. If you later decide to sell it, the product adds:

- Switchyard's own app registrations with each provider
- a hosted hub that still can't read user data
- guided setup that includes a GUI version of the workspace generator
- the business pieces around all of that

Phases 0–4 don't need to be redone. Nothing here starts until you make a go decision.

## What carries over unchanged

- Local-first design: secrets stay on each device.
- Zero-knowledge sync: the server can't read anything.
- The policy model: identities, routes, walls, thresholds.
- Signed builds and updates, the audit log, the security testing.

## What changes

| Area | For you now | As a product |
|---|---|---|
| Provider apps | A GitHub App you register for yourself, `gh` import, pasted tokens | Switchyard registers a GitHub App, a Linear OAuth app and an Atlassian OAuth app. Each provider has its own review. |
| Hub | Self-hosted on Unraid | Hosted by us, end-to-end encrypted, plus a self-host option |
| Setup | App wizard and CLI | Guided onboarding: workspace, accounts, limits, logins, surfaces in one flow |
| Distribution | Signed builds from CI | Website, auto-update channels, Homebrew cask, winget |
| Support | You | Docs, a redacted diagnostics bundle, issue intake |
| Security | Internal tests and red-team scripts | External audit before launch, then a bug bounty, a security page and a disclosure policy |
| Legal | None | Privacy policy, terms, data-processing terms for teams, export rules for encryption software (to check) |
| Name | Switchyard (working name) | Trademark search first. A discontinued JBoss project was called SwitchYard. |

## The GUI workspace generator

You asked for this: a GUI version of the workspace generator, so a user can set up their workspace, account thresholds and logins.

### One onboarding flow

1. **This device.** Name it, choose its classes (personal, work), and plan other devices.
2. **Accounts.** Sign in to each provider. Identity pinning confirms each account is the intended one.
3. **Walls and thresholds.**
   - Choose which accounts are personal and which are work.
   - Set each account's limits: which devices, which tools, the largest permissions, the longest token lifetime, how often to confirm with Touch ID or Hello, and when to alert.
4. **Surfaces.** Detect installed agent apps from the shared catalog and connect the ones you choose.
5. **Workspace.** Generate the AI workspace with the `wsx` engine: folder, `AGENTS.md`, adapters, skills, projects. Wire it to the identities just created.
6. **Check.** Run a full health check and show a plain summary of what was set up.

### How it fits project 18

- **`wsx` stays the engine.** The app calls `wsx` through a JSON interface and never reimplements its logic.
- **One source of truth for identity scopes.** `wsx` already keeps a remote → scope → identity map (`context/remotes.json`). In the product, that file is generated from Switchyard's rules.
- **No Python install for users.** The app bundles a private Python runtime.

**What project 18 would need:**

1. A machine-readable mode for every command (`--json` in and out).
2. A stable schema for scan results and the remotes map.
3. Packaging as a library or sidecar that the app can bundle.

These go on project 18's roadmap only after the go decision.

### Screens to design (later)

- Welcome
- Devices
- Accounts
- Walls and limits
- Surfaces
- Workspace
- Review

Same visual system as the Switchyard app.

## Business model options (not decided)

| Option | For | Against |
|---|---|---|
| Free local app, paid sync and team features | Easy to try. Revenue tied to multi-device value. | Solo users may never pay |
| One-time license with paid upgrades | Simple, and people like it for local tools | Uneven revenue |
| Open-source core, paid hosted hub | Source you can inspect builds trust in a credential tool | Others can self-host for free |

Lean toward **open core** for a security tool, but decide at the gate.

## Market check before committing

- **Who has the pain?** Developers and designers with work and personal accounts who use AI agents across several tools and machines.
- **Competing answers:**
  - 1Password (shell plugins, SSH agent, agent sign-in)
  - Git Credential Manager
  - `gh` multi-account
  - MCP gateways
  - application secrets managers (a different job)
- **Validate:**
  - About 10 conversations with people who have the pain.
  - A landing page.
  - Your own usage data from phases 1–4, especially incidents caught and time saved.

## Team features (only if asked for)

- Shared policy templates from a company: org-defined walls and required thresholds.
- A compliance view: which devices meet policy.

Keep these zero-knowledge, and stay out of device management.

## Go / no-go checklist

- [ ] Two or more months of daily personal use with the success measures met
- [ ] Market conversations show real demand
- [ ] Name cleared
- [ ] External security audit budgeted
- [ ] Provider app reviews understood (GitHub, Linear, Atlassian)
- [ ] Support time accepted
- [ ] Decision recorded in the [decision log](decisions.md)
