---
title: Personas & access — Overview
type: plan
project: 26-synapse
status: draft
updated: 2026-10-14
---

# Personas & access — Overview

> **Module of the workspace app (2026-10-14).** This folder was the whole plan (then codenamed Switchyard) until Sean widened the product to a desktop workspace app, now codenamed Synapse. It is the **Personas & access** module of that app. The design here still holds. Start with the [big picture](../00-big-picture.md), then read these pages for the depth on accounts, logins and devices. Below, "Synapse" means the app this module belongs to.

**TL;DR:** This module gives every tool the right login for the project it is working in, on Mac and Windows. You sign in once per account on each device. Rules you write once decide which account each request gets. When something goes wrong, the menu bar or system tray tells you.

_Codename. The name is a tracked [fact](../01-workspace-model.md#facts-one-source-many-places); see the [commercial path](../08-commercial-path.md) for the trademark check._

## The problem

Tools like `gh` and git keep one "active account" per machine. Every terminal, editor and AI agent on that machine shares it. Logging in anywhere flips the account for everything at once.

Today the workspace holds this together by hand:

- a Claude-only environment overlay
- per-remote git `includeIf` rules for commit identity
- an SSH host alias for the employer account
- separate `gh` config folders
- a standing rule to run `gh auth switch` back after every login

It works, but each new tool or device adds another place for it to break. Errors show up late, usually as a failed push or a commit under the wrong name. Agent apps add a second version of the problem: most of them allow one account per tracker, such as one Linear account, even when you have two.

## What Synapse does

It has five jobs.

1. **Routes logins.** It decides the identity for each request from context, mostly the repo's remote. There is no "current account" to flip.
2. **Holds secrets safely.** Tokens live in each device's own secure storage (macOS Keychain, Windows TPM-protected store). They never sync.
3. **Connects tools.** git, `gh`, SSH and other command-line tools ask Synapse through doors they already have. Agent apps reach Linear, Jira and GitHub through a local gateway that adds the right account.
4. **Watches health.** It checks tokens, configs, commits and your Vaultwarden server, then notifies you before a tool fails.
5. **Keeps devices in step.** Enrolled devices share the same rules. They never share secrets.

## Goals

- **G1 — Right identity, every time.** No wrong-account commits, pushes or tracker writes.
- **G2 — Nothing to remember.** No manual `gh auth switch`, no per-tool login rituals.
- **G3 — Secrets stay put.** A token stays on the device that earned it, and only goes to the one process that needs it for one request.
- **G4 — Problems are visible early.** Expiring, revoked or misrouted credentials show up as notifications first.
- **G5 — Same behaviour on Mac and Windows** from the first phase.
- **G6 — Product-grade security** even while it's only for you.

## Non-goals

- **Not a password manager.** Vaultwarden does that job. See [Vaultwarden](05-vaultwarden.md).
- **No browser autofill** and no website logins.
- **No control over hosted surfaces.** claude.ai connectors and cloud agents sign in on the vendor's servers. Synapse can list them and remind you. It can't hand them a login.
- **Not a secrets manager for deployed apps.** Production secrets for your apps belong in their own systems.
- **Not device management.** It doesn't manage OS settings, updates or other apps.
- **It never works around employer controls.** It works inside SSO (single sign-on), org app restrictions and token approval flows.

## Decisions from your answers (2026-10-14)

| You said | What it means for the plan |
|---|---|
| Look into Bitwarden through Vaultwarden on Unraid | Vaultwarden replaces 1Password as your password manager. Synapse integrates with it but never needs it to run. Details in [Vaultwarden](05-vaultwarden.md). |
| Cover both cases | The Work MBP holds personal and employer identities from the start. Strict walls keep them apart. |
| Include Windows | Mac and Windows ship together in every phase. The Mac-only SwiftUI idea is dropped in favour of Rust + Tauri 2, the same stack as Fontface. |
| Just for me, but secure regardless | Security is designed as if it were a product from day one. Product work (phase 5) waits for a go decision. |
| If commercial, add a GUI workspace generator | **Changed later the same day:** the GUI generator is now a key part of the tool for everyone, not a commercial extra. See [Create and import](../04-generator-and-importer.md) and decision D34. |

The full decision log is in [decisions.md](../decisions.md).

## Confirmed by Sean (2026-10-14)

- **The Windows PC is personal-only.** Employer identities never live there.
- **"Account thresholds" means per-account limits:**
  - which devices and tools may use an account
  - the largest token permissions allowed
  - the longest token lifetime
  - how often Touch ID or Windows Hello is required
  - when to alert
- **Users define their own personas.** Work and personal are defaults, not the only options. A persona's walls can be held two ways:
  - **By surface:** one app per persona, for example Cursor for work only.
  - **By duplicate installs:** two copies of the same app, such as two Claude desktop apps, each signed into a different account.

  The surface model treats each install as its own **instance** tied to one persona. See the [workspace model](../01-workspace-model.md).
- **Your employer allows it.** IT approval is confirmed for holding employer logins on the Work MBP.

## How we'll know it works

- Zero wrong-identity commits or pushes over 30 days of daily use.
- Zero manual `gh auth switch` commands.
- A new device is set up in under 15 minutes.
- Expiring tokens are flagged at least 7 days ahead.
- The git credential step adds under 50 ms per operation.

## Alternatives considered

| Option | What it covers | Why it isn't enough |
|---|---|---|
| Keep the current workspace machinery | git and `gh` for Claude on Macs | Brittle, Claude-specific, no Windows, no MCP accounts, no health view |
| Git Credential Manager (GCM) | Several GitHub accounts for git over HTTPS on Mac and Windows, keyed by repo path | One door only. No `gh`, MCP, health, walls or fleet. |
| `gh` multi-account | Several logins stored | Still one active account per config |
| 1Password shell plugins + SSH agent | Per-folder CLI logins, SSH keys | You want to leave 1Password. No MCP account routing. |
| Existing MCP gateways (for example Docker's MCP Toolkit) | Central MCP credentials | Not routed by project or wall |

None of these routes identity by project across git, `gh`, SSH and MCP together, with health checks and multi-device rules. That gap is what this module fills.

## Glossary

- **Identity:** one account at one provider, such as "Personal GitHub (snds)".
- **Class:** the side of the wall an identity or repo is on, `personal` or `employer`.
- **Route rule:** "requests for X use identity Y."
- **Wall:** a rule that can never be overridden, such as "personal identities are never used in employer repos."
- **Surface:** an app or tool that does work for you, such as Claude Code, Cursor, the terminal or the Claude desktop app.
- **Adapter:** the small piece that connects one surface to Synapse.
- **Daemon:** the background program that holds secrets and makes decisions (`sy-access`).
- **Shim:** a stand-in program that tools call instead of the real one. It asks the daemon, then runs the real tool.
- **MCP (Model Context Protocol):** the standard way AI agents call outside tools such as Linear or Jira.
- **Gateway:** Synapse's MCP relay. It adds the right account and keeps the token away from the agent.
- **Hub:** an optional server on Unraid that passes encrypted rules between devices.
- **Fleet:** your set of enrolled devices.
- **Presence check:** Touch ID, Windows Hello or your login password, required before a sensitive action.
- **Threshold:** a per-account limit or alert level.

## Module documents

1. [Overview](00-overview.md), this page
2. [Systems](01-systems.md): the access parts and how they fit
3. [Integrations and dependencies](02-integrations.md): providers, tools, platforms, infrastructure, risks
4. [How it works](03-how-it-works.md): rules, request flows, health checks, screens, device lifecycle
5. [Security](04-security.md): credential threat model, controls, limits, testing
6. [Vaultwarden](05-vaultwarden.md): parity, Unraid deployment, 1Password migration
7. [Phases](06-phases.md): this module's internal phases. The [roadmap](../07-roadmap.md) places them in the whole build.

App-level documents: [big picture](../00-big-picture.md), [commercial path](../08-commercial-path.md), [decision log](../decisions.md).
